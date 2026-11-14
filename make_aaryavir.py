"""Builds specs/myth_ep3_aaryavir.json: "Aaryavir Sehwag: Like Father, Like Son?" (Myth or Data? Ep. 3; long + Short).
Aaryavir's tournament numbers come from the Cricbuzz commentary snapshots of his five innings (data/cricbuzz/u19_*.json; they reproduce BCCI's
Player-of-the-Tournament figures exactly: 361 runs, average 90.25, one hundred and three fifties) and the Cricinfo final capture.
Virender Sehwag's career figures are from ESPNcricinfo's player profile / Wikipedia (checked 14 Nov 2026); the style comparison uses Cricsheet
(165 of his ODI innings, 2002-2013, an archive sample).
    CS_DIR=/path/to/odis_json python3 make_aaryavir.py"""
import glob, json, os, statistics, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voice_lint, variants

CS = os.environ.get("CS_DIR", "/tmp/claude-0/cs_odi_dl/json")

# ---------------------------------------------------------------- Aaryavir: five innings (Cricbuzz commentary snapshots)
FILES = [("Nepal", "u19_nep"), ("Pakistan", "u19_grp_pak"), ("UAE", "u19_uae"), ("Afghanistan", "u19_semi_afg"), ("Pakistan (final)", "u19_final")]
inn = []
for name, f in FILES:
    cb = json.load(open(f"data/cricbuzz/{f}.json", encoding="utf-8"))
    seq, seen = [], set()
    for c in sorted((c for c in cb["comments"] if c.get("batsmanStriker", {}).get("batName") == "Aaryavir Sehwag" and c.get("ballNbr")),
                    key=lambda c: (c["inningsId"], c["batsmanStriker"]["batBalls"], c["batsmanStriker"]["batRuns"])):
        b = c["batsmanStriker"]; k = (b["batBalls"], b["batRuns"])
        if k not in seen: seen.add(k); seq.append((b["batBalls"], b["batRuns"], b.get("batFours", 0), b.get("batSixes", 0), b.get("batDots", 0)))
    fin = max(seq); first = next(x[0] for x in seq if x[1] > 0)
    fifty = next((x[0] for x in seq if x[1] >= 50), None); hundred = next((x[0] for x in seq if x[1] >= 100), None)
    out = any(c.get("event") and "WICKET" in c["event"] and " to Aaryavir Sehwag" in c["commText"].split("!!")[0] for c in cb["comments"])
    inn.append(dict(name=name, runs=fin[1], balls=fin[0], f=fin[2], s=fin[3], dots=fin[4], first=first, fifty=fifty, hundred=hundred, out=out))
assert [(i["runs"], i["balls"], i["f"], i["s"], i["out"]) for i in inn] == [(70, 52, 7, 4, False), (22, 40, 1, 1, True), (160, 168, 17, 7, True), (51, 57, 4, 4, True), (58, 61, 9, 0, True)]
R, B = sum(i["runs"] for i in inn), sum(i["balls"] for i in inn); F, S6 = sum(i["f"] for i in inn), sum(i["s"] for i in inn); D = sum(i["dots"] for i in inn)
OUTS = sum(i["out"] for i in inn)
assert (R, B, F, S6, D, OUTS) == (361, 378, 38, 16, 218, 4) and round(R / OUTS, 2) == 90.25                      # = BCCI's 361 runs, average 90.25
assert sum(1 for i in inn if i["runs"] >= 100) == 1 and sum(1 for i in inn if 50 <= i["runs"] < 100) == 3
SR, DOTS, BND = round(100 * R / B), round(100 * D / B), round(100 * (F * 4 + S6 * 6) / R)
assert (SR, DOTS, BND) == (96, 58, 69), (SR, DOTS, BND)
firsts = [i["first"] for i in inn]; assert firsts == [1, 1, 14, 4, 2] and statistics.median(firsts) == 2
uae = inn[2]; assert (uae["fifty"], uae["hundred"]) == (69, 131) and uae["runs"] - 100 == 60 and uae["balls"] - 131 == 37
assert [i["fifty"] for i in inn] == [34, None, 69, 56, 51]
assert (inn[1]["runs"], inn[1]["balls"], inn[1]["dots"], inn[4]["runs"], inn[4]["balls"], inn[4]["dots"]) == (22, 40, 27, 58, 61, 32)
assert (round(100 * 22 / 40), round(100 * 58 / 61), round(100 * 27 / 40), round(100 * 32 / 61)) == (55, 95, 68, 52)
# the final, from the Cricinfo capture: 58 off 61, nine fours, shared a 95-run opening stand
sys.path.insert(0, "analysis")
import u19_final as U
a = U.I[U.I.batter == "Aaryavir Sehwag"]; assert (int(a.bat_runs.sum()), int(a.faced.sum()), int(a.four.sum())) == (58, 61, 9)
assert int(U.I[U.I.overs <= 17.4].runs.sum()) == 95 and U.I[U.I.wicket].iloc[0].batter == "Aaryavir Sehwag"

# ---------------------------------------------------------------- Virender Sehwag
# career figures (ESPNcricinfo profile / Wikipedia): ODIs 251 matches, 8273 runs, 15 hundreds, 38 fifties, SR 104.33, 1132 fours, 136 sixes; Tests 8586 runs, 23 hundreds, 32 fifties, HS 319
V_ODI = dict(runs=8273, h=15, f50=38, sr=104.33, fours=1132, sixes=136); V_TEST = dict(runs=8586, h=23, f50=32, sr=82.23, hs=319)
assert V_ODI["h"] + V_TEST["h"] == 38
v_bnd = round(100 * (V_ODI["fours"] * 4 + V_ODI["sixes"] * 6) / V_ODI["runs"]); v_conv = round(100 * V_ODI["h"] / (V_ODI["h"] + V_ODI["f50"]))
assert (v_bnd, v_conv) == (65, 28)
# Cricsheet sample: 165 of his ODI innings, 2002-2013
runs = balls = dots = fours = sixes = 0; fr = []; n = 0
for f in glob.glob(f"{CS}/*.json"):
    m = json.load(open(f)); i = m["info"]
    if i.get("gender") != "male" or i.get("match_type") != "ODI": continue
    nm = next((p for t in i["players"].values() for p in t if p == "V Sehwag"), None)
    if not nm: continue
    for x in m["innings"]:
        if x.get("super_over"): continue
        b_ = r_ = d_ = f_ = s_ = 0; first = None
        for ov in x["overs"]:
            for dl in ov["deliveries"]:
                if dl["batter"] != nm: continue
                r = dl["runs"]["batter"]
                if not dl.get("extras", {}).get("wides"):
                    b_ += 1; d_ += r == 0
                    if first is None and r > 0: first = b_
                r_ += r; f_ += r == 4; s_ += r == 6
        if b_: n += 1; runs += r_; balls += b_; dots += d_; fours += f_; sixes += s_; fr.append(first) if first else None
assert (n, runs, balls) == (165, 5763, 5442), (n, runs, balls)
a_sr, a_dots, a_bnd, a_first = round(100 * runs / balls), round(100 * dots / balls), round(100 * (fours * 4 + sixes * 6) / runs), statistics.median(fr)
print("archive", a_sr, a_dots, a_bnd, a_first, fours, sixes)
assert (a_sr, a_dots, a_bnd, a_first) == (106, 53, 65, 2)
print("all facts asserted: tournament", R, B, SR, DOTS, BND, "| father archive", a_sr, a_dots, a_bnd, a_first)

# ---------------------------------------------------------------- scenes
def S(vo, sc, **kw): return dict({"vo": vo, "scene": sc}, **kw)
def stage(vo, panel, av, **kw): return S(vo, dict({"type": "stage", "panel": dict(panel, at=.05), "avatars": av}, **kw))
def tok(t, nm, kit=None): return {"t": t, "kit": kit or t, "name": nm}
rows = [{"label": f"{i['name']}", "v": i["runs"], "text": f"{i['runs']}{'' if i['out'] else '*'} ({i['balls']})", **({"hl": True} if i["runs"] == 160 else {})} for i in inn]

long = [
 S("Three hundred and sixty-one runs in five innings. An average of ninety. And the Player of the Tournament award at the Under nineteen Asia Cup. Aaryavir Sehwag is nineteen years old, and he is the son of India's former opener, Virender Sehwag. So the question is: is it like father, like son?",
   {"type": "lab_big", "kicker": "U19 ASIA CUP · PLAYER OF THE TOURNAMENT", "title": "Aaryavir Sehwag.", "value": 361, "label": "runs in five innings · average 90.25", "color": "red"}),
 S("This is Myth or Data. The claim: Aaryavir Sehwag is just like his father. We'll test it against Virender Sehwag's numbers, one trait at a time.",
   {"type": "lab_title", "kicker": "MYTH OR DATA? · EP. 3", "lines": ["Like father,", "[like son?]"], "teaser": "Aaryavir Sehwag · U19 Asia Cup 2026"}, chapter="The claim"),
 S("First, the tournament. Seventy not out off fifty-two against Nepal. Twenty-two against Pakistan in the group stage. A hundred and sixty against the UAE. Fifty-one in the semi-final. And fifty-eight in the final. Four dismissals, three fifties and one hundred. That is three sixty-one runs, at an average of ninety and a quarter.",
   {"type": "lab_dots", "kicker": "AARYAVIR SEHWAG · EVERY INNINGS · U19 ASIA CUP 2026", "title": "Five innings. One hundred.", "domain": [0, 170], "ticks": [0, 80, 160], "tick_labels": False, "rows": rows}, chapter="The tournament"),
 S("The hundred came against the UAE, and it did not start like a Sehwag innings. He took fourteen balls to score his first run. Fifty took sixty-nine balls. The hundred, a hundred and thirty-one. Then he hit his last sixty runs off just thirty-seven balls, finishing on a hundred and sixty with seventeen fours and seven sixes.",
   {"type": "lab_big", "kicker": "VS UAE · 160 OFF 168", "title": "Fourteen balls for the first run.", "value": 160, "label": "50 off 69 balls · 100 off 131 · last 60 off 37", "color": "red", "word": "fourteen"}),
 S("Afterwards, he said he had made a promise. In his words: \"I told my dad I will get a big hundred. I have a legacy to live up to, as he only likes big hundreds.\"",
   {"type": "lab_big_text", "kicker": "AARYAVIR SEHWAG · AFTER THE 160", "lines": ["\"I have a legacy", "[to live up to.]\""]}),
 S("Big scores are not new for him. In November twenty twenty-four, in the Cooch Behar Trophy, he made two hundred and ninety-seven. Last month, in the Vinoo Mankad Trophy, one hundred and seventy-three off a hundred and forty-three balls. And then, in Oman, a hundred and sixty. Each of them is a Sehwag-sized innings.",
   {"type": "lab_dots", "kicker": "AARYAVIR SEHWAG · BIG SCORES", "title": "The big-score habit.", "domain": [0, 300], "ticks": [0, 150, 300], "tick_labels": False, "rows": [
       {"label": "Cooch Behar Trophy · Nov 2024", "v": 297, "text": "297", "hl": True, "word": "ninety-seven"}, {"label": "Vinoo Mankad Trophy · Oct 2026", "v": 173, "text": "173 (143)"}, {"label": "U19 Asia Cup v UAE · Nov 2026", "v": 160, "text": "160 (168)"}]}),
 S("What is that legacy? Virender Sehwag scored thirty-eight international hundreds: twenty-three in Tests and fifteen in one-day internationals. Two of them were Test triple centuries, with a highest of three nineteen. Eight thousand, five hundred and eighty-six Test runs at a strike rate of eighty-two, and eight thousand, two hundred and seventy-three ODI runs at a hundred and four.",
   {"type": "lab_big", "kicker": "VIRENDER SEHWAG · INTERNATIONAL CRICKET", "title": "The legacy.", "value": 38, "suffix": " HUNDREDS", "label": "23 in Tests, 15 in ODIs · two Test triple centuries", "color": "red"}, chapter="The legacy"),
 S("Test one: turning fifties into hundreds. Aaryavir made four scores of fifty or more in the tournament, and turned one into a hundred. That is twenty-five per cent. His father, in one-day internationals, turned twenty-eight per cent: fifteen hundreds from fifty-three scores of fifty or more. Almost the same.",
   {"type": "lab_compare", "kicker": "TEST 1 · CONVERTING FIFTIES", "title": "Almost the same.", "a": tok("IND", "AARYAVIR · U19 ASIA CUP"), "b": tok("IND", "VIRENDER · ODIs"), "rows": [
       ["Scores of 50 or more", "4", "53", "level"], ["Hundreds", "1", "15", "level"], ["Share made into hundreds", "25%", "28%", "level"]]}, chapter="The tests"),
 S("Test two: boundaries. Sixty-nine per cent of Aaryavir's tournament runs came in fours and sixes: thirty-eight fours and sixteen sixes. For his father in ODIs, it was sixty-five per cent. Same shape of innings: most of the runs in boundaries.",
   {"type": "lab_compare", "kicker": "TEST 2 · RUNS IN BOUNDARIES", "title": "The same shape.", "a": tok("IND", "AARYAVIR · U19 ASIA CUP"), "b": tok("IND", "VIRENDER · ODIs"), "rows": [
       ["Runs in fours and sixes", "69%", "65%", "level"], ["Fours", "38", "1,132", "level"], ["Sixes", "16", "136", "level"]]}),
 S("Test three: the start. In our archive of a hundred and sixty-five of his father's one-day innings, the median wait for his first run was two balls. Aaryavir's median, across five innings, was also two balls. Four of the five innings began within four balls. The fourteen-ball start was the exception, not the rule.",
   {"type": "lab_dots", "kicker": "BALLS FACED BEFORE THE FIRST RUN", "title": "A father's start.", "domain": [0, 15], "ticks": [0, 5, 10, 15], "rows": [
       {"label": "Nepal", "v": 1, "text": "1"}, {"label": "Pakistan", "v": 1, "text": "1"}, {"label": "UAE", "v": 14, "text": "14", "hl": True, "word": "fourteen"},
       {"label": "Afghanistan", "v": 4, "text": "4"}, {"label": "Pakistan (final)", "v": 2, "text": "2"}, {"label": "Virender, median", "v": 2, "text": "2 (archive)", "hl": True}]}),
 S("Test four: pace. Here, the son is different. Aaryavir's strike rate in the tournament was ninety-six. His father's in ODIs was a hundred and four. And Aaryavir faced a dot ball fifty-eight times in every hundred, against fifty-three in our archive of his father's innings. He is slower, and he lets more balls go by.",
   {"type": "lab_compare", "kicker": "TEST 3 · PACE", "title": "Here, he is different.", "a": tok("IND", "AARYAVIR · U19 ASIA CUP"), "b": tok("IND", "VIRENDER · ODIs"), "rows": [
       ["Strike rate", "96", "104", "b"], ["Dot balls per hundred", "58", "53", "b"]]}),
 S("There was one quiet game. Against Pakistan in the group stage, he made twenty-two off forty balls, and was caught at deep mid-wicket. Pakistan won by three wickets. Six days later, against the same side in the final, he made fifty-eight off sixty-one, with nine fours. His strike rate went from fifty-five to ninety-five, and his dot balls fell from sixty-eight per cent to fifty-two.",
   {"type": "lab_compare", "kicker": "AARYAVIR SEHWAG · PAKISTAN, TWICE", "title": "Learning on the job.", "a": tok("IND", "GROUP · 8 NOV"), "b": tok("IND", "FINAL · 14 NOV"), "rows": [
       ["Runs", "22", "58", "b"], ["Balls", "40", "61", "level"], ["Strike rate", "55", "95", "b"], ["Dot balls", "68%", "52%", "b"]]}),
 S("In the final, Aaryavir played another role. He and Lakshya Raichandani put on ninety-five for the first wicket, and Sehwag made fifty-eight off sixty-one balls, with nine fours. Not a blitz. A platform. India chased three hundred and thirty-eight and won by one wicket.",
   {"type": "lab_big", "kicker": "THE FINAL · AARYAVIR SEHWAG", "title": "A platform, not a blitz.", "value": 95, "label": "for the first wicket: Sehwag 58 off 61, Raichandani 80", "color": "red", "word": "ninety-five"}, chapter="The final"),
 S("So, is Aaryavir Sehwag just like his father? Our verdict: half busted. The appetite is the same: boundaries, big hundreds, and a fast first run. But the pace is not. He is slower, and more patient, and for a nineteen-year-old in a final, that may be exactly what India needed.",
   {"type": "lab_big_text", "kicker": "THE VERDICT", "lines": ["Same appetite.", "[Different pace.]"]}, chapter="The verdict"),
 S("Will Aaryavir Sehwag play for India like his father did? Tell us in the comments, and follow for more Myth or Data.",
   {"type": "cta", "lines": [{"t": "THE NEXT SEHWAG?"}, {"t": "MYTH OR DATA?", "c": "gold"}], "pill": "SUBSCRIBE FOR MORE"}),
]

VEN = {"time": "day", "crowd": [[25, 100, 200], [240, 240, 240], [250, 150, 30], [20, 60, 140]], "boards": [[25, 100, 200], [250, 150, 30]]}
IN = lambda pose, **k: dict(kit="IND", pose=pose, **k)
short = [
 stage("Three hundred and sixty-one runs. An average of ninety. Player of the Tournament at the Under nineteen Asia Cup. Aaryavir Sehwag.",
       {"kind": "versus", "at": 0.0, "kicker": "AARYAVIR SEHWAG · U19 ASIA CUP", "left": {"v": "361", "l": "Runs in 5 innings", "c": "gold"}, "right": {"v": "90.25", "l": "Average", "c": "gold"}},
       [IN("raise", x=.5)], cam="push", fx=["vignette", "spot", "confetti"], fx_at=.3),
 stage("He is nineteen. And his father is Virender Sehwag: thirty-eight international hundreds, and two Test triple centuries.",
       {"kind": "bignum", "kicker": "VIRENDER SEHWAG", "label": "INTERNATIONAL HUNDREDS", "value": 38, "count_dur": .7, "color": "gold"},
       [IN("stance", x=.34, hit="loft", ghost=True)], view="side", cam="pull", stumps=[.2, .93], ball={"at": .5, "shot": "six"}, fx=["vignette", "sparks"]),
 stage("After his hundred and sixty, he said: \"I have a legacy to live up to.\" So is it like father, like son? We checked.",
       {"kind": "headline", "kicker": "AFTER THE 160", "lines": [{"t": "\"A LEGACY"}, {"t": "TO LIVE UP TO.\"", "c": "gold"}]},
       [IN("helmet", x=.5)], cam="push", fx=["vignette", "spot"]),
 stage("Test one: fifties into hundreds. He converted twenty-five per cent. His father, in ODIs, twenty-eight.",
       {"kind": "versus", "kicker": "FIFTIES MADE INTO HUNDREDS", "left": {"v": "25%", "l": "Aaryavir", "c": "gold"}, "right": {"v": "28%", "l": "Virender", "c": "gold"}},
       [IN("drive", x=.32, hit="drive", ghost=True)], view="side", cam="drift", stumps=[.2, .93], ball={"at": .5, "shot": "four"}, fx=["vignette", "flash", "speed"]),
 stage("Test two: boundaries. Sixty-nine per cent of his runs, against sixty-five for his father.",
       {"kind": "versus", "kicker": "RUNS IN FOURS AND SIXES", "left": {"v": "69%", "l": "Aaryavir", "c": "gold"}, "right": {"v": "65%", "l": "Virender", "c": "gold"}},
       [IN("pull", x=.32, hit="cut", ghost=True)], view="side", cam="push", stumps=[.2, .93], ball={"at": .5, "shot": "four"}, fx=["vignette", "shake"]),
 stage("Test three: the start. His father's median wait for a first run: two balls. Aaryavir's: also two.",
       {"kind": "versus", "kicker": "BALLS BEFORE THE FIRST RUN", "left": {"v": "2", "l": "Aaryavir", "c": "gold"}, "right": {"v": "2", "l": "Virender", "c": "gold"}},
       [IN("stance", x=.5)], cam="wide", fx=["vignette"]),
 stage("But the pace is different. A strike rate of ninety-six, against his father's hundred and four.",
       {"kind": "versus", "kicker": "STRIKE RATE", "left": {"v": "96", "l": "Aaryavir", "c": "gold"}, "right": {"v": "104", "l": "Virender", "c": "red"}},
       [IN("defend", x=.34)], view="side", cam="push", stumps=[.2, .93], fx=["vignette"]),
 stage("Same appetite. Different pace. Our verdict: half busted.",
       {"kind": "verdict", "verdict": "half", "at": .55}, [IN("arms_wide", x=.5)], cam="wide", fx=["vignette", "spot", "confetti"], fx_at=.5),
 dict(variants.YT_CTA),
]

SRC = ["Aaryavir Sehwag's five innings: the Cricbuzz commentary captures of the Nepal (4th match), Pakistan (8th match), UAE (11th match) and Afghanistan (semi-final) games, and the final (Cricbuzz 175720 + Cricinfo 1558444). "
       "His totals (361 runs, average 90.25, one hundred, three fifties) reproduce the Player of the Tournament figures in BCCI's Instagram post.",
       "Quote: Aaryavir Sehwag to the media after his 160 vs UAE, as reported by Outlook India: https://www.outlookindia.com/sports/cricket/india-vs-uae-u-19-asia-cup-2026-aaryavir-sehwag-promise-father-virender",
       "Earlier big scores (press reports): 297 in the Cooch Behar Trophy https://cricket.com/news/virender-sehwags-son-aaryavir-smashes-297-in-cooch-behar-trophy-11222024-1732257974695 ; 173 off 143 in the Vinoo Mankad Trophy https://www.bjsports.live/latest-news-en/aaryavir-sehwag-smashes-173-off-143-to-lead-delhi-u19-in-vinoo-mankad-trophy ; 160 off 168 vs UAE https://wisden.com/cricket-news/son-of-india-legend-aaryavir-sehwag-smashes-160-in-168-balls-for-india-u19",
       "Virender Sehwag's career figures: ESPNcricinfo player profile and Wikipedia (Tests: 8,586 runs, 23 hundreds, 32 fifties, highest 319; ODIs: 251 matches, 8,273 runs, 15 hundreds, 38 fifties, strike rate 104.33, 1,132 fours, 136 sixes). Checked 14 Nov 2026.",
       "Style comparison for Virender Sehwag: Cricsheet ball-by-ball archive (cricsheet.org, ODC-BY), 165 of his ODI innings 2002-2013 (a sample: coverage is partial), balls faced exclude wides. The two players' figures come from different levels of cricket (Under-19 against senior internationals), so they show style, not quality.",
       "All figures computed in make_aaryavir.py. Graphics are original illustrations: no photographs or likeness of any player."]
TAGS = ["Aaryavir Sehwag", "Virender Sehwag", "U19 Asia Cup 2026", "Aaryavir Sehwag 160", "India U19", "like father like son", "Sehwag legacy", "Myth or Data", "cricket analysis", "The Third Man"]
DESC_L = ("Aaryavir Sehwag, Player of the Tournament at the Under-19 Asia Cup 2026: 361 runs in five innings, average 90.25, one hundred and three fifties. Is he just like his father, Virender Sehwag? "
          "Myth or Data tests four traits: converting fifties into hundreds, boundary hitting, the start of the innings and the pace of scoring.\n\n"
          "Sources: Cricbuzz and ESPNcricinfo match pages (captured with our own tool); Virender Sehwag's career figures from ESPNcricinfo and Wikipedia; Cricsheet ball-by-ball archive (partial sample). "
          "The two players' numbers come from different levels of cricket, so they compare style, not quality. All graphics are original illustrations.\n\n#AaryavirSehwag #VirenderSehwag #U19AsiaCup #INDvPAK")
DESC_S = ("Is Aaryavir Sehwag the next Sehwag? Player of the Tournament at the Under-19 Asia Cup: 361 runs, average 90.25. Myth or Data tests him against his father Virender Sehwag. "
          "Data: Cricbuzz and ESPNcricinfo, Cricsheet; analysis by The Third Man. Full video on the channel.\n#AaryavirSehwag #VirenderSehwag #U19AsiaCup")
spec = {"slug": "myth_ep3_aaryavir", "theme": "stadium", "theme_long": "lab", "captions": "v2", "captions_long": False, "series": "myth", "tag": "MYTH OR DATA?", "tagsub": "EP. 3 · AARYAVIR SEHWAG",
        "files": {"long": "Aaryavir_Sehwag_Like_Father_Like_Son_Myth_or_Data", "short": "Aaryavir_Sehwag_Like_Father_Like_Son_Short_9x16"},
        "thumb": {"kicker": "MYTH OR DATA? · EP. 3", "lines": [{"t": "LIKE FATHER,"}, {"t": "LIKE SON?", "c": "gold"}], "hero": "361", "herosize": 420},
        "sources": SRC, "venue": VEN, "long": long, "short": short,
        "yt": {"long": {"title": "Aaryavir Sehwag: Like Father, Like Son? | Myth or Data", "description": DESC_L, "tags": TAGS},
               "short": {"title": "Is Aaryavir Sehwag the Next Sehwag? | U19 Asia Cup Player of the Tournament #Shorts", "description": DESC_S, "tags": TAGS}}}
voice_lint.fix_spec(spec)
json.dump(spec, open("specs/myth_ep3_aaryavir.json", "w"), ensure_ascii=False, indent=1)
print("wrote specs/myth_ep3_aaryavir.json: long", sum(len(x["vo"].split()) for x in long), "words,", len(long), "scenes; short", sum(len(x["vo"].split()) for x in short), "words")
