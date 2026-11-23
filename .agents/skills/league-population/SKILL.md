---
name: league-population
description: "Who is in the bot league and why: the lines (a strategy and the bots descended from its founder) and the ledger's table of them, the main line and the side lines that are protected while they still improve, exploiters and the other fixed opponents, the rule that only one of two bots that play alike stays, the caps, and how to read the population's variety from a tournament. Load it at the start of a league iteration, before admitting, promoting, retiring or deleting a bot, and when the league has stopped improving."
---

# Who is in the league

A bot is measured by its games against the others, so the population is the league's measuring stick as well as its stock of parents. This skill keeps both varied. What an iteration tries is in [`league-ideas`](../league-ideas/SKILL.md), what a result may decide in [`league-evidence`](../league-evidence/SKILL.md), the sources in [`league-breeding`](../league-breeding/SKILL.md).

## Why

After 36 iterations, measured on the training maps:

- **One line.** Every active bot descended from one founder, and shared 91% to 99% of its code with the champion. In 35 of 36 iterations every candidate had the same parent.
- **Copies.** Twelve pairs of bots ended more than half of their games the same to the soldier; `exact_stallfeed` and `ori_hold_exact` 88% of them. The league's fifteen bots played like about six.
- **A stick made of what it measures.** 71% of the champion's games were against its own line and `ori_mimic`, the sparring bot the line began from, and 132.5 of the 141.5 points it lost. 88% of the games inside the line ran to the turn limit, and 39% were drawn. Its lost games, which every iteration studied, were mirror games.
- **New strategies died at birth.** A founder had to beat the champion's line by the rule made for a small fix: 10 of 14 were deleted in the iteration that wrote them, three of those rated above their parent, the champion, on the training maps.

Replacing a bot only by a better copy of itself climbs the hill it stands on and never finds another. A new strategy needs time to be tuned before it meets the best, and somewhere to live meanwhile.

## The parts

- **A line** is a founder and every bot descended from it: one strategy. The ledger's table **The lines**, above its lessons, names each line, its strategy in a sentence, its head and its state.
- **A bot's line** is its parent's (`bot.toml`), with two exceptions that the first words of its idea mark: a `Founder:` begins a line of its own, and an `Exploiter` belongs to none. Sparring bots belong to none. The bots made before these rules are in the lines the table gives them.
- **The main line** is the champion's. **A side line** is any other line with an active bot. A line's **head** and the **champion** are defined in [`league-evidence`](../league-evidence/SKILL.md): the champion is the main line's head, and the ledger names it.
- **Fixed opponents** are the `retired` bots: the old heads, the heads of closed lines, the exploiters. They play every tournament and never change.
- **The references** are the sparring bots and the outside opponents: what the league is measured against, and never selected. The default bots play too, and decide nothing.

## One of two bots that play alike stays

A whole round robin prints **Bots that play alike**: pairs that ended at least half of their games against the same opponent, on the same map and from the same seat, the same to the soldier. Such a pair is one bot counted twice: it doubles its weight in every rating, doubles the games that say the same thing, and adds no parent worth choosing.

Take the table of the training maps, in its order, the most alike first. Of each pair in which both bots are still there, one **leaves**: `uv run league delete NAME`. Which one:

- **The champion, the sparring bots and the outside opponents never leave.** When one of the pair is one of them, the other leaves; a pair of two such is left as it is.
- **A bot promoted in this iteration that plays alike its parent replaces it:** the parent leaves, whichever rates higher. If the parent was its line's head or the champion, the promoted bot now is.
- **Otherwise the bot that takes fewer points from the champion head to head leaves**, the lower-rated when they take the same. Its status and its line don't matter: a retired bot can stay and an active one leave, and two bots promoted from one parent that play alike end as one.

Then **measure again** (from the cache), since a bot that left changes what the others have in common, and repeat until the table lists no pair but pairs of bots that never leave.

Do this twice an iteration: after the first measurement, so that the candidates are measured against a field without copies, and after the promotions, on the population as it then is.

When a line's last active bot leaves this way, the line is closed, and its row says why.

## Side lines

- **A founder that is admitted** ([`league-evidence`](../league-evidence/SKILL.md)) starts a side line: `league status NAME active`, and a row in **The lines**.
- **A side line gets a candidate every iteration** ([`league-ideas`](../league-ideas/SKILL.md), the slate): a fix from its head's own lost games, or a graft from the main line. Its candidates are selected like any fix or graft, against their own parent. They never have to beat the champion.
- **It is closed after two iterations of work in a row without a promotion.** An iteration of work, for a line, is one in which the line had a candidate, whatever became of it. The iteration that admitted its founder is not one, and an iteration in which the slate had no place for the line neither counts nor breaks the row. Its row in **The lines** keeps the count. Closed: its head becomes `retired`, its other bots are deleted, and its row says **closed**, with what the line showed. A line that still improves stays, however far below the champion.
- **At most two side lines.** A free place is filled by the next founder; a founder is never written while both are taken.
- **When the main line changes** ([`league-evidence`](../league-evidence/SKILL.md), The champion), the old main line is a side line under the same rule, its count at 0.
- **A closed line may be founded again**, from its head's code, when a game shows what it lacked. Say in the new row what is different.

## Fixed opponents

- **An exploiter that is admitted** becomes `retired` at once. It is there to be beaten: the main line's next findings come from its games.
- **A parent that its promoted child doesn't play alike** stays active; the caps say who is retired when the line then has more than three.
- **At most eight.** Over that, delete the one that takes the fewest points from the active bots together (the pair table): an opponent that every active bot beats everywhere teaches nothing. Sparring bots don't count among them and are never deleted.

## Caps

- **At most three active bots in a line.** Over that, retire the line's lowest-rated active bot that is not its head.
- **At most two side lines and eight fixed opponents**, as above.

## Reading the variety

Each iteration, from the first measurement, note in the ledger:

- the pairs that play alike, and who left;
- the share of the champion's games, and of its lost points, that are against its own line (the pair table's row);
- the champion's **weakest pairing**, and the player outside its line that takes the most points from it;
- the lines, with each side line's iterations of work without a promotion.

**When no player outside the main line takes a third of the points from the champion**, the league has stopped testing it: the slate gets an exploiter ([`league-ideas`](../league-ideas/SKILL.md)).

## Never

- Delete or change a sparring bot, or change an active or retired bot's code.
- Keep a bot because it once was the champion. What it takes from today's bots is what it is kept for.
- Close a side line that promoted something in its last iteration of work, or ask its bots to beat the champion in order to stay. Only the rule for bots that play alike compares them with anyone but their parent.
