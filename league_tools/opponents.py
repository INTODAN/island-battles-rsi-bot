"""Outside opponents: bots that live outside this repository and play in every tournament.

A player's own bot project can be a fixed opponent of the league without its
code coming here. ``opponents.local.toml`` (not in git) names each one:

    [opponents.outside_player]
    directory = "/path/to/their/bot/project"
    python = ".venv/bin/python"   # the project's interpreter, relative to directory
    entry = "bot:play"            # module:function, run from directory

Each plays every tournament like a default bot: it is never a candidate,
never changes status, and its results count in the ratings. Its fingerprint is
its project's Python files and lock file, so a change there plays its matches
again.
"""

from __future__ import annotations

import hashlib
import tomllib
from dataclasses import dataclass
from pathlib import Path

from .paths import LEAGUE
from .roster import ANCHOR, NAME

CONFIG = LEAGUE / "opponents.local.toml"
# Directories of a bot project that hold no code of the bot.
SKIPPED = {".venv", ".git", "__pycache__", ".pytest_cache", ".ruff_cache", "tests", "dist", "node_modules"}


@dataclass(frozen=True)
class Opponent:
    """An outside bot: where its project is, and how to run it."""

    name: str
    directory: Path
    python: Path
    entry: str

    def specification(self) -> dict[str, object]:
        """The runner's description of this player."""
        return {
            "worker": [str(self.python), "-m", "island_battles_client.worker", self.entry],
            "directory": str(self.directory),
            "environment": {"PYTHONHASHSEED": "0"},
        }

    def fingerprint(self) -> str:
        """A hash of the project's Python files and lock file: what decides how it plays."""
        digest = hashlib.sha256()
        files = [
            path
            for path in self.directory.rglob("*")
            if path.is_file()
            and (path.suffix == ".py" or path.name == "uv.lock")
            and not SKIPPED & set(path.relative_to(self.directory).parts)
        ]
        for path in sorted(files):
            digest.update(path.relative_to(self.directory).as_posix().encode())
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
        return "outside:" + digest.hexdigest()


def load_opponents(config: Path = CONFIG) -> dict[str, Opponent]:
    """The outside opponents that ``opponents.local.toml`` names; none without the file.

    Raises:
        ValueError: An entry is incomplete, its name isn't a bot name, or its interpreter is missing.
    """
    if not config.is_file():
        return {}
    data = tomllib.loads(config.read_text(encoding="utf-8")).get("opponents", {})
    opponents = {}
    for name, entry in sorted(data.items()):
        if not NAME.fullmatch(name) or ANCHOR.fullmatch(name):
            raise ValueError(f"{config}: {name!r} is not an opponent name: lower-case letters, digits and _")
        try:
            directory = Path(entry["directory"]).expanduser()
            python = directory / entry.get("python", ".venv/bin/python")
            opponent = Opponent(name=name, directory=directory, python=python, entry=entry.get("entry", "bot:play"))
        except (KeyError, TypeError) as error:
            raise ValueError(f"{config}: opponent {name!r} needs a directory") from error
        if not opponent.python.is_file():
            raise ValueError(f"{config}: opponent {name!r}: no interpreter at {opponent.python}")
        opponents[name] = opponent
    return opponents
