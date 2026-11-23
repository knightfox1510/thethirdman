"""Part 2 of the Day 5 counterfactual: calibrate the Test-archive hazards (analysis/gill_sim.py) to this pitch with NZ's own second innings, then simulate the last overs and the three chances. Writes data/provenance/gill_sim_results.json."""
import json, os, random, collections
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G = json.load(open(f"{R}/data/provenance/gill_sim.json")); H = {s: [h for h, n, d in G["hazard"][s]] for s in ("mid", "tail")}; BK = G["buckets"]
H["tail"][6] = H["tail"][5]
def bucket(n):
    for i, (a, b) in enumerate(BK):
        if a <= n < b: return i
SH = [o for o in json.load(open(f"{R}/data/provenance/nz_shots_d5.json")) if o["inn"] == 3]
order = []
for o in SH:
    if o["bat"] not in order: order.append(o["bat"])
print("order", order)
POS = {b: i + 1 for i, b in enumerate(order)}; POS["Jamieson"] = 8; POS["Smith"] = 9; POS["Henry"] = 10; POS["Duffy"] = 11
def hz(pos, faced, f=1.0): return f * (H["tail"] if pos >= 8 else H["mid"])[bucket(faced)]
# --- calibrate: expected dismissals on Day 5 given who faced what
faced = collections.Counter(); exp_d5 = 0.0; exp_all = 0.0; balls_d5 = 0
for o in SH:
    wide = o["res"] == "wide"
    if not wide:
        h = hz(POS[o["bat"]], faced[o["bat"]]); exp_all += h
        if o["over"] > 44.6: exp_d5 += h; balls_d5 += 1
        faced[o["bat"]] += 1
f_pitch = 3 / exp_d5; print("expected dismissals on Day 5 at archive rates", round(exp_d5, 2), "observed 3 -> pitch factor", round(f_pitch, 3), "balls", balls_d5)
# --- strike rotation: share of balls with an odd number of runs (last 24 overs)
last = [o for o in SH if o["over"] > 95.6]; q = sum(1 for o in last if o["runs"] % 2 == 1 and o["res"] in ("1 run", "3 runs")) / len(last); print("odd-run share", round(q, 3), len(last))
def at_ball(over):
    """state of the innings just before the ball at `over`: wickets down and balls faced by each batter."""
    fc = collections.Counter(); w = 0
    for o in SH:
        if o["over"] >= over - 1e-9: break
        if o["res"] != "wide": fc[o["bat"]] += 1
        if o["wkt"]: w += 1
    return w, fc
def sim(w0, batters, tail, balls, f, mult=1.0, n=100000, need=None, seed=1):
    """batters: [(name, pos, faced)] the two at the crease; tail: [(name, pos)] to come; returns distribution of wickets and P(all out)."""
    rnd = random.Random(seed); dist = collections.Counter(); allout = 0
    for _ in range(n):
        cr = [list((nm, p, fc)) for nm, p, fc in batters]; nxt = list(tail); w = w0; strike = 0; b = 0
        while b < balls and w < 10:
            nm, p, fc = cr[strike]; h = min(0.5, hz(p, fc, f) * mult); b += 1
            if rnd.random() < h:
                w += 1
                if w >= 10: break
                if nxt: nn = nxt.pop(0); cr[strike] = [nn[0], nn[1], 0]
                else: break
            else:
                cr[strike][2] += 1
                if rnd.random() < q: strike ^= 1
            if b % 6 == 0: strike ^= 1
        dist[w - w0] += 1; allout += (w >= 10)
    return {k: v / n for k, v in sorted(dist.items())}, allout / n
w, fc = at_ball(104.7)                                        # 15 overs to go (after 104.6)
print("state at 15 overs to go: wickets", w, {k: fc[k] for k in ("Daryl Mitchell", "Glenn Phillips")})
TAIL = [("Kyle Jamieson", 8), ("Nathan Smith", 9), ("Matt Henry", 10), ("Jacob Duffy", 11)]
bat0 = [("Daryl Mitchell", POS["Daryl Mitchell"], fc["Daryl Mitchell"]), ("Glenn Phillips", POS["Glenn Phillips"], fc["Glenn Phillips"])]
OUT = {"f_pitch": f_pitch, "exp_d5": exp_d5, "q": q, "w_at_15": w, "balls_faced_at_15": {k: fc[k] for k in ("Daryl Mitchell", "Glenn Phillips")}, "scen": {}}
for nm, f in (("this_pitch", f_pitch), ("archive_average", 1.0)):
    for balls in (90, 150, 240, 360):
        d, a = sim(w, bat0, TAIL, balls, f); OUT["scen"][f"{nm}_{balls}"] = {"p_win": a, "dist": d}; print(nm, balls, "P(5+ wickets)", round(a, 4), {k: round(v, 3) for k, v in d.items()})
for m in (1.25, 1.5, 2.0, 3.0):
    d, a = sim(w, bat0, TAIL, 90, f_pitch, mult=m); OUT["scen"][f"attack_{m}"] = {"p_win": a, "dist": d}; print("attack x", m, round(a, 4))
# --- the three chances: P(India bowl NZ out in the rest of the day) with vs without the dismissal
def rest_of_day(over, extra_wkt=False, f=f_pitch):
    w0, fcn = at_ball(over); balls_left = int(round((90 - (over - 44.6) ) * 6)) if False else int(round((90.0 - (int(over) - 44 + (over % 1) * 10 / 6 )) * 6))
    cur = [b for b in ("Tom Blundell", "Daryl Mitchell", "Glenn Phillips") if fcn[b] > 0 or b in ("Daryl Mitchell",)]
    return w0, fcn, balls_left
for label, over, who, pair in (("run-out missed (73.1, Mitchell on 12)", 73.1, "Daryl Mitchell", ("Tom Blundell", "Daryl Mitchell")), ("bat-pad, no short leg (88.2, Mitchell on 24)", 88.2, "Daryl Mitchell", ("Glenn Phillips", "Daryl Mitchell")), ("Kamboj kicker, drop (94.4, Mitchell on 24)", 94.4, "Daryl Mitchell", ("Glenn Phillips", "Daryl Mitchell"))):
    w0, fcn = at_ball(over); ov_in_day = (int(over) - 44) + (over % 1) * 10 / 6 - 0.0; balls_left = int(round((90 - (over - 44.6 + 0.0 if False else (int(over) + (over % 1) * 10 / 6 - 44.6 - 0.0))) * 6)); 
    elapsed_overs = (int(over) + (round(over % 1, 1) * 10) / 6) - (44 + 6 / 6)   # over 44.6 ends at 45.0 overs completed
    balls_left = int(round((90 - elapsed_overs) * 6))
    cur = [(n, POS[n], fcn[n]) for n in pair]; stay = [c for c in cur]
    tailq = [(nm, POS[nm]) for nm in order if nm not in pair and fcn[nm] == 0 and nm not in ("Tom Latham", "Henry Nicholls", "Devon Conway", "Rachin Ravindra")] 
    rest = [t for t in TAIL]
    pool = [(nm, POS[nm]) for nm in ("Tom Blundell", "Glenn Phillips") if nm not in pair and fcn[nm] == 0] + TAIL
    base_d, base_a = sim(w0, cur, pool, balls_left, f_pitch, n=100000)
    out_i = [i for i, (n, p, fcz) in enumerate(cur) if n == who][0]; surv = cur[1 - out_i]
    nb = pool[0]; pool2 = pool[1:]
    chg_d, chg_a = sim(w0 + 1, [surv, (nb[0], nb[1], 0)], pool2, balls_left, f_pitch, n=100000)
    OUT["scen"][f"chance_{over}"] = {"label": label, "wickets_down": w0, "balls_left": balls_left, "p_win_actual": base_a, "p_win_if_taken": chg_a, "pair": [c[0] for c in cur], "faced": [c[2] for c in cur]}
    print(label, "wkts", w0, "balls left", balls_left, "P(win) actual", round(base_a, 4), "-> if taken", round(chg_a, 4))
json.dump(OUT, open(f"{R}/data/provenance/gill_sim_results.json", "w"), indent=1, default=str)
