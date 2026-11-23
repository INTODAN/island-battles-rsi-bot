#!/usr/bin/env bash
# The league's checks: format, lint, types and tests of the tools (Python) and
# of every bot (Go). A bot that fails them doesn't play.
set -euo pipefail
cd "$(dirname "$0")/.."
uv run --locked ruff format --check
uv run --locked ruff check
uv run --locked ty check
uv run --locked pytest -q
unformatted=$(gofmt -l bots tests)
if [[ -n "$unformatted" ]]; then
  echo "gofmt would change these files (run gofmt -w on them):" >&2
  echo "$unformatted" >&2
  exit 1
fi
go mod verify >/dev/null
go vet ./...
# Only the league's tests: a test file in a bot's directory is refused, never run.
go test ./tests/...
