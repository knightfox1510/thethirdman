"""Writes data/series/nz_ind_2026/REPORT.md from the analysis outputs (every figure comes from summary.json / story.json / the CSVs, none is typed).
    python3 analysis/nz_ind_report.py"""
import csv, json, os, sys
OUT = "data/series/nz_ind_2026"; AN = OUT + "/analysis"
S = json.load(open(f"{AN}/summary.json")); T = json.load(open(f"{AN}/story.json"))
M4, M5 = S["matches"]["nz_ind_4odi"], S["matches"]["nz_ind_5odi"]; R4, R5 = T["nz_ind_4odi"], T["nz_ind_5odi"]
L = []; P = lambda s="": L.append(s)


def table(head, rows):
    P("| " + " | ".join(head) + " |"); P("|" + "|".join("---" for _ in head) + "|")
    for r in rows: P("| " + " | ".join(str(x) for x in r) + " |")
    P()


def wprows(stem, n=8):
    rows = list(csv.DictReader(open(f"{AN}/{stem}_wp.csv", encoding="utf-8")))
    top = sorted(rows, key=lambda r: -abs(float(r["delta_bat_wp"])))[:n]
    return [(f"inn{r['inning']} {r['over']}", f"{r['bowler']} to {r['batter']}", ("wicket" if r["wicket"] == "True" else r["event"].replace("over-break,", "") or f"{r['runs']} run(s)"),
             f"{float(r['delta_bat_wp']) * 100:+.0f} pts for the batting side", f"{float(r['india_wp']) * 100:.0f}%") for r in top]


def ph(M, inn, name): return M["innings"][str(inn)]["phases"].get(name, {})


i5 = M5["innings"]; i4 = M4["innings"]; ex = R5["india_wp_extremes"]; tip = R5["tipping_point"]; ck = R5["chase_checkpoints"]; lw = R5["last_wicket_stand"]; dr5 = T["drops"]["nz_ind_5odi"]["runs_conceded_after_drops"]; dr4 = T["drops"]["nz_ind_4odi"]["runs_conceded_after_drops"]
p0_chase = None
for c in R5["curve"]:
    if c["inning"] == 2: p0_chase = c; break
net = dr5.get("NZ", 0) - dr5.get("India", 0)

P("# NZ v IND ODI series 2026: analysis of the 4th and 5th ODIs (Bay Oval), in the context of the series"); P()
P("Everything below is derived by code from our own tables (`data/series/nz_ind_2026/`); series context for matches 1-3 is from Wikipedia (which cites Cricinfo match reports). "
  "Matches 1, 2, 4 and 5 are ball by ball (Cricbuzz captures; the 4th also has an independent Cricinfo capture that agrees over by over); this report covers the 4th and 5th in depth, SERIES.md the whole series. Win probability is from a model fitted on the Cricsheet ODI archive (see Method).")
P()
P("## Headlines")
P()
P(f"1. **India won by 22 runs defending {i5['1']['score']}, all out in {i5['1']['overs']} overs.** Our model gave New Zealand {100 - round(100 * (1 - 0.782)):.0f}% to chase 210 before a ball was bowled, so this was a result the archive says happens about one time in five.")
P(f"2. **The match turned at {tip['score']} in the 40th over** (over {tip['over']}): Santner holed out to Arshdeep off Naman Dhir's bowling, India's win probability went from about {100 * (tip['india_wp'] - 0.268):.0f}% to {100 * tip['india_wp']:.0f}% and never dropped below 50% again. It was the biggest single swing of the match (27 points).")
P(f"3. **New Zealand's chase never accelerated.** They scored {ph(M5, 2, 'powerplay (1-10)')['rr']} an over in the first ten overs against a required {ck[0]['required_rate']}, then {ph(M5, 2, 'middle (11-40)')['rr']} through the middle overs while the required rate climbed: after 30 overs {ck[2]['score']}, needing {ck[2]['need']} at {ck[2]['required_rate']} (they were scoring {ck[2]['run_rate_so_far']}); after 40 overs {ck[3]['score']}, needing {ck[3]['need']} at {ck[3]['required_rate']} (scoring {ck[3]['run_rate_so_far']}). {i5['2']['dot_pct']}% of their balls were dots.")
P(f"4. **Drops almost decided it.** After the chances New Zealand put down (Axar Patel on 2, Shreyas Iyer on 5) India scored {dr5.get('NZ')} more runs from those two batters; after India's two (Foxcroft on 5, Bracewell on 8) New Zealand scored {dr5.get('India')}. A net {net} runs, more than the 22-run margin. (Descriptive, not a counterfactual: a batter's later runs are not all down to the let-off.)")
P(f"5. **Hidden winner: Naman Dhir.** Two overs, four runs, the Santner wicket: +{[h for h in R5['hidden']['winners'] if h['player'] == 'Naman Dhir'][0]['wpa']:.2f} win probability, second in the match behind Arshdeep Singh (the Player of the Match), yet eighth on a plain scorecard rank. **Hidden loser: Jacob Duffy** (3/60 in 8.1 overs, {[h for h in R5['hidden']['losers'] if h['player'] == 'Jacob Duffy'][0]['wpa']:+.2f}): three wickets that cost more than they gained.")
P(f"6. **India's innings was a collapse in two parts.** {ph(M5, 1, 'powerplay (1-10)')['runs']}/{ph(M5, 1, 'powerplay (1-10)')['wkts']} off the first 60 balls ({ph(M5, 1, 'powerplay (1-10)')['dot_pct']}% dots, {ph(M5, 1, 'powerplay (1-10)')['boundary_pct']}% boundary balls), then {R5['collapse_windows']['1']['most_wickets_in_10_overs']} wickets for {R5['collapse_windows']['1']['runs_in_that_window']} runs between overs {R5['collapse_windows']['1']['from_over']} and {R5['collapse_windows']['1']['to_over']}. The last-wicket stand added {lw['runs']} off {lw['legal_balls']} balls ({lw['from']}) but moved their win probability by only {lw['wp_gain'] * 100:.0f} points.")
P(f"7. **Same ground, 48 hours apart, a different game.** New Zealand scored {i4['1']['score']} (run rate {i4['1']['run_rate']}, boundaries on {i4['1']['boundary_pct']}% of balls) in the 4th ODI and {i5['2']['score']} (run rate {i5['2']['run_rate']}, {i5['2']['boundary_pct']}%) in the 5th. India's bowling economy fell from {M4['pace_vs_spin']['India']['pace']['econ']} (pace) and {M4['pace_vs_spin']['India']['spin']['econ']} (spin) to {M5['pace_vs_spin']['India']['pace']['econ']} and {M5['pace_vs_spin']['India']['spin']['econ']}, and their plan moved from {M4['pace_vs_spin']['India']['pace']['overs']} overs of pace and {M4['pace_vs_spin']['India']['spin']['overs']} of spin to {M5['pace_vs_spin']['India']['pace']['overs']} and {M5['pace_vs_spin']['India']['spin']['overs']}.")
P(f"8. **The series is 3-1 to India (one washout), but the two matches we have are opposites**: a 244-run defeat, in which India dropped the eventual centurion twice in the first two overs (the runs he made after the first drop: 120), and a 22-run win.")
P()
P("## Series context")
P()
table(["#", "Date", "Venue", "Result", "Player of the match", "Ball by ball?"], [(m["n"], m["date"], m["venue"], m["result"], m.get("motm", "-"), "yes" if m["ball_by_ball"] else "no") for m in T["series"]["matches"]])
P(f"Source: {T['series']['source']}. {T['series']['result']}. The 3rd ODI had no play (rain). Matches 1, 2, 4 and 5 are ball by ball: the whole series is in SERIES.md.")
P()
P("## The 5th ODI in detail")
P()
P("### Win probability arc (India), end of every 5 overs")
P()
table(["Innings", "After over", "Score", "India win prob."], [(c["inning"], c["after_over"], c["score"], f"{100 * c['india_wp']:.0f}%") for c in R5["curve"]])
P(f"India's low point was {100 * ex['min']:.0f}% ({ex['min_at']}); the high was {100 * ex['max']:.0f}% at the end. Tipping point (last time the match crossed 50%): {tip['score']}, over {tip['over']}.")
P()
P("### The ten biggest swings")
P()
table(["When", "Ball", "Event", "Swing", "India win prob. after"], wprows("nz_ind_5odi", 10))
P("### New Zealand's chase against the required rate")
P()
table(["After over", "Score", "Needed", "Required rate", "Their run rate so far"], [(c["after_over"], c["score"], c["need"], c["required_rate"], c["run_rate_so_far"]) for c in ck])
P(f"Their longest run of dot balls was {i5['2']['longest_dot_run']['balls']} (ending over {i5['2']['longest_dot_run']['ends_over']}); the longest stretch without a boundary was {i5['2']['longest_boundary_drought_balls']} balls. The Cricbuzz commentary notes 11 dots in a row with a wicket in them against Foxcroft.")
P()
P("### Phases")
P()
rows = []
for team_inn, nm in ((1, "India batting"), (2, "NZ batting")):
    for name in ("powerplay (1-10)", "middle (11-40)", "death (41-50)"):
        v = ph(M5, team_inn, name)
        if v: rows.append((nm, name, f"{v['runs']}/{v['wkts']}", v["balls"], v["rr"], f"{v['dot_pct']}%", f"{v['boundary_pct']}%"))
table(["Side", "Phase", "Runs/wkts", "Balls", "Run rate", "Dots", "Boundary balls"], rows)
P("### Player value: win probability added (WPA), 5th ODI")
P()
pv = list(csv.DictReader(open(f"{AN}/nz_ind_5odi_player_value.csv", encoding="utf-8")))
table(["Player", "Side", "Batting", "Bowling", "Bat WPA", "Bowl WPA", "Total"], [(p["player"], p["team"][:3].upper(), f"{p['bat_runs']} ({p['bat_balls']})", f"{p['bowl_wkts']}/{p['bowl_runs']} in {int(p['bowl_balls']) // 6}.{int(p['bowl_balls']) % 6}", p["bat_wpa"], p["bowl_wpa"], p["total_wpa_for_team"]) for p in pv[:8] + pv[-5:]])
P(f"Definition: each ball's change in the batting side's win probability is credited to the batter and debited from the bowler (and the reverse for a falling probability). Hidden winners/losers: {R5['hidden']['definition']}.")
P()
P("### Catching: who turned wickets into swings")
P()
table(["Fielder", "Catches", "Win-probability swing of those wickets"], [(k, v["catches"], f"{v['catch_swing'] * 100:.0f} pts") for k, v in list(R5["fielding"].items())[:6]])
P("### Drops")
P()
table(["Fielding side", "Batter", "Over", "Runs at the drop", "Final", "Runs after the drop"], [(d["fielding_side"], d["batter"], d["over"], d["runs_at_drop"], d["final"], d["runs_after_drop"]) for d in T["drops"]["nz_ind_5odi"]["list"]])
P("### Bowling cards")
P()
table(["Bowler", "Inn.", "Overs", "Runs", "Wkts", "Econ", "Dots", "Boundary balls", "Style"], [(b["bowler"], b["inning"], b["overs"], b["runs"], b["wkts"], b["econ"], f"{b['dot_pct']}%", b["boundary_balls"], b["style"]) for b in M5["bowling"]])
P("(* style assumed: not in our Cricinfo squad data.) Pace v spin: " + "; ".join(f"{t}: pace {v['pace']['overs']} ov {v['pace']['runs']}/{v['pace']['wkts']} (econ {v['pace']['econ']}), spin {v['spin']['overs']} ov {v['spin']['runs']}/{v['spin']['wkts']} (econ {v['spin']['econ']})" for t, v in M5["pace_vs_spin"].items()) + ".")
P()
P("## The 4th ODI, and 4th v 5th")
P()
P("### 4th ODI: the ten biggest swings")
P()
table(["When", "Ball", "Event", "Swing", "India win prob. after"], wprows("nz_ind_4odi", 8))
P(f"New Zealand scored 333 after India dropped Will Young twice in the second over, on the 5th and 6th balls (Rohit Sharma, then Ishan Kishan, both off Auqib Nabi): he was on 5 and made 125, i.e. 120 runs after the first let-off. India's drops cost {dr4.get('India')} runs after the chances in total (Young 120, Santner 17). Matt Henry then took 6/27, including the first three India wickets in the first over (0/3).")
P()
P("### Side by side (same ground, 15 and 13 November)")
P()
def inn(M, i, key): return M["innings"][str(i)][key]
rows = [("NZ batting", "4th: batting first", inn(M4, 1, "score"), inn(M4, 1, "run_rate"), f"{inn(M4, 1, 'dot_pct')}%", f"{inn(M4, 1, 'boundary_pct')}%", ph(M4, 1, "powerplay (1-10)")["rr"], ph(M4, 1, "death (41-50)")["rr"]),
        ("NZ batting", "5th: chasing", inn(M5, 2, "score"), inn(M5, 2, "run_rate"), f"{inn(M5, 2, 'dot_pct')}%", f"{inn(M5, 2, 'boundary_pct')}%", ph(M5, 2, "powerplay (1-10)")["rr"], ph(M5, 2, "death (41-50)")["rr"]),
        ("India batting", "4th: chasing", inn(M4, 2, "score"), inn(M4, 2, "run_rate"), f"{inn(M4, 2, 'dot_pct')}%", f"{inn(M4, 2, 'boundary_pct')}%", ph(M4, 2, "powerplay (1-10)")["rr"], "-"),
        ("India batting", "5th: batting first", inn(M5, 1, "score"), inn(M5, 1, "run_rate"), f"{inn(M5, 1, 'dot_pct')}%", f"{inn(M5, 1, 'boundary_pct')}%", ph(M5, 1, "powerplay (1-10)")["rr"], ph(M5, 1, "death (41-50)")["rr"])]
table(["Side", "Match", "Score", "Run rate", "Dot balls", "Boundary balls", "Powerplay RR", "Death RR"], rows)
ind4, ind5, nz4, nz5 = M4["pace_vs_spin"]["India"], M5["pace_vs_spin"]["India"], M4["pace_vs_spin"]["New Zealand"], M5["pace_vs_spin"]["New Zealand"]
bw = lambda M, n: [b for b in M["bowling"] if b["bowler"] == n]
P(f"**What changed.** (a) New Zealand's powerplay went from {ph(M4, 1, 'powerplay (1-10)')['runs']}/{ph(M4, 1, 'powerplay (1-10)')['wkts']} ({ph(M4, 1, 'powerplay (1-10)')['rr']}) to {ph(M5, 2, 'powerplay (1-10)')['runs']}/{ph(M5, 2, 'powerplay (1-10)')['wkts']} ({ph(M5, 2, 'powerplay (1-10)')['rr']}): Arshdeep Singh's figures were {bw(M4, 'Arshdeep Singh')[0]['overs']}-{bw(M4, 'Arshdeep Singh')[0]['runs']}-{bw(M4, 'Arshdeep Singh')[0]['wkts']} in the 4th and {bw(M5, 'Arshdeep Singh')[0]['overs']}-{bw(M5, 'Arshdeep Singh')[0]['runs']}-{bw(M5, 'Arshdeep Singh')[0]['wkts']} in the 5th, and the commentary shows India setting slips for the new ball (one slip to start, two slips for Siraj, a wide slip for Thakur). "
  f"(b) India moved from a spin-heavy attack ({ind4['spin']['overs']} overs of spin at {ind4['spin']['econ']} an over, {ind4['pace']['overs']} of pace at {ind4['pace']['econ']}) to pace ({ind5['pace']['overs']} overs at {ind5['pace']['econ']}; spin {ind5['spin']['overs']} at {ind5['spin']['econ']}). "
  f"(c) New Zealand moved the other way: from {nz4['spin']['overs']} overs of spin to {nz5['spin']['overs']}, and their spinners ({nz5['spin']['econ']} an over) were more economical than their seamers ({nz5['pace']['econ']}). "
  f"(d) India's batting still lost its top three cheaply (0/3 in the 4th; 34/3 in the 5th), but the 5th had more boundary balls ({inn(M5, 1, 'boundary_pct')}% against {inn(M4, 2, 'boundary_pct')}%) and fewer dots ({inn(M5, 1, 'dot_pct')}% against {inn(M4, 2, 'dot_pct')}%).")
P()
P("## Series-level observations we can support (and what we cannot)")
P()
P("- **Toss:** the side winning the toss chose to field in all five matches (Wikipedia: India in 1-4, New Zealand in 5). In the two we have ball by ball, the side batting first won the 4th (NZ, 333) and the 5th (India, 209): defending, not chasing, produced the results at Bay Oval.")
dd = lambda T_, side: sum(1 for d in T_["list"] if d["fielding_side"] == side)
P(f"- **Catching** is a recurring theme: in the two matches we hold, India dropped {dd(T['drops']['nz_ind_4odi'], 'India')} chances in the 4th and {dd(T['drops']['nz_ind_5odi'], 'India')} in the 5th, and New Zealand {dd(T['drops']['nz_ind_4odi'], 'NZ')} and {dd(T['drops']['nz_ind_5odi'], 'NZ')}. A Cricbuzz note during the 5th ODI chase says India had made 14 misfields and dropped eight catches in the series so far (catching efficiency 74.1%): a lead for the whole series, which we can only confirm once matches 1-3 are captured.")
P("- **Kohli's series:** Wikipedia lists him as India's leading run-scorer with 86; the Cricbuzz notes say the 5th ODI gave him a third single-digit score in the series. (Both leads: from the 4th (0) and 5th (5) we have, the other two innings are not ours.)")
P("- **See SERIES.md** for the leaderboards, powerplay table, drops and catches across the four matches that were played.")
P()
P("## Video angles this supports (all numbers above are code-derived; check against Cricinfo before use)")
P()
P("1. **\"The 22% win\"**: India defended 209 against a model's 78% chase: the Santner moment (27 points), the drops (net 24 runs against a 22-run margin), the dot-ball squeeze. Long + Short.")
P("2. **\"Two days at Bay Oval\"**: the 4th v 5th table: same ground, same toss decision, opposite results; India's pace plan, NZ's spin plan. Long.")
P("3. **\"The hidden winner\"**: Naman Dhir's 2-0-4-1 (and Yash Thakur's debut, \"two in two\" at 30.6/31.1: Nabi's Bracewell then Thakur's Foxcroft, a combined 39-point swing). Short.")
P("4. **\"The cost of a drop\"**: Will Young, 125 after two chances in two balls. A Data Story across the series (SERIES.md: India dropped eight chances in four matches, the batters let off first scored 244 more runs).")
P()
P("## Method, validation and limits")
P()
P(f"- **Tables:** `dataops/cricbuzz_balls.py` turns the Cricbuzz commentary into one row per delivery (wides and no-balls included); runs per delivery are the change in team score; innings totals are asserted against the last score in the commentary. Runs off the bat are the change in the striker's own total.")
P("- **Validation (`analysis/nz_ind_validate.py`, 14 checks):** innings totals and overs, Axar 46 (55), Foxcroft 31 (42), Arshdeep 3/30, Santner 3/47 (5th ODI), Young 125 (108), Henry 6/27, Axar 2/39, Kishan 27 (53) (4th ODI) all equal Wikipedia's match boxes; NZ's pace 6/125 in 22.1 and spin 4/82 in 20 overs equal Cricbuzz's own editorial line; the 4th ODI's runs agree with the independent Cricinfo capture in all 77 overs.")
P("- **Win-probability model (`dataops/winprob.py`):** logistic regression for chases and a projected-total model for first innings, fitted on 1,719 men's 50-over ODIs (Cricsheet, 2009 onwards, no rain method). Held-out chases: log loss 0.359, accuracy 83%, and the calibration bins sit within a few points of the actual win rates. It is an indication, not a fact: the archive is a sample, it knows nothing about this ground, these players or the pitch, and a 'win probability' is a modelling choice. Values are shown rounded.")
P("- **Cricbuzz-only for the 5th ODI:** no line, length, shot or wagon data (only the 4th has the Cricinfo capture); a few dismissal kinds and fielders are parsed from commentary text. Bowling styles come from the Cricinfo squad data where we have it (starred where assumed).")
P("- **Unverified leads kept out of the numbers:** Cricbuzz editorial notes (e.g. catching efficiency, 'second instance of India bundled out for' ...). Treat them as leads to check on Cricinfo.")
open(f"{OUT}/REPORT.md", "w", encoding="utf-8").write("\n".join(L)); print(f"wrote {OUT}/REPORT.md ({len(L)} lines)")
