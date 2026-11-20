#!/usr/bin/env bash
# graphify-setup.sh — hook SessionStart: prepara o Graphify no repo git da sessão, sem config por projeto.
#   não-git → nada | sem `graphify` no PATH → avisa 1x por repo (marcador em $HX_HOME/state/)
#   com graphify → `graphify-out/` no .gitignore; em background: `graphify hook install` (se ausente)
#   e `graphify extract <repo> --code-only` (só AST local, sem LLM) se não houver graphify-out/.
# Nunca falha a sessão: erro → log em $HX_HOME/.graphify.log + exit 0.
# Bypass: HX_NO_GRAPHIFY=1. HX_GRAPHIFY_SYNC=1 roda a parte de background em primeiro plano (testes).
set -u

[ "${HX_NO_GRAPHIFY:-0}" = "1" ] && exit 0
[ -n "${HX_HOME:-}${HOME:-}" ] || exit 0
HX="${HX_HOME:-$HOME/.hx}"
LOG="$HX/.graphify.log"
STATE="$HX/state"
LOCK_MAX_AGE_MIN=60
LOG_MAX_BYTES=1048576
LOCK_DIR=""

# Log com teto: acima de LOG_MAX_BYTES mantém só as últimas linhas.
if [ -f "$LOG" ] && [ "$(wc -c <"$LOG" 2>/dev/null || echo 0)" -gt "$LOG_MAX_BYTES" ]; then
  { tail -n 500 "$LOG" >"$LOG.tmp" && mv -f "$LOG.tmp" "$LOG"; } 2>/dev/null || rm -f "$LOG.tmp" 2>/dev/null
fi

log() { printf '%s [%s] %s\n' "$(date '+%Y-%m-%dT%H:%M:%S')" "${TOP:-?}" "$*" >>"$LOG" 2>/dev/null || true; }

project_dir() {
  local input cwd=""
  if [ ! -t 0 ]; then
    input="$(cat 2>/dev/null || true)"
    cwd="$(printf '%s' "$input" | tr -d '\r\n' |
      sed -nE 's/.*"cwd"[[:space:]]*:[[:space:]]*"(([^"\\]|\\.)*)".*/\1/p' | head -n1 |
      sed -e 's#\\\\#/#g' -e 's#\\/#/#g')"
  fi
  printf '%s' "${CLAUDE_PROJECT_DIR:-${cwd:-$PWD}}"
}

repo_key() { printf '%s' "$1" | cksum | cut -d' ' -f1; }

# .gitignore: adiciona `graphify-out/` se faltar; preserva CRLF/LF; cria o arquivo se não existir.
ensure_gitignore() {
  local file="$1/.gitignore" eol=$'\n'
  if [ -f "$file" ]; then
    grep -qE '^/?graphify-out/?[[:space:]]*$' "$file" && return 0
    [ -n "$(tr -cd '\r' <"$file" | head -c1)" ] && eol=$'\r\n'
    if [ -s "$file" ] && [ -n "$(tail -c1 "$file")" ]; then printf '%s' "$eol" >>"$file" || return 1; fi
  fi
  printf 'graphify-out/%s' "$eol" >>"$file"
}

abs_path() { case "$2" in /*|[A-Za-z]:*) printf '%s' "$2" ;; *) printf '%s/%s' "$1" "$2" ;; esac; }

# Checagem rápida (sem subprocess Python): o post-commit tem o bloco que `graphify hook install` grava?
hook_present_fast() {
  local hook
  hook="$(git -C "$1" rev-parse --git-path hooks/post-commit 2>/dev/null)" || return 1
  hook="$(abs_path "$1" "$hook")"
  [ -f "$hook" ] && grep -q 'graphify-hook-start' "$hook"
}

# core.hooksPath dentro do worktree (ex.: .husky/ versionado) → não mexer em hooks do projeto.
hooks_path_in_worktree() {
  local hp
  hp="$(git -C "$1" config --get core.hooksPath 2>/dev/null)" || return 1
  [ -n "$hp" ] || return 1
  case "$(abs_path "$1" "$hp")" in "$1"/*) return 0 ;; esac
  return 1
}

graph_ready() { [ -f "$1/graphify-out/graph.json" ]; }

release_lock() { [ -n "$LOCK_DIR" ] && rm -rf "$LOCK_DIR"; }

background_setup() {
  local top="$1"
  LOCK_DIR="$STATE/graphify-$(repo_key "$1").lock"
  find "$LOCK_DIR" -maxdepth 0 -mmin +"$LOCK_MAX_AGE_MIN" -exec rm -rf {} + 2>/dev/null
  if ! mkdir "$LOCK_DIR" 2>/dev/null; then LOCK_DIR=""; log "setup já em andamento; pulando"; return 0; fi
  trap release_lock EXIT
  if hooks_path_in_worktree "$top"; then
    log "core.hooksPath versionado no repo; pulando graphify hook install"
  elif ! (cd "$top" && graphify hook status) 2>>"$LOG" | grep -q 'post-commit: installed'; then
    log "graphify hook install"
    (cd "$top" && graphify hook install) >>"$LOG" 2>&1 || log "ERRO: graphify hook install falhou"
  fi
  if ! graph_ready "$top"; then
    log "graphify extract --code-only"
    graphify extract "$top" --code-only >>"$LOG" 2>&1 || log "ERRO: graphify extract falhou"
  fi
}

main() {
  local dir
  dir="$(project_dir)"
  TOP="$(git -C "$dir" rev-parse --show-toplevel 2>/dev/null)" || return 0
  [ -n "$TOP" ] || return 0
  mkdir -p "$STATE" 2>/dev/null || true

  if ! command -v graphify >/dev/null 2>&1; then
    local mark="$STATE/graphify-missing-$(repo_key "$TOP")"
    [ -e "$mark" ] && return 0
    : >"$mark" 2>/dev/null || log "ERRO: não gravou marcador $mark"
    echo "Graphify não instalado; /hx usa fallback rg. Instale: uv tool install graphifyy"
    return 0
  fi

  ensure_gitignore "$TOP" || log "ERRO: não atualizou $TOP/.gitignore"
  if graph_ready "$TOP" && { hook_present_fast "$TOP" || hooks_path_in_worktree "$TOP"; }; then return 0; fi

  if [ "${HX_GRAPHIFY_SYNC:-0}" = "1" ]; then
    background_setup "$TOP"
  else
    (cd "$TOP" && background_setup "$TOP") </dev/null >>"$LOG" 2>&1 &
    disown 2>/dev/null || true
  fi
}

main || log "ERRO: graphify-setup saiu com status $?"
exit 0
