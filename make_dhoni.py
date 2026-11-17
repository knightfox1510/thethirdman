"""Builds the Dhoni package (Nov 2026, after CSK announced his retirement from the IPL on 17 Nov 2026):
  specs/dhoni_retires.json       Channel Ep1       vertical tribute (YouTube Short + IG version), CSK avatar, stage look
  specs/dhoni_ipl_story.json     Data Stories Ep13  "Dhoni's IPL in numbers": the finisher (long + Short + IG carousel)
  specs/dhoni_captain_myth.json  Myth or Data Ep4   "Did CSK just win the close ones?" (long + Short)
Numbers: career and captaincy totals are reported figures (Cricinfo records page as supplied by the owner, Cricketaddictor, ETV Bharat, Eastern Eye, Khel Now, Wikipedia);
every archive figure comes from analysis/dhoni_ipl.py (Sportmonks IPL 2013-2025, "in our archive", super overs excluded) and is read back from data/provenance/dhoni_ipl_figures.json, never typed.
Known disagreement, resolved: ETV Bharat says "226 matches as captain" - that is the figure before 2025 (he captained about nine more CSK matches in 2025); the totals 235 / 136 / 97 / 2 add up in three sources.
Win rate is stated as "136 of 235" (57.87% counts no-results as matches; 58.37% leaves them out), never as a bare percentage."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voice_lint
from dataops import verify as V
from variants import YT_CTA

F = json.load(open("data/provenance/dhoni_ipl_figures.json"))
r = lambda x, n=0: int(round(x)) if n == 0 else round(x, n)
PH = {k: F[f"phase_{k}"] for k in ("powerplay", "middle", "death")}
L2, O20, CD = F["last2"], F["over20"], F["chase_death"]
SEAS = {s["season"]: s for s in F["seasons"]}
CS = F["csk_dhoni_seasons"]
RANK = {e["team"]: e for e in F["league_rank_dhoni_seasons"]}
pct = lambda a, b: round(100 * a / b)

# ---------------------------------------------------------------- claims
CI, CA, ETV, EE, KN, IS, WP, ITV = "cricinfo", "cricketaddictor", "etvbharat", "easterneye", "khelnow", "insidesport", "wikipedia", "indiatv"
c = V.Claims("dhoni_ipl_story")
c.check("IPL matches (career)", 278, {ETV: 278, EE: 278, KN: 278, CA: 278})
c.check("IPL runs (career)", 5439, {ETV: 5439, EE: 5439, KN: 5439, CA: 5439})
c.check("IPL titles as captain (2010, 2011, 2018, 2021, 2023)", 5, {ETV: 5, CA: 5, EE: 5, KN: 5})
c.check("IPL finals as captain", 10, {ETV: 10, CA: 10})
c.check("Champions League T20 titles", 2, {ETV: 2, KN: 2})
c.check("matches as IPL captain (CSK + Rising Pune Supergiant)", 235, {CA: 235, IS: 235})
c.check("wins as IPL captain", 136, {CA: 136, IS: 136})
c.check("losses as IPL captain", 97, {CA: 88 + 9, IS: 97})
c.check("no results / ties as IPL captain", 2, {CA: 2, IS: 2})
c.check("five titles level with Rohit Sharma, the most by an IPL captain", "joint-most", {WP: "joint-most", ITV: "joint-most"})
c.check("archive: strike rate overs 1-6", r(PH["powerplay"]["dhoni"]["sr"]), {"sportmonks": r(PH["powerplay"]["dhoni"]["sr"])}, scope="archive")
c.check("archive: league strike rate overs 1-6", r(PH["powerplay"]["league_sr"]), {"sportmonks": r(PH["powerplay"]["league_sr"])}, scope="archive")
c.check("archive: strike rate overs 7-15", r(PH["middle"]["dhoni"]["sr"]), {"sportmonks": r(PH["middle"]["dhoni"]["sr"])}, scope="archive")
c.check("archive: league strike rate overs 7-15", r(PH["middle"]["league_sr"]), {"sportmonks": r(PH["middle"]["league_sr"])}, scope="archive")
c.check("archive: strike rate overs 16-20", r(PH["death"]["dhoni"]["sr"]), {"sportmonks": r(PH["death"]["dhoni"]["sr"])}, scope="archive")
c.check("archive: league strike rate overs 16-20", r(PH["death"]["league_sr"]), {"sportmonks": r(PH["death"]["league_sr"])}, scope="archive")
c.check("archive: balls faced overs 16-20", PH["death"]["dhoni"]["balls"], {"sportmonks": PH["death"]["dhoni"]["balls"]}, scope="archive")
c.check("archive: most runs in overs 16-20", F["death_most_runs"]["first_val"], {"sportmonks": F["death_most_runs"]["first_val"]}, scope="archive")
c.check("archive: most balls faced in overs 16-20", F["death_most_balls"]["first"], {"sportmonks": F["death_most_balls"]["first"]}, scope="archive")
c.check("archive: strike rate last two overs", r(L2["dhoni"]["sr"]), {"sportmonks": r(L2["dhoni"]["sr"])}, scope="archive")
c.check("archive: league strike rate last two overs", r(L2["league_sr"]), {"sportmonks": r(L2["league_sr"])}, scope="archive")
c.check("archive: sixes in the last two overs", F["last2_most_sixes"]["first_val"], {"sportmonks": F["last2_most_sixes"]["first_val"]}, scope="archive")
c.check("archive: next best sixes in the last two overs (Hardik Pandya)", F["last2_most_sixes"]["second_val"], {"sportmonks": F["last2_most_sixes"]["second_val"]}, scope="archive")
c.check("archive: most runs in the last two overs", F["last2_most_runs"]["first_val"], {"sportmonks": F["last2_most_runs"]["first_val"]}, scope="archive")
c.check("archive: strike rate in the 20th over", r(O20["dhoni"]["sr"]), {"sportmonks": r(O20["dhoni"]["sr"])}, scope="archive")
c.check("archive: league strike rate in the 20th over", r(O20["league_sr"]), {"sportmonks": r(O20["league_sr"])}, scope="archive")
for y in (2013, 2018, 2023, 2024, 2025):
    c.check(f"archive: {y} death-over strike rate", r(SEAS[y]["death_sr"]), {"sportmonks": r(SEAS[y]["death_sr"])}, scope="archive")
c.check("archive: 2025 league death-over strike rate", r(SEAS[2025]["league_death_sr"]), {"sportmonks": r(SEAS[2025]["league_death_sr"])}, scope="archive")
c.save(); c_story = c

m = V.Claims("dhoni_captain_myth")
m.check("matches as IPL captain", 235, {CA: 235, IS: 235}); m.check("wins as IPL captain", 136, {CA: 136, IS: 136})
m.check("titles", 5, {ETV: 5, CA: 5, EE: 5}); m.check("finals", 10, {ETV: 10, CA: 10}); m.check("Champions League T20 titles", 2, {ETV: 2, KN: 2})
m.check("five titles level with Rohit Sharma", "joint-most", {WP: "joint-most", ITV: "joint-most"})
m.check("archive: decided CSK matches in the eight seasons", CS["decided"], {"sportmonks": CS["decided"]}, scope="archive")
m.check("archive: CSK wins in those matches", CS["won"], {"sportmonks": CS["won"]}, scope="archive")
m.check("archive: close finishes (<=10 runs or <=2 wickets)", CS["tight"], {"sportmonks": CS["tight"]}, scope="archive")
m.check("archive: close finishes won", CS["tight_won"], {"sportmonks": CS["tight_won"]}, scope="archive")
m.check("archive: every other match", CS["rest"], {"sportmonks": CS["rest"]}, scope="archive"); m.check("archive: every other match won", CS["rest_won"], {"sportmonks": CS["rest_won"]}, scope="archive")
m.check("archive: Mumbai Indians win rate, same seasons", round(RANK["Mumbai Indians"]["pct"]), {"sportmonks": round(RANK["Mumbai Indians"]["pct"])}, scope="archive")
assert RANK["Chennai Super Kings"]["pct"] > RANK["Mumbai Indians"]["pct"] > RANK["Kolkata Knight Riders"]["pct"]
assert CS["tight"] == 16 and CS["tight_won"] == 9 and CS["decided"] == 129 and CS["won"] == 80, CS
c_myth = m

t = V.Claims("dhoni_retires")
for k, v, s in (("matches", 278, {ETV: 278, EE: 278, KN: 278}), ("runs", 5439, {ETV: 5439, EE: 5439, KN: 5439}), ("titles", 5, {ETV: 5, CA: 5, EE: 5}), ("finals", 10, {ETV: 10, CA: 10}),
                ("captain matches", 235, {CA: 235, IS: 235}), ("captain wins", 136, {CA: 136, IS: 136}), ("Champions League T20 titles", 2, {ETV: 2, KN: 2})):
    t.check(k, v, s)
t.check("retirement as a player, mentor role from 2027 (CSK announcement, 17 Nov 2026)", "retired, team mentor", {EE: "retired, team mentor", KN: "retired, team mentor", "kalingatv": "retired, team mentor", "crickettimes": "retired, team mentor"})
t.check("archive: sixes in the last two overs", F["last2_most_sixes"]["first_val"], {"sportmonks": F["last2_most_sixes"]["first_val"]}, scope="archive")
c_tribute = t
for cc in (c_story, c_myth, c_tribute):
    assert cc.summary().get("UNVERIFIED", 0) == 0 and cc.summary().get("CONFLICT", 0) == 0, cc.summary()
c_myth.save(); c_tribute.save()

# ---------------------------------------------------------------- helpers
CTA_YT = {"vo": YT_CTA["vo"], "scene": YT_CTA["scene"]}
VENUE = {"time": "night", "crowd": [[250, 200, 20], [240, 240, 240], [25, 100, 200], [20, 60, 140]], "boards": [[250, 200, 20], [25, 100, 200]]}   # yellow stands: CSK's home colours, no logos
TAGS = ["MS Dhoni", "Dhoni IPL", "Dhoni retirement", "Dhoni IPL retirement", "CSK", "Chennai Super Kings", "IPL 2027", "Dhoni captain", "IPL records", "cricket analysis", "The Third Man"]
SRC_COMMON = ["Retirement and mentor role: CSK announcement, 17 November 2026, as reported by Eastern Eye https://www.easterneye.biz/ms-dhoni-retires-ipl-csk-mentor-2027-records/ , Khel Now https://khelnow.com/cricket/ms-dhoni-ipl-appointed-as-csk-mentor-202611 , Kalinga TV https://kalingatv.com/sports/ms-dhoni-announces-retirement-from-ipl/ and Cricket Times https://crickettimes.com/2026/11/fans-get-emotional-as-ms-dhoni-announces-retirement-ahead-of-ipl-2027/ (we could not read the franchise's own post).",
              "Career totals (278 matches, 5,439 runs, average 38.30, strike rate 137.45, 24 fifties, 5 titles, 10 finals, 2 Champions League T20 titles): ETV Bharat https://www.etvbharat.com/en/sports/ms-dhoni-retirement-ipl-career-achievements-records-chennai-super-kings-enn26111704201 , Cricketaddictor https://cricketaddictor.com/cricket-news/ms-dhonis-record-as-ipl-captain-full-batting-stats-and-key-numbers-after-retirement-466132/ , Eastern Eye, Khel Now.",
              "Captaincy (235 matches, 136 wins, 97 losses, 2 no results; CSK and Rising Pune Supergiant): ESPNcricinfo records, most matches as captain https://www.cricinfo.com/records/trophy/individual-most-matches-as-captain/indian-premier-league-117 (page supplied by the channel owner; we could not open it), Cricketaddictor and Insidesport https://www.insidesport.in/ms-dhoni-captaincy-records-in-all-formats-and-ipl/ . ETV Bharat's '226 matches' is the figure before 2025. Five titles level with Rohit Sharma: Wikipedia, 'List of Indian Premier League captains' https://en.wikipedia.org/wiki/List_of_Indian_Premier_League_captains and India TV.",
              "In our archive: Sportmonks ball-by-ball, every IPL match 2013-2026 (2008-2012 are not in our plan; MSD's figures cover the seasons he played, 2013-2025, as he missed 2026), super overs excluded; powerplay = overs 1-6, middle 7-15, death 16-20. Figures: analysis/dhoni_ipl.py (data/provenance/dhoni_ipl_figures.json)."]


def stage(vo, panel, pose="stand", cam="push", fx=("vignette", "spot"), **kw):
    sc = {"type": "stage", "panel": dict(panel, at=0.05), "avatars": [{"kit": "CSK", "pose": pose, "x": 0.5}], "cam": cam, "fx": list(fx)}; sc.update(kw)
    return {"vo": vo, "scene": sc}


# ---------------------------------------------------------------- 1. tribute Short
tribute = [
    stage("चेन्नई have announced it. MSD has retired from the IPL, and will become the team's mentor.",
          {"kind": "headline", "kicker": "CSK ANNOUNCE · 17 NOV 2026", "lines": [{"t": "DHONI RETIRES"}, {"t": "FROM THE IPL", "c": "gold"}]}, pose="stand"),
    stage("Two hundred and seventy-eight matches. Five thousand, four hundred and thirty-nine runs.",
          {"kind": "versus", "kicker": "MS DHONI · IPL CAREER", "left": {"v": "278", "l": "Matches", "c": "gold"}, "right": {"v": "5,439", "l": "Runs", "c": "gold"}, "sep": "&"}, pose="stance", cam="pull"),
    stage("Five titles as captain: twenty ten, twenty eleven, twenty eighteen, twenty twenty-one, and twenty twenty-three.",
          {"kind": "bignum", "kicker": "AS CAPTAIN", "label": "IPL TITLES", "value": 5, "count_dur": 0.6, "color": "gold", "note": "2010 · 2011 · 2018 · 2021 · 2023"}, pose="raise", fx=("vignette", "spot", "confetti"), fx_at=0.4),
    stage("Ten IPL finals. And two Champions League titles.",
          {"kind": "versus", "kicker": "AS CAPTAIN", "left": {"v": "10", "l": "IPL finals", "c": "gold"}, "right": {"v": "2", "l": "Champions League T20 titles", "c": "gold"}, "sep": "&"}, pose="celebrate", fx=("vignette", "spot", "confetti"), fx_at=0.3),
    stage("Two hundred and thirty-five matches as IPL captain. One hundred and thirty-six wins.",
          {"kind": "versus", "kicker": "MS DHONI · IPL CAPTAIN", "left": {"v": "235", "l": "Matches", "c": "gold"}, "right": {"v": "136", "l": "Wins", "c": "gold"}, "sep": "→"}, pose="stand", cam="wide"),
    stage("And in the last two overs of an innings, no one in our data has hit more sixes: ninety-eight.",
          {"kind": "bignum", "kicker": "THE FINISHER", "label": "SIXES IN THE LAST TWO OVERS", "value": F["last2_most_sixes"]["first_val"], "count_dur": 0.7, "color": "gold", "note": "OUR DATA: IPL 2013-2026 · HE PLAYED 2013-2025"},
          pose="stance", view="side", cam="pull", stumps=[0.2, 0.93], ball={"at": 0.5, "shot": "six"}, fx=("vignette", "sparks")),
    stage("Thank you, MSD.", {"kind": "headline", "kicker": "THE THIRD MAN", "lines": [{"t": "THANK YOU,"}, {"t": "DHONI.", "c": "gold"}]}, pose="raise", fx=("vignette", "spot", "confetti"), fx_at=0.3),
    CTA_YT,
]
DESC_T = ("MS Dhoni has retired from the IPL as a player and becomes Chennai Super Kings' team mentor, CSK announced on 17 November 2026. His IPL in numbers: 278 matches, 5,439 runs, five titles as captain (2010, 2011, 2018, 2021, 2023), ten finals, "
          "two Champions League T20 titles, and 136 wins in 235 matches as captain. In our data (IPL 2013-2026), no one hit more sixes in the last two overs of an innings than his 98.\n\nSources: Eastern Eye, Khel Now, ETV Bharat, Cricketaddictor, Cricinfo records, Sportmonks ball-by-ball (our own analysis). Illustrated avatar, not a likeness.\n\n#MSDhoni #CSK #IPL #Shorts")
t_spec = {"slug": "dhoni_retires", "theme": "stadium", "captions": "v2", "series": "channel", "tag": "THE THIRD MAN", "tagsub": "DHONI RETIRES FROM THE IPL",
          "files": {"short": "x"}, "thumb": {"kicker": "CSK ANNOUNCE", "lines": [{"t": "DHONI RETIRES"}, {"t": "FROM THE IPL", "c": "gold"}], "hero": "5", "herosize": 640},
          "sources": SRC_COMMON, "venue": VENUE, "short": tribute, "long": [],
          "yt": {"short": {"title": "MS Dhoni Retires From the IPL: 5 Titles, 278 Matches | CSK #Shorts", "description": DESC_T, "tags": TAGS}}}
c_tribute.save(t_spec)

# ---------------------------------------------------------------- 2. Data Stories Ep 13
sr = lambda x: f"{x:.0f}"
story_long = [
    {"vo": "Two hundred and seventy-eight IPL matches. Five titles. MSD has retired, so we went through every ball he faced since twenty thirteen to see what made him MSD. And the answer is not in the first fifteen overs. It's in the last two.",
     "scene": {"type": "statement", "lines": [{"t": "278 MATCHES."}, {"t": "5 TITLES.", "c": "gold"}], "sub": "MS DHONI · IPL CAREER · OUR DATA: IPL 2013-2026 (HE PLAYED 2013-2025)"}},
    {"vo": "For fifteen overs, he was quieter than the league. A strike rate of eighty in the powerplay, and ninety-three in the middle overs, against one twenty-eight for everyone else. Then the game came to him.",
     "scene": {"type": "compare", "head": {"t": "OVERS 1 TO 15", "sub": "STRIKE RATE · OUR DATA: IPL 2013-2026"}, "a": {"name": "THE LEAGUE", "color": "ink"}, "b": {"name": "DHONI", "color": "gold"},
               "rows": [["POWERPLAY (OVERS 1-6)", sr(PH["powerplay"]["league_sr"]), sr(PH["powerplay"]["dhoni"]["sr"]), "a"], ["MIDDLE (OVERS 7-15)", sr(PH["middle"]["league_sr"]), sr(PH["middle"]["dhoni"]["sr"]), "a"]]}},
    {"vo": "From the sixteenth over, it flipped. One seventy-four, against one sixty for the league. One thousand, four hundred and seventy-five balls faced, more than anyone in our data. Two thousand, five hundred and seventy-three runs, more than anyone.",
     "scene": {"type": "stats", "head": {"t": "OVERS 16 TO 20", "sub": "STRIKE RATE · OUR DATA: IPL 2013-2026"}, "tiles": [{"v": sr(PH["death"]["dhoni"]["sr"]), "l": "DHONI", "c": "gold"}, {"v": sr(PH["death"]["league_sr"]), "l": "THE LEAGUE", "c": "ink"}, {"v": f'{F["death_most_runs"]["first_val"]:,}', "l": "RUNS, MOST IN OUR ARCHIVE", "c": "gold"}]}},
    {"vo": "And the last two overs? Those were his. One thousand, two hundred and seventy runs. Ninety-eight sixes. The next best has fifty-nine.",
     "scene": {"type": "bignum", "head": {"t": "THE LAST TWO OVERS"}, "value": F["last2_most_sixes"]["first_val"], "label": "SIXES, MORE THAN ANYONE", "color": "gold", "note": f'Next best: {F["last2_most_sixes"]["second_val"]} (Hardik Pandya) · our data: IPL 2013-2026'}},
    {"vo": "In the final over itself, he scored at two fifty-two. The rest of the league managed one eighty-two. That's not a finish. That's a signature.",
     "scene": {"type": "bars", "head": {"t": "THE 20TH OVER", "sub": "STRIKE RATE"}, "max": 270, "dec": 0, "items": [{"label": "LEAGUE", "value": O20["league_sr"], "text": sr(O20["league_sr"]), "color": "ink"}, {"label": "DHONI", "value": O20["dhoni"]["sr"], "text": sr(O20["dhoni"]["sr"]), "color": "gold"}]}},
    {"vo": "He kept doing it for a decade. Two hundred and three in twenty thirteen. Two hundred and one in twenty eighteen. In twenty twenty-three, the title year, one eighty-six. In twenty twenty-four, two twenty-one. And in twenty twenty-five, one fifty-two, below the league's one seventy-two.",
     "scene": {"type": "line", "head": {"t": "DEATH-OVER STRIKE RATE, SEASON BY SEASON", "sub": "DHONI VS THE LEAGUE · OVERS 16-20"}, "ymin": 120, "ymax": 230, "yticks": [120, 150, 180, 210], "ylabel": "STRIKE RATE",
               "xticks": [[2013, "2013"], [2016, "2016"], [2019, "2019"], [2022, "2022"], [2025, "2025"]],
               "series": [{"name": "DHONI", "color": "gold", "at": 0.1, "dur": 0.75, "points": [[y, SEAS[y]["death_sr"]] for y in sorted(SEAS)]},
                          {"name": "LEAGUE", "color": "ink", "at": 0.1, "dur": 0.75, "points": [[y, SEAS[y]["league_death_sr"]] for y in sorted(SEAS)]}]}},
    {"vo": "Our verdict? MSD was never an accumulator. He built slowly, and then no one in our data scored more in the last two overs. Five titles. Two hundred and seventy-eight matches. One job: finish.",
     "scene": {"type": "statement", "kicker": "OUR VERDICT", "lines": [{"t": "A SLOW BUILD."}, {"t": "THEN NO ONE", "c": "gold"}, {"t": "SCORED MORE.", "c": "gold"}]}},
    {"vo": "Thank you, MSD. Is he the greatest finisher in IPL history? Tell us in the comments, and subscribe for more data stories.",
     "scene": {"type": "cta", "lines": [{"t": "THANK YOU,"}, {"t": "MSD.", "c": "gold"}], "pill": "THE GREATEST FINISHER? TELL US BELOW"}},
]
story_short = [
    {"vo": "Ninety-eight sixes in the last two overs of an innings. More than anyone in our data. That is MSD.",
     "scene": {"type": "lab_big", "title": "", "value": F["last2_most_sixes"]["first_val"], "dec": 0, "label": "Sixes in the last two overs", "color": "red", "count_dur": 0.8, "kicker": "MS Dhoni · our data: IPL 2013-2026"}},
    {"vo": "In overs sixteen to twenty, one seventy-four, against one sixty for the league.",
     "scene": {"type": "lab_vs", "kicker": "THE NUMBERS", "title": "Strike rate, overs 16-20.", "items": [{"label": "League", "v": PH["death"]["league_sr"], "text": sr(PH["death"]["league_sr"]), "c": "ink", "at": 0.1}, {"label": "Dhoni", "v": PH["death"]["dhoni"]["sr"], "text": sr(PH["death"]["dhoni"]["sr"]), "c": "red", "at": 0.4}], "max": 200}},
    {"vo": "And in the final over, two fifty-two.",
     "scene": {"type": "lab_big", "title": "", "value": r(O20["dhoni"]["sr"]), "dec": 0, "label": "20th-over strike rate", "color": "red", "count_dur": 0.7, "kicker": f'The league: {r(O20["league_sr"])}'}},
    {"vo": "Quieter than the league for fifteen overs. Then, no one scored more. Thank you, MSD.",
     "scene": {"type": "lab_big_text", "lines": ["QUIET START.", "[NO ONE]", "[SCORED MORE.]"]}},
    {"vo": YT_CTA["vo"], "scene": YT_CTA["scene"]},
]
DESC_S_ = ("MS Dhoni's IPL, in numbers: 98 sixes in the last two overs of an innings (more than anyone in our data), a death-overs strike rate of 174 against 160 for the league, and 252 in the 20th over. A slow start, then no one scored more. Full breakdown on the channel.\n\n"
           "In our archive: Sportmonks ball-by-ball, IPL 2013-2026 (MSD played 2013-2025), overs 16-20, super overs excluded.\n\n#MSDhoni #CSK #IPL #Shorts")
DESC_L_ = ("MS Dhoni's IPL in numbers: we went through every ball he faced in the IPL since 2013. For fifteen overs he was slower than the league (strike rate 80 in the powerplay, 93 in overs 7-15, against 128). Then from the 16th over: 174 against 160, "
           "across 1,475 balls and 2,573 runs, both more than anyone in our archive. In the last two overs, 1,270 runs and 98 sixes (next best: 59). In the 20th over, a strike rate of 252 against 182 for the league. A slow build, then no one scored more.\n\n"
           "Career: 278 IPL matches, 5,439 runs, five titles as captain (2010, 2011, 2018, 2021, 2023). CSK announced his retirement from the IPL as a player on 17 November 2026; he becomes team mentor.\n\n"
           "Method: Sportmonks ball-by-ball, every IPL match 2013-2026 (2008-2012 are not in our data; MSD played 2013-2025 within it), super overs excluded; death overs = 16-20. All archive figures are 'in our archive'. Career totals: Eastern Eye, Khel Now, ETV Bharat, Cricketaddictor.\n\n#MSDhoni #CSK #IPL #DataStory")
carousel = {"cover": {"kicker": "MS DHONI · IPL", "lines": [{"t": "THE FINISHER"}, {"t": "IN NUMBERS", "c": "gold"}], "hero": "98"}, "slides": [["long", 0], ["long", 1], ["long", 2], ["long", 3], ["long", 4], ["long", 5]],
            "cta": {"lines": [{"t": "THE GREATEST"}, {"t": "FINISHER?", "c": "gold"}], "pill": "FULL BREAKDOWN ON YOUTUBE · LINK IN BIO"},
            "caption": ("MS Dhoni has retired from the IPL. 💛\n\nWe went through every ball he faced since 2013. For 15 overs he was slower than the league. From the 16th over: 174 against 160. In the last two overs: 1,270 runs and 98 sixes, more than anyone in our data.\n\nSwipe through the numbers ➡️ Full breakdown on YouTube (link in bio).\n\n"
                        "Data: Sportmonks ball-by-ball, IPL 2013-2026 (MSD played 2013-2025), in our archive.\n\n#MSDhoni #Dhoni #CSK #ChennaiSuperKings #IPL #IPL2027 #cricket #cricketanalysis #TheThirdMan")}

# ---- the vertical long version for Instagram (variants.py igfull): the whole long narration in 9:16 stage scenes (CSK avatar, tribute energy), then its own end card
def full_scene(i, panel, pose="stand", cam="push", fx=("vignette", "spot"), **kw):
    sc = {"type": "stage", "panel": dict(panel, at=0.05), "avatars": [{"kit": "CSK", "pose": pose, "x": 0.5}], "cam": cam, "fx": list(fx)}; sc.update(kw)
    return {"vo": story_long[i]["vo"], "scene": sc}
G_ = lambda v, l, c="gold": {"v": v, "l": l, "c": c}
T_ = lambda kick, rows: {"kind": "table", "kicker": kick, "rows": rows}
SIDE_ = dict(view="side", stumps=[0.2, 0.93])
full = [
    full_scene(0, {"kind": "versus", "kicker": "MS DHONI · IPL · OUR DATA: 2013-2026", "left": G_("278", "Matches"), "right": G_("5", "Titles"), "sep": "&"}, pose="raise", cam="push", fx=("vignette", "spot", "confetti"), fx_at=0.3),
    full_scene(1, T_("OVERS 1-15 · STRIKE RATE · DHONI VS THE LEAGUE", [["Powerplay (overs 1-6)", f'{sr(PH["powerplay"]["dhoni"]["sr"])} vs {sr(PH["powerplay"]["league_sr"])}'], ["Middle overs (7-15)", f'{sr(PH["middle"]["dhoni"]["sr"])} vs {sr(PH["middle"]["league_sr"])}']]),
               pose="stance", cam="wide", fx=("vignette", "spot"), **SIDE_),
    full_scene(2, T_("OVERS 16-20 · THE FLIP", [["Dhoni, strike rate", sr(PH["death"]["dhoni"]["sr"]), "gold"], ["The league, strike rate", sr(PH["death"]["league_sr"])], ["Balls faced (most in our data)", f'{PH["death"]["dhoni"]["balls"]:,}'], ["Runs (most in our data)", f'{F["death_most_runs"]["first_val"]:,}', "gold"]]),
               pose="loft", hit="loft", ghost=True, cam="pull", ball={"at": 0.5, "shot": "six"}, fx=("vignette", "shake", "sparks"), **SIDE_),
    full_scene(3, {"kind": "bignum", "kicker": "THE LAST TWO OVERS", "label": "SIXES · NEXT BEST: 59", "value": F["last2_most_sixes"]["first_val"], "count_dur": 0.8, "color": "gold", "note": "OUR DATA: IPL 2013-2026"},
               pose="loft", hit="loft", ghost=True, cam="push", ball={"at": 0.5, "shot": "six"}, fx=("vignette", "flash", "sparks", "confetti"), fx_at=0.5, **SIDE_),
    full_scene(4, {"kind": "versus", "kicker": "THE 20TH OVER · STRIKE RATE", "left": G_(sr(O20["dhoni"]["sr"]), "Dhoni"), "right": G_(sr(O20["league_sr"]), "The league", "white"), "sep": "vs"},
               pose="drive", hit="drive", ghost=True, cam="drift", ball={"at": 0.5, "shot": "four"}, fx=("vignette", "speed", "flash"), **SIDE_),
    full_scene(5, T_("DEATH-OVER STRIKE RATE · DHONI VS THE LEAGUE", [[str(y), f'{sr(SEAS[y]["death_sr"])} vs {sr(SEAS[y]["league_death_sr"])}'] + (["gold"] if y in (2013, 2018, 2023, 2024) else []) for y in (2013, 2018, 2023, 2024, 2025)]),
               pose="walk", cam="drift", fx=("vignette", "spot")),
    full_scene(6, {"kind": "headline", "kicker": "OUR VERDICT", "lines": [{"t": "A SLOW BUILD."}, {"t": "THEN NO ONE", "c": "gold"}, {"t": "SCORED MORE.", "c": "gold"}]}, pose="celebrate", cam="wide", fx=("vignette", "spot", "confetti"), fx_at=0.4),
]
reel_cta = {"vo": "Thank you, MSD. Is he the greatest finisher in IPL history? Tell us in the comments. For the full data story, follow The Third Man on YouTube. Link in bio.",
            "scene": {"type": "cta", "lines": [{"t": "THANK YOU,"}, {"t": "MSD.", "c": "gold"}], "yt": {"label": "THE THIRD MAN", "handle": "YOUTUBE @thethirdman_angle", "bio": "LINK IN BIO"}}}
reel_caption = ("MS Dhoni has retired from the IPL, and the numbers say what the highlights always did. 💛\n\nFor 15 overs he was quieter than the league. From the 16th over: 174 against 160. In the last two overs: 1,270 runs and 98 sixes, more than anyone in our data. In the final over, 252 against 182.\n\n"
                "Thank you, MSD. Is he the greatest finisher in IPL history? Tell us below.\n\nFull data story on YouTube: The Third Man (@thethirdman_angle). Link in bio.\n\nData: Sportmonks ball-by-ball, IPL 2013-2026 (he played 2013-2025), in our archive.\n\n"
                "#MSDhoni #Dhoni #CSK #ChennaiSuperKings #IPL #IPL2027 #cricket #cricketanalysis #TheThirdMan")
s_spec = {"slug": "dhoni_ipl_story", "theme": "lab", "theme_long": "whites", "captions": "lab", "captions_long": False, "series": "data", "tag": "DATA STORY", "tagsub": "DHONI'S IPL IN NUMBERS",
          "files": {"long": "x", "short": "x"}, "thumb": {"kicker": "MS DHONI · IPL", "lines": [{"t": "THE FINISHER"}, {"t": "IN NUMBERS", "c": "gold"}], "hero": "98", "herosize": 520},
          "ig_cover": {"lines": [{"t": "DHONI'S IPL:"}, {"t": "THE FINISHER", "c": "gold"}], "sub": "BY THE NUMBERS", "hero": "98"}, "sources": SRC_COMMON, "venue": VENUE, "long": story_long, "short": story_short, "carousel": carousel, "full": full, "full_theme": "stadium", "full_captions": "v2", "reel_cta": reel_cta, "reel_caption": reel_caption,
          "yt": {"long": {"title": "MS Dhoni IPL Career: How He Finished, in Numbers | Data Story Ep 13", "description": DESC_L_, "tags": TAGS},
                 "short": {"title": "Dhoni: 98 Sixes in the Last Two Overs | Data Story Ep 13 #Shorts", "description": DESC_S_, "tags": TAGS}}}
c_story.save(s_spec)

# ---------------------------------------------------------------- 3. Myth or Data Ep 4
D = "twenty thirteen to fifteen, twenty eighteen to twenty twenty-one, and twenty twenty-three"
myth_long = [
    {"vo": "MSD. Five titles, ten finals. But some say चेन्नई just won the close ones. Is that true?",
     "scene": {"type": "lab_title", "kicker": "MYTH OR DATA? · EP. 4", "lines": ["Dhoni's CSK:", "[just lucky?]"], "teaser": "IPL captaincy · 2013-2023"}},
    {"vo": "He captained two hundred and thirty-five IPL matches, and won one hundred and thirty-six. Five titles, level with रोहित शर्मा as the most by any captain. Ten finals. And two Champions League titles.",
     "scene": {"type": "lab_big", "kicker": "MS DHONI · IPL CAPTAIN", "title": "A decade of winning.", "value": 136, "label": "wins in 235 matches as captain · five titles, ten finals", "color": "red"}},
    {"vo": f"The myth: चेन्नई got through on nail-biters. So we looked at every decided CSK match in the eight seasons he was captain: {D}. In our archive.",
     "scene": {"type": "lab_big_text", "kicker": "THE MYTH · OUR DATA: IPL 2013-2026", "lines": ["CSK just won", "[the close ones.]"]}},
    {"vo": "A close finish is ten runs or fewer, or two wickets or fewer. There were sixteen. चेन्नई won nine. Fifty-six percent, not far from a coin flip. In every other match, they won sixty-three percent.",
     "scene": {"type": "lab_compare", "kicker": "CSK · EIGHT SEASONS · OUR DATA: IPL 2013-2026", "title": "Close games: nothing special.", "a": {"t": "CSK", "kit": "CSK", "name": "CLOSE FINISHES"}, "b": {"t": "CSK", "kit": "CSK", "name": "EVERY OTHER MATCH"},
               "rows": [["Matches", str(CS["tight"]), str(CS["rest"]), "level"], ["Won", str(CS["tight_won"]), str(CS["rest_won"]), "level"], ["Win rate", f'{pct(CS["tight_won"], CS["tight"])}%', f'{pct(CS["rest_won"], CS["rest"])}%', "b"]]}},
    {"vo": "Across all one hundred and twenty-nine decided matches, चेन्नई won eighty. Sixty-two percent. The best of any franchise that played all eight seasons, ahead of मुंबई at fifty-nine.",
     "scene": {"type": "lab_dots", "kicker": "WIN RATE · THE SAME EIGHT SEASONS · OUR DATA: IPL 2013-2026", "title": "The best record in the league.", "domain": [30, 70], "ticks": [30, 50, 70], "tick_labels": False,
               "rows": [{"label": n, "v": RANK[k]["pct"], "text": f'{round(RANK[k]["pct"])}%', **({"hl": True} if k == "Chennai Super Kings" else {})} for n, k in
                        (("Chennai", "Chennai Super Kings"), ("Mumbai", "Mumbai Indians"), ("Kolkata", "Kolkata Knight Riders"), ("Bengaluru", "Royal Challengers Bengaluru"), ("Rajasthan", "Rajasthan Royals"), ("Hyderabad", "Sunrisers Hyderabad"), ("Punjab", "Punjab Kings"), ("Delhi", "Delhi Capitals"))]}},
    {"vo": "So, did चेन्नई just win the close ones? Our verdict: busted. They won those about as often as a coin lands heads, and everything else far more. The wins came from everywhere, not from a few lucky finishes.",
     "scene": {"type": "lab_big_text", "kicker": "THE VERDICT", "lines": ["Not luck.", "[Just wins.]"]}},
    {"vo": "Is MSD the greatest IPL captain? Tell us in the comments, and follow for more Myth or Data.",
     "scene": {"type": "cta", "lines": [{"t": "THE GREATEST"}, {"t": "IPL CAPTAIN?", "c": "gold"}], "pill": "SUBSCRIBE FOR MORE"}},
]
myth_short = [
    stage("The story goes that MSD's चेन्नई just got lucky in close finishes. We checked every one.",
          {"kind": "headline", "kicker": "MYTH OR DATA? · EP. 4", "lines": [{"t": "DHONI'S CSK:"}, {"t": "JUST LUCKY?", "c": "gold"}]}, pose="stand"),
    stage("In close finishes, ten runs or fewer, or two wickets or fewer, they won nine of sixteen. Fifty-six percent. In every other match, sixty-three.",
          {"kind": "versus", "kicker": "CSK · OUR DATA: IPL 2013-2026", "left": {"v": "56%", "l": "Close finishes (9 of 16)", "c": "gold"}, "right": {"v": "63%", "l": "Every other match", "c": "gold"}, "sep": "vs"}, pose="stance", cam="pull"),
    stage("Overall, sixty-two percent of decided matches. The best of any franchise across those eight seasons.",
          {"kind": "bignum", "kicker": "THE EIGHT SEASONS HE LED", "label": "WIN RATE (%), ALL DECIDED MATCHES", "value": 62, "count_dur": 0.7, "color": "gold", "note": "Mumbai Indians: 59% · our data: IPL 2013-2026"}, pose="raise", fx=("vignette", "spot", "confetti"), fx_at=0.4),
    stage("Not luck. Just wins. Our verdict: busted.", {"kind": "verdict", "verdict": "busted"}, pose="arms_wide", cam="wide", fx=("vignette", "spot", "confetti"), fx_at=0.5),
    CTA_YT,
]
DESC_ML = ("MS Dhoni's Chennai Super Kings won five IPL titles and played ten finals. Did CSK just win the close ones? We checked every decided match in the eight seasons he was captain (2013, 2014, 2015, 2018, 2019, 2020, 2021, 2023, in our archive): "
           "in close finishes (10 runs or fewer, or 2 wickets or fewer) CSK won 9 of 16 (56%); in every other match 71 of 113 (63%). Overall 80 of 129 decided matches, 62%, the best of any franchise across those seasons (Mumbai Indians 59%). Verdict: busted.\n\n"
           "Captaincy: 235 IPL matches, 136 wins, 97 losses, 2 no results (CSK and Rising Pune Supergiant); five titles, level with Rohit Sharma as the most by a captain. CSK announced his retirement from the IPL as a player on 17 November 2026.\n\n"
           "Method: Sportmonks ball-by-ball and results, IPL 2013-2026; seasons attributed to him as captain (2016-17 CSK were suspended; 2022, 2024 and 2025 had other captains for part or all of the season, so are left out); super overs excluded.\n\n#MSDhoni #CSK #IPL #MythOrData")
DESC_MS = ("Did Dhoni's CSK just win the close ones? In close finishes they won 9 of 16 (56%); in every other match, 63%. Overall 62% of decided matches in the eight seasons he captained them, the best in the league. Verdict: busted. Full breakdown on the channel.\n\nIn our archive: Sportmonks ball-by-ball and results, IPL 2013-2025.\n\n#MSDhoni #CSK #MythOrData #Shorts")
m_spec = {"slug": "dhoni_captain_myth", "theme": "stadium", "theme_long": "lab", "captions": "v2", "captions_long": False, "series": "myth", "tag": "MYTH OR DATA?", "tagsub": "EP. 4 · DHONI'S CSK",
          "files": {"long": "x", "short": "x"}, "thumb": {"kicker": "MYTH OR DATA? · EP. 4", "lines": [{"t": "DHONI'S CSK:"}, {"t": "JUST LUCKY?", "c": "gold"}], "hero": "62%", "herosize": 420},
          "sources": SRC_COMMON, "venue": VENUE, "long": myth_long, "short": myth_short,
          "yt": {"long": {"title": "MS Dhoni: Did CSK Just Win the Close Ones? | Myth or Data Ep 4", "description": DESC_ML, "tags": TAGS},
                 "short": {"title": "MS Dhoni: Did CSK Just Win the Close Ones? | Myth or Data Ep 4 #Shorts", "description": DESC_MS, "tags": TAGS}}}
c_myth.save(m_spec)

for sp in (t_spec, s_spec, m_spec):
    voice_lint.fix_spec(sp)
    sp["files"].setdefault("long", "_unused")          # Short-only spec: engine.thumb() still wants a long name (files starting _unused are deleted after the build)
    json.dump(sp, open(f"specs/{sp['slug']}.json", "w"), ensure_ascii=False, indent=1)
    print("wrote specs/%s.json" % sp["slug"], voice_lint.check_spec(sp, ("long", "short")) or "voice lint clean")
