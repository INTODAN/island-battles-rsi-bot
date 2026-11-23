"""The wall-clock time of an iteration's steps, or any other work's: ``league clock``.

``league clock start STEP`` and ``league clock stop STEP`` write the time to
``runs/clock.jsonl``; ``league clock report`` prints each step's start, end and
minutes, its share of the whole, and the steps still open. It is how an agent
that may run nothing but ``league`` commands (the automated iteration's)
times its steps, and how everyone else does too, so that every iteration's
times are read the same way.
"""

from __future__ import annotations

import datetime
import json
import re
from pathlib import Path
from typing import Any

from .paths import RUNS

CLOCK = RUNS / "clock.jsonl"
# A step's name: short, plain, and nothing a log could abuse.
STEP = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ._:/+-]{0,59}$")


def _now() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)


def mark(event: str, step: str, path: Path = CLOCK, now: datetime.datetime | None = None) -> datetime.datetime:
    """Write that STEP started or stopped (event ``start`` or ``stop``); returns the time written."""
    if event not in ("start", "stop"):
        raise ValueError(f"an event is start or stop, not {event!r}")
    if not STEP.match(step):
        raise ValueError("a step's name is 1 to 60 letters, digits, spaces and ._:/+-, starting with a letter or digit")
    when = now or _now()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps({"event": event, "step": step, "time": when.isoformat(timespec="seconds")}) + "\n")
    return when


def load(path: Path = CLOCK) -> list[dict[str, Any]]:
    """The clock's events, oldest first; lines that aren't events are skipped."""
    if not path.is_file():
        return []
    events = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(line)
            event["at"] = datetime.datetime.fromisoformat(event["time"])
        except ValueError, KeyError, TypeError:
            continue
        if event.get("event") in ("start", "stop") and isinstance(event.get("step"), str):
            events.append(event)
    return sorted(events, key=lambda event: event["at"])


def steps(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Each step's start and end (None while open), in the order they started.

    A step started again after it stopped is a step of its own, with ``#2`` after its name.
    """
    done: list[dict[str, Any]] = []
    open_steps: dict[str, dict[str, Any]] = {}
    count: dict[str, int] = {}
    for event in events:
        name = event["step"]
        if event["event"] == "start":
            if name in open_steps:
                continue
            count[name] = count.get(name, 0) + 1
            label = name if count[name] == 1 else f"{name} #{count[name]}"
            open_steps[name] = {"step": label, "start": event["at"], "end": None}
            done.append(open_steps[name])
        elif name in open_steps:
            open_steps.pop(name)["end"] = event["at"]
    return done


def _minutes(seconds: float) -> str:
    return f"{seconds / 60:.1f}"


def report(events: list[dict[str, Any]], now: datetime.datetime | None = None) -> str:
    """The clock as a Markdown table, with the total and the steps still open."""
    timed = steps(events)
    if not timed:
        return "No step on the clock: `league clock start STEP` starts one."
    now = now or _now()
    first = min(step["start"] for step in timed)
    last = max(step["end"] or now for step in timed)
    total = max((last - first).total_seconds(), 1.0)
    lines = [
        "| Step | Start | End | Minutes | Share |",
        "| --- | --- | --- | ---: | ---: |",
    ]
    for step in timed:
        end = step["end"] or now
        seconds = (end - step["start"]).total_seconds()
        lines.append(
            f"| {step['step']} | {step['start']:%H:%M:%S} | {'open' if step['end'] is None else f'{end:%H:%M:%S}'} "
            f"| {_minutes(seconds)} | {seconds / total:.0%} |"
        )
    lines.append("")
    lines.append(f"Total: {_minutes(total)} minutes, from {first:%H:%M:%S} to {last:%H:%M:%S} UTC.")
    slowest = sorted(timed, key=lambda step: (step["end"] or now) - step["start"], reverse=True)[:3]
    lines.append(
        "Slowest: "
        + ", ".join(
            f"{step['step']} ({_minutes(((step['end'] or now) - step['start']).total_seconds())})" for step in slowest
        )
        + "."
    )
    still_open = [step["step"] for step in timed if step["end"] is None]
    if still_open:
        lines.append(f"Still open (counted to now): {', '.join(still_open)}.")
    return "\n".join(lines)
