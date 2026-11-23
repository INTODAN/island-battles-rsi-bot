"""What the detectors read off a demo: sends, what became of each group, captures and each team's totals.

Turns are counted as ``digest`` counts them: the board of turn T is
``demo["frames"][T - 1]``, and what happened in turn T (its sends, clashes
and captures) is the difference between that board and the next one.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from league_tools import digest

# The speed of a group, in map units per turn, at each speed level.
SPEEDS = {1: 0.5, 2: 1.0, 3: 1.5, 4: 2.0}


def team_names(demo: dict[str, Any]) -> dict[int, str]:
    """Each team's colour and the name of the bot that played it."""
    return {team["color"]: team["name"] for team in demo["teams"]}


def winner(demo: dict[str, Any]) -> int | None:
    """The winning team's colour, or None for a draw or a game still running."""
    outcome = demo.get("outcome") or {}
    return outcome.get("winner_team_color") or None


def ran_to_limit(demo: dict[str, Any]) -> bool:
    """Whether the game ended at the turn limit rather than by an elimination."""
    return (demo.get("outcome") or {}).get("reason") == "generation_cap"


def last_turn(demo: dict[str, Any]) -> int:
    """The last turn whose board the demo holds."""
    return len(demo["frames"])


def distance(first: dict[str, Any], second: dict[str, Any]) -> float:
    """Two castles' (or a group's and a castle's) distance in map units."""
    return digest._distance(first, second)


def walk(length: float, speed_level: int) -> int:
    """The turns a group at that speed level takes to walk that far."""
    return max(1, math.ceil(length / SPEEDS.get(speed_level, 0.5) - 1e-9))


def production(castle: dict[str, Any]) -> int:
    """What a castle produces a turn."""
    return castle["upgrades"].get("generation_amount", 1)


@dataclass(frozen=True)
class Totals:
    """A team's castles, soldiers in castles, soldiers in groups and production on one board."""

    castles: int
    in_castles: int
    walking: int
    production: int

    @property
    def soldiers(self) -> int:
        """Every soldier the team has, standing or walking."""
        return self.in_castles + self.walking


def totals(demo: dict[str, Any], color: int) -> list[Totals]:
    """A team's totals on every board, the board of turn T at index T - 1."""
    return [Totals(*digest._totals(frame, color)) for frame in demo["frames"]]


@dataclass(frozen=True)
class Group:
    """A soldier group from the turn it left to the turn it ended.

    Attributes:
        id: The group's id.
        team: Its team's colour.
        origin: The castle it left, as it stood on the board of its send's turn.
        target: The castle it walked to, as it stood on that board.
        soldiers: What it left with.
        speed_level: The speed level it copied.
        sent: The turn it was sent.
        ended: The turn it ended in (landed or was destroyed); None while it
            was still walking at the game's end.
        took: Whether its target was its team's on the board after it ended
            (it landed at its own castle, or it, or a group with it, took the target).
        target_team: Whose the target was on the board of the send's turn.
        last: The soldiers it had on the last board it was seen on, after
            any clash on the way: what it landed with, unless a clash in its
            last turn took more.
        destroyed: Whether a clash in the turn it ended left it with no soldiers,
            so it never landed.
    """

    id: int
    team: int
    origin: dict[str, Any]
    target: dict[str, Any]
    soldiers: int
    speed_level: int
    sent: int
    ended: int | None
    took: bool
    target_team: int
    last: int
    destroyed: bool

    @property
    def length(self) -> float:
        """How far it had to walk."""
        return distance(self.origin, self.target)

    @property
    def walk_turns(self) -> int:
        """How many turns its walk takes at its speed."""
        return walk(self.length, self.speed_level)


def groups(demo: dict[str, Any]) -> list[Group]:
    """Every group seen on a board, in the order they were sent.

    A group that left and was destroyed in the same turn is on no board,
    and is not here.
    """
    frames = demo["frames"]
    first: dict[int, tuple[int, dict[str, Any]]] = {}
    last_seen: dict[int, int] = {}
    last_soldiers: dict[int, int] = {}
    for index, frame in enumerate(frames):
        for group in frame["soldier_groups"]:
            if group["id"] not in first:
                first[group["id"]] = (index, group)
            last_seen[group["id"]] = index
            last_soldiers[group["id"]] = group["soldiers"]
    found = []
    for group_id, (index, group) in sorted(first.items(), key=lambda item: (item[1][0], item[0])):
        # The group is first on board index, so it was sent in the turn whose board is index - 1.
        before = {castle["id"]: castle for castle in frames[max(index - 1, 0)]["castles"]}
        origin, target = before[group["origin_castle_id"]], before[group["destination_castle_id"]]
        end_index = last_seen[group_id] + 1
        ended = end_index if end_index < len(frames) else None
        took = ended is not None and any(
            castle["id"] == target["id"] and castle["team_color"] == group["team_color"]
            for castle in frames[end_index]["castles"]
        )
        destroyed = ended is not None and any(
            participant["group_id"] == group_id and participant["soldiers_after"] == 0
            for clash in frames[end_index]["clashes"]
            for participant in clash["participants"]
        )
        found.append(
            Group(
                id=group_id,
                team=group["team_color"],
                origin=origin,
                target=target,
                soldiers=group["soldiers"],
                speed_level=group["upgrades"].get("speed", 1),
                sent=max(index, 1),
                ended=ended,
                took=took,
                target_team=target["team_color"],
                last=last_soldiers[group_id],
                destroyed=destroyed,
            )
        )
    return found


@dataclass(frozen=True)
class Capture:
    """A castle that changed hands in a turn."""

    turn: int
    castle: int
    lost_by: int
    taken_by: int
    soldiers_before: int


def captures(demo: dict[str, Any]) -> list[Capture]:
    """Every castle that changed hands, in turn order."""
    frames = demo["frames"]
    found = []
    for index in range(len(frames) - 1):
        before = {castle["id"]: castle for castle in frames[index]["castles"]}
        for castle in frames[index + 1]["castles"]:
            earlier = before[castle["id"]]
            if castle["team_color"] != earlier["team_color"]:
                found.append(
                    Capture(index + 1, castle["id"], earlier["team_color"], castle["team_color"], earlier["soldiers"])
                )
    return found


def production_lost(demo: dict[str, Any], capture: Capture) -> int:
    """What a capture cost the team that lost the castle: its production on every board until it got it back.

    Counted from the board after the capture to the game's last board, or to
    the board where the team holds the castle again.
    """
    lost = 0
    for frame in demo["frames"][capture.turn :]:
        castle = next(castle for castle in frame["castles"] if castle["id"] == capture.castle)
        if castle["team_color"] == capture.lost_by:
            break
        lost += production(castle)
    return lost


def spans(turns: list[int], gap: int = 1) -> list[tuple[int, int]]:
    """Sorted turns joined into stretches, where a stretch breaks after more than ``gap`` turns without one."""
    found: list[tuple[int, int]] = []
    for turn in sorted(turns):
        if found and turn - found[-1][1] <= gap:
            found[-1] = (found[-1][0], turn)
        else:
            found.append((turn, turn))
    return found
