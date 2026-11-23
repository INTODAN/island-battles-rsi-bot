// juggernaut: one stack, fed by every rear castle, that walks from capture to capture.
//
// Iteration 42, a founder (its code started from pounce, whose board helpers it keeps). A real
// game lost on claw (game 482) was won by a bot whose rear castles kept a few soldiers and fed
// one front castle to 274, which bought speed and struck. No line of the league plays so:
//
//   - Economy: rear castles buy production only, up to topProduction, and send everything
//     their landings don't need to the stack; the stack buys production, then speed up to
//     stackSpeed (speed 4), so its strikes are short at any distance.
//   - Defence: no reserve in the rear. The stack is the reserve: it keeps what the enemy
//     castles' whole stock within guardWalk turns could land on it, less its growth.
//   - Attack: only from the stack, at the target with the lowest price plus twice the walk,
//     priced at its exact count at landing, its burst, and the whole stock of every other
//     enemy castle that could land on it in time (no castle is assumed to keep a reserve).
//     The capture is nearer the enemy, so it is the next stack, and the rear feeds it.
//   - Expansion: pounce's: the neutrals on its own side, exactly plus a margin.
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
	// At most this many castles pay for one neutral.
	neutralPayers = 2
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
		if walk >= b.turnsLeft() {
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
			hold += max(0, b.enemySpare(enemy, overrides)-b.rate(target)*b.travel(enemy, target))
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

// stackOf is the own castle nearest any enemy castle, by walk, ties by id; nil without enemies.
func stackOf(b *board) *castle {
	var stack *castle
	best := math.MaxInt
	for _, c := range b.own {
		for _, enemy := range b.enemies {
			if walk := walkTurns(c.distance(enemy), b.speedOf(1)); walk < best || (walk == best && c.id < stack.id) {
				stack, best = c, walk
			}
		}
	}
	return stack
}

// guard is what the enemy castles' whole stock within guardWalk turns could land on the castle beyond its growth.
func (b *board) guard(c *castle) int {
	most := 0
	for _, enemy := range b.enemies {
		walk := b.travel(enemy, c)
		if walk <= guardWalk && walk < b.turnsLeft() {
			most += max(0, b.left(enemy)-b.rate(c)*walk)
		}
	}
	return most
}

// smash sends the stack at the cheapest target it can take and still keep its guard. Returns the log note.
func smash(b *board, stack *castle) string {
	longest := smashWalk
	if b.finishing() {
		longest = b.turnsLeft() - 1
	}
	spare := b.safeOut(stack) - b.guard(stack)
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
			for _, enemy := range b.enemies {
				if enemy.id != target.id && 1+b.travel(enemy, target) <= walk {
					need += b.left(enemy)
				}
			}
		} else if target.team == neutral && b.sooner(b.enemies, target) < walk {
			continue
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
		keep := 0
		if isStack {
			keep = b.guard(c)
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
	for _, c := range b.own {
		if c.id == stack.id || b.level(c, production) < topProduction {
			continue
		}
		bound := false
		for _, g := range b.groups {
			if g.destination == c.id && g.team != b.team {
				bound = true
			}
		}
		if give := b.safeOut(c); !bound && give >= feedLeast {
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
