"""Day 1 of NZ v India, 1st Test (Basin Reserve, 19 Nov 2026, NZ 1st innings): figures from the owner's Cricbuzz full-commentary capture (data/cricbuzz/nz_ind_1st_test_2026_day1.json, 599 entries, 498 deliveries).
Line/length are OUR classification of Cricbuzz's per-ball commentary text (keywords below); the sessions' aggregates (control %, false-shot % by length) are Cricbuzz's own and are credited as such.
Writes data/provenance/nz_day1_figures.json.   python3 analysis/nz_day1.py"""
import json, os, re, collections
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(f"{R}/data/cricbuzz/nz_ind_1st_test_2026_day1.json")); C = d["comments"]


def text(x):
    t = x["commText"]
    for v in x.get("commentaryFormats", {}).values():
        for fid, val in zip(v["formatId"], v["formatValue"]): t = t.replace(fid, val)
    return t.replace("\\n", "\n")


rows = sorted(({"ts": x["timestamp"], "over": x.get("overNumber"), "ev": x.get("event", ""), "text": text(x), "score": x.get("batTeamScore"), "runs": x.get("totalRuns", 0), "bs": x.get("batsmanStriker") or {}, "bw": x.get("bowlerStriker") or {}} for x in C), key=lambda r: r["ts"])
balls = [r for r in rows if r["over"]]
M = re.compile(r"^(.+?) to (.+?), (no run|\d+ runs?|FOUR|SIX|out [^,]+|leg byes?|byes?|wide|no ball)[^,]*(?:, ?(.*))?$", re.S)
LEN = [("yorker", r"yorker"), ("short", r"\bbouncer|\bbumper|\bshort (?:delivery|ball|outside|and|on|down|around|across)|^short\b|\bshort,|shortish|short and"), ("short_of_length", r"short of (?:a )?length|back of (?:a )?length|short-of-length"),
       ("good", r"good length|\blength delivery|\blength outside|length ball|good-length"), ("full", r"\bfull|fullish|driving length|half-volley|half volley")]


def length_of(t):
    t = t.lower()
    if re.search(r"tossed up|flighted|flatter|sliding|fired|\d+\.\d+ks tossed", t): return "spin"
    for k, p in LEN:
        if re.search(p, t): return k
    return None


def kph(t):
    m = re.search(r"(\d{2,3}\.\d)ks", t); return float(m.group(1)) if m else None


D = []
for r in balls:
    m = M.match(r["text"].split("\n")[0]) or M.match(r["text"])
    if not m: continue
    bowler, bat, res, desc = m.group(1), m.group(2), m.group(3), m.group(4) or ""
    ov, bl = r["over"], int(round((r["over"] % 1) * 10)); D.append({"over": ov, "ball": bl, "bowler": bowler, "bat": bat, "res": res, "runs": r["runs"], "wkt": "WICKET" in r["ev"], "len": length_of(desc if desc else r["text"]), "kph": kph(r["text"]), "text": r["text"], "score": r["score"], "ev": r["ev"]})
spin = {"Washington Sundar"}
OUT = {"deliveries": len(D)}
fin = {}
for r in balls:
    b = r["bw"].get("bowlName")
    if b: fin[b] = (r["bw"]["bowlOvs"], r["bw"]["bowlMaidens"], r["bw"]["bowlRuns"], r["bw"]["bowlWkts"])
OUT["bowling_final"] = {b: {"ov": v[0], "m": v[1], "r": v[2], "w": v[3]} for b, v in fin.items()}
last = balls[-1]; OUT["stumps"] = {"over": last["over"], "score": last["score"]}
for who in ("Henry Nicholls", "Glenn Phillips"):
    x = [r for r in balls if r["bs"].get("batName") == who][-1]["bs"]; OUT[who] = {k: x[k] for k in ("batRuns", "batBalls", "batFours", "batDots", "batStrikeRate")}
# session boundaries: lunch = 'Should be the last ball before lunch', tea = 'Final over before Tea'
def over_at(ts): return [r for r in balls if r["ts"] <= ts][-1]["over"]
lunch_ts = [r["ts"] for r in rows if "last ball before lunch" in r["text"]][0]; tea_ts = [r["ts"] for r in rows if "Final over before Tea" in r["text"]][0]
OUT["lunch_over"] = over_at(lunch_ts); OUT["tea_over"] = over_at(tea_ts); OUT["lunch_score"] = [r for r in balls if r["ts"] <= lunch_ts][-1]["score"]; OUT["tea_score"] = [r for r in balls if r["ts"] <= tea_ts][-1]["score"]
def sess(o): return 1 if o <= OUT["lunch_over"] + .001 else (2 if o <= OUT["tea_over"] + .001 else 3)
for x in D: x["sess"] = sess(x["over"])
# length by session (seamers only) and wickets
tab = collections.defaultdict(lambda: collections.Counter())
for x in D:
    if x["bowler"] in spin or x["len"] in (None, "spin"): continue
    tab[x["sess"]][x["len"]] += 1; tab["day"][x["len"]] += 1
OUT["length_by_session"] = {str(k): dict(v) for k, v in tab.items()}
WK = [{"over": x["over"], "bowler": x["bowler"], "bat": x["bat"], "len": x["len"], "score": x["score"], "text": x["text"][:260]} for x in D if x["wkt"]]
OUT["wickets"] = WK
# speeds by bowler
sp = collections.defaultdict(list)
for x in D:
    if x["kph"]: sp[x["bowler"]].append(x["kph"])
OUT["speed"] = {b: {"n": len(v), "avg": round(sum(v) / len(v), 1), "max": max(v)} for b, v in sp.items()}
# runs by session and by bowler-length
OUT["runs_by_length_seam"] = {k: sum(x["runs"] for x in D if x["bowler"] not in spin and x["len"] == k) for k in ("full", "good", "short_of_length", "short", "yorker")}
OUT["balls_by_length_seam"] = {k: sum(1 for x in D if x["bowler"] not in spin and x["len"] == k) for k in ("full", "good", "short_of_length", "short", "yorker")}
os.makedirs(f"{R}/data/provenance", exist_ok=True); json.dump(OUT, open(f"{R}/data/provenance/nz_day1_figures.json", "w"), indent=1, ensure_ascii=False)
json.dump([{k: v for k, v in x.items() if k != "text"} for x in D], open(f"{R}/data/provenance/nz_day1_balls.json", "w"))
print(json.dumps({k: v for k, v in OUT.items() if k != "wickets"}, indent=1)); print("unclassified length:", sum(1 for x in D if x["len"] is None and x["bowler"] not in spin), "of", sum(1 for x in D if x["bowler"] not in spin))
