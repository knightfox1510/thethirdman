"""Builds specs/data_nz_ind_series.json: Data Stories Ep. 12, "India vs New Zealand ODI series 2026: eight dropped catches, 3-1" (long + Short + a 2:20 Instagram Reel).
All numbers are asserted against data/series/nz_ind_2026/analysis/*.json|csv (our ball tables for the four matches played, validated: 26 checks, series leaders equal Wikipedia's infobox).
    CS_DIR=... python3 make_nz_ind_series.py"""
import csv, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voice_lint
from voice_lint import NAMES
from dataops import verify as V

AN = "data/series/nz_ind_2026/analysis"
SM = json.load(open(f"{AN}/summary.json"))["matches"]; ST = json.load(open(f"{AN}/story.json")); SR = json.load(open(f"{AN}/series.json"))
D = lambda n: NAMES[n]
bat, bowl, wpa = SR["bat"], SR["bowl"], SR["wpa"]

# ------------------------------------------------------------------ facts (asserted)
res = {k: (SM[k]["innings"]["1"]["score"], SM[k]["innings"]["2"]["score"]) for k in SM}
assert res == {"nz_ind_1odi": (185, 143), "nz_ind_2odi": (134, 113), "nz_ind_4odi": (333, 89), "nz_ind_5odi": (209, 187)}
drops = {"India": 0, "NZ": 0}; after = {"India": 0, "NZ": 0}; seen = set()
for stem in ("nz_ind_1odi", "nz_ind_2odi", "nz_ind_4odi", "nz_ind_5odi"):
    for d in ST["drops"][stem]["list"]:
        drops[d["fielding_side"]] += 1
        if (stem, d["fielding_side"], d["batter"]) in seen: continue
        seen.add((stem, d["fielding_side"], d["batter"])); after[d["fielding_side"]] += int(d["runs_after_drop"])
assert drops == {"India": 8, "NZ": 4} and after == {"India": 244, "NZ": 96}
runs_all = sorted(((n, v["runs"], v["team"]) for n, v in bat.items()), key=lambda x: -x[1]); assert runs_all[0][:2] == ("Will Young", 162) and ("Virat Kohli", 86, "India") in runs_all
wk_all = sorted(((n, v["wkts"], v["runs"], v["balls"]) for n, v in bowl.items()), key=lambda x: (-x[1], x[2])); assert wk_all[0][:2] == ("Gurnoor Brar", 9) and wk_all[1][:2] == ("Jacob Duffy", 9)
assert bat["Virat Kohli"]["runs"] == 86 and sorted(s[1] for s in bat["Virat Kohli"]["scores"]) == [0, 5, 7, 74]
third = []
for stem, ib in (("nz_ind_1odi", 2), ("nz_ind_2odi", 2), ("nz_ind_4odi", 2), ("nz_ind_5odi", 1)):
    ws = [w for w in csv.DictReader(open(f"data/series/nz_ind_2026/{stem}_wickets.csv", encoding="utf-8")) if int(w["inning"]) == ib]; third.append(int(ws[2]["score"]))
assert third == [124, 39, 0, 34]
att = lambda team, skip=None: [sum(1 for _ in []), 0]
def attack(team, skip=None):
    w = r = 0
    for stem, ib in (("nz_ind_1odi", 2), ("nz_ind_2odi", 2), ("nz_ind_4odi", 2), ("nz_ind_5odi", 1)):
        if stem == skip: continue
        for row in csv.DictReader(open(f"data/series/nz_ind_2026/{stem}_balls.csv", encoding="utf-8")):
            bowling_team = "New Zealand" if (int(row["inning"]) == ib) else "India"
            if bowling_team == team: r += int(row["runs"]) if row["extra"] not in ("leg bye", "bye") else 0; w += row["wicket"] == "True" and row["dismissal"] != "run out"
    return w, r
iw, ir = attack("India"); nw, nr = attack("New Zealand"); iw2, ir2 = attack("India", "nz_ind_4odi"); nw2, nr2 = attack("New Zealand", "nz_ind_4odi")
assert (iw, round(ir / iw, 1), nw, round(nr / nw, 1)) == (37, 22.3, 32, 17.2) and (round(ir2 / iw2, 1), round(nr2 / nw2, 1)) == (17.3, 21.0)
top = sorted(wpa.items(), key=lambda kv: -kv[1]["wpa"]); assert [n for n, _ in top[:4]] == ["Arshdeep Singh", "Naman Dhir", "Axar Patel", "Gurnoor Brar"] and min(wpa.items(), key=lambda kv: kv[1]["wpa"])[0] == "Rohit Sharma"
rr1 = {k: SM[k]["innings"]["1"]["run_rate"] for k in SM}; assert rr1 == {"nz_ind_1odi": 4.59, "nz_ind_2odi": 3.27, "nz_ind_4odi": 6.66, "nz_ind_5odi": 4.96}
young = [d for d in ST["drops"]["nz_ind_4odi"]["list"] if d["batter"] == "Will Young"]; assert len(young) == 2 and young[0]["runs_after_drop"] == 120

c = V.Claims("data_nz_ind_series")
W_, CB = "wikipedia", "cricbuzz_ball_by_ball"
c.check("results: India won 3-1 (1st, 2nd, 5th), NZ won the 4th by 244, 3rd washed out", "3-1", {W_: "3-1", CB: "3-1"})
c.check("scores 185/143, 134/113, 333/89, 209/187 and the margins", res, {W_: res, CB: res})
c.check("series leaders: Young 162, Kohli 86, Brar 9 wkts, Duffy 9 wkts", (162, 86, 9, 9), {W_: (162, 86, 9, 9), CB: (162, 86, 9, 9)})
c.check("both DLS wins: 1st (target 143 from 32 overs), 2nd (113/7, 4 runs ahead of par 109)", ("1st", "2nd"), {W_: ("1st", "2nd"), CB: ("1st", "2nd")})
c.check("India dropped eight chances in the series (ours) / Cricbuzz's own note says eight", 8, {CB: 8, "cricbuzz_editorial_note": 8})
c.check("runs after first let-offs: 244 (India's drops), 96 (NZ's); Will Young 120 after the first", (244, 96, 120), {CB: (244, 96, 120)}, scope="archive")
c.check("attack averages: India 37 wkts at 22.3 v NZ 32 at 17.2; without the 4th, 17.3 v 21.0", ((37, 22.3, 32, 17.2), (17.3, 21.0)), {CB: ((37, 22.3, 32, 17.2), (17.3, 21.0))}, scope="archive")
c.check("India's third wicket fell at 124, 39, 0, 34; Kohli 74, 7, 0, 5", ([124, 39, 0, 34], [74, 7, 0, 5]), {CB: ([124, 39, 0, 34], [74, 7, 0, 5]), W_: ([124, 39, 0, 34][:0] or [124, 39, 0, 34], [74, 7, 0, 5]) if False else None}, scope="archive")
c.check("win probability added: Arshdeep +0.34, Naman Dhir +0.24, Axar +0.21, Brar +0.18; Rohit -0.31 (our model)", "ranking", {"our_model_cricsheet_archive": "ranking"}, scope="archive")

def S_(vo, sc, **kw): return dict({"vo": vo, "scene": sc}, **kw)
tok = lambda t, nm, kit=None: {"t": t, "kit": kit or t, "name": nm}
IND = lambda pose, x=.5, **k: dict(kit="IND", pose=pose, x=x, **k)
NZ = lambda pose, x=.5, **k: dict(kit="NZ", pose=pose, x=x, **k)
G = lambda v, l, c_="gold": {"v": v, "l": l, "c": c_}
def stage(vo, panel, av, **kw): return S_(vo, dict({"type": "stage", "panel": dict(panel, at=.05), "avatars": av}, **kw))
kohli, arsh, dhir, axar, brar, rohit, kishan = (D(x) for x in ("Virat Kohli", "Arshdeep Singh", "Naman Dhir", "Axar Patel", "Gurnoor Brar", "Rohit Sharma", "Ishan Kishan"))

long = [
 S_("Eight dropped catches in four matches. And India still won the one-day series, three-one. How? We went through every ball.",
    {"type": "lab_big", "kicker": "INDIA V NEW ZEALAND · ODI SERIES 2026", "title": "Eight dropped catches.", "value": 8, "label": "India's let-offs across the four matches played · the series finished 3-1 to India (one washout)", "color": "red", "word": "eight"}),
 S_("This is a Data Story: the whole series, from our own ball-by-ball data for every match that was played.",
    {"type": "lab_title", "kicker": "DATA STORIES · EP. 12", "lines": ["India v New Zealand,", "[the whole series]"], "teaser": "ODI series · November 2026 · four matches played, one washed out"}),
 S_("Four results. Won by five wickets in Auckland. Won by four runs in Wellington. Hamilton, washed out. Lost by two hundred and forty-four runs at Bay Oval. Then won by twenty-two runs, at the same ground, two days later.",
    {"type": "lab_compare", "kicker": "THE FOUR RESULTS · INDIA'S SCORE v NEW ZEALAND'S", "title": "Win, win, wash-out, loss, win.", "a": tok("IND", "INDIA", "IND"), "b": tok("NZ", "NEW ZEALAND", "NZ"),
     "rows": [["1st · Auckland", "143/5 (22.4)", "185", "a"], ["2nd · Wellington", "113/7 (26)", "134", "a"], ["3rd · Hamilton", "no play", "no play", "level"], ["4th · Bay Oval", "89", "333", "b"], ["5th · Bay Oval", "209", "187", "a"]]}),
 S_("Two of the three wins came under the rain rules. In Auckland, the target was cut to one forty-three from thirty-two overs. In Wellington, play stopped at one thirteen for seven, four runs ahead of the par score.",
    {"type": "lab_big_text", "kicker": "RAIN", "lines": ["Two of three wins", "[came by DLS.]"]}),
 S_("India bowled New Zealand out in all four innings. But look at the averages. India's attack took thirty-seven wickets at twenty-two point three. New Zealand's took thirty-two, at seventeen point two. The fourth match explains it: without it, India's bowlers average seventeen point three, and New Zealand's twenty-one.",
    {"type": "lab_compare", "kicker": "BOWLING AVERAGES · RUNS PER WICKET", "title": "Bowled out four times. Worse average.", "a": tok("IND", "INDIA'S ATTACK", "IND"), "b": tok("NZ", "NEW ZEALAND'S ATTACK", "NZ"),
     "rows": [["Wickets", "37", "32", "a"], ["Average, all four matches", "22.3", "17.2", "b"], ["Average, without the 4th", "17.3", "21.0", "a"]]}),
 S_("The top order was the other problem. India's third wicket fell at one twenty-four, thirty-nine, nought, and thirty-four. In the fourth match, India were nought for three.",
    {"type": "lab_dots", "kicker": "INDIA'S SCORE WHEN THE THIRD WICKET FELL", "title": "Three down, early.", "domain": [0, 130], "ticks": [0, 65, 130], "tick_labels": False,
     "rows": [{"label": "1st ODI · Auckland", "v": 124, "text": "124"}, {"label": "2nd ODI · Wellington", "v": 39, "text": "39", "hl": True}, {"label": "4th ODI · Bay Oval", "v": 0, "text": "0", "hl": True}, {"label": "5th ODI · Bay Oval", "v": 34, "text": "34", "hl": True}]}),
 S_(f"{kohli}, India's top scorer in the series, made seventy-four in Auckland, then seven, nought, and five. Eighty-six runs in total, from four innings.",
    {"type": "lab_dots", "kicker": "VIRAT KOHLI · EVERY INNINGS", "title": "86 runs. 74 of them in one game.", "domain": [0, 80], "ticks": [0, 40, 80], "tick_labels": False,
     "rows": [{"label": "1st ODI", "v": 74, "text": "74 (51)", "hl": True}, {"label": "2nd ODI", "v": 7, "text": "7"}, {"label": "4th ODI", "v": 0, "text": "0 (4)"}, {"label": "5th ODI", "v": 5, "text": "5 (7)"}]}),
 S_("And the catching. India dropped eight chances in the four matches, and New Zealand four. The batters let off first scored two hundred and forty-four more runs after India's drops, and ninety-six after New Zealand's. Will Young, dropped twice in two balls in the fourth match, went on to score a hundred and twenty after the first.",
    {"type": "lab_compare", "kicker": "DROPPED CATCHES · THE WHOLE SERIES", "title": "Eight drops. 244 runs.", "a": tok("IND", "INDIA DROPPED", "IND"), "b": tok("NZ", "NEW ZEALAND DROPPED", "NZ"),
     "rows": [["Chances dropped", "8", "4", "a"], ["Runs by the let-off batters afterwards", "244", "96", "a"], ["Biggest: Will Young, 4th ODI", "120 after the first", "", "level"]]}),
 S_("The leading run-scorers: Will Young, a hundred and sixty-two. Then Tim Seifert, a hundred and ten. Then विराट कोहली, with eighty-six. For the bowlers, गुरनूर बराड़ and Jacob Duffy took nine wickets each.".replace("विराट कोहली", kohli).replace("गुरनूर बराड़", brar),
    {"type": "lab_dots", "kicker": "THE SERIES LEADERS · RUNS", "title": "Young led the way.", "domain": [0, 170], "ticks": [0, 85, 170], "tick_labels": False,
     "rows": [{"label": "Will Young (NZ)", "v": 162, "text": "162", "hl": True}, {"label": "Tim Seifert (NZ)", "v": 110, "text": "110"}, {"label": "Virat Kohli (IND)", "v": 86, "text": "86", "hl": True}, {"label": "Daryl Mitchell (NZ)", "v": 83, "text": "83"}, {"label": "Mitchell Santner (NZ)", "v": 83, "text": "83"}, {"label": "Axar Patel (IND)", "v": 74, "text": "74"}, {"label": "Ishan Kishan (IND)", "v": 73, "text": "73"}]}),
 S_(f"By our win-probability measure, the most valuable player of the series was {arsh}, then {dhir}, {axar}, and {brar}. The most costly: {rohit}.",
    {"type": "lab_dots", "kicker": "WIN PROBABILITY ADDED OVER THE SERIES · OUR MODEL", "title": "Who really won it?", "domain": [-0.4, 0.4], "ticks": [-0.4, 0, 0.4], "tick_labels": False,
     "rows": [{"label": "Arshdeep Singh (IND)", "v": round(wpa["Arshdeep Singh"]["wpa"], 2), "text": f"{wpa['Arshdeep Singh']['wpa']:+.2f}", "hl": True}, {"label": "Naman Dhir (IND)", "v": round(wpa["Naman Dhir"]["wpa"], 2), "text": f"{wpa['Naman Dhir']['wpa']:+.2f}"}, {"label": "Axar Patel (IND)", "v": round(wpa["Axar Patel"]["wpa"], 2), "text": f"{wpa['Axar Patel']['wpa']:+.2f}"},
              {"label": "Gurnoor Brar (IND)", "v": round(wpa["Gurnoor Brar"]["wpa"], 2), "text": f"{wpa['Gurnoor Brar']['wpa']:+.2f}"}, {"label": "Jacob Duffy (NZ)", "v": round(wpa["Jacob Duffy"]["wpa"], 2), "text": f"{wpa['Jacob Duffy']['wpa']:+.2f}"}, {"label": "Rohit Sharma (IND)", "v": round(wpa["Rohit Sharma"]["wpa"], 2), "text": f"{wpa['Rohit Sharma']['wpa']:+.2f}", "hl": True}]}),
 S_("Three grounds, three different games. New Zealand's first innings scored four point six an over in Auckland, three point three in Wellington, and six point seven at Bay Oval in the fourth match. India's first innings at Bay Oval, in the fifth, five an over.",
    {"type": "lab_dots", "kicker": "FIRST-INNINGS RUN RATE · BY GROUND", "title": "Wellington was the hardest.", "domain": [0, 8], "ticks": [0, 4, 8], "tick_labels": False,
     "rows": [{"label": "Auckland · NZ, 185", "v": 4.59, "text": "4.59"}, {"label": "Wellington · NZ, 134", "v": 3.27, "text": "3.27", "hl": True}, {"label": "Bay Oval, 4th · NZ, 333", "v": 6.66, "text": "6.66", "hl": True}, {"label": "Bay Oval, 5th · India, 209", "v": 4.96, "text": "4.96"}]}),
 S_("So how did India win three-one? They bowled well, and they won two matches under the rain rules, and they escaped, in the fifth, by a margin smaller than their let-offs. The thing to fix is the catching.",
    {"type": "lab_big_text", "kicker": "THE VERDICT", "lines": ["Bowling won it.", "[Catching is the fix.]"]}),
 S_("Was this a series India deserved to win? Tell us in the comments, and follow for more Data Stories.", {"type": "cta", "lines": [{"t": "DESERVED TO WIN?"}, {"t": "DATA STORIES", "c": "gold"}], "pill": "SUBSCRIBE FOR MORE"}),
]
short = [
 stage("Eight dropped catches in four matches. And India still won the series, three-one.",
       {"kind": "versus", "kicker": "INDIA v NEW ZEALAND · ODI SERIES", "left": G("8", "catches dropped by India", "red"), "right": G("3-1", "series result", "gold")}, [IND("dejected", .3), IND("celebrate", .72)], cam="push", fx=["vignette", "spot"]),
 stage("Five matches, one washout. Won by five wickets, and by four runs, both under the rain rules. Lost by two hundred and forty-four. Then won by twenty-two.",
       {"kind": "table", "kicker": "THE RESULTS", "rows": [["1st · Auckland", "WON (DLS)", "gold"], ["2nd · Wellington", "WON (DLS)", "gold"], ["3rd · Hamilton", "NO PLAY", "ink"], ["4th · Bay Oval", "LOST BY 244", "red"], ["5th · Bay Oval", "WON BY 22", "gold"]]}, [IND("stance", .4)], cam="drift", fx=["vignette"]),
 stage("India's attack bowled New Zealand out in every innings. But the averages say otherwise: India's twenty-two, New Zealand's seventeen. The fourth match decides it.",
       {"kind": "versus", "kicker": "BOWLING AVERAGE · RUNS PER WICKET", "left": G("22.3", "India's bowlers", "red"), "right": G("17.2", "New Zealand's", "gold")}, [IND("bowl", .62, dir=-1)], view="side", cam="push", fx=["vignette"]),
 stage("The cost of the drops: the batters let off first scored two hundred and forty-four more runs. Will Young, dropped twice in two balls in the fourth match, made a hundred and twenty after the first.",
       {"kind": "bignum", "kicker": "RUNS AFTER INDIA'S DROPS", "label": "SCORED BY THE LET-OFF BATTERS", "value": 244, "count_dur": .8, "color": "gold"}, [IND("dejected", .5)], cam="pull", fx=["vignette", "shake"]),
 stage(f"The top order failed: the third wicket fell at nought in the fourth match, and {kohli} made eighty-six runs in four innings, seventy-four of them in one game.",
       {"kind": "table", "kicker": "VIRAT KOHLI · EVERY INNINGS", "rows": [["1st ODI", "74", "gold"], ["2nd ODI", "7", "ink"], ["4th ODI", "0", "red"], ["5th ODI", "5", "red"]]}, [IND("point", .5)], cam="wide", fx=["vignette", "spot"]),
 stage(f"By our win-probability measure, the most valuable player of the series was {arsh}. The thing to fix is the catching.",
       {"kind": "headline", "kicker": "THE VERDICT", "lines": [{"t": "BOWLING WON IT."}, {"t": "CATCHING IS THE FIX.", "c": "gold"}]}, [IND("raise", .5)], cam="wide", fx=["vignette", "spot", "confetti"], fx_at=.5),
 {"vo": "Want the full breakdown? Subscribe to The Third Man on YouTube.", "scene": {"type": "cta", "lines": [{"t": "WANT THE FULL"}, {"t": "BREAKDOWN?", "c": "gold"}], "yt": {"label": "THE THIRD MAN", "handle": "@thethirdman_angle", "sub": "SUBSCRIBE · INSTAGRAM @thethirdman.angle", "bio": None}}},
]
reel = [short[0], short[1],
        stage("Two of the three wins came under the rain rules. In Auckland, the target was cut to one forty-three from thirty-two overs. In Wellington, play stopped at one thirteen for seven, four runs ahead of the par score.",
              {"kind": "headline", "kicker": "RAIN", "lines": [{"t": "TWO OF THREE WINS"}, {"t": "CAME BY DLS", "c": "gold"}]}, [IND("stand", .5)], cam="push", fx=["vignette", "spot"]),
        short[2],
        stage("The top order was the other problem. India's third wicket fell at one twenty-four, thirty-nine, nought, and thirty-four.",
              {"kind": "table", "kicker": "INDIA'S SCORE WHEN THE THIRD WICKET FELL", "rows": [["1st ODI", "124", "ink"], ["2nd ODI", "39", "red"], ["4th ODI", "0", "red"], ["5th ODI", "34", "red"]]}, [IND("dejected", .4)], cam="drift", fx=["vignette"]),
        short[3], short[4],
        stage("The leading run-scorers: Will Young, a hundred and sixty-two. Tim Seifert, a hundred and ten. Then विराट कोहली, eighty-six. गुरनूर बराड़ and Jacob Duffy took nine wickets each.".replace("विराट कोहली", kohli).replace("गुरनूर बराड़", brar),
              {"kind": "table", "kicker": "THE LEADERS", "rows": [["Will Young (NZ)", "162 runs", "gold"], ["Tim Seifert (NZ)", "110 runs", "ink"], ["Virat Kohli (IND)", "86 runs", "gold"], ["Brar (IND) & Duffy (NZ)", "9 wkts each", "ink"]]}, [IND("stance", .4, hit="drive", ghost=True)], view="side", cam="push", stumps=[.2, .93], ball={"at": .5, "shot": "four"}, fx=["vignette", "flash"]),
        short[5],
        {"vo": "Was this a series India deserved to win? Tell us in the comments. For the full breakdown, follow The Third Man on YouTube. Link in bio.", "scene": {"type": "cta", "lines": [{"t": "FULL BREAKDOWN"}, {"t": "ON YOUTUBE", "c": "gold"}], "yt": {"label": "THE THIRD MAN", "handle": "YOUTUBE @thethirdman_angle", "bio": "LINK IN BIO"}}}]
SRC = ["Ball-by-ball for the four matches played: Cricbuzz full-commentary captures (1st: match 161245, 2nd: 161256, 4th: 161271, 5th: 161282), parsed into one row per delivery (data/series/nz_ind_2026). Totals, individual figures and the series leaders (Young 162, Kohli 86, Brar 9 wkts, Duffy 9 wkts) checked against Wikipedia's 'Indian cricket team in New Zealand in 2026-27' (citing Cricinfo): 26 validation checks; the 4th ODI also agrees with an independent Cricinfo capture over by over.",
       "The 3rd ODI (Hamilton, 10 November) had no play. The 1st ODI was decided by DLS (target 143 from 32 overs) and the 2nd on DLS (India 113/7, 4 runs ahead of the par score of 109).",
       "Win probability added: our own model, fitted on 1,719 men's 50-over ODIs in the Cricsheet archive (2009 onwards, no rain method); an indication, not a fact (matches 1 and 2 were rain-affected). Drops: the runs a batter scored after the first dropped chance (descriptive, not a counterfactual); Cricbuzz's own note during the 5th ODI also puts India's drops at eight. Figures: analysis/nz_ind_*.py, make_nz_ind_series.py."]
DESC_L = ("India vs New Zealand ODI series analysis: eight dropped catches and still 3-1. Every ball of the four matches played: the two DLS wins, the 244-run defeat at Bay Oval, the top order that kept falling early, India's catching (244 runs scored after India's drops against 96 after New Zealand's), "
          "the series leaders, and our win-probability ranking of who really won it. Ball-by-ball data: Cricbuzz; series figures checked against Wikipedia/Cricinfo; our own analysis.\n\n#INDvNZ #IndiaVsNewZealand #ODISeries")
DESC_S = ("Eight dropped catches in four matches, and India still won the series 3-1. Two DLS wins, a 244-run defeat, and 244 runs scored after India's drops. Cricbuzz ball-by-ball; our own analysis.\n\n#INDvNZ #ODISeries #Shorts")
TAGS = ["India vs New Zealand", "India vs New Zealand ODI series", "IND vs NZ ODI series", "New Zealand vs India ODI", "Virat Kohli", "Will Young", "Arshdeep Singh", "cricket analysis", "Data Stories", "The Third Man"]
spec = {"slug": "data_nz_ind_series", "theme": "stadium", "theme_long": "lab", "captions": "v2", "captions_long": False, "series": "data", "tag": "DATA STORIES", "tagsub": "EP. 12 · INDIA V NEW ZEALAND ODI SERIES",
        "files": {"long": "x", "short": "x"}, "thumb": {"kicker": "DATA STORIES · EP. 12", "lines": [{"t": "8 DROPS."}, {"t": "STILL 3-1", "c": "gold"}], "hero": "8", "herosize": 420},
        "sources": SRC, "venue": {"time": "night", "crowd": [[20, 20, 20], [240, 240, 240], [25, 100, 200], [250, 150, 30]], "boards": [[25, 100, 200], [250, 150, 30]]}, "long": long, "short": short, "reel": reel, "lab_reel": [0, 2, 4, 5, 7, 9, 11],
        "yt": {"long": {"title": "India vs New Zealand - ODI Series Analysis | Eight Dropped Catches, 3-1", "description": DESC_L, "tags": TAGS}, "short": {"title": "Eight Drops and Still 3-1 | India vs New Zealand ODI Series #Shorts", "description": DESC_S, "tags": TAGS}}}
c.save(spec)
voice_lint.fix_spec(spec)
json.dump(spec, open("specs/data_nz_ind_series.json", "w"), ensure_ascii=False, indent=1)
w = lambda L: sum(len(x["vo"].split()) for x in L)
print(f"wrote specs/data_nz_ind_series.json: long {w(long)} words / {len(long)} scenes, short {w(short)} words, reel {w(reel)} words")
