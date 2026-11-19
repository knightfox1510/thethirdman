"""Scenes for the Test day-one match story (lab + stadium themes use the theme tokens): wicketmap (a top-down pitch with where each wicket ball pitched) and overstrip (every over of the day as one strip).
Installed by looks.install."""
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


# lengths in metres from the batter's stumps (typical bands)
BANDS = [(0, 2, "YORKER"), (2, 4, "FULL"), (4, 6, "GOOD LENGTH"), (6, 8, "BACK OF A LENGTH"), (8, 10, "SHORT")]


def sc_wicketmap(c, g, t, D, s):
    LK.header(c, g, t, D, s); l = _L(g); sh = g.fmt == "short"; items = s["items"]; n = len(items)
    top = l["top"] + 20; bot = l["bot"] - 40; H = bot - top; sc = min(H / 10.0, 95 if sh else 80); sx = sc * (1.6 if sh else 1.9); pw = 3.0 * sx
    cx = (l["x0"] + 230 + pw / 2) if not sh else (l["x0"] + 215 + pw / 2); x0 = cx - pw / 2
    a = eo(prog(t, .05, .5))
    # pitch + bands
    rrect(c, x0 - 6, top, pw + 12, H, 8, (214, 196, 150) if gfx.THEME in ("lab", "whites") else (120, 104, 70), a * .55)
    for lo, hi, nm in BANDS:
        y0 = top + lo * sc; y1 = top + hi * sc
        if (lo // 2) % 2 == 0: c.drawRect(skia.Rect.MakeXYWH(x0 - 6, y0, pw + 12, y1 - y0), paint((255, 255, 255), .10 * a))
        text(c, nm, x0 - 22, (y0 + y1) / 2 + 8, 19 if sh else 20, "monoSB", gfx.MUTED, a, "r", track=1)
    # stumps (batter's end) and crease
    for k in (-1, 0, 1): c.drawRect(skia.Rect.MakeXYWH(cx + k * .115 * sx - 3, top - 22, 6, 24), paint(gfx.INK, a))
    p = paint(gfx.INK, a); p.setStrokeWidth(3); c.drawLine(x0 - 6, top + 2, x0 + pw + 6, top + 2, p)
    text(c, "BATTER'S END · LINES FROM OFF STUMP →", cx, top - 34, 18, "monoSB", gfx.MUTED, a, "c", track=1)
    for k, lab in ((0, "OFF"), (.34, "4TH"), (.57, "5TH"), (.8, "6TH")):
        xx = cx + k * sx; ln = paint(gfx.INK, .16 * a); ln.setStrokeWidth(1.5); c.drawLine(xx, top + 6, xx, bot, ln)
        text(c, lab, xx, bot + 24, 16, "mono", gfx.MUTED, a, "c")
    for i, it in enumerate(items):
        st = D * (.14 + .62 * i / max(1, n)); q = eback(prog(t, st, st + .5)); qa = clamp(q)
        if qa <= 0: continue
        bx = cx + it["x"] * sx; by = top + it["len"] * sc
        red = LK.RED
        # movement arrow (in = towards the stumps/leg, out = away to off)
        mv = it.get("move")
        if mv:
            dx = -.32 * sx if mv == "in" else .32 * sx; ap = paint(red, .75 * qa); ap.setStrokeWidth(4)
            c.drawLine(bx, by, bx + dx * clamp(prog(t, st + .2, st + .7)), by - 1.1 * sc * clamp(prog(t, st + .2, st + .7)), ap)
        c.drawCircle(bx, by, (20 if sh else 17) * (.6 + .4 * q), paint(red, qa)); c.drawCircle(bx, by, (20 if sh else 17) * (.6 + .4 * q), paint((255, 255, 255), qa, stroke=3))
        text(c, str(it["n"]), bx, by + 7, 20, "interB", (255, 255, 255), qa, "c")
    # cards on the right (or below on vertical)
    rx = (x0 + pw + 110) if not sh else (x0 + pw + 40); rw = l["x1"] - rx; rh = min((H - 10) / max(n, 1), 150 if sh else 110)
    for i, it in enumerate(items):
        st = D * (.14 + .62 * i / max(1, n)); q = eo(prog(t, st, st + .5)); y = top + i * rh
        if q <= 0: continue
        rrect(c, rx, y + 4, rw, rh - 10, 12, (255, 255, 255) if gfx.THEME in ("lab", "whites") else (28, 40, 70), q * .95, stroke=2, scol=LK.RED, sa=.5 * q)
        text(c, f'{it["n"]}', rx + 24, y + rh * .5 + 14, 44 if sh else 46, "interB", LK.RED, q)
        nm = f'{it["who"]}  b {it["by"]}' if it.get("kind", "b") == "b" else f'{it["who"]}  c {it["catcher"]} b {it["by"]}'
        tz = E.fit(nm, rw - 90, 26 if sh else 30, "interB", -1); text(c, nm, rx + 70, y + rh * .40, tz, "interB", gfx.INK, q)
        for j, ln in enumerate(E.wrap(it["note"], rw - 90, 19 if sh else 21, "inter")[:2]): text(c, ln, rx + 70, y + rh * .40 + (28 if sh else 30) + j * (24 if sh else 26), 19 if sh else 21, "inter", gfx.MUTED, q)
        text(c, f'{it["over"]} ov · {it["score"]}', rx + rw - 14, y + 30, 18, "monoSB", gfx.MUTED, q, "r")
    if s.get("footnote"): text(c, s["footnote"], l["x0"], bot + 62, 18, "mono", gfx.MUTED, eo(prog(t, D * .5, D * .5 + .6)))


def sc_overstrip(c, g, t, D, s):
    LK.header(c, g, t, D, s); l = _L(g); sh = g.fmt == "short"; ov = s["overs"]; n = len(ov); rows = 3 if sh else 1; per = math.ceil(n / rows)
    gap = 3 if not sh else 4; cw = (l["x1"] - l["x0"] - gap * (per - 1)) / per; ch = 300 if not sh else 190; top = l["top"] + (40 if not sh else 30)
    prog_all = eo(prog(t, .1, D * .8 if D > 1 else .8)); shown = prog_all * n
    cut1, cut2 = s["session_cuts"]; split = s.get("split")                                  # overs after which the lunch / tea break fall; split = over index where the 'no wickets' stand begins
    for r in range(rows):
        y = top + r * (ch + 60)
        for j in range(per):
            i = r * per + j
            if i >= n: break
            runs, w = ov[i]; x = l["x0"] + j * (cw + gap)
            a = clamp(shown - i)
            if a <= 0: continue
            col = LK.RED if w else (GRN if runs == 0 else (AMB if runs >= 7 else (GREY if runs <= 3 else (230, 180, 80))))
            hh = ch * (.45 + .55 * (1 if w else min(1, (runs + 1) / 9)))
            if gfx.THEME not in ("lab", "whites") and col == GREY: col = (110, 125, 150)
            rrect(c, x, y + ch - hh * a, cw, hh * a, 2, col, 1)
            if w: text(c, "W", x + cw / 2, y + ch - hh * a - 8, 22 if not sh else 20, "interB", LK.RED, a, "c")
        # session marks
        for lab, cut in (("LUNCH", cut1), ("TEA", cut2)):
            if r * per < cut <= (r + 1) * per:
                xx = l["x0"] + (cut - r * per) * (cw + gap) - gap / 2; lp = paint(gfx.INK, .6 * clamp(shown / max(1, cut))); lp.setStrokeWidth(2); c.drawLine(xx, y - 8, xx, y + ch + 24, lp)
                text(c, lab, xx, y + ch + 46, 18, "monoSB", gfx.MUTED, clamp(shown / max(1, cut)), "c", track=1)
    ya = top + rows * (ch + 60) + 50; q = eo(prog(t, D * .55, D * .55 + .7))
    for k, (txt, colr) in enumerate(s["legend_lines"]):
        text(c, txt, l["x0"], ya + k * (46 if not sh else 54), 34 if not sh else 36, "interB", LK.RED if colr == "red" else gfx.INK, q)
    if s.get("footnote"): text(c, s["footnote"], l["x0"], ya + len(s["legend_lines"]) * (46 if not sh else 54) + 14, 18, "mono", gfx.MUTED, q)


def install(engine, looks):
    global E, LK
    E = engine; LK = looks
    E.SCENES.update({"wicketmap": sc_wicketmap, "overstrip": sc_overstrip})
