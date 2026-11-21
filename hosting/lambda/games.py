"""The hosted bot's record of its real games, kept in S3 as zips.

A hosted bot sees a game only through its turn deliveries: the board of every
generation it plays, its own answer and its own log lines. The game tells it
neither that the game ended nor how, and its demo endpoint is for the roster's
players, not their bots. So the bot keeps every turn it plays, and once the
game is over (its last turn, or no new turn long after the last one's
deadline) packs them into ``games/<id>/game-<id>.zip``:

- ``demo.json``: a demo in the game's own format (schema 2), one frame per
  turn the bot played, with the bot's log lines; ``league digest`` and the
  demo viewer open it. It lacks the final generation, the outcome and the
  other teams' logs, which only the game has.
- ``turns.jsonl``: each turn's commands, memory, time to play and whether the
  server took the answer.
- ``game.json``: the summary the home page shows.

The result is estimated from the last board the bot saw, and says so.
"""

from __future__ import annotations

import io
import json
import zipfile
from collections.abc import Callable, Iterable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Protocol

# How long after the last turn's deadline a game with no new turn is over.
STALE_AFTER_DEADLINE = timedelta(seconds=60)
# How long a game whose turns have no deadline may wait for its next turn.
STALE_WITHOUT_DEADLINE = timedelta(minutes=30)
# A game is "playing" on the home page while its last turn is this recent.
LIVE_WINDOW = timedelta(seconds=90)
# The S3 requests made at once when reading many objects.
PARALLEL_READS = 16
PREFIX = "games/"


class Store(Protocol):
    """Where the games are kept: an S3 bucket, or a dict in tests."""

    def put(self, key: str, body: bytes, content_type: str) -> None:
        """Write an object."""
        ...

    def get(self, key: str) -> bytes | None:
        """Read an object, or None when it doesn't exist."""
        ...

    def keys(self, prefix: str) -> list[str]:
        """Every key under prefix."""
        ...

    def download_url(self, key: str, filename: str) -> str:
        """A short-lived URL that downloads the object as filename."""
        ...


class S3Store:
    """A Store on an S3 bucket."""

    def __init__(self, bucket: str) -> None:
        """Use the bucket with the function's own credentials."""
        import boto3  # noqa: PLC0415 - in Lambda's runtime, not the bot's

        self.bucket = bucket
        self.s3 = boto3.client("s3")

    def put(self, key: str, body: bytes, content_type: str) -> None:
        """Write an object."""
        self.s3.put_object(Bucket=self.bucket, Key=key, Body=body, ContentType=content_type)

    def get(self, key: str) -> bytes | None:
        """Read an object, or None when it doesn't exist."""
        try:
            return self.s3.get_object(Bucket=self.bucket, Key=key)["Body"].read()
        except self.s3.exceptions.NoSuchKey:
            return None

    def keys(self, prefix: str) -> list[str]:
        """Every key under prefix."""
        found: list[str] = []
        for page in self.s3.get_paginator("list_objects_v2").paginate(Bucket=self.bucket, Prefix=prefix):
            found.extend(item["Key"] for item in page.get("Contents", []))
        return found

    def download_url(self, key: str, filename: str) -> str:
        """A presigned GET valid for five minutes."""
        return self.s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": self.bucket,
                "Key": key,
                "ResponseContentDisposition": f'attachment; filename="{filename}"',
            },
            ExpiresIn=300,
        )


class MemoryStore:
    """A Store in memory, for tests and local runs."""

    def __init__(self) -> None:
        """Start empty."""
        self.objects: dict[str, bytes] = {}

    def put(self, key: str, body: bytes, content_type: str) -> None:
        """Write an object."""
        self.objects[key] = body

    def get(self, key: str) -> bytes | None:
        """Read an object, or None when it doesn't exist."""
        return self.objects.get(key)

    def keys(self, prefix: str) -> list[str]:
        """Every key under prefix."""
        return sorted(key for key in self.objects if key.startswith(prefix))

    def download_url(self, key: str, filename: str) -> str:
        """The key itself."""
        return f"memory://{key}"


def game_key(game_id: int) -> str:
    """The key of a game's summary."""
    return f"{PREFIX}{game_id}/game.json"


def turn_key(game_id: int, turn_number: int) -> str:
    """The key of one recorded turn."""
    return f"{PREFIX}{game_id}/turns/{turn_number:05d}.json"


def zip_key(game_id: int) -> str:
    """The key of a finished game's zip."""
    return f"{PREFIX}{game_id}/game-{game_id}.zip"


def _now_text(now: datetime) -> str:
    return now.astimezone(UTC).isoformat(timespec="seconds")


def _time(text: str | None) -> datetime | None:
    return datetime.fromisoformat(text) if text else None


def _json(value: object) -> bytes:
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode()


# Maps -------------------------------------------------------------------


def _shape(castles: Iterable[dict[str, Any]]) -> frozenset[tuple[float, float]]:
    return frozenset((round(float(castle["x"]), 1), round(float(castle["y"]), 1)) for castle in castles)


@dataclass(frozen=True)
class KnownMaps:
    """The maps the league knows, by where their castles stand."""

    shapes: dict[frozenset[tuple[float, float]], str]

    @classmethod
    def load(cls, *directories: Path) -> KnownMaps:
        """Read every map file under the directories."""
        shapes: dict[frozenset[tuple[float, float]], str] = {}
        for directory in directories:
            for path in sorted(directory.glob("**/*.json")):
                data = json.loads(path.read_text())
                shapes.setdefault(_shape(data["castles"]), data.get("map_name") or path.stem)
        return cls(shapes)

    def name(self, generation: dict[str, Any]) -> str:
        """The map's name, or what it is: "8 castles, 2 teams"."""
        castles = generation["castles"]
        known = self.shapes.get(_shape(castles))
        if known:
            return known
        teams = {castle["team_color"] for castle in castles} - {0}
        teams |= {group["team_color"] for group in generation["soldier_groups"]}
        return f"{len(castles)} castles, {len(teams)} teams"


# Recording turns --------------------------------------------------------


def _strength(generation: dict[str, Any], color: int) -> tuple[int, int]:
    castles = [castle for castle in generation["castles"] if castle["team_color"] == color]
    soldiers = sum(castle["soldiers"] for castle in castles)
    soldiers += sum(group["soldiers"] for group in generation["soldier_groups"] if group["team_color"] == color)
    return len(castles), soldiers


def _others(generation: dict[str, Any], color: int) -> set[int]:
    teams = {castle["team_color"] for castle in generation["castles"]}
    teams |= {group["team_color"] for group in generation["soldier_groups"]}
    return teams - {0, color}


def record_turn(
    store: Store,
    *,
    bot: str,
    turn: dict[str, Any],
    result: dict[str, Any],
    submitted: int | None,
    play_ms: float,
    maps: KnownMaps,
    now: datetime,
) -> dict[str, Any]:
    """Keep one played turn and update its game's summary; returns the summary.

    turn is the delivered BotTurn as JSON, result the BotTurnResult that was
    submitted and submitted the HTTP status the server answered it with.
    """
    game_id = turn["game_id"]
    number = turn["turn_number"]
    generation = turn["generation"]
    color = turn["team_color"]
    record = {
        "received_at": _now_text(now),
        "turn": turn,
        "result": result,
        "submit_status": submitted,
        "play_ms": round(play_ms, 1),
    }
    store.put(turn_key(game_id, number), _json(record), "application/json")

    old = json.loads(store.get(game_key(game_id)) or b"null") or {}
    deadline = _time(turn.get("turn_deadline_at"))
    stale_at = deadline + STALE_AFTER_DEADLINE if deadline else now + STALE_WITHOUT_DEADLINE
    ours, theirs = _strength(generation, color), [_strength(generation, other) for other in _others(generation, color)]
    accepted = submitted is not None and 200 <= submitted < 300
    summary = {
        "game_id": game_id,
        "bot": bot,
        "team_color": color,
        "max_generations": turn["max_generations"],
        "map": old.get("map") or maps.name(generation),
        "first_turn_at": old.get("first_turn_at") or _now_text(now),
        "updated_at": _now_text(now),
        "stale_at": _now_text(stale_at),
        "first_turn": min(number, old.get("first_turn", number)),
        "last_turn": max(number, old.get("last_turn", 0)),
        "turns": old.get("turns", 0) + 1,
        "accepted": old.get("accepted", 0) + int(accepted),
        "commands": old.get("commands", 0) + len(result.get("commands", [])),
        "passed": old.get("passed", 0) + int(_passed(result)),
        "slowest_ms": max(round(play_ms, 1), old.get("slowest_ms", 0)),
        "castles": ours[0],
        "soldiers": ours[1],
        "enemy_castles": sum(team[0] for team in theirs),
        "enemy_soldiers": sum(team[1] for team in theirs),
        "status": "playing",
        "result": None,
        "result_note": None,
        "zip": None,
    }
    store.put(game_key(game_id), _json(summary), "application/json")
    return summary


def _passed(result: dict[str, Any]) -> bool:
    return any(line.get("logger") == "island_battles.bots" for line in result.get("logs", []))


# Finishing games --------------------------------------------------------


def _castles(count: int) -> str:
    return f"{count} castle" if count == 1 else f"{count} castles"


def estimate_result(summary: dict[str, Any]) -> tuple[str, str]:
    """The likely result from the last board the bot saw, and why.

    The bot never sees the final generation. A game that reached its last turn
    is decided by castles; one that stopped early ended in an elimination,
    which the stronger side most likely did.
    """
    ours = (summary["castles"], summary["soldiers"])
    theirs = (summary["enemy_castles"], summary["enemy_soldiers"])
    if summary["last_turn"] >= summary["max_generations"] - 1:
        if ours[0] == theirs[0]:
            return "draw", f"reached the turn limit with {_castles(ours[0])} each on the last board seen"
        result = "won" if ours[0] > theirs[0] else "lost"
        return result, f"reached the turn limit, {_castles(ours[0])} to {theirs[0]} on the last board seen"
    if theirs == (0, 0):
        return "won", "no enemy left on the last board seen"
    result = "won" if ours > theirs else "lost"
    return result, (
        f"ended at turn {summary['last_turn'] + 1} of {summary['max_generations']}: "
        f"{_castles(ours[0])} and {ours[1]} soldiers to {theirs[0]} and {theirs[1]} on the last board seen"
    )


def _read_turns(store: Store, game_id: int) -> list[dict[str, Any]]:
    keys = store.keys(f"{PREFIX}{game_id}/turns/")
    with ThreadPoolExecutor(PARALLEL_READS) as pool:
        bodies = list(pool.map(store.get, keys))
    turns = [json.loads(body) for body in bodies if body]
    return sorted(turns, key=lambda record: record["turn"]["turn_number"])


def build_demo(summary: dict[str, Any], turns: list[dict[str, Any]], now: datetime) -> dict[str, Any]:
    """A demo in the game's format from the turns the bot played."""
    color = summary["team_color"]
    first = turns[0]["turn"]["generation"]
    others = sorted(_others(first, color))
    teams = [{"color": color, "name": summary["bot"], "players": [summary["bot"]]}]
    teams += [{"color": other, "name": f"Team {other}", "players": []} for other in others]
    frames = [record["turn"]["generation"] for record in turns]
    logs = [
        {
            "generation_id": record["turn"]["generation"]["id"],
            "hidden_team_colors": others,
            "players": [
                {"display_name": summary["bot"], "team_color": color, "lines": record["result"].get("logs", [])}
            ],
        }
        for record in turns
    ]
    return {
        "format": "island-battles-demo",
        "schema_version": 2,
        "game_id": summary["game_id"],
        "saved_at": _now_text(now),
        "teams": teams,
        "frames": frames,
        "logs": logs,
        # The game's outcome isn't sent to a bot; game.json has the estimate.
        "outcome": None,
    }


def finish(store: Store, game_id: int, now: datetime) -> dict[str, Any] | None:
    """Pack a game into its zip and mark it finished; returns the summary."""
    summary = json.loads(store.get(game_key(game_id)) or b"null")
    if not summary:
        return None
    turns = _read_turns(store, game_id)
    if not turns:
        return None
    result, note = estimate_result(summary)
    summary.update(status="finished", result=result, result_note=note, finished_at=_now_text(now))
    summary["zip"] = zip_key(game_id)
    lines = [
        json.dumps(
            {
                "turn_number": record["turn"]["turn_number"],
                "generation_id": record["turn"]["generation"]["id"],
                "received_at": record["received_at"],
                "play_ms": record["play_ms"],
                "submit_status": record["submit_status"],
                "commands": record["result"].get("commands", []),
                "memory": record["result"].get("memory"),
            },
            separators=(",", ":"),
        )
        for record in turns
    ]
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("demo.json", json.dumps(build_demo(summary, turns, now), separators=(",", ":")))
        archive.writestr("turns.jsonl", "\n".join(lines) + "\n")
        archive.writestr("game.json", json.dumps(summary, indent=2))
    store.put(zip_key(game_id), buffer.getvalue(), "application/zip")
    store.put(game_key(game_id), _json(summary), "application/json")
    return summary


def is_over(summary: dict[str, Any], now: datetime) -> bool:
    """Whether a game still marked playing is over."""
    if summary.get("status") == "finished":
        return False
    if summary["last_turn"] >= summary["max_generations"] - 1:
        return True
    stale_at = _time(summary.get("stale_at"))
    return stale_at is not None and now >= stale_at


def all_games(store: Store) -> list[dict[str, Any]]:
    """Every game's summary, newest first."""
    keys = [key for key in store.keys(PREFIX) if key.endswith("/game.json")]
    with ThreadPoolExecutor(PARALLEL_READS) as pool:
        bodies = list(pool.map(store.get, keys))
    games = [json.loads(body) for body in bodies if body]
    return sorted(games, key=lambda game: game["game_id"], reverse=True)


def finish_over_games(store: Store, now: datetime, games: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Pack every game that is over; returns all summaries, newest first."""
    games = all_games(store) if games is None else games
    finished: dict[int, dict[str, Any]] = {}
    for game in games:
        if is_over(game, now):
            done = finish(store, game["game_id"], now)
            if done:
                finished[game["game_id"]] = done
    return [finished.get(game["game_id"], game) for game in games]


def overview(games: list[dict[str, Any]], now: datetime) -> dict[str, Any]:
    """The home page's numbers."""
    record = {"won": 0, "lost": 0, "draw": 0}
    for game in games:
        if game.get("result") in record:
            record[game["result"]] += 1
    latest = max(games, key=lambda game: game["updated_at"]) if games else None
    live = bool(latest and now - datetime.fromisoformat(latest["updated_at"]) < LIVE_WINDOW)
    return {
        "games": len(games),
        "record": record,
        "turns": sum(game["turns"] for game in games),
        "accepted": sum(game["accepted"] for game in games),
        "passed": sum(game["passed"] for game in games),
        "slowest_ms": max((game["slowest_ms"] for game in games), default=0),
        "latest": latest,
        "live": live,
    }


def safely(action: Callable[[], Any], report: Callable[[str], None]) -> Any:  # noqa: ANN401 - whatever action returns
    """Run action, reporting rather than raising: keeping games never costs a turn."""
    try:
        return action()
    except Exception as error:  # noqa: BLE001 - see above
        report(f"games: {type(error).__name__}: {error}")
        return None
