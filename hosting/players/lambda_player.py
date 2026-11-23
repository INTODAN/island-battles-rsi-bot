"""The Lambda player: one invocation plays batches of the match store's queue (``league player --drain``).

A schedule invokes it every few minutes, and a tournament in request mode may
invoke it at once (``LEAGUE_PLAYER_FUNCTION``), with ``{"batch": N}``. It
plays until the queue holds nothing it can lease, or until its time is nearly
up: it takes no new batch in the last ``SAFETY_SECONDS``.

The image (``Dockerfile``) holds the league's tools, Go, the Go modules that
``go.mod`` pins and the runner built from ``runner.toml``'s commit
(``LEAGUE_RUNNER_BINARY``). Lambda's filesystem is read-only but ``/tmp``, so
the bots' binaries, the local cache and Go's build cache go there
(``LEAGUE_SHARED``, ``GOCACHE``), the build cache started from the image's warm
one.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any, Protocol

# Go's build cache as the image left it: the SDK and the standard packages a bot may import, compiled.
WARM_CACHE = Path("/opt/go-cache")
# No new batch starts this close to the function's timeout: a batch of 25 matches takes well under a minute.
SAFETY_SECONDS = 120
DEFAULT_BATCH = 25
MAX_BATCH = 200


class Context(Protocol):
    """What the handler reads of Lambda's context."""

    def get_remaining_time_in_millis(self) -> int:
        """The milliseconds left before the function times out."""
        ...


def arguments(event: dict[str, Any] | None, remaining_milliseconds: int) -> list[str]:
    """The ``league`` command line for an invocation: its batch, and the seconds it may take new batches for."""
    batch = DEFAULT_BATCH
    requested = (event or {}).get("batch")
    if isinstance(requested, int) and not isinstance(requested, bool):
        batch = min(max(requested, 1), MAX_BATCH)
    seconds = max(remaining_milliseconds / 1000 - SAFETY_SECONDS, 1)
    return ["player", "--drain", "--batch", str(batch), "--max-seconds", f"{seconds:.0f}"]


def handler(event: dict[str, Any] | None, context: Context) -> dict[str, Any]:
    """Play the queue's matches for one invocation, and return the command's exit status."""
    cache = Path(os.environ.get("GOCACHE", "/tmp/go-cache"))
    if WARM_CACHE.is_dir() and not cache.exists():
        shutil.copytree(WARM_CACHE, cache)
    # Imported here: the league's paths read LEAGUE_SHARED when they load.
    from league_tools import cli

    command = arguments(event, context.get_remaining_time_in_millis())
    return {"status": cli.main(command), "command": command}
