"""Adds spec["full"] to specs/myth_ep3_aaryavir.json: the full-detail vertical version of Episode 3 (every scene and the whole narration of the long video,
laid out for 9:16 as stadium-stage scenes with the data panels). Build: `python3 variants.py igfull specs/myth_ep3_aaryavir.json`. Re-run after make_aaryavir.py."""
import json
P = "specs/myth_ep3_aaryavir.json"; spec = json.load(open(P)); L = [x["vo"] for x in spec["long"]]
def stage(i, panel, av, **kw): return {"vo": L[i], "scene": dict({"type": "stage", "panel": dict(panel, at=.05), "avatars": av}, **kw)}
IND = lambda pose, x=.5, **k: dict(kit="IND", pose=pose, x=x, **k)
G = lambda v, l, c="gold": {"v": v, "l": l, "c": c}
T = lambda kick, rows: {"kind": "table", "kicker": kick, "rows": rows}
SIDE = dict(view="side", stumps=[.2, .93])
full = [
 stage(0, {"kind": "versus", "sep": "&", "kicker": "AARYAVIR SEHWAG · U19 ASIA CUP", "left": G("361", "Runs in 5 innings"), "right": G("90.25", "Average")}, [IND("raise")], cam="push", fx=["vignette", "spot", "confetti"], fx_at=.3),
 stage(1, {"kind": "headline", "kicker": "MYTH OR DATA? · EP. 3", "lines": [{"t": "LIKE FATHER,"}, {"t": "LIKE SON?", "c": "gold"}]}, [IND("stand")], cam="wide", fx=["vignette", "spot"]),
 stage(2, T("EVERY INNINGS · U19 ASIA CUP 2026", [["Nepal", "70* (52)"], ["Pakistan", "22 (40)"], ["UAE", "160 (168)", "gold"], ["Afghanistan", "51 (57)"], ["Pakistan (final)", "58 (61)"]]),
       [IND("stance", .34, hit="drive", ghost=True)], cam="drift", ball={"at": .5, "shot": "four"}, fx=["vignette", "flash", "speed"], **SIDE),
 stage(3, {"kind": "bignum", "kicker": "VS UAE · 160 OFF 168", "label": "BALLS FOR HIS FIRST RUN", "value": 14, "count_dur": .7, "color": "gold"},
       [IND("stance", .34, hit="loft", ghost=True)], cam="pull", ball={"at": .5, "shot": "six"}, fx=["vignette", "shake", "sparks"], **SIDE),
 stage(4, {"kind": "headline", "kicker": "AFTER THE 160", "lines": [{"t": "\"A LEGACY"}, {"t": "TO LIVE UP TO.\"", "c": "gold"}]}, [IND("helmet")], cam="push", fx=["vignette", "spot"]),
 stage(5, T("AARYAVIR SEHWAG · BIG SCORES", [["Cooch Behar Trophy · Nov 2024", "297", "gold"], ["Vinoo Mankad Trophy · Oct 2026", "173 (143)"], ["U19 Asia Cup v UAE · Nov 2026", "160 (168)"]]),
       [IND("pull", .34, hit="cut", ghost=True)], cam="drift", ball={"at": .5, "shot": "four"}, fx=["vignette", "shake"], **SIDE),
 stage(6, T("VIRENDER SEHWAG · 38 INTERNATIONAL HUNDREDS", [["Test hundreds", "23"], ["ODI hundreds", "15"], ["Test triple centuries", "2", "gold"], ["Highest Test score", "319"]]),
       [IND("stand")], cam="wide", fx=["vignette", "spot"]),
 stage(7, T("FIFTIES · AARYAVIR VS VIRENDER", [["Scores of 50 or more", "4 vs 53"], ["Hundreds", "1 vs 15"], ["Made into hundreds", "25% vs 28%", "gold"]]),
       [IND("drive", .32, hit="drive", ghost=True)], cam="push", ball={"at": .5, "shot": "four"}, fx=["vignette", "flash"], **SIDE),
 stage(8, T("BOUNDARIES · AARYAVIR VS VIRENDER", [["Runs in fours and sixes", "69% vs 65%", "gold"], ["Fours", "38 vs 1,132"], ["Sixes", "16 vs 136"]]),
       [IND("pull", .32, hit="cut", ghost=True)], cam="drift", ball={"at": .5, "shot": "four"}, fx=["vignette", "shake"], **SIDE),
 stage(9, T("TEST 3 · BALLS BEFORE THE FIRST RUN", [["Nepal", "1"], ["Pakistan", "1"], ["UAE", "14", "gold"], ["Afghanistan", "4"], ["Pakistan (final)", "2"], ["Virender, median (archive)", "2", "gold"]]),
       [IND("stance")], cam="wide", fx=["vignette"]),
 stage(10, T("PACE · AARYAVIR VS VIRENDER", [["Strike rate", "96 vs 104", "red"], ["Dot balls per hundred", "58 vs 53", "red"]]),
        [IND("defend", .34)], cam="push", fx=["vignette"], **SIDE),
 stage(11, T("PAKISTAN · GROUP VS FINAL", [["Runs", "22 vs 58"], ["Balls", "40 vs 61"], ["Strike rate", "55 vs 95", "gold"], ["Dot balls", "68% vs 52%", "gold"]]),
        [IND("dejected", .3), IND("drive", .74)], cam="drift", fx=["vignette"]),
 stage(12, {"kind": "bignum", "kicker": "THE FINAL · SEHWAG 58 OFF 61 · RAICHANDANI 80", "label": "FIRST-WICKET PARTNERSHIP", "value": 95, "count_dur": .8, "color": "gold"},
        [IND("celebrate")], cam="push", fx=["vignette", "spot", "confetti"], fx_at=.4),
 stage(13, {"kind": "verdict", "verdict": "half", "at": .55}, [IND("arms_wide")], cam="wide", fx=["vignette", "spot", "confetti"], fx_at=.6),
]
spec["full"] = full
json.dump(spec, open(P, "w"), ensure_ascii=False, indent=1)
print("full:", len(full), "scenes,", sum(len(x["vo"].split()) for x in full), "words (+ CTA)")
