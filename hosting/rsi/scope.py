"""Check that an iteration's commits change only what an iteration may change.

    python3 hosting/rsi/scope.py BASE [HEAD] [--names-from runs/real]

An iteration may change a bot's directory under ``bots/``, the ledger
(``ledger/iterations.md`` and ``ledger/real-games.txt``) and the deployed bot's
name (``hosting/lambda/bot``), and add new map files to ``maps/train/`` or
``maps/holdout/``. Anything else in the diff from BASE to HEAD fails the
check. The automated iteration's pull request runs it, and so does every pull
request from a ``claude/league-iteration-`` branch: a model that read an
opponent's logs must not be able to change a workflow, a tool or a test.

With ``--names-from``, the players' names in the real games' demos under that
directory must not appear in the lines the diff adds: the repository is public,
and the ledger describes real games without names.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Iterable
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
ALLOWED = (
    re.compile(r"^bots/[a-z][a-z0-9_]*/[^/].*$"),
    re.compile(r"^ledger/(iterations\.md|real-games\.txt)$"),
    re.compile(r"^hosting/lambda/bot$"),
)
NEW_MAP = re.compile(r"^maps/(train|holdout)/[a-z0-9_]+\.json$")
# Shorter names match too much ordinary text to check.
MIN_NAME = 3


def out_of_scope(changes: Iterable[tuple[str, str]]) -> list[str]:
    """The changes, as (git status letter, path), that an iteration may not make."""
    bad = []
    for status, path in changes:
        if any(rule.match(path) for rule in ALLOWED):
            continue
        if status == "A" and NEW_MAP.match(path):
            continue
        bad.append(f"{status} {path}")
    return bad


def player_names(directory: Path, ignore: set[str]) -> set[str]:
    """The players' display names in the demos under directory, other than those in ignore."""
    names: set[str] = set()
    for path in directory.glob("*/demo.json"):
        demo = json.loads(path.read_text())
        for team in demo.get("teams", []):
            names.update(team.get("players") or [])
        for entry in demo.get("logs", []):
            names.update(player.get("display_name", "") for player in entry.get("players", []))
    return {name for name in names if len(name.strip()) >= MIN_NAME and name.lower() not in ignore}


def added_lines(diff: str) -> list[tuple[str, int, str]]:
    """The lines a ``git diff --unified=0`` adds, as (path, line number, text)."""
    added = []
    path, number = "", 0
    for line in diff.splitlines():
        if line.startswith("+++ "):
            path = line[6:] if line.startswith("+++ b/") else line[4:]
        elif line.startswith("@@"):
            hunk = re.search(r"\+(\d+)", line)
            number = int(hunk.group(1)) if hunk else 0
        elif line.startswith("+"):
            added.append((path, number, line[1:]))
            number += 1
    return added


def leaked(added: Iterable[tuple[str, int, str]], names: set[str]) -> list[str]:
    """Where a name appears, as a whole word, in the added lines: ``path:line``.

    The names themselves are never printed: the checks' logs of a public repository are public.
    """
    patterns = [re.compile(rf"(?<!\w){re.escape(name.lower())}(?!\w)") for name in names]
    return [f"{path}:{number}" for path, number, text in added if any(p.search(text.lower()) for p in patterns)]


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout


def main(argv: list[str] | None = None) -> int:
    """Run the check; returns the exit status."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("base")
    parser.add_argument("head", nargs="?", default="HEAD")
    parser.add_argument("--names-from", type=Path)
    parser.add_argument("--also", type=Path, nargs="*", default=[], help="more files to check for names (a PR body)")
    args = parser.parse_args(argv)

    lines = _git("diff", "--name-status", "--no-renames", f"{args.base}...{args.head}").splitlines()
    changes = [(line.split("\t")[0][0], line.split("\t")[-1]) for line in lines if line.strip()]
    if not changes:
        print("the iteration changed nothing", file=sys.stderr)
        return 1
    failed = False
    for change in out_of_scope(changes):
        print(f"out of an iteration's scope: {change}", file=sys.stderr)
        failed = True
    if args.names_from is not None:
        bots = {path.name.lower() for path in (ROOT / "bots").iterdir() if path.is_dir()}
        names = player_names(args.names_from, bots | {f"level{n}" for n in range(1, 4)})
        added = added_lines(_git("diff", "--unified=0", f"{args.base}...{args.head}"))
        for path in args.also:
            added += [(str(path), n, text) for n, text in enumerate(path.read_text().splitlines(), 1)]
        for place in leaked(added, names):
            print(f"a real game's player name is on the added line {place}", file=sys.stderr)
            failed = True
    if not failed:
        print(f"{len(changes)} changed files, all in an iteration's scope")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
