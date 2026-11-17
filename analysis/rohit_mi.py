"""Data pack for a possible 'Rohit Sharma returns as Mumbai Indians captain' video (IPL 2027).
Sources: Sportmonks ball-by-ball (data/ipl, IPL 2013-2026) and the Cricsheet IPL archive (every season 2008-2026, scratchpad csipl/x). Everything printed is 'in our archive'.
Captain seasons (Wikipedia 'List of Indian Premier League captains' + MI season pages): Rohit led MI from mid-2013 to 2023; Hardik Pandya 2024-2026. 2013 is a split season, so season comparisons use 2014-2023 (Rohit) and 2024-2026 (Hardik).
    python3 analysis/rohit_mi.py"""
import glob, json, os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from common import ipl
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "provenance", "rohit_mi_figures.json")
IPL_DIR = os.environ.get("IPL_DIR", "/tmp/claude-0/-home-user-thethirdman/0e6d8023-8d7b-5fe3-9abc-6751d93064e2/scratchpad/csipl/x")
ROHIT, MI = "Rohit Sharma", "Mumbai Indians"
df = ipl(); rs = df[df.batter == ROHIT]; F = {}
sr = lambda x: round(100 * x.bat_runs.sum() / max(1, (x.legal == 1).sum()), 1)
agg = lambda x: {"inn": int(x.groupby(["fixture", "inning"]).ngroups), "runs": int(x.bat_runs.sum()), "balls": int((x.legal == 1).sum()), "sr": sr(x), "fours": int(x.four.sum()), "sixes": int(x.six.sum())}
# --- 1. Rohit's batting by season (Sportmonks 2013-2026)
dis = df[(df.out_id == rs.batter_id.iloc[0]) | (df.out_id.isna() & (df.striker_out == 1) & (df.batter == ROHIT))]
seasons = {}
for y, g in rs.groupby("season"):
    inn = g.groupby(["fixture", "inning"]).bat_runs.sum(); lg = df[(df.season == y) & (df.phase == "powerplay")]
    seasons[int(y)] = {**agg(g), "fifties": int(((inn >= 50) & (inn < 100)).sum()), "hundreds": int((inn >= 100).sum()), "pp_sr": sr(g[g.phase == "powerplay"]), "league_pp_sr": sr(lg), "team": g.bat_team.iloc[0]}
F["rohit_by_season"] = seasons
def block(ys):
    g = rs[rs.season.isin(ys)]; inn = g.groupby(["fixture", "inning"]).bat_runs.sum(); a = agg(g); a["fifties_plus"] = int((inn >= 50).sum()); a["seasons"] = len(set(g.season)); a["runs_per_inn"] = round(a["runs"] / a["inn"], 1); return a
F["rohit_captain_seasons_2014_2023"] = block(range(2014, 2024)); F["rohit_non_captain_2024_2026"] = block(range(2024, 2027)); F["rohit_all_sportmonks_2013_2026"] = block(range(2013, 2027))
# --- 2. every IPL season from Cricsheet: Rohit's career (2008-2026) and MI's results
yr = lambda s: {"2007/08": 2008, "2009": 2009, "2009/10": 2010, "2020/21": 2020}.get(str(s), int(str(s)[:4]))
career = collections.defaultdict(lambda: {"runs": 0, "balls": 0, "fours": 0, "sixes": 0}); inns = collections.defaultdict(int); mi = collections.defaultdict(lambda: {"P": 0, "W": 0, "L": 0, "playoff": 0, "final": 0, "title": 0})
for f in glob.glob(IPL_DIR + "/*.json"):
    d = json.load(open(f)); i = d["info"]
    if i.get("match_type") != "T20" or "Indian Premier League" not in (i.get("event") or {}).get("name", ""): continue
    y = yr(i["season"]); w = (i.get("outcome") or {}).get("winner"); st = (i.get("event") or {}).get("stage")
    if MI in i["teams"]:
        r = mi[y]; r["P"] += 1; r["W"] += (w == MI); r["L"] += (bool(w) and w != MI)
        if st: r["playoff"] = 1
        if st == "Final": r["final"] = 1; r["title"] += (w == MI)
    for inn in d["innings"]:
        had = False
        for ov in inn["overs"]:
            for dl in ov["deliveries"]:
                if dl["batter"] == "RG Sharma":
                    had = True; c = career[y]; c["runs"] += dl["runs"]["batter"]; c["balls"] += ("wides" not in dl.get("extras", {})); c["fours"] += dl["runs"]["batter"] == 4 and not dl.get("extras", {}).get("noballs", 0) and True; c["sixes"] += dl["runs"]["batter"] == 6
        if had: inns[y] += 1
F["rohit_cricsheet_by_season"] = {int(y): {**c, "inn": inns[y]} for y, c in sorted(career.items())}
tot = {k: sum(c[k] for c in career.values()) for k in ("runs", "balls", "sixes")}; tot["inn"] = sum(inns.values()); tot["sr"] = round(100 * tot["runs"] / tot["balls"], 1); F["rohit_cricsheet_career_2008_2026"] = tot
F["mi_by_season"] = {int(y): v for y, v in sorted(mi.items())}
cap = lambda y: "Harbhajan/Tendulkar/Ponting (pre-Rohit)" if y <= 2012 else ("Ponting then Rohit" if y == 2013 else ("Rohit" if y <= 2023 else "Hardik"))
def dec(ys): W = sum(mi[y]["W"] for y in ys); L = sum(mi[y]["L"] for y in ys); return {"W": W, "L": L, "win_pct": round(100 * W / (W + L), 1), "playoffs": sum(mi[y]["playoff"] for y in ys), "seasons": len(list(ys)), "titles": sum(mi[y]["title"] for y in ys)}
F["mi_under_rohit_2014_2023"] = dec(range(2014, 2024)); F["mi_under_hardik_2024_2026"] = dec(range(2024, 2027)); F["mi_2013"] = dec([2013])
# --- print
print("== Rohit by season (Sportmonks): innings runs SR | PP SR vs league | 50s 100s")
for y, v in seasons.items(): print(f'  {y} {v["team"][:14]:14} {v["inn"]:>2} inn {v["runs"]:>4} runs SR {v["sr"]:>6} | PP {v["pp_sr"]:>6} vs {v["league_pp_sr"]:>6} | 50s {v["fifties"]} 100s {v["hundreds"]}')
for k in ("rohit_captain_seasons_2014_2023", "rohit_non_captain_2024_2026"): print(k, F[k])
print("Cricsheet career 2008-2026:", F["rohit_cricsheet_career_2008_2026"])
print("== MI by season (Cricsheet)")
for y, v in F["mi_by_season"].items(): print(f'  {y} {cap(y):38} W{v["W"]:>2} L{v["L"]:>2} playoff {v["playoff"]} final {v["final"]} title {v["title"]}')
print("MI 2014-23:", F["mi_under_rohit_2014_2023"], "| 2024-26:", F["mi_under_hardik_2024_2026"], "| 2013:", F["mi_2013"])
json.dump(F, open(OUT, "w"), indent=1, default=str); print("saved", OUT)
