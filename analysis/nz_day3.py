"""Day 3 of NZ v IND, 1st Test (Basin Reserve, 21 Nov 2026): India's first innings from 38.6 (Day-2 stumps, 159/1) to 124.6 (Day-3 stumps, 486/4), from the owner's Cricbuzz capture
(data/cricbuzz/nz_ind_1st_test_day3.json, innings 2). The capture still has no NZ-innings entries after 243/5 (Day 1). Length classes are OUR keyword read of Cricbuzz's text.
Writes data/provenance/nz_day3_figures.json and nz_day3_balls.json (whole India innings, 'day' = 2 or 3).   python3 analysis/nz_day3.py"""
import json, os, re, collections
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(f"{R}/data/cricbuzz/nz_ind_1st_test_day3.json")); C = [x for x in d["comments"] if x["inningsId"] == 2]


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
D = []
for r in balls:
    m = M.match(r["text"].split("\n")[0]) or M.match(r["text"])
    if not m: continue
    D.append({"over": r["over"], "bowler": m.group(1), "bat": m.group(2), "res": m.group(3), "runs": r["runs"], "wkt": "WICKET" in r["ev"] or m.group(3).startswith("out"), "nb": "no ball" in m.group(3), "len": length_of(m.group(4) or r["text"]),
              "ts": r["ts"], "score": r["score"], "day": 3 if r["over"] > 38.6 + 1e-9 else 2})
D3 = [x for x in D if x["day"] == 3]
OUT = {"deliveries": len(D3), "innings_deliveries": len(D)}
last = balls[-1]; OUT["stumps"] = {"over": last["over"], "score": last["score"]}
bat = {}
for r in balls:
    b = r["bs"].get("batName")
    if b: bat[b] = r["bs"]
OUT["batters"] = {b: {k: x[k] for k in ("batRuns", "batBalls", "batFours", "batSixes", "batDots", "batStrikeRate")} for b, x in bat.items()}
fin = {}
for r in balls:
    b = r["bw"].get("bowlName")
    if b: fin[b] = r["bw"]
OUT["bowling_final"] = {b: {"ov": x["bowlOvs"], "m": x["bowlMaidens"], "r": x["bowlRuns"], "w": x["bowlWkts"], "nb": x.get("bowlNoballs"), "wd": x.get("bowlWides")} for b, x in fin.items()}
def at(txt):
    z = [r["ts"] for r in rows if txt in r["text"]]; return z[0] if z else None
lunch, tea = at("that's lunch"), at("Tea, Day 3")
def last_before(ts): return [r for r in balls if r["ts"] <= ts][-1]
OUT["lunch"] = {"over": last_before(lunch)["over"], "score": last_before(lunch)["score"]} if lunch else None
OUT["tea"] = {"over": last_before(tea)["over"], "score": last_before(tea)["score"]} if tea else None
OUT["wickets"] = [{"over": x["over"], "bowler": x["bowler"], "bat": x["bat"], "score": x["score"]} for x in D if x["wkt"]]
OUT["milestones"] = [{"over": r["over"], "ev": r["ev"], "score": r["score"], "bat": r["bs"].get("batName"), "runs": r["bs"].get("batRuns"), "balls": r["bs"].get("batBalls")} for r in balls if any(k in r["ev"] for k in ("FIFTY", "HUNDRED", "PARTNERSHIP", "WICKET", "SIX", "UDRS"))]
blk = collections.OrderedDict()
for x in sorted(D3, key=lambda x: x["ts"]):
    b = int(x["over"]) // 10; blk.setdefault(b, [0, 0, 0]); blk[b][0] += x["runs"]; blk[b][1] += 1; blk[b][2] += x["wkt"]
OUT["blocks_by_10_overs"] = {f"{b*10}-{b*10+9}": v for b, v in blk.items()}
by = collections.defaultdict(lambda: [0, 0, 0, 0])
for x in D3:
    k = x["bowler"]; by[k][0] += 1; by[k][1] += x["runs"]; by[k][2] += x["wkt"]; by[k][3] += x["nb"]
OUT["day3_bowlers"] = {k: {"balls": v[0], "runs": v[1], "wkts": v[2], "nb": v[3]} for k, v in by.items()}
OUT["day3_runs"] = sum(x["runs"] for x in D3); OUT["day3_fours"] = sum(1 for x in D3 if x["res"] == "FOUR"); OUT["day3_sixes"] = sum(1 for x in D3 if x["res"] == "SIX"); OUT["day3_dots"] = sum(1 for x in D3 if x["res"] == "no run")
OUT["day3_by_length"] = {k: {"balls": sum(1 for x in D3 if x["len"] == k and not x["nb"]), "runs": sum(x["runs"] for x in D3 if x["len"] == k and not x["nb"])} for k in ("full", "good", "short_of_length", "short")}
OUT["reviews"] = [{"over": r["over"], "text": r["text"][:220]} for r in balls if "UDRS" in r["ev"] or "second review" in r["text"] or "burnt all" in r["text"] or "lose their" in r["text"]]
OUT["notes"] = [r["text"][:400] for r in rows if re.search(r"new ball|second new ball", r["text"]) and not r["over"]][:6]
json.dump(OUT, open(f"{R}/data/provenance/nz_day3_figures.json", "w"), indent=1, ensure_ascii=False)
json.dump([{k: v for k, v in x.items()} for x in D], open(f"{R}/data/provenance/nz_day3_balls.json", "w"))
print(json.dumps(OUT, indent=1, ensure_ascii=False)[:6500])
