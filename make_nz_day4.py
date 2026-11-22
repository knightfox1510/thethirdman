"""Writes specs/nz_ind_1st_test_day4.json: The Replay Room Ep 7, India vs New Zealand, 1st Test, Day 4 (Basin Reserve, 22 Nov 2026), VERTICAL (~160 s, lab look).
Source: the owner's ball-by-ball commentary capture of Day 4 (India 720/9 declared; NZ 119/2), parsed by analysis/nz_day4.py and analysis/shots.py (SHOTS_IN=nz_ind_1st_test_day4.json SHOTS_OUT=nz_shots_d4.json SHOTS_INN=2,3).
Records are the capture's own notes, said 'in our records'; no source is named on screen or in the voice-over.   python3 make_nz_day4.py"""
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
F = json.load(open("data/provenance/nz_day4_figures.json")); SH = json.load(open("data/provenance/nz_shots_d4.json")); CB = "cricbuzz"
b2, b3, i2, i3 = F["inn2"]["batters"], F["inn3"]["batters"], F["inn2"], F["inn3"]
assert i2["end"] == {"over": 165.6, "score": 720} and i3["end"] == {"over": 44.6, "score": 119} and len(i2["wickets"]) == 9 and [x["bat"] for x in i3["wickets"]] == ["Tom Latham", "Henry Nicholls"]
assert (b2["Rishabh Pant"]["batRuns"], b2["Rishabh Pant"]["batBalls"], b2["Rishabh Pant"]["batFours"], b2["Rishabh Pant"]["batSixes"]) == (128, 153, 10, 6)
assert [(b2[k]["batRuns"], b2[k]["batBalls"]) for k in ("Anshul Kamboj", "Dhruv Jurel", "Akash Deep")] == [(38, 42), (78, 79), (13, 5)] and b2["Akash Deep"]["batSixes"] == 2
ph = i2["bowlers"]["Glenn Phillips"]; assert (ph["ov"], ph["r"], ph["w"]) == (24, 154, 3) and F["sixes_by_bowler_innings"]["Glenn Phillips"] == 9 and F["sixes_by_bowler_day4"]["Glenn Phillips"] == 7
assert (b3["Devon Conway"]["batRuns"], b3["Devon Conway"]["batBalls"], b3["Rachin Ravindra"]["batRuns"], b3["Rachin Ravindra"]["batBalls"], b3["Henry Nicholls"]["batRuns"], b3["Henry Nicholls"]["batBalls"]) == (59, 137, 27, 72, 31, 59)
assert F["day4_india"] == {"runs": 234, "overs": 41.0}; rr = round(234 / 41, 2); assert rr == 5.71
assert 720 - 368 == 352 and 352 - 119 == 233
c = V.Claims("nz_ind_1st_test_day4")
c.check("India 720/9 declared in 165.6 overs; lead 352 over NZ's 368; Day 4 = 234 runs in 41 overs (5.71 an over) from 486/4", (720, 9, 368, 352, 234, 41, 5.71), {CB: (720, 9, 368, 352, 234, 41, 5.71)}, scope="archive")
c.check("Pant 128 (153): 10 fours, 6 sixes; hundred brought up with a six off Phillips (105 after the six, 135 balls); passed McCullum on the Test sixes list", (128, 153, 10, 6), {CB: (128, 153, 10, 6)}, scope="archive")
c.check("Kamboj 38 (42), Jurel 78 (79), Akash Deep 13 (5) with 2 sixes", (38, 42, 78, 79, 13, 5, 2), {CB: (38, 42, 78, 79, 13, 5, 2)}, scope="archive")
c.check("Phillips 24-0-154-3; 9 sixes off him in the innings, 7 on Day 4 (our count of sixes by bowler)", (24, 154, 3, 9, 7), {CB: (24, 154, 3, 9, 7)}, scope="archive")
c.check("Latham c Pant b Bumrah 0 off the second ball (0 in the first innings): a pair; third NZ captain with a Test pair (Cave 1956, Fleming 1997); eighth NZ opener pair, second against India after McIntosh (Ahmedabad 2010)", (0, 0, 3, 8, 2), {CB: (0, 0, 3, 8, 2)}, scope="archive")
c.check("Nicholls c Jurel b Prasidh 31 (59) at 22.1 (60/2); Conway 59* (137), Rachin 27* (72), 59 unbeaten; NZ 119/2 at stumps, 233 behind", (31, 59, 60, 59, 27, 72, 119, 233), {CB: (31, 59, 60, 59, 27, 72, 119, 233)}, scope="archive")
c.check("control: 81.6% in the first 30 overs of NZ's second innings, 98.9% in the 15 overs after", (81.6, 98.9), {CB: (81.6, 98.9)}, scope="archive")
I3 = [o for o in SH if o["inn"] == 3]
def panel(xs, title):
    k = [o for o in xs if o["line"] and o["len"] and o["line"] != "wide"]; n = len(k)
    balls = [[o["line"], o["len"], "w" if o["wkt"] else ("b" if o["res"] in ("FOUR", "SIX") else ("r" if o["runs"] > 0 else "d"))] for o in k]
    sh = round(100 * sum(1 for o in k if o["len"] == "short") / n); lg = round(100 * sum(1 for o in k if o["line"] == "leg") / n)
    return dict(title=title, n=n, balls=balls, cells={}), sh, lg
PA, sh1, lg1 = panel([o for o in I3 if o["over"] <= 22.1], "FIRST 22 OVERS"); PB, sh2, lg2 = panel([o for o in I3 if o["over"] > 22.1], "AFTER NICHOLLS")
PA["stats"] = [(f"{sh1}%", "SHORT"), (f"{lg1}%", "ON THE LEG SIDE")]; PB["stats"] = [(f"{sh2}%", "SHORT"), (f"{lg2}%", "ON THE LEG SIDE")]
assert sh2 >= 40 and sh1 <= 30 and lg2 >= 20, (sh1, sh2, lg1, lg2)
c.check("India's bowling (our read of lines/lengths): short %d%% -> %d%%, leg side %d%% -> %d%% after Nicholls' wicket" % (sh1, sh2, lg1, lg2), (sh1, sh2, lg1, lg2), {CB: (sh1, sh2, lg1, lg2)}, scope="archive")
pw = [o for o in SH if o["inn"] == 2 and o["bat"] == "Rishabh Pant" and o["ang"] is not None]
PS = [[o["ang"], min(o["runs"], 6) if o["res"] != "no ball" else 4, "s" if o["res"] == "SIX" else ("f" if o["res"] == "FOUR" or o["runs"] >= 4 else "n")] for o in pw]
POFF = sum(o["runs"] for o in pw if o["ang"] > 0); PLEG = sum(o["runs"] for o in pw if o["ang"] < 0); PST = sum(o["runs"] for o in pw if o["ang"] == 0)
straight6 = sum(1 for o in SH if o["inn"] == 2 and o["bat"] == "Rishabh Pant" and o["res"] == "SIX" and o["ang"] == 0); assert straight6 == 3
IN = "data/licensed/in/"
COLD = {"type": "statement", "kicker": "DAY 4 · 720 FOR 9 DECLARED", "lines": [{"t": "720."}, {"t": "AND A PAIR.", "c": "gold"}], "sub": "India lead by 352. Latham: second ball, again."}
PANT = {"type": "photocard", "kicker": "RISHABH PANT · DAY 4", "title": "128.", "img": IN + "nz_day4_pant_hundred.jpg", "crop_short": (130, 330, 1130, 997), "tag": "128 (153) · 10 FOURS · 6 SIXES", "name": "PANT", "mono": "HIS HUNDRED CAME WITH A SIX", "caption": "Past Brendon McCullum on the Test sixes list.", "chip": "128", "chip_sub": "OFF 153 BALLS"}
PW = {"type": "wagon", "head": {"t": "PANT'S 128", "sub": "WHERE THE RUNS WENT · ILLUSTRATIVE"}, "pts": PS, "photo": {"img": IN + "nz_day4_pant_hundred.jpg", "crop": (190, 300, 890, 1000)}, "chips": [("6", "SIXES"), ("10", "FOURS"), (f"{straight6}", "SIXES STRAIGHT")], "footnote": f"{len(pw)} SCORING SHOTS PLACED · ZONES READ FROM THE BALL-BY-BALL TEXT"}
PHIL = {"type": "stats", "head": {"t": "GLENN PHILLIPS", "sub": "OFF-SPIN · INDIA'S INNINGS"}, "tiles": [{"v": "9", "l": "SIXES CONCEDED · 7 TODAY", "c": "red"}, {"v": "154", "l": "RUNS IN 24 OVERS", "c": "ink"}, {"v": "3", "l": "WICKETS ANYWAY", "c": "gold"}]}
LATE = {"type": "bars", "head": {"t": "THE LATE ORDER", "sub": "RUNS AND BALLS · DAY 4"}, "max": 100, "dec": 0, "items": [{"label": "JUREL · 78 OFF 79", "value": 78, "color": "gold"}, {"label": "KAMBOJ · 38 OFF 42 · NIGHTWATCHMAN", "value": 38, "color": "ink"}, {"label": "SUNDAR · 24 OFF 26", "value": 24, "color": "ink"}, {"label": "AKASH DEEP · 13 OFF 5 · 2 SIXES", "value": 13, "color": "red"}]}
DECL = {"type": "stats", "head": {"t": "THE DECLARATION", "sub": "486/4 TO 720/9 · 165.6 OVERS"}, "tiles": [{"v": "234", "l": "RUNS IN 41 OVERS", "c": "gold"}, {"v": f"{rr}", "l": "AN OVER", "c": "ink"}, {"v": "+352", "l": "LEAD AT THE DECLARATION", "c": "red"}]}
BUM = {"type": "photocard", "kicker": "THE REPLY · OVER ONE", "title": "0.", "img": IN + "nz_day4_bumrah_celebrate.jpg", "crop_short": (0, 90, 1280, 943), "tag": "c PANT b BUMRAH · 0.2 OV", "name": "LATHAM", "mono": "A PAIR · THE THIRD NZ CAPTAIN TO BAG ONE", "caption": "The eighth by a New Zealand opener in Tests.", "chip": "0, 0", "chip_sub": "SECOND BALL, BOTH INNINGS"}
CATCH = {"type": "photocard", "kicker": "OVER TWENTY-TWO", "title": "31.", "img": IN + "nz_day4_prasidh_jurel_catch.jpg", "crop_short": (0, 0, 1280, 853), "tag": "c JUREL b PRASIDH · 22.1 OV", "name": "NICHOLLS", "mono": "A DIVING CATCH AT SHORT LEG", "caption": "The first-innings centurion goes for 31 off 59.", "chip": "60/2", "chip_sub": "NEW ZEALAND"}
PITCH = {"type": "pitchtop", "head": {"t": "WHERE INDIA BOWLED", "sub": "THE PITCH FROM ABOVE · EACH DOT A DELIVERY · ILLUSTRATIVE"}, "panels": [PA, PB], "footnote": "POSITIONS ARE OUR READ OF THE BALL-BY-BALL TEXT (LINE AND LENGTH ZONES) · BATTER AT THE TOP"}
CTRL = {"type": "compare", "head": {"t": "NEW ZEALAND SETTLE", "sub": "CONWAY AND RACHIN · 59 UNBEATEN · IN OUR RECORDS"}, "a": {"name": "FIRST 30 OVERS", "color": "gold"}, "b": {"name": "NEXT 15 OVERS", "color": "red"}, "rows": [["CONTROL", "81.6%", "98.9%", "b"]]}
STAKES = {"type": "stats", "head": {"t": "STUMPS · DAY 4", "sub": "NEW ZEALAND 119/2 · 44.6 OVERS"}, "tiles": [{"v": "233", "l": "STILL BEHIND", "c": "red"}, {"v": "8", "l": "WICKETS INDIA NEED", "c": "gold"}, {"v": "59*", "l": "CONWAY NOT OUT · 137 BALLS", "c": "ink"}]}
MIC = {"type": "statement", "kicker": "THE STUMP MIC · PRASIDH TO RACHIN", "lines": [{"t": "\u201cHIT ONE"}, {"t": "CONVINCING.\u201d", "c": "gold"}], "sub": "\u201cAnd I will agree.\u201d"}
POLL = {"type": "list", "head": {"t": "YOUR CALL", "sub": "DAY 5 · COMMENT 1, 2 OR 3"}, "items": [{"h": "1 · INDIA WIN", "d": "eight wickets, one day", "c": "gold", "cue": "india"}, {"h": "2 · A DRAW", "d": "the flat pitch holds", "cue": "draw"}, {"h": "3 · NZ WIN", "d": "an unlikely turnaround", "cue": "zealand"}]}
short = [
    {"vo": "India declare on seven twenty for nine, a lead of three fifty-two. And in the second ball of New Zealand's reply, their captain Tom Latham is out for a pair. Day four had it all.", "scene": COLD},
    {"vo": "It began with Rishabh Pant. A hundred, brought up with a six, off a hundred and fifty-three balls for a hundred and twenty-eight. Ten fours, six sixes. He passed Brendon McCullum on the Test sixes list.", "scene": PANT},
    {"vo": f"Look at the wheel. {w(POFF)} through the off side, {w(PLEG)} through the leg, {w(PST)} straight. Three of the six sixes went down the ground.", "scene": PW},
    {"vo": "The man who paid was Glenn Phillips. Twenty-four overs, a hundred and fifty-four runs, and nine sixes, seven of them today. He still took three wickets.", "scene": PHIL},
    {"vo": "Then the lower order. Dhruv Jurel, seventy-eight off seventy-nine. The nightwatchman, Anshul Kamboj, thirty-eight off forty-two. Akash Deep, thirteen off five balls, two sixes.", "scene": LATE},
    {"vo": "Two hundred and thirty-four runs in forty-one overs, five point seven one an over. Then India declared.", "scene": DECL},
    {"vo": "The reply. Jasprit Bumrah, second ball, Latham caught behind. Nought in the first innings, nought in the second. The third New Zealand captain with a Test pair, and the eighth New Zealand opener.", "scene": BUM},
    {"vo": "Henry Nicholls, the first-innings centurion, lasted fifty-nine balls. Prasidh Krishna got one to jump, and Dhruv Jurel dived at short leg. Sixty for two.", "scene": CATCH},
    {"vo": "The stump mic caught Prasidh in Rachin Ravindra's ear. Try another shot. Hit one convincing, and I will agree. Rachin did not rise to it.", "scene": MIC},
    {"vo": f"India's plan shifted too. In the first twenty-two overs, {w(sh1)} per cent of the balls were short. After Nicholls, {w(sh2)}, and a quarter on the leg side.", "scene": PITCH},
    {"vo": "But Devon Conway and Rachin Ravindra settled. Fifty-nine unbeaten. Their control went from eighty-two per cent in the first thirty overs to ninety-nine in the next fifteen.", "scene": CTRL},
    {"vo": "New Zealand, one nineteen for two, still two thirty-three behind. India need eight wickets on a flat pitch. Can they force a win, or is it a draw?", "scene": STAKES},
    {"vo": "Day five. Comment one, India win. Two, a draw. Three, a New Zealand win.", "scene": POLL},
    dict(YT_CTA, vo="Subscribe, and we'll break down day five the same way."),
]
SRC = ["Day 4 ball-by-ball (India 720/9 declared; New Zealand 119/2): Cricbuzz full commentary for New Zealand v India, 1st Test, 22 November 2026 (owner's capture; bowler lines, no-ball counts, control rates and the pair note are Cricbuzz's). https://www.cricbuzz.com/live-cricket-full-commentary/161285/nz-vs-ind-1st-test-india-tour-of-new-zealand-2026",
       "Figures: analysis/nz_day4.py, analysis/shots.py. Wagon wheel and pitch map positions are our read of the commentary text (approximate zones)."]
TAGS = ["India vs New Zealand", "India vs New Zealand 1st Test", "IND vs NZ 1st Test", "New Zealand vs India Test", "Rishabh Pant", "Tom Latham", "Glenn Phillips", "Jasprit Bumrah", "Dhruv Jurel", "Devon Conway", "Basin Reserve", "Wellington Test", "Day 4 analysis", "cricket analysis", "The Third Man"]
DS = ("India vs New Zealand, 1st Test day four: India declare on 720 for 9, a lead of 352. Rishabh Pant's hundred with a six and 128 in all, nine sixes off Glenn Phillips, Dhruv Jurel 78 off 79, and Tom Latham out for a pair, the third New Zealand captain with one in Tests. New Zealand 119 for 2, still 233 behind. Can India take eight wickets on Day 5? Comment 1 India win, 2 draw, 3 New Zealand win. Full breakdown on the channel.\n\n#INDvNZ #IndiaVsNewZealand #1stTest #Shorts")
spec = {"slug": "nz_ind_1st_test_day4", "theme": "lab", "theme_long": "lab", "captions": "lab", "captions_long": False, "series": "replay", "tag": "THE REPLAY ROOM", "tagsub": "NZ V IND · 1ST TEST · DAY 4",
        "files": {"long": "_unused", "short": "x"}, "venue": {"time": "day", "crowd": [[20, 20, 22], [230, 230, 230], [25, 100, 200], [20, 60, 140]], "boards": [[20, 20, 22], [25, 100, 200]]},
        "thumb": {"kicker": "NZ V IND · 1ST TEST · DAY 4", "lines": [{"t": "720 AND"}, {"t": "A PAIR", "c": "gold"}], "hero": "720", "herosize": 420},
        "ig_cover": {"lines": [{"t": "720 AND"}, {"t": "A PAIR", "c": "gold"}], "sub": "1ST TEST · DAY 4", "hero": "720"}, "sources": SRC, "short": short,
        "yt": {"short": {"title": "720 and a Pair: Pant's Hundred, Latham Out | India vs New Zealand 1st Test Day 4 #Shorts", "description": DS, "tags": TAGS}}}
c.save(spec); voice_lint.fix_spec(spec)
json.dump(spec, open("specs/nz_ind_1st_test_day4.json", "w"), ensure_ascii=False, indent=1)
print("short words", sum(len(s["vo"].split()) for s in short), "|", voice_lint.check_spec(spec, ("short",)) or "lint clean", "|", spec["files"], "| panels", PA["n"], PB["n"], sh1, sh2, lg1, lg2, "| pant wheel", POFF, PLEG, PST)
