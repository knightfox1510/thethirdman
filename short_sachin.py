"""Vertical 9:16 Short: 'What if Sachin played in the T20 era?' with burned-in captions."""
import os, sys, json, subprocess, numpy as np, skia
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gfx
from gfx import (text, rrect, paint, prog, eo, eio, eback, lerp, clamp, count_str, twidth,
                 INK, MUTED, GOLD, BLUE, RED, PANEL, LINE, BG)

VW, VH, FPS = 1080, 1920, 30
gfx.W, gfx.H = VW, VH            # background / grain read these at draw time
CX = VW / 2


def tag(c, a=1.0):
    gfx.logo_lockup(c, 70, 150, 64, a)
    rrect(c, 70, 220, 128, 44, 6, GOLD, a)
    text(c, "WHAT IF?", 134, 254, 34, "bebas", BG, a, "c", track=1.5)
    text(c, "SACHIN IN THE T20 ERA", 216, 253, 22, "interSB", INK, a * .85, track=3)


def v_hook(c, t, D):
    k = lambda f: f * D
    p = eo(prog(t, 0, .9))
    sw = eio(prog(t, k(.45), k(.45) + .5))
    y = lerp(820, 470, sw); s = lerp(330, 170, sw); a = lerp(1, .35, sw)
    text(c, count_str(100 * eo(prog(t, 0, 1.4))), CX, y, s, "bebas", GOLD if sw < .5 else INK, a * p, "c", glow=18 * (1 - sw))
    text(c, "INTERNATIONAL HUNDREDS", CX, y + lerp(80, 56, sw), lerp(40, 28, sw), "interB", MUTED, a * p, "c", track=6)
    p1 = eback(prog(t, k(.5), k(.5) + .6)); a1 = prog(t, k(.5), k(.5) + .25)
    if a1 > 0:
        c.save(); c.translate(CX, 1020); sc = lerp(1.5, 1, p1); c.scale(sc, sc)
        text(c, "1", 0, 0, 380, "bebas", GOLD, a1, "c", glow=26)
        c.restore()
        text(c, "T20 INTERNATIONAL", CX, 1110, 52, "interB", INK, eo(prog(t, k(.6), k(.6) + .5)), "c", track=8)


def v_bars(c, t, D):
    k = lambda f: f * D
    text(c, "STRIKE RATE", 90, 400, 110, "bebas", INK, eo(prog(t, 0, .6)), track=2)
    text(c, "RUNS PER 100 BALLS", 94, 450, 26, "interB", MUTED, eo(prog(t, 0, .6)), track=5)
    bw = 900 / 170
    for i, (tt, lab, v, cc) in enumerate([(k(.40), "SACHIN · IPL CAREER", 119.8, INK),
                                          (k(.80), "TOP ORDER · IPL TODAY", 158.5, GOLD)]):
        p = eo(prog(t, tt, tt + .9)); a = prog(t, tt, tt + .25)
        y = 600 + i * 260
        text(c, lab, 90, y, 30, "interB", MUTED, a, track=4)
        c.drawRect(skia.Rect.MakeXYWH(90, y + 26, 900, 100), paint(LINE, .35 * a))
        rrect(c, 90, y + 26, v * bw * p, 100, 10, cc, a)
        text(c, f"{v * p:.1f}", 90 + v * bw * p - 20, y + 100, 92, "bebas", BG, a * clamp(p * 3 - 2), "r")
    pg = eo(prog(t, k(.9), k(.9) + .4))
    if pg > 0:
        text(c, "+39 GAP", CX, 1180, 90, "bebas", RED, pg, "c", track=3)


def v_scale(c, t, D):
    k = lambda f: f * D
    text(c, "ADJUST FOR TODAY", CX, 420, 100, "bebas", INK, eo(prog(t, 0, .6)), "c", track=2)
    p = eo(prog(t, k(.35), k(.35) + .5))
    v = lerp(119.8, 146, eio(prog(t, k(.45), k(.95))))
    text(c, count_str(v, False) if v > 145.5 else f"{v:.1f}", CX, 920, 340, "bebas", GOLD, p, "c", glow=24)
    text(c, "ERA-ADJUSTED STRIKE RATE", CX, 1010, 34, "interB", GOLD, p, "c", track=6)
    text(c, "Rough estimate: IPL strike rate × today's top-order inflation", CX, 1070, 24, "inter", MUTED, p * .9, "c")


def v_cut(c, t, D):
    k = lambda f: f * D
    a = eo(prog(t, 0, .6))
    text(c, "THE UPPER CUT", CX, 400, 120, "bebas", INK, a, "c", track=2)
    text(c, "vs SHOAIB AKHTAR  ·  2003", CX, 455, 30, "interB", GOLD, a, "c", track=5)
    c.save(); c.translate(CX - 50, 820); c.scale(.85, .85)
    gfx.field(c, 0, 0, a, t, lambda f: f * D * .62, D)
    c.restore()


def v_verdict(c, t, D):
    for i, (ln, col_) in enumerate([("NOT A SLOGGER.", INK), ("THE ANCHOR", INK), ("WHO EXPLODES.", GOLD)]):
        tt = [0.0, .42, .62][i] * D
        p = eo(prog(t, tt, tt + .45))
        text(c, ln, CX, 620 + i * 190 + (1 - p) * 40, 170, "bebas", col_, p, "c", track=2, glow=12 if i == 2 else 0)


def v_cta(c, t, D):
    gfx.logo_lockup(c, CX, 420, 120, eo(prog(t, 0, .5)), "c")
    for i, (ln, col_) in enumerate([("WOULD SACHIN", INK), ("HAVE DOMINATED", INK), ("THE T20 ERA?", GOLD)]):
        p = eo(prog(t, i * .15, i * .15 + .5))
        text(c, ln, CX, 640 + i * 165 + (1 - p) * 40, 150, "bebas", col_, p, "c", track=2)
    p = eback(prog(t, D * .5, D * .5 + .5))
    if p > 0:
        c.save(); c.translate(CX, 1150); s = clamp(p, 0, 1.2); c.scale(s, s)
        rrect(c, -330, -50, 660, 100, 50, GOLD, clamp(p))
        text(c, "FULL BREAKDOWN ON THE CHANNEL", 0, 14, 38, "bebas", BG, clamp(p), "c", track=3)
        c.restore()


SCENES = [v_hook, v_bars, v_scale, v_cut, v_verdict, v_cta]


def groups(words, maxc=16):
    out, cur = [], []
    for w in words:
        if cur and (sum(len(x["w"]) + 1 for x in cur) + len(w["w"]) > maxc or cur[-1]["w"][-1] in ".?,"):
            out.append(cur); cur = []
        cur.append(w)
    if cur: out.append(cur)
    return out


def captions(c, t, grps):
    """t = time within the paragraph audio."""
    gi = None
    for i, g in enumerate(grps):
        end = grps[i + 1][0]["s"] if i + 1 < len(grps) else g[-1]["e"] + .4
        if g[0]["s"] - .05 <= t < end:
            gi = i; break
    if gi is None: return
    g = grps[gi]
    pop = eback(prog(t, g[0]["s"] - .05, g[0]["s"] + .12))
    size = 76
    ws = [x["w"].upper() for x in g]
    widths = [twidth(w, size, "interB") for w in ws]
    total = sum(widths) + 22 * (len(ws) - 1)
    x = CX - total / 2; y = 1400
    c.save(); c.translate(CX, y); s = .85 + .15 * clamp(pop, 0, 1.1); c.scale(s, s); c.translate(-CX, -y)
    for w, wd, wo in zip(ws, widths, g):
        active = wo["s"] <= t
        f = skia.Font(gfx.TF["interB"], size)
        sp = paint(BG, .95, stroke=14); sp.setStrokeJoin(skia.Paint.kRound_Join)
        c.drawString(w, x, y, f, sp)
        c.drawString(w, x, y, f, paint(GOLD if active and wo is g[-1] or (active and t < wo["e"]) else INK))
        x += wd + 22
    c.restore()


def build(base):
    meta = json.load(open(f"{base}/vo/meta.json"))
    leads = [0.15] + [0.22] * (len(meta) - 1)
    tails = [0.3] * (len(meta) - 1) + [1.6]
    durs = [round((l + m["dur"] + tl) * FPS) / FPS for l, m, tl in zip(leads, meta, tails)]
    starts = np.concatenate([[0], np.cumsum(durs)]); total = float(starts[-1])
    grps = [groups(m["words"]) for m in meta]
    return meta, leads, durs, starts, total, grps


def draw(c, i, lt, D, T, total, frame, lead, grps):
    gfx.background(c, T)
    a = min(clamp(lt / .2) if i > 0 else 1, clamp((D - lt) / .2) if i < len(SCENES) - 1 else 1)
    c.saveLayerAlpha(None, int(255 * a))
    SCENES[i](c, lt, D)
    c.restore()
    tag(c)
    captions(c, lt - lead, grps)
    c.drawRect(skia.Rect.MakeXYWH(0, 0, VW * clamp(T / total), 8), paint(GOLD, .9))
    gfx.grain(c, frame)
    g = clamp((total - T) / .6)
    if g < 1: c.drawRect(skia.Rect.MakeWH(VW, VH), paint((0, 0, 0), 1 - g))


def render_scene(base, i):
    meta, leads, durs, starts, total, grps = build(base)
    D = durs[i]; n = int(round(D * FPS))
    tmp, out = f"{base}/s{i}.tmp.mp4", f"{base}/s{i}.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{VW}x{VH}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                          "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    arr = np.zeros((VH, VW, 4), np.uint8); s = skia.Surface(arr); c = s.getCanvas()
    f0 = int(round(starts[i] * FPS))
    for fr in range(n):
        lt = fr / FPS
        draw(c, i, lt, D, starts[i] + lt, total, f0 + fr, leads[i], grps[i])
        s.flushAndSubmit(); p.stdin.write(arr.tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, out)


def still(base, i, f, out):
    meta, leads, durs, starts, total, grps = build(base)
    arr = np.zeros((VH, VW, 4), np.uint8); s = skia.Surface(arr); c = s.getCanvas()
    lt = f * durs[i]
    draw(c, i, lt, durs[i], starts[i] + lt, total, 0, leads[i], grps[i]); s.flushAndSubmit()
    skia.Image.fromarray(arr, colorType=skia.kRGBA_8888_ColorType).save(out, skia.kJPEG, 88)


if __name__ == "__main__":
    base = sys.argv[2]
    if sys.argv[1] == "scene":
        render_scene(base, int(sys.argv[3]))
    elif sys.argv[1] == "stills":
        for i, f in [(0, .85), (1, .97), (2, .9), (3, .9), (4, .9), (5, .9)]:
            still(base, i, f, f"{base}/st{i}.jpg")
    elif sys.argv[1] == "audio":
        meta, leads, durs, starts, total, grps = build(base)
        ins, flt = [], []
        for i in range(len(meta)):
            ins += ["-i", f"{base}/vo/p{i}.mp3"]; ms = int((starts[i] + leads[i]) * 1000)
            flt.append(f"[{i}:a]aresample=44100,aformat=channel_layouts=stereo,adelay={ms}|{ms}[v{i}]")
        n = len(meta)
        subprocess.run(["python3", os.path.join(os.path.dirname(os.path.abspath(__file__)), "music.py"), str(total + 9), f"{base}/music.wav"], check=True)
        flt.append("".join(f"[v{i}]" for i in range(n)) + f"amix=inputs={n}:normalize=0,apad=whole_dur={total}[vo]")
        flt.append("[vo]asplit=2[vo1][vosc]")
        flt.append(f"[{n}:a]atrim=start=9,asetpts=PTS-STARTPTS,volume=0.14[mus]")
        flt.append("[mus][vosc]sidechaincompress=threshold=0.03:ratio=6:attack=40:release=500[duck]")
        flt.append(f"[vo1][duck]amix=inputs=2:normalize=0,atrim=0:{total},loudnorm=I=-14:TP=-1.5[out]")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-i", f"{base}/music.wav", "-filter_complex", ";".join(flt),
                        "-map", "[out]", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", f"{base}/mix.m4a"], check=True)
        print("total", total, "scenes", len(meta))
