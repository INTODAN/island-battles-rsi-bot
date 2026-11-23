#!/usr/bin/env bash
# Builds dist/lambda/bot.zip: the Lambda handler and the Python SDK with its
# dependencies for Lambda's python3.14 runtime on arm64, and one league bot,
# a Go program built for linux/arm64 (bin/<bot>), which the handler plays
# through its worker.
#
#   hosting/lambda/build.sh [bot]     # the bot's directory under bots/, hosting/lambda/bot by default
set -euo pipefail
cd "$(dirname "$0")/../.."
bot="${1:-$(tr -d '[:space:]' < hosting/lambda/bot)}"
[[ -f "bots/$bot/main.go" ]] || { echo "no bot bots/$bot/main.go" >&2; exit 1; }

out=dist/lambda
rm -rf "$out"
mkdir -p "$out/package/bin"
uv export --frozen --no-dev --no-emit-project --no-hashes --quiet -o "$out/requirements.txt"
uv pip install --quiet --target "$out/package" \
  --python-platform aarch64-manylinux2014 --python-version 3.14 --only-binary :all: \
  -r "$out/requirements.txt"
# A static binary for Lambda's arm64, without the build's paths.
CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build -trimpath -buildvcs=false -ldflags="-s -w" -o "$out/package/bin/$bot" "./bots/$bot"
cp hosting/lambda/handler.py hosting/lambda/games.py hosting/lambda/owner.py hosting/lambda/page.py hosting/lambda/bot "$out/package/"
# The league's digest, which games.py puts in each game's zip.
cp league_tools/digest.py "$out/package/digest.py"
# The iterations' studies of real games, which the home page shows under each game.
mkdir -p "$out/package/studies"
studies=(); [[ -d ledger/studies ]] && studies=(ledger/studies/[0-9]*.md)
[[ -e "${studies[0]:-}" ]] && cp "${studies[@]}" "$out/package/studies/"
# The league's maps, which name the map of a real game.
mkdir -p "$out/package/maps"
cp maps/*/*.json "$out/package/maps/"
(cd "$out/package" && find . -name __pycache__ -prune -exec rm -rf {} + && zip -qr9 ../bot.zip .)
echo "$out/bot.zip ($(du -h "$out/bot.zip" | cut -f1)), bot $bot: set BOT=$bot"
