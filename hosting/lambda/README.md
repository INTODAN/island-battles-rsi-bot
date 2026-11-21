# A league bot as a hosted bot on AWS Lambda

A [hosted bot](https://github.com/INTODAN/island-battles-go/blob/main/backend/README.md#hosted-and-uploaded-bots) is a public HTTPS URL. The game POSTs each turn's `TurnDelivery` to it and waits up to 5 seconds for a 2xx. The bot submits its answer itself, with the delivery's token. [`handler.py`](handler.py) does that on a Lambda function URL, using the SDK's own `serve` code to play and submit. It submits before it answers, because Lambda freezes once the handler returns.

## What is deployed

In `eu-central-1`, next to the game:

| Resource | Name |
| --- | --- |
| Function | `island-battles-league-bot`: `python3.14`, arm64, 512 MB, 15 s timeout, reserved concurrency 5, env `BOT=bots.<bot>.bot:play` for the bot that [`bot`](bot) names |
| Function URL | auth `NONE`; the bot's URL is the function URL followed by `/turn` |
| Role | `island-battles-league-bot`: writes its own logs, nothing else |
| Code | `s3://island-battles-league-bot-<account>/bot.zip` |
| Logs | `/aws/lambda/island-battles-league-bot`, 14 days |

A cold start takes about 0.9 s and a warm turn about 60 ms. A game is a few hundred requests, well inside Lambda's free tier, which the account shares with the game's own functions.

## Deploying

[`bot`](bot) names the bot that is deployed: the ledger's champion, which an iteration that crowns a new one changes. Only a bot that a tournament measured is deployed.

**On main, by itself.** [`deploy-bot.yml`](../../.github/workflows/deploy-bot.yml) runs on every push to main that changes `bots/`, `hosting/lambda/` or `uv.lock`, and from the Actions tab. It runs `scripts/check.sh`, builds the zip, uploads it, updates the function's code and its `BOT`, and checks that `GET <url>/health` names the bot. It signs in with GitHub's OIDC as the role `island-battles-league-bot-deploy`, which only main of this repository may assume, and which may only upload `bot.zip` and update this one function. The repository variables `AWS_DEPLOY_ROLE_ARN`, `BOT_BUCKET` and `BOT_FUNCTION` say where.

**By hand,** the same steps:

1. `hosting/lambda/build.sh [bot]` builds `dist/lambda/bot.zip` with `bots/<bot>/` (the one `bot` names by default).
2. Upload it to `s3://island-battles-league-bot-<account>/bot.zip`, then call `UpdateFunctionCode` with that S3 object.
3. When the bot changed, set `BOT=bots.<bot>.bot:play` with `UpdateFunctionConfiguration`.
4. Check the deployment: `GET <url>/health` should name the bot.
