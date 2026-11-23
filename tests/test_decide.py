"""The selection's and the population's rules as code: league_tools/decide.py and league_tools/lines.py."""

from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

import pytest

from league_tools import cli, decide, lines, tournament
from league_tools.decide import Candidate, Decision, Evidence, Numbers
from league_tools.lines import Line, Lines
from league_tools.roster import Bot

# --- Building summaries as tournament.summarize and tournament.run give them --------


def compared(better: int, worse: int, luck: float, maps: dict[str, int] | None = None) -> dict[str, Any]:
    """What tournament.paired returns, with the chance by luck given."""
    maps = maps if maps is not None else {"strait": better - worse}
    return {
        "better": better,
        "worse": worse,
        "same": 10,
        "net": float(better - worse),
        "drawn_better": 0,
        "drawn_worse": 0,
        "unread": 0,
        "maps": maps,
        "luck": luck,
    }


def summary(
    ratings: dict[str, int],
    pairs: Mapping[tuple[str, str], tuple[float, float]] | None = None,
    paired: dict[str, dict[str, Any]] | None = None,
    compare: dict[str, dict[str, dict[str, Any]]] | None = None,
    alike: Iterable[tuple[str, str]] = (),
    failed: dict[str, int] | None = None,
) -> dict[str, Any]:
    """A tournament summary: standings, the pair table (both ways), the paired tables and the bots alike."""
    table: dict[str, dict[str, list[float]]] = {name: {} for name in ratings}
    for (first, second), (points, games) in (pairs or {}).items():
        table.setdefault(first, {})[second] = [points, games]
        table.setdefault(second, {})[first] = [games - points, games]
    standings = [
        {
            "player": name,
            "rating": rating,
            "failed_turns": (failed or {}).get(name, 0),
            "slowest_turn_milliseconds": 10.0,
        }
        for name, rating in sorted(ratings.items(), key=lambda item: -item[1])
    ]
    out: dict[str, Any] = {"standings": standings, "pairs": table, "paired": paired or {}}
    out["alike"] = [{"bots": sorted(pair), "games": 100, "same_game": 0.9, "same_result": 0.9} for pair in alike]
    if compare:
        out["compared"] = compare
    return out


LINES = Lines(
    champion="champ",
    lines=[
        Line(name="main", strategy="the main strategy", state="main", head="champ", bots=["champ", "second"]),
        Line(name="side", strategy="a side strategy", state="side", head="sidehead", bots=["sidehead"]),
    ],
)
BOTS = ["champ", "second", "sidehead", "mimic", "fixed"]
REFERENCES = ["mimic"]


def fix(name: str = "cand", parent: str = "champ", kind: str = "fix", base_head: str | None = "champ") -> Candidate:
    return Candidate(
        name=name, kind=kind, parent=parent, line="main", idea=f"{kind.title()}: something", base_head=base_head
    )


def evidence(
    head_to_head: float = 31,
    train: dict[str, Any] | None = None,
    references: tuple[float, float] = (50, 50),
    holdout: dict[str, Any] | None = None,
    every: dict[str, Any] | None = None,
    name: str = "cand",
    parent: str = "champ",
) -> Evidence:
    """The runs of one fix against its parent: each step's table, or None for a run not played."""
    pairs = {(name, "mimic"): (references[0], 60), (parent, "mimic"): (references[1], 60), (name, parent): (30, 60)}

    def run(table: dict[str, Any] | None) -> dict[str, Any] | None:
        if table is None:
            return None
        return summary({name: 2000, parent: 1990, "mimic": 1800}, pairs, paired={name: table})

    return Evidence(
        head_to_head=summary({name: 0, parent: 0}, {(name, parent): (head_to_head, 60)}),
        train=run(train),
        holdout=run(holdout),
        all=run(every),
    )


def judge(candidate: Candidate, found: Evidence, main_go: dict[str, int] | None = None) -> Decision:
    (decision,) = decide.decide([candidate], found, LINES, [*BOTS, candidate.name], REFERENCES, main_go or {})
    return decision


GOOD_TRAIN = compared(30, 10, 0.01)


# --- A fix or a graft -----------------------------------------------------------


def test_a_fix_with_a_third_of_the_points_or_fewer_is_rejected_head_to_head() -> None:
    rejected = judge(fix(), evidence(head_to_head=20))
    assert rejected.decision == "rejected" and "a third of the points or fewer" in rejected.rule
    assert rejected.numbers.points == (20, 60) and rejected.numbers.train is None
    # Above a third it goes on, and waits for the training maps.
    going_on = judge(fix(), evidence(head_to_head=20.5))
    assert (going_on.decision, going_on.needs) == ("pending", "train")
    assert judge(fix(), Evidence()).needs == "head_to_head"


def test_a_fix_clearly_worse_on_the_training_maps_is_rejected_from_a_chance_of_a_fifth() -> None:
    worse = judge(fix(), evidence(train=compared(10, 11, 0.20)))
    assert worse.decision == "rejected" and "clearly worse" in worse.rule
    # Worse, not clearly: a margin a game or two below 0 rejects nothing.
    going_on = judge(fix(), evidence(train=compared(10, 11, 0.21)))
    assert (going_on.decision, going_on.needs) == ("pending", "holdout")


def test_a_fix_more_than_three_points_below_its_parent_against_the_references_is_rejected() -> None:
    exactly_three = judge(fix(), evidence(train=GOOD_TRAIN, references=(47, 50)))
    assert exactly_three.decision == "pending" and exactly_three.numbers.references == (47, 50)
    more = judge(fix(), evidence(train=GOOD_TRAIN, references=(46.5, 50)))
    assert more.decision == "rejected" and "against the references (46.5 to 50)" in more.rule


def test_the_references_leave_out_the_parent_when_it_is_one() -> None:
    table = summary({"a": 0, "mimic": 0, "other": 0}, {("a", "mimic"): (40, 60), ("a", "other"): (10, 60)})
    assert decide.references_points(table, "a", ["mimic", "other"], "mimic") == 10
    assert decide.references_points(table, "a", ["mimic", "other"], "") == 50


def test_a_fix_is_promoted_when_confirmed_on_holdout_and_clear_on_all_maps() -> None:
    promoted = judge(fix(), evidence(train=GOOD_TRAIN, holdout=compared(5, 2, 0.20), every=compared(35, 12, 0.05)))
    assert promoted.decision == "promoted" and promoted.numbers.all is not None
    assert promoted.numbers.holdout is not None and promoted.numbers.holdout.word == "confirmed"
    # Not clear on all maps, with a margin above 0: unresolved, not refuted.
    unresolved = judge(fix(), evidence(train=GOOD_TRAIN, holdout=compared(5, 2, 0.20), every=compared(35, 12, 0.06)))
    assert unresolved.decision == "unresolved" and "confirmed on all maps" in unresolved.rule
    # Not confirmed on the holdout maps, and no margin on all maps: rejected.
    rejected = judge(fix(), evidence(train=GOOD_TRAIN, holdout=compared(2, 5, 0.6), every=compared(12, 12, 1.0)))
    assert rejected.decision == "rejected" and "worse on the holdout maps" in rejected.rule


def test_a_failed_turn_or_an_unknown_kind_is_left_for_review() -> None:
    found = evidence()
    assert found.head_to_head is not None
    found.head_to_head["standings"][0]["failed_turns"] = 1
    assert judge(fix(), found).decision == "needs_review"
    unknown = Candidate(name="cand", kind=None, parent="champ", line="main", idea="Better strikes")
    assert judge(unknown, evidence()).decision == "needs_review"


# --- A simplification -------------------------------------------------------------


def test_a_simplification_needs_a_shorter_main_go_and_not_to_be_clearly_worse() -> None:
    simpler = fix(kind="simplification")
    longer = judge(simpler, evidence(train=GOOD_TRAIN), {"cand": 900, "champ": 900})
    assert longer.decision == "rejected" and "not shorter" in longer.rule
    shorter = {"cand": 850, "champ": 900}
    # A margin below 0 that is not clearly worse, and a references loss, don't reject a simplification.
    kept = judge(
        simpler,
        evidence(
            train=compared(8, 10, 0.5), references=(40, 50), holdout=compared(1, 2, 0.7), every=compared(9, 12, 0.4)
        ),
        shorter,
    )
    assert kept.decision == "promoted" and kept.numbers.main_go == (850, 900)
    worse = judge(
        simpler,
        evidence(train=compared(8, 10, 0.5), holdout=compared(1, 2, 0.7), every=compared(9, 30, 0.01)),
        shorter,
    )
    assert worse.decision == "rejected" and "clearly worse than champ on all maps" in worse.rule


# --- A founder and an exploiter -----------------------------------------------------


def strategy_evidence(name: str, points: float, alike: Iterable[tuple[str, str]] = (), train: bool = True) -> Evidence:
    champion = summary({name: 0, "champ": 0}, {(name, "champ"): (points, 60)})
    field = summary({name: 1900, "champ": 2100, "mimic": 1800}, alike=alike) if train else None
    return Evidence(champion=champion, train=field)


def founder(name: str = "found") -> Candidate:
    return Candidate(name=name, kind="founder", parent="mimic", line=name, idea="Founder: a new way")


def test_a_founder_needs_a_third_of_the_points_from_the_champion() -> None:
    assert judge(founder(), strategy_evidence("found", 20)).decision == "admitted"
    under = judge(founder(), strategy_evidence("found", 19.5))
    assert under.decision == "rejected" and "under a third" in under.rule
    assert judge(founder(), Evidence()).needs == "champion"
    assert judge(founder(), strategy_evidence("found", 25, train=False)).needs == "train"


def test_a_founder_alike_another_candidate_is_admitted_and_alike_a_league_bot_is_not() -> None:
    other = Candidate(name="other", kind="fix", parent="champ", line="main", idea="Fix: x", base_head="champ")
    found = strategy_evidence("found", 25, alike=[("found", "other")])
    decisions = decide.decide([founder(), other], found, LINES, [*BOTS, "found", "other"], REFERENCES, {})
    assert decisions[0].decision == "admitted"
    alike = judge(founder(), strategy_evidence("found", 25, alike=[("found", "second")]))
    assert alike.decision == "rejected" and "plays alike a bot of the league: second" in alike.rule


def test_founders_take_the_free_side_places_in_order() -> None:
    first, second = founder("one"), founder("two")
    found = Evidence(
        champion=summary({"one": 0, "two": 0, "champ": 0}, {("one", "champ"): (30, 60), ("two", "champ"): (30, 60)}),
        train=summary({"one": 1900, "two": 1900, "champ": 2100}),
    )
    decisions = decide.decide([first, second], found, LINES, [*BOTS, "one", "two"], REFERENCES, {}, max_side_lines=2)
    assert [decision.decision for decision in decisions] == ["admitted", "needs_review"]
    assert "no side place is free" in decisions[1].rule


def test_an_exploiter_needs_three_fifths_of_the_points_from_the_champion() -> None:
    exploiter = Candidate(name="exp", kind="exploiter", parent="champ", line=None, idea="Exploiter of champ: x")
    assert judge(exploiter, strategy_evidence("exp", 36)).decision == "admitted"
    assert judge(exploiter, strategy_evidence("exp", 35.5)).decision == "rejected"


# --- A candidate whose parent moved ------------------------------------------------------


def moved_evidence(head_to_head_against_head: float, against_head: dict[str, Any]) -> Evidence:
    """``cand`` was written from ``old``, the head then; ``champ`` is the head now."""
    ratings = {"cand": 2000, "old": 1980, "champ": 1990, "mimic": 1800}
    pairs = {("cand", "mimic"): (50, 60), ("old", "mimic"): (50, 60), ("champ", "mimic"): (50, 60)}

    def run(parent: dict[str, Any], head: dict[str, Any]) -> dict[str, Any]:
        return summary(ratings, pairs, compare={"cand": {"old": parent, "champ": head}})

    return Evidence(
        head_to_head=summary(ratings, {("cand", "old"): (35, 60), ("cand", "champ"): (head_to_head_against_head, 60)}),
        train=run(GOOD_TRAIN, against_head),
        holdout=run(compared(5, 2, 0.1), against_head),
        all=run(compared(35, 12, 0.01), against_head),
    )


def test_a_candidate_whose_parent_is_no_longer_the_head_is_judged_against_the_head() -> None:
    candidate = fix(parent="old", base_head="old")
    bots = [*BOTS, "old", "cand"]
    passes = decide.decide([candidate], moved_evidence(31, compared(30, 10, 0.01)), LINES, bots, REFERENCES, {})
    assert passes[0].decision == "promoted" and passes[0].numbers.against == "champ"
    assert passes[0].parent_numbers is not None and passes[0].parent_numbers.against == "old"
    superseded = decide.decide([candidate], moved_evidence(18, compared(30, 10, 0.01)), LINES, bots, REFERENCES, {})
    assert superseded[0].decision == "superseded" and "not against its line's head champ" in superseded[0].rule
    # Started from another bot of the line on purpose, it is judged against its parent alone.
    own = decide.decide([fix(parent="old")], moved_evidence(18, compared(30, 10, 0.01)), LINES, bots, REFERENCES, {})
    assert own[0].decision == "promoted" and own[0].parent_numbers is None


# --- The population's upkeep ----------------------------------------------------------


def bot(name: str, status: str, parent: str = "", idea: str = "Fix: x") -> Bot:
    return Bot(name=name, status=status, parent=parent, iteration=1, idea=idea)


class Field:
    """A measure that knows each bot's rating, the pairs that play alike and the points taken from the champion."""

    def __init__(
        self,
        ratings: dict[str, int],
        alike: Iterable[tuple[str, str]] = (),
        pairs: Mapping[tuple[str, str], tuple[float, float]] | None = None,
        holdout: dict[str, int] | None = None,
    ) -> None:
        self.ratings, self.alike, self.pairs, self.holdout = ratings, list(alike), pairs or {}, holdout
        self.measured: list[tuple[list[str], str]] = []

    def __call__(self, population: list[str], maps: str) -> dict[str, Any]:
        self.measured.append((population, maps))
        here = set(population) | {"outside"}
        ratings = self.holdout if maps == "holdout" and self.holdout else self.ratings
        return summary(
            {name: rating for name, rating in ratings.items() if name in here},
            {pair: points for pair, points in self.pairs.items() if set(pair) <= here},
            alike=[pair for pair in self.alike if set(pair) <= here],
        )


ROSTER = [
    bot("champ", "active"),
    bot("second", "active", "champ"),
    bot("sidehead", "active", idea="Founder: x"),
    bot("mimic", "sparring"),
    bot("fixed", "retired"),
]
RATINGS = {"champ": 2100, "second": 2050, "sidehead": 1900, "mimic": 1800, "fixed": 1950}


def decision(name: str, outcome: str, parent: str = "champ", line: str | None = "main", kind: str = "fix") -> Decision:
    candidate = Candidate(name=name, kind=kind, parent=parent, line=line, idea=f"{kind.title()}: x", base_head=parent)
    return Decision(candidate, outcome, "the rule", Numbers(against=parent))


def kinds(actions: list[decide.Action]) -> list[tuple[str, str, str | None]]:
    return [(action.kind, action.bot, action.status) for action in actions]


def line_named(found: Lines, name: str) -> Line:
    line = found.get(name)
    assert line is not None
    return line


def test_the_current_population_without_candidates_has_no_actions() -> None:
    result = decide.upkeep([], LINES, ROSTER, Field(RATINGS), 40)
    assert result.actions == [] and result.lines == LINES and not result.champion_changed


def test_a_promotion_from_the_head_makes_the_head_and_the_champion() -> None:
    roster_now = [*ROSTER, bot("a", "candidate", "champ"), bot("b", "candidate", "champ"), bot("c", "candidate")]
    train = summary({"a": 2120, "b": 2140, "champ": 2100})
    decisions = [decision("a", "promoted"), decision("b", "promoted"), decision("c", "rejected")]
    result = decide.upkeep(decisions, LINES, roster_now, Field(RATINGS | {"a": 2120, "b": 2140}), 40, train=train)
    assert ("status", "a", "active") in kinds(result.actions) and ("delete", "c", None) in kinds(result.actions)
    # Two promoted from the head: the higher-rated is the head, and the champion.
    assert result.lines.champion == "b" and result.lines.main.head == "b" and result.champion_changed
    assert {"a", "b"} <= set(result.lines.main.bots) and LINES.champion == "champ"
    # Four active bots in the main line: the lowest-rated that is not the head is retired.
    assert ("status", "second", "retired") in kinds(result.actions)


def test_of_two_bots_that_play_alike_the_one_with_fewer_points_from_the_champion_leaves() -> None:
    roster_now = [*ROSTER, bot("third", "retired")]
    pairs = {("second", "champ"): (20, 60), ("third", "champ"): (25, 60)}
    field = Field(RATINGS | {"third": 1900}, alike=[("second", "third")], pairs=pairs)
    result = decide.upkeep([], LINES, roster_now, field, 40)
    assert kinds(result.actions) == [("delete", "second", None)] and "fewer points" in result.actions[0].reason
    assert line_named(result.lines, "main").bots == ["champ"]
    # It was measured again once the bot left, and then nothing was left to clear.
    assert len(field.measured) == 2 and "second" not in field.measured[1][0]


def test_the_champion_sparring_bots_and_outside_opponents_never_leave() -> None:
    field = Field(RATINGS, alike=[("champ", "second"), ("mimic", "fixed"), ("mimic", "outside"), ("champ", "mimic")])
    result = decide.upkeep([], LINES, ROSTER, field, 40, outside=["outside"])
    assert kinds(result.actions) == [("delete", "second", None), ("delete", "fixed", None)]


def test_a_promoted_bot_that_plays_alike_its_parent_replaces_it() -> None:
    roster_now = [*ROSTER, bot("child", "candidate", "second")]
    # The parent takes more from the champion, and still leaves.
    pairs = {("second", "champ"): (30, 60), ("child", "champ"): (20, 60)}
    field = Field(RATINGS | {"child": 2000}, alike=[("child", "second")], pairs=pairs)
    result = decide.upkeep([decision("child", "promoted", parent="second")], LINES, roster_now, field, 40)
    assert ("delete", "second", None) in kinds(result.actions) and "replaces it" in result.actions[-1].reason
    # Its parent was not the head: the champion stays.
    assert result.lines.champion == "champ"


def test_a_promoted_bot_replaces_its_parent_as_the_head_of_a_side_line() -> None:
    roster_now = [*ROSTER, bot("sidechild", "candidate", "sidehead")]
    field = Field(RATINGS | {"sidechild": 1890}, alike=[("sidechild", "sidehead")])
    promoted = decision("sidechild", "promoted", parent="sidehead", line="side")
    result = decide.upkeep([promoted], LINES, roster_now, field, 40)
    # Promoted from the head, it is the head at once; its parent then leaves for playing alike it.
    assert line_named(result.lines, "side").head == "sidechild"
    assert ("delete", "sidehead", None) in kinds(result.actions)
    assert line_named(result.lines, "side").without_promotion == 0


def test_a_side_line_closes_after_two_iterations_of_work_without_a_promotion() -> None:
    once = Lines(
        champion="champ", lines=[LINES.lines[0], Line("side", "s", "side", "sidehead", ["sidehead", "old"], 1)]
    )
    roster_now = [*ROSTER, bot("old", "retired", "sidehead"), bot("try", "candidate", "sidehead")]
    rejected = decision("try", "rejected", parent="sidehead", line="side")
    result = decide.upkeep([rejected], once, roster_now, Field(RATINGS | {"old": 1700}), 40)
    side = result.lines.get("side")
    assert side is not None and side.state == "closed" and side.without_promotion == 2
    assert ("status", "sidehead", "retired") in kinds(result.actions) and ("delete", "old", None) in kinds(
        result.actions
    )
    # Its first iteration of work without a promotion counts one; an iteration without its candidate counts none.
    first = decide.upkeep([rejected], LINES, roster_now, Field(RATINGS | {"old": 1700}), 40)
    assert line_named(first.lines, "side").without_promotion == 1
    idle = decide.upkeep([decision("m", "rejected")], once, roster_now, Field(RATINGS | {"old": 1700}), 40)
    assert line_named(idle.lines, "side").without_promotion == 1
    assert idle.lines.main.without_promotion == 1


def test_an_admitted_founder_starts_a_side_line_and_an_exploiter_is_a_fixed_opponent() -> None:
    roster_now = [*ROSTER, bot("found", "candidate", "mimic", "Founder: x"), bot("exp", "candidate", "champ")]
    decisions = [
        decision("found", "admitted", parent="mimic", line="found", kind="founder"),
        decision("exp", "admitted", line=None, kind="exploiter"),
    ]
    result = decide.upkeep(decisions, LINES, roster_now, Field(RATINGS | {"found": 1950, "exp": 2200}), 40)
    assert ("status", "found", "active") in kinds(result.actions) and ("status", "exp", "retired") in kinds(
        result.actions
    )
    found = result.lines.get("found")
    assert found is not None and (found.state, found.head, found.without_promotion) == ("side", "found", 0)


def test_over_eight_fixed_opponents_the_one_that_takes_fewest_from_the_active_bots_leaves() -> None:
    fixed = [f"old{index}" for index in range(9)]
    roster_now = [*ROSTER[:4], *(bot(name, "retired") for name in fixed)]
    pairs = {(name, "champ"): (10 + index, 60) for index, name in enumerate(fixed)}
    pairs[("old3", "champ")] = (2, 60)
    result = decide.upkeep([], LINES, roster_now, Field(RATINGS | dict.fromkeys(fixed, 1900), pairs=pairs), 40)
    assert kinds(result.actions) == [("delete", "old3", None)]


def test_the_main_line_changes_when_a_side_head_beats_the_champion() -> None:
    pairs = {("sidehead", "champ"): (30, 60)}
    field = Field(RATINGS | {"sidehead": 2150}, pairs=pairs, holdout=RATINGS | {"sidehead": 2100})
    result = decide.upkeep([], LINES, ROSTER, field, 40)
    assert result.lines.champion == "sidehead" and result.champion_changed
    assert result.lines.main.name == "side" and line_named(result.lines, "main").state == "side"
    # Below the champion on the holdout maps, or under half the points against it: nothing changes.
    below = Field(RATINGS | {"sidehead": 2150}, pairs=pairs, holdout=RATINGS | {"sidehead": 2099})
    assert decide.upkeep([], LINES, ROSTER, below, 40).lines.champion == "champ"
    fewer = Field(RATINGS | {"sidehead": 2150}, pairs={("sidehead", "champ"): (29.5, 60)})
    assert decide.upkeep([], LINES, ROSTER, fewer, 40).lines.champion == "champ"
    assert [maps for _, maps in fewer.measured] == ["train"]


def test_a_tie_the_rules_cant_break_is_left_for_review() -> None:
    roster_now = [*ROSTER, bot("twin", "retired")]
    field = Field(RATINGS | {"twin": 1950}, alike=[("fixed", "twin")])
    result = decide.upkeep([], LINES, roster_now, field, 40)
    assert [action.kind for action in result.actions] == ["needs_review"] and result.reviews


def test_the_side_lines_cap_is_one_constant() -> None:
    assert decide.MAX_SIDE_LINES == 4
    three = Lines(champion="champ", lines=[*LINES.lines, Line("b", "b", "side", "b", ["b"]), Line("c", "c", "side")])
    result = decide.upkeep([], three, ROSTER, Field(RATINGS), 40, max_side_lines=2)
    assert result.reviews and "over the cap of 2" in result.reviews[0].reason
    assert not decide.upkeep([], three, ROSTER, Field(RATINGS), 40).reviews


# --- The lines file -----------------------------------------------------------------------


def test_the_lines_file_round_trips_and_names_the_champion(tmp_path: Path) -> None:
    path = tmp_path / "lines.toml"
    lines.write_lines(LINES, path)
    assert lines.load_lines(path) == LINES
    path.write_text(lines.dumps(LINES).replace('champion = "champ"', 'champion = "second"'))
    with pytest.raises(ValueError, match="not the main line's head"):
        lines.load_lines(path)
    league = lines.load_lines()
    assert league.champion == league.main.head and len(league.side) <= decide.MAX_SIDE_LINES


def test_a_bots_line_is_its_listing_its_parents_or_its_own() -> None:
    known = {
        "fresh": bot("fresh", "candidate", "second"),
        "deeper": bot("deeper", "candidate", "fresh"),
        "found": bot("found", "candidate", "champ", "Founder: a new way"),
        "exp": bot("exp", "candidate", "champ", "Exploiter of champ: x"),
        "mimic": bot("mimic", "sparring"),
        "fromspar": bot("fromspar", "candidate", "mimic"),
    }
    assert [lines.line_of(name, LINES, known) for name in known] == ["main", "main", "found", None, None, None]
    assert lines.line_of("champ", LINES, known) == "main"
    assert lines.kind_of("Graft from x: y") == "graft" and lines.kind_of("(b) A strike") is None


# --- league decide -------------------------------------------------------------------------


def test_play_selection_plays_the_runs_the_skill_plays(monkeypatch: pytest.MonkeyPatch) -> None:
    league = [*ROSTER, bot("cand", "candidate", "champ"), bot("found", "candidate", "mimic", "Founder: a new way")]
    monkeypatch.setattr(decide.roster_module, "load_roster", lambda: league)
    monkeypatch.setattr(decide.lines_module, "load_lines", lambda: LINES)
    monkeypatch.setattr(decide, "load_opponents", lambda: {})
    monkeypatch.setattr(decide, "main_go_lines", lambda names: {})
    calls: list[tuple[str, str, list[str]]] = []
    ratings = {"cand": 2110, "found": 1950, "champ": 2100, "mimic": 1800}
    pairs = {("cand", "champ"): (31, 60), ("found", "champ"): (25, 60)}

    def run(players: list[str], maps: str, run_id: str, focus: list[str] | None = None, **settings: object) -> dict:
        calls.append((run_id, maps, sorted(players)))
        table = compared(30, 10, 0.01)
        return summary(ratings, pairs, paired={"cand": table}, compare={"cand": {"champ": table}})

    monkeypatch.setattr(decide, "_run", run)
    selection = decide.play_selection(None, "iteration-40-decide")
    assert [decision.decision for decision in selection.decisions] == ["promoted", "admitted"]
    assert [run_id for run_id, _, _ in calls] == [
        "iteration-40-decide-parents",
        "iteration-40-decide-found-champion",
        "iteration-40-decide-select",
        "iteration-40-decide-select-holdout",
        "iteration-40-decide-select-all",
    ]
    # The selection's field is the population with the candidates added; the holdout run plays the fix alone.
    assert {"cand", "found", "champ", "fixed", "level3"} <= set(calls[2][2])
    assert "found" not in calls[3][2] and calls[3][1] == "holdout"
    report = decide.report(selection, decide.upkeep(selection.decisions, LINES, league, Field(ratings), 40))
    assert "| `cand` | champ | Fix: x |" in report and "**promoted**" in report and "| `found` |" in report
    with pytest.raises(ValueError, match="not a candidate"):
        decide.play_selection(["champ"], "x")


def test_league_decide_without_candidates_prints_no_decisions_and_no_actions(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    selection = decide.Selection([], [], Evidence(), LINES, {bot.name: bot for bot in ROSTER}, [])
    monkeypatch.setattr(decide, "play_selection", lambda names, prefix: selection)
    monkeypatch.setattr(decide, "measurer", lambda outside, prefix: Field(RATINGS))
    applied: list[decide.Upkeep] = []
    monkeypatch.setattr(decide, "apply", applied.append)
    assert cli.main(["decide", "--iteration", "40"]) == 0
    out = capsys.readouterr().out
    assert "No candidates to decide." in out and "No actions." in out and "| `main` |" in out
    assert not applied
    assert cli.main(["decide", "--json", "--apply"]) == 0
    assert '"decisions": []' in capsys.readouterr().out and len(applied) == 1


def test_apply_writes_the_champion_before_deleting_its_parent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    done: list[str] = []
    monkeypatch.setattr(decide, "HOSTED", tmp_path / "bot")
    monkeypatch.setattr(decide.roster_module, "set_status", lambda name, status: done.append(f"{name} {status}"))
    monkeypatch.setattr(decide.roster_module, "delete_bot", lambda name: done.append(f"delete {name}"))
    monkeypatch.setattr(decide.lines_module, "write_lines", lambda written: done.append("lines"))
    new = Lines(champion="cand", lines=[Line("main", "m", "main", "cand", ["cand"])])
    actions = [decide.Action("status", "cand", "promoted", "active"), decide.Action("delete", "champ", "alike")]
    decide.apply(decide.Upkeep(actions, new, champion_changed=True))
    assert (tmp_path / "bot").read_text() == "cand\n" and done == ["cand active", "delete champ", "lines"]


def test_a_margins_words_are_the_tables() -> None:
    margin = decide._margin(compared(5, 2, 0.2, {"a": 2, "b": 1, "c": 0, "d": -1}))
    assert (margin.margin, margin.maps_better, margin.maps_worse, margin.word) == (3, 2, 1, "confirmed")
    assert margin.word == tournament.reading(3, 0.2)
