"""Figures for specs/death_kings.json: IPL death overs (16-20)."""
from common import ipl, bowling, econ, show, section

df = ipl()
d = df[df.phase == "death"]
recent = d[d.season >= 2022]

section("League death economy by season")
for yr, g in d.groupby("season"):
    show(str(yr), econ(g))
show("league 2022-2026", econ(recent))

section("Best death economy 2022-2026 (min 300 legal balls)")
b = bowling(recent, "bowler").query("balls >= 300").sort_values("econ")
for nm, r in b.head(8).iterrows():
    show(nm, f"{r.econ:.2f}  ({int(r.balls)} balls, {int(r.wkts)} wkts)")

section("How Bumrah does it, 2022-2026 (legal balls)")
for nm, g in [("Bumrah", recent[recent.bowler == "Jasprit Bumrah"]), ("League", recent)]:
    lb = g.legal_bowl.sum()
    show(nm, f"balls per six {lb / max(1, g.six.sum()):.1f} | boundary balls {100 * (g.four | g.six)[g.legal_bowl].sum() / lb:.1f}% | "
             f"dots {100 * g['dot'].sum() / lb:.1f}%")

section("Bumrah death economy by season")
for yr, r in bowling(d[d.bowler == "Jasprit Bumrah"], "season").iterrows():
    show(str(yr), f"{r.econ:.2f}  ({int(r.balls)} balls)")

section("Most death-over wickets 2013-2026")
for nm, r in bowling(d, "bowler").sort_values("wkts", ascending=False).head(5).iterrows():
    show(nm, int(r.wkts), "{}")
