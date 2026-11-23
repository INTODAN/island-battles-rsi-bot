---
name: league-evidence
description: "What a tournament's numbers may decide in the bot league: the table of a candidate's games next to its parent's (better, worse, the same), the margins that make a result clear, confirmed or nothing, the rules that promote a fix, a graft or a simplification and admit a founder or an exploiter, who the champion is, the maps every iteration adds, and what a rating can't say. Load it before selecting candidates in a league iteration, before saying that one bot is better than another, and before changing the selection rules."
---

# What a result may decide

A league iteration keeps a bot only on what a tournament showed. This skill says how much a tournament can show, and the rule for each kind of candidate. The kinds are in [`league-ideas`](../league-ideas/SKILL.md), the lines and the population in [`league-population`](../league-population/SKILL.md), the sources in [`league-breeding`](../league-breeding/SKILL.md).

## Why the rules have margins

Until iteration 36 a candidate was promoted when it had more than half the points against its parent, rated above it and didn't rate below it on the holdout maps, each by any amount. Measured afterwards:

- **38 games separate bots about 110 rating points apart.** Two equal bots give any score from 13 to 25 of 38. Of 119 head-to-heads, 48 ended within a point of half, and 13 of the 28 promotions had a head-to-head within 2.5 points of half.
- **Some promotions were noise.** In the field of iteration 36, `harrier_attackers` (promoted on 19.5 of 38 and one rating point) did better than its parent in 10 games against the others and worse in 9, with 589 the same. Of the twelve parent-to-child steps still in the population, four show no gain on the training maps, and two of those a loss.
- **A holdout set that is asked every iteration stops being held out.** Its maps, fifteen by then, had been asked about some forty candidates, and rejected two of the last by 11 and 12 rating points.

## The paired table

Bots are deterministic. A game that the candidate's change never touched ends as its parent's did, and says nothing. The evidence is the games that ended otherwise.

Every round robin of the whole population that lists a bot with its parent (`tournament --add`) prints **Each listed bot against its parent**, and in it **Its games against the others, next to the parent's**: for each opponent, map and seat that both met, whether the bot did **better** than its parent, **worse** or **the same**. Their games against each other are not in it. The next column, **Margin, noise**, is computed from those:

- the **margin** is better minus worse;
- the **noise** is the root of better plus worse: what the margin of a change that does nothing typically comes to.

A result is:

- **worse** when the margin is below 0, and **clearly worse** when it is below minus the noise;
- **confirmed** when the margin is at least the noise and at least 3;
- **clear** when the margin is at least twice the noise and at least 6;
- **nothing** otherwise. With no game changed, there is no result at all: the candidate plays as its parent does.

| Better, worse | Margin, noise | It says |
|---|---|---|
| 0, 0 | +0, 0.0 | nothing: its parent's copy |
| 10, 9 | +1, 4.4 | nothing |
| 76, 74 | +2, 12.2 | nothing |
| 4, 0 | +4, 2.0 | confirmed, and too few games to be clear |
| 17, 10 | +7, 5.2 | confirmed |
| 30, 9 | +21, 6.2 | clear |
| 112, 44 | +68, 12.5 | clear |
| 18, 24 | -6, 6.5 | worse |
| 30, 53 | -23, 9.1 | clearly worse |

This is chess-engine testing's likelihood of superiority, counted on the games that changed: confirmed is about 5 chances in 6 that the candidate is better, clear about 49 in 50, if the games were independent. They are not: one map's games move together, and two opponents that play alike repeat each other. That is why promotion asks for clear, and why bots that play alike leave the league before anything is selected ([`league-population`](../league-population/SKILL.md)).

**Two sets of maps together** are their counts added: 77 better and 54 worse on the training maps with 61 and 32 on the holdout maps are 138 and 86, a margin of 52 against a noise of 15.0.

## A fix or a graft

Three steps, each cheaper than the next, and each drops only what it can judge. The fractions are the rule; the numbers in brackets are for 19 training maps, two games a map.

1. **Head to head against its parent** (`--focus CANDIDATES --parents`): **rejected with a third of the points or fewer** (12.5 of 38 or fewer). Above that the head-to-head decides nothing.
2. **The training maps** (`--add CANDIDATES`): **rejected when it is worse** (a margin below 0), or when its points against the **references** (the sparring bots and the outside opponents, added up from the pair table, the parent itself left out when it is one of them) are **more than three below its parent's**. A bot that gains against its own line and loses to the references has learned its line, and the real games are played against the references' kind.
3. **The holdout maps** (`--maps holdout --add CANDIDATES`, for the candidates that passed step 2): **promoted when it is confirmed there and clear on both sets together.**

`harrier_feedkeep`, as iteration 36's field has it: 23 of 38 against its parent; 77 better and 54 worse on training, 67 points against the references to its parent's 65.5; 61 and 32 on holdout, a margin of 29 against a noise of 9.6, so confirmed; together 52 against twice 15.0, so clear. Promoted.

A candidate that fails is rejected and deleted (`uv run league delete NAME`). **Never promote on a margin that falls short by a little**, and never change a candidate after its holdout run.

**Unresolved is not refuted.** A candidate whose margin was above 0 on both sets and short of the rule is recorded in the ledger as **unresolved**, with its numbers. Its idea may be written again once the two sets together hold five more maps than they did, and that try is not counted among the idea's three (below).

## A simplification

A candidate that only removes a mechanism, or a special case of one, is promoted when it has more than a third of the points against its parent, is **not clearly worse** on the training maps nor on the holdout maps, and its `main.go` has fewer lines than its parent's. A bot that plays as well with less code is easier to read, faster, and easier to graft from.

## A founder and an exploiter

A new strategy is not better than a line with thirty iterations in it, and is not asked to be. Both are **admitted**, by the training maps alone:

- **A founder** is admitted when it passes the gate, takes **a third of the points or more from the champion** head to head (13 of 38 or more), and plays alike no bot of the league in the select run's table **Bots that play alike** (another candidate doesn't count). It becomes `active`, the first bot of a side line.
- **An exploiter** is admitted when it passes the gate and takes **three fifths of the points or more from the champion** (23 of 38 or more). It becomes `retired`: a fixed opponent.

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

- **Every iteration adds two holdout maps and a training map**, before the first measurement: `uv run league new-map NAME --seed S --set holdout` twice, and once with `--set train`, with seeds the iteration's number times 100 plus 1, 2 and 3. No bot was ever selected on them, so part of every confirmation is on maps that no earlier choice has touched, and every iteration can see a little more than the last.
- **Holdout games are never read**, and a candidate is never changed after its holdout run.
- **An idea gets three tries in a line.** After three rejections of one mechanism, in whatever form, it is closed for that line until a real game shows something new. Trying again until one passes is how luck gets promoted.

## What the league can resolve

A change that alters a fifth of its parent's games and wins six in ten of those needs about 500 games next to the parent's to be clear. A candidate has two games a map against each opponent that isn't a copy of another: with six such opponents and 34 maps, about 400. So a small fix of a mature line will often end unresolved. That is the measure telling the truth, not a fault to work around: the answer is more maps, more opponents unlike each other, and candidates that change more.

## What a rating can't say

- **A rating counts every opponent once.** A bot's rating rises with the number of copies of the bots it beats. In iteration 36, 71% of the champion's games were against its own line and the sparring bot the line began from. Read the paired table and the points against the references before the rating.
- **A difference of two ratings has about twice the error of one.** "Nine points above its parent" is not a result.
- **Ratings compare within one table**: the same players, the same maps. Never across a `--focus` run, and across iterations only through `ori_mimic`. When bots leave or maps are added, every rating moves with no bot changed.
- **A candidate chosen because it scored well scored partly by luck**, so its next measurement is usually lower. The holdout maps are that second measurement. Report the holdout numbers of a promoted bot, not only the training ones.
- **Several candidates are several chances for luck.** The clear margin is set for three to six a round.

## Record

For every candidate the ledger keeps its points against its parent, its better and worse games on the training maps and on the holdout maps, its points against the references next to its parent's, and the rule that decided. For the champion, each iteration: its points against the references, and its **weakest pairing** (the opponent that takes the most points from it). A champion whose rating rises while its weakest pairing falls is forgetting something.
