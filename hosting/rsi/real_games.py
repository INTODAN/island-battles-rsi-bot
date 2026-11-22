"""Download the hosted bot's real games that no iteration has studied yet.

    uv run python hosting/rsi/real_games.py --bucket BUCKET --out runs/real [--limit 10]

Reads every ``games/<id>/game.json`` in the games bucket, keeps the games that
are finished with a final demo and whose id ``ledger/real-games.txt`` doesn't
list, and unpacks the newest ``--limit`` of them into ``OUT/<id>/`` (the
files of the hosted bot's zip: ``demo.json``, ``digest.txt``, ``turns.jsonl``,
``game.json``...). Prints their ids, one per line, oldest first.

The zips carry players' names and their bots' logs: ``runs/`` is not in git,
and nothing from here is committed.
"""

from __future__ import annotations

import argparse
import io
import json
import zipfile
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
STUDIED = ROOT / "ledger" / "real-games.txt"
# The files of a hosted bot's zip; anything else in a zip is left out.
ZIP_FILES = ("demo.json", "digest.txt", "turns.jsonl", "game.json", "game-ended.json", "README.txt")


def studied(path: Path = STUDIED) -> set[int]:
    """The ids of the real games that an iteration has studied."""
    if not path.exists():
        return set()
    return {int(line.split()[0]) for line in path.read_text().splitlines() if line.strip() and line[0].isdigit()}


def is_final(summary: dict[str, Any]) -> bool:
    """A finished game whose demo won't change: the one to study."""
    return summary.get("status") == "finished" and summary.get("demo") != "pending"


def to_study(summaries: Iterable[dict[str, Any]], done: set[int], limit: int) -> list[int]:
    """The newest ``limit`` final games not in ``done``, oldest first."""
    ready = sorted(s["game_id"] for s in summaries if is_final(s) and s["game_id"] not in done)
    return ready[-limit:] if limit > 0 else ready


def unpack(data: bytes, directory: Path) -> None:
    """Write a game zip's known files into directory, by their names alone."""
    directory.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for name in archive.namelist():
            if name in ZIP_FILES:
                (directory / name).write_bytes(archive.read(name))


def main(argv: list[str] | None = None) -> None:
    """Download and unpack the games to study, and print their ids."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--bucket", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=10, help="the most games to study in one iteration (0: all)")
    args = parser.parse_args(argv)

    import boto3

    s3 = boto3.client("s3")
    pages = s3.get_paginator("list_objects_v2").paginate(Bucket=args.bucket, Prefix="games/", Delimiter="/")
    prefixes = [entry["Prefix"] for page in pages for entry in page.get("CommonPrefixes", [])]

    def summary(prefix: str) -> dict[str, Any] | None:
        try:
            return json.loads(s3.get_object(Bucket=args.bucket, Key=f"{prefix}game.json")["Body"].read())
        except s3.exceptions.NoSuchKey:
            return None

    with ThreadPoolExecutor(16) as pool:
        summaries = [s for s in pool.map(summary, prefixes) if s and isinstance(s.get("game_id"), int)]
    chosen = to_study(summaries, studied(), args.limit)
    for game_id in chosen:
        data = s3.get_object(Bucket=args.bucket, Key=f"games/{game_id}/game-{game_id}.zip")["Body"].read()
        unpack(data, args.out / str(game_id))
        print(game_id)


if __name__ == "__main__":
    main()
