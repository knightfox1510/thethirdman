"""Win-probability trajectory, turning points and player value for the NZ v IND ODIs we have ball-by-ball (4th and 5th, from the Cricbuzz captures).
    CS_DIR=... python3 analysis/nz_ind_wp.py
Writes data/series/nz_ind_2026/analysis/<match>_wp.csv and prints the biggest swings. Win probability is from dataops/winprob.py (fitted on the Cricsheet ODI archive; validated there)."""
import csv, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from dataops import winprob

from analysis_cfg_shim import *  # noqa
OUT = "data/series/nz_ind_2026"; M = winprob.load()
MATCHES = {k: {"india_bats": INFO[k]["india_bats"], "label": INFO[k]["label"], "revision": INFO[k].get("revision")} for k in STEMS}


def read(stem):
    rows = list(csv.DictReader(open(f"{OUT}/{stem}_balls.csv", encoding="utf-8")))
    for r in rows:
        for k in ("inning", "ball_no", "runs", "bat_runs", "score_after", "wkts_after"): r[k] = int(r[k])
        r["over"] = float(r["over"]); r["legal"] = r["legal"] == "True"; r["wicket"] = r["wicket"] == "True"
    return rows


def trajectory(stem):
    rows = read(stem); ib = MATCHES[stem]["india_bats"]; target = max(r["score_after"] for r in rows if r["inning"] == 1) + 1; rev = MATCHES[stem].get("revision")
    out = []
    p0 = {1: float(M.p_first(0, 300, 0)[0]), 2: float(M.p_chase(target, 300, 0)[0])}
    prev = {1: p0[1], 2: p0[2]}; legal = {1: 0, 2: 0}
    for r in rows:
        inn = r["inning"]; legal[inn] += r["legal"]; left = 300 - legal[inn]
        if inn == 1: wp = float(M.p_first(r["score_after"], left, r["wkts_after"])[0])
        else:
            tg, tot = (rev["target"], rev["balls_total"]) if (rev and legal[2] >= rev["after_legal_ball"]) else (target, 300)           # a rain-revised chase: the DLS target and the shorter innings
            wp = float(M.p_chase(tg - r["score_after"], tot - legal[2], r["wkts_after"])[0])
        wp_india = wp if inn == ib else 1 - wp                         # win probability of the side batting that innings, restated for India
        if inn == 1: bat_wp = wp; prev_india = prev[1] if ib == 1 else 1 - prev[1]
        else: prev_india = prev[2] if ib == 2 else 1 - prev[2]
        d_bat = wp - prev[inn]; prev[inn] = wp
        out.append({**{k: r[k] for k in ("inning", "over", "ball_no", "legal", "bowler", "batter", "runs", "wicket", "dismissal", "event", "score_after", "wkts_after")}, "bat_wp": round(wp, 4), "india_wp": round(wp_india, 4), "delta_bat_wp": round(d_bat, 4), "text": r["text"][:240]})
    return out, target, p0


def main():
    res = {}
    for stem, cfg in MATCHES.items():
        tr, target, p0 = trajectory(stem); res[stem] = tr
        with open(f"{OUT}/analysis/{stem}_wp.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(tr[0].keys())); w.writeheader(); w.writerows(tr)
        ib = cfg["india_bats"]
        print(f"\n=== {cfg['label']} ({stem}): target {target}; P(side batting first wins) at ball 0 = {p0[1]:.3f}; P(chase wins) at ball 0 = {p0[2]:.3f}")
        big = sorted(tr, key=lambda r: -abs(r["delta_bat_wp"]))[:10]
        for r in big:
            who = "India" if r["inning"] == ib else "NZ"
            print(f"  inn{r['inning']} {r['over']:>5} {who:5s} bat swing {r['delta_bat_wp']:+.3f} -> India WP {r['india_wp']:.2f} | {r['bowler']} to {r['batter']} | {r['text'][:110]}")
    return res


if __name__ == "__main__":
    main()
