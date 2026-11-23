# Island Battles RSI bot: the bot league

The league is where Island Battles bots are **written and improved by AI agents alone**. A population of Go bots, each a program whose `play` function plays one turn on the game's [Go SDK](https://github.com/INTODAN/island-battles-go/blob/main/clients/island-battles-go/README.md), plays round robins in the [headless runner](https://github.com/INTODAN/island-battles-go/blob/main/backend/README.md#headless-matches). An agent studies the games and the bots' logs, changes the bots, and keeps a change only when the next tournament says it is better. The best bot of the league is its **champion**, the bot this work is for.

People change the tools, the maps and the rules of the loop. **Only agents change `bots/`.**

## Layout

| Path | What it is |
|---|---|
| `bots/<name>/main.go` | A bot: a Go program, `package main`, whose `play` plays one turn and whose `main` is `islandbattles.Main(play)`. Its directory is a package of its own (more `.go` files may sit beside `main.go`) and imports nothing from another bot. |
| `bots/<name>/bot.toml` | The bot's status (`candidate`, `active`, `retired` or `sparring`), its parent, the iteration that made it and its idea in a sentence. |
| `maps/train/` | The maps whose games an agent may study. `claw` is the official game's default map, rebuilt from the first board of a real game. |
| `maps/holdout/` | The maps that only give numbers: nobody reads their games, so a bot can't be fitted to them. |
| `go.mod`, `go.sum` | The one Go module of every bot, which pins the game's Go SDK. |
| `league_tools/` | The `league` command (Python): tournaments, ratings, the game digest, the roster and the map maker. |
| `ledger/iterations.md` | What every iteration tried, measured, kept and learned. The league's memory between sessions. |
| `ledger/real-games.txt` | The ids of the hosted bot's real games that an iteration has studied. |
| `opponents.local.toml` (not in git) | Outside opponents: real players' bots that play every tournament from their own projects ([`league_tools/opponents.py`](league_tools/opponents.py)). |
| `scripts/serve_maps.py`, `scripts/lobby-run.js` | Play a bot against a hosted bot in lobby games on the league's maps, several tabs at once, when a person asks for it. An iteration never plays another player's bot. |
| `hosting/rsi/`, `.github/workflows/real-game-iteration.yml`, `.github/actions/` | The automated iteration: each real game the hosted bot finishes starts an iteration that studies it and merges itself, its tournaments played on several runners at once ([hosting/rsi/README.md](hosting/rsi/README.md)). |
| `tests/`, `scripts/check.sh` | The checks every bot and tool passes before it plays: `tests/bots/` are the bots' (Go), the rest the tools' (Python). |
| `runs/` (not in git) | Results, the result cache and the demos of every match played here, and the bots' binaries (`runs/bin/`). A git worktree's tournaments use the main checkout's `runs/cache/`, `runs/bin/` and `.runner/`. |
| `runner.toml` | The commit of the game that the league plays. |
| `.runner/` (not in git) | The game's source at that commit, and the runner built from it. |
| `.agents/skills/` | The procedures an agent follows here: the league's two, and the game's rules. |

## How a game is played

`league tournament` plays every pair of players on every chosen map **from both sides**, in one run of the game's headless runner (`backend/cmd/headless-match` of [INTODAN/island-battles-go](https://github.com/INTODAN/island-battles-go)). That command plays whole games in memory with the server's own rules: the same turn (`BotTurn`), the same command checks as `POST /generation/commands`, the same simulation and end rule, and no database, lobby or network. Each bot is built once per tournament, and not again while its code is the same (`runs/bin/<name>-<hash>`), and plays as the Go SDK's worker (`<binary> worker`), the program an uploaded bot's package runs on the server. The default bots, levels 1 to 3, play in the runner itself as `level1`, `level2` and `level3`.

A headless game differs from a lobby's in what it leaves out: no turn deadline (a bot that fails or takes over 2 seconds passes the turn, and the result counts it), no real-time turns, nobody leaves. The backend README's [Headless matches](https://github.com/INTODAN/island-battles-go/blob/main/backend/README.md#headless-matches) has the details.

**Speed.** On a 32-thread desktop, the 504 matches of the whole league (4 bots and the 3 default bots, 14 maps, both sides, 123 turns a game on average) took 5 seconds with the Python bots the league had then. A Go bot's turn costs about 0.5 ms in its worker, the SDK's reading and writing included, and about 1.3 ms as the runner measures it, three times less than the Python bots' (the ledger's setup after iteration 36). Bots are deterministic, so a match is decided by the runner's build, the map, the two bots' Go code, the Go SDK's version and the settings. `league tournament` keys its cache on those and on the players' names, and **doesn't play the same match twice**: after a change to one bot, only that bot's matches are played. Every checkout of the repository shares one cache and one runner, the main checkout's (`LEAGUE_SHARED` names another directory), so a new worktree's first tournament doesn't play the league again: from a cold cache the 5,700 matches of the training maps take about 4 minutes on a 6-core desktop (12 with the Python bots), and more on a machine with fewer cores. One tournament plays at a time on the machine, whichever checkout it runs from: another waits, then takes from the cache what the first played. Several at once only made every turn slower (18 matches at once on 12 hardware threads took an eighth longer than 12), and a turn that runs out of time fails and is played again. The runner is built without the commit's stamp, so moving the pin to a commit that leaves the backend alone keeps the cache. Since a match's key decides it, machines can share a tournament: `--shard K/N` plays the K-th of N slices, and their caches merged hold the whole of it, which is how the automated iteration plays on several GitHub runners at once. A result with a failed turn is never kept, since a turn can time out because the machine was busy: it is played again next time. The timings in a cached result are those of the run that played it; `--no-cache` plays everything again.

**Every match leaves a demo** in `runs/cache/`, the file **Save demo** writes, with both bots' log lines for every turn. `league digest` prints it as text (any demo, a real game's **Save demo** file too), `league replay` replays a team's turns in demos through a bot and counts where the bot makes the team's commands (the tool for building a sparring bot from lobby games), and `league unpack` unpacks it for the demo viewer (`/game/demo-viewer/` of a running backend).

## The game is somewhere else

This repository holds bots and the tools that measure them. The game, its rules, its SDK and the headless runner are [INTODAN/island-battles-go](https://github.com/INTODAN/island-battles-go), and nothing here changes them.

- **`runner.toml` pins the game**: the runner is built from that commit, so every rating in the ledger belongs to that commit's rules. Moving the pin is a change of its own: play both sets of maps again and record the standings before the next iteration, and copy the rules skills again from the template at the new commit.
- **The bots' SDK is the game's Go module** (`github.com/INTODAN/island-battles-go/clients/island-battles-go`, the version `go.mod` requires), as for any player's Go bot. Moving it is a change of the setup like moving the pin. The tools are Python and read turns and demos with the Python SDK from PyPI (`island-battles-python` in `uv.lock`); so do outside opponents and the hosted bot's handler.
- **To try a runner or a rule that isn't merged yet**, set `ISLAND_BATTLES_GO` to a checkout of the game: the runner is then built from there.
- **Something the league needs from the game** (a faster runner, a new option, a map's file) is an issue in the game's repository, and is done there.

## Ratings

A tournament's ratings are a Bradley-Terry fit of its games, shown on the Elo scale, with **the sparring bot `ori_mimic` fixed at 1800**. `ori_mimic` is never changed and never deleted, so a rating means the same in every iteration, and the champion's rating over the iterations is the league's progress. A fit doesn't depend on the order of the games.

The anchor has to win and lose games in the table. The fit gives every player one drawn game against an average player besides its real ones, so a player that wins nothing sits where that one draw puts it, not where its games do. Until iteration 29 the anchor was `level3` at 1000; from iteration 30 the population rules had deleted every bot it beat, and in the training tables `level2` and `level3` won nothing, both printed 1000, and every rating rose about 370 points. `ori_mimic` scores about half its games against the whole field. 1800 is about its rating in the tables of iterations 24 to 29, so the training ratings go on from those; the holdout ratings, where it stood at 1943 to 2101, read about 200 to 300 lower than in those iterations. The ratings of iterations 30 to 35 compare within their tables only. A tournament without `ori_mimic` has `level3` at 1000, and one without either has its mean at 1000.

Changing `ori_mimic`'s code would move the scale: a sparring bot that plays more like the opponent is a new bot with a new name. When `ori_mimic`'s score in the whole population's tables falls toward 0.1, the anchor needs to move again, a change of the league's setup like this one.

A rating says something only when the player met the whole field. `tournament --focus NAME` plays NAME's pairs alone: use it to find NAME's lost games quickly, never to compare ratings. `tournament --add NAME` adds NAME to the whole round robin, which costs the same thanks to the cache, and its ratings count.

Deterministic bots give one game per pair, map and side, so the number of maps is the sample size. More maps make a rating mean more; `league new-map` makes fair ones from a seed.

## The loop

One **iteration** is one pass, and ends as one commit. The [bot-league-iteration skill](.agents/skills/bot-league-iteration/SKILL.md) is the procedure; in short:

0. **Claim.** Iterations run one at a time, each from the last one's ledger entry. `scripts/claim-iteration.sh claim` pushes the branch `claude/league-iteration-N` before anything else, and fails when another session or the automated iteration holds N; `scripts/claim-iteration.sh status` says who does. The iteration's commit replaces the claim on that branch, and the number is free again once it has merged.

1. **Measure.** Play the population and the default bots on the training maps. Most of it comes from the cache.
2. **Study.** Take the champion's lost and drawn games, and its slow wins, on the training maps. Read the digest, then the turns that decided the game with both bots' logs. Write each finding as: what happened (map, turn), why, and the change that would fix it.
3. **Vary.** One candidate per idea: `league new` copies a parent, and the agent changes only that directory. Three kinds of ideas: a **fix** of something a game showed, a **graft** of a mechanism another bot has, and, when two iterations promoted nothing, a new **founder** with a different strategy.
4. **Gate.** `scripts/check.sh` passes, no failed turn, no turn slower than 200 ms.
5. **Select.** In a round robin of the whole population with the candidates added, a candidate is promoted when it beats its parent head to head, rates higher than it on the training maps, and doesn't rate lower than it on the holdout maps. A rejected candidate is deleted; the ledger keeps what it tried and its numbers.
6. **Record.** The standings, the ideas, the decisions and what was learned about the game go in `ledger/iterations.md`, with a review of the league itself: whether its field, maps and rules can still tell a strong bot, and what would fix them when they can't.

What keeps the loop honest:

- **Holdout maps** catch a bot that learned the training maps instead of the game. Their games are never read.
- **The default bots, the retired and sparring bots and the outside opponents stay in every tournament**, so a new bot must still beat the old ones, and a strategy that only beats the current champion doesn't win.
- **One idea per candidate**, so a result says something about the idea.
- **The population stays varied**: at most six active bots, and a bot is retired only when another does everything it does better.

## Rules for a bot

Three skills in [`.agents/skills/`](.agents/skills/), copied from the game's [Python bot template](https://github.com/INTODAN/island-battles-go/tree/main/templates/python-bot), describe the game's rules and how a bot is written; the rules apply here unchanged, and the SDK's names have the same meaning in Go (the Go SDK's README has [a table of both](https://github.com/INTODAN/island-battles-go/blob/main/clients/island-battles-go/README.md#python-names-and-go-names)). The game has no Go bot template yet. On top of them, the Go tests in `tests/bots/` build every bot, play its turns through its worker as a tournament does, and check:

- **Self-contained**: its directory holds `bot.toml` and Go files of one package, and imports only the SDK and a short list of pure standard packages (`cmp`, `container/heap`, `container/list`, `context`, `encoding/json`, `errors`, `fmt`, `iter`, `math`, `math/bits`, `slices`, `sort`, `strconv`, `strings`, `unicode`, `unicode/utf8`); nothing from another bot.
- **Pure**: no package-level variable, no `init`, no goroutine, no clock, randomness, file or network. The same turn gives the same result, however many turns the process played before. A Go map is walked in a new order every time: a bot never lets that order choose (sort the keys first).
- **It logs every turn** what it decided and why, in a line or two. A game whose bots say nothing can't be studied.
- **Every result is one the server accepts**, on six boards (the SDK's fixture, under attack, with burst debt and top levels, with empty castles, without enemy castles and without castles) and on 300 boards made from seeds.
- **Its memory stays small** over a run of turns.

The tests don't measure speed. The tournament does: its **Slowest turn** column should stay well under 200 ms; a real-time game gives a bot one second.

The bots were Python until the setup after iteration 36, and were ported to Go to play exactly as before (the ledger has the check). That is why they measure distances with `hypot`, a copy of CPython's `math.hypot`: Go's `math.Hypot` differs from it in the last bit on about a third of the boards' distances, enough to round a walk to another turn now and then. A new bot may use either; switching an existing bot is a change like any other, measured by a tournament.

## Commands

Run them from the repository root. They need [uv](https://docs.astral.sh/uv/), Go 1.25 or newer and git: `uv run` installs the tools, Go fetches the SDK that `go.mod` pins and builds the bots, and the first tournament fetches the game's source and builds the runner.

```sh
uv run league roster
uv run league tournament                    # the population and levels 1-3 on the training maps
uv run league tournament --focus NAME       # only NAME's matches: its lost games and longest wins
uv run league tournament --add NAME         # NAME, a candidate too, in the whole round robin
uv run league tournament --focus NAME --parents   # only NAME against its parent: the head-to-head rule
uv run league ledger                        # the lessons, every candidate tried, the last three entries
uv run league tournament --maps holdout     # or: all, or map names
uv run league tournament --shard 2/8        # a slice of the matches into the cache, no standings: for 8 machines
uv run league digest DEMO                   # the timeline, the logistics and the events of a game (a hosted game's zip too)
uv run league digest DEMO --turns 40-55     # those turns whole, with both bots' logs
uv run league new NAME --parent PARENT --iteration N --idea "..."
uv run league rematch DEMO... --bot NAME       # those games again with NAME in its parent's seat: did the change act?
uv run league status NAME active            # or: candidate, retired, sparring
uv run league new-map NAME --seed N --set train
uv run league replay DEMO... --bot NAME --team 2   # how closely a bot repeats a team's commands: for a sparring bot
uv run league unpack DEMO                   # a plain .json for the demo viewer
gofmt -w bots/NAME                          # format a bot's Go code, as the checks want it
scripts/check.sh                            # format, lint, types and tests of the tools and the bots
```

`tournament --strict` exits with status 1 when a match wasn't played, a player failed a turn or there was no match; the pull request checks run it on one map.

## What is not here yet

- **The champion plays nowhere but here.** Shipping it means `island-battles-bot package` and an upload, a hosted bot, or a rated bot name on the leaderboard. Before that it must play real lobby games with `island-battles-bot run`, where turns have deadlines and a network.
- **No Go bot template in the game.** The rules skills come from the game's Python template, whose examples are Python; the `bot-league` skill maps them to the Go SDK. A Go template with its own skills would replace that.
- **Two teams only.** The runner plays any number of teams; the tournament pairs two.
- **Official maps come by hand.** The game lists its default maps but doesn't serve their map files (INTODAN/island-battles-go#390). `claw` was rebuilt from a saved demo's first board; a new default map needs the same.
- **Real opponents only by proxy.** A player's bot plays every tournament as an outside opponent, and two sparring bots play like the hosted bot of the real games (`ori_mimic`, built from its commands in lobby demos, makes its exact commands on 75% of its turns; `ori_like` is an older, rougher stand-in). The league doesn't play that hosted bot itself: every game against it is one its owner can learn from too. The game's runner can't play hosted bots yet anyway (INTODAN/island-battles-go#407).
- **Real games are studied one iteration at a time.** The hosted bot keeps every real game it plays as a zip with the game's own demo ([hosting/lambda/README.md](hosting/lambda/README.md#its-games)), and each one starts an automated iteration that studies it ([hosting/rsi/README.md](hosting/rsi/README.md)). Its pull request merges itself when the checks pass, so a bot can reach main and the hosted bot without a person reading it.
