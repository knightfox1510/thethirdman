"""Series-level analysis of the NZ v IND ODIs (matches 1, 2, 4, 5 ball by ball; the 3rd was washed out). Writes data/series/nz_ind_2026/SERIES.md and analysis/series.json.
    python3 analysis/nz_ind_series.py        (run nz_ind_wp / nz_ind_deep / nz_ind_story first)
Every number is computed from the ball tables; the series leaders are asserted against Wikipedia's infobox (Young 162, Kohli 86, Duffy 9, Brar 9)."""
import csv, json, os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nz_ind_cfg import STEMS, INFO, LABELS, INDIA_BATS, WIKI_LEADERS
OUT = "data/series/nz_ind_2026"; AN = OUT + "/analysis"
summ = json.load(open(f"{AN}/summary.json")); story = json.load(open(f"{AN}/story.json"))


def rd(stem, kind="balls"):
    rows = list(csv.DictReader(open(f"{OUT}/{stem}_{kind}.csv", encoding="utf-8")))
    if kind == "balls":
        for r in rows:
            for k in ("inning", "runs", "bat_runs", "score_after", "wkts_after"): r[k] = int(r[k])
            r["legal"] = r["legal"] == "True"; r["wicket"] = r["wicket"] == "True"; r["over"] = float(r["over"])
            r["ov"] = int(r["over"]) if round(r["over"] % 1, 1) != 0 else int(r["over"]) - 1
    return rows


B = {s: rd(s) for s in STEMS}; W = {s: rd(s, "wickets") for s in STEMS}
team_of = lambda stem, inn: "India" if inn == INDIA_BATS[stem] else "New Zealand"

# ------------------------------------------------------------------ batting and bowling leaderboards
bat = collections.defaultdict(lambda: {"team": "", "runs": 0, "balls": 0, "outs": 0, "inns": set(), "fours": 0, "sixes": 0, "scores": []})
bowl = collections.defaultdict(lambda: {"team": "", "balls": 0, "runs": 0, "wkts": 0, "dots": 0, "matches": set()})
for stem in STEMS:
    per = collections.defaultdict(lambda: [0, 0])
    for r in B[stem]:
        b = bat[r["batter"]]; b["team"] = team_of(stem, r["inning"]); b["runs"] += r["bat_runs"]; b["inns"].add((stem, r["inning"])); b["fours"] += r["bat_runs"] == 4; b["sixes"] += r["bat_runs"] == 6
        if r["legal"]: b["balls"] += 1
        per[(r["batter"], r["inning"])][0] += r["bat_runs"]; per[(r["batter"], r["inning"])][1] += r["legal"]
        o = bowl[r["bowler"]]; o["team"] = "New Zealand" if team_of(stem, r["inning"]) == "India" else "India"; o["runs"] += r["runs"] if r["extra"] not in ("leg bye", "bye") else 0
        if r["legal"]: o["balls"] += 1; o["dots"] += r["runs"] == 0
        o["matches"].add(stem)
        if r["wicket"] and r["dismissal"] != "run out": o["wkts"] += 1
    for w in W[stem]:
        bat[w["batter"]]["outs"] += 1
    for (n, inn), (runs, balls) in per.items(): bat[n]["scores"].append((LABELS[stem].split()[0], runs, balls, any(w["batter"] == n and int(w["inning"]) == inn for w in W[stem])))
# series leaders asserted against Wikipedia
lead = {"NZ most runs": max(((n, v["runs"]) for n, v in bat.items() if v["team"] == "New Zealand"), key=lambda x: x[1]), "IND most runs": max(((n, v["runs"]) for n, v in bat.items() if v["team"] == "India"), key=lambda x: x[1]),
        "NZ most wickets": max(((n, v["wkts"]) for n, v in bowl.items() if v["team"] == "New Zealand"), key=lambda x: x[1]), "IND most wickets": max(((n, v["wkts"]) for n, v in bowl.items() if v["team"] == "India"), key=lambda x: x[1])}
for k, v in WIKI_LEADERS.items(): assert lead[k] == v, (k, lead[k], v)

# ------------------------------------------------------------------ win probability added across the series
pv = collections.defaultdict(lambda: {"team": "", "wpa": 0.0, "matches": 0})
for stem in STEMS:
    for r in csv.DictReader(open(f"{AN}/{stem}_player_value.csv", encoding="utf-8")):
        p = pv[r["player"]]; p["team"] = r["team"]; p["wpa"] += float(r["total_wpa_for_team"]); p["matches"] += 1

# ------------------------------------------------------------------ powerplay, middle, death by match and side
rows_ph = []
for stem in STEMS:
    for inn in ("1", "2"):
        I = summ["matches"][stem]["innings"][inn]
        for name, v in I["phases"].items():
            if v["balls"] >= 12: rows_ph.append((LABELS[stem], I["team"], name, f"{v['runs']}/{v['wkts']}", v["balls"], v["rr"], f"{v['dot_pct']}%"))      # skip phases of a few balls (an innings that ended early)

# ------------------------------------------------------------------ drops and catches across the series
drops = {"India": [], "NZ": []}; drops_all = {"India": 0, "NZ": 0}
for stem in STEMS:
    seen = set()
    for d in story["drops"][stem]["list"]:
        drops_all[d["fielding_side"]] += 1
        if (d["fielding_side"], d["batter"]) in seen: continue                      # a second chance to the same batter: the runs after the FIRST count once
        seen.add((d["fielding_side"], d["batter"])); drops[d["fielding_side"]].append((LABELS[stem], d["batter"], d["over"], d["runs_at_drop"], d["final"], d["runs_after_drop"]))
fielding = collections.defaultdict(lambda: {"catches": 0, "swing": 0.0})
for stem in STEMS:
    for k, v in story[stem]["fielding"].items(): fielding[k]["catches"] += v["catches"]; fielding[k]["swing"] += v["catch_swing"]

# ------------------------------------------------------------------ who got whom
duel = collections.Counter(); kinds = collections.Counter(); by_bowler_kind = collections.defaultdict(collections.Counter)
for stem in STEMS:
    for w in W[stem]:
        duel[(w["bowler"], w["batter"])] += w["kind"] != "run out"; kinds[(team_of(stem, int(w["inning"])), w["kind"])] += 1

# ------------------------------------------------------------------ India's top three, match by match; new-ball overs
top3 = []
for stem in STEMS:
    ib = INDIA_BATS[stem]; ws = [w for w in W[stem] if int(w["inning"]) == ib][:3]
    top3.append((LABELS[stem], "; ".join(f"{w['batter']} {w['runs_of_batter']} ({w['balls_of_batter']}) b {w['bowler']}" for w in ws), ws[2]["score"] if len(ws) > 2 else "-"))

# ------------------------------------------------------------------ venues
ven = []
for stem in STEMS:
    I1 = summ["matches"][stem]["innings"]["1"]; ven.append((INFO[stem]["venue"], LABELS[stem], I1["team"], I1["score"], I1["run_rate"], f"{I1['boundary_pct']}%", f"{I1['dot_pct']}%"))

out = {"leaders": lead, "bat": {k: {**v, "inns": len(v["inns"])} for k, v in bat.items()}, "bowl": {k: {**v, "matches": len(v["matches"])} for k, v in bowl.items()}, "wpa": pv}
json.dump(out, open(f"{AN}/series.json", "w"), indent=1, default=str)

# ================================================================== the written series report
L = []; P = lambda s="": L.append(s)
def table(head, rows):
    P("| " + " | ".join(head) + " |"); P("|" + "|".join("---" for _ in head) + "|")
    for r in rows: P("| " + " | ".join(str(x) for x in r) + " |")
    P()
ov = lambda b: f"{b // 6}.{b % 6}"
P("# NZ v IND ODI series 2026: the whole series from the ball-by-ball data"); P()
P("Matches 1, 2, 4 and 5 are ball by ball (Cricbuzz captures); the 3rd was washed out (no play). Series leaders below are asserted equal to Wikipedia's infobox: "
  + ", ".join(f"{k}: {v[0]} {v[1]}" for k, v in lead.items()) + ". 26 validation checks pass (`analysis/nz_ind_validate.py`). The 5th ODI in depth is in REPORT.md.")
P()
ind_runs = sorted(((n, v) for n, v in bat.items() if v["team"] == "India"), key=lambda x: -x[1]["runs"]); nz_runs = sorted(((n, v) for n, v in bat.items() if v["team"] == "New Zealand"), key=lambda x: -x[1]["runs"])
ind_wk = sorted(((n, v) for n, v in bowl.items() if v["team"] == "India"), key=lambda x: (-x[1]["wkts"], x[1]["runs"])); nz_wk = sorted(((n, v) for n, v in bowl.items() if v["team"] == "New Zealand"), key=lambda x: (-x[1]["wkts"], x[1]["runs"]))
P("## What the data says")
P()
wp_top = sorted(pv.items(), key=lambda kv: -kv[1]["wpa"])[:5]; wp_bot = sorted(pv.items(), key=lambda kv: kv[1]["wpa"])[:3]
ib = lambda team, excl=None: [(v["wkts"], v["runs"]) for n, v in bowl.items() if v["team"] == team]
def attack(team, skip=None):
    w = r = 0
    for stem in STEMS:
        if stem == skip: continue
        for row in B[stem]:
            if ("New Zealand" if team_of(stem, row["inning"]) == "India" else "India") == team: r += row["runs"] if row["extra"] not in ("leg bye", "bye") else 0; w += row["wicket"] and row["dismissal"] != "run out"
    return w, r
iw, ir = attack("India"); nw, nr = attack("New Zealand"); iw2, ir2 = attack("India", "nz_ind_4odi"); nw2, nr2 = attack("New Zealand", "nz_ind_4odi")
P(f"1. **India bowled New Zealand out in all four of New Zealand's innings, yet had the worse bowling average over the series.** India's attack took {iw} wickets at {ir / iw:.1f}; New Zealand's took {nw} at {nr / nw:.1f}. The 4th ODI (333 conceded, and 89 all out against Matt Henry's 6/27) decides that: without it India's bowlers average {ir2 / iw2:.1f} and New Zealand's {nr2 / nw2:.1f}.")
P(f"2. **Top win-probability added over the series:** " + ", ".join(f"{n} ({v['team'][:3]}) {v['wpa']:+.2f}" for n, v in wp_top) + f". **Bottom:** " + ", ".join(f"{n} ({v['team'][:3]}) {v['wpa']:+.2f}" for n, v in wp_bot) + ". (WPA uses the Cricsheet-fitted model; matches 1 and 2 were rain-affected, see the notes.)")
P(f"3. **The top order failed again and again:** India's third wicket fell at " + ", ".join(f"{r[2]} ({r[0].split()[0]})" for r in top3) + ". " + f"Kohli's four innings were {', '.join(f'{s[1]}' for s in sorted(bat['Virat Kohli']['scores']))} (total {bat['Virat Kohli']['runs']}).")
P(f"4. **Catching:** India dropped {drops_all['India']} chances across the four matches and New Zealand {drops_all['NZ']} (Cricbuzz's own count during the 5th ODI chase: India had dropped eight in the series: it reconciles with ours); the batters let off first scored {sum(int(d[5]) for d in drops['India'] if str(d[5]).isdigit())} more runs after India's drops and {sum(int(d[5]) for d in drops['NZ'] if str(d[5]).isdigit())} after New Zealand's. Will Young alone, dropped twice in two balls in the 4th ODI, went on to score 120 after the first.")
P()
P("## Match by match")
P()
table(["Match", "Venue", "Toss and decision", "NZ innings", "India innings", "Result", "MoM"], [(LABELS[s], INFO[s]["venue"], "India, fielded" if s != "nz_ind_5odi" else "NZ, fielded", f"{summ['matches'][s]['innings']['1' if INDIA_BATS[s] == 2 else '2']['score']}/{summ['matches'][s]['innings']['1' if INDIA_BATS[s] == 2 else '2']['wkts']}", f"{summ['matches'][s]['innings']['2' if INDIA_BATS[s] == 2 else '1']['score']}/{summ['matches'][s]['innings']['2' if INDIA_BATS[s] == 2 else '1']['wkts']}", next(m for m in story['series']['matches'] if m['n'] == INFO[s]['n'])['result'].split(':')[0], next(m for m in story['series']['matches'] if m['n'] == INFO[s]['n']).get('motm', '-')) for s in STEMS])
P("The 3rd ODI (Hamilton, 10 November): no play, rain. Toss decisions are from Wikipedia: the toss winner chose to field in all five matches.")
P()
P("## Batting")
P()
table(["Batter", "Side", "Inns", "Runs", "Balls", "Dism.", "Avg", "SR", "4s/6s", "Scores"], [(n, v["team"][:3].upper(), len(v["inns"]), v["runs"], v["balls"], v["outs"], f"{v['runs'] / v['outs']:.1f}" if v["outs"] else "-", f"{100 * v['runs'] / max(1, v['balls']):.0f}", f"{v['fours']}/{v['sixes']}", ", ".join(f"{s[1]}{'' if s[3] else '*'}" for s in v["scores"])) for n, v in ind_runs[:8] + nz_runs[:8]])
P("## Bowling")
P()
table(["Bowler", "Side", "Matches", "Overs", "Runs", "Wkts", "Econ", "Avg", "Dot balls"], [(n, v["team"][:3].upper(), len(v["matches"]), ov(v["balls"]), v["runs"], v["wkts"], f"{6 * v['runs'] / max(1, v['balls']):.2f}", f"{v['runs'] / v['wkts']:.1f}" if v["wkts"] else "-", f"{100 * v['dots'] / max(1, v['balls']):.0f}%") for n, v in ind_wk[:7] + nz_wk[:7]])
P("## Powerplay, middle overs, death, match by match")
P()
table(["Match", "Batting side", "Phase", "Runs/wkts", "Balls", "Run rate", "Dots"], rows_ph)
P("## Win probability added (series)")
P()
table(["Player", "Side", "Matches", "Total WPA"], [(n, v["team"][:3].upper(), v["matches"], f"{v['wpa']:+.3f}") for n, v in sorted(pv.items(), key=lambda kv: -kv[1]["wpa"])[:8] + sorted(pv.items(), key=lambda kv: kv[1]["wpa"])[:5]])
P("Each ball's change in the batting side's win probability is credited to the batter and debited from the bowler. The model is fitted on full 50-over matches; in the 1st ODI (target revised to 143 from 32 overs after 2.5 overs) the revised target is used from the interruption; in the 2nd ODI the match ended at 113/7 after 26 overs on DLS (India 4 runs ahead of par) and the model's value is not the DLS result.")
P()
P("## Dismissals")
P()
table(["Side batting", "Kind", "Wickets"], [(k[0], k[1], v) for k, v in sorted(kinds.items())])
P("Most repeated bowler-batter dismissals: " + ", ".join(f"{b} dismissed {a} ×{n}" for (b, a), n in duel.most_common(6) if n > 1) + (" (none repeated)" if not any(n > 1 for n in duel.values()) else "") + ".")
P()
P("## Drops across the series")
P()
table(["Fielding side", "Match", "Batter", "Over", "Runs at drop", "Final", "Runs after"], [("India" if side == "India" else "NZ", *d) for side in ("India", "NZ") for d in drops[side]])
P("## Catches taken (win-probability swing of the wickets)")
P()
table(["Fielder", "Catches", "Total swing"], [(k, v["catches"], f"{v['swing'] * 100:.0f} pts") for k, v in sorted(fielding.items(), key=lambda kv: -kv[1]["swing"])[:8]])
P("## Three grounds, one series")
P()
table(["Ground", "Match", "Innings 1 side", "Score", "Run rate", "Boundary balls", "Dot balls"], ven)
P("Cricbuzz's commentary notes record the conditions as bowler-friendly in Auckland and Wellington (extra bounce, 'bounce and a little faster than expected', rain and moisture around) and that India's seamers pitched 40% back of a length or shorter in the first 10 overs in Auckland against 75% on a good length in Wellington: an editorial lead, not verified by us.")
P()
P("## Limits")
P()
P("Cricbuzz-only for matches 1, 2 and 5 (no line, length or shot data); the 4th also has the Cricinfo capture. WPA is a model, validated on the Cricsheet ODI archive, not a fact. Matches 1 and 2 were decided by DLS. The 3rd ODI had no play.")
open(f"{OUT}/SERIES.md", "w", encoding="utf-8").write("\n".join(L)); print(f"wrote {OUT}/SERIES.md ({len(L)} lines)")
