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
"""

from __future__ import annotations

import base64
import json
import logging
import os
from pathlib import Path
from typing import Any

from island_battles_client._generated import BotTurnResult, TurnDelivery
from island_battles_client.cli import MAX_BODY_BYTES, BotServer, load_play, submit_refusal
from island_battles_client.game_log import ClientLogging
from pydantic import ValidationError

BOT = os.environ.get("BOT") or f"bots.{Path(__file__).with_name('bot').read_text().strip()}.bot:play"
# The longest a turn may play; the turn's deadline cuts it shorter, as in serve.
TURN_TIMEOUT_SECONDS = float(os.environ.get("TURN_TIMEOUT_SECONDS", "8"))


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
    _post = BotServer._post

    def __init__(self, spec: str, turn_timeout: float) -> None:
        """Load the bot and attach the logging that ``run_turn`` reads."""
        self.bot = _Bot(spec)
        self.turn_timeout = turn_timeout
        self.client_logging = ClientLogging(self, logging.INFO, True, None)
        self.client_logging.attach()

    def take(self, delivery: TurnDelivery) -> None:
        """Play the delivered turn and submit the answer, or a pass."""
        result: BotTurnResult = self.play(delivery)
        self.submit(delivery, result)


_bot = LambdaBot(BOT, TURN_TIMEOUT_SECONDS)


def _answer(status: int, body: object) -> dict[str, Any]:
    """A function URL response with a JSON body."""
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def handler(event: dict[str, Any], context: object) -> dict[str, Any]:
    """Answer one function URL request: ``POST /turn`` or ``GET /health``."""
    http = event.get("requestContext", {}).get("http", {})
    method = http.get("method", "")
    path = event.get("rawPath", "/")
    if method == "GET" and path in ("/", "/health"):
        return _answer(200, {"name": _bot.bot.spec, "ok": True})
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
    _bot.take(delivery)
    return _answer(200, {"accepted": True})
