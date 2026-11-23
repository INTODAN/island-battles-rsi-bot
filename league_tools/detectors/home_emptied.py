"""A castle sent out most of its soldiers while an enemy castle near it could take what was left, and fell.

The lessons it comes from: "A castle taken with 1 soldier near the enemy
falls unless another castle reinforces it", "An upgrade beside a stocked
enemy castle hands it over" (the same hole, made by a send), and real game
474, where castles emptied for strikes were taken one at a time.

A send empties a castle when, in one turn, a castle that held at least
``HELD`` soldiers sends at least half of them (all its groups of that turn together) and keeps at
most half. It is a mistake when, on the board of that turn, an enemy castle
whose group would land within ``REACH`` turns (at its own speed level) holds
more than the castle kept plus what it grows during that walk, and the
castle is then captured by the enemy within ``FALLS_WITHIN`` turns. One flag
per castle lost, for the last such send before it.

Cost: the castle's production lost, a turn's production for every board the
enemy held it, to the game's end or until it was taken back.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from league_tools.detectors import Flag, _board

KIND = "home_emptied"

# An enemy castle is near when its group lands within this many turns.
REACH = 6
# The castle must fall within this many turns of the send.
FALLS_WITHIN = 10
# A castle with fewer soldiers has no garrison to empty.
HELD = 10


def detect(demo: dict[str, Any]) -> list[Flag]:
    """Every castle lost soon after a send left it to a near enemy castle."""
    names = _board.team_names(demo)
    frames = demo["frames"]
    sent: dict[tuple[int, int], int] = defaultdict(int)
    for group in _board.groups(demo):
        sent[(group.sent, group.origin["id"])] += group.soldiers
    # Each castle's emptying sends: the turn, the team that sent and the evidence.
    empties: dict[int, list[tuple[int, int, str]]] = defaultdict(list)
    for (turn, castle_id), amount in sent.items():
        board = {castle["id"]: castle for castle in frames[turn - 1]["castles"]}
        castle = board[castle_id]
        held = castle["soldiers"]
        kept = held - amount
        if held < HELD or amount * 2 < held or kept * 2 > held:
            continue
        team = castle["team_color"]
        for enemy in sorted(board.values(), key=lambda other: _board.distance(castle, other)):
            if enemy["team_color"] in (0, team):
                continue
            steps = _board.walk(_board.distance(enemy, castle), enemy["upgrades"].get("speed", 1))
            if steps <= REACH and enemy["soldiers"] > kept + _board.production(castle) * steps:
                empties[castle_id].append(
                    (
                        turn,
                        team,
                        f"castle {castle_id} {held} -> {kept} soldiers ({amount} sent) while enemy castle "
                        f"{enemy['id']} held {enemy['soldiers']}, {steps} turns away",
                    )
                )
                break
    flags = []
    for capture in _board.captures(demo):
        if capture.lost_by == 0 or capture.taken_by == 0:
            continue
        before = [
            (turn, evidence)
            for turn, team, evidence in empties.get(capture.castle, [])
            if team == capture.lost_by and 0 <= capture.turn - turn <= FALLS_WITHIN
        ]
        if not before or capture.lost_by not in names:
            continue
        turn, evidence = before[-1]
        owner = capture.lost_by
        lost = _board.production_lost(demo, capture)
        flags.append(
            Flag(
                owner,
                names[owner],
                KIND,
                (turn, capture.turn),
                f"{evidence}; it fell on turn {capture.turn} ({lost} production lost)",
                float(lost),
            )
        )
    return flags
