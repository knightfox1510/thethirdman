"""Stat Check: Bumrah or Rashid? Every IPL ball they've bowled (Sportmonks IPL ball-by-ball 2013-2026; both careers start 2013+).
    python3 analysis/bumrah_rashid.py
Economy = runs off the bat + wides + no-balls per 6 legal balls (byes/leg-byes excluded). Wickets = striker dismissals credited to the
bowler (run-outs, retired, obstructing excluded). Super overs excluded."""
import pandas as pd, numpy as np
from common import ipl
NB = ("Run Out", "Retired", "Obstructing")
P = {"Jasprit Bumrah": "Bumrah", "Rashid Khan": "Rashid"}


def bowl(x):
    lb = x.legal_bowl.sum(); w = x[x.wicket & ~x.dismissal.str.contains("|".join(NB), case=False, na=False)]
    w = w[w.striker_out | w.out_id.isna()]
    bnd = x[(x["four"] | x["six"]) & x.legal]
    return dict(balls=int(lb), overs=f"{int(lb) // 6}.{int(lb) % 6}", runs=int(x.runs.sum()), wkts=len(w), econ=6 * x.runs.sum() / max(1, lb),
                sr=lb / max(1, len(w)), avg=x.runs.sum() / max(1, len(w)), dot=100 * (x["dot"] & x["legal_bowl"]).sum() / max(1, lb),
                bpb=lb / max(1, len(bnd)), sixes=int(x["six"].sum()), bp6=lb / max(1, x["six"].sum()), matches=x.fixture.nunique())


if __name__ == "__main__":
    d = ipl(); d = d[d.bowler.isin(P)]
    for name, x in d.groupby("bowler"):
        print(f"\n## {P[name]}: seasons {x.season.min()}-{x.season.max()}")
        print(" career", {k: (round(v, 2) if isinstance(v, float) else v) for k, v in bowl(x).items()})
        for ph in ("powerplay", "middle", "death"):
            print(f"  {ph:<10}", {k: round(v, 2) if isinstance(v, float) else v for k, v in bowl(x[x.phase == ph]).items() if k in ("balls", "econ", "wkts", "sr", "dot", "bpb")})
        for h in ("right-hand-bat", "left-hand-bat"):
            print(f"  v {h:<15}", {k: round(v, 2) if isinstance(v, float) else v for k, v in bowl(x[x.bat_hand == h]).items() if k in ("balls", "econ", "wkts", "sr", "dot")})
        bys = x.groupby("season").apply(lambda s: pd.Series(bowl(s))).loc[:, ["matches", "wkts", "econ"]]
        print(bys.round(2).to_string())
        print("  seasons with economy under 7:", int((bys.econ < 7).sum()), "of", len(bys))
        b = x.groupby("batter").apply(lambda s: pd.Series(bowl(s))); b = b[b.balls >= 30].sort_values("econ")
        print("  most balls to:", b.sort_values("balls", ascending=False).head(5)[["balls", "runs", "wkts", "econ"]].round(2).to_string())
    a = ipl(); lg = 6 * a.runs.sum() / a.legal_bowl.sum(); print("\nleague economy 2013-2026 (bowler runs):", round(lg, 2))
    for ph in ("powerplay", "middle", "death"):
        y = a[a.phase == ph]; print(" league", ph, round(6 * y.runs.sum() / y.legal_bowl.sum(), 2))
