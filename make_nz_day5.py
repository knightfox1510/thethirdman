"""Writes specs/nz_ind_1st_test_day5.json: The Replay Room Ep 8, India vs New Zealand, 1st Test, Day 5 (Basin Reserve, 23 Nov 2026), VERTICAL (~165 s, lab look): how NZ batted out the day (239/5, a draw), the chances, the
stand, India's plan, did India give up too soon, the WTC cost. Source: the owner's ball-by-ball capture (analysis/nz_day5.py, analysis/shots.py with SHOTS_IN=nz_ind_1st_test_day5.json SHOTS_OUT=nz_shots_d5.json SHOTS_INN=3).
Records, the WTC table and the pitch report are the capture's own notes, said 'in our records'; no source is named on screen or in the voice-over.   python3 make_nz_day5.py"""
import json, os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voice_lint
from dataops import verify as V
from variants import YT_CTA

ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split(); TENS = "x x twenty thirty forty fifty sixty seventy eighty ninety".split()
def w(n):
    n = int(n)
    if n < 20: return ONES[n]
    if n < 100: return TENS[n // 10] + ("-" + ONES[n % 10] if n % 10 else "")
    h, r = divmod(n, 100); return ONES[h] + " hundred" + (" and " + w(r) if r else "")
F = json.load(open("data/provenance/nz_day5_figures.json")); F4 = json.load(open("data/provenance/nz_day4_figures.json")); SH = json.load(open("data/provenance/nz_shots_d5.json")); CB = "cricbuzz"
bt, bw = F["batters"], F["bowlers"]; b4 = F4["inn3"]["bowlers"]
assert F["end"] == {"over": 119.6, "score": 239} and [x["bat"] for x in F["wickets"]] == ["Devon Conway", "Rachin Ravindra", "Tom Blundell"]
assert (F["morning"]["runs"], F["morning"]["wkts"], F["morning"]["overs"], F["middle"]["runs"], F["middle"]["wkts"], F["middle"]["overs"], F["evening"]["runs"], F["evening"]["wkts"], F["evening"]["overs"]) == (38, 2, 26.0, 49, 1, 25.0, 33, 0, 24.0)
assert 239 - 119 == 120 == 38 + 49 + 33 and 26 + 25 + 24 == 75 and round(120 / 75, 2) == 1.6
D5 = [o for o in SH if o["inn"] == 3 and o["over"] > 44.6]; dots = sum(1 for o in D5 if o["res"] == "no run"); nb = len(D5); dotpct = round(100 * dots / nb)
assert (dots, nb) == (387, 451) and dotpct == 86
d5 = {k: dict(ov=round(bw[k]["ov"] - b4.get(k, {"ov": 0})["ov"]), m=bw[k]["m"] - b4.get(k, {"m": 0})["m"], r=bw[k]["r"] - b4.get(k, {"r": 0})["r"], w=bw[k]["w"] - b4.get(k, {"w": 0})["w"]) for k in bw}
assert sum(v["m"] for v in d5.values()) == 34 and sum(v["ov"] for v in d5.values()) == 75 and sum(bw[k]["m"] for k in bw) == 42
assert d5["Prasidh Krishna"] == dict(ov=11, m=8, r=3, w=1) and d5["Washington Sundar"] == dict(ov=27, m=12, r=49, w=1)
mi, ph = bt["Daryl Mitchell"], bt["Glenn Phillips"]; assert (mi["batRuns"], mi["batBalls"], mi["batDots"], ph["batRuns"], ph["batBalls"], ph["batDots"]) == (49, 186, 160, 26, 126, 111) and 239 - 176 == 63 and 119.6 - 76.6 == 43.0 and mi["batBalls"] + ph["batBalls"] == 312
c = V.Claims("nz_ind_1st_test_day5")
c.check("Day 5: NZ 119/2 to 239/5 in 75 overs (120 runs, 1.60 an over): morning 38/2 in 26 overs, to tea 49/1 in 25, last session 33/0 in 24; India took 3 wickets (Conway 65, Rachin 37, Blundell 15)", (119, 239, 75, 120, 38, 49, 33, 3), {CB: (119, 239, 75, 120, 38, 49, 33, 3)}, scope="archive")
c.check("387 dot balls of 451 on Day 5 (86%); 34 maidens in 75 overs; India's innings 42 maidens, the most by a team innings in the WTC 2025-27 cycle", (387, 451, 34, 42), {CB: (387, 451, 34, 42)}, scope="archive")
c.check("Mitchell 49* (186 balls, 160 dots) and Phillips 26* (126, 111 dots): 63* in 259 balls over 43 overs (176/5 to 239/5)", (49, 186, 160, 26, 126, 111, 63, 259, 43), {CB: (49, 186, 160, 26, 126, 111, 63, 259, 43)}, scope="archive")
c.check("43 overs: second-most for an NZ sixth-wicket-or-lower stand in the third innings of a drawn Test this century; record 123 overs, McCullum and Watling (352), Wellington 2014 v India", (43, 123, 352), {CB: (43, 123, 352)}, scope="archive")
c.check("Mitchell's chances: run-out missed by Akash Deep (73.1, on 12), bat-pad off Prasidh with no forward short leg (88.2, on 24), Kamboj kicker, Padikkal could not hold (94.4, on 24)", (12, 24, 24), {CB: (12, 24, 24)}, scope="archive")
c.check("Prasidh Day 5: 11-8-3-1; Washington 27-12-49-1; Bumrah 11-6-9-0; Kamboj 13-4-24-1; Akash Deep 10-4-22-0", (11, 8, 3, 1), {CB: (11, 8, 3, 1)}, scope="archive")
c.check("conditions: breeze 22 km/h from the north, 16 degrees, some cloud, no rain threat; pitch dried out, grass dead, still a very good batting surface", (22, 16), {CB: (22, 16)}, scope="archive")
c.check("WTC: both sides 4 points; NZ 66.67 percent, slip behind Australia to third; India 4th on 50, need to win all next 6 Tests; 16 points missed across two drawn Tests", (4, 66.67, 50, 6, 16), {CB: (4, 66.67, 50, 6, 16)}, scope="archive")
c.check("Handshake with about an hour left (17:40 local): India had 3 wickets in 75 overs (one every 25); Nicholls 175* Player of the Match, Phillips 118 in NZ's 368", (3, 75, 175, 118, 368), {CB: (3, 75, 175, 118, 368)}, scope="archive")
OVERS = [(r, wk) for _, r, wk in F["per_over"]]; assert len(OVERS) == 75 and sum(r for r, _ in OVERS) in range(118, 125) and sum(1 for _, wk in OVERS if wk) == 3
def panel(lo, hi, title):
    k = [o for o in SH if o["inn"] == 3 and lo < o["over"] <= hi and o["line"] and o["len"] and o["line"] != "wide"]; n = len(k)
    balls = [[o["line"], o["len"], "w" if o["wkt"] else ("b" if o["res"] in ("FOUR", "SIX") else ("r" if o["runs"] > 0 else "d"))] for o in k]
    stump = round(100 * sum(1 for o in k if o["line"] in ("off", "outside_off")) / n); mid = round(100 * sum(1 for o in k if o["line"] == "middle") / n)
    return dict(title=title, n=n, balls=balls, cells={}), stump, mid
PA, off1, mid1 = panel(44.6, 70.6, "BEFORE LUNCH"); PB, off2, mid2 = panel(70.6, 95.6, "LUNCH TO TEA")
PA["stats"] = [(f"{off1}%", "ON OR OUTSIDE OFF"), (f"{mid1}%", "ON MIDDLE")]; PB["stats"] = [(f"{off2}%", "ON OR OUTSIDE OFF"), (f"{mid2}%", "ON MIDDLE")]
assert off2 > off1 and mid1 > mid2, (off1, off2, mid1, mid2)
c.check("India's lines (our read, balls with a stated line and length): on or outside off %d%% before lunch -> %d%% lunch to tea; on middle %d%% -> %d%%" % (off1, off2, mid1, mid2), (off1, off2, mid1, mid2), {CB: (off1, off2, mid1, mid2)}, scope="archive")
IN = "data/licensed/in/"
COLD = {"type": "statement", "kicker": "DAY 5 · THE FIRST TEST IS DRAWN", "lines": [{"t": "239/5."}, {"t": "A DRAW.", "c": "gold"}], "sub": "India needed eight wickets. They took three."}
DAY = {"type": "stats", "head": {"t": "A DAY OF BLOCKING", "sub": "NEW ZEALAND · 119/2 TO 239/5 · 75 OVERS"}, "tiles": [{"v": "1.60", "l": "RUNS AN OVER", "c": "gold"}, {"v": f"{dotpct}%", "l": "DOT BALLS · 387 OF 451", "c": "red"}, {"v": "34", "l": "MAIDENS IN 75 OVERS", "c": "ink"}]}
STRIP = {"type": "overstrip", "head": {"t": "THE DAY, OVER BY OVER", "sub": "RUNS IN EACH OVER · RED = WICKET · GREEN = MAIDEN"}, "overs": OVERS, "session_cuts": (26, 51), "legal_lines": None, "legend_lines": [("BEFORE LUNCH: 38 RUNS, 2 WICKETS", "ink"), ("LUNCH TO TEA: 49 RUNS, 1 WICKET", "ink"), ("LAST SESSION: 33 RUNS, NO WICKET", "red")], "footnote": "OUR BALL-BY-BALL · LUNCH AFTER 26 OVERS, TEA AFTER 51"}
rr = [round(38 / 26, 2), round(49 / 25, 2), round(33 / 24, 2)]
COND = {"type": "stats", "head": {"t": "THE CONDITIONS", "sub": "BASIN RESERVE · DAY FIVE · IN OUR RECORDS"}, "tiles": [{"v": "22 KM/H", "l": "BREEZE FROM THE NORTH", "c": "gold"}, {"v": "16°C", "l": "SOME CLOUD, NO RAIN", "c": "ink"}, {"v": "DEAD", "l": "GRASS · PITCH DRIED OUT", "c": "red"}]}
PITCH = {"type": "pitchtop", "head": {"t": "WHERE INDIA BOWLED", "sub": "THE PITCH FROM ABOVE · EACH DOT A DELIVERY · ILLUSTRATIVE"}, "panels": [PA, PB], "footnote": "POSITIONS ARE OUR READ OF THE BALL-BY-BALL TEXT (BALLS WITH A STATED LINE AND LENGTH) · BATTER AT THE TOP"}
MORN = {"type": "photocard", "kicker": "THE MORNING · TWO WICKETS", "title": "2 for 38.", "img": IN + "nz_day5_pant_catch.jpg", "crop_short": (0, 0, 1280, 853), "tag": "38 RUNS IN 26 OVERS", "name": "CONWAY AND RACHIN OUT", "mono": "CONWAY 65 (165) · RACHIN 37 (129)", "caption": "Conway c Pant b Sundar. Rachin c Rahul b Prasidh. Then the shutters came down.", "chip": "139/4", "chip_sub": "BY THE 60TH OVER"}
LIFE = {"type": "timeline", "head": {"t": "DARYL MITCHELL'S THREE LIVES", "sub": "ALL THREE IN THE SESSION BEFORE TEA"}, "events": [{"y": "73.1", "t": "On 12: Akash Deep misses a run-out", "c": "red"}, {"y": "88.2", "t": "On 24: bat-pad off Prasidh, no short leg in place", "hl": True}, {"y": "94.4", "t": "On 24: Kamboj kicker, Padikkal can't hold on", "c": "red"}]}
STAND = {"type": "photocard", "kicker": "THE WALL · 176/5 TO 239/5", "title": "63*.", "img": IN + "nz_day5_mitchell_phillips.jpg", "crop_short": (0, 0, 1280, 853), "tag": "259 BALLS · 43 OVERS", "name": "MITCHELL AND PHILLIPS", "mono": "49* OFF 186 · 26* OFF 126", "caption": "Over three hundred balls between them. Not one more wicket.", "chip": "63*", "chip_sub": "259 BALLS"}
dpc = [("PHILLIPS", ph["batDots"], ph["batBalls"]), ("MITCHELL", mi["batDots"], mi["batBalls"]), ("RACHIN", bt["Rachin Ravindra"]["batDots"], bt["Rachin Ravindra"]["batBalls"]), ("BLUNDELL", bt["Tom Blundell"]["batDots"], bt["Tom Blundell"]["batBalls"]), ("CONWAY", bt["Devon Conway"]["batDots"], bt["Devon Conway"]["batBalls"])]
DOTS = {"type": "bars", "head": {"t": "SHARE OF DOT BALLS", "sub": "NEW ZEALAND'S SECOND INNINGS · BY BATTER"}, "max": 100, "dec": 0, "items": [{"label": f"{n} · {d} DOTS OF {b}", "value": round(100 * d / b), "color": "red" if n in ("PHILLIPS", "MITCHELL") else "ink"} for n, d, b in dpc]}
REC = {"type": "compare", "head": {"t": "WELLINGTON REMEMBERS", "sub": "NZ SIXTH-WICKET-OR-LOWER STANDS IN A DRAWN TEST'S THIRD INNINGS · IN OUR RECORDS"}, "a": {"name": "MITCHELL + PHILLIPS 2026", "color": "red"}, "b": {"name": "McCULLUM + WATLING 2014", "color": "ink"}, "rows": [["OVERS BATTED", "43", "123", "b"], ["RUNS", "63*", "352", "b"]]}
BOWL = {"type": "bars", "head": {"t": "INDIA'S BOWLING TODAY", "sub": "OVERS-MAIDENS-RUNS-WICKETS · 34 MAIDENS IN 75 OVERS"}, "max": 3, "dec": 2, "items": [{"label": "PRASIDH · 11-8-3-1", "value": round(3 / 11, 2), "color": "gold"}, {"label": "BUMRAH · 11-6-9-0", "value": round(9 / 11, 2), "color": "ink"}, {"label": "SUNDAR · 27-12-49-1", "value": round(49 / 27, 2), "color": "ink"}, {"label": "KAMBOJ · 13-4-24-1", "value": round(24 / 13, 2), "color": "ink"}, {"label": "AKASH DEEP · 10-4-22-0", "value": round(22 / 10, 2), "color": "red"}]}
SHAKE = {"type": "photocard", "kicker": "ABOUT AN HOUR LEFT", "title": "Handshake.", "img": IN + "nz_day5_handshake.jpg", "crop_short": (0, 0, 1280, 853), "tag": "5 WICKETS NEEDED", "name": "INDIA CALL IT", "mono": "THREE WICKETS IN 75 OVERS: ONE EVERY 25", "caption": "Mitchell offered a hand. Gill took it.", "chip": "239/5", "chip_sub": "DRAW AGREED"}
PART = {"type": "photocard", "kicker": "THE LAST OVERS", "title": "Part-timers.", "img": IN + "nz_day5_jaiswal_bowling.jpg", "crop_short": (0, 0, 1280, 853), "tag": "JAISWAL 2-0-4-0 · JUREL 1-0-1-0", "name": "JAISWAL AND JUREL", "mono": "BUMRAH: 2 OVERS IN THE LAST SESSION", "caption": "Prasidh bowled 2 of the last 24 overs.", "chip": "24", "chip_sub": "OVERS IN THE LAST SESSION"}
WTC = {"type": "list", "head": {"t": "THE WTC COST", "sub": "BOTH SIDES GET FOUR POINTS · IN OUR RECORDS"}, "items": [{"h": "NEW ZEALAND 66.67%", "d": "slip behind Australia to third", "c": "gold"}, {"h": "INDIA FOURTH ON 50", "d": "must win all six remaining Tests"}, {"h": "16 POINTS MISSED", "d": "across two drawn Tests in a row"}, {"h": "SRI LANKA, THEN HERE", "d": "India could not close out either"}]}
POLL = {"type": "list", "head": {"t": "YOUR CALL", "sub": "DID INDIA GIVE UP TOO SOON? COMMENT 1, 2 OR 3"}, "items": [{"h": "1 · YES", "d": "an hour was enough to try", "c": "gold", "cue": "yes"}, {"h": "2 · NO", "d": "the pitch had nothing left", "cue": "two"}, {"h": "3 · FAIR", "d": "right call, hard to argue", "cue": "fair"}]}
TEST = {"type": "stats", "head": {"t": "THE TEST IN THREE NUMBERS", "sub": "WELLINGTON · 19 TO 23 NOVEMBER"}, "tiles": [{"v": "368", "l": "NEW ZEALAND · NICHOLLS 175* (PLAYER OF THE MATCH)", "c": "ink"}, {"v": "720/9", "l": "INDIA DECLARED · LEAD 352", "c": "gold"}, {"v": "239/5", "l": "NEW ZEALAND SECOND INNINGS · DRAW", "c": "red"}]}
short = [
    {"vo": "Two thirty-nine for five, and the first Test is drawn. India needed eight wickets on day five. They took three. Here is how New Zealand held on.", "scene": COLD},
    {"vo": "One point six runs an over. Eighty-six per cent of balls were dots. Thirty-four maidens in seventy-five overs. Blocking, by plan.", "scene": DAY},
    {"vo": "The whole day over by over. Two wickets before lunch, one after, and none in the last session.", "scene": STRIP},
    {"vo": "The conditions gave India little: a twenty-two kilometre breeze, sixteen degrees, dead grass, a dried-out pitch.", "scene": COND},
    {"vo": f"India's lines tightened. Before lunch, {w(off1)} per cent were on or outside off. After lunch, {w(off2)}. The stumps were no longer under attack.", "scene": PITCH},
    {"vo": "The morning gave India two: Conway, caught by Rishabh Pant off Washington Sundar, then Rachin Ravindra at gully. Thirty-eight runs in twenty-six overs.", "scene": MORN},
    {"vo": "India's best hope was Daryl Mitchell, and he had three lives: a run-out missed, a bat-pad with no short leg, a kicker Padikkal could not hold.", "scene": LIFE},
    {"vo": "Then the wall. Mitchell and Phillips: sixty-three unbeaten, off two hundred and fifty-nine balls, forty-three overs.", "scene": STAND},
    {"vo": f"Phillips left {w(ph['batDots'])} of {w(ph['batBalls'])} balls alone. Mitchell, {w(mi['batDots'])} of {w(mi['batBalls'])}.", "scene": DOTS},
    {"vo": "It is the second-longest stand like it by New Zealand this century. The record, a hundred and twenty-three overs, was set on this ground, against India.", "scene": REC},
    {"vo": "India bowled well. Prasidh Krishna: eleven overs, eight maidens, three runs. Forty-two maidens in the innings, the most by any team in this cycle.", "scene": BOWL},
    {"vo": "So, too soon? With about an hour left, Mitchell offered his hand and Shubman Gill took it. Three wickets in seventy-five overs, one every twenty-five. India needed five.", "scene": SHAKE},
    {"vo": "The last overs went to part-timers, Jaiswal and Jurel. Bumrah bowled two overs in the last session. Prasidh, two.", "scene": PART},
    {"vo": "The cost. New Zealand fall to sixty-six point six seven per cent, behind Australia. India stay fourth on fifty, and need all six remaining Tests. Sixteen points missed in two draws.", "scene": WTC},
    {"vo": "The match in three numbers. New Zealand three sixty-eight, Henry Nicholls one seventy-five not out, the Player of the Match. India seven twenty for nine. And New Zealand two thirty-nine for five.", "scene": TEST},
    {"vo": "Did India give up too soon? Comment one, yes. Two, no. Three, fair.", "scene": POLL},
    dict(YT_CTA, vo="Subscribe, and we'll break down the series decider the same way."),
]
SRC = ["Day 5 ball-by-ball (New Zealand 239/5, draw): Cricbuzz full commentary for New Zealand v India, 1st Test, 23 November 2026 (owner's capture; bowler lines, records, WTC table, pitch report and match notes are Cricbuzz's). https://www.cricbuzz.com/live-cricket-full-commentary/161285/nz-vs-ind-1st-test-india-tour-of-new-zealand-2026",
       "Figures: analysis/nz_day5.py, analysis/shots.py. Session splits and run rates are our arithmetic; the pitch map is our read of the commentary text (approximate zones)."]
TAGS = ["India vs New Zealand", "India vs New Zealand 1st Test", "IND vs NZ 1st Test", "New Zealand vs India Test", "Daryl Mitchell", "Glenn Phillips", "Shubman Gill", "Prasidh Krishna", "Washington Sundar", "Basin Reserve", "Wellington Test", "WTC", "Day 5 analysis", "cricket analysis", "The Third Man"]
DS = ("India vs New Zealand, 1st Test day five: the draw at the Basin Reserve. New Zealand 239 for 5 after batting 75 overs: 1.60 runs an over, 86 per cent dot balls. Daryl Mitchell's three lives, the Mitchell and Phillips stand of 63 off 259 balls, India's bowling plan, the WTC cost, and did India give up too soon? Comment 1 yes, 2 no, 3 fair. Full breakdown on the channel.\n\n#INDvNZ #IndiaVsNewZealand #1stTest #Shorts")
spec = {"slug": "nz_ind_1st_test_day5", "theme": "lab", "theme_long": "lab", "captions": "lab", "captions_long": False, "series": "replay", "tag": "THE REPLAY ROOM", "tagsub": "NZ V IND · 1ST TEST · DAY 5",
        "files": {"long": "_unused", "short": "x"}, "venue": {"time": "day", "crowd": [[20, 20, 22], [230, 230, 230], [25, 100, 200], [20, 60, 140]], "boards": [[20, 20, 22], [25, 100, 200]]},
        "thumb": {"kicker": "NZ V IND · 1ST TEST · DAY 5", "lines": [{"t": "8 NEEDED."}, {"t": "3 TAKEN.", "c": "gold"}], "hero": "239", "herosize": 420},
        "ig_cover": {"lines": [{"t": "8 NEEDED."}, {"t": "3 TAKEN.", "c": "gold"}], "sub": "1ST TEST · DAY 5 · DRAWN", "hero": "239"}, "sources": SRC, "short": short,
        "yt": {"short": {"title": "India Needed 8, Took 3: How New Zealand Drew | India vs New Zealand 1st Test Day 5 #Shorts", "description": DS, "tags": TAGS}}}
c.save(spec); voice_lint.fix_spec(spec)
json.dump(spec, open("specs/nz_ind_1st_test_day5.json", "w"), ensure_ascii=False, indent=1)
print("short words", sum(len(s["vo"].split()) for s in short), "|", voice_lint.check_spec(spec, ("short",)) or "lint clean", "|", spec["files"], "| lines", off1, off2, mid1, mid2, PA["n"], PB["n"])
