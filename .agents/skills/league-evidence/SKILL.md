---
name: league-evidence
description: "What a tournament's numbers may decide in the bot league: the table of a candidate's games next to its parent's (better, worse, the same), the margins that make a result clear, confirmed or nothing, the rules that promote a fix, a graft or a simplification and admit a founder or an exploiter, who the champion is, the maps every iteration adds, and what a rating can't say. Load it before selecting candidates in a league iteration, before saying that one bot is better than another, and before changing the selection rules."
---

# What a result may decide

A league iteration keeps a bot only on what a tournament showed. This skill says how much a tournament can show, and the rule for each kind of candidate. The kinds are in [`league-ideas`](../league-ideas/SKILL.md), the lines and the population in [`league-population`](../league-population/SKILL.md), the sources in [`league-breeding`](../league-breeding/SKILL.md).

## Why the rules have margins

Until iteration 36 a candidate was promoted when it had more than half the points against its parent, rated above it and didn't rate below it on the holdout maps, each by any amount. Measured afterwards:

- **38 games, a head-to-head on 19 maps, separate bots about 110 rating points apart.** Two equal bots give any score from 13 to 25 of 38. Of 119 head-to-heads, 48 ended within a point of half, and 13 of the 28 promotions had a head-to-head within 2.5 points of half.
- **Some promotions were noise.** In the field of iteration 36, `harrier_attackers` (promoted on 19.5 of 38 and one rating point) did better than its parent in 10 games against the others and worse in 9, with 589 the same. Of the twelve parent-to-child steps still in the population, four show no gain on the training maps, and two of those a loss.
- **A holdout set that is asked every iteration stops being held out.** Its maps, fifteen by then, had been asked about some forty candidates, and rejected two of the last by 11 and 12 rating points.

## The paired table

Bots are deterministic. A game that the candidate's change never touched ends as its parent's did, and says nothing. The evidence is the games that ended otherwise.

Every round robin of the whole population that lists a bot with its parent (`tournament --add`) prints **Each listed bot against its parent**, and in it:

- **Its games against the others, next to the parent's**: for each opponent, map and seat that both met, whether the bot did **better** than its parent, **worse** or **the same**. Their games against each other are not in it.
- **Of them, draws told apart by production**: a draw is not the end of what a game says. When both drew, the bot did better if it out-produced its opponent over the game and its parent didn't, or its parent was out-produced and it wasn't. In the drawn games in which one side led, that side was the higher-rated bot 85% of the time, more often than the winner of a game decided at the turn limit. The soldiers held at the end say nothing: the bot that never strikes ends with the most.
- **Margin**: better minus worse.
- **Maps**: on how many maps its margin was above 0, and on how many below.
- **By luck**: the chance that a change which does nothing gives a margin this far from 0, **a map's games counted as one**. A map's games move together (the same castles, the same race for them), so what was drawn is the map, not the game. Had the change done nothing, each map's margin could as well have come out with the other sign; the column is the share of all those ways that reach the margin played. It is exact, and it can't be small on few maps: six maps all one way give one in 64.

A result is:

- **worse** when the margin is below 0, and **clearly worse** when by luck is then 20% or less;
- **confirmed** when the margin is above 0 and by luck is 20% or less, one time in five;
- **clear** when the margin is above 0 and by luck is 5% or less, one time in twenty;
- **nothing** otherwise. With no game changed there is no result at all: the candidate plays as its parent does.

From iteration 37's field, on the 29 training maps:

| Bot | Better, worse | Margin | Maps | By luck | It says |
|---|---|---|---|---|---|
| `harrier_front` | 212, 72 | +140 | 17 better, 4 worse | 0.2% | clear |
| `stallfeed_growtrickle` | 50, 17 | +33 | 14 better, 3 worse | under 0.1% | clear |
| `exact_stallfeed` | 31, 13 | +18 | 4 better, 3 worse | 15.6% | confirmed |
| `harrier_attackers` | 20, 13 | +7 | 6 better, 4 worse | 20.9% | nothing |
| `harrier_feedkeep` | 125, 111 | +14 | 12 better, 10 worse | 39.2% | nothing |
| `ori_hold_exact` | 64, 66 | -2 | 11 better, 6 worse | 48.6% | worse |

**Count the maps, not the games.** On the holdout maps `growtrickle_feedkeep` did better than its parent in 144 games and worse in 75. Counted as 219 separate games that would be one chance in several hundred thousand. They came from 25 maps, of which six went the other way: luck gives such a margin one time in twelve. The games of a map are one draw between them, and the first version of these rules, which counted games, overstated what it knew about threefold.

**Two sets of maps together** are one more run, on all of them: `--maps all --add CANDIDATES`. It prints the same table over both sets, and lists no games, since holdout maps are in it.

## A fix or a graft

Three steps, each cheaper than the next, and each drops only what it can judge. The fractions are the rule; the numbers in brackets are for 30 training maps, two games a map.

1. **Head to head against its parent** (`--focus CANDIDATES --parents`): **rejected with a third of the points or fewer** (20 of 60 or fewer). Above that the head-to-head decides nothing.
2. **The training maps** (`--add CANDIDATES`): **rejected when it is worse** (a margin below 0), or when its points against the **references** (the sparring bots and the outside opponents, added up from the pair table, the parent itself left out when it is one of them) are **more than three below its parent's**. A fix that doesn't come out ahead on the maps it was read from has nothing going for it, and a bot that gains against its own line and loses to the references has learned its line.
3. **The holdout maps, and all maps** (`--maps holdout --add CANDIDATES`, then `--maps all --add CANDIDATES`, for the candidates that passed step 2): **promoted when it is confirmed on the holdout maps and clear on all maps together.**

The past promotions, as iteration 37's field has them on 29 training and 25 holdout maps:

- `harrier_front`: 39 of 58 against its parent; +140 on training, 102.5 points against the references to its parent's 97; +82 on holdout at 0.8%, so confirmed; +222 on all maps at under 0.1%, so clear. **Promoted.**
- `feedkeep_speedhelp`, promoted by the old rule on 22 of 38 and one rating point: +14 on training; +39 on holdout at 10.8%, confirmed; +53 on all maps at 10.6%, not clear. **Unresolved.**
- `harrier_feedkeep`: +14 on training, +15 on holdout at 38%, not confirmed. **Unresolved.**
- `ori_hold_exact`: -2 on training. **Rejected** there.

Of the thirteen promotions still in the league, four pass, each at under 0.1% on all maps; none of the other nine is below 7%.

A candidate that fails is rejected and deleted (`uv run league delete NAME`). **Never promote on a chance that falls short by a little**, and never change a candidate after its holdout run.

**Unresolved is not refuted.** A candidate whose margin was above 0 on both sets and short of the rule is recorded in the ledger as **unresolved**, with its numbers. Its idea may be written again once the two sets together hold five more maps than they did, and that try is not counted among the idea's three (below).

## A simplification

A candidate that only removes a mechanism, or a special case of one, is promoted when it has more than a third of the points against its parent, is **not clearly worse** on the training maps nor on all maps together, and its `main.go` has fewer lines than its parent's. A bot that plays as well with less code is easier to read, faster, and easier to graft from.

## A founder and an exploiter

A new strategy is not better than a line with thirty iterations in it, and is not asked to be. Both are **admitted**, by the training maps alone:

- **A founder** is admitted when it passes the gate, takes **a third of the points or more from the champion** head to head (20 of 60 or more), and plays alike no bot of the league in the select run's table **Bots that play alike** (another candidate doesn't count). It becomes `active`, the first bot of a side line.
- **An exploiter** is admitted when it passes the gate and takes **three fifths of the points or more from the champion** (36 of 60 or more). It becomes `retired`: a fixed opponent.

Its games against the champion, with the games it didn't win listed:

```sh
uv run league tournament --bots NAME,CHAMPION --focus NAME --anchors '' --no-opponents --strict --run-id iteration-N-NAME-champion
```

Read its points in that run's pair table. **The points that decide are those of the code as it goes to the gate**: run the command once more after the last revision.

Neither plays the holdout maps to be admitted: admission claims nothing about strength, and every question asked of the holdout maps wears them out. Its rating is recorded, not judged, and so is its row in the tables against the bot whose code it started from: that bot is not its measure.

## The champion

- **A line's head** is its top-rated active bot on the training maps, except that a bot promoted from the head is the head from then on, whatever the two ratings say.
- **The champion is the main line's head.** The ledger's last entry names it; step 1's table only confirms that it is still there.
- **The main line changes** only when a side line's head, in the iteration's final tables, rates above the champion on the training maps, rates not below it on the holdout maps, and has at least half the points against it head to head (the pair table). Until then the champion stays, and the ledger says that the side line leads on training.

## Maps

- **Every iteration adds two holdout maps and a training map**, before the first measurement: `uv run league new-map NAME --seed S --set holdout` twice, and once with `--set train`, with seeds the iteration's number times 100 plus 1, 2 and 3, and names of lower-case letters and digits. No bot was ever selected on them, so part of every confirmation is on maps that no earlier choice has touched, and every iteration can see a little more than the last.
- **Holdout games are never read**, and a candidate is never changed after its holdout run.
- **An idea gets three tries in a line.** After three rejections of one mechanism, in whatever form, it is closed for that line until a real game shows something new. Trying again until one passes is how luck gets promoted.

## What the league can resolve

With 54 maps, the four past promotions that were large (a margin of 58 to 343 games over all maps) are beyond doubt, and a step the size of the champion's over its parent, 53 games, is not: luck gives it one time in ten. So a small fix of a mature line will often end unresolved. That is the measure telling the truth, not a fault to work around: the answer is more maps, more opponents unlike each other, and candidates that change more.

## What a rating can't say

- **A rating counts every opponent once.** A bot's rating rises with the number of copies of the bots it beats. In iteration 36, 71% of the champion's games were against its own line and the sparring bot the line began from. Read the paired table and the points against the references before the rating.
- **A difference of two ratings has about twice the error of one.** "Nine points above its parent" is not a result.
- **Ratings compare within one table**: the same players, the same maps. Never across a `--focus` run, and across iterations only through `ori_mimic`. When bots leave or maps are added, every rating moves with no bot changed.
- **A candidate chosen because it scored well scored partly by luck**, so its next measurement is usually lower. `harrier_feedkeep` did better than its parent by 69 games on the 34 maps it was chosen on, and worse by 40 on the twenty maps added afterwards. The new maps of every iteration are that second measurement. Report a promoted bot's numbers on them, not only the training ones.
- **Several candidates are several chances for luck.** The clear margin is set for three to six a round.

## Record

For every candidate the ledger keeps its points against its parent, its better and worse games on the training maps and on the holdout maps, its points against the references next to its parent's, and the rule that decided. For the champion, each iteration: its points against the references, and its **weakest pairing** (the opponent that takes the most points from it). A champion whose rating rises while its weakest pairing falls is forgetting something.
