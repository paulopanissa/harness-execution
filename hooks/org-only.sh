#!/usr/bin/env bash
# org-only.sh — detecta se o repo atual está no modo org (módulo corporativo privado).
#   org-only.sh --check [dir]     exit 0 se ativo, 1 se não
#   org-only.sh --get <chave>     imprime valor do preset (~/.hx/vendor/org-preset/hx-org.yaml)
#   org-only.sh <cmd> [args...]   executa <cmd> (stdin repassado) só se ativo; senão exit 0
# Ativo = org_enabled: true no config E (remote casa remote_pattern OU CLAUDE.md local cita claude_md_marker).
set -u

HX="${HX_HOME:-$HOME/.hx}"
PRESET="$HX/vendor/org-preset/hx-org.yaml"

preset_get() {
  [ -f "$PRESET" ] || return 1
  sed -nE "s/^$1:[[:space:]]*\"?([^\"]*)\"?[[:space:]]*$/\\1/p" "$PRESET" | head -n1
}

org_active() {
  local dir="${1:-$PWD}" pattern marker root
  grep -Eq '^org_enabled:[[:space:]]*(true|yes|on)[[:space:]]*(#.*)?$' "$HX/config.yaml" 2>/dev/null || return 1
  pattern="$(preset_get remote_pattern)"
  marker="$(preset_get claude_md_marker)"
  if [ -n "$pattern" ] && git -C "$dir" remote -v 2>/dev/null | grep -Eqi "$pattern"; then
    return 0
  fi
  [ -n "$marker" ] || return 1
  root="$(git -C "$dir" rev-parse --show-toplevel 2>/dev/null || printf '%s' "$dir")"
  grep -qsF "$marker" "$root/CLAUDE.md"
}

case "${1:-}" in
  --check) org_active "${2:-$PWD}" ;;
  --get)
    [ -n "${2:-}" ] || { echo "uso: org-only.sh --get <chave>" >&2; exit 2; }
    preset_get "$2"
    ;;
  "")
    echo "uso: org-only.sh --check [dir] | --get <chave> | <cmd> [args...]" >&2
    exit 2
    ;;
  *)
    if org_active "${CLAUDE_PROJECT_DIR:-$PWD}"; then
      exec "$@"
    fi
    exit 0
    ;;
esac
