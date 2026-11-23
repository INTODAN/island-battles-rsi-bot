"""Build the league's Go bots, and play turns through a bot's worker.

Every bot is a Go program, ``bots/<name>/main.go`` and any other ``.go`` files
of its own, in the repository's one Go module (``go.mod``), which pins the
game's Go SDK. The SDK's ``worker`` subcommand plays turns over stdin and
stdout, in the JSON Lines protocol the headless runner speaks to it.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
from collections.abc import Iterable
from pathlib import Path
from types import TracebackType
from typing import Any, Self

from .paths import BINARIES, BOTS, LEAGUE
from .roster import fingerprint as code_fingerprint

# The Go SDK's module, which go.mod requires at one version.
SDK_MODULE = "github.com/INTODAN/island-battles-go/clients/island-battles-go"


def sdk_version() -> str:
    """The version of the Go SDK that go.mod requires.

    Raises:
        RuntimeError: go.mod doesn't require the SDK.
    """
    text = (LEAGUE / "go.mod").read_text(encoding="utf-8")
    found = re.search(rf"^\s*(?:require\s+)?{re.escape(SDK_MODULE)}\s+(\S+)", text, re.MULTILINE)
    if not found:
        raise RuntimeError(f"go.mod doesn't require {SDK_MODULE}")
    return found.group(1)


def fingerprint(directory: Path) -> str:
    """A hash of a bot's Go code and the SDK's version: what decides how it plays."""
    return hashlib.sha256(f"{SDK_MODULE} {sdk_version()} {code_fingerprint(directory)}".encode()).hexdigest()


def binary_path(name: str) -> Path:
    """Where the binary of a bot's current code goes, named by its fingerprint."""
    return BINARIES / f"{name}-{fingerprint(BOTS / name)[:16]}"


def build(names: Iterable[str]) -> dict[str, Path]:
    """Build the bots that have no binary of their current code yet, in one go build, and return every binary.

    Raises:
        RuntimeError: A bot didn't compile.
    """
    wanted = {name: binary_path(name) for name in dict.fromkeys(names)}
    missing = [name for name, binary in wanted.items() if not binary.is_file()]
    if missing:
        BINARIES.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=BINARIES, prefix=".build-") as output:
            # Without the build's paths and stamp, the same code gives the same binary in every checkout.
            built = subprocess.run(
                [
                    "go",
                    "build",
                    "-trimpath",
                    "-buildvcs=false",
                    "-o",
                    output + os.sep,
                    *(f"./bots/{name}" for name in missing),
                ],
                cwd=LEAGUE,
                check=False,
                capture_output=True,
                text=True,
            )
            if built.returncode != 0:
                raise RuntimeError(f"a bot didn't build:\n{built.stderr.strip()}")
            for name in missing:
                os.replace(Path(output) / name, wanted[name])
    return wanted


class WorkerError(RuntimeError):
    """The worker answered a turn with an error: the bot failed or returned an invalid result."""


class Worker:
    """A bot's worker process, which plays one turn per call, as the runner plays it.

    Use it as a context manager: the process ends when the block does.
    """

    def __init__(self, name: str) -> None:
        """Build the bot if needed, and start its worker."""
        binary = build([name])[name]
        self.process = subprocess.Popen(
            [str(binary), "worker"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
        )
        if self._read() != {"ready": True}:
            raise WorkerError(f"{name}'s worker didn't start")

    def _read(self) -> dict[str, Any]:
        assert self.process.stdout is not None
        line = self.process.stdout.readline()
        if not line:
            raise WorkerError("the worker stopped")
        return json.loads(line)

    def play(self, turn: dict[str, Any]) -> dict[str, Any]:
        """Play one turn (a BotTurn as JSON) and return the result (a BotTurnResult as JSON).

        Raises:
            WorkerError: The bot failed the turn.
        """
        assert self.process.stdin is not None
        self.process.stdin.write(json.dumps({"turn": turn}) + "\n")
        self.process.stdin.flush()
        answer = self._read()
        if "error" in answer:
            raise WorkerError(answer["error"])
        return answer["result"]

    def __enter__(self) -> Self:
        """Return the worker."""
        return self

    def __exit__(
        self,
        kind: type[BaseException] | None,
        error: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """End the worker: it exits when its stdin closes."""
        if self.process.stdin is not None:
            self.process.stdin.close()
        self.process.wait()
