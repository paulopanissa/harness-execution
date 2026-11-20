---
description: Gate determinístico + reviewer no diff + resumo de PR
argument-hint: [branch-base, ex. origin/main]
---
Base: $ARGUMENTS (vazio → diff local contra HEAD)

1. `bash ~/.hx/scripts/gate.sh` (com `--base $ARGUMENTS` se informado). Zero IA.
   - `GATE: FAIL` → mostrar as linhas e PARAR. Não chamar reviewer.
2. `GATE: PASS` → `reviewer` com o output do gate.
   - Lista de erros → mostrar e PARAR (usuário decide corrigir ou `/hx:fix`).
3. `PASS` → descrição de PR em 5 bullets (`~/.hx/i18n/pt-BR/skills/quality/pre-pr-gate.md`) + título conventional commit.
4. Não fazer push/abrir PR sem confirmação.
