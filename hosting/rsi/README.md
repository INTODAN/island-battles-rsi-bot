# The real-game study: real games in, their mistakes on the hosted bot's page

Each real game the hosted bot finishes is studied for its mistakes, with nobody in the loop, and the study goes onto the hosted bot's page. That is all the automation does: it runs no iteration, writes no candidate and plays no tournament. Iterations are run by asking for one ("run a league iteration"), and their proposals still go through the integrator ([`integrate.yml`](../../.github/workflows/integrate.yml), [docs/parallel-iterations.md](../../docs/parallel-iterations.md)).

```
hosted bot (hosting/lambda) ── packs games/<id>/game-<id>.zip in S3
        │ S3 event notification: games/ ... .zip
        ▼
notifier (notifier.py, a Lambda) ── skips a game whose demo is still pending
        │ repository_dispatch "real-game"
        ▼
real-game-study.yml, one at a time
   1. study     downloads the final games ledger/real-games.txt doesn't list (real_games.py); Claude Code
                reads each one (league digest), finds the hosted bot's mistakes and writes
                ledger/analyses/<id>.md (the full analysis) and ledger/studies/<id>.md (two or three lines);
                only those files go into a clean checkout, which lists the games in ledger/real-games.txt
                and checks the diff for its scope and names (scope.py --kind study)
   2. publish   on a fresh runner: the diff onto its base, the same check, a pull request from
                claude/league-study-<run id>, merged once the checks pass
        ▼
deploy-bot.yml deploys the hosted bot again: its page shows each game's study and links its analysis
```

| File | What it is |
| --- | --- |
| [`notifier.py`](notifier.py) | The Lambda that turns a packed zip into a `repository_dispatch`. |
| [`real_games.py`](real_games.py) | Lists the games bucket and unpacks the final games no study has read, newest `--limit` first. |
| [`scope.py`](scope.py) | Fails when a branch's diff touches anything its kind may not: a study's (`--kind study`) may only add `ledger/studies/<id>.md` and `ledger/analyses/<id>.md` and list the games in `ledger/real-games.txt`; a run's (`--kind run`) may only add its candidates, its own files under `ledger/runs/`, `ledger/lessons/` and `ledger/studies/`, new maps and new detectors; an iteration's (the integrator's) also the ledger, the lines and `hosting/lambda/bot`. With `--names-from`, also when a real game's player name is on an added line. The pull request checks run it on every `claude/league-study-`, `claude/league-run-` and `claude/league-iteration-` branch. |
| [`run_times.py`](run_times.py) | Where a workflow run's time went, by job, by round of runners and by slow step. |
| [`../../.github/workflows/real-game-study.yml`](../../.github/workflows/real-game-study.yml) | The study: study, publish. |
| [`../../.github/workflows/integrate.yml`](../../.github/workflows/integrate.yml) | The integrator: the runs' proposals waiting become iterations on `main`. |

## How it behaves

- **One study at a time.** The workflow's concurrency group `real-game-study` runs one study at a time, and each waits for its pull request to merge, so the next one starts from a `main` that lists the games already studied and never studies one twice. A dispatch that arrives meanwhile waits; a newer one replaces it, and the study that starts takes every game still waiting, up to `RSI_GAMES_PER_RUN` (10), newest first. With none waiting, it stops at once.
- **What a study writes.** For each game, `ledger/analyses/<id>.md`: the map, the bot that played, the result, how the game went, its mistakes (most costly first, with their turns, the cause in the bot's logs or code, and what would have avoided it), what it did well, and which of the ledger's lessons from real games it confirms. And `ledger/studies/<id>.md`: two or three plain sentences, the main mistakes with their turns, which the page shows under the game with a link to the analysis. The workflow, not Claude, lists the game in `ledger/real-games.txt`. A game Claude couldn't read stays unlisted, for the next study.
- **The page.** The merge changes `ledger/studies/` and `ledger/analyses/`, which deploys the hosted bot again ([`deploy-bot.yml`](../../.github/workflows/deploy-bot.yml)): `build.sh` bundles both, and the page shows each study under its game with **The full analysis**, a link to the file on GitHub.
- **The cost is the subscription.** Each study uses your Claude subscription (`CLAUDE_CODE_OAUTH_TOKEN`). The model is `RSI_MODEL`, Opus by default; with several games it reads each one in a subagent of its own. Set it to `sonnet` to spend less.
- **Nobody plays the other player's bot.** A study reads the games that happened; it never starts one.

## What keeps it safe without a reviewer

A real game's demo holds the other players' names and their bots' log lines: text written by someone else, which Claude reads. The protections hold even if the model is talked into something:

- **Claude's step can write nothing outside its runner.** Its GitHub token is the workflow's read-only one, the checkout keeps no git credentials, the AWS credentials are cleared before it starts, and its tools are the file tools and `league digest`: no web, no `git push`, no `gh`, no tournament.
- **Nothing after Claude runs from Claude's working tree.** Claude's tools can change any file there, `scope.py` and `.git` too. After the study, only each chosen game's two files are copied, by a Python with no import from the working tree and no symlink followed, into a fresh checkout of the base, and that checkout's own `scope.py` checks it (`--kind study`, with names) before its diff leaves the runner. The publish job, on a runner Claude never ran on, applies only those paths of the diff to the base, and its own tools commit, check and push them. The name check reads the real games downloaded again after Claude, not the copies Claude had.
- **The App token that pushes the study is made after Claude has finished**, on the publish job's runner, after the scope check passes; it is revoked after the merge.
- **The scope check is required by branch protection.** A change to a workflow, a tool, a test, a bot or a skill can't merge from a study's branch, however it got there.
- **No names.** The scope check also fails when a player's name from the studied demos is on an added line, and prints the place, never the name: the checks' logs of a public repository are public.
- **The real games stay out of git and the artifacts**: `runs/` is ignored, and the one artifact is the study's diff, which leaves its runner only after the scope and name check passes on it.

What it doesn't protect against: an analysis that is wrong. It changes no bot; an iteration that builds on it still has to pass the league's selection rules.

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

Once, by hand. Nothing works until all of it is done; until then the dispatches find no workflow secrets and the study fails at Claude's step.

### GitHub

1. **A GitHub App** for the league, installed on this repository alone, with the permissions Contents: read and write, Pull requests: read and write, Issues: read and write (for the label), Metadata: read. Save its id as the repository variable `RSI_APP_ID` and a private key as the secret `RSI_APP_PRIVATE_KEY`.
2. **The Claude token:** run `claude setup-token` on your computer and save the token as the secret `CLAUDE_CODE_OAUTH_TOKEN` (`gh secret set CLAUDE_CODE_OAUTH_TOKEN`). In a narrow terminal it prints the token across two lines; the workflow removes the line break that a paste keeps.
3. **Settings → General → Allow auto-merge** on.
4. **A ruleset for `main`:** require a pull request (no approvals), and require the status checks **League** and **Iteration scope**. Without the required checks, `gh pr merge --auto` merges at once.
5. **A fine-grained token for the notifier:** this repository only, Contents: read and write (what `repository_dispatch` needs). It goes into SSM below, not into GitHub.
6. Optional variables: `RSI_MODEL` (`opus` or `sonnet`), `RSI_GAMES_PER_RUN` (the most games one study reads, 10 by default).
7. Optional, the match store, for the integrator: `LEAGUE_STORE` and `LEAGUE_STORE_ROLE_ARN`: [hosting/players/README.md](../players/README.md) says what to make first.

### AWS (`eu-central-1`, next to the hosted bot)

1. **The token:** an SSM SecureString parameter `/island-battles-league/github-dispatch-token` holding the fine-grained token.
2. **The notifier:** a function `island-battles-league-notifier`, `python3.14`, arm64, 256 MB, 30 s, code `hosting/rsi/notifier.py` zipped alone, handler `notifier.handler`, env `GITHUB_REPOSITORY=INTODAN/island-battles-rsi-bot` and `GITHUB_TOKEN_PARAMETER=/island-battles-league/github-dispatch-token`. Its role may write its own logs, `s3:GetObject` on `arn:aws:s3:::island-battles-league-games-<account>/games/*` (it reads the summary inside the zip: the `game.json` next to it is written after the zip), and `ssm:GetParameter` on that parameter.
3. **The event:** allow `s3.amazonaws.com` to invoke the notifier (from the games bucket's ARN and account), then add an event notification to the games bucket: `s3:ObjectCreated:*`, prefix `games/`, suffix `.zip`, to the notifier. Adding it with `PutBucketNotificationConfiguration` replaces the bucket's whole configuration: read it first and keep what is there.
4. **The read role for the workflow:** `island-battles-league-games-read`, assumed with GitHub's OIDC (the provider the deploy role uses) only by `repo:INTODAN/island-battles-rsi-bot:ref:refs/heads/main`, with `s3:ListBucket` on the games bucket for the prefix `games/*` and `s3:GetObject` on `games/*`, nothing else. Save its ARN as the repository variable `AWS_GAMES_READ_ROLE_ARN`, and the bucket's name as `GAMES_BUCKET`.

### Trying it

Start **Real-game study** from the Actions tab: it studies the newest final games that no study has read. The first one finds every game the hosted bot ever kept and takes the newest ten; each later one the next ten. Its pull request `claude/league-study-<run id>` merges itself once the checks pass, and the deploy that follows puts the studies on the page.
