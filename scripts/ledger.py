#!/usr/bin/env python3
"""Ledger helper for Clean Streets skills.

Every skill under .claude/skills/<name>/ keeps an append-only run log at
.claude/skills/<name>/LEDGER.md. This script is the only supported way to
write to a ledger, so entries stay in a format that tests and other skills
can parse.

Subcommands
  init   --skill NAME                      create an empty ledger for a new skill
  add    --skill NAME --outcome O --actions N --summary "..." [--metric k=v ...]
         [--detail "..." ...] [--next "..."] [--started ISO]
  show   --skill NAME [--last N] [--json]  print recent entries
  seen   --skill NAME --key TOKEN          exit 0 if TOKEN appears in the ledger
  check  [--skill NAME]                    validate ledger format (exit 1 on problems)

No third-party dependencies. Run from anywhere inside the repository.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

OUTCOMES = ("success", "partial", "error", "aborted", "noop")
HEADER_RE = re.compile(
    r"^## (?P<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?(?:[+-]\d{2}:\d{2}|Z)) \| "
    r"run (?P<run>\d{4,}) \| (?P<outcome>[a-z]+)$"
)
METRIC_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=[^\s]+$")


def repo_root() -> Path:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        return Path(out)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return Path(__file__).resolve().parents[1]


def skills_dir() -> Path:
    return repo_root() / ".claude" / "skills"


def ledger_path(skill: str) -> Path:
    return skills_dir() / skill / "LEDGER.md"


def now_iso() -> str:
    try:
        from zoneinfo import ZoneInfo
        dt = datetime.now(ZoneInfo("America/Los_Angeles"))
    except Exception:  # tzdata missing: fall back to local offset
        dt = datetime.now().astimezone()
    return dt.isoformat(timespec="minutes")


def ledger_header(skill: str) -> str:
    return (
        f"# Ledger: {skill}\n\n"
        "Append-only run log for this skill. One entry per run, newest at the bottom.\n"
        "Written by `scripts/ledger.py add`; never hand-edit or delete past entries.\n"
        "Format and privacy rules: `.claude/skills/README.md`.\n"
    )


def parse(text: str) -> tuple[str, list[dict]]:
    """Return (preamble, entries). Raises ValueError on malformed content."""
    lines = text.splitlines()
    entries: list[dict] = []
    preamble: list[str] = []
    current: dict | None = None
    for lineno, line in enumerate(lines, 1):
        if line.startswith("## "):
            m = HEADER_RE.match(line)
            if not m:
                raise ValueError(f"line {lineno}: malformed entry header: {line!r}")
            if m["outcome"] not in OUTCOMES:
                raise ValueError(f"line {lineno}: unknown outcome {m['outcome']!r}")
            current = {
                "timestamp": m["ts"], "run": int(m["run"]), "outcome": m["outcome"],
                "actions": None, "summary": None, "metrics": {}, "details": [],
                "next": None, "line": lineno,
            }
            entries.append(current)
        elif current is None:
            preamble.append(line)
        else:
            s = line.rstrip()
            if s.startswith("- actions: "):
                try:
                    current["actions"] = int(s[len("- actions: "):])
                except ValueError:
                    raise ValueError(f"line {lineno}: actions must be an integer")
            elif s.startswith("- summary: "):
                current["summary"] = s[len("- summary: "):]
            elif s.startswith("- metrics: "):
                for tok in s[len("- metrics: "):].split():
                    if not METRIC_RE.match(tok):
                        raise ValueError(f"line {lineno}: bad metric token {tok!r}")
                    k, v = tok.split("=", 1)
                    current["metrics"][k] = v
            elif s.startswith("- next: "):
                current["next"] = s[len("- next: "):]
            elif s.startswith("  - "):
                current["details"].append(s[4:])
    for e in entries:
        if e["actions"] is None:
            raise ValueError(f"run {e['run']:04d}: missing '- actions:' line")
        if not e["summary"]:
            raise ValueError(f"run {e['run']:04d}: missing '- summary:' line")
    runs = [e["run"] for e in entries]
    if runs != sorted(runs) or len(set(runs)) != len(runs):
        raise ValueError("run numbers must be unique and strictly increasing")
    return "\n".join(preamble), entries


def load(skill: str) -> tuple[Path, str, list[dict]]:
    path = ledger_path(skill)
    if not path.exists():
        sys.exit(f"no ledger at {path} (run: scripts/ledger.py init --skill {skill})")
    text = path.read_text(encoding="utf-8")
    try:
        preamble, entries = parse(text)
    except ValueError as exc:
        sys.exit(f"{path}: {exc}")
    return path, text, entries


def cmd_init(args: argparse.Namespace) -> int:
    path = ledger_path(args.skill)
    if path.exists():
        print(f"ledger already exists: {path}")
        return 0
    if not path.parent.is_dir():
        sys.exit(f"skill directory does not exist: {path.parent}")
    path.write_text(ledger_header(args.skill), encoding="utf-8")
    print(f"created {path}")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    path, text, entries = load(args.skill)
    if args.outcome not in OUTCOMES:
        sys.exit(f"outcome must be one of {', '.join(OUTCOMES)}")
    for tok in args.metric or []:
        if not METRIC_RE.match(tok):
            sys.exit(f"metric must look like key=value with no spaces: {tok!r}")
    run = (entries[-1]["run"] + 1) if entries else 1
    ts = args.started or now_iso()
    block = [f"## {ts} | run {run:04d} | {args.outcome}",
             f"- actions: {args.actions}",
             f"- summary: {args.summary.strip()}"]
    if args.metric:
        block.append("- metrics: " + " ".join(args.metric))
    if args.detail:
        block.append("- details:")
        block.extend(f"  - {d.strip()}" for d in args.detail)
    if args.next:
        block.append(f"- next: {args.next.strip()}")
    new_text = text.rstrip("\n") + "\n\n" + "\n".join(block) + "\n"
    parse(new_text)  # self-check before writing
    path.write_text(new_text, encoding="utf-8")
    print(f"appended run {run:04d} to {path}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    path, text, entries = load(args.skill)
    chosen = entries[-args.last:] if args.last else entries
    if args.json:
        print(json.dumps(chosen, indent=2))
        return 0
    if not chosen:
        print(f"{path}: no entries yet")
        return 0
    for e in chosen:
        print(f"run {e['run']:04d}  {e['timestamp']}  {e['outcome']}  actions={e['actions']}")
        print(f"  {e['summary']}")
        if e["metrics"]:
            print("  metrics: " + " ".join(f"{k}={v}" for k, v in e["metrics"].items()))
        for d in e["details"]:
            print(f"    - {d}")
        if e["next"]:
            print(f"  next: {e['next']}")
    return 0


def cmd_seen(args: argparse.Namespace) -> int:
    path = ledger_path(args.skill)
    if not path.exists():
        return 1
    pattern = re.compile(r"(?<![\w:./@-])" + re.escape(args.key) + r"(?![\w:./@-])")
    return 0 if pattern.search(path.read_text(encoding="utf-8")) else 1


def cmd_check(args: argparse.Namespace) -> int:
    problems: list[str] = []
    base = skills_dir()
    targets = [base / args.skill] if args.skill else sorted(p for p in base.iterdir() if p.is_dir())
    for d in targets:
        if d.name.startswith(".") or d.name.startswith("_"):
            continue
        if not (d / "SKILL.md").exists():
            problems.append(f"{d}: missing SKILL.md")
        ledger = d / "LEDGER.md"
        if not ledger.exists():
            problems.append(f"{d}: missing LEDGER.md (every skill keeps a ledger)")
            continue
        try:
            parse(ledger.read_text(encoding="utf-8"))
        except ValueError as exc:
            problems.append(f"{ledger}: {exc}")
    for p in problems:
        print(p, file=sys.stderr)
    if not problems:
        print(f"ok: {len(targets)} skill ledger(s) valid")
    return 1 if problems else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init"); p.add_argument("--skill", required=True); p.set_defaults(fn=cmd_init)

    p = sub.add_parser("add")
    p.add_argument("--skill", required=True)
    p.add_argument("--outcome", required=True, choices=OUTCOMES)
    p.add_argument("--actions", required=True, type=int)
    p.add_argument("--summary", required=True)
    p.add_argument("--metric", action="append", help="key=value (repeatable)")
    p.add_argument("--detail", action="append", help="one detail line (repeatable)")
    p.add_argument("--next", help="what the next run should pick up")
    p.add_argument("--started", help="ISO-8601 start time; default is now in Pacific time")
    p.set_defaults(fn=cmd_add)

    p = sub.add_parser("show")
    p.add_argument("--skill", required=True)
    p.add_argument("--last", type=int, default=5)
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_show)

    p = sub.add_parser("seen")
    p.add_argument("--skill", required=True)
    p.add_argument("--key", required=True)
    p.set_defaults(fn=cmd_seen)

    p = sub.add_parser("check"); p.add_argument("--skill"); p.set_defaults(fn=cmd_check)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
