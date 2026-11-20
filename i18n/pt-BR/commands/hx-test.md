---
description: Testes cirúrgicos só para os arquivos do git diff
argument-hint: [arquivo opcional para restringir]
---
Escopo: $ARGUMENTS (vazio → todo o diff)

1. Ler `~/.hx/i18n/pt-BR/skills/quality/lean-test.md` e seguir.
2. Arquivos: `git diff --name-only HEAD` + `git ls-files --others --exclude-standard` (filtrar por `$ARGUMENTS` se informado). Ignorar testes, configs e `.md`.
3. Para cada função/branch nova ou alterada: happy path + 1–2 edge cases críticos, no padrão de teste do repo.
4. `bash ~/.hx/scripts/gate.sh` → exit 0.

Saída (≤ 15 linhas): `arquivo de teste — casos` + `GATE`.
