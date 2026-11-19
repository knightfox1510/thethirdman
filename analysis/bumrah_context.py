"""Bumrah in context (Cricsheet Tests since 2018 and our Sportmonks IPL cache): how his wickets differ from other fast bowlers, how he performs by innings and by pitch type, and his IPL phases vs the league.
python3 analysis/bumrah_context.py -> data/provenance/bumrah_context_figures.json"""
import json, glob, os, sys, collections
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, f"{R}/analysis")
from nz_tests import SPIN
BAD = ("run out", "retired hurt", "retired out", "obstructing the field"); B = "JJ Bumrah"
st = collections.defaultdict(lambda: collections.Counter()); inn = collections.defaultdict(lambda: [0, 0, 0]); rel = []
for f in sorted(glob.glob(f"{R}/data/cricsheet/tests/*.json")):
    d = json.load(open(f)); i = d["info"]
    if i["dates"][0] < "2018-01-01": continue
    mr = mw = 0; per = collections.defaultdict(lambda: [0, 0])
    for n, x in enumerate(d["innings"]):
        for ov in x["overs"]:
            for dl in ov["deliveries"]:
                ex = dl.get("extras", {}); cost = dl["runs"]["batter"] + ex.get("wides", 0) + ex.get("noballs", 0); mr += cost
                wk = [w for w in dl.get("wickets", []) if w["kind"] not in BAD]; mw += len(wk); per[dl["bowler"]][0] += cost; per[dl["bowler"]][1] += len(wk)
                b = dl["bowler"]
                if b in SPIN: continue
                st[b]["balls"] += "wides" not in ex and "noballs" not in ex; st[b]["runs"] += cost
                for w in wk: st[b]["wkts"] += 1; st[b][w["kind"]] += 1
                if b == B:
                    g = inn["1st/2nd" if n % 2 == 0 else "3rd/4th"]; g[0] += cost; g[1] += "wides" not in ex and "noballs" not in ex; g[2] += len(wk)
    if B in per and mw: rel.append((i["dates"][0], mr / mw, per[B][0] / max(1, per[B][1]) if per[B][1] else None, per[B]))
pace = {b: v for b, v in st.items() if v["wkts"] >= 50 and b != B}
tot = collections.Counter(); [tot.update(v) for v in pace.values()]
OUT = {"pace_bowlers_50plus_wkts_since_2018": len(pace), "baseline_bowled_lbw_pct": round(100 * (tot["bowled"] + tot["lbw"]) / tot["wkts"], 1), "baseline_avg": round(tot["runs"] / tot["wkts"], 1), "baseline_sr": round(tot["balls"] / tot["wkts"], 1)}
b = st[B]; OUT["bumrah_bowled_lbw_pct"] = round(100 * (b["bowled"] + b["lbw"]) / b["wkts"], 1); OUT["bumrah_wkts"] = b["wkts"]
OUT["innings"] = {k: {"wkts": v[2], "avg": round(v[0] / v[2], 1), "sr": round(v[1] / v[2], 1)} for k, v in inn.items()}
# relative to the match: Bumrah's average divided by the average of all bowlers in the match, bucketed by the match average (a proxy for pitch: low = bowler-friendly, high = flat)
buckets = collections.defaultdict(lambda: [0, 0, 0, 0, 0])
for date, mavg, _, (r, w) in rel:
    k = "bowler-friendly (match avg under 28)" if mavg < 28 else ("balanced (28-38)" if mavg < 38 else "flat (38+)")
    buckets[k][0] += r; buckets[k][1] += w; buckets[k][2] += 1; buckets[k][3] += mavg
OUT["by_pitch_type"] = {k: {"tests": v[2], "bumrah_avg": round(v[0] / max(1, v[1]), 1), "match_avg_all_bowlers": round(v[3] / v[2], 1), "bumrah_wkts": v[1]} for k, v in buckets.items()}
# IPL phases (our Sportmonks cache, 2013-2026, super overs excluded), against the league in the same seasons
sys.path.insert(0, f"{R}/analysis")
from common import ipl
df = ipl(); lg = df[df.legal_bowl == 1]; bm = lg[lg.bowler == "Jasprit Bumrah"]; ip = {}
for ph in ("powerplay", "middle", "death"):
    x = bm[bm.phase == ph]; seas = x.groupby("season").size(); y = lg[(lg.phase == ph) & lg.season.isin(seas.index)]
    lgs = y.groupby("season").apply(lambda s: 6 * s.runs.sum() / len(s)); wavg = float((lgs.reindex(seas.index) * seas).sum() / seas.sum())
    ip[ph] = {"balls": int(len(x)), "econ": round(6 * x.runs.sum() / len(x), 2), "league_econ_same_seasons_weighted": round(wavg, 2), "dot_pct": round(100 * x["dot"].mean(), 1)}
OUT["ipl_phases"] = ip; OUT["ipl_seasons"] = f'{int(bm.season.min())}-{int(bm.season.max())}'
for hand in ("Left", "Right"):
    x = bm[bm.bat_hand == f"{hand.lower()}-hand-bat"]; y = lg[lg.bat_hand == f"{hand.lower()}-hand-bat"]; OUT[f"ipl_vs_{hand.lower()}_handers"] = {"balls": int(len(x)), "econ": round(6 * x.runs.sum() / max(1, len(x)), 2), "league_econ": round(6 * y.runs.sum() / len(y), 2)}
json.dump(OUT, open(f"{R}/data/provenance/bumrah_context_figures.json", "w"), indent=1); print(json.dumps(OUT, indent=1))
