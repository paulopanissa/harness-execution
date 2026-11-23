#!/usr/bin/env bash
# gate.sh — validação determinística do diff (zero IA). Requer bash >= 4.
# Roda só typecheck/lint/testes relacionados aos arquivos alterados.
# Uso: gate.sh [--base <ref>]   (ou env HX_GATE_BASE=origin/main)
# Saída: "GATE: PASS" (exit 0) | "GATE: FAIL — <etapa>" + ≤ 25 linhas + caminho do log completo (exit 1)
set -uo pipefail

MAX_LINES=25
FULL_LOG="${HX_GATE_LOG:-${HX_HOME:-$HOME/.hx}/state/gate-last-fail.log}"
BASE="${HX_GATE_BASE:-}"
while [ $# -gt 0 ]; do
  case "$1" in
    --base) BASE="${2:-}"; shift 2 ;;
    -h|--help) sed -n '2,5p' "$0"; exit 0 ;;
    *) echo "gate.sh: argumento desconhecido: $1" >&2; exit 2 ;;
  esac
done

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "GATE: FAIL — fora de repositório git"; exit 1; }
cd "$ROOT" || exit 1

LOG="$(mktemp "${TMPDIR:-/tmp}/hx-gate.XXXXXX")"
trap 'rm -f "$LOG"' EXIT
FAILED_STEP=""
RAN=0

# ---------- helpers ----------
changed_files() {
  {
    [ -n "$BASE" ] && git diff --name-only --diff-filter=ACMR "$BASE...HEAD" 2>/dev/null
    git diff --name-only --diff-filter=ACMR HEAD 2>/dev/null || git diff --name-only --diff-filter=ACMR --cached
    git ls-files --others --exclude-standard
  } | sort -u | while IFS= read -r f; do [ -f "$f" ] && printf '%s\n' "$f"; done
}

run_step() { # run_step <rótulo> <dir> <cmd...>
  local label="$1" dir="$2"; shift 2
  RAN=1
  printf '\n### %s (%s): %s\n' "$label" "$dir" "$*" >>"$LOG"
  if ! (cd "$dir" && "$@") >>"$LOG" 2>&1; then
    FAILED_STEP="$label @ $dir"
    return 1
  fi
}

fail() {
  local clean filtered
  clean="$(sed -e 's/\x1b\[[0-9;]*[A-Za-z]//g' "$LOG")"
  filtered="$(printf '%s\n' "$clean" |
    grep -E -i 'error|fail|✖|×|✗|expected|received|assert|traceback|exception|cannot find|not found|[^ ]+:[0-9]+:[0-9]+' |
    grep -v -E '^[[:space:]]*$' | tail -n "$MAX_LINES")"
  [ -z "$filtered" ] && filtered="$(printf '%s\n' "$clean" | tail -n "$MAX_LINES")"
  echo "GATE: FAIL — $FAILED_STEP"
  printf '%s\n' "$filtered"
  # Saída filtrada é parcial: guarda o log completo para leitura com range, sem rerodar o gate.
  if mkdir -p "${FULL_LOG%/*}" 2>/dev/null && printf '%s\n' "$clean" >"$FULL_LOG" 2>/dev/null; then
    echo "log completo: $FULL_LOG"
  fi
  exit 1
}

has_cmd() { command -v "$1" >/dev/null 2>&1; }

# ---------- coleta ----------
mapfile -t FILES < <(changed_files)
if [ "${#FILES[@]}" -eq 0 ]; then echo "GATE: PASS (sem alterações)"; exit 0; fi

JS_FILES=(); PY_FILES=(); RS_CHANGED=0; CS_CHANGED=0
for f in "${FILES[@]}"; do
  case "$f" in
    */node_modules/*|*/dist/*|*/build/*|*/.next/*) ;;
    *.ts|*.tsx|*.js|*.jsx|*.mjs|*.cjs|*.mts|*.cts|*.vue|*.svelte) JS_FILES+=("$f") ;;
    *.py) PY_FILES+=("$f") ;;
    *.rs) RS_CHANGED=1 ;;
    *.cs) CS_CHANGED=1 ;;
  esac
done

# ---------- JS/TS ----------
nearest_pkg_dir() {
  local d; d="$(dirname "$1")"
  while :; do
    [ -f "$d/package.json" ] && { printf '%s' "$d"; return 0; }
    [ "$d" = "." ] && return 1
    d="$(dirname "$d")"
  done
}

detect_pm() { # sobe de $1 até a raiz procurando lockfile
  local d="$1"
  while :; do
    [ -f "$d/pnpm-lock.yaml" ] && { echo pnpm; return; }
    [ -f "$d/yarn.lock" ] && { echo yarn; return; }
    { [ -f "$d/bun.lockb" ] || [ -f "$d/bun.lock" ]; } && { echo bun; return; }
    [ -f "$d/package-lock.json" ] && { echo npm; return; }
    [ "$d" = "." ] && break
    d="$(dirname "$d")"
  done
  echo npm
}

pkg_has() { # pkg_has <dir> scripts|deps <nome>
  (cd "$1" && node -e '
    const p=require("./package.json"),[k,n]=process.argv.slice(1);
    const src=k==="scripts"?p.scripts:{...p.dependencies,...p.devDependencies};
    process.exit(src&&src[n]?0:1)' "$2" "$3") 2>/dev/null
}

pm_exec() { # pm_exec <pm> <bin> [args]
  local pm="$1"; shift
  case "$pm" in
    pnpm) pnpm exec "$@" ;;
    yarn) yarn "$@" ;;
    bun) bunx "$@" ;;
    *) npx --no-install "$@" ;;
  esac
}

check_js_pkg() { # check_js_pkg <dir> <arquivos relativos...>
  local dir="$1"; shift
  local files=("$@") pm ts_changed=0 f
  pm="$(detect_pm "$dir")"
  for f in "${files[@]}"; do case "$f" in *.ts|*.tsx|*.mts|*.cts|*.vue) ts_changed=1 ;; esac; done

  if pkg_has "$dir" scripts typecheck; then
    run_step "typecheck" "$dir" "$pm" run typecheck || return 1
  elif [ "$ts_changed" = 1 ] && [ -f "$dir/tsconfig.json" ] && pkg_has "$dir" deps typescript; then
    run_step "tsc" "$dir" pm_exec "$pm" tsc --noEmit --incremental \
      --tsBuildInfoFile node_modules/.cache/hx-gate.tsbuildinfo -p tsconfig.json || return 1
  fi

  if pkg_has "$dir" deps eslint; then
    run_step "eslint" "$dir" pm_exec "$pm" eslint "${files[@]}" || return 1
  elif pkg_has "$dir" deps @biomejs/biome; then
    run_step "biome" "$dir" pm_exec "$pm" biome check "${files[@]}" || return 1
  fi

  if pkg_has "$dir" deps vitest; then
    run_step "vitest related" "$dir" pm_exec "$pm" vitest related --run --passWithNoTests "${files[@]}" || return 1
  elif pkg_has "$dir" deps jest; then
    run_step "jest related" "$dir" pm_exec "$pm" jest --bail --findRelatedTests --passWithNoTests "${files[@]}" || return 1
  elif pkg_has "$dir" scripts build; then
    run_step "build (sem test runner)" "$dir" "$pm" run build || return 1
  fi
}

if [ "${#JS_FILES[@]}" -gt 0 ]; then
  has_cmd node || { FAILED_STEP="node não encontrado no PATH"; fail; }
  declare -A PKG_FILES=()
  for f in "${JS_FILES[@]}"; do
    pkg="$(nearest_pkg_dir "$f")" || continue
    rel="$f"; [ "$pkg" != "." ] && rel="${f#"$pkg"/}"
    PKG_FILES["$pkg"]+="$rel"$'\n'
  done
  for pkg in "${!PKG_FILES[@]}"; do
    mapfile -t rels < <(printf '%s' "${PKG_FILES[$pkg]}" | sed '/^$/d')
    check_js_pkg "$pkg" "${rels[@]}" || fail
  done
fi

# ---------- Python ----------
find_python() {
  if [ -f uv.lock ] && has_cmd uv; then echo "uv run python"; return; fi
  if [ -f poetry.lock ] && has_cmd poetry; then echo "poetry run python"; return; fi
  local c
  for c in python3 python "py -3"; do
    $c -c 'import sys' >/dev/null 2>&1 && { echo "$c"; return; }
  done
  return 1
}

related_py_tests() {
  local f base stem t
  for f in "${PY_FILES[@]}"; do
    base="${f##*/}"; stem="${base%.py}"
    case "$base" in
      test_*.py|*_test.py) printf '%s\n' "$f" ;;
      *) git ls-files -- "*test_${stem}.py" "*${stem}_test.py" 2>/dev/null ;;
    esac
  done | sort -u | while IFS= read -r t; do [ -f "$t" ] && printf '%s\n' "$t"; done
}

if [ "${#PY_FILES[@]}" -gt 0 ]; then
  PY="$(find_python)" || { FAILED_STEP="python não encontrado"; fail; }
  # shellcheck disable=SC2086
  if $PY -m ruff --version >/dev/null 2>&1; then
    run_step "ruff" "." $PY -m ruff check "${PY_FILES[@]}" || fail
  elif has_cmd ruff; then
    run_step "ruff" "." ruff check "${PY_FILES[@]}" || fail
  fi
  if { [ -f mypy.ini ] || grep -qs '^\[tool\.mypy\]' pyproject.toml; } && $PY -m mypy --version >/dev/null 2>&1; then
    run_step "mypy" "." $PY -m mypy "${PY_FILES[@]}" || fail
  fi
  mapfile -t PY_TESTS < <(related_py_tests)
  if [ "${#PY_TESTS[@]}" -gt 0 ] && $PY -m pytest --version >/dev/null 2>&1; then
    printf '\n### pytest: %s\n' "${PY_TESTS[*]}" >>"$LOG"
    RAN=1
    $PY -m pytest -q -x "${PY_TESTS[@]}" >>"$LOG" 2>&1
    rc=$?
    if [ "$rc" -ne 0 ] && [ "$rc" -ne 5 ]; then FAILED_STEP="pytest"; fail; fi
  fi
fi

# ---------- Rust / .NET (gamedev comum) ----------
if [ "$RS_CHANGED" = 1 ] && [ -f Cargo.toml ] && has_cmd cargo; then
  run_step "cargo check" "." cargo check --quiet --all-targets || fail
fi
if [ "$CS_CHANGED" = 1 ] && [ ! -d ProjectSettings ] && has_cmd dotnet && ls ./*.sln ./*.csproj >/dev/null 2>&1; then
  run_step "dotnet build" "." dotnet build -nologo -v q || fail
fi

if [ "$RAN" = 0 ]; then
  echo "GATE: PASS (nenhum checker aplicável)"
else
  echo "GATE: PASS"
fi
exit 0
