"""Pitch behaviour on Day 5 (our keyword counts on the ball-by-ball text by session) and the Basin Reserve in the men's Test archive. Writes data/provenance/gill_pitch.json.   python3 analysis/gill_pitch.py"""
import json, re, glob, collections, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(f"{R}/data/cricbuzz/nz_ind_1st_test_day5.json"))
def text(x):
    s = x["commText"]
    for v in x.get("commentaryFormats", {}).values():
        for a, b in zip(v["formatId"], v["formatValue"]): s = s.replace(a, b)
    return s
C3 = sorted([x for x in d["comments"] if x["inningsId"] == 3 and x.get("overNumber") and x["overNumber"] > 44.6], key=lambda x: x["timestamp"]); M = re.compile(r"^(.+?) to (.+?), ")
FS = re.compile(r"beaten|inside edge|outside edge|thick edge|edge|misses|missed|play and a miss|plays and misses|lbw|appeal|uppish|lobs", re.I)
OUT = {"false_shot_per_100": {}}
for nm, a, b in (("morning", 44.6, 70.6), ("middle", 70.6, 95.6), ("evening", 95.6, 119.7), ("last15", 104.6, 119.7)):
    xs = [text(x) for x in C3 if a < x["overNumber"] <= b and M.match(text(x).split("\n")[0])]; OUT["false_shot_per_100"][nm] = [round(100 * sum(1 for s in xs if FS.search(s)) / len(xs), 1), len(xs)]
ov = collections.OrderedDict()
for x in C3:
    if x["overNumber"] > 104.6:
        m = M.match(text(x).split("\n")[0])
        if m: ov.setdefault(int(x["overNumber"]), m.group(1))
OUT["last15_bowlers"] = dict(collections.Counter(ov.values())); OUT["last15_order"] = list(ov.values())
a = collections.defaultdict(lambda: [0, 0, 0, 0])
for f in sorted(glob.glob(f"{R}/data/cricsheet/tests/*.json")):
    dd = json.load(open(f)); i = dd["info"]
    if i.get("gender") != "male" or i["dates"][0] < "2001-06-01" or i.get("city") not in ("Wellington", "Christchurch", "Hamilton", "Auckland", "Dunedin", "Mount Maunganui", "Napier"): continue
    key = "Basin Reserve" if "Basin" in i.get("venue", "") else "other NZ venues"; a[key][2] += 1; a[key][3] += i.get("outcome", {}).get("result") == "draw"
    for k, inn in enumerate(dd["innings"]):
        if k < 2: continue
        for o in inn["overs"]:
            for dl in o["deliveries"]:
                ex = dl.get("extras", {}); a[key][1] += not ("wides" in ex or "noballs" in ex); a[key][0] += sum(1 for w in dl.get("wickets", []) if w["kind"] not in ("retired hurt", "retired out", "obstructing the field"))
OUT["ground"] = {k: {"matches": v[2], "draws": v[3], "wkts_per_100_overs_inn34": round(v[0] * 600 / v[1], 1), "balls": v[1]} for k, v in a.items()}
json.dump(OUT, open(f"{R}/data/provenance/gill_pitch.json", "w"), indent=1); print(json.dumps(OUT, indent=1))
