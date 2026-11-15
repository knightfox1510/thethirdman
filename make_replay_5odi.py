"""Builds specs/replay_5odi.json: The Replay Room Ep. 3, "India vs New Zealand - 5th ODI: how India won at 22%" (long + Short + a 2:20 Instagram Reel cut).
Every number is asserted against the analysis tables (data/series/nz_ind_2026/, built by analysis/nz_ind_*.py from the Cricbuzz ball-by-ball capture and validated against Wikipedia's
match box and Cricbuzz's own summary lines). Win probability is OUR model (fitted on the Cricsheet ODI archive) and is said to be ours on screen and in the narration.
    CS_DIR=... python3 make_replay_5odi.py"""
import csv, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voice_lint
from voice_lint import NAMES
from dataops import verify as V

AN = "data/series/nz_ind_2026/analysis"; OUT = "data/series/nz_ind_2026"
S = json.load(open(f"{AN}/summary.json"))["matches"]["nz_ind_5odi"]; T = json.load(open(f"{AN}/story.json")); R = T["nz_ind_5odi"]; R4 = T["nz_ind_4odi"]; S4 = json.load(open(f"{AN}/summary.json"))["matches"]["nz_ind_4odi"]
D = lambda n: NAMES[n]                                          # Devanagari for every subcontinent name
pv = {r["player"]: r for r in csv.DictReader(open(f"{AN}/nz_ind_5odi_player_value.csv", encoding="utf-8"))}
wp = list(csv.DictReader(open(f"{AN}/nz_ind_5odi_wp.csv", encoding="utf-8")))
i1, i2 = S["innings"]["1"], S["innings"]["2"]; ck = R["chase_checkpoints"]; lw = R["last_wicket_stand"]

# ------------------------------------------------------------------ facts (asserted)
assert (i1["score"], i1["wkts"], i1["overs"], i2["score"], i2["wkts"], i2["overs"]) == (209, 10, "42.1", 187, 10, "48.1")
p_def = round(100 * (1 - 0.782)); assert p_def == 22                                              # our model: P(NZ chase 210) = 78.2% at ball 0 (analysis/nz_ind_wp.py prints it)
pp1 = i1["phases"]["powerplay (1-10)"]; assert (pp1["runs"], pp1["wkts"], pp1["balls"], round(pp1["dot_pct"])) == (37, 3, 60, 70)
assert (lw["runs"], lw["legal_balls"]) == (26, 10) and round(lw["wp_gain"] * 100) == 7
assert [(c["after_over"], c["score"]) for c in ck] == [(10, "41/1"), (20, "80/2"), (30, "116/4"), (40, "155/6"), (48, "187/10")]
assert (ck[0]["required_rate"], ck[0]["run_rate_so_far"], ck[2]["required_rate"], ck[2]["run_rate_so_far"], ck[3]["required_rate"], ck[3]["run_rate_so_far"]) == (4.22, 4.1, 4.7, 3.87, 5.5, 3.88)
tp = R["tipping_point"]; assert (tp["over"], tp["score"], round(100 * tp["india_wp"])) == (40.4, "158/7", 64)
top = sorted(wp, key=lambda r: -abs(float(r["delta_bat_wp"])))[:2]; assert (top[0]["over"], top[0]["bowler"], top[0]["batter"]) == ("40.4", "Naman Dhir", "Mitchell Santner") and round(100 * abs(float(top[0]["delta_bat_wp"]))) == 27
sw = {r["over"]: abs(float(r["delta_bat_wp"])) for r in wp if r["wicket"] == "True"}; assert round(100 * (sw["30.6"] + sw["31.1"])) == 39
dr = T["drops"]["nz_ind_5odi"]["runs_conceded_after_drops"]; assert dr == {"NZ": 61, "India": 37} and 61 - 37 == 24
assert [(d["batter"], d["runs_at_drop"], d["runs_after_drop"]) for d in T["drops"]["nz_ind_5odi"]["list"]] == [("Axar Patel", "2", 44), ("Shreyas Iyer", "5", 17), ("Dean Foxcroft", "5", 26), ("Michael Bracewell", "8", 11)]
dh = pv["Naman Dhir"]; assert (dh["bowl_balls"], dh["bowl_runs"], dh["bowl_wkts"], round(100 * float(dh["total_wpa_for_team"]))) == ("12", "4", "1", 26) and R["hidden"]["winners"][0]["player"] == "Naman Dhir"
ar = pv["Arshdeep Singh"]; assert (ar["bowl_balls"], ar["bowl_runs"], ar["bowl_wkts"]) == ("60", "30", "3") and max(pv.values(), key=lambda r: float(r["total_wpa_for_team"]))["player"] == "Arshdeep Singh"
ps = S["pace_vs_spin"]; assert (ps["India"]["pace"]["overs"], ps["India"]["pace"]["econ"], ps["India"]["spin"]["econ"], ps["New Zealand"]["pace"]["econ"], ps["New Zealand"]["spin"]["econ"]) == ("40.0", 3.88, 3.92, 5.64, 4.1)
n4, n5 = S4["innings"]["1"], i2; assert (n4["run_rate"], n5["run_rate"]) == (6.66, 3.88) and (S4["innings"]["1"]["phases"]["powerplay (1-10)"]["rr"], i2["phases"]["powerplay (1-10)"]["rr"]) == (7.2, 4.1) and (round(n4["dot_pct"]), round(n5["dot_pct"])) == (47, 61)
a4 = [b for b in S4["bowling"] if b["bowler"] == "Arshdeep Singh"][0]; a5 = [b for b in S["bowling"] if b["bowler"] == "Arshdeep Singh"][0]; assert (a4["runs"], a4["wkts"], a5["runs"], a5["wkts"]) == (55, 1, 30, 3)
early = max(float(r["india_wp"]) for r in wp if r["inning"] == "2" and float(r["over"]) <= 20); assert early <= .25
yt = [b for b in S["bowling"] if b["bowler"] == "Yash Thakur"][0]; assert (yt["overs"], yt["runs"], yt["wkts"]) == ("10.0", 38, 1)

c = V.Claims("replay_5odi")
W_, CB = "wikipedia", "cricbuzz_ball_by_ball"
c.check("India 209 (42.1), NZ 187 (48.1), India won by 22 runs", (209, 187, 22), {W_: (209, 187, 22), CB: (i1["score"], i2["score"], i1["score"] - i2["score"])})
c.check("Axar Patel 46 (55); Arshdeep Singh 3/30; Santner 3/47; Foxcroft 31 (42)", ((46, 55), (3, 30), (3, 47), (31, 42)), {W_: ((46, 55), (3, 30), (3, 47), (31, 42)), CB: ((46, 55), (3, 30), (3, 47), (31, 42))})
c.check("Arshdeep Singh Player of the Match; Yash Thakur ODI debut", ("Arshdeep Singh", "Yash Thakur"), {W_: ("Arshdeep Singh", "Yash Thakur"), CB: ("Arshdeep Singh", "Yash Thakur")})
c.check("NZ pace 6/125 in 22.1 overs, spin 4/82 in 20 overs", ((6, 125, "22.1"), (4, 82, "20.0")), {CB: ((6, 125, "22.1"), (4, 82, "20.0")), "cricbuzz_editorial_line": ((6, 125, "22.1"), (4, 82, "20.0"))})
c.check("India's chance of defending 209 = 22% (our model)", 22, {"our_model_cricsheet_archive": 22}, scope="archive")
c.check("Santner's wicket at 158/7 was a 27-point swing; India >50% from there (our model)", (27, 64), {"our_model_cricsheet_archive": (27, 64)}, scope="archive")
c.check("the double (Bracewell 30.6, Foxcroft 31.1) = 39 points (our model)", 39, {"our_model_cricsheet_archive": 39}, scope="archive")
c.check("drops: 61 runs after NZ's let-offs, 37 after India's (descriptive)", (61, 37), {CB: (61, 37)}, scope="archive")
c.check("Naman Dhir 2-0-4-1, +26 points (our model), hidden winner", 26, {"our_model_cricsheet_archive": 26}, scope="archive")
c.check("4th v 5th at Bay Oval: NZ run rate 6.66 v 3.88; powerplay 7.2 v 4.1; Arshdeep 55/1 v 30/3", ((6.66, 3.88), (7.2, 4.1), (55, 1, 30, 3)), {CB: ((6.66, 3.88), (7.2, 4.1), (55, 1, 30, 3)), "cricinfo_4th_odi_capture": ((6.66, 3.88), (7.2, 4.1), (55, 1, 30, 3))}, scope="archive")

# ------------------------------------------------------------------ scenes
def S_(vo, sc, **kw): return dict({"vo": vo, "scene": sc}, **kw)
tok = lambda t, nm, kit=None: {"t": t, "kit": kit or t, "name": nm}
IND = lambda pose, x=.5, **k: dict(kit="IND", pose=pose, x=x, **k)
NZ = lambda pose, x=.5, **k: dict(kit="NZ", pose=pose, x=x, **k)
G = lambda v, l, c="gold": {"v": v, "l": l, "c": c}
def stage(vo, panel, av, **kw): return S_(vo, dict({"type": "stage", "panel": dict(panel, at=.05), "avatars": av}, **kw))
rohit, kohli, gaik, axar, kishan, dhir, arsh, siraj, nabi, thakur, iyer = (D(x) for x in ("Rohit Sharma", "Virat Kohli", "Ruturaj Gaikwad", "Axar Patel", "Ishan Kishan", "Naman Dhir", "Arshdeep Singh", "Mohammed Siraj", "Auqib Nabi", "Yash Thakur", "Shreyas Iyer"))

long = [
 S_(f"India made two hundred and nine. Our model gave them twenty-two per cent to defend it. They won by twenty-two runs. Here is how it happened, from our own ball-by-ball data.",
    {"type": "lab_big", "kicker": "INDIA V NEW ZEALAND · 5TH ODI · BAY OVAL", "title": "India's chance of defending 209.", "value": 22, "suffix": "%", "label": "our model, before the chase began · India won by 22 runs", "color": "red", "word": "twenty-two"}),
 S_("This is The Replay Room. The fifth and final one-day international of the series, at Bay Oval, ball by ball.",
    {"type": "lab_title", "kicker": "THE REPLAY ROOM · EP. 3", "lines": ["The 22%", "[win]"], "teaser": "India v New Zealand · 5th ODI · 15 November 2026"}),
 S_(f"First, India's innings. All out for two hundred and nine in forty-two overs. {rohit}, {kohli} and {gaik} were gone with thirty-four on the board. Two forty-sixes, from {axar} and {kishan}, kept them alive.",
    {"type": "lab_dots", "kicker": "INDIA · EVERY INNINGS · 5TH ODI", "title": "209 all out.", "domain": [0, 50], "ticks": [0, 25, 50], "tick_labels": False,
     "rows": [{"label": "Rohit Sharma", "v": 7, "text": "7 (13)"}, {"label": "Virat Kohli", "v": 5, "text": "5 (7)"}, {"label": "Ruturaj Gaikwad", "v": 18, "text": "18 (27)"}, {"label": "Shreyas Iyer", "v": 22, "text": "22 (26)"},
              {"label": "Axar Patel", "v": 46, "text": "46 (55)", "hl": True}, {"label": "Naman Dhir", "v": 22, "text": "22 (31)"}, {"label": "Ishan Kishan", "v": 46, "text": "46 (58)", "hl": True}, {"label": "Arshdeep Singh", "v": 14, "text": "14 (4)"}, {"label": "Mohammed Siraj", "v": 14, "text": "14* (20)"}]}),
 S_("The powerplay was the problem. Thirty-seven for three off the first sixty balls. Seven balls in every ten were dots.",
    {"type": "lab_big", "kicker": "INDIA · POWERPLAY · OVERS 1 TO 10", "title": "Three down, almost nothing scored.", "value": 37, "suffix": " / 3", "label": "off 60 balls · 70% dot balls · 5% boundary balls", "color": "red"}),
 S_(f"A last-wicket flurry added twenty-six runs off the final ten balls, with two sixes from {arsh}. It lifted the total. But it moved India's chances by only seven points. They were still the underdogs.",
    {"type": "lab_big", "kicker": "INDIA · LAST-WICKET STAND", "title": "Twenty-six off ten balls.", "value": 26, "label": "183/9 to 209/10 · India's win probability +7 points (our model)", "color": "red", "word": "twenty-six"}),
 S_("New Zealand needed four point two runs an over, and they never got ahead of it. Four point one in the powerplay, three point eight through the middle overs. By the fortieth over, they were scoring three point nine and needed five and a half.",
    {"type": "lab_compare", "kicker": "NEW ZEALAND'S CHASE · SCORING v REQUIRED", "title": "Never ahead of the rate.", "a": tok("NZ", "SCORING RATE", "NZ"), "b": tok("IND", "REQUIRED RATE", "IND"),
     "rows": [["After 10 overs · 41/1", "4.10", "4.22", "b"], ["After 30 overs · 116/4", "3.87", "4.70", "b"], ["After 40 overs · 155/6", "3.88", "5.50", "b"]]}),
 S_("Here is India's chance of winning, over by over. Never above twenty-five per cent in the first twenty overs. Then the wickets: it climbs, falls back, and finally crosses fifty per cent for good at one fifty-eight for seven.",
    {"type": "lab_dots", "kicker": "INDIA'S WIN PROBABILITY DURING NZ'S CHASE · OUR MODEL", "title": "From 13% to 98%.", "domain": [0, 100], "ticks": [0, 50, 100], "tick_labels": False,
     "rows": [{"label": f"After over {c_['after_over']} · {c_['score']}", "v": round(100 * c_["india_wp"]), "text": f"{round(100 * c_['india_wp'])}%", "hl": c_["after_over"] == 40} for c_ in R["curve"] if c_["inning"] == 2 and c_["after_over"] in (5, 10, 20, 25, 30, 35, 40, 45)]}),
 S_(f"The biggest swing: over forty point four. {dhir}, in his second over, gets Mitchell Santner to hole out to {arsh}. Twenty-seven points, in one ball. Just over nine overs earlier, a double: {nabi} gets Bracewell, and the debutant {thakur} bowls Foxcroft next ball. Together, thirty-nine points.",
    {"type": "lab_dots", "kicker": "BIGGEST SWINGS · POINTS OF WIN PROBABILITY · OUR MODEL", "title": "Three wickets turned it.", "domain": [0, 30], "ticks": [0, 15, 30], "tick_labels": False,
     "rows": [{"label": "40.4 Santner c Arshdeep b Dhir", "v": 27, "text": "27", "hl": True}, {"label": "31.1 Foxcroft b Thakur", "v": 20, "text": "20", "hl": True}, {"label": "21.3 Allen b Siraj", "v": 19, "text": "19"}, {"label": "30.6 Bracewell c Dhir b Nabi", "v": 18, "text": "18", "hl": True}, {"label": "42.4 Clarke c Kishan b Arshdeep", "v": 14, "text": "14"}, {"label": "20.4 Kelly b Arshdeep", "v": 14, "text": "14"}]}),
 S_("Then the let-offs. New Zealand dropped अक्षर पटेल on two, and Shreyas Iyer on five. Those two batters scored sixty-one more runs. India dropped Foxcroft on five, and Bracewell on eight. They scored thirty-seven. A net twenty-four runs: more than the margin of twenty-two.".replace("अक्षर पटेल", axar).replace("Shreyas Iyer", iyer),
    {"type": "lab_compare", "kicker": "DROPPED CATCHES · RUNS SCORED AFTER THE LET-OFF", "title": "The drops were worth the match.", "a": tok("IND", "INDIA'S LET-OFFS", "IND"), "b": tok("NZ", "NEW ZEALAND'S LET-OFFS", "NZ"),
     "rows": [["First let-off", "44 · Axar, on 2", "26 · Foxcroft, on 5", "level"], ["Second let-off", "17 · Iyer, on 5", "11 · Bracewell, on 8", "level"], ["Runs after the let-offs", "61", "37", "a"]]}),
 S_(f"The hidden winner: {dhir}. Two overs, four runs, one wicket. By our measure, he was the second most valuable player of the match, behind {arsh}, the Player of the Match, who took three for thirty. And the hidden loser: Jacob Duffy, three wickets, but sixty runs in eight overs.",
    {"type": "lab_big", "kicker": "HIDDEN WINNER · WIN PROBABILITY ADDED · OUR MODEL", "title": "Naman Dhir's two overs.", "value": 26, "suffix": " POINTS", "label": "2-0-4-1 · the Santner wicket · second to Arshdeep Singh (+37) · hidden loser: Duffy 3/60 (-20)", "color": "red"}),
 S_("India leaned on pace: forty overs, at three point eight eight an over. New Zealand's seamers went at five point six four, but their two spinners, Santner and Bracewell, at four point one.",
    {"type": "lab_compare", "kicker": "PACE v SPIN · 5TH ODI", "title": "The attacks.", "a": tok("IND", "INDIA", "IND"), "b": tok("NZ", "NEW ZEALAND", "NZ"),
     "rows": [["Pace · overs", "40.0 (155/7)", "22.1 (125/6)", "level"], ["Pace · economy", "3.88", "5.64", "a"], ["Spin · economy", "3.92", "4.10", "a"]]}),
 S_(f"Two days earlier, on the same ground, New Zealand had scored three thirty-three, at six point six six an over. In the fifth, three point eight eight. Their powerplay: seven point two, then four point one. {arsh}'s ten overs cost fifty-five runs in the fourth, and thirty in the fifth.",
    {"type": "lab_compare", "kicker": "SAME GROUND, TWO DAYS APART · NZ BATTING", "title": "What changed at Bay Oval.", "a": tok("NZ", "4TH ODI", "NZ"), "b": tok("NZ", "5TH ODI", "NZ"),
     "rows": [["Run rate", "6.66", "3.88", "level"], ["Powerplay run rate", "7.20", "4.10", "level"], ["Dot balls", "47%", "61%", "level"], ["Arshdeep Singh, 10 overs", "55 runs, 1 wkt", "30 runs, 3 wkts", "b"]]}),
 S_("So how does a twenty-two per cent chance win? A collapse in the middle overs, two let-offs worth more than the margin, and an attack that never let New Zealand get going. Our model says that match goes the other way four times in five.",
    {"type": "lab_big_text", "kicker": "THE VERDICT", "lines": ["22% to win.", "[Won by 22 runs.]"]}),
 S_("Which moment turned it for you? Tell us in the comments, and follow for more from The Replay Room.", {"type": "cta", "lines": [{"t": "THE REPLAY ROOM"}, {"t": "EVERY BALL, DECODED", "c": "gold"}], "pill": "SUBSCRIBE FOR MORE"}),
]
short = [
 stage("India made two hundred and nine. Our model gave them twenty-two per cent to defend it. They won by twenty-two runs.",
       {"kind": "versus", "kicker": "5TH ODI · INDIA v NEW ZEALAND", "left": G("22%", "India's chance (our model)"), "right": G("22", "runs: the margin")}, [IND("celebrate", .3), NZ("dejected", .74)], cam="push", fx=["vignette", "spot", "confetti"], fx_at=.5),
 stage(f"India were thirty-seven for three after sixty balls, and bowled out for two hundred and nine. Then New Zealand needed four point two an over, and scored three point nine.",
       {"kind": "table", "kicker": "THE SETUP", "rows": [["India · powerplay", "37 / 3", "red"], ["India · all out", "209", "ink"], ["NZ · needed", "4.22 an over", "gold"], ["NZ · scored", "3.88 an over", "red"]]}, [IND("stance", .4)], cam="drift", fx=["vignette"]),
 stage(f"The turning point: Mitchell Santner holes out to {arsh} off {dhir}. Twenty-seven points of win probability in one ball. India never fell below fifty per cent again.",
       {"kind": "headline", "kicker": "OVER 40.4 · 158 FOR 7", "lines": [{"t": "27 POINTS."}, {"t": "ONE BALL.", "c": "gold"}]}, [IND("celebrate", .5, hit=None)], cam="push", fx=["vignette", "spot", "flash"]),
 stage("Then the drops. New Zealand put down two chances: those batters scored sixty-one more. India dropped two: thirty-seven. A net twenty-four runs, more than the margin.",
       {"kind": "versus", "kicker": "RUNS AFTER THE LET-OFF", "left": G("61", "after NZ's drops", "gold"), "right": G("37", "after India's drops", "ink")}, [IND("point", .3), NZ("dejected", .74)], cam="wide", fx=["vignette"]),
 stage(f"The hidden winner: {dhir}. Two overs, four runs, and the Santner wicket. Second most valuable player of the match, behind {arsh}.",
       {"kind": "bignum", "kicker": "NAMAN DHIR · 2-0-4-1", "label": "POINTS OF WIN PROBABILITY ADDED", "value": 26, "count_dur": .7, "color": "gold"}, [IND("raise", .5)], cam="pull", fx=["vignette", "sparks"]),
 stage(f"Two days earlier, on the same ground, New Zealand had scored three thirty-three. {arsh}'s ten overs cost fifty-five runs then. In the fifth, thirty runs and three wickets.",
       {"kind": "versus", "kicker": "BAY OVAL · NZ BATTING", "left": G("333", "4th ODI"), "right": G("187", "5th ODI")}, [IND("bowl", .62, dir=-1)], view="side", cam="push", fx=["vignette"]),
 {"vo": "Want the full breakdown? Subscribe to The Third Man on YouTube.", "scene": {"type": "cta", "lines": [{"t": "WANT THE FULL"}, {"t": "BREAKDOWN?", "c": "gold"}], "yt": {"label": "THE THIRD MAN", "handle": "@thethirdman_angle", "sub": "SUBSCRIBE · INSTAGRAM @thethirdman.angle", "bio": None}}},
]
reel = [short[0], short[1],
        stage("Here is India's chance, over by over, during the chase. Thirteen per cent after five overs. Sixteen after twenty. Fifty-eight after thirty-five. Eighty-one after forty-five.",
              {"kind": "table", "kicker": "INDIA'S WIN PROBABILITY · OUR MODEL", "rows": [["After 5 overs", "13%", "red"], ["After 20 overs", "16%", "red"], ["After 35 overs", "58%", "gold"], ["After 45 overs", "81%", "gold"]]}, [IND("stance", .4)], cam="drift", fx=["vignette"]),
        short[2],
        stage(f"Nine overs earlier, a double. {nabi} gets Bracewell caught, and the debutant {thakur} bowls Foxcroft with the very next ball. Thirty-nine points between them.",
              {"kind": "versus", "kicker": "OVERS 30.6 AND 31.1", "left": G("18", "Bracewell, c Dhir", "gold"), "right": G("20", "Foxcroft, b Thakur", "gold")}, [IND("bowl", .62, dir=-1)], view="side", cam="push", fx=["vignette", "shake"]),
        short[3], short[4],
        stage("India's seamers bowled forty overs at three point eight eight. New Zealand's seamers went at five point six four. Their spinners did better, at four point one.",
              {"kind": "table", "kicker": "ECONOMY · 5TH ODI", "rows": [["India pace", "3.88", "gold"], ["India spin", "3.92", "ink"], ["NZ pace", "5.64", "red"], ["NZ spin", "4.10", "ink"]]}, [IND("defend", .34)], view="side", cam="push", stumps=[.2, .93], fx=["vignette"]),
        short[5],
        stage("So how does a twenty-two per cent chance win? A collapse in the middle overs, two let-offs worth more than the margin, and a bowling attack that never let New Zealand get going.",
              {"kind": "headline", "kicker": "THE VERDICT", "lines": [{"t": "22% TO WIN."}, {"t": "WON BY 22.", "c": "gold"}]}, [IND("arms_wide", .5)], cam="wide", fx=["vignette", "spot", "confetti"], fx_at=.5),
        {"vo": "Which moment turned it for you? Tell us in the comments. For the full breakdown, follow The Third Man on YouTube. Link in bio.", "scene": {"type": "cta", "lines": [{"t": "FULL BREAKDOWN"}, {"t": "ON YOUTUBE", "c": "gold"}], "yt": {"label": "THE THIRD MAN", "handle": "YOUTUBE @thethirdman_angle", "bio": "LINK IN BIO"}}}]
SRC = ["Ball-by-ball: Cricbuzz full-commentary capture of the 5th ODI (match 161282), parsed into one row per delivery (data/series/nz_ind_2026); innings totals and individual figures checked against Wikipedia's match box ('Indian cricket team in New Zealand in 2026-27', citing Cricinfo) and Cricbuzz's own pace/spin summary line.",
       "Win probability, swings, 'win probability added' and the hidden winner: our own model, fitted on 1,719 men's 50-over ODIs in the Cricsheet archive (2009 onwards, no rain method), validated on held-out matches (accuracy 83%); an indication, not a fact. Drops: the runs a batter scored after a dropped chance (descriptive, not a counterfactual).",
       "4th ODI comparison: Cricbuzz capture of the 4th ODI, with an independent Cricinfo capture agreeing over by over. Figures: analysis/nz_ind_*.py, make_replay_5odi.py."]
DESC_L = ("India vs New Zealand, 5th ODI analysis: how India won at 22%. India made 209; our model gave New Zealand a 78% chance to chase it, and India won by 22 runs. The powerplay collapse, the 27-point turning point at 158/7, the drops worth more than the margin, "
          "the hidden winner (Naman Dhir) and what changed at Bay Oval in two days. Ball-by-ball data: Cricbuzz; win-probability model fitted on the Cricsheet archive (our own analysis).\n\n#INDvNZ #IndiaVsNewZealand #5thODI")
DESC_S = ("How India won the 5th ODI against New Zealand at 22%: 209 all out, a 27-point turning point, drops worth more than the margin, and the hidden winner. Cricbuzz ball-by-ball; our own model.\n\n#INDvNZ #5thODI #Shorts")
TAGS = ["India vs New Zealand", "India vs New Zealand 5th ODI", "IND vs NZ 5th ODI", "New Zealand vs India ODI", "Arshdeep Singh", "Naman Dhir", "Mitchell Santner", "Bay Oval", "cricket analysis", "The Replay Room", "The Third Man"]
spec = {"slug": "replay_5odi", "theme": "stadium", "theme_long": "lab", "captions": "v2", "captions_long": False, "series": "replay", "tag": "THE REPLAY ROOM", "tagsub": "EP. 3 · 5TH ODI · INDIA V NEW ZEALAND",
        "files": {"long": "x", "short": "x"}, "thumb": {"kicker": "5TH ODI · REPLAY ROOM", "lines": [{"t": "INDIA'S"}, {"t": "22% WIN", "c": "gold"}], "hero": "22%", "herosize": 360},
        "sources": SRC, "venue": {"time": "day", "crowd": [[25, 100, 200], [240, 240, 240], [20, 20, 20], [250, 150, 30]], "boards": [[25, 100, 200], [250, 150, 30]]}, "long": long, "short": short, "reel": reel, "lab_reel": [0, 3, 5, 7, 8, 9, 12],
        "yt": {"long": {"title": "India vs New Zealand - 5th ODI Analysis | How India Won at 22%", "description": DESC_L, "tags": TAGS}, "short": {"title": "How India Won at 22% | India vs New Zealand 5th ODI #Shorts", "description": DESC_S, "tags": TAGS}}}
c.save(spec)
voice_lint.fix_spec(spec)
json.dump(spec, open("specs/replay_5odi.json", "w"), ensure_ascii=False, indent=1)
w = lambda L: sum(len(x["vo"].split()) for x in L)
print(f"wrote specs/replay_5odi.json: long {w(long)} words / {len(long)} scenes, short {w(short)} words, reel {w(reel)} words")
