---
description: Self-chaining HX pipeline — Azure work item, GitHub issue, URL or text → validated delivery
argument-hint: <WI-123 | 123 | #45 | URL | text>
---
Input: $ARGUMENTS

## 1. Source
- `^\d+$` or `^WI-\d+$` or URL `dev.azure.com/.../_workitems/edit/N` → **Azure DevOps MCP** (`azure-devops`): title, description, acceptance criteria, type, parent.
- `^#\d+$` or URL `github.com/<owner>/<repo>/(issues|pull)/N` → **GitHub MCP** (fallback: `gh issue view N --json title,body,labels`).
- Anything else → the free text is the requirement; go straight to `explorer`.
Summarize in ≤ 10 lines: goal, acceptance, constraints. Do not save to a file.

## 2. Mode
`bash ~/.hx/hooks/org-only.sh --check` → exit 0 = **Org active**; otherwise **Minimal**.

### Org active (private corporate module)
- Ignore `/oc` and any legacy `CLAUDE.md` section.
- Branch must match `org-only.sh --get branch_regex` (`{id}` = id). If not: `git switch -c <type>/<id>` (Bug→`fix`, others→`feat`; ambiguous → ask).
- Phases in order: `org-only.sh --get phases`. For EACH phase: read ONLY `~/.hx/vendor/org/<phase_path with {phase}>`, run it, move on. Do not read the next one before finishing the current one.
- In `work`: use `explorer` + stack agent + `gate.sh` (steps 1–4 below).
- Pause before the PR/push phase for confirmation.

### Minimal (default)
1. **explorer** → Context Pack (≤ 30 lines). `BLOCKER:` in the pack → ask the user.
2. **Routing** by the pack's `STACK:` line (or by the files):
   - `*.tsx|*.jsx`, `next.config.*`, `tailwind.config.*`, `components/`, `app/`, `pages/` → `react-ts-dev`
   - backend `*.ts`, `nest-cli.json`, `prisma/`, `src/modules/`, workers/queues → `node-ts-dev`
   - `*.py`, `pyproject.toml`, `requirements*.txt` → `python-dev`
   - `project.godot`, `*.gd`, `Assets/`+`ProjectSettings/`, deps `phaser|pixi|three|bevy|love`, game loop/ECS → `gamedev-dev`
   - mixed → one agent per stack, sequential (backend before frontend).
3. The stack agent receives ONLY: Context Pack + acceptance criteria.
4. `bash ~/.hx/scripts/gate.sh`. FAIL → hand the lines back to the same agent. 2 failures in a row → STOP and report.
5. **reviewer** with the gate output + acceptance. Error list → same agent fixes → back to 4 (max 2 cycles).
6. `PASS` → PR summary (5 bullets from `~/.hx/skills/quality/pre-pr-gate.md`) + `~/.hx/skills/core/memory-distill.md`.
7. Ask before commit/push/PR.

## Allowed pauses
Critical ambiguity · failure after 2 attempts · before push/PR. Nothing else.

## Final output (≤ 20 lines)
`SOURCE` · `MODE` · `AGENTS` · `FILES (file:line)` · `GATE` · `REVIEW` · `PR (5 bullets)` · `MEMORY`
