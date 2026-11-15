"""Summarise captures from the Chrome extension's batch mode (page_*.json, list_*.json, cricinfo_*.json, cricbuzz_*.json) so they can be used as reference data.
    python3 -m dataops.ingest <folder>      # copies them to data/cricinfo|cricbuzz|reference/captures and prints what each holds
A team results list / Statsguru table captured with 'Save this page' becomes a Tier A reference for dataops/audit.py (add the parser for its layout the first time one arrives)."""
import json, os, shutil, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(folder):
    for f in sorted(os.listdir(folder)):
        if not f.endswith(".json"): continue
        d = json.load(open(os.path.join(folder, f), encoding="utf-8"))
        if f.startswith(("cricinfo_", "cricbuzz_")): dst = f"{ROOT}/data/{f.split('_')[0]}"; info = f"{len(d.get('comments', []))} balls, tabs {list(d.get('pages', {}))[:4]}"
        elif f.startswith(("page_", "list_")):
            dst = f"{ROOT}/data/reference/captures"; info = f"{len(d.get('tables', []))} tables, {len(d.get('links', d.get('matches', [])))} match links, title {d.get('title', '')[:50]!r}"
        else: continue
        os.makedirs(dst, exist_ok=True); target = os.path.join(dst, f)
        if os.path.exists(target):                                                 # never keep two copies of a match: replace only with a MORE complete capture
            import hashlib
            if hashlib.sha1(open(target, "rb").read()).digest() == hashlib.sha1(open(os.path.join(folder, f), "rb").read()).digest(): print(f"{f[:60]:60s} duplicate (identical): skipped"); continue
            if f.startswith(("cricinfo_", "cricbuzz_")):
                old = json.load(open(target, encoding="utf-8"))
                if (len(old.get("comments", [])), len(old.get("pages", {}))) >= (len(d.get("comments", [])), len(d.get("pages", {}))) and old.get("schema", 1) >= d.get("schema", 1): print(f"{f[:60]:60s} existing capture is as complete or better: skipped"); continue
        shutil.copy(os.path.join(folder, f), target); print(f"{f[:60]:60s} -> {os.path.relpath(dst, ROOT)}  {info}")
    from . import store; idx = store.build(); print(f"index: {len(idx)} matches, {sum(r['complete'] for r in idx.values())} complete")


if __name__ == "__main__":
    main(sys.argv[1])
