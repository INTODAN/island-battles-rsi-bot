"""The turn the game turned for good, and every castle the loser lost.

The mistake: none by itself. It marks, in every decided game, the window a
study reads first ("find the turn where the game turned", the bot-league
skill's Studying a game), which a study found by hand until now.

The lead on a board is the production lead (the sum of each team's castles'
production levels); where production is level, the soldiers' lead (in
castles and walking); where both are level, the castles' lead. The turning
point is the first turn from which the winner led on every board to the end.
A game won on castles at the limit by a team that didn't lead so at the end
falls back on the castles' lead alone. The flag is the loser's, one per
decided game. Its window runs from the turning point to the first castle the
loser lost from then on, at most ``LONGEST`` turns on (the turning point
alone if it lost none), and its evidence lists both teams' numbers at
the turning point and every castle the loser lost in the game, with its turn.

Cost: the castles the loser lost from the turning point on.
"""

from __future__ import annotations

from typing import Any

from league_tools.detectors import Flag, _board

KIND = "turning_point"

# The window a study reads first is at most this many turns after the turning point.
LONGEST = 15


def lead(first: _board.Totals, second: _board.Totals, castles_only: bool = False) -> int:
    """Who leads on a board: 1 for the first team, -1 for the second, 0 for neither.

    Production first, then soldiers, then castles; or castles alone.
    """
    pairs = [(first.castles, second.castles)]
    if not castles_only:
        pairs = [(first.production, second.production), (first.soldiers, second.soldiers), *pairs]
    for mine, theirs in pairs:
        if mine != theirs:
            return 1 if mine > theirs else -1
    return 0


def turned(winning: list[_board.Totals], losing: list[_board.Totals], castles_only: bool) -> int | None:
    """The first turn from which the winner led on every board to the end, or None if it didn't lead at the end."""
    turn = None
    for index in range(len(winning) - 1, -1, -1):
        if lead(winning[index], losing[index], castles_only) != 1:
            break
        turn = index + 1
    return turn


def detect(demo: dict[str, Any]) -> list[Flag]:
    """The loser's turning point in a decided game; nothing in a draw."""
    names = _board.team_names(demo)
    won = _board.winner(demo)
    if won is None or len(names) != 2:
        return []
    (lost,) = [color for color in names if color != won]
    winning, losing = _board.totals(demo, won), _board.totals(demo, lost)
    turn = turned(winning, losing, castles_only=False) or turned(winning, losing, castles_only=True)
    if turn is None:
        return []
    castles_lost = [capture for capture in _board.captures(demo) if capture.lost_by == lost]
    after = [capture for capture in castles_lost if capture.turn >= turn]
    window = (turn, min(after[0].turn, turn + LONGEST) if after else turn)
    at = turn - 1
    listed = ", ".join(f"{capture.castle} on {capture.turn}" for capture in castles_lost) or "none"
    evidence = (
        f"from turn {turn} {names[won]} led to the end: production {winning[at].production} to "
        f"{losing[at].production}, soldiers {winning[at].soldiers} to {losing[at].soldiers}, castles "
        f"{winning[at].castles} to {losing[at].castles}; castles lost: {listed}"
    )
    return [Flag(lost, names[lost], KIND, window, evidence, float(len(after)))]
