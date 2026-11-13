#!/usr/bin/env python3
"""Read or update the live tracker on the control-room site (the schedule now lives in the site's storage).
Env: TTM_SITE_URL (e.g. https://thethirdman.vercel.app), TTM_SITE_KEY (the site password). Never commit either.
  python3 site_sync.py show
  python3 site_sync.py set "<content substring>" status=Posted link=https://youtu.be/xxx notes="..."
  python3 site_sync.py add date=2026-11-20 platform="YouTube long" content="Title" status="To build"
"""
import json, os, sys, urllib.request

URL = os.environ.get("TTM_SITE_URL", "").rstrip("/")
KEY = os.environ.get("TTM_SITE_KEY", "")

def call(method, body=None):
    if not URL: sys.exit("set TTM_SITE_URL")
    req = urllib.request.Request(URL + "/api/schedule", method=method, data=json.dumps(body).encode() if body else None,
                                 headers={"content-type": "application/json", "x-ttm-key": KEY})
    try:
        with urllib.request.urlopen(req, timeout=30) as r: return json.load(r)
    except urllib.error.HTTPError as e: sys.exit(f"{e.code}: {e.read().decode()[:300]}")

def kv(args): return dict(a.split("=", 1) for a in args)

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "show"
    cur = call("GET")
    rows, base = cur.get("rows") or [], cur.get("updated")
    if cmd == "show":
        for r in sorted(rows, key=lambda r: r.get("date") or "9"): print(r["date"], "|", r["status"], "|", r["content"])
        return
    if not KEY: sys.exit("set TTM_SITE_KEY")
    if cmd == "set":
        hit = [r for r in rows if sys.argv[2].lower() in r["content"].lower()]
        if not hit: sys.exit("no row matches")
        for r in hit: r.update(kv(sys.argv[3:]))
    elif cmd == "add":
        rows.append({"id": None, **kv(sys.argv[2:])})
    else: sys.exit(__doc__)
    print(call("PUT", {"rows": rows, "base": base}))

main()
