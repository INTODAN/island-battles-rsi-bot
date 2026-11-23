"""A game that ran to the turn limit while one team led clearly for a long stretch: a win that didn't arrive.

The lessons it comes from: "A bot that only attacks what one castle affords
alone never finishes" (the economist held 1,100 soldiers in 7 castles for
80 turns against one castle), "A level game at production 4 is a draw unless
someone strikes exactly", and "a draw at the limit is often a win that
didn't arrive" (iteration 38's `speedhelp_landlate`).

A team leads clearly on a board when it has at least ``RATIO`` times the
other's soldiers (in castles and walking), and no fewer castles and no less
production. The mistake is a game that ended at the turn limit with a
stretch of at least ``STRETCH`` boards in a row on which the same team led
clearly. The flag is the leader's, for its longest such stretch.

Cost: the turns of the stretch.
"""

from __future__ import annotations

from typing import Any

from league_tools.detectors import Flag, _board

KIND = "idle_lead"

RATIO = 1.5
STRETCH = 100


def detect(demo: dict[str, Any]) -> list[Flag]:
    """The leader's longest clear lead in a game that ran to the limit."""
    names = _board.team_names(demo)
    if not _board.ran_to_limit(demo) or len(names) != 2:
        return []
    flags = []
    first, second = sorted(names)
    teams = {first: _board.totals(demo, first), second: _board.totals(demo, second)}
    for team, other in ((first, second), (second, first)):
        ahead = [
            index + 1
            for index, (mine, theirs) in enumerate(zip(teams[team], teams[other], strict=True))
            if mine.soldiers >= RATIO * max(theirs.soldiers, 1)
            and mine.castles >= theirs.castles
            and mine.production >= theirs.production
        ]
        if not ahead:
            continue
        start, end = max(_board.spans(ahead), key=lambda span: (span[1] - span[0], -span[0]))
        if end - start + 1 < STRETCH:
            continue
        mine, theirs = teams[team][start - 1], teams[other][start - 1]
        at_end = teams[team][end - 1], teams[other][end - 1]
        flags.append(
            Flag(
                team,
                names[team],
                KIND,
                (start, end),
                f"led clearly from turn {start} to {end} ({end - start + 1} turns): soldiers {mine.soldiers} to "
                f"{theirs.soldiers}, castles {mine.castles} to {theirs.castles} at the start; soldiers "
                f"{at_end[0].soldiers} to {at_end[1].soldiers}, castles {at_end[0].castles} to {at_end[1].castles} "
                "at the end; the game ran to the limit",
                float(end - start + 1),
            )
        )
    return flags
