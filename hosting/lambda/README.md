# A league bot as a hosted bot on AWS Lambda

A [hosted bot](https://github.com/INTODAN/island-battles-go/blob/main/backend/README.md#hosted-and-uploaded-bots) is a public HTTPS URL. The game POSTs each turn's `TurnDelivery` to it and waits up to 5 seconds for a 2xx. The bot submits its answer itself, with the delivery's token. [`handler.py`](handler.py) does that on a Lambda function URL, using the SDK's own `serve` code to play and submit. It submits before it answers, because Lambda freezes once the handler returns.

## What is deployed

In `eu-central-1`, next to the game:

| Resource | Name |
| --- | --- |
| Function | `island-battles-league-bot`: `python3.14`, arm64, 512 MB, 15 s timeout, reserved concurrency 5, env `BOT=bots.<bot>.bot:play` for the bot that [`bot`](bot) names, `GAMES_BUCKET` and `GAMES_KEY` (see [Its games](#its-games)) |
| Function URL | auth `NONE`; the bot's URL is the function URL followed by `/turn` |
| Role | `island-battles-league-bot`: writes its own logs, and reads and writes `games/` in the games bucket |
| Games | `s3://island-battles-league-games-<account>/games/`, private |
| Code | `s3://island-battles-league-bot-<account>/bot.zip` |
| Logs | `/aws/lambda/island-battles-league-bot`, 14 days |

A cold start takes about 0.9 s and a warm turn about 60 ms. A game is a few hundred requests, well inside Lambda's free tier, which the account shares with the game's own functions.

## Its games

With `GAMES_BUCKET` set, the bot keeps every real game it plays ([`games.py`](games.py)), and its function URL serves a home page:

| Path | What it is |
| --- | --- |
| `GET /` | The home page ([`page.py`](page.py)): whether it is playing, its record, the turns it played, and every game with its result, opponent, map, team, turns and a **Zip** button. |
| `POST /game-ended` | Where the game sends the end of each game. |
| `GET /api/games` | The same as JSON. |
| `GET /games/<id>.zip?key=…` | Redirects to a 5-minute download of a finished game's zip. `key` is `GAMES_KEY`; the page asks for it once and remembers it in the browser. Without `GAMES_KEY`, anyone may download. |
| `GET /health` | The bot, and whether it keeps games. |

**How a game is kept.** After submitting each turn, the bot writes it (the board, its answer, its logs, the server's status and, when the server refused the answer, why, and the time it took) to `games/<id>/turns/`, and updates `games/<id>/game.json`. When the game ends, however it ends, the game POSTs a `GameEndedDelivery` to the bot's URL with its last segment replaced by `game-ended`: `<function URL>/game-ended` (INTODAN/island-battles-go#413, the backend README's [The end of a game](https://github.com/INTODAN/island-battles-go/blob/main/backend/README.md#the-end-of-a-game)). It holds the outcome, the final generation, the bot's last memory and a link that downloads the game's demo, with every team's logs. The bot keeps it as `games/<id>/game-ended.json`, downloads the demo (only from the game's own host), and packs `games/<id>/game-<id>.zip`:

| File | What it is |
| --- | --- |
| `demo.json` | The game's own demo. `league digest` and `league unpack` take the zip itself; the demo viewer opens `demo.json`. |
| `digest.txt` | `league digest` of the demo: the timeline, each team's logistics and the events. |
| `turns.jsonl` | One line per turn the bot played: its commands and memory, its time to play, and the server's status and reason for its answer. The demo doesn't have these. |
| `game.json` | The summary the home page shows: the result, the opponents as the demo names them, the map. |
| `game-ended.json` | The end as delivered, without the demo link. |
| `README.txt` | What each file is. |

**When something is missing:**
- **The download fails.** The zip is packed from the bot's own turns, with the delivered outcome, and the game is marked `pending`. The bot tries again whenever the page, the API or a zip is read, and when a new game starts, until the link expires (7 days).
- **No end arrives** (a runner that failed, or a game played before the game sent ends). The game is packed once no turn came for a minute past the last one's deadline (half an hour when turns have none). Its demo is rebuilt from the bot's turns, so it stops at the bot's last turn and has no other team's logs. Its result is **estimated** from the last board the bot saw, and the page marks it ≈.

The map is named when its castles stand where a map of `maps/` has them, and is otherwise described ("8 castles, 2 teams").

A real game's zip is not committed (AGENTS.md): it carries players' names and their bots' logs. What it shows goes in the ledger, in words. Keeping a turn costs about three S3 requests, made after the turn is submitted, so they never make a turn late.

### Setting it up

Once, by hand:

1. Create the private bucket `island-battles-league-games-<account>` in `eu-central-1` (all public access blocked).
2. Add an inline policy `games` to the role `island-battles-league-bot`: `s3:GetObject` and `s3:PutObject` on `arn:aws:s3:::island-battles-league-games-<account>/games/*`, and `s3:ListBucket` on the bucket with the condition `s3:prefix` like `games/*`.
3. Set `GAMES_BUCKET` and `GAMES_KEY` (a long random string) on the function. The deploy keeps them: it changes only `BOT`.

## Deploying

[`bot`](bot) names the bot that is deployed: the ledger's champion, which an iteration that crowns a new one changes. Only a bot that a tournament measured is deployed.

**On main, by itself.** [`deploy-bot.yml`](../../.github/workflows/deploy-bot.yml) runs on every push to main that changes `bots/`, `hosting/lambda/` or `uv.lock`, and from the Actions tab. It runs `scripts/check.sh`, builds the zip, uploads it, updates the function's code and its `BOT` (keeping its other variables), and checks that `GET <url>/health` names the bot. It signs in with GitHub's OIDC as the role `island-battles-league-bot-deploy`, which only main of this repository may assume, and which may only upload `bot.zip` and update this one function. The repository variables `AWS_DEPLOY_ROLE_ARN`, `BOT_BUCKET` and `BOT_FUNCTION` say where.

**By hand,** the same steps:

1. `hosting/lambda/build.sh [bot]` builds `dist/lambda/bot.zip` with `bots/<bot>/` (the one `bot` names by default).
2. Upload it to `s3://island-battles-league-bot-<account>/bot.zip`, then call `UpdateFunctionCode` with that S3 object.
3. When the bot changed, set `BOT=bots.<bot>.bot:play` with `UpdateFunctionConfiguration`, keeping the other variables.
4. Check the deployment: `GET <url>/health` should name the bot.
