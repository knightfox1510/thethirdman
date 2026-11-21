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


def _jit(i): return ((i * 37) % 11 - 5) * 1.3                                  # deterministic angle jitter (degrees), so overlapping rays fan out


def sc_wagon(c, g, t, D, s):
    LK.header(c, g, t, D, s); l = _L(g); sh = g.fmt == "short"; W = g.W
    R = 400 if sh else 330; cx = W / 2 if sh else 560; cy = l["top"] + (80 if sh else 40) + R; a = eo(prog(t, .05, .5))
    # field: rope circle, inner circle, pitch strip
    c.drawCircle(cx, cy, R + 10, paint((0, 0, 0), .10 * a, blur=22))
    c.drawCircle(cx, cy, R, paint((226, 233, 214), a))
    c.drawCircle(cx, cy, R, paint(gfx.INK, a, stroke=4)); ip = paint(gfx.INK, .35 * a, stroke=2); c.drawCircle(cx, cy, R * .5, ip)
    rrect(c, cx - 15, cy - 70, 30, 140, 4, (214, 196, 150), a)
    for k in range(-1, 2): c.drawRect(skia.Rect.MakeXYWH(cx + k * 8 - 1.5, cy - 72, 3, 9), paint(gfx.INK, a))
    text(c, "OFF SIDE", cx + R - 10, cy + R + 52, 22, "monoSB", gfx.MUTED, a, "r", track=2); text(c, "LEG SIDE", cx - R + 10, cy + R + 52, 22, "monoSB", gfx.MUTED, a, "l", track=2)
    text(c, "STRAIGHT", cx, cy - R - 16, 20, "monoSB", gfx.MUTED, a, "c", track=2)
    shots = s["pts"]; n = len(shots); shown = eo(prog(t, .2, max(.8, D * .75))) * n
    for i, (ang, runs, kind) in enumerate(shots):
        q = clamp(shown - i)
        if q <= 0: continue
        th = math.radians(ang + _jit(i)); ln = R * {1: .30, 2: .52, 3: .74}.get(runs, 1.0) * (1.0 if kind != "s" else 1.04) * (.35 + .65 * q) if kind in ("f", "s") or runs in (1, 2, 3) else R * .4 * q
        x2 = cx + math.sin(th) * ln; y2 = cy - math.cos(th) * ln
        col = LK.RED if kind == "s" else (AMB if kind == "f" else gfx.INK)
        p = paint(col, (.95 if kind in ("f", "s") else .45) * q); p.setStrokeWidth(5 if kind == "s" else (4 if kind == "f" else 2)); c.drawLine(cx, cy, x2, y2, p)
        if kind in ("f", "s"): c.drawCircle(x2, y2, 9 if kind == "s" else 7, paint(col, q))
    # key
    ky = cy + R + 100
    for j, (lab, col) in enumerate((("SIX", LK.RED), ("FOUR", AMB), ("1-3 RUNS", gfx.INK))):
        kx = l["x0"] + j * 190; c.drawCircle(kx + 10, ky - 8, 9, paint(col, a)); text(c, lab, kx + 28, ky, 22, "monoSB", gfx.INK, a, track=1)
    # photo inset (top right of the header band) and chips
    if s.get("photo") and sh:
        ph = s["photo"]; qa = eo(prog(t, .1, .6)); pr = 105; px, py = l["x1"] - pr, l["top"] - 30
        c.save(); c.clipPath(skia.Path().addCircle(px, py, pr)); im = _pimg(ph["img"]); cr = ph["crop"]
        c.drawImageRect(im, skia.Rect.MakeLTRB(*cr), skia.Rect.MakeXYWH(px - pr, py - pr, 2 * pr, 2 * pr), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear), paint((255, 255, 255), qa)); c.restore()
        c.drawCircle(px, py, pr, paint(gfx.INK, qa, stroke=5))
    ya = ky + 70; chips = s.get("chips", [])
    for j, (v, lb) in enumerate(chips):
        cw = (920 - 18 * (len(chips) - 1)) / max(1, len(chips)) if sh else 360; cx_ = l["x0"] + j * (cw + 18); qq = eo(prog(t, D * .4 + .1 * j, D * .4 + .6 + .1 * j))
        rrect(c, cx_, ya, cw, 150, 14, (255, 255, 255), qq, stroke=3, scol=LK.RED if j else gfx.INK, sa=qq); text(c, v, cx_ + cw / 2, ya + 80, 70, "interB", LK.RED if j else gfx.INK, qq, "c"); text(c, lb, cx_ + cw / 2, ya + 125, 21, "monoSB", gfx.MUTED, qq, "c")
    if s.get("footnote"): text(c, s["footnote"], l["x0"], ya + 200, 18, "mono", gfx.MUTED, eo(prog(t, D * .5, D * .5 + .6)))


_IMG = {}
def _pimg(path):
    if path not in _IMG: _IMG[path] = skia.Image.open(path)
    return _IMG[path]


LINES = [("LEG", "leg"), ("MIDDLE", "middle"), ("OFF", "off"), ("OUTSIDE OFF", "outside_off")]
LENS = [("FULL", "full"), ("GOOD", "good"), ("SHORT OF A LENGTH", "short_of_length"), ("SHORT", "short")]


def sc_pitchzones(c, g, t, D, s):
    """Two pitch panels (line by length). Cell shade = share of the panel's deliveries; the number is that share in %."""
    LK.header(c, g, t, D, s); l = _L(g); sh = g.fmt == "short"; a = eo(prog(t, .05, .5))
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


def install(engine, looks):
    global E, LK
    E = engine; LK = looks
    E.SCENES.update({"wagon": sc_wagon, "pitchzones": sc_pitchzones})
