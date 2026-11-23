"""The idea queue: what the next run should work on, the most points first.

With many runs at once (docs/parallel-iterations.md), the slate of the
``league-ideas`` skill is the league's, not one iteration's: the places open on
main as it is now. A run takes the top place nobody holds (``league lease``),
in this order:

1. **Each side line's place**: one at a time, since its rule counts iterations
   of work in a row.
2. **An exploiter**, when no player outside the main line takes a third of the
   points from the champion.
3. **A founder** for each free side place.
4. **A superseded candidate's graft**: a change that beat its parent and was
   overtaken by another promotion from the same head. It has evidence already,
   so it is the cheapest good candidate the league has.
5. **The champion's mistakes**, by the detectors (``league mistakes``): each kind
   scored by the maps it cost points on, a map counted once (its share of the
   flagged games there that the champion didn't win), so a mistake seen on many
   maps comes before one seen many times on one map.
6. **The ideas not tried** of the recent entries and runs, which have no
   numbers: after every mistake that has.

Each place has a key, the name a run leases it under: ``slot/<champion>/<place>``
for 1 to 3 (they open again when the champion changes) and ``idea/<hash>`` for
the rest.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Collection, Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .ledger import ITERATION, RUN_LINE, candidates
from .lines import Lines

IDEAS_HEADING = re.compile(r"^\*\*Ideas not tried:?\*\*:?\s*$|^#+\s*Ideas not tried\b", re.IGNORECASE)


@dataclass
class Place:
    """A place in the league's slate: what a run would write, and why."""

    key: str
    kind: str
    what: str
    score: float
    evidence: str = ""


def _idea_key(text: str) -> str:
    return "idea/" + hashlib.sha256(" ".join(text.lower().split()).encode()).hexdigest()[:12]


def exploiter_due(summary: Mapping[str, Any] | None, lines: Lines) -> bool:
    """Whether no player outside the main line takes a third of the points from the champion."""
    if not summary:
        return False
    main = set(lines.main.bots)
    champion = lines.champion
    for player, row in summary.get("pairs", {}).items():
        if player in main or player == champion:
            continue
        points, games = row.get(champion, (0, 0))
        if games and points * 3 >= games:
            return False
    return True


def mistake_places(rows: Collection[Any], champion: str) -> list[Place]:
    """The champion's kinds of mistake as places, scored by the maps they cost points on."""
    places = []
    for row in rows:
        if not row.games or not row.points_lost:
            continue
        share = row.points_lost / row.games
        score = round(len(row.maps) * share, 2)
        what = f"Fix the champion's `{row.kind}`: {row.games} games on {len(row.maps)} maps, {row.points_lost:g} points"
        example = row.examples[0] if row.examples else {}
        evidence = ""
        if example:
            turns = ", ".join("-".join(str(turn) for turn in pair) for pair in example.get("turns", [])[:3])
            players = " v ".join(example.get("players", []))
            evidence = (
                f"e.g. {example.get('map', '?')}, {players}, {example.get('result', '')}, "
                f"turns {turns}: {example.get('evidence', '')} ({example.get('demo', '')})"
            )
        places.append(Place(f"idea/mistake-{champion}-{row.kind}", "fix", what, score, evidence))
    return sorted(places, key=lambda place: (-place.score, place.key))


def ideas_not_tried(text: str) -> list[str]:
    """The items of every **Ideas not tried** list in a text, in order."""
    found: list[str] = []
    inside = False
    for line in text.splitlines():
        if IDEAS_HEADING.match(line.strip()):
            inside = True
            continue
        if inside:
            if line.startswith("- "):
                found.append(line[2:].strip())
            elif line.strip() and not line.startswith("  "):
                inside = False
    return found


def recent_ideas(ledger_text: str, root: Path, recent: int = 3) -> list[str]:
    """The ideas not tried of the last ``recent`` entries and the runs they name, newest first, once each."""
    lines = ledger_text.splitlines()
    starts = [index for index, line in enumerate(lines) if ITERATION.match(line)]
    if not starts:
        return []
    tail = "\n".join(lines[starts[-recent] if len(starts) >= recent else starts[0] :])
    texts = [tail]
    for name in RUN_LINE.findall(tail):
        run = root / name
        if run.is_file():
            texts.append(run.read_text(encoding="utf-8"))
    ideas = [idea for text in texts for idea in ideas_not_tried(text)]
    return list(dict.fromkeys(reversed(ideas)))


def superseded(ledger_text: str) -> list[str]:
    """The candidate lines of the ledger whose decision was **superseded**, newest first."""
    return [line for line in reversed(candidates(ledger_text)) if "**superseded**" in line]


def queue(
    lines: Lines,
    statuses: Mapping[str, str],
    summary: Mapping[str, Any] | None,
    mistakes: Collection[Any],
    ledger_text: str,
    root: Path,
    max_side_lines: int,
    held: Collection[str] = (),
) -> list[Place]:
    """Every open place of the slate, in the order runs should take them, without the ones held."""
    champion = lines.champion
    places: list[Place] = []
    for line in lines.side:
        if line.head and statuses.get(line.head) == "active":
            places.append(
                Place(
                    f"slot/{champion}/side-{line.name}",
                    "side line",
                    f"A fix or a graft for the side line `{line.name}`, from its head `{line.head}`",
                    float("inf"),
                    f"{line.without_promotion} iterations of work without a promotion",
                )
            )
    if exploiter_due(summary, lines):
        places.append(
            Place(
                f"slot/{champion}/exploiter",
                "exploiter",
                f"An exploiter of `{champion}`: no player outside the main line takes a third of its points",
                1e9,
            )
        )
    free = max(0, max_side_lines - len(lines.side))
    for index in range(1, free + 1):
        places.append(
            Place(f"slot/{champion}/founder-{index}", "founder", "A founder: a new strategy for a free side place", 1e8)
        )
    for line in superseded(ledger_text):
        places.append(Place(_idea_key(line), "graft", f"Graft the superseded change into the head: {line}", 1e7))
    places += mistake_places(mistakes, champion)
    for idea in recent_ideas(ledger_text, root):
        places.append(Place(_idea_key(idea), "idea", idea, 0.0))
    seen: set[str] = set()
    out = []
    for place in places:
        if place.key in held or place.key in seen:
            continue
        seen.add(place.key)
        out.append(place)
    return out


def markdown(places: list[Place]) -> str:
    """The queue as a table."""
    if not places:
        return "No open place.\n"
    rows = ["| # | Key | Kind | What | Score | Evidence |", "|---|---|---|---|---|---|"]
    for number, place in enumerate(places, 1):
        score = "first" if place.score == float("inf") else f"{place.score:g}"
        cells = [str(number), f"`{place.key}`", place.kind, place.what, score, place.evidence]
        rows.append("| " + " | ".join(cell.replace("|", "\\|") for cell in cells) + " |")
    return "\n".join(rows) + "\n"


def as_json(places: list[Place]) -> list[dict[str, Any]]:
    """The queue for the dispatcher."""
    return [asdict(place) | {"score": None if place.score == float("inf") else place.score} for place in places]
