#!/usr/bin/env python3
"""Read the public iCloud Shared Album that Travis posts cleanup photos to.

The album's "Public Website" link needs no login. This script lists the
photos, downloads new ones into images/album/ (resized for the web), and
writes data/photos.json, which the website gallery and the field-updates
skill read.

  python3 scripts/shared_album.py list            # newest first, as JSON
  python3 scripts/shared_album.py sync            # download new photos, update data/photos.json
  python3 scripts/shared_album.py sync --keep 60  # keep at most 60 newest on disk

The album token defaults to the Clean Streets album; override with
--token or the CLEANSTREETS_ALBUM_TOKEN environment variable.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_TOKEN = "D2Av3MQjuCw8TL1ZXjOY8RyIL6ACAEQARogAOQ1MbkrM6kKhxtgPjdvaWJDExmXQEtOg2jOBdZ2RjM"
B62 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
ROOT = Path(__file__).resolve().parents[1]
ALBUM_DIR = ROOT / "images" / "album"
INDEX = ROOT / "data" / "photos.json"
MAX_EDGE = 1400  # pixels; enough for a full-width gallery tile and social posts


def _b62(s: str) -> int:
    n = 0
    for c in s:
        n = n * 62 + B62.index(c)
    return n


def host_for(token: str) -> str:
    part = _b62(token[1]) if token[0] == "A" else _b62(token[1:3])
    return f"p{part:02d}-sharedstreams.icloud.com"


def _post(host: str, token: str, path: str, body: dict):
    req = urllib.request.Request(
        f"https://{host}/{token}/sharedstreams/{path}", data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "Origin": "https://www.icloud.com",
                 "User-Agent": "Mozilla/5.0 (cleanstreets-skills)"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, dict(r.headers), json.load(r)
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, dict(e.headers), json.loads(raw)
        except ValueError:
            return e.code, dict(e.headers), {"error": raw[:200].decode(errors="replace")}


def fetch_stream(token: str) -> tuple[str, dict]:
    host = host_for(token)
    status, headers, data = _post(host, token, "webstream", {"streamCtag": None})
    redirect = headers.get("X-Apple-MMe-Host") or (data.get("X-Apple-MMe-Host") if isinstance(data, dict) else None)
    if status == 330 or (redirect and "photos" not in data):
        host = redirect
        status, headers, data = _post(host, token, "webstream", {"streamCtag": None})
    if status != 200 or "photos" not in data:
        raise SystemExit(f"ERROR: album fetch failed (HTTP {status}): {str(data)[:200]}")
    return host, data


def best_derivative(photo: dict) -> tuple[str, dict]:
    """The largest derivative (by width) and its checksum."""
    best = max(photo["derivatives"].items(), key=lambda kv: int(kv[1].get("width", 0)))
    return best[0], best[1]


def asset_urls(host: str, token: str, guids: list[str]) -> dict:
    """POST photo GUIDs; the response's items are keyed by derivative checksum."""
    status, _, data = _post(host, token, "webasseturls", {"photoGuids": guids})
    if status != 200:
        raise SystemExit(f"ERROR: asset url fetch failed (HTTP {status})")
    return data.get("items", {})


def photo_records(data: dict) -> list[dict]:
    recs = []
    for p in data.get("photos", []):
        if p.get("mediaAssetType") == "video":
            continue
        key, d = best_derivative(p)
        recs.append({
            "guid": p["photoGuid"],
            "date": p.get("dateCreated"),
            "caption": (p.get("caption") or "").strip(),
            "width": int(d.get("width", 0)),
            "height": int(d.get("height", 0)),
            "checksum": d["checksum"],
        })
    recs.sort(key=lambda r: r["date"] or "", reverse=True)
    return recs


def cmd_list(args) -> int:
    _, data = fetch_stream(args.token)
    recs = photo_records(data)
    print(json.dumps({"album": data.get("streamName"), "count": len(recs), "photos": recs[: args.limit]}, indent=2))
    return 0


def _resize(raw: bytes) -> tuple[bytes, int, int]:
    try:
        from PIL import Image, ImageOps
    except ImportError:
        return raw, 0, 0
    im = Image.open(io.BytesIO(raw))
    im = ImageOps.exif_transpose(im).convert("RGB")
    im.thumbnail((MAX_EDGE, MAX_EDGE))
    out = io.BytesIO()
    im.save(out, "JPEG", quality=82, optimize=True, progressive=True)
    return out.getvalue(), im.width, im.height


def cmd_sync(args) -> int:
    host, data = fetch_stream(args.token)
    recs = photo_records(data)[: args.keep]
    ALBUM_DIR.mkdir(parents=True, exist_ok=True)
    existing = json.loads(INDEX.read_text()) if INDEX.exists() else {"photos": []}
    have = {p["guid"]: p for p in existing.get("photos", [])}

    new = [r for r in recs if r["guid"] not in have or not (ROOT / have[r["guid"]]["file"]).exists()]
    if new:
        urls = asset_urls(host, args.token, [r["guid"] for r in new])
    downloaded = 0
    for r in new:
        item = urls.get(r["checksum"])
        if not item:
            print(f"WARN: no asset url for {r['guid'][:8]}", file=sys.stderr)
            continue
        url = f"https://{item['url_location']}{item['url_path']}"
        with urllib.request.urlopen(url, timeout=120) as resp:
            raw = resp.read()
        body, w, h = _resize(raw)
        name = f"{(r['date'] or 'undated')[:10]}-{r['guid'][:8].lower()}.jpg"
        (ALBUM_DIR / name).write_bytes(body)
        r["file"] = f"images/album/{name}"
        if w:
            r["width"], r["height"] = w, h
        downloaded += 1

    merged = []
    for r in recs:
        rec = have.get(r["guid"], r)
        rec.update({k: v for k, v in r.items() if k != "file"})
        if "file" in rec and (ROOT / rec["file"]).exists():
            merged.append(rec)
    keep_files = {ROOT / r["file"] for r in merged}
    removed = 0
    for f in ALBUM_DIR.glob("*.jpg"):
        if f not in keep_files:
            f.unlink()
            removed += 1
    INDEX.write_text(json.dumps({
        "album": data.get("streamName"),
        "synced_at": datetime.now(timezone.utc).isoformat(timespec="minutes"),
        "count": len(merged),
        "photos": [{k: v for k, v in r.items() if k != "checksum"} for r in merged],
    }, indent=2) + "\n")
    print(f"OK: album '{data.get('streamName')}' has {len(recs)} photos in range; "
          f"downloaded {downloaded} new, removed {removed} old; {len(merged)} indexed in {INDEX.relative_to(ROOT)}")
    return 0


def main(argv=None) -> int:
    import os
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--token", default=os.environ.get("CLEANSTREETS_ALBUM_TOKEN", DEFAULT_TOKEN))
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("list"); p.add_argument("--limit", type=int, default=20); p.set_defaults(fn=cmd_list)
    p = sub.add_parser("sync"); p.add_argument("--keep", type=int, default=48); p.set_defaults(fn=cmd_sync)
    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
