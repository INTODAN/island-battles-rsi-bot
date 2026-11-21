import io
import json
import sys
import zipfile
from copy import deepcopy
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from island_battles_client.fixture import fixture_turn_data

from league_tools import digest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "hosting" / "lambda"))

import games  # noqa: E402
import page  # noqa: E402

START = datetime(2026, 11, 21, 20, 0, tzinfo=UTC)
MAPS = games.KnownMaps.load(ROOT / "maps")


def _turn(number: int, max_generations: int = 300, deadline: datetime | None = None) -> dict[str, Any]:
    turn = deepcopy(fixture_turn_data())
    turn.update(game_id=7, turn_number=number, max_generations=max_generations)
    turn["generation"]["id"] = 100 + number
    turn["turn_deadline_at"] = deadline.isoformat() if deadline else None
    return turn


def _play(
    store: games.Store, number: int, now: datetime, max_generations: int = 300, deadline: datetime | None = None
) -> dict[str, Any]:
    result = {"commands": [], "logs": [{"level": "info", "logger": "island_battles.player", "message": f"t{number}"}]}
    return games.record_turn(
        store,
        bot="finish_speed",
        turn=_turn(number, max_generations, deadline),
        result=result,
        submitted=200,
        play_ms=3.0,
        maps=MAPS,
        now=now,
    )


def test_a_game_that_reaches_its_last_turn_is_packed_into_a_zip_the_digest_reads(tmp_path: Path) -> None:
    store = games.MemoryStore()
    for number in range(1, 5):
        summary = _play(store, number, START + timedelta(seconds=number), max_generations=5)
    assert summary["turns"] == 4 and summary["accepted"] == 4
    assert games.is_over(summary, START)
    done = games.finish(store, 7, START)
    assert done is not None and done["status"] == "finished"
    # Team 1 holds two castles to team 2's one on the last board.
    assert done["result"] == "won"

    data = store.get(games.zip_key(7))
    assert data is not None
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        assert sorted(archive.namelist()) == ["demo.json", "game.json", "turns.jsonl"]
        assert len(archive.read("turns.jsonl").decode().splitlines()) == 4
    path = tmp_path / "game-7.zip"
    path.write_bytes(data)
    demo = digest.load_demo(path)
    assert demo["format"] == "island-battles-demo" and demo["schema_version"] == 2
    assert [frame["id"] for frame in demo["frames"]] == [101, 102, 103, 104]
    assert demo["logs"][0]["players"][0]["lines"][0]["message"] == "t1"
    assert "finish_speed" in digest.digest(demo)


def test_a_game_with_no_turn_long_after_its_deadline_is_over() -> None:
    store = games.MemoryStore()
    _play(store, 1, START, deadline=START + timedelta(seconds=30))
    assert games.finish_over_games(store, START + timedelta(seconds=60))[0]["status"] == "playing"
    later = games.finish_over_games(store, START + timedelta(seconds=120))
    assert later[0]["status"] == "finished"
    assert store.get(games.zip_key(7)) is not None
    # A turn that still comes reopens the game.
    assert _play(store, 2, START + timedelta(seconds=130))["status"] == "playing"


def test_a_known_map_is_named_and_another_is_described() -> None:
    claw = json.loads((ROOT / "maps" / "train" / "claw.json").read_text())
    generation = {"castles": claw["castles"], "soldier_groups": []}
    assert MAPS.name(generation) == "claw"
    assert MAPS.name(_turn(1)["generation"]) == "4 castles, 2 teams"


def test_the_home_page_lists_the_games() -> None:
    store = games.MemoryStore()
    for number in range(1, 5):
        _play(store, number, START, max_generations=5)
    listed = games.finish_over_games(store, START)
    overview = games.overview(listed, START + timedelta(minutes=5))
    assert overview["record"] == {"won": 1, "lost": 0, "draw": 0}
    html = page.render("finish_speed", overview, listed, key_required=True)
    assert "Game 7" in html and "/games/7.zip" in html and "1–0–0" in html
    assert "<script>alert" not in page.render("<script>alert(1)</script>", overview, listed, key_required=False)
