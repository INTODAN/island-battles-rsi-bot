"""scripts/claim-iteration.sh: one iteration at a time, claimed on the remote."""

import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "scripts" / "claim-iteration.sh"
LEDGER = (
    "# Ledger\n\n## Iteration 7: something\n\n## Iteration 8: the last one\n\n## Iterations 1 to 8, in one container\n"
)


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def _claim(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([str(SCRIPT), *args], cwd=cwd, capture_output=True, text=True)


@pytest.fixture
def clones(tmp_path: Path) -> tuple[Path, Path]:
    """Two sessions' clones of one remote whose main's ledger ends at iteration 8."""
    seed = tmp_path / "seed"
    (seed / "ledger").mkdir(parents=True)
    (seed / "ledger" / "iterations.md").write_text(LEDGER)
    _git(tmp_path, "init", "-q", "-b", "main", str(seed))
    for key, value in (("user.name", "test"), ("user.email", "test@example.com")):
        _git(seed, "config", key, value)
    _git(seed, "add", "-A")
    _git(seed, "commit", "-q", "-m", "seed")
    _git(tmp_path, "clone", "-q", "--bare", str(seed), str(tmp_path / "remote.git"))
    sessions = []
    for name in ("a", "b"):
        _git(tmp_path, "clone", "-q", str(tmp_path / "remote.git"), name)
        for key, value in (("user.name", name), ("user.email", f"{name}@example.com")):
            _git(tmp_path / name, "config", key, value)
        sessions.append(tmp_path / name)
    return sessions[0], sessions[1]


def test_only_one_session_claims_a_number(clones: tuple[Path, Path]) -> None:
    a, b = clones
    assert _claim(a, "status").returncode == 0
    first = _claim(a, "claim", "--by", "session a")
    assert first.returncode == 0, first.stderr
    number, claim = first.stdout.split()
    assert number == "9"
    # The claim is an empty commit on main: it pushes no work.
    assert _git(a, "rev-parse", f"{claim}^") == _git(a, "rev-parse", "origin/main")
    assert _git(a, "rev-parse", f"{claim}^{{tree}}") == _git(a, "rev-parse", "origin/main^{tree}")

    second = _claim(b, "claim")
    assert second.returncode == 2
    assert "session a" in second.stderr
    assert _claim(b, "status").returncode == 2


def test_a_claim_is_released_only_by_its_holder(clones: tuple[Path, Path]) -> None:
    a, b = clones
    number, claim = _claim(a, "claim").stdout.split()
    assert _claim(b, "release", number, "0" * 40).returncode != 0
    assert _claim(a, "release", number, claim).returncode == 0
    assert _claim(b, "claim").returncode == 0


def test_the_iteration_replaces_its_claim(clones: tuple[Path, Path]) -> None:
    a, b = clones
    number, claim = _claim(a, "claim").stdout.split()
    ledger = a / "ledger" / "iterations.md"
    ledger.write_text(LEDGER + f"\n## Iteration {number}: done\n")
    _git(a, "commit", "-q", "-am", f"League iteration {number}")
    ref = f"refs/heads/claude/league-iteration-{number}"
    _git(a, "push", "-q", f"--force-with-lease={ref}:{claim}", "origin", f"HEAD:{ref}")
    # The claim is gone, so it can't be released any more: the pull request holds the number.
    assert _claim(a, "release", number, claim).returncode != 0

    # Going on from the unmerged iteration claims the next number; from main, it is still taken.
    chained = _claim(a, "claim", "--base", "HEAD")
    assert chained.returncode == 0, chained.stderr
    assert chained.stdout.split()[0] == str(int(number) + 1)
    assert _claim(b, "claim").returncode == 2
