"""growtrickle_feedkeep: freed reserves strike, they don't feed.

Iteration 34, from stallfeed_growtrickle. Near the end a castle's reserve
counts only enemy castles that could land before the last generation, and
feeding sent everything above it to the front. On inlet (a new training map)
and bight, against six bots of the line, castles fed 920 to 940 soldiers to a
front that already held as many and struck nothing, and the emptied castles
were taken on turns 297 and 298 by an enemy that bought speed: 32 games lost on
castles at the limit. Iteration 32 stopped all feeding in the last 30 turns
(16.5 of 34). Here feeding, and the stalled castles' feeding, keep a castle's
reserve against every enemy castle at any turn; the freed reserve still pays
for strikes.

stallfeed_growtrickle's docstring follows.

stallfeed_growtrickle: a group the castle outgrows before it lands is no attack.

Iteration 30, from endreserve_stallfeed. An attacked castle (any enemy group
bound for it) buys nothing, pays for nothing and feeds nothing; level1's
groups of 1 kept the line on one castle for 300 turns on nine maps (18 draws).
Iteration 26 capped every attacked castle's spending at what its landings leave
(half against its parent) and iteration 28 lifted every rule from a castle its
landings wouldn't take (13 of 34). Here an enemy group counts only when it holds
more soldiers than the castle produces before it lands; a real strike still
freezes the castle's whole stock, as before. The log names the castles whose
enemy groups were all outgrown.

endreserve_stallfeed's docstring follows.

endreserve_stallfeed: sameturn_endreserve with the feeding of stalled castles.

Iteration 29, from sameturn_endreserve, a graft from sameturn_stallfeed (both
promoted from exact_sameturn in iteration 28). A castle behind the front whose
next upgrade it could pay but which would then be left to a single enemy
castle, not attacked, sends what it can spare above its reserve to the front
once that is FEED_AT or more. The log shows these sends as "stalled>".

sameturn_endreserve's docstring follows.

sameturn_endreserve: no reserve against an enemy castle that can't land before the end.

Iteration 28, from exact_sameturn. Games inside the line end in hoards: on
archipelago against ori_hold both sides held over 4,500 soldiers in six castles
on turn 300 and drew, because every castle kept a reserve against the strongest
enemy castle and so had nothing to strike with. A strike from a castle no enemy
can reach before the game ends risks nothing: here a castle's reserve and its
holds() check count only enemy castles whose group, sent now, would land before
the last generation is created. The log names the castles whose reserve this
lowered, with the soldiers it freed.

exact_sameturn's docstring follows.

exact_sameturn: help that lands on the turn of the capture still counts.

Iteration 27, from ori_hold_exact. Defence took only helpers whose group lands
before the landing that would take the castle. Groups land in id order, so a
helper landing on that same turn lands after the enemy's and retakes the castle
at once, with the castle's upgrades, if it brings what the castle lacked plus
one. On loch (against hold_exactstrike, turn 79) castle 0, 3 turns from castle 2
with 51 soldiers, could have covered the 30 it lacked, but the capture was also
3 turns away; castle 2 (production 2, 31 soldiers) fell on turn 81 and the game
was lost 14 turns later. Here a helper is in time when its walk is at most the
fall's turn. The log marks such help with "(same turn)".

ori_hold_exact's docstring follows.

ori_hold_exact: ori_hold with ori_finish's exact strikes.

Iteration 26, from ori_hold, a graft from ori_finish, which beats ori_hold 19.5
of 34 and draws it on most maps. When an attack's last group lands within
SHORT_WALK turns, or within FINISH_TURNS of the turn limit, an attack on an
enemy castle costs what the target will hold plus EXACT_EXTRA plus its burst
potential (if it can burst) instead of need(); half of what the other enemy
castles could bring is dropped for a short walk and kept near the turn limit.
Neutrals keep need(). The log marks an exact strike with "exact".

ori_hold's docstring follows.

ori_hold: the hosted bot's rules, and holding what it takes.

Iteration 25, from ori_mimic. The league's oldest lessons are about holding: a
castle taken with 1 soldier near the enemy falls unless another castle
reinforces it, and defence is about the landing that takes the castle. The
hosted bot retakes fresh captures within one to four turns, and ori_mimic's own
captures face the same. Two changes, everything else is ori_mimic's:

* Defence also takes help from castles that are themselves under attack, each
  sending at most what leaves it with a non-negative balance through every
  landing bound for it.
* hold(), run right after defend(): a neutral that one of this bot's groups is
  bound for, and that playing every landing in order would leave to the
  enemy, is sent the fewest soldiers that leave it ours after the last landing,
  from the nearest castle that can pay and lands no later than the first enemy
  group that would take it.

ori_mimic's docstring follows.

A sparring opponent that plays by the rules read off the hosted bot's games of 2026-11-22: ori_mimic.

Its rules come from 17 lobby games (1,437 turns) of the hosted bot's current
version against safe_hold, each command read off consecutive frames, and from
the 18 games of the version before it; a replay of every turn the hosted bot
played, through this bot, measured each rule: it makes the hosted bot's exact
commands on 75% of the current version's turns. One price runs through
them: need(x) = x + x // 10 + 3, what it sends to take a castle that will hold
x when its groups land.

0. Turn 1: production 2; then the cheapest neutral whose soldiers plus walk
   are at most the production-3 cost, or production 3; every spend leaves the
   castle safe against each enemy castle walking 1 unit a turn.
1. Defence: a castle that the groups bound for it would take is sent what it
   lacks plus one, from castles whose groups land before the fall.
2. Speed strikes: a castle buys its next speed level and strikes in the same
   turn when, with that speed, it can pay the strike and the strike at its
   current speed it can't, or costs SPEED_SAVING more than speed and strike.
   Against a last enemy castle it strikes with what will be there plus one.
3. Upgrades, production 2, 3, 4, then speed 2: bought on the first turn the
   castle has the soldiers, unless an enemy group is bound for it or one enemy
   castle could then take it at need(what it would find).
4. Attacks: the enemy castle with the smallest price, need(its soldiers when
   the last group lands) plus half of what the other enemy castles could bring
   before that, launched the first turn the castles nearest it can pay.
5. Neutrals, ranked by soldiers plus the shortest walk to them: priced like an
   attack, paid by up to four castles nearest first; a castle within
   SAVE_TURNS of its next upgrade doesn't help another castle pay.
6. Feeding: a castle at production 4 and speed 2 or more, not the front, not
   under attack, sends all its soldiers to the front once it has FEED_AT, if
   it is still safe with none.

Every send keeps the sender's reserve: the fewest soldiers with which no single
enemy castle could take it at need(what it would find).
"""

from math import ceil

from island_battles_client import (
    NEUTRAL_TEAM_COLOR,
    BotTurn,
    BotTurnResult,
    Castle,
    PublicGenerationCommand,
    SoldierGroup,
    UpgradeType,
    burst_potential,
    can_burst,
    logger,
    production,
    send_soldier_group,
    turn_result,
    upgrade_castle,
)

# need(x) = x + x // NEED_TENTH + NEED_FIXED: what it sends to take a castle that will hold x.
NEED_TENTH = 10
NEED_FIXED = 3
# Production and speed levels the upgrade rule buys up to, production first.
TOP_PRODUCTION = 4
TOP_SPEED = 2
# A fully upgraded castle behind the front sends all its soldiers there once it has this many.
FEED_AT = 10
# At most this many castles send to one target in a turn.
MOST_SENDERS = 4
# A castle that would fall is sent what it lacks plus this many.
DEFENCE_SPARE = 1
# A castle buys speed for a strike it could already pay when that saves more than this many.
SPEED_SAVING = 7
# A castle this many turns of production from its next upgrade doesn't help pay for a neutral.
SAVE_TURNS = 3
# On turn 1 every spend must hold against enemies walking this many units a turn.
FIRST_TURN_WALK = 1.0
# An attack landing within this many turns counts the target exactly.
SHORT_WALK = 5
# So does an attack landing within this many turns of the turn limit.
FINISH_TURNS = 30
# Soldiers added to an exact count of the target.
EXACT_EXTRA = 2
# Landing order of this turn's sends, after every group on the board.
LATER_ID = 1 << 40


def need(soldiers: int) -> int:
    """The soldiers it sends to take a castle that will hold this many when they land."""
    return soldiers + soldiers // NEED_TENTH + NEED_FIXED


class Board:
    """The turn's board, and what this turn's commands have spent so far."""

    def __init__(self, turn: BotTurn) -> None:
        """Read the board from the turn."""
        self.turn = turn
        self.team = turn.team_color
        self.castles = sorted(turn.generation.castles, key=lambda castle: castle.id)
        self.groups = sorted(turn.generation.soldier_groups, key=lambda group: group.id)
        self.own = [castle for castle in self.castles if castle.team_color == self.team]
        self.enemies = [castle for castle in self.castles if castle.team_color not in (self.team, NEUTRAL_TEAM_COLOR)]
        self.neutrals = [castle for castle in self.castles if castle.team_color == NEUTRAL_TEAM_COLOR]
        self.commands: list[PublicGenerationCommand] = []
        self.spent: dict[int, int] = {}
        self.bought: dict[tuple[int, UpgradeType], int] = {}
        # This turn's sends to each castle: (turns until it lands, soldiers).
        self.sent: dict[int, list[tuple[int, int]]] = {}

    def table(self, upgrade_type: UpgradeType, level: int) -> tuple[float, int] | None:
        """An upgrade level's value and cost, or None past the top."""
        for upgrade in self.turn.upgrades:
            if upgrade.type == upgrade_type:
                if level > upgrade.max_level:
                    return None
                for entry in upgrade.levels:
                    if entry.level == level:
                        return entry.value, entry.soldier_cost
        return None

    def level(self, castle: Castle, upgrade_type: UpgradeType) -> int:
        """The castle's level of an upgrade type, counting this turn's purchases."""
        return castle.upgrades[upgrade_type] + self.bought.get((castle.id, upgrade_type), 0)

    def rate(self, castle: Castle) -> int:
        """Soldiers the castle produces a turn, counting this turn's purchases."""
        entry = self.table(UpgradeType.generation_amount, self.level(castle, UpgradeType.generation_amount))
        return int(entry[0]) if entry else 1

    def speed_of(self, level: int) -> float:
        """Map units a turn at a speed level."""
        entry = self.table(UpgradeType.speed, level)
        return entry[0] if entry else 0.5

    def travel(self, origin: Castle, target: Castle) -> int:
        """Turns a group sent now from origin takes to land on target (with origin's speed this turn)."""
        level = (
            self.level(origin, UpgradeType.speed)
            if origin.team_color == self.team
            else origin.upgrades[UpgradeType.speed]
        )
        return max(1, ceil(origin.distance(target) / self.speed_of(level) - 1e-9))

    def arrival(self, group: SoldierGroup) -> int:
        """Turns until a group lands, if nothing stops it."""
        speed = self.speed_of(group.upgrades[UpgradeType.speed])
        return max(1, ceil(group.distance_left() / speed - 1e-9))

    def left(self, castle: Castle) -> int:
        """Soldiers the castle hasn't spent this turn."""
        return castle.soldiers - self.spent.get(castle.id, 0)

    def in_time(self, enemy: Castle, castle: Castle) -> bool:
        """Whether a group the enemy castle sends now at the castle lands before the game's last generation."""
        return self.travel(enemy, castle) < self.turn.max_generations - self.turn.turn_number

    def holds(self, castle: Castle, soldiers: int, rate: int) -> bool:
        """Whether no single enemy castle that could land in time could take the castle at need(what it would find)."""
        return all(
            enemy.soldiers <= need(soldiers + rate * self.travel(enemy, castle))
            for enemy in self.enemies
            if self.in_time(enemy, castle)
        )

    def reserve(self, castle: Castle, everyone: bool = False) -> int:
        """The fewest soldiers the castle keeps so that it holds (against enemy castles that land in time)."""
        rate = self.rate(castle)
        keep = 0
        for enemy in self.enemies:
            if not everyone and not self.in_time(enemy, castle):
                continue
            # The fewest soldiers x that need(x) covers the enemy castle's, less what grows while it walks.
            fewest = max(0, (enemy.soldiers - NEED_FIXED) * NEED_TENTH // (NEED_TENTH + 1) - 1)
            while need(fewest) < enemy.soldiers:
                fewest += 1
            keep = max(keep, fewest - rate * self.travel(enemy, castle))
        return keep

    def avail(self, castle: Castle) -> int:
        """Soldiers the castle can send this turn."""
        return max(0, self.left(castle) - self.reserve(castle))

    def targeted(self, castle: Castle) -> bool:
        """Whether an enemy group is bound for the castle."""
        return any(group.destination_castle_id == castle.id and group.team_color != self.team for group in self.groups)

    def attacked(self, castle: Castle) -> bool:
        """Whether an enemy group bound for the castle holds more than the castle produces before it lands."""
        rate = production(self.turn, castle)
        return any(
            group.destination_castle_id == castle.id
            and group.team_color != self.team
            and group.soldiers > rate * self.arrival(group)
            for group in self.groups
        )

    def send(self, origin: Castle, target: Castle, amount: int) -> None:
        """Send soldiers, counting them as spent."""
        self.commands.append(send_soldier_group(origin.id, target.id, amount))
        self.spent[origin.id] = self.spent.get(origin.id, 0) + amount
        self.sent.setdefault(target.id, []).append((self.travel(origin, target), amount))

    def buy(self, castle: Castle, upgrade_type: UpgradeType, cost: int) -> None:
        """Buy the castle's next level of an upgrade type."""
        self.commands.append(upgrade_castle(castle.id, upgrade_type))
        self.spent[castle.id] = self.spent.get(castle.id, 0) + cost
        self.bought[(castle.id, upgrade_type)] = self.bought.get((castle.id, upgrade_type), 0) + 1

    def senders(self, target: Castle) -> list[tuple[int, int, Castle]]:
        """The castles that can send to the target this turn, nearest first: (turns, id, castle)."""
        return sorted(
            (self.travel(castle, target), castle.id, castle)
            for castle in self.own
            if castle.id != target.id and self.avail(castle) >= 1 and not self.attacked(castle)
        )

    def safe_out(self, castle: Castle) -> int:
        """Soldiers an attacked castle can send now and still not fall to any landing bound for it."""
        events = sorted(
            (self.arrival(group), group.id, group.team_color == self.team, group.soldiers)
            for group in self.groups
            if group.destination_castle_id == castle.id
        )
        soldiers = self.left(castle)
        rate = production(self.turn, castle)
        lowest = soldiers
        now = 0
        for landing, _, friendly, size in events:
            soldiers += rate * (landing - now)
            now = landing
            soldiers += size if friendly else -size
            lowest = min(lowest, soldiers)
        return max(0, lowest)

    def give_of(self, castle: Castle) -> int:
        """Soldiers the castle can send to help: those available, and if attacked no more than it can spare."""
        if self.attacked(castle):
            return min(self.avail(castle), self.safe_out(castle))
        return self.avail(castle)

    def send_split(self, chosen: list[Castle], target: Castle, amount: int, helping: bool = False) -> list[str]:
        """Send amount from the chosen castles, nearest first: the farther ones send all, the nearest the rest."""
        parts = []
        remaining = amount
        for castle in reversed(chosen[1:]):
            room = self.give_of(castle) if helping else self.avail(castle)
            give = min(room, remaining - 1) if remaining > 1 else 0
            if give >= 1:
                self.send(castle, target, give)
                parts.append(f"{castle.id}:{give}")
                remaining -= give
        if remaining >= 1:
            self.send(chosen[0], target, remaining)
            parts.append(f"{chosen[0].id}:{remaining}")
        return parts

    def at_landing(self, target: Castle, turns: int) -> tuple[int, int]:
        """Who holds the target and with how many soldiers in this many turns, after the groups bound for it."""
        events = [
            (self.arrival(group), group.id, group.team_color, group.soldiers)
            for group in self.groups
            if group.destination_castle_id == target.id
        ]
        for index, (landing, amount) in enumerate(self.sent.get(target.id, [])):
            events.append((landing, LATER_ID + index, self.team, amount))
        owner = target.team_color
        soldiers = target.soldiers
        rate = production(self.turn, target) if owner != NEUTRAL_TEAM_COLOR else 0
        now = 0
        for landing, _, team, size in sorted(events):
            if landing > turns:
                break
            soldiers += rate * (landing - now)
            now = landing
            if team == owner:
                soldiers += size
            elif size > soldiers:
                owner = team
                soldiers = size - soldiers
                rate = 1
            else:
                soldiers -= size
        soldiers += rate * (turns - now)
        return owner, soldiers


def first_turn(board: Board) -> str:
    """Turn 1: production 2, then cheap neutrals or production 3. Returns the log note."""
    notes = []
    for castle in board.own:
        # The opening is for a castle that starts the game at production 1.
        if board.level(castle, UpgradeType.generation_amount) != 1:
            continue

        def safe(after: int, rate: int, castle: Castle = castle) -> bool:
            return all(
                enemy.soldiers < after + rate * ceil(castle.distance(enemy) / FIRST_TURN_WALK - 1e-9)
                for enemy in board.enemies
            )

        second = board.table(UpgradeType.generation_amount, 2)
        if second and board.left(castle) >= second[1]:
            board.buy(castle, UpgradeType.generation_amount, second[1])
            notes.append(f"production2@{castle.id}")
        third = board.table(UpgradeType.generation_amount, 3)
        third_cost = third[1] if third else 1 << 30
        while True:
            left = board.left(castle)
            options = []
            for neutral in board.neutrals:
                if neutral.id in board.sent:
                    continue
                walk = board.travel(castle, neutral)
                if left >= third_cost and neutral.soldiers + walk > third_cost:
                    continue
                price = need(neutral.soldiers)
                if price <= left and safe(left - price, 2):
                    options.append((neutral.soldiers + walk, walk, neutral.id, neutral, price))
            if options:
                _, _, _, neutral, price = min(options)
                board.send(castle, neutral, price)
                notes.append(f"take>{neutral.id} {castle.id}:{price}")
                continue
            if (
                board.level(castle, UpgradeType.generation_amount) == 2
                and left >= third_cost
                and safe(left - third_cost, 3)
            ):
                board.buy(castle, UpgradeType.generation_amount, third_cost)
                notes.append(f"production3@{castle.id}")
            break
    return " ".join(notes)


def defend(board: Board) -> str:
    """Send help to castles that the groups bound for them would take. Returns the log note."""
    notes = []
    for castle in board.own:
        events = sorted(
            (board.arrival(group), group.id, group.team_color == board.team, group.soldiers)
            for group in board.groups
            if group.destination_castle_id == castle.id
        )
        if not any(not friendly for _, _, friendly, _ in events):
            continue
        soldiers = board.left(castle)
        rate = production(board.turn, castle)
        now = 0
        lowest = 0
        fall = None
        for landing, _, friendly, size in events:
            soldiers += rate * (landing - now)
            now = landing
            soldiers += size if friendly else -size
            if soldiers < lowest:
                lowest = soldiers
                if fall is None:
                    fall = landing
        if fall is None:
            continue
        missing = -lowest + DEFENCE_SPARE
        helpers = sorted(
            (board.travel(other, castle), other.id, other)
            for other in board.own
            if other.id != castle.id and board.give_of(other) >= 1
        )
        helpers = [entry for entry in helpers if entry[0] <= fall]
        chosen = []
        total = 0
        for _, _, helper in helpers[:MOST_SENDERS]:
            chosen.append(helper)
            total += board.give_of(helper)
            if total >= missing:
                break
        if total < missing:
            continue
        late = " (same turn)" if max(board.travel(helper, castle) for helper in chosen) == fall else ""
        notes.append(f"help>{castle.id}{late} " + " ".join(board.send_split(chosen, castle, missing, helping=True)))
    return " ".join(notes)


def hold(board: Board) -> str:
    """Send what it takes to keep a neutral that an enemy group would retake. Returns the log note."""
    notes = []
    for target in board.neutrals:
        landings = sorted(
            [board.arrival(group) for group in board.groups if group.destination_castle_id == target.id]
            + [turns for turns, _ in board.sent.get(target.id, [])]
        )
        ours = (
            any(group.destination_castle_id == target.id and group.team_color == board.team for group in board.groups)
            or target.id in board.sent
        )
        enemy = any(
            group.destination_castle_id == target.id and group.team_color != board.team for group in board.groups
        )
        if not ours or not enemy:
            continue
        last = landings[-1]
        owner, _ = board.at_landing(target, last)
        if owner in (board.team, NEUTRAL_TEAM_COLOR):
            continue
        deadline = next(
            turns for turns in landings if board.at_landing(target, turns)[0] not in (board.team, NEUTRAL_TEAM_COLOR)
        )

        def holds_with(origin: Castle, amount: int, target: Castle = target, last: int = last) -> bool:
            turns = board.travel(origin, target)
            board.sent.setdefault(target.id, []).append((turns, amount))
            try:
                return board.at_landing(target, max(last, turns))[0] == board.team
            finally:
                board.sent[target.id].pop()

        for walk, _, origin in board.senders(target):
            if walk > deadline:
                break
            room = board.avail(origin)
            if room < 1 or not holds_with(origin, room):
                continue
            low, high = 1, room
            while low < high:
                middle = (low + high) // 2
                if holds_with(origin, middle):
                    high = middle
                else:
                    low = middle + 1
            board.send(origin, target, low)
            notes.append(f"hold>{target.id}:{origin.id}:{low}")
            break
    return " ".join(notes)


def is_exact(board: Board, turns: int) -> bool:
    """Whether a strike whose last group lands in this many turns counts the target exactly."""
    turn = board.turn
    return turns <= SHORT_WALK or turn.max_generations - turn.turn_number <= turns + FINISH_TURNS


def attack_price(board: Board, target: Castle, turns: int, neutral: bool = False) -> int:
    """What it sends at a castle it doesn't hold when its last group lands in this many turns (0: already won).

    Strikes on enemy castles count the target exactly when the walk is short or the game nearly over.
    """
    owner, soldiers = board.at_landing(target, turns)
    if owner == board.team:
        return 0
    turn = board.turn
    finish = turn.max_generations - turn.turn_number <= turns + FINISH_TURNS
    short = turns <= SHORT_WALK
    exact = not neutral and (finish or short)
    nearby = 0
    if not exact or finish or not short:
        for other in board.enemies:
            if other.id == target.id:
                continue
            walk = board.travel(other, target)
            if walk < turns:
                nearby += other.soldiers + production(turn, other) * (turns - walk)
    if exact:
        burst = burst_potential(turn, target) if can_burst(target) else 0
        return soldiers + EXACT_EXTRA + burst + nearby // 2
    return need(soldiers) + nearby // 2


def speed_strike(board: Board) -> str:
    """Buy a castle's next speed level and strike with it, when that is the cheaper way to pay. Returns the log note."""
    candidates = []
    for target in board.enemies:
        for walk, _, origin in board.senders(target):
            level = board.level(origin, UpgradeType.speed) + 1
            entry = board.table(UpgradeType.speed, level)
            if entry is None:
                continue
            speed, cost = entry
            price = attack_price(board, target, max(1, ceil(origin.distance(target) / speed - 1e-9)))
            if price < 1 or price + cost > board.avail(origin):
                continue
            plain = attack_price(board, target, walk)
            if 1 <= plain <= board.avail(origin) and price + cost > plain - SPEED_SAVING:
                continue
            candidates.append((price + cost, target.id, origin.id, target, origin, price, cost))
    if not candidates and len(board.enemies) == 1:
        candidates = last_castle_strikes(board, board.enemies[0])
    if not candidates:
        return ""
    _, _, _, target, origin, price, cost = min(candidates)
    if cost:
        board.buy(origin, UpgradeType.speed, cost)
    board.send(origin, target, price)
    return f"{'speed+' if cost else ''}strike>{target.id} {origin.id}:{price}"


def last_castle_strikes(board: Board, target: Castle) -> list[tuple[int, int, int, Castle, Castle, int, int]]:
    """Strikes at the enemy's last castle with what will be there plus one, when the full price is out of reach."""
    candidates = []
    for _, _, origin in board.senders(target):
        level = board.level(origin, UpgradeType.speed)
        for extra in (0, 1):
            entry = board.table(UpgradeType.speed, level + extra)
            if entry is None:
                continue
            speed, cost = entry[0], entry[1] if extra else 0
            turns = max(1, ceil(origin.distance(target) / speed - 1e-9))
            owner, soldiers = board.at_landing(target, turns)
            if owner == board.team:
                continue
            if soldiers + 1 + cost <= board.avail(origin) < attack_price(board, target, turns) + cost:
                candidates.append((soldiers + 1 + cost, target.id, origin.id, target, origin, soldiers + 1, cost))
    return candidates


def upgrade(board: Board, castle: Castle) -> str:
    """Buy the castle's next upgrades while it can and no single enemy castle could then take it."""
    if board.attacked(castle):
        return ""
    bought = []
    while True:
        production_level = board.level(castle, UpgradeType.generation_amount)
        speed_level = board.level(castle, UpgradeType.speed)
        if production_level < TOP_PRODUCTION:
            upgrade_type, level = UpgradeType.generation_amount, production_level + 1
        elif speed_level < TOP_SPEED:
            upgrade_type, level = UpgradeType.speed, speed_level + 1
        else:
            break
        entry = board.table(upgrade_type, level)
        if entry is None:
            break
        cost = entry[1]
        after = board.left(castle) - cost
        if after < 0:
            break
        rate = int(entry[0]) if upgrade_type == UpgradeType.generation_amount else board.rate(castle)
        if not board.holds(castle, after, rate):
            break
        board.buy(castle, upgrade_type, cost)
        bought.append(
            f"{'production' if upgrade_type == UpgradeType.generation_amount else 'speed'}{level}@{castle.id}"
        )
    return " ".join(bought)


def attack(board: Board) -> str:
    """Strike the enemy castle with the smallest price once the castles nearest it can pay. Returns the log note."""
    best = None
    for target in board.enemies:
        senders = board.senders(target)
        if not senders:
            continue
        price = None
        paid_by = None
        for count in range(1, min(MOST_SENDERS, len(senders)) + 1):
            chosen = senders[:count]
            turns = max(walk for walk, _, _ in chosen)
            amount = attack_price(board, target, turns)
            if price is None:
                price = amount
            if amount >= 1 and sum(board.avail(castle) for _, _, castle in chosen) >= amount:
                price = amount
                paid_by = chosen
                break
        if price is None or price < 1:
            continue
        if best is None or price < best[0]:
            best = (price, target, paid_by)
    if best is None:
        return ""
    price, target, chosen = best
    if chosen is None:
        return ""
    turns = max(board.travel(castle, target) for _, _, castle in chosen)
    kind = "exact" if is_exact(board, turns) else "need"
    parts = board.send_split([castle for _, _, castle in chosen], target, price)
    return f"strike>{target.id} {kind} {price} " + " ".join(parts)


def saving(board: Board, castle: Castle) -> bool:
    """Whether the castle is a few turns from affording its next upgrade."""
    production_level = board.level(castle, UpgradeType.generation_amount)
    speed_level = board.level(castle, UpgradeType.speed)
    if production_level < TOP_PRODUCTION:
        entry = board.table(UpgradeType.generation_amount, production_level + 1)
    elif speed_level < TOP_SPEED:
        entry = board.table(UpgradeType.speed, speed_level + 1)
    else:
        return False
    if entry is None:
        return False
    short = entry[1] - board.left(castle)
    return 0 < short <= SAVE_TURNS * board.rate(castle)


def expand(board: Board) -> str:
    """Take the neutrals cheapest counting the walk, when the castles nearest them can pay. Returns the log note."""
    notes = []

    def rank(neutral: Castle) -> tuple[int, int, int]:
        walk = min((board.travel(castle, neutral) for castle in board.own), default=0)
        return neutral.soldiers + walk, neutral.soldiers, neutral.id

    for target in sorted(board.neutrals, key=rank):
        everyone = board.senders(target)
        if not everyone:
            break
        helpers = [entry for entry in everyone if not saving(board, entry[2])]
        for count in range(1, MOST_SENDERS + 1):
            senders = everyone if count == 1 else helpers
            if count > len(senders):
                break
            chosen = senders[:count]
            turns = max(walk for walk, _, _ in chosen)
            amount = attack_price(board, target, turns, neutral=True)
            if amount < 1:
                break
            if sum(board.avail(castle) for _, _, castle in chosen) >= amount:
                parts = board.send_split([castle for _, _, castle in chosen], target, amount)
                notes.append(f"take>{target.id} " + " ".join(parts))
                break
    return " ".join(notes)


def stalled(board: Board, castle: Castle) -> bool:
    """Whether the castle could pay its next upgrade but would then be left to a single enemy castle."""
    production_level = board.level(castle, UpgradeType.generation_amount)
    speed_level = board.level(castle, UpgradeType.speed)
    if production_level < TOP_PRODUCTION:
        entry = board.table(UpgradeType.generation_amount, production_level + 1)
        rate = int(entry[0]) if entry else board.rate(castle)
    elif speed_level < TOP_SPEED:
        entry = board.table(UpgradeType.speed, speed_level + 1)
        rate = board.rate(castle)
    else:
        return False
    if entry is None:
        return False
    after = board.left(castle) - entry[1]
    return after >= 0 and not board.holds(castle, after, rate)


def stall_feed(board: Board) -> str:
    """Castles behind the front whose next upgrade is unsafe send their spare soldiers to the front."""
    if not board.enemies or len(board.own) < 2:
        return ""
    front = min(board.own, key=lambda castle: (min(castle.distance(e) for e in board.enemies), castle.id))
    parts = []
    for castle in board.own:
        if castle.id == front.id or board.attacked(castle) or not stalled(board, castle):
            continue
        amount = max(0, board.left(castle) - board.reserve(castle, everyone=True))
        if amount < FEED_AT:
            continue
        board.send(castle, front, amount)
        parts.append(f"{castle.id}:{amount}")
    return f"stalled>{front.id} " + " ".join(parts) if parts else ""


def feed(board: Board) -> str:
    """Fully upgraded castles behind the front send it everything, if they hold with none. Returns the log note."""
    if not board.enemies or len(board.own) < 2:
        return ""
    front = min(board.own, key=lambda castle: (min(castle.distance(e) for e in board.enemies), castle.id))
    parts = []
    for castle in board.own:
        if (
            castle.id == front.id
            or board.level(castle, UpgradeType.generation_amount) < TOP_PRODUCTION
            or board.level(castle, UpgradeType.speed) < TOP_SPEED
            or board.attacked(castle)
            or board.left(castle) < FEED_AT
            or board.reserve(castle, everyone=True) > 0
        ):
            continue
        amount = board.left(castle)
        board.send(castle, front, amount)
        parts.append(f"{castle.id}:{amount}")
    return f"feed>{front.id} " + " ".join(parts) if parts else ""


def play(turn: BotTurn) -> BotTurnResult:
    """Play one turn: a pure function of the turn.

    Args:
        turn: The board, this bot's team, the upgrade table and last turn's memory.

    Returns:
        The commands to run, and the memory for the next turn.
    """
    board = Board(turn)
    if turn.turn_number == 1:
        notes = [first_turn(board)]
    else:
        notes = [defend(board), hold(board), speed_strike(board)]
        notes += [upgrade(board, castle) for castle in board.own]
        notes += [attack(board), expand(board), feed(board), stall_feed(board)]
    freed = [
        f"{castle.id}:{board.reserve(castle, everyone=True) - board.reserve(castle)}"
        for castle in board.own
        if board.reserve(castle, everyone=True) > board.reserve(castle)
    ]
    if freed:
        notes.append("late reserve freed " + " ".join(freed))
    if turn.turn_number > 1:
        outgrown = [str(castle.id) for castle in board.own if board.targeted(castle) and not board.attacked(castle)]
        if outgrown:
            notes.append("outgrows groups bound for " + ",".join(outgrown))
    logger.info(
        "turn %d: %d castles producing %d a turn; %s",
        turn.turn_number,
        len(board.own),
        sum(production(turn, castle) for castle in board.own),
        " ".join(note for note in notes if note) or "saving",
    )
    return turn_result(board.commands)
