"""Story-level metrics for the 5th ODI (and the 4th for comparison): win-probability curve by over, the tipping point, the chase's required rate against what NZ scored, the cost of drops,
the last-wicket stand's value, collapses, and the series context (Wikipedia for matches 1-3).
    CS_DIR=... python3 analysis/nz_ind_story.py   -> data/series/nz_ind_2026/analysis/story.json and a printed digest"""
import csv, json, os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = "data/series/nz_ind_2026"; AN = OUT + "/analysis"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nz_ind_cfg import INDIA_BATS


def wp(stem):
    rows = list(csv.DictReader(open(f"{AN}/{stem}_wp.csv", encoding="utf-8")))
    for r in rows:
        r["inning"] = int(r["inning"]); r["over"] = float(r["over"]); r["india_wp"] = float(r["india_wp"]); r["delta_bat_wp"] = float(r["delta_bat_wp"]); r["score_after"] = int(r["score_after"]); r["wkts_after"] = int(r["wkts_after"]); r["runs"] = int(r["runs"]); r["legal"] = r["legal"] == "True"
    return rows


def main():
    out = {}
    for stem in INDIA_BATS:
        rows = wp(stem); ib = INDIA_BATS[stem]; R = {}
        # WP curve at the end of each 5 overs (India's win probability)
        curve = []
        for inn in (1, 2):
            last = {}
            for r in rows:
                if r["inning"] == inn: last[int(r["over"] - 1e-9) if r["over"] % 1 else int(r["over"]) - 1] = r
            for ov in sorted(last):
                if (ov + 1) % 5 == 0 or ov == max(last): curve.append({"inning": inn, "after_over": ov + 1, "score": f"{last[ov]['score_after']}/{last[ov]['wkts_after']}", "india_wp": last[ov]["india_wp"]})
        R["curve"] = curve
        # tipping point: the last time India's win probability crossed 50% (and stayed on its final side)
        final = rows[-1]["india_wp"]; side = final >= .5; tip = None
        for r in rows:
            if (r["india_wp"] >= .5) != side: tip = None
            elif tip is None: tip = r
        R["tipping_point"] = {"over": tip["over"], "inning": tip["inning"], "score": f"{tip['score_after']}/{tip['wkts_after']}", "india_wp": tip["india_wp"], "text": tip["text"][:160]} if tip else None
        R["india_wp_extremes"] = {"min": min(rows, key=lambda r: r["india_wp"])["india_wp"], "min_at": (lambda r: f"inn{r['inning']} over {r['over']} ({r['score_after']}/{r['wkts_after']})")(min(rows, key=lambda r: r["india_wp"])), "max": max(rows, key=lambda r: r["india_wp"])["india_wp"], "max_at": (lambda r: f"inn{r['inning']} over {r['over']} ({r['score_after']}/{r['wkts_after']})")(max(rows, key=lambda r: r["india_wp"]))}
        # chase: required vs actual
        chase = [r for r in rows if r["inning"] == 2]; target = max(r["score_after"] for r in rows if r["inning"] == 1) + 1; seen = 0; req = []
        for r in chase:
            seen += r["legal"]
            if r["legal"] and seen % 60 == 0 or r is chase[-1]:
                left = 300 - seen; need = target - r["score_after"]
                req.append({"after_over": seen // 6, "score": f"{r['score_after']}/{r['wkts_after']}", "need": need, "balls_left": left, "required_rate": round(6 * need / left, 2) if left else None, "run_rate_so_far": round(6 * r["score_after"] / seen, 2)})
        R["chase_checkpoints"] = req
        out[stem] = R
    # the last-wicket stand and collapses in the 5th (India batting first)
    rows = wp("nz_ind_5odi"); inn1 = [r for r in rows if r["inning"] == 1]
    i9 = next(i for i, r in enumerate(inn1) if r["wkts_after"] == 9); start = inn1[i9]; rest = inn1[i9 + 1:]
    out["nz_ind_5odi"]["last_wicket_stand"] = {"from": f"{start['score_after']}/9 to {inn1[-1]['score_after']}/10", "runs": inn1[-1]["score_after"] - start["score_after"], "legal_balls": sum(r["legal"] for r in rest),
                                               "india_wp_before": start["india_wp"], "india_wp_after": inn1[-1]["india_wp"], "wp_gain": round(inn1[-1]["india_wp"] - start["india_wp"], 3)}
    wk = [r for r in inn1 if r["wicket"] == "True"]
    out["nz_ind_5odi"]["india_fall_of_wickets"] = [(r["score_after"], r["over"]) for r in wk]
    # runs scored after dropped chances (both matches, from the drops in nz_ind_deep summary)
    summ = json.load(open(f"{AN}/summary.json")); drops = {}
    for stem, M in summ["matches"].items():
        ib = INDIA_BATS[stem]; rows_ = []
        for d in M["drops"]:
            fin = d["batter_final_runs"]; at = d["batter_runs_at_drop"]
            try: cost = int(fin) - int(at)
            except Exception: cost = None
            fielding = "NZ" if d["inning"] == ib else "India"                     # a drop in India's batting innings was by NZ
            rows_.append({"fielding_side": fielding, "batter": d["batter"], "over": d["over"], "runs_at_drop": at, "final": fin, "runs_after_drop": cost})
        tot = collections.defaultdict(int); seen = set()
        for r in rows_:                                                          # two chances to the same batter in one innings: the runs after the FIRST drop count once
            key = (r["fielding_side"], r["batter"])
            if r["runs_after_drop"] and key not in seen: tot[r["fielding_side"]] += r["runs_after_drop"]; seen.add(key)
        drops[stem] = {"list": rows_, "runs_conceded_after_drops": dict(tot)}
    out["drops"] = drops
    out["series"] = {"source": "Wikipedia, 'Indian cricket team in New Zealand in 2026-27' (Tier C; cites Cricinfo match reports); matches 4 and 5 are also in our own captures",
                     "matches": [{"n": 1, "date": "2026-11-04", "venue": "Eden Park, Auckland", "result": "India won by 5 wickets (DLS): NZ 185 (40.2), India 143/5 (22.4), target 143 from 32", "motm": "Anshul Kamboj", "top": "Kohli 74 (51); Arshdeep 4/70; Duffy 3/49", "ball_by_ball": True},
                                 {"n": 2, "date": "2026-11-07", "venue": "Wellington Regional Stadium", "result": "India won by 4 runs (DLS): NZ 134 (41), India 113/7 (26), par 109", "motm": "Gurnoor Brar (4/30)", "top": "Mitchell 55 (104); Iyer 30 (46); Jamieson 3/35", "note": "Fisher replaced Tickner as a concussion substitute", "ball_by_ball": True},
                                 {"n": 3, "date": "2026-11-10", "venue": "Seddon Park, Hamilton", "result": "No result (rain, no play)", "ball_by_ball": False},
                                 {"n": 4, "date": "2026-11-13", "venue": "Bay Oval, Mount Maunganui", "result": "New Zealand won by 244 runs: NZ 333, India 89 (26.4)", "motm": "Matt Henry (6/27)", "top": "Young 125 (108)", "note": "Iyer captained India in ODIs for the first time", "ball_by_ball": True},
                                 {"n": 5, "date": "2026-11-15", "venue": "Bay Oval, Mount Maunganui", "result": "India won by 22 runs: India 209 (42.1), NZ 187 (48.1)", "motm": "Arshdeep Singh (3/30)", "top": "Axar 46 (55); Santner 3/47; Foxcroft 31 (42)", "note": "Yash Thakur ODI debut", "ball_by_ball": True}],
                     "result": "India won the series 3-1 (one no result)"}
    for stem in INDIA_BATS:
        rows = wp(stem); bs = list(csv.DictReader(open(f"{OUT}/{stem}_balls.csv", encoding="utf-8"))); wk = list(csv.DictReader(open(f"{OUT}/{stem}_wickets.csv", encoding="utf-8")))
        fld = collections.defaultdict(lambda: {"catches": 0, "catch_swing": 0.0})
        for w in wk:
            if w["kind"] == "caught" and w["fielder"]:
                sw = next((-r["delta_bat_wp"] for r in rows if r["inning"] == int(w["inning"]) and abs(r["over"] - float(w["over"])) < 1e-9 and r["wicket"] == "True"), 0)
                fld[w["fielder"]]["catches"] += 1; fld[w["fielder"]]["catch_swing"] += sw
        out[stem]["fielding"] = {k: {"catches": v["catches"], "catch_swing": round(v["catch_swing"], 3)} for k, v in sorted(fld.items(), key=lambda kv: -kv[1]["catch_swing"])}
        col = {}
        for inn in (1, 2):
            lb = [r for r in rows if r["inning"] == inn]; best = None; legal_idx = []
            n = 0
            for r in lb:
                n += r["legal"]; legal_idx.append(n)
            for i, r in enumerate(lb):
                j = i
                while j < len(lb) and legal_idx[j] - legal_idx[i] < 60: j += 1
                win = lb[i:j]; k = sum(x["wicket"] == "True" for x in win); runs = win[-1]["score_after"] - (lb[i - 1]["score_after"] if i else 0)
                if best is None or (k, -runs) > (best[0], -best[1]): best = (k, runs, lb[i]["over"], win[-1]["over"])
            col[inn] = {"most_wickets_in_10_overs": best[0], "runs_in_that_window": best[1], "from_over": best[2], "to_over": best[3]}
        out[stem]["collapse_windows"] = col
    # hidden winners / losers: win-probability rank against a plain scorecard rank (runs + 20 x wickets, a transparent heuristic)
    for stem in INDIA_BATS:
        pv = list(csv.DictReader(open(f"{AN}/{stem}_player_value.csv", encoding="utf-8")))
        for p in pv:
            p["wpa"] = float(p["total_wpa_for_team"]); p["card_points"] = int(p["bat_runs"]) + 20 * int(p["bowl_wkts"]); p["bowl_balls"] = int(p["bowl_balls"]); p["bowl_runs"] = int(p["bowl_runs"])
        byw = sorted(pv, key=lambda p: -p["wpa"]); byc = sorted(pv, key=lambda p: -p["card_points"])
        for i, p in enumerate(byw): p["wpa_rank"] = i + 1
        for i, p in enumerate(byc): p["card_rank"] = i + 1
        n = len(pv); mk = lambda p: {"player": p["player"], "team": p["team"], "wpa": p["wpa"], "wpa_rank": p["wpa_rank"], "card_rank": p["card_rank"], "line": f"{p['bat_runs']} ({p['bat_balls']}); {p['bowl_wkts']}/{p['bowl_runs']} in {p['bowl_balls'] // 6}.{p['bowl_balls'] % 6}"}
        out[stem]["hidden"] = {"definition": "hidden winner: top-4 win-probability added but outside the top-4 of a plain scorecard rank (runs + 20 x wickets); hidden loser: bottom-5 win-probability added although inside the scorecard top-6",
                               "winners": [mk(p) for p in byw[:4] if p["card_rank"] > 4], "losers": [mk(p) for p in byw[-5:] if p["card_rank"] <= 6]}
    json.dump(out, open(f"{AN}/story.json", "w"), indent=1, ensure_ascii=False, default=str)
    return out


if __name__ == "__main__":
    o = main()
    for stem in INDIA_BATS:
        R = o[stem]; print(f"\n##### {stem}: India WP extremes {R['india_wp_extremes']}; tipping point {R['tipping_point']}")
        print("  curve:", [(c["inning"], c["after_over"], c["score"], round(c["india_wp"], 2)) for c in R["curve"]])
        print("  chase checkpoints:", [(c["after_over"], c["score"], c["need"], c["required_rate"], c["run_rate_so_far"]) for c in R["chase_checkpoints"]])
    print("\nlast-wicket stand:", o["nz_ind_5odi"]["last_wicket_stand"]); print("India FoW:", o["nz_ind_5odi"]["india_fall_of_wickets"])
    print("drops:", json.dumps(o["drops"], indent=0)[:1500])
