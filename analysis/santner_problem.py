"""Figures for specs/santner_problem.json: NZ v India T20I series, Oct-Nov 2026 (fixtures 71014-71018)."""
from common import t20i, batting, bowling, econ, show, section

FX = [71014, 71015, 71016, 71017, 71018]
x = t20i(FX)
nz_bowl = x[x.bowl_team == "New Zealand"]
ind = x[x.bat_team == "India"]
san = ind[ind.bowler == "Mitchell Santner"]
pace = ind[ind.bowl_kind == "right-arm pace"]

section("Economy vs India by NZ bowler type")
for k, d in nz_bowl.groupby("bowl_kind"):
    show(k, econ(d))

section("Santner's series")
b = bowling(x[x.bowler == "Mitchell Santner"], "fixture")
show("balls / overs", f"{int(b.balls.sum())} / {b.balls.sum() / 6:.0f}")
show("wickets", int(b.wkts.sum()), "{}")
for fx, r in b.iterrows():
    show(f"  game {FX.index(fx) + 1} ({fx})", f"{int(r.wkts)}/{int(r.runs)} in {int(r.balls)} balls")
legal = x[(x.bowler == "Mitchell Santner") & x.legal_bowl]
show("legal balls in overs 7-15", f"{int((legal.phase == 'middle').sum())} of {len(legal)}")

section("India batting vs pace (min 15 balls)")
bp = batting(pace, "batter").query("balls >= 15").sort_values("sr", ascending=False)
for nm, r in bp.iterrows():
    show(nm, f"SR {r.sr:.1f}  ({int(r.runs)} off {int(r.balls)})")
tp = batting(pace.assign(all=1), "all").iloc[0]
show("India as a team vs pace: SR / balls per wicket", f"{tp.sr:.1f} / {tp.bpd:.1f}")
ts = batting(san.assign(all=1), "all").iloc[0]
show("India vs Santner: SR / balls per wicket", f"{ts.sr:.1f} / {ts.bpd:.1f}")

section("India batters vs Santner")
for nm, r in batting(san, "batter").sort_values("balls", ascending=False).iterrows():
    show(nm, f"{int(r.runs)} off {int(r.balls)}, out {int(r.outs)}, SR {r.sr:.1f}")

section("By batting hand vs Santner")
for h, r in batting(san, "bat_hand").iterrows():
    show(h, f"SR {r.sr:.1f}")
