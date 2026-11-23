package bots

import (
	"bufio"
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"go/ast"
	"go/parser"
	"go/token"
	"maps"
	"math/rand/v2"
	"os"
	"os/exec"
	"path/filepath"
	"slices"
	"strconv"
	"strings"
	"testing"

	islandbattles "github.com/INTODAN/island-battles-go/clients/island-battles-go"
)

// sdkPath is the Go SDK's import path: the one module a bot may import.
const sdkPath = "github.com/INTODAN/island-battles-go/clients/island-battles-go"

// allowedImports are the standard packages a bot may import besides the SDK: nothing that reads a clock, a
// file, the network or the process, no randomness, no goroutines' tools, and nothing whose order varies.
var allowedImports = map[string]bool{
	"cmp":            true,
	"container/heap": true,
	"container/list": true,
	"context":        true,
	"encoding/json":  true,
	"errors":         true,
	"fmt":            true,
	"iter":           true,
	"math":           true,
	"math/bits":      true,
	"slices":         true,
	"sort":           true,
	"strconv":        true,
	"strings":        true,
	"unicode":        true,
	"unicode/utf8":   true,
}

// firstGenerationID is where the turns' generation IDs start: the server's don't start at 1, so a bot that
// reads the ID as the turn number shows it here.
const firstGenerationID = 5538

// root is the repository's root.
var root = func() string {
	directory, err := filepath.Abs("../..")
	if err != nil {
		panic(err)
	}
	return directory
}()

// binaries are the bots' programs, built once for every test.
var binaries map[string]string

func TestMain(m *testing.M) {
	directory, err := os.MkdirTemp("", "league-bots-")
	if err != nil {
		panic(err)
	}
	build := exec.Command("go", "build", "-trimpath", "-o", directory+string(os.PathSeparator), "./bots/...")
	build.Dir = root
	if output, err := build.CombinedOutput(); err != nil {
		fmt.Fprintf(os.Stderr, "the bots didn't build:\n%s", output)
		os.Exit(1)
	}
	binaries = map[string]string{}
	for _, name := range names() {
		binaries[name] = filepath.Join(directory, name)
	}
	status := m.Run()
	_ = os.RemoveAll(directory)
	os.Exit(status)
}

// names are the league's bots: every directory of bots/ with a bot.toml.
func names() []string {
	found, err := filepath.Glob(filepath.Join(root, "bots", "*", "bot.toml"))
	if err != nil {
		panic(err)
	}
	var result []string
	for _, path := range found {
		result = append(result, filepath.Base(filepath.Dir(path)))
	}
	slices.Sort(result)
	return result
}

// worker is a bot's worker process, which plays turns as the runner gives them.
type worker struct {
	command *exec.Cmd
	input   *bufio.Writer
	output  *bufio.Reader
}

func startWorker(t *testing.T, name string) *worker {
	t.Helper()
	command := exec.Command(binaries[name], "worker")
	stdin, err := command.StdinPipe()
	if err != nil {
		t.Fatal(err)
	}
	stdout, err := command.StdoutPipe()
	if err != nil {
		t.Fatal(err)
	}
	if err := command.Start(); err != nil {
		t.Fatal(err)
	}
	w := &worker{command: command, input: bufio.NewWriter(stdin), output: bufio.NewReader(stdout)}
	t.Cleanup(func() {
		_ = stdin.Close()
		_ = command.Wait()
	})
	var ready struct{ Ready bool }
	if err := w.read(&ready); err != nil || !ready.Ready {
		t.Fatalf("%s's worker didn't start: %v", name, err)
	}
	return w
}

func (w *worker) read(target any) error {
	line, err := w.output.ReadBytes('\n')
	if err != nil {
		return err
	}
	return json.Unmarshal(line, target)
}

// play plays one turn, and returns the result as the worker encoded it, or the worker's error.
func (w *worker) play(turn islandbattles.Turn) (json.RawMessage, error) {
	request, err := json.Marshal(map[string]any{"turn": turn})
	if err != nil {
		return nil, err
	}
	if _, err := w.input.Write(append(request, '\n')); err != nil {
		return nil, err
	}
	if err := w.input.Flush(); err != nil {
		return nil, err
	}
	var answer struct {
		Result json.RawMessage `json:"result"`
		Error  *string         `json:"error"`
	}
	if err := w.read(&answer); err != nil {
		return nil, err
	}
	if answer.Error != nil {
		return nil, errors.New(*answer.Error)
	}
	return answer.Result, nil
}

// mustPlay plays one turn and decodes the result, failing the test on an error.
func (w *worker) mustPlay(t *testing.T, turn islandbattles.Turn) (islandbattles.Result, json.RawMessage) {
	t.Helper()
	raw, err := w.play(turn)
	if err != nil {
		t.Fatalf("turn %d failed: %v", turn.TurnNumber, err)
	}
	var result islandbattles.Result
	if err := json.Unmarshal(raw, &result); err != nil {
		t.Fatalf("the result is not a BotTurnResult: %v", err)
	}
	return result, raw
}

// group is a group of a team on its way from one castle to another, share of the way there.
func group(id, team, soldiers uint, origin, target islandbattles.Castle, share float64) islandbattles.SoldierGroup {
	return islandbattles.SoldierGroup{
		ID:                  id,
		TeamColor:           team,
		Soldiers:            soldiers,
		OriginCastleID:      origin.ID,
		DestinationCastleID: target.ID,
		X:                   origin.X + (target.X-origin.X)*share,
		Y:                   origin.Y + (target.Y-origin.Y)*share,
		ClashRadius:         0.25,
		Upgrades:            maps.Clone(origin.Upgrades),
	}
}

// own are the indexes of the team's castles.
func own(generation *islandbattles.Generation, team uint) []int {
	var found []int
	for index, castle := range generation.Castles {
		if castle.TeamColor == team {
			found = append(found, index)
		}
	}
	return found
}

// enemy is the first castle of another team.
func enemy(generation *islandbattles.Generation, team uint) islandbattles.Castle {
	for _, castle := range generation.Castles {
		if castle.TeamColor != islandbattles.NeutralTeamColor && castle.TeamColor != team {
			return castle
		}
	}
	panic("the board has no enemy castle")
}

// underAttack: every castle of the team has a large enemy group about to land on it.
func underAttack(generation *islandbattles.Generation, team uint) {
	from := enemy(generation, team)
	generation.SoldierGroups = []islandbattles.SoldierGroup{}
	for index, castle := range own(generation, team) {
		generation.SoldierGroups = append(generation.SoldierGroups,
			group(uint(index), from.TeamColor, uint(25+20*index), from, generation.Castles[castle], 0.9))
	}
}

// boards are the fixture's variants that every bot must answer acceptably.
var boards = map[string]func(generation *islandbattles.Generation, team uint){
	"the fixture":  func(*islandbattles.Generation, uint) {},
	"under attack": underAttack,
	// The team's castles are rich; one owes a burst, one has every upgrade at its top level.
	"debt and top levels": func(generation *islandbattles.Generation, team uint) {
		underAttack(generation, team)
		for index, castle := range own(generation, team) {
			c := &generation.Castles[castle]
			c.Upgrades[islandbattles.BurstPotentialUpgrade] = 2
			if index == 0 {
				// Short of what is about to land on it, and not allowed to burst.
				c.Soldiers, c.BurstDebt = 6, 3
			} else {
				c.Soldiers = 200
				c.Upgrades = islandbattles.Upgrades{"burst_potential": 4, "clash_stop_generations": 3, "generation_amount": 4, "speed": 4}
			}
		}
	},
	// The team's castles hold no soldiers or one.
	"poor": func(generation *islandbattles.Generation, team uint) {
		underAttack(generation, team)
		for index, castle := range own(generation, team) {
			generation.Castles[castle].Soldiers = uint(index % 2)
		}
	},
	// Every other team's castles are neutral; its groups are still out.
	"no enemy castles": func(generation *islandbattles.Generation, team uint) {
		for index := range generation.Castles {
			if generation.Castles[index].TeamColor != team {
				generation.Castles[index].TeamColor = islandbattles.NeutralTeamColor
			}
		}
	},
	// The team has lost its castles and has one group left.
	"no castles": func(generation *islandbattles.Generation, team uint) {
		to := enemy(generation, team)
		castles := own(generation, team)
		generation.SoldierGroups = []islandbattles.SoldierGroup{group(0, team, 9, generation.Castles[castles[0]], to, 0.5)}
		for _, castle := range castles {
			generation.Castles[castle].TeamColor = to.TeamColor
		}
	},
}

// boardNames are the boards' names, in order.
func boardNames() []string {
	return slices.Sorted(maps.Keys(boards))
}

// gameTurn is the fixture turn on a board, at a turn number, for a team (0: the fixture's), with memory.
func gameTurn(turnNumber int, memory islandbattles.Memory, team uint, board string) islandbattles.Turn {
	turn := islandbattles.FixtureTurn()
	turn.TurnNumber = turnNumber
	turn.Generation.ID = uint(firstGenerationID + turnNumber - 1)
	turn.Memory = memory
	if team != 0 {
		turn.TeamColor = team
	}
	boards[board](&turn.Generation, turn.TeamColor)
	return turn
}

// fixtureTeams are the teams that own castles on the fixture.
func fixtureTeams() []uint {
	teams := map[uint]bool{}
	for _, castle := range islandbattles.FixtureTurn().Generation.Castles {
		if castle.TeamColor != islandbattles.NeutralTeamColor {
			teams[castle.TeamColor] = true
		}
	}
	return slices.Sorted(maps.Keys(teams))
}

// randomTurn is a board made from a seed: owners, soldiers, levels, debts and groups all vary.
func randomTurn(seed uint64) islandbattles.Turn {
	random := rand.New(rand.NewPCG(seed, 2026))
	choose := func(options ...uint) uint { return options[random.IntN(len(options))] }
	turn := islandbattles.FixtureTurn()
	tops := map[islandbattles.UpgradeType]int{}
	for _, upgrade := range turn.Upgrades {
		tops[upgrade.Type] = upgrade.MaxLevel
	}
	type spot struct{ x, y float64 }
	var spots []spot
	for _, x := range []float64{-4, -2, 0, 2, 4} {
		for _, y := range []float64{-2, 0, 2} {
			spots = append(spots, spot{x, y})
		}
	}
	random.Shuffle(len(spots), func(i, j int) { spots[i], spots[j] = spots[j], spots[i] })
	generation := &turn.Generation
	generation.Castles = nil
	for id, place := range spots[:2+random.IntN(8)] {
		upgrades := islandbattles.Upgrades{}
		for _, upgradeType := range islandbattles.UpgradeTypes() {
			upgrades[upgradeType] = 1 + random.IntN(tops[upgradeType])
		}
		generation.Castles = append(generation.Castles, islandbattles.Castle{
			ID:        uint(id),
			TeamColor: choose(0, 1, 1, 2, 2),
			Soldiers:  choose(0, 1, 3, 8, 15, 30, 60, 120),
			X:         place.x,
			Y:         place.y,
			Upgrades:  upgrades,
			BurstDebt: choose(0, 0, 0, 2, 7),
		})
	}
	generation.SoldierGroups = []islandbattles.SoldierGroup{}
	for id := range random.IntN(7) {
		pair := random.Perm(len(generation.Castles))[:2]
		origin, target := generation.Castles[pair[0]], generation.Castles[pair[1]]
		generation.SoldierGroups = append(generation.SoldierGroups,
			group(uint(id), choose(1, 2), choose(1, 5, 20, 70), origin, target, random.Float64()))
	}
	turn.TeamColor = choose(1, 2)
	turn.TurnNumber = int(choose(1, 2, 40, 150, 299))
	generation.ID = uint(firstGenerationID + turn.TurnNumber - 1)
	return turn
}

// command is a command's parameters, whichever its type.
type command struct {
	Origin      *uint                     `json:"origin_castle_id"`
	Destination uint                      `json:"destination_castle_id"`
	Castle      *uint                     `json:"castle_id"`
	Amount      uint                      `json:"soldier_amount"`
	UpgradeType islandbattles.UpgradeType `json:"upgrade_type"`
}

// rejection is why the server would reject the result, or "": the rules of validateCommands. The sends and
// upgrades are checked in order, each against what the ones before it spent; then the bursts, each against the
// castle's potential with every level the result bought.
func rejection(turn islandbattles.Turn, result islandbattles.Result) string {
	castles := map[uint]islandbattles.Castle{}
	soldiers := map[uint]int{}
	levels := map[uint]islandbattles.Upgrades{}
	for _, castle := range turn.Generation.Castles {
		castles[castle.ID] = castle
		soldiers[castle.ID] = int(castle.Soldiers)
		levels[castle.ID] = maps.Clone(castle.Upgrades)
	}
	table := map[islandbattles.UpgradeType]map[int]islandbattles.UpgradeLevel{}
	for _, upgrade := range turn.Upgrades {
		table[upgrade.Type] = map[int]islandbattles.UpgradeLevel{}
		for _, level := range upgrade.Levels {
			table[upgrade.Type][level.Level] = level
		}
	}
	parameters := make([]command, len(result.Commands))
	for index, entry := range result.Commands {
		if err := json.Unmarshal(entry.Parameters, &parameters[index]); err != nil {
			return fmt.Sprintf("command %d's parameters don't decode: %v", index, err)
		}
		p := parameters[index]
		id := p.Castle
		if p.Origin != nil {
			id = p.Origin
		}
		if id == nil {
			return fmt.Sprintf("command %d names no castle", index)
		}
		castle, found := castles[*id]
		if !found || castle.TeamColor != turn.TeamColor {
			return fmt.Sprintf("castle %d is not the team's", *id)
		}
		switch entry.CommandType {
		case islandbattles.SendSoldierGroupCommand:
			if _, found := castles[p.Destination]; !found || p.Destination == *id {
				return fmt.Sprintf("castle %d sends to %d", *id, p.Destination)
			}
			if p.Amount < 1 {
				return fmt.Sprintf("castle %d sends no soldiers", *id)
			}
			soldiers[*id] -= int(p.Amount)
		case islandbattles.UpgradeCastleCommand:
			level := levels[*id].Level(p.UpgradeType) + 1
			levels[*id][p.UpgradeType] = level
			entry, found := table[p.UpgradeType][level]
			if !found {
				return fmt.Sprintf("castle %d upgrades %s past its top level", *id, p.UpgradeType)
			}
			soldiers[*id] -= int(entry.SoldierCost)
		case islandbattles.BurstCastleCommand:
		default:
			return fmt.Sprintf("command %d has the unknown type %q", index, entry.CommandType)
		}
		if soldiers[*id] < 0 {
			return fmt.Sprintf("castle %d spends %d soldiers more than it has", *id, -soldiers[*id])
		}
	}
	burst := map[uint]bool{}
	for index, entry := range result.Commands {
		if entry.CommandType != islandbattles.BurstCastleCommand {
			continue
		}
		id, amount := *parameters[index].Castle, parameters[index].Amount
		potential, found := table[islandbattles.BurstPotentialUpgrade][levels[id].Level(islandbattles.BurstPotentialUpgrade)]
		if castles[id].BurstDebt > 0 || burst[id] {
			return fmt.Sprintf("castle %d bursts with a debt, or twice", id)
		}
		if !found || amount < 1 || float64(amount) > potential.Value {
			return fmt.Sprintf("castle %d bursts %d, above its potential of %g", id, amount, potential.Value)
		}
		burst[id] = true
	}
	return ""
}

func TestTheLeagueHasBots(t *testing.T) {
	if len(names()) == 0 {
		t.Fatal("bots/ has no bot")
	}
}

func TestResultsAreOnesTheServerAccepts(t *testing.T) {
	for _, name := range names() {
		t.Run(name, func(t *testing.T) {
			t.Parallel()
			w := startWorker(t, name)
			for _, board := range boardNames() {
				for _, team := range fixtureTeams() {
					turn := gameTurn(1, nil, team, board)
					result, _ := w.mustPlay(t, turn)
					if problem := rejection(turn, result); problem != "" {
						t.Errorf("%s, team %d: %s", board, team, problem)
					}
				}
			}
			for seed := range uint64(300) {
				turn := randomTurn(seed)
				result, _ := w.mustPlay(t, turn)
				if problem := rejection(turn, result); problem != "" {
					t.Errorf("random board %d: %s", seed, problem)
				}
			}
		})
	}
}

func TestTheCheckRejectsWhatTheServerRejects(t *testing.T) {
	// The check above would be worthless if it let these through.
	turn := gameTurn(1, nil, 0, "debt and top levels")
	castles := own(&turn.Generation, turn.TeamColor)
	owing, rich := turn.Generation.Castles[castles[0]].ID, turn.Generation.Castles[castles[1]].ID
	other := enemy(&turn.Generation, turn.TeamColor).ID
	send, upgrade, burst := islandbattles.SendSoldierGroup, islandbattles.UpgradeCastle, islandbattles.BurstCastle
	rejected := map[string][]islandbattles.Command{
		"overspending across commands":  {send(rich, other, 150), send(rich, other, 51)},
		"a castle of another team":      {send(other, rich, 1)},
		"an upgrade past the top level": {upgrade(rich, islandbattles.SpeedUpgrade)},
		"a burst with a debt":           {burst(owing, 1)},
		"a burst above the potential":   {burst(rich, 17)},
		"two bursts of one castle":      {burst(rich, 1), burst(rich, 1)},
		"a send to itself":              {send(rich, rich, 1)},
	}
	for name, commands := range rejected {
		if rejection(turn, islandbattles.Result{Commands: commands}) == "" {
			t.Errorf("the check lets %s through", name)
		}
	}
	if problem := rejection(turn, islandbattles.Result{Commands: []islandbattles.Command{burst(rich, 16), send(rich, other, 200)}}); problem != "" {
		t.Errorf("the check rejects a full burst and a full send: %s", problem)
	}
	// A burst counts a level bought anywhere in the same result.
	fixture := gameTurn(1, nil, 0, "the fixture")
	if problem := rejection(fixture, islandbattles.Result{Commands: []islandbattles.Command{burst(0, 4), upgrade(0, islandbattles.BurstPotentialUpgrade)}}); problem != "" {
		t.Errorf("the check misses a level bought after the burst: %s", problem)
	}
	if rejection(fixture, islandbattles.Result{Commands: []islandbattles.Command{burst(0, 4)}}) == "" {
		t.Error("the check lets a burst above the potential through")
	}
}

func TestTheSameTurnGivesTheSameResult(t *testing.T) {
	for _, name := range names() {
		t.Run(name, func(t *testing.T) {
			t.Parallel()
			w := startWorker(t, name)
			for _, board := range boardNames() {
				for _, turnNumber := range []int{1, 2, 150, 299} {
					var memory islandbattles.Memory
					if turnNumber > 1 {
						first, _ := w.mustPlay(t, gameTurn(1, nil, 0, board))
						memory = first.Memory
					}
					_, first := w.mustPlay(t, gameTurn(turnNumber, memory, 0, board))
					// Other turns in between, as a process that plays many games has.
					w.mustPlay(t, randomTurn(uint64(turnNumber)))
					_, second := w.mustPlay(t, gameTurn(turnNumber, memory, 0, board))
					if !bytes.Equal(first, second) {
						t.Errorf("%s, turn %d: two answers\n%s\n%s", board, turnNumber, first, second)
					}
				}
			}
			// A Go map's order changes on every walk: a bot that walks one where it matters answers differently.
			for seed := range uint64(100) {
				_, first := w.mustPlay(t, randomTurn(seed))
				_, second := w.mustPlay(t, randomTurn(seed))
				if !bytes.Equal(first, second) {
					t.Errorf("random board %d: two answers\n%s\n%s", seed, first, second)
				}
			}
		})
	}
}

func TestMemoryStaysASmallJSONObject(t *testing.T) {
	for _, name := range names() {
		t.Run(name, func(t *testing.T) {
			t.Parallel()
			w := startWorker(t, name)
			var memory islandbattles.Memory
			for turnNumber := 1; turnNumber < 40; turnNumber++ {
				result, _ := w.mustPlay(t, gameTurn(turnNumber, memory, 0, "the fixture"))
				memory = result.Memory
				if size, err := memory.Size(); err != nil || size >= islandbattles.MemoryLimitBytes/8 {
					t.Fatalf("turn %d: memory of %d bytes (%v); the limit for a league bot is %d", turnNumber, size, err, islandbattles.MemoryLimitBytes/8)
				}
			}
		})
	}
}

func TestTheBotLogsItsTurn(t *testing.T) {
	// A game can only be studied if its bots say what they decided.
	for _, name := range names() {
		t.Run(name, func(t *testing.T) {
			t.Parallel()
			w := startWorker(t, name)
			for _, board := range boardNames() {
				result, _ := w.mustPlay(t, gameTurn(2, nil, 0, board))
				if len(result.Logs) == 0 {
					t.Errorf("%s: no log line", board)
				}
			}
		})
	}
}

// impurities is what makes a bot's file depend on more than the turn: imports, state, goroutines.
func impurities(source string) []string {
	files := token.NewFileSet()
	file, err := parser.ParseFile(files, "main.go", source, parser.SkipObjectResolution)
	if err != nil {
		return []string{fmt.Sprintf("doesn't parse: %v", err)}
	}
	var found []string
	if file.Name.Name != "main" {
		found = append(found, fmt.Sprintf("is package %s, not main", file.Name.Name))
	}
	for _, spec := range file.Imports {
		path, _ := strconv.Unquote(spec.Path.Value)
		if path != sdkPath && !allowedImports[path] {
			found = append(found, "imports "+path)
		}
	}
	for _, declaration := range file.Decls {
		switch declaration := declaration.(type) {
		case *ast.GenDecl:
			// A value that lives between turns could be one a turn changes: the same process plays many games.
			if declaration.Tok == token.VAR {
				for _, spec := range declaration.Specs {
					for _, name := range spec.(*ast.ValueSpec).Names {
						found = append(found, fmt.Sprintf("keeps a package-level variable %s at line %d", name.Name, files.Position(name.Pos()).Line))
					}
				}
			}
		case *ast.FuncDecl:
			if declaration.Recv == nil && declaration.Name.Name == "init" {
				found = append(found, fmt.Sprintf("has an init function at line %d", files.Position(declaration.Pos()).Line))
			}
		}
	}
	ast.Inspect(file, func(node ast.Node) bool {
		if statement, ok := node.(*ast.GoStmt); ok {
			found = append(found, fmt.Sprintf("starts a goroutine at line %d", files.Position(statement.Pos()).Line))
		}
		return true
	})
	return found
}

func TestBotsAreSelfContainedAndPure(t *testing.T) {
	// A bot imports only the SDK and a few pure standard packages, and keeps nothing between turns.
	for _, name := range names() {
		directory := filepath.Join(root, "bots", name)
		if _, err := os.Stat(filepath.Join(directory, "main.go")); err != nil {
			t.Errorf("%s has no main.go", name)
		}
		err := filepath.WalkDir(directory, func(path string, entry os.DirEntry, err error) error {
			if err != nil || entry.IsDir() {
				return err
			}
			relative, _ := filepath.Rel(directory, path)
			switch {
			case strings.HasSuffix(path, "_test.go"):
			case strings.HasSuffix(path, ".go"):
				if filepath.Dir(relative) != "." {
					t.Errorf("%s: %s is in a package of its own; a bot is one package", name, relative)
				}
				source, err := os.ReadFile(path)
				if err != nil {
					return err
				}
				for _, problem := range impurities(string(source)) {
					t.Errorf("%s: %s %s", name, relative, problem)
				}
			case relative == "bot.toml":
			default:
				t.Errorf("%s: %s is neither Go code nor bot.toml", name, relative)
			}
			return nil
		})
		if err != nil {
			t.Error(err)
		}
	}
}

func TestThePurityCheckFindsWhatItIsFor(t *testing.T) {
	cases := map[string]string{
		"package main\nimport \"github.com/INTODAN/island-battles-rsi-bot/bots/economist\"": "imports github.com/INTODAN/island-battles-rsi-bot/bots/economist",
		"package main\nimport \"math/rand/v2\"":                                             "imports math/rand/v2",
		"package main\nimport \"time\"":                                                     "imports time",
		"package main\nimport \"os\"":                                                       "imports os",
		"package main\nimport \"maps\"":                                                     "imports maps",
		"package main\nvar seen = map[int]int{}":                                            "keeps a package-level variable seen at line 2",
		"package main\nvar (\n\tcalls int\n)":                                               "keeps a package-level variable calls at line 3",
		"package main\nfunc init() {}":                                                      "has an init function at line 2",
		"package main\nfunc play() {\n\tgo play()\n}":                                       "starts a goroutine at line 3",
		"package bot": "is package bot, not main",
	}
	for source, problem := range cases {
		if found := impurities(source); !slices.Equal(found, []string{problem}) {
			t.Errorf("%q: found %q, want %q", source, found, problem)
		}
	}
	pure := "package main\nimport (\n\t\"math\"\n\tislandbattles \"" + sdkPath + "\"\n)\nconst wave = 8\n" +
		"type board struct{ spent map[int]int }\nfunc play() { b := board{spent: map[int]int{}}; _ = b; _ = math.Pi; _ = islandbattles.NeutralTeamColor }"
	if found := impurities(pure); len(found) != 0 {
		t.Errorf("a pure bot has impurities: %q", found)
	}
}
