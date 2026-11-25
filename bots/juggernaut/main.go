// juggernaut, corrected on its real games' mistakes.
//
// The hosted bot's server games against other players' bots were studied for their three costliest mistakes each,
// and every mistake's board was given to juggernaut alone (it has no memory, so one turn reproduces it exactly). These
// rules stop it repeating them, each grounded in the timing of landings and what nearby enemy castles can send:
//
//   - Captures hold (holdMargin, holdNeed, plan): smash and expand price a capture so that, for holdWalk turns after
//     its last landing, it holds against the whole stock of any one enemy castle that could land on it by then (its
//     production until it leaves and the groups bound for it), with the help of the own castles within helpWalk turns;
//     a castle that pays is no help at a turn it holds less than now, and every payer must hold too. A neutral is not
//     taken by groups that an enemy castle, seeing the first leave, could land between.
//   - Feeds keep a garrison (feedThreats, feedReserve, feedGive): a rear castle keeps what the enemy castles that can
//     land on it before the stack's help could spare; nothing is fed to a stack that falls before the feed lands,
//     unless this turn's feeds together take it back.
//   - The stack stands (pickStack, standsFed, stackBefore): the front-most castle that still holds with this turn's
//     feeds; at the same front one holding far more stays, then the more central, then the larger.
//   - Upgrades don't empty a castle (enemyBound, reachFalls, largestInReach): no upgrade while enemy groups walk in, no
//     purchase that makes a castle fall to the enemy castles in reach (counting the speed they can afford), and a
//     threatened stack buys no speed.
//   - Defence saves what it can (rescue, holdsWith, helpSpare, intercept): help is sized to hold through every
//     landing up to holdBeyond turns after the fall, a castle no help can hold gets none, a helper keeps a reserve
//     against the strongest enemy castle near it, and a lone castle meets the group that would take it halfway when
//     the clash stops it long enough.
//
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
	// A capture must hold for this many turns after it lands against any one enemy castle's whole stock, and so must
	// the castles that pay for it until then.
	holdWalk = 4
	// The own castles within this many turns of a capture help it hold.
	helpWalk = 4
	// At most this many castles pay for one neutral.
	neutralPayers = 2
	// In the game's last this many turns any strike that lands in time is allowed, and contested neutrals too.
	finishTurns = 30
	// Landing order of this turn's sends, after every group on the board.
	laterID = 1 << 40
	// A walk's turns are rounded up, less this much, so that an exact walk isn't a turn longer.
	walkSlack = 1e-9
	// Help holds a castle through the landings up to this many turns after the one that would take it.
	holdBeyond = 4
	// Help that leaves a castle short by at most this many is sent all the same: the enemy takes it with next to
	// nothing, and the next turn retakes it.
	fallShort = 3
	// A helper keeps this many quarters of what the strongest enemy castle near it could land on it.
	helperKeep = 3
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

// defend saves the own castles that the groups bound for them would take. A castle is helped only when the help
// that lands in time holds it through the landings bound for it, and helpers give only what they can spare beside
// the enemy castles near them; a castle that help can't save meets the group that takes it halfway, when a clash
// stops that group long enough for the castle to grow past it. The log names each castle helped (help>C in T and
// who gives what), met (meet>G from C) or left to fall (lost>C in T short, with what help there was).
func defend(b *board) string {
	var notes []string
	for _, c := range b.own {
		fall, taker := 0, 0
		for _, e := range b.landings(c) {
			if e.team == b.team {
				continue
			}
			if owner, _ := b.atLanding(c, e.turns); owner != b.team {
				fall, taker = e.turns, e.id
				break
			}
		}
		if fall == 0 {
			continue
		}
		parts, saved := b.rescue(c, fall)
		if saved {
			notes = append(notes, fmt.Sprintf("help>%d in %d %s", c.id, fall, strings.Join(parts, " ")))
			continue
		}
		if note := b.intercept(c, taker); note != "" {
			notes = append(notes, note)
			continue
		}
		notes = append(notes, fmt.Sprintf("lost>%d in %d short %s", c.id, fall, strings.Join(parts, " ")))
	}
	return strings.Join(notes, " ")
}

// rescuer is an own castle that can land help on a castle in time: its walk, what it gives at most, and the speed
// level it buys first to land in time (0 for none) and that level's cost.
type rescuer struct {
	castle *castle
	walk   int
	spare  int
	level  int
	cost   int
}

// helpSpare is what an own castle can give to save another, after paying cost for a speed level: what its own
// landings don't need, less three quarters of what the strongest enemy castle within guardWalk turns could land on
// it beyond its growth, so that saving one castle doesn't hand over the helper. A helper that can't hold against
// that castle anyway gives all its landings don't need.
func (b *board) helpSpare(h *castle, cost int) int {
	out := b.safeOut(h) - cost
	keep := 0
	for _, enemy := range b.enemies {
		if walk := b.travel(enemy, h); walk <= guardWalk && walk < b.turnsLeft() {
			keep = max(keep, b.left(enemy)-b.rate(h)*walk)
		}
	}
	if b.left(h)-cost <= keep {
		return max(0, out)
	}
	return max(0, min(out, b.left(h)-cost-keep*helperKeep/4))
}

// holdsWith is whether the castle, holding start soldiers now, is still own at the end of every turn that one of the
// events lands in (groups land in id order, so a castle taken and retaken in one turn is held).
func (b *board) holdsWith(c *castle, start int, events []event) bool {
	sortEvents(events)
	owner, soldiers, rate, now := b.team, start, b.rate(c), 0
	for index, e := range events {
		soldiers += rate * (e.turns - now)
		now = e.turns
		switch {
		case e.team == owner:
			soldiers += e.soldiers
		case e.soldiers > soldiers || (e.soldiers == soldiers && owner == b.team):
			// An even fight leaves the castle at 0: counted as lost, so that help keeps a margin of one.
			owner, soldiers = e.team, e.soldiers-soldiers
		default:
			soldiers -= e.soldiers
		}
		if (index == len(events)-1 || events[index+1].turns != e.turns) && owner != b.team {
			return false
		}
	}
	return true
}

// rescue sends the castle, which falls in fall turns, the least help that lands by then and holds it through every
// landing bound for it, nearest helpers first. It sends nothing when the help can't hold it. Returns the log parts
// and whether it was saved.
func (b *board) rescue(c *castle, fall int) ([]string, bool) {
	var found []rescuer
	for _, h := range b.own {
		if h.id == c.id {
			continue
		}
		// Help that an enemy group bound elsewhere meets on its way doesn't land.
		if walk := b.travel(h, c); walk <= fall {
			if b.crossedBy(h, c, b.speedOf(b.level(h, speed))) {
				continue
			}
			if spare := b.helpSpare(h, 0); spare >= 1 {
				found = append(found, rescuer{h, walk, spare, 0, 0})
			}
			continue
		}
		// Help that walks too slowly may buy its next speed level to land in time.
		level := b.level(h, speed) + 1
		value, cost, ok := b.table(speed, level)
		if !ok {
			continue
		}
		walk := walkTurns(h.distance(c), value)
		if walk > fall || b.crossedBy(h, c, value) {
			continue
		}
		if spare := b.helpSpare(h, cost); spare >= 1 {
			found = append(found, rescuer{h, walk, spare, level, cost})
		}
	}
	slices.SortStableFunc(found, func(first, second rescuer) int {
		if first.level != second.level {
			return first.level - second.level
		}
		if first.walk != second.walk {
			return first.walk - second.walk
		}
		return first.castle.id - second.castle.id
	})
	var base []event
	for _, e := range b.landings(c) {
		if e.turns <= fall+holdBeyond {
			base = append(base, e)
		}
	}
	latest := 0
	for _, e := range base {
		latest = max(latest, e.turns)
	}
	// holds is whether the castle, extra soldiers richer, holds when the first count helpers send their spare now
	// (the last of them only last), and, when later is set, every helper sends what it produces each turn after.
	holds := func(count, last, extra int, later bool) bool {
		events := slices.Clone(base)
		for index, r := range found[:count] {
			give := r.spare
			if index == count-1 {
				give = last
			}
			events = append(events, event{r.walk, laterID + 1000 + index, b.team, give})
		}
		if later {
			for index, r := range found {
				for turns := r.walk + 1; turns <= latest; turns++ {
					events = append(events, event{turns, laterID + 2000 + index, b.team, b.rate(r.castle)})
				}
			}
		}
		return b.holdsWith(c, b.left(c)+extra, events)
	}
	var could []string
	for _, r := range found {
		could = append(could, fmt.Sprintf("%d:%d", r.castle.id, r.spare))
	}
	if len(found) == 0 {
		return could, false
	}
	all := found[len(found)-1].spare
	count, low := len(found), all
	switch {
	case holds(count, all, 0, true):
		// The least help now, nearest first, that holds it without counting what the helpers produce later; all
		// of it when none does.
		least := 0
		for least < len(found) && !holds(least+1, found[least].spare, 0, false) {
			least++
		}
		if least < len(found) {
			count = least + 1
			high := found[least].spare
			low = 1
			for low < high {
				middle := (low + high) / 2
				if holds(count, middle, 0, false) {
					high = middle
				} else {
					low = middle + 1
				}
			}
		}
	case holds(count, all, fallShort, true):
		// Short by so little that the enemy takes it with next to nothing: all the help goes, and the castle is
		// retaken next.
	default:
		// No help holds it: none is sent.
		return could, false
	}
	var parts []string
	for index, r := range found[:count] {
		give := r.spare
		if index == count-1 {
			give = low
		}
		if r.level > 0 {
			b.buy(r.castle, speed, r.cost)
			parts = append(parts, fmt.Sprintf("speed%d@%d", r.level, r.castle.id))
		}
		b.send(r.castle, c, give)
		parts = append(parts, fmt.Sprintf("%d:%d", r.castle.id, give))
	}
	return parts, true
}

// intercept sends the castle's own soldiers at the group that would take it, back along its way, when they are at
// least half of it: the clash stops it for its clash-stop turns, and the castle grows past what is left of it.
// Returns the log note, empty when that doesn't hold the castle.
func (b *board) intercept(c *castle, taker int) string {
	var source *islandbattles.SoldierGroup
	for index := range b.turn.Generation.SoldierGroups {
		if g := &b.turn.Generation.SoldierGroups[index]; int(g.ID) == taker {
			source = g
		}
	}
	if source == nil || int(source.OriginCastleID) == c.id {
		return ""
	}
	var origin *castle
	for _, other := range b.castles {
		if other.id == int(source.OriginCastleID) {
			origin = other
		}
	}
	if origin == nil {
		return ""
	}
	soldiers := int(source.Soldiers)
	amount := (soldiers + 1) / 2
	if amount < 1 || amount > b.safeOutBefore(c, taker) {
		return ""
	}
	// Where they meet: head on, within the clash radius, and how long the group then takes to land.
	theirs := b.speedOf(source.Upgrades.Level(speed))
	ours := b.speedOf(b.level(c, speed))
	radius := max(source.ClashRadius, 0.25)
	away := hypot(source.X-c.x, source.Y-c.y)
	meet := max(0, away-radius) / (theirs + ours)
	if b.crossed(c, origin, ours, meet, source.ID) {
		return ""
	}
	clashTurn := int(math.Floor(meet)) + 1
	stop, _, found := b.table(islandbattles.ClashStopGenerationsUpgrade, source.Upgrades.Level(islandbattles.ClashStopGenerationsUpgrade))
	if !found {
		stop = 1
	}
	rest := max(0, away-theirs*meet-radius/2)
	// One turn less than the walk, so that a group stopped late in a turn is not counted a turn later than it is.
	lands := clashTurn + int(stop) - 1 + walkTurns(rest, theirs) - 1
	var events []event
	for _, e := range b.landings(c) {
		if e.id == taker {
			if soldiers-amount > 0 {
				events = append(events, event{max(e.turns, lands), e.id, e.team, soldiers - amount})
			}
			continue
		}
		events = append(events, e)
	}
	if !b.holdsWith(c, b.left(c)-amount, events) {
		return ""
	}
	// Sent at the origin, but it never lands there: it isn't counted as a landing.
	b.commands = append(b.commands, islandbattles.SendSoldierGroup(uint(c.id), uint(origin.id), uint(amount)))
	b.spent[c.id] += amount
	return fmt.Sprintf("meet>%d from %d %d:%d", taker, c.id, c.id, amount)
}

// crossed is whether another enemy group, walking on to its castle, comes within clash reach of a group sent now
// from the castle toward origin at this speed before the meeting time.
func (b *board) crossed(c, origin *castle, ours, meet float64, taker uint) bool {
	return b.crossedExcept(c, origin, ours, meet, func(other *islandbattles.SoldierGroup) bool { return other.ID == taker })
}

// crossedBy is whether a group sent now from the castle to the target at this speed meets an enemy group bound
// elsewhere.
func (b *board) crossedBy(from, target *castle, ours float64) bool {
	return b.crossedExcept(from, target, ours, from.distance(target)/ours, func(other *islandbattles.SoldierGroup) bool {
		return int(other.DestinationCastleID) == target.id
	})
}

// crossedExcept is crossed, leaving out the enemy groups that skip says.
func (b *board) crossedExcept(c, origin *castle, ours, meet float64, skip func(*islandbattles.SoldierGroup) bool) bool {
	away := c.distance(origin)
	if away == 0 {
		return false
	}
	dx, dy := (origin.x-c.x)/away, (origin.y-c.y)/away
	for index := range b.turn.Generation.SoldierGroups {
		other := &b.turn.Generation.SoldierGroups[index]
		if skip(other) || int(other.TeamColor) == b.team {
			continue
		}
		var target *castle
		for _, candidate := range b.castles {
			if candidate.id == int(other.DestinationCastleID) {
				target = candidate
			}
		}
		if target == nil {
			continue
		}
		left := hypot(target.x-other.X, target.y-other.Y)
		theirs := b.speedOf(other.Upgrades.Level(speed))
		ox, oy := 0.0, 0.0
		if left > 0 {
			ox, oy = (target.x-other.X)/left, (target.y-other.Y)/left
		}
		const samples = 64
		for step := 0; step <= samples; step++ {
			t := meet * float64(step) / samples
			if theirs*t > left {
				break
			}
			walked := theirs * t
			if hypot(c.x+dx*ours*t-other.X-ox*walked, c.y+dy*ours*t-other.Y-oy*walked) <= max(other.ClashRadius, 0.25) {
				return true
			}
		}
	}
	return false
}

// safeOutBefore is what the castle can send now and still hold every landing before the given group's.
func (b *board) safeOutBefore(c *castle, taker int) int {
	soldiers := b.left(c)
	rate := b.rate(c)
	lowest := soldiers
	now := 0
	for _, e := range b.landings(c) {
		if e.id == taker {
			break
		}
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
		// An enemy castle that sees the first group leave can land before the last one: it takes what the first left.
		if !b.finishing() && 1+b.sooner(b.enemies, target) <= walk {
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
		need, holds := b.holdNeed(target, all[:count], soldiers+neutralExtra+hold)
		if holds && total >= need {
			return &option{target, walk, need, plan(all[:count], need), need + 2*walk}
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

// standsFed is whether the castle is still ours after every group bound for it lands (this turn's sends included),
// with the feeds the rear castles would send it this turn (feedStack's: production at the top, no enemy group bound
// for them, at least feedLeast to give) landing after their walks. Once it falls, every other enemy castle sends what
// it can spare to hold it, landing a walk after the fall, so a feed that only lands later rarely wins it back.
func (b *board) standsFed(c *castle) bool {
	saved := b.sent[c.id]
	defer func() { b.sent[c.id] = saved }()
	b.sent[c.id] = slices.Clone(saved)
	for _, h := range b.own {
		if h.id == c.id || b.level(h, production) < topProduction || b.boundFor(h) {
			continue
		}
		if give := b.safeOut(h); give >= feedLeast {
			b.sent[c.id] = append(b.sent[c.id], landing{b.travel(h, c), give})
		}
	}
	events := b.landings(c)
	owner, soldiers, rate, now := c.team, b.left(c), b.rate(c), 0
	held := false
	for index := 0; index < len(events); index++ {
		e := events[index]
		soldiers += rate * (e.turns - now)
		now = e.turns
		switch {
		case e.team == owner:
			soldiers += e.soldiers
		case e.soldiers > soldiers:
			owner, soldiers = e.team, e.soldiers-soldiers
		default:
			soldiers -= e.soldiers
		}
		if owner != b.team && !held {
			held = true
			for _, enemy := range b.enemies {
				events = append(events, event{now + b.travel(enemy, c), laterID * 2, owner, b.enemySpare(enemy, nil)})
			}
			sortEvents(events[index+1:])
		}
	}
	return owner == b.team
}

// boundFor is whether an enemy group is bound for the castle.
func (b *board) boundFor(c *castle) bool {
	for _, g := range b.groups {
		if g.destination == c.id && g.team != b.team {
			return true
		}
	}
	return false
}

// front is stackOf's measure: the walk at speed 1 from the castle to the nearest enemy castle.
func (b *board) front(c *castle) int {
	best := math.MaxInt
	for _, enemy := range b.enemies {
		best = min(best, walkTurns(c.distance(enemy), b.speedOf(1)))
	}
	return best
}

// spread is the castle's walks at speed 1 to every enemy castle, added up: a corner castle's is the largest.
func (b *board) spread(c *castle) int {
	total := 0
	for _, enemy := range b.enemies {
		total += walkTurns(c.distance(enemy), b.speedOf(1))
	}
	return total
}

// pickStack is the stack: stackOf's front-most castle, but never one that will be lost (its feeds can't land in
// time to save it), and between castles at the same front the better one by stackBefore. Nil without enemies;
// stackOf when every castle will be lost.
func pickStack(b *board) *castle {
	if len(b.enemies) == 0 {
		return nil
	}
	var stack *castle
	for _, c := range b.own {
		if b.standsFed(c) && (stack == nil || b.stackBefore(c, stack)) {
			stack = c
		}
	}
	if stack == nil {
		return stackOf(b)
	}
	return stack
}

// stackBefore is whether castle c is a better stack than castle d: the nearer the enemy; at the same front, one that
// holds far more (moving an army costs its walk and empties a castle beside the enemy), then the more central (a
// corner castle is far from the fight), then the one that holds more, then the lower id.
func (b *board) stackBefore(c, d *castle) bool {
	if b.front(c) != b.front(d) {
		return b.front(c) < b.front(d)
	}
	if many, few := max(b.left(c), b.left(d)), min(b.left(c), b.left(d)); many >= 2*few+feedLeast {
		return b.left(c) > b.left(d)
	}
	if b.spread(c) != b.spread(d) {
		return b.spread(c) < b.spread(d)
	}
	if b.left(c) != b.left(d) {
		return b.left(c) > b.left(d)
	}
	return c.id < d.id
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

// holdMargin is how far the castle holds, at worst, from turn first to turn last, once the senders in paid have sent
// what they give to the target: against each enemy castle's whole stock at the turn it would leave, its production
// and the groups bound for it counted, the castle holds what it will hold then (its growth and the groups bound for
// it counted) plus what this bot's other castles within helpWalk turns could land on it by then. An enemy castle
// sees a capture the turn after the sends leave, but one that owns the target may refill it this turn. It is the
// hold of a capture when the castle is the target, and of a castle that pays for one when it is a sender.
func (b *board) holdMargin(c, target *castle, paid []sender, first, last int) int {
	saved, had := b.sent[target.id]
	for _, s := range paid {
		b.spent[s.castle.id] += s.spare
		b.sent[target.id] = append(b.sent[target.id], landing{s.walk, s.spare})
	}
	defer func() {
		for _, s := range paid {
			b.spent[s.castle.id] -= s.spare
		}
		if had {
			b.sent[target.id] = saved
		} else {
			delete(b.sent, target.id)
		}
	}()
	worst := math.MaxInt
	for h := first; h <= last; h++ {
		worst = min(worst, b.marginAt(c, target, paid, h))
	}
	return worst
}

// marginAt is holdMargin at turn h alone, with the senders' sends already counted: what the castle will hold, plus
// what the own castles within helpWalk turns could land on it by then, less the strongest one enemy castle's stock.
// A castle that paid for a neutral capture and is thinner then than it is now helps it with nothing: what it has left
// is its own hold beside the enemy, and counting it twice let the stack take a neutral with 2 over its count, keep
// half, and lose both to the next strike.
func (b *board) marginAt(c, target *castle, paid []sender, h int) int {
	owner, held := b.atLanding(c, h)
	if owner != b.team {
		held = -held
	}
	help, strongest := 0, 0
	for _, other := range b.castles {
		if other.id == c.id || other.team == neutral {
			continue
		}
		travel := b.travel(other, c)
		if h-travel < 1 && (h-travel < 0 || other.team == b.team || c.team != other.team) {
			continue
		}
		switch holder, stock := b.atLanding(other, h-travel); holder {
		case neutral:
		case b.team:
			if travel > helpWalk {
				continue
			}
			if c.id == target.id && target.team == neutral && paying(paid, other) && stock < other.soldiers {
				continue
			}
			help += max(0, stock)
		default:
			strongest = max(strongest, stock)
		}
	}
	return held + help - strongest
}

// paying is whether the castle is one of the senders.
func paying(paid []sender, c *castle) bool {
	for _, s := range paid {
		if s.castle.id == c.id {
			return true
		}
	}
	return false
}

// plan is how sendFrom would pay amount from the senders, nearest first: each sender with what it gives.
func plan(senders []sender, amount int) []sender {
	var paid []sender
	for _, s := range senders {
		if amount <= 0 {
			break
		}
		if give := min(s.spare, amount); give >= 1 {
			paid = append(paid, sender{s.walk, s.castle, give})
			amount -= give
		}
	}
	return paid
}

// holdNeed is the fewest soldiers, need or more, that the senders (paying nearest first) can take the target with so
// that the capture holds for holdWalk turns after it lands and every sender holds until then too; false when no
// amount they can pay does.
func (b *board) holdNeed(target *castle, senders []sender, need int) (int, bool) {
	total := 0
	for _, s := range senders {
		total += s.spare
	}
	for need <= total {
		paid := plan(senders, need)
		last := 0
		for _, s := range paid {
			last = max(last, s.walk)
		}
		margin := b.holdMargin(target, target, paid, last, last+holdWalk)
		if margin >= 0 {
			for _, s := range paid {
				if b.holdMargin(s.castle, target, paid, 1, last+holdWalk) < 0 {
					return need, false
				}
			}
			return need, true
		}
		// A capture that the senders' own stock can't make hold, since what they send is no longer theirs to help with.
		if next := b.holdMargin(target, target, plan(senders, need-margin), last, last+holdWalk); next <= margin {
			return need, false
		}
		need -= margin
	}
	return need, false
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
		need, holds := b.holdNeed(target, []sender{{walk, stack, spare}}, need)
		if !holds {
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

// enemyBound is whether an enemy group is walking to the castle.
func (b *board) enemyBound(c *castle) bool {
	for _, g := range b.groups {
		if g.destination == c.id && g.team != b.team {
			return true
		}
	}
	return false
}

// reachFalls is whether the castle, after paying cost and producing gain more a turn, would fall to what the enemy
// castles could land on it: each enemy castle at its stock after the groups feeding it land (up to guardWalk turns
// from now), less the speed levels it could buy to walk at most guardWalk turns, against what the castle holds then,
// its own groups and growth counted.
func (b *board) reachFalls(c *castle, cost, gain int) bool {
	horizon := 2 * guardWalk
	threat := make([]int, horizon+1)
	for _, enemy := range b.enemies {
		// best[t] is the most the enemy castle could land on the castle by turn t.
		best := make([]int, horizon+1)
		for wait := 0; wait <= guardWalk; wait++ {
			owner, stock := b.atLanding(enemy, wait)
			if owner != enemy.team {
				break
			}
			level, paid := enemy.upgrades.Level(speed), 0
			for {
				if walk := walkTurns(enemy.distance(c), b.speedOf(level)); walk <= guardWalk {
					for t := wait + walk; t <= horizon; t++ {
						best[t] = max(best[t], stock-paid)
					}
				}
				_, price, found := b.table(speed, level+1)
				if !found || paid+price > stock {
					break
				}
				level, paid = level+1, paid+price
			}
		}
		for t := range best {
			threat[t] += best[t]
		}
	}
	for t := 1; t <= horizon && t < b.turnsLeft(); t++ {
		owner, soldiers := b.atLanding(c, t)
		if owner != b.team {
			return false
		}
		if soldiers-cost+gain*t < threat[t] {
			return true
		}
	}
	return false
}

// largestInReach is the most soldiers an enemy castle holds that lands on the castle within this many turns.
func (b *board) largestInReach(c *castle, turns int) int {
	most := 0
	for _, enemy := range b.enemies {
		if b.travel(enemy, c) <= turns {
			most = max(most, b.left(enemy))
		}
	}
	return most
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
		// A castle that enemy groups are walking to spends nothing on upgrades until they have landed.
		if b.enemyBound(c) {
			break
		}
		// Nor what would let a nearby enemy castle take it (one that holds without the purchase): the enemy castle
		// counted with the groups that feed it and the speed it could buy to land sooner.
		gain := 0
		if upgradeType == production {
			value, _, _ := b.table(production, level)
			gain = int(value) - b.rate(c)
		}
		if b.reachFalls(c, cost, gain) && !b.reachFalls(c, 0, 0) {
			break
		}
		// Speed doesn't help a castle hold: a stack that the enemy castles in reach could already take keeps every
		// soldier home rather than walk faster.
		if upgradeType == speed && b.reachFalls(c, cost, 0) {
			break
		}
		// Speed only serves the stack's strikes: the stack doesn't buy it when that drops it below the largest enemy
		// castle that could land on it before the price has grown back.
		if largest := b.largestInReach(c, (cost+b.rate(c)-1)/b.rate(c)); upgradeType == speed && b.left(c)-cost < largest && b.left(c) >= largest {
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

// feedThreats are the enemy castles that could land on a feeder before the stack's help, with their walks to it: an
// enemy group launched now is seen next turn, and help from the stack walks travel(stack, c) from then. While the
// stack is under attack, or after its landings (the feeds sent so far among them) short of its guard, enemy castles
// nearer the stack than the feeder are left to the stack: against them it is the front, and the feed is what holds it.
func (b *board) feedThreats(c, stack *castle) map[int]int {
	help := 1 + b.travel(stack, c)
	stackSafe := b.safeOut(stack) > b.guard(stack)
	for _, g := range b.groups {
		if g.destination == stack.id && g.team != b.team {
			stackSafe = false
		}
	}
	threats := map[int]int{}
	for _, enemy := range b.enemies {
		walk := b.travel(enemy, c)
		if walk > help || (!stackSafe && walk > b.travel(enemy, stack)) || walk >= b.turnsLeft() {
			continue
		}
		threats[enemy.id] = walk
	}
	return threats
}

// feedReserve is what a feeder keeps home when it sends the stack give: enough to hold, with its growth until each
// landing, against what its feedThreats could spare, each landing with every one that lands no later. What an enemy
// castle can spare is its stock above the reserve it must keep against this bot's castles, the stack holding the feed
// (nothing, when it falls before the feed lands).
func (b *board) feedReserve(c, stack *castle, give int) int {
	overrides := map[int]int{c.id: b.left(c) - give, stack.id: b.left(stack) + give}
	for _, sent := range b.sent[stack.id] {
		overrides[stack.id] += sent.soldiers
	}
	if b.stackFalls(c, stack) {
		overrides[stack.id] = 0
	}
	threats := b.feedThreats(c, stack)
	spare := map[int]int{}
	for _, enemy := range b.enemies {
		if _, near := threats[enemy.id]; near {
			spare[enemy.id] = b.enemySpare(enemy, overrides)
		}
	}
	// An enemy castle can wait for the groups bound for it, and its growth, until it must leave to beat the help:
	// against its waiting the castle grows too, so it is compared at the latest launch.
	help := 1 + b.travel(stack, c)
	keep := 0
	for _, enemy := range b.enemies {
		walk, near := threats[enemy.id]
		if !near {
			continue
		}
		total := 0
		for _, other := range b.enemies {
			if otherWalk, otherNear := threats[other.id]; otherNear && otherWalk <= walk {
				total += spare[other.id] + b.enemyGain(other, help-otherWalk)
			}
		}
		keep = max(keep, total-b.rate(c)*help)
	}
	return keep
}

// enemyGain is what an enemy castle gains in this many turns from its growth and the groups bound for it.
func (b *board) enemyGain(enemy *castle, turns int) int {
	if owner, soldiers := b.atLanding(enemy, turns); owner == enemy.team {
		return max(0, soldiers-b.left(enemy))
	}
	return 0
}

// hopeless is whether the castle, keeping everything, could not hold against the whole stock of one of its
// feedThreats: then its garrison only matters in the stack.
func (b *board) hopeless(c, stack *castle) bool {
	out := b.safeOut(c)
	threats := b.feedThreats(c, stack)
	for _, enemy := range b.enemies {
		if walk, near := threats[enemy.id]; near && out < b.left(enemy)-b.rate(c)*walk {
			return true
		}
	}
	return false
}

// feedGive is the most the castle can feed the stack and still keep its feedReserve; everything when it is hopeless.
func (b *board) feedGive(c, stack *castle) int {
	out := b.safeOut(c)
	if b.hopeless(c, stack) {
		return out
	}
	fits := func(give int) bool { return out-give >= b.feedReserve(c, stack, give) }
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

// stackFalls is whether the stack falls to a landing before a group sent now from the castle could land on it.
func (b *board) stackFalls(c, stack *castle) bool {
	walk := b.travel(c, stack)
	for _, e := range b.landings(stack) {
		if e.turns >= walk {
			break
		}
		if owner, _ := b.atLanding(stack, e.turns); owner != b.team {
			return true
		}
	}
	return false
}

// retakes is whether the stack is this bot's again once every group sent to it this turn has landed.
func (b *board) retakes(stack *castle) bool {
	last := 0
	for _, sent := range b.sent[stack.id] {
		last = max(last, sent.turns)
	}
	owner, _ := b.atLanding(stack, last)
	return owner == b.team
}

// feedStack sends the stack what every rear castle's landings don't need, when no enemy group is bound for it, less
// its feedReserve. A stack that falls before a feed lands gets the feeds only when together they take it back: else
// they would only be spent on the enemy's new castle.
func feedStack(b *board, stack *castle) string {
	var moves []string
	commands, spent, sent := len(b.commands), map[int]int{}, slices.Clone(b.sent[stack.id])
	for id, amount := range b.spent {
		spent[id] = amount
	}
	late := false
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
		if bound {
			continue
		}
		if give := b.feedGive(c, stack); give >= feedLeast {
			late = late || b.stackFalls(c, stack)
			b.send(c, stack, give)
			moves = append(moves, fmt.Sprintf("%d:%d", c.id, give))
		}
	}
	if late && !b.retakes(stack) {
		b.commands, b.spent, b.sent[stack.id] = b.commands[:commands], spent, sent
		return fmt.Sprintf("nofeed>%d falls", stack.id)
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
	stack := pickStack(b)
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
