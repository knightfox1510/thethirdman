"""Builds specs/gambhir_player_coach.json: "Gautam Gambhir: Player vs Coach" (Data Stories Ep. 11; long + Short).
Coach record = every men's international India played from 27 Jul 2024 (Gambhir's first match in charge) in the Cricsheet archive of Tests, ODIs and T20Is
(downloaded to CS_DIR/tests|odis|t20s; matches abandoned without a ball bowled are not in Cricsheet). Player numbers: career figures from Wikipedia/ESPNcricinfo (Test, ODI, T20I),
his strike rates from our archive (Cricsheet: 34 of 37 T20I innings, 134 ODI innings: a sample, labelled as such) and the Sportmonks IPL cache (2013-2017).
    CS_DIR=/tmp/claude-0/cs_new python3 make_gambhir.py"""
import glob, json, os, sys, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "analysis"))
import common, voice_lint

CS = os.environ.get("CS_DIR", "/tmp/claude-0/cs_new"); START = "2024-07-27"
REC, BAT = {}, {}
for fmt in ("tests", "odis", "t20s"):
    c = collections.Counter(); runs = balls = 0; first = None; pl = {"r": 0, "b": 0, "inn": 0}
    for p in sorted(glob.glob(f"{CS}/{fmt}/*.json")):
        m = json.load(open(p)); i = m["info"]
        if "India" not in i["teams"] or i.get("gender") != "male": continue
        gp = [x for t in i["players"].values() for x in t if x == "G Gambhir"]
        if gp:                                                                                     # Gambhir the player (archive sample)
            for inn in m["innings"]:
                if inn.get("super_over"): continue
                seen = False
                for ov in inn["overs"]:
                    for d in ov["deliveries"]:
                        if d["batter"] == "G Gambhir":
                            seen = True; pl["r"] += d["runs"]["batter"]; pl["b"] += "wides" not in d.get("extras", {})
                pl["inn"] += seen
        if i["dates"][0] < START: continue
        o = i.get("outcome", {})
        c["W" if o.get("winner") == "India" or o.get("eliminator") == "India" else "L" if ("winner" in o or "eliminator" in o) else "NR" if o.get("result") == "no result" else o.get("result", "?")] += 1
        first = first or i["dates"][0]
        for inn in m["innings"]:
            if inn["team"] != "India" or inn.get("super_over"): continue
            for ov in inn["overs"]:
                for d in ov["deliveries"]:
                    runs += d["runs"]["total"]; balls += ("wides" not in d.get("extras", {}) and "noballs" not in d.get("extras", {}))
    REC[fmt] = dict(c); BAT[fmt] = (runs, balls, pl)
tests, odis, t20 = REC["tests"], REC["odis"], REC["t20s"]
# ---------------------------------------------------------------- facts (all asserted)
assert (sum(tests.values()), tests["W"], tests["L"], tests["draw"]) == (21, 8, 10, 3)
assert (sum(odis.values()), odis["W"], odis["L"], odis["tie"]) == (26, 15, 10, 1)
assert (sum(t20.values()), t20["W"], t20["L"], t20["NR"], t20.get("tie", 0)) == (68, 48, 16, 4, 0), t20     # two ties were won in the super over
assert 21 + 26 + 68 == 115
assert (round(100 * 8 / 21, 1), round(100 * 15 / 26, 1), round(100 * 48 / 68, 1)) == (38.1, 57.7, 70.6)
assert round(100 * BAT["t20s"][0] / BAT["t20s"][1]) == 167 and round(100 * BAT["odis"][0] / BAT["odis"][1]) == 103
pt, po = BAT["t20s"][2], BAT["odis"][2]
assert (pt["inn"], pt["r"], round(100 * pt["r"] / pt["b"])) == (34, 918, 119)                                        # archive sample of his 37 T20I innings
assert round(100 * po["r"] / po["b"]) == 86 and po["inn"] == 134
I = common.ipl(); G = I[I.batter == "Gautam Gambhir"]
ipl = {}
for y in range(2013, 2018):
    L, d = I[I.season == y], G[G.season == y]
    ipl[y] = (round(100 * d.bat_runs.sum() / d.legal.sum()), round(100 * L.bat_runs.sum() / L.legal.sum()), int(d.bat_runs.sum()))
assert [(v[0], v[1]) for v in ipl.values()] == [(119, 121), (114, 129), (118, 132), (122, 131), (128, 133)], ipl
assert sum(v[2] for v in ipl.values()) == 2068 and all(a < b for a, b, _ in ipl.values())
gaps_exact = []
for y in range(2013, 2018):
    L, d = I[I.season == y], G[G.season == y]; gaps_exact.append(100 * L.bat_runs.sum() / L.legal.sum() - 100 * d.bat_runs.sum() / d.legal.sum())
assert round(max(gaps_exact)) == 15 and min(gaps_exact) > 0
# series results from the Tests list (checked against Wikipedia's account: NZ 0-3, England 2-2, wins v Bangladesh and West Indies, loss to South Africa; Australia 1-3 and Sri Lanka 1-0 from the same results)
print("all facts asserted", REC)

# ---------------------------------------------------------------- scenes
def S(vo, sc, **kw): return dict({"vo": vo, "scene": sc}, **kw)
def stage(vo, panel, av, **kw): return S(vo, dict({"type": "stage", "panel": dict(panel, at=.05), "avatars": av}, **kw))
IND = lambda pose, x=.5, **k: dict(kit="IND", pose=pose, x=x, **k)
G_ = lambda v, l, c="gold": {"v": v, "l": l, "c": c}
tok = lambda t, nm, kit=None: {"t": t, "kit": kit or t, "name": nm}
VEN = {"time": "night", "crowd": [[25, 100, 200], [240, 240, 240], [250, 150, 30], [20, 60, 140]], "boards": [[25, 100, 200], [250, 150, 30]]}

long = [
 S("Four ICC trophies. Two as a player: the two thousand seven T-twenty World Cup, and the twenty eleven World Cup. Two as India's head coach: the twenty twenty-five Champions Trophy, and the twenty twenty-six T-twenty World Cup. So who was better, गौतम गंभीर the player, or गौतम गंभीर the coach?",
   {"type": "lab_big", "kicker": "GAUTAM GAMBHIR · PLAYER VS COACH", "title": "Four ICC trophies.", "value": 4, "label": "two as a player, two as India's head coach", "color": "red"}),
 S("This is a Data Story. We will put the player's numbers next to the coach's results, one at a time, and see what each tells us.",
   {"type": "lab_title", "kicker": "DATA STORIES · EP. 11", "lines": ["Player", "[vs coach?]"], "teaser": "Gautam Gambhir · 2007 to 2026"}),
 S("The player first. He was a big-match batter. In the two thousand seven T-twenty World Cup final against Pakistan, seventy-five off fifty-four balls. In the twenty eleven World Cup final, ninety-seven off a hundred and twenty-two.",
   {"type": "lab_dots", "kicker": "GAUTAM GAMBHIR · THE PLAYER · WORLD CUP FINALS", "title": "Two finals, two big innings.", "domain": [0, 100], "ticks": [0, 50, 100], "tick_labels": False,
    "rows": [{"label": "2007 T20 World Cup final", "v": 75, "text": "75 (54)", "hl": True}, {"label": "2011 World Cup final", "v": 97, "text": "97 (122)", "hl": True}]}),
 S("Across his career, he was an opener of real quality. Fifty-eight Tests: four thousand, one hundred and fifty-four runs at forty-two, with nine hundreds. A hundred and forty-seven one-day internationals: five thousand, two hundred and thirty-eight runs at nearly forty, with eleven hundreds. In T-twenty internationals, thirty-seven matches at twenty-seven.",
   {"type": "lab_dots", "kicker": "GAUTAM GAMBHIR · THE PLAYER · CAREER BATTING AVERAGE", "title": "A Test and one-day opener.", "domain": [0, 50], "ticks": [0, 25, 50], "tick_labels": False,
    "rows": [{"label": "Tests · 58 matches · 9 hundreds", "v": 41.95, "text": "41.95", "hl": True}, {"label": "ODIs · 147 matches · 11 hundreds", "v": 39.68, "text": "39.68"}, {"label": "T20Is · 37 matches", "v": 27.41, "text": "27.41"}]}),
 S("In the IPL, he captained Kolkata Knight Riders to two titles, in twenty twelve and twenty fourteen.",
   {"type": "lab_big_text", "kicker": "GAUTAM GAMBHIR · THE PLAYER · IPL", "lines": ["Two IPL titles", "[as captain.]"]}),
 S("But his T-twenty batting was patient. In the IPL, from twenty thirteen to twenty seventeen, he scored two thousand and sixty-eight runs. And his strike rate was below the league's in every one of those five seasons, by as much as fifteen points.",
   {"type": "lab_dots", "kicker": "GAMBHIR'S IPL STRIKE RATE VS THE LEAGUE'S · SPORTMONKS", "title": "Below the league, every year.", "domain": [100, 140], "ticks": [100, 120, 140], "tick_labels": False,
    "rows": [{"label": f"{y} · league {v[1]}", "v": v[0], "text": f"{v[0]}"} for y, v in ipl.items()]}),
 S("In T-twenty internationals, in our archive of thirty-four of his thirty-seven innings, he struck at one nineteen. And in one-day internationals, at eighty-six. A patient opener, by modern standards.",
   {"type": "lab_big", "kicker": "THE PLAYER · T20I STRIKE RATE · OUR ARCHIVE", "title": "A patient opener.", "value": 119, "label": "34 of his 37 T20I innings, 918 runs · ODIs: 86", "color": "red"}),
 S("Now, the coach. In July twenty twenty-four, गौतम गंभीर became India's head coach. His first match in charge was a T-twenty international in Sri Lanka, at the end of July. Since then, in our archive, India have played a hundred and fifteen men's internationals under him.",
   {"type": "lab_big", "kicker": "THE COACH · SINCE JULY 2024", "title": "India under Gambhir.", "value": 115, "label": "men's internationals · 21 Tests, 26 ODIs, 68 T20Is", "color": "red"}),
 S("Here is the record. In Tests: eight wins, ten losses and three draws. In one-day internationals: fifteen wins, ten losses and a tie. In T-twenty internationals: forty-eight wins, sixteen losses and four no-results. That is a win rate of thirty-eight per cent in Tests, fifty-eight per cent in one-day cricket, and seventy-one per cent in T-twenty.",
   {"type": "lab_dots", "kicker": "INDIA UNDER GAMBHIR · WIN RATE BY FORMAT · SINCE 27 JULY 2024", "title": "Strong in white ball. Not in Tests.", "domain": [0, 100], "ticks": [0, 50, 100], "tick_labels": False,
    "rows": [{"label": "Tests · W8 L10 D3", "v": 38.1, "text": "38%"}, {"label": "ODIs · W15 L10 T1", "v": 57.7, "text": "58%"}, {"label": "T20Is · W48 L16 NR4", "v": 70.6, "text": "71%", "hl": True}]}),
 S("And the trophies came. The Champions Trophy in twenty twenty-five, unbeaten: five matches, five wins. The Asia Cup in twenty twenty-five, beating Pakistan in the final. And the twenty twenty-six T-twenty World Cup. As Kolkata Knight Riders' mentor, he had also won the IPL in twenty twenty-four.",
   {"type": "lab_big_text", "kicker": "THE COACH · TROPHIES", "lines": ["Champions Trophy. Asia Cup.", "[T20 World Cup.]"]}),
 S("But Tests are where it has hurt. Seven Test series under him. Three wins: Bangladesh, West Indies and Sri Lanka. One draw: two-all in England. And three defeats: New Zealand three-nil, Australia three-one, and South Africa two-nil.",
   {"type": "lab_dots", "kicker": "TEST SERIES UNDER GAMBHIR · INDIA'S MARGIN", "title": "Three wins, one draw, three defeats.", "domain": [-3, 3], "ticks": [-3, 0, 3], "tick_labels": False,
    "rows": [{"label": "Bangladesh · 2-0", "v": 2, "text": "+2"}, {"label": "New Zealand · 0-3", "v": -3, "text": "-3", "hl": True}, {"label": "Australia · 1-3", "v": -2, "text": "-2"}, {"label": "England · 2-2", "v": 0, "text": "0"},
             {"label": "West Indies · 2-0", "v": 2, "text": "+2"}, {"label": "South Africa · 0-2", "v": -2, "text": "-2"}, {"label": "Sri Lanka · 1-0", "v": 1, "text": "+1"}]}),
 S("Two of those defeats came at home: three-nil against New Zealand, and two-nil against South Africa.",
   {"type": "lab_big", "kicker": "TEST SERIES LOST AT HOME UNDER GAMBHIR", "title": "Two home defeats.", "value": 2, "label": "0-3 v New Zealand (2024) · 0-2 v South Africa (2025)", "color": "red"}),
 S("Now compare the styles. As a player, in our archive, his strike rate was one nineteen in T-twenty, and eighty-six in one-day cricket. India under him strike at one sixty-seven and one hundred and three. The patient opener now coaches a team that scores much faster than he ever did.",
   {"type": "lab_compare", "kicker": "STYLE · PLAYER VS COACH'S TEAM", "title": "Faster than he ever was.", "a": tok("IND", "GAMBHIR · AS A PLAYER", "IND"), "b": tok("IND", "INDIA · UNDER GAMBHIR", "IND"),
    "rows": [["T20 strike rate", "119", "167", "b"], ["ODI strike rate", "86", "103", "b"]]}),
 S("So, player or coach? As a player, he delivered in the biggest finals. As a coach, India's white-ball results are strong: three trophies, and a winning record in both limited-overs formats. But in Tests, eight wins from twenty-one is the weak spot. The player was patient. His team is not. And Test cricket is where that gap shows.",
   {"type": "lab_big_text", "kicker": "THE VERDICT", "lines": ["Trophies in white ball.", "[Tests still to solve.]"]}),
 S("Is गौतम गंभीर a better player or a better coach? Tell us in the comments, and follow for more Data Stories.",
   {"type": "cta", "lines": [{"t": "PLAYER OR COACH?"}, {"t": "DATA STORIES", "c": "gold"}], "pill": "SUBSCRIBE FOR MORE"}),
]

short = [
 stage("As a player, गौतम गंभीर struck at about one nineteen in T-twenty cricket. The India team he coaches strikes at one sixty-seven. Player or coach: who wins?",
       {"kind": "versus", "kicker": "GAMBHIR · T20 STRIKE RATE", "left": G_("119", "As a player", "ink"), "right": G_("167", "India, his team")}, [IND("stance")], cam="push", fx=["vignette", "spot"]),
 stage("As a player, he won two World Cup finals: seventy-five off fifty-four in two thousand seven, and ninety-seven in the twenty eleven final.",
       {"kind": "versus", "sep": "&", "kicker": "THE PLAYER · WORLD CUP FINALS", "left": G_("75", "2007 T20 final"), "right": G_("97", "2011 final")}, [IND("raise")], cam="wide", fx=["vignette", "spot", "confetti"], fx_at=.3),
 stage("As a coach, India won the Champions Trophy unbeaten, the Asia Cup, and the twenty twenty-six T-twenty World Cup.",
       {"kind": "table", "kicker": "THE COACH · TROPHIES", "rows": [["Champions Trophy 2025", "5 / 5", "gold"], ["Asia Cup 2025", "WON"], ["T20 World Cup 2026", "WON", "gold"]]}, [IND("celebrate")], cam="push", fx=["vignette", "confetti"], fx_at=.3),
 stage("In T-twenty, India have won forty-eight of sixty-eight. In one-day cricket, fifteen of twenty-six.",
       {"kind": "table", "kicker": "INDIA UNDER GAMBHIR · WIN RATE", "rows": [["T20Is · W48 of 68", "71%", "gold"], ["ODIs · W15 of 26", "58%"]]}, [IND("point")], cam="drift", fx=["vignette"]),
 stage("But in Tests: twenty-one matches, eight wins, ten losses. Including two home series defeats.",
       {"kind": "versus", "kicker": "TESTS UNDER GAMBHIR", "left": G_("8", "Wins"), "right": G_("10", "Losses", "red")}, [IND("dejected")], cam="pull", fx=["vignette"]),
 stage("So, trophies in white ball. Tests still to solve. The patient player now coaches a very fast team.",
       {"kind": "headline", "kicker": "PLAYER VS COACH", "lines": [{"t": "WHITE BALL: TROPHIES."}, {"t": "TESTS: TO SOLVE.", "c": "gold"}]}, [IND("arms_wide")], cam="wide", fx=["vignette", "spot"]),
 {"vo": "Want the full breakdown? Subscribe to The Third Man on YouTube.", "scene": {"type": "cta", "lines": [{"t": "WANT THE FULL"}, {"t": "BREAKDOWN?", "c": "gold"}], "yt": {"label": "THE THIRD MAN", "handle": "@thethirdman_angle", "sub": "SUBSCRIBE · INSTAGRAM @thethirdman.angle", "bio": None}}},
]

SRC = ["Coach record: every men's Test, ODI and T20I India played from 27 July 2024 (Gambhir's first match in charge) in the Cricsheet archive (cricsheet.org): 21 Tests, 26 ODIs, 68 T20Is. Matches abandoned without a ball bowled are not in the archive; super-over ties are counted as wins for the winner. Other reports quote slightly different totals for the same period; headline results were checked against Wikipedia's account of his tenure.",
       "Series results: Bangladesh 2-0, New Zealand 0-3, Australia 1-3, England 2-2, West Indies 2-0, South Africa 0-2, Sri Lanka 1-0 (Tests, from the same archive). Champions Trophy 2025: five wins from five; T20 World Cup 2026 and Asia Cup 2025 won (ICC / Wikipedia).",
       "Player career figures (Tests 58, ODIs 147, T20Is 37; averages 41.95, 39.68, 27.41; finals 75 off 54 in 2007 and 97 off 122 in 2011; two IPL titles as KKR captain, 2012 and 2014): https://en.wikipedia.org/wiki/Gautam_Gambhir",
       "Gambhir's strike rates (T20I 119 from 34 of 37 innings; ODI 86 from 134 innings) are from our Cricsheet archive, a sample, not career totals. IPL 2013-2017: Sportmonks ball-by-ball cache (runs off the bat per 100 legal balls; league = all batters that season; super overs excluded). India's strike rates under him are runs per 100 legal balls in the same archive. Figures: make_gambhir.py."]
DESC_L = ("India vs the player: Gautam Gambhir, player vs coach. As a player he scored 75 off 54 in the 2007 T20 World Cup final and 97 in the 2011 World Cup final. As India's head coach since July 2024: the Champions Trophy, the Asia Cup and the T20 World Cup, "
          "48 wins in 68 T20Is, and eight wins in 21 Tests. How the patient opener's career compares with the fast-scoring team he coaches. Data: Cricsheet archive, Sportmonks IPL ball-by-ball (our own analysis), career figures from Wikipedia.\n\n"
          "Chapters in the pinned comment.\n#GautamGambhir #TeamIndia #Cricket")
DESC_S = ("Gautam Gambhir, player vs coach: 4 ICC trophies, 2 as a player and 2 as India's head coach. Strike rate 119 as a player, 167 for his India team; 48 wins in 68 T20Is, but 8 wins in 21 Tests. Data: Cricsheet archive, Sportmonks (our own analysis).\n\n#GautamGambhir #TeamIndia #Shorts")
TAGS = ["Gautam Gambhir", "Gautam Gambhir coach", "Gautam Gambhir player vs coach", "India head coach", "Team India", "Champions Trophy 2025", "T20 World Cup 2026", "cricket analysis", "Data Stories", "The Third Man"]
spec = {"slug": "gambhir_player_coach", "theme": "stadium", "theme_long": "lab", "captions": "v2", "captions_long": False, "series": "data", "tag": "DATA STORIES", "tagsub": "EP. 11 · GAMBHIR: PLAYER VS COACH",
        "files": {"long": "x", "short": "x"},
        "thumb": {"kicker": "DATA STORIES · EP. 11", "lines": [{"t": "PLAYER"}, {"t": "VS COACH", "c": "gold"}], "hero": "4", "herosize": 420},
        "sources": SRC, "venue": VEN, "long": long, "short": short,
        "yt": {"long": {"title": "Gautam Gambhir: Player vs Coach | The Full Data Story", "description": DESC_L, "tags": TAGS},
               "short": {"title": "Gautam Gambhir: Player vs Coach | Who Did It Better? #Shorts", "description": DESC_S, "tags": TAGS}}}
voice_lint.fix_spec(spec)
json.dump(spec, open("specs/gambhir_player_coach.json", "w"), ensure_ascii=False, indent=1)
print("wrote specs/gambhir_player_coach.json: long", sum(len(x["vo"].split()) for x in long), "words;", "short", sum(len(x["vo"].split()) for x in short), "words")
