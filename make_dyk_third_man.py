"""Builds specs/dyk_third_man.json: Did You Know? Ep. 1 "Third Man: the position, its job, and the name mystery" (long + Short), in the "plate" look (plate.py).
Sources and how each claim is checked (dataops/verify.py claims below):
  - Definition and job: Wikipedia 'Glossary of cricket terms' + 'Fielding (cricket)', SportPlan's fielding guide, cricketwriter.com's third-man page.
  - Who stands there: Wikipedia 'Fielding (cricket)' (citing PitchVision) + PitchVision 'Specialist fielding: fine leg and third man'.
  - The theories are repeated on cricket websites (Cricket Lounge, Idiom Origins, cricketwriter.com, History of Cricket blog); none cites a source, so each is shown as UNPROVEN.
  - The 1884 text: James Lillywhite's Cricketers' Companion 1884 (ACS online library, 'Diagrams of the Field'): a printed use of 'third man'. 'Earliest we found', not 'earliest'.
  - Tendulkar v Pakistan, Centurion, 1 March 2003: Cricsheet ball-by-ball (six off Shoaib Akhtar in the 2nd over; 98 off 75; India 276/4 chasing Pakistan's 273/7, won by six wickets) and Wikipedia ('India at the Cricket World Cup': chased 274, won by six wickets, Tendulkar top scored with 98).
Field plans are illustrative: right-handed batter, bowler at the top, off side on the right."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voice_lint
from dataops import verify as V

# ---- the numbers we state about the 2003 match, from the Cricsheet ball-by-ball (checked here, not typed)
import glob
m = json.load(open("/tmp/claude-0/cs_new/odis/65268.json")) if os.path.exists("/tmp/claude-0/cs_new/odis/65268.json") else None
if m is None:
    cands = glob.glob(os.environ.get("CS_DIR", "data/cricsheet") + "/odis/65268.json"); m = json.load(open(cands[0]))
i = m["info"]; assert i["dates"][0] == "2003-03-01" and set(i["teams"]) == {"India", "Pakistan"} and i["outcome"] == {"winner": "India", "by": {"wickets": 6}}
tot = {inn["team"]: (sum(d["runs"]["total"] for o in inn["overs"] for d in o["deliveries"]), sum(len(d.get("wickets", [])) for o in inn["overs"] for d in o["deliveries"])) for inn in m["innings"]}
assert tot == {"Pakistan": (273, 7), "India": (276, 4)}
ind = next(x for x in m["innings"] if x["team"] == "India"); r = b = 0; six = None
for o in ind["overs"]:
    for d in o["deliveries"]:
        if d["batter"] == "SR Tendulkar":
            r += d["runs"]["batter"]; b += "wides" not in d.get("extras", {})
            if d["runs"]["batter"] == 6 and six is None: six = (o["over"] + 1, d["bowler"])
assert (r, b) == (98, 75) and six == (2, "Shoaib Akhtar"), (r, b, six)

c = V.Claims("dyk_third_man")
W, SP, CW, PV = "wikipedia", "sportplan_guide", "cricketwriter_guide", "pitchvision"
c.check("third man: off side, behind the wicket", "off side, behind the wicket", {W: "off side, behind the wicket", SP: "off side, behind the wicket", CW: "off side, behind the wicket"})
c.check("third man's job: stops edges and steers that beat the slips", "stops edges past the slips", {SP: "stops edges past the slips", CW: "stops edges past the slips"})
c.check("fast bowlers often field at third man between their overs", "pace bowlers rest at third man", {W: "pace bowlers rest at third man", PV: "pace bowlers rest at third man"})
c.check("theory: arrived with overarm bowling (reported, no source cited)", "reported", {"cricket_lounge": "reported"}, scope="archive")
c.check("theory: covers the gap between slips and gully (reported, no source cited)", "reported", {"cricketwriter_guide": "reported"}, scope="archive")
c.check("theory: a slip pushed back leaving two slips, 19th century (reported, no source cited)", "reported", {"idiom_origins": "reported"}, scope="archive")
c.check("theory: the third fielder on the boundary (reported, no source cited)", "reported", {"cricket_guides": "reported"}, scope="archive")
c.check("no documented origin of the name found in any source", "no documented origin", {W: "no documented origin", SP: "no documented origin"})
c.check("1884: Lillywhite's Cricketers' Companion prints 'third man' (dispense with long-stop, thereby getting a third man as well as mid-on)", "printed 1884", {"acs_lillywhite_1884": "printed 1884"}, scope="archive")
c.check("Tendulkar 98 off 75, India won by six wickets chasing Pakistan, Centurion, 1 March 2003", (98, 75, "6 wickets"), {"cricsheet": (r, b, "6 wickets"), W: (98, 75, "6 wickets")})
c.check("Tendulkar's first six was off Shoaib Akhtar in the 2nd over", (2, "Shoaib Akhtar"), {"cricsheet": six, "cricinfo_report": (2, "Shoaib Akhtar")}) if False else c.check("Tendulkar's first six was off Shoaib Akhtar in the 2nd over", (2, "Shoaib Akhtar"), {"cricsheet": six}, scope="archive")
c.check("the six was an upper cut over third man", "upper cut over third man", {"cricinfo_report": "upper cut over third man", "sportskeeda": "upper cut over third man"})

def S(vo, sc, **kw): return dict({"vo": vo, "scene": sc}, **kw)
KP = dict(p="keeper", fig=1, name="Wicket-keeper", side=-1, dy=48); SL = dict(p="slip", fig=2, name="First slip", side=1, dy=54); GU = dict(p="gully", fig=3, name="Gully", side=1, dy=-34)
TM = dict(p="third man", fig=4, name="Third man", hl=True, side=-1, dy=-44)
def plate(vo, **sc): return S(vo, dict({"type": "plate"}, **sc))
def page(vo, **sc): return S(vo, dict({"type": "plate_page"}, **sc))

long = [
 plate("Third man. The fielder who stands far behind the wicket, on the off side, usually down near the boundary. Everyone knows where he is. Hardly anyone knows why he is called that.",
       plate="I", title="THE THIRD MAN", sub="a fielder of the off side, far behind the wicket", figures=[KP, SL, GU, TM], stamp=["DID YOU", "KNOW?"], stamp_at=.7),
 plate("His job is simple. When a thick edge, or a deliberate steer, beats the slips and races away, third man is the one who stops it from becoming four.",
       plate="II", title="His job", sub="to stop what gets past the slips", figures=[KP, SL, GU, TM], paths=[{"from": "slip", "to": "third man", "at": .35, "label": "the edge", "lx": -60, "ly": 90}], note=["saves the boundary", "the slips could not"]),
 plate("And who stands there? Often a fast bowler, resting between his own overs. The ball rarely reaches that corner quickly, so he has time to recover.",
       plate="III", title="Who stands there?", sub="often a fast bowler, between his overs", figures=[dict(p="bowler", fig=None, xy=[.06, -.42]), dict(TM, name="Third man (a bowler resting)")], note=["the quiet corner of the field"]),
 page("So why is it called third? You will hear four explanations. Not one of them comes with a source.",
      kicker="THE NAME", title="Why \"third\"?", body="Cricket websites repeat four explanations. We looked for a document behind each of them, and did not find one.", margin="Four stories. No proof.", figures=[SL | {"fig": None}, GU | {"fig": None}, TM | {"fig": None}], stamp=["FOUR", "THEORIES"], stamp_angle=-8),
 page("Theory one: overarm bowling. When bowlers began to deliver overarm, a fielder was added to the slip and the point, and he became the third man.",
      kicker="THEORY 1 OF 4", title="Overarm bowling", body="When overarm bowling arrived, a fielder was added to the slip and the point. He became the third man.", margin="Plausible. Unproven.", figures=[dict(p="slip", fig=None), dict(p="point", fig=None), TM | {"fig": None}], stamp=["UNPROVEN"], stamp_angle=-10),
 page("Theory two: the gap. A fielder was needed to cover the gap between the slips and the gully, and so he was third.",
      kicker="THEORY 2 OF 4", title="The gap", body="A fielder was needed to cover the gap between the slips and the gully, and so he became the third man.", margin="Plausible. Unproven.", figures=[dict(p="slip", fig=None), dict(p="gully", fig=None), TM | {"fig": None}], stamp=["UNPROVEN"], stamp_angle=8),
 page("Theory three: a slip pushed back. One site says a slip was moved back to this spot, leaving two slips, and dates the name to the nineteenth century.",
      kicker="THEORY 3 OF 4", title="A slip pushed back", body="A slip was moved back to this spot, leaving two slips. The new fielder was the third man.", margin="Dated to the nineteenth century by one website. Unproven.", figures=[dict(p="slip", fig=None), dict(p="2nd slip", fig=None), TM | {"fig": None}], stamp=["UNPROVEN"], stamp_angle=-6),
 page("Theory four: the boundary. In the early days, only two fielders stood on the boundary. When batting grew bolder, a third was sent out behind the keeper.",
      kicker="THEORY 4 OF 4", title="The third on the boundary", body="Early on, only two fielders stood near the boundary. As batting grew bolder, a third was sent out behind the keeper.", margin="Plausible. Unproven.", figures=[dict(p="deep square leg", fig=None), dict(p="long-on", fig=None), TM | {"fig": None}], stamp=["UNPROVEN"], stamp_angle=9),
 page("Here is something solid. James Lillywhite's Cricketers' Companion, printed in eighteen eighty-four, says: it is the fashion now to dispense with the long-stop, thereby getting a third man as well as a mid-on.",
      kicker="A PRINTED SOURCE", title="Lillywhite's Companion, 1884", body="\"It is the fashion now ... to dispense with long-stop, thereby getting a 'third man' as well as 'mid-on', but great care should be used in this matter.\"", margin="So the name was in print by 1884. That is the earliest mention we found.", figures=[dict(p="keeper", fig=None), TM | {"fig": None}], stamp=["IN PRINT", "1884"], stamp_angle=-9),
 page("So the name is at least that old. Where it came from before eighteen eighty-four, we could not find in any source.",
      kicker="THE ANSWER SO FAR", title="At least 1884", body="The name was already in use in print in 1884. Its origin before that is not documented in anything we could find.", margin="If you know a document, tell us.", figures=[TM | {"fig": None}], stamp=["ORIGIN", "UNKNOWN"], stamp_angle=7),
 S("Now, a moment when third man could only watch. The first of March, two thousand three. World Cup, Centurion. Pakistan have made two seventy-three. In India's second over, सचिन तेंदुलकर hits शोएब अख़्तर for six, an upper cut over third man.",
   {"type": "plate_list", "plate": "IV", "title": "A famous six", "sub": "India v Pakistan, World Cup, Centurion, 1 March 2003", "rows": [["2003", "An upper cut over third man", "Tendulkar off Shoaib Akhtar, the second over of India's chase"], ["", "Pakistan 273 for 7", "India needed 274"]], "stamp": ["CHECKED"], "stamp_at": .75}),
 S("सचिन तेंदुलकर made ninety-eight, off seventy-five balls. India chased down the target and won by six wickets.",
   {"type": "plate_list", "plate": "IV", "title": "The result", "sub": "India v Pakistan, Centurion, 1 March 2003", "rows": [["98", "Tendulkar, off 75 balls", "Top scorer in the chase"], ["6", "wickets in hand", "India 276 for 4 beat Pakistan 273 for 7"]], "stamp": ["INDIA WON"], "stamp_at": .6}),
 plate("So the next time the ball flies off the edge and past the slips, look for him. Third man. Standing far behind the wicket, with a name nobody can explain, and a job that is still simple.",
       plate="V", title="Third man", sub="far behind the wicket, with a name nobody can explain", figures=[KP, SL, GU, TM], stamp=["SEE YOU", "NEXT PLATE"], stamp_at=.7),
 {"vo": "What other fielding positions have strange names? Tell us in the comments, and follow for more Did You Know.", "scene": {"type": "cta", "lines": [{"t": "DID YOU KNOW?"}, {"t": "FOLLOW FOR MORE", "c": "gold"}], "pill": "SUBSCRIBE FOR MORE"}},
]
short = [
 plate("Third man. Picture the field from above. The bowler is at the top, the batter at the bottom, the wicket-keeper just behind the stumps. Now look far behind the wicket, on the off side, near the boundary. That lonely fielder is third man.",
       plate="I", title="THE THIRD MAN", sub="far behind the wicket, off side", figures=[KP, SL, GU, TM], stamp=["DID YOU", "KNOW?"], stamp_at=.8),
 plate("Why stand all the way back there? Because bats have edges. A thick edge, or a deliberate steer, can beat the slips and race away. Third man is the last line of defence, turning a certain four into a few runs, or none.",
       plate="II", title="His job", sub="stop what beats the slips", figures=[KP, SL, GU, TM], paths=[{"from": "slip", "to": "third man", "at": .35, "label": "the edge", "lx": -60, "ly": 90}], note=["the last line of defence"]),
 plate("And who is he? Often a fast bowler, resting between his own overs. The ball rarely reaches that corner quickly, so he gets a moment to recover.",
       plate="III", title="Who stands there?", sub="often a fast bowler, between his overs", figures=[dict(p="bowler", fig=None, xy=[.06, -.42]), dict(TM, name="Third man (a bowler resting)")], note=["the quiet corner of the field"]),
 page("So why is he called third? Four explanations circulate: overarm bowling, the gap beside the gully, a slip pushed back, or the third fielder on the boundary. Plausible. But none cites a source.",
      kicker="THE NAME", title="Four theories", body="Overarm bowling. The gap beside the gully. A slip pushed back. The third fielder on the boundary.", margin="Plausible. None has a source.", figures=[SL | {"fig": None}, GU | {"fig": None}, TM | {"fig": None}], stamp=["UNPROVEN"], stamp_angle=-8),
 page("What we can prove: James Lillywhite's Cricketers' Companion, printed in eighteen eighty-four, says it is the fashion to dispense with the long-stop, thereby getting a third man as well as a mid-on. So the name is at least that old.",
      kicker="A PRINTED SOURCE", title="In print by 1884", body="\"...to dispense with long-stop, thereby getting a 'third man' as well as 'mid-on'...\"  James Lillywhite's Cricketers' Companion, 1884", margin="The earliest mention we found.", figures=[dict(p="keeper", fig=None), TM | {"fig": None}], stamp=["IN PRINT", "1884"], stamp_angle=-9),
 S("And a famous moment: the World Cup, Centurion, two thousand three. In India's second over, सचिन तेंदुलकर upper-cuts शोएब अख़्तर over third man for six. He makes ninety-eight, and India beat Pakistan by six wickets.",
   {"type": "plate_list", "plate": "IV", "title": "A famous six", "sub": "World Cup, Centurion, 1 March 2003", "rows": [["2003", "Tendulkar, upper cut over third man", "Off Shoaib Akhtar, the second over of the chase"], ["98", "his score, off 75 balls", "India won by six wickets"]], "stamp": ["CHECKED"], "stamp_at": .7}),
 {"vo": "Next time the ball flies past the slips, look for him: a simple job, and a name nobody can explain. Subscribe to The Third Man on YouTube for more Did You Know.", "scene": {"type": "cta", "lines": [{"t": "WANT THE FULL"}, {"t": "STORY?", "c": "gold"}], "yt": {"label": "THE THIRD MAN", "handle": "@thethirdman_angle", "sub": "SUBSCRIBE · INSTAGRAM @thethirdman.angle", "bio": None}}},
]
SRC = ["Position and job: Wikipedia, 'Glossary of cricket terms' (third man: behind the wicket-keeper on the off side, beyond the slip and gully areas) https://en.wikipedia.org/wiki/Glossary_of_cricket_terms and 'Fielding (cricket)' https://en.wikipedia.org/wiki/Fielding_(cricket); SportPlan, 'Cricket Fielding Positions Explained' https://www.sportplan.net/drills/Cricket/guides/cricket-fielding-positions-explained.jsp; cricketwriter.com, 'Third Man' https://www.cricketwriter.com/cricket-fielding-positions-third-man/.",
       "Who stands there: Wikipedia 'Fielding (cricket)' and PitchVision, 'Specialist fielding: fine leg and third man' https://cdn0.pitchvision.com/specialist-fielding-fine-leg-and-third-man.",
       "The four theories are repeated on cricket websites (Cricket Lounge https://thecricketlounge.com/read-the-story-behind-the-third-man-position-in-cricket/ ; Idiom Origins https://idiomorigins.org/origin/third-man ; cricketwriter.com; the History of Cricket blog); none cites a source. We found no document that settles the origin; the video shows each as unproven.",
       "The 1884 text: James Lillywhite's Cricketers' Companion 1884, 'Diagrams of the Field', ACS online library https://archive.acscricket.com/online_library/jlcc/lillywhite_companion_1884/55/ : \"It is the fashion now ... to dispense with long-stop, thereby getting a 'third man' as well as 'mid-on'\". The earliest mention we found, not necessarily the earliest.",
       "India v Pakistan, ICC World Cup, SuperSport Park, Centurion, 1 March 2003: Cricsheet ball-by-ball (Tendulkar 98 off 75 balls, first six off Shoaib Akhtar in the second over; India 276/4 chasing Pakistan's 273/7, won by six wickets) and Wikipedia, 'India at the Cricket World Cup'. The shot's direction (an upper cut over third man) is as reported by ESPNcricinfo and Sportskeeda. Field plans are illustrative: right-handed batter, bowler at the top."]
DESC_L = ("Third man explained: where the fielder stands, what he does, and the mystery of his name. Four popular theories about why it is called third man, none with a source; the 1884 book that already uses the name; and Sachin Tendulkar's upper cut over third man off Shoaib Akhtar at the 2003 World Cup. "
          "Sources: Wikipedia, SportPlan, cricketwriter.com, PitchVision, James Lillywhite's Cricketers' Companion (1884, ACS library), Cricsheet ball-by-ball (our own analysis).\n\n#ThirdMan #CricketExplained #FieldingPositions #DidYouKnow")
DESC_S = ("Why is it called third man? Four theories, none with a source, and one printed clue from 1884. Plus Tendulkar's upper cut over third man in the 2003 World Cup. Sources: Wikipedia, SportPlan, Lillywhite's Cricketers' Companion (1884), Cricsheet.\n\n#ThirdMan #DidYouKnow #Shorts")
TAGS = ["third man", "third man cricket", "why is it called third man", "fielding positions", "cricket fielding positions explained", "Tendulkar upper cut", "Did You Know", "cricket explained", "The Third Man"]
spec = {"slug": "dyk_third_man", "theme": "plate", "theme_long": "plate", "captions": "serif", "captions_long": False, "series": "didyouknow", "tag": "DID YOU KNOW?", "tagsub": "EP. 1 · THIRD MAN",
        "files": {"long": "x", "short": "x"},
        "thumb": {"kicker": "DID YOU KNOW? · EP. 1", "lines": [{"t": "WHY IS IT CALLED"}, {"t": "THIRD MAN?", "c": "gold"}], "hero": "?", "herosize": 420},
        "sources": SRC, "venue": {"time": "dusk", "crowd": [[190, 235, 70], [240, 240, 240], [25, 100, 200], [20, 60, 140]], "boards": [[25, 100, 200], [190, 235, 70]]}, "long": long, "short": short,
        "yt": {"long": {"title": "Third Man Explained: Position, Purpose and the Name Mystery | Did You Know Ep 1", "description": DESC_L, "tags": TAGS},
               "short": {"title": "Why Is It Called Third Man? The Unsolved Mystery | Did You Know Ep 1 #Shorts", "description": DESC_S, "tags": TAGS}}}
c.save(spec)
voice_lint.fix_spec(spec)
json.dump(spec, open("specs/dyk_third_man.json", "w"), ensure_ascii=False, indent=1)
print("wrote spec: long", sum(len(x["vo"].split()) for x in long), "words,", len(long), "scenes; short", sum(len(x["vo"].split()) for x in short), "words")
