"""The ``league`` command."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

from . import digest as digest_module
from . import ledger, maps, opponents, roster, tournament
from . import rematch as rematch_module
from . import replay as replay_module
from .paths import LEDGER, MAPS, RUNS


def _tournament(arguments: argparse.Namespace) -> int:
    bots = roster.load_roster()
    if arguments.bots:
        names = [name.strip() for name in arguments.bots.split(",")]
    else:
        names = [bot.name for bot in bots if bot.status != "candidate"]
    focus = [name.strip() for name in arguments.focus.split(",")] if arguments.focus else []
    added = [name.strip() for name in arguments.add.split(",")] if arguments.add else []
    names += [name for name in focus + added if name not in names]
    known = {bot.name: bot for bot in bots}
    parents = {
        name: known[name].parent
        for name in focus + added
        if name in known and known[name].parent in known and known[name].parent != name
    }
    if arguments.parents:
        if not focus:
            raise ValueError("--parents plays each bot of --focus against its parent: name them with --focus")
        orphans = [name for name in focus if name not in parents]
        if orphans:
            raise ValueError(f"no parent of the league to play against: {', '.join(orphans)}")
        names += [parent for parent in parents.values() if parent not in names]
    names += [f"level{level}" for level in arguments.anchors.split(",") if level]
    if not arguments.no_opponents:
        names += [name for name in opponents.load_opponents() if name not in names]
    plan = tournament.Tournament(
        players=names,
        maps=tournament.map_files(arguments.maps),
        focus=focus,
        listed=focus + added,
        parents=parents,
        parents_only=arguments.parents,
        max_generations=arguments.max_generations,
        turn_timeout_milliseconds=arguments.turn_timeout_milliseconds,
        parallel=arguments.parallel,
        use_cache=not arguments.no_cache,
    )
    run_id = arguments.run_id or f"{time.strftime('%Y%m%d-%H%M%S')}-{os.getpid()}"
    summary, table = tournament.run(plan, run_id)
    print(table)
    print(f"Written to {RUNS / run_id}", file=sys.stderr)
    failed = [row["player"] for row in summary["standings"] if row["failed_turns"]]
    if arguments.strict and (failed or summary["errors"] or not summary["matches"]):
        print(
            f"league: --strict: {summary['matches']} matches, {len(summary['errors'])} of them not played, "
            f"and these players failed turns: {', '.join(failed) or 'none'}",
            file=sys.stderr,
        )
        return 1
    return 0


def _digest(arguments: argparse.Namespace) -> int:
    window = None
    if arguments.turns:
        first, _, last = arguments.turns.partition("-")
        window = (int(first), int(last or first))
    demo = digest_module.load_demo(Path(arguments.demo))
    print(digest_module.digest(demo, arguments.every, window, arguments.logs, arguments.key_events), end="")
    return 0


def _replay(arguments: argparse.Namespace) -> int:
    paths = [Path(demo) for demo in arguments.demo]
    print(replay_module.run(paths, arguments.bot, arguments.team, arguments.examples), end="")
    return 0


def _rematch(arguments: argparse.Namespace) -> int:
    run_id = arguments.run_id or f"rematch-{arguments.bot}"
    table, results = rematch_module.run(
        [Path(demo) for demo in arguments.demo],
        arguments.bot,
        arguments.replaces,
        RUNS / run_id,
        max_generations=arguments.max_generations,
        turn_timeout_milliseconds=arguments.turn_timeout_milliseconds,
    )
    print(table, end="")
    failed = any(
        "error" in result or any(seat["failed_turns"] for seat in result["seats"] if seat["name"] == arguments.bot)
        for result in results
    )
    return 1 if failed else 0


def _unpack(arguments: argparse.Namespace) -> int:
    source = Path(arguments.demo)
    name = source.name.removesuffix(".gz")
    name = name.removesuffix(".zip") + ".json" if name.endswith(".zip") else name
    target = Path(arguments.output or RUNS / "view" / name)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(digest_module.load_demo(source)))
    print(target)
    return 0


def _ledger(arguments: argparse.Namespace) -> int:
    print(ledger.load(LEDGER / "iterations.md", arguments.recent), end="")
    return 0


def _roster(arguments: argparse.Namespace) -> int:
    for bot in roster.load_roster():
        if arguments.json:
            print(json.dumps(bot.__dict__))
        else:
            parent = f" (from {bot.parent})" if bot.parent else ""
            print(f"{bot.name:<24} {bot.status:<10} iteration {bot.iteration}{parent}: {bot.idea}")
    return 0


def _new(arguments: argparse.Namespace) -> int:
    bot = roster.new_bot(arguments.name, arguments.parent, arguments.iteration, arguments.idea)
    print(f"created {bot.directory} as a candidate, copied from {bot.parent}")
    return 0


def _new_map(arguments: argparse.Namespace) -> int:
    if not re.fullmatch(r"[a-z][a-z0-9-]*", arguments.name) or list(MAPS.glob(f"*/{arguments.name}.json")):
        raise ValueError(f"{arguments.name!r} is taken or not a map name: lower-case letters, digits and -")
    target = MAPS / arguments.set / f"{arguments.name}.json"
    target.write_text(json.dumps(maps.generate(arguments.name, arguments.seed), indent=2) + "\n", encoding="utf-8")
    print(target)
    return 0


def _status(arguments: argparse.Namespace) -> int:
    bot = roster.set_status(arguments.name, arguments.status)
    print(f"{bot.name} is now {bot.status}")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Run the ``league`` command."""
    parser = argparse.ArgumentParser(prog="league", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    play = commands.add_parser(
        "tournament",
        help="play every pair of bots on every map from both sides, and print the standings",
    )
    play.add_argument("--bots", help="the bots, by name; default: every bot that is not a candidate")
    play.add_argument(
        "--focus",
        help="play only the pairs with one of these bots (added to the bots), and list their lost games and longest "
        "wins; quick, but its ratings come from those pairs alone",
    )
    play.add_argument(
        "--add",
        help="add these bots, candidates too, to the whole round robin, and list their lost games and longest wins",
    )
    play.add_argument(
        "--parents",
        action="store_true",
        help="with --focus: play each focused bot against its parent alone, the head-to-head rule of the selection "
        "and the gate on those games",
    )
    play.add_argument("--anchors", default="1,2,3", help="default bot levels to add; '' for none")
    play.add_argument(
        "--no-opponents", action="store_true", help="leave out the outside opponents of opponents.local.toml"
    )
    play.add_argument("--maps", default="train", help="train, holdout, all, or map names")
    play.add_argument("--max-generations", type=int, default=300)
    play.add_argument("--turn-timeout-milliseconds", type=int, default=2000)
    play.add_argument("--parallel", type=int, default=0, help="matches at once; default: the CPUs")
    play.add_argument("--no-cache", action="store_true", help="play every match again")
    play.add_argument("--run-id", help="the directory under runs/; default: the time")
    play.add_argument(
        "--strict",
        action="store_true",
        help="exit with status 1 when a match was not played, a player failed a turn or there was no match",
    )
    play.set_defaults(handler=_tournament)

    study = commands.add_parser("digest", help="print a demo as a timeline, events and logs")
    study.add_argument("demo")
    study.add_argument("--every", type=int, default=10, help="turns per timeline row")
    study.add_argument("--turns", help="show these turns whole, such as 40-55")
    study.add_argument("--logs", default="all", help="with --turns: a team's name, all or none")
    study.add_argument(
        "--key-events",
        action="store_true",
        help="list only captures, eliminations, upgrades and bursts; a game with over 250 events is listed so anyway",
    )
    study.set_defaults(handler=_digest)

    replay = commands.add_parser(
        "replay",
        help="count how closely a bot reproduces one team's commands in saved demos, to build and re-check a "
        "sparring bot that imitates a real opponent",
    )
    replay.add_argument(
        "demo", nargs="+", help="demos, packed with gzip or not, such as lobby games against the opponent"
    )
    replay.add_argument("--bot", required=True, help="the league bot to replay, by name (bots/NAME/bot.py)")
    replay.add_argument(
        "--team", type=int, choices=(1, 2), default=2, help="the team's colour to imitate; default 2, the opponent"
    )
    replay.add_argument("--examples", type=int, default=4, help="examples listed under each kind of disagreement")
    replay.set_defaults(handler=_replay)

    again = commands.add_parser(
        "rematch",
        help="play studied games again with a candidate in its parent's seat: the result, and the first turn it "
        "commanded something else",
    )
    again.add_argument("demo", nargs="+", help="league games' demos, as a tournament listed them (runs/cache/...)")
    again.add_argument("--bot", required=True, help="the candidate, by name")
    again.add_argument("--replaces", help="whose seat it takes; default: its parent")
    again.add_argument("--max-generations", type=int, default=300, help="as the studied games were played")
    again.add_argument("--turn-timeout-milliseconds", type=int, default=2000, help="as the studied games were played")
    again.add_argument("--run-id", help="the directory under runs/ for the bots' stderr; default: rematch-BOT")
    again.set_defaults(handler=_rematch)

    unpack = commands.add_parser("unpack", help="unpack a demo for the demo viewer, and print its path")
    unpack.add_argument("demo")
    unpack.add_argument("--output")
    unpack.set_defaults(handler=_unpack)

    brief = commands.add_parser(
        "ledger",
        help="print the ledger as an iteration starts from it: the lessons, every candidate tried with its idea "
        "and decision, and the last entries in full",
    )
    brief.add_argument("--recent", type=int, default=3, help="iterations to print in full")
    brief.set_defaults(handler=_ledger)

    listing = commands.add_parser("roster", help="list the bots")
    listing.add_argument("--json", action="store_true")
    listing.set_defaults(handler=_roster)

    new = commands.add_parser("new", help="copy a bot to a new candidate")
    new.add_argument("name")
    new.add_argument("--parent", required=True)
    new.add_argument("--iteration", type=int, required=True)
    new.add_argument("--idea", required=True)
    new.set_defaults(handler=_new)

    status = commands.add_parser("status", help="set a bot's status")
    status.add_argument("name")
    status.add_argument("status", choices=roster.STATUSES)
    status.set_defaults(handler=_status)

    new_map = commands.add_parser("new-map", help="make a fair two-team map from a seed")
    new_map.add_argument("name")
    new_map.add_argument("--seed", type=int, required=True)
    new_map.add_argument("--set", choices=("train", "holdout"), required=True)
    new_map.set_defaults(handler=_new_map)

    arguments = parser.parse_args(argv)
    try:
        return arguments.handler(arguments)
    except (ValueError, RuntimeError, OSError) as error:
        print(f"league: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
