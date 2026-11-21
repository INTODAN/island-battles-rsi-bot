# Agent guide

This repository is a **bot league** for the game Island Battles: Python bots that only AI agents write and improve, and the tools that play them against each other and measure them. [README.md](README.md) is the design; read it first.

The game is a separate project, [INTODAN/island-battles-go](https://github.com/INTODAN/island-battles-go). This repository is a player of that game, as any person's bot project is, and holds none of its code.

## What to do when asked

- **"Run a league iteration"**, "improve the bots", "do RSI": follow the [`bot-league-iteration`](.agents/skills/bot-league-iteration/SKILL.md) skill from start to end. The request needs to say nothing more.
- **Anything else here** (a tool, a map, a test, reading results): read the [`bot-league`](.agents/skills/bot-league/SKILL.md) skill first.
- **Writing or changing a bot's code**: also [`island-battles-rules`](.agents/skills/island-battles-rules/SKILL.md), [`writing-a-bot`](.agents/skills/writing-a-bot/SKILL.md) and [`bot-logging`](.agents/skills/bot-logging/SKILL.md).

## Rules

- **Only an iteration changes `bots/`.** A change to a bot that no tournament measured doesn't go in.
- **Nothing here changes the game.** When the league needs something from the game or its headless runner (speed, an option, a map's file, a bug), don't work around it here: open an issue in INTODAN/island-battles-go that says what the league needs and why, and do the work there, by that repository's own AGENTS.md. Then move `runner.toml` to the merged commit, as README.md's [The game is somewhere else](README.md#the-game-is-somewhere-else) describes.
- **The repository is public.** Never commit a secret. Never commit a real game's demo either: it carries players' names and their bots' logs. What a real game showed goes in the ledger, in words, without names.
- **Commit, push and open a pull request only as asked.** One iteration is one commit.
- Run `scripts/check.sh` before you say something is done. The pull request checks run it, and a tournament on one map.

## The copied skills

`island-battles-rules`, `writing-a-bot` and `bot-logging` are copies of the skills in the game's Python bot template (`templates/python-bot/.agents/skills/`), taken at the commit in `runner.toml`. They mention that template's scripts (`scripts/run.sh`, `island-battles-bot serve`), which this repository doesn't have: here a bot plays through `league tournament`. Don't edit the copies; when `runner.toml` moves to a commit that changed them, copy them again.
