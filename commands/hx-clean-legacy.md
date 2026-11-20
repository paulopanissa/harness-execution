---
description: Remove the legacy "## Configuração do Projeto" (/oc) section from the current repo's CLAUDE.md
argument-hint: [path to CLAUDE.md]
---
Target: $ARGUMENTS (empty → `CLAUDE.md` at the repo root: `git rev-parse --show-toplevel`)

1. `bash ~/.hx/hooks/strip-legacy-oc.sh <target> --dry-run` → show the diff.
2. Nothing to remove → say so and stop.
3. Confirm with the user. Yes → `bash ~/.hx/hooks/strip-legacy-oc.sh <target>` (backup at `<target>.hx-bak`).
4. Repeat for `apps/*/CLAUDE.md` files that have the section (`rg -l "Configura(ç|c)(ã|a)o do Projeto" -g CLAUDE.md`).
5. Do not commit.
