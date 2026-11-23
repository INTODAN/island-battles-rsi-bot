// ori_hold: the hosted bot's rules, and holding what it takes.
//
// Iteration 25, from ori_mimic. The league's oldest lessons are about holding: a
// castle taken with 1 soldier near the enemy falls unless another castle
// reinforces it, and defence is about the landing that takes the castle. The
// hosted bot retakes fresh captures within one to four turns, and ori_mimic's own
// captures face the same. Two changes, everything else is ori_mimic's:
//
//   - Defence also takes help from castles that are themselves under attack, each
//     sending at most what leaves it with a non-negative balance through every
//     landing bound for it.
//   - hold(), run right after defend(): a neutral that one of this bot's groups is
//     bound for, and that playing every landing in order would leave to the
//     enemy, is sent the fewest soldiers that leave it ours after the last landing,
//     from the nearest castle that can pay and lands no later than the first enemy
//     group that would take it.
//
// ori_mimic's comment follows.
//
// A sparring opponent that plays by the rules read off the hosted bot's games of 2026-11-22: ori_mimic.
//
// Its rules come from 17 lobby games (1,437 turns) of the hosted bot's current
// version against safe_hold, each command read off consecutive frames, and from
// the 18 games of the version before it; a replay of every turn the hosted bot
// played, through this bot, measured each rule: it makes the hosted bot's exact
// commands on 75% of the current version's turns. One price runs through
// them: need(x) = x + x / 10 + 3, what it sends to take a castle that will hold
// x when its groups land.
//
//  0. Turn 1: production 2; then the cheapest neutral whose soldiers plus walk
//     are at most the production-3 cost, or production 3; every spend leaves the
//     castle safe against each enemy castle walking 1 unit a turn.
//  1. Defence: a castle that the groups bound for it would take is sent what it
//     lacks plus one, from castles whose groups land before the fall.
//  2. Speed strikes: a castle buys its next speed level and strikes in the same
//     turn when, with that speed, it can pay the strike and the strike at its
//     current speed it can't, or costs speedSaving more than speed and strike.
//     Against a last enemy castle it strikes with what will be there plus one.
//  3. Upgrades, production 2, 3, 4, then speed 2: bought on the first turn the
//     castle has the soldiers, unless an enemy group is bound for it or one enemy
//     castle could then take it at need(what it would find).
//  4. Attacks: the enemy castle with the smallest price, need(its soldiers when
//     the last group lands) plus half of what the other enemy castles could bring
//     before that, launched the first turn the castles nearest it can pay.
//  5. Neutrals, ranked by soldiers plus the shortest walk to them: priced like an
//     attack, paid by up to four castles nearest first; a castle within
//     saveTurns of its next upgrade doesn't help another castle pay.
//  6. Feeding: a castle at production 4 and speed 2 or more, not the front, not
//     under attack, sends all its soldiers to the front once it has feedAt, if
//     it is still safe with none.
//
// Every send keeps the sender's reserve: the fewest soldiers with which no single
// enemy castle could take it at need(what it would find).
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
	feedAt = 10
	// At most this many castles send to one target in a turn.
	mostSenders = 4
	// A castle that would fall is sent what it lacks plus this many.
	defenceSpare = 1
	// A castle buys speed for a strike it could already pay when that saves more than this many.
	speedSaving = 7
	// A castle this many turns of production from its next upgrade doesn't help pay for a neutral.
	saveTurns = 3
	// On turn 1 every spend must hold against enemies walking this many units a turn.
	firstTurnWalk = 1.0
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
		if enemy.soldiers > need(soldiers+rate*b.travel(enemy, c)) {
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

// safeOut is the soldiers an attacked castle can send now and still not fall to any landing bound for it.
func (b *board) safeOut(c *castle) int {
	soldiers := b.left(c)
	rate := b.production(c)
	lowest := soldiers
	now := 0
	for _, e := range b.landings(c) {
		soldiers += rate * (e.turns - now)
		now = e.turns
		if e.team == b.team {
			soldiers += e.soldiers
		} else {
			soldiers -= e.soldiers
		}
		lowest = min(lowest, soldiers)
	}
	return max(0, lowest)
}

// giveOf is the soldiers the castle can send to help: those available, and if attacked no more than it can spare.
func (b *board) giveOf(c *castle) int {
	if b.attacked(c) {
		return min(b.avail(c), b.safeOut(c))
	}
	return b.avail(c)
}

// sendSplit sends amount from the chosen castles, nearest first: the farther ones send all, the nearest the rest.
func (b *board) sendSplit(chosen []*castle, target *castle, amount int, helping bool) []string {
	var parts []string
	remaining := amount
	for index := len(chosen) - 1; index >= 1; index-- {
		c := chosen[index]
		room := b.avail(c)
		if helping {
			room = b.giveOf(c)
		}
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
				if enemy.soldiers >= after+rate*int(math.Ceil(c.distance(enemy)/firstTurnWalk-walkSlack)) {
					return false
				}
			}
			return true
		}
		if _, cost, found := b.table(production, 2); found && b.left(c) >= cost {
			b.buy(c, production, cost)
			notes = append(notes, fmt.Sprintf("production2@%d", c.id))
		}
		thirdCost := noCost
		if _, cost, found := b.table(production, 3); found {
			thirdCost = cost
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
				if left >= thirdCost && n.soldiers+walk > thirdCost {
					continue
				}
				price := need(n.soldiers)
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
		soldiers := b.left(c)
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
		var helpers []sender
		for _, other := range b.own {
			if other.id != c.id && b.giveOf(other) >= 1 {
				helpers = append(helpers, sender{b.travel(other, c), other})
			}
		}
		sortSenders(helpers)
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
			total += b.giveOf(helper.castle)
			if total >= missing {
				break
			}
		}
		if total < missing {
			continue
		}
		notes = append(notes, fmt.Sprintf("help>%d ", c.id)+strings.Join(b.sendSplit(chosen, c, missing, true), " "))
	}
	return strings.Join(notes, " ")
}

// hold sends what it takes to keep a neutral that an enemy group would retake. Returns the log note.
func hold(b *board) string {
	var notes []string
	for _, target := range b.neutrals {
		var landings []int
		ours, enemy := false, false
		for _, g := range b.groups {
			if g.destination == target.id {
				landings = append(landings, b.arrival(g))
				if g.team == b.team {
					ours = true
				} else {
					enemy = true
				}
			}
		}
		sent, tried := b.sent[target.id]
		for _, s := range sent {
			landings = append(landings, s.turns)
		}
		ours = ours || tried
		if !ours || !enemy {
			continue
		}
		slices.Sort(landings)
		last := landings[len(landings)-1]
		if owner, _ := b.atLanding(target, last); owner == b.team || owner == neutral {
			continue
		}
		deadline := 0
		for _, turns := range landings {
			if owner, _ := b.atLanding(target, turns); owner != b.team && owner != neutral {
				deadline = turns
				break
			}
		}
		holdsWith := func(origin *castle, amount int) bool {
			turns := b.travel(origin, target)
			b.sent[target.id] = append(b.sent[target.id], landing{turns, amount})
			owner, _ := b.atLanding(target, max(last, turns))
			b.sent[target.id] = b.sent[target.id][:len(b.sent[target.id])-1]
			return owner == b.team
		}
		for _, s := range b.senders(target) {
			if s.walk > deadline {
				break
			}
			room := b.avail(s.castle)
			if room < 1 || !holdsWith(s.castle, room) {
				continue
			}
			low, high := 1, room
			for low < high {
				middle := (low + high) / 2
				if holdsWith(s.castle, middle) {
					high = middle
				} else {
					low = middle + 1
				}
			}
			b.send(s.castle, target, low)
			notes = append(notes, fmt.Sprintf("hold>%d:%d:%d", target.id, s.castle.id, low))
			break
		}
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
	parts := b.sendSplit(castlesOf(bestChosen), bestTarget, bestPrice, false)
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

// expand takes the neutrals cheapest counting the walk, when the castles nearest them can pay. Returns the log note.
func expand(b *board) string {
	var notes []string
	type ranked struct {
		rank   int
		target *castle
	}
	order := make([]ranked, 0, len(b.neutrals))
	for _, n := range b.neutrals {
		walk := 0
		for index, c := range b.own {
			if turns := b.travel(c, n); index == 0 || turns < walk {
				walk = turns
			}
		}
		order = append(order, ranked{n.soldiers + walk, n})
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
		for count := 1; count <= mostSenders; count++ {
			senders := helpers
			if count == 1 {
				senders = everyone
			}
			if count > len(senders) {
				break
			}
			chosen := senders[:count]
			amount := attackPrice(b, target, lastWalk(chosen))
			if amount < 1 {
				break
			}
			if availOf(b, chosen) >= amount {
				parts := b.sendSplit(castlesOf(chosen), target, amount, false)
				notes = append(notes, fmt.Sprintf("take>%d ", target.id)+strings.Join(parts, " "))
				break
			}
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
			b.left(c) < feedAt ||
			b.reserve(c) > 0 {
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
	if turn.TurnNumber == 1 {
		notes = append(notes, firstTurn(b))
	} else {
		notes = append(notes, defend(b), hold(b), speedStrike(b))
		for _, c := range b.own {
			notes = append(notes, upgrade(b, c))
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
