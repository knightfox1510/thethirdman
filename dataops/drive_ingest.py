"""Stream the owner's Cricinfo scrapes from Drive into compact, verified match records, then (optionally) move each processed raw file into Drive's Archive.
    python3 -m dataops.drive_ingest list                       # what is in the Drive inbox folders (no download)
    python3 -m dataops.drive_ingest run [--limit N] [--only odi|ipl] [--move] [--workers 4]
Per match: data/cricinfo_compact/<matchid>.json.gz = meta, innings totals, batting/bowling cards, ball table (id, inning, over, ball, batter, bowler, runs, extras, wicket, wagon x/y/zone, line, length, shot, control)
plus reconciliation (ball sums vs scorecard totals) and coverage flags. Manifest: data/cricinfo_compact/manifest.jsonl (one line per source file: status OK / TEXT_ONLY / MISMATCH / BAD / SERIES / DUP).
A raw file is moved to Archive/Cricinfo extracts/<odi|ipl>/ ONLY after its record is written and reconciled (OK or TEXT_ONLY or SERIES); mismatches stay put for review. Never deletes anything.
The raw files are 1-110 MB each (about 19 GB in all), too big to hold: each is downloaded to a temp file, compacted, and removed."""
import gzip, hashlib, json, os, re, sys, tempfile, threading, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, f"{ROOT}/publish")
from gauth import api, token
OUT = f"{ROOT}/data/cricinfo_compact"; MAN = f"{OUT}/manifest.jsonl"; ROOTID = "1pHAKlG4kKtXbIS5JK6zj7UcVcsWIKuj7"; D = "https://www.googleapis.com/drive/v3/files"; LOCK = threading.Lock()
def call(*a, **k):
    for i in range(6):
        try: return api(*a, **k)
        except BaseException as e:
            if i == 5: raise
            time.sleep(2 * (i + 1))
def ls(pid):
    out = []; tok = None
    while True:
        p = {"q": f"'{pid}' in parents and trashed=false", "fields": "nextPageToken,files(id,name,mimeType,size,md5Checksum)", "pageSize": 1000, "supportsAllDrives": "true", "includeItemsFromAllDrives": "true"}
        if tok: p["pageToken"] = tok
        r = call("GET", D, "drive", params=p); out += r.get("files", []); tok = r.get("nextPageToken")
        if not tok: return out
def find(pid, name, make=False):
    for f in ls(pid):
        if f["name"] == name and f["mimeType"].endswith("folder"): return f["id"]
    if not make: raise SystemExit(f"folder {name} not found")
    return call("POST", D + "?supportsAllDrives=true", "drive", body={"name": name, "mimeType": "application/vnd.google-apps.folder", "parents": [pid]})["id"]
def folders():
    b = find(find(find(ROOTID, "Data"), "Cricinfo extracts"), "Data"); return {"odi": find(b, "Cricinfo extracts"), "ipl": find(b, "Cricinfo IPL extracts")}
def download(fid, path):
    req = urllib.request.Request(f"{D}/{fid}?alt=media&supportsAllDrives=true", headers={"Authorization": "Bearer " + token("drive")}); h = hashlib.md5()
    with urllib.request.urlopen(req, timeout=600) as u, open(path, "wb") as o:
        while True:
            b = u.read(1 << 20)
            if not b: break
            o.write(b); h.update(b)
    return h.hexdigest()
def compact(d):
    """-> (record, status, note). Modern layout: pages['full-scorecard'] JSON. Old layout: text pages only."""
    pg = d.get("pages", {}); mid = str(d.get("match_id", ""))
    sc = (pg.get("full-scorecard") or {}).get("props", {}).get("appPageProps", {}).get("data")
    if not sc:
        txt = {k: v for k, v in pg.items() if k.endswith("_text") or isinstance(v, str)}
        return {"match_id": mid, "slug": d.get("match_slug"), "layout": "text", "text": txt, "series": d.get("series"), "url": d.get("page_url")}, "TEXT_ONLY", "scorecard text only"
    m = sc["match"]; inns = sc["content"].get("innings", []) + sc["content"].get("superOverInnings", []); teams = {t["team"]["id"]: t["team"].get("name") for t in m.get("teams", []) if t.get("team")}
    rec = {"match_id": mid, "slug": m.get("slug"), "layout": "json", "title": m.get("title"), "format": m.get("format"), "season": m.get("season"), "start": m.get("startDate"), "series": (m.get("series") or {}).get("longName"), "ground": (m.get("ground") or {}).get("name"),
           "status": m.get("statusText"), "winner_team_id": m.get("winnerTeamId"), "toss_winner_team_id": m.get("tossWinnerTeamId"), "teams": [{"id": t["team"].get("id"), "name": t["team"].get("name")} for t in m.get("teams", []) if t.get("team")], "innings": [], "balls": []}
    players = {}
    for i in inns:
        for b in i.get("inningBatsmen", []): players[b["player"]["id"]] = b["player"].get("name")
        for b in i.get("inningBowlers", []): players[b["player"]["id"]] = b["player"].get("name")
        rec["innings"].append({"n": i["inningNumber"], "team": (i.get("team") or {}).get("name"), "runs": i["runs"], "wickets": i["wickets"], "overs": i.get("overs"), "balls": i.get("balls"), "extras": i.get("extras"),
                               "bat": [{"id": b["player"]["id"], "runs": b.get("runs"), "balls": b.get("balls"), "fours": b.get("fours"), "sixes": b.get("sixes"), "out": b.get("dismissalText", {}).get("short") if isinstance(b.get("dismissalText"), dict) else b.get("dismissalText")} for b in i.get("inningBatsmen", [])],
                               "bowl": [{"id": b["player"]["id"], "overs": b.get("overs"), "maidens": b.get("maidens"), "conceded": b.get("conceded"), "wickets": b.get("wickets")} for b in i.get("inningBowlers", [])]})
    rec["players"] = {str(k): v for k, v in players.items()}
    for x in d.get("comments", []):
        if x.get("ballNumber") is None or x.get("batsmanPlayerId") is None or x.get("totalRuns") is None: continue
        rec["balls"].append([x["inningNumber"], x["overNumber"], x["ballNumber"], x["batsmanPlayerId"], x["bowlerPlayerId"], x["batsmanRuns"], x["totalRuns"], x.get("wides", 0), x.get("noballs", 0), x.get("byes", 0), x.get("legbyes", 0),
                             int(bool(x.get("isWicket"))), x.get("dismissalType"), x.get("outPlayerId"), x.get("wagonX"), x.get("wagonY"), x.get("wagonZone"), x.get("pitchLine"), x.get("pitchLength"), x.get("shotType"), x.get("shotControl")])
    rec["ball_cols"] = "inn,over,ball,batter,bowler,bat_runs,total_runs,wides,noballs,byes,legbyes,wicket,dismissal,out_player,wagon_x,wagon_y,wagon_zone,line,length,shot,control".split(",")
    B = rec["balls"]; cov = {"balls": len(B), "wagon": sum(1 for b in B if b[16]), "line": sum(1 for b in B if b[17]), "shot": sum(1 for b in B if b[19])}; rec["coverage"] = cov
    if not B: return rec, "OK", "scorecard only (no ball-by-ball)"
    bad = []
    for i in rec["innings"]:
        if i["n"] > 2: continue
        bs = [b for b in B if b[0] == i["n"]]
        if not bs: bad.append(f"inn{i['n']}: no balls"); continue
        runs = sum(b[6] for b in bs); wk = sum(b[11] for b in bs)
        if runs != i["runs"] or wk != i["wickets"]: bad.append(f"inn{i['n']}: balls {runs}/{wk} vs card {i['runs']}/{i['wickets']}")
    rec["reconcile"] = bad or "ok"
    return rec, ("MISMATCH" if bad else "OK"), "; ".join(bad)
def process(src, f, move, arch, st):
    name = f["name"]; row = {"src": src, "name": name, "drive_id": f["id"], "bytes": int(f.get("size", 0))}
    try:
        if name == "desktop.ini": return
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json", dir=st["tmp"]); tmp.close(); row["md5"] = download(f["id"], tmp.name)
        if name.endswith(".zip"): row["status"] = "SKIP"; row["note"] = "zip, left in place"; os.unlink(tmp.name)
        else:
            d = json.load(open(tmp.name, encoding="utf-8")); os.unlink(tmp.name)
            if name.startswith("series_"): row["status"] = "SERIES"; os.makedirs(f"{OUT}/series", exist_ok=True); json.dump(d, gzip.open(f"{OUT}/series/{name[:150]}.gz", "wt", encoding="utf-8"), ensure_ascii=False); row["note"] = "series page kept"
            else:
                rec, status, note = compact(d); row["status"] = status; row["note"] = note; row["match_id"] = rec["match_id"]; row["coverage"] = rec.get("coverage")
                key = rec["match_id"]
                with LOCK:
                    seen = st["seen"].get(key)
                    if seen and seen != row["md5"]: row["status"] = "DUP_DIFF"; row["note"] = "same match id, different content: kept first, review"
                    elif seen: row["status"] = "DUP"
                    else: st["seen"][key] = row["md5"]
                if row["status"] in ("OK", "TEXT_ONLY", "MISMATCH"): json.dump(rec, gzip.open(f"{OUT}/{key}.json.gz", "wt", encoding="utf-8"), ensure_ascii=False)
        if move and row["status"] in ("OK", "TEXT_ONLY", "SERIES", "DUP"):
            call("PATCH", f"{D}/{f['id']}?supportsAllDrives=true&addParents={arch}&removeParents={st['parent'][src]}", "drive", body={}); row["moved"] = True
    except BaseException as e: row["status"] = "BAD"; row["note"] = str(e)[:200]
    with LOCK:
        open(MAN, "a").write(json.dumps(row, ensure_ascii=False) + "\n"); st["n"] += 1
        if st["n"] % 25 == 0: print(st["n"], "done", flush=True)
def main(a):
    fo = folders(); os.makedirs(OUT, exist_ok=True)
    if a[0] == "list":
        for k, v in fo.items(): fs = ls(v); print(k, len(fs), "files", round(sum(int(x.get("size", 0)) for x in fs) / 1e9, 1), "GB"); return
    lim = int(a[a.index("--limit") + 1]) if "--limit" in a else 10 ** 9; only = a[a.index("--only") + 1] if "--only" in a else None; move = "--move" in a; w = int(a[a.index("--workers") + 1]) if "--workers" in a else 4
    done = set(); seen = {}
    if os.path.exists(MAN):
        for l in open(MAN):
            r = json.loads(l)
            if r["status"] in ("OK", "TEXT_ONLY", "SERIES", "DUP", "SKIP") and (r.get("moved") or not move): done.add(r["drive_id"])
            if r.get("match_id") and r.get("md5") and r["status"] in ("OK", "TEXT_ONLY", "MISMATCH"): seen[r["match_id"]] = r["md5"]
    arch = None
    if move: ar = find(ROOTID, "Archive"); ce = find(ar, "Cricinfo extracts", True); arch = {k: find(ce, k, True) for k in fo}
    st = {"tmp": tempfile.mkdtemp(), "seen": seen, "n": 0, "parent": fo}; todo = []
    for k, v in fo.items():
        if only and k != only: continue
        todo += [(k, f) for f in ls(v) if f["id"] not in done and f["name"] != "desktop.ini"]
    todo = todo[:lim]; print("to do", len(todo), flush=True)
    with ThreadPoolExecutor(w) as ex:
        for k, f in todo: ex.submit(process, k, f, move, arch[k] if arch else None, st)
    print("ALL DONE", flush=True)
if __name__ == "__main__": main(sys.argv[1:] or ["list"])
