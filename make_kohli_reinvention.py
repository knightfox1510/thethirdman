"""Builds specs/myth_ep2_kohli_reinvention.json: Myth or Data? Ep. 2, "Is Kohli too slow for modern T20?" (a Short).
Every number spoken or shown is computed from the Sportmonks IPL ball-by-ball cache (data/ipl, 2013-2026) and asserted here.
Conventions (analysis/common.py): super overs excluded; strike rate = runs off the bat per 100 legal balls faced; phases powerplay = overs 1-6.
    SM_KEY=... python3 fetch_ipl.py     # once, to build the cache
    python3 make_kohli_reinvention.py"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "analysis"))
import common
import voice_lint

I = common.ipl()
K = I[I.batter == "Virat Kohli"].copy()
K["kind"] = K.bowl_kind.map(lambda v: "spin" if "spin" in str(v) else "pace")
sr = lambda d: 100 * d.bat_runs.sum() / d.legal.sum()
S = {y: K[K.season == y] for y in range(2013, 2027)}
SR = {y: sr(d) for y, d in S.items()}

# ---------------------------------------------------------------- facts (all asserted)
assert min(SR, key=SR.get) == 2022 and max(SR, key=SR.get) == 2026                     # worst and best IPL season for strike rate
assert round(SR[2022]) == 116 and round(SR[2026]) == 166 and round(SR[2026], 1) == 165.8
assert [round(SR[y]) for y in (2023, 2024, 2025)] == [140, 155, 145]
assert all(SR[2026] > SR[y] for y in SR if y != 2026) and all(SR[2022] < SR[y] for y in SR if y != 2022)
bpb = lambda d: d.legal.sum() / (d.four.sum() + d.six.sum())                           # balls faced per four or six
assert (round(bpb(S[2022]), 1), round(bpb(S[2026]), 1)) == (7.4, 4.2)
pp = lambda y: sr(S[y][S[y].phase == "powerplay"])
assert (round(pp(2022)), round(pp(2026))) == (117, 175)
dotp = lambda d: 100 * d["dot"].sum() / d.legal.sum()
assert (round(dotp(S[2022])), round(dotp(S[2026]))) == (38, 24)
lg = lambda y: sr(I[I.season == y])
gap22, gap26 = SR[2022] - lg(2022), SR[2026] - lg(2026)
assert (round(lg(2022)), round(lg(2026))) == (134, 156) and (round(gap22), round(gap26)) == (-18, 9)
sp, pa = sr(S[2026][S[2026].kind == "spin"]), sr(S[2026][S[2026].kind == "pace"])
assert (round(sp), round(pa)) == (130, 178)
assert S[2026].bat_runs.sum() == 675 and round(sr(S[2025]), 1) == 144.7             # matches RCB's official 675 runs; 2025 as in rcb_back_to_back
print("all facts asserted")

# ---------------------------------------------------------------- scenes
def stage(vo, panel, av, **kw): return {"vo": vo, "scene": dict({"type": "stage", "panel": dict(panel, at=.05), "avatars": av}, **kw)}
RCB = lambda pose, **k: dict(kit="RCB", number=18, pose=pose, **k)

short = [
 stage("Twenty twenty-two: a strike rate of one sixteen, the worst season of his IPL career. Twenty twenty-six: one sixty-six, the best. Is विराट कोहली too slow for modern T-twenty? We checked every ball.",
       {"kind": "versus", "at": 0.0, "kicker": "IS KOHLI TOO SLOW FOR T20?", "left": {"v": "116", "l": "IPL 2022 strike rate", "c": "red"}, "right": {"v": "166", "l": "IPL 2026 strike rate", "c": "gold"}},
       [RCB("dejected", x=.3), RCB("celebrate", x=.74)], cam="push"),
 stage("It wasn't one lucky year. One forty in twenty twenty-three. One fifty-five in twenty twenty-four. One forty-five in twenty twenty-five. And one sixty-six in twenty twenty-six.",
       {"kind": "table", "kicker": "STRIKE RATE BY SEASON", "rows": [["2022", "116", "red"], ["2023", "140"], ["2024", "155"], ["2025", "145"], ["2026", "166", "gold"]]},
       [RCB("stance", x=.4)], cam="drift"),
 stage("The change starts at the start. In the powerplay, he struck at one seventeen in twenty twenty-two. In twenty twenty-six, one seventy-five.",
       {"kind": "versus", "kicker": "POWERPLAY STRIKE RATE", "left": {"v": "117", "l": "2022", "c": "red"}, "right": {"v": "175", "l": "2026", "c": "gold"}},
       [RCB("drive", x=.34, hit="drive")], view="side", cam="push", stumps=[.18, .95], ball={"at": .55, "shot": "four"}),
 stage("In twenty twenty-two he hit a four or a six every seven balls. Now, every four.",
       {"kind": "versus", "kicker": "BALLS PER BOUNDARY", "left": {"v": "7.4", "l": "2022", "c": "red"}, "right": {"v": "4.2", "l": "2026", "c": "gold"}},
       [RCB("pull", x=.34, hit="pull")], view="side", cam="pull", stumps=[.18, .95], ball={"at": .55, "shot": "six"}),
 stage("Part of that is the whole league speeding up. So we measured him against it. In twenty twenty-two he was eighteen points below the league's strike rate. In twenty twenty-six, nine above.",
       {"kind": "versus", "kicker": "KOHLI VS THE LEAGUE'S STRIKE RATE", "left": {"v": "-18", "l": "2022", "c": "red"}, "right": {"v": "+9", "l": "2026", "c": "gold"}},
       [RCB("stand", x=.5)], cam="wide"),
 stage("One gap is left: spin. In twenty twenty-six he struck at one thirty against spin, and one seventy-eight against pace.",
       {"kind": "versus", "kicker": "2026 · BY BOWLER TYPE", "left": {"v": "178", "l": "vs pace", "c": "gold"}, "right": {"v": "130", "l": "vs spin", "c": "ink"}},
       [RCB("stance", x=.4)], cam="push"),
 stage("So is Kohli too slow for modern T-twenty? No. His slowest season came in twenty twenty-two. His fastest is the latest. Our verdict: busted.",
       {"kind": "verdict", "verdict": "busted", "at": .72}, [RCB("raise", x=.5)], cam="wide"),
 {"vo": "Which Kohli innings changed your mind? Tell us in the comments, and follow for episode three.",
  "scene": {"type": "cta", "lines": [{"t": "MYTH OR DATA?"}, {"t": "EPISODE 3 NEXT", "c": "gold"}], "pill": "FOLLOW FOR MORE"}},
]

SRC = ["Sportmonks ball-by-ball, IPL 2013-2026 (data/ipl cache). Virat Kohli's legal balls faced; super overs excluded; strike rate = runs off the bat per 100 balls; powerplay = overs 1-6; "
       "bowler type from Sportmonks bowling style. League strike rate = all batters' runs off the bat per 100 legal balls in the season. Figures: make_kohli_reinvention.py.",
       "Cross-check: Kohli's 2026 total (675 runs, strike rate about 165.8) matches RCB's own season review: https://royalchallengers.com/rcb-cricket-news/news/from-virat-kohli-to-tim-david-rcbs-top-five-batters-in-ipl-2026"]
DESC = ("Myth or Data? Episode 2. Is Virat Kohli too slow for modern T20? Every ball of his IPL career, 2013 to 2026: his strike rate went from 116 in 2022, his slowest season, "
        "to 166 in 2026, his fastest, measured against the league too. Data: Sportmonks ball-by-ball (our own analysis); 2026 total cross-checked with RCB's season review. "
        "Super overs excluded; strike rate is runs off the bat per 100 balls.")
TAGS = ["Virat Kohli", "Kohli IPL 2026", "RCB", "IPL strike rate", "cricket stats", "Myth or Data", "cricket shorts", "The Third Man"]
spec = {"slug": "myth_ep2_kohli_reinvention", "theme": "stadium", "captions": "v2", "tag": "MYTH OR DATA?", "tagsub": "EP. 2 · KOHLI'S REINVENTION",
        "files": {"long": "_unused", "short": "Myth_or_Data_Ep2_Kohli_Reinvention_9x16"},
        "thumb": {"kicker": "MYTH OR DATA? · EP. 2", "lines": [{"t": "IS KOHLI"}, {"t": "TOO SLOW?", "c": "gold"}], "hero": "165.8", "herosize": 300},
        "sources": SRC, "short": short,
        "venue": {"time": "night", "crowd": [[214, 30, 40], [20, 20, 20], [240, 240, 240], [212, 175, 55]], "boards": [[214, 30, 40], [20, 20, 20]]},
        "yt": {"short": {"title": "Is Kohli too slow for T20? His strike rate: 116 to 166 📊 #Shorts", "description": DESC, "tags": TAGS}}}
voice_lint.fix_spec(spec)
json.dump(spec, open("specs/myth_ep2_kohli_reinvention.json", "w"), ensure_ascii=False, indent=1)
print("wrote spec,", sum(len(x["vo"].split()) for x in short), "words")
