#!/usr/bin/env python3
"""Active patron counts and monthly revenue from the Patreon API, counts only.

Resolves the creator token through scripts/cs_secrets.py (environment variable,
then 1Password, then the git-ignored config file) and never prints it.
Output is aggregate numbers safe to commit to this public repository.

  python3 scripts/patreon_stats.py                 # print counts as JSON
  python3 scripts/patreon_stats.py --out data/patreon_stats.json

Exit 0 with JSON on success; exit 1 with a WARN line if no token is
available or the API refuses the request, so callers fall back to the
supporter roll.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cs_secrets  # noqa: E402

CAMPAIGN_ID = "4769349"
BASE = "https://www.patreon.com/api/oauth2/v2"


def fetch_members(token: str, campaign_id: str) -> list[dict]:
    fields = "patron_status,currently_entitled_amount_cents,last_charge_status,is_follower"
    url = f"{BASE}/campaigns/{campaign_id}/members?" + urllib.parse.urlencode(
        {"fields[member]": fields, "page[count]": "100"})
    members: list[dict] = []
    while url:
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}",
                                                   "User-Agent": "cleanstreets-skills/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            page = json.load(resp)
        members.extend(m.get("attributes", {}) for m in page.get("data", []))
        cursor = page.get("meta", {}).get("pagination", {}).get("cursors", {}).get("next")
        url = (f"{BASE}/campaigns/{campaign_id}/members?" + urllib.parse.urlencode(
            {"fields[member]": fields, "page[count]": "100", "page[cursor]": cursor})) if cursor else None
    return members


def summarize(members: list[dict]) -> dict:
    active = [m for m in members if m.get("patron_status") == "active_patron"]
    return {
        "synced_at": datetime.now(timezone.utc).isoformat(timespec="minutes"),
        "campaign_id": CAMPAIGN_ID,
        "active_patrons": len(active),
        "declined_patrons": sum(1 for m in members if m.get("patron_status") == "declined_patron"),
        "former_patrons": sum(1 for m in members if m.get("patron_status") == "former_patron"),
        "followers": sum(1 for m in members if m.get("patron_status") is None and m.get("is_follower")),
        "mrr_usd": round(sum(m.get("currently_entitled_amount_cents") or 0 for m in active) / 100, 2),
        "total_members": len(members),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", help="also write the JSON to this path")
    ap.add_argument("--campaign", default=CAMPAIGN_ID)
    args = ap.parse_args(argv)

    token, source = cs_secrets.resolve("patreon", with_source=True)
    if not token:
        print("WARN: no Patreon token available; use the supporter roll instead", file=sys.stderr)
        return 1
    try:
        stats = summarize(fetch_members(token, args.campaign))
    except urllib.error.HTTPError as exc:
        print(f"WARN: Patreon API returned HTTP {exc.code}; use the supporter roll instead", file=sys.stderr)
        return 1
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"WARN: Patreon API unreachable ({type(exc).__name__}); use the supporter roll instead", file=sys.stderr)
        return 1
    stats["token_source"] = source
    text = json.dumps(stats, indent=2)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
