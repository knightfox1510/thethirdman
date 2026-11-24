"""Scenes for the Vaibhav Suryavanshi technique explainer (lab look): 'techimg' (a supplied technique graphic zooms to one callout, with our own ring and caption) and 'follow' (C versus O follow-through, drawn).
Installed by looks.install."""
import math
import skia
import gfx
from gfx import text, rrect, paint, prog, eo, clamp
import shot_scenes as SS
E = None; LK = None
SAMP = skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear)


def sc_techimg(c, g, t, D, s):
    LK.header(c, g, t, D, SS._hd(s)); l = SS._L(g); sh = g.fmt == "short"
    x0, x1 = l["x0"], l["x1"]; cw = x1 - x0; ch = cw * 9 / 16; y0 = l["top"] + 40; a = eo(prog(t, .05, .5))
    im = SS._pimg(s["img"]); iw, ih = im.width(), im.height(); bx0, by0, bx1, by1 = s["box"]
    zk = s.get("zoom", 2.3); zw = iw / zk; zh = ih / zk; zcx = (bx0 + bx1) / 2; zcy = (by0 + by1) / 2
    zx0 = min(max(zcx - zw / 2, 0), iw - zw); zy0 = min(max(zcy - zh / 2, 0), ih - zh); z = eo(prog(t, .4, 1.4))
    cr = (zx0 * z, zy0 * z, iw - (iw - zx0 - zw) * z, ih - (ih - zy0 - zh) * z)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x0, y0 + 14, cw, ch), 18, 18), paint((0, 0, 0), .22 * a, blur=22))
    c.save(); c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x0, y0, cw, ch), 18, 18), doAntiAlias=True)
    c.drawImageRect(im, skia.Rect.MakeLTRB(*cr), skia.Rect.MakeXYWH(x0, y0, cw, ch), SAMP, paint((255, 255, 255), a))
    if s.get("ring"):
        rx, ry, rr = s["ring"]; kx = cw / (cr[2] - cr[0]); ky = ch / (cr[3] - cr[1])
        pulse = 1 + .06 * math.sin(t * 5); q = eo(prog(t, .9, 1.4))
        c.drawOval(skia.Rect.MakeXYWH(x0 + (rx - rr - cr[0]) * kx, y0 + (ry - rr * .8 - cr[1]) * ky, 2 * rr * kx * pulse, 1.6 * rr * ky * pulse), paint(LK.RED, q, stroke=7))
    c.restore(); c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x0, y0, cw, ch), 18, 18), paint(gfx.INK, a, stroke=4))
    yb = y0 + ch + 70; q = eo(prog(t, .3, .9))
    c.drawCircle(x0 + 46, yb + 28, 46, paint(LK.RED, q)); text(c, s["n"], x0 + 46, yb + 52, 64, "interB", (255, 255, 255), q, "c")
    text(c, s["title"], x0 + 120, yb + 18, E.fit(s["title"], cw - 130, 58, "interB", -1), "interB", gfx.INK, q)
    text(c, s.get("tag", "THE BACKSWING"), x0 + 120, yb + 62, 24, "monoSB", LK.RED, q, track=2)
    for j, ln in enumerate(E.wrap(s["body"], cw, 36, "interB")[:4]): text(c, ln, x0, yb + 150 + 52 * j, 36, "interB", gfx.INK, eo(prog(t, .6 + .12 * j, 1.1 + .12 * j)))
    if s.get("foot"): text(c, s["foot"], x0, l["bot"] - 10, 20, "mono", gfx.MUTED, eo(prog(t, .8, 1.4)))


def _arc(c, cx, cy, r, a0, sweep, col, al, w=14):
    p = skia.Path(); p.addArc(skia.Rect.MakeXYWH(cx - r, cy - r, 2 * r, 2 * r), a0, sweep)
    pt = paint(col, al, stroke=w); pt.setStrokeCap(skia.Paint.kRound_Cap); c.drawPath(p, pt)


def sc_follow(c, g, t, D, s):
    LK.header(c, g, t, D, SS._hd(s)); l = SS._L(g); W = g.W; y0 = l["top"] + 80
    for k, (lab, sub, sw, col, a0) in enumerate((("MOST BATTERS", "THE FINISH LOOKS LIKE A  C", 200, gfx.INK, 120), ("VAIBHAV", "THE FINISH LOOKS LIKE AN  O", 330, LK.RED, 100))):
        cx = W / 2; cy = y0 + 250 + k * 560; q = eo(prog(t, .2 + .9 * k, 1.4 + .9 * k)); R = 190
        c.drawCircle(cx, cy, R + 34, paint((226, 233, 214), eo(prog(t, .1 + .9 * k, .5 + .9 * k))))
        c.drawCircle(cx - 30, cy + 60, 34, paint(gfx.INK, .85 * q))                    # head (the batter, from behind)
        _arc(c, cx - 30, cy + 40, R, a0, sw * q, col, q)
        ex = cx - 30 + R * math.cos(math.radians(a0 + sw * q)); ey = cy + 40 + R * math.sin(math.radians(a0 + sw * q)); c.drawCircle(ex, ey, 14, paint(col, q))
        text(c, lab, cx, cy - R - 50, 28, "monoSB", LK.RED if k else gfx.MUTED, q, "c", track=2); text(c, sub, cx, cy + R + 78, E.fit(sub, 880, 40, "interB", 0), "interB", gfx.INK, q, "c")
    if s.get("foot"): text(c, s["foot"], l["x0"], l["bot"] - 10, 20, "mono", gfx.MUTED, eo(prog(t, 1.2, 2)))


def install(engine, looks):
    global E, LK
    E = engine; LK = looks
    E.SCENES.update({"techimg": sc_techimg, "follow": sc_follow})
