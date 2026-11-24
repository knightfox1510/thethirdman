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
    """The supplied technique graphic, cut down to the figure (no callout text); our own labels sit beside it. crop = (x0, y0, x1, y1) in image pixels; ring = (x, y, r) in image pixels."""
    LK.header(c, g, t, D, dict(s, title=s["head"]["t"], sub=s["head"].get("sub", ""))); l = SS._L(g)
    x0, x1 = l["x0"], l["x1"]; cr = s["crop"]; cwid = cr[2] - cr[0]; chgt = cr[3] - cr[1]; ch = 760; cw = ch * cwid / chgt; y0 = l["top"] + 50; a = eo(prog(t, .05, .5))
    im = SS._pimg(s["img"])
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x0, y0 + 14, cw, ch), 18, 18), paint((0, 0, 0), .22 * a, blur=22))
    c.save(); c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x0, y0, cw, ch), 18, 18), doAntiAlias=True)
    c.drawRect(skia.Rect.MakeXYWH(x0, y0, cw, ch), paint((255, 255, 255), a))
    c.drawImageRect(im, skia.Rect.MakeLTRB(*cr), skia.Rect.MakeXYWH(x0, y0, cw, ch), SAMP, paint((255, 255, 255), a))
    for mx0, my0, mx1, my1 in s.get("mask", []):
        k = cw / cwid; c.drawRect(skia.Rect.MakeLTRB(x0 + (mx0 - cr[0]) * k, y0 + (my0 - cr[1]) * k, x0 + (mx1 - cr[0]) * k, y0 + (my1 - cr[1]) * k), paint((255, 255, 255), a))
    if s.get("ring"):
        rx, ry, rr = s["ring"]; k = cw / cwid; pulse = 1 + .05 * math.sin(t * 5); q = eo(prog(t, .5, 1.0))
        c.drawOval(skia.Rect.MakeXYWH(x0 + (rx - rr - cr[0]) * k - rr * k * (pulse - 1), y0 + (ry - rr * .8 - cr[1]) * k - rr * k * (pulse - 1), 2 * rr * k * pulse, 1.6 * rr * k * pulse), paint(LK.RED, q, stroke=8))
    c.restore(); c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x0, y0, cw, ch), 18, 18), paint(gfx.INK, a, stroke=4))
    xr = x0 + cw + 40; wr = x1 - xr; q = eo(prog(t, .3, .9))
    c.drawCircle(xr + 40, y0 + 50, 40, paint(LK.RED, q)); text(c, s["n"], xr + 40, y0 + 72, 56, "interB", (255, 255, 255), q, "c")
    text(c, s.get("tag", ""), xr, y0 + 150, 22, "monoSB", LK.RED, q, track=2)
    for j, ln in enumerate(E.wrap(s["title"], wr, 54, "interB")[:3]): text(c, ln, xr, y0 + 215 + 62 * j, 54, "interB", gfx.INK, q)
    yb = y0 + 215 + 62 * min(3, len(E.wrap(s["title"], wr, 54, "interB"))) + 30
    for j, ln in enumerate(E.wrap(s["body"], wr, 32, "interB")[:9]): text(c, ln, xr, yb + 46 * j, 32, "interB", gfx.INK, eo(prog(t, .6 + .1 * j, 1.1 + .1 * j)))


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
