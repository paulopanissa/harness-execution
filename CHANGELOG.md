# Changelog

All notable changes to HX. Versions follow [SemVer](https://semver.org/). Update an existing install with `python ~/.hx/scripts/update.py`.

## [Unreleased]
### Added
- `CONTRIBUTING.md` (EN + pt-BR), `SECURITY.md`, `CODEOWNERS`, issue and PR templates, Dependabot for GitHub Actions (patch/minor bumps auto-merge after CI).
- `hooks/graphify-setup.sh` (`SessionStart`, registered by `sync.py`, checked by `install.py`): in any git repo, adds `graphify-out/` to `.gitignore`, builds a code-only graph in the background (`graphify extract --code-only`, no LLM) and runs `graphify hook install` when missing. Warns once per repo when `graphify` is not installed. Opt out with `HX_NO_GRAPHIFY=1`; log in `~/.hx/.graphify.log`.
- Codex skills: `sync.py` generates `$hx`, `$hx-fix`, `$hx-pre-pr`... in `~/.agents/skills/` (override with `HX_CODEX_SKILLS_HOME`), since the Codex TUI rejects custom `/hx` commands.
- Optional [RTK](https://github.com/rtk-ai/rtk) integration: `rtk: true` in `config.yaml` (or `install.py --rtk` / `--no-rtk`) makes `sync.py` register `rtk hook claude` and `rtk hook codex` as `PreToolUse` Bash hooks, only when `rtk` is on the `PATH`. `AGENTS.md` tells the agent to use `rtk bypass <cmd>` when filtered output lacks detail.

### Changed
- `gate.sh` saves the full output of a failing step to `~/.hx/state/gate-last-fail.log` (override with `HX_GATE_LOG`) and prints its path as `log completo:`, so the agent reads it with a range instead of rerunning the gate.

## [0.2.0] - 2026-11-20
### Added
- `scripts/update.py`: update in place (fast-forward pull, org repos, sync, validation). `--check` only reports.
- `scripts/measure.py`: `baseline` (static HX footprint per language) and `sessions` (real token usage from Claude Code and Codex transcripts).
- `hooks/read-guard.sh`: blocks reading a file over 400 lines without `offset`/`limit` (`HX_ALLOW_READ=1` bypass, `HX_READ_MAX_LINES` to tune).
- Rules in English by default; full pt-BR set in `i18n/pt-BR/`, selected with `language: pt-BR` in `config.yaml`.
- Test suite (`tests/`, stdlib `unittest`) and GitHub Actions CI on Ubuntu and Windows.
- `VERSION` and this changelog.

### Changed
- Agents, commands, skills and `AGENTS.md` translated to English.
- Anti-`.md` hook: `review*.md` narrowed to `review.md`, `review-*.md`, `*-review.md` (no longer blocks `reviewer.md`).

## [0.1.0] - 2026-11-19
### Added
- Initial harness: `/hx` flow, 6 agents, commands, skills, deterministic gate, anti-`.md` hook, optional private org module, UI mods catalog.
