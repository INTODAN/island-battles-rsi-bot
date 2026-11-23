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


# --- The integrator's own parts: collecting a run's branch, and what it writes --------------

import re  # noqa: E402
import subprocess  # noqa: E402

from league_tools import integrate  # noqa: E402


def _git(cwd: Path, *arguments: str) -> str:
    return subprocess.run(["git", *arguments], cwd=cwd, check=True, capture_output=True, text=True).stdout


def _repository(tmp_path: Path) -> Path:
    """A main with one bot and the lines, and a run's branch from it."""
    root = tmp_path / "league"
    (root / "bots" / "champion").mkdir(parents=True)
    (root / "bots" / "champion" / "main.go").write_text("package main\n")
    (root / "ledger").mkdir()
    (root / "ledger" / "lines.toml").write_text('champion = "champion"\n\n[[line]]\nname = "main"\nhead = "champion"\n')
    _git(root, "init", "-q", "-b", "main")
    _git(root, "-c", "user.name=t", "-c", "user.email=t@t", "add", "-A")
    _git(root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "base")
    return root


def _commit_run(root: Path, run: str, files: dict[str, str]) -> str:
    branch = f"claude/league-run-{run}"
    _git(root, "checkout", "-q", "-b", branch, "main")
    for path, text in files.items():
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_text(text)
    _git(root, "-c", "user.name=t", "-c", "user.email=t@t", "add", "-A")
    _git(root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", run)
    _git(root, "checkout", "-q", "main")
    return branch


def test_a_runs_branch_is_collected_with_its_candidates_maps_studies_and_the_heads_at_its_base(
    tmp_path: Path,
) -> None:
    root = _repository(tmp_path)
    branch = _commit_run(
        root,
        "20261124-aaaaaa",
        {
            "bots/champion_fix/main.go": "package main\n",
            "bots/champion_fix/bot.toml": 'status = "candidate"\n',
            "ledger/runs/20261124-aaaaaa.md": "Minutes: 21\n",
            "ledger/studies/481.md": "A study.\n",
            "maps/holdout/fjordtwo.json": "{}\n",
        },
    )
    proposal = integrate.collect(branch, cwd=root)

    assert isinstance(proposal, integrate.Proposal)
    assert proposal.run == "20261124-aaaaaa"
    assert proposal.candidates == ["champion_fix"]
    assert proposal.maps == ["holdout/fjordtwo"]
    assert proposal.real_games == ["481"]
    assert proposal.base_heads == {"main": "champion"}


def test_a_run_that_changes_a_bot_or_lacks_its_account_or_takes_a_name_is_skipped(tmp_path: Path) -> None:
    root = _repository(tmp_path)
    changes = _commit_run(root, "r-1", {"bots/champion/main.go": "package main // changed\n", "ledger/runs/r-1.md": ""})
    no_account = _commit_run(root, "r-2", {"bots/other/main.go": "package main\n"})
    late = _commit_run(root, "r-3", {"bots/late/main.go": "package main\n", "ledger/runs/r-3.md": ""})
    (root / "bots" / "late").mkdir()
    (root / "bots" / "late" / "main.go").write_text("package main\n")
    _git(root, "-c", "user.name=t", "-c", "user.email=t@t", "add", "-A")
    _git(root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "another run took late")

    assert "out of a run's scope: M bots/champion/main.go" in str(integrate.collect(changes, cwd=root))
    assert "no ledger/runs/r-2.md" in str(integrate.collect(no_account, cwd=root))
    assert "another run took the name first" in str(integrate.collect(late, cwd=root))
    assert "is not a run's branch" in str(integrate.collect("main", cwd=root))


def test_the_lines_table_is_replaced_and_the_words_around_it_kept() -> None:
    text = (
        "# Ledger\n\n## The lines\n\nWords.\n\n| Line | Head |\n|---|---|\n| `a` | x |\n\nAfter.\n\n## Lessons so far\n"
    )
    out = integrate.replace_lines_table(text, ["| Line | Head |", "|---|---|", "| `b` | y |"])
    assert "| `b` | y |" in out and "| `a` | x |" not in out
    assert "Words." in out and "After." in out and out.endswith("## Lessons so far\n")


def test_the_iterations_number_progress_row_minutes_and_real_games(tmp_path: Path) -> None:
    assert integrate.next_iteration(LEDGER) == 3
    summary = {"standings": [{"player": "champ", "rating": 2101}]}
    assert integrate.progress_row(40, "2026-11-24", "21", "champ", summary) == "40,2026-11-24,21,champ,2101,ori_mimic\n"
    run = tmp_path / "run.md"
    run.write_text("# Run\n\nMinutes: 18.5\n")
    assert integrate.run_minutes(run) == "18.5"
    assert integrate.run_minutes(tmp_path / "none.md") == ""
    games = tmp_path / "real-games.txt"
    games.write_text("# header\n471 2026-11-23\n")
    integrate.add_real_games(games, ["471", "481"], "2026-11-24")
    assert games.read_text() == "# header\n471 2026-11-23\n481 2026-11-24\n"


# --- The idea queue ---------------------------------------------------------------------------

from league_tools import ideas  # noqa: E402
from league_tools.lines import Line, Lines  # noqa: E402
from league_tools.mistakes import Row  # noqa: E402


def _lines() -> Lines:
    return Lines(
        champion="champ",
        lines=[
            Line(name="main", strategy="s", state="main", head="champ", bots=["champ", "other"]),
            Line(name="side", strategy="s", state="side", head="sidehead", bots=["sidehead"], without_promotion=1),
        ],
    )


def test_the_queue_puts_side_lines_then_the_exploiter_then_founders_then_grafts_mistakes_and_ideas(
    tmp_path: Path,
) -> None:
    summary = {"pairs": {"sidehead": {"champ": [5, 60]}, "other": {"champ": [30, 60]}}}
    rows = [
        Row("thin_border", games=21, maps={"a", "b", "c"}, points_lost=6.5),
        Row("home_emptied", games=7, maps={"a", "b"}, points_lost=7.0),
        Row("never", games=0),
    ]
    text = LEDGER + "\n**Ideas not tried:**\n- Keep one shared reserve.\n- Rank nearer neutrals first.\n\nAfter.\n"
    text += (
        "| Candidate | Parent | Idea | Decision |\n|---|---|---|---|\n| `x` | champ | Fix: y. | **superseded**: z |\n"
    )
    places = ideas.queue(_lines(), {"sidehead": "active"}, summary, rows, text, tmp_path, max_side_lines=4)

    kinds = [place.kind for place in places]
    assert kinds == ["side line", "exploiter", "founder", "founder", "founder", "graft", "fix", "fix", "idea", "idea"]
    assert places[0].key == "slot/champ/side-side"
    assert places[6].key.endswith("home_emptied")  # 2 maps x 7/7 lost beats 3 maps x 6.5/21
    assert places[8].what == "Rank nearer neutrals first."


def test_a_held_place_is_left_out_and_no_exploiter_while_someone_outside_tests_the_champion(tmp_path: Path) -> None:
    summary = {"pairs": {"sidehead": {"champ": [20, 60]}}}
    places = ideas.queue(
        _lines(), {"sidehead": "active"}, summary, [], "", tmp_path, max_side_lines=2, held={"slot/champ/side-side"}
    )
    assert [place.kind for place in places] == ["founder"]


# --- Leases on git refs -----------------------------------------------------------------------

from league_tools import leases  # noqa: E402


def _remote(tmp_path: Path) -> tuple[leases.GitRefs, leases.GitRefs]:
    """Two clones' lease backends on one bare remote."""
    remote = tmp_path / "remote.git"
    _git(tmp_path, "init", "-q", "--bare", str(remote))
    clones = []
    for name in ("a", "b"):
        clone = tmp_path / name
        _git(tmp_path, "init", "-q", str(clone))
        _git(clone, "remote", "add", "origin", str(remote))
        clones.append(leases.GitRefs(cwd=clone))
    return clones[0], clones[1]


def test_of_two_runs_one_takes_a_key_and_the_other_is_told_who_holds_it(tmp_path: Path) -> None:
    a, b = _remote(tmp_path)
    assert leases.take(a, "slot/champ/side-x", "run-a").run == "run-a"
    held = leases.take(b, "slot/champ/side-x", "run-b")
    assert held.run == "run-a"
    assert [lease.key for lease in leases.held(b, "slot/")] == ["slot/champ/side-x"]
    assert not leases.release(b, "slot/champ/side-x", "run-b")
    assert leases.release(a, "slot/champ/side-x", "run-a")
    assert leases.take(b, "slot/champ/side-x", "run-b").run == "run-b"


def test_an_expired_lease_is_taken_over_and_a_held_one_renewed(tmp_path: Path) -> None:
    a, b = _remote(tmp_path)
    leases.take(a, "idea/abc", "run-a", hours=-1)
    assert leases.held(b) == []
    assert leases.take(b, "idea/abc", "run-b").run == "run-b"
    assert leases.renew(b, "run-b") == ["idea/abc"]
    leases.take(b, "run/run-b", "run-b")
    assert leases.drop(a, "run-b") == ["idea/abc", "run/run-b"]
    assert leases.held(a) == []


def test_a_key_is_checked() -> None:
    assert leases.check_key("study/0123abcd") == "study/0123abcd"
    for bad in ("other/x", "slot/../x", "idea/", "idea/a b"):
        try:
            leases.check_key(bad)
        except ValueError:
            continue
        raise AssertionError(bad)
    assert re.match(r"^\d{8}-[0-9a-f]{6}$", leases.new_run_id())


def test_a_proposal_whose_files_are_withdrawn_leaves_the_tree_as_it_was(tmp_path: Path) -> None:
    root = _repository(tmp_path)
    branch = _commit_run(
        root, "r-9", {"bots/bad/main.go": "package main\n", "ledger/runs/r-9.md": "", "maps/train/new.json": "{}"}
    )
    proposal = integrate.collect(branch, cwd=root)
    assert isinstance(proposal, integrate.Proposal)
    integrate.bring(proposal, cwd=root)
    assert (root / "bots" / "bad" / "main.go").is_file()
    integrate.withdraw(proposal, cwd=root)
    assert not (root / "bots" / "bad").exists() and not (root / "maps" / "train" / "new.json").exists()
    assert _git(root, "status", "--porcelain") == ""
