"""The castle nearest the enemy stood thin while rear castles held many, and fell.

The lesson it comes from: "The lightly held castle on the border decides a
level game" (a real game on `claw`: the castle at (0, -3) was captured four
times, usually held under 20 soldiers while the stacks stood elsewhere), and
real game 474, where rear castles saved apart while one enemy stack took
them one at a time.

On each board, a team's border castle is its castle nearest an enemy castle
(ties by id), for a team with at least two castles. It stands thin when the
nearest enemy castle holds more than it does, and one of the team's other
castles holds at least ``RATIO`` times its soldiers and ``MARGIN`` more. The
mistake is a border castle that stood thin for at least ``STRETCH`` boards in
a row and was captured by the enemy on the turn after the last of them or
within ``FALLS_WITHIN`` turns. One flag per castle lost; its window is the
stretch's last ``LONGEST`` turns and the fall.

Cost: the castle's production lost, a turn's production for every board the
enemy held it, to the game's end or until it was taken back.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from league_tools.detectors import Flag, _board

KIND = "thin_border"

RATIO = 3
MARGIN = 20
STRETCH = 3
FALLS_WITHIN = 3
# The window to read is at most this many turns before the fall.
LONGEST = 15


def detect(demo: dict[str, Any]) -> list[Flag]:
    """Every border castle lost after standing thin beside a rear that held many."""
    names = _board.team_names(demo)
    # Each castle's turns of standing thin: its soldiers, the fullest rear castle and the nearest enemy castle then.
    thin: dict[tuple[int, int], dict[int, tuple[int, int, int, int, int]]] = defaultdict(dict)
    for index, frame in enumerate(demo["frames"]):
        for team in names:
            own = [castle for castle in frame["castles"] if castle["team_color"] == team]
            enemies = [castle for castle in frame["castles"] if castle["team_color"] not in (0, team)]
            if len(own) < 2 or not enemies:
                continue
            border, enemy = min(
                ((castle, other) for castle in own for other in enemies),
                key=lambda pair: (_board.distance(*pair), pair[0]["id"], pair[1]["id"]),
            )
            rear = max((castle for castle in own if castle is not border), key=lambda castle: castle["soldiers"])
            soldiers = border["soldiers"]
            if (
                enemy["soldiers"] > soldiers
                and rear["soldiers"] >= RATIO * soldiers
                and rear["soldiers"] >= soldiers + MARGIN
            ):
                thin[(border["id"], team)][index + 1] = (
                    soldiers,
                    rear["id"],
                    rear["soldiers"],
                    enemy["id"],
                    enemy["soldiers"],
                )
    flags = []
    for capture in _board.captures(demo):
        if capture.taken_by == 0 or capture.lost_by not in names:
            continue
        boards = thin.get((capture.castle, capture.lost_by), {})
        recent = [turn for turn in boards if 0 <= capture.turn - turn <= FALLS_WITHIN]
        if not recent:
            continue
        stretch = [span for span in _board.spans(list(boards)) if span[0] <= max(recent) <= span[1]][0]
        first, last = stretch[0], max(recent)
        if last - first + 1 < STRETCH:
            continue
        soldiers, rear, held, enemy, enemy_held = boards[last]
        lost = _board.production_lost(demo, capture)
        flags.append(
            Flag(
                capture.lost_by,
                names[capture.lost_by],
                KIND,
                (max(first, capture.turn - LONGEST), capture.turn),
                f"border castle {capture.castle} held {soldiers} (turns {first}-{last}) while castle {rear} held "
                f"{held} and the nearest enemy castle {enemy} held {enemy_held}; it fell on turn {capture.turn} "
                f"({lost} production lost)",
                float(lost),
            )
        )
    return flags
