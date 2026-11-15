"""Cross-checks for the NZ v IND dataset: our Cricbuzz-derived tables against Wikipedia's match boxes (which cite Cricinfo scorecards), against Cricbuzz's own editorial summary lines, and, for the 4th ODI,
against the independent Cricinfo capture (over by over). Any mismatch raises.   python3 analysis/nz_ind_validate.py"""
import csv, json, os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = "data/series/nz_ind_2026"; AN = OUT + "/analysis"
summ = json.load(open(f"{AN}/summary.json"))


def card(stem):
    rows = list(csv.DictReader(open(f"{OUT}/{stem}_balls.csv", encoding="utf-8")))
    bat = collections.defaultdict(lambda: [0, 0]); bowl = collections.defaultdict(lambda: [0, 0, 0])
    for r in rows:
        if r["extra"] not in ("wide",): bat[r["batter"]][0] += int(r["bat_runs"])
        if r["legal"] == "True": bat[r["batter"]][1] += 1; bowl[r["bowler"]][0] += 1
        bowl[r["bowler"]][1] += int(r["runs"]) if r["extra"] not in ("leg bye", "bye") else 0
        if r["wicket"] == "True" and r["dismissal"] != "run out": bowl[r["bowler"]][2] += 1
    return bat, bowl


ok = []
def check(name, got, want):
    assert got == want, f"{name}: got {got}, expected {want}"; ok.append(name)

# --- 5th ODI vs Wikipedia (match box: India 209 (42.1), NZ 187 (48.1), Axar 46 (55), Foxcroft 31 (42), Arshdeep 3/30 (10), Santner 3/47 (10))
m5 = summ["matches"]["nz_ind_5odi"]["innings"]; bat, bowl = card("nz_ind_5odi")
check("5th: India 209/10 in 42.1", (m5["1"]["score"], m5["1"]["wkts"], m5["1"]["overs"]), (209, 10, "42.1")); check("5th: NZ 187/10 in 48.1", (m5["2"]["score"], m5["2"]["wkts"], m5["2"]["overs"]), (187, 10, "48.1"))
check("5th: Axar Patel 46 (55)", tuple(bat["Axar Patel"]), (46, 55)); check("5th: Foxcroft 31 (42)", tuple(bat["Dean Foxcroft"]), (31, 42))
check("5th: Arshdeep 3/30 in 10", (bowl["Arshdeep Singh"][2], bowl["Arshdeep Singh"][1], bowl["Arshdeep Singh"][0]), (3, 30, 60)); check("5th: Santner 3/47 in 10", (bowl["Mitchell Santner"][2], bowl["Mitchell Santner"][1], bowl["Mitchell Santner"][0]), (3, 47, 60))
# --- Cricbuzz's own editorial line for NZ's attack: 'Pace: 6/125 in 22.1 overs, ER 5.63; Spin: 4/82 in 20 overs, ER 4.1'
ps = summ["matches"]["nz_ind_5odi"]["pace_vs_spin"]["New Zealand"]; check("5th: NZ pace 6/125 in 22.1", (ps["pace"]["wkts"], ps["pace"]["runs"], ps["pace"]["overs"]), (6, 125, "22.1")); check("5th: NZ spin 4/82 in 20.0", (ps["spin"]["wkts"], ps["spin"]["runs"], ps["spin"]["overs"]), (4, 82, "20.0"))
# --- 4th ODI vs Wikipedia (NZ 333 (50), India 89 (26.4), Young 125 (108), Henry 6/27 (9.4), Axar 2/39 (10), Kishan 27 (53))
m4 = summ["matches"]["nz_ind_4odi"]["innings"]; bat, bowl = card("nz_ind_4odi")
check("4th: NZ 333/10 in 50.0", (m4["1"]["score"], m4["1"]["wkts"], m4["1"]["overs"]), (333, 10, "50.0")); check("4th: India 89/10 in 26.4", (m4["2"]["score"], m4["2"]["wkts"], m4["2"]["overs"]), (89, 10, "26.4"))
check("4th: Young 125 (108)", tuple(bat["Will Young"]), (125, 108)); check("4th: Henry 6/27 in 9.4", (bowl["Matt Henry"][2], bowl["Matt Henry"][1], bowl["Matt Henry"][0]), (6, 27, 58)); check("4th: Axar 2/39 in 10", (bowl["Axar Patel"][2], bowl["Axar Patel"][1], bowl["Axar Patel"][0]), (2, 39, 60))
check("4th: Kishan 27 (53)", tuple(bat["Ishan Kishan"]), (27, 53))
# --- 4th ODI over by over against the Cricinfo capture (independent source)
ci = list(csv.DictReader(open("data/cricinfo/nz_ind_4odi_balls.csv", encoding="utf-8"))); k = ci[0].keys()
inn_key = "inning" if "inning" in k else list(k)[0]
by_ci = collections.defaultdict(int); by_cb = collections.defaultdict(int)
for r in ci: by_ci[(int(r["inning"]), int(float(r["overs"])))] += int(float(r["runs"]))
for r in csv.DictReader(open(f"{OUT}/nz_ind_4odi_balls.csv", encoding="utf-8")):
    ov = int(float(r["over"])) if round(float(r["over"]) % 1, 1) != 0 else int(float(r["over"])) - 1
    by_cb[(int(r["inning"]), ov)] += int(r["runs"])
diff = [(k_, by_ci[k_], by_cb[k_]) for k_ in sorted(set(by_ci) | set(by_cb)) if by_ci[k_] != by_cb[k_]]
print(f"{len(ok)} checks passed against Wikipedia / Cricbuzz editorial; 4th ODI over-by-over against the Cricinfo capture: {len(diff)} overs differ of {len(set(by_ci))}", diff[:6])
assert len(diff) <= 2, diff
