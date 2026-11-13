"""Builds specs/henry_6balls.json: the Short "3 Wickets In 6 Balls! Matt Henry vs India" (NZ v IND, 4th ODI, Mount Maunganui).
Illustrated recreation of Henry's first over. The six deliveries come from the Cricinfo ball table; dismissal wording comes from the
Cricbuzz capture. A highlights clip was used privately as a staging reference only (no footage, no likeness, no logos).
    python3 cricinfo_import.py data/cricinfo/nz_ind_4odi.json data/cricbuzz/nz_ind_4odi.json   # builds the csv first
    python3 make_henry_over.py"""
import json, pandas as pd
import voice_lint

b = pd.read_csv("data/cricinfo/nz_ind_4odi_balls.csv")
n2 = b[b.inning == 2]
ov = n2.iloc[:6]
cb = open("data/cricbuzz/nz_ind_4odi.json", encoding="utf-8").read()

# ---------------------------------------------------------------- facts (all asserted)
assert (n2.runs.sum(), n2.wicket.sum()) == (89, 10)
assert set(ov.bowler) == {"Matt Henry"} and ov.legal.all() and int(ov.runs.sum()) == 0
assert list(ov.overs) == [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
assert list(ov.batter) == ["Rohit Sharma", "Virat Kohli", "Virat Kohli", "Virat Kohli", "Virat Kohli", "Shreyas Iyer"]
assert ov.wicket.tolist() == [True, False, False, False, True, True] and int(ov.wicket.sum()) == 3
assert (ov.bat_runs == 0).all()
# dismissal wording (Cricbuzz scorecard lines); Cricinfo's numeric dismissal codes agree on the order 1, 2, 3
assert "Rohit Sharma c Finn Allen b Matt Henry 0(1)" in cb
assert "Kohli b Matt Henry 0(4)" in cb
assert "Iyer lbw b Matt Henry 0(1)" in cb
assert [int(x) for x in ov[ov.wicket].dismissal] == [1, 2, 3]
# the three balls between the wickets
mid = ov.iloc[1:4]
assert list(mid.pitch_line) == ["OUTSIDE_OFFSTUMP"] * 3
assert list(mid.pitch_length) == ["FULL", "FULL", "SHORT_OF_A_GOOD_LENGTH"]
assert (mid.wicket == False).all() and int(ov.iloc[4].pitch_length == "SHORT") == 1 and ov.iloc[4].pitch_line == "OUTSIDE_OFFSTUMP"
assert ov.iloc[0].pitch_line == "ON_THE_STUMPS"
# match context
hn = n2[n2.bowler == "Matt Henry"]
assert (int(hn.wicket.sum()), int(hn.runs.sum()), len(hn)) == (6, 27, 60)
assert n2.runs.sum() == 89 and "Matt Henry" in cb
print("all facts asserted")

# ---------------------------------------------------------------- scenes (stadium stage, illustrated, no likeness)
def S(vo, sc, **kw): return dict({"vo": vo, "scene": sc}, **kw)
def stage(vo, panel, av, **kw): return S(vo, dict({"type": "stage", "panel": dict(panel, at=.05), "avatars": av}, **kw))
VEN = {"time": "day", "crowd": [[20, 20, 20], [235, 235, 235], [20, 20, 25], [60, 60, 60]], "boards": [[20, 20, 20], [235, 235, 235]]}
bowl = lambda x=.66: dict(kit="NZ", pose="bowl", x=x, dir=-1)
bat = lambda pose="stance", x=.26: dict(kit="IND", pose=pose, x=x)

short = [
 stage("Three wickets. Six balls. Matt Henry against India.",
       {"kind": "headline", "kicker": "4TH ODI · MOUNT MAUNGANUI", "lines": [{"t": "3 WICKETS."}, {"t": "6 BALLS.", "c": "gold"}]},
       [bowl(), bat("dejected")], view="side", cam="wide", stumps=[.17, .93]),
 stage("Ball one. On the stumps. रोहित शर्मा is caught. Nought.",
       {"kind": "headline", "kicker": "BALL ONE", "lines": [{"t": "ROHIT. CAUGHT."}, {"t": "0 (1)", "c": "red"}]},
       [bowl(), bat("stance")], view="side", cam="push", stumps=[.17, .93]),
 stage("Then three balls to विराट कोहली. Outside off stump. Full, full, and just short of a good length. No run.",
       {"kind": "table", "kicker": "BALLS TWO TO FOUR", "rows": [["Ball 2 · full", "dot", "ink"], ["Ball 3 · full", "dot", "ink"], ["Ball 4 · short of good length", "dot", "ink"]]},
       [bowl(), bat("stance")], view="side", cam="drift", stumps=[.17, .93]),
 stage("Ball five. Outside off, short. विराट कोहली is bowled. Nought off four.",
       {"kind": "headline", "kicker": "BALL FIVE", "lines": [{"t": "KOHLI. BOWLED."}, {"t": "0 (4)", "c": "red"}]},
       [bowl(), bat("stance")], view="side", cam="push", stumps=[.17, .93], ball={"at": .55, "shot": "bowled"}),
 stage("Ball six. श्रेयस अय्यर, first ball. Lbw. Nought.",
       {"kind": "headline", "kicker": "BALL SIX", "lines": [{"t": "IYER. LBW."}, {"t": "0 (1)", "c": "red"}]},
       [bowl(), bat("dejected")], cam="pull"),
 stage("India were nought for three, and never came back. They were all out for eighty-nine.",
       {"kind": "bignum", "label": "INDIA AFTER ONE OVER", "value": 0, "suffix": " / 3", "count_dur": .5, "kicker": "Henry's first over"},
       [dict(kit="IND", pose="dejected", x=.5)], cam="drift"),
 stage("Matt Henry finished with six for twenty-seven. Follow for the full breakdown.",
       {"kind": "headline", "kicker": "THE REPLAY ROOM", "lines": [{"t": "6 FOR 27."}, {"t": "FULL BREAKDOWN →", "c": "gold"}]},
       [dict(kit="NZ", pose="raise", x=.5, cap=True)], cam="push"),
]

SRC = ["ESPNcricinfo match capture, NZ v IND 4th ODI, Mount Maunganui (match 1539440): ball-by-ball with line, length and shot data, captured with our own tool.",
       "Cricbuzz match capture (match 161271): over-by-over cross-check and dismissal wording (c Finn Allen b Henry; b Henry; lbw b Henry).",
       "Official result in both sources: New Zealand won by 244 runs; Player of the Match Matt Henry.",
       "All figures computed in make_henry_over.py from data/cricinfo/nz_ind_4odi_balls.csv. Scenes are illustrated recreations (not broadcast footage); a highlights clip was used privately as a staging reference only."]
TITLE = "3 Wickets In 6 Balls! Matt Henry vs India"
DESC = ("Matt Henry's first over against India in the 4th ODI at Mount Maunganui: Rohit Sharma caught, Virat Kohli bowled, Shreyas Iyer lbw, all in six balls, "
        "no runs conceded. Illustrated recreation built from ball-by-ball data (ESPNcricinfo and Cricbuzz match pages, our own analysis). Part of The Replay Room; the full breakdown is on the channel.")
TAGS = ["Matt Henry", "India vs New Zealand", "Rohit Sharma", "Virat Kohli", "Shreyas Iyer", "4th ODI", "cricket analysis", "The Replay Room", "The Third Man"]
spec = {"slug": "henry_6balls", "theme": "stadium", "theme_long": "lab", "captions": "serif", "captions_long": False, "series": "replay",
        "tag": "THE REPLAY ROOM", "tagsub": "HENRY · 3 WICKETS IN 6 BALLS",
        "files": {"long": "Henry_Long_unused", "short": "3_Wickets_In_6_Balls_Matt_Henry_vs_India_Short_9x16"},
        "thumb": {"kicker": "MATT HENRY", "lines": [{"t": "3 WICKETS"}, {"t": "6 BALLS", "c": "gold"}], "hero": "3", "herosize": 420},
        "sources": SRC, "venue": VEN, "short": short,
        "yt": {"short": {"title": TITLE + " #Shorts", "description": DESC, "tags": TAGS}}}
voice_lint.fix_spec(spec)
json.dump(spec, open("specs/henry_6balls.json", "w"), ensure_ascii=False, indent=1)
print("wrote specs/henry_6balls.json,", sum(len(x["vo"].split()) for x in short), "words")
