---
description: Game feature straight to gamedev-dev with the gamedev skills
argument-hint: <feature>
---
Feature: $ARGUMENTS

1. `explorer` → Context Pack (engine, affected scene/systems, current loop/update).
2. `gamedev-dev` with the pack. On-demand skills by feature:
   - systems/states/events → `~/.hx/skills/gamedev/game-architecture.md`
   - controls/impact/feedback → `~/.hx/skills/gamedev/game-feel-juice.md`
   - mass spawning/hot loop/FPS → `~/.hx/skills/gamedev/game-perf-budget.md`
3. `bash ~/.hx/scripts/gate.sh` (no tests → build/lint).
4. `reviewer` focused on: allocation in update, FPS dependence, coupling, listener leaks.
5. Output (≤ 20 lines): `DONE (file:line)` · `PERF` · `GATE` · `REVIEW` · `PLAYTEST (steps)`.
