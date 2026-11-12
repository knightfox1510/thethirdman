"""Figures for specs/rcb_back_to_back.json: RCB 2024-2026 vs the league."""
from common import ipl, batting, bowling, run_rate, show, section

RCB = "Royal Challengers Bengaluru"
df = ipl()

for yr in (2024, 2025, 2026):
    s = df[df.season == yr]
    section(f"{yr}")
    for ph in (None, "powerplay", "death"):
        x = s if ph is None else s[s.phase == ph]
        t = x.groupby("bowl_team").apply(run_rate).sort_values()
        show(f"RCB bowling {ph or 'overall'}: economy / rank / league",
             f"{t[RCB]:.2f} / {list(t.index).index(RCB) + 1} of {len(t)} / {run_rate(x):.2f}")
    bw = bowling(s[s.bowl_team == RCB], "bowler").sort_values("wkts", ascending=False).head(4)
    for nm, r in bw.iterrows():
        show(f"  {nm}", f"{int(r.wkts)} wkts, econ {r.econ:.2f}")
    k = batting(s[(s.bat_team == RCB) & (s.batter == "Virat Kohli")], "season").iloc[0]
    show("  Virat Kohli", f"{int(k.runs)} runs, SR {k.sr:.1f}")
