---
name: measuring-time
description: "Measure where the time of any work here goes (a league iteration, a tournament, a tool change, an Actions run of the real-game iteration) and end it with a review of how to make the next one faster. Load it at the start of an iteration or any long task in this repository, before timing a step, when reading an Actions run's times, and when asked why something is slow or how to speed it up."
---

# Measuring time

The league exists to make the bots better faster, so the time from a real game to a better deployed bot is one of its numbers, like a rating. Every piece of work here measures its time, and **ends with a review of how to make the next one faster**: an iteration in its ledger entry and report, an Actions run in its summary, any other task in its report. Never by doing less of the work: the same games read, the same checks, the same gate.

## What to measure

Time everything that takes more than a few seconds, from its start to its end, and keep the numbers you were given rather than estimates.

- **Your steps: `league clock`.** It is a `league` command, so the automated iteration's Claude, which may run nothing else, can use it too.

  ```sh
  uv run league clock reset                 # once, before the work's first step
  uv run league clock start "2 study"       # at a step's start
  uv run league clock stop "2 study"        # at its end
  uv run league clock report                # every step: start, end, minutes, share, the slowest, the open ones
  ```

  Name the steps as the work's own steps are named (an iteration's `0 ledger`, `1 measure`, ... `7 report`), and add the commands inside them that take longer than a minute (`3 vary: rematch feedkeep_x`, `4 gate: head-to-head`). A step can be started again after it stopped; the report counts it again. The clock is `runs/clock.jsonl`, outside the repository's files; `--file` names another. Start each piece of work with `league clock reset`, or the report's total runs from the last one's first step.

- **Tournaments time themselves.** Each prints, on its standard error, `Time:` lines: how long it waited for another tournament, how many matches it played and how fast, and its whole time split into finding and playing its matches and everything after (ratings, tables, files). Copy them; don't time a tournament by hand.

- **Subagents.** Note when you start them and when the last one reports: their time is the longest one's, not the sum. Ask each for its own start and end in its report.

- **An Actions run: `hosting/rsi/run_times.py RUN_ID`.** Each job's wait in the queue and its minutes; each round of runners (`Warm K/N`, `Gate K/N`) as its slowest, median and fastest runner, since a round lasts as long as its slowest; every step of a minute or more; and the run's whole time. The real-game iteration writes it to the summary of every run, failed ones too, and gives it to its second half as `runs/rsi/times.txt`. Each Claude step's log also says its turns and minutes, and which tools it called how many times.

## Where time goes

Put every minute of the total in one of these, since each has a different cure:

| Kind | Looks like | Who can make it faster |
| --- | --- | --- |
| **Playing** | tournaments' `played N matches in S s`; a round of runners | the work itself (fewer matches played twice, the cache reused), a tool (`league_tools/`), more runners (`RSI_SHARDS`), the game's runner (an issue in INTODAN/island-battles-go) |
| **Waiting to play** | `waited S s for another tournament`; subagents' head-to-heads one after the other on one machine | the work's order (start what doesn't need the machine meanwhile), another machine |
| **Thinking** | a Claude step's minutes beyond the games it played; reading, writing candidates and the ledger | parallel subagents, briefer reading (`league ledger`, not the whole file), a smaller model where a skill allows one |
| **Setup** | checkout, uv, Go, the cache's download: the minute every runner spends before it plays | the workflow (fewer jobs, caches), not the iteration |
| **Queue and waits** | a job's "Queued" minutes; the claim waiting for another iteration | the workflow, or a person's scheduling |
| **Failure** | a job or a step run again, a run that failed and started over | the cause's fix: a failed run is the most expensive time there is |

A step's time is only as interesting as its share of the total: the review starts at the largest share, not the step that is easiest to change.

## The review: how to make the next one faster

At the end of every iteration, and of every other long task, before its report:

1. **The numbers.** `league clock report` (and `run_times.py` for an Actions run): the total, each step's minutes and share, the three slowest, and the total of the last comparable piece of work (the ledger's last entry's **Time**), with the difference.
2. **Where it went.** The total split into the kinds above, in minutes. Say which numbers were measured and which estimated; a step nobody measured is a finding, and the next one measures it.
3. **Why the slowest were slow.** For each of the slowest steps, what in it took the time, from its own output: matches played rather than cached (and why the cache missed), a round's slowest runner against its median, subagents that waited for each other, a run that failed and started over.
4. **What to change**, each with the minutes it should save, sorted by who can do it:
   - **The next iteration** (an order of steps, a command not run twice, a cache linked first): goes in the ledger entry, and the next iteration does it.
   - **A tool or the workflow** (`league_tools/`, `scripts/`, `hosting/rsi/`, `.github/`): a separate change after the iteration, never inside it, measured before and after with the same work; say what it is in the report.
   - **The game or its runner**: an issue in INTODAN/island-battles-go, as AGENTS.md says.
   - **A setting a person controls** (`RSI_SHARDS`, `RSI_MODEL`, `RSI_GAMES_PER_RUN`, the plan's runners): a proposal, with its evidence.
5. **What last time's review proposed**, and whether it was done and saved what it said. A proposal not done is raised again, with how many runs it has stood.

Write it even when nothing is slow: "52 minutes, 20 of them the gate's slowest runner; nothing proposed" is a review. In the ledger it is the entry's **Time** paragraph; in a report, its time line.
