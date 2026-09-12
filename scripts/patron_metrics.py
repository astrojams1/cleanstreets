#!/usr/bin/env python3
"""Patron metrics from the repository's own data, no credentials required.

data/supporters.csv is refreshed daily from the Patrons Google Sheet by
scripts/update_supporters.py (see .github/workflows/update_supporters.yml).
Its git history is therefore a free, dated record of who appears on the
public supporter roll. This script reports the current roll and the names
that joined or left it since a past commit.

  python3 scripts/patron_metrics.py                 # current roll vs 7 days ago
  python3 scripts/patron_metrics.py --since-days 30
  python3 scripts/patron_metrics.py --json

Caveat: the roll lists everyone the sheet marks as a supporter, which is
not the same as "currently paying on Patreon". Treat joins as the reliable
signal; treat the total as an upper bound on active patrons. The
patreon-growth skill uses the Patreon API for the active count when a token
is available and falls back to this script otherwise.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

CSV_REL = "data/supporters.csv"


def git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def repo_root() -> Path:
    return Path(git("rev-parse", "--show-toplevel").strip())


def parse_roll(text: str) -> tuple[list[str], list[str]]:
    """Return (all_names, top_supporter_names) from supporters.csv text."""
    reader = csv.reader(io.StringIO(text))
    next(reader, None)  # header: Supporter, Top Supporter
    names: list[str] = []
    top: list[str] = []
    for row in reader:
        if not row or not row[0].strip():
            continue
        name = row[0].strip()
        names.append(name)
        if len(row) > 1 and row[1].strip().upper() == "TRUE":
            top.append(name)
    return names, top


def commit_before(days: int) -> str | None:
    """Newest commit touching the CSV that is at least `days` days old."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S")
    out = git("log", "-1", "--format=%H", f"--before={cutoff}", "--", CSV_REL).strip()
    return out or None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--since-days", type=int, default=7)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    root = repo_root()
    current_text = (root / CSV_REL).read_text(encoding="utf-8")
    names, top = parse_roll(current_text)
    last_change = git("log", "-1", "--format=%ad", "--date=short", "--", CSV_REL).strip()

    result = {
        "as_of_commit_date": last_change,
        "roll_total": len(names),
        "top_supporters": len(top),
        "since_days": args.since_days,
        "baseline_commit": None,
        "joined": [],
        "left": [],
    }
    ref = commit_before(args.since_days)
    if ref:
        old_names, _ = parse_roll(git("show", f"{ref}:{CSV_REL}"))
        old_set, new_set = set(old_names), set(names)
        result["baseline_commit"] = ref[:7]
        result["joined"] = sorted(new_set - old_set)
        result["left"] = sorted(old_set - new_set)

    if args.json:
        print(json.dumps(result, indent=2))
        return 0
    print(f"Supporter roll: {result['roll_total']} names ({result['top_supporters']} top supporters), "
          f"last updated {last_change}")
    if ref:
        print(f"Since {args.since_days}d ago (commit {result['baseline_commit']}): "
              f"+{len(result['joined'])} joined, -{len(result['left'])} left")
        for n in result["joined"]:
            print(f"  + {n}")
        for n in result["left"]:
            print(f"  - {n}")
    else:
        print(f"No commit older than {args.since_days} days touches {CSV_REL}; no diff available")
    return 0


if __name__ == "__main__":
    sys.exit(main())
