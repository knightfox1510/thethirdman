"""Adds spec["reel"] to specs/myth_ep3_aaryavir.json: the ~2.5 minute vertical Instagram Reel cut of Episode 3 (Instagram stops recommending Reels over 3 minutes).
Same verified facts as the long video (see make_aaryavir.py); built with `python3 variants.py igreel specs/myth_ep3_aaryavir.json`. Re-run after make_aaryavir.py."""
import json
P = "specs/myth_ep3_aaryavir.json"; spec = json.load(open(P))
def stage(vo, panel, av, **kw): return {"vo": vo, "scene": dict({"type": "stage", "panel": dict(panel, at=.05), "avatars": av}, **kw)}
IND = lambda pose, x=.5, **k: dict(kit="IND", pose=pose, x=x, **k)
V = lambda l, r, kick: {"kind": "versus", "kicker": kick, "left": l, "right": r}
G = lambda v, l, c="gold": {"v": v, "l": l, "c": c}
reel = [
 stage("Three hundred and sixty-one runs in five innings. Player of the Tournament at the Under nineteen Asia Cup. आर्यवीर सहवाग is nineteen, the son of वीरेंद्र सहवाग. Is it like father, like son? We tested it.",
       dict(V(G("361", "Runs in 5 innings"), G("90.25", "Average"), "AARYAVIR SEHWAG · U19 ASIA CUP"), sep="&"), [IND("raise")], cam="push", fx=["vignette", "spot", "confetti"], fx_at=.3),
 stage("Five innings: seventy not out against Nepal. Twenty-two against Pakistan. A hundred and sixty against the UAE. Fifty-one in the semi-final, and fifty-eight in the final.",
       {"kind": "table", "kicker": "EVERY INNINGS · U19 ASIA CUP 2026", "rows": [["Nepal", "70*"], ["Pakistan", "22"], ["UAE", "160", "gold"], ["Afghanistan", "51"], ["Pakistan (final)", "58"]]},
       [IND("stance", .34, hit="drive", ghost=True)], view="side", cam="drift", stumps=[.2, .93], ball={"at": .5, "shot": "four"}, fx=["vignette", "flash", "speed"]),
 stage("The hundred against the UAE did not start like a सहवाग innings. Fourteen balls for his first run. Then his last sixty runs came off just thirty-seven balls.",
       {"kind": "bignum", "kicker": "VS UAE · 160 OFF 168", "label": "BALLS FOR HIS FIRST RUN", "value": 14, "count_dur": .7, "color": "gold"},
       [IND("stance", .34, hit="loft", ghost=True)], view="side", cam="pull", stumps=[.2, .93], ball={"at": .5, "shot": "six"}, fx=["vignette", "shake", "sparks"]),
 stage("Afterwards, he said: \"I told my dad I will get a big hundred. I have a legacy to live up to.\"",
       {"kind": "headline", "kicker": "AFTER THE 160", "lines": [{"t": "\"A LEGACY"}, {"t": "TO LIVE UP TO.\"", "c": "gold"}]}, [IND("helmet")], cam="push", fx=["vignette", "spot"]),
 stage("That legacy: thirty-eight international hundreds, including two Test triple centuries.",
       {"kind": "bignum", "kicker": "VIRENDER SEHWAG", "label": "INTERNATIONAL HUNDREDS", "value": 38, "count_dur": .7, "color": "gold"}, [IND("stand")], cam="wide", fx=["vignette", "spot"]),
 stage("Test one: turning fifties into hundreds. आर्यवीर turned one of his four into a hundred, twenty-five per cent. His father, in one-day internationals, twenty-eight. Almost the same.",
       V(G("25%", "Aaryavir"), G("28%", "Virender"), "FIFTIES MADE INTO HUNDREDS"), [IND("stance", .32, hit="cut", ghost=True)], view="side", cam="push", stumps=[.2, .93], ball={"at": .5, "shot": "four"}, fx=["vignette", "flash"]),
 stage("Test two: boundaries. Sixty-nine per cent of his runs came in fours and sixes. For his father, sixty-five. The same shape of innings.",
       V(G("69%", "Aaryavir"), G("65%", "Virender"), "RUNS IN FOURS AND SIXES"), [IND("pull", .32, hit="cut", ghost=True)], view="side", cam="drift", stumps=[.2, .93], ball={"at": .5, "shot": "four"}, fx=["vignette", "shake"]),
 stage("Test three: the start. In our archive of his father's one-day innings, the median wait for a first run was two balls. आर्यवीर's, across five innings, also two.",
       V(G("2", "Aaryavir"), G("2", "Virender"), "BALLS BEFORE THE FIRST RUN"), [IND("stance")], cam="wide", fx=["vignette"]),
 stage("Test four: pace. Here, the son is different. A strike rate of ninety-six, against his father's hundred and four. He is slower, and he lets more balls go by.",
       V(G("96", "Aaryavir"), G("104", "Virender", "red"), "STRIKE RATE"), [IND("defend", .34)], view="side", cam="push", stumps=[.2, .93], fx=["vignette"]),
 stage("There was one quiet game. Against Pakistan in the group stage, twenty-two off forty balls. Six days later, in the final, fifty-eight off sixty-one, with nine fours.",
       V(G("55", "Group stage SR", "red"), G("95", "Final SR"), "PAKISTAN, TWICE · STRIKE RATE"), [IND("dejected", .3), IND("drive", .74)], cam="drift", fx=["vignette"]),
 stage("So, is आर्यवीर सहवाग just like his father? Our verdict: half busted. The appetite is the same. The pace is not. He is slower, and more patient, and in a final, that may be exactly what India needed.",
       {"kind": "verdict", "verdict": "half", "at": .45}, [IND("arms_wide")], cam="wide", fx=["vignette", "spot", "confetti"], fx_at=.6),
]
spec["reel"] = reel
json.dump(spec, open(P, "w"), ensure_ascii=False, indent=1)
print("reel:", len(reel), "scenes,", sum(len(x["vo"].split()) for x in reel), "words (+ CTA)")
