"""hxlib — utilitários compartilhados do harness HX (stdlib only)."""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Any

# Pipes no Windows (Git Bash, hooks) herdam cp1252 → acentos quebram. Console real usa UTF-16.
for _stream in (sys.stdout, sys.stderr):
    if not _stream.isatty() and hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

HOME = Path.home()
HX_HOME = Path(os.environ.get("HX_HOME", HOME / ".hx")).expanduser()
CLAUDE_HOME = Path(os.environ.get("HX_CLAUDE_HOME", HOME / ".claude")).expanduser()
CODEX_HOME = Path(os.environ.get("CODEX_HOME", HOME / ".codex")).expanduser()
# Skills de usuário do Codex CLI (`$nome` no prompt).
CODEX_SKILLS_HOME = Path(os.environ.get("HX_CODEX_SKILLS_HOME", HOME / ".agents" / "skills")).expanduser()

CONFIG_PATH = HX_HOME / "config.yaml"
LAST_SYNC_PATH = HX_HOME / ".last_sync"
MANIFEST_PATH = HX_HOME / ".manifest.json"
FALLBACK_MEMORY = HX_HOME / "fallback-memory.jsonl"
ORG_PRESET_DIR = HX_HOME / "vendor" / "org-preset"
ORG_PRESET_FILE = ORG_PRESET_DIR / "hx-org.yaml"
ORG_VENDOR_DIR = HX_HOME / "vendor" / "org"
MODS_DIR = HX_HOME / "mods"
I18N_DIR = HX_HOME / "i18n"
LANGUAGES = ("en", "pt-BR")

TIERS = ("fast", "default", "deep")
DEFAULT_CONFIG: dict[str, Any] = {
    "language": "en",
    "org_enabled": False,
    "org_preset": "",
    "auto_update_days": 7,
    "mods": "",
    # Integração opcional com RTK (filtro de saída de Bash): sync.py registra `rtk hook` se o binário existir.
    "rtk": False,
    "models": {
        "claude_fast": "haiku",
        "claude_default": "sonnet",
        "claude_deep": "opus",
        "codex_fast": "",
        "codex_default": "",
        "codex_deep": "",
    },
    "fallbacks": {
        "claude_fast": "sonnet",
        "claude_default": "opus",
        "claude_deep": "sonnet",
        "codex_fast": "",
        "codex_default": "",
        "codex_deep": "",
    },
}

_KEY_RE = re.compile(r"^(\s*)([A-Za-z0-9_.-]+)\s*:(.*)$")


def _scalar(raw: str) -> Any:
    value = raw.strip()
    if not value:
        return ""
    if value[0] in "\"'":
        end = value.find(value[0], 1)
        return value[1:end] if end > 0 else value[1:]
    value = re.split(r"\s+#", value, maxsplit=1)[0].strip()
    lowered = value.lower()
    if lowered in ("true", "yes", "on"):
        return True
    if lowered in ("false", "no", "off"):
        return False
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def parse_yaml(text: str) -> dict[str, Any]:
    """Parser YAML mínimo: escalares no topo + um nível de mapa aninhado."""
    root: dict[str, Any] = {}
    current: dict[str, Any] | None = None
    for lineno, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = _KEY_RE.match(line)
        if not match:
            raise ValueError(f"config.yaml:{lineno}: linha inválida: {line!r}")
        indent, key, rest = len(match.group(1)), match.group(2), match.group(3)
        if indent == 0:
            if rest.strip() == "" or rest.strip().startswith("#"):
                current = {}
                root[key] = current
            else:
                root[key] = _scalar(rest)
                current = None
        else:
            if current is None:
                raise ValueError(f"config.yaml:{lineno}: chave aninhada sem pai")
            current[key] = _scalar(rest)
    return root


def _fmt(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    text = str(value)
    if text == "" or re.search(r"[:#\"']|^\s|\s$", text):
        return '"' + text.replace('"', '\\"') + '"'
    return text


def dump_yaml(cfg: dict[str, Any]) -> str:
    lines = ["# Gerado/atualizado por ~/.hx/scripts/install.py — edite e rode sync.py"]
    for key, value in cfg.items():
        if isinstance(value, dict):
            lines.append(f"{key}:")
            lines.extend(f"  {k}: {_fmt(v)}" for k, v in value.items())
        else:
            lines.append(f"{key}: {_fmt(value)}")
    return "\n".join(lines) + "\n"


def merge_config(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for key in {**base, **override}:
        b, o = base.get(key), override.get(key)
        if isinstance(b, dict) and isinstance(o, dict):
            merged[key] = {**b, **o}
        else:
            merged[key] = o if key in override else b
    return merged


def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        return merge_config(DEFAULT_CONFIG, {})
    raw = parse_yaml(CONFIG_PATH.read_text(encoding="utf-8"))
    current = {k: v for k, v in raw.items() if k in DEFAULT_CONFIG}  # descarta chaves obsoletas
    return merge_config(DEFAULT_CONFIG, current)


def language(cfg: dict[str, Any]) -> str:
    """Idioma das regras (`language` no config.yaml). Inválido → en."""
    lang = str(cfg.get("language") or "en")
    return lang if lang in LANGUAGES else "en"


def localized(rel: str, cfg: dict[str, Any]) -> Path:
    """Arquivo de regra no idioma configurado; cai para o inglês (raiz) se não houver tradução."""
    lang = language(cfg)
    if lang != "en":
        candidate = I18N_DIR / lang / rel
        if candidate.is_file():
            return candidate
    return HX_HOME / rel


def load_org_preset() -> dict[str, Any]:
    """Preset privado do módulo org (clonado de `org_preset`). Vazio se ausente."""
    if not ORG_PRESET_FILE.is_file():
        return {}
    return parse_yaml(ORG_PRESET_FILE.read_text(encoding="utf-8"))


def mods_selected(cfg: dict[str, Any]) -> list[str]:
    return [m.strip() for m in str(cfg.get("mods") or "").split(",") if m.strip()]


def save_config(cfg: dict[str, Any]) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(dump_yaml(cfg), encoding="utf-8")


def resolve_model(cfg: dict[str, Any], tool: str, tier: str) -> str:
    """Modelo do tier; vazio → fallback; vazio → '' (herda do CLI)."""
    tier = tier if tier in TIERS else "default"
    key = f"{tool}_{tier}"
    return str(cfg.get("models", {}).get(key) or cfg.get("fallbacks", {}).get(key) or "")


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Frontmatter flat `key: value` (valores crus, aspas removidas)."""
    if not text.startswith("---"):
        return {}, text
    parts = re.split(r"^---[ \t]*\r?$", text, maxsplit=2, flags=re.MULTILINE)
    if len(parts) < 3:
        return {}, text
    meta: dict[str, str] = {}
    for line in parts[1].splitlines():
        match = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$", line)
        if match:
            value = match.group(2).strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            meta[match.group(1)] = value
    return meta, parts[2].lstrip("\r\n")
