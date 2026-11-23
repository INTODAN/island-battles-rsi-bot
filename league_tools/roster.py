"""The league's bots: one directory each under ``bots/``, a Go program (``main.go``) with a ``bot.toml``."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import tomllib
from dataclasses import dataclass
from pathlib import Path

from .paths import BOTS

STATUSES = ("candidate", "active", "retired", "sparring")
NAME = re.compile(r"[a-z][a-z0-9_]*")
ANCHOR = re.compile(r"level([0-9]+)")


@dataclass(frozen=True)
class Bot:
    """One bot of the league, as its ``bot.toml`` describes it."""

    name: str
    status: str
    parent: str
    iteration: int
    idea: str

    @property
    def directory(self) -> Path:
        """The bot's directory."""
        return BOTS / self.name


def load_bot(name: str) -> Bot:
    """Read a bot's ``bot.toml``.

    Raises:
        ValueError: The bot is missing, or its file is not a valid ``bot.toml``.
    """
    if not NAME.fullmatch(name):
        raise ValueError(f"{name!r} is not a bot name: lower-case letters, digits and _, starting with a letter")
    path = BOTS / name / "bot.toml"
    if not path.is_file() or not (BOTS / name / "main.go").is_file():
        raise ValueError(f"there is no bot {name!r}: {path.parent} needs main.go and bot.toml")
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    bot = Bot(
        name=name,
        status=str(data.get("status", "")),
        parent=str(data.get("parent", "")),
        iteration=int(data.get("iteration", 0)),
        idea=str(data.get("idea", "")),
    )
    if bot.status not in STATUSES:
        raise ValueError(f"{path}: status must be one of {', '.join(STATUSES)}")
    return bot


def load_roster() -> list[Bot]:
    """Every bot of the league, by name."""
    names = sorted(path.parent.name for path in BOTS.glob("*/bot.toml"))
    return [load_bot(name) for name in names]


def _toml_string(value: str) -> str:
    """A TOML basic string: JSON's escapes, with other characters as they are."""
    return json.dumps(value, ensure_ascii=False).replace("\x7f", "\\u007f")


def write_bot(bot: Bot) -> None:
    """Write a bot's ``bot.toml``."""
    lines = [
        "# candidate: new and unproven. active: in the population. retired: no longer",
        "# developed, kept as an opponent. sparring: a fixed opponent built to play like a",
        "# real one; never changed, never counted with the retired bots, never deleted.",
        f"status = {_toml_string(bot.status)}",
        "# The bot this one's code was copied from. A founder keeps it too: the ledger's",
        "# table of the lines says which line a bot belongs to.",
        f"parent = {_toml_string(bot.parent)}",
        "# The league iteration that created it (ledger/iterations.md).",
        f"iteration = {bot.iteration}",
        "# What this bot tries that its parent doesn't, in a sentence.",
        f"idea = {_toml_string(bot.idea)}",
    ]
    (bot.directory / "bot.toml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def new_bot(name: str, parent: str, iteration: int, idea: str) -> Bot:
    """Copy ``parent`` to a new candidate named ``name``.

    Raises:
        ValueError: The name is taken or not a valid bot name.
    """
    if not NAME.fullmatch(name) or ANCHOR.fullmatch(name):
        raise ValueError(
            f"{name!r} is not a bot name: lower-case letters, digits and _, "
            "starting with a letter, and not levelN, which names a default bot"
        )
    if (BOTS / name).exists():
        raise ValueError(f"there is already a bot {name!r}")
    source = load_bot(parent)
    shutil.copytree(source.directory, BOTS / name)
    bot = Bot(name=name, status="candidate", parent=parent, iteration=iteration, idea=idea)
    write_bot(bot)
    return bot


def set_status(name: str, status: str) -> Bot:
    """Change a bot's status."""
    if status not in STATUSES:
        raise ValueError(f"status must be one of {', '.join(STATUSES)}")
    current = load_bot(name)
    bot = Bot(
        name=name,
        status=status,
        parent=current.parent,
        iteration=current.iteration,
        idea=current.idea,
    )
    write_bot(bot)
    return bot


def delete_bot(name: str) -> Bot:
    """Delete a bot's directory: a rejected candidate, or a bot the population's rules remove.

    Git keeps what was committed. A sparring bot holds the rating scale and
    stands for a real opponent, so it is never deleted.

    Raises:
        ValueError: There is no such bot, or it is a sparring bot.
    """
    bot = load_bot(name)
    if bot.status == "sparring":
        raise ValueError(f"{name} is a sparring bot, which is never deleted")
    shutil.rmtree(bot.directory)
    return bot


def sources(directory: Path) -> list[Path]:
    """A bot's Go files that build into it: every ``.go`` file but its tests."""
    return sorted(path for path in directory.rglob("*.go") if not path.name.endswith("_test.go"))


def fingerprint(directory: Path) -> str:
    """A hash of a bot's Go files, its tests left out: the code that plays."""
    digest = hashlib.sha256()
    for path in sources(directory):
        digest.update(path.relative_to(directory).as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()
