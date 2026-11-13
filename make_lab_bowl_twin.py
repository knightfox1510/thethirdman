"""Builds specs/lab_ep2_bumrah_twin.json from analysis/lab_bowl_twin.py; claims asserted."""
import json, sys, numpy as np
sys.path.insert(0, "analysis")
import lab_bowl_twin as L
t = L.table(); M = L.M
row = lambda b, s: t[(t.bowler == b) & (t.season == s)].iloc[0]
JB, DS = row("Jasprit Bumrah", 2024), row("Dale Steyn", 2013)
near = L.near(t, "Jasprit Bumrah", 2024, k=600); top5 = near.head(5); d1 = float(top5.dist.iloc[0]); med = float(near.dist.median())
assert top5.bowler.iloc[0] == "Dale Steyn" and round(d1, 2) == 1.89 and len(t) == 513
assert all(L.near(t, "Jasprit Bumrah", 2024, [x for x in M if x != m], k=1).bowler.iloc[0] == "Dale Steyn" for m in M)
rev = L.near(t, "Dale Steyn", 2013, k=5).reset_index(drop=True); rank_rev = int(rev.index[rev.bowler == "Jasprit Bumrah"][0]) + 1; assert rank_rev == 3
assert (JB.balls, JB.wkts, round(JB.Economy, 2)) == (311, 20, 6.48) and (DS.balls, DS.wkts, round(DS.Economy, 2)) == (407, 19, 5.66)
FOOT = "IPL ball-by-ball, Sportmonks · bowling seasons with 180+ balls, 2013-2026 (513) · 10 measures z-scored within season · analysis/lab_bowl_twin.py"
TABS = ["INPUTS", "MODEL", "TWIN", "CHECKS"]
TEAM = {"Sunrisers Hyderabad": "SRH", "Mumbai Indians": "MI", "Delhi Capitals": "DC", "Lucknow Super Giants": "LSG", "Royal Challengers Bengaluru": "RCB",
        "Kolkata Knight Riders": "KKR", "Gujarat Titans": "GT", "Rajasthan Royals": "RR", "Chennai Super Kings": "CSK", "Punjab Kings": "PBKS"}
ini = lambda n: "".join(w[0] for w in n.split()[:2]).upper()
NM = {"Economy": "Economy", "PP economy": "Powerplay economy", "Death economy": "Death economy", "Dot %": "Dot-ball %", "Balls per wicket": "Balls per wicket",
      "Boundary % conceded": "Boundary % conceded", "Balls per six": "Balls per six", "Death share": "Share of balls at the death", "PP share": "Share of balls in powerplay",
      "Econ v left-handers": "Economy v left-handers"}
def S(vo, sc): return {"vo": vo, "scene": sc}
sp = lambda i: {"tabs": TABS, "tab": i, "foot": FOOT}
rows = [dict(label=NM[m], v=round(float(JB["p_" + m])), text=f"{JB[m]:.1f}") for m in M]
for r, m in zip(rows, M):
    if m in ("Dot %", "Balls per six"): r.update(hl=True, at=.3 if m == "Dot %" else .55, badge="#1")
hook = S("Jasprit बुमराह's twenty twenty-four IPL was one of the best fast-bowling seasons ever. So we asked a model: has anyone ever bowled like that?",
         {"type": "lab_title", "kicker": "THE LAB · EP. 2", "lines": ["Who is", "Bumrah's", "[bowling twin?]"], "players": [{"kit": "MI", "pose": "bowl", "cap": True, "name": "Jasprit Bumrah", "sub": "Mumbai Indians · IPL 2024", "chips": [[f"{JB.Economy:.2f}", "economy"], [str(JB.wkts), "wickets"]]}]})
inputs = S("Ten measures from every ball he bowled. Economy overall, in the powerplay and at the death. Dot balls. Sixes. Where he bowls, and who to. He ranked first in his season for dot balls, and for balls per six.",
           dict(type="lab_dots", kicker="STEP 1 · THE INPUTS", title="10 measures.", sub="IPL 2024 · percentile v that season's bowlers (180+ balls)", rows=rows, **sp(0)))
assert JB["p_Dot %"] == 100 and JB["p_Balls per six"] == 100
model = S("Then, every IPL bowling season since twenty thirteen with a hundred and eighty balls or more. Five hundred and thirteen of them. Each measured against its own season.",
          dict(type="lab_big", kicker="STEP 2 · THE MODEL", title="Every season.", value=513, unit="seasons", label="IPL bowling seasons with 180+ balls, 2013 to 2026", **sp(1)))
cloud = [round(float(x), 2) for x in near.dist.values]
LBL = {"Mohsin Khan": "Mohsin Khan", "Bhuvneshwar Kumar": "Bhuvneshwar", "Sunil Narine": "Narine", "Anrich Nortje": "Nortje", "Dale Steyn": "Steyn"}
items = [dict(label=f"#{k + 1} {LBL.get(r.bowler, r.bowler.split()[-1])}", sub=f"{r.season} · {r.dist:.2f}", d=round(float(r.dist), 2), t=ini(r.bowler), kit=TEAM.get(r.team, "ink"),
              ang=[180, 300, 25, 125, 240][k], word=["steyn", "second", "third", "fourth", "fifth"][k]) for k, (_, r) in enumerate(top5.iterrows())]
names = [r.bowler for _, r in top5.iterrows()]; print(names, [round(x, 2) for x in top5.dist])
HI = {"Bhuvneshwar Kumar": "भुवनेश्वर", "Sunil Narine": "Sunil Narine"}
top = S(f"Fifth, {HI.get(names[4], names[4].split()[-1])}, in twenty thirteen. Fourth, {HI.get(names[3], names[3].split()[-1])}, in twenty twenty-six. Third, Mohsin Khan. Second, Anrich Nortje. And the closest of all? Dale Steyn.",
        dict(type="lab_radial", kicker="THE CLOSEST SEASONS", title="Top 5.", sub="distance from Bumrah 2024 · all 10 measures", items=items, cloud=cloud, dmax=10,
             rings=[2, 5, 10], center={"label": "BUMRAH 2024"}, **sp(2)))
assert names == ["Dale Steyn", "Anrich Nortje", "Mohsin Khan", "Bhuvneshwar Kumar", "Sunil Narine"] and list(top5.season) == [2013, 2021, 2022, 2026, 2013]
reveal = S("Dale Steyn, for Sunrisers Hyderabad, in twenty thirteen. Nineteen wickets at five point six six. Both were near the top of their season for dot balls, and both went for under six an over against left-handers. The difference? Steyn was even harder to hit for six. Bumrah took wickets more often.",
           dict(type="lab_compare", kicker=f"#1 OF {len(near)} · DISTANCE {d1:.2f}", title="Dale Steyn, 2013.", a={"t": "JB", "kit": "MI", "name": "Bumrah 2024"},
                b={"t": "DS", "kit": "SRH", "name": "Steyn 2013"}, rows=[
                    ["Economy", f"{JB.Economy:.2f}", f"{DS.Economy:.2f}", "b"], ["Dot-ball %", f"{JB['Dot %']:.1f}", f"{DS['Dot %']:.1f}", "b"],
                    ["Economy v left-handers", f"{JB['Econ v left-handers']:.2f}", f"{DS['Econ v left-handers']:.2f}", "level"],
                    ["Balls per six", f"{JB['Balls per six']:.0f}", f"{DS['Balls per six']:.0f}", "b"], ["Balls per wicket", f"{JB['Balls per wicket']:.1f}", f"{DS['Balls per wicket']:.1f}", "a"]], foot=FOOT))
assert DS["p_Dot %"] >= 95 and JB["p_Dot %"] >= 95 and JB["Econ v left-handers"] < 6 and DS["Econ v left-handers"] < 6 and DS["Balls per six"] > JB["Balls per six"] and JB["Balls per wicket"] < DS["Balls per wicket"]
checks = S("And the checks. Drop any one measure: still Steyn, all ten times. Change the minimum to one fifty or two forty balls: still Steyn. One honest caveat: on Steyn's own list, बुमराह comes third.",
           dict(type="lab_score", kicker="AND BEFORE YOU ASK", title="The checks.", rows=[
               {"label": "Drop any one of the 10 measures", "win": "Steyn · 10 of 10", "c": "green", "word": "drop"},
               {"label": "Minimum 150 or 240 balls", "win": "Steyn", "c": "green", "word": "minimum"},
               {"label": "Search from Steyn's side", "win": "Bumrah · #3", "c": "grey", "word": "caveat"}], **sp(3)))
cta = S("So the closest thing to बुमराह at his best? Dale Steyn at his. Who should we put in the lab next? Tell us in the comments.",
        {"type": "cta", "lines": [{"t": "WHO'S NEXT"}, {"t": "IN THE LAB?", "c": "gold"}], "pill": "SUBSCRIBE FOR MORE"})
# lightning round (long)
lr = []
for b, words in [("Bhuvneshwar Kumar", "भुवनेश्वर कुमार's twenty twenty-six, with twenty-eight wickets, matches Lasith Malinga in twenty fourteen."),
                 ("Kagiso Rabada", "Kagiso Rabada, the purple cap winner, matches Nandre Burger. In the same season."),
                 ("Jofra Archer", "Jofra Archer's twenty twenty-six matches Yash Dayal's twenty twenty-four."),
                 ("Anshul Kamboj", "And Anshul Kamboj matches Anrich Nortje's twenty twenty. The closest pair of the lot.")]:
    a = row(b, 2026); n = L.near(t, b, 2026, k=1).iloc[0]
    lr.append(S(words, dict(type="lab_compare", kicker=f"LIGHTNING ROUND · DISTANCE {n.dist:.2f}", title=f"{b.split()[-1]} → {n.bowler.split()[-1]}, {n.season}.",
                            a={"t": ini(b), "kit": TEAM.get(a.team, "ink"), "name": f"{b.split()[-1]} 2026"}, b={"t": ini(n.bowler), "kit": TEAM.get(n.team, "ink"), "name": f"{n.bowler.split()[-1]} {n.season}"},
                            rows=[["Economy", f"{a.Economy:.2f}", f"{n.Economy:.2f}", "level"], ["Wickets", str(a.wkts), str(n.wkts), "level"],
                                  ["Dot-ball %", f"{a['Dot %']:.1f}", f"{n['Dot %']:.1f}", "level"], ["Share of balls at the death", f"{a['Death share']:.0f}%", f"{n['Death share']:.0f}%", "level"]], foot=FOOT)))
chk = {b: L.near(t, b, 2026, k=1).iloc[0].bowler for b in ("Bhuvneshwar Kumar", "Kagiso Rabada", "Jofra Archer", "Anshul Kamboj")}
assert chk == {"Bhuvneshwar Kumar": "Lasith Malinga", "Kagiso Rabada": "Nandre Burger", "Jofra Archer": "Yash Dayal", "Anshul Kamboj": "Anrich Nortje"}, chk
assert row("Bhuvneshwar Kumar", 2026).wkts == 28
spec = {"slug": "lab_ep2_bumrah_twin", "theme": "lab", "captions": "lab", "series": "lab", "tag": "THE LAB", "tagsub": "EP. 2 · BUMRAH'S TWIN",
        "files": {"long": "The_Lab_Ep2_Bumrah_Bowling_Twin", "short": "The_Lab_Ep2_Bumrah_Twin_Short_9x16"},
        "thumb": {"kicker": "THE LAB · EP. 2", "lines": [{"t": "BUMRAH'S"}, {"t": "BOWLING TWIN", "c": "gold"}], "hero": "1.89", "herosize": 280},
        "sources": ["Sportmonks IPL ball-by-ball 2013-2026; bowling seasons with 180+ legal balls (513); 10 measures z-scored within season; Euclidean distance. analysis/lab_bowl_twin.py, make_lab_bowl_twin.py",
                    "https://crictracker.com/t20/ipl-indian-premier-league/archives-ipl-2013/stats/bowling-best-economy-rates/ (Steyn 2013: 67.5 overs, 19 wickets, economy 5.66)"],
        "short": [hook, inputs, model, top, reveal, checks, cta],
        "long": [hook, inputs, model, top, reveal, checks] + [S("Then we ran the model on IPL twenty twenty-six's top wicket-takers.",
                 dict(type="lab_big_text", kicker="LIGHTNING ROUND", lines=["Everyone", "gets a [twin.]"], foot=FOOT))] + lr + [cta]}
for k, nm in [(0, "The question"), (1, "The inputs"), (3, "The twin"), (5, "The checks"), (6, "Lightning round")]: spec["long"][k] = dict(spec["long"][k], chapter=nm)
spec["yt"] = {"long": {"title": "Who is Bumrah's bowling twin? We ran 513 IPL seasons through a model", "description": "The Lab, Episode 2: Jasprit Bumrah's 2024 IPL season, matched against every IPL bowling season since 2013. Plus the twins of IPL 2026's top wicket-takers.",
                       "tags": ["Jasprit Bumrah", "Dale Steyn", "IPL stats", "Bhuvneshwar Kumar", "Lasith Malinga", "cricket analytics", "The Lab", "The Third Man"]},
              "short": {"title": "Bumrah's bowling twin? The model found a legend 🧪 #Shorts", "description": "The Lab, Ep. 2: 10 measures, 513 IPL bowling seasons, one nearest neighbour.", "tags": ["Bumrah", "Dale Steyn", "IPL", "The Lab", "The Third Man"]}}
import voice_lint; voice_lint.fix_spec(spec)
json.dump(spec, open("specs/lab_ep2_bumrah_twin.json", "w"), ensure_ascii=False, indent=1)
print("short words", sum(len(x["vo"].split()) for x in spec["short"]), "long", sum(len(x["vo"].split()) for x in spec["long"]))
