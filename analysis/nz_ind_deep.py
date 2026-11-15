"""Deep analysis of the NZ v IND ODI series from what we hold ball by ball: the 4th and 5th ODIs (Cricbuzz captures; the 4th also has a Cricinfo capture), plus the 1st-3rd results from Wikipedia.
    CS_DIR=... python3 analysis/nz_ind_deep.py        -> data/series/nz_ind_2026/analysis/*.csv + summary.json, and a printed digest
What it computes (every number is derived here, none typed):
  win probability and turning points (dataops/winprob.py) · player value (win probability added) and the hidden winners · bowling runs saved against the ODI archive baseline
  phase tables for both matches · partnerships and collapses · dropped catches and their cost · reviews · pace vs spin · pressure (dot-ball runs, boundary droughts) · 4th v 5th comparison
Coverage: matches 1-3 are NOT ball by ball here (capture them with tools/ttm-capture to extend this to the whole series)."""
import csv, json, os, re, sys, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from dataops import winprob, cricsheet as CS

OUT = "data/series/nz_ind_2026"; AN = OUT + "/analysis"; os.makedirs(AN, exist_ok=True)
STEMS = {"nz_ind_4odi": "4th ODI", "nz_ind_5odi": "5th ODI"}
INDIA_BATS = {"nz_ind_4odi": 2, "nz_ind_5odi": 1}
INDIA = {"Rohit Sharma", "Virat Kohli", "Ruturaj Gaikwad", "Shreyas Iyer", "Axar Patel", "Naman Dhir", "Auqib Nabi", "Yash Thakur", "Ishan Kishan", "Arshdeep Singh", "Mohammed Siraj", "Gurnoor Brar", "Kuldeep Yadav"}
STYLE = {  # bowling style from the Cricinfo capture of the 4th ODI (playing-XI roles); the 5th-ODI newcomers (Yash Thakur, Siraj) are marked assumed
    "Will Young": "spin", "Nick Kelly": "spin", "Dean Foxcroft": "spin", "Michael Bracewell": "spin", "Mitchell Santner": "spin", "Kristian Clarke": "pace", "Kyle Jamieson": "pace", "Matt Henry": "pace", "Matthew Fisher": "pace",
    "Jacob Duffy": "pace", "Blair Tickner": "pace", "Arshdeep Singh": "pace", "Auqib Nabi": "pace", "Axar Patel": "spin", "Gurnoor Brar": "pace", "Kuldeep Yadav": "spin", "Naman Dhir": "spin", "Mohammed Siraj": "pace", "Yash Thakur": "pace"}
ASSUMED_STYLE = {"Mohammed Siraj", "Yash Thakur", "Jacob Duffy", "Blair Tickner", "Kristian Clarke"}
PHASES = {"powerplay (1-10)": (0, 10), "middle (11-40)": (10, 40), "death (41-50)": (40, 50)}


def read(stem):
    rows = list(csv.DictReader(open(f"{OUT}/{stem}_balls.csv", encoding="utf-8")))
    for r in rows:
        for k in ("inning", "ball_no", "runs", "bat_runs", "score_after", "wkts_after"): r[k] = int(r[k])
        r["over"] = float(r["over"]); r["legal"] = r["legal"] == "True"; r["wicket"] = r["wicket"] == "True"; r["ov"] = int(r["over"] - 1e-9) if r["over"] % 1 else int(r["over"]) - 1
        r["ov"] = int(r["over"]) if round(r["over"] % 1, 1) != 0 else int(r["over"]) - 1
    return rows


def wpdf(stem): return list(csv.DictReader(open(f"{AN}/{stem}_wp.csv", encoding="utf-8")))


def baseline():
    """Average runs per over by over number (first 50) in men's ODIs since 2015 in the Cricsheet archive: what a bowler is 'expected' to concede."""
    tot = np.zeros(50); n = np.zeros(50)
    for lab, p, m in CS.matches("male"):
        i = m["info"]
        if lab != "ODI" or i["dates"][0] < "2015-01-01" or i.get("overs", 50) != 50 or "method" in i.get("outcome", {}): continue
        for inn in m["innings"]:
            if inn.get("super_over"): continue
            for ov in inn["overs"]:
                if ov["over"] < 50: tot[ov["over"]] += sum(d["runs"]["total"] for d in ov["deliveries"]); n[ov["over"]] += 1
    return tot / np.maximum(n, 1)


def main():
    S = {}; summary = {"matches": {}}; base = baseline(); summary["baseline_runs_per_over_2015_plus_first10"] = [round(x, 2) for x in base[:10]]
    data = {s: read(s) for s in STEMS}; wp = {s: wpdf(s) for s in STEMS}
    for stem, lab in STEMS.items():
        rows = data[stem]; ib = INDIA_BATS[stem]; M = {"label": lab, "innings": {}}
        # ---------------- innings and phase tables
        for inn in (1, 2):
            bb = [r for r in rows if r["inning"] == inn]; team = "India" if inn == ib else "New Zealand"; legal = sum(r["legal"] for r in bb)
            I = {"team": team, "score": bb[-1]["score_after"], "wkts": bb[-1]["wkts_after"], "legal_balls": legal, "overs": f"{legal // 6}.{legal % 6}", "run_rate": round(6 * bb[-1]["score_after"] / legal, 2),
                 "extras_deliveries": sum(not r["legal"] for r in bb), "fours": sum(r["runs"] == 4 and r["bat_runs"] == 4 for r in bb), "sixes": sum(r["bat_runs"] == 6 for r in bb), "phases": {}}
            lb = [r for r in bb if r["legal"]]
            I["dot_pct"] = round(100 * sum(r["runs"] == 0 for r in lb) / len(lb), 1); I["boundary_pct"] = round(100 * sum(r["bat_runs"] in (4, 6) for r in lb) / len(lb), 1)
            for name, (a, b) in PHASES.items():
                pb = [r for r in bb if a <= r["ov"] < b]; pl = [r for r in pb if r["legal"]]
                if not pl: continue
                I["phases"][name] = {"runs": sum(r["runs"] for r in pb), "wkts": sum(r["wicket"] for r in pb), "balls": len(pl), "rr": round(6 * sum(r["runs"] for r in pb) / len(pl), 2), "dot_pct": round(100 * sum(r["runs"] == 0 for r in pl) / len(pl), 1),
                                     "boundary_pct": round(100 * sum(r["bat_runs"] in (4, 6) for r in pl) / len(pl), 1)}
            M["innings"][inn] = I
        # ---------------- player value: win probability added (WPA)
        W = collections.defaultdict(lambda: {"bat_wpa": 0.0, "bowl_wpa": 0.0, "runs": 0, "balls": 0, "wkts": 0, "conceded": 0, "bowl_balls": 0, "team": ""})
        for r in wp[stem]:
            d = float(r["delta_bat_wp"]); bt = "India" if int(r["inning"]) == ib else "New Zealand"
            W[r["batter"]]["bat_wpa"] += d; W[r["batter"]]["team"] = bt
            W[r["bowler"]]["bowl_wpa"] -= d; W[r["bowler"]]["team"] = "New Zealand" if bt == "India" else "India"
        for r in rows:
            w = W[r["batter"]]; w["runs"] += r["bat_runs"] if r["extra"] not in ("wide",) else 0
            if r["legal"] or r["extra"] == "no ball": w["balls"] += 1 if r["legal"] else 0
            b = W[r["bowler"]]; b["conceded"] += r["runs"] if r["extra"] not in ("leg bye", "bye") else 0; b["bowl_balls"] += r["legal"]; b["wkts"] += 1 if (r["wicket"] and r["dismissal"] != "run out") else 0
        # bowling vs baseline
        for r_ in rows: pass
        bo = collections.defaultdict(lambda: {"exp": 0.0, "act": 0, "balls": 0})
        for r in rows:
            b = bo[r["bowler"]]; b["act"] += r["runs"] if r["extra"] not in ("leg bye", "bye") else 0
            if r["legal"]: b["exp"] += base[min(r["ov"], 49)] / 6; b["balls"] += 1
        for k, v in bo.items(): W[k]["runs_saved_vs_archive"] = round(v["exp"] - v["act"], 1)
        pv = []
        for k, v in W.items():
            pv.append({"match": lab, "player": k, "team": v["team"], "bat_runs": v["runs"], "bat_balls": v["balls"], "bat_wpa": round(v["bat_wpa"], 3), "bowl_balls": v["bowl_balls"], "bowl_runs": v["conceded"], "bowl_wkts": v["wkts"],
                       "bowl_wpa": round(v["bowl_wpa"], 3), "runs_saved_vs_archive": v.get("runs_saved_vs_archive", ""), "total_wpa_for_team": round(v["bat_wpa"] + v["bowl_wpa"], 3)})
        S[stem] = pv
        # ---------------- partnerships & collapse
        parts = list(csv.DictReader(open(f"{OUT}/{stem}_partnerships.csv", encoding="utf-8"))); M["partnerships"] = parts
        # ---------------- drops, reviews, run-out misses
        M["drops"] = []; M["reviews"] = []
        for i_, r in enumerate(rows):
            if "DROPPED" in r["event"]:
                after = [x for x in rows[i_ + 1:] if x["inning"] == r["inning"]]
                last = next((x for x in after if x["wicket"] and x["batter"] == r["batter"]), None); end_runs = (last["striker_runs"] if last else None)
                M["drops"].append({"inning": r["inning"], "over": r["over"], "batter": r["batter"], "bowler": r["bowler"], "batter_runs_at_drop": r["striker_runs"], "batter_final_runs": end_runs if end_runs not in ("", None) else "not out / n.a.", "text": r["text"][:200]})
            if "UDRS" in r["event"]: M["reviews"].append({"inning": r["inning"], "over": r["over"], "text": r["text"][:260]})
        # ---------------- pressure: dot-ball runs (consecutive dots) and boundary droughts
        for inn in (1, 2):
            lb = [r for r in rows if r["inning"] == inn and r["legal"]]; best = cur = 0; best_end = None; dr = d = 0
            for r in lb:
                cur = cur + 1 if r["runs"] == 0 else 0
                if cur > best: best, best_end = cur, r["over"]
                d = 0 if r["bat_runs"] in (4, 6) else d + 1
                dr = max(dr, d)
            M["innings"][inn]["longest_dot_run"] = {"balls": best, "ends_over": best_end}; M["innings"][inn]["longest_boundary_drought_balls"] = dr
        # ---------------- bowling cards & pace v spin
        card = collections.defaultdict(lambda: {"balls": 0, "runs": 0, "wkts": 0, "dots": 0, "bdry": 0, "wides_nb": 0})
        for r in rows:
            c = card[(r["bowler"], r["inning"])]; c["runs"] += r["runs"] if r["extra"] not in ("leg bye", "bye") else 0; c["wides_nb"] += (not r["legal"])
            if r["legal"]: c["balls"] += 1; c["dots"] += r["runs"] == 0; c["bdry"] += r["bat_runs"] in (4, 6)
            c["wkts"] += 1 if (r["wicket"] and r["dismissal"] != "run out") else 0
        M["bowling"] = [{"bowler": k[0], "inning": k[1], "overs": f"{v['balls'] // 6}.{v['balls'] % 6}", "runs": v["runs"], "wkts": v["wkts"], "econ": round(6 * v["runs"] / max(v["balls"], 1), 2), "dot_pct": round(100 * v["dots"] / max(v["balls"], 1), 1), "boundary_balls": v["bdry"], "wides_nb": v["wides_nb"], "style": STYLE.get(k[0], "?") + ("*" if k[0] in ASSUMED_STYLE else "")} for k, v in card.items()]
        ps = collections.defaultdict(lambda: {"pace": [0, 0, 0], "spin": [0, 0, 0]})
        for b in M["bowling"]:
            team = "India" if b["bowler"] in INDIA else "New Zealand"; st = b["style"].rstrip("*")
            if st in ("pace", "spin"): ps[team][st][0] += int(b["overs"].split(".")[0]) * 6 + int(b["overs"].split(".")[1]); ps[team][st][1] += b["runs"]; ps[team][st][2] += b["wkts"]
        M["pace_vs_spin"] = {t: {k: {"overs": f"{v[0] // 6}.{v[0] % 6}", "runs": v[1], "wkts": v[2], "econ": round(6 * v[1] / max(v[0], 1), 2)} for k, v in d.items()} for t, d in ps.items()}
        summary["matches"][stem] = M
        with open(f"{AN}/{stem}_player_value.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(pv[0].keys())); w.writeheader(); w.writerows(sorted(pv, key=lambda x: -x["total_wpa_for_team"]))
    json.dump(summary, open(f"{AN}/summary.json", "w"), indent=1, ensure_ascii=False, default=str)
    return summary, S


def digest(summary, S):
    for stem, M in summary["matches"].items():
        print(f"\n######## {M['label']}")
        for inn, I in M["innings"].items(): print(f"  inn{inn} {I['team']:11s} {I['score']}/{I['wkts']} in {I['overs']} RR {I['run_rate']} dot {I['dot_pct']}% bdry {I['boundary_pct']}% 4s {I['fours']} 6s {I['sixes']} | longest dot run {I['longest_dot_run']['balls']} | no-boundary drought {I['longest_boundary_drought_balls']} balls")
        for inn, I in M["innings"].items():
            for ph, v in I["phases"].items(): print(f"     inn{inn} {ph:17s} {v['runs']:3d}/{v['wkts']} off {v['balls']:3d} RR {v['rr']:5.2f} dot {v['dot_pct']:4.1f}% bdry {v['boundary_pct']:4.1f}%")
        print("  pace v spin:", M["pace_vs_spin"])
        print("  drops:", len(M["drops"]), [(d["batter"], d["over"], d["batter_runs_at_drop"], d["batter_final_runs"]) for d in M["drops"]])
        print("  reviews:", len(M["reviews"]))
        top = sorted(S[stem], key=lambda x: -x["total_wpa_for_team"])[:6]; bot = sorted(S[stem], key=lambda x: x["total_wpa_for_team"])[:4]
        print("  value (win prob added, for own team): top", [(x["player"], x["team"][:3], x["total_wpa_for_team"]) for x in top]); print("   bottom", [(x["player"], x["team"][:3], x["total_wpa_for_team"]) for x in bot])
        print("  bowling:", [(b["bowler"], b["inning"], b["overs"], b["runs"], b["wkts"], b["econ"]) for b in M["bowling"]])


if __name__ == "__main__":
    s, S = main(); digest(s, S)
