"""Runs in parallel: the ledger's run files and proposed lessons, and the scope of a run's and the curator's branch."""

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "hosting" / "rsi"))

import scope  # noqa: E402

from league_tools import ledger  # noqa: E402

LEDGER = """# Ledger

## Lessons so far

- A lesson.

## Iteration 1: first

Run: ledger/runs/20261124-aaaaaa.md

| Candidate | Parent | Idea | Decision |
|---|---|---|---|
| `a` | p | Fix: hold. | **rejected** |

## Iteration 2: second

Run: ledger/runs/20261124-bbbbbb.md

| Candidate | Parent | Idea | Decision |
|---|---|---|---|
| `b` | p | Fix: strike. | **promoted** |
"""


def test_the_brief_prints_the_recent_entries_run_files_and_the_lessons_not_folded(tmp_path: Path) -> None:
    directory = tmp_path / "ledger"
    (directory / "runs").mkdir(parents=True)
    (directory / "lessons").mkdir()
    (directory / "iterations.md").write_text(LEDGER)
    (directory / "runs" / "20261124-aaaaaa.md").write_text("The first run's findings.\n")
    (directory / "runs" / "20261124-bbbbbb.md").write_text("The second run's findings.\n")
    (directory / "lessons" / "20261124-bbbbbb.md").write_text("- A group that lands after a burst loses.\n")

    brief = ledger.load(directory / "iterations.md", recent=1)

    assert "The second run's findings." in brief
    assert "The first run's findings." not in brief
    assert "### Run 20261124-bbbbbb" in brief and "lands after a burst" in brief
    assert ledger.run_files(LEDGER, recent=2) == ["ledger/runs/20261124-aaaaaa.md", "ledger/runs/20261124-bbbbbb.md"]


def test_a_ledger_without_runs_or_lessons_prints_as_before(tmp_path: Path) -> None:
    path = tmp_path / "iterations.md"
    path.write_text("# Ledger\n\n## Lessons so far\n\n- A lesson.\n\n## Iteration 1: first\n\nText.\n")
    assert ledger.load(path) == ledger.brief(path.read_text())


def test_a_run_only_adds_its_candidates_its_files_maps_and_detectors() -> None:
    allowed = [
        ("A", "bots/new_fix/main.go"),
        ("A", "bots/new_fix/bot.toml"),
        ("A", "ledger/runs/20261124-aaaaaa.md"),
        ("A", "ledger/lessons/20261124-aaaaaa.md"),
        ("A", "ledger/studies/481.md"),
        ("A", "maps/holdout/fjord.json"),
        ("A", "league_tools/detectors/late_strike.py"),
        ("A", "tests/detectors/test_late_strike.py"),
    ]
    assert scope.out_of_scope(allowed, "run", {"champion"}) == []


def test_a_run_changes_and_deletes_nothing() -> None:
    refused = [
        ("M", "bots/champion/bot.toml"),
        ("A", "bots/champion/extra.go"),
        ("D", "bots/old/main.go"),
        ("M", "ledger/iterations.md"),
        ("A", "ledger/lines.toml"),
        ("M", "league_tools/detectors/turning_point.py"),
        ("A", "league_tools/tournament_extra.py"),
        ("M", "maps/train/claw.json"),
        ("A", "hosting/lambda/bot"),
    ]
    assert scope.out_of_scope(refused, "run", {"champion", "old"}) == [f"{s} {p}" for s, p in refused]


def test_the_integrator_may_write_the_lines_and_carry_the_runs_files() -> None:
    allowed = [
        ("M", "ledger/lines.toml"),
        ("A", "ledger/runs/20261124-aaaaaa.md"),
        ("A", "ledger/lessons/20261124-aaaaaa.md"),
        ("M", "bots/champion/bot.toml"),
    ]
    assert scope.out_of_scope(allowed) == []


def test_the_curator_folds_lessons_and_nothing_else() -> None:
    assert scope.out_of_scope([("M", "ledger/iterations.md"), ("D", "ledger/lessons/x-1.md")], "curator") == []
    refused = [("A", "ledger/lessons/x-1.md"), ("M", "bots/a/main.go"), ("D", "ledger/iterations.md")]
    assert scope.out_of_scope(refused, "curator") == [f"{s} {p}" for s, p in refused]
