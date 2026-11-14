"""Figures for specs/replay_u19_final.json: ACC Men's U19 Asia Cup 2026 final, India U19 v Pakistan U19, Al Amerat (Oman), 14 Nov 2026.
Source: Cricinfo + Cricbuzz captures -> data/cricinfo/u19_final_balls.csv (python3 cricinfo_import.py data/cricinfo/u19_final.json data/cricbuzz/u19_final.json).
Conventions (match the scorecards): balls faced = deliveries that are not wides (no-balls count); bowler runs exclude byes and leg byes;
wickets credited to a bowler exclude run outs (Cricinfo dismissal code 4); inning 1 = Pakistan, inning 2 = India."""
import pandas as pd

D = pd.read_csv("data/cricinfo/u19_final_balls.csv")
D["faced"] = D.wides == 0
D["bowl_runs"] = D.runs - D.byes - D.legbyes - D.penalties
D["bowler_wkt"] = D.wicket & D.dismissal.isin([1, 2, 3])
D["cum"] = D.groupby("inning").runs.cumsum(); D["wk"] = D.groupby("inning").wicket.cumsum(); D["lb"] = D.groupby("inning").legal.cumsum()
P, I = D[D.inning == 1], D[D.inning == 2]


def batting(g):
    out = g.groupby("batter").agg(runs=("bat_runs", "sum"), balls=("faced", "sum"), fours=("four", "sum"), sixes=("six", "sum"))
    out["sr"] = 100 * out.runs / out.balls; return out.sort_values("runs", ascending=False)


def bowling(g):
    out = g.groupby("bowler").agg(balls=("legal", "sum"), runs=("bowl_runs", "sum"), wkts=("bowler_wkt", "sum"), wides=("wides", "sum"), dots=("runs", lambda s: int((s == 0).sum())))
    out["overs"] = out.balls // 6 + (out.balls % 6) / 10; out["econ"] = 6 * out.runs / out.balls; return out.sort_values("wkts", ascending=False)


def phases(g, edges=((1, 10), (11, 20), (21, 30), (31, 40), (41, 50))):
    return [(int(g[(g.over_no >= a) & (g.over_no <= b)].runs.sum()), int(g[(g.over_no >= a) & (g.over_no <= b)].wicket.sum())) for a, b in edges]


def after(g, over):
    h = g[g.over_no <= over]; return int(h.runs.sum()), int(h.wicket.sum()), int(h.legal.sum())


if __name__ == "__main__":
    pd.set_option("display.width", 200)
    print("PAK", int(P.runs.sum()), int(P.wicket.sum()), " IND", int(I.runs.sum()), int(I.wicket.sum()))
    print(batting(P).round(1).head(6)); print(batting(I).round(1).head(8))
    print(bowling(I).round(2)); print(bowling(P).round(2))   # India's bowlers are in P's table (they bowled to Pakistan)
    print("phases PAK", phases(P), "IND", phases(I))
    for ov in (10, 20, 30, 35, 40, 44, 45, 46, 47, 48, 49, 50): print(ov, "PAK", after(P, ov), "IND", after(I, ov))
    print("IND per over 41-50", [int(I[I.over_no == o].runs.sum()) for o in range(41, 51)], "PAK per over 41-50", [int(P[P.over_no == o].runs.sum()) for o in range(41, 51)])
    print("sixes", P.groupby("batter").six.sum().sort_values(ascending=False).head(3).to_dict(), I.groupby("batter").six.sum().sort_values(ascending=False).head(3).to_dict())
    print("ctrl false% PAK", round(100 * (P[P.legal].control == 2).mean()), "IND", round(100 * (I[I.legal].control == 2).mean()), "dot%", round(100 * (P[P.legal].runs == 0).mean()), round(100 * (I[I.legal].runs == 0).mean()))
    print("boundary runs PAK", int(P.four.sum() * 4 + P.six.sum() * 6), "IND", int(I.four.sum() * 4 + I.six.sum() * 6))
