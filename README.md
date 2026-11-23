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
  <b>One agent harness for Claude Code and Codex CLI.</b><br>
  Fewer tokens, no throwaway spec <code>.md</code> files in your repo, and every task routed to the right stack agent.
</p>

<p align="center"><b>English</b> · <a href="docs/README.pt-BR.md">Português</a></p>

---

## Why

Coding agents burn tokens in three places: context nobody asked for, text nobody reads, and rework caused by skipped validation. HX goes after all three:

| Problem | What HX does |
|---|---|
| Bloated context | A fixed lookup order: code graph → memory by query → surgical reads. The `explorer` agent returns a **Context Pack of at most 30 lines**. |
| Preloaded skills | Skills live in `skills/` and are read **only when a phase needs them**. Nothing enters the prompt by default. |
| `plan.md`, `analysis.md`, `notes.md`… | The `block-spec-md.sh` hook **blocks** creating intermediate Markdown. Plans stay in the conversation. |
| "Done" without proof | `gate.sh` runs typecheck, lint and tests **only for changed files**. No `GATE: PASS`, not done. |
| Two tools, two configs | `AGENTS.md` is the single source, linked to `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md`. Agents are generated as `.md` (Claude) and `.toml` (Codex) by `sync.py`. |

## Install

Requirements: `git`, `bash` and Python 3.11+. No third-party Python packages. On Windows, `bash` is the Git Bash that ships with Git for Windows: the hooks run in it, while `install.py`, `sync.py` and `update.py` run from PowerShell or Cmd.

### 1. Prerequisites

macOS (Homebrew):

```bash
brew install git python@3.12
```

Linux (Debian/Ubuntu; on Fedora use `sudo dnf install git python3`):

```bash
sudo apt install git python3
python3 --version   # must be 3.11 or newer
```

Windows (PowerShell or Cmd), then open a new terminal so the `PATH` is refreshed:

```powershell
winget install Git.Git
winget install Python.Python.3.12
```

### 2. Clone and run the installer

macOS / Linux:

```bash
git clone https://github.com/paulopanissa/harness-execution ~/.hx
python3 ~/.hx/scripts/install.py
```

Windows, PowerShell:

```powershell
git clone https://github.com/paulopanissa/harness-execution "$HOME\.hx"
py "$HOME\.hx\scripts\install.py"
```

Windows, Cmd:

```bat
git clone https://github.com/paulopanissa/harness-execution "%USERPROFILE%\.hx"
py "%USERPROFILE%\.hx\scripts\install.py"
```

The installer:

1. asks whether you want a **private org module** (optional, see below);
2. asks whether to turn on **RTK**, only if the `rtk` binary is already installed (see [Optional tools](#optional-tools-graphify-ai-memory-rtk));
3. writes `~/.hx/config.yaml` and wires `AGENTS.md`, agents, commands and hooks into Claude Code and Codex;
4. validates everything (links, frontmatter, TOML, hooks);
5. offers the **UI mods** from the catalog. Nothing is preselected; you choose.

Non-interactive flags: `--no-org`, `--org <url>`, `--mods filetree,hx-skin`, `--no-mods`, `--rtk`, `--no-rtk`.

After editing anything in `~/.hx`, run `sync.py` (`--dry-run` to preview).

> **Commands in this README** are written for macOS/Linux (`python3 ~/.hx/scripts/...`). On Windows use `py "$HOME\.hx\scripts\..."` in PowerShell or `py "%USERPROFILE%\.hx\scripts\..."` in Cmd. Tool CLIs (`graphify`, `rtk`, `claude`, `codex`) are the same on every OS unless a section says otherwise.

### Updating

No reinstall needed. `update.py` fast-forwards `~/.hx`, pulls the org repos if enabled, re-syncs and validates. Your `config.yaml`, mods and memory are git-ignored and stay untouched, so settings such as `rtk: true` survive. It does not update the optional tools; each one has its own upgrade command (see below).

```bash
python3 ~/.hx/scripts/update.py --check   # is there a new version?
python3 ~/.hx/scripts/update.py           # apply it (--autostash if you edited tracked files)
```

See [CHANGELOG.md](CHANGELOG.md) for what changed.

### Language

Rules ship in English (also the cheapest in tokens). A full Brazilian Portuguese set lives in `i18n/pt-BR/`. The agent always replies in your language either way.

```yaml
# ~/.hx/config.yaml
language: pt-BR   # en (default) | pt-BR
```

Then run `sync.py`. A file missing from a translation falls back to English.

## Using it in your projects: nothing to configure

HX lives on **your machine**, not in your repositories. The installer links `AGENTS.md` as your global `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md`, and puts `/hx` in your user commands. So:

- open any project (new, cloned, or imported) and type `/hx <task>`; it just works;
- you do **not** add anything to the project's `CLAUDE.md`, `.claude/` or `.codex/`;
- nothing from HX is committed to the project, and teammates without HX are not affected;
- the project's own `CLAUDE.md` still applies for domain rules (stack, commands, code style).

You do not need to edit `~/.claude.json` or `settings.json` by hand either: `sync.py` merges the hooks it needs and keeps a backup.

## Optional tools: Graphify, ai-memory, RTK

`AGENTS.md` tells the agent to gather context in this order: **Graphify → ai-memory → surgical reads**, and RTK trims the Bash output the agent reads. All three are recommended and all three are optional.

**They are separate open-source projects.** HX does not bundle, copy or fork their code, does not pin their branches and never downloads them. You install each binary yourself; HX only wires it in (rules in `AGENTS.md`, hooks registered by `sync.py`). A missing tool is skipped and nothing breaks.

| Tool | Saves tokens on | How HX wires it |
|---|---|---|
| [Graphify](https://github.com/safishamsi/graphify) | reading whole files to find symbols | `SessionStart` hook builds the graph per repo, automatically |
| [ai-memory](https://github.com/alphaonedev/ai-memory-mcp) | rediscovering the same gotchas | MCP server you register once; `explorer` and `memory-distill` query it |
| [RTK](https://github.com/rtk-ai/rtk) | long `git`, test and build output | `PreToolUse` Bash hook, registered by `sync.py` when `rtk: true` |

> The one-line installers below pipe a remote script into your shell. Read the script first if you do not trust the source.

### Graphify: code graph

Graphify builds a graph of your repository (symbols, dependencies, call sites). The agent queries it through the CLI instead of reading whole files.

Install `uv` first:

| OS | Command |
|---|---|
| macOS | `brew install uv` |
| Linux | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Windows (PowerShell or Cmd) | `winget install astral-sh.uv` |

Then, on any OS and shell:

```bash
uv tool install graphifyy            # the package name has two "y" (or: pipx install graphifyy)
graphify install                     # Claude Code skill
graphify install --platform codex    # Codex skill
```

`graphify` not found afterwards? Run `uv tool update-shell` and open a new terminal. Upgrade later with `uv tool upgrade graphifyy`.

**Automatic setup (Claude Code).** `sync.py` registers the `SessionStart` hook `hooks/graphify-setup.sh`. No per-project config. When a session starts inside a git repository:

- `graphify` not on `PATH` → one short warning per repository, then silence (marker in `~/.hx/state/`).
- `graphify-out/` is added to the project's `.gitignore` if missing (idempotent, keeps the file's line endings).
- No `graphify-out/` yet → `graphify extract <repo> --code-only` runs in the background: local AST (tree-sitter) only, no LLM, no API key.
- Graphify git hooks missing → `graphify hook install` (rebuilds the graph on commit/checkout/merge; it also registers a merge driver in `.gitattributes`).
- Already set up → nothing. Errors never break the session; they go to `~/.hx/.graphify.log`.

Opt out with `HX_NO_GRAPHIFY=1`. Manual commands still work:

```bash
/graphify .                # full graph incl. docs/images (Codex: $graphify .); uses your model API key
graphify update .          # after a git pull
```

### ai-memory: memory by query

ai-memory is a SQLite-backed MCP memory server. `explorer` pulls gotchas with 1 to 3 queries, and the `memory-distill` skill stores 3 to 5 durable facts at the end of each task.

Install:

macOS / Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/alphaonedev/ai-memory-mcp/main/install.sh | sh
```

Windows, PowerShell:

```powershell
irm https://raw.githubusercontent.com/alphaonedev/ai-memory-mcp/main/install.ps1 | iex
```

Windows, Cmd:

```bat
powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/alphaonedev/ai-memory-mcp/main/install.ps1 | iex"
```

Any OS with Rust: `cargo install ai-memory`.

Register it under the name **`ai-memory`**, which is the name `AGENTS.md` uses. Use an absolute `--db` path; on Windows write it with forward slashes.

macOS / Linux:

```bash
claude mcp add ai-memory --scope user -- ai-memory --db "$HOME/.claude/ai-memory.db" mcp --tier semantic
codex mcp add ai-memory -- ai-memory --db "$HOME/.claude/ai-memory.db" mcp --tier semantic
```

Windows, PowerShell (quote `'--'`: npm and Volta install `claude`/`codex` as `.ps1` shims, and PowerShell swallows a bare `--` before it reaches them):

```powershell
$db = "$($HOME -replace '\\','/')/.claude/ai-memory.db"
claude mcp add ai-memory --scope user '--' ai-memory --db $db mcp --tier semantic
codex mcp add ai-memory '--' ai-memory --db $db mcp --tier semantic
```

Windows, Cmd:

```bat
claude mcp add ai-memory --scope user -- ai-memory --db "%USERPROFILE:\=/%/.claude/ai-memory.db" mcp --tier semantic
codex mcp add ai-memory -- ai-memory --db "%USERPROFILE:\=/%/.claude/ai-memory.db" mcp --tier semantic
```

Check with `claude mcp list` / `codex mcp list`. Pointing both tools at the same `--db` lets Claude Code and Codex share one memory. Tools exposed: `memory_store`, `memory_recall`, `memory_search`.

Using Obsidian? Swap in a vault-backed memory MCP such as [mem-vault](https://github.com/jagoff/mem-vault) or [obsidian-memory-mcp](https://github.com/YuNaga224/obsidian-memory-mcp) and register it as `ai-memory`. The rule stays the same: the agent queries memory and never reads the whole vault.

### RTK: filtered Bash output

RTK rewrites the agent's Bash commands before they run (`git status` → `rtk git status`) and returns compact output. You keep working as usual; the savings show up in `rtk gain`.

1. Install the binary:

   | OS | Command |
   |---|---|
   | macOS, or Linux with Homebrew | `brew install rtk` |
   | Linux, macOS, WSL, Git Bash | `curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh \| sh` |
   | Windows (PowerShell or Cmd) | `winget install rtk-ai.rtk` |

2. Turn it on in HX, either way:

   ```bash
   python3 ~/.hx/scripts/install.py --rtk   # or set "rtk: true" in ~/.hx/config.yaml and run sync.py
   ```

   `sync.py` then adds `rtk hook claude` to `~/.claude/settings.json` and `rtk hook codex` to `~/.codex/hooks.json`. The hook is added only when `rtk: true` **and** `rtk` is on the `PATH`, so Bash never breaks.

3. Restart Claude Code and Codex so they see the new `PATH`.

4. Check: `rtk init --show` lists `[ok] Hook: rtk hook claude` (its `RTK.md: not found` line is expected: the RTK rule lives in `AGENTS.md`). After some work, `rtk gain` shows the tokens saved.

Good to know:

- When filtered output hides a detail, the agent runs `rtk bypass <cmd>` on its own.
- Only the **Bash** tool is filtered. Commands Claude Code runs through its PowerShell tool are not.
- `gate.sh` is not affected: the commands inside it run unfiltered, and on failure it keeps the full log in `~/.hx/state/gate-last-fail.log`.
- Upgrade: `brew upgrade rtk` or `winget upgrade rtk-ai.rtk` (`update.py` does not touch the binary).
- Turn off: `rtk: false` stops `sync.py` from adding the hook but does not remove an existing one (RTK may have installed it itself). Remove it for good with `rtk init -g --uninstall`.

### Without any of them

Everything still works, at a higher token cost. Memory goes to `~/.hx/fallback-memory.jsonl` (one JSON line per fact) and is searched with `rg`.

## Flow

```text
/hx <issue | work item | URL | text>
  └─ explorer          read-only, Context Pack ≤ 30 lines
      └─ stack agent   node-ts-dev · react-ts-dev · python-dev · gamedev-dev
          └─ gate.sh   typecheck + lint + tests related to the diff
              └─ reviewer  PASS  or  file:line — error
                  └─ PR summary (5 bullets) + memory distillation
```

The agent pauses only for: critical ambiguity, failure after 2 attempts, and before push/PR.

### Commands

| Command | Does |
|---|---|
| `/hx <input>` | the full flow above |
| `/hx:fix <error>` | root cause first, minimal fix, gate |
| `/hx:test` | tests only for new/changed paths |
| `/hx:pre-pr` | gate + review + PR summary |
| `/hx:game <feature>` | gamedev flow (loop, ECS, perf budget) |
| `/hx:clean-legacy` | strips old orchestrator config from `CLAUDE.md` |
| `/hx:org <phase> <id>` | one phase of the org flow (org module only) |

In Codex the TUI rejects custom `/hx` commands, so `sync.py` generates them as skills: type `$hx`, `$hx-fix`, `$hx-pre-pr`… (in `~/.agents/skills/`). A `/hx…` typed as plain text still works: `AGENTS.md` tells the agent to read `~/.hx/commands/<file>.md`.

### Agents

| Agent | When | Access |
|---|---|---|
| `explorer` | always first | read-only |
| `node-ts-dev` | Node, NestJS, Prisma, APIs, queues | write |
| `react-ts-dev` | React, Next.js, Tailwind, UI | write |
| `python-dev` | Python, FastAPI, automation, AI pipelines | write |
| `gamedev-dev` | game loop, ECS, physics, shaders | write |
| `reviewer` | diff + gate + security | read-only |

Models per tier (`fast`, `default`, `deep`) are set in `config.yaml`, separately for Claude and Codex.

## UI mods

Mods change the Claude Code interface (panes, bars, themes). **They run outside the model: zero tokens**, unless the catalog says otherwise.

```bash
python3 ~/.hx/scripts/mod.py list
python3 ~/.hx/scripts/mod.py install hx-skin filetree
python3 ~/.hx/scripts/mod.py remove filetree
```

| Mod | What it is | Source |
|---|---|---|
| `filetree` | live tree of files read/edited | [data-goblin/claude-code-filetree](https://github.com/data-goblin/claude-code-filetree) |
| `blast-radius` | impact of each edit | [hamzafer/claude-code-mods](https://github.com/hamzafer/claude-code-mods) |
| `savvy-progress` | turn progress bar | [Berkay2002/berkays-mods](https://github.com/Berkay2002/berkays-mods) |
| `hx-skin` | **Dusk** (a refined Dracula), **Ember** and **Tide** skins; `/hx-skin` switches | this repo, `mods/hx-skin` |
| `claude-skins` | community skin pack (manual install) | [basicScandal/claude-skins](https://github.com/basicScandal/claude-skins) |

The catalog (`mods/catalog.json`) has a `codex` list reserved for when Codex gets equivalent mods. PRs adding mods are welcome.

## Org module (private, optional)

Companies usually have their own flow (phases, branch naming, guard hooks). **None of that ships in this repo.** HX only knows how to read a *preset* that you keep in a private repository:

```yaml
# hx-org.yaml (in YOUR private repo)
name: acme
vendor_repo: git@github.com:acme/agent-flow.git   # where each phase file lives
remote_pattern: github\.com[:/]acme/              # active only in company repos
claude_md_marker: acme-agent-flow                 # or when the local CLAUDE.md mentions this
phase_path: phases/{phase}.md
phases: discovery,kickoff,work,pre-pr,pr
branch_regex: ^(fix|feat|chore|refactor)/{id}$
guard_hooks: test-db-guard.js                     # optional, hooks from the vendor repo
```

```bash
python3 ~/.hx/scripts/install.py --org git@github.com:acme/hx-preset.git
```

The preset and the flow repo are cloned into `~/.hx/vendor/` (git-ignored) and refreshed in the background every `auto_update_days`. Outside company repos, org mode turns itself off.

## Measuring tokens

```bash
python3 ~/.hx/scripts/measure.py baseline --lang all     # what HX adds to context
python3 ~/.hx/scripts/measure.py sessions --days 7       # real usage from local transcripts
python3 ~/.hx/scripts/measure.py sessions --project my-api --tool claude --json
```

`baseline` estimates the always-loaded part (`AGENTS.md` + agent/command descriptions, about 1.6k tokens) and each on-demand file. `sessions` sums the usage recorded by Claude Code (`~/.claude/projects`) and Codex (`~/.codex/sessions`) per project: uncached input, cache writes, cache reads, output and cache hit rate. Nothing leaves your machine.

## Layout

```text
~/.hx
├── AGENTS.md            single source of rules (Claude + Codex)
├── agents/              6 agents → .md (Claude) and .toml (Codex)
├── commands/            /hx and subcommands
├── skills/              core · quality · stack · gamedev (on demand)
├── i18n/pt-BR/          full Brazilian Portuguese rule set
├── hooks/               block-spec-md · read-guard · org-only · strip-legacy-oc
├── scripts/             install · update · sync · gate · measure · mod · check_updates
├── tests/               unittest suite (run in CI on Ubuntu and Windows)
├── mods/                catalog + hx-skin
├── docs/                translations
└── vendor/              (local) private org module
```

## Rules enforced by `AGENTS.md`

- Short answers; never repeat code already on disk, cite `file:line`.
- Context: code graph → memory by query → surgical reads. No repo-wide scans.
- Enforced by hooks, not only by prompt: no intermediate plan/spec `.md` (`block-spec-md.sh`), no whole-file read over 400 lines (`read-guard.sh`; bypass `HX_ALLOW_READ=1`).
- Library docs via Context7 before guessing an API.
- Conventional commits; commit, push and PR only after confirmation.
- Bugs: root cause before editing; 3 failed attempts → stop and report.

## Development

```bash
python3 -m unittest discover -s tests -t tests
```

The suite runs sync, update and the hooks inside a throwaway sandbox (its own `HX_HOME`, Claude and Codex homes), so it never touches your real install.

Pull requests are welcome; read [CONTRIBUTING.md](CONTRIBUTING.md) first. Security issues: [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE). Use it, adapt it, send a PR.
