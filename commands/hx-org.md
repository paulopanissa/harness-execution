---
description: One phase of the org module flow (corporate, lazy) — e.g. discovery | kickoff | work | pre-pr | pr
argument-hint: <phase> <id>
---
Args: $ARGUMENTS → `<phase> <id>`

1. `org_enabled: true` in `~/.hx/config.yaml`? No → reply `Org module disabled: run python3 ~/.hx/scripts/install.py --org <preset-url>` and stop.
2. Valid phases: `bash ~/.hx/hooks/org-only.sh --get phases` (comma-separated). Invalid phase → list them and stop.
3. Phase path: `bash ~/.hx/hooks/org-only.sh --get phase_path` with `{phase}` replaced, relative to `~/.hx/vendor/org/`. Read ONLY that file. Missing → report the path and stop.
4. Run the phase for `<id>` following the file. Branch: `--get branch_regex` with `{id}` replaced.
5. Ignore `/oc` and legacy `CLAUDE.md` sections. Any `.md` the phase requires goes in `docs/specs/`.
6. In `work`: `explorer` + stack agent + `bash ~/.hx/scripts/gate.sh`.
7. PR/push phase: ask for confirmation first.
