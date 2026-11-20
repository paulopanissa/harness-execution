#!/usr/bin/env bash
# read-guard.sh — PreToolUse hook (Read).
# Blocks reading a large text file whole: > HX_READ_MAX_LINES (default 400) lines
# with no offset/limit. Forces surgical reads (AGENTS.md §2).
# One-off bypass: HX_ALLOW_READ=1. Exit 2 = block (stderr goes back to the agent).
set -u

[ "${HX_ALLOW_READ:-0}" = "1" ] && exit 0
MAX="${HX_READ_MAX_LINES:-400}"

INPUT="$(cat)"
FLAT="$(printf '%s' "$INPUT" | tr -d '\r\n')"

# A range was given → fine.
printf '%s' "$FLAT" | grep -Eq '"(offset|limit|pages)"[[:space:]]*:[[:space:]]*[0-9"]' && exit 0

FILE_RAW="$(printf '%s' "$FLAT" |
  sed -nE 's/.*"file_path"[[:space:]]*:[[:space:]]*"(([^"\\]|\\.)*)".*/\1/p' | head -n1)"
[ -z "$FILE_RAW" ] && exit 0

FILE="$(printf '%s' "$FILE_RAW" | sed -e 's#\\\\#/#g' -e 's#\\/#/#g')"
if command -v cygpath >/dev/null 2>&1; then
  FILE="$(cygpath -u "$FILE" 2>/dev/null || printf '%s' "$FILE")"
fi
[ -f "$FILE" ] || exit 0

# Binary/visual formats are read differently by the tool → ignore.
case "$(printf '%s' "$FILE" | tr '[:upper:]' '[:lower:]')" in
  *.png|*.jpg|*.jpeg|*.gif|*.webp|*.bmp|*.ico|*.pdf|*.ipynb) exit 0 ;;
esac

LINES="$(wc -l < "$FILE" 2>/dev/null | tr -d '[:space:]')"
case "$LINES" in ''|*[!0-9]*) exit 0 ;; esac
[ "$LINES" -le "$MAX" ] && exit 0

cat >&2 <<EOF
HX read-guard: '$FILE' has $LINES lines (> $MAX) and no offset/limit.
Locate the section first (Graphify, or rg -n scoped to the file), then Read with offset/limit.
Whole file truly needed: set HX_ALLOW_READ=1 or raise HX_READ_MAX_LINES.
EOF
exit 2
