# Island Battles RSI bot: the bot league

The league is where Island Battles bots are **written and improved by AI agents alone**. A population of Python bots, each a `play(turn)` function on the [Python SDK](https://github.com/INTODAN/island-battles-go/blob/main/clients/island-battles-python/README.md), plays round robins in the [headless runner](https://github.com/INTODAN/island-battles-go/blob/main/backend/README.md#headless-matches). An agent studies the games and the bots' logs, changes the bots, and keeps a change only when the next tournament says it is better. The best bot of the league is its **champion**, the bot this work is for.

People change the tools, the maps and the rules of the loop. **Only agents change `bots/`.**

## Layout

| Path | What it is |
|---|---|
| `bots/<name>/bot.py` | A bot: `play(turn)`. Its directory is a package of its own and imports nothing from another bot. |
| `bots/<name>/bot.toml` | The bot's status (`candidate`, `active`, `retired` or `sparring`), its parent, the iteration that made it and its idea in a sentence. |
| `maps/train/` | The maps whose games an agent may study. `claw` is the official game's default map, rebuilt from the first board of a real game. |
| `maps/holdout/` | The maps that only give numbers: nobody reads their games, so a bot can't be fitted to them. |
| `league_tools/` | The `league` command: tournaments, ratings, the game digest, the roster and the map maker. |
| `ledger/iterations.md` | What every iteration tried, measured, kept and learned. The league's memory between sessions. |
| `opponents.local.toml` (not in git) | Outside opponents: real players' bots that play every tournament from their own projects ([`league_tools/opponents.py`](league_tools/opponents.py)). |
| `scripts/serve_maps.py`, `scripts/lobby-run.js` | Play a bot against a hosted bot in lobby games on the league's maps, several tabs at once: the check against real opponents. |
| `tests/`, `scripts/check.sh` | The checks every bot and tool passes before it plays. |
| `runs/` (not in git) | Results, the result cache and the demos of every match played here. |
| `runner.toml` | The commit of the game that the league plays. |
| `.runner/` (not in git) | The game's source at that commit, and the runner built from it. |
| `.agents/skills/` | The procedures an agent follows here: the league's two, and the game's rules. |

## How a game is played

`league tournament` plays every pair of players on every chosen map **from both sides**, in one run of the game's headless runner (`backend/cmd/headless-match` of [INTODAN/island-battles-go](https://github.com/INTODAN/island-battles-go)). That command plays whole games in memory with the server's own rules: the same turn (`BotTurn`), the same command checks as `POST /generation/commands`, the same simulation and end rule, and no database, lobby or network. Each bot runs in the SDK's worker (`python -m island_battles_client.worker bots.<name>.bot:play`), as an uploaded bot does on the server. The default bots, levels 1 to 3, play in the runner itself as `level1`, `level2` and `level3`.

A headless game differs from a lobby's in what it leaves out: no turn deadline (a bot that fails or takes over 2 seconds passes the turn, and the result counts it), no real-time turns, nobody leaves. The backend README's [Headless matches](https://github.com/INTODAN/island-battles-go/blob/main/backend/README.md#headless-matches) has the details.

**Speed.** On a 32-thread desktop, the 504 matches of the whole league (4 bots and the 3 default bots, 14 maps, both sides, 123 turns a game on average) take 5 seconds; a league bot's turn costs about 1 ms, the SDK's reading of the turn included. Bots are deterministic, so a match is decided by the runner's build, the map, the two bots' code, the SDK and the settings. `league tournament` keys its cache on those and on the players' names, and **doesn't play the same match twice**: after a change to one bot, only that bot's matches are played. The runner is built without the commit's stamp, so moving the pin to a commit that leaves the backend alone keeps the cache. A result with a failed turn is never kept, since a turn can time out because the machine was busy: it is played again next time. The timings in a cached result are those of the run that played it; `--no-cache` plays everything again.

**Every match leaves a demo** in `runs/cache/`, the file **Save demo** writes, with both bots' log lines for every turn. `league digest` prints it as text (any demo, a real game's **Save demo** file too), and `league unpack` unpacks it for the demo viewer (`/game/demo-viewer/` of a running backend).

## The game is somewhere else

This repository holds bots and the tools that measure them. The game, its rules, its SDK and the headless runner are [INTODAN/island-battles-go](https://github.com/INTODAN/island-battles-go), and nothing here changes them.

- **`runner.toml` pins the game**: the runner is built from that commit, so every rating in the ledger belongs to that commit's rules. Moving the pin is a change of its own: play both sets of maps again and record the standings before the next iteration, and copy the rules skills again from the template at the new commit.
- **The SDK comes from PyPI** (`island-battles-python`, the version in `uv.lock`), as it does for any player's bot.
- **To try a runner or a rule that isn't merged yet**, set `ISLAND_BATTLES_GO` to a checkout of the game: the runner is then built from there.
- **Something the league needs from the game** (a faster runner, a new option, a map's file) is an issue in the game's repository, and is done there.

## Ratings

A tournament's ratings are a Bradley-Terry fit of its games, shown on the Elo scale, with **`level3` fixed at 1000**. The default bots never change, so a rating means the same in every iteration, and the champion's rating over the iterations is the league's progress. A fit doesn't depend on the order of the games.

A rating says something only when the player met the whole field. `tournament --focus NAME` plays NAME's pairs alone: use it to find NAME's lost games quickly, never to compare ratings. `tournament --add NAME` adds NAME to the whole round robin, which costs the same thanks to the cache, and its ratings count.

Deterministic bots give one game per pair, map and side, so the number of maps is the sample size. More maps make a rating mean more; `league new-map` makes fair ones from a seed.

## The loop

One **iteration** is one pass, and ends as one commit. The [bot-league-iteration skill](.agents/skills/bot-league-iteration/SKILL.md) is the procedure; in short:

1. **Measure.** Play the population and the default bots on the training maps. Most of it comes from the cache.
2. **Study.** Take the champion's lost and drawn games, and its slow wins, on the training maps. Read the digest, then the turns that decided the game with both bots' logs. Write each finding as: what happened (map, turn), why, and the change that would fix it.
3. **Vary.** One candidate per idea: `league new` copies a parent, and the agent changes only that directory. Three kinds of ideas: a **fix** of something a game showed, a **graft** of a mechanism another bot has, and, when two iterations promoted nothing, a new **founder** with a different strategy.
4. **Gate.** `scripts/check.sh` passes, no failed turn, no turn slower than 200 ms.
5. **Select.** In a round robin of the whole population with the candidates added, a candidate is promoted when it beats its parent head to head, rates higher than it on the training maps, and doesn't rate lower than it on the holdout maps. A rejected candidate is deleted; the ledger keeps what it tried and its numbers.
6. **Record.** The standings, the ideas, the decisions and what was learned about the game go in `ledger/iterations.md`.

What keeps the loop honest:

- **Holdout maps** catch a bot that learned the training maps instead of the game. Their games are never read.
- **The default bots, the retired and sparring bots and the outside opponents stay in every tournament**, so a new bot must still beat the old ones, and a strategy that only beats the current champion doesn't win.
- **One idea per candidate**, so a result says something about the idea.
- **The population stays varied**: at most six active bots, and a bot is retired only when another does everything it does better.

## Rules for a bot

Three skills in [`.agents/skills/`](.agents/skills/), copied from the game's [Python bot template](https://github.com/INTODAN/island-battles-go/tree/main/templates/python-bot), describe the game's rules and how a bot is written; they apply here unchanged. On top of them, `tests/test_bots.py` checks for every bot:

- **Self-contained**: it imports only the SDK, a short list of pure standard modules (`math`, `dataclasses`, `collections`, `itertools`, `functools`, `heapq`, `bisect`, `enum`, `operator`, `typing`) and its own package.
- **Pure**: no globals, no value at module or class level that a turn could change, no clock, randomness, file or network. The same turn gives the same result.
- **It logs every turn** what it decided and why, in a line or two. A game whose bots say nothing can't be studied.
- **Every result is one the server accepts**, on six boards (the SDK's fixture, under attack, with burst debt and top levels, with empty castles, without enemy castles and without castles) and on 300 boards made from seeds.
- **Its memory stays small** over a run of turns.

The tests don't measure speed. The tournament does: its **Slowest turn** column should stay well under 200 ms; a real-time game gives a bot one second.

## Commands

Run them from the repository root. They need [uv](https://docs.astral.sh/uv/), Go 1.25 or newer and git: `uv run` installs the Python side, and the first tournament fetches the game's source and builds the runner.

```sh
uv run league roster
uv run league tournament                    # the population and levels 1-3 on the training maps
uv run league tournament --focus NAME       # only NAME's matches: its lost games and longest wins
uv run league tournament --add NAME         # NAME, a candidate too, in the whole round robin
uv run league tournament --maps holdout     # or: all, or map names
uv run league digest DEMO                   # the timeline, the logistics and the events of a game
uv run league digest DEMO --turns 40-55     # those turns whole, with both bots' logs
uv run league new NAME --parent PARENT --iteration N --idea "..."
uv run league status NAME active            # or: candidate, retired, sparring
uv run league new-map NAME --seed N --set train
uv run league unpack DEMO                   # a plain .json for the demo viewer
scripts/check.sh                                      # format, lint, types and tests
```

`tournament --strict` exits with status 1 when a match wasn't played, a player failed a turn or there was no match; the pull request checks run it on one map.

## What is not here yet

- **The champion plays nowhere but here.** Shipping it means `island-battles-bot package` and an upload, a hosted bot, or a rated bot name on the leaderboard. Before that it must play real lobby games with `island-battles-bot run`, where turns have deadlines and a network.
- **Two teams only.** The runner plays any number of teams; the tournament pairs two.
- **Official maps come by hand.** The game lists its default maps but doesn't serve their map files (INTODAN/island-battles-go#390). `claw` was rebuilt from a saved demo's first board; a new default map needs the same.
- **Real opponents only by proxy.** A player's bot plays every tournament as an outside opponent, and `ori_like`, a sparring bot, plays like the hosted bot of the real games; the hosted bot itself is met only in lobby games, by the check before a promotion, until the game's runner can play hosted bots (INTODAN/island-battles-go#407).
