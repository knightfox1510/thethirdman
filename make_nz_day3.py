"""Writes specs/nz_ind_1st_test_day3.json: The Replay Room Ep 6, India vs New Zealand, 1st Test, Day 3 (Basin Reserve, 21 Nov 2026), VERTICAL only (~155 s, lab look).
Source: the owner's Cricbuzz capture (India's innings to 486/4; NZ's Day-2 morning still missing), parsed by analysis/nz_day3.py. Records and milestones are Cricbuzz's own lists (printed on its commentary page),
said 'per Cricbuzz'.   python3 make_nz_day3.py"""
import json, os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voice_lint
from dataops import verify as V
from variants import YT_CTA

F = json.load(open("data/provenance/nz_day3_figures.json")); B = json.load(open("data/provenance/nz_day3_balls.json")); CB = "cricbuzz"
bt, bf = F["batters"], F["bowling_final"]
assert F["stumps"]["score"] == 486 and F["lunch"] == {"over": 65.6, "score": 239} and F["tea"] == {"over": 92.6, "score": 344}
assert [(w["over"], w["bat"], w["score"]) for w in F["wickets"]] == [(27.5, "Yashasvi Jaiswal", 130), (82.6, "Devdutt Padikkal", 295), (103.3, "Rahul", 386), (124.4, "Shubman Gill", 486)]
assert (bt["KL Rahul"]["batRuns"], bt["KL Rahul"]["batBalls"], bt["Devdutt Padikkal"]["batRuns"], bt["Devdutt Padikkal"]["batBalls"], bt["Shubman Gill"]["batRuns"], bt["Shubman Gill"]["batBalls"], bt["Rishabh Pant"]["batRuns"], bt["Rishabh Pant"]["batBalls"]) == (136, 290, 80, 175, 98, 146, 55, 62)
assert (bt["Shubman Gill"]["batFours"], bt["Shubman Gill"]["batSixes"]) == (9, 2)
assert (bf["Jacob Duffy"]["ov"], bf["Jacob Duffy"]["r"], bf["Jacob Duffy"]["w"], bf["Jacob Duffy"]["nb"], bf["Nathan Smith"]["nb"], bf["Glenn Phillips"]["nb"]) == (29, 181, 1, 7, 4, 3)
def sc(o): return [x for x in B if x["over"] <= o][-1]["score"]
assert (sc(38.6), sc(65.6), sc(92.6), sc(124.6), sc(79.6)) == (159, 239, 344, 486, 288)
S1, S2, S3 = (239 - 159, 27.0), (344 - 239, 27.0), (486 - 344, 32.0); assert (S1[0], S2[0], S3[0]) == (80, 105, 142)
rr = [round(S1[0] / 27, 2), round(S2[0] / 27, 2), round(S3[0] / 32, 2)]; assert rr == [2.96, 3.89, 4.44]
c = V.Claims("nz_ind_1st_test_day3")
c.check("India 486/4 at stumps (124.6 overs), lead of 118 over NZ's 368; Day 3 = 327 runs for 3 wickets in 86 overs (from 159/1 at 38.6)", (486, 4, 368, 118, 327, 3, 86), {CB: (486, 4, 368, 118, 327, 3, 86)}, scope="archive")
c.check("sessions: lunch 239/1 (80 in 27 overs), tea 344/2 (105 in 27), stumps 486/4 (142 in 32, two wickets: Rahul and Gill); run rates 2.96, 3.89, 4.44", (80, 105, 142, 2.96, 3.89, 4.44), {CB: (80, 105, 142, 2.96, 3.89, 4.44)}, scope="archive")
c.check("Rahul 100 off 207 balls (68.4), out b Smith 136 (290); Cricbuzz: first hundred in NZ and a Test hundred in all SENA countries", (100, 207, 136, 290), {CB: (100, 207, 136, 290)}, scope="archive")
c.check("Padikkal 80 (175) b Jamieson at 295/2; second-wicket stand with Rahul 165", (80, 175, 295, 165), {CB: (80, 175, 295, 165)}, scope="archive")
c.check("second new ball at 80 overs: 56 runs in the next 13 overs (288 at 79.6 to 344 at 92.6)", (288, 344, 56), {CB: (288, 344, 56)}, scope="archive")
c.check("Gill fifty (66 balls) with a six at 100.3 that took India past 368; Gill b Duffy 98 (146), 9 fours 2 sixes, third-last ball of the day", (66, 371, 98, 146, 9, 2), {CB: (66, 371, 98, 146, 9, 2)}, scope="archive")
c.check("Pant 52 off 55 (15 off 37, then 37 off 18), two sixes in a row off Duffy at 120.4/120.5; 55* (62)", (52, 55, 15, 37, 37, 18, 55, 62), {CB: (52, 55, 15, 37, 37, 18, 55, 62)}, scope="archive")
c.check("Cricbuzz list: highest scores as India Test captain in NZ: 192 Azharuddin, 116 Gavaskar, 103* Azharuddin, 98 Gill, 68 Dhoni", (192, 116, 103, 98, 68), {CB: (192, 116, 103, 98, 68)}, scope="archive")
c.check("Cricbuzz list: Gill dismissed in the 90s four times (91 Brisbane 2021, 91 Rajkot 2024, 90 Mumbai 2024, 98 Wellington 2026); Dhoni 4, Tendulkar 2 as captain; Dhoni 98 v Vettori, Nagpur 2010", (91, 91, 90, 98, 4, 2, 98), {CB: (91, 91, 90, 98, 4, 2, 98)}, scope="archive")
c.check("Cricbuzz list: all of India's top five past 50 in a Test innings: five times (Kolkata 1998, Mohali 1999, Brabourne 2009, Dharamsala 2024, Wellington 2026)", 5, {CB: 5}, scope="archive")
c.check("NZ bowling: Duffy 29-1-181-1 with 7 no-balls; Smith 4, Phillips 3 (14 in the innings); Henry 29-7-86-1; Jamieson 27-6-57-1", (29, 181, 7, 4, 3, 14), {CB: (29, 181, 7, 4, 3, 14)}, scope="archive")
IN = "data/licensed/in/"
COLD = {"type": "statement", "kicker": "DAY 3 · THREE BALLS TO GO", "lines": [{"t": "98."}, {"t": "TWO SHORT.", "c": "gold"}], "sub": "Gill b Duffy. But India led by 118."}
TURN = {"type": "stats", "head": {"t": "DAY THREE", "sub": "159/1 TO 486/4"}, "tiles": [{"v": "327", "l": "RUNS", "c": "gold"}, {"v": "3", "l": "WICKETS · 86 OVERS", "c": "ink"}, {"v": "+118", "l": "FROM 209 BEHIND", "c": "red"}]}
SESS = {"type": "bars", "head": {"t": "EVERY SESSION FASTER", "sub": "RUNS PER OVER · INDIA'S INNINGS"}, "max": 5, "dec": 2, "items": [{"label": "BEFORE LUNCH · 80 RUNS · 0 WKTS", "value": rr[0], "color": "ink"}, {"label": "LUNCH TO TEA · 105 RUNS · 1 WKT", "value": rr[1], "color": "ink"}, {"label": "TEA TO STUMPS · 142 RUNS · 2 WKTS", "value": rr[2], "color": "red"}]}
KLH = {"type": "photocard", "kicker": "KL RAHUL · DAY 3", "title": "100.", "img": IN + "nz_day3_rahul_hundred.jpg", "crop_short": (0, 250, 1280, 1103), "tag": "100 (207) · 68.4 OV", "name": "RAHUL", "mono": "FIRST HUNDRED IN NEW ZEALAND", "caption": "Per Cricbuzz: a Test hundred in all four SENA countries.", "chip": "136", "chip_sub": "OFF 290 BALLS"}
PAD = {"type": "stats", "head": {"t": "DEVDUTT PADIKKAL", "sub": "THE SECOND-WICKET STAND WITH RAHUL"}, "tiles": [{"v": "80", "l": "OFF 175 BALLS · b JAMIESON", "c": "gold"}, {"v": "165", "l": "STAND FOR THE SECOND WICKET", "c": "ink"}, {"v": "-20", "l": "FROM A HUNDRED", "c": "red"}]}
GILLP = {"type": "photocard", "kicker": "SHUBMAN GILL · INDIA CAPTAIN", "title": "98.", "img": IN + "nz_day3_batter_pull_apollo.jpg", "crop_short": (0, 280, 1280, 1133), "tag": "98 (146) · 9 FOURS · 2 SIXES", "name": "GILL", "mono": "b DUFFY · 124.4 · THIRD-LAST BALL", "caption": "Pushed in front of the pad. The ball sneaked through.", "chip": "98", "chip_sub": "OFF 146 BALLS"}
NEWB = {"type": "timeline", "head": {"t": "THE SECOND NEW BALL", "sub": "TAKEN AT 80 OVERS"}, "events": [{"y": "80.0", "t": "to tea: 56 runs in 13 overs, one wicket", "hl": True}, {"y": "100.3", "t": "Gill's fifty: a six, and India lead", "c": "red"}, {"y": "103.3", "t": "Rahul b Smith for 136", "c": "ink"}]}
PANT = {"type": "photocard", "kicker": "RISHABH PANT", "title": "52.", "img": IN + "nz_day3_pant_pull.jpg", "crop_short": (0, 380, 1280, 1233), "tag": "52 (55) · 2 SIXES IN 2 BALLS", "name": "PANT", "mono": "15 OFF 37, THEN 37 OFF 18", "caption": "The lead went past 100.", "chip": "55*", "chip_sub": "OFF 62 BALLS"}
CAPT = {"type": "bars", "head": {"t": "INDIA CAPTAINS IN NEW ZEALAND", "sub": "HIGHEST TEST SCORES · PER CRICBUZZ"}, "max": 200, "dec": 0, "items": [{"label": "AZHARUDDIN · AUCKLAND 1990", "value": 192, "color": "ink"}, {"label": "GAVASKAR · AUCKLAND 1976", "value": 116, "color": "ink"}, {"label": "AZHARUDDIN · WELLINGTON 1998", "value": 103, "color": "ink"}, {"label": "GILL · WELLINGTON 2026", "value": 98, "color": "red"}, {"label": "DHONI · WELLINGTON 2014", "value": 68, "color": "ink"}]}
NINE = {"type": "list", "head": {"t": "GILL IN THE NINETIES", "sub": "TEST DISMISSALS · PER CRICBUZZ"}, "items": [{"h": "91 · BRISBANE 2021", "d": "v Australia"}, {"h": "91 · RAJKOT 2024", "d": "v England"}, {"h": "90 · MUMBAI 2024", "d": "v New Zealand"}, {"h": "98 · WELLINGTON 2026", "d": "v New Zealand · like Dhoni, 98, Nagpur 2010", "c": "gold"}]}
FIVE = {"type": "list", "head": {"t": "ALL FIVE PAST FIFTY", "sub": "INDIA'S TOP FIVE · THE FIFTH TIME IN TESTS · PER CRICBUZZ"}, "items": [{"h": "JAISWAL 85", "d": "c Blundell b Henry"}, {"h": "RAHUL 136", "d": "b Smith"}, {"h": "PADIKKAL 80", "d": "b Jamieson"}, {"h": "GILL 98", "d": "b Duffy", "c": "gold"}, {"h": "PANT 55*", "d": "not out"}]}
ATT = {"type": "bars", "head": {"t": "NEW ZEALAND'S BOWLERS", "sub": "RUNS PER OVER · FULL INNINGS SO FAR"}, "max": 8, "dec": 2, "items": [{"label": "JAMIESON · 27-6-57-1", "value": round(57 / 27, 2), "color": "gold"}, {"label": "HENRY · 29-7-86-1", "value": round(86 / 29, 2), "color": "ink"}, {"label": "SMITH · 24-4-65-1 · 4 NO-BALLS", "value": round(65 / 24, 2), "color": "ink"}, {"label": "DUFFY · 29-1-181-1 · 7 NO-BALLS", "value": round(181 / 29, 2), "color": "red"}]}
POLL = {"type": "list", "head": {"t": "YOUR CALL", "sub": "INDIA LEAD BY 118 · COMMENT 1, 2 OR 3"}, "items": [{"h": "1 · UNDER 200", "d": "India are bowled out soon", "c": "gold"}, {"h": "2 · 200 TO 300", "d": "a sporting declaration"}, {"h": "3 · MORE", "d": "India bat New Zealand out of the game"}]}
short = [
    {"vo": "Three balls left in the day. Shubman Gill, on ninety-eight. Jacob Duffy bowls him through the gate. But day three was bigger than that. India started it two hundred and nine behind. They finished a hundred and eighteen ahead.", "scene": COLD},
    {"vo": "Three hundred and twenty-seven runs. Three wickets. Eighty-six overs.", "scene": TURN},
    {"vo": "And every session was faster. Eighty runs before lunch. A hundred and five to tea. A hundred and forty-two in the evening.", "scene": SESS},
    {"vo": "The morning was KL Rahul's. A hundred off two hundred and seven balls, his first in New Zealand, and by Cricbuzz's count a Test hundred in every SENA country.", "scene": KLH},
    {"vo": "Devdutt Padikkal added a hundred and sixty-five with him. Eighty, and then one ball from Kyle Jamieson that held its line. A hundred, missed by twenty.", "scene": PAD},
    {"vo": "Then the second new ball. Thirteen overs, fifty-six runs. Gill's fifty, a pull for six, put India in front. Rahul fell soon after, bowled by Nathan Smith for a hundred and thirty-six.", "scene": NEWB},
    {"vo": "Then Rishabh Pant. Fifteen off thirty-seven balls, and then thirty-seven off eighteen. Two sixes in two balls off Duffy. Fifty-two off fifty-five.", "scene": PANT},
    {"vo": "Gill made ninety-eight, off a hundred and forty-six balls. Nine fours, two sixes.", "scene": GILLP},
    {"vo": "It is the fourth-highest score by an India captain in New Zealand. Only Azharuddin, twice, and Gavaskar have made more.", "scene": CAPT},
    {"vo": "But it is his fourth dismissal in the nineties. Ninety-one, ninety-one, ninety, and now ninety-eight. The second India captain out in the nineties against New Zealand. The first was MS Dhoni, for an identical ninety-eight.", "scene": NINE},
    {"vo": "Still, all five of India's top five went past fifty. It has happened five times in Tests, says Cricbuzz.", "scene": FIVE},
    {"vo": "New Zealand's bowlers paid. Jacob Duffy: twenty-nine overs, one wicket, a hundred and eighty-one runs. Fourteen no-balls in the innings, seven of them his.", "scene": ATT},
    {"vo": "So, day four. India lead by a hundred and eighteen, with six wickets in hand. How big a lead do they set? Comment one, under two hundred. Two, two hundred to three hundred. Three, more.", "scene": POLL},
    dict(YT_CTA, vo="Subscribe, and we'll break down day four the same way."),
]
SRC = ["India's first innings on Day 3: Cricbuzz full commentary for New Zealand v India, 1st Test, 21 November 2026 (owner's capture; bowler lines, no-ball counts, and the record and milestone lists are Cricbuzz's). https://www.cricbuzz.com/live-cricket-full-commentary/161285/nz-vs-ind-1st-test-india-tour-of-new-zealand-2026",
       "Figures: analysis/nz_day3.py. Session splits and run rates are our arithmetic from Cricbuzz's scores."]
TAGS = ["India vs New Zealand", "India vs New Zealand 1st Test", "IND vs NZ 1st Test", "New Zealand vs India Test", "Shubman Gill", "KL Rahul", "Rishabh Pant", "Devdutt Padikkal", "Jacob Duffy", "Basin Reserve", "Wellington Test", "Day 3 analysis", "cricket analysis", "The Third Man"]
DS = ("India vs New Zealand, 1st Test day three: India 486 for 4, a lead of 118. KL Rahul's hundred, Devdutt Padikkal 80, Rishabh Pant's fifty, and Shubman Gill out for 98 off the third-last ball of the day. The records: Gill's fourth dismissal in the nineties, the fourth-highest score by an India captain in New Zealand. How big a lead do India set? Comment 1 under 200, 2 200 to 300, 3 more. Full breakdown on the channel.\n\n#INDvNZ #IndiaVsNewZealand #1stTest #Shorts")
spec = {"slug": "nz_ind_1st_test_day3", "theme": "lab", "theme_long": "lab", "captions": "lab", "captions_long": False, "series": "replay", "tag": "THE REPLAY ROOM", "tagsub": "NZ V IND · 1ST TEST · DAY 3",
        "files": {"long": "_unused", "short": "x"}, "venue": {"time": "day", "crowd": [[20, 20, 22], [230, 230, 230], [25, 100, 200], [20, 60, 140]], "boards": [[20, 20, 22], [25, 100, 200]]},
        "thumb": {"kicker": "NZ V IND · 1ST TEST · DAY 3", "lines": [{"t": "98. TWO"}, {"t": "RUNS SHORT", "c": "gold"}], "hero": "98", "herosize": 420},
        "ig_cover": {"lines": [{"t": "98. TWO"}, {"t": "RUNS SHORT", "c": "gold"}], "sub": "1ST TEST · DAY 3", "hero": "98"}, "sources": SRC, "short": short,
        "yt": {"short": {"title": "Gill Out for 98, India Lead by 118 | India vs New Zealand 1st Test Day 3 #Shorts", "description": DS, "tags": TAGS}}}
c.save(spec); voice_lint.fix_spec(spec)
json.dump(spec, open("specs/nz_ind_1st_test_day3.json", "w"), ensure_ascii=False, indent=1)
print("short words", sum(len(s["vo"].split()) for s in short), "|", voice_lint.check_spec(spec, ("short",)) or "lint clean", "|", spec["files"])
