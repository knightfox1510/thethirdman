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

# ---- shotfig: a drawn side-on figure in four phases (our own illustration, always labelled ILLUSTRATIVE) ----------------------------------------------------------------
POSES = {   # joints on a 100 x 100 board (y down): head, hip, front knee/foot, back knee/foot, hands, bat tip
    "stance":  dict(head=(46, 16), hip=(46, 52), kf=(54, 72), ff=(60, 94), kb=(40, 73), fb=(33, 94), hands=(56, 40), bat=(63, 90)),
    "across":  dict(head=(42, 16), hip=(41, 52), kf=(52, 72), ff=(62, 94), kb=(34, 74), fb=(26, 94), hands=(46, 28), bat=(30, 6)),
    "punch":   dict(head=(48, 18), hip=(47, 52), kf=(56, 73), ff=(62, 94), kb=(41, 76), fb=(34, 90), hands=(66, 30), bat=(90, 22)),
    "finish":  dict(head=(48, 14), hip=(44, 50), kf=(55, 72), ff=(61, 94), kb=(40, 74), fb=(34, 88), hands=(58, 4), bat=(46, -8)),
}


def _fig(c, x, y, sc, pose, col, a, bat=(226, 150, 24)):
    P = POSES[pose]; X = lambda k: (x + P[k][0] * sc, y + P[k][1] * sc)
    sh = (P["hip"][0] + (P["head"][0] - P["hip"][0]) * .78, P["hip"][1] + (P["head"][1] - P["hip"][1]) * .78)               # the shoulders, 78% of the way up the trunk
    S = (x + sh[0] * sc, y + sh[1] * sc)
    def ln(p0, p1, w, cc):
        pt = paint(cc, a, stroke=w); pt.setStrokeCap(skia.Paint.kRound_Cap); c.drawLine(p0[0], p0[1], p1[0], p1[1], pt)
    ln(X("hip"), S, sc * 5.2, col); ln(X("hip"), X("kf"), sc * 4.2, col); ln(X("kf"), X("ff"), sc * 3.6, col); ln(X("hip"), X("kb"), sc * 4.2, col); ln(X("kb"), X("fb"), sc * 3.6, col)
    ln(S, X("hands"), sc * 3.4, col); ln(X("hands"), X("bat"), sc * 2.6, bat)
    c.drawCircle(*X("head"), sc * 5.2, paint(col, a)); c.drawCircle(X("head")[0] + sc * 1.8, X("head")[1] - sc * 1.0, sc * 5.6, paint((255, 255, 255), .0))


def sc_shotfig(c, g, t, D, s):
    LK.header(c, g, t, D, dict(s, title=s["head"]["t"], sub=s["head"].get("sub", ""))); l = SS._L(g); x0, x1 = l["x0"], l["x1"]; y0 = l["top"] + 30
    if s.get("photo"):
        ph = s["photo"]; qa = eo(prog(t, .05, .5)); pw = 430; ph_h = 430; im = SS._pimg(ph["img"])
        c.save(); c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x0, y0, pw, ph_h), 20, 20), doAntiAlias=True)
        c.drawImageRect(im, skia.Rect.MakeLTRB(*ph["crop"]), skia.Rect.MakeXYWH(x0, y0, pw, ph_h), SAMP, paint((255, 255, 255), qa)); c.restore()
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x0, y0, pw, ph_h), 20, 20), paint(gfx.INK, qa, stroke=4))
        xr = x0 + pw + 40; wr = x1 - xr
        text(c, "ILLUSTRATIVE", xr, y0 + 40, 24, "monoSB", LK.RED, qa, track=3)
        for j, ln_ in enumerate(E.wrap(s["cap"], wr, 34, "interB")[:8]): text(c, ln_, xr, y0 + 100 + 48 * j, 34, "interB", gfx.INK, eo(prog(t, .3 + .08 * j, .8 + .08 * j)))
        gy = y0 + ph_h + 50
    else: gy = y0
    pw_ = (x1 - x0 - 24) / 2; ph2 = 380; steps = s["steps"]
    for k, st in enumerate(steps):
        cx_ = x0 + (k % 2) * (pw_ + 24); cy_ = gy + (k // 2) * (ph2 + 24); q = eo(prog(t, .5 + .55 * k, 1.0 + .55 * k)); on = prog(t, .5 + .55 * k, 99) > 0
        rrect(c, cx_, cy_, pw_, ph2, 18, (255, 255, 255), q, stroke=3, scol=LK.RED if k == len(steps) - 1 else gfx.INK, sa=q)
        gnd = paint((120, 120, 110), .6 * q, stroke=3); c.drawLine(cx_ + 24, cy_ + ph2 - 82, cx_ + pw_ - 24, cy_ + ph2 - 82, gnd)
        _fig(c, cx_ + pw_ * .22, cy_ + 34, 2.85, st["pose"], gfx.INK, q)
        if st.get("ball") and k >= 2:
            bx, by = st["ball"]; c.drawCircle(cx_ + pw_ * .22 + bx * 2.85, cy_ + 34 + by * 2.85, 9, paint(LK.RED, q))
        c.drawCircle(cx_ + 34, cy_ + 34, 22, paint(LK.RED, q)); text(c, str(k + 1), cx_ + 34, cy_ + 43, 28, "interB", (255, 255, 255), q, "c")
        text(c, st["t"], cx_ + 24, cy_ + ph2 - 40, E.fit(st["t"], pw_ - 48, 30, "interB", -1), "interB", gfx.INK, q); text(c, st.get("d", ""), cx_ + 24, cy_ + ph2 - 12, E.fit(st.get("d", ""), pw_ - 48, 18, "monoSB", 1), "monoSB", gfx.MUTED, q, track=1)


def sc_cordon(c, g, t, D, s):
    """The slip cordon from above (our illustration; fielder positions are typical, not the actual field) with the edges' directions from the day's wagon coordinates and an empty chair where a third slip would stand."""
    LK.header(c, g, t, D, dict(s, title=s["head"]["t"], sub=s["head"].get("sub", ""))); l = SS._L(g); x0, x1 = l["x0"], l["x1"]; a = eo(prog(t, .05, .5)); W = g.W
    cx = x0 + 150; cy = l["bot"] - 190; Rb = min(cy - l["top"] - 110, 760)
    c.drawCircle(cx, cy, Rb, paint((226, 233, 214), a)); c.drawCircle(cx, cy, Rb, paint(gfx.INK, a, stroke=4)); c.drawCircle(cx, cy, Rb * .55, paint(gfx.INK, .25 * a, stroke=2))
    rrect(c, cx - 14, cy - 40, 28, 90, 4, (214, 196, 150), a)
    for k in (-1, 0, 1): c.drawRect(skia.Rect.MakeXYWH(cx + k * 8 - 1.5, cy - 44, 3, 9), paint(gfx.INK, a))
    text(c, "BATTER'S STUMPS", cx + 26, cy + 34, 17, "monoSB", gfx.MUTED, a, "l", track=1); text(c, "BEHIND THE WICKET", cx + Rb * .35, l["top"] + 8, 18, "monoSB", gfx.MUTED, a, "c", track=2)
    F = [("KEEPER", 0, 75), ("1ST SLIP", 11, 135), ("2ND SLIP", 20, 185), (None, 30, 238), ("GULLY", 58, 215)]
    for i, (lab, ang, r) in enumerate(F):
        q = eo(prog(t, .2 + .12 * i, .7 + .12 * i)); th = math.radians(ang); fx = cx + r * math.sin(th); fy = cy - r * math.cos(th)
        if lab:
            c.drawCircle(fx, fy, 17, paint(gfx.INK, q)); text(c, lab, fx + 26, fy + 7, 20, "monoSB", gfx.INK, q, "l", track=1)
        else:
            e = eo(prog(t, s.get("empty_at", 3.0), s.get("empty_at", 3.0) + .6)) if s.get("empty_at") else q
            dp = paint(LK.RED, max(q, e), stroke=5); c.drawCircle(fx, fy, 22, dp)
            c.drawRect(skia.Rect.MakeXYWH(fx - 9, fy - 12, 18, 14), paint(LK.RED, max(q, e)))                                    # a chair: seat, back, legs
            c.drawRect(skia.Rect.MakeXYWH(fx - 9, fy - 24, 4, 14), paint(LK.RED, max(q, e))); c.drawLine(fx - 8, fy + 2, fx - 8, fy + 14, paint(LK.RED, max(q, e), stroke=3)); c.drawLine(fx + 8, fy + 2, fx + 8, fy + 14, paint(LK.RED, max(q, e), stroke=3))
            text(c, s["empty"], fx + 32, fy + 7, 22, "interB", LK.RED, max(q, e), "l")
    for i, e in enumerate(s["edges"]):
        q = clamp((t - (s.get("ray_at", 1.2) + .5 * i)) / .6)
        if q <= 0: continue
        th = math.radians(e["ang"]); R = Rb * e.get("len", 1.0); ex = cx + R * math.sin(th) * q; ey = cy - R * math.cos(th) * q
        p = paint(LK.RED, .9, stroke=5); c.drawLine(cx, cy - 20, ex, ey, p); c.drawCircle(ex, ey, 10, paint(LK.RED, 1))
        if q >= 1: text(c, e["lab"], ex + 16, ey + 8 + 4 * (i % 2), 22, "monoSB", gfx.INK, 1, "l", track=1)
    text(c, s["foot"], x0, l["bot"] + 40, 18, "mono", gfx.MUTED, eo(prog(t, .8, 1.4)))


def install(engine, looks):
    global E, LK
    E = engine; LK = looks
    E.SCENES.update({"techimg": sc_techimg, "follow": sc_follow, "shotfig": sc_shotfig, "cordon": sc_cordon})
