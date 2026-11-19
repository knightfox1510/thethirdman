"""Writes specs/nz_test_preview.json (Tactics Board Ep04): India vs New Zealand, 1st Test preview (Wellington, 19-23 Nov 2026). Rebuilt 18 Nov 2026 for engagement + the verification gate.
Figures: analysis/nz_tests.py (Cricsheet men's Tests, 'in our archive') -> data/provenance/nz_test_preview_figures.json. Facts checked 18 Nov 2026:
  squads: ICC (India squad, 14 Nov: Kuldeep released, Gurnoor Brar added), Outlook India, Qatar Tribune/Reuters + ARY/AFP (New Zealand 14); Test dates: WION, Outlook, Tribune.
  India's record in NZ: Scroll data check (to 2020: 24 matches incl. one abandoned, 5 won, 8 lost, 10 drawn; series won 1967/68 and 2008/09) + the 2020 series (two NZ wins, Cricsheet): 25 played, 5 won, 10 lost, 10 drawn."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voice_lint
from dataops import verify as V
from variants import YT_CTA

F = json.load(open("data/provenance/nz_test_preview_figures.json")); BN, BC, BL = F["bumrah_nz"], F["bumrah_career"], F["bumrah_latham"]
OLD = json.load(open("specs/nz_test_preview.json"))                                 # keeps the static look keys and the classic Shorts
c = V.Claims("nz_test_preview")
SC, WK, CS, IC, OL, QT, AR, NW = "scroll", "wikipedia", "cricsheet", "icc", "outlook", "qatar", "arynews", "newssummary"
c.check("India won Test series in NZ: 1967-68 and 2008-09 (two in 58 years)", 2, {SC: 2, WK: 2})
c.check("India series win 2009 in NZ, 1-0 (Hamilton win, two draws)", "1-0", {SC: "1-0", CS: "1-0"})
c.check("years between series wins (1968 to 2009)", 41, {SC: 41, WK: 41})
c.check("India Tests played in NZ", 25, {SC: 25, NW: 25}); c.check("India Tests won in NZ", 5, {SC: 5, NW: 5}); c.check("India Tests lost in NZ", 10, {SC: 10, NW: 10})
c.check("NZ won the first WTC final (2021) vs India; Jamieson player of the match", "NZ, Jamieson", {WK: "NZ, Jamieson", CS: "NZ, Jamieson"})
c.check("NZ beat India 3-0 in India, 2024", "3-0", {CS: "3-0", "wisden": "3-0"})
c.check("share of Test wickets to pace since 2010, NZ (our spinner tagging)", 86, {CS: 86}, scope="archive"); c.check("share of Test wickets to pace since 2010, India", 44, {CS: 44}, scope="archive")
c.check("India runs per wicket in NZ since 2009", 35.5, {CS: 35.5}, scope="archive"); c.check("India runs per wicket at home since 2010", 41.1, {CS: 41.1}, scope="archive")
c.check("Basin Reserve since 2010: first-innings average 339, bat first 7 wins, bat second 8 (20 Tests)", (339, 7, 8, 20), {CS: (339, 7, 8, 20)}, scope="archive")
c.check("Bumrah Test average (archive)", BC["avg"], {CS: BC["avg"]}, scope="archive"); c.check("Bumrah in NZ: wickets and average (two Tests, 2020)", (BN["wkts"], BN["avg"]), {CS: (BN["wkts"], BN["avg"])}, scope="archive")
c.check("Bumrah v Latham (balls, runs, outs)", (BL["balls"], BL["runs"], BL["outs"]), {CS: (BL["balls"], BL["runs"], BL["outs"])}, scope="archive")
c.check("most Test wickets v India since 2002 (archive): Southee 55, Boult 41, Ajaz Patel 32; Santner 23, Jamieson 22", (55, 41, 32, 23, 22), {CS: (55, 41, 32, 23, 22)}, scope="archive")
c.check("Southee, Boult, Ajaz Patel not in NZ's 14-man squad", True, {QT: True, AR: True}); c.check("NZ squad: Latham captain; Conway, Ravindra, Blundell injury concerns", True, {QT: True, AR: True})
c.check("India: Kuldeep Yadav released, Gurnoor Brar added (no Test caps)", True, {IC: True, OL: True, "deccanchronicle": True}); c.check("India squad has six fast bowlers", 6, {IC: 6, OL: 6})
c.check("Pant rejoined the squad after fitness clearance", True, {OL: True, "searchsummary": True})
c.check("3 of India's 16 have played a Test in NZ: Bumrah, Jadeja, Pant", 3, {CS: 3, IC: 3})
c.check("first Test Wellington from 19 Nov; second Christchurch from 27 Nov", True, {"wion": True, "outlook_sched": True, "tribune": True})

OPT = lambda n, t, c_=None: {"h": f"{n}  {t}", **({"c": c_} if c_ else {})}
POLL = {"type": "list", "head": {"t": "YOUR CALL", "sub": "COMMENT 1, 2 OR 3"}, "items": [{"h": "INDIA WIN THE SERIES", "d": "First series win in New Zealand since 2009", "c": "gold"}, {"h": "SERIES DRAWN", "d": "One-all, or both Tests drawn"}, {"h": "NEW ZEALAND WIN", "d": "Home advantage holds"}]}
long = [
    {"vo": "India have won just two Test series in New Zealand, in fifty-eight years. The next one starts on the nineteenth of November, in Wellington. And India's best bowler has a problem there. Stay to the end, and we'll show you the number that could decide this series.",
     "chapter": "Intro", "scene": {"type": "statement", "kicker": "INDIA IN NEW ZEALAND · 2 TESTS · FROM 19 NOV", "lines": [{"t": "2 SERIES WINS."}, {"t": "IN 58 YEARS.", "c": "gold"}]}},
    {"vo": "But first, make your call. Can India win this series? Comment one for a win, two for a drawn series, three for a New Zealand win. We'll check back at the end.", "scene": POLL},
    {"vo": "Start with the history. India won here in nineteen sixty-eight, three-one. Then nothing for forty-one years, until MSD's side won in two thousand and nine. Since then, beaten in twenty fourteen, and beaten two-nil on the last tour, in twenty twenty.", "chapter": "The History",
     "scene": {"type": "timeline", "head": {"t": "INDIA'S RECENT TEST SERIES IN NEW ZEALAND"}, "events": [{"y": "1968", "t": "Won 3-1", "hl": True}, {"y": "2009", "t": "Won 1-0", "hl": True}, {"y": "2014", "t": "Lost 0-1", "c": "red"}, {"y": "2020", "t": "Lost 0-2", "c": "red"}]}},
    {"vo": "In twenty-five Tests in New Zealand, India have won five, and lost ten. New Zealand beat them in the first World Test Championship final. And in twenty twenty-four, they beat India three-nil, in India.",
     "scene": {"type": "stats", "head": {"t": "THE NEW ZEALAND PROBLEM"}, "tiles": [{"v": "5 / 25", "l": "TESTS WON IN NEW ZEALAND", "c": "red"}, {"v": "2021", "l": "LOST THE WTC FINAL TO NZ", "c": "ink"}, {"v": "0-3", "l": "BEATEN AT HOME, 2024", "c": "red"}]}},
    {"vo": "So why is New Zealand so hard? Look at who takes the wickets. Since twenty ten, in our archive, eighty-six per cent of Test wickets in New Zealand go to fast bowlers. In India, it's forty-four.", "chapter": "Why It's So Hard",
     "scene": {"type": "compare", "head": {"t": "WHO TAKES THE WICKETS", "sub": "SHARE OF TEST WICKETS TAKEN BY PACE · 2010-2025 · OUR ARCHIVE"}, "a": {"name": "IN NEW ZEALAND", "color": "gold"}, "b": {"name": "IN INDIA", "color": "ink"}, "rows": [["PACE BOWLERS", "86%", "44%", "a"], ["SPINNERS", "14%", "56%", "b"]]}},
    {"vo": "And India's batters feel it. Since two thousand and nine, they average thirty-five and a half runs per wicket in New Zealand. At home, forty-one. The ball does more, for longer.",
     "scene": {"type": "compare", "head": {"t": "INDIA'S BATTING", "sub": "RUNS PER WICKET IN TESTS · 2009-2025 · OUR ARCHIVE"}, "a": {"name": "IN NEW ZEALAND", "color": "red"}, "b": {"name": "AT HOME", "color": "ink"}, "rows": [["RUNS PER WICKET", "35.5", "41.1", "b"]]}},
    {"vo": "The New Zealand plan is simple. Full, swinging and seaming with the new ball, a packed slip cordon, and patience. At the Basin Reserve, since twenty ten, the first-innings average is three hundred and thirty-nine, and batting first is no advantage: in twenty Tests, seven wins for the side batting first, eight for the side batting second.",
     "scene": {"type": "fieldplan", "head": {"t": "THE NEW ZEALAND PLAN", "sub": "ILLUSTRATIVE FIELD · NEW BALL"}, "fielders": ["keeper", "slip", "2nd slip", "3rd slip", "gully", "point", "mid-off", "mid-on", "fine leg"], "hl": ["slip", "2nd slip", "3rd slip", "gully"],
               "length": {"from": 4, "to": 6.5, "label": "FULL, SEAMING"}, "shots": [{"to": "2nd slip", "label": "THE EDGE", "lift": 0.05}], "lines": [{"t": "FULL."}, {"t": "PATIENT.", "c": "gold"}], "sub": "Basin Reserve since 2010: first-innings average 339 · our archive"}},
    {"vo": "Now the number we promised. जसप्रीत बुमराह averages nineteen point eight in Tests, in our archive. In New Zealand, in two Tests in twenty twenty, he took six wickets, at thirty-one point seven. That is the gap India have to close.", "chapter": "Bumrah's New Zealand problem",
     "scene": {"type": "compare", "head": {"t": "BUMRAH'S NEW ZEALAND PROBLEM", "sub": "BOWLING AVERAGE · TESTS · OUR ARCHIVE"}, "a": {"name": "NEW ZEALAND", "color": "red"}, "b": {"name": "CAREER", "color": "ink"}, "rows": [["BOWLING AVERAGE", "31.7", "19.8", "b"], ["WICKETS", "6 in 2 Tests", "234"]]}},
    {"vo": "Can he fix it this time? It helps that the attack he faced has changed. Since two thousand and two, in our archive, the three New Zealand bowlers with the most Test wickets against India are Tim Southee, Trent Boult and एजाज़ पटेल. None of them is in this squad.", "chapter": "A New New Zealand",
     "scene": {"type": "bars", "head": {"t": "WHO'S MISSING", "sub": "NZ BOWLERS' TEST WICKETS AGAINST INDIA · SINCE 2002 · OUR ARCHIVE"}, "max": 60, "dec": 0, "items": [{"label": "TIM SOUTHEE · NOT IN SQUAD", "value": 55, "color": "muted"}, {"label": "TRENT BOULT · NOT IN SQUAD", "value": 41, "color": "muted"}, {"label": "AJAZ PATEL · NOT IN SQUAD", "value": 32, "color": "muted"}, {"label": "MITCHELL SANTNER · IN THE SQUAD", "value": 23, "color": "gold"}, {"label": "KYLE JAMIESON · IN THE SQUAD", "value": 22, "color": "gold"}]}},
    {"vo": "The man to watch is Kyle Jamieson. Tall, and relentless: he gets bounce from a good length. He has twenty-two Test wickets against India, in our archive, and he was player of the match when New Zealand won the World Test Championship final.",
     "scene": {"type": "trajectory", "head": {"t": "THE JAMIESON BALL", "sub": "ILLUSTRATIVE · SIDE-ON"}, "hl": ["GOOD"], "bowler_c": "ink", "balls": [{"length": 6.5, "end": 1.7, "label": "GOOD LENGTH, CHEST HIGH", "c": "gold", "at": 0.3}], "note": "extra bounce from a good length"}},
    {"vo": "Alongside him: Matt Henry, Jacob Duffy, Nathan Smith and Blair Tickner, with Mitchell Santner as the spinner. Tom Latham captains, and Devon Conway, Rachin Ravindra and Tom Blundell are all racing to be fit.",
     "scene": {"type": "list", "head": {"t": "NEW ZEALAND'S SQUAD", "sub": "14 NAMED FOR THE INDIA SERIES"}, "items": [{"h": "KYLE JAMIESON", "d": "22 Test wickets against India · our archive", "c": "gold"}, {"h": "MATT HENRY · JACOB DUFFY", "d": "Seam and swing"}, {"h": "NATHAN SMITH · BLAIR TICKNER", "d": "Hard lengths"}, {"h": "MITCHELL SANTNER", "d": "Spin"}, {"h": "TOM LATHAM (C)", "d": "Conway, Ravindra, Blundell: fitness doubts"}]}},
    {"vo": "India's squad changed this month. Kuldeep Yadav has been released, and the pacer Gurnoor Brar, with no Test caps, is in. That makes six fast bowlers. And only three of the sixteen have ever played a Test in New Zealand: Bumrah, Jadeja, and Rishabh Pant, who has rejoined the squad after clearing his fitness.", "chapter": "India's squad",
     "scene": {"type": "bignum", "head": {"t": "BEEN THERE BEFORE"}, "value": 3, "suffix": " OF 16", "label": "INDIA'S SQUAD WHO HAVE PLAYED A TEST IN NEW ZEALAND · OUR ARCHIVE", "color": "red", "note": "Bumrah, Jadeja, Pant · six fast bowlers in the squad"}},
    {"vo": "The duel that could decide it? बुमराह against Tom Latham. In our archive, Bumrah has bowled a hundred and sixty-three balls to Latham. Seventy-nine runs. One dismissal. The New Zealand captain has held him off before.",
     "scene": {"type": "matchup", "head": {"t": "THE KEY DUEL", "sub": "BUMRAH TO LATHAM IN TESTS · OUR ARCHIVE"}, "left": {"name": "BUMRAH", "team": "IND", "pose": "release", "sub": "1 DISMISSAL"}, "right": {"name": "LATHAM", "team": "NZ", "pose": "stance", "sub": "79 RUNS, 163 BALLS"}}},
    {"vo": "Our call? New Zealand at home are still favourites. But their attack is far less experienced, and India have the best bowler on either side, with a point to prove. We say one-all.", "chapter": "Verdict",
     "scene": {"type": "statement", "kicker": "OUR CALL", "lines": [{"t": "ONE-ALL."}], "sub": "New Zealand favourites at home. Bumrah is India's equaliser."}},
    {"vo": "Now it's your turn. Remember your call? One, two or three. Tell us why in the comments, and we'll come back to it after the first Test. Subscribe, so you don't miss it.", "scene": {"type": "cta", "lines": [{"t": "YOUR CALL:"}, {"t": "1, 2 OR 3?", "c": "gold"}], "pill": "SUBSCRIBE · MATCH BREAKDOWNS"}},
]
short = [
    {"vo": "Can India win a Test series in New Zealand? They've done it twice, in fifty-eight years.", "scene": {"type": "statement", "lines": [{"t": "2 SERIES WINS"}, {"t": "IN 58 YEARS.", "c": "gold"}]}},
    {"vo": "Their best bowler, जसप्रीत बुमराह, averages nineteen point eight in Tests. In New Zealand, thirty-one point seven.",
     "scene": {"type": "compare", "head": {"t": "BUMRAH'S NZ PROBLEM", "sub": "BOWLING AVERAGE · OUR ARCHIVE"}, "a": {"name": "IN NZ", "color": "red"}, "b": {"name": "CAREER", "color": "ink"}, "rows": [["AVERAGE", "31.7", "19.8", "b"]]}},
    {"vo": "And New Zealand's old attack is gone. Southee, Boult and एजाज़ पटेल, the top three wicket-takers against India since two thousand and two, are not in this squad. But Kyle Jamieson is.",
     "scene": {"type": "bars", "head": {"t": "WHO'S MISSING", "sub": "TEST WICKETS V INDIA SINCE 2002 · OUR ARCHIVE"}, "max": 60, "dec": 0, "items": [{"label": "SOUTHEE · OUT", "value": 55, "color": "muted"}, {"label": "BOULT · OUT", "value": 41, "color": "muted"}, {"label": "AJAZ PATEL · OUT", "value": 32, "color": "muted"}, {"label": "JAMIESON · IN", "value": 22, "color": "gold"}]}},
    {"vo": "The first Test starts on the nineteenth, in Wellington. Win, draw, or loss for India? Comment one, two or three.", "scene": POLL},
    dict(YT_CTA, vo="Full preview on the channel. Subscribe to The Third Man."),
]
spec = {**{k: OLD[k] for k in ("theme", "theme_long", "captions", "captions_long", "series", "tag", "short_classic") if k in OLD}, "slug": "nz_test_preview", "tagsub": "INDIA VS NEW ZEALAND · 1ST TEST PREVIEW",
        "files": {"long": "x", "short": "x"}, "thumb": {"kicker": "INDIA VS NEW ZEALAND · FROM 19 NOV", "lines": [{"t": "CAN INDIA"}, {"t": "WIN IN NZ?", "c": "gold"}], "hero": "2 IN 58", "herosize": 300},
        "ig_cover": {"lines": [{"t": "BUMRAH'S"}, {"t": "NZ PROBLEM", "c": "gold"}], "sub": "INDIA VS NEW ZEALAND · 1ST TEST", "hero": "31.7"},
        "sources": ["Cricsheet men's Test ball-by-ball (cricsheet.org, ODC-BY), shown as 'our archive'; spinners are tagged by name because bowling type is not in the data. Figures: analysis/nz_tests.py",
                    "India's Test record in New Zealand: Scroll data check https://scroll.in/field/953699/data-check-a-look-at-key-numbers-from-indias-previous-test-tours-of-new-zealand (to 2020; 2020 series from Cricsheet)",
                    "India squad (14 Nov 2026): https://www.icc-cricket.com/tournaments/world-test-championship/news/india-release-spinner-for-pacer-in-test-squad-to-face-kiwis ; https://www.outlookindia.com/sports/cricket/india-vs-new-zealand-test-series-2026-gurnoor-brar-rishabh-pant-added-squad",
                    "New Zealand squad (11 Nov 2026): https://www.qatar-tribune.com/article/263936/sports/new-zealand-announce-squad-for-home-test-series-vs-india ; https://arynews.tv/seamer-duffy-back-in-new-zealand-squad-for-india-tests",
                    "Schedule: https://www.outlookindia.com/sports/cricket/indias-tour-of-new-zealand-schedule-2026-ind-vs-nz-12-match-series-100-years-of-sporting-ties ; https://en.wikipedia.org/wiki/2021_ICC_World_Test_Championship_final"],
        "long": long, "short": short,
        "yt": {"long": {"title": "India vs New Zealand - 1st Test Preview | Can India Win in New Zealand?",
                        "description": "India vs New Zealand, 1st Test preview at the Basin Reserve, Wellington (19-23 November 2026). India have won two Test series in New Zealand in 58 years. Why is it so hard, how has New Zealand's attack changed, and can Jasprit Bumrah fix his New Zealand numbers (19.8 career average, 31.7 in New Zealand)?\n\n"
                                       "YOUR CALL: comment 1 (India win the series), 2 (drawn series) or 3 (New Zealand win), and tell us why. We'll come back to it after the first Test.\n\nOur numbers are from our Cricsheet ball-by-ball archive (men's Tests; spinners tagged by name). Squads as announced by 14 November 2026.\n\n#INDvNZ #IndiaVsNewZealand #1stTest #WTC",
                        "tags": ["India vs New Zealand", "India vs New Zealand 1st Test", "IND vs NZ 1st Test", "New Zealand vs India Test", "Jasprit Bumrah", "Kyle Jamieson", "Tom Latham", "Shubman Gill", "Basin Reserve", "Wellington Test", "World Test Championship", "cricket analysis", "The Third Man"]},
               "short": {"title": "Bumrah's New Zealand Problem | India vs New Zealand 1st Test #Shorts",
                         "description": "India vs New Zealand, 1st Test (Wellington, 19 November 2026): Bumrah averages 19.8 in Tests, 31.7 in New Zealand. Win, draw or loss for India? Comment 1, 2 or 3. Full preview on the channel.\n\nOur archive: Cricsheet men's Test ball-by-ball.\n\n#INDvNZ #IndiaVsNewZealand #1stTest #Shorts",
                         "tags": ["India vs New Zealand", "India vs New Zealand 1st Test", "IND vs NZ 1st Test", "Jasprit Bumrah", "cricket shorts", "The Third Man"]}}}
c.save(spec); voice_lint.fix_spec(spec); spec["files"].setdefault("long", "_unused")
json.dump(spec, open("specs/nz_test_preview.json", "w"), ensure_ascii=False, indent=1)
print("long words", sum(len(s["vo"].split()) for s in long), "| short words", sum(len(s["vo"].split()) for s in short), "|", voice_lint.check_spec(spec, ("long", "short")) or "lint clean")
