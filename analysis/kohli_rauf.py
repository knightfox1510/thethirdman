"""Kohli v Pakistan, MCG, T20 World Cup, 23 Oct 2022 (Cricsheet match 1298150): the chase over by over, the 19th over, Kohli's innings, the last over; plus archive rates from our verified ball-by-ball.
Archive = data/cricinfo_compact (men's T20 records with line and length, mostly IPL) and Cricsheet men's T20 chases.   python3 analysis/kohli_rauf.py  -> data/provenance/kohli_rauf_figures.json"""
import json, glob, gzip, os, collections
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(f"{R}/data/cricsheet/t20s/1298150.json")); i = d["info"]; assert i["teams"] == ["Pakistan", "India"] and i["dates"] == ["2022-10-23"] and i["gender"] == "male"
pak, ind = d["innings"]; tot = lambda inn: sum(x["runs"]["total"] for o in inn["overs"] for x in o["deliveries"]); assert (tot(pak), tot(ind)) == (159, 160)
cum = 0; w = 0; after = {}; kr = kb = 0; k4 = k6 = 0; sixes_at = []; legal = 0
for ov in ind["overs"]:
    for dl in ov["deliveries"]:
        e = dl.get("extras", {}); isw = "wides" in e; isn = "noballs" in e
        if not isw and not isn: legal += 1
        cum += dl["runs"]["total"]; w += len(dl.get("wickets", []))
        if dl["batter"] == "V Kohli":
            if not isw: kb += 1
            kr += dl["runs"]["batter"]; k4 += dl["runs"]["batter"] == 4; k6 += dl["runs"]["batter"] == 6
            if dl["runs"]["batter"] == 6: sixes_at.append((ov["over"] + 1, legal))
    after[ov["over"] + 1] = dict(score=cum, wkts=w, kohli=kr, kohli_balls=kb)
assert (kr, kb, k4, k6) == (82, 53, 6, 4)
r19 = [x["runs"]["total"] for x in ind["overs"][18]["deliveries"]]; assert r19 == [1, 1, 0, 1, 6, 6]
need_before_sixes = 160 - after[18]["score"] - sum(r19[:4]); assert need_before_sixes == 28
rauf = [[x["runs"]["total"] for x in o["deliveries"] if x["bowler"] == "Haris Rauf"] for o in ind["overs"]]; rauf_ov = {k + 1: sum(v) for k, v in enumerate(rauf) if v}; assert rauf_ov == {4: 7, 6: 9, 16: 6, 19: 15}
last = [(x["batter"], x["runs"]["batter"], x["runs"]["total"], x.get("extras"), [q["kind"] for q in x.get("wickets", [])]) for x in ind["overs"][19]["deliveries"]]
assert last[3][3] == {"noballs": 1} and last[3][1] == 6 and last[4][3] == {"wides": 1} and last[5][3] == {"byes": 3} and last[6][4] == ["stumped"] and last[7][3] == {"wides": 1} and last[8][1] == 1
last_legal = sum(1 for o in ind["overs"][18:] for x in o["deliveries"] if "wides" not in x.get("extras", {}) and "noballs" not in x.get("extras", {})) ; assert last_legal == 12      # the win came off the last legal ball
six_last8 = sum(1 for o, lg in sixes_at if lg >= 112); assert six_last8 == 3, sixes_at
# archive: Cricinfo-captured men's T20 with line and length (legal balls, innings 1-2)
rows = []
for f in glob.glob(f"{R}/data/cricinfo_compact/[0-9]*.json.gz"):
    r = json.load(gzip.open(f, "rt"))
    if r.get("layout") != "json" or not r["balls"] or not (r.get("format") or "").upper().startswith("T20") or r["coverage"]["line"] < 50: continue
    rows += [b for b in r["balls"] if b[0] in (1, 2) and b[17] and b[18] and not b[7]]
STR = (4, 5)                                                       # the two wagon zones either side of straight (straight drives land in zones 4 and 5)
bl = [b for b in rows if b[18] == "SHORT_OF_A_GOOD_LENGTH" and b[17] == "ON_THE_STUMPS" and b[1] >= 17]; six = [b for b in bl if b[5] == 6]; strs = [b for b in six if b[16] in STR]
arch = {"balls": len(bl), "sixes": len(six), "straight_sixes": len(strs), "p_six": round(len(six) / len(bl), 4), "p_straight": round(len(strs) / len(bl), 4), "matches_used": None}
# chases needing 25-31 off 8 balls with at most 5 down (Cricsheet men's T20 chases, 20-over)
n = wn = 0
for f in glob.glob(f"{R}/data/cricsheet/t20s/*.json"):
    x = json.load(open(f)); ii = x["info"]
    if ii.get("gender") != "male" or len(x["innings"]) < 2 or ii.get("overs", 20) != 20: continue
    inn = x["innings"][1]; tg = inn.get("target", {}).get("runs"); win = ii.get("outcome", {}).get("winner")
    if not tg or not win: continue
    c = lg = wk = 0; hit = False
    for ov in inn["overs"]:
        for dl in ov["deliveries"]:
            e = dl.get("extras", {}); lg += ("wides" not in e and "noballs" not in e); c += dl["runs"]["total"]; wk += len(dl.get("wickets", []))
            if not hit and lg == 112 and ov["over"] + 1 >= 19 and 25 <= tg - c <= 31 and wk <= 5: n += 1; wn += win == inn["team"]; hit = True
out = {"match": {"pak": 159, "ind": 160, "kohli": [kr, kb, k4, k6]}, "after_over": after, "over19": r19, "need_before_sixes": need_before_sixes, "rauf_by_over": rauf_ov, "rauf_first3": 22, "last_over": [str(z) for z in last], "sixes_in_last8": six_last8, "archive": arch, "chase_28_8": {"situations": n, "wins": wn}}
assert 20 <= n <= 40 and wn / n < .2 and 1000 < arch["balls"] < 3000 and .07 < arch["p_six"] < .10 and .015 < arch["p_straight"] < .025
os.makedirs(f"{R}/data/provenance", exist_ok=True); json.dump(out, open(f"{R}/data/provenance/kohli_rauf_figures.json", "w"), indent=1); print(json.dumps({k: out[k] for k in ("archive", "chase_28_8", "rauf_by_over", "sixes_in_last8")}))
