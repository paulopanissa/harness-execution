---
description: Systematic debugging — root cause, minimal fix, gate
argument-hint: <error | stack trace | behavior>
---
Error: $ARGUMENTS

1. Read `~/.hx/skills/core/systematic-debugging.md` and follow it.
2. `explorer` with the error → Context Pack focused on the failure point (stack trace, files, ai-memory gotchas).
3. Minimal reproduction (a failing command/test). No repro → collect signal, do not edit.
4. Hypotheses (3–5 → 2) with evidence; prove one.
5. Minimal fix at the cause + regression test (`~/.hx/skills/quality/lean-test.md`), via the pack's stack agent.
6. `bash ~/.hx/scripts/gate.sh` → exit 0 required.
7. 3 strikes → STOP and report.

Output (≤ 15 lines): `CAUSE` · `REPRO` · `FIX (file:line)` · `TEST` · `GATE`.
