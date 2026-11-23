"""Every bot of the league has a complete bot.toml.

The checks of the bots' code, that it builds, answers every board with a result
the server accepts, logs every turn, keeps its memory small and imports only
what is pure, are Go tests: ``tests/bots/bots_test.go``, which ``go test ./...``
runs (``scripts/check.sh`` does).
"""

import pytest

from league_tools.paths import BOTS
from league_tools.roster import ANCHOR, NAME, Bot, load_roster

ROSTER = load_roster()
NAMES = [bot.name for bot in ROSTER]


def test_the_league_has_bots() -> None:
    assert NAMES


@pytest.mark.parametrize("bot", ROSTER, ids=NAMES)
def test_bot_toml_is_complete(bot: Bot) -> None:
    assert NAME.fullmatch(bot.name) and not ANCHOR.fullmatch(bot.name)
    assert bot.idea.strip()
    assert bot.parent == "" or bot.parent != bot.name
    assert (BOTS / bot.name / "main.go").is_file()
