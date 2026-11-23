---
name: league-ideas
description: "What a league iteration tries: the slate of candidates and the places in it that explore, which bot each candidate starts from, the five kinds (fix, graft, simplification, founder, exploiter) and how each is written and checked before the gate, which games to study besides the champion's losses to its own line, and what to do when nothing is promoted. Load it before choosing the games to study and before writing candidates in a league iteration."
---

# What an iteration tries

An iteration has three to six candidates. This skill spends them. Who they join is in [`league-population`](../league-population/SKILL.md), how they are judged in [`league-evidence`](../league-evidence/SKILL.md), the sources in [`league-breeding`](../league-breeding/SKILL.md).

## Why

What 36 iterations and 119 candidates showed:

- **Fixes of the champion run dry.** Fixes passed 18 times in 94, grafts 6 in 11, founders 4 in 14 although each had to beat the champion at once. A promoted candidate gained about 90 rating points over its parent in iterations 1 to 10, and about 25 in iterations 26 to 35, where the largest gain (80) was a founder's.
- **One parent is one hill.** Iterations 14 to 24 took 42 candidates from `safe_hold` and promoted one. The next step up came from a founder on other code.
- **The step changes came from outside the line**: a founder written from a real game's winner (iteration 7), founders on the real opponent's rules (25), a founder that attacks a habit of those rules (34).
- **The champion's lost games were mirror games**: nine tenths of the points it lost, it lost to its own line. A fix read from them makes the line better at beating itself.

## The slate

Decide the slate after the first measurement and before any game is studied: the games to read follow from it. It has as many places as the iteration has candidates: three, or six when subagents write them. Fill it in this order until it is full:

1. **One candidate for each side line**, from its head.
2. **An exploiter**, when no player outside the main line takes a third of the points from the champion (the pair table of the first measurement).
3. **A founder**, for each free place among the two side lines.
4. **The main line**: fixes, grafts, a simplification.

**One place is always the main line's**, even when 1 to 3 would fill the slate: then the last of them waits. An exploiter that waited last iteration doesn't wait again: this time the main line's place is the one that gives way.

**A stalled main line** is one in which nothing was promoted in the last two iterations. Its place may hold a graft, a simplification, or a fix of a game the champion lost to a player outside its line (the pair table says whether there is one), and never a fix of a game inside the line. Any further place it would have had goes to an exploiter aimed at another habit of the champion's.

| Side lines | A slate of three | A slate of six |
|---|---|---|
| none | exploiter if due, else a second founder; a founder; main line | exploiter if due; two founders; main line in the rest |
| one | its candidate; exploiter if due, else a founder; main line | its candidate; exploiter if due; a founder; main line in the rest |
| two | their two candidates; main line | their two candidates; exploiter if due; main line in the rest |

## Which bot a candidate starts from

- **A main line's candidate starts from its head**, unless the head's last three fixes, grafts and simplifications were all rejected: then from another active bot of the line, or it is a graft into the head or a simplification of it. A bot whose children keep failing has no small steps left. A promotion from the head starts the count again.
- **A side line's candidate starts from its head.**
- **A founder or an exploiter starts from whatever code suits it**: any bot of the league, a retired or sparring one too, or nearly nothing. Where git can be read (not in the automated iteration), a deleted bot as well: `git log --diff-filter=D --name-only -- bots/` finds it, `git show COMMIT^:bots/NAME/main.go` prints it. A bot deleted before iteration 37 is Python (`bot.py`): its strategy can be read there, and is written again in Go. `league new` needs a parent: name the bot whose code it starts from, and leave `parent` in `bot.toml` as the command wrote it, for a founder too: the tools read it.

## The kinds

Begin every idea with its kind: `Fix:`, `Graft from NAME:`, `Simplification:`, `Founder:`, `Exploiter of NAME:`. The ledger's candidate lines are then searchable by kind, and a bot's line can be read from its idea.

**Fix.** The smallest change that answers one finding. A finding seen in one game is a guess: find the same situation in three games on two maps (the digests, or `grep` the logs of the listed demos) or choose another. A real game counts as one of the three. A constant tuned inside the candidate on the training maps is part of the fix, as before.

**Graft.** A mechanism another bot has, copied in. Graft whenever two candidates were promoted from one parent, whenever a side line promoted something the main line lacks, and the other way round: the main line's defence into a side line is usually its cheapest gain.

**Simplification.** One mechanism removed, or one special case, so that `main.go` is shorter. Worth a place when a mechanism's log line shows it seldom acts, when a lesson says the situation it answered is gone, or when the head has grown by 100 lines since the last one. It is promoted by not being clearly worse ([`league-evidence`](../league-evidence/SKILL.md)).

**Founder.** A new strategy: it differs from every line in at least two of economy (what it buys and when), expansion (which neutrals and when), defence (what it keeps home) and attack (when, from where, how sized). A line's code with one mechanism added is a fix, whatever it is called. Where founders come from, the best first:

- a real game: what the winner did that no line does;
- a lesson that says what the real opponents reward and the league punishes (production before the front, waiting, the guarded upgrade);
- a rejected candidate that the ledger says rated above its parent, or did best of all against a reference: with its line's rule no longer in its way, it is a founder;
- the opposite of a premise of the main line: no front, no reserve, nothing bought before the first capture;
- a closed line, with what it lacked.

**Exploiter.** A bot whose only aim is to beat the champion. Read the champion's code and its logs in a few long wins for what it always or never does, and write the narrowest bot that punishes it. It may lose to everyone else.

## Founders and exploiters get an inner loop

A first draft of a strategy is its worst version. Before the gate, play the new bot against the champion ([`league-evidence`](../league-evidence/SKILL.md) has the command, which lists the games it didn't win), read two or three of them with `digest`, and revise: **up to three revisions**, on the training maps only, and then the command once more, since the points that decide are those of the code that goes to the gate. A subagent that writes a founder or an exploiter does this itself and reports the points after each revision. Fixes and grafts get no such loop: their check is the rematch, and their judge the selection.

## Which games to study

In this order, three to five findings as before:

1. **Real games** the request names.
2. **The champion's games against players outside its line**: side lines, exploiters, old lines' heads, sparring bots, outside opponents. Its lost and drawn games against them come first, and the pairing where its row is worst. `tournament --focus CHAMPION` lists only its twenty shortest; for its games against one player: `uv run league tournament --bots CHAMPION,NAME --focus CHAMPION --anchors '' --no-opponents`.
3. **Each side line's head**: its shortest losses, for that line's candidate.
4. **A long win** of the champion's.
5. **Games inside the champion's line**: at most half of the games studied, and none for a stalled line's fix.

For an exploiter, the games are the champion's wins: what it does every time is what can be punished.

## Ideas that wait, and ideas that are closed

- **A finding that got no place** goes in the ledger entry under **Ideas not tried**, with its game and turns. The next iteration reads them before it studies anything.
- **Before writing a candidate, search the ledger's candidate lines for its mechanism.** Rejected once: say what is different now. Rejected three times in the line: closed, until a real game shows something new.
- **An unresolved candidate** (a margin above 0 on all maps, and short of the rule) is not one of the three. Its idea may be written again when the map sets hold five more maps ([`league-evidence`](../league-evidence/SKILL.md)).
- **A candidate that changes fewer than ten games** of its parent's in the whole field (the paired table) was a rare mechanism. Say so in the ledger, so that nobody tunes it.

## When nothing is promoted

- **Once:** nothing changes. Most ideas fail.
- **Twice in a row in the main line:** it is stalled, and the slate above applies.
- **Four times in a row, with no side line alive:** the league needs new information more than new code. Say so in the report: a person can add real games, an outside opponent, or a sparring bot.
- **A side line** that promotes nothing twice is closed, and its place goes to a new founder. That is the method working.
