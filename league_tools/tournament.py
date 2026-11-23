"""Play a round robin between bots, with cached results, and sum it up."""

from __future__ import annotations

import functools
import hashlib
import json
import os
import sys
import time
from collections import defaultdict
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from itertools import combinations
from pathlib import Path
from typing import Any

from . import digest, engine, gobots, ratings
from . import store as match_store
from .opponents import load_opponents
from .paths import BOTS, CACHE, LEAGUE, MAPS, RUNS
from .roster import ANCHOR, load_bot


@dataclass
class Tournament:
    """What to play: every pair of players, on every map, from both sides."""

    players: list[str]
    maps: list[Path]
    # With a focus, only the pairs with a focused player are played.
    focus: list[str] = field(default_factory=list)
    # The players whose lost games and longest wins the tables list.
    listed: list[str] = field(default_factory=list)
    # Each listed bot's parent, for the table that compares them.
    parents: dict[str, str] = field(default_factory=dict)
    # With a focus, play only each focused bot against its parent: the
    # head-to-head rule, and the gate on those games, in a few seconds.
    parents_only: bool = False
    max_generations: int = 300
    turn_timeout_milliseconds: int = 2000
    parallel: int = 0
    use_cache: bool = True
    # (K, N): play only the K-th of N slices of the matches, for runners that
    # share a tournament; their caches together hold the whole of it.
    shard: tuple[int, int] | None = None


def parse_shard(text: str) -> tuple[int, int]:
    """A shard written ``K/N``: the K-th of N slices, counted from 1.

    Raises:
        ValueError: It isn't two whole numbers with 1 <= K <= N.
    """
    index, _, count = text.partition("/")
    if not (index.isdigit() and count.isdigit() and 1 <= int(index) <= int(count)):
        raise ValueError(f"--shard {text!r}: write K/N, the K-th of N slices, such as 2/8")
    return int(index), int(count)


def in_shard(key: str, shard: tuple[int, int] | None) -> bool:
    """Whether a match's key falls in the shard: every key falls in exactly one of N shards.

    A key is a hash, so the shards are even and every runner agrees on them,
    whatever its cache holds.
    """
    if shard is None:
        return True
    index, count = shard
    return int(key, 16) % count == index - 1


def map_files(selection: str) -> list[Path]:
    """The map files a selection names: ``train``, ``holdout``, ``all`` or names.

    Raises:
        ValueError: A name is not a map of the league, or two maps share a name.
    """
    if selection in ("train", "holdout"):
        files = sorted((MAPS / selection).glob("*.json"))
    elif selection == "all":
        files = sorted(MAPS.glob("*/*.json"))
    else:
        files = []
        for name in selection.split(","):
            found = sorted(MAPS.glob(f"*/{name.strip()}.json"))
            if not found:
                raise ValueError(f"there is no map {name.strip()!r} under {MAPS}")
            files.extend(found)
    names = [file.stem for file in files]
    repeated = sorted({name for name in names if names.count(name) > 1})
    if repeated:
        raise ValueError(f"more than one map is named {', '.join(repeated)}; a map's name is its file's")
    return files


def has_holdout(maps: list[Path]) -> bool:
    """Whether any of the maps is a holdout map, whose games nobody reads."""
    return any(file.parent.name == "holdout" for file in maps)


def player_specification(name: str, binary: Path | None = None) -> dict[str, Any]:
    """The runner's description of a player: a default bot, an outside opponent or a league bot.

    Args:
        name: The player.
        binary: A league bot's program, from ``gobots.build``; its current code's by default.
    """
    anchor = ANCHOR.fullmatch(name)
    if anchor:
        return {"default_level": int(anchor.group(1))}
    outside = load_opponents().get(name)
    if outside is not None:
        return outside.specification()
    load_bot(name)
    return {"worker": [str(binary or gobots.binary_path(name)), "worker"], "directory": str(LEAGUE)}


@functools.cache
def player_fingerprint(name: str) -> str:
    """What decides how a player plays: its code, and for a league bot the Go SDK's version."""
    if ANCHOR.fullmatch(name):
        return name
    outside = load_opponents().get(name)
    if outside is not None:
        return outside.fingerprint()
    return gobots.fingerprint(BOTS / name)


def match_key(build: str, map_hash: str, seats: list[str], fingerprints: list[str], settings: list[int]) -> str:
    """The name of a match's result in the cache.

    It covers everything that decides the game, and the seats' names, which
    the result carries: two bots with the same code have results of their own.
    """
    return hashlib.sha256(json.dumps([build, map_hash, seats, fingerprints, settings]).encode()).hexdigest()[:32]


def _write_atomically(path: Path, text: str) -> None:
    """Write a file that another checkout's tournament may be reading."""
    partial = path.with_name(f".{path.name}.{os.getpid()}")
    partial.write_text(text, encoding="utf-8")
    os.replace(partial, path)


def cached_result(key: str) -> dict[str, Any] | None:
    """A match's cached result, when its demo is still there."""
    result_file, demo_file = CACHE / f"{key}.json", CACHE / f"{key}.json.gz"
    if not result_file.is_file() or not demo_file.is_file():
        return None
    return json.loads(result_file.read_text(encoding="utf-8")) | {"demo": str(demo_file)}


def play(tournament: Tournament, run_directory: Path) -> list[dict[str, Any]]:
    """Play the tournament's matches, reusing cached results, and return them all.

    Every pair with a focused player (every pair, without a focus) plays on
    every map from both sides; two default bots never play each other.
    """
    focus = set(tournament.focus)
    if tournament.parents_only:
        pairs = [(name, tournament.parents[name]) for name in tournament.focus if name in tournament.parents]
    else:
        pairs = [
            pair
            for pair in combinations(dict.fromkeys(tournament.players), 2)
            if not all(ANCHOR.fullmatch(name) for name in pair) and (not focus or focus & set(pair))
        ]
    matches = [
        (map_file, seats) for map_file in tournament.maps for pair in pairs for seats in (list(pair), list(pair[::-1]))
    ]
    return play_matches(
        matches,
        run_directory,
        max_generations=tournament.max_generations,
        turn_timeout_milliseconds=tournament.turn_timeout_milliseconds,
        parallel=tournament.parallel,
        use_cache=tournament.use_cache,
        shard=tournament.shard,
    )


def kept(line: dict[str, Any]) -> bool:
    """Whether a match's line is a result to keep: the match was played, and nobody failed a turn."""
    return "error" not in line and not any(seat["failed_turns"] for seat in line["seats"])


def keep_locally(line: dict[str, Any]) -> None:
    """Keep a match's result in the local cache, or drop it there when it isn't one to keep."""
    cached = CACHE / f"{line['id']}.json"
    if kept(line):
        _write_atomically(cached, json.dumps(line))
    else:
        # The runner has replaced the demo, so an earlier result of
        # this match no longer belongs to it.
        cached.unlink(missing_ok=True)


def keep_in_store(store: match_store.Store, line: dict[str, Any]) -> bool:
    """Keep a match's line in the store, and in the local cache when it is the match's result.

    A line with a failed turn, or of a match the runner couldn't play, is an
    attempt (the store's ``failed/``), not the result, and the match is played
    again next time, until the ``MAX_FAILED_ATTEMPTS``-th attempt: that one is
    the result, failed turns and all, and ``--strict`` fails on it.

    Returns:
        Whether the line is now the match's result.
    """
    key = line["id"]
    cached, demo = CACHE / f"{key}.json", CACHE / f"{key}.json.gz"
    final = kept(line)
    if not final:
        attempt = store.record_failure(key, line)
        final = attempt >= match_store.MAX_FAILED_ATTEMPTS
        if final:
            print(
                f"league: {line.get('map')} {' vs '.join(line.get('players') or [])}: attempt {attempt} failed too, "
                "and is kept as the match's result",
                file=sys.stderr,
            )
    with_demo = final and "error" not in line and demo.is_file()
    if with_demo:
        _write_atomically(cached, json.dumps(line))
    else:
        cached.unlink(missing_ok=True)
    if final:
        store.put_result(key, line, demo.read_bytes() if with_demo else None)
    return final


def run_schedule(
    build: engine.Build,
    players: dict[str, dict[str, Any]],
    maps: dict[str, str],
    matches: list[dict[str, Any]],
    run_directory: Path,
    keep: Callable[[dict[str, Any]], None],
    *,
    max_generations: int,
    turn_timeout_milliseconds: int,
    parallel: int,
    environment: dict[str, str] | None = None,
) -> None:
    """Play matches in one run of the headless runner, and hand each match's line to ``keep`` as it ends.

    Args:
        build: The runner.
        players: Each player's description for the runner (``player_specification``).
        maps: Each map's file, by the map's name.
        matches: The matches: their keys (``id``), maps and seats.
        run_directory: Where the bots' stderr goes (``workers.log``).
        keep: Called with each match's line.
        max_generations: The matches' setting.
        turn_timeout_milliseconds: The matches' setting.
        parallel: Matches at once.
        environment: The runner's environment; this process's by default.
    """
    schedule = {
        "players": players,
        "maps": maps,
        "matches": matches,
        "max_generations": max_generations,
        "turn_timeout_milliseconds": turn_timeout_milliseconds,
        "parallel": parallel,
        "demo_directory": str(CACHE),
        "compress_demos": True,
    }
    started = time.monotonic()
    log = run_directory / "workers.log"
    lines = (
        engine.play(build.binary, schedule, log)
        if environment is None
        else engine.play(build.binary, schedule, log, environment=environment)
    )
    for line in lines:
        keep(line)
    seconds = time.monotonic() - started
    print(
        f"Time: played {len(matches)} matches in {seconds:.0f} s, {len(matches) / max(seconds, 0.001):.1f} "
        f"a second on {parallel} at once",
        file=sys.stderr,
    )


@dataclass
class _Plan:
    """A call of ``play_matches``: its matches, what decides each, and the results so far."""

    build: engine.Build
    settings: list[int]
    parallel: int
    run_directory: Path
    # Each match by its key, as the runner's schedule names it.
    planned: dict[str, dict[str, Any]] = field(default_factory=dict)
    # Each match's map file and its players' fingerprints, by its key.
    sources: dict[str, tuple[Path, list[str]]] = field(default_factory=dict)
    map_hashes: dict[Path, str] = field(default_factory=dict)
    # The outside opponents, whose matches no other machine can play.
    outside: set[str] = field(default_factory=set)
    results: dict[str, dict[str, Any]] = field(default_factory=dict)

    def shared(self, key: str) -> bool:
        """Whether another machine can play a match: none of its players is an outside opponent."""
        return not self.outside & set(self.planned[key]["seats"])

    def from_cache(self) -> list[dict[str, Any]]:
        """Take what the local cache has; returns the matches still without a result."""
        for key in self.planned:
            if key not in self.results:
                cached = cached_result(key)
                if cached is not None:
                    self.results[key] = cached
        return self.missing()

    def missing(self) -> list[dict[str, Any]]:
        """The matches without a result yet."""
        return [match for key, match in self.planned.items() if key not in self.results]

    def from_store(self, store: match_store.Store, matches: list[dict[str, Any]]) -> int:
        """Take what the store has of these matches, into the local cache too; returns how many it had."""
        keys = [match["id"] for match in matches if match["id"] not in self.results and self.shared(match["id"])]
        found = match_store.each(lambda key: store.fetch(key, CACHE), keys)
        for key, result in zip(keys, found, strict=True):
            if result is not None:
                self.results[key] = result
        return sum(result is not None for result in found)

    def play_here(self, matches: list[dict[str, Any]], keep: Callable[[dict[str, Any]], None]) -> None:
        """Play matches on this machine, building the league bots that need it."""
        names = sorted({name for match in matches for name in match["seats"]})
        # Each league bot is built once per tournament, and not again while its code is the same.
        binaries = gobots.build(name for name in names if not ANCHOR.fullmatch(name) and name not in self.outside)

        def kept_here(line: dict[str, Any]) -> None:
            self.results[line["id"]] = line
            keep(line)

        run_schedule(
            self.build,
            {name: player_specification(name, binaries.get(name)) for name in names},
            {map_file.stem: str(map_file) for map_file in self.map_hashes},
            matches,
            self.run_directory,
            kept_here,
            max_generations=self.settings[0],
            turn_timeout_milliseconds=self.settings[1],
            parallel=self.parallel,
        )

    def request(self, key: str) -> dict[str, Any]:
        """What the players need to play a match: the queue's entry."""
        map_file, fingerprints = self.sources[key]
        match = self.planned[key]
        return {
            "key": key,
            "build": self.build.hash,
            "map": {"name": match["map"], "sha256": self.map_hashes[map_file]},
            "seats": match["seats"],
            "fingerprints": fingerprints,
            "settings": self.settings,
        }


def play_matches(
    matches: list[tuple[Path, list[str]]],
    run_directory: Path,
    max_generations: int = 300,
    turn_timeout_milliseconds: int = 2000,
    parallel: int = 0,
    use_cache: bool = True,
    shard: tuple[int, int] | None = None,
) -> list[dict[str, Any]]:
    """Play these matches (a map and its seats, in order), reusing cached results, and return them all.

    Bots are deterministic, so a match is decided by the runner's build, the
    map, the two bots' code and the settings. A match with the same key as an
    earlier one is not played again. A result with a failed turn is not kept:
    a turn can run out of time because the machine was busy, and the next
    tournament plays that match again. With a shard, only the matches whose
    key falls in it are played and returned.

    With a match store (``LEAGUE_STORE``, ``league_tools/store.py``) the local
    cache is a read-through copy of it: what the cache lacks is taken from the
    store, and what neither has is played once for the whole league. In play
    mode, the default, this machine leases what it can, plays it as without a
    store and writes the results to the store; the matches other machines hold
    are waited for, and taken over when their lease ends. In request mode,
    for a step that read real games, it sends the bots' code and the maps,
    queues the matches for the players (``league player``) and waits for
    them: it never writes a result to the store. A result with a failed turn
    is then played again at most ``MAX_FAILED_ATTEMPTS`` times, the last
    attempt being the result. ``use_cache=False`` leaves the store alone.

    Outside opponents (``opponents.local.toml``) can't be played on another
    machine: their matches are always played here, kept in the local cache
    alone, and never written to the store or asked for.
    """
    build = engine.build()
    # A bot's code is read once per tournament, not once per match.
    player_fingerprint.cache_clear()
    settings = [max_generations, turn_timeout_milliseconds]
    plan = _Plan(build, settings, parallel or os.cpu_count() or 1, run_directory, outside=set(load_opponents()))
    for map_file, seats in matches:
        if map_file not in plan.map_hashes:
            plan.map_hashes[map_file] = hashlib.sha256(map_file.read_bytes()).hexdigest()
        fingerprints = [player_fingerprint(name) for name in seats]
        key = match_key(build.hash, plan.map_hashes[map_file], seats, fingerprints, settings)
        if not in_shard(key, shard):
            continue
        plan.planned[key] = {"id": key, "map": map_file.stem, "seats": seats}
        plan.sources[key] = (map_file, fingerprints)
    results = plan.results
    store = match_store.open_store(build.hash) if use_cache else None

    to_play = plan.from_cache() if use_cache else plan.missing()
    from_store = plan.from_store(store, to_play) if store is not None else 0
    to_play = plan.missing()
    part = f" in shard {shard[0]}/{shard[1]}" if shard else ""
    stored = f" ({from_store} of them from the store)" if store is not None else ""
    print(
        f"{len(plan.planned)} matches{part}: {len(results)} cached{stored}, {len(to_play)} to play",
        file=sys.stderr,
        flush=True,
    )
    if not to_play:
        return [results[key] for key in plan.planned if key in results]
    CACHE.mkdir(parents=True, exist_ok=True)
    if store is not None and store.mode == "request":
        _request(plan, store, to_play)
        return [results[key] for key in plan.planned if key in results]
    # One tournament plays at a time on this machine, whichever checkout it
    # runs from: several at once only slow every turn down (and a turn that
    # runs out of time fails), and the one that waits finds in the cache
    # what the other played.
    waiting = time.monotonic()
    others: list[dict[str, Any]] = []
    with engine.exclusive(CACHE / ".play.lock", "league: waiting for another tournament to finish playing"):
        waited = time.monotonic() - waiting
        if waited >= 1:
            print(f"Time: waited {waited:.0f} s for another tournament", file=sys.stderr)
        before = len(to_play)
        to_play = plan.from_cache() if use_cache else to_play
        if store is not None:
            plan.from_store(store, to_play)
            to_play = plan.missing()
        if len(to_play) < before:
            print(f"{before - len(to_play)} of them were played meanwhile; {len(to_play)} to play", file=sys.stderr)
        if to_play and store is None:
            plan.play_here(to_play, keep_locally)
        elif to_play and store is not None:
            others = _lease_and_play(plan, store, to_play)
    if store is not None and others:
        _wait_for(plan, store, others, take_over=True)
    return [results[key] for key in plan.planned if key in results]


def _lease(
    plan: _Plan, store: match_store.Store, matches: list[dict[str, Any]]
) -> tuple[dict[str, match_store.Lease], list[dict[str, Any]]]:
    """Lease what can be leased of these matches; returns the leases, and the matches someone else holds.

    A match whose result came in between the look in the store and the lease
    is taken from the store, and its lease given back.
    """
    seconds = match_store.lease_seconds(len(matches), plan.parallel)
    got = match_store.each(lambda match: store.lease(match["id"], seconds), matches)
    leases = {lease.key: lease for lease in got if lease is not None}
    held = [match for match, lease in zip(matches, got, strict=True) if lease is None]
    keys = list(leases)
    for key, result in zip(keys, match_store.each(lambda key: store.fetch(key, CACHE), keys), strict=True):
        if result is not None:
            plan.results[key] = result
            store.release(leases.pop(key))
    return leases, held


def _play_leased(
    plan: _Plan, store: match_store.Store, matches: list[dict[str, Any]], leases: dict[str, match_store.Lease]
) -> None:
    """Play matches here while holding their leases, writing each result to the store as it ends."""
    if not matches:
        return
    with match_store.Heartbeat(store, leases.values()) as heartbeat:

        def keep(line: dict[str, Any]) -> None:
            key = line["id"]
            if key not in plan.planned or not plan.shared(key):
                keep_locally(line)
                return
            keep_in_store(store, line)
            lease = heartbeat.pop(key)
            if lease is not None:
                store.release(lease)

        plan.play_here(matches, keep)


def _lease_and_play(plan: _Plan, store: match_store.Store, to_play: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Lease what this machine can of the matches and play it; returns the matches other players hold."""
    alone = [match for match in to_play if not plan.shared(match["id"])]
    shared = [match for match in to_play if plan.shared(match["id"])]
    leases, others = _lease(plan, store, shared)
    print(
        f"Store: {len(leases)} of them leased here, {len(others)} held by other players"
        + (f", {len(alone)} with an outside opponent, played here alone" if alone else ""),
        file=sys.stderr,
    )
    _play_leased(plan, store, alone + [match for match in shared if match["id"] in leases], leases)
    return others


def _request(plan: _Plan, store: match_store.Store, to_play: list[dict[str, Any]]) -> None:
    """Ask the players for the matches that neither the cache nor the store has, and wait for them.

    Sends the league bots' code and the maps the store lacks, and queues the
    matches. It writes no result, lease or failed attempt to the store: a
    machine that never saw this step's inputs builds the code and plays it.
    """
    alone = [match for match in to_play if not plan.shared(match["id"])]
    shared = [match for match in to_play if plan.shared(match["id"])]
    if alone:
        with engine.exclusive(CACHE / ".play.lock", "league: waiting for another tournament to finish playing"):
            plan.play_here(alone, keep_locally)
    sent: set[str] = set()
    for match in shared:
        map_file, fingerprints = plan.sources[match["id"]]
        for name, fingerprint in zip(match["seats"], fingerprints, strict=True):
            if ANCHOR.fullmatch(name) or fingerprint in sent:
                continue
            if gobots.fingerprint(BOTS / name) != fingerprint:
                raise RuntimeError(f"bots/{name} changed while the tournament ran; play it again")
            store.put_code(fingerprint, BOTS / name)
            sent.add(fingerprint)
        if str(map_file) not in sent:
            if store.put_map(map_file.read_bytes()) != plan.map_hashes[map_file]:
                raise RuntimeError(f"{map_file} changed while the tournament ran; play it again")
            sent.add(str(map_file))
    added = sum(match_store.each(lambda match: store.enqueue(plan.request(match["id"])), shared))
    woken = store.wake_players(added)
    print(
        f"Store: requested {added} matches from the players"
        + (f" ({len(shared) - added} were requested already)" if added < len(shared) else "")
        + (f", and woke {woken} Lambda players" if woken else "")
        + (f"; {len(alone)} with an outside opponent were played here" if alone else ""),
        file=sys.stderr,
        flush=True,
    )
    _wait_for(plan, store, shared, take_over=False)


def _wait_for(plan: _Plan, store: match_store.Store, matches: list[dict[str, Any]], take_over: bool) -> None:
    """Wait for matches that other players hold or were asked for, polling the store with a backoff.

    With ``take_over``, a match whose lease ended without a result (its player
    stopped, or its attempt failed a turn) is leased and played here. Without
    it (request mode), a match off the queue without a result was refused by
    the players. A match still missing after ``LEAGUE_STORE_WAIT_SECONDS`` is
    returned as not played.
    """
    pending = {match["id"]: match for match in matches}
    if not pending:
        return
    started = time.monotonic()
    limit = match_store.wait_seconds()
    delay = match_store.POLL_SECONDS
    taken = refused = 0
    while True:
        keys = list(pending)
        for key, result in zip(keys, match_store.each(lambda key: store.fetch(key, CACHE), keys), strict=True):
            if result is not None:
                plan.results[key] = result
                del pending[key]
        if not pending:
            break
        if take_over:
            leases, _ = _lease(plan, store, list(pending.values()))
            for key in [key for key in pending if key in plan.results]:
                del pending[key]
            if leases:
                with engine.exclusive(CACHE / ".play.lock", "league: waiting for another tournament to finish playing"):
                    _play_leased(plan, store, [pending.pop(key) for key in list(leases)], leases)
                taken += len(leases)
                delay = match_store.POLL_SECONDS
                continue
        else:
            # Off the queue first, then no result: a player that played it wrote the result before it dequeued.
            keys = list(pending)
            gone = match_store.each(lambda key: not store.is_queued(key) and not store.has_result(key), keys)
            for key in [key for key, off in zip(keys, gone, strict=True) if off]:
                match = pending.pop(key)
                plan.results[key] = {
                    "id": key,
                    "map": match["map"],
                    "players": match["seats"],
                    "error": "the store's players refused it: see their output",
                }
                refused += 1
        if not pending or time.monotonic() - started >= limit:
            break
        time.sleep(delay)
        delay = min(delay * 2, match_store.MAX_POLL_SECONDS)
    for key, match in pending.items():
        plan.results[key] = {
            "id": key,
            "map": match["map"],
            "players": match["seats"],
            "error": f"no player of the store played it within {limit:.0f} s",
        }
    print(
        f"Time: waited {time.monotonic() - started:.0f} s for {len(matches)} matches "
        + ("that other players held" if take_over else "from the store's players")
        + (f"; took over {taken} whose lease ended" if taken else "")
        + (f"; {refused} refused" if refused else "")
        + (f"; {len(pending)} never came" if pending else ""),
        file=sys.stderr,
    )


def points(result: dict[str, Any], player: str) -> float:
    """A player's points in a game: a win 1, a draw 0.5, a loss 0."""
    return 0.5 if result["winner"] is None else float(result["winner"] == player)


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Standings, the table of every pair, each player's record per map and the problems."""
    record: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "games": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "failed_turns": 0,
            "slowest_turn_milliseconds": 0.0,
        }
    )
    pair_points: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    map_points: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    games = []
    errors = []
    for result in results:
        if "error" in result:
            errors.append(
                {
                    "map": result["map"],
                    "players": result["players"],
                    "error": result["error"],
                }
            )
            continue
        first, second = result["players"]
        first_score = points(result, first)
        games.append((first, second, first_score))
        for name, opponent, score, seat in (
            (first, second, first_score, result["seats"][0]),
            (second, first, 1 - first_score, result["seats"][1]),
        ):
            row = record[name]
            row["games"] += 1
            row["wins" if score == 1 else "losses" if score == 0 else "draws"] += 1
            row["failed_turns"] += seat["failed_turns"]
            row["slowest_turn_milliseconds"] = max(row["slowest_turn_milliseconds"], seat["slowest_turn_milliseconds"])
            pair_points[name][opponent][0] += score
            pair_points[name][opponent][1] += 1
            map_points[name][result["map"]][0] += score
            map_points[name][result["map"]][1] += 1
    rating = ratings.fit(games)
    standings = [
        {
            "player": name,
            "rating": round(rating[name]),
            "score": round((row["wins"] + row["draws"] / 2) / row["games"], 3),
            **row,
        }
        for name, row in sorted(record.items(), key=lambda item: (-rating[item[0]], item[0]))
    ]
    return {
        "standings": standings,
        "pairs": {name: dict(row) for name, row in pair_points.items()},
        "maps": {name: dict(row) for name, row in map_points.items()},
        "errors": errors,
    }


def losses(results: list[dict[str, Any]], player: str) -> list[dict[str, Any]]:
    """The games a player lost or drew, shortest first: the ones worth studying."""
    lost = [
        result
        for result in results
        if "error" not in result and player in result["players"] and result["winner"] != player
    ]
    return sorted(lost, key=lambda result: (result["winner"] is None, result["generations"]))


def longest_wins(results: list[dict[str, Any]], player: str) -> list[dict[str, Any]]:
    """The games a player won, longest first: a slow win hides a weakness."""
    won = [result for result in results if "error" not in result and result["winner"] == player]
    return sorted(won, key=lambda result: -result["generations"])


# Two bots are listed as alike from this share of games that ended the same to
# the soldier. In the population of iteration 36 a bot and its copy with one
# rare mechanism shared 61% to 88% of their games, two branches of one line 16%
# to 48%, and two bots with code of their own none.
ALIKE = 0.5

# A game as its player saw it end: its points, the game's length, and the
# castles and soldiers it held.
Ending = tuple[float, Any, Any, Any]


def _endings(results: list[dict[str, Any]]) -> dict[str, dict[tuple[str, str, int], Ending]]:
    """Every player's games, each under its opponent, map and seat."""
    endings: dict[str, dict[tuple[str, str, int], Ending]] = defaultdict(dict)
    for result in results:
        if "error" in result:
            continue
        for seat, name in enumerate(result["players"]):
            end = result["seats"][seat]
            endings[name][(result["players"][1 - seat], result["map"], seat)] = (
                points(result, name),
                result.get("generations"),
                end.get("castles"),
                end.get("soldiers"),
            )
    return endings


def by_luck(margins: Iterable[int]) -> float:
    """The chance that a change which does nothing gives a margin as far from 0 as the one played.

    ``margins`` are a bot's better games minus its worse ones on each map. A
    map's games move together (the same castles, the same race for them), so
    the map is what was drawn, not the game. Had the change done nothing, each
    map's margin would as likely have come out with the other sign: of all the
    ways to choose the signs, this is the share whose total is at least as far
    from 0, on the same side, as the total played. It is an exact test, with no
    assumption that games are independent, and it can't be small on few maps:
    with every changed map in the bot's favour it is one in two for one map and
    one in 64 for six.

    Returns:
        The share, from above 0 to 1; 1 when the total is 0.
    """
    played = list(margins)
    sizes = [abs(margin) for margin in played if margin]
    total = sum(played)
    if total == 0:
        return 1.0
    ways: dict[int, int] = {0: 1}
    for size in sizes:
        spread: dict[int, int] = defaultdict(int)
        for reached, count in ways.items():
            spread[reached + size] += count
            spread[reached - size] += count
        ways = spread
    return sum(count for reached, count in ways.items() if reached >= abs(total)) / 2 ** len(sizes)


@functools.cache
def _demo_lead(demo: str, written: int, size: int, color: int, other: int) -> int | None:
    """``_draw_lead`` of one writing of a demo file: a match played again gets a new answer."""
    try:
        return digest.production_lead(digest.load_demo(Path(demo)), color, other)
    except OSError, ValueError, KeyError, TypeError:
        return None


def _draw_lead(result: dict[str, Any], seat: int) -> int | None:
    """Whether the player in ``seat`` out-produced its opponent in a game (1, -1 or 0), or None when that can't be read.

    It can't when the result names no team colours or no demo, or the demo is
    missing or broken.
    """
    colors = [end.get("team_color") for end in result["seats"]]
    demo = result.get("demo")
    if demo is None or None in colors:
        return None
    try:
        file = Path(demo).stat()
    except OSError:
        return None
    return _demo_lead(str(demo), file.st_mtime_ns, file.st_size, colors[seat], colors[1 - seat])


def paired(results: list[dict[str, Any]], name: str, parent: str) -> dict[str, Any]:
    """A bot's games next to its parent's against the same opponent, on the same map, from the same seat.

    Bots are deterministic, so a game the bot's change never touched ends as
    its parent's did and says nothing about the change. The games that ended
    otherwise are the evidence: how many the bot did better in, how many worse,
    the points it gained in all of them, and ``luck``, the chance that a change
    which does nothing gives such a margin (``by_luck``, over ``maps``, each
    map's better minus worse). The games of the two against each other are
    left out: the head-to-head counts those.

    A game is better when it ended with more points, and, when both drew,
    when the bot had the production lead over the game and its parent didn't,
    or the parent was behind and the bot wasn't (``digest.production_lead``):
    a draw is not the end of what a game says. ``drawn_better`` and
    ``drawn_worse`` count those among ``better`` and ``worse``. ``unread``
    counts the pairs of drawn games of which one couldn't be read: such a pair
    counts as the same, since half a comparison is none.
    """
    games: dict[str, dict[tuple[str, str, int], tuple[dict[str, Any], int]]] = {name: {}, parent: {}}
    for result in results:
        if "error" in result:
            continue
        for seat, player in enumerate(result["players"]):
            if player in games:
                games[player][(result["players"][1 - seat], result["map"], seat)] = (result, seat)
    count: dict[str, Any] = {"better": 0, "worse": 0, "same": 0, "net": 0.0}
    count |= {"drawn_better": 0, "drawn_worse": 0, "unread": 0}
    maps: dict[str, int] = defaultdict(int)

    for case, (mine, seat) in games[name].items():
        if case[0] in (name, parent) or case not in games[parent]:
            continue
        theirs, their_seat = games[parent][case]
        gain = points(mine, name) - points(theirs, parent)
        count["net"] += gain
        drawn = gain == 0 and mine["winner"] is None
        if drawn:
            leads = (_draw_lead(mine, seat), _draw_lead(theirs, their_seat))
            if leads[0] is None or leads[1] is None:
                count["unread"] += 1
            else:
                gain = leads[0] - leads[1]
        count["better" if gain > 0 else "worse" if gain < 0 else "same"] += 1
        if drawn and gain:
            count["drawn_better" if gain > 0 else "drawn_worse"] += 1
        maps[case[1]] += (gain > 0) - (gain < 0)
    return count | {"maps": dict(sorted(maps.items())), "luck": by_luck(list(maps.values()))}


def alike(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The pairs of bots that play alike, the most alike first.

    Two bots met the same opponent on the same map from the same seat. When
    those games ended the same to the soldier (the result, the length, the
    castles and soldiers held) in ``ALIKE`` of the cases or more, the two make
    the same commands nearly everywhere: as opponents they are one bot counted
    twice, and as members of the population one of them adds nothing. The
    default bots are left out: nobody chooses between them.
    """
    endings = _endings(results)
    names = sorted(name for name in endings if not ANCHOR.fullmatch(name))
    pairs = []
    for first, second in combinations(names, 2):
        cases = [case for case in endings[first] if case[0] not in (first, second) and case in endings[second]]
        if not cases:
            continue
        same_game = sum(endings[first][case] == endings[second][case] for case in cases)
        if same_game < ALIKE * len(cases):
            continue
        same_result = sum(endings[first][case][0] == endings[second][case][0] for case in cases)
        pairs.append(
            {
                "bots": [first, second],
                "games": len(cases),
                "same_game": round(same_game / len(cases), 3),
                "same_result": round(same_result / len(cases), 3),
            }
        )
    return sorted(pairs, key=lambda pair: (-pair["same_game"], pair["bots"]))


def _where(maps: list[Path]) -> str:
    """A run's maps in words: a whole set, both sets, or how many of them."""
    for directory, name in ((MAPS / "train", "training"), (MAPS / "holdout", "holdout")):
        if sorted(maps) == sorted(directory.glob("*.json")):
            return f"the {len(maps)} {name} maps"
    if sorted(maps) == sorted(MAPS.glob("*/*.json")):
        return f"all {len(maps)} maps, training and holdout"
    return f"{len(maps)} of the maps: not the table the rule for bots that play alike reads"


def alike_table(pairs: list[dict[str, Any]], where: str) -> list[str]:
    """The lines of the table of ``alike``'s pairs, or none without a pair.

    Args:
        pairs: What ``alike`` returned.
        where: The maps the games were played on, in words: the rule that one of two bots leaves reads the
            training maps' table only.
    """
    if not pairs:
        return []
    lines = [
        "",
        f"Bots that play alike on {where} (from {ALIKE:.0%} of their games against the same opponent, on the same "
        "map and from the same seat ending the same to the soldier):",
        "",
        "| Bots | The same game | The same result | Games |",
        "|---|---|---|---|",
    ]
    lines += [
        f"| `{pair['bots'][0]}`, `{pair['bots'][1]}` | {pair['same_game']:.0%} | {pair['same_result']:.0%} "
        f"| {pair['games']} |"
        for pair in pairs
    ]
    return lines


def game_line(result: dict[str, Any]) -> str:
    """One game of a list: its map, seats, outcome, length and demo."""
    return (
        f"- {result['map']}: {' vs '.join(result['players'])}: {result['outcome']['summary']} "
        f"in {result['generations']} generations: `{result['demo']}`"
    )


# What a margin comes to, by the chance of it by luck (the ``league-evidence``
# skill, which also says what each kind of candidate needs on which maps).
CONFIRMED, CLEAR = 0.20, 0.05


def reading(margin: int, luck: float) -> str:
    """A run's margin in the selection's words: clear, confirmed, nothing, worse or clearly worse."""
    if margin > 0:
        return "clear" if luck <= CLEAR else "confirmed" if luck <= CONFIRMED else "nothing"
    if margin < 0:
        return "clearly worse" if luck <= CONFIRMED else "worse"
    return "nothing"


def chance(share: float) -> str:
    """A chance as the tables print it: a percentage, and never a 0 that isn't one."""
    return "under 0.1%" if share < 0.001 else f"{share:.1%}"


def against_parents(summary: dict[str, Any], parents: dict[str, str], whole: bool) -> list[str]:
    """A table of each listed bot next to its parent: the numbers the selection reads.

    The head-to-head points, and from a whole round robin the two ratings and
    the bot's games against the others next to its parent's (``paired``):
    their margin (better minus worse), the maps the bot did better and worse
    on, the chance of such a margin by luck, a map's games counted as one
    (``by_luck``), and what that comes to on this run's maps (``reading``).
    It promotes nothing: the ``league-evidence`` skill says which reading each
    kind of candidate needs on which maps.

    Args:
        summary: What ``summarize`` returned, with ``paired`` when the round robin was whole.
        parents: Each listed bot's parent.
        whole: Whether every pair played, so that the ratings count.
    """
    rating = {row["player"]: row["rating"] for row in summary["standings"]}
    changed = summary.get("paired", {}) if whole else {}
    rows = []
    for name, parent in parents.items():
        points = summary["pairs"].get(name, {}).get(parent)
        if points is None:
            continue
        cells = [f"`{name}`", f"`{parent}`", f"{points[0]:g}/{points[1]:g}"]
        if whole:
            cells.append(f"{rating[name]} ({rating[parent]})")
        if name in changed:
            better, worse, same = changed[name]["better"], changed[name]["worse"], changed[name]["same"]
            margins = changed[name]["maps"].values()
            cells.append(f"{better} better, {worse} worse, {same} the same")
            cells.append(f"{changed[name]['drawn_better']} better, {changed[name]['drawn_worse']} worse")
            cells.append(f"{better - worse:+d}")
            cells.append(
                f"{sum(margin > 0 for margin in margins)} better, {sum(margin < 0 for margin in margins)} worse"
            )
            cells.append(chance(changed[name]["luck"]))
            cells.append(reading(better - worse, changed[name]["luck"]))
        rows.append("| " + " | ".join(cells) + " |")
    if not rows:
        return []
    header = ["Bot", "Parent", "Points against the parent"]
    if whole:
        header.append("Rating (parent's)")
    if changed:
        header += [
            "Its games against the others, next to the parent's",
            "Of them, draws told apart by production",
            "Margin",
            "Maps",
            "By luck",
            "On these maps",
        ]
    lines = ["", "Each listed bot against its parent" + ("" if whole else " (ratings don't count here)") + ":", ""]
    lines += ["| " + " | ".join(header) + " |", "|---" * len(header) + "|", *rows]
    return lines


def markdown(
    summary: dict[str, Any],
    results: list[dict[str, Any]],
    listed: list[str],
    list_games: bool,
    parent_table: list[str] | None = None,
) -> str:
    """The summary as Markdown tables.

    Args:
        summary: What ``summarize`` returned.
        results: The matches.
        listed: The players whose lost games and longest wins are listed.
        list_games: False leaves those lists out, as for holdout maps, whose
            games nobody reads.
        parent_table: The lines of ``against_parents``, printed after the standings.
    """
    lines = [
        "| Player | Rating | Score | W | D | L | Failed turns | Slowest turn (ms) |",
        "|---|---|---|---|---|---|---|---|",
    ]
    order = [row["player"] for row in summary["standings"]]
    for row in summary["standings"]:
        lines.append(
            f"| {row['player']} | {row['rating']} | {row['score']:.3f} | {row['wins']} | {row['draws']} "
            f"| {row['losses']} | {row['failed_turns']} | {row['slowest_turn_milliseconds']:.1f} |"
        )
    lines += parent_table or []

    def cell(points: list[float] | None) -> str:
        return "" if points is None else f"{points[0]:g}/{points[1]:g}"

    lines += ["", "Points of the row's player against the column's:", ""]
    lines += ["| | " + " | ".join(order) + " |", "|---" * (len(order) + 1) + "|"]
    for name in order:
        cells = [cell(summary["pairs"][name].get(opponent)) for opponent in order]
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    map_names = sorted({result["map"] for result in results})
    lines += ["", "Points per map:", ""]
    lines += ["| | " + " | ".join(map_names) + " |", "|---" * (len(map_names) + 1) + "|"]
    for name in order:
        cells = [cell(summary["maps"][name].get(map_name)) for map_name in map_names]
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    for error in summary["errors"]:
        lines.append(f"\nNOT PLAYED {error['map']} {' vs '.join(error['players'])}: {error['error']}")
    if listed and not list_games:
        lines += ["", "Holdout maps were played: their games are not listed, and nobody digests them."]
    for name in listed if list_games else []:
        lines += ["", f"Games {name} didn't win (demo to digest):", ""]
        lines += [game_line(result) for result in losses(results, name)[:20]]
        lines += ["", f"Longest wins of {name}:", ""]
        lines += [game_line(result) for result in longest_wins(results, name)[:5]]
    failures = [
        f"- {result['map']} {' vs '.join(result['players'])}: {seat['name']} turn {failure['turn']}: "
        f"{failure['message'].strip().splitlines()[-1][:300]}"
        for result in results
        if "error" not in result
        for seat in result["seats"]
        for failure in seat["failures"][:1]
    ]
    if failures:
        lines += ["", "Failed turns (the first of each game):", "", *failures[:30]]
    return "\n".join(lines) + "\n"


def failed_players(results: list[dict[str, Any]]) -> list[str]:
    """The players that failed a turn in any of the games."""
    return sorted(
        {
            seat["name"]
            for result in results
            if "error" not in result
            for seat in result["seats"]
            if seat["failed_turns"]
        }
    )


def shard_summary(results: list[dict[str, Any]], shard: tuple[int, int]) -> dict[str, Any]:
    """What a shard played, without ratings: a slice of the matches rates nobody.

    Its holdout games' numbers stay unseen too, as the iteration's selection needs.
    """
    errors = [
        {"map": result["map"], "players": result["players"], "error": result["error"]}
        for result in results
        if "error" in result
    ]
    failed_games = sum(
        1 for result in results if "error" not in result and any(seat["failed_turns"] for seat in result["seats"])
    )
    return {
        "shard": f"{shard[0]}/{shard[1]}",
        "matches": len(results),
        "failed_games": failed_games,
        "failed_players": failed_players(results),
        "errors": errors,
    }


def shard_report(summary: dict[str, Any]) -> str:
    """A shard's summary as text: how many matches, and which went wrong."""
    lines = [
        f"Shard {summary['shard']}: {summary['matches']} matches, {summary['failed_games']} with a failed turn, "
        f"{len(summary['errors'])} not played. No standings: a shard's games rate nobody; "
        "play the tournament without --shard once every shard's cache is in runs/cache."
    ]
    lines += [f"NOT PLAYED {e['map']} {' vs '.join(e['players'])}: {e['error']}" for e in summary["errors"]]
    return "\n".join(lines) + "\n"


def run(tournament: Tournament, run_id: str) -> tuple[dict[str, Any], str]:
    """Play a tournament and write its results, summary and tables under ``runs/<run_id>/``.

    A shard's summary has no standings, pairs or maps: the tables come from the
    whole tournament, played again from the shards' caches together.
    """
    run_directory = RUNS / run_id
    run_directory.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    results = play(tournament, run_directory)
    playing = time.monotonic() - started
    if tournament.shard:
        summary = shard_summary(results, tournament.shard)
        table = shard_report(summary)
    else:
        summary = summarize(results) | {"matches": len(results), "failed_players": failed_players(results)}
        parents = {name: parent for name, parent in tournament.parents.items() if name in tournament.listed}
        whole = not tournament.focus
        # Only a whole round robin has every bot's games against the same
        # opponents: a focused run's would compare a bot with nothing.
        pairs = alike(results) if whole else []
        if whole:
            summary["paired"] = {name: paired(results, name, parent) for name, parent in parents.items()}
            unread = sum(compared["unread"] for compared in summary["paired"].values())
            if unread:
                print(
                    f"league: {unread} pairs of drawn games had a demo that couldn't be read: they count as the same",
                    file=sys.stderr,
                )
            summary["alike"] = pairs
        parent_table = against_parents(summary, parents, whole=whole)
        parent_table += alike_table(pairs, _where(tournament.maps))
        table = markdown(summary, results, tournament.listed, not has_holdout(tournament.maps), parent_table)
    with (run_directory / "results.jsonl").open("w", encoding="utf-8") as file:
        for result in results:
            file.write(json.dumps(result) + "\n")
    (run_directory / "summary.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    (run_directory / "summary.md").write_text(table, encoding="utf-8")
    after = time.monotonic() - started - playing
    # Where a tournament's time goes: finding and playing its matches (the
    # cache's reading, the wait for another tournament, the games), then
    # everything after (ratings, tables, files).
    print(
        f"Time: {playing + after:.0f} s in all: {playing:.0f} s to read or play {len(results)} matches, "
        f"{after:.0f} s after (ratings, tables, files)",
        file=sys.stderr,
    )
    return summary, table
