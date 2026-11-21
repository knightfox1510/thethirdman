"""Writes specs/nz_ind_1st_test_day3.json: The Replay Room Ep 6, India vs New Zealand, 1st Test, Day 3 (Basin Reserve, 21 Nov 2026), VERTICAL only (~155 s, lab look).
Source: the owner's Cricbuzz capture (India's innings to 486/4; NZ's Day-2 morning still missing), parsed by analysis/nz_day3.py. Records and milestones are Cricbuzz's own lists (printed on its commentary page),
said 'per Cricbuzz'.   python3 make_nz_day3.py"""
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
SH = json.load(open("data/provenance/nz_shots.json"))
def wagon(bat, day=None):
    xs = [o for o in SH if o["bat"] == bat and o["ang"] is not None and (day is None or o["day"] == day)]
    shots = [[o["ang"], min(o["runs"], 6) if o["res"] != "no ball" else 4, "s" if o["res"] == "SIX" else ("f" if o["res"] == "FOUR" or o["runs"] >= 4 else "n")] for o in xs]
    tot = sum(o["runs"] for o in xs); off = sum(o["runs"] for o in xs if o["ang"] > 0); leg = sum(o["runs"] for o in xs if o["ang"] < 0); st = sum(o["runs"] for o in xs if o["ang"] == 0)
    return shots, dict(n=len(xs), tot=tot, off=off, leg=leg, st=st, fours=sum(1 for q in shots if q[2] == "f"), sixes=sum(1 for q in shots if q[2] == "s"))
KS, KW = wagon("KL Rahul"); GS, GW = wagon("Shubman Gill"); PS, PW = wagon("Rishabh Pant")
pant_short = [o for o in SH if o["bat"] == "Rishabh Pant" and o["day"] == 3 and o["len"] == "short"]; PSH = (len(pant_short), sum(o["runs"] for o in pant_short))
def panel(sess, title):
    xs = [o for o in SH if o["sess"] == sess and o["line"] and o["len"] and o["line"] != "wide"]; cells = collections.Counter(f'{o["line"]}|{"full" if o["len"] == "yorker" else o["len"]}' for o in xs)
    n = len(xs); line = collections.Counter(o["line"] for o in xs); ln = collections.Counter(o["len"] for o in xs)
    return dict(title=title, n=n, cells=dict(cells)), {k: round(100 * v / n) for k, v in line.items()}, {k: round(100 * v / n) for k, v in ln.items()}
P1, L1, E1 = panel(1, "BEFORE LUNCH"); P3, L3, E3 = panel(3, "AFTER TEA")
assert L1["off"] + L1["outside_off"] >= 80 and L3["leg"] >= 24, (L1, L3)
off1 = L1["off"] + L1["outside_off"]; leg3 = L3["leg"]; short3 = E3["short"]
P1["stats"] = [(f"{off1}%", "ON OR OUTSIDE OFF"), (f'{L1["leg"]}%', "ON THE LEG SIDE")]; P3["stats"] = [(f'{L3["off"] + L3["outside_off"]}%', "ON OR OUTSIDE OFF"), (f"{leg3}%", "ON THE LEG SIDE")]
print("wagon KL", KW, "Gill", GW, "Pant", PW, "pant short", PSH, "| pitch", off1, L1["leg"], leg3, short3, P1["n"], P3["n"])
c.check("our read of NZ's lines: before lunch %d%% on or outside off, %d%% leg side; after tea %d%% leg side (zones from the commentary text)" % (off1, L1["leg"], leg3), (off1, L1["leg"], leg3), {CB: (off1, L1["leg"], leg3)}, scope="archive")
c.check("Pant vs short balls on Day 3: %d balls, %d runs (our read)" % PSH, PSH, {CB: PSH}, scope="archive")
COLD = {"type": "statement", "kicker": "DAY 3 · THREE BALLS TO GO", "lines": [{"t": "98."}, {"t": "TWO SHORT.", "c": "gold"}], "sub": "Gill b Duffy. But India led by 118."}
SESS = {"type": "bars", "head": {"t": "EVERY SESSION FASTER", "sub": "RUNS PER OVER · 159/1 TO 486/4 · +118"}, "max": 5, "dec": 2, "items": [{"label": "BEFORE LUNCH · 80 RUNS · 0 WKTS", "value": rr[0], "color": "ink"}, {"label": "LUNCH TO TEA · 105 RUNS · 1 WKT", "value": rr[1], "color": "ink"}, {"label": "TEA TO STUMPS · 142 RUNS · 2 WKTS", "value": rr[2], "color": "red"}]}
PITCH = {"type": "pitchzones", "head": {"t": "WHERE NEW ZEALAND BOWLED", "sub": "SHARE OF DELIVERIES · LINE BY LENGTH · ILLUSTRATIVE"}, "panels": [P1, P3], "footnote": "OUR READ OF THE BALL-BY-BALL TEXT · BATTER'S END AT THE TOP · SHADE = SHARE OF THE PANEL'S BALLS"}
KLH = {"type": "photocard", "kicker": "KL RAHUL · DAY 3", "title": "100.", "img": IN + "nz_day3_rahul_hundred.jpg", "crop_short": (0, 250, 1280, 1103), "tag": "100 (207) · 68.4 OV", "name": "RAHUL", "mono": "FIRST HUNDRED IN NEW ZEALAND", "caption": "A Test hundred in all four SENA countries.", "chip": "136", "chip_sub": "OFF 290 BALLS"}
KLW = {"type": "wagon", "head": {"t": "RAHUL'S 136", "sub": "WHERE THE RUNS WENT · ILLUSTRATIVE"}, "pts": KS, "chips": [(f'{KW["leg"]}', "RUNS LEG SIDE"), (f'{KW["off"]}', "RUNS OFF SIDE"), (f'{KW["st"]}', "STRAIGHT")], "footnote": f'{KW["n"]} SCORING SHOTS PLACED · ZONES READ FROM THE BALL-BY-BALL TEXT'}
PAD = {"type": "photocard", "kicker": "DEVDUTT PADIKKAL", "title": "80.", "img": IN + "nz_day3_padikkal_cut.jpg", "crop_short": (150, 20, 1150, 667), "tag": "80 (175) · b JAMIESON", "name": "PADIKKAL", "mono": "165 FOR THE SECOND WICKET", "caption": "One ball that held its line. A hundred, missed by twenty.", "chip": "80", "chip_sub": "OFF 175 BALLS"}
PANTW = {"type": "wagon", "head": {"t": "PANT'S 55*", "sub": "WHERE THE RUNS WENT · ILLUSTRATIVE"}, "pts": PS, "photo": {"img": IN + "nz_day3_pant_pull.jpg", "crop": (300, 560, 1000, 1260)}, "chips": [(f'{bt["Rishabh Pant"]["batSixes"]}', "SIXES"), (f'{bt["Rishabh Pant"]["batFours"]}', "FOURS"), (f"{PSH[1]}", f"RUNS OFF {PSH[0]} SHORT BALLS")], "footnote": f'{PW["n"]} SCORING SHOTS PLACED · ZONES READ FROM THE BALL-BY-BALL TEXT'}
GILLW = {"type": "wagon", "head": {"t": "GILL'S 98", "sub": "WHERE THE RUNS WENT · ILLUSTRATIVE"}, "pts": GS, "photo": {"img": IN + "nz_day3_batter_pull_apollo.jpg", "crop": (330, 280, 1030, 980)}, "chips": [(f'{bt["Shubman Gill"]["batFours"]}', "FOURS"), (f'{bt["Shubman Gill"]["batSixes"]}', "SIXES"), ("146", "BALLS FACED")], "footnote": f'{GW["n"]} SCORING SHOTS PLACED · ZONES READ FROM THE BALL-BY-BALL TEXT'}
CAPT = {"type": "bars", "head": {"t": "INDIA CAPTAINS IN NEW ZEALAND", "sub": "HIGHEST TEST SCORES · IN OUR RECORDS"}, "max": 200, "dec": 0, "items": [{"label": "AZHARUDDIN · AUCKLAND 1990", "value": 192, "color": "ink"}, {"label": "GAVASKAR · AUCKLAND 1976", "value": 116, "color": "ink"}, {"label": "AZHARUDDIN · WELLINGTON 1998", "value": 103, "color": "ink"}, {"label": "GILL · WELLINGTON 2026", "value": 98, "color": "red"}, {"label": "DHONI · WELLINGTON 2014", "value": 68, "color": "ink"}]}
NINE = {"type": "list", "head": {"t": "GILL IN THE NINETIES", "sub": "TEST DISMISSALS · IN OUR RECORDS"}, "items": [{"h": "91 · BRISBANE 2021", "d": "v Australia"}, {"h": "91 · RAJKOT 2024", "d": "v England"}, {"h": "90 · MUMBAI 2024", "d": "v New Zealand"}, {"h": "98 · WELLINGTON 2026", "d": "v New Zealand · like Dhoni, 98, Nagpur 2010", "c": "gold"}]}
FIVE = {"type": "list", "head": {"t": "ALL FIVE PAST FIFTY", "sub": "INDIA'S TOP FIVE · THE FIFTH TIME IN TESTS"}, "items": [{"h": "JAISWAL 85", "d": "c Blundell b Henry"}, {"h": "RAHUL 136", "d": "b Smith"}, {"h": "PADIKKAL 80", "d": "b Jamieson"}, {"h": "GILL 98", "d": "b Duffy", "c": "gold"}, {"h": "PANT 55*", "d": "not out"}]}
ATT = {"type": "bars", "head": {"t": "NEW ZEALAND'S BOWLERS", "sub": "RUNS PER OVER · FULL INNINGS SO FAR"}, "max": 8, "dec": 2, "items": [{"label": "JAMIESON · 27-6-57-1", "value": round(57 / 27, 2), "color": "gold"}, {"label": "HENRY · 29-7-86-1", "value": round(86 / 29, 2), "color": "ink"}, {"label": "SMITH · 24-4-65-1 · 4 NO-BALLS", "value": round(65 / 24, 2), "color": "ink"}, {"label": "DUFFY · 29-1-181-1 · 7 NO-BALLS", "value": round(181 / 29, 2), "color": "red"}]}
POLL = {"type": "list", "head": {"t": "YOUR CALL", "sub": "INDIA LEAD BY 118 · COMMENT 1, 2 OR 3"}, "items": [{"h": "1 · UNDER 200", "d": "India are bowled out soon", "c": "gold"}, {"h": "2 · 200 TO 300", "d": "a sporting declaration"}, {"h": "3 · MORE", "d": "India bat New Zealand out of the game"}]}
short = [
    {"vo": "Three balls left. Shubman Gill, on ninety-eight. Jacob Duffy bowls him through the gate. But India started day three two hundred and nine behind. They finished a hundred and eighteen ahead.", "scene": COLD},
    {"vo": "Three hundred and twenty-seven runs, three wickets, and every session faster. Eighty before lunch, a hundred and five to tea, a hundred and forty-two after.", "scene": SESS},
    {"vo": f"New Zealand began stump to stump. Before lunch, {w(off1)} per cent were on or outside off. By the evening, a quarter were on the leg side.", "scene": PITCH},
    {"vo": "The morning was KL Rahul's. A hundred off two hundred and seven balls, his first in New Zealand, and a Test hundred in every SENA country.", "scene": KLH},
    {"vo": f"{w(KW['leg']).capitalize()} of his placed runs came through the leg side, {w(KW['off'])} through the off.", "scene": KLW},
    {"vo": "Devdutt Padikkal added a hundred and sixty-five with him. Eighty, then one Jamieson ball held its line. A hundred, missed by twenty.", "scene": PAD},
    {"vo": f"Then Rishabh Pant. Fifteen off thirty-seven, then thirty-seven off eighteen. Two sixes in two balls off Duffy. The short ball gave him {w(PSH[1])} runs from {w(PSH[0])} balls.", "scene": PANTW},
    {"vo": "Gill's fifty was a pull for six, and it put India in front. Ninety-eight off a hundred and forty-six, nine fours, two sixes, mostly on the leg side.", "scene": GILLW},
    {"vo": "It is the fourth-highest score by an India captain in New Zealand. Only Azharuddin, twice, and Gavaskar have made more.", "scene": CAPT},
    {"vo": "But it is his fourth dismissal in the nineties. Ninety-one, ninety-one, ninety, now ninety-eight. MS Dhoni was also out for ninety-eight against New Zealand, in Nagpur.", "scene": NINE},
    {"vo": "Still, all five of India's top five went past fifty. It has happened five times in Tests.", "scene": FIVE},
    {"vo": "New Zealand's bowlers paid. Jacob Duffy: twenty-nine overs, one wicket, a hundred and eighty-one runs. Fourteen no-balls in the innings, seven his.", "scene": ATT},
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
