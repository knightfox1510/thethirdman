"""Writes specs/lab_ep3_vaibhav_204.json: The Lab Ep 3, Vaibhav Suryavanshi's 204 off 53 (India A v UAE, 24 Nov 2026) and what makes it possible. VERTICAL (~160 s). Storyboard: docs/VAIBHAV_SCRIPT.md.
Data: analysis/vaibhav.py (IPL/T20I splits), analysis/vaibhav_uae.py (the innings, from the owner's match commentary capture). No source named on screen or in the voice-over.   python3 make_vaibhav.py"""
import json, os, sys
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
U = json.load(open("data/provenance/vaibhav_uae_figures.json")); F = json.load(open("data/provenance/vaibhav_figures.json")); I = U["innings"]; M = U["milestones_balls"]; CB = "cricbuzz"; CI = "cricinfo"
assert (I["runs"], I["balls"], I["fours"], I["sixes"], round(I["sr"]), round(I["boundary_share"])) == (204, 53, 7, 28, 385, 96) and M == {"50": 16, "100": 28, "150": 40, "200": 52} and U["six_dirs"] == {"leg_side": 8, "straight": 7, "off_side": 8}
ip = F["ipl"]; assert (ip["inns"], ip["all"]["runs"], round(ip["all"]["sr"])) == (23, 1028, 229)
t4, rs = ip["vs_top4"]["top4"], ip["vs_top4"]["rest"]; assert (round(t4["sr"]), round(rs["sr"]), round(t4["avg"]), round(rs["avg"])) == (248, 207, 54, 36)
po = ip["playoffs"]; assert (po["runs"], po["balls"]) == (193, 76)
bw = {x["bowler"]: x for x in ip["bowlers"]}
T = F["t20i"]; assert len(T) == 10 and sum(x["runs"] for x in T) == 295
def agg(xs): r = sum(x["runs"] for x in xs); b = sum(x["balls"] for x in xs); o = sum(1 for x in xs if x["out"]); return round(100 * r / b), round(r / max(o, 1)), r, b, o
zim = agg([x for x in T if "Zimbabwe" in x["teams"]]); big = agg([x for x in T if set(x["teams"]) & {"England", "New Zealand", "Pakistan", "Sri Lanka"}])
assert zim[:2] == (196, 50) and big[:2] == (176, 21), (zim, big)
dm = ip["dismissal_types"]; assert dm["Catch Out"] == 18 and sum(dm.values()) == 23
pi = [x for x in ip["innings"] if x["po"]]; assert [(x["runs"], x["balls"]) for x in pi] == [(97, 29), (96, 47)]
d = {x["date"]: x["bowler"] for x in ip["dismissals"]}; assert d["2026-05-27"] == "Praful Hinge" and d["2026-05-29"] == "Kagiso Rabada"
c = V.Claims("lab_ep3_vaibhav_204")
c.check("India A v UAE, Asia Cup Rising Stars (50 overs), 24 Nov 2026: India A chased 250 in 14.2 overs; Vaibhav 204 (53), 7 fours, 28 sixes (196 in boundaries, SR 385)", (250, 14.2, 204, 53, 7, 28, 196), {CB: (250, 14.2, 204, 53, 7, 28, 196), CI: (250, 14.2, 204, 53, 7, 28, 196)}, scope="archive")
c.check("milestones in balls 50/100/150/200: 16/28/40/52 (match commentary; the records are said as 'in our records')", (16, 28, 40, 52), {CB: (16, 28, 40, 52)}, scope="archive")
c.check("28 sixes: 23 placed from the commentary text: 8 leg side, 7 straight, 8 off side", (23, 8, 7, 8), {CB: (23, 8, 7, 8)}, scope="archive")
c.check("by bowler: Ibrar Ahmad 57 off 13, Basil Hameed 43 off 12 (dismissed him c Aryansh Sharma 12.5)", (57, 13, 43, 12), {CB: (57, 13, 43, 12)}, scope="archive")
c.check("IPL career: 23 innings, 1,028 runs, SR 229", (23, 1028, 229), {"sportmonks": (23, 1028, 229), CI: (23, 1028, 229)})
c.check("IPL splits (our count): vs top-four sides by season wins SR %d (avg %d) vs the rest %d (avg %d); playoffs 193 off 76" % (round(t4["sr"]), round(t4["avg"]), round(rs["sr"]), round(rs["avg"])), (248, 207, 193, 76), {"sportmonks": (248, 207, 193, 76)}, scope="archive")
c.check("T20I career: 10 innings, 295 runs", (10, 295), {"cricsheet": (10, 295), CI: (10, 295)})
c.check("T20I splits (our count): v England/NZ/Pakistan/Sri Lanka avg %d SR %d; v Zimbabwe avg %d SR %d" % (big[1], big[0], zim[1], zim[0]), (21, 176, 50, 196), {"cricsheet": (21, 176, 50, 196)}, scope="archive")
c.check("dismissed in the IPL playoffs: Eliminator 97 (29) c off Praful Hinge, Qualifier Two 96 (47) c off Kagiso Rabada; 18 of 23 IPL dismissals caught", (97, 29, 96, 47, 18, 23), {"sportmonks": (97, 29, 96, 47, 18, 23)}, scope="archive")
c.check("registered DOB 27 March 2011: aged 15 years 8 months on 24 Nov 2026; youngest male cricketer to play for India (reported)", (2011, 3, 27, 15, 8), {CB: (2011, 3, 27, 15, 8)}, scope="archive")
c.check("first-class: 11 matches, average 23.5", (11, 23.5), {CI: (11, 23.5)}, scope="archive")
IN = "data/licensed/in/"; T1 = IN + "vaibhav_technique_ref.jpg"; T2 = IN + "vaibhav_technique_graphic2.png"
pts = [[x["ang"], x["runs"] if x["runs"] < 4 else x["runs"], "s" if x["res"] == "SIX" else ("f" if x["res"] == "FOUR" else "n")] for x in U["rows"] if x["ang"] is not None and x["res"] in ("SIX", "FOUR", "1 run", "2 runs")]
COLD = {"type": "photocard", "kicker": "INDIA A V UAE · 24 NOVEMBER 2026", "title": "204.", "img": IN + "vaibhav_celebration.webp", "crop_short": (0, 60, 718, 538), "tag": "204 (53) · 28 SIXES", "name": "VAIBHAV SURYAVANSHI", "mono": "AGED 15 YEARS, 8 MONTHS", "caption": "India A chased 250 with 214 balls to spare", "chip": "385", "chip_sub": "STRIKE RATE"}
STATS = {"type": "stats", "head": {"t": "THE INNINGS", "sub": "INDIA A CHASED 250 IN 14.2 OVERS"}, "tiles": [{"v": "385", "l": "STRIKE RATE", "c": "red"}, {"v": "96%", "l": "OF HIS RUNS IN BOUNDARIES", "c": "gold"}, {"v": "11", "l": "DOT BALLS OF 53", "c": "ink"}]}
MILE = {"type": "bars", "head": {"t": "BALLS FOR EACH FIFTY", "sub": "204 OFF 53 · IN OUR RECORDS"}, "max": 20, "dec": 0, "items": [{"label": "0 TO 50", "value": 16, "color": "ink"}, {"label": "50 TO 100", "value": 12, "color": "gold"}, {"label": "100 TO 150", "value": 12, "color": "gold"}, {"label": "150 TO 200", "value": 12, "color": "red"}]}
WAG = {"type": "wagon", "head": {"t": "28 SIXES", "sub": "WHERE THE RUNS WENT · ILLUSTRATIVE"}, "pts": pts, "photo": {"img": IN + "vaibhav_portrait.jpg", "crop": (480, 20, 980, 520)}, "chips": [("8", "LEG SIDE"), ("7", "STRAIGHT"), ("8", "OFF SIDE")], "footnote": "23 OF 28 SIXES PLACED · ZONES READ FROM OUR BALL-BY-BALL NOTES"}
BWL = {"type": "bars", "head": {"t": "RUNS OFF EACH BOWLER", "sub": "UAE ATTACK · BALLS FACED IN BRACKETS"}, "max": 60, "dec": 0, "items": [{"label": "IBRAR AHMAD (13)", "value": 57, "color": "red"}, {"label": "ZAHID ALI (14)", "value": 45, "color": "ink"}, {"label": "BASIL HAMEED (12)", "value": 43, "color": "gold"}, {"label": "UDDISH SURI (9)", "value": 41, "color": "ink"}, {"label": "SIMRANJEET (5)", "value": 18, "color": "ink"}]}
AGE = {"type": "photocard", "kicker": "THE YOUNGEST TO PLAY FOR INDIA", "title": "15.", "img": IN + "vaibhav_portrait.jpg", "crop_short": (400, 0, 1100, 467), "tag": "BORN 27 MARCH 2011 · AS REGISTERED", "name": "15 YEARS, 8 MONTHS", "mono": "TWO IPL SEASONS", "caption": "1,028 IPL runs at a strike rate of 229", "chip": "1,028", "chip_sub": "IPL RUNS · 23 INNINGS"}
CMP1 = {"type": "compare", "head": {"t": "BIG TEAMS, SMALL TEAMS?", "sub": "T20 INTERNATIONALS · 10 INNINGS"}, "a": {"name": "ENG · NZ · PAK · SL", "color": "ink"}, "b": {"name": "ZIMBABWE", "color": "gold"}, "rows": [["AVERAGE", str(big[1]), str(zim[1]), "b"], ["STRIKE RATE", str(big[0]), str(zim[0]), "b"]]}
CMP2 = {"type": "compare", "head": {"t": "IN THE IPL IT FLIPS", "sub": "STRIKE RATE AND AVERAGE · 23 INNINGS"}, "a": {"name": "TOP FOUR SIDES", "color": "red"}, "b": {"name": "THE REST", "color": "ink"}, "rows": [["STRIKE RATE", "248", "207", "a"], ["AVERAGE", "54", "36", "a"]]}
GOT = {"type": "list", "head": {"t": "WHO GOT HIM", "sub": "ON THE BIG STAGES"}, "items": [{"h": "ELIMINATOR · HINGE", "d": "caught for 97 off 29 balls", "c": "gold", "cue": "hinge"}, {"h": "QUALIFIER 2 · RABADA", "d": "caught for 96 off 47 balls", "c": "gold", "cue": "rabada"}, {"h": "T20Is · ARCHER TWICE", "d": "then Jacks, Saim Ayub, Fisher, Smith", "cue": "archer"}]}
TE1 = {"type": "techimg", "head": {"t": "WHY IT WORKS", "sub": "THE TECHNIQUE · 1 OF 4"}, "img": T1, "box": (370, 40, 520, 240), "zoom": 1.0, "ring": (435, 95, 85), "n": "1", "title": "BAT PAST THE VERTICAL", "tag": "THE BACKSWING", "body": "A longer swing arc, and more time to build bat speed before impact. Experts say it looks closer to baseball or golf than cricket."}
TE2 = {"type": "techimg", "head": {"t": "WHY IT WORKS", "sub": "THE TECHNIQUE · 2 OF 4"}, "img": T1, "box": (250, 190, 500, 330), "zoom": 1.0, "ring": (360, 270, 120), "n": "2", "title": "CLOSED SHOULDERS", "tag": "SEPARATION", "body": "At the top of the backswing, his shoulders stay closed against his hips. The more of that separation, the more force when the body unwinds."}
TE3 = {"type": "techimg", "head": {"t": "WHY IT WORKS", "sub": "THE TECHNIQUE · 3 OF 4"}, "img": T2, "box": (440, 330, 600, 580), "zoom": 1.0, "ring": (500, 470, 110), "n": "3", "title": "THE BRACED FRONT KNEE", "tag": "THE DOWNSWING", "body": "Like a fast bowler's front leg: the lower body stops, the upper body flings through. Weight transfer becomes rotation."}
FOL = {"type": "follow", "head": {"t": "THE FINISH", "sub": "THE TECHNIQUE · 4 OF 4 · ILLUSTRATIVE"}}
WEAK = {"type": "statement", "kicker": "SO WHERE IS THE WEAKNESS?", "lines": [{"t": "NOT FOUND"}, {"t": "YET.", "c": "gold"}], "sub": "18 of his 23 IPL dismissals were catches. The red ball is the open question: 11 first-class matches, average 23."}
COUR = {"type": "statement", "kicker": "THE EXPERTS' PUZZLE", "lines": [{"t": "TECHNIQUE CAN"}, {"t": "BE TAUGHT.", "c": "gold"}], "sub": "“The courage to hit cannot.” His childhood coach, on why others who hit as far are not Vaibhav."}
POLL = {"type": "list", "head": {"t": "YOUR CALL", "sub": "WHERE IS THE WEAKNESS? COMMENT 1, 2 OR 3"}, "items": [{"h": "1 · LEFT-ARM PACE", "d": "and off-spin", "c": "gold", "cue": "left"}, {"h": "2 · THE RED BALL", "d": "Tests will tell", "cue": "red"}, {"h": "3 · NOWHERE YET", "d": "bowlers haven't found it", "cue": "nowhere"}]}
short = [
    {"vo": "Two hundred and four. Off fifty-three balls. Twenty-eight sixes. Vaibhav Sooryavanshi is fifteen years old.", "scene": COLD},
    {"vo": "India A needed two fifty. They finished with two hundred and fourteen balls to spare, and ninety-six per cent of his runs were boundaries.", "scene": STATS},
    {"vo": "Fifty off sixteen balls. Then a hundred, a hundred and fifty, two hundred, each fifty in just twelve. In our records, nothing faster.", "scene": MILE},
    {"vo": "Where did the sixes go? Twenty-three we could place: eight over the leg side, seven straight, eight over the off side. No bowler could hide.", "scene": WAG},
    {"vo": "Ibrar Ahmad went for fifty-seven off thirteen balls. Basil Hameed, forty-three off twelve, and he is the one who finally got him.", "scene": BWL},
    {"vo": "Officially registered date of birth, twenty-seventh March, twenty eleven. Fifteen years, eight months, the youngest to play for India, with a thousand and twenty-eight IPL runs already.", "scene": AGE},
    {"vo": "Does he only beat small teams? In T-twenty internationals, against England, New Zealand, Pakistan and Sri Lanka, he averages twenty-one. Against Zimbabwe, fifty.", "scene": CMP1},
    {"vo": "But in the IPL, it flips. Against the top four sides, a strike rate of two forty-eight. Against the rest, two oh seven.", "scene": CMP2},
    {"vo": "Who got him on the big stages? Praful Hinge, in the Eliminator, for ninety-seven. Rabada, in Qualifier Two, for ninety-six. In T-twenty internationals, Archer twice.", "scene": GOT},
    {"vo": "So why does it work? His bat goes past the vertical, a longer arc, more time to build speed. Experts say it looks closer to baseball or golf than cricket.", "scene": TE1},
    {"vo": "At the top of the backswing, his shoulders stay closed against his hips. They call it separation. The more of it, the more force when the body unwinds.", "scene": TE2},
    {"vo": "Then the front knee braces, like a fast bowler's. The lower body stops, the upper body flings through. Weight transfer turns into rotation.", "scene": TE3},
    {"vo": "Most batters finish like a C. His finish is closer to an O, the bat high above the shoulder, the shoulder held in line.", "scene": FOL},
    {"vo": "So where is the weakness? Eighteen of his twenty-three IPL dismissals were catches. And the red ball is the open question: eleven first-class matches, average twenty-three.", "scene": WEAK},
    {"vo": "His childhood coach says technique can be taught, the courage to hit cannot. And experts say the bowlers haven't found his weakness yet.", "scene": COUR},
    {"vo": "Where is the weakness? Comment one, left-arm pace. Two, the red ball. Three, nowhere yet.", "scene": POLL},
    dict(YT_CTA, vo="Subscribe, and we'll break down every big innings like this."),
]
SRC = ["The innings (India A v UAE, Asia Cup Rising Stars, 24 November 2026): Cricbuzz ball-by-ball commentary and Cricinfo ball-by-ball (owner's captures); 204 (53), 28 sixes, 7 fours cross-checked in both. Milestones and shot directions come from the commentary text only.",
       "Career: IPL ball-by-ball (Sportmonks, IPL 2025-26: 23 innings, 1,028 runs, SR 229); T20 internationals (Cricsheet, 10 innings, 295 runs; Cricinfo profile). Splits against teams and bowlers are our own count (analysis/vaibhav.py).",
       "Technique: Cricbuzz feature, 'What makes Vaibhav Sooryavanshi possible' (comments from a Loughborough University biomechanics researcher, a power-hitting coach and Vaibhav's childhood coach, paraphrased). Technique graphics: owner-supplied, redrawn.",
       "Date of birth (27 March 2011) as officially registered, as reported; some reports question it."]
TAGS = ["Vaibhav Suryavanshi", "Vaibhav Sooryavanshi", "204 off 53", "India A vs UAE", "Asia Cup Rising Stars", "Rajasthan Royals", "IPL 2026", "cricket analysis", "batting technique", "The Third Man"]
DS = ("Vaibhav Suryavanshi, 15 years old, hit 204 off 53 balls for India A against the UAE in the Asia Cup Rising Stars, 28 sixes, a strike rate of 385. What makes it possible: the bat past the vertical, closed shoulders, the braced front knee, the O-shaped follow-through. How he does against small and big teams, and the bowlers who have got him on the big stages (Praful Hinge in the Eliminator, Kagiso Rabada in Qualifier Two). Date of birth as officially registered. Comment 1 left-arm pace, 2 the red ball, 3 nowhere yet.\n\n#VaibhavSuryavanshi #INDAvUAE #RisingStars #Shorts")
spec = {"slug": "lab_ep3_vaibhav_204", "theme": "lab", "theme_long": "lab", "captions": "lab", "captions_long": False, "series": "lab", "tag": "THE LAB", "tagsub": "VAIBHAV SURYAVANSHI · 204 OFF 53",
        "files": {"long": "_unused", "short": "x"}, "venue": {"time": "day", "crowd": [[20, 20, 22], [230, 230, 230], [25, 100, 200], [20, 60, 140]], "boards": [[20, 20, 22], [25, 100, 200]]},
        "thumb": {"kicker": "INDIA A V UAE · 24 NOV 2026", "lines": [{"t": "204 OFF 53"}, {"t": "AGED 15", "c": "gold"}], "hero": "204", "herosize": 360},
        "ig_cover": {"lines": [{"t": "204 OFF 53"}, {"t": "AGED 15", "c": "gold"}], "sub": "VAIBHAV SURYAVANSHI", "hero": "204"}, "sources": SRC, "short": short,
        "yt": {"short": {"title": "Vaibhav Suryavanshi: 204 Off 53 Balls, Explained | India A vs UAE #Shorts", "description": DS, "tags": TAGS}}}
c.save(spec); voice_lint.fix_spec(spec)
json.dump(spec, open("specs/lab_ep3_vaibhav_204.json", "w"), ensure_ascii=False, indent=1)
print("short words", sum(len(s["vo"].split()) for s in short), "|", voice_lint.check_spec(spec, ("short",)) or "lint clean", "|", spec["files"], "| chars", sum(len(s["vo"]) for s in short))
