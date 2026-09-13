#!/usr/bin/env python3
"""Render the latest album photos into the website's #photos section.

Reads data/photos.json (written by scripts/shared_album.py sync) and
rewrites the markup between <!-- photos:start --> and <!-- photos:end -->
in index.html. Everything outside the markers is untouched.

  python3 scripts/update_photos.py            # newest 12
  python3 scripts/update_photos.py --count 8
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_HTML = ROOT / "index.html"
PHOTOS = ROOT / "data" / "photos.json"
START, END = "<!-- photos:start -->", "<!-- photos:end -->"


def nice_date(iso: str | None) -> str:
    if not iso:
        return "recently"
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).strftime("%B %-d, %Y")
    except ValueError:
        return iso[:10]


def render(photos: list[dict], count: int) -> str:
    tiles = []
    for p in photos[:count]:
        alt = html.escape(f"Clean Streets crew cleanup photo, {nice_date(p.get('date'))}")
        cap = html.escape(p.get("caption") or "")
        tiles.append(
            '      <figure class="m-0">\n'
            f'       <img alt="{alt}" class="w-full aspect-square object-cover rounded-xl shadow-sm border border-orange-100" '
            f'height="{p.get("height", 0)}" loading="lazy" src="{html.escape(p["file"])}" width="{p.get("width", 0)}"/>\n'
            + (f'       <figcaption class="text-xs text-gray-500 mt-1">{cap}</figcaption>\n' if cap else "")
            + "      </figure>"
        )
    if not tiles:
        return '      <p class="text-gray-500 text-center">Photos from the crew are on their way.</p>'
    return "\n".join(tiles)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--count", type=int, default=12)
    args = ap.parse_args(argv)
    data = json.loads(PHOTOS.read_text(encoding="utf-8"))
    text = INDEX_HTML.read_text(encoding="utf-8")
    if START not in text or END not in text:
        sys.exit("ERROR: photo markers not found in index.html")
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    new_block = f"{START}\n{render(data.get('photos', []), args.count)}\n     {END}"
    updated = pattern.sub(lambda _: new_block, text, count=1)
    if updated != text:
        INDEX_HTML.write_text(updated, encoding="utf-8")
        print(f"OK: rendered {min(args.count, len(data.get('photos', [])))} photos into index.html")
    else:
        print("OK: gallery unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
