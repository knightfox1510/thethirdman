"""Builds specs/dyk_fielding_positions.json: Did You Know? Ep. 1, "Fielding positions explained: where is third man?" (a Short).
Definitions are checked against two independent written sources (claims in dataops/verify.py):
  - Wikipedia: "Fielding (cricket)" (naming system, silly [citing the OED], square, slips numbered outwards, close catchers) and "Glossary of cricket terms" (third man).
  - SportPlan, "Cricket Fielding Positions Explained (With a Full Field Diagram)": same points in its own words.
Neither explains why it is called "third man", and we found no documented origin: the video says so instead of repeating a theory.
Field plans are illustrative (right-handed batter; mirrored for a left-hander)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voice_lint
from dataops import verify as V

c = V.Claims("dyk_fielding_positions")
W, G = "wikipedia", "sportplan_guide"
c.check("names work as two parts: an angle word (cover, mid-wicket, leg) and a distance word (short, deep, long, silly)", "angle word + distance word", {W: "angle word + distance word", G: "angle word + distance word"})
c.check("silly = very close to the batter (a perceived danger)", "very close, dangerous", {W: "very close, dangerous", G: "very close, dangerous"})
c.check("square = level with the batter, across the pitch", "level with the batter", {W: "level with the batter", G: "level with the batter"})
c.check("slips are numbered outwards from the wicket-keeper", "first slip nearest the keeper", {W: "first slip nearest the keeper", G: "first slip nearest the keeper"})
c.check("third man is on the off side, behind the wicket", "off side, behind the wicket", {W: "off side, behind the wicket", G: "off side, behind the wicket"})
c.check("third man stops edges that get past the slips (purpose)", "stops edges past the slips", {W: None, G: "stops edges past the slips", "cricketwriter_guide": "stops edges past the slips"})
c.check("no documented origin of the name 'third man' found", "no documented origin", {W: "no documented origin", G: "no documented origin"})

def S(vo, sc, **kw): return dict({"vo": vo, "scene": sc}, **kw)
def board(vo, head, fielders, **kw): return S(vo, dict({"type": "board", "tone": "navy", "tag": "ILLUSTRATIVE FIELD", "head": head, "fielders": fielders, "batter_label": "", "big_labels": True}, **kw))
ALL = ["keeper", "slip", "2nd slip", "gully", "point", "cover", "mid-off", "mid-on", "midwicket", "square leg", "fine leg", "third man", "deep midwicket", "long-on"]
short = [
 board("Third man. Silly mid-off. Deep backward square leg. Cricket's fielding names sound like nonsense. But they are a code, and once you can read it, you can read any field.",
       ["Cricket's fielding names", "[are a code]"], ALL, labels=False, note=["third man · silly mid-off", "deep backward square leg"]),
 board("The first word gives the angle from the batter: leg, cover, mid-wicket, point.",
       ["Word one:", "[the angle]"], ["cover", "midwicket", "point", "square leg"], hl=["cover", "midwicket"], note=["leg · cover · mid-wicket · point"]),
 board("A second word gives the distance. Short is closer. Deep or long is farther. And silly means so close that it looks dangerous, which is exactly where the name comes from.",
       ["Word two:", "[the distance]"], ["short leg", "deep square leg", "cover", "deep cover"], hl=["short leg", "deep square leg"], note=["short = closer · deep or long = farther", "[silly = dangerously close]"]),
 board("Square means level with the batter, across the pitch. Backward and forward tilt the angle.",
       ["Square means", "[level with the bat]"], ["square leg", "point", "backward point"], hl=["square leg", "point"], note=["square = level with the batter", "backward / forward tilt the angle"]),
 board("Close catchers have their own code. Slips are numbered outwards from the wicket-keeper: first slip, second slip, third slip. Together, the slip cordon.",
       ["Slips are numbered", "[from the keeper]"], ["keeper", "slip", "2nd slip", "3rd slip", "gully"], zones=[{"pos": ["slip", "2nd slip", "3rd slip"], "label": "slip cordon", "at": .3}], note=["first slip · second slip · third slip", "numbered outwards from the keeper"]),
 board("Third man stands behind the wicket, on the off side, far beyond the slips. His job: stop the edges that fly past them and race to the boundary.",
       ["Where is", "[third man?]"], ["keeper", "slip", "2nd slip", "gully", "third man"], hl=["third man"], labels=True, note=["off side, behind the wicket,", "[far beyond the slips]"]),
 S("So why is it called third man? Honestly, nobody has a documented answer. The name is old, and the explanations you hear are only theories.",
   {"type": "stage", "panel": {"kind": "headline", "kicker": "WHY 'THIRD'?", "lines": [{"t": "NO DOCUMENTED"}, {"t": "ANSWER.", "c": "gold"}], "at": .05}, "avatars": [{"kit": "IND", "pose": "point", "x": .5}], "cam": "push", "fx": ["vignette", "spot"]}),
 {"vo": "Now you can read any field. Follow for more Did You Know.", "scene": {"type": "cta", "lines": [{"t": "DID YOU KNOW?"}, {"t": "FOLLOW FOR MORE", "c": "gold"}], "yt": {"label": "THE THIRD MAN", "handle": "@thethirdman_angle", "sub": "SUBSCRIBE · INSTAGRAM @thethirdman.angle", "bio": None}}},
]
SRC = ["Definitions checked against two independent written sources: Wikipedia, 'Fielding (cricket)' https://en.wikipedia.org/wiki/Fielding_(cricket) (naming system; 'silly' per the Oxford English Dictionary; slips numbered outwards from the wicket-keeper) and 'Glossary of cricket terms' https://en.wikipedia.org/wiki/Glossary_of_cricket_terms (third man: behind the wicket-keeper on the off side, beyond slip and gully); and SportPlan, 'Cricket Fielding Positions Explained' https://www.sportplan.net/drills/Cricket/guides/cricket-fielding-positions-explained.jsp (same points; third man's purpose, also stated by https://www.cricketwriter.com/cricket-fielding-positions-third-man/).",
       "Neither source, and no other we found, documents why the position is called 'third man'; the video says the origin is not documented. Field plans are illustrative, for a right-handed batter (mirrored for a left-hander); positions are neither fixed nor precisely defined and fielders can stand anywhere. Figures: make_dyk_fielding.py."]
DESC = ("Fielding positions explained: where is third man, and why are cricket's fielding names so strange? The names are a code: an angle word (leg, cover, mid-wicket, point) and a distance word (short, deep, long, silly). Slips are numbered outwards from the wicket-keeper; third man stands behind the wicket on the off side. "
        "Why is it called third man? No documented origin exists. Illustrative field plans for a right-handed batter. Sources: Wikipedia (Fielding (cricket); Glossary of cricket terms) and SportPlan's fielding positions guide.\n\n#DidYouKnow #CricketExplained #FieldingPositions #Shorts")
TAGS = ["fielding positions", "cricket fielding positions explained", "third man", "silly point", "slip cordon", "cricket explained", "Did You Know", "cricket rules", "The Third Man"]
spec = {"slug": "dyk_fielding_positions", "theme": "stadium", "captions": "v2", "captions_long": False, "series": "didyouknow", "tag": "DID YOU KNOW?", "tagsub": "EP. 1 · FIELDING POSITIONS",
        "files": {"long": "Did_You_Know_Ep01_unused", "short": "x"},
        "thumb": {"kicker": "DID YOU KNOW? · EP. 1", "lines": [{"t": "WHERE IS"}, {"t": "THIRD MAN?", "c": "gold"}], "hero": "?", "herosize": 420},
        "sources": SRC, "venue": {"time": "dusk", "crowd": [[190, 235, 70], [240, 240, 240], [25, 100, 200], [20, 60, 140]], "boards": [[25, 100, 200], [190, 235, 70]]}, "short": short,
        "yt": {"short": {"title": "Fielding Positions Explained: Where Is Third Man? | Did You Know Ep 1 #Shorts", "description": DESC, "tags": TAGS}}}
c.save(spec)
voice_lint.fix_spec(spec)
json.dump(spec, open("specs/dyk_fielding_positions.json", "w"), ensure_ascii=False, indent=1)
print("wrote spec,", sum(len(x["vo"].split()) for x in short), "words,", len(short), "scenes")
