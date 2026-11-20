---
description: Pipeline HX auto-encadeado — WI Azure, issue GitHub, URL ou texto → entrega validada
argument-hint: <WI-123 | 123 | #45 | URL | texto>
---
Entrada: $ARGUMENTS

## 1. Origem
- `^\d+$` ou `^WI-\d+$` ou URL `dev.azure.com/.../_workitems/edit/N` → **Azure DevOps MCP** (`azure-devops`): título, descrição, critérios de aceite, tipo, parent.
- `^#\d+$` ou URL `github.com/<owner>/<repo>/(issues|pull)/N` → **GitHub MCP** (fallback: `gh issue view N --json title,body,labels`).
- Outro → texto livre é o requisito; vai direto ao `explorer`.
Resuma em ≤ 10 linhas: objetivo, aceite, restrições. Não salvar em arquivo.

## 2. Modo
`bash ~/.hx/hooks/org-only.sh --check` → exit 0 = **Org ativo**; senão **Minimalista**.

### Org ativo (módulo corporativo privado)
- Ignorar `/oc` e qualquer seção legada de `CLAUDE.md`.
- Branch deve casar `org-only.sh --get branch_regex` (`{id}` = id). Se não: `git switch -c <tipo>/<id>` (Bug→`fix`, demais→`feat`; ambíguo → perguntar).
- Fases em ordem: `org-only.sh --get phases`. Para CADA fase: ler SÓ `~/.hx/vendor/org/<phase_path com {phase}>`, executar, seguir. Não ler a próxima antes de concluir a atual.
- Em `work`: usar `explorer` + agente da stack + `gate.sh` (passos 1–4 abaixo).
- Pausar antes da fase de PR/push para confirmação.

### Minimalista (padrão)
1. **explorer** → Context Pack (≤ 30 linhas). `BLOQUEIO:` no pack → perguntar ao usuário.
2. **Roteamento** pela linha `STACK:` do pack (ou pelos arquivos):
   - `*.tsx|*.jsx`, `next.config.*`, `tailwind.config.*`, `components/`, `app/`, `pages/` → `react-ts-dev`
   - `*.ts` backend, `nest-cli.json`, `prisma/`, `src/modules/`, workers/filas → `node-ts-dev`
   - `*.py`, `pyproject.toml`, `requirements*.txt` → `python-dev`
   - `project.godot`, `*.gd`, `Assets/`+`ProjectSettings/`, deps `phaser|pixi|three|bevy|love`, game loop/ECS → `gamedev-dev`
   - misto → um agente por stack, sequencial (backend antes do frontend).
3. Agente da stack recebe SÓ: Context Pack + critérios de aceite.
4. `bash ~/.hx/scripts/gate.sh`. FAIL → devolver as linhas ao mesmo agente. 2 falhas seguidas → PARAR e reportar.
5. **reviewer** com output do gate + aceite. Lista → mesmo agente corrige → volta ao 4 (máx. 2 ciclos).
6. `PASS` → resumo de PR (5 bullets de `~/.hx/i18n/pt-BR/skills/quality/pre-pr-gate.md`) + `~/.hx/i18n/pt-BR/skills/core/memory-distill.md`.
7. Perguntar antes de commit/push/PR.

## Pausas permitidas
Ambiguidade crítica · falha após 2 tentativas · antes de push/PR. Nenhuma outra.

## Saída final (≤ 20 linhas)
`ORIGEM` · `MODO` · `AGENTES` · `ARQUIVOS (arquivo:linha)` · `GATE` · `REVIEW` · `PR (5 bullets)` · `MEMÓRIA`
