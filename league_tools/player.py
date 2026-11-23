"""``league player``: play the matches that someone asked the match store for.

A step that may not write results (``LEAGUE_STORE_MODE=request``, the
automated iteration's Claude steps) sends the bots' code and the maps to the
store and queues the matches it needs. A player takes them from the queue,
leases them, and plays them as a tournament does: the same runner, the same
schedule, the same rules for a failed turn. It writes each result to the store
and takes the match off the queue.

A player builds only code from the store, never the working tree's ``bots/``,
and checks everything a request says before it plays, since whoever wrote the
request may have been talked into something:

- the bot's code, unpacked from ``code/<fingerprint>.tar.gz``, must have that
  fingerprint, and hold Go files alone;
- its imports must be the bot tests' (``tests/bots/bots_test.go``): the SDK
  and a short list of pure standard packages, nothing that reaches a file,
  the network, the process or a clock, and no cgo or assembly;
- the map must have the hash it is named by;
- the key must be the one ``match_key`` gives for this player's runner build,
  the map's hash, the seats, the fingerprints and the settings: a result is
  written under the key of the game that was played, never another.

The bots are built and played without the player's AWS credentials in their
environment. A request that fails a check is refused: taken off the queue,
with the reason printed, and nothing played.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

from . import engine, gobots
from . import store as match_store
from .paths import LEAGUE, SHARED
from .roster import ANCHOR, NAME
from .tournament import keep_in_store, match_key, run_schedule

# What a bot may import besides the SDK: the bot tests' allowedImports (tests/bots/bots_test.go).
ALLOWED_IMPORTS = frozenset(
    {
        "cmp",
        "container/heap",
        "container/list",
        "context",
        "encoding/json",
        "errors",
        "fmt",
        "iter",
        "math",
        "math/bits",
        "slices",
        "sort",
        "strconv",
        "strings",
        "unicode",
        "unicode/utf8",
    }
)
# Files of a Go package that aren't plain Go: none may be in a bot.
FOREIGN_FILES = ("CgoFiles", "CFiles", "CXXFiles", "MFiles", "HFiles", "FFiles", "SFiles", "SwigFiles", "SysoFiles")
# Bounds on a request's settings, so that one request can't hold a player for hours.
MAX_GENERATIONS = 1000
MAX_TURN_MILLISECONDS = 10_000
MAP_NAME = re.compile(r"[A-Za-z0-9_-]{1,64}")
HEX = re.compile(r"[0-9a-f]{64}")
# The player's runs: the bots' stderr, and the directories it builds requested code in.
PLAYER_RUNS = SHARED / "runs" / "player"
DEFAULT_BATCH = 50


class Refused(ValueError):
    """A request that the player won't play: why, in a sentence."""


def environment() -> dict[str, str]:
    """The environment that bots are built and played in: this one without credentials, and without cgo."""
    hidden = ("AWS_", "LEAGUE_STORE", "GITHUB_TOKEN", "ACTIONS_")
    kept = {name: value for name, value in os.environ.items() if not name.startswith(hidden)}
    return kept | {"CGO_ENABLED": "0"}


def check_request(key: str, entry: dict[str, Any], build_hash: str) -> None:
    """Check that a queued request is well formed and that its key is the game it describes.

    Raises:
        Refused: It isn't.
    """
    try:
        seats, fingerprints, settings = entry["seats"], entry["fingerprints"], entry["settings"]
        map_name, map_hash = entry["map"]["name"], entry["map"]["sha256"]
        build = entry["build"]
    except KeyError, TypeError:
        raise Refused("the request lacks its build, map, seats, fingerprints or settings") from None
    if build != build_hash:
        raise Refused(f"it is for the runner build {str(build)[:16]}, and this player's is {build_hash[:16]}")
    if not (isinstance(seats, list) and len(seats) == 2 and all(isinstance(name, str) for name in seats)):
        raise Refused("a match has two seats, each a player's name")
    if len(set(seats)) != 2 or not all(NAME.fullmatch(name) for name in seats):
        raise Refused("a seat is not a bot's name, or both seats are the same")
    if not (isinstance(fingerprints, list) and len(fingerprints) == 2):
        raise Refused("a match has a fingerprint for each seat")
    for name, fingerprint in zip(seats, fingerprints, strict=True):
        if ANCHOR.fullmatch(name):
            if fingerprint != name:
                raise Refused(f"the default bot {name}'s fingerprint is its name")
        elif not (isinstance(fingerprint, str) and HEX.fullmatch(fingerprint)):
            raise Refused(f"{name}'s fingerprint is not a league bot's (an outside opponent is never played here)")
    if all(ANCHOR.fullmatch(name) for name in seats):
        raise Refused("two default bots never play each other")
    if not (
        isinstance(settings, list)
        and len(settings) == 2
        and all(isinstance(value, int) and value > 0 for value in settings)
        and settings[0] <= MAX_GENERATIONS
        and settings[1] <= MAX_TURN_MILLISECONDS
    ):
        raise Refused(f"the settings are two whole numbers up to {MAX_GENERATIONS} and {MAX_TURN_MILLISECONDS}")
    if not (isinstance(map_name, str) and MAP_NAME.fullmatch(map_name) and HEX.fullmatch(str(map_hash))):
        raise Refused("the map's name or hash is not one")
    if match_key(build_hash, map_hash, seats, fingerprints, settings) != key:
        raise Refused("its key is not the key of the game it describes")


def check_imports(tree: Path, name: str, environment: dict[str, str] | None = None) -> None:
    """Check, with ``go list``, that a bot of a build tree imports only what the bot tests allow.

    ``go list`` reads the package as the compiler will, without building or
    running anything.

    Raises:
        Refused: The package doesn't load, imports something else, or has files that aren't Go.
    """
    listed = subprocess.run(
        ["go", "list", "-json", f"./bots/{name}"],
        cwd=tree,
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )
    if listed.returncode != 0:
        raise Refused(f"{name}'s code doesn't load: {listed.stderr.strip()[-300:]}")
    package = json.loads(listed.stdout)
    if package.get("Name") != "main":
        raise Refused(f"{name}'s code is not package main")
    foreign = [file for kind in FOREIGN_FILES for file in package.get(kind) or []]
    if foreign:
        raise Refused(f"{name}'s code has files that aren't plain Go: {', '.join(foreign[:5])}")
    imports = package.get("Imports") or []
    refused = [
        path
        for path in imports
        if path not in ALLOWED_IMPORTS and path != gobots.SDK_MODULE and not path.startswith(gobots.SDK_MODULE + "/")
    ]
    if refused:
        raise Refused(f"{name} imports what a bot may not: {', '.join(refused)}")


def materialise(store: match_store.Store, tree: Path, name: str, fingerprint: str) -> None:
    """Unpack a bot's code from the store into a build tree, as ``bots/<name>/``, and check its fingerprint.

    Raises:
        Refused: The store has no code under the fingerprint, the tarball holds
            more than Go files, or the code's fingerprint is another.
    """
    directory = tree / "bots" / name
    if directory.exists():
        if gobots.fingerprint(directory) != fingerprint:
            raise Refused(f"two requests of one batch want two codes of {name}")
        return
    data = store.code(fingerprint)
    if data is None:
        raise Refused(f"the store has no code of {name} under its fingerprint {fingerprint[:16]}")
    try:
        match_store.unpack_bot(data, directory)
    except (ValueError, OSError, EOFError) as error:
        shutil.rmtree(directory, ignore_errors=True)
        raise Refused(str(error)) from None
    found = gobots.fingerprint(directory)
    if found != fingerprint:
        shutil.rmtree(directory, ignore_errors=True)
        raise Refused(f"{name}'s code has the fingerprint {found[:16]}, not the requested {fingerprint[:16]}")


def _refuse(store: match_store.Store, key: str, reason: str, lease: match_store.Lease | None = None) -> None:
    print(f"league player: refused {key}: {reason}", file=sys.stderr, flush=True)
    store.dequeue(key)
    if lease is not None:
        store.release(lease)


def take(
    store: match_store.Store, build_hash: str, batch: int, parallel: int
) -> tuple[list[tuple[dict[str, Any], match_store.Lease]], int, bool]:
    """Lease up to ``batch`` queued matches that nobody plays yet.

    A request with a result already is taken off the queue. Two requests of
    one batch must agree on each bot's code and each map's file, since a
    schedule names players and maps by name: a request that doesn't is left
    for the next batch.

    Returns:
        The requests leased, with their leases; how many were refused; and
        whether any was left for the next batch.
    """
    taken: list[tuple[dict[str, Any], match_store.Lease]] = []
    codes: dict[str, str] = {}
    maps: dict[str, str] = {}
    refused = 0
    deferred = False
    seconds = match_store.lease_seconds(batch, parallel)
    for key in store.queued():
        if len(taken) >= batch:
            deferred = True
            break
        if store.has_result(key):
            store.dequeue(key)
            continue
        entry = store.queue_entry(key)
        if entry is None:
            continue
        try:
            check_request(key, entry, build_hash)
        except Refused as error:
            _refuse(store, key, str(error))
            refused += 1
            continue
        wanted = dict(zip(entry["seats"], entry["fingerprints"], strict=True))
        if (
            any(codes.get(name, code) != code for name, code in wanted.items())
            or maps.get(entry["map"]["name"], entry["map"]["sha256"]) != entry["map"]["sha256"]
        ):
            deferred = True
            continue
        lease = store.lease(key, seconds)
        if lease is None:
            continue
        if store.has_result(key):
            store.release(lease)
            store.dequeue(key)
            continue
        codes |= wanted
        maps[entry["map"]["name"]] = entry["map"]["sha256"]
        taken.append((entry, lease))
    return taken, refused, deferred


def play(
    store: match_store.Store,
    build: engine.Build,
    taken: list[tuple[dict[str, Any], match_store.Lease]],
    parallel: int,
) -> tuple[int, int]:
    """Play leased requests in a build tree of their own code, and write the results; returns played and refused."""
    PLAYER_RUNS.mkdir(parents=True, exist_ok=True)
    clean = environment()
    refused = 0
    played = 0
    with (
        tempfile.TemporaryDirectory(dir=PLAYER_RUNS, prefix="tree-") as directory,
        match_store.Heartbeat(store, [lease for _, lease in taken]) as heartbeat,
    ):
        tree = Path(directory)
        for module_file in ("go.mod", "go.sum"):
            shutil.copy(LEAGUE / module_file, tree / module_file)
        (tree / "maps").mkdir()
        ready: list[dict[str, Any]] = []
        for entry, _ in taken:
            try:
                for name, fingerprint in zip(entry["seats"], entry["fingerprints"], strict=True):
                    if not ANCHOR.fullmatch(name):
                        materialise(store, tree, name, fingerprint)
                map_file = tree / "maps" / f"{entry['map']['name']}.json"
                if not map_file.exists():
                    data = store.map_data(entry["map"]["sha256"])
                    if data is None:
                        raise Refused("the store has no map file with the requested hash")
                    map_file.write_bytes(data)
            except Refused as error:
                _refuse(store, entry["key"], str(error), heartbeat.pop(entry["key"]))
                refused += 1
                continue
            ready.append(entry)
        names = sorted({name for entry in ready for name in entry["seats"] if not ANCHOR.fullmatch(name)})
        bad: dict[str, str] = {}
        for name in names:
            try:
                check_imports(tree, name, clean)
            except Refused as error:
                bad[name] = str(error)
        good = [name for name in names if name not in bad]
        try:
            binaries = gobots.build(good, bots=tree / "bots", environment=clean)
        except RuntimeError:
            # One bot that doesn't compile fails the whole build: build each alone,
            # and refuse the matches of the ones that fail, not the batch.
            binaries = {}
            for name in good:
                try:
                    binaries |= gobots.build([name], bots=tree / "bots", environment=clean)
                except RuntimeError as error:
                    bad[name] = f"the bot {name} doesn't compile: {str(error)[-500:]}"
        for entry in [entry for entry in ready if bad.keys() & set(entry["seats"])]:
            reason = next(bad[name] for name in entry["seats"] if name in bad)
            _refuse(store, entry["key"], reason, heartbeat.pop(entry["key"]))
            refused += 1
            ready.remove(entry)
        if not ready:
            return played, refused

        def keep(line: dict[str, Any]) -> None:
            nonlocal played
            if keep_in_store(store, line):
                store.dequeue(line["id"])
            played += 1
            lease = heartbeat.pop(line["id"])
            if lease is not None:
                store.release(lease)

        groups: dict[tuple[int, int], list[dict[str, Any]]] = {}
        for entry in ready:
            groups.setdefault((entry["settings"][0], entry["settings"][1]), []).append(entry)
        for (max_generations, turn_timeout_milliseconds), entries in groups.items():
            players: dict[str, dict[str, Any]] = {}
            for entry in entries:
                for name in entry["seats"]:
                    anchor = ANCHOR.fullmatch(name)
                    players[name] = (
                        {"default_level": int(anchor.group(1))}
                        if anchor
                        else {"worker": [str(binaries[name]), "worker"], "directory": str(tree)}
                    )
            run_schedule(
                build,
                players,
                {entry["map"]["name"]: str(tree / "maps" / f"{entry['map']['name']}.json") for entry in entries},
                [{"id": entry["key"], "map": entry["map"]["name"], "seats": entry["seats"]} for entry in entries],
                PLAYER_RUNS,
                keep,
                max_generations=max_generations,
                turn_timeout_milliseconds=turn_timeout_milliseconds,
                parallel=parallel,
                environment=clean,
            )
    return played, refused


def run(drain: bool, batch: int = DEFAULT_BATCH, max_seconds: float | None = None, parallel: int = 0) -> int:
    """Play the queue's matches, a batch at a time, until it is empty (``drain``) or the time is up.

    Without ``drain`` it waits for more requests, backing off up to
    ``MAX_POLL_SECONDS``, until ``max_seconds``. With it, it ends once no
    request is left that it could lease: what other players hold, they play.
    ``max_seconds`` stops it taking a new batch, not playing one.

    Returns:
        The exit status: 0.

    Raises:
        ValueError: No store is set, or the store is in request mode.
    """
    build = engine.build()
    store = match_store.open_store(build.hash)
    if store is None:
        raise ValueError(f"league player plays the match store's queue: set {match_store.STORE_VARIABLE}")
    if store.mode != "play":
        raise ValueError(f"league player writes results: {match_store.MODE_VARIABLE} must be play, not {store.mode}")
    parallel = parallel or os.cpu_count() or 1
    print(
        f"league player {store.played_by['machine']}: store {store.location}, runner build {store.namespace}",
        file=sys.stderr,
        flush=True,
    )
    started = time.monotonic()
    played = refused = 0
    delay = match_store.POLL_SECONDS
    while max_seconds is None or time.monotonic() - started < max_seconds:
        taken, turned_down, deferred = take(store, build.hash, batch, parallel)
        refused += turned_down
        if taken:
            done, turned_down = play(store, build, taken, parallel)
            played += done
            refused += turned_down
            delay = match_store.POLL_SECONDS
            continue
        if deferred:
            continue
        if drain:
            break
        time.sleep(delay)
        delay = min(delay * 2, match_store.MAX_POLL_SECONDS)
    print(
        f"league player: {played} matches played, {refused} requests refused, in {time.monotonic() - started:.0f} s",
        file=sys.stderr,
        flush=True,
    )
    return 0
