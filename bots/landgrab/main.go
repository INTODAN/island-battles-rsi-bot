// landgrab: land first. Every castle takes the neutrals that pay back soonest before it buys any production level,
// and attacks only as one strike from every castle that can join, landing on one enemy castle on the same turn.
//
// Iteration 42, a founder (its code started from pounce's, whose board helpers, travel times and defence it keeps).
// The main line buys production before it pays any neutral and takes only the neutrals on its side; this bot does
// the opposite:
//
//   - Economy: no production level in a castle while a neutral it would help pay for pays back within
//     neutralHorizon turns (its walk plus the soldiers it costs) and the payers can save up for it soon; then
//     production up to topProduction and speed up to topSpeed, each level only while the castle, with what its
//     neighbours can land in time, still holds what the most dangerous single enemy castle could land on it.
//   - Expansion: every neutral, contested ones too, cheapest payback first, paid together by up to neutralPayers
//     of the nearest castles, sized to hold at landing against what the enemy castles could spare against it.
//   - Defence: pounce's. Every castle keeps home what the enemy castles could spare and land on it; a castle
//     that the groups bound for it would take is sent what it lacks.
//   - Attack: one strike at a time. Every enemy castle is priced exactly at each landing turn up to strikeWalk;
//     the one whose price is lowest next to what all the castles landing by then can spare is struck by all of
//     them, the farthest leaving first, so that every group lands on the same turn (the plan is in memory).
//
// pounce's comment follows.
//
// pounce: a counter-puncher that keeps its soldiers home and strikes a castle the turn its garrison drops.
//
// Iteration 40, a founder (its code started from ori_like's scaffolding, with the
// main line's board helpers copied in). The hosted real opponent takes a castle the
// turn it spends down on an upgrade or a send, its growth counted exactly ("an
// upgrade beside a stocked enemy castle hands it over"); nothing in the league
// punishes that. This bot has no front and stages nothing:
//
//   - Defence: every castle keeps home what the enemy castles could spare and land
//     on it, less its growth on the way, plus what the groups bound for it would
//     take. An enemy castle's spare is its stock above the reserve the main line's
//     rules keep against each of this bot's castles (enemyNeed); the rest is a
//     hoard that never comes; a castle that its landings would take is sent what it lacks
//     from the castles whose groups land in time, which may spend their reserve on
//     it, and else from a castle that buys its next speed level to land in time.
//   - Economy: production up to topProduction, then speed up to topSpeed, in every
//     castle, each level only when the castle still keeps its reserve afterwards,
//     bought before any neutral is paid.
//   - Expansion: neutrals on its own side of the map (no enemy castle reaches them
//     sooner), paid exactly plus neutralExtra plus what the enemy could spare
//     against the capture, by up to two castles; a contested
//     neutral is left to the enemy and struck after it takes it, thin.
//   - Attack: every turn, every enemy castle (and every neutral an enemy group will
//     take) is priced exactly at each landing turn up to punishWalk: its soldiers,
//     growth, groups bound for it, burst, and what the other enemy castles could
//     spare and land on it by then; the castles whose groups land by that turn strike
//     together when what they can spare above their reserve covers it. A castle
//     that just upgraded or sent its stock out is the one that comes out cheap.
//
// ori_like's comment follows.
//
// Ori-like: a sparring opponent built to play like the hosted bot of the real games.
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
	// Production and speed levels every castle buys up to, production first.
	topProduction = 4
	topSpeed      = 2
	// A strike lands within this many turns.
	strikeWalk = 8
	// Soldiers a strike brings over the exact count of what it will meet.
	strikeExtra = 2
	// A neutral castle is taken with this many soldiers over what it will hold.
	neutralExtra = 2
	// The main line's price of a castle that will hold x: x + x/enemyNeedTenth + enemyNeedFixed. Its castles keep
	// what that price says against each of ours, and spare only the rest.
	enemyNeedTenth = 10
	enemyNeedFixed = 3
	// At most this many castles, the nearest, pay for one neutral together.
	neutralPayers = 3
	// A neutral that pays back within this many turns (walk plus the soldiers it costs) is taken before any
	// production level is bought: the payback of production level 3 (20 soldiers for one more a turn).
	neutralHorizon = 20
	// Castles save for such a neutral instead of buying production when this many turns of growth would pay it.
	saveTurns = 10
	// In the game's last this many turns any strike that lands in time is allowed.
	finishTurns = 30
	// Landing order of this turn's sends, after every group on the board.
	laterID = 1 << 40
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

// event is a group's landing on a castle: its turn, id, team and soldiers.
type event struct {
	turns    int
	id       int
	team     int
	soldiers int
}

// purchase is a castle and an upgrade type it bought levels of.
type purchase struct {
	castle      int
	upgradeType islandbattles.UpgradeType
}

// sender is a castle that can send to a target, with its walk there and what it can spare.
type sender struct {
	walk   int
	castle *castle
	spare  int
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
	// sent is this turn's sends to each castle.
	sent map[int][]landing
	// held are the castles that wait to join the strike on a later turn; saving, those that save for a neutral.
	held   map[int]bool
	saving map[int]bool
}

// newBoard reads the board from the turn.
func newBoard(turn islandbattles.Turn) *board {
	b := &board{
		turn:   turn,
		team:   int(turn.TeamColor),
		spent:  map[int]int{},
		bought: map[purchase]int{},
		sent:   map[int][]landing{},
		held:   map[int]bool{},
		saving: map[int]bool{},
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

// burstPotential is the largest burst the castle may order now: 0 while it has debt.
func (b *board) burstPotential(c *castle) int {
	if c.burstDebt > 0 {
		return 0
	}
	value, _, found := b.table(burst, c.upgrades.Level(burst))
	if !found {
		return 0
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

// turnsLeft is the turns of the game left, this one included.
func (b *board) turnsLeft() int {
	return b.turn.MaxGenerations - b.turn.TurnNumber
}

// finishing is whether the game is in its last finishTurns turns.
func (b *board) finishing() bool {
	return b.turnsLeft() <= finishTurns
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

// sortEvents sorts by landing turn, then id.
func sortEvents(events []event) {
	slices.SortFunc(events, func(first, second event) int {
		if first.turns != second.turns {
			return first.turns - second.turns
		}
		return first.id - second.id
	})
}

// landings are the groups bound for the castle, this turn's sends included, in landing order.
func (b *board) landings(c *castle) []event {
	var events []event
	for _, g := range b.groups {
		if g.destination == c.id {
			events = append(events, event{b.arrival(g), g.id, g.team, g.soldiers})
		}
	}
	for index, sent := range b.sent[c.id] {
		events = append(events, event{sent.turns, laterID + index, b.team, sent.soldiers})
	}
	sortEvents(events)
	return events
}

// atLanding is who holds the target and with how many soldiers in this many turns, after the groups bound for it.
func (b *board) atLanding(target *castle, turns int) (int, int) {
	owner := target.team
	soldiers := b.left(target)
	rate := 0
	if owner != neutral {
		rate = b.rate(target)
	}
	now := 0
	for _, e := range b.landings(target) {
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
			rate = b.rate(target)
		default:
			soldiers -= e.soldiers
		}
	}
	soldiers += rate * (turns - now)
	return owner, soldiers
}

// safeOut is the soldiers the castle can send now and still not fall to any landing bound for it.
func (b *board) safeOut(c *castle) int {
	soldiers := b.left(c)
	rate := b.rate(c)
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

// enemyNeed is what the main line's rules send to take a castle that will hold this many: x + x/10 + 3.
func enemyNeed(soldiers int) int {
	return soldiers + floorDiv(soldiers, enemyNeedTenth) + enemyNeedFixed
}

// floorDiv divides rounding down, also for a negative dividend.
func floorDiv(dividend, divisor int) int {
	quotient := dividend / divisor
	if (dividend%divisor != 0) && ((dividend < 0) != (divisor < 0)) {
		quotient--
	}
	return quotient
}

// ownLeft is the soldiers an own castle holds, or what overrides says it will hold after this turn's sends.
func (b *board) ownLeft(c *castle, overrides map[int]int) int {
	if soldiers, found := overrides[c.id]; found {
		return soldiers
	}
	return b.left(c)
}

// enemySpare is what the enemy castle can send: its soldiers above the reserve it keeps so that none of this bot's
// castles (holding what overrides says) could take it at enemyNeed. Its stock beyond that is a hoard.
func (b *board) enemySpare(enemy *castle, overrides map[int]int) int {
	keep := 0
	for _, c := range b.own {
		walk := b.travel(c, enemy)
		if walk >= b.turnsLeft() {
			continue
		}
		soldiers := b.ownLeft(c, overrides)
		fewest := max(0, floorDiv((soldiers-enemyNeedFixed)*enemyNeedTenth, enemyNeedTenth+1)-1)
		for enemyNeed(fewest) < soldiers {
			fewest++
		}
		keep = max(keep, fewest-b.rate(enemy)*walk)
	}
	return max(0, b.left(enemy)-keep)
}

// threat is what the enemy castles (not except) could spare and land on the castle beyond its growth on the way,
// at this production rate, once the castle holds this many; only enemy castles that land before the game ends count.
func (b *board) threat(c *castle, except, rate, holding int) int {
	return b.threatFrom(c, except, rate, holding, false)
}

// threatFrom is threat, or with single what the one most dangerous enemy castle could spare and land.
func (b *board) threatFrom(c *castle, except, rate, holding int, single bool) int {
	overrides := map[int]int{c.id: holding}
	total, largest := 0, 0
	for _, enemy := range b.enemies {
		if enemy.id == except {
			continue
		}
		walk := b.travel(enemy, c)
		if walk >= b.turnsLeft() {
			continue
		}
		land := max(0, b.enemySpare(enemy, overrides)-rate*walk)
		total += land
		largest = max(largest, land)
	}
	if single {
		return largest
	}
	return total
}

// avail is the soldiers the castle can spare: what no landing bound for it needs, less what the enemy castles other
// than except could spare against it once it has sent them.
func (b *board) avail(c *castle, except int) int {
	out := b.safeOut(c)
	rate := b.rate(c)
	fits := func(amount int) bool {
		return out-amount >= b.threat(c, except, rate, b.left(c)-amount)
	}
	low, high := 0, out
	for low < high {
		middle := (low + high + 1) / 2
		if fits(middle) {
			low = middle
		} else {
			high = middle - 1
		}
	}
	return low
}

// senders are the own castles that can spare soldiers for the target, with their walks, nearest first.
func (b *board) senders(target *castle, except int) []sender {
	var found []sender
	for _, c := range b.own {
		if c.id == target.id {
			continue
		}
		if spare := b.avail(c, except); spare >= 1 {
			found = append(found, sender{b.travel(c, target), c, spare})
		}
	}
	slices.SortStableFunc(found, func(first, second sender) int {
		if first.walk != second.walk {
			return first.walk - second.walk
		}
		return first.castle.id - second.castle.id
	})
	return found
}

// sendFrom sends amount from the senders, nearest first. Returns the log parts.
func (b *board) sendFrom(senders []sender, target *castle, amount int) []string {
	var parts []string
	for _, s := range senders {
		if amount <= 0 {
			break
		}
		give := min(s.spare, amount)
		if give < 1 {
			continue
		}
		b.send(s.castle, target, give)
		parts = append(parts, fmt.Sprintf("%d:%d", s.castle.id, give))
		amount -= give
	}
	return parts
}

// defend sends what a castle lacks to the castles that the groups bound for them would take. Returns the log note.
func defend(b *board) string {
	var notes []string
	for _, c := range b.own {
		fall, lack := 0, 0
		for _, e := range b.landings(c) {
			if e.team == b.team {
				continue
			}
			if owner, soldiers := b.atLanding(c, e.turns); owner != b.team {
				fall, lack = e.turns, soldiers+1
				break
			}
		}
		if lack == 0 {
			continue
		}
		// A castle that will certainly fall outweighs a strike that may come: helpers keep only what their own
		// landings need.
		var helpers []sender
		for _, h := range b.own {
			if h.id != c.id && b.travel(h, c) <= fall && b.safeOut(h) >= 1 {
				helpers = append(helpers, sender{b.travel(h, c), h, b.safeOut(h)})
			}
		}
		slices.SortStableFunc(helpers, func(first, second sender) int {
			if first.walk != second.walk {
				return first.walk - second.walk
			}
			return first.castle.id - second.castle.id
		})
		parts := b.sendFrom(helpers, c, lack)
		inTime := 0
		for _, h := range helpers {
			inTime += h.spare
		}
		// Help that walks too slowly: a castle that can pay its next speed level and still give buys it, when that
		// makes its group land by the fall.
		if inTime < lack {
			lack -= inTime
			for _, h := range b.own {
				if lack <= 0 {
					break
				}
				if h.id == c.id || b.travel(h, c) <= fall {
					continue
				}
				level := b.level(h, speed) + 1
				value, cost, found := b.table(speed, level)
				if !found || b.safeOut(h)-cost < 1 || walkTurns(h.distance(c), value) > fall {
					continue
				}
				b.buy(h, speed, cost)
				give := min(b.safeOut(h), lack)
				b.send(h, c, give)
				parts = append(parts, fmt.Sprintf("speed%d@%d %d:%d", level, h.id, h.id, give))
				lack -= give
			}
		}
		notes = append(notes, fmt.Sprintf("help>%d in %d %s", c.id, fall, strings.Join(parts, " ")))
	}
	return strings.Join(notes, " ")
}

// option is a neutral's price: the target, the landing turn, the soldiers it needs, who pays, and its payback.
type option struct {
	target  *castle
	walk    int
	need    int
	senders []sender
	rank    int
}

// better is whether one option ranks before another: lower rank, then the earlier landing, then the lower id.
func (first *option) better(second *option) bool {
	if second == nil {
		return true
	}
	if first.rank != second.rank {
		return first.rank < second.rank
	}
	if first.walk != second.walk {
		return first.walk < second.walk
	}
	return first.target.id < second.target.id
}

// helpFor is what the other enemy castles could spare and land on the target by the turn, once the senders have
// sent all they can: they see a strike the turn after its first group leaves.
func (b *board) helpFor(target *castle, turns int, senders []sender) int {
	overrides := map[int]int{}
	for _, s := range senders {
		overrides[s.castle.id] = b.left(s.castle) - s.spare
	}
	total := 0
	for _, enemy := range b.enemies {
		if enemy.id != target.id && 1+b.travel(enemy, target) <= turns {
			total += b.enemySpare(enemy, overrides)
		}
	}
	return total
}

// plan is the strike under way: the target, the turn number its groups land on, and the castles that join it.
type plan struct {
	Target int   `json:"target"`
	Land   int   `json:"land"`
	From   []int `json:"from"`
}

// memory is what the bot keeps between turns.
type memory struct {
	Strike *plan `json:"strike,omitempty"`
}

// strikePrice is what a strike landing on the target in this many turns must bring, and false when the target
// won't be an enemy's then.
func (b *board) strikePrice(target *castle, walk int, joining []sender) (int, bool) {
	owner, soldiers := b.atLanding(target, walk)
	if owner == b.team || owner == neutral {
		return 0, false
	}
	need := soldiers + strikeExtra + b.helpFor(target, walk, joining)
	if owner == target.team {
		need += b.burstPotential(target)
	}
	return need, true
}

// choose is the strike to start: over every enemy castle and landing turn up to strikeWalk, the one whose price is
// the smallest share of what the castles landing by then can spare. Nil when none can be paid.
func choose(b *board) *plan {
	longest := strikeWalk
	if b.finishing() {
		longest = b.turnsLeft() - 1
	}
	var best *plan
	bestNeed, bestTotal := 0, 1
	for _, target := range b.castles {
		if target.team == b.team {
			continue
		}
		all := b.senders(target, target.id)
		for walk := 1; walk <= longest; walk++ {
			var joining []sender
			total := 0
			for _, s := range all {
				if s.walk <= walk {
					joining = append(joining, s)
					total += s.spare
				}
			}
			if len(joining) == 0 {
				continue
			}
			need, enemy := b.strikePrice(target, walk, joining)
			if !enemy || total < need {
				continue
			}
			// need/total < bestNeed/bestTotal, without division; ties keep the earlier (lower id, shorter walk).
			if best == nil || need*bestTotal < bestNeed*total {
				from := make([]int, 0, len(joining))
				for _, s := range joining {
					from = append(from, s.castle.id)
				}
				best = &plan{target.id, b.turn.TurnNumber + walk, from}
				bestNeed, bestTotal = need, total
			}
		}
	}
	return best
}

// strike carries on the strike under way, or starts the cheapest one: the castles whose walk lands on the plan's
// turn send all they can spare, the nearer ones are held for a later turn. Returns the plan to remember and the log.
func strike(b *board, current *plan) (*plan, string) {
	byID := map[int]*castle{}
	for _, c := range b.castles {
		byID[c.id] = c
	}
	started := false
	if current != nil {
		target, found := byID[current.Target]
		if !found || target.team == b.team || current.Land <= b.turn.TurnNumber {
			current = nil
		} else {
			// Still worth it? What lands by then: the groups already sent, and what the castles still to send can spare.
			walk := current.Land - b.turn.TurnNumber
			var rest []sender
			total := 0
			for _, id := range current.From {
				c, mine := byID[id]
				if !mine || c.team != b.team || b.travel(c, target) > walk {
					continue
				}
				if spare := b.avail(c, target.id); spare >= 1 {
					rest = append(rest, sender{b.travel(c, target), c, spare})
					total += spare
				}
			}
			need, enemy := b.strikePrice(target, walk, rest)
			if !enemy || len(rest) == 0 || total < need {
				note := fmt.Sprintf("strike>%d dropped (need %d, can %d)", target.id, need, total)
				if !enemy {
					note = fmt.Sprintf("strike>%d done", target.id)
				}
				return nil, note
			}
		}
	}
	if current == nil {
		current = choose(b)
		if current == nil {
			return nil, ""
		}
		started = true
	}
	target := byID[current.Target]
	walk := current.Land - b.turn.TurnNumber
	var parts []string
	waiting := 0
	for _, id := range current.From {
		c, mine := byID[id]
		if !mine || c.team != b.team {
			continue
		}
		switch travel := b.travel(c, target); {
		case travel == walk:
			if spare := b.avail(c, target.id); spare >= 1 {
				b.send(c, target, spare)
				parts = append(parts, fmt.Sprintf("%d:%d", c.id, spare))
			}
		case travel < walk:
			b.held[c.id] = true
			waiting++
		}
	}
	verb := "strike"
	if started {
		verb = "new strike"
	}
	note := fmt.Sprintf("%s>%d lands turn %d, sent %s, %d held", verb, target.id, current.Land, strings.Join(parts, " "), waiting)
	if waiting == 0 {
		return nil, note
	}
	return current, note
}

// nearest are the own castles nearest the target, by walk then id, at most count of them.
func (b *board) nearest(target *castle, count int) []*castle {
	sorted := slices.Clone(b.own)
	slices.SortStableFunc(sorted, func(first, second *castle) int {
		if walk := b.travel(first, target) - b.travel(second, target); walk != 0 {
			return walk
		}
		return first.id - second.id
	})
	return sorted[:min(count, len(sorted))]
}

// bound is whether a group, or a send of this turn, is bound for the castle.
func (b *board) bound(target *castle) bool {
	if _, sent := b.sent[target.id]; sent {
		return true
	}
	for _, g := range b.groups {
		if g.destination == target.id {
			return true
		}
	}
	return false
}

// holdAgainst is what the enemy castles could spare and land on the target beyond its growth on the way, once the
// payers hold what overrides says.
func (b *board) holdAgainst(target *castle, overrides map[int]int) int {
	hold := 0
	for _, enemy := range b.enemies {
		hold += max(0, b.enemySpare(enemy, overrides)-b.travel(enemy, target))
	}
	return hold
}

// payback is the turns a neutral takes to pay back what its capture loses: the nearest castle's walk plus the
// soldiers it holds and neutralExtra (a captured castle produces one a turn).
func (b *board) payback(target *castle) int {
	return b.sooner(b.own, target) + b.left(target) + neutralExtra
}

// sooner is the fewest turns in which any of the castles could land on the target.
func (b *board) sooner(castles []*castle, target *castle) int {
	fewest := math.MaxInt
	for _, c := range castles {
		fewest = min(fewest, b.travel(c, target))
	}
	return fewest
}

// neutralOption is the cheapest way to take the neutral castle with up to neutralPayers of the nearest castles, or
// nil.
func neutralOption(b *board, target *castle) *option {
	if b.bound(target) {
		return nil
	}
	var all []sender
	for _, s := range b.senders(target, -1) {
		if !b.held[s.castle.id] {
			all = append(all, s)
		}
	}
	total := 0
	for count := 1; count <= min(neutralPayers, len(all)); count++ {
		total += all[count-1].spare
		walk := all[count-1].walk
		if walk >= b.turnsLeft() {
			break
		}
		_, soldiers := b.atLanding(target, walk)
		overrides := map[int]int{}
		for _, s := range all[:count] {
			overrides[s.castle.id] = b.left(s.castle) - s.spare
		}
		need := soldiers + neutralExtra + b.holdAgainst(target, overrides)
		if total >= need {
			return &option{target, walk, need, all[:count], soldiers + neutralExtra + walk}
		}
	}
	return nil
}

// expand takes the neutral castles that it can pay, soonest payback first, those that pay back within horizon
// turns only. Returns the log note.
func expand(b *board, horizon int) string {
	var notes []string
	for range len(b.neutrals) {
		var best *option
		for _, target := range b.neutrals {
			if b.payback(target) > horizon {
				continue
			}
			if candidate := neutralOption(b, target); candidate != nil && candidate.better(best) {
				best = candidate
			}
		}
		if best == nil {
			break
		}
		parts := b.sendFrom(best.senders, best.target, best.need)
		notes = append(notes, fmt.Sprintf("take>%d payback %d %s", best.target.id, best.rank, strings.Join(parts, " ")))
	}
	return strings.Join(notes, " ")
}

// saving marks the castles that save for a neutral instead of buying production: for each neutral not yet bound
// that pays back within neutralHorizon and that no enemy castle reaches sooner, the fewest of its nearest castles
// (at most neutralPayers) whose stock and saveTurns turns of growth would pay it. Returns the neutrals saved for.
func saving(b *board) []int {
	var targets []int
	for _, target := range b.neutrals {
		if b.bound(target) || b.payback(target) > neutralHorizon || b.sooner(b.enemies, target) < b.sooner(b.own, target) {
			continue
		}
		overrides := map[int]int{}
		can := 0
		var payers []*castle
		for _, c := range b.nearest(target, neutralPayers) {
			payers = append(payers, c)
			overrides[c.id] = 0
			can += b.left(c) + b.rate(c)*saveTurns
			if can >= b.left(target)+neutralExtra+b.holdAgainst(target, overrides) {
				for _, p := range payers {
					b.saving[p.id] = true
				}
				targets = append(targets, target.id)
				break
			}
		}
	}
	return targets
}

// cover is what the other own castles could land on the castle, all they can send safely, in time to answer a
// strike from the nearest enemy castle that they see the turn after it leaves.
func (b *board) cover(c *castle) int {
	soonest := b.sooner(b.enemies, c)
	total := 0
	for _, h := range b.own {
		if h.id != c.id && 1+b.travel(h, c) <= soonest {
			total += b.safeOut(h)
		}
	}
	return total
}

// nextUpgrade is the type and level the castle buys next, and false when it buys nothing more.
func nextUpgrade(b *board, c *castle) (islandbattles.UpgradeType, int, bool) {
	if level := b.level(c, production); level < topProduction {
		if b.saving[c.id] {
			return "", 0, false
		}
		return production, level + 1, true
	}
	if level := b.level(c, speed); level < topSpeed {
		return speed, level + 1, true
	}
	return "", 0, false
}

// upgrade buys the castle's next levels while it keeps its reserve afterwards. Returns the log note.
func upgrade(b *board, c *castle) string {
	if b.held[c.id] {
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
		rate := b.rate(c)
		if upgradeType == production {
			rate = int(value)
		}
		// An upgrade keeps home, with what its neighbours can land in time, what the most dangerous enemy castle
		// could land, not all of them: the sum of every enemy castle's spare grows with the enemy's hoard and would
		// freeze the economy.
		if b.safeOut(c) < cost || b.safeOut(c)-cost+b.cover(c) < b.threatFrom(c, -1, rate, b.left(c)-cost, true) {
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

// play plays one turn: a pure function of the turn and the memory.
func play(_ context.Context, turn islandbattles.Turn) (islandbattles.Result, error) {
	b := newBoard(turn)
	var mem memory
	if len(turn.Memory) > 0 {
		if err := turn.Memory.Decode(&mem); err != nil {
			mem = memory{}
		}
	}
	notes := []string{defend(b)}
	var note string
	mem.Strike, note = strike(b, mem.Strike)
	notes = append(notes, note, expand(b, neutralHorizon))
	saved := saving(b)
	for _, c := range b.own {
		notes = append(notes, upgrade(b, c))
	}
	notes = append(notes, expand(b, math.MaxInt))
	producing, home := 0, 0
	for _, c := range b.own {
		producing += b.rate(c)
		home += b.left(c)
	}
	said := slices.DeleteFunc(notes, func(note string) bool { return note == "" })
	summary := strings.Join(said, " ")
	if summary == "" {
		summary = "waiting"
	}
	next, err := islandbattles.NewMemory(mem)
	if err != nil {
		return islandbattles.Result{}, err
	}
	return islandbattles.Result{
		Commands: b.commands,
		Memory:   next,
		Logs: []islandbattles.LogLine{islandbattles.Logf(
			"turn %d: %d castles producing %d a turn, %d home, saving for %v; %s",
			turn.TurnNumber, len(b.own), producing, home, saved, summary,
		)},
	}, nil
}
