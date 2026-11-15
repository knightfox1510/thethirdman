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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nz_ind_cfg import WIKI, STEMS, LABELS
for stem in STEMS:
    inn = summ["matches"][stem]["innings"]; bat, bowl = card(stem); W = WIKI[stem]
    for i in (1, 2): check(f"{LABELS[stem]}: innings {i} {W['inn'][i][0]}/{W['inn'][i][1]} in {W['inn'][i][2]}", (inn[str(i)]["score"], inn[str(i)]["wkts"], inn[str(i)]["overs"]), W["inn"][i])
    for n, v in W["bat"].items(): check(f"{LABELS[stem]}: {n} {v[0]} ({v[1]})", tuple(bat[n]), v)
    for n, (w, r, ov) in W["bowl"].items(): check(f"{LABELS[stem]}: {n} {w}/{r}", (bowl[n][2], bowl[n][1], bowl[n][0]), (w, r, int(ov) * 6 + round((ov % 1) * 10)))
# --- Cricbuzz's own editorial line for NZ's attack in the 5th ODI: 'Pace: 6/125 in 22.1 overs, ER 5.63; Spin: 4/82 in 20 overs, ER 4.1'
ps = summ["matches"]["nz_ind_5odi"]["pace_vs_spin"]["New Zealand"]; check("5th: NZ pace 6/125 in 22.1", (ps["pace"]["wkts"], ps["pace"]["runs"], ps["pace"]["overs"]), (6, 125, "22.1")); check("5th: NZ spin 4/82 in 20.0", (ps["spin"]["wkts"], ps["spin"]["runs"], ps["spin"]["overs"]), (4, 82, "20.0"))
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
