export const meta = {
  name: 'mistake-analysis-determinism',
  description: 'Analyze 60 jug_fix vs rival_mimic games 10x each with 4 model configs; write top-3 mistakes per bot per game',
  phases: [{ title: 'Analyze', detail: '4 configs x 10 reps x 6 batches of 10 games' }],
}
const S = '<the study directory>'  // the scratchpad folder the study ran in
const CONFIGS = [
  { key: 'opus-default' },
  { key: 'sonnet-high', model: 'sonnet', effort: 'high' },
  { key: 'opus-medium', model: 'opus', effort: 'medium' },
  { key: 'fable-medium', model: 'fable', effort: 'medium' },
]
const jobs = []
for (let rep = 1; rep <= 10; rep++)
  for (const c of CONFIGS)
    for (let b = 1; b <= 6; b++) jobs.push({ c, rep, b })
const todo = jobs.filter(j => !args.skip.includes(`${j.c.key}_r${j.rep}_b${j.b}`)).filter((j, i) => i % 2 === args.part)
log(`part ${args.part}: ${todo.length} jobs`)

const prompt = (j) => `You are analyzing Island Battles games between two bots, jug_fix and rival_mimic. (Analysis run ${j.rep}.)

1. Read the game rules: ${S}/rules.md
2. Read the file ${S}/batch${j.b}.txt (use allow_large if needed). It holds 10 games, each starting with "======== GAME gNN ========", followed by that game's digest: the teams, the outcome, a timeline table (castles / soldiers in castles / soldiers in groups / production), logistics, and the events (captures, upgrades, bursts, eliminations, sometimes sends and clashes).
Use no other tools besides Read for those two files and one Write at the end. Do not run commands, do not look at other files.

For EACH of the 10 games, analyze it on its own and find the TOP 3 MISTAKES OF EACH BOT (3 for jug_fix, 3 for rival_mimic), ranked by how much they cost that bot in this game (rank 1 = costliest). A mistake is a decision (or a repeated pattern of decisions) the bot made, or failed to make, that a better player would have done differently. Ground each one in the digest: turns, castle ids, numbers. Even in a game a bot won, find its 3 biggest mistakes.

Write your results as JSON to ${S}/out/${j.c.key}_r${j.rep}_b${j.b}.json with exactly this shape:
{"games":[{"game":"gNN","jug_fix":[M,M,M],"rival_mimic":[M,M,M]}, ... 10 games]}
where each M is {"rank":1,"title":"<short name of the mistake, under 10 words>","turns":"<turn or range, e.g. 105-112>","castles":[<castle ids involved>],"description":"<what the bot did wrong and what it should have done, under 40 words>"}.
Make sure the file is valid JSON. Then reply with just: done`

phase('Analyze')
const res = await parallel(todo.map(j => () =>
  agent(prompt(j), { label: `${j.c.key} r${j.rep} b${j.b}`, phase: 'Analyze', ...(j.c.model ? { model: j.c.model } : {}), ...(j.c.effort ? { effort: j.c.effort } : {}) })
    .then(t => ({ k: `${j.c.key}_r${j.rep}_b${j.b}`, ok: t != null }))))
return { finished: res.filter(Boolean).filter(r => r.ok).length, failed: res.filter(r => !r || !r.ok).map(r => r && r.k) }
