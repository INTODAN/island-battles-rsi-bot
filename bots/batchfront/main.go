// batchfront: the frontline line refounded on what the real opponent of games 471-474 did.
//
// Iteration 39, a founder on safe_hold's code (the last bot of the frontline
// line, closed in iteration 38). Four rules, none of them the ori line's:
//
//   - Production is the entry fee: every castle buys production 2 and 3 before
//     it pays for anything (two levels on one turn when it can); until it is at
//     the top it pays only for a neutral whose price plus twice the walk is at
//     most cheapNeutral, and only a castle at the top feeds, strikes or takes a
//     dear neutral. Speed 2 follows the top.
//   - Rear castles at the top feed the front (the castle nearest the enemy) in
//     batches of feedBatch or more, which at production 4 is every three turns,
//     and not while an enemy group is bound for them.
//   - A neutral is paid by the one or two castles nearest it (within
//     neutralSpread turns of the nearest), never by a castle far behind, and
//     not at all when an enemy castle reaches it sooner. Its price plays every
//     known landing on it and adds what holds it after the capture: holdShare
//     of what the strongest enemy castle within holdWindow turns will have, less
//     what the castle grows while that group walks.
//   - A strike leaves from up to strikeCastles castles whose walks are within
//     strikeSpread turns of the nearest one's; the nearer ones wait (the plan is
//     kept in the memory, their soldiers held) so that every group lands on the
//     same turn. A plan whose groups haven't left is dropped when the target
//     outgrows it.
//
// The log line counts castles, production, the front, the soldiers held for a
// strike and the castles short under attack, and names each upgrade
// (production@C), neutral taken (take>N), strike planned (strike>T@turn, with
// (wait) on the parts that leave later), part launched (go>T), feed (feed>F)
// and help (C+>D).
//
// safe_hold's comment follows.
//
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
	guard = 1
	// Every castle buys production up to this level before it pays for anything
	// else; between it and the top it pays only for a neutral whose price plus
	// twice the walk is at most cheapNeutral.
	firstProduction = 3
	cheapNeutral    = 30
	// A neutral is paid by at most this many castles, those whose walk to it is
	// within neutralSpread turns of the nearest castle's.
	neutralCastles = 2
	neutralSpread  = 1
	// A neutral is taken with enough to hold, after the capture, against holdShare
	// of what the strongest enemy castle within holdWindow turns of it will have.
	holdWindow = 14
	holdShare  = 0.5
	// An enemy castle is struck only with this many times its soldiers and reinforcements.
	strikeMargin = 1.5
	// A strike leaves from at most this many castles, those whose walk is within
	// strikeSpread turns of the nearest one's; the nearer ones leave later, so that
	// every group lands on the same turn.
	strikeCastles = 3
	strikeSpread  = 4
	// A castle at the top of production sends its spare soldiers to the front once they are this many.
	feedBatch = 12
	// Every castle buys speed up to this level once its production is at the top.
	speedLevel = 2
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
	// bought is the levels of each type each castle bought this turn.
	bought map[purchase]int
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
		bought:       map[purchase]int{},
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

// boughtLevels is the levels of a type the castle bought this turn.
func (b *board) boughtLevels(c *castle, upgradeType islandbattles.UpgradeType) int {
	return b.bought[purchase{c.id, upgradeType}]
}

// nextUpgradeCost is what the castle's next level of a type costs, counting this turn's purchases: false at the top.
func (b *board) nextUpgradeCost(c *castle, upgradeType islandbattles.UpgradeType) (int, bool) {
	level := c.upgrades.Level(upgradeType) + b.boughtLevels(c, upgradeType) + 1
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
	if b.boughtLevels(c, upgradeType) > 0 {
		return false
	}
	return b.buyAgain(c, upgradeType, reserve)
}

// buyAgain buys the castle's next level of an upgrade if it leaves the reserve, a level more this turn too.
func (b *board) buyAgain(c *castle, upgradeType islandbattles.UpgradeType, reserve int) bool {
	cost, found := b.nextUpgradeCost(c, upgradeType)
	if !found || b.left(c)-cost < reserve {
		return false
	}
	b.bought[purchase{c.id, upgradeType}]++
	b.commands = append(b.commands, islandbattles.UpgradeCastle(uint(c.id), upgradeType))
	b.spent[c.id] += cost
	if upgradeType == speed {
		b.speedBought[c.id]++
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

// planned is one castle's part of a planned strike.
type planned struct {
	Castle int  `json:"castle"`
	Amount int  `json:"amount"`
	Sent   bool `json:"sent"`
}

// plan is a strike whose groups leave on different turns so that they land together.
type plan struct {
	Target int `json:"target"`
	// Land is the turn number on which the groups land.
	Land    int       `json:"land"`
	Senders []planned `json:"senders"`
}

// memory is what the bot keeps between turns: the strike under way.
type memory struct {
	Strike *plan `json:"strike,omitempty"`
}

// byTravel sorts castles by their walk to the target, then by id.
func byTravel(b *board, castles []*castle, target *castle) []*castle {
	sorted := slices.Clone(castles)
	slices.SortStableFunc(sorted, func(first, second *castle) int {
		if walk := b.travel(first, target) - b.travel(second, target); walk != 0 {
			return walk
		}
		return first.id - second.id
	})
	return sorted
}

// castleByID finds a castle of the board, nil when there is none.
func (b *board) castleByID(id int) *castle {
	for _, c := range b.castles {
		if c.id == id {
			return c
		}
	}
	return nil
}

// strikeNeed is what a strike landing in land turns must bring, less what is already on its way.
func strikeNeed(b *board, target *castle, land int) int {
	turn := b.turn
	reinforcing := 0
	for _, g := range b.groups {
		if g.destination == target.id && g.team != b.team && b.arrival(g) <= land {
			reinforcing += g.soldiers
		}
	}
	margin := strikeMargin
	extra := 0
	if turn.MaxGenerations-turn.TurnNumber <= land+finishTurns {
		// The finish: no margin, but the burst the target could still add.
		margin = 1.0
		if target.burstDebt == 0 {
			extra = b.burstPotential(target)
		}
	}
	return ceilTimes(target.soldiers+reinforcing, margin) + b.production(target)*land + extra + 1 - b.headingTo(target, true)
}

// carryStrike launches the parts of the strike under way whose walk is now as long as the turns left to its
// landing, and holds the others' soldiers. Returns the plan still under way, or nil.
func carryStrike(b *board, p *plan, committed map[int]int, notes *[]string) *plan {
	now := b.turn.TurnNumber
	target := b.castleByID(p.Target)
	if target == nil || target.team == b.team || target.team == neutral {
		return nil
	}
	anySent := false
	waiting := 0
	for _, s := range p.Senders {
		anySent = anySent || s.Sent
		if !s.Sent {
			waiting += s.Amount
		}
	}
	if !anySent && strikeNeed(b, target, p.Land-now) > waiting {
		*notes = append(*notes, fmt.Sprintf("drop>%d", p.Target))
		return nil
	}
	var parts []string
	open := false
	for index := range p.Senders {
		s := &p.Senders[index]
		if s.Sent {
			continue
		}
		c := b.castleByID(s.Castle)
		if c == nil || c.team != b.team {
			s.Sent = true
			continue
		}
		if b.travel(c, target) >= p.Land-now {
			amount := min(s.Amount, b.left(c)-b.headingTo(c, false))
			if amount >= 1 {
				b.send(c, target, amount)
				parts = append(parts, fmt.Sprintf("%d:%d", c.id, amount))
			}
			s.Sent = true
			continue
		}
		committed[c.id] += s.Amount
		open = true
	}
	if len(parts) > 0 {
		*notes = append(*notes, fmt.Sprintf("go>%d@%d ", p.Target, p.Land)+strings.Join(parts, " "))
	}
	if !open {
		return nil
	}
	return p
}

// planStrike plans a strike on the cheapest enemy castle that the (up to strikeCastles) castles nearest it can
// take, their groups landing on one turn. The castles whose walk is that turn's leave now.
func planStrike(b *board, spare map[int]int, ready map[int]bool, notes *[]string) *plan {
	found := false
	bestCost, bestNeed, bestLand := 0, 0, 0
	var bestTarget *castle
	var bestJoining []*castle
	for _, target := range b.enemies {
		var able []*castle
		for _, c := range b.own {
			if ready[c.id] && spare[c.id] >= 1 {
				able = append(able, c)
			}
		}
		if len(able) == 0 {
			continue
		}
		able = byTravel(b, able, target)
		nearest := b.travel(able[0], target)
		var joining []*castle
		land := 0
		total := 0
		for _, c := range able {
			if len(joining) == strikeCastles || b.travel(c, target) > nearest+strikeSpread {
				break
			}
			joining = append(joining, c)
			land = max(land, b.travel(c, target))
			total += spare[c.id]
		}
		need := strikeNeed(b, target, land)
		if need < 1 || total < need {
			continue
		}
		cost := need + 2*land - 3*b.production(target)
		if !found || cost < bestCost {
			found = true
			bestCost, bestNeed, bestLand, bestTarget, bestJoining = cost, need, land, target, joining
		}
	}
	if !found {
		return nil
	}
	now := b.turn.TurnNumber
	p := &plan{Target: bestTarget.id, Land: now + bestLand}
	var parts []string
	open := false
	for _, c := range bestJoining {
		amount := spare[c.id]
		spare[c.id] = 0
		if b.travel(c, bestTarget) >= bestLand {
			b.send(c, bestTarget, amount)
			p.Senders = append(p.Senders, planned{c.id, amount, true})
			parts = append(parts, fmt.Sprintf("%d:%d", c.id, amount))
		} else {
			p.Senders = append(p.Senders, planned{c.id, amount, false})
			parts = append(parts, fmt.Sprintf("%d:%d(wait)", c.id, amount))
			open = true
		}
	}
	finish := ""
	if b.turn.MaxGenerations-now <= bestLand+finishTurns {
		finish = "finish "
	}
	*notes = append(*notes, fmt.Sprintf("%sstrike>%d@%d need %d ", finish, bestTarget.id, p.Land, bestNeed)+strings.Join(parts, " "))
	if !open {
		return nil
	}
	return p
}

// holdNeed is what the castles' groups, landing in land turns, must bring to take the neutral and hold it: every
// known landing on it, then the strongest enemy castle within holdWindow turns of it striking with holdShare of
// what it will have, less what the castle grows while that group walks.
func holdNeed(b *board, target *castle, land, available int) int {
	if b.holdsAfter(target, land, 0, 1.0, true) {
		return 0
	}
	if !b.holdsAfter(target, land, available, 1.0, true) {
		return available + 1
	}
	low, high := 1, available
	for low < high {
		middle := floorDiv(low+high, 2)
		if b.holdsAfter(target, land, middle, 1.0, true) {
			high = middle
		} else {
			low = middle + 1
		}
	}
	grows := int(b.tableValue(production, target.upgrades.Level(production)))
	threat := 0
	for _, enemy := range b.enemies {
		walk := b.travel(enemy, target)
		if walk > holdWindow {
			continue
		}
		threat = max(threat, ceilTimes(enemy.soldiers+b.production(enemy)*land, holdShare)-grows*walk)
	}
	return low + threat
}

// expand takes the cheapest neutral that the castles nearest it can take and hold, for at most maxCost. Returns
// the log note.
func expand(b *board, spare map[int]int, ready map[int]bool, maxCost int) string {
	if len(b.own) == 0 {
		return ""
	}
	found := false
	bestCost, bestNeed := 0, 0
	var bestTarget *castle
	var bestPaying []*castle
	for _, target := range b.neutrals {
		nearestOwn := byTravel(b, b.own, target)
		nearest := b.travel(nearestOwn[0], target)
		var paying []*castle
		land, available := 0, 0
		for _, c := range nearestOwn {
			if len(paying) == neutralCastles || b.travel(c, target) > nearest+neutralSpread {
				break
			}
			if ready[c.id] && spare[c.id] >= 1 {
				paying = append(paying, c)
				land = max(land, b.travel(c, target))
				available += spare[c.id]
			}
		}
		if len(paying) == 0 {
			continue
		}
		// A neutral an enemy castle reaches sooner is the enemy's to take.
		contested := false
		for _, enemy := range b.enemies {
			if b.travel(enemy, target) < land {
				contested = true
			}
		}
		if contested {
			continue
		}
		need := holdNeed(b, target, land, available)
		if need < 1 || need > available {
			continue
		}
		cost := need + 2*land
		if cost > maxCost {
			continue
		}
		if !found || cost < bestCost {
			found = true
			bestCost, bestNeed, bestTarget, bestPaying = cost, need, target, paying
		}
	}
	if !found {
		return ""
	}
	var parts []string
	left := bestNeed
	for _, c := range bestPaying {
		amount := min(left, spare[c.id])
		if amount < 1 {
			break
		}
		b.send(c, bestTarget, amount)
		spare[c.id] -= amount
		left -= amount
		parts = append(parts, fmt.Sprintf("%d:%d", c.id, amount))
	}
	return fmt.Sprintf("take>%d need %d ", bestTarget.id, bestNeed) + strings.Join(parts, " ")
}

// toEnemy is the distance from the castle to the nearest enemy castle.
func toEnemy(b *board, c *castle) float64 {
	nearest := c.distance(b.enemies[0])
	for _, enemy := range b.enemies[1:] {
		nearest = min(nearest, c.distance(enemy))
	}
	return nearest
}

// topped is whether the castle's production is at the top of the table.
func (b *board) topped(c *castle) bool {
	_, more := b.nextUpgradeCost(c, production)
	return !more
}

// play plays one turn: a pure function of the turn and the memory.
func play(_ context.Context, turn islandbattles.Turn) (islandbattles.Result, error) {
	b := newBoard(turn)
	var mem memory
	if len(turn.Memory) > 0 {
		if err := turn.Memory.Decode(&mem); err != nil {
			mem = memory{}
		}
	}
	var notes []string
	short, unheld := reinforce(b, &notes)
	committed := map[int]int{}
	if mem.Strike != nil {
		mem.Strike = carryStrike(b, mem.Strike, committed, &notes)
	}
	// Production first: a castle below firstProduction buys it and keeps the rest.
	spare := map[int]int{}
	early := map[int]bool{}
	ready := map[int]bool{}
	reserve := func(c *castle) int {
		return b.headingTo(c, false) + guard + committed[c.id]
	}
	for _, c := range b.own {
		for c.upgrades.Level(production)+b.boughtLevels(c, production) < firstProduction &&
			b.buyAgain(c, production, reserve(c)) {
			notes = append(notes, fmt.Sprintf("production@%d", c.id))
		}
		early[c.id] = c.upgrades.Level(production)+b.boughtLevels(c, production) >= firstProduction
		ready[c.id] = b.topped(c)
		if early[c.id] {
			spare[c.id] = max(0, b.left(c)-reserve(c))
		}
	}
	for _, pass := range []struct {
		paying  map[int]bool
		maxCost int
	}{{ready, math.MaxInt}, {early, cheapNeutral}} {
		for range 8 {
			if unheld > 0 {
				break
			}
			taken := expand(b, spare, pass.paying, pass.maxCost)
			if taken == "" {
				break
			}
			notes = append(notes, taken)
		}
	}
	// Then the rest of production, and speed once production is at the top.
	for _, c := range b.own {
		if !early[c.id] {
			continue
		}
		keep := b.left(c) - spare[c.id]
		if b.buy(c, production, keep) {
			notes = append(notes, fmt.Sprintf("production@%d", c.id))
		} else if b.topped(c) && c.upgrades.Level(speed) < speedLevel && b.buy(c, speed, keep) {
			notes = append(notes, fmt.Sprintf("speed@%d", c.id))
		}
		spare[c.id] = max(0, b.left(c)-keep)
		ready[c.id] = b.topped(c)
	}
	if mem.Strike == nil && len(b.enemies) > 0 {
		mem.Strike = planStrike(b, spare, ready, &notes)
	}
	front := -1
	if len(b.enemies) > 0 && len(b.own) > 0 {
		frontCastle := b.own[0]
		for _, c := range b.own[1:] {
			if toEnemy(b, c) < toEnemy(b, frontCastle) {
				frontCastle = c
			}
		}
		front = frontCastle.id
		var moves []string
		for _, c := range b.own {
			if c.id == front || !ready[c.id] || spare[c.id] < feedBatch || b.headingTo(c, false) > 0 ||
				toEnemy(b, frontCastle) >= toEnemy(b, c) {
				continue
			}
			b.send(c, frontCastle, spare[c.id])
			moves = append(moves, fmt.Sprintf("%d:%d", c.id, spare[c.id]))
			spare[c.id] = 0
		}
		if len(moves) > 0 {
			notes = append(notes, fmt.Sprintf("feed>%d ", front)+strings.Join(moves, " "))
		}
	}
	producing := 0
	held := 0
	for _, c := range b.own {
		producing += b.production(c)
		held += committed[c.id]
	}
	summary := strings.Join(notes, " ")
	if summary == "" {
		summary = "saving"
	}
	next, err := islandbattles.NewMemory(mem)
	if err != nil {
		return islandbattles.Result{}, err
	}
	return islandbattles.Result{
		Commands: b.commands,
		Memory:   next,
		Logs: []islandbattles.LogLine{islandbattles.Logf(
			"turn %d: %d castles producing %d a turn, front %d, %d held for a strike, %d short under attack (%d unheld); %s",
			turn.TurnNumber, len(b.own), producing, front, held, short, unheld, summary,
		)},
	}, nil
}
