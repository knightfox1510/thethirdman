"""Counterfactual for NZ v IND 1st Test, Day 5: what if India had kept bowling the last ~15 overs? Hazards are estimated from the men's Test ball-by-ball archive (Cricsheet, men only, 2001 onward),
calibrated to this pitch with Day 5's own dismissals, then simulated ball by ball. Writes data/provenance/gill_sim.json.   python3 analysis/gill_sim.py
The simulation is a model of dismissal risk, not a prediction; the video says so."""
import json, glob, os, random, collections, math
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); D = f"{R}/data/cricsheet/tests"
BUCKETS = [(0, 10), (10, 30), (30, 60), (60, 100), (100, 150), (150, 250), (250, 9999)]
def bucket(n):
    for i, (a, b) in enumerate(BUCKETS):
        if a <= n < b: return i
exp = {"mid": [[0, 0] for _ in BUCKETS], "tail": [[0, 0] for _ in BUCKETS]}                # [balls, dismissals] by balls-faced bucket: middle order (pos 3-7) and tail (pos 8-11), innings 3-4, men's Tests since 2001
win = collections.defaultdict(lambda: [0, 0])                                               # windows: wickets in legal balls 630-720 by wickets down at ball 630
n_m = 0
for f in sorted(glob.glob(f"{D}/*.json")):
    d = json.load(open(f)); i = d["info"]
    if i.get("gender") != "male" or i["dates"][0] < "2001-06-01": continue
    n_m += 1
    for k, inn in enumerate(d["innings"]):
        if k < 2 or inn.get("declared") or inn.get("target"): continue                         # batting second time, no declaration, no chase (a chase changes intent)
        faced = collections.Counter(); order = []; wk = 0; balls = 0; w_at = None
        for ov in inn["overs"]:
            for dl in ov["deliveries"]:
                st, ns = dl["batter"], dl["non_striker"]
                for b in (st, ns):
                    if b not in order: order.append(b)
                ex = dl.get("extras", {}); legal = not ("wides" in ex or "noballs" in ex)
                pos = order.index(st) + 1; bk = bucket(faced[st])
                if "wides" not in ex:
                    side = "tail" if pos >= 8 else ("mid" if pos >= 3 else None)
                    if side: exp[side][bk][0] += 1
                    faced[st] += 1
                out = [w for w in dl.get("wickets", []) if w["kind"] not in ("retired hurt", "retired out", "obstructing the field")]
                for w in out:
                    po = w["player_out"]
                    if po == st and "wides" not in ex:
                        side = "tail" if pos >= 8 else ("mid" if pos >= 3 else None)
                        if side: exp[side][bk][1] += 1
                    wk += len(out) if False else 1
                if legal:
                    balls += 1
                    if balls == 630: w_at = wk
                    if 630 < balls <= 720 and w_at is not None: pass
        # window wickets: recount cleanly
        wk = 0; balls = 0; w0 = None; wwin = 0
        for ov in inn["overs"]:
            for dl in ov["deliveries"]:
                ex = dl.get("extras", {}); legal = not ("wides" in ex or "noballs" in ex)
                nw = sum(1 for w in dl.get("wickets", []) if w["kind"] not in ("retired hurt", "retired out", "obstructing the field"))
                if w0 is not None and balls < 720: wwin += nw
                wk += nw
                if legal:
                    balls += 1
                    if balls == 630: w0 = wk
        if w0 is not None: win[min(w0, 8)][0] += 1; win[min(w0, 8)][1] += wwin; win[("dist", min(w0, 8), min(wwin, 10))][0] += 1
H = {s: [(v[1] / v[0] if v[0] else 0.0, v[0], v[1]) for v in exp[s]] for s in exp}
print("matches", n_m); print("hazards per ball (mid):", [(round(h, 4), n, d) for h, n, d in H["mid"]]); print("hazards per ball (tail):", [(round(h, 4), n, d) for h, n, d in H["tail"]])
print("windows 630-720 legal balls by wickets down:", {k: v for k, v in sorted(win.items(), key=lambda kv: str(kv[0])) if not isinstance(k, tuple)})
five = {k[2]: v[0] for k, v in win.items() if isinstance(k, tuple) and k[1] == 5}; print("five down, wickets in next 15 overs:", dict(sorted(five.items())))
json.dump({"hazard": H, "buckets": BUCKETS, "windows": {str(k): v for k, v in win.items()}}, open(f"{R}/data/provenance/gill_sim.json", "w"))
