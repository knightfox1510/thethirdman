"""Builds the Bumrah vertical (look B) with narration, music and mix, in two versions: the YouTube Short and the Instagram Reel.
Narration, timing and the music mix come from the engine (tts / plan / mix); the pictures from bumrah_render.py, stretched to each paragraph's length.
    python3 bumrah_build.py            -> deliver/bumrah_unplayable/<name>.mp4, <name>_IG.mp4 (+ .srt, covers)"""
import os, sys, json, shutil, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
sys.argv = [sys.argv[0]]
import engine as E, bumrah_render as B
R = B.R; SPEC = json.load(open(f"{R}/specs/bumrah_unplayable.json")); SLUG = SPEC["slug"]; NAME = SPEC["files"]["short"]; OUT = f"{R}/deliver/{SLUG}"; os.makedirs(OUT, exist_ok=True)
DESIGN = {n: (D, f) for n, D, f in B.SCENES}; ORDER = ["cold open", "the wrong action", "numbers", "four frames", "callouts", "release", "stumps", "old ball", "short format", "the back", "managed", "verdict", "poll"]
FPS = 30


def voice(variant):
    spec = json.loads(json.dumps(SPEC)); sc = spec["short"]
    if variant == "ig": sc[-1] = {"vo": SPEC["short_ig_end"], "scene": sc[-1]["scene"]}
    E.lint_vo(spec); base = f"{R}/out/{SLUG}{'__igshort' if variant == 'ig' else ''}/short"; os.makedirs(base, exist_ok=True)
    E.tts([s["vo"] for s in sc], f"{base}/vo", "short"); meta, lead, durs, starts, total = E.plan(spec, "short", base)
    E.mix(spec, "short", base, total, lead, starts, len(sc)); return spec, base, meta, lead, durs, starts, total


def frames(fn, Dd, Dr, ff):
    n = int(round(Dr * FPS)); prev = None
    for k in range(n):
        t = k / FPS * (Dd / Dr); im = fn(t, Dd).convert("RGB"); yield im


def main():
    res = {v: voice(v) for v in ("yt", "ig")}
    durs = res["yt"][4]; assert all(abs(a - b) < 1e-6 for a, b in zip(durs[:-1], res["ig"][4][:-1])), "shared narration differs between versions"
    print("scene durations", [round(d, 1) for d in durs], "total yt", round(res["yt"][6], 1), "ig", round(res["ig"][6], 1), flush=True)
    vid = f"{R}/out/{SLUG}/short/video_main.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{B.W}x{B.H}", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", vid], stdin=subprocess.PIPE)
    prev = None
    for i, nm in enumerate(ORDER):
        Dd, fn = DESIGN[nm]; Dr = durs[i]; print(f"scene {i + 1}/13 {nm} {Dr:.1f}s", flush=True)
        for k, im in enumerate(frames(fn, Dd, Dr, ff)):
            if k < 9 and prev is not None: im = Image.blend(prev, im, B.ease((k + 1) / 9))
            ff.stdin.write(np.asarray(im, np.uint8).tobytes()); last = im
        prev = last
    ff.stdin.close(); ff.wait()
    for variant, endfn, suffix in (("yt", B.s_end_yt, ""), ("ig", B.s_end, "_IG")):
        spec, base, meta, lead, dd, starts, total = res[variant]; Dr = dd[-1]; ev = f"{base}/video_end.mp4"
        e = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{B.W}x{B.H}", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", ev], stdin=subprocess.PIPE)
        for k in range(int(round(Dr * FPS))):
            im = endfn(k / FPS, Dr).convert("RGB")
            if k < 9: im = Image.blend(prev, im, B.ease((k + 1) / 9))
            e.stdin.write(np.asarray(im, np.uint8).tobytes())
        e.stdin.close(); e.wait()
        lst = f"{base}/list.txt"; open(lst, "w").write(f"file '{vid}'\nfile '{ev}'\n"); full = f"{base}/video.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", full], check=True)
        out = f"{OUT}/{NAME}{suffix}.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", full, "-i", f"{base}/mix.m4a", "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "copy", "-shortest", "-movflags", "+faststart", out], check=True)
        E.srt(meta, lead, starts, f"{OUT}/{NAME}{suffix}.srt"); B.cover().save(f"{OUT}/{NAME}{'_IG' if suffix else ''}_cover.jpg", quality=92) if True else None
        print(variant, "->", out, round(total, 1), "s", flush=True)


if __name__ == "__main__": main()
