"""Day 5 of NZ v IND, 1st Test (Basin Reserve, 23 Nov 2026): New Zealand's second innings from 44.6 overs (119/2 at Day-4 stumps) to the draw at 119.6 overs (239/5), from the owner's ball-by-ball commentary capture
(data/cricbuzz/nz_ind_1st_test_day5.json, innings 3). Sessions are cut at the lunch, tea and handshake notes. Writes data/provenance/nz_day5_figures.json.   python3 analysis/nz_day5.py"""
import json, os, re, collections
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(f"{R}/data/cricbuzz/nz_ind_1st_test_day5.json")); C3 = sorted((x for x in d["comments"] if x["inningsId"] == 3), key=lambda x: x["timestamp"])


def text(x):
    t = x["commText"]
    for v in x.get("commentaryFormats", {}).values():
        for fid, val in zip(v["formatId"], v["formatValue"]): t = t.replace(fid, val)
    return t


balls = [x for x in C3 if x.get("overNumber")]
def note_ts(pat): return [x["timestamp"] for x in C3 if not x.get("overNumber") and re.search(pat, text(x))][0]
LUNCH, TEA, END = note_ts(r"Just 38 runs in 26 overs"), note_ts(r"Tea on Day 5"), note_ts(r"India have had enough")
def at(ts): z = [x for x in balls if x["timestamp"] <= ts][-1]; return z["overNumber"], z["batTeamScore"]
def wk_before(ts): return sum(1 for x in balls if "WICKET" in x.get("event", "") and x["timestamp"] <= ts and x["overNumber"] > 44.6)
OUT = {"start": {"over": 44.6, "score": 119}, "end": {"over": balls[-1]["overNumber"], "score": balls[-1]["batTeamScore"]}}
bat = {}; bowl = {}
for x in C3:
    b = x.get("batsmanStriker") or {}
    if b.get("batName"): bat[b["batName"]] = {k: b[k] for k in ("batRuns", "batBalls", "batFours", "batSixes", "batDots")}
    w = x.get("bowlerStriker") or {}
    if w.get("bowlName"): bowl[w["bowlName"]] = {"ov": w["bowlOvs"], "m": w["bowlMaidens"], "r": w["bowlRuns"], "w": w["bowlWkts"], "nb": w.get("bowlNoballs")}
OUT["batters"] = bat; OUT["bowlers"] = bowl
OUT["wickets"] = [{"over": x["overNumber"], "score": x["batTeamScore"], "bat": (x.get("batsmanStriker") or {}).get("batName"), "runs": (x.get("batsmanStriker") or {}).get("batRuns"), "balls": (x.get("batsmanStriker") or {}).get("batBalls")} for x in balls if "WICKET" in x.get("event", "") and x["overNumber"] > 44.6]
S = json.load(open(f"{R}/data/provenance/nz_shots_d5.json")); D5 = [o for o in S if o["over"] > 44.6]
for i, (nm, a, b) in enumerate((("morning", 0, LUNCH), ("middle", LUNCH, TEA), ("evening", TEA, END))):
    z = [x for x in balls if x["overNumber"] > 44.6 and a < x["timestamp"] <= b] if i else [x for x in balls if x["overNumber"] > 44.6 and x["timestamp"] <= b]
    rows = [o for o in D5 if any(abs(o["over"] - x["overNumber"]) < 1e-9 and o["ts"] == x["timestamp"] for x in z)] if False else None
    o0, s0 = (44.6, 119) if i == 0 else at(a); o1, s1 = at(b)
    OUT[nm] = {"over_from": o0, "over_to": o1, "runs": s1 - s0, "wkts": wk_before(b) - (0 if i == 0 else wk_before(a)), "overs": round(o1 - o0 + 0.0, 1)}
# per-over runs and wickets (overs 45..119)
ov = collections.OrderedDict()
for x in balls:
    if x["overNumber"] > 44.6:
        k = int(x["overNumber"]); ov.setdefault(k, [0, False]); ov[k][0] += x.get("totalRuns", 0); ov[k][1] = ov[k][1] or "WICKET" in x.get("event", "")
OUT["per_over"] = [[k, v[0], v[1]] for k, v in ov.items()]; OUT["maidens_day5"] = sum(1 for v in ov.values() if v[0] == 0)
# bowler overs by session (from the ball rows with an over number)
def bws(a, b): return dict(collections.Counter(re.match(r"(.+?) to ", text(x)).group(1) for x in balls if x["overNumber"] > 44.6 and a < x["timestamp"] <= b and re.match(r"(.+?) to ", text(x)) and (x["overNumber"] * 10) % 10 == 6))
OUT["overs_by_bowler"] = {"morning": bws(0, LUNCH), "middle": bws(LUNCH, TEA), "evening": bws(TEA, END)}
OUT["dots_day5"] = sum(1 for o in D5 if o["res"] == "no run"); OUT["balls_day5"] = len(D5)
json.dump(OUT, open(f"{R}/data/provenance/nz_day5_figures.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps({k: v for k, v in OUT.items() if k != "per_over"}, indent=1, ensure_ascii=False)); print([tuple(p) for p in OUT["per_over"]][:80])
