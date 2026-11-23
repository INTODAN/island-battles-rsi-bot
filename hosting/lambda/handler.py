"""An AWS Lambda function URL that plays a league bot as an Island Battles hosted bot.

The game POSTs a ``TurnDelivery`` to the bot's URL and waits up to 5 seconds for
any 2xx; the bot submits its answer itself, with the delivery's submit token,
to the game's ``POST /generation/commands``. That is the protocol of
``island-battles-bot serve``, and this handler plays and submits a turn with the
Python SDK's own code for it (``BotServer.play`` and ``BotServer.submit``): the
same time budget, the same pass when the bot fails or is slow, and the same
retries.

The bot is a league bot, a Go program: the handler plays each turn through the
program's ``worker`` subcommand, the Go SDK's JSON Lines protocol that the
headless runner plays it with, in one process that the Lambda instance keeps
between turns. ``build.sh`` builds the program for Lambda (``bin/<bot>``); run
from the repository, as the tests do, the handler builds it with the league's
tools.

Unlike ``serve``, it submits before it answers rather than after, since Lambda
freezes the instance once the handler returns. ``GET /health`` answers like
``serve``'s, with the bot's name. ``BOT`` names the bot; by default it is the
one that the file ``bot`` names, which ``build.sh`` packages next to this one.

With ``GAMES_BUCKET`` set, it also keeps every turn it plays in that bucket.
When a game ends, the game POSTs its end to ``/game-ended``, the bot's URL with
its last segment replaced: the bot downloads the game's demo from the link in
it and packs the game into a zip (``games.py``). ``GET /`` is the bot's home
page, which lists the games; ``GET /games/<id>.zip`` downloads one.

The home page, ``/api/games`` and the zips are the owner's alone (``owner.py``):
they need the session that signing in with the owner's Google account gives
(``POST /sign-in``), or, for a zip, ``?key=`` the value of ``GAMES_KEY``. A turn,
a game's end and ``/health`` need nothing, since the game and the deploy call them.
"""

from __future__ import annotations

import base64
import hmac
import json
import logging
import os
import re
import subprocess
import threading
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import games
import httpx
import owner
import page
from island_battles_client._generated import BotTurn, BotTurnResult, TurnDelivery
from island_battles_client.cli import MAX_BODY_BYTES, BotServer, submit_refusal
from island_battles_client.game_log import ClientLogging
from pydantic import ValidationError

# The bot's name under bots/. A deploy before the bots were Go set BOT to "bots.<name>.bot:play", which names it too.
BOT = (
    (os.environ.get("BOT") or Path(__file__).with_name("bot").read_text())
    .strip()
    .split(":")[0]
    .removeprefix("bots.")
    .removesuffix(".bot")
)
# The longest a turn may play; the turn's deadline cuts it shorter, as in serve.
TURN_TIMEOUT_SECONDS = float(os.environ.get("TURN_TIMEOUT_SECONDS", "8"))
# The bucket that keeps the real games; without it nothing is kept.
GAMES_BUCKET = os.environ.get("GAMES_BUCKET", "")
# A key that downloads a game's zip without signing in, for scripts; without it only the owner may.
GAMES_KEY = os.environ.get("GAMES_KEY", "")
# Who may open the home page: the Google client ID its button signs in with, the owner's
# address (or several, comma-separated) and the secret that signs their session.
OWNER = owner.Owner.from_settings(
    os.environ.get("GOOGLE_CLIENT_ID", ""), os.environ.get("OWNER_EMAIL", ""), os.environ.get("SESSION_SECRET", "")
)
# The map files that name a game's map: packaged next to this file, or the repository's.
_HERE = Path(__file__).parent
# The iterations' studies of real games: bundled by build.sh, or the ledger's when run from the repository.
STUDIES = page.load_studies(
    *[path for path in (_HERE / "studies", _HERE.parent.parent / "ledger" / "studies") if path.is_dir()]
)
MAPS = games.KnownMaps.load(*[path for path in (_HERE / "maps", _HERE.parent.parent / "maps") if path.is_dir()])
_ZIP_PATH = re.compile(r"^/games/(\d+)\.zip$")
# The largest demo the bot downloads, and how long it waits for it.
MAX_DEMO_BYTES = 64 * 1024 * 1024
DEMO_TIMEOUT_SECONDS = 10.0
_log = logging.getLogger("island_battles.hosting")


def bot_binary(name: str) -> Path:
    """The bot's program: packaged by build.sh, or built from the repository's code."""
    packaged = _HERE / "bin" / name
    if packaged.is_file():
        return packaged
    from league_tools import gobots  # noqa: PLC0415 - only in the repository, not in the package

    return gobots.build([name])[name]


class WorkerPlay:
    """A Go bot's play function: each call is one turn through the bot's worker process.

    The process is started on the first turn and kept for the next; one that
    stopped is started again. A turn that the worker answers with an error, a
    failed or invalid turn, raises, so the turn passes as serve passes it.
    """

    def __init__(self, binary: Path) -> None:
        """Remember the program; the process starts with the first turn."""
        self.binary = binary
        self._process: subprocess.Popen[str] | None = None
        # One turn at a time: a turn that ran out of time still owns the process until it answers.
        self._lock = threading.Lock()

    def _worker(self) -> subprocess.Popen[str]:
        if self._process is not None and self._process.poll() is None:
            return self._process
        process = subprocess.Popen(
            [str(self.binary), "worker"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        assert process.stdout is not None
        if json.loads(process.stdout.readline() or "{}") != {"ready": True}:
            process.kill()
            raise RuntimeError(f"{self.binary.name}'s worker didn't start")
        self._process = process
        return process

    def __call__(self, turn: BotTurn) -> dict[str, Any]:
        """Play one turn, and return the result as the worker wrote it."""
        if not self._lock.acquire(blocking=False):
            # A turn that ran out of time still waits for this worker: end it, so that this turn and the next
            # ones get a new worker instead of each waiting behind it until it too runs out of time.
            stuck = self._process
            if stuck is not None:
                stuck.kill()
            self._lock.acquire()
        try:
            process = self._worker()
            assert process.stdin is not None and process.stdout is not None
            process.stdin.write(json.dumps({"turn": turn.model_dump(mode="json", by_alias=True)}) + "\n")
            process.stdin.flush()
            line = process.stdout.readline()
            if not line:
                self._process = None
                raise RuntimeError(f"{self.binary.name}'s worker stopped")
            answer = json.loads(line)
        finally:
            self._lock.release()
        if "error" in answer:
            raise RuntimeError(answer["error"])
        return answer["result"]


class _Bot:
    """The bot, in the shape of ``serve``'s ``ReloadingPlay``."""

    def __init__(self, name: str) -> None:
        """Find the bot's program; its worker starts with the first turn."""
        self.name = name
        self._play = WorkerPlay(bot_binary(name))

    def get(self) -> WorkerPlay:
        """The bot's play function."""
        return self._play


class LambdaBot:
    """What ``BotServer.play`` and ``BotServer.submit`` read, without a socket."""

    play = BotServer.play
    submit = BotServer.submit

    def __init__(self, name: str, turn_timeout: float) -> None:
        """Find the bot and attach the logging that ``run_turn`` reads."""
        self.bot = _Bot(name)
        self.turn_timeout = turn_timeout
        self.client_logging = ClientLogging(self, logging.INFO, True, None)
        self.client_logging.attach()
        # The batch that _post sent last, the server's status for it and its reason.
        self.sent: tuple[BotTurnResult, int | None, str] | None = None

    @property
    def name(self) -> str:
        """The bot's name: its directory under bots/."""
        return self.bot.name

    def _post(self, delivery: TurnDelivery, result: BotTurnResult) -> tuple[int | None, str, str | None]:
        """POST one batch as serve does, remembering what was sent and the answer."""
        answer = BotServer._post(self, delivery, result)  # ty: ignore[invalid-argument-type]
        status, detail, _ = answer
        self.sent = (result, status, "" if status is not None and 200 <= status < 300 else detail)
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
        submitted, status, detail = self.sent or (result, None, "")
        turn = delivery.turn

        def keep() -> None:
            now = datetime.now(UTC)
            summary = games.record_turn(
                store,
                bot=self.name,
                turn=turn.model_dump(mode="json", by_alias=True),
                result=submitted.model_dump(mode="json", by_alias=True),
                submitted=status,
                detail=detail,
                play_ms=play_ms,
                maps=MAPS,
                now=now,
            )
            if store.get(games.end_key(turn.game_id)) is not None:
                # The game's end came before this turn was kept: pack it again with this turn.
                games.complete(store, turn.game_id, download_demo, MAPS, self.name, now)
            elif turn.turn_number == 1 and summary["turns"] == 1:
                # A new game: a good moment to pack the games that are over, without downloads.
                games.finish_over_games(store, now)

        games.safely(keep, _log.error)

    def end(self, end: dict[str, Any], store: games.Store) -> dict[str, Any] | None:
        """Keep a game's end, download its demo and pack the game."""
        games.record_end(store, end)
        return games.complete(store, end["game_id"], download_demo, MAPS, self.name, datetime.now(UTC))


def download_demo(url: str) -> bytes:
    """Download a game's demo from its link, which must be on the game's host."""
    refusal = submit_refusal(url)
    if refusal is not None:
        raise ValueError(refusal.replace("submit.url", "the demo link"))
    with httpx.Client(timeout=DEMO_TIMEOUT_SECONDS, follow_redirects=False) as client:
        with client.stream("GET", url) as response:
            response.raise_for_status()
            body = bytearray()
            for chunk in response.iter_bytes():
                body += chunk
                if len(body) > MAX_DEMO_BYTES:
                    raise ValueError(f"the demo is larger than {MAX_DEMO_BYTES} bytes")
    return bytes(body)


_bot = LambdaBot(BOT, TURN_TIMEOUT_SECONDS)
_store: games.Store | None = games.S3Store(GAMES_BUCKET) if GAMES_BUCKET else None


def _answer(status: int, body: object) -> dict[str, Any]:
    """A function URL response with a JSON body."""
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json", "Cache-Control": "no-store"},
        "body": json.dumps(body),
    }


def tokeninfo(credential: str) -> object:
    """Google's claims of an ID token, once Google says it is genuine.

    Google answers 400 to a token that isn't; any other failure (an outage, a limit) raises
    ``httpx.HTTPError``, which isn't the credential's fault.
    """
    with httpx.Client(timeout=5.0) as client:
        response = client.get(owner.TOKENINFO_URL, params={"id_token": credential})
    if response.status_code == 400:
        raise owner.Refused("Google didn't accept the credential")
    response.raise_for_status()
    return response.json()


def _is_owner(event: dict[str, Any]) -> bool:
    return OWNER.signed_in(owner.cookie_value(event), time.time())


def _sign_in(event: dict[str, Any]) -> dict[str, Any]:
    """Sign the owner in with the ID token that Google's button gave the page."""
    try:
        data = _body(event)
        credential = json.loads(data).get("credential", "") if len(data) <= 8192 else ""
    except ValueError, AttributeError, RecursionError:
        credential = ""
    nonce = owner.cookie_value(event, owner.NONCE_COOKIE) or ""
    try:
        session = OWNER.sign_in(str(credential), nonce, tokeninfo, time.time())
    except owner.Refused as refusal:
        return _answer(403, {"detail": str(refusal)})
    except httpx.HTTPError, ValueError:
        return _answer(502, {"detail": "Google couldn't be asked about the credential; try again"})
    answer = _answer(200, {"signed_in": True})
    answer["cookies"] = [
        owner.set_cookie(session, owner.SESSION_SECONDS),
        owner.set_cookie("", 0, owner.NONCE_COOKIE),
        owner.set_cookie("", 0, owner.SIGNED_OUT_COOKIE),
    ]
    return answer


def _sign_out() -> dict[str, Any]:
    """End the session in this browser, and keep it from signing in silently until the button is used."""
    answer = _answer(200, {"signed_in": False})
    answer["cookies"] = [
        owner.set_cookie("", 0),
        owner.set_cookie("1", owner.SIGNED_OUT_SECONDS, owner.SIGNED_OUT_COOKIE),
    ]
    return answer


def _closed(event: dict[str, Any]) -> dict[str, Any]:
    """The sign-in page, for whoever isn't the signed-in owner, with the nonce its sign-in must carry.

    A browser keeps its nonce while it has one, so two of its tabs on the page ask for the same.
    """
    client_id = OWNER.client_id if OWNER.ready else ""
    nonce = owner.cookie_value(event, owner.NONCE_COOKIE)
    if not owner.valid_nonce(nonce):
        nonce = owner.new_nonce()
    signed_out = owner.cookie_value(event, owner.SIGNED_OUT_COOKIE) == "1"
    return {
        "statusCode": 401,
        "headers": {"Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store"},
        "cookies": [owner.set_cookie(str(nonce), owner.NONCE_SECONDS, owner.NONCE_COOKIE)] if client_id else [],
        "body": page.render_sign_in(client_id, str(nonce), signed_out=signed_out),
    }


def _games(store: games.Store) -> list[dict[str, Any]]:
    """Every game, newest first, after packing the ones that are over."""
    return games.finish_over_games(store, datetime.now(UTC), download_demo, MAPS)


def _home(store: games.Store | None) -> dict[str, Any]:
    """The home page."""
    listed = _games(store) if store else []
    summary = games.overview(listed, datetime.now(UTC))
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store"},
        "body": page.render(_bot.name, summary, listed, STUDIES),
    }


def _zip(store: games.Store, game_id: int, allowed: bool) -> dict[str, Any]:
    """Redirect to a short-lived download of a finished game's zip."""
    if not allowed:
        return _answer(403, {"detail": "a game's zip is the owner's: sign in on the home page, or ?key=..."})
    if store.get(games.game_key(game_id)) is None:
        return _answer(404, {"detail": f"no game {game_id}"})
    games.finish_over_games(store, datetime.now(UTC), download_demo, MAPS)
    summary = json.loads(store.get(games.game_key(game_id)) or b"{}")
    if not summary.get("zip"):
        return _answer(409, {"detail": f"game {game_id} is still being played"})
    url = store.download_url(summary["zip"], f"island-battles-game-{game_id}.zip")
    return {"statusCode": 302, "headers": {"Location": url, "Cache-Control": "no-store"}, "body": ""}


def _body(event: dict[str, Any]) -> bytes:
    raw = event.get("body") or ""
    return base64.b64decode(raw) if event.get("isBase64Encoded") else raw.encode()


def _game_ended(event: dict[str, Any]) -> dict[str, Any]:
    """Keep the end of a game, with its demo. The game doesn't wait for the answer."""
    data = _body(event)
    if len(data) > MAX_BODY_BYTES:
        return _answer(413, {"detail": "request body is too large"})
    try:
        end = json.loads(data)
        game_id, color = end["game_id"], end["team_color"]
        if not isinstance(game_id, int) or not isinstance(color, int) or game_id < 1:
            raise ValueError("game_id and team_color must be whole numbers")
        if not isinstance(end["outcome"]["reason"], str) or not isinstance(end["generation"]["castles"], list):
            raise ValueError("it has no outcome or no final generation")
    except (ValueError, KeyError, TypeError) as error:
        return _answer(422, {"detail": f"the body is not a GameEndedDelivery: {error}"})
    store = _store
    if store is None:
        return _answer(202, {"accepted": True, "kept": False})
    summary = games.safely(lambda: _bot.end(end, store), _log.error)
    _log.info("game %s ended: %s", game_id, summary and summary.get("result_note"))
    return _answer(202, {"accepted": True, "kept": summary is not None})


def handler(event: dict[str, Any], context: object) -> dict[str, Any]:
    """Answer one function URL request: a turn, a game's end, the home page, the games or the health check."""
    http = event.get("requestContext", {}).get("http", {})
    method = http.get("method", "")
    path = event.get("rawPath", "/")
    if method == "GET" and path == "/health":
        return _answer(200, {"name": _bot.name, "ok": True, "games": _store is not None})
    if method == "POST" and path == "/sign-in":
        return _sign_in(event)
    if method == "POST" and path == "/sign-out":
        return _sign_out()
    if method == "GET" and path == "/":
        return _home(_store) if _is_owner(event) else _closed(event)
    if method == "GET" and path == "/api/games":
        if not _is_owner(event):
            return _answer(401, {"detail": "the games are the owner's: sign in on the home page"})
        listed = _games(_store) if _store else []
        return _answer(200, {"overview": games.overview(listed, datetime.now(UTC)), "games": listed})
    zip_path = _ZIP_PATH.match(path)
    if method == "GET" and zip_path:
        if _store is None:
            return _answer(404, {"detail": "this bot keeps no games"})
        key = (event.get("queryStringParameters") or {}).get("key", "")
        by_key = bool(GAMES_KEY) and hmac.compare_digest(key.encode(), GAMES_KEY.encode())
        return _zip(_store, int(zip_path.group(1)), by_key or _is_owner(event))
    if method == "POST" and path == "/game-ended":
        return _game_ended(event)
    if method != "POST" or path not in ("/", "/turn"):
        return _answer(404, {"detail": "not found"})
    data = _body(event)
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
