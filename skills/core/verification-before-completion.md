# Skill: verification-before-completion
Never claim "done", "fixed" or "passing" without fresh evidence.

## Rule
1. Run `bash ~/.hx/scripts/gate.sh` AFTER the last edit of this round.
2. Only `exit 0` with output `GATE: PASS` (or `GATE: PASS (...)`) counts.
3. Output from an earlier round, another agent, or "should pass" does not count.
4. `GATE: PASS (no applicable checker)` → say explicitly that nothing was verified automatically and list the manual check done.
5. Failed → do not claim done. Fix (max 2) or report the FAIL with the gate lines.

## Final report
`GATE: PASS` + list of changed `file:line`. No "everything works" without the gate.
