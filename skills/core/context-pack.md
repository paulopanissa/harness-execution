# Skill: context-pack
Minimal context-gathering protocol. Output ≤ 30 lines.

## Fixed order
1. **Graphify**: query the request's symbol/file/feature → relevant nodes, direct deps (1 hop), callers. Stop once the change point is found.
2. **ai-memory**: 1–3 queries (module, feature, error term). Extract only applicable gotchas/decisions. Never list or read a whole Obsidian vault.
3. **Surgical reads**: exact ranges of the files found. > 400 lines → range only. Max ~8 files.

## Fallback (Graphify or ai-memory unavailable)
- Scope: the target module directory. `rg -n "<symbol>" <module-dir>`; never the whole repo without `-g`/dir.
- Callers: `rg -n "<symbol>\(" <parent-dir> -g '!**/node_modules/**'`.
- Memory: `rg -i "<term>" ~/.hx/fallback-memory.jsonl` (JSONL: `{"repo","area","fact","date"}`).

## Output
```
STACK: ...
GOAL: ...
FILES:
- path:Lx-Ly — reason
DEPS: ...
GOTCHAS: ...
TESTS: ...
ACCEPTANCE:
- ...
RISK: ...
```
Forbidden: pasting code, creating `.md`, proposing new architecture.
