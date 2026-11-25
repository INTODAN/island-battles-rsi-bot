// A sparring opponent that plays like another player's hosted bot ("the opponent"), by rules read off
// 164 server games of league bots against it (2026-11-23/24): rival_mimic. Founded on ori_mimic's code:
// the opponent plays by the same price, need(x) = x + x / 10 + 3, and mostly the same order of rules, so
// what follows is ori_mimic's rules with what the opponent does differently. Checked by replaying every
// turn the opponent played through this bot (league replay) and by playing the league bots that met it
// on the same eight maps (how many real results it gives again).
//
//  0. Opening (one castle, still at production 1): production 2, then neutrals by soldiers plus walk
//     (at most production 3's cost plus rankSlack), then production 3. A spend must leave the castle safe:
//     no enemy castle holds more than need(what is left plus production times its walk at 1 unit a
//     turn, less one turn). When the first neutral is unsafe now but safe with one more turn of
//     soldiers, it waits and buys nothing.
//  1. Defence: as ori_mimic.
//  2. Speed strikes: as ori_mimic (buy the next speed level and strike when that is the cheaper way).
//  3. Per castle: first a lone strike at the neutral ranked first by price plus walk when that is at
//     most its next upgrade's cost; then production 2, 3, 4, speed 2, on the first turn it has the
//     soldiers and stays safe against every enemy castle walking at least 1 unit a turn.
//  4. Attacks: as ori_mimic, the cheapest enemy castle at need(at landing) plus half of what other
//     enemy castles could bring before.
//  5. Neutrals, ranked by price plus walk from our richest castle; a neutral an enemy castle is at least
//     as near is left alone until an enemy group walks at it; one castle alone pays if it can (the
//     nearest that can), else up to four nearest; and it saves for the first one it can't pay rather
//     than take a later one.
//  6. Feeding: a castle at production 4 and speed 2, not the front, not attacked, sends everything to
//     the front when it holds feedAt to feedMax soldiers (whatever its reserve): the opponent feeds in
//     packets of 12 and lets larger stocks stand.
//
// Not reproduced: the opponent attacks much less often than this bot on a quiet board (no enemy group
// walking): its trigger there wasn't found, and holding back made the stand-in lose games the opponent
// won. It also often strikes with what will be there plus one and adds a second small group of 4 to 6.
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
	// need(x) = x + x / needTenth + needFixed: what it sends to take a castle that will hold x.
	needTenth = 10
	needFixed = 3
	// Production and speed levels the upgrade rule buys up to, production first.
	topProduction = 4
	topSpeed      = 2
	// A fully upgraded castle behind the front sends all its soldiers there once it has this many.
	feedAt = 12
	// ... and holds them once it has more than this many.
	feedMax = 15
	// At most this many castles send to one target in a turn.
	mostSenders = 4
	// A castle that would fall is sent what it lacks plus this many.
	defenceSpare = 1
	// A castle buys speed for a strike it could already pay when that saves more than this many.
	speedSaving = 7
	// A neutral is left alone when an enemy castle is no more than this much farther from it than ours.
	contestMargin = 0.0
	// A castle this many turns of production from its next upgrade doesn't help pay for a neutral.
	saveTurns = 6
	// A castle takes a neutral before its next upgrade when the neutral's price plus walk is at most the upgrade's
	// cost plus this many.
	cheapSlack = 0
	// The opening takes a neutral whose soldiers plus walk are at most production 3's cost plus this many.
	rankSlack = 5
	// On turn 1 every spend must hold against enemies walking this many units a turn.
	firstTurnWalk = 1.0
	// An upgrade must leave the castle safe against enemies walking at least this many units a turn.
	threatWalk = 1.0
	// Landing order of this turn's sends, after every group on the board.
	laterID = 1 << 40
	// A walk's turns are rounded up, less this much, so that an exact walk isn't a turn longer.
	walkSlack = 1e-9
	// No team: a neutral castle's colour.
	neutral = 0
	// Where turn 1 has no production-3 level to save for.
	noCost = 1 << 30
)

const (
	production = islandbattles.GenerationAmountUpgrade
	speed      = islandbattles.SpeedUpgrade
)

func main() {
	islandbattles.Main(play)
}

// need is the soldiers it sends to take a castle that will hold this many when they land.
func need(soldiers int) int {
	return soldiers + floorDiv(soldiers, needTenth) + needFixed
}

// floorDiv divides rounding down, also for a negative dividend.
func floorDiv(dividend, divisor int) int {
	quotient := dividend / divisor
	if (dividend%divisor != 0) && ((dividend < 0) != (divisor < 0)) {
		quotient--
	}
	return quotient
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

// purchase is a castle and an upgrade type it bought levels of.
type purchase struct {
	castle      int
	upgradeType islandbattles.UpgradeType
}

// sender is a castle that can send to a target, with its walk there.
type sender struct {
	walk   int
	castle *castle
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
	spent    map[int]int
	bought   map[purchase]int
	// sent is this turn's sends to each castle. A castle is in it once
	// anything was sent to it, or tried, even when the list is empty again.
	sent map[int][]landing
}

// newBoard reads the board from the turn.
func newBoard(turn islandbattles.Turn) *board {
	b := &board{
		turn:   turn,
		team:   int(turn.TeamColor),
		spent:  map[int]int{},
		bought: map[purchase]int{},
		sent:   map[int][]landing{},
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

// table is an upgrade level's value and cost, and false past the top.
func (b *board) table(upgradeType islandbattles.UpgradeType, level int) (float64, int, bool) {
	for _, upgrade := range b.turn.Upgrades {
		if upgrade.Type != upgradeType {
			continue
		}
		if level > upgrade.MaxLevel {
			return 0, 0, false
		}
		for _, entry := range upgrade.Levels {
			if entry.Level == level {
				return entry.Value, int(entry.SoldierCost), true
			}
		}
	}
	return 0, 0, false
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

// level is the castle's level of an upgrade type, counting this turn's purchases.
func (b *board) level(c *castle, upgradeType islandbattles.UpgradeType) int {
	return c.upgrades.Level(upgradeType) + b.bought[purchase{c.id, upgradeType}]
}

// rate is the soldiers the castle produces a turn, counting this turn's purchases.
func (b *board) rate(c *castle) int {
	value, _, found := b.table(production, b.level(c, production))
	if !found {
		return 1
	}
	return int(value)
}

// speedOf is the map units a turn at a speed level.
func (b *board) speedOf(level int) float64 {
	value, _, found := b.table(speed, level)
	if !found {
		return 0.5
	}
	return value
}

// travel is the turns a group sent now from origin takes to land on target (with origin's speed this turn).
func (b *board) travel(origin, target *castle) int {
	level := origin.upgrades.Level(speed)
	if origin.team == b.team {
		level = b.level(origin, speed)
	}
	return walkTurns(origin.distance(target), b.speedOf(level))
}

// threatTravel is the turns an enemy castle's group takes to reach c, as if it walked at least threatWalk units a turn.
func (b *board) threatTravel(enemy, c *castle) int {
	return walkTurns(enemy.distance(c), max(b.speedOf(enemy.upgrades.Level(speed)), threatWalk))
}

// arrival is the turns until a group lands, if nothing stops it.
func (b *board) arrival(g *group) int {
	return walkTurns(g.left, b.speedOf(g.upgrades.Level(speed)))
}

// left is the soldiers the castle hasn't spent this turn.
func (b *board) left(c *castle) int {
	return c.soldiers - b.spent[c.id]
}

// holds is whether no single enemy castle could take the castle at need(what it would find).
func (b *board) holds(c *castle, soldiers, rate int) bool {
	for _, enemy := range b.enemies {
		if enemy.soldiers > need(soldiers+rate*b.threatTravel(enemy, c)) {
			return false
		}
	}
	return true
}

// reserve is the fewest soldiers the castle keeps so that it holds.
func (b *board) reserve(c *castle) int {
	rate := b.rate(c)
	keep := 0
	for _, enemy := range b.enemies {
		// The fewest soldiers x that need(x) covers the enemy castle's, less what grows while it walks.
		fewest := max(0, floorDiv((enemy.soldiers-needFixed)*needTenth, needTenth+1)-1)
		for need(fewest) < enemy.soldiers {
			fewest++
		}
		keep = max(keep, fewest-rate*b.travel(enemy, c))
	}
	return keep
}

// avail is the soldiers the castle can send this turn.
func (b *board) avail(c *castle) int {
	return max(0, b.left(c)-b.reserve(c))
}

// attacked is whether an enemy group is bound for the castle.
func (b *board) attacked(c *castle) bool {
	for _, g := range b.groups {
		if g.destination == c.id && g.team != b.team {
			return true
		}
	}
	return false
}

// send sends soldiers, counting them as spent.
func (b *board) send(origin, target *castle, amount int) {
	b.commands = append(b.commands, islandbattles.SendSoldierGroup(uint(origin.id), uint(target.id), uint(amount)))
	b.spent[origin.id] += amount
	b.sent[target.id] = append(b.sent[target.id], landing{b.travel(origin, target), amount})
}

// buy buys the castle's next level of an upgrade type.
func (b *board) buy(c *castle, upgradeType islandbattles.UpgradeType, cost int) {
	b.commands = append(b.commands, islandbattles.UpgradeCastle(uint(c.id), upgradeType))
	b.spent[c.id] += cost
	b.bought[purchase{c.id, upgradeType}]++
}

// senders are the castles that can send to the target this turn, nearest first.
func (b *board) senders(target *castle) []sender {
	var found []sender
	for _, c := range b.own {
		if c.id != target.id && b.avail(c) >= 1 && !b.attacked(c) {
			found = append(found, sender{b.travel(c, target), c})
		}
	}
	sortSenders(found)
	return found
}

// sortSenders sorts by walk, then castle id.
func sortSenders(senders []sender) {
	slices.SortFunc(senders, func(first, second sender) int {
		if first.walk != second.walk {
			return first.walk - second.walk
		}
		return first.castle.id - second.castle.id
	})
}

// event is a group's landing on a castle.
type event struct {
	turns    int
	id       int
	team     int
	soldiers int
}

// landings are the groups bound for the castle, in the order they land.
func (b *board) landings(c *castle) []event {
	var events []event
	for _, g := range b.groups {
		if g.destination == c.id {
			events = append(events, event{b.arrival(g), g.id, g.team, g.soldiers})
		}
	}
	sortEvents(events)
	return events
}

// sortEvents sorts by landing turn, then id.
func sortEvents(events []event) {
	slices.SortFunc(events, func(first, second event) int {
		if first.turns != second.turns {
			return first.turns - second.turns
		}
		return first.id - second.id
	})
}

// sendSplit sends amount from the chosen castles, nearest first: the farther ones send all, the nearest the rest.
func (b *board) sendSplit(chosen []*castle, target *castle, amount int) []string {
	var parts []string
	remaining := amount
	for index := len(chosen) - 1; index >= 1; index-- {
		c := chosen[index]
		room := b.avail(c)
		give := 0
		if remaining > 1 {
			give = min(room, remaining-1)
		}
		if give >= 1 {
			b.send(c, target, give)
			parts = append(parts, fmt.Sprintf("%d:%d", c.id, give))
			remaining -= give
		}
	}
	if remaining >= 1 {
		b.send(chosen[0], target, remaining)
		parts = append(parts, fmt.Sprintf("%d:%d", chosen[0].id, remaining))
	}
	return parts
}

// atLanding is who holds the target and with how many soldiers in this many turns, after the groups bound for it.
func (b *board) atLanding(target *castle, turns int) (int, int) {
	var events []event
	for _, g := range b.groups {
		if g.destination == target.id {
			events = append(events, event{b.arrival(g), g.id, g.team, g.soldiers})
		}
	}
	for index, sent := range b.sent[target.id] {
		events = append(events, event{sent.turns, laterID + index, b.team, sent.soldiers})
	}
	sortEvents(events)
	owner := target.team
	soldiers := target.soldiers
	rate := 0
	if owner != neutral {
		rate = b.production(target)
	}
	now := 0
	for _, e := range events {
		if e.turns > turns {
			break
		}
		soldiers += rate * (e.turns - now)
		now = e.turns
		switch {
		case e.team == owner:
			soldiers += e.soldiers
		case e.soldiers > soldiers:
			owner = e.team
			soldiers = e.soldiers - soldiers
			rate = 1
		default:
			soldiers -= e.soldiers
		}
	}
	soldiers += rate * (turns - now)
	return owner, soldiers
}

// firstTurn is turn 1: production 2, then cheap neutrals or production 3. Returns the log note.
func firstTurn(b *board) string {
	var notes []string
	for _, c := range b.own {
		// The opening is for a castle that starts the game at production 1.
		if b.level(c, production) != 1 {
			continue
		}
		safe := func(after, rate int) bool {
			for _, enemy := range b.enemies {
				if enemy.soldiers > need(after+rate*(int(math.Ceil(c.distance(enemy)/firstTurnWalk-walkSlack))-1)) {
					return false
				}
			}
			return true
		}
		thirdCost := noCost
		if _, cost, found := b.table(production, 3); found {
			thirdCost = cost
		}
		if _, cost, found := b.table(production, 2); found && b.left(c) >= cost {
			// The first neutral it would take after production 2: when that is unsafe now but safe with one more
			// turn's soldiers, it waits a turn and buys nothing.
			left := b.left(c) - cost
			var first *castle
			firstRank, firstWalk := 0, 0
			for _, n := range b.neutrals {
				walk := b.travel(c, n)
				rank := n.soldiers + walk
				if rank > thirdCost+rankSlack || need(n.soldiers) > left {
					continue
				}
				if first == nil || rank < firstRank || (rank == firstRank && (walk < firstWalk || (walk == firstWalk && n.id < first.id))) {
					first, firstRank, firstWalk = n, rank, walk
				}
			}
			if first != nil && !safe(left-need(first.soldiers), 2) && safe(left+b.production(c)-need(first.soldiers), 2) {
				notes = append(notes, fmt.Sprintf("wait>%d", first.id))
				continue
			}
			b.buy(c, production, cost)
			notes = append(notes, fmt.Sprintf("production2@%d", c.id))
		}
		for {
			left := b.left(c)
			type option struct {
				rank, walk int
				neutral    *castle
				price      int
			}
			var best *option
			for _, n := range b.neutrals {
				if _, tried := b.sent[n.id]; tried {
					continue
				}
				walk := b.travel(c, n)
				price := need(n.soldiers)
				if n.soldiers+walk > thirdCost+rankSlack {
					continue
				}
				if price <= left && safe(left-price, 2) {
					candidate := option{n.soldiers + walk, walk, n, price}
					if best == nil || candidate.rank < best.rank ||
						(candidate.rank == best.rank && (candidate.walk < best.walk ||
							(candidate.walk == best.walk && candidate.neutral.id < best.neutral.id))) {
						best = &candidate
					}
				}
			}
			if best != nil {
				b.send(c, best.neutral, best.price)
				notes = append(notes, fmt.Sprintf("take>%d %d:%d", best.neutral.id, c.id, best.price))
				continue
			}
			if b.level(c, production) == 2 && left >= thirdCost && safe(left-thirdCost, 3) {
				b.buy(c, production, thirdCost)
				notes = append(notes, fmt.Sprintf("production3@%d", c.id))
			}
			break
		}
	}
	return strings.Join(notes, " ")
}

// defend sends help to castles that the groups bound for them would take. Returns the log note.
func defend(b *board) string {
	var notes []string
	for _, c := range b.own {
		events := b.landings(c)
		hostile := false
		for _, e := range events {
			if e.team != b.team {
				hostile = true
			}
		}
		if !hostile {
			continue
		}
		soldiers := c.soldiers
		rate := b.production(c)
		now := 0
		lowest := 0
		fall := -1
		for _, e := range events {
			soldiers += rate * (e.turns - now)
			now = e.turns
			if e.team == b.team {
				soldiers += e.soldiers
			} else {
				soldiers -= e.soldiers
			}
			if soldiers < lowest {
				lowest = soldiers
				if fall < 0 {
					fall = e.turns
				}
			}
		}
		if fall < 0 {
			continue
		}
		missing := -lowest + defenceSpare
		helpers := b.senders(c)
		var chosen []*castle
		total := 0
		count := 0
		for _, helper := range helpers {
			if helper.walk >= fall {
				continue
			}
			if count == mostSenders {
				break
			}
			count++
			chosen = append(chosen, helper.castle)
			total += b.avail(helper.castle)
			if total >= missing {
				break
			}
		}
		if total < missing {
			continue
		}
		notes = append(notes, fmt.Sprintf("help>%d ", c.id)+strings.Join(b.sendSplit(chosen, c, missing), " "))
	}
	return strings.Join(notes, " ")
}

// attackPrice is what it sends at a castle it doesn't hold when its last group lands in this many turns (0:
// already won).
func attackPrice(b *board, target *castle, turns int) int {
	owner, soldiers := b.atLanding(target, turns)
	if owner == b.team {
		return 0
	}
	nearby := 0
	for _, other := range b.enemies {
		if other.id == target.id {
			continue
		}
		if walk := b.travel(other, target); walk < turns {
			nearby += other.soldiers + b.production(other)*(turns-walk)
		}
	}
	return need(soldiers) + floorDiv(nearby, 2)
}

// strike is a strike that speedStrike may choose.
type strike struct {
	total  int
	target *castle
	origin *castle
	price  int
	cost   int
}

// less orders strikes by their total, then target, origin, price and cost.
func (first strike) less(second strike) bool {
	if first.total != second.total {
		return first.total < second.total
	}
	if first.target.id != second.target.id {
		return first.target.id < second.target.id
	}
	if first.origin.id != second.origin.id {
		return first.origin.id < second.origin.id
	}
	if first.price != second.price {
		return first.price < second.price
	}
	return first.cost < second.cost
}

// speedStrike buys a castle's next speed level and strikes with it, when that is the cheaper way to pay.
// Returns the log note.
func speedStrike(b *board) string {
	var candidates []strike
	for _, target := range b.enemies {
		for _, s := range b.senders(target) {
			origin := s.castle
			unitsPerTurn, cost, found := b.table(speed, b.level(origin, speed)+1)
			if !found {
				continue
			}
			price := attackPrice(b, target, walkTurns(origin.distance(target), unitsPerTurn))
			if price < 1 || price+cost > b.avail(origin) {
				continue
			}
			plain := attackPrice(b, target, s.walk)
			if 1 <= plain && plain <= b.avail(origin) && price+cost > plain-speedSaving {
				continue
			}
			candidates = append(candidates, strike{price + cost, target, origin, price, cost})
		}
	}
	if len(candidates) == 0 && len(b.enemies) == 1 {
		candidates = lastCastleStrikes(b, b.enemies[0])
	}
	if len(candidates) == 0 {
		return ""
	}
	best := candidates[0]
	for _, candidate := range candidates[1:] {
		if candidate.less(best) {
			best = candidate
		}
	}
	if best.cost != 0 {
		b.buy(best.origin, speed, best.cost)
	}
	b.send(best.origin, best.target, best.price)
	prefix := ""
	if best.cost != 0 {
		prefix = "speed+"
	}
	return fmt.Sprintf("%sstrike>%d %d:%d", prefix, best.target.id, best.origin.id, best.price)
}

// lastCastleStrikes are strikes at the enemy's last castle with what will be there plus one, when the full price
// is out of reach.
func lastCastleStrikes(b *board, target *castle) []strike {
	var candidates []strike
	for _, s := range b.senders(target) {
		origin := s.castle
		level := b.level(origin, speed)
		for extra := 0; extra <= 1; extra++ {
			unitsPerTurn, cost, found := b.table(speed, level+extra)
			if !found {
				continue
			}
			if extra == 0 {
				cost = 0
			}
			turns := walkTurns(origin.distance(target), unitsPerTurn)
			owner, soldiers := b.atLanding(target, turns)
			if owner == b.team {
				continue
			}
			if avail := b.avail(origin); soldiers+1+cost <= avail && avail < attackPrice(b, target, turns)+cost {
				candidates = append(candidates, strike{soldiers + 1 + cost, target, origin, soldiers + 1, cost})
			}
		}
	}
	return candidates
}

// nextUpgrade is the type and level the upgrade rule buys next for the castle, and false when it buys nothing more.
func nextUpgrade(b *board, c *castle) (islandbattles.UpgradeType, int, bool) {
	if level := b.level(c, production); level < topProduction {
		return production, level + 1, true
	}
	if level := b.level(c, speed); level < topSpeed {
		return speed, level + 1, true
	}
	return "", 0, false
}

// upgrade buys the castle's next upgrades while it can and no single enemy castle could then take it.
func upgrade(b *board, c *castle) string {
	if b.attacked(c) {
		return ""
	}
	var bought []string
	for {
		upgradeType, level, more := nextUpgrade(b, c)
		if !more {
			break
		}
		value, cost, found := b.table(upgradeType, level)
		if !found {
			break
		}
		after := b.left(c) - cost
		if after < 0 {
			break
		}
		rate := b.rate(c)
		if upgradeType == production {
			rate = int(value)
		}
		if !b.holds(c, after, rate) {
			break
		}
		b.buy(c, upgradeType, cost)
		name := "speed"
		if upgradeType == production {
			name = "production"
		}
		bought = append(bought, fmt.Sprintf("%s%d@%d", name, level, c.id))
	}
	return strings.Join(bought, " ")
}

// cheapNeutral sends the castle alone at the neutral ranked first by soldiers plus walk, when that rank is at
// most the cost of the castle's next upgrade and the castle can pay. Returns the log note.
func cheapNeutral(b *board, c *castle) string {
	upgradeType, level, more := nextUpgrade(b, c)
	if !more || b.attacked(c) {
		return ""
	}
	_, cost, found := b.table(upgradeType, level)
	if !found {
		return ""
	}
	var best *castle
	bestRank, bestWalk := 0, 0
	for _, n := range b.neutrals {
		if _, tried := b.sent[n.id]; tried || contested(b, n) {
			continue
		}
		walk := b.travel(c, n)
		rank := max(0, attackPrice(b, n, walk)) + walk
		if rank > cost+cheapSlack {
			continue
		}
		if best == nil || rank < bestRank || (rank == bestRank && (walk < bestWalk || (walk == bestWalk && n.id < best.id))) {
			best, bestRank, bestWalk = n, rank, walk
		}
	}
	if best == nil {
		return ""
	}
	price := attackPrice(b, best, bestWalk)
	if price < 1 || price > b.avail(c) {
		return ""
	}
	b.send(c, best, price)
	return fmt.Sprintf("take>%d %d:%d", best.id, c.id, price)
}

// castlesOf are the senders' castles.
func castlesOf(senders []sender) []*castle {
	castles := make([]*castle, len(senders))
	for index, s := range senders {
		castles[index] = s.castle
	}
	return castles
}

// lastWalk is the longest walk of the senders.
func lastWalk(senders []sender) int {
	longest := senders[0].walk
	for _, s := range senders[1:] {
		longest = max(longest, s.walk)
	}
	return longest
}

// availOf is what the senders can send together.
func availOf(b *board, senders []sender) int {
	total := 0
	for _, s := range senders {
		total += b.avail(s.castle)
	}
	return total
}

// attack strikes the enemy castle with the smallest price once the castles nearest it can pay. Returns the log note.
func attack(b *board) string {
	found := false
	bestPrice := 0
	var bestTarget *castle
	var bestChosen []sender
	for _, target := range b.enemies {
		senders := b.senders(target)
		if len(senders) == 0 {
			continue
		}
		price := 0
		priced := false
		var paidBy []sender
		for count := 1; count <= min(mostSenders, len(senders)); count++ {
			chosen := senders[:count]
			amount := attackPrice(b, target, lastWalk(chosen))
			if !priced {
				price = amount
				priced = true
			}
			if amount >= 1 && availOf(b, chosen) >= amount {
				price = amount
				paidBy = chosen
				break
			}
		}
		if !priced || price < 1 {
			continue
		}
		if !found || price < bestPrice {
			found = true
			bestPrice, bestTarget, bestChosen = price, target, paidBy
		}
	}
	if !found || bestChosen == nil {
		return ""
	}
	parts := b.sendSplit(castlesOf(bestChosen), bestTarget, bestPrice)
	return fmt.Sprintf("strike>%d need %d ", bestTarget.id, bestPrice) + strings.Join(parts, " ")
}

// saving is whether the castle is a few turns from affording its next upgrade.
func saving(b *board, c *castle) bool {
	upgradeType, level, more := nextUpgrade(b, c)
	if !more {
		return false
	}
	_, cost, found := b.table(upgradeType, level)
	if !found {
		return false
	}
	short := cost - b.left(c)
	return 0 < short && short <= saveTurns*b.rate(c)
}

// contested is whether an enemy castle is at least as near the neutral as our nearest castle, and no enemy
// group is bound for it yet.
func contested(b *board, target *castle) bool {
	ours, theirs := math.Inf(1), math.Inf(1)
	for _, c := range b.own {
		ours = min(ours, c.distance(target))
	}
	for _, c := range b.enemies {
		theirs = min(theirs, c.distance(target))
	}
	if theirs > ours+contestMargin {
		return false
	}
	for _, g := range b.groups {
		if g.destination == target.id && g.team != b.team {
			return false
		}
	}
	return true
}

// richest is our castle with the most soldiers left, the first by id among equals.
func richest(b *board) *castle {
	best := b.own[0]
	for _, c := range b.own[1:] {
		if b.left(c) > b.left(best) {
			best = c
		}
	}
	return best
}

// expand takes the neutrals cheapest counting the walk, when the castles nearest them can pay. Returns the log note.
func expand(b *board) string {
	if len(b.own) == 0 {
		return ""
	}
	var notes []string
	type ranked struct {
		rank   int
		target *castle
	}
	order := make([]ranked, 0, len(b.neutrals))
	for _, n := range b.neutrals {
		// Ranked from the castle with the most soldiers left.
		walk := b.travel(richest(b), n)
		order = append(order, ranked{max(0, attackPrice(b, n, walk)) + walk, n})
	}
	slices.SortFunc(order, func(first, second ranked) int {
		if first.rank != second.rank {
			return first.rank - second.rank
		}
		if first.target.soldiers != second.target.soldiers {
			return first.target.soldiers - second.target.soldiers
		}
		return first.target.id - second.target.id
	})
	for _, entry := range order {
		target := entry.target
		if contested(b, target) {
			continue
		}
		everyone := b.senders(target)
		if len(everyone) == 0 {
			break
		}
		var helpers []sender
		for _, s := range everyone {
			if !saving(b, s.castle) {
				helpers = append(helpers, s)
			}
		}
		settled := false
		for count := 1; count <= mostSenders; count++ {
			senders := helpers
			if count == 1 {
				senders = everyone
			}
			if count > len(senders) {
				break
			}
			chosen := senders[:count]
			if count == 1 {
				// One castle alone: the nearest that can pay.
				for _, s := range everyone {
					if price := attackPrice(b, target, s.walk); price >= 1 && b.avail(s.castle) >= price {
						chosen = []sender{s}
						break
					}
				}
			}
			amount := attackPrice(b, target, lastWalk(chosen))
			if amount < 1 {
				settled = true
				break
			}
			if availOf(b, chosen) >= amount {
				parts := b.sendSplit(castlesOf(chosen), target, amount)
				notes = append(notes, fmt.Sprintf("take>%d ", target.id)+strings.Join(parts, " "))
				settled = true
				break
			}
		}
		if !settled {
			// It saves for the first neutral it can't pay yet rather than take a later one.
			break
		}
	}
	return strings.Join(notes, " ")
}

// front is the castle of ours nearest an enemy castle.
func front(b *board) *castle {
	var nearest *castle
	nearestDistance := 0.0
	for _, c := range b.own {
		distance := math.Inf(1)
		for _, enemy := range b.enemies {
			distance = min(distance, c.distance(enemy))
		}
		if nearest == nil || distance < nearestDistance {
			nearest, nearestDistance = c, distance
		}
	}
	return nearest
}

// feed sends everything of the fully upgraded castles behind the front there, if they hold with none.
// Returns the log note.
func feed(b *board) string {
	if len(b.enemies) == 0 || len(b.own) < 2 {
		return ""
	}
	to := front(b)
	var parts []string
	for _, c := range b.own {
		if c.id == to.id ||
			b.level(c, production) < topProduction ||
			b.level(c, speed) < topSpeed ||
			b.attacked(c) ||
			b.left(c) < feedAt || b.left(c) > feedMax {
			continue
		}
		amount := b.left(c)
		b.send(c, to, amount)
		parts = append(parts, fmt.Sprintf("%d:%d", c.id, amount))
	}
	if len(parts) == 0 {
		return ""
	}
	return fmt.Sprintf("feed>%d ", to.id) + strings.Join(parts, " ")
}

// play plays one turn: a pure function of the turn.
func play(_ context.Context, turn islandbattles.Turn) (islandbattles.Result, error) {
	b := newBoard(turn)
	var notes []string
	if len(b.own) == 1 && b.level(b.own[0], production) == 1 {
		notes = append(notes, firstTurn(b))
	} else {
		notes = append(notes, defend(b), speedStrike(b))
		for _, c := range b.own {
			notes = append(notes, cheapNeutral(b, c), upgrade(b, c))
		}
		notes = append(notes, attack(b), expand(b), feed(b))
	}
	producing := 0
	for _, c := range b.own {
		producing += b.production(c)
	}
	said := slices.DeleteFunc(notes, func(note string) bool { return note == "" })
	summary := strings.Join(said, " ")
	if summary == "" {
		summary = "saving"
	}
	return islandbattles.Result{
		Commands: b.commands,
		Logs:     []islandbattles.LogLine{islandbattles.Logf("turn %d: %d castles producing %d a turn; %s", turn.TurnNumber, len(b.own), producing, summary)},
	}, nil
}
