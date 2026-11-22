"""Ratings from a set of games: a Bradley-Terry fit, shown on the Elo scale."""

from __future__ import annotations

import math
import sys
from collections import defaultdict
from collections.abc import Iterable

# The players every rating is measured against, with the rating each is fixed
# at: the first of them that played. ``ori_mimic`` is a sparring bot, never
# changed and never deleted, that wins and loses against the whole population,
# so its games place it, and every rating with it, the same in every
# tournament. 1800 is about its rating in the tables of iterations 24 to 29,
# which still had ``level3`` at 1000, so the training scale goes on from them.
# ``level3`` at 1000, the anchor until then, serves a tournament without
# ``ori_mimic``; it stopped working in the whole population's tables once
# ``level3`` won no game in them, since a player that wins nothing sits at the
# fit's prior, not where its games put it.
RATING_ANCHORS = (("ori_mimic", 1800.0), ("level3", 1000.0))
# Far more rounds than a fit needs; real tournaments settle within a few hundred.
MAX_ROUNDS = 100_000


def fit(games: Iterable[tuple[str, str, float]]) -> dict[str, float]:
    """Rate the players of ``games``.

    Each game is ``(first, second, score)``, where score is the first
    player's: 1 for a win, 0.5 for a draw, 0 for a loss. Unlike running Elo
    updates, the fit doesn't depend on the order of the games. Every player
    also gets one drawn game against an average player, which keeps the
    rating of a player who won or lost everything finite.

    Returns:
        Each player's rating. The first of ``RATING_ANCHORS`` that played has
        its fixed rating; when none played, the mean is 1000.
    """
    score: dict[str, float] = defaultdict(float)
    played: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for first, second, first_score in games:
        score[first] += first_score
        score[second] += 1 - first_score
        played[first][second] += 1
        played[second][first] += 1
    players = sorted(played)
    if not players:
        return {}
    strength = dict.fromkeys(players, 1.0)
    # Each player's strength is updated with the others' newest ones, which
    # settles in far fewer rounds than updating all of them at once.
    for _ in range(MAX_ROUNDS):
        change = 0.0
        for player in players:
            expected = 1 / (strength[player] + 1)
            for opponent, count in played[player].items():
                expected += count / (strength[player] + strength[opponent])
            updated = (score[player] + 0.5) / expected
            change = max(change, abs(math.log(updated / strength[player])))
            strength[player] = updated
        if change < 1e-10:
            break
    else:
        # Only a player that beat another hundreds of times in a row gets
        # here; its rating is still as good as the rounds made it.
        print(f"league: the ratings hadn't settled after {MAX_ROUNDS} rounds; they are approximate", file=sys.stderr)
    ratings = {player: 400 * math.log10(strength[player]) for player in players}
    for anchor, fixed in RATING_ANCHORS:
        if anchor in ratings:
            return {player: fixed + rating - ratings[anchor] for player, rating in ratings.items()}
    mean = sum(ratings.values()) / len(ratings)
    return {player: 1000 + rating - mean for player, rating in ratings.items()}
