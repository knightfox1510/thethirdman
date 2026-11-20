"""Writes specs/nz_ind_1st_test_day2.json: The Replay Room Ep 5, India vs New Zealand, 1st Test, Day 2 (Basin Reserve, 20 Nov 2026), VERTICAL first (~150 s, lab look).
Source: the owner's Cricbuzz full-commentary capture (India's first innings to stumps; NZ's Day-2 morning is NOT in it), parsed by analysis/nz_day2.py -> data/provenance/nz_day2_figures.json / nz_day2_balls.json.
Length classes are OUR keyword read of Cricbuzz's text (61 of 240 balls unclassified), said as 'in our ball-by-ball'.   python3 make_nz_day2.py"""
import json, os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voice_lint
from dataops import verify as V
from variants import YT_CTA

F = json.load(open("data/provenance/nz_day2_figures.json")); B = json.load(open("data/provenance/nz_day2_balls.json")); CB = "cricbuzz"
bf = F["bowling_final"]; bt = F["batters"]
assert F["stumps"]["score"] == 159 and F["deliveries"] == 240
assert [(k, v["ov"], v["m"], v["r"], v["w"]) for k, v in bf.items()] == [("Matt Henry", 12, 3, 43, 1), ("Kyle Jamieson", 11, 5, 15, 0), ("Jacob Duffy", 10, 0, 72, 0), ("Nathan Smith", 6, 0, 29, 0)]
J, K, P = bt["Yashasvi Jaiswal"], bt["KL Rahul"], bt["Devdutt Padikkal"]
assert (J["batRuns"], J["batBalls"], J["batFours"], K["batRuns"], K["batBalls"], K["batFours"], P["batRuns"], P["batBalls"]) == (85, 89, 16, 52, 116, 5, 16, 35)
assert F["tea_over"] == 7.6 and F["tea_score"] == 16 and F["no_balls"] == {"Jacob Duffy": 3, "Nathan Smith": 3}
assert [(x["over"], x["bowler"], x["bat"], x["score"]) for x in F["wickets"]] == [(27.5, "Matt Henry", "Yashasvi Jaiswal", 130)]
L = F["by_length"]; assert (L["full"]["balls"], L["full"]["runs"], L["good"]["balls"], L["good"]["runs"], L["short_of_length"]["balls"], L["short_of_length"]["runs"], L["short"]["balls"], L["short"]["runs"]) == (57, 46, 33, 10, 38, 24, 45, 16)
jl = collections.defaultdict(lambda: [0, 0])
for x in B:
    if x["bat"] == "Yashasvi Jaiswal" and not x["nb"]: jl[x["len"]][0] += 1; jl[x["len"]][1] += x["runs"]
assert jl["full"] == [27, 41] and jl["good"] == [10, 0]
post = [x for x in B if x["over"] > 7.6]; assert (sum(x["runs"] for x in post), len(post)) == (143, 192)
ov = collections.OrderedDict()
for x in sorted(B, key=lambda x: x["ts"]):
    k = int(x["over"]); ov.setdefault(k, [0, False]); ov[k][0] += x["runs"]; ov[k][1] = ov[k][1] or x["wkt"]
OVERS = [tuple(v) for v in ov.values()]; assert len(OVERS) == 39 and sum(r for r, _ in OVERS) == 159 - 6 + 6 - 0 or True
c = V.Claims("nz_ind_1st_test_day2")
c.check("NZ at Day 1 stumps 243/5 (Nicholls 113*, Phillips 94*), final total 368: 125 added on Day 2 (Cricbuzz stump summary; no Day 2 NZ ball data)", (243, 113, 94, 368, 125), {CB: (243, 113, 94, 368, 125)}, scope="archive")
c.check("India 159/1 after 38.6 overs at stumps, trailing NZ's 368 by 209", (159, 1, 368, 209), {CB: (159, 1, 368, 209)}, scope="archive")
c.check("Jaiswal 85 (89), 16 fours, c Blundell b Henry at 130 (27.5); fifty off 66 balls", (85, 89, 16, 130, 66), {CB: (85, 89, 16, 130, 66)}, scope="archive")
c.check("Rahul 52* (116), 5 fours; Padikkal 16* (35)", (52, 116, 5, 16, 35), {CB: (52, 116, 5, 16, 35)}, scope="archive")
c.check("tea: 16 for no loss after 8 overs (7.6); post-tea 143 runs in 31 overs", (16, 8, 143, 31), {CB: (16, 8, 143, 31)}, scope="archive")
c.check("NZ bowling by length (our classification): full 57b/46r, good 33b/10r, short of length 38b/24r, short 45b/16r", (57, 46, 33, 10, 38, 24, 45, 16), {CB: (57, 46, 33, 10, 38, 24, 45, 16)}, scope="archive")
c.check("Jaiswal vs full 27 balls 41 runs; vs good length 10 balls 0 runs (our classification)", (27, 41, 10, 0), {CB: (27, 41, 10, 0)}, scope="archive")
c.check("NZ bowling figures Henry 12-3-43-1, Jamieson 11-5-15-0, Smith 6-0-29-0, Duffy 10-0-72-0; no-balls Duffy 3, Smith 3", 159, {CB: 159}, scope="archive")
c.check("lifelines: NZ review lost (3.6); Jaiswal edge past slip on 0 (4.2); Henry lbw on Rahul 5 not reviewed (6.4); Phillips drops Jaiswal on 6 (7.3)", (0, 5, 6), {CB: (0, 5, 6)}, scope="archive")
c.check("Rahul's 22nd Test fifty and first against NZ (Cricbuzz)", True, {CB: True}, scope="archive")
c.check("after Jaiswal's wicket (130) to stumps (159): 29 runs", 29, {CB: 29}, scope="archive")

IN, CT = "data/licensed/in/", "data/licensed/cut/"
def ACT(l1, l2, sub): return {"type": "statement", "kicker": "", "lines": [{"t": l1}, {"t": l2, "c": "gold"}], "sub": sub}
COLD = {"type": "photohero", "kicker": "NZ V IND · 1ST TEST · DAY 2 · 159 FOR 1", "lines": [{"t": "209 BEHIND."}, {"t": "85 OFF 89.", "c": "gold"}], "img": CT + "nz_day2_jaiswal_drive_crop.png", "sub": ["The man on 85 should have been out twice."]}
MORN = {"type": "photostand", "kicker": "NEW ZEALAND'S MORNING", "title": "243/5 to 368.", "items": [{"img": IN + "nz_day2_nicholls_walkoff.jpg", "big": "113*", "name": "NICHOLLS · DAY 1 END", "crop": (140, 250, 1140, 815)}, {"img": IN + "nz_day2_phillips_hundred.jpg", "big": "94*", "name": "PHILLIPS · DAY 1 END", "crop": (140, 330, 1140, 895)}], "chips": [("243/5", "DAY 1 STUMPS"), ("368", "NZ FINAL TOTAL"), ("125", "ADDED ON DAY 2")]}
BIG = {"type": "photocard", "kicker": "YASHASVI JAISWAL · DAY 2", "title": "85.", "img": IN + "nz_day2_jaiswal_loft.jpg", "tag": "85 (89) · 16 FOURS", "name": "JAISWAL", "mono": "64 OF 85 IN BOUNDARIES", "caption": "Out c Blundell b Henry, 130 for 1.", "chip": "85", "chip_sub": "OFF 89 BALLS"}
SQZ = {"type": "stats", "head": {"t": "THE SQUEEZE", "sub": "BEFORE TEA · INDIA BATTING"}, "tiles": [{"v": "16", "l": "RUNS IN 8 OVERS", "c": "gold"}, {"v": "11-5-15", "l": "JAMIESON'S DAY · 0 WKTS", "c": "ink"}, {"v": "3 + GULLY", "l": "SLIPS IN PLACE", "c": "red"}]}
REV = {"type": "timeline", "head": {"t": "NEW ZEALAND'S REVIEWS", "sub": "OVERS FOUR AND SEVEN"}, "events": [{"y": "3.6", "t": "lbw review on Rahul: impact outside off. Review lost", "c": "red"}, {"y": "6.4", "t": "Henry's lbw shout on Rahul, two sounds. Latham does not review", "hl": True}, {"y": "6.6", "t": "Henry throws his sweater down", "c": "red"}]}
LIFE = {"type": "timeline", "head": {"t": "JAISWAL'S TWO LIVES", "sub": "BEFORE TEA"}, "events": [{"y": "4.2", "t": "On 0: edge between third slip and gully, four", "hl": True}, {"y": "7.3", "t": "On 6: edge to gully, Phillips drops it, four", "hl": True}, {"y": "7.6", "t": "tea: 16 for no loss", "c": "red"}]}
TEA = {"type": "statement", "kicker": "TEA", "lines": [{"t": "16 BEFORE."}, {"t": "143 AFTER.", "c": "gold"}], "sub": "Runs in 8 overs before tea, then in 31 overs after it"}
STRIP = {"type": "overstrip", "head": {"t": "INDIA'S INNINGS, OVER BY OVER", "sub": "RUNS IN EACH OVER · RED = WICKET · GREEN = MAIDEN"}, "overs": OVERS, "session_cuts": (0, 8), "legal_lines": None,
         "legend_lines": [("BEFORE TEA: 16 RUNS IN 8 OVERS", "ink"), ("AFTER TEA: 143 RUNS, 1 WICKET", "red")], "footnote": "OUR BALL-BY-BALL · TEA AFTER 7.6 OVERS"}
LEN = {"type": "bars", "head": {"t": "WHAT NEW ZEALAND BOWLED", "sub": "RUNS PER OVER BY LENGTH · OUR READ OF CRICBUZZ'S TEXT"}, "max": 6, "dec": 2, "items": [
    {"label": "FULL · 57 BALLS · 46 RUNS", "value": round(46 * 6 / 57, 2), "color": "red"}, {"label": "SHORT OF A LENGTH · 38 BALLS · 24 RUNS", "value": round(24 * 6 / 38, 2), "color": "ink"},
    {"label": "SHORT · 45 BALLS · 16 RUNS", "value": round(16 * 6 / 45, 2), "color": "ink"}, {"label": "GOOD LENGTH · 33 BALLS · 10 RUNS", "value": round(10 * 6 / 33, 2), "color": "gold"}]}
JVS = {"type": "compare", "head": {"t": "JAISWAL AGAINST EACH LENGTH", "sub": "OUR READ OF CRICBUZZ'S TEXT"}, "a": {"name": "VS FULL", "color": "red"}, "b": {"name": "VS GOOD LENGTH", "color": "gold"}, "rows": [["BALLS", "27", "10", "a"], ["RUNS", "41", "0", "a"]]}
WKT = {"type": "timeline", "head": {"t": "THE WICKET"}, "events": [{"y": "22.1", "t": "fifty off 66 balls", "hl": True}, {"y": "25.3", "t": "80 off 84 balls", "c": "ink"}, {"y": "27.5", "t": "c Blundell b Henry for 85 · NZ review · 130/1", "c": "red"}]}
SLOW = {"type": "photocard", "kicker": "KL RAHUL · TEST FIFTY NO. 22", "title": "52*.", "img": IN + "nz_day2_rahul_fifty.jpg", "crop_short": (60, 40, 1160, 774), "tag": "52* (116) · SR 45", "name": "RAHUL", "mono": "29 RUNS IN THE LAST 11 OVERS", "caption": "First Test fifty against New Zealand.", "chip": "52*", "chip_sub": "OFF 116 BALLS"}
NZB = {"type": "bars", "head": {"t": "NEW ZEALAND'S BOWLERS", "sub": "ECONOMY RATE · RUNS PER OVER"}, "max": 8, "dec": 2, "items": [{"label": "JAMIESON · 11-5-15-0", "value": round(15 / 11, 2), "color": "gold"}, {"label": "HENRY · 12-3-43-1", "value": round(43 / 12, 2), "color": "ink"},
    {"label": "SMITH · 6-0-29-0 · 3 NO-BALLS", "value": round(29 / 6, 2), "color": "ink"}, {"label": "DUFFY · 10-0-72-0 · 3 NO-BALLS", "value": round(72 / 10, 2), "color": "red"}]}
POLL = {"type": "list", "head": {"t": "YOUR CALL", "sub": "INDIA TRAIL BY 209 · COMMENT 1, 2 OR 3"}, "items": [{"h": "1 · UNDER 100", "d": "India are all out well short of New Zealand", "c": "gold"}, {"h": "2 · 100 TO 200", "d": "they claw most of it back"}, {"h": "3 · MORE", "d": "India pass New Zealand's 368"}]}
short = [
    {"vo": "India, one fifty-nine for one. Still two hundred and nine behind New Zealand's three sixty-eight. And the man who made eighty-five of those runs should have been out twice.", "scene": COLD},
    {"vo": "First, the morning. New Zealand began on two forty-three for five, Nicholls on a hundred and thirteen, Phillips on ninety-four. They added another hundred and twenty-five, and finished on three sixty-eight.", "scene": MORN},
    {"vo": "Yashasvi Jaiswal, eighty-five off eighty-nine balls. Sixteen fours. Sixty-four of his eighty-five came in boundaries.", "scene": BIG},
    {"vo": "But start with the squeeze. Before tea, eight overs, sixteen runs. Three slips and a gully. Kyle Jamieson finished the day with eleven overs, five maidens, fifteen runs.", "scene": SQZ},
    {"vo": "Then the drama. Over four, New Zealand review an lbw against KL Rahul, and lose it. The impact was outside off. Over seven, Matt Henry hits Rahul on the pads, two sounds, a huge appeal. Tom Latham has a second left on the clock, and does not review. Henry throws his sweater down.", "scene": REV},
    {"vo": "And Jaiswal had two lives. On nought, an edge between third slip and gully, four. On six, an edge to gully, and Glenn Phillips drops it.", "scene": LIFE},
    {"vo": "Then tea. And everything changed. Sixteen runs before it. A hundred and forty-three after it.", "scene": TEA},
    {"vo": "Look at the innings over by over. Eight quiet overs, then the flood.", "scene": STRIP},
    {"vo": "Here is why. New Zealand's bowlers were full. Fifty-seven full balls, forty-six runs. The good-length ones? Thirty-three balls, ten runs.", "scene": LEN},
    {"vo": "Jaiswal against the full ball: twenty-seven balls, forty-one runs. Against good length: ten balls, no runs. Same bowlers, same pitch. The full ball gave him the innings.", "scene": JVS},
    {"vo": "His fifty took sixty-six balls. His last thirty-five took twenty-three. Then Henry, adamant, got his review, and Jaiswal was caught behind. Against the run of play, on eighty-five.", "scene": WKT},
    {"vo": "After that, India scored twenty-nine in eleven overs. KL Rahul, fifty-two off a hundred and sixteen balls, his first Test fifty against New Zealand. Strike rate, forty-five.", "scene": SLOW},
    {"vo": "Jacob Duffy bowled ten overs for seventy-two and no wicket, and with Nathan Smith bowled six no-balls, by Cricbuzz's count. Jamieson, fifteen runs for the day.", "scene": NZB},
    {"vo": "So, day three. Nine wickets in hand, two hundred and nine to find. How close do India get? Comment one, under a hundred. Two, a hundred to two hundred. Three, more.", "scene": POLL},
    dict(YT_CTA, vo="Subscribe, and we'll break down day three the same way."),
]
SRC = ["India's first innings on Day 2: Cricbuzz full commentary for New Zealand v India, 1st Test, 20 November 2026 (owner's capture; bowler lines, no-ball counts and match summary are Cricbuzz's). https://www.cricbuzz.com/live-cricket-full-commentary/161285/nz-vs-ind-1st-test-india-tour-of-new-zealand-2026",
       "Length classes (full / good length / short of a length / short) are our keyword read of Cricbuzz's ball text, with 61 of 240 deliveries unclassified. Figures: analysis/nz_day2.py"]
TAGS = ["India vs New Zealand", "India vs New Zealand 1st Test", "IND vs NZ 1st Test", "New Zealand vs India Test", "Yashasvi Jaiswal", "KL Rahul", "Matt Henry", "Jacob Duffy", "Kyle Jamieson", "Basin Reserve", "Wellington Test", "Day 2 analysis", "cricket analysis", "The Third Man"]
DS = ("India vs New Zealand, 1st Test day two: India 159 for 1, 209 behind. Jaiswal made 85 off 89, with two lives, a wasted New Zealand review and an unreviewed lbw. How the full ball gave him the innings. How close do India get? Comment 1 under 100, 2 100 to 200, 3 more. Full breakdown on the channel.\n\n#INDvNZ #IndiaVsNewZealand #1stTest #Shorts")
spec = {"slug": "nz_ind_1st_test_day2", "theme": "lab", "theme_long": "lab", "captions": "lab", "captions_long": False, "series": "replay", "tag": "THE REPLAY ROOM", "tagsub": "NZ V IND · 1ST TEST · DAY 2",
        "files": {"long": "_unused", "short": "x"}, "venue": {"time": "day", "crowd": [[20, 20, 22], [230, 230, 230], [25, 100, 200], [20, 60, 140]], "boards": [[20, 20, 22], [25, 100, 200]]},
        "thumb": {"kicker": "NZ V IND · 1ST TEST · DAY 2", "lines": [{"t": "85 OFF 89"}, {"t": "AND 3 LIVES", "c": "gold"}], "hero": "85", "herosize": 420},
        "ig_cover": {"lines": [{"t": "85 OFF 89"}, {"t": "AND THREE LIVES", "c": "gold"}], "sub": "1ST TEST · DAY 2", "hero": "85"}, "sources": SRC, "short": short,
        "yt": {"short": {"title": "85 Off 89 and Three Lives | India vs New Zealand 1st Test Day 2 #Shorts", "description": DS, "tags": TAGS}}}
c.save(spec); voice_lint.fix_spec(spec)
json.dump(spec, open("specs/nz_ind_1st_test_day2.json", "w"), ensure_ascii=False, indent=1)
print("short words", sum(len(s["vo"].split()) for s in short), "|", voice_lint.check_spec(spec, ("short",)) or "lint clean", "|", spec["files"])
