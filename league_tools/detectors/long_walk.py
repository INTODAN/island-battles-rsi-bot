"""Attacks that walked many turns, far beyond the board's usual distances, and took nothing.

The lessons it comes from: "Short lines beat long walks" and "A defender
that sees a long attack coming out-reinforces it" (a real game on `claw`:
the loser attacked castles 6 to 8.2 units away, 12 to 17 turns of walking,
and its 84 soldiers met 115), and "Speed pays for long attacks".

The board's step is the median, over the castles of the first board, of
each castle's distance to its nearest other castle. A long walk is a group
sent at a castle that wasn't its team's, whose walk takes at least
``TURNS`` turns at its speed and is at least ``STEPS`` steps long, and that
ended without its target being its team's on the next board. One team's
long walks at one castle whose sends are no more than ``GAP`` turns apart
make one flag, when they carried ``SOLDIERS`` soldiers or more together: a
single soldier sent far is a feint, not an attack. Its window is the first
of those walks, from its send to its end; its evidence counts them all.

Cost: the soldiers sent on those long walks.
"""

from __future__ import annotations

import statistics
from collections import defaultdict
from typing import Any

from league_tools.detectors import Flag, _board

KIND = "long_walk"

TURNS = 12
STEPS = 2.5
GAP = 10
SOLDIERS = 15


def step(demo: dict[str, Any]) -> float:
    """The board's step: the median distance from a castle to its nearest other castle."""
    castles = demo["frames"][0]["castles"]
    if len(castles) < 2:
        return 0.0
    return statistics.median(
        min(_board.distance(castle, other) for other in castles if other is not castle) for castle in castles
    )


def detect(demo: dict[str, Any]) -> list[Flag]:
    """Every run of failed long walks by one team at one castle."""
    names = _board.team_names(demo)
    unit = step(demo)
    walks: dict[tuple[int, int], list[_board.Group]] = defaultdict(list)
    for group in _board.groups(demo):
        if (
            group.team in names
            and group.target_team != group.team
            and group.ended is not None
            and not group.took
            and group.walk_turns >= TURNS
            and group.length >= STEPS * unit
        ):
            walks[(group.team, group.target["id"])].append(group)
    flags = []
    for (team, target), found in sorted(walks.items()):
        for first, last in _board.spans([group.sent for group in found], GAP):
            run = [group for group in found if first <= group.sent <= last]
            total = sum(group.soldiers for group in run)
            if total < SOLDIERS:
                continue
            longest = max(run, key=lambda group: group.walk_turns)
            flags.append(
                Flag(
                    team,
                    names[team],
                    KIND,
                    (first, run[0].ended or first),
                    f"{len(run)} groups, {total} soldiers, walked at castle {target} and took nothing; the longest "
                    f"{longest.length:.1f} units in {longest.walk_turns} turns at speed level {longest.speed_level}, "
                    f"where the board's step is {unit:.1f}",
                    float(total),
                )
            )
    return flags
