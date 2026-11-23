---
name: league-breeding
description: "Why the bot league breeds its bots the way it does: what a review of its first 36 iterations measured, what the research on similar loops found (LLM-driven program evolution, league training of game agents, niching and quality-diversity, the statistics of game-engine testing), with sources, the rule each finding became, what was left out and what the tools don't measure yet. Load it before changing the rules of the loop, the population or the selection, or when a rule's reason matters. An iteration doesn't need it."
---

# How the league breeds, and why

The rules are in three skills, which an iteration follows: [`league-population`](../league-population/SKILL.md) (who is in the league), [`league-ideas`](../league-ideas/SKILL.md) (what an iteration tries) and [`league-evidence`](../league-evidence/SKILL.md) (what a result may decide). This one holds their reasons. It was written after iteration 36 from the ledger, a tournament of that population, and a search of the work on loops like this one. The numbers the sources give are quoted as they give them; a claim that could not be read in its source is left out.

## What the review measured

| What | The number | The rule it became |
|---|---|---|
| One parent | Every candidate of an iteration had the same parent in 35 of 36 iterations | The slate, and which bot a candidate starts from |
| One line | Every active bot shared 91% to 99% of its code with the champion | Side lines |
| Copies | 12 pairs of bots ended over half of their games the same to the soldier | One of two bots that play alike stays |
| A mirror for a measure | 71% of the champion's games, and 132.5 of the 141.5 points it lost, were against its own line and the sparring bot it began from; 88% of those games ran to the turn limit | Exploiters; the games to study; points against the references |
| Founders judged at birth | 10 of 14 deleted in their first iteration, three of them rated above their parent | Admission, and protection while a line improves |
| Selection inside the noise | 48 of 119 head-to-heads within a point of half; 4 of the 12 parent-to-child steps still in the league show no gain | The paired table |
| Games are not separate draws | `harrier_feedkeep` did better than its parent in 88 games and worse in 60, one chance in a hundred if games were independent. They came from 13 maps, of which five went the other way: one chance in four | The chance by luck, a map's games counted as one |
| A draw says who led | Of 2,429 drawn games between league bots, one side out-produced the other over the game in 936, and it was the higher-rated bot in 85% of them; the winner of a game decided at the turn limit is in 79%. The side with more soldiers at the end was the higher-rated in 46% | Two drawn games are told apart by the production lead |
| A worn holdout | Its maps were asked about 40 candidates | Two new holdout maps an iteration; three tries an idea |
| What the field can resolve | On 54 maps, with a map's games counted as one, four of the thirteen past promotions are beyond doubt and none of the other nine is below one chance in fourteen | Twenty maps added at once, and three every iteration; unresolved is not refuted; places that change more |
| Chosen on the maps it is measured on | `harrier_feedkeep` did better than its parent by 69 games on the 34 maps it was chosen on, and worse by 40 on twenty maps added afterwards | New maps every iteration; confirmed on holdout, clear on all |
| Small steps shrink | A promotion gained about 90 rating points in iterations 1 to 10, about 25 in 26 to 35 | Places that explore; the stalled line |
| The league's order is not the world's | Six candidates ranked by wins against a player's bot came out nearly the reverse of their league order (iteration 23) | The references guard |

## What similar work found

### Loops in which a language model writes the programs

| Finding | Source | Here |
|---|---|---|
| Always building on the best program is beaten by keeping every working one and choosing parents by score and by how few children each has had: 50.0% of tasks solved, against 39.7% from the best and 23.0% from the latest. The best lineage passed through two programs worse than their parents. | [Darwin Gödel Machine, 2025](https://arxiv.org/abs/2505.22954); the same weighting in [ShinkaEvolve, 2025](https://arxiv.org/abs/2509.19349) | A parent with three rejected children in a row is left; side lines live below the champion |
| Ten populations that never meet, the worse half wiped every few hours and restarted from a survivor's best: with one population the search found its target in 0 of 5 runs, with ten in 2 of 5. | [FunSearch, 2023](https://www.nature.com/articles/s41586-023-06924-6) | Lines; a line that stops improving is closed and its place refilled |
| A program evolved against one opponent is brittle. Evolved against its ten predecessors, cycles fell by 77% and generality rose. One specialist beat or tied 27.9% of human programs; the specialists together beat 89.1%. | [Digital Red Queen, 2026](https://arxiv.org/abs/2601.03335) | Fixed opponents kept without copies; no judging by the parent alone |
| A program revised up to ten times against its opponents' play scored 122.1 where a single draft scored 30.9. | [Code-Space Response Oracles, 2026](https://arxiv.org/abs/2603.10098); draft, then debug and improve in [AIDE, 2025](https://arxiv.org/abs/2502.13138) | The inner loop of founders and exploiters |
| With the same edit operators, greedy search, tree search and evolution did equally well: the operators were the limit. Choosing the final program on the data that selected it cost 9 to 13 points. | [AI research agents, 2025](https://arxiv.org/abs/2507.02554) | Five named kinds of candidate; confirmation on maps nobody studied |
| Distinct operators (a program unlike its parents, a parameter change, a simplification) and hints distilled from comparing a better program with a worse one both improved search. | [Evolution of Heuristics, 2024](https://arxiv.org/abs/2401.02051); [ReEvo, 2024](https://arxiv.org/abs/2402.01145) | The kinds; the ledger's lessons and ideas not tried |
| Models in code tournaments mostly edit without grounding in the last round's logs, and often don't check that a change acts. | [CodeClash, 2025](https://arxiv.org/abs/2511.00839) | Already the league's rule: a finding with its turns, then the rematch |
| A cheap test first, the full evaluation only for what passes. | [AlphaEvolve, 2025](https://arxiv.org/abs/2506.13131) | Head-to-head, then training, then holdout |

### Leagues of game-playing agents

| Finding | Source | Here |
|---|---|---|
| Agents whose only aim is to beat the main agents, frozen into the league once they win 70% and then started again, raised the main agent from 1540 to 1693 rating points; exploiters of the whole league, to 1824. Self-play alone had a high rating and a worst result against its own past versions of 46%, against 71%. | [AlphaStar, 2019](https://storage.googleapis.com/deepmind-media/research/alphastar/AlphaStar_unformatted.pdf) | Exploiters; the champion's weakest pairing |
| A rating can be raised by adding copies of the bots a player beats. A measure that weighs opponents by the game's equilibrium doesn't move with copies, though it jumps with small changes of the results. | [Re-evaluating Evaluation, 2018](https://arxiv.org/abs/1806.02643) | Copies leave; the paired table before the rating |
| Answering only the latest opponent chases cycles; answering a mixture of the population doesn't. | [PSRO, 2017](https://arxiv.org/abs/1711.00832); [OpenAI Five, 2019](https://arxiv.org/abs/1912.06680), 20% of games against past versions | Fixed opponents and references in every tournament |
| Games of skill have many strategies of middling strength that beat each other in circles. A small population cycles; above a size it climbs. | [Spinning tops, 2020](https://arxiv.org/abs/2004.09468) | Several lines at once |
| Opponents kept from past generations, with a win counted for more when few others can get it, found a winner in 7 generations against 12 to 29 without one of the parts. | Rosin and Belew, 1997, as measured by [Lubberts and Miikkulainen, 2001](https://www.cs.utexas.edu/users/nn/downloads/papers/lubberts.coevolution-gecco01.pdf) | Fixed opponents kept for what they take from the active bots |
| Bot authors report a local ladder that improved at every step while the bot got worse on the real one. | [A challenge winner's notes](https://gist.github.com/reCurs3/7d4eb5b952790e3009337f61c3341074); [a Halite IV team](https://github.com/0Zeta/HaliteIV-Bot) | The references guard; real games first |

### Keeping a search varied

| Finding | Source | Here |
|---|---|---|
| New structure is worse at first and dies before it is tuned. Letting it compete inside its own kind made the search 7 times faster; a kind that doesn't improve for 15 generations stops breeding. | [NEAT, 2002](https://www.cse.unr.edu/~sushil/class/gas/papers/NEAT.pdf) | A side line is protected while it promotes, closed after two iterations without |
| New individuals added on a schedule and kept apart from the old by age: an error of 28.7 against 153.1 for the plain search. Restarts that keep the old best fail, because its offspring swamp the newcomers. | [ALPS, 2006](https://gpbib.pmacs.upenn.edu/gecco2006/docs/p815.pdf) | A founder whenever a side place is free; never judged against the champion |
| A child that replaces its parent only when better keeps the niches the search began with and makes none. | [Covantes Osuna and Sudholt, 2018](https://arxiv.org/abs/1803.09766) | Admission by another rule than promotion |
| Keeping the best of each kind of behaviour finds better single solutions on deceptive problems than optimising directly, when the kinds are chosen to matter. | [MAP-Elites, 2015](https://arxiv.org/abs/1504.04909); [Pugh and others, 2016](https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2016.00040/full) | A line's head per strategy |
| Solutions carried between niches solved what direct optimisation couldn't; with transfer off, the hardest problems stayed unsolved. A newcomer is admitted for being good enough, not best. | [POET, 2019](https://arxiv.org/abs/1901.01753) | Grafts between lines; a third of the points admits a founder |
| On stagnation, start again wider. | [IPOP-CMA-ES, 2005](http://www.cmap.polytechnique.fr/~nikolaus.hansen/cec2005ipopcmaes.pdf) | A stalled main line gives its places to exploring |
| Evolved programs grow without getting better, and the growth slows the search. Size limits and a preference for the smaller answer it. | [A Field Guide to Genetic Programming, 2008](https://faculty.washington.edu/seattle/GA-2008/FieldGuideGP.pdf), 11.3 | Simplifications |

### Deciding from games

| Finding | Source | Here |
|---|---|---|
| A patch passes a test with stated error rates on tens of thousands of games, then a second, independent one. Code removal passes a looser test: not worse. An author gets four or five tries. The measured gain of a patch that passed is biased upward. | [Fishtest](https://official-stockfish.github.io/docs/fishtest-wiki/Creating-my-first-test.html), [its mathematics](https://official-stockfish.github.io/docs/fishtest-wiki/Fishtest-Mathematics.html) and [FAQ](https://official-stockfish.github.io/docs/fishtest-wiki/Fishtest-FAQ.html) | Clear and confirmed; simplifications; three tries |
| The chance that one player is the better is read from wins minus losses over the root of their sum; draws don't count. Games from one opening are paired, and the pair is the unit. | [Match statistics](https://www.chessprogramming.org/Match_Statistics); [Fishtest mathematics](https://official-stockfish.github.io/docs/fishtest-wiki/Fishtest-Mathematics.html) | The margin of the games that changed, and its chance by luck with the map as the unit |
| Two systems compared on the same cases need far fewer cases; cases that come in clusters widen the error up to threefold. | [Adding Error Bars to Evals, 2024](https://arxiv.org/abs/2411.00640) | The paired table; an exact test over maps, which here widened the error about threefold too |
| Openings that favour one side, each played from both, cut draws from 91.6% to 47.0%; engine testing prefers them to balanced ones. | [Unbalanced openings, 2024](https://www.sp-cc.de/uho_2024.htm) | Tried and not taken: see below |
| A holdout asked adaptively stops telling the truth; it lasts when it answers only above a margin, and fresh data needs neither. | [The reusable holdout, 2015](https://arxiv.org/abs/1506.02629); [The Ladder, 2015](https://arxiv.org/abs/1502.04585) | Confirmed on holdout by a margin; two new holdout maps an iteration |
| Choosing the best of several noisy candidates overstates it by about as much as candidates differ. | [Cawley and Talbot, 2010](https://www.jmlr.org/papers/v11/cawley10a.html) | The holdout as the second measurement |
| Agents trained on generated levels needed about 10,000 of them before the gap to unseen levels closed. | [Procgen, 2020](https://arxiv.org/abs/1912.01588) | Three maps added every iteration |

## What was left out

- **Maps that are not mirrors.** Measured after iteration 37, on eight seeds, each as a mirror and with one castle of a neutral pair, or of every pair, moved half a step and made one step cheaper or dearer. Draws fell from 14% of games to 9% or 10%, and games at the turn limit from 46% to about 40%. But the seat then decided a third of the pairs (each bot winning from the better seat) where it decided a tenth on mirrors, and the known steps showed less on them, not more. An early castle that costs a little less is too much of an edge in this game. Moving castles without changing their price left the seats even and the draws as they were. The option was not kept. With the copies gone, one bot comes out ahead in nine pairs of ten on mirrors.
- **A longer game.** More turns would let some drawn games end, at the cost of every game at the limit taking longer, and the frozen ones would stay frozen. The production lead reads the same games without playing them again.
- **A grid of behaviours** (MAP-Elites proper). It needs behaviour measured from games, which no tool does yet, and the league holds ten to twenty bots: lines are its niches.
- **An equilibrium rating** beside the fitted one. It jumps with small changes and needs a tool. Removing copies gives the part that mattered.
- **A sequential test** that plays until the result is sure. Bots are deterministic, so the sample is the maps: adding maps is the league's way of playing more.
- **Automatic tuning of constants.** The methods cost tens of thousands of games a run. A constant is tuned inside one candidate.
- **A strategy chosen per opponent from a record of past games.** A league bot remembers nothing between games.

## What the tools don't measure yet

Each is a change to `league_tools/`, made between iterations and measured with a full tournament, or an issue in the game's repository.

- **The production lead from the runner.** The league reads it from each drawn game's demo. The runner could report it with the result, and for decided games too.
- **Behaviour from the demos** (first attack, share of soldiers walking, production by turn 50), to say that two bots differ in kind, not only in results.
- **Opponents nobody studies**: a held-out player, as the holdout maps are held-out maps.
- **Rotating the holdout maps**: the set grows by two an iteration, and a person moves the oldest to training when it is large.
- **Reading git in the automated iteration**: it can't run `git log` or `git show`, so a founder there can't start from a deleted bot's code.

## Changing these rules

A rule here is a claim about what makes the league improve faster. Change one as a change of the league's setup: between iterations, with a ledger entry that says what changed and what was measured, and with the numbers of **What the review measured** taken again a few iterations later.
