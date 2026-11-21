#!/usr/bin/env bash
# Builds dist/lambda/bot.zip: the Lambda handler, one league bot and the SDK
# with its dependencies for Lambda's python3.14 runtime on arm64.
#
#   hosting/lambda/build.sh [bot]     # the bot's directory under bots/, hosting/lambda/bot by default
set -euo pipefail
cd "$(dirname "$0")/../.."
bot="${1:-$(tr -d '[:space:]' < hosting/lambda/bot)}"
[[ -f "bots/$bot/bot.py" ]] || { echo "no bot bots/$bot/bot.py" >&2; exit 1; }

out=dist/lambda
rm -rf "$out"
mkdir -p "$out/package/bots/$bot"
uv export --frozen --no-dev --no-emit-project --no-hashes --quiet -o "$out/requirements.txt"
uv pip install --quiet --target "$out/package" \
  --python-platform aarch64-manylinux2014 --python-version 3.14 --only-binary :all: \
  -r "$out/requirements.txt"
cp bots/__init__.py "$out/package/bots/"
cp "bots/$bot/"*.py "$out/package/bots/$bot/"
cp hosting/lambda/handler.py hosting/lambda/games.py hosting/lambda/page.py hosting/lambda/bot "$out/package/"
# The league's maps, which name the map of a real game.
mkdir -p "$out/package/maps"
cp maps/*/*.json "$out/package/maps/"
(cd "$out/package" && find . -name __pycache__ -prune -exec rm -rf {} + && zip -qr9 ../bot.zip .)
echo "$out/bot.zip ($(du -h "$out/bot.zip" | cut -f1)), bot $bot: set BOT=bots.$bot.bot:play"
