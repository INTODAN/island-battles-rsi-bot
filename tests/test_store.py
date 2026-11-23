import hashlib
import io
import json
import multiprocessing
import multiprocessing.synchronize
import os
import sys
import tarfile
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

import boto3
import pytest
from botocore.stub import Stubber

from league_tools import cli, gobots, player, store, tournament

BUILD = "b" * 64


@dataclass
class League:
    """A league of fake bots with a runner that records what it plays, and a match store in a directory."""

    root: Path
    bots: Path
    map_file: Path
    store_root: Path
    # Every match played, by key, one line each, whichever process played it.
    played_log: Path
    failing: set[str] = field(default_factory=set)
    built_from: list[Path] = field(default_factory=list)

    def played(self) -> list[str]:
        return self.played_log.read_text().split() if self.played_log.exists() else []

    def matches(self, names: list[str]) -> list[tuple[Path, list[str]]]:
        pairs = [(first, second) for index, first in enumerate(names) for second in names[index + 1 :]]
        return [(self.map_file, seats) for pair in pairs for seats in (list(pair), list(pair[::-1]))]

    def open(self, mode: str = "play") -> store.Store:
        return store.Store(store.DirectoryBackend(self.store_root), BUILD, mode)


def bot(directory: Path, name: str, body: str = "") -> None:
    (directory / name).mkdir(parents=True, exist_ok=True)
    (directory / name / "main.go").write_text(f"package main\n\n// {name}\n{body}")


@pytest.fixture
def league(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> League:
    bots = tmp_path / "bots"
    for name in ("first", "second", "third", "fourth"):
        bot(bots, name)
    map_file = tmp_path / "maps" / "duel.json"
    map_file.parent.mkdir()
    map_file.write_text(json.dumps({"map_name": "duel"}))
    fake = League(tmp_path, bots, map_file, tmp_path / "store", tmp_path / "played.log")
    monkeypatch.setattr(tournament, "BOTS", bots)
    monkeypatch.setattr(tournament, "CACHE", tmp_path / "cache")
    monkeypatch.setattr(tournament, "player_specification", lambda name, binary=None: {})
    monkeypatch.setattr(tournament, "load_opponents", lambda: {})
    monkeypatch.setattr(tournament.engine, "build", lambda: tournament.engine.Build(BUILD, tmp_path / "runner"))
    monkeypatch.setattr(player, "PLAYER_RUNS", tmp_path / "player")
    monkeypatch.setattr(store, "POLL_SECONDS", 0.02)
    monkeypatch.setattr(store, "MAX_POLL_SECONDS", 0.1)
    monkeypatch.setenv(store.STORE_VARIABLE, str(fake.store_root))

    def build(names: object, bots: Path = bots, environment: dict[str, str] | None = None) -> dict[str, Path]:
        fake.built_from.append(bots)
        return {name: tmp_path / "bin" / name for name in names}  # ty: ignore[not-iterable]

    def play(binary: Path, schedule: dict, worker_log: Path, environment: dict[str, str] | None = None) -> list[dict]:
        lines = []
        demos = Path(schedule["demo_directory"])
        demos.mkdir(parents=True, exist_ok=True)
        for match in schedule["matches"]:
            time.sleep(0.005)
            with fake.played_log.open("a") as log:
                log.write(match["id"] + "\n")
            (demos / f"{match['id']}.json.gz").write_bytes(b"demo of " + match["id"].encode())
            seats = [
                {
                    "name": name,
                    "failed_turns": int(name in fake.failing),
                    "failures": [],
                    "slowest_turn_milliseconds": 1,
                }
                for name in match["seats"]
            ]
            lines.append(
                {
                    "id": match["id"],
                    "map": match["map"],
                    "players": match["seats"],
                    "winner": match["seats"][0],
                    "generations": 10,
                    "seats": seats,
                }
            )
        return lines

    monkeypatch.setattr(tournament.gobots, "build", build)
    monkeypatch.setattr(tournament.engine, "play", play)
    return fake


def test_without_a_store_nothing_changes(league: League, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(store.STORE_VARIABLE)
    assert store.open_store(BUILD) is None
    results = tournament.play_matches(league.matches(["first", "second"]), league.root / "run")
    assert len(results) == len(league.played()) == 2 and not league.store_root.exists()


def test_a_match_played_by_one_machine_is_read_by_another(league: League, monkeypatch: pytest.MonkeyPatch) -> None:
    matches = league.matches(["first", "second", "level3"])
    first = tournament.play_matches(matches, league.root / "run")
    assert len(league.played()) == 6
    # Another machine: its own empty cache, the same store.
    monkeypatch.setattr(tournament, "CACHE", league.root / "other-cache")
    again = tournament.play_matches(matches, league.root / "run")
    assert len(league.played()) == 6
    assert [result["id"] for result in again] == [result["id"] for result in first]
    assert all(Path(result["demo"]).parent == league.root / "other-cache" for result in again)
    kept = json.loads(next((league.store_root / BUILD[:16] / "results").glob("*.json")).read_text())
    assert set(kept["played_by"]) == {"machine", "run"}
    # Every lease was given back.
    assert not list((league.store_root / BUILD[:16] / "leases").iterdir())


def _machine(
    cache: Path, matches: list[tuple[Path, list[str]]], start: multiprocessing.synchronize.Event, out: Path
) -> None:
    tournament.CACHE = cache
    os.environ[store.PLAYER_VARIABLE] = cache.name
    start.wait()
    results = tournament.play_matches(matches, cache.parent / f"run-{cache.name}")
    out.write_text(json.dumps(sorted(result["id"] for result in results if "error" not in result)))


def test_two_machines_at_once_play_each_match_once(league: League) -> None:
    fork = multiprocessing.get_context("fork")
    start = fork.Event()
    plans = {
        "machine-a": league.matches(["first", "second", "third"]),
        "machine-b": league.matches(["first", "second", "fourth"]),
    }
    machines = [
        fork.Process(
            target=_machine,
            args=(league.root / name, matches, start, league.root / f"{name}.out"),
        )
        for name, matches in plans.items()
    ]
    for machine in machines:
        machine.start()
    start.set()
    for machine in machines:
        machine.join(60)
        assert machine.exitcode == 0
    played = league.played()
    # 3 pairs each, 1 in common, both sides: 10 matches, each played once, and each machine has all of its own.
    assert len(played) == len(set(played)) == 10
    for name in plans:
        assert len(json.loads((league.root / f"{name}.out").read_text())) == 6


def test_an_expired_lease_is_taken_over_once_and_a_live_one_is_not(league: League) -> None:
    dead, alive = league.open(), league.open()
    dead.played_by = {"machine": "dead", "run": "1"}
    old = dead.lease("key", -1)
    assert old is not None and dead.holder("key")["expired"]  # ty: ignore[not-subscriptable]
    contenders = [league.open() for _ in range(8)]
    won: list[store.Lease] = []
    barrier = threading.Barrier(len(contenders))

    def take(contender: store.Store) -> None:
        barrier.wait()
        lease = contender.lease("key", 60)
        if lease is not None:
            won.append(lease)

    threads = [threading.Thread(target=take, args=(contender,)) for contender in contenders]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert len(won) == 1
    # The dead player's lease is no longer its own: it can neither renew nor release it.
    assert dead.renew(old, 60) is None
    dead.release(old)
    assert alive.lease("key", 60) is None
    renewed = contenders[0].renew(won[0], 60)
    assert renewed is not None and renewed.tag != won[0].tag


def test_a_tournament_waits_for_a_lease_and_takes_it_over_when_it_ends(
    league: League, capsys: pytest.CaptureFixture[str]
) -> None:
    matches = league.matches(["first", "second"])
    key = tournament.match_key(
        BUILD,
        hashlib.sha256(league.map_file.read_bytes()).hexdigest(),
        ["first", "second"],
        [gobots.fingerprint(league.bots / "first"), gobots.fingerprint(league.bots / "second")],
        [300, 2000],
    )
    other = league.open()
    other.played_by = {"machine": "gone", "run": "1"}
    assert other.lease(key, 0.3) is not None
    results = tournament.play_matches(matches, league.root / "run")
    assert len(results) == 2 and all("error" not in result for result in results)
    assert sorted(league.played()) == sorted(result["id"] for result in results)
    assert "took over 1 whose lease ended" in capsys.readouterr().err


def test_a_failed_turn_is_played_again_three_times_at_most(league: League) -> None:
    matches = league.matches(["first", "second"])
    league.failing.add("second")
    failed = league.store_root / BUILD[:16] / "failed"
    for attempt in (1, 2):
        results = tournament.play_matches(matches, league.root / "run")
        assert len(league.played()) == 2 * attempt
        assert len(list(failed.glob("*.json"))) == 2 * attempt
        assert not (league.store_root / BUILD[:16] / "results").exists()
        assert tournament.failed_players(results) == ["second"]
    tournament.play_matches(matches, league.root / "run")
    # The third failure is the result: kept in the store and the cache, never played again, and --strict fails on it.
    assert len(league.played()) == 6 and len(list(failed.glob("*.json"))) == 6
    assert len(list((league.store_root / BUILD[:16] / "results").glob("*.json"))) == 2
    results = tournament.play_matches(matches, league.root / "run")
    assert len(league.played()) == 6 and tournament.failed_players(results) == ["second"]


def test_request_mode_queues_and_never_writes_a_result_and_a_player_plays_the_queue(
    league: League, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv(store.MODE_VARIABLE, "request")
    monkeypatch.setenv(store.WAIT_VARIABLE, "0.2")
    matches = league.matches(["first", "second", "level3"])
    results = tournament.play_matches(matches, league.root / "run")
    namespace = league.store_root / BUILD[:16]
    assert league.played() == [] and all("within" in result["error"] for result in results)
    assert sorted(path.name for path in namespace.iterdir()) == ["code", "maps", "queue"]
    assert len(list((namespace / "queue").iterdir())) == 6 and len(list((namespace / "code").iterdir())) == 2
    with pytest.raises(RuntimeError):
        league.open("request").put_result("key", {}, b"")

    # A player plays the queue, from the store's code alone, without the store set to request.
    monkeypatch.delenv(store.MODE_VARIABLE)
    monkeypatch.setattr(player, "check_imports", lambda tree, name, environment=None: None)
    assert cli.main(["player", "--drain"]) == 0
    assert len(league.played()) == 6 and not list((namespace / "queue").iterdir())
    assert league.built_from and all(
        bots != league.bots and bots.parent.parent == league.root / "player" for bots in league.built_from
    )

    # The requester, on a machine of its own, now finds every match in the store.
    monkeypatch.setenv(store.MODE_VARIABLE, "request")
    monkeypatch.setattr(tournament, "CACHE", league.root / "requester-cache")
    capsys.readouterr()
    again = tournament.play_matches(matches, league.root / "run")
    assert len(league.played()) == 6 and all("error" not in result for result in again)
    assert "6 cached (6 of them from the store), 0 to play" in capsys.readouterr().err


def _request(league: League, names: list[str]) -> dict:
    """Queue one match as request mode does, and return its entry."""
    requester = league.open("request")
    map_hash = requester.put_map(league.map_file.read_bytes())
    fingerprints = [gobots.fingerprint(league.bots / name) for name in names]
    for name, fingerprint in zip(names, fingerprints, strict=True):
        requester.put_code(fingerprint, league.bots / name)
    entry = {
        "key": tournament.match_key(BUILD, map_hash, names, fingerprints, [300, 2000]),
        "build": BUILD,
        "map": {"name": "duel", "sha256": map_hash},
        "seats": names,
        "fingerprints": fingerprints,
        "settings": [300, 2000],
    }
    assert requester.enqueue(entry)
    return entry


def test_a_player_refuses_code_that_is_not_what_its_fingerprint_says(
    league: League, capsys: pytest.CaptureFixture[str]
) -> None:
    entry = _request(league, ["first", "second"])
    # Someone writes other code under first's fingerprint.
    bot(league.root / "tampered", "first", "func main() {}\n")
    league.open().backend.write(
        f"{BUILD[:16]}/code/{entry['fingerprints'][0]}.tar.gz", store.pack_bot(league.root / "tampered" / "first")
    )
    assert player.run(drain=True) == 0
    assert league.played() == [] and not (league.store_root / BUILD[:16] / "results").exists()
    assert not league.open().is_queued(entry["key"])
    assert "not the requested" in capsys.readouterr().err


def test_a_player_refuses_a_key_that_is_not_its_game(league: League, capsys: pytest.CaptureFixture[str]) -> None:
    entry = _request(league, ["first", "second"])
    forged = entry | {"key": "0" * 32}
    assert league.open("request").enqueue(forged)
    league.open().dequeue(entry["key"])
    assert player.run(drain=True) == 0
    assert league.played() == [] and "its key is not the key" in capsys.readouterr().err


def test_a_player_refuses_a_bot_that_imports_what_a_bot_may_not(
    league: League, capsys: pytest.CaptureFixture[str]
) -> None:
    bot(league.bots, "first", 'import "os"\n\nfunc main() { os.Exit(0) }\n')
    bot(league.bots, "second", 'import "fmt"\n\nfunc main() { fmt.Println() }\n')
    entry = _request(league, ["first", "second"])
    assert player.run(drain=True) == 0
    assert league.played() == [] and not league.open().is_queued(entry["key"])
    assert "first imports what a bot may not: os" in capsys.readouterr().err
    # The bot's own imports, read by go list as the compiler reads them.
    tree = league.root / "tree"
    (tree / "bots").mkdir(parents=True)
    for module_file in ("go.mod", "go.sum"):
        (tree / module_file).write_bytes((tournament.LEAGUE / module_file).read_bytes())
    bot(tree / "bots", "fine", 'import "fmt"\n\nfunc main() { fmt.Println() }\n')
    player.check_imports(tree, "fine")


def test_a_bots_code_is_packed_the_same_and_unpacked_only_as_go_files(tmp_path: Path) -> None:
    bot(tmp_path / "bots", "first", "func main() {}\n")
    (tmp_path / "bots" / "first" / "bot.toml").write_text('status = "active"\n')
    packed = store.pack_bot(tmp_path / "bots" / "first")
    time.sleep(0.01)
    assert store.pack_bot(tmp_path / "bots" / "first") == packed
    store.unpack_bot(packed, tmp_path / "copy")
    assert [path.name for path in (tmp_path / "copy").iterdir()] == ["main.go"]
    assert gobots.fingerprint(tmp_path / "copy") == gobots.fingerprint(tmp_path / "bots" / "first")
    for name in ("../escape.go", "notes.txt", "main_test.go"):
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
            info = tarfile.TarInfo(name)
            info.size = 1
            archive.addfile(info, io.BytesIO(b"x"))
        with pytest.raises(ValueError):
            store.unpack_bot(buffer.getvalue(), tmp_path / "other")


def test_a_store_is_named_by_its_location(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    assert store.open_store(BUILD) is None
    monkeypatch.setenv(store.STORE_VARIABLE, "s3://league-store/matches")
    opened = store.open_store(BUILD)
    assert opened is not None and isinstance(opened.backend, store.S3Backend)
    assert (opened.backend.bucket, opened.backend.prefix, opened.namespace) == ("league-store", "matches/", BUILD[:16])
    monkeypatch.setenv(store.STORE_VARIABLE, f"file://{tmp_path}")
    opened = store.open_store(BUILD)
    assert opened is not None and isinstance(opened.backend, store.DirectoryBackend)
    assert opened.backend.root == tmp_path
    monkeypatch.setenv(store.MODE_VARIABLE, "write")
    with pytest.raises(ValueError):
        store.open_store(BUILD)
    monkeypatch.setenv(store.STORE_VARIABLE, "s3://")
    with pytest.raises(ValueError):
        store.backend_at("s3://")


def test_the_s3_store_writes_leases_only_on_its_conditions() -> None:
    client = boto3.client("s3", region_name="eu-central-1", aws_access_key_id="x", aws_secret_access_key="x")
    backend = store.S3Backend("league-store", "matches", client=client)
    key = "matches/ns/leases/k"
    with Stubber(client) as stub:
        stub.add_response(
            "put_object", {"ETag": '"one"'}, {"Bucket": "league-store", "Key": key, "Body": b"a", "IfNoneMatch": "*"}
        )
        stub.add_client_error("put_object", "PreconditionFailed", http_status_code=412)
        stub.add_response(
            "put_object", {"ETag": '"two"'}, {"Bucket": "league-store", "Key": key, "Body": b"b", "IfMatch": '"one"'}
        )
        stub.add_client_error("put_object", "PreconditionFailed", http_status_code=412)
        stub.add_client_error("put_object", "ConditionalRequestConflict", http_status_code=409)
        stub.add_response("delete_object", {}, {"Bucket": "league-store", "Key": key, "IfMatch": '"two"'})
        stub.add_client_error("delete_object", "PreconditionFailed", http_status_code=412)
        stub.add_client_error("get_object", "NoSuchKey", http_status_code=404)
        stub.add_client_error("get_object", "AccessDenied", http_status_code=403)
        assert backend.create("ns/leases/k", b"a") == '"one"'
        assert backend.create("ns/leases/k", b"a") is None
        assert backend.replace("ns/leases/k", b"b", '"one"') == '"two"'
        assert backend.replace("ns/leases/k", b"c", '"one"') is None
        assert backend.replace("ns/leases/k", b"c", '"one"') is None
        assert backend.delete("ns/leases/k", '"two"') is True
        assert backend.delete("ns/leases/k", '"two"') is False
        assert backend.read("ns/leases/k") is None
        with pytest.raises(Exception, match="AccessDenied"):
            backend.read("ns/leases/k")
        stub.assert_no_pending_responses()


def test_the_lambda_player_drains_batches_until_its_time_is_nearly_up(monkeypatch: pytest.MonkeyPatch) -> None:
    sys.path.insert(0, str(Path(__file__).parent.parent / "hosting" / "players"))
    import lambda_player

    assert lambda_player.arguments({"batch": 10}, 900_000) == [
        "player",
        "--drain",
        "--batch",
        "10",
        "--max-seconds",
        "780",
    ]
    assert lambda_player.arguments(None, 60_000)[3:] == ["25", "--max-seconds", "1"]
    assert lambda_player.arguments({"batch": 10**6}, 900_000)[3] == "200"
    assert lambda_player.arguments({"batch": "all"}, 900_000)[3] == "25"
    called: list[list[str]] = []
    monkeypatch.setattr(cli, "main", lambda argv: called.append(argv) or 0)

    class Context:
        def get_remaining_time_in_millis(self) -> int:
            return 300_000

    assert lambda_player.handler({}, Context())["status"] == 0
    assert called == [["player", "--drain", "--batch", "25", "--max-seconds", "180"]]


def test_a_bot_that_doesnt_compile_is_refused_and_the_rest_of_the_batch_plays(
    league: League, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    broken = _request(league, ["first", "second"])
    fine = _request(league, ["third", "fourth"])
    monkeypatch.setattr(player, "check_imports", lambda tree, name, environment=None: None)

    def build(names: object, bots: Path = league.bots, environment: dict[str, str] | None = None) -> dict[str, Path]:
        names = list(names)  # ty: ignore[invalid-argument-type]
        if "first" in names:
            raise RuntimeError("bots/first/main.go:3: undefined: x")
        return {name: league.root / "bin" / name for name in names}

    monkeypatch.setattr(tournament.gobots, "build", build)
    assert player.run(drain=True) == 0
    assert league.played() == [fine["key"]]
    assert not league.open().is_queued(broken["key"]) and "first doesn't compile" in capsys.readouterr().err


def test_a_lease_renewed_while_its_match_ends_is_released_with_its_new_tag(league: League) -> None:
    held = league.open().lease("k" * 32, 0.05)
    assert held is not None
    beat = store.Heartbeat(league.open(), [held], interval=0.01)
    with beat:
        time.sleep(0.1)
        lease = beat.pop("k" * 32)
    assert lease is not None
    league.open().release(lease)
    assert league.open().holder("k" * 32) is None
