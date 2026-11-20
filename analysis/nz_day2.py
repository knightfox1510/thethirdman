"""Day 2 of NZ v India, 1st Test (Basin Reserve, 20 Nov 2026): India's first innings to stumps, from the owner's Cricbuzz full-commentary capture
(data/cricbuzz/nz_ind_1st_test_day2.json, innings 2 = India, 281 entries). The capture holds NO NZ-innings entries after 243/5 (Day 1), so NZ's morning (to 368) is not analysed from ball data.
Line/length are OUR keyword classification of Cricbuzz's ball text; control/false-shot aggregates are Cricbuzz's own. Writes data/provenance/nz_day2_figures.json.   python3 analysis/nz_day2.py"""
import json, os, re, collections
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(f"{R}/data/cricbuzz/nz_ind_1st_test_day2.json")); C = [x for x in d["comments"] if x["inningsId"] == 2]
def text(x):
    t = x["commText"]
    for v in x.get("commentaryFormats", {}).values():
        for fid, val in zip(v["formatId"], v["formatValue"]): t = t.replace(fid, val)
    return t.replace("\\n", "\n")


rows = sorted(({"ts": x["timestamp"], "over": x.get("overNumber"), "ev": x.get("event", ""), "text": text(x), "score": x.get("batTeamScore"), "runs": x.get("totalRuns", 0),
                "bs": x.get("batsmanStriker") or {}, "bw": x.get("bowlerStriker") or {}} for x in C), key=lambda r: r["ts"])
balls = [r for r in rows if r["over"]]
M = re.compile(r"^(.+?) to (.+?), (no run|\d+ runs?|FOUR|SIX|out [^,]+|leg byes?|byes?|wide|no ball)[^,]*(?:, ?(.*))?$", re.S)
LEN = [("yorker", r"yorker"), ("short", r"\bbouncer|\bbumper|\bshort (?:delivery|ball|outside|and|on|down|around|across)|^short\b|\bshort,|shortish|short and"),
       ("short_of_length", r"short of (?:a )?length|back of (?:a )?length|short-of-a-length"), ("good", r"good length|\blength delivery|\blength outside|length ball|good-length"), ("full", r"\bfull|fullish|driving length|half-volley|half volley")]
def length_of(t):
    t = t.lower()
    for k, p in LEN:
        if re.search(p, t): return k
    return None
def kph(t):
    m = re.search(r"(\d{2,3}\.\d)kph|(\d{2,3}\.\d)ks", t); return float((m.group(1) or m.group(2))) if m else None
D = []
for r in balls:
    m = M.match(r["text"].split("\n")[0]) or M.match(r["text"])
    if not m: continue
    bowler, bat, res, desc = m.group(1), m.group(2), m.group(3), m.group(4) or ""
    D.append({"over": r["over"], "bowler": bowler, "bat": bat, "res": res, "runs": r["runs"], "wkt": "WICKET" in r["ev"], "nb": res == "no ball" or "no ball" in res, "len": length_of(desc or r["text"]), "kph": kph(r["text"]), "ts": r["ts"], "score": r["score"], "text": r["text"]})
OUT = {"deliveries": len(D), "legal": sum(1 for x in D if not x["nb"] and x["res"] != "wide")}
fin = {}
for r in balls:
    b = r["bw"].get("bowlName")
    if b: fin[b] = (r["bw"]["bowlOvs"], r["bw"]["bowlMaidens"], r["bw"]["bowlRuns"], r["bw"]["bowlWkts"], r["bw"].get("bowlNoballs"))
OUT["bowling_final"] = {b: dict(zip(("ov", "m", "r", "w", "nb"), v)) for b, v in fin.items()}
last = {}
for r in balls:
    b = r["bs"].get("batName")
    if b: last[b] = r["bs"]
OUT["batters"] = {b: {k: x[k] for k in ("batRuns", "batBalls", "batFours", "batSixes", "batDots", "batStrikeRate")} for b, x in last.items()}
tea = [r["ts"] for r in rows if "Tea, Day 2" in r["text"] or "Final over before Tea" in r["text"]]
tea_ts = [r["ts"] for r in rows if "Tea, Day 2" in r["text"]]
OUT["tea_over"] = [r for r in balls if r["ts"] <= (tea_ts[0] if tea_ts else 0)][-1]["over"] if tea_ts else None
OUT["tea_score"] = [r for r in balls if r["ts"] <= tea_ts[0]][-1]["score"] if tea_ts else None
OUT["stumps"] = {"over": balls[-1]["over"], "score": balls[-1]["score"]}
OUT["wickets"] = [{"over": x["over"], "bowler": x["bowler"], "bat": x["bat"], "score": x["score"], "text": x["text"][:300]} for x in D if x["wkt"]]
sp = collections.defaultdict(list)
for x in D:
    if x["kph"]: sp[x["bowler"]].append(x["kph"])
OUT["speed"] = {b: {"n": len(v), "avg": round(sum(v) / len(v), 1), "max": max(v)} for b, v in sp.items()}
OUT["no_balls"] = collections.Counter(x["bowler"] for x in D if x["nb"])
OUT["no_balls"] = dict(OUT["no_balls"])
for k in ("full", "good", "short_of_length", "short", "yorker"):
    xs = [x for x in D if x["len"] == k and not x["nb"]]; OUT.setdefault("by_length", {})[k] = {"balls": len(xs), "runs": sum(x["runs"] for x in xs)}
OUT["by_length"]["unclassified"] = sum(1 for x in D if x["len"] is None)
# runs per 6-over block and boundaries
blk = collections.OrderedDict()
for x in sorted(D, key=lambda x: x["ts"]):
    b = int(x["over"]) // 6; blk.setdefault(b, [0, 0]); blk[b][0] += x["runs"]; blk[b][1] += 1
OUT["blocks"] = {f"{b*6}-{b*6+5}": v for b, v in blk.items()}
OUT["fours"] = sum(1 for x in D if x["res"] == "FOUR"); OUT["dots"] = sum(1 for x in D if x["res"] == "no run")
OUT["milestones"] = [{"over": r["over"], "ev": r["ev"], "score": r["score"]} for r in balls if any(k in r["ev"] for k in ("FIFTY", "TEAM_HUNDRED", "PARTNERSHIP", "WICKET", "UDRS"))]
os.makedirs(f"{R}/data/provenance", exist_ok=True); json.dump(OUT, open(f"{R}/data/provenance/nz_day2_figures.json", "w"), indent=1, ensure_ascii=False)
json.dump([{k: v for k, v in x.items() if k != "text"} for x in D], open(f"{R}/data/provenance/nz_day2_balls.json", "w"))
print(json.dumps({k: v for k, v in OUT.items() if k not in ("wickets",)}, indent=1))
print(json.dumps(OUT["wickets"], indent=1))
