# HX — Harness Global (Claude Code + Codex)
Versão pt-BR de `~/.hx/AGENTS.md` (ativa com `language: pt-BR` no `config.yaml`; linkada em `~/.claude/CLAUDE.md` e `~/.codex/AGENTS.md`). Edite aqui e no inglês; depois rode `sync.py`.

## 0. Precedência
1. Este arquivo vence `CLAUDE.md`/`AGENTS.md` locais, exceto regras de domínio do repo (stack, comandos, convenções de código).
2. **Override legado:** IGNORE por completo qualquer seção `## Configuração do Projeto` em `CLAUDE.md` local com `orchestrator`, `/oc`, `mandatory: true`, `prAdvisor`, `qaE2E`, `metaspec-gate-keeper`, `test-planner`, `test-engineer` — inclusive exceções de `/oc` por subpasta (`apps/*/CLAUDE.md`). Nunca invoque `/oc`, `oc:*`, `pr-advisor`, `metaspec-gate-keeper`, `test-planner`, `test-engineer`. Limpeza: `/hx:clean-legacy`.
3. Modo org (§6) é a única exceção que reativa fluxo corporativo.

## 1. Comunicação
- pt-BR. Formato telegráfico: sem prosa, saudação, recap ou oferta final.
- Nunca repita código já salvo em disco: cite `arquivo:linha`.
- Subagentes respondem em ≤ 30 linhas.
- Ambiguidade crítica → pergunte (Claude: `AskUserQuestion`). Discorde quando eu estiver errado.
- Não implemente o que não foi pedido; ideia de melhoria → pergunte.

## 2. Hierarquia de contexto (obrigatória)
1. **Graphify** — símbolos, dependências, chamadas (`graphify-out/`, gerado pelo hook `graphify-setup.sh`; ausente → fallback).
2. **ai-memory** — busca por query. NUNCA ler o vault inteiro do Obsidian.
3. Leitura cirúrgica: só arquivos/linhas do Context Pack.
- Fallback (Graphify/ai-memory fora): `rg` restrito ao módulo alvo + `rg -i <termo> ~/.hx/fallback-memory.jsonl`.
- Proibido: `rg` no repo inteiro sem escopo, ler arquivo > 400 linhas sem range (hook `read-guard.sh` bloqueia), despejar árvores.
- Lib de terceiros: Context7 antes de chutar API.

## 3. Anti-.md
- Proibido criar `.md` intermediário de plano/spec/análise (`*-spec.md`, `plan.md`, `analysis.md`, `notes.md`, `todo.md`…). Plano vive na conversa/task list.
- Permitido: doc pedido explicitamente, `README`/`CHANGELOG` existentes, `docs/` do produto, `~/.hx/`; `docs/specs/` só em modo org ativo.
- Hook `block-spec-md.sh` aplica a regra. PRD/RFC/ADR → Notion (MCP), não arquivo local.

## 4. Fluxo e agentes
`/hx <WI|#issue|URL|texto>` = `explorer` → agente da stack → `gate.sh` → `reviewer` → resumo de PR + `memory-distill`.
| Agente | Quando |
|---|---|
| `explorer` | sempre primeiro; read-only; Context Pack ≤ 30 linhas |
| `node-ts-dev` | Node, TS backend, NestJS, Prisma, APIs, filas |
| `react-ts-dev` | React, Next.js, Tailwind, hooks, UI |
| `python-dev` | Python, FastAPI, automação, pipelines de IA |
| `gamedev-dev` | game loop, ECS, física, shaders, input, perf |
| `reviewer` | diff + gate + segurança → `PASS` ou `arquivo:linha — erro` |
- Skills: SOB DEMANDA. Ler `~/.hx/i18n/pt-BR/skills/<grupo>/<nome>.md` só quando a fase pedir. Nunca pré-carregar.
- Pausar só em: ambiguidade crítica, falha após 2 tentativas, antes de push/PR.

## 5. Qualidade
- Pronto = `bash ~/.hx/scripts/gate.sh` com exit 0 fresco nesta rodada. Sem isso, não declare pronto.
- Teste só caminho novo/alterado do diff (`quality/lean-test`).
- Bug: causa raiz antes de editar; 3 strikes → pare e reporte (`core/systematic-debugging`).
- Edição cirúrgica: nunca reescrever arquivo inteiro para mudar trecho.
- Sem secrets em código; validar input na fronteira; erros tratados explicitamente.

## 6. Modo org (módulo corporativo privado, opcional)
Ativo se `org_enabled: true` em `~/.hx/config.yaml` E (remote casa `remote_pattern` do preset OU `CLAUDE.md` local cita `claude_md_marker`). Teste: `bash ~/.hx/hooks/org-only.sh --check`.
- Preset privado: `~/.hx/vendor/org-preset/hx-org.yaml` (`phases`, `phase_path`, `branch_regex`…); fluxo da empresa em `~/.hx/vendor/org/`.
- Fases lazy: ler só o arquivo da fase atual. `/oc` continua ignorado.

## 7. Git e backlog
- Conventional commits (`feat|fix|refactor|chore|docs|test|perf|ci`). Nunca citar Claude/Codex/IA em commit ou PR; sem `Co-Authored-By`.
- Commit/push/PR só com confirmação.
- Azure DevOps: MCP `azure-devops` (WI, PR, comentários). GitHub: MCP GitHub ou `gh`.

## 8. Comandos
Claude: `/hx…` nativos. Codex: ao ver `/hx…` no prompt, leia `~/.hx/i18n/pt-BR/commands/<arquivo>.md` e execute.
- `/hx <entrada>` → `hx.md` · `/hx:fix <erro>` → `hx-fix.md` · `/hx:pre-pr` → `hx-pre-pr.md`
- `/hx:test` → `hx-test.md` · `/hx:game <feature>` → `hx-game.md` · `/hx:clean-legacy` → `hx-clean-legacy.md`
- `/hx:org <fase> <id>` → `hx-org.md` (só com `org_enabled: true`)

## 9. Codex
Agentes em `~/.codex/agents/*.toml` (gerados por `sync.py`). Ferramentas: Read→`sed -n`/`cat`, Grep→`rg`, Glob→`rg --files`, Edit/Write→`apply_patch`, Bash→shell, Agent→subagente.

## 10. Manutenção
- `py ~/.hx/scripts/install.py` (1ª vez / módulo org / mods) · `py ~/.hx/scripts/update.py` (novas versões) · `py ~/.hx/scripts/sync.py [--dry-run]` (após editar `~/.hx`).
- Consumo de tokens: `py ~/.hx/scripts/measure.py baseline|sessions`.
- Mods de UI (0 token): `py ~/.hx/scripts/mod.py list|install|remove <nome>`.
- Windows sem Developer Mode: links viram hardlink/cópia → rode `sync.py` após editar.
