"""Frontline that finishes level games: frontline_finish.

Iteration 8, from frontline. In the last FINISH_TURNS turns before the
strike would land at the turn limit, a strike needs the target's soldiers,
reinforcements, growth and its largest burst exactly, not STRIKE_MARGIN times
them: a game level at the limit is a draw, and an exact strike with more
soldiers wins it.
frontline (iteration 7): a new strategy on speed_margin's scaffolding (its Board and its
reinforcement of castles that would fall). Every castle buys production, then
speed up to SPEED_LEVEL once production is at its top. Castles take neutral
castles with NEUTRAL_MARGIN. The castle nearest the enemy is the front: every
other castle sends it its spare soldiers once they are BATCH or more. An enemy
castle is struck by the own castles whose groups land within STRIKE_SPREAD
turns of the nearest one, all at once, when their spare soldiers together are
STRIKE_MARGIN times its defenders.
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
    next_upgrade_cost,
    production,
    send_soldier_group,
    turn_result,
    upgrade_castle,
)


class Board:
    """The turn's board, and what this turn's commands have spent so far."""

    def __init__(self, turn: BotTurn) -> None:
        """Read the board from the turn."""
        self.turn = turn
        self.castles = sorted(turn.generation.castles, key=lambda castle: castle.id)
        self.groups = sorted(turn.generation.soldier_groups, key=lambda group: group.id)
        self.own = [castle for castle in self.castles if castle.team_color == turn.team_color]
        self.others = [castle for castle in self.castles if castle.team_color != turn.team_color]
        self.enemies = [castle for castle in self.others if castle.team_color != NEUTRAL_TEAM_COLOR]
        self.neutrals = [castle for castle in self.others if castle.team_color == NEUTRAL_TEAM_COLOR]
        self.commands: list[PublicGenerationCommand] = []
        # Soldiers each castle has spent this turn. The server rejects the
        # whole result when a castle spends more than it has.
        self.spent: dict[int, int] = {}
        # Speed levels bought this turn, which the groups sent after them have.
        self.speed_bought: dict[int, int] = {}
        self.bought: set[tuple[int, UpgradeType]] = set()
        # Soldiers this turn's commands sent to each castle.
        self.sent_to: dict[int, int] = {}

    def level_value(self, upgrade_type: UpgradeType, level: int) -> float:
        """The value of an upgrade type's level, from the turn's table."""
        for upgrade in self.turn.upgrades:
            if upgrade.type == upgrade_type:
                for entry in upgrade.levels:
                    if entry.level == level:
                        return entry.value
        return 0.0

    def left(self, castle: Castle) -> int:
        """The soldiers the castle hasn't spent yet this turn."""
        return castle.soldiers - self.spent.get(castle.id, 0)

    def travel_turns(self, origin: Castle, target: Castle) -> int:
        """The turns a group sent now from origin takes to land on target."""
        level = origin.upgrades[UpgradeType.speed] + self.speed_bought.get(origin.id, 0)
        return max(
            1,
            ceil(origin.distance(target) / self.level_value(UpgradeType.speed, level) - 1e-9),
        )

    def arrival_turns(self, group: SoldierGroup) -> int:
        """The turns until a group lands, if nothing stops it."""
        speed = self.level_value(UpgradeType.speed, group.upgrades[UpgradeType.speed])
        return max(1, ceil(group.distance_left() / speed - 1e-9))

    def heading_to(self, castle: Castle, friendly: bool) -> int:
        """The soldiers on their way to the castle: this bot's, or everyone else's."""
        return sum(
            group.soldiers
            for group in self.groups
            if group.destination_castle_id == castle.id and (group.team_color == self.turn.team_color) == friendly
        )

    def defenders_on_arrival(self, origin: Castle, target: Castle) -> int:
        """The soldiers a group sent now from origin would meet in target.

        A castle that a team owns grows while the group walks; a neutral one
        doesn't.
        """
        growth = 0
        if target.team_color != NEUTRAL_TEAM_COLOR:
            growth = production(self.turn, target) * self.travel_turns(origin, target)
        return target.soldiers + growth

    def send(self, origin: Castle, target: Castle, amount: int) -> None:
        """Send soldiers, counting them as spent."""
        self.commands.append(send_soldier_group(origin.id, target.id, amount))
        self.spent[origin.id] = self.spent.get(origin.id, 0) + amount
        self.sent_to[target.id] = self.sent_to.get(target.id, 0) + amount

    def contested_defenders(self, origin: Castle, target: Castle) -> tuple[int, int, bool]:
        """What a group sent now from origin would meet in target: soldiers, growth, and whether an enemy holds it.

        Enemy groups bound for the target that land no later than this group
        land first: on a neutral castle they fight its soldiers and may take
        it, which then grows; on an enemy castle they join its soldiers.
        """
        travel = self.travel_turns(origin, target)
        arrivals = sorted(
            (self.arrival_turns(group), group.id, group.soldiers)
            for group in self.groups
            if group.destination_castle_id == target.id
            and group.team_color != self.turn.team_color
            and self.arrival_turns(group) <= travel
        )
        if target.team_color != NEUTRAL_TEAM_COLOR:
            reinforcing = sum(soldiers for _, _, soldiers in arrivals)
            growth = self.defenders_on_arrival(origin, target) - target.soldiers
            return target.soldiers + reinforcing, growth, True
        soldiers = target.soldiers
        enemy_since = None
        for landing, _, amount in arrivals:
            if enemy_since is None:
                if amount > soldiers:
                    soldiers = amount - soldiers
                    enemy_since = landing
                else:
                    soldiers -= amount
            else:
                soldiers += amount
        if enemy_since is None:
            return soldiers, 0, False
        # The castle grows at level 1 from the turn after its capture.
        return soldiers, max(0, travel - enemy_since), True

    def buy(self, castle: Castle, upgrade_type: UpgradeType, reserve: int = 0) -> bool:
        """Buy the castle's next level of an upgrade if it leaves the reserve, once a turn."""
        cost = next_upgrade_cost(self.turn, castle, upgrade_type)
        if cost is None or self.left(castle) - cost < reserve or (castle.id, upgrade_type) in self.bought:
            return False
        self.bought.add((castle.id, upgrade_type))
        self.commands.append(upgrade_castle(castle.id, upgrade_type))
        self.spent[castle.id] = self.spent.get(castle.id, 0) + cost
        if upgrade_type == UpgradeType.speed:
            self.speed_bought[castle.id] = 1
        return True


# Soldiers a castle keeps home besides what is on its way to attack it.
GUARD = 4
# A neutral castle is taken with this many times what it will hold.
NEUTRAL_MARGIN = 1.4
# An enemy castle is struck only with this many times its soldiers and reinforcements.
STRIKE_MARGIN = 1.5
# A castle sends its spare soldiers to the front once they are this many.
BATCH = 10
# Castles whose groups land within this many turns of the nearest one join a strike.
STRIKE_SPREAD = 2
# Every castle buys speed up to this level once its production is at the top.
SPEED_LEVEL = 2
# A strike that lands within this many turns of the turn limit counts the target exactly.
FINISH_TURNS = 30


def reinforce(board: Board, notes: list[str]) -> tuple[int, int]:
    """Send help to castles that would fall, from castles whose groups land in time.

    Returns the castles short under attack and how many of them stay short.
    """
    turn = board.turn
    shortfall: dict[int, int] = {}
    deadline: dict[int, int] = {}
    for castle in board.own:
        attackers = [
            group
            for group in board.groups
            if group.destination_castle_id == castle.id and group.team_color != turn.team_color
        ]
        if not attackers:
            continue
        soonest = min(board.arrival_turns(group) for group in attackers)
        holding = castle.soldiers + production(turn, castle) * soonest + board.heading_to(castle, friendly=True)
        missing = sum(group.soldiers for group in attackers) + 1 - holding
        if missing > 0:
            shortfall[castle.id] = missing
            deadline[castle.id] = soonest
    by_id = {castle.id: castle for castle in board.castles}
    for needy_id in sorted(shortfall, key=lambda castle_id: (deadline[castle_id], castle_id)):
        needy = by_id[needy_id]
        helpers = sorted(
            (castle for castle in board.own if castle.id not in shortfall),
            key=lambda castle: (castle.distance(needy), castle.id),
        )
        for helper in helpers:
            if shortfall[needy_id] <= 0:
                break
            if board.travel_turns(helper, needy) > deadline[needy_id]:
                continue
            spare = board.left(helper) - board.heading_to(helper, friendly=False) - GUARD
            amount = min(spare, shortfall[needy_id])
            if amount < 1:
                continue
            board.send(helper, needy, amount)
            notes.append(f"{helper.id}+>{needy_id}:{amount}")
            shortfall[needy_id] -= amount
    return len(shortfall), sum(1 for missing in shortfall.values() if missing > 0)


def strike(board: Board, spare: dict[int, int]) -> str:
    """Strike the cheapest enemy castle that the castles nearest it can take together. Returns the log note."""
    turn = board.turn
    best = None
    for target in board.enemies:
        ready = sorted(
            (board.travel_turns(castle, target), castle.id, castle) for castle in board.own if spare[castle.id] >= 1
        )
        if not ready:
            continue
        nearest = ready[0][0]
        joining = [(walk, castle) for walk, _, castle in ready if walk <= nearest + STRIKE_SPREAD]
        last = max(walk for walk, _ in joining)
        reinforcing = sum(
            group.soldiers
            for group in board.groups
            if group.destination_castle_id == target.id
            and group.team_color != turn.team_color
            and board.arrival_turns(group) <= last
        )
        friendly = board.heading_to(target, friendly=True)
        margin = STRIKE_MARGIN
        extra = 0
        if turn.max_generations - turn.turn_number <= last + FINISH_TURNS:
            # The finish: no margin, but the burst the target could still add.
            margin = 1.0
            extra = int(burst_potential(turn, target)) if can_burst(target) else 0
        need = ceil((target.soldiers + reinforcing) * margin) + production(turn, target) * last + extra + 1 - friendly
        total = sum(spare[castle.id] for _, castle in joining)
        if need < 1 or total < need:
            continue
        cost = need + 2 * last - 3 * production(turn, target)
        if best is None or cost < best[0]:
            best = (cost, need, target, joining)
    if best is None:
        return ""
    _, need, target, joining = best
    parts = []
    for _, castle in joining:
        amount = spare[castle.id]
        board.send(castle, target, amount)
        spare[castle.id] = 0
        parts.append(f"{castle.id}:{amount}")
    finish = "finish " if turn.max_generations - turn.turn_number <= joining[-1][0] + FINISH_TURNS else ""
    return f"{finish}strike>{target.id} need {need} " + " ".join(parts)


def expand(board: Board, castle: Castle, spare: dict[int, int]) -> str:
    """Take the cheapest neutral castle this castle can afford with the margin. Returns the log note."""
    best = None
    for target in board.neutrals:
        defenders, growth, enemy_held = board.contested_defenders(castle, target)
        need = ceil(defenders * NEUTRAL_MARGIN) + growth + 1
        need -= board.heading_to(target, friendly=True) + board.sent_to.get(target.id, 0)
        if need < 1 or need > spare[castle.id]:
            continue
        cost = need + 2 * board.travel_turns(castle, target)
        if best is None or cost < best[0]:
            best = (cost, need, target)
    if best is None:
        return ""
    _, need, target = best
    board.send(castle, target, need)
    spare[castle.id] -= need
    return f"{castle.id}->{target.id}:{need}"


def play(turn: BotTurn) -> BotTurnResult:
    """Play one turn: a pure function of the turn.

    Args:
        turn: The board, this bot's team, the upgrade table and last turn's memory.

    Returns:
        The commands to run, and the memory for the next turn.
    """
    board = Board(turn)
    notes: list[str] = []
    short, unheld = reinforce(board, notes)
    spare: dict[int, int] = {}
    for castle in board.own:
        reserve = board.heading_to(castle, friendly=False) + GUARD
        if board.buy(castle, UpgradeType.generation_amount, reserve=reserve):
            notes.append(f"production@{castle.id}")
        elif (
            next_upgrade_cost(turn, castle, UpgradeType.generation_amount) is None
            and castle.upgrades[UpgradeType.speed] < SPEED_LEVEL
            and board.buy(castle, UpgradeType.speed, reserve=reserve)
        ):
            notes.append(f"speed@{castle.id}")
        spare[castle.id] = max(0, board.left(castle) - reserve)
    struck = strike(board, spare)
    if struck:
        notes.append(struck)
    for castle in board.own:
        if spare[castle.id] >= 1:
            expanded = expand(board, castle, spare)
            if expanded:
                notes.append(expanded)
    if board.enemies and board.own:

        def to_enemy(castle: Castle) -> float:
            return min(castle.distance(enemy) for enemy in board.enemies)

        front = min(board.own, key=lambda castle: (to_enemy(castle), castle.id))
        moves = []
        for castle in board.own:
            if castle.id == front.id or spare[castle.id] < BATCH or to_enemy(front) >= to_enemy(castle):
                continue
            board.send(castle, front, spare[castle.id])
            moves.append(f"{castle.id}:{spare[castle.id]}")
            spare[castle.id] = 0
        if moves:
            notes.append(f"stage>{front.id} " + " ".join(moves))
    logger.info(
        "turn %d: %d castles producing %d a turn, %d short under attack (%d unheld); %s",
        turn.turn_number,
        len(board.own),
        sum(production(turn, castle) for castle in board.own),
        short,
        unheld,
        " ".join(notes) or "saving",
    )
    return turn_result(board.commands)
