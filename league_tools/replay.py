"""Replay a team's turns in saved demos through a league bot, and count where the bot agrees.

Its purpose is building and re-checking a sparring bot (``status = "sparring"``)
that imitates a real opponent, from lobby demos of games against it. For every
turn of one team the replay reads the team's real commands off the demo
(``team_commands``), builds the turn the team saw, plays it through the bot's
worker, as a tournament does, and compares the two sets of commands, by category. Each turn is replayed
open loop: the bot always sees the real board, never one its own commands made.

Categories, by the board of the turn:

- upgrade: a (castle, type) bought; compared per turn as exact multisets
- neutral: sends at a neutral castle, summed per target; same target, total within 1
- attack: sends at an enemy castle, summed per target; same target, total within 2
- defence: sends to an own castle that enemy groups are bound for, per target; total within 2
- feed: other sends to an own castle, per (origin, target); amount within 1
- idle: turns with no command at all
"""

from __future__ import annotations

import collections
import math
from pathlib import Path
from typing import Any

from island_battles_client import BotTurn
from island_battles_client.fixture import fixture_turn_data

from .digest import load_demo
from .gobots import Worker, WorkerError
from .roster import load_bot

# The most a category's total may differ from the team's and still count as the same command.
TOLERANCE = {"neutral": 1, "attack": 2, "defence": 2, "feed": 1}
CATEGORIES = tuple(TOLERANCE)
MAX_GENERATIONS = 300
# How many kinds of disagreement the report lists.
LISTED_KINDS = 14

Send = tuple[int, int, int]
Upgrade = tuple[Any, str]


def upgrade_table() -> list[dict[str, Any]]:
    """The upgrade table of the game; the demos don't carry one."""
    return fixture_turn_data()["upgrades"]


def _costs() -> dict[str, list[int]]:
    return {entry["type"]: [level["soldier_cost"] for level in entry["levels"]] for entry in upgrade_table()}


def team_commands(demo: dict[str, Any], color: int) -> list[dict[str, Any]]:
    """What a team commanded in each turn, read off the board of the turn and the next.

    Frame i is the board the players saw at turn i + 1, and the commands of that
    turn made frame i + 1: a group new on it is a send, a raised level an
    upgrade, a raised burst debt a burst. A group that left and was destroyed in
    the same turn is on no board; it is listed as ``unseen`` with the size it had
    in its clash, and the comparison leaves it out.
    """
    costs = _costs()
    frames = demo["frames"]
    turns = []
    for index in range(len(frames) - 1):
        before, after = frames[index], frames[index + 1]
        castles_before = {castle["id"]: castle for castle in before["castles"]}
        known = {group["id"] for group in before["soldier_groups"]}
        upgrades: list[dict[str, Any]] = []
        sends: list[dict[str, Any]] = []
        for castle in after["castles"]:
            earlier = castles_before[castle["id"]]
            if earlier["team_color"] != color:
                continue
            for kind, level in castle["upgrades"].items():
                for new_level in range(earlier["upgrades"].get(kind, 1) + 1, level + 1):
                    cost = costs.get(kind, [0] * new_level)[new_level - 1]
                    upgrades.append({"castle": castle["id"], "type": kind, "level": new_level, "cost": cost})
            if castle["burst_debt"] > earlier["burst_debt"]:
                upgrades.append({"castle": castle["id"], "type": "burst", "level": castle["burst_debt"], "cost": 0})
        for group in after["soldier_groups"]:
            if group["id"] in known or group["team_color"] != color:
                continue
            origin = castles_before[group["origin_castle_id"]]
            target = castles_before[group["destination_castle_id"]]
            distance = math.hypot(origin["x"] - target["x"], origin["y"] - target["y"])
            sends.append(
                {
                    "origin": origin["id"],
                    "dest": target["id"],
                    "amount": group["soldiers"],
                    "distance": round(distance, 3),
                    "unseen": False,
                }
            )
        still_there = {group["id"] for group in after["soldier_groups"]}
        for clash in after["clashes"]:
            for member in clash["participants"]:
                if member["team_color"] == color and member["group_id"] not in known | still_there:
                    sends.append({"origin": None, "dest": None, "amount": member["soldiers_before"], "unseen": True})
        turns.append({"turn": index + 1, "upgrades": upgrades, "sends": sends})
    return turns


def _castle(castle: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": castle["id"],
        "team_color": castle["team_color"],
        "soldiers": castle["soldiers"],
        "x": float(castle["x"]),
        "y": float(castle["y"]),
        "upgrades": dict(castle["upgrades"]),
        "burst_debt": castle["burst_debt"],
    }


def _group(group: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": group["id"],
        "team_color": group["team_color"],
        "soldiers": group["soldiers"],
        "x": float(group["x"]),
        "y": float(group["y"]),
        "origin_castle_id": group["origin_castle_id"],
        "destination_castle_id": group["destination_castle_id"],
        "clash_radius": float(group.get("clash_radius", 0.25)),
        "upgrades": dict(group["upgrades"]),
    }


def bot_turn(demo: dict[str, Any], index: int, color: int) -> BotTurn:
    """The turn a team saw at frame ``index``: the real board, with the standard upgrade table."""
    frame = demo["frames"][index]
    return BotTurn.model_validate(
        {
            "game_id": max(1, int(demo.get("game_id") or 1)),
            "generation": {
                "id": index + 1,
                "castles": [_castle(castle) for castle in frame["castles"]],
                "soldier_groups": [_group(group) for group in frame["soldier_groups"]],
                "clashes": [],
            },
            "max_generations": MAX_GENERATIONS,
            "memory": None,
            "team_color": color,
            "turn_deadline_at": None,
            "turn_number": index + 1,
            "upgrades": upgrade_table(),
        }
    )


def classify(
    frame: dict[str, Any], color: int, upgrades: list[Upgrade], sends: list[Send]
) -> dict[str, collections.Counter]:
    """Sort a turn's upgrades and sends into the categories, by the board of the turn."""
    castles = {castle["id"]: castle for castle in frame["castles"]}
    threatened = {group["destination_castle_id"] for group in frame["soldier_groups"] if group["team_color"] != color}
    found: dict[str, collections.Counter] = {name: collections.Counter() for name in ("upgrade", *CATEGORIES)}
    found["upgrade"].update(upgrades)
    for origin, target, amount in sends:
        owner = castles[target]["team_color"]
        if owner == 0:
            found["neutral"][target] += amount
        elif owner != color:
            found["attack"][target] += amount
        elif target in threatened:
            found["defence"][target] += amount
        else:
            found["feed"][(origin, target)] += amount
    return found


def bot_commands(result: dict[str, Any]) -> tuple[list[Upgrade], list[Send]]:
    """The upgrades and sends in a bot's result (a BotTurnResult as JSON)."""
    upgrades: list[Upgrade] = []
    sends: list[Send] = []
    for command in result["commands"]:
        kind, parameters = command["command_type"], command["parameters"]
        if kind == "upgrade_castle":
            upgrades.append((parameters["castle_id"], str(parameters["upgrade_type"])))
        elif kind == "send_soldier_group":
            sends.append(
                (parameters["origin_castle_id"], parameters["destination_castle_id"], parameters["soldier_amount"])
            )
        else:
            upgrades.append((parameters.get("castle_id"), kind))
    return upgrades, sends


class Report:
    """What the replay counted, and where the bot and the team parted."""

    def __init__(self, bot: str, examples: int) -> None:
        """Start an empty report for ``bot``, listing ``examples`` places per kind of disagreement."""
        self.bot = bot
        self.examples = examples
        self.stats: collections.Counter[str] = collections.Counter()
        self.kinds: collections.Counter[str] = collections.Counter()
        self.where: dict[str, list[str]] = collections.defaultdict(list)

    def note(self, kind: str, where: str) -> None:
        """Count a disagreement of this kind, and keep where it was if there are not enough examples."""
        self.kinds[kind] += 1
        if len(self.where[kind]) < self.examples:
            self.where[kind].append(where)

    def text(self) -> str:
        """The numbers and the most common disagreements, as the command prints them."""
        stats = self.stats
        turns = stats["turns"]

        def share(part: int, whole: int) -> str:
            return f"{part}/{whole} ({100 * part / whole:.0f}%)" if whole else f"{part}/0"

        lines = [
            f"bot: {self.bot}",
            f"turns replayed: {turns}",
            f"exact turn match (same commands, same amounts): {share(stats['exact'], turns)}",
            f"loose turn match (tolerances per category): {share(stats['loose'], turns)}",
            f"idle turns: team {stats['team idle']}, bot {stats['bot idle']}, both {stats['both idle']}"
            f" -> of the team's idle turns the bot was idle too in {share(stats['both idle'], stats['team idle'])}",
            f"upgrades: turns with a purchase matched exactly {share(stats['upgrade match'], stats['upgrade turns'])};"
            f" recall {share(stats['upgrade tp'], stats['upgrade team'])},"
            f" precision {share(stats['upgrade tp'], stats['upgrade bot'])}",
        ]
        for name in CATEGORIES:
            lines.append(
                f"{name:<8}: recall {share(stats[name + ' tp'], stats[name + ' team'])},"
                f" precision {share(stats[name + ' tp'], stats[name + ' bot'])}  (tolerance {TOLERANCE[name]})"
            )
        lines += ["", "most common disagreements:"]
        for kind, count in self.kinds.most_common(LISTED_KINDS):
            lines.append(f"  {count:5d}  {kind}")
            lines += [f"           {where}" for where in self.where[kind]]
        return "\n".join(lines) + "\n"


def _compare(
    report: Report,
    frame: dict[str, Any],
    color: int,
    where: str,
    real: dict,
    bot_upgrades: list[Upgrade],
    bot_sends: list[Send],
) -> None:
    stats = report.stats
    real_sends = [(send["origin"], send["dest"], send["amount"]) for send in real["sends"] if not send["unseen"]]
    real_upgrades = [(upgrade["castle"], upgrade["type"]) for upgrade in real["upgrades"]]
    theirs = classify(frame, color, real_upgrades, real_sends)
    mine = classify(frame, color, bot_upgrades, bot_sends)
    stats["turns"] += 1
    stats["exact"] += (sorted(real_upgrades, key=str), sorted(real_sends)) == (
        sorted(bot_upgrades, key=str),
        sorted(bot_sends),
    )
    loose = True
    if theirs["upgrade"] or mine["upgrade"]:
        stats["upgrade turns"] += 1
        if theirs["upgrade"] == mine["upgrade"]:
            stats["upgrade match"] += 1
        else:
            loose = False
            for (castle, kind), _ in (theirs["upgrade"] - mine["upgrade"]).items():
                report.note(f"upgrade missed: the team bought {kind}", f"{where} c{castle}")
            for (castle, kind), _ in (mine["upgrade"] - theirs["upgrade"]).items():
                report.note(f"upgrade extra: the bot bought {kind}", f"{where} c{castle}")
    stats["upgrade team"] += sum(theirs["upgrade"].values())
    stats["upgrade tp"] += sum((theirs["upgrade"] & mine["upgrade"]).values())
    stats["upgrade bot"] += sum(mine["upgrade"].values())
    for name in CATEGORIES:
        real_side, bot_side = theirs[name], mine[name]
        stats[f"{name} team"] += len(real_side)
        stats[f"{name} bot"] += len(bot_side)
        for key, amount in real_side.items():
            if key in bot_side and abs(bot_side[key] - amount) <= TOLERANCE[name]:
                stats[f"{name} tp"] += 1
            elif key in bot_side:
                loose = False
                more = "bot more" if bot_side[key] > amount else "bot less"
                report.note(
                    f"{name}: same target, size off ({more})", f"{where} {key} team {amount} bot {bot_side[key]}"
                )
            else:
                loose = False
                other = "other target" if bot_side else "did not"
                report.note(
                    f"{name}: team sent, bot {other}", f"{where} {key} team {amount} bot {dict(bot_side) or '-'}"
                )
        for key, amount in bot_side.items():
            if key not in real_side:
                loose = False
                if not real_side:
                    report.note(f"{name}: bot sent, team did not", f"{where} {key} bot {amount}")
    team_idle = not real["upgrades"] and not real["sends"]
    bot_idle = not bot_upgrades and not bot_sends
    stats["team idle"] += team_idle
    stats["bot idle"] += bot_idle
    stats["both idle"] += team_idle and bot_idle
    stats["loose"] += loose


def replay(demos: list[tuple[str, dict[str, Any]]], bot_name: str, color: int = 2, examples: int = 4) -> Report:
    """Replay every turn of a team in the demos, which the team still had a castle in, through a bot."""
    load_bot(bot_name)
    report = Report(bot_name, examples)
    with Worker(bot_name) as bot:
        for name, demo in demos:
            for real in team_commands(demo, color):
                index = real["turn"] - 1
                frame = demo["frames"][index]
                if not any(castle["team_color"] == color for castle in frame["castles"]):
                    continue
                where = f"{name} t{real['turn']}"
                try:
                    result = bot.play(bot_turn(demo, index, color).model_dump(mode="json"))
                    upgrades, sends = bot_commands(result)
                except WorkerError as error:  # a bot that fails made no command
                    report.note(f"bot error: {(str(error).strip().splitlines() or ['no message'])[0][:60]}", where)
                    upgrades, sends = [], []
                _compare(report, frame, color, where, real, upgrades, sends)
    return report


def run(paths: list[Path], bot_name: str, color: int = 2, examples: int = 4) -> str:
    """The report of a bot's replay of a team's turns in the demos at ``paths``."""
    demos = [(path.name.split(".")[0], load_demo(path)) for path in paths]
    return replay(demos, bot_name, color, examples).text()
