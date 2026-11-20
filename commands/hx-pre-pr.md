---
description: Deterministic gate + reviewer on the diff + PR summary
argument-hint: [base branch, e.g. origin/main]
---
Base: $ARGUMENTS (empty → local diff against HEAD)

1. `bash ~/.hx/scripts/gate.sh` (with `--base $ARGUMENTS` if given). Zero AI.
   - `GATE: FAIL` → show the lines and STOP. Do not call the reviewer.
2. `GATE: PASS` → `reviewer` with the gate output.
   - Error list → show it and STOP (the user decides to fix or run `/hx:fix`).
3. `PASS` → PR description in 5 bullets (`~/.hx/skills/quality/pre-pr-gate.md`) + conventional-commit title.
4. No push/PR without confirmation.
