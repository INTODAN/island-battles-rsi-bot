"""Play a studied game again with a candidate in its parent's seat.

A candidate is written from a few games: the finding names a game, its turns and
the decision that lost it. Before the gate plays the candidate hundreds of times,
this plays those games once more with the candidate where its parent sat, the
same opponent, map and side, which takes seconds, and says:

- the result before and after, where "before" is the parent's game played again
  with the same runner, opponent and settings (the studied game itself when none
  changed, which the cache then gives at once);
- the first turn on which the candidate commanded something else than its parent
  did, with both bots' commands and log lines of that turn. Bots are
  deterministic, so up to that turn both games are the same move for move; a
  candidate that never commands anything else never used its change in that game.

It answers "does the change do what its idea says, in the game it came from?",
not "is it better": a handful of games can't say that, and the gate and the
selection still decide. Its matches go to the tournament's cache, so the gate
doesn't play them again.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import tournament
from .digest import load_demo
from .replay import team_commands
from .roster import load_bot
from .tournament import points


@dataclass(frozen=True)
class Source:
    """A league game to play again: its demo, its result and the seats of the rematch."""

    demo: Path
    result: dict[str, Any]
    map_file: Path
    seats: list[str]


def source_result(demo: Path) -> dict[str, Any]:
    """The tournament's result of a game, kept beside its demo in the cache.

    Raises:
        ValueError: The demo is not a league game's: no result sits beside it.
    """
    name = demo.name
    key = name.removesuffix(".json.gz") if name.endswith(".json.gz") else ""
    result_file = demo.with_name(f"{key}.json")
    if not key or not result_file.is_file():
        raise ValueError(
            f"{demo} has no result beside it: rematch needs a demo that a tournament listed "
            "(runs/cache/<key>.json.gz with <key>.json), and a match with a failed turn keeps no result"
        )
    result = json.loads(result_file.read_text(encoding="utf-8"))
    if "error" in result or "players" not in result:
        raise ValueError(f"{demo}: its match was not played")
    return result


def plan(demos: list[Path], bot: str, replaces: str) -> list[Source]:
    """The rematches: each game with ``bot`` in the seat ``replaces`` had.

    Raises:
        ValueError: A game is not a league game's, ``replaces`` didn't play it,
            or its map is a holdout map, whose games nobody reads.
    """
    sources = []
    for demo in dict.fromkeys(demo.resolve() for demo in demos):
        result = source_result(demo)
        players = result["players"]
        if replaces not in players:
            raise ValueError(f"{demo}: {replaces} didn't play this game ({' vs '.join(players)})")
        if bot in players:
            raise ValueError(f"{demo}: {bot} already played this game")
        (map_file,) = tournament.map_files(result["map"])
        if tournament.has_holdout([map_file]):
            raise ValueError(f"{demo}: {result['map']} is a holdout map; its games are never studied or replayed")
        seats = [bot if name == replaces else name for name in players]
        sources.append(Source(demo, result, map_file, seats))
    return sources


def _commands(turn: dict[str, Any]) -> tuple[list[tuple[Any, ...]], list[tuple[Any, ...]]]:
    upgrades = sorted((entry["castle"], entry["type"], entry["level"]) for entry in turn["upgrades"])
    sends = sorted(
        (
            entry["origin"] if entry["origin"] is not None else -1,
            entry["dest"] if entry["dest"] is not None else -1,
            entry["amount"],
        )
        for entry in turn["sends"]
    )
    return upgrades, sends


def describe(turn: dict[str, Any]) -> str:
    """A turn's commands, as the boards show them."""
    upgrades, sends = _commands(turn)
    parts = [f"{kind} {level} at {castle}" for castle, kind, level in upgrades]
    parts += [
        f"{amount} from {origin} to {dest}" if origin >= 0 else f"{amount} (unseen)" for origin, dest, amount in sends
    ]
    return ", ".join(parts) or "nothing"


def first_difference(before: list[dict[str, Any]], after: list[dict[str, Any]]) -> int | None:
    """The first turn whose commands differ between two games of one team, or None when none does."""
    for old, new in zip(before, after, strict=False):
        if _commands(old) != _commands(new):
            return old["turn"]
    return None


def _team_color(result: dict[str, Any], player: str) -> int:
    return next(seat["team_color"] for seat in result["seats"] if seat["name"] == player)


def _log_lines(demo: dict[str, Any], turn: int, player: str) -> list[str]:
    logs = demo.get("logs", [])
    if turn - 1 >= len(logs):
        return []
    return [
        line["message"]
        for entry in logs[turn - 1]["players"]
        if entry["display_name"] == player
        for line in entry["lines"]
    ]


def _outcome(result: dict[str, Any]) -> str:
    return f"{result['outcome']['summary']} in {result['generations']} generations"


def report(source: Source, before: dict[str, Any], after: dict[str, Any], bot: str, replaces: str) -> list[str]:
    """What changed in one game, as lines of Markdown.

    Args:
        source: The studied game.
        before: The parent's game played again now, which is the studied one
            when the runner, the bots and the settings are what they were.
        after: The candidate's game in the parent's seat.
        bot: The candidate.
        replaces: The parent, whose seat the candidate took.
    """
    opponent = next(name for name in source.result["players"] if name != replaces)
    lines = [f"## {source.result['map']}, against {opponent}", ""]
    if "error" in before:
        return [*lines, f"- {replaces}: NOT PLAYED again: {before['error']}", ""]
    if before["id"] != source.result["id"]:
        lines.append(
            f"- The runner, a bot or the settings changed since the studied game (`{source.demo}`): "
            f"{replaces}'s game as it plays now is compared instead."
        )
    lines.append(f"- {replaces}: {_outcome(before)}: `{before['demo']}`")
    if "error" in after:
        return [*lines, f"- {bot}: NOT PLAYED: {after['error']}", ""]
    lines.append(f"- {bot}: {_outcome(after)}: `{after['demo']}`")
    seat = next(seat for seat in after["seats"] if seat["name"] == bot)
    if seat["failed_turns"]:
        message = seat["failures"][0]["message"].strip().splitlines()[-1][:300] if seat["failures"] else ""
        lines.append(f"- **{bot} failed {seat['failed_turns']} turns**: {message}")
    lines.append(f"- Points: {points(before, replaces):g} before, {points(after, bot):g} after.")
    old_demo, new_demo = load_demo(Path(before["demo"])), load_demo(Path(after["demo"]))
    color = _team_color(before, replaces)
    old_turns, new_turns = team_commands(old_demo, color), team_commands(new_demo, color)
    turn = first_difference(old_turns, new_turns)
    if turn is None:
        lines.append(f"- **{bot} commanded what {replaces} did on every turn: its change never acted in this game.**")
        return [*lines, ""]
    lines += [
        f"- First different command: turn {turn}; both games are the same move for move before it.",
        f"  - {replaces}: {describe(old_turns[turn - 1])}",
        *[f"    - log: {message}" for message in _log_lines(old_demo, turn, replaces)],
        f"  - {bot}: {describe(new_turns[turn - 1])}",
        *[f"    - log: {message}" for message in _log_lines(new_demo, turn, bot)],
        f"- Read on with `uv run league digest {after['demo']} --turns {turn}-{turn + 10}`.",
        "",
    ]
    return lines


def run(
    demos: list[Path],
    bot: str,
    replaces: str | None,
    run_directory: Path,
    max_generations: int = 300,
    turn_timeout_milliseconds: int = 2000,
) -> tuple[str, list[dict[str, Any]]]:
    """Play the games again with ``bot`` in the seat of ``replaces`` (its parent by default), and the parent's too.

    Both are played with the same settings, which should be the studied games':
    the tournament's by default.

    Returns:
        The report as Markdown, and the rematches' results.

    Raises:
        ValueError: The bot has no parent and none was named, or a game can't be played again.
    """
    replaced = replaces or load_bot(bot).parent
    if not replaced:
        raise ValueError(f"{bot} has no parent: say whose seat it takes with --replaces")
    sources = plan(demos, bot, replaced)
    matches = [(source.map_file, seats) for source in sources for seats in (source.result["players"], source.seats)]
    results = tournament.play_matches(
        matches,
        run_directory,
        max_generations=max_generations,
        turn_timeout_milliseconds=turn_timeout_milliseconds,
    )
    by_game = {(result["map"], tuple(result["players"])): result for result in results}
    missing = {"error": "the runner returned no result"}
    lines = [f"# {bot} in {replaced}'s seat", ""]
    total_before = total_after = 0.0
    played = []
    for source in sources:
        before = by_game.get((source.result["map"], tuple(source.result["players"])), missing)
        after = by_game.get((source.result["map"], tuple(source.seats)), missing)
        lines += report(source, before, after, bot, replaced)
        if "error" not in before and "error" not in after:
            played.append(after)
            total_before += points(before, replaced)
            total_after += points(after, bot)
    lines += [
        f"Points in these games ({len(played)}): {replaced} {total_before:g}, {bot} {total_after:g}.",
        "",
        "These are the games the change was written from: they say whether it does what its idea says, "
        "not whether it is better. The gate and the selection decide that.",
    ]
    return "\n".join(lines) + "\n", results
