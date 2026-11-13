"""Series looks for The Third Man (installed into engine.py at import):
  lab     - "The Lab": editorial paper, dot plots, beeswarms, unit dots, rings, radial neighbours, scorecards, round tabs
  board   - "Tactics Board": tilted 3D field with pucks, highlighted zones, ball paths, year tags (cream or navy)
  retro   - "What If?": sepia film look with newspaper-style clippings (scene "film": true works on any theme)
  card    - "Rising Star": a trading card that flips from front (player) to back (stats)
Captions: spec "captions": "lab" (grey words turn black as spoken, numbers boxed) or "serif" (italic, highlighted)."""
import math, random
import skia
import gfx
from gfx import text, rrect, paint, prog, eo, eio, eback, clamp, twidth

E = None          # the engine module (set by install)
HL = (255, 214, 0)        # highlighter yellow
RED = (214, 36, 56)

gfx.TF.update({
    "serif": skia.Typeface.MakeFromFile(gfx.FD + "PlayfairBold.ttf"),
    "serifI": skia.Typeface.MakeFromFile(gfx.FD + "PlayfairItalic.ttf"),
    "serifBI": skia.Typeface.MakeFromFile(gfx.FD + "PlayfairBoldItalic.ttf"),
    "mono": skia.Typeface.MakeFromFile(gfx.FD + "PlexMono.ttf"),
    "monoSB": skia.Typeface.MakeFromFile(gfx.FD + "PlexMonoSB.ttf"),
})
gfx.THEMES.update({
    "lab": dict(BG=(246, 245, 241), INK=(20, 20, 22), MUTED=(130, 130, 128), GOLD=RED, BLUE=(40, 100, 200), RED=RED,
                ORANGE=(230, 120, 20), PANEL=(255, 255, 255), LINE=(222, 220, 212), display="Inter-Bold.otf",
                heading="Inter-Bold.otf", glow=0.0, light=True),
    "board": dict(BG=(14, 27, 54), INK=(245, 242, 232), MUTED=(150, 160, 185), GOLD=HL, BLUE=(120, 180, 255), RED=(232, 70, 70),
                  ORANGE=(255, 150, 40), PANEL=(20, 36, 70), LINE=(48, 64, 100), display="Bebas.ttf", heading="OswaldBold.ttf",
                  glow=0.0, light=False),
    "retro": dict(BG=(232, 222, 198), INK=(40, 32, 24), MUTED=(120, 105, 85), GOLD=(170, 40, 30), BLUE=(60, 80, 110),
                  RED=(170, 40, 30), ORANGE=(180, 100, 40), PANEL=(244, 236, 216), LINE=(200, 186, 160), display="PlayfairBold.ttf",
                  heading="PlayfairBold.ttf", glow=0.0, light=True),
    "card": dict(BG=(8, 12, 26), INK=(244, 241, 234), MUTED=(150, 160, 185), GOLD=(245, 183, 0), BLUE=(63, 169, 245),
                 RED=(232, 64, 64), ORANGE=(255, 128, 20), PANEL=(17, 24, 46), LINE=(52, 64, 98), display="Bebas.ttf",
                 heading="OswaldBold.ttf", glow=1.0, light=False),
})
LOOKS = ("lab", "board", "retro", "card")


def col(c_):
    if isinstance(c_, (list, tuple)): return tuple(c_)
    if c_ in E.TEAMS: return E.TEAMS[c_][0]
    return {"red": RED, "hl": HL, "ink": gfx.INK, "muted": gfx.MUTED, "gold": gfx.GOLD, "blue": gfx.BLUE, "green": (40, 150, 90),
            "grey": (175, 175, 172)}.get(c_, gfx.INK)


def T(it, D, default=0.0):
    """When an item appears: its word cue if resolved, else its "at" fraction of the scene."""
    return it.get("_t", D * it.get("at", default)) if isinstance(it, dict) else D * default


# ---------------------------------------------------------------- backgrounds
def _grid(c, step, color, a):
    p = paint(color, a); p.setStrokeWidth(1.2)
    for x in range(0, gfx.W + step, step): c.drawLine(x, 0, x, gfx.H, p)
    for y in range(0, gfx.H + step, step): c.drawLine(0, y, gfx.W, y, p)


def bg_lab(c, T_):
    c.clear(gfx.ci((246, 245, 241))); _grid(c, 54, (0, 0, 0), .035)


def bg_board(c, T_, tone="navy"):
    if tone == "cream":
        c.clear(gfx.ci((240, 236, 226))); _grid(c, 60, (0, 0, 0), .05)
    else:
        sh = skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, gfx.H)], [gfx.ci((18, 32, 62)), gfx.ci((9, 18, 40))])
        c.drawPaint(skia.Paint(Shader=sh)); _grid(c, 60, (255, 255, 255), .035)


_FIB = None


def bg_retro(c, T_):
    global _FIB
    c.clear(gfx.ci((232, 222, 198)))
    if _FIB is None:
        r = random.Random(3); _FIB = [(r.random(), r.random(), r.random(), r.random()) for _ in range(260)]
    for x, y, l, a in _FIB:          # paper fibres
        p = paint((150, 130, 100), .08 + .1 * a); p.setStrokeWidth(1.2)
        c.drawLine(x * gfx.W, y * gfx.H, x * gfx.W + 30 * l, y * gfx.H + 6 * (a - .5), p)
    vg = skia.GradientShader.MakeRadial(skia.Point(gfx.W / 2, gfx.H / 2), max(gfx.W, gfx.H) * .75,
                                        [gfx.ci((0, 0, 0), 0), gfx.ci((60, 40, 20), .35)], [.55, 1])
    c.drawPaint(skia.Paint(Shader=vg))


def bg_card(c, T_):
    c.clear(gfx.ci((8, 12, 26)))
    sh = skia.GradientShader.MakeRadial(skia.Point(gfx.W / 2, gfx.H * .42), max(gfx.W, gfx.H) * .55,
                                        [gfx.ci((50, 70, 130), .55), gfx.ci((8, 12, 26), 0)])
    c.drawPaint(skia.Paint(Shader=sh))
    for k in range(3):                 # slow diagonal light sweeps
        x = ((T_ * 90 + k * 700) % (gfx.W + 1400)) - 700
        p = skia.Path(); p.moveTo(x, 0); p.lineTo(x + 160, 0); p.lineTo(x - 340, gfx.H); p.lineTo(x - 500, gfx.H); p.close()
        c.drawPath(p, paint((255, 255, 255), .025))


# ---------------------------------------------------------------- shared bits
def L(g):
    """Layout of an editorial scene."""
    if g.fmt == "short":
        return dict(x0=80, x1=1000, tabs=170, kick=262, title=352, tsize=86, sub=402, top=470, bot=1300, foot=1350, cap=1440, csize=46)
    return dict(x0=140, x1=1780, tabs=70, kick=128, title=208, tsize=78, sub=252, top=300, bot=900, foot=950, cap=1015, csize=40)


def rich(c, s, x, y, size, tf, color, a, align="l", box=HL, boxtext=(20, 20, 22), track=0):
    """Text where [bracketed] parts sit in a highlighter box."""
    parts = []; cur = ""; inb = False
    for ch in s:
        if ch in "[]":
            if cur: parts.append((cur, inb))
            cur = ""; inb = ch == "["
        else: cur += ch
    if cur: parts.append((cur, inb))
    ws = [twidth(p, size, tf, track) for p, _ in parts]; tot = sum(ws)
    xx = x - tot / 2 if align == "c" else (x - tot if align == "r" else x)
    for (p, b), w in zip(parts, ws):
        if b:
            pad = size * .12
            rrect(c, xx - pad * .4, y - size * .82, w + pad * .8, size * 1.02, size * .08, box, a)
            text(c, p, xx, y, size, tf, boxtext, a, track=track)
        else:
            text(c, p, xx, y, size, tf, color, a, track=track)
        xx += w
    return tot


def token(c, x, y, r, label, kit="ink", a=1.0, ring=None, sub=None):
    """A player token: a team-colour disc with initials (no photos, no likeness)."""
    k = col(kit); lum = E._lum(k)
    c.drawCircle(x, y + r * .08, r, paint((0, 0, 0), .18 * a, blur=r * .25))
    c.drawCircle(x, y, r, paint(k, a))
    c.drawCircle(x, y, r * .93, paint((255, 255, 255), .25 * a, stroke=r * .05))
    if ring: c.drawCircle(x, y, r * 1.12, paint(col(ring), a, stroke=max(3, r * .09)))
    tc = (255, 255, 255) if lum < .6 else (20, 20, 22)
    text(c, label, x, y + r * .3, r * .78, "interB", tc, a, "c", track=-1)
    if sub: text(c, sub, x, y + r + 34, 24, "mono", gfx.MUTED, a, "c")


def header(c, g, t, D, s, ink=None, tf="interB"):
    l = L(g); a = eo(prog(t, 0, .4)); ink = ink or gfx.INK
    if s.get("tabs"):
        tabs = s["tabs"]; act = s.get("tab", -1); x = l["x0"]; sz = 22 if g.fmt == "short" else 20
        for k, tb in enumerate(tabs):
            w = twidth(tb, sz, "monoSB", 1) + 26
            on = k == act; done = k < act
            rrect(c, x, l["tabs"] - 26, w, 38, 19, HL if on else ((225, 223, 215) if done else (240, 238, 232)), a)
            text(c, tb, x + 13, l["tabs"], sz, "monoSB", (20, 20, 22) if on else ((90, 90, 90) if done else (160, 160, 155)), a, track=1)
            x += w + 10
    if s.get("kicker"):
        text(c, s["kicker"].upper(), l["x0"], l["kick"], 26 if g.fmt == "short" else 24, "mono", gfx.MUTED, a, track=3)
    if s.get("title"):
        z = E.fit(s["title"].replace("[", "").replace("]", ""), l["x1"] - l["x0"], l["tsize"], tf, -2)
        q = eo(prog(t, .05, .45))
        c.save(); c.translate(0, (1 - q) * 20)
        rich(c, s["title"], l["x0"], l["title"], z, tf, ink, q, track=-2)
        c.restore()
    if s.get("sub"):
        text(c, s["sub"], l["x0"], l["sub"], 24 if g.fmt == "short" else 22, "mono", gfx.MUTED, a)
    if s.get("foot"):
        fy = l["foot"]
        for k, ln in enumerate(E.wrap(s["foot"], l["x1"] - l["x0"], 19, "mono")[:3]):
            text(c, ln, l["x0"], fy + k * 26, 19, "mono", gfx.MUTED, a * .9)
    if s.get("note"):                  # handwritten-style aside
        n = s["note"]; na = eo(prog(t, T(n, D, .5), T(n, D, .5) + .5))
        c.save(); c.translate(g.W * n.get("x", .7), g.H * n.get("y", .62)); c.rotate(-4)
        text(c, n["t"], 0, 0, 40 if g.fmt == "short" else 36, "serifI", RED, na, "c")
        c.restore()


# ---------------------------------------------------------------- The Lab scenes
def _chip(c, x, y, txt, sub, a, rot=-4, colr=None):
    """A sticker-style stat chip."""
    colr = colr or (20, 20, 22)
    w = max(twidth(txt, 46, "interB", -1), twidth(sub, 18, "monoSB", 2)) + 44
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(.6 + .4 * a, .6 + .4 * a)
    rrect(c, -w / 2 + 6, -38 + 8, w, 92, 12, (0, 0, 0), .18 * a)
    rrect(c, -w / 2, -38, w, 92, 12, (255, 255, 255), a, stroke=3, scol=colr, sa=a)
    text(c, txt, 0, 14, 46, "interB", colr, a, "c", track=-1)
    text(c, sub.upper(), 0, 42, 18, "monoSB", gfx.MUTED, a, "c", track=2)
    c.restore()


def _plate(c, x, y, name, sub, kit, a):
    k = col(kit); w = max(twidth(name.upper(), 40, "interB", 1), twidth(sub.upper(), 18, "monoSB", 2)) + 56
    rrect(c, x - w / 2, y - 44, w, 84, 10, (20, 20, 22), a)
    c.drawRect(skia.Rect.MakeXYWH(x - w / 2, y - 44, 10, 84), paint(k, a))
    text(c, name.upper(), x + 4, y - 4, 40, "interB", (255, 255, 255), a, "c", track=1)
    text(c, sub.upper(), x + 4, y + 26, 18, "monoSB", HL, a, "c", track=2)


def _portrait(c, cx, cy, R, P, t, a, dirn=1):
    """An illustrated player inside a disc (team kit, no likeness)."""
    k = col(P.get("kit", "ink"))
    c.drawCircle(cx, cy + 10, R, paint((0, 0, 0), .15 * a, blur=24))
    c.drawCircle(cx, cy, R, paint(P.get("disc", HL), a))
    c.save(); p = skia.Path(); p.addCircle(cx, cy, R); c.clipPath(p, doAntiAlias=True)
    for kk in range(7):                                   # halftone rays
        ang = math.radians(kk * 26 - 80 + 4 * math.sin(t * .6)); pp = paint((255, 255, 255), .16 * a); pp.setStrokeWidth(R * .12)
        c.drawLine(cx, cy + R, cx + math.cos(ang) * R * 2, cy + R - math.sin(ang) * R * 2, pp)
    E.avatar(c, cx, cy + R * .98, R * 1.55, P.get("kit", "IND"), P.get("number"), P.get("pose", "raise"), t, a,
             dir=dirn, cap=P.get("cap"), pads=P.get("pads"))
    c.restore()
    c.drawCircle(cx, cy, R, paint(E._sh(k, .8), a, stroke=10))


def sc_lab_title(c, g, t, D, s):
    """Opening card. One player: portrait disc + name plate + stat chips. Two players: split halves, VS stamp."""
    l = L(g); short = g.fmt == "short"
    lines = [ln["t"] if isinstance(ln, dict) else ln for ln in s.get("lines", [])]
    ps = s.get("players") or [{"t": tk.get("t"), "kit": tk.get("kit"), "name": tk.get("name", "")} for tk in s.get("tokens", [])]
    a = eo(prog(t, 0, .35))
    two = len(ps) == 2
    if two:                                               # split background in the two kits
        for i, P in enumerate(ps):
            q = eo(prog(t, 0, .45)); k = col(P.get("kit", "ink"))
            x0 = 0 if i == 0 else g.W / 2
            off = (-1 if i == 0 else 1) * (1 - q) * g.W * .5
            c.drawRect(skia.Rect.MakeXYWH(x0 + off, 0, g.W / 2, g.H), paint(k, .14 * q))
    ky = 250 if short else 120
    text(c, s.get("kicker", "STAT CHECK"), g.W / 2 if short or two else l["x0"], ky, 34, "serifBI", RED, a, "c" if short or two else "l")
    y = ky + 105; size = 104 if short else (92 if two else 96)
    for k, ln in enumerate(lines):
        q = eo(prog(t, .05 + .12 * k, .45 + .12 * k))
        wmax = (l["x1"] - l["x0"]) * (1 if short or two else .5)
        z = E.fit(ln.replace("[", "").replace("]", ""), wmax, size, "interB", -2)
        c.save(); c.translate(0, (1 - q) * 30)
        rich(c, ln, g.W / 2 if short or two else l["x0"], y, z, "interB", gfx.INK, q, "c" if short or two else "l", box=RED, boxtext=(255, 255, 255), track=-2)
        c.restore(); y += z * 1.06
    if not ps: return
    if two:
        R = 265 if short else 200
        cy = (y + 400) if short else 640
        for i, P in enumerate(ps):
            q = eback(prog(t, .2 + .1 * i, .75 + .1 * i))
            cx = g.W / 2 + (-1 if i == 0 else 1) * ((250 if short else 420) + (1 - q) * 400)
            _portrait(c, cx, cy, R * (.7 + .3 * q), P, t, q, dirn=1 if i == 0 else -1)
            _plate(c, cx, cy + R + 70, P.get("name", ""), P.get("sub", ""), P.get("kit", "ink"), eo(prog(t, .6, .95)))
            if P.get("chip"):
                ch = P["chip"]; _chip(c, cx + (-1 if i == 0 else 1) * R * .55, cy - R * .95, ch[0], ch[1], eback(prog(t, .5 + .15 * i, .9 + .15 * i)),
                                      rot=-6 if i == 0 else 6, colr=E._sh(col(P.get("kit", "ink")), .85))
        if s.get("teaser"):
            text(c, s["teaser"].upper(), g.W / 2, cy + R + 200 if short else cy + R + 150, 26, "monoSB", gfx.MUTED, eo(prog(t, .9, 1.3)), "c", track=4)
        qs = eback(prog(t, .7, 1.05)); sc = 2.2 - 1.2 * qs
        c.save(); c.translate(g.W / 2, cy); c.rotate(-8); c.scale(sc, sc)
        c.drawCircle(0, 0, 70, paint(RED, min(1, qs * 1.5)))
        c.drawCircle(0, 0, 70, paint((255, 255, 255), min(1, qs * 1.5), stroke=6))
        text(c, "VS", 0, 22, 64, "interB", (255, 255, 255), min(1, qs * 1.5), "c", track=-1)
        c.restore()
    else:
        P = ps[0]; R = 300 if short else 290
        cx, cy = (g.W / 2, y + 360) if short else (g.W * .72, g.H * .52)
        q = eback(prog(t, .15, .7))
        _portrait(c, cx, cy, R * (.75 + .25 * q), P, t, q)
        _plate(c, cx, cy + R + 60, P.get("name", ""), P.get("sub", ""), P.get("kit", "ink"), eo(prog(t, .45, .8)))
        for j, ch in enumerate(P.get("chips", [])):
            pos = [(-R * .85, -R * .75, -7), (R * .9, -R * .35, 6), (-R * .95, R * .35, 5)][j % 3]
            _chip(c, cx + pos[0], cy + pos[1], ch[0], ch[1], eback(prog(t, .35 + .15 * j, .75 + .15 * j)), rot=pos[2])


def sc_lab_big_text(c, g, t, D, s):
    """An editorial statement: big lines, [highlighted] parts boxed."""
    header(c, g, t, D, {k: v for k, v in s.items() if k != "title"}); l = L(g); short = g.fmt == "short"
    lines = [ln["t"] if isinstance(ln, dict) else ln for ln in s["lines"]]
    size = 104 if short else 110; y = (l["top"] + l["bot"]) / 2 - (len(lines) - 1) * size * .55 + size * .3
    for k, ln in enumerate(lines):
        q = eo(prog(t, .08 + .14 * k, .5 + .14 * k))
        z = E.fit(ln.replace("[", "").replace("]", ""), l["x1"] - l["x0"], size, "interB", -2)
        c.save(); c.translate(0, (1 - q) * 26)
        rich(c, ln, l["x0"], y, z, "interB", gfx.INK, q, "l", box=HL, track=-2)
        c.restore(); y += z * 1.12


def sc_lab_vs(c, g, t, D, s):
    """Two or three big numbers stacked, each with a label and a bar to scale."""
    header(c, g, t, D, s); l = L(g); short = g.fmt == "short"
    its = s["items"]; n = len(its); mx = s.get("max") or max(float(it["v"]) for it in its) * 1.08
    h = (l["bot"] - l["top"]) / n; w = l["x1"] - l["x0"]
    for k, it in enumerate(its):
        st = T(it, D, .1 + .3 * k); q = eo(prog(t, st, st + .45)); qb = eio(prog(t, st, st + .9))
        y = l["top"] + k * h + h * .55
        cc = col(it.get("c", "red" if k == n - 1 else "ink"))
        x = l["x0"]
        if it.get("t"):
            token(c, x + 34, y - 60, 34, it["t"], it.get("kit", "ink"), q); x += 84
        text(c, it["label"], x, y - 50, 32 if short else 28, "interSB", gfx.INK, q)
        txt = it.get("text", f'{float(it["v"]):g}')
        z = 150 if short else 120
        text(c, txt, l["x1"], y + 50, z, "interB", cc, q, "r", track=-3)
        bw = (w - twidth(txt, z, "interB", -3) - 60) * clamp(float(it["v"]) / mx) * qb
        rrect(c, l["x0"], y + 2, w - twidth(txt, z, "interB", -3) - 60, 26, 13, (226, 224, 216), q)
        rrect(c, l["x0"], y + 2, max(26, bw), 26, 13, cc, q)


def sc_lab_dots(c, g, t, D, s):
    header(c, g, t, D, s); l = L(g); short = g.fmt == "short"
    rows = s["rows"]; n = len(rows)
    lw = 360 if short else 520
    xa, xb = l["x0"] + lw, l["x1"] - 110
    top = l["top"] + 40; rh = min(66 if short else 44, (l["bot"] - top) / max(1, n))
    lo, hi = s.get("domain", [0, 100])
    X = lambda v: xa + (xb - xa) * (v - lo) / (hi - lo)
    a = eo(prog(t, .2, .6))
    for v in (s.get("ticks", [lo, (lo + hi) / 2, hi]) if s.get("tick_labels", True) else []):
        text(c, f"{v:g}", X(v), top - 26, 20, "mono", gfx.MUTED, a, "c")
    series = s.get("series")                   # optional legend for two-dot rows
    if series:
        x = l["x0"]
        for se in series:
            c.drawCircle(x + 10, top - 34, 9, paint(col(se["c"]), a))
            text(c, se["name"], x + 26, top - 26, 24, "interB", gfx.INK, a); x += twidth(se["name"], 24, "interB") + 60
    for k, r in enumerate(rows):
        y = top + k * rh + rh * .6
        st = D * s.get("from", .08) + k * D * s.get("stagger", .45) / max(1, n)
        q = eo(prog(t, st, st + .5))
        hl = r.get("hl") and t >= T(r, D, 0) if isinstance(r.get("hl"), bool) else False
        lsz = 28 if short else 24
        if hl: rrect(c, l["x0"] - 8, y - lsz * .95, twidth(r["label"], lsz, "interSB") + 16, lsz * 1.35, 6, (250, 205, 212), q)
        text(c, r["label"], l["x0"], y, lsz, "interSB" if hl else "inter", gfx.INK, q)
        lp = paint((205, 203, 196), q); lp.setStrokeWidth(2); c.drawLine(xa, y - 9, xb, y - 9, lp)
        for v in s.get("ticks", [lo, (lo + hi) / 2, hi])[1:-1]:
            c.drawLine(X(v), y - 15, X(v), y - 3, lp)
        vals = r["v"] if isinstance(r["v"], list) else [r["v"]]
        cols = [col(se["c"]) for se in series] if series else [RED if hl else gfx.INK]
        if len(vals) == 2:
            pp = paint((40, 40, 40), .5 * q); pp.setStrokeWidth(4); c.drawLine(X(lo + (vals[0] - lo) * q), y - 9, X(lo + (vals[1] - lo) * q), y - 9, pp)
        for j, v in enumerate(vals):
            vx = X(lo + (v - lo) * q)
            c.drawCircle(vx, y - 9, 13 if short else 10, paint(cols[j % len(cols)], q))
            if hl and j == 0: c.drawCircle(vx, y - 9, 18, paint(RED, q, stroke=3))
        txt = r.get("text", f'{vals[0]:g}')
        text(c, txt, xb + 26, y, 26 if short else 22, "monoSB", gfx.INK, q)
        if r.get("badge") and hl:
            bx = xb + 26 + twidth(txt, 26, "monoSB") + 14
            rrect(c, bx, y - 26, twidth(r["badge"], 22, "monoSB") + 14, 34, 5, RED, q)
            text(c, r["badge"], bx + 7, y - 2, 22, "monoSB", (255, 255, 255), q)


def _swarm(vals, X, r):
    placed = []; out = []
    for v in sorted(vals):
        x = X(v); y = 0; k = 0
        while any((x - px) ** 2 + (y - py) ** 2 < (2 * r) ** 2 for px, py in placed if abs(px - x) < 2 * r):
            k += 1; y = ((k + 1) // 2) * 2 * r * (1 if k % 2 else -1) * .92
        placed.append((x, y)); out.append((v, x, y))
    return out


def sc_lab_swarm(c, g, t, D, s):
    header(c, g, t, D, s); l = L(g); short = g.fmt == "short"
    lo, hi = s["domain"]; xa, xb = l["x0"] + 20, l["x1"] - 20
    X = lambda v: xa + (xb - xa) * (clamp((v - lo) / (hi - lo)))
    cy = (l["top"] + l["bot"]) / 2 + (40 if short else 0)
    r = s.get("r", 7 if short else 6)
    key = (g.fmt, len(s["values"]))
    if s.get("_lay", {}).get("k") != key: s["_lay"] = {"k": key, "pts": _swarm(s["values"], X, r)}
    pts = s["_lay"]["pts"]
    st = D * s.get("from", .05)
    for v, x, y in pts:
        q = clamp((t - st - .9 * (x - xa) / (xb - xa)) / .25)
        if q > 0: c.drawCircle(x, cy + y, r * .9, paint(s.get("dot", (150, 150, 146)), .75 * q))
    ap = paint(gfx.INK, eo(prog(t, st, st + .5))); ap.setStrokeWidth(2)
    ay = cy + max(abs(y) for _, _, y in pts) + 50 if pts else cy + 100
    c.drawLine(xa, ay, xb, ay, ap)
    for tv in s.get("ticks", [lo, hi]):
        text(c, f"{tv:g}", X(tv), ay + 34, 22, "mono", gfx.MUTED, eo(prog(t, st, st + .5)), "c")
    if s.get("axis"): text(c, s["axis"], (xa + xb) / 2, ay + 70, 22, "mono", gfx.MUTED, eo(prog(t, st, st + .5)), "c")
    for k, hp in enumerate(s.get("hl", [])):
        ht = T(hp, D, .45 + .12 * k); q = eback(prog(t, ht, ht + .45))
        if q <= 0: continue
        x = X(hp["v"]); y = cy + hp.get("dy", -170 if k % 2 == 0 else 170)
        lp = paint(gfx.INK, q); lp.setStrokeWidth(2); c.drawLine(x, cy, x, y, lp)
        c.drawCircle(x, cy, r * 1.6, paint(col(hp.get("c", "red")), q))
        token(c, x, y, (40 if short else 34) * q, hp.get("t", ""), hp.get("kit", "ink"), q)
        side = -1 if x > (xa + xb) / 2 else 1
        tx = x + side * (60 if short else 50)
        text(c, hp["label"], tx, y + 2, 28 if short else 24, "interB", gfx.INK, q, "l" if side > 0 else "r")
        if hp.get("sub"): text(c, hp["sub"], tx, y + 32, 20, "mono", gfx.MUTED, q, "l" if side > 0 else "r")


def sc_lab_units(c, g, t, D, s):
    header(c, g, t, D, s); l = L(g); short = g.fmt == "short"
    rows = s["rows"]; y = l["top"] + 60
    rad = 22 if short else 18; gap = rad * 2.6
    for k, r in enumerate(rows):
        st = T(r, D, .1 + .3 * k); q = eo(prog(t, st, st + .4))
        if r.get("t"): token(c, l["x0"] + 26, y - 10, 26, r["t"], r.get("kit", "ink"), q)
        text(c, r["label"], l["x0"] + (66 if r.get("t") else 0), y, 30 if short else 26, "interB", gfx.INK, q)
        y += 56
        n, kk = r.get("n", 10), r["k"]
        for j in range(n):
            x = l["x0"] + rad + j * gap; qq = clamp((t - st - .05 * j) / .2)
            full = j + 1 <= kk; part = kk - j if (not full and kk > j) else 0
            c.drawCircle(x, y, rad, paint((222, 220, 212), qq))
            if full or part:
                cc = col(r.get("c", "ink"))
                if full: c.drawCircle(x, y, rad, paint(cc, qq))
                else:
                    c.save(); c.clipRect(skia.Rect.MakeLTRB(x - rad, y - rad, x - rad + 2 * rad * part, y + rad)); c.drawCircle(x, y, rad, paint(cc, qq)); c.restore()
        text(c, r.get("text", f"{kk:g}"), l["x0"] + rad + n * gap + 10, y + 16, 44 if short else 38, "interB", col(r.get("c", "ink")), q)
        y += rad + (110 if short else 80)


def sc_lab_big(c, g, t, D, s):
    header(c, g, t, D, s); l = L(g); short = g.fmt == "short"
    v = s["value"]; dec = s.get("dec", 0); st = T(s, D, .1); q = eio(prog(t, st, st + s.get("count_dur", 1.0)))
    cur = s.get("from", 0) + (v - s.get("from", 0)) * q
    vs = s.get("prefix", "") + f"{cur:,.{dec}f}" + s.get("suffix", "")
    y = (l["top"] + l["bot"]) / 2 + (40 if short else 60)
    z = E.fit(vs, (l["x1"] - l["x0"]) * .75, 230 if short else 260, "interB", -4)
    w = text(c, vs, l["x0"], y, z, "interB", col(s.get("color", "red")), eo(prog(t, st, st + .3)), track=-4)
    if s.get("unit"):
        text(c, s["unit"], l["x0"] + twidth(vs, z, "interB", -4) + 20, y, 40 if short else 36, "interB", gfx.INK, eo(prog(t, st + .3, st + .7)))
    if s.get("label"):
        for k, ln in enumerate(E.wrap(s["label"], l["x1"] - l["x0"], 34 if short else 30, "inter")):
            text(c, ln, l["x0"], y + 70 + k * 44, 34 if short else 30, "inter", gfx.MUTED, eo(prog(t, st + .4, st + .8)))


def sc_lab_radial(c, g, t, D, s):
    header(c, g, t, D, s); l = L(g); short = g.fmt == "short"
    cx = (l["x0"] + l["x1"]) / 2 if short else g.W * .62; cy = (l["top"] + l["bot"]) / 2 + (30 if short else 20)
    R = 400 if short else 300; dmax = s.get("dmax", 8)
    a = eo(prog(t, .1, .6))
    RS = lambda d: R * math.sqrt(min(d, dmax * 1.04) / dmax)        # square-root scale: spreads out the close ones
    for d in s.get("rings", [2, 4, 6, 8]):
        rr = RS(d); c.drawCircle(cx, cy, rr, paint((190, 188, 180), a * .7, stroke=1.6))
        la = math.radians(s.get("ring_ang", 72))
        text(c, f"d = {d:g}", cx + rr * math.cos(la), cy + rr * math.sin(la) + 7, 19, "mono", gfx.MUTED, a, "c")
    rnd = random.Random(5)
    cloud = s.get("cloud") or [dmax * (.35 + .65 * rnd.random() ** .6) for _ in range(500)]
    for k, d in enumerate(cloud):
        ang = rnd.random() * math.tau; rr = RS(d)
        q = clamp((t - .2 - .6 * k / len(cloud)) / .3)
        if q > 0: c.drawCircle(cx + rr * math.cos(ang), cy + rr * math.sin(ang), 2.6, paint((150, 148, 140), .45 * q))
    ct = s.get("center", {}); c.drawCircle(cx, cy, 13, paint(RED, a))
    text(c, ct.get("label", ""), cx, cy + 40, 22, "monoSB", gfx.INK, a, "c")
    items = s.get("items", [])
    for k, it in enumerate(items):
        st = T(it, D, .35 + .1 * (len(items) - k)); q = eback(prog(t, st, st + .45))
        if q <= 0: continue
        ang = math.radians(it.get("ang", 200 + k * 47)); rr = RS(it["d"])
        x, y = cx + rr * math.cos(ang), cy + rr * math.sin(ang)
        lp = paint(gfx.INK, q); lp.setStrokeWidth(2); c.drawLine(cx, cy, x, y, lp)
        tr = (44 if short else 36) * (1.25 if k == 0 else 1) * q
        token(c, x, y, tr, it.get("t", ""), it.get("kit", "ink"), q, ring=RED if k == 0 else None)
        text(c, it["label"], x, y - tr - 16, 28 if short else 24, "interB", gfx.INK, q, "c")
        if it.get("sub"): text(c, it["sub"], x, y + tr + 30, 20, "mono", gfx.MUTED, q, "c")


def sc_lab_score(c, g, t, D, s):
    header(c, g, t, D, s); l = L(g); short = g.fmt == "short"
    rows = s["rows"]; rh = 92 if short else 70; y = l["top"] + 30
    w = (l["x1"] - l["x0"]) * (1 if short else .62)
    for k, r in enumerate(rows):
        st = T(r, D, .08 + .6 * k / max(1, len(rows))); q = eo(prog(t, st, st + .35))
        rrect(c, l["x0"], y, w, rh - 18, 10, (255, 255, 255), q, stroke=2, scol=(40, 40, 40), sa=q)
        text(c, r["label"], l["x0"] + 26, y + rh * .5, 32 if short else 26, "interSB", gfx.INK, q)
        tag = r["win"].upper(); tw = twidth(tag, 24, "monoSB", 1) + 28; cc = col(r.get("c", "ink"))
        rrect(c, l["x0"] + w - tw - 18, y + (rh - 18) / 2 - 20, tw, 40, 6, cc, q)
        text(c, tag, l["x0"] + w - tw / 2 - 18, y + (rh - 18) / 2 + 9, 24, "monoSB", (255, 255, 255) if E._lum(cc) < .6 else (20, 20, 22), q, "c", track=1)
        y += rh


def sc_lab_rings(c, g, t, D, s):
    header(c, g, t, D, s); l = L(g); short = g.fmt == "short"
    its = s["items"]; n = len(its); R = 170 if short else 150
    for k, it in enumerate(its):
        cx = l["x0"] + (l["x1"] - l["x0"]) * (k + .5) / n; cy = (l["top"] + l["bot"]) / 2
        st = T(it, D, .1 + .2 * k); q = eio(prog(t, st, st + 1.0))
        c.drawCircle(cx, cy, R, paint((225, 223, 215), 1, stroke=26))
        p = paint(col(it.get("c", "red")), 1, stroke=26); p.setStrokeCap(skia.Paint.kRound_Cap)
        c.drawArc(skia.Rect.MakeXYWH(cx - R, cy - R, 2 * R, 2 * R), -90, 360 * it["v"] / 100 * q, False, p)
        text(c, f'{it["v"] * q:.{it.get("dec", 0)}f}%', cx, cy + 26, 76 if short else 64, "interB", col(it.get("c", "red")), eo(prog(t, st, st + .3)), "c")
        if it.get("t"): token(c, cx, cy - R - 70, 34, it["t"], it.get("kit", "ink"), eo(prog(t, st, st + .3)))
        text(c, it["label"], cx, cy + R + 64, 28 if short else 24, "interB", gfx.INK, eo(prog(t, st, st + .3)), "c")


def sc_lab_compare(c, g, t, D, s):
    """Head-to-head table: two tokens on top, rows of [label, a, b, winner a|b|level]."""
    header(c, g, t, D, s); l = L(g); short = g.fmt == "short"
    A, B = s["a"], s["b"]; w = l["x1"] - l["x0"]
    ca, cb = l["x0"] + w * .62, l["x0"] + w * .88; y = l["top"] + 40
    a = eo(prog(t, .1, .5))
    for cxx, P in ((ca, A), (cb, B)):
        token(c, cxx, y, 40 if short else 34, P["t"], P.get("kit", "ink"), a)
        text(c, P["name"], cxx, y + 74, 26 if short else 22, "interB", gfx.INK, a, "c")
    y += 150; rh = 88 if short else 64
    for k, r in enumerate(s["rows"]):
        st = T(r, D, .15 + .6 * k / max(1, len(s["rows"]))); q = eo(prog(t, st, st + .35))
        lp = paint((210, 208, 200), q); lp.setStrokeWidth(2); c.drawLine(l["x0"], y + rh * .62, l["x1"], y + rh * .62, lp)
        text(c, r[0], l["x0"], y + rh * .4, 30 if short else 26, "inter", gfx.INK, q)
        for j, (cxx, v) in enumerate(((ca, r[1]), (cb, r[2]))):
            win = (r[3] == "a" and j == 0) or (r[3] == "b" and j == 1)
            if win: rrect(c, cxx - 80, y + rh * .4 - 38, 160, 50, 8, HL, q)
            text(c, v, cxx, y + rh * .4, 36 if short else 30, "interB" if win else "inter", gfx.INK if win else gfx.MUTED, q, "c")
        y += rh


# ---------------------------------------------------------------- Tactics Board
def _board_matrix(g, tilt=.62):
    short = g.fmt == "short"
    if short: cx, top, bot, wb = g.W / 2, 560, 1330, 1010
    else: cx, top, bot, wb = g.W / 2, 330, 1000, 1240
    wt = wb * tilt
    src = [skia.Point(-575, -500), skia.Point(575, -500), skia.Point(575, 500), skia.Point(-575, 500)]
    dst = [skia.Point(cx - wt / 2, top), skia.Point(cx + wt / 2, top), skia.Point(cx + wb / 2, bot), skia.Point(cx - wb / 2, bot)]
    m = skia.Matrix(); m.setPolyToPoly(src, dst)
    return m


def _fp(name_or_xy):
    if isinstance(name_or_xy, str): fx, fy = E.POS[name_or_xy]
    else: fx, fy = name_or_xy
    return fx * 500 * 1.15 / 1.15, fy * 500      # plane units: x and y both scaled by R=500


def _bez(p0, p1, p2, f):
    return ((1 - f) ** 2 * p0[0] + 2 * (1 - f) * f * p1[0] + f * f * p2[0], (1 - f) ** 2 * p0[1] + 2 * (1 - f) * f * p1[1] + f * f * p2[1])


def sc_board(c, g, t, D, s):
    tone = s.get("tone", "navy"); navy = tone == "navy"
    bg_board(c, t, tone)
    ink = (245, 242, 232) if navy else (20, 26, 40)
    short = g.fmt == "short"
    m = _board_matrix(g, s.get("tilt", .62))
    a = eo(prog(t, 0, .5))
    c.save(); c.concat(m)
    fc = (24, 44, 84) if navy else (250, 248, 240)
    c.drawOval(skia.Rect.MakeLTRB(-575, -500, 575, 500), paint(fc, a))
    c.drawOval(skia.Rect.MakeLTRB(-575, -500, 575, 500), paint(ink, .7 * a, stroke=5))
    ring = paint(ink, .45 * a, stroke=3); ring.setPathEffect(skia.DashPathEffect.Make([18, 14], 0))
    c.drawOval(skia.Rect.MakeLTRB(-300, -280, 300, 280), ring)
    c.drawRect(skia.Rect.MakeLTRB(-22, -125, 22, 125), paint((210, 190, 140) if navy else (226, 208, 160), a))
    for yy in (-112, 112): c.drawRect(skia.Rect.MakeLTRB(-40, yy - 2, 40, yy + 2), paint(ink, .8 * a))
    ln = s.get("length")
    if ln:   # a length band on the pitch, metres from the batter's stumps
        y0 = 125 - ln["from"] / 20.12 * 250; y1 = 125 - ln["to"] / 20.12 * 250; q = eo(prog(t, T(ln, D, .2), T(ln, D, .2) + .5))
        c.drawRect(skia.Rect.MakeLTRB(-60, min(y0, y1), 60, max(y0, y1)), paint(col(ln.get("c", "hl")), .85 * q))
    for z in s.get("zones", []):       # highlighted zones around groups of positions
        q = eo(prog(t, T(z, D, .3), T(z, D, .3) + .5))
        if q <= 0: continue
        c.saveLayerAlpha(None, int(255 * .38 * q))
        pts = [_fp(p) for p in z["pos"]]
        for x, y in pts: c.drawCircle(x, y, z.get("r", 70), paint(col(z.get("c", "hl"))))
        if len(pts) > 1:
            pa = skia.Path(); pa.moveTo(*pts[0])
            for p in pts[1:]: pa.lineTo(*p)
            pp = paint(col(z.get("c", "hl")), 1, stroke=z.get("r", 70) * 2); pp.setStrokeJoin(skia.Paint.kRound_Join); pp.setStrokeCap(skia.Paint.kRound_Cap)
            c.drawPath(pa, pp)
        c.restore()
    for pth in s.get("paths", []):    # ball paths: from -> to, curved, drawn on
        st = T(pth, D, .4); q = eio(prog(t, st, st + pth.get("dur", .8)))
        if q <= 0: continue
        p0 = _fp(pth.get("from", (0, .25))); p2 = _fp(pth["to"]); bend = pth.get("bend", .25)
        p1 = ((p0[0] + p2[0]) / 2 - (p2[1] - p0[1]) * bend, (p0[1] + p2[1]) / 2 + (p2[0] - p0[0]) * bend)
        pa = skia.Path(); pa.moveTo(*p0)
        for k in range(1, 41):
            f = q * k / 40; pa.lineTo(*_bez(p0, p1, p2, f))
        pp = paint(col(pth.get("c", "hl")), 1, stroke=9); pp.setStrokeCap(skia.Paint.kRound_Cap)
        if pth.get("dash"): pp.setPathEffect(skia.DashPathEffect.Make([24, 18], 0))
        c.drawPath(pa, pp)
        e = _bez(p0, p1, p2, q); e2 = _bez(p0, p1, p2, max(0, q - .04))
        ang = math.atan2(e[1] - e2[1], e[0] - e2[0])
        ah = skia.Path(); ah.moveTo(e[0] + 30 * math.cos(ang), e[1] + 30 * math.sin(ang))
        ah.lineTo(e[0] + 22 * math.cos(ang + 2.5), e[1] + 22 * math.sin(ang + 2.5)); ah.lineTo(e[0] + 22 * math.cos(ang - 2.5), e[1] + 22 * math.sin(ang - 2.5)); ah.close()
        c.drawPath(ah, paint(col(pth.get("c", "hl")), 1))
    c.restore()
    # pucks (drawn upright, projected)
    pucks = [dict(p="batter", xy=(0, .27), c="red", label=s.get("batter_label", ""))] if s.get("batter", True) else []
    hl = set(s.get("hl", [])); zoned = {p for z in s.get("zones", []) for p in z["pos"]}
    for k, f in enumerate(s.get("fielders", [])):
        nm = f if isinstance(f, str) else f["p"]
        lab = nm if s.get("labels", True) and nm not in zoned and nm != "keeper" else ""
        pucks.append(dict(p=nm, xy=E.POS[nm], c="hl" if nm in hl else ("white" if navy else "navy"), label=lab,
                          at=.1 + .3 * k / max(1, len(s["fielders"]))))
    for pk in s.get("pucks", []): pucks.append(pk)
    top_y = _board_matrix(g).mapXY(0, -500).y(); bot_y = _board_matrix(g).mapXY(0, 500).y()
    order = sorted(pucks, key=lambda p: m.mapXY(*_fp(p.get("xy", p["p"]))).y())
    for pk in order:
        X, Y = _fp(pk.get("xy", pk["p"])); pt = m.mapXY(X, Y); x, y = pt.x(), pt.y()
        q = eback(prog(t, D * pk.get("at", .05), D * pk.get("at", .05) + .35))
        if q <= 0: continue
        sc = (.7 + .3 * (y - top_y) / max(1, bot_y - top_y)) * (1.0 if short else .9) * q
        rw, rh, hh = 34 * sc, 12 * sc, 14 * sc
        cc = {"white": (240, 240, 236), "navy": (22, 36, 72), "hl": HL, "red": (226, 60, 60)}.get(pk["c"], col(pk["c"]))
        c.drawOval(skia.Rect.MakeXYWH(x - rw * 1.1, y - rh + 6 * sc, rw * 2.2, rh * 2.2), paint((0, 0, 0), .3))
        c.drawRect(skia.Rect.MakeLTRB(x - rw, y - hh, x + rw, y), paint(E._sh(cc, .72) if pk["c"] != "white" else (190, 190, 186)))
        c.drawOval(skia.Rect.MakeXYWH(x - rw, y - rh, rw * 2, rh * 2), paint(E._sh(cc, .72) if pk["c"] != "white" else (190, 190, 186)))
        c.drawOval(skia.Rect.MakeXYWH(x - rw, y - hh - rh, rw * 2, rh * 2), paint(cc))
        if pk.get("label"):
            lt = pk["label"]; lz = (24 if short else 20)
            text(c, lt, x, y + 30 * sc + 8, lz, "serifI", ink, q * .95, "c")
    for z in s.get("zones", []):                  # one label per zone, beside it
        q = eo(prog(t, T(z, D, .3) + .3, T(z, D, .3) + .7))
        pts = [m.mapXY(*_fp(p)) for p in z["pos"]]
        zx = max(p.x() for p in pts) + (40 if short else 34); zy = sum(p.y() for p in pts) / len(pts) + 50
        lab = z.get("label", "slip cordon" if any("slip" in p for p in z["pos"]) else "")
        if lab:
            tw = twidth(lab, 28 if short else 24, "serifBI") + 24
            rrect(c, zx - 12, zy - 30, tw, 42, 6, HL, q)
            text(c, lab, zx, zy, 28 if short else 24, "serifBI", (20, 20, 22), q)
    # year tag + headline
    if s.get("tag"):
        tg = s["tag"]; tw = twidth(tg, 30, "monoSB") + 24; ty = 300 if short else 90
        rrect(c, 80 if short else 140, ty - 32, tw, 46, 4, HL, a)
        text(c, tg, (80 if short else 140) + 12, ty, 30, "monoSB", (20, 20, 22), a)
    if s.get("head"):
        y = 410 if short else 200; z = 64 if short else 58
        for k, ln in enumerate(s["head"] if isinstance(s["head"], list) else [s["head"]]):
            q = eo(prog(t, .1 + .12 * k, .5 + .12 * k))
            zz = E.fit(ln.replace("[", "").replace("]", ""), g.W - 200, z, "serifBI")
            rich(c, ln, g.W / 2, y + k * zz * 1.15, zz, "serifBI", ink, q, "c")
    if s.get("foot"):
        text(c, s["foot"].upper(), g.W / 2, 1390 if short else 1050, 19, "mono", (150, 160, 185) if navy else (120, 120, 116), a, "c", track=2)


# ---------------------------------------------------------------- What If? (retro)
SEPIA = [0.393 * .9, 0.769 * .9, 0.189 * .9, 0, 0.04,
         0.349 * .9, 0.686 * .9, 0.168 * .9, 0, 0.03,
         0.272 * .9, 0.534 * .9, 0.131 * .9, 0, 0.0,
         0, 0, 0, 1, 0]


def film_on(spec, s): return s.get("film", spec.get("theme") == "retro" and s.get("film", True))


def film_begin(c):
    p = skia.Paint(); p.setColorFilter(skia.ColorFilters.Matrix(SEPIA)); c.saveLayer(None, p)


def film_end(c, g, T_, frame):
    c.restore()
    r = random.Random(frame // 2)
    for _ in range(r.randint(0, 3)):          # scratches
        x = r.random() * g.W; p = paint((255, 250, 235), .18 + .2 * r.random()); p.setStrokeWidth(1 + 2 * r.random())
        c.drawLine(x, 0, x + r.uniform(-20, 20), g.H, p)
    for _ in range(r.randint(2, 7)):          # dust
        c.drawCircle(r.random() * g.W, r.random() * g.H, 1 + 3 * r.random(), paint((30, 20, 10), .35))
    c.drawRect(skia.Rect.MakeWH(g.W, g.H), paint((0, 0, 0), .04 + .05 * abs(math.sin(T_ * 23))))   # flicker
    vg = skia.GradientShader.MakeRadial(skia.Point(g.W / 2, g.H / 2), max(g.W, g.H) * .7, [gfx.ci((0, 0, 0), 0), gfx.ci((20, 12, 4), .55)], [.5, 1])
    c.drawPaint(skia.Paint(Shader=vg))


def _torn(x, y, w, h, seed):
    r = random.Random(seed); p = skia.Path(); p.moveTo(x, y)
    for k in range(1, 30): p.lineTo(x + w * k / 29, y + r.uniform(-5, 5))
    for k in range(1, 30): p.lineTo(x + w + r.uniform(-5, 5), y + h * k / 29)
    for k in range(1, 30): p.lineTo(x + w - w * k / 29, y + h + r.uniform(-5, 5))
    for k in range(1, 30): p.lineTo(x + r.uniform(-5, 5), y + h - h * k / 29)
    p.close(); return p


def sc_clipping(c, g, t, D, s):
    """An illustrative newspaper-style cutting (no real masthead). Headline, dateline, column text."""
    short = g.fmt == "short"
    if gfx.THEME != "retro": bg_retro(c, t)
    w, h = (900, 760) if short else (980, 700)
    cx, cy = g.W / 2, (g.H * .44 if short else g.H * .5)
    q = eback(prog(t, .05, .6)); rot = s.get("rot", -3) + (1 - q) * 8
    c.save(); c.translate(cx, cy + (1 - q) * 120); c.rotate(rot); c.scale(.9 + .1 * q, .9 + .1 * q)
    path = _torn(-w / 2, -h / 2, w, h, s.get("seed", 1))
    c.save(); c.translate(10, 14); c.drawPath(path, paint((0, 0, 0), .25, blur=12)); c.restore()
    c.drawPath(path, paint((244, 237, 218)))
    x0 = -w / 2 + 50; y = -h / 2 + 70
    text(c, s.get("dateline", "").upper(), x0, y, 22, "mono", (90, 80, 66), 1, track=2)
    rule = paint((60, 50, 40)); rule.setStrokeWidth(3); c.drawLine(x0, y + 20, w / 2 - 50, y + 20, rule)
    y += 100
    for ln in s["headline"]:
        z = E.fit(ln, w - 100, 92, "serif"); text(c, ln, x0, y, z, "serif", (30, 24, 18), 1); y += z * 1.05
    if s.get("deck"):
        for ln in E.wrap(s["deck"], w - 100, 34, "serifI"): text(c, ln, x0, y + 20, 34, "serifI", (70, 60, 48), 1); y += 44
    y += 50; r = random.Random(s.get("seed", 1))
    colw = (w - 140) / 2
    for colx in (x0, x0 + colw + 40):        # column text as grey lines
        yy = y
        while yy < h / 2 - 60:
            c.drawRect(skia.Rect.MakeXYWH(colx, yy, colw * (.75 + .25 * r.random()), 9), paint((150, 138, 118), .7)); yy += 22
    c.restore()
    text(c, "ILLUSTRATIVE", g.W - (80 if short else 140), 300 if short else 90, 20, "mono", (110, 96, 76), eo(prog(t, .3, .7)), "r", track=3)


def sc_quote(c, g, t, D, s):
    """A verified quote, big serif italic, with attribution and source."""
    short = g.fmt == "short"
    if gfx.THEME not in ("retro", "lab"): bg_retro(c, t)
    l = L(g); y = 600 if short else 360; z = 64 if short else 60; ink = gfx.INK
    text(c, "“", l["x0"] - 10, y - 20, 200, "serif", RED, eo(prog(t, 0, .4)))
    for k, ln in enumerate(E.wrap(s["q"], l["x1"] - l["x0"], z, "serifI")):
        rich(c, ln, l["x0"], y + 90 + k * z * 1.25, z, "serifI", ink, eo(prog(t, .1 + .08 * k, .5 + .08 * k)))
    n = len(E.wrap(s["q"], l["x1"] - l["x0"], z, "serifI"))
    text(c, "— " + s["who"], l["x0"], y + 130 + n * z * 1.25, 30, "interSB", ink, eo(prog(t, .5, .9)))
    if s.get("src"): text(c, s["src"].upper(), l["x0"], y + 172 + n * z * 1.25, 18, "mono", gfx.MUTED, eo(prog(t, .5, .9)), track=2)


# ---------------------------------------------------------------- Rising Star card
def sc_card(c, g, t, D, s):
    short = g.fmt == "short"
    cw, ch = (680, 960) if short else (520, 740)
    cx, cy = (g.W / 2, 930) if short else (g.W * .32, g.H * .54)
    fl = T(s, D, s.get("flip_at", .45)) if "word" in s or "flip_at" in s else None
    if fl is None and "_t" in s: fl = s["_t"]
    q_in = eback(prog(t, 0, .7))
    fq = clamp((t - fl) / .55) if fl is not None else 0
    ang = math.pi * eio(fq); sx = abs(math.cos(ang)); back = ang > math.pi / 2
    k = col(s.get("kit", "IND")); k2 = E._lift(k, .35)
    c.save(); c.translate(cx, cy + (1 - q_in) * 300); c.rotate((1 - q_in) * -10 + 1.5 * math.sin(t * .8)); c.scale(sx * q_in, q_in)
    rect = skia.Rect.MakeXYWH(-cw / 2, -ch / 2, cw, ch)
    c.drawRRect(skia.RRect.MakeRectXY(rect.makeOffset(0, 18), 36, 36), paint((0, 0, 0), .45, blur=30))
    holo = skia.GradientShader.MakeSweep(0, 0, [gfx.ci(c_) for c_ in ((255, 214, 0), (255, 120, 200), (90, 200, 255), (140, 255, 170), (255, 214, 0))])
    pp = skia.Paint(Shader=holo); pp.setAntiAlias(True)
    c.drawRRect(skia.RRect.MakeRectXY(rect, 36, 36), pp)
    inner = rect.makeInset(16, 16)
    if not back:
        sh = skia.GradientShader.MakeLinear([skia.Point(0, -ch / 2), skia.Point(0, ch / 2)], [gfx.ci(k2), gfx.ci(E._sh(k, .45))])
        c.drawRRect(skia.RRect.MakeRectXY(inner, 26, 26), skia.Paint(Shader=sh, AntiAlias=True))
        text(c, s.get("banner", "RISING STAR"), 0, -ch / 2 + 90, 54, "bebas", (255, 255, 255), 1, "c", track=6)
        c.save(); c.clipRRect(skia.RRect.MakeRectXY(inner, 26, 26), doAntiAlias=True)
        E.avatar(c, 0, ch / 2 - 250, 520 if short else 400, s.get("kit", "IND"), s.get("number"), s.get("pose", "raise"), t, 1)
        c.restore()
        band = skia.Rect.MakeLTRB(inner.left(), ch / 2 - 230, inner.right(), inner.bottom())
        c.drawRect(band, paint((8, 12, 26), .88))
        text(c, s["name"].upper(), 0, ch / 2 - 150, E.fit(s["name"].upper(), cw - 80, 76, "bebas", 3), "bebas", (255, 255, 255), 1, "c", track=3)
        text(c, s.get("role", "").upper(), 0, ch / 2 - 96, 24, "monoSB", HL, 1, "c", track=3)
        text(c, s.get("team", "").upper(), 0, ch / 2 - 58, 22, "mono", (200, 205, 220), 1, "c", track=2)
    else:
        c.scale(-1, 1); c.scale(-1, 1)
        c.drawRRect(skia.RRect.MakeRectXY(inner, 26, 26), paint((14, 20, 40)))
        text(c, s.get("back_title", "THE NUMBERS").upper(), 0, -ch / 2 + 100, 48, "bebas", HL, 1, "c", track=4)
        rows = s.get("stats", []); y = -ch / 2 + 190; rh = (ch - 280) / max(1, len(rows))
        for j, r in enumerate(rows):
            qq = eo(prog(t, fl + .5 + .18 * j, fl + .8 + .18 * j))
            text(c, r[1], -cw / 2 + 60, y + rh * .55, E.fit(r[1], cw * .45, 88, "bebas"), "bebas", col(r[2]) if len(r) > 2 else (255, 255, 255), qq)
            for li, ln in enumerate(E.wrap(r[0].upper(), cw * .42, 22, "monoSB")[:3]):
                text(c, ln, cw * .02, y + rh * .3 + li * 28, 22, "monoSB", (200, 205, 220), qq, track=1)
            if j < len(rows) - 1:
                lp = paint((255, 255, 255), .12 * qq); lp.setStrokeWidth(2); c.drawLine(-cw / 2 + 50, y + rh, cw / 2 - 50, y + rh, lp)
            y += rh
    # sheen sweep
    c.save(); c.clipRRect(skia.RRect.MakeRectXY(rect, 36, 36), doAntiAlias=True)
    sx0 = ((t * 500) % (cw * 3)) - cw * 1.5
    sp = skia.Path(); sp.moveTo(sx0, -ch); sp.lineTo(sx0 + 90, -ch); sp.lineTo(sx0 - 200, ch); sp.lineTo(sx0 - 290, ch); sp.close()
    c.drawPath(sp, paint((255, 255, 255), .12)); c.restore()
    c.restore()
    if not short and s.get("side"):          # long format: notes beside the card
        y = 300
        for ln in s["side"]:
            text(c, ln, g.W * .58, y, 44, "interB", gfx.INK, eo(prog(t, .4, .8))); y += 70


# ---------------------------------------------------------------- captions
def captions(c, g, t, grps, style, s=None):
    gi = None
    for i, gr in enumerate(grps):
        end = grps[i + 1][0]["s"] if i + 1 < len(grps) else gr[-1]["e"] + .4
        if gr[0]["s"] - .05 <= t < end: gi = i; break
    if gi is None: return
    gr = grps[gi]; l = L(g)
    lab = style == "lab"
    tf = "interB" if lab else "serifI"; size = l["csize"] + (0 if lab else 8)
    maxw = (l["x1"] - l["x0"]) * (1 if g.fmt == "short" else .8)
    lines, cur = [], []
    for wo in gr:
        trial = " ".join([x["w"] for x in cur] + [wo["w"]])
        if cur and twidth(trial, size, tf) > maxw: lines.append(cur); cur = []
        cur.append(wo)
    if cur: lines.append(cur)
    on_dark = gfx.THEME in ("board", "card", "stadium") or (s is not None and (s.get("type") == "board" and s.get("tone", "navy") == "navy"
                                                                              or s.get("type") in ("stage", "card")))
    if on_dark and gfx.THEME not in ("board", "card"):      # a soft subtitle band over busy pictures
        bw = max(sum(twidth(w["w"] + " ", size, tf) for w in ln) for ln in lines[:3]) + 60; bh = len(lines[:3]) * size * 1.3 + 30
        rrect(c, g.W / 2 - bw / 2, l["cap"] - size - 12, bw, bh, 18, (10, 12, 20), .62)
    for li, ln in enumerate(lines[:3]):
        ws = [twidth(w["w"] + " ", size, tf) for w in ln]; x = g.W / 2 - sum(ws) / 2; y = l["cap"] + li * size * 1.3
        for wo, wd in zip(ln, ws):
            spoken = wo["s"] <= t; w = wo["w"]
            key = any(ch.isdigit() for ch in w) or w.strip(".,?!:;").lower() in E.NUMWORDS
            if key and spoken:
                tw = twidth(w.strip(".,?!:;"), size, tf)
                rrect(c, x - 6, y - size * .86, tw + 12, size * 1.12, 5, RED if lab else HL, 1)
                text(c, w, x, y, size, tf, (255, 255, 255) if lab else (20, 20, 22), 1)
            else:
                if on_dark: cc = (255, 255, 255) if spoken else (150, 160, 185)
                else: cc = gfx.INK if spoken else (185, 183, 176)
                if not lab and not on_dark and gfx.THEME != "retro": cc = gfx.INK if spoken else (150, 150, 150)
                text(c, w, x, y, size, tf, cc, 1)
            x += wd


def chrome(c, g, spec, T_, total, last):
    """Minimal chrome for the editorial looks: a progress hairline and a small wordmark."""
    dark = gfx.THEME in ("board", "card")
    ink = (245, 242, 232) if dark else (20, 20, 22)
    c.drawRect(skia.Rect.MakeXYWH(0, 0, g.W * clamp(T_ / max(1, total)), 5), paint(RED if not dark else HL, .9))
    x, y = (g.W - 80, 96) if g.fmt == "short" else (g.W - 140, 1040)
    c.drawCircle(x - twidth("THE THIRD MAN", 20, "monoSB", 2) - 18, y - 7, 6, paint(RED, 1))
    text(c, "THE THIRD MAN", x, y, 20, "monoSB", ink, .85, "r", track=2)


# ---------------------------------------------------------------- install
def install(engine):
    global E
    E = engine
    E.SCENES.update({"lab_title": sc_lab_title, "lab_dots": sc_lab_dots, "lab_swarm": sc_lab_swarm, "lab_units": sc_lab_units,
                     "lab_big": sc_lab_big, "lab_radial": sc_lab_radial, "lab_score": sc_lab_score, "lab_rings": sc_lab_rings,
                     "lab_compare": sc_lab_compare, "lab_big_text": sc_lab_big_text, "lab_vs": sc_lab_vs, "board": sc_board, "clipping": sc_clipping, "quote": sc_quote, "card": sc_card})
    E.NO_CAPTION |= {"lab_title"}
    prev_bg = gfx.background

    def bg(c, T_):
        th = gfx.THEME
        if th == "lab": return bg_lab(c, T_)
        if th == "board": return bg_board(c, T_)
        if th == "retro": return bg_retro(c, T_)
        if th == "card": return bg_card(c, T_)
        return prev_bg(c, T_)
    gfx.background = bg
    prev_chrome = E.chrome

    def ch(c, g, spec, T_, total, last):
        if gfx.THEME in LOOKS: return chrome(c, g, spec, T_, total, last)
        return prev_chrome(c, g, spec, T_, total, last)
    E.chrome = ch


def resolve_words(s, words, lead):
    """Give every dict in a scene that has a "word" cue its time "_t" (first match after the previous cue)."""
    if not words: return
    W = [(E._norm(w["w"]), lead + w["s"]) for w in words]

    def walk(o):
        if isinstance(o, dict):
            if o.get("word") and "_t" not in o:
                key = E._norm(o["word"])
                for w, tm in W:
                    if w == key: o["_t"] = tm; break
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(s)


def extra_sfx(s, D, T0):
    ev = []; ty = s.get("type", "")
    if ty in ("lab_dots", "lab_score", "lab_compare"):
        rows = s.get("rows", [])
        for k, r in enumerate(rows):
            st = T(r, D, .08 + .6 * k / max(1, len(rows))) if ty != "lab_dots" else D * s.get("from", .08) + k * D * s.get("stagger", .45) / max(1, len(rows))
            ev.append([T0 + st, "tick", .8])
    elif ty in ("lab_big", "lab_rings"):
        ev.append([T0 + T(s, D, .1), "whoosh", .6])
    elif ty in ("lab_radial", "lab_swarm"):
        for k, it in enumerate(s.get("items", s.get("hl", []))):
            ev.append([T0 + T(it, D, .45 + .12 * k), "tick", 1])
    elif ty == "board":
        ev.append([T0 + .05, "whoosh", .5])
        for p in s.get("paths", []): ev.append([T0 + T(p, D, .4), "whoosh", .7])
    elif ty == "clipping":
        ev.append([T0 + .1, "whoosh", .8]); ev.append([T0 + .55, "stamp", .35])
    elif ty == "lab_title":
        ev.append([T0 + .05, "whoosh", .7]); ev.append([T0 + .4, "tick", 1]); ev.append([T0 + .55, "tick", 1])
        if len(s.get("players") or s.get("tokens") or []) == 2: ev.append([T0 + .95, "stamp", .8])
    elif ty == "card":
        ev.append([T0 + .05, "whoosh", .8])
        fl = s.get("_t", D * s.get("flip_at", .45)); ev.append([T0 + fl, "whoosh", 1]); ev.append([T0 + fl + .5, "crowd", .5])
    return ev
