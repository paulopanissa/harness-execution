<p align="center">
  <img src="../assets/banner.svg" alt="HX — Harness Execution" width="100%">
</p>

<p align="center">
  <a href="../LICENSE"><img alt="MIT" src="https://img.shields.io/badge/license-MIT-bd93f9?style=flat-square"></a>
  <img alt="Claude Code" src="https://img.shields.io/badge/Claude%20Code-ready-ff92d0?style=flat-square">
  <img alt="Codex CLI" src="https://img.shields.io/badge/Codex%20CLI-ready-6cc3d5?style=flat-square">
  <img alt="Python" src="https://img.shields.io/badge/python-3.11%2B-7ee0a1?style=flat-square">
  <img alt="deps" src="https://img.shields.io/badge/deps-stdlib%20only-f1c27d?style=flat-square">
</p>

<p align="center">
  <b>Um único harness de agentes para Claude Code e Codex CLI.</b><br>
  Menos tokens, nenhum <code>.md</code> de spec perdido no repo, e cada tarefa roteada para o agente certo da stack.
</p>

<p align="center"><a href="../README.md">English</a> · <b>Português</b></p>

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

### Atualizando

Não precisa reinstalar. O `update.py` faz fast-forward em `~/.hx`, atualiza os repos org (se ativos), sincroniza e valida. `config.yaml`, mods e memória ficam fora do git e não são tocados.

```bash
python3 ~/.hx/scripts/update.py --check   # tem versão nova?
python3 ~/.hx/scripts/update.py           # aplica (--autostash se você editou arquivos versionados)
```

O que mudou: [CHANGELOG.md](../CHANGELOG.md).

### Idioma

As regras vêm em inglês (também o mais barato em tokens). O conjunto completo em português fica em `i18n/pt-BR/`. Nos dois casos o agente responde no seu idioma.

```yaml
# ~/.hx/config.yaml
language: pt-BR   # en (padrão) | pt-BR
```

Depois rode `sync.py`. Arquivo sem tradução cai para o inglês.

## Usando nos seus projetos: nada para configurar

O HX mora **na sua máquina**, não nos repositórios. O instalador liga o `AGENTS.md` como seu `~/.claude/CLAUDE.md` global e `~/.codex/AGENTS.md`, e coloca o `/hx` nos comandos de usuário. Então:

- abra qualquer projeto (novo, clonado ou importado) e digite `/hx <tarefa>`; funciona direto;
- você **não** adiciona nada no `CLAUDE.md`, `.claude/` ou `.codex/` do projeto;
- nada do HX é commitado no projeto, e quem não usa HX não é afetado;
- o `CLAUDE.md` do próprio projeto continua valendo para regras de domínio (stack, comandos, estilo).

Também não precisa editar `~/.claude.json` ou `settings.json` na mão: o `sync.py` mescla os hooks necessários e guarda backup.

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

## Contexto: Graphify + ai-memory (recomendado)

O `AGENTS.md` manda o agente buscar contexto nesta ordem: **Graphify → ai-memory → leitura cirúrgica**. Os dois são opcionais. Sem eles, o HX cai no fallback (`rg` restrito ao módulo + `~/.hx/fallback-memory.jsonl`), mas gasta mais token.

### Graphify: grafo de código

[safishamsi/graphify](https://github.com/safishamsi/graphify) monta um grafo do repositório (símbolos, dependências, chamadas). O agente consulta pela CLI, sem ler arquivo inteiro.

```bash
uv tool install graphifyy            # ou: pipx install graphifyy  (pacote com dois "y")
graphify install                     # skill no Claude Code
graphify install --platform codex    # skill no Codex
```

Em cada repositório:

```bash
/graphify .                # no Claude Code (no Codex: $graphify .)
graphify hook install      # recria o grafo a cada commit/checkout
graphify update .          # depois de um git pull
```

A saída fica em `graphify-out/`. Coloque essa pasta no `.gitignore` do projeto. Código é processado localmente (tree-sitter); docs e imagens usam a sua chave da API.

### ai-memory: memória por query

[alphaonedev/ai-memory-mcp](https://github.com/alphaonedev/ai-memory-mcp) é um servidor MCP de memória em SQLite. O `explorer` busca gotchas com 1 a 3 queries, e a skill `memory-distill` grava 3 a 5 fatos permanentes ao fim de cada tarefa.

```bash
cargo install ai-memory
# macOS/Linux, alternativa:
curl -fsSL https://raw.githubusercontent.com/alphaonedev/ai-memory-mcp/main/install.sh | sh
```

Registre com o nome **`ai-memory`**, que é o nome que o `AGENTS.md` usa. Prefira caminho absoluto no `--db`:

```bash
claude mcp add ai-memory --scope user -- ai-memory --db "$HOME/.claude/ai-memory.db" mcp --tier semantic
codex mcp add ai-memory -- ai-memory --db "$HOME/.claude/ai-memory.db" mcp --tier semantic
```

Usar o mesmo `--db` nos dois faz Claude Code e Codex dividirem a mesma memória. Ferramentas expostas: `memory_store`, `memory_recall`, `memory_search`.

Usa Obsidian? Troque por um MCP de memória que grava no vault, como [mem-vault](https://github.com/jagoff/mem-vault) ou [obsidian-memory-mcp](https://github.com/YuNaga224/obsidian-memory-mcp), e registre com o nome `ai-memory`. A regra continua: o agente consulta por query e nunca lê o vault inteiro.

### Sem nenhum dos dois

Funciona igual, só que mais caro. A memória vai para `~/.hx/fallback-memory.jsonl`, uma linha JSON por fato, e é buscada com `rg`.

## Medindo tokens

```bash
python3 ~/.hx/scripts/measure.py baseline --lang all     # quanto o HX adiciona ao contexto
python3 ~/.hx/scripts/measure.py sessions --days 7       # uso real pelos transcripts locais
python3 ~/.hx/scripts/measure.py sessions --project minha-api --tool claude --json
```

`baseline` estima a parte sempre carregada (`AGENTS.md` + descrições de agentes/comandos, cerca de 1,6k tokens) e cada arquivo sob demanda. `sessions` soma o uso gravado pelo Claude Code (`~/.claude/projects`) e pelo Codex (`~/.codex/sessions`) por projeto: input sem cache, escrita e leitura de cache, output e taxa de acerto do cache. Nada sai da sua máquina.

## Estrutura

```text
~/.hx
├── AGENTS.md            fonte única de regras (Claude + Codex)
├── agents/              6 agentes → .md (Claude) e .toml (Codex)
├── commands/            /hx e subcomandos
├── skills/              core · quality · stack · gamedev (sob demanda)
├── i18n/pt-BR/          conjunto completo de regras em português
├── hooks/               block-spec-md · read-guard · org-only · strip-legacy-oc
├── scripts/             install · update · sync · gate · measure · mod · check_updates
├── tests/               suíte unittest (roda no CI em Ubuntu e Windows)
├── mods/                catálogo + hx-skin
└── vendor/              (local) módulo org privado
```

## Regras que o `AGENTS.md` impõe

- Respostas curtas; nunca repetir código já salvo, citar `arquivo:linha`.
- Contexto: grafo de código → memória por query → leitura cirúrgica. Nada de varrer o repo inteiro.
- Garantido por hook, não só por prompt: nada de `.md` intermediário de plano/spec (`block-spec-md.sh`) nem leitura inteira de arquivo com mais de 400 linhas (`read-guard.sh`; bypass `HX_ALLOW_READ=1`).
- Docs de biblioteca via Context7 antes de chutar API.
- Conventional commits; commit, push e PR só com confirmação.
- Bug: causa raiz antes de editar; 3 tentativas falhas → para e reporta.

## Desenvolvimento

```bash
python3 -m unittest discover -s tests -t tests
```

A suíte roda sync, update e os hooks num sandbox descartável (`HX_HOME`, Claude e Codex próprios), sem tocar na sua instalação real.

## Licença

[MIT](../LICENSE). Use, adapte, mande PR.
