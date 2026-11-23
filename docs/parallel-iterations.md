# Many iterations at once, no game played twice

A design. Nothing here is built yet. It changes the rules of the loop, so each part, once built, is a change of the league's setup with its own ledger entry ([`league-breeding`](../.agents/skills/league-breeding/SKILL.md)).

## Why only one iteration runs now

An iteration holds its number from the claim to its merge, 19 to 39 minutes (`ledger/progress.csv`, iterations 36 to 39), and everything else waits. The lock is that wide because four things are shared:

| What | Why two iterations collide on it |
|---|---|
| **The number and the ledger** | N is the ledger's last entry plus one. Two iterations from the same entry are both N, and both edit the top of `ledger/iterations.md` (The lines, Lessons so far). |
| **The population** | Each iteration deletes bots that play alike, promotes, retires, closes side lines and applies the caps. Two that start from the same population each decide against a field the other one changes. Two fixes of the same head can both be promoted, and the head has two children. |
| **The maps** | Seeds are N01, N02, N03, so two iterations called N make the same three maps under different names. |
| **The result cache** | It is shared by the checkouts of one machine (`runs/cache`, `LEAGUE_SHARED`) and, in the automated iteration, by the runners of one run (artifacts merged by `.github/actions/league-cache`). Two machines, or two runs, don't see each other's matches. |

Games are played twice even with one iteration at a time:

- **The first half's games.** In the automated iteration, the matches Claude's runner plays (rematches, the candidates' head-to-heads, a founder's rounds against the champion) aren't passed on, so that Claude can't plant a result (`hosting/rsi/README.md`, *No result Claude could have written is trusted*). The gate's runners play every head-to-head again.
- **A cold machine.** A new cloud session or a new desktop starts from an empty cache and plays the population's 5,700 training matches again, about 4 minutes on 6 cores (README, *Speed*).
- **Two runs of the workflow.** Each restores the last saved cache. Whatever another run played since then is played again.

The study is done twice too. Two iterations from the same entry see the same champion and the same lost games, and both read them.

## The idea

**Play once, decide in order.** An iteration is two different kinds of work:

1. **Work that depends only on code**: playing a match, building a bot, reading a game. Its result is a function of its input. It can run anywhere, at any time, in parallel, and it should run exactly once in the league's life.
2. **Decisions that change the population**: promotions, deletions, the champion, the ledger's number. They must happen one at a time, but they are mechanical rules applied to tables that come from the cache, and they take seconds.

Today the lock covers both, so it lasts the whole iteration. The design covers only the second with it. Three parts:

- **A match store** that every machine reads and only trusted players write, with a lease on each match key, so a match is played once in the league's life ([part 1](#part-1-the-match-store)).
- **Runs and the integrator.** Many **runs** work at once, each from whatever `main` was when it started, and each ends as a **proposal**: candidates and findings, not decisions. A deterministic **integrator** applies the selection and population rules to each proposal against the current `main`, one proposal at a time, in about a minute ([part 2](#part-2-runs-and-the-integrator)).
- **Leases on the rest of the work that should happen once**: a real game, a league game to study, a place in the slate, an idea, a bot's name ([part 3](#part-3-leases-on-the-rest)).

```
         run A ─┐        study, write, play ──► proposal A ─┐
         run B ─┼─ many at once, each from main            ├─► integrator ─► main (iteration N, N+1, ...)
         run C ─┘        study, write, play ──► proposal C ─┘   one at a time, about a minute each
                           │      ▲
                 lease, request   │ results
                           ▼      │
                   match store + players: each match key played once, ever
```

## Part 1: the match store

### What it holds

The cache as it is now (`<key>.json` and `<key>.json.gz` for each match), moved from one machine's `runs/cache` to one store for the whole league: an S3 bucket next to the hosted bot's, in `eu-central-1`, under the game's pin (`<pin>/<key>.json`). The key stays `match_key` in `league_tools/tournament.py`. It covers the runner's build, the map's hash, the seats, the bots' code and SDK, and the settings, so a result is as good on every machine. Bot binaries go there too (`bin/<name>-<hash>`), and the runner's (`runner/<build-hash>`), so no machine builds what another already built.

`runs/cache` becomes a read-through copy: `cached_result` looks locally, then in the store, and keeps what it found.

### Exactly once: a lease per key

S3 has conditional writes (`PutObject` with `If-None-Match: *` creates an object only if it doesn't exist; `If-Match: <etag>` replaces one only if it is unchanged). That is all a lease needs:

1. **Result there?** Take it. The match is not played.
2. **Lease** `leases/<key>`, created with `If-None-Match: *`, holding the player's id and an expiry (two minutes past the match's expected time). Of two players that try, one wins.
3. **The winner plays**, writes `<key>.json.gz` then `<key>.json` (a result counts once its `.json` is there, as now), and deletes the lease.
4. **The loser doesn't play.** It moves on to its other matches, and at the end waits for the leased ones' results.
5. **An expired lease** is taken over with `If-Match` on its ETag: its player died. That is the one way a match is started twice, and the first start left no result, so no game is ever played twice to the end.

**A failed turn** is played again on purpose, as now: a turn can time out because the machine was busy. The store keeps the attempt (`failed/<key>-<n>.json`) without counting it as the result, and caps the retries at three. After three failures the match is a real failure of the bot, the result says so, and `--strict` fails. The retry is a second measurement of a broken one, not a duplicate.

### Who may write

A result in the store is trusted by every later iteration, so **only players write it**. A player is a process that builds bots from code it was sent, plays them in the runner, and has nothing else running on its machine: no Claude, no real game. A machine where Claude runs, in the workflow or in a person's session, **only reads and requests**:

- **Request** (`league request`, called by `league tournament`): send the code of the bots the store has no binary for (a bot's directory as a tarball, content-addressed by `gobots.fingerprint`), and the list of matches. The request service writes the code and queues the keys that have neither a result nor a lease. Sending code can't fake a result: the player builds and plays it, and the bot tests' import rules already make every bot untrusted but harmless code.
- **Read**: the results and demos, by key.

So Claude's first half sends its rematches and head-to-heads to the players instead of playing them, and the gate finds them in the store. The duplicate of the first half is gone, and so is the reason for it.

The request service is a Lambda behind a URL (as the hosted bot's page already is). It takes a GitHub OIDC token from the workflow's jobs, or a per-person token in a session, and gives an iteration a scoped token that can request and read, never write. It limits each token to a number of matches a day, which caps what a misled model can spend.

### The players

Any machine that runs `league player` and has the write role:

- **Lambda** (arm64, 2 to 4 GB, so 1 to 2 vCPU), triggered by the queue in batches of matches, each batch one run of the headless runner. A Go bot's turn costs about 1.3 ms in the runner, so a 123-turn match is about a third of a second; a batch of 50 matches fits in a minute. A thousand Lambdas at once play the whole league's 5,700 training matches in seconds. This is the recommended default: it is in the account and region the league already uses, and it costs nothing while nobody plays.
- **GitHub runners**, as the warm and gate jobs are now: `league player --drain` instead of `league tournament --shard K/N`. Sharding by key stays as a fallback for a run without the store.
- **A person's desktop**, as a player while it is idle (`league player`), if its owner gives it the role. It builds only from code in the store, never from its working tree.

One tournament still plays at a time on a machine (`.play.lock`). That rule is about a machine's cores and stays as it is.

**Outside opponents** (`opponents.local.toml`, not in git) are the one player kind a remote player can't run. Their matches keep being played on the machine that has them, and are written to a local cache only. Until an outside opponent is in the store's config, its games stay one machine's.

### What changes for a tournament

Nothing an iteration reads. `league tournament` plans the same matches, finds them in the local cache, then the store, requests the missing ones, plays them locally only when no store is set (`LEAGUE_STORE` unset: a person working offline, the pull request checks), and prints the same tables. The `Time:` lines gain one for waiting on the players.

## Part 2: runs and the integrator

### A run

A **run** is today's iteration without its decisions. It does steps 0 to 4 and step 5's tables as now, from the `main` it started on (its **base**), and ends with a **proposal** on its branch `claude/league-run-<id>`:

- its candidates under `bots/` (status `candidate`), each with its kind, parent, line and idea in `bot.toml`, as now;
- its three new maps;
- `ledger/runs/<id>.md`: what is now the ledger entry, without the standings and decisions: the findings with their games and turns, the slate and why, each candidate's rematch and head-to-head, the tables the run saw on its base, ideas not tried, the review of the league itself, lessons proposed, the time;
- the studies of the real games it took (`ledger/studies/<id>.md`).

A run doesn't promote, delete, retire, close or change `hosting/lambda/bot`. It may still reject: a candidate that fails the head-to-head or the gate against its own parent is rejected by the run. That decision is about the candidate alone, so it doesn't depend on what other runs do. A run's id is its claim's (below). Its maps' seeds come from the id, not from N.

### The integrator

`league integrate <run-branch>` is a deterministic tool, not an agent. It applies the proposal to `main` as it is now (the **head**) and writes iteration N, the next number of the ledger:

1. **The field.** The head's population, plus the proposal's candidates and maps.
2. **The missing matches.** Every match of the selection's tournaments (`--add CANDIDATES` on the training, holdout and all maps) that the store doesn't have. These are the candidates against the bots that entered `main` after the run's base, and everyone on the maps that other runs added. None was ever played, so none is a duplicate. With the players, a minute or less.
3. **The rules**, as [`league-evidence`](../.agents/skills/league-evidence/SKILL.md) and [`league-population`](../.agents/skills/league-population/SKILL.md) give them. They are already mechanical: the words of the paired table (confirmed, clear, clearly worse), the points against the references, `main.go` shorter, plays alike nobody, a third or three fifths against the champion. Each run's candidates are judged against the head, not against its base.
4. **The population's upkeep** on the result: bots that play alike, side lines' counts and closures, the caps, the main line's change. Today an agent does this from the tables, by rules that leave no choice.
5. **The record.** Appends `## Iteration N` to `ledger/iterations.md`: which run, its base, the decisions with their numbers, the standings on both map sets, the champion before and after, and a link to `ledger/runs/<id>.md`. Writes the row of `ledger/progress.csv` and `hosting/lambda/bot`. Updates the table **The lines**, which is data the rules produce.
6. **One commit** onto `main`, through a merge queue or a workflow whose concurrency group is `integrate`: the one lock that is left. It is held for the minute of steps 2 to 6, not for the run's half hour.

Writing the rules as code is most of the work of this design, and it is also worth doing alone: today an agent applies 30 lines of rules by hand in every iteration, and a tool that applies them is tested once.

### A candidate whose parent moved

Run A and run B both write a fix of the champion `X`. A integrates first and promotes `X_a`, the new champion. When B integrates, its `X_b` has a parent that is no longer the head.

- **`X_b` is judged against the head**, `X_a`, with the same paired table and the same rule as against a parent. That is a stricter test (more games differ), and it is the right one: `X_b` becomes the head only if it is clearly better than the bot it would replace.
- **If it passes against its own parent but not against the head**, it is **superseded**: deleted, and recorded as a graft that has evidence for it. The next main-line place in any run takes it first: "graft `X_b`'s change into `X_a`" is the cheapest good candidate the league has, since `league-ideas` already says to graft whenever two candidates were promoted from one parent.

A side line's candidate, a founder and an exploiter are judged as now: the champion's points against them come from the head's champion. A founder that finds both side places taken at integration is **waiting**: kept as a candidate, offered the next free place, and deleted after three integrations. In practice part 3's slots stop this from happening.

### The ledger

- `ledger/iterations.md` grows by the integrator only, so runs never conflict on it.
- **Lessons so far** gets no edits from a run. A run proposes lessons in its own file. A **curator run**, an agent with no candidates, every ten integrations or when a run asks, folds the proposed lessons into the top of the ledger. It is the only writer of that section.
- `league ledger` prints the lines, the lessons, the candidate lines (now read from the integrator's entries and the runs' files), the last three iterations, and the proposed lessons not folded yet.

## Part 3: leases on the rest

Some work besides playing should happen once. Each gets a lease, created atomically. The lease is a git ref on GitHub (`refs/league/<kind>/<name>`, created only if absent, as `scripts/claim-iteration.sh` does today with a branch) or a store object with `If-None-Match`. Refs need no new service and show up in `git ls-remote`. The store works from a Claude step that has no push access, which the automated iteration needs. Use the store, with `league lease` as the one command.

| Lease | Held by | Stops |
|---|---|---|
| `run/<id>` | a run, from start to integration | nothing by itself: it names the run, its base and who runs it, as the claim does now |
| `real/<game-id>` | a run, until integrated | two runs studying the same real game. `ledger/real-games.txt` is written by the integrator. |
| `study/<match-key>` | the run that reads a league game | two runs reading the same game. The findings go to `studies/league/<match-key>.md` in the store (league games only, so they may be shared). A second run that wants that game reads them instead of reading it again. A finding is about a game and two bots' code, both fixed by the key, so it stays true. |
| `slot/<head>/<place>` | a run, for its slate | two runs filling the same place: the same side line's candidate twice, a third founder when two places are free. `<head>` is the commit of `main`, so the slots open again when it moves. |
| `idea/<hash>` | a run, for a candidate's idea | two runs writing the same fix. The hash is of the finding's mechanism in a few words, chosen by the run. The check is an agent's: before claiming, `league lease list idea` shows the ideas held, and a run doesn't write one that is the same idea in other words. |
| `name/<bot>` | `league new`, for good | two bots with the same name |

A lease expires (an hour, renewed by the run while it works) so that a dead run frees its places. `scripts/claim-iteration.sh` becomes `league lease run`: there is no iteration number to claim any more.

### The slate becomes the league's

The slate of [`league-ideas`](../.agents/skills/league-ideas/SKILL.md) is per iteration. With many runs, it is the list of places open on the head, and a run takes the places it can fill:

- **Each side line**: one place at a time. Its rule counts iterations of work in a row, and two candidates of one side line at once would integrate as two iterations of work.
- **An exploiter**: one, while no player outside the main line takes a third of the points from the champion.
- **Founders**: as many as the free side places, minus the founders already held.
- **The main line**: open-ended, each with a distinct idea lease. This is where the scale comes from. A run is one to six candidates, so twenty runs are a slate of 20 to 120 candidates on the main line, each with a finding of its own.

Twenty runs at once means twenty agents, so this costs Claude usage, not games: [the cost of scale](#what-it-costs).

## What keeps it honest

- **Every decision is still made against the field that will exist after it.** The integrator judges each candidate against the head, with every match against the bots other runs added. A run's own tables are its evidence for its work, never for a promotion.
- **Holdout maps stay unread.** Nothing in this design reads a holdout game. Each run adds two holdout maps, so the holdout set grows faster, and the maps another run added are untouched by this run's choices. That is better than now.
- **More candidates, more lucky passes.** Each candidate's chance of passing by luck stays the same (the rules' 5% and 20%), so twenty times the candidates gives about twenty times the lucky promotions, alongside twenty times the real ones. Two things hold this back. First, a candidate that integrates after others is judged on more maps and against a head that changed, so luck has to hold twice. Second, the league already measures progress by points against the references and the fixed opponents, which no run changes. If the champion's rating rises and those points don't, the bar is too low: make "clear" (5%) the rule for every promotion of the main line, a change to `league-evidence`.
- **Holdout reuse.** Many selections on one holdout set leak information through which candidates pass, even when nobody reads a game. Fresh maps per run help, since each run's candidates also meet holdout maps nobody chose with them in mind. If promotions come faster than the references' points move, a candidate could be confirmed only on holdout maps added after its run's base. That is a later rule, not part of the first version.
- **Nothing Claude writes is trusted as a result.** Only players write the store. The workflow's other protections (no credentials while Claude runs, the scope check, the name check, the fresh checkout after each half) stay as they are. The integrator runs in a job where no Claude ran.

## What it costs

- **Games:** fewer than now for the same number of iterations. The first half's games, a cold machine's league and two runs' overlap are each played once. What remains is linear in the new bots and the new maps.
- **Claude:** linear in the number of runs. Each automated run uses the subscription the workflow runs on (`CLAUDE_CODE_OAUTH_TOKEN`), so twenty runs at once use it twenty times as fast. The knob is `RSI_MAX_RUNS`, below.
- **Compute:** Lambda time for the matches, a few cents per thousand matches at 2 GB and a third of a second each. Plus S3 for the store: demos are a few tens of KB compressed, and a million matches is tens of GB.
- **Maps:** each run adds three maps, and every map is a match for every pair. Twenty runs a day add 60 maps, which at today's population of about fifteen players is about 60 × 15 × 14 = 12,600 matches a day for the population alone. That is cheap for the players but not free. If the map sets grow faster than the evidence needs, the integrator can add the three maps instead, once per N integrations. That choice belongs to [`league-evidence`](../.agents/skills/league-evidence/SKILL.md)'s Maps section.

## How many runs at once

The workflow's concurrency group moves from the whole iteration to the integrate job. A dispatcher, a scheduled workflow or the real-game dispatch itself, starts a run while:

- fewer than `RSI_MAX_RUNS` runs hold a lease (default 4 to start, then raised as the numbers below allow), and
- a slot is open on the head, or the main line has an idea in **Ideas not tried** that nobody holds, or a real game nobody holds is waiting.

A person's session is a run like any other. It takes its leases, works, and pushes its proposal; the integrator decides.

Raise `RSI_MAX_RUNS` while three numbers stay healthy, all in the ledger: the share of a run's proposals that are superseded at integration (above a half, the runs are writing the same thing), the integrator's queue time (above ten minutes, the lock is the bottleneck again), and the champion's points against the references per day.

## Building it, in order

Each step is useful alone and can be measured before the next starts. The time of each iteration goes in the ledger, as the [`measuring-time`](../.agents/skills/measuring-time/SKILL.md) skill asks.

1. **The match store and the players.** `league_tools/store.py` (read-through, leases, requests), `league player`, the request service, the bucket and the write role. The workflow's warm and gate jobs become players, and the first half requests instead of playing. Check: a full tournament through the store gives the results the local cache has, and the first half's head-to-heads are not played again by the gate (count the `to play` lines). This removes every duplicate game that exists today, even with one iteration at a time.
2. **The rules as code.** `league decide`, which reads the selection's tables and prints the decisions and the population's upkeep that the skills now ask an agent to make. Run it next to the agent in two or three iterations. It must agree with every decision the agent made, or the difference must be a mistake the agent made.
3. **Runs and the integrator.** Split the ledger (`ledger/runs/`, the integrator's entries, proposed lessons, the curator run). Add `league integrate`, the integrate workflow, the run branches and the leases of part 3. Change the [`bot-league-iteration`](../.agents/skills/bot-league-iteration/SKILL.md) skill: its steps 5 to 7 shrink to writing the proposal. Change `scope.py` for `claude/league-run-` branches, which may not change a status but a candidate's. Check with two runs at once from the same base, one of them a main-line fix that is sure to pass: the second must integrate against the first's promotion.
4. **Many runs.** The dispatcher and `RSI_MAX_RUNS`. Lift the concurrency group of `real-game-iteration.yml` off the run.

## Questions for a person

- **Lambda players, or GitHub runners only?** Lambda needs an IAM role for the players and a URL for requests. Runners need nothing new, but each run then plays only on its own runners, and two runs that request the same match at the same time still play it once (the lease), just more slowly.
- **Does a person's desktop write to the store?** It makes a 32-thread desktop a fast player. It also makes that desktop trusted: nothing Claude runs on it may hold the write role.
- **Is the integrator allowed to merge to `main` with nobody reading it?** The automated iteration already merges itself, so this changes how often, not whether.
- **Two side lines**, the population's cap, limits the parallel places outside the main line to about four. More side lines would give more independent lanes, which is the island model of the evolution literature that [`league-breeding`](../.agents/skills/league-breeding/SKILL.md) draws on. That is a change of the breeding rules, measured on its own, not part of this design.
