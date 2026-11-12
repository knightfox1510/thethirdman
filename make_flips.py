"""Writes the flip Short specs from analysis/flips.py, so every number comes straight from the data."""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "analysis"))
import flips as F

CS_SRC = "Cricsheet ball-by-ball data (cricsheet.org, ODC-BY). Figures: analysis/flips.py"


def save(spec): json.dump(spec, open(f"specs/{spec['slug']}.json", "w"), ensure_ascii=False, indent=1); print("wrote", spec["slug"])


# 1. MI captains vs Rohit
by = F.mi_captains(); rohit = by["Rohit Sharma"]
pct = lambda r: 100 * sum(r) / len(r)
order = [("Ricky Ponting", "drive"), ("Kieron Pollard", "pull"), ("Suryakumar Yadav", "drive"), ("Jasprit Bumrah", "release"), ("Hardik Pandya", "defend")]
pairs = []
for nm, pose in order:
    r = by[nm]; n = len(r)
    pairs.append({"name": nm, "team": "MI", "pose": pose, "n": f"{n} GAME{'S' if n > 1 else ''} AS CAPTAIN", "value": round(pct(r), 1),
                  "bench": round(pct(rohit[:n]), 1), "color": "#D4A82E"})
save({"slug": "flip_mi_captains", "files": {"short": "Every_MI_Captain_vs_Rohit_Sharma_Flip_9x16"},
      "title": {"kicker": "MUMBAI INDIANS CAPTAINS", "lines": ["EVERY MI CAPTAIN", "VS ROHIT SHARMA"],
                "sub": "Win % in decided IPL matches, at the same number of games as captain"},
      "metric": "WIN %", "better": "higher", "dec": 1, "bench": {"name": "Rohit Sharma", "team": "MI", "pose": "pull", "color": "#004BA0"},
      "pairs": pairs, "end": {"lines": [f"ROHIT AFTER {len(rohit)} GAMES:", f"{pct(rohit):.1f}%"], "ask": "WHO COMES CLOSEST?"},
      "sources": ["Sportmonks IPL fixtures and line-ups (captain flag), IPL 2013-2026. Win % of decided matches (no-results left out). Figures: analysis/flips.py"],
      "yt": {"short": {"title": "Every MI captain vs Rohit Sharma 📊 #Shorts", "description": "Win % of every Mumbai Indians captain since 2013, against Rohit Sharma at the same number of games. Data: every IPL match since 2013.",
                       "tags": ["Rohit Sharma", "Hardik Pandya", "Mumbai Indians", "IPL", "IPL captain", "cricket stats", "cricket shorts", "The Third Man"]}}})

# 2. Bumrah vs the best fast bowlers of the century, after 52 Tests
PACE = [("JJ Bumrah", "Jasprit Bumrah", "IND", None), ("SCJ Broad", "Stuart Broad", "ENG", "#C8102E"), ("TA Boult", "Trent Boult", "NZ", None),
        ("MA Starc", "Mitchell Starc", "AUS", None), ("Mohammed Shami", "Mohammed Shami", "IND", "#F28C28"), ("JR Hazlewood", "Josh Hazlewood", "AUS", None),
        ("K Rabada", "Kagiso Rabada", "SA", None), ("PJ Cummins", "Pat Cummins", "AUS", None)]
tb = F.test_bowling_by_match([p[0] for p in PACE]); nb = len(tb["JJ Bumrah"]); ba = F.avg(tb["JJ Bumrah"])[0]
pairs = [{"name": nm, "team": tm, "pose": "release", "n": f"{nb} TESTS", "value": round(F.avg(tb[k][:nb])[0], 2), "bench": round(ba, 2),
          **({"color": col} if col else {})} for k, nm, tm, col in PACE[1:]]
save({"slug": "flip_bumrah_52_tests", "files": {"short": "Bumrah_vs_Best_Fast_Bowlers_After_52_Tests_Flip_9x16"},
      "title": {"kicker": f"FAST BOWLERS AFTER {nb} TESTS", "lines": ["BUMRAH VS", "THE BEST OF THE CENTURY"],
                "sub": f"Test bowling average after {nb} Tests. Lower is better"},
      "metric": "BOWLING AVERAGE", "better": "lower", "dec": 2, "bench": {"name": "Jasprit Bumrah", "team": "IND", "pose": "release", "color": "#1F5FB8"},
      "pairs": pairs, "end": {"lines": [f"BUMRAH: {ba:.2f}", "NOBODY ELSE UNDER 22"], "ask": "WHO'S THE GREATEST?"},
      "sources": [CS_SRC, "Fast bowlers whose whole Test careers are in the data (debut 2007 or later), compared after the same number of Tests"],
      "yt": {"short": {"title": f"Bumrah vs the best fast bowlers after {nb} Tests 🔥 #Shorts", "description": f"Test bowling average after {nb} Tests: Jasprit Bumrah against Cummins, Rabada, Hazlewood, Starc, Boult, Broad and Shami.",
                       "tags": ["Jasprit Bumrah", "Pat Cummins", "Kagiso Rabada", "Test cricket", "fast bowling", "cricket stats", "cricket shorts", "The Third Man"]}}})

# 3. Joe Root vs everyone, at the same number of Tests
BAT = [("JE Root", "Joe Root", "ENG", None), ("Babar Azam", "Babar Azam", "PAK", None), ("M Labuschagne", "Marnus Labuschagne", "AUS", None),
       ("V Kohli", "Virat Kohli", "IND", None), ("Shubman Gill", "Shubman Gill", "IND", None), ("KS Williamson", "Kane Williamson", "NZ", None),
       ("SPD Smith", "Steve Smith", "AUS", None), ("HC Brook", "Harry Brook", "ENG", "#C8102E"), ("YBK Jaiswal", "Yashasvi Jaiswal", "IND", None)]
tt = F.test_batting_by_match([b[0] for b in BAT]); root = tt["JE Root"]
pairs = []
for k, nm, tm, col in BAT[1:]:
    x = tt[k]; n = len(x)
    pairs.append({"name": nm, "team": tm, "pose": "drive", "n": f"{n} TESTS", "value": sum(r for _, r in x), "bench": sum(r for _, r in root[:n]),
                  **({"color": col} if col else {})})
save({"slug": "flip_root_same_point", "files": {"short": "Joe_Root_vs_Everyone_Same_Point_Flip_9x16"},
      "title": {"kicker": "TEST RUNS AT THE SAME POINT", "lines": ["JOE ROOT VS", "EVERYONE ELSE"],
                "sub": "Test runs after the same number of Tests"},
      "metric": "TEST RUNS", "better": "higher", "dec": 0, "bench": {"name": "Joe Root", "team": "ENG", "pose": "drive", "color": "#14306B"},
      "pairs": pairs, "end": {"lines": [f"ROOT: {sum(r for _, r in root):,} RUNS", f"IN {len(root)} TESTS"], "ask": "WHO CATCHES HIM?"},
      "sources": [CS_SRC, "Batters whose whole Test careers are in the data (debut 2010 or later); data to October 2026"],
      "yt": {"short": {"title": "Joe Root vs everyone at the same point 🏏 #Shorts", "description": "Test runs after the same number of Tests: Joe Root against Smith, Williamson, Kohli, Brook, Jaiswal, Gill, Babar and Labuschagne.",
                       "tags": ["Joe Root", "Steve Smith", "Virat Kohli", "Kane Williamson", "Harry Brook", "Yashasvi Jaiswal", "Test cricket", "cricket shorts", "The Third Man"]}}})

# 4. Abhishek vs the world's T20I openers
OPEN = [("Abhishek Sharma", "Abhishek Sharma", "IND", None), ("Babar Azam", "Babar Azam", "PAK", None), ("RG Sharma", "Rohit Sharma", "IND", "#F28C28"),
        ("DA Warner", "David Warner", "AUS", None), ("FH Allen", "Finn Allen", "NZ", None), ("TM Head", "Travis Head", "AUS", None),
        ("JC Buttler", "Jos Buttler", "ENG", None), ("PD Salt", "Phil Salt", "ENG", "#C8102E")]
oi = F.t20i_opening_innings([o[0] for o in OPEN]); ab = oi["Abhishek Sharma"]
sr = lambda x: 100 * sum(i[1] for i in x) / max(1, sum(i[2] for i in x))
pairs = []
for k, nm, tm, col in OPEN[1:]:
    n = min(len(oi[k]), len(ab))
    pairs.append({"name": nm, "team": tm, "pose": "drive", "n": f"{n} INNINGS AS OPENER", "value": round(sr(oi[k][:n]), 1), "bench": round(sr(ab[:n]), 1),
                  **({"color": col} if col else {})})
save({"slug": "flip_abhishek_openers", "files": {"short": "Abhishek_vs_World_T20I_Openers_Flip_9x16"},
      "title": {"kicker": "T20I OPENERS AT THE SAME POINT", "lines": ["ABHISHEK SHARMA VS", "THE WORLD'S OPENERS"],
                "sub": "T20I strike rate as an opener, after the same number of innings"},
      "metric": "STRIKE RATE", "better": "higher", "dec": 1, "bench": {"name": "Abhishek Sharma", "team": "IND", "pose": "pull", "color": "#1F5FB8", "mirror": True},
      "pairs": pairs, "end": {"lines": [f"ABHISHEK: {sr(ab):.1f}", f"AFTER {len(ab)} INNINGS"], "ask": "WHO'S THE BEST OPENER?"},
      "sources": [CS_SRC, "T20 internationals; innings in which the batter was one of the first two to bat; strike rate = runs off the bat per 100 balls faced (wides excluded)"],
      "yt": {"short": {"title": "Abhishek Sharma vs the world's T20I openers ⚡ #Shorts", "description": "T20I strike rate as an opener after the same number of innings: Abhishek Sharma against Salt, Head, Buttler, Allen, Warner, Rohit and Babar.",
                       "tags": ["Abhishek Sharma", "Phil Salt", "Travis Head", "Jos Buttler", "T20I", "T20 cricket", "cricket stats", "cricket shorts", "The Third Man"]}}})
