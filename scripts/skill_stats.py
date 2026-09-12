#!/usr/bin/env python3
"""Performance and hygiene facts about every skill, computed from the ledgers.

Used by the skill-improver skill so its judgments start from numbers rather
than impressions. Two subcommands:

  stats [--since-days N] [--json]   per-skill run counts, outcomes, actions,
                                    metric trends, stuck next-lines, repeats
  lint  [--json]                    references in SKILL.md and references/ to
                                    paths, scripts, or skills that don't exist,
                                    oversized files, missing frontmatter fields

Exit status: 0 always for stats; for lint, 1 if any finding is reported.
No third-party dependencies.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ledger  # noqa: E402

SKILL_MD_MAX_LINES = 250
REFERENCE_MAX_LINES = 400


def skill_dirs(root: Path) -> list[Path]:
    base = root / ".claude" / "skills"
    return sorted(p for p in base.iterdir() if p.is_dir() and not p.name.startswith((".", "_")))


def parse_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def numeric(v: str):
    try:
        return float(v)
    except ValueError:
        return None


def skill_stats(d: Path, since: datetime | None) -> dict:
    text = (d / "LEDGER.md").read_text(encoding="utf-8") if (d / "LEDGER.md").exists() else ""
    _, entries = ledger.parse(text) if text else ("", [])
    all_runs = len(entries)
    if since:
        entries = [e for e in entries if parse_ts(e["timestamp"]) >= since]
    outcomes = Counter(e["outcome"] for e in entries)
    actions = [e["actions"] for e in entries]

    # Metric trend: first and last numeric value per key in the window.
    trend: dict[str, dict] = {}
    for e in entries:
        for k, v in e["metrics"].items():
            n = numeric(v)
            t = trend.setdefault(k, {"first": None, "last": None, "non_numeric": 0, "samples": 0})
            t["samples"] += 1
            if n is None:
                t["non_numeric"] += 1
                continue
            if t["first"] is None:
                t["first"] = n
            t["last"] = n

    # A next-line that repeats verbatim across runs is work that never gets done.
    nexts = Counter(e["next"] for e in entries if e["next"])
    stuck_next = [n for n, c in nexts.items() if c >= 2]

    # Repeated detail prefixes (error, note, policy) point at recurring friction.
    detail_kinds = Counter(dl.split("|", 1)[0].split(":", 1)[0].strip() for e in entries for dl in e["details"])
    error_lines = [dl for e in entries for dl in e["details"] if dl.lower().startswith(("error", "note"))]

    last = entries[-1] if entries else None
    return {
        "skill": d.name,
        "runs_total": all_runs,
        "runs_in_window": len(entries),
        "outcomes": dict(outcomes),
        "actions_total": sum(actions),
        "actions_per_run": round(sum(actions) / len(actions), 2) if actions else None,
        "zero_action_runs": sum(1 for a in actions if a == 0),
        "metric_trend": trend,
        "stuck_next": stuck_next,
        "detail_kinds": dict(detail_kinds),
        "error_or_note_lines": error_lines[-10:],
        "last_run": {"timestamp": last["timestamp"], "outcome": last["outcome"], "next": last["next"]} if last else None,
        "handoffs_emitted": sum(1 for e in entries for dl in e["details"] if dl.startswith("handoff:")),
    }


PATH_RE = re.compile(r"`((?:\.claude/|scripts/|tests/|data/|references/)[A-Za-z0-9_./\-]+)`")
SKILL_REF_RE = re.compile(r"\b([a-z][a-z0-9]+(?:-[a-z0-9]+)+)\b")


def lint_skill(root: Path, d: Path, known_skills: set[str]) -> list[str]:
    findings: list[str] = []
    skill_md = d / "SKILL.md"
    if not skill_md.exists():
        return [f"{d.name}: missing SKILL.md"]
    text = skill_md.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        findings.append(f"{d.name}/SKILL.md: no frontmatter")
    else:
        fm = m.group(1)
        for field in ("name:", "description:", "version:"):
            if field not in fm:
                findings.append(f"{d.name}/SKILL.md: frontmatter missing {field}")
    n = text.count("\n") + 1
    if n > SKILL_MD_MAX_LINES:
        findings.append(f"{d.name}/SKILL.md: {n} lines, over the {SKILL_MD_MAX_LINES}-line budget; move detail to references/")
    if "scripts/ledger.py add" not in text:
        findings.append(f"{d.name}/SKILL.md: does not end the run with a ledger entry")

    files = [skill_md] + sorted((d / "references").glob("**/*.md")) if (d / "references").exists() else [skill_md]
    for f in files:
        body = f.read_text(encoding="utf-8")
        rel = f.relative_to(root)
        if f != skill_md and body.count("\n") + 1 > REFERENCE_MAX_LINES:
            findings.append(f"{rel}: over {REFERENCE_MAX_LINES} lines; split or archive old material")
        for ref in set(PATH_RE.findall(body)):
            clean = ref.rstrip("/")
            candidates = [root / clean, d / clean]
            if "<" in clean or "*" in clean or "{" in clean:
                continue
            # .claude/data/ holds git-ignored, optional files (tokens, caches);
            # tmp-build/ is per-run scratch. Neither is expected to exist.
            if clean.startswith((".claude/data/", "tmp-build")):
                continue
            if not any(c.exists() for c in candidates):
                findings.append(f"{rel}: references `{ref}` which does not exist")
        for name in set(SKILL_REF_RE.findall(body)):
            if name.endswith("-processor") or name.endswith("-growth") or name.endswith("-improver"):
                if name not in known_skills:
                    findings.append(f"{rel}: mentions skill `{name}` which is not in .claude/skills")
    return findings


def cmd_stats(args, root: Path) -> int:
    since = datetime.now(timezone.utc) - timedelta(days=args.since_days) if args.since_days else None
    results = [skill_stats(d, since) for d in skill_dirs(root)]
    if args.json:
        print(json.dumps(results, indent=2))
        return 0
    for r in results:
        print(f"{r['skill']}: {r['runs_in_window']} runs in window ({r['runs_total']} total), "
              f"outcomes {r['outcomes']}, actions/run {r['actions_per_run']}, zero-action runs {r['zero_action_runs']}")
        for k, t in r["metric_trend"].items():
            if t["first"] is not None:
                print(f"    {k}: {t['first']:g} -> {t['last']:g} over {t['samples']} runs")
        for s in r["stuck_next"]:
            print(f"    stuck next: {s}")
        for line in r["error_or_note_lines"]:
            print(f"    {line}")
        if r["last_run"]:
            print(f"    last run {r['last_run']['timestamp']} {r['last_run']['outcome']}")
    return 0


def cmd_lint(args, root: Path) -> int:
    dirs = skill_dirs(root)
    known = {d.name for d in dirs}
    findings = [f for d in dirs for f in lint_skill(root, d, known)]
    if args.json:
        print(json.dumps(findings, indent=2))
    else:
        for f in findings:
            print(f)
        if not findings:
            print(f"ok: {len(dirs)} skills, no lint findings")
    return 1 if findings else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=None, help="repository root (default: git toplevel)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("stats"); p.add_argument("--since-days", type=int, default=0); p.add_argument("--json", action="store_true"); p.set_defaults(fn=cmd_stats)
    p = sub.add_parser("lint"); p.add_argument("--json", action="store_true"); p.set_defaults(fn=cmd_lint)
    args = ap.parse_args(argv)
    root = Path(args.root) if args.root else ledger.repo_root()
    return args.fn(args, root)


if __name__ == "__main__":
    sys.exit(main())
