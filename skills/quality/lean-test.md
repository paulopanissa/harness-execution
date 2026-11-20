# Skill: lean-test
Surgical tests only for new/changed paths of the diff. No test planner, no test-plan file.

## Scope
1. `git diff --name-only HEAD` + `git ls-files --others --exclude-standard` → changed code files.
2. For each new or changed function/branch: 1 happy path + 1–2 critical edge cases (null/empty, boundary, expected error, permission denied).
3. Untouched code → no tests. Pure refactor with existing tests passing → no new test.

## Rules
- Put tests where the repo's pattern says (`*.spec.ts`, `*.test.tsx`, `tests/test_*.py`).
- Reuse existing fixtures/factories. New fixture ≤ 15 lines.
- Mock only at the boundary (HTTP, DB, queue, clock, FS). Never mock the unit under test.
- Assert observable behavior; no whole-tree snapshots.
- Test name = behavior: `returns 404 when the order does not exist`.
- Deterministic tests: no sleep, no real network, fixed seed.

## Finish
`bash ~/.hx/scripts/gate.sh` (runs only tests related to the diff).
