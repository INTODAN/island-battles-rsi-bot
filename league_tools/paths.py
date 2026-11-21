"""Where the league keeps its files."""

from pathlib import Path

LEAGUE = Path(__file__).resolve().parents[1]
BOTS = LEAGUE / "bots"
MAPS = LEAGUE / "maps"
RUNS = LEAGUE / "runs"
CACHE = RUNS / "cache"
LEDGER = LEAGUE / "ledger"
# Which commit of the game the headless runner is built from.
RUNNER_PIN = LEAGUE / "runner.toml"
# The game's source at that commit, fetched on the first build, and the runner built from it.
RUNNER_SOURCE = LEAGUE / ".runner" / "source"
ENGINE = LEAGUE / ".runner" / "headless-match"
