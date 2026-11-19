"""Writes specs/bumrah_unplayable.json: Data Stories Ep16, 'Why Jasprit Bumrah is unplayable' (vertical, look B). The pictures are drawn by bumrah_render.py; the narration, music and mix by bumrah_build.py through the engine.
Figures: analysis/bumrah_tests.py + analysis/bumrah_context.py (Cricsheet men's Tests, our Sportmonks IPL cache); published sources are listed in docs/BUMRAH_BRIEF.md.   python3 make_bumrah.py"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voice_lint
from dataops import verify as V
F0 = json.load(open("data/provenance/bumrah_tests_figures.json")); F1 = json.load(open("data/provenance/bumrah_context_figures.json"))
CSH = "cricsheet"; c = V.Claims("bumrah_unplayable")
c.check("Test career: 52 Tests, 234 wickets, average 19.79", (52, 234, 19.79), {CSH: (F0["tests"], F0["wkts"], F0["avg"]), "cricketcomau": (52, 234, 19.79), "wikipedia": (52, 234, 19.79)})
c.check("first bowler to 200 Test wickets at an average under 20", True, {"wisden": True, "icc": True, "espncricinfo": True})
c.check("other pace bowlers (50+ wkts since 2018) average 26.1", F1["baseline_avg"], {CSH: F1["baseline_avg"]}, scope="archive")
c.check("bowled or lbw: Bumrah 52%, other quicks 33%", (round(F1["bumrah_bowled_lbw_pct"]), round(F1["baseline_bowled_lbw_pct"])), {CSH: (52, 33)}, scope="archive")
c.check("average 23.9 in the first 20 overs, 18.2 after", (F0["new_ball_overs1_20"]["avg"], F0["old_ball_overs21plus"]["avg"]), {CSH: (23.9, 18.2)}, scope="archive")
bp = F1["by_pitch_type"]; rat = [round(100 * v["bumrah_avg"] / v["match_avg_all_bowlers"]) for v in bp.values()]; assert min(rat) >= 69 and max(rat) <= 75, rat
c.check("about 70-75% of the match average on every type of pitch", (min(rat), max(rat)), {CSH: (min(rat), max(rat))}, scope="archive")
ip = F1["ipl_phases"]["death"]; c.check("IPL death overs economy 7.87 vs 9.60 (same seasons)", (ip["econ"], round(ip["league_econ_same_seasons_weighted"], 1)), {"sportmonks": (7.87, 9.6)}, scope="archive")
c.check("T20 World Cup 2024: 15 wickets, Player of the Tournament", (15, True), {"wikipedia": (15, True), "wisden": (15, True), "outlook": (15, True)})
c.check("T20 World Cup 2026 final: 4/15, Player of the Match", (4, 15, True), {"indiatv": (4, 15, True), "latestly": (4, 15, True), "outlook": (4, 15, True)})
c.check("stress fracture 2019; stress fracture 2022 (out of the T20 World Cup)", True, {"wisden": True, "espncricinfo": True})
c.check("back surgery March 2023", True, {"espn": True, "mykhel": True, "wikipedia": True})
c.check("back spasm in Sydney, January 2025", True, {"theprint": True, "mykhel": True, "wisden": True})
c.check("England 2025: three Tests of five planned", True, {"icc": True, "espncricinfo": True})
c.check("played 52 of India's 81 men's Tests since his debut", tuple(F0["played_of"]), {CSH: (52, 81)}, scope="archive")
c.check("India won 42% of Tests with him, 69% without", (round(F0["india_with"]["win_pct"]), round(F0["india_without"]["win_pct"])), {CSH: (42, 69)}, scope="archive")      # Wisden (to July 2025): 43.5% with, 70.4% without: the same picture
c.check("without him India played 17 of 29 Tests at home; with him 16 of 52", (17, 29, 16, 52), {CSH: (17, 29, 16, 52)}, scope="archive")
c.check("release about 48 cm closer than Kemar Roach", 48, {"cricketcom": 48, "cricketcomau": 48})
c.check("ICC: more than 15 degrees of straightening is illegal; hyperextension discounted", 15, {"icc": 15, "theprint": 15})
c.check("48 cm at 140 km/h is about 12 ms (our arithmetic)", round(0.48 / (140 / 3.6) * 1000), {"arithmetic": 12}, scope="archive")
VO = [
    "Over one, in Wellington. Tom Latham leaves a ball from Jasprit Bumrah. It comes back, and hits off stump. How does a man with the wrong action get the best Test average of any bowler with two hundred wickets?",
    "A short, stuttering run-up. An elbow that bends the wrong way. A back that has already fractured. By the old textbook, this should not work.",
    "Two hundred and thirty-four Test wickets, at nineteen point seven nine. The other quicks since twenty eighteen, in our archive: twenty-six. He was the first to two hundred wickets with an average under twenty.",
    "Here is why. One delivery, four frames: the load, the leap, the bound, and the release.",
    "The elbow hyperextends, which the rules discount. One analysis has him releasing about half a metre closer than Kemar Roach: twelve milliseconds less to react, by our arithmetic. And the backspin makes it a heavy ball: it bounces more than batters expect.",
    "Closer, lower than most quicks, and hard to read: the leave that comes back.",
    "So he hits the stumps. In our archive, fifty-two per cent of his Test wickets are bowled or lbw. For other quicks, thirty-three.",
    "He is better with the old ball: twenty-four runs a wicket early, eighteen after. And on any pitch, about seventy to seventy-five per cent of the match average.",
    "In T-twenty, it is the yorker. IPL death overs, in our archive: seven point eight seven an over, against nine point six. Fifteen wickets and Player of the Tournament at the twenty twenty-four World Cup, and four for fifteen in the twenty twenty-six final.",
    "The price: a stress fracture in twenty nineteen. Another in twenty twenty-two. Surgery in March twenty twenty-three. A spasm in Sydney in twenty twenty-five. Of India's eighty-one Tests, he has played fifty-two. Action or workload, nobody outside has seen the scans.",
    "India win more without him: forty-two per cent with him, sixty-nine without. But without him, India played seventeen of their twenty-nine Tests at home. It is not a fair fight.",
    "Unplayable when fit. The price is the body.",
    "So, the best fast bowler ever? One, yes. Two, top three. Three, not yet.",
]
END_YT = "Subscribe to The Third Man for the full breakdown."; END_IG = "Full breakdown on YouTube. Link in bio."
NAMES_ = ["cold open", "the wrong action", "numbers", "four frames", "callouts", "release", "stumps", "old ball", "short format", "the back", "managed", "verdict", "poll"]
short = [{"vo": v, "scene": {"type": "statement", "lines": [{"t": n.upper()}]}} for v, n in zip(VO, NAMES_)] + [{"vo": END_YT, "scene": {"type": "statement", "lines": [{"t": "END"}]}}]
TAGS = ["Jasprit Bumrah", "Bumrah bowling action", "Bumrah why unplayable", "Bumrah injury", "Bumrah stats", "best fast bowler", "India cricket", "Test cricket", "cricket analysis", "The Third Man"]
DS = ("Jasprit Bumrah: why he is unplayable. The short run-up, the hyperextended elbow, the release; 52% of his Test wickets bowled or lbw; better with the old ball; and the cost: the back. Best fast bowler ever? Comment 1 yes, 2 top three, 3 not yet.\n\n"
      "Our archive: Cricsheet men's Tests since 2018 and IPL 2013-2026. Career figures: Cricinfo via Wikipedia and cricket.com.au. The action: ICC rules, Ian Pont and Dr Kumar Satish Ravi (ThePrint), cricket.com analysis (48 cm vs Kemar Roach). Injury timeline: Wisden, ESPNcricinfo.\n\n#Bumrah #JaspritBumrah #Cricket #Shorts")
spec = {"slug": "bumrah_unplayable", "thumb": {"kicker": "DATA STORY · EP 16", "lines": [{"t": "BUMRAH:"}, {"t": "UNPLAYABLE WHEN FIT", "c": "gold"}], "hero": "19.79", "herosize": 480}, "ig_cover": {"lines": [{"t": "BUMRAH:"}, {"t": "UNPLAYABLE WHEN FIT", "c": "gold"}], "sub": "52 TESTS · 234 WICKETS", "hero": "19.79"}, "theme": "lab", "captions": "lab", "series": "data", "tag": "DATA STORY", "tagsub": "BUMRAH: WHY HE IS UNPLAYABLE", "files": {"short": "x", "long": "_unused"}, "outro": False,
        "sources": ["Cricsheet men's Test ball-by-ball (cricsheet.org, ODC-BY), 'our archive': analysis/bumrah_tests.py, analysis/bumrah_context.py. IPL: our Sportmonks cache 2013-2026.",
                    "Career figures: https://en.wikipedia.org/wiki/Jasprit_Bumrah (Cricinfo figures to 5 Oct 2026) and https://www.cricket.com.au/players/CA:10982",
                    "Action: https://theprint.in/sport/from-his-biomechanics-anatomy-to-hypermobility-what-makes-jasprit-bumrah-unique/2432437/ ; ICC illegal bowling action regulations https://www.icc-cricket.com/about/cricket/rules-and-regulations/illegal-bowling-actions ; release point analysis: cricket.com 'Decoded: Jasprit Bumrah' (48 cm vs Kemar Roach)",
                    "Injuries and workload: https://www.wisden.com/series/sri-lanka-in-india-2022-23/cricket-news/back-and-forth-a-timeline-of-jasprit-bumrahs-back-injuries ; https://www.icc-cricket.com/news/gambhir-reveals-bumrah-plan-for-remaining-england-tests ; with-and-without analysis: https://www.wisden.com/series/england-vs-india-m-2025/cricket-news/explained-why-india-win-more-tests-without-bumrah-than-with-him",
                    "T20 World Cups: Wisden / Outlook (2024), Outlook / IndiaTV (2026 final)"],
        "short": short, "short_ig_end": END_IG, "yt": {"short": {"title": "Jasprit Bumrah: Why He Is Unplayable | Data Story Ep 16 #Shorts", "description": DS, "tags": TAGS}}}
c.save(spec); voice_lint.fix_spec(spec); json.dump(spec, open("specs/bumrah_unplayable.json", "w"), ensure_ascii=False, indent=1)
print("words", sum(len(x["vo"].split()) for x in short), voice_lint.check_spec(spec, ("short",)) or "lint clean", "| files:", spec["files"])
