"""The Lab Ep. 2: Bumrah's bowling twin. Every IPL bowling season 2013-2026 with 180+ legal balls (Sportmonks ball-by-ball).
Ten measures, z-scored within season; distance = Euclidean. Economy counts runs off the bat + wides + no-balls."""
import sys, numpy as np, pandas as pd
from common import ipl
MIN = 180
M = ["Economy", "PP economy", "Death economy", "Dot %", "Balls per wicket", "Boundary % conceded", "Balls per six", "Death share", "PP share", "Econ v left-handers"]
NB = ("Run Out", "Retired", "Obstructing")


def table():
    d = ipl(); rows = []
    for (season, bid), x in d.groupby(["season", "bowler_id"]):
        lb = int(x.legal_bowl.sum())
        if lb < MIN: continue
        w = x[x["wicket"] & ~x.dismissal.str.contains("|".join(NB), case=False, na=False)]
        econ = lambda y: 6 * y.runs.sum() / y.legal_bowl.sum() if y.legal_bowl.sum() >= 24 else np.nan
        rows.append(dict(season=season, bowler=x.bowler.iloc[0], team=x.bowl_team.iloc[-1], balls=lb, wkts=len(w), kind=x.bowl_kind.iloc[0],
                         **{"Economy": 6 * x.runs.sum() / lb, "PP economy": econ(x[x.phase == "powerplay"]), "Death economy": econ(x[x.phase == "death"]),
                            "Dot %": 100 * (x["dot"] & x["legal_bowl"]).sum() / lb, "Balls per wicket": lb / max(1, len(w)),
                            "Boundary % conceded": 100 * (x["four"] | x["six"]).sum() / lb, "Balls per six": lb / max(1, x["six"].sum()),
                            "Death share": 100 * x[x.phase == "death"].legal_bowl.sum() / lb, "PP share": 100 * x[x.phase == "powerplay"].legal_bowl.sum() / lb,
                            "Econ v left-handers": econ(x[x.bat_hand == "left-hand-bat"])}))
    t = pd.DataFrame(rows)
    for m in M:
        t[m] = t.groupby("season")[m].transform(lambda s: s.fillna(s.median()))
        g = t.groupby("season")[m]; t["z_" + m] = (t[m] - g.transform("mean")) / g.transform("std"); t["p_" + m] = g.rank(pct=True) * 100
    return t.reset_index(drop=True)


def near(t, who, season, ms=M, k=6):
    Z = t[["z_" + m for m in ms]].values; i = t[(t.bowler == who) & (t.season == season)].index[0]
    dd = np.sqrt(((Z - Z[i]) ** 2).sum(1)); x = t.assign(dist=dd); return x[x.bowler != who].sort_values("dist").head(k)


if __name__ == "__main__":
    t = table(); print("seasons", len(t))
    b = t[t.bowler == "Jasprit Bumrah"][["season", "balls", "wkts", "Economy", "Death economy", "Dot %"]].round(2); print(b.to_string(index=False))
    for s in (2020, 2024, 2025):
        print(f"\n== Bumrah {s}"); print(near(t, "Jasprit Bumrah", s)[["season", "bowler", "team", "Economy", "wkts", "dist"]].round(2).to_string(index=False))
