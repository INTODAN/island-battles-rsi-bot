# The automated runs: real games and ideas in, proposals out, iterations merged

Many runs of the league work at once, with nobody in the loop ([docs/parallel-iterations.md](../../docs/parallel-iterations.md)). Each **run** starts from `main` as it is, studies, writes candidates and gates them, and ends as a **proposal** on its branch `claude/league-run-<id>`. The **integrator** decides every waiting proposal on `main`, one iteration each, and merges it:

```
hosted bot (hosting/lambda) ── packs games/<id>/game-<id>.zip in S3
        │ S3 event notification: games/ ... .zip
        ▼
notifier (notifier.py, a Lambda) ── skips a game whose demo is still pending
        │ repository_dispatch "real-game"          dispatch.yml (a schedule) ── repository_dispatch "league-run"
        ▼                                                │ while fewer than RSI_MAX_RUNS runs are leased
real-game-iteration.yml, a run, many at once ◄───────────┘ and `league ideas --free` has places
   1. start     stops at RSI_MAX_RUNS leased runs; chooses the final games ledger/real-games.txt doesn't
                list (real_games.py); leases the run (league lease run) and each game it gets (real/<id>)
   2. warm ×N   each runner plays a shard of the population's round robin (league tournament --shard K/N)
   3. study     Claude Code, the whole run: the skill's steps 0 to 4 and step 5's proposal
                (ledger/runs/<id>.md, ledger/lessons/<id>.md, the real games' studies), checked in a clean
                checkout for its scope and names before it leaves the runner
   4. propose   on a fresh runner: the run's paths onto its base, one commit, scope.py --kind run with
                the names, scripts/check.sh, the push of claude/league-run-<id>, a "run-ready" dispatch
        ▼
integrate.yml (no model, one at a time) ── league integrate: every waiting proposal becomes iteration N,
        │                                   N+1, ...; one pull request, merged once the checks pass;
        │                                   the runs' branches and leases are deleted
        ▼
deploy-bot.yml deploys the champion that hosting/lambda/bot names
```

With a match store (the repository variable `LEAGUE_STORE`, [hosting/players/README.md](../players/README.md)), the runners share their matches through the store, not artifacts: each warm runner plays its shard into the store and then the store's queue (`league player --drain`), and Claude's step runs its tournaments in request mode (`LEAGUE_STORE_MODE=request`): it reads the store and queues what it lacks. A **players** job of `RSI_STORE_PLAYERS` runners (2) runs beside it and plays that queue until the study has ended. A match played once, by any run or any machine, is never played again. The leases are the store's objects too. Without `LEAGUE_STORE`, the leases are git refs (`refs/league/leases/`), and Claude's runner plays its own gate.

| File | What it is |
| --- | --- |
| [`notifier.py`](notifier.py) | The Lambda that turns a packed zip into a `repository_dispatch`. |
| [`real_games.py`](real_games.py) | Lists the games bucket and unpacks the final games no iteration has studied, newest `--limit` first. |
| [`scope.py`](scope.py) | Fails when a branch's diff touches anything its kind may not: a run's (`--kind run`) may only add its candidates, its own files under `ledger/runs/`, `ledger/lessons/` and `ledger/studies/`, new maps and new detectors; an iteration's (the integrator's) also the ledger, the lines and `hosting/lambda/bot`. With `--names-from`, also when a real game's player name is on an added line. The pull request checks run it on every `claude/league-run-` and `claude/league-iteration-` branch. |
| [`run_times.py`](run_times.py) | Where a workflow run's time went, by job, by round of runners and by slow step. |
| [`../../.github/workflows/real-game-iteration.yml`](../../.github/workflows/real-game-iteration.yml) | A run: start, warm, study, propose. |
| [`../../.github/workflows/integrate.yml`](../../.github/workflows/integrate.yml) | The integrator: the proposals waiting become iterations on `main`. |
| [`../../.github/workflows/dispatch.yml`](../../.github/workflows/dispatch.yml) | The dispatcher: starts runs while fewer than `RSI_MAX_RUNS` are leased and the idea queue has free places. |
| [`../../.github/actions/`](../../.github/actions/) | `league-cache` sets up a runner and merges into its `runs/cache` what the run's other runners played; `league-cache-upload` uploads what this runner played. With a match store, neither shares matches: the store does. |

## How it behaves

- **Many runs at once.** The workflow has no concurrency group: every dispatch starts a run, and leases keep them off each other's work. A run first counts the `run/` leases held (`league lease list run/`) and stops with a notice at `RSI_MAX_RUNS` (10); its games wait for the next run.
- **Started by real games or by the dispatcher.** A `real-game` dispatch (the notifier's) studies the final games that no run has studied (`ledger/real-games.txt`) and no other run holds, up to `RSI_GAMES_PER_RUN` (10), newest first; when every one is taken, the run stops at once with a notice. A `league-run` dispatch (the dispatcher's, or the workflow started by hand) takes the waiting games too, and with none starts from `league ideas`: the league's open places, the most points first. By hand, the input `real_games: none` starts a run without games.
- **Leases, not a number.** A run has an id (`league lease run`, such as `20261124-3fa91c`), not an iteration number: the integrator numbers the iterations. The start job leases the run and its real games for 8 hours, since Claude's step can renew nothing, with an App token that is revoked at once (or, with a store, the player role). Claude's step leases its places, ideas, studied games and names through the store when there is one; without one it can't push, so it chooses its places from `league ideas --free`, which leaves out what other runs hold. A run that fails or is cancelled before its push drops its leases (the job **Release the leases**); a pushed proposal keeps them until the integrator drops them.
- **A run proposes; the integrator decides.** The run promotes, retires and deletes nothing that `main` has, and writes no ledger entry: its push is the proposal, and a `run-ready` dispatch starts the integrator (which also runs every 15 minutes). The integrator ([`integrate.yml`](../../.github/workflows/integrate.yml), concurrency group `integrate`, no model) takes every waiting proposal, the oldest base first, applies the selection and population rules as code against `main` as it is then (`league integrate`), writes iteration N's entry, `ledger/progress.csv`, `ledger/real-games.txt` and `hosting/lambda/bot`, and merges them in one pull request once the checks pass. While one of its pull requests is open, it waits for a person.
- **Every run says where its time went.** The last job, `Times`, writes [`run_times.py`](run_times.py)'s account to the run's summary page, whatever its result: each job's minutes and wait in the queue, each round of runners by its slowest, median and fastest runner, and every step of a minute or more. Claude reads the same account so far (`runs/rsi/times.txt`), times its own steps with `league clock`, and ends the run's account with the [`measuring-time`](../../.agents/skills/measuring-time/SKILL.md) skill's review and its `Minutes:` line, which the integrator copies into `ledger/progress.csv`.
- **The population's round robin is played on `RSI_SHARDS` runners at once** (8), since one runner has 4 CPUs. Each runner plays the slice that `league tournament --shard K/N` gives it, and uploads the matches it played; the study merges them into its cache and saves it before Claude starts, so a run that fails later keeps what they played.
- **The cost is the subscription.** Each run uses your Claude subscription (`CLAUDE_CODE_OAUTH_TOKEN`), and `RSI_MAX_RUNS` runs may go at once: they share your plan's limits with your own use. Lower `RSI_MAX_RUNS` to spend less.
- **The model** is `RSI_MODEL`, Opus by default; the prompt has it write fixes, grafts and simplifications with Sonnet subagents and read flagged windows with Haiku subagents, as the skill allows. Set it to `sonnet` to spend less.
- **Nobody plays the other player's bot.** A run studies the games that happened; it never starts one (the skill's *No games against another player's bot*).

## What keeps it safe without a reviewer

A real game's demo holds the other players' names and their bots' log lines: text written by someone else, which Claude reads. The protections hold even if the model is talked into something:

- **Claude's step can write nothing outside its runner.** Their GitHub token is the workflow's read-only one, the checkout keeps no git credentials, the AWS credentials are cleared before it starts, and its tools are the league's commands, the file tools and `scripts/check.sh`: no web, no `git push`, no `gh`. With a match store, the one AWS role Claude's steps have is the store's request role: it reads the store and creates requests, bots' code and maps (create only, never replace), and IAM gives it no write to results, leases or failed attempts, whatever the tools on the runner were changed to do. The App token that leases the run and its games is made before Claude, in the start job on another runner, and revoked as soon as they are leased.
- **Nothing after Claude runs from Claude's working tree.** Claude's tools can change any file there, the league's tools, `scope.py`, `.github/actions/` and `.git` too. After the study, only what a run may add (new candidates' directories under `bots/`, new files of `ledger/runs/`, `ledger/lessons/` and `ledger/studies/`, new maps, new detectors with their tests) is copied, by a Python with no import from the working tree and no symlink followed, into a fresh checkout of the base, and that checkout's own `scope.py` checks it (`--kind run`, with names) before its diff leaves the runner. The propose job, on a runner Claude never ran on, applies only those paths of the diff to the base, and its own tools commit, check (`scope.py --kind run` with names, `scripts/check.sh`) and push them. The name check reads the real games downloaded again after Claude, not the copies Claude had.
- **No result Claude could have written is trusted.** The cache is saved before Claude's step, never after, and what Claude's runner played isn't passed on: a fabricated result in `runs/cache` would otherwise count as a played match in every later run. The integrator plays the selection's matches itself, from the cache or the store, in a job where no Claude ran.
- **With a match store, a request can't fake a result either.** Claude's steps only ask; the players job's runners (Claude never ran on them) and the Lambda players play. A player builds only code from the store, and refuses a request whose code doesn't have the fingerprint asked for, imports anything but the SDK and the bot tests' pure standard packages, has cgo or assembly, names a map that isn't its hash, or has a key that isn't the game it describes; it builds and plays the bots without its AWS credentials in their environment. So a run's candidates can play before `scripts/check.sh` has passed on them: the player applies the import rule itself. Every result in the store says which machine and run played it (`played_by`). What a misled model can still do is queue many matches: they cost players' time, and a request service with a daily limit per token is the follow-up ([hosting/players/README.md](../players/README.md#what-is-left-for-later)).
- **The App token that pushes the proposal is made after Claude has finished**, on the propose job's runner, and only after the scope check and `scripts/check.sh` pass; it is revoked after the push. The run's branch can't reach `main` by itself: the integrator checks it again (`scope.py --kind run`) and merges only what it wrote, with its own token.
- **The scope check is required by branch protection.** A change to a workflow, a tool, a test, a skill or an existing map can't merge from a run's or an iteration's branch, however it got there.
- **No names.** The scope check also fails when a player's name from the studied demos is on an added line, and prints the place, never the name: the checks' logs of a public repository are public.
- **A bot can't reach the network.** `tests/bots/bots_test.go` allows only pure standard packages (no `os`, `net` or `time`), so a bot that the model was misled into writing plays badly and loses the tournament; it can't send anything anywhere.
- **The real games stay out of git, the caches and the artifacts**: `runs/` is ignored, and the cache holds `runs/cache`, `.runner` and Go's build cache alone. A public repository's artifacts are public, so the runners share only league games (`runs/cache`'s results and demos, of league bots, played by runners Claude never ran on) and the run's diff, which leaves its runner only after the scope and name check passes on it. The propose job never has the real games but for the name check, downloaded there.

What it doesn't protect against: a model that writes a worse bot that still passes the league's selection rules. Those rules are the gate, as they are for a person's iteration; an iteration the integrator merged can be reverted like any other.

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
6. Optional variables: `RSI_MODEL` (`opus` or `sonnet`), `RSI_GAMES_PER_RUN`, `RSI_MAX_RUNS` (the runs leased at once, 10 by default; the dispatcher reads it too), `RSI_SHARDS` (the runners that play at once, 8 by default; a public repository's free plan runs 20 jobs at a time).
7. Optional, the match store: `LEAGUE_STORE`, `AWS_STORE_PLAYER_ROLE_ARN` and `AWS_STORE_REQUEST_ROLE_ARN`, with `LEAGUE_PLAYER_FUNCTION`, `RSI_STORE_PLAYERS` and `LEAGUE_GO_VERSION` if wanted: [hosting/players/README.md](../players/README.md) says what to make first. The players job holds its role for up to 8 hours and Claude's step its own for 4: set the roles' maximum session duration to allow it. With a store, the start and release jobs lease through the player role.

### AWS (`eu-central-1`, next to the hosted bot)

1. **The token:** an SSM SecureString parameter `/island-battles-league/github-dispatch-token` holding the fine-grained token.
2. **The notifier:** a function `island-battles-league-notifier`, `python3.14`, arm64, 256 MB, 30 s, code `hosting/rsi/notifier.py` zipped alone, handler `notifier.handler`, env `GITHUB_REPOSITORY=INTODAN/island-battles-rsi-bot` and `GITHUB_TOKEN_PARAMETER=/island-battles-league/github-dispatch-token`. Its role may write its own logs, `s3:GetObject` on `arn:aws:s3:::island-battles-league-games-<account>/games/*` (it reads the summary inside the zip: the `game.json` next to it is written after the zip), and `ssm:GetParameter` on that parameter.
3. **The event:** allow `s3.amazonaws.com` to invoke the notifier (from the games bucket's ARN and account), then add an event notification to the games bucket: `s3:ObjectCreated:*`, prefix `games/`, suffix `.zip`, to the notifier. Adding it with `PutBucketNotificationConfiguration` replaces the bucket's whole configuration: read it first and keep what is there.
4. **The read role for the workflow:** `island-battles-league-games-read`, assumed with GitHub's OIDC (the provider the deploy role uses) only by `repo:INTODAN/island-battles-rsi-bot:ref:refs/heads/main`, with `s3:ListBucket` on the games bucket for the prefix `games/*` and `s3:GetObject` on `games/*`, nothing else. Save its ARN as the repository variable `AWS_GAMES_READ_ROLE_ARN`, and the bucket's name as `GAMES_BUCKET`.

### Trying it

Start **Real-game iteration** from the Actions tab: it studies the newest final games that no run has studied or holds, or, with none, starts from `league ideas`. The first run finds every game the hosted bot ever kept and takes the newest ten. Its proposal waits on `claude/league-run-<id>` until **Integrate** runs.
