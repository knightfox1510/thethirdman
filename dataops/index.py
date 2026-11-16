"""The master match index: every international match Cricinfo lists, built ONCE from list pages, then a capture queue from it.
Owner plan (Nov 2026): capture ALL matches from Cricinfo (it has line/length/shot/control/wagon that Cricsheet lacks); Cricsheet stays a cross-check, not a reason to skip a match.
    python3 -m dataops.index urls --template 'URL with {page}' --pages 26 [--out data/index/urls_odi.txt]   # list-page URLs to paste into the extension's batch box (each is saved as a page file)
    python3 -m dataops.index build <folder-with-saved-list-pages>        # -> data/index/matches.json (one row per match id: url, official number, date, teams, format, gender, raw text)
    python3 -m dataops.index check                                       # cross-check official numbers + dates against Cricsheet (proves the numbering assumption before you trust it)
    python3 -m dataops.index queue [--since 2003] [--format ODI] [--team India] [--chunk 500] [--only-missing-from-cricsheet]   # -> data/index/queue_NNN.txt (match URLs not yet captured, newest first)
A list page is any page whose rows link to matches (Statsguru match results, a season archive, a team results page): the extension's "page" job saves its tables and links, this tool reads them.
Match URLs of the legacy form /ci/engine/match/<id>.html are accepted (they redirect to the current URL in the browser)."""
import argparse, collections, datetime, glob, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDX = os.path.join(ROOT, "data", "index"); MATCHES = os.path.join(IDX, "matches.json")
NUM = re.compile(r"\b(Test|ODI|T20I|T20)\s*(?:no\.?|#|number)\s*(\d{1,5})\b", re.I)
VS = re.compile(r"([A-Z][A-Za-z .'&-]{1,28}?)\s+(?:v|vs|v\.)\s+([A-Z][A-Za-z .'&-]{1,28}?)(?=\s+(?:Test|ODI|T20I|T20|WODI|WT20I|#|\d|at\b|won|lost|tied|drawn|no result|match)|\s*,|\s*$)")
MON = {m: i for i, m in enumerate("jan feb mar apr may jun jul aug sep oct nov dec".split(), 1)}


def parse_date(t):
    m = re.search(r"\b(\d{4})-(\d{2})-(\d{2})\b", t)
    if m: return m.group(0)
    m = re.search(r"\b(\d{1,2})\s+([A-Za-z]{3})[a-z]*\s+(\d{4})\b", t)
    if m and m.group(2).lower() in MON: return f"{m.group(3)}-{MON[m.group(2).lower()]:02d}-{int(m.group(1)):02d}"
    m = re.search(r"\b([A-Za-z]{3})[a-z]*\s+(\d{1,2}),?\s+(\d{4})\b", t)
    if m and m.group(1).lower() in MON: return f"{m.group(3)}-{MON[m.group(1).lower()]:02d}-{int(m.group(2)):02d}"
    return None


def parse_row(text, url):
    t = re.sub(r"\s+", " ", text); n = NUM.search(t)
    fmt = None
    if n: fmt = {"t20": "T20I"}.get(n.group(1).lower(), n.group(1).upper() if n.group(1).lower() != "test" else "Test")
    elif re.search(r"\bT20I\b", t): fmt = "T20I"
    elif re.search(r"\bODI\b", t): fmt = "ODI"
    elif re.search(r"\bTest\b", t): fmt = "Test"
    v = VS.search(t)
    return {"number": int(n.group(2)) if n else None, "format": fmt, "date": parse_date(t), "teams": [v.group(1).strip(), v.group(2).strip()] if v else None,
            "gender": "female" if re.search(r"women|female|\bWT20I|\bWODI", t + " " + url, re.I) else "male"}


def mid(u):
    m = re.search(r"/series/[^/]+-\d+/[^/]+-(\d+)(?:/|$)", u) or re.search(r"/(?:ci/engine/)?match/(\d+)\.html", u)
    return m.group(1) if m else None


def build(folder):
    rows = {}; files = sorted(glob.glob(os.path.join(folder, "*.json")))
    for p in files:
        try: d = json.load(open(p, encoding="utf-8"))
        except Exception: continue
        try:                                                    # a saved series page: its own structured match list (id, title, date) is more reliable than row text
            for m in d["next_data"]["props"]["appPageProps"]["data"]["content"]["matches"]:
                if not (m and m.get("objectId") and m.get("slug") and m.get("series")): continue
                i = str(m["objectId"]); txt = f'{m.get("title", "")} {m.get("startDate", "")} {m.get("format", "")} {m.get("status", "")}'
                r = parse_row(txt, ""); r.update({"id": i, "url": f'https://www.espncricinfo.com/series/{m["series"]["slug"]}-{m["series"]["objectId"]}/{m["slug"]}-{i}/full-scorecard', "text": txt[:300], "source": os.path.basename(p)})
                r["date"] = (m.get("startDate") or "")[:10] or r["date"]; r["format"] = r["format"] or ({"TEST": "Test", "ODI": "ODI", "T20I": "T20I"}.get(str(m.get("format", "")).upper()))
                rows[i] = r
        except Exception: pass
        srcs = [d] + list((d.get("views") or {}).values())
        for src in srcs:
            for l in src.get("links", []) or d.get("links", []):
                if l.get("kind") != "match": continue
                i = str(l.get("id") or mid(l.get("url", "")) or "")
                if not i: continue
                r = parse_row(l.get("text", ""), l.get("url", "")); r.update({"id": i, "url": l["url"], "text": l.get("text", "")[:300], "source": os.path.basename(p)})
                old = rows.get(i)
                if not old or sum(v is not None for v in r.values()) > sum(v is not None for v in old.values()): rows[i] = r
    os.makedirs(IDX, exist_ok=True); out = sorted(rows.values(), key=lambda r: (r["date"] or "", r["id"]))
    json.dump(out, open(MATCHES, "w"), indent=1)
    c = collections.Counter((r["format"], r["gender"]) for r in out)
    print(f"{len(out)} matches from {len(files)} saved pages -> {os.path.relpath(MATCHES, ROOT)}")
    for k, v in sorted(c.items(), key=lambda x: str(x)): print("  ", k, v)
    print("  with number:", sum(1 for r in out if r["number"]), " with date:", sum(1 for r in out if r["date"]), " with teams:", sum(1 for r in out if r["teams"]))


def check():
    from . import gaps as G
    held = {}
    for r in G.load():
        if r["num"]: held[(r["fmt"], r["gender"], r["num"])] = r
    rows = json.load(open(MATCHES)); ok = bad = nomatch = 0; samples = []
    for r in rows:
        if not (r["number"] and r["format"] and r["date"]): continue
        h = held.get((r["format"], r["gender"], r["number"]))
        if not h: nomatch += 1; continue
        d = datetime.date.fromisoformat
        if abs((d(h["date"]) - d(r["date"])).days) <= 7 and set(map(str.lower, h["teams"])) & set(map(str.lower, r["teams"] or h["teams"])): ok += 1
        else: bad += 1; samples.append((r["format"], r["number"], r["date"], r["teams"], h["date"], h["teams"]))
    print(f"number+date agree with Cricsheet: {ok}; disagree: {bad}; not in Cricsheet (the gaps): {nomatch}")
    for s in samples[:10]: print("  DISAGREE", s)
    if bad > 0.02 * max(1, ok + bad): print("!! numbering does not line up: do NOT use the official number to dedupe")


def queue(a):
    rows = json.load(open(MATCHES)); known = set()
    cap = os.path.join(ROOT, "data", "capture_index.json")
    if os.path.exists(cap):
        for k, v in json.load(open(cap)).items():
            if k.startswith("cricinfo:") and v.get("complete"): known.add(k.split(":", 1)[1])
    held = set()
    if a.only_missing_from_cricsheet:
        from . import gaps as G
        held = {(r["fmt"], r["gender"], r["num"]) for r in G.load() if r["num"]}
    out = []
    for r in rows:
        if r["id"] in known: continue
        if a.format and r["format"] != a.format: continue
        if a.since and r["date"] and int(r["date"][:4]) < a.since: continue
        if a.team and not any(a.team.lower() in t.lower() for t in (r["teams"] or [])): continue
        if a.only_missing_from_cricsheet and r["number"] and (r["format"], r["gender"], r["number"]) in held: continue
        out.append(r)
    out.sort(key=lambda r: r["date"] or "", reverse=True)
    for f in glob.glob(os.path.join(IDX, "queue_*.txt")): os.remove(f)
    for k in range(0, len(out), a.chunk):
        with open(os.path.join(IDX, f"queue_{k // a.chunk + 1:03d}.txt"), "w") as f: f.write("\n".join(r["url"] for r in out[k:k + a.chunk]) + "\n")
    print(f"{len(out)} matches to capture ({len(rows)} in the index, {len(known)} already complete) -> {-(-len(out) // a.chunk)} queue file(s) in data/index/")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    u = sp.add_parser("urls"); u.add_argument("--template", required=True); u.add_argument("--pages", type=int, required=True); u.add_argument("--out")
    b = sp.add_parser("build"); b.add_argument("folder")
    sp.add_parser("check")
    q = sp.add_parser("queue"); q.add_argument("--since", type=int); q.add_argument("--format"); q.add_argument("--team"); q.add_argument("--chunk", type=int, default=500); q.add_argument("--only-missing-from-cricsheet", action="store_true")
    a = ap.parse_args()
    if a.cmd == "urls":
        assert "{page}" in a.template, "template needs {page}"
        t = "\n".join(a.template.format(page=p) for p in range(1, a.pages + 1)) + "\n"
        if a.out: os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True); open(a.out, "w").write(t); print(f"{a.pages} URLs -> {a.out}")
        else: print(t)
    elif a.cmd == "build": build(a.folder)
    elif a.cmd == "check": check()
    else: queue(a)
