"""Figures for specs/powerplay_revolution.json: IPL powerplay (overs 1-6), 2013-2026."""
from common import ipl, run_rate, show, section

df = ipl()
pp = df[df.phase == "powerplay"]
matches = df.groupby("season").fixture.nunique()
inn = pp.groupby(["season", "fixture", "inning"]).agg(runs=("team_runs", "sum"), wk=("wicket", "sum"))

section("Powerplay run rate / 60+ share / 80+ count / sixes per match / wickets per match")
for yr, g in pp.groupby("season"):
    i = inn.loc[yr]
    show(str(yr), f"RR {run_rate(g):.2f} | 60+ {100 * (i.runs >= 60).mean():.1f}% | 80+ {int((i.runs >= 80).sum())} | "
                  f"6s/match {g.six.sum() / matches[yr]:.2f} | wkts/match {g.wicket.sum() / matches[yr]:.2f}")

section("Highest powerplay scores")
top = inn.sort_values("runs", ascending=False).head(5)
for (yr, fx, ing), r in top.iterrows():
    d = pp[(pp.fixture == fx) & (pp.inning == ing)]
    show(f"{d.date.iloc[0]} {d.bat_team.iloc[0]} v {d.bowl_team.iloc[0]}", f"{int(r.runs)}/{int(r.wk)}")
