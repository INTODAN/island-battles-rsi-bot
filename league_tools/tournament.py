"""Play a round robin between bots, with cached results, and sum it up."""

from __future__ import annotations

import functools
import hashlib
import json
import os
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from itertools import combinations
from pathlib import Path
from typing import Any

from . import engine, gobots, ratings
from .opponents import load_opponents
from .paths import BOTS, CACHE, LEAGUE, MAPS, RUNS
from .roster import ANCHOR, load_bot


@dataclass
class Tournament:
    """What to play: every pair of players, on every map, from both sides."""

    players: list[str]
    maps: list[Path]
    # With a focus, only the pairs with a focused player are played.
    focus: list[str] = field(default_factory=list)
    # The players whose lost games and longest wins the tables list.
    listed: list[str] = field(default_factory=list)
    # Each listed bot's parent, for the table that compares them.
    parents: dict[str, str] = field(default_factory=dict)
    # With a focus, play only each focused bot against its parent: the
    # head-to-head rule, and the gate on those games, in a few seconds.
    parents_only: bool = False
    max_generations: int = 300
    turn_timeout_milliseconds: int = 2000
    parallel: int = 0
    use_cache: bool = True
    # (K, N): play only the K-th of N slices of the matches, for runners that
    # share a tournament; their caches together hold the whole of it.
    shard: tuple[int, int] | None = None


def parse_shard(text: str) -> tuple[int, int]:
    """A shard written ``K/N``: the K-th of N slices, counted from 1.

    Raises:
        ValueError: It isn't two whole numbers with 1 <= K <= N.
    """
    index, _, count = text.partition("/")
    if not (index.isdigit() and count.isdigit() and 1 <= int(index) <= int(count)):
        raise ValueError(f"--shard {text!r}: write K/N, the K-th of N slices, such as 2/8")
    return int(index), int(count)


def in_shard(key: str, shard: tuple[int, int] | None) -> bool:
    """Whether a match's key falls in the shard: every key falls in exactly one of N shards.

    A key is a hash, so the shards are even and every runner agrees on them,
    whatever its cache holds.
    """
    if shard is None:
        return True
    index, count = shard
    return int(key, 16) % count == index - 1


def map_files(selection: str) -> list[Path]:
    """The map files a selection names: ``train``, ``holdout``, ``all`` or names.

    Raises:
        ValueError: A name is not a map of the league, or two maps share a name.
    """
    if selection in ("train", "holdout"):
        files = sorted((MAPS / selection).glob("*.json"))
    elif selection == "all":
        files = sorted(MAPS.glob("*/*.json"))
    else:
        files = []
        for name in selection.split(","):
            found = sorted(MAPS.glob(f"*/{name.strip()}.json"))
            if not found:
                raise ValueError(f"there is no map {name.strip()!r} under {MAPS}")
            files.extend(found)
    names = [file.stem for file in files]
    repeated = sorted({name for name in names if names.count(name) > 1})
    if repeated:
        raise ValueError(f"more than one map is named {', '.join(repeated)}; a map's name is its file's")
    return files


def has_holdout(maps: list[Path]) -> bool:
    """Whether any of the maps is a holdout map, whose games nobody reads."""
    return any(file.parent.name == "holdout" for file in maps)


def player_specification(name: str, binary: Path | None = None) -> dict[str, Any]:
    """The runner's description of a player: a default bot, an outside opponent or a league bot.

    Args:
        name: The player.
        binary: A league bot's program, from ``gobots.build``; its current code's by default.
    """
    anchor = ANCHOR.fullmatch(name)
    if anchor:
        return {"default_level": int(anchor.group(1))}
    outside = load_opponents().get(name)
    if outside is not None:
        return outside.specification()
    load_bot(name)
    return {"worker": [str(binary or gobots.binary_path(name)), "worker"], "directory": str(LEAGUE)}


@functools.cache
def player_fingerprint(name: str) -> str:
    """What decides how a player plays: its code, and for a league bot the Go SDK's version."""
    if ANCHOR.fullmatch(name):
        return name
    outside = load_opponents().get(name)
    if outside is not None:
        return outside.fingerprint()
    return gobots.fingerprint(BOTS / name)


def match_key(build: str, map_hash: str, seats: list[str], fingerprints: list[str], settings: list[int]) -> str:
    """The name of a match's result in the cache.

    It covers everything that decides the game, and the seats' names, which
    the result carries: two bots with the same code have results of their own.
    """
    return hashlib.sha256(json.dumps([build, map_hash, seats, fingerprints, settings]).encode()).hexdigest()[:32]


def _write_atomically(path: Path, text: str) -> None:
    """Write a file that another checkout's tournament may be reading."""
    partial = path.with_name(f".{path.name}.{os.getpid()}")
    partial.write_text(text, encoding="utf-8")
    os.replace(partial, path)


def cached_result(key: str) -> dict[str, Any] | None:
    """A match's cached result, when its demo is still there."""
    result_file, demo_file = CACHE / f"{key}.json", CACHE / f"{key}.json.gz"
    if not result_file.is_file() or not demo_file.is_file():
        return None
    return json.loads(result_file.read_text(encoding="utf-8")) | {"demo": str(demo_file)}


def play(tournament: Tournament, run_directory: Path) -> list[dict[str, Any]]:
    """Play the tournament's matches, reusing cached results, and return them all.

    Every pair with a focused player (every pair, without a focus) plays on
    every map from both sides; two default bots never play each other.
    """
    focus = set(tournament.focus)
    if tournament.parents_only:
        pairs = [(name, tournament.parents[name]) for name in tournament.focus if name in tournament.parents]
    else:
        pairs = [
            pair
            for pair in combinations(dict.fromkeys(tournament.players), 2)
            if not all(ANCHOR.fullmatch(name) for name in pair) and (not focus or focus & set(pair))
        ]
    matches = [
        (map_file, seats) for map_file in tournament.maps for pair in pairs for seats in (list(pair), list(pair[::-1]))
    ]
    return play_matches(
        matches,
        run_directory,
        max_generations=tournament.max_generations,
        turn_timeout_milliseconds=tournament.turn_timeout_milliseconds,
        parallel=tournament.parallel,
        use_cache=tournament.use_cache,
        shard=tournament.shard,
    )


def play_matches(
    matches: list[tuple[Path, list[str]]],
    run_directory: Path,
    max_generations: int = 300,
    turn_timeout_milliseconds: int = 2000,
    parallel: int = 0,
    use_cache: bool = True,
    shard: tuple[int, int] | None = None,
) -> list[dict[str, Any]]:
    """Play these matches (a map and its seats, in order), reusing cached results, and return them all.

    Bots are deterministic, so a match is decided by the runner's build, the
    map, the two bots' code and the settings. A match with the same key as an
    earlier one is not played again. A result with a failed turn is not kept:
    a turn can run out of time because the machine was busy, and the next
    tournament plays that match again. With a shard, only the matches whose
    key falls in it are played and returned.
    """
    build = engine.build()
    # A bot's code is read once per tournament, not once per match.
    player_fingerprint.cache_clear()
    settings = [max_generations, turn_timeout_milliseconds]
    planned: dict[str, dict[str, Any]] = {}
    map_hashes: dict[Path, str] = {}
    for map_file, seats in matches:
        if map_file not in map_hashes:
            map_hashes[map_file] = hashlib.sha256(map_file.read_bytes()).hexdigest()
        fingerprints = [player_fingerprint(name) for name in seats]
        key = match_key(build.hash, map_hashes[map_file], seats, fingerprints, settings)
        if not in_shard(key, shard):
            continue
        planned[key] = {"id": key, "map": map_file.stem, "seats": seats}
    results: dict[str, dict[str, Any]] = {}

    def from_cache() -> list[dict[str, Any]]:
        if use_cache:
            for key in planned:
                if key not in results:
                    cached = cached_result(key)
                    if cached is not None:
                        results[key] = cached
        return [match for key, match in planned.items() if key not in results]

    to_play = from_cache()
    part = f" in shard {shard[0]}/{shard[1]}" if shard else ""
    print(f"{len(planned)} matches{part}: {len(results)} cached, {len(to_play)} to play", file=sys.stderr, flush=True)
    if not to_play:
        return [results[key] for key in planned if key in results]
    CACHE.mkdir(parents=True, exist_ok=True)
    # One tournament plays at a time on this machine, whichever checkout it
    # runs from: several at once only slow every turn down (and a turn that
    # runs out of time fails), and the one that waits finds in the cache
    # what the other played.
    with engine.exclusive(CACHE / ".play.lock", "league: waiting for another tournament to finish playing"):
        before = len(to_play)
        to_play = from_cache()
        if len(to_play) < before:
            print(f"{before - len(to_play)} of them were played meanwhile; {len(to_play)} to play", file=sys.stderr)
        if to_play:
            names = sorted({name for match in to_play for name in match["seats"]})
            # Each league bot is built once per tournament, and not again while its code is the same.
            outside = load_opponents()
            binaries = gobots.build(name for name in names if not ANCHOR.fullmatch(name) and name not in outside)
            schedule = {
                "players": {name: player_specification(name, binaries.get(name)) for name in names},
                "maps": {map_file.stem: str(map_file) for map_file in map_hashes},
                "matches": to_play,
                "max_generations": max_generations,
                "turn_timeout_milliseconds": turn_timeout_milliseconds,
                "parallel": parallel or os.cpu_count() or 1,
                "demo_directory": str(CACHE),
                "compress_demos": True,
            }
            for line in engine.play(build.binary, schedule, run_directory / "workers.log"):
                results[line["id"]] = line
                cached = CACHE / f"{line['id']}.json"
                if "error" not in line and not any(seat["failed_turns"] for seat in line["seats"]):
                    _write_atomically(cached, json.dumps(line))
                else:
                    # The runner has replaced the demo, so an earlier result of
                    # this match no longer belongs to it.
                    cached.unlink(missing_ok=True)
    return [results[key] for key in planned if key in results]


def points(result: dict[str, Any], player: str) -> float:
    """A player's points in a game: a win 1, a draw 0.5, a loss 0."""
    return 0.5 if result["winner"] is None else float(result["winner"] == player)


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Standings, the table of every pair, each player's record per map and the problems."""
    record: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "games": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "failed_turns": 0,
            "slowest_turn_milliseconds": 0.0,
        }
    )
    pair_points: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    map_points: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    games = []
    errors = []
    for result in results:
        if "error" in result:
            errors.append(
                {
                    "map": result["map"],
                    "players": result["players"],
                    "error": result["error"],
                }
            )
            continue
        first, second = result["players"]
        first_score = points(result, first)
        games.append((first, second, first_score))
        for name, opponent, score, seat in (
            (first, second, first_score, result["seats"][0]),
            (second, first, 1 - first_score, result["seats"][1]),
        ):
            row = record[name]
            row["games"] += 1
            row["wins" if score == 1 else "losses" if score == 0 else "draws"] += 1
            row["failed_turns"] += seat["failed_turns"]
            row["slowest_turn_milliseconds"] = max(row["slowest_turn_milliseconds"], seat["slowest_turn_milliseconds"])
            pair_points[name][opponent][0] += score
            pair_points[name][opponent][1] += 1
            map_points[name][result["map"]][0] += score
            map_points[name][result["map"]][1] += 1
    rating = ratings.fit(games)
    standings = [
        {
            "player": name,
            "rating": round(rating[name]),
            "score": round((row["wins"] + row["draws"] / 2) / row["games"], 3),
            **row,
        }
        for name, row in sorted(record.items(), key=lambda item: (-rating[item[0]], item[0]))
    ]
    return {
        "standings": standings,
        "pairs": {name: dict(row) for name, row in pair_points.items()},
        "maps": {name: dict(row) for name, row in map_points.items()},
        "errors": errors,
    }


def losses(results: list[dict[str, Any]], player: str) -> list[dict[str, Any]]:
    """The games a player lost or drew, shortest first: the ones worth studying."""
    lost = [
        result
        for result in results
        if "error" not in result and player in result["players"] and result["winner"] != player
    ]
    return sorted(lost, key=lambda result: (result["winner"] is None, result["generations"]))


def longest_wins(results: list[dict[str, Any]], player: str) -> list[dict[str, Any]]:
    """The games a player won, longest first: a slow win hides a weakness."""
    won = [result for result in results if "error" not in result and result["winner"] == player]
    return sorted(won, key=lambda result: -result["generations"])


def game_line(result: dict[str, Any]) -> str:
    """One game of a list: its map, seats, outcome, length and demo."""
    return (
        f"- {result['map']}: {' vs '.join(result['players'])}: {result['outcome']['summary']} "
        f"in {result['generations']} generations: `{result['demo']}`"
    )


def against_parents(summary: dict[str, Any], parents: dict[str, str], whole: bool, maps: str) -> list[str]:
    """A table of each listed bot next to its parent, with the selection rules its numbers meet.

    Args:
        summary: What ``summarize`` returned.
        parents: Each listed bot's parent.
        whole: Whether every pair played, so that the ratings count.
        maps: ``train``, ``holdout`` or anything else: which rules apply.
    """
    rating = {row["player"]: row["rating"] for row in summary["standings"]}
    rows = []
    for name, parent in parents.items():
        points = summary["pairs"].get(name, {}).get(parent)
        if points is None:
            continue
        cells = [f"`{name}`", f"`{parent}`", f"{points[0]:g}/{points[1]:g}"]
        if maps != "holdout":
            cells.append("yes" if points[0] > points[1] / 2 else "no")
        if whole:
            above = rating[name] > rating[parent]
            cells.append(f"{rating[name]} ({rating[parent]})")
            if maps == "holdout":
                cells.append("yes" if rating[name] >= rating[parent] else "no")
            elif maps == "train":
                cells.append("yes" if above else "no")
        rows.append("| " + " | ".join(cells) + " |")
    if not rows:
        return []
    header = ["Bot", "Parent", "Points against the parent"]
    if maps != "holdout":
        header.append("More than half")
    if whole:
        header.append("Rating (parent's)")
        if maps == "holdout":
            header.append("Holdout rating not below the parent's")
        elif maps == "train":
            header.append("Rated above the parent")
    lines = ["", "Each listed bot against its parent" + ("" if whole else " (ratings don't count here)") + ":", ""]
    lines += ["| " + " | ".join(header) + " |", "|---" * len(header) + "|", *rows]
    return lines


def markdown(
    summary: dict[str, Any],
    results: list[dict[str, Any]],
    listed: list[str],
    list_games: bool,
    parent_table: list[str] | None = None,
) -> str:
    """The summary as Markdown tables.

    Args:
        summary: What ``summarize`` returned.
        results: The matches.
        listed: The players whose lost games and longest wins are listed.
        list_games: False leaves those lists out, as for holdout maps, whose
            games nobody reads.
        parent_table: The lines of ``against_parents``, printed after the standings.
    """
    lines = [
        "| Player | Rating | Score | W | D | L | Failed turns | Slowest turn (ms) |",
        "|---|---|---|---|---|---|---|---|",
    ]
    order = [row["player"] for row in summary["standings"]]
    for row in summary["standings"]:
        lines.append(
            f"| {row['player']} | {row['rating']} | {row['score']:.3f} | {row['wins']} | {row['draws']} "
            f"| {row['losses']} | {row['failed_turns']} | {row['slowest_turn_milliseconds']:.1f} |"
        )
    lines += parent_table or []

    def cell(points: list[float] | None) -> str:
        return "" if points is None else f"{points[0]:g}/{points[1]:g}"

    lines += ["", "Points of the row's player against the column's:", ""]
    lines += ["| | " + " | ".join(order) + " |", "|---" * (len(order) + 1) + "|"]
    for name in order:
        cells = [cell(summary["pairs"][name].get(opponent)) for opponent in order]
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    map_names = sorted({result["map"] for result in results})
    lines += ["", "Points per map:", ""]
    lines += ["| | " + " | ".join(map_names) + " |", "|---" * (len(map_names) + 1) + "|"]
    for name in order:
        cells = [cell(summary["maps"][name].get(map_name)) for map_name in map_names]
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    for error in summary["errors"]:
        lines.append(f"\nNOT PLAYED {error['map']} {' vs '.join(error['players'])}: {error['error']}")
    if listed and not list_games:
        lines += ["", "Holdout maps were played: their games are not listed, and nobody digests them."]
    for name in listed if list_games else []:
        lines += ["", f"Games {name} didn't win (demo to digest):", ""]
        lines += [game_line(result) for result in losses(results, name)[:20]]
        lines += ["", f"Longest wins of {name}:", ""]
        lines += [game_line(result) for result in longest_wins(results, name)[:5]]
    failures = [
        f"- {result['map']} {' vs '.join(result['players'])}: {seat['name']} turn {failure['turn']}: "
        f"{failure['message'].strip().splitlines()[-1][:300]}"
        for result in results
        if "error" not in result
        for seat in result["seats"]
        for failure in seat["failures"][:1]
    ]
    if failures:
        lines += ["", "Failed turns (the first of each game):", "", *failures[:30]]
    return "\n".join(lines) + "\n"


def failed_players(results: list[dict[str, Any]]) -> list[str]:
    """The players that failed a turn in any of the games."""
    return sorted(
        {
            seat["name"]
            for result in results
            if "error" not in result
            for seat in result["seats"]
            if seat["failed_turns"]
        }
    )


def shard_summary(results: list[dict[str, Any]], shard: tuple[int, int]) -> dict[str, Any]:
    """What a shard played, without ratings: a slice of the matches rates nobody.

    Its holdout games' numbers stay unseen too, as the iteration's selection needs.
    """
    errors = [
        {"map": result["map"], "players": result["players"], "error": result["error"]}
        for result in results
        if "error" in result
    ]
    failed_games = sum(
        1 for result in results if "error" not in result and any(seat["failed_turns"] for seat in result["seats"])
    )
    return {
        "shard": f"{shard[0]}/{shard[1]}",
        "matches": len(results),
        "failed_games": failed_games,
        "failed_players": failed_players(results),
        "errors": errors,
    }


def shard_report(summary: dict[str, Any]) -> str:
    """A shard's summary as text: how many matches, and which went wrong."""
    lines = [
        f"Shard {summary['shard']}: {summary['matches']} matches, {summary['failed_games']} with a failed turn, "
        f"{len(summary['errors'])} not played. No standings: a shard's games rate nobody; "
        "play the tournament without --shard once every shard's cache is in runs/cache."
    ]
    lines += [f"NOT PLAYED {e['map']} {' vs '.join(e['players'])}: {e['error']}" for e in summary["errors"]]
    return "\n".join(lines) + "\n"


def run(tournament: Tournament, run_id: str) -> tuple[dict[str, Any], str]:
    """Play a tournament and write its results, summary and tables under ``runs/<run_id>/``.

    A shard's summary has no standings, pairs or maps: the tables come from the
    whole tournament, played again from the shards' caches together.
    """
    run_directory = RUNS / run_id
    run_directory.mkdir(parents=True, exist_ok=True)
    results = play(tournament, run_directory)
    if tournament.shard:
        summary = shard_summary(results, tournament.shard)
        table = shard_report(summary)
    else:
        summary = summarize(results) | {"matches": len(results), "failed_players": failed_players(results)}
        sets = {file.parent.name for file in tournament.maps}
        parent_table = against_parents(
            summary,
            {name: parent for name, parent in tournament.parents.items() if name in tournament.listed},
            whole=not tournament.focus,
            maps=sets.pop() if len(sets) == 1 else "",
        )
        table = markdown(summary, results, tournament.listed, not has_holdout(tournament.maps), parent_table)
    with (run_directory / "results.jsonl").open("w", encoding="utf-8") as file:
        for result in results:
            file.write(json.dumps(result) + "\n")
    (run_directory / "summary.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    (run_directory / "summary.md").write_text(table, encoding="utf-8")
    return summary, table
