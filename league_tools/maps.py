"""Make new maps for the league: fair two-team maps from a seed, and the official game's default maps."""

from __future__ import annotations

import json
import random
import re
import urllib.request
from collections.abc import Callable
from typing import Any

OFFICIAL_GAME = "https://island-battles.elidan.org"

NEUTRAL_SOLDIERS = (5, 8, 10, 12, 15, 18, 20, 25, 30)


def generate(name: str, seed: int) -> dict[str, Any]:
    """A map file for two teams, the same from both sides.

    Every castle at (x, y) has its twin at (-x, -y), so neither seat starts
    ahead. The same seed gives the same map.
    """
    rng = random.Random(seed)
    width, height = rng.choice((10, 12, 14, 16)), rng.choice((8, 10))
    half_width, half_height = width / 2, height / 2

    def half_step(low: float, high: float) -> float:
        return rng.randint(round(low * 2), round(high * 2)) / 2

    home = (half_step(half_width - 2, half_width - 0.5), half_step(-half_height / 2, half_height / 2))
    taken = [home, (-home[0], -home[1])]
    castles: list[dict[str, Any]] = [
        {"team_color": 1, "x": -home[0], "y": -home[1], "starting_soldier_amount": 30},
        {"team_color": 2, "x": home[0], "y": home[1], "starting_soldier_amount": 30},
    ]
    if rng.random() < 0.4:
        taken.append((0.0, 0.0))
        castles.append({"team_color": 0, "x": 0, "y": 0, "starting_soldier_amount": rng.randint(20, 35)})
    pairs = rng.randint(2, 5)
    attempts = 0
    while pairs > 0 and attempts < 1000:
        attempts += 1
        spot = (half_step(0, half_width - 0.5), half_step(-half_height + 0.5, half_height - 0.5))
        twin = (-spot[0], -spot[1])
        if any((spot[0] - x) ** 2 + (spot[1] - y) ** 2 < 1.5**2 for x, y in [*taken, twin]):
            continue
        taken += [spot, twin]
        soldiers = rng.choice(NEUTRAL_SOLDIERS)
        castles.append({"team_color": 0, "x": twin[0], "y": twin[1], "starting_soldier_amount": soldiers})
        castles.append({"team_color": 0, "x": spot[0], "y": spot[1], "starting_soldier_amount": soldiers})
        pairs -= 1
    return {
        "map_name": name,
        "player_amount": 2,
        "plane_size_x": width,
        "plane_size_y": height,
        "neutral_starting_soldier_amount": 15,
        "castles": castles,
    }


def official_name(map_name: str) -> str:
    """The league's file name for an official map: its name in lower case, words joined by hyphens."""
    return re.sub(r"[^a-z0-9]+", "-", map_name.lower()).strip("-")


def _get_json(url: str) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310 - the game's own https address
        return json.load(response)


def official(
    game_url: str = OFFICIAL_GAME, get: Callable[[str], dict[str, Any]] | None = None
) -> dict[str, dict[str, Any]]:
    """The game's default maps for two teams, as map files, by the league's name for each.

    The game lists its default maps at ``GET /map/templates`` and serves each one's
    map file at ``GET /map/templates/{map_template_id}`` (INTODAN/island-battles-go#390).
    The tournament pairs two teams, so maps for more teams are left out.
    """
    get = get or _get_json
    base = game_url.rstrip("/")
    found: dict[str, dict[str, Any]] = {}
    for listed in get(f"{base}/map/templates")["maps"]:
        if listed["team_count"] != 2:
            continue
        document = get(f"{base}/map/templates/{int(listed['map_template_id'])}")
        found[official_name(listed["map_name"])] = document
    return found
