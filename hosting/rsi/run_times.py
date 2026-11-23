"""Where a GitHub Actions run's time went: its jobs, its rounds of runners and its slow steps.

    python3 hosting/rsi/run_times.py RUN_ID [--repo OWNER/NAME] [--slow-step SECONDS]

It reads the run's jobs with ``gh api`` (GH_TOKEN) and prints, as Markdown:
each job's wait in the queue and its minutes; each round of runners (the jobs
whose names differ only by ``K/N``, such as ``Warm 3/8``) as its slowest,
median and fastest runner, since a round lasts as long as its slowest; the
steps longer than --slow-step; and the run's time from its creation to its
last job's end. The automated iteration gives it to its second half, and
writes it to the summary of every run, a failed one too: the
``measuring-time`` skill says how to read it.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import statistics
import subprocess
import sys
from typing import Any

ROUND = re.compile(r"^(?P<round>.+?) (?P<k>\d+)/(?P<n>\d+)$")


def _at(stamp: str | None) -> datetime.datetime | None:
    return datetime.datetime.fromisoformat(stamp.replace("Z", "+00:00")) if stamp else None


def _seconds(start: str | None, end: str | None) -> float | None:
    first, last = _at(start), _at(end)
    return (last - first).total_seconds() if first and last else None


def _minutes(seconds: float | None) -> str:
    return "–" if seconds is None else f"{seconds / 60:.1f}"


def report(run: dict[str, Any], jobs: list[dict[str, Any]], slow_step: float = 60) -> str:
    """The run's times as Markdown, from the API's run and its jobs."""
    lines = [
        "| Job | Result | Queued | Minutes |",
        "| --- | --- | ---: | ---: |",
    ]
    rounds: dict[str, list[tuple[str, float]]] = {}
    slow: list[tuple[float, str, str]] = []
    ends: list[datetime.datetime] = []
    for job in sorted(jobs, key=lambda job: job.get("started_at") or ""):
        seconds = _seconds(job.get("started_at"), job.get("completed_at"))
        conclusion = job.get("conclusion") or job.get("status", "")
        if conclusion == "skipped":
            continue
        name = job["name"]
        found = ROUND.match(name)
        if found and seconds is not None:
            rounds.setdefault(found["round"], []).append((found["k"], seconds))
        else:
            queued = _seconds(job.get("created_at"), job.get("started_at"))
            lines.append(f"| {name} | {conclusion} | {_minutes(queued)} | {_minutes(seconds)} |")
        end = _at(job.get("completed_at"))
        if end is not None:
            ends.append(end)
        for step in job.get("steps") or []:
            step_seconds = _seconds(step.get("started_at"), step.get("completed_at"))
            if step_seconds is not None and step_seconds >= slow_step:
                slow.append((step_seconds, name, step["name"]))
    if rounds:
        lines += [
            "",
            "| Round | Runners | Slowest | Median | Fastest | Slowest runner |",
            "| --- | ---: | ---: | ---: | ---: | --- |",
        ]
        for name, runners in rounds.items():
            times = [seconds for _, seconds in runners]
            slowest = max(runners, key=lambda runner: runner[1])
            lines.append(
                f"| {name} | {len(runners)} | {_minutes(max(times))} | {_minutes(statistics.median(times))} "
                f"| {_minutes(min(times))} | {slowest[0]} |"
            )
    if slow:
        # A round's runners run the same steps: its slowest runner's are enough.
        seen: set[tuple[str, str]] = set()
        lines += ["", f"Steps of a minute or more ({_minutes(slow_step)} min and up), slowest first:", ""]
        for seconds, job, step in sorted(slow, reverse=True):
            found = ROUND.match(job)
            key = (found["round"] if found else job, step)
            if key in seen:
                continue
            seen.add(key)
            lines.append(f"- {_minutes(seconds)} min: {job}: {step}")
    created = _at(run.get("created_at"))
    if created and ends:
        last = max(ends)
        lines += [
            "",
            f"The run: {_minutes((last - created).total_seconds())} minutes, from {created:%H:%M} to {last:%H:%M} UTC.",
        ]
    return "\n".join(lines)


def _api(path: str) -> dict[str, Any]:
    out = subprocess.run(["gh", "api", path], check=True, capture_output=True, text=True).stdout
    return json.loads(out)


def main(argv: list[str] | None = None) -> int:
    """Print a run's times."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("run_id")
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", "INTODAN/island-battles-rsi-bot"))
    parser.add_argument("--slow-step", type=float, default=60, help="list the steps of at least this many seconds")
    args = parser.parse_args(argv)
    run = _api(f"repos/{args.repo}/actions/runs/{args.run_id}")
    jobs: list[dict[str, Any]] = []
    page = 1
    while True:
        batch = _api(f"repos/{args.repo}/actions/runs/{args.run_id}/jobs?per_page=100&page={page}")["jobs"]
        jobs += batch
        if len(batch) < 100:
            break
        page += 1
    print(report(run, jobs, args.slow_step))
    return 0


if __name__ == "__main__":
    sys.exit(main())
