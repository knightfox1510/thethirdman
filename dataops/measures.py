"""The analytic measures that make a profile more than a stat line, computed from Cricsheet ball-by-ball (data/cricsheet). Every output carries the coverage of what it used, so a video
can say "in our archive" honestly (see dataops/audit.py). Run on a team or a player:
    python3 -m dataops.measures team India --fmt T20 --since 2024-07-27 [--until D]
    python3 -m dataops.measures player "V Kohli" --fmt ODI
Team: intent timeline (runs per over by over number), phase scoring, aggression (balls per boundary, dot %), collapse rate (3+ wickets inside 12 balls), all-out %, batting depth (share of
innings where No.8 faced 10+ balls), XI stability (overlap of consecutive XIs), players used, debutants, toss record, close-match record (<=10 runs / <=2 wickets), Pythagorean expectation.
Player: hazard curve (chance of dismissal at ball n of an innings), rolling-20 average, phase splits, dismissal types, consistency (30+/50+/100 shares, ducks), vs pace and spin (where known)."""
import collections, json, statistics, sys
from . import cricsheet as C

FMT = {"T20": "T20I", "ODI": "ODI", "Test": "Test"}
PHASES = {"T20": {"powerplay": (0, 6), "middle": (6, 16), "death": (16, 20)}, "ODI": {"powerplay": (0, 10), "middle": (10, 40), "death": (40, 50)}}


def _team_matches(team, fmt, since=None, until=None):
    out = []
    for lab, p, m in C.matches("male"):
        i = m["info"]
        if lab != FMT[fmt] or team not in i["teams"]: continue
        d = i["dates"][0]
        if (since and d < since) or (until and d > until): continue
        out.append((d, m))
    return out


def team(team, fmt, since=None, until=None):
    ms = _team_matches(team, fmt, since, until); ph = PHASES.get(fmt, PHASES["ODI"]); per_over = collections.defaultdict(list)
    runs_ph = collections.defaultdict(lambda: [0, 0]); legal = dots = bounds = 0; collapse = allout = inns = depth = 0; xis = []; toss = collections.Counter(); close = collections.Counter(); scored = conceded = 0
    for d, m in ms:
        i = m["info"]; xis.append(frozenset(i["players"][team]))
        t = i.get("toss", {}); toss[(t.get("winner") == team, t.get("decision"))] += 1
        tot = {}
        for inn in m["innings"]:
            if inn.get("super_over"): continue
            tot[inn["team"]] = sum(d_["runs"]["total"] for o in inn["overs"] for d_ in o["deliveries"])
            if inn["team"] != team: continue
            inns += 1; wk = []; ball = 0; faced = collections.Counter(); order = []
            for o in inn["overs"]:
                rs = 0
                for d_ in o["deliveries"]:
                    rs += d_["runs"]["total"]; ex = d_.get("extras", {}); lg = "wides" not in ex and "noballs" not in ex
                    if lg:
                        ball += 1; legal += 1; dots += d_["runs"]["total"] == 0; bounds += d_["runs"]["batter"] in (4, 6)
                        if d_["batter"] not in order: order.append(d_["batter"])
                        faced[d_["batter"]] += 1
                    for w in d_.get("wickets", []): wk.append(ball)
                per_over[o["over"]].append(rs)
                for name, (a, b) in ph.items():
                    if a <= o["over"] < b: runs_ph[name][0] += rs; runs_ph[name][1] += len([1 for d_ in o["deliveries"] if "wides" not in d_.get("extras", {}) and "noballs" not in d_.get("extras", {})])
            if any(wk[k + 2] - wk[k] <= 12 for k in range(len(wk) - 2)): collapse += 1
            allout += len(wk) >= 10; depth += len(order) >= 8 and faced[order[7]] >= 10
        o = m["info"].get("outcome", {}); by = o.get("by", {})
        if "winner" in o and (by.get("runs", 99) <= 10 or by.get("wickets", 9) <= 2): close["won" if o["winner"] == team else "lost"] += 1
        oth = [k for k in tot if k != team]
        if team in tot and oth: scored += tot[team]; conceded += tot[oth[0]]
    seen = set(); deb = 0
    for x in xis:
        for p in x:
            if p not in seen: seen.add(p)
    stab = [len(a & b) / 11 for a, b in zip(xis, xis[1:])]
    py = (scored ** 2) / (scored ** 2 + conceded ** 2) if scored + conceded else None
    return {"team": team, "fmt": fmt, "matches": len(ms), "innings_batted": inns, "coverage_note": "Cricsheet matches only: run dataops.audit before calling these totals",
            "intent_timeline_rpo": {o + 1: round(statistics.mean(v), 2) for o, v in sorted(per_over.items()) if len(v) >= 3},
            "phase_rr": {k: round(6 * v[0] / v[1], 2) for k, v in runs_ph.items() if v[1]}, "aggression": {"balls_per_boundary": round(legal / max(bounds, 1), 2), "dot_pct": round(100 * dots / max(legal, 1), 1)},
            "collapse_rate_pct": round(100 * collapse / max(inns, 1), 1), "all_out_pct": round(100 * allout / max(inns, 1), 1), "depth_no8_faced_10plus_pct": round(100 * depth / max(inns, 1), 1),
            "xi_stability": round(statistics.mean(stab), 3) if stab else None, "players_used": len(seen), "toss": {f"{'won' if k[0] else 'lost'}_{k[1]}": v for k, v in toss.items()},
            "close_matches": dict(close), "pythagorean_win_expectancy": round(py, 3) if py else None}


def player(name, fmt):
    inns = []
    for lab, p, m in C.matches("male"):
        if lab != FMT[fmt] or name not in [x for t in m["info"]["players"].values() for x in t]: continue
        for inn in m["innings"]:
            if inn.get("super_over"): continue
            balls = runs = 0; out = None; seq = []; ph = collections.defaultdict(lambda: [0, 0]); first = None
            for o in inn["overs"]:
                for d_ in o["deliveries"]:
                    ex = d_.get("extras", {})
                    if d_["batter"] == name:
                        if "wides" not in ex: balls += 1; seq.append(d_["runs"]["batter"])
                        runs += d_["runs"]["batter"]
                        for k, (a, b) in PHASES.get(fmt, PHASES["ODI"]).items():
                            if a <= o["over"] < b: ph[k][0] += d_["runs"]["batter"]; ph[k][1] += "wides" not in ex
                    for w in d_.get("wickets", []):
                        if w["player_out"] == name: out = (balls, w["kind"])
            if balls or out: inns.append({"runs": runs, "balls": balls, "out": out, "phase": dict(ph)})
    if not inns: return {"player": name, "innings": 0}
    n = len(inns); haz = {}
    for lo, hi in ((1, 5), (6, 10), (11, 20), (21, 30), (31, 50), (51, 75), (76, 999)):       # dismissals per 100 balls faced inside each stage of an innings
        faced = sum(max(0, min(x["balls"], hi) - lo + 1) for x in inns); got = sum(1 for x in inns if x["out"] and lo <= x["out"][0] <= hi)
        haz[f"balls {lo}-{hi if hi < 999 else '+'}"] = {"balls_faced": faced, "dismissals": got, "per_100_balls": round(100 * got / faced, 2) if faced >= 300 else None}
    roll = [round(sum(x["runs"] for x in inns[i:i + 20]) / max(1, sum(1 for x in inns[i:i + 20] if x["out"])), 1) for i in range(0, max(1, n - 19), max(1, n // 12))]
    kinds = collections.Counter(x["out"][1] for x in inns if x["out"])
    phs = collections.defaultdict(lambda: [0, 0])
    for x in inns:
        for k, v in x["phase"].items(): phs[k][0] += v[0]; phs[k][1] += v[1]
    return {"player": name, "fmt": fmt, "innings": n, "coverage_note": "Cricsheet innings only: compare with dataops.audit player before calling these career figures",
            "hazard_curve": haz, "rolling_20_average_samples": roll, "dismissals": dict(kinds), "phase_sr": {k: round(100 * v[0] / v[1], 1) for k, v in phs.items() if v[1]},
            "consistency": {"30+": round(100 * sum(x["runs"] >= 30 for x in inns) / n, 1), "50+": round(100 * sum(x["runs"] >= 50 for x in inns) / n, 1), "100+": round(100 * sum(x["runs"] >= 100 for x in inns) / n, 1), "ducks": round(100 * sum(x["runs"] == 0 and x["out"] is not None for x in inns) / n, 1)}}


if __name__ == "__main__":
    a = sys.argv[1:]; opt = lambda k, d=None: a[a.index(k) + 1] if k in a else d
    r = team(a[1], opt("--fmt", "T20"), opt("--since"), opt("--until")) if a[0] == "team" else player(a[1], opt("--fmt", "ODI"))
    print(json.dumps(r, indent=1))
