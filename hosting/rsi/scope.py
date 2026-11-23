"""Check that an iteration's commits change only what an iteration may change.

    python3 hosting/rsi/scope.py BASE [HEAD] [--kind iteration|run|curator] [--names-from runs/real]

An iteration may change a bot's directory under ``bots/``, the ledger
(``ledger/iterations.md``, ``ledger/real-games.txt``, ``ledger/progress.csv`` and a real game's study,
``ledger/studies/<game id>.md``) and the deployed bot's
name (``hosting/lambda/bot``), and add new map files to ``maps/train/`` or
``maps/holdout/``. Anything else in the diff from BASE to HEAD fails the
check. The automated iteration's pull request runs it, and so does every pull
request from a ``claude/league-iteration-`` branch: a model that read an
opponent's logs must not be able to change a workflow, a tool or a test.

Since runs work in parallel (docs/parallel-iterations.md) there are three
kinds of branch, ``--kind``:

- ``run`` (``claude/league-run-<id>``): a run's proposal. It only **adds**: new
  bots' directories (its candidates), its account ``ledger/runs/<id>.md``, the
  lessons it proposes ``ledger/lessons/<id>.md``, a real game's study, new map
  files and new detectors (``league_tools/detectors/<name>.py`` with its test
  ``tests/detectors/test_<name>.py``). It changes and deletes nothing: a status,
  an existing bot, the ledger's entries and the lines are the integrator's.
- ``iteration`` (``claude/league-iteration-N``, the default): what an iteration
  or the integrator writes, as above, and the lines file ``ledger/lines.toml``,
  the runs' and lessons' files it carries, and the new detectors the runs added.
- ``curator``: folds the proposed lessons into the ledger: ``ledger/iterations.md``
  only, and deletes files of ``ledger/lessons/``.

With ``--names-from``, the players' names in the real games' demos under that
directory must not appear in the lines the diff adds: the repository is public,
and the ledger describes real games without names.
A name that BASE's files already hold as a word (a display name that is an
ordinary word, such as one the bots' comments use) leaks nothing new and can't
be told from that word, so it is not checked: every candidate copies its
parent's comments, and they would all fail.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Collection, Iterable
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
RUN_FILE = r"[a-z0-9][a-z0-9-]*\.md"
ALLOWED = (
    re.compile(r"^bots/[a-z][a-z0-9_]*/[^/].*$"),
    re.compile(r"^ledger/(iterations\.md|real-games\.txt|progress\.csv|lines\.toml)$"),
    re.compile(r"^ledger/studies/[0-9]+\.md$"),
    re.compile(rf"^ledger/(runs|lessons)/{RUN_FILE}$"),
    re.compile(r"^hosting/lambda/bot$"),
)
NEW_MAP = re.compile(r"^maps/(train|holdout)/[a-z0-9_]+\.json$")
NEW_DETECTOR = re.compile(r"^league_tools/detectors/[a-z][a-z0-9_]*\.py$")
NEW_DETECTOR_TEST = re.compile(r"^tests/detectors/test_[a-z][a-z0-9_]*\.py$")
# What a run's branch may add; it may change or delete nothing.
RUN_ADDS = (
    re.compile(r"^bots/[a-z][a-z0-9_]*/[^/].*$"),
    re.compile(rf"^ledger/(runs|lessons)/{RUN_FILE}$"),
    re.compile(r"^ledger/studies/[0-9]+\.md$"),
    NEW_MAP,
    NEW_DETECTOR,
    NEW_DETECTOR_TEST,
)
KINDS = ("iteration", "run", "curator")
# Shorter names match too much ordinary text to check.
MIN_NAME = 3


def out_of_scope(
    changes: Iterable[tuple[str, str]], kind: str = "iteration", base_bots: Collection[str] = ()
) -> list[str]:
    """The changes, as (git status letter, path), that a branch of this kind may not make.

    Args:
        changes: (git status letter, path) for every file the branch changed.
        kind: ``iteration``, ``run`` or ``curator`` (the module's docstring).
        base_bots: for a run, the bots BASE has: a run adds only bots BASE doesn't have.
    """
    if kind == "run":
        return [
            f"{status} {path}"
            for status, path in changes
            if status != "A"
            or not any(rule.match(path) for rule in RUN_ADDS)
            or (path.startswith("bots/") and path.split("/")[1] in base_bots)
        ]
    if kind == "curator":
        return [
            f"{status} {path}"
            for status, path in changes
            if not (path == "ledger/iterations.md" and status == "M")
            and not (status == "D" and re.match(rf"^ledger/lessons/{RUN_FILE}$", path))
        ]
    bad = []
    for status, path in changes:
        if any(rule.match(path) for rule in ALLOWED):
            continue
        if status == "A" and (NEW_MAP.match(path) or NEW_DETECTOR.match(path) or NEW_DETECTOR_TEST.match(path)):
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


def already_public(names: set[str], base: str) -> set[str]:
    """The names that BASE's tracked files already hold as a whole word, in any case."""
    public = set()
    for name in names:
        found = subprocess.run(
            ["git", "grep", "-q", "-i", "-w", "-F", "-e", name, base, "--"],
            cwd=ROOT,
            capture_output=True,
        )
        if found.returncode == 0:
            public.add(name)
    return public


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
    parser.add_argument("--kind", choices=KINDS, default="iteration")
    parser.add_argument("--names-from", type=Path)
    parser.add_argument("--also", type=Path, nargs="*", default=[], help="more files to check for names (a PR body)")
    args = parser.parse_args(argv)

    lines = _git("diff", "--name-status", "--no-renames", f"{args.base}...{args.head}").splitlines()
    changes = [(line.split("\t")[0][0], line.split("\t")[-1]) for line in lines if line.strip()]
    if not changes:
        print("the iteration changed nothing", file=sys.stderr)
        return 1
    failed = False
    listed = _git("ls-tree", "-d", "--name-only", args.base, "bots/").splitlines()
    base_bots = {line.split("/", 1)[1] for line in listed if "/" in line}
    for change in out_of_scope(changes, args.kind, base_bots):
        print(f"out of a {args.kind}'s scope: {change}", file=sys.stderr)
        failed = True
    if args.names_from is not None:
        bots = {path.name.lower() for path in (ROOT / "bots").iterdir() if path.is_dir()}
        names = player_names(args.names_from, bots | {f"level{n}" for n in range(1, 4)})
        public = already_public(names, args.base)
        if public:
            print(f"{len(public)} of the {len(names)} names are words BASE already holds: not checked")
        names -= public
        added = added_lines(_git("diff", "--unified=0", f"{args.base}...{args.head}"))
        for path in args.also:
            added += [(str(path), n, text) for n, text in enumerate(path.read_text().splitlines(), 1)]
        for place in leaked(added, names):
            print(f"a real game's player name is on the added line {place}", file=sys.stderr)
            failed = True
    if not failed:
        print(f"{len(changes)} changed files, all in a {args.kind}'s scope")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
