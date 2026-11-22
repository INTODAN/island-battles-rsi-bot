import gzip
import io
import json
import sys
import time
import zipfile
from copy import deepcopy
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from island_battles_client.fixture import fixture_turn_data

from league_tools import digest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "hosting" / "lambda"))

import games  # noqa: E402
import owner  # noqa: E402
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
    # Even after its last turn, a game waits for its end, until no turn came for long.
    assert not games.is_over(summary, START + timedelta(seconds=5))
    assert games.is_over(summary, START + timedelta(hours=1))
    done = games.finish(store, 7, START)
    assert done is not None and done["status"] == "finished"
    # Team 1 holds two castles to team 2's one on the last board.
    assert done["result"] == "won"

    data = store.get(games.zip_key(7))
    assert data is not None
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        assert sorted(archive.namelist()) == ["README.txt", "demo.json", "digest.txt", "game.json", "turns.jsonl"]
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
    listed = games.finish_over_games(store, START + timedelta(hours=1))
    overview = games.overview(listed, START + timedelta(minutes=5))
    assert overview["record"] == {"won": 1, "lost": 0, "draw": 0}
    html = page.render("finish_speed", overview, listed)
    assert "Game 7" in html and "/games/7.zip" in html and "1–0–0" in html
    assert "<script>alert" not in page.render("<script>alert(1)</script>", overview, listed)


def _end(color: int = 1, winner: int | None = 2, expires: datetime | None = None) -> dict[str, Any]:
    final = deepcopy(fixture_turn_data()["generation"])
    final["id"] = 200
    return {
        "game_id": 7,
        "team_color": color,
        "turn_number": 6,
        "outcome": {
            "reason": "last_team_standing",
            "winner_team_color": winner,
            "summary": "Red won",
            "departures": [],
        },
        "generation": final,
        "memory": {"seen": 5},
        "demo": {
            "url": "https://island-battles.elidan.org/game/7/demo?token=ibdt1.x.y",
            "expires_at": (expires or START + timedelta(days=7)).isoformat(),
        },
    }


def _real_demo() -> bytes:
    frames = [_turn(number)["generation"] for number in range(1, 6)]
    demo = {
        "format": "island-battles-demo",
        "schema_version": 2,
        "game_id": 7,
        "saved_at": START.isoformat(),
        "teams": [
            {"color": 1, "name": "Blue", "players": ["finish_speed"]},
            {"color": 2, "name": "Red", "players": ["Kraken"]},
        ],
        "frames": frames,
        "logs": [{"generation_id": frame["id"], "hidden_team_colors": [], "players": []} for frame in frames],
        "outcome": {"reason": "last_team_standing", "winner_team_color": 2, "summary": "Red won", "departures": []},
    }
    return json.dumps(demo).encode()


def test_a_delivered_end_packs_the_games_own_demo_with_the_real_result(tmp_path: Path) -> None:
    store = games.MemoryStore()
    for number in range(1, 6):
        _play(store, number, START)
    games.record_end(store, _end())
    links: list[str] = []

    def download(url: str) -> bytes:
        links.append(url)
        return gzip.compress(_real_demo())

    summary = games.complete(store, 7, download, MAPS, "finish_speed", START)
    assert summary is not None
    assert links == [_end()["demo"]["url"]]
    assert summary["result"] == "lost" and summary["estimated"] is False and summary["demo"] == "full"
    assert summary["result_note"] == "Red won" and summary["opponents"] == ["Red (Kraken)"]
    assert summary["turns"] == 5 and summary["final_turn"] == 6

    data = store.get(games.zip_key(7))
    assert data is not None
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        names = set(archive.namelist())
        assert names == {"demo.json", "digest.txt", "turns.jsonl", "game.json", "game-ended.json", "README.txt"}
        assert json.loads(archive.read("demo.json"))["outcome"]["summary"] == "Red won"
        assert "Red won" in archive.read("digest.txt").decode()
        # The link's token stays out of the zip.
        assert "ibdt1" not in archive.read("game-ended.json").decode()
    path = tmp_path / "game-7.zip"
    path.write_bytes(data)
    assert digest.load_demo(path)["teams"][1]["players"] == ["Kraken"]
    # A finished game is not estimated over later.
    assert games.finish_over_games(store, START + timedelta(days=1))[0]["estimated"] is False


def test_a_demo_that_fails_to_download_is_tried_again_while_its_link_lasts() -> None:
    store = games.MemoryStore()
    for number in range(1, 4):
        _play(store, number, START)
    games.record_end(store, _end(winner=None))

    def broken(url: str) -> bytes:
        raise OSError("connection reset")

    summary = games.complete(store, 7, broken, MAPS, "finish_speed", START)
    assert summary is not None
    assert summary["demo"] == "pending" and summary["result"] == "draw" and summary["estimated"] is False
    assert "connection reset" in summary["demo_error"]
    assert store.get(games.zip_key(7)) is not None
    retried = games.finish_over_games(store, START + timedelta(minutes=5), lambda url: _real_demo(), MAPS)
    assert retried[0]["demo"] == "full"


def test_the_handler_takes_a_game_end_at_its_sibling_path(monkeypatch: pytest.MonkeyPatch) -> None:
    import handler  # noqa: PLC0415 - loads the bot

    store = games.MemoryStore()
    monkeypatch.setattr(handler, "_store", store)
    monkeypatch.setattr(handler, "download_demo", lambda url: _real_demo())
    event = {"requestContext": {"http": {"method": "POST"}}, "rawPath": "/game-ended", "body": json.dumps(_end())}
    answer = handler.handler(event, None)
    assert answer["statusCode"] == 202 and json.loads(answer["body"])["kept"] is True
    assert json.loads(store.get(games.game_key(7)) or b"{}")["demo"] == "full"
    bad = handler.handler({**event, "body": "{}"}, None)
    assert bad["statusCode"] == 422


def test_a_demo_link_off_the_games_host_is_refused() -> None:
    import handler  # noqa: PLC0415 - loads the bot

    with pytest.raises(ValueError, match="demo link"):
        handler.download_demo("https://example.com/game/7/demo?token=x")


def test_the_estimate_never_replaces_a_delivered_end() -> None:
    store = games.MemoryStore()
    for number in range(1, 4):
        _play(store, number, START)
    games.record_end(store, _end())
    full = games.complete(store, 7, lambda url: _real_demo(), MAPS, "finish_speed", START)
    assert full is not None and full["demo"] == "full"
    assert games.finish(store, 7, START + timedelta(hours=1)) is None
    assert games.finish_over_games(store, START + timedelta(hours=1))[0]["result"] == "lost"


def test_a_turn_kept_after_the_end_packs_the_game_again(monkeypatch: pytest.MonkeyPatch) -> None:
    import handler  # noqa: PLC0415 - loads the bot
    from island_battles_client._generated import TurnDelivery  # noqa: PLC0415

    store = games.MemoryStore()
    monkeypatch.setattr(handler, "download_demo", lambda url: _real_demo())
    monkeypatch.setattr(handler.BotServer, "_post", lambda self, delivery, result: (200, "", None))
    for number in range(1, 3):
        _play(store, number, START)
    games.record_end(store, _end())
    games.complete(store, 7, handler.download_demo, MAPS, "finish_speed", START)
    # The last turn's record lands after the end was handled.
    late = {
        "turn": _turn(3),
        "submit": {"url": "https://island-battles.elidan.org/generation/commands", "token": "t", "deadline_at": None},
    }
    handler._bot.take(TurnDelivery.model_validate(late), store)
    summary = json.loads(store.get(games.game_key(7)) or b"{}")
    assert summary["status"] == "finished" and summary["demo"] == "full" and summary["turns"] == 3


def test_the_games_are_listed_without_reading_their_turns() -> None:
    store = games.MemoryStore()
    _play(store, 1, START)
    listed: list[str] = []
    keys = store.keys
    store.keys = lambda prefix: listed.append(prefix) or keys(prefix)  # type: ignore[method-assign]
    assert [game["game_id"] for game in games.all_games(store)] == [7]
    assert listed == []


OWNER = owner.Owner.from_settings("client.apps.googleusercontent.com", "Owner@example.com", "s" * 32)
NOW = 1_800_000_000.0


def _claims(**changes: str) -> dict[str, Any]:
    claims = {
        "aud": OWNER.client_id,
        "iss": "https://accounts.google.com",
        "exp": str(int(NOW) + 600),
        "email": "owner@example.com",
        "email_verified": "true",
    }
    return {**claims, **changes}


def test_only_the_owners_google_account_signs_in() -> None:
    session = OWNER.sign_in("token", lambda credential: _claims(), NOW)
    assert OWNER.signed_in(session, NOW) and not OWNER.signed_in(session, NOW + owner.SESSION_SECONDS + 1)
    refused = [
        _claims(email="someone@example.com"),
        _claims(aud="another.apps.googleusercontent.com"),
        _claims(iss="https://evil.example.com"),
        _claims(exp=str(int(NOW) - 1)),
        _claims(email_verified="false"),
    ]
    for claims in refused:
        with pytest.raises(owner.Refused):
            OWNER.sign_in("token", lambda credential, claims=claims: claims, NOW)
    expires = session.split(".")[0]
    assert not OWNER.signed_in(f"{int(expires) + 100}.{session.split('.')[1]}", NOW)
    assert not owner.Owner.from_settings(OWNER.client_id, "owner@example.com", "t" * 32).signed_in(session, NOW)
    closed = owner.Owner.from_settings("", "owner@example.com", "s" * 32)
    with pytest.raises(owner.Refused):
        closed.sign_in("token", lambda credential: _claims(), NOW)


def test_the_home_page_the_games_and_their_zips_are_the_owners(monkeypatch: pytest.MonkeyPatch) -> None:
    import handler  # noqa: PLC0415 - loads the bot

    store = games.MemoryStore()
    for number in range(1, 6):
        _play(store, number, START, max_generations=5)
    monkeypatch.setattr(handler, "_store", store)
    monkeypatch.setattr(handler, "OWNER", OWNER)
    monkeypatch.setattr(handler, "GAMES_KEY", "")
    monkeypatch.setattr(handler, "tokeninfo", lambda credential: _claims(exp=str(int(time.time()) + 600)))

    def get(path: str, **extra: object) -> dict[str, Any]:
        return handler.handler({"requestContext": {"http": {"method": "GET"}}, "rawPath": path, **extra}, None)

    closed = get("/")
    assert closed["statusCode"] == 401 and "accounts.google.com/gsi/client" in closed["body"]
    assert "Game 7" not in closed["body"]
    for hidden in (handler._bot.name, "github.com", "champion", "league"):
        assert hidden not in closed["body"]
    assert get("/api/games")["statusCode"] == 401
    assert get("/games/7.zip")["statusCode"] == 403
    assert get("/health")["statusCode"] == 200

    sign_in = {"requestContext": {"http": {"method": "POST"}}, "rawPath": "/sign-in"}
    answer = handler.handler({**sign_in, "body": json.dumps({"credential": "token"})}, None)
    assert answer["statusCode"] == 200
    cookie = answer["cookies"][0].split(";")[0]
    assert "HttpOnly" in answer["cookies"][0] and "Secure" in answer["cookies"][0]
    home = get("/", cookies=[cookie])
    assert home["statusCode"] == 200 and "Game 7" in home["body"] and "Sign out" in home["body"]
    assert get("/", headers={"cookie": f"other=1; {cookie}"})["statusCode"] == 200
    assert get("/api/games", cookies=[cookie])["statusCode"] == 200
    assert get("/games/7.zip", cookies=[cookie])["statusCode"] == 302

    monkeypatch.setattr(handler, "tokeninfo", lambda credential: _claims(email="someone@example.com"))
    refused = handler.handler({**sign_in, "body": json.dumps({"credential": "token"})}, None)
    assert refused["statusCode"] == 403 and "cookies" not in refused
    monkeypatch.setattr(handler, "GAMES_KEY", "the-key")
    assert get("/games/7.zip", queryStringParameters={"key": "the-key"})["statusCode"] == 302
    assert get("/games/7.zip", queryStringParameters={"key": "wrong"})["statusCode"] == 403
