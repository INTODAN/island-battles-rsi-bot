"""The automated iteration: the notifier, the choice of real games to study and the scope check."""

import io
import json
import sys
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "hosting" / "rsi"))

import notifier  # noqa: E402
import real_games  # noqa: E402
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
        ("A", "bots/ori_fast/bot.py"),
        ("M", "bots/ori_hold/bot.toml"),
        ("D", "bots/old_bot/bot.py"),
        ("M", "ledger/iterations.md"),
        ("M", "ledger/real-games.txt"),
        ("M", "hosting/lambda/bot"),
        ("A", "maps/train/new_map.json"),
    ]
    assert scope.out_of_scope(allowed) == []
    refused = [
        ("M", ".github/workflows/checks.yml"),
        ("M", "bots/__init__.py"),
        ("M", "maps/train/claw.json"),
        ("M", "league_tools/tournament.py"),
        ("M", "tests/test_bots.py"),
        ("M", "hosting/lambda/handler.py"),
        ("M", ".agents/skills/bot-league-iteration/SKILL.md"),
        ("A", "AGENTS.md"),
    ]
    assert scope.out_of_scope(refused) == [f"{status} {path}" for status, path in refused]


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
