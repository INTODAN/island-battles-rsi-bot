"""The integrator: runs' proposals become iterations, one after another, on main as it is now.

A run (docs/parallel-iterations.md) works from the main it started on, its
base, and ends as a proposal on its branch ``claude/league-run-<id>``: new
candidates, its account ``ledger/runs/<id>.md``, the lessons it proposes, the
studies of the real games it read, new maps and new detectors. It decides
nothing that changes the population. The integrator does, in this order, for
every proposal waiting:

1. **Collect.** The branch only adds what a run may add (``scope.py --kind run``)
   and nothing that main already has under the same name; else it is refused,
   with the reason. Its files are brought into the working tree.
2. **Decide**, the oldest base first: the selection's runs with the proposal's
   candidates (``decide.play_selection``), each judged against its parent and,
   when its line's head moved since the run's base, against the head
   (``superseded`` when it beats its parent and not the head); then the
   population's upkeep. A candidate the rules leave undecided is deleted, with
   the reason: a run can write it again.
3. **Record** iteration N: its entry in ``ledger/iterations.md`` (the decisions,
   the upkeep, the standings on both sets of maps, a ``Run:`` line naming the
   run's file), the table **The lines**, ``ledger/lines.toml``, the row of
   ``ledger/progress.csv``, the studied real games and ``hosting/lambda/bot``.
4. **Commit** the iteration, one commit each, when asked.

Every match comes from the cache or the store, or is played once: the
candidates against what entered main since their base, and everyone on the maps
other runs added. No model runs here; the rules are ``league_tools/decide.py``.
"""

from __future__ import annotations

import datetime
import re
import subprocess
import sys
import tomllib
from collections.abc import Callable, Collection, Iterable
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType
from typing import Any

from . import decide as decide_module
from . import lines as lines_module
from . import roster as roster_module
from .ledger import ITERATION
from .paths import BOTS, LEAGUE, LEDGER

BRANCH_PREFIX = "claude/league-run-"
RUN_ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")
MINUTES = re.compile(r"^Minutes:\s*([0-9]+(?:\.[0-9]+)?)\s*$", re.MULTILINE)
LINES_HEADING = "## The lines"
LESSONS_HEADING = "## Lessons so far"


def _scope() -> ModuleType:
    """hosting/rsi/scope.py, imported when the integrator needs it (a Lambda player's image has no hosting/)."""
    sys.path.insert(0, str(LEAGUE / "hosting" / "rsi"))
    import scope

    return scope


def _git(*arguments: str, cwd: Path = LEAGUE) -> str:
    return subprocess.run(["git", *arguments], cwd=cwd, check=True, capture_output=True, text=True).stdout


@dataclass
class Proposal:
    """A run's proposal, as its branch holds it."""

    run: str
    branch: str
    base: str
    base_time: int
    added: list[str]
    base_heads: dict[str, str] = field(default_factory=dict)

    @property
    def candidates(self) -> list[str]:
        """The bots the run added: its candidates, in name order."""
        return sorted({path.split("/")[1] for path in self.added if path.startswith("bots/")})

    @property
    def maps(self) -> list[str]:
        """The maps the run added, as ``set/name``."""
        return sorted(
            path.removeprefix("maps/").removesuffix(".json") for path in self.added if path.startswith("maps/")
        )

    @property
    def real_games(self) -> list[str]:
        """The ids of the real games the run studied."""
        return sorted(
            Path(path).stem for path in self.added if path.startswith("ledger/studies/") and path.endswith(".md")
        )


def run_of(branch: str) -> str:
    """A run's id from its branch's name.

    Raises:
        ValueError: The branch is not a run's.
    """
    name = branch.removeprefix("origin/").removeprefix("refs/remotes/origin/")
    run = name.removeprefix(BRANCH_PREFIX)
    if not name.startswith(BRANCH_PREFIX) or not RUN_ID.match(run):
        raise ValueError(f"{branch!r} is not a run's branch ({BRANCH_PREFIX}<id>)")
    return run


def _heads(lines_text: str) -> dict[str, str]:
    """Each line's head, from a lines file's text."""
    data = tomllib.loads(lines_text)
    return {line["name"]: line.get("head", "") for line in data.get("line", [])}


def collect(branch: str, cwd: Path = LEAGUE) -> Proposal | str:
    """The proposal on a run's branch, or why it can't be integrated.

    It may add only what a run adds, nothing that main (HEAD) already has, and
    it must have its account ``ledger/runs/<id>.md``.
    """
    try:
        run = run_of(branch)
    except ValueError as error:
        return str(error)
    base = _git("merge-base", "HEAD", branch, cwd=cwd).strip()
    lines = _git("diff", "--name-status", "--no-renames", f"{base}...{branch}", cwd=cwd).splitlines()
    changes = [(line.split("\t")[0][0], line.split("\t")[-1]) for line in lines if line.strip()]
    listed = _git("ls-tree", "-d", "--name-only", base, "bots/", cwd=cwd).splitlines()
    base_bots = {line.split("/", 1)[1] for line in listed if "/" in line}
    scope = _scope()
    bad = scope.out_of_scope(changes, "run", base_bots)
    if bad:
        return f"run {run}: out of a run's scope: {', '.join(bad)}"
    for _, path in changes:
        problems = scope.impure(path, _git("show", f"{branch}:{path}", cwd=cwd)) if path.endswith(".py") else []
        if problems:
            return f"run {run}: {path} breaks the detectors' rules: {', '.join(problems)}"
    added = [path for _, path in changes]
    if f"ledger/runs/{run}.md" not in added:
        return f"run {run}: no ledger/runs/{run}.md, the run's account"
    taken = [path for path in added if (cwd / path).exists()]
    if taken:
        return f"run {run}: main already has {', '.join(taken)}: another run took the name first"
    try:
        lines_text = _git("show", f"{base}:ledger/lines.toml", cwd=cwd)
    except subprocess.CalledProcessError:
        lines_text = ""
    base_time = int(_git("show", "-s", "--format=%ct", base, cwd=cwd).strip())
    return Proposal(run, branch, base, base_time, added, _heads(lines_text) if lines_text else {})


def bring(proposal: Proposal, cwd: Path = LEAGUE) -> None:
    """Bring a proposal's files into the working tree."""
    _git("checkout", proposal.branch, "--", *proposal.added, cwd=cwd)


def verify(proposal: Proposal, cwd: Path = LEAGUE) -> str | None:
    """Why the proposal's code may not run here, or None: the bots' checks, and the detectors' tests, pass with it in.

    A bot is untrusted code: the checks hold it to pure standard packages (no
    file, network or clock) before it plays on a machine that writes the store.
    A detector and its test were already read for the same rules (``collect``),
    so running their tests runs only pure code; a detector whose test fails
    would fail ``scripts/check.sh`` after the batch, and every proposal with it.
    """
    if proposal.candidates:
        checked = subprocess.run(["go", "test", "./tests/..."], cwd=cwd, capture_output=True, text=True)
        if checked.returncode != 0:
            return f"run {proposal.run}: the bots' checks fail with its candidates: {checked.stdout[-2000:]}"
    if any(path.endswith(".py") for path in proposal.added):
        tests = ["tests/test_detectors.py"] + [path for path in proposal.added if path.startswith("tests/detectors/")]
        checked = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *tests],
            cwd=cwd,
            capture_output=True,
            text=True,
        )
        if checked.returncode != 0:
            return f"run {proposal.run}: the detectors' tests fail with its detectors: {checked.stdout[-2000:]}"
    return None


def withdraw(proposal: Proposal, cwd: Path = LEAGUE) -> None:
    """Take a proposal's files out of the working tree again."""
    _git("rm", "-q", "-r", "-f", "--cached", "--ignore-unmatch", "--", *proposal.added, cwd=cwd)
    for path in proposal.added:
        (cwd / path).unlink(missing_ok=True)
    for name in proposal.candidates:
        directory = cwd / "bots" / name
        if directory.is_dir() and not any(directory.iterdir()):
            directory.rmdir()


def next_iteration(ledger_text: str) -> int:
    """One more than the ledger's last ``## Iteration N``."""
    found = [ITERATION.match(line) for line in ledger_text.splitlines()]
    return max((int(match.group(1)) for match in found if match), default=0) + 1


def replace_lines_table(ledger_text: str, table: list[str]) -> str:
    """The ledger with the table under **The lines** replaced, its words around it kept."""
    rows = ledger_text.split("\n")
    try:
        start = next(index for index, row in enumerate(rows) if row.startswith(LINES_HEADING))
    except StopIteration:
        return ledger_text
    end = next((index for index in range(start + 1, len(rows)) if rows[index].startswith("## ")), len(rows))
    first = next((index for index in range(start, end) if rows[index].startswith("|")), None)
    if first is None:
        return "\n".join([*rows[:end], *table, "", *rows[end:]])
    last = first
    while last + 1 < end and rows[last + 1].startswith("|"):
        last += 1
    return "\n".join([*rows[:first], *table, *rows[last + 1 :]])


def standings_table(summary: dict[str, Any] | None) -> list[str]:
    """A summary's standings as a short Markdown table."""
    if not summary or not summary.get("standings"):
        return ["Not played."]
    rows = ["| Player | Rating | Score | Wins | Draws | Losses |", "|---|---|---|---|---|---|"]
    for row in summary["standings"]:
        rows.append(
            f"| `{row['player']}` | {row['rating']} | {row['score']:.3f} | {row['wins']} | {row['draws']} | "
            f"{row['losses']} |"
        )
    return rows


def entry(
    iteration: int,
    proposal: Proposal,
    date: str,
    selection: decide_module.Selection,
    upkeep: decide_module.Upkeep,
    holdout: dict[str, Any] | None,
    undecided: Iterable[str],
    champion_before: str,
) -> str:
    """Iteration N's entry in the ledger."""
    decisions = selection.decisions
    promoted = [d.candidate.name for d in decisions if d.decision in ("promoted", "admitted")]
    title = f"promoted {', '.join(promoted)}" if promoted else "nothing promoted"
    out = [
        f"## Iteration {iteration}: run {proposal.run}, {title}",
        "",
        f"Run: ledger/runs/{proposal.run}.md",
        "",
        f"Integrated on {date} by `league integrate`, from the run's base `{proposal.base[:12]}`. "
        f"Maps the run added: {', '.join(proposal.maps) or 'none'}. "
        f"Real games it studied: {', '.join(proposal.real_games) or 'none'}.",
        "",
        "### Decisions",
        "",
        *(decide_module.decisions_table(decisions) or ["The run proposed no candidate."]),
    ]
    left = list(undecided)
    if left:
        out += ["", f"Left undecided by the rules and deleted, for a run to write again: {', '.join(left)}."]
    out += ["", "### The population's upkeep", "", *(decide_module.actions_list(upkeep.actions) or ["No actions."])]
    champion = upkeep.lines.champion
    if champion != champion_before:
        out += ["", f"**The champion is now `{champion}`**, was `{champion_before}`."]
    else:
        out += ["", f"The champion stays `{champion}`."]
    out += ["", "### Standings on the training maps", "", *standings_table(upkeep.final)]
    out += ["", "### Standings on the holdout maps", "", *standings_table(holdout)]
    return "\n".join(out) + "\n"


def progress_row(iteration: int, date: str, minutes: str, champion: str, summary: dict[str, Any] | None) -> str:
    """The iteration's row of ``ledger/progress.csv``."""
    rating = ""
    for row in (summary or {}).get("standings", []):
        if row["player"] == champion:
            rating = str(row["rating"])
    return f"{iteration},{date},{minutes},{champion},{rating},ori_mimic\n"


def run_minutes(run_file: Path) -> str:
    """The run's time in minutes, from its account's ``Minutes:`` line; empty when it has none."""
    if not run_file.is_file():
        return ""
    found = MINUTES.search(run_file.read_text(encoding="utf-8"))
    return found.group(1) if found else ""


def add_real_games(path: Path, ids: Collection[str], date: str) -> None:
    """List the real games a run studied, once each."""
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    listed = {line.split()[0] for line in text.splitlines() if line.strip() and not line.startswith("#")}
    new = [game for game in ids if game not in listed]
    if new:
        path.write_text(text + "".join(f"{game} {date}\n" for game in new), encoding="utf-8")


@dataclass
class Outcome:
    """What integrating one proposal did."""

    run: str
    iteration: int | None
    summary: str


def integrate_one(
    proposal: Proposal,
    iteration: int,
    date: str,
    commit: Callable[[str], None] | None = None,
) -> Outcome:
    """Decide a proposal's candidates on main as it is now, apply the upkeep and record iteration N.

    The proposal's files must already be in the working tree (``bring``).
    """
    prefix = f"iteration-{iteration}-integrate"
    lines_before = lines_module.load_lines()
    champion_before = lines_before.champion
    candidates = [name for name in proposal.candidates if roster_module.load_bot(name).status == "candidate"]
    base_heads = proposal.base_heads or {line.name: line.head for line in lines_before.lines}
    selection = decide_module.play_selection(candidates, prefix, base_heads=base_heads)
    measure = decide_module.measurer(selection.outside, prefix)
    result = decide_module.upkeep(
        selection.decisions,
        selection.lines,
        list(selection.roster.values()),
        measure,
        iteration,
        train=selection.evidence.train,
        outside=selection.outside,
    )
    decide_module.apply(result)
    undecided = [name for name in candidates if (BOTS / name).is_dir()]
    undecided = [name for name in undecided if roster_module.load_bot(name).status == "candidate"]
    for name in undecided:
        roster_module.delete_bot(name)
    population = [bot.name for bot in roster_module.load_roster() if bot.status != "candidate"]
    holdout = measure(population, "holdout")
    ledger_path = LEDGER / "iterations.md"
    text = ledger_path.read_text(encoding="utf-8")
    statuses = {bot.name: bot.status for bot in roster_module.load_roster()}
    text = replace_lines_table(text, lines_module.table(result.lines, statuses))
    text = (
        text.rstrip("\n")
        + "\n\n"
        + entry(iteration, proposal, date, selection, result, holdout, undecided, champion_before)
    )
    ledger_path.write_text(text, encoding="utf-8")
    champion = result.lines.champion
    with (LEDGER / "progress.csv").open("a", encoding="utf-8") as file:
        file.write(
            progress_row(iteration, date, run_minutes(LEDGER / "runs" / f"{proposal.run}.md"), champion, result.final)
        )
    add_real_games(LEDGER / "real-games.txt", proposal.real_games, date)
    decided = ", ".join(f"{d.candidate.name} {d.decision}" for d in selection.decisions) or "no candidate"
    summary = f"League iteration {iteration}: run {proposal.run}: {decided}"
    if commit is not None:
        commit(summary)
    return Outcome(proposal.run, iteration, summary)


def integrate(branches: Iterable[str], commit: bool = False, date: str | None = None) -> list[Outcome]:
    """Integrate every run's branch that can be, the oldest base first, each as one iteration.

    A proposal that can't be integrated is **refused** (out of a run's scope, a
    name main has, checks that fail with it: it never will be) or has **failed**
    (an error while deciding it, which may pass next time); either way the
    others go on. With ``commit``, a failed proposal's changes are undone.
    """
    today = date or datetime.datetime.now(datetime.UTC).date().isoformat()
    outcomes: list[Outcome] = []
    proposals: list[Proposal] = []
    for branch in branches:
        found = collect(branch)
        if isinstance(found, str):
            try:
                run = run_of(branch)
            except ValueError:
                outcomes.append(Outcome(branch, None, f"skipped: {found}"))
                continue
            outcomes.append(Outcome(run, None, f"refused {run}: {found}"))
        else:
            proposals.append(found)
    proposals.sort(key=lambda proposal: (proposal.base_time, proposal.run))

    def committer(message: str) -> None:
        _git("add", "-A", "bots", "ledger", "maps", "hosting/lambda/bot", "league_tools/detectors", "tests")
        _git("commit", "-q", "-m", message)

    for proposal in proposals:
        taken = [path for path in proposal.added if (LEAGUE / path).exists()]
        if taken:
            outcomes.append(Outcome(proposal.run, None, f"refused {proposal.run}: an earlier run took {taken[0]}"))
            continue
        bring(proposal)
        refused = verify(proposal)
        if refused is not None:
            withdraw(proposal)
            outcomes.append(Outcome(proposal.run, None, f"refused {proposal.run}: {refused}"))
            continue
        iteration = next_iteration((LEDGER / "iterations.md").read_text(encoding="utf-8"))
        try:
            outcomes.append(integrate_one(proposal, iteration, today, committer if commit else None))
        except Exception as error:  # One proposal that fails must not stop the others.
            if not commit:
                raise
            restore()
            outcomes.append(Outcome(proposal.run, None, f"failed {proposal.run}: {type(error).__name__}: {error}"))
    return outcomes


def restore(cwd: Path = LEAGUE) -> None:
    """Put the paths an iteration writes back as the last commit has them: a proposal that failed leaves nothing."""
    paths = ["bots", "ledger", "maps", "hosting/lambda/bot", "league_tools/detectors", "tests"]
    _git("reset", "-q", "--", *paths, cwd=cwd)
    tracked = [path for path in paths if _git("ls-tree", "HEAD", "--", path, cwd=cwd).strip()]
    if tracked:
        _git("checkout", "-q", "HEAD", "--", *tracked, cwd=cwd)
    _git("clean", "-fdq", "--", *paths, cwd=cwd)


def waiting_branches(remote: str = "origin") -> list[str]:
    """The runs' branches on the remote, as ``remote/claude/league-run-<id>``."""
    _git("fetch", "-q", remote, f"+refs/heads/{BRANCH_PREFIX}*:refs/remotes/{remote}/{BRANCH_PREFIX}*")
    listed = _git("for-each-ref", "--format=%(refname:short)", f"refs/remotes/{remote}/{BRANCH_PREFIX}*")
    return [line for line in listed.splitlines() if line.strip()]
