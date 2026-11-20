#!/usr/bin/env bash
# block-spec-md.sh — hook PreToolUse (Write|Edit|MultiEdit).
# Bloqueia CRIAÇÃO de .md de spec/plano/análise fora de docs/ e ~/.hx/.
# docs/specs/ e docs/plans/ só são liberados em modo org ativo.
# Bypass pontual: HX_ALLOW_MD=1. Exit 2 = bloqueia (stderr volta ao agente).
set -u

HX="${HX_HOME:-$HOME/.hx}"
[ "${HX_ALLOW_MD:-0}" = "1" ] && exit 0

INPUT="$(cat)"

json_field() {
  printf '%s' "$INPUT" | tr -d '\r\n' |
    sed -nE "s/.*\"$1\"[[:space:]]*:[[:space:]]*\"(([^\"\\\\]|\\\\.)*)\".*/\\1/p" | head -n1
}

to_posix() {
  local p
  p="$(printf '%s' "$1" | sed -e 's#\\\\#/#g' -e 's#\\/#/#g' -e 's#\\#/#g')"
  if command -v cygpath >/dev/null 2>&1; then
    p="$(cygpath -u "$p" 2>/dev/null || printf '%s' "$p")"
  fi
  printf '%s' "$p" | tr '[:upper:]' '[:lower:]'
}

FILE_RAW="$(json_field file_path)"
[ -z "$FILE_RAW" ] && exit 0

case "$(printf '%s' "$FILE_RAW" | tr '[:upper:]' '[:lower:]')" in
  *.md|*.markdown) ;;
  *) exit 0 ;;
esac

FILE_NATIVE="$(printf '%s' "$FILE_RAW" | sed -e 's#\\\\#/#g' -e 's#\\/#/#g')"
[ -e "$FILE_NATIVE" ] && exit 0   # editar arquivo existente é permitido

FILE="$(to_posix "$FILE_RAW")"
HXP="$(to_posix "$HX")"
case "$FILE" in "$HXP"/*) exit 0 ;; esac

BASE="${FILE##*/}"
IN_SPEC_DIR=0
case "$FILE" in */specs/*|*/spec/*|*/plans/*|*/.plans/*|*/planning/*) IN_SPEC_DIR=1 ;; esac

SPEC_NAME=0
case "$BASE" in
  *-spec.md|*.spec.md|*_spec.md|spec.md|specs.md|*-specs.md|metaspec*.md|\
  plan.md|*-plan.md|*_plan.md|plano*.md|planning*.md|implementation*.md|\
  analysis.md|*-analysis.md|*_analysis.md|analise*.md|análise*.md|investigation*.md|findings.md|\
  design.md|*-design.md|research.md|*-research.md|requirements.md|proposal*.md|\
  notes.md|*-notes.md|todo.md|tasks.md|task-*.md|context.md|*-context.md|context-pack*.md|\
  summary.md|*-summary.md|report.md|*-report.md|progress.md|status.md|handoff*.md|scratch*.md|\
  checklist*.md|roadmap.md|prd*.md|rfc*.md|adr-*.md|review*.md|test-plan*.md)
    SPEC_NAME=1 ;;
esac

[ "$SPEC_NAME" = "0" ] && [ "$IN_SPEC_DIR" = "0" ] && exit 0

case "$FILE" in
  */docs/*)
    if [ "$IN_SPEC_DIR" = "0" ]; then exit 0; fi
    CWD_RAW="$(json_field cwd)"
    CWD="${CLAUDE_PROJECT_DIR:-${CWD_RAW:-$PWD}}"
    if bash "$HX/hooks/org-only.sh" --check "$CWD" 2>/dev/null; then exit 0; fi
    ;;
esac

cat >&2 <<EOF
HX anti-.md: criação bloqueada de '$FILE_RAW' (spec/plano/análise intermediário).
Mantenha plano/análise na conversa ou task list. PRD/RFC/ADR → Notion.
Doc de produto pedido explicitamente → docs/ (docs/specs/ só em modo org). Bypass: HX_ALLOW_MD=1.
EOF
exit 2
