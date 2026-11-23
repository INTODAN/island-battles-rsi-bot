// Frontline that pays safe neutrals exactly and holds them: safe_hold.
//
// Iteration 13, from finish_safe. A neutral castle paid exactly must also
// outlast the enemy castles whose groups could land on it within holdTurns
// after the capture, less what it grows in that time: finish_safe took safe
// neutrals with 1 soldier and lost them to the next enemy castle along.
// finish_safe (iteration 10), from hold_finish. A neutral castle that no enemy castle is
// nearer to than the castle attacking it is paid exactly: its own soldiers are
// certain, and no enemy strikes it back before it grows. A contested neutral
// still costs neutralMargin times its soldiers. hold_exact (iteration 9) paid
// every neutral exactly and lost the castles it took with 1 soldier next to
// the enemy.
// hold_finish (iteration 9), from frontline_hold, with frontline_finish's finish grafted in:
// in the last finishTurns turns before the strike would land at the turn
// limit, a strike needs the target's soldiers, reinforcements, growth and its
// largest burst exactly, not strikeMargin times them.
// frontline_hold (iteration 8), from frontline. A neutral castle's price is found by playing
// every known landing on it in order, the bot's groups and the enemy's, before
// and after the new group, with its growth once owned: the new group is the
// fewest soldiers that leave it the bot's after the last of them. frontline
// subtracted its own groups bound for the target whatever their landing turn,
// so it topped up with groups of 1 that landed alone, and it ignored enemy
// groups that land after its own, so it wore neutrals down for the enemy.
// frontline (iteration 7): a new strategy on speed_margin's scaffolding (its Board and its
// reinforcement of castles that would fall). Every castle buys production, then
// speed up to speedLevel once production is at its top. Castles take neutral
// castles with neutralMargin. The castle nearest the enemy is the front: every
// other castle sends it its spare soldiers once they are batch or more. An enemy
// castle is struck by the own castles whose groups land within strikeSpread
// turns of the nearest one, all at once, when their spare soldiers together are
// strikeMargin times its defenders.
package main

import (
	"context"
	"fmt"
	"math"
	"slices"
	"strings"

	islandbattles "github.com/INTODAN/island-battles-go/clients/island-battles-go"
)

const (
	// Soldiers a castle keeps home besides what is on its way to attack it.
	guard = 4
	// A neutral castle is taken with this many times what it will hold.
	neutralMargin = 1.4
	// An enemy castle is struck only with this many times its soldiers and reinforcements.
	strikeMargin = 1.5
	// A castle sends its spare soldiers to the front once they are this many.
	batch = 10
	// Castles whose groups land within this many turns of the nearest one join a strike.
	strikeSpread = 2
	// Every castle buys speed up to this level once its production is at the top.
	speedLevel = 2
	// A neutral paid exactly must outlast the enemy castles that could land within this many turns after the capture.
	holdTurns = 5
	// A strike that lands within this many turns of the turn limit counts the target exactly.
	finishTurns = 30
	// Landing order of this turn's sends, after every group on the board, and of
	// the group being sized, after those.
	laterID = 1 << 40
	newID   = 1 << 50
	// A walk's turns are rounded up, less this much, so that an exact walk isn't a turn longer.
	walkSlack = 1e-9
	// No team: a neutral castle's colour.
	neutral = 0
)

const (
	production = islandbattles.GenerationAmountUpgrade
	speed      = islandbattles.SpeedUpgrade
	burst      = islandbattles.BurstPotentialUpgrade
)

func main() {
	islandbattles.Main(play)
}

// hypot is the length of (x, y), rounded as the Python SDK's distance rounds it
// (CPython's math.hypot): math.Hypot differs in the last bit on about a third of
// the boards' distances, and a walk's turns are rounded from them.
func hypot(x, y float64) float64 {
	x, y = math.Abs(x), math.Abs(y)
	largest := max(x, y)
	if math.IsInf(largest, 0) || largest == 0 {
		return largest
	}
	_, exponent := math.Frexp(largest)
	if exponent < -1023 {
		const smallest = 2.2250738585072014e-308
		return smallest * hypot(x/smallest, y/smallest)
	}
	scale := math.Ldexp(1, -exponent)
	csum, frac1, frac2 := 1.0, 0.0, 0.0
	for _, value := range [2]float64{x, y} {
		value *= scale
		high := float64(value * value)
		low := math.FMA(value, value, -high)
		sum := float64(csum + high)
		frac1 += low
		frac2 += float64(csum-sum) + high
		csum = sum
	}
	root := math.Sqrt(float64(csum-1.0) + float64(frac1+frac2))
	high := float64(-root * root)
	low := math.FMA(-root, root, -high)
	sum := float64(csum + high)
	frac1 += low
	frac2 += float64(csum-sum) + high
	csum = sum
	rest := float64(csum-1.0) + float64(frac1+frac2)
	root += rest / float64(2.0*root)
	return root / scale
}

// walkTurns is the turns a walk of this distance takes at this speed: at least one.
func walkTurns(distance, unitsPerTurn float64) int {
	return max(1, int(math.Ceil(distance/unitsPerTurn-walkSlack)))
}

// ceilTimes is ceil(soldiers * margin), as Python rounds an int times a float up.
func ceilTimes(soldiers int, margin float64) int {
	return int(math.Ceil(float64(soldiers) * margin))
}

// castle is a castle of the board, with plain ints.
type castle struct {
	id        int
	team      int
	soldiers  int
	x, y      float64
	upgrades  islandbattles.Upgrades
	burstDebt int
}

// distance is the straight-line distance from the castle to another.
func (from *castle) distance(to *castle) float64 {
	return hypot(to.x-from.x, to.y-from.y)
}

// group is a soldier group of the board.
type group struct {
	id          int
	team        int
	soldiers    int
	destination int
	upgrades    islandbattles.Upgrades
	// left is the distance still to go to its destination castle.
	left float64
}

// landing is a send of this turn: the turns until it lands and its soldiers.
type landing struct {
	turns    int
	soldiers int
}

// purchase is a castle and an upgrade type it bought.
type purchase struct {
	castle      int
	upgradeType islandbattles.UpgradeType
}

// event is a landing on a castle: (turn, order, team, soldiers).
type event struct {
	turns    int
	order    int
	team     int
	soldiers int
}

// sortEvents sorts by landing turn, then order (unique).
func sortEvents(events []event) {
	slices.SortFunc(events, func(first, second event) int {
		if first.turns != second.turns {
			return first.turns - second.turns
		}
		return first.order - second.order
	})
}

// board is the turn's board, and what this turn's commands have spent so far.
type board struct {
	turn     islandbattles.Turn
	team     int
	castles  []*castle
	groups   []*group
	own      []*castle
	enemies  []*castle
	neutrals []*castle
	commands []islandbattles.Command
	// spent is the soldiers each castle has spent this turn. The server rejects the
	// whole result when a castle spends more than it has.
	spent map[int]int
	// speedBought is the speed levels bought this turn, which the groups sent after them have.
	speedBought map[int]int
	bought      map[purchase]bool
	// sentLandings is this turn's sends to each castle: (turns until it lands, soldiers).
	sentLandings map[int][]landing
}

// newBoard reads the board from the turn.
func newBoard(turn islandbattles.Turn) *board {
	b := &board{
		turn:         turn,
		team:         int(turn.TeamColor),
		spent:        map[int]int{},
		speedBought:  map[int]int{},
		bought:       map[purchase]bool{},
		sentLandings: map[int][]landing{},
	}
	byID := map[int]*castle{}
	for _, source := range turn.Generation.Castles {
		c := &castle{
			id:        int(source.ID),
			team:      int(source.TeamColor),
			soldiers:  int(source.Soldiers),
			x:         source.X,
			y:         source.Y,
			upgrades:  source.Upgrades,
			burstDebt: int(source.BurstDebt),
		}
		b.castles = append(b.castles, c)
		byID[c.id] = c
	}
	slices.SortStableFunc(b.castles, func(first, second *castle) int { return first.id - second.id })
	for _, source := range turn.Generation.SoldierGroups {
		g := &group{
			id:          int(source.ID),
			team:        int(source.TeamColor),
			soldiers:    int(source.Soldiers),
			destination: int(source.DestinationCastleID),
			upgrades:    source.Upgrades,
		}
		if destination, found := byID[g.destination]; found {
			g.left = hypot(destination.x-source.X, destination.y-source.Y)
		}
		b.groups = append(b.groups, g)
	}
	slices.SortStableFunc(b.groups, func(first, second *group) int { return first.id - second.id })
	for _, c := range b.castles {
		switch c.team {
		case b.team:
			b.own = append(b.own, c)
		case neutral:
			b.neutrals = append(b.neutrals, c)
		default:
			b.enemies = append(b.enemies, c)
		}
	}
	return b
}

// tableValue is the value of an upgrade type's level, from the turn's table, and 0 when it lacks it.
func (b *board) tableValue(upgradeType islandbattles.UpgradeType, level int) float64 {
	for _, upgrade := range b.turn.Upgrades {
		if upgrade.Type == upgradeType {
			for _, entry := range upgrade.Levels {
				if entry.Level == level {
					return entry.Value
				}
			}
		}
	}
	return 0.0
}

// levelValue is the value of the castle's level of a type, as the SDK reads it: false when the table lacks it.
func (b *board) levelValue(c *castle, upgradeType islandbattles.UpgradeType) (float64, bool) {
	level := c.upgrades.Level(upgradeType)
	for _, upgrade := range b.turn.Upgrades {
		if upgrade.Type == upgradeType {
			for _, entry := range upgrade.Levels {
				if entry.Level == level {
					return entry.Value, true
				}
			}
			return 0, false
		}
	}
	return 0, false
}

// production is what the castle produces a turn while a team owns it, not counting this turn's purchases.
func (b *board) production(c *castle) int {
	value, found := b.levelValue(c, production)
	if !found {
		return 1
	}
	return int(value)
}

// burstPotential is the largest burst the castle may order, not counting this turn's purchases.
func (b *board) burstPotential(c *castle) int {
	value, found := b.levelValue(c, burst)
	if !found {
		return 0
	}
	return int(value)
}

// nextUpgradeCost is what the castle's next level of a type costs, as the SDK reads it: false at the top.
func (b *board) nextUpgradeCost(c *castle, upgradeType islandbattles.UpgradeType) (int, bool) {
	level := c.upgrades.Level(upgradeType) + 1
	for _, upgrade := range b.turn.Upgrades {
		if upgrade.Type == upgradeType {
			for _, entry := range upgrade.Levels {
				if entry.Level == level {
					return int(entry.SoldierCost), true
				}
			}
			return 0, false
		}
	}
	return 0, false
}

// left is the soldiers the castle hasn't spent yet this turn.
func (b *board) left(c *castle) int {
	return c.soldiers - b.spent[c.id]
}

// travel is the turns a group sent now from origin takes to land on target.
func (b *board) travel(origin, target *castle) int {
	level := origin.upgrades.Level(speed) + b.speedBought[origin.id]
	return walkTurns(origin.distance(target), b.tableValue(speed, level))
}

// arrival is the turns until a group lands, if nothing stops it.
func (b *board) arrival(g *group) int {
	return walkTurns(g.left, b.tableValue(speed, g.upgrades.Level(speed)))
}

// headingTo is the soldiers on their way to the castle: this bot's, or everyone else's.
func (b *board) headingTo(c *castle, friendly bool) int {
	total := 0
	for _, g := range b.groups {
		if g.destination == c.id && (g.team == b.team) == friendly {
			total += g.soldiers
		}
	}
	return total
}

// send sends soldiers, counting them as spent.
func (b *board) send(origin, target *castle, amount int) {
	turns := b.travel(origin, target)
	b.commands = append(b.commands, islandbattles.SendSoldierGroup(uint(origin.id), uint(target.id), uint(amount)))
	b.spent[origin.id] += amount
	b.sentLandings[target.id] = append(b.sentLandings[target.id], landing{turns, amount})
}

// landings is every known landing on the target, in the order they land.
//
// Groups on the board land in group id order within a turn; this turn's sends
// get higher ids than any group on the board.
func (b *board) landings(target *castle) []event {
	var events []event
	for _, g := range b.groups {
		if g.destination == target.id {
			events = append(events, event{b.arrival(g), g.id, g.team, g.soldiers})
		}
	}
	for index, sent := range b.sentLandings[target.id] {
		events = append(events, event{sent.turns, laterID + index, b.team, sent.soldiers})
	}
	sortEvents(events)
	return events
}

// holdsAfter is whether a group of amount landing on target in travel turns leaves it the bot's after every
// known landing.
//
// What the target holds and the enemy's groups count margin times; a castle's
// growth between landings counts as it is.
func (b *board) holdsAfter(target *castle, travel, amount int, margin float64, exact bool) bool {
	ownTeam := b.team
	events := b.landings(target)
	events = append(events, event{travel, newID, ownTeam, amount})
	sortEvents(events)
	owner := target.team
	soldiers := ceilTimes(target.soldiers, margin)
	if owner == ownTeam || (exact && owner == neutral) {
		soldiers = target.soldiers
	}
	rate := b.production(target)
	capturedRate := int(b.tableValue(production, target.upgrades.Level(production)))
	now := 0
	for _, e := range events {
		if owner != neutral {
			soldiers += rate * (e.turns - now)
		}
		now = e.turns
		size := e.soldiers
		if e.team != ownTeam {
			size = ceilTimes(size, margin)
		}
		switch {
		case e.team == owner:
			soldiers += size
		case size > soldiers:
			owner = e.team
			soldiers = size - soldiers
			rate = capturedRate
		default:
			soldiers -= size
		}
	}
	return owner == ownTeam
}

// needToHold is the fewest soldiers that, sent now from origin, leave the target the bot's after every known
// landing.
//
// 0 when it becomes the bot's without a new group, available + 1 when even all
// the available soldiers won't do.
func (b *board) needToHold(origin, target *castle, available int, margin float64, exact bool) int {
	travel := b.travel(origin, target)
	if b.holdsAfter(target, travel, 0, margin, exact) {
		return 0
	}
	if !b.holdsAfter(target, travel, available, margin, exact) {
		return available + 1
	}
	low, high := 1, available
	for low < high {
		middle := floorDiv(low+high, 2)
		if b.holdsAfter(target, travel, middle, margin, exact) {
			high = middle
		} else {
			low = middle + 1
		}
	}
	return low
}

// floorDiv divides rounding down, also for a negative dividend.
func floorDiv(dividend, divisor int) int {
	quotient := dividend / divisor
	if (dividend%divisor != 0) && ((dividend < 0) != (divisor < 0)) {
		quotient--
	}
	return quotient
}

// buy buys the castle's next level of an upgrade if it leaves the reserve, once a turn.
func (b *board) buy(c *castle, upgradeType islandbattles.UpgradeType, reserve int) bool {
	cost, found := b.nextUpgradeCost(c, upgradeType)
	if !found || b.left(c)-cost < reserve || b.bought[purchase{c.id, upgradeType}] {
		return false
	}
	b.bought[purchase{c.id, upgradeType}] = true
	b.commands = append(b.commands, islandbattles.UpgradeCastle(uint(c.id), upgradeType))
	b.spent[c.id] += cost
	if upgradeType == speed {
		b.speedBought[c.id] = 1
	}
	return true
}

// reinforce sends help to castles that would fall, from castles whose groups land in time.
//
// Returns the castles short under attack and how many of them stay short.
func reinforce(b *board, notes *[]string) (int, int) {
	shortfall := map[int]int{}
	deadline := map[int]int{}
	var needyIDs []int
	for _, c := range b.own {
		attacking := 0
		soonest := 0
		found := false
		for _, g := range b.groups {
			if g.destination == c.id && g.team != b.team {
				if turns := b.arrival(g); !found || turns < soonest {
					soonest = turns
				}
				found = true
				attacking += g.soldiers
			}
		}
		if !found {
			continue
		}
		holding := c.soldiers + b.production(c)*soonest + b.headingTo(c, true)
		missing := attacking + 1 - holding
		if missing > 0 {
			shortfall[c.id] = missing
			deadline[c.id] = soonest
			needyIDs = append(needyIDs, c.id)
		}
	}
	byID := map[int]*castle{}
	for _, c := range b.castles {
		byID[c.id] = c
	}
	slices.SortFunc(needyIDs, func(first, second int) int {
		if deadline[first] != deadline[second] {
			return deadline[first] - deadline[second]
		}
		return first - second
	})
	for _, needyID := range needyIDs {
		needy := byID[needyID]
		var helpers []*castle
		for _, c := range b.own {
			if _, short := shortfall[c.id]; !short {
				helpers = append(helpers, c)
			}
		}
		slices.SortStableFunc(helpers, func(first, second *castle) int {
			firstDistance, secondDistance := first.distance(needy), second.distance(needy)
			switch {
			case firstDistance < secondDistance:
				return -1
			case firstDistance > secondDistance:
				return 1
			}
			return first.id - second.id
		})
		for _, helper := range helpers {
			if shortfall[needyID] <= 0 {
				break
			}
			if b.travel(helper, needy) > deadline[needyID] {
				continue
			}
			spare := b.left(helper) - b.headingTo(helper, false) - guard
			amount := min(spare, shortfall[needyID])
			if amount < 1 {
				continue
			}
			b.send(helper, needy, amount)
			*notes = append(*notes, fmt.Sprintf("%d+>%d:%d", helper.id, needyID, amount))
			shortfall[needyID] -= amount
		}
	}
	unheld := 0
	for _, missing := range shortfall {
		if missing > 0 {
			unheld++
		}
	}
	return len(shortfall), unheld
}

// joiner is a castle that joins a strike, with its walk there.
type joiner struct {
	walk   int
	castle *castle
}

// strike strikes the cheapest enemy castle that the castles nearest it can take together. Returns the log note.
func strike(b *board, spare map[int]int) string {
	turn := b.turn
	found := false
	bestCost, bestNeed := 0, 0
	var bestTarget *castle
	var bestJoining []joiner
	for _, target := range b.enemies {
		var ready []joiner
		for _, c := range b.own {
			if spare[c.id] >= 1 {
				ready = append(ready, joiner{b.travel(c, target), c})
			}
		}
		if len(ready) == 0 {
			continue
		}
		slices.SortFunc(ready, func(first, second joiner) int {
			if first.walk != second.walk {
				return first.walk - second.walk
			}
			return first.castle.id - second.castle.id
		})
		nearest := ready[0].walk
		var joining []joiner
		for _, j := range ready {
			if j.walk <= nearest+strikeSpread {
				joining = append(joining, j)
			}
		}
		last := joining[0].walk
		for _, j := range joining[1:] {
			last = max(last, j.walk)
		}
		reinforcing := 0
		for _, g := range b.groups {
			if g.destination == target.id && g.team != b.team && b.arrival(g) <= last {
				reinforcing += g.soldiers
			}
		}
		friendly := b.headingTo(target, true)
		margin := strikeMargin
		extra := 0
		if turn.MaxGenerations-turn.TurnNumber <= last+finishTurns {
			// The finish: no margin, but the burst the target could still add.
			margin = 1.0
			if target.burstDebt == 0 {
				extra = b.burstPotential(target)
			}
		}
		need := ceilTimes(target.soldiers+reinforcing, margin) + b.production(target)*last + extra + 1 - friendly
		total := 0
		for _, j := range joining {
			total += spare[j.castle.id]
		}
		if need < 1 || total < need {
			continue
		}
		cost := need + 2*last - 3*b.production(target)
		if !found || cost < bestCost {
			found = true
			bestCost, bestNeed, bestTarget, bestJoining = cost, need, target, joining
		}
	}
	if !found {
		return ""
	}
	var parts []string
	for _, j := range bestJoining {
		amount := spare[j.castle.id]
		b.send(j.castle, bestTarget, amount)
		spare[j.castle.id] = 0
		parts = append(parts, fmt.Sprintf("%d:%d", j.castle.id, amount))
	}
	finish := ""
	if turn.MaxGenerations-turn.TurnNumber <= bestJoining[len(bestJoining)-1].walk+finishTurns {
		finish = "finish "
	}
	return fmt.Sprintf("%sstrike>%d need %d ", finish, bestTarget.id, bestNeed) + strings.Join(parts, " ")
}

// expand takes the cheapest neutral this castle can afford, exactly when it is safe. Returns the log note (= safe).
func expand(b *board, c *castle, spare map[int]int) string {
	found := false
	bestCost, bestNeed := 0, 0
	var bestTarget *castle
	bestSafe := false
	for _, target := range b.neutrals {
		// Safe: no enemy castle is nearer to the neutral than this castle.
		safe := true
		for _, enemy := range b.enemies {
			if !(enemy.distance(target) >= c.distance(target)) {
				safe = false
				break
			}
		}
		need := b.needToHold(c, target, spare[c.id], neutralMargin, safe)
		if safe && need >= 1 {
			walk := b.travel(c, target)
			threat := 0
			for _, enemy := range b.enemies {
				if b.travel(enemy, target) <= walk+holdTurns {
					threat += enemy.soldiers
				}
			}
			need += max(0, threat-b.production(target)*holdTurns)
		}
		if need < 1 || need > spare[c.id] {
			continue
		}
		cost := need + 2*b.travel(c, target)
		if !found || cost < bestCost {
			found = true
			bestCost, bestNeed, bestTarget, bestSafe = cost, need, target, safe
		}
	}
	if !found {
		return ""
	}
	b.send(c, bestTarget, bestNeed)
	spare[c.id] -= bestNeed
	mark := ""
	if bestSafe {
		mark = "="
	}
	return fmt.Sprintf("%d->%d%s:%d", c.id, bestTarget.id, mark, bestNeed)
}

// toEnemy is the distance from the castle to the nearest enemy castle.
func toEnemy(b *board, c *castle) float64 {
	nearest := c.distance(b.enemies[0])
	for _, enemy := range b.enemies[1:] {
		nearest = min(nearest, c.distance(enemy))
	}
	return nearest
}

// play plays one turn: a pure function of the turn.
func play(_ context.Context, turn islandbattles.Turn) (islandbattles.Result, error) {
	b := newBoard(turn)
	var notes []string
	short, unheld := reinforce(b, &notes)
	spare := map[int]int{}
	for _, c := range b.own {
		reserve := b.headingTo(c, false) + guard
		if b.buy(c, production, reserve) {
			notes = append(notes, fmt.Sprintf("production@%d", c.id))
		} else if _, more := b.nextUpgradeCost(c, production); !more &&
			c.upgrades.Level(speed) < speedLevel &&
			b.buy(c, speed, reserve) {
			notes = append(notes, fmt.Sprintf("speed@%d", c.id))
		}
		spare[c.id] = max(0, b.left(c)-reserve)
	}
	if struck := strike(b, spare); struck != "" {
		notes = append(notes, struck)
	}
	for _, c := range b.own {
		if spare[c.id] >= 1 {
			if expanded := expand(b, c, spare); expanded != "" {
				notes = append(notes, expanded)
			}
		}
	}
	if len(b.enemies) > 0 && len(b.own) > 0 {
		front := b.own[0]
		frontDistance := toEnemy(b, front)
		for _, c := range b.own[1:] {
			if distance := toEnemy(b, c); distance < frontDistance {
				front, frontDistance = c, distance
			}
		}
		var moves []string
		for _, c := range b.own {
			if c.id == front.id || spare[c.id] < batch || toEnemy(b, front) >= toEnemy(b, c) {
				continue
			}
			b.send(c, front, spare[c.id])
			moves = append(moves, fmt.Sprintf("%d:%d", c.id, spare[c.id]))
			spare[c.id] = 0
		}
		if len(moves) > 0 {
			notes = append(notes, fmt.Sprintf("stage>%d ", front.id)+strings.Join(moves, " "))
		}
	}
	producing := 0
	for _, c := range b.own {
		producing += b.production(c)
	}
	summary := strings.Join(notes, " ")
	if summary == "" {
		summary = "saving"
	}
	return islandbattles.Result{
		Commands: b.commands,
		Logs: []islandbattles.LogLine{islandbattles.Logf(
			"turn %d: %d castles producing %d a turn, %d short under attack (%d unheld); %s",
			turn.TurnNumber, len(b.own), producing, short, unheld, summary,
		)},
	}, nil
}
