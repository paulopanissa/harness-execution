---
description: Remove a seção legada "## Configuração do Projeto" (/oc) do CLAUDE.md do repo atual
argument-hint: [caminho do CLAUDE.md]
---
Alvo: $ARGUMENTS (vazio → `CLAUDE.md` na raiz do repo: `git rev-parse --show-toplevel`)

1. `bash ~/.hx/hooks/strip-legacy-oc.sh <alvo> --dry-run` → mostrar o diff.
2. Nada a remover → informar e parar.
3. Confirmar com o usuário. Sim → `bash ~/.hx/hooks/strip-legacy-oc.sh <alvo>` (backup em `<alvo>.hx-bak`).
4. Repetir para `apps/*/CLAUDE.md` que tenham a seção (`rg -l "Configura(ç|c)(ã|a)o do Projeto" -g CLAUDE.md`).
5. Não commitar.
