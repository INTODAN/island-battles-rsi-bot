"""The selection and the population's rules as code: what ``league decide`` prints and applies.

The rules are the ``league-evidence`` and ``league-population`` skills'; this
module applies them to the tables of the selection's tournaments, and decides
nothing those skills leave to judgment: such a case comes back as
``needs_review``, with its reason, for an agent or a person.

Two parts, each pure:

- ``decide``: each candidate's decision (promoted, admitted, rejected,
  unresolved, superseded), the rule that decided it and its numbers, from the
  summaries of the runs the ``bot-league-iteration`` skill plays. A candidate
  whose rule needs a run that isn't there yet comes back ``pending``, naming
  the run, so the caller plays it and asks again.
- ``upkeep``: the population's upkeep after the decisions: the bots that play
  alike, the side lines' counts and closures, the caps, the main line's change
  and the new head and champion, as a list of actions and the lines after them.
  It measures the population through a callable, so the caller plays (or reads
  from the cache) what the rules need.

``play_selection`` and ``apply`` are the rest of ``league decide``: they play
the tournaments and change the roster and the lines file.
"""

from __future__ import annotations

import copy
import itertools
import json
from collections.abc import Callable, Collection, Mapping
from dataclasses import asdict, dataclass, field, replace
from typing import Any

from . import lines as lines_module
from . import roster as roster_module
from . import tournament
from .lines import Line, Lines, kind_of, line_of
from .opponents import load_opponents
from .paths import BOTS, RUNS
from .roster import HOSTED, Bot

# The caps of the population (the ``league-population`` skill). The cap of
# side lines rises to four once runs are parallel (docs/parallel-iterations.md).
MAX_SIDE_LINES = 4
MAX_ACTIVE_IN_LINE = 3
MAX_FIXED_OPPONENTS = 8
# The gate: a candidate's slowest turn must stay under this.
SLOWEST_TURN_MILLISECONDS = 200.0
# A fix or a graft is rejected with more than this many points fewer than its
# parent against the references.
REFERENCES_SLACK = 3.0
# Rounds of "measure, then one of each pair that plays alike leaves" before
# giving up: each round removes a bot, so the population runs out long before.
ALIKE_ROUNDS = 30

Summary = dict[str, Any]
# (population, maps) -> the summary of a whole round robin of those bots, the
# default bots and the outside opponents, on "train" or "holdout".
Measure = Callable[[list[str], str], Summary]

DECISIONS = ("promoted", "admitted", "rejected", "unresolved", "superseded", "needs_review", "pending")
RUNS_NEEDED = ("head_to_head", "champion", "train", "holdout", "all")


@dataclass(frozen=True)
class Candidate:
    """A candidate as the rules see it."""

    name: str
    # fix, graft, simplification, founder or exploiter: the first word of its idea; None when it has none.
    kind: str | None
    parent: str
    # Its line's name: a founder's own, None for an exploiter.
    line: str | None
    idea: str = ""
    # Its line's head when it was written. When that was its parent and the
    # head has moved since, it is judged against the head too.
    base_head: str | None = None


@dataclass(frozen=True)
class Evidence:
    """The summaries of the selection's runs (``tournament.summarize``, as ``tournament.run`` returns them).

    The tables of games next to another bot's are read from a summary's
    ``compared`` (candidate, then the bot it is set next to, then what
    ``tournament.paired`` returned), and for its parent from ``paired`` too.

    Attributes:
        head_to_head: The candidates against their parents (and heads) alone: ``--focus C --parents``.
        champion: Founders and exploiters against the champion alone; pairs from each one's run together.
        train: The whole population with the candidates added, on the training maps: ``--add C``.
        holdout: The same on the holdout maps: ``--maps holdout --add C``. Only its tables are read.
        all: The same on all maps: ``--maps all --add C``.
    """

    head_to_head: Summary | None = None
    champion: Summary | None = None
    train: Summary | None = None
    holdout: Summary | None = None
    all: Summary | None = None


@dataclass(frozen=True)
class Margin:
    """A candidate's games against the others next to another bot's (``tournament.paired``), in the rules' words."""

    better: int
    worse: int
    same: int
    maps_better: int
    maps_worse: int
    luck: float

    @property
    def margin(self) -> int:
        """Better minus worse."""
        return self.better - self.worse

    @property
    def word(self) -> str:
        """What it comes to: clear, confirmed, nothing, worse or clearly worse."""
        return tournament.reading(self.margin, self.luck)

    def text(self) -> str:
        """As the ledger writes it."""
        return (
            f"{self.better}, {self.worse} ({self.margin:+d}; {self.maps_better} maps better, {self.maps_worse} worse; "
            f"{tournament.chance(self.luck)}): {self.word}"
        )


@dataclass(frozen=True)
class Numbers:
    """What the rules read of a candidate, against one bot (its parent, its line's head or the champion)."""

    against: str
    # Head-to-head points and games against ``against``.
    points: tuple[float, float] | None = None
    # Training ratings: the candidate's and ``against``'s.
    rating: tuple[int, int | None] | None = None
    train: Margin | None = None
    holdout: Margin | None = None
    all: Margin | None = None
    # Points against the references: the candidate's and ``against``'s.
    references: tuple[float, float] | None = None
    # Lines of main.go: the candidate's and ``against``'s.
    main_go: tuple[int, int] | None = None
    # The bots of the league it plays alike, from the training table.
    alike: tuple[str, ...] = ()


@dataclass(frozen=True)
class Decision:
    """One candidate's decision, the rule that decided it, and its numbers."""

    candidate: Candidate
    # One of DECISIONS.
    decision: str
    rule: str
    numbers: Numbers
    # When it was judged against its line's head too: the numbers against its own parent.
    parent_numbers: Numbers | None = None
    # With ``pending``: the run it waits for, one of RUNS_NEEDED.
    needs: str | None = None


@dataclass(frozen=True)
class Action:
    """One change of the population.

    ``kind`` is ``status`` (set ``bot``'s status to ``status``), ``delete``
    (delete ``bot``), ``champion`` (``bot`` is the new champion) or
    ``needs_review`` (nothing is changed: an agent or a person decides).
    """

    kind: str
    bot: str
    reason: str
    status: str | None = None


@dataclass
class Upkeep:
    """What the population's rules do after the decisions."""

    actions: list[Action]
    lines: Lines
    # The last training summary measured: the population as it is after the actions.
    final: Summary | None = None
    # Whether the champion is another bot now (``lines.champion``).
    champion_changed: bool = False

    @property
    def reviews(self) -> list[Action]:
        """The cases the rules leave to judgment."""
        return [action for action in self.actions if action.kind == "needs_review"]


# --- Reading the summaries ---------------------------------------------------


def _pair_points(summary: Summary | None, name: str, opponent: str) -> tuple[float, float] | None:
    if summary is None:
        return None
    points = summary.get("pairs", {}).get(name, {}).get(opponent)
    return None if points is None else (float(points[0]), float(points[1]))


def _ratings(summary: Summary | None) -> dict[str, int]:
    return {row["player"]: row["rating"] for row in (summary or {}).get("standings", [])}


def _standing(summary: Summary | None, name: str) -> dict[str, Any] | None:
    return next((row for row in (summary or {}).get("standings", []) if row["player"] == name), None)


def _margin(compared: Mapping[str, Any]) -> Margin:
    maps = list(compared["maps"].values())
    return Margin(
        better=compared["better"],
        worse=compared["worse"],
        same=compared["same"],
        maps_better=sum(margin > 0 for margin in maps),
        maps_worse=sum(margin < 0 for margin in maps),
        luck=compared["luck"],
    )


def _compared(summary: Summary | None, candidate: Candidate, against: str) -> Margin | None:
    """The candidate's games next to ``against``'s in a summary, or None when it has none."""
    if summary is None:
        return None
    found = summary.get("compared", {}).get(candidate.name, {}).get(against)
    if found is None and against == candidate.parent:
        found = summary.get("paired", {}).get(candidate.name)
    return None if found is None else _margin(found)


def references_points(summary: Summary, name: str, references: Collection[str], leave_out: str) -> float:
    """A bot's points against the references, from the pair table, ``leave_out`` left out."""
    row = summary.get("pairs", {}).get(name, {})
    return sum(float(row[reference][0]) for reference in references if reference != leave_out and reference in row)


def _gate(summary: Summary | None, name: str, run: str) -> str | None:
    """Why the candidate fails the gate in a run, or None."""
    row = _standing(summary, name)
    if row is None:
        return None
    if row["failed_turns"]:
        return (
            f"{row['failed_turns']} failed turns in the {run} run: fix it or drop it, or play the run again if a "
            "turn ran out of time while the machine was busy"
        )
    if row["slowest_turn_milliseconds"] >= SLOWEST_TURN_MILLISECONDS:
        return (
            f"its slowest turn in the {run} run took {row['slowest_turn_milliseconds']:.1f} ms, not under "
            f"{SLOWEST_TURN_MILLISECONDS:g}: fix it or drop it"
        )
    return None


def _share(points: tuple[float, float]) -> str:
    return f"{points[0]:g}/{points[1]:g}"


# --- The rules for each kind -------------------------------------------------


def _change(
    candidate: Candidate,
    against: str,
    evidence: Evidence,
    references: Collection[str],
    main_go: Mapping[str, int],
) -> tuple[str, str, Numbers, str | None]:
    """A fix, a graft or a simplification against one bot: (decision, rule, numbers, run needed).

    The three steps of ``league-evidence``: the head-to-head, the training
    maps, then the holdout maps and all maps together.
    """
    numbers = Numbers(against=against)
    simplification = candidate.kind == "simplification"
    if simplification:
        if candidate.name not in main_go or against not in main_go:
            return "needs_review", f"no main.go to count for {candidate.name} or {against}", numbers, None
        numbers = replace(numbers, main_go=(main_go[candidate.name], main_go[against]))
    points = _pair_points(evidence.head_to_head, candidate.name, against)
    if points is None:
        return "pending", f"its head-to-head against {against} is not played", numbers, "head_to_head"
    numbers = replace(numbers, points=points)
    failed = _gate(evidence.head_to_head, candidate.name, "head-to-head")
    if failed:
        return "needs_review", failed, numbers, None
    if points[0] * 3 <= points[1]:
        return "rejected", f"a third of the points or fewer against {against} ({_share(points)})", numbers, None
    if numbers.main_go is not None and numbers.main_go[0] >= numbers.main_go[1]:
        lines = numbers.main_go
        return "rejected", f"its main.go is not shorter than {against}'s ({lines[0]} lines, {lines[1]})", numbers, None

    ratings = _ratings(evidence.train)
    if candidate.name not in ratings:
        return "pending", "the training maps are not played", numbers, "train"
    numbers = replace(numbers, rating=(ratings[candidate.name], ratings.get(against)))
    failed = _gate(evidence.train, candidate.name, "training")
    if failed:
        return "needs_review", failed, numbers, None
    train = _compared(evidence.train, candidate, against)
    if train is None:
        return "needs_review", f"the training table has no games of it next to {against}'s", numbers, None
    numbers = replace(numbers, train=train)
    assert evidence.train is not None
    mine = references_points(evidence.train, candidate.name, references, against)
    theirs = references_points(evidence.train, against, references, against)
    numbers = replace(numbers, references=(mine, theirs))
    if train.word == "clearly worse":
        return "rejected", f"clearly worse than {against} on the training maps", numbers, None
    if not simplification and mine < theirs - REFERENCES_SLACK:
        return (
            "rejected",
            f"over {REFERENCES_SLACK:g} points fewer than {against} against the references ({mine:g} to {theirs:g})",
            numbers,
            None,
        )

    holdout = _compared(evidence.holdout, candidate, against)
    if holdout is None:
        return "pending", "the holdout maps are not played", numbers, "holdout"
    numbers = replace(numbers, holdout=holdout)
    every = _compared(evidence.all, candidate, against)
    if every is None:
        return "pending", "all maps together are not played", numbers, "all"
    numbers = replace(numbers, all=every)
    if simplification:
        if every.word == "clearly worse":
            return "rejected", f"clearly worse than {against} on all maps together", numbers, None
        return "promoted", f"not clearly worse than {against}, and its main.go is shorter", numbers, None
    if holdout.word in ("confirmed", "clear") and every.word == "clear":
        return "promoted", f"confirmed on the holdout maps and clear on all maps against {against}", numbers, None
    missed = []
    if holdout.word not in ("confirmed", "clear"):
        missed.append(f"{holdout.word} on the holdout maps")
    if every.word != "clear":
        missed.append(f"{every.word} on all maps")
    short = " and ".join(missed)
    if every.margin > 0:
        return "unresolved", f"a margin above 0 on all maps, short of the rule: {short}", numbers, None
    return "rejected", f"{short} against {against}", numbers, None


def _new_strategy(
    candidate: Candidate,
    champion: str,
    evidence: Evidence,
    candidates: Collection[str],
    references: Collection[str],
) -> tuple[str, str, Numbers, str | None]:
    """A founder or an exploiter, by its points against the champion and the training maps."""
    numbers = Numbers(against=champion)
    points = _pair_points(evidence.champion, candidate.name, champion)
    if points is None:
        return "pending", f"its run against the champion {champion} is not played", numbers, "champion"
    numbers = replace(numbers, points=points)
    failed = _gate(evidence.champion, candidate.name, "champion's")
    if failed:
        return "needs_review", failed, numbers, None
    founder = candidate.kind == "founder"
    if founder and points[0] * 3 < points[1]:
        return "rejected", f"under a third of the points from the champion ({_share(points)})", numbers, None
    if not founder and points[0] * 5 < points[1] * 3:
        return "rejected", f"under three fifths of the points from the champion ({_share(points)})", numbers, None
    ratings = _ratings(evidence.train)
    if candidate.name not in ratings:
        return "pending", "the training maps are not played", numbers, "train"
    assert evidence.train is not None
    numbers = replace(
        numbers,
        rating=(ratings[candidate.name], ratings.get(champion)),
        references=(
            references_points(evidence.train, candidate.name, references, ""),
            references_points(evidence.train, champion, references, ""),
        ),
    )
    failed = _gate(evidence.train, candidate.name, "training")
    if failed:
        return "needs_review", failed, numbers, None
    if not founder:
        return "admitted", f"three fifths of the points or more from the champion ({_share(points)})", numbers, None
    alike = tuple(
        other
        for pair in evidence.train.get("alike", [])
        if candidate.name in pair["bots"]
        for other in pair["bots"]
        if other != candidate.name and other not in candidates
    )
    numbers = replace(numbers, alike=alike)
    if alike:
        return "rejected", f"plays alike a bot of the league: {', '.join(alike)}", numbers, None
    return (
        "admitted",
        f"a third of the points or more from the champion ({_share(points)}), and plays alike no bot of the league",
        numbers,
        None,
    )


def decide(
    candidates: list[Candidate],
    evidence: Evidence,
    lines: Lines,
    bots: Collection[str],
    references: Collection[str],
    main_go: Mapping[str, int],
    max_side_lines: int = MAX_SIDE_LINES,
) -> list[Decision]:
    """Each candidate's decision by the ``league-evidence`` skill's rule for its kind.

    A fix, a graft or a simplification is judged against its parent. When its
    parent was its line's head when it was written (``base_head``) and the head
    has moved since, it is judged against the head too: promoted only when it
    passes against both, and ``superseded`` when it passes against its parent
    alone. When its parent has left the league, it is judged against the head
    alone. A founder and an exploiter are judged by their points against the
    champion; founders take the free side places in the candidates' order.

    Args:
        candidates: The candidates, in the order their places are filled.
        evidence: The summaries of the runs played so far.
        lines: The lines as they are now: each line's head and the champion.
        bots: Every bot of the league now, the candidates too.
        references: The sparring bots and the outside opponents.
        main_go: The lines of each bot's main.go, for simplifications.
        max_side_lines: The cap of side lines.

    Returns:
        A decision for each candidate, in their order. ``pending`` names the
        run it waits for: play it, and decide again.
    """
    names = {candidate.name for candidate in candidates}
    free = max_side_lines - len(lines.side)
    decisions = []
    for candidate in candidates:
        decision = _decide_one(candidate, evidence, lines, bots, names, references, main_go)
        if decision.candidate.kind == "founder" and decision.decision == "admitted":
            if free <= 0:
                decision = replace(
                    decision,
                    decision="needs_review",
                    rule=f"{decision.rule}; but no side place is free (at most {max_side_lines} side lines): the "
                    "design keeps it waiting for the next free place, which is not built yet",
                )
            free -= 1
        decisions.append(decision)
    return decisions


def _decide_one(
    candidate: Candidate,
    evidence: Evidence,
    lines: Lines,
    bots: Collection[str],
    candidates: Collection[str],
    references: Collection[str],
    main_go: Mapping[str, int],
) -> Decision:
    if candidate.kind not in lines_module.KINDS:
        return Decision(
            candidate,
            "needs_review",
            "its idea doesn't begin with its kind "
            "(Fix:, Graft from NAME:, Simplification:, Founder:, Exploiter of NAME:)",
            Numbers(against=candidate.parent),
        )
    if candidate.kind in ("founder", "exploiter"):
        decision, rule, numbers, needs = _new_strategy(candidate, lines.champion, evidence, candidates, references)
        return Decision(candidate, decision, rule, numbers, needs=needs)
    line = lines.get(candidate.line)
    if line is None or line.state == "closed":
        return Decision(
            candidate,
            "needs_review",
            f"a {candidate.kind} in no open line (its parent {candidate.parent} is in {candidate.line or 'none'})",
            Numbers(against=candidate.parent),
        )
    head = line.head
    if candidate.parent not in bots:
        if not head or head not in bots:
            return Decision(
                candidate, "needs_review", "neither its parent nor its line's head is in the league", Numbers("")
            )
        decision, rule, numbers, needs = _change(candidate, head, evidence, references, main_go)
        if decision != "pending":
            rule = f"judged against its line's head {head}, its parent {candidate.parent} having left: {rule}"
        return Decision(candidate, decision, rule, numbers, needs=needs)
    decision, rule, numbers, needs = _change(candidate, candidate.parent, evidence, references, main_go)
    moved = candidate.base_head == candidate.parent and head and head != candidate.parent and head in bots
    if decision != "promoted" or not moved:
        return Decision(candidate, decision, rule, numbers, needs=needs)
    against_head, head_rule, head_numbers, needs = _change(candidate, head, evidence, references, main_go)
    if against_head == "promoted":
        rule = f"{rule}; and against its line's head {head}, which its parent no longer is: {head_rule}"
        return Decision(candidate, "promoted", rule, head_numbers, parent_numbers=numbers)
    if against_head in ("pending", "needs_review"):
        return Decision(candidate, against_head, head_rule, head_numbers, parent_numbers=numbers, needs=needs)
    rule = f"passes against its parent {candidate.parent}, not against its line's head {head}: {head_rule}"
    return Decision(candidate, "superseded", rule, head_numbers, parent_numbers=numbers)


# --- The population's upkeep -------------------------------------------------


@dataclass
class _State:
    """The population as the upkeep changes it."""

    status: dict[str, str]
    parent: dict[str, str]
    lines: Lines
    actions: list[Action] = field(default_factory=list)
    champion_changed: bool = False

    def present(self, name: str) -> bool:
        return name in self.status

    def set_status(self, name: str, status: str, reason: str) -> None:
        if self.status.get(name) != status:
            self.status[name] = status
            self.actions.append(Action("status", name, reason, status))

    def delete(self, name: str, reason: str) -> None:
        if name in self.status:
            del self.status[name]
            self.actions.append(Action("delete", name, reason))
            for line in self.lines.lines:
                if name in line.bots:
                    line.bots.remove(name)

    def review(self, name: str, reason: str) -> None:
        action = Action("needs_review", name, reason)
        if action not in self.actions:
            self.actions.append(action)

    def deletions(self) -> int:
        return sum(action.kind == "delete" for action in self.actions)

    def population(self) -> list[str]:
        return sorted(name for name, status in self.status.items() if status != "candidate")

    def active(self, line: Line) -> list[str]:
        return [name for name in line.bots if self.status.get(name) == "active"]

    def make_head(self, line: Line, name: str, reason: str) -> None:
        if line.head == name:
            return
        line.head = name
        if line.state == "main":
            self.lines.champion = name
            self.champion_changed = True
            self.actions.append(Action("champion", name, reason))


def _apply_decisions(state: _State, decisions: list[Decision], ratings: Mapping[str, int], iteration: int) -> None:
    """Statuses of the decided candidates, new lines, and the heads that promotions moved."""
    heads = {line.name: line.head for line in state.lines.lines}
    from_head: dict[str, list[str]] = {}
    for decision in decisions:
        candidate = decision.candidate
        name = candidate.name
        if decision.decision == "promoted":
            state.set_status(name, "active", f"promoted: {decision.rule}")
            line = state.lines.get(candidate.line)
            if line is not None:
                if name not in line.bots:
                    line.bots.append(name)
                if decision.numbers.against == heads[line.name] or candidate.parent == heads[line.name]:
                    from_head.setdefault(line.name, []).append(name)
        elif decision.decision == "admitted" and candidate.kind == "founder":
            state.set_status(name, "active", f"admitted: {decision.rule}; the first bot of a side line")
            strategy = candidate.idea.split(":", 1)[1].strip() if ":" in candidate.idea else candidate.idea
            state.lines.lines.append(
                Line(
                    name=name,
                    strategy=strategy,
                    state="side",
                    head=name,
                    bots=[name],
                    note=f"admitted in iteration {iteration}",
                )
            )
        elif decision.decision == "admitted":
            state.set_status(name, "retired", f"admitted: {decision.rule}; a fixed opponent")
        elif decision.decision in ("rejected", "unresolved", "superseded"):
            state.delete(name, f"{decision.decision}: {decision.rule}")
        else:
            state.review(name, f"left a candidate, {decision.decision}: {decision.rule}")
    for line_name, promoted in from_head.items():
        line = state.lines.get(line_name)
        assert line is not None
        best = max(promoted, key=lambda name: (ratings.get(name, -(10**9)), name))
        reason = f"promoted from the head {heads[line_name]} of `{line_name}`"
        if len(promoted) > 1:
            reason += f"; of {', '.join(promoted)}, all promoted from it, the highest-rated on the training maps"
        state.make_head(line, best, reason)
    for decision in decisions:
        line = state.lines.get(decision.candidate.line)
        if decision.decision != "promoted" or line is None or decision.candidate.name == line.head:
            continue
        rating, head_rating = ratings.get(decision.candidate.name), ratings.get(line.head)
        if rating is not None and head_rating is not None and rating > head_rating:
            state.review(
                decision.candidate.name,
                f"promoted from {decision.candidate.parent}, not from the head, and rates above the head {line.head} "
                f"({rating} to {head_rating}): a head is its line's top-rated active bot, except a bot promoted from "
                "the head; say which is the head",
            )


def _leaver(
    state: _State, pair: list[str], summary: Summary, never: Collection[str], promoted: Collection[str]
) -> tuple[str | None, str]:
    """Which of a pair that plays alike leaves, and why; None when neither does."""
    first, second = pair
    keep = [name in never or state.status.get(name) == "sparring" for name in pair]
    if all(keep):
        return None, "both never leave"
    if keep[0] or keep[1]:
        stays, leaves = (first, second) if keep[0] else (second, first)
        return leaves, f"plays alike {stays}, which never leaves"
    for child, parent in ((first, second), (second, first)):
        if child in promoted and state.parent.get(child) == parent:
            return parent, f"plays alike {child}, its child promoted in this iteration, which replaces it"
    champion = state.lines.champion
    taken = {name: (_pair_points(summary, name, champion) or (0.0, 0.0))[0] for name in pair}
    ratings = _ratings(summary)
    if taken[first] != taken[second]:
        low, high = (first, second) if taken[first] < taken[second] else (second, first)
        return low, f"plays alike {high}, and takes fewer points from the champion ({taken[low]:g} to {taken[high]:g})"
    if ratings.get(first) != ratings.get(second):
        low, high = sorted(pair, key=lambda name: ratings.get(name, -(10**9)))
        return low, f"plays alike {high}, takes as many points from the champion ({taken[low]:g}), and rates lower"
    return None, "takes as many points from the champion as the other, and rates the same"


def _leave(state: _State, name: str, reason: str, summary: Summary, replaced_by: str | None) -> None:
    """A bot leaves for playing alike another; its line's head moves, or the line closes."""
    line = state.lines.listed(name)
    state.delete(name, reason)
    if line is None or line.head != name:
        return
    if replaced_by is not None and replaced_by in line.bots:
        state.make_head(line, replaced_by, f"replaces its parent {name}, the head of `{line.name}`")
        return
    ratings = _ratings(summary)
    active = sorted(state.active(line), key=lambda bot: -ratings.get(bot, -(10**9)))
    if active:
        state.make_head(line, active[0], f"the top-rated active bot of `{line.name}` once its head {name} left")
        return
    if line.state == "main":
        state.review(line.name, f"the main line's head {name} left and no active bot of the line is left")
        return
    line.head = ""
    line.state = "closed"
    line.note = f"closed: its last active bot {name} left for playing alike another"


def _alike(state: _State, measure: Measure, never_extra: Collection[str], promoted: Collection[str]) -> Summary | None:
    """One of each pair that plays alike leaves, measured again after each round, until no pair is left to clear."""
    summary = None
    for _ in range(ALIKE_ROUNDS):
        summary = measure(state.population(), "train")
        left = False
        for pair in summary.get("alike", []):
            names = list(pair["bots"])
            if not all(state.present(name) or name in never_extra for name in names):
                continue
            never = {state.lines.champion, *never_extra}
            leaves, reason = _leaver(state, names, summary, never, promoted)
            if leaves is None:
                if reason != "both never leave":
                    state.review(" and ".join(names), f"play alike, and the rule can't say who leaves: {reason}")
                continue
            other = names[1] if leaves == names[0] else names[0]
            replaced_by = other if other in promoted and state.parent.get(other) == leaves else None
            _leave(state, leaves, reason, summary, replaced_by)
            left = True
        if not left:
            return summary
    return summary


def _side_lines(state: _State, decisions: list[Decision], new_lines: Collection[str], iteration: int) -> None:
    """Each line's count of iterations of work without a promotion; a side line at two is closed."""
    for line in state.lines.lines:
        if line.state == "closed" or line.name in new_lines:
            continue
        worked = [
            decision
            for decision in decisions
            if decision.candidate.line == line.name
            and decision.candidate.kind not in ("founder", "exploiter")
            and decision.decision not in ("pending", "needs_review")
        ]
        if not worked:
            continue
        if any(decision.decision == "promoted" for decision in worked):
            line.without_promotion = 0
            continue
        line.without_promotion += 1
        if line.state != "side" or line.without_promotion < 2:
            continue
        reason = f"`{line.name}` is closed: two iterations of work in a row without a promotion (iteration {iteration})"
        if line.head and state.present(line.head):
            state.set_status(line.head, "retired", f"{reason}; its head becomes a fixed opponent")
        for bot in [bot for bot in line.bots if bot != line.head]:
            state.delete(bot, reason)
        line.state = "closed"
        line.note = f"closed in iteration {iteration}: two iterations of work in a row without a promotion"


def _caps(state: _State, summary: Summary | None, max_side_lines: int) -> None:
    """At most three active bots in a line, eight fixed opponents and ``max_side_lines`` side lines."""
    ratings = _ratings(summary)
    for line in state.lines.lines:
        while len(state.active(line)) > MAX_ACTIVE_IN_LINE:
            others = [bot for bot in state.active(line) if bot != line.head]
            lowest = min(others, key=lambda bot: (ratings.get(bot, -(10**9)), bot))
            state.set_status(
                lowest,
                "retired",
                f"over {MAX_ACTIVE_IN_LINE} active bots in `{line.name}`: its lowest-rated that is not the head",
            )
    while True:
        fixed = [name for name, status in state.status.items() if status == "retired"]
        if len(fixed) <= MAX_FIXED_OPPONENTS:
            break
        active = [name for name, status in state.status.items() if status == "active"]
        taken = {
            name: sum((_pair_points(summary, name, bot) or (0.0, 0.0))[0] for bot in active) for name in sorted(fixed)
        }
        fewest = min(taken.values())
        lowest = [name for name, points in taken.items() if points == fewest]
        if len(lowest) > 1:
            state.review(
                ", ".join(lowest),
                f"over {MAX_FIXED_OPPONENTS} fixed opponents, and these take the fewest points from the active bots "
                f"alike ({fewest:g}): say which leaves",
            )
            break
        state.delete(
            lowest[0],
            f"over {MAX_FIXED_OPPONENTS} fixed opponents: takes the fewest points from the active bots ({fewest:g})",
        )
    if len(state.lines.side) > max_side_lines:
        state.review(
            ", ".join(line.name for line in state.lines.side),
            f"{len(state.lines.side)} side lines, over the cap of {max_side_lines}: the rules don't say which closes",
        )


def _main_line(state: _State, summary: Summary | None, measure: Measure, iteration: int, max_side_lines: int) -> None:
    """The main line changes when a side line's head beats the champion by the rule of ``league-evidence``."""
    champion = state.lines.champion
    ratings = _ratings(summary)
    if champion not in ratings:
        return
    leaders = []
    for line in state.lines.side:
        head = line.head
        points = _pair_points(summary, head, champion)
        if not head or head not in ratings or points is None:
            continue
        if ratings[head] > ratings[champion] and points[0] * 2 >= points[1]:
            leaders.append(line)
    if not leaders:
        return
    holdout = _ratings(measure(state.population(), "holdout"))
    leaders = [line for line in leaders if holdout.get(line.head, -(10**9)) >= holdout.get(champion, 10**9)]
    if len(leaders) > 1:
        state.review(
            ", ".join(line.head for line in leaders),
            "more than one side line's head passes the rule for the main line's change: say which",
        )
        return
    if not leaders:
        return
    new_main = leaders[0]
    old_main = state.lines.main
    old_main.state, old_main.without_promotion = "side", 0
    old_main.note = f"a side line since iteration {iteration}, when `{new_main.name}` passed it"
    new_main.state = "main"
    new_main.note = f"the main line since iteration {iteration}"
    state.lines.champion = new_main.head
    state.champion_changed = True
    state.actions.append(
        Action(
            "champion",
            new_main.head,
            f"the head of the side line `{new_main.name}` rates above {champion} on the training maps "
            f"({ratings[new_main.head]} to {ratings[champion]}), not below it on the holdout maps, and takes at least "
            "half the points from it: the main line changes",
        )
    )
    if len(state.lines.side) > max_side_lines:
        state.review(
            ", ".join(line.name for line in state.lines.side),
            f"{len(state.lines.side)} side lines once the main line changed, over the cap of {max_side_lines}: "
            "the rules don't say which closes",
        )


def upkeep(
    decisions: list[Decision],
    lines: Lines,
    roster: Collection[Bot],
    measure: Measure,
    iteration: int,
    train: Summary | None = None,
    outside: Collection[str] = (),
    max_side_lines: int = MAX_SIDE_LINES,
) -> Upkeep:
    """The population's upkeep after the decisions, by the ``league-population`` skill.

    In order: the decided candidates' statuses, the new lines and heads; the
    bots that play alike, measured again after each round until no pair is
    left that may be cleared; the side lines' counts and closures; the caps;
    the main line's change. Nothing is changed: the actions say what to change.

    Args:
        decisions: What ``decide`` returned.
        lines: The lines as they are now. They are not changed: the result holds new ones.
        roster: The league's bots, the candidates too.
        measure: Plays (or reads from the cache) a population's whole round robin.
        iteration: The iteration, for the lines' notes.
        train: The selection's training summary, whose ratings choose the head when two bots were promoted from it.
        outside: The outside opponents, which never leave.
        max_side_lines: The cap of side lines.
    """
    state = _State(
        status={bot.name: bot.status for bot in roster},
        parent={bot.name: bot.parent for bot in roster},
        lines=copy.deepcopy(lines),
    )
    _apply_decisions(state, decisions, _ratings(train), iteration)
    promoted = {decision.candidate.name for decision in decisions if decision.decision == "promoted"}
    new_lines = {
        decision.candidate.name
        for decision in decisions
        if decision.decision == "admitted" and decision.candidate.kind == "founder"
    }
    final = _alike(state, measure, outside, promoted)
    measured = state.deletions()
    _side_lines(state, decisions, new_lines, iteration)
    _caps(state, final, max_side_lines)
    # A closed line's bots or a fixed opponent that left change the field:
    # measure it again, and clear it of copies again, so the final table is
    # the population's as it now is.
    while state.deletions() > measured:
        final = _alike(state, measure, outside, promoted)
        measured = state.deletions()
        _caps(state, final, max_side_lines)
    _main_line(state, final, measure, iteration, max_side_lines)
    return Upkeep(actions=state.actions, lines=state.lines, final=final, champion_changed=state.champion_changed)


# --- Playing the selection, and applying it ----------------------------------

ANCHORS = ["level1", "level2", "level3"]


def candidate_of(bot: Bot, lines: Lines, roster: Mapping[str, Bot]) -> Candidate:
    """A candidate of the roster as the rules see it: its kind and line from its idea and parent.

    Its ``base_head`` is its line's head now, so a candidate decided in the
    iteration that wrote it is judged against its parent alone.
    """
    line = line_of(bot.name, lines, roster)
    found = lines.get(line)
    return Candidate(
        name=bot.name,
        kind=kind_of(bot.idea),
        parent=bot.parent,
        line=line,
        idea=bot.idea,
        base_head=found.head if found is not None and found.head else None,
    )


def main_go_lines(names: Collection[str]) -> dict[str, int]:
    """The lines of each bot's main.go."""
    counts = {}
    for name in names:
        path = BOTS / name / "main.go"
        if path.is_file():
            counts[name] = len(path.read_text(encoding="utf-8").splitlines())
    return counts


def opponents_of(candidate: Candidate, lines: Lines, bots: Collection[str]) -> list[str]:
    """The bots a candidate's games are set next to: its parent, and its line's head when it is judged against it."""
    if candidate.kind in ("founder", "exploiter"):
        return [lines.champion]
    found = lines.get(candidate.line)
    head = found.head if found is not None else ""
    against = [candidate.parent] if candidate.parent in bots else []
    moved = candidate.base_head == candidate.parent or candidate.parent not in bots
    if head and head in bots and head != candidate.parent and moved:
        against.append(head)
    return against


@dataclass
class Selection:
    """What ``play_selection`` found: the candidates, the decisions, and what they were decided on."""

    candidates: list[Candidate]
    decisions: list[Decision]
    evidence: Evidence
    lines: Lines
    roster: dict[str, Bot]
    outside: list[str]


def _merge(first: Summary | None, second: Summary) -> Summary:
    """Two focused runs' pairs and gate numbers as one."""
    if first is None:
        return second
    merged = copy.deepcopy(first)
    for name, row in second.get("pairs", {}).items():
        merged.setdefault("pairs", {}).setdefault(name, {}).update(row)
    rows = {row["player"]: row for row in merged.get("standings", [])}
    for row in second.get("standings", []):
        if row["player"] not in rows:
            merged.setdefault("standings", []).append(row)
            continue
        mine = rows[row["player"]]
        mine["failed_turns"] += row["failed_turns"]
        mine["slowest_turn_milliseconds"] = max(mine["slowest_turn_milliseconds"], row["slowest_turn_milliseconds"])
    return merged


def _run(
    players: list[str],
    maps: str,
    run_id: str,
    focus: list[str] | None = None,
    parents: dict[str, str] | None = None,
    parents_only: bool = False,
    compare: Mapping[str, list[str]] | None = None,
) -> Summary:
    """Play a tournament (from the cache where it can) and add ``compared``: each candidate next to other bots.

    ``compared`` is ``tournament.paired`` over the run's own results: the same
    table the run prints against a parent, set next to a line's head too. A
    holdout run's results are read for it as the run reads them for its own
    table: nothing of a game is printed.
    """
    focus = focus or []
    parents = parents or {}
    plan = tournament.Tournament(
        players=list(dict.fromkeys(players)),
        maps=tournament.map_files(maps),
        focus=focus,
        listed=focus + [name for name in parents if name not in focus],
        parents=parents,
        parents_only=parents_only,
    )
    summary, _ = tournament.run(plan, run_id)
    if compare:
        with (RUNS / run_id / "results.jsonl").open(encoding="utf-8") as file:
            results = [json.loads(line) for line in file]
        summary["compared"] = {
            name: {opponent: tournament.paired(results, name, opponent) for opponent in opponents}
            for name, opponents in compare.items()
        }
    return summary


def play_selection(names: list[str] | None, prefix: str, base_heads: Mapping[str, str] | None = None) -> Selection:
    """Play the runs the candidates' rules need, as the ``bot-league-iteration`` skill plays them, and decide.

    The head-to-heads first (``--focus C --parents``), each founder's and
    exploiter's run against the champion, then the training maps with the
    candidates still in (``--add``), then the holdout maps and all maps for the
    fixes, grafts and simplifications that went on. A run's matches come from
    the cache where they were played.

    Args:
        names: The candidates; every candidate of the roster when None.
        prefix: The run ids' prefix, such as ``iteration-40-decide``.
        base_heads: Each line's head when the candidates' run started (the integrator's): a
            candidate whose parent was its line's head then, and no longer is, is judged against the
            head too. Without it, the heads now: every candidate is judged against its parent alone.

    Raises:
        ValueError: A name is not a candidate of the roster.
    """
    roster = {bot.name: bot for bot in roster_module.load_roster()}
    lines = lines_module.load_lines()
    chosen = names if names is not None else [name for name, bot in roster.items() if bot.status == "candidate"]
    for name in chosen:
        if name not in roster or roster[name].status != "candidate":
            raise ValueError(f"{name!r} is not a candidate of the league")
    candidates = [candidate_of(roster[name], lines, roster) for name in chosen]
    if base_heads is not None:
        candidates = [replace(c, base_head=base_heads.get(c.line or "") or None) for c in candidates]
    outside = list(load_opponents())
    references = [name for name, bot in roster.items() if bot.status == "sparring"] + outside
    population = [name for name, bot in roster.items() if bot.status != "candidate"]
    main_go = main_go_lines(roster)
    against = {candidate.name: opponents_of(candidate, lines, roster) for candidate in candidates}
    evidence = Evidence()
    decisions: list[Decision] = []
    for _ in range(len(RUNS_NEEDED) + 1):
        decisions = decide(candidates, evidence, lines, roster, references, main_go)
        waiting: dict[str, list[Candidate]] = {}
        for decision in decisions:
            if decision.decision == "pending" and decision.needs:
                waiting.setdefault(decision.needs, []).append(decision.candidate)
        if not waiting:
            break
        for needs, group in waiting.items():
            evidence = _play_needed(needs, group, evidence, against, population, outside, prefix)
    return Selection(candidates, decisions, evidence, lines, roster, outside)


def _play_needed(
    needs: str,
    group: list[Candidate],
    evidence: Evidence,
    against: Mapping[str, list[str]],
    population: list[str],
    outside: list[str],
    prefix: str,
) -> Evidence:
    """Play the run that ``needs`` names for these candidates, and add it to the evidence."""
    names = [candidate.name for candidate in group]
    if needs == "head_to_head":
        summary = evidence.head_to_head
        for index in range(max(len(against[name]) for name in names)):
            parents = {name: against[name][index] for name in names if len(against[name]) > index}
            run_id = f"{prefix}-parents" if index == 0 else f"{prefix}-heads"
            players = [*parents, *parents.values()]
            summary = _merge(
                summary, _run(players, "train", run_id, focus=list(parents), parents=parents, parents_only=True)
            )
        return replace(evidence, head_to_head=summary)
    if needs == "champion":
        summary = evidence.champion
        for name in names:
            champion = against[name][0]
            summary = _merge(summary, _run([name, champion], "train", f"{prefix}-{name}-champion", focus=[name]))
        return replace(evidence, champion=summary)
    players = population + names + ANCHORS + outside
    parents = {candidate.name: candidate.parent for candidate in group if candidate.parent in population}
    compare = {name: [bot for bot in against[name] if bot in population] for name in names}
    if needs == "train":
        return replace(evidence, train=_run(players, "train", f"{prefix}-select", parents=parents, compare=compare))
    holdout = _run(players, "holdout", f"{prefix}-select-holdout", parents=parents, compare=compare)
    every = _run(players, "all", f"{prefix}-select-all", parents=parents, compare=compare)
    return replace(evidence, holdout=holdout, all=every)


def measurer(outside: list[str], prefix: str) -> Measure:
    """``upkeep``'s measure: a population's whole round robin with the default bots and the outside opponents."""
    rounds = itertools.count(1)

    def measure(population: list[str], maps: str) -> Summary:
        run_id = f"{prefix}-after-{next(rounds)}" if maps == "train" else f"{prefix}-after-{maps}"
        return _run(population + ANCHORS + outside, maps, run_id)

    return measure


def apply(result: Upkeep) -> None:
    """Make the upkeep's changes: the champion the hosted bot plays as, the statuses, the deletions, the lines."""
    if result.champion_changed:
        HOSTED.write_text(result.lines.champion + "\n", encoding="utf-8")
    for action in result.actions:
        if action.kind == "status" and action.status:
            roster_module.set_status(action.bot, action.status)
        elif action.kind == "delete":
            roster_module.delete_bot(action.bot)
    lines_module.write_lines(result.lines)


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def decisions_table(decisions: list[Decision]) -> list[str]:
    """The decisions as the ledger's candidate table (``| Candidate | Parent | Idea | ... | Decision |``)."""
    if not decisions:
        return []
    rows = [
        "| Candidate | Parent | Idea | Against parent | Training (parent's) | Better, worse on training (margin, maps, "
        "by luck) | Against the references (parent's) | Holdout | All maps | Decision |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for decision in decisions:
        candidate, numbers = decision.candidate, decision.numbers
        new_strategy = candidate.kind in ("founder", "exploiter")
        parent = candidate.parent
        if numbers.against and numbers.against != candidate.parent and not new_strategy:
            parent += f" (judged against {numbers.against})"
        points = "not played"
        if numbers.points is not None:
            points = _share(numbers.points)
            if new_strategy:
                points = f"against the champion: {points}"
            elif decision.parent_numbers is not None and decision.parent_numbers.points is not None:
                points = f"{_share(decision.parent_numbers.points)}; against {numbers.against}: {points}"
        rating = "not played"
        if numbers.rating is not None:
            mine, theirs = numbers.rating
            rating = f"{mine} ({theirs})" if theirs is not None else str(mine)
        references = "not played"
        if numbers.references is not None:
            references = f"{numbers.references[0]:g} ({numbers.references[1]:g})"
        train = numbers.train.text() if numbers.train else ("—" if new_strategy else "not played")
        cells = [
            f"`{candidate.name}`",
            parent,
            candidate.idea,
            points,
            rating,
            train,
            references,
            numbers.holdout.text() if numbers.holdout else "not played",
            numbers.all.text() if numbers.all else "not played",
            f"**{decision.decision}**: {decision.rule}",
        ]
        rows.append("| " + " | ".join(_cell(cell) for cell in cells) + " |")
    return rows


def actions_list(actions: list[Action]) -> list[str]:
    """The upkeep's actions, one line each."""
    out = []
    for action in actions:
        if action.kind == "status":
            out.append(f"- `{action.bot}` becomes {action.status}: {action.reason}")
        elif action.kind == "delete":
            out.append(f"- delete `{action.bot}`: {action.reason}")
        elif action.kind == "champion":
            out.append(f"- `{action.bot}` is the champion: {action.reason}")
        else:
            out.append(f"- NEEDS REVIEW: {action.bot}: {action.reason}")
    return out


def report(selection: Selection, result: Upkeep) -> str:
    """What ``league decide`` prints: the decisions, the actions, and the lines after them."""
    out = ["## Decisions", ""]
    out += decisions_table(selection.decisions) or ["No candidates to decide."]
    out += ["", "## The population's upkeep", ""]
    out += actions_list(result.actions) or ["No actions."]
    statuses = {name: bot.status for name, bot in selection.roster.items()}
    statuses |= {action.bot: action.status for action in result.actions if action.kind == "status" and action.status}
    out += ["", "## The lines after them", "", *lines_module.table(result.lines, statuses)]
    return "\n".join(out) + "\n"


def as_json(selection: Selection, result: Upkeep) -> str:
    """The decisions, the actions and the lines after them, for the integrator."""
    return json.dumps(
        {
            "decisions": [asdict(decision) for decision in selection.decisions],
            "actions": [asdict(action) for action in result.actions],
            "lines": asdict(result.lines),
            "champion": result.lines.champion,
            "champion_changed": result.champion_changed,
        },
        indent=1,
    )
