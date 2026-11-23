"""Small groups sent one after another at one castle, each lost alone, where together they would have taken it.

The lessons it comes from: "Trickles lose to stacks" (a real game on `claw`:
groups of 9 to 21 from two castles at the same castle arrived one at a time
and each lost alone), "Staging alone doesn't help" and the strike that
lands every castle's group together (iteration 7's `frontline`).

A failed landing is a group that reached its target (no clash destroyed it
on the way), was no bigger than what the target held on the board of its
landing turn (it couldn't have taken it alone), and left it still not its
team's on the next board. A trickle
is at least ``GROUPS`` failed landings of one team at one castle that wasn't
the team's when they left, on at least two different turns within
``WINDOW`` turns of the first, whose soldiers together (as each was last
seen walking, after any clash on the way) exceed what the target held on
the board of the first landing's turn plus what it produced until the last
one's. The target must not change hands in that window: a
race for a castle that someone takes is not a trickle. One flag per
trickle.

Cost: the soldiers the trickle's groups landed with.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from league_tools.detectors import Flag, _board

KIND = "trickled_attack"

GROUPS = 3
WINDOW = 8


def detect(demo: dict[str, Any]) -> list[Flag]:
    """Every trickle of failed groups at one castle that together would have taken it."""
    names = _board.team_names(demo)
    frames = demo["frames"]
    failed: dict[tuple[int, int], list[_board.Group]] = defaultdict(list)
    for group in _board.groups(demo):
        if group.ended is None or group.destroyed or group.target_team == group.team:
            continue
        held = next(castle for castle in frames[group.ended - 1]["castles"] if castle["id"] == group.target["id"])
        if group.last > held["soldiers"]:
            continue
        failed[(group.team, group.target["id"])].append(group)
    changed = {(capture.castle, capture.turn) for capture in _board.captures(demo)}
    flags = []
    for (team, target), trickle in sorted(failed.items()):
        trickle.sort(key=lambda group: (group.ended or 0, group.id))
        start = 0
        while start < len(trickle):
            first = trickle[start]
            first_end = first.ended or 0
            batch = [group for group in trickle[start:] if (group.ended or 0) - first_end <= WINDOW]
            start += len(batch)
            batch = [group for group in batch if not group.took]
            if team not in names or len(batch) < GROUPS:
                continue
            last_end = max(group.ended or 0 for group in batch)
            if len({group.ended for group in batch}) < 2:
                continue
            if any((target, turn) in changed for turn in range(first_end, last_end + 1)):
                continue
            castle = next(castle for castle in frames[first_end - 1]["castles"] if castle["id"] == target)
            grows = _board.production(castle) * (last_end - first_end) if castle["team_color"] else 0
            needed = castle["soldiers"] + grows
            total = sum(group.last for group in batch)
            if total <= needed:
                continue
            sizes = ", ".join(f"{group.last} on {group.ended}" for group in batch)
            flags.append(
                Flag(
                    team,
                    names[team],
                    KIND,
                    (min(group.sent for group in batch), last_end),
                    f"{len(batch)} groups at castle {target} each landed and lost alone ({sizes}): {total} "
                    f"soldiers against {castle['soldiers']} held on turn {first_end} and {grows} grown until turn "
                    f"{last_end}",
                    float(total),
                )
            )
    return flags
