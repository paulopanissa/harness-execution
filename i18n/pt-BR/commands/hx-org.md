---
description: Fase do fluxo do módulo org (corporativo, lazy) — ex.: discovery | kickoff | work | pre-pr | pr
argument-hint: <fase> <id>
---
Args: $ARGUMENTS → `<fase> <id>`

1. `org_enabled: true` em `~/.hx/config.yaml`? Não → responder `Módulo org desativado: rode py ~/.hx/scripts/install.py --org <url-do-preset>` e parar.
2. Fases válidas: `bash ~/.hx/hooks/org-only.sh --get phases` (lista separada por vírgula). Fase inválida → listar e parar.
3. Caminho da fase: `bash ~/.hx/hooks/org-only.sh --get phase_path` com `{phase}` substituído, relativo a `~/.hx/vendor/org/`. Ler SOMENTE esse arquivo. Ausente → reportar caminho e parar.
4. Executar a fase para `<id>` seguindo o arquivo. Branch: `--get branch_regex` com `{id}` substituído.
5. Ignorar `/oc` e seções legadas de `CLAUDE.md`. `.md` exigido pela fase vai em `docs/specs/`.
6. Em `work`: `explorer` + agente da stack + `bash ~/.hx/scripts/gate.sh`.
7. Fase de PR/push: pedir confirmação antes.
