import sys, os, json, subprocess, numpy as np, skia
sys.path.insert(0, os.path.dirname(__file__))
import gfx
from gfx import W, H, FPS

FADE = 0.35
SC = float(os.environ.get("SCALE", "1"))
OW, OH = int(W * SC), int(H * SC)


def draw(arr, surface, idx, lt, D, T, total, frame):
    c = surface.getCanvas()
    c.save(); c.scale(SC, SC)
    gfx.background(c, T)
    a = min(gfx.clamp(lt / FADE), gfx.clamp((D - lt) / FADE)) if idx > 0 else gfx.clamp((D - lt) / FADE)
    c.saveLayerAlpha(None, int(255 * a))
    gfx.SCENES[idx](c, lt, D)
    c.restore()
    gfx.chrome(c, T, total, 1.0 if idx < len(gfx.SCENES) - 1 else 0.0)
    gfx.grain(c, frame)
    g = min(gfx.clamp(T / 0.6), gfx.clamp((total - T) / 1.0))
    if g < 1:
        c.drawRect(skia.Rect.MakeWH(W, H), gfx.paint((0, 0, 0), 1 - g))
    c.restore()
    surface.flushAndSubmit()


def still(idx, lt, D, starts, total, out):
    arr = np.zeros((H, W, 4), np.uint8)
    s = skia.Surface(arr)
    draw(arr, s, idx, lt, D, starts[idx] + lt, total, 0)
    skia.Image.fromarray(arr, colorType=skia.kRGBA_8888_ColorType).save(out, skia.kJPEG, 90)


def scene_file(idx, durs, outdir):
    starts = np.concatenate([[0], np.cumsum(durs)])
    total = float(starts[-1]); D = durs[idx]
    n = int(round(D * FPS))
    out = f"{outdir}/scene{idx}.mp4"; tmp = f"{outdir}/scene{idx}.tmp.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba",
                          "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
                          "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), tmp], stdin=subprocess.PIPE)
    arr = np.zeros((OH, OW, 4), np.uint8)
    s = skia.Surface(arr)
    f0 = int(round(starts[idx] * FPS))
    for i in range(n):
        lt = i / FPS
        draw(arr, s, idx, lt, D, starts[idx] + lt, total, f0 + i)
        p.stdin.write(arr.tobytes())
    p.stdin.close()
    if p.wait() == 0:
        os.replace(tmp, out)
    else:
        raise SystemExit(f"scene {idx} failed")


if __name__ == "__main__":
    mode = sys.argv[1]
    durs = json.load(open(sys.argv[2]))
    if mode == "scene":
        scene_file(int(sys.argv[3]), durs, sys.argv[4])
