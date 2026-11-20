#!/usr/bin/env python3
"""measure.py — HX token footprint and real session usage (stdlib only).

  measure.py baseline [--lang en|pt-BR|all]
      Static estimate of what HX adds to context (≈ chars/4).
  measure.py sessions [--days N] [--project TEXT] [--tool claude|codex|all] [--json]
      Real usage summed from local transcripts:
      Claude ~/.claude/projects/**/*.jsonl, Codex ~/.codex/sessions/**/*.jsonl.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hxlib import CLAUDE_HOME, CODEX_HOME, HX_HOME, LANGUAGES, language, load_config, parse_frontmatter  # noqa: E402

CHARS_PER_TOKEN = 4


def estimate(text: str) -> int:
    return (len(text) + CHARS_PER_TOKEN - 1) // CHARS_PER_TOKEN


# ---------------------------------------------------------------- baseline
def _source(rel: str, lang: str) -> Path:
    if lang != "en":
        candidate = HX_HOME / "i18n" / lang / rel
        if candidate.is_file():
            return candidate
    return HX_HOME / rel


def _rel_files(folder: str, pattern: str = "*.md") -> list[str]:
    root = HX_HOME / folder
    return sorted(p.relative_to(HX_HOME).as_posix() for p in root.rglob(pattern))


def baseline_rows(lang: str) -> list[tuple[str, str, int]]:
    """(group, item, tokens). 'always' = loaded every turn; the rest only on demand."""
    rows: list[tuple[str, str, int]] = []
    rows.append(("always", "AGENTS.md", estimate(_source("AGENTS.md", lang).read_text(encoding="utf-8"))))
    for group in ("agents", "commands"):
        for rel in _rel_files(group):
            meta, body = parse_frontmatter(_source(rel, lang).read_text(encoding="utf-8"))
            name = Path(rel).stem
            rows.append(("always", f"{group}/{name} (description)", estimate(meta.get("description", ""))))
            rows.append((f"on-demand {group}", name, estimate(body)))
    for rel in _rel_files("skills"):
        text = _source(rel, lang).read_text(encoding="utf-8")
        rows.append(("on-demand skills", rel.removeprefix("skills/").removesuffix(".md"), estimate(text)))
    return rows


def cmd_baseline(args: argparse.Namespace) -> int:
    langs = list(LANGUAGES) if args.lang == "all" else [args.lang or language(load_config())]
    for lang in langs:
        rows = baseline_rows(lang)
        always = sum(t for g, _, t in rows if g == "always")
        print(f"\n== language: {lang} (≈ {CHARS_PER_TOKEN} chars/token)")
        print(f"always loaded per session : ~{always:,} tokens")
        by_group: dict[str, list[tuple[str, int]]] = defaultdict(list)
        for group, item, tokens in rows:
            if group != "always":
                by_group[group].append((item, tokens))
        for group, items in by_group.items():
            print(f"{group:<26}: ~{sum(t for _, t in items):,} tokens total, loaded one at a time")
            for item, tokens in sorted(items, key=lambda x: -x[1]):
                print(f"    {item:<38} ~{tokens:,}")
    return 0


# ---------------------------------------------------------------- sessions
@dataclass
class Usage:
    sessions: set[str] = field(default_factory=set)
    turns: int = 0
    input: int = 0
    cache_write: int = 0
    cache_read: int = 0
    output: int = 0

    def add(self, session: str, inp: int, cw: int, cr: int, out: int, turns: int = 1) -> None:
        self.sessions.add(session)
        self.turns += turns
        self.input += inp
        self.cache_write += cw
        self.cache_read += cr
        self.output += out

    def merge(self, other: "Usage", prefix: str) -> None:
        self.sessions |= {f"{prefix}:{s}" for s in other.sessions}
        self.turns += other.turns
        self.input += other.input
        self.cache_write += other.cache_write
        self.cache_read += other.cache_read
        self.output += other.output

    @property
    def prompt_total(self) -> int:
        return self.input + self.cache_write + self.cache_read

    def as_dict(self) -> dict[str, Any]:
        hit = self.cache_read / self.prompt_total if self.prompt_total else 0.0
        return {
            "sessions": len(self.sessions), "turns": self.turns, "input": self.input,
            "cache_write": self.cache_write, "cache_read": self.cache_read,
            "output": self.output, "cache_hit": round(hit, 3),
        }


def _parse_ts(raw: Any) -> datetime | None:
    if not isinstance(raw, str):
        return None
    try:
        ts = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    return ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)


def _jsonl(path: Path) -> Iterator[dict[str, Any]]:
    try:
        with path.open(encoding="utf-8", errors="replace") as handle:
            for line in handle:
                try:
                    item = json.loads(line)
                except ValueError:
                    continue
                if isinstance(item, dict):
                    yield item
    except OSError as err:
        print(f"measure: skipped {path} ({err})", file=sys.stderr)


def _recent(root: Path, since: datetime) -> Iterator[Path]:
    """Transcripts touched since `since` (older files cannot hold newer records)."""
    floor = since.timestamp()
    for path in root.rglob("*.jsonl"):
        try:
            if path.stat().st_mtime >= floor:
                yield path
        except OSError:
            continue


def claude_usage(since: datetime, project: str) -> dict[str, Usage]:
    """Last record per message id wins (streaming writes the same id several times)."""
    root = CLAUDE_HOME / "projects"
    if not root.is_dir():
        return {}
    latest: dict[str, tuple[str, str, dict[str, Any]]] = {}
    for path in _recent(root, since):
        proj = path.relative_to(root).parts[0]
        if project and project.lower() not in proj.lower():
            continue
        for item in _jsonl(path):
            msg = item.get("message")
            if item.get("type") != "assistant" or not isinstance(msg, dict) or not isinstance(msg.get("usage"), dict):
                continue
            ts = _parse_ts(item.get("timestamp"))
            if ts is None or ts < since:
                continue
            key = str(msg.get("id") or f"{path}:{item.get('uuid')}")
            latest[key] = (proj, str(item.get("sessionId") or path.stem), msg["usage"])
    result: dict[str, Usage] = defaultdict(Usage)
    for proj, session, u in latest.values():
        result[proj].add(
            session,
            int(u.get("input_tokens") or 0),
            int(u.get("cache_creation_input_tokens") or 0),
            int(u.get("cache_read_input_tokens") or 0),
            int(u.get("output_tokens") or 0),
        )
    return dict(result)


def codex_usage(since: datetime, project: str) -> dict[str, Usage]:
    """Per rollout file, the last cumulative `token_count` total."""
    root = CODEX_HOME / "sessions"
    if not root.is_dir():
        return {}
    result: dict[str, Usage] = defaultdict(Usage)
    for path in _recent(root, since):
        cwd, session, last, turns, last_ts = "?", path.stem, None, 0, None
        for item in _jsonl(path):
            payload = item.get("payload") if isinstance(item.get("payload"), dict) else {}
            if item.get("type") == "session_meta" and cwd == "?":
                cwd = str(payload.get("cwd") or "?")
                session = str(payload.get("id") or session)
            if item.get("type") == "event_msg" and payload.get("type") == "token_count":
                info = payload.get("info") or {}
                if isinstance(info.get("total_token_usage"), dict):
                    last, turns = info["total_token_usage"], turns + 1
                    last_ts = _parse_ts(item.get("timestamp")) or last_ts
        if last is None or last_ts is None or last_ts < since:
            continue
        proj = Path(cwd.replace("\\", "/")).name or cwd
        if project and project.lower() not in cwd.lower():
            continue
        cached = int(last.get("cached_input_tokens") or 0)
        result[proj].add(
            session,
            max(int(last.get("input_tokens") or 0) - cached, 0),
            int(last.get("cache_write_input_tokens") or 0),
            cached,
            int(last.get("output_tokens") or 0),
            turns,
        )
    return dict(result)


def _fmt(n: int) -> str:
    for unit, size in (("M", 1_000_000), ("k", 1_000)):
        if n >= size:
            return f"{n / size:.1f}{unit}"
    return str(n)


def print_table(title: str, data: dict[str, Usage], top: int) -> None:
    print(f"\n== {title}")
    if not data:
        print("   (no data)")
        return
    head = f"{'project':<34}{'sess':>5}{'turns':>7}{'input':>9}{'c.write':>9}{'c.read':>9}{'output':>9}{'hit':>6}"
    print(head)
    total = Usage()
    ranked = sorted(data.items(), key=lambda kv: -kv[1].prompt_total)
    if len(ranked) > top:
        rest = Usage()
        for proj, u in ranked[top:]:
            rest.merge(u, prefix=proj)
        ranked = ranked[:top] + [(f"({len(data) - top} more)", rest)]
    for proj, u in ranked:
        d = u.as_dict()
        print(f"{proj[-33:]:<34}{d['sessions']:>5}{d['turns']:>7}{_fmt(u.input):>9}{_fmt(u.cache_write):>9}"
              f"{_fmt(u.cache_read):>9}{_fmt(u.output):>9}{d['cache_hit']:>6.0%}")
        total.merge(u, prefix=proj)
    d = total.as_dict()
    print(f"{'TOTAL':<34}{len(total.sessions):>5}{total.turns:>7}{_fmt(total.input):>9}{_fmt(total.cache_write):>9}"
          f"{_fmt(total.cache_read):>9}{_fmt(total.output):>9}{d['cache_hit']:>6.0%}")


def cmd_sessions(args: argparse.Namespace) -> int:
    since = datetime.now(timezone.utc) - timedelta(days=args.days)
    report: dict[str, dict[str, Usage]] = {}
    if args.tool in ("claude", "all"):
        report["claude"] = claude_usage(since, args.project)
    if args.tool in ("codex", "all"):
        report["codex"] = codex_usage(since, args.project)
    if args.json:
        print(json.dumps({tool: {p: u.as_dict() for p, u in data.items()} for tool, data in report.items()}, indent=2))
        return 0
    print(f"Usage since {since:%Y-%m-%d %H:%M} UTC ({args.days} day(s)). input = uncached prompt tokens.")
    for tool, data in report.items():
        print_table(tool, data, args.top)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("baseline", help="static HX footprint estimate")
    b.add_argument("--lang", choices=[*LANGUAGES, "all"], help="default: config language")
    s = sub.add_parser("sessions", help="real usage from local transcripts")
    s.add_argument("--days", type=int, default=7)
    s.add_argument("--project", default="", help="substring filter on project/cwd")
    s.add_argument("--tool", choices=("claude", "codex", "all"), default="all")
    s.add_argument("--top", type=int, default=12, help="rows per tool before grouping the rest")
    s.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if getattr(args, "days", 1) < 1:
        parser.error("--days must be >= 1")
    return cmd_baseline(args) if args.cmd == "baseline" else cmd_sessions(args)


if __name__ == "__main__":
    sys.exit(main())
