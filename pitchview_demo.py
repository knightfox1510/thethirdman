"""Renders one poster per situation from REAL balls in the captured matches (4th ODI, NZ v IND), plus the over / wagon / eye views.
    python3 pitchview_demo.py   ->  deliver/_pitchview_mockups/v3/"""
import os, pandas as pd
from pitchview import *
from pitchview_render import *
OUT = "deliver/_pitchview_mockups/v3/"; os.makedirs(OUT, exist_ok=True)
T4 = ("data/cricinfo/nz_ind_4odi_balls.csv", "data/cricinfo/nz_ind_4odi.json"); CB = "data/cricbuzz/nz_ind_4odi.json"; M = "NZ v IND · 4th ODI"
P = PALS["swiss"]; PR = PALS["red_soil_swiss"]
def ball(inn, ov, **kw): return from_table(*T4, inn, ov, cricbuzz=CB, **kw)
def go(name, dl, cam=None, pal=P, force=None):
    if force: dl.force_kind = force
    tr = trajectory(dl); c = cam(tr) if callable(cam) else (cam or follow_cam(tr, -50, 30)); poster(pal, dl, tr, c, OUT + name + ".png", match=M); print("  ", name)
side = lambda tr: Cam((0, PL - 3, 0.8), -38, 22, 15, F=1700, cy=390)
go("stumped_kelly", ball(1, 14.2), side)
go("runout_direct_hit_jamieson_henry", ball(1, 49.5))
go("runout_throw_fisher", ball(1, 49.6))
go("six_young_pull", ball(1, 13.4))
d = pd.read_csv(T4[0]); fours = d[(d.four == True) & (d.noballs == 0) & (d.wides == 0)]; r = fours.iloc[2]
go("four_" + r.batter.split()[-1].lower(), ball(int(r.inning), float(r.overs)))
go("wide_jamieson", ball(1, 49.1), lambda tr: Cam((0, PL - 5, 0.8), 30, 22, 17, F=1700, cy=390))
go("noball_kuldeep", ball(1, 25.4), lambda tr: Cam((0, 6, 0.5), -40, 26, 15, F=1700, cy=390), force="no_ball")
go("misfield_iyer_extra_cover", ball(1, 24.6))
kohli = ball(2, 0.5); go("view_batter_eye_kohli", kohli, lambda tr: LookCam((0.55, PL + 0.7, 1.6), (0, 8, 0.9), F=1250, cy=380))
rohit = ball(2, 0.1); go("view_keeper_eye_rohit", rohit, lambda tr: LookCam((0.0, PL + 12.0, 1.0), (0, PL - 6, 0.6), F=2100, cy=380))
go("spin_kuldeep_allen_red_soil", ball(1, 25.4), lambda tr: Cam((0, PL / 2, 0.5), -35, 30, 26, F=1700, cy=390), pal=PR)
hen = d[(d.inning == 2) & (d.over_no == 1)].head(6); over_poster(P, hen, OUT + "over_henry_first.png", "OVER 1", ["MATT HENRY", " · ".join(dict.fromkeys(n.split()[-1].upper() for n in hen.batter))], M)
y = d[(d.inning == 1) & (d.batter == "Will Young")]; wagon_poster(P, y, OUT + "wagon_young_innings.png", "WILL YOUNG", ["WHERE THE RUNS WENT", f"{int(y.bat_runs.sum())} OFF {int((y.legal == True).sum())} BALLS"], M)
print("done")
