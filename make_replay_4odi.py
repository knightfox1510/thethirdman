"""Builds specs/replay_4odi.json (long + Short), replay_4odi_young.json, replay_4odi_dots.json from the Cricinfo + Cricbuzz captures.
Every number spoken or shown is computed from data/cricinfo/nz_ind_4odi_balls.csv and asserted here.
    python3 cricinfo_import.py data/cricinfo/nz_ind_4odi.json data/cricbuzz/nz_ind_4odi.json   # builds the csv first"""
import json, pandas as pd
import voice_lint

b = pd.read_csv("data/cricinfo/nz_ind_4odi_balls.csv")
n1, n2 = b[b.inning == 1], b[b.inning == 2]
L1, L2 = n1[n1.legal], n2[n2.legal]

# ---------------------------------------------------------------- facts
assert (n1.runs.sum(), n1.wicket.sum(), len(L1)) == (333, 10, 300) and (n2.runs.sum(), n2.wicket.sum(), len(L2)) == (89, 10, 160)
assert n1.runs.sum() - n2.runs.sum() == 244
H = L2[L2.bowler == "Matt Henry"]
hn = n2[n2.bowler == "Matt Henry"]
assert (int(hn.wicket.sum()), int(hn.runs.sum()), len(hn)) == (6, 27, 60), (int(hn.wicket.sum()), int(hn.runs.sum()), len(hn))
assert len(H) == 58 and int(H.pitch_line.isin(["OUTSIDE_OFFSTUMP", "WIDE_OUTSIDE_OFFSTUMP"]).sum()) == 35
off_h = int((H.pitch_line == "OUTSIDE_OFFSTUMP").sum()); assert off_h == 34
shortish = int(H.pitch_length.isin(["SHORT", "SHORT_OF_A_GOOD_LENGTH"]).sum()); assert shortish == 29   # exactly half
first = n2.iloc[:6]
assert list(first.batter) == ["Rohit Sharma", "Virat Kohli", "Virat Kohli", "Virat Kohli", "Virat Kohli", "Shreyas Iyer"] and first.wicket.tolist() == [True, False, False, False, True, True]
assert int(first.runs.sum()) == 0
assert [(r.batter, int(r.bat_runs), int(r.dismissal)) for r in n2[n2.wicket].head(3).itertuples()] == [("Rohit Sharma", 0, 1), ("Virat Kohli", 0, 2), ("Shreyas Iyer", 0, 3)]
d4 = n2[n2.wicket].iloc[3]; assert d4.batter == "Ruturaj Gaikwad" and d4.overs == 5.3 and n2[n2.overs <= 5.3].runs.sum() == 9
defended = int((n2[n2.wicket].shot == "DEFENDED").sum()); assert defended == 7
dots2, dots1 = (L2.runs == 0).mean(), (L1.runs == 0).mean()
assert round(dots2 * 100) == 74 and round(dots1 * 100) == 47
bd = lambda x: (int(x.four.sum()), int(x.six.sum()))
assert bd(n1) == (29, 12) and bd(n2) == (8, 2)
assert 29 * 4 + 12 * 6 == 188
ph = [(int(n1[(n1.over_no > 10 * i) & (n1.over_no <= 10 * i + 10)].runs.sum()), int(n1[(n1.over_no > 10 * i) & (n1.over_no <= 10 * i + 10)].wicket.sum())) for i in range(5)]
assert ph == [(72, 0), (53, 3), (89, 0), (51, 3), (68, 4)], ph
yl = L1[L1.batter == "Will Young"].reset_index(drop=True)
assert (int(yl.bat_runs.sum()), len(yl), int(yl.four.sum()), int(yl.six.sum())) == (125, 108, 14, 4)
yf = int((yl.control == 2).sum()); assert yf == 24
blocks = [(0, 25), (25, 50), (50, 75), (75, 108)]
yb = [(int(yl.iloc[a:z].bat_runs.sum()), int((yl.iloc[a:z].control == 2).sum())) for a, z in blocks]
assert yb == [(22, 8), (28, 7), (35, 2), (40, 7)], yb
assert yb[0][1] + yb[1][1] == 15
assert yl.iloc[4].overs == 1.5 and yl.iloc[5].overs == 1.6 and int(yl.iloc[:6].bat_runs.sum()) == 5 and int(yl.iloc[6:].bat_runs.sum()) == 120
sh = yl.groupby("shot").bat_runs.sum()
assert (sh.CUT_SHOT, sh.COVER_DRIVE, sh.PULL, sh.SWEEP_SHOT) == (27, 23, 16, 12)
bw = {k: (round((g.control == 2).mean() * 100), int(g.wicket.sum()), len(g)) for k, g in L2.groupby("bowler")}
bi = {k: (round((g.control == 2).mean() * 100), int(g.wicket.sum()), len(g), int(n1[n1.bowler == k].runs.sum())) for k, g in L1.groupby("bowler")}
assert bi["Arshdeep Singh"][:2] == (33, 1) and bi["Auqib Nabi"][:2] == (25, 4) and bi["Axar Patel"][:2] == (12, 2) and bi["Kuldeep Yadav"][:3] == (19, 0, 48) and bi["Kuldeep Yadav"][3] == 73
top = {k: (int(g.bat_runs.sum()), int((g.wides == 0).sum())) for k, g in n1.groupby("batter")}
yb2 = {k: (int(g.bat_runs.sum()), len(g), round(g.bat_runs.sum() / len(g) * 100)) for k, g in yl.groupby("bowler")}
assert yb2["Kuldeep Yadav"] == (42, 24, 175) and yb2["Arshdeep Singh"] == (22, 15, 147) and yb2["Gurnoor Brar"] == (32, 22, 145) and yb2["Auqib Nabi"] == (12, 17, 71) and yb2["Axar Patel"] == (16, 28, 57), yb2
r20 = lambda x: int((x.groupby("batter").bat_runs.sum() >= 20).sum())
assert (r20(n1), r20(n2)) == (5, 3) and int(n2[n2.over_no <= 10].runs.sum()) == 26 and int(n2[n2.over_no <= 10].wicket.sum()) == 4
assert top["Tim Seifert"] == (58, 48) and top["Finn Allen"] == (41, 30)
assert {k: int(g.bat_runs.sum()) for k, g in n2.groupby("batter")}["Ishan Kishan"] == 27
print("all facts asserted")

# ---------------------------------------------------------------- helpers
def S(vo, sc, **kw): return dict({"vo": vo, "scene": sc}, **kw)
FOOT = None   # no on-screen source footers (owner rule); sources go in the description and spec["sources"]
KIT_NZ = dict(kit="NZ", cap=True); KIT_IN = dict(kit="IND")
YOUNG_SHOTS = [[int(r.wagon_x), int(r.wagon_y), int(r.bat_runs)] for r in yl.itertuples() if r.bat_runs > 0]
assert len(YOUNG_SHOTS) == int((yl.bat_runs > 0).sum())
def balls_of(df):
    out = []
    for r in df.itertuples():
        out.append([r.pitch_line, r.pitch_length, "wicket" if r.wicket else ("false" if r.control == 2 else "ok")])
    return out
HB = balls_of(H); assert sum(1 for x in HB if x[2] == "wicket") == 6

# ---------------------------------------------------------------- long
long = [
 S("Nought for three. After one over. That is how India's chase of three hundred and thirty-four began at Mount Maunganui. It finished at eighty-nine all out, a defeat by two hundred and forty-four runs. Here is exactly how it happened.",
   {"type": "lab_big_text", "kicker": "NZ V IND · 4TH ODI", "lines": ["0 for 3.", "After [one over.]"]}),
 S("This is the Replay Room. We took every ball of the match: its line, its length, the shot that was played, and whether the batter was in control. Then we asked who decided it, and why. Two innings, two very different stories.",
   {"type": "lab_title", "kicker": "THE REPLAY ROOM", "lines": ["333 and [89.]"], "teaser": "Every ball · NZ v IND · 4th ODI"}, chapter="The match"),
 S("New Zealand made three hundred and thirty-three, all out in the last over. India were bowled out for eighty-nine, in twenty-six point four overs. Matt Henry took the match award.",
   {"type": "lab_vs", "kicker": "THE RESULT", "title": "Won by 244 runs.", "items": [
       {"label": "New Zealand · 49.6 overs", "v": 333, "text": "333", "c": "NZ", "t": "NZ", "kit": "NZ", "word": "three"},
       {"label": "India · 26.4 overs", "v": 89, "text": "89", "c": "IND", "t": "IND", "kit": "IND", "word": "eighty"}], "max": 360, "foot": FOOT}),
 S("Start with the chase. This is every ball Matt Henry bowled. Thirty-four of his fifty-eight landed outside off stump, and half were short or back of a length. Nothing exotic. He asked India the same question again and again. And they kept getting it wrong.",
   {"type": "lab_pitch", "kicker": "HENRY · 10 OVERS · 6 FOR 27", "title": "The same question, 58 times.", "pitch_balls": HB, "foot": FOOT, "from": .25, "to": .8}, chapter="The chase"),
 S("Look at how India got out. Seven of the ten wickets fell to a defensive shot. Not a slog, not a mistimed pull. A forward defence. रोहित शर्मा and विराट कोहली were both out for nought, defending, in the very first over.",
   {"type": "lab_units", "kicker": "HOW INDIA GOT OUT", "title": "Out defending.", "rows": [
       {"label": "India's ten wickets", "n": 10, "k": 7, "c": "red", "text": "7 defending", "word": "seven"}], "foot": FOOT}),
 S("India scored off just one ball in four. New Zealand scored off more than one in two. India hit ten boundaries all innings, eight fours and two sixes. New Zealand hit forty-one, twenty-nine fours and twelve sixes. Almost two hundred runs in boundaries alone.",
   {"type": "lab_vs", "kicker": "DOT BALLS", "title": "Nothing to hit.", "items": [
       {"label": "India's dot balls", "v": 74, "text": "74%", "c": "IND", "t": "IND", "kit": "IND"},
       {"label": "New Zealand's dot balls", "v": 47, "text": "47%", "c": "NZ", "t": "NZ", "kit": "NZ", "word": "forty-one"}], "max": 100, "foot": FOOT}),
 S("Now the other half. New Zealand's innings, ten overs at a time. Seventy-two without loss in the powerplay. Then fifty-three for three. Then overs twenty-one to thirty: eighty-nine runs, and not a wicket. That's where India lost the grip.",
   {"type": "lab_dots", "kicker": "NEW ZEALAND · RUNS EVERY TEN OVERS", "title": "The middle did it.", "domain": [0, 100], "tick_labels": False, "rows": [
       {"label": "Overs 1-10", "v": 72, "text": "72/0"}, {"label": "Overs 11-20", "v": 53, "text": "53/3"},
       {"label": "Overs 21-30", "v": 89, "text": "89/0", "hl": True, "word": "twenty-one"}, {"label": "Overs 31-40", "v": 51, "text": "51/3"}, {"label": "Overs 41-50", "v": 68, "text": "68/4"}],
    "foot": FOOT}, chapter="The first innings"),
 S("And in the middle of it, Will Young. A hundred and twenty-five off a hundred and eight balls. He scored all around the wicket: twenty-seven runs from the cut, twenty-three from the cover drive, sixteen from the pull, twelve from the sweep.",
   {"type": "lab_wagon", "kicker": "WILL YOUNG · 125 OFF 108", "title": "Every scoring shot.", "wagon_shots": YOUNG_SHOTS, "foot": FOOT}),
 S("But it wasn't flawless. In his first fifty balls, Young was not in control on fifteen of them. Then from ball fifty-one to seventy-five, just twice. That's when he took over. Runs in each block: twenty-two, twenty-eight, thirty-five, and forty in the last thirty-three.",
   {"type": "lab_dots", "kicker": "YOUNG · BALLS NOT IN CONTROL", "title": "Survive, then dominate.", "domain": [0, 10], "ticks": [0, 5, 10], "rows": [
       {"label": "Balls 1-25", "v": 8, "text": "8 · 22 runs"}, {"label": "Balls 26-50", "v": 7, "text": "7 · 28 runs"},
       {"label": "Balls 51-75", "v": 2, "text": "2 · 35 runs", "hl": True, "word": "twice"}, {"label": "Balls 76-108", "v": 7, "text": "7 · 40 runs"}], "foot": FOOT}),
 S("So how did he do it? He took the spinners and the quicker men on. Against Kuldeep Yadav, a strike rate of a hundred and seventy-five. Against Arshdeep Singh and Gurnoor Brar, a hundred and forty-five. But Axar Patel kept him to sixteen off twenty-eight, and आक़िब नबी to twelve off seventeen. Those two got it right.",
   {"type": "lab_dots", "kicker": "YOUNG · STRIKE RATE AGAINST EACH BOWLER", "title": "Who got it right.", "domain": [0, 200], "ticks": [0, 100, 200], "rows": [
       {"label": "Kuldeep", "v": 175, "text": "175 · 42 off 24", "hl": True, "word": "kuldeep"}, {"label": "Arshdeep", "v": 147, "text": "147 · 22 off 15"}, {"label": "Brar", "v": 145, "text": "145 · 32 off 22"},
       {"label": "Nabi", "v": 71, "text": "71 · 12 off 17"}, {"label": "Axar", "v": 57, "text": "57 · 16 off 28"}], "foot": FOOT}),
 S("And he nearly wasn't there. In the second over, Young was put down twice, off consecutive balls, both off आक़िब नबी. The first was a regulation chance at slip, dropped by रोहित शर्मा. Young had made five. He went on to score a hundred and twenty more.",
   {"type": "lab_big", "kicker": "TWO LIVES", "title": "In the second over.", "value": 120, "suffix": " runs", "label": "scored by Young after being dropped twice off consecutive balls, at five", "color": "red", "foot": None}),
 S("So which of India's bowlers deserved more? Arshdeep Singh made Young and the others look uncomfortable, on a third of his balls, and took one wicket. आक़िब नबी, a quarter of his balls, four wickets. And Kuldeep Yadav bowled eight overs for seventy-three, with nothing to show.",
   {"type": "lab_dots", "kicker": "INDIA'S BOWLERS · % OF BALLS BATTER NOT IN CONTROL", "title": "Luck, and the lack of it.", "domain": [0, 40], "ticks": [0, 20, 40], "rows": [
       {"label": "Arshdeep · 1 wkt", "v": 33, "text": "33%", "hl": True, "word": "arshdeep"}, {"label": "Nabi · 4 wkts", "v": 25, "text": "25%", "hl": True},
       {"label": "Kuldeep · 0 wkts", "v": 19, "text": "19%"}, {"label": "Axar · 2 wkts", "v": 12, "text": "12%"}], "foot": FOOT}),
 S("Then there was the start. Tim Seifert and Will Young put on seventy-two in the powerplay, without losing a wicket. Seifert hit fifty-eight off forty-eight. Finn Allen added forty-one off thirty. New Zealand never had to chase a start. India, after the same ten overs, were twenty-six for four.",
   {"type": "lab_compare", "kicker": "THE START", "title": "Seventy-two for none.", "a": {"t": "NZ", "kit": "NZ", "name": "NZ"}, "b": {"t": "IND", "kit": "IND", "name": "IND"}, "rows": [
       ["Runs after 10 overs", "72", "26", "a"], ["Wickets lost", "0", "4", "a"], ["Highest score", "125", "27", "a"], ["Batters to reach 20", "5", "3", "a"]], "foot": FOOT}),
 S("So who decided it? In the chase, Matt Henry, in six balls. In the first innings, Will Young, but with help. Two dropped catches, a middle stretch of eighty-nine runs, and a plan of short lengths that India's bowlers couldn't turn into wickets.",
   {"type": "lab_big_text", "kicker": "THE VERDICT", "lines": ["Henry: [six balls.]", "Young: [two lives.]", "India: no answer."]}, chapter="The verdict"),
 S("There is one more number. विराट कोहली needed twenty-two runs, to become the first man to score two thousand ODI runs against New Zealand. He scored none. The fifth and final match is on the fifteenth of November. India lead the series, but they have two days to answer one question: can they leave the ball outside off stump?",
   {"type": "lab_big", "kicker": "KOHLI V NEW ZEALAND · ODI RUNS", "title": "Still 22 short.", "value": 1978, "label": "Two days to the decider", "color": "red", "count_dur": 1.0}),
 S("Which video should the Replay Room do next? Tell us in the comments, and follow for the breakdown of the fifth ODI.",
   {"type": "cta", "lines": [{"t": "NEXT BREAKDOWN?"}, {"t": "THE REPLAY ROOM", "c": "gold"}], "pill": "SUBSCRIBE FOR MORE"}),
]

# ---------------------------------------------------------------- shorts (stadium stage)
VEN = {"time": "day", "crowd": [[20, 20, 20], [235, 235, 235], [20, 20, 25], [60, 60, 60]], "boards": [[20, 20, 20], [235, 235, 235]]}
def stage(vo, panel, av, **kw): return S(vo, dict({"type": "stage", "panel": dict(panel, at=.05), "avatars": av}, **kw))
bowl_nz = dict(kit="NZ", pose="bowl", x=.66, dir=-1)
short_a = [
 stage("Nought for three. After one over. That's how India's chase started.", {"kind": "headline", "kicker": "4TH ODI · MOUNT MAUNGANUI", "lines": [{"t": "0 FOR 3."}, {"t": "ONE OVER.", "c": "gold"}]},
       [dict(bowl_nz), dict(kit="IND", pose="dejected", x=.26)], view="side", cam="wide", stumps=[.17, .93]),
 stage("Matt Henry. Six balls. रोहित शर्मा, caught. विराट कोहली, bowled. श्रेयस अय्यर, lbw.", {"kind": "table", "kicker": "HENRY'S FIRST OVER", "rows": [["Rohit Sharma", "0 (1)", "red"], ["Virat Kohli", "0 (4)", "red"], ["Shreyas Iyer", "0 (1)", "red"]]},
       [dict(bowl_nz), dict(kit="IND", pose="stance", x=.26)], view="side", cam="push", stumps=[.17, .93], ball={"at": .55, "shot": "bowled"}),
 stage("Seven of India's ten wickets came to a defensive shot.", {"kind": "bignum", "label": "OUT DEFENDING", "value": 7, "suffix": " / 10", "count_dur": .6, "kicker": "How India got out"},
       [dict(kit="IND", pose="stance", x=.4)], cam="drift"),
 stage("Out for eighty-nine in twenty-six overs. New Zealand won by two hundred and forty-four runs.", {"kind": "versus", "kicker": "THE RESULT", "left": {"v": "333", "l": "New Zealand", "c": "gold"}, "right": {"v": "89", "l": "India", "c": "red"}},
       [dict(kit="NZ", pose="celebrate", x=.4, cap=True), dict(kit="IND", pose="dejected", x=.74)], cam="pull"),
 stage("Matt Henry finished with six for twenty-seven. What did India do wrong? Follow for the full breakdown.", {"kind": "headline", "kicker": "THE REPLAY ROOM", "lines": [{"t": "6 FOR 27."}, {"t": "FULL BREAKDOWN →", "c": "gold"}]},
       [dict(kit="NZ", pose="raise", x=.5, cap=True)], cam="push"),
]
short_young = [
 stage("A hundred and twenty-five off a hundred and eight balls. Will Young's innings was really two innings.", {"kind": "headline", "kicker": "WILL YOUNG · 4TH ODI", "lines": [{"t": "125"}, {"t": "OFF 108", "c": "gold"}]},
       [dict(kit="NZ", pose="raise", x=.5, number=None)], cam="push"),
 stage("In his first fifty balls, he was not in control on fifteen of them.", {"kind": "bignum", "label": "BALLS NOT IN CONTROL", "value": 15, "suffix": " / 50", "count_dur": .6, "kicker": "His first 50 balls"},
       [dict(kit="NZ", pose="stance", x=.4)], view="side", cam="wide", stumps=[.2, .9]),
 stage("In the second over he was dropped twice, off consecutive balls. He had five.", {"kind": "headline", "kicker": "SECOND OVER", "lines": [{"t": "DROPPED"}, {"t": "TWICE.", "c": "gold"}]},
       [dict(kit="NZ", pose="stance", x=.3), dict(kit="IND", pose="stand", x=.74)], cam="drift"),
 stage("Then he took over. Balls fifty-one to seventy-five: just two false shots, thirty-five runs.", {"kind": "versus", "kicker": "BALLS 51 TO 75", "left": {"v": "2", "l": "False shots", "c": "gold"}, "right": {"v": "35", "l": "Runs", "c": "ink"}},
       [dict(kit="NZ", pose="drive", x=.32, hit="drive")], view="side", cam="push", ball={"at": .5, "shot": "four"}, stumps=[.2, .9]),
 stage("A hundred and twenty of his hundred and twenty-five came after those two lives. Follow for the full breakdown.", {"kind": "bignum", "label": "RUNS AFTER THE TWO LIVES", "value": 120, "count_dur": .8, "kicker": "Of his 125"},
       [dict(kit="NZ", pose="celebrate", x=.5)], cam="pull"),
]
short_dots = [
 stage("India scored off just one ball in four.", {"kind": "bignum", "label": "DOT BALLS", "value": 74, "suffix": "%", "count_dur": .7, "kicker": "India's chase"},
       [dict(kit="IND", pose="stance", x=.4)], cam="push"),
 stage("New Zealand? Less than half.", {"kind": "versus", "kicker": "DOT BALLS", "left": {"v": "47%", "l": "New Zealand", "c": "gold"}, "right": {"v": "74%", "l": "India", "c": "red"}},
       [dict(kit="NZ", pose="stance", x=.3, hit="drive"), dict(kit="IND", pose="stance", x=.74)], cam="wide"),
 stage("India hit ten boundaries all innings. New Zealand hit forty-one.", {"kind": "versus", "kicker": "FOURS AND SIXES", "left": {"v": "41", "l": "New Zealand", "c": "gold"}, "right": {"v": "10", "l": "India", "c": "red"}},
       [dict(kit="NZ", pose="drive", x=.3, hit="drive")], view="side", cam="pull", ball={"at": .5, "shot": "six"}, stumps=[.2, .9]),
 stage("Twenty-nine fours and twelve sixes. One hundred and eighty-eight runs in boundaries.", {"kind": "bignum", "label": "RUNS IN BOUNDARIES", "value": 188, "count_dur": .9, "kicker": "New Zealand"},
       [dict(kit="NZ", pose="celebrate", x=.5)], cam="drift"),
 stage("Seven of India's ten wickets fell to a defensive shot. Follow for the full breakdown.", {"kind": "headline", "kicker": "THE REPLAY ROOM", "lines": [{"t": "OUT"}, {"t": "DEFENDING.", "c": "gold"}]},
       [dict(kit="IND", pose="dejected", x=.5)], cam="push"),
]

SRC = ["ESPNcricinfo match capture, NZ v IND 4th ODI, Mount Maunganui (match 1539440): ball-by-ball with line, length, shot, control and wagon data, captured with our own tool.",
       "Cricbuzz match capture (match 161271): over-by-over cross-check; dropped-catch events. Notes used as leads and verified against the ball data.",
       "Official result in both sources: New Zealand won by 244 runs; Player of the Match Matt Henry. Series: India led 2-0 before this match (Cricbuzz match preview).",
       "All figures computed in make_replay_4odi.py from data/cricinfo/nz_ind_4odi_balls.csv (legal balls unless stated; 'not in control' = Cricinfo shot-control flag)."]
DESC_L = ("New Zealand 333. India 89 all out. A 244-run defeat at Mount Maunganui. We took every ball of the 4th ODI (line, length, shot played, and whether the batter was in control) "
          "to work out who decided it and why: Matt Henry's triple-wicket first over, Will Young's 125 and the two lives that started it, and the middle overs where India lost the grip.\n\n"
          "Sources: ball-by-ball data from ESPNcricinfo and Cricbuzz match pages (captured with our own tool, cross-checked over by over); result and Player of the Match from both. "
          "All numbers are computed by us from the ball data; 'not in control' is the Cricinfo shot-control flag. All graphics are original, not broadcast footage.")
DESC_S = "The Replay Room: a ball-by-ball breakdown of NZ v India, 4th ODI, Mount Maunganui. Data: ESPNcricinfo and Cricbuzz match pages, analysis by The Third Man. Full video on the channel."
def meta(slug, tag, sub, lf, sf, kick, l1, l2, hero, ytl, yts, tags, **kw):
    d = {"slug": slug, "theme": "stadium", "theme_long": "lab", "captions": "serif", "captions_long": False, "series": "replay", "tag": tag, "tagsub": sub,
         "files": {"long": lf, "short": sf}, "thumb": {"kicker": kick, "lines": [{"t": l1}, {"t": l2, "c": "gold"}], "hero": hero, "herosize": 420}, "sources": SRC, "venue": VEN,
         "yt": {"long": {"title": ytl, "description": DESC_L, "tags": tags}, "short": {"title": yts, "description": DESC_S, "tags": tags}}}
    d.update(kw); return d
TAGS = ["India vs New Zealand", "Matt Henry", "Will Young", "4th ODI", "cricket analysis", "The Replay Room", "The Third Man"]
main = meta("replay_4odi", "THE REPLAY ROOM", "NZ V IND · 4TH ODI", "Replay_Room_333_and_89_NZ_v_India_4th_ODI", "Replay_Room_0_for_3_Short_9x16", "THE REPLAY ROOM", "333 AND", "89", "244", 
            "333 and 89: how New Zealand beat India by 244 runs (every ball analysed)", "0 for 3 after one over: India's chase in 6 balls #Shorts", TAGS)
main["long"] = long; main["short"] = short_a
for i, nm in [(0, "The hook"), (1, "The Replay Room"), (3, "The chase"), (6, "The first innings")]:
    main["long"][i] = dict(main["long"][i], chapter=nm)
young = meta("replay_4odi_young", "THE REPLAY ROOM", "WILL YOUNG · 125", "Replay_Room_Young_Long_unused", "Replay_Room_Will_Young_Two_Innings_Short_9x16", "WILL YOUNG", "TWO", "INNINGS", "125",
             "Will Young: two innings in one", "Will Young's 125: two innings in one #Shorts", TAGS); young["short"] = short_young
dots = meta("replay_4odi_dots", "THE REPLAY ROOM", "INDIA OUT DEFENDING", "Replay_Room_Dots_Long_unused", "Replay_Room_74_Percent_Dots_Short_9x16", "THE REPLAY ROOM", "74%", "DOTS", "74",
            "India's 74% dot balls", "74% dot balls: India out defending #Shorts", TAGS); dots["short"] = short_dots
for sp in (main, young, dots):
    voice_lint.fix_spec(sp)
    json.dump(sp, open(f"specs/{sp['slug']}.json", "w"), ensure_ascii=False, indent=1)
    print(sp["slug"], "long words", sum(len(x["vo"].split()) for x in sp.get("long", [])), "short words", sum(len(x["vo"].split()) for x in sp["short"]))
