"""The ledger as an iteration starts from it: the lessons, every idea tried, and the last entries whole.

``ledger/iterations.md`` grows by an entry every iteration, and most of an old
entry (its standings, its pair tables) is history that the next iteration
doesn't need. What it does need from all of them is in the lessons and in the
candidate tables: which ideas were tried, on which parent, and why each was
promoted or rejected. This prints those, and the last entries in full.

Since runs work in parallel (docs/parallel-iterations.md), an iteration's entry
is written by the integrator, and the run's own account (its findings, its
slate, its review of the league) is ``ledger/runs/<run id>.md``, which the entry
names on a line ``Run: ledger/runs/<id>.md``. A run proposes lessons in
``ledger/lessons/<run id>.md`` instead of editing the ledger's top; the curator
folds them into **Lessons so far** and deletes the files. The brief prints the
recent entries' run files and every lesson not folded yet.
"""

from __future__ import annotations

import re
from pathlib import Path

LESSONS = "## Lessons so far"
ITERATION = re.compile(r"^## Iteration (\d+)\b")
CANDIDATE_TABLE = re.compile(r"^\| Candidate \|")
RUN_LINE = re.compile(r"^Run: (ledger/runs/[A-Za-z0-9_.-]+\.md)\s*$", re.MULTILINE)


def _cells(row: str) -> list[str]:
    return [cell.strip() for cell in row.strip().strip("|").split("|")]


def candidates(text: str) -> list[str]:
    """One line for every candidate in the ledger's candidate tables, oldest first."""
    lines = []
    iteration = ""
    header: list[str] | None = None
    for row in text.splitlines():
        match = ITERATION.match(row)
        if match:
            iteration = match.group(1)
        if CANDIDATE_TABLE.match(row):
            header = _cells(row)
            continue
        if header is None:
            continue
        if not row.startswith("|"):
            header = None
            continue
        cells = _cells(row)
        if len(cells) != len(header) or set(cells[0]) <= {"-"}:
            continue
        column = dict(zip(header, cells, strict=True))
        numbers = [
            f"{name.split(' (')[0].lower()} {column[name]}"
            for name in header
            if name not in ("Candidate", "Parent", "Idea", "Decision") and column[name]
        ]
        lines.append(
            f"- {iteration}: {column['Candidate']} from {column.get('Parent', '?')}: {column.get('Idea', '')} "
            f"({'; '.join(numbers)}) {column.get('Decision', '')}"
        )
    return lines


def brief(text: str, recent: int = 3) -> str:
    """The lessons, a line for every candidate ever tried, and the last ``recent`` iterations whole.

    The entries between the last iterations (a change of the league's setup) come whole too.
    """
    lines = text.splitlines()
    sections = [index for index, line in enumerate(lines) if line.startswith("## ")]
    lessons = next((index for index in sections if lines[index].startswith(LESSONS)), None)
    iterations = [index for index in sections if ITERATION.match(lines[index])]
    start = iterations[-recent] if len(iterations) >= recent else (iterations[0] if iterations else len(lines))
    head_end = next((index for index in sections if lessons is not None and index > lessons), start)
    earlier = [lines[index][3:] for index in sections if head_end <= index < start]
    out = lines[:head_end]
    out += ["", "## Every candidate tried (from the entries' candidate tables)", "", *candidates(text)]
    if earlier:
        out += ["", "## The earlier entries (`grep` ledger/iterations.md for one in full)", ""]
        out += [f"- {title}" for title in earlier]
    out += ["", *lines[start:]]
    return "\n".join(out) + "\n"


def run_files(text: str, recent: int = 3) -> list[str]:
    """The run files that the last ``recent`` iterations' entries name, oldest first."""
    lines = text.splitlines()
    starts = [index for index, line in enumerate(lines) if ITERATION.match(line)]
    if not starts:
        return []
    tail = "\n".join(lines[starts[-recent] if len(starts) >= recent else starts[0] :])
    return list(dict.fromkeys(RUN_LINE.findall(tail)))


def proposed_lessons(directory: Path) -> list[tuple[str, str]]:
    """The lessons runs proposed and the curator hasn't folded yet, as (run id, text), by run id."""
    folder = directory / "lessons"
    if not folder.is_dir():
        return []
    return [(path.stem, path.read_text(encoding="utf-8").strip()) for path in sorted(folder.glob("*.md"))]


def load(path: Path, recent: int = 3) -> str:
    """``brief`` of the ledger file, with the recent entries' run files and the lessons not folded yet."""
    text = path.read_text(encoding="utf-8")
    out = brief(text, recent)
    root = path.parent.parent
    runs = [(name, root / name) for name in run_files(text, recent)]
    if runs:
        out += "\n## The runs of the last entries\n"
        for name, run in runs:
            body = run.read_text(encoding="utf-8").strip() if run.is_file() else "(missing)"
            out += f"\n### {name}\n\n{body}\n"
    lessons = proposed_lessons(path.parent)
    if lessons:
        out += "\n## Lessons proposed by runs, not folded into Lessons so far yet\n"
        for run_id, body in lessons:
            out += f"\n### Run {run_id}\n\n{body}\n"
    return out
