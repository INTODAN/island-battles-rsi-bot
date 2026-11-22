# The automated iteration: real games in, a merged iteration out

Every real game the hosted bot finishes starts a league iteration that studies it, with nobody in the loop:

```
hosted bot (hosting/lambda) ── packs games/<id>/game-<id>.zip in S3
        │ S3 event notification: games/ ... .zip
        ▼
notifier (notifier.py, a Lambda) ── skips a game whose demo is still pending
        │ repository_dispatch "real-game"
        ▼
real-game-iteration.yml (GitHub Actions)
   1. downloads the final games that ledger/real-games.txt doesn't list (real_games.py), into runs/real/
   2. Claude Code runs the bot-league-iteration skill on them
   3. commits, checks the scope and the names (scope.py) and scripts/check.sh
   4. pushes claude/league-iteration-N, opens the pull request, and merges it once the checks pass
        ▼
deploy-bot.yml deploys the champion that hosting/lambda/bot names
```

| File | What it is |
| --- | --- |
| [`notifier.py`](notifier.py) | The Lambda that turns a packed zip into a `repository_dispatch`. |
| [`real_games.py`](real_games.py) | Lists the games bucket and unpacks the final games no iteration has studied, newest `--limit` first. |
| [`scope.py`](scope.py) | Fails when an iteration's diff touches anything but `bots/<name>/`, the ledger (with `ledger/studies/<id>.md`, the study of a real game that the bot's page shows), `hosting/lambda/bot` or a new map, and when a real game's player name is on an added line. The pull request checks run it on every `claude/league-iteration-` branch. |
| [`../../.github/workflows/real-game-iteration.yml`](../../.github/workflows/real-game-iteration.yml) | The workflow. |

## How it behaves

- **One iteration at a time.** The workflow's concurrency group keeps one run going and one waiting; dispatches that arrive meanwhile replace the waiting one. The waiting run studies every final game that no iteration has studied, up to `RSI_GAMES_PER_RUN` (10), so a burst of games makes one more iteration, not one each. A game left out by the limit is studied by a later run.
- **The run holds the queue until its pull request has merged**, so the next iteration starts from this one's ledger entry. While an automated iteration's pull request is open (its checks failed, or it didn't merge within an hour), every later run fails at its first step and the games wait: fix or close that pull request, then start the workflow again from the Actions tab.
- **No cap.** Each merge deploys a bot, whose games start more iterations. Each iteration runs on your Claude subscription (`CLAUDE_CODE_OAUTH_TOKEN`), so the iterations share your plan's limits with your own use.
- **The model** is `RSI_MODEL`, Opus by default; the skill lets it hand candidates to Sonnet subagents. Set it to `sonnet` to spend less.
- **Nobody plays the other player's bot.** The iteration studies the games that happened; it never starts one (the skill's *No games against another player's bot*).

## What keeps it safe without a reviewer

A real game's demo holds the other players' names and their bots' log lines: text written by someone else, which Claude reads. The protections hold even if the model is talked into something:

- **Claude's step can write nothing outside the runner.** Its GitHub token is the workflow's read-only one, the checkout keeps no git credentials, the AWS credentials are cleared before it starts, and its tools are the league's commands, the file tools and `scripts/check.sh`: no web, no `git push`, no `gh`.
- **The App token that pushes and merges is made after Claude has finished**, and only after the scope check and `scripts/check.sh` pass.
- **The scope check is required by branch protection.** A change to a workflow, a tool, a test, a skill or an existing map can't merge from an iteration's branch, however it got there.
- **No names.** The scope check also fails when a player's name from the studied demos is on an added line or in the pull request's body, and prints the place, never the name: the checks' logs of a public repository are public.
- **A bot can't reach the network.** `tests/test_bots.py` allows only pure standard modules, so a bot that the model was misled into writing plays badly and loses the tournament; it can't send anything anywhere.
- **The real games stay out of git and out of the caches**: `runs/` is ignored, the cache holds `runs/cache` and `.runner` alone, and nothing is uploaded as an artifact (a public repository's artifacts are public).

What it doesn't protect against: a model that writes a worse bot that still passes the league's selection rules. Those rules are the gate, as they are for a person's iteration; a pull request merged here can be reverted like any other.

## What is deployed

In `eu-central-1`, next to the hosted bot:

| Resource | Name |
| --- | --- |
| Function | `island-battles-league-notifier`: `python3.14`, arm64, 256 MB, 30 s, handler `notifier.handler`, env `GITHUB_REPOSITORY` and `GITHUB_TOKEN_PARAMETER` |
| Code | `s3://island-battles-league-bot-<account>/notifier.zip` (`notifier.py` alone). No workflow deploys it: after changing `notifier.py`, zip it, upload it there and call `UpdateFunctionCode`. |
| Role | `island-battles-league-notifier`: its own logs, `s3:GetObject` on `games/*`, `ssm:GetParameter` on the token |
| Event | the games bucket's notification `real-game-zips`: `s3:ObjectCreated:*`, prefix `games/`, suffix `.zip` |
| Read role | `island-battles-league-games-read`: GitHub's OIDC, main of this repository only; `s3:ListBucket` on `games/*` and `s3:GetObject` on `games/*` |
| Logs | `/aws/lambda/island-battles-league-notifier`, 14 days |
| Token | `/island-battles-league/github-dispatch-token` (SSM SecureString): **made by hand**, never by an agent |

## Setting it up

Once, by hand. Nothing works until all of it is done; until then the dispatches find no workflow secrets and the run fails at Claude's step.

### GitHub

1. **A GitHub App** for the league, installed on this repository alone, with the permissions Contents: read and write, Pull requests: read and write, Issues: read and write (for the label), Metadata: read. Save its id as the repository variable `RSI_APP_ID` and a private key as the secret `RSI_APP_PRIVATE_KEY`.
2. **The Claude token:** run `claude setup-token` on your computer and save the token as the secret `CLAUDE_CODE_OAUTH_TOKEN` (`gh secret set CLAUDE_CODE_OAUTH_TOKEN`). In a narrow terminal it prints the token across two lines; the workflow removes the line break that a paste keeps.
3. **Settings → General → Allow auto-merge** on.
4. **A ruleset for `main`:** require a pull request (no approvals), and require the status checks **League** and **Iteration scope**. Without the required checks, `gh pr merge --auto` merges at once.
5. **A fine-grained token for the notifier:** this repository only, Contents: read and write (what `repository_dispatch` needs). It goes into SSM below, not into GitHub.
6. Optional variables: `RSI_MODEL` (`opus` or `sonnet`), `RSI_GAMES_PER_RUN`.

### AWS (`eu-central-1`, next to the hosted bot)

1. **The token:** an SSM SecureString parameter `/island-battles-league/github-dispatch-token` holding the fine-grained token.
2. **The notifier:** a function `island-battles-league-notifier`, `python3.14`, arm64, 256 MB, 30 s, code `hosting/rsi/notifier.py` zipped alone, handler `notifier.handler`, env `GITHUB_REPOSITORY=INTODAN/island-battles-rsi-bot` and `GITHUB_TOKEN_PARAMETER=/island-battles-league/github-dispatch-token`. Its role may write its own logs, `s3:GetObject` on `arn:aws:s3:::island-battles-league-games-<account>/games/*` (it reads the summary inside the zip: the `game.json` next to it is written after the zip), and `ssm:GetParameter` on that parameter.
3. **The event:** allow `s3.amazonaws.com` to invoke the notifier (from the games bucket's ARN and account), then add an event notification to the games bucket: `s3:ObjectCreated:*`, prefix `games/`, suffix `.zip`, to the notifier. Adding it with `PutBucketNotificationConfiguration` replaces the bucket's whole configuration: read it first and keep what is there.
4. **The read role for the workflow:** `island-battles-league-games-read`, assumed with GitHub's OIDC (the provider the deploy role uses) only by `repo:INTODAN/island-battles-rsi-bot:ref:refs/heads/main`, with `s3:ListBucket` on the games bucket for the prefix `games/*` and `s3:GetObject` on `games/*`, nothing else. Save its ARN as the repository variable `AWS_GAMES_READ_ROLE_ARN`, and the bucket's name as `GAMES_BUCKET`.

### Trying it

Start **Real-game iteration** from the Actions tab: it studies the newest final games that no iteration has studied. The first run finds every game the hosted bot ever kept and takes the newest ten.
