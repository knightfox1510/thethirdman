"""Shot placement and delivery zones for India's first innings (NZ v IND, 1st Test, 2026) from the owner's ball-by-ball commentary capture. Direction and line/length are OUR keyword read of the text
(approximate zones, not tracked coordinates). Off side is drawn on the right for every batter. Writes data/provenance/nz_shots.json.   python3 analysis/shots.py"""
import json, os, re, collections
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_IN = os.environ.get("SHOTS_IN", "nz_ind_1st_test_day3.json"); SRC_OUT = os.environ.get("SHOTS_OUT", "nz_shots.json"); INNS = [int(i) for i in os.environ.get("SHOTS_INN", "2").split(",")]
d = json.load(open(f"{R}/data/cricbuzz/{SRC_IN}")); C = [x for x in d["comments"] if x["inningsId"] in INNS]


def text(x):
    t = x["commText"]
    for v in x.get("commentaryFormats", {}).values():
        for fid, val in zip(v["formatId"], v["formatValue"]): t = t.replace(fid, val)
    return t.replace("\\n", "\n")


M = re.compile(r"^(.+?) to (.+?), (no run|\d+ runs?|FOUR|SIX|out [^,]+|leg byes?|byes?|wide|no ball)[^,]*(?:, ?(.*))?$", re.S)
# zones: angle in degrees from straight down the ground (0); + = off side, - = leg side; (pattern, angle) in priority order
ZONES = [
    (r"behind square on the off|behind square off|off-side behind square|behind square on the off-side", 118),
    (r"third man|fine third|wide of gully|past gully|through gully|between (?:second )?slip and gully|past (?:the )?slip|through the slip|over the slip|slip cordon|wide of slip|over gully|past backward point|between slip", 140),
    (r"backward point|deep point|behind point|wide of point|to point|through point|past point|point fielder|\bpoint\b|square of the wicket|square on the off|cuts? |cut ", 105),
    (r"extra cover|deep cover|through cover|wide of cover|to cover|past cover|over cover|\bcover\b|cover-point", 62),
    (r"mid-?off|wide of mid-off|straight of mid-off", 28),
    (r"down the ground|straight down|back past the bowler|past the bowler|straight of the bowler|long-?off|long-?on|straight drive|straight over|over the bowler|back over the bowler", 0),
    (r"mid-?on|wide of mid-on|straight of mid-on", -28),
    (r"mid-?wicket|midwicket|wide of mid-wicket|deep mid", -62),
    (r"backward square leg|behind square on the leg|square leg|deep square", -105),
    (r"fine leg|fine on the leg|down the leg|glanc|paddle|off the pads|leg-side|leg side|behind square on the leg|behind square", -140),
]
LINE = [("wide", r"wide outside off|well wide|way outside|wide of off|wide on the off"), ("outside_off", r"outside off|outside the off|fifth stump|sixth stump|just outside"), ("off", r"\bon off\b|off stump|around off|on the off stump|\boff\b"),
        ("middle", r"on middle|middle stump|middle and|\bmiddle\b|on the stumps|on the stumps"), ("leg", r"leg stump|down the leg|on the pads|on leg|\bon the legs?\b|leg side|\bleg\b")]
LEN = [("yorker", r"yorker"), ("short", r"\bbouncer|\bbumper|\bshort (?:delivery|ball|outside|and|on|down|around|across)|^short\b|\bshort,|shortish|short and"), ("short_of_length", r"short of (?:a )?length|back of (?:a )?length|short-of-a-length"), ("good", r"good length|\blength delivery|\blength outside|length ball|good-length|on a length"), ("full", r"\bfull|fullish|driving length|half-volley|half volley")]
def pick(t, table):
    t = t.lower()
    for k, p in table:
        if re.search(p, t): return k
def zone(shot):
    best = None
    for pat, ang in ZONES:
        m = re.search(pat, shot)
        if m and (best is None or m.start() < best[0]): best = (m.start(), ang)
    return None if best is None else best[1]
rows = sorted(C, key=lambda x: x["timestamp"]); out = []
for x in rows:
    if not x.get("overNumber"): continue
    t = text(x); m = M.match(t.split("\n")[0]) or M.match(t)
    if not m: continue
    res, desc = m.group(3), (m.group(4) or "")
    runs = x.get("totalRuns", 0); legal = res not in ("wide",) and "no ball" not in res
    bat = (x.get("batsmanStriker") or {}).get("batName") or m.group(2)
    day = (3 if x["overNumber"] > 38.6 + 1e-9 else 2) if x["inningsId"] == 2 else 0
    sess = 1 if x["overNumber"] <= 65.6 else (2 if x["overNumber"] <= 92.6 else 3) if day == 3 else 0
    shot = desc.lower()
    out.append({"inn": x["inningsId"], "over": x["overNumber"], "day": day, "sess": sess, "bowler": m.group(1), "bat": bat, "res": res, "runs": runs, "len": pick(desc, LEN), "line": pick(desc, LINE), "ang": zone(shot) if (runs > 0 and "bye" not in res and "wide" not in res) else None, "wkt": "WICKET" in x.get("event", "")})
json.dump(out, open(f"{R}/data/provenance/{SRC_OUT}", "w"))
score = [o for o in out if o["runs"] > 0 and "bye" not in o["res"] and "wide" not in o["res"]]
print(len(out), "balls;", len(score), "scoring shots;", sum(1 for o in score if o["ang"] is not None), "placed")
for b in ("KL Rahul", "Rahul", "Shubman Gill", "Rishabh Pant", "Devdutt Padikkal", "Yashasvi Jaiswal"):
    s = [o for o in score if o["bat"] == b]; p = [o for o in s if o["ang"] is not None]
    off = sum(o["runs"] for o in p if o["ang"] > 0); leg = sum(o["runs"] for o in p if o["ang"] < 0); st = sum(o["runs"] for o in p if o["ang"] == 0)
    print(b, len(s), len(p), "runs placed", sum(o["runs"] for o in p), "off", off, "leg", leg, "straight", st)
print("line counts day3", collections.Counter(o["line"] for o in out if o["day"] == 3)); print("len counts day3", collections.Counter(o["len"] for o in out if o["day"] == 3))
for s in (1, 2, 3): print("sess", s, collections.Counter(o["line"] for o in out if o["sess"] == s))
