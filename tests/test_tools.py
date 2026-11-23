"""The league's tools: ratings, the tournament's summary, the digest and the roster."""

import contextlib
import gzip
import json
import re
from collections.abc import Generator
from pathlib import Path
from types import SimpleNamespace

import pytest
from island_battles_client import (
    NEUTRAL_TEAM_COLOR,
    BotTurn,
    BotTurnResult,
    UpgradeType,
    send_soldier_group,
    turn_result,
    upgrade_castle,
)

from league_tools import cli, clock, digest, engine, maps, ratings, rematch, replay, roster, tournament


def test_ratings_put_the_winner_above_and_level3_at_1000() -> None:
    games = [("strong", "level3", 1.0)] * 6 + [("level3", "weak", 1.0)] * 6 + [("strong", "weak", 0.5)] * 2
    fitted = ratings.fit(games)
    assert fitted["level3"] == pytest.approx(1000)
    assert fitted["strong"] > fitted["level3"] > fitted["weak"]


def test_ratings_fix_ori_mimic_at_1800_before_level3() -> None:
    """level3 winning nothing doesn't move the scale: the sparring bot that wins and loses holds it."""
    games = [("strong", "ori_mimic", 1.0)] * 3 + [("ori_mimic", "strong", 1.0)] * 2 + [("ori_mimic", "level3", 1.0)] * 6
    games += [("strong", "level3", 1.0)] * 6
    fitted = ratings.fit(games)
    assert fitted["ori_mimic"] == pytest.approx(1800)
    assert fitted["strong"] > fitted["ori_mimic"] > fitted["level3"]
    # Without either anchor, the mean is 1000.
    unanchored = ratings.fit([("a", "b", 1.0), ("a", "b", 0.5)])
    assert sum(unanchored.values()) / 2 == pytest.approx(1000) and unanchored["a"] > unanchored["b"]


def test_ratings_do_not_depend_on_the_order_of_the_games() -> None:
    games = [("a", "b", 1.0), ("b", "c", 1.0), ("c", "a", 0.5), ("a", "b", 0.0)]
    assert ratings.fit(games) == pytest.approx(ratings.fit(games[::-1]))


def result(first: str, second: str, winner: str | None, map_name: str = "strait") -> dict:
    seat = {"failed_turns": 0, "slowest_turn_milliseconds": 1.0, "failures": []}
    return {
        "id": f"{first}-{second}-{map_name}",
        "map": map_name,
        "players": [first, second],
        "winner": winner,
        "generations": 40,
        "outcome": {"summary": "someone wins"},
        "seats": [{"name": first, **seat}, {"name": second, **seat}],
        "demo": "demo.json.gz",
    }


def test_summary_counts_points_from_both_seats() -> None:
    results = [result("a", "b", "a"), result("b", "a", "a"), result("a", "level3", None)]
    results.append({"id": "x", "map": "strait", "players": ["a", "b"], "error": "no map"})
    summary = tournament.summarize(results)
    rows = {row["player"]: row for row in summary["standings"]}
    assert (rows["a"]["wins"], rows["a"]["draws"], rows["a"]["losses"]) == (2, 1, 0)
    assert summary["pairs"]["b"]["a"] == [0, 2]
    assert summary["maps"]["a"]["strait"] == [2.5, 3]
    assert summary["errors"] == [{"map": "strait", "players": ["a", "b"], "error": "no map"}]
    table = tournament.markdown(summary, results, ["b"], list_games=True)
    assert "Games b didn't win" in table and "Longest wins of b" in table and "NOT PLAYED" in table
    # A holdout map's games are never listed: nobody reads them.
    hidden = tournament.markdown(summary, results, ["b"], list_games=False)
    assert "demo.json.gz" not in hidden and "Holdout maps were played" in hidden
    holdout, train = Path("maps/holdout/ridge.json"), Path("maps/train/strait.json")
    assert tournament.has_holdout([train, holdout]) and not tournament.has_holdout([train])


def test_ratings_settle_for_a_player_that_wins_everything() -> None:
    games = [("best", "level3", 1.0)] * 40 + [("level3", "worst", 1.0)] * 40 + [("best", "worst", 1.0)] * 40
    fitted = ratings.fit(games)
    # Fitted to the end, the result no longer moves when the fit is run from its own answer's games again.
    assert fitted == pytest.approx(ratings.fit(games[::-1]), abs=1e-6)
    assert fitted["best"] - fitted["level3"] == pytest.approx(fitted["level3"] - fitted["worst"], abs=1e-4)


def test_a_match_is_cached_under_its_players_names(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Two bots with the same code have results of their own, and a failed turn is played again."""
    bots, cache = tmp_path / "bots", tmp_path / "cache"
    for name in ("first", "copy"):
        (bots / name).mkdir(parents=True)
        (bots / name / "bot.py").write_text("def play(turn): ...\n")
    map_file = tmp_path / "duel.json"
    map_file.write_text("{}")
    monkeypatch.setattr(tournament, "BOTS", bots)
    monkeypatch.setattr(tournament, "CACHE", cache)
    monkeypatch.setattr(tournament, "player_specification", lambda name: {})
    monkeypatch.setattr(tournament.engine, "build", lambda: tournament.engine.Build("build", tmp_path / "runner"))
    played: list[list[str]] = []
    failing = {"copy"}

    def play(binary: Path, schedule: dict, worker_log: Path) -> list[dict]:
        lines = []
        for match in schedule["matches"]:
            played.append(match["seats"])
            (cache / f"{match['id']}.json.gz").write_bytes(b"demo")
            failed = [int(name in failing) for name in match["seats"]]
            seats = [
                {"name": name, "failed_turns": count, "failures": []}
                for name, count in zip(match["seats"], failed, strict=True)
            ]
            lines.append(
                {"id": match["id"], "map": match["map"], "players": match["seats"], "winner": None, "seats": seats}
            )
        return lines

    monkeypatch.setattr(tournament.engine, "play", play)
    plan = tournament.Tournament(players=["first", "copy", "level3"], maps=[map_file])
    results = tournament.play(plan, tmp_path / "run")
    assert sorted(result["players"] for result in results) == sorted(played) and len(played) == 6
    # Every match with "copy" had a failed turn, so only the two without it were kept.
    failing.clear()
    played.clear()
    again = tournament.play(plan, tmp_path / "run")
    assert len(played) == 4 and all("copy" in seats for seats in played)
    assert sorted(result["players"] for result in again) == sorted(result["players"] for result in results)
    played.clear()
    tournament.play(plan, tmp_path / "run")
    assert played == []
    # A match played again with a failed turn loses its earlier result: its demo was replaced.
    failing.add("first")
    tournament.play(
        tournament.Tournament(players=["first", "level3"], maps=[map_file], use_cache=False), tmp_path / "run"
    )
    failing.clear()
    played.clear()
    tournament.play(plan, tmp_path / "run")
    assert len(played) == 2 and all(set(seats) == {"first", "level3"} for seats in played)
    played.clear()
    # A cached result whose demo is gone is played again.
    next(cache.glob("*.json.gz")).unlink()
    tournament.play(plan, tmp_path / "run")
    assert len(played) == 1
    assert tournament.match_key("b", "m", ["first", "copy"], ["x", "x"], [300, 2000]) != tournament.match_key(
        "b", "m", ["copy", "first"], ["x", "x"], [300, 2000]
    )


def _fake_league(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, names: list[str]) -> tuple[Path, list[list[str]]]:
    """Bots with code, a map and a runner that records what it plays: the first seat always wins."""
    bots, cache = tmp_path / "bots", tmp_path / "cache"
    for name in names:
        (bots / name).mkdir(parents=True)
        (bots / name / "bot.py").write_text(f"def play(turn): ...  # {name}\n")
    map_file = tmp_path / "duel.json"
    map_file.write_text("{}")
    monkeypatch.setattr(tournament, "BOTS", bots)
    monkeypatch.setattr(tournament, "CACHE", cache)
    monkeypatch.setattr(tournament, "player_specification", lambda name: {})
    monkeypatch.setattr(tournament.engine, "build", lambda: tournament.engine.Build("build", tmp_path / "runner"))
    played: list[list[str]] = []

    def play(binary: Path, schedule: dict, worker_log: Path) -> list[dict]:
        lines = []
        for match in schedule["matches"]:
            played.append(match["seats"])
            (cache / f"{match['id']}.json.gz").write_bytes(b"demo")
            seats = [
                {"name": name, "failed_turns": 0, "failures": [], "slowest_turn_milliseconds": 1.0}
                for name in match["seats"]
            ]
            lines.append(
                {
                    "id": match["id"],
                    "map": match["map"],
                    "players": match["seats"],
                    "winner": match["seats"][0],
                    "generations": 10,
                    "outcome": {"summary": "won"},
                    "seats": seats,
                    "demo": str(cache / f"{match['id']}.json.gz"),
                }
            )
        return lines

    monkeypatch.setattr(tournament.engine, "play", play)
    return map_file, played


def test_parents_plays_each_focused_bot_against_its_parent_alone(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    map_file, played = _fake_league(tmp_path, monkeypatch, ["parent", "child", "other", "third"])
    monkeypatch.setattr(tournament, "RUNS", tmp_path / "runs")
    plan = tournament.Tournament(
        players=["parent", "other", "child", "level3"],
        maps=[map_file],
        focus=["child"],
        listed=["child"],
        parents={"child": "parent"},
        parents_only=True,
    )
    summary, table = tournament.run(plan, "h2h")
    assert sorted(played) == [["child", "parent"], ["parent", "child"]]
    assert "| `child` | `parent` | 1/2 | no |" in table
    # The whole round robin then plays only what the head-to-head run didn't, and says where the rules stand.
    played.clear()
    whole = tournament.Tournament(
        players=["parent", "other", "child", "level3"],
        maps=[map_file],
        listed=["child"],
        parents={"child": "parent"},
    )
    summary, table = tournament.run(whole, "whole")
    assert len(played) == 10 and ["child", "parent"] not in played
    assert "Rating (parent's)" in table and "Rated above the parent" not in table  # the map is in no set


def test_a_tournament_that_waited_takes_what_the_other_played(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    map_file, played = _fake_league(tmp_path, monkeypatch, ["first", "second"])
    plan = tournament.Tournament(players=["first", "second"], maps=[map_file])
    real_exclusive = tournament.engine.exclusive

    @contextlib.contextmanager
    def exclusive(lock_file: Path, waiting: str = "") -> Generator[None]:
        # Another checkout's tournament plays the same matches while this one waits for the lock.
        other = tournament.Tournament(players=["first", "second"], maps=[map_file])
        monkeypatch.setattr(tournament.engine, "exclusive", real_exclusive)
        tournament.play(other, tmp_path / "other")
        with real_exclusive(lock_file, waiting):
            yield

    monkeypatch.setattr(tournament.engine, "exclusive", exclusive)
    results = tournament.play(plan, tmp_path / "run")
    assert len(played) == 2 and len(results) == 2


def test_the_cache_and_the_runner_are_shared_by_every_checkout(monkeypatch: pytest.MonkeyPatch) -> None:
    """A git worktree uses its main checkout's cache and runner, so its first tournament isn't played cold."""
    from league_tools import paths

    assert (paths.SHARED / "runner.toml").is_file()
    assert paths.CACHE == paths.SHARED / "runs" / "cache" and paths.RUNNER_SOURCE.parent == paths.RUNNER
    monkeypatch.setenv(paths.SHARED_VARIABLE, "/somewhere/else")
    assert paths._shared_root() == Path("/somewhere/else")


def castle(castle_id: int, team_color: int, soldiers: int, x: float, levels: dict | None = None) -> dict:
    upgrades = {"speed": 1, "generation_amount": 1, "burst_potential": 1, "clash_stop_generations": 1}
    return {
        "id": castle_id,
        "team_color": team_color,
        "soldiers": soldiers,
        "x": x,
        "y": 0,
        "upgrades": upgrades | (levels or {}),
        "burst_debt": 0,
    }


def test_shards_split_a_tournament_into_parts_that_make_the_whole(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """N runners that each play one shard play every match once, and together leave the whole in the cache."""
    bots, cache = tmp_path / "bots", tmp_path / "cache"
    for name in ("first", "second", "third"):
        (bots / name).mkdir(parents=True)
        (bots / name / "bot.py").write_text(f"def play(turn): ...  # {name}\n")
    maps = []
    for name in ("duel", "ring"):
        maps.append(tmp_path / f"{name}.json")
        maps[-1].write_text(json.dumps({"name": name}))
    monkeypatch.setattr(tournament, "BOTS", bots)
    monkeypatch.setattr(tournament, "CACHE", cache)
    monkeypatch.setattr(tournament, "player_specification", lambda name: {})
    monkeypatch.setattr(tournament.engine, "build", lambda: tournament.engine.Build("build", tmp_path / "runner"))
    played: list[str] = []

    def play(binary: Path, schedule: dict, worker_log: Path) -> list[dict]:
        lines = []
        for match in schedule["matches"]:
            played.append(match["id"])
            (cache / f"{match['id']}.json.gz").write_bytes(b"demo")
            seats = [{"name": name, "failed_turns": 0, "failures": []} for name in match["seats"]]
            lines.append(
                {"id": match["id"], "map": match["map"], "players": match["seats"], "winner": None, "seats": seats}
            )
        return lines

    monkeypatch.setattr(tournament.engine, "play", play)
    players = ["first", "second", "third", "level3"]
    shards = []
    for index in (1, 2, 3):
        plan = tournament.Tournament(players=players, maps=maps, shard=(index, 3))
        shards.append({result["id"] for result in tournament.play(plan, tmp_path / "run")})
    # Six pairs, two sides, two maps: each match in exactly one shard, and each shard has some.
    assert len(played) == len(set(played)) == 24 == sum(len(shard) for shard in shards)
    assert all(shards) and set(played) == set().union(*shards)
    played.clear()
    whole = tournament.play(tournament.Tournament(players=players, maps=maps), tmp_path / "run")
    assert played == [] and {result["id"] for result in whole} == set().union(*shards)
    # The shard of a match doesn't depend on what the cache holds.
    again = tournament.play(tournament.Tournament(players=players, maps=maps, shard=(2, 3)), tmp_path / "run")
    assert played == [] and {result["id"] for result in again} == shards[1]
    assert tournament.parse_shard("2/8") == (2, 8)
    for text in ("0/3", "4/3", "2", "a/b", "1/0"):
        with pytest.raises(ValueError):
            tournament.parse_shard(text)


def test_a_shard_reports_no_ratings_and_strict_counts_its_failures(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A shard's summary rates nobody, and --strict fails on its failed turns but not on an empty shard."""

    def seat(name: str, failed: int) -> dict:
        return {"name": name, "failed_turns": failed, "failures": [], "slowest_turn_milliseconds": 9.0}

    results = [
        {"id": "a", "map": "duel", "players": ["x", "y"], "winner": "x", "seats": [seat("x", 0), seat("y", 2)]},
        {"id": "b", "map": "duel", "players": ["y", "x"], "winner": None, "seats": [seat("y", 0), seat("x", 0)]},
        {"id": "c", "map": "ring", "players": ["x", "y"], "error": "the worker died"},
    ]
    monkeypatch.setattr(tournament, "RUNS", tmp_path)
    monkeypatch.setattr(tournament, "play", lambda plan, directory: results)
    plan = tournament.Tournament(players=["x", "y"], maps=[], shard=(2, 4))
    summary, table = tournament.run(plan, "shard")
    assert summary == {
        "shard": "2/4",
        "matches": 3,
        "failed_games": 1,
        "failed_players": ["y"],
        "errors": [{"map": "ring", "players": ["x", "y"], "error": "the worker died"}],
    }
    assert "rating" not in json.loads((tmp_path / "shard" / "summary.json").read_text())
    assert table.startswith("Shard 2/4: 3 matches, 1 with a failed turn, 1 not played.") and "NOT PLAYED ring" in table
    whole, _ = tournament.run(tournament.Tournament(players=["x", "y"], maps=[]), "whole")
    assert whole["failed_players"] == ["y"] and whole["standings"]

    outcomes: list[dict] = []
    monkeypatch.setattr(cli.tournament, "run", lambda plan, run_id: (outcomes.pop(0), ""))
    arguments = ["tournament", "--bots", "x,y", "--anchors", "", "--no-opponents", "--maps", "train", "--strict"]
    empty = {"matches": 0, "errors": [], "failed_players": []}
    outcomes += [dict(empty), dict(empty), dict(empty, matches=5, failed_players=["y"])]
    assert cli.main([*arguments, "--shard", "1/8"]) == 0
    assert cli.main(arguments) == 1
    assert cli.main([*arguments, "--shard", "1/8"]) == 1


def test_digest_reads_the_events_between_boards() -> None:
    group = {
        "id": 0,
        "team_color": 1,
        "soldiers": 20,
        "x": 0.5,
        "y": 0,
        "origin_castle_id": 0,
        "destination_castle_id": 1,
        "clash_radius": 0.25,
        "upgrades": {"speed": 2},
    }
    frames = [
        {"id": 1, "castles": [castle(0, 1, 30, -1), castle(1, 2, 5, 1)], "soldier_groups": [], "clashes": []},
        {
            "id": 2,
            "castles": [castle(0, 1, 1, -1, {"speed": 2}), castle(1, 2, 6, 1)],
            "soldier_groups": [group],
            "clashes": [],
        },
        {
            "id": 3,
            "castles": [castle(0, 1, 2, -1, {"speed": 2}), castle(1, 1, 13, 1)],
            "soldier_groups": [],
            "clashes": [],
        },
    ]
    line = {"level": "info", "logger": "island_battles.player", "message": "all in"}
    demo = {
        "teams": [{"color": 1, "name": "blue", "players": ["blue"]}, {"color": 2, "name": "red", "players": ["red"]}],
        "outcome": {"summary": "blue wins as the last team standing"},
        "frames": frames,
        "logs": [
            {"generation_id": 1, "players": [{"display_name": "blue", "team_color": 1, "lines": [line]}]},
            {"generation_id": 2, "players": []},
            {"generation_id": 3, "players": []},
        ],
    }
    events = digest.events(demo)
    assert (1, "upgrade: blue castle 0 speed 1->2") in events
    assert any(turn == 1 and event.startswith("send: blue 20 soldiers from castle 0") for turn, event in events)
    assert (2, "capture: castle 1 red (6 soldiers) -> blue (13 soldiers)") in events
    assert (2, "eliminated: red") in events
    assert digest.logistics(demo)[0] == (
        "  blue: sent 20 soldiers, 2.0 away on average, 0 to its own castles and 20 at others; "
        "30% of its soldiers were walking; lost 0 in clashes"
    )
    assert "send:" not in digest.digest(demo, key_only=True) and "capture:" in digest.digest(demo, key_only=True)
    text = digest.digest(demo, turns=(1, 1))
    assert "log blue [info]: all in" in text and "| 3 | 2 / 15 / 0 / 2 | 0 / 0 / 0 / 0 | 0 |" in text


def test_new_bot_copies_its_parent_as_a_candidate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(roster, "BOTS", tmp_path)
    (tmp_path / "founder").mkdir()
    (tmp_path / "founder" / "bot.py").write_text("def play(turn): ...\n")
    founder = roster.Bot(name="founder", status="active", parent="", iteration=0, idea="the first")
    monkeypatch.setattr(roster.Bot, "directory", property(lambda bot: tmp_path / bot.name))
    roster.write_bot(founder)
    child = roster.new_bot("founder_fast", "founder", 3, 'a "quoted" idea')
    assert roster.load_bot("founder_fast") == child
    assert (child.status, child.parent, child.iteration) == ("candidate", "founder", 3)
    assert roster.fingerprint(tmp_path / "founder") == roster.fingerprint(tmp_path / "founder_fast")
    with pytest.raises(ValueError):
        roster.new_bot("level4", "founder", 3, "a default bot's name")
    with pytest.raises(ValueError):
        roster.new_bot("founder_fast", "founder", 3, "taken")
    assert json.loads(json.dumps(child.__dict__))["name"] == "founder_fast"
    # Whatever an idea says, its bot.toml reads back.
    odd = roster.new_bot("founder_odd", "founder", 4, 'faster \U0001f680 "rush"\\ \x7f\ttab')
    assert roster.load_bot("founder_odd") == odd
    with pytest.raises(ValueError):
        roster.load_bot("../founder")


def test_digest_shows_a_group_destroyed_the_turn_it_left() -> None:
    walker = {
        "id": 3,
        "team_color": 1,
        "soldiers": 4,
        "x": 0,
        "y": 0,
        "origin_castle_id": 0,
        "destination_castle_id": 1,
        "clash_radius": 0.25,
        "upgrades": {"speed": 1},
    }
    clash = {
        "id": 1,
        "time": 0.5,
        "participants": [
            {"group_id": 3, "team_color": 1, "soldiers_before": 10, "soldiers_after": 4},
            {"group_id": 7, "team_color": 2, "soldiers_before": 6, "soldiers_after": 0},
        ],
    }
    frames = [
        {
            "id": 1,
            "castles": [castle(0, 1, 5, -1), castle(1, 2, 9, 1)],
            "soldier_groups": [walker | {"soldiers": 10}],
            "clashes": [],
        },
        {"id": 2, "castles": [castle(0, 1, 6, -1), castle(1, 2, 4, 1)], "soldier_groups": [walker], "clashes": [clash]},
    ]
    demo = {
        "teams": [{"color": 1, "name": "blue"}, {"color": 2, "name": "red"}],
        "outcome": None,
        "frames": frames,
        "logs": [{"players": []}] * 2,
    }
    assert digest.events(demo) == [
        (1, "send: red 6 soldiers as group 7, which a clash destroyed in the same turn"),
        (1, "clash: blue group 3 10->4, red group 7 6->0"),
    ]


@pytest.mark.parametrize("seed", range(20))
def test_generated_map_is_the_same_from_both_sides(seed: int) -> None:
    generated = maps.generate("made", seed)
    assert generated == maps.generate("made", seed)
    spots = {(castle["x"], castle["y"]): castle for castle in generated["castles"]}
    assert len(spots) == len(generated["castles"])
    for (x, y), castle in spots.items():
        twin = spots[(-x, -y)]
        assert abs(x) <= generated["plane_size_x"] / 2 and abs(y) <= generated["plane_size_y"] / 2
        assert twin["starting_soldier_amount"] == castle["starting_soldier_amount"]
        assert {castle["team_color"], twin["team_color"]} in ({0}, {1, 2})


def test_the_runner_is_pinned_to_one_commit_of_the_game() -> None:
    repository, commit = engine.pin()
    assert repository == "https://github.com/INTODAN/island-battles-go"
    assert re.fullmatch(r"[0-9a-f]{40}", commit), "a branch or a short hash would let the rules move under the ratings"


def test_a_local_checkout_of_the_game_replaces_the_pinned_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv(engine.LOCAL_SOURCE_VARIABLE, str(tmp_path))
    assert engine.source() == tmp_path.resolve()


def test_outside_opponents_come_from_the_local_file(tmp_path: Path) -> None:
    from league_tools import opponents

    project = tmp_path / "their_bot"
    (project / ".venv" / "bin").mkdir(parents=True)
    (project / ".venv" / "bin" / "python").write_text("", encoding="utf-8")
    (project / "bot.py").write_text("def play(turn): ...\n", encoding="utf-8")
    config = tmp_path / "opponents.local.toml"
    config.write_text(f'[opponents.outside_player]\ndirectory = "{project}"\n', encoding="utf-8")
    loaded = opponents.load_opponents(config)
    assert list(loaded) == ["outside_player"]
    spec = loaded["outside_player"].specification()
    assert spec["worker"] == [str(project / ".venv/bin/python"), "-m", "island_battles_client.worker", "bot:play"]
    assert spec["directory"] == str(project)
    before = loaded["outside_player"].fingerprint()
    # The project's virtual environment isn't its code; its own files are.
    (project / ".venv" / "lib.py").write_text("x = 1\n", encoding="utf-8")
    assert loaded["outside_player"].fingerprint() == before
    (project / "bot.py").write_text("def play(turn): return None\n", encoding="utf-8")
    assert loaded["outside_player"].fingerprint() != before
    assert opponents.load_opponents(tmp_path / "missing.toml") == {}


def test_an_outside_opponent_needs_its_interpreter(tmp_path: Path) -> None:
    from league_tools import opponents

    config = tmp_path / "opponents.local.toml"
    config.write_text(f'[opponents.outside_player]\ndirectory = "{tmp_path}"\n', encoding="utf-8")
    with pytest.raises(ValueError, match="no interpreter"):
        opponents.load_opponents(config)


def test_sparring_is_a_status(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(roster, "BOTS", tmp_path)
    (tmp_path / "rival").mkdir()
    (tmp_path / "rival" / "bot.py").write_text("def play(turn): ...\n", encoding="utf-8")
    roster.write_bot(roster.Bot(name="rival", status="sparring", parent="", iteration=22, idea="plays like a rival"))
    assert roster.load_bot("rival").status == "sparring"


def replay_demo() -> dict:
    """Two boards: blue's castle 0 buys production and sends 46 soldiers at red's castle 2, which makes the third."""
    group = {
        "id": 0,
        "team_color": 1,
        "soldiers": 46,
        "x": -2.5,
        "y": 0,
        "origin_castle_id": 0,
        "destination_castle_id": 2,
        "clash_radius": 0.25,
        "upgrades": {"speed": 1},
    }
    first = {
        "id": 1,
        "castles": [castle(0, 1, 60, -3), castle(1, 0, 5, 0), castle(2, 2, 10, 3)],
        "soldier_groups": [],
        "clashes": [],
    }
    second = {
        "id": 2,
        "castles": [castle(0, 1, 4, -3, {"generation_amount": 2}), castle(1, 0, 5, 0), castle(2, 2, 11, 3)],
        "soldier_groups": [group],
        "clashes": [],
    }
    return {"frames": [first, second, second | {"id": 3}]}


def test_replay_reads_a_known_send_and_upgrade_off_the_boards() -> None:
    first, second = replay.team_commands(replay_demo(), 1)[:2]
    assert first["upgrades"] == [{"castle": 0, "type": "generation_amount", "level": 2, "cost": 10}]
    assert [(send["origin"], send["dest"], send["amount"]) for send in first["sends"]] == [(0, 2, 46)]
    assert first["sends"][0]["distance"] == 6.0
    assert second["upgrades"] == [] and second["sends"] == []


def fixture_play(turn: BotTurn) -> BotTurnResult:
    """The replay demo's blue team: a castle at production 1 with 56 soldiers buys production and sends 46."""
    commands = []
    for own in turn.generation.castles:
        if own.team_color != turn.team_color or own.upgrades[UpgradeType.generation_amount] != 1 or own.soldiers < 56:
            continue
        enemy = next(c for c in turn.generation.castles if c.team_color not in (turn.team_color, NEUTRAL_TEAM_COLOR))
        commands += [upgrade_castle(own.id, UpgradeType.generation_amount), send_soldier_group(own.id, enemy.id, 46)]
    return turn_result(commands)


def test_a_bot_replayed_on_boards_it_made_agrees_fully(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A bot of the test's own, so the test needs no bot of the population, which the population rules may delete."""
    demo = replay_demo()
    path = tmp_path / "game.json.gz"
    path.write_bytes(gzip.compress(json.dumps(demo).encode()))
    monkeypatch.setattr(replay, "load_bot", lambda name: SimpleNamespace(play=fixture_play))
    report = replay.replay([("game", digest.load_demo(path))], "fixture", color=1)
    assert report.stats["turns"] == 2
    assert report.stats["exact"] == report.stats["loose"] == 2  # turn 2: neither the team nor the bot did anything
    assert (report.stats["upgrade tp"], report.stats["neutral team"], report.stats["attack tp"]) == (1, 0, 1)
    assert report.stats["attack team"] == report.stats["attack bot"] == 1
    assert "exact turn match" in report.text() and "bot: fixture" in report.text()


def test_rematch_finds_the_first_turn_a_candidate_commands_otherwise() -> None:
    before = replay.team_commands(replay_demo(), 1)
    assert rematch.first_difference(before, replay.team_commands(replay_demo(), 1)) is None
    other = replay_demo()
    other["frames"][1]["soldier_groups"][0]["soldiers"] = 40
    after = replay.team_commands(other, 1)
    assert rematch.first_difference(before, after) == 1
    assert rematch.describe(before[0]) == "generation_amount 2 at 0, 46 from 0 to 2"
    assert rematch.describe(after[1]) == "nothing"
    # A send to castle 0 is not an unseen send.
    to_home = {"turn": 1, "upgrades": [], "sends": [{"origin": 2, "dest": 0, "amount": 5}]}
    unseen = {"turn": 1, "upgrades": [], "sends": [{"origin": None, "dest": None, "amount": 5}]}
    assert rematch.first_difference([to_home], [unseen]) == 1
    assert rematch.describe(to_home) == "5 from 2 to 0"


def test_rematch_seats_the_candidate_where_its_parent_sat(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    for kind in ("train", "holdout"):
        (tmp_path / kind).mkdir()
        (tmp_path / kind / f"{kind}-map.json").write_text("{}")
    monkeypatch.setattr(rematch.tournament, "map_files", lambda name: [tmp_path / name.split("-")[0] / f"{name}.json"])

    def game(key: str, map_name: str) -> Path:
        (tmp_path / f"{key}.json").write_text(json.dumps(result("rival", "parent", "rival", map_name)))
        demo = tmp_path / f"{key}.json.gz"
        demo.write_bytes(b"demo")
        return demo

    (source,) = rematch.plan([game("a", "train-map")], "child", "parent")
    assert source.seats == ["rival", "child"] and source.map_file.parent.name == "train"
    with pytest.raises(ValueError, match="holdout"):
        rematch.plan([game("b", "holdout-map")], "child", "parent")
    with pytest.raises(ValueError, match="didn't play"):
        rematch.plan([game("c", "train-map")], "child", "stranger")
    loose = tmp_path / "saved.json"
    loose.write_text("{}")
    with pytest.raises(ValueError, match="no result beside it"):
        rematch.plan([loose], "child", "parent")


def test_rematch_compares_with_the_parents_game_as_it_plays_now(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Each game is played twice, parent and candidate; a game named twice is played and counted once."""
    (tmp_path / "train").mkdir()
    (tmp_path / "train" / "duel.json").write_text("{}")
    monkeypatch.setattr(rematch.tournament, "map_files", lambda name: [tmp_path / "train" / f"{name}.json"])
    acting = replay_demo()
    acting["frames"][1]["soldier_groups"][0]["soldiers"] = 40
    demos = {"same.json.gz": replay_demo(), "acting.json.gz": acting}
    monkeypatch.setattr(rematch, "load_demo", lambda path: demos.get(path.name, replay_demo()))

    def game(players: list[str], winner: str | None, key: str, demo: str) -> dict:
        seats = [
            {"name": name, "team_color": color, "failed_turns": 0, "failures": []}
            for color, name in [(1, players[0]), (2, players[1])]
        ]
        return result(*players, winner, "duel") | {"id": key, "seats": seats, "demo": demo}

    studied = []
    for key, opponent in (("a", "rival"), ("b", "other")):
        (tmp_path / f"{key}.json").write_text(json.dumps(game(["parent", opponent], opponent, key, "")))
        (tmp_path / f"{key}.json.gz").write_bytes(b"demo")
        studied.append(tmp_path / f"{key}.json.gz")
    played: list[list[list[str]]] = []

    def play_matches(matches: list, run_directory: Path, **settings: int) -> list[dict]:
        played.append([seats for _, seats in matches])
        assert settings == {"max_generations": 200, "turn_timeout_milliseconds": 2000}
        return [
            # The parent's game against rival is the studied one; against other, something changed.
            game(["parent", "rival"], "rival", "a", "a.json.gz"),
            game(["child", "rival"], "rival", "c1", "same.json.gz"),
            game(["parent", "other"], "other", "b2", "b2.json.gz"),
            game(["child", "other"], "child", "c2", "acting.json.gz"),
        ]

    monkeypatch.setattr(rematch.tournament, "play_matches", play_matches)
    text, _ = rematch.run(
        [studied[0], studied[0], studied[1]], "child", "parent", tmp_path / "run", max_generations=200
    )
    assert played == [[["parent", "rival"], ["child", "rival"], ["parent", "other"], ["child", "other"]]]
    rival, other = text.split("## duel, against ")[1:]
    assert "never acted" in rival and "changed since" not in rival
    assert "changed since the studied game" in other and "First different command: turn 1" in other
    assert "40 from 0 to 2" in other and "Points in these games (2): parent 0, child 1." in text


def test_the_ledger_brief_keeps_the_lessons_every_idea_and_the_last_entries() -> None:
    from league_tools import ledger

    text = "\n".join(
        [
            "# The league's ledger",
            "",
            "## Lessons so far",
            "",
            "- A lesson.",
            "",
            "## Iteration 1: first",
            "",
            "| Candidate | Parent | Idea | Against parent | Decision |",
            "|---|---|---|---|---|",
            "| `old_idea` | founder | Strike early. | 3/18 | **rejected**: below its parent. |",
            "",
            "A long standings table nobody needs again.",
            "",
            "## Setup after iteration 1: a new map",
            "",
            "## Iteration 2: second",
            "",
            "| Candidate | Parent | Idea | Against parent | Decision |",
            "|---|---|---|---|---|",
            "| `new_idea` | old | Hold. | 12/18 | **promoted** |",
        ]
    )
    brief = ledger.brief(text, recent=1)
    assert "- A lesson." in brief
    assert "- 1: `old_idea` from founder: Strike early. (against parent 3/18) **rejected**: below its parent." in brief
    assert "- 2: `new_idea` from old: Hold. (against parent 12/18) **promoted**" in brief
    assert "A long standings table" not in brief
    assert "- Iteration 1: first" in brief and "- Setup after iteration 1: a new map" in brief
    assert brief.rstrip().endswith("| `new_idea` | old | Hold. | 12/18 | **promoted** |")


def test_the_clock_times_steps_counts_a_step_started_again_and_reports_the_open_ones(tmp_path: Path) -> None:
    import datetime

    path = tmp_path / "clock.jsonl"
    at = datetime.datetime(2026, 11, 23, 8, 0, tzinfo=datetime.UTC)
    minutes = lambda n: at + datetime.timedelta(minutes=n)  # noqa: E731
    clock.mark("start", "0 ledger", path, minutes(0))
    clock.mark("stop", "0 ledger", path, minutes(2))
    clock.mark("start", "2 study", path, minutes(2))
    clock.mark("stop", "2 study", path, minutes(8))
    clock.mark("start", "2 study", path, minutes(9))
    path.write_text(path.read_text() + "not an event\n")
    text = clock.report(clock.load(path), now=minutes(10))
    assert "| 0 ledger | 08:00:00 | 08:02:00 | 2.0 | 20% |" in text
    assert "| 2 study | 08:02:00 | 08:08:00 | 6.0 | 60% |" in text
    assert "| 2 study #2 | 08:09:00 | open | 1.0 | 10% |" in text
    assert "Total: 10.0 minutes" in text
    assert "Slowest: 2 study (6.0)" in text
    assert "Still open (counted to now): 2 study #2." in text
    assert clock.reset(path) == 5
    assert clock.load(path) == []
    with pytest.raises(ValueError):
        clock.mark("start", "", path)
    with pytest.raises(ValueError):
        clock.mark("pause", "0 ledger", path)
