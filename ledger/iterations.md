# The league's ledger

One entry per iteration, newest last. An entry says what was measured, what was tried, what was kept and what was learned, so that the next session starts from here and doesn't try a rejected idea again. Ratings have `level3` at 1000.

## Lessons so far

Short, general statements about the game that the games have shown. Add to them, and correct them when a later game says otherwise.

- On `circle` (two castles 4 apart, no neutral castles) a bot that spends its first soldiers on upgrades loses to one that sends everything at once: 32 soldiers arrive on turn 11, before production level 3 has paid for itself.
- Production upgrades pay on most maps with neutral castles: the economist, which does nothing else cleverly, beats default level 3 in 24 of 28 games. `islands` was the exception (4 of 12 points there), and the cause wasn't production but holding: see the next lesson.
- **A castle taken with 1 soldier near the enemy falls unless another castle reinforces it.** A bot that never sends soldiers to its own castles loses them to groups of 8 to 15 while its home castle holds 15 to 20 two or three units away and waits. Reinforcing a castle that would fall, from castles whose groups land before the attack, took the economist line from 4 to 14 of 16 points on `islands` and from 1108 to 1271 overall (iteration 1).
- **Castles that choose their targets independently in one turn send twice at one target** (two groups of 21 at a neutral of 20), and a neutral that an enemy group is already walking to is a different target: it will be an enemy castle, or a weakened neutral, when yours lands. Counting both is worth about 90 rating points (iteration 1).
- **Defence is about the landing that takes the castle, not the first one.** Counting every attacker against the first landing's deadline makes help look too late when the second group is the one that captures; playing the landings in order found help in time and beat its parent 16 of 18 (iteration 2).
- **A static reserve against the strongest enemy castle costs more than it saves.** Holding home what any enemy castle could send, before buying production, lost to its parent 4 of 18 and didn't even win `circle`'s opening (iteration 2's `reinforce_threat`): the economy it gave up mattered more than the strikes it deterred.
- **Steady small waves pin an economy that reserves every attacker in full.** `rusher`'s groups of 8, one every few turns, kept the economist line's home castle at production 2 to 4 on `strait` for 60 turns, although its growth alone would have met each wave. Reserving only what the landings need, growth counted, raised the score against `rusher` (16 against 14 of 18) but lost the mirror match against the parent (8 of 18), so it is not yet a gain (iteration 3).
- **Speed pays for long attacks.** A group that walks half as long meets half the target's growth and half the time for its owner to reinforce it; 10 soldiers for speed level 2 before an attack of over 8 turns beat its parent 16 of 18 (iteration 4).
- **Staging at the front finishes games the economist line couldn't.** Idle castles sending their spare soldiers to the castle nearest the enemy beat its parent 13 of 18 and took 26 of 26 points on `claw`, where its parent held 4,000 soldiers in six castles and never struck (iteration 4).
- **Keeping an attacking castle strong against its neighbours costs more than it saves**, as the production reserve did in iteration 2: an attack that may not leave its castle weaker than the strongest enemy castle could beat lost to its parent 3 of 18 (iteration 4).
- **Counting everything an enemy castle's owner could send to it makes a bot too timid.** Adding to a target's defenders the soldiers of every other enemy castle whose group could land first lost to its parent 5 of 18 (iteration 5): the owner seldom sends them all, and a bot that waits for that margin attacks too late. The real game's lesson stands for long walks; summing every castle within the walk overcounts it.
- **Mechanisms that only act in rare situations split the mirror match.** A candidate that differs from its parent only when, say, a rescue would be too slow plays most mirror games move for move like it, and two of its last three such candidates took exactly 9 of 18 against the parent while rating above it (`contested_timeline` in iteration 3, `speed_rescue` in iteration 5). The head-to-head rule then decides on a few games.
- **Put the attack margin on what is uncertain.** A castle's growth during the walk is certain; its soldiers and the groups bound for it are not. Applying the 1.3 margin to the soldiers and reinforcements only, and adding the growth as it is, beat its parent 14 of 18 and took `gyre` 30 of 30 (iteration 6): the old margin on growth kept the bot from striking castles that a steady attacker had emptied.
- **`circle`'s rush can be held only at a price.** Keeping the lone opening castle above what the enemy's castle could take turned both losses to `expander` into draws at the limit, but cost more on `claw` and `strait` than it gained (7 of 18 against its parent, iteration 6). Answering an attack at its origin, through the attacker, changed the length of 13 games and the winner of none.
- **A bot that only attacks what one castle affords alone never finishes.** Once the enemy's last castle holds more than any one of its castles can beat with the margin, it waits: the economist held 1,100 soldiers in 7 castles for 80 turns against one castle of 130 to 280 on `claw`. Sending every idle castle's spare soldiers at once, sized for the farthest group, was worse (iteration 1's `economist_pool`, 5 of 18 points against its parent). *What works (iteration 7):* a strike by the castles whose groups land within two turns of the nearest one, all at once, after the rear castles have fed the castle nearest the enemy: `frontline` beat every bot of the league, the champion 16 of 18.
- **Staging alone doesn't help the economist line.** Grafting `contested_stage`'s staging into the champion took exactly half against the parent twice (iteration 5 and 7): soldiers moved to the front still wait for one castle to afford a target alone. Staging pays with a strike made for it.
- **Counting the enemy groups that land after yours pays for neutral castles.** Playing every landing on a target in order, before and after the new group, fell 105 points below its parent on the holdout maps for every target of the economist line (iteration 7's `margin_landings`), but for `frontline`'s neutral targets alone it was promoted (iteration 8's `frontline_hold`), and it took the `ridge` games from the player's bot.
- **Near the turn limit, a strike should count exactly.** A margin that keeps a strike safe in the middle game turns a level end into a draw; dropping it in the last 30 turns, with the target's burst counted instead, won `circle` against the player's bot and beat the parent 10 of 18 (iteration 8's `frontline_finish`).
- **Production before the front is right against one opponent and wrong in the league.** Holding a rear castle's soldiers for its next production level before staging won `delta` against the player's bot, on both sides, but lost to its parent 7 of 18 (iteration 8's `frontline_economy`): the league's bots punish a late front more than they punish a thin economy.

From a real game between two players' bots on the official map, `claw` (2026-11-21, 195 turns; read with `league digest`, not played here):

- **Production is the entry fee, not an edge.** By turn 100 seven of the eight castles were at production level 4 and the eighth at 3, and the game stood at four castles each from turn 62 to turn 149. The league's founders, the economist apart, never buy production; a bot that only out-produces the default bots has not met a real opponent yet.
- **Short lines beat long walks.** The winner sent its soldiers 4.4 units on average and the loser 6.0. The winner moved every castle's production forward to a front castle every three turns (2,062 of its 3,373 soldiers sent went to its own castles), and its last strikes, of 74 to 98 soldiers, left from that castle. The loser attacked castles 6 to 8.2 units from where its soldiers stood, 12 to 17 turns of walking at speed level 1.
- **A defender that sees a long attack coming out-reinforces it.** On turn 53 the loser sent 84 soldiers at a castle that held 25, 8.2 units away. The defender added soldiers from two castles within 3.2 units and held 115 the turn before they arrived. Counting a target's defenders as its soldiers plus its growth is wrong for a walk of 17 turns: count what its owner can bring within the travel time.
- **Trickles lose to stacks.** After that, the loser kept sending groups of 9 to 21 from two castles at the same castle. They arrived one at a time and each lost alone.
- **The lightly held castle on the border decides a level game.** The castle at (0, -3) was captured four times, usually held under 20 soldiers while the stacks stood elsewhere, and its last capture, on turn 149, made production 19 against 12; the game ended 46 turns later.
- **Clashes trade one for one** (687 soldiers lost on each side), so nothing is won in the field: a group sent out of a castle at an arriving stack only delays it, when it is at least half the stack's size.
- **Neither bot bought speed**, in a game where attacks walked 12 to 17 turns. Whether speed level 2, for 10 soldiers, pays on a map this size is untested. *In the league it pays (iteration 4):* buying the next speed level before an attack that would walk more than 8 turns was the largest single gain so far, 1320 to 1518 on the training maps and 1679 to 1969 on the holdout maps.

From a real game of the champion, `speed_margin`, against a hosted bot in a lobby on `claw` (2026-11-21, 72 turns, lost with 0 castles to 8; read with `league digest`, not played here):

- **The opponent fed a front castle in batches and struck from two castles at once.** It bought production at home to level 3 on turns 1 and 2, took neutrals with groups of 14 to 18 at castles of 10, then bought production and speed level 2 on every castle; its three rear castles sent groups of 12 to the castle nearest us every three turns (499 of its 808 soldiers sent went to its own castles), and its strikes left from two or three castles at once: 39 and 22 at a castle of 29 on turn 50, 65, 12 and 7 at a castle of 37 on turn 66.
- **It won the game in the race for the two middle castles.** The champion took its two near neutrals by turn 9, then lost both middle castles: it sent 11 at a neutral of 10 from 5 units away, topped it up with groups of 1 that landed alone, and took the other middle castle with 1 soldier on turn 26, one turn before an enemy group of 23 landed. From turn 27 it had 3 castles to 5, and production 12 to 20 by turn 51.
- **The champion saved for 23 turns at home** (turns 27 to 50, "saving" every turn, 117 soldiers in three castles by turn 51) and sent nothing to its own castles all game; its first speed level came on turn 57.

From games of the league's bots against a second real opponent, a player's bot run here in the headless runner from its own project (2026-11-21, every map, both sides; the bot isn't in this repository):

- **It punishes a front that starves the rear.** `frontline` lost `delta` and `islands` to it on both sides: its home castle stayed at production 3 on `delta` and 2 on `islands` for 100 turns, because it sent every 10 to 12 spare soldiers to the front before it held the 20 or 30 its next level cost; the opponent reached production 19 to 23 with four or five castles. It also sent small groups out to meet `frontline`'s walking groups, which lost 215 soldiers in clashes on `delta`.
- **A level game at production 4 is a draw unless someone strikes exactly.** On `circle` both bots reached production 4 and `frontline` kept a lead of 16 to 46 soldiers for 270 turns without striking, since its strike wanted 1.5 times the defenders. `speed_margin` won the same map in 41 turns, striking when the opponent had spent on burst levels.

## Iteration 0: the founders

**Date:** 2026-11-21. **Maps:** 9 training (8 of the league's own and `claw`, the official map, rebuilt from the first board of a real game), 5 holdout. **Matches:** 504.

Four founders with different strategies, written to be simple and to disagree with each other, not to be good:

| Bot | Idea |
|---|---|
| `expander` | Each castle takes the cheapest castle it can afford alone, neutral or enemy; no upgrades. |
| `rusher` | Buy speed, then send every wave at the nearest enemy castle; neutrals only when close and cheap. |
| `economist` | Buy production levels first, expand with the surplus, attack enemies only with a margin. |
| `sentinel` | Burst and reinforce castles that would fall, and strike enemy castles that emptied. |

Training maps:

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| economist | 1108 | 0.852 | 92 | 0 | 16 |
| level3 | 1000 | 0.667 | 44 | 8 | 20 |
| sentinel | 831 | 0.519 | 50 | 12 | 46 |
| expander | 797 | 0.472 | 47 | 8 | 53 |
| level2 | 751 | 0.361 | 23 | 6 | 43 |
| rusher | 742 | 0.398 | 34 | 18 | 56 |
| level1 | 481 | 0.111 | 0 | 16 | 56 |

Holdout maps:

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| economist | 1462 | 0.983 | 59 | 0 | 1 |
| level3 | 1000 | 0.588 | 22 | 3 | 15 |
| sentinel | 836 | 0.508 | 27 | 7 | 26 |
| rusher | 802 | 0.467 | 25 | 6 | 29 |
| expander | 775 | 0.433 | 26 | 0 | 34 |
| level2 | 710 | 0.275 | 10 | 2 | 28 |
| level1 | 380 | 0.050 | 0 | 4 | 36 |

**Champion:** `economist`.

**Where it loses (training maps):** `islands` (4 of 12 points) and `strait` (8 of 12), and both `circle` games against `expander`. It wins all 12 of its games on `claw`. Nobody has read those games beyond `circle` yet; that is iteration 1's first job.

**Known from the review of the founders, for an iteration to fix** (a founder's code is not changed outside the loop):

- `sentinel` pays 10 soldiers for burst level 2 in a castle under attack to burst at most 4, and doesn't count the 10 in what the castle still lacks. On `archipelago` against `economist`, turn 52, castle 6 held 12 soldiers, paid 10 to burst 1, and fell.
- No founder defends against, or uses, anything the real game above showed: none moves soldiers forward between its own castles, none times several castles' groups to land together, and none counts a target's possible reinforcements.

**No bot failed a turn**, and no bot took more than 20 ms for a turn.

## Iteration 1: hold what you take

**Date:** 2026-11-21. **Maps:** 9 training, 5 holdout (unchanged). **Matches:** 756 in the training selection round robin, 330 in the holdout selection; the final standings are 594 training and 330 holdout matches. The baseline (`iteration-1-before`, 324 matches) gave exactly iteration 0's training table, so the runner and the cache agree with the ledger.

**Findings** (all from `economist`'s games on the training maps):

1. **It never reinforces its own castles.** In every game it lost, it sent 0 soldiers to its own castles. `strait`, against `rusher`, turns 16 to 18: castle 0 held 15 to 19 soldiers and logged "saving" while castle 2, 2.5 units away, held 3 against a group of 8 walking at it, and fell on turn 18; then castles 6 and 7 went the same way. `islands` against `level3`, turn 15: castle 2, taken on turn 5 with 1 soldier, fell to a group of 15 that had been walking since turn 2. `gyre` against `rusher`: castles 4, 7, 3, 2 and 9 each fell holding 1 to 6. **Cause:** its only defence is a reserve the size of the groups heading at a castle, which a castle that just grew from 1 soldier can't have. **Idea:** sentinel's reinforcement, grafted in, and only from castles whose group lands before the first attacker.
2. **It doesn't count who else is going to its target.** `islands` against `expander` and against `level3`, turn 4: it sent 11 soldiers 6.8 units at neutral castle 3, which the enemy's group took on turn 5. Against `expander`, turn 36: castles 0 and 2 each sent 21 at neutral castle 7, which held 20. **Cause:** it reads the target's soldiers and its own groups on the board, but neither the enemy's groups bound for the same castle nor this turn's sends. **Idea:** count enemy groups that land first (they take a neutral or reinforce their castle) and this turn's own sends.
3. **It can't finish, and it trickles.** `claw` against `level3` (a win in 207 turns): from turn 121 its 7 castles held 360 to 2,244 soldiers against one castle of 42 to 282, and it logged "saving" until turn 199, because no castle alone could afford the target with the 1.3 margin. `islands` against `level3`, turns 39 to 53: 13 sends of 1 to 13 soldiers at castle 5, most lost one at a time in clashes. **Cause:** a target is only ever one castle's job. **Idea:** castles that found nothing to afford alone pool their spare soldiers in one strike.

The economist logged nothing about threats, which is why finding 1 needed the board: both promoted candidates log what they saw (castles short under attack, contested neutrals).

**Candidates:**

| Candidate | Parent | Idea | Training rating | Against parent | Holdout rating (parent's) | Decision |
|---|---|---|---|---|---|---|
| `economist_reinforce` | economist | Graft from sentinel: a castle that would fall to the groups heading to it is reinforced first by own castles whose groups land in time. | 1293 (1106) | 15/18 | 1567 (1443) | **promoted** |
| `economist_contested` | economist | Size an attack by every group bound for the target: enemy groups that land first on a neutral or reinforce an enemy castle, and this turn's own sends. | 1198 (1106) | 13/18 | 1589 (1443) | **promoted** |
| `economist_pool` | economist | When no castle can afford a target alone, several castles strike it together with their spare soldiers in the same turn. | 1024 (1106) | 5/18 | not played | **rejected**: lost to its parent head to head and rated below it. Its games weren't read; it lost to `economist` on `strait`, `archipelago` and `crossing`, and scored less than its parent on `strait` (6/18 against 10/18) and `gyre` (8/18 against 12/18). A guess, not checked: a pooled strike empties every idle castle at once, which is the opposite of finding 1. |

All three passed the gate: no failed turn, slowest turns 17.0, 17.6 and 28.4 ms.

**Status changes:** `economist_reinforce` and `economist_contested` are active. `economist` is **retired**: `economist_reinforce`'s row of the pair table matches or beats it against every other player, on the training maps and on the holdout maps. Active: 5; retired: 1.

Training maps (`iteration-1-train`, 594 matches):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| economist_reinforce | 1271 | 0.875 | 122 | 8 | 14 |
| economist_contested | 1165 | 0.785 | 111 | 4 | 29 |
| economist (retired) | 1076 | 0.694 | 96 | 8 | 40 |
| level3 | 1000 | 0.519 | 52 | 8 | 48 |
| sentinel | 826 | 0.403 | 52 | 12 | 80 |
| expander | 808 | 0.382 | 51 | 8 | 85 |
| rusher | 784 | 0.354 | 42 | 18 | 84 |
| level2 | 747 | 0.250 | 24 | 6 | 78 |
| level1 | 483 | 0.074 | 0 | 16 | 92 |

Holdout maps (`iteration-1-holdout`, 330 matches):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| economist_contested | 1589 | 0.900 | 72 | 0 | 8 |
| economist_reinforce | 1567 | 0.887 | 70 | 2 | 8 |
| economist (retired) | 1443 | 0.812 | 64 | 2 | 14 |
| level3 | 1000 | 0.392 | 22 | 3 | 35 |
| sentinel | 861 | 0.394 | 28 | 7 | 45 |
| rusher | 815 | 0.350 | 25 | 6 | 49 |
| expander | 789 | 0.325 | 26 | 0 | 54 |
| level2 | 726 | 0.183 | 10 | 2 | 48 |
| level1 | 397 | 0.033 | 0 | 4 | 56 |

**Champion:** `economist_reinforce`, 1271 on the training maps (iteration 0's champion, `economist`, was 1108; 1076 in this tournament). It beats `level3` and `sentinel` 18 of 18. The two promoted bots split their pair 9/18 on training and 5/10 on holdout; `economist_contested` leads on the holdout maps by 22 points.

**Where the champion still loses (training maps):**

- `circle` against `expander`, both sides, in 12 turns: it buys production on turn 1 and dies to the all-in, as iteration 0's first lesson says. No economist descendant has answered it.
- `strait` (turn 64) and `gyre` (turn 91) against `rusher`, both sides: unread this iteration. Reinforcement didn't change these games; rusher's waves of 8 arrive every few turns from several castles.
- Against `economist_contested`: 5 losses on `gyre`, `islands`, `claw` and `delta`, three of them at the generation limit, and draws at the limit on `circle` and `claw` against both economist descendants: neither finishes a level game (the fourth lesson).

**Next:** the obvious candidate is the two promoted ideas together (`economist_reinforce` with `economist_contested`'s target accounting), measured from the start. Then `rusher` on `strait` and `gyre`, and a finish that isn't a pool of every idle castle.

## Iteration 2: the two ideas together, and defence in order

**Date:** 2026-11-21. **Maps:** 9 training, 5 holdout (unchanged). **Matches:** 1,134 in the training selection round robin, 520 in the holdout selection; the final standings are 936 training and 520 holdout matches. The baseline (`iteration-2-before`) gave exactly iteration 1's training table.

**Findings** (from `economist_reinforce`'s games on the training maps):

1. **It spends its home castle down while an enemy castle can strike.** `circle`, against `expander`, turns 1 to 4: it bought production levels 2 and 3 and held 7 soldiers on turn 4; `expander`, 4 units away with 33, sent 32 that turn and took the castle on turn 11 (28 held). **Cause:** its reserve counts groups already walking, never an enemy castle that could send. **Idea:** keep home what the strongest enemy castle could bring before its group lands.
2. **Its reinforcement never fired on `strait`.** Against `rusher`, turn 12: castle 2 held 6 against two groups of 8, landing in 3 and about 7 turns; castle 0, 5 turns away, had 15. All 16 attackers were counted against the first landing's deadline of 3 turns, so no helper was "in time", although the second group, the one that took the castle on turn 18, could have been met. The game is move for move the same as `economist`'s. **Cause:** the shortfall is measured at the first landing. **Idea:** play the landings in order and help in time for the one that would capture.
3. **It still sends twice at one target.** `gyre`, against `economist_contested` (which won both sides), turn 39: castles 0 and 4 each sent 26 at neutral castle 9, which held 25. This is iteration 1's finding 2, which `economist_contested` answers. **Idea:** graft that accounting in, as iteration 1's entry proposed.

**Candidates:**

| Candidate | Parent | Idea | Training rating (parent's) | Against parent | Holdout rating (parent's) | Decision |
|---|---|---|---|---|---|---|
| `reinforce_timeline` | economist_reinforce | Reinforce against the attack that would take the castle: play the attackers' landings in order and help in time for the first one that captures. | 1364 (1277) | 16/18 | 1764 (1543) | **promoted** |
| `reinforce_contested` | economist_reinforce | Graft from economist_contested: size an attack by every group bound for the target, enemy groups that land first and this turn's own sends. | 1358 (1277) | 11.5/18 | 1746 (1543) | **promoted** |
| `reinforce_threat` | economist_reinforce | Keep home what the strongest enemy castle could bring before its group lands; buy and attack only with the rest. | 1186 (1277) | 4/18 | not played | **rejected**: lost to its parent and rated below it. It took 20 of 22 points on `strait` (parent 16) but fewer elsewhere, and still lost `circle`'s opening (14/22 against 15/22); its games weren't read. |

All three passed the gate: no failed turn, slowest turns 18.7, 15.8 and 14.7 ms.

**Status changes:** `reinforce_timeline` and `reinforce_contested` are active. `economist_reinforce` stays active: neither candidate's row matches it everywhere (`reinforce_timeline` took 14/18 from `economist` to its 15; `reinforce_contested` 16/18 from `level3` to its 18). That made seven active bots, so `sentinel`, the lowest-rated active bot (843), is **retired**: `reinforce_timeline`'s row beats it against every other player. Active: 6; retired: 2.

Training maps (`iteration-2-train`, 936 matches):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| reinforce_contested | 1321 | 0.831 | 143 | 13 | 24 |
| reinforce_timeline | 1318 | 0.828 | 143 | 12 | 25 |
| economist_reinforce | 1228 | 0.747 | 126 | 17 | 37 |
| economist_contested | 1175 | 0.694 | 120 | 10 | 50 |
| economist (retired) | 1080 | 0.594 | 100 | 14 | 66 |
| level3 | 1000 | 0.417 | 56 | 8 | 80 |
| expander | 832 | 0.328 | 55 | 8 | 117 |
| sentinel (retired) | 827 | 0.322 | 52 | 12 | 116 |
| rusher | 821 | 0.317 | 48 | 18 | 114 |
| level2 | 768 | 0.201 | 26 | 6 | 112 |
| level1 | 494 | 0.056 | 0 | 16 | 128 |

Holdout maps (`iteration-2-holdout`, 520 matches):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| reinforce_timeline | 1764 | 0.900 | 88 | 4 | 8 |
| reinforce_contested | 1746 | 0.890 | 87 | 4 | 9 |
| economist_reinforce | 1543 | 0.760 | 73 | 6 | 21 |
| economist_contested | 1543 | 0.760 | 75 | 2 | 23 |
| economist (retired) | 1391 | 0.660 | 64 | 4 | 32 |
| level3 | 1000 | 0.294 | 22 | 3 | 55 |
| sentinel (retired) | 881 | 0.325 | 29 | 7 | 64 |
| rusher | 823 | 0.280 | 25 | 6 | 69 |
| expander | 797 | 0.260 | 26 | 0 | 74 |
| level2 | 736 | 0.138 | 10 | 2 | 68 |
| level1 | 407 | 0.025 | 0 | 4 | 76 |

**Champion:** `reinforce_contested`, 1321 on the training maps (iteration 1's champion, `economist_reinforce`, was 1271; 1228 in this tournament). `reinforce_timeline` is 3 points behind on training and 18 ahead on holdout, and wins their pair 11/18 to 7/18 for `reinforce_contested`: the two are equals with different strengths.

**Where the champion still loses (training maps):** `circle` against `expander` in 12 turns (both sides; still nobody's answer); `strait` against `rusher` (79 turns), `level3` (76) and `economist_reinforce` (125); `gyre` against `rusher` (75); `islands` against `level2` (85 and 93) and `reinforce_timeline` (146); `archipelago` against `economist`; `delta` against `reinforce_timeline` and `economist_contested`, in games of 219 to 300 turns.

**Next:** `reinforce_timeline`'s defence grafted into `reinforce_contested` (both promoted, one idea each); `strait`, where the champion loses to four players; and `circle`'s opening, which neither a reserve nor anything else has answered.

## Iteration 3: nothing promoted

**Date:** 2026-11-21. **Maps:** 9 training, 5 holdout (unchanged). **Matches:** 1,584 in the training selection round robin; no holdout selection (no candidate passed); the final standings are 936 training and 520 holdout matches, all from the cache, the same as iteration 2's. The baseline (`iteration-3-before`) gave exactly iteration 2's training table.

**Findings** (from `reinforce_contested`'s games on the training maps):

1. **Its reserve doesn't count growth, so steady waves pin it.** `strait`, against `rusher`, turns 30 to 33: castle 0 held 13 to 15 soldiers at production 2 and logged "saving", with one group of 8 three to five turns away, which its growth alone would have met. The reserve was the 8 in full plus 4, so it couldn't buy production 3 or strike `rusher`'s castles, which held 2 to 9 after each wave. Its production stayed at 2 to 4 for the whole 79-turn game. **Idea:** keep home only what the castle needs now to hold through every landing, its growth counted.
2. **It tops up attacks in trickles.** `strait`, against `level3`, turns 22 to 27 and 42 to 47: castle 0 sent 14 and then 2, 1, 1, 2, 1 at castle 2, and later 18 and then 2, 1, 1, 2, 1; its small groups died in clashes on turns 47 and 55, and castle 2 changed hands six times. **Cause:** each turn it adds whatever the target's growth or reinforcements added since the last send. **Idea:** own groups count towards a target only when the new group lands with them.
3. **Its defence is still measured at the first landing.** `reinforce_timeline` beats it 11/18 to 7/18 (on `islands` and `delta`). **Idea:** graft `reinforce_timeline`'s defence, as iteration 2's entry proposed.

**Candidates:**

| Candidate | Parent | Idea | Training rating (parent's) | Against parent | Decision |
|---|---|---|---|---|---|
| `contested_timeline` | reinforce_contested | Graft from reinforce_timeline: reinforce against the landing that would take the castle, played in order, not the first one. | 1382 (1349) | 9/18 | **rejected**: exactly half against its parent, not more, although it rated above it and scored 15 to 18 of 18 against every bot below the top three. |
| `contested_growth` | reinforce_contested | A castle under attack keeps home only what it needs now to hold through every landing, counting its growth until each lands. | 1327 (1349) | 8/18 | **rejected**: below its parent in both rules. |
| `contested_notopup` | reinforce_contested | No top-ups: own groups already walking to a target count only if the new group lands within a turn of them, so attacks land as stacks. | 1272 (1349) | 7/18 | **rejected**: below its parent in both rules; it lost 4/18 to `reinforce_timeline`. |

All three passed the gate: no failed turn, slowest turns 22.2, 36.5 and 35.8 ms. None played the holdout maps.

**Status changes:** none. Active: `reinforce_contested`, `reinforce_timeline`, `economist_reinforce`, `economist_contested`, `expander`, `rusher`; retired: `economist`, `sentinel`.

**Standings:** unchanged from iteration 2 (`iteration-3-train` and `iteration-3-holdout`): training `reinforce_contested` 1321, `reinforce_timeline` 1318, `economist_reinforce` 1228, `economist_contested` 1175, `economist` 1080, `level3` 1000, `expander` 832, `sentinel` 827, `rusher` 821, `level2` 768, `level1` 494; holdout `reinforce_timeline` 1764, `reinforce_contested` 1746, `economist_reinforce` 1543, `economist_contested` 1543, `economist` 1391, `level3` 1000, `sentinel` 881, `rusher` 823, `expander` 797, `level2` 736, `level1` 407.

**Champion:** `reinforce_contested`, 1321, unchanged.

**Where the champion still loses:** as in iteration 2: `circle` against `expander`, `strait` against four players, `gyre` against `rusher`, `islands` against `level2` and `reinforce_timeline`.

**What this says:** the top of the league is now three economist descendants that differ in one mechanism each and split their games about evenly; a change that helps against the rest of the field doesn't show against the parent. If iteration 4 also promotes nothing, iteration 5 starts with new maps and a founder, as the iteration skill says.

## Iteration 4: speed and the front

**Date:** 2026-11-21. **Maps:** 9 training, 5 holdout (unchanged). **Matches:** 1,584 in the training selection round robin, 750 in the holdout selection; the final standings are 1,014 training and 750 holdout matches. The baseline (`iteration-4-before`) gave exactly iteration 3's training table.

**Findings** (from `reinforce_contested`'s games on the training maps):

1. **It never finishes a won game.** `claw`, against `reinforce_timeline`, turns 131 to 300: six castles grew from 470 to 4,286 soldiers against two castles of 165 to 1,437; on turn 150 each of its castles held 92 to 131 and the nearest enemy castle 111, which no single castle could take with the 1.3 margin and the growth of the walk. It won on castle count at the limit; against an equal it would have drawn. **Idea:** the real game's short lines: idle castles send their spare soldiers to the castle nearest the enemy, which can then strike alone.
2. **It empties castles next to strong enemy castles.** `islands`, against `level2`, turn 63: castle 0 sent 29 of its 36 soldiers at `level2`'s home castle 8.0 units away (16 turns), and castle 2 spent 26 on production level 4, keeping 8; `level2`'s castles of 39 and 29 stood 2.9 and 1.6 units away. On turn 64 both struck, and the bot was out by turn 84. **Idea:** an attack may not leave its castle weaker than the strongest enemy castle could beat; unlike iteration 2's rejected `reinforce_threat`, production buys aren't held back.
3. **Its attacks walk at speed level 1.** In the same game, turns 47 to 62, a group of 24 walked 7 units (14 turns) to castle 7 while 12 more groups of 1 or 2 followed it, each adding the target's growth of one more turn; the bot has never bought speed, and neither had the real game's players. **Idea:** buy the next speed level before an attack that would walk more than 8 turns.

**Candidates:**

| Candidate | Parent | Idea | Training rating (parent's) | Against parent | Holdout rating (parent's) | Decision |
|---|---|---|---|---|---|---|
| `contested_speed` | reinforce_contested | Before an attack that would walk more than SPEED_WALK turns, its castle buys the next speed level when it can afford both. | 1518 (1320) | 16/18 | 1969 (1679) | **promoted** |
| `contested_stage` | reinforce_contested | Short lines: a castle that finds nothing to attack alone sends its spare soldiers to the own castle nearest the enemy, which then strikes alone. | 1369 (1320) | 13/18 | 1764 (1679) | **promoted** |
| `contested_attack_guard` | reinforce_contested | An attack may not leave its castle with fewer soldiers than the strongest enemy castle could beat on arrival; production buys are not held back. | 1227 (1320) | 3/18 | not played | **rejected**: below its parent in both rules; 12/26 on `claw` against its parent's 21. |

All three passed the gate: no failed turn, slowest turns 22.0, 16.7 and 23.1 ms (`contested_stage` took 38.1 ms on a holdout map).

**Status changes:** `contested_speed` and `contested_stage` are active. `reinforce_contested` is **retired**: `contested_speed`'s row matches or beats it against every other player on both sets of maps. That left seven active bots, so `rusher`, the lowest-rated active bot (845), is **retired** as well: `contested_speed`'s row beats it against every other player. Active: `contested_speed`, `contested_stage`, `reinforce_timeline`, `economist_reinforce`, `economist_contested`, `expander`; retired: `economist`, `sentinel`, `reinforce_contested`, `rusher`.

Training maps (`iteration-4-train`, 1,014 matches):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| contested_speed | 1512 | 0.896 | 186 | 15 | 15 |
| contested_stage | 1391 | 0.810 | 169 | 12 | 35 |
| reinforce_timeline | 1296 | 0.727 | 149 | 16 | 51 |
| reinforce_contested (retired) | 1293 | 0.725 | 147 | 19 | 50 |
| economist_reinforce | 1235 | 0.669 | 134 | 21 | 61 |
| economist_contested | 1165 | 0.600 | 122 | 15 | 79 |
| economist (retired) | 1086 | 0.519 | 103 | 18 | 95 |
| level3 | 1000 | 0.344 | 58 | 8 | 114 |
| expander | 856 | 0.292 | 59 | 8 | 149 |
| rusher (retired) | 845 | 0.282 | 52 | 18 | 146 |
| sentinel (retired) | 830 | 0.269 | 52 | 12 | 152 |
| level2 | 780 | 0.167 | 27 | 6 | 147 |
| level1 | 503 | 0.044 | 0 | 16 | 164 |

Holdout maps (`iteration-4-holdout`, 750 matches):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| contested_speed | 1969 | 0.933 | 108 | 8 | 4 |
| reinforce_timeline | 1776 | 0.825 | 96 | 6 | 18 |
| contested_stage | 1764 | 0.817 | 98 | 0 | 22 |
| reinforce_contested (retired) | 1679 | 0.758 | 88 | 6 | 26 |
| economist_reinforce | 1574 | 0.683 | 78 | 8 | 34 |
| economist_contested | 1514 | 0.642 | 75 | 4 | 41 |
| economist (retired) | 1398 | 0.567 | 66 | 4 | 50 |
| level3 | 1000 | 0.235 | 22 | 3 | 75 |
| sentinel (retired) | 882 | 0.271 | 29 | 7 | 84 |
| rusher (retired) | 824 | 0.233 | 25 | 6 | 89 |
| expander | 798 | 0.217 | 26 | 0 | 94 |
| level2 | 737 | 0.110 | 10 | 2 | 88 |
| level1 | 408 | 0.020 | 0 | 4 | 96 |

**Champion:** `contested_speed`, 1512 on the training maps (iteration 3's champion, `reinforce_contested`, was 1321; 1293 in this tournament).

**Where the champion still loses (training maps):** `circle` against `expander` in 12 turns, both sides (every economist descendant still loses it); `strait` against `rusher` (79 turns), `level3` (76), `contested_stage` (94 and 100) and `economist_reinforce` (125), both sides each; `gyre` against `rusher` (75); `claw` against `contested_stage` (103); `islands` against `level2` (93, one side). Draws at the limit on `circle` against `contested_stage`, `economist` and `economist_contested`.

**Next:** `contested_stage`'s staging grafted into `contested_speed` (both promoted, and staging beats the champion on `claw` and `strait`); `strait`, where the champion loses to four players; `circle`'s opening.

## Iteration 5: nothing promoted

**Date:** 2026-11-21. **Maps:** 9 training, 5 holdout (unchanged). **Matches:** 2,106 in the training selection round robin; no holdout selection (no candidate passed); the final standings are 1,014 training and 750 holdout matches, all from the cache, the same as iteration 4's. The baseline (`iteration-5-before`) gave exactly iteration 4's training table.

**Findings** (from `contested_speed`'s games on the training maps):

1. **A castle that no helper reaches in time falls while big castles watch.** `strait`, against `economist_reinforce`, turns 82 to 84: castle 4 (production level 1, 14 soldiers) logged as unheld three turns running while castles 0 and 2 held 70 to 78 and 50 to 58, 7 turns away at speed level 1; it fell on turn 84 with 1 soldier. `islands`, against `level2`, turns 77 to 80: castle 5 (13) faced a group of 32 with no helper in time and fell. Speed was never bought: every walk on `strait` is 7 turns or less, under the champion's threshold of 8. **Idea:** a helper that is too slow buys speed when that makes its group land in time.
2. **Castles it takes fall again within ten turns.** `islands`, against `level2`: castle 5 taken on turn 51 with 4 soldiers and lost on turn 61, taken again on turn 71 with 9 and lost on turn 80; castle 3 taken on turn 82 with 8 and lost on turn 92, to groups of 32 to 44 from castles 1.6 to 6.8 units away. **Cause:** a target's defenders are its soldiers, growth and the groups bound for it, never what its owner could send there, the real game's lesson. **Idea:** count the soldiers of the owner's castles whose groups could land first.
3. **`contested_stage` beats the champion on `strait` and `claw`, both sides** (5/18 to 13/18 for the champion overall). **Idea:** graft its staging, as iteration 4's entry proposed.

**Candidates:**

| Candidate | Parent | Idea | Training rating (parent's) | Against parent | Decision |
|---|---|---|---|---|---|
| `speed_rescue` | contested_speed | A castle too slow to reinforce a castle that would fall buys its next speed level when that makes its group land in time. | 1502 (1490) | 9/18 | **rejected**: exactly half against its parent, not more, though it rated above it. |
| `speed_stage` | contested_speed | Graft from contested_stage: a castle that finds nothing to attack alone sends its spare soldiers to the own castle nearest the enemy. | 1421 (1490) | 9/18 | **rejected**: half against its parent and rated below it. It beat `rusher` and `level3` 18/18 where the parent took 14 and 16, but lost 8/18 to `contested_stage` itself and 11/18 to `economist_reinforce` against the parent's 15. |
| `speed_reach` | contested_speed | An enemy castle's defenders include what its owner's other castles could send there before the attack lands. | 1331 (1490) | 5/18 | **rejected**: below its parent in both rules; 46 draws in 270 games, the most of any bot, as it waited for margins it never got. |

All three passed the gate: no failed turn, slowest turns 16.1, 13.4 and 17.7 ms. None played the holdout maps.

**Status changes:** none. Active: `contested_speed`, `contested_stage`, `reinforce_timeline`, `economist_reinforce`, `economist_contested`, `expander`; retired: `economist`, `sentinel`, `reinforce_contested`, `rusher`.

**Standings:** unchanged from iteration 4 (`iteration-5-train`, `iteration-5-holdout`); see that entry's tables.

**Champion:** `contested_speed`, 1512 on the training maps and 1969 on the holdout maps, unchanged.

**Where the champion still loses:** as in iteration 4: `circle` against `expander`; `strait` against `rusher`, `level3`, `contested_stage` and `economist_reinforce`; `gyre` against `rusher`; `claw` against `contested_stage`; `islands` against `level2`.

**Next:** iterations 3 and 5 promoted nothing, and two near misses were exact halves against the parent. If iteration 6 also promotes nothing, iteration 7 starts by adding maps (more games per pair) and with a founder. `circle`'s opening has now survived five iterations: it may need a founder that doesn't buy production first.

## Iteration 6: the margin on what is uncertain

**Date:** 2026-11-21. **Maps:** 9 training, 5 holdout (unchanged). **Matches:** 2,106 in the training selection round robin, 880 in the holdout selection; the final standings are 1,134 training and 880 holdout matches. The baseline (`iteration-6-before`) gave exactly iteration 5's training table.

**Findings** (from `contested_speed`'s games on the training maps):

1. **It never strikes a steady attacker's empty castles.** `gyre`, against `rusher`, turns 36 to 40: `rusher`'s castles held 2 to 9 soldiers after each wave of 8 to 12, while castle 0 held 15 to 21. Its nearest, castle 4 (3 units, 6 turns, 5 to 9 soldiers at production 1), needed `ceil((9 + 6) × 1.3) + 1` = 21 with the margin on the growth as well; with the wave of 8 walking at it, castle 0 had 8 to spare. The game was lost on turn 75. **Idea (a):** the margin covers the target's soldiers and reinforcements, not its certain growth.
2. **The soldiers it keeps for an incoming wave do nothing.** In the same game, castle 0 kept 8 to 12 home against each wave while the wave's origin stood empty on the same line. **Idea (b):** answer an attack by striking its origin through the attacker: the group meets it head-on, and if it has more than twice the attacker it walks on.
3. **`circle`'s opening, lost by every economist descendant since iteration 0.** Turns 1 to 4 (iteration 2's finding 1): it buys production down to 7 soldiers, and `expander`, 4 units away with 33, takes the castle. Iteration 2's `reinforce_threat` held that reserve all game and lost. **Idea (c):** hold it only while the bot owns a single castle.

**Candidates:**

| Candidate | Parent | Idea | Training rating (parent's) | Against parent | Holdout rating (parent's) | Decision |
|---|---|---|---|---|---|---|
| `speed_margin` | contested_speed | The attack margin covers the target's soldiers and reinforcements, not its growth during the walk, which is certain. | 1562 (1471) | 14/18 | 2010 (1937) | **promoted** |
| `speed_counter` | contested_speed | Answer an attack by striking its origin along the same line: the group meets the attacker head-on, so the soldiers kept home for it go out instead. | 1471 (1471) | 9/18 | not played | **rejected**: half against its parent and the same rating. The counter fired (16 times in one `gyre` game) but changed the winner of no game: its row of the pair table is its parent's, cell for cell. |
| `speed_opening` | contested_speed | While the bot has one castle, it spends nothing below what the strongest enemy castle could take; unlike reinforce_threat, only in the opening. | 1422 (1471) | 7/18 | not played | **rejected**: below its parent in both rules. It drew both `circle` games against `expander` (the parent loses them) but fell to 18.5/30 on `claw` and 14/30 on `strait` (parent 24.5 and 19). |

All three passed the gate: no failed turn, slowest turns 36.3, 19.3 and 10.3 ms.

**Status changes:** `speed_margin` is active. `contested_speed` stays active: `speed_margin` scored less against `reinforce_timeline` (15/18 to its 17). That made seven active bots, so `expander`, the lowest-rated active bot (880 in the selection), is **retired**: `speed_margin`'s row beats it against every other player. It stays in every tournament as a retired opponent, with its `circle` rush. Active: `speed_margin`, `contested_speed`, `contested_stage`, `reinforce_timeline`, `economist_reinforce`, `economist_contested`; retired: `economist`, `sentinel`, `reinforce_contested`, `rusher`, `expander`.

Training maps (`iteration-6-train`, 1,134 matches):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| speed_margin | 1557 | 0.893 | 198 | 22 | 14 |
| contested_speed | 1482 | 0.844 | 187 | 21 | 26 |
| contested_stage | 1387 | 0.769 | 173 | 14 | 47 |
| reinforce_timeline | 1292 | 0.684 | 151 | 18 | 65 |
| reinforce_contested (retired) | 1281 | 0.673 | 147 | 21 | 66 |
| economist_reinforce | 1232 | 0.626 | 134 | 25 | 75 |
| economist_contested | 1163 | 0.558 | 122 | 17 | 95 |
| economist (retired) | 1097 | 0.491 | 104 | 22 | 108 |
| level3 | 1000 | 0.313 | 58 | 8 | 132 |
| expander (retired) | 873 | 0.278 | 61 | 8 | 165 |
| rusher (retired) | 863 | 0.269 | 54 | 18 | 162 |
| sentinel (retired) | 837 | 0.248 | 52 | 12 | 170 |
| level2 | 803 | 0.162 | 29 | 6 | 163 |
| level1 | 512 | 0.040 | 0 | 16 | 182 |

Holdout maps (`iteration-6-holdout`, 880 matches):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| speed_margin | 2010 | 0.915 | 119 | 0 | 11 |
| contested_speed | 1937 | 0.877 | 110 | 8 | 12 |
| reinforce_timeline | 1825 | 0.808 | 102 | 6 | 22 |
| contested_stage | 1779 | 0.777 | 101 | 0 | 29 |
| reinforce_contested (retired) | 1668 | 0.700 | 88 | 6 | 36 |
| economist_reinforce | 1567 | 0.631 | 78 | 8 | 44 |
| economist_contested | 1509 | 0.592 | 75 | 4 | 51 |
| economist (retired) | 1395 | 0.523 | 66 | 4 | 60 |
| level3 | 1000 | 0.214 | 22 | 3 | 85 |
| sentinel (retired) | 882 | 0.250 | 29 | 7 | 94 |
| rusher (retired) | 824 | 0.215 | 25 | 6 | 99 |
| expander (retired) | 798 | 0.200 | 26 | 0 | 104 |
| level2 | 737 | 0.100 | 10 | 2 | 98 |
| level1 | 409 | 0.018 | 0 | 4 | 106 |

**Champion:** `speed_margin`, 1557 on the training maps and 2010 on the holdout maps (iteration 5's champion, `contested_speed`, was 1512 and 1969; 1482 and 1937 in this tournament). Over iterations 1 to 6 the champion went from 1108 to 1557 against the same fixed `level3`.

**Where the champion still loses (training maps):** `circle` against `expander` in 12 turns, both sides; `claw` against `contested_stage` (76 and 81 turns) and `crossing` against it (138 and 182); `strait` against `rusher` (93) and `reinforce_timeline` (114), both sides; `islands` against `level2` (86 and 112); `archipelago` against `economist` (159); `crossing` against `contested_speed` at the limit. Draws at the limit on `circle` against `contested_speed`, `contested_stage` and `economist`.

**Next:** `contested_stage` now beats the champion on `claw` and `crossing`, both sides: its staging, measured against the new champion. `strait`, against two players. `circle`'s opening still has no answer that pays for itself.

## Iteration 7: the front, after a real opponent

**Date:** 2026-11-21. **Maps:** 9 training, 5 holdout (unchanged). **Matches:** 2,394 in the training selection round robin, 1,170 in the holdout selection; the final standings are 1,836 training and 1,020 holdout matches. The baseline (`iteration-7-before`, 1,584 matches) gave exactly iteration 6's training table.

Before this iteration the champion played its first real game, against a hosted bot in a lobby on `claw`, and lost it in 72 turns (the lessons above). This iteration's founder is built after that opponent: the league had no bot that plays like it, and a strategy that beats the champion in a real game is the one the league should meet.

**Findings** (the real game, and `speed_margin`'s games on the training maps):

1. **It takes contested castles with 1 soldier and loses them a turn later.** The real game, turn 26: castle 4 taken with 1, lost on turn 27 to groups of 18 and 5 sent on turns 20 and 21. `claw`, against `contested_stage`, turn 19: castle 2 taken with 1 and lost on turn 20 to a group of 4 one turn behind; castle 4 taken on turn 26 and lost on turn 36. **Cause:** a target's defenders count only the enemy groups that land before the new group. **Idea (a):** play every landing on the target in order.
2. **It tops up in groups of 1 that land alone.** The real game, turns 16 to 19 and 21 to 26: groups of 1 and 2 at castles 2 and 4, logged `0->2!:1`; its group of 11 landed a turn before the enemy's, alone, while the accounting counted it with every later send. `claw` against `contested_stage`, turns 11 to 19, the same from the other side. **Cause:** the bot's own groups bound for a target count whatever their landing turn. The same idea (a) answers it: the landings in order, own groups too.
3. **It saves at home while the enemy builds a front.** The real game, turns 27 to 50: "saving" every turn with 3 castles at production 12, while the opponent moved its rear castles' soldiers to its castle nearest us and struck from two castles at once. `contested_stage`, which stages, beats the champion on `claw` and `crossing`, both sides. **Ideas:** (b) graft the staging; (c) a founder that plays as the real opponent did.

**Candidates:**

| Candidate | Parent | Idea | Training rating (parent's) | Against parent | Holdout rating (parent's) | Decision |
|---|---|---|---|---|---|---|
| `frontline` | speed_margin (scaffolding) | A new strategy, from the real game's winner: every castle buys production then speed, rear castles feed the castle nearest the enemy in batches, and the castles nearest a target strike it together. | 1677 (1501) | 16/18 | 2161 (2004) | **promoted** |
| `margin_landings` | speed_margin | Size an attack by playing every landing on the target in order, own and enemy groups, before and after this one: send what leaves the castle ours after the last of them. | 1535 (1501) | 10.5/18 | 1899 (2004) | **rejected**: its holdout rating is below its parent's. |
| `margin_stage` | speed_margin | Graft from contested_stage: a castle that finds nothing to attack alone sends its spare soldiers to the own castle nearest the enemy. | 1490 (1501) | 9/18 | not played | **rejected**: half against its parent and rated below it; 30/32 on `claw` (parent 25) but 20/32 on `crossing` and 22/32 on `far-shores` (parent 27 and 28). |

All three passed the gate: no failed turn, slowest turns 12.9, 18.9 and 20.0 ms.

**Status changes:** `frontline` is active. `speed_margin` stays active: `frontline` scored less against `level3` on the training maps (16/18 to its 18) and against `contested_speed`, `economist_reinforce` and `economist` on the holdout maps. That made seven active bots, so `economist_contested`, the lowest-rated active bot (1149 in the selection), is **retired**: `frontline`'s row beats it against every other player on both sets of maps. Active: `frontline`, `speed_margin`, `contested_speed`, `contested_stage`, `reinforce_timeline`, `economist_reinforce`; retired: `economist`, `sentinel`, `reinforce_contested`, `rusher`, `expander`, `economist_contested`.

Training maps (`iteration-7-train`, 1,836 matches):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| frontline | 1668 | 0.925 | 225 | 16 | 11 |
| speed_margin | 1517 | 0.837 | 199 | 24 | 29 |
| contested_speed | 1459 | 0.796 | 189 | 23 | 40 |
| contested_stage | 1373 | 0.726 | 175 | 16 | 61 |
| reinforce_timeline | 1285 | 0.647 | 153 | 20 | 79 |
| reinforce_contested (retired) | 1266 | 0.629 | 147 | 23 | 82 |
| economist_reinforce | 1219 | 0.585 | 134 | 27 | 91 |
| economist_contested (retired) | 1153 | 0.522 | 122 | 19 | 111 |
| economist (retired) | 1089 | 0.460 | 104 | 24 | 124 |
| level3 | 1000 | 0.296 | 60 | 8 | 148 |
| expander (retired) | 875 | 0.266 | 63 | 8 | 181 |
| rusher (retired) | 855 | 0.250 | 54 | 18 | 180 |
| sentinel (retired) | 830 | 0.230 | 52 | 12 | 188 |
| level2 | 795 | 0.148 | 29 | 6 | 181 |
| level1 | 506 | 0.037 | 0 | 16 | 200 |

Holdout maps (`iteration-7-holdout`, 1,020 matches):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| frontline | 2111 | 0.929 | 130 | 0 | 10 |
| speed_margin | 2009 | 0.879 | 123 | 0 | 17 |
| contested_speed | 1934 | 0.836 | 113 | 8 | 19 |
| reinforce_timeline | 1811 | 0.757 | 103 | 6 | 31 |
| contested_stage | 1758 | 0.721 | 101 | 0 | 39 |
| reinforce_contested (retired) | 1654 | 0.650 | 88 | 6 | 46 |
| economist_reinforce | 1568 | 0.593 | 79 | 8 | 53 |
| economist_contested (retired) | 1501 | 0.550 | 75 | 4 | 61 |
| economist (retired) | 1403 | 0.493 | 67 | 4 | 69 |
| level3 | 1000 | 0.196 | 22 | 3 | 95 |
| sentinel (retired) | 882 | 0.232 | 29 | 7 | 104 |
| rusher (retired) | 824 | 0.200 | 25 | 6 | 109 |
| expander (retired) | 798 | 0.186 | 26 | 0 | 114 |
| level2 | 737 | 0.092 | 10 | 2 | 108 |
| level1 | 409 | 0.017 | 0 | 4 | 116 |

**Champion:** `frontline`, 1668 on the training maps and 2111 on the holdout maps (iteration 6's champion, `speed_margin`, was 1557 and 2010; 1517 and 2009 in this tournament).

**Where the champion still loses (training maps):** `claw`, the official map, against `contested_stage` (90 and 91 turns) and `level3` (119), both sides; `circle` against `expander` in 12 turns, both sides, and draws at the limit there against five bots; `crossing` against `contested_speed` (123), both sides; `far-shores` against `speed_margin` (141); `islands` against `reinforce_timeline` at the limit, both sides.

**Next:** `claw`, where the champion loses four games and the real games are played.

**After the iteration**, `frontline` played the same hosted bot in a lobby on `claw`, from the same side as the real game above, and won as the last team standing in 92 turns (8 castles and 315 soldiers to 0), with no failed turn. It took the middle castle 2 four times and lost it three; the game turned from turn 73, when its strikes took castles 6, 7 and the enemy's home castle 1 in eleven turns. Its production was 10 to 10 on turn 51 and 15 to 12 on turn 81: unlike `speed_margin`, it never fell behind in castles after turn 41.

## Iteration 8: holding neutrals, and the finish

**Date:** 2026-11-21. **Maps:** 9 training, 5 holdout (unchanged). **Matches:** 2,700 in the training selection round robin, 1,330 in the holdout selection; the final standings are 1,836 training and 1,020 holdout matches. No separate baseline was played: iteration 7's final standings (`iteration-7-train`) are this commit's, with nothing changed in between.

The goal given for this and the next iterations is to beat two real opponents on every map: the hosted bot of iteration 7's real games, and a player's bot that plays here in the headless runner from its own project (above). `frontline` beat the player's bot 18 times in 28 games, drew 2 and lost 8 (`delta`, `islands` and the holdout maps `atoll` and `ridge`, each on both sides; `circle` drawn); against the hosted bot it had won `claw` and `archipelago`, drawn `circle` at the limit (1,142 soldiers to 1,141) and lost `crossing` in 129 turns. The findings come from the training maps only.

**Findings** (`frontline`'s games against the player's bot):

1. **The front starves the rear's production.** `delta`, turns 20 to 121: home castle 0 at production 3 logged `stage>6 0:11` or `0:12` every four turns and never held the 30 for level 4; production 6 against 8 to 19. `islands`: home castle at production 2 the whole game. **Idea (a):** a rear castle stages only once its production is at the top.
2. **It never finishes a level game.** `circle`, turns 30 to 300: production 4 each, a lead of 16 to 46 soldiers, "saving" every turn: the strike needed 1.5 times the defenders. **Idea (b):** near the turn limit a strike counts the target exactly, its burst included.
3. **It wears neutrals down for the enemy and tops up in groups of 1.** `delta`, turns 21 to 29: `0->3:1` eight turns running at a neutral of 25, 8 units away; the opponent took it on turn 29 with 1 soldier. **Idea (c):** iteration 7's landing simulation, for neutral targets: take only what stays the bot's after every known landing.

**Candidates:**

| Candidate | Parent | Idea | Training rating (parent's) | Against parent | Holdout rating (parent's) | Decision |
|---|---|---|---|---|---|---|
| `frontline_hold` | frontline | A neutral castle is taken only with what leaves it the bot's after every known landing on it, own and enemy, in order; no top-ups that land alone. | 1661 (1635) | 9.5/18 | 2134 (2122) | **promoted** |
| `frontline_finish` | frontline | Near the turn limit a strike counts the target exactly, its soldiers, growth, burst and reinforcements, instead of with the margin, so a level game is finished instead of drawn. | 1642 (1635) | 10/18 | 2198 (2122) | **promoted** |
| `frontline_economy` | frontline | A rear castle stages its spare soldiers at the front only once its production is at the top level: production first, then the front. | 1579 (1635) | 7/18 | not played | **rejected**: below its parent in both rules (34/34 on `delta`, but 25/34 on `archipelago` and 26/34 on `islands`). |

All three passed the gate: no failed turn, slowest turns 14.4, 17.6 and 20.1 ms.

Against the player's bot (28 games each, not a selection rule): `frontline_hold` 20 wins, 2 draws, 6 losses (it won `ridge`); `frontline_finish` 20 wins, 8 losses (it won `circle`); `frontline_economy` 14 wins, 2 draws, 12 losses (it won `delta` and lost `archipelago`, `claw` and `crossing`).

**Status changes:** `frontline_hold` and `frontline_finish` are active; `frontline` stays active (neither candidate's row matches it everywhere). That made eight active bots: `economist_reinforce` (1211 in the selection) and then `reinforce_timeline` (1275), the lowest-rated active bots, are **retired**, each matched or beaten everywhere by a `frontline` bot. That made eight retired bots, so the two lowest-rated, `sentinel` (818) and `rusher` (843), are **deleted**. Active: `frontline_hold`, `frontline_finish`, `frontline`, `speed_margin`, `contested_speed`, `contested_stage`; retired: `reinforce_timeline`, `reinforce_contested`, `economist_reinforce`, `economist_contested`, `economist`, `expander`.

**Deleting two retired bots moved every rating:** with fewer weak opponents, `level1` fell from 506 to 333 on the training maps and every holdout rating rose by about 150 (`frontline` 2111 to 2270, against the same `level3`). The numbers below aren't comparable with earlier entries'; compare bots within this table.

Training maps (`iteration-8-train`, 1,836 matches):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| frontline_hold | 1665 | 0.859 | 204 | 25 | 23 |
| frontline_finish | 1656 | 0.853 | 203 | 24 | 25 |
| frontline | 1647 | 0.847 | 199 | 29 | 24 |
| speed_margin | 1493 | 0.726 | 169 | 28 | 55 |
| contested_speed | 1446 | 0.685 | 159 | 27 | 66 |
| contested_stage | 1363 | 0.607 | 143 | 20 | 89 |
| reinforce_timeline (retired) | 1289 | 0.536 | 123 | 24 | 105 |
| reinforce_contested (retired) | 1262 | 0.510 | 115 | 27 | 110 |
| economist_reinforce (retired) | 1224 | 0.474 | 104 | 31 | 117 |
| economist_contested (retired) | 1157 | 0.411 | 92 | 23 | 137 |
| economist (retired) | 1087 | 0.349 | 74 | 28 | 150 |
| level3 | 1000 | 0.181 | 38 | 2 | 176 |
| expander (retired) | 886 | 0.198 | 47 | 6 | 199 |
| level2 | 815 | 0.083 | 17 | 2 | 197 |
| level1 | 333 | 0.005 | 0 | 2 | 214 |

Holdout maps (`iteration-8-holdout`, 1,020 matches):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| frontline_finish | 2345 | 0.900 | 126 | 0 | 14 |
| frontline_hold | 2282 | 0.864 | 119 | 4 | 17 |
| frontline | 2270 | 0.857 | 118 | 4 | 18 |
| speed_margin | 2140 | 0.771 | 108 | 0 | 32 |
| contested_speed | 2060 | 0.714 | 96 | 8 | 36 |
| reinforce_timeline (retired) | 1936 | 0.621 | 84 | 6 | 50 |
| contested_stage | 1879 | 0.579 | 81 | 0 | 59 |
| reinforce_contested (retired) | 1791 | 0.514 | 69 | 6 | 65 |
| economist_reinforce (retired) | 1730 | 0.471 | 62 | 8 | 70 |
| economist_contested (retired) | 1642 | 0.414 | 56 | 4 | 80 |
| economist (retired) | 1554 | 0.364 | 49 | 4 | 87 |
| level3 | 1000 | 0.067 | 8 | 0 | 112 |
| level2 | 882 | 0.050 | 6 | 0 | 114 |
| expander (retired) | 815 | 0.114 | 16 | 0 | 124 |
| level1 | 296 | 0.000 | 0 | 0 | 120 |

**Champion:** `frontline_hold`, 1665 on the training maps (`frontline` 1647 in the same table); `frontline_finish` leads the holdout maps.

**Where the champion still loses:** to the player's bot on `delta`, `islands` and `atoll`, with `circle` drawn; the hosted bot's `crossing` and `circle`. In the league, `circle` (21/34 for every `frontline` bot).

**Next:** the two promoted ideas together (`frontline_hold` with `frontline_finish`'s finish), then the starved rear in a form the league doesn't punish.
