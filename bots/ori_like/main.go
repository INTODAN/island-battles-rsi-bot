// Ori-like: a sparring opponent built to play like the hosted bot of the real games.
//
// Sparring bot (iteration 22's setup), on frontline's code. It plays as the
// hosted bot that beats the league did in 30 lobby games (2026-11-21): the home
// buys production up to openingProduction before it sends anything; neutral
// castles are bought with neutralCushion soldiers over their price, before any
// strike, so expansion goes on all game; rear castles feed the front in fixed
// batches of batch; strikes from the castles nearest a target need strikeMargin
// times its defenders. It is never a parent and never changes: it is the
// league's stand-in for that opponent, so its results against a candidate
// should say how the candidate would fare against the real one.
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
	// A neutral castle is taken with this many soldiers over what it will hold.
	neutralCushion = 5
	// An enemy castle is struck only with this many times its soldiers and reinforcements.
	strikeMargin = 1.6
	// A castle sends its spare soldiers to the front once they are this many.
	batch = 12
	// While it has one castle, the home buys production up to this level before it sends anything.
	openingProduction = 3
	// Castles whose groups land within this many turns of the nearest one join a strike.
	strikeSpread = 2
	// Every castle buys speed up to this level once its production is at the top.
	speedLevel = 2
	// A walk's turns are rounded up, less this much, so that an exact walk isn't a turn longer.
	walkSlack = 1e-9
	// No team: a neutral castle's colour.
	neutral = 0
)

const (
	production = islandbattles.GenerationAmountUpgrade
	speed      = islandbattles.SpeedUpgrade
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
	id       int
	team     int
	soldiers int
	x, y     float64
	upgrades islandbattles.Upgrades
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

// purchase is a castle and an upgrade type it bought this turn.
type purchase struct {
	castle      int
	upgradeType islandbattles.UpgradeType
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
	// Soldiers each castle has spent this turn. The server rejects the
	// whole result when a castle spends more than it has.
	spent map[int]int
	// Speed levels bought this turn, which the groups sent after them have.
	speedBought map[int]int
	bought      map[purchase]bool
	// Soldiers this turn's commands sent to each castle.
	sentTo map[int]int
}

// newBoard reads the board from the turn.
func newBoard(turn islandbattles.Turn) *board {
	b := &board{
		turn:        turn,
		team:        int(turn.TeamColor),
		spent:       map[int]int{},
		speedBought: map[int]int{},
		bought:      map[purchase]bool{},
		sentTo:      map[int]int{},
	}
	byID := map[int]*castle{}
	for _, source := range turn.Generation.Castles {
		c := &castle{
			id:       int(source.ID),
			team:     int(source.TeamColor),
			soldiers: int(source.Soldiers),
			x:        source.X,
			y:        source.Y,
			upgrades: source.Upgrades,
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
		if c.team == b.team {
			b.own = append(b.own, c)
		} else {
			if c.team != neutral {
				b.enemies = append(b.enemies, c)
			} else {
				b.neutrals = append(b.neutrals, c)
			}
		}
	}
	return b
}

// levelValue is the value of an upgrade type's level, from the turn's table (0 when it lacks it).
func (b *board) levelValue(upgradeType islandbattles.UpgradeType, level int) float64 {
	for _, upgrade := range b.turn.Upgrades {
		if upgrade.Type == upgradeType {
			for _, entry := range upgrade.Levels {
				if entry.Level == level {
					return entry.Value
				}
			}
		}
	}
	return 0
}

// production is what the castle produces a turn while a team owns it, as the SDK reads it.
func (b *board) production(c *castle) int {
	level := c.upgrades.Level(production)
	for _, upgrade := range b.turn.Upgrades {
		if upgrade.Type == production {
			for _, entry := range upgrade.Levels {
				if entry.Level == level {
					return int(entry.Value)
				}
			}
			return 1
		}
	}
	return 1
}

// nextUpgradeCost is what the castle's next level of a type costs, as the SDK reads it, and false at the top.
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

// travelTurns is the turns a group sent now from origin takes to land on target.
func (b *board) travelTurns(origin, target *castle) int {
	level := origin.upgrades.Level(speed) + b.speedBought[origin.id]
	return walkTurns(origin.distance(target), b.levelValue(speed, level))
}

// arrivalTurns is the turns until a group lands, if nothing stops it.
func (b *board) arrivalTurns(g *group) int {
	return walkTurns(g.left, b.levelValue(speed, g.upgrades.Level(speed)))
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

// defendersOnArrival is the soldiers a group sent now from origin would meet in target.
//
// A castle that a team owns grows while the group walks; a neutral one doesn't.
func (b *board) defendersOnArrival(origin, target *castle) int {
	growth := 0
	if target.team != neutral {
		growth = b.production(target) * b.travelTurns(origin, target)
	}
	return target.soldiers + growth
}

// send sends soldiers, counting them as spent.
func (b *board) send(origin, target *castle, amount int) {
	b.commands = append(b.commands, islandbattles.SendSoldierGroup(uint(origin.id), uint(target.id), uint(amount)))
	b.spent[origin.id] += amount
	b.sentTo[target.id] += amount
}

// arrival is an enemy group's landing: its turns, id and soldiers.
type arrival struct {
	turns    int
	id       int
	soldiers int
}

// contestedDefenders is what a group sent now from origin would meet in target: soldiers, growth, and whether an
// enemy holds it.
//
// Enemy groups bound for the target that land no later than this group land first: on a neutral castle they
// fight its soldiers and may take it, which then grows; on an enemy castle they join its soldiers.
func (b *board) contestedDefenders(origin, target *castle) (int, int, bool) {
	travel := b.travelTurns(origin, target)
	var arrivals []arrival
	for _, g := range b.groups {
		if g.destination == target.id && g.team != b.team && b.arrivalTurns(g) <= travel {
			arrivals = append(arrivals, arrival{b.arrivalTurns(g), g.id, g.soldiers})
		}
	}
	slices.SortFunc(arrivals, func(first, second arrival) int {
		if first.turns != second.turns {
			return first.turns - second.turns
		}
		if first.id != second.id {
			return first.id - second.id
		}
		return first.soldiers - second.soldiers
	})
	if target.team != neutral {
		reinforcing := 0
		for _, a := range arrivals {
			reinforcing += a.soldiers
		}
		growth := b.defendersOnArrival(origin, target) - target.soldiers
		return target.soldiers + reinforcing, growth, true
	}
	soldiers := target.soldiers
	enemySince := -1
	held := false
	for _, a := range arrivals {
		if !held {
			if a.soldiers > soldiers {
				soldiers = a.soldiers - soldiers
				enemySince = a.turns
				held = true
			} else {
				soldiers -= a.soldiers
			}
		} else {
			soldiers += a.soldiers
		}
	}
	if !held {
		return soldiers, 0, false
	}
	// The castle grows at level 1 from the turn after its capture.
	return soldiers, max(0, travel-enemySince), true
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
	var needy []int
	for _, c := range b.own {
		var attackers []*group
		for _, g := range b.groups {
			if g.destination == c.id && g.team != b.team {
				attackers = append(attackers, g)
			}
		}
		if len(attackers) == 0 {
			continue
		}
		soonest := b.arrivalTurns(attackers[0])
		total := 0
		for _, g := range attackers {
			soonest = min(soonest, b.arrivalTurns(g))
			total += g.soldiers
		}
		holding := c.soldiers + b.production(c)*soonest + b.headingTo(c, true)
		missing := total + 1 - holding
		if missing > 0 {
			shortfall[c.id] = missing
			deadline[c.id] = soonest
			needy = append(needy, c.id)
		}
	}
	byID := map[int]*castle{}
	for _, c := range b.castles {
		byID[c.id] = c
	}
	order := slices.Clone(needy)
	slices.SortStableFunc(order, func(first, second int) int {
		if deadline[first] != deadline[second] {
			return deadline[first] - deadline[second]
		}
		return first - second
	})
	for _, needyID := range order {
		target := byID[needyID]
		var helpers []*castle
		for _, c := range b.own {
			if _, short := shortfall[c.id]; !short {
				helpers = append(helpers, c)
			}
		}
		slices.SortStableFunc(helpers, func(first, second *castle) int {
			firstDistance, secondDistance := first.distance(target), second.distance(target)
			if firstDistance < secondDistance {
				return -1
			}
			if firstDistance > secondDistance {
				return 1
			}
			return first.id - second.id
		})
		for _, helper := range helpers {
			if shortfall[needyID] <= 0 {
				break
			}
			if b.travelTurns(helper, target) > deadline[needyID] {
				continue
			}
			spare := b.left(helper) - b.headingTo(helper, false) - guard
			amount := min(spare, shortfall[needyID])
			if amount < 1 {
				continue
			}
			b.send(helper, target, amount)
			*notes = append(*notes, fmt.Sprintf("%d+>%d:%d", helper.id, needyID, amount))
			shortfall[needyID] -= amount
		}
	}
	unheld := 0
	for _, id := range needy {
		if shortfall[id] > 0 {
			unheld++
		}
	}
	return len(needy), unheld
}

// ready is a castle that can join a strike, with its walk to the target.
type ready struct {
	walk   int
	castle *castle
}

// strike strikes the cheapest enemy castle that the castles nearest it can take together. Returns the log note.
func strike(b *board, spare map[int]int) string {
	found := false
	bestCost, bestNeed := 0, 0
	var bestTarget *castle
	var bestJoining []ready
	for _, target := range b.enemies {
		var candidates []ready
		for _, c := range b.own {
			if spare[c.id] >= 1 {
				candidates = append(candidates, ready{b.travelTurns(c, target), c})
			}
		}
		if len(candidates) == 0 {
			continue
		}
		slices.SortStableFunc(candidates, func(first, second ready) int {
			if first.walk != second.walk {
				return first.walk - second.walk
			}
			return first.castle.id - second.castle.id
		})
		nearest := candidates[0].walk
		var joining []ready
		for _, r := range candidates {
			if r.walk <= nearest+strikeSpread {
				joining = append(joining, r)
			}
		}
		last := joining[0].walk
		for _, r := range joining[1:] {
			last = max(last, r.walk)
		}
		reinforcing := 0
		for _, g := range b.groups {
			if g.destination == target.id && g.team != b.team && b.arrivalTurns(g) <= last {
				reinforcing += g.soldiers
			}
		}
		friendly := b.headingTo(target, true)
		margin := float64(float64(target.soldiers+reinforcing) * strikeMargin)
		need := int(math.Ceil(margin)) + b.production(target)*last + 1 - friendly
		total := 0
		for _, r := range joining {
			total += spare[r.castle.id]
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
	for _, r := range bestJoining {
		amount := spare[r.castle.id]
		b.send(r.castle, bestTarget, amount)
		spare[r.castle.id] = 0
		parts = append(parts, fmt.Sprintf("%d:%d", r.castle.id, amount))
	}
	return fmt.Sprintf("strike>%d need %d ", bestTarget.id, bestNeed) + strings.Join(parts, " ")
}

// expand takes the cheapest neutral castle this castle can afford with the cushion. Returns the log note.
func expand(b *board, c *castle, spare map[int]int) string {
	found := false
	bestCost, bestNeed := 0, 0
	var bestTarget *castle
	for _, target := range b.neutrals {
		defenders, growth, _ := b.contestedDefenders(c, target)
		need := defenders + growth + neutralCushion
		need -= b.headingTo(target, true) + b.sentTo[target.id]
		if need < 1 || need > spare[c.id] {
			continue
		}
		cost := need + 2*b.travelTurns(c, target)
		if !found || cost < bestCost {
			found = true
			bestCost, bestNeed, bestTarget = cost, need, target
		}
	}
	if !found {
		return ""
	}
	b.send(c, bestTarget, bestNeed)
	spare[c.id] -= bestNeed
	return fmt.Sprintf("%d->%d:%d", c.id, bestTarget.id, bestNeed)
}

// orSaying is the notes joined by spaces, or the fallback when there are none.
func orSaying(notes []string, fallback string) string {
	if joined := strings.Join(notes, " "); joined != "" {
		return joined
	}
	return fallback
}

// play plays one turn: a pure function of the turn.
func play(_ context.Context, turn islandbattles.Turn) (islandbattles.Result, error) {
	b := newBoard(turn)
	var notes []string
	if len(b.own) == 1 && b.own[0].upgrades.Level(production) < openingProduction {
		home := b.own[0]
		if b.buy(home, production, b.headingTo(home, false)) {
			notes = append(notes, fmt.Sprintf("opening production@%d", home.id))
		}
		return islandbattles.Result{
			Commands: b.commands,
			Logs: []islandbattles.LogLine{
				islandbattles.Logf("turn %d: opening; %s", turn.TurnNumber, orSaying(notes, "saving for production")),
			},
		}, nil
	}
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
	for _, c := range b.own {
		if spare[c.id] >= 1 {
			if expanded := expand(b, c, spare); expanded != "" {
				notes = append(notes, expanded)
			}
		}
	}
	if struck := strike(b, spare); struck != "" {
		notes = append(notes, struck)
	}
	if len(b.enemies) > 0 && len(b.own) > 0 {
		toEnemy := func(c *castle) float64 {
			nearest := c.distance(b.enemies[0])
			for _, enemy := range b.enemies[1:] {
				nearest = min(nearest, c.distance(enemy))
			}
			return nearest
		}
		front := b.own[0]
		frontDistance := toEnemy(front)
		for _, c := range b.own[1:] {
			if distance := toEnemy(c); distance < frontDistance {
				front, frontDistance = c, distance
			}
		}
		var moves []string
		for _, c := range b.own {
			if c.id == front.id || spare[c.id] < batch || toEnemy(front) >= toEnemy(c) {
				continue
			}
			b.send(c, front, batch)
			moves = append(moves, fmt.Sprintf("%d:%d", c.id, batch))
			spare[c.id] -= batch
		}
		if len(moves) > 0 {
			notes = append(notes, fmt.Sprintf("stage>%d ", front.id)+strings.Join(moves, " "))
		}
	}
	producing := 0
	for _, c := range b.own {
		producing += b.production(c)
	}
	return islandbattles.Result{
		Commands: b.commands,
		Logs: []islandbattles.LogLine{
			islandbattles.Logf(
				"turn %d: %d castles producing %d a turn, %d short under attack (%d unheld); %s",
				turn.TurnNumber, len(b.own), producing, short, unheld, orSaying(notes, "saving"),
			),
		},
	}, nil
}
