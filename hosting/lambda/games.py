"""The hosted bot's record of its real games, kept in S3 as zips.

The bot keeps every turn it plays, after submitting it: the board, its answer,
its log lines, the server's status and the time it took. When the game ends,
the game POSTs a ``GameEndedDelivery`` to the bot's ``/game-ended`` (#413 of
the game): the outcome, the final generation and a link that downloads the
game's demo, with every team's logs. The bot downloads it and packs the game
into ``games/<id>/game-<id>.zip``:

- ``demo.json``: the game's own demo; ``league digest`` and the demo viewer
  open it.
- ``turns.jsonl``: each turn's commands, memory, time to play and whether the
  server took the answer.
- ``game.json``: the summary the home page shows.
- ``game-ended.json``: the end of the game as it was delivered, without its
  demo link.
- ``digest.txt``: ``league digest`` of the demo: the timeline, each team's
  logistics and the events.
- ``README.txt``: what each file is.

A download that fails is tried again whenever the games are read, until the
link expires. A game whose end never arrives (a runner that failed, or a game
played before the game sent ends) is packed from the turns the bot kept, once
no turn came long after the last one's deadline: its demo stops at the bot's
last turn and lacks the other teams' logs, and its result is estimated from
the last board the bot saw, and says so.
"""

from __future__ import annotations

import gzip
import importlib
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


def end_key(game_id: int) -> str:
    """The key of a game's end, as it was delivered."""
    return f"{PREFIX}{game_id}/game-ended.json"


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
    detail: str = "",
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
        "submit_detail": detail or None,
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
        # Only the game's own demo has the outcome; game.json has the result.
        "outcome": None,
    }


def _turn_lines(turns: list[dict[str, Any]]) -> str:
    lines = [
        json.dumps(
            {
                "turn_number": record["turn"]["turn_number"],
                "generation_id": record["turn"]["generation"]["id"],
                "received_at": record["received_at"],
                "play_ms": record["play_ms"],
                "submit_status": record["submit_status"],
                "submit_detail": record.get("submit_detail"),
                "commands": record["result"].get("commands", []),
                "memory": record["result"].get("memory"),
            },
            separators=(",", ":"),
        )
        for record in turns
    ]
    return "".join(line + "\n" for line in lines)


_README = """Island Battles game {game_id}, played by the hosted bot {bot} as team {team}.

demo.json        The game's demo ({demo}). Open it with `league digest`, `league unpack` or
                 the game's demo viewer; `league digest` also takes this zip as it is.
digest.txt       `league digest` of the demo: the timeline, each team's logistics and the events.
turns.jsonl      One line per turn the bot played: its commands and memory, how long it took,
                 the server's status for its answer, and the server's reason when it refused it.
game.json        The summary that the bot's home page shows.
game-ended.json  The end of the game as the game delivered it: the outcome, the final
                 generation and the bot's last memory (only when the game sent it).

Result: {result}{estimated}. {note}
"""

_DEMO_KINDS = {
    "full": "the game's own, with every team's logs and the outcome",
    "pending": "rebuilt from the bot's turns for now: the game's own is downloaded later",
    "partial": "rebuilt from the bot's turns: it stops at the bot's last turn, without the other teams' logs",
}


def _digest(demo: bytes) -> str:
    """The league's digest of a demo, or why there is none."""
    try:
        try:
            module = importlib.import_module("league_tools.digest")
        except ImportError:
            module = importlib.import_module("digest")
        return module.digest(json.loads(demo), key_only=False)
    except Exception as error:  # noqa: BLE001 - a zip without a digest is still a zip
        return f"No digest: {type(error).__name__}: {error}\n"


def _pack(
    store: Store,
    summary: dict[str, Any],
    demo: bytes,
    turns: list[dict[str, Any]],
    end: dict[str, Any] | None,
) -> None:
    """Write the game's zip and its summary."""
    summary["zip"] = zip_key(summary["game_id"])
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("demo.json", demo)
        archive.writestr("digest.txt", _digest(demo))
        archive.writestr("turns.jsonl", _turn_lines(turns))
        archive.writestr("game.json", json.dumps(summary, indent=2))
        if end is not None:
            archive.writestr("game-ended.json", json.dumps(_without_link(end), indent=2))
        archive.writestr(
            "README.txt",
            _README.format(
                game_id=summary["game_id"],
                bot=summary["bot"],
                team=summary["team_color"],
                demo=_DEMO_KINDS.get(summary.get("demo", "partial"), "?"),
                result=summary.get("result"),
                estimated=", estimated" if summary.get("estimated") else "",
                note=summary.get("result_note") or "",
            ),
        )
    store.put(zip_key(summary["game_id"]), buffer.getvalue(), "application/zip")
    store.put(game_key(summary["game_id"]), _json(summary), "application/json")


def _without_link(end: dict[str, Any]) -> dict[str, Any]:
    """The end without its demo link, whose token downloads the demo."""
    return {**end, "demo": {"expires_at": end.get("demo", {}).get("expires_at")}}


def finish(store: Store, game_id: int, now: datetime) -> dict[str, Any] | None:
    """Pack a game whose end never came from the turns the bot kept, with an estimated result."""
    summary = json.loads(store.get(game_key(game_id)) or b"null")
    if not summary:
        return None
    turns = _read_turns(store, game_id)
    if not turns:
        return None
    result, note = estimate_result(summary)
    summary.update(status="finished", result=result, result_note=note, finished_at=_now_text(now))
    summary.update(estimated=True, demo="partial")
    demo = json.dumps(build_demo(summary, turns, now), separators=(",", ":")).encode()
    _pack(store, summary, demo, turns, None)
    return summary


def record_end(store: Store, end: dict[str, Any]) -> None:
    """Keep a game's end as it was delivered, demo link included, until the demo is in."""
    store.put(end_key(end["game_id"]), _json(end), "application/json")


def _result(outcome: dict[str, Any], color: int) -> str:
    winner = outcome.get("winner_team_color")
    if winner is None:
        return "draw"
    return "won" if winner == color else "lost"


def _opponents(demo: dict[str, Any], color: int) -> list[str]:
    """The other teams as the demo names them: the team, then its players."""
    named = []
    for team in demo.get("teams", []):
        if team.get("color") == color:
            continue
        players = ", ".join(team.get("players") or [])
        named.append(f"{team.get('name')} ({players})" if players else str(team.get("name")))
    return named


def complete(
    store: Store,
    game_id: int,
    download: Callable[[str], bytes],
    maps: KnownMaps,
    bot: str,
    now: datetime,
) -> dict[str, Any] | None:
    """Pack a game whose end was delivered, with the game's own demo; returns the summary.

    When the demo can't be downloaded, the game is packed from the turns the
    bot kept, with the delivered outcome, and marked to try again while the
    link lasts.
    """
    end = json.loads(store.get(end_key(game_id)) or b"null")
    if not end:
        return None
    old = json.loads(store.get(game_key(game_id)) or b"null") or {}
    color = end["team_color"]
    final = end["generation"]
    ours, theirs = _strength(final, color), [_strength(final, other) for other in _others(final, color)]
    turns = _read_turns(store, game_id)
    summary = {
        "game_id": game_id,
        "bot": old.get("bot", bot),
        "team_color": color,
        "max_generations": old.get("max_generations", end["turn_number"] + 1),
        "map": old.get("map") or maps.name(final),
        "first_turn_at": old.get("first_turn_at") or _now_text(now),
        "updated_at": old.get("updated_at") or _now_text(now),
        "first_turn": old.get("first_turn", 1),
        "last_turn": old.get("last_turn", 0),
        "turns": old.get("turns", 0),
        "accepted": old.get("accepted", 0),
        "commands": old.get("commands", 0),
        "passed": old.get("passed", 0),
        "slowest_ms": old.get("slowest_ms", 0),
        "final_turn": end["turn_number"],
        "castles": ours[0],
        "soldiers": ours[1],
        "enemy_castles": sum(team[0] for team in theirs),
        "enemy_soldiers": sum(team[1] for team in theirs),
        "status": "finished",
        "result": _result(end["outcome"], color),
        "result_note": end["outcome"].get("summary"),
        "reason": end["outcome"].get("reason"),
        "estimated": False,
        "finished_at": _now_text(now),
        "opponents": old.get("opponents", []),
    }
    link = end.get("demo") or {}
    expires = _time(link.get("expires_at"))
    demo: bytes | None = None
    if link.get("url") and (expires is None or now < expires):
        try:
            demo = download(link["url"])
            if demo[:2] == b"\x1f\x8b":
                demo = gzip.decompress(demo)
            parsed = json.loads(demo)
            if parsed.get("format") != "island-battles-demo":
                raise ValueError("the download is not an Island Battles demo")
            summary["opponents"] = _opponents(parsed, color)
        except Exception as error:  # noqa: BLE001 - kept to try again
            summary["demo_error"] = f"{type(error).__name__}: {error}"[:300]
            demo = None
    if demo is not None:
        summary["demo"] = "full"
    else:
        # Packed from the bot's own turns for now, and tried again later.
        summary["demo"] = "pending" if expires is None or now < expires else "partial"
        if not turns:
            store.put(game_key(game_id), _json(summary), "application/json")
            return summary
        demo = json.dumps(build_demo(summary, turns, now), separators=(",", ":")).encode()
    _pack(store, summary, demo, turns, end)
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


def finish_over_games(
    store: Store,
    now: datetime,
    download: Callable[[str], bytes] | None = None,
    maps: KnownMaps | None = None,
) -> list[dict[str, Any]]:
    """Pack every game that is over, and download the demos still pending; returns all summaries, newest first."""
    games = all_games(store)
    finished: dict[int, dict[str, Any]] = {}
    for game in games:
        done: dict[str, Any] | None = None
        if game.get("demo") == "pending" and download is not None:
            done = complete(store, game["game_id"], download, maps or KnownMaps({}), game["bot"], now)
        elif is_over(game, now):
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
