"""NZ v IND, 2nd Test, Hagley Oval, Christchurch, Day 1 (27 Nov 2026): the owner's Cricinfo capture (match 1539443): 517 deliveries with line, length, shot, control and wagon zone, plus the day's commentary text (speeds, chances, reviews).
Ground and series history from Cricsheet men's Tests (partial before 2001-02; NEVER used for 'first/only/never').   python3 analysis/nz2_day1.py  -> data/provenance/nz2_day1_figures.json  and  data/cricinfo/nz2_day1_balls.csv"""
import json, re, os, glob, collections, sys
import numpy as np, pandas as pd
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(f"{R}/data/cricinfo/nz_ind_2nd_test_day1.json")); C = d["comments"]
sc = d["pages"]["full-scorecard"]["props"]["appPageProps"]["data"]; content = sc["content"]; inn = content["innings"][0]
PL = {}
for b in inn["inningBatsmen"] + inn["inningBowlers"]: PL[b["player"]["id"]] = b["player"]["name"]
for tp in content["matchPlayers"]["teamPlayers"]:
    for p in tp["players"]:
        pp = p.get("player", p); PL.setdefault(pp["id"], pp.get("name"))
NZP = {p["player"]["id"] for tp in content["matchPlayers"]["teamPlayers"] if tp["team"]["name"] == "New Zealand" for p in tp["players"]}
# commentary text
t = d["pages"]["ball-by-ball-commentary_text"]; L = t.split("\n"); txt = {}
for i, l in enumerate(L):
    s = l.strip()
    if re.fullmatch(r"\d+\.\d", s) and i + 3 < len(L) and " TO " in L[i + 2]:
        txt[float(s)] = (L[i + 2].strip(), " ".join(x.strip() for x in L[i + 4:i + 6] if x.strip()))
rows = []
for x in C:
    h, tx = txt.get(round(x["oversActual"], 1), ("", ""))
    sp = re.search(r"(\d{2,3})\s?kph", tx)
    rows.append(dict(over=round(x["oversActual"], 1), ov=x["overNumber"], ball=x["ballNumber"], bowler=PL.get(x["bowlerPlayerId"]), bat=PL.get(x["batsmanPlayerId"]), runs=x["totalRuns"], bat_runs=x["batsmanRuns"], four=int(x["isFour"]), six=int(x["isSix"]), wkt=int(x["isWicket"]), dis=x["dismissalType"],
                     wide=x["wides"], nb=x["noballs"], bye=x["byes"] + x["legbyes"], line=x["pitchLine"], length=x["pitchLength"], shot=x["shotType"], ctl=x["shotControl"], zone=x["wagonZone"], wx=x["wagonX"], wy=x["wagonY"], kph=int(sp.group(1)) if sp else None, text=tx, head=h, score=x["totalInningRuns"], wk_total=x["totalInningWickets"]))
df = pd.DataFrame(rows).sort_values(["ov", "ball"]).reset_index(drop=True); df["legal"] = ((df.wide == 0) & (df.nb == 0)).astype(int)
assert len(df) == 517 and df.legal.sum() == 510 and df.runs.sum() == 246 and df.wkt.sum() == 5, (len(df), df.legal.sum(), df.runs.sum(), df.wkt.sum())
df.to_csv(f"{R}/data/cricinfo/nz2_day1_balls.csv", index=False)
df["sess"] = np.where(df.ov <= 26, 1, np.where(df.ov <= 50, 2, 3))
OUT = {}
def agg(x):
    leg = x[x.legal == 1]; n = len(leg); sh = x[x.shot.notna()]
    return dict(balls=int(n), runs=int(x.runs.sum()), wkts=int(x.wkt.sum()), rr=round(6 * x.runs.sum() / n, 2) if n else None, dot_pct=round(100 * (leg.runs == 0).mean(), 1) if n else None, fours=int(x.four.sum()),
                ctl2_pct=round(100 * (leg.ctl == 2).mean(), 1) if n else None, left_pct=round(100 * (leg.shot == "LEFT_ALONE").mean(), 1) if n else None)
OUT["day"] = agg(df); OUT["sessions"] = {f"S{k}": agg(df[df.sess == k]) for k in (1, 2, 3)}
# first 10, overs 41-44 collapse, last 15
OUT["first10"] = agg(df[df.ov <= 10]); OUT["overs11_40"] = agg(df[(df.ov > 10) & (df.ov <= 40)]); OUT["collapse_41_44"] = agg(df[(df.ov >= 41) & (df.ov <= 44)]); OUT["overs45_70"] = agg(df[(df.ov >= 45) & (df.ov <= 70)]); OUT["last15"] = agg(df[df.ov >= 71]); OUT["new_ball_81_85"] = agg(df[df.ov >= 81]); OUT["old_ball"] = agg(df[df.ov <= 80])
# bowlers
bw = {}
for b, x in df.groupby("bowler"):
    x = x.assign(conc=x.runs - x.bye); leg = x[x.legal == 1]; a = agg(x); a["runs"] = int(x.conc.sum()); a["rr"] = round(6 * a["runs"] / len(leg), 2); a["dot_pct"] = round(100 * (leg.conc == 0).mean(), 1); a["overs"] = round(len(leg) / 6, 1)
    a["maidens"] = int(sum(1 for _, o in x.groupby("ov") if o.legal.sum() == 6 and o.conc.sum() == 0))        # bowler runs exclude byes and leg byes
    lc = leg.length.value_counts(normalize=True) * 100; a["len_pct"] = {k: round(v, 1) for k, v in lc.items()}; ln = leg.line.value_counts(normalize=True) * 100; a["line_pct"] = {k: round(v, 1) for k, v in ln.items()}
    a["kph_avg"] = round(float(leg.kph.mean()), 1) if leg.kph.notna().sum() >= 8 else None; a["kph_n"] = int(leg.kph.notna().sum()); a["kph_max"] = int(leg.kph.max()) if leg.kph.notna().any() else None
    a["full_or_good_pct"] = round(float(lc.get("FULL", 0) + lc.get("GOOD_LENGTH", 0) + lc.get("YORKER", 0)), 1); a["short_pct"] = round(float(lc.get("SHORT_OF_A_GOOD_LENGTH", 0) + lc.get("SHORT", 0)), 1)
    bw[b] = a
OUT["bowlers"] = bw
# batters
bt = {}
for b, x in df.groupby("bat"):
    leg = x[x.legal == 1]; a = agg(x); a["runs"] = int(x.bat_runs.sum()); a["sr"] = round(100 * a["runs"] / len(leg), 1); sh = leg.shot.value_counts(); a["shots"] = {k: int(v) for k, v in sh.head(8).items()}
    played = leg[~leg.shot.isin(["LEFT_ALONE", "DEFENDED"])]; a["attacking_pct"] = round(100 * len(played) / len(leg), 1); a["runs_per_attacking"] = round(played.bat_runs.sum() / max(1, len(played)), 2)
    a["by_len"] = {k: dict(balls=int(len(v)), runs=int(v.bat_runs.sum()), ctl2=int((v.ctl == 2).sum())) for k, v in leg.groupby("length")}
    a["zones"] = {int(k): int(v) for k, v in x[x.bat_runs > 0].groupby("zone").bat_runs.sum().items() if k}
    bt[b] = a
OUT["batters"] = bt
# line x length grid, runs per ball, control
g = {}
for ln_, x in df[df.legal == 1].groupby("line"):
    for le, y in x.groupby("length"): g[f"{ln_}|{le}"] = dict(balls=int(len(y)), runs=int(y.runs.sum()), ctl2=int((y.ctl == 2).sum()), wkts=int(y.wkt.sum()))
OUT["grid"] = g
leg = df[df.legal == 1]; OUT["length_mix"] = {k: round(100 * v, 1) for k, v in leg.length.value_counts(normalize=True).items()}; OUT["line_mix"] = {k: round(100 * v, 1) for k, v in leg.line.value_counts(normalize=True).items()}
OUT["by_length"] = {k: dict(balls=int(len(v)), runs=int(v.runs.sum()), rr=round(6 * v.runs.sum() / len(v), 2), ctl2_pct=round(100 * (v.ctl == 2).mean(), 1), wkts=int(v.wkt.sum()), dot_pct=round(100 * (v.runs == 0).mean(), 1)) for k, v in leg.groupby("length")}
OUT["by_line"] = {k: dict(balls=int(len(v)), runs=int(v.runs.sum()), rr=round(6 * v.runs.sum() / len(v), 2), ctl2_pct=round(100 * (v.ctl == 2).mean(), 1), wkts=int(v.wkt.sum())) for k, v in leg.groupby("line")}
OUT["shots_all"] = {k: dict(n=int(len(v)), runs=int(v.bat_runs.sum()), ctl2=int((v.ctl == 2).sum())) for k, v in leg.groupby("shot")}
# the wickets, the fours
W = df[df.wkt == 1][["over", "bowler", "bat", "dis", "line", "length", "shot", "ctl", "score", "text"]]; OUT["wickets"] = W.to_dict("records")
OUT["fours"] = df[df.four == 1][["over", "bowler", "bat", "line", "length", "shot", "zone"]].to_dict("records")
# over by over
ov = df.groupby("ov").agg(runs=("runs", "sum"), wkts=("wkt", "sum")); OUT["maidens_total"] = int(((ov.runs == 0)).sum()); OUT["best_over"] = ov.runs.idxmax(); OUT["best_over_runs"] = int(ov.runs.max())
# chances: text keywords
kw = re.compile(r"dropped|drops|drop it|edge|nick|beaten|play and (a )?miss|appeal|lbw|review|just short|fell short|falls short|airs|through the gap|misses|mis-?hit|false shot|inside edge|outside edge", re.I)
ch = df[(df.ctl == 2) | df.text.str.contains(kw)][["over", "bowler", "bat", "line", "length", "shot", "ctl", "text"]]; OUT["n_ctl2"] = int((leg.ctl == 2).sum()); OUT["chance_rows"] = ch.to_dict("records")
OUT["fow"] = [(f["fowWicketNum"], f["dismissalBatsman"]["name"], f["fowRuns"], f["fowOvers"]) for f in inn["inningFallOfWickets"]]
json.dump(OUT, open(f"{R}/data/provenance/nz2_day1_figures.json", "w"), indent=1, default=str)
print(json.dumps({k: OUT[k] for k in ("day", "sessions", "first10", "collapse_41_44", "last15", "new_ball_81_85", "length_mix", "line_mix", "by_length", "by_line", "n_ctl2")}, indent=0, default=str)[:3500])
