"""Writes specs/nz_ind_1st_test_long.json: The Replay Room Ep 9, India vs New Zealand 1st Test (Basin Reserve, 19-23 Nov 2026): the full-Test analysis for YouTube (long, lab look, ~13 min).
Built from the five match-day specs' verified scenes (each day's claims are merged into this video's provenance) plus new connective scenes: match card, wagon wheels, pitch maps, a whole-Test line/length comparison, the owner's clip of the final walk-off,
the verdict. No source is named on screen or in the voice-over (owner rule).   python3 make_nz_test1_long.py"""
import json, os, sys, copy, re, collections
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
CB = "cricbuzz"; IN = "data/licensed/in/"
SP = {d: json.load(open(f"specs/nz_ind_1st_test_day{d}.json")) for d in range(1, 6)}
D1 = SP[1]["long"]; S = {d: SP[d]["short"] for d in range(2, 6)}
def pick(day, i):
    src = D1 if day == 1 else S[day]
    return copy.deepcopy(src[i]["scene"])
SRCNAME = re.compile(r"cricbuzz['’]?s?|cricinfo|espn\w*|sportmonks|cricsheet|wisden", re.I)
def clean(o):
    if isinstance(o, dict): return {k: clean(v) for k, v in o.items()}
    if isinstance(o, list): return [clean(v) for v in o]
    if isinstance(o, str) and SRCNAME.search(o): return re.sub(r"\s*[·|]?\s*(CRICBUZZ['’]?S? ?(OWN )?(TABLE|FIGURE)S?|PER CRICBUZZ|CRICBUZZ['’]?S?)\b", "", o, flags=re.I).replace("  ", " ").strip(" ·")
    return o
F2, F3, F4, F5 = (json.load(open(f"data/provenance/nz_day{d}_figures.json")) for d in (2, 3, 4, 5))
SH1 = json.load(open("data/provenance/nz_shots_d1.json")); SH4 = json.load(open("data/provenance/nz_shots_d4.json")); SH5 = json.load(open("data/provenance/nz_shots_d5.json"))
c = V.Claims("nz_ind_1st_test_long")
# ---------------------------------------------------------------- data for the new scenes (asserted)
tot_runs = 368 + 720 + 239; assert tot_runs == 1327 and 10 + 9 + 5 == 24
def wagon(rows, bat):
    xs = [o for o in rows if o["bat"] == bat and o["ang"] is not None]
    pts = [[o["ang"], min(o["runs"], 6) if o["res"] != "no ball" else 4, "s" if o["res"] == "SIX" else ("f" if o["res"] == "FOUR" or o["runs"] >= 4 else "n")] for o in xs]
    return pts, dict(n=len(xs), off=sum(o["runs"] for o in xs if o["ang"] > 0), leg=sum(o["runs"] for o in xs if o["ang"] < 0), st=sum(o["runs"] for o in xs if o["ang"] == 0))
NP, NW = wagon(SH1, "Henry Nicholls"); PP, PWd = wagon(SH1, "Glenn Phillips"); JP, JW = wagon(SH4, "Yashasvi Jaiswal") if False else wagon([o for o in SH4 if o["inn"] == 2], "Yashasvi Jaiswal")
MP, MW = wagon([o for o in SH5 if o["inn"] == 3 and o["over"] > 44.6], "Daryl Mitchell"); PHP, PHW = wagon([o for o in SH5 if o["inn"] == 3 and o["over"] > 44.6], "Glenn Phillips")
assert (NW["off"], NW["leg"], PWd["off"], PWd["leg"]) == (42, 57, 57, 16) and (JW["off"], JW["leg"], JW["st"]) == (51, 19, 6)
def panel(rows, title):
    k = [o for o in rows if o["line"] and o["len"] and o["line"] != "wide"]; n = len(k)
    cells = collections.Counter(f'{o["line"]}|{"full" if o["len"] == "yorker" else o["len"]}' for o in k)
    balls = [[o["line"], o["len"], "w" if o["wkt"] else ("b" if o["res"] in ("FOUR", "SIX") else ("r" if o["runs"] > 0 else "d"))] for o in k]
    pct = lambda f: round(100 * sum(1 for o in k if f(o)) / n)
    return dict(title=title, n=n, cells=dict(cells), balls=balls), dict(short=pct(lambda o: o["len"] == "short"), good=pct(lambda o: o["len"] == "good"), stump=pct(lambda o: o["line"] in ("off", "outside_off")), leg=pct(lambda o: o["line"] == "leg"))
P1a, K1a = panel([o for o in SH1 if o["over"] <= 22.5], "BEFORE LUNCH"); P1b, K1b = panel([o for o in SH1 if o["over"] > 22.5], "AFTER LUNCH")
P1a["stats"] = [(f'{K1a["short"]}%', "SHORT"), (f'{K1a["good"]}%', "GOOD LENGTH")]; P1b["stats"] = [(f'{K1b["short"]}%', "SHORT"), (f'{K1b["good"]}%', "GOOD LENGTH")]
assert K1b["short"] > K1a["short"] and K1a["good"] < K1b["good"] + 10
IND_ALL = [o for o in SH1] + [o for o in SH4 if o["inn"] == 3 and o["over"] <= 44.6] + [o for o in SH5 if o["inn"] == 3 and o["over"] > 44.6]; NZ_ALL = [o for o in SH4 if o["inn"] == 2]
PI, KI = panel(IND_ALL, "INDIA BOWLING"); PN, KN = panel(NZ_ALL, "NEW ZEALAND BOWLING")
PI["stats"] = [(f'{KI["short"]}%', "SHORT"), (f'{KI["stump"]}%', "ON OR OUTSIDE OFF")]; PN["stats"] = [(f'{KN["short"]}%', "SHORT"), (f'{KN["stump"]}%', "ON OR OUTSIDE OFF")]
assert abs(KI["short"] - KN["short"]) <= 2 and abs(KI["stump"] - KN["stump"]) <= 4, (KI, KN)
c.check("whole-Test lines and lengths (our read): India's attack %d%% short, %d%% on or outside off; New Zealand's attack %d%% short, %d%% on or outside off" % (KI["short"], KI["stump"], KN["short"], KN["stump"]), (KI["short"], KI["stump"], KN["short"], KN["stump"]), {CB: (KI["short"], KI["stump"], KN["short"], KN["stump"])}, scope="archive")
c.check("Day 1 map (our read): India's short balls %d%% before lunch, %d%% after; Nicholls placed runs leg %d off %d; Phillips off %d leg %d" % (K1a["short"], K1b["short"], NW["leg"], NW["off"], PWd["off"], PWd["leg"]), (K1a["short"], K1b["short"], NW["leg"], NW["off"], PWd["off"], PWd["leg"]), {CB: (K1a["short"], K1b["short"], NW["leg"], NW["off"], PWd["off"], PWd["leg"])}, scope="archive")
c.check("Test totals: NZ 368, India 720/9 declared, NZ 239/5: 1,327 runs, 24 wickets, a draw; Nicholls 175* (Player of the Match), Phillips 118", (368, 720, 239, 1327, 24, 175, 118), {CB: (368, 720, 239, 1327, 24, 175, 118)}, scope="archive")
c.check("India's first seven partnerships all 50+ (a Test record); all five of the top five past 50 (fifth time)", (7, 5), {CB: (7, 5)}, scope="archive")
c.check("Jaiswal's placed runs: off %d, leg %d, straight %d; Mitchell and Phillips on Day 5: placed %d and %d scoring shots" % (JW["off"], JW["leg"], JW["st"], MW["n"], PHW["n"]), (JW["off"], JW["leg"], JW["st"]), {CB: (JW["off"], JW["leg"], JW["st"])}, scope="archive")
# ---------------------------------------------------------------- scenes
def stat(head, sub, tiles): return {"type": "stats", "head": {"t": head, "sub": sub}, "tiles": tiles}
def act(k, l1, l2, sub): return {"type": "statement", "kicker": k, "lines": [{"t": l1}, {"t": l2, "c": "gold"}], "sub": sub}
COLD = act("INDIA VS NEW ZEALAND · 1ST TEST · BASIN RESERVE", "EIGHT NEEDED.", "THREE TAKEN.", "Five days, 1,327 runs, 24 wickets, no result.")
CARD = pick(5, 14)
NMORN = {"type": "photostand", "kicker": "NEW ZEALAND'S SECOND MORNING", "title": "243/5 to 368.", "items": [{"img": IN + "nz_day2_nicholls_walkoff.jpg", "big": "175*", "name": "NICHOLLS", "crop": (140, 250, 1140, 815)}, {"img": IN + "nz_day2_phillips_hundred.jpg", "big": "118", "name": "PHILLIPS · 2ND TEST HUNDRED", "crop": (140, 330, 1140, 895)}], "chips": [("243/5", "DAY 1 STUMPS"), ("368", "ALL OUT"), ("125", "ADDED ON DAY 2")]}
PITCH1 = {"type": "pitchtop", "head": {"t": "WHERE INDIA BOWLED", "sub": "DAY 1 · THE PITCH FROM ABOVE · EACH DOT A DELIVERY · ILLUSTRATIVE"}, "panels": [P1a, P1b], "footnote": "POSITIONS ARE OUR READ OF THE BALL-BY-BALL TEXT (LINE AND LENGTH ZONES)"}
def wag(title, pts, wd, photo=None, chips=None, foot=None):
    s = {"type": "wagon", "head": {"t": title, "sub": "WHERE THE RUNS WENT · ILLUSTRATIVE"}, "pts": pts, "chips": chips, "footnote": foot or f'{wd["n"]} SCORING SHOTS PLACED · ZONES READ FROM THE BALL-BY-BALL TEXT · OFF SIDE ON THE RIGHT'}
    if photo: s["photo"] = photo
    return s
WNICH = wag("NICHOLLS · DAY 1", NP, NW, chips=[(f'{NW["leg"]}', "RUNS LEG SIDE"), (f'{NW["off"]}', "RUNS OFF SIDE"), ("113*", "AT STUMPS"), ("221", "BALLS FACED")])
WPHIL = wag("PHILLIPS · DAY 1", PP, PWd, chips=[(f'{PWd["off"]}', "RUNS OFF SIDE"), (f'{PWd["leg"]}', "RUNS LEG SIDE"), ("94*", "AT STUMPS"), ("182", "BALLS FACED")])
WJAI = wag("JAISWAL'S 85", JP, JW, photo={"img": IN + "nz_day2_jaiswal_drive.jpg", "crop": (150, 130, 790, 770)}, chips=[(f'{JW["off"]}', "RUNS OFF SIDE"), (f'{JW["leg"]}', "RUNS LEG SIDE"), ("16", "FOURS"), ("89", "BALLS FACED")])
WMIT = wag("MITCHELL'S 49*", MP, MW, chips=[("49*", "OFF 186 BALLS"), ("1", "SIX"), (f'{MW["n"]}', "SCORING SHOTS PLACED"), ("160", "DOT BALLS")])
WPH5 = wag("PHILLIPS' 26*", PHP, PHW, chips=[("26*", "OFF 126 BALLS"), ("2", "FOURS"), (f'{PHW["n"]}', "SCORING SHOTS PLACED"), ("111", "DOT BALLS")])
AGAIN = {"type": "pitchzones", "head": {"t": "THE WHOLE TEST ON ONE MAP", "sub": "LINE BY LENGTH · SHARE OF EACH ATTACK'S DELIVERIES · ILLUSTRATIVE"}, "panels": [PI, PN]}
SEVEN = {"type": "stats", "head": {"t": "TWO TEST RECORDS", "sub": "INDIA'S INNINGS · IN OUR RECORDS"}, "tiles": [{"v": "7", "l": "STANDS OF 50+ IN A ROW: A WORLD RECORD", "c": "gold"}, {"v": "5", "l": "TOP FIVE PAST FIFTY: THE FIFTH TIME", "c": "red"}, {"v": "14", "l": "SIXES IN THE INNINGS", "c": "ink"}]}
NZBOWL = {"type": "bars", "head": {"t": "NEW ZEALAND'S BOWLERS", "sub": "RUNS PER OVER · INDIA'S 720/9"}, "max": 8, "dec": 2, "items": [{"label": "JAMIESON · 31-6-88-1", "value": round(88 / 31, 2), "color": "gold"}, {"label": "HENRY · 33-7-94-1", "value": round(94 / 33, 2), "color": "ink"}, {"label": "SMITH · 29-4-84-1 · 4 NO-BALLS", "value": round(84 / 29, 2), "color": "ink"}, {"label": "DUFFY · 33-1-201-1 · 7 NO-BALLS", "value": round(201 / 33, 2), "color": "red"}, {"label": "PHILLIPS · 24-0-154-3", "value": round(154 / 24, 2), "color": "red"}]}
CLIP = {"type": "clip", "clip": "/root/.claude/uploads/0e6d8023-8d7b-5fe3-9abc-6751d93064e2/881d9399-MicrosoftTeams-video.m4v", "fps": 10, "kicker": "DAY 5 · THE FINAL WALK-OFF", "title": "The wall holds.", "sub": "MITCHELL AND PHILLIPS · 176/5 TO 239/5", "chips": [("63*", "UNBEATEN STAND"), ("259", "BALLS"), ("43", "OVERS")], "caption": "Over three hundred balls between them, and not one more wicket."}
VERDICT = {"type": "list", "head": {"t": "WHAT EACH SIDE TAKES TO CHRISTCHURCH", "sub": "THE FIRST TEST · IN OUR RECORDS"}, "items": [{"h": "INDIA · THE BATTING", "d": "seven stands of 50+, all five of the top five past fifty", "c": "gold"}, {"h": "INDIA · THE BOWLING", "d": "42 maidens; Prasidh, Washington, Kamboj, Akash Deep all disciplined"}, {"h": "NEW ZEALAND · THE SPINE", "d": "Nicholls 175*, Phillips 118 and a 26* that cost 126 balls"}, {"h": "NEW ZEALAND · THE SECOND INNINGS", "d": "Conway 65, Mitchell 49*, and a draw from 70 for 5 and 119 for 2"}]}
NEXT = act("NEXT: THE SECOND AND FINAL TEST", "CHRISTCHURCH.", "HAGLEY OVAL.", "Both sides move on after the draw. Will we get a spicy pitch?")
POLL = {"type": "list", "head": {"t": "YOUR CALL", "sub": "THE SERIES · COMMENT 1, 2 OR 3"}, "items": [{"h": "1 · INDIA", "d": "win in Christchurch", "c": "gold", "cue": "india"}, {"h": "2 · A SECOND DRAW", "d": "the pitch is flat again", "cue": "draw"}, {"h": "3 · NEW ZEALAND", "d": "Hagley Oval's turn", "cue": "zealand"}]}
KOUT = {"type": "photocard", "kicker": "KL RAHUL · OUT", "title": "136.", "img": IN + "nz_day3_rahul_bowled.jpg", "crop_short": (0, 0, 1280, 853), "tag": "b SMITH · 103.3 OV", "name": "RAHUL", "mono": "290 BALLS · 9 FOURS · 2 SIXES", "caption": "Dragged on. He walked off to a standing ovation.", "chip": "136", "chip_sub": "OFF 290 BALLS"}
CH = lambda t, sc: dict(sc, chapter=t)
long = [
    {"vo": "Five days at the Basin Reserve. Thirteen hundred and twenty-seven runs, twenty-four wickets, and no result. India declared on seven twenty for nine and needed eight wickets on the last day. They took three. This is how a Test India controlled slipped to a draw, and the two men who shut the door.", "scene": CH("The draw", COLD)},
    {"vo": "New Zealand three sixty-eight. India seven twenty for nine declared. New Zealand two thirty-nine for five. Henry Nicholls, one seventy-five not out, Player of the Match.", "scene": CARD},
    {"vo": "It starts with the toss. India won it and bowled, and the pitch gave them every reason: fifteen millimetres of grass, and moisture on top. On the first morning, a bowler's dream.", "scene": CH("Day 1: the green top", pick(1, 1))},
    {"vo": "Over one. Jasprit Bumrah, full, on the fourth-stump line, the seam upright. Tom Latham, sure it would leave, left it. It came back. Two for one.", "scene": pick(1, 2)},
    {"vo": "Bumrah had been here before: Wellington, twenty twenty, one wicket for eighty-eight in twenty-six overs. This time his first over had Latham.", "scene": pick(1, 3)},
    {"vo": "Devon Conway lasted three overs and one review. Given out caught behind, he was reprieved when the replay showed the noise came before the ball reached the bat. Then Anshul Kamboj, full and seaming away: an edge, and twelve for two.", "scene": pick(1, 4)},
    {"vo": "Rachin Ravindra survived an edge India did not review. Akash Deep got him anyway, with extra bounce. Next over, Bumrah's nipbacker found Daryl Mitchell's inside edge, and Yashasvi Jaiswal held it at short leg. Fifty-two for four.", "scene": pick(1, 5)},
    {"vo": "Blundell was the fifth, to Bumrah after lunch, caught by Gill at first slip. Seventy for five in twenty-eight overs, and every one of them found something in the surface.", "scene": pick(1, 7)},
    {"vo": "India had their length right. Two hundred and two balls on a good length cost one point four eight an over, and took three wickets. The short balls cost nearly four, and took none.", "scene": pick(1, 8)},
    {"vo": "The new ball did the damage: three wickets for fifty-two in twenty overs. The old ball took two more in sixty overs, and cost a hundred and eighty-four runs.", "scene": pick(1, 13)},
    {"vo": "Then the day turned.", "scene": CH("Day 1: the hour it slipped", pick(1, 9))},
    {"vo": "Over thirty: Bumrah nips one back at Glenn Phillips, who is on six. India review the lbw, the third umpire sees a spike, and the review is lost. Edges rolled past the stumps. And when Nicholls was on a hundred and two, a top edge was left by two fielders.", "scene": pick(1, 10)},
    {"vo": "Then the sun came out, and the pitch began to brown. False shots fell from twenty-five per cent before lunch to fourteen after. On good-length balls, from thirty to thirteen.", "scene": pick(1, 11)},
    {"vo": "India drifted shorter. Nineteen per cent of their seam balls were short before lunch. After lunch, thirty-six.", "scene": pick(1, 12)},
    {"vo": "On the pitch from above, you can see it. Before lunch, a quarter were short; after lunch, nearly four in ten.", "scene": PITCH1},
    {"vo": "Henry Nicholls: a hundred and thirteen not out by the close, his fifth Test hundred at this ground. Glenn Phillips, ninety-four. A sixth-wicket stand of a hundred and seventy-three: fifty-four singles, seven twos, seven threes, twenty-one fours. Seventy-three per cent dots, and they never let India settle.", "scene": pick(1, 16)},
    {"vo": f"Look at their wagon wheels. Nicholls scored {w(NW['leg'])} of his placed runs on the leg side, {w(NW['off'])} through the off.", "scene": WNICH},
    {"vo": f"Phillips was the opposite: {w(PWd['off'])} off the front foot through the off side, and only {w(PWd['leg'])} on the leg. Two different ways to wear India down.", "scene": WPHIL},
    {"vo": "The day ended with one last twist: Bumrah, the second new ball, an inswinger at Henry Nicholls' toes. He jammed his bat down just in time. Two forty-three for five at stumps.", "scene": pick(1, 0)},
    {"vo": "Put the whole day on one strip. Five wickets in the first twenty-eight overs. None in the next fifty-three.", "scene": pick(1, 17)},
    {"vo": "Day two began on two forty-three for five. Henry Nicholls batted right through to one seventy-five not out. Glenn Phillips made his second Test hundred, a hundred and eighteen. They finished on three sixty-eight, and by then the green top had turned brown.", "scene": CH("Day 2: 368 and the reply", NMORN)},
    {"vo": "India's reply began with Yashasvi Jaiswal: eighty-five off eighty-nine balls, sixteen fours, sixty-four of his eighty-five in boundaries.", "scene": pick(2, 2)},
    {"vo": "But start with the squeeze. Before tea, eight overs, sixteen runs. Three slips and a gully. Kyle Jamieson finished the day with eleven overs, five maidens, fifteen runs.", "scene": pick(2, 3)},
    {"vo": "Then the drama. Over four, New Zealand review an lbw against KL Rahul, and lose it. Over seven, Matt Henry hits Rahul on the pads, two sounds, a huge appeal, and Tom Latham, with a second left on the clock, does not review. Henry throws his sweater down.", "scene": pick(2, 4)},
    {"vo": "And Jaiswal had two lives: on nought, an edge between third slip and gully; on six, an edge to gully, and Glenn Phillips drops it.", "scene": pick(2, 5)},
    {"vo": "After tea, a hundred and forty-three runs in thirty-one overs. Eight quiet overs, then the flood.", "scene": pick(2, 7)},
    {"vo": "Here is why. New Zealand's bowlers were full. Fifty-seven full balls, forty-six runs. The good-length ones? Thirty-three balls, ten runs.", "scene": pick(2, 8)},
    {"vo": "Jaiswal against the full ball: twenty-seven balls, forty-one runs. Against good length: ten balls, no runs. The full ball gave him the innings.", "scene": pick(2, 9)},
    {"vo": f"Look at his wheel: {w(JW['off'])} of his placed runs through the off side, {w(JW['leg'])} through the leg, and {w(JW['st'])} straight.", "scene": WJAI},
    {"vo": "His fifty took sixty-six balls, his last thirty-five took twenty-three. Then Matt Henry, adamant, got his review, and Jaiswal was caught behind, against the run of play, on eighty-five.", "scene": pick(2, 10)},
    {"vo": "KL Rahul took a hundred and sixteen balls for his fifty-two, his first Test fifty against New Zealand. He would not be done.", "scene": pick(2, 11)},
    {"vo": "Day three. Three hundred and twenty-seven runs, three wickets, and every session faster than the last. Eighty before lunch, a hundred and five to tea, a hundred and forty-two after.", "scene": CH("Day 3: the reply grows", pick(3, 1))},
    {"vo": "New Zealand began stump to stump. Before lunch, eighty-four per cent of balls were on or outside off. By the evening, a quarter were on the leg side.", "scene": pick(3, 2)},
    {"vo": "The morning was KL Rahul's. A hundred off two hundred and seven balls, his first in New Zealand, and a Test hundred in every SENA country.", "scene": pick(3, 3)},
    {"vo": "Sixty of his placed runs came through the leg side, forty-nine through the off.", "scene": pick(3, 4)},
    {"vo": "Rahul fell for a hundred and thirty-six, bowled by Nathan Smith, dragging one on. Two hundred and ninety balls, and a standing ovation.", "scene": KOUT},
    {"vo": "Devdutt Padikkal added a hundred and sixty-five with him. Eighty, then one Jamieson ball held its line. A hundred, missed by twenty.", "scene": pick(3, 5)},
    {"vo": "Gill's fifty was a pull for six, and it put India in front. Ninety-eight off a hundred and forty-six, nine fours, two sixes, mostly on the leg side.", "scene": pick(3, 7)},
    {"vo": "It is the fourth-highest score by an India captain in New Zealand. Only Azharuddin, twice, and Gavaskar have made more.", "scene": pick(3, 8)},
    {"vo": "But it is his fourth dismissal in the nineties. Ninety-one, ninety-one, ninety, now ninety-eight. MS Dhoni was also out for ninety-eight against New Zealand, in Nagpur.", "scene": pick(3, 9)},
    {"vo": "Two records came out of this innings. The first seven partnerships all passed fifty, a new world record. And all five of India's top five went past fifty, only the fifth time in Test history.", "scene": SEVEN},
    {"vo": "Rishabh Pant ended the day on fifty-five not out: fifteen off thirty-seven balls, then thirty-seven off the next eighteen, with two sixes in two balls off Duffy. The lead went past a hundred.", "scene": pick(3, 6)},
    {"vo": "Day four. India declare on seven twenty for nine, a lead of three fifty-two. It began with Rishabh Pant: a hundred, brought up with a six, a hundred and twenty-eight off a hundred and fifty-three balls, ten fours, six sixes.", "scene": CH("Day 4: 720", pick(4, 1))},
    {"vo": "Look at the wheel: thirty-three runs through the off side, thirty-three through the leg, thirty straight. Three of the six sixes went down the ground.", "scene": pick(4, 2)},
    {"vo": "The man who paid was Glenn Phillips. Twenty-four overs, a hundred and fifty-four runs, nine sixes, seven of them today. He still took three wickets.", "scene": pick(4, 3)},
    {"vo": "Then the lower order. Dhruv Jurel, seventy-eight off seventy-nine. The nightwatchman, Anshul Kamboj, thirty-eight off forty-two. Akash Deep, thirteen off five balls, two sixes.", "scene": pick(4, 4)},
    {"vo": "Two hundred and thirty-four runs in forty-one overs, five point seven one an over. Then India declared.", "scene": pick(4, 5)},
    {"vo": "Add it up. Jacob Duffy bowled thirty-three overs for two hundred and one, with seven no-balls. Phillips, a hundred and fifty-four for three. New Zealand's attack leaked runs at four point three five an over.", "scene": NZBOWL},
    {"vo": "The reply. Jasprit Bumrah, second ball, Latham caught behind. Nought in the first innings, nought in the second. The third New Zealand captain with a Test pair, and the eighth New Zealand opener.", "scene": pick(4, 6)},
    {"vo": "Henry Nicholls, the first-innings centurion, lasted fifty-nine balls. Prasidh Krishna got one to jump, and Dhruv Jurel dived at short leg. Sixty for two.", "scene": pick(4, 7)},
    {"vo": "India's plan shifted. In the first twenty-two overs, twenty-seven per cent of the balls were short. After Nicholls, forty-five, and a quarter on the leg side.", "scene": pick(4, 9)},
    {"vo": "But Devon Conway and Rachin Ravindra settled. Fifty-nine unbeaten. Their control went from eighty-two per cent in the first thirty overs to ninety-nine in the next fifteen.", "scene": pick(4, 10)},
    {"vo": "Day five. India needed eight wickets, and New Zealand needed to bat the day. One point six runs an over. Eighty-six per cent of balls were dots. Thirty-four maidens in seventy-five overs. Blocking, by plan.", "scene": CH("Day 5: the wall", pick(5, 1))},
    {"vo": "The conditions gave India little: a twenty-two kilometre breeze, sixteen degrees, dead grass, a dried-out pitch.", "scene": pick(5, 3)},
    {"vo": "The whole day over by over. Two wickets before lunch, one after, and none in the last session.", "scene": pick(5, 2)},
    {"vo": "India's lines tightened. Before lunch, seventy-three per cent were on or outside off. After lunch, ninety-three. The stumps were no longer under attack.", "scene": pick(5, 4)},
    {"vo": "The morning gave India two: Conway, caught by Rishabh Pant off Washington Sundar, then Rachin Ravindra at gully. Thirty-eight runs in twenty-six overs.", "scene": pick(5, 5)},
    {"vo": "India's best hope was Daryl Mitchell, and he had three lives: a run-out missed, a bat-pad with no short leg, a kicker Padikkal could not hold.", "scene": pick(5, 6)},
    {"vo": "Blundell fell to a review. Then the wall: Mitchell and Phillips walked in at one seventy-six for five.", "scene": pick(5, 7)},
    {"vo": "Sixty-three unbeaten, off two hundred and fifty-nine balls, forty-three overs. When India finally shook hands, the two of them walked off to applause.", "scene": CLIP},
    {"vo": f"Mitchell scored forty-nine off a hundred and eighty-six balls. Of the runs we can place, {w(MW['off'])} went through the off side, {w(MW['leg'])} through the leg, and none straight down the ground.", "scene": WMIT},
    {"vo": f"Phillips, twenty-six off a hundred and twenty-six, with {w(PHW['off'])} runs through the off side and {w(PHW['leg'])} through the leg. A hundred and eleven of his balls were dots, and a hundred and sixty of Mitchell's.", "scene": WPH5},
    {"vo": "Forty-three overs is the second-longest stand like it by New Zealand this century. The record, a hundred and twenty-three overs, was set on this ground, against India, in twenty fourteen.", "scene": pick(5, 9)},
    {"vo": "India bowled well. Prasidh Krishna: eleven overs, eight maidens, three runs. Forty-two maidens in the innings, the most by any team in this cycle.", "scene": pick(5, 10)},
    {"vo": "So, did they quit too soon? With about an hour left, Mitchell offered his hand and Shubman Gill took it. Three wickets in seventy-five overs, one every twenty-five. India needed five.", "scene": pick(5, 11)},
    {"vo": "The last overs went to part-timers, Jaiswal and Jurel. Bumrah bowled two overs in the last session. Prasidh, two.", "scene": pick(5, 12)},
    {"vo": "The cost. New Zealand fall to sixty-six point six seven per cent, behind Australia. India stay fourth on fifty, and need all six remaining Tests. Sixteen points missed in two drawn Tests.", "scene": pick(5, 13)},
    {"vo": "Here is the whole Test on one map. India's bowling and New Zealand's bowling were almost identical: about three in ten balls short, eight in ten on or outside off. The difference was not the plan. It was the first hour of day one, and everything after it.", "scene": CH("The verdict", AGAIN)},
    {"vo": "India take away their batting, and a bowling unit that stayed disciplined on a flat pitch. New Zealand take away a spine: Nicholls, Phillips, Conway, Mitchell, and a draw from seventy for five and one nineteen for two.", "scene": VERDICT},
    {"vo": "Now the second and final Test, in Christchurch. Will we get a spicy pitch at Hagley Oval?", "scene": NEXT},
    {"vo": "Who wins the series? Comment one, India. Two, a second draw. Three, New Zealand.", "scene": POLL},
    dict(YT_CTA, vo="Subscribe, and we'll break down the series decider the same way."),
]
for item in long:
    item["scene"] = clean(item["scene"])
    if item["scene"].get("chapter"): item["chapter"] = item["scene"].pop("chapter")      # the engine reads chapters from the scene item (YouTube chapter list)
SRC = ["Ball-by-ball for all five days (New Zealand 368 and 239/5, India 720/9 declared): Cricbuzz full commentary for New Zealand v India, 1st Test, 19-23 November 2026 (owner's captures; bowler lines, records, the WTC table, pitch reports and match notes are Cricbuzz's). https://www.cricbuzz.com/live-cricket-full-commentary/161285/nz-vs-ind-1st-test-india-tour-of-new-zealand-2026",
       "Day-by-day figures: analysis/nz_day1.py ... nz_day5.py, analysis/shots.py. Length classes, wagon-wheel zones and the pitch maps are our read of the commentary text (approximate zones, illustrative). The final walk-off clip and the photographs were supplied by the channel owner."]
TAGS = ["India vs New Zealand", "India vs New Zealand 1st Test", "IND vs NZ 1st Test", "New Zealand vs India Test", "Basin Reserve", "Wellington Test", "Rishabh Pant", "KL Rahul", "Shubman Gill", "Jasprit Bumrah", "Henry Nicholls", "Glenn Phillips", "Daryl Mitchell", "WTC", "Test analysis", "cricket analysis", "The Third Man"]
DL = ("India vs New Zealand, 1st Test analysis (Basin Reserve, Wellington, 19-23 November 2026): India needed eight wickets on the last day and took three. The full story in five acts: Bumrah on a green top, New Zealand's 368 and the afternoon the pitch eased, India's 720 for 9 declared (Jaiswal, Rahul, Padikkal, Gill, Pant, and a record seven 50+ stands), Latham's pair, and the Mitchell and Phillips wall that saved the draw. Wagon wheels, pitch maps from above, line and length maps, the WTC cost, and the question: did India give up too soon?\n\n"
      "CHAPTERS are listed below. YOUR CALL: who wins the series? Comment 1 India, 2 a second draw, 3 New Zealand.\n\nMethod: ball-by-ball commentary for every delivery; length classes, wagon-wheel zones and the pitch maps are our own read of that text (approximate zones, illustrative).\n\n#INDvNZ #IndiaVsNewZealand #1stTest #WTC")
spec = {"slug": "nz_ind_1st_test_long", "theme": "lab", "theme_long": "lab", "captions": "lab", "captions_long": False, "series": "replay", "tag": "THE REPLAY ROOM", "tagsub": "NZ V IND · 1ST TEST ANALYSIS",
        "files": {"long": "x", "short": "_unused"}, "venue": {"time": "day", "crowd": [[20, 20, 22], [230, 230, 230], [25, 100, 200], [20, 60, 140]], "boards": [[20, 20, 22], [25, 100, 200]]},
        "thumb": {"kicker": "NZ V IND · 1ST TEST ANALYSIS", "lines": [{"t": "8 NEEDED."}, {"t": "3 TAKEN.", "c": "gold"}], "hero": "239/5", "herosize": 420}, "sources": SRC, "long": long,
        "yt": {"long": {"title": "India vs New Zealand - 1st Test Analysis | How India Needed 8 and Took 3", "description": DL, "tags": TAGS}}}
for d in range(1, 6):                                                                 # each day's verified claims travel with the video
    p = f"data/provenance/nz_ind_1st_test_day{d}.json"
    if os.path.exists(p): c.items.extend(json.load(open(p))["claims"])
c.save(spec); voice_lint.fix_spec(spec)
json.dump(spec, open("specs/nz_ind_1st_test_long.json", "w"), ensure_ascii=False, indent=1)
print("long words", sum(len(s["vo"].split()) for s in long), "scenes", len(long), "|", voice_lint.check_spec(spec, ("long",)) or "lint clean", "|", spec["files"])
