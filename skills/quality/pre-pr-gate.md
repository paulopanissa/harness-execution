# Skill: pre-pr-gate
Cheap gate first; AI only if bash passes.

## Steps
1. `bash ~/.hx/scripts/gate.sh [--base origin/<target-branch>]`.
   - `GATE: FAIL` → stop. Show the lines, fix (max 2) or hand back to the stack agent. Do not call `reviewer`.
2. `GATE: PASS` → call `reviewer` with: gate output + acceptance criteria. It reads the diff.
   - Error list → fix → back to step 1 (max 2 cycles; then report).
3. Reviewer `PASS` → PR description in exactly 5 bullets:
```
- **What:** <change>
- **Why:** <motivation/WI>
- **How:** <approach, key files>
- **Tests:** <gate PASS + tests added>
- **Risk:** <low|medium|high> — <rollback/impact>
```
4. Title: conventional commit (`feat(scope): ...`). No mention of AI/Claude/Codex.
5. No push/PR without the user's confirmation.
