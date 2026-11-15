"""The capture index: which matches/pages we already hold, how complete each capture is, and what the browser batch mode should skip.
    python3 -m dataops.store index      # scan data/cricinfo, data/cricbuzz, data/reference/captures -> data/capture_index.json
    python3 -m dataops.store known      # JSON of COMPLETE match ids per site, to paste into the extension's "Import known ids" (it then never re-captures them)
    python3 -m dataops.store missing    # matches we hold that are incomplete (no scorecard, no playing XI tab, low ball count, captured while live) and need a re-capture
Three layers stop the same data being captured twice: (1) the extension remembers finished ids in the browser; (2) it is seeded with this index ('known'); (3) dataops.ingest
keeps one file per match id (by content hash, replacing it only with a MORE complete capture)."""
import glob, hashlib, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = f"{ROOT}/data/capture_index.json"; SCHEMA = 3


def describe(path):
    d = json.load(open(path, encoding="utf-8")); site = d.get("site") or ("cricbuzz" if "cricbuzz" in os.path.basename(path) else "cricinfo")
    pages = d.get("pages", {}); tabs = sorted({k.replace("_text", "") for k in pages})
    match = next((v["props"]["appPageProps"]["data"]["match"] for v in pages.values() if isinstance(v, dict) and v.get("props", {}).get("appPageProps", {}).get("data", {}).get("match")), {})
    names = " ".join(tabs)
    return {"site": site, "id": str(d.get("match_id", "")), "file": os.path.relpath(path, ROOT), "saved_at": d.get("saved_at"), "balls": len(d.get("comments", [])), "tabs": tabs,
            "has_scorecard": "scorecard" in names or bool(match), "has_xi": "playing-xi" in names or "squads" in names, "has_commentary_expected": match.get("hasCommentary"), "wants_xi": bool(match.get("hasMatchPlayers")),
            "state": match.get("state"), "schema": d.get("schema", 1), "sha1": hashlib.sha1(open(path, "rb").read()).hexdigest()[:12]}


def complete(r):
    ok = r["has_scorecard"] and r["state"] in (None, "POST") and (r["site"] != "cricinfo" or (r["schema"] >= SCHEMA and (r["has_xi"] or not r["wants_xi"])))
    if r["has_commentary_expected"]: ok = ok and r["balls"] >= 150
    return ok


def build():
    idx = {}
    for p in sorted(glob.glob(f"{ROOT}/data/cricinfo/*.json") + glob.glob(f"{ROOT}/data/cricbuzz/*.json")):
        try: r = describe(p)
        except Exception as e: print("skip", p, e); continue
        if not r["id"]: continue
        key = f"{r['site']}:{r['id']}"
        if key not in idx or (r["balls"], len(r["tabs"])) > (idx[key]["balls"], len(idx[key]["tabs"])): idx[key] = r
    for k, r in idx.items(): r["complete"] = complete(r)
    json.dump(idx, open(INDEX, "w"), indent=1); return idx


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "index"; idx = build()
    if cmd == "known":
        out = {}
        for k, r in idx.items():
            if r["complete"]: out.setdefault(r["site"], []).append(r["id"])
        print(json.dumps(out))
    elif cmd == "missing":
        for k, r in idx.items():
            if not r["complete"]: print(k, {x: r[x] for x in ("balls", "state", "has_xi", "wants_xi", "schema")})
    else:
        print(len(idx), "matches indexed;", sum(r["complete"] for r in idx.values()), "complete ->", os.path.relpath(INDEX, ROOT))
