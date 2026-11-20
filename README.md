<p align="center">
  <img src="assets/banner.svg" alt="HX — Harness Execution" width="100%">
</p>

<p align="center">
  <a href="LICENSE"><img alt="MIT" src="https://img.shields.io/badge/license-MIT-bd93f9?style=flat-square"></a>
  <img alt="Claude Code" src="https://img.shields.io/badge/Claude%20Code-ready-ff92d0?style=flat-square">
  <img alt="Codex CLI" src="https://img.shields.io/badge/Codex%20CLI-ready-6cc3d5?style=flat-square">
  <img alt="Python" src="https://img.shields.io/badge/python-3.11%2B-7ee0a1?style=flat-square">
  <img alt="deps" src="https://img.shields.io/badge/deps-stdlib%20only-f1c27d?style=flat-square">
</p>

<p align="center">
  <b>Um único harness de agentes para Claude Code e Codex CLI.</b><br>
  Menos tokens, nenhum <code>.md</code> de spec perdido no repo, e cada tarefa roteada para o agente certo da stack.
</p>

---

## Por que existe

Agentes de código gastam token em três lugares: contexto que ninguém pediu, texto que ninguém lê e retrabalho por falta de validação. O HX ataca os três:

| Problema | O que o HX faz |
|---|---|
| Contexto inchado | Hierarquia obrigatória: grafo de código → memória por query → leitura cirúrgica. O `explorer` entrega um **Context Pack de no máximo 30 linhas**. |
| Skills pré-carregadas | Skills ficam em `skills/` e só são lidas **quando a fase pede**. Nada entra no prompt por padrão. |
| `plan.md`, `analysis.md`, `notes.md`… | Hook `block-spec-md.sh` **bloqueia** a criação de `.md` intermediário. Plano vive na conversa. |
| "Pronto" sem prova | `gate.sh` roda typecheck, lint e testes **só dos arquivos alterados**. Sem `GATE: PASS`, não está pronto. |
| Duas ferramentas, duas configs | `AGENTS.md` é a fonte única, linkada em `~/.claude/CLAUDE.md` e `~/.codex/AGENTS.md`. Agentes viram `.md` (Claude) e `.toml` (Codex) gerados pelo `sync.py`. |

## Instalação

Requisitos: `git`, `bash` (no Windows, Git Bash) e Python 3.11+. Sem dependências externas.

```bash
git clone https://github.com/paulopanissa/harness-execution ~/.hx
python3 ~/.hx/scripts/install.py      # Windows: py ~/.hx/scripts/install.py
```

O instalador:

1. pergunta se você quer um **módulo corporativo privado** (opcional, veja abaixo);
2. grava `~/.hx/config.yaml`, liga `AGENTS.md`, agentes, comandos e hooks no Claude Code e no Codex;
3. valida tudo (links, frontmatter, TOML, hooks);
4. oferece os **mods de UI** do catálogo. Nenhum vem marcado; você escolhe.

Flags para rodar sem perguntas: `--no-org`, `--org <url>`, `--mods filetree,hx-skin`, `--no-mods`.

Depois de editar qualquer coisa em `~/.hx`, rode `python3 ~/.hx/scripts/sync.py` (`--dry-run` para ver antes).

## Fluxo

```text
/hx <issue | WI | URL | texto>
  └─ explorer        read-only, Context Pack ≤ 30 linhas
      └─ agente da stack   node-ts-dev · react-ts-dev · python-dev · gamedev-dev
          └─ gate.sh       typecheck + lint + testes relacionados ao diff
              └─ reviewer  PASS  ou  arquivo:linha — erro
                  └─ resumo de PR (5 bullets) + destilação de memória
```

Pausa só em três casos: ambiguidade crítica, falha após 2 tentativas, antes de push/PR.

### Comandos

| Comando | Faz |
|---|---|
| `/hx <entrada>` | pipeline completo acima |
| `/hx:fix <erro>` | causa raiz primeiro, correção mínima, gate |
| `/hx:test` | testes só do caminho novo/alterado |
| `/hx:pre-pr` | gate + review + resumo de PR |
| `/hx:game <feature>` | fluxo de gamedev (loop, ECS, perf budget) |
| `/hx:clean-legacy` | remove configs de orquestradores antigos do `CLAUDE.md` |
| `/hx:org <fase> <id>` | fase do fluxo corporativo (só com módulo org ativo) |

No Codex, os mesmos comandos funcionam como texto: o `AGENTS.md` instrui o agente a ler `~/.hx/commands/<arquivo>.md`.

### Agentes

| Agente | Quando | Acesso |
|---|---|---|
| `explorer` | sempre primeiro | read-only |
| `node-ts-dev` | Node, NestJS, Prisma, APIs, filas | escrita |
| `react-ts-dev` | React, Next.js, Tailwind, UI | escrita |
| `python-dev` | Python, FastAPI, automação, IA | escrita |
| `gamedev-dev` | game loop, ECS, física, shaders | escrita |
| `reviewer` | diff + gate + segurança | read-only |

Modelo por tier (`fast`, `default`, `deep`) é configurável em `config.yaml`, separado para Claude e Codex.

## Mods de UI

Mods mudam a interface do Claude Code (painéis, barras, temas). **Rodam fora do modelo: zero token**, salvo onde o catálogo avisa.

```bash
python3 ~/.hx/scripts/mod.py list
python3 ~/.hx/scripts/mod.py install hx-skin filetree
python3 ~/.hx/scripts/mod.py remove filetree
```

| Mod | O que é | Origem |
|---|---|---|
| `filetree` | árvore de arquivos lidos/editados, ao vivo | [data-goblin/claude-code-filetree](https://github.com/data-goblin/claude-code-filetree) |
| `blast-radius` | impacto de cada edição | [hamzafer/claude-code-mods](https://github.com/hamzafer/claude-code-mods) |
| `savvy-progress` | barra de progresso do turno | [Berkay2002/berkays-mods](https://github.com/Berkay2002/berkays-mods) |
| `hx-skin` | skins **Dusk** (Drácula refinado), **Ember** e **Tide**; `/hx-skin` troca | este repo, `mods/hx-skin` |
| `claude-skins` | pacote da comunidade (manual) | [basicScandal/claude-skins](https://github.com/basicScandal/claude-skins) |

O catálogo (`mods/catalog.json`) tem uma lista `codex` reservada para quando o Codex tiver mods equivalentes. PRs com novos mods são bem-vindos.

## Módulo org (privado e opcional)

Empresas costumam ter um fluxo próprio (fases, padrão de branch, guardas). O HX **não traz nada disso no repo público**. Ele só sabe ler um *preset* que você mantém num repositório privado:

```yaml
# hx-org.yaml (no SEU repo privado)
name: acme
vendor_repo: git@github.com:acme/agent-flow.git   # onde ficam os arquivos de cada fase
remote_pattern: github\.com[:/]acme/              # ativa só em repos da empresa
claude_md_marker: acme-agent-flow                 # ou quando o CLAUDE.md local cita isto
phase_path: phases/{phase}.md
phases: discovery,kickoff,work,pre-pr,pr
branch_regex: ^(fix|feat|chore|refactor)/{id}$
guard_hooks: test-db-guard.js                     # opcional, hooks do vendor
```

```bash
python3 ~/.hx/scripts/install.py --org git@github.com:acme/hx-preset.git
```

Preset e fluxo são clonados em `~/.hx/vendor/` (ignorado pelo git) e atualizados em background a cada `auto_update_days`. Fora dos repos da empresa, o modo org fica desligado sozinho.

## Estrutura

```text
~/.hx
├── AGENTS.md            fonte única de regras (Claude + Codex)
├── agents/              6 agentes → .md (Claude) e .toml (Codex)
├── commands/            /hx e subcomandos
├── skills/              core · quality · stack · gamedev (sob demanda)
├── hooks/               block-spec-md · org-only · strip-legacy-oc
├── scripts/             install · sync · gate · mod · check_updates
├── mods/                catálogo + hx-skin
└── vendor/              (local) módulo org privado
```

## Regras que o `AGENTS.md` impõe

- Respostas curtas; nunca repetir código já salvo, citar `arquivo:linha`.
- Contexto: grafo de código → memória por query → leitura cirúrgica. Nada de varrer o repo inteiro.
- Docs de biblioteca via Context7 antes de chutar API.
- Conventional commits; commit, push e PR só com confirmação.
- Bug: causa raiz antes de editar; 3 tentativas falhas → para e reporta.

As regras estão em português, mas são fáceis de adaptar: edite `AGENTS.md` e rode `sync.py`.

## English (short)

**HX** is a single agent harness for **Claude Code** and **Codex CLI**. One `AGENTS.md`, six routed agents, on-demand skills, a diff-scoped quality gate, a hook that blocks throwaway spec/plan Markdown files, and an optional zero-token UI mods catalog. Corporate workflows live in a private preset repo, never here.

```bash
git clone https://github.com/paulopanissa/harness-execution ~/.hx
python3 ~/.hx/scripts/install.py
```

## Licença

[MIT](LICENSE). Use, adapte, mande PR.
