"""The league's lines as data: ``ledger/lines.toml``.

A line is a founder and the bots descended from it: one strategy. The
``league-population`` skill keeps them in the ledger's table **The lines**;
this file holds the same, for the rules as code (``league decide``) to read
and write. Each line has its name, its strategy in a sentence, its head, its
state (``main``, ``side`` or ``closed``), the count of its iterations of work
in a row without a promotion, and the bots that belong to it. The file also
names the champion, the main line's head.

The bots made before the rules of lines are listed in the line the table
gives them, so nothing is inferred for them. A new bot's line is read from its
idea and its parent: a ``Founder:`` begins a line of its own, an
``Exploiter`` belongs to none, and any other bot is in its parent's line.
"""

from __future__ import annotations

import json
import re
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from .paths import LEDGER
from .roster import Bot

LINES_FILE = LEDGER / "lines.toml"
STATES = ("main", "side", "closed")
KINDS = ("fix", "graft", "simplification", "founder", "exploiter")
# An idea begins with its kind (the ``league-ideas`` skill): ``Fix:``,
# ``Graft from NAME:``, ``Simplification:``, ``Founder:``, ``Exploiter of NAME:``.
KIND = re.compile(r"\s*(Fix|Graft|Simplification|Founder|Exploiter)\b")


@dataclass
class Line:
    """One line: a strategy and the bots descended from its founder."""

    name: str
    strategy: str
    state: str
    head: str = ""
    bots: list[str] = field(default_factory=list)
    # Iterations of work in a row without a promotion: a side line is closed at two.
    without_promotion: int = 0
    # What the table's row says besides: why a line closed, what it showed.
    note: str = ""


@dataclass
class Lines:
    """Every line of the league, and the champion."""

    champion: str
    lines: list[Line]

    def get(self, name: str | None) -> Line | None:
        """The line of that name, or None."""
        return next((line for line in self.lines if line.name == name), None)

    @property
    def main(self) -> Line:
        """The main line: the champion's.

        Raises:
            ValueError: No line is the main one.
        """
        found = [line for line in self.lines if line.state == "main"]
        if len(found) != 1:
            raise ValueError(f"the lines need exactly one main line, not {len(found)}")
        return found[0]

    @property
    def side(self) -> list[Line]:
        """The side lines, in the file's order."""
        return [line for line in self.lines if line.state == "side"]

    def listed(self, bot: str) -> Line | None:
        """The line whose ``bots`` list the bot, or None."""
        return next((line for line in self.lines if bot in line.bots), None)


def kind_of(idea: str) -> str | None:
    """A candidate's kind, from the first word of its idea: fix, graft, simplification, founder or exploiter."""
    match = KIND.match(idea)
    return match.group(1).lower() if match else None


def line_of(name: str, lines: Lines, roster: Mapping[str, Bot]) -> str | None:
    """The name of a bot's line, or None for a bot of no line.

    A bot the file lists is in that line. Otherwise a sparring bot and an
    ``Exploiter`` are in none, a ``Founder:`` begins its own (named after it),
    and any other bot is in its parent's line, read up the parent chain.

    Args:
        name: The bot.
        lines: The lines.
        roster: The league's bots by name.
    """
    seen: set[str] = set()
    while name not in seen:
        seen.add(name)
        listed = lines.listed(name)
        if listed is not None:
            return listed.name
        bot = roster.get(name)
        if bot is None or bot.status == "sparring":
            return None
        kind = kind_of(bot.idea)
        if kind == "exploiter":
            return None
        if kind == "founder":
            return name
        if not bot.parent or bot.parent == name:
            return None
        name = bot.parent
    return None


def load_lines(path: Path = LINES_FILE) -> Lines:
    """Read the lines file.

    Raises:
        ValueError: A line has no name or an unknown state, or the champion is not the main line's head.
    """
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    lines = []
    for row in data.get("line", []):
        line = Line(
            name=str(row.get("name", "")),
            strategy=str(row.get("strategy", "")),
            state=str(row.get("state", "")),
            head=str(row.get("head", "")),
            bots=[str(bot) for bot in row.get("bots", [])],
            without_promotion=int(row.get("without_promotion", 0)),
            note=str(row.get("note", "")),
        )
        if not line.name or line.state not in STATES:
            raise ValueError(f"{path}: a line needs a name and a state of {', '.join(STATES)}: {row}")
        lines.append(line)
    loaded = Lines(champion=str(data.get("champion", "")), lines=lines)
    if loaded.main.head != loaded.champion:
        raise ValueError(f"{path}: the champion {loaded.champion!r} is not the main line's head {loaded.main.head!r}")
    return loaded


def _string(value: str) -> str:
    """A TOML basic string."""
    return json.dumps(value, ensure_ascii=False)


def dumps(lines: Lines) -> str:
    """The lines file's text."""
    out = [
        "# The league's lines: what the ledger's table \"The lines\" says, as data for `league decide`",
        "# (league_tools/lines.py). A line is a founder and the bots descended from it. state is main,",
        "# side or closed; without_promotion counts the line's iterations of work in a row without a",
        "# promotion (a side line is closed at two); bots are the bots of the league in the line.",
        f"champion = {_string(lines.champion)}",
    ]
    for line in lines.lines:
        out += ["", "[[line]]", f"name = {_string(line.name)}", f"state = {_string(line.state)}"]
        out.append(f"head = {_string(line.head)}")
        out.append(f"strategy = {_string(line.strategy)}")
        out.append("bots = [" + ", ".join(_string(bot) for bot in line.bots) + "]")
        out.append(f"without_promotion = {line.without_promotion}")
        out.append(f"note = {_string(line.note)}")
    return "\n".join(out) + "\n"


def write_lines(lines: Lines, path: Path = LINES_FILE) -> None:
    """Write the lines file."""
    path.write_text(dumps(lines), encoding="utf-8")


def table(lines: Lines, statuses: Mapping[str, str]) -> list[str]:
    """The lines as the ledger's table **The lines**.

    Args:
        lines: The lines.
        statuses: Each bot of the league's status.
    """
    rows = ["| Line | Its strategy | Head | Other active bots | State |", "|---|---|---|---|---|"]
    for line in lines.lines:
        others = [f"`{bot}`" for bot in line.bots if bot != line.head and statuses.get(bot) == "active"]
        state = line.state
        if line.state != "closed":
            count = line.without_promotion
            state += f"; {count} iteration{'' if count == 1 else 's'} of work without a promotion"
        if line.note:
            state += f"; {line.note}"
        head = f"`{line.head}`" if line.head else "none"
        rows.append(f"| `{line.name}` | {line.strategy} | {head} | {', '.join(others) or 'none'} | {state} |")
    return rows
