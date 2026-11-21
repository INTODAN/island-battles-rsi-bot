"""Economist that reinforces, counts who else is going, and stages its soldiers at the front.

Iteration 4, from reinforce_contested. A castle that finds no target it can
afford alone sends its spare soldiers, once they are STAGE_MIN or more, to the
own castle nearest an enemy castle, so that one castle holds enough to strike
alone. reinforce_contested (iteration 2) is economist_reinforce with
economist_contested's target accounting: what a target holds when a group lands
counts the enemy groups that land there first and the groups this turn already
sent there.
economist_reinforce came from economist, with sentinel's reinforcement. A castle
whose soldiers and growth won't hold against the enemy groups heading to it is
reinforced first, by the nearest own castles whose groups land before the
first attacker. Then, as economist, every castle buys generation_amount
levels while it can keep a guard home. With what is left it takes the cheapest
castle it can afford alone, preferring ones that already produce more, and an
enemy castle only with ATTACK_MARGIN times its defenders. The bot keeps
nothing between turns except its memory.
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

    def contested_defenders(self, origin: Castle, target: Castle) -> tuple[int, bool]:
        """What a group sent now from origin would meet in target, and whether an enemy would hold it.

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
            return self.defenders_on_arrival(origin, target) + reinforcing, True
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
            return soldiers, False
        # The castle grows at level 1 from the turn after its capture.
        return soldiers + max(0, travel - enemy_since), True

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
# The bot attacks an enemy castle only with this many times its defenders.
ATTACK_MARGIN = 1.3
# A castle stages its spare soldiers at the front only once they are this many.
STAGE_MIN = 10


def stage(board: Board, idle: list[tuple[Castle, int]]) -> str:
    """Send the idle castles' spare soldiers to the front castle: the own castle nearest an enemy castle.

    A castle sends only when the front is nearer an enemy castle than it is,
    and only STAGE_MIN soldiers or more. Returns the log note, or "".
    """
    if not board.enemies or not idle:
        return ""

    def to_enemy(castle: Castle) -> float:
        return min(castle.distance(enemy) for enemy in board.enemies)

    front = min(board.own, key=lambda castle: (to_enemy(castle), castle.id))
    moves = []
    for castle, spare in idle:
        if castle.id == front.id or spare < STAGE_MIN or to_enemy(front) >= to_enemy(castle):
            continue
        board.send(castle, front, spare)
        moves.append(f"{castle.id}:{spare}")
    if not moves:
        return ""
    return f"stage>{front.id} " + " ".join(moves)


def play(turn: BotTurn) -> BotTurnResult:
    """Play one turn: a pure function of the turn.

    Args:
        turn: The board, this bot's team, the upgrade table and last turn's memory.

    Returns:
        The commands to run, and the memory for the next turn.
    """
    board = Board(turn)
    notes = []
    # What each castle lacks to hold against the attacks on their way to it,
    # and the turns until the first of them lands.
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
        # The nearest helpers first; a group that lands after the attack
        # only retakes, so it doesn't help.
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
    unheld = sum(1 for missing in shortfall.values() if missing > 0)
    idle: list[tuple[Castle, int]] = []
    for castle in board.own:
        reserve = board.heading_to(castle, friendly=False) + GUARD
        if board.buy(castle, UpgradeType.generation_amount, reserve=reserve):
            notes.append(f"production@{castle.id}")
        available = board.left(castle) - reserve
        if available < 1:
            continue
        best = None
        for target in board.others:
            defenders, enemy_held = board.contested_defenders(castle, target)
            if enemy_held:
                defenders = ceil(defenders * ATTACK_MARGIN)
            friendly = board.heading_to(target, friendly=True) + board.sent_to.get(target.id, 0)
            need = defenders + 1 - friendly
            if need < 1 or need > available:
                continue
            # A castle that already produces more is worth more.
            cost = need + 2 * board.travel_turns(castle, target) - 3 * production(turn, target)
            if best is None or cost < best[0]:
                best = (cost, need, target)
        if best is not None:
            board.send(castle, best[2], best[1])
            contested = (
                "!" if best[2].team_color == NEUTRAL_TEAM_COLOR and board.heading_to(best[2], friendly=False) else ""
            )
            notes.append(f"{castle.id}->{best[2].id}{contested}:{best[1]}")
        else:
            idle.append((castle, available))
    staged = stage(board, idle)
    if staged:
        notes.append(staged)
    bought = int((turn.memory or {}).get("bought", 0)) + sum("production@" in note for note in notes)
    logger.info(
        "turn %d: %d castles producing %d a turn, %d short under attack (%d unheld); %s (! = contested neutral)",
        turn.turn_number,
        len(board.own),
        sum(production(turn, castle) for castle in board.own),
        len(shortfall),
        unheld,
        " ".join(notes) or "saving",
    )
    return turn_result(board.commands, memory={"bought": bought})
