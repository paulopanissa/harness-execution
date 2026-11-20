---
description: Feature de jogo direto no gamedev-dev com skills de gamedev
argument-hint: <feature>
---
Feature: $ARGUMENTS

1. `explorer` → Context Pack (engine, cena/sistemas afetados, loop/update atual).
2. `gamedev-dev` com o pack. Skills sob demanda conforme a feature:
   - sistemas/estados/eventos → `~/.hx/i18n/pt-BR/skills/gamedev/game-architecture.md`
   - controle/impacto/feedback → `~/.hx/i18n/pt-BR/skills/gamedev/game-feel-juice.md`
   - spawn em massa/loop quente/FPS → `~/.hx/i18n/pt-BR/skills/gamedev/game-perf-budget.md`
3. `bash ~/.hx/scripts/gate.sh` (sem testes → build/lint).
4. `reviewer` focado em: alocação no update, dependência de FPS, acoplamento, leak de listeners.
5. Saída (≤ 20 linhas): `FEITO (arquivo:linha)` · `PERF` · `GATE` · `REVIEW` · `PLAYTEST (passos)`.
