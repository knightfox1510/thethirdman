"""Figures for specs/ipl_batting_evolution.json: how IPL batting changed, 2013-2026."""
import pandas as pd
from common import ipl, batting, econ, run_rate, show, section

df = ipl()
m = df.groupby("season").fixture.nunique()
inn = df.groupby(["season", "fixture", "inning"]).team_runs.sum().reset_index()
lb = df[df.legal_bowl]

section("Totals")
for yr in m.index:
    i = inn[inn.season == yr]
    show(str(yr), f"200+ {int((i.team_runs >= 200).sum())} | avg 1st-inns {i[i.inning == 'S1'].team_runs.mean():.1f} | "
                  f"max {i.team_runs.max()} | matches {m[yr]}")

section("Run rate by phase / boundaries / dots")
for yr, g in df.groupby("season"):
    l = lb[lb.season == yr]
    show(str(yr), " | ".join(f"{ph[:2]} {run_rate(g[g.phase == ph]):.2f}" for ph in ("powerplay", "middle", "death")) +
         f" | 4s/m {g.four.sum() / m[yr]:.1f} | 6s/m {g.six.sum() / m[yr]:.1f} | bdry {100 * (l.four | l.six).mean():.1f}% | dots {100 * l['dot'].mean():.1f}%")

section("Strike rate by batting position (order of first ball faced) / depth / wickets")
d = df.sort_values(["fixture", "inning", "ball"]).copy()
first = d.drop_duplicates(["fixture", "inning", "batter_id"])[["fixture", "inning", "batter_id"]].copy()
first["pos"] = first.groupby(["fixture", "inning"]).cumcount() + 1
d = d.merge(first, on=["fixture", "inning", "batter_id"])
d["grp"] = pd.cut(d.pos, [0, 3, 7, 11], labels=["top3", "4-7", "8-11"])
ii = d.groupby(["season", "fixture", "inning"]).agg(wk=("wicket", "sum"), maxpos=("pos", "max"))
for yr, g in d.groupby("season"):
    sr = g.groupby("grp", observed=True).apply(lambda x: 100 * x.bat_runs.sum() / x.legal.sum())
    j = ii.loc[yr]
    show(str(yr), f"top3 {sr['top3']:.1f} | 4-7 {sr['4-7']:.1f} | no.8 faced {100 * (j.maxpos >= 8).mean():.1f}% | wkts/inns {j.wk.mean():.2f}")

section("The 150 club (200+ balls, SR 150+)")
b = batting(df, ["season", "batter"]); q = b[b.balls >= 200]
for yr in m.index:
    x = q.loc[yr]; show(str(yr), f"{int((x.sr >= 150).sum())} of {len(x)}")
top = q.loc[2026].sort_values("sr", ascending=False).head(5)
for nm, r in top.iterrows(): show(f"  2026 {nm}", f"SR {r.sr:.1f}, {int(r.runs)} runs")

section("Chasing 200+ (second innings beats a first-innings total of 200+)")
p = inn.pivot_table(index=["season", "fixture"], columns="inning", values="team_runs").dropna().reset_index()
t = p[p.S1 >= 200].assign(won=lambda x: x.S2 > x.S1)
for a, z in [(2013, 2022), (2023, 2025), (2026, 2026)]:
    x = t[t.season.between(a, z)]; show(f"{a}-{z}", f"{int(x.won.sum())} of {len(x)} ({100 * x.won.mean():.1f}%)")

section("Impact Player: 2020-22 vs 2023-26")
for a, z in [(2020, 2022), (2023, 2026)]:
    x = df[df.season.between(a, z)]; mm = x.fixture.nunique(); i = inn[inn.season.between(a, z)]
    show(f"{a}-{z}", f"RR {run_rate(x):.2f} | 200+/match {(i.team_runs >= 200).sum() / mm:.2f} | 6s/match {x.six.sum() / mm:.1f}")

section("Bowlers")
ov = df.groupby(["season", "fixture", "inning", "over"]).team_runs.sum()
spin = df.bowl_kind.isin(["off-spin", "leg-spin", "left-arm spin"]); pace = df.bowl_kind.isin(["right-arm pace", "left-arm pace"])
for yr in (2013, 2026):
    o = ov.loc[yr]
    show(str(yr), f"overs 15+ {100 * (o >= 15).mean():.1f}% | overs <=6 {100 * (o <= 6).mean():.1f}% | "
                  f"spin econ {econ(df[spin & (df.season == yr)]):.2f} | pace econ {econ(df[pace & (df.season == yr)]):.2f}")
