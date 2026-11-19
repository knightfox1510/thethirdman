"""Writes specs/nz_ind_1st_test_day1.json: The Replay Room Ep 4, India vs New Zealand, 1st Test, Day 1 (Basin Reserve, 19 Nov 2026): long (lab look) + a ~160 s vertical (stadium look).
Source: the owner's Cricbuzz full-commentary capture of day one (data/cricbuzz/nz_ind_1st_test_day1... , 499 deliveries parsed by analysis/nz_day1.py -> data/provenance/nz_day1_figures.json / nz_day1_balls.json).
Numbers that only Cricbuzz has are said to be 'in our ball-by-ball'; the tea state (140/5, Nicholls 66*, Phillips 42*, Bumrah 3/31, Akash Deep 1/22, Kamboj 1/39) and the five dismissals are corroborated by Telangana Today and The Open Press.
Cricbuzz's own tables (control %, false-shot % and length splits) are Cricbuzz's; 'after lunch' splits are derived by subtracting the lunch table from the day table.  python3 make_nz_day1.py"""
import json, os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voice_lint
from dataops import verify as V
from variants import YT_CTA

F = json.load(open("data/provenance/nz_day1_figures.json")); B = json.load(open("data/provenance/nz_day1_balls.json"))
CB, TT, OP, CSH = "cricbuzz", "telanganatoday", "openpress", "cricsheet"
ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split(); TENS = "x x twenty thirty forty fifty sixty seventy eighty ninety".split()


def w(n):
    n = int(n)
    if n < 20: return ONES[n]
    if n < 100: return TENS[n // 10] + ("-" + ONES[n % 10] if n % 10 else "")
    h, r = divmod(n, 100); return ONES[h] + " hundred" + (" and " + w(r) if r else "")


# ------------------------------------------------------------------ figures asserted against the parsed data
bf = F["bowling_final"]; assert F["stumps"]["score"] == 243 and F["deliveries"] == 498
assert [(k, v["ov"], v["m"], v["r"], v["w"]) for k, v in bf.items()] == [("Jasprit Bumrah", 17, 5, 52, 3), ("Anshul Kamboj", 18, 4, 57, 1), ("Akash Deep", 15, 5, 33, 1), ("Prasidh Krishna", 16, 2, 58, 0), ("Washington Sundar", 16, 2, 38, 0)]
assert sum(v["r"] for v in bf.values()) + 5 == 243                       # 5 extras
assert F["lunch_over"] == 22.5 and F["lunch_score"] == 60 and F["tea_over"] == 47.6 and F["tea_score"] == 140
assert [(x["over"], x["bowler"], x["bat"], x["score"]) for x in F["wickets"]] == [(0.3, "Jasprit Bumrah", "Tom Latham", 2), (3.2, "Anshul Kamboj", "Devon Conway", 12), (19.1, "Akash Deep", "Rachin Ravindra", 51), (20.6, "Jasprit Bumrah", "Daryl Mitchell", 52), (28.2, "Jasprit Bumrah", "Blundell", 70)]
NI, PH = F["Henry Nicholls"], F["Glenn Phillips"]; assert (NI["batRuns"], NI["batBalls"], PH["batRuns"], PH["batBalls"]) == (113, 221, 94, 182)
st = [x for x in B if x["over"] > 28.2 + 1e-9]; pre = [x for x in B if x["over"] <= 28.2 + 1e-9]
c_ = collections.Counter(x["runs"] for x in st if x["res"] != "wide")
assert (len(st), sum(x["runs"] for x in st), sum(x["wkt"] for x in st)) == (327, 173, 0) and (len(pre), sum(x["runs"] for x in pre), sum(x["wkt"] for x in pre)) == (171, 70, 5)
dots = c_[0]; assert (dots, c_[1], c_[2], c_[3], c_[4]) == (238, 54, 7, 7, 21) and round(100 * dots / 327) == 73
bb = [x for x in B if x["bowler"] == "Jasprit Bumrah" and x["over"] > 28.2 + 1e-9]; assert (len(bb), sum(x["runs"] for x in bb), sum(x["wkt"] for x in bb)) == (48, 35, 0)
# Cricbuzz tables (lunch table for session 1; day table) and the derived after-lunch split
S1 = {"full": (2, 23, 32, .25), "good": (2, 16, 76, .302), "short": (0, 11, 25, .16)}; DAY = {"full": (2, 67, 78, .153), "good": (3, 50, 202, .193), "short": (0, 77, 122, .09)}
AFT = {k: (DAY[k][0] - S1[k][0], DAY[k][1] - S1[k][1], DAY[k][2] - S1[k][2], (DAY[k][3] * DAY[k][2] - S1[k][3] * S1[k][2]) / (DAY[k][2] - S1[k][2])) for k in DAY}
n1 = sum(v[2] for v in S1.values()); n2 = sum(v[2] for v in AFT.values()); assert (n1, sum(v[2] for v in DAY.values())) == (133, 402)
short1, short2 = round(100 * S1["short"][2] / n1), round(100 * AFT["short"][2] / n2); full1, full2 = round(100 * S1["full"][2] / n1), round(100 * AFT["full"][2] / n2); good1, good2 = round(100 * S1["good"][2] / n1), round(100 * AFT["good"][2] / n2)
gfs1, gfs2 = round(100 * S1["good"][3]), round(100 * AFT["good"][3]); assert (short1, short2, full1, full2, good1, good2, gfs1, gfs2) == (19, 36, 24, 17, 57, 47, 30, 13)
econ = {"good": 1.48, "short": 3.78, "full": 5.15}; assert all(abs(DAY[k][1] * 6 / DAY[k][2] - econ[k]) < .01 for k in econ)      # Cricbuzz's published rates (it truncates 1.485 to 1.48)
# runs and wicket per over
ov = collections.OrderedDict()
for x in B:
    k = int(x["over"]); ov.setdefault(k, [0, False]); ov[k][0] += x["runs"]; ov[k][1] = ov[k][1] or x["wkt"]
def seg(a, b):
    z = [x for x in B if a <= int(x["over"]) <= b]; return sum(x["runs"] for x in z), sum(x["wkt"] for x in z)
BALL1, BALL2, BALL3 = seg(0, 19), seg(20, 79), seg(80, 81); assert (BALL1, BALL2, BALL3) == ((52, 3), (184, 2), (7, 0))      # first 20 overs, overs 21-80 (old ball), overs 81-82 (second new ball)
OVERS = [tuple(v) for v in ov.values()]; assert len(OVERS) == 82 and sum(r for r, _ in OVERS) == 243 and sum(wk for _, wk in OVERS) == 5
SESS = (23, 48)                                                     # lunch after 22.5 overs, tea after 47.6

c = V.Claims("nz_ind_1st_test_day1")
c.check("score at tea: 140/5; Nicholls 66*, Phillips 42*", (140, 5, 66, 42), {CB: (140, 5, 66, 42), TT: (140, 5, 66, 42), OP: (140, 5, 66, 42)})
c.check("figures at tea: Bumrah 3/31, Akash Deep 1/22, Kamboj 1/39", ((3, 31), (1, 22), (1, 39)), {CB: ((3, 31), (1, 22), (1, 39)), TT: ((3, 31), (1, 22), (1, 39))})
c.check("wickets: Latham, Mitchell, Blundell to Bumrah; Conway to Kamboj; Ravindra to Akash Deep", 5, {CB: 5, OP: 5})
c.check("lunch 60/4 (after 22.5 overs)", (60, 4), {CB: (60, 4), TT: (60, 4)})
c.check("pitch easing after lunch: browning off as the sun came out", True, {CB: True, TT: True, OP: True})
c.check("stumps 243/5 after 81.6 overs", (243, 5), {CB: (243, 5)}, scope="archive")
c.check("Nicholls 113 (221), Phillips 94 (182), 6th-wicket stand 173 off 327 balls", (113, 221, 94, 182, 173, 327), {CB: (113, 221, 94, 182, 173, 327)}, scope="archive")
c.check("full bowling figures (Bumrah 17-5-52-3, Kamboj 18-4-57-1, Akash 15-5-33-1, Prasidh 16-2-58-0, Sundar 16-2-38-0)", 243, {CB: 243}, scope="archive")
c.check("stand: 54 singles, 7 twos, 7 threes, 21 fours; 238 dots of 327 (73%)", (54, 7, 7, 21, 238, 327), {CB: (54, 7, 7, 21, 238, 327)}, scope="archive")
c.check("after Blundell: Bumrah 48 balls, 35 runs, no wicket", (48, 35, 0), {CB: (48, 35, 0)}, scope="archive")
c.check("5 wickets in the first 28.2 overs (171 balls, 70 runs); none in the next 53.4 overs (327 balls, 173 runs)", (171, 70, 5, 327, 173, 0), {CB: (171, 70, 5, 327, 173, 0)}, scope="archive")
c.check("false shots 25.1% before lunch vs 13.6% in session 2 (Cricbuzz's own figures)", (25.1, 13.6), {CB: (25.1, 13.6)}, scope="archive")
c.check("seam length table, day: full 2/67 78b, good 3/50 202b, short 0/77 122b", ((2, 67, 78), (3, 50, 202), (0, 77, 122)), {CB: ((2, 67, 78), (3, 50, 202), (0, 77, 122))}, scope="archive")
c.check("derived split after lunch: short share 19% -> 36%, good-length false shots 30% -> 13%", (19, 36, 30, 13), {CB: (short1, short2, gfs1, gfs2)}, scope="archive")
c.check("Nicholls had four hundreds at the Basin Reserve before today", 4, {CSH: 4, CB: 4})
c.check("ball age: first 20 overs 52/3, overs 21-80 184/2, second new ball (overs 81-82) 7/0", (52, 3, 184, 2, 7, 0), {CB: (52, 3, 184, 2, 7, 0)}, scope="archive")
c.check("India won the toss and bowled; 15 mm of grass, moisture on top in the morning", True, {CB: True}, scope="archive")
c.check("lifelines: Phillips lbw review lost on 6 (30.3); Nicholls dropped on 102 (73.3)", (6, 102), {CB: (6, 102)}, scope="archive")

NOTES = {1: "FULL · 4TH-STUMP LINE · SEAM UPRIGHT, CAME BACK", 2: "FULL, ANGLED IN, SEAMED AWAY · EDGE TO PANT", 3: "SHORT OF A LENGTH, EXTRA BOUNCE · EDGE TO PANT", 4: "GOOD-LENGTH NIPBACKER · INSIDE EDGE TO SHORT LEG", 5: "SHORT OF A LENGTH, ANGLED BACK · EDGE TO GILL"}
WM = {"type": "wicketmap", "head": {"t": "WHERE THE FIVE WICKETS CAME FROM"}, "footnote": "ILLUSTRATIVE · PLACEMENT READ FROM THE BALL-BY-BALL COMMENTARY · LINES MEASURED FROM THE OFF STUMP", "items": [
    {"n": 1, "who": "LATHAM", "by": "BUMRAH", "x": .34, "len": 2.6, "move": "in", "note": NOTES[1], "over": "0.3", "score": "2/1"},
    {"n": 2, "who": "CONWAY", "by": "KAMBOJ", "x": .11, "len": 3.6, "move": "out", "note": NOTES[2], "over": "3.2", "score": "12/2", "kind": "c", "catcher": "PANT"},
    {"n": 3, "who": "RAVINDRA", "by": "AKASH DEEP", "x": .57, "len": 6.5, "note": NOTES[3], "over": "19.1", "score": "51/3", "kind": "c", "catcher": "PANT"},
    {"n": 4, "who": "MITCHELL", "by": "BUMRAH", "x": 0.0, "len": 5.0, "move": "in", "note": NOTES[4], "over": "20.6", "score": "52/4", "kind": "c", "catcher": "JAISWAL"},
    {"n": 5, "who": "BLUNDELL", "by": "BUMRAH", "x": .57, "len": 6.4, "move": "in", "note": NOTES[5], "over": "28.2", "score": "70/5", "kind": "c", "catcher": "GILL"}]}
STRIP = {"type": "overstrip", "head": {"t": "THE WHOLE DAY, OVER BY OVER", "sub": "RUNS IN EACH OVER · RED = WICKET · GREEN = MAIDEN"}, "overs": OVERS, "session_cuts": SESS,
         "legal_lines": None, "legend_lines": [("FIRST 28.2 OVERS: 5 WICKETS, 70 RUNS", "red"), ("NEXT 53.4 OVERS: 0 WICKETS, 173 RUNS", "ink")], "footnote": "OUR BALL-BY-BALL · LUNCH AFTER 22.5 OVERS, TEA AFTER 47.6"}
BALLAGE = {"type": "stats", "head": {"t": "THE BALL", "sub": "NEW ZEALAND'S RUNS AND WICKETS BY AGE OF THE BALL"}, "tiles": [{"v": "52 / 3", "l": "FIRST 20 OVERS · NEW BALL", "c": "gold"}, {"v": "184 / 2", "l": "OVERS 21-80 · OLD BALL", "c": "red"}, {"v": "7 / 0", "l": "OVERS 81-82 · SECOND NEW BALL", "c": "ink"}]}
LIFE = {"type": "list", "head": {"t": "THE LIFELINES", "sub": "NEW ZEALAND'S ESCAPES"}, "items": [
    {"h": "30.3 · PHILLIPS ON 6", "d": "lbw review lost: the third umpire gave an inside edge", "c": "gold"}, {"h": "35.4 · PHILLIPS ON 19", "d": "inside edge rolls past the stumps"},
    {"h": "50.3 · PHILLIPS ON 51", "d": "edge wide of where a third slip would stand"}, {"h": "73.3 · NICHOLLS ON 102", "d": "top edge dropped: Pant and Padikkal both left it"}, {"h": "79.3 · PHILLIPS ON 91", "d": "edge past the stumps to the keeper"}]}
POLL = {"type": "list", "head": {"t": "YOUR CALL", "sub": "WHO WON DAY ONE? COMMENT 1, 2 OR 3"}, "items": [{"h": "NICHOLLS", "d": "113 not out, the fifth hundred at the Basin", "c": "gold"}, {"h": "PHILLIPS", "d": "94 not out, 173 together"}, {"h": "BUMRAH", "d": "3 for 52, all before the 29th over"}]}
long = [
    {"vo": "Seventy for five. India had won the toss, the conditions and the morning. By stumps, New Zealand were two hundred and forty-three for five. This is how day one in Wellington turned, and the stretch of overs where it slipped away.", "chapter": "Intro",
     "scene": {"type": "statement", "kicker": "NEW ZEALAND V INDIA · 1ST TEST · DAY 1", "lines": [{"t": "70 FOR 5."}, {"t": "THEN 243 FOR 5.", "c": "gold"}]}},
    {"vo": "Everything here comes from our ball-by-ball of the day. India won the toss, and Shubman Gill chose to bowl. The pitch had fifteen millimetres of grass, and moisture on top in the morning. Helpful conditions, and in the first hour the seamers made them count.", "chapter": "The conditions",
     "scene": {"type": "stats", "head": {"t": "THE CONDITIONS", "sub": "BASIN RESERVE · MORNING"}, "tiles": [{"v": "15 MM", "l": "GRASS ON THE PITCH", "c": "gold"}, {"v": "MOISTURE", "l": "ON TOP IN THE MORNING", "c": "ink"}, {"v": "BOWL", "l": "INDIA WON THE TOSS", "c": "red"}]}},
    {"vo": "Jasprit Bumrah's first over told the story. Full, on the fourth-stump line, the seam bolt upright. Tom Latham left it, expecting it to go away. It came back late, and hit off stump. Two for one.", "chapter": "The new ball",
     "scene": {"type": "trajectory", "head": {"t": "BUMRAH'S FIRST OVER", "sub": "ILLUSTRATIVE · SIDE-ON · LATHAM B BUMRAH"}, "hl": ["FULL"], "bowler_c": "ink", "balls": [{"length": 3.2, "end": 0.4, "label": "FULL · 4TH-STUMP LINE", "c": "gold", "at": 0.3}], "note": "seam upright: Latham left it, it came back in"}},
    {"vo": "Then a review that went New Zealand's way. Devon Conway was given out caught behind off Bumrah, and reviewed at once: the noise came before the ball reached the bat. Not out. Two overs later Anshul Kamboj bowled full and angled in, it seamed away, and Conway edged to Pant. Twelve for two.",
     "scene": {"type": "timeline", "head": {"t": "THE FIRST FOUR OVERS"}, "events": [{"y": "0.3", "t": "Latham bowled by Bumrah · 2/1", "hl": True}, {"y": "2.5", "t": "Conway reviews: not out", "c": "red"}, {"y": "3.2", "t": "Conway c Pant b Kamboj · 12/2", "hl": True}]}},
    {"vo": "Rachin Ravindra rode his luck. India did not review an edge behind, and a direct hit from Kamboj missed. Then Akash Deep found extra bounce, short of a length outside off, and the edge went to Pant. Fifty-one for three. The last ball of the next over was Bumrah, a good-length ball that nipped back. Daryl Mitchell, who had been walking at him, got an inside edge to short leg, where Yashasvi Jaiswal held it. Fifty-two for four.",
     "scene": {"type": "list", "head": {"t": "TWO IN TWO OVERS", "sub": "OVERS 19 AND 20"}, "items": [{"h": "RAVINDRA C PANT B AKASH DEEP", "d": "short of a length, extra bounce · 51/3", "c": "gold"}, {"h": "MITCHELL C JAISWAL B BUMRAH", "d": "good-length nipbacker, inside edge to short leg · 52/4", "c": "gold"}]}},
    {"vo": "Sixty for four at lunch. New Zealand were rattled: Cricbuzz has them playing and missing or edging on twenty-five per cent of balls in that session.", "chapter": "Lunch: 60 for 4",
     "scene": {"type": "bignum", "head": {"t": "BEFORE LUNCH"}, "value": 25, "suffix": "%", "label": "OF BALLS DREW A FALSE SHOT · CRICBUZZ'S OWN FIGURE", "color": "red", "note": "60 for 4 at lunch"}},
    {"vo": "After lunch, Bumrah struck again. Tom Blundell, short of a length, angled back into the fifth-stump line; he left his bat hanging out and edged to Gill at first slip, who hung on. Seventy for five, in twenty-eight overs. Here is where all five wickets came from.", "chapter": "Five wickets, 70 runs", "scene": WM},
    {"vo": "And here is what worked. India's seamers bowled two hundred and two balls on a good length, for just one point four eight an over, and three wickets. The full balls took two wickets but cost over five an over. The short balls cost nearly four an over, and took none.", "chapter": "What worked",
     "scene": {"type": "bars", "head": {"t": "WHAT WORKED", "sub": "INDIA'S SEAMERS · RUNS PER OVER BY LENGTH · CRICBUZZ'S TABLE"}, "max": 6, "dec": 2, "items": [{"label": "GOOD LENGTH · 202 BALLS · 3 WKTS", "value": 1.48, "color": "gold"}, {"label": "SHORT · 122 BALLS · 0 WKTS", "value": 3.78, "color": "ink"}, {"label": "FULL · 78 BALLS · 2 WKTS", "value": 5.15, "color": "red"}]}},
    {"vo": "The ball told the same story. The new ball did the work: three wickets for fifty-two in the first twenty overs. The old ball took two wickets in the next sixty overs, and cost a hundred and eighty-four runs. The second new ball had two overs before stumps: seven runs, no wicket.", "chapter": "The ball", "scene": BALLAGE},
    {"vo": "So where did it turn? Over thirty. Bumrah nips one back, Gill reviews an lbw against Glenn Phillips, who was on six, and the third umpire sees an inside edge. India lose the review. Five overs later, another inside edge rolls past the stumps. And it kept happening.", "chapter": "Where it turned", "scene": LIFE},
    {"vo": "Then the pitch eased. At lunch the pitch report said it was browning off as the sun came out, with not the kind of movement we saw before lunch. The numbers agree. Cricbuzz has New Zealand's false shots at twenty-five per cent before lunch, and thirteen and a half in the next session. On good-length balls, thirty per cent before lunch, and about thirteen after.", "chapter": "The sun comes out",
     "scene": {"type": "compare", "head": {"t": "THE PITCH EASES", "sub": "FALSE SHOTS · CRICBUZZ · AFTER-LUNCH SPLIT DERIVED"}, "a": {"name": "BEFORE LUNCH", "color": "gold"}, "b": {"name": "AFTER LUNCH", "color": "ink"}, "rows": [["ALL BALLS", "25%", "14%", "a"], ["GOOD-LENGTH BALLS", "30%", "13%", "a"]]}},
    {"vo": "And India's lengths slipped. Before lunch, nineteen per cent of their seam balls were short. After lunch, thirty-six. Good-length balls fell from fifty-seven per cent to forty-seven. The pitch asked for a fuller length, and India drifted shorter.", "chapter": "Lengths",
     "scene": {"type": "compare", "head": {"t": "INDIA'S LENGTHS DRIFTED", "sub": "SHARE OF SEAM BALLS · DERIVED FROM CRICBUZZ'S TABLES"}, "a": {"name": "BEFORE LUNCH", "color": "gold"}, "b": {"name": "AFTER LUNCH", "color": "red"}, "rows": [["SHORT", "19%", "36%", "b"], ["GOOD LENGTH", "57%", "47%", "a"], ["FULL", "24%", "17%", "a"]]}},
    {"vo": "Henry Nicholls made the most of it. A hundred and thirteen not out, off two hundred and twenty-one balls, his fifth Test hundred at the Basin Reserve: in our archive he had four here before today. Playing late, behind the line. Cricbuzz had his control at ninety per cent, against seventy for the other New Zealand batters.", "chapter": "Nicholls",
     "scene": {"type": "bignum", "head": {"t": "HENRY NICHOLLS"}, "value": 113, "suffix": "*", "label": "OFF 221 BALLS · 14 FOURS · CONTROL 90%", "color": "gold", "note": "fifth Test hundred at the Basin Reserve"}},
    {"vo": "And Glenn Phillips, ninety-four not out, off a hundred and eighty-two. Together, one hundred and seventy-three, unbroken. They ran everything: fifty-four singles, seven twos, seven threes, and twenty-one fours. Still seventy-three per cent dot balls, but India could never make that count.", "chapter": "The stand",
     "scene": {"type": "stats", "head": {"t": "173 UNBROKEN", "sub": "NICHOLLS AND PHILLIPS · 327 BALLS"}, "tiles": [{"v": "54", "l": "SINGLES", "c": "ink"}, {"v": "7", "l": "TWOS", "c": "gold"}, {"v": "7", "l": "THREES", "c": "gold"}, {"v": "21", "l": "FOURS", "c": "red"}]}},
    {"vo": "Put the whole day on one strip. Five wickets in the first twenty-eight overs. None in the next fifty-three.", "chapter": "The whole day", "scene": STRIP},
    {"vo": "The bowlers. Bumrah, seventeen overs, three for fifty-two. After Blundell, forty-eight balls, thirty-five runs and no wicket. Akash Deep, fifteen overs, one for thirty-three. Kamboj, eighteen, one for fifty-seven. Prasidh Krishna, sixteen overs, none for fifty-eight, with nine fours. And Washington Sundar, sixteen overs for thirty-eight.", "chapter": "The bowlers",
     "scene": {"type": "bars", "head": {"t": "THE BOWLERS", "sub": "ECONOMY RATE · RUNS PER OVER"}, "max": 4.5, "dec": 2, "items": [{"label": "AKASH DEEP · 15-5-33-1", "value": round(33 / 15, 2), "color": "gold"}, {"label": "SUNDAR · 16-2-38-0", "value": round(38 / 16, 2), "color": "ink"}, {"label": "BUMRAH · 17-5-52-3", "value": round(52 / 17, 2), "color": "ink"}, {"label": "KAMBOJ · 18-4-57-1", "value": round(57 / 18, 2), "color": "ink"}, {"label": "PRASIDH · 16-2-58-0", "value": round(58 / 16, 2), "color": "red"}]}},
    {"vo": "India took the second new ball at eighty overs. Bumrah's first ball went for four, then five dots, one of them a toe-crusher that Nicholls only just jammed his bat down on. Kamboj bowled the last over. Two hundred and forty-three for five.", "chapter": "The second new ball",
     "scene": {"type": "timeline", "head": {"t": "THE LAST HALF HOUR"}, "events": [{"y": "73.3", "t": "Nicholls dropped on 102", "c": "red"}, {"y": "80", "t": "second new ball taken", "hl": True}, {"y": "80.6", "t": "Bumrah's toe-crusher: survived", "c": "red"}, {"y": "82", "t": "stumps: 243/5", "hl": True}]}},
    {"vo": "So what now? As Cricbuzz's commentators said at tea, anything over two hundred and fifty could hurt India later. That is fifty more runs. Day two starts with the new ball, and five wickets to take. Now your call: who won day one? Nicholls, Phillips or Bumrah? Comment one, two or three, and tell us what India should do first.", "chapter": "Day two", "scene": POLL},
    {"vo": "Subscribe, and we'll break down day two the same way.", "scene": {"type": "cta", "lines": [{"t": "WHO WON"}, {"t": "DAY ONE?", "c": "gold"}], "pill": "SUBSCRIBE · MATCH BREAKDOWNS"}},
]


short = [
    {"vo": "Seventy for five. Then two hundred and forty-three for five, and nobody could break the stand. Here is how day one in Wellington turned.", "scene": long[0]["scene"]},
    {"vo": "India won the toss and bowled. Fifteen millimetres of grass, moisture on top. Bumrah's first over: full, fourth-stump line, seam upright. Latham left it, expecting it to go away. It came back.", "scene": long[2]["scene"]},
    {"vo": "Conway reviewed a caught-behind, and won. Two overs later Kamboj, full and angled in, seamed it away, and Conway edged to Pant. Twelve for two.", "scene": long[3]["scene"]},
    {"vo": "Ravindra was reprieved, twice. Then Akash Deep found extra bounce and Pant took the edge. Bumrah's nipbacker took Mitchell at short leg. Sixty for four at lunch.", "scene": long[4]["scene"]},
    {"vo": "After lunch, Blundell edged to Gill. Seventy for five. Two full balls, one good length, two short of a length: all five found something in the surface.", "scene": WM},
    {"vo": "Look at what worked. Good-length balls cost one point four eight an over, and took three wickets. The full balls took two, but cost over five. The short balls cost nearly four an over, and took none.", "scene": {"type": "bars", "head": {"t": "WHAT WORKED", "sub": "RUNS PER OVER BY LENGTH · CRICBUZZ"}, "max": 6, "dec": 2, "items": [{"label": "GOOD · 202 BALLS · 3 WKTS", "value": 1.48, "color": "gold"}, {"label": "SHORT · 122 BALLS · 0 WKTS", "value": 3.78, "color": "ink"}, {"label": "FULL · 78 BALLS · 2 WKTS", "value": 5.15, "color": "red"}]}},
    {"vo": "The new ball did the work: three wickets for fifty-two in twenty overs. The old ball: two wickets in sixty overs, and a hundred and eighty-four runs.", "scene": BALLAGE},
    {"vo": "Then it turned. Phillips, on six, survived an lbw review, and India lost it. Inside edges rolled past the stumps. A catch was dropped.", "scene": LIFE},
    {"vo": "And the pitch eased as the sun came out. False shots fell from twenty-five per cent before lunch to fourteen after. On good-length balls, from thirty to thirteen.", "scene": {"type": "compare", "head": {"t": "THE PITCH EASES", "sub": "FALSE SHOTS · CRICBUZZ · DERIVED SPLIT"}, "a": {"name": "BEFORE LUNCH", "color": "gold"}, "b": {"name": "AFTER LUNCH", "color": "ink"}, "rows": [["ALL BALLS", "25%", "14%", "a"], ["GOOD LENGTH", "30%", "13%", "a"]]}},
    {"vo": "India drifted shorter, too. Nineteen per cent of their seam balls were short before lunch. After lunch, thirty-six. The pitch wanted a fuller length.", "scene": {"type": "compare", "head": {"t": "LENGTHS DRIFTED", "sub": "SHARE OF SEAM BALLS · DERIVED"}, "a": {"name": "BEFORE LUNCH", "color": "gold"}, "b": {"name": "AFTER LUNCH", "color": "red"}, "rows": [["SHORT", "19%", "36%", "b"], ["GOOD LENGTH", "57%", "47%", "a"]]}},
    {"vo": "Bumrah finished with three for fifty-two. After Blundell, forty-eight balls, thirty-five runs, and no wicket. His work was done by the twenty-ninth over.", "scene": {"type": "bignum", "head": {"t": "JASPRIT BUMRAH"}, "value": 3, "suffix": "/52", "label": "17 OVERS · ALL THREE WICKETS BEFORE THE 29TH OVER", "color": "gold", "note": "after Blundell: 48 balls, 35 runs, no wicket"}},
    {"vo": "Henry Nicholls: a hundred and thirteen not out, his fifth hundred at the Basin Reserve. Glenn Phillips: ninety-four not out. Together, one seventy-three.", "scene": {"type": "stats", "head": {"t": "NEW ZEALAND'S SIXTH-WICKET STAND", "sub": "UNBROKEN · 173 OFF 327 BALLS"}, "tiles": [{"v": "113*", "l": "NICHOLLS · 221 BALLS", "c": "gold"}, {"v": "94*", "l": "PHILLIPS · 182 BALLS", "c": "gold"}]}},
    {"vo": "They ran seven twos and seven threes, and hit twenty-one fours. India went fifty-three overs without a wicket.", "scene": STRIP},
    {"vo": "India took the second new ball at eighty overs. Bumrah's first ball went for four, then five dots, one a toe-crusher that Nicholls only just survived. Two hundred and forty-three for five at stumps.", "scene": {"type": "statement", "kicker": "STUMPS · DAY 1", "lines": [{"t": "243 FOR 5."}, {"t": "NZ ON TOP.", "c": "gold"}], "sub": "Second new ball taken at 80 overs"}},
    {"vo": "So who won day one? Nicholls, Phillips, or Bumrah? Comment one, two or three, and tell us what India should do first on day two.", "scene": POLL},
    dict(YT_CTA, vo="Subscribe, and we'll break down day two the same way."),
]
SRC = ["Ball-by-ball for day one: Cricbuzz full commentary for New Zealand v India, 1st Test, 19 November 2026 (owner's capture; Cricbuzz's own session tables for control, false shots and length). https://www.cricbuzz.com/live-cricket-full-commentary/161285/nz-vs-ind-1st-test-india-tour-of-new-zealand-2026",
       "Tea-time state and the five dismissals corroborated by Telangana Today https://telanganatoday.com/1st-test-new-zealand-recover-to-140-5-at-tea-despite-bumrahs-three-wickets and The Open Press https://theopenpress.in/article/india-vs-new-zealand-1st-test-nicholls-phillips-century-partnership-19-november",
       "Nicholls' four earlier Test hundreds at the Basin Reserve: Cricsheet men's Test ball-by-ball archive (cricsheet.org, ODC-BY) and Cricbuzz. Figures: analysis/nz_day1.py, analysis/nz_tests.py"]
TAGS = ["India vs New Zealand", "India vs New Zealand 1st Test", "IND vs NZ 1st Test", "New Zealand vs India Test", "Jasprit Bumrah", "Henry Nicholls", "Glenn Phillips", "Shubman Gill", "Basin Reserve", "Wellington Test", "Day 1 analysis", "cricket analysis", "The Third Man"]
DL = ("India vs New Zealand, 1st Test day one analysis at the Basin Reserve, Wellington (19 November 2026): how 70 for 5 became 243 for 5. Where India's five wickets came from (line, length and movement), why the pitch eased as the sun came out, how India's lengths drifted shorter after lunch, "
      "and the unbroken 173 between Henry Nicholls (113*) and Glenn Phillips (94*).\n\nYOUR CALL: who won day one? Comment 1 (Nicholls), 2 (Phillips) or 3 (Bumrah), and tell us what India should do first on day two.\n\n"
      "Method: our ball-by-ball of the day (Cricbuzz commentary); Cricbuzz's own session tables for control, false-shot and length figures, with the after-lunch splits derived by subtracting the lunch table from the day table. Placement of the wicket balls is read from the commentary and is illustrative.\n\n#INDvNZ #IndiaVsNewZealand #1stTest #Day1")
DS = ("India vs New Zealand, 1st Test day one: 70 for 5 became 243 for 5. Where the five wickets came from, how the sun and pitch changed the game, and the 173 stand. Who won day one? Comment 1 Nicholls, 2 Phillips, 3 Bumrah. Full breakdown on the channel.\n\n#INDvNZ #IndiaVsNewZealand #1stTest #Shorts")
spec = {"slug": "nz_ind_1st_test_day1", "theme": "lab", "theme_long": "lab", "captions": "lab", "captions_long": False, "series": "replay", "tag": "THE REPLAY ROOM", "tagsub": "NZ V IND · 1ST TEST · DAY 1",
        "files": {"long": "x", "short": "x"}, "venue": {"time": "day", "crowd": [[20, 20, 22], [230, 230, 230], [25, 100, 200], [20, 60, 140]], "boards": [[20, 20, 22], [25, 100, 200]]},
        "thumb": {"kicker": "NZ V IND · 1ST TEST · DAY 1", "lines": [{"t": "70/5 TO"}, {"t": "243/5", "c": "gold"}], "hero": "173", "herosize": 420},
        "ig_cover": {"lines": [{"t": "HOW 70/5"}, {"t": "BECAME 243/5", "c": "gold"}], "sub": "1ST TEST · DAY 1", "hero": "173"}, "sources": SRC, "long": long, "short": short,
        "yt": {"long": {"title": "India vs New Zealand - 1st Test Day 1 Analysis | How 70/5 Became 243/5", "description": DL, "tags": TAGS},
               "short": {"title": "How 70/5 Became 243/5 | India vs New Zealand 1st Test Day 1 #Shorts", "description": DS, "tags": TAGS}}}
def describe(sc):
    t = sc["type"]; h = (sc.get("head") or {}).get("t") or sc.get("kicker") or ""
    extra = ""
    if sc.get("lines"): extra = " / ".join(l["t"] if isinstance(l, dict) else l for l in sc["lines"])
    elif sc.get("tiles"): extra = " | ".join(f'{x["v"]} {x["l"]}' for x in sc["tiles"])
    elif sc.get("items"): extra = " | ".join((x.get("h") or x.get("label") or x.get("who") or "") + (" " + str(x["value"]) if "value" in x else "") for x in sc["items"])
    elif sc.get("rows"): extra = " | ".join(" / ".join(str(y) for y in r[:3]) for r in sc["rows"])
    elif sc.get("events"): extra = " | ".join(f'{e["y"]} {e["t"]}' for e in sc["events"])
    elif "value" in sc: extra = f'{sc["value"]}{sc.get("suffix", "")} {sc.get("label", "")}'
    return f"{t}: {h}" + (f" ({extra})" if extra else "")


with open("docs/NZ_DAY1_SCRIPT.md", "w") as f:
    f.write("# NZ v IND, 1st Test, Day 1: script and storyboard (DRAFT for review, 19 Nov 2026)\nLong (lab look, about %d words, ~5.5 min) and vertical Instagram/Short (lab look, about %d words, ~160 s). Names are shown in Latin here; the build converts subcontinent names to Devanagari. Nothing is voiced or rendered until approved.\n" % (sum(len(x["vo"].split()) for x in long), sum(len(x["vo"].split()) for x in short)))
    for nm, lst in (("LONG", long), ("VERTICAL", short)):
        f.write(f"\n## {nm}\n")
        for i, x in enumerate(lst, 1): f.write(f"\n**{i}. {describe(x['scene'])}**\n> {x['vo']}\n")
c.save(spec); voice_lint.fix_spec(spec); spec["files"].setdefault("long", "_unused")
json.dump(spec, open("specs/nz_ind_1st_test_day1.json", "w"), ensure_ascii=False, indent=1)
print("long words", sum(len(s["vo"].split()) for s in long), "| short words", sum(len(s["vo"].split()) for s in short), "|", voice_lint.check_spec(spec, ("long", "short")) or "lint clean")
