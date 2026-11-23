# Many iterations at once, no game played twice

Built: the store and its players, the detectors, the rules as code (`league decide`), the integrator, the leases, the idea queue, the curator, the dispatcher and the four side lines. Deploying the store and the Lambda players to AWS is the one step left to a person (`hosting/players/README.md`); until then everything works as before on one machine, and the dispatcher starts one run at a time. It changes the rules of the loop, so each part, once built, is a change of the league's setup with its own ledger entry ([`league-breeding`](../.agents/skills/league-breeding/SKILL.md)).

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

Today the lock covers both, so it lasts the whole iteration. The design locks only the decisions. Four parts:

- **A match store** that every machine reads and writes (a person's computer, GitHub runners, Lambda), with a lease on each match key, so a match is played once in the league's life ([part 1](#part-1-the-match-store)).
- **Runs and the integrator.** Many **runs** work at once, each from whatever `main` was when it started, and each ends as a **proposal**: candidates and findings, not decisions. A deterministic **integrator** applies the selection and population rules to each proposal against the current `main`, one proposal at a time, in about a minute ([part 2](#part-2-runs-and-the-integrator)).
- **Leases on the rest of the work that should happen once**: a real game, a league game to study, a place in the slate, an idea, a bot's name ([part 3](#part-3-leases-on-the-rest)).
- **More runs on the same subscription**: detectors (code that finds known mistakes in every game once), a cheaper model for each bulk job, and ideas ranked by the points their mistake costs ([part 4](#part-4-more-runs-on-the-same-subscription)).

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

### Every machine plays and writes

A match is played wherever the tournament runs: a person's computer, a GitHub runner, a Lambda. Each one takes the lease, plays, and writes the result to the store, the same way. A person's computer running an iteration is no different from the workflow running one.

Each result records who played it (`played_by`: the machine and the run), so if one machine's results are ever in doubt, the store can drop that machine's results and the matches get played again.

**One exception: a Claude step that reads real games.** A real game's text was written by other players and may try to talk the model into something, such as writing a fake result that every later iteration would trust. So in the automated iteration, the steps where Claude has the real games **request** matches instead of playing them, and a machine that never saw those games plays them:

- **Request** (`league tournament` does it by itself when `LEAGUE_STORE_MODE=request`): send the code of the bots the store has no binary for (a bot's directory as a tarball, content-addressed by `gobots.fingerprint`) and the list of matches. The request service writes the code and queues the keys that have neither a result nor a lease. Sending code can't fake a result, because another machine builds the code and plays it. The bot tests' import rules already make every bot harmless code.
- **Read**: the results and demos, by key.

The automated iteration's first half then sends its rematches and head-to-heads to the queue instead of playing them on a runner whose results are thrown away, and the gate finds them in the store. The duplicate of the first half is gone, and so is the reason for it.

The request service is a Lambda behind a URL, as the hosted bot's page already is. It accepts a GitHub OIDC token from the workflow's jobs and gives the Claude step a scoped token that can request and read, never write. It limits each token to a number of matches a day, which caps what a misled model can spend.

### Where matches are played

The same command everywhere: `league tournament` plays its own missing matches, and `league player` plays the queue's.

- **Locally.** `league tournament` on a person's computer plays what the store lacks, with every core, as now. `league player` lets an idle computer play other runs' queued matches too.
- **GitHub runners**, as the warm and gate jobs are now: `league player --drain` replaces `league tournament --shard K/N`. Sharding by key stays as a fallback for a run with no store.
- **Lambda** (arm64, 2 to 4 GB, so 1 to 2 vCPU), triggered by the queue in batches of matches, each batch one run of the headless runner. A Go bot's turn costs about 1.3 ms in the runner, so a 123-turn match takes about a third of a second, and a batch of 50 matches fits in a minute. A thousand Lambdas at once play the whole league's 5,700 training matches in seconds. It is in the account and region the league already uses, and it costs nothing while nobody plays.

**Machines share games only when they build the same runner.** The key holds the runner binary's hash, and a game played on arm64 may differ in the last bit of a float from one played on amd64 (fused multiply-add), so a key is per architecture and Go version. GitHub runners and most desktops are amd64: the Lambda players are built for amd64 too (`hosting/players/`, `ARCH=x86_64` by default), so all of them share one key space. An Apple-silicon desktop plays its own.

Two machines that want the same match at the same moment don't both play it: one holds the lease, and the other waits for the result while it plays its own matches. One tournament still plays at a time on a machine (`.play.lock`). That rule is about a machine's cores and stays as it is.

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
6. **One commit** onto `main`, merged with nobody reading it, as the automated iteration is now. The integrator runs in a workflow whose concurrency group is `integrate`: the one lock that is left. It is held for the minute of steps 2 to 6, not for the run's half hour.

**Many proposals at once.** One integration a minute is 60 an hour, and with no cap on runs that becomes the limit again. So the integrator takes **every proposal waiting** when it starts, not one. It plays one tournament with all their candidates added, so their matches against each other are played once too, and then applies the rules proposal by proposal in a fixed order (the oldest base first). Each later proposal is judged against the head the earlier ones produced. Each proposal is still its own iteration N, N+1, ... in the ledger. A batch of twenty costs about as much time as a batch of one, since its matches are played by the players at once.

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

Twenty runs at once means twenty agents, so the cost of scale is Claude usage, not games. Part 4 is about that cost.

## Part 4: more runs on the same subscription

Most of a run's Claude usage goes on reading games: the digest, then the turns that decided the game with both bots' logs, game after game (iteration 39's study was 14.6 of its 25 minutes). Most of that reading looks for things code can find. Three changes move the reading to code and the rest to cheaper models, so Opus is spent where judgment is needed.

### Detectors: code finds the mistakes, once per game

A **detector** is a small Python function that reads one demo and returns the turns where a known mistake happened, each with its evidence in numbers:

```
detect(demo) -> [Flag(team, turns=(40, 52), kind="home_emptied",
                      evidence="home 34 -> 6 soldiers while an enemy stack of 30 stood 2.1 away", cost=...)]
```

- **Where they come from.** The ledger's **Lessons so far** and findings already describe the mistakes in words: long walks, attacks trickled in small groups, a border castle left thin, help that buys speed too early, strikes that land a turn after a burst, production bought while neutrals that pay back in 15 turns stay neutral, a game that runs to the turn limit while one side leads. Each one that can be stated in numbers becomes a detector. The game's state is in the demo every turn, so a detector needs no bot's code.
- **A turning point detector** for every game: the turn where the lead in production, soldiers or castles changed for good, and the turn of each castle lost. That is the window a study reads first today, found by hand.
- **Run once per match on a machine, kept by key.** `league mistakes` runs every detector on a demo the first time it needs its flags, and keeps them beside the demo in the local cache (`<key>.flags-<detectors-hash>.json`); a new or changed detector runs again. Flags never go to the store: computing them replays no game and takes milliseconds, and since a run can add a detector, a machine that writes the store never needs to run one.
- **`league mistakes`** sums them up for a tournament: for each bot and each kind of mistake, in how many games and how many points it cost, the shortest games where it happened, and the turns. The champion's table is what a study starts from: instead of choosing games to read whole, a run sees "`home_emptied` in 31 of the champion's 58 lost games, on 9 maps", with the windows to read.
- **Runs add detectors.** When a run finds a mistake that no detector knows, it writes the detector in the same run, with a test on the game where it found it, under `league_tools/detectors/`. A detector only flags turns. It never changes a result, a rating or a decision. `scope.py` lets a run's branch add a file there, and change none that exists. A detector is code that other people's sessions run, written by a model that may have read other players' games, so it is held to pure code as a bot is: a test parses every detector and refuses any import outside a short list (`math`, `dataclasses`, the demo readers) and any name such as `open`, `eval` or `getattr`, or a dunder attribute. A detector that flags too much (most turns of most games) tells nobody anything: its test checks that it doesn't flag the game's quiet turns. The library grows with every run, and each run reads less than the one before.
- **Holdout games are never scanned for a run.** `league mistakes` refuses holdout maps, as `rematch` does. The detectors still run on holdout demos when they are played, so the flags exist, but only a person may read them, to check whether a fix learned the training maps.

### A model for each job

The skill already lets candidates be written by Sonnet from a precise brief. With the detectors' windows, the reading becomes as precise:

| Job | Model | Why |
|---|---|---|
| Plan the slate; choose which flagged windows to read; judge each finding's evidence; write a founder's or exploiter's strategy; the review of the league itself | Opus | judgment, and short |
| Read one flagged window (`digest --turns` with both bots' logs) and say whether the flag's mistake is what happened, and why the bot did it | Haiku, one per window, many at once | a narrow question with the evidence in front of it |
| Write a fix or a graft from a finding with its evidence; run its rematch until the change acts | Sonnet | a precise brief, as now |
| Integrate | no model | the rules as code (part 2) |

Opus still reads every finding's evidence before it becomes a candidate, as the skill asks now. What changes is that it reads Haiku's answer and the quoted log lines, not the whole game.

### Ideas ranked by evidence

The dispatcher keeps an **idea queue**: every open place of the slate, every idea in **Ideas not tried**, every superseded candidate's graft, every kind of mistake in the champion's `league mistakes` table that no idea holds. Each has a score: the champion's points lost in games where its mistake shows, by maps (a map's games count once, as in the evidence rules), so an idea seen on many maps outranks one seen in many games of one map. Side lines' places and an exploiter that is due are taken first, since the population's rules need them every iteration. A new run takes the top idea nobody holds. Usage goes to the mistakes that cost the most points first, and a rare mistake waits until the common ones are fixed.

### What a run costs then

A run that starts from a ranked idea and a mistakes table skips most of step 2's choosing and reading, and its candidates are written by Sonnet. Rough guess, to be measured: a third of today's Opus usage per run, so ten runs at once cost about what three cost now. The time of each step and the models' usage go in each run's file (`measuring-time`), and the dispatcher's limit is set from them.

## What keeps it honest

- **Every decision is still made against the field that will exist after it.** The integrator judges each candidate against the head, with every match against the bots other runs added. A run's own tables are its evidence for its work, never for a promotion.
- **Holdout maps stay unread.** Nothing in this design reads a holdout game. Each run adds two holdout maps, so the holdout set grows faster, and the maps another run added are untouched by this run's choices. That is better than now.
- **More candidates, more lucky passes.** Each candidate's chance of passing by luck stays the same (the rules' 5% and 20%), so twenty times the candidates gives about twenty times the lucky promotions, alongside twenty times the real ones. Two things hold this back. First, a candidate that integrates after others is judged on more maps and against a head that changed, so luck has to hold twice. Second, the league already measures progress by points against the references and the fixed opponents, which no run changes. If the champion's rating rises and those points don't, the bar is too low: make "clear" (5%) the rule for every promotion of the main line, a change to `league-evidence`.
- **Holdout reuse.** Many selections on one holdout set leak information through which candidates pass, even when nobody reads a game. Fresh maps per run help, since each run's candidates also meet holdout maps nobody chose with them in mind. If promotions come faster than the references' points move, a candidate could be confirmed only on holdout maps added after its run's base. That is a later rule, not part of the first version.
- **A run that reads real games can't write a result.** Those steps only request (part 1), and every result says who played it. The workflow's other protections (no credentials while Claude runs, the scope check, the name check, the fresh checkout after each half) stay as they are. The integrator runs in a job where no Claude ran.
- **Detectors point; they don't decide.** A flag only chooses what is read. A finding still needs the turns read and the evidence quoted, and a candidate still has to pass the same rules. A wrong detector wastes reading, never a promotion.

## What it costs

- **Games:** fewer than now for the same number of iterations. The first half's games, a cold machine's league and two runs' overlap are each played once. What remains is linear in the new bots and the new maps.
- **Claude:** linear in the number of runs, and each run costs less than today's iteration (part 4). Each automated run uses the subscription the workflow runs on (`CLAUDE_CODE_OAUTH_TOKEN`). The knob is `RSI_MAX_RUNS`, below.
- **Compute:** Lambda time for the matches, a few cents per thousand matches at 2 GB and a third of a second each. Plus S3 for the store: demos are a few tens of KB compressed, and a million matches is tens of GB.
- **Maps:** each run adds three maps, and every map is a match for every pair. Twenty runs a day add 60 maps, which at today's population of about fifteen players is about 60 × 15 × 14 = 12,600 matches a day for the population alone. That is cheap for the players but not free. If the map sets grow faster than the evidence needs, the integrator can add the three maps instead, once per N integrations. That choice belongs to [`league-evidence`](../.agents/skills/league-evidence/SKILL.md)'s Maps section.

## How many runs at once

Nothing in the design caps it. Matches are played once whatever the number of runs. The integrator takes every waiting proposal in one batch. The main line's places are open-ended. What is left is the subscription, and how many distinct ideas the league has.

The workflow's concurrency group moves from the whole iteration to the integrate job. A dispatcher (a scheduled workflow, and the real-game dispatch itself) starts a run while:

- fewer than `RSI_MAX_RUNS` runs hold a lease (**10** to start), and
- the idea queue (part 4) has an idea nobody holds, or a real game nobody holds is waiting.

A person's session is a run like any other, on their computer. It takes its leases and the top idea, works, plays its matches into the store, and pushes its proposal. The integrator decides.

Raise `RSI_MAX_RUNS` while these numbers stay healthy, all in the ledger:
- **The share of proposals superseded at integration.** Above a half, the runs are writing the same thing.
- **Whether the idea queue empties.** Runs that take low-ranked ideas are spending usage on rare mistakes.
- **The champion's points against the references, per day.** If they stop rising while the rating rises, the promotions are luck (above).
- **The subscription's usage.** It must leave room for a person's own work.

## Building it, in order

Each step is useful alone and can be measured before the next starts. The time of each iteration goes in the ledger, as the [`measuring-time`](../.agents/skills/measuring-time/SKILL.md) skill asks.

1. **The match store.** `league_tools/store.py` (read-through, leases, `played_by`, requests), `league player`, the bucket, the request service and the Lambda players. Local tournaments, the workflow's runners and Lambda all play through it, and the automated first half requests instead of playing. Check: a full tournament through the store gives the results the local cache has, and the first half's head-to-heads are not played again by the gate (count the `to play` lines). This removes every duplicate game that exists today, even with one iteration at a time.
2. **The detectors.** `league_tools/detectors/` with the first ones written from **Lessons so far** and the turning point, `league mistakes`, and the players running them after each match. Check: on iteration 39's games, the flags point at the turns its findings named. This makes even today's single iteration cheaper, before anything runs in parallel.
3. **The rules as code.** `league decide`, which reads the selection's tables and prints the decisions and the population's upkeep that the skills now ask an agent to make. Run it next to the agent in two or three iterations. It must agree with every decision the agent made, or the difference must be a mistake the agent made.
4. **Runs and the integrator.** Split the ledger (`ledger/runs/`, the integrator's entries, proposed lessons, the curator run). Add `league integrate` with batches, the integrate workflow, the run branches and the leases of part 3. Change the [`bot-league-iteration`](../.agents/skills/bot-league-iteration/SKILL.md) skill: step 2 starts from `league mistakes` and hands windows to Haiku, and steps 5 to 7 shrink to writing the proposal. Change `scope.py` for `claude/league-run-` branches: they may add a detector, and may change no status but a candidate's. Check with two runs at once from the same base, one of them a main-line fix that is sure to pass: the second must integrate against the first's promotion.
5. **Many runs.** The idea queue, the dispatcher, and `RSI_MAX_RUNS=10`. Lift the concurrency group of `real-game-iteration.yml` off the run. Raise the cap of side lines to four, with its setup entry in the ledger ([below](#four-side-lines-once-runs-are-parallel)).

## Decided

- **Matches run anywhere**: a person's computer, GitHub runners and Lambda, all writing to the store the same way. Only a Claude step that reads real games requests instead.
- **The integrator merges to `main` with nobody reading it**, as the automated iteration does now.
- **10 runs at once to start**, with no cap in the design.
- **Runs may add detectors.**
- **To spend less of the subscription:** cheaper models for the bulk reading and writing, and ideas ranked by evidence. No candidates without Claude: the rule that a number is not an idea stays.
- **Four side lines** instead of two, from the step that starts many runs (below).

## Four side lines, once runs are parallel

The population's cap of **two side lines becomes four** in step 5 of the build, the step that starts many runs at once. It is a change of the league's setup, so it gets its own **Setup after iteration N** entry in the ledger, and [`league-population`](../.agents/skills/league-population/SKILL.md) and [`league-ideas`](../.agents/skills/league-ideas/SKILL.md) change with it.

**Why four.**

- **The league's main weakness is a field made of the champion's relatives.** After iteration 36, 71% of the champion's games, and 132.5 of the 141.5 points it lost, were against its own line and the sparring bot it began from (`league-breeding`, *What the review measured*). Every side line is a strategy that tests the champion from outside. Four of them make a field that measures the champion against more ways of playing.
- **The research the league follows says to keep more niches.** NEAT protects new structure inside its own species until it is tuned. POET's hardest problems were solved by moving solutions between niches. The Darwin Gödel Machine did better by keeping every working program than by building on the best one. The cap of two was set for an iteration of three to six candidates, and `league-breeding` says the league's lines are its niches.
- **Side lines are where parallel runs don't collide.** Main-line runs all start from one head, and when two of them pass, one is superseded. Runs on different side lines never touch each other's bots. With one run per side line at a time, four side lines are four runs that can't conflict.
- **The step changes came from outside the line** (`league-ideas`, *Why*): founders written from a real game's winner (iteration 7), from the real opponent's rules (25), and against a habit of those rules (34). Four places give founders twice the room.

**Why not now, and why not more.**

- **Not with one iteration at a time.** The slate gives every side line a place before the main line, and keeps one place for the main line. With four side lines, a slate of three or six would be mostly side lines, and the champion's line would get one candidate an iteration. Parallel runs remove that limit: each side line has its own run, and the main line has the rest.
- **Not more than four, yet.** Each side line adds up to three active bots, so four lines bring the population to about 25 players (three main-line bots, twelve on side lines, eight fixed opponents, the sparring bots and the default bots). With the store, a new candidate then costs about 25 × 2 × 57 ≈ 2,900 matches, under a minute on Lambda. Beyond that, the field's ratings and the **Bots that play alike** table start to fill with weak relatives of weak lines. Four is a step that can be measured. If, after ten integrations with four, every side line still promotes and the champion gains points against them, the next step is six.

**What else changes with it.**

- **Founders get a lower cost to try.** With more free places, a founder is written whenever a place is free, as now. The rule that admits it (a third of the points from the champion, and playing like no bot in the league) stays as it is.
- **Closing a side line is unchanged**: two iterations of work in a row without a promotion. With parallel runs, an iteration of work for a line is an integration that had a candidate of that line. One run per side line at a time keeps that count meaningful.
- **What would show it was wrong.** Check after ten integrations with four side lines. If more than half of the side lines are closed without having promoted anything, or the champion's points against the references stopped rising, go back to two. The ledger's entry for the change says to check this.
