"""Figures for specs/abhishek_plan.json: Abhishek Sharma by bowler type, IPL 2013-2026 + India T20Is."""
import json, os
from common import ipl, t20i, batting, show, section

NAME = "Abhishek Sharma"
ids = json.load(open(os.path.join(os.path.dirname(__file__), "..", "data", "abhishek_t20i_ids.json")))
I = ipl(); I = I[I.batter == NAME]
T = t20i(ids); T = T[T.batter == NAME]


def innings_ball_no(d):
    """1-based count of legal balls faced by the batter within each innings."""
    d = d.sort_values(["fixture", "inning", "ball"]).copy()
    d["n"] = d.groupby(["fixture", "inning"]).legal.cumsum()
    return d


section("IPL strike rate by season")
for yr, r in batting(I, "season").iterrows():
    show(str(yr), f"SR {r.sr:.1f}  runs {int(r.runs)}")

section("IPL boom or bust")
inn = I.groupby(["fixture", "inning"]).agg(runs=("bat_runs", "sum"), balls=("legal", "sum"), out=("striker_out", "max"))
show("innings", len(inn), "{}")
show("scores of 50+", int((inn.runs >= 50).sum()), "{}")
show("out within first 6 balls", int((inn.out & (inn.balls <= 6)).sum()), "{}")
show("share of innings", 100 * (inn.out & (inn.balls <= 6)).mean(), "{:.1f}%")

section("IPL first six balls by bowler type")
f6 = innings_ball_no(I)
f6 = f6[f6.n <= 6]
for k, r in batting(f6, "bowl_kind").iterrows():
    show(k, f"SR {r.sr:.1f}, balls per dismissal {r.bpd:.1f}  ({int(r.runs)} off {int(r.balls)}, {int(r.outs)} out)")

section("IPL + T20I by bowler type (balls per dismissal = lower is more dangerous)")
both = I._append(T) if hasattr(I, "_append") else __import__("pandas").concat([I, T])
for k, r in batting(both[both.bowl_kind != "unknown"], "bowl_kind").iterrows():
    show(k, f"bpd {r.bpd:.1f}, SR {r.sr:.1f}")
