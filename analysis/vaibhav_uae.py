"""Vaibhav Sooryavanshi's 204 (53 balls) for India A v UAE, 11th match, Group B, ACC Men's Asia Cup Rising Stars 2026 (Doha, 24 Nov 2026), from the owner's ball-by-ball commentary capture
(data/cricbuzz/ind_uae_rising_stars_2026.json; result and score corroborated by the Cricinfo profile capture). Direction/line/length are OUR keyword read of the text. Writes data/provenance/vaibhav_uae_figures.json.   python3 analysis/vaibhav_uae.py"""
import json, os, re, collections, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, f"{R}/analysis")
d = json.load(open(f"{R}/data/cricbuzz/ind_uae_rising_stars_2026.json")); C = sorted([x for x in d["comments"] if x["inningsId"] == 2 and x.get("overNumber")], key=lambda x: x["timestamp"])
def text(x):
    s = x["commText"]
    for v in x.get("commentaryFormats", {}).values():
        for a, b in zip(v["formatId"], v["formatValue"]): s = s.replace(a, b)
    return s
ZONES = [(r"third man|fine third|wide of gully|past gully", 140), (r"backward point|deep point|\bpoint\b|square of the wicket|cuts? ", 105), (r"extra cover|deep cover|through cover|\bcover\b", 62), (r"mid-?off|long-?off|wide of mid-off|straight of mid-off", 28),
         (r"down the ground|straight down|back past the bowler|over the bowler|over the bowler's head|straight over|straight", 0), (r"mid-?on|long-?on", -28), (r"mid-?wicket|midwicket|deep mid-wicket|deep midwicket|slog.?sweep", -62), (r"square leg|deep square|backward square", -105), (r"fine leg|down the leg|glance|flick|behind square", -140)]
def zone(s):
    s = s.lower(); best = None
    for p, a in ZONES:
        m = re.search(p, s)
        if m and (best is None or m.start() < best[0]): best = (m.start(), a)
    return None if best is None else best[1]
rows = []
for x in C:
    b = x.get("batsmanStriker") or {}
    if b.get("batName") != "Vaibhav Sooryavanshi": continue
    t = text(x).split("\n")[0]; m = re.match(r"(.+?) to (.+?), (SIX|FOUR|no run|\d runs?|wide|byes?|out [^,]*)", t)
    if not m: continue
    res = m.group(3); runs = 6 if res == "SIX" else (4 if res == "FOUR" else (int(res[0]) if res[0].isdigit() and "run" in res else 0))
    rows.append({"over": x["overNumber"], "bowler": m.group(1), "res": res, "runs": runs, "score": b["batRuns"], "balls": b["batBalls"], "ang": zone(t.lower()) if runs > 0 else None, "text": t[:200]})
legal = [r for r in rows if r["res"] != "wide"]
OUT = {"innings": {"runs": 204, "balls": 53, "fours": 7, "sixes": 28, "sr": round(100 * 204 / 53, 1), "boundary_runs": 7 * 4 + 28 * 6, "boundary_share": round(100 * (7 * 4 + 28 * 6) / 204, 1)}}
mile = {}
for r in rows:
    for m_ in (50, 100, 150, 200):
        if r["score"] >= m_ and m_ not in mile: mile[m_] = r["balls"]
OUT["milestones_balls"] = mile
bw = collections.defaultdict(lambda: [0, 0, 0, 0])
for r in legal:
    k = r["bowler"]; bw[k][0] += 1; bw[k][1] += r["runs"]; bw[k][2] += r["res"] == "SIX"; bw[k][3] += r["res"] == "FOUR"
OUT["by_bowler"] = {k: {"balls": v[0], "runs": v[1], "sixes": v[2], "fours": v[3]} for k, v in bw.items()}
six = [r for r in rows if r["res"] == "SIX"]; ang = [r["ang"] for r in six if r["ang"] is not None]
OUT["sixes_placed"] = len(ang); OUT["sixes_total"] = len(six); OUT["six_dirs"] = {"leg_side": sum(1 for a in ang if a < 0), "straight": sum(1 for a in ang if a == 0), "off_side": sum(1 for a in ang if a > 0)}
by_over = collections.OrderedDict()
for r in rows: by_over[int(r["over"])] = by_over.get(int(r["over"]), 0) + r["runs"]
OUT["runs_by_over"] = dict(by_over); OUT["rows"] = rows
OUT["partners"] = {"Abhishek Sharma": 68, "Prabhsimran Singh": 108 - 68, "Rinku Singh": 245 - 108}
OUT["dots"] = sum(1 for r in legal if r["runs"] == 0); OUT["dismissal"] = "c Aryansh Sharma b Basil Hameed (12.5 ov, 245/3)"
json.dump(OUT, open(f"{R}/data/provenance/vaibhav_uae_figures.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps({k: v for k, v in OUT.items() if k != "rows"}, indent=1)); print(len(rows), len(legal))
