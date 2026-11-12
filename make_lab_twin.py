"""Builds specs/lab_ep1_abhishek_twin.json from analysis/lab_twin.py (every number comes from the table)."""
import json, sys, numpy as np, pandas as pd
sys.path.insert(0, "analysis")
import lab_twin as L

t = L.table().reset_index(drop=True)
M = L.M
key = lambda b, s: t[(t.batter == b) & (t.season == s)].iloc[0]
AB, GM = key("Abhishek Sharma", 2026), key("Glenn Maxwell", 2023)
Z = t[["z_" + m for m in M]].values
def dists(row):
    d = np.sqrt(((Z - Z[row.name]) ** 2).sum(1)); x = t.assign(dist=d); return x[x.batter != row.batter].sort_values("dist")
near = dists(AB); top5 = near.head(5)
s26 = t[t.season == 2026]; n26 = len(s26)
rank = lambda m, hi=True: int((s26[m] > AB[m]).sum() + 1) if hi else int((s26[m] < AB[m]).sum() + 1)
r_bpd = rank("Balls per dismissal")          # 1 = hardest to dismiss
worse_bpd = n26 - r_bpd                       # how many got out more often
med = float(near.dist.median()); d1 = float(top5.dist.iloc[0])
print("ranks", {m: rank(m) for m in M}, "bpd rank", r_bpd, "worse", worse_bpd, "median", round(med, 2), "d1", round(d1, 2))
SHORT_TEAM = {"Sunrisers Hyderabad": "SRH", "Royal Challengers Bengaluru": "RCB", "Delhi Capitals": "DC", "Mumbai Indians": "MI",
              "Punjab Kings": "PBKS", "Kolkata Knight Riders": "KKR", "Chennai Super Kings": "CSK", "Rajasthan Royals": "RR",
              "Gujarat Titans": "GT", "Lucknow Super Giants": "LSG"}
ini = lambda n: "".join(w[0] for w in n.split()[:2]).upper()
lab_names = {"SR": "Strike rate", "PP SR": "Powerplay strike rate", "Middle SR": "Overs 7-15 strike rate", "Boundary %": "Boundary %",
             "Six %": "Six %", "Dot %": "Dot-ball %", "Balls per dismissal": "Balls per dismissal", "Average": "Average",
             "SR v pace": "Strike rate v pace", "SR v spin": "Strike rate v spin", "First 10 balls SR": "First 10 balls strike rate"}
def dotrows(hl):
    rows = []
    for m in M:
        v = AB[m]; txt = f"{v:.1f}" if v < 100 or m.endswith("%") else f"{v:.0f}"
        r = dict(label=lab_names[m], v=round(float(AB["p_" + m])), text=txt)
        if m in hl: r.update(hl=True, at=hl[m]); r["badge"] = f"#{rank(m)}" if rank(m) <= 3 else None
        if not r.get("badge"): r.pop("badge", None)
        rows.append(r)
    return rows
FOOT = "IPL ball-by-ball, Sportmonks · seasons with 200+ balls faced, 2013-2026 · super overs excluded · analysis/lab_twin.py"
TABS = ["INPUTS", "MODEL", "MAP", "TWIN", "CHECKS"]
sp = lambda d: {"tabs": TABS, "tab": d}
radial_items = []
angs = [180, 300, 25, 125, 240]
for k, (_, r) in enumerate(top5.iterrows()):
    radial_items.append(dict(label=f"#{k + 1} {r.batter.split()[-1]}", sub=f"{r.season} · {r.dist:.2f}", d=round(float(r.dist), 2),
                             t=ini(r.batter), kit=SHORT_TEAM.get(r.team, "ink"), ang=angs[k], word=r.batter.split()[-1].lower() if k < 4 else "maxwell"))
cloud = [round(float(x), 2) for x in near.dist.values]
cmp_rows = [["Strike rate", f"{AB.SR:.1f}", f"{GM.SR:.1f}", "a"], ["Strike rate v pace", f"{AB['SR v pace']:.1f}", f"{GM['SR v pace']:.1f}", "level"],
            ["Balls per dismissal", f"{AB['Balls per dismissal']:.1f}", f"{GM['Balls per dismissal']:.1f}", "level"],
            ["Six %", f"{AB['Six %']:.1f}", f"{GM['Six %']:.1f}", "level"], ["Strike rate v spin", f"{AB['SR v spin']:.1f}", f"{GM['SR v spin']:.1f}", "a"]]
spec = json.load(open("specs/lab_ep1_abhishek_twin.json")) if False else {}
spec.update({
 "slug": "lab_ep1_abhishek_twin", "theme": "lab", "captions": "lab", "tag": "THE LAB", "tagsub": "EP. 1 · ABHISHEK'S TWIN",
 "files": {"long": "The_Lab_Ep1_Abhishek_Sharma_Statistical_Twin", "short": "The_Lab_Ep1_Abhishek_Twin_Short_9x16"},
 "thumb": {"kicker": "THE LAB · EP. 1", "lines": [{"t": "ABHISHEK'S"}, {"t": "STATISTICAL TWIN", "c": "gold"}], "hero": f"{d1:.2f}", "herosize": 260},
 "sources": ["Sportmonks IPL ball-by-ball cache, 2013-2026 (data/ipl). Seasons with 200+ balls faced (405). 11 measures, z-scored within each season; distance = Euclidean across the 11. Dismissals counted for the player out (bowled rows carry no out_id; non-striker run-outs included). analysis/lab_twin.py, make_lab_twin.py",
             "https://www.crictracker.com/cricket-appeal/ipl-2026-top-10-batters-of-the-season/6/ (Abhishek 2026: 563 runs, SR 204.72)",
             "https://royalchallengers.com/rcb-cricket-news/news/faf-du-plessis-to-glenn-maxwell-top-3-batsmen-for-rcb-in-ipl-2023 (Maxwell 2023: 400 runs, SR 183.48)"],
})
json.dump({"AB": {m: float(AB[m]) for m in M}, "ranks": {m: rank(m) for m in M}, "n26": n26, "top5": top5[["season", "batter", "dist"]].values.tolist(),
           "median": med, "worse_bpd": worse_bpd, "GM": {m: float(GM[m]) for m in M}}, open("data/lab_twin_ep1_facts.json", "w"), default=str, indent=1)

# ---------------------------------------------------------------- extra facts for the long version
lg = t.groupby("season").apply(lambda x: 100 * x.runs.sum() / x.balls.sum())
own = {int(r.season): round(float(d), 2) for (_, r), d in zip(t[t.batter == "Abhishek Sharma"].iterrows(),
       np.sqrt(((Z[t.batter == "Abhishek Sharma"] - Z[AB.name]) ** 2).sum(1))) if r.season != 2026}
nn = []
for i in range(len(t)):
    d = np.sqrt(((Z - Z[i]) ** 2).sum(1)); d[(t.batter_id == t.batter_id[i]).values] = 99; nn.append(d.min())
t["nn"] = nn; iso = t.sort_values("nn", ascending=False).head(4)
print("league SR 2013", round(lg[2013], 1), "2026", round(lg[2026], 1), "own", own)
print(iso[["season", "batter", "runs", "SR", "nn"]].round(2).values.tolist())
AS = {"t": "AS", "kit": "SRH", "name": "Abhishek 2026"}; GMt = {"t": "GM", "kit": "RCB", "name": "Maxwell 2023"}
for k, w in enumerate(["closest", "second", "third", "fourth", "fifth"]): radial_items[k]["word"] = w
def S(vo, scene): return {"vo": vo, "scene": scene}
hook = S("There's nobody like अभिषेक शर्मा. Or is there? We built a model to find his statistical twin.",
         {"type": "lab_title", "kicker": "THE LAB · EP. 1", "lines": ["Who is", "Abhishek Sharma's", "[statistical twin?]"], "tokens": [AS]})
inputs = S(f"Step one. Eleven measures, from every ball he faced in twenty twenty-six. Each one is ranked against the thirty batters who faced two hundred balls or more.",
           dict(type="lab_dots", kicker="STEP 1 · THE INPUTS", title="11 measures.", sub="IPL 2026 · percentile v the 30 batters with 200+ balls",
                rows=dotrows({}), foot=FOOT, **sp(0)))
second = S("He's second for strike rate. Second in the powerplay. Second against pace, and second against spin.",
           dict(type="lab_dots", kicker="STEP 1 · THE INPUTS", title="Second, again and again.", sub="IPL 2026 · percentile v the 30 batters with 200+ balls",
                rows=dotrows({"SR": .1, "PP SR": .25, "SR v pace": .45, "SR v spin": .65}), from_=0, foot=FOOT, **sp(0)))
second["scene"]["from"] = 0.0; second["scene"]["stagger"] = .05; second["scene"].pop("from_")
catch = S(f"The catch? He's out every twenty balls. Only {['zero','one','two','three','four','five','six'][worse_bpd]} of the thirty got out more often.",
          dict(type="lab_dots", kicker="STEP 1 · THE INPUTS", title="The catch.", sub="IPL 2026 · percentile v the 30 batters with 200+ balls",
               rows=dotrows({"Balls per dismissal": .25}), foot=FOOT, stagger=.05, **{"from": 0.0}, **sp(0)))
model = S("Step two. We measured the same eleven things for every IPL season since twenty thirteen. Four hundred and five of them.",
          dict(type="lab_big", kicker="STEP 2 · THE MODEL", title="Every season.", value=405, unit="seasons",
               label="Every IPL batting season with 200+ balls faced, 2013 to 2026", color="red", foot=FOOT, **sp(1)))
mapsc = S(f"Then we measured how far each season sits from his, across all eleven at once. Most are a long way off. A typical season sits five point eight eight away.",
          dict(type="lab_swarm", kicker="STEP 3 · THE MAP", title="One distance.", sub="from Abhishek 2026 · all 11 measures · lower = more alike",
               values=cloud, domain=[0, 12], ticks=[0, 3, 6, 9, 12], axis="distance (z-scores within each season)",
               hl=[{"v": round(med, 2), "label": "Typical season", "sub": f"{med:.2f}", "t": "~", "kit": [150, 150, 146], "word": "typical", "dy": -190}],
               foot=FOOT, **sp(2)))
top = S("Fifth, ऋषभ पंत in twenty eighteen. Fourth, Travis Head. Third, Ryan Rickelton. Second, पंत again, in twenty seventeen. And the closest of all?",
        dict(type="lab_radial", kicker="THE CLOSEST SEASONS", title="Top 5.", sub="distance from Abhishek 2026 · all 11 measures",
             items=radial_items, cloud=cloud, dmax=8, rings=[1, 2, 4, 8], center={"label": "ABHISHEK 2026"}, foot=FOOT, **sp(3)))
reveal = S("Glenn Maxwell, in twenty twenty-three. Almost the same strike rate against pace. Out every eighteen to twenty balls. A six every seven balls or so. The difference? अभिषेक is quicker overall, and far quicker against spin.",
           dict(type="lab_compare", kicker=f"#1 OF {len(near)} SEASONS · DISTANCE {d1:.2f}", title="Glenn Maxwell, 2023.", a=AS | {"name": "Abhishek 2026"},
                b=GMt, rows=cmp_rows, foot=FOOT, **sp(3)))
closer = S(f"His distance from Maxwell: one point six two. A typical season: five point eight eight. More than three and a half times further away.",
           dict(type="lab_units", kicker="HOW CLOSE IS CLOSE?", title="3.6 times closer.", rows=[
               {"label": "Maxwell 2023", "t": "GM", "kit": "RCB", "k": round(d1, 2), "n": 6, "c": "red", "text": f"{d1:.2f}", "word": "maxwell"},
               {"label": "Typical season", "k": round(med, 2), "n": 6, "c": "grey", "text": f"{med:.2f}", "word": "typical"}],
               sub="each dot = 1 unit of distance", foot=FOOT, **sp(3)))
checks = S("And before you ask. We dropped each measure, one at a time. Maxwell stayed on top, all eleven times. We lowered the bar to a hundred and fifty balls. Still Maxwell. And on Maxwell's own list, number one is अभिषेक.",
           dict(type="lab_score", kicker="AND BEFORE YOU ASK", title="Three checks.", rows=[
               {"label": "Drop any one of the 11 measures", "win": "Maxwell · 11 of 11", "c": "green", "word": "dropped"},
               {"label": "Lower the bar to 150 balls", "win": "Maxwell", "c": "green", "word": "lowered"},
               {"label": "Search from Maxwell's side", "win": "Abhishek · #1", "c": "green", "word": "own"}], foot=FOOT, **sp(4)))
twice = S("One more thing. His twenty twenty-four season? Its closest match is Maxwell too. From twenty fourteen.",
          dict(type="lab_score", kicker="ONE MORE THING", title="Twice.", rows=[
              {"label": "Abhishek 2026", "win": f"Maxwell 2023 · {d1:.2f}", "c": "red", "at": .05},
              {"label": "Abhishek 2024", "win": "Maxwell 2014 · 2.40", "c": "red", "word": "maxwell"}], foot=FOOT, **sp(4)))
cta = S("So, he isn't one of a kind. He's the Big Show, opening the batting. Who should we put in the lab next? Tell us in the comments.",
        {"type": "cta", "lines": [{"t": "WHO'S NEXT"}, {"t": "IN THE LAB?", "c": "gold"}], "pill": "SUBSCRIBE FOR MORE"})
spec["short"] = [hook, inputs, second, catch, model, mapsc, top, reveal, closer, checks, twice, cta]

# long: same spine, plus the method, his own seasons, and the seasons with no twin
assert round(lg[2013]) == 127 and round(lg[2026]) == 163, (lg[2013], lg[2026])
why = S("Why rank him against his own season? Because the game keeps getting faster. Among these batters, the average strike rate was one twenty-seven in twenty thirteen. In twenty twenty-six, it was one sixty-three. A strike rate that was elite then is ordinary now. So every number is compared with its own season first.",
        dict(type="lab_units", kicker="STEP 2 · THE MODEL", title="Same season, same scale.", rows=[
            {"label": "Average strike rate, 2013", "k": round(lg[2013] / 50, 2), "n": 5, "c": "grey", "text": f"{lg[2013]:.0f}", "at": .15},
            {"label": "Average strike rate, 2026", "k": round(lg[2026] / 50, 2), "n": 5, "c": "red", "text": f"{lg[2026]:.0f}", "word": "twenty-six"}],
            sub="qualified batters (200+ balls) · each dot = 50 strike rate", foot=FOOT, **sp(1)))
ownsc = S(f"We also checked his own seasons. His twenty twenty-four and twenty twenty-five seasons sit close to twenty twenty-six. His first full season, twenty twenty-two, is miles away. That year, he struck at one thirty-three.",
          dict(type="lab_units", kicker="HIS OWN SEASONS", title="A different player in 2022.", rows=[
              {"label": "Abhishek 2025", "t": "AS", "kit": "SRH", "k": own.get(2025, 0), "n": 6, "c": "red", "text": f"{own.get(2025, 0):.2f}", "at": .15},
              {"label": "Abhishek 2024", "t": "AS", "kit": "SRH", "k": own.get(2024, 0), "n": 6, "c": "red", "text": f"{own.get(2024, 0):.2f}", "at": .3},
              {"label": "Abhishek 2022", "t": "AS", "kit": "SRH", "k": own.get(2022, 0), "n": 6, "c": "grey", "text": f"{own.get(2022, 0):.2f}", "word": "twenty-two"}],
              sub="distance from his 2026 season", foot=FOOT, **sp(3)))
iso_rows = [{"label": f"{r.batter} {int(r.season)}", "win": f"nearest {r.nn:.2f}", "c": "ink", "at": .1 + .15 * k} for k, (_, r) in enumerate(iso.iterrows())]
alone = S("So who really is one of a kind? These seasons sit furthest from anyone else's.",
          dict(type="lab_score", kicker="ONE OF A KIND", title="No twin.", rows=iso_rows, sub="largest distance to the nearest other player's season", foot=FOOT, **sp(4)))
TEAMK = lambda team, season: SHORT_TEAM.get(team, "ink")
def pair(vo, who, tw, ts, title, word):
    a = key(who, 2026); b = key(tw, ts)
    d = float(np.sqrt(((Z[a.name] - Z[b.name]) ** 2).sum()))
    nm = lambda n: n.replace("Lokesh Rahul", "KL Rahul")
    rows = [["Strike rate", f"{a.SR:.1f}", f"{b.SR:.1f}", "level"], ["Average", f"{a.Average:.1f}", f"{b.Average:.1f}", "level"],
            ["Strike rate percentile", f"{a['p_SR']:.0f}", f"{b['p_SR']:.0f}", "level"], ["Six %", f"{a['Six %']:.1f}", f"{b['Six %']:.1f}", "level"]]
    return S(vo, dict(type="lab_compare", kicker=f"LIGHTNING ROUND · DISTANCE {d:.2f}", title=title, a={"t": ini(nm(who)), "kit": TEAMK(a.team, 2026), "name": f"{nm(who).split()[-1]} 2026"},
                      b={"t": ini(nm(tw)), "kit": TEAMK(b.team, ts), "name": f"{nm(tw).split()[-1]} {ts}", "word": word}, rows=rows, foot=FOOT, **sp(4)))
lr_intro = S("So we ran the model on IPL twenty twenty-six's other top run-scorers. Some twins are obvious. Some are not.",
             dict(type="lab_big", kicker="LIGHTNING ROUND", title="Everyone gets a twin.", value=6, unit="more batters",
                  label="IPL 2026's top run-scorers, each matched against every season since 2013", color="red", foot=FOOT, **sp(4)))
p_gill = pair("शुभमन गिल's closest match is the man at the other end. His opening partner, साई सुदर्शन, in the same season.", "Shubman Gill", "Sai Sudharsan", 2026, "Gill → his own partner.", "partner")
p_sai = pair("And सुदर्शन's twin? Shaun Marsh, in twenty thirteen. Marsh struck at just one twenty. But in twenty thirteen, that was a little below the league average. Just like one fifty-eight is today.", "Sai Sudharsan", "Shaun Marsh", 2013, "Sudharsan → Shaun Marsh, 2013.", "marsh")
p_kohli = pair("विराट कोहली matches another opening partner. Faf du Plessis, in twenty twenty-three. The same average: fifty-six.", "Virat Kohli", "Faf du Plessis", 2023, "Kohli → Faf, 2023.", "faf")
p_klaasen = pair("Heinrich Klaasen matches संजू सैमसन's twenty twenty-four. Both averaged forty-eight, with a strike rate right in the middle of the league.", "Heinrich Klaasen", "Sanju Samson", 2024, "Klaasen → Samson, 2024.", "samson")
p_kishan = pair("And इशान किशन's twenty twenty-six looks like KL Rahul's twenty sixteen. Very different numbers, until you put each one in its own season.", "Ishan Kishan", "Lokesh Rahul", 2016, "Kishan → KL Rahul, 2016.", "rahul")
vs_ = key("Vaibhav Suryavanshi", 2026); vs_nn = float(t.loc[vs_.name, "nn"])
lone = S(f"And then there's वैभव सूर्यवंशी. Seven seventy-six runs, at a strike rate of two thirty-seven. His nearest match is three point one three away. Only one season in our data is further from everyone else.",
         dict(type="lab_big", kicker="NO TWIN", title="Sooryavanshi, 2026.", value=round(vs_nn, 2), dec=2, unit="to his nearest match",
              label="Strike rate 237.3 · 776 runs · the second most isolated IPL season since 2013", color="red", foot=FOOT, **sp(4)))
assert round(vs_nn, 2) == 3.13 and int((t.nn > vs_nn).sum()) == 1, (vs_nn, (t.nn > vs_nn).sum())
spec["long"] = [hook, inputs, second, catch, model, why, mapsc, top, reveal, closer, ownsc, checks, twice, lr_intro, p_gill, p_sai, p_kohli, p_klaasen, p_kishan, lone, alone, cta]
spec["chapters"] = True
for k, name in [(0, "The question"), (1, "The inputs"), (4, "The model"), (6, "The map"), (7, "The twin"), (11, "The checks"), (13, "Lightning round"), (19, "No twin")]:
    spec["long"][k]["chapter"] = name
spec["yt"] = {"long": {"title": "Who is Abhishek Sharma's statistical twin? We ran every IPL season since 2013",
                       "description": "The Lab, Episode 1. We measured Abhishek Sharma's IPL 2026 season on 11 measures, then compared it with all 405 IPL batting seasons (200+ balls) since 2013. The closest match is a surprise, and it holds up when we stress-test the model.",
                       "tags": ["Abhishek Sharma", "Glenn Maxwell", "IPL 2026", "IPL stats", "cricket analytics", "statistical twin", "The Lab", "The Third Man"]},
              "short": {"title": "Abhishek Sharma's statistical twin? The model says... 🧪 #Shorts",
                        "description": "The Lab, Ep. 1: 11 measures, 405 IPL seasons, one nearest neighbour.",
                        "tags": ["Abhishek Sharma", "Glenn Maxwell", "IPL", "cricket stats", "The Lab", "The Third Man"]}}
json.dump(spec, open("specs/lab_ep1_abhishek_twin.json", "w"), ensure_ascii=False, indent=1)
print("short words", sum(len(x["vo"].split()) for x in spec["short"]), "long words", sum(len(x["vo"].split()) for x in spec["long"]))
