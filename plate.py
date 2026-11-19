"""The "plate" look for Did You Know?: an old field-guide / naturalist's plate. Cream paper, double-ruled border, ink drawings with numbered figures, red stamp.
Scenes (installed into engine.SCENES by looks.install):
  plate       - PLATE I: a title, a hand-inked field (top-down, bowler at the top, right-hander, off side on the right) with numbered figures, optional dashed ball paths, a legend and a stamp
  plate_page  - a page of text for one idea (a theory, a rule): heading, body, a margin note, a small inset field and a stamp (e.g. UNPROVEN)
  plate_list  - a ruled table of dated entries with dotted leaders (year, what, detail), for "notable uses"
Everything is our own drawing (no photos, no logos). Field plans are illustrative; positions come from engine.POS."""
import math, random
import skia
import gfx
from gfx import text, rrect, paint, prog, eo, eio, eback, clamp, twidth

E = None
PAPER = (238, 226, 196)
INK = (52, 36, 26)
RED = (160, 40, 36)
FAINT = (150, 120, 70)
_BG = {}


def install(engine):
    global E
    E = engine
    E.SCENES.update({"plate": sc_plate, "plate_page": sc_plate_page, "plate_list": sc_plate_list})


# ---------------------------------------------------------------- paper
def bg(c, T_):
    W, H = gfx.W, gfx.H
    img = _BG.get((W, H))
    if img is None:
        arr = __import__("numpy").zeros((H, W, 4), "uint8"); sf = skia.Surface(arr); cc = sf.getCanvas(); r = random.Random(4)
        cc.clear(skia.Color(*PAPER))
        g = skia.Paint(); g.setShader(skia.GradientShader.MakeRadial((W / 2, H / 2), max(W, H) * .75, [skia.Color(244, 234, 206, 0), skia.Color(205, 180, 130, 90)], [0, 1])); cc.drawRect(skia.Rect.MakeWH(W, H), g)
        for _ in range(int(W * H / 700)): cc.drawCircle(r.random() * W, r.random() * H, r.uniform(.5, 2.0), paint(FAINT, r.uniform(.03, .13)))
        for _ in range(26):                                                       # a few fibres
            x, y = r.random() * W, r.random() * H; cc.drawLine(x, y, x + r.uniform(-40, 40), y + r.uniform(-12, 12), paint(FAINT, .08))
        sf.flushAndSubmit(); img = sf.makeImageSnapshot(); _BG[(W, H)] = img
    c.drawImage(img, 0, 0)


def _frame(c, g, a=1.0):
    """Double-ruled border; inside the Instagram-safe band for Shorts."""
    if g.fmt == "short": x0, y0, x1, y1 = 56, 262, g.W - 56, g.H - 262
    else: x0, y0, x1, y1 = 56, 50, g.W - 56, g.H - 50
    for o, w in ((0, 3.2), (16, 1.4)): c.drawRect(skia.Rect.MakeLTRB(x0 + o, y0 + o, x1 - o, y1 - o), paint(INK, .88 * a, stroke=w))
    return x0 + 16, y0 + 16, x1 - 16, y1 - 16


# ---------------------------------------------------------------- hand-inked primitives (deterministic jitter: no flicker between frames)
def _jcircle(c, cx, cy, rad, p, seed, j=2.6, n=72):
    r = random.Random(seed); pa = skia.Path()
    for k in range(n + 3):
        a = 2 * math.pi * k / n; rr = rad + r.uniform(-j, j)
        (pa.moveTo if k == 0 else pa.lineTo)(cx + rr * math.cos(a), cy + rr * math.sin(a))
    c.drawPath(pa, p)


def _jline(c, p0, p1, p, seed, j=1.6, seg=10):
    r = random.Random(seed); pa = skia.Path(); pa.moveTo(*p0)
    for k in range(1, seg + 1):
        f = k / seg; pa.lineTo(p0[0] + (p1[0] - p0[0]) * f + r.uniform(-j, j), p0[1] + (p1[1] - p0[1]) * f + r.uniform(-j, j))
    c.drawPath(pa, p)


def _fig(c, x, y, s, col, a, hot=False):
    """A little inked fielder: head, body, arms, a soft shadow."""
    c.drawOval(skia.Rect.MakeXYWH(x - 15 * s, y + 20 * s, 30 * s, 9 * s), paint((0, 0, 0), .16 * a))
    c.drawCircle(x, y - 22 * s, 10.5 * s, paint(col, .96 * a))
    p = paint(col, .96 * a, stroke=7 * s); p.setStrokeCap(skia.Paint.kRound_Cap); c.drawLine(x, y - 10 * s, x, y + 14 * s, p)
    p2 = paint(col, .96 * a, stroke=4.2 * s); p2.setStrokeCap(skia.Paint.kRound_Cap); c.drawLine(x - 13 * s, y - 2 * s, x + 13 * s, y - 2 * s, p2)
    c.drawLine(x, y + 14 * s, x - 7 * s, y + 26 * s, p2); c.drawLine(x, y + 14 * s, x + 7 * s, y + 26 * s, p2)


def field(c, cx, cy, R, figures, t, D, s, small=False, show_labels=True):
    """The inked field: boundary with engraved ticks, inner ring, pitch, batter, figures [{p|xy, fig, hl, label, at}], ball paths [{from, to, at, bend}]."""
    a = eo(prog(t, 0, .45)); k = R / 400
    _jcircle(c, cx, cy, R, paint(INK, .88 * a, stroke=3.4), 11, 3 * k)
    rin = paint(INK, .38 * a, stroke=2); rin.setPathEffect(skia.DashPathEffect.Make([14, 10], 0)); _jcircle(c, cx, cy, R * .55, rin, 12, 2.6 * k)
    for i in range(72):
        ang = 2 * math.pi * i / 72; _jline(c, (cx + (R - 20 * k) * math.cos(ang), cy + (R - 20 * k) * math.sin(ang)), (cx + R * math.cos(ang), cy + R * math.sin(ang)), paint(INK, .5 * a, stroke=1.6), 100 + i, .7, 2)
    pr = skia.Rect.MakeLTRB(cx - 14 * k, cy - R * .22, cx + 14 * k, cy + R * .22)
    c.drawRect(pr, paint((218, 194, 140), .92 * a)); c.drawRect(pr, paint(INK, .85 * a, stroke=2))
    for yy in (-.2, .2): c.drawLine(cx - 24 * k, cy + R * yy, cx + 24 * k, cy + R * yy, paint(INK, .8 * a, stroke=2))
    if s.get("batter", True):
        bx, by = cx + 22 * k, cy + R * .2 + 16 * k; text(c, "batter", bx, by + 8 * k, 24 * max(k, .62) + 4, "serifI", INK, .75 * a)
    pos = E.POS
    for i, f in enumerate(figures):
        st = D * (f.get("at", .12 + .5 * i / max(1, len(figures))))
        q = eback(prog(t, st, st + .35))
        if q <= 0: continue
        xy = f.get("xy") or pos[f["p"]]; x, y = cx + xy[0] * R, cy + xy[1] * R; hot = f.get("hl", False)
        sc = (1.25 if hot else 1.0) * max(k, .6) * q
        if hot:
            ring = paint(RED, .8 * q, stroke=3); ring.setPathEffect(skia.DashPathEffect.Make([9, 7], 0)); c.drawCircle(x, y - 2, 46 * max(k, .6), ring)
        _fig(c, x, y, sc, RED if hot else INK, 1.0)
        lab = f.get("fig")
        if lab and show_labels:
            side = f.get("side", 1 if xy[0] >= 0 else -1)
            text(c, "Fig. " + str(lab), x + side * 40 * max(k, .62) - (0 if side > 0 else twidth("Fig. " + str(lab), 30 * max(k, .62) + 2, "serifI")), y + (f.get("dy", -34)) * max(k, .62), 30 * max(k, .62) + 2, "serifI", RED if hot else INK, q)
        if f.get("label") and not small:
            side = f.get("side", 1 if xy[0] >= 0 else -1)
            text(c, f["label"], x + side * 40 * max(k, .62) - (0 if side > 0 else twidth(f["label"], 28 * max(k, .62) + 2, "serifBI")), y + f.get("ldy", 26) * max(k, .62), 28 * max(k, .62) + 2, "serifBI", RED if hot else INK, q)
    for pth in s.get("paths", []):                                                  # dashed ball paths with an arrow head
        st = D * pth.get("at", .55); q = eio(prog(t, st, st + pth.get("dur", .9)))
        if q <= 0: continue
        p0 = pth.get("from_xy") or pos[pth["from"]]; p2 = pth.get("to_xy") or pos[pth["to"]]
        P0 = (cx + p0[0] * R, cy + p0[1] * R); P2 = (cx + p2[0] * R, cy + p2[1] * R); bend = pth.get("bend", .22)
        P1 = ((P0[0] + P2[0]) / 2 - (P2[1] - P0[1]) * bend, (P0[1] + P2[1]) / 2 + (P2[0] - P0[0]) * bend)
        bz = lambda f: ((1 - f) ** 2 * P0[0] + 2 * (1 - f) * f * P1[0] + f * f * P2[0], (1 - f) ** 2 * P0[1] + 2 * (1 - f) * f * P1[1] + f * f * P2[1])
        pa = skia.Path(); pa.moveTo(*P0)
        for j in range(1, 41): pa.lineTo(*bz(q * j / 40))
        pp = paint(RED, .92, stroke=4.4); pp.setPathEffect(skia.DashPathEffect.Make([16, 11], 0)); pp.setStrokeCap(skia.Paint.kRound_Cap); c.drawPath(pa, pp)
        e, e2 = bz(q), bz(max(0, q - .04)); an = math.atan2(e[1] - e2[1], e[0] - e2[0])
        ah = skia.Path(); ah.moveTo(e[0] + 20 * math.cos(an), e[1] + 20 * math.sin(an)); ah.lineTo(e[0] + 4 * math.cos(an + 2.4), e[1] + 4 * math.sin(an + 2.4)); ah.lineTo(e[0] + 4 * math.cos(an - 2.4), e[1] + 4 * math.sin(an - 2.4)); ah.close()
        c.drawPath(ah, paint(RED, .95))
        if pth.get("label"): text(c, pth["label"], P1[0] + pth.get("lx", 0), P1[1] + pth.get("ly", 0), 30, "serifI", RED, q)


def stamp(c, x, y, lines, t, t0, ang=-12, r=96, col=RED):
    q = eback(prog(t, t0, t0 + .3))
    if q <= 0: return
    c.save(); c.translate(x, y); c.rotate(ang); c.scale(q, q)
    c.drawCircle(0, 0, r, paint(col, .92, stroke=5)); c.drawCircle(0, 0, r - 14, paint(col, .9, stroke=2))
    n = len(lines); z0 = r * .36 if n <= 2 else r * .3
    for i, ln in enumerate(lines): text(c, ln, 0, (i - (n - 1) / 2) * z0 * 1.18 + z0 * .34, E.fit(ln, r * 1.5, z0 * 1.35, "bebas"), "bebas", col, .95, "c", track=2)
    c.restore()


def _header(c, g, s, t, D, x0, y0, x1, y1, ax="c"):
    """PLATE n / title / subtitle. Returns the y below the header."""
    a = eo(prog(t, 0, .4)); short = g.fmt == "short"; cxm = (x0 + x1) / 2 if ax == "c" else x0 + 30
    al = "c" if ax == "c" else "l"
    if s.get("plate"): text(c, "PLATE " + str(s["plate"]) if not str(s["plate"]).startswith("PLATE") else str(s["plate"]), cxm, y0 + (84 if short else 78), 32 if short else 38, "serifI", INK, .8 * a, al, track=10)
    ty = y0 + (200 if short else 205)
    if s.get("title"):
        z = E.fit(s["title"], (x1 - x0 - 60) if ax == "c" else 780, 96 if short else 112, "serifBI"); text(c, s["title"], cxm, ty, z, "serifBI", INK, a, al)
    if s.get("sub"):
        zs = 38 if short else 46; lh = 46 if short else 58
        lines = E.wrap(s["sub"], (x1 - x0 - 120) if ax == "c" else 760, zs, "serifI")
        for i, ln in enumerate(lines[:3]): text(c, ln, cxm, ty + 68 + i * lh, zs, "serifI", INK, .85 * a, al)
        return ty + 68 + min(3, len(lines)) * lh
    return ty + 30


# ---------------------------------------------------------------- scenes
def sc_plate(c, g, t, D, s):
    bg(c, t); x0, y0, x1, y1 = _frame(c, g, eo(prog(t, 0, .3))); short = g.fmt == "short"
    figs = s.get("figures", [])
    if short:
        yb = _header(c, g, s, t, D, x0, y0, x1, y1)
        R = 340; cx, cy = g.W / 2, yb + 90 + R
        field(c, cx, cy, R, figs, t, D, s)
        ly = cy + R + 78; nrows = len([f for f in figs if f.get("fig") is not None]) if s.get("legend", True) else 0
        for i, f in enumerate([f for f in figs if f.get("fig") is not None] if s.get("legend", True) else []):
            q = eo(prog(t, D * (.3 + .4 * i / max(1, len(figs))), D * (.3 + .4 * i / max(1, len(figs))) + .4))
            text(c, f"Fig. {f['fig']}  {f.get('name') or f.get('label') or f['p'].title()}", x0 + 56, ly + i * 42, 31, "serifI", RED if f.get("hl") else INK, q)
        if s.get("note"):
            nl = s["note"] if isinstance(s["note"], list) else [s["note"]]
            for i, ln in enumerate(nl): text(c, ln, g.W / 2, ly + nrows * 42 + 30 + i * 44, 34, "serifBI", RED, eo(prog(t, D * .5, D * .5 + .5)), "c")
        if s.get("stamp"): stamp(c, x1 - 150, y1 - 120, s["stamp"], t, D * s.get("stamp_at", .6))
    else:
        yb = _header(c, g, s, t, D, x0, y0, x1, y1, ax="l")
        R = 380; cx, cy = x1 - 470, (y0 + y1) / 2 + 10
        field(c, cx, cy, R, figs, t, D, s)
        ly = yb + 80
        for i, f in enumerate(figs if s.get("legend", True) else []):
            if f.get("fig") is None: continue
            q = eo(prog(t, D * (.3 + .4 * i / max(1, len(figs))), D * (.3 + .4 * i / max(1, len(figs))) + .4))
            text(c, f"Fig. {f['fig']}  {f.get('name') or f.get('label') or f['p'].title()}", x0 + 30, ly + i * 56, 40, "serifI", RED if f.get("hl") else INK, q)
        if s.get("note"):
            nl = s["note"] if isinstance(s["note"], list) else [s["note"]]
            for i, ln in enumerate(nl): text(c, ln, x0 + 30, y1 - 80 - (len(nl) - 1 - i) * 58, 44, "serifBI", RED, eo(prog(t, D * .5, D * .5 + .5)))
        if s.get("stamp"): stamp(c, x0 + 680, y1 - 190, s["stamp"], t, D * s.get("stamp_at", .6), r=110)


def sc_plate_page(c, g, t, D, s):
    bg(c, t); x0, y0, x1, y1 = _frame(c, g, eo(prog(t, 0, .3))); short = g.fmt == "short"
    a = eo(prog(t, 0, .4))
    text(c, s.get("kicker", ""), x0 + 40, y0 + (84 if short else 80), 30 if short else 38, "mono", INK, .8 * a, track=6)
    z = E.fit(s.get("title", ""), x1 - x0 - 80, 92 if short else 118, "serifBI"); text(c, s.get("title", ""), x0 + 40, y0 + (190 if short else 205), z, "serifBI", INK, a)
    bw = (x1 - x0 - 110) if short else 1000; size = 42 if short else 52; y = y0 + (270 if short else 300)
    for i, ln in enumerate(E.wrap(s.get("body", ""), bw, size, "serifI")):
        q = eo(prog(t, .25 + .08 * i, .65 + .08 * i)); text(c, ln, x0 + 40, y + i * (size + 14), size, "serifI", INK, .95 * q)
    n = len(E.wrap(s.get("body", ""), bw, size, "serifI")); yn = y + n * (size + 14) + 24
    if s.get("margin"):
        mz = 36 if short else 44
        for i, ln in enumerate(E.wrap(s["margin"], bw, mz, "serifBI")): text(c, ln, x0 + 40, yn + i * (mz + 12), mz, "serifBI", RED, eo(prog(t, D * .5, D * .5 + .5)))
        yn += len(E.wrap(s["margin"], bw, mz, "serifBI")) * (mz + 12) + 20
    if s.get("figures"):
        R = 190 if short else 290; cx, cy = (g.W / 2, min(y1 - R - 60, max(yn + R + 20, y0 + 900))) if short else (x1 - 470, (y0 + y1) / 2 + 40)
        field(c, cx, cy, R, s["figures"], t, D, dict(s, batter=False), small=True)
    if s.get("stamp"): stamp(c, (x1 - 170) if short else (x1 - 1010), (y1 - 200) if short else (y1 - 190), s["stamp"], t, D * s.get("stamp_at", .55), ang=s.get("stamp_angle", 10), r=96 if short else 120)


def sc_plate_list(c, g, t, D, s):
    bg(c, t); x0, y0, x1, y1 = _frame(c, g, eo(prog(t, 0, .3))); short = g.fmt == "short"
    yb = _header(c, g, s, t, D, x0, y0, x1, y1)
    rows = s.get("rows", []); y = yb + (96 if short else 90); lw = x1 - x0 - 100
    avail = (y1 - 110) - y; rh = min(230 if short else 250, avail / max(1, len(rows))); size = 50 if short else 56
    c.drawLine(x0 + 50, y - 50, x1 - 50, y - 50, paint(INK, .8, stroke=2))
    for i, r in enumerate(rows):
        st = D * (.1 + .6 * i / max(1, len(rows))); q = eo(prog(t, st, st + .4)); yy = y + i * rh
        if q <= 0: continue
        yr, what = (r[0], r[1]); detail = r[2] if len(r) > 2 else ""
        text(c, str(yr), x0 + 50, yy, size - 4, "monoSB", RED, q)
        z = E.fit(what, lw - 230, size, "serifBI"); text(c, what, x0 + 50 + 210, yy, z, "serifBI", INK, q)
        if detail:
            for j, ln in enumerate(E.wrap(detail, lw - 230, size - 14, "serifI")[:3]): text(c, ln, x0 + 50 + 210, yy + 48 + j * 42, size - 14, "serifI", INK, .88 * q)
        c.drawLine(x0 + 50, yy + rh - 62, x1 - 50, yy + rh - 62, paint(INK, .25 * q, stroke=1.4))
    if s.get("stamp"): stamp(c, x1 - 150, y1 - 140, s["stamp"], t, D * s.get("stamp_at", .7))


def sfx(s, D, T0):
    ev = [[T0 + .05, "whoosh", .5]]
    if s.get("stamp"): ev.append([T0 + D * s.get("stamp_at", .6) + .1, "stamp", .6])
    for i, f in enumerate(s.get("figures", [])): ev.append([T0 + D * f.get("at", .12 + .5 * i / max(1, len(s["figures"]))) + .1, "tick", .6])
    return ev
