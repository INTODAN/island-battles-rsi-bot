# The league's ledger

One entry per iteration, newest last. An entry says what was measured, what was tried, what was kept and what was learned, so that the next session starts from here and doesn't try a rejected idea again. Ratings have `level3` at 1000.

## Lessons so far

Short, general statements about the game that the games have shown. Add to them, and correct them when a later game says otherwise.

- On `circle` (two castles 4 apart, no neutral castles) a bot that spends its first soldiers on upgrades loses to one that sends everything at once: 32 soldiers arrive on turn 11, before production level 3 has paid for itself.
- Production upgrades pay on most maps with neutral castles: the economist, which does nothing else cleverly, beats default level 3 in 24 of 28 games. `islands` was the exception (4 of 12 points there), and the cause wasn't production but holding: see the next lesson.
- **A castle taken with 1 soldier near the enemy falls unless another castle reinforces it.** A bot that never sends soldiers to its own castles loses them to groups of 8 to 15 while its home castle holds 15 to 20 two or three units away and waits. Reinforcing a castle that would fall, from castles whose groups land before the attack, took the economist line from 4 to 14 of 16 points on `islands` and from 1108 to 1271 overall (iteration 1).
- **Castles that choose their targets independently in one turn send twice at one target** (two groups of 21 at a neutral of 20), and a neutral that an enemy group is already walking to is a different target: it will be an enemy castle, or a weakened neutral, when yours lands. Counting both is worth about 90 rating points (iteration 1).
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
