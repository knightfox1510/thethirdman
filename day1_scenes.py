"""Scenes for the Test day-one match story (lab + stadium themes use the theme tokens): wicketmap (a top-down pitch with where each wicket ball pitched) and overstrip (every over of the day as one strip).
Installed by looks.install."""
import math
import skia
import gfx
from gfx import text, rrect, paint, prog, eo, eback, clamp, twidth
E = None; LK = None
AMB = (226, 150, 24); GRN = (40, 150, 90); GREY = (170, 170, 168)


def _hd(s):
    h = s.get("head")
    return dict(s, title=h["t"], sub=h.get("sub", "")) if (isinstance(h, dict) and not s.get("title")) else s


def _L(g):
    l = dict(LK.L(g))
    if g.fmt == "short": l["bot"] = 1620
    return l


# lengths in metres from the batter's stumps (typical bands)
BANDS = [(0, 2, "YORKER"), (2, 4, "FULL"), (4, 6, "GOOD LENGTH"), (6, 8, "BACK OF A LENGTH"), (8, 10, "SHORT")]


def sc_wicketmap(c, g, t, D, s):
    LK.header(c, g, t, D, _hd(s)); l = _L(g); sh = g.fmt == "short"; items = s["items"]; n = len(items)
    top = l["top"] + 20; bot = l["bot"] - 40; H = bot - top; sc = min(H / 10.0, 95 if sh else 80); sx = sc * (1.05 if sh else 1.9); pw = 3.0 * sx
    cx = (l["x0"] + 230 + pw / 2) if not sh else (l["x0"] + 175 + pw / 2); x0 = cx - pw / 2
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
    rx = (x0 + pw + 110) if not sh else (x0 + pw + 34); rw = l["x1"] - rx; rh = min((H - 10) / max(n, 1), 150 if sh else 110)
    for i, it in enumerate(items):
        st = D * (.14 + .62 * i / max(1, n)); q = eo(prog(t, st, st + .5)); y = top + i * rh
        if q <= 0: continue
        rrect(c, rx, y + 4, rw, rh - 10, 12, (255, 255, 255) if gfx.THEME in ("lab", "whites") else (28, 40, 70), q * .95, stroke=2, scol=LK.RED, sa=.5 * q)
        text(c, f'{it["n"]}', rx + 24, y + rh * .5 + 14, 44 if sh else 46, "interB", LK.RED, q)
        nm = f'{it["who"]}  b {it["by"]}' if it.get("kind", "b") == "b" else f'{it["who"]}  c {it["catcher"]} b {it["by"]}'
        tz = E.fit(nm, rw - 120, 26 if sh else 30, "interB", -1); text(c, nm, rx + 70, y + rh * .40, tz, "interB", gfx.INK, q)
        for j, ln in enumerate(E.wrap(it["note"], rw - 90, 19 if sh else 21, "inter")[:2]): text(c, ln, rx + 70, y + rh * .40 + (28 if sh else 30) + j * (24 if sh else 26), 19 if sh else 21, "inter", gfx.MUTED, q)
        text(c, f'{it["over"]} ov · {it["score"]}', rx + rw - 14, y + 30, 18, "monoSB", gfx.MUTED, q, "r")
    if s.get("footnote"):
        for j, ln in enumerate(E.wrap(s["footnote"], l["x1"] - l["x0"], 17, "mono")[:3]): text(c, ln, l["x0"], bot + 62 + j * 24, 17, "mono", gfx.MUTED, eo(prog(t, D * .5, D * .5 + .6)))


def sc_overstrip(c, g, t, D, s):
    LK.header(c, g, t, D, _hd(s)); l = _L(g); sh = g.fmt == "short"; ov = s["overs"]; n = len(ov); rows = 3 if sh else 1; per = math.ceil(n / rows)
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
    E.SCENES.update({"wicketmap": sc_wicketmap, "overstrip": sc_overstrip}); install_photo(engine, looks)


# ---------------------------------------------------------------- photo scenes (owner-supplied photos, data/licensed): photohero, photocard, photovs, photostand, photopoll
import os
ROOT = os.path.dirname(os.path.abspath(__file__)); _PI = {}


def _pimg(path):
    if path not in _PI: _PI[path] = skia.Image.open(path if os.path.isabs(path) else os.path.join(ROOT, path))
    return _PI[path]


def draw_photo(c, path, x, y, w, h, a=1.0, r=0, crop=None, rot=0, shadow=False):
    """Photo covering the w x h box (centre-cropped, or a crop box (x0, y0, x1, y1) in image pixels), rounded corners r, optional tilt."""
    im = _pimg(path); iw, ih = im.width(), im.height()
    if crop is None:
        k = max(w / iw, h / ih); sw, sh_ = w / k, h / k; crop = ((iw - sw) / 2, (ih - sh_) / 2, (iw + sw) / 2, (ih + sh_) / 2)
    c.save(); c.translate(x + w / 2, y + h / 2); c.rotate(rot); c.translate(-w / 2, -h / 2)
    if shadow: c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(0, 14, w, h), r, r), paint((0, 0, 0), .28 * a, blur=24))
    c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(0, 0, w, h), r, r), doAntiAlias=True)
    c.drawImageRect(im, skia.Rect.MakeLTRB(*crop), skia.Rect.MakeXYWH(0, 0, w, h), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear), paint((255, 255, 255), a))
    c.restore()


def draw_cut(c, path, cx, bottom, hh, a=1.0, rot=0):
    """A transparent cut-out standing on y=bottom, hh tall, centred on cx."""
    im = _pimg(path); k = hh / im.height(); ww = im.width() * k
    c.save(); c.translate(cx, bottom); c.rotate(rot); c.drawImageRect(im, skia.Rect.MakeXYWH(0, 0, im.width(), im.height()), skia.Rect.MakeXYWH(-ww / 2, -hh, ww, hh), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear), paint((255, 255, 255), a)); c.restore()


def _tag(c, x, y, t_, a, size=26, fill=None):
    fill = fill or LK.RED; wd = twidth(t_, size, "monoSB", 1) + 36
    rrect(c, x, y, wd, size + 22, 8, fill, a); text(c, t_, x + 18, y + size + 6, size, "monoSB", (255, 255, 255), a, track=1); return wd


def _disc(c, cx, cy, R, a, ink=False):
    c.drawCircle(cx, cy, R, paint((225, 222, 212) if ink else (255, 232, 235), a)); c.drawCircle(cx, cy, R, paint(gfx.INK if ink else LK.RED, a, stroke=6))


def sc_photohero(c, g, t, D, s):
    sh = g.fmt == "short"; W, H = g.W, g.H; q = eo(prog(t, .0, .5)); qb = eback(prog(t, .1, .8)); x0 = 80 if sh else 140
    text(c, s["kicker"], x0, 260 if sh else 330, 26, "monoSB", LK.RED, q, track=2)
    y = 380 if sh else 450
    for k, ln in enumerate(s["lines"]):
        z = E.fit(ln["t"], (W - 2 * x0) if sh else 860, (112 if k == 0 else 150) if sh else 104, "interB", -2); qq = eo(prog(t, .1 + .15 * k, .55 + .15 * k))
        text(c, ln["t"], x0, y + (k * 130 if sh else k * 120), z, "interB", LK.RED if ln.get("c") == "gold" else gfx.INK, qq, track=-2)
    cx, cy, R = (W / 2, 1210, 450) if sh else (1380, 450, 320)
    _disc(c, cx, cy, R * (.8 + .2 * qb), clamp(qb)); draw_cut(c, s["img"], cx, cy + R * .86, R * 1.72 * (.9 + .1 * qb), clamp(qb))
    if s.get("sub"):
        for j, ln in enumerate(s["sub"][:2]): text(c, ln, x0, (1740 + j * 62) if sh else (760 + j * 56), 40 if j == 0 else 30, "interB" if j == 0 else "mono", gfx.INK if j == 0 else gfx.MUTED, eo(prog(t, D * .35, D * .35 + .6)))


def sc_photocard(c, g, t, D, s):
    sh = g.fmt == "short"; W, H = g.W, g.H; q = eo(prog(t, .0, .45)); x0 = 80 if sh else 140
    text(c, s["kicker"], x0, 250 if sh else 150, 28 if sh else 26, "monoSB", LK.RED, q, track=2)
    if sh: text(c, s["title"], x0, 330 + 100, 130, "interB", gfx.INK, q, track=-2)
    pw, ph = (920, 613) if sh else (1000, 667); px, py = (80, 540) if sh else (120, 230); qa = eo(prog(t, .1, .6))
    draw_photo(c, s["img"], px, py + (1 - qa) * 40, pw, ph, qa, 22, crop=s.get("crop_short" if sh else "crop_long"), rot=-1.6 if sh else -1.4, shadow=True)
    _tag(c, px + 40, py + 30, s["tag"], qa)
    if sh:
        text(c, s["name"], x0, 1310, E.fit(s["name"], 920, 78, "interB", -1), "interB", gfx.INK, eo(prog(t, .5, 1.0)))
        text(c, s["mono"], x0, 1420, E.fit(s["mono"], 920, 30, "monoSB", 1), "monoSB", LK.RED, eo(prog(t, .6, 1.1)), track=1); cl = E.wrap(s["caption"], 920, 34, "interB")[:2]
        for j, ln in enumerate(cl): text(c, ln, x0, 1478 + 42 * j, 34, "interB", gfx.INK, eo(prog(t, .7, 1.2)))
        cy0 = 1540 + 42 * len(cl)
        rrect(c, 80, cy0, 250, 120, 18, (255, 255, 255), eo(prog(t, .8, 1.3)), stroke=4, scol=gfx.INK, sa=1); text(c, s["chip"], 205, cy0 + 80, 78, "interB", gfx.INK, eo(prog(t, .8, 1.3)), "c")
        text(c, s.get("chip_sub", ""), 360, cy0 + 60, E.fit(s.get("chip_sub", ""), 640, 26, "monoSB", 1), "monoSB", gfx.MUTED, eo(prog(t, .8, 1.3)), track=1)
    else:
        text(c, s["name"], 1260, 440, E.fit(s["name"], 560, 84, "interB", -1), "interB", LK.RED, eo(prog(t, .5, 1.0)))
        text(c, s["mono"], 1260, 560, E.fit(s["mono"], 520, 28, "monoSB", 1), "monoSB", gfx.INK, eo(prog(t, .6, 1.1)), track=1)
        for j, ln in enumerate(E.wrap(s["caption"], 520, 28, "interB")[:3]): text(c, ln, 1260, 620 + 40 * j, 28, "interB", gfx.MUTED, eo(prog(t, .7, 1.2)))
        rrect(c, 1260, 720, 230, 110, 16, (255, 255, 255), eo(prog(t, .8, 1.3)), stroke=4, scol=gfx.INK, sa=1); text(c, s["chip"], 1375, 800, 70, "interB", gfx.INK, eo(prog(t, .8, 1.3)), "c")


def sc_photovs(c, g, t, D, s):
    sh = g.fmt == "short"; W, H = g.W, g.H; q = eo(prog(t, .0, .45)); x0 = 80 if sh else 140
    text(c, s["kicker"], x0, 250 if sh else 130, 26, "monoSB", LK.RED, q, track=2)
    if sh:
        for k, ln in enumerate(s["lines"]): text(c, ln["t"], x0, 330 + 110 * k, 100, "interB", LK.RED if ln.get("c") == "gold" else gfx.INK, eo(prog(t, .05 + .1 * k, .5 + .1 * k)))
    else: text(c, " ".join(ln["t"] for ln in s["lines"]), x0, 195, 70, "interB", gfx.INK, eo(prog(t, .05, .5)))
    items = s["items"]
    for k, it in enumerate(items):
        qb = eback(prog(t, .2 + .25 * k, .9 + .25 * k)); cx = (290 + 500 * k) if sh else (560 + 800 * k); R = 240 if sh else 190; cy = 880 if sh else 540
        ink = it.get("ink", k == 0); _disc(c, cx, cy, R * (.8 + .2 * qb), clamp(qb), ink)
        draw_cut(c, it["img"], cx, cy + R - 4 + (14 if sh else 20), (it["h"] * R / 240 if sh else it.get("h_long", it["h"] * R / 190)) * (.9 + .1 * qb), clamp(qb))
        by = cy + R + 30; rrect(c, cx - 230 if sh else cx - 200, by, 460 if sh else 400, 100 if sh else 80, 12, gfx.INK if ink else LK.RED, clamp(qb)); text(c, it["ttl"], cx, by + (65 if sh else 54), 38 if sh else 32, "interB", (255, 255, 255), clamp(qb), "c")
        text(c, it["big"], cx, by + (270 if sh else 220), 170 if sh else 130, "interB", gfx.INK if ink else LK.RED, eo(prog(t, .6 + .25 * k, 1.2 + .25 * k)), "c"); text(c, it["sub"], cx, by + (325 if sh else 270), 24 if sh else 22, "monoSB", gfx.MUTED, eo(prog(t, .8 + .25 * k, 1.4 + .25 * k)), "c")
    if s.get("foot") and sh:
        for j, ln in enumerate(s["foot"][:2]): text(c, ln, x0, 1700 + 60 * j, 38 if j == 0 else 26, "interB" if j == 0 else "mono", gfx.INK if j == 0 else gfx.MUTED, eo(prog(t, D * .5, D * .5 + .6)))


def sc_photostand(c, g, t, D, s):
    """Two photo cards (stacked on vertical, side by side on long) with the big number over each, and a chip row."""
    sh = g.fmt == "short"; W, H = g.W, g.H; q = eo(prog(t, .0, .45)); x0 = 80 if sh else 140
    text(c, s["kicker"], x0, 250 if sh else 130, 26, "monoSB", LK.RED, q, track=2); text(c, s["title"], x0, 340 if sh else 200, 96 if sh else 70, "interB", gfx.INK, eo(prog(t, .05, .5)), track=-2)
    for k, it in enumerate(s["items"]):
        qa = eo(prog(t, .15 + .3 * k, .75 + .3 * k)); pw, ph = (920, 520) if sh else (780, 520); px, py = (80, 430 + k * 560) if sh else (140 + k * 830, 270)
        draw_photo(c, it["img"], px, py + (1 - qa) * 40, pw, ph, qa, 22, crop=it.get("crop"), rot=(-1 if k == 0 else 1) * (1.0 if sh else .8), shadow=True)
        rrect(c, px + 24, py + ph - 176, 430, 152, 14, (20, 20, 22), .84 * qa); text(c, it["name"], px + 44, py + ph - 140, 22, "monoSB", (255, 214, 0), qa, track=1); text(c, it["big"], px + 44, py + ph - 48, E.fit(it["big"], 382, 100, "interB"), "interB", (255, 255, 255), qa)
    ya = (1650 if sh else 840)
    for j, (v, lb) in enumerate(s.get("chips", [])):
        cw = (920 - 3 * 18) / 4 if sh else (1640 - 3 * 18) / 4; cx_ = x0 + j * (cw + 18); qq = eo(prog(t, D * .45 + .12 * j, D * .45 + .6 + .12 * j))
        rrect(c, cx_, ya, cw, 150, 14, (255, 255, 255), qq, stroke=3, scol=LK.RED if j else gfx.INK, sa=qq); text(c, v, cx_ + cw / 2, ya + 80, 80, "interB", LK.RED if j else gfx.INK, qq, "c"); text(c, lb, cx_ + cw / 2, ya + 125, 22, "monoSB", gfx.MUTED, qq, "c")


def sc_photopoll(c, g, t, D, s):
    sh = g.fmt == "short"; W, H = g.W, g.H; q = eo(prog(t, .0, .45)); x0 = 80 if sh else 140
    text(c, s["kicker"], x0, 250 if sh else 130, 26, "monoSB", LK.RED, q, track=2); text(c, "Who won", x0, 330 + 40 if sh else 220, 120 if sh else 80, "interB", gfx.INK, q, track=-2); text(c, "day one?", x0, 455 + 40 if sh else 300, 120 if sh else 80, "interB", LK.RED, q, track=-2)
    items = s["items"]; n = len(items)
    for i, it in enumerate(items):
        st = D * (.1 + .5 * i / n); qq = eo(prog(t, st, st + .5)); hl = it.get("c") == "gold"
        if sh: y = 740 + i * 330; w_, h_ = 920, 290; x_ = 80
        else: y = 400 + i * 190; w_, h_ = 1640, 170; x_ = x0
        rrect(c, x_, y + (1 - qq) * 30, w_, h_, 24, (255, 255, 255), qq, stroke=5, scol=LK.RED if hl else LINE_, sa=qq)
        text(c, str(i + 1), x_ + 40, y + h_ * .72, 130 if sh else 100, "interB", LK.RED, qq)
        draw_photo(c, it["img"], x_ + w_ - (230 if sh else 190), y + 20, (190 if sh else 130), (250 if sh else 130), qq, 95 if sh else 65, crop=(it["crop_short"] if sh else it["crop_long"]))
        text(c, it["h"], x_ + 190, y + h_ * .5, 70 if sh else 54, "interB", gfx.INK, qq); text(c, it["d"], x_ + 190, y + h_ * .5 + 56, E.fit(it["d"], (w_ - 460) if sh else 800, 30, "interB", 0), "interB", gfx.MUTED, qq)


LINE_ = (222, 220, 212)


def install_photo(engine, looks):
    engine.SCENES.update({"photohero": sc_photohero, "photocard": sc_photocard, "photovs": sc_photovs, "photostand": sc_photostand, "photopoll": sc_photopoll})
