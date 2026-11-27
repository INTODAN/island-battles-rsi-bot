# How deterministic is an agent's game analysis?

A study of 2026-11-27. The league's iterations lean on agents that read a game and name the bots' mistakes. This study asks two questions:

- How much does that reading change when the same game is analyzed again, by the same model or by another one?
- Across many games, do the bots repeat the same mistakes, or do the analyses find a wide variety?

## Setup

- **Bots**:
  - `jug_fix`: the juggernaut of branch `claude/champion-mistake-correction-791867`, the strongest of the three juggernauts.
  - `rival_mimic`: the stand-in for a hosted rival, commit 848df8a on branch `claude/gibor-champion-mistakes-bdbdc1`.
  - In a full tournament (82 maps, both sides), `jug_fix` went 53 W, 42 D, 69 L against `rival_mimic`.
- **Games**: 60 of that tournament's games, 20 that `jug_fix` won, 20 draws and 20 that it lost, each outcome on 20 different maps ([games.json](games.json)).
- **What an analyst saw**: the game's `league digest`, a timeline, logistics and events, with no bot logs ([digests/](digests/)). Each analyst received 10 games in one batch, together with the rules.
- **Task**: for each game, the top 3 mistakes of each bot, ranked by cost, each with a title, turns, castles and a short description.
- **Model setups**: Opus 5.5 at the default effort, Opus 5.5 at medium, Sonnet 5.5 at high, Fable 5.2 at medium.
- **Repeats**: each setup analyzed every game 10 times from scratch.
- **Totals**: 2,400 game analyses and 14,400 mistakes ([mistakes.jsonl.gz](mistakes.jsonl.gz), one JSON line per mistake).
- **Kinds**:
  - To compare free text, one agent built a list of 19 mistake kinds from a random sample of 700 mistakes ([taxonomy.json](taxonomy.json)).
  - Agents at low effort then sorted every mistake into one kind; the result is the `kind` field.
  - The sorting is itself one more source of noise, so the agreement below is a lower bound.

## How deterministic the analyses are

Every pair of analyses of the same game and bot was compared in three ways:

- **Kind overlap**: the Jaccard overlap of the two sets of top-3 kinds.
- **Same #1**: how often both analyses rank the same kind first.
- **Same mistake**: the share of one analysis's mistakes that the other also found, counted as the same kind with turns within 10 of each other.

| Pair | Kind overlap | Same #1 | Same mistake |
|---|---|---|---|
| Opus default vs itself | 0.62 | 66% | 72% |
| Opus medium vs itself | 0.63 | 67% | 73% |
| Fable medium vs itself | 0.64 | 64% | 74% |
| Sonnet high vs itself | 0.58 | 58% | 68% |
| Opus default vs Opus medium | 0.62 | 66% | 72% |
| Opus vs Sonnet, Opus vs Fable | 0.53 | 55–59% | 64–65% |
| Sonnet vs Fable | 0.49 | 54% | 61% |
| Baseline: same model, different games | 0.17 | 13% | – |

What the table shows:

- **Same model, run again: about 60% the same.** Two runs usually share 2 of the 3 kinds.
- **The third mistake varies most.** Over 10 runs, one game and bot gets about 5.5 different kinds (6.1 for Sonnet).
- **Effort doesn't matter for Opus.** Opus at medium and at the default effort agree as much as Opus agrees with itself.
- **Different models agree 10 to 15 points less.** Sonnet is the noisiest. Fable stresses the rival's late production upgrades more than the others.
- **The readings come from the games themselves.** Agreement on the same game is far above the baseline of two different games.
- **`jug_fix` reads more consistently than `rival_mimic`**: a kind overlap of 0.65 against 0.59 for Opus default.
- **"Same mistake" is a loose match.** Whole-game patterns such as "passive all game" match easily.

**Practical rule**: a mistake that several independent runs agree on is reliable; one run's third mistake is close to chance. An iteration that acts on a game's analysis should run it at least 3 times and keep what recurs.

## Do the bots repeat their mistakes?

Mostly they do: a few patterns repeat, and a long tail follows.

- **Each bot's range**: each bot used all 19 kinds, but its top 6 kinds hold most of its mistakes (about 14 effective kinds by entropy).
- **Consensus mistakes**: a kind is a consensus mistake of a game when at least half of the 40 analyses name it. Each game has about 2.5 of them per bot.

The counts below are games out of 60 in which the kind was a consensus mistake.

**`jug_fix`**:

| Mistake | Games | Where it shows up |
|---|---|---|
| A big idle stockpile while tied or behind on castles | 28 | Most of the draws |
| Slow expansion, losing the race for neutral castles | 25 | |
| Sends that strip its own castles, which are then taken cheaply | 18 | The main pattern in its losses |
| Captures held too thin and lost back | 14 | |
| A won game finished late, after long stockpiling | 13 | The main pattern in its wins |
| Soldiers looping between its own castles | 10 | |
| Speed upgrades that nothing used | 10 | |

**`rival_mimic`**:

| Mistake | Games | Where it shows up |
|---|---|---|
| Passive with a stockpile | 25 | |
| Slow expansion | 21 | |
| Large idle stacks while its castles fall one by one | 17 | The main pattern in the games it lost |
| Production upgrades late or never | 13 | |
| A lead never pressed to elimination | 13 | The main pattern in the games it won |

Both bots share the two largest kinds: passivity up to the turn limit, and slow expansion. Each has its own on top:

- `jug_fix` overextends: its castles are emptied by its own sends.
- `rival_mimic` defends passively and doesn't convert a lead.

The full numbers, including the mistake shares by outcome, are in [metrics.txt](metrics.txt). In that file, `win`, `draw` and `loss` are always from `jug_fix`'s side.
