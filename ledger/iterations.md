# The league's ledger

One entry per iteration, newest last. An entry says what was measured, what was tried, what was kept and what was learned, so that the next session starts from here and doesn't try a rejected idea again. Ratings have `level3` at 1000 up to iteration 29, no fixed point in iterations 30 to 35 (see the setup after iteration 35), and `ori_mimic` at 1800 from then on.

## The lines

A line is a founder and the bots descended from it: one strategy. The main line is the champion's; a side line is worked every iteration and closed when two iterations of work in a row promote nothing in it (the `league-population` skill). Every iteration updates this table.

| Line | Its strategy | Head | Other active bots | State |
|---|---|---|---|---|
| `pounce` | A counter-puncher with no front and no staging: every castle keeps home what the enemy castles could spare against it (their stock above the reserve the `ori` rules keep), production to 4 then speed to 2 above that reserve, only the neutrals on its own side, and every enemy castle priced exactly at each landing turn up to six, struck by the castles that land together when their spare covers it. Founded in iteration 40 on `ori_like`'s scaffolding with the `ori` line's board helpers. | `pounce_reach` | `pounce` | side; 0 iterations of work without a promotion; a side line since iteration 45, when `burstguard` passed it |
| `ori` | The hosted bot's rules as read off its games (production at home first, neutrals priced like attacks, rear castles feeding one front, nothing bought or sent from a castle under attack), with the league's holding, exact strikes and reserves; since iteration 34 one small group kept walking at the enemy's front castle. Founded in iteration 25 on `ori_mimic`'s code. | `fullfeed_unfreeze` | none | closed; closed in iteration 43: two iterations of work in a row without a promotion |
| `frontline` | Production then speed in every castle, rear castles staging at the castle nearest the enemy, strikes from there with a margin. Founded in iteration 7 from a real game's winner; the champions of iterations 7 to 24. | none | none | closed; closed in iteration 25, when the `ori` founders passed it. Until iteration 38 `safe_hold` took more points from the champion than any other player outside the main line. Its code is in git, as Python and as Go. Head: none: `safe_hold`, its last bot, was deleted in iteration 38 by the cap on retired bots |
| `batchfront` | Founded in iteration 39 on `safe_hold`'s code (the closed `frontline` line) with what the real opponent of games 471 to 474 did: every castle buys production to 3 first and takes only cheap neutrals until production 4; rear castles feed one front in batches of 12; a neutral is paid by the one or two castles nearest it and sized to hold; strikes from up to three castles timed to land together; no reserve against the strongest enemy castle, no freeze under attack, no harassment. | `batchfront_keep` | none | closed; closed in iteration 43: two iterations of work in a row without a promotion |
| `landgrab` | land first: every castle takes the neutrals that pay back soonest before it buys any production level, the nearest two or three castles paying each together, and attacks only as one strike from every castle landing on one enemy castle on the same turn. | `landgrab` | none | side; 0 iterations of work without a promotion; admitted in iteration 43 |
| `burstguard` | castles past production 4 buy burst levels before speed; no standing reserve against the enemy's spare: a castle keeps what the strongest enemy castle within 4 turns could land less its growth and its burst, and a castle a landing would take this turn bursts to hold. | `burstguard` | none | main; 0 iterations of work without a promotion; the main line since iteration 45 |

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
- **A trickle of single soldiers freezes a bot that treats any enemy group as an attack.** `level1` sends one soldier a turn; the `ori_` line, which keeps an attacked castle out of upgrades, neutrals and strikes, sat on one castle at production 2 for 300 turns and drew 18 games on nine maps (iteration 26). Letting an attacked castle spend what leaves it holding through every landing won all 34 of those games but took exactly half against its parent: the freeze also kept castles home that the stronger bots would have taken.
- **Exact strikes and holding add up.** `ori_finish`'s exact short and late strikes on top of `ori_hold`'s holding beat `ori_hold` 18.5 of 34 and 16 of 26 on holdout, and rose 21 points on training and 65 on holdout (iteration 26's `ori_hold_exact`). Two ideas that were each promoted from the same parent combined without cancelling.
- **Counting the enemy's staged batches in a castle's safety makes it timid, as counting every neighbour did.** Adding to an enemy castle's threat its side's groups landing on it within the walk lost to its parent 14 of 34 (iteration 26's `ori_hold_staged`), although it was the batches that took the castle in the game that suggested it.
- **Help that lands on the turn of the capture is in time.** Groups land in id order, so a helper landing on the same turn as the group that takes a castle lands after it and retakes the castle at once, with its upgrades, if it brings what the castle lacked plus one. Counting such helpers beat its parent 20 of 34 and rose 47 points on training and 98 on holdout (iteration 27's `exact_sameturn`), the largest holdout gain since iteration 13.
- **A castle that can neither upgrade safely nor feed should feed.** Sending the spare soldiers of a castle whose next upgrade would leave it to one enemy castle to the front beat its parent 19 of 34 (iteration 27's `exact_stallfeed`).
- **A reserve against a castle that can't arrive in time is a hoard.** Bots that keep a reserve against the strongest enemy castle end level games with thousands of soldiers each and draw. Counting only enemy castles whose group could land before the last generation beat the parent 22 of 34 and rose 57 points on training and 52 on holdout (iteration 28's `sameturn_endreserve`).
- **Freeing an attacked castle entirely is worse than freezing it.** Treating a castle as attacked only when its landings would take it won every game against `level1`'s trickle but lost to the parent 13 of 34 (iteration 28's `sameturn_fallonly`): a castle that spends down to what its landings leave is taken by the next group. Two forms of the idea have now failed; the trickle is worth 9 points a tournament.
- **The `ori_` line's upgrade order holds against changes to it.** Letting castles that save for an upgrade help pay for neutrals, or making production 4 wait while a near neutral remains, both lost rating to their parent (iteration 29's `endreserve_helpall` and `endreserve_prod4late`), as reordering production did on the `hold_` line in iteration 23. Production first, the hosted bot's order, keeps winning the league.
- **The trickle is answered by asking whether the castle outgrows it.** An enemy group that holds no more soldiers than the castle produces before it lands is no attack; counting only the others, so that a real strike still freezes the castle's stock, won every game against `level1` and passed every rule (iteration 30's `stallfeed_growtrickle`, 17.5 of 34 against its parent, 15 points up on holdout). The two earlier forms changed what an attacked castle may spend, and lost.
- **Pricing help like an attack, or holding strike captures, doesn't pay in the league.** Adding to help half of what the enemy could still bring, and topping up enemy castles our strike will take, each lost to the parent 16 of 34 (iteration 30): the extra soldiers are taken from the strikes and staging that decide the race.
- **Defence refinements in the `ori_` line now split its mirror match.** Partial help, pricing help like an attack, cumulative trickles and holding strike captures each took 16 to 17 of 34 against their parent (iterations 30 and 31): the line's games against itself are decided move for move, and a change that acts only under attack changes a few of them either way.
- **An enemy that buys speed strikes from farther than its speed says.** At the end of a game the `ori_` line freed reserves against castles 8 turns away and fed the soldiers to the front; the enemy bought speed 3 in the same turn as its strike and took the emptied castles (iteration 32, 30 games lost on castles at the limit). Counting the speed it could buy fixed those games and still lost the mirror match (14.5 of 34): what loses a bot's games against its own line is not always what loses them against the others.
- **Keeping the enemy's castles under attack freezes a bot that won't spend under attack, on the training maps.** The hosted bot's rules buy and send nothing from a castle an enemy group is bound for; a founder that keeps a group of production-times-walk-plus-one walking at every enemy castle beat its parent 23 of 36 and every player of the league on training (89 points up), and fell 12 points below its parent on holdout (iteration 33's `harrier`). Against the hosted bot itself, which has that rule, it is untested.
- **Freeze the castle the enemy strikes from, not all of them.** One group of production-times-walk-plus-one kept walking at the enemy castle nearest ours beat its parent 25 of 38 and rose 80 points on training and 51 on holdout (iteration 34's `harrier_front`); the same groups at every enemy castle had fallen on holdout (iteration 33), and at castles that could upgrade lost the mirror match. One frozen castle costs the enemy its front; many cost us more than they freeze.
- **Freed reserves should strike, not feed.** Keeping the reserve against every enemy castle when feeding, while the end of the game frees it for strikes, beat its parent 19.5 of 38 and 21.5 of 30 on holdout, 83 points up there (iteration 34's `growtrickle_feedkeep`). Stopping all late feeding had lost (iteration 32).
- **Grafts of two promoted siblings keep paying.** Every time two candidates were promoted from one parent, the next iteration's graft of one into the other passed (iterations 26, 28, 29 and 35): `ori_hold_exact`, `endreserve_stallfeed` and `harrier_feedkeep` are such grafts, and three of the session's four champions.
- **Ideas that lose the league can win the player's bot.** In iteration 23 the order of six candidates against the player's bot (54, 51, 48, 46, 46 and 40 wins of 60) was nearly the reverse of their order in the league; the bot that waited longest to strike (`hold_opening`, 7 of 34 against its parent) won the most.
- **The race for castles decides the league; production decides the real games.** Saving rear castles' soldiers for production once no neutral castle is on the bot's side lost to its parent 8 of 18 (iteration 9's `hold_phase`), as iteration 8's `frontline_economy` did; both real opponents still out-produce every `frontline` bot (the hosted bot reached production 4 at home by turn 44 on `crossing`, while the `frontline` bots stayed at 2 until turn 90).
- **Production before the front is right against one opponent and wrong in the league.** Holding a rear castle's soldiers for its next production level before staging won `delta` against the player's bot, on both sides, but lost to its parent 7 of 18 (iteration 8's `frontline_economy`): the league's bots punish a late front more than they punish a thin economy.
- **A frozen game is lost by whoever breaks it, unless it was lost anyway.** Inside the `harrier` line both sides' castles keep a reserve against the strongest enemy castle and grow alike, and a game freezes with nothing spared for 200 turns (`reef` against `growtrickle_feedkeep`: 3 castles each, "saving" from turn 51 to 286, drawn with 2,088 soldiers each); 56 of the champion's 123 training draws end with identical castles and soldiers. A strike from everything at a frozen enemy is answered by its reinforcements (`reef`, turn 63: 339 soldiers met by a defender that sent 184 to help): on the four maps it changed most, from a castle lead it turned 20 wins at the limit into eliminations (`sound`, `islands`), from a level freeze 18 draws into losses against 6 into wins, and only from behind did it pay (18 losses into wins, `crossing`, `shelf`); over all 19 maps it scored 31.5 points less than its parent against the rest of the field. Behind only, it beat its parent 20 of 38 and rose 3 points on training, and fell 11 on holdout (iteration 36's `feedkeep_stall`).
- **Ties broken anew every turn cost a line that keeps one front.** Breaking every equal choice with a per-turn seeded shuffle, not the castle id, beat `ori_hold` 18.5 of 34 (before iteration 36, against the iteration-25 population), but took exactly half against `harrier_feedkeep` and rated 52 below it (iteration 36's `feedkeep_dice`): its games weren't read, so why is still open. A likely cause, to check first: its front, its harassed castle and its senders are chosen by distance with the id as the tie-break, and a tie that flips from turn to turn would split the stack between two fronts; if so, a seed should pick once a game where the choice must stay the same.
- **Defence that buys speed to arrive in time passes, barely, and moves games map by map.** When no helper would land before a castle falls, letting one that can afford its next speed level buy it and help beat its parent 22 of 38 (22 draws), rated 1 point above it on training and 22 on holdout (iteration 37's `feedkeep_speedhelp`), while its points against the field moved by up to 15 on single maps both ways (`strait` 16/36 against 31, `spit` 31 against 19). A rule that acts on a few turns of a game decides which games are won more than how many.
- **Soldiers sent at the end must land before it.** Near the limit, freed reserves struck at castles 7 to 15 turns away with 6 to 10 left, and a level game stayed level with thousands of soldiers walking at the end. Dropping a sender that can't land before the last generation, unless the speed levels it can pay make it land, beat its parent 21.5 of 38 and rated 65 points above it on training and 52 on holdout, the largest gain of the line (iteration 38's `speedhelp_landlate`): a draw at the limit is often a win that didn't arrive.
- **A castle with nothing left to buy should feed the front.** Feeding stopped at castles with any reserve, so fully upgraded rear castles saved apart while one enemy stack grew and took them one at a time (real game 474, turns 80 to 108; `archipelago`, 49 turns of saving). Letting such a castle feed what it holds above its reserve beat its parent 21 of 38, 13 points above it on training and 29 on holdout (iteration 38's `speedhelp_fullfeed`), but it lost points to the strikers (`ori_like` 27 against 34): the fed soldiers leave a castle that a strike then finds thinner.
- **Buying speed for help only on the last chance gave back `strait` and lost `gyre` and `haven`** (19 of 38, iteration 38's `speedhelp_lastchance`): iteration 37's speed-help wins some maps for the same reason it loses others, so a cut-off that is right for one map shape is wrong for another.
- **Fixes for the real opponent's `claw` games lose the league's mirror match.** Five candidates from three real losses on `claw` (paying a contested neutral from castles saving for an upgrade, captures priced with the neighbours' help, feeding only from behind the front, reserves that count the enemy's inbound feeds, no harassment at a fed castle) each acted where its finding was and took 14 to 18 of 38 against their parent (iteration 37). `ori_mimic`, the stand-in, plays `claw`'s opening move for move as the `harrier` line does, so the race the real games were lost in doesn't happen in the league.

- **A bot that freezes under attack is beaten by one that keeps every castle under attack.** The `ori` line buys and sends nothing from a castle an enemy group bound for it would outgrow; an exploiter on the champion's own code that keeps one group of production-times-walk-plus-one walking at every enemy castle of 6 soldiers or more, from any castle while its production is at least the enemy's, took 51 of 60 from the champion on training and 36 of 54 on holdout (iteration 39's `punisher`). Iteration 33's `harrier` did this from fully upgraded castles only, capped at 20, and fell on holdout; uncapped and from every castle it is the largest edge any bot has had over a champion. The hosted bot has the same rule.
- **Counting the enemy's own groups landing on its castles makes the `ori` line timid, in every form.** Counting them in `reserve()` and `holds()` themselves (strikes, help and upgrades), within 4 turns, lost to the parent 22.5 of 60 and was clearly worse in the field, 74 games better and 174 worse on 6 maps against 23 (iteration 39's `landlate_inbound`), after the threat form (iteration 26, 14/34) and the feeding form (iteration 37, 15/38). The cause is in every real game and in five of this iteration's seven studied games; the answer is not a bigger reserve in this line. Closed for the line.
- **Feeding fully upgraded castles beats the champion head to head and loses to the strikers.** Grafted into the champion it took 36 of 60 from it, the best head-to-head in the line since iteration 34, but only 8 more games better than worse in the field and 10.5 points fewer against the sparring bots (`ori_mimic` 53.5 against 57, `ori_like` 46 against 53; iteration 39's `landlate_fullfeed`), as iteration 38's `speedhelp_fullfeed` lost to `ori_like`. Real game 474's deciding mistake has a fix that the stand-ins for its opponent punish.
- **A freeze under attack should not stop an upgrade the castle can pay through every landing.** `punisher` kept castles at production 1 for 30 turns with groups of 6 while they held up to nine times that (`estuary`, castle 4). Letting a frozen castle buy a level when, after paying, it still holds through each landing bound for it, its growth counted, beat its parent by 79 games in the field (clear) and by 38 on holdout (clear) (iteration 40's `fullfeed_unfreeze`). The two earlier forms freed what an attacked castle may send (iterations 26 and 28) and failed; the upgrade alone passes.
- **A bot with no reserve loses its castles to strikes sized to what it left.** `batchfront` spent castles down to 1 to 8 soldiers beside enemy castles of 30 to 45 (upgrades on `circle`, a take on `gyre`, feed batches on `gyre`, `inlet` and `haven`), and each was struck at exactly that. Keeping what the strongest enemy castle within 4 turns could land, less the castle's growth, beat its parent 42 of 62 and was clear on both sets (iteration 40's `batchfront_keep`); a horizon of 8 or 14 turns cost the economy and lost the head-to-head (26 and 20 of 62), as iteration 2's static reserve did.
- **Pricing the enemy's spare instead of its stock beats the `ori` line.** A founder that counts an enemy castle's threat and its help as only its soldiers above the reserve the `ori` rules keep took 47 to 51 of 62 from every `ori` bot, where the same founder counting the whole stock took 3 (iteration 40's `pounce`): that line keeps most of its soldiers as reserves it never sends, and a bot that knows it strikes past them. It takes fewer points from the sparring bots than the `ori` champion (101 of 124 against 114 on training, 86 against 106.5 of 116 on holdout) and loses to `batchfront`, which keeps no such reserve.
- **Uncapped harassment of every castle is not a gain for the line that freezes.** Grafting `punisher`'s groups at every enemy castle into the champion beat it 47 of 62 and was clear on training (+89), and showed nothing on the 27 holdout maps (+4 at 46.7%) (iteration 40's `landlate_punish`, unresolved), as iteration 33's `harrier` fell on holdout.
- **`pounce`'s losses come from where its soldiers stand, not from how it prices threats.** In iteration 41 three fixes of its pricing (counting the groups walking in to each enemy castle, keeping back what enemy groups walking at a castle would take, and striking up to 10 turns out instead of 6) each acted in the games they came from and turned some losses into wins there, and each was worse in the field (−46, −7 and −73 games). Its hoard sits 7 to 13 turns from every enemy castle on `wharf`, `bight` and `far-shores`: a bot with no front has its soldiers where it can neither strike nor help in time.
- **A rule that stops every strike while any castle is short stops too many.** `batchfront_keep` with no strike while `reinforce` reported a castle short lost to its parent 21.5 of 64 and was clearly worse (iteration 41's `keep_nostrike`): a castle is short on most turns of a long game.

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

## Iteration 26: ori_finish's exact strikes on ori_hold

**Date:** 2026-11-22. **Maps:** 17 training, 13 holdout (unchanged). **Matches:** 7,038 in the training selection round robin, 4,368 in the holdout selection. Three candidates from the champion, written one after the other. **Run in a cloud container with 4 CPUs and an empty cache**, so the baseline played all 5,100 training and 3,900 holdout matches again, and **without the outside opponent** (no `opponents.local.toml` there): every rating below is from a field without the player's bot and is not comparable with iteration 25's numbers. The baseline (`iteration-26-before`) put `ori_hold` first at 1866. **The check against the real opponent was not played** (the session had no browser lobby or the hosted bot's URL; the person who asked chose to skip it), so the promotion below is unverified against the hosted bot.

**Findings** (`ori_hold`'s games on the training maps):

1. **A trickle of groups of 1 freezes it.** `islands` against `level1` (a draw at the limit): from turn 2 `level1` sends one soldier a turn at `ori_hold`'s home; `ori_hold` logged "saving" for 299 turns, one castle at production 2, 334 soldiers. `attacked()` (any enemy group bound for a castle) bars a castle from upgrades, from `senders()` and so from every neutral and strike. 18 draws against `level1` on nine maps, 9 points. **Idea (a):** an attacked castle may spend what leaves it holding through every landing bound for it.
2. **Upgrade checks read an enemy castle without its batches.** `gyre` against `hold_exactstrike` (lost in 64 turns), turn 38: front castle 4 bought production 4 down to 2 soldiers because enemy castle 3, 3.6 units away, held 18; two batches of 10 landed there on turn 39 and castle 3 struck with 38, taking castle 4 on turn 42. **Idea (b):** an enemy castle's threat counts its own side's groups landing on it within the walk.
3. **It draws its own line.** 32 of its 64 games against `ori_finish` and `ori_mimic` end at the limit (`ori_finish` beats it 19.5 of 34): it strikes only at need(P) plus half the neighbours, so a level game never ends. **Idea (c):** graft `ori_finish`'s exact strikes (short walk or near the limit).
4. Also read: `haven` and `loch` against `finish_speed` and `finish_safe` (71 and 94 turns): the `frontline` line had 45 to 56% of its soldiers walking and sent twice as many as `ori_hold`, whose castles feed the front only at production 4 and speed 2; a capture with 1 soldier on `haven` (castle 5, turn 30) was lost at once. Not made a candidate this time.

| Candidate | Parent | Idea | Training rating (parent's) | Against parent | Holdout (parent's) | Decision |
|---|---|---|---|---|---|---|
| `ori_hold_exact` | ori_hold | (c) Strikes landing within 5 turns, or within 30 of the limit, cost the target plus 2 plus its burst instead of need(). | 1888 (1867) | 18.5/34 | 2207 (2142), 16/26 | **promoted** (the champion); hosted-bot check not played |
| `ori_hold_trickle` | ori_hold | (a) An attacked castle spends what leaves it holding through every landing. | 1867 (1867) | 17/34 | not played | **rejected**: exactly half against its parent. It took 34 of 34 from `level1` (parent 25) and lost 3 points each to `frontline_hold` and `hold_finish`. |
| `ori_hold_staged` | ori_hold | (b) An enemy castle's threat counts its side's groups landing on it within the walk. | 1848 (1867) | 14/34 | not played | **rejected**: below its parent in both rules (17 against 23 from `hold_exactstrike`). |

All three passed the gate. The three gate runs played at once on 4 CPUs and showed slowest turns of 211 to 363 ms; each of those matches played again alone took 7 to 13 ms at most, so the spikes were the machine.

**Status changes:** `ori_hold_exact` active, the champion. `ori_hold` stays active: `ori_hold_exact` scored less than it against `hold_exactstrike` (21 against 23) and `safe_hold` on training. With eight active bots, `frontline_finish` is retired (`frontline` matches or beats it everywhere on training); no other active bot is matched everywhere, so seven stay active. With seven retired, `contested_stage`, the lowest rated (1321), is deleted.

Training maps (`iteration-26-train`, 5,100 matches, exit 0):

| Player | Rating | Score | W | D | L |
| --- | --- | --- | --- | --- | --- |
| ori_hold_exact | 1861 | 0.775 | 387 | 122 | 69 |
| ori_hold | 1836 | 0.750 | 369 | 129 | 80 |
| ori_finish | 1824 | 0.738 | 364 | 125 | 89 |
| hold_exactstrike | 1812 | 0.725 | 401 | 36 | 141 |
| ori_mimic (sparring) | 1795 | 0.708 | 343 | 132 | 103 |
| safe_hold (retired) | 1747 | 0.654 | 358 | 40 | 180 |
| finish_speed | 1680 | 0.578 | 309 | 50 | 219 |
| finish_safe (retired) | 1677 | 0.574 | 313 | 38 | 227 |
| frontline | 1646 | 0.539 | 281 | 61 | 236 |
| frontline_finish (retired) | 1638 | 0.530 | 275 | 63 | 240 |
| hold_finish | 1638 | 0.529 | 276 | 60 | 242 |
| frontline_hold (retired) | 1625 | 0.516 | 269 | 58 | 251 |
| ori_like (sparring) | 1616 | 0.505 | 278 | 28 | 272 |
| speed_margin (retired) | 1449 | 0.336 | 168 | 52 | 358 |
| contested_speed (retired) | 1377 | 0.277 | 131 | 58 | 389 |
| level1 | 1188 | 0.071 | 0 | 72 | 438 |
| level3 | 1000 | 0.025 | 13 | 0 | 497 |
| level2 | 759 | 0.006 | 3 | 0 | 507 |

Holdout maps (`iteration-26-holdout`, 3,900 matches, exit 0):

| Player | Rating | Score | W | D | L |
| --- | --- | --- | --- | --- | --- |
| ori_hold_exact | 2144 | 0.839 | 330 | 82 | 30 |
| ori_finish | 2138 | 0.835 | 328 | 82 | 32 |
| ori_hold | 2082 | 0.790 | 308 | 82 | 52 |
| ori_mimic (sparring) | 2051 | 0.762 | 296 | 82 | 64 |
| hold_exactstrike | 1992 | 0.708 | 308 | 10 | 124 |
| safe_hold (retired) | 1953 | 0.670 | 291 | 10 | 141 |
| finish_safe (retired) | 1863 | 0.577 | 253 | 4 | 185 |
| finish_speed | 1826 | 0.538 | 234 | 8 | 200 |
| frontline_finish (retired) | 1815 | 0.527 | 223 | 20 | 199 |
| hold_finish | 1806 | 0.518 | 218 | 22 | 202 |
| frontline_hold (retired) | 1792 | 0.505 | 212 | 22 | 208 |
| frontline | 1779 | 0.491 | 207 | 20 | 215 |
| ori_like (sparring) | 1711 | 0.425 | 188 | 0 | 254 |
| speed_margin (retired) | 1582 | 0.314 | 135 | 8 | 299 |
| contested_speed (retired) | 1504 | 0.260 | 105 | 20 | 317 |
| level1 | 1316 | 0.062 | 0 | 48 | 342 |
| level3 | 1000 | 0.010 | 4 | 0 | 386 |
| level2 | 614 | 0.000 | 0 | 0 | 390 |

**Champion:** `ori_hold_exact`, 1861 on training and 2144 on holdout; `ori_hold` was 1866 in this iteration's baseline and is 1836 here.

**Where it still loses:** `circle` (draws with nearly everyone), `loch` and `firth` against the `frontline` line, whose castles stage to the front from production 2 or 3 while the `ori_` line feeds only at production 4 and speed 2 (finding 4); draws against `level1` remain (finding 1's idea took exactly half against its parent and could come back with something more).

**Time:** 25 minutes from the first command to the final tables. Step 0: 1 min. Step 1: 13 min (the baseline, 5,100 matches from an empty cache, with the holdout baseline of 3,900 played beside it; playing is all of it, the tables take under a second). Step 2: under 1 min of commands. Steps 3 and 4: 4 min (three gate runs at once, then 1 min replaying the slow matches alone). Step 5: 2 min (selection 35 s, 102 matches; holdout 70 s, 468 matches). Step 6: final tables from the cache in 3 s. Iteration 25's time was not recorded. The slowest step is a one-time cost of a fresh container; next time the gate is one `--focus A,B,C` run, as the skill says, so its slowest-turn column is believable at once.

## Iteration 27: help that lands on the turn of the capture

**Date:** 2026-11-22. **Maps:** 17 training, 13 holdout (unchanged). **Matches:** 7,038 in the training selection round robin, 4,862 in the holdout selection. Three candidates from the champion, written one after the other. Same container as iteration 26 (no outside opponent, no check against the hosted bot: every promotion below is unverified against it). The baseline (`iteration-27-before`) is iteration 26's final table, all from the cache.

**Findings** (`ori_hold_exact`'s games on the training maps):

1. **Help that would land on the capture's turn is called too late.** `loch` against `hold_exactstrike` (lost in 96 turns), turns 77 to 81: four groups (28, 18, 34 and 10) converged on castle 2 (production 2, 31 soldiers). On turn 79 castle 0, 2.5 units away at speed 2 (3 turns) with 51 soldiers, could cover the 30 that castle 2 lacked, but the capturing landing was also 3 turns away, and `defend()` takes only helpers that land strictly before it; castle 0 logged "saving" and castle 2 fell on turn 81. Groups land in id order, so a helper on that turn lands after the enemy and retakes the castle with its upgrades. **Idea (a):** a helper is in time when it lands on or before the fall's turn.
2. **A castle whose upgrade is blocked idles.** The same game, turns 70 to 80: castle 2 held 25 to 31 soldiers at production 2, its next level blocked by `holds()` (enemy castle 6, 40 to 60 soldiers, 5.7 units away), and only fully upgraded castles feed the front; it neither upgraded nor fed. 24% of the champion's soldiers were walking, 59% of `hold_exactstrike`'s. **Idea (b):** a stalled castle feeds the front what it can spare.
3. **`ori_finish` still beats its descendant** (17.5 of 34): it has the exact strikes and none of `ori_hold`'s holding. `gyre` against `safe_hold` (lost in 58 turns, as in iteration 26): the champion's castle 4 bought production 4 down to 2 soldiers on turn 38 next to enemy castle 3 being fed batches, and fell on turn 42. **Idea (c):** drop `hold()`, the top-up of captures an enemy group would retake, and keep those soldiers for strikes.
4. The 18 draws against `level1` and the 30 points lost on `circle` are unchanged (iteration 26's findings).

| Candidate | Parent | Idea | Training rating (parent's) | Against parent | Holdout (parent's) | Decision |
|---|---|---|---|---|---|---|
| `exact_sameturn` | ori_hold_exact | (a) Defence takes helpers whose group lands on or before the turn of the landing that would take the castle. | 1904 (1857) | 20/34 | 2227 (2129), 18/26 | **promoted** (the champion) |
| `exact_stallfeed` | ori_hold_exact | (b) A castle behind the front whose next upgrade would leave it unsafe sends what it can spare to the front once that is 10 or more. | 1871 (1857) | 19/34 | 2139 (2129), 14/26 | **promoted** |
| `exact_nohold` | ori_hold_exact | (c) No `hold()`. | 1831 (1857) | 17.5/34 | not played | **rejected**: rated below its parent (it lost 5 points each to `frontline_hold` and `hold_finish`). |

All three passed the gate in one `--focus` run (1,938 matches, 4.5 minutes): no failed turn, slowest turns 24 to 67 ms.

**Status changes:** `exact_sameturn` and `exact_stallfeed` active; `exact_sameturn` is the champion. `ori_hold_exact` stays active: both candidates score less than it against someone (`exact_sameturn` 25 against 27 from `finish_speed`; `exact_stallfeed` 30 against 31 from `speed_margin`). Nine active bots, and none is matched or beaten everywhere by another on training, so none is retired.

Training maps (`iteration-27-train`, 6,358 matches, exit 0):

| Player | Rating | Score | W | D | L |
| --- | --- | --- | --- | --- | --- |
| exact_sameturn | 1902 | 0.782 | 430 | 150 | 66 |
| exact_stallfeed | 1869 | 0.750 | 402 | 165 | 79 |
| ori_hold_exact | 1858 | 0.738 | 394 | 166 | 86 |
| ori_hold | 1834 | 0.714 | 373 | 177 | 96 |
| ori_finish | 1826 | 0.705 | 370 | 171 | 105 |
| hold_exactstrike | 1808 | 0.686 | 423 | 40 | 183 |
| ori_mimic (sparring) | 1800 | 0.677 | 348 | 179 | 119 |
| safe_hold (retired) | 1747 | 0.618 | 377 | 44 | 225 |
| finish_speed | 1681 | 0.542 | 323 | 54 | 269 |
| finish_safe (retired) | 1666 | 0.525 | 318 | 42 | 286 |
| frontline | 1651 | 0.507 | 295 | 65 | 286 |
| frontline_finish (retired) | 1644 | 0.499 | 289 | 67 | 290 |
| hold_finish | 1632 | 0.486 | 282 | 64 | 300 |
| frontline_hold (retired) | 1621 | 0.474 | 275 | 62 | 309 |
| ori_like (sparring) | 1606 | 0.457 | 279 | 32 | 335 |
| speed_margin (retired) | 1459 | 0.311 | 172 | 58 | 416 |
| contested_speed (retired) | 1400 | 0.263 | 135 | 70 | 441 |
| level1 | 1267 | 0.093 | 0 | 108 | 470 |
| level3 | 1000 | 0.022 | 13 | 0 | 565 |
| level2 | 760 | 0.005 | 3 | 0 | 575 |

Holdout maps (`iteration-27-holdout`, 4,862 matches, exit 0):

| Player | Rating | Score | W | D | L |
| --- | --- | --- | --- | --- | --- |
| exact_sameturn | 2227 | 0.864 | 380 | 94 | 20 |
| exact_stallfeed | 2139 | 0.800 | 335 | 120 | 39 |
| ori_finish | 2132 | 0.794 | 331 | 122 | 41 |
| ori_hold_exact | 2129 | 0.791 | 330 | 122 | 42 |
| ori_hold | 2071 | 0.741 | 308 | 116 | 70 |
| ori_mimic (sparring) | 2044 | 0.717 | 296 | 116 | 82 |
| hold_exactstrike | 1973 | 0.648 | 315 | 10 | 169 |
| safe_hold (retired) | 1933 | 0.607 | 295 | 10 | 189 |
| finish_safe (retired) | 1853 | 0.526 | 258 | 4 | 232 |
| frontline_finish (retired) | 1817 | 0.490 | 232 | 20 | 242 |
| finish_speed | 1809 | 0.482 | 234 | 8 | 252 |
| hold_finish | 1801 | 0.474 | 223 | 22 | 249 |
| frontline_hold (retired) | 1788 | 0.462 | 217 | 22 | 255 |
| frontline | 1784 | 0.457 | 216 | 20 | 258 |
| ori_like (sparring) | 1702 | 0.381 | 188 | 0 | 306 |
| speed_margin (retired) | 1588 | 0.287 | 137 | 10 | 347 |
| contested_speed (retired) | 1520 | 0.241 | 105 | 28 | 361 |
| level1 | 1395 | 0.081 | 0 | 72 | 370 |
| level3 | 1000 | 0.009 | 4 | 0 | 438 |
| level2 | 614 | 0.000 | 0 | 0 | 442 |

**Champion:** `exact_sameturn`, 1902 on training (iteration 26's champion `ori_hold_exact`: 1861 then, 1858 now) and 2227 on holdout (2144).

**Where it still loses:** `circle` and `loch`; draws against `level1` and the `ori_` line; `finish_speed` takes 2 more points from it than from its parent.

**Time:** 8 minutes from the first command to the final tables (iteration 26: 25). Step 1 (from the cache): 3 s. Step 2: 2 min of reading. Step 3: 1 min. Step 4: 4.5 min, the one `--focus` gate run, 1,938 matches, the slowest step: every candidate pair is played there once and then reused by the selection. Step 5: selection from the cache in 3 s; holdout 2.5 min (962 matches). Step 6: final tables in 4 s. Nothing to change in the tools: the time is playing, at about 7 matches a second on 4 CPUs.

## Iteration 28: no reserve against a castle that can't arrive in time

**Date:** 2026-11-22. **Maps:** 17 training, 13 holdout (unchanged). **Matches:** 8,500 in the training selection round robin, 5,928 in the holdout selection. Three candidates from the champion, written one after the other. Same container as iteration 26: no outside opponent, no check against the hosted bot. The baseline (`iteration-28-before`) is iteration 27's final table, from the cache.

**Findings** (`exact_sameturn`'s games on the training maps):

1. **Games inside the line end in hoards.** 120 of its games against `ori_hold`, `ori_hold_exact`, `ori_finish`, `ori_mimic` and `exact_stallfeed` ended at the turn limit, most as draws. `archipelago` against `ori_hold` (a draw): from turn 111 both sides held six castles and over 1,100 soldiers, on turn 300 4,906 against 4,638, and nobody struck: every castle keeps a reserve against the strongest enemy castle, which grows with the enemy's hoard, and strikes pay only from what is above it. In the last turns a reserve against an enemy castle whose group could no longer land before the end protects nothing. **Idea (a):** reserves and the upgrade check count only enemy castles that can land in time.
2. **The trickle freeze is still there**: 18 draws against `level1` (iteration 26's finding 1). **Idea (b), another form than iteration 26's:** a castle counts as attacked only when the landings bound for it would take it, and is otherwise unrestricted.
3. **The two promoted ideas of iteration 27 were made apart.** **Idea (c):** graft `exact_stallfeed`'s feeding of stalled castles into the champion.
4. The shortest losses are still `gyre` and `claw` against `safe_hold`, `hold_exactstrike` and the `frontline` line (58 to 77 turns), as in iterations 26 and 27.

| Candidate | Parent | Idea | Training rating (parent's) | Against parent | Holdout (parent's) | Decision |
|---|---|---|---|---|---|---|
| `sameturn_endreserve` | exact_sameturn | (a) A castle's reserve and upgrade check count only enemy castles whose group, sent now, lands before the last generation. | 1902 (1845) | 22/34 | 2261 (2209), 16/26 | **promoted** (the champion) |
| `sameturn_stallfeed` | exact_sameturn | (c) Graft from `exact_stallfeed`. | 1853 (1845) | 18/34 | 2216 (2209), 15/26 | **promoted** |
| `sameturn_fallonly` | exact_sameturn | (b) Attacked only when the landings would take the castle. | not counted (13/34) | 13/34 | not played | **rejected**: lost to its parent. It won all 34 games against `level1` (parent 25) and lost 16 points to `finish_safe`, 14 each to `frontline_hold` and `hold_finish`, 12 to `ori_like`: unrestricted castles under attack spend what the attack then takes. |

All three passed the gate in one `--focus` run (2,142 matches, 5.7 minutes): no failed turn, slowest turns 48 to 88 ms.

**Status changes:** `sameturn_endreserve` and `sameturn_stallfeed` active; `sameturn_endreserve` is the champion. `exact_sameturn` is retired: `sameturn_endreserve` matches or beats it against every other player, on both sets of maps. No other active bot is matched everywhere, so nine stay active. With seven retired, `contested_speed`, the lowest rated (1381 in the selection), is deleted; the field is one player smaller, which lifts every rating on both tables.

Training maps (`iteration-28-train`, 7,038 matches, exit 0):

| Player | Rating | Score | W | D | L |
| --- | --- | --- | --- | --- | --- |
| sameturn_endreserve | 1982 | 0.795 | 491 | 99 | 90 |
| sameturn_stallfeed | 1933 | 0.748 | 418 | 181 | 81 |
| exact_sameturn (retired) | 1926 | 0.741 | 416 | 176 | 88 |
| exact_stallfeed | 1895 | 0.708 | 386 | 191 | 103 |
| ori_hold_exact | 1882 | 0.694 | 378 | 188 | 114 |
| ori_hold | 1864 | 0.674 | 359 | 199 | 122 |
| ori_finish | 1847 | 0.655 | 347 | 197 | 136 |
| hold_exactstrike | 1831 | 0.637 | 412 | 42 | 226 |
| ori_mimic (sparring) | 1829 | 0.635 | 330 | 203 | 147 |
| safe_hold (retired) | 1772 | 0.569 | 364 | 46 | 270 |
| finish_speed | 1709 | 0.496 | 309 | 56 | 315 |
| frontline | 1675 | 0.457 | 277 | 67 | 336 |
| finish_safe (retired) | 1674 | 0.456 | 288 | 44 | 348 |
| frontline_finish (retired) | 1668 | 0.449 | 271 | 69 | 340 |
| hold_finish | 1649 | 0.428 | 258 | 66 | 356 |
| frontline_hold (retired) | 1638 | 0.416 | 251 | 64 | 365 |
| ori_like (sparring) | 1626 | 0.403 | 257 | 34 | 389 |
| speed_margin (retired) | 1481 | 0.268 | 156 | 52 | 472 |
| level1 | 1385 | 0.118 | 0 | 144 | 468 |
| level3 | 1000 | 0.015 | 9 | 0 | 603 |
| level2 | 765 | 0.003 | 2 | 0 | 610 |

Holdout maps (`iteration-28-holdout`, 5,382 matches, exit 0):

| Player | Rating | Score | W | D | L |
| --- | --- | --- | --- | --- | --- |
| sameturn_endreserve | 2324 | 0.852 | 414 | 58 | 48 |
| sameturn_stallfeed | 2284 | 0.823 | 368 | 120 | 32 |
| exact_sameturn (retired) | 2274 | 0.815 | 363 | 122 | 35 |
| exact_stallfeed | 2191 | 0.746 | 319 | 138 | 63 |
| ori_finish | 2182 | 0.738 | 315 | 138 | 67 |
| ori_hold_exact | 2178 | 0.735 | 312 | 140 | 68 |
| ori_hold | 2122 | 0.683 | 290 | 130 | 100 |
| ori_mimic (sparring) | 2101 | 0.662 | 280 | 128 | 112 |
| hold_exactstrike | 2018 | 0.579 | 296 | 10 | 214 |
| safe_hold (retired) | 1980 | 0.540 | 276 | 10 | 234 |
| finish_safe (retired) | 1909 | 0.469 | 242 | 4 | 274 |
| frontline_finish (retired) | 1876 | 0.437 | 217 | 20 | 283 |
| finish_speed | 1845 | 0.408 | 208 | 8 | 304 |
| hold_finish | 1843 | 0.406 | 200 | 22 | 298 |
| frontline | 1843 | 0.406 | 201 | 20 | 299 |
| frontline_hold (retired) | 1831 | 0.394 | 194 | 22 | 304 |
| ori_like (sparring) | 1751 | 0.323 | 168 | 0 | 352 |
| speed_margin (retired) | 1637 | 0.238 | 119 | 10 | 391 |
| level1 | 1554 | 0.103 | 0 | 96 | 372 |
| level3 | 1000 | 0.004 | 2 | 0 | 466 |
| level2 | 719 | 0.000 | 0 | 0 | 468 |

**Champion:** `sameturn_endreserve`, 1982 on training and 2324 on holdout; in the selection, with the same field as iteration 27's tables plus the candidates, it was 1902 against `exact_sameturn`'s 1845.

**Where it still loses:** draws against `level1` (18) and `circle`; the short losses on `gyre` and `claw` to the `hold_`/`frontline` lines' staged strikes.

**Time:** 11 minutes (iteration 27: 8). Step 1: 3 s. Step 2: 1 min. Step 3: 1 min. Step 4: 5.7 min, the gate (2,142 matches), the slowest step. Step 5: selection from the cache in 3 s, holdout 3 min (1,066 matches). Step 6: 4 s. The gate plays every candidate's matches once and the selections reuse them: there is nothing left to cut but the playing itself.

## Iteration 29: the stalled castles' feeding on the champion

**Date:** 2026-11-22. **Maps:** 17 training, 13 holdout (unchanged). **Matches:** 9,282 in the training selection round robin, 5,928 in the holdout selection. Three candidates from the champion, written one after the other. Same container as iteration 26: no outside opponent, no check against the hosted bot.

**Findings** (`sameturn_endreserve`'s games on the training maps):

1. **The upgrade race loses the race for neutrals.** `gyre` against `safe_hold` (lost in 58 turns, the champion's shortest loss for the fourth iteration running): turns 10 to 18 the log says "saving" every turn while home castle 0 saves for production 4 (bought on turn 19); castles 4 and 6, at production 1 and 2, can't pay a 12-soldier neutral alone, and a castle within three turns of its next upgrade doesn't help pay. `safe_hold` took neutral 3 on turn 19 and had four castles to three from then. **Ideas (a)** castles saving for an upgrade still help pay for neutrals; **(b)** production 4 waits while a neutral nearer to the castle than to any enemy remains.
2. **The two stalled-feeding bots promoted from the line (iterations 27 and 28) have not met this champion's reserve rule.** **Idea (c):** graft `sameturn_stallfeed`'s feeding of stalled castles.
3. Unchanged: 18 draws against `level1`, and `circle` (22 of 40 points).

| Candidate | Parent | Idea | Training rating (parent's) | Against parent | Holdout (parent's) | Decision |
|---|---|---|---|---|---|---|
| `endreserve_stallfeed` | sameturn_endreserve | (c) Graft from `sameturn_stallfeed`. | 1995 (1980) | 18.5/34 | 2322 (2315), 15/26 | **promoted** (the champion) |
| `endreserve_helpall` | sameturn_endreserve | (a) A castle a few turns from its next upgrade still helps pay for a neutral. | 1953 (1980) | 19/34 | not played | **rejected**: rated below its parent (4.5 points fewer against `ori_mimic`, 4 against `ori_like`), though it won the mirror match. |
| `endreserve_prod4late` | sameturn_endreserve | (b) Production 4 waits while a neutral nearer to the castle than to any enemy remains. | 1957 (1980) | 17/34 | not played | **rejected**: exactly half against its parent, rated below it. |

All three passed the gate in one `--focus` run (2,244 matches, 6.7 minutes): no failed turn, slowest turns 27 to 56 ms.

**Status changes:** `endreserve_stallfeed` active, the champion. `sameturn_endreserve` stays active (it scores 2 more against `finish_speed`). With eleven active bots, three that another active bot matches or beats everywhere on training are retired, lowest rated first: `hold_finish` (by `hold_exactstrike`), `ori_finish` (by `sameturn_endreserve` and others) and `sameturn_stallfeed` (by `endreserve_stallfeed`); eight stay active, none of them matched everywhere. With nine retired, the three lowest rated are deleted: `speed_margin` (1488), `frontline_hold` (1649) and `hold_finish` (1659).

Training maps (`iteration-29-train`, 5,712 matches, exit 0):

| Player | Rating | Score | W | D | L |
| --- | --- | --- | --- | --- | --- |
| endreserve_stallfeed | 1981 | 0.775 | 419 | 111 | 82 |
| sameturn_endreserve | 1966 | 0.760 | 408 | 114 | 90 |
| sameturn_stallfeed (retired) | 1914 | 0.705 | 341 | 181 | 90 |
| exact_sameturn (retired) | 1904 | 0.694 | 336 | 178 | 98 |
| exact_stallfeed | 1868 | 0.653 | 304 | 191 | 117 |
| ori_hold_exact | 1853 | 0.636 | 294 | 190 | 128 |
| ori_hold | 1841 | 0.621 | 280 | 200 | 132 |
| ori_finish (retired) | 1831 | 0.609 | 275 | 196 | 141 |
| ori_mimic (sparring) | 1816 | 0.591 | 263 | 197 | 152 |
| hold_exactstrike | 1812 | 0.587 | 340 | 38 | 234 |
| safe_hold (retired) | 1755 | 0.518 | 296 | 42 | 274 |
| finish_speed | 1714 | 0.469 | 265 | 44 | 303 |
| frontline | 1662 | 0.410 | 229 | 44 | 339 |
| frontline_finish (retired) | 1659 | 0.407 | 227 | 44 | 341 |
| finish_safe (retired) | 1651 | 0.399 | 224 | 40 | 348 |
| ori_like (sparring) | 1612 | 0.358 | 204 | 30 | 378 |
| level1 | 1476 | 0.149 | 0 | 162 | 382 |
| level3 | 1000 | 0.011 | 6 | 0 | 538 |
| level2 | 552 | 0.000 | 0 | 0 | 544 |

Holdout maps (`iteration-29-holdout`, 4,368 matches, exit 0):

| Player | Rating | Score | W | D | L |
| --- | --- | --- | --- | --- | --- |
| endreserve_stallfeed | 2220 | 0.814 | 342 | 78 | 48 |
| sameturn_endreserve | 2212 | 0.808 | 339 | 78 | 51 |
| sameturn_stallfeed (retired) | 2173 | 0.774 | 297 | 130 | 41 |
| exact_sameturn (retired) | 2163 | 0.765 | 293 | 130 | 45 |
| exact_stallfeed | 2093 | 0.699 | 255 | 144 | 69 |
| ori_finish (retired) | 2083 | 0.688 | 250 | 144 | 74 |
| ori_hold_exact | 2078 | 0.684 | 248 | 144 | 76 |
| ori_hold | 2030 | 0.635 | 232 | 130 | 106 |
| ori_mimic (sparring) | 2008 | 0.611 | 221 | 130 | 117 |
| hold_exactstrike | 1899 | 0.498 | 228 | 10 | 230 |
| safe_hold (retired) | 1861 | 0.459 | 210 | 10 | 248 |
| finish_safe (retired) | 1798 | 0.397 | 184 | 4 | 280 |
| frontline_finish (retired) | 1789 | 0.389 | 178 | 8 | 282 |
| frontline | 1761 | 0.363 | 166 | 8 | 294 |
| finish_speed | 1737 | 0.342 | 158 | 4 | 306 |
| ori_like (sparring) | 1672 | 0.288 | 135 | 0 | 333 |
| level1 | 1579 | 0.130 | 0 | 108 | 308 |
| level3 | 1000 | 0.005 | 2 | 0 | 414 |
| level2 | 719 | 0.000 | 0 | 0 | 416 |

**Champion:** `endreserve_stallfeed`, 1981 on training and 2220 on holdout. With three weak players gone, every rating on these tables is lower than iteration 28's for the same bot (`sameturn_endreserve` 1982 then, 1966 now): compare within a table. `level1` now rates 1476, far above `level3`: it draws 162 of its 544 games, nearly all against the `ori_` line, whose trickle freeze (iterations 26 and 28) has become a large share of its lost points.

**Where it still loses:** `level1`'s 18 draws; `circle`; `gyre` and `claw` to staged strikes.

**Time:** 10 minutes (iteration 28: 11). The gate, 2,244 matches in 6.7 minutes, is the slowest step; the holdout selection took 2 minutes (546 matches); the rest came from the cache in seconds.

## Iteration 30: a trickle the castle outgrows is no attack

**Date:** 2026-11-22. **Maps:** 17 training, 13 holdout (unchanged). **Matches:** 7,752 in the training selection round robin, 4,862 in the holdout selection. Three candidates from the champion, written one after the other. Same container as iteration 26: no outside opponent, no check against the hosted bot.

**Findings** (`endreserve_stallfeed`'s games on the training maps):

1. **Exact help is overrun by the waves that follow it.** `claw` against `hold_exactstrike` (lost in 68 turns), turns 47 to 51: castle 6 (18 soldiers, production 4) was helped with 8 against groups of 33 and 8 (the log: `help>6 (same turn) 1:8`); the attacker's castles 3 and 4 then sent 4, 4, 16 and 4 more on the next turns, while castle 7 fed the front castle 2 (`feed>2 7:10`) and castle 2 held 38 soldiers 3.6 units away; castle 6 fell on turn 51 with 1 soldier. **Idea (a):** help is priced like an attack: what the castle lacks plus half of what enemy castles that could land by the fall could send.
2. **A strike's capture is not held.** The same game: the line took the enemy's castle 0 on turn 53 with 4 soldiers and lost it on turn 57 to groups already walking there; `hold()` tops up only neutrals. **Idea (b):** `hold()` also covers enemy castles our groups will take.
3. **The trickle freeze, a third form.** 18 draws against `level1` again. Iteration 26 capped every attacked castle's spending (half against its parent), iteration 28 lifted every rule from a castle its landings wouldn't take (13 of 34: the castles spent their stock under a real strike). **Idea (c):** an enemy group counts only when it holds more soldiers than the castle produces before it lands, so a real strike still freezes the whole stock.

| Candidate | Parent | Idea | Training rating (parent's) | Against parent | Holdout (parent's) | Decision |
|---|---|---|---|---|---|---|
| `stallfeed_growtrickle` | endreserve_stallfeed | (c) An enemy group makes a castle attacked only when it holds more than the castle produces before it lands. | 2002 (1993) | 17.5/34 | 2236 (2221), 13/26 | **promoted** (the champion) |
| `stallfeed_defmargin` | endreserve_stallfeed | (a) Help adds half of what enemy castles that could land by the fall could send. | 1980 (1993) | 16/34 | not played | **rejected**: below its parent in both rules. |
| `stallfeed_holdstrike` | endreserve_stallfeed | (b) `hold()` covers enemy castles our groups will take. | 1989 (1993) | 16/34 | not played | **rejected**: below its parent in both rules. |

All three passed the gate in one `--focus` run (2,040 matches, 6.7 minutes): no failed turn, slowest turns 28 to 67 ms. `stallfeed_growtrickle` won all 34 training games and all 26 holdout games against `level1` (its parent 25 and 20) and lost a point to each of four other players on training; on holdout its row equals its parent's except against `level1`.

**Status changes:** `stallfeed_growtrickle` active, the champion. `endreserve_stallfeed` stays active (it scores more against `exact_sameturn`, `finish_safe`, `sameturn_endreserve` and `sameturn_stallfeed`). With nine active bots, the three lowest rated that another active bot matches or beats everywhere on training are retired: `frontline` (by `hold_exactstrike` and the champion), `finish_speed` and `ori_hold` (by the champion and others); six stay active. With nine retired, the three lowest rated are deleted: `finish_safe` (1652), `frontline_finish` (1671) and `frontline` (1674).

**The rating scale lost its anchor.** The deleted bots were the last players `level3` ever beat: in the final tables `level2` and `level3` win nothing, and the fit (one virtual draw each against a fixed average player) then puts both at that prior, so `level3` = 1000 no longer measures anything and every rating jumps by about 370 points. Ratings within one table still compare; ratings from here on can't be put next to earlier iterations'. Keeping a weak player that `level3` beats, or anchoring differently, is a change of the league's setup for a person to decide; it is not made here.

Training maps (`iteration-30-train`, 4,522 matches, exit 0):

| Player | Rating | Score | W | D | L |
| --- | --- | --- | --- | --- | --- |
| stallfeed_growtrickle | 2366 | 0.748 | 350 | 114 | 80 |
| endreserve_stallfeed | 2354 | 0.735 | 335 | 130 | 79 |
| sameturn_endreserve | 2345 | 0.725 | 329 | 131 | 84 |
| sameturn_stallfeed (retired) | 2278 | 0.648 | 261 | 183 | 100 |
| exact_sameturn (retired) | 2272 | 0.642 | 259 | 180 | 105 |
| exact_stallfeed | 2246 | 0.609 | 235 | 193 | 116 |
| ori_hold_exact | 2230 | 0.590 | 225 | 192 | 127 |
| ori_hold (retired) | 2220 | 0.578 | 213 | 203 | 128 |
| ori_finish (retired) | 2213 | 0.569 | 210 | 199 | 135 |
| ori_mimic (sparring) | 2198 | 0.551 | 200 | 199 | 145 |
| hold_exactstrike | 2183 | 0.533 | 274 | 32 | 238 |
| safe_hold (retired) | 2125 | 0.463 | 236 | 32 | 276 |
| finish_speed (retired) | 2117 | 0.454 | 232 | 30 | 282 |
| ori_like (sparring) | 1985 | 0.318 | 160 | 26 | 358 |
| level1 | 1931 | 0.170 | 0 | 162 | 314 |
| level2 | 1000 | 0.000 | 0 | 0 | 476 |
| level3 | 1000 | 0.000 | 0 | 0 | 476 |

Holdout maps (`iteration-30-holdout`, 3,458 matches, exit 0):

| Player | Rating | Score | W | D | L |
| --- | --- | --- | --- | --- | --- |
| stallfeed_growtrickle | 2199 | 0.803 | 291 | 86 | 39 |
| endreserve_stallfeed | 2183 | 0.788 | 279 | 98 | 39 |
| sameturn_endreserve | 2167 | 0.774 | 273 | 98 | 45 |
| sameturn_stallfeed (retired) | 2126 | 0.736 | 236 | 140 | 40 |
| exact_sameturn (retired) | 2111 | 0.721 | 230 | 140 | 46 |
| exact_stallfeed | 2035 | 0.644 | 193 | 150 | 73 |
| ori_hold_exact | 2017 | 0.625 | 185 | 150 | 81 |
| ori_finish (retired) | 2017 | 0.625 | 185 | 150 | 81 |
| ori_hold (retired) | 1968 | 0.575 | 172 | 134 | 110 |
| ori_mimic (sparring) | 1943 | 0.548 | 161 | 134 | 121 |
| hold_exactstrike | 1795 | 0.404 | 164 | 8 | 244 |
| safe_hold (retired) | 1757 | 0.370 | 150 | 8 | 258 |
| finish_speed (retired) | 1692 | 0.317 | 132 | 0 | 284 |
| level1 | 1601 | 0.148 | 0 | 108 | 256 |
| ori_like (sparring) | 1593 | 0.248 | 103 | 0 | 313 |
| level3 | 1000 | 0.005 | 2 | 0 | 362 |
| level2 | 718 | 0.000 | 0 | 0 | 364 |

**Champion:** `stallfeed_growtrickle`, 2366 on training and 2199 on holdout on the unanchored scale; in the selection (anchored as before) it was 2002 against its parent's 1993.

**Where it still loses:** `circle`; staged strikes on `gyre` and `claw` from `hold_exactstrike` and `safe_hold`; draws in the `ori_` line's mirror games.

**Time:** 11 minutes (iteration 29: 10). The gate, 2,040 matches in 6.7 minutes, is the slowest step; holdout selection 2 minutes; the rest from the cache.

## Iteration 31: nothing promoted

**Date:** 2026-11-22. **Maps:** 17 training, 13 holdout (unchanged). **Matches:** 6,358 in the training selection round robin; no holdout selection. Three candidates from the champion, written one after the other. Same container as iteration 26: no outside opponent, no check against the hosted bot.

**Findings** (`stallfeed_growtrickle`'s games on the training maps):

1. **The trickle rule judged groups one at a time.** `islands` against `finish_speed` (lost in 81 turns), turns 51 to 57: ten groups of 2 to 8 soldiers from four castles converged on home castle 0, each holding less than the castle grows before it lands, so the castle was never attacked to the bot; on turn 52 castles 2 and 4 struck castle 5 (`strike>5 exact 24 2:13 4:11`) and castle 0 fell on turn 57. **Idea (a):** the groups count together, in landing order.
2. **A neutral paid from home emptied it.** `loch` against `safe_hold` (lost in 84 turns), turn 56: home castle 0 sent 57 at a neutral of 25 (`take>7 0:57`: need(25) plus half of what nearby enemy castles could bring), needed help on turns 59 and 62 and fell on turn 67. **Idea (b):** graft `finish_safe`'s rule, a neutral no enemy castle is nearer to than our nearest sender costs need() alone.
3. **All-or-nothing help.** In both games the helpers in time could cover the first capturing landing but not every landing, and sent nothing. **Idea (c):** send all they can when it covers the first capture.
4. Unchanged: `circle` is drawn by everyone at production 4 (1,144 against 1,142 soldiers on turn 300 against `hold_exactstrike`), and mirror games inside the line end level.

| Candidate | Parent | Idea | Training rating (parent's) | Against parent | Decision |
|---|---|---|---|---|---|
| `growtrickle_partialhelp` | stallfeed_growtrickle | (c) | 2392 (2380) | 17/34 | **rejected**: exactly half against its parent, though rated above it. |
| `growtrickle_safeneutral` | stallfeed_growtrickle | (b) | 2379 (2380) | 17/34 | **rejected**: half against its parent, rated below it (4 points fewer against `ori_like`, 4 more against `hold_exactstrike`). |
| `growtrickle_cumulative` | stallfeed_growtrickle | (a) | 2374 (2380) | 16.5/34 | **rejected**: below its parent in both rules. |

All three passed the gate in one `--focus` run (1,836 matches, 7 minutes): no failed turn, slowest turns 42 to 55 ms. The ratings are on iteration 30's unanchored scale.

**Status changes:** none; the final tables (`iteration-31-train`, `iteration-31-holdout`, both exit 0) equal iteration 30's. **Champion:** `stallfeed_growtrickle`, unchanged.

**Time:** 9 minutes. The gate (7 minutes) is the slowest step; there was no holdout run.

## Iteration 32: nothing promoted, the late emptying

**Date:** 2026-11-22. **Maps:** 17 training, 13 holdout (unchanged). **Matches:** 6,358 in the training selection round robin; no holdout selection. Three candidates from the champion, written one after the other. Same container as iteration 26: no outside opponent, no check against the hosted bot.

**Findings** (`stallfeed_growtrickle`'s games on the training maps; its worst map is now `bight`, 16 of 32):

1. **The end-of-game reserve empties the rear for a late strike.** `bight` against `ori_hold` (lost on castles at the limit, 1 to 5): on turn 292 enemy castle 2 was 8 turns away at speed 2 with 8 turns left, so castles 0 and 4 counted it out of time, freed their reserves (`late reserve freed 0:889 4:889`) and fed 940 and 936 soldiers to front castle 3, which already held 1,016 and struck nothing. On turn 293 `ori_hold` bought speed 3 and struck both with 35 and 41 (`speed+strike>4 2:35 strike>0 need 41 2:41`) and took them on turns 297 and 298. The same ending lost 30 games at the limit on `bight`, `far-shores`, `archipelago` and `haven` against six bots of the line. **Ideas (a)** count an enemy castle in time at any speed it could buy this turn; **(b)** feed nothing in the last 30 turns; **(c)** read every reserve and upgrade check at the speeds an enemy castle could buy, all game.
2. `delta` against `finish_speed` (lost in 108 turns): the middle castle 2 changed hands six times, each capture leaving 2 to 7 soldiers. Not made a candidate (iteration 30's `stallfeed_holdstrike` and iteration 31's ideas were near it).

| Candidate | Parent | Idea | Training rating (parent's) | Against parent | Decision |
|---|---|---|---|---|---|
| `growtrickle_endnofeed` | stallfeed_growtrickle | (b) | 2376 (2385) | 16.5/34 | **rejected**: below its parent in both rules. |
| `growtrickle_buyspeed` | stallfeed_growtrickle | (c) | 2361 (2385) | 16/34 | **rejected**: below its parent in both rules. |
| `growtrickle_endspeed` | stallfeed_growtrickle | (a) | 2359 (2385) | 14.5/34 | **rejected**: below its parent in both rules; 4 points fewer against `endreserve_stallfeed`. |

All three passed the gate in one `--focus` run (1,836 matches, 8 minutes): no failed turn, slowest turns 56 to 120 ms. Fixing the loss that the games showed lost more of the line's mirror games than it won: the line's bots free their reserves at the same moment, and a bot that keeps its stock home then loses the race for castles at the end instead.

**Status changes:** none; the final tables (`iteration-32-train`, `iteration-32-holdout`, exit 0) equal iteration 30's. **Champion:** `stallfeed_growtrickle`, unchanged. **Nothing was promoted twice in a row:** iteration 33 starts by adding a training map and a holdout map, and one of its candidates is a founder.

**Time:** 10 minutes; the gate (8 minutes) is the slowest step.

## Iteration 33: more maps, and a founder that keeps the enemy under attack

**Date:** 2026-11-22. **Maps:** 18 training, 14 holdout: **the map set grew** before this iteration's first measurement, after two iterations that promoted nothing, with `cove` (training, `league new-map cove --seed 3301`: 12 castles, neutrals of 8, 15, 15, 20 and 30 on each side) and `mere` (holdout, seed 3302). Every rating moved with them. **Matches:** 4,788 in the baseline (266 new), 6,732 in the training selection round robin, 4,200 in the holdout selection for the one that passed. Same container as iteration 26: no outside opponent, no check against the hosted bot.

**Findings** (`stallfeed_growtrickle`'s games on the training maps; on `cove` it lost nothing and drew 3 games inside the line):

1. **What the line never does, and what it can't stand.** No `ori_` bot, and not the hosted bot whose rules they copy, buys an upgrade, pays for a neutral or a strike, or feeds the front from a castle that an enemy group is bound for (since iteration 30, a group holding more than the castle produces before it lands). Iterations 31 and 32 changed the line's defence and endgame and promoted nothing. **Idea (a), a founder:** keep one small group walking at every enemy castle, its production times the walk plus one.
2. **Captures that the next enemy castle retakes.** `delta` against `finish_speed` (lost in 108 turns): the middle castle 2 changed hands six times, each capture leaving 2 to 7 soldiers. **Ideas (b)** top up any castle below its reserve before an enemy group is bound for it; **(c)** an exact short strike also pays half of what the other enemy castles could land on the target within five turns after the capture (iteration 13's lesson, on this line).

| Candidate | Parent | Idea | Training rating (parent's) | Against parent | Holdout (parent's) | Decision |
|---|---|---|---|---|---|---|
| `harrier` | stallfeed_growtrickle | (a) A founder: every enemy castle no group of ours walks to is sent its production times the walk plus one (at most 20), from the nearest fully upgraded castle, before feeding. | 2485 (2396) | 23/36 | 2216 (2228), 12/28 | **rejected** by the holdout maps. On training it scored more than its parent against every player (8 more against `finish_speed`, 5.5 against `ori_hold`); on holdout less against `finish_speed`, `hold_exactstrike` and `safe_hold`. |
| `growtrickle_holdcapture` | stallfeed_growtrickle | (c) | 2359 (2396) | 17.5/36 | not played | **rejected**: rated below its parent. |
| `growtrickle_topup` | stallfeed_growtrickle | (b) | not counted | 16/36 | not played | **rejected**: below its parent in both rules (14 points fewer against `ori_mimic`). As played, it didn't count its own groups already walking to the castle, so it could top up the same shortfall on several turns: a flaw of the version measured, not of the idea alone. |

All three passed the gate in one `--focus` run (1,944 matches, 8 minutes): no failed turn, slowest turns 39 to 71 ms.

**Status changes:** none. **Champion:** `stallfeed_growtrickle`, unchanged. Three iterations in a row have promoted nothing; `harrier` is the third bot to rise on training and fall on holdout since iteration 13's list, so the next iteration's candidates should be stated without map geometry, and the idea of freezing the enemy's castles may come back in another form, measured from the start.

Training maps (`iteration-33-train`, 4,788 matches, exit 0):

| Player | Rating | Score | W | D | L |
| --- | --- | --- | --- | --- | --- |
| stallfeed_growtrickle | 2389 | 0.760 | 379 | 117 | 80 |
| endreserve_stallfeed | 2374 | 0.744 | 361 | 135 | 80 |
| sameturn_endreserve | 2362 | 0.731 | 354 | 134 | 88 |
| sameturn_stallfeed (retired) | 2293 | 0.653 | 280 | 192 | 104 |
| exact_sameturn (retired) | 2288 | 0.646 | 279 | 186 | 111 |
| exact_stallfeed | 2248 | 0.598 | 245 | 199 | 132 |
| ori_hold (retired) | 2234 | 0.581 | 229 | 211 | 136 |
| ori_hold_exact | 2233 | 0.580 | 235 | 198 | 143 |
| ori_finish (retired) | 2218 | 0.562 | 221 | 205 | 150 |
| ori_mimic (sparring) | 2209 | 0.551 | 214 | 207 | 155 |
| hold_exactstrike | 2194 | 0.533 | 291 | 32 | 253 |
| safe_hold (retired) | 2125 | 0.451 | 244 | 32 | 300 |
| finish_speed (retired) | 2121 | 0.446 | 242 | 30 | 304 |
| ori_like (sparring) | 1999 | 0.321 | 172 | 26 | 378 |
| level1 | 1951 | 0.179 | 0 | 180 | 324 |
| level2 | 1000 | 0.000 | 0 | 0 | 504 |
| level3 | 1000 | 0.000 | 0 | 0 | 504 |

Holdout maps (`iteration-33-holdout`, 3,724 matches, exit 0):

| Player | Rating | Score | W | D | L |
| --- | --- | --- | --- | --- | --- |
| stallfeed_growtrickle | 2224 | 0.808 | 319 | 86 | 43 |
| endreserve_stallfeed | 2206 | 0.792 | 305 | 100 | 43 |
| sameturn_endreserve | 2191 | 0.779 | 299 | 100 | 49 |
| sameturn_stallfeed (retired) | 2141 | 0.732 | 257 | 142 | 49 |
| exact_sameturn (retired) | 2127 | 0.719 | 251 | 142 | 55 |
| exact_stallfeed | 2054 | 0.645 | 213 | 152 | 83 |
| ori_hold_exact | 2030 | 0.621 | 202 | 152 | 94 |
| ori_finish (retired) | 2030 | 0.621 | 202 | 152 | 94 |
| ori_hold (retired) | 1987 | 0.576 | 190 | 136 | 122 |
| ori_mimic (sparring) | 1964 | 0.551 | 179 | 136 | 133 |
| hold_exactstrike | 1807 | 0.400 | 174 | 10 | 264 |
| safe_hold (retired) | 1772 | 0.368 | 160 | 10 | 278 |
| finish_speed (retired) | 1703 | 0.312 | 140 | 0 | 308 |
| level1 | 1635 | 0.161 | 0 | 126 | 266 |
| ori_like (sparring) | 1603 | 0.243 | 109 | 0 | 339 |
| level3 | 1000 | 0.005 | 2 | 0 | 390 |
| level2 | 718 | 0.000 | 0 | 0 | 392 |

**Time:** 14 minutes (iteration 32: 10). Adding the maps and the baseline: 1.3 minutes (266 new matches), with the holdout baseline played beside the writing of the candidates. The gate, 1,944 matches in 8 minutes, is the slowest step; holdout selection 2 minutes.

## Iteration 34: freeze the enemy's front, and freed reserves don't feed

**Date:** 2026-11-22. **Maps:** 19 training, 15 holdout: **the map set grew** again before the first measurement (nothing promoted in iterations 32 and 33, and `harrier` rose on training and fell on holdout), with `inlet` (training, `league new-map inlet --seed 3401`) and `brine` (holdout, seed 3402). **Matches:** 5,054 in the baseline (266 new), 7,106 in the training selection round robin, 5,040 in the holdout selection for the two that passed. Same container as iteration 26: no outside opponent, no check against the hosted bot.

**Findings** (`stallfeed_growtrickle`'s games on the training maps):

1. **The late emptying again, on the new map.** On `inlet` the champion lost 14 games on castles at the limit to every older bot of the line, as on `bight` in iteration 32: against `ori_hold`, turn 292, castle 0 fed 920 soldiers to the front (`feed>2 0:920 late reserve freed 0:869`), and was taken on turn 297. Iteration 32 stopped all feeding in the last 30 turns and lost the mirror match. **Idea (a), another form:** feeding keeps the reserve against every enemy castle; the freed reserve pays only for strikes.
2. **`harrier` (iteration 33) froze the whole enemy and traded soldiers with bots that don't freeze.** It lost holdout points to the `hold_` line, which keeps upgrading and striking under attack. **Ideas, two forms of the founder, without map geometry:** (b) harass only the enemy castle nearest ours, the one its staging and strikes come from; (c) harass only enemy castles that could pay their next upgrade now.

| Candidate | Parent | Idea | Training rating (parent's) | Against parent | Holdout (parent's) | Decision |
|---|---|---|---|---|---|---|
| `harrier_front` | stallfeed_growtrickle | (b) A founder: one group walks at the enemy castle nearest ours, its production times the walk plus one (at most 20), from the nearest fully upgraded castle, before feeding. | 2477 (2397) | 25/38 | 2216 (2165), 17/30 | **promoted** (the champion) |
| `growtrickle_feedkeep` | stallfeed_growtrickle | (a) Feeding keeps the reserve against every enemy castle at any turn. | 2401 (2397) | 19.5/38 | 2248 (2165), 21.5/30 | **promoted** |
| `harrier_upgrades` | stallfeed_growtrickle | (c) A founder: groups only at enemy castles that could pay their next production or speed level. | 2389 (2397) | 17/38 | not played | **rejected**: below its parent in both rules, though it took 8 more points from `finish_speed` and 6 from `hold_exactstrike`. |

All three passed the gate in one `--focus` run (2,052 matches, 8 minutes): no failed turn, slowest turns 24 to 33 ms.

**Status changes:** `harrier_front` and `growtrickle_feedkeep` active; `harrier_front`, first on training, is the champion (`growtrickle_feedkeep` is first on holdout). `stallfeed_growtrickle` stays active (`harrier_front` scores a point less than it against `ori_like`; `growtrickle_feedkeep` less against several). With eight active bots, the two lowest rated that another active bot matches or beats everywhere are retired: `hold_exactstrike` and `ori_hold_exact` (both by `harrier_front`, which also matches `exact_stallfeed`); six stay active. With eight retired, the two lowest rated were to be deleted, `finish_speed` (2131) and `safe_hold` (2140); `finish_speed` is deleted, but `safe_hold` stays, retired, as a seventh: `tests/test_tools.py` replays it by name, so deleting it failed `scripts/check.sh` (found after this iteration's commit, fixed in the next one). A test that needs a bot of the population is for a person to change; until then `safe_hold` is kept.

Training maps (`iteration-34-train`, with `safe_hold`, exit 0):

| Player | Rating | Score | W | D | L |
| --- | --- | --- | --- | --- | --- |
| harrier_front | 2458 | 0.789 | 435 | 150 | 61 |
| growtrickle_feedkeep | 2387 | 0.717 | 390 | 146 | 110 |
| stallfeed_growtrickle | 2380 | 0.709 | 383 | 150 | 113 |
| endreserve_stallfeed | 2369 | 0.696 | 367 | 165 | 114 |
| sameturn_endreserve | 2358 | 0.683 | 362 | 159 | 125 |
| sameturn_stallfeed (retired) | 2300 | 0.616 | 283 | 230 | 133 |
| exact_sameturn (retired) | 2290 | 0.604 | 280 | 221 | 145 |
| exact_stallfeed | 2249 | 0.556 | 242 | 234 | 170 |
| ori_hold (retired) | 2246 | 0.552 | 233 | 247 | 166 |
| ori_hold_exact (retired) | 2236 | 0.539 | 233 | 231 | 182 |
| ori_finish (retired) | 2229 | 0.532 | 225 | 237 | 184 |
| ori_mimic (sparring) | 2227 | 0.529 | 220 | 244 | 182 |
| hold_exactstrike (retired) | 2187 | 0.481 | 295 | 32 | 319 |
| safe_hold (retired) | 2116 | 0.402 | 244 | 32 | 370 |
| ori_like (sparring) | 1980 | 0.277 | 165 | 28 | 453 |
| level1 | 1952 | 0.158 | 0 | 180 | 390 |
| level2 | 1000 | 0.000 | 0 | 0 | 570 |
| level3 | 1000 | 0.000 | 0 | 0 | 570 |

Holdout maps (`iteration-34-holdout`, with `safe_hold`, exit 0):

| Player | Rating | Score | W | D | L |
| --- | --- | --- | --- | --- | --- |
| growtrickle_feedkeep | 2209 | 0.813 | 357 | 115 | 38 |
| harrier_front | 2177 | 0.784 | 344 | 112 | 54 |
| stallfeed_growtrickle | 2125 | 0.734 | 310 | 129 | 71 |
| endreserve_stallfeed | 2112 | 0.721 | 295 | 145 | 70 |
| sameturn_endreserve | 2095 | 0.703 | 286 | 145 | 79 |
| sameturn_stallfeed (retired) | 2051 | 0.657 | 243 | 184 | 83 |
| exact_sameturn (retired) | 2041 | 0.645 | 237 | 184 | 89 |
| exact_stallfeed | 1966 | 0.563 | 193 | 188 | 129 |
| ori_finish (retired) | 1956 | 0.551 | 188 | 186 | 136 |
| ori_hold_exact (retired) | 1947 | 0.541 | 182 | 188 | 140 |
| ori_hold (retired) | 1925 | 0.518 | 177 | 174 | 159 |
| ori_mimic (sparring) | 1911 | 0.502 | 170 | 172 | 168 |
| hold_exactstrike (retired) | 1761 | 0.351 | 174 | 10 | 326 |
| safe_hold (retired) | 1739 | 0.331 | 164 | 10 | 336 |
| ori_like (sparring) | 1655 | 0.265 | 135 | 0 | 375 |
| level1 | 1644 | 0.160 | 0 | 144 | 306 |
| level3 | 1000 | 0.004 | 2 | 0 | 448 |
| level2 | 719 | 0.000 | 0 | 0 | 450 |

**Champion:** `harrier_front`, 2458 on training and 2177 on holdout (`stallfeed_growtrickle` 2380 and 2125 in the same tables). The training table's scale is still unanchored (`level3` wins nothing there); on holdout `level3` won 2 games.

**Where it still loses:** `circle` and the line's mirror draws; against `ori_like` it scored a point less than its parent. Whether freezing the enemy's front pays against the hosted bot, whose rules it is aimed at, is the question the check against the real opponent should answer before it is trusted.

**Time:** 15 minutes (iteration 33: 14). Maps and baseline 1 minute; gate 8 minutes (the slowest step); holdout selection 4.7 minutes (1,050 matches: two candidates and two new holdout maps).

## Iteration 35: the freeze with feeding that keeps the reserve

**Date:** 2026-11-22. **Maps:** 19 training, 15 holdout (unchanged since iteration 34). **Matches:** 7,866 in the training selection round robin, 5,610 in the holdout selection for the two that passed. Three candidates from the champion, written one after the other. Same container as iteration 26: no outside opponent, no check against the hosted bot.

**Findings** (`harrier_front`'s games on the training maps):

1. **The late draws.** `rill` and `inlet` gave 22 non-wins each, all draws at the limit inside the line; `growtrickle_feedkeep`, promoted beside it in iteration 34, rose 83 points on holdout with the ending they come from. **Idea (a):** graft its feeding rule.
2. **A harassment group takes a castle it was sent to freeze.** `claw` against `ori_finish` (lost in 76 turns): the middle castle 2 changed hands ten times from turn 29 to turn 70, each capture leaving 0 to 8 soldiers; groups of production-times-walk-plus-one land on a castle that was just emptied and take it, and the enemy's next castle along retakes it. **Idea (b):** don't send a harassment group that would take the castle.
3. **Strikes come in waves** (iteration 30's `claw` game: 33 and 8, then 4, 4, 16 and 4 more). **Idea (c):** also keep under attack every enemy castle whose groups are walking at ours.

| Candidate | Parent | Idea | Training rating (parent's) | Against parent | Holdout (parent's) | Decision |
|---|---|---|---|---|---|---|
| `harrier_feedkeep` | harrier_front | (a) Graft from `growtrickle_feedkeep`. | 2497 (2462) | 23/38 | 2226 (2169), 20.5/30 | **promoted** (the champion) |
| `harrier_attackers` | harrier_front | (c) | 2463 (2462) | 19.5/38 | 2177 (2169), 15.5/30 | **promoted**: it passed every rule, the training ones by the smallest margins possible. |
| `harrier_nocapture` | harrier_front | (b) | 2462 (2462) | 19/38 | not played | **rejected**: it played every training game as its parent did (an identical row; the skip never changed a game), so half against its parent; and one turn took 245 ms, over the gate's 200. |

The gate ran as one `--focus` run (2,166 matches, 9 minutes): no failed turn, slowest turns 43 and 68 ms for the two promoted.

**Status changes:** `harrier_feedkeep` and `harrier_attackers` active; `harrier_feedkeep` is the champion. `harrier_front` stays active (`harrier_feedkeep` scores less than it against `sameturn_endreserve` and `stallfeed_growtrickle`). With eight active bots, `exact_stallfeed`, matched or beaten everywhere by six others, is retired; seven stay active. With eight retired, the two lowest rated that may be deleted are: `hold_exactstrike` (2194) and `ori_finish` (2239); `safe_hold` (2130) is lower but stays, since `tests/test_tools.py` replays it (iteration 34). The `hold_` line is now `safe_hold` alone.

Training maps (`iteration-35-train`, 5,700 matches, exit 0):

| Player | Rating | Score | W | D | L |
| --- | --- | --- | --- | --- | --- |
| harrier_feedkeep | 2470 | 0.781 | 443 | 123 | 80 |
| harrier_front | 2437 | 0.748 | 398 | 171 | 77 |
| harrier_attackers | 2436 | 0.747 | 400 | 165 | 81 |
| growtrickle_feedkeep | 2375 | 0.682 | 358 | 165 | 123 |
| stallfeed_growtrickle | 2360 | 0.666 | 349 | 162 | 135 |
| sameturn_endreserve | 2351 | 0.655 | 338 | 170 | 138 |
| endreserve_stallfeed | 2348 | 0.652 | 333 | 176 | 137 |
| sameturn_stallfeed (retired) | 2275 | 0.567 | 251 | 231 | 164 |
| exact_sameturn (retired) | 2267 | 0.557 | 249 | 222 | 175 |
| exact_stallfeed (retired) | 2226 | 0.510 | 217 | 225 | 204 |
| ori_hold (retired) | 2225 | 0.509 | 209 | 240 | 197 |
| ori_hold_exact (retired) | 2214 | 0.497 | 213 | 216 | 217 |
| ori_mimic (sparring) | 2206 | 0.488 | 198 | 234 | 214 |
| safe_hold (retired) | 2115 | 0.390 | 238 | 28 | 380 |
| ori_like (sparring) | 1949 | 0.251 | 148 | 28 | 470 |
| level1 | 1934 | 0.140 | 0 | 160 | 410 |
| level2 | 1000 | 0.000 | 0 | 0 | 570 |
| level3 | 1000 | 0.000 | 0 | 0 | 570 |

Holdout maps (`iteration-35-holdout`, 4,500 matches, exit 0):

| Player | Rating | Score | W | D | L |
| --- | --- | --- | --- | --- | --- |
| harrier_feedkeep | 2176 | 0.786 | 336 | 130 | 44 |
| growtrickle_feedkeep | 2165 | 0.775 | 328 | 135 | 47 |
| harrier_attackers | 2124 | 0.735 | 306 | 138 | 66 |
| harrier_front | 2116 | 0.727 | 302 | 138 | 70 |
| stallfeed_growtrickle | 2076 | 0.685 | 277 | 145 | 88 |
| endreserve_stallfeed | 2060 | 0.668 | 260 | 161 | 89 |
| sameturn_endreserve | 2039 | 0.644 | 248 | 161 | 101 |
| sameturn_stallfeed (retired) | 1992 | 0.592 | 208 | 188 | 114 |
| exact_sameturn (retired) | 1987 | 0.586 | 205 | 188 | 117 |
| exact_stallfeed (retired) | 1913 | 0.504 | 167 | 180 | 163 |
| ori_hold_exact (retired) | 1895 | 0.484 | 157 | 180 | 173 |
| ori_hold (retired) | 1888 | 0.476 | 158 | 170 | 182 |
| ori_mimic (sparring) | 1875 | 0.463 | 153 | 166 | 191 |
| safe_hold (retired) | 1718 | 0.314 | 160 | 0 | 350 |
| ori_like (sparring) | 1637 | 0.253 | 129 | 0 | 381 |
| level1 | 1619 | 0.142 | 0 | 128 | 322 |
| level3 | 1000 | 0.004 | 2 | 0 | 448 |
| level2 | 719 | 0.000 | 0 | 0 | 450 |

**Champion:** `harrier_feedkeep`, 2470 on training and 2176 on holdout; `harrier_front` 2437 and 2116 in the same tables. On holdout, where `level3` still wins 2 games, the champion of iteration 25 (`ori_hold`, 1888 here) is 288 points behind it.

**Where it still loses:** `circle` (the line draws it with everyone at production 4) and the mirror draws inside the line; `claw`'s middle castle; whether the freeze pays against the hosted bot itself is untested.

**Time:** 16 minutes (iteration 34: 15). The gate, 2,166 matches in 9 minutes, and the holdout selection, 1,110 matches in 5.6 minutes, are the slowest steps: the population and the map set grew, so each candidate plays about 700 matches.

## Iterations 26 to 35, in one container: what to carry forward

- **The check against the real opponent was not played in any of them.** Eleven bots were promoted on the league's rules alone (`ori_hold_exact`, `exact_sameturn`, `exact_stallfeed`, `sameturn_endreserve`, `sameturn_stallfeed`, `endreserve_stallfeed`, `stallfeed_growtrickle`, `harrier_front`, `growtrickle_feedkeep`, `harrier_feedkeep`, `harrier_attackers`). Before `harrier_feedkeep` is trusted, it and `ori_hold` should play the hosted bot in the same session; the `harrier` bots are aimed at the hosted bot's own rule and may do better or worse there than in the league.
- **No outside opponent played.** The player's bot (`opponents.local.toml`) wasn't in this container.
- **The training scale has lost its anchor** since iteration 30: `level3` and `level2` win no training game, so their ratings are the fit's prior. Within a table ratings compare; across iterations they don't. The holdout scale still has 2 wins for `level3`.
- **`tests/test_tools.py` depends on `safe_hold`**, a bot the population rules would have deleted in iteration 34.
- **Time:** the ten iterations took 2 hours 14 minutes, from 19:36 to 21:50, the first of them 25 minutes (an empty cache). Every later iteration was 8 to 16 minutes, nearly all of it playing the gate and the holdout selection at about 4 to 7 matches a second on 4 CPUs.

## Setup after iteration 35: the ratings anchored on `ori_mimic`

**Date:** 2026-11-22. A change of the league's setup, made between iterations and measured with a full tournament on both sets of maps. No bot changed.

**Why.** From iteration 30 the population rules had deleted every bot `level3` ever beat (`frontline`, `frontline_finish` and `finish_safe` in iteration 30, then `finish_speed` and `hold_exactstrike`). In the training tables `level2` and `level3` won no game, so the fit put both at its prior (the one drawn game every player gets against an average player), both printed 1000, and with `level3` fixed at 1000 every rating rose about 370 points. Ratings still compared within a table, but not across iterations, and the champion's rating stopped measuring the league's progress.

**What changed:**

- **The anchor is `ori_mimic` at 1800** (`league_tools/ratings.py`, `RATING_ANCHORS`). It is a sparring bot: never changed, never deleted, and it scores about half its games against the whole field (0.488 on training, 0.463 on holdout), so its games, not the prior, place it. 1800 is about its rating in the training tables of iterations 24 to 29 (1764 to 1829), the last ones in which `level3` still won games, so the training scale goes on from those. On holdout it stood at 1943 to 2101 then, so holdout ratings read about 200 to 300 lower than in those iterations. A tournament without `ori_mimic` has `level3` at 1000; one without either has its mean at 1000. The shift moves every rating in a table by the same amount, so no comparison inside a table changes, and no earlier selection would have gone otherwise.
- **`ori_mimic` is never to change**, since its code holds the scale: a better imitation of the hosted bot is a new sparring bot. When its score in the whole population's tables falls toward 0.1 the anchor needs moving again, as a change of the setup (README, Ratings).
- **The replay test plays a bot of its own.** `tests/test_tools.py::test_a_bot_replayed_on_boards_it_made_agrees_fully` replayed `safe_hold` by name, so deleting `safe_hold` under the six-retired rule failed `scripts/check.sh` (iteration 34). It now replays a fixture bot defined in the test, and fails if that bot's send differs by one soldier. `safe_hold` stays retired for now, a seventh retired bot. The next iteration's rules may delete it like any other.

**Measured.** The same population as iteration 35, every match played again (empty cache). Every pair, map and side gave the result iteration 35 recorded: the W/D/L columns are equal row for row. Only the scale moved: training ratings are 406 lower than in iteration 35's table (`harrier_feedkeep` 2470 → 2064), holdout 75 lower (2176 → 2102). On holdout several bots had single turns over 200 ms (`exact_sameturn` 465, `stallfeed_growtrickle` 330, `ori_hold_exact` 329, `ori_hold` 327, `harrier_front` 221, `safe_hold` 208) with no failed turn and the same results. That is the run on a busy 4-CPU container, not changed code (no bot changed), but the next iteration's gate should watch it.

Training maps (`setup-36-train`, 5,700 matches, exit 0):

| Player | Rating | Score | W | D | L |
| --- | --- | --- | --- | --- | --- |
| harrier_feedkeep | 2064 | 0.781 | 443 | 123 | 80 |
| harrier_front | 2031 | 0.748 | 398 | 171 | 77 |
| harrier_attackers | 2030 | 0.747 | 400 | 165 | 81 |
| growtrickle_feedkeep | 1969 | 0.682 | 358 | 165 | 123 |
| stallfeed_growtrickle | 1954 | 0.666 | 349 | 162 | 135 |
| sameturn_endreserve | 1945 | 0.655 | 338 | 170 | 138 |
| endreserve_stallfeed | 1942 | 0.652 | 333 | 176 | 137 |
| sameturn_stallfeed (retired) | 1869 | 0.567 | 251 | 231 | 164 |
| exact_sameturn (retired) | 1861 | 0.557 | 249 | 222 | 175 |
| exact_stallfeed (retired) | 1820 | 0.510 | 217 | 225 | 204 |
| ori_hold (retired) | 1819 | 0.509 | 209 | 240 | 197 |
| ori_hold_exact (retired) | 1808 | 0.497 | 213 | 216 | 217 |
| ori_mimic (sparring) | 1800 | 0.488 | 198 | 234 | 214 |
| safe_hold (retired) | 1709 | 0.390 | 238 | 28 | 380 |
| ori_like (sparring) | 1543 | 0.251 | 148 | 28 | 470 |
| level1 | 1528 | 0.140 | 0 | 160 | 410 |
| level2 | 594 | 0.000 | 0 | 0 | 570 |
| level3 | 594 | 0.000 | 0 | 0 | 570 |

Holdout maps (`setup-36-holdout`, 4,500 matches, exit 0):

| Player | Rating | Score | W | D | L |
| --- | --- | --- | --- | --- | --- |
| harrier_feedkeep | 2102 | 0.786 | 336 | 130 | 44 |
| growtrickle_feedkeep | 2090 | 0.775 | 328 | 135 | 47 |
| harrier_attackers | 2049 | 0.735 | 306 | 138 | 66 |
| harrier_front | 2042 | 0.727 | 302 | 138 | 70 |
| stallfeed_growtrickle | 2001 | 0.685 | 277 | 145 | 88 |
| endreserve_stallfeed | 1985 | 0.668 | 260 | 161 | 89 |
| sameturn_endreserve | 1964 | 0.644 | 248 | 161 | 101 |
| sameturn_stallfeed (retired) | 1917 | 0.592 | 208 | 188 | 114 |
| exact_sameturn (retired) | 1912 | 0.586 | 205 | 188 | 117 |
| exact_stallfeed (retired) | 1838 | 0.504 | 167 | 180 | 163 |
| ori_hold_exact (retired) | 1820 | 0.484 | 157 | 180 | 173 |
| ori_hold (retired) | 1813 | 0.476 | 158 | 170 | 182 |
| ori_mimic (sparring) | 1800 | 0.463 | 153 | 166 | 191 |
| safe_hold (retired) | 1643 | 0.314 | 160 | 0 | 350 |
| ori_like (sparring) | 1562 | 0.253 | 129 | 0 | 381 |
| level1 | 1544 | 0.142 | 0 | 128 | 322 |
| level3 | 925 | 0.004 | 2 | 0 | 448 |
| level2 | 644 | 0.000 | 0 | 0 | 450 |

**Champion:** `harrier_feedkeep`, 2064 on training and 2102 on holdout on the new scale. On training it is 264 above `ori_mimic`. In iteration 29's table, the last one where `level3` still won training games, the champion `endreserve_stallfeed` was 165 above it (1981 against 1816), on fewer maps. That is the progress of iterations 30 to 35 in the one measure that spans them. `level2` and `level3` (594 on training) still win nothing there. Their ratings are the prior's and mean nothing.

## Iteration 36: seeded randomness, and the frozen game

**Date:** 2026-11-23. **Maps:** 19 training, 15 holdout (unchanged). **Matches:** 5,700 in the baseline (`iteration-36-before`, equal to the training table of the setup after iteration 35 match for match), 7,866 in the training selection (7,106 when re-rated with the tournament tool of #16), 5,040 in the holdout selection for the one that passed. Two candidates from the champion, written one after the other. As in iterations 26 to 35: no outside opponent, no check against the hosted bot. The number was claimed with `scripts/claim-iteration.sh` at about 00:47, after the real-game iteration that was to be 36 was cancelled; the baseline (from 00:33) and the two candidates were made before the claim, while that run was still going, and nothing measured in between was kept without the claim.

**The idea it tests: seeded randomness.** The hosted bot of the real games is said to randomize some of its actions from a seed (by a person, not yet read off its games), so that it can't be predicted; every league bot is deterministic, and its code is public. A league bot may not use `random` or a clock, and a league match must replay exactly for its cached result to stay true, so the candidates' seed comes from the turn itself, is drawn on the first turn and is kept in memory (48 bits as hex, under what a JSON number keeps exactly), and the dice are splitmix64 written into the bot:

- in a game with a turn deadline (every real game), the seed mixes the game's id, the team and the first deadline: each real game draws a new one;
- without deadlines (the headless runner), it mixes the first board and the team: a league match replays exactly. The runner's game id is the match's place in the run's schedule, so a seed from it would make a league result depend on which matches the run played.
- The game's id and deadline are no secret from the opponent: a seed nobody can compute would need the hosted bot's handler (`hosting/lambda/`) to put a secret one in the memory of a game's first turn. Not done.

**Findings** (`harrier_feedkeep`'s games on the training maps):

1. **The mirror freeze.** 56 of its 123 draws end with identical castles and soldiers on both sides. `reef` against `growtrickle_feedkeep` (both sides): 3 castles each from turn 21, both logs "saving" from turn 51 to turn 286 with every castle at production 4 and speed 2 (turn 150: 436, 528 and 432 soldiers in each side's castles), then the end-of-game strikes cross in the field and the game is drawn at 2,088 each. **Cause:** each castle's reserve is sized against the strongest enemy castle, which grows exactly as fast as it does; no deterministic rule on either side ever breaks the symmetry. **Idea (a):** a strike at a seeded moment once the game has frozen.
2. **Every tie is broken by the castle id**, so an opponent with the code knows each equal choice in advance. **Idea (b):** break ties with a seeded shuffle.

Before this iteration (against the iteration-25 population, in a worktree that hadn't seen iterations 26 to 35, so not an iteration of the ledger) the same two ideas were tried on `ori_hold`: the seeded freeze strike, from every frozen game, beat it 22 of 34 and took its draws from 106 to 64; the tie shuffle beat it 18.5 of 34; a third, the target drawn among those within 10% of the cheapest, took exactly 17 of 34.

| Candidate | Parent | Idea | Training rating (parent's) | Against parent | Holdout (parent's) | Decision |
|---|---|---|---|---|---|---|
| `feedkeep_stall` | harrier_feedkeep | (a) Once no castle changed hands for 20 turns, no neutral is left and the bot holds fewer castles than the enemy, each turn has a seeded 1-in-5 chance of a strike at the cheapest enemy castle from all the senders' soldiers, reserve included. | 2056 (2053) | 20/38 | 2083 (2094), 15/30 | **rejected**: below its parent on the holdout maps. |
| `feedkeep_dice` | harrier_feedkeep | (b) Every tie the castle id broke is broken by a per-turn shuffle drawn from the seed. | 2001 (2053) | 19/38 | not played | **rejected**: half against its parent and below it. |

`feedkeep_stall` was tuned once on the training maps, before any holdout game: from every frozen game (not only from behind) it beat its parent 22 of 38 and rated 2021 against 2047; against the parent's games it turned 18 losses at the limit into wins (`crossing`, `shelf`) and 20 wins at the limit and 18 draws into eliminations (`sound`, `islands`). Behind only, its changed games were `crossing` (5 losses into wins), `haven` (one loss into a win, two wins into losses), `claw` (four wins and two draws into losses) and `archipelago` (one each way). The freeze draws on `reef`, `rill` and `circle` didn't change in either form: the strike from a level freeze (`reef`, turn 63, 339 soldiers from three castles) was met by the defender's help and changed no castle.

The gate: no failed turn, slowest turns 47 to 86 ms.

**Status changes:** none. Both candidates are deleted; the champion is unchanged.

Training maps (`iteration-36-train`, 5,700 matches, exit 0; equal to the setup's after iteration 35):

| Player | Rating | Score | W | D | L |
| --- | --- | --- | --- | --- | --- |
| harrier_feedkeep | 2064 | 0.781 | 443 | 123 | 80 |
| harrier_front | 2031 | 0.748 | 398 | 171 | 77 |
| harrier_attackers | 2030 | 0.747 | 400 | 165 | 81 |
| growtrickle_feedkeep | 1969 | 0.682 | 358 | 165 | 123 |
| stallfeed_growtrickle | 1954 | 0.666 | 349 | 162 | 135 |
| sameturn_endreserve | 1945 | 0.655 | 338 | 170 | 138 |
| endreserve_stallfeed | 1942 | 0.652 | 333 | 176 | 137 |
| sameturn_stallfeed (retired) | 1869 | 0.567 | 251 | 231 | 164 |
| exact_sameturn (retired) | 1861 | 0.557 | 249 | 222 | 175 |
| exact_stallfeed (retired) | 1820 | 0.510 | 217 | 225 | 204 |
| ori_hold (retired) | 1819 | 0.509 | 209 | 240 | 197 |
| ori_hold_exact (retired) | 1808 | 0.497 | 213 | 216 | 217 |
| ori_mimic (sparring) | 1800 | 0.488 | 198 | 234 | 214 |
| safe_hold (retired) | 1709 | 0.390 | 238 | 28 | 380 |
| ori_like (sparring) | 1543 | 0.251 | 148 | 28 | 470 |
| level1 | 1528 | 0.140 | 0 | 160 | 410 |
| level2 | 594 | 0.000 | 0 | 0 | 570 |
| level3 | 594 | 0.000 | 0 | 0 | 570 |

Holdout maps (`iteration-36-holdout`, 4,500 matches, exit 0; equal to the setup's after iteration 35):

| Player | Rating | Score | W | D | L |
| --- | --- | --- | --- | --- | --- |
| harrier_feedkeep | 2102 | 0.786 | 336 | 130 | 44 |
| growtrickle_feedkeep | 2090 | 0.775 | 328 | 135 | 47 |
| harrier_attackers | 2049 | 0.735 | 306 | 138 | 66 |
| harrier_front | 2042 | 0.727 | 302 | 138 | 70 |
| stallfeed_growtrickle | 2001 | 0.685 | 277 | 145 | 88 |
| endreserve_stallfeed | 1985 | 0.668 | 260 | 161 | 89 |
| sameturn_endreserve | 1964 | 0.644 | 248 | 161 | 101 |
| sameturn_stallfeed (retired) | 1917 | 0.592 | 208 | 188 | 114 |
| exact_sameturn (retired) | 1912 | 0.586 | 205 | 188 | 117 |
| exact_stallfeed (retired) | 1838 | 0.504 | 167 | 180 | 163 |
| ori_hold_exact (retired) | 1820 | 0.484 | 157 | 180 | 173 |
| ori_hold (retired) | 1813 | 0.476 | 158 | 170 | 182 |
| ori_mimic (sparring) | 1800 | 0.463 | 153 | 166 | 191 |
| safe_hold (retired) | 1643 | 0.314 | 160 | 0 | 350 |
| ori_like (sparring) | 1562 | 0.253 | 129 | 0 | 381 |
| level1 | 1544 | 0.142 | 0 | 128 | 322 |
| level3 | 925 | 0.004 | 2 | 0 | 448 |
| level2 | 644 | 0.000 | 0 | 0 | 450 |

**Champion:** `harrier_feedkeep`, 2064 on training and 2102 on holdout, as in the setup after iteration 35 (`ori_mimic` at 1800).

**Where it still loses:** the level frozen games inside the line, which a strike from everything breaks against itself (it pays only from behind, and then too little to hold on the holdout maps); `circle`; `claw`'s middle castle. The randomness the league can't measure: its opponents don't learn, so an unpredictable bot gains nothing here that a deterministic one lacks. What a seed buys is measured against an opponent that adapts, the hosted bot, which no iteration plays.

**Time:** 39 minutes to the final tables, from 00:33 to 01:12, and 8 more to rebase onto the new rating anchor and re-rate every table from the cache (iteration 35: 16). The baseline (17 minutes, 5,088 of 5,700 matches played) and the holdout selection (13 minutes, 4,572 of 5,040 played) are the slowest steps, because this worktree's cache had none of the results of iterations 26 to 35, played in another container; the gate took 4 minutes and the training selection seconds. **Speed-up:** an iteration should start from the cache of the one before it: with it, this iteration's two long runs would have played about 1,100 matches instead of 9,700. The real-game iteration now restores one (`.github/actions/league-cache`); a session in a new worktree should link or copy the main checkout's `runs/cache/` first, as this one did. Its ratings were played before `ori_mimic` became the anchor and re-rated from the cache with the new tools afterwards: every decision is the same on both scales.

## Iteration 37: three real losses on claw, and help that buys speed

**Date:** 2026-11-23. **Maps:** 19 training, 15 holdout (unchanged). **Matches:** 5,700 in the baseline (`iteration-37-before`, all from the cache that the runners played, equal to iteration 36's training table row for row). Split across runners: the population's round robin was played on every map by other runners; this first half ran steps 0 to 3 and step 4's head-to-head. The number was claimed by the automated iteration's workflow. Started by the hosted bot's real games 471, 472 and 473; six candidates, written in parallel by subagents (Sonnet).

**Real games studied** (all three on `claw`, all lost by elimination to another player's hosted bot, our bot as team 1; the second half doesn't have them, so what they showed is here):

- **471** (the hosted bot was `ori_hold`, 136 turns): our home bought production 2 and 3 on turns 1 and 2 and sent its first neutral attack on turn 6, the opponent on turn 2. On turn 17 the middle castle 4 was paid from home, 5.8 away (12 turns at speed 1), with 4 from castle 5 (`take>4 5:4 0:18`), while castle 3, 3.2 away with 9 soldiers, was saving for production 2 (bought on turn 18). It was taken on turn 28 with 12 and lost on turn 30 to 18 sent on turn 24 from the opponent's castle 3.2 away. From turn 25 to 78 the middle castles were retaken six times, nearly always with 3 soldiers, from groups paid mostly by the home castle 5 to 5.8 away and leaving on different turns, and each was lost within 1 to 8 turns to batches of 12 fed from castles 3.2 to 3.6 away; 282 of the 310 soldiers it sent at others went at those two castles. From turn 85 to 136 it logged `saving` every turn: at turn 106 its three castles held 84, 138 and 92 (314) while the opponent fed castle 4 to 274; on turn 107 it struck castle 3 from two castles (177 and 45) and took it at turn 110 while the other two held 188 idle, then castle 0 (turn 122) and castle 5 (turn 136). Turns 39 to 42: castle 2 taken with 3 fell to a group of 11; castle 5 had 10 to 16 at speed 1 (8 turns), too slow to help, and bought production 3 on turn 44.
- **472** (`harrier_feedkeep`, 129 turns): the same opening (`take>4 5:4 0:18` on turn 17, castle 4 lost at turn 30). Ten captures of a middle castle from turn 28 to 74, most with 2 soldiers (exact strikes of target plus 2: `strike>4 exact 2 3:2`, `strike>2 exact 5 5:3 3:2`), each retaken within 1 to 6 turns, often by groups from two enemy castles at once. Turns 77 to 90: the opponent held castle 4 from turn 70, fed it 12 at a time from two castles every three turns, bought production 4 and speed 3 there, grew it from 14 to 82, and on turn 88 struck our border castle 3 (35) with 45 and 6; it fell at turn 90 with 41, while our castles held 115 and castles 3 and 5 trickled 34 soldiers into exact strikes on castle 2 between turns 79 and 89 (`strike>2 exact 10 5:8 3:2`). Production went from 11 against 16 to 8 against 19. Then `saving` from turn 96 to 129 on two castles (252 soldiers at turn 121) while one enemy castle of 324 beside both took them one at a time (turns 123, 129), each strike smaller than our two castles together. Its three harassment groups (7, 10, 13) froze nothing: the 7 died in a clash with a feed batch, and the opponent upgraded the target while it walked.
- **473** (`harrier_feedkeep`, 118 turns): the same opening, castle 4 lost at turn 30. 47 groups (375 soldiers) at the middle castles, 36 of them of 10 or fewer; 8 of 10 captures landed with exactly 2; turns 83 to 93 five strikes of 7 or 8 at castle 2 (3 to 5 soldiers), each answered by a top-up of 5 from the opponent's castle 4, one turn nearer. **The deciding turns, read again here:** on turns 83 and 86 `feed>3 0:12 5:12` left castles 0 and 5 with 4 each while the opponent's castle 4 showed 13 soldiers on the board with 37 of its own soldiers landing on it the next turn and 36 more walking in (54 on turn 87); on turn 87 it struck castle 5 with 43 and 12; our help held the first wave (`help>5 3:22 0:6`), the second (33 and 12 on turn 90) took castle 5 at turn 95, defence being 3 soldiers short of what helpers in time could give and sending nothing. From turn 96 the last two castles saved (reserves above their whole stock) while the opponent produced 21 to 26 a turn to our 8; on turn 107 it struck castle 3 from three castles at once (162) and defence sent nothing (castle 0 had 82 but only 14 above its reserve), harassing a castle of 91 with 13 instead.

What the three show in common: **the race for `claw`'s middle castles was lost on turn 17 to a long walk from home while the near castle saved for an upgrade**; **captures sized to take (plus 2), not to hold**, retaken within a few turns, again and again; **a border castle emptied by feeding or upgrading beside an enemy castle that the board showed small but whose own feed batches were landing on it**; and at the end **soldiers frozen in separate castles by reserves against one big enemy stack**, taken one by one. The harassment groups froze nothing against this opponent (it upgrades and feeds under them) and were mostly lost in clashes with its batches. Checked against the lessons from earlier real games: long walks, trickled attacks, the thin border castle, batches and strikes from two or three castles at once all recur; "an upgrade beside a stocked enemy castle" was seen (472 turn 77, 473 turn 86) but didn't decide either game.

**Measured:** champion `harrier_feedkeep`, **2064** on training (iteration 36: 2064), 0.781, 443 W 123 D 80 L. Its pair row: 20/38 against `sameturn_endreserve`, 23 against `harrier_front` and `growtrickle_feedkeep`, 24 against `stallfeed_growtrickle`, 25 against `harrier_attackers` and `endreserve_stallfeed`, 31 to 38 against the rest. Its map row is worst on `reef` 17/34, `circle` 20, `cove` and `rill` 22, `claw` and `shelf` 23. Its shortest losses are on `claw` (to `ori_mimic` in 80 turns, to `ori_like` in 89, to `safe_hold`, `harrier_front` and `harrier_attackers` in 94 to 102) and `firth` as team 1 (to eight bots of its line in 93 to 101 turns), then `gyre` and `cove`; every `circle` game is a draw.

**Findings** (league games on the training maps, each read by its own subagent with `digest` and `--turns` and both bots' logs, the decisive evidence checked again here):

1. **Feeding empties a border castle beside an enemy castle being stocked.** `firth`, team 1 against `exact_stallfeed` (`1887f942…`), turns 59 to 67: castle 7, 4.7 from enemy castle 10, fed its stock 6.8 units back to castle 9, the team's single front (`feed>9 7:12` on turn 59, `feed>9 5:12 7:16` on turn 63, left with 4); castle 10 showed 11 on turn 63 with a feed of 12 landing on it (26 on turn 64); turn 64 `strike>7 exact 22 10:22`; castle 7 fell on turn 67 holding 16, and production went from 17 against 19 to 13 against 23. The same turns and logs against `sameturn_endreserve` (`7bb22e15…`). `gyre` against `harrier_attackers` (`df55ad1b…`), turn 57: castle 3 fed 13 (`feed>5 3:13 7:12`), left with 4, beside enemy castle 4 (14 on the board, three of its own feeds landing, 28 the next turn), struck with 22 on turn 58, lost on turn 67. `cove` against `endreserve_stallfeed` (`cc3c219b…`), turn 63: castle 11 (20, 2.2 from enemy castle 9) sent a harassment group of 13 while castle 9 held 18 with five feeds walking in; castle 9 held 50 on turn 65, struck it with 25 and took it on turn 67. Real game 473, turns 83 to 87, the same. **Cause:** `reserve()` and `holds()` count only an enemy castle's soldiers on the board, never its own groups landing on it; and `feed()` sends every castle's stock to one front, even a castle that is itself a border castle. **Ideas:** (a) feeding, stalled feeding and harassing count the enemy castle's inbound groups; (f) a castle feeds only a front nearer than itself to the enemy. Iteration 26's `ori_hold_staged` counted the enemy's batches in every safety check and lost; (a) counts them only in the voluntary sends that empty a castle.
2. **Exact short strikes bounce off a help of 3, then trickle.** `gyre` (`df55ad1b…`), turns 59 to 72: `strike>9 exact 29 5:29`, then 17, 4 and 7, each answered by `help>9 2:3` from an enemy castle two turns from the target; castle 5 drained from 48 to 20 and fell on turn 72. `cove` (`cc3c219b…`), turn 63: `strike>10 exact 18 8:18`, answered by `help>10 (same turn) 0:3`, then 5 and 6 more; turns 66 to 72 at castle 4: 30, 11, 5, 12, 9, against helps of 1 to 3, never taken. `firth`: castle 2 changed hands 16 times, our captures leaving 2. Real games 472 and 473: 8 of 10 captures landed with exactly 2. **Cause:** for a short exact strike `attack_price()` drops the term for the target's neighbours, so the price is target plus 2. **Idea (b):** the short exact strike pays half of what the neighbours whose group lands no later than ours could send, as the long strikes do.
3. **Defence never buys speed to arrive in time, and the would-be helpers spend the same soldiers.** `claw`, team 1 against `ori_mimic` (`5fc0b23b…`), turns 64 to 69: 70 soldiers from castle 4 at our home castle 0 (43; 10 short when they land); castles 3 (57) and 5 (33) were 2.8 away at speed 1, 6 turns, one more than the strike's 5. On turn 65 castle 3 bought speed 2 anyway, for `speed+strike>2 3:13` and `harass> 4:3:17`, and castle 5 bought production 4; castle 0 fell on turn 69 with 58. Turns 70 to 75 the same at castle 3. Real game 471, turns 39 to 42, the same. No log line said a castle was about to fall. **Cause:** `defend()` takes only helpers in time at their current speed and skips the castle silently when they fall short. **Idea (c):** a helper that can pay its next speed level and still give the help buys it and helps; log `cannot hold>` when nothing can.
4. **The harassment groups die against the feed batches.** `cove` turn 63 (above, the group traded 13 for 13 in a clash with a feed); `claw` against `ori_like` (`a413f988…`, team 2), turns 49 to 76: seven groups (81 soldiers), two wiped by feed groups, nothing frozen; `firth` turns 74 and 79: `harass> 7:3:17` twice at a castle fed every turn, one cut to 5 by a feed, the other into a castle that reached 86; real games 472 and 473, the same. **Idea (d):** no harassment at an enemy castle its own side's groups are bound for.
5. **`claw`'s opening, in the league too.** Against `ori_mimic` the two bots play move for move to turn 17 (`take>4 5:4 0:17`, as in all three real games); castle 3 was saving; castle 4 went to `ori_mimic` on turn 25 (after a hold group of exactly 10 that landed alone and left it neutral at 0) and stayed its front all game. **Cause:** `expand()` keeps castles a few turns from their next upgrade out of a neutral's payers. **Idea (e):** a contested neutral (one an enemy castle reaches no later than our nearest castle) may be paid by castles saving for an upgrade. Iteration 29's `endreserve_helpall` let them pay for every neutral and lost; this is the contested ones only.

Seen and not made a candidate: on `circle` (`a69e5f3b…`, a draw like all 28) both bots buy production 4 on turn 12 at 32 soldiers, left with 2; the upgrade check (`holds()`) uses the enemy's current speed and `need()`, so it misses the strike an enemy that buys speed 2 in the same turn could make (22 against 18): the real opponent's 17-turn `circle` win. Iteration 32's `growtrickle_buyspeed` counted bought speed in the reserves and lost. On `archipelago` (`ad646f12…`, a 300-turn win 9 to 3) the lead stood on two thin middle castles that nothing fed (56 and 75 soldiers with rear castles at 631 to 831), and on turn 294 an exact strike of 1,131 left that couldn't land before the last generation (`attack()` doesn't check `in_time`); the reserve, each castle's own against the largest enemy castle, froze 49 turns of a lead. `gyre`'s mirror losses are a seat effect: team 1 wins all four `harrier` mirror games there in 87 turns.

| Candidate | Parent | Idea | Rematch (first different turn; before → after) | Against parent | Decision so far |
|---|---|---|---|---|---|
| `feedkeep_speedhelp` | harrier_feedkeep | (c) When no helper lands before a castle falls, a helper that can pay its next speed level and still give the help buys it and helps; `cannot hold>C` when nothing can. | `claw`/`ori_mimic`: turn 47, `help>2 speed@5 (same turn) 5:3` where the parent bought production 3 (castle 2 fell anyway on turn 52, `cannot hold>2` turns 48 to 52); lost 0 → 0 (78 turns, not 80). `cove`/`endreserve_stallfeed`: turn 48, `help>9 speed@11 (same turn) 11:3`; 0 → 1 (win at the limit). `claw`/`ori_like`: never acted. The finding's own turns 64 to 65 didn't come: the game had changed from turn 47. | **22/38** (11 W 22 D 5 L; lost `strait` both sides, one `claw`, `crossing`, `firth`; won `archipelago`, `delta`, `gyre`, `haven` 2/2) | to the gate; **promoted** (below) |
| `feedkeep_exactnear` | harrier_feedkeep | (b) A short exact strike on an enemy castle also pays half of what the target's neighbours could send that lands no later than our group. | `gyre`: turn 43, a take elsewhere instead of `strike>4 exact 30`; 0 → 0. `cove`: turn 51, harass instead of `strike>9 exact 9`; 0 → 1. `firth`: turn 42, production 4 instead of speed and a strike; 0 → 1. `claw`/`ori_mimic`: turn 33, `saving` instead of `speed+strike>2 0:6`; 0 → 0.5. | 18/38 | **rejected**: no more than half against its parent; ratings not played. |
| `feedkeep_contested` | harrier_feedkeep | (e) A contested neutral may be paid by castles saving for their next upgrade. | `claw`: turn 15 or 16, `take>4 contested 0:13 3:7` where the parent waited; `ori_mimic` 0 → 1, `harrier_front` 0 → 1, `safe_hold` 0 → 0 (86 turns, not 102). | 18/38 (2/2 on `claw` and `archipelago`, 0/2 on `crossing`, `far-shores`, `firth`) | **rejected**: no more than half; not played. |
| `feedkeep_ownfront` | harrier_feedkeep | (f) A castle feeds only a front nearer than itself to the enemy. As measured: only a front nearer than it to **every** enemy castle (the nearest-enemy form didn't act on `firth`'s turn 63, where castle 7's nearest enemy castle is the centre, not castle 10). | `firth`/`exact_stallfeed`: turn 59, `ownfront 7` kept 12; lost in 121, not 93. `firth`/`sameturn_endreserve`: turn 59; 0 → 1. `claw`/`ori_like`: turn 64; lost in 121, not 89. | 17/38 | **rejected**: no more than half; not played. |
| `feedkeep_inbound` | harrier_feedkeep | (a) Feeding, stalled feeding and harassing keep a reserve that counts each enemy castle's own groups landing on it before its group could reach ours. | `firth` both: turn 63, `inbound kept 7:16`; 0 → 1 each. `cove`: turn 55, `inbound kept 11:11`; 0 → 1. `gyre`: turn 40; 0 → 0. | 15/38 (13 losses, all at the limit on castles: it keeps soldiers back and ends with fewer castles) | **rejected**: no more than half; not played. |
| `feedkeep_harassfed` | harrier_feedkeep | (d) No harassment group at an enemy castle its own side's groups are bound for. | `cove`: turn 57, `harass> skip 9 fed`; 0 → 0 (at the limit, not in 105). `claw`/`ori_like`: turn 49, the 12 fed instead; 0 → 1. `firth`: turn 74; 0 → 0. | 14/38 (0/2 on six maps: `archipelago`, `crossing`, `delta`, `haven`, `islands`, `loch`) | **rejected**: no more than half; not played. |

The head-to-heads: `uv run league tournament --focus <the six> --parents --strict --run-id iteration-37-parents`, 228 matches, exit 0, no failed turn, slowest turns 10.9 to 24.7 ms. The five rejected candidates' directories are deleted. `feedkeep_speedhelp` then failed `ruff format --check` on one long line; it was formatted and its head-to-head played again (38 matches, exit 0): **22/38**, no failed turn, slowest turn 10.8 ms. `scripts/check.sh` passes with it (365 tests).

Read as a group: five of the six real-game fixes lost the mirror match. Each acted where its finding was (most of the rematches turned a loss into a win or a draw), and each lost games elsewhere, mostly at the limit on castles. Against the parent the real opponent's habits don't show: `ori_mimic`, the stand-in, makes `claw`'s opening move for move as the parent does.

**Not done or not verified here:** the real games can't be rematched (`rematch` takes league games only), so no candidate was checked against them. `feedkeep_speedhelp` never acted on `ori_like`'s `claw` game, and its first action against `ori_mimic` didn't save the castle. Nothing in this half compares a candidate's ratings, and no holdout game was opened.

**Time so far** (from 08:39:56): step 0, 20 seconds (skills, ledger, `check.sh` in 4 s); step 1, 43 seconds (5,700 matches, all cached; the runner was built from source first); step 2, 6 minutes (the `--focus` run 1 s; ten games read in parallel by ten subagents, the longest 3.7 minutes, real game 473; checking the evidence 1 minute); step 3, 4 minutes (six candidates written in parallel, each with its rematches and its own head-to-head, the longest 2.3 minutes); step 4's head-to-head, 40 seconds (all 228 matches cached, then 38 played again after formatting). 12.5 minutes to the hand-over, against iteration 36's 39 minutes for the whole iteration. The slowest step was the study, now as long as its longest game. **Speed-up:** each candidate subagent should run `ruff format` on its candidate before its head-to-head, so a formatting change doesn't replay it (38 matches here).

**Second half** (on another runner, from the hand-over, every match from the cache that the gate's eight runners played):

**The gate.** `scripts/check.sh` passes (365 tests). `uv run league tournament --focus feedkeep_speedhelp --parents --strict` (38 matches, all cached, exit 0) gives 22/38 again; `uv run league tournament --focus feedkeep_speedhelp --strict --run-id iteration-37-candidates` (684 matches, all cached, exit 0): no failed turn, slowest turn 17.0 ms. It plays.

**Selection.** `iteration-37-select` (6,384 matches, all cached, exit 0): `feedkeep_speedhelp` 2061 against its parent's 2060, 22/38 head to head: both training rules hold, the second by one point. `iteration-37-select-holdout` (5,040 matches, all cached, exit 0): 2121 against 2099, 17/30 against the parent: **promoted**.

| Candidate | Parent | Idea | Training rating (parent's) | Against parent | Holdout (parent's) | Decision |
|---|---|---|---|---|---|---|
| `feedkeep_speedhelp` | harrier_feedkeep | (c) A helper that can pay its next speed level and still give the help buys it and helps when no helper would land in time; `cannot hold>C` when nothing can. | 2061 (2060) | 22/38 | 2121 (2099), 17/30 | **promoted** |

The other five were rejected at the head-to-head (the first half's table above): no more than half against their parent, ratings not played.

**What the promotion is made of.** The totals hide large moves map by map, in both directions. Training, its points against the field's 18 others (out of 36) against the parent's: `strait` 16 against 31, `gyre` 22 against 28.5, `claw` 21 against 24; `delta` 32 against 27, `firth` 31 against 25, `archipelago` 32 against 28, `islands` 33 against 29. Holdout: `ridge` 14 against 26, `tor` 24 against 28; `scatter` 36 against 25, `spit` 31 against 19, `mere` 31 against 25. A defence rule that acts on a few turns a game changes which games are won rather than how many: the training selection was decided by one rating point, and the holdout by 22. On `claw`, the map of all three real games, the new champion scores 3 points less than its parent in the league.

**Status changes:** `feedkeep_speedhelp` is active and the champion (first on both sets of maps); `hosting/lambda/bot` now names it. `harrier_feedkeep` stays active: the new champion scores less than it against `harrier_attackers` (23.5/38 to 25), `growtrickle_feedkeep`, `endreserve_stallfeed`, `sameturn_stallfeed`, `exact_sameturn`, `safe_hold` and `ori_like`. That makes **eight active bots**, but none is retired: in the training selection's pair table no active bot's row is matched or beaten everywhere by another's (the nearest: `harrier_front` misses `stallfeed_growtrickle`'s row only against `ori_like`, 36 to 37). On holdout `growtrickle_feedkeep` matches or beats `stallfeed_growtrickle` and `endreserve_stallfeed` everywhere, but the rule has been read on the training table, as in iteration 35, where seven stayed active the same way. Six retired, none deleted. The five rejected candidates' directories were deleted in the first half.

Training maps (`iteration-37-train`, 6,384 matches, all cached, exit 0):

| Player | Rating | Score | W | D | L |
| --- | --- | --- | --- | --- | --- |
| feedkeep_speedhelp | 2061 | 0.762 | 452 | 139 | 93 |
| harrier_feedkeep | 2060 | 0.761 | 448 | 145 | 91 |
| harrier_front | 2026 | 0.727 | 407 | 180 | 97 |
| harrier_attackers | 2026 | 0.727 | 410 | 174 | 100 |
| growtrickle_feedkeep | 1972 | 0.667 | 366 | 181 | 137 |
| stallfeed_growtrickle | 1955 | 0.648 | 359 | 168 | 157 |
| sameturn_endreserve | 1951 | 0.643 | 351 | 178 | 155 |
| endreserve_stallfeed | 1944 | 0.636 | 344 | 182 | 158 |
| sameturn_stallfeed (retired) | 1872 | 0.552 | 256 | 243 | 185 |
| exact_sameturn (retired) | 1863 | 0.542 | 255 | 231 | 198 |
| exact_stallfeed (retired) | 1819 | 0.490 | 218 | 235 | 231 |
| ori_hold (retired) | 1817 | 0.488 | 209 | 250 | 225 |
| ori_hold_exact (retired) | 1807 | 0.477 | 214 | 224 | 246 |
| ori_mimic (sparring) | 1800 | 0.469 | 199 | 244 | 241 |
| safe_hold (retired) | 1720 | 0.385 | 248 | 30 | 406 |
| ori_like (sparring) | 1550 | 0.243 | 151 | 30 | 503 |
| level1 | 1526 | 0.132 | 0 | 160 | 448 |
| level2 | 595 | 0.000 | 0 | 0 | 608 |
| level3 | 595 | 0.000 | 0 | 0 | 608 |

Holdout maps (`iteration-37-holdout`, 5,040 matches, all cached, exit 0):

| Player | Rating | Score | W | D | L |
| --- | --- | --- | --- | --- | --- |
| feedkeep_speedhelp | 2121 | 0.787 | 367 | 116 | 57 |
| harrier_feedkeep | 2099 | 0.767 | 342 | 144 | 54 |
| growtrickle_feedkeep | 2092 | 0.760 | 336 | 149 | 55 |
| harrier_attackers | 2045 | 0.712 | 313 | 143 | 84 |
| harrier_front | 2037 | 0.705 | 309 | 143 | 88 |
| stallfeed_growtrickle | 1999 | 0.664 | 281 | 155 | 104 |
| endreserve_stallfeed | 1988 | 0.651 | 266 | 171 | 103 |
| sameturn_endreserve | 1968 | 0.629 | 254 | 171 | 115 |
| sameturn_stallfeed (retired) | 1915 | 0.570 | 210 | 196 | 134 |
| exact_sameturn (retired) | 1910 | 0.565 | 207 | 196 | 137 |
| exact_stallfeed (retired) | 1840 | 0.487 | 169 | 188 | 183 |
| ori_hold_exact (retired) | 1823 | 0.469 | 159 | 188 | 193 |
| ori_hold (retired) | 1812 | 0.457 | 158 | 178 | 204 |
| ori_mimic (sparring) | 1800 | 0.444 | 153 | 174 | 213 |
| safe_hold (retired) | 1642 | 0.298 | 161 | 0 | 379 |
| ori_like (sparring) | 1571 | 0.246 | 133 | 0 | 407 |
| level1 | 1542 | 0.133 | 0 | 128 | 352 |
| level3 | 925 | 0.004 | 2 | 0 | 478 |
| level2 | 644 | 0.000 | 0 | 0 | 480 |

**Champion:** `feedkeep_speedhelp`, **2061** on training (iteration 36's champion `harrier_feedkeep`: 2064, now 2060 with one more player in the table) and **2121** on holdout (iteration 36: 2102).

**Where it still loses:** `strait` (16/36, where its parent took 31: the first thing for the next iteration to read: why it lost the map its parent won is not read here), `reef` 18, `claw` and `circle` 21, `gyre` 22; on `claw` the real games' opening race (the middle castle paid from home on turn 17), the captures sized to take and not to hold, and the border castle emptied by feeding all stand: five candidates for them lost the mirror match. The next iteration should read why `strait` and `claw` got worse first, and since `ori_mimic` plays `claw`'s opening move for move as our line does, a fix for the real games' opening can't be measured against it.

### The league itself

- **One family, raised again.** Every active bot and five of the six retired ones descend from `ori_mimic` through `ori_hold`; the only other strategies left are `safe_hold` (retired, the old `hold_` line) and `ori_like` (sparring). Eight active bots, all of the `ori_hold` → `exact_sameturn` → `sameturn_endreserve` line. A champion's rating is earned mostly against its relatives: 7 of its 18 opponents are its line's active bots. Iteration 36 said the same of its frozen mirror games, so it has stood for at least two iterations. *What an iteration can do:* a founder written from the rules and the Lessons, not from this line's code. *What only a person can do:* an outside opponent or a sparring bot of another strategy.
- **The population rule no longer keeps six active.** Eight are active because no row is matched everywhere; as the line's bots grow alike, a half point against `ori_like` or `level1` keeps a bot. *For a person:* a tolerance in the rule (matched within a point or two), or a cap that retires the lowest-rated anyway.
- **Who teaches nothing.** `level2` and `level3` win no game on training and `level1` none (only draws); three of 19 players add nothing but the anchor's spread. `ori_like` wins 151 of 684 games.
- **What the numbers can separate.** The head-to-head was 22/38 with 22 draws, and the training ratings differ by one point: the selection's training half was decided by a margin a few games make. The map rows move by up to 15 points either way. *For a person:* more training maps, or more than two games per pair and map, would make a one-point decision mean more.
- **What the league can't show.** The three real losses were all on `claw` against a bot that `ori_mimic` stands in for, and the stand-in plays `claw`'s opening like our line: the real opponent's early middle-castle race and its fed batches don't happen in the league. Five fixes for them lost the mirror match. *For a person:* a sparring bot rebuilt from these three games (production at home first, middle castles taken from the near castles by turn 17, batches of 12 from two castles every three turns), as a new sparring bot, `ori_mimic` staying as the anchor.

**Time:** the first half, 12.5 minutes from 08:39:56 to the hand-over (its own account above); with the claim (08:37:32 to 08:37:59), the population's warm-up on eight runners (08:38:01 to 08:39:10, about 1 minute) and the study job (08:39:12 to 08:53:48), 16.3 minutes. The gate's eight runners played every match with the candidate on both sets of maps in 08:53:50 to 08:56:00 (2.2 minutes). The second half, from 08:56:03: the gate (`check.sh` 3 s, both runs 33 s, all cached) at 08:57:53, the selection and holdout selection at 08:58:07 (seconds), the final tables at 08:58:45 (4 s), then the ledger, the studies and the report until about 09:02 (4 minutes). Total from the claim: about 25 minutes, from 08:37:32 to 09:02 (iteration 36: 39 minutes to the final tables). Slowest steps: the study (14.6 minutes of job time, as long as its longest game, real game 473) and the writing of the record in the second half; the playing, split eight ways, is now about 3 minutes in all. **Speed-up:** the runner's setup in each job (`uv` and the Go runner built from source, about 30 seconds a job here) is now a visible share; caching the built runner between jobs would save it. As the first half proposed: candidate subagents should run `ruff format` before their head-to-head.

## Setup after iteration 37: the bots are Go

**Date:** 2026-11-23. A change of the league's setup, made between iterations and measured with full tournaments on both sets of maps. Every bot plays exactly as before. (Measured from iteration 36's population, then again with iteration 37's champion.)

**Why.** Python turns were 93% of a match's time, and over half of a Python turn was the Python SDK's worker around `play`, not the bot. The game's Go SDK has the same worker protocol, which the runner speaks to both.

**What changed:**

- **Every bot is a Go program**, `bots/<name>/main.go` on the game's Go SDK (`go.mod` pins `clients/island-battles-go` v1.5.0, the release of the Python SDK 1.5.0 the bots used). Each is a port of its Python code line for line: the same rules, constants, order of decisions and log lines. To round as Python did, the ports keep plain `int`s, floor division where `//` met a negative number, and `hypot`, a copy of CPython's `math.hypot` (Go's `math.Hypot` differed in the last bit on 35% of a million test distances, and a walk's turns are rounded from them).
- **A tournament builds each bot once** (`runs/bin/<name>-<hash>`) and plays it as `<binary> worker`. A match's key covers the bot's Go files and the SDK's version, so every match was played again once.
- **The bots' checks are Go tests** (`tests/bots/`): the same six boards and 300 seeded boards through each bot's worker, the same turn answered twice, small memory, a log line every turn, and a static check that a bot imports only the SDK and pure standard packages and keeps no package-level variable, `init` or goroutine. `scripts/check.sh` adds `gofmt`, `go vet` and `go test ./...`.
- **`league replay`** plays a bot's turns through its worker. **The hosted bot** keeps its Lambda function, runtime and permissions: the zip carries the champion built for linux/arm64 and the handler plays each turn through its worker. The automated iteration may run `gofmt` instead of `ruff format`.

**Measured.**

- **Each port gives its Python bot's answers.** Each bot's Go and Python workers were given the same 15,727 turns (the fixture's boards, 3,000 seeded boards and every frame of 40 league games, both teams): every answer was the same, commands, memory and log lines byte for byte.
- **The tournaments are the same games.** With every bot in Go, the 5,700 training and 4,500 holdout matches gave the Python bots' results, and every demo was identical, every frame and every log line. The W/D/L columns and the ratings of both tables are iteration 36's, row for row: `harrier_feedkeep` 2064 on training and 2102 on holdout. The final run with the committed code (`final2-train`, `final2-holdout`, exit 0 with `--strict`) is the same again. **Iteration 37's champion, `feedkeep_speedhelp`,** merged while this was under review and was ported the same way: its Go and Python workers gave the same answers to 18,198 turns, its 1,224 matches against the whole field on all 34 maps gave the same results and identical demos as Python and Go, and the all-Go tournaments with it (`go37-train`, 6,384 matches, and `go37-holdout`, 5,040, exit 0 with `--strict`) equal iteration 37's two tables row for row: `feedkeep_speedhelp` 2061 on training and 2121 on holdout. Its first try had one failed turn in each of three of the 10,200 matches, "didn't answer within 2s" from bots whose slowest turn in those games is 2.4 ms: the machine stalled. Played again, as the tournament does with a failed turn, they were clean and equal to Python's.
- **Speed**, on a 12-thread desktop (6 cores), otherwise idle (load 3 before):
  - **A whole training tournament from an empty cache**, 5,700 matches at 12 at once, straight through the runner: **724 s with the Python bots, 256 s with the Go bots, 2.8 times faster** (7.9 against 22.2 matches a second). The same 5,700 results both times.
  - **A league bot's turn as the runner measures it** in that tournament: 4.07 ms against 1.32 ms, 3.1 times. The champion's slowest turn went from 116 to 27 ms.
  - **The champion's worker alone**, 11,806 turns of real games without the runner: 2.35 ms a turn in Python, 0.46 ms in Go, 5.1 times. The rest of a Go turn in a tournament, about 0.9 ms, is the runner's: encoding the turn, the pipe and the scheduling, in the game's repository.
  - **An iteration's tournaments** are mostly its candidates' matches against the field, about 1,150 a candidate on both sets of maps, which cost what the whole tournament's matches cost: about 2.8 times less, some 50 seconds a candidate here instead of two and a half minutes.

**For the next iterations.** A candidate is Go: `league new` copies `main.go`, and `gofmt -w bots/<candidate>` before the checks. The rules skills are still the Python template's; the `bot-league` skill maps them to Go. Never let a Go map's order choose anything: Go walks a map in a new order every time (the tests answer each board twice to catch it).

## Iteration 38: help that buys speed too early, and strikes that land too late

**Date:** 2026-11-23. **Maps:** 19 training, 15 holdout (unchanged). **Matches:** 6,384 in the baseline (`iteration-38-before`, all from the cache that the runners played, equal to iteration 37's training table row for row). Split across runners: the population's round robin was played on every map by other runners; this first half ran steps 0 to 3 and step 4's head-to-head. The number was claimed by the automated iteration's workflow. Started by the hosted bot's real game 474; six candidates, written in parallel by subagents (Sonnet).

**Real game studied** (the second half doesn't have it, so what it showed is here):

- **474** (`claw`, 108 turns, lost by elimination to another player's hosted bot; our bot was `feedkeep_speedhelp`, team 1). The same opening as 471 to 473: production 2 and 3 at home on turns 1 and 2, castle 4 paid from home on turn 17 (`take>4 5:4 0:18`, 5.8 away, 11 turns at speed 1) while castle 3 bought production 2 on turn 18; castle 4 was taken on turn 28 with 12, logged `cannot hold>4` on turns 29 to 34 (home still bought speed 2 on turn 30), and fell on turn 35. Castle 2 was paid in pieces (`take>2` on turns 23, 25 and 27, leaving castles 3 and 5 with 1 to 3) and then changed hands eight times from turn 30 to 38, each capture leaving 2 to 4, against batches of 7 already walking to it; castles 4 (turn 55) and 7 (turn 73) were taken with 2 the same way and retaken in 2 to 5 turns. **The end decided it:** turns 80 to 95 `saving` every turn on three castles (84, 81, 84 at turn 94) while the opponent fed castle 4 to 194 with batches of 12; on turn 95 it struck castle 3 with 98 and kept 80, castle 3 fell at turn 98 holding 93, castle 5 at turn 105 holding 128, home at 108. `feed()` never moved the rear castles' soldiers to castle 3, because it feeds only a castle whose reserve is 0, and against a stack of 100 or more it never is; `stallFeed()` covers only castles with an upgrade left, and all three were fully upgraded. The speed-help rule of iteration 37 never acted (31 `cannot hold>` lines, no `speed@`): early no castle could pay the level, and on turn 96 castle 0's reserve against a castle of 106 left it 18 to give where 21 were needed. Seven harassment groups froze nothing; one of 10 died against the 58 that struck. The hosted turn times: turn 1 took 260 ms and turn 6 took 289 ms (every other turn 25 ms or less), over the gate's 200: probably the Lambda's cold start, not the bot (its league turns are under 16 ms).

Checked against iteration 37's findings from 471 to 473: the middle-castle race lost to a long walk from home recurs; captures sized to take and retaken recur, at their worst; the border castle emptied by feeding recurs (turns 47 and 52, castle 3 left with 3 beside castle 4) but wasn't punished; soldiers frozen in separate castles and taken one by one recurs and decided the game; harassment froze nothing again.

**Measured:** champion `feedkeep_speedhelp`, **2061** on training (iteration 37: 2061), 0.762, 452 W 139 D 93 L. Its pair row: 21/38 against `sameturn_endreserve`, 22 against `harrier_feedkeep` and `growtrickle_feedkeep`, 23.5 against `harrier_attackers`, 24 against `endreserve_stallfeed`, 24.5 against `harrier_front`, 25 against `stallfeed_growtrickle`, 27 to 38 against the rest. Its map row is worst on `strait` 16/36 (its parent: 31), `reef` 18, `circle` and `claw` 21, `gyre` 22, `rill` 23. Shortest losses: `claw` to `ori_mimic` in 78 turns, `gyre` to `safe_hold` in 79 (both seats), `claw` to `ori_like` in 89, then `claw` to most of its line in 94 to 102; on `strait` it loses by elimination to every bot of its line, both seats, in 165 to 177 turns.

**Findings** (league games on the training maps, each read by its own subagent with `digest` and `--turns` and both bots' logs, all at once with the real game; the decisive evidence of findings 1 and 2 checked again here):

1. **Speed-help buys speed when waiting a turn would do, and pays more than it sends.** `strait`, team 1 against `harrier_feedkeep` (`5ab23239…`) and against `stallfeed_growtrickle` (`943fe9b8…`): both games are move for move the parent's winning games until turn 54, where `help>2 speed@6 (same turn) 6:1 0:4` bought speed 2 on castle 6 (11 soldiers) to send 1, which died in a clash on turn 56; the parent logged `saving` and on turn 55 `help>2 (same turn) 0:3`, and castle 2 held. The opponent then led in production for the rest of the game. **Cause:** `defend()`'s fast helpers are taken whenever their sped-up walk is in time, with no check that it is the last turn they could help, nor that they give as much as the speed costs. **Idea (a):** buy speed for help only on the last chance, and only when the help is at least the cost.
2. **Strikes sent at the end that can't land before it.** `reef`, team 1 against `ori_mimic` (`4d9994b2…`, drawn, frozen from turn 42 with 3 castles each, `saving` to turn 289): turn 290 `strike>1 exact 2140 4:992 0:996 2:152 late reserve freed …`, walks of about 15 turns with 10 left; 2,140 soldiers still walking at turn 300. `archipelago` against `endreserve_stallfeed` (`95c643c9…`, won at the limit): turn 294 `strike>3 exact 1131 4:663 2:467 6:1`, 7 turns with 6 left, while castle 4 bought production 4 the same turn. **Cause:** `attack()` never checks that a sender lands before the last generation, while `reserve()` frees soldiers exactly when the enemy's walk, as long as ours, can't. **Idea (b):** drop such senders, unless speed levels they can pay make them land in time.
3. **Fully upgraded castles above their reserve never feed.** `archipelago` (`95c643c9…`), turns 243 to 291: 49 turns of `saving`; on turn 288 castle 0 held 903 against a reserve of about 706, while the middle castles 8 and 9 grew alone to 119 and 100; castle 9 fell on turn 294 to a strike of 108. Real game 474, turns 80 to 98, the same. **Cause:** `feed()` skips any castle with a reserve above 0; `stallFeed()` only castles with an upgrade left. **Idea (c):** a fully upgraded castle feeds the front what it holds above its reserve, once that is `feedAt` or more.
4. **Feeding a castle defence has given up.** `claw`, team 2 against `ori_like` (`db55c1e5…`, lost in 89): castle 5, taken on turn 61 with 2 beside the enemy's home, became the castle nearest the enemy; turns 64 and 65 `cannot hold>5 cannot hold>6 feed>5 4:17`, then `feed>5 1:12`; castles 5 and 6 fell on turn 66 with 29 fed soldiers still walking, and castle 4, left with 4, fell on turn 75. `gyre` against `safe_hold` (`f4f5d94e…`), turn 46: `cannot hold>9 … feed>9 0:12`. **Cause:** `front()` takes the castle nearest an enemy with no regard to `defend()`. **Idea (e):** a castle defence couldn't hold this turn is never the front.
5. **`claw`'s middle castle held to exactly 0.** `claw`, team 1 against `ori_mimic` (`68055cdd…`, lost in 78): turn 18 `hold>4:3:10` sent 10 at a neutral of 10, which the simulation counted as ours at 0 after the 21-against-21 groups cancel; on turn 25 our 10 left it neutral at 0 and `ori_mimic`'s single soldier landing that turn took it (`capture: castle 4 neutral (0 soldiers) -> ori_mimic (1 soldiers)`); it was `ori_mimic`'s front all game. The real games' lost middle race, in the league. **Cause:** `hold()`'s `holdsWith` accepts ownership at 0 soldiers. **Idea (f):** a held neutral must end with at least 1.
6. **Defence aims at a dip that our own same-turn landing repairs.** Same game, turns 46 to 52: `help>2 speed@5 (same turn) 5:3` sent 3 while castle 5 kept 9, then `cannot hold>2` on turns 48 to 52 with castle 5 four turns away at speed 2; castle 2 fell on turn 52. An enemy group of 6 lands at t3 before ours of 19 and 3 the same turn (id order), so `fall` was 3 and castle 5 (walk 4) was skipped, although the real deficit came at t5. **Cause:** `defend()` takes `fall` and `lowest` per landing, not per turn. **Idea (h):** the balance counts after each turn's last landing.

Seen and not made a candidate: `gyre` against `safe_hold` (`f4f5d94e…`, turn 55 `production4@4` left castle 4 with 4 beside enemy castle 5 at 16 with 24 landing on it; struck on turn 56, lost on 59, and the home through it on 66) and `claw` against `ori_mimic` (turn 71 `feed>3 0:13` emptied home beside castle 4 at 18 with three batches of 12 landing; home fell on 75): the safety checks count an enemy castle's soldiers, not its own groups landing on it. That is iteration 37's `feedkeep_inbound` (15/38) and iteration 26's `ori_hold_staged` (14/34), both rejected; it was the most frequent cause in this iteration's games (four of six) and the real ones, but no third form was tried. Exact short strikes that ignore the target's neighbours (`claw` against `ori_like`, castle 5 taken with 2 on turn 61) are iteration 37's `feedkeep_exactnear` (18/38). Harassment groups of 9 to 19 at castles of hundreds (`archipelago`, every 6 turns from turn 243) and into staging groups (`gyre`, four times from turn 68): iteration 37's `feedkeep_harassfed` (14/38) was another form; not retried.

| Candidate | Parent | Idea | Rematch (first different turn; before → after) | Against parent | Decision so far |
|---|---|---|---|---|---|
| `speedhelp_landlate` | feedkeep_speedhelp | (b) A strike's senders must land before the last generation: a sender that can't is dropped, unless speed levels it can pay (and still send a soldier) make it land in time; it buys them (`intime:speed@C`). | `reef`/`ori_mimic`: turn 290, `strike>1 exact 2084 4:942 2:1068 0:74 intime:speed@0 intime:speed@2 intime:speed@4 …` with speed 3 and 4 bought; draw → win. `archipelago`: turn 294, `strike>5 exact 703 0:702 6:1 intime:speed@0`, the late sends from 4 and 2 dropped; win → win. | **21.5/38** (12 W 19 D 7 L; won `delta`, `reef`, `sound` 2/2; lost `gyre` 0/2, one each of `claw`, `haven`, `archipelago`, `crossing`, `firth`) | to the gate |
| `speedhelp_fullfeed` | feedkeep_speedhelp | (c) A castle with every upgrade bought feeds the front what it holds above its reserve once that is `feedAt` or more (`C:N+` in `feed>`). | `archipelago`: turn 58 (not 243), `feed>6 0:21+` beside the parent's `take>9 6:33 2:16 stalled>6 4:18 10:15`; win → draw at the limit. | **21/38** (10 W 22 D 6 L; won `islands` and `haven` 2/2; lost `cove` 0/2, one each of `claw`, `firth`, `gyre`, `crossing`) | to the gate |
| `speedhelp_livefront` | feedkeep_speedhelp | (e) A castle defence couldn't hold this turn is never the front: feeding and stalled feeding go to the next castle by the same order (`feed>4 (not 5)`), or nowhere. | `claw`/`ori_like`: turn 64, nothing fed where the parent sent `feed>5 4:17`; loss in 89 → win in 89. `gyre`/`safe_hold`: turn 46, `feed>2 (not 9) 0:12`; loss in 79 → loss in 76. | **20/38** (6 W 28 D 4 L; won `crossing` and `haven` 2/2; lost `firth` 0/2, one each of `claw`, `archipelago`) | to the gate |
| `speedhelp_lastchance` | feedkeep_speedhelp | (a) A helper buys speed only on its last chance (its sped-up walk equals the fall, its walk at its own speed is longer) and only when it gives at least the speed's cost. | `strait`/`harrier_feedkeep`: turn 54, `cannot hold>2` and no speed, where the parent of this line logged `help>2 speed@6 (same turn) 6:1 0:4`; loss in 165 → draw. `strait`/`stallfeed_growtrickle`: turn 54, the same; loss in 174 → win. | 19/38 (6 W 26 D 6 L; won `strait` and `crossing` 2/2, lost `gyre` and `haven` 0/2) | **rejected**: no more than half against its parent; ratings not played. |
| `speedhelp_holdspare` | feedkeep_speedhelp | (f) A held neutral must end with at least 1 soldier (`holdSpare`), not ours at 0. | `claw`/`ori_mimic`: turn 18, `production2@3` where the parent sent `hold>4:3:10` (no sender could pay a hold with a soldier left); loss in 78 → draw. | 19/38 (4 W 30 D 4 L; every map 1/2) | **rejected**: no more than half; not played. |
| `speedhelp_lowfall` | feedkeep_speedhelp | (h) Defence's fall and shortfall count after each turn's last landing. | `claw`/`ori_mimic`: turn 47, `production3@5` where the parent bought speed to help with 3; loss in 78 → loss in 87. | 17/38 (6 W 22 D 10 L; lost `archipelago`, `cove`, `crossing` 0/2) | **rejected**: no more than half; not played. |

The head-to-heads: `uv run league tournament --focus <the six> --parents --strict --run-id iteration-38-parents`, 228 matches, all cached from the subagents' own runs, exit 0, no failed turn, slowest turns 7.5 to 13.0 ms (the parent 15.0). The three rejected candidates' directories are deleted. `scripts/check.sh` passes with the three left (97 tool tests, the bots' Go tests ok). The diffs were read here: each changes only the function its idea names, and logs it.

Read as a group: the three that passed are about the turns the parent wastes (late strikes, spare soldiers that never move, feeds into a lost castle); the three that failed change defence and holding, as most defence refinements of this line have since iteration 30 (the Lessons: they split the mirror match). `speedhelp_lastchance` took back `strait` from the parent's own speed-help, as finding 1 said, and lost as much on `gyre` and `haven`: iteration 37's speed-help seems to win those maps for the reason it loses `strait`.

**Not done or not verified here:** the real game can't be rematched (`rematch` takes league games only), so no candidate was checked against it; `speedhelp_fullfeed`'s change acts from turn 58 on `archipelago`, long before the finding's turns, and its rematch went from a win to a draw (not read further). Nothing in this half compares a candidate's ratings, and no holdout game was opened.

**Time so far** (from 09:27:54, `league clock report`):

| Step | Start | End | Minutes | Share |
| --- | --- | --- | ---: | ---: |
| 0 ledger | 09:27:54 | 09:29:11 | 1.3 | 12% |
| 1 measure | 09:29:11 | 09:29:48 | 0.6 | 6% |
| 2 study | 09:29:48 | 09:34:25 | 4.6 | 44% |
| 2 study: subagents | 09:30:20 | 09:34:25 | 4.1 | 39% |
| 3 vary | 09:34:26 | 09:37:54 | 3.5 | 33% |
| 3 vary: six candidate subagents | 09:34:46 | 09:37:45 | 3.0 | 29% |
| 4 gate: head-to-head | 09:37:54 | 09:38:00 | 0.1 | 1% |
| 4 gate: check.sh | 09:38:00 | 09:38:14 | 0.2 | 2% |

10.4 minutes to the hand-over's start (iteration 37's first half: 12.5). Step 0 includes `scripts/check.sh` (55 s, the first Go build of the bots' tests on this machine); step 1 was 6,384 matches, all cached (34 s). The study: six subagents (the real game and seven league games) at once, the longest 2.8 minutes (`reef` and `archipelago` together), then checking the evidence. The candidates: six Sonnet subagents at once, each with its rematches and head-to-head, the longest 3.0 minutes; their head-to-heads queued one after the other on the machine (waits of 6 to 16 s) and played 38 matches each in 7 to 9 s. No candidate needed formatting after its head-to-head (iteration 37's proposal, done). **Speed-up:** the first half is now mostly thinking; the one measurable saving left is `scripts/check.sh` in step 0 (55 s here against 4 s in iteration 37), whose Go build cache could be restored with the league cache.

**Second half** (another runner, from the hand-over; the gate's, the selection's and the final tables' matches were played by eight runners into the cache, and every run below read them from it).

**Gate.** `scripts/check.sh` passes (97 tool tests, the bots' Go tests ok). `uv run league tournament --focus speedhelp_fullfeed,speedhelp_landlate,speedhelp_livefront --parents --strict --run-id iteration-38-parents` (114 matches) and `... --strict --run-id iteration-38-candidates` (2,280 matches) both exit 0, all cached: no match unplayed, no failed turn; slowest turns 8.3 ms (`speedhelp_landlate`), 7.8 (`speedhelp_fullfeed`), 7.7 (`speedhelp_livefront`). All three play.

**Selection, training** (`iteration-38-select`, 8,664 matches, all cached, exit 0): all three pass both rules.

| Candidate | Against parent | Rating (parent 2060) | Holdout (`iteration-38-select-holdout`, 6,840 matches; parent 2103) | Holdout against parent | Decision |
|---|---|---|---|---|---|
| `speedhelp_landlate` | 21.5/38 | **2125** | **2155** | 17/30 | **promoted**: the new champion |
| `speedhelp_fullfeed` | 21/38 | 2073 | 2132 | 17/30 | **promoted** |
| `speedhelp_livefront` | 20/38 | 2064 | 2081 | 15.5/30 | **rejected**: its holdout rating is below its parent's (2081 against 2103) |
| `speedhelp_lastchance` | 19/38 | not played | not played | | rejected in the first half: no more than half against its parent |
| `speedhelp_holdspare` | 19/38 | not played | not played | | rejected in the first half |
| `speedhelp_lowfall` | 17/38 | not played | not played | | rejected in the first half |

`speedhelp_landlate`'s gain is the largest since the line began: 65 points over its parent on training and 52 on holdout, and on training it scores at least as much as its parent against every other player (25 against `harrier_feedkeep` where the parent took 22, 24.5 against `sameturn_endreserve` where it took 21). The two promoted candidates split by map set: on training `speedhelp_landlate` beats `speedhelp_fullfeed` 22.5 of 38, on holdout `speedhelp_fullfeed` beats it 21 of 30. `speedhelp_fullfeed` scored less than the parent against seven players on training, `ori_like` most (27 against 34): its feeding leaves castles thinner against a strike.

**Status changes:** `speedhelp_landlate` and `speedhelp_fullfeed` are active; `speedhelp_landlate` is the champion and `hosting/lambda/bot` now names it. `feedkeep_speedhelp` is **retired**: `speedhelp_landlate` matches or beats its row of the training pair table against every other player. That makes nine active bots, but none is retired: in the selection's training pair table no active bot's row is matched or beaten everywhere by another's (the nearest: `harrier_attackers` by `speedhelp_landlate`, which misses it only against `safe_hold`, 27 to 33; `speedhelp_fullfeed` by `speedhelp_landlate`, only against `safe_hold`, 27 to 28). With seven retired, the lowest rated, **`safe_hold` (1745 in the selection), is deleted**. It was the last bot of the old `hold_` line, and the field's last strategy from outside the `ori_hold` family apart from the sparring bots (see **The league itself**). `speedhelp_livefront`'s directory is deleted. Active: `speedhelp_landlate`, `speedhelp_fullfeed`, `harrier_feedkeep`, `harrier_front`, `harrier_attackers`, `growtrickle_feedkeep`, `sameturn_endreserve`, `stallfeed_growtrickle`, `endreserve_stallfeed`; retired: `feedkeep_speedhelp`, `sameturn_stallfeed`, `exact_sameturn`, `exact_stallfeed`, `ori_hold`, `ori_hold_exact`; sparring: `ori_mimic`, `ori_like`.

Training maps (`iteration-38-train`, 7,106 matches, all cached, exit 0):

| Player | Rating | Score | W | D | L |
| --- | --- | --- | --- | --- | --- |
| speedhelp_landlate | 2143 | 0.801 | 514 | 128 | 80 |
| speedhelp_fullfeed | 2082 | 0.742 | 445 | 181 | 96 |
| feedkeep_speedhelp (retired) | 2072 | 0.731 | 439 | 178 | 105 |
| harrier_feedkeep | 2056 | 0.715 | 427 | 178 | 117 |
| harrier_front | 2017 | 0.672 | 388 | 194 | 140 |
| harrier_attackers | 2014 | 0.669 | 390 | 186 | 146 |
| growtrickle_feedkeep | 1977 | 0.627 | 352 | 201 | 169 |
| sameturn_endreserve | 1962 | 0.609 | 340 | 200 | 182 |
| stallfeed_growtrickle | 1962 | 0.609 | 346 | 187 | 189 |
| endreserve_stallfeed | 1952 | 0.598 | 331 | 201 | 190 |
| sameturn_stallfeed (retired) | 1874 | 0.508 | 239 | 255 | 228 |
| exact_sameturn (retired) | 1867 | 0.500 | 239 | 244 | 239 |
| exact_stallfeed (retired) | 1817 | 0.444 | 197 | 247 | 278 |
| ori_hold (retired) | 1808 | 0.434 | 183 | 261 | 278 |
| ori_hold_exact (retired) | 1803 | 0.429 | 192 | 236 | 294 |
| ori_mimic (sparring) | 1800 | 0.426 | 179 | 257 | 286 |
| ori_like (sparring) | 1551 | 0.219 | 142 | 32 | 548 |
| level1 | 1546 | 0.124 | 0 | 160 | 486 |
| level2 | 612 | 0.000 | 0 | 0 | 646 |
| level3 | 612 | 0.000 | 0 | 0 | 646 |

Holdout maps (`iteration-38-holdout`, 5,610 matches, all cached, exit 0):

| Player | Rating | Score | W | D | L |
| --- | --- | --- | --- | --- | --- |
| speedhelp_landlate | 2159 | 0.789 | 404 | 91 | 75 |
| speedhelp_fullfeed | 2132 | 0.763 | 396 | 78 | 96 |
| feedkeep_speedhelp (retired) | 2109 | 0.740 | 351 | 142 | 77 |
| harrier_feedkeep | 2092 | 0.723 | 331 | 162 | 77 |
| growtrickle_feedkeep | 2080 | 0.711 | 324 | 162 | 84 |
| harrier_attackers | 2033 | 0.660 | 299 | 154 | 117 |
| harrier_front | 2028 | 0.654 | 295 | 155 | 120 |
| stallfeed_growtrickle | 1993 | 0.614 | 268 | 164 | 138 |
| endreserve_stallfeed | 1974 | 0.592 | 249 | 177 | 144 |
| sameturn_endreserve | 1957 | 0.573 | 238 | 177 | 155 |
| sameturn_stallfeed (retired) | 1902 | 0.511 | 189 | 204 | 177 |
| exact_sameturn (retired) | 1896 | 0.504 | 185 | 204 | 181 |
| exact_stallfeed (retired) | 1832 | 0.433 | 150 | 194 | 226 |
| ori_hold_exact (retired) | 1815 | 0.416 | 140 | 194 | 236 |
| ori_hold (retired) | 1807 | 0.407 | 136 | 192 | 242 |
| ori_mimic (sparring) | 1800 | 0.400 | 134 | 188 | 248 |
| ori_like (sparring) | 1610 | 0.239 | 136 | 0 | 434 |
| level1 | 1574 | 0.125 | 0 | 128 | 382 |
| level3 | 965 | 0.004 | 2 | 0 | 508 |
| level2 | 684 | 0.000 | 0 | 0 | 510 |

**Champion:** `speedhelp_landlate`, **2143** on training (iteration 37's champion `feedkeep_speedhelp`: 2061, now 2072 in a field without `safe_hold`) and **2159** on holdout (iteration 37: 2121, now 2109). The ratings of this entry's final tables are one player smaller than the selection's, which lifts most of them a little.

**Real game 474, what this iteration did for it:** its deciding mistake, three fully upgraded castles saving apart while one enemy stack grew (turns 80 to 98), is what `speedhelp_fullfeed` answers, and it was promoted, but it is not the champion, so the hosted bot doesn't carry it yet. The champion's fix, strikes that land before the limit, is from the league's games, not this one. The middle-castle race (castle 4 paid from home on turn 17, castle 2 retaken eight times) had no candidate that passed: `speedhelp_holdspare` (19/38) was the one aimed at it. No candidate could be rematched on the real game.

**Where it still loses:** on training its map row is worst on `strait` 18/38, `circle` 22, `claw`, `gyre` and `rill` 23, `shelf` 25; on holdout `ridge` 11/38 and `brine` 21. Its pair row is closest against its parent (21.5/38), `speedhelp_fullfeed` (22.5; 9/30 on holdout) and `sameturn_endreserve` (24.5). `strait` is still the map the line lost through iteration 37's speed-help (`speedhelp_lastchance` took it back 2/2 and lost `gyre` and `haven`). **The next iteration starts with** the graft of `speedhelp_fullfeed`'s feeding into `speedhelp_landlate` (each wins the other's map set; the Lessons say such grafts have passed four times out of four), and a founder for **The league itself**'s first point. Still open from the hand-over: the safety checks count an enemy castle's soldiers but not its own groups landing on it, the most frequent cause in this iteration's games and the real one, which has failed twice in other forms.

### The league itself

- **One family, raised for the third iteration, and narrower now.** Every active bot and every retired one descends from `ori_mimic` through `ori_hold`; the population rule deleted `safe_hold`, the last bot of another line, this iteration. Outside the family only the two sparring bots and the default levels remain. Of the champion's 19 opponents, 14 descend from `ori_hold` and a 15th is `ori_mimic`, the line's root. Iterations 36 and 37 raised this and nobody answered it: a founder has not been written since iteration 34's `harrier_front`, itself on this line's scaffolding. *What an iteration can do:* the next iteration writes a founder from the rules and the Lessons, not from this code, before its other ideas. *What only a person can do:* an outside opponent or a sparring bot of another strategy; and exempting the last bot of a strategy from the deletion rule, so that a test the field no longer takes isn't removed by a rating.
- **The population rule no longer keeps six active** (second iteration): nine are active, kept by a point or less against `safe_hold`, a bot now deleted, or `ori_like`. *For a person:* a tolerance in the "matched everywhere" rule, or a cap that retires the lowest rated anyway.
- **Who teaches nothing.** `level2` and `level3` win no game on either set of maps (two wins for `level3` on holdout), `level1` only draws: three of 20 players add only the anchor's spread.
- **What the numbers can separate.** Both promotions came from head-to-heads of 21 and 21.5 of 38 with 19 and 22 draws; the two promoted siblings swap order between the map sets (22.5 of 38 one way on training, 21 of 30 the other on holdout). The training ratings, 65 points apart, are clearer than the head-to-heads. *For a person:* more than two games per pair and map, or more maps.
- **What the league can't show.** The real games' opening race on `claw` is still not played in the league: `ori_mimic` plays that opening as our line does (raised in iteration 37). *For a person:* a sparring bot rebuilt from the real games 471 to 474.

**Time:** the whole run from 09:22 UTC (`runs/rsi/times.txt`): the claim 0.4 minutes; the population's warm-up on eight runners, 4.0 minutes (median runner 3.2); the first half's job 13.0 minutes, Claude's part 12.0 and its own clock 10.4 (above); the gate's eight runners, 2.9 minutes (median 2.0); then this second half, from about 09:43: about a minute of setup before its clock, then (`league clock report`)

| Step | Start | End | Minutes |
| --- | --- | --- | ---: |
| 4 gate: check.sh | 09:44:39 | 09:45:39 | 1.0 |
| 4 gate: candidates (both runs) | 09:45:40 | 09:46:12 | 0.5 |
| 5 select (both runs and the status rules) | 09:46:19 | 09:47:09 | 0.8 |
| 5 final tables | 09:47:10 | 09:47:15 | 0.1 |
| 6 record (with `check.sh`, 10 s) and 7 report | 09:47:37 | 09:49:37 | 2.0 |

The second half: 5.0 minutes on its clock, 09:44:39 to 09:49:37. Total: about 28 minutes from the claim (09:22) to the report (iteration 37: about 25). **Where it went:** playing about 7 minutes (the two rounds of runners, each as long as its slowest runner; every tournament on the halves' machines read the cache in 1 or 2 seconds, and the first half's head-to-heads played 38 matches each in 7 to 9 s); thinking about 11 minutes (the first half's study and candidates, about 8 of its 10.4 minutes, and this half's selection rules, record and report, about 3); setup about 6 minutes (four jobs' checkout and tools, and `scripts/check.sh`'s first Go build, 55 s in the first half and 60 s here, against 3 s in iteration 37's Python second half); queue 0.1 minutes; no failure. **Why it was slower than iteration 37:** the warm-up took 4.0 minutes against about 1 (its slowest runner played its shard for 3.7 minutes): probably the population's Go matches weren't in the downloaded cache yet, since every match key changed with the Go bots and their own measurement was made on a desktop; not verified here. That cost is once. The second is the Go build: each job downloads the Go modules (the first tournament of each job prints them) and builds the tests and bots from nothing. **What to change**, by who can do it: *the workflow* (`.github/workflows/real-game-iteration.yml`): restore the Go module and build caches (`~/go/pkg/mod`, `~/.cache/go-build`) and `runs/bin/` with the league cache, about 1 minute a job, 4 to 5 minutes a run; raised by iteration 37 (the built runner) and this iteration's first half, not yet done. *The next iteration:* nothing in its order; the second half's own time is now the record's writing, which needs no machine. *The game or its runner, a person's settings:* nothing proposed.

## Setup after iteration 38: how the league breeds

**The entry after this one replaces this entry's margin and noise** with a chance by luck that counts a map's games as one, and its numbers with numbers on more maps. Where the two differ, the next entry and the `league-evidence` skill hold.

**Date:** 2026-11-23. A change of the rules of the loop, made between iterations after a review of the ledger and of the population's games, with a search of the research on loops like this one. No bot changed, and no iteration ran. The review was measured on the population of iteration 36, before iteration 37's champion and before the bots were Go; the Go ports play the same games, so its numbers stand for the bots it names. **What the next iteration finds** (not done here: only an iteration changes `bots/`). Measured on the population of iteration 37, sixteen bots, 6,384 matches on the training maps, all from the cache. (Iteration 38 merged before this entry did, with two promotions and without `safe_hold`: the entry after this one has the list for its population.) Thirteen pairs play alike, and by the rule, taken until no pair is left, nine bots leave. In the first pass: `ori_hold_exact`, `exact_sameturn`, `endreserve_stallfeed`, `harrier_front`, `ori_hold`, `exact_stallfeed`, `stallfeed_growtrickle`, and `harrier_feedkeep`, which ends half of its games as the champion promoted from it does. With those gone, `sameturn_endreserve` and `sameturn_stallfeed` end 55% of their games the same, and `sameturn_stallfeed` leaves in the second. That leaves `feedkeep_speedhelp`, `harrier_attackers`, `growtrickle_feedkeep` and `sameturn_endreserve` active, `safe_hold` retired, and the two sparring bots: a round robin of 1,596 matches on the training maps where there were 6,384. The champion's rating in that field is 2023, not 2061, with no bot changed: a rating belongs to its table. Its weakest pairing is `sameturn_endreserve`, 21 of 38. It then loses 68.5 points, 47.5 of them to its own line, in a third of its games; before, 147.5 of 162.5 to its line and `ori_mimic`, in 72% of them. The iteration decides on its own measurement, not on this list. With no side line, and no player outside the main line taking a third of the points from the champion (`safe_hold` takes 11 of 38, `ori_mimic` 6), its slate of three is an exploiter, a founder and one place for the main line.

**What the smaller field can tell.** Counted against the six bots and three default bots that would have stayed in iteration 36's population, the twelve past steps come out as six promoted (`harrier_front` 40 and 26 on training with 26 and 15 on holdout, `sameturn_endreserve`, `stallfeed_growtrickle`, `exact_sameturn`, `exact_stallfeed`, `ori_hold`) and six not: the four above, `growtrickle_feedkeep` (21 and 25 on training, 24 and 4 on holdout), and `harrier_feedkeep` itself (19 and 16, 14 and 6: confirmed on holdout, a margin of 11 together against the 14.8 that clear asks, so unresolved). The copies had made its step look surer than the games against distinct opponents show. A change of that size needs about 500 games next to the parent's to be clear, and the cleared field with 34 maps gives about 400: that is why every iteration now adds three maps, and why places of the slate go to candidates that change more.

**Founders worth founding again**, now that a founder need not beat the champion at once: `opener` and `opener_safe` (production to level 3 before anything is sent: above their parent on training, the best of any bot against the player's bot, 33 and 61 points short on holdout), `converge` (11 of 20 against the champion), `counter` (13 of 26), `ambush` (30 of 34 points on `circle`).

**Not done, not verified.** No iteration has run under these rules; iteration 38 was running under the old ones while this was written. The margins were checked on the twelve past promotions above, not on new candidates; whether they promote more of what is real is for the next iterations to show, by the numbers above taken again. No outside opponent was in this checkout. The margins treat games as independent, which they are not: an interval that counts a map's games as one is in `league-breeding`'s list of what the tools don't measure yet, with maps that are not mirrors, behaviour read from the demos, and opponents nobody studies.

**Ideas not tried:** iteration 36's, as it left them: the level frozen games inside the line; `circle`; `claw`'s middle castle. The first is a game inside the line, of which at most half of the games studied may be. Outside the line, `safe_hold` takes both games from the champion on `claw`, `delta` and `loch`.

## Setup after iteration 38: a map counted as one, draws told apart, and twenty more maps

**Date:** 2026-11-23. A second change of the league's setup after the breeding rules above, made between iterations and measured with tournaments on both sets of maps. No bot changed, and no iteration ran. It was measured on the population of iteration 37; iteration 38 merged meanwhile, and the standings and **What the next iteration finds** below are of its population. It replaces the margin and noise of the entry above with a chance that counts a map's games as one, reads who led in a drawn game, and adds twenty maps. A fourth thing was built, measured and not kept: maps that are not mirrors.

**What changed:**

- **By luck, a map's games counted as one.** The table of a bot against its parent no longer prints a noise. It prints the margin (better minus worse), the maps the bot did better and worse on, and **By luck**: the chance that a change which does nothing gives such a margin when each map's margin could as well have had the other sign. It is exact, and it can't be small on few maps. **Confirmed** is now a margin above 0 with by luck at 20% or less, **clear** at 5% or less, **clearly worse** a margin below 0 at 20% or less. A fix or a graft is promoted when it is not clearly worse on the training maps, no more than three points below its parent against the references, confirmed on the holdout maps and clear on all maps together, which is one more run: `--maps all --add CANDIDATES`. The table's last column says which of those words a run's margin comes to. Everything else in the rules above stands.
- **Draws told apart.** When a bot and its parent both drew against the same opponent, on the same map, from the same seat, the bot did better if it out-produced its opponent over the game and its parent didn't, or its parent was out-produced and it wasn't. The table says how many of the better and worse games were such draws. The tool reads it from the demos; ratings and points still count a draw as half.
- **Twenty maps.** Training, seeds 370001 to 370010: `bayou`, `breakwater`, `causeway`, `estuary`, `fjord`, `headland`, `isthmus`, `lowtide`, `moraine`, `shingle`. Holdout, seeds 370011 to 370020: `barrens`, `floe`, `glacis`, `hollows`, `kelpbed`, `ledge`, `mudflat`, `narrows`, `outcrop`, `saltpan`. The sets are 29 and 25. Nobody has looked at a holdout map's file or games.
- **`league delete` refuses the champion** that `hosting/lambda/bot` names, as it refuses a sparring bot, and the table of the bots that play alike says which maps it is of: the rule reads the training maps' table.
- **`league new-map` takes a name of lower-case letters and digits only**, which is what the check of an iteration's changes lets a new map be named: a name with a hyphen was made and then refused at the end of the iteration.

**Measured.**

- **Games are not separate draws.** On the 19 training maps of iteration 37, `harrier_feedkeep` did better than its parent in 88 games against the others and worse in 60. As 148 separate games that is one chance in a hundred. They came from 13 maps, of which five went the other way: one chance in four. Over all 34 maps, counting games gave the past promotions two to three times the certainty that counting maps does.
- **A draw says who led.** Of 2,429 drawn games between league bots on the 34 maps, one side out-produced the other over the game in 936. That side was the higher-rated bot in 85% of them; the winner of a game decided at the turn limit is in 79%. The side with more soldiers at the end was the higher-rated in 46%: the bot that never strikes ends with the most. Told apart this way, the large past steps grew (`harrier_front` from a margin of 106 games over the 34 maps to 152, `sameturn_endreserve` from 141 to 208) and the ones that showed nothing still showed nothing (`harrier_attackers` 6 and 6, `feedkeep_speedhelp` 10 and 8).
- **Maps that are not mirrors: not kept.** Eight seeds, each as a mirror and in four uneven forms, the whole population on each (13,440 matches). With a castle of a neutral pair moved half a step and made one step cheaper or dearer, draws fell and games at the turn limit fell, but the seat then decided a third of the pairs of games, and the past promotions showed less, not more:

| Kind of map | Drawn | At the limit | Pairs with one bot ahead | Pairs split by seat | The 13 past steps: margin in the known direction, of games changed |
|---|---|---|---|---|---|
| Mirror | 14% | 46% | 76% | 11% | +107 of 511 |
| One pair moved and repriced | 9% | 36% | 61% | 33% | +68 of 388 |
| Every pair moved and repriced, by chance | 10% | 39% | 60% | 33% | +63 of 281 |
| Every pair moved and repriced in team 1's favour | 10% | 41% | 57% | 38% | +37 of 373 |
| Every pair moved, none repriced | 13% | 53% | 67% | 23% | +148 of 494 |

  A neutral castle that costs one step less is too much of an edge in this game. Moving castles without changing their price kept the seats even and the draws as they were; its +148 against the mirrors' +107 is inside what eight maps vary by (seed by seed the mirrors gave from -20 to +42). The generator's option and its code were removed. With the copies gone, one bot comes out ahead in 89% of the pairs on mirrors.
- **The twenty maps.** `setup-38-train`, 9,744 matches of which 3,360 were played (146 s, 23 a second on 12 at once), and `setup-38-holdout`, 8,400 of which 3,360 were played (139 s), both exit 0 with `--strict`, no failed turn. The matches on the old maps are the cached ones.
- **The past promotions on 54 maps.** Each of the thirteen parent-to-child steps in the population, in the whole field: better and worse games (of them draws told apart), the margin, and by luck.

| Child | Training (29 maps) | Holdout (25 maps) | All 54 maps | By the rule |
|---|---|---|---|---|
| `feedkeep_speedhelp` | 91, 77 (2, 2 draws): +14, 33.1% | 89, 50 (0, 0 draws): +39, 10.8% | +53, 10.6% | unresolved |
| `harrier_feedkeep` | 125, 111 (6, 0 draws): +14, 39.2% | 104, 89 (4, 2 draws): +15, 38.0% | +29, 33.2% | unresolved |
| `harrier_attackers` | 20, 13 (0, 0 draws): +7, 20.9% | 6, 2 (0, 0 draws): +4, 15.6% | +11, 9.9% | unresolved |
| `harrier_front` | 212, 72 (28, 2 draws): +140, 0.2% | 162, 80 (54, 4 draws): +82, 0.8% | +222, under 0.1% | promoted |
| `growtrickle_feedkeep` | 123, 100 (10, 4 draws): +23, 32.3% | 144, 75 (4, 2 draws): +69, 8.6% | +92, 9.0% | unresolved |
| `stallfeed_growtrickle` | 50, 17 (0, 0 draws): +33, under 0.1% | 36, 11 (0, 0 draws): +25, 0.2% | +58, under 0.1% | promoted |
| `endreserve_stallfeed` | 47, 38 (3, 2 draws): +9, 38.2% | 16, 6 (0, 0 draws): +10, 9.4% | +19, 24.7% | unresolved |
| `sameturn_endreserve` | 242, 78 (42, 0 draws): +164, 0.3% | 228, 49 (55, 0 draws): +179, 0.2% | +343, under 0.1% | promoted |
| `sameturn_stallfeed` | 41, 27 (6, 6 draws): +14, 20.7% | 12, 13 (0, 0 draws): -1, 50.0% | +13, 25.0% | unresolved |
| `exact_sameturn` | 88, 11 (0, 0 draws): +77, 0.3% | 93, 18 (4, 0 draws): +75, 0.5% | +152, under 0.1% | promoted |
| `exact_stallfeed` | 31, 13 (11, 6 draws): +18, 15.6% | 7, 1 (0, 0 draws): +6, 25.0% | +24, 7.4% | unresolved |
| `ori_hold_exact` | 64, 66 (6, 2 draws): -2, 48.6% | 66, 76 (12, 18 draws): -10, 39.4% | -12, 39.8% | rejected: short of the rule |
| `ori_hold` | 35, 21 (8, 0 draws): +14, 29.5% | 21, 8 (0, 0 draws): +13, 10.2% | +27, 10.8% | unresolved |

  Four pass, each at under 0.1% over all maps; none of the other nine is below 7%.
- **What the twenty new maps say alone.** No bot was ever chosen on them, so they are the first measurement of these steps that selection hasn't touched. `sameturn_endreserve` (160 better, 25 worse), `stallfeed_growtrickle` (32, 9), `harrier_front` (133, 63), `exact_sameturn` (54, 18) and `feedkeep_speedhelp` (85, 40) hold on them, each at under 4% by luck. `harrier_feedkeep`, 165 better and 96 worse on the 34 maps it was chosen on, is 64 better and 104 worse on the new twenty; `ori_hold`, 43 and 12 on the old maps, is 13 and 17. A bot chosen for scoring well on some maps scored partly by luck on them.

- **Iteration 38's promotions**, in its own field on the 54 maps. `speedhelp_landlate` did better than its parent in 163 games on the training maps and worse in 28, and 144 and 50 on the holdout maps: +229 on all maps at under 0.1%, promoted by this rule as by the old one. `speedhelp_fullfeed` did better in 98 and worse in 101 on the training maps, confirmed on holdout (+43 at 13.9%) and not clear on all maps (+40 at 21.2%): unresolved by this rule. And `feedkeep_speedhelp`'s step over its parent is +80 on all maps at 4.6% in this field, where it was +53 at 10.6% in iteration 37's: a chance near the line moves with the field.

**The standings on the new sets** (the population of iteration 38, `ori_mimic` at 1800; of the new bots' matches 2,146 and 1,850 were played, at 22 and 21 a second).

Training maps (`setup-39-train`, 29 maps, 10,846 matches, exit 0):

| Player | Rating | Score | W | D | L |
| --- | --- | --- | --- | --- | --- |
| speedhelp_landlate | 2194 | 0.815 | 820 | 157 | 125 |
| feedkeep_speedhelp | 2118 | 0.744 | 696 | 248 | 158 |
| speedhelp_fullfeed | 2117 | 0.744 | 705 | 229 | 168 |
| harrier_feedkeep | 2085 | 0.711 | 655 | 256 | 191 |
| harrier_attackers | 2065 | 0.689 | 641 | 237 | 224 |
| harrier_front | 2064 | 0.688 | 638 | 240 | 224 |
| growtrickle_feedkeep | 2012 | 0.631 | 562 | 266 | 274 |
| stallfeed_growtrickle | 1999 | 0.616 | 553 | 251 | 298 |
| endreserve_stallfeed | 1988 | 0.604 | 524 | 283 | 295 |
| sameturn_endreserve | 1985 | 0.600 | 519 | 285 | 298 |
| sameturn_stallfeed | 1903 | 0.506 | 381 | 354 | 367 |
| exact_sameturn | 1894 | 0.497 | 379 | 337 | 386 |
| exact_stallfeed | 1831 | 0.428 | 305 | 333 | 464 |
| ori_hold_exact | 1817 | 0.414 | 297 | 318 | 487 |
| ori_mimic | 1800 | 0.396 | 269 | 335 | 498 |
| ori_hold | 1799 | 0.395 | 266 | 339 | 497 |
| level1 | 1619 | 0.154 | 0 | 304 | 682 |
| ori_like | 1595 | 0.227 | 234 | 32 | 836 |
| level2 | 566 | 0.000 | 0 | 0 | 986 |
| level3 | 566 | 0.000 | 0 | 0 | 986 |

Holdout maps (`setup-39-holdout`, 25 maps, 9,350 matches, exit 0):

| Player | Rating | Score | W | D | L |
| --- | --- | --- | --- | --- | --- |
| speedhelp_landlate | 2122 | 0.786 | 672 | 150 | 128 |
| speedhelp_fullfeed | 2070 | 0.734 | 628 | 139 | 183 |
| feedkeep_speedhelp | 2054 | 0.717 | 576 | 211 | 163 |
| growtrickle_feedkeep | 2028 | 0.688 | 540 | 228 | 182 |
| harrier_feedkeep | 2017 | 0.676 | 524 | 237 | 189 |
| harrier_attackers | 1993 | 0.649 | 515 | 203 | 232 |
| harrier_front | 1991 | 0.646 | 513 | 202 | 235 |
| stallfeed_growtrickle | 1976 | 0.629 | 477 | 241 | 232 |
| endreserve_stallfeed | 1961 | 0.612 | 448 | 267 | 235 |
| sameturn_endreserve | 1952 | 0.602 | 440 | 263 | 247 |
| sameturn_stallfeed | 1866 | 0.501 | 322 | 307 | 321 |
| exact_sameturn | 1864 | 0.498 | 320 | 306 | 324 |
| exact_stallfeed | 1817 | 0.445 | 273 | 299 | 378 |
| ori_hold_exact | 1810 | 0.437 | 266 | 298 | 386 |
| ori_hold | 1808 | 0.435 | 262 | 303 | 385 |
| ori_mimic | 1800 | 0.426 | 259 | 292 | 399 |
| ori_like | 1578 | 0.232 | 220 | 0 | 730 |
| level1 | 1576 | 0.141 | 0 | 240 | 610 |
| level3 | 852 | 0.002 | 2 | 0 | 848 |
| level2 | 572 | 0.000 | 0 | 0 | 850 |

**Champion:** `speedhelp_landlate`, 2194 on the 29 training maps and 2122 on the 25 holdout maps. On iteration 38's 19 and 15 it was 2125 and 2155: the ratings moved with the maps, with no bot changed.

**What the next iteration finds** (not done here: only an iteration changes `bots/`). On the 29 training maps, by the rule taken until no pair is left, nine of the seventeen bots leave for playing alike another, in three passes: `ori_hold_exact`, `sameturn_stallfeed`, `endreserve_stallfeed`, `ori_hold`, `harrier_front`, `stallfeed_growtrickle` and `exact_stallfeed`; then `feedkeep_speedhelp`, which ends 56% of its games as the champion promoted from it does; then `exact_sameturn`. Every retired bot is among them. That leaves six active bots, all of the main line (`speedhelp_landlate`, `speedhelp_fullfeed`, `harrier_feedkeep`, `harrier_attackers`, `growtrickle_feedkeep`, `sameturn_endreserve`), of which the cap of three in a line retires the three lowest-rated that are not the head, and the two sparring bots: 3,016 matches on the training maps where there are 10,846, and the champion at 2167 in that field. Its weakest pairing is `speedhelp_fullfeed`, 31.5 of 58. **No bot of another line is left**: `safe_hold` was deleted in iteration 38, and of the sparring bots `ori_like` takes 6 of 58 points from the champion and `ori_mimic` 3. The slate of three is an exploiter, a founder and one place for the main line. The iteration decides on its own measurement, not on this list.

**Not done, not verified.** No iteration has run under these rules. The two thresholds, one time in five and one in twenty, are a choice: with them, four of thirteen past promotions pass, and a step the size of the champion's over its parent ends unresolved. Whether that is too strict for the league to move is for the next iterations to show. No outside opponent was in this checkout. A longer game was not tried: more turns would let some drawn games end, and the frozen ones would stay frozen.

**Time.** The steps of this work were not clocked with `league clock`, which is the first thing to do differently: only the tournaments' own lines are measured. They give 19 minutes of playing in all, at 21 to 24 matches a second on 12 at once: two calibration runs of 8,064 matches (333 s and 342 s), the twenty maps (146 s and 139 s), and iteration 38's two new bots on all 54 (99 s and 88 s). The calibration runs were the largest share and one of them was a second pass, played because the first uneven form was too strong and its favoured maps had a bug that a test found while the run was playing: writing the test before the run would have saved six minutes. Reading the demos of drawn games adds about 2 to 5 seconds a listed bot to a run's tables (70 s for fifteen bots on all 54 maps). **To change:** the runner could report each team's production over the game with the result, which is an issue for the game's repository; until then the cost is paid once a run.

## Iteration 39: the real opponent's habits in the league's games, a freeze exploited, and a founder from them

**Date:** 2026-11-23. **Maps:** 30 training, 27 holdout: the map sets grew by `cairn` (training, seed 3903) and `sandbar` and `tideway` (holdout, seeds 3901 and 3902), so every rating moved with no bot changed. **Matches:** 11,220 in the first measurement (`iteration-39-before`, 374 played), 3,120 once the copies had left. Run on one machine (not split across runners); the number was claimed with `scripts/claim-iteration.sh`. No real game was named: the hosted bot's games 471 to 474 were studied in iterations 37 and 38. Six candidates, the exploiter and the founders written by subagents, the two fixes by Sonnet subagents, the graft here.

**The real games' lessons in this iteration.** Every study brief carried the ledger's lessons from real games as a checklist (the middle castles paid from far away, captures sized to take, a border castle emptied beside an enemy castle its own batches are landing on, castles saving apart, harassment that freezes nothing, a front fed in batches with strikes from two or three castles, the upgrade beside a stocked enemy castle, long walks and trickles). Of the seven league games studied (five against the sparring bots, the long win, one inside the line), captures retaken within a few turns showed in all seven, the opponent's batches and multi-castle strikes in six (in part on `archipelago`), and the border castle emptied beside an enemy castle being fed in five (`haven`, `isthmus`, `claw` against `ori_mimic`, `cairn`, `claw` against `ori_like`; a variant on `estuary`), where it decided four of the games. The slate took three of its six places from them: the graft for game 474's deciding mistake, the third form of the inbound count (lesson 3), and a founder built from what the opponent of games 471 to 474 did. Two of the three were rejected by the league: the inbound count clearly worse, the graft by its points against the sparring bots, which stand in for the real opponents; the founder was admitted.

**The population as found.** Eleven pairs played alike on the 30 training maps. By the rule, in three passes: `ori_hold_exact`, `sameturn_stallfeed`, `endreserve_stallfeed`, `ori_hold`, `harrier_front`, `stallfeed_growtrickle`, `exact_stallfeed`; then `feedkeep_speedhelp` (56% of its games the same as the champion's); then `exact_sameturn` (51% with `sameturn_endreserve`). Six active bots were left, all in the main line, and the cap of three retired the three lowest that are not the head: `harrier_attackers`, `growtrickle_feedkeep`, `sameturn_endreserve`. The field: `speedhelp_landlate` 2165, `speedhelp_fullfeed` 2109, `harrier_feedkeep` 2063, the three retired, `ori_mimic` 1800, `ori_like` 1701 and the default levels. Half the champion's games (300 of 600) were against its own line, and 100 of the 109.5 points it lost. Its weakest pairing: `speedhelp_fullfeed`, 28.5 of 60. Outside the line, `ori_like` took 7 of 60 and `ori_mimic` 3: no player outside the line took a third, so the exploiter was due.

**The slate** (six places, no side line): an exploiter (due); two founders (no side line, so both free places; the first from what the real opponent did, the second from the rules and the lessons); three for the main line, which promoted in iteration 38: the graft the last entry asked for, and two fixes of findings from the champion's games against the sparring bots.

**Findings** (each game read by its own subagent with `digest`, `--turns` and both bots' logs; the decisive evidence of finding 1 checked here (`haven`, turns 69 and 70); the others rest on the subagents' quoted digest and log lines):

1. **Strikes, help and upgrades empty a castle beside an enemy castle whose own batches are landing on it** (real-game lesson 3). `haven`, team 1 against `ori_like` (`a6307569…`), turn 69: `strike>7 exact 18 0:18` left home with 4 while enemy castle 6 showed 17 with five groups of 12 walking in; turn 70 `strike>0 need 32 5:7 6:28`; home fell on turn 79. `isthmus` (`b3802a0b…`), turn 82: `help>5 0:36` left home with 4 beside castle 2 (8, fed to 60 by turn 85), struck with 56 on turn 86, fell on 90. `claw` against `ori_mimic` (`cfab6f28…`), turns 55 and 56: `production4@0` and `production4@3` (30 to 4 each) beside castle 4 (16, fed to 32 the next turn), struck with 44 on turn 60. `cairn`, team 2 against `ori_like` (`2bba81df…`), turns 61 and 65: `feed>3 1:18` and `1:16` left home with 4 beside castle 5 with batches of 12 landing; struck with 50 on turn 68. **Cause:** `reserve()` and `holds()` take an enemy castle as its soldiers and growth, not the groups landing on it. **Idea:** count them (third form, after iterations 26 and 37).
2. **Feeding a castle defence has given up.** `claw`, team 2 against `ori_like` (`4c4bb667…`), turns 64 and 65: `cannot hold>5 cannot hold>6 feed>5 4:17`, then `feed>5 1:12`; castle 5 fell on 66 with the feeds walking, castle 4 (left with 4) on 75. `haven` turns 67 and 79 (`cannot hold>7 feed>7 4:10`), `isthmus` turn 36 (`cannot hold>2 feed>2 0:13`, the 13 lost in a clash with 27). **Cause:** `front()` ignores `defend()`. **Idea:** a castle defence couldn't hold is never the front (iteration 38's `speedhelp_livefront`, its second try).
3. **Fully upgraded castles save apart.** `estuary` against `speedhelp_fullfeed` (`43f2dd1a…`): the two play move for move to turn 80; on turn 81 fullfeed's `feed>5 1:10+` gave its front the soldiers that let it help on turn 84 (`help>7 (same turn) 5:3`), and the champion lost castle 6 on turn 87 and the game in 126. **Idea:** the graft of `speedhelp_fullfeed`'s feeding, as the last entry said.
4. **A long win never converted.** `archipelago`, team 1 against `ori_mimic` (`187e100f…`, won 8 to 4 at the limit): from turn 80 to 294 both sides saved 250 to 900 soldiers a castle (`saving` on 115 turns); no strike went at a stocked castle until `late reserve freed` on turn 295. The reserves against every enemy castle added up to about five times any one of them. Also: castles 4, 8 and 10 stayed at production 1 to 3 for about 240 turns, because `upgrade()` refuses a level when the castle wouldn't hold after it, also when it doesn't hold before it either (castle 4: need(255) = 283 against castle 7's 291). Not given a place (one game): see **Ideas not tried**.
5. **The middle castles, again.** `claw` against `ori_mimic`: move for move to turn 17, then `hold>4:3:10` on turn 18 left castle 4 neutral at 0 for `ori_mimic`'s single soldier on turn 25, as in iteration 38 (its `speedhelp_holdspare`, 19/38, rejected). `cairn`: `expand()` ranked the two contested middle castles (14 turns from both homes) before an uncontested neutral 9 turns away, which stayed neutral until turn 60; `attackPrice()` adds an enemy castle only when its walk is strictly shorter than ours (`walk < turns`). Not given a place: **Ideas not tried**.

| Candidate | Parent | Idea | Against parent | Training (parent's) | Better, worse on training (margin, maps, by luck) | Against the references (parent's) | Holdout | Decision |
|---|---|---|---|---|---|---|---|---|
| `landlate_fullfeed` | speedhelp_landlate | Graft from speedhelp_fullfeed: a castle with every upgrade bought feeds the front what it holds above its reserve, once that is FEED_AT or more. (Rematch: `archipelago`/`ori_mimic` turn 58, `feed>6 0:21+`; win → draw. `archipelago`/`harrier_attackers` turn 58; win at the limit → win in 154. `estuary`/`speedhelp_fullfeed` turn 81, `feed>4 0:10+`; loss → draw.) | **36/60** | 2113 (2105) | 100, 92 (+8; 13 maps better, 9 worse; 35.6%): nothing | 99.5 (110): `ori_mimic` 53.5 (57), `ori_like` 46 (53) | not played | **rejected**: over three points fewer than its parent against the references |
| `landlate_inbound` | speedhelp_landlate | Fix: reserve() and holds() count each enemy castle as its soldiers plus its own side's groups landing on it within 4 turns (and no later than its group could reach ours). (Rematch: `cairn` turn 61, `inbound 5:+24` and no feed, loss in 81 → loss in 100; `claw`/`ori_mimic` turn 27, no `take>2`, loss → win at the limit; `haven` turn 44, `isthmus` turn 52, losses → losses. Uncapped it was far more timid; the cap of 4 turns was tuned in the candidate.) | 22.5/60 | 2031 (2105) | 74, 174 (−100; 6 better, 23 worse; under 0.1%): clearly worse | 103 (110) | not played | **rejected**: clearly worse on training. The third rejection of the mechanism in the line: closed |
| `landlate_lostfront` | speedhelp_landlate | Fix: a castle defend() can't hold this turn is never the front: feed() and stallFeed() send to the next castle by the same order (`feed>3 (not 7)`), or nowhere. (Rematch: `claw`/`ori_like` turn 64, no feed, loss → win; `haven` turn 67, loss → loss; `isthmus` turn 36, loss in 110 → loss in 79.) | 31/60 | 2092 (2105) | 39, 56 (−17; 9 better, 8 worse; 19.4%): clearly worse | 107.5 (110) | not played | **rejected**: clearly worse on training (the idea's second rejection) |
| `punisher` | ori_like (code: speedhelp_landlate's) | Exploiter of speedhelp_landlate: the champion freezes a castle an enemy group bound for it would outgrow; one group of production-times-walk-plus-one, uncapped, keeps walking at every enemy castle of 6 or more (`freeze>`), from any castle while its production is at least the enemy's, and no reserve is kept against a castle so frozen. | against the champion: 36.5, 37.5, 39, 38 in its first four versions, **51/60** as it went to the gate (see below) | 2325 | — | 110 | not played | **admitted**: retired, a fixed opponent |
| `batchfront` | ori_like (code: safe_hold's) | Founder: production to 3 in every castle first, only cheap neutrals until production 4; rear castles feed one front in batches of 12; neutrals paid by the one or two castles nearest them and sized to hold; strikes from up to three castles timed to land together. | against the champion: 12 (safe_hold's code), 6, 4, 18, 10, **22/60** | 1957 | — | 69 | not played | **admitted**: active, a side line; plays alike no bot |
| `waves` | ori_like | Founder: no front, no staging, no standing reserve; every attack a wave whose castles launch so their groups land together, sized to the target plus what its owner can bring within the walk. | against the champion: 7, 5.5, 11.5, 8; **11.5/60** as it went to the gate | not played | — | — | not played | **rejected** at the gate: under a third of the points from the champion |

The gate: `scripts/check.sh` passes (99 tool tests, the bots' Go tests ok). `iteration-39-parents` exits 0 (300 matches); `iteration-39-candidates` (3,900 matches, 3,470 played) failed one turn of `growtrickle_feedkeep`, not a candidate (2,000 ms), and the same command again played that match without a failure and exits 0; the slowest turns of the candidates were 16.0 to 50.9 ms (`landlate_inbound`). In the selection (`iteration-39-select`, 7,020 matches, all cached) neither the founder nor the exploiter plays alike a bot of the league; of the fixes, `landlate_fullfeed` plays alike `speedhelp_fullfeed` (66%) and `landlate_lostfront` the champion (62%).

**The inner loops overran.** The exploiter's and `batchfront`'s writers revised up to three times as the skill says, and between and after the revisions ran single-constant sweeps of the code against the champion: about a dozen variants for `punisher` and about 25 runs for `batchfront`. Both reported it. `punisher`'s points over its sweep of one constant (`freezeFloor`) went from 33.5 to 51; its own versions before the sweeps stood at 38 and 39, over the 36 an exploiter needs, so it is admitted either way, but its 51 is partly fitted to the champion's games on these maps (on holdout it takes 36 of 54). `batchfront`'s 22 is two points over the bar and swung from 9 to 23 with one constant; its writer stopped there. Both are admitted on the code that went to the gate, with this said here. A risk in `punisher` that its tables don't isolate: with `trustFreeze` its reserve ignores an enemy castle one of its groups is walking at, and such groups can die in a clash with a feed batch before they land. *For a person:* the inner loop's limit isn't enforced by anything; a tool that counts the runs of a run-id prefix, or the brief saying "no sweeps" in so many words, would.

**Status changes:** `punisher` retired (an admitted exploiter); `batchfront` active, the first bot of the side line `batchfront`; `harrier_attackers`, `growtrickle_feedkeep` and `sameturn_endreserve` retired by the cap; deleted: the nine copies above, and `landlate_fullfeed`, `landlate_inbound`, `landlate_lostfront`, `waves`. Active: `speedhelp_landlate`, `speedhelp_fullfeed`, `harrier_feedkeep`, `batchfront`; retired: `punisher`, `harrier_attackers`, `growtrickle_feedkeep`, `sameturn_endreserve`; sparring: `ori_mimic`, `ori_like`. `iteration-39-after` lists no bots that play alike.

Training maps (`iteration-39-train`, 3,900 matches, all cached, exit 0):

| Player | Rating | Score | W | D | L | Failed turns | Slowest turn (ms) |
|---|---|---|---|---|---|---|---|
| punisher | 2280 | 0.896 | 632 | 26 | 62 | 0 | 19.3 |
| speedhelp_landlate | 2093 | 0.746 | 493 | 88 | 139 | 0 | 20.7 |
| speedhelp_fullfeed | 2047 | 0.701 | 449 | 111 | 160 | 0 | 17.2 |
| harrier_feedkeep | 2007 | 0.659 | 415 | 119 | 186 | 0 | 18.7 |
| harrier_attackers | 1989 | 0.641 | 416 | 91 | 213 | 0 | 21.9 |
| growtrickle_feedkeep | 1954 | 0.603 | 379 | 111 | 230 | 0 | 20.8 |
| sameturn_endreserve | 1950 | 0.599 | 362 | 139 | 219 | 0 | 21.2 |
| batchfront | 1911 | 0.558 | 390 | 24 | 306 | 0 | 17.7 |
| ori_mimic | 1800 | 0.448 | 262 | 121 | 337 | 0 | 22.8 |
| ori_like | 1668 | 0.338 | 234 | 18 | 468 | 0 | 15.5 |
| level1 | 1455 | 0.067 | 0 | 80 | 520 | 0 | 10.7 |
| level3 | 1008 | 0.005 | 3 | 0 | 597 | 0 | 8.1 |
| level2 | 859 | 0.002 | 1 | 0 | 599 | 0 | 7.3 |

Holdout maps (`iteration-39-holdout`, 4,050 matches, 1,450 played, exit 0):

| Player | Rating | Score | W | D | L | Failed turns | Slowest turn (ms) |
|---|---|---|---|---|---|---|---|
| punisher | 2109 | 0.793 | 499 | 30 | 119 | 0 | 16.9 |
| speedhelp_landlate | 2055 | 0.741 | 445 | 70 | 133 | 0 | 19.4 |
| speedhelp_fullfeed | 2040 | 0.725 | 437 | 66 | 145 | 0 | 23.9 |
| harrier_feedkeep | 2001 | 0.684 | 395 | 97 | 156 | 0 | 22.1 |
| growtrickle_feedkeep | 1987 | 0.669 | 385 | 97 | 166 | 0 | 18.1 |
| harrier_attackers | 1959 | 0.639 | 374 | 80 | 194 | 0 | 18.6 |
| sameturn_endreserve | 1906 | 0.581 | 318 | 117 | 213 | 0 | 22.7 |
| batchfront | 1901 | 0.576 | 365 | 16 | 267 | 0 | 16.1 |
| ori_mimic | 1800 | 0.473 | 252 | 109 | 287 | 0 | 19.7 |
| ori_like | 1610 | 0.319 | 207 | 0 | 441 | 0 | 23.8 |
| level1 | 1391 | 0.056 | 0 | 60 | 480 | 0 | 11.6 |
| level3 | 935 | 0.004 | 2 | 0 | 538 | 0 | 13.6 |
| level2 | 654 | 0.000 | 0 | 0 | 540 | 0 | 18.3 |

**Champion:** `speedhelp_landlate`, unchanged: **2093** on training (this iteration's "before", in the cleared field: 2165; on 30 maps with the copies, 2195; the setup after iteration 38: 2194 on 29) and **2055** on holdout (2122 on 25 maps in the setup after iteration 38). Its ratings fell with no bot changed: the field now holds `punisher`, which takes 51 of 60 from it, and `batchfront`. Against the references: 110 of 120 on training (`ori_mimic` 57, `ori_like` 53), 98.5 of 108 on holdout (49.5, 49). Its weakest pairing is `punisher`, 9 of 60 on training and 18 of 54 on holdout; inside its line, `speedhelp_fullfeed`, 31.5 of 60 and 20 of 54 on holdout.

**Where it still loses:** to `punisher`, which it holds only on `circle` and `reef` (draws), `gyre` (both seats) and single games on `claw`, `lowtide`, `moraine`, `rill` and `archipelago`: it freezes every castle that a group of its own production times the walk walks at. On training its map row is worst on `strait` 11/24, `cairn`, `claw`, `haven` and `shelf` 14, `circle` and `shingle` 15; on holdout `brine` and `tor` 13, `ridge` and `tideway` 14. **The next iteration starts with** the exploiter's games: the champion's freeze under attack is the hole `punisher` found and the hosted opponent's rules share; a fix that lets a castle under a group it outgrows go on spending what leaves it holding (iteration 30's `stallfeed_growtrickle` answered the trickle so) is the main line's first place. And `batchfront` gets its first candidate from its own lost games.

**Ideas not tried:**
- `upgrade()` refuses a level for a castle that doesn't hold either way (`archipelago` against `ori_mimic`, castles 4, 8 and 10 at production 1 to 3 from turn 47 or 80 to 295): refuse only when it holds before and not after. One game; look for it in two more before writing it.
- The reserves against every enemy castle, summed, freeze a level game (`archipelago`, turns 80 to 294): keep one shared reserve against the largest enemy stack. The real game 474's end too.
- `expand()` ranks a contested neutral before a nearer uncontested one, and `attackPrice()` counts only enemy castles strictly nearer (`walk < turns`), so equal walks add nothing (`cairn`, turns 8 to 45, castle 3 neutral until turn 60). Iteration 37's `feedkeep_contested` (18/38) was another form.
- `hold()` accepts a neutral left at 0 (`claw` against `ori_mimic`, turn 18): iteration 38's `speedhelp_holdspare` (19/38) was this; rejected once.
- The exact short strike ignores the target's neighbours (`claw` against `ori_mimic`, castle 2 taken with 2 or 3 four times and retaken in 2 to 9 turns; `archipelago`, castle 9 about 75 times): iteration 37's `feedkeep_exactnear` (18/38), rejected once.
- `defend()` counts a castle at 0 after the last landing as held, and only groups already sent (`estuary` against `speedhelp_fullfeed`, turns 92 to 94).

### The league itself

- **One family, raised for the fourth iteration, answered in part.** Before this iteration every bot outside the sparring and default bots descended from `ori_hold`. Now `batchfront`, on `frontline` code, is the first side line since iteration 25, and `punisher`, though it is the champion's code with one mechanism, plays alike no bot. Of the champion's 12 opponents, 5 are its own line, 2 are its root's sparring bots, `punisher` its own code: still most of its field. *What an iteration can do:* work `batchfront` as a side line. *What only a person can do:* an outside opponent; a sparring bot rebuilt from real games 471 to 474 (raised in iterations 37 and 38).
- **The references and the real games disagree with the head-to-head** (new). The graft for real game 474's deciding mistake beat the champion 36 of 60 and lost 10.5 points to the two sparring bots; the bots that stand in for the real opponent punish the fix the real game asked for. Either the real opponent would punish it too, or the stand-ins don't play like the opponent of games 471 to 474: `ori_mimic` was built from another player's games of 2026-11-22, and plays `claw`'s opening as our line does (raised in iterations 37 and 38). *For a person:* the sparring bot from games 471 to 474, before the next real-game fix is judged by the references.
- **The champion has a hole the league didn't test.** `punisher` takes 51 of 60 (36 of 54 on holdout). Iteration 33's `harrier` had shown the freeze, capped and from fully upgraded castles only; nothing in the field kept the champion's castles under attack since. The exploiter rule found it; it is now a fixed opponent, and the champion's rating includes it.
- **Who teaches nothing.** `level2` and `level3` win 1 and 3 games, `level1` only draws: three of 13 players add only spread (fourth iteration).
- **The inner loop has no limit that a tool checks** (above).
- **What the numbers can separate.** With copies cleared and 30 training maps, both rejections of fixes were clear (under 0.1% and 19.4%); the graft's +8 was nothing at 35.6% though it took 36 of 60 head to head. A head-to-head and the field can point opposite ways, and the rules read the field.

**Time** (`league clock report`, from 16:09:33; the reading of the skills and the ledger before the claim was not clocked):

| Step | Start | End | Minutes | Share |
| --- | --- | --- | ---: | ---: |
| 0 ledger | 16:09:33 | 16:09:49 | 0.3 | 1% |
| 1 measure | 16:09:50 | 16:11:14 | 1.4 | 6% |
| 2 study | 16:11:15 | 16:15:09 | 3.9 | 18% |
| 3 vary | 16:15:10 | 16:24:21 | 9.2 | 42% |
| 4 gate | 16:24:21 | 16:27:06 | 2.8 | 13% |
| 5 select | 16:27:07 | 16:28:46 | 1.6 | 8% |
| 6 record | 16:28:47 | 16:31:09 | 2.4 | 11% |
| 7 report | 16:31:10 | open | 0.2 | 1% |

Total: 21.8 minutes, from 16:09:33 to 16:31:22 UTC.
Slowest: 3 vary (9.2), 2 study (3.9), 4 gate (2.8).
Still open (counted to now): 7 report.

On the clock, from the first step to the record; the reading before it is not in it (iteration 38: about 28 minutes from the claim, split across runners). **Where it went:** playing about 6 minutes (the first measurement's 374 matches in 18 s, the candidates' gate run 3,470 matches in 140 s, the final holdout table 1,450 in 56 s, the head-to-heads and the inner loops' runs inside the subagents); thinking the rest: the study (seven subagents at once, 16:12:36 to 16:14:55, the longest 2.3 minutes) and the candidates (the two fixes 1 minute each with Sonnet; the founders and the exploiter 7.8 to 9.7 minutes, the slowest step of the iteration, mostly their inner loops and sweeps); setup 0.2 minutes (`scripts/check.sh` 9 s); one failure, the gate's failed turn, 2 seconds to play again. **What to change:** *the next iteration:* start the founders and the exploiter at once after the slate, before the study, as this one did, since they need no finding; here they ran beside the study and the fixes. *A tool or the brief:* the inner loop's limit (above), which would also bound its time. Iteration 38's proposal (the workflow restoring Go caches) is still not done; this iteration ran on a desktop and didn't need it.

## Setup after iteration 39: runs in parallel, every match played once

**Date:** 2026-11-24. A change of the league's setup, made between iterations; no bot changed, and no iteration ran. The design and its reasons are [docs/parallel-iterations.md](../docs/parallel-iterations.md).

**What changed.** An iteration was one session from the claim to the merge, 19 to 39 minutes, and every other waited. It is now two parts. A **run** (the `bot-league-iteration` skill's steps 0 to 4) works from the main it started on, beside any number of others, and ends as a proposal on `claude/league-run-<id>`: its candidates, its account `ledger/runs/<id>.md`, the lessons it proposes `ledger/lessons/<id>.md`. The **integrator** (`league integrate`, `.github/workflows/integrate.yml`) decides each proposal on main as it is when it arrives, one iteration each, by the selection and population rules written as code (`league decide`, `league_tools/decide.py`): this entry's next iteration is the first it writes. The **curator** folds the proposed lessons into **Lessons so far**. The lines are data too (`ledger/lines.toml`), and the table above is printed from them.

- **Every match is played once** in the league's life: a shared store (`LEAGUE_STORE`, `league_tools/store.py`) with a lease on each match key, written by every machine that plays (a person's computer, GitHub runners, Lambda), except a Claude step that read real games, which only requests. Until the store is deployed, the cache is one machine's, as before, and the dispatcher starts one run at a time.
- **Work that should happen once is leased** (`league lease`): a run, a real game, a league game to study, a place of the slate, an idea, a name.
- **The slate is the league's** (`league ideas`): the side lines' places, the exploiter when due, founders for free places, superseded grafts, then the champion's mistakes ranked by the maps they cost it points on.
- **Detectors** (`league_tools/detectors/`, `league mistakes`) find known mistakes in every game; a run reads the windows they flag, and adds a detector for a mistake none knows.
- **A candidate whose parent was its line's head at the run's base, and no longer is,** is judged against the head too: promoted only if it passes against both, **superseded** if it beats only its parent. A superseded change is the next graft.
- **Four side lines** instead of two: with parallel runs a side line's place no longer takes the main line's (docs/parallel-iterations.md, Four side lines). To check after ten integrations: if more than half of the side lines closed without a promotion, or the champion's points against the references stopped rising, go back to two.
- **The dispatcher** (`.github/workflows/dispatch.yml`) keeps up to `RSI_MAX_RUNS` (10) automated runs going while the idea queue has places.

**What a rating means** doesn't change: the same anchor, the same rules, the same maps. Each run still adds two holdout maps and a training map, with seeds from its id; the map sets grow faster.

**Not done, not verified.** No run has gone through the integrator on main yet. It was tried end to end on a scratch branch: a copy of the champion proposed as a fix was rejected (no game changed; nothing on the holdout maps), deleted, and recorded as iteration 40 with its row of progress, the champion unchanged at 2093, in one commit. The store and the Lambda players are built and tested on a directory store and stubbed S3, not deployed. The detectors were calibrated on 450 games of three training maps.

## Iteration 40: the freeze answered in an upgrade, a reserve for `batchfront`, and a counter-puncher that takes the main line

**Date:** 2026-11-23. **Maps:** 31 training, 29 holdout: the map sets grew by `wharf` (training, seed 4003) and `dune` and `quay` (holdout, seeds 4001 and 4002), so every rating moved with no bot changed. **Matches:** 4,650 in the first measurement (`iteration-40-before`, 150 played). Run on one desktop, not split across runners, by a session that ran it after the automated iterations of the day stopped (both runs of the real-game iteration for iteration 40 failed in their first half at the check that every ledger entry has its row in `ledger/progress.csv`, which a hand-over can't have yet; their claim was given back). No real game was named. Six candidates were planned and five written: the founder by a subagent on the default model, the graft, the simplification and the two fixes by Sonnet subagents; seven studies by Sonnet subagents.

**The population as found.** No pair played alike on the 31 training maps. The field: `punisher` 2266, `speedhelp_landlate` 2104, `speedhelp_fullfeed` 2057, `harrier_feedkeep` 2011, the retired `harrier_attackers` 1997, `growtrickle_feedkeep` 1958, `sameturn_endreserve` 1952, `batchfront` 1907, `ori_mimic` 1800, `ori_like` 1666. The champion's games against its own line: 310 of 744 (42%), and 100 of the 183 points it lost (55%). Its weakest pairing: `punisher`, 11 of 62. Outside its line `punisher` took 51 of 62 and `batchfront` 22, a third: no exploiter was due.

**The slate** (six places; one side line, `batchfront`): its candidate; a founder for the free side place; four for the main line. The main line had promoted nothing once (not stalled), but the head's last three fixes, grafts and simplifications (iteration 39) were all rejected, so its places were a graft into the head (`punisher`'s harassment), a simplification of the head, and a fix from `speedhelp_fullfeed`, another active bot of the line. The sixth place, a second main-line fix (the neutral take that empties border castles, finding 3), was left out: its form needs a reserve that counts two enemy castles together, which lessons of iterations 2 and 5 say makes this line timid; see **Ideas not tried**.

**Findings** (each game read by its own subagent with `digest`, `--turns` and both bots' logs; the `gyre` evidence and each candidate's diff checked here):

1. **A frozen castle keeps its stock and buys nothing.** `estuary`, the champion as team 1 against `punisher` (`7ffb962f…`), turns 32 to 60: castle 4, at production 1, was frozen on 27 of 29 turns by groups of 6, 7 and 16 (`freeze> 4:1:6` on turns 31, 35, 39) while it held 7 to 58 soldiers (45 at turn 39, 55 at 43), logging `saving`; it bought production 2 and 3 only on turn 50, the one turn no group was bound for it. Castle 2 stayed at production 1 all game. 100 soldiers less production than `punisher` over turns 1 to 70. `haven` against `punisher` (`5be22b0e…`) was lost another way (castle 1 emptied by a take on turn 55, struck with 24 and 8 on 56, `cannot hold>1` until it fell on 62). **Cause:** `upgrade()` refuses any castle `attacked()` marks. **Idea:** a frozen castle may buy a level when after paying it still holds through every landing bound for it.
2. **`batchfront` spends its castles to the minimum beside stocked enemy castles.** `circle` against `level3` (`0351b1fb…`), turns 12 and 15: production 4 (32 to 6) and speed 2 (14 to 8) beside a castle of 44; struck with 29 on turn 16, lost on 19. `gyre` against `ori_mimic` (`c87b210f…`), turn 44: `take>9 need 47 2:5 4:42` left castle 4 with 8 beside castle 3 with 38; `strike>4 need 35` on turn 45, castle 4 lost on 50; turn 54 a feed of 12 left castle 0 with 5, taken on 57. `inlet` against `harrier_feedkeep` (`8cecebed…`), turn 58: a feed left castle 0 with 5 (to a front that held 32), struck with 27, lost on 63. `haven` against `growtrickle_feedkeep` (`44c10294…`), turns 40 to 47: feeds left castle 0 with 5, and castle 3 bought production and speed (40 to 8) while 43 walked at castle 0. **Cause:** `reserve(c)` counts only enemy groups already walking at the castle. **Idea:** keep what the strongest enemy castle in reach could land.
3. **The champion's neutral takes empty border castles.** `strait` against `batchfront` (`8b6dc668…`), turn 30: three castles paid neutral 4 and were left at 2, 3 and 4; castle 6 was struck from turn 31 and fell on 36 (`cannot hold>6` on 33 to 35). `haven` against `punisher`, turn 55 (above). `cairn` against `batchfront` (`a229b353…`): a feed of 28 left castle 1 with 4 toward a castle `defend` had called `cannot hold>3` (iteration 39's lost-front idea, rejected twice). Not given a place: **Ideas not tried**.
4. **`batchfront` strikes the champion with stacks timed to land together, and the champion's help sees them one turn before.** `strait` turns 61 to 66 (groups of 8, 8, 34 and 12 landing on castle 2 together; `outgrows groups bound for 2` until turn 64, `cannot hold>2` on 65), `claw` against `batchfront` (`612d8265…`), turns 58 to 62. No idea that this iteration could write in one change.

| Candidate | Parent | Idea | Against parent | Training (parent's) | Better, worse on training (margin, maps, by luck) | Against the references (parent's) | Holdout: better, worse (margin, by luck); all maps | Decision |
|---|---|---|---|---|---|---|---|---|
| `fullfeed_unfreeze` | speedhelp_fullfeed | Fix: a castle that an enemy group freezes may still buy an upgrade when its soldiers after the cost cover every landing bound for it, its growth until each counted, and holds() passes. (Rematch in the champion's seat against `punisher`: `estuary` both seats, turn 16, `saving` → `production2@2 unfrozen`, losses → wins; `bight` turn 67, loss → loss.) | 33.5/62 | 2103 (2047) | 117, 38 (+79; 21 better, 6 worse; under 0.1%): clear | 102.5 (99.5) | 72, 34 (+38, 4.3%): clear; all maps +115, under 0.1%: clear | **promoted** |
| `batchfront_keep` | batchfront | Fix: a castle spends only down to what the strongest enemy castle within 4 turns could land on it, less its own growth until then (`keep>`). (Rematch: `gyre` turn 43, `inlet` turn 55, `haven` turn 34, a production buy skipped, three losses → wins; `circle` unchanged, still lost to `level3`. Horizon 8: 26/62 against the parent, 14: 20/62, 4 kept: three values tried, one over the brief's two.) | 42/62 | 2006 (1940) | 111, 56 (+55; 17 better, 7 worse; 4.1%): clear | 90 (71) | 150, 24 (+126, under 0.1%): clear; all maps +177, under 0.1%: clear | **promoted** |
| `landlate_punish` | speedhelp_landlate | Graft from punisher: every enemy castle of freezeFloor (6) or more kept frozen by one group of its production times the walk plus one, from any castle while our production is at least the enemy's, in place of the head's one harassed front castle; punisher's trustFreeze not taken. (Rematch against `punisher`: `haven` turn 21 `freeze> 3:1:8`, loss → draw; `estuary` turn 13, loss in 81 → loss in 175.) | 47/62 | 2167 (2077) | 196, 107 (+89; 20 better, 7 worse; 0.6%): clear | 115 (114) | 131, 127 (+4, 46.7%): nothing; all maps +57, 11.4%: confirmed | **unresolved**: not confirmed on holdout, a margin above 0 on all maps |
| `landlate_lean` | speedhelp_landlate | Simplification: defend() no longer buys a speed level in a far castle so its help lands before a castle falls (`help>` with `speed@` on 12 turns in 6 of 11 of the champion's games); 55 lines shorter. | 23.5/62 | 2035 (2077) | 50, 95 (−45; 6 better, 17 worse; 2.8%): clearly worse | 115.5 (114) | not played | **rejected**: clearly worse on training |
| `pounce` | ori_like (scaffolding, with the `ori` line's board helpers) | Founder: a counter-puncher with no front: every castle keeps home what the enemy castles could spare and land on it (their stock above the reserve the main line keeps), less its growth; production then speed only above that reserve; only the neutrals on its side; strikes any enemy castle (or a neutral the enemy is taking) whose exact count at landing, with its growth, burst and the help other enemy castles could spare in time, the castles landing within six turns can spare. | against the champion: 4, 3, 47, **51/62** (three revisions, each from a game read; no sweeps) | 2195 | — | 101 | not played to be admitted | **admitted**, then **the main line** (below) |

The gate: `scripts/check.sh` passes (103 tool tests, the bots' Go tests ok). `iteration-40-parents` exits 0; `iteration-40-candidates` (4,650 matches, 4,267 played in 170 s) exits 0 with no failed turn; the candidates' slowest turns 15.3 to 21.4 ms. In the selection (`iteration-40-select`, 9,300 matches, all cached) `pounce` plays alike no bot; `fullfeed_unfreeze` plays alike its parent (55%), `landlate_lean` plays alike `harrier_feedkeep` (68%) and the champion (53%).

**The main line changed.** In the final tables `pounce`, the head of a side line, rates above the champion on the training maps (2132 against 2041) and on the holdout maps (2073 against 2009), and takes 51 of 62 from it head to head: by the rule it is the champion, and `ori` is a side line, its count at 0. `fullfeed_unfreeze`, the `ori` line's top-rated active bot on training (2054), is its head. **What the rule doesn't ask, and the numbers show:** `pounce` takes fewer points than `speedhelp_landlate` from the sparring bots that stand in for the real opponent: 101 of 124 on training (`ori_mimic` 54, `ori_like` 47) against 114 (59, 55), and 86 of 116 on holdout (52, 34) against 106.5. It loses to `batchfront` (27 of 62) and `batchfront_keep` (23.5). Its edge is over the `ori` line, whose reserves it prices.

**Status changes:** `pounce` active, the main line, the champion (`hosting/lambda/bot`); `fullfeed_unfreeze` active, head of `ori`; `batchfront_keep` active, head of `batchfront`; deleted: `landlate_punish`, `landlate_lean`, `speedhelp_fullfeed` (played alike its promoted child, 60%), `harrier_attackers` (played alike `harrier_feedkeep`, 51%, and took fewer points from the champion of the first measurement: 16 against 19.5). Active: `pounce`; `fullfeed_unfreeze`, `speedhelp_landlate`, `harrier_feedkeep`; `batchfront_keep`, `batchfront`. Retired: `punisher`, `growtrickle_feedkeep`, `sameturn_endreserve`. Sparring: `ori_mimic`, `ori_like`. `iteration-40-after` lists no bots that play alike.

Training maps (`iteration-40-train`, 5,456 matches, all cached, exit 0):

| Player | Rating | Score | W | D | L | Failed turns | Slowest turn (ms) |
|---|---|---|---|---|---|---|---|
| pounce | 2132 | 0.788 | 615 | 41 | 150 | 0 | 19.3 |
| punisher | 2125 | 0.782 | 614 | 32 | 160 | 0 | 23.7 |
| fullfeed_unfreeze | 2054 | 0.710 | 522 | 100 | 184 | 0 | 17.1 |
| speedhelp_landlate | 2041 | 0.695 | 517 | 87 | 202 | 0 | 20.7 |
| harrier_feedkeep | 1980 | 0.629 | 451 | 112 | 243 | 0 | 18.7 |
| batchfront_keep | 1977 | 0.625 | 478 | 52 | 276 | 0 | 15.2 |
| growtrickle_feedkeep | 1946 | 0.592 | 426 | 102 | 278 | 0 | 18.2 |
| sameturn_endreserve | 1934 | 0.578 | 400 | 132 | 274 | 0 | 21.8 |
| batchfront | 1902 | 0.543 | 416 | 44 | 346 | 0 | 26.6 |
| ori_mimic | 1800 | 0.438 | 295 | 116 | 395 | 0 | 22.8 |
| ori_like | 1673 | 0.329 | 253 | 24 | 529 | 0 | 17.8 |
| level1 | 1443 | 0.062 | 0 | 84 | 598 | 0 | 10.7 |
| level3 | 1070 | 0.007 | 5 | 0 | 677 | 0 | 7.2 |
| level2 | 842 | 0.001 | 1 | 0 | 681 | 0 | 6.2 |

Holdout maps (`iteration-40-holdout`, 5,104 matches; the first run played 754 and failed one turn of `pounce` at 2,000 ms, and the same command again played that match without a failure and exits 0):

| Player | Rating | Score | W | D | L | Failed turns | Slowest turn (ms) |
|---|---|---|---|---|---|---|---|
| pounce | 2073 | 0.753 | 553 | 29 | 172 | 0 | 54.1 |
| punisher | 2051 | 0.729 | 533 | 34 | 187 | 0 | 15.4 |
| batchfront_keep | 2035 | 0.713 | 520 | 35 | 199 | 0 | 11.9 |
| speedhelp_landlate | 2009 | 0.685 | 484 | 65 | 205 | 0 | 17.5 |
| fullfeed_unfreeze | 2002 | 0.676 | 480 | 60 | 214 | 0 | 20.3 |
| harrier_feedkeep | 1961 | 0.631 | 431 | 90 | 233 | 0 | 37.9 |
| growtrickle_feedkeep | 1953 | 0.621 | 422 | 93 | 239 | 0 | 18.0 |
| batchfront | 1922 | 0.588 | 428 | 30 | 296 | 0 | 16.1 |
| sameturn_endreserve | 1882 | 0.543 | 356 | 107 | 291 | 0 | 22.7 |
| ori_mimic | 1800 | 0.457 | 288 | 113 | 353 | 0 | 19.7 |
| ori_like | 1653 | 0.330 | 249 | 0 | 505 | 0 | 24.6 |
| level1 | 1377 | 0.047 | 0 | 60 | 578 | 0 | 11.6 |
| level3 | 928 | 0.003 | 2 | 0 | 636 | 0 | 13.6 |
| level2 | 647 | 0.000 | 0 | 0 | 638 | 0 | 18.3 |

**Champion:** `pounce`, **2132** on training and **2073** on holdout. The old champion `speedhelp_landlate`: 2041 and 2009 in these tables, 2104 in this iteration's "before", 2093 in iteration 39's final table. Against the references: 101 of 124 on training, 86 of 116 on holdout (the old champion 114 and 106.5). Its weakest pairing: `batchfront_keep`, 23.5 of 62 on training and 17 of 58 on holdout; `batchfront` 27 of 62.

**Where it still loses:** to the `batchfront` line (73.5 of its 170.5 lost points on training) and to `ori_like` (15 on training, 24 on holdout): bots that keep no reserve, against which its reading of the enemy's spare (stock above the `ori` reserve) undercounts the threat. Its worst training maps: `far-shores` 9/26, `breakwater` 11, `cairn` and `haven` 14, `reef` 15, `circle` and `causeway` 16. **The next iteration starts with** the champion's games against `batchfront_keep` and `ori_like`: a fix that prices a no-reserve enemy's whole stock as its threat is the main line's first place. `ori` and `batchfront` each get a candidate.

**Ideas not tried:**
- The `ori` line's neutral takes empty border castles beside stocked enemy castles (`strait` against `batchfront`, turn 30; `haven` against `punisher`, turn 55): a take may not leave a sender below what the enemy castles that land together could take. Lessons of iterations 2 and 5 say counting more than one enemy castle made bots timid; a form limited to the senders of a take is untried.
- `ori` defence sees a timed multi-castle strike only a turn before it lands (`strait` turns 61 to 66, `claw` turns 58 to 62 against `batchfront`).
- `batchfront`'s `circle` loss to `level3` stands: its keep acts only within 4 turns, and `level3`'s castle is 4 units away at speed 1. A rule for a lone castle.
- `batchfront` sizes a neutral take to the neutral's soldiers now, not at landing (`inlet` turn 10: 4 sent at a neutral of 5).
- The `ori` line's freeze counts long walks from the turn they are sent (`estuary`, castle 2 frozen on about 55 of 57 turns by 16-turn walks): count only groups landing within a few turns.
- The ideas of iteration 39's list stand.

### The league itself

- **The champion is now a bot that the stand-ins for the real opponent like less** (new, first). The main-line rule changed the line on ratings and the head-to-head; `pounce` takes 13 fewer points from the sparring bots on training and 20.5 fewer on holdout than the bot it replaced, and its edge comes from pricing the `ori` line's reserves, which most of the field still is (6 of its 11 non-default opponents are `ori` code). The hosted bot will deploy it. *What only a person can do:* add the references to the main-line rule (a side line's head must not take fewer points from the references than the champion), or decide that ratings alone choose; and, as raised in iterations 37 to 39, a sparring bot from real games 471 to 474. *What the next iteration can do:* the fix above, from the champion's losses to the no-reserve bots.
- **One family, raised for the fifth iteration, now answered.** Three lines live: `pounce` (new code), `ori`, `batchfront` (`frontline` code). The champion's lost points: 50.5 of 170.5 to `ori` bots, 73.5 to `batchfront`'s, 19 to `punisher`, 23 to the sparring bots.
- **Who teaches nothing.** `level2` and `level3` win 1 and 5 games, `level1` only draws (fifth iteration).
- **The inner loop's limit held** in the founder's brief ("no sweeps", three revisions), and was overrun by one value in a fix's horizon. A tool that counts a run-id prefix's runs is still not built (second iteration).
- **The automated iteration can't finish a first half** since the check of `ledger/progress.csv` was added: a hand-over is a ledger entry without its row. Both of today's runs for iteration 40 failed there. *For a person:* let the check skip a hand-over, or have the first half write a provisional row.

**Time** (`league clock report`, from the claim at 17:19:04; the reading of the skills and the ledger before the claim, and the wait for the Actions runs, not clocked): 0 ledger 0.6 min, 1 measure 0.6, 2 study 5.0, 3 vary 4.0, 4 gate 3.3, 5 select 4.4, 6 record 1.9; 19.8 minutes in all, 17:19:04 to 17:38:53 UTC (iteration 39: 21.8 on the clock). **Where it went:** playing about 7 minutes (the gate's 4,267 matches in 170 s, the holdout selection's 2,736 in 114 s, the final holdout table's 754 in 41 s, the subagents' head-to-heads and the founder's runs); thinking the rest: the studies (seven Sonnet subagents at once, 17:22:37 to 17:24:02, the longest 1.5 minutes), the founder (17:21:46 to 17:28:52, 7.1 minutes, beside the studies and the fixes: the slowest single piece, as in iteration 39), the fixes 1 to 1.5 minutes each with Sonnet, the record. No failure but the one timed-out turn, 2 seconds to play again. **What was different:** iteration 39's proposal was done: the founder, the graft and the simplification started before the study, since they need no finding, and the study and the fixes all ran on Sonnet. **To change:** *the next iteration:* the gate's and the holdout's plays (about 5 minutes) are the largest single share left, and they play only the candidates' new matches; nothing to cut there without doing less. *A tool:* the holdout selection could start playing the candidates' holdout matches in the background (`--shard`-like, no tables) as soon as the training selection passes them, while the paired table is read. *The workflow:* the progress-row check above.

## Iteration 41: the new champion's pricing, fixed three ways, and nothing promoted

**Date:** 2026-11-23. **Maps:** 32 training, 31 holdout: the map sets grew by `slough` (training, seed 4103) and `jetty` and `berm` (holdout, seeds 4101 and 4102). **Matches:** 5,632 in the first measurement (`iteration-41-before`, 176 played). Run on one desktop, from the branch of iteration 40 (not yet merged; claimed with `--base`). No real game was named. Five candidates, written by subagents (four on Sonnet, `pounce_strikes` on the default model); eight studies, on Sonnet.

**The population as found.** No pair played alike. The field: `pounce` 2134, `punisher` 2124, `fullfeed_unfreeze` 2055, `speedhelp_landlate` 2040, `batchfront_keep` 1985, `harrier_feedkeep` 1984, `growtrickle_feedkeep` 1949, `sameturn_endreserve` 1935, `batchfront` 1906, `ori_mimic` 1800, `ori_like` 1673. The champion is alone in its line: none of its games or lost points are against its own line. It lost 182.5 points of 704: 40.5 to `batchfront_keep`, 37 to `batchfront`, 19 to `punisher`, 17 to `ori_like`, 15 to `fullfeed_unfreeze`, the rest 8 to 13 each. `batchfront_keep` and `batchfront` each take over a third: no exploiter due.

**The slate** (five places; two side lines): `ori`'s candidate, `batchfront`'s candidate, three for the main line, each a fix of a finding from the champion's games against players outside its line (it has no line of its own yet). A sixth would have been a second fix of the same pricing.

**Findings** (eight games, each by its own subagent; the decisive lines of findings 1 and 4 checked in the candidates' rematches):

1. **The hoard never strikes.** `wharf` against `batchfront_keep` (`c54ffb6b…`, turns 57 to 63, 102 to 118 at home, `waiting`), `bight` against `batchfront_keep` (`e455f1aa…`, turns 30 to 71, 67 to 113, no `pounce>` line all game), `far-shores` against `ori_like` (`7ca89f6a…`, turns 56 to 73, 132 to 235). The diagnosis (a log of the cheapest failed strike): the castles holding it are 7 to 13 turns from every enemy castle, beyond `punishWalk` (6); `threat` cut nothing.
2. **The batches an enemy castle has walking in are invisible.** `bayou` against `ori_like` (`8fc75a34…`), turns 55 to 61: castle 7 bought production and speed (32 to 4) while three groups of 12 walked in to castle 8 (8, then 32), which struck it with 28. `wharf`: castles at 5 soldiers fed trains of 12. **Cause:** `enemySpare` reads an enemy castle's stock only.
3. **Help and upgrades spend a castle that enemy groups are already walking at.** `bight` turns 72 to 77 (castle 0 from 73 to 6 in help to castle 4, then struck); `breakwater` against `punisher` (`d45bda30…`), turns 21 to 26. In the code, `safeOut` already plays every landing; the gap is only where our own help offsets an enemy group.
4. **`fullfeed_unfreeze`'s new rule counts one turn of growth too many.** `circle` against `punisher` (`5922b563…`), turn 12: `production4@0 unfrozen` took 32 to 6 against a group of 25 landing on turn 17; `coversLandings` counted 26, the castle held 22; a castle produces nothing on the turn it buys. `speedhelp_landlate` drew the game.
5. **`batchfront_keep` strikes while its own castles are short.** `islands` against `speedhelp_landlate` (`509cbbe4…`), turns 63 to 66; `fjord` against `sameturn_endreserve` (`bba36fca…`), turn 61; iteration 40's `haven` game, turn 52.
6. Also seen, not given a place: `pounce` loses `haven` as team 1 to every `ori` bot on the same turns (51 to 58): its home sent 13 at a castle of 2, and 24, 13 and 1 from three castles took it; the captured castles ping-pong with garrisons of 2 to 8 (castle 5 nine times). `ori` bots spend a border castle on neutrals and harassment beside a stocked `batchfront` castle (`strait` turns 30 and 41 to 52).

| Candidate | Parent | Idea | Against parent | Training (parent's) | Better, worse on training (margin, maps, by luck) | Against the references (parent's) | Holdout | Decision |
|---|---|---|---|---|---|---|---|---|
| `pounce_massthreat` | pounce | Fix: the threat to a castle counts each enemy castle's soldiers with its own side's groups walking in to it that land within six turns (`mass>`). (`threat` was already a sum over enemy castles. Rematch: `bayou` turn 32, a production level not bought, loss → win; `wharf` turn 43, loss → loss; the two `haven` games never acted.) | 31/64 | 2049 (2085) | 34, 80 (−46; 8 better, 11 worse; 4.2%): clearly worse | 99.5 (103) | not played | **rejected**: clearly worse on training |
| `pounce_inbound` | pounce | Fix: what a castle may send is also capped by what the enemy groups walking at it alone would take, its own inbound help not counted (`inbound>`). (Rematch: `bight` turn 79, no 1-soldier help, loss → loss; `bayou` turn 42, castle 9 kept 4, loss → win; `breakwater` never acted.) | 32/64 | 2080 (2085) | 15, 22 (−7; 6 better, 10 worse; 25.8%): worse | 100 (103) | 5, 2 (+3, 50%): nothing; all maps −1 | **rejected**: not confirmed on holdout, and no margin on all maps |
| `pounce_strikes` | pounce | Fix: a strike may land up to 10 turns out, not 6 (`punishWalk`), since its price already counts the target's growth and the help that lands by then; the cheapest failed strike is logged (`nostrike>`). (Rematch: `wharf` turn 42, loss → loss; `bight` turn 30, loss → win; `far-shores` turn 28, loss → win.) | 33.5/64 | 2031 (2085) | 85, 158 (−73; 10 better, 16 worse; 3.1%): clearly worse | 91 (103) | not played | **rejected**: clearly worse on training, and 12 points fewer against the references |
| `unfreeze_margin` | fullfeed_unfreeze | Fix: `coversLandings` counts no growth on the turn of the purchase. (Rematch: both `circle` seats, turn 12, `saving`, loss → draw; `shingle` turn 67, win → win sooner; `inlet` unchanged.) | 32/64 | 2007 (2013) | 4, 14 (−10; 2 better, 5 worse; 18.0%): clearly worse | 106.5 (106.5) | not played | **rejected**: clearly worse on training; plays alike its parent (88%) |
| `keep_nostrike` | batchfront_keep | Fix: no strike planned or launched while `reinforce` reports a castle short (`nostrike`). (Rematch: `islands` turn 38, `fjord` turn 63, `haven` turn 28 (as `batchfront`); losses → losses at the limit.) | 21.5/64 | 1968 (2003) | 69, 96 (−27; 8 better, 16 worse; 14.2%): clearly worse | 83 (94) | not played | **rejected**: clearly worse on training |

The gate: `scripts/check.sh` passes; `iteration-41-parents` and `iteration-41-candidates` (5,120 matches, 4,783 played in 205 s) exit 0 with no failed turn; slowest turns 15.6 to 25.2 ms. The selection: `iteration-41-select` (all cached); `iteration-41-select-holdout` for `pounce_inbound` (1,220 played in 58 s) and `iteration-41-select-all`.

**Status changes:** the five candidates deleted. The population is iteration 40's. `iteration-41-after` lists no bots that play alike.

Training maps (`iteration-41-train`, 5,632 matches, exit 0):

| Player | Rating | Score | W | D | L | Failed turns | Slowest turn (ms) |
|---|---|---|---|---|---|---|---|
| pounce | 2134 | 0.788 | 635 | 41 | 156 | 0 | 19.3 |
| punisher | 2124 | 0.779 | 632 | 32 | 168 | 0 | 23.7 |
| fullfeed_unfreeze | 2055 | 0.709 | 540 | 100 | 192 | 0 | 17.1 |
| speedhelp_landlate | 2040 | 0.693 | 533 | 87 | 212 | 0 | 20.7 |
| batchfront_keep | 1985 | 0.632 | 500 | 52 | 280 | 0 | 15.2 |
| harrier_feedkeep | 1984 | 0.631 | 469 | 112 | 251 | 0 | 28.0 |
| growtrickle_feedkeep | 1949 | 0.593 | 442 | 102 | 288 | 0 | 18.2 |
| sameturn_endreserve | 1935 | 0.577 | 414 | 132 | 286 | 0 | 21.8 |
| batchfront | 1906 | 0.546 | 432 | 44 | 356 | 0 | 26.6 |
| ori_mimic | 1800 | 0.436 | 305 | 116 | 411 | 0 | 22.8 |
| ori_like | 1673 | 0.328 | 261 | 24 | 547 | 0 | 17.8 |
| level1 | 1439 | 0.060 | 0 | 84 | 620 | 0 | 10.7 |
| level3 | 1065 | 0.007 | 5 | 0 | 699 | 0 | 10.1 |
| level2 | 838 | 0.001 | 1 | 0 | 703 | 0 | 10.0 |

Holdout maps (`iteration-41-holdout`, 5,456 matches, exit 0):

| Player | Rating | Score | W | D | L | Failed turns | Slowest turn (ms) |
|---|---|---|---|---|---|---|---|
| pounce | 2076 | 0.751 | 591 | 29 | 186 | 0 | 54.1 |
| punisher | 2062 | 0.737 | 577 | 34 | 195 | 0 | 15.4 |
| batchfront_keep | 2043 | 0.717 | 560 | 35 | 211 | 0 | 11.9 |
| speedhelp_landlate | 2007 | 0.678 | 511 | 71 | 224 | 0 | 17.5 |
| fullfeed_unfreeze | 2006 | 0.676 | 515 | 60 | 231 | 0 | 20.3 |
| harrier_feedkeep | 1964 | 0.630 | 460 | 96 | 250 | 0 | 37.9 |
| growtrickle_feedkeep | 1958 | 0.623 | 453 | 99 | 254 | 0 | 18.0 |
| batchfront | 1927 | 0.588 | 459 | 30 | 317 | 0 | 16.1 |
| sameturn_endreserve | 1888 | 0.545 | 382 | 115 | 309 | 0 | 22.7 |
| ori_mimic | 1800 | 0.453 | 308 | 115 | 383 | 0 | 19.7 |
| ori_like | 1652 | 0.328 | 264 | 0 | 542 | 0 | 24.6 |
| level1 | 1379 | 0.047 | 0 | 64 | 618 | 0 | 11.6 |
| level3 | 918 | 0.003 | 2 | 0 | 680 | 0 | 13.6 |
| level2 | 637 | 0.000 | 0 | 0 | 682 | 0 | 18.3 |

**Champion:** `pounce`, unchanged: **2134** on training (iteration 40: 2132 on 31 maps) and **2076** on holdout (2073 on 29). Against the references: 103 of 128 on training (`ori_mimic` 56, `ori_like` 47), 89 of 124 on holdout (54, 35). Its weakest pairing: `batchfront_keep`, 23.5 of 64 on training and 19 of 62 on holdout; then `batchfront`, 27 and 20.

**Where it still loses:** to the `batchfront` line and `ori_like`, the bots that keep no reserve and feed one front; its soldiers stand far from every enemy castle. **The next iteration starts with** the champion's place: where its soldiers stand. It has no front; a graft of a front (rear castles feeding the castle nearest the enemy, as both side lines do) is a graft, not a fix of its pricing, and the three fixes of its pricing this iteration all failed. `ori` and `batchfront` each have one iteration of work without a promotion: a second closes them.

**Ideas not tried:**
- `pounce` captures castles it can't hold (`haven`, castle 5 changing hands nine times with garrisons of 2 to 8): a strike should also pay the garrison the enemy's spare would take back.
- `pounce` sends help in pieces sized to each turn's shortfall (`wharf` turns 47 to 56, ten groups of 4 to 19 into castle 6, which fell): help once in one group or not at all.
- `pounce`'s neutral takes with senders landing apart (`bayou` turn 59, 20 and 17 landing two turns apart; the enemy took the weakened neutral).
- `batchfront_keep` expands late: a second castle at production 1 pays no neutral (`islands` turns 10 to 34).
- `batchfront_keep`'s keep ignores groups walking in to an enemy castle (`fjord` turn 61, about 100 at castle 9).
- The `ori` line's harassment and upgrades drain a castle beside a stocked enemy castle (`strait` turns 36 to 52).
- The ideas of iteration 40's list stand.

### The league itself

- **The champion takes fewer points from the references than the one it replaced** (second iteration): 103 of 128 on training against `speedhelp_landlate`'s 118 in the same table (`ori_mimic` 61, `ori_like` 57), and 89 of 124 on holdout against 114.5. Raised in iteration 40 with a proposed change of the main-line rule; still open, and the hosted bot runs `pounce` once iteration 40 merges.
- **The champion has no line of its own**, so its lost points are all against other lines, for the first time since iteration 24. The field's variety is better than it was; its weakest pairings are both of one side line.
- **Three fixes of one bot's pricing failed together.** Each acted in its games and turned losses there into wins (`bayou`, `bight`, `far-shores`), and each was worse against the field. Rematches on a finding's games keep pointing one way and the field the other, as in iterations 37 and 39: the selection is doing its job.
- **Who teaches nothing.** `level2` and `level3` win 1 and 5 games, `level1` only draws (sixth iteration).
- **Iteration 40 is not merged.** Iteration 41 was claimed on its branch; until a person merges iteration 40 (it changes the champion, see its review), every later iteration stacks on it.

**Time** (`league clock report`): 0 ledger 0.3 min, 1 measure 0.4, 2 study 4.2, 3 vary 2.9, 4 gate 3.8, 5 select 1.9, 6 record 0.8; 14.3 minutes in all, 17:41:30 to 17:55:46 UTC (iteration 40: 19.8). **Where it went:** playing about 5.5 minutes (the gate's 4,783 matches in 205 s, the holdout selection's 1,220 in 58 s); thinking the rest: eight studies at once on Sonnet (17:43:24 to 17:45:15, the longest 1.9 minutes), five writers at once (17:46:07 to 17:48:55, the longest `pounce_strikes` at 2.8 minutes with its diagnosis). **What was different:** no founder, whose inner loop was iteration 40's longest piece; the fixes started the moment their findings were in, before the last study finished. **To change:** *the next iteration:* the gate run is now the largest share (3.8 minutes, 4,783 matches); every candidate's head-to-head was already played, so nothing more can be cached. *A tool:* the gate's whole-field run could be started per candidate as each writer finishes (they are independent), so that it overlaps the writing of the others; today it waits for the last writer.

## Setup after iteration 41: the game at v1.7.0, and the official maps as the game serves them

**Date:** 2026-11-23. A change of the league's setup, made between iterations; no bot changed, and no iteration ran.

**What changed.**
- **`runner.toml`** moves from `d6e86b3` to `3f1503e` (the game's `v1.7.0`). For the runner this brings INTODAN/island-battles-go#425 (a turn that runs out of time is measured from when its timeout starts, never a little under it) and #419 (the game's own checks now play real Python and Go workers through the runner, and its README says how to build it from outside, as `league_tools/engine.py` already does). The rules of a headless game don't change: every holdout match, replayed at the new pin with no cache, ended as in iteration 41's table, win for win.
- **The bots' Go SDK** moves from `v1.5.0` to `v1.7.0`, and the tools' Python SDK from 1.5.0 to 1.7.0. Their new pieces (a game-end callback with a demo link, late batches that join the open turn in real-time games, `island-battles-bot match`) don't touch a headless game; the runner sends workers no game-end line. The copied rules skills are copied again at the new commit (a late order is played in the turn open when it arrives).
- **Official maps come from the game** (INTODAN/island-battles-go#390, #423; this repository's #3): `uv run league official-maps` saves each default map for two teams that `GET /map/templates/{id}` serves. `claw` is the served file now; it is the same map as the one rebuilt from a demo (only its name, `Claw`, and the upgrades it states at level 1 differ). **`star-of-david-duo`** (13 castles, 24 by 24, six neutral castles of 20 with burst 2 and a centre castle of 40 that produces 2) is new, in training. The game's two maps for three and four teams wait for #1. The hosted bot's page now names a known map by its file, so the served `Claw` still shows as `claw`.

**Standings.** The training set grew by one map, so its ratings moved with no bot changed.

Training maps (`setup-after-41-train`, 5,808 matches, exit 0):

| Player | Rating | Score | W | D | L | Failed turns | Slowest turn (ms) |
|---|---|---|---|---|---|---|---|
| pounce | 2137 | 0.791 | 658 | 41 | 159 | 0 | 45.9 |
| punisher | 2128 | 0.782 | 655 | 32 | 171 | 0 | 72.1 |
| fullfeed_unfreeze | 2056 | 0.710 | 559 | 100 | 199 | 0 | 52.7 |
| speedhelp_landlate | 2041 | 0.694 | 552 | 87 | 219 | 0 | 43.8 |
| harrier_feedkeep | 1982 | 0.629 | 484 | 112 | 262 | 0 | 40.8 |
| batchfront_keep | 1980 | 0.627 | 512 | 52 | 294 | 0 | 37.9 |
| growtrickle_feedkeep | 1952 | 0.597 | 461 | 102 | 295 | 0 | 43.2 |
| sameturn_endreserve | 1933 | 0.576 | 427 | 134 | 297 | 0 | 44.1 |
| batchfront | 1901 | 0.541 | 442 | 44 | 372 | 0 | 62.6 |
| ori_mimic | 1800 | 0.437 | 316 | 118 | 424 | 0 | 60.7 |
| ori_like | 1672 | 0.328 | 269 | 24 | 565 | 0 | 34.6 |
| level1 | 1440 | 0.061 | 0 | 88 | 638 | 0 | 29.7 |
| level3 | 1059 | 0.007 | 5 | 0 | 721 | 0 | 50.7 |
| level2 | 831 | 0.001 | 1 | 0 | 725 | 0 | 18.7 |

Holdout maps (`setup-after-41-holdout`, 5,456 matches, exit 0):

| Player | Rating | Score | W | D | L | Failed turns | Slowest turn (ms) |
|---|---|---|---|---|---|---|---|
| pounce | 2076 | 0.751 | 591 | 29 | 186 | 0 | 36.1 |
| punisher | 2062 | 0.737 | 577 | 34 | 195 | 0 | 23.0 |
| batchfront_keep | 2043 | 0.717 | 560 | 35 | 211 | 0 | 18.2 |
| speedhelp_landlate | 2007 | 0.678 | 511 | 71 | 224 | 0 | 41.6 |
| fullfeed_unfreeze | 2006 | 0.676 | 515 | 60 | 231 | 0 | 18.9 |
| harrier_feedkeep | 1964 | 0.630 | 460 | 96 | 250 | 0 | 37.2 |
| growtrickle_feedkeep | 1958 | 0.623 | 453 | 99 | 254 | 0 | 19.6 |
| batchfront | 1927 | 0.588 | 459 | 30 | 317 | 0 | 22.9 |
| sameturn_endreserve | 1888 | 0.545 | 382 | 115 | 309 | 0 | 26.3 |
| ori_mimic | 1800 | 0.453 | 308 | 115 | 383 | 0 | 24.4 |
| ori_like | 1652 | 0.328 | 264 | 0 | 542 | 0 | 32.7 |
| level1 | 1379 | 0.047 | 0 | 64 | 618 | 0 | 19.6 |
| level3 | 918 | 0.003 | 2 | 0 | 680 | 0 | 11.7 |
| level2 | 637 | 0.000 | 0 | 0 | 682 | 0 | 13.7 |

**Champion:** `pounce`, unchanged: **2137** on training (iteration 41: 2134 on 32 maps) and **2076** on holdout (unchanged). On `star-of-david-duo` it takes 23 of 26, as `punisher` does; `ori_mimic` takes 12.

**Not verified.** The slowest turns on training (up to 72 ms) are higher than in iteration 41 because the league's checks ran on the same machine during the tournament; no turn came near the 200 ms gate. Runs that started from main before this change measured at the old pin; since no headless result changed, their numbers still hold, but a match cached under the old runner's hash is played again at the new one.

**Time:** the two tournaments took 4.5 and 4.3 minutes; the whole change about 40 minutes, most of it reading the game's pull requests.

## Iteration 42: run 20261123-13f1e2, nothing promoted

Run: ledger/runs/20261123-13f1e2.md

Integrated on 2026-11-23 by `league integrate`, from the run's base `042cbce387bc`. Maps the run added: holdout/foreland, holdout/tombolo, train/backshore. Real games it studied: none.

### Decisions

| Candidate | Parent | Idea | Against parent | Training (parent's) | Better, worse on training (margin, maps, by luck) | Against the references (parent's) | Holdout | All maps | Decision |
|---|---|---|---|---|---|---|---|---|---|
| `pounce_front` | pounce | Graft from batchfront_keep: rear castles feed what they can spare above pounce's reserve to the front, the own castle nearest the enemy, in batches of 12 or more, never while an enemy group is bound for them. | 35/68 | 2186 (2142) | 107, 69 (+38; 16 maps better, 9 worse; 5.7%): confirmed | 107 (111) | not played | not played | **rejected**: over 3 points fewer than pounce against the references (107 to 111) |

### The population's upkeep

- delete `pounce_front`: rejected: over 3 points fewer than pounce against the references (107 to 111)

The champion stays `pounce`.

### Standings on the training maps

| Player | Rating | Score | Wins | Draws | Losses |
|---|---|---|---|---|---|
| `pounce` | 2149 | 0.797 | 684 | 41 | 159 |
| `punisher` | 2134 | 0.783 | 676 | 32 | 176 |
| `fullfeed_unfreeze` | 2065 | 0.714 | 581 | 100 | 203 |
| `speedhelp_landlate` | 2048 | 0.696 | 572 | 87 | 225 |
| `harrier_feedkeep` | 1986 | 0.629 | 500 | 112 | 272 |
| `batchfront_keep` | 1984 | 0.627 | 528 | 52 | 304 |
| `growtrickle_feedkeep` | 1954 | 0.594 | 474 | 102 | 308 |
| `sameturn_endreserve` | 1940 | 0.578 | 443 | 136 | 305 |
| `batchfront` | 1900 | 0.535 | 451 | 44 | 389 |
| `ori_mimic` | 1800 | 0.433 | 323 | 120 | 441 |
| `ori_like` | 1671 | 0.325 | 275 | 24 | 585 |
| `level1` | 1446 | 0.061 | 0 | 92 | 656 |
| `level3` | 1056 | 0.007 | 5 | 0 | 743 |
| `level2` | 828 | 0.001 | 1 | 0 | 747 |

### Standings on the holdout maps

| Player | Rating | Score | Wins | Draws | Losses |
|---|---|---|---|---|---|
| `pounce` | 2072 | 0.748 | 627 | 29 | 202 |
| `punisher` | 2057 | 0.732 | 611 | 34 | 213 |
| `batchfront_keep` | 2047 | 0.721 | 601 | 35 | 222 |
| `fullfeed_unfreeze` | 2015 | 0.686 | 559 | 60 | 239 |
| `speedhelp_landlate` | 2007 | 0.678 | 546 | 71 | 241 |
| `harrier_feedkeep` | 1963 | 0.629 | 492 | 96 | 270 |
| `growtrickle_feedkeep` | 1953 | 0.617 | 480 | 99 | 279 |
| `batchfront` | 1928 | 0.590 | 491 | 30 | 337 |
| `sameturn_endreserve` | 1890 | 0.547 | 412 | 115 | 331 |
| `ori_mimic` | 1800 | 0.454 | 332 | 115 | 411 |
| `ori_like` | 1650 | 0.328 | 281 | 0 | 577 |
| `level1` | 1367 | 0.044 | 0 | 64 | 662 |
| `level3` | 907 | 0.003 | 2 | 0 | 724 |
| `level2` | 626 | 0.000 | 0 | 0 | 726 |

## Iteration 43: run 20261123-1c1bd6, promoted landgrab, pounce_reach

Run: ledger/runs/20261123-1c1bd6.md

Integrated on 2026-11-23 by `league integrate`, from the run's base `042cbce387bc`. Maps the run added: holdout/levee, holdout/marsh, train/tarn. Real games it studied: none.

### Decisions

| Candidate | Parent | Idea | Against parent | Training (parent's) | Better, worse on training (margin, maps, by luck) | Against the references (parent's) | Holdout | All maps | Decision |
|---|---|---|---|---|---|---|---|---|---|
| `keep_inbound` | batchfront_keep | Fix: keep() counts at an enemy castle the enemy groups walking to it that land within the keep's horizon: gyre turns 63 to 67 (castle 0 sent 20 to the front while 12-soldier batches walked to enemy castle 4, which then took castle 0) and fjord turn 61 (about 100 at castle 9). | 31/70 | 2018 (2007) | 82, 59 (+23; 13 maps better, 14 worse; 15.2%): confirmed | 104 (104) | 67, 64 (+3; 16 maps better, 11 worse; 45.9%): nothing | 133, 123 (+10; 28 maps better, 25 worse; 37.1%): nothing | **unresolved**: a margin above 0 on all maps, short of the rule: nothing on the holdout maps and nothing on all maps |
| `landgrab` | pounce | Founder: land first: every castle takes the neutrals that pay back soonest before it buys any production level, the nearest two or three castles paying each together, and attacks only as one strike from every castle landing on one enemy castle on the same turn. | against the champion: 42/70 | 1949 (2098) | — | 82 (115) | not played | not played | **admitted**: a third of the points or more from the champion (42/70), and plays alike no bot of the league |
| `pounce_helperkeep` | pounce | Fix: a castle that is the only one whose help lands in time at a thin own castle beside a stocked enemy castle keeps that castle's shortfall when it upgrades or pays a neutral; haven turn 20 (production bought by the only helper of castles 3 and 5), breakwater turn 41 (castle 1 paid a far neutral and castle 3 fell on 44), wharf turn 68. | 37.5/70 | 2111 (2098) | 22, 7 (+15; 4 maps better, 2 worse; 25.0%): nothing | 117 (115) | 6, 7 (-1; 1 maps better, 3 worse; 50.0%): worse | 26, 13 (+13; 5 maps better, 5 worse; 25.0%): nothing | **unresolved**: a margin above 0 on all maps, short of the rule: worse on the holdout maps and nothing on all maps |
| `pounce_reach` | pounce | Fix: from turn 60, while no group of ours walks at an enemy castle and we hold more soldiers than the enemy, strikes may walk as far as the finishing window allows instead of only six turns: bight, castles 0 and 4 held up to 974 and 894 from turn 31 to 269 with every enemy castle 7.4 to 7.8 away, a 5-to-1 win at the limit instead of an elimination. | 33/70 | 2104 (2098) | 26, 10 (+16; 11 maps better, 4 worse; 6.8%): confirmed | 117.5 (115) | 46, 15 (+31; 10 maps better, 5 worse; 4.8%): clear | 64, 22 (+42; 17 maps better, 9 worse; 1.7%): clear | **promoted**: confirmed on the holdout maps and clear on all maps against pounce |
| `pounce_wholehelp` | pounce | Fix: help is sent only when what lands in time covers the whole shortfall, and speed is bought for help only then; otherwise the helpers keep their soldiers: haven turn 23, wharf turn 71 (speed bought, castle fell anyway, castle 2 then got 4 a turn), breakwater turns 49 to 61 and cairn turns 42 to 48 (groups of 3 or 4 a turn eaten in clashes). | 38/70 | not played | not played | not played | not played | not played | **needs_review**: 1 failed turns in the head-to-head run: fix it or drop it, or play the run again if a turn ran out of time while the machine was busy |
| `unfreeze_pairreserve` | fullfeed_unfreeze | Fix: a feed leaves the feeding castle what the two strongest enemy castles that could land on it within a few turns of each other could land together, not only the strongest one: cairn turns 41 to 54 (castle 1 fed down to 4 to 6 three times, then 8 and 39 landed together from castles 4 and 5). | 31.5/70 | 1997 (2017) | 78, 115 (-37; 10 maps better, 16 worse; 5.3%): clearly worse | 115.5 (117.5) | not played | not played | **rejected**: clearly worse than fullfeed_unfreeze on the training maps |

Left undecided by the rules and deleted, for a run to write again: pounce_wholehelp.

### The population's upkeep

- delete `keep_inbound`: unresolved: a margin above 0 on all maps, short of the rule: nothing on the holdout maps and nothing on all maps
- `landgrab` becomes active: admitted: a third of the points or more from the champion (42/70), and plays alike no bot of the league; the first bot of a side line
- delete `pounce_helperkeep`: unresolved: a margin above 0 on all maps, short of the rule: worse on the holdout maps and nothing on all maps
- `pounce_reach` becomes active: promoted: confirmed on the holdout maps and clear on all maps against pounce
- NEEDS REVIEW: pounce_wholehelp: left a candidate, needs_review: 1 failed turns in the head-to-head run: fix it or drop it, or play the run again if a turn ran out of time while the machine was busy
- delete `unfreeze_pairreserve`: rejected: clearly worse than fullfeed_unfreeze on the training maps
- `pounce_reach` is the champion: promoted from the head pounce of `pounce`
- `fullfeed_unfreeze` becomes retired: `ori` is closed: two iterations of work in a row without a promotion (iteration 43); its head becomes a fixed opponent
- delete `speedhelp_landlate`: `ori` is closed: two iterations of work in a row without a promotion (iteration 43)
- delete `harrier_feedkeep`: `ori` is closed: two iterations of work in a row without a promotion (iteration 43)
- delete `growtrickle_feedkeep`: `ori` is closed: two iterations of work in a row without a promotion (iteration 43)
- delete `sameturn_endreserve`: `ori` is closed: two iterations of work in a row without a promotion (iteration 43)
- `batchfront_keep` becomes retired: `batchfront` is closed: two iterations of work in a row without a promotion (iteration 43); its head becomes a fixed opponent
- delete `batchfront`: `batchfront` is closed: two iterations of work in a row without a promotion (iteration 43)

**The champion is now `pounce_reach`**, was `pounce`.

### Standings on the training maps

| Player | Rating | Score | Wins | Draws | Losses |
|---|---|---|---|---|---|
| `pounce_reach` | 2051 | 0.751 | 488 | 76 | 136 |
| `pounce` | 2046 | 0.746 | 483 | 79 | 138 |
| `batchfront_keep` | 2015 | 0.714 | 487 | 26 | 187 |
| `punisher` | 2004 | 0.703 | 475 | 34 | 191 |
| `fullfeed_unfreeze` | 1995 | 0.694 | 467 | 37 | 196 |
| `landgrab` | 1942 | 0.637 | 423 | 46 | 231 |
| `ori_mimic` | 1800 | 0.491 | 305 | 78 | 317 |
| `ori_like` | 1723 | 0.423 | 287 | 18 | 395 |
| `level1` | 1364 | 0.041 | 0 | 46 | 514 |
| `level3` | 1103 | 0.009 | 5 | 0 | 555 |
| `level2` | 684 | 0.000 | 0 | 0 | 560 |

### Standings on the holdout maps

| Player | Rating | Score | Wins | Draws | Losses |
|---|---|---|---|---|---|
| `batchfront_keep` | 2085 | 0.788 | 542 | 19 | 139 |
| `pounce_reach` | 2043 | 0.746 | 492 | 60 | 148 |
| `pounce` | 2031 | 0.734 | 481 | 65 | 154 |
| `punisher` | 1967 | 0.666 | 459 | 15 | 226 |
| `fullfeed_unfreeze` | 1955 | 0.653 | 446 | 22 | 232 |
| `landgrab` | 1925 | 0.621 | 415 | 39 | 246 |
| `ori_mimic` | 1800 | 0.491 | 312 | 64 | 324 |
| `ori_like` | 1774 | 0.467 | 327 | 0 | 373 |
| `level1` | 1319 | 0.030 | 0 | 34 | 526 |
| `level3` | 1142 | 0.011 | 6 | 0 | 554 |
| `level2` | 886 | 0.002 | 1 | 0 | 559 |

## Iteration 44: run 20261123-627ceb, nothing promoted

Run: ledger/runs/20261123-627ceb.md

Integrated on 2026-11-23 by `league integrate`, from the run's base `042cbce387bc`. Maps the run added: holdout/rcflats, holdout/rcmarsh, train/rcbluff. Real games it studied: none.

### Decisions

| Candidate | Parent | Idea | Against parent | Training (parent's) | Better, worse on training (margin, maps, by luck) | Against the references (parent's) | Holdout | All maps | Decision |
|---|---|---|---|---|---|---|---|---|---|
| `pounce_forward` | pounce | Fix: a castle whose threat exceeds what it holds, and that no helper could reach before the enemy castles that threaten it, is topped up now from the castles that land soonest, before the enemy sends. | 30/72 | 1982 (2047) | 57, 124 (-67; 4 maps better, 23 worse; under 0.1%): clearly worse | 108 (119) | not played | not played | **rejected**: clearly worse than pounce on the training maps |
| `pounce_nearwalk` | pounce | Fix: a neutral castle is taken only by senders whose walk is at most punishWalk turns, unless the game is finishing. | 48/72 | 2130 (2047) | 160, 98 (+62; 22 maps better, 9 worse; 3.4%): clear | 124 (119) | 109, 116 (-7; 17 maps better, 13 worse; 41.0%): worse | 250, 200 (+50; 35 maps better, 23 worse; 11.0%): confirmed | **unresolved**: a margin above 0 on all maps, short of the rule: worse on the holdout maps and confirmed on all maps |
| `pounce_sharedhold` | pounce (judged against pounce_reach) | Fix: an upgrade or a neutral take may spend a castle below its own threat when the other castles' spare that lands before the enemy's covers the rest. | 58/72; against pounce_reach: 57/72 | 2191 (2050) | 181, 44 (+137; 29 maps better, 4 worse; under 0.1%): clear | 116 (121.5) | not played | not played | **superseded**: passes against its parent pounce, not against its line's head pounce_reach: over 3 points fewer than pounce_reach against the references (116 to 121.5) |
| `pounce_together` | pounce | Fix: a strike's and a neutral take's senders land within one turn of each other: a sender that would land earlier waits, so the target meets them in one landing. | 35/72 | 2061 (2047) | 87, 74 (+13; 17 maps better, 10 worse; 28.4%): nothing | 123 (119) | 84, 69 (+15; 17 maps better, 11 worse; 24.5%): nothing | 160, 131 (+29; 34 maps better, 22 worse; 14.6%): confirmed | **unresolved**: a margin above 0 on all maps, short of the rule: nothing on the holdout maps and confirmed on all maps |

### The population's upkeep

- delete `pounce_forward`: rejected: clearly worse than pounce on the training maps
- delete `pounce_nearwalk`: unresolved: a margin above 0 on all maps, short of the rule: worse on the holdout maps and confirmed on all maps
- delete `pounce_sharedhold`: superseded: passes against its parent pounce, not against its line's head pounce_reach: over 3 points fewer than pounce_reach against the references (116 to 121.5)
- delete `pounce_together`: unresolved: a margin above 0 on all maps, short of the rule: nothing on the holdout maps and confirmed on all maps

The champion stays `pounce_reach`.

### Standings on the training maps

| Player | Rating | Score | Wins | Draws | Losses |
|---|---|---|---|---|---|
| `pounce_reach` | 2047 | 0.754 | 504 | 78 | 138 |
| `pounce` | 2045 | 0.752 | 501 | 81 | 138 |
| `batchfront_keep` | 2002 | 0.708 | 497 | 26 | 197 |
| `punisher` | 1997 | 0.703 | 489 | 34 | 197 |
| `fullfeed_unfreeze` | 1991 | 0.697 | 483 | 37 | 200 |
| `landgrab` | 1926 | 0.626 | 428 | 46 | 246 |
| `ori_mimic` | 1800 | 0.497 | 319 | 78 | 323 |
| `ori_like` | 1712 | 0.418 | 292 | 18 | 410 |
| `level1` | 1352 | 0.040 | 0 | 46 | 530 |
| `level3` | 1145 | 0.012 | 7 | 0 | 569 |
| `level2` | 952 | 0.003 | 2 | 0 | 574 |

### Standings on the holdout maps

| Player | Rating | Score | Wins | Draws | Losses |
|---|---|---|---|---|---|
| `batchfront_keep` | 2067 | 0.775 | 564 | 19 | 157 |
| `pounce_reach` | 2043 | 0.751 | 524 | 64 | 152 |
| `pounce` | 2029 | 0.737 | 511 | 69 | 160 |
| `punisher` | 1962 | 0.666 | 485 | 15 | 240 |
| `fullfeed_unfreeze` | 1952 | 0.655 | 474 | 22 | 244 |
| `landgrab` | 1922 | 0.622 | 441 | 39 | 260 |
| `ori_mimic` | 1800 | 0.496 | 334 | 66 | 340 |
| `ori_like` | 1766 | 0.464 | 343 | 0 | 397 |
| `level1` | 1315 | 0.030 | 0 | 36 | 556 |
| `level3` | 1128 | 0.010 | 6 | 0 | 586 |
| `level2` | 871 | 0.002 | 1 | 0 | 591 |

## Iteration 45: run 20261123-8bf2a7, promoted burstguard

Run: ledger/runs/20261123-8bf2a7.md

Integrated on 2026-11-23 by `league integrate`, from the run's base `042cbce387bc`. Maps the run added: holdout/marram, holdout/sedge, train/fenwick. Real games it studied: none.

### Decisions

| Candidate | Parent | Idea | Against parent | Training (parent's) | Better, worse on training (margin, maps, by luck) | Against the references (parent's) | Holdout | All maps | Decision |
|---|---|---|---|---|---|---|---|---|---|
| `burstguard` | pounce | Founder: castles past production 4 buy burst levels before speed; no standing reserve against the enemy's spare: a castle keeps what the strongest enemy castle within 4 turns could land less its growth and its burst, and a castle a landing would take this turn bursts to hold. | against the champion: 53/74 | 2061 (2031) | — | 114 (125.5) | not played | not played | **admitted**: a third of the points or more from the champion (53/74), and plays alike no bot of the league |

### The population's upkeep

- `burstguard` becomes active: admitted: a third of the points or more from the champion (53/74), and plays alike no bot of the league; the first bot of a side line
- `burstguard` is the champion: the head of the side line `burstguard` rates above pounce_reach on the training maps (2061 to 2031), not below it on the holdout maps, and takes at least half the points from it: the main line changes

**The champion is now `burstguard`**, was `pounce_reach`.

### Standings on the training maps

| Player | Rating | Score | Wins | Draws | Losses |
|---|---|---|---|---|---|
| `burstguard` | 2061 | 0.745 | 583 | 47 | 184 |
| `pounce_reach` | 2031 | 0.714 | 536 | 90 | 188 |
| `pounce` | 2028 | 0.711 | 533 | 91 | 190 |
| `batchfront_keep` | 2004 | 0.685 | 543 | 29 | 242 |
| `punisher` | 1997 | 0.677 | 532 | 38 | 244 |
| `fullfeed_unfreeze` | 1988 | 0.666 | 523 | 39 | 252 |
| `landgrab` | 1935 | 0.608 | 466 | 58 | 290 |
| `ori_mimic` | 1800 | 0.466 | 340 | 78 | 396 |
| `ori_like` | 1737 | 0.408 | 321 | 22 | 471 |
| `level1` | 1344 | 0.035 | 0 | 46 | 620 |
| `level3` | 1199 | 0.015 | 10 | 0 | 656 |
| `level2` | 1114 | 0.009 | 6 | 0 | 660 |

### Standings on the holdout maps

| Player | Rating | Score | Wins | Draws | Losses |
|---|---|---|---|---|---|
| `burstguard` | 2097 | 0.770 | 629 | 64 | 165 |
| `batchfront_keep` | 2089 | 0.763 | 639 | 31 | 188 |
| `pounce_reach` | 2038 | 0.710 | 565 | 88 | 205 |
| `pounce` | 2027 | 0.698 | 552 | 93 | 213 |
| `punisher` | 1968 | 0.633 | 534 | 19 | 305 |
| `fullfeed_unfreeze` | 1950 | 0.614 | 512 | 30 | 316 |
| `landgrab` | 1939 | 0.602 | 481 | 71 | 306 |
| `ori_mimic` | 1800 | 0.458 | 356 | 74 | 428 |
| `ori_like` | 1786 | 0.445 | 382 | 0 | 476 |
| `level1` | 1324 | 0.028 | 0 | 40 | 662 |
| `level3` | 1120 | 0.009 | 6 | 0 | 696 |
| `level2` | 1011 | 0.004 | 3 | 0 | 699 |
