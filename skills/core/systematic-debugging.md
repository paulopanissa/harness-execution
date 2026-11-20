# Skill: systematic-debugging
Root cause before editing. Zero `.md`.

## Steps
1. **Exact symptom**: error message, stack, input, environment. No paraphrasing.
2. **Minimal reproduction**: one command/test that fails deterministically. No repro → collect more signal (temporary log), do not edit.
3. **Hypotheses**: list 3–5 possible causes; narrow to the 2 most likely with evidence (Context Pack, `git log -L`, blame of the section).
4. **Prove**: temporary log/assert or a test that confirms ONE hypothesis. Only then edit.
5. **Minimal fix** at the cause, not the symptom. A regression test that failed before and passes after.
6. Remove temporary logs. `bash ~/.hx/scripts/gate.sh`.

## 3-strike rule
3 failed fix attempts → STOP. Report (≤ 10 lines): symptom, discarded hypotheses + evidence, next suspect, what is still unknown.

## Forbidden
- Editing "to see if it helps" without a hypothesis.
- Silencing the error (empty `try/catch`, skipping a test, `any`, `# type: ignore`) as a fix.
- Creating analysis/plan files.
