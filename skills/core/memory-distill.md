# Skill: memory-distill
When closing a task: extract 3–5 PERMANENT lines. No diary.

## Criteria (only if ALL hold)
- Not derivable from the code/git (`git log`, reading the file).
- Useful for future tasks (gotcha, decision, constraint, non-obvious command).
- Fits in 1 line (≤ 160 chars), with area/module.

## Format
`[<repo>/<area>] <fact>. Reason: <why>.`
E.g.: `[api/billing] Stripe webhook needs the raw body; no json middleware on that route. Reason: signature check fails.`

## Destination
1. **ai-memory** (store each line as a memory tagged repo/area).
2. Unavailable → append to `~/.hx/fallback-memory.jsonl`:
   `{"repo":"<repo>","area":"<area>","fact":"<fact>","date":"<YYYY-MM-DD>"}`
3. Obsidian: only through ai-memory; never open/write the vault directly.

Nothing new → save nothing and say `MEMORY: nothing new`.
