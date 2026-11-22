"""Day 4 of NZ v IND, 1st Test (Basin Reserve, 22 Nov 2026): India's innings from 124.6 (Day-3 stumps, 486/4) to the declaration at 720/9 (165.6 overs), and New Zealand's second innings to stumps (119/2, 44.6 overs),
from the owner's ball-by-ball commentary capture (data/cricbuzz/nz_ind_1st_test_day4.json: innings 1 = NZ first innings to 243/5 only, 2 = India, 3 = NZ second innings). Writes data/provenance/nz_day4_figures.json.   python3 analysis/nz_day4.py"""
import json, os, re, collections
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(f"{R}/data/cricbuzz/nz_ind_1st_test_day4.json")); C = d["comments"]


def text(x):
    t = x["commText"]
    for v in x.get("commentaryFormats", {}).values():
        for fid, val in zip(v["formatId"], v["formatValue"]): t = t.replace(fid, val)
    return t


OUT = {}
for inn in (2, 3):
    xs = sorted((x for x in C if x["inningsId"] == inn), key=lambda x: x["timestamp"]); bat = {}; bowl = {}
    for x in xs:
        b = x.get("batsmanStriker") or {}
        if b.get("batName"): bat[b["batName"]] = {k: b[k] for k in ("batRuns", "batBalls", "batFours", "batSixes")}
        w = x.get("bowlerStriker") or {}
        if w.get("bowlName"): bowl[w["bowlName"]] = {"ov": w["bowlOvs"], "m": w["bowlMaidens"], "r": w["bowlRuns"], "w": w["bowlWkts"], "nb": w.get("bowlNoballs")}
    balls = [x for x in xs if x.get("overNumber")]; last = balls[-1]
    wk = [{"over": x["overNumber"], "score": x["batTeamScore"], "bat": (x.get("batsmanStriker") or {}).get("batName"), "runs": (x.get("batsmanStriker") or {}).get("batRuns"), "balls": (x.get("batsmanStriker") or {}).get("batBalls"), "text": text(x)[:200]} for x in balls if "WICKET" in x.get("event", "")]
    OUT[f"inn{inn}"] = {"batters": bat, "bowlers": bowl, "end": {"over": last["overNumber"], "score": last["batTeamScore"]}, "wickets": wk}
i2 = sorted((x for x in C if x["inningsId"] == 2 and x.get("overNumber")), key=lambda x: x["timestamp"])
OUT["day4_india"] = {"runs": 720 - 486, "overs": round(165.6 - 124.6, 1)}
OUT["sixes_by_bowler_day4"] = dict(collections.Counter((re.match(r"(.+?) to ", text(x)) or [None, "?"])[1] for x in i2 if x["overNumber"] > 124.6 and x.get("event", "").find("SIX") >= 0))
OUT["sixes_by_bowler_innings"] = dict(collections.Counter((re.match(r"(.+?) to ", text(x)) or [None, "?"])[1] for x in i2 if "SIX" in x.get("event", "")))
OUT["control_note"] = [text(x)[:240] for x in C if "control percentage" in text(x)][:1]
OUT["pair_note"] = [text(x)[:240] for x in C if "eighth instance of a NZ opener" in text(x)][:1]
json.dump(OUT, open(f"{R}/data/provenance/nz_day4_figures.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps({k: (v if k not in ("inn2", "inn3") else {"end": v["end"], "bowlers": v["bowlers"], "batters": v["batters"], "wk": [(w["over"], w["score"], w["bat"], w["runs"]) for w in v["wickets"]]}) for k, v in OUT.items()}, indent=1, ensure_ascii=False))
