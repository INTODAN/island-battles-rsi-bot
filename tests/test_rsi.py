"""The automated iteration: the notifier, the choice of real games to study and the scope check."""

import argparse
import io
import json
import sys
import zipfile
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "hosting" / "rsi"))

import notifier  # noqa: E402
import real_games  # noqa: E402
import run_times  # noqa: E402
import scope  # noqa: E402


def _event(*keys: str) -> dict[str, Any]:
    return {"Records": [{"s3": {"bucket": {"name": "games-bucket"}, "object": {"key": key}}} for key in keys]}


def test_the_notifier_reads_only_game_zips() -> None:
    event = _event("games/12/game-12.zip", "games/12/game.json", "games/13/game-14.zip", "other/game-1.zip")
    assert notifier.zipped_games(event) == [("games-bucket", 12)]
    assert notifier.zipped_games({"Records": [{"s3": {"bucket": {"name": "b"}, "object": {"key": None}}}]}) == []


def test_the_notifier_dispatches_finished_games_with_a_final_demo() -> None:
    summaries = {
        1: {"status": "finished", "demo": "full"},
        2: {"status": "finished", "demo": "pending"},
        3: {"status": "finished", "demo": "partial", "estimated": True},
        4: {"status": "playing"},
    }
    sent: list[list[int]] = []

    def send(ids: list[int]) -> int:
        sent.append(ids)
        return 204

    event = _event(*(f"games/{n}/game-{n}.zip" for n in (1, 2, 3, 4, 5)))
    assert notifier.notify(event, lambda _bucket, game_id: summaries.get(game_id), send) == [1, 3]
    assert sent == [[1, 3]]
    assert notifier.dispatch_body([3, 1, 3]) == {"event_type": "real-game", "client_payload": {"game_ids": [1, 3]}}


def test_the_notifier_sends_nothing_for_a_pending_game() -> None:
    def send(ids: list[int]) -> int:
        raise AssertionError("nothing to send")

    event = _event("games/2/game-2.zip")
    assert notifier.notify(event, lambda _b, _g: {"status": "finished", "demo": "pending"}, send) == []


def test_the_notifier_reads_the_summary_inside_the_zip() -> None:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("game.json", json.dumps({"game_id": 3, "status": "finished", "demo": "full"}))
    assert notifier.packed_summary(buffer.getvalue()) == {"game_id": 3, "status": "finished", "demo": "full"}
    empty = io.BytesIO()
    with zipfile.ZipFile(empty, "w") as archive:
        archive.writestr("demo.json", "{}")
    assert notifier.packed_summary(empty.getvalue()) is None


def test_the_studied_games_are_read_from_the_ledger_list(tmp_path: Path) -> None:
    path = tmp_path / "real-games.txt"
    path.write_text("# a comment\n12 2026-11-22\n\n40 2026-11-23\n")
    assert real_games.studied(path) == {12, 40}
    assert real_games.studied(tmp_path / "none.txt") == set()
    assert real_games.studied(ROOT / "ledger" / "real-games.txt") is not None


def test_only_new_final_games_are_studied_newest_first_kept() -> None:
    summaries = [{"game_id": n, "status": "finished", "demo": "full"} for n in (5, 1, 9, 7, 3)] + [
        {"game_id": 11, "status": "finished", "demo": "pending"},
        {"game_id": 12, "status": "playing"},
    ]
    assert real_games.to_study(summaries, {7}, limit=2) == [5, 9]
    assert real_games.to_study(summaries, {7}, limit=0) == [1, 3, 5, 9]


def test_a_later_job_names_the_games_it_downloads() -> None:
    assert real_games.parse_ids("471, 472,") == [471, 472]
    assert real_games.parse_ids("") == []
    with pytest.raises(argparse.ArgumentTypeError):
        real_games.parse_ids("471,../x")


def test_a_zip_is_unpacked_by_its_known_names_only(tmp_path: Path) -> None:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("demo.json", "{}")
        archive.writestr("game.json", "{}")
        archive.writestr("../escape.txt", "no")
        archive.writestr("bot.py", "no")
    real_games.unpack(buffer.getvalue(), tmp_path / "7")
    assert sorted(path.name for path in tmp_path.rglob("*") if path.is_file()) == ["demo.json", "game.json"]


def test_the_scope_allows_bots_the_ledger_the_deployed_bot_and_new_maps() -> None:
    allowed = [
        ("A", "bots/ori_fast/main.go"),
        ("M", "bots/ori_hold/bot.toml"),
        ("D", "bots/old_bot/main.go"),
        ("M", "ledger/iterations.md"),
        ("M", "ledger/real-games.txt"),
        ("M", "ledger/progress.csv"),
        ("A", "ledger/studies/471.md"),
        ("M", "hosting/lambda/bot"),
        ("A", "maps/train/new_map.json"),
    ]
    assert scope.out_of_scope(allowed) == []
    refused = [
        ("M", ".github/workflows/checks.yml"),
        ("M", "go.mod"),
        ("M", "tests/bots/bots_test.go"),
        ("M", "maps/train/claw.json"),
        ("M", "league_tools/tournament.py"),
        ("M", "tests/test_bots.py"),
        ("M", "hosting/lambda/handler.py"),
        ("M", ".agents/skills/bot-league-iteration/SKILL.md"),
        ("A", "AGENTS.md"),
        ("A", "ledger/studies/notes.md"),
    ]
    assert scope.out_of_scope(refused) == [f"{status} {path}" for status, path in refused]


def test_a_study_adds_only_its_games_summaries_and_analyses_and_lists_them() -> None:
    allowed = [
        ("A", "ledger/studies/483.md"),
        ("A", "ledger/analyses/483.md"),
        ("M", "ledger/real-games.txt"),
    ]
    assert scope.out_of_scope(allowed, "study") == []
    refused = [
        ("M", "ledger/studies/471.md"),
        ("D", "ledger/analyses/471.md"),
        ("A", "ledger/analyses/notes.md"),
        ("A", "ledger/runs/20261124-abc123.md"),
        ("M", "ledger/iterations.md"),
        ("A", "bots/new_bot/main.go"),
        ("M", "hosting/lambda/bot"),
        ("D", "ledger/real-games.txt"),
    ]
    assert scope.out_of_scope(refused, "study") == [f"{status} {path}" for status, path in refused]


def test_a_study_only_appends_its_own_games_to_the_list() -> None:
    diff = (
        "--- a/ledger/real-games.txt\n+++ b/ledger/real-games.txt\n@@ -9,0 +10,2 @@\n+483 2026-11-24\n+484 2026-11-24\n"
    )
    assert scope.study_list_problems(diff, {"483", "484"}) == []
    assert scope.study_list_problems(diff, {"483"}) == ["lists game 484, whose study it doesn't add"]
    removed = "@@ -1 +0,0 @@\n-471 2026-11-23\n"
    assert scope.study_list_problems(removed, {"483"}) == ["removes a listed game"]
    assert scope.study_list_problems("@@ -9,0 +10 @@\n+483 soon\n", {"483"}) == ["adds a line that isn't `<id> <date>`"]


def test_the_scope_finds_players_names_without_printing_them(tmp_path: Path) -> None:
    demo = {
        "teams": [{"color": 1, "name": "Blue", "players": ["Alice Smith"]}, {"color": 2, "name": "Red", "players": []}],
        "logs": [{"players": [{"display_name": "ori_hold", "lines": []}, {"display_name": "zed99", "lines": []}]}],
    }
    (tmp_path / "7").mkdir()
    (tmp_path / "7" / "demo.json").write_text(json.dumps(demo))
    names = scope.player_names(tmp_path, ignore={"ori_hold"})
    assert names == {"Alice Smith", "zed99"}

    diff = "\n".join(
        [
            "+++ b/ledger/iterations.md",
            "@@ -10,0 +11,3 @@",
            "+The opponent sent 25 from Blue.",
            "+Then alice smith's bot waited.",
            "+zed990 is not a name here.",
        ]
    )
    added = scope.added_lines(diff)
    assert added[1] == ("ledger/iterations.md", 12, "Then alice smith's bot waited.")
    assert scope.leaked(added, names) == ["ledger/iterations.md:12"]


def test_a_name_the_repository_already_holds_as_a_word_is_not_checked() -> None:
    # "castle" is all over the base's bots and skills. The second is in no file, this one included:
    # it is put together here, so that HEAD holding this test doesn't hold the name.
    names = {"castle", "zq-" + "nobody-7731"}
    assert scope.already_public(names, "HEAD") == {"castle"}


def test_a_runs_times_show_its_jobs_its_rounds_by_their_slowest_runner_and_its_slow_steps() -> None:
    def job(
        name: str, start: str, end: str, steps: list[dict[str, Any]] | None = None, result: str = "success"
    ) -> dict[str, Any]:
        return {
            "name": name,
            "conclusion": result,
            "created_at": "2026-11-23T08:00:00Z",
            "started_at": f"2026-11-23T08:{start}Z",
            "completed_at": f"2026-11-23T08:{end}Z",
            "steps": steps or [],
        }

    jobs = [
        job("Claim", "00:00", "01:00"),
        job("Warm 1/2", "01:00", "04:00"),
        job(
            "Warm 2/2",
            "01:00",
            "08:00",
            [{"name": "Play the shard", "started_at": "2026-11-23T08:01:30Z", "completed_at": "2026-11-23T08:07:30Z"}],
        ),
        job("Gate ${{ matrix.shard }}/8", "08:00", "08:00", result="skipped"),
        job("Study (first half)", "08:00", "20:00"),
    ]
    text = run_times.report({"created_at": "2026-11-23T08:00:00Z"}, jobs)
    assert "| Claim | success | 0.0 | 1.0 |" in text
    assert "| Warm | 2 | 7.0 | 5.0 | 3.0 | 2 |" in text
    assert "- 6.0 min: Warm 2/2: Play the shard" in text
    assert "Gate" not in text
    assert "The run: 20.0 minutes, from 08:00 to 08:20 UTC." in text
