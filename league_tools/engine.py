"""Build and run the game's headless match runner.

The runner is a command of the game's own repository (``backend/cmd/headless-match``
of INTODAN/island-battles-go), which plays whole games in memory with the
server's rules. The league builds it from the commit that ``runner.toml`` names.
"""

from __future__ import annotations

import contextlib
import fcntl
import hashlib
import json
import os
import subprocess
import sys
import tomllib
from collections.abc import Generator, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .paths import RUNNER, RUNNER_PIN, RUNNER_SOURCE

# A checkout of the game's repository to build the runner from, instead of the
# pinned commit: for trying a change of the runner or the rules before it is merged.
LOCAL_SOURCE_VARIABLE = "ISLAND_BATTLES_GO"


def pin() -> tuple[str, str]:
    """The game's repository and the commit of it that the league plays, from ``runner.toml``."""
    document = tomllib.loads(RUNNER_PIN.read_text(encoding="utf-8"))
    return document["repository"], document["commit"]


def _git(directory: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(directory), *arguments], check=False, capture_output=True, text=True)


def source() -> Path:
    """The directory of the game's source to build from, fetching the pinned commit when it isn't there yet.

    Raises:
        RuntimeError: The pinned commit couldn't be fetched.
    """
    local = os.environ.get(LOCAL_SOURCE_VARIABLE)
    if local:
        return Path(local).expanduser().resolve()
    repository, commit = pin()
    if _git(RUNNER_SOURCE, "rev-parse", "HEAD").stdout.strip() == commit:
        return RUNNER_SOURCE
    RUNNER_SOURCE.mkdir(parents=True, exist_ok=True)
    for arguments in (
        ["init", "--quiet"],
        ["fetch", "--quiet", "--depth", "1", repository, commit],
        ["checkout", "--quiet", "--detach", "FETCH_HEAD"],
    ):
        step = _git(RUNNER_SOURCE, *arguments)
        if step.returncode != 0:
            raise RuntimeError(f"couldn't fetch commit {commit} of {repository}: {step.stderr.strip()}")
    return RUNNER_SOURCE


@contextlib.contextmanager
def exclusive(lock_file: Path, waiting: str = "") -> Generator[None]:
    """Hold a lock that one process at a time may hold, across checkouts.

    The lock goes when the process does, so a crashed holder never blocks
    the next one.

    Args:
        lock_file: The file whose lock it is.
        waiting: Printed when another process holds the lock.
    """
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    with lock_file.open("a") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            if waiting:
                print(waiting, file=sys.stderr, flush=True)
            fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


@dataclass(frozen=True)
class Build:
    """A build of the runner: the hash that names it and the binary to run."""

    hash: str
    binary: Path


def build() -> Build:
    """Build the runner, and return the build.

    Go rebuilds only what changed, so this takes a moment when nothing did.
    The hash changes whenever the rules or the runner do, which is what makes
    a cached result stale. The binary's file is named by its hash, so another
    checkout that builds another commit meanwhile can't change what this
    tournament runs.

    Raises:
        RuntimeError: The game's source couldn't be fetched, or the runner didn't build.
    """
    with exclusive(RUNNER / "build.lock", "league: waiting for another checkout's build of the runner"):
        output = RUNNER / f"headless-match.{os.getpid()}"
        # Without the commit's stamp and the build's paths, the same sources give
        # the same binary in every checkout, so the cache survives them.
        built = subprocess.run(
            ["go", "build", "-buildvcs=false", "-trimpath", "-o", str(output), "./backend/cmd/headless-match"],
            cwd=source(),
            check=False,
        )
        if built.returncode != 0:
            output.unlink(missing_ok=True)
            raise RuntimeError("the headless runner didn't build; see the compiler's messages above")
        digest = hashlib.sha256(output.read_bytes()).hexdigest()
        binary = RUNNER / f"headless-match-{digest[:16]}"
        os.replace(output, binary)
    return Build(hash=digest, binary=binary)


def play(binary: Path, schedule: dict[str, Any], worker_log: Path) -> Iterator[dict[str, Any]]:
    """Play a schedule, and yield each match's line as it ends.

    Args:
        binary: The runner to play it with, from ``build``.
        schedule: The runner's schedule document.
        worker_log: Where the bots' own stderr goes.

    Raises:
        RuntimeError: The runner refused the schedule or stopped early.
    """
    worker_log.parent.mkdir(parents=True, exist_ok=True)
    with worker_log.open("ab") as errors:
        process = subprocess.Popen(
            [str(binary)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=errors,
            text=True,
            encoding="utf-8",
        )
        assert process.stdin is not None and process.stdout is not None
        process.stdin.write(json.dumps(schedule))
        process.stdin.close()
        for line in process.stdout:
            if line.strip():
                yield json.loads(line)
        if process.wait() != 0:
            tail = worker_log.read_text(encoding="utf-8", errors="replace")[-2000:]
            raise RuntimeError(f"headless-match stopped with status {process.returncode}:\n{tail}")
