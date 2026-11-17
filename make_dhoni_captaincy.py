"""Builds specs/dhoni_captaincy_all.json: Data Stories Ep14, "MSD's IPL captaincy, the complete record" (long + Short), on ALL IPL data (every season 2008-2025), not just the Sportmonks 2013+ window.
Numbers and how each is checked (dataops/verify.py):
  - Captaincy totals (235 matches, 136 wins, 97 losses, 2 no-results; CSK + Rising Pune Supergiant): Wikipedia 'List of Indian Premier League captains' (page edited 19 Sep 2026, read 17 Nov 2026), Cricketaddictor, Insidesport;
    the owner also supplied the Cricinfo records page (not readable by us). Five titles level with Rohit Sharma: Wikipedia + India TV. 'Most matches and most wins as captain': Wikipedia's table + myKhel (May 2023 table, same ranking).
  - CSK results per season 2008-2025: Wikipedia's CSK season table and the Cricsheet IPL archive agree on wins in every season; Cricsheet is short of a few abandoned matches (2008: 58 of 59 matches, 2009: 57 of 59, 2010 and 2012 one each),
    so only WINS, finals, titles and playoff seasons are stated per season, never losses.
  - Franchise comparison (playoff seasons, finals, win rate on decided matches): Cricsheet IPL archive, all seasons 2008-2025, shown as 'OUR DATA'. MI: six finals / five titles also in myKhel.
  - 2026: Dhoni did not play, CSK finished outside the playoffs; the video's window is 2008-2025.
Win rate is quoted on decided matches (wins / (wins + losses)) for every franchise. Dhoni's own record is 'won 136 of 235' (no percentage: 57.87% counts no-results as matches, 58.37% does not)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voice_lint
from dataops import verify as V
from variants import YT_CTA

F = json.load(open("data/provenance/dhoni_captaincy_all_figures.json"))
FR = F["franchises"]; CSK_S = {int(k): v for k, v in F["csk_by_season"].items()}; CSK, MI = FR["Chennai Super Kings"], FR["Mumbai Indians"]
WIKI_W = {2008: 9, 2009: 8, 2010: 9, 2011: 11, 2012: 10, 2013: 12, 2014: 10, 2015: 10, 2018: 11, 2019: 10, 2020: 6, 2021: 11, 2022: 4, 2023: 10, 2024: 7, 2025: 4}      # Wikipedia, Chennai Super Kings season table
CRICSHEET_W = {y: CSK_S[y]["W"] for y in WIKI_W}
WP, ITV, CA, IS, MK, CS, ETV = "wikipedia", "indiatv", "cricketaddictor", "insidesport", "mykhel", "cricsheet", "etvbharat"

c = V.Claims("dhoni_captaincy_all")
c.check("matches as IPL captain (CSK + Rising Pune Supergiant)", 235, {WP: 235, CA: 235, IS: 235})
c.check("wins as IPL captain", 136, {WP: 136, CA: 136, IS: 136})
c.check("most matches as IPL captain: MS Dhoni", "Dhoni", {WP: "Dhoni", MK: "Dhoni"})
c.check("most wins as IPL captain: MS Dhoni", "Dhoni", {WP: "Dhoni", MK: "Dhoni"})
c.check("titles as captain", 5, {WP: 5, CA: 5, ETV: 5})
c.check("five titles level with Rohit Sharma", "joint-most", {WP: "joint-most", ITV: "joint-most"})
c.check("IPL seasons with CSK (2008-2015, 2018-2025)", 16, {WP: 16, CS: len(CSK["seasons"])})
c.check("CSK finals", 10, {ETV: 10, CA: 10, CS: CSK["finals"]})
c.check("CSK titles", 5, {ETV: 5, CA: 5, CS: CSK["titles"]})
c.check("CSK playoff seasons (2008-15, 2018, 2019, 2021, 2023)", 12, {WP: 12, CS: CSK["playoff_seasons"]})
for y in (2008, 2011, 2013, 2018, 2022, 2024, 2025): c.check(f"CSK wins {y}", WIKI_W[y], {WP: WIKI_W[y], CS: CRICSHEET_W[y]})
c.check("MI finals", 6, {MK: 6, CS: MI["finals"]})
c.check("MI titles", 5, {MK: 5, CS: MI["titles"]})
c.check("archive: MI playoff seasons", MI["playoff_seasons"], {CS: MI["playoff_seasons"]}, scope="archive")
c.check("archive: MI seasons", MI["n_seasons"], {CS: MI["n_seasons"]}, scope="archive")
c.check("archive: CSK win rate on decided matches (%)", round(CSK["win_pct"]), {CS: round(CSK["win_pct"])}, scope="archive")
c.check("archive: MI win rate on decided matches (%)", round(MI["win_pct"]), {CS: round(MI["win_pct"])}, scope="archive")
assert CSK["finals"] == max(v["finals"] for v in FR.values()) and CSK["win_pct"] == max(v["win_pct"] for v in FR.values() if v["decided"] >= 100)
assert CSK["playoff_seasons"] == 12 and MI["playoff_seasons"] == 11 and MI["n_seasons"] == 18, (CSK, MI)
others = [v["win_pct"] for k, v in FR.items() if k not in ("Chennai Super Kings", "Mumbai Indians") and v["decided"] >= 100]
assert max(others) < 53, others               # "everyone else is at fifty-two or below"
assert c.summary().get("UNVERIFIED", 0) == 0 and c.summary().get("CONFLICT", 0) == 0, c.summary()

DATA = "OUR DATA: EVERY IPL SEASON, 2008-2025"
pc = lambda x: f"{round(x)}%"
TEAMS = (("CSK", "Chennai Super Kings", "gold"), ("MI", "Mumbai Indians", "ink"), ("KKR", "Kolkata Knight Riders", "ink"), ("RCB", "Royal Challengers Bengaluru", "ink"), ("RR", "Rajasthan Royals", "ink"),
         ("SRH", "Sunrisers Hyderabad", "ink"), ("PBKS", "Punjab Kings", "ink"), ("DC", "Delhi Capitals", "ink"))
long = [
    {"vo": "Two hundred and thirty-five matches as an IPL captain. One hundred and thirty-six wins. No captain in IPL history has won more. This is MSD's captaincy, across every season, from the very first one.",
     "scene": {"type": "statement", "lines": [{"t": "235 MATCHES."}, {"t": "136 WINS.", "c": "gold"}], "sub": f"MS DHONI · IPL CAPTAIN · {DATA}"}},
    {"vo": "Sixteen seasons with चेन्नई, and look at the shape. Nine wins in the first season. Eleven in twenty eleven. Twelve in twenty thirteen. Then two suspended years, and the comeback: eleven wins and a title in twenty eighteen. A fifth title in twenty twenty-three. And the final seasons were harder: four wins, seven, and four.",
     "scene": {"type": "line", "head": {"t": "CSK WINS, SEASON BY SEASON", "sub": f"SUSPENDED 2016-17 · {DATA}"}, "ymin": 0, "ymax": 14, "yticks": [0, 4, 8, 12], "ylabel": "WINS",
               "xticks": [[2008, "2008"], [2012, "2012"], [2016, "2016"], [2020, "2020"], [2025, "2025"]],
               "series": [{"name": "CSK", "color": "gold", "at": 0.1, "dur": 0.8, "points": [[y, CSK_S[y]["W"]] for y in sorted(CSK_S) if y <= 2025]}]}},
    {"vo": "Ten finals in sixteen seasons. No franchise has played more. Five titles.",
     "scene": {"type": "bignum", "head": {"t": "CSK IN THE FINAL"}, "value": 10, "label": "FINALS IN 16 SEASONS · 5 TITLES", "color": "gold", "note": DATA}},
    {"vo": "Put चेन्नई next to the next best franchise, मुंबई. Playoffs: twelve seasons out of sixteen, against eleven out of eighteen. Finals: ten against six. And titles: five each.",
     "scene": {"type": "compare", "head": {"t": "CSK VS MUMBAI", "sub": DATA}, "a": {"name": "MUMBAI", "color": "ink"}, "b": {"name": "CSK", "color": "gold"},
               "rows": [["PLAYOFF SEASONS", f'{MI["playoff_seasons"]} of {MI["n_seasons"]}', f'{CSK["playoff_seasons"]} of {CSK["n_seasons"]}', "b"], ["FINALS", str(MI["finals"]), str(CSK["finals"]), "b"], ["TITLES", str(MI["titles"]), str(CSK["titles"]), "level"]]}},
    {"vo": "Across all eighteen seasons, चेन्नई won more of their decided matches than any franchise. Fifty-seven percent. मुंबई, fifty-five. Everyone else, at fifty-two or below.",
     "scene": {"type": "bars", "head": {"t": "WIN RATE, DECIDED MATCHES", "sub": DATA}, "max": 60, "dec": 0, "suffix": "%",
               "items": [{"label": ab, "value": FR[nm]["win_pct"], "text": pc(FR[nm]["win_pct"]), "color": col} for ab, nm, col in TEAMS]}},
    {"vo": "So here is the record. Two hundred and thirty-five matches. One hundred and thirty-six wins. Five titles, level with रोहित शर्मा. And a captain who came back in twenty twenty-five, when his team needed him.",
     "scene": {"type": "stats", "head": {"t": "MS DHONI · IPL CAPTAIN", "sub": "CSK AND RISING PUNE SUPERGIANT"}, "tiles": [{"v": "235", "l": "MATCHES", "c": "ink"}, {"v": "136", "l": "WINS", "c": "gold"}, {"v": "5", "l": "TITLES", "c": "gold"}]}},
    {"vo": "Our verdict? The most successful captain in IPL history. The most matches, the most wins, and ten finals. Thank you, MSD.",
     "scene": {"type": "statement", "kicker": "OUR VERDICT", "lines": [{"t": "THE MOST SUCCESSFUL"}, {"t": "CAPTAIN IN", "c": "gold"}, {"t": "IPL HISTORY.", "c": "gold"}]}},
    {"vo": "Who is the greatest IPL captain? Tell us in the comments, and subscribe for more data stories.",
     "scene": {"type": "cta", "lines": [{"t": "THANK YOU,"}, {"t": "MSD.", "c": "gold"}], "pill": "THE GREATEST IPL CAPTAIN? TELL US BELOW"}},
]
short = [
    {"vo": "One hundred and thirty-six wins as an IPL captain. No one has won more. That is MSD.",
     "scene": {"type": "lab_big", "title": "", "value": 136, "dec": 0, "label": "Wins as an IPL captain", "color": "red", "count_dur": 0.8, "kicker": "MS Dhoni · every IPL season"}},
    {"vo": "Ten finals in sixteen seasons. Five titles.",
     "scene": {"type": "lab_big", "title": "", "value": 10, "dec": 0, "label": "Finals in 16 seasons", "color": "red", "count_dur": 0.7, "kicker": "Five titles · our data: 2008-2025"}},
    {"vo": "Twelve playoff seasons out of sixteen. Mumbai, eleven out of eighteen.",
     "scene": {"type": "lab_vs", "kicker": "THE NUMBERS", "title": "Seasons in the playoffs.", "items": [{"label": "Mumbai (11 of 18)", "v": 100 * MI["playoff_seasons"] / MI["n_seasons"], "text": pc(100 * MI["playoff_seasons"] / MI["n_seasons"]), "c": "ink", "at": 0.1},
                                                                                                                  {"label": "CSK (12 of 16)", "v": 100 * CSK["playoff_seasons"] / CSK["n_seasons"], "text": pc(100 * CSK["playoff_seasons"] / CSK["n_seasons"]), "c": "red", "at": 0.4}], "max": 100}},
    {"vo": "The most successful captain in IPL history. Thank you, MSD.",
     "scene": {"type": "lab_big_text", "lines": ["THE MOST", "[SUCCESSFUL CAPTAIN]", "[IN IPL HISTORY.]"]}},
    {"vo": YT_CTA["vo"], "scene": YT_CTA["scene"]},
]

# ---- vertical full version for Instagram (variants.py igfull): the whole long narration in 9:16 stage scenes (CSK avatar, tribute energy), then its own end card
VENUE = {"time": "night", "crowd": [[250, 200, 20], [240, 240, 240], [25, 100, 200], [20, 60, 140]], "boards": [[250, 200, 20], [25, 100, 200]]}
def full_scene(i, panel, pose="stand", cam="push", fx=("vignette", "spot"), **kw):
    sc = {"type": "stage", "panel": dict(panel, at=0.05), "avatars": [{"kit": "CSK", "pose": pose, "x": 0.5}], "cam": cam, "fx": list(fx)}; sc.update(kw)
    return {"vo": long[i]["vo"], "scene": sc}
G_ = lambda v, l, c="gold": {"v": v, "l": l, "c": c}
T_ = lambda kick, rows: {"kind": "table", "kicker": kick, "rows": rows}
SIDE_ = dict(view="side", stumps=[0.2, 0.93])
full = [
    full_scene(0, {"kind": "versus", "kicker": "IPL CAPTAIN · OUR DATA 2008-2025", "left": G_("235", "Matches"), "right": G_("136", "Wins"), "sep": "→"}, pose="raise", cam="push", fx=("vignette", "spot", "confetti"), fx_at=0.3),
    full_scene(1, T_("CSK WINS PER SEASON · NONE 2016-17", [["2008, the first season", str(WIKI_W[2008])], ["2011 (title)", str(WIKI_W[2011]), "gold"], ["2013", str(WIKI_W[2013])], ["2018 (title)", str(WIKI_W[2018]), "gold"], ["2023 (title)", str(WIKI_W[2023]), "gold"], ["2022 / 2024 / 2025", f"{WIKI_W[2022]} / {WIKI_W[2024]} / {WIKI_W[2025]}"]]),
               pose="walk", cam="drift", fx=("vignette", "spot")),
    full_scene(2, {"kind": "bignum", "kicker": "CSK FINALS · OUR DATA 2008-2025", "label": "FINALS IN 16 SEASONS · 5 TITLES", "value": 10, "count_dur": 0.8, "color": "gold"},
               pose="celebrate", cam="push", fx=("vignette", "spot", "confetti"), fx_at=0.4),
    full_scene(3, T_("CSK VS MUMBAI · OUR DATA 2008-25", [["Playoff seasons", f'{CSK["playoff_seasons"]} of {CSK["n_seasons"]} vs {MI["playoff_seasons"]} of {MI["n_seasons"]}', "gold"], ["Finals", f'{CSK["finals"]} vs {MI["finals"]}', "gold"], ["Titles", f'{CSK["titles"]} vs {MI["titles"]}']]),
               pose="stance", cam="pull", fx=("vignette", "spot"), **SIDE_),
    full_scene(4, T_("WIN RATE · OUR DATA 2008-2025", [["Chennai (CSK)", pc(CSK["win_pct"]), "gold"], ["Mumbai", pc(MI["win_pct"])], ["Kolkata", pc(FR["Kolkata Knight Riders"]["win_pct"])], ["Everyone else", "50% or below"]]),
               pose="drive", hit="drive", ghost=True, cam="drift", ball={"at": 0.5, "shot": "four"}, fx=("vignette", "speed", "flash"), **SIDE_),
    full_scene(5, {"kind": "versus", "kicker": "MS DHONI · CSK + RISING PUNE SUPERGIANT", "left": G_("136", "Wins"), "right": G_("5", "Titles"), "sep": "&"}, pose="raise", cam="push", fx=("vignette", "spot", "confetti"), fx_at=0.4),
    full_scene(6, {"kind": "headline", "kicker": "OUR VERDICT", "lines": [{"t": "THE MOST SUCCESSFUL"}, {"t": "CAPTAIN IN", "c": "gold"}, {"t": "IPL HISTORY.", "c": "gold"}]}, pose="celebrate", cam="wide", fx=("vignette", "spot", "confetti"), fx_at=0.4),
]
reel_cta = {"vo": "Thank you, MSD. Who is the greatest IPL captain? Tell us in the comments. For the full data story, follow The Third Man on YouTube. Link in bio.",
            "scene": {"type": "cta", "lines": [{"t": "THANK YOU,"}, {"t": "MSD.", "c": "gold"}], "yt": {"label": "THE THIRD MAN", "handle": "YOUTUBE @thethirdman_angle", "bio": "LINK IN BIO"}}}
reel_caption = ("MS Dhoni's IPL captaincy, every season. 💛\n\n235 matches as captain. 136 wins, more than any captain in IPL history. Ten finals in sixteen seasons with CSK, five titles, and the playoffs in 12 of those 16 seasons. Against Mumbai, the next best franchise: 12 of 16 playoff seasons vs 11 of 18, finals 10 vs 6.\n\n"
                "Thank you, MSD. Who is the greatest IPL captain? Tell us below.\n\nFull data story on YouTube: The Third Man (@thethirdman_angle). Link in bio.\n\nOur data: every IPL season 2008-2025.\n\n"
                "#MSDhoni #Dhoni #CSK #ChennaiSuperKings #IPL #IPL2027 #IPLCaptains #cricket #cricketanalysis #TheThirdMan")
SRC = ["Captaincy totals (235 matches, 136 wins, 97 losses, 2 no results, CSK and Rising Pune Supergiant): Wikipedia, 'List of Indian Premier League captains' https://en.wikipedia.org/wiki/List_of_Indian_Premier_League_captains (page last edited 19 September 2026), Cricketaddictor https://cricketaddictor.com/cricket-news/ms-dhonis-record-as-ipl-captain-full-batting-stats-and-key-numbers-after-retirement-466132/ and Insidesport; ESPNcricinfo's records page (supplied by the channel owner) could not be opened by us. Five titles level with Rohit Sharma: Wikipedia and India TV.",
       "CSK season results 2008-2025: Wikipedia, 'Chennai Super Kings' season table https://en.wikipedia.org/wiki/Chennai_Super_Kings and the Cricsheet IPL ball-by-ball archive https://cricsheet.org/downloads/ipl_json.zip (wins agree in every season; Cricsheet lacks a few abandoned matches, so we state wins, finals, titles and playoff seasons, not losses).",
       "Franchise comparison (playoff seasons, finals, titles, win rate on decided matches), every IPL season 2008-2025: Cricsheet IPL archive, shown as 'our data'. Mumbai Indians' six finals and five titles: myKhel https://www.mykhel.com/cricket/ms-dhoni-vs-rohit-sharma-ipl-stats-and-record-best-captain-in-indian-premier-league-215101.html . Captaincy changes (Jadeja in 2022, Gaikwad's injury in 2025): Wikipedia, 'Chennai Super Kings'.",
       "Retirement from the IPL as a player and the mentor role: CSK announcement, 17 November 2026, as reported by Eastern Eye, Khel Now, Kalinga TV and Cricket Times. Figures: analysis/dhoni_captaincy_all.py."]
TAGS = ["MS Dhoni", "Dhoni IPL captain", "Dhoni captaincy record", "Dhoni retirement", "CSK", "Chennai Super Kings", "IPL captains", "IPL records", "most successful IPL captain", "IPL data", "cricket analysis", "The Third Man"]
DL = ("MS Dhoni's IPL captaincy, the complete record: every season from 2008 to 2025, not just the recent ones. 235 matches as captain (Chennai Super Kings and Rising Pune Supergiant), 136 wins, five titles (level with Rohit Sharma as the most by a captain). "
      "CSK reached ten finals in the sixteen seasons they played, and the playoffs in twelve of them. Against Mumbai Indians, the next best franchise: playoffs 12 of 16 seasons vs 11 of 18, finals 10 vs 6, titles 5 each. "
      "Over all eighteen seasons CSK won 57% of their decided matches, more than any franchise; Mumbai 55%, everyone else 52% or below.\n\nCSK announced MSD's retirement from the IPL as a player, and his role as team mentor, on 17 November 2026.\n\n"
      "Method: Cricsheet IPL ball-by-ball for every match 2008-2025 (our data); CSK's wins per season match Wikipedia's season table in every year. We state wins, finals and playoff seasons per season, not losses, because Cricsheet lacks a few abandoned matches. "
      "Win rate = wins / (wins + losses). Dhoni's own record is won 136 of 235 (57.87% counts no-results as matches).\n\n#MSDhoni #CSK #IPL #DataStory")
DS = ("MS Dhoni as IPL captain: 136 wins (no one has won more), ten finals in sixteen seasons, five titles. CSK reached the playoffs in 12 of 16 seasons, Mumbai in 11 of 18. Full breakdown on the channel.\n\n"
      "Our data: every IPL season 2008-2025 (Cricsheet ball-by-ball, checked against Wikipedia's season tables).\n\n#MSDhoni #CSK #IPL #Shorts")
spec = {"slug": "dhoni_captaincy_all", "theme": "lab", "theme_long": "whites", "captions": "lab", "captions_long": False, "series": "data", "tag": "DATA STORY", "tagsub": "MSD'S IPL CAPTAINCY, THE COMPLETE RECORD",
        "files": {"long": "x", "short": "x"}, "thumb": {"kicker": "MS DHONI · EVERY IPL SEASON", "lines": [{"t": "THE COMPLETE"}, {"t": "CAPTAINCY RECORD", "c": "gold"}], "hero": "136", "herosize": 520},
        "sources": SRC, "venue": VENUE, "long": long, "short": short, "full": full, "full_theme": "stadium", "full_captions": "v2", "reel_cta": reel_cta, "reel_caption": reel_caption,
        "yt": {"long": {"title": "MS Dhoni IPL Captaincy: The Complete Record, 2008-2025 | Data Story Ep 14", "description": DL, "tags": TAGS},
               "short": {"title": "Dhoni: 136 Wins, 10 Finals as IPL Captain | Data Story Ep 14 #Shorts", "description": DS, "tags": TAGS}}}
c.save(spec); voice_lint.fix_spec(spec)
spec["files"].setdefault("long", "_unused")
json.dump(spec, open("specs/dhoni_captaincy_all.json", "w"), ensure_ascii=False, indent=1)
print("wrote specs/dhoni_captaincy_all.json", voice_lint.check_spec(spec, ("long", "short")) or "voice lint clean", "|", sum(len(x["vo"]) for x in long), "+", sum(len(x["vo"]) for x in short), "chars to voice (before reuse)")
