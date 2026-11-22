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
- **A neutral castle's soldiers are certain; a margin on them leaves big neutrals to the enemy.** With 1.4 times a neutral's own soldiers, a neutral of 25 cost 36 from one castle, and two of them stayed neutral next to `frontline`'s front for 130 turns on `delta`. Paying them exactly won `delta`, `islands` and `atoll` against the player's bot (24 of 28 games against 20), but lost the mirror match to its parent 5 of 18 (iteration 9's `hold_exact`): cheaper neutrals were taken thinner and fell. The idea needs the holding to come with it.
- **Pay a neutral exactly only where the enemy can't strike it back.** Paying every neutral exactly took castles with 1 soldier next to the enemy and lost them (iteration 9's `hold_exact`, 5 of 18 against its parent); paying exactly only neutrals that no enemy castle is nearer to than the attacker beat its parent 10 of 18 and was promoted (iteration 10's `finish_safe`), and beat the player's bot in 24 of 28 games.
- **Speed for the rear pays.** Buying speed level 2 in a rear castle before its first batch to the front, instead of after its production tops out, beat its parent 12 of 18 (iteration 10's `finish_speed`): soldiers that walk half as long are soldiers that fight.
- **A front that buys nothing is a front that loses.** Keeping the front castle's soldiers for strikes alone, with no production or speed bought there, lost to its parent 1 of 18 (iteration 10's `finish_front`): the front is where the staged soldiers are, and the levels they buy there pay even when the castle later falls.
- **A castle taken exactly must also outlast the next enemy castle along.** "No enemy castle nearer than the attacker" wasn't safe: `finish_safe` took castles with 1 soldier on `strait` and lost them within one to five turns to enemy castles a little farther away. Adding to an exact price what the enemy castles within five turns of the capture could send, less the castle's growth, beat its parent 14 of 20 and rose 198 points on the holdout maps (iteration 13's `safe_hold`).
- **Landing every castle's group on one turn is not enough without a front.** A founder that plans waves, each castle launching on the turn that lands its group with the others', beat the champion 11 of 20 head to head but rated 220 below it: without staging its castles walk long and its rear never fights (iteration 13's `converge`, 8 of 34 points on `islands`).
- **Rear speed for long walks wins the real opponents and loses the holdout maps.** Buying speed in rear castles whose walk to the front is over 8 turns beat its parent 16 of 26 and the player's bot 34 of 42 games, the best of any bot, but fell 91 points below its parent on the holdout maps (iteration 17's `hold_speedfar`; `skerry` 17/30 against 22, `twin-keeps` 23 against 29). Three candidates have now risen on training and fallen on holdout (`margin_landings`, `hold_retake`, `hold_speedfar`).
- **Local fronts shorten the lines and win the training maps, not yet the holdout maps.** Staging each rear castle to its own nearest castle nearer the enemy, instead of to one front, beat its parent 21 of 28, its best mirror score since iteration 9, and rose 63 points on training (`crossing` 32/34 against 22, `sound` 30 against 21), but lost 25 on holdout (`scatter` 22/32 against 28; iteration 18's `hold_localfront`). Four candidates have now risen on training and fallen on holdout.
- **A holdout set that gates every promotion stops being held out.** Six candidates in a row (iterations 16 to 19) rose on the training maps, beat their parent head to head, and fell below it on the holdout maps. On iteration 19's new holdout map `key`, which no bot was ever selected on, both candidates beat the champion (26 and 27 points against 25); on `lagoon`, part of every holdout gate since iteration 13, the champion led them 28 to 22 and 18. A champion is partly the bot that happened to fit the holdout maps it passed, and its descendants regress from that fit. Fresh holdout maps restore the test; a rejected idea retried on them must still come in another form. *Not always the explanation (iteration 20):* `opener_safe` also lost both brand-new holdout maps, `tor` (20 points against 26) and `wick` (24 against 26).
- **`circle` is won by waiting for the enemy to spend its home.** Every `frontline` bot and the hosted bot buy production 2 and 3 by turn 3, leaving their only castle with 7 soldiers; a bot that buys nothing for 12 turns and strikes the first enemy castle it can take with a speed-2 group took 30 of 34 points on `circle` against its parent's 19 (iteration 21's `ambush`). Everywhere else the same waiting lost (1446 against 1798).
- **A castle that waits for a better neutral must stop staging too.** Waiting up to four turns of production for the best-value neutral passed every league rule (iteration 22's `hold_bestneutral`: 18 of 34 against its parent, 31 points up on training and 32 on holdout) and then won 1 of 17 lobby games against the hosted bot, against the champion's 4: the waiting castle kept sending its batches of 10 to the front (`wait>4` for 17 turns on `archipelago` while `stage>10 0:10` went on), so it waited without saving and lost the race the idea was for.
- **Stopping the waiting castle's staging doesn't save the idea.** Iteration 23's `hold_waitnostage` waited for the best neutral and kept the waiting castle out of strikes and staging: 10 of 34 against its parent, 92 points below it, and no win against the hosted bot. Waiting for a neutral loses the league's races whatever the waiting castle does meanwhile.
- **The hosted bot is a moving target.** The champion that won 4 of 17 lobby games against it on 2026-11-21 won none of the same 17 on 2026-11-22, and lost `circle` in 17 turns where it had drawn at the limit (iteration 23). A record against an opponent someone else maintains holds for the session it was played in.
- **An upgrade beside a stocked enemy castle hands it over.** On `circle` (2026-11-22) the champion bought production 4 at 34 soldiers, down to 8, with the hosted bot's castle 4 units away holding 34; that turn the hosted bot bought speed 2 and sent 25, its growth on the way counted exactly, and took the castle on turn 17. The league's bots never strike a castle for its upgrade, so nothing in the league punishes this.
- **Strike exactly when the walk is short.** Counting a target's soldiers, growth, reinforcements and burst exactly (plus 2) for strikes that land within five turns, instead of 1.5 times them, beat its parent 26 of 34, its best mirror score since iteration 7, and rose 83 points on training and 29 on holdout (iteration 24's `hold_exactstrike`). Over a short walk little can change before the landing, and a margin there only lets the target grow back.
- **Guarding upgrades costs the league and buys the real games.** Skipping an upgrade that would leave the castle to a single enemy castle (at speed 2) took the only draws and the only win any bot got from the hosted bot on 2026-11-22 (`circle` drawn by three such candidates, `claw` won by one), and lost to its parent 10 to 14 of 34 in the league (iteration 24). `ori_mimic` doesn't punish an upgrade the way the hosted bot does: the candidates that guarded most scored worst against it.
- **The real opponent's own rules, with the league's lessons added, beat the league's best line.** Founders written on `ori_mimic`'s code (the hosted bot's rules read off its games) took the top of both tables in iteration 25: `ori_hold` (helpers under attack may help if they still hold, and a capture the enemy would retake is topped up) and `ori_finish` (strikes over a short walk or near the turn limit count the target exactly) beat their parent 17.5 and 18.5 of 34, rated 1876 and 1855 against its 1836 on training and 1969 and 2020 against 1938 on holdout, and won 58 of 60 games against the player's bot with no loss (2 draws on `circle`). Against the hosted bot itself they won 2 and 1 of 17 games on the board, where every bot of the line before them won none.
- **Burst levels cost a mirror match its race.** Buying burst levels 2 and 3 on a castle near the enemy (30 soldiers) to burst when an attack would take it lost to the parent 2 of 34 (iteration 25's `exact_burst`): the purchase came at the turn the front's soldiers decided the race, and no league bot's strike ever met a burst it hadn't counted.
- **A lobby win by the opponent's timeout is not a win.** In long games the hosted bot sometimes failed to answer within 30 seconds and forfeited (7 of 85 games in iteration 25); a tab that the browser slows can make our bot forfeit too (2). Count only games decided on the board.
- **Ideas that lose the league can win the player's bot.** In iteration 23 the order of six candidates against the player's bot (54, 51, 48, 46, 46 and 40 wins of 60) was nearly the reverse of their order in the league; the bot that waited longest to strike (`hold_opening`, 7 of 34 against its parent) won the most.
- **The race for castles decides the league; production decides the real games.** Saving rear castles' soldiers for production once no neutral castle is on the bot's side lost to its parent 8 of 18 (iteration 9's `hold_phase`), as iteration 8's `frontline_economy` did; both real opponents still out-produce every `frontline` bot (the hosted bot reached production 4 at home by turn 44 on `crossing`, while the `frontline` bots stayed at 2 until turn 90).
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

## Iteration 9: the finish, on the champion

**Date:** 2026-11-21. **Maps:** 9 training, 5 holdout (unchanged). **Matches:** 2,700 in the training selection round robin, 1,170 in the holdout selection; the final standings are 1,836 training and 1,020 holdout matches. The baseline is iteration 8's final standings, the same commit.

Real games since iteration 8, against the hosted bot in a lobby on the league's map files (one side each, Blue): `frontline` won `archipelago` (115 turns), drew `circle` at the limit (1,142 soldiers to 1,141) and lost `crossing` (129); `frontline_hold` lost `crossing` (108) and `delta` (107).

**Findings:**

1. **The two promoted ideas of iteration 8 are in different bots.** `frontline_finish` wins `circle` against the player's bot; `frontline_hold` wins `ridge`. **Idea (a):** the finish grafted into the champion.
2. **The rear never buys production after the race is over.** The hosted bot's `crossing` game against `frontline_hold`: home castle 0 at production 2 until turn 90, the hosted bot's home at 4 by turn 44; the staged soldiers bought production 4 and speed at the front castle 8 instead, which changed hands twelve times and was lost on turn 87. **Idea (b):** once no neutral castle is on the bot's side, rear castles save for production before staging.
3. **Neutrals of 25 next to the front stay neutral.** `delta` against the player's bot, turns 30 to 130: castles 2 and 4, 2 units from the front castle 6, needed 36 each from one castle under the 1.4 margin on their own soldiers. **Idea (c):** no margin on a neutral's own soldiers.

**Candidates:**

| Candidate | Parent | Idea | Training rating (parent's) | Against parent | Holdout rating (parent's) | Decision |
|---|---|---|---|---|---|---|
| `hold_finish` | frontline_hold | Graft from frontline_finish: near the turn limit a strike counts the target exactly, its soldiers, growth, burst and reinforcements, instead of with the margin. | 1717 (1661) | 15/18 | 2296 (2296) | **promoted** |
| `hold_exact` | frontline_hold | A neutral castle's own soldiers are certain: the margin covers only the enemy groups that may land on it, not what it holds. | 1684 (1661) | 5/18 | not played | **rejected**: lost to its parent head to head, though it rated above it (34/34 on `archipelago` and `gyre`, 24/34 on `delta` and `strait`). Against the player's bot it won 24 of 28 games, the most of any bot. |
| `hold_phase` | frontline_hold | Once no neutral castle is nearer an own castle than every enemy castle, a rear castle saves for its next production level before it stages at the front. | 1627 (1661) | 8/18 | not played | **rejected**: below its parent in both rules. |

All three passed the gate: no failed turn, slowest turns 12.7, 11.9 and 16.9 ms.

Against the player's bot (28 games each): `hold_exact` 24 wins, 2 draws, 2 losses (it lost only `shoals`, and drew `circle`); `hold_finish` 22 wins, 6 losses (`delta`, `islands`, `atoll`); `hold_phase` and `frontline_hold` 20, 2, 6.

**Status changes:** `hold_finish` is active; `frontline_hold` stays active (`hold_finish`'s row doesn't match it everywhere). With seven active bots, `contested_stage` (1359 in the selection), the lowest-rated active bot, is **retired**: `hold_finish`'s row beats it everywhere. That made seven retired bots, so `expander` (927), the lowest-rated, is **deleted**. Active: `hold_finish`, `frontline_finish`, `frontline`, `frontline_hold`, `speed_margin`, `contested_speed`; retired: `contested_stage`, `reinforce_timeline`, `reinforce_contested`, `economist_reinforce`, `economist_contested`, `economist`.

**The holdout scale has lost its anchor:** the default bots win no holdout game now, so the fit puts `level1`, `level2` and `level3` all at 1000 and the other ratings float. Compare holdout ratings within one table only.

Training maps (`iteration-9-train`, 1,836 matches):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| hold_finish | 1764 | 0.851 | 200 | 29 | 23 |
| frontline_finish | 1725 | 0.823 | 191 | 33 | 28 |
| frontline | 1720 | 0.819 | 191 | 31 | 30 |
| frontline_hold | 1704 | 0.808 | 190 | 27 | 35 |
| speed_margin | 1552 | 0.679 | 156 | 30 | 66 |
| contested_speed | 1494 | 0.625 | 143 | 29 | 80 |
| contested_stage (retired) | 1420 | 0.556 | 129 | 22 | 101 |
| reinforce_timeline (retired) | 1344 | 0.484 | 109 | 26 | 117 |
| reinforce_contested (retired) | 1307 | 0.450 | 99 | 29 | 124 |
| economist_reinforce (retired) | 1277 | 0.423 | 90 | 33 | 129 |
| economist_contested (retired) | 1194 | 0.351 | 76 | 25 | 151 |
| economist (retired) | 1127 | 0.298 | 60 | 30 | 162 |
| level3 | 1000 | 0.102 | 22 | 0 | 194 |
| level2 | 805 | 0.037 | 8 | 0 | 208 |
| level1 | 299 | 0.000 | 0 | 0 | 216 |

Holdout maps (`iteration-9-holdout`, 1,020 matches):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| frontline_finish | 2522 | 0.886 | 122 | 4 | 14 |
| frontline | 2452 | 0.843 | 116 | 4 | 20 |
| hold_finish | 2431 | 0.829 | 113 | 6 | 21 |
| frontline_hold | 2431 | 0.829 | 113 | 6 | 21 |
| speed_margin | 2264 | 0.707 | 99 | 0 | 41 |
| contested_speed | 2181 | 0.643 | 86 | 8 | 46 |
| reinforce_timeline (retired) | 2062 | 0.550 | 74 | 6 | 60 |
| contested_stage (retired) | 2007 | 0.507 | 71 | 0 | 69 |
| reinforce_contested (retired) | 1922 | 0.443 | 59 | 6 | 75 |
| economist_reinforce (retired) | 1882 | 0.414 | 54 | 8 | 78 |
| economist_contested (retired) | 1774 | 0.343 | 46 | 4 | 90 |
| economist (retired) | 1684 | 0.293 | 39 | 4 | 97 |
| level1 | 1000 | 0.000 | 0 | 0 | 120 |
| level2 | 1000 | 0.000 | 0 | 0 | 120 |
| level3 | 1000 | 0.000 | 0 | 0 | 120 |

**Champion:** `hold_finish`, 1764 on the training maps (`frontline_hold` 1704 in the same table).

**Where the champion still loses:** to the player's bot on `delta`, `islands` and `atoll`; to the hosted bot on `crossing` and `delta` (as `frontline_hold`). In the league, `circle` (19/34 for every `frontline` bot) and `archipelago` (29/34).

**Next:** `hold_exact`'s exact neutrals, with what makes a cheap neutral hold: why it lost the mirror match is unread. The starved rear against the real opponents, in a form the race for castles allows.

## Iteration 10: safe neutrals and a fast rear

**Date:** 2026-11-21. **Maps:** 9 training, 5 holdout (unchanged). **Matches:** 2,700 in the training selection round robin, 1,330 in the holdout selection; the final standings are 1,836 training and 1,020 holdout matches. The baseline is iteration 9's final standings, the same commit.

Real games since iteration 9, against the hosted bot in a lobby (Blue): `hold_finish` lost `far-shores` in 116 turns.

**Findings:**

1. **`hold_exact` lost its parent's games by taking castles with 1 soldier next to the enemy.** `strait`, iteration 9's mirror game (57 turns): castles 6, 7 and 4 taken with 1 soldier on turns 16, 34 and 45, each lost within two to ten turns to the castle across the line. **Idea (a):** pay exactly only the neutrals no enemy castle is nearer to than the attacker.
2. **The rear's soldiers walk at speed level 1 for the whole game.** The hosted bot's `far-shores` game against `hold_finish`: up to 164 of its soldiers walking on turn 71 against the hosted bot's 63; its rear castles bought speed only once their production was at the top, which they never reached (home castle 0 at production 2 until turn 83; the hosted bot's home at 4 and speed 2 by turn 40). **Idea (b):** a rear castle buys speed before its first batch.
3. **The staged soldiers buy levels at the front, which then falls.** The hosted bot's `crossing` game against `frontline_hold`: front castle 8 bought production 1 to 4 and speed on turns 70 to 75 and was lost on turn 87. **Idea (c):** the front buys nothing.

**Candidates:**

| Candidate | Parent | Idea | Training rating (parent's) | Against parent | Holdout rating (parent's) | Decision |
|---|---|---|---|---|---|---|
| `finish_safe` | hold_finish | A neutral castle that no enemy castle is nearer to than the attacking castle is paid exactly; the margin on its own soldiers stays only for contested neutrals. | 1849 (1778) | 10/18 | 2562 (2428) | **promoted** |
| `finish_speed` | hold_finish | A rear castle buys speed level 2 before it stages its first batch, so its batches walk to the front twice as fast. | 1839 (1778) | 12/18 | 2572 (2428) | **promoted** |
| `finish_front` | hold_finish | The front castle buys neither production nor speed: what is staged there is for strikes. | 1402 (1778) | 1/18 | not played | **rejected**: below its parent in both rules. |

All three passed the gate: no failed turn, slowest turns 11.1, 10.3 and under 20 ms.

Against the player's bot (28 games each): `finish_safe` 24 wins, 4 losses (`islands`, `shoals`); `hold_finish` 22 and 6 (`delta`, `islands`, `atoll`); `finish_speed` 20 and 8; `finish_front` 8 and 20.

**Status changes:** `finish_safe` and `finish_speed` are active; `hold_finish` stays active (neither row matches it everywhere). With eight active bots, `contested_speed` (1503 in the selection) and then `speed_margin` (1558), the lowest-rated, are **retired**: `finish_safe`'s row beats each everywhere. That made eight retired bots, so the two lowest-rated, `economist` (1166) and `economist_contested` (1203), are **deleted**. Active: `finish_speed`, `finish_safe`, `hold_finish`, `frontline_hold`, `frontline_finish`, `frontline`; retired: `speed_margin`, `contested_speed`, `contested_stage`, `reinforce_timeline`, `reinforce_contested`, `economist_reinforce`.

Training maps (`iteration-10-train`, 1,836 matches):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| finish_speed | 1881 | 0.833 | 199 | 22 | 31 |
| finish_safe | 1881 | 0.833 | 199 | 22 | 31 |
| hold_finish | 1805 | 0.772 | 180 | 29 | 43 |
| frontline_hold | 1756 | 0.728 | 170 | 27 | 55 |
| frontline_finish | 1756 | 0.728 | 167 | 33 | 52 |
| frontline | 1751 | 0.724 | 167 | 31 | 54 |
| speed_margin (retired) | 1592 | 0.575 | 131 | 28 | 93 |
| contested_speed (retired) | 1519 | 0.508 | 114 | 28 | 110 |
| contested_stage (retired) | 1452 | 0.448 | 102 | 22 | 128 |
| reinforce_timeline (retired) | 1392 | 0.397 | 88 | 24 | 140 |
| reinforce_contested (retired) | 1324 | 0.343 | 73 | 27 | 152 |
| economist_reinforce (retired) | 1313 | 0.335 | 70 | 29 | 153 |
| level3 | 1000 | 0.046 | 10 | 0 | 206 |
| level2 | 879 | 0.023 | 5 | 0 | 211 |
| level1 | 454 | 0.000 | 0 | 0 | 216 |

Holdout maps (`iteration-10-holdout`, 1,020 matches; the default bots win nothing, so the scale floats):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| finish_speed | 2409 | 0.843 | 118 | 0 | 22 |
| finish_safe | 2399 | 0.836 | 117 | 0 | 23 |
| frontline_finish | 2361 | 0.807 | 111 | 4 | 25 |
| frontline | 2307 | 0.764 | 105 | 4 | 31 |
| hold_finish | 2263 | 0.729 | 99 | 6 | 35 |
| frontline_hold | 2263 | 0.729 | 99 | 6 | 35 |
| speed_margin (retired) | 2086 | 0.579 | 81 | 0 | 59 |
| contested_speed (retired) | 2008 | 0.514 | 69 | 6 | 65 |
| reinforce_timeline (retired) | 1925 | 0.450 | 61 | 4 | 75 |
| contested_stage (retired) | 1846 | 0.393 | 55 | 0 | 85 |
| economist_reinforce (retired) | 1758 | 0.336 | 44 | 6 | 90 |
| reinforce_contested (retired) | 1708 | 0.307 | 41 | 4 | 95 |
| level1 | 1000 | 0.000 | 0 | 0 | 120 |
| level2 | 1000 | 0.000 | 0 | 0 | 120 |
| level3 | 1000 | 0.000 | 0 | 0 | 120 |

**Champion:** `finish_speed`, 1881 on the training maps, level with `finish_safe`, and first on the holdout maps (2409 to 2399).

**Where the champion still loses:** to the player's bot on 4 maps of 14, both sides (`archipelago`, `claw`, `gyre`, `twin-keeps`), where `finish_safe` wins; `finish_safe` loses `islands` and `shoals`. Against the hosted bot, `crossing`, `delta` and `far-shores` are lost by the earlier champions and not yet played by these two.

**Next:** the two promoted ideas together, and the hosted bot's maps with the new champion.

## Iteration 11: nothing promoted

**Date:** 2026-11-21. **Maps:** 9 training, 5 holdout (unchanged). **Matches:** 2,700 in the training selection round robin; no holdout selection (no candidate passed); the final standings are iteration 10's, all from the cache.

**Findings** (`finish_safe`'s and `finish_speed`'s games against the player's bot on `islands`, which both lost or nearly lost):

1. **Strikes become trickles.** `islands`, turns 20 to 30: castles 0 and 2 sent groups of 1 to 8 at castle 5 every turn, which the player's bot met one at a time with groups of 2 to 9 (136 soldiers lost in clashes). **Cause:** a strike takes the bot's groups already walking off what the target needs, so every turn's new spare soldiers follow as a top-up. **Idea (b):** one strike at a time per target.
2. **Strikes come before neutrals, so neutrals on the bot's own side stay neutral.** Same game, turns 11 to 110: castles 4 (15 soldiers) and 6 (20), both nearer the bot than the enemy, stayed neutral while two castles at production 2 fed the strikes; production 4 for 100 turns against 4 to 18. **Idea (c):** neutrals before strikes.
3. **`finish_safe` and `finish_speed` win different maps against the player's bot** (`archipelago`, `claw`, `gyre` and `twin-keeps` for `finish_safe`; `islands` and `shoals` for `finish_speed`). **Idea (a):** the safe neutrals grafted into `finish_speed`.

**Candidates:**

| Candidate | Parent | Idea | Training rating (parent's) | Against parent | Decision |
|---|---|---|---|---|---|
| `speed_safe` | finish_speed | Graft from finish_safe: a neutral castle that no enemy castle is nearer to than the attacking castle is paid exactly; contested neutrals keep the margin. | 1867 (1896) | 9/18 | **rejected**: half against its parent and rated below it. Against the player's bot it won 24 of 28 games (`archipelago` and `far-shores` lost). |
| `speed_onestrike` | finish_speed | One strike at a time: a target the bot's groups are already walking to isn't struck again until they land. | 1828 (1896) | 8/18 | **rejected**: below its parent in both rules. |
| `speed_expandfirst` | finish_speed | Neutrals before strikes: each castle takes the neutral castle it can afford before its spare soldiers join a strike. | 1849 (1896) | 7/18 | **rejected**: below its parent in both rules. |

All three passed the gate: no failed turn, slowest turns 10.1, 13.4 and 15.2 ms. None played the holdout maps.

**Status changes:** none. **Standings:** iteration 10's (`iteration-11-train`, `iteration-11-holdout`). **Champion:** `finish_speed`, 1881, level with `finish_safe` (in this iteration's selection, with the candidates in the field, `finish_safe` led 1919 to 1896).

**What this says:** for the second time (`hold_exact` in iteration 9, `speed_safe` now) a candidate that beat the player's bot more often than its parent was rejected by the league's mirror match. The league measures the bots against each other and three default bots; the real opponents reward holding and economy more than the league does.

## Iteration 12: nothing promoted

**Date:** 2026-11-21. **Maps:** 9 training, 5 holdout (unchanged). **Matches:** 2,700 in the training selection round robin; no holdout selection; the standings are iteration 10's.

Real games since iteration 11, against the hosted bot in a lobby (Blue): `finish_speed` won `islands` (62 turns), `strait` (68), `crossing` (123) and `far-shores` (110), lost `delta` (108) and drew `circle` at the limit (1,142 soldiers to 1,141, the same as `frontline`: on `circle` the hosted bot plays move for move as the `frontline` bots do).

**Findings:**

1. **Speed for a rear castle next to the front costs the race.** `islands`, `finish_speed` against `frontline` (lost in 75 turns): home castle 0 bought speed on turn 6, 25 soldiers to `frontline`'s 35 on turn 11; it lost to every `frontline` bot there. **Idea (a):** rear speed only for a walk to the front longer than 8 turns, the speed lesson's threshold.
2. **Help that would land late is never sent.** The hosted bot's `delta` game: castle 4 logged unheld from turn 76 and fell on turn 84 with 17 soldiers; the hosted bot holds what it takes with 5 to 9. **Idea (b):** help that lands up to three turns late, sized to retake.
3. **The front strikes while another castle falls.** Same game, turns 77 and 81: castle 2 struck castle 5 with 26 and 28 soldiers while castle 4 was unheld. **Idea (c):** no strike while an own castle is unheld.

| Candidate | Parent | Idea | Training rating (parent's) | Against parent | Decision |
|---|---|---|---|---|---|
| `speed_far` | finish_speed | A rear castle buys speed before staging only when its walk to the front is longer than SPEED_WALK turns. | 1872 (1894) | 9/18 | **rejected**: half against its parent, rated below it (30/34 on `islands`, parent 24; 25/34 on `claw`, parent 31). |
| `speed_retake` | finish_speed | A castle that would fall is also helped by castles whose groups land up to RETAKE_TURNS after the attack, sized to take it back. | 1843 (1894) | 11/18 | **rejected**: rated below its parent. |
| `speed_rescuefirst` | finish_speed | No strike while an own castle is short under attack and no help reaches it in time. | 1745 (1894) | 2/18 | **rejected**: below its parent in both rules. |

All three passed the gate (no failed turn, slowest turns 10.3, 10.4 and 13.0 ms). Against the player's bot: `speed_far` and `speed_retake` 22 of 28, `speed_rescuefirst` 20, the parent 20.

**Status changes:** none. **Champion:** `finish_speed`, unchanged.

**Next:** iterations 11 and 12 promoted nothing, so iteration 13 starts by adding a training and a holdout map, and one of its candidates is a founder.

## Iteration 13: more maps, and holding safe neutrals

**Date:** 2026-11-21. **Maps:** 10 training, 6 holdout: **the map set grew** before this iteration's first measurement, after two iterations that promoted nothing, with `reef` (training, `league new-map reef --seed 1301`: 6 castles, two neutrals of 8 and two of 5) and `lagoon` (holdout, seed 1302). Every rating moved with them. **Matches:** 2,040 in the baseline (`iteration-13-before`, 204 of them new), 3,000 in the training selection round robin, 1,326 in the holdout selection; the final standings are 2,040 training and 1,224 holdout matches. On the new baseline `finish_safe` (1906) leads `finish_speed` (1888), so it is the champion this iteration studies.

**Findings** (`finish_safe`'s games on the training maps):

1. **Safe neutrals are taken with 1 soldier and lost.** `strait`, against `frontline_hold` (lost in 69 turns): castle 6 taken on turn 27 with 1 and lost on turn 32; castle 4 taken on turn 36 with 1 and lost on turn 37; both had no enemy castle nearer than the attacker, but enemy castles a little farther struck them. **Idea (a):** an exact price must also outlast the enemy castles that could land within a few turns of the capture.
2. **`finish_speed` beats it on `islands` and `gyre`, both sides.** **Idea (b):** graft the rear speed.
3. **Founder** (two iterations without a promotion): the real opponents land their stacks together; **idea (c):** a bot built around waves whose groups land on one turn.

| Candidate | Parent | Idea | Training rating (parent's) | Against parent | Holdout rating (parent's) | Decision |
|---|---|---|---|---|---|---|
| `safe_hold` | finish_safe | A neutral paid exactly must also outlast what enemy castles could land on it within HOLD_TURNS after the capture. | 1921 (1854) | 14/20 | 2231 (2033) | **promoted** |
| `safe_speed` | finish_safe | Graft from finish_speed: a rear castle buys speed level 2 before it stages its first batch. | 1854 (1854) | 7/20 | not played | **rejected**: below its parent head to head, level in rating. It beat the player's bot 28 of 32. |
| `converge` | finish_safe (scaffolding) | A new strategy: no staging; the castles within reach of one enemy castle launch at different turns so that their groups land on it together. | 1632 (1854) | 11/20 | not played | **rejected**: rated 222 below its parent. |

All three passed the gate (no failed turn, slowest turns 11.0, 11.2 and 10.3 ms). Against the player's bot (32 games now, 16 maps): `safe_speed` 28 wins, 4 losses; `finish_safe` 26 and 6; `safe_hold` 24 and 8 (`islands`, `reef`, `lagoon`, `shoals`); `converge` 14, 2 draws, 16 losses.

**Status changes:** `safe_hold` is active; `finish_safe` stays active. With seven active bots, `frontline_hold` (1754 in the selection) is **retired**: `finish_speed`'s row matches or beats it everywhere. That made seven retired bots, so `economist_reinforce` (1328), the lowest-rated, is **deleted**. Active: `safe_hold`, `finish_safe`, `finish_speed`, `hold_finish`, `frontline_finish`, `frontline`; retired: `frontline_hold`, `speed_margin`, `contested_speed`, `contested_stage`, `reinforce_timeline`, `reinforce_contested`.

Training maps (`iteration-13-train`, 2,040 matches, exit 0):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| safe_hold | 1902 | 0.836 | 221 | 26 | 33 |
| finish_safe | 1849 | 0.793 | 209 | 26 | 45 |
| finish_speed | 1841 | 0.786 | 203 | 34 | 43 |
| hold_finish | 1768 | 0.720 | 183 | 37 | 60 |
| frontline_hold (retired) | 1727 | 0.680 | 173 | 35 | 72 |
| frontline_finish | 1727 | 0.680 | 170 | 41 | 69 |
| frontline | 1723 | 0.677 | 170 | 39 | 71 |
| speed_margin (retired) | 1602 | 0.561 | 141 | 32 | 107 |
| contested_speed (retired) | 1489 | 0.457 | 111 | 34 | 135 |
| contested_stage (retired) | 1407 | 0.389 | 98 | 22 | 160 |
| reinforce_timeline (retired) | 1346 | 0.343 | 82 | 28 | 170 |
| reinforce_contested (retired) | 1301 | 0.311 | 72 | 30 | 178 |
| level3 | 1000 | 0.042 | 10 | 0 | 230 |
| level2 | 879 | 0.021 | 5 | 0 | 235 |
| level1 | 454 | 0.000 | 0 | 0 | 240 |

Holdout maps (`iteration-13-holdout`, 1,224 matches, exit 0):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| safe_hold | 2216 | 0.935 | 157 | 0 | 11 |
| finish_safe | 2017 | 0.821 | 138 | 0 | 30 |
| finish_speed | 1968 | 0.786 | 128 | 8 | 32 |
| frontline_finish | 1905 | 0.738 | 118 | 12 | 38 |
| frontline | 1860 | 0.702 | 112 | 12 | 44 |
| hold_finish | 1831 | 0.679 | 107 | 14 | 47 |
| frontline_hold (retired) | 1831 | 0.679 | 107 | 14 | 47 |
| speed_margin (retired) | 1603 | 0.500 | 84 | 0 | 84 |
| contested_speed (retired) | 1478 | 0.411 | 67 | 4 | 97 |
| reinforce_timeline (retired) | 1451 | 0.393 | 65 | 2 | 101 |
| contested_stage (retired) | 1405 | 0.363 | 61 | 0 | 107 |
| reinforce_contested (retired) | 1187 | 0.244 | 40 | 2 | 126 |
| level3 | 1000 | 0.042 | 6 | 0 | 138 |
| level1 | 526 | 0.000 | 0 | 0 | 144 |
| level2 | 526 | 0.000 | 0 | 0 | 144 |

**Champion:** `safe_hold`, 1902 on the training maps and 2216 on the holdout maps (`finish_safe` 1849 and 2017 in the same tables).

**Where the champion still loses:** to the player's bot on `islands`, `reef`, `lagoon` and `shoals`.

## Iteration 14: nothing promoted

**Date:** 2026-11-21. **Maps:** 10 training, 6 holdout (unchanged). **Matches:** 3,000 in the training selection round robin; no holdout selection; the standings are iteration 13's.

**Findings** (`safe_hold`'s games):

1. **The rear never buys its own production while the front holds plenty.** `reef`, against the player's bot (lost in 150 turns): production 9 against 12 from turn 36 to the end; home castle 0 at production 3 from turn 11, castle 4 at 2, while front castle 2, at production 4 and speed 2, held 100 to 190 soldiers. **Idea (a):** once the front is at the top of production and holds more than any enemy castle, the rear keeps its soldiers for its own levels.
2. **The home behind the front is staged empty.** `strait`, against `frontline` (lost in 68 turns): home castle 0 held 18 on turn 39 and fell to one strike. **Idea (b):** a rear castle stages only what leaves it more than the nearest enemy castle holds.
3. **The margin keeps a rich front idle.** `reef` again: 150 to 190 soldiers in one castle against enemy castles of 50 to 113. **Idea (c):** when the bot's soldiers are 1.5 times the enemy's, strike exactly.

| Candidate | Parent | Idea | Training rating (parent's) | Against parent | Decision |
|---|---|---|---|---|---|
| `hold_rearfund` | safe_hold | Once the front castle's production is at the top and it holds more than the strongest enemy castle, rear castles keep their soldiers for their own production instead of staging. | 1861 (1899) | 10/20 | **rejected**: half against its parent, rated below it; it still lost `reef` to the player's bot. |
| `hold_stageguard` | safe_hold | A rear castle stages only what leaves it more soldiers than the nearest enemy castle holds. | 1792 (1899) | 7/20 | **rejected**: below its parent in both rules (16/34 on `claw` and `gyre`, parent 30). |
| `hold_rich` | safe_hold | When the bot's soldiers outnumber the enemy's by half again, a strike counts the target exactly instead of with the margin. | 1889 (1899) | 10/20 | **rejected**: half against its parent, rated below it. |

All three passed the gate (slowest turns 11.6, 10.7 and 9.9 ms). Against the player's bot each won 24 of 32 or fewer, as the parent did.

**Status changes:** none. **Champion:** `safe_hold`, unchanged.

## Iteration 15: nothing promoted

**Date:** 2026-11-21. **Maps:** 10 training, 6 holdout (unchanged). **Matches:** 3,000 in the training selection round robin; no holdout selection; the standings are iteration 13's.

**Findings** (`safe_hold`'s `islands` game against the player's bot, lost in 114 turns):

1. **Big neutrals need two castles, and expansion uses one.** Turns 11 to 110: two castles at production 2 each held 8 to 16 soldiers while neutrals of 15 and 20 on the bot's side stayed neutral. **Idea (a):** the castles nearest a neutral take it together when no one alone can.
2. **Strikes take every spare soldier, so production stops at level 2.** Same turns: production 4 for 100 turns; no castle held the 24 for level 3. **Idea (b):** a castle joins a strike only with what its next production level doesn't need.
3. **Strikes trickle.** 36 to 44 soldiers walking at castle 5 in groups of 1 to 8 at any time, 136 lost in clashes. **Idea (c):** one strike per target until it lands (iteration 11's `speed_onestrike`, on the new champion).

| Candidate | Parent | Idea | Training rating (parent's) | Against parent | Decision |
|---|---|---|---|---|---|
| `hold_poolneutral` | safe_hold | A neutral castle that no castle can afford alone is taken by the castles nearest it together. | 1759 (1916) | 8/20 | **rejected**: below its parent in both rules (16/34 on `islands`, parent 30). |
| `hold_strikefund` | safe_hold | A castle joins a strike only with the spare soldiers it doesn't need for its next production level. | 1944 (1916) | 8/20 | **rejected**: lost to its parent head to head, though it rated 28 above it (`claw` 32/34 and `crossing` 26/34, parent 27 and 20). |
| `hold_onestrike` | safe_hold | One strike at a time per enemy castle. | 1902 (1916) | 9/20 | **rejected**: below its parent in both rules; it beat the player's bot 26 of 32 (parent 24). |

All three passed the gate (slowest turns 11.6, 11.1 and 12.4 ms).

**Status changes:** none. **Champion:** `safe_hold`, unchanged.

**Next:** iterations 14 and 15 promoted nothing: iteration 16 adds maps and a founder. `hold_strikefund` is the second candidate in three iterations to rate above its parent and lose the mirror match; with 10 training maps the mirror match is 20 games, most of them decided the same way from both sides.

## Iteration 16: more maps, nothing promoted

**Date:** 2026-11-21. **Maps:** 11 training, 7 holdout: **the map set grew** before the first measurement, after two iterations without a promotion, with `shelf` (training, seed 1601, 8 castles) and `cays` (holdout, seed 1602, 13 castles). **Matches:** 2,244 in the baseline (`iteration-16-before`), 3,300 in the training selection, 1,442 in the holdout selection; the final standings are 2,244 training and 1,428 holdout matches. `safe_hold` stays the champion on the new baseline (1931).

**Findings:**

1. **Founder:** the player's bot, which beats every league bot on `islands` and `reef`, plans: it schedules launches from several castles to land together, ranks neutrals by return, keeps soldiers for its next level, reinforces and bursts to save castles, and punishes enemy castles that just weakened (its own log lines). **Idea (a):** a bot built that way, with no front.
2. **Late help is never sent** (iteration 12's finding 2, against the hosted bot on `delta`). **Idea (b):** retake, on the new champion.
3. **No league bot uses bursts to defend.** **Idea (c):** a castle that would fall with no help in time bursts when the burst saves it.

| Candidate | Parent | Idea | Training rating (parent's) | Against parent | Holdout rating (parent's) | Decision |
|---|---|---|---|---|---|---|
| `planner` | safe_hold (scaffolding) | A new strategy, after the player's bot: no front; every castle saves for its next production level, big neutrals are taken by several castles at once, and enemy castles by waves whose groups land on one turn. | 1505 (1852) | 5/22 | not played | **rejected**: below its parent in both rules (3/34 on `archipelago`). |
| `hold_retake` | safe_hold | A castle that would fall is also helped by castles whose groups land up to RETAKE_TURNS after the attack, sized to take it back. | 1884 (1852) | 14/22 | 2077 (2189) | **rejected**: its holdout rating is 112 below its parent's. |
| `hold_burstsave` | safe_hold | A castle that would fall with no help in time buys burst potential and bursts when the burst makes it hold. | 1852 (1852) | 11/22 | not played | **rejected**: it never fired; every game is its parent's. A burst of 4 for 10 soldiers is never worth it to a castle without burst levels, and the league's castles have none. |

All three passed the gate (slowest turns 23.7, 17.4 and 15.9 ms). Against the player's bot (36 games, 18 maps) every candidate but `planner` won 24, as the parent did; it now beats the league's bots on `shelf` and `cays` too.

**Status changes:** none.

Training maps (`iteration-16-train`, 2,244 matches, exit 0):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| safe_hold | 1931 | 0.847 | 247 | 28 | 33 |
| finish_safe | 1881 | 0.808 | 235 | 28 | 45 |
| finish_speed | 1839 | 0.773 | 217 | 42 | 49 |
| hold_finish | 1780 | 0.719 | 199 | 45 | 64 |
| frontline_hold (retired) | 1742 | 0.683 | 189 | 43 | 76 |
| frontline_finish | 1729 | 0.670 | 182 | 49 | 77 |
| frontline | 1725 | 0.667 | 182 | 47 | 79 |
| speed_margin (retired) | 1592 | 0.539 | 149 | 34 | 125 |
| contested_speed (retired) | 1521 | 0.474 | 129 | 34 | 145 |
| contested_stage (retired) | 1410 | 0.380 | 106 | 22 | 180 |
| reinforce_timeline (retired) | 1388 | 0.364 | 98 | 28 | 182 |
| reinforce_contested (retired) | 1316 | 0.312 | 80 | 32 | 196 |
| level3 | 1000 | 0.038 | 10 | 0 | 254 |
| level2 | 880 | 0.019 | 5 | 0 | 259 |
| level1 | 456 | 0.000 | 0 | 0 | 264 |

Holdout maps (`iteration-16-holdout`, 1,428 matches, exit 0):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| safe_hold | 2259 | 0.929 | 182 | 0 | 14 |
| finish_safe | 2096 | 0.837 | 164 | 0 | 32 |
| finish_speed | 2003 | 0.770 | 147 | 8 | 41 |
| frontline_finish | 1950 | 0.730 | 136 | 14 | 46 |
| hold_finish | 1918 | 0.704 | 131 | 14 | 51 |
| frontline | 1911 | 0.699 | 130 | 14 | 52 |
| frontline_hold (retired) | 1905 | 0.694 | 129 | 14 | 53 |
| speed_margin (retired) | 1634 | 0.490 | 96 | 0 | 100 |
| contested_speed (retired) | 1522 | 0.413 | 79 | 4 | 113 |
| reinforce_timeline (retired) | 1474 | 0.383 | 74 | 2 | 120 |
| contested_stage (retired) | 1441 | 0.362 | 71 | 0 | 125 |
| reinforce_contested (retired) | 1210 | 0.240 | 46 | 2 | 148 |
| level3 | 1000 | 0.036 | 6 | 0 | 162 |
| level2 | 724 | 0.006 | 1 | 0 | 167 |
| level1 | 528 | 0.000 | 0 | 0 | 168 |

**Champion:** `safe_hold`, 1931 on the training maps.

**Next:** iterations 14 to 16 promoted nothing, and two candidates (iteration 7's `margin_landings`, now `hold_retake`) rose on training and fell on the holdout maps: iteration 17 adds training maps and a founder.

## Iteration 17: more maps, nothing promoted

**Date:** 2026-11-21. **Maps:** 13 training, 8 holdout: **the map set grew** before the first measurement (two iterations without a promotion, and a second candidate that rose on training and fell on holdout), with `sound` and `bight` (training, seeds 1701 and 1702) and `skerry` (holdout, seed 1703). **Matches:** 2,652 in the baseline, 3,900 in the training selection, 1,632 in the holdout selection; the final standings are 2,652 training and 1,632 holdout matches. `safe_hold` stays the champion (1860).

**Findings:**

1. **Rear speed wins the back-and-forth over contested castles.** `sound`, `safe_hold` against `finish_speed` (lost in 102 turns): castle 3 changed hands six times between turns 18 and 41, and `finish_speed`'s castles, with speed bought on turns 10 and 26, retook it each time sooner. Iteration 13's graft of that speed (`safe_speed`) lost 7 of 20. **Idea (a):** rear speed only for walks longer than 8 turns.
2. **Strikes from the front walk at speed level 2.** **Idea (b):** the front buys speed level 3 once its production is at the top.
3. **Founder:** every `frontline` bot sends its soldiers out all game; **idea (c):** a counter-puncher that holds and strikes only enemy castles whose soldiers just fell.

| Candidate | Parent | Idea | Training rating (parent's) | Against parent | Holdout rating (parent's) | Decision |
|---|---|---|---|---|---|---|
| `hold_speedfar` | safe_hold | A rear castle buys speed level 2 before staging when its walk to the front is longer than SPEED_WALK turns. | 1852 (1810) | 16/26 | 2073 (2164) | **rejected**: its holdout rating is 91 below its parent's. Against the player's bot: 34 wins, 8 losses. |
| `hold_frontspeed` | safe_hold | The front castle buys speed level 3 once its production is at the top. | 1815 (1810) | 13/26 | not played | **rejected**: half against its parent. Against the player's bot: 32 wins, 2 draws, 8 losses. |
| `counter` | safe_hold (scaffolding) | A new strategy: no front and no staging; every castle builds and holds, and the bot strikes only enemy castles whose soldiers just fell. | 1688 (1810) | 13/26 | not played | **rejected**: half against its parent, rated 122 below it. |

All three passed the gate (slowest turns 12.5, 10.8 and 12.2 ms). The parent beat the player's bot 30 of 42 games.

**Status changes:** none.

Training maps (`iteration-17-train`, 2,652 matches, exit 0):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| safe_hold | 1860 | 0.846 | 293 | 30 | 41 |
| finish_safe | 1797 | 0.797 | 275 | 30 | 59 |
| finish_speed | 1778 | 0.780 | 263 | 42 | 59 |
| hold_finish | 1728 | 0.736 | 244 | 48 | 72 |
| frontline_hold (retired) | 1680 | 0.692 | 229 | 46 | 89 |
| frontline_finish | 1670 | 0.683 | 222 | 53 | 89 |
| frontline | 1656 | 0.669 | 218 | 51 | 95 |
| speed_margin (retired) | 1491 | 0.514 | 169 | 36 | 159 |
| contested_speed (retired) | 1430 | 0.459 | 149 | 36 | 179 |
| contested_stage (retired) | 1317 | 0.365 | 122 | 22 | 220 |
| reinforce_timeline (retired) | 1312 | 0.361 | 117 | 29 | 218 |
| reinforce_contested (retired) | 1254 | 0.319 | 100 | 32 | 232 |
| level3 | 1000 | 0.058 | 18 | 0 | 294 |
| level2 | 789 | 0.018 | 5 | 1 | 306 |
| level1 | 350 | 0.000 | 0 | 0 | 312 |

Holdout maps (`iteration-17-holdout`, 1,632 matches, exit 0):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| safe_hold | 2182 | 0.911 | 204 | 0 | 20 |
| finish_safe | 2053 | 0.830 | 186 | 0 | 38 |
| finish_speed | 1954 | 0.754 | 165 | 8 | 51 |
| frontline_finish | 1922 | 0.728 | 156 | 14 | 54 |
| hold_finish | 1885 | 0.696 | 149 | 14 | 61 |
| frontline | 1880 | 0.692 | 148 | 14 | 62 |
| frontline_hold (retired) | 1864 | 0.679 | 145 | 14 | 65 |
| speed_margin (retired) | 1662 | 0.509 | 114 | 0 | 110 |
| contested_speed (retired) | 1586 | 0.451 | 99 | 4 | 121 |
| reinforce_timeline (retired) | 1517 | 0.402 | 89 | 2 | 133 |
| contested_stage (retired) | 1449 | 0.357 | 80 | 0 | 144 |
| reinforce_contested (retired) | 1241 | 0.246 | 54 | 2 | 168 |
| level3 | 1000 | 0.031 | 6 | 0 | 186 |
| level2 | 727 | 0.005 | 1 | 0 | 191 |
| level1 | 533 | 0.000 | 0 | 0 | 192 |

**Champion:** `safe_hold`, 1860 on the training maps.

## Iteration 18: more maps, nothing promoted

**Date:** 2026-11-21. **Maps:** 14 training, 9 holdout: **the map set grew** before the first measurement (iterations 16 and 17 promoted nothing), with `haven` (training, seed 1801) and `spit` (holdout, seed 1802). **Matches:** 2,856 in the baseline, 4,200 in the training selection, 1,836 in the holdout selection. `safe_hold` stays the champion (1804).

**Findings** (`safe_hold`'s games):

1. **Its soldiers walk to one front from every lane.** `delta` against `hold_finish` (lost in about 130 turns): 57% of its soldiers walking, 5.9 units a send, 160 in groups on turn 71, 322 lost in clashes; it lost `delta` to five players and `crossing` to six. **Idea (a):** each rear castle stages to its own nearest castle nearer the enemy.
2. **A strike sends every joining castle's spare.** Same game: castles emptied by strikes. **Idea (b):** a strike sends what it needs.
3. **Founder:** both real opponents keep winning the walk; **idea (c):** speed first in every castle.

| Candidate | Parent | Idea | Training rating (parent's) | Against parent | Holdout rating (parent's) | Decision |
|---|---|---|---|---|---|---|
| `hold_localfront` | safe_hold | Each rear castle stages to its own front: the nearest own castle that is nearer the enemy than it is. | 1803 (1740) | 21/28 | 2157 (2182) | **rejected**: its holdout rating is 25 below its parent's (241 of 288 holdout points against 246). |
| `hold_needstrike` | safe_hold | A strike sends what it needs, from the nearest joining castles first; the rest stays home. | 1754 (1740) | 17/28 | 2129 (2182) | **rejected**: its holdout rating is 53 below its parent's (`skerry` 14/32 against 23). |
| `sprinter` | safe_hold (scaffolding) | A new strategy: speed first; every castle buys speed level 2 before any production level. | 1621 (1740) | 11/28 | not played | **rejected**: below its parent in both rules (9/34 on `archipelago`). |

All three passed the gate (slowest turns 14.5, 12.7 and 12.7 ms). Against the player's bot (46 games, 23 maps): `hold_needstrike` 34 wins as its parent did; `hold_localfront` 26; `sprinter` 26.

**Status changes:** none.

Training maps (`iteration-18-train`, 2,856 matches, exit 0):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| safe_hold | 1804 | 0.837 | 313 | 30 | 49 |
| finish_safe | 1753 | 0.796 | 297 | 30 | 65 |
| finish_speed | 1717 | 0.765 | 279 | 42 | 71 |
| hold_finish | 1683 | 0.735 | 263 | 50 | 79 |
| frontline_hold (retired) | 1650 | 0.704 | 252 | 48 | 92 |
| frontline_finish | 1638 | 0.693 | 244 | 55 | 93 |
| frontline | 1635 | 0.690 | 244 | 53 | 95 |
| speed_margin (retired) | 1438 | 0.505 | 180 | 36 | 176 |
| contested_speed (retired) | 1386 | 0.459 | 162 | 36 | 194 |
| contested_stage (retired) | 1272 | 0.365 | 132 | 22 | 238 |
| reinforce_timeline (retired) | 1247 | 0.346 | 121 | 29 | 242 |
| reinforce_contested (retired) | 1203 | 0.314 | 107 | 32 | 253 |
| level3 | 1000 | 0.074 | 25 | 0 | 311 |
| level2 | 725 | 0.016 | 5 | 1 | 330 |
| level1 | 287 | 0.000 | 0 | 0 | 336 |

Holdout maps (`iteration-18-holdout`, 1,836 matches, exit 0):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| safe_hold | 2220 | 0.913 | 230 | 0 | 22 |
| finish_safe | 2049 | 0.802 | 202 | 0 | 50 |
| finish_speed | 2003 | 0.766 | 189 | 8 | 55 |
| frontline_finish | 1960 | 0.730 | 177 | 14 | 61 |
| hold_finish | 1931 | 0.706 | 171 | 14 | 67 |
| frontline_hold (retired) | 1922 | 0.698 | 169 | 14 | 69 |
| frontline | 1912 | 0.690 | 167 | 14 | 71 |
| speed_margin (retired) | 1701 | 0.516 | 130 | 0 | 122 |
| contested_speed (retired) | 1610 | 0.448 | 111 | 4 | 137 |
| reinforce_timeline (retired) | 1523 | 0.389 | 97 | 2 | 153 |
| contested_stage (retired) | 1459 | 0.349 | 88 | 0 | 164 |
| reinforce_contested (retired) | 1269 | 0.250 | 62 | 2 | 188 |
| level3 | 1000 | 0.028 | 6 | 0 | 210 |
| level2 | 729 | 0.005 | 1 | 0 | 215 |
| level1 | 535 | 0.000 | 0 | 0 | 216 |

**Champion:** `safe_hold`, unchanged.

## Iteration 19: more maps, nothing promoted

**Date:** 2026-11-21. **Maps:** 15 training, 10 holdout: **the map set grew** before the first measurement, with `firth` (training, seed 1901) and `key` (holdout, seed 1902). **Matches:** 3,060 in the baseline, 4,500 in the training selection, 2,040 in the holdout selection. `safe_hold` stays the champion (1837).

**Findings:**

1. **A front per lane rose on training and fell on holdout** (iteration 18). **Idea (a):** in another form, each rear castle stages along its shortest route to the enemy: the castle nearer the enemy that minimizes the walk there plus its own distance to the enemy.
2. **Strikes take castles that the enemy retakes**, as neutrals were before `safe_hold`. **Idea (b):** a strike must leave the captured castle able to outlast the enemy castles within five turns of it.
3. **Founder:** the hosted bot that beat the champion on `claw` bought production 2 and 3 on turns 1 and 2 before sending anything. **Idea (c):** that opening.

| Candidate | Parent | Idea | Training rating (parent's) | Against parent | Holdout rating (parent's) | Decision |
|---|---|---|---|---|---|---|
| `hold_route` | safe_hold | Each rear castle stages to the own castle nearer the enemy that makes its route to the enemy shortest. | 1861 (1792) | 21/30 | 2071 (2112) | **rejected**: holdout rating 41 below its parent's. On the new holdout map `key`: 26 points against 25. |
| `opener` | safe_hold (scaffolding) | A new strategy from the hosted bot's opening: the home castle buys production up to level 3 before any castle sends a soldier. | 1837 (1792) | 21/30 | 2079 (2112) | **rejected**: holdout rating 33 below its parent's (`key` 27 against 25, `lagoon` 18 against 28). Against the player's bot it won 42 of 50 games, the best of any bot. |
| `hold_strikehold` | safe_hold | A strike must also leave the captured castle able to outlast the enemy castles that could land on it within HOLD_TURNS after the capture. | 1702 (1792) | 14/30 | not played | **rejected**: below its parent in both rules. Against the player's bot it won 40 of 50. |

All three passed the gate (slowest turns 11.2, 10.4 and 13.4 ms). The parent beat the player's bot in 36 of 50 games.

**Status changes:** none.

Training maps (`iteration-19-train`, 3,060 matches, exit 0):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| safe_hold | 1837 | 0.848 | 341 | 30 | 49 |
| finish_safe | 1782 | 0.805 | 323 | 30 | 67 |
| finish_speed | 1715 | 0.748 | 293 | 42 | 85 |
| hold_finish | 1694 | 0.729 | 280 | 52 | 88 |
| frontline_hold (retired) | 1673 | 0.710 | 273 | 50 | 97 |
| frontline | 1657 | 0.694 | 264 | 55 | 101 |
| frontline_finish | 1649 | 0.687 | 260 | 57 | 103 |
| speed_margin (retired) | 1464 | 0.514 | 198 | 36 | 186 |
| contested_speed (retired) | 1399 | 0.457 | 174 | 36 | 210 |
| contested_stage (retired) | 1291 | 0.369 | 144 | 22 | 254 |
| reinforce_timeline (retired) | 1261 | 0.346 | 131 | 29 | 260 |
| reinforce_contested (retired) | 1206 | 0.307 | 113 | 32 | 275 |
| level3 | 1000 | 0.069 | 25 | 0 | 335 |
| level2 | 726 | 0.015 | 5 | 1 | 354 |
| level1 | 288 | 0.000 | 0 | 0 | 360 |

Holdout maps (`iteration-19-holdout`, 2,040 matches, exit 0):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| safe_hold | 2148 | 0.904 | 252 | 2 | 26 |
| finish_safe | 1991 | 0.796 | 222 | 2 | 56 |
| finish_speed | 1931 | 0.746 | 205 | 8 | 67 |
| frontline_finish | 1906 | 0.725 | 195 | 16 | 69 |
| hold_finish | 1890 | 0.711 | 191 | 16 | 73 |
| frontline_hold (retired) | 1866 | 0.689 | 185 | 16 | 79 |
| frontline | 1850 | 0.675 | 181 | 16 | 83 |
| speed_margin (retired) | 1661 | 0.507 | 142 | 0 | 138 |
| contested_speed (retired) | 1587 | 0.446 | 123 | 4 | 153 |
| reinforce_timeline (retired) | 1564 | 0.429 | 119 | 2 | 159 |
| contested_stage (retired) | 1465 | 0.357 | 100 | 0 | 180 |
| reinforce_contested (retired) | 1326 | 0.275 | 76 | 2 | 202 |
| level3 | 1000 | 0.025 | 6 | 0 | 234 |
| level2 | 734 | 0.004 | 1 | 0 | 239 |
| level1 | 541 | 0.000 | 0 | 0 | 240 |

**Champion:** `safe_hold`, unchanged.

**Next:** fresh holdout maps before the first measurement, and the strongest rejected ideas in other forms.

## Iteration 20: fresh holdout maps, nothing promoted

**Date:** 2026-11-21. **Maps:** 16 training, 12 holdout: **the map set grew** before the first measurement, with `rill` (training, seed 2001) and two holdout maps, `tor` and `wick` (seeds 2002 and 2003): two, because the holdout set is the one that has gated every promotion. **Matches:** 3,264 in the baseline, 4,800 in the training selection, 2,448 in the holdout selection. `safe_hold` stays the champion (1847).

**Findings:**

1. **Iteration 19's founder opened well and lost the old holdout maps.** **Idea (a):** the opening only when no enemy castle could take the home during it.
2. **Lanes, a third form:** iterations 18 and 19 chose the castle to stage to by its distance to any enemy castle. **Idea (b):** each rear castle stages to the own castle nearest the enemy castle nearest it.
3. **Front speed, in another form** (iteration 17's `hold_frontspeed` took half against its parent): **idea (c):** speed level 3 at the front only when its strikes would walk more than 8 turns.

| Candidate | Parent | Idea | Training rating (parent's) | Against parent | Holdout rating (parent's) | Decision |
|---|---|---|---|---|---|---|
| `opener_safe` | safe_hold (scaffolding) | A new strategy from the hosted bot's opening: while it has one castle and no enemy castle could take it during the opening, the home buys production up to level 3 before sending anything. | 1866 (1830) | 23/32 | 2042 (2103) | **rejected**: holdout rating 61 below its parent's, on the new holdout maps too (`tor` 20 against 26, `wick` 24 against 26). Against the player's bot it won 48 of 56, the best of any bot. |
| `hold_lanefront` | safe_hold | Each rear castle stages to the front of its own lane: the own castle nearest to the enemy castle nearest it. | 1840 (1830) | 15/32 | not played | **rejected**: lost to its parent head to head. |
| `hold_frontlong` | safe_hold | The front castle buys speed level 3 when its production is at the top and its strikes would walk more than SPEED_WALK turns. | 1838 (1830) | 16/32 | not played | **rejected**: half against its parent. |

All three passed the gate (slowest turns 15.2, 13.9 and 13.4 ms). The parent beat the player's bot 42 of 56.

**Status changes:** none.

Training maps (`iteration-20-train`, 3,264 matches, exit 0):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| safe_hold | 1847 | 0.844 | 363 | 30 | 55 |
| finish_safe | 1780 | 0.790 | 339 | 30 | 79 |
| finish_speed | 1724 | 0.741 | 311 | 42 | 95 |
| hold_finish | 1716 | 0.734 | 302 | 54 | 92 |
| frontline_hold (retired) | 1697 | 0.717 | 295 | 52 | 101 |
| frontline | 1688 | 0.709 | 290 | 55 | 103 |
| frontline_finish | 1676 | 0.698 | 284 | 57 | 107 |
| speed_margin (retired) | 1475 | 0.511 | 208 | 42 | 198 |
| contested_speed (retired) | 1403 | 0.449 | 180 | 42 | 226 |
| contested_stage (retired) | 1303 | 0.368 | 154 | 22 | 272 |
| reinforce_timeline (retired) | 1277 | 0.349 | 139 | 35 | 274 |
| reinforce_contested (retired) | 1219 | 0.308 | 119 | 38 | 291 |
| level3 | 1000 | 0.065 | 25 | 0 | 359 |
| level2 | 727 | 0.014 | 5 | 1 | 378 |
| level1 | 290 | 0.000 | 0 | 0 | 384 |

Holdout maps (`iteration-20-holdout`, 2,448 matches, exit 0):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| safe_hold | 2141 | 0.902 | 302 | 2 | 32 |
| finish_safe | 1984 | 0.795 | 266 | 2 | 68 |
| finish_speed | 1919 | 0.741 | 245 | 8 | 83 |
| hold_finish | 1899 | 0.723 | 233 | 20 | 83 |
| frontline_finish | 1899 | 0.723 | 233 | 20 | 83 |
| frontline_hold (retired) | 1878 | 0.705 | 227 | 20 | 89 |
| frontline | 1851 | 0.682 | 219 | 20 | 97 |
| speed_margin (retired) | 1663 | 0.518 | 174 | 0 | 162 |
| contested_speed (retired) | 1550 | 0.429 | 141 | 6 | 189 |
| reinforce_timeline (retired) | 1497 | 0.390 | 129 | 4 | 203 |
| contested_stage (retired) | 1476 | 0.375 | 126 | 0 | 210 |
| reinforce_contested (retired) | 1313 | 0.277 | 90 | 6 | 240 |
| level3 | 1000 | 0.028 | 8 | 0 | 280 |
| level2 | 686 | 0.003 | 1 | 0 | 287 |
| level1 | 493 | 0.000 | 0 | 0 | 288 |

**Champion:** `safe_hold`, unchanged.

## Iteration 21: more maps, nothing promoted

**Date:** 2026-11-21. **Maps:** 17 training, 13 holdout: **the map set grew** before the first measurement, with `loch` (training, seed 2101) and `fen` (holdout, seed 2102). **Matches:** 3,468 in the baseline, 5,100 in the training selection; no holdout selection. `safe_hold` stays the champion (1876).

**Findings:**

1. **`circle` is drawn by mirrors.** The hosted bot's `circle` games and every `frontline` bot's: production 2 on turn 1 and 3 on turn 3, a home of 7 soldiers on turn 4, then 1,142 soldiers to 1,141 at the limit. **Idea (a), founder:** wait, and strike the first enemy castle that falls below what the home can land on it.
2. **The home falls to one strike** (`strait` and `islands`, iterations 14 and 18). Guarding every rear castle lost (iteration 14). **Idea (b):** guard the home alone.
3. **Rear speed for long walks rose on training and fell on holdout** (iteration 17). **Idea (c):** in another form, only once the race for castles is over.

| Candidate | Parent | Idea | Training rating (parent's) | Against parent | Decision |
|---|---|---|---|---|---|
| `ambush` | safe_hold (scaffolding) | A new strategy: for the first AMBUSH_TURNS turns buy nothing; strike the first enemy castle that falls below what a speed-2 group from home can land on it. | 1446 (1798) | 6/34 | **rejected**: below its parent in both rules; it won `circle` 30/34 (parent 19) and `haven` 34/34. |
| `hold_homeguard` | safe_hold | The home castle stages only what leaves it more than the strongest enemy castle within HOME_WALK turns of it holds. | 1775 (1798) | 17/34 | **rejected**: half against its parent, rated below it. |
| `hold_latespeed` | safe_hold | Once no neutral castle is on the bot's side, a rear castle whose walk to the front is longer than SPEED_WALK turns buys speed level 2 before staging. | 1779 (1798) | 14/34 | **rejected**: below its parent in both rules. Against the player's bot it won 50 of 60 (parent 46). |

All three passed the gate (slowest turns 13.6, 13.3 and 14.3 ms).

**Status changes:** none.

Training maps (`iteration-21-train`, 3,468 matches, exit 0):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| safe_hold | 1876 | 0.853 | 391 | 30 | 55 |
| finish_safe | 1785 | 0.782 | 357 | 30 | 89 |
| finish_speed | 1747 | 0.748 | 335 | 42 | 99 |
| hold_finish | 1733 | 0.735 | 323 | 54 | 99 |
| frontline_hold (retired) | 1714 | 0.718 | 316 | 52 | 108 |
| frontline | 1702 | 0.707 | 309 | 55 | 112 |
| frontline_finish | 1690 | 0.696 | 303 | 57 | 116 |
| speed_margin (retired) | 1485 | 0.508 | 221 | 42 | 213 |
| contested_speed (retired) | 1412 | 0.445 | 191 | 42 | 243 |
| contested_stage (retired) | 1319 | 0.372 | 166 | 22 | 288 |
| reinforce_timeline (retired) | 1290 | 0.350 | 149 | 35 | 292 |
| reinforce_contested (retired) | 1228 | 0.307 | 127 | 38 | 311 |
| level3 | 1000 | 0.061 | 25 | 0 | 383 |
| level2 | 728 | 0.013 | 5 | 1 | 402 |
| level1 | 291 | 0.000 | 0 | 0 | 408 |

Holdout maps (`iteration-21-holdout`, 2,652 matches, exit 0):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| safe_hold | 2070 | 0.882 | 320 | 2 | 42 |
| finish_safe | 1962 | 0.805 | 292 | 2 | 70 |
| finish_speed | 1895 | 0.750 | 269 | 8 | 87 |
| frontline_finish | 1878 | 0.736 | 258 | 20 | 86 |
| hold_finish | 1859 | 0.720 | 251 | 22 | 91 |
| frontline_hold (retired) | 1840 | 0.703 | 245 | 22 | 97 |
| frontline | 1828 | 0.692 | 242 | 20 | 102 |
| speed_margin (retired) | 1619 | 0.514 | 187 | 0 | 177 |
| contested_speed (retired) | 1502 | 0.423 | 151 | 6 | 207 |
| reinforce_timeline (retired) | 1445 | 0.382 | 137 | 4 | 223 |
| contested_stage (retired) | 1420 | 0.365 | 133 | 0 | 231 |
| reinforce_contested (retired) | 1280 | 0.280 | 99 | 6 | 259 |
| level3 | 1000 | 0.035 | 11 | 0 | 301 |
| level2 | 630 | 0.003 | 1 | 0 | 311 |
| level1 | 438 | 0.000 | 0 | 0 | 312 |

**Champion:** `safe_hold`, 1876 on the training maps, champion since iteration 13.

**Where it stands after iterations 12 to 21:** one promotion (`safe_hold`, iteration 13) in ten iterations. Seven candidates beat the champion head to head and rated above it on training, and six of them fell below it on the holdout maps. The map set grew from 10 and 6 to 17 and 13 maps. Against the player's bot the champion wins 46 of 60 games; five rejected candidates won more (`opener_safe` 48 of 56, `hold_latespeed` 50 of 60).

## Setup after iteration 21: real opponents in the league

**Date:** 2026-11-21. A change of the league's setup, asked for by the people who run it, made between iterations and measured with a full tournament on both sets of maps.

**Why.** The champion, `safe_hold`, played the hosted bot of the real games in lobbies on the league's maps (as Blue, 21 maps before the run was stopped): 4 wins (`archipelago`, `far-shores`, `gyre`, `loch`), a draw at the limit (`circle`) and 16 losses (`bight`, `claw`, `crossing`, `delta`, `firth`, `haven`, `islands`, `reef`, `rill`, `shelf`, `sound`, `strait` and the holdout maps `atoll`, `cays`, `fen`, `key`). Its predecessor `finish_speed` had won `crossing`, `islands`, `strait` and `far-shores` against it. In every lost training game the hosted bot took a third, often a fourth, neutral castle between turns 23 and 64 while `safe_hold` stopped at one or two, then out-produced it (10 to 15 against 3 to 10 by turn 61), with 34 to 55% of its soldiers walking to `safe_hold`'s 51 to 67%. The league had promoted a bot that beats the league and loses to the real opponent.

**What changed:**

- **Outside opponents** (`league_tools/opponents.py`, `opponents.local.toml`, not in git): a player's bot plays every tournament from its own project, like a default bot. The player's bot of iterations 8 to 21 is the first.
- **A `sparring` status** for fixed opponents that play like a real one, never parents, never counted with the retired bots, never deleted. **`ori_like`** is the first: `frontline`'s code with the hosted bot's habits from its 30 lobby games (production 3 at home before anything, neutrals bought with a cushion of 5 before strikes, batches of 12 to the front, strikes at 1.6 times the defenders). Against `safe_hold` it reproduces the hosted bot's result on 10 of the 17 training maps (it wins 9 where the hosted bot won 12); 18 settings were tried and these matched best. It is a stand-in, not a copy.
- **The check against real opponents** before a promotion (the iteration skill): a candidate that passed the holdout maps plays the hosted bot in lobby games on the training maps, five tabs at once (`scripts/serve_maps.py`, `scripts/lobby-run.js`), and is promoted only if it wins at least as many as the champion. The champion's record to beat: `safe_hold`, 4 wins of 17 training maps.
- **Six candidates per iteration when subagents write them**, a smaller model allowed, every diff read before it plays.

Training maps (`setup-22-train`, 4,522 matches, exit 0):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| safe_hold | 1782 | 0.822 | 431 | 32 | 81 |
| finish_safe | 1714 | 0.763 | 399 | 32 | 113 |
| finish_speed | 1683 | 0.733 | 377 | 44 | 123 |
| hold_finish | 1677 | 0.728 | 368 | 56 | 120 |
| ori_like | 1664 | 0.715 | 375 | 28 | 141 |
| frontline_hold (retired) | 1660 | 0.711 | 359 | 56 | 129 |
| frontline | 1644 | 0.696 | 349 | 59 | 136 |
| frontline_finish | 1637 | 0.688 | 345 | 59 | 140 |
| speed_margin (retired) | 1437 | 0.489 | 244 | 44 | 256 |
| outside_player | 1398 | 0.452 | 242 | 8 | 294 |
| contested_speed (retired) | 1388 | 0.443 | 219 | 44 | 281 |
| contested_stage (retired) | 1309 | 0.373 | 191 | 24 | 329 |
| reinforce_timeline (retired) | 1260 | 0.334 | 161 | 41 | 342 |
| reinforce_contested (retired) | 1207 | 0.294 | 140 | 40 | 364 |
| level3 | 1000 | 0.069 | 33 | 0 | 443 |
| level2 | 679 | 0.012 | 5 | 1 | 470 |
| level1 | 243 | 0.000 | 0 | 0 | 476 |

Holdout maps (`setup-22-holdout`, 3,458 matches, exit 0):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| safe_hold | 1916 | 0.865 | 359 | 2 | 55 |
| finish_safe | 1824 | 0.796 | 330 | 2 | 84 |
| finish_speed | 1769 | 0.748 | 307 | 8 | 101 |
| frontline_finish | 1738 | 0.719 | 289 | 20 | 107 |
| hold_finish | 1733 | 0.714 | 286 | 22 | 108 |
| frontline_hold (retired) | 1717 | 0.700 | 280 | 22 | 114 |
| frontline | 1697 | 0.680 | 273 | 20 | 123 |
| ori_like | 1655 | 0.639 | 266 | 0 | 150 |
| speed_margin (retired) | 1522 | 0.510 | 212 | 0 | 204 |
| outside_player | 1496 | 0.486 | 202 | 0 | 214 |
| contested_speed (retired) | 1421 | 0.418 | 171 | 6 | 239 |
| contested_stage (retired) | 1363 | 0.370 | 154 | 0 | 262 |
| reinforce_timeline (retired) | 1335 | 0.349 | 143 | 4 | 269 |
| reinforce_contested (retired) | 1223 | 0.272 | 110 | 6 | 300 |
| level3 | 1000 | 0.052 | 19 | 0 | 345 |
| level2 | 533 | 0.003 | 1 | 0 | 363 |
| level1 | 341 | 0.000 | 0 | 0 | 364 |

## Iteration 22: six candidates, and the first check against the real opponent

**Date:** 2026-11-21. **Maps:** 17 training, 13 holdout (unchanged since the setup). **Matches:** 8,500 in the training selection round robin (six candidates, the outside opponent and the sparring bot in the field), plus the holdout selection for the one that passed. The baseline is the setup's standings (`setup-22-train`), the same population. Six candidates, written in parallel by subagents (a smaller model), every diff read before it played.

**Findings** (the champion's lobby games against the hosted bot, training maps only):

1. **On compact maps the hold check makes the bot's own neutrals unaffordable.** `haven`, turns 12 to 36: castle 7 (25 soldiers, 2.7 units from home) stayed neutral while the bot logged "saving"; its price summed every enemy castle within five turns of it. **Idea (a):** count only the strongest one.
2. **Strikes before neutrals** (`islands`, iteration 15's finding 2, now with the real opponent's evidence). **Idea (b):** neutrals first.
3. **The hosted bot buys a neutral with 4 or 5 soldiers to spare**; the bot pays 1.4 times a contested neutral. **Idea (c):** a cushion of 5 instead.
4. **The first neutral is the only affordable one, not the best one.** `bight`, turn 1: 16 soldiers to the contested centre castle 3 (taken with 1, lost on turn 23) while castle 4, 2.8 units from home, waited until turn 66. **Idea (d):** wait up to four turns for the best neutral.
5. **Rear castles stay at production 2** (home at 2 until turn 83 on `far-shores`, 90 on `crossing`). **Ideas (e) and (f):** fixed batches of 12 to the front; or rear castles reach production 3 before staging.

| Candidate | Parent | Idea | Training rating (parent's) | Against parent | Holdout (parent's) | Hosted bot | Decision |
|---|---|---|---|---|---|---|---|
| `hold_bestneutral` | safe_hold | A castle waits up to WAIT_TURNS for the neutral with the best return instead of taking a worse one it can afford now. | 1828 (1797) | 18/34 | 1942 (1910) | 1 win, 1 draw, 15 losses (champion: 4 wins) | **rejected** by the check against the real opponent. |
| `hold_nearthreat` | safe_hold | A neutral paid exactly must outlast the strongest single enemy castle that could land on it within HOLD_TURNS, not all of them together. | 1791 (1797) | 16/34 | not played | not played | **rejected**: below its parent in both rules. |
| `hold_batch12` | safe_hold | Rear castles stage fixed batches of BATCH soldiers instead of all their spare. | 1790 (1797) | 17/34 | not played | not played | **rejected**: half against its parent, rated below it. |
| `hold_rear3` | safe_hold | A rear castle saves for its next production level, up to level 3, before it stages. | 1765 (1797) | 17/34 | not played | not played | **rejected**: half against its parent, rated below it. Against the player's bot it won 50 of 60 (parent 46). |
| `hold_expandfirst` | safe_hold | Neutrals before strikes. | 1755 (1797) | 12/34 | not played | not played | **rejected**: below its parent in both rules. |
| `hold_cushion` | safe_hold | A contested neutral costs what it needs exactly plus NEUTRAL_CUSHION soldiers, not NEUTRAL_MARGIN times. | 1737 (1797) | 12/34 | not played | not played | **rejected**: below its parent in both rules. |

All six passed the gate: no failed turn, slowest turns 60 to 75 ms with the six tournaments running at once.

**Status changes:** none. **Champion:** `safe_hold`, unchanged.

**The check against the real opponent, in practice:** five lobby tabs played the 17 training maps in about 20 minutes, one tab losing time to a start button that stayed disabled (`lobby-run.js` now retries it). The check rejected the only candidate the league would have promoted.

## Iteration 23: six ways to expand faster, and the opponent moved

**Date:** 2026-11-22. **Maps:** 17 training, 13 holdout (unchanged). **Matches:** 8,500 in the training selection round robin, 3,900 in the holdout selection for the one that passed. Six candidates from the champion, written in parallel by subagents (a smaller model), every diff read before it played; one (`hold_jointneutral`) failed the purity test for a constant set from another constant and was fixed to the literal before the gate.

**Findings** (the champion's lobby games against the hosted bot of 2026-11-21, training maps):

1. **Production comes before neutrals.** `play()` buys production on every castle before `expand()`: on `shelf` the front castle bought production 2, 3 and 4 on turns 15 to 25, 60 soldiers, while the hosted bot took the neutrals of 30 and 23. **Ideas (a)** the top production level after expansion; **(e)** with (b) below.
2. **Only one castle can buy a neutral.** On `crossing`, turns 28 to 30, the hosted bot took the 25-soldier middle neutral with groups from three castles at once (8 + 16 + 6 + 6) while the champion's castles held 6, 14 and 18 and never took it. **Idea (b):** castles take a neutral together.
3. **The waiting castle staged** (iteration 22's `hold_bestneutral`). **Idea (c):** wait for the best neutral and keep the waiting castle home.
4. **Strikes and staging start before the expansion ends.** **Idea (d):** an opening without either until the bot has four castles.
5. **Safe neutrals are taken with 1 soldier** (`reef`, `crossing`, `bight`, `shelf`); the hosted bot leaves 3 to 6. **Idea (f):** a cushion of 3 on a safe neutral.

| Candidate | Parent | Idea | Training rating (parent's) | Against parent | Holdout (parent's) | Player's bot (parent's), of 60 | Hosted bot, of 17 | Decision |
|---|---|---|---|---|---|---|---|---|
| `hold_cushion3` | safe_hold | (f) A safe neutral is paid SAFE_CUSHION (3) soldiers more than its exact price. | 1834 (1813) | 19/34 | 1781 (1914) | 40 (46) | 1 win (`gyre`) | **rejected**: 133 below its parent on the holdout maps. |
| `hold_prodlast` | safe_hold | (a) Production level 4 and speed only after strikes and expansion. | 1705 (1813) | 14/34 | not played | 46 (46) | 0 | **rejected**: below its parent in both rules. |
| `hold_waitnostage` | safe_hold | (c) Wait up to 4 turns for the best neutral, the waiting castle out of strikes and staging. | 1721 (1813) | 10/34 | not played | 51 (46) | 0 | **rejected**: below its parent in both rules. |
| `hold_jointneutral` | safe_hold | (b) Castles landing within 2 turns of each other take a neutral together. | 1711 (1813) | 10/34 | not played | 46 (46) | 0 of 11 played | **rejected**: below its parent in both rules. |
| `hold_expander` | safe_hold | (a) and (b) together. | 1638 (1813) | 8/34 | not played | 48 (46) | 0 of 6 played | **rejected**: below its parent in both rules. |
| `hold_opening` | safe_hold | (d) No strikes or staging while the bot has under 4 castles, neutrals remain and it is turn 80 or earlier. | 1637 (1813) | 7/34 | not played | 54 (46) | not played | **rejected**: below its parent in both rules. |

All six passed the gate: no failed turn, slowest turns 14 to 80 ms with the six tournaments running at once.

**The check against the real opponent, as a measure.** Five candidates, rejected by the league, played the hosted bot anyway (one per tab, each on its own port) to see whether the league and the real opponent agree. Some tabs lost games to a lobby that showed the new map late (`lobby-run.js` now waits for it and retries a map). The results were far below the champion's 4 wins of the day before, so the champion played its five best maps again in the same session, then all 17: **it lost all 17**, `circle` in 17 turns. The hosted bot had changed since the previous day, and the rule that compared a candidate with a record from another day compared nothing; the iteration skill now has the champion play in the same session. The 17 games' demos were saved for study (not in git).

**Status changes:** none. **Champion:** `safe_hold`, unchanged.

## Setup after iteration 23: a sparring bot built from the hosted bot's commands

**Date:** 2026-11-22. A change of the league's setup, made between iterations and measured with a full tournament on both sets of maps.

**Why.** `ori_like` matched the hosted bot's habits but not its results: as Red against the champion it won 9 of the 17 training maps where the hosted bot won 12 (2026-11-21). A study of every command the hosted bot gave in its saved lobby games (18 games of 2026-11-21, 2,122 turns, and 17 of 2026-11-22, 1,437 turns; each command read off consecutive frames, and checked against the bot's own count of its commands on all but one turn) found rules that fit closely: every capture is sized need(x) = x + x // 10 + 3, x being what the castle will hold when the groups land, plus half of what the enemy's other castles could bring first (exact on 69 of 77 neutral waves and 102 of 115 attacks in the first games); upgrades in the order production 2, 3, 4, speed 2, each the first turn the castle has the soldiers, unless an enemy group is bound for it or one enemy castle could then take it; fully upgraded rear castles send everything to the castle nearest the enemy at 10 or more (477 of 935 moves between its castles were exactly 12). The version of 2026-11-22 also buys speed to strike sooner (speed and a strike from the same castle in one turn 11 times, against once before) and prices neutrals like attacks.

**What changed:**

- **`ori_mimic`**, a sparring bot written from those rules (a founder, not a copy of anyone's code). Given every turn the hosted bot played on 2026-11-22, it makes the hosted bot's exact commands on 75% of them (1,077 of 1,437; the first draft, from the older games only, 49%). In the league it is the strongest player on both sets of maps, and as Red against the champion it wins 10 of the 17 training maps, where the hosted bot won all 17 that day: closer, still weaker.
- **`league replay`** (`league_tools/replay.py`): replays one team's turns in saved demos through a league bot and counts how often its commands match, by kind (upgrades, neutrals, attacks, defence, feeds). It is how a sparring bot is built and checked again when the opponent changes.

Training maps (`setup-24-train`, 5,100 matches, exit 0):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| ori_mimic (sparring) | 1790 | 0.812 | 439 | 61 | 78 |
| safe_hold | 1771 | 0.796 | 443 | 34 | 101 |
| finish_safe | 1703 | 0.734 | 407 | 34 | 137 |
| finish_speed | 1685 | 0.716 | 391 | 46 | 141 |
| hold_finish | 1667 | 0.699 | 375 | 58 | 145 |
| frontline_hold (retired) | 1651 | 0.683 | 366 | 58 | 154 |
| ori_like (sparring) | 1650 | 0.682 | 379 | 30 | 169 |
| frontline | 1642 | 0.674 | 359 | 61 | 158 |
| frontline_finish | 1635 | 0.667 | 355 | 61 | 162 |
| speed_margin (retired) | 1442 | 0.472 | 246 | 54 | 278 |
| outside_player | 1398 | 0.431 | 244 | 10 | 324 |
| contested_speed (retired) | 1394 | 0.427 | 221 | 52 | 305 |
| contested_stage (retired) | 1310 | 0.353 | 191 | 26 | 361 |
| reinforce_timeline (retired) | 1263 | 0.316 | 161 | 43 | 374 |
| reinforce_contested (retired) | 1214 | 0.279 | 140 | 43 | 395 |
| level3 | 1000 | 0.065 | 33 | 0 | 477 |
| level1 | 762 | 0.018 | 0 | 18 | 492 |
| level2 | 680 | 0.011 | 5 | 1 | 504 |

Holdout maps (`setup-24-holdout`, 3,900 matches, exit 0):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| ori_mimic (sparring) | 1956 | 0.873 | 374 | 24 | 44 |
| safe_hold | 1901 | 0.835 | 368 | 2 | 72 |
| finish_safe | 1801 | 0.753 | 332 | 2 | 108 |
| finish_speed | 1756 | 0.713 | 311 | 8 | 123 |
| frontline_finish | 1732 | 0.690 | 295 | 20 | 127 |
| hold_finish | 1728 | 0.686 | 292 | 22 | 128 |
| frontline_hold (retired) | 1713 | 0.672 | 286 | 22 | 134 |
| frontline | 1695 | 0.654 | 279 | 20 | 143 |
| ori_like (sparring) | 1651 | 0.611 | 270 | 0 | 172 |
| speed_margin (retired) | 1519 | 0.484 | 213 | 2 | 227 |
| outside_player | 1489 | 0.457 | 202 | 0 | 240 |
| contested_speed (retired) | 1425 | 0.400 | 171 | 12 | 259 |
| contested_stage (retired) | 1361 | 0.348 | 154 | 0 | 288 |
| reinforce_timeline (retired) | 1337 | 0.330 | 143 | 6 | 293 |
| reinforce_contested (retired) | 1232 | 0.258 | 110 | 8 | 324 |
| level3 | 1000 | 0.049 | 19 | 0 | 371 |
| level1 | 794 | 0.015 | 0 | 12 | 378 |
| level2 | 534 | 0.003 | 1 | 0 | 389 |

## Iteration 24: the strike at a short walk counts exactly

**Date:** 2026-11-22. **Maps:** 17 training, 13 holdout (unchanged). **Matches:** 9,282 in the training selection round robin, 4,368 in the holdout selection for the one that passed; `ori_mimic` of the setup above in the field. Six candidates from the champion, written in parallel by subagents (a smaller model), every diff read before it played.

**Findings** (the champion's 17 lobby games against the hosted bot of 2026-11-22, all lost, demos saved for study):

1. **An upgrade that one enemy castle can punish.** `circle`, turn 13: production 4 at 34 soldiers, 8 left, the enemy's castle 4 units away at 34; it bought speed 2 and sent 25, enough to the soldier, and took the castle on turn 17. **Ideas (a)** skip such an upgrade; **(b)** spend nothing, upgrade or send, below what keeps the castle from any single enemy castle.
2. **Fresh captures retaken within one to four turns** (`haven` castles 4 and 5, `rill` castles 4 and 5): the enemy sends at a neutral as soon as it sees our group walking there, sized for what we will leave, and the champion helps only castles it owns. **Idea (c):** top up a capture that an enemy group bound for it would take.
3. **The opponent keeps no reserve** (its castles at 0 to 3 soldiers after every upgrade, its rear castles at 4 to 8 between batches) and the champion strikes only with 1.5 times the defenders. **Idea (d):** strikes that land within five turns count the target exactly.

| Candidate | Parent | Idea | Training rating (parent's) | Against parent | Holdout (parent's) | Player's bot (parent's), of 60 | Hosted bot, of 17 (champion: 0) | Decision |
|---|---|---|---|---|---|---|---|---|
| `hold_exactstrike` | safe_hold | (d) A strike whose last group lands within SHORT_STRIKE (5) turns counts the target exactly, plus STRIKE_EXTRA (2). | 1871 (1788) | 26/34 | 1928 (1899) | 48 (46) | 0 | **promoted** |
| `hold_topup` | safe_hold | (c) Top up a neutral our group is bound for when an enemy group bound for it would take it. | 1785 (1788) | 18/34 | not played | 46 (46) | 0 | **rejected**: rated below its parent. |
| `hold_upsafe` | safe_hold | (a) Skip an upgrade that would leave the castle to one enemy castle at speed 2. | 1752 (1788) | 14/34 | not played | 42 (46) | 0, `circle` drawn | **rejected**: below its parent in both rules. |
| `hold_upsafe_topup` | safe_hold | (a) and (c). | 1721 (1788) | 13/34 | not played | 42 (46) | 0, `circle` drawn | **rejected**: below its parent in both rules. |
| `hold_upsafe_exact` | safe_hold | (a) and (d). | 1763 (1788) | 11/34 | not played | 44 (46) | not played | **rejected**: below its parent in both rules. |
| `hold_upsafe_all` | safe_hold | (b) Upgrades and sends keep what holds the castle against any single enemy castle; strikes as the parent. | 1663 (1788) | 10/34 | not played | 44 (46) | 1 (`claw`), `circle` drawn | **rejected**: below its parent in both rules. |

All six passed the gate: no failed turn, slowest turns 27 to 43 ms with the six tournaments running at once. The selection was first played with a first draft of `ori_mimic` in the field and played again once the setup above was committed; the decisions were the same (`hold_exactstrike` 1861 against 1773 then).

**The check against the real opponent:** the champion's record of the same session was 0 of 17; `hold_exactstrike` lost all 17 too, so it was not worse, and it was promoted. The candidates the league rejected played as a measure (above): the upgrade guards gave the only points. A background tab's timers slow to one a minute, which made two tabs look stuck; `lobby-run.js` now waits in a worker.

**Status changes:** `hold_exactstrike` active (the champion). `safe_hold` retired: `hold_exactstrike` did as well or better against every player that stays in the league (it scored a point less than its parent only against `hold_upsafe_exact`, a rejected candidate). With seven retired bots, `reinforce_contested`, the lowest rated of them (1227), is deleted.

Training maps (`iteration-24-train`, 5,100 matches, exit 0):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| hold_exactstrike | 1814 | 0.822 | 458 | 34 | 86 |
| ori_mimic (sparring) | 1779 | 0.792 | 428 | 60 | 90 |
| safe_hold (retired) | 1736 | 0.753 | 416 | 38 | 124 |
| finish_safe | 1680 | 0.697 | 385 | 36 | 157 |
| finish_speed | 1663 | 0.680 | 369 | 48 | 161 |
| hold_finish | 1636 | 0.652 | 348 | 58 | 172 |
| ori_like (sparring) | 1633 | 0.649 | 360 | 30 | 188 |
| frontline_hold (retired) | 1622 | 0.637 | 339 | 58 | 181 |
| frontline | 1611 | 0.625 | 331 | 61 | 186 |
| frontline_finish | 1604 | 0.619 | 327 | 61 | 190 |
| speed_margin (retired) | 1423 | 0.433 | 226 | 48 | 304 |
| outside_player | 1391 | 0.403 | 228 | 10 | 340 |
| contested_speed (retired) | 1368 | 0.382 | 198 | 46 | 334 |
| contested_stage (retired) | 1283 | 0.311 | 167 | 26 | 385 |
| reinforce_timeline (retired) | 1266 | 0.298 | 153 | 39 | 386 |
| level3 | 1000 | 0.055 | 28 | 0 | 482 |
| level1 | 795 | 0.018 | 0 | 18 | 492 |
| level2 | 641 | 0.007 | 3 | 1 | 506 |

Holdout maps (`iteration-24-holdout`, 3,900 matches, exit 0):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| ori_mimic (sparring) | 1943 | 0.860 | 369 | 22 | 51 |
| hold_exactstrike | 1897 | 0.826 | 360 | 10 | 72 |
| safe_hold (retired) | 1868 | 0.803 | 350 | 10 | 82 |
| finish_safe | 1771 | 0.717 | 315 | 4 | 123 |
| finish_speed | 1729 | 0.676 | 295 | 8 | 139 |
| hold_finish | 1688 | 0.636 | 270 | 22 | 150 |
| frontline_finish | 1688 | 0.636 | 271 | 20 | 151 |
| frontline_hold (retired) | 1675 | 0.622 | 264 | 22 | 156 |
| frontline | 1652 | 0.600 | 255 | 20 | 167 |
| ori_like (sparring) | 1621 | 0.568 | 251 | 0 | 191 |
| outside_player | 1484 | 0.434 | 192 | 0 | 250 |
| speed_margin (retired) | 1481 | 0.432 | 190 | 2 | 250 |
| contested_speed (retired) | 1398 | 0.360 | 155 | 8 | 279 |
| contested_stage (retired) | 1334 | 0.310 | 137 | 0 | 305 |
| reinforce_timeline (retired) | 1308 | 0.292 | 127 | 4 | 311 |
| level3 | 1000 | 0.041 | 16 | 0 | 374 |
| level1 | 828 | 0.015 | 0 | 12 | 378 |
| level2 | 568 | 0.003 | 1 | 0 | 389 |

## Iteration 25: the hosted bot's rules, with the league's lessons

**Date:** 2026-11-22. **Maps:** 17 training, 13 holdout (unchanged). **Matches:** 9,282 in the training selection round robin, 4,862 in the holdout selection for the two that passed. Six candidates written in parallel by subagents (a smaller model), every diff read before it played. Four of them are **founders** on the sparring bot `ori_mimic`'s code, which the iteration skill now allows: the sparring bot is then the parent in every rule, and stays as it is. `ori_mimic`'s reserve, counted up one soldier at a time, was replaced by the same number computed directly (identical commands on 300 random boards, eight times faster; its slowest turn had reached 1.4 s with six tournaments running).

**Findings:**

1. **`ori_mimic`, the hosted bot's rules, is the strongest player in the league** (iteration 24's tables) and loses to its original on the board only a little less than the league's bots. **Ideas:** found new bots on it, with what the league knows that the hosted bot doesn't.
2. **The hosted bot never bursts and sizes every capture need(P) = P + P // 10 + 3**; a burst of 8 as its group lands beats that for any castle under about 50. No league bot bursts. **Idea (a):** burst defence.
3. **`ori_mimic` draws more than any bot (60 of 578 training games)**: its price adds half of what the target's neighbours could bring, so a level game is never finished. **Idea (b):** exact strikes over a short walk and near the turn limit (iteration 8's and iteration 24's lessons).
4. **Its defence takes help only from castles no enemy group is bound for, and it never helps a capture the enemy will retake** (the league's oldest lesson: a castle taken with 1 soldier falls unless another castle reinforces it). **Idea (c):** both.

| Candidate | Parent | Idea | Training rating (parent's) | Against parent | Holdout (parent's) | Player's bot, of 60 | Hosted bot, of 17 (champion: 0) | Decision |
|---|---|---|---|---|---|---|---|---|
| `ori_hold` | ori_mimic | A new strategy (c): a castle under attack may help another if it still holds, help counts its turn's earlier sends, and a capture an enemy group would retake is topped up to hold. | 1876 (1836) | 17.5/34 | 1969 (1938) | 58, 2 draws, 0 lost | 2 wins (`islands`, `reef`), 1 draw (`rill`) | **promoted** (the champion) |
| `ori_finish` | ori_mimic | A new strategy (b): strikes over a walk of 5 turns or less, or near the turn limit, cost what the target will hold plus 2 and its burst instead of need(P). | 1855 (1836) | 18.5/34 | 2020 (1938) | 58, 2 draws, 0 lost | 1 win (`loch`), and one by the hosted bot's timeout (`haven`) | **promoted** |
| `ori_burst` | ori_mimic | A new strategy (a): burst levels up to 3 near the enemy, and a burst when the landing that takes a castle is this turn. | 1728 (1836) | 8/34 | not played | 56, 2 draws | 0 on the board (1 draw) | **rejected**: below its parent in both rules. |
| `ori_burst_finish` | ori_mimic | (a) and (b). | 1738 (1836) | 7.5/34 | not played | 56, 2 draws | 0 on the board | **rejected**: below its parent in both rules. |
| `exact_burst_upsafe` | hold_exactstrike | (a) and iteration 24's upgrade guard. | 1583 (1818) | 7/34 | not played | 40, 2 draws | not played | **rejected**: below its parent in both rules. |
| `exact_burst` | hold_exactstrike | (a) on the champion. | 1576 (1818) | 2/34 | not played | 42, 2 draws | not played | **rejected**: below its parent in both rules. |

All six passed the gate: no failed turn, slowest turns 11 to 61 ms.

**The check against the real opponent:** the champion `hold_exactstrike` had lost all 17 that session; `ori_mimic` itself, played as a measure, won 2 on the board (`firth`, `islands`) and drew `reef`. Seven of the 85 games ended by the hosted bot's timeout and two by ours (a tab the browser slowed); the founders' unfinished and forfeited maps were played again in two tabs, all lost.

**Status changes:** `ori_hold` and `ori_finish` active; `ori_hold` is the champion (first on training, 1811; `ori_finish` first on holdout, 2062). With eight active bots, `finish_safe` is retired (`hold_exactstrike` matches or beats it against everyone); no other active bot is matched everywhere, so seven stay active. With seven retired, `reinforce_timeline`, the lowest rated, is deleted.

Training maps (`iteration-25-train`, 5,712 matches, exit 0):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| ori_hold | 1811 | 0.791 | 430 | 108 | 74 |
| ori_finish | 1795 | 0.776 | 425 | 100 | 87 |
| hold_exactstrike | 1781 | 0.763 | 449 | 36 | 127 |
| ori_mimic (sparring) | 1764 | 0.747 | 401 | 112 | 99 |
| safe_hold (retired) | 1713 | 0.694 | 405 | 40 | 167 |
| finish_speed | 1653 | 0.631 | 361 | 50 | 201 |
| finish_safe (retired) | 1652 | 0.629 | 366 | 38 | 208 |
| hold_finish | 1614 | 0.588 | 330 | 60 | 222 |
| frontline | 1606 | 0.579 | 323 | 63 | 226 |
| ori_like (sparring) | 1601 | 0.574 | 336 | 30 | 246 |
| frontline_hold (retired) | 1601 | 0.574 | 321 | 60 | 231 |
| frontline_finish | 1600 | 0.573 | 319 | 63 | 230 |
| speed_margin (retired) | 1413 | 0.379 | 206 | 52 | 354 |
| outside_player | 1380 | 0.350 | 208 | 12 | 392 |
| contested_speed (retired) | 1351 | 0.325 | 172 | 54 | 386 |
| contested_stage (retired) | 1285 | 0.273 | 153 | 28 | 431 |
| level1 | 1022 | 0.050 | 0 | 54 | 490 |
| level3 | 1000 | 0.044 | 24 | 0 | 520 |
| level2 | 648 | 0.006 | 3 | 0 | 541 |

Holdout maps (`iteration-25-holdout`, 4,368 matches, exit 0):

| Player | Rating | Score | W | D | L |
|---|---|---|---|---|---|
| ori_finish | 2062 | 0.870 | 378 | 58 | 32 |
| ori_hold | 2006 | 0.831 | 358 | 62 | 48 |
| ori_mimic (sparring) | 1978 | 0.810 | 348 | 62 | 58 |
| hold_exactstrike | 1907 | 0.750 | 346 | 10 | 112 |
| safe_hold (retired) | 1875 | 0.720 | 332 | 10 | 126 |
| finish_safe (retired) | 1789 | 0.637 | 296 | 4 | 168 |
| finish_speed | 1747 | 0.594 | 274 | 8 | 186 |
| frontline_finish | 1730 | 0.577 | 260 | 20 | 188 |
| hold_finish | 1723 | 0.571 | 256 | 22 | 190 |
| frontline_hold (retired) | 1711 | 0.558 | 250 | 22 | 196 |
| frontline | 1696 | 0.543 | 244 | 20 | 204 |
| ori_like (sparring) | 1647 | 0.494 | 231 | 0 | 237 |
| speed_margin (retired) | 1521 | 0.376 | 173 | 6 | 289 |
| outside_player | 1506 | 0.363 | 170 | 0 | 298 |
| contested_speed (retired) | 1443 | 0.312 | 138 | 16 | 314 |
| contested_stage (retired) | 1383 | 0.269 | 126 | 0 | 342 |
| level1 | 1106 | 0.043 | 0 | 36 | 380 |
| level3 | 1000 | 0.024 | 10 | 0 | 406 |
| level2 | 462 | 0.000 | 0 | 0 | 416 |
