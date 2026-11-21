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
- **A bot that only attacks what one castle affords alone never finishes.** Once the enemy's last castle holds more than any one of its castles can beat with the margin, it waits: the economist held 1,100 soldiers in 7 castles for 80 turns against one castle of 130 to 280 on `claw`. Sending every idle castle's spare soldiers at once, sized for the farthest group, was worse (iteration 1's `economist_pool`, 5 of 18 points against its parent); a finish that works is still to be found.

From a real game between two players' bots on the official map, `claw` (2026-11-21, 195 turns; read with `league digest`, not played here):

- **Production is the entry fee, not an edge.** By turn 100 seven of the eight castles were at production level 4 and the eighth at 3, and the game stood at four castles each from turn 62 to turn 149. The league's founders, the economist apart, never buy production; a bot that only out-produces the default bots has not met a real opponent yet.
- **Short lines beat long walks.** The winner sent its soldiers 4.4 units on average and the loser 6.0. The winner moved every castle's production forward to a front castle every three turns (2,062 of its 3,373 soldiers sent went to its own castles), and its last strikes, of 74 to 98 soldiers, left from that castle. The loser attacked castles 6 to 8.2 units from where its soldiers stood, 12 to 17 turns of walking at speed level 1.
- **A defender that sees a long attack coming out-reinforces it.** On turn 53 the loser sent 84 soldiers at a castle that held 25, 8.2 units away. The defender added soldiers from two castles within 3.2 units and held 115 the turn before they arrived. Counting a target's defenders as its soldiers plus its growth is wrong for a walk of 17 turns: count what its owner can bring within the travel time.
- **Trickles lose to stacks.** After that, the loser kept sending groups of 9 to 21 from two castles at the same castle. They arrived one at a time and each lost alone.
- **The lightly held castle on the border decides a level game.** The castle at (0, -3) was captured four times, usually held under 20 soldiers while the stacks stood elsewhere, and its last capture, on turn 149, made production 19 against 12; the game ended 46 turns later.
- **Clashes trade one for one** (687 soldiers lost on each side), so nothing is won in the field: a group sent out of a castle at an arriving stack only delays it, when it is at least half the stack's size.
- **Neither bot bought speed**, in a game where attacks walked 12 to 17 turns. Whether speed level 2, for 10 soldiers, pays on a map this size is untested.

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
