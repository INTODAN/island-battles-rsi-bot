"""Starts the real-game study when the hosted bot has packed a real game.

An AWS Lambda function, called by the games bucket's event notification for
every object created under ``games/`` that ends in ``.zip``. For each zip it
reads the game's summary packed inside it (``game.json``: the copy next to the
zip is written after it, so it can still be the old one) and, when the game is
finished and its demo is final, sends a ``repository_dispatch`` of
type ``real-game`` to the league's repository. The workflow
``real-game-study.yml`` answers it.

A game whose demo is still ``pending`` (the game's own demo didn't download
yet) is skipped: the hosted bot packs its zip again once the demo is in, and
that zip calls this again. A zip packed twice sends two dispatches; the
workflow studies each game once, whatever starts it.

Environment:

- ``GITHUB_REPOSITORY``: ``owner/name`` of the league.
- ``GITHUB_TOKEN_PARAMETER``: the SSM parameter (a SecureString) that holds a
  fine-grained token of that repository alone, with Contents read and write:
  what ``repository_dispatch`` needs, and nothing more.
"""

from __future__ import annotations

import io
import json
import logging
import os
import re
import urllib.parse
import urllib.request
import zipfile
from collections.abc import Callable
from typing import Any

EVENT_TYPE = "real-game"
ZIP_KEY = re.compile(r"^games/(\d+)/game-(\d+)\.zip$")

_log = logging.getLogger()
_log.setLevel(logging.INFO)


def zipped_games(event: dict[str, Any]) -> list[tuple[str, int]]:
    """The (bucket, game id) of every game zip that an S3 event notification names."""
    found = []
    for record in event.get("Records", []):
        s3 = record.get("s3", {})
        bucket = s3.get("bucket", {}).get("name")
        key = urllib.parse.unquote_plus(s3.get("object", {}).get("key") or "")
        match = ZIP_KEY.match(key)
        if bucket and match and match.group(1) == match.group(2):
            found.append((bucket, int(match.group(1))))
    return found


def is_final(summary: dict[str, Any] | None) -> bool:
    """Whether a game's summary says its zip is the one to study: finished, with no demo still to come."""
    return bool(summary) and summary.get("status") == "finished" and summary.get("demo") != "pending"


def packed_summary(data: bytes) -> dict[str, Any] | None:
    """The summary that a game's zip holds, or None when it holds none."""
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        if "game.json" not in archive.namelist():
            return None
        return json.loads(archive.read("game.json"))


def dispatch_body(game_ids: list[int]) -> dict[str, Any]:
    """The repository_dispatch request's body."""
    return {"event_type": EVENT_TYPE, "client_payload": {"game_ids": sorted(set(game_ids))}}


def send_dispatch(repository: str, token: str, game_ids: list[int]) -> int:
    """POST the dispatch to GitHub; returns the HTTP status (204 when GitHub took it)."""
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repository}/dispatches",
        data=json.dumps(dispatch_body(game_ids)).encode(),
        method="POST",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "island-battles-league-notifier",
        },
    )
    with urllib.request.urlopen(request, timeout=10) as response:  # noqa: S310 - a fixed https URL
        return response.status


def notify(
    event: dict[str, Any],
    read_summary: Callable[[str, int], dict[str, Any] | None],
    send: Callable[[list[int]], int],
) -> list[int]:
    """Send one dispatch for the final games that the event names; returns their ids."""
    ready = [game_id for bucket, game_id in zipped_games(event) if is_final(read_summary(bucket, game_id))]
    if ready:
        status = send(ready)
        _log.info("dispatched games %s: HTTP %s", ready, status)
    return ready


def handler(event: dict[str, Any], context: object) -> dict[str, Any]:
    """The Lambda entry point."""
    import boto3  # the Lambda runtime has it; imported here so tests need no AWS

    s3 = boto3.client("s3")
    ssm = boto3.client("ssm")

    def read_summary(bucket: str, game_id: int) -> dict[str, Any] | None:
        try:
            data = s3.get_object(Bucket=bucket, Key=f"games/{game_id}/game-{game_id}.zip")["Body"].read()
        except s3.exceptions.NoSuchKey:
            return None
        return packed_summary(data)

    def send(game_ids: list[int]) -> int:
        token = ssm.get_parameter(Name=os.environ["GITHUB_TOKEN_PARAMETER"], WithDecryption=True)
        return send_dispatch(os.environ["GITHUB_REPOSITORY"], token["Parameter"]["Value"], game_ids)

    return {"dispatched": notify(event, read_summary, send)}
