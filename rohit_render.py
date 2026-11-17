"""Silent render of the 'Mumbai cha Raja' Rohit Sharma video from the approved G frames (rohit_final2.py): 1080x1920, 30 fps, NO audio stream (the voice-over and music come later, from ElevenLabs, only if MI announce).
Motion: every frame builds on in staggered bands over a blurred ghost of itself, slow zoom, a flash and quick crossfade at each cut; the ring, the 2013 bars and the 538, the face-off scores and the chant's waveform animate for real.
Output: deliver/rohit_mumbai_cha_raja/Channel_Ep03_Mumbai_cha_Raja_Short_9x16_IG.mp4 (+ cover from the opening frame, no episode number on screen).   python3 rohit_render.py [--preview]"""
import os, subprocess, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import rohit_final2 as R

FPS = 30; W, H = 1080, 1920; ROOT = os.path.dirname(os.path.abspath(__file__)); PREVIEW = "--preview" in sys.argv
OUTD = f"{ROOT}/deliver/rohit_mumbai_cha_raja"; NAME = "Channel_Ep03_Mumbai_cha_Raja_Short_9x16_IG"
ease = R.ease
# (name, seconds, kind, function): 'band' = static still built on band by band; 'live' = the function itself animates (p = progress, t = seconds)
SCENES = [("cold open", 7, "band", R.f1), ("chant", 7, "live_t", R.f2), ("ring", 9, "live_p", R.f3), ("deccan to mumbai", 9, "band", R.f4), ("2013 ribbon", 9, "live_p", R.f5), ("six titles", 9, "band", R.f6),
          ("the reign", 8, "band", R.f7), ("face-off", 9, "live_p", R.f8), ("card front", 7, "band", R.f9), ("card back", 8, "band", R.f10), ("records", 9, "band", R.f11), ("close", 8, "band", R.f12)]
if PREVIEW: SCENES = [(n, 2.0, k, f) for n, _, k, f in SCENES]


def bands(still, s, reveal=1.5, n=9):
    ghost = ImageEnhance.Brightness(still.filter(ImageFilter.GaussianBlur(22))).enhance(.35); out = ghost.copy(); bh = H // n + 1
    for i in range(n):
        q = ease((s / reveal) * 1.25 - i * 0.09)
        if q <= 0: continue
        band = still.crop((0, i * bh, W, min(H, (i + 1) * bh))); off = int((1 - q) * 70 * (1 if i % 2 else -1))
        if q < 1: band = Image.blend(ghost.crop((0, i * bh, W, min(H, (i + 1) * bh))), band, q)
        out.paste(band, (off, i * bh))
    return out


def zoom(img, z, cx=.5, cy=.5):
    if z <= 1.0005: return img
    w, h = int(W / z), int(H / z); l = int((W - w) * cx); t = int((H - h) * cy); return img.crop((l, t, l + w, t + h)).resize((W, H), Image.BILINEAR)


def main():
    os.makedirs(OUTD, exist_ok=True); out = f"{OUTD}/{NAME}{'_preview' if PREVIEW else ''}.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    prev = None; total = 0
    for si, (name, dur, kind, fn) in enumerate(SCENES):
        n = int(dur * FPS); still = fn().convert("RGB") if kind in ("band",) else None; print(f"scene {si + 1}/{len(SCENES)}: {name} ({dur}s)", flush=True)
        for k in range(n):
            s = k / FPS; p = s / dur
            if kind == "band": img = bands(still, s)
            elif kind == "live_t": img = fn(s).convert("RGB")
            else: img = fn(min(1.0, s / (dur * 0.62))).convert("RGB")                  # animated build over the first ~60% of the scene, then hold
            img = zoom(img, 1.0 + 0.05 * ease(p) , .5, .45)
            if s < 0.12: img = Image.blend(img, Image.new("RGB", (W, H), (255, 255, 255)), .5 * (1 - s / .12))
            if prev is not None and s < 0.3: img = Image.blend(prev, img, ease(s / .3))
            ff.stdin.write(np.asarray(img, np.uint8).tobytes()); total += 1; last = img
        prev = last
    ff.stdin.close(); ff.wait(); print("frames", total, "->", out)
    if not PREVIEW:
        R.f1().convert("RGB").save(f"{OUTD}/{NAME.replace('_IG', '')}_cover.jpg", quality=92); R.f1().convert("RGB").save(f"{OUTD}/{NAME}_cover.jpg", quality=92)


if __name__ == "__main__":
    main()
