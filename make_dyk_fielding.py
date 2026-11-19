"""Builds specs/dyk_fielding_positions.json: Did You Know? Ep. 2, "Fielding positions: how to read any field" (a Short), in the "plate" look (plate.py).
Explanatory format (docs/DID_YOU_KNOW.md): what the names mean, show it drawn, the rule that limits where fielders may stand (Law 28.4), the loose-labels caveat.
Claims and where each is checked (dataops/verify.py claims below):
  - Naming system (angle word + distance word; silly / short / deep / long; square; fine; slips numbered outwards; positions not fixed): Wikipedia 'Fielding (cricket)' and SportPlan's fielding guide (plus Wikipedia 'Glossary of cricket terms' for cover/fine/cordon).
  - Which side each position is on: SportPlan guide, Wikipedia glossary (cover, mid-wicket named as off/leg side).
  - Law 28.4 (no more than two fielders, other than the wicket-keeper, behind the popping crease on the on side; breach = no ball): MCC Laws of Cricket 2017 Code (3rd edition 2022; quoted by Wisden) and the ICC Playing Conditions, Men's Test / ODI / T20I clause 28.4 (ODI 28.4.3: striker's end umpire calls no ball).
CAVEAT: MCC published a 2026 edition of the Laws (in force from October 2026). Its ten headline changes do not touch Law 28, but we could not read the full 2026 text, so the Law number is stated from the 2017 Code and the ICC conditions.
Field plans are illustrative: right-handed batter, bowler at the top, off side on the right."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voice_lint
from dataops import verify as V

c = V.Claims("dyk_fielding_positions")
W, SP, G = "wikipedia", "sportplan_guide", "wikipedia_glossary"
c.check("names work as two parts: an angle word (leg, cover, mid-wicket, point) and a distance word (silly, short, deep, long)", "angle word + distance word", {W: "angle word + distance word", SP: "angle word + distance word"})
c.check("short = closer to the batter; deep or long = farther", "short closer, deep/long farther", {W: "short closer, deep/long farther", SP: "short closer, deep/long farther"})
c.check("silly = so close to the batter that it is dangerous", "very close, dangerous", {W: "very close, dangerous", SP: "very close, dangerous"})
c.check("square = level with the batter, across the pitch", "level with the batter", {W: "level with the batter", SP: "level with the batter"})
c.check("fine = behind the batter, closer to the line of the pitch (the opposite of square)", "behind, near the line of the pitch", {G: "behind, near the line of the pitch", SP: "behind, near the line of the pitch"})
c.check("point, cover, mid-off are off-side positions", "off side", {SP: "off side", G: "off side"})
c.check("mid-on, mid-wicket, square leg are leg-side positions", "leg side", {SP: "leg side", G: "leg side"})
c.check("fine leg is behind square on the leg side; third man is its off-side counterpart", "fine leg / third man", {SP: "fine leg / third man", W: "fine leg / third man"})
c.check("slips are numbered outwards from the wicket-keeper; together the slip cordon", "numbered outwards from the keeper", {W: "numbered outwards from the keeper", SP: "numbered outwards from the keeper"})
c.check("gully is squarer than the slips, on the off side", "squarer than the slips, off side", {SP: "squarer than the slips, off side", G: "squarer than the slips, off side"})
c.check("Law 28.4: no more than two fielders, other than the wicket-keeper, behind the popping crease on the on side", "two behind the popping crease on the on side", {"mcc_laws": "two behind the popping crease on the on side", "icc_playing_conditions": "two behind the popping crease on the on side"})
c.check("a breach is a no ball, called by the striker's end umpire", "no ball", {"mcc_laws": "no ball", "icc_playing_conditions": "no ball"})
c.check("positions are neither fixed nor precisely defined (captain's choice; left-handers reverse the sides)", "not fixed", {W: "not fixed", SP: "not fixed"})


def S(vo, sc, **kw): return dict({"vo": vo, "scene": sc}, **kw)
def plate(vo, **sc): return S(vo, dict({"type": "plate"}, **sc))
def page(vo, **sc): return S(vo, dict({"type": "plate_page"}, **sc))
def F(p, label=None, **kw):
    d = {"p": p, "fig": None}
    if label: d["label"] = label
    d.update(kw); return d

ALL = [F("keeper"), F("slip"), F("gully"), F("point", "point", side=1), F("cover", "cover", side=1), F("mid-off", "mid-off", side=1), F("mid-on", "mid-on", side=-1), F("midwicket"), F("square leg", "square leg", side=-1), F("fine leg", "fine leg", side=-1), F("third man", "third man", hl=True, side=-1)]
short = [
 plate("Silly mid-off. Deep backward square leg. Third man. Cricket's fielding names sound like nonsense. They are not. They are a code, and once you can read it, you can read any field.",
       plate="I", title="READING THE FIELD", sub="the names are a code", figures=ALL, legend=False, stamp=["DID YOU", "KNOW?"], stamp_at=.75),
 plate("The first word is an angle, seen from the batter. Point, cover and mid-off sit on the off side. Mid-on, mid-wicket and square leg sit on the leg side.",
       plate="II", title="Word one: the angle", sub="off side on the right, leg side on the left",
       figures=[F("point", "point", side=1, ldy=-26), F("cover", "cover", side=1), F("mid-off", "mid-off", side=1), F("mid-on", "mid-on", side=-1), F("midwicket", "mid-wicket", side=-1), F("square leg", "square leg", side=-1)],
       legend=False, note=["off side: point · cover · mid-off", "leg side: mid-on · mid-wicket · square leg"]),
 plate("The second word is the distance. Short means closer to the batter. Deep, or long, means farther. And silly means so close that it is dangerous, only a few metres from the bat.",
       plate="III", title="Word two: the distance", sub="short · deep · long · silly",
       figures=[F("short leg", "short leg", side=-1), F("deep square leg", "deep square leg", side=-1), F("cover", "cover", side=1), F("deep cover", "deep cover", side=1)],
       legend=False, note=["short = closer · deep or long = farther", "silly = dangerously close"]),
 plate("Square means level with the batter, across the pitch. Fine is the opposite: behind the batter, close to the line of the pitch. So fine leg is behind square on the leg side, and third man is its partner on the off side.",
       plate="IV", title="Square and fine", sub="across the pitch, or behind it",
       figures=[F("square leg", "square leg", side=-1), F("point", "point", side=1), F("fine leg", "fine leg", side=-1), F("third man", "third man", side=1, hl=True)],
       legend=False, note=["square = level with the batter", "fine = behind, near the line of the pitch"]),
 plate("Close to the keeper, slips are numbered outwards. First slip, second slip, third slip. Together, the slip cordon. The gully stands a little squarer, on the off side.",
       plate="V", title="The slip cordon", sub="numbered outwards from the keeper",
       figures=[dict(p="keeper", fig=1, name="Wicket-keeper", side=-1, dy=48), dict(p="slip", fig=2, name="First slip", side=1, dy=54), dict(p="2nd slip", fig=3, name="Second slip", side=1, dy=-40), dict(p="3rd slip", fig=4, name="Third slip", side=1, dy=-46), dict(p="gully", fig=5, name="Gully", side=1, dy=-34)],
       ),
 page("Here is the twist. Fielders cannot stand anywhere. Law twenty-eight point four says that when the bowler delivers, no more than two fielders, besides the keeper, may be behind the batting crease on the leg side. A third there, and the umpire calls no ball.",
      kicker="THE LAW", title="Law 28.4", body="At the instant of the bowler's delivery there shall not be more than two fielders, other than the wicket-keeper, behind the popping crease on the on side.", margin="A breach is a no ball.",
      figures=[F("keeper"), F("fine leg"), F("deep square leg"), F("leg slip", hl=True)], stamp=["LAW", "28.4"], stamp_angle=-9),
 page("Everything else is the captain's call. The names are loose labels, not fixed spots, and for a left-hander, every side flips.",
      kicker="THE CATCH", title="Not fixed", body="Positions are neither fixed nor precisely defined. The captain moves them for the bowler and the batter, and a left-hander reverses the sides.", margin="So a field is a plan, not a map.", figures=[F("point"), F("cover"), F("fine leg"), F("third man"), F("mid-on")], stamp=["CAPTAIN'S", "CALL"], stamp_angle=8),
 {"vo": "Now you can read any field. Next match, try naming every fielder before the commentator does. Subscribe to The Third Man on YouTube for more Did You Know.", "scene": {"type": "cta", "lines": [{"t": "WANT THE FULL"}, {"t": "STORY?", "c": "gold"}], "yt": {"label": "THE THIRD MAN", "handle": "@thethirdman_angle", "sub": "SUBSCRIBE · INSTAGRAM @thethirdman.angle", "bio": None}}},
]
SRC = ["Names and definitions, checked against two independent written sources: Wikipedia, 'Fielding (cricket)' https://en.wikipedia.org/wiki/Fielding_(cricket) (names as an angle word plus a distance word; silly, short, deep, long; square; slips numbered outwards from the wicket-keeper; positions 'neither fixed nor precisely defined') and 'Glossary of cricket terms' https://en.wikipedia.org/wiki/Glossary_of_cricket_terms (cover, fine, cordon); and SportPlan, 'Cricket Fielding Positions Explained' https://www.sportplan.net/drills/Cricket/guides/cricket-fielding-positions-explained.jsp (sides, square, slips, gully, third man, mirrored for left-handers).",
       "Law 28.4 (Limitation of on side fielders): MCC Laws of Cricket, 2017 Code (3rd edition 2022), Law 28 'The Fielder' https://www.lords.org/mcc/the-laws/the-fielder (also quoted by Wisden, https://www.wisden.com/series/australia-in-england-2024/cricket-news/england-concede-rare-bodyline-no-ball-for-illegal-leg-side-field-placings); ICC Men's Test Playing Conditions clause 28.4 https://www.icc-cricket.com/news/mens-test-match-clause-28-the-fielder and Men's ODI clause 28.4.2-28.4.3 (striker's end umpire calls no ball) https://icc-cricket.com/news/mens-odi-match-clause-28-the-fielder. The 'on side' is the leg side for the batter.",
       "MCC published a 2026 edition of the Laws, in force from October 2026 (https://www.lords.org/getmedia/72990a68-98cd-4c6e-89ac-a2dce54533ad/Ten-major-changes-to-Laws-for-2026-edition_5.pdf); its ten headline changes do not touch Law 28, but the full 2026 text was not read, so check the clause number against the current edition. Field plans are illustrative, for a right-handed batter (mirrored for a left-hander). Figures: make_dyk_fielding.py."]
DESC = ("Fielding positions explained: how to read any cricket field. Names are a code: an angle word (cover, mid-wicket, point, square leg) and a distance word (short, deep, long, silly). Slips are numbered outwards from the wicket-keeper. "
        "Then the twist: Law 28.4 says no more than two fielders, besides the wicket-keeper, may stand behind the batting crease on the leg side when the bowler delivers; a third is a no ball. Positions are loose labels, not fixed spots. Illustrative field plans for a right-handed batter.\n\n"
        "Sources: MCC Laws of Cricket (Law 28.4, 2017 Code, 3rd edition 2022), ICC Playing Conditions clause 28.4, Wikipedia (Fielding (cricket); Glossary of cricket terms), SportPlan's fielding positions guide.\n\n#FieldingPositions #CricketExplained #DidYouKnow #Shorts")
TAGS = ["fielding positions", "cricket fielding positions explained", "silly mid-off", "square leg", "slip cordon", "Law 28.4", "cricket rules", "cricket explained", "Did You Know", "The Third Man"]
spec = {"slug": "dyk_fielding_positions", "theme": "plate", "captions": "serif", "captions_long": False, "series": "didyouknow", "tag": "DID YOU KNOW?", "tagsub": "EP. 2 · FIELDING POSITIONS",
        "files": {"long": "x", "short": "x"},
        "thumb": {"kicker": "DID YOU KNOW? · EP. 2", "lines": [{"t": "READ ANY"}, {"t": "CRICKET FIELD", "c": "gold"}], "hero": "?", "herosize": 420},
        "sources": SRC, "venue": {"time": "dusk", "crowd": [[190, 235, 70], [240, 240, 240], [25, 100, 200], [20, 60, 140]], "boards": [[25, 100, 200], [190, 235, 70]]}, "short": short,
        "yt": {"short": {"title": "Fielding Positions Explained: How to Read Any Field | Did You Know Ep 2 #Shorts", "description": DESC, "tags": TAGS}}}
c.save(spec)
voice_lint.fix_spec(spec)
json.dump(spec, open("specs/dyk_fielding_positions.json", "w"), ensure_ascii=False, indent=1)
print("wrote spec,", sum(len(x["vo"].split()) for x in short), "words,", len(short), "scenes")
