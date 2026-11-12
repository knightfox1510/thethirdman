"""The Lab Ep. 1: who is Abhishek Sharma's statistical twin? (IPL 2013-2026, Sportmonks ball-by-ball)
    python3 analysis/lab_twin.py ["Abhishek Sharma"] [season]
Method: every IPL batting season with 200+ balls faced. 11 measures per season. Each measure is turned into a z-score
against the same season's qualified batters (so eras compare fairly), and the distance between two seasons is the
Euclidean distance across the 11 z-scores. Percentiles are within the same season. Super overs excluded."""
import sys, json, math
import numpy as np, pandas as pd
from common import ipl

MIN_BALLS = 200
M = ["SR", "PP SR", "Middle SR", "Boundary %", "Six %", "Dot %", "Balls per dismissal", "Average", "SR v pace", "SR v spin", "First 10 balls SR"]


def table():
    d = ipl()
    d = d[d.season >= 2013]
    rows = []
    # dismissals by the player actually out (catches non-striker run-outs, which striker_out misses)
    # out_id is missing on bowled dismissals, so: rows naming the player out + striker dismissals with no out_id
    oid = d.out_id.where(d.out_id.notna(), d.batter_id.where(d.striker_out))
    w = d[oid.notna()]
    outs_by = w.groupby(["season", oid[oid.notna()].astype(int)]).size()
    for (season, bid), x in d.groupby(["season", "batter_id"]):
        f = x[x.legal]
        balls = len(f)
        if balls < MIN_BALLS: continue
        runs = x.bat_runs.sum(); outs = int(outs_by.get((season, bid), 0))
        def sr(m):
            ff = f[m]; return 100 * ff.bat_runs.sum() / len(ff) if len(ff) >= 30 else np.nan
        # first 10 balls of each innings
        first = f.sort_values(["fixture", "ball"]).groupby(["fixture", "inning"]).head(10)
        rows.append(dict(season=season, batter=x.batter.iloc[0], batter_id=bid, team=x.bat_team.iloc[-1], balls=balls, runs=runs, outs=outs,
                         **{"SR": 100 * runs / balls, "PP SR": sr(f.phase == "powerplay"), "Middle SR": sr(f.phase == "middle"),
                            "Boundary %": 100 * (f["four"].sum() + f["six"].sum()) / balls, "Six %": 100 * f["six"].sum() / balls,
                            "Dot %": 100 * f["dot"].sum() / balls, "Balls per dismissal": balls / max(1, outs), "Average": runs / max(1, outs),
                            "SR v pace": sr(f.bowl_kind.str.contains("pace")), "SR v spin": sr(f.bowl_kind.str.contains("spin")),
                            "First 10 balls SR": 100 * first.bat_runs.sum() / max(1, len(first))}))
    t = pd.DataFrame(rows)
    for m in M:      # fill rare gaps (e.g. <30 balls v spin) with that season's median
        t[m] = t.groupby("season")[m].transform(lambda s: s.fillna(s.median()))
        g = t.groupby("season")[m]
        t["z_" + m] = (t[m] - g.transform("mean")) / g.transform("std")
        t["p_" + m] = g.rank(pct=True) * 100
    return t


if __name__ == "__main__":
    who = sys.argv[1] if len(sys.argv) > 1 else "Abhishek Sharma"
    t = table()
    print(f"qualified seasons (>= {MIN_BALLS} balls): {len(t)}  ({t.season.min()}-{t.season.max()}), batters: {t.batter_id.nunique()}")
    me = t[t.batter == who].sort_values("season")
    print(me[["season", "team", "balls", "runs", "SR", "PP SR", "Boundary %", "Six %", "Dot %", "Average"]].round(1).to_string(index=False))
    season = int(sys.argv[2]) if len(sys.argv) > 2 else int(me.season.max())
    a = me[me.season == season].iloc[0]
    Z = t[["z_" + m for m in M]].values; za = a[["z_" + m for m in M]].values.astype(float)
    t["dist"] = np.sqrt(((Z - za) ** 2).sum(1))
    others = t[t.batter != who].sort_values("dist")
    print(f"\n== {who} {season}: percentiles within season")
    for m in M: print(f"  {m:<20} {a[m]:7.1f}   pct {a['p_' + m]:5.0f}   z {a['z_' + m]:+.2f}")
    print("\n== nearest other seasons")
    print(others[["season", "batter", "team", "balls", "runs", "SR", "dist"]].head(12).round(2).to_string(index=False))
    print(f"\nmedian distance to all other seasons: {others.dist.median():.2f}; seasons within 3.0: {(others.dist < 3).sum()}")
    own = t[(t.batter == who) & (t.season != season)][["season", "dist"]]
    print("own other seasons:", own.round(2).to_dict("records"))
    # how alone: rank of his season by nearest-neighbour distance among all seasons
    nn = []
    for i in range(len(t)):
        d_ = np.sqrt(((Z - Z[i]) ** 2).sum(1)); d_[i] = 99
        d_[(t.batter_id == t.batter_id.iloc[i]).values] = 99
        nn.append(d_.min())
    t["nn"] = nn
    r = (t.nn > t.loc[a.name, "nn"]).sum()
    print(f"his nearest-neighbour distance {t.loc[a.name, 'nn']:.2f}; seasons more isolated: {r} of {len(t)}")
    json.dump({"dist_all": others.dist.round(3).tolist(), "season": season}, open(f"/tmp/claude-0/-home-claude/f3a29212-d6a0-5c29-bfa8-22c13b5be039/scratchpad/twin_{season}.json", "w"))
    t.to_pickle("/tmp/claude-0/-home-claude/f3a29212-d6a0-5c29-bfa8-22c13b5be039/scratchpad/twin_table.pkl")
