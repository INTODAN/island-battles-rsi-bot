"""The detectors, their flags' cache and ``league mistakes``.

Demos are built here, small and in the shape a real league demo has
(``runs/cache/<key>.json.gz``): the repository holds no demo. A last test
runs every detector over the demos this machine's cache holds, when it holds
some, and checks that none flags most of a game.
"""

import gzip
import json
import sys
from pathlib import Path
from typing import Any

import pytest

from league_tools import cli, digest, flags, mistakes, tournament
from league_tools.detectors import (
    Flag,
    _board,
    home_emptied,
    idle_lead,
    long_walk,
    thin_border,
    trickled_attack,
    turning_point,
)
from league_tools.paths import CACHE

PACKAGE = Path(flags.PACKAGE)

# The rule lives in hosting/rsi/scope.py, which checks a run's added detectors
# from their source before anything imports them.
sys.path.insert(0, str(Path(__file__).parent.parent / "hosting" / "rsi"))
from scope import rule_breaks  # noqa: E402


def test_every_detector_module_imports_and_calls_only_what_is_allowed() -> None:
    sources = sorted(PACKAGE.glob("*.py"))
    assert len(sources) >= 7
    for path in sources:
        assert rule_breaks(path.read_text(encoding="utf-8")) == [], path.name


def test_the_import_rule_catches_what_it_must() -> None:
    assert rule_breaks("import os") == ["import os"]
    assert rule_breaks("from pathlib import Path") == ["from pathlib import Path"]
    assert rule_breaks("from league_tools import tournament") == ["from league_tools import tournament"]
    assert rule_breaks("from .. import paths") == ["from league_tools import paths"]
    assert rule_breaks("x = open('f')") == ["open"]
    assert rule_breaks("x = getattr(a, 'b')") == ["getattr"]
    assert rule_breaks("x = ().__class__.__subclasses__()") == [".__subclasses__", ".__class__"]
    assert rule_breaks("from league_tools import digest\nfrom . import _board\nimport math") == []


def test_the_registry_holds_every_detector_with_its_kind_and_docstring() -> None:
    assert flags.kinds() == [
        "home_emptied",
        "idle_lead",
        "long_walk",
        "thin_border",
        "trickled_attack",
        "turning_point",
    ]
    for module in flags.registry():
        assert "Cost:" in (module.__doc__ or ""), module.__name__
    assert flags.detectors_hash() == flags.detectors_hash() and len(flags.detectors_hash()) == 64


# Demos in the shape of the league's: a board per turn, the board of turn T at index T - 1.


def castle(
    castle_id: int, team: int, soldiers: int, x: float, y: float = 0, production: int = 1, speed: int = 1
) -> dict[str, Any]:
    return {
        "id": castle_id,
        "team_color": team,
        "soldiers": soldiers,
        "x": x,
        "y": y,
        "upgrades": {
            "burst_potential": 1,
            "clash_stop_generations": 1,
            "generation_amount": production,
            "speed": speed,
        },
        "burst_debt": 0,
    }


def group(
    group_id: int, team: int, soldiers: int, origin: int, target: int, x: float = 0, speed: int = 1
) -> dict[str, Any]:
    return {
        "id": group_id,
        "team_color": team,
        "soldiers": soldiers,
        "x": x,
        "y": 0,
        "origin_castle_id": origin,
        "destination_castle_id": target,
        "clash_radius": 0.25,
        "upgrades": {"burst_potential": 1, "clash_stop_generations": 1, "generation_amount": 1, "speed": speed},
    }


def board(castles: list[dict[str, Any]], groups: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {"id": 0, "castles": castles, "soldier_groups": groups or [], "clashes": []}


def demo(boards: list[dict[str, Any]], winner: int | None, reason: str = "last_team_standing") -> dict[str, Any]:
    return {
        "format": "island-battles-demo",
        "teams": [
            {"color": 1, "name": "first", "players": ["first"]},
            {"color": 2, "name": "second", "players": ["second"]},
        ],
        "outcome": {"reason": reason, "winner_team_color": winner, "summary": "", "departures": []},
        "frames": [frame | {"id": index + 1} for index, frame in enumerate(boards)],
        "logs": [{"players": []} for _ in boards],
    }


def turned_game(winner: int | None) -> dict[str, Any]:
    """Level for three turns, the second team ahead in production from turn 4, its capture on turn 6."""
    boards = []
    for index in range(10):
        first_home = castle(0, 1, 12 if index == 1 else 10, -4)
        their_production = 2 if index >= 3 else 1
        lost = index >= 6
        boards.append(
            board(
                [
                    first_home,
                    castle(1, 2, 10, 4, production=their_production),
                    castle(2, 2 if lost else 1, 10, -1),
                    castle(3, 2, 10, 1),
                ]
            )
        )
    return demo(boards, winner)


def test_turning_point_marks_the_turn_the_lead_held_and_the_castles_lost() -> None:
    (flag,) = turning_point.detect(turned_game(winner=2))
    assert (flag.team, flag.bot, flag.kind, flag.turns, flag.cost) == (1, "first", "turning_point", (4, 6), 1.0)
    assert "from turn 4 second led to the end" in flag.evidence and "castles lost: 2 on 6" in flag.evidence


def test_turning_point_is_silent_in_a_draw() -> None:
    assert turning_point.detect(turned_game(winner=None)) == []


def emptied_game(enemy_soldiers: int) -> dict[str, Any]:
    """The first team's castle 0 sends 26 of its 30 on turn 1 beside an enemy castle, and falls on turn 4."""
    boards = []
    for index in range(6):
        home = castle(0, 1 if index < 4 else 2, 30 if index == 0 else 4, 0)
        walking = [group(9, 1, 26, 0, 2, x=-index)] if 1 <= index <= 3 else []
        boards.append(board([home, castle(1, 2, enemy_soldiers, 2), castle(2, 2, 40, -10)], walking))
    return demo(boards, 2)


def test_home_emptied_flags_a_castle_emptied_beside_a_stocked_enemy_castle_that_then_fell() -> None:
    (flag,) = home_emptied.detect(emptied_game(enemy_soldiers=25))
    assert (flag.team, flag.turns, flag.cost) == (1, (1, 4), 2.0)
    assert "castle 0 30 -> 4 soldiers (26 sent) while enemy castle 1 held 25, 4 turns away" in flag.evidence


def test_home_emptied_is_silent_when_no_near_enemy_castle_could_take_what_was_left() -> None:
    # 5 soldiers 4 turns away can't take 4 that grow 1 a turn: the castle fell to something else.
    assert home_emptied.detect(emptied_game(enemy_soldiers=5)) == []


def thin_game(rear_soldiers: int) -> dict[str, Any]:
    """The first team's border castle holds 5 beside an enemy castle of 20 for five turns, and falls on turn 5."""
    boards = [
        board(
            [
                castle(0, 1 if index < 5 else 2, 5, 0),
                castle(1, 2, 20, 2),
                castle(2, 1, rear_soldiers, -5),
                castle(3, 2, 10, 7),
            ]
        )
        for index in range(8)
    ]
    return demo(boards, 2)


def test_thin_border_flags_a_border_castle_lost_while_the_rear_held_many() -> None:
    (flag,) = thin_border.detect(thin_game(rear_soldiers=40))
    assert (flag.team, flag.turns, flag.cost) == (1, (1, 5), 3.0)
    assert "border castle 0 held 5 (turns 1-5) while castle 2 held 40" in flag.evidence


def test_thin_border_is_silent_when_the_rear_held_little_more() -> None:
    assert thin_border.detect(thin_game(rear_soldiers=12)) == []


def trickle_game(size: int) -> dict[str, Any]:
    """Three groups of ``size`` sent on turns 1 to 3 at an enemy castle of 20, landing on turns 5 to 7."""
    boards = []
    for index in range(10):
        walking = [group(10 + sent, 1, size, 0, 1, x=index - sent) for sent in (1, 2, 3) if sent <= index <= sent + 3]
        boards.append(board([castle(0, 1, 50, 0), castle(1, 2, 20, 4)], walking))
    return demo(boards, None, "generation_cap")


def test_trickled_attack_flags_groups_that_landed_alone_and_together_would_have_taken_it() -> None:
    (flag,) = trickled_attack.detect(trickle_game(size=8))
    assert (flag.team, flag.turns, flag.cost) == (1, (1, 7), 24.0)
    assert "3 groups at castle 1 each landed and lost alone (8 on 5, 8 on 6, 8 on 7)" in flag.evidence


def test_trickled_attack_is_silent_when_together_they_were_still_too_few() -> None:
    assert trickled_attack.detect(trickle_game(size=5)) == []


def walk_game(speed: int) -> dict[str, Any]:
    """A group of 20 sent on turn 1 at an enemy castle 10 units off, on a board whose castles stand 1 apart."""
    turns = 10 / (0.5 * speed)
    boards = []
    for index in range(25):
        walking = [group(5, 1, 20, 0, 3, x=index * 0.5 * speed, speed=speed)] if 1 <= index <= turns - 1 else []
        boards.append(
            board([castle(0, 1, 10, 0), castle(1, 1, 10, -1), castle(2, 2, 10, 11), castle(3, 2, 30, 10)], walking)
        )
    return demo(boards, None, "generation_cap")


def test_long_walk_flags_an_attack_that_walked_many_turns_and_took_nothing() -> None:
    (flag,) = long_walk.detect(walk_game(speed=1))
    assert (flag.team, flag.turns, flag.cost) == (1, (1, 20), 20.0)
    assert "10.0 units in 20 turns at speed level 1, where the board's step is 1.0" in flag.evidence


def test_long_walk_is_silent_when_speed_made_the_walk_short() -> None:
    assert long_walk.detect(walk_game(speed=4)) == []


def lead_game(reason: str, second_soldiers: int) -> dict[str, Any]:
    boards = [board([castle(0, 1, 100, 0), castle(1, 2, second_soldiers, 5)]) for _ in range(120)]
    return demo(boards, None, reason)


def test_idle_lead_flags_a_long_clear_lead_in_a_game_that_ran_to_the_limit() -> None:
    (flag,) = idle_lead.detect(lead_game("generation_cap", 50))
    assert (flag.team, flag.turns, flag.cost) == (1, (1, 120), 120.0)


def test_idle_lead_is_silent_when_the_lead_is_slim_or_the_game_ended_early() -> None:
    assert idle_lead.detect(lead_game("generation_cap", 80)) == []
    assert idle_lead.detect(lead_game("last_team_standing", 50)) == []


def test_flags_are_computed_once_per_match_and_kept_under_the_detectors_hash(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(flags, "CACHE", tmp_path)
    path = tmp_path / "match.json.gz"
    path.write_bytes(gzip.compress(json.dumps(turned_game(winner=2)).encode()))
    found = flags.flags_for({"id": "match", "demo": str(path)})
    assert [flag.kind for flag in found] == ["turning_point"]
    assert flags.flags_path("match") == tmp_path / f"match.flags-{flags.detectors_hash()[:12]}.json"
    assert flags.flags_path("match").is_file()

    def fail(_demo: dict[str, Any]) -> list[Flag]:
        raise AssertionError("the flags were computed again")

    monkeypatch.setattr(flags, "run_all", fail)
    assert flags.flags_for({"id": "match", "demo": str(path)}) == found


def test_mistakes_sum_each_bots_flags_by_kind(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(flags, "CACHE", tmp_path)
    results = []
    for index, (game, winner) in enumerate(((turned_game(2), "second"), (emptied_game(25), "second"))):
        path = tmp_path / f"{index}.json.gz"
        path.write_bytes(gzip.compress(json.dumps(game).encode()))
        results.append(
            {
                "id": str(index),
                "map": f"map{index}",
                "players": ["first", "second"],
                "seats": [{"team_color": 1}, {"team_color": 2}],
                "winner": winner,
                "generations": len(game["frames"]),
                "demo": str(path),
            }
        )
    found = mistakes.tables(results, ["first", "second"], examples=1)
    rows = {row.kind: row for row in found["first"]}
    assert (rows["turning_point"].games, len(rows["turning_point"].maps), rows["turning_point"].points_lost) == (
        2,
        2,
        2,
    )
    assert rows["home_emptied"].games == 1 and rows["home_emptied"].cost == 2
    assert [example["generations"] for example in rows["turning_point"].examples] == [6]
    assert all(row.games == 0 for row in found["second"])
    text = mistakes.markdown(found, mistakes.games_played(results))
    assert "| turning_point | 2 | 2 | 2 | 2 |" in text and "## second: 2 games" in text
    assert json.loads(json.dumps(mistakes.as_json(found)))["first"][0]["kind"] == "turning_point"


def test_mistakes_refuse_holdout_maps(capsys: pytest.CaptureFixture[str]) -> None:
    holdout = tournament.map_files("holdout")[0].stem
    assert cli.main(["mistakes", "--maps", holdout, "--anchors", ""]) == 1
    assert "holdout" in capsys.readouterr().err


# The demos this machine's cache holds: none on a machine that never played a tournament.
CACHED_DEMOS = sorted(CACHE.glob("*.json.gz"))[:200]


@pytest.mark.skipif(len(CACHED_DEMOS) < 20, reason="the local result cache holds too few demos")
def test_no_detector_flags_most_of_the_games_this_machine_played() -> None:
    """Every detector over up to 200 real demos of the local cache.

    Each flag's turns lie in its game and point where its kind says, and no
    detector flags most of the games' turns: one that did would tell nobody
    anything.
    """
    demos = CACHED_DEMOS
    flagged = {kind: 0 for kind in flags.kinds()}
    mostly = {kind: 0 for kind in flags.kinds()}
    turns = 0
    for path in demos:
        game = digest.load_demo(path)
        length = len(game["frames"])
        turns += length
        covered: dict[str, set[int]] = {kind: set() for kind in flags.kinds()}
        lost = {(capture.turn, capture.lost_by) for capture in _board.captures(game) if capture.taken_by}
        for flag in flags.run_all(game):
            assert 1 <= flag.turns[0] <= flag.turns[1] <= length, (path, flag)
            assert flag.bot == _board.team_names(game)[flag.team] and flag.cost >= 0, (path, flag)
            if flag.kind in ("home_emptied", "thin_border"):
                # Each ends on the turn the enemy took the flagged team's castle.
                assert (flag.turns[1], flag.team) in lost, (path, flag)
            if flag.kind == "turning_point":
                assert _board.winner(game) not in (None, flag.team), (path, flag)
            covered[flag.kind].update(range(flag.turns[0], flag.turns[1] + 1))
        for kind, seen in covered.items():
            flagged[kind] += len(seen)
            mostly[kind] += len(seen) * 2 > length
    for kind in flags.kinds():
        assert flagged[kind] < turns / 4, kind
        assert mostly[kind] < len(demos) / 10, kind
