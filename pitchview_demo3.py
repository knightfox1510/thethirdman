"""v5: (1) commentary-only matches drawn (no Cricinfo table), (2) an animation for every remaining situation on real balls of the 4th ODI, (3) animated builds of the over page and the wagon plot.
    python3 pitchview_demo3.py posters | anim | reveal"""
import os, sys, glob, subprocess, json, pandas as pd
from multiprocessing import Pool
from pitchview import *
from pitchview_cb import from_commentary
from pitchview_render import *
OUT = "deliver/_pitchview_mockups/v5/"; os.makedirs(OUT, exist_ok=True)
T4 = ("data/cricinfo/nz_ind_4odi_balls.csv", "data/cricinfo/nz_ind_4odi.json"); CB4 = "data/cricbuzz/nz_ind_4odi.json"; M4 = "NZ v IND · 4th ODI"; P = PALS["swiss"]
LABEL = {"nz_ind_1odi": "NZ v IND · 1st ODI", "nz_ind_2odi": "NZ v IND · 2nd ODI", "nz_ind_5odi": "NZ v IND · 5th ODI", "u19_uae": "U19 Asia Cup · v UAE", "u19_final": "U19 Asia Cup Final"}
def cbd(f, inn, ov, force=None, **kw):
    dl = from_commentary(f"data/cricbuzz/{f}.json", inn, ov, **kw)
    if force: dl.force_kind = force
    return dl
def post(name, dl, f, cam=None):
    tr = trajectory(dl); poster(P, dl, tr, cam(tr) if callable(cam) else (cam or follow_cam(tr, -50, 30)), OUT + name + ".png", match=LABEL[f]); print("  ", name, flush=True)
def posters():
    post("cb_runout_phillips_mitchell_1odi", cbd("nz_ind_1odi", 1, 21.1), "nz_ind_1odi")
    post("cb_dropped_mitchell_cover_1odi", cbd("nz_ind_1odi", 1, 17.3), "nz_ind_1odi")
    post("cb_catch_kohli_run_1odi", cbd("nz_ind_1odi", 1, 28.3), "nz_ind_1odi")
    post("cb_review_seifert_1odi", cbd("nz_ind_1odi", 1, 5.6), "nz_ind_1odi")
    post("cb_free_hit_tickner_5odi", cbd("nz_ind_5odi", 2, 47.5), "nz_ind_5odi")
    post("cb_bouncer_helmet_axar_2odi", cbd("nz_ind_2odi", 2, 8.5), "nz_ind_2odi", lambda tr: Cam((0, PL - 3, 0.8), -38, 22, 15, F=1700, cy=390))
    post("cb_overthrow_khudadad_u19uae", cbd("u19_uae", 2, 37.2), "u19_uae", lambda tr: Cam((0, PL - 3, 0.8), -38, 22, 15, F=1700, cy=390))
    post("cb_dropped_six_qadir_u19final", cbd("u19_final", 1, 23.3, force="dropped"), "u19_final")
SPECS = [("bowled_kohli", (2, 0.5), None, "near"), ("lbw_iyer", (2, 0.6), None, "near"), ("stumped_kelly", (1, 14.2), None, "near"), ("four_seifert", (1, 2.2), None, "follow"), ("wide_jamieson", (1, 49.1), None, "near"),
         ("noball_seifert", (1, 1.3, 0), "no_ball", "near"), ("free_hit_six_seifert", (1, 1.3, 1), None, "follow"), ("dropped_kelly", (2, 5.4), None, "follow"), ("runout_missed_kohli", (1, 47.2), None, "follow"),
         ("runout_throw_fisher", (1, 49.6), None, "follow"), ("misfield_iyer", (1, 24.6), None, "follow"), ("leave_allen", None, None, "near"), ("leg_bye_seifert", (1, 9.1), None, "near"), ("review_young", (1, 33.3), None, "near"),
         ("spin_kuldeep", (1, 25.4), "no_ball", "near"), ("bouncer_brar", (1, 11.3), None, "near"), ("swing_arshdeep", (1, 0.5), None, "near"), ("catch_allen_short_cover", (1, 30.2), None, "follow")]
def one(spec):
    name, key, force, cam = spec
    if key is None:
        d = pd.read_csv(T4[0]); lv = d[(d.shot == "LEFT_ALONE") & (d.runs == 0) & (d.wicket == False)].iloc[3]; key = (int(lv.inning), float(lv.overs))
    dl = from_table(*T4, key[0], key[1], cricbuzz=CB4, nth=(key[2] if len(key) > 2 else 0))
    if force: dl.force_kind = force
    tr = trajectory(dl); out = OUT + "anim_" + name + ".mp4"
    if cam == "near": orbit = (-60, -25)
    else: orbit = (-64, -26)
    animate(P, dl, tr, out, M4, seconds=5.0, fps=20, orbit=orbit); print("   anim", name, flush=True)
def reveal():
    d = pd.read_csv(T4[0]); hen = d[(d.inning == 2) & (d.over_no == 1)].head(6); y = d[(d.inning == 1) & (d.batter == "Will Young")]; fr = OUT + "_rv/"; os.makedirs(fr, exist_ok=True)
    names = ["  ".join(dict.fromkeys(n.split()[-1].upper() for n in hen.batter))][0]
    def mk(out, frames):
        for i, f in enumerate(frames): f(fr + f"f{i:03d}.png"); Image.open(fr + f"f{i:03d}.png").resize((720, 1280), Image.LANCZOS).save(fr + f"f{i:03d}.png")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "20", "-i", fr + "f%03d.png", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", out], check=True)
        for g in glob.glob(fr + "*.png"): os.remove(g)
    frames = []
    for k in range(1, 7): frames += [(lambda o, k=k: over_poster(P, hen.head(k), o, "OVER 1", ["MATT HENRY", names.replace("  ", " · ")], M4, S=1.0))] * 14
    mk(OUT + "anim_over_reveal_henry.mp4", frames)
    n = len(y); steps = list(range(6, n + 1, max(1, n // 40))) + [n]
    mk(OUT + "anim_wagon_young_innings.mp4", [(lambda o, k=k: wagon_poster(P, y.head(k), o, "WILL YOUNG", ["WHERE THE RUNS WENT", f"BALL {k} OF {n}"], M4, S=1.0)) for k in steps for _ in range(2)])
    os.rmdir(fr); print("   reveals", flush=True)
if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "posters"
    if mode == "posters": posters()
    elif mode == "anim":
        with Pool(4) as pool: pool.map(one, SPECS, chunksize=1)
    elif mode == "reveal": reveal()
