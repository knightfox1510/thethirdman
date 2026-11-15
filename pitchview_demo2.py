"""v4: the situations added in the second pass, on real balls of the 4th ODI (NZ v IND): free hit, no-ball, dropped chances, missed run-out, reviews, leave, byes, bouncer, swing, round the wicket, edge, field view;
plus the two animations (a run out and a boundary).   python3 pitchview_demo2.py [anim]"""
import os, sys, json, pandas as pd
from pitchview import *
from pitchview_render import *
OUT = "deliver/_pitchview_mockups/v4/"; os.makedirs(OUT, exist_ok=True)
T4 = ("data/cricinfo/nz_ind_4odi_balls.csv", "data/cricinfo/nz_ind_4odi.json"); CB = "data/cricbuzz/nz_ind_4odi.json"; M = "NZ v IND · 4th ODI"; P = PALS["swiss"]
def ball(inn, ov, **kw): return from_table(*T4, inn, ov, cricbuzz=CB, **kw)
def go(name, dl, cam=None, pal=P, force=None):
    if force: dl.force_kind = force
    tr = trajectory(dl); c = cam(tr) if callable(cam) else (cam or follow_cam(tr, -50, 30)); poster(pal, dl, tr, c, OUT + name + ".png", match=M); print("  ", name)
near = lambda tr: Cam((0, PL - 3, 0.8), -38, 22, 15, F=1700, cy=390)
if "anim" not in sys.argv:
    d = pd.read_csv(T4[0])
    go("free_hit_six_seifert", ball(1, 1.3, nth=1))
    go("noball_seifert_overstep", ball(1, 1.3, nth=0), lambda tr: Cam((0, 6, 0.5), -40, 26, 15, F=1700, cy=390), force="no_ball")
    go("dropped_rohit_slip_young", ball(1, 1.5), follow_cam)
    go("dropped_kelly_backward_point", ball(2, 5.4))
    go("runout_missed_kohli_mid_off", ball(1, 47.2))
    go("review_lbw_iyer_three_reds", ball(2, 0.6), lambda tr: Cam((0, PL - 1.0, 0.9), 24, 9, 9.5, cy=390))
    go("review_not_out_young", ball(1, 33.3), near)
    lv = d[(d.shot == "LEFT_ALONE") & (d.runs == 0) & (d.wicket == False)].iloc[3]; go("leave_" + lv.batter.split()[-1].lower(), ball(int(lv.inning), float(lv.overs)), near)
    go("leg_bye_seifert", ball(1, 9.1), near); go("bye_clarke", ball(1, 40.1), near)
    go("bouncer_brar_young", ball(1, 11.3), near)
    go("swing_arshdeep_seifert", ball(1, 0.5), near)
    go("round_the_wicket_arshdeep_young", ball(1, 26.5), near)
    go("edge_young_arshdeep", ball(1, 0.1), near)
    cm = json.load(open(CB, encoding="utf-8"))["comments"]; ov = d[(d.inning == 2) & (d.over_no == 1)].head(6)
    field_poster(P, cm, 2, 0.0, ov, OUT + "field_view_henry_first_over.png", "THE FIELD", ["AS THE COMMENTARY", "DESCRIBES IT"], M)
    # smoke test of the rare dismissals (no real example exists in our captures): the code path must run, nothing is saved
    for k in ("hit_wicket", "handled", "obstruct", "timed_out", "retired", "caught_bowled"):
        dl = ball(2, 0.5); dl.force_kind = k; tr = trajectory(dl); from pitchview_situations import situation; assert situation(dl, tr)["kind"] == k
    print("rare dismissal code paths run")
else:
    animate(P, ball(1, 49.5), trajectory(ball(1, 49.5)), OUT + "anim_runout_direct_hit.mp4", M, seconds=6.0)
    print("   anim runout")
    animate(P, ball(1, 13.4), trajectory(ball(1, 13.4)), OUT + "anim_six_young_pull.mp4", M, seconds=6.0)
    print("   anim six")
