// juggernaut: one stack, fed by every rear castle, that walks from capture to capture.
//
// Changes proposed from the hosted bot's real games (471 to 648; each mistake's board replayed one turn at a
// time and judged, not measured in a tournament):
//
//   - Strikes and neutral takes are priced to hold: against every enemy castle that could take them back at a speed
//     it can afford, its landings and growth counted; a neutral is paid only by castles that land together.
//   - The stack's guard counts the groups landing on enemy castles; an upgrade keeps what an enemy castle could land
//     after buying speed; a speed upgrade also keeps the strongest enemy stock within 12 turns; nothing is bought
//     while enemy groups worth the cost walk at the castle.
//   - The stack is the castle nearest the enemy (a production-1 capture counts three turns farther), ties by the
//     shortest total distance to the others; never a castle about to fall or one the defence gave up.
//   - Rear castles keep what an enemy castle (or an own castle about to fall) could land before the stack's help,
//     unless that reserve couldn't hold the castle anyway; a castle still building production feeds what it holds
//     beyond twice its next level's cost.
//   - Help is sized for every landing up to guardWalk turns after the first that takes the castle, with a margin
//     only from what helpers hold beyond their own guard; none is sent where it can't save the castle, and a hopeless
//     castle's soldiers walk to the nearest castle that isn't lost; a much stronger helper keeps what the enemy
//     castles near it could land; no stronger castle helps a production-1 capture.
//   - A castle meets an attacking wave with half its size when that stops it long enough to hold.
//
// The log names the stack (stack@C), its strike (smash>T in W need N), feeds (feed>S c:n)
// and every upgrade. pounce's comment follows.
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
	// Production and speed levels every castle buys up to, production first (rear castles buy no speed).
	topProduction = 4
	topSpeed      = 2
	// The stack's speed level, bought after its production.
	stackSpeed = 4
	// A rear castle feeds the stack only with at least this many soldiers.
	feedLeast = 8
	// The stack keeps what the enemy castles within this many turns could land on it.
	guardWalk = 4
	// The stack strikes no further than this many turns, unless the game is finishing.
	smashWalk = 12
	// A strike lands within this many turns, so the target's owner has little time to answer it.
	punishWalk = 6
	// Soldiers a strike brings over the exact count of what it will meet.
	strikeExtra = 2
	// At most this many strikes a turn.
	mostStrikes = 3
	// A neutral castle is taken with this many soldiers over what it will hold.
	neutralExtra = 2
	// The main line's price of a castle that will hold x: x + x/enemyNeedTenth + enemyNeedFixed. Its castles keep
	// what that price says against each of ours, and spare only the rest.
	enemyNeedTenth = 10
	enemyNeedFixed = 3
	// At most this many castles pay for one neutral, their groups landing at most neutralGap turns apart.
	neutralPayers = 2
	neutralGap    = 2
	// A castle within this many map units as near an enemy castle as the stack (or the castle it helps) is is as
	// much in its way, and keeps a reserve against it.
	exposureSlack = 0.5
	// In the game's last this many turns any strike that lands in time is allowed, and contested neutrals too.
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
	origin      int
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
	// lost are the own castles the defence gave up this turn.
	lost map[int]bool
}

// newBoard reads the board from the turn.
func newBoard(turn islandbattles.Turn) *board {
	b := &board{
		turn:   turn,
		team:   int(turn.TeamColor),
		spent:  map[int]int{},
		bought: map[purchase]int{},
		sent:   map[int][]landing{},
		lost:   map[int]bool{},
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
			origin:      int(source.OriginCastleID),
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
	overrides := map[int]int{c.id: holding}
	total := 0
	for _, enemy := range b.enemies {
		if enemy.id == except {
			continue
		}
		walk := b.travel(enemy, c)
		if walk >= b.turnsLeft() {
			continue
		}
		total += max(0, b.enemySpare(enemy, overrides)-rate*walk)
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
	lost := map[int]bool{}
	defer func() {
		// A castle that can't be saved saves its soldiers: they walk to the nearest own castle that isn't lost, when
		// they land there before the enemy does here (a castle that empties early only falls sooner).
		for _, c := range b.own {
			if !lost[c.id] {
				continue
			}
			var to *castle
			for _, o := range b.own {
				if o.id != c.id && !lost[o.id] && (to == nil || c.distance(o) < c.distance(to)) {
					to = o
				}
			}
			if to == nil {
				continue
			}
			first := math.MaxInt
			for _, e := range b.landings(c) {
				if e.team != b.team {
					first = min(first, e.turns)
				}
			}
			if give := b.left(c); give >= feedLeast && first > 1 {
				b.send(c, to, give)
			}
		}
	}()
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
		// Help sized for the first landing that takes the castle loses it to the next: count every enemy landing up to
		// guardWalk turns after it against what the castle holds and grows.
		last := fall
		{
			held, now, against := b.left(c), 0, 0
			for _, e := range b.landings(c) {
				if e.turns > fall+guardWalk {
					break
				}
				last = e.turns
				held += b.rate(c) * (e.turns - now)
				now = e.turns
				if e.team == b.team {
					held += e.soldiers
				} else {
					against += e.soldiers
					lack = max(lack, against-held+1)
				}
			}
		}
		// A castle that will certainly fall outweighs a strike that may come: helpers keep only what their own
		// landings need.
		var helpers []sender
		for _, h := range b.own {
			if b.level(c, production) == 1 && b.left(h) > b.left(c) {
				// A fresh capture that produces 1 isn't worth a stronger castle's soldiers.
				continue
			}
			if h.id != c.id && b.travel(h, c) <= fall && b.safeOut(h) >= 1 {
				// A helper keeps what the enemy castles at least as near it as the castle it helps could land: saving
				// one castle must not open another.
				reserve := 0
				for _, t := range b.threats(h, c) {
					// Only a helper that holds over twice what the castle it helps does keeps a reserve: it is worth more than the
					// castle it would save.
					net := t.stock - b.rate(h)*t.walk
					if t.near && b.left(h) > 2*b.left(c) && net > 0 && t.walk <= guardWalk && t.walk < b.turnsLeft() {
						reserve += net
					}
				}
				if spare := b.safeOut(h) - reserve; spare >= 1 {
					helpers = append(helpers, sender{b.travel(h, c), h, spare})
				}
			}
		}
		slices.SortStableFunc(helpers, func(first, second sender) int {
			if first.walk != second.walk {
				return first.walk - second.walk
			}
			return first.castle.id - second.castle.id
		})
		inTime, later := 0, 0
		for _, h := range helpers {
			inTime += h.spare
			// It grows until its last group that still lands in time (by the last landing counted), and can send that
			// too on later turns.
			later += b.rate(h.castle) * (last - h.walk)
		}
		// Help that walks too slowly: a castle that can pay its next speed level and still give may buy it, when that
		// makes its group land by the fall.
		type speedHelp struct {
			castle *castle
			level  int
			cost   int
		}
		var faster []speedHelp
		possible := inTime + later
		for _, h := range b.own {
			if h.id == c.id || b.travel(h, c) <= fall {
				continue
			}
			level := b.level(h, speed) + 1
			value, cost, found := b.table(speed, level)
			if !found || b.safeOut(h)-cost < 1 || walkTurns(h.distance(c), value) > fall {
				continue
			}
			faster = append(faster, speedHelp{h, level, cost})
			possible += b.safeOut(h) - cost
		}
		var parts []string
		if possible+1 < lack {
			// Help that falls far short of saving the castle is lost with it: send none, and meet the attacker if that
			// holds it. (Short by less, it may still hold: help and growth on later turns come on top of this estimate.)
			if note := intercept(b, c, fall); note != "" {
				parts = append(parts, note)
			} else {
				parts = append(parts, "lost")
				b.lost[c.id] = true
				// Hopeless (help covers under half of it): the castle's own soldiers leave it.
				lost[c.id] = 2*possible < lack
			}
			notes = append(notes, fmt.Sprintf("help>%d in %d %s", c.id, fall, strings.Join(parts, " ")))
			continue
		}
		// Help that only covers this landing leaves the castle to the next one: add what the enemy castles near it
		// could still land, as far as the helpers have it.
		parts = b.sendFrom(helpers, c, lack)
		// The margin comes only from what a helper holds beyond what the enemy castles near it could land.
		if margin := b.guard(c, false); margin > 0 {
			var extra []sender
			for _, h := range helpers {
				if spare := b.safeOut(h.castle) - b.guard(h.castle, false); spare >= 1 {
					extra = append(extra, sender{h.walk, h.castle, spare})
				}
			}
			parts = append(parts, b.sendFrom(extra, c, margin)...)
		}
		lack -= inTime
		margin := b.guard(c, false)
		for _, f := range faster {
			if lack <= 0 {
				break
			}
			b.buy(f.castle, speed, f.cost)
			// Help that buys speed comes with a margin only from what the helper holds beyond its own guard.
			give := min(b.safeOut(f.castle), lack)
			if extra := min(margin, b.safeOut(f.castle)-b.guard(f.castle, false)-give); extra > 0 {
				give += extra
				margin -= extra
			}
			b.send(f.castle, c, give)
			parts = append(parts, fmt.Sprintf("speed%d@%d %d:%d", f.level, f.castle.id, f.castle.id, give))
			lack -= give
		}
		notes = append(notes, fmt.Sprintf("help>%d in %d %s", c.id, fall, strings.Join(parts, " ")))
	}
	return strings.Join(notes, " ")
}

// intercept meets the enemy group that would take the castle with half its soldiers, sent from the castle itself
// toward the group's origin: a clash where the smaller side has half or more stops both groups for the group's
// clash_stop_generations, and costs the attacker as many as were sent. Only when the castle then holds through the
// delayed landing and every other enemy landing by then. Returns the log part, or "".
func intercept(b *board, c *castle, fall int) string {
	var attacker *group
	for _, g := range b.groups {
		if g.destination == c.id && g.team != b.team && b.arrival(g) == fall && (attacker == nil || g.soldiers > attacker.soldiers) {
			attacker = g
		}
	}
	if attacker == nil {
		return ""
	}
	// Groups of the same wave (same origin, same landing) walk together and clash together.
	wave := 0
	for _, g := range b.groups {
		if g.destination == c.id && g.team == attacker.team && g.origin == attacker.origin && b.arrival(g) == fall {
			wave += g.soldiers
		}
	}
	var origin *castle
	for _, o := range b.castles {
		if o.id == attacker.origin {
			origin = o
		}
	}
	if origin == nil || origin.id == c.id {
		return ""
	}
	amount := (wave + 1) / 2
	if amount < 1 || b.left(c) < amount {
		return ""
	}
	stop, _, found := b.table(islandbattles.ClashStopGenerationsUpgrade, attacker.upgrades.Level(islandbattles.ClashStopGenerationsUpgrade))
	if !found || stop < 1 {
		return ""
	}
	landing := fall + int(stop) - 1
	held := b.left(c) - amount + b.rate(c)*landing
	against := wave - amount
	for _, g := range b.groups {
		sameWave := g.team == attacker.team && g.origin == attacker.origin && b.arrival(g) == fall
		if g.destination == c.id && !sameWave && b.arrival(g) <= landing {
			if g.team == b.team {
				held += g.soldiers
			} else {
				against += g.soldiers
			}
		}
	}
	if held <= against {
		return ""
	}
	b.send(c, origin, amount)
	return fmt.Sprintf("meet%d %d:%d", attacker.id, c.id, amount)
}

// option is a strike or a neutral's price: the target, the landing turn, the soldiers it needs and who pays.
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
// sent all they can: they see a strike the turn after it leaves.
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

// strikeOption is the earliest strike on the target that the castles landing by then can pay, or nil.
func strikeOption(b *board, target *castle) *option {
	longest := punishWalk
	if b.finishing() {
		longest = b.turnsLeft() - 1
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
		owner, soldiers := b.atLanding(target, walk)
		if owner == b.team || owner == neutral {
			continue
		}
		need := soldiers + strikeExtra + b.helpFor(target, walk, joining)
		if owner == target.team {
			need += b.burstPotential(target)
		}
		if total < need {
			continue
		}
		return &option{target, walk, need, joining, need + 2*walk - 3*b.rate(target)}
	}
	return nil
}

// strike strikes the enemy castles that the castles landing in time can take, cheapest first. Returns the log note.
func strike(b *board) string {
	var notes []string
	for range mostStrikes {
		var best *option
		for _, target := range b.castles {
			if target.team == b.team {
				continue
			}
			if candidate := strikeOption(b, target); candidate != nil && candidate.better(best) {
				best = candidate
			}
		}
		if best == nil {
			break
		}
		parts := b.sendFrom(best.senders, best.target, best.need)
		notes = append(notes, fmt.Sprintf("pounce>%d in %d need %d %s", best.target.id, best.walk, best.need, strings.Join(parts, " ")))
	}
	return strings.Join(notes, " ")
}

// sooner is the fewest turns in which any of the castles could land on the target.
func (b *board) sooner(castles []*castle, target *castle) int {
	fewest := math.MaxInt
	for _, c := range castles {
		fewest = min(fewest, b.travel(c, target))
	}
	return fewest
}

// neutralOption is the cheapest way to take the neutral castle with up to neutralPayers castles, or nil.
func neutralOption(b *board, target *castle) *option {
	if _, tried := b.sent[target.id]; tried {
		return nil
	}
	for _, g := range b.groups {
		if g.destination == target.id {
			return nil
		}
	}
	if !b.finishing() && b.sooner(b.enemies, target) < b.sooner(b.own, target) {
		return nil
	}
	all := b.senders(target, -1)
	total := 0
	for count := 1; count <= min(neutralPayers, len(all)); count++ {
		total += all[count-1].spare
		walk := all[count-1].walk
		if walk >= b.turnsLeft() || walk-all[0].walk > neutralGap {
			// Payers whose groups land apart take the castle with the first and lose it before the rest arrive.
			break
		}
		_, soldiers := b.atLanding(target, walk)
		// The capture must hold what the enemy castles could spare against it, less its growth on their way.
		overrides := map[int]int{}
		for _, s := range all[:count] {
			overrides[s.castle.id] = b.left(s.castle) - s.spare
		}
		hold := 0
		for _, enemy := range b.enemies {
			back := b.travel(enemy, target)
			growth := 0
			if walk > punishWalk && back <= walk+guardWalk {
				// An enemy castle near the capture grows while a long walk of ours goes on: it meets a bigger answer.
				growth = b.rate(enemy) * walk
			}
			spared := max(0, b.enemySpare(enemy, overrides)+growth-b.rate(target)*back)
			// An enemy castle that can land on the capture as fast as ours did, at a speed it can afford, takes it back
			// with its whole stock, not only what its reserve spares.
			retakes := 0
			free := min(b.left(enemy), b.enemySpare(enemy, overrides))
			for _, option := range b.reaches(enemy, target) {
				if option.walk <= max(guardWalk, walk) && walk+option.walk < b.turnsLeft() {
					stock := free + b.incoming(enemy, walk) + b.rate(enemy)*walk - option.paid
					retakes = max(retakes, stock-b.rate(target)*option.walk)
				}
			}
			hold += max(spared, retakes)
		}
		need := soldiers + neutralExtra + hold
		if total >= need {
			return &option{target, walk, need, all[:count], need + 2*walk}
		}
	}
	return nil
}

// expand takes the neutral castles on this bot's side that it can pay, cheapest first. Returns the log note.
func expand(b *board) string {
	var notes []string
	for range len(b.neutrals) {
		var best *option
		for _, target := range b.neutrals {
			if candidate := neutralOption(b, target); candidate != nil && candidate.better(best) {
				best = candidate
			}
		}
		if best == nil {
			break
		}
		parts := b.sendFrom(best.senders, best.target, best.need)
		notes = append(notes, fmt.Sprintf("take>%d %s", best.target.id, strings.Join(parts, " ")))
	}
	return strings.Join(notes, " ")
}

// nextUpgrade is the type and level the castle buys next, and false when it buys nothing more.
func nextUpgrade(b *board, c *castle) (islandbattles.UpgradeType, int, bool) {
	if level := b.level(c, production); level < topProduction {
		return production, level + 1, true
	}
	if level := b.level(c, speed); level < topSpeed {
		return speed, level + 1, true
	}
	return "", 0, false
}

// upgrade buys the castle's next levels while it keeps its reserve afterwards. Returns the log note.
func upgrade(b *board, c *castle) string {
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
		if b.safeOut(c)-cost < b.threat(c, -1, rate, b.left(c)-cost) {
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

// stackOf is the own castle nearest any enemy castle, by walk, ties by the shortest total distance to the other own
// castles (so feeds walk less), skipping a castle its landings take; nil without enemies.
func stackOf(b *board) *castle {
	walks := map[int]int{}
	best := math.MaxInt
	var places []*castle
	for _, c := range b.own {
		if b.falls(c) && len(b.own) > 1 {
			// A castle its landings take before a feed could land is no place to gather.
			continue
		}
		walk := math.MaxInt
		for _, enemy := range b.enemies {
			walk = min(walk, walkTurns(c.distance(enemy), b.speedOf(1)))
		}
		if b.lost[c.id] {
			// A castle the defence gave up is no place to gather.
			continue
		}
		switch b.level(c, production) {
		case 1:
			// A fresh capture that produces 1 is a poor place to gather: it counts three turns farther.
			walk += 3
		case 2:
			walk++
		}
		walks[c.id] = walk
		best = min(best, walk)
		places = append(places, c)
	}
	var stack *castle
	bestSpread := 0.0
	for _, c := range places {
		if walks[c.id] > best {
			continue
		}
		spread := 0.0
		for _, other := range b.own {
			spread += c.distance(other)
		}
		if stack == nil || spread < bestSpread {
			stack, bestSpread = c, spread
		}
	}
	return stack
}

// threat is a castle that could strike: its walk to a castle and the soldiers it will have.
type threat struct {
	walk    int
	stock   int
	toStack int
	// near is whether c is at most exposureSlack farther from it than the other castle: as much in its way.
	near bool
}

// threats are the enemy castles, with their landings counted, and the own castles that the enemy is about to take
// (with what it will hold there), each with its walk to c.
func (b *board) threats(c, other *castle) []threat {
	var found []threat
	for _, enemy := range b.enemies {
		walk := b.travel(enemy, c)
		near := c.distance(enemy) <= other.distance(enemy)+exposureSlack
		found = append(found, threat{walk, b.left(enemy) + b.incoming(enemy, walk), b.travel(enemy, other), near})
	}
	for _, o := range b.own {
		if o.id == c.id {
			continue
		}
		for _, e := range b.landings(o) {
			if e.team == b.team {
				continue
			}
			if owner, soldiers := b.atLanding(o, e.turns); owner != b.team {
				walk := e.turns + walkTurns(o.distance(c), b.speedOf(1))
				near := c.distance(o) <= other.distance(o)+exposureSlack
				found = append(found, threat{walk, soldiers, e.turns + walkTurns(o.distance(other), b.speedOf(1)), near})
				break
			}
		}
	}
	return found
}

// incoming is the soldiers of the castle's own team that land on it within this many turns.
func (b *board) incoming(c *castle, turns int) int {
	total := 0
	for _, g := range b.groups {
		if g.destination == c.id && g.team == c.team && b.arrival(g) <= turns {
			total += g.soldiers
		}
	}
	return total
}

// guard is what the enemy castles' whole stock within guardWalk turns (the groups landing on them by then counted)
// could land on the castle beyond its growth.
func (b *board) guard(c *castle, speedUp bool) int {
	most := 0
	for _, enemy := range b.enemies {
		// With speedUp, the enemy castle may also buy speed levels and send in the same turn: the best of them within
		// reach counts. An upgrade keeps that (it empties the castle for good); a strike moves the soldiers forward.
		best, paid := 0, 0
		for level := enemy.upgrades.Level(speed); level == enemy.upgrades.Level(speed) || speedUp; level++ {
			if level > enemy.upgrades.Level(speed) {
				_, cost, found := b.table(speed, level)
				if !found {
					break
				}
				paid += cost
			}
			walk := walkTurns(enemy.distance(c), b.speedOf(level))
			if walk <= guardWalk && walk < b.turnsLeft() {
				best = max(best, b.left(enemy)+b.incoming(enemy, walk)-paid-b.rate(c)*walk)
			}
		}
		most += best
	}
	return most
}

// reachOption is a walk an enemy castle could make to a castle, and what the speed levels for it cost.
type reachOption struct {
	walk int
	paid int
}

// reaches are the walks the enemy castle could make to c this turn: at its speed, and at each higher speed level it
// buys first.
func (b *board) reaches(enemy, c *castle) []reachOption {
	var options []reachOption
	base, paid := enemy.upgrades.Level(speed), 0
	for level := base; ; level++ {
		if level > base {
			_, cost, found := b.table(speed, level)
			if !found || paid+cost > b.left(enemy) {
				break
			}
			paid += cost
		}
		options = append(options, reachOption{walkTurns(enemy.distance(c), b.speedOf(level)), paid})
	}
	return options
}

// falls is whether a landing bound for the own castle takes it although every other own castle whose group lands
// by then sent all it can spare.
func (b *board) falls(c *castle) bool {
	for _, e := range b.landings(c) {
		owner, soldiers := b.atLanding(c, e.turns)
		if owner == b.team {
			continue
		}
		help := 0
		for _, other := range b.own {
			if walk := b.travel(other, c); other.id != c.id && walk <= e.turns {
				// What it can spare now, and what it grows and can still send in time.
				help += b.safeOut(other) + b.rate(other)*(e.turns-walk)
			}
		}
		return help <= soldiers
	}
	return false
}

// smash sends the stack at the cheapest target it can take and still keep its guard. Returns the log note.
func smash(b *board, stack *castle) string {
	longest := smashWalk
	if b.finishing() {
		longest = b.turnsLeft() - 1
	}
	spare := b.safeOut(stack) - b.guard(stack, true)
	var best *option
	for _, target := range b.castles {
		if target.team == b.team || target.id == stack.id {
			continue
		}
		walk := b.travel(stack, target)
		if walk > longest {
			continue
		}
		owner, soldiers := b.atLanding(target, walk)
		if owner == b.team {
			continue
		}
		need := soldiers + strikeExtra
		if owner != neutral {
			need += b.burstPotential(target)
		} else if target.team == neutral && b.sooner(b.enemies, target) < walk {
			continue
		}
		for _, enemy := range b.enemies {
			if enemy.id == target.id {
				continue
			}
			// At the speed it can afford, an enemy castle either helps the target before the landing (its stock, less
			// the levels) or takes the capture back (what it will hold by then, its
			// landings and growth counted, less the levels and the capture's growth) within guardWalk turns of it, or
			// as fast as our strike walked there: the price holds against the worse.
			// An enemy castle sends only what it can spare: the rest it keeps home against our castles (the stack
			// above all), so a big stack makes its neighbours' answers small.
			free := min(b.left(enemy), b.enemySpare(enemy, nil))
			helps, retakes := 0, 0
			for _, option := range b.reaches(enemy, target) {
				if owner != neutral && 1+option.walk <= walk {
					helps = max(helps, free+b.incoming(enemy, walk-option.walk-1)-option.paid)
				} else if option.walk <= max(guardWalk+2, walk) && walk+option.walk < b.turnsLeft() {
					// A retake that lands after the game's end doesn't count.
					stock := free + b.incoming(enemy, walk) + b.rate(enemy)*walk - option.paid
					retakes = max(retakes, stock-b.rate(target)*option.walk)
				}
			}
			need += max(helps, retakes)
		}
		if need > spare {
			continue
		}
		candidate := &option{target, walk, need, nil, need + 2*walk}
		if candidate.better(best) {
			best = candidate
		}
	}
	if best == nil {
		return ""
	}
	b.send(stack, best.target, best.need)
	return fmt.Sprintf("smash>%d in %d need %d", best.target.id, best.walk, best.need)
}

// build buys the castle's next levels: production for every castle, then speed for the stack, each only while the
// castle still holds through its landings (and the stack its guard). Returns the log note.
func build(b *board, c *castle, isStack bool) string {
	var bought []string
	for {
		upgradeType, level := production, b.level(c, production)+1
		if level > topProduction {
			if !isStack {
				break
			}
			upgradeType, level = speed, b.level(c, speed)+1
			if level > stackSpeed {
				break
			}
		}
		_, cost, found := b.table(upgradeType, level)
		if !found {
			break
		}
		coming := 0
		for _, g := range b.groups {
			if g.destination == c.id && g.team != b.team {
				coming += g.soldiers
			}
		}
		if coming >= cost {
			// Enemy groups worth the upgrade walk at the castle: it buys nothing until they have landed.
			break
		}
		var keep int
		if isStack {
			keep = b.guard(c, true)

			// For speed, the stack keeps at least what the strongest enemy castle within three times guardWalk could bring.
			for _, enemy := range b.enemies {
				if upgradeType != speed {
					break
				}
				for _, option := range b.reaches(enemy, c) {
					if option.walk <= 3*guardWalk {
						keep = max(keep, b.left(enemy)+b.incoming(enemy, option.walk)-option.paid)
					}
				}
			}
		} else {
			// A rear castle keeps what the enemy castles could spare against it, at its new rate.
			rate := b.rate(c)
			if upgradeType == production {
				value, _, _ := b.table(production, level)
				rate = int(value)
			}
			keep = b.threat(c, -1, rate, b.left(c)-cost)
		}
		if b.safeOut(c)-cost < keep {
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

// feedStack sends the stack what every rear castle's landings don't need, when no enemy group is bound for it.
func feedStack(b *board, stack *castle) string {
	var moves []string
	// A stack that holds less than its guard is fed by every rear castle, upgraded or not.
	weak := b.left(stack) < b.guard(stack, true)
	for _, c := range b.own {
		if c.id == stack.id {
			continue
		}
		if !weak && b.level(c, production) < topProduction {
			// A castle still building its production feeds only what it holds beyond twice its next level's cost.
			_, cost, found := b.table(production, b.level(c, production)+1)
			if !found || b.safeOut(c) < 2*cost {
				continue
			}
		}
		bound := false
		for _, g := range b.groups {
			if g.destination == c.id && g.team != b.team {
				bound = true
			}
		}
		// Keep what an enemy castle (or an own castle about to fall to the enemy) that lands on this one before the
		// stack's help could would take.
		keep := 0
		back := b.travel(stack, c)
		for _, t := range b.threats(c, stack) {
			if t.walk < back && t.walk < b.turnsLeft() {
				keep = max(keep, t.stock-b.rate(c)*t.walk+1)
			}
		}
		if keep > b.left(c) {
			// A reserve the castle couldn't hold with anyway saves nothing: its soldiers fight at the stack.
			keep = 0
		}
		if give := b.safeOut(c) - keep; !bound && give >= feedLeast && back < b.turnsLeft() {
			b.send(c, stack, give)
			moves = append(moves, fmt.Sprintf("%d:%d", c.id, give))
		}
	}
	if len(moves) == 0 {
		return ""
	}
	return fmt.Sprintf("feed>%d %s", stack.id, strings.Join(moves, " "))
}

// play plays one turn: a pure function of the turn.
func play(_ context.Context, turn islandbattles.Turn) (islandbattles.Result, error) {
	b := newBoard(turn)
	notes := []string{defend(b)}
	stack := stackOf(b)
	if stack != nil {
		notes = append(notes, fmt.Sprintf("stack@%d", stack.id))
		notes = append(notes, smash(b, stack))
	}
	for _, c := range b.own {
		notes = append(notes, build(b, c, stack != nil && c.id == stack.id))
	}
	notes = append(notes, expand(b))
	if stack != nil {
		notes = append(notes, feedStack(b, stack))
	}
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
	return islandbattles.Result{
		Commands: b.commands,
		Logs: []islandbattles.LogLine{islandbattles.Logf(
			"turn %d: %d castles producing %d a turn, %d home; %s", turn.TurnNumber, len(b.own), producing, home, summary,
		)},
	}, nil
}
