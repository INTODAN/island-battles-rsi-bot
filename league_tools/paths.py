"""Where the league keeps its files."""

import os
import subprocess
from pathlib import Path

LEAGUE = Path(__file__).resolve().parents[1]
BOTS = LEAGUE / "bots"
MAPS = LEAGUE / "maps"
RUNS = LEAGUE / "runs"
LEDGER = LEAGUE / "ledger"
# Which commit of the game the headless runner is built from.
RUNNER_PIN = LEAGUE / "runner.toml"

# Overrides the directory that holds the result cache and the runner.
SHARED_VARIABLE = "LEAGUE_SHARED"


def _shared_root() -> Path:
    """The checkout whose result cache and runner every checkout of the repository uses.

    A git worktree (an iteration's branch, a subagent's) shares the main
    checkout's: a match is keyed on everything that decides it, so a result
    played in one checkout is as good in another, and a new worktree doesn't
    play the whole league again before its first tournament.
    """
    override = os.environ.get(SHARED_VARIABLE)
    if override:
        return Path(override).expanduser().resolve()
    try:
        common = subprocess.run(
            ["git", "-C", str(LEAGUE), "rev-parse", "--path-format=absolute", "--git-common-dir"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except OSError, subprocess.CalledProcessError:
        return LEAGUE
    root = Path(common).parent
    return root if (root / "runner.toml").is_file() else LEAGUE


SHARED = _shared_root()
# Every match's result and demo, by the match's key: shared by all checkouts.
CACHE = SHARED / "runs" / "cache"
# The game's source at that commit, fetched on the first build, and the runners built from it.
RUNNER = SHARED / ".runner"
RUNNER_SOURCE = RUNNER / "source"
# The bots' binaries, each named by its bot and a hash of its code: shared by all checkouts.
BINARIES = SHARED / "runs" / "bin"
