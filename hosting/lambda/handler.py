"""An AWS Lambda function URL that plays a league bot as an Island Battles hosted bot.

The game POSTs a ``TurnDelivery`` to the bot's URL and waits up to 5 seconds for
any 2xx; the bot submits its answer itself, with the delivery's submit token,
to the game's ``POST /generation/commands``. That is the protocol of
``island-battles-bot serve``, and this handler plays and submits a turn with the
SDK's own code for it (``BotServer.play`` and ``BotServer.submit``): the same
time budget, the same pass when the bot fails or is slow, and the same retries.

Unlike ``serve``, it submits before it answers rather than after, since Lambda
freezes the instance once the handler returns. ``GET /health`` answers like
``serve``'s. ``BOT`` names the bot; by default it is the one that the file
``bot`` names, which ``build.sh`` packages next to this one.

With ``GAMES_BUCKET`` set, it also keeps every turn it plays in that bucket and
packs each finished game into a zip (``games.py``), and ``GET /`` is the bot's
home page, which lists them; ``GET /games/<id>.zip`` downloads one, with
``?key=`` the value of ``GAMES_KEY`` when that is set.
"""

from __future__ import annotations

import base64
import hmac
import json
import logging
import os
import re
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import games
import page
from island_battles_client._generated import BotTurnResult, TurnDelivery
from island_battles_client.cli import MAX_BODY_BYTES, BotServer, load_play, submit_refusal
from island_battles_client.game_log import ClientLogging
from pydantic import ValidationError

BOT = os.environ.get("BOT") or f"bots.{Path(__file__).with_name('bot').read_text().strip()}.bot:play"
# The longest a turn may play; the turn's deadline cuts it shorter, as in serve.
TURN_TIMEOUT_SECONDS = float(os.environ.get("TURN_TIMEOUT_SECONDS", "8"))
# The bucket that keeps the real games; without it nothing is kept.
GAMES_BUCKET = os.environ.get("GAMES_BUCKET", "")
# The key that downloads a game's zip; without it anyone may.
GAMES_KEY = os.environ.get("GAMES_KEY", "")
# The map files that name a game's map: packaged next to this file, or the repository's.
_HERE = Path(__file__).parent
MAPS = games.KnownMaps.load(*[path for path in (_HERE / "maps", _HERE.parent.parent / "maps") if path.is_dir()])
_ZIP_PATH = re.compile(r"^/games/(\d+)\.zip$")
_log = logging.getLogger("island_battles.hosting")


class _Bot:
    """The loaded bot, in the shape of ``serve``'s ``ReloadingPlay``."""

    def __init__(self, spec: str) -> None:
        """Load the bot's play function from ``module:function``."""
        self.spec = spec
        self._play = load_play(spec)

    def get(self) -> Any:  # noqa: ANN401 - the SDK's Play
        """The bot's play function."""
        return self._play


class LambdaBot:
    """What ``BotServer.play`` and ``BotServer.submit`` read, without a socket."""

    play = BotServer.play
    submit = BotServer.submit

    def __init__(self, spec: str, turn_timeout: float) -> None:
        """Load the bot and attach the logging that ``run_turn`` reads."""
        self.bot = _Bot(spec)
        self.turn_timeout = turn_timeout
        self.client_logging = ClientLogging(self, logging.INFO, True, None)
        self.client_logging.attach()
        # The batch that _post sent last, and the server's status for it.
        self.sent: tuple[BotTurnResult, int | None] | None = None

    @property
    def name(self) -> str:
        """The bot's name: its directory under bots/."""
        return self.bot.spec.split(":")[0].removeprefix("bots.").removesuffix(".bot")

    def _post(self, delivery: TurnDelivery, result: BotTurnResult) -> tuple[int | None, str, str | None]:
        """POST one batch as serve does, remembering what was sent and the answer."""
        answer = BotServer._post(self, delivery, result)  # ty: ignore[invalid-argument-type]
        self.sent = (result, answer[0])
        return answer

    def take(self, delivery: TurnDelivery, store: games.Store | None) -> None:
        """Play the delivered turn and submit the answer, or a pass; then keep the turn."""
        self.sent = None
        started = time.perf_counter()
        result: BotTurnResult = self.play(delivery)
        play_ms = (time.perf_counter() - started) * 1000
        self.submit(delivery, result)
        if store is None:
            return
        submitted, status = self.sent or (result, None)
        turn = delivery.turn

        def keep() -> None:
            now = datetime.now(UTC)
            summary = games.record_turn(
                store,
                bot=self.name,
                turn=turn.model_dump(mode="json", by_alias=True),
                result=submitted.model_dump(mode="json", by_alias=True),
                submitted=status,
                play_ms=play_ms,
                maps=MAPS,
                now=now,
            )
            if games.is_over(summary, now):
                games.finish(store, turn.game_id, now)
            elif turn.turn_number == 1:
                # A new game: a good moment to pack the games that are over.
                games.finish_over_games(store, now)

        games.safely(keep, _log.error)


_bot = LambdaBot(BOT, TURN_TIMEOUT_SECONDS)
_store: games.Store | None = games.S3Store(GAMES_BUCKET) if GAMES_BUCKET else None


def _answer(status: int, body: object) -> dict[str, Any]:
    """A function URL response with a JSON body."""
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def _games(store: games.Store) -> list[dict[str, Any]]:
    """Every game, newest first, after packing the ones that are over."""
    return games.finish_over_games(store, datetime.now(UTC))


def _home(store: games.Store | None) -> dict[str, Any]:
    """The home page."""
    listed = _games(store) if store else []
    summary = games.overview(listed, datetime.now(UTC))
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store"},
        "body": page.render(_bot.name, summary, listed, bool(GAMES_KEY)),
    }


def _zip(store: games.Store, game_id: int, key: str) -> dict[str, Any]:
    """Redirect to a short-lived download of a finished game's zip."""
    if GAMES_KEY and not hmac.compare_digest(key.encode(), GAMES_KEY.encode()):
        return _answer(403, {"detail": "a game's zip needs the owner's key: ?key=..."})
    if store.get(games.game_key(game_id)) is None:
        return _answer(404, {"detail": f"no game {game_id}"})
    games.finish_over_games(store, datetime.now(UTC))
    summary = json.loads(store.get(games.game_key(game_id)) or b"{}")
    if not summary.get("zip"):
        return _answer(409, {"detail": f"game {game_id} is still being played"})
    url = store.download_url(summary["zip"], f"island-battles-game-{game_id}.zip")
    return {"statusCode": 302, "headers": {"Location": url, "Cache-Control": "no-store"}, "body": ""}


def handler(event: dict[str, Any], context: object) -> dict[str, Any]:
    """Answer one function URL request: ``POST /turn``, the home page, the games or ``GET /health``."""
    http = event.get("requestContext", {}).get("http", {})
    method = http.get("method", "")
    path = event.get("rawPath", "/")
    if method == "GET" and path == "/health":
        return _answer(200, {"name": _bot.bot.spec, "ok": True, "games": _store is not None})
    if method == "GET" and path == "/":
        return _home(_store)
    if method == "GET" and path == "/api/games":
        listed = _games(_store) if _store else []
        return _answer(200, {"overview": games.overview(listed, datetime.now(UTC)), "games": listed})
    zip_path = _ZIP_PATH.match(path)
    if method == "GET" and zip_path:
        if _store is None:
            return _answer(404, {"detail": "this bot keeps no games"})
        query = event.get("queryStringParameters") or {}
        return _zip(_store, int(zip_path.group(1)), query.get("key", ""))
    if method != "POST" or path not in ("/", "/turn"):
        return _answer(404, {"detail": "not found"})
    raw = event.get("body") or ""
    data = base64.b64decode(raw) if event.get("isBase64Encoded") else raw.encode()
    if len(data) > MAX_BODY_BYTES:
        return _answer(413, {"detail": "request body is too large"})
    try:
        delivery = TurnDelivery.model_validate_json(data)
    except ValidationError as error:
        return _answer(422, {"detail": f"the body is not a TurnDelivery: {error}"})
    refusal = submit_refusal(str(delivery.submit.url))
    if refusal is not None:
        return _answer(400, {"detail": refusal})
    _bot.take(delivery, _store)
    return _answer(200, {"accepted": True})
