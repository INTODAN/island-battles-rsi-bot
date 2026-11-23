"""Sum up the detectors' flags over a tournament: for each bot and each kind of mistake, where and what it cost."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from . import flags as flags_module
from . import opponents, roster, tournament
from .detectors import Flag
from .paths import RUNS
from .roster import ANCHOR


def players(bots: str | None, focus: str | None, anchors: str, no_opponents: bool) -> tuple[list[str], list[str]]:
    """The players and the focused bots, chosen as ``league tournament`` chooses them for the same arguments."""
    league = roster.load_roster()
    names = [name.strip() for name in bots.split(",")] if bots else [b.name for b in league if b.status != "candidate"]
    focused = [name.strip() for name in focus.split(",")] if focus else []
    names += [name for name in focused if name not in names]
    names += [f"level{level}" for level in anchors.split(",") if level]
    if not no_opponents:
        names += [name for name in opponents.load_opponents() if name not in names]
    return names, focused


@dataclass
class Row:
    """One bot's mistakes of one kind over a tournament."""

    kind: str
    games: int = 0
    maps: set[str] = field(default_factory=set)
    points_lost: float = 0.0
    cost: float = 0.0
    examples: list[dict[str, Any]] = field(default_factory=list)


def tables(results: list[dict[str, Any]], bots: list[str], examples: int) -> dict[str, list[Row]]:
    """For each bot, one row per kind of mistake, every kind listed even where it never showed.

    A game counts once for a kind however many flags of that kind the bot has
    in it. Points lost are 1 for a lost game and 0.5 for a draw. The examples
    are the shortest such games.
    """
    rows: dict[str, dict[str, Row]] = {bot: {kind: Row(kind) for kind in flags_module.kinds()} for bot in bots}
    found: dict[str, dict[str, list[tuple[int, dict[str, Any]]]]] = defaultdict(lambda: defaultdict(list))
    for result in results:
        if "error" in result:
            continue
        game_flags = flags_module.flags_for(result)
        for seat, name in enumerate(result["players"]):
            if name not in rows:
                continue
            color = result["seats"][seat]["team_color"]
            mine: dict[str, list[Flag]] = defaultdict(list)
            for flag in game_flags:
                if flag.team == color:
                    mine[flag.kind].append(flag)
            for kind, kind_flags in mine.items():
                row = rows[name].setdefault(kind, Row(kind))
                row.games += 1
                row.maps.add(result["map"])
                row.points_lost += 1 - tournament.points(result, name)
                row.cost += sum(flag.cost for flag in kind_flags)
                found[name][kind].append(
                    (
                        result["generations"],
                        {
                            "map": result["map"],
                            "players": result["players"],
                            "seat": seat + 1,
                            "result": "won"
                            if result["winner"] == name
                            else "drew"
                            if result["winner"] is None
                            else "lost",
                            "generations": result["generations"],
                            "demo": result["demo"],
                            "turns": [list(flag.turns) for flag in kind_flags],
                            "evidence": kind_flags[0].evidence,
                        },
                    )
                )
    for name, kinds in found.items():
        for kind, games in kinds.items():
            games.sort(key=lambda entry: (entry[0], entry[1]["demo"]))
            rows[name][kind].examples = [entry for _, entry in games[:examples]]
    return {name: list(by_kind.values()) for name, by_kind in rows.items()}


def ordered(rows: list[Row]) -> list[Row]:
    """A bot's rows, the kind that cost it the most points first."""
    return sorted(rows, key=lambda row: (-row.points_lost, -row.games, row.kind))


def as_json(found: dict[str, list[Row]]) -> dict[str, Any]:
    """The tables as JSON can hold them, each bot's rows in the order of the text's."""
    return {
        name: [
            {
                "kind": row.kind,
                "games": row.games,
                "maps": sorted(row.maps),
                "points_lost": row.points_lost,
                "cost": row.cost,
                "examples": row.examples,
            }
            for row in ordered(rows)
        ]
        for name, rows in found.items()
    }


def markdown(found: dict[str, list[Row]], games: dict[str, int]) -> str:
    """The tables as text: one per bot, then each kind's shortest games."""
    lines = []
    for name, rows in found.items():
        lines += [
            f"## {name}: {games.get(name, 0)} games",
            "",
            "| Kind | Games | Maps | Points lost in them | Cost |",
            "|---|---|---|---|---|",
        ]
        lines += [
            f"| {row.kind} | {row.games} | {len(row.maps)} | {row.points_lost:g} | {row.cost:g} |"
            for row in ordered(rows)
        ]
        lines.append("")
        for row in ordered(rows):
            if not row.examples:
                continue
            lines.append(f"{row.kind}, the shortest games:")
            for example in row.examples:
                windows = ", ".join(f"{first}-{last}" for first, last in example["turns"])
                lines.append(
                    f"- {example['map']}: {' vs '.join(example['players'])}, seat {example['seat']}, "
                    f"{example['result']} in {example['generations']}; turns {windows}: {example['evidence']}: "
                    f"`{example['demo']}`"
                )
            lines.append("")
    return "\n".join(lines)


def run(plan: tournament.Tournament, run_id: str, examples: int) -> tuple[dict[str, list[Row]], list[dict[str, Any]]]:
    """Play what the tournament lacks, compute every match's flags once, and sum them up for its listed bots.

    Raises:
        ValueError: A map is a holdout map: its games are never read by a run.
    """
    if tournament.has_holdout(plan.maps):
        raise ValueError("league mistakes reads games: holdout maps are never read; use train or training maps' names")
    run_directory = RUNS / run_id
    run_directory.mkdir(parents=True, exist_ok=True)
    results = tournament.play(plan, run_directory)
    # The default bots' mistakes teach nothing: the league never changes them.
    bots = plan.listed or [name for name in dict.fromkeys(plan.players) if not ANCHOR.fullmatch(name)]
    return tables(results, bots, examples), results


def games_played(results: list[dict[str, Any]]) -> dict[str, int]:
    """How many played games each player has in the results."""
    count: dict[str, int] = defaultdict(int)
    for result in results:
        if "error" not in result:
            for name in result["players"]:
                count[name] += 1
    return count
