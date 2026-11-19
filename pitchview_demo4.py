"""v6: (1) the poster with NO source text on screen (provenance goes to <poster>.notes.json), (2) the same balls on a realistic turf ground (green mown grass, tan pitch, creases, rope, stands).
    python3 pitchview_demo4.py"""
import os, pandas as pd
from pitchview import *
from pitchview_cb import from_commentary
from pitchview_render import *
OUT = "deliver/_pitchview_mockups/v6/"; os.makedirs(OUT, exist_ok=True)
T4 = ("data/cricinfo/nz_ind_4odi_balls.csv", "data/cricinfo/nz_ind_4odi.json"); CB = "data/cricbuzz/nz_ind_4odi.json"; M = "NZ v IND · 4th ODI"
def ball(inn, ov, **kw): return from_table(*T4, inn, ov, cricbuzz=CB, **kw)
low = lambda tr: Cam((0, PL - 1.0, 0.9), 24, 9, 9.5, cy=390)
near = lambda tr: Cam((0, PL - 3, 0.8), -38, 22, 15, F=1700, cy=390)
def go(name, dl, cam, pal="turf_swiss", match=M):
    tr = trajectory(dl); poster(PALS[pal], dl, tr, cam(tr) if callable(cam) else cam, OUT + name + ".png", match=match); print("  ", name, flush=True)
for pal, tag in (("turf_swiss", "turf"), ("swiss", "flat")):
    go(f"{tag}_catch_rohit_first_slip", ball(2, 0.1), follow_cam, pal)
    go(f"{tag}_bowled_kohli_kept_low", ball(2, 0.5), low, pal)
    go(f"{tag}_six_young", ball(1, 13.4), follow_cam, pal)
    go(f"{tag}_runout_direct_hit", ball(1, 49.5), follow_cam, pal)
go("turf_stumped_kelly", ball(1, 14.2), near)
go("turf_wide_jamieson", ball(1, 49.1), lambda tr: Cam((0, PL - 5, 0.8), 30, 22, 17, F=1700, cy=390))
dl = from_commentary("data/cricbuzz/nz_ind_1odi.json", 1, 17.3); go("turf_commentary_only_dropped_1odi", dl, follow_cam, match="NZ v IND · 1st ODI")
d = pd.read_csv(T4[0]); hen = d[(d.inning == 2) & (d.over_no == 1)].head(6); names = " · ".join(dict.fromkeys(n.split()[-1].upper() for n in hen.batter))
over_poster(PALS["swiss"], hen, OUT + "flat_over_henry.png", "OVER 1", ["MATT HENRY", names], M); print("   over")
