---
description: Surgical tests only for the files in the git diff
argument-hint: [optional file to narrow the scope]
---
Scope: $ARGUMENTS (empty → the whole diff)

1. Read `~/.hx/skills/quality/lean-test.md` and follow it.
2. Files: `git diff --name-only HEAD` + `git ls-files --others --exclude-standard` (filtered by `$ARGUMENTS` if given). Skip tests, configs and `.md`.
3. For each new or changed function/branch: happy path + 1–2 critical edge cases, following the repo's test pattern.
4. `bash ~/.hx/scripts/gate.sh` → exit 0.

Output (≤ 15 lines): `test file — cases` + `GATE`.
