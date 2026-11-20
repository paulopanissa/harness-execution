#!/usr/bin/env bash
# strip-legacy-oc.sh — remove a seção "## Configuração do Projeto" de um CLAUDE.md
# SOMENTE se ela contém chaves legadas (orchestrator, /oc, prAdvisor, qaE2E).
# Uso: strip-legacy-oc.sh [caminho/CLAUDE.md] [--dry-run]
# Exit: 0 removido (ou mostraria remoção no dry-run) | 3 nada a remover | 1 erro.
set -euo pipefail

TARGET=""
DRY=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY=1 ;;
    -h|--help) sed -n '2,5p' "$0"; exit 0 ;;
    *) TARGET="$arg" ;;
  esac
done

if [ -z "$TARGET" ]; then
  ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
  TARGET="$ROOT/CLAUDE.md"
fi
[ -f "$TARGET" ] || { echo "strip-legacy-oc: '$TARGET' não encontrado" >&2; exit 1; }

TMP="$(mktemp "${TMPDIR:-/tmp}/hx-strip.XXXXXX")"
trap 'rm -f "$TMP"' EXIT

rc=0
awk '
function flush() {
  if (insec) { if (legacy) removed = 1; else printf "%s", buf }
  buf = ""; insec = 0; legacy = 0
}
{
  line = $0
  if (line ~ /^[[:space:]]*(```|~~~)/) infence = !infence
  if (!infence && line ~ /^##?[[:space:]]/) {
    flush()
    if (line ~ /^##[[:space:]]+Configura(ç|c)(ã|a)o do Projeto/) insec = 1
  }
  if (insec) {
    buf = buf line "\n"
    if (line ~ /orchestrator|\/oc([^A-Za-z0-9_-]|$)|prAdvisor|qaE2E/) legacy = 1
    next
  }
  print line
}
END { flush(); exit(removed ? 0 : 3) }
' "$TARGET" >"$TMP" || rc=$?

if [ "$rc" -eq 3 ]; then
  echo "strip-legacy-oc: nenhuma seção legada em '$TARGET'"
  exit 3
elif [ "$rc" -ne 0 ]; then
  echo "strip-legacy-oc: falha ao processar '$TARGET' (awk rc=$rc)" >&2
  exit 1
fi

if [ "$DRY" -eq 1 ]; then
  diff -u "$TARGET" "$TMP" || true
  echo "strip-legacy-oc: dry-run — nada gravado"
  exit 0
fi

cp -p "$TARGET" "$TARGET.hx-bak"
cat "$TMP" >"$TARGET"
echo "strip-legacy-oc: seção removida de '$TARGET' (backup: $TARGET.hx-bak)"
