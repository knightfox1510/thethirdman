"""Scenes for placement visuals (lab look): 'wagon' (a wagon wheel built from shot zones read from the ball-by-ball text) and 'pitchzones' (where deliveries landed, line by length, two panels).
Zones are approximate (our reading of the commentary text), so scenes say ILLUSTRATIVE. Off side is drawn on the right for every batter. Installed by looks.install."""
import math
import skia
import gfx
from gfx import text, rrect, paint, prog, eo, eback, clamp, twidth
E = None; LK = None
AMB = (226, 150, 24); GRN = (40, 150, 90); GREY = (170, 170, 168)


def _L(g):
    l = dict(LK.L(g))
    if g.fmt == "short": l["bot"] = 1620
    return l


def _hd(s):
    """The lab header reads title/sub; scenes here carry head {t, sub} like the chart scenes do."""
    h = s.get("head")
    return dict(s, title=h["t"], sub=h.get("sub", "")) if (isinstance(h, dict) and not s.get("title")) else s


def _jit(i): return ((i * 37) % 11 - 5) * 1.3                                  # deterministic angle jitter (degrees), so overlapping rays fan out


def sc_wagon(c, g, t, D, s):
    LK.header(c, g, t, D, _hd(s)); l = _L(g); sh = g.fmt == "short"; W = g.W
    R = 400 if sh else 285; cx = W / 2 if sh else 480; cy = l["top"] + (80 if sh else 60) + R; a = eo(prog(t, .05, .5))
    c.drawCircle(cx, cy, R + 10, paint((0, 0, 0), .10 * a, blur=22))
    c.drawCircle(cx, cy, R, paint((226, 233, 214), a))
    c.drawCircle(cx, cy, R, paint(gfx.INK, a, stroke=4)); ip = paint(gfx.INK, .35 * a, stroke=2); c.drawCircle(cx, cy, R * .5, ip)
    fl = bool(s.get("batter_top"))                                  # batter at the top end of the pitch, bowler at the bottom: straight is DOWN the page
    if fl:
        sl = 150 * (R / 400); rrect(c, cx - 15, cy - 8, 30, sl, 4, (214, 196, 150), a)
        for yy in (cy - 8, cy - 8 + sl - 9):
            for k in range(-1, 2): c.drawRect(skia.Rect.MakeXYWH(cx + k * 8 - 1.5, yy, 3, 9), paint(gfx.INK, a))
        text(c, "BATTER", cx + 30, cy - 12, 17, "monoSB", gfx.MUTED, a, "l", track=1); text(c, "BOWLER", cx + 30, cy + sl + 6, 17, "monoSB", gfx.MUTED, a, "l", track=1)
        text(c, "OFF SIDE", cx + R - 10, cy + R + 44, 22, "monoSB", gfx.MUTED, a, "r", track=2); text(c, "LEG SIDE", cx - R + 10, cy + R + 44, 22, "monoSB", gfx.MUTED, a, "l", track=2)
        text(c, "STRAIGHT", cx, cy + R + 44, 22, "monoSB", gfx.MUTED, a, "c", track=2); text(c, "BEHIND THE WICKET", cx, cy - R - 16, 20, "monoSB", gfx.MUTED, a, "c", track=2)
    else:
        rrect(c, cx - 15, cy - 70 * (R / 400), 30, 140 * (R / 400), 4, (214, 196, 150), a)
        for k in range(-1, 2): c.drawRect(skia.Rect.MakeXYWH(cx + k * 8 - 1.5, cy - 72 * (R / 400), 3, 9), paint(gfx.INK, a))
        text(c, "OFF SIDE", cx + R - 10, cy + R + 44, 22, "monoSB", gfx.MUTED, a, "r", track=2); text(c, "LEG SIDE", cx - R + 10, cy + R + 44, 22, "monoSB", gfx.MUTED, a, "l", track=2)
        text(c, "STRAIGHT", cx, cy - R - 16, 20, "monoSB", gfx.MUTED, a, "c", track=2)
    shots = s["pts"]; n = len(shots); shown = eo(prog(t, .2, max(.8, D * .75))) * n
    for i, (ang, runs, kind) in enumerate(shots):
        q = clamp(shown - i)
        if q <= 0: continue
        th = math.radians(ang + _jit(i)); ln = R * {1: .30, 2: .52, 3: .74}.get(runs, 1.0) * (1.0 if kind != "s" else 1.04) * (.35 + .65 * q) if kind in ("f", "s") or runs in (1, 2, 3) else R * .4 * q
        x2 = cx + math.sin(th) * ln; y2 = cy + (1 if s.get("batter_top") else -1) * math.cos(th) * ln
        col = LK.RED if kind == "s" else (AMB if kind == "f" else gfx.INK)
        p = paint(col, (.95 if kind in ("f", "s") else .45) * q); p.setStrokeWidth(5 if kind == "s" else (4 if kind == "f" else 2)); c.drawLine(cx, cy, x2, y2, p)
        if kind in ("f", "s"): c.drawCircle(x2, y2, 9 if kind == "s" else 7, paint(col, q))
    ky = cy + R + (100 if sh else 90)
    for j, (lab, col) in enumerate((("SIX", LK.RED), ("FOUR", AMB), ("1-3 RUNS", gfx.INK))):
        kx = (l["x0"] if sh else cx - R) + j * 190; c.drawCircle(kx + 10, ky - 8, 9, paint(col, a)); text(c, lab, kx + 28, ky, 22, "monoSB", gfx.INK, a, track=1)
    if s.get("photo"):
        ph = s["photo"]; qa = eo(prog(t, .1, .6)); pr = 105 if sh else 130; px, py = (l["x1"] - pr, l["top"] - 30) if sh else (1500, 470)
        c.save(); c.clipPath(skia.Path().addCircle(px, py, pr)); im = _pimg(ph["img"]); cr = ph["crop"]
        c.drawImageRect(im, skia.Rect.MakeLTRB(*cr), skia.Rect.MakeXYWH(px - pr, py - pr, 2 * pr, 2 * pr), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear), paint((255, 255, 255), qa)); c.restore()
        c.drawCircle(px, py, pr, paint(gfx.INK, qa, stroke=5))
    chips = s.get("chips", [])
    for j, (v, lb) in enumerate(chips):
        if sh:
            cw = (920 - 18 * (len(chips) - 1)) / max(1, len(chips)); cx_ = l["x0"] + j * (cw + 18); cy_ = ky + 70; chh = 150
        else:
            cw, chh = 330, 130; cx_ = 940 + (j % 2) * (cw + 20); cy_ = 640 + (j // 2) * (chh + 20)
        qq = eo(prog(t, D * .4 + .1 * j, D * .4 + .6 + .1 * j))
        rrect(c, cx_, cy_, cw, chh, 14, (255, 255, 255), qq, stroke=3, scol=LK.RED if j else gfx.INK, sa=qq); text(c, v, cx_ + cw / 2, cy_ + chh * .55, 64 if sh else 56, "interB", LK.RED if j else gfx.INK, qq, "c"); text(c, lb, cx_ + cw / 2, cy_ + chh - 16, E.fit(lb, cw - 24, 21, "monoSB", 1), "monoSB", gfx.MUTED, qq, "c", track=1)
    if s.get("footnote"):
        yf = (ky + 70 + 200) if sh else 1056
        for j, ln_ in enumerate(E.wrap(s["footnote"], l["x1"] - l["x0"], 17, "mono")[:2]): text(c, ln_, l["x0"], yf + 24 * j, 17, "mono", gfx.MUTED, eo(prog(t, D * .5, D * .5 + .6)))


_IMG = {}
def _pimg(path):
    if path not in _IMG: _IMG[path] = skia.Image.open(path)
    return _IMG[path]


LINES = [("LEG", "leg"), ("MIDDLE", "middle"), ("OFF", "off"), ("OUTSIDE OFF", "outside_off")]
LENS = [("FULL", "full"), ("GOOD", "good"), ("SHORT OF A LENGTH", "short_of_length"), ("SHORT", "short")]


def sc_pitchzones(c, g, t, D, s):
    """Two pitch panels (line by length). Cell shade = share of the panel's deliveries; the number is that share in %."""
    LK.header(c, g, t, D, _hd(s)); l = _L(g); sh = g.fmt == "short"; a = eo(prog(t, .05, .5))
    panels = s["panels"]; npn = len(panels); gap = 30; pw = ((l["x1"] - l["x0"]) - gap * (npn - 1)) / npn; top = l["top"] + 70; ch = 150 if sh else 120
    for k, pn in enumerate(panels):
        x0 = l["x0"] + k * (pw + gap); qk = eo(prog(t, .1 + .25 * k, .7 + .25 * k)); tot = pn["n"]
        rrect(c, x0, l["top"] - 10, pw, 54, 10, gfx.INK if k == 0 else LK.RED, qk); text(c, pn["title"], x0 + pw / 2, l["top"] + 28, 26, "interB", (255, 255, 255), qk, "c")
        lw = pw / len(LINES)
        rrect(c, x0, top, pw, ch * len(LENS), 8, (214, 196, 150), .55 * qk)
        for j, (lab, _) in enumerate(LINES): text(c, lab.replace("OUTSIDE OFF", "OUT. OFF"), x0 + j * lw + lw / 2, top + ch * len(LENS) + 30, 17, "monoSB", gfx.MUTED, qk, "c")
        for i, (ln_, lk) in enumerate(LENS):
            if k == 0: text(c, ln_.replace("SHORT OF A LENGTH", "BACK OF LGTH"), x0 - 6, top + i * ch + 26, 13, "monoSB", gfx.MUTED, qk, "l")
            for j, (_, line_k) in enumerate(LINES):
                v = pn["cells"].get(f"{line_k}|{lk}", 0); share = 100.0 * v / tot; qq = clamp((qk * 1.2 - .1) + 0)
                shade = min(.85, share / 16.0)
                x = x0 + j * lw; y = top + i * ch
                c.drawRect(skia.Rect.MakeXYWH(x + 2, y + 2, lw - 4, ch - 4), paint(LK.RED if k else gfx.INK, shade * .9 * qq))
                if share >= 1: text(c, f"{round(share)}", x + lw / 2, y + ch / 2 + 14, 44 if sh else 34, "interB", (255, 255, 255) if shade > .38 else gfx.INK, qq, "c")
        for j in range(len(LINES) + 1): c.drawLine(x0 + j * lw, top, x0 + j * lw, top + ch * len(LENS), paint(gfx.INK, .15 * qk))
        for ln_ in pn.get("stats", []): pass
        yy = top + ch * len(LENS) + 78
        for j, (v, lb) in enumerate(pn.get("stats", [])):
            text(c, v, x0 + 6, yy + j * 56, 40, "interB", LK.RED if k else gfx.INK, eo(prog(t, D * .35 + .1 * j, D * .35 + .6 + .1 * j))); text(c, lb, x0 + 6 + twidth(v, 40, "interB", 0) + 14, yy + j * 56 - 4, 20, "monoSB", gfx.MUTED, eo(prog(t, D * .35 + .1 * j, D * .35 + .6 + .1 * j)))
    if s.get("footnote"):
        for j, ln_ in enumerate(E.wrap(s["footnote"], l["x1"] - l["x0"], 17, "mono")[:3]): text(c, ln_, l["x0"], l["bot"] - 70 + j * 24, 17, "mono", gfx.MUTED, eo(prog(t, D * .5, D * .5 + .6)))


LN_X = {"leg": (-.46, -.10), "middle": (-.10, .10), "off": (.10, .38), "outside_off": (.38, 1.0), "wide": (1.0, 1.4)}      # metres from middle stump, off side positive
LN_Y = {"yorker": (1.0, 2.0), "full": (2.0, 4.0), "good": (4.0, 6.0), "short_of_length": (6.0, 8.0), "short": (8.0, 10.0)}            # metres from the batter's stumps


def sc_pitchtop(c, g, t, D, s):
    """The pitch from above: grass panels with the 22-yard strip, creases and stumps; each delivery is a dot where its line and length put it (jittered inside its zone). Vertical: panels side by side; long: panels stacked, the pitch lying along the page."""
    if g.fmt != "short": return sc_pitchtop_long(c, g, t, D, s)
    return _sc_pitchtop_v(c, g, t, D, s)


def sc_pitchtop_long(c, g, t, D, s):
    LK.header(c, g, t, D, _hd(s)); l = _L(g); a = eo(prog(t, .05, .5)); panels = s["panels"]; npn = len(panels); gap = 18
    top = l["top"] - 20; H = (1010 - top - gap * (npn - 1)) / npn; m = min(H / 3.9, 84.0); x0 = l["x0"]; pw = l["x1"] - l["x0"]
    for k, pn in enumerate(panels):
        y0 = top + k * (H + gap); qk = eo(prog(t, .1 + .2 * k, .7 + .2 * k)); cy = y0 + H / 2; sx = x0 + 70                 # sx = the batter's stumps (left)
        c.save(); c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x0, y0, pw, H), 14, 14), doAntiAlias=True)
        c.drawRect(skia.Rect.MakeXYWH(x0, y0, pw, H), paint((86, 138, 78), qk))
        for i in range(int(pw // 56) + 1):
            if i % 2 == 0: c.drawRect(skia.Rect.MakeXYWH(x0 + i * 56, y0, 56, H), paint((104, 156, 92), .55 * qk))
        sw = 3.05 * m; c.drawRect(skia.Rect.MakeXYWH(sx - 1.3 * m, cy - sw / 2, 12.2 * m, sw), paint((205, 184, 138), qk)); c.drawRect(skia.Rect.MakeXYWH(sx + 1.0 * m, cy - sw * .32, 8.2 * m, sw * .64), paint((190, 168, 120), .45 * qk))
        wp = paint((250, 250, 245), qk); wp.setStrokeWidth(3)
        c.drawLine(sx + 1.22 * m, cy - 2.4 * m if 2.4 * m < H / 2 else y0 + 4, sx + 1.22 * m, cy + 2.4 * m if 2.4 * m < H / 2 else y0 + H - 4, wp)
        c.drawLine(sx, cy - 1.32 * m, sx, cy + 1.32 * m, wp); c.drawLine(sx, cy - 1.32 * m, sx + 1.22 * m, cy - 1.32 * m, wp); c.drawLine(sx, cy + 1.32 * m, sx + 1.22 * m, cy + 1.32 * m, wp)
        for j in (-1, 0, 1): c.drawRect(skia.Rect.MakeXYWH(sx - 12, cy + j * 0.11 * m - 2.5, 14, 5), paint((245, 232, 200), qk))
        for lo, lab in ((2.0, "FULL"), (4.0, "GOOD"), (6.0, "BACK OF A LENGTH"), (8.0, "SHORT")):
            dl = paint((255, 255, 255), .30 * qk); dl.setStrokeWidth(2); c.drawLine(sx + lo * m, cy - sw / 2, sx + lo * m, cy + sw / 2, dl)
            if k == 0: text(c, lab, sx + lo * m + 6, cy - sw / 2 + 18, 13, "monoSB", (240, 244, 236), qk, "l", track=1)
        n = len(pn["balls"]); shown = qk * eo(prog(t, .3, max(.9, D * .8))) * n
        for i, (ln_, le_, out) in enumerate(pn["balls"]):
            q = clamp(shown - i)
            if q <= 0: continue
            xa, xb = LN_X[ln_]; ya, yb = LN_Y[le_]; fx = ((i * 53) % 17) / 17.0; fy = ((i * 29) % 13) / 13.0
            bx = sx + (ya + (yb - ya) * fy) * m; by = cy - (xa + (xb - xa) * fx) * m
            col = {"d": (250, 250, 245), "r": AMB, "b": LK.RED, "w": (20, 20, 22)}[out]; r = 6 if out in ("d", "r") else 8
            c.drawCircle(bx, by, r, paint(col, (.55 if out == "d" else .95) * q))
            if out == "w": c.drawCircle(bx, by, 12, paint(LK.RED, q, stroke=4))
        c.restore()
        px = x0 + 12.4 * m + 80
        rrect(c, px, y0 + 16, 340, 46, 10, gfx.INK if k == 0 else LK.RED, qk); text(c, pn["title"], px + 170, y0 + 48, 24, "interB", (255, 255, 255), qk, "c")
        for j, (v, lb) in enumerate(pn.get("stats", [])):
            qs = eo(prog(t, D * .35 + .1 * j, D * .35 + .6 + .1 * j)); text(c, v, px, y0 + 120 + j * 54, 44, "interB", (255, 255, 255), qs); text(c, lb, px + twidth(v, 44, "interB", 0) + 14, y0 + 112 + j * 54, 20, "monoSB", (240, 244, 236), qs, track=1)
    ky = 1030
    for j, (lab, col) in enumerate((("DOT BALL", (150, 150, 145)), ("RUNS", AMB), ("BOUNDARY", LK.RED), ("WICKET", (20, 20, 22)))):
        kx = l["x0"] + j * 200; c.drawCircle(kx + 9, ky - 7, 8, paint(col, a)); text(c, lab, kx + 26, ky, 19, "monoSB", gfx.INK, a, track=1)
    if s.get("footnote"): text(c, s["footnote"], l["x0"] + 860, ky, E.fit(s["footnote"], 780, 16, "mono"), "mono", gfx.MUTED, eo(prog(t, D * .5, D * .5 + .6)))


def _sc_pitchtop_v(c, g, t, D, s):
    """The pitch from above: two grass panels with the 22-yard strip, creases and stumps; each delivery is a dot where its line and length put it (jittered inside its zone)."""
    LK.header(c, g, t, D, _hd(s)); l = _L(g); a = eo(prog(t, .05, .5)); panels = s["panels"]; npn = len(panels); gap = 24
    pw = ((l["x1"] - l["x0"]) - gap * (npn - 1)) / npn; m = 62.0; top = l["top"] + 70; gh = 10.9 * m + 50
    for k, pn in enumerate(panels):
        x0 = l["x0"] + k * (pw + gap); cx = x0 + pw / 2; qk = eo(prog(t, .1 + .25 * k, .7 + .25 * k)); y0 = top + 36                 # y0 = the batter's stumps
        rrect(c, x0, l["top"] - 10, pw, 54, 10, gfx.INK if k == 0 else LK.RED, qk); text(c, pn["title"], x0 + pw / 2, l["top"] + 28, 26, "interB", (255, 255, 255), qk, "c")
        c.save(); c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x0, top, pw, gh), 14, 14), doAntiAlias=True)
        c.drawRect(skia.Rect.MakeXYWH(x0, top, pw, gh), paint((86, 138, 78), qk))
        for i in range(int(gh // 56) + 1):                                                                                  # mown stripes
            if i % 2 == 0: c.drawRect(skia.Rect.MakeXYWH(x0, top + i * 56, pw, 56), paint((104, 156, 92), .55 * qk))
        sw = 3.05 * m; px = cx - sw / 2; c.drawRect(skia.Rect.MakeXYWH(px, y0 - 1.3 * m, sw, 12.2 * m), paint((205, 184, 138), qk))          # the strip
        c.drawRect(skia.Rect.MakeXYWH(px + sw * .18, y0 + 1.0 * m, sw * .64, 8.2 * m), paint((190, 168, 120), .45 * qk))                       # worn middle
        wp = paint((250, 250, 245), qk); wp.setStrokeWidth(3)
        c.drawLine(cx - 2.4 * m, y0 + 1.22 * m, cx + 2.4 * m, y0 + 1.22 * m, wp)                                           # popping crease
        c.drawLine(cx - 1.32 * m, y0, cx + 1.32 * m, y0, wp); c.drawLine(cx - 1.32 * m, y0, cx - 1.32 * m, y0 + 1.22 * m, wp); c.drawLine(cx + 1.32 * m, y0, cx + 1.32 * m, y0 + 1.22 * m, wp)
        for j in (-1, 0, 1): c.drawRect(skia.Rect.MakeXYWH(cx + j * 0.11 * m - 2.5, y0 - 12, 5, 14), paint((245, 232, 200), qk))   # the stumps
        for lo, lab in ((2.0, "FULL"), (4.0, "GOOD"), (6.0, "BACK OF A LENGTH"), (8.0, "SHORT")):
            dl = paint((255, 255, 255), .30 * qk); dl.setStrokeWidth(2); c.drawLine(px, y0 + lo * m, px + sw, y0 + lo * m, dl)
            if k == 0: text(c, lab.replace("BACK OF A LENGTH", "BACK OF LGTH"), x0 + 8, y0 + lo * m - 8, 13, "monoSB", (240, 244, 236), qk, "l", track=1)
        n = len(pn["balls"]); shown = qk * eo(prog(t, .3, max(.9, D * .8))) * n
        for i, (ln_, le_, out) in enumerate(pn["balls"]):
            q = clamp(shown - i)
            if q <= 0: continue
            xa, xb = LN_X[ln_]; ya, yb = LN_Y[le_]; fx = ((i * 53) % 17) / 17.0; fy = ((i * 29) % 13) / 13.0
            bx = cx + (xa + (xb - xa) * fx) * m * (1 if True else 1); by = y0 + (ya + (yb - ya) * fy) * m
            col = {"d": (250, 250, 245), "r": AMB, "b": LK.RED, "w": (20, 20, 22)}[out]; r = 7 if out in ("d", "r") else 9
            c.drawCircle(bx, by, r, paint(col, (.55 if out == "d" else .95) * q))
            if out == "w": c.drawCircle(bx, by, 13, paint(LK.RED, q, stroke=4))
        c.restore()
        yy = top + gh + 56
        for j, (v, lb) in enumerate(pn.get("stats", [])):
            qs = eo(prog(t, D * .35 + .1 * j, D * .35 + .6 + .1 * j)); text(c, v, x0 + 4, yy + j * 52, 38, "interB", LK.RED if k else gfx.INK, qs); text(c, lb, x0 + 4 + twidth(v, 38, "interB", 0) + 12, yy + j * 52 - 4, E.fit(lb, pw - 120, 19, "monoSB", 1), "monoSB", gfx.MUTED, qs, track=1)
    ky = top + gh + 56 + 52 * 2 + 24
    for j, (lab, col) in enumerate((("DOT BALL", (150, 150, 145)), ("RUNS", AMB), ("BOUNDARY", LK.RED), ("WICKET", (20, 20, 22)))):
        kx = l["x0"] + j * 225; c.drawCircle(kx + 9, ky - 7, 8, paint(col, a)); text(c, lab, kx + 26, ky, 19, "monoSB", gfx.INK, a, track=1)
    if s.get("footnote"):
        for j, ln_ in enumerate(E.wrap(s["footnote"], l["x1"] - l["x0"], 16, "mono")[:2]): text(c, ln_, l["x0"], ky + 36 + 22 * j, 16, "mono", gfx.MUTED, eo(prog(t, D * .5, D * .5 + .6)))


_CLIPF = {}


def _clip_frames(path, fps=10):
    """Frames of a supplied clip as small jpgs (out/clips/<name>/f0001.jpg ...), extracted once."""
    import os, subprocess, glob, hashlib
    key = hashlib.md5(path.encode()).hexdigest()[:8]; d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "clips", key)
    if not glob.glob(d + "/f*.jpg"):
        os.makedirs(d, exist_ok=True); subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", path, "-vf", f"fps={fps},scale=540:-2", "-q:v", "3", d + "/f%04d.jpg"], check=True)
    return sorted(glob.glob(d + "/f*.jpg"))


def sc_clip(c, g, t, D, s):
    """A supplied portrait clip (owner-provided) in a phone-style frame, with a kicker, a title and stat chips beside it (long) or below it (vertical)."""
    sh = g.fmt == "short"; l = _L(g); fr = _clip_frames(s["clip"], s.get("fps", 10)); fps = s.get("fps", 10)
    i = min(len(fr) - 1, int(max(0.0, t - s.get("clip_at", 0.3)) * fps * s.get("speed", 1.0)))
    LK.header(c, g, t, D, dict(s, title=s.get("title", ""), sub=s.get("sub", ""), kicker=s.get("kicker", "")))
    key = fr[i]
    if key not in _CLIPF: _CLIPF[key] = skia.Image.open(key)
    im = _CLIPF[key]; a = eo(prog(t, .05, .5))
    if sh: fw, fh = 440, 782; fx, fy = (g.W - fw) / 2, l["top"] + 20
    else: fw, fh = 450, 800; fx, fy = 1260, 230
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(fx - 6, fy - 6 + 14, fw + 12, fh + 12), 26, 26), paint((0, 0, 0), .25 * a, blur=22))
    c.save(); c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(fx, fy, fw, fh), 22, 22), doAntiAlias=True)
    c.drawImageRect(im, skia.Rect.MakeWH(im.width(), im.height()), skia.Rect.MakeXYWH(fx, fy, fw, fh), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear), paint((255, 255, 255), a)); c.restore()
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(fx, fy, fw, fh), 22, 22), paint(gfx.INK, a, stroke=5))
    chips = s.get("chips", [])
    for j, (v, lb) in enumerate(chips):
        qq = eo(prog(t, D * .2 + .15 * j, D * .2 + .7 + .15 * j))
        if sh: cw = (920 - 18 * (len(chips) - 1)) / max(1, len(chips)); cx_ = l["x0"] + j * (cw + 18); cy_ = fy + fh + 40; chh = 130
        else: cw, chh = 620, 130; cx_ = 140; cy_ = 340 + j * (chh + 24)
        rrect(c, cx_, cy_, cw, chh, 14, (255, 255, 255), qq, stroke=3, scol=LK.RED if j else gfx.INK, sa=qq); text(c, v, cx_ + cw / 2, cy_ + chh * .58, 64, "interB", LK.RED if j else gfx.INK, qq, "c"); text(c, lb, cx_ + cw / 2, cy_ + chh - 14, E.fit(lb, cw - 24, 21, "monoSB", 1), "monoSB", gfx.MUTED, qq, "c", track=1)
    if s.get("caption") and not sh:
        for j, ln_ in enumerate(E.wrap(s["caption"], 980, 34, "interB")[:3]): text(c, ln_, 140, 340 + len(chips) * 154 + 50 + 44 * j, 34, "interB", gfx.INK, eo(prog(t, D * .5, D * .5 + .7)))


def install(engine, looks):
    global E, LK
    E = engine; LK = looks
    E.SCENES.update({"wagon": sc_wagon, "pitchzones": sc_pitchzones, "pitchtop": sc_pitchtop, "clip": sc_clip})
