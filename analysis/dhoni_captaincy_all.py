"""Figures for specs/dhoni_captaincy_all.json: MS Dhoni's IPL captaincy against the WHOLE IPL (2008-2025 seasons; 2026 shown only where stated).
Source: Cricsheet ball-by-ball IPL archive (ipl_json, every match file, men's T20, event stage = playoff stage), downloaded from cricsheet.org/downloads/ipl_json.zip into IPL_DIR.
Known gaps (checked against Wikipedia's season tables): Cricsheet has 58 of 59 matches in 2008, 57 of 59 in 2009 and misses a few abandoned matches in 2010 and 2012, so wins and playoff results are complete
but a team's 'matches played' can be one or two short in those seasons. We therefore compare teams on WINS and on decided matches (wins + losses) and say 'in our archive'.
    IPL_DIR=<dir with the .json files> python3 analysis/dhoni_captaincy_all.py"""
import glob, json, os, collections
IPL_DIR = os.environ.get("IPL_DIR", "/tmp/claude-0/-home-user-thethirdman/0e6d8023-8d7b-5fe3-9abc-6751d93064e2/scratchpad/csipl/x")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "provenance", "dhoni_captaincy_all_figures.json")
CANON = {"Delhi Daredevils": "Delhi Capitals", "Kings XI Punjab": "Punjab Kings", "Royal Challengers Bangalore": "Royal Challengers Bengaluru", "Rising Pune Supergiants": "Rising Pune Supergiant"}
yr = lambda s: {"2007/08": 2008, "2009": 2009, "2009/10": 2010, "2020/21": 2020}.get(str(s), int(str(s)[:4]))
T = collections.defaultdict(lambda: collections.defaultdict(lambda: {"P": 0, "W": 0, "L": 0, "NR": 0, "playoff": 0, "final": 0, "champ": 0}))
matches = collections.Counter()
for f in glob.glob(IPL_DIR + "/*.json"):
    d = json.load(open(f)); i = d["info"]
    if i.get("match_type") != "T20" or "Indian Premier League" not in (i.get("event") or {}).get("name", ""): continue
    y = yr(i["season"]); matches[y] += 1; w = (i.get("outcome") or {}).get("winner"); st = (i.get("event") or {}).get("stage")
    for tm in i["teams"]:
        t = CANON.get(tm, tm); r = T[t][y]; r["P"] += 1
        if "super_over" in (i.get("outcome") or {}).get("by", {}) or (i.get("outcome") or {}).get("result") == "tie": pass
        if w == tm: r["W"] += 1
        elif w: r["L"] += 1
        else: r["NR"] += 1
        if st: r["playoff"] = 1
        if st == "Final": r["final"] = 1; r["champ"] += (w == tm)
F = {"matches_per_season": dict(sorted(matches.items()))}
rows = {}
for t, ys in T.items():
    seasons = sorted(ys); W = sum(ys[y]["W"] for y in ys if y <= 2025); L = sum(ys[y]["L"] for y in ys if y <= 2025)
    rows[t] = {"seasons": [y for y in seasons if y <= 2025], "n_seasons": len([y for y in seasons if y <= 2025]), "W": W, "L": L, "decided": W + L, "win_pct": round(100 * W / max(1, W + L), 1),
               "playoff_seasons": sum(ys[y]["playoff"] for y in ys if y <= 2025), "finals": sum(ys[y]["final"] for y in ys if y <= 2025), "titles": sum(ys[y]["champ"] for y in ys if y <= 2025)}
F["franchises"] = rows
F["csk_by_season"] = {y: {k: T["Chennai Super Kings"][y][k] for k in ("P", "W", "L", "NR", "playoff", "final", "champ")} for y in sorted(T["Chennai Super Kings"])}
F["rps_2016"] = T["Rising Pune Supergiant"][2016]
print("matches per season (Cricsheet):", F["matches_per_season"])
print(f'{"franchise":30}{"seasons":>8}{"W":>5}{"dec":>5}{"win%":>7}{"playoffs":>9}{"finals":>7}{"titles":>7}')
for t, r in sorted(rows.items(), key=lambda kv: -kv[1]["win_pct"]):
    if r["decided"] >= 100: print(f'{t:30}{r["n_seasons"]:>8}{r["W"]:>5}{r["decided"]:>5}{r["win_pct"]:>7}{r["playoff_seasons"]:>9}{r["finals"]:>7}{r["titles"]:>7}')
print("CSK by season:", {y: (v["W"], v["P"]) for y, v in F["csk_by_season"].items()}); print("RPS 2016:", F["rps_2016"])
json.dump(F, open(OUT, "w"), indent=1, default=str); print("saved", OUT)
