export const meta = {
  name: 'mistake-taxonomy',
  description: 'Build a mistake taxonomy from a sample, then classify all 14400 mistakes into it',
  phases: [{ title: 'Taxonomy' }, { title: 'Classify' }],
}
const S = '<the study directory>'  // the scratchpad folder the study ran in
phase('Taxonomy')
const tax = await agent(`Read ${S}/sample.txt: 700 mistakes that analysts found in Island Battles games (a castle-capture strategy game) between two bots, jug_fix and rival_mimic. Each line is "[bot] title :: description".
Build a taxonomy of mistake KINDS that covers them: 15 to 25 categories, each a distinct strategic error, not overlapping, at a level where two analysts describing the same error in different words would land in the same category (e.g. "never attacked despite a stockpile" vs "passive hoarding at the generation cap" are one kind). Include an "other" category. Use only Read on that one file.`,
  { phase: 'Taxonomy', schema: { type: 'object', required: ['categories'], properties: { categories: { type: 'array', items: { type: 'object', required: ['id', 'name', 'definition'], properties: { id: { type: 'string', description: 'short snake_case id' }, name: { type: 'string' }, definition: { type: 'string' } } } } } } })
const taxText = tax.categories.map(c => `${c.id}: ${c.name} - ${c.definition}`).join('\n')
phase('Classify')
const chunks = Array.from({ length: 24 }, (_, i) => `c${String(i).padStart(2, '0')}`)
const res = await parallel(chunks.map(c => () => agent(`Classify Island Battles bot mistakes into a fixed taxonomy.

Taxonomy (id: name - definition):
${taxText}

Read ${S}/chunks/${c}.txt (use allow_large if needed). Each line is "<id> [bot] title :: description". Assign each line exactly one category id from the taxonomy (the one that best describes the core error; "other" only if nothing fits).
Write a JSON object mapping each line's numeric id (as a string) to its category id to ${S}/cls/${c}.json, e.g. {"12":"passive_hoarding", ...}, covering all 600 lines. Use only Read for that file and Write for the output; no other tools. Then reply: done`,
  { label: `classify ${c}`, phase: 'Classify', effort: 'low' })))
return { taxonomy: tax.categories, done: res.filter(Boolean).length }
