"""Detectors: code that finds a known mistake in one demo, with its turns and its numbers.

A detector is a module of this package whose name doesn't start with ``_``.
It has a ``KIND`` (its name in the tables), a docstring that states the
mistake, how it is measured and the lesson it comes from, and
``detect(demo) -> list[Flag]``. It reads only the demo, through
``league_tools.digest`` and ``_board``, and never a file, a bot's code or the
network: ``tests/test_detectors.py`` checks what each module imports and
calls. A detector only points at turns. It never changes a result, a rating
or a decision.

``league_tools/flags.py`` finds the detectors, runs them and keeps their flags
by match key; ``league mistakes`` sums them up for a tournament.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Flag:
    """One mistake in one game: whose, where, and how much it mattered.

    Attributes:
        team: The team's colour (1 or 2).
        bot: The name of the bot in that seat.
        kind: The detector's ``KIND``.
        turns: The first and last turn of the window to read, as
            ``digest --turns`` counts them.
        evidence: The numbers that show the mistake, in a sentence.
        cost: How much it mattered, in the unit the detector's docstring
            names (soldiers, production-turns or turns). Costs of one kind
            add up; costs of two kinds don't compare.
    """

    team: int
    bot: str
    kind: str
    turns: tuple[int, int]
    evidence: str
    cost: float

    def as_dict(self) -> dict[str, Any]:
        """The flag as JSON can hold it."""
        return {
            "team": self.team,
            "bot": self.bot,
            "kind": self.kind,
            "turns": list(self.turns),
            "evidence": self.evidence,
            "cost": self.cost,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Flag:
        """A flag read back from ``as_dict``."""
        first, last = data["turns"]
        return cls(int(data["team"]), data["bot"], data["kind"], (first, last), data["evidence"], data["cost"])
