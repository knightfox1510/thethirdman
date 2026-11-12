"""Drawing helpers and scenes for 'What if Sachin played in the T20 era?'"""
import math, os, numpy as np, skia

W, H, FPS = 1920, 1080, 30
FD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts") + "/"
IN = FD
TF = {
    "bebas": skia.Typeface.MakeFromFile(FD + "Bebas.ttf"),
    "oswald": skia.Typeface.MakeFromFile(FD + "OswaldBold.ttf"),
    "inter": skia.Typeface.MakeFromFile(IN + "Inter-Medium.otf"),
    "interSB": skia.Typeface.MakeFromFile(IN + "Inter-SemiBold.otf"),
    "interB": skia.Typeface.MakeFromFile(IN + "Inter-Bold.otf"),
    "interL": skia.Typeface.MakeFromFile(IN + "Inter-Light.otf"),
}

# palette
BG = (7, 11, 24)
INK = (244, 241, 234)
MUTED = (150, 160, 185)
GOLD = (245, 183, 0)
ORANGE = (255, 128, 20)
BLUE = (63, 169, 245)
RED = (232, 64, 64)
PANEL = (17, 24, 46)
LINE = (52, 64, 98)


def col(c, a=1.0):
    return skia.Color4f(c[0] / 255, c[1] / 255, c[2] / 255, max(0.0, min(1.0, a)))


def ci(c, a=1.0):
    return skia.ColorSetARGB(int(255 * max(0, min(1, a))), *c)


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def prog(t, t0, t1):
    return clamp((t - t0) / (t1 - t0)) if t1 > t0 else float(t >= t0)


def eo(x):  # ease out cubic
    x = clamp(x); return 1 - (1 - x) ** 3


def eio(x):
    x = clamp(x); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2


def eback(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def lerp(a, b, x):
    return a + (b - a) * x


def paint(c=None, a=1.0, stroke=None, blur=None):
    c = INK if c is None else c
    p = skia.Paint(AntiAlias=True, Color4f=col(c, a))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
        p.setStrokeCap(skia.Paint.kRound_Cap)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


_FB = {}


def _font(tf, size, ch):
    """Font for one character, falling back to Inter Bold when the face lacks the glyph."""
    key = (tf, ch)
    if key not in _FB:
        _FB[key] = tf if skia.Font(TF[tf], 20).unicharToGlyph(ord(ch)) else "interB"
    use = _FB[key]
    f = skia.Font(TF[use], size * (0.78 if use != tf and tf in ("bebas", "oswald") else 1))
    f.setSubpixel(True)
    return f


def _plain(s, tf):
    return all(_FB.get((tf, ch), None) == tf or (_FB.setdefault((tf, ch), tf if skia.Font(TF[tf], 20).unicharToGlyph(ord(ch)) else "interB") == tf) for ch in s)


def twidth(s, size, tf="inter", track=0):
    if _plain(s, tf):
        f = skia.Font(TF[tf], size)
        if not track:
            return f.measureText(s)
        return sum(f.measureText(ch) for ch in s) + track * (len(s) - 1)
    return sum(_font(tf, size, ch).measureText(ch) for ch in s) + track * (len(s) - 1)


def text(c, s, x, y, size, tf="inter", color=None, a=1.0, align="l", track=0, glow=0):
    color = INK if color is None else color
    if a <= 0.003:
        return
    f = skia.Font(TF[tf], size)
    f.setSubpixel(True)
    w = twidth(s, size, tf, track)
    if align == "c": x -= w / 2
    elif align == "r": x -= w
    paints = []
    glow = glow * GLOWK
    if glow:
        paints.append(paint(color, a * 0.55, blur=glow))
    paints.append(paint(color, a))
    plain = _plain(s, tf)
    for p in paints:
        if plain and not track:
            c.drawString(s, x, y, f, p)
        else:
            xx = x
            for ch in s:
                ff = f if plain else _font(tf, size, ch)
                c.drawString(ch, xx, y, ff, p)
                xx += ff.measureText(ch) + track
    return w


def rrect(c, x, y, w, h, r, color=None, a=1.0, stroke=None, scol=None, sa=1.0):
    color = PANEL if color is None else color; scol = LINE if scol is None else scol
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r)
    c.drawRRect(rr, paint(color, a))
    if stroke:
        c.drawRRect(rr, paint(scol, sa, stroke=stroke))


def count_str(v, comma=True):
    return f"{int(round(v)):,}" if comma else str(int(round(v)))


# ---------------------------------------------------------------- background
_rng = np.random.default_rng(7)
_GRAIN = []
for _ in range(6):
    n = _rng.integers(0, 255, (H // 2, W // 2), dtype=np.uint8)
    rgba = np.dstack([n, n, n, np.full_like(n, 255)])
    _GRAIN.append(skia.Image.fromarray(np.ascontiguousarray(rgba), colorType=skia.kRGBA_8888_ColorType))
_DUST = _rng.random((70, 4))


def background(c, T):
    c.clear(ci(BG))
    # floodlight glows, slowly drifting
    for (cx, cy, r, colr, a, ph) in [(1500, -120, 1100, (60, 90, 170), .55, 0.0),
                                     (250, 1150, 900, (40, 60, 120), .45, 1.7),
                                     (1700, 900, 700, (120, 80, 10), .18, 3.1)]:
        cx += 60 * math.sin(T * .12 + ph); cy += 40 * math.cos(T * .1 + ph)
        sh = skia.GradientShader.MakeRadial(skia.Point(cx, cy), r, [ci(colr, a), ci(colr, 0)])
        c.drawPaint(skia.Paint(Shader=sh))
    # light beams from top right
    for i in range(3):
        ang = math.radians(118 + i * 9 + 2.5 * math.sin(T * .2 + i))
        x0, y0 = 1650 + i * 90, -60
        path = skia.Path()
        L = 2400
        a1, a2 = ang - .035, ang + .035
        path.moveTo(x0, y0)
        path.lineTo(x0 + L * math.cos(a1), y0 + L * math.sin(a1))
        path.lineTo(x0 + L * math.cos(a2), y0 + L * math.sin(a2))
        path.close()
        sh = skia.GradientShader.MakeLinear([skia.Point(x0, y0), skia.Point(x0 - 900, y0 + 1100)],
                                            [ci((170, 200, 255), .07), ci((170, 200, 255), 0)])
        c.drawPath(path, skia.Paint(AntiAlias=True, Shader=sh))
    # dust in the light
    for (u, v, s, sp) in _DUST:
        x = (u * W + T * (8 + 14 * sp)) % W
        y = (v * H - T * (5 + 10 * s)) % H
        c.drawCircle(x, y, 1 + 2.2 * s, paint((200, 215, 255), .10 + .18 * sp))
    # vignette
    sh = skia.GradientShader.MakeRadial(skia.Point(W / 2, H / 2), 1250, [ci(BG, 0), ci((0, 0, 0), .75)], [0.45, 1.0])
    c.drawPaint(skia.Paint(Shader=sh))


def grain(c, frame):
    img = _GRAIN[frame % len(_GRAIN)]
    p = skia.Paint(Alphaf=0.045)
    p.setBlendMode(skia.BlendMode.kOverlay)
    c.drawImageRect(img, skia.Rect.MakeWH(W, H), skia.SamplingOptions(), p)


def chrome(c, T, total, a=1.0):
    """Persistent series tag top-left and thin progress line."""
    rrect(c, 70, 58, 128, 44, 6, GOLD, a)
    text(c, "WHAT IF?", 134, 92, 34, "bebas", BG, a, "c", track=1.5)
    text(c, "SACHIN IN THE T20 ERA", 216, 91, 22, "interSB", INK, a * .85, track=3)
    logo_lockup(c, W - 70, 80, 52, a * .9, "r")
    c.drawRect(skia.Rect.MakeXYWH(0, H - 6, W, 6), paint(LINE, a * .5))
    c.drawRect(skia.Rect.MakeXYWH(0, H - 6, W * clamp(T / total), 6), paint(GOLD, a * .9))


def header(c, lt, title, sub=None, x=120, y=230):
    p = eo(prog(lt, 0.0, 0.7))
    off = (1 - p) * 40
    c.drawRect(skia.Rect.MakeXYWH(x, y - 72 + off, 8, 74), paint(GOLD, p))
    text(c, title, x + 30, y + off, 96, "bebas", INK, p, track=2)
    if sub:
        text(c, sub, x + 34, y + 46 + off, 26, "interSB", MUTED, p, track=4)


# ---------------------------------------------------------------- scenes
def s_hook(c, t, D):
    k = lambda f: f * D
    # phase A: 100 counts up center
    pA = eo(prog(t, 0.2, k(.26)))
    move = eio(prog(t, k(.30), k(.38)))     # 100 shrinks to column 1
    dim = eio(prog(t, k(.60), k(.68)))      # row dims, "1" arrives
    rowy = lerp(560, 330, dim)
    cols = [W / 2 - 560, W / 2, W / 2 + 560]
    size = lerp(380, 190, move)
    x = lerp(W / 2, cols[0], move)
    y = lerp(640, rowy, move)
    ra = lerp(1, .28, dim)
    text(c, count_str(100 * pA), x, y, size, "bebas", GOLD if move < .5 else INK, ra, "c", glow=18 * (1 - move))
    text(c, "INTERNATIONAL CENTURIES", x, y + lerp(80, 60, move), lerp(40, 28, move), "interSB", MUTED, ra * eo(prog(t, .4, 1.2)), "c", track=6)
    for i, (num, lab, tt) in enumerate([(34357, "INTERNATIONAL RUNS", k(.36)), (24, "YEARS AT THE TOP", k(.44))]):
        p = eo(prog(t, tt, tt + .7))
        cx = cols[i + 1]
        text(c, count_str(num * eo(prog(t, tt, tt + 1.2))), cx, rowy + (1 - p) * 50, 190, "bebas", INK, ra * p, "c")
        text(c, lab, cx, rowy + 60 + (1 - p) * 50, 28, "interSB", MUTED, ra * p, "c", track=6)
    # the "1"
    p1 = eback(prog(t, k(.66), k(.66) + .7))
    a1 = prog(t, k(.66), k(.66) + .3)
    if a1 > 0:
        s = lerp(1.6, 1.0, p1)
        c.save(); c.translate(W / 2, 790); c.scale(s, s)
        text(c, "1", 0, 0, 330, "bebas", GOLD, a1, "c", glow=26)
        c.restore()
        text(c, "T20 INTERNATIONAL", W / 2, 870, 46, "interB", INK, eo(prog(t, k(.72), k(.72) + .6)), "c", track=10)
        text(c, "IN 24 YEARS. EXACTLY ONE.", W / 2, 930, 26, "interSB", MUTED, eo(prog(t, k(.8), k(.8) + .6)), "c", track=6)


def s_jburg(c, t, D):
    k = lambda f: f * D
    header(c, t, "JOHANNESBURG", "1 DECEMBER 2006  ·  INDIA'S FIRST-EVER T20 INTERNATIONAL")
    pp = eo(prog(t, k(.12), k(.12) + .8))
    px, py, pw, ph = 120, 330 + (1 - pp) * 80, 1680, 520
    rrect(c, px, py, pw, ph, 22, PANEL, .82 * pp, stroke=2, scol=LINE, sa=pp)
    text(c, "SOUTH AFRICA 126/9   ·   INDIA 127/4 (19.5 OV)", px + 50, py + 70, 28, "interSB", MUTED, pp, track=3)
    c.drawRect(skia.Rect.MakeXYWH(px + 50, py + 100, pw - 100, 2), paint(LINE, pp))
    rows = [(k(.30), "BATTING", "S. TENDULKAR", "b Langeveldt", "10", "(12 balls)"),
            (k(.46), "BOWLING", "S. TENDULKAR", "lbw", "1", "wicket")]
    for i, (tt, lab, name, how, big, small) in enumerate(rows):
        p = eo(prog(t, tt, tt + .6))
        yy = py + 200 + i * 130
        xo = (1 - p) * -60
        text(c, lab, px + 50 + xo, yy, 24, "interB", GOLD, p, track=5)
        text(c, name, px + 280 + xo, yy, 46, "oswald", INK, p, track=1)
        text(c, how, px + 760 + xo, yy, 34, "inter", MUTED, p)
        text(c, big, px + pw - 330, yy + 12, 120, "bebas", GOLD if i == 0 else INK, p, "r", glow=10 if i == 0 else 0)
        text(c, small, px + pw - 310, yy, 30, "interSB", MUTED, p)
    pr = eo(prog(t, k(.60), k(.60) + .6))
    rrect(c, px + 50, py + 400, (pw - 100) * pr, 76, 12, GOLD, pr)
    text(c, "INDIA WON BY 6 WICKETS", px + 90, py + 452, 40, "bebas", BG, prog(t, k(.62), k(.62) + .4), track=3)
    pn = eo(prog(t, k(.80), k(.80) + .6))
    text(c, "HE NEVER PLAYED ANOTHER T20I FOR INDIA", W / 2, 960 + (1 - pn) * 30, 40, "interB", INK, pn, "c", track=5)


def cap_icon(c, cx, cy, s, a):
    # generic sports cap, drawn from shapes
    p = paint(ORANGE, a)
    dome = skia.Path()
    dome.moveTo(cx - 70 * s, cy)
    dome.cubicTo(cx - 70 * s, cy - 95 * s, cx + 70 * s, cy - 95 * s, cx + 70 * s, cy)
    dome.close()
    c.drawPath(dome, p)
    brim = skia.Path()
    brim.moveTo(cx + 10 * s, cy - 4 * s)
    brim.cubicTo(cx + 90 * s, cy - 10 * s, cx + 150 * s, cy - 2 * s, cx + 155 * s, cy + 14 * s)
    brim.cubicTo(cx + 110 * s, cy + 20 * s, cx + 50 * s, cy + 14 * s, cx + 10 * s, cy + 10 * s)
    brim.close()
    c.drawRect(skia.Rect.MakeXYWH(cx - 70 * s, cy - 6 * s, 140 * s, 10 * s), paint((215, 100, 10), a))
    c.drawPath(brim, paint((215, 100, 10), a))
    c.drawCircle(cx, cy - 70 * s, 7 * s, paint((215, 100, 10), a))
    for dx in (-30, 0, 30):
        c.drawLine(cx, cy - 70 * s, cx + dx * s * 1.6, cy, paint((215, 100, 10), a * .7, stroke=2.5 * s))


def s_ipl(c, t, D):
    k = lambda f: f * D
    header(c, t, "THE IPL YEARS", "MUMBAI  ·  2008 – 2013")
    years = list(range(2008, 2014))
    x0, x1, ly = 220, 1700, 760
    pl = eio(prog(t, k(.06), k(.30)))
    c.drawLine(x0, ly, lerp(x0, x1, pl), ly, paint(LINE, 1, stroke=4))
    hi = eo(prog(t, k(.62), k(.62) + .6))
    for i, yv in enumerate(years):
        x = lerp(x0, x1, i / 5)
        p = eback(prog(t, k(.06) + i * k(.04), k(.06) + i * k(.04) + .5))
        is10 = yv == 2010
        r = 14 * p * (1 + (.6 * hi if is10 else 0))
        colr = ORANGE if (is10 and hi > .05) else INK
        if is10 and hi > 0:
            c.drawCircle(x, ly, r * 2.6, paint(ORANGE, .25 * hi, blur=18))
        c.drawCircle(x, ly, r, paint(colr, clamp(p)))
        text(c, str(yv), x, ly + 62, 34, "oswald", colr if is10 else MUTED, clamp(p) * (1 - .5 * hi * (not is10)), "c")
    # runs counter
    pr = eo(prog(t, k(.32), k(.32) + .6))
    text(c, count_str(2334 * eo(prog(t, k(.32), k(.32) + 1.3))), 220, 520 + (1 - pr) * 40, 200, "bebas", INK, pr * (1 - .6 * hi))
    text(c, "IPL RUNS FOR MUMBAI", 228, 580 + (1 - pr) * 40, 28, "interSB", MUTED, pr * (1 - .6 * hi), track=6)
    # orange cap card
    if hi > 0:
        cx, cy = 1180, 470 + (1 - hi) * 40
        rrect(c, 820, 300 + (1 - hi) * 40, 900, 330, 22, PANEL, .9 * hi, stroke=2, scol=ORANGE, sa=.8 * hi)
        cap_icon(c, 960, cy + 30, 1.05, hi)
        text(c, "ORANGE CAP  ·  2010", 1150, cy - 50, 34, "interB", ORANGE, hi, track=5)
        p2 = eo(prog(t, k(.70), k(.70) + .6))
        text(c, count_str(618 * eo(prog(t, k(.70), k(.70) + 1.0))), 1150, cy + 90, 150, "bebas", INK, p2)
        text(c, "RUNS", 1360, cy + 90, 44, "bebas", MUTED, p2, track=2)
        p3 = eo(prog(t, k(.80), k(.80) + .6))
        text(c, "AT AGE 36", 1500, cy + 90, 44, "bebas", GOLD, p3, track=2)


def s_problem(c, t, D):
    k = lambda f: f * D
    header(c, t, "THE PROBLEM", "STRIKE RATE  =  RUNS PER 100 BALLS")
    split = eio(prog(t, k(.66), k(.66) + .8))
    bw_max = lerp(1500, 980, split)
    bx, by = 140, 360
    scale = bw_max / 170
    bars = [(k(.06), "SACHIN  ·  IPL CAREER", 119.8, INK),
            (k(.32), "TOP-ORDER BATTERS  ·  IPL 2008", 130.1, BLUE),
            (k(.46), "TOP-ORDER BATTERS  ·  IPL 2025", 158.5, GOLD)]
    for i, (tt, lab, v, cc) in enumerate(bars):
        p = eo(prog(t, tt, tt + 1.0))
        a = clamp(prog(t, tt, tt + .3))
        yy = by + i * 165
        text(c, lab, bx, yy, 26, "interB", MUTED, a, track=4)
        c.drawRect(skia.Rect.MakeXYWH(bx, yy + 20, bw_max, 74), paint(LINE, .35 * a))
        rrect(c, bx, yy + 20, v * scale * p, 74, 8, cc, a)
        text(c, f"{v * p:.1f}", bx + v * scale * p + 22, yy + 86, 82, "bebas", cc, a)
    # gap callout
    pg = eo(prog(t, k(.56), k(.56) + .6)) * (1 - split)
    if pg > 0:
        x1, x2, yy = bx + 119.8 * scale, bx + 158.5 * scale, by + 3 * 165 + 30
        c.drawLine(x1, yy, x2, yy, paint(RED, pg, stroke=4))
        c.drawLine(x1, yy - 16, x1, yy + 16, paint(RED, pg, stroke=4))
        c.drawLine(x2, yy - 16, x2, yy + 16, paint(RED, pg, stroke=4))
        text(c, "A 39-POINT GAP", (x1 + x2) / 2, yy + 60, 40, "bebas", RED, pg, "c", track=3)
    # powerplay panel
    if split > 0:
        px = lerp(1950, 1240, split)
        rrect(c, px, 330, 560, 560, 22, PANEL, .9, stroke=2, scol=LINE)
        text(c, "POWERPLAY", px + 50, 410, 30, "interB", MUTED, 1, track=6)
        text(c, "RUNS PER OVER", px + 50, 448, 22, "interSB", MUTED, .7, track=4)
        p1 = eo(prog(t, k(.72), k(.72) + .6)); p2 = eo(prog(t, k(.80), k(.80) + .8))
        text(c, "2008", px + 50, 540, 30, "oswald", BLUE, p1)
        text(c, "7.12", px + 50, 680, 150, "bebas", BLUE, p1)
        if p2 > 0:
            ax = px + 260
            c.drawLine(ax, 620, ax + 50 * p2, 620, paint(MUTED, p2, stroke=5))
            path = skia.Path(); path.moveTo(ax + 50 * p2 + 14, 620); path.lineTo(ax + 50 * p2 - 6, 606); path.lineTo(ax + 50 * p2 - 6, 634); path.close()
            c.drawPath(path, paint(MUTED, p2))
        text(c, "2025", px + 340, 540, 30, "oswald", GOLD, p2)
        text(c, f"{7.12 + 2.0 * p2:.2f}", px + 340, 680, 150, "bebas", GOLD, p2, glow=12)
        text(c, "+28%", px + 280, 810, 70, "bebas", GOLD, eo(prog(t, k(.88), k(.88) + .5)), "c")


def field(c, cx, cy, a, t, k, D):
    R = 360
    c.drawOval(skia.Rect.MakeXYWH(cx - R * 1.15, cy - R, 2.3 * R, 2 * R), paint((20, 52, 40), .55 * a))
    c.drawOval(skia.Rect.MakeXYWH(cx - R * 1.15, cy - R, 2.3 * R, 2 * R), paint(INK, .5 * a, stroke=3))
    c.drawOval(skia.Rect.MakeXYWH(cx - R * .6, cy - R * .55, 1.2 * R, 1.1 * R), paint(INK, .15 * a, stroke=2))
    rrect(c, cx - 14, cy - 90, 28, 180, 4, (190, 165, 110), .8 * a)
    # fielders (right-hander at bottom end: off side is screen-right, behind is down)
    bx0, by0 = cx, cy + 82
    spots = [(45, 150, "SLIP"), (270, 70, "POINT"), (300, -130, "COVER"), (110, -260, "MID-OFF"),
             (-110, -260, "MID-ON"), (-300, -90, "MID-WICKET"), (-220, 250, "FINE LEG")]
    for dx, dy, lab in spots:
        x, y = bx0 + dx, by0 + dy
        c.drawCircle(x, y, 9, paint(BLUE, a))
        text(c, lab, x, y - 18, 16, "interSB", MUTED, a * .8, "c", track=2)
    # batter at bottom end, ball goes over third man (behind, off side = right)
    bxp, byp = cx, cy + 82
    c.drawCircle(bxp, byp, 11, paint(GOLD, a))
    text(c, "THIRD MAN", cx + R * .55, cy + R * .80, 18, "interB", INK, a * .85, "c", track=3)
    pb = eio(prog(t, k(.66), k(.66) + 1.4))
    if pb > 0:
        ex, ey = cx + R * 1.10, cy + R * .86
        ctrl = (cx + R * .55, cy + R * .22)
        path = skia.Path(); path.moveTo(bxp, byp); path.quadTo(ctrl[0], ctrl[1], ex, ey)
        meas = skia.PathMeasure(path, False)
        L = meas.getLength()
        seg = skia.Path(); meas.getSegment(0, L * pb, seg, True)
        c.drawPath(seg, paint(GOLD, a * .35, stroke=14, blur=8))
        c.drawPath(seg, paint(GOLD, a, stroke=4))
        pos, _ = meas.getPosTan(L * pb)
        if pb < 1:
            c.drawCircle(pos.x(), pos.y(), 10, paint((255, 255, 255), a))
        else:
            pb6 = eback(prog(t, k(.66) + 1.4, k(.66) + 2.0))
            c.drawCircle(ex, ey, 70 * pb6, paint(GOLD, .3 * a, blur=10))
            text(c, "SIX", ex + 45, ey + 50 * pb6, 100 * pb6 + 1, "bebas", GOLD, a, "c", glow=10)


def s_case(c, t, D):
    k = lambda f: f * D
    header(c, t, "THE CASE FOR SACHIN")
    # part A: ODI strike rate
    aA = eo(prog(t, .3, 1.0)) * (1 - eio(prog(t, k(.27), k(.31))))
    if aA > 0:
        text(c, f"{86.2 * eo(prog(t, .3, 1.6)):.1f}", W / 2, 640, 340, "bebas", GOLD, aA, "c", glow=20)
        text(c, "ODI STRIKE RATE", W / 2, 720, 40, "interB", INK, aA, "c", track=10)
        text(c, "FAR QUICKER THAN MOST OF HIS ERA", W / 2, 780, 26, "interSB", MUTED, aA * eo(prog(t, k(.12), k(.12) + .6)), "c", track=6)
    # part B: Sharjah desert storm
    aB = eo(prog(t, k(.31), k(.31) + .6)) * (1 - eio(prog(t, k(.53), k(.57))))
    if aB > 0:
        lt = t - k(.31)
        for i in range(160):
            ang = i * 2.39996 + lt * (0.5 + (i % 7) * .08)
            rr = 120 + (i * 37 % 520)
            x = W / 2 + rr * 1.5 * math.cos(ang); y = 600 + rr * .55 * math.sin(ang)
            c.drawCircle(x, y, 2 + (i % 4), paint((220, 170, 90), aB * (.15 + (i % 5) * .06)))
        text(c, "SHARJAH  ·  1998", W / 2, 470, 34, "interB", GOLD, aB, "c", track=8)
        text(c, "THE DESERT STORM", W / 2, 640, 200, "bebas", INK, aB, "c", track=4, glow=8)
        text(c, "SACHIN vs AUSTRALIA", W / 2, 720, 32, "interSB", MUTED, aB, "c", track=6)
    # part C: upper cut field diagram
    aC = eo(prog(t, k(.57), k(.57) + .7))
    if aC > 0:
        field(c, 1250, 600, aC, t, k, D)
        text(c, "CENTURION  ·  2003", 140, 420, 30, "interB", GOLD, aC, track=6)
        text(c, "THE UPPER CUT", 140, 530, 120, "bebas", INK, aC, track=2)
        text(c, "vs SHOAIB AKHTAR", 144, 585, 30, "interSB", MUTED, aC, track=5)
        p = eo(prog(t, k(.84), k(.84) + .6))
        rrect(c, 140, 650, 470 * p, 70, 10, GOLD, p)
        text(c, "NOW A T20 STAPLE", 165, 698, 44, "bebas", BG, prog(t, k(.86), k(.86) + .3), track=3)
        text(c, "He played it before the format existed.", 144, 780, 28, "inter", MUTED, eo(prog(t, k(.9), k(.9) + .6)))


def s_scale(c, t, D):
    k = lambda f: f * D
    header(c, t, "ADJUST FOR THE ERA")
    chips = ["FLAT PITCHES", "BIGGER BATS", "IMPACT PLAYER"]
    x = 150
    for i, ch in enumerate(chips):
        p = eback(prog(t, k(.05) + i * k(.07), k(.05) + i * k(.07) + .5))
        w = twidth(ch, 30, "interB", 4) + 70
        c.save(); c.translate(x + w / 2, 340); c.scale(clamp(p, 0, 1.2), clamp(p, 0, 1.2))
        rrect(c, -w / 2, -34, w, 68, 34, PANEL, clamp(p), stroke=2, scol=BLUE, sa=clamp(p))
        text(c, ch, 0, 11, 30, "interB", INK, clamp(p), "c", track=4)
        c.restore()
        x += w + 26
    # equation
    pe = eo(prog(t, k(.38), k(.38) + .7))
    y = 640
    parts = [("119.8", INK, "SACHIN · IPL"), ("×", MUTED, ""), ("158.5", GOLD, "TOP ORDER 2025"), ("÷", MUTED, ""),
             ("130.1", BLUE, "TOP ORDER 2008")]
    xx = 150
    for i, (s, cc, lab) in enumerate(parts):
        p = eo(prog(t, k(.38) + i * .25, k(.38) + i * .25 + .5))
        w = twidth(s, 124, "bebas")
        text(c, s, xx, y + (1 - p) * 30, 124, "bebas", cc, p)
        if lab:
            text(c, lab, xx + w / 2, y + 46, 19, "interB", MUTED, p, "c", track=3)
        xx += w + 42
    pr = eo(prog(t, k(.58), k(.58) + .6))
    text(c, "=", xx, y, 124, "bebas", MUTED, pr)
    xx += 90
    val = 146 * eo(prog(t, k(.58), k(.58) + 1.4))
    text(c, count_str(val), xx, y + 40, 280, "bebas", GOLD, pr, glow=24)
    text(c, "ERA-ADJUSTED", xx + 6, y + 92, 24, "interB", GOLD, pr, track=5)
    text(c, "STRIKE RATE", xx + 6, y + 126, 24, "interB", GOLD, pr, track=5)
    text(c, "Rough estimate: his IPL strike rate scaled by the rise in top-order strike rates, 2008 to 2025.",
         150, 900, 24, "inter", MUTED, eo(prog(t, k(.66), k(.66) + .6)))
    pf = eo(prog(t, k(.82), k(.82) + .6))
    text(c, "WINS THE POWERPLAY.  KEEPS HIS WICKET.", 150, 980, 52, "bebas", INK, pf, track=4)


def s_verdict(c, t, D):
    k = lambda f: f * D
    header(c, t, "THE VERDICT")
    gx, gy, gw, gh = 150, 330, 880, 560
    pa = eo(prog(t, .3, 1.0))
    c.drawLine(gx, gy + gh, gx + gw, gy + gh, paint(LINE, pa, stroke=3))
    c.drawLine(gx, gy, gx, gy + gh, paint(LINE, pa, stroke=3))
    for v in (25, 50, 75, 100):
        yy = gy + gh - v / 110 * gh
        c.drawLine(gx, yy, gx + gw, yy, paint(LINE, .35 * pa, stroke=1))
        text(c, str(v), gx - 18, yy + 8, 22, "interSB", MUTED, pa, "r")
    text(c, "RUNS", gx, gy - 20, 22, "interB", MUTED, pa, track=4)
    text(c, "BALLS FACED", gx + gw, gy + gh + 45, 22, "interB", MUTED, pa, "r", track=4)
    # illustrative innings worm: run a ball to 30, then explode
    pts = []
    for b in range(0, 56):
        r = b if b <= 30 else 30 + (b - 30) * 1.0 + 0.085 * (b - 30) ** 2
        pts.append((gx + b / 60 * gw, gy + gh - r / 110 * gh))
    pl = eio(prog(t, k(.08), k(.55)))
    n = max(2, int(len(pts) * pl))
    path = skia.Path(); path.moveTo(*pts[0])
    for p_ in pts[1:n]:
        path.lineTo(*p_)
    c.drawPath(path, paint(GOLD, .35, stroke=16, blur=10))
    c.drawPath(path, paint(GOLD, 1, stroke=6))
    if n > 1:
        c.drawCircle(*pts[n - 1], 11, paint((255, 255, 255)))
    l1 = eo(prog(t, k(.22), k(.22) + .5))
    text(c, "RUN A BALL", gx + 22 / 60 * gw, gy + gh - 22 / 110 * gh - 36, 34, "bebas", INK, l1, "c", track=3)
    l2 = eo(prog(t, k(.48), k(.48) + .5))
    text(c, "THEN EXPLODES", gx + 55 / 60 * gw - 50, gy + 70, 34, "bebas", GOLD, l2, "r", track=3)
    text(c, "Illustrative innings", gx + gw, gy - 20, 20, "inter", MUTED, pa * .8, "r")
    # big verdict text on the right
    pv = eo(prog(t, k(.58), k(.58) + .7))
    for i, ln in enumerate(["NOT A SLOGGER.", "THE ANCHOR", "WHO EXPLODES."]):
        pi = eo(prog(t, k(.58) + i * .3, k(.58) + i * .3 + .6))
        text(c, ln, 1150 + (1 - pi) * 40, 480 + i * 118, 116, "bebas", GOLD if i == 2 else INK, pi, track=2)
    pq = eo(prog(t, k(.84), k(.84) + .7))
    text(c, "Maybe the most complete T20 batter", 1154, 860, 32, "interSB", MUTED, pq)
    text(c, "we never got to see.", 1154, 904, 32, "interSB", MUTED, pq)


def s_cta(c, t, D):
    logo_lockup(c, W / 2, 240, 110, eo(prog(t, 0, .6)), "c")
    p1 = eo(prog(t, .1, .8)); p2 = eo(prog(t, .4, 1.1))
    text(c, "WOULD SACHIN HAVE", W / 2, 470 + (1 - p1) * 40, 150, "bebas", INK, p1, "c", track=3)
    text(c, "DOMINATED THE T20 ERA?", W / 2, 620 + (1 - p2) * 40, 150, "bebas", GOLD, p2, "c", track=3, glow=14)
    p3 = eo(prog(t, 1.2, 1.8))
    text(c, "TELL US IN THE COMMENTS", W / 2, 720, 34, "interB", MUTED, p3, "c", track=8)
    p4 = eback(prog(t, 1.8, 2.4))
    pulse = 1 + .04 * math.sin(max(0, t - 2.4) * 5)
    if p4 > 0:
        c.save(); c.translate(W / 2, 840); s = clamp(p4, 0, 1.2) * pulse; c.scale(s, s)
        rrect(c, -170, -42, 340, 84, 42, RED, clamp(p4))
        text(c, "SUBSCRIBE", 0, 14, 40, "bebas", INK, clamp(p4), "c", track=4)
        c.restore()


SCENES = [s_hook, s_jburg, s_ipl, s_problem, s_case, s_scale, s_verdict, s_cta]


# ---------------------------------------------------------------- brand: The Third Man (field map mark)
def logo_mark(c, cx, cy, size, a=1.0, detail=True):
    """Field-map mark scaled to `size` px diameter, centered at (cx, cy)."""
    s = size / 190.0
    c.save(); c.translate(cx - 95 * s, cy - 95 * s); c.scale(s, s)
    c.drawCircle(95, 95, 86, paint(INK, a, stroke=6 if detail else 9))
    if detail:
        c.drawCircle(95, 95, 50, paint(LINE, a, stroke=3))
        for (x, y) in [(55, 48), (140, 58), (38, 112), (150, 104)]:
            c.drawCircle(x, y, 6, paint(MUTED, a, stroke=3))
    rrect(c, 89, 72, 12, 46, 3, INK, a)
    c.drawCircle(140, 148, 14 if detail else 17, paint(GOLD, a))
    c.restore()


def logo_lockup(c, x, y, h, a=1.0, align="l"):
    """Mark + 'THE THIRD MAN' wordmark; (x, y) = left/center of the mark row baseline area, h = mark height."""
    tw = twidth("THIRD MAN", h * .62, "bebas", track=1) + h * 0.28
    total = h + tw
    x0 = x - total / 2 if align == "c" else (x - total if align == "r" else x)
    logo_mark(c, x0 + h / 2, y, h, a, detail=h >= 70)
    text(c, "THE", x0 + h * 1.28, y - h * .14, h * .2, "interB", MUTED, a, track=h * .06)
    text(c, "THIRD MAN", x0 + h * 1.26, y + h * .33, h * .62, "bebas", INK, a, track=1)


# ---------------------------------------------------------------- themes
THEMES = {
    "floodlights": dict(BG=(7, 11, 24), INK=(244, 241, 234), MUTED=(150, 160, 185), GOLD=(245, 183, 0), BLUE=(63, 169, 245),
                        RED=(232, 64, 64), ORANGE=(255, 128, 20), PANEL=(17, 24, 46), LINE=(52, 64, 98),
                        display="Bebas.ttf", heading="OswaldBold.ttf", glow=1.0, light=False),
    "whites": dict(BG=(250, 250, 247), INK=(16, 33, 63), MUTED=(91, 100, 114), GOLD=(31, 122, 77), BLUE=(43, 108, 176),
                   RED=(200, 50, 43), ORANGE=(214, 110, 20), PANEL=(255, 255, 255), LINE=(226, 226, 218),
                   display="SpaceGroteskBold.ttf", heading="SpaceGroteskBold.ttf", glow=0.0, light=True),
    "blue": dict(BG=(10, 42, 107), INK=(255, 255, 255), MUTED=(184, 199, 232), GOLD=(255, 153, 51), BLUE=(120, 190, 255),
                 RED=(255, 92, 92), ORANGE=(255, 153, 51), PANEL=(11, 47, 120), LINE=(44, 79, 150),
                 display="TekoBold.ttf", heading="TekoSemi.ttf", glow=0.6, light=False),
    "scoreboard": dict(BG=(14, 36, 22), INK=(245, 241, 230), MUTED=(169, 183, 159), GOLD=(255, 201, 60), BLUE=(120, 200, 230),
                       RED=(255, 107, 74), ORANGE=(255, 160, 60), PANEL=(5, 13, 7), LINE=(36, 69, 47),
                       display="BigShouldersBlack.ttf", heading="BigShouldersBold.ttf", glow=0.5, light=False),
}
THEME = "floodlights"
GLOWK = 1.0
_TF0 = dict(TF)


def apply_theme(name):
    global THEME, GLOWK
    th = THEMES[name]; THEME = name; GLOWK = th["glow"]
    g = globals()
    for k in ("BG", "INK", "MUTED", "GOLD", "BLUE", "RED", "ORANGE", "PANEL", "LINE"):
        g[k] = th[k]
    TF["bebas"] = skia.Typeface.MakeFromFile(FD + th["display"]) if name != "floodlights" else _TF0["bebas"]
    TF["oswald"] = skia.Typeface.MakeFromFile(FD + th["heading"]) if name != "floodlights" else _TF0["oswald"]
    _FB.clear()


_bg_floodlights = background


def background(c, T):
    if THEME == "floodlights":
        return _bg_floodlights(c, T)
    if THEME == "whites":
        c.clear(ci(BG))
        sh = skia.GradientShader.MakeRadial(skia.Point(W * .3, H * .2), max(W, H) * .9, [ci((255, 255, 255), 1), ci((238, 238, 230), 1)])
        c.drawPaint(skia.Paint(Shader=sh))
        R = min(W, H) * .55
        cx, cy = W * .86 + 8 * math.sin(T * .1), H * .78
        c.drawCircle(cx, cy, R, paint(LINE, .55, stroke=3))
        c.drawCircle(cx, cy, R * .55, paint(LINE, .35, stroke=2))
        return
    if THEME == "blue":
        sh = skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(W, H)], [ci((10, 42, 107)), ci((14, 59, 140)), ci((10, 42, 107))], [0, .55, 1])
        c.drawPaint(skia.Paint(Shader=sh))
        c.save()
        off = (T * 12) % 58
        for i in range(-4, 14):
            x0 = W * .78 + i * 58 + off
            p = skia.Path(); p.moveTo(x0, 0); p.lineTo(x0 + 26, 0); p.lineTo(x0 + 26 - H * .47, H); p.lineTo(x0 - H * .47, H); p.close()
            c.drawPath(p, paint(GOLD, .10))
        c.restore()
        sh = skia.GradientShader.MakeRadial(skia.Point(W / 2, H / 2), max(W, H) * .8, [ci((0, 0, 0), 0), ci((0, 0, 20), .35)], [0.5, 1.0])
        c.drawPaint(skia.Paint(Shader=sh))
        return
    if THEME == "scoreboard":
        c.clear(ci(BG))
        for y in range(0, H, 180):
            c.drawRect(skia.Rect.MakeXYWH(0, y, W, 3), paint((18, 46, 29), 1))
        c.drawRect(skia.Rect.MakeXYWH(7, 7, W - 14, H - 14), paint((42, 42, 42), 1, stroke=14))
        sh = skia.GradientShader.MakeRadial(skia.Point(W / 2, H / 2), max(W, H) * .8, [ci((0, 0, 0), 0), ci((0, 0, 0), .45)], [0.45, 1.0])
        c.drawPaint(skia.Paint(Shader=sh))
