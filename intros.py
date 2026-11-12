"""Channel intro options for The Third Man. usage: intros.py <name|all> [theme] [fmt] [scale]"""
import os, sys, math, subprocess, wave, numpy as np, skia
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine, gfx
from gfx import text, rrect, paint, prog, eo, eio, eback, lerp, clamp, twidth

FPS = 30
TAG = "CRICKET FROM A DIFFERENT ANGLE"


def lockup_center(c, g, y, h, a, t0, t):
    """Mark + wordmark reveal, centred at y; animated from t0."""
    p = eback(prog(t, t0, t0 + .5)); pw = eo(prog(t, t0 + .15, t0 + .65))
    tw = twidth("THIRD MAN", h * .62, "bebas", 1) + h * .28
    total = h + tw; x0 = g.W / 2 - total / 2
    c.save(); c.translate(x0 + h / 2, y); s = clamp(p, 0, 1.15); c.scale(s, s); c.translate(-(x0 + h / 2), -y)
    gfx.logo_mark(c, x0 + h / 2, y, h, a * clamp(p), detail=True)
    c.restore()
    text(c, "THE", x0 + h * 1.28 + (1 - pw) * 40, y - h * .14, h * .2, "interB", gfx.MUTED, a * pw, track=h * .06)
    text(c, "THIRD MAN", x0 + h * 1.26 + (1 - pw) * 40, y + h * .33, h * .62, "bebas", gfx.INK, a * pw, track=1)


def tagline(c, g, y, a):
    text(c, TAG, g.W / 2, y, 30 if g.fmt == "long" else 32, "interB", gfx.GOLD, a, "c", track=7)


# ---------------------------------------------------------------- A: field map (the logo draws itself)
def intro_fieldmap(c, g, t):
    engine.outro_frame(c, g, min(t * 1.1, 3.2))


# ---------------------------------------------------------------- B: stumps (ball hits, bails fly, logo lands)
def intro_stumps(c, g, t):
    gfx.background(c, 50 + t)
    W, H = g.W, g.H
    gy = H * (.66 if g.fmt == "long" else .58)
    cx = W / 2
    fade = 1 - eio(prog(t, 1.55, 1.95))
    if fade > 0:
        c.drawLine(cx - 420, gy, cx + 420, gy, paint(gfx.LINE, fade, stroke=6))
        hit = t >= 1.2
        shake = (math.sin(t * 70) * 6 * (1 - prog(t, 1.2, 1.6))) if hit else 0
        for k, dx in enumerate((-46, 0, 46)):
            ps = eback(prog(t, .05 + k * .08, .45 + k * .08))
            h = 300 * clamp(ps, 0, 1.08)
            ang = (shake * (1.5 if k == 1 else .6)) if hit else 0
            c.save(); c.translate(cx + dx, gy); c.rotate(ang)
            rrect(c, -11, -h, 22, h, 6, gfx.INK, fade)
            c.restore()
        # bails
        for k, side in enumerate((-1, 1)):
            if not hit:
                pb = eo(prog(t, .5, .7))
                rrect(c, cx + side * 23 - 26, gy - 312, 52, 12, 5, gfx.GOLD, pb * fade)
            else:
                tt = t - 1.2
                bx = cx + side * 23 + side * 380 * tt; by = gy - 312 - 520 * tt + 900 * tt * tt
                c.save(); c.translate(bx, by); c.rotate(side * 720 * tt)
                rrect(c, -26, -6, 52, 12, 5, gfx.GOLD, fade); c.restore()
        # ball
        if t < 1.2:
            pb = eio(prog(t, .6, 1.2))
            bx = lerp(W + 60, cx, pb); by = lerp(gy - 420, gy - 150, pb) - math.sin(pb * math.pi) * 60
            for k in range(6):
                q = max(0, pb - k * .03)
                c.drawCircle(lerp(W + 60, cx, q), lerp(gy - 420, gy - 150, q) - math.sin(q * math.pi) * 60, 18 - k * 2, paint(gfx.RED, .25 * (1 - k / 6)))
            c.drawCircle(bx, by, 20, paint(gfx.RED))
        pr = prog(t, 1.2, 1.7)
        if 0 < pr < 1:
            c.drawCircle(cx, gy - 150, 30 + 260 * eo(pr), paint(gfx.GOLD, .9 * (1 - pr), stroke=8))
    lockup_center(c, g, H * .45 if g.fmt == "long" else H * .45, 210 if g.fmt == "long" else 170, 1, 1.7, t)
    tagline(c, g, H * .45 + (200 if g.fmt == "long" else 190), eo(prog(t, 2.25, 2.7)))


# ---------------------------------------------------------------- C: scoreboard flip (tiles spell the name)
def intro_flip(c, g, t):
    gfx.background(c, 80 + t)
    W, H = g.W, g.H
    long = g.fmt == "long"
    rows = ["THE", "THIRD MAN"]
    tw_, th_, gap = (118, 160, 12) if long else (96, 132, 10)
    y0 = H * (.30 if long else .32)
    k = 0
    for r, word in enumerate(rows):
        n = len(word)
        x0 = W / 2 - (n * tw_ + (n - 1) * gap) / 2
        y = y0 + r * (th_ + 24)
        for i, ch in enumerate(word):
            st = .15 + k * .09; k += 1
            if ch == " ":
                continue
            p = prog(t, st, st + .28)
            x = x0 + i * (tw_ + gap)
            rrect(c, x, y, tw_, th_, 10, gfx.INK, .14)
            if p <= 0: continue
            sy = abs(math.cos(math.pi * (1 - eo(p)))) if p < 1 else 1
            c.save(); c.translate(x + tw_ / 2, y + th_ / 2); c.scale(1, max(.02, sy))
            rrect(c, -tw_ / 2, -th_ / 2, tw_, th_, 10, gfx.INK, 1)
            text(c, ch, 0, th_ * .30, th_ * .78, "bebas", gfx.GOLD if r == 1 and i >= 6 else gfx.BG, 1, "c")
            c.restore()
            c.drawRect(skia.Rect.MakeXYWH(x, y + th_ / 2 - 1.5, tw_, 3), paint(gfx.BG, .9))
    pm = eback(prog(t, 1.55, 2.05))
    if pm > 0:
        gfx.logo_mark(c, W / 2, y0 + 2 * (th_ + 24) + (150 if long else 140), (190 if long else 170) * clamp(pm, 0, 1.15), clamp(pm))
    tagline(c, g, y0 + 2 * (th_ + 24) + (330 if long else 310), eo(prog(t, 2.2, 2.7)))


# ---------------------------------------------------------------- D: kinetic type (Every ball. Every field. Every angle.)
def intro_kinetic(c, g, t):
    gfx.background(c, 120 + t)
    W, H = g.W, g.H
    words = [("EVERY BALL.", 0.0), ("EVERY FIELD.", .45), ("EVERY ANGLE.", .9)]
    for i, (w, st) in enumerate(words):
        en = st + .45 if i < 2 else 1.5
        if st <= t < en:
            p = prog(t, st, en)
            sz = engine.fit(w, W - 200, 230 if g.fmt == "long" else 170, "bebas")
            s = 1.12 - .12 * eo(prog(t, st, st + .2))
            c.save(); c.translate(W / 2, H / 2); c.scale(s, s)
            text(c, w, 0, sz * .35, sz, "bebas", gfx.GOLD if i == 2 else gfx.INK, 1 if i < 2 else 1 - prog(t, 1.35, 1.5), "c", track=3)
            c.restore()
    if t >= 1.45:
        lockup_center(c, g, H * .45, 210 if g.fmt == "long" else 170, 1, 1.5, t)
        tagline(c, g, H * .45 + (200 if g.fmt == "long" else 190), eo(prog(t, 2.05, 2.5)))


INTROS = {"fieldmap": (intro_fieldmap, 1.45), "stumps": (intro_stumps, 1.2), "flip": (intro_flip, 1.55), "kinetic": (intro_kinetic, 1.5)}
DUR = 3.2


def audio(path, impact, ticks=(), dur=DUR):
    from scipy.signal import butter, lfilter
    SR = 48000; n = int(SR * dur); t = np.arange(n) / SR; rng = np.random.default_rng(5)
    b, a = butter(2, [800 / (SR / 2), 6000 / (SR / 2)], "band")
    env = np.clip((t - (impact - .6)) / .6, 0, 1) ** 2 * np.exp(-np.clip(t - impact, 0, None) * 8)
    out = lfilter(b, a, rng.standard_normal(n)) * env * .3
    kt = np.clip(t - impact, 0, None)
    out += np.sin(2 * np.pi * (55 + 60 * np.exp(-kt * 25)) * kt) * np.exp(-kt * 7) * (t >= impact) * .7
    for k, f in enumerate([880, 1108.7, 1318.5, 1760]):
        st = impact + .1 + k * .06; tt = np.clip(t - st, 0, None)
        out += (np.sin(2 * np.pi * f * tt) + .3 * np.sin(2 * np.pi * 2.76 * f * tt)) * np.exp(-tt * 2.6) * (t >= st) * .1
    hb, ha = butter(2, 3000 / (SR / 2), "high")
    for tk in ticks:
        i0 = int(tk * SR); L = int(.03 * SR)
        if i0 + L < n: out[i0:i0 + L] += lfilter(hb, ha, rng.standard_normal(L)) * np.exp(-np.arange(L) / SR * 120) * .35
    out *= np.clip((dur - t) / .5, 0, 1)
    out /= np.abs(out).max() + 1e-9; out *= .8
    st = np.stack([out, np.roll(out, 300)], 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype(np.int16).tobytes())


def render(name, theme="whites", fmt="long", scale=1.0, out=None):
    engine.apply_theme(theme); g = engine.setup(fmt)
    fn, impact = INTROS[name]
    OW, OH = int(g.W * scale), int(g.H * scale)
    out = out or f"{engine.ROOT}/out/intro_{name}_{theme}_{fmt}.mp4"
    vid = out.replace(".mp4", "_v.mp4"); wav = out.replace(".mp4", ".wav")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{OW}x{OH}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", vid], stdin=subprocess.PIPE)
    arr = np.zeros((OH, OW, 4), np.uint8); sf = skia.Surface(arr); c = sf.getCanvas()
    for fr in range(int(DUR * FPS)):
        t = fr / FPS
        c.save(); c.scale(scale, scale); fn(c, g, t); gfx.grain(c, fr); c.restore()
        sf.flushAndSubmit(); p.stdin.write(arr.tobytes())
    p.stdin.close(); p.wait()
    ticks = [.15 + k * .09 + .14 for k in range(12)] if name == "flip" else ()
    audio(wav, impact, ticks)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vid, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-ar", "48000", "-ac", "2", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
    return out


if __name__ == "__main__":
    names = list(INTROS) if sys.argv[1] == "all" else [sys.argv[1]]
    theme = sys.argv[2] if len(sys.argv) > 2 else "whites"
    fmt = sys.argv[3] if len(sys.argv) > 3 else "long"
    scale = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
    for n in names: print(render(n, theme, fmt, scale))
