"""Figures for specs/bay_oval_new_ball.json: Bay Oval men's ODI history (Cricsheet, to Oct 2025) + the 4th ODI capture (13 Nov 2026).
Cricsheet source: https://cricsheet.org/downloads/odis_json.zip (unzipped to the dir given by CS_DIR; ODC-BY).
    CS_DIR=/path/to/odis_json python3 analysis/bay_oval_new_ball.py
Conventions: men's ODIs only; "new ball" = overs 1-10 (the first powerplay); runs = runs of the innings incl. extras; completed 50-over matches unless stated."""
import glob, json, os, sys, collections
CS = os.environ.get("CS_DIR", "/tmp/claude-0/cs_odi_dl/json")
NZ_CITIES = {"Auckland", "Hamilton", "Wellington", "Christchurch", "Napier", "Dunedin", "Queenstown", "Nelson", "Whangarei", "Mount Maunganui", "Hastings", "Lincoln", "New Plymouth", "Invercargill", "Rangiora", "Tauranga"}
CAUGHT = {"caught", "caught and bowled"}


def innings_rows(m):
    i = m["info"]; out = []
    for k, inn in enumerate(m["innings"]):
        if inn.get("super_over"): continue
        runs = wk = 0; p1r = p1w = 0; first_w = None; kinds = collections.Counter(); balls = 0; w1 = 0
        for o in inn["overs"]:
            for d in o["deliveries"]:
                r = d["runs"]["total"]; runs += r
                legal = not (d.get("extras", {}).get("wides") or d.get("extras", {}).get("noballs"))
                if legal: balls += 1
                if o["over"] < 10: p1r += r
                if "wickets" in d:
                    for w in d["wickets"]:
                        if w["kind"] == "retired hurt": continue
                        wk += 1
                        if o["over"] < 10: p1w += 1; kinds[w["kind"]] += 1
                        if o["over"] == 0: w1 += 1
        out.append(dict(inn=k + 1, team=inn["team"], runs=runs, wk=wk, p1r=p1r, p1w=p1w, p1kinds=kinds, w1=w1, balls=balls))
    return out


def load():
    ms = []
    for f in glob.glob(f"{CS}/*.json"):
        m = json.load(open(f)); i = m["info"]
        if i.get("gender") != "male" or i.get("match_type") != "ODI" or i.get("overs") != 50: continue
        ms.append(m)
    return ms


if __name__ == "__main__":
    ms = load(); print("men's 50-over ODIs", len(ms))
    bay = [m for m in ms if "Bay Oval" in m["info"].get("venue", "")]
    nz = [m for m in ms if m["info"].get("city") in NZ_CITIES and m not in bay]
    print("Bay Oval", len(bay), "other NZ", len(nz))
    for name, grp in (("Bay Oval", bay), ("Other NZ", nz), ("All ODIs", ms)):
        rows = [r for m in grp for r in innings_rows(m)]
        n = len(rows); f1 = [r for r in rows if r["inn"] == 1]; f2 = [r for r in rows if r["inn"] == 2]
        print(f"\n{name}: innings {n}")
        print("  avg 1st inn", round(sum(r['runs'] for r in f1) / len(f1), 1), " avg 2nd", round(sum(r['runs'] for r in f2) / len(f2), 1))
        print("  new ball (ov 1-10): runs/inn", round(sum(r['p1r'] for r in rows) / n, 1), " wkts/inn", round(sum(r['p1w'] for r in rows) / n, 2),
              " RR", round(sum(r['p1r'] for r in rows) / n / 10, 2), " wkt in over 1 %", round(100 * sum(1 for r in rows if r['w1'] > 0) / n, 1))
        kinds = sum((r["p1kinds"] for r in rows), collections.Counter()); tot = sum(kinds.values())
        print("  dismissals ov1-10:", {k: f"{round(100*v/tot)}%" for k, v in kinds.most_common(5)}, "n", tot)
        print("  innings losing 3+ wkts in ov1-10: %", round(100 * sum(1 for r in rows if r['p1w'] >= 3) / n, 1))
    print("\nBay Oval match list")
    for m in sorted(bay, key=lambda m: m["info"]["dates"][0]):
        i = m["info"]; r = innings_rows(m); o = i["outcome"]
        print(i["dates"][0], i["teams"], [(x["team"], x["runs"], x["wk"], f"p1 {x['p1r']}/{x['p1w']}") for x in r], o.get("winner"), o.get("by"), "toss", i["toss"]["winner"], i["toss"]["decision"])
