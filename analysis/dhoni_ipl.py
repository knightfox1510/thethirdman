"""Figures for the Dhoni package (specs dhoni_retires, dhoni_ipl_story, dhoni_captain_myth): Mahendra Singh Dhoni in the IPL, seasons 2013-2025 in our Sportmonks archive.
Everything printed here is "in our archive" (2008-2012 are not in the plan); career totals (278 matches, 5,439 runs ...) and captaincy come from news / Cricinfo records, not from here.
    python3 analysis/dhoni_ipl.py            (needs data/ipl: SM_KEY=... python3 fetch_ipl.py)"""
import json, os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ipl, show, section

NAME = "Mahendra Singh Dhoni"
CSK = "Chennai Super Kings"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "provenance", "dhoni_ipl_figures.json")
df = ipl()
df = df[df.season <= 2025]                       # he did not play in 2026
d = df[df.batter == NAME]
faced = d[d.legal == 1] if "legal" in d else d
F = {}


def sr(x): return 100 * x.bat_runs.sum() / max(1, (x.legal == 1).sum())


def agg(x):
    return {"runs": int(x.bat_runs.sum()), "balls": int((x.legal == 1).sum()), "sr": round(sr(x), 1), "fours": int(x.four.sum()), "sixes": int(x.six.sum())}


section("Archive career 2013-2025 (batting)")
F["archive_total"] = agg(d); F["innings"] = int(d.groupby(["fixture", "inning"]).ngroups)
dis = df[(df.out_id == d.batter_id.iloc[0]) | ((df.out_id.isna()) & (df.striker_out == 1) & (df.batter == NAME))]
F["dismissals"] = int(dis.wicket.sum()); F["not_outs"] = F["innings"] - F["dismissals"]
show("archive runs / balls / SR / 4s / 6s", str(F["archive_total"])); show("innings / dismissals / not outs", f'{F["innings"]} / {F["dismissals"]} / {F["not_outs"]}')

section("By phase vs everyone else (same seasons)")
league = df[df.season.isin(sorted(d.season.unique()))]
for ph in ("powerplay", "middle", "death"):
    a = d[d.phase == ph]; l = league[(league.phase == ph)]
    F[f"phase_{ph}"] = {"dhoni": agg(a), "league_sr": round(sr(l), 1)}
    show(f"{ph}: Dhoni vs league SR", f'{sr(a):.1f} vs {sr(l):.1f} ({int((a.legal == 1).sum())} balls)')

section("Overs 19-20 (the last two overs)")
l2 = league[league.over.isin([18, 19])]; d2 = d[d.over.isin([18, 19])]      # over is 0-indexed: 18 and 19 are the 19th and 20th overs
F["last2"] = {"dhoni": agg(d2), "league_sr": round(sr(l2), 1)}; show("overs 19-20 Dhoni vs league SR / sixes", f'{sr(d2):.1f} vs {sr(l2):.1f} / {int(d2.six.sum())} sixes')
l1 = league[league.over == 19]; d1 = d[d.over == 19]
F["over20"] = {"dhoni": agg(d1), "league_sr": round(sr(l1), 1)}; show("20th over Dhoni vs league SR", f'{sr(d1):.1f} vs {sr(l1):.1f} ({int((d1.legal == 1).sum())} balls)')

section("Chasing vs setting (inning S2 = chase)")
for lab, inn in (("chasing", "S2"), ("batting first", "S1")):
    a = d[d.inning == inn]; F[f"{lab}"] = agg(a); show(f"{lab}", str(agg(a)))
cd = d[(d.inning == "S2") & (d.phase == "death")]; cl = league[(league.inning == "S2") & (league.phase == "death")]
F["chase_death"] = {"dhoni": agg(cd), "league_sr": round(sr(cl), 1)}; show("chasing at the death: Dhoni vs league SR", f'{sr(cd):.1f} vs {sr(cl):.1f} ({int((cd.legal == 1).sum())} balls)')

section("Season by season (strike rate in overs 16-20; balls)")
seas = []
for yr, g in d.groupby("season"):
    gd = g[g.phase == "death"]; lg = league[(league.season == yr) & (league.phase == "death")]
    seas.append({"season": int(yr), "runs": int(g.bat_runs.sum()), "balls": int((g.legal == 1).sum()), "sr": round(sr(g), 1), "death_sr": round(sr(gd), 1), "death_balls": int((gd.legal == 1).sum()), "league_death_sr": round(sr(lg), 1), "sixes": int(g.six.sum())})
    show(str(yr), f'{seas[-1]["runs"]} runs, SR {seas[-1]["sr"]}, death SR {seas[-1]["death_sr"]} vs league {seas[-1]["league_death_sr"]} ({seas[-1]["death_balls"]} balls), sixes {seas[-1]["sixes"]}')
F["seasons"] = seas

section("Best ball-for-ball stretches: sixes in 19-20 by season / last-over finishes")
F["sixes_19_20_by_season"] = {int(k): int(v) for k, v in d2.groupby("season").six.sum().items()}
show("sixes in overs 19-20 by season", str(F["sixes_19_20_by_season"]))

section("CSK and the league: results of every decided match (winner by team id), seasons Dhoni captained")
import glob, re
from collections import Counter
raw = {}
for fp in glob.glob(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "ipl", "fx_*.json")):
    r = json.load(open(fp)); raw[r["id"]] = r
D_SEASONS = [2013, 2014, 2015, 2018, 2019, 2020, 2021, 2023]      # CSK played, Dhoni captain (CSK was suspended 2016-17; 2022, 2024, 2025 had other captains for part or all of the season)
rows = []
for fx, r in raw.items():
    if fx not in set(df.fixture) or not r.get("winner_team_id"): continue
    m = re.match(r"(.+?) won by (\d+) (runs?|wickets?)", r.get("note") or "")
    if not m: continue
    names = {r["localteam_id"]: r["localteam"]["name"], r["visitorteam_id"]: r["visitorteam"]["name"]}
    season = int(df[df.fixture == fx].season.iloc[0])
    rows.append(dict(season=season, teams=list(names.values()), winner=names[r["winner_team_id"]], margin=int(m[2]), kind=m[3][:3]))
def tight(x): return (x["kind"] == "run" and x["margin"] <= 10) or (x["kind"] == "wic" and x["margin"] <= 2)
def canon(n): return {"Delhi Daredevils": "Delhi Capitals", "Kings XI Punjab": "Punjab Kings", "Royal Challengers Bangalore": "Royal Challengers Bengaluru"}.get(n, n)
W, P = Counter(), Counter()
for x in rows:
    if x["season"] in D_SEASONS:
        for t in x["teams"]: P[canon(t)] += 1
        W[canon(x["winner"])] += 1
rank = sorted(P, key=lambda t: -W[t] / P[t]); F["league_rank_dhoni_seasons"] = [{"team": t, "won": W[t], "played": P[t], "pct": round(100 * W[t] / P[t], 1)} for t in rank]
for e in F["league_rank_dhoni_seasons"]: show(e["team"], f'{e["won"]}/{e["played"]} = {e["pct"]}%')
csk = [x for x in rows if CSK in x["teams"] and x["season"] in D_SEASONS]; t = [x for x in csk if tight(x)]; n = [x for x in csk if not tight(x)]
F["csk_dhoni_seasons"] = {"decided": len(csk), "won": sum(x["winner"] == CSK for x in csk), "tight": len(t), "tight_won": sum(x["winner"] == CSK for x in t), "rest": len(n), "rest_won": sum(x["winner"] == CSK for x in n), "seasons": D_SEASONS}
c = F["csk_dhoni_seasons"]; show("CSK decided matches / won", f'{c["decided"]} / {c["won"]} = {100 * c["won"] / c["decided"]:.1f}%')
show("tight finishes (<=10 runs or <=2 wickets) / won", f'{c["tight"]} / {c["tight_won"]} = {100 * c["tight_won"] / c["tight"]:.1f}%'); show("all other matches / won", f'{c["rest"]} / {c["rest_won"]} = {100 * c["rest_won"] / c["rest"]:.1f}%')
json.dump(F, open(OUT, "w"), indent=1, default=str)
print("\nsaved", OUT)

section("Volume records in our archive (no minimum-balls cut-off): who scored most in the final two overs and in overs 16-20")
x2 = df[df.over.isin([18, 19])].groupby("batter").agg(runs=("bat_runs", "sum"), sixes=("six", "sum"), balls=("legal", lambda s: int((s == 1).sum())))
xd = df[df.phase == "death"].groupby("batter").agg(runs=("bat_runs", "sum"), sixes=("six", "sum"), balls=("legal", lambda s: int((s == 1).sum())))
def top(t, col): s_ = t[col].sort_values(ascending=False); return {"first": s_.index[0], "first_val": int(s_.iloc[0]), "second": s_.index[1], "second_val": int(s_.iloc[1])}
F["last2_most_runs"] = top(x2, "runs"); F["last2_most_sixes"] = top(x2, "sixes"); F["death_most_runs"] = top(xd, "runs"); F["death_most_balls"] = top(xd, "balls")
for k in ("last2_most_runs", "last2_most_sixes", "death_most_runs", "death_most_balls"): show(k, str(F[k]))
json.dump(F, open(OUT, "w"), indent=1, default=str)
