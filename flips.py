"""Flip Shorts: a benchmark vs challengers at the same point in their careers, no narration, cut to a beat.

    python3 flips.py specs/flip_<slug>.json         # -> deliver/<slug>/<files.short>.mp4 (+ _cover.jpg)

Spec:
  slug, files.short, title{kicker, lines[], sub}, metric, better ("higher"|"lower"),
  bench{name, team, pose, color}, pairs[{name, team, pose, n, value, bench, color?}],   # bench = benchmark's value at the same point
  end{lines[], ask}, dec, suffix, sources[], yt{short{...}}
Look: hard cuts on the beat between a benchmark panel and a challenger panel, team colours (no logos or photos),
an original silhouette, the player's name on a white bar, and one giant number. Music is synthesised here."""
import json, os, subprocess, sys
import numpy as np, skia

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import engine as E, gfx

W, H, FPS = 1080, 1920, 30
BPM = 100; BEAT = 60 / BPM
FLIP = 2 * BEAT              # each panel holds for two beats (1.2 s)
TITLE, END = 4 * BEAT, 5 * BEAT


def hexcol(h): h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def panel_color(p, default):
    if p.get("color"): return hexcol(p["color"]) if isinstance(p["color"], str) else tuple(p["color"])
    if p.get("team") in E.TEAMS: return E.TEAMS[p["team"]][0]
    return default


def lum(c): return (0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]) / 255


def stripes(c, col, t):
    """Diagonal band texture over a flat panel (tone of the panel itself)."""
    c.drawRect(skia.Rect.MakeWH(W, H), gfx.paint(col))
    shade = tuple(min(255, int(v * 1.12 + 8)) for v in col) if lum(col) < .5 else tuple(int(v * .9) for v in col)
    c.save(); c.rotate(-28)
    off = (t * 40) % 120
    for x in range(-2400, 2400, 120):
        c.drawRect(skia.Rect.MakeXYWH(x + off, -400, 46, 3600), gfx.paint(shade, .55))
    c.restore()


def panel(c, spec, who, value, n_label, col, t, bench=False):
    stripes(c, col, t)
    ink = (255, 255, 255) if lum(col) < .62 else (16, 20, 30)
    pop = 1 + .05 * max(0, 1 - t / .18)                       # small punch-in on every cut
    c.save(); c.translate(W / 2, H / 2); c.scale(pop, pop); c.translate(-W / 2, -H / 2)
    # top: kicker
    E.text(c, spec["title"]["kicker"], W / 2, 150, 34, "interB", ink, .85, "c", track=6)
    # silhouette in a ring (stands in for a photo)
    cx, cy = W / 2, 520
    c.drawCircle(cx, cy, 250, gfx.paint(ink, .10))
    c.drawCircle(cx, cy, 250, gfx.paint(ink, .9, stroke=8))
    fig_col = ink
    E.figure(c, who.get("pose", "stance"), cx + (20 if who.get("pose") == "release" else 0), cy + 225, 400, fig_col, 1,
             mirror=who.get("mirror", False), ball=who.get("pose") in ("release", "spin"))
    # name bar
    by = 820
    c.drawRect(skia.Rect.MakeXYWH(0, by, W, 96), gfx.paint((255, 255, 255)))
    nm = who["name"].upper(); E.text(c, nm, W / 2, by + 68, E.fit(nm, W - 120, 64, "bebas", 3), "bebas", (16, 20, 30), 1, "c", track=3)
    if who.get("team"):   # neutral pill so the code reads on any panel colour (no logos)
        code = who["team"]; fs = 30; pw = E.twidth(code, fs, "interB", 3) + 44
        gfx.rrect(c, W / 2 - pw / 2, by + 116, pw, 50, 25, ink, .16)
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(W / 2 - pw / 2, by + 116, pw, 50), 25, 25), gfx.paint(ink, .9, stroke=3))
        E.text(c, code, W / 2, by + 152, fs, "interB", ink, 1, "c", track=3)
    E.text(c, ("AFTER " if bench else "") + n_label, W / 2, by + 228, 40, "interB", ink, .9, "c", track=4)
    # the number
    dec = spec.get("dec", 1); vs = f"{value:,.{dec}f}{spec.get('suffix', '')}"
    E.text(c, vs, W / 2, 1420, E.fit(vs, W - 120, 330, "bebas", 2), "bebas", ink, 1, "c")
    E.text(c, spec["metric"], W / 2, 1510, 56, "bebas", ink, .95, "c", track=6)
    if spec.get("better"): E.text(c, f"{spec['better'].upper()} IS BETTER", W / 2, 1566, 28, "interB", ink, .7, "c", track=5)
    c.restore()
    gfx.logo_lockup(c, 70, H - 120, 64, .9) if lum(col) < .5 else None


def title_card(c, spec, t):
    gfx.apply_theme("floodlights"); gfx.background(c, t + 3)
    ti = spec["title"]; p = gfx.eo(gfx.clamp(t / .5))
    E.text(c, ti["kicker"], W / 2, 640, 38, "interB", gfx.GOLD, p, "c", track=8)
    y = 760
    for k, ln in enumerate(ti["lines"]):
        z = E.fit(ln, W - 140, 150, "bebas", 2); y += z * .92
        q = gfx.eo(gfx.clamp((t - .15 * k) / .45))
        E.text(c, ln, W / 2 + (1 - q) * 60, y, z, "bebas", gfx.INK if k == 0 else gfx.GOLD, q, "c", track=2)
    if ti.get("sub"):
        for j, l in enumerate(E.wrap(ti["sub"], W - 200, 40, "interSB")):
            E.text(c, l, W / 2, y + 110 + j * 52, 40, "interSB", gfx.MUTED, gfx.clamp((t - .5) / .4), "c")
    gfx.logo_lockup(c, W / 2, 1650, 80, 1, "c")


def end_card(c, spec, t):
    gfx.apply_theme("floodlights"); gfx.background(c, t + 3)
    en = spec["end"]; y = 720
    for k, ln in enumerate(en["lines"]):
        z = E.fit(ln, W - 140, 140, "bebas", 2); y += z * .92
        q = gfx.eo(gfx.clamp((t - .12 * k) / .4))
        E.text(c, ln, W / 2, y, z, "bebas", gfx.INK if k % 2 == 0 else gfx.GOLD, q, "c", track=2)
    if en.get("ask"):
        q = gfx.eo(gfx.clamp((t - .6) / .4)); s = en["ask"]; pw = E.twidth(s, 40, "interB", 4) + 90
        gfx.rrect(c, W / 2 - pw / 2, y + 90, pw, 92, 46, gfx.GOLD, q)
        E.text(c, s, W / 2, y + 150, 40, "interB", gfx.BG, q, "c", track=4)


def timeline(spec):
    segs = [("title", TITLE, None)]
    for p in spec["pairs"]:
        segs += [("bench", FLIP, p), ("chal", FLIP, p)]
    segs.append(("end", END, None))
    return segs


def music(path, dur, cuts):
    """A punchy synthesised beat at BPM: kick, clap, hats, bass and a short riser on every cut."""
    from scipy.signal import butter, lfilter
    SR = 48000; n = int(SR * dur); t = np.arange(n) / SR; out = np.zeros(n); rng = np.random.default_rng(7)
    hb, ha = butter(2, 6000 / (SR / 2), "high"); nb, na = butter(2, [900 / (SR / 2), 5000 / (SR / 2)], "band")
    roots = [45, 45, 41, 43]   # A A F G
    k = 0
    while k * BEAT < dur:
        i0 = int(k * BEAT * SR); L = min(n - i0, int(.35 * SR)); tt = np.arange(L) / SR
        out[i0:i0 + L] += np.sin(2 * np.pi * (48 + 90 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 9) * .9            # kick
        if k % 2 == 1:
            Lc = min(n - i0, int(.18 * SR))
            out[i0:i0 + Lc] += lfilter(nb, na, rng.standard_normal(Lc)) * np.exp(-np.arange(Lc) / SR * 22) * .55   # clap
        for h in (0, .5):
            j0 = int((k + h) * BEAT * SR); Lh = min(n - j0, int(.05 * SR))
            if Lh > 0: out[j0:j0 + Lh] += lfilter(hb, ha, rng.standard_normal(Lh)) * np.exp(-np.arange(Lh) / SR * 80) * .18
        f = 440 * 2 ** ((roots[(k // 4) % 4] - 69) / 12); Lb = min(n - i0, int(BEAT * .9 * SR)); tb = np.arange(Lb) / SR
        out[i0:i0 + Lb] += np.sign(np.sin(2 * np.pi * f * tb)) * np.exp(-tb * 5) * .12                              # bass pluck
        k += 1
    for cut in cuts:                                                                                                  # whoosh into each cut
        a = int(max(0, cut - .25) * SR); b = min(n, int(cut * SR)); L = b - a
        if L > 0: out[a:b] += lfilter(nb, na, rng.standard_normal(L)) * np.linspace(0, 1, L) ** 2 * .25
    out *= np.clip((dur - t) / .6, 0, 1); out /= np.abs(out).max() + 1e-9; out *= .85
    st = np.stack([out, np.roll(out, 240)], 1)
    import wave
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype(np.int16).tobytes())


def build(spec_path):
    spec = json.load(open(spec_path)); slug = spec["slug"]
    base = f"{ROOT}/out/{slug}/flip"; os.makedirs(base, exist_ok=True)
    outdir = f"{ROOT}/deliver/{slug}"; os.makedirs(outdir, exist_ok=True)
    E.apply_theme("floodlights")
    segs = timeline(spec); total = sum(s[1] for s in segs)
    bench_col = panel_color(spec["bench"], (200, 30, 40))
    tmp = f"{base}/video.tmp.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), tmp],
                         stdin=subprocess.PIPE)
    arr = np.zeros((H, W, 4), np.uint8); sf = skia.Surface(arr); c = sf.getCanvas()
    cuts, t0, frame = [], 0.0, 0
    cover = None
    for kind, d, pr in segs:
        cuts.append(t0)
        n = int(round((t0 + d) * FPS)) - int(round(t0 * FPS))
        for f in range(n):
            t = f / FPS; c.clear(skia.ColorBLACK)
            if kind == "title": title_card(c, spec, t)
            elif kind == "end": end_card(c, spec, t)
            elif kind == "bench":
                panel(c, spec, spec["bench"], pr["bench"], pr["n"], bench_col, t, bench=True)
            else:
                panel(c, spec, pr, pr["value"], pr["n"], panel_color(pr, (240, 200, 30)), t)
            gfx.grain(c, frame); frame += 1
            sf.flushAndSubmit(); p.stdin.write(arr.tobytes())
            if kind == "title" and f == n - 1: cover = arr[..., :3].copy()
        t0 += d
    p.stdin.close()
    if p.wait() != 0: raise SystemExit("render failed")
    wav = f"{base}/music.wav"; music(wav, total, cuts[1:])
    main = f"{base}/main.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-i", wav, "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
                    "-ar", "48000", "-ac", "2", "-c:a", "aac", "-b:a", "192k", "-shortest", main], check=True)
    outro = f"{ROOT}/out/outro_short.mp4"
    lst = f"{base}/final.txt"; open(lst, "w").write(f"file '{main}'\nfile '{outro}'\n")
    final = f"{outdir}/{spec['files']['short']}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags", "+faststart", final], check=True)
    from PIL import Image
    Image.fromarray(cover).save(f"{outdir}/{spec['files']['short']}_cover.jpg", quality=92)
    print(final)


if __name__ == "__main__":
    build(sys.argv[1])
