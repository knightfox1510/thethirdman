"""Vaibhav Suryavanshi: batting record to date in our data (Sportmonks IPL 2025-26 ball-by-ball; Cricsheet men's T20Is 2026). Splits by season, bowling type, phase, balls faced, opposition strength, and the bowlers who dismissed him.
Writes data/provenance/vaibhav_figures.json.   python3 analysis/vaibhav.py"""
import sys, json, glob, os, collections
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, f"{R}/analysis")
import common, pandas as pd
df = common.ipl(); NAME = "Vaibhav Suryavanshi"; v = df[df.batter == NAME].copy()
def agg(x):
    b = int(x.legal.sum()); r = int(x.bat_runs.sum()); w = int(((x.out_id == x.batter_id) | (x.out_id.isna() & (x.striker_out == 1)) & (x.wicket == 1)).sum()) if len(x) else 0
    return {"balls": b, "runs": r, "outs": int(x.wicket.sum()), "sr": round(100 * r / b, 1) if b else None, "avg": round(r / max(1, int(x.wicket.sum())), 1), "fours": int(x["four"].sum()), "sixes": int(x["six"].sum()), "dot_pct": round(100 * x["dot"].sum() / b, 1) if b else None, "bpb": round(b / max(1, int(x["four"].sum() + x["six"].sum())), 1)}
OUT = {"ipl": {}}
OUT["ipl"]["all"] = agg(v); OUT["ipl"]["inns"] = int(v.fixture.nunique())
for s in (2025, 2026): OUT["ipl"][str(s)] = {**agg(v[v.season == s]), "inns": int(v[v.season == s].fixture.nunique())}
OUT["ipl"]["by_kind"] = {k: agg(x) for k, x in v.groupby("bowl_kind") if x.legal.sum() >= 20}
v["pace"] = v.bowl_kind.astype(str).str.contains("pace|medium", case=False); OUT["ipl"]["pace_vs_spin"] = {("pace" if k else "spin"): agg(x) for k, x in v.groupby("pace")}
OUT["ipl"]["by_phase"] = {k: agg(x) for k, x in v.groupby("phase")}
# balls faced in the innings (1..): first 10, 11-25, 26+
v = v.sort_values(["date", "inning", "over", "ball"]); v["nb"] = v.groupby("fixture").legal.cumsum()
OUT["ipl"]["by_balls_faced"] = {nm: agg(v[(v.nb > a) & (v.nb <= b)]) for nm, a, b in (("balls 1-10", 0, 10), ("balls 11-25", 10, 25), ("balls 26+", 25, 999))}
ins = v.groupby("fixture").agg(date=("date", "first"), opp=("bowl_team", "first"), balls=("legal", "sum"), runs=("bat_runs", "sum"), fours=("four", "sum"), sixes=("six", "sum"), out=("wicket", "max")).sort_values("date")
ins["sr"] = (100 * ins.runs / ins.balls).round(1); OUT["ipl"]["innings"] = [{k: (str(x) if k == "date" else x) for k, x in r.items()} for r in ins.reset_index().to_dict("records")]
# opposition strength: wins per season from the fixtures (higher S1/S2 total wins); top four by wins = the playoff teams; the last four fixtures of a season are the playoffs
d2 = df[df.inning.isin(["S1", "S2"])]; tot = d2.groupby(["season", "fixture", "date", "inning", "bat_team"]).runs.sum().reset_index()
wins = collections.Counter(); fixt = []
for (s_, f, dt), g in tot.groupby(["season", "fixture", "date"]):
    g = g.sort_values("inning")
    if len(g) == 2:
        a_, b_ = g.iloc[0], g.iloc[1]; fixt.append((int(s_), f, dt))
        if a_.runs != b_.runs: wins[(int(s_), (a_ if a_.runs > b_.runs else b_).bat_team)] += 1
table = {s_: sorted(((t, n) for (ss, t), n in wins.items() if ss == s_), key=lambda x: -x[1]) for s_ in (2025, 2026)}
OUT["ipl"]["table"] = {str(s_): t for s_, t in table.items()}
top4 = {s_: {t for t, n in tab[:4]} for s_, tab in table.items()}
playoffs = {s_: {f for ss, f, dt in sorted([x for x in fixt if x[0] == s_], key=lambda x: str(x[2]))[-4:]} for s_ in (2025, 2026)}
v["big"] = v.apply(lambda r: r.bowl_team in top4[int(r.season)], axis=1); v["po"] = v.apply(lambda r: r.fixture in playoffs[int(r.season)], axis=1)
OUT["ipl"]["vs_top4"] = {"top4": agg(v[v.big]), "rest": agg(v[~v.big])}; OUT["ipl"]["playoffs"] = agg(v[v.po]); OUT["ipl"]["league"] = agg(v[~v.po])
OUT["ipl"]["by_opp"] = {k: agg(x) for k, x in v.groupby("bowl_team")}
ins["po"] = [bool(x) for x in v.groupby("fixture").po.first().reindex(ins.index)]; OUT["ipl"]["innings"] = [{k: (str(x) if k == "date" else x) for k, x in r.items()} for r in ins.reset_index().to_dict("records")]
# bowlers
bw = v.groupby("bowler").agg(balls=("legal", "sum"), runs=("bat_runs", "sum"), outs=("wicket", "sum"), kind=("bowl_kind", "first")); bw["sr"] = (100 * bw.runs / bw.balls).round(0)
OUT["ipl"]["bowlers"] = bw.reset_index().sort_values(["outs", "balls"], ascending=False).to_dict("records")
OUT["ipl"]["dismissals"] = v[v.wicket == 1][["date", "bowl_team", "bowler", "bowl_kind", "dismissal", "nb"]].astype(str).to_dict("records")
OUT["ipl"]["dismissal_types"] = dict(collections.Counter(v[v.wicket == 1].dismissal))
# Cricsheet T20Is
PID = "470f446b"; t = []
for f in sorted(glob.glob(f"{R}/data/cricsheet/t20s/*.json")):
    d = json.load(open(f)); i = d["info"]; ppl = i.get("registry", {}).get("people", {})
    if PID not in ppl.values(): continue
    nm = [k for k, x in ppl.items() if x == PID][0]; row = {"date": i["dates"][0], "event": (i.get("event") or {}).get("name"), "teams": i["teams"], "venue": i.get("venue"), "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "out": None, "bowler": None, "kind": None, "stage": i.get("event", {}).get("stage") if isinstance(i.get("event"), dict) else None, "dots": 0}
    for inn in d["innings"]:
        for ov in inn["overs"]:
            for dl in ov["deliveries"]:
                if dl["batter"] != nm: continue
                ex = dl.get("extras", {})
                if "wides" not in ex: row["balls"] += 1
                rr = dl["runs"]["batter"]; row["runs"] += rr; row["fours"] += rr == 4; row["sixes"] += rr == 6; row["dots"] += (rr == 0 and "wides" not in ex)
                for w in dl.get("wickets", []):
                    if w["player_out"] == nm: row["out"] = w["kind"]; row["bowler"] = dl["bowler"]
    t.append(row)
OUT["t20i"] = t
json.dump(OUT, open(f"{R}/data/provenance/vaibhav_figures.json", "w"), indent=1, ensure_ascii=False, default=str)
print(json.dumps({k: OUT["ipl"][k] for k in ("all", "2025", "2026", "pace_vs_spin", "by_phase", "by_balls_faced", "vs_top4", "dismissal_types")}, indent=1))
print(OUT["ipl"]["table"]); print(OUT["ipl"]["by_kind"]);
for r in t: print(r["date"], r["event"], r["teams"], r["runs"], r["balls"], r["out"], r["bowler"])
