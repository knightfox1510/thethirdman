"""Ground and series history for NZ v IND, 2nd Test, Hagley Oval (Cricsheet men's Tests, our archive; coverage is partial before 2001-02, so 'in our archive').   python3 analysis/nz2_ground.py -> data/provenance/nz2_ground_figures.json"""
import json, glob, os, collections
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ms = []
for f in glob.glob(f"{R}/data/cricsheet/tests/*.json"):
    d = json.load(open(f)); i = d["info"]
    if i.get("gender") != "male": continue
    ms.append((f, d))
def inn_stats(inn):
    runs = wk = legal = 0; at85 = None; ov85 = (0, 0)
    for ov in inn["overs"]:
        for dl in ov["deliveries"]:
            e = dl.get("extras", {}); 
            if "wides" not in e and "noballs" not in e: legal += 1
            runs += dl["runs"]["total"]; wk += len(dl.get("wickets", []))
        if ov["over"] + 1 == 85: ov85 = (runs, wk)
    return dict(team=inn["team"], runs=runs, wkts=wk, overs=round(legal / 6, 1), at85=ov85 if legal >= 510 else None, rr=round(6 * runs / legal, 2) if legal else None)
def row(f, d):
    i = d["info"]; inns = [inn_stats(x) for x in d["innings"]]; o = i.get("outcome", {})
    return dict(date=i["dates"][0], venue=i["venue"], teams=i["teams"], toss=i["toss"], winner=o.get("winner"), by=o.get("by"), result=o.get("result"), inns=inns, dis=collections.Counter(w["kind"] for x in d["innings"] for ov in x["overs"] for dl in ov["deliveries"] for w in dl.get("wickets", [])))
hag = sorted([row(f, d) for f, d in ms if "Hagley" in d["info"]["venue"]], key=lambda r: r["date"])
OUT = {"hagley": [dict(date=r["date"], teams=r["teams"], toss=f'{r["toss"]["winner"]} {r["toss"]["decision"]}', winner=r["winner"], by=r["by"], result=r["result"], inns=[(x["team"], x["runs"], x["wkts"], x["overs"]) for x in r["inns"]]) for r in hag]}
first = [r["inns"][0] for r in hag if r["inns"]]
OUT["hagley_n"] = len(hag); OUT["hagley_first_inn_avg"] = round(sum(x["runs"] for x in first) / len(first), 1); OUT["hagley_first_inn_runs"] = [x["runs"] for x in first]
at85 = [x["at85"] for x in first if x["at85"]]; OUT["first_inn_after_85"] = at85; OUT["after85_avg"] = (round(sum(a[0] for a in at85) / len(at85), 1), round(sum(a[1] for a in at85) / len(at85), 2)) if at85 else None
OUT["toss"] = collections.Counter(f'{r["toss"]["decision"]}' for r in hag); OUT["toss_winner_won"] = sum(1 for r in hag if r["winner"] == r["toss"]["winner"]); OUT["bat_first_wins"] = sum(1 for r in hag if r["winner"] and r["winner"] == r["inns"][0]["team"]); OUT["draws"] = sum(1 for r in hag if r["result"] in ("draw",)); OUT["decided"] = sum(1 for r in hag if r["winner"])
tot = collections.Counter()
for r in hag: tot.update(r["dis"])
OUT["hagley_dismissals"] = dict(tot); allruns = sum(x["runs"] for r in hag for x in r["inns"]); allw = sum(x["wkts"] for r in hag for x in r["inns"]); allov = sum(x["overs"] for r in hag for x in r["inns"]); OUT["hagley_rpo"] = round(allruns / allov, 2); OUT["hagley_runs_per_wkt"] = round(allruns / max(1, allw), 1)
# overall NZ venues average for comparison
nz_names = ("Hagley", "Basin Reserve", "Seddon", "Eden Park", "Bay Oval", "University Oval", "McLean", "Westpac", "Carisbrook", "Lancaster", "AMI Stadium", "Jade Stadium", "Trust Bank", "Basin")
nz = [row(f, d) for f, d in ms if any(n in d["info"]["venue"] for n in nz_names) and d["info"]["dates"][0] >= "2001-06-01"]
OUT["nz_all"] = dict(n=len(nz), rpo=round(sum(x["runs"] for r in nz for x in r["inns"]) / sum(x["overs"] for r in nz for x in r["inns"]), 2), runs_per_wkt=round(sum(x["runs"] for r in nz for x in r["inns"]) / max(1, sum(x["wkts"] for r in nz for x in r["inns"])), 1))
ind = sorted([r for r in nz if set(r["teams"]) == {"India", "New Zealand"}], key=lambda r: r["date"])
OUT["india_in_nz"] = [dict(date=r["date"], venue=r["venue"], toss=f'{r["toss"]["winner"]} {r["toss"]["decision"]}', winner=r["winner"], by=r["by"], result=r["result"], inns=[(x["team"], x["runs"], x["wkts"]) for x in r["inns"]]) for r in ind]
OUT["india_nz_record"] = dict(n=len(ind), nz_wins=sum(r["winner"] == "New Zealand" for r in ind), india_wins=sum(r["winner"] == "India" for r in ind), draws=sum(1 for r in ind if not r["winner"]))
# player records at Hagley (batters; runs, dismissals)
bat = collections.defaultdict(lambda: [0, 0, 0, 0]); bowl = collections.defaultdict(lambda: [0, 0, 0])
for f, d in ms:
    if "Hagley" not in d["info"]["venue"]: continue
    for x in d["innings"]:
        seen = set()
        for ov in x["overs"]:
            for dl in ov["deliveries"]:
                b = dl["batter"]; bat[b][0] += dl["runs"]["batter"]; bat[b][2] += ("wides" not in dl.get("extras", {})); seen.add(b)
                bl = dl["bowler"]; e = dl.get("extras", {}); bowl[bl][0] += dl["runs"]["batter"] + e.get("wides", 0) + e.get("noballs", 0); bowl[bl][1] += ("wides" not in e and "noballs" not in e)
                for w in dl.get("wickets", []):
                    bat[w["player_out"]][1] += 1
                    if w["kind"] not in ("run out", "retired hurt", "retired out", "obstructing the field"): bowl[bl][2] += 1
        for b in seen: bat[b][3] += 1
names = ["TWM Latham", "DP Conway", "HM Nicholls", "TA Blundell", "DJ Mitchell", "GD Phillips", "R Ravindra", "JJ Bumrah", "Washington Sundar", "Akash Deep", "A Kamboj", "KL Rahul", "RR Pant", "RG Sharma", "V Kohli", "Mohammed Siraj", "MJ Henry", "KA Jamieson", "T Southee", "MJ Santner", "W Young", "KS Williamson"]
OUT["hagley_players"] = {n: dict(inns=bat[n][3], runs=bat[n][0], outs=bat[n][1], avg=round(bat[n][0] / bat[n][1], 1) if bat[n][1] else None, balls=bat[n][2]) for n in names if n in bat}
OUT["hagley_bowlers"] = {n: dict(balls=bowl[n][1], runs=bowl[n][0], wkts=bowl[n][2], avg=round(bowl[n][0] / bowl[n][2], 1) if bowl[n][2] else None, econ=round(6 * bowl[n][0] / bowl[n][1], 2)) for n in names if n in bowl and bowl[n][1] > 0}
json.dump(OUT, open(f"{R}/data/provenance/nz2_ground_figures.json", "w"), indent=1, default=str)
print(json.dumps({k: OUT[k] for k in ("hagley_n", "hagley_first_inn_avg", "hagley_first_inn_runs", "first_inn_after_85", "after85_avg", "toss", "toss_winner_won", "bat_first_wins", "draws", "decided", "hagley_dismissals", "hagley_rpo", "hagley_runs_per_wkt", "nz_all", "india_nz_record")}, default=str))
for r in OUT["hagley"]: print(r)
print(json.dumps(OUT["india_in_nz"], default=str)[:1800]); print(OUT["hagley_players"]); print(OUT["hagley_bowlers"])
