"""Bumrah in Tests (Cricsheet men's Test archive, data/cricsheet/tests; debut Jan 2018): career line, home/away/SENA splits, how he gets wickets, India with and without him, availability gaps, workload.  python3 analysis/bumrah_tests.py -> data/provenance/bumrah_tests_figures.json"""
import json, glob, os, collections, datetime
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); D = f"{R}/data/cricsheet/tests"; B = "JJ Bumrah"
IND = {"Mumbai", "Chennai", "Kolkata", "Delhi", "Bangalore", "Bengaluru", "Ahmedabad", "Nagpur", "Mohali", "Chandigarh", "Kanpur", "Hyderabad", "Rajkot", "Visakhapatnam", "Pune", "Ranchi", "Indore", "Dharamsala", "Lucknow", "Guwahati", "Cuttack", "Mumbai (Brabourne)", "New Delhi", "Kolkata ", "Dharamshala"}
SENA = {"South Africa", "England", "New Zealand", "Australia"}
BAD = ("run out", "retired hurt", "retired out", "obstructing the field")
rows = []; kinds = collections.Counter(); lines = {"all": [0, 0, 0]}; by = collections.defaultdict(lambda: [0, 0, 0, 0]); fifers = []; spells = collections.Counter(); pos = collections.Counter(); inn_w = collections.Counter(); newb = [0, 0, 0]; oldb = [0, 0, 0]
matches = []
for f in sorted(glob.glob(f"{D}/*.json")):
    d = json.load(open(f)); i = d["info"]
    if "India" not in i["teams"]: continue
    date = i["dates"][0]
    if date < "2018-01-01": continue
    opp = [t for t in i["teams"] if t != "India"][0]; played = B in sum(i["players"].values(), [])
    home = i.get("city") in IND; ev = (i.get("event") or {}).get("name", "") if isinstance(i.get("event"), dict) else str(i.get("event", ""))
    neutral = "World Test Championship Final" in ev or i.get("city") in ("Southampton", "London") and "Final" in ev
    res = i.get("outcome", {}); won = res.get("winner") == "India"; lost = (res.get("winner") not in (None, "India"))
    matches.append({"date": date, "opp": opp, "home": home, "neutral": neutral, "played": played, "won": won, "lost": lost, "city": i.get("city")})
    if not played: continue
    r = bl = w = 0; mw = 0
    for n, inn in enumerate(d["innings"]):
        if inn["team"] == "India": continue
        order = []
        for ov in inn["overs"]:
            for dl in ov["deliveries"]:
                for x in (dl["batter"], dl["non_striker"]):
                    if x not in order: order.append(x)
        for ov in inn["overs"]:
            oi = ov["over"]
            for dl in ov["deliveries"]:
                if dl["bowler"] != B: continue
                ex = dl.get("extras", {}); cost = dl["runs"]["batter"] + ex.get("wides", 0) + ex.get("noballs", 0); legal = "wides" not in ex and "noballs" not in ex
                r += cost; bl += legal
                b_ = newb if oi < 20 else oldb; b_[0] += cost; b_[1] += legal
                for x in dl.get("wickets", []):
                    if x["kind"] in BAD: continue
                    w += 1; mw += 1; kinds[x["kind"]] += 1; b_[2] += 1; inn_w["1st/2nd innings" if n % 2 == 0 else "3rd/4th innings"] += 1
                    p = order.index(x["player_out"]) + 1 if x["player_out"] in order else 0; pos["top 4 (1-4)" if p <= 4 else ("middle (5-7)" if p <= 7 else "tail (8-11)")] += 1
                    spells["overs 1-20 (new ball)" if oi < 20 else "overs 21-80 (old ball)" if oi < 80 else "80+ (second new ball)"] += 1
    key = "home" if home else ("neutral" if neutral else ("SENA away" if opp in SENA else "other away"))
    by[key][0] += r; by[key][1] += bl; by[key][2] += w; by[key][3] += 1
    rows.append((date, opp, i.get("city"), key, r, bl, w))
    if w >= 5: fifers.append((date, opp, i.get("city"), w))
tot = [sum(x[4] for x in rows), sum(x[5] for x in rows), sum(x[6] for x in rows)]
OUT = {"tests": len(rows), "runs": tot[0], "balls": tot[1], "wkts": tot[2], "avg": round(tot[0] / tot[2], 2), "sr": round(tot[1] / tot[2], 1), "econ": round(tot[0] * 6 / tot[1], 2), "match_wkts_5plus": fifers, "dismissals": dict(kinds), "innings": dict(inn_w), "batting_position": dict(pos), "ball_age_wkts": dict(spells),
       "new_ball_overs1_20": {"runs": newb[0], "balls": newb[1], "wkts": newb[2], "avg": round(newb[0] / max(1, newb[2]), 1)}, "old_ball_overs21plus": {"runs": oldb[0], "balls": oldb[1], "wkts": oldb[2], "avg": round(oldb[0] / max(1, oldb[2]), 1)},
       "by_venue_type": {k: {"tests": v[3], "wkts": v[2], "avg": round(v[0] / max(1, v[2]), 1), "sr": round(v[1] / max(1, v[2]), 1), "econ": round(v[0] * 6 / max(1, v[1]), 2)} for k, v in by.items()}}
# India with and without him (all India Tests since his debut, decided matches)
def rec(sel):
    m = [x for x in matches if sel(x)]; return {"matches": len(m), "won": sum(x["won"] for x in m), "lost": sum(x["lost"] for x in m), "drawn": len(m) - sum(x["won"] for x in m) - sum(x["lost"] for x in m), "win_pct": round(100 * sum(x["won"] for x in m) / max(1, len(m)), 1)}
OUT["india_with"] = rec(lambda x: x["played"]); OUT["india_without"] = rec(lambda x: not x["played"])
OUT["india_with_away"] = rec(lambda x: x["played"] and not x["home"]); OUT["india_without_away"] = rec(lambda x: not x["played"] and not x["home"]); OUT["india_with_home"] = rec(lambda x: x["played"] and x["home"]); OUT["india_without_home"] = rec(lambda x: not x["played"] and x["home"])
OUT["share_of_his_tests_away"] = round(100 * sum(1 for x in rows if x[3] != "home") / len(rows), 1)
# availability gaps (days between consecutive India Tests that he missed in a row)
gaps = []; run = 0; start = None
for x in matches:
    if not x["played"]:
        run += 1; start = start or x["date"]
    else:
        if run >= 3: gaps.append((start, x["date"], run))
        run = 0; start = None
OUT["missed_runs_3plus"] = gaps
OUT["india_tests_since_debut"] = len(matches); OUT["played_of"] = (len(rows), len(matches)); rows.sort(); OUT["first_test"] = rows[0][:3]; OUT["last_test"] = rows[-1][:3]
json.dump(OUT, open(f"{R}/data/provenance/bumrah_tests_figures.json", "w"), indent=1, default=str)
print(json.dumps(OUT, indent=1, default=str))
