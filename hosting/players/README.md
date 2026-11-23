# The match store and its Lambda players

Part 1 of [Many iterations at once, no game played twice](../../docs/parallel-iterations.md#part-1-the-match-store): one store of match results for every machine of the league, and players that play the matches someone asked it for. Nothing here is deployed yet; this file is what to make, by hand.

## How it plays

`LEAGUE_STORE` names the store: `s3://<bucket>/<prefix>` for the league's bucket, or a directory. Unset, nothing changes: a tournament plays and caches on its machine alone, as the pull request checks and offline work need.

- **A tournament** (`league tournament`, and `league rematch`, which plays through it) looks in the local cache, then in the store, and copies what the store has into `runs/cache`. In play mode (the default), it leases the matches nobody holds, plays them on its machine as without a store, and writes each result to the store. It waits for the matches that another machine holds, and takes over a lease that ended without a result.
- **In request mode** (`LEAGUE_STORE_MODE=request`), for a step that read real games, it writes no result: it sends the bots' code (`code/<fingerprint>.tar.gz`) and the maps (`maps/<sha256>.json`) the store lacks, queues the matches (`queue/<key>.json`) and waits for the players.
- **A player** (`league player`) leases queued matches, a batch at a time, plays them through the same runner and writes their results. It builds only code from the store, never a working tree's `bots/`, and checks a request before it plays: the code's fingerprint is the one asked for, its imports are the bot tests' (the SDK and pure standard packages, no cgo or assembly), the map's hash is its name, and the key is the one `match_key` gives for the player's own runner build. It builds and plays the bots without its AWS credentials in their environment. A request that fails a check is taken off the queue, and the player prints why.
- **Outside opponents** (`opponents.local.toml`) can't be played anywhere else: their matches are played on their machine and kept in its local cache alone.

The layout under the prefix, by runner build (the first 16 characters of its hash): `results/<key>.json` and `.json.gz` (the result counts once its `.json` is there, written after the demo), `leases/<key>`, `failed/<key>-<n>.json` (an attempt with a failed turn; the third is the result), `queue/`, `code/`, `maps/`. Each result says who played it (`played_by`). [`league_tools/store.py`](../../league_tools/store.py) has the details.

**One runner build per namespace.** A match's key covers the runner's build, and the build's hash changes with the architecture and the Go version that built it. A player serves only requests from machines whose runner has its hash: the image is built for x86_64 by default, like a GitHub runner (amd64), so Lambda serves their requests when it is built with the Go version the workflow uses (`GO_VERSION=... hosting/players/deploy.sh`; set `LEAGUE_GO_VERSION` to the same full version). An arm64 image would play a key space of its own. `league player` prints its build, and a tournament's matches show up under `<prefix>/<build>/`, so a mismatch is easy to see.

## The Lambda player

| File | What it is |
| --- | --- |
| [`Dockerfile`](Dockerfile) | The image: AWS Lambda's Python 3.14 base for `ARCH` (x86_64 by default, to share one key space with GitHub runners and most desktops), Go `GO_VERSION`, the league's tools installed with uv (`--extra store`, for boto3), the Go modules that `go.mod` pins with the SDK compiled into a warm build cache, and the runner built from `runner.toml`'s commit (`LEAGUE_RUNNER_BINARY`). No bot's code. |
| [`lambda_player.py`](lambda_player.py) | The handler, `lambda_player.handler`: `league player --drain` for one invocation, `{"batch": N}` matches at a time (25 by default), taking no new batch in its last two minutes. |
| [`deploy.sh`](deploy.sh) | Builds the image, pushes it to ECR and points the function at it. A person runs it. |

## What to make in AWS (`eu-central-1`, next to the hosted bot)

| Resource | What it is |
| --- | --- |
| Bucket | `island-battles-league-store-<account>`, private, no public access. General purpose buckets have the conditional writes the leases need. `LEAGUE_STORE=s3://island-battles-league-store-<account>/matches`. Optional: a lifecycle rule that expires `matches/*/queue/` objects after a week, for requests nobody played. |
| Image repository | ECR `island-battles-league-player`, private, keeping the last few images. |
| Function | `island-battles-league-player`: the image, `ARCH` (x86_64 by default, to share one key space with GitHub runners and most desktops), 3,538 MB (2 vCPU), timeout 900 s, ephemeral storage 4 GB, reserved concurrency 50 (what a burst may cost at most), env `LEAGUE_STORE` and `LEAGUE_PLAYER_ID=lambda`. |
| Schedule | EventBridge Scheduler, every 5 minutes, invokes the function with `{"batch": 25}`: the players that drain whatever is queued. A request may also wake players at once (`LEAGUE_PLAYER_FUNCTION`, below). |
| Player role | The function's execution role: its logs, and on the bucket `s3:GetObject`, `s3:PutObject` and `s3:DeleteObject` on `matches/*`, `s3:ListBucket` for the prefix `matches/`. The same S3 rights in a second role, `island-battles-league-store-player`, assumed with GitHub's OIDC by `repo:INTODAN/island-battles-rsi-bot:ref:refs/heads/main`: the workflow's warm, gate and players jobs. |
| Request role | `island-battles-league-store-request`, GitHub's OIDC, the same subject: `s3:GetObject` on `matches/*`, `s3:ListBucket` for `matches/`, and `s3:PutObject` only on `matches/*/queue/*`, `matches/*/code/*` and `matches/*/maps/*`, with the condition `"Null": {"s3:if-none-match": "false"}` so that it can only create, never replace; and `s3:PutObject` and `s3:DeleteObject` on `matches/work-leases/*`, the runs' leases (`league lease`), so that an automated run leases its places, ideas and games. Nothing on `results/`, `leases/` or `failed/`: a misled model could at worst drop another run's lease, which costs duplicated work, never a false result. Optionally `lambda:InvokeFunction` on the player function. The automated iteration's Claude steps run with this role. |

Then, in GitHub, the repository variables `LEAGUE_STORE`, `AWS_STORE_PLAYER_ROLE_ARN` and `AWS_STORE_REQUEST_ROLE_ARN`, and optionally `LEAGUE_PLAYER_FUNCTION` (the function's name, for requests to wake players), `RSI_STORE_PLAYERS` (the players job's runners, 2 by default) and `LEAGUE_GO_VERSION`. Unset `LEAGUE_STORE` and the workflow plays through artifacts as before.

On a person's computer: `LEAGUE_STORE=s3://... uv run league tournament` with credentials that may write (the player role's rights), and `uv run league player` to let an idle computer play the queue. `uv run` installs boto3 with the dev tools; `uv sync --extra store` without them.

## What is left for later

- **The request service.** The design's request path is a Lambda behind a URL that takes a GitHub OIDC token and gives a Claude step a scoped token that can request and read, never write, limited to a number of matches a day. Until it exists, request mode writes `queue/`, `code/` and `maps/` itself with the request role, which has no daily limit: a misled model could queue many matches, which cost Lambda time but never a false result.
- **Bot and runner binaries in the store** (`bin/`, `runner/`), so that no machine builds what another built.
- **Detectors after each match** (step 2 of the design's build), which the players are the place to run.
