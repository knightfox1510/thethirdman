"""The Third Man video engine.
Spec-driven renderer for long-form (16:9) and Shorts (9:16) videos with word-synced captions,
subtitles, an animated logo outro and cover images.

usage:
  engine.py build  specs/<slug>.json [long|short|both]   full pipeline
  engine.py stills specs/<slug>.json long|short           preview sheet only (needs voice done)
  engine.py scene  specs/<slug>.json long|short <i>       (internal) render one scene
  engine.py outro  long|short                             render the logo outro clip
  engine.py thumb  specs/<slug>.json                      cover images only
"""
import os, sys, json, math, hashlib, base64, subprocess, urllib.request
import numpy as np, skia

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import gfx
from gfx import (text, rrect, paint, prog, eo, eio, eback, lerp, clamp, twidth,
                 INK, MUTED, GOLD, BLUE, RED, PANEL, LINE, BG, ORANGE)

GREEN = (70, 200, 120)
COL = {"ink": INK, "gold": GOLD, "blue": BLUE, "red": RED, "orange": ORANGE, "muted": MUTED, "green": GREEN}
FPS = 30
XI_KEY = os.environ.get("XI_KEY", "")
VOICE = "siw1N9V8LmYeEWKyWBxv"  # Ruhaan
TEMPO = {"long": 1.04, "short": 1.07}
SHOW = {"सचिन": "Sachin", "तेंदुलकर": "Tendulkar", "शोएब": "Shoaib", "अख़्तर": "Akhtar", "मुंबई": "Mumbai",
        "शारजाह": "Sharjah", "हार्दिक": "Hardik", "पंड्या": "Pandya", "अर्शदीप": "Arshdeep", "सिंह": "Singh",
        "बुमराह": "Bumrah", "जसप्रीत": "Jasprit", "धोनी": "Dhoni", "महेंद्र": "Mahendra", "कोहली": "Kohli", "विराट": "Virat",
        "रोहित": "Rohit", "शर्मा": "Sharma", "श्रेयस": "Shreyas", "अय्यर": "Iyer", "उमरान": "Umran", "मलिक": "Malik",
        "मयंक": "Mayank", "यादव": "Yadav", "जवागल": "Javagal", "श्रीनाथ": "Srinath", "गांगुली": "Ganguly",
        "सौरव": "Sourav", "द्रविड़": "Dravid", "राहुल": "Rahul", "कुंबले": "Kumble", "युवराज": "Yuvraj",
        "गंभीर": "Gambhir", "गौतम": "Gautam", "सेहवाग": "Sehwag", "इरफ़ान": "Irfan", "पठान": "Pathan",
        "रैना": "Raina", "जडेजा": "Jadeja", "अश्विन": "Ashwin", "शमी": "Shami", "सिराज": "Siraj", "पंजाब": "Punjab",
        "अभिषेक": "Abhishek", "वैभव": "Vaibhav", "सूर्यवंशी": "Sooryavanshi", "ईशांत": "Ishant", "वरुण": "Varun",
        "आरोन": "Aaron", "नवदीप": "Navdeep", "सैनी": "Saini", "जहीर": "Zaheer", "ख़ान": "Khan", "कपिल": "Kapil", "देव": "Dev", "शुभमन": "Shubman", "गिल": "Gill", "तिलक": "Tilak", "वर्मा": "Varma", "भुवनेश्वर": "Bhuvneshwar", "कुमार": "Kumar", "क्रुणाल": "Krunal"}


THEME_KEYS = ("INK", "MUTED", "GOLD", "BLUE", "RED", "PANEL", "LINE", "BG", "ORANGE")


def apply_theme(name):
    gfx.apply_theme(name)
    g = globals()
    for k in THEME_KEYS:
        g[k] = getattr(gfx, k)
    COL.update({"ink": INK, "gold": GOLD, "blue": BLUE, "red": RED, "orange": ORANGE, "muted": MUTED})


def C(x):
    if x is None: return INK
    return COL.get(x, INK) if isinstance(x, str) else tuple(x)


# ------------------------------------------------------------------ geometry
class G:
    def __init__(self, fmt):
        self.fmt = fmt
        if fmt == "long":
            self.W, self.H = 1920, 1080
            self.x0, self.x1, self.top, self.bot = 140, 1780, 330, 980
            self.hx, self.hy, self.hs = 120, 230, 96
        else:
            self.W, self.H = 1080, 1920
            # no burned-in captions any more: the content block sits in the middle of the screen,
            # clear of the Shorts/Reels UI at the bottom (~350 px)
            self.x0, self.x1, self.top, self.bot = 80, 1000, 660, 1520
            self.hx, self.hy, self.hs = 80, 560, 100
        self.cx = (self.x0 + self.x1) / 2
        self.cw = self.x1 - self.x0
        self.cy = (self.top + self.bot) / 2


def fit(s, maxw, size, tf, track=0):
    while size > 10 and twidth(s, size, tf, track) > maxw:
        size *= .96
    return size


def wrap(s, maxw, size, tf):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if cur and twidth(t, size, tf) > maxw:
            lines.append(cur); cur = w
        else:
            cur = t
    if cur: lines.append(cur)
    return lines


def rv(i, n, D, a=.08, b=.68):
    return D * (a + (b - a) * (i / max(1, n - 1) if n > 1 else 0))


def at(item, i, n, D, a=.08, b=.68):
    if isinstance(item, dict):
        if "_ts" in item: return item["_ts"]
        if "at" in item: return item["at"] * D
    return rv(i, n, D, a, b)


# ---- auto-cue: reveal each item when the narrator says its key word
import re
STOP = {"THE", "AND", "FOR", "WITH", "OFF", "FROM", "THAT", "THIS", "WAS", "ARE", "HIS", "HER", "ITS", "OUT", "NOT", "BUT",
        "HAS", "HAD", "YOU", "ALL", "CAN", "OUR", "BALL", "BALLS", "OVER", "OVERS", "RUNS", "RATE", "IPL", "INDIA", "TEAM"}
CUE_FIELDS = {"lines": ("t",), "items": ("label", "h"), "tiles": ("l", "v"), "events": ("t", "y"),
              "balls": ("n", "label"), "marks": ("l",), "shots": ("label",)}


def _norm(w):
    return re.sub(r"[^A-Z]", "", w.upper())


def autocue(s, words, lead):
    if s.get("_cued"): return
    s["_cued"] = True
    W = [(_norm(w["w"]), lead + w["s"]) for w in words]
    ptr = 0
    order = []
    if s.get("type") == "swap":
        order = [("left", s["left"], ("name",)), ("right", s["right"], ("name",))]
    for key, fields in CUE_FIELDS.items():
        lst = s.get(key)
        if not isinstance(lst, list): continue
        for k, it in enumerate(lst):
            if isinstance(it, str):
                lst[k] = it = {"t": it} if key == "lines" else {"h": it}
            order.append((key, it, fields))
    for key, it, fields in order:
        toks = []
        for f in fields:
            toks += [t for t in re.findall(r"[A-Za-z]{3,}", str(it.get(f, ""))) if t.upper() not in STOP]
        toks = [t.upper() for t in toks]
        for j in range(ptr, len(W)):
            w = W[j][0]
            if w and any(w == t or (len(t) >= 5 and len(w) >= 5 and (w.startswith(t[:5]) or t.startswith(w[:5]))) for t in toks):
                it["_ts"] = max(0.0, W[j][1] - .12); ptr = j + 1
                break


def head(c, g, t, s):
    h = s.get("head")
    if not h: return
    p = eo(prog(t, 0, .6)); off = (1 - p) * 30
    size = fit(h["t"], g.cw - 40, g.hs, "bebas", 2)
    c.drawRect(skia.Rect.MakeXYWH(g.hx, g.hy - size * .74 + off, 8, size * .76), paint(GOLD, p))
    text(c, h["t"], g.hx + 28, g.hy + off, size, "bebas", INK, p, track=2)
    if h.get("sub"):
        ss = fit(h["sub"], g.cw - 40, 26, "interSB", 4)
        text(c, h["sub"], g.hx + 32, g.hy + 44 + off, ss, "interSB", MUTED, p, track=4)


# ------------------------------------------------------------------ scene types
def sc_title(c, g, t, D, s, big=150):
    lines = s["lines"]; n = len(lines)
    sizes = []
    for ln in lines:
        tt = ln["t"] if isinstance(ln, dict) else ln
        sizes.append(fit(tt, g.cw, s.get("size", big), "bebas", 2))
    lh = [z * 1.0 for z in sizes]
    total = sum(lh) + (60 if s.get("kicker") else 0)
    y = g.cy - total / 2 + (40 if s.get("kicker") else 0) + (30 if s.get("head") else 0)
    if s.get("kicker"):
        k0 = at(lines[0], 0, n, D, .02, s.get("spread", .45)) if lines else 0
        text(c, s["kicker"], g.cx, y - 10, 30, "interB", GOLD, eo(prog(t, max(0, k0 - .3), k0 + .2)), "c", track=8)
        y += 50
    for i, ln in enumerate(lines):
        tt = ln["t"] if isinstance(ln, dict) else ln
        cc = C(ln.get("c")) if isinstance(ln, dict) else INK
        st = at(ln, i, n, D, .02, s.get("spread", .45))
        p = eo(prog(t, st, st + .5))
        y += lh[i] * .86
        text(c, tt, g.cx, y + (1 - p) * 40, sizes[i], "bebas", cc, p, "c", track=2, glow=12 if cc == GOLD else 0)
        y += lh[i] * .14
    if s.get("sub"):
        p = eo(prog(t, D * s.get("subat", .6), D * s.get("subat", .6) + .6))
        sz = 30 if g.fmt == "long" else 32
        for j, l in enumerate(wrap(s["sub"], g.cw - 80, sz, "interSB")):
            text(c, l, g.cx, y + 70 + j * sz * 1.35, sz, "interSB", MUTED, p, "c")


def sc_statement(c, g, t, D, s):
    sc_title(c, g, t, D, s, big=170)


def sc_bignum(c, g, t, D, s):
    head(c, g, t, s)
    v0, v1, dec = s.get("from", 0), s["value"], s.get("dec", 0)
    a = s.get("count_at", .12)
    p = eo(prog(t, D * a, D * a + .5))
    v = lerp(v0, v1, eio(prog(t, D * a, D * a + s.get("count_dur", 1.4))))
    sv = f"{s.get('prefix', '')}{v:,.{dec}f}{s.get('suffix', '')}" if s.get("comma", True) else f"{s.get('prefix', '')}{v:.{dec}f}{s.get('suffix', '')}"
    final = f"{s.get('prefix', '')}{v1:,.{dec}f}{s.get('suffix', '')}"
    size = fit(final, g.cw, 330 if g.fmt == "long" else 300, "bebas")
    y = g.cy + size * .3 + (20 if s.get("head") else 0)
    cc = C(s.get("color", "gold"))
    if gfx.THEME == "scoreboard" and p > 0:
        x = g.cx - twidth(sv, size, "bebas") / 2
        for ch in sv:
            w_ = twidth(ch, size, "bebas")
            if ch not in ".,*+ ":
                rrect(c, x - size * .04, y - size * .80, w_ + size * .08, size * .92, 6, PANEL, p)
                c.drawRect(skia.Rect.MakeXYWH(x - size * .04, y - size * .35, w_ + size * .08, 3), paint(BG, p))
            x += w_
    text(c, sv, g.cx, y, size, "bebas", cc, p, "c", glow=22)
    if s.get("label"):
        ls = fit(s["label"], g.cw, 40, "interB", 8)
        text(c, s["label"], g.cx, y + 80, ls, "interB", INK, p, "c", track=8)
    if s.get("note"):
        pn = eo(prog(t, D * .55, D * .55 + .6))
        for j, l in enumerate(wrap(s["note"], g.cw - 60, 28, "interSB")):
            text(c, l, g.cx, y + 140 + j * 38, 28, "interSB", MUTED, pn, "c")


def sc_bars(c, g, t, D, s):
    head(c, g, t, s)
    items = s["items"]; n = len(items)
    mx = s.get("max") or max(it["value"] for it in items) * 1.12
    dec = s.get("dec", 1); unit = s.get("unit", "")
    top = g.top + 20; avail = g.bot - top - (60 if s.get("note") else 0)
    slot = min(avail / n, 190 if g.fmt == "long" else 210)
    bh = slot * .42; lab = 26 if g.fmt == "long" else 28
    vw = 230 if g.fmt == "long" else 200
    bw = g.cw - vw
    for i, it in enumerate(items):
        st = at(it, i, n, D, .06, s.get("spread", .6))
        p = eo(prog(t, st, st + 1.0)); a = prog(t, st, st + .3)
        y = top + i * slot
        lx = g.x0
        if it.get("team"): lx += team_chip(c, it["team"], g.x0, y + lab - lab * 1.05, lab * 1.3, a) + 14
        text(c, it["label"], lx, y + lab, fit(it["label"], g.cw - (lx - g.x0), lab, "interB", 4), "interB", MUTED, a, track=4)
        c.drawRect(skia.Rect.MakeXYWH(g.x0, y + lab + 14, bw, bh), paint(LINE, .35 * a))
        w = bw * clamp(it["value"] / mx) * p
        if it.get("team") and not it.get("color"): it["color"] = "team:" + it["team"]
        rrect(c, g.x0, y + lab + 14, w, bh, 8, C(it.get("color")), a)
        vs = it.get("text") or f"{it['value'] * p:,.{dec}f}{unit}"
        if it.get("text") and p < 1: vs = f"{it['value'] * p:,.{dec}f}{unit}"
        text(c, vs, g.x0 + w + 20, y + lab + 14 + bh * .82, bh * 1.05, "bebas", C(it.get("color")), a)
    if s.get("note"):
        pn = eo(prog(t, D * .7, D * .7 + .6))
        for j, l in enumerate(wrap(s["note"], g.cw, 26, "interSB")):
            text(c, l, g.x0, g.bot - 10 + j * 34, 26, "interSB", MUTED, pn)


def sc_compare(c, g, t, D, s):
    head(c, g, t, s)
    A, B, rows = s["a"], s["b"], s["rows"]; n = len(rows)
    ca = C(A.get("color") or ("team:" + A["team"] if A.get("team") else "blue"))
    cb = C(B.get("color") or ("team:" + B["team"] if B.get("team") else "gold"))
    top = g.top + 10
    p0 = eo(prog(t, 0, .6))
    xa, xb = g.x0 + g.cw * .17, g.x1 - g.cw * .17
    ns = 60 if g.fmt == "long" else 56
    text(c, A["name"], xa, top + 50, fit(A["name"], g.cw * .34, ns, "bebas", 1), "bebas", ca, p0, "c", track=1)
    text(c, B["name"], xb, top + 50, fit(B["name"], g.cw * .34, ns, "bebas", 1), "bebas", cb, p0, "c", track=1)
    if A.get("sub"): text(c, A["sub"], xa, top + 86, 22, "interB", MUTED, p0, "c", track=3)
    if B.get("sub"): text(c, B["sub"], xb, top + 86, 22, "interB", MUTED, p0, "c", track=3)
    rt = top + 130; slot = min((g.bot - rt) / n, 140)
    vs = 78 if g.fmt == "long" else 70
    for i, r in enumerate(rows):
        lab, av, bv = r[0], r[1], r[2]; win = r[3] if len(r) > 3 else None
        st = rv(i, n, D, .1, s.get("spread", .65))
        p = eo(prog(t, st, st + .5))
        y = rt + i * slot
        rrect(c, g.x0, y, g.cw, slot - 16, 14, PANEL, .75 * p)
        text(c, lab, g.cx, y + (slot - 16) / 2 + 9, fit(lab, g.cw * .3, 24, "interB", 3), "interB", MUTED, p, "c", track=3)
        for val, x, cc, side in [(av, xa, ca, "a"), (bv, xb, cb, "b")]:
            hl = win == side
            text(c, val, x, y + (slot - 16) / 2 + vs * .36, fit(val, g.cw * .3, vs, "bebas"), "bebas", cc if hl or not win else MUTED, p, "c", glow=10 if hl else 0)
        if win:
            x = (xa + g.cx) / 2 - 40 if win == "a" else (xb + g.cx) / 2 + 40
            c.drawCircle(x, y + (slot - 16) / 2, 8 * p, paint(ca if win == "a" else cb, p))


def sc_list(c, g, t, D, s):
    head(c, g, t, s)
    items = s["items"]; n = len(items)
    top = g.top + 10
    cols = 2 if (g.fmt == "long" and n >= 4) else 1
    rows = math.ceil(n / cols)
    gap = 22
    cw = (g.cw - gap * (cols - 1)) / cols
    ch = min((g.bot - top - gap * (rows - 1)) / rows, 200)
    top += max(0, (g.bot - top - (rows * ch + (rows - 1) * gap)) / 2)
    for i, it in enumerate(items):
        h = it["h"] if isinstance(it, dict) else it
        d = it.get("d") if isinstance(it, dict) else None
        st = at(it, i, n, D, .06, s.get("spread", .7))
        p = eo(prog(t, st, st + .5))
        col, row = (i % cols, i // cols) if cols == 2 else (0, i)
        x = g.x0 + col * (cw + gap); y = top + row * (ch + gap) + (1 - p) * 30
        rrect(c, x, y, cw, ch, 16, PANEL, .85 * p, stroke=2, scol=LINE, sa=p)
        num = it.get("n", str(i + 1)) if isinstance(it, dict) else str(i + 1)
        text(c, num, x + 34, y + ch / 2 + 32, 90, "bebas", C(it.get("c", "gold")) if isinstance(it, dict) else GOLD, p)
        tx = x + 110; tw = cw - 140
        hs = fit(h, tw, 44 if g.fmt == "long" else 46, "oswald")
        if d:
            dl = wrap(d, tw, 24 if g.fmt == "long" else 27, "inter")[:2]
            block = hs + 10 + len(dl) * 32
            yy = y + (ch - block) / 2 + hs * .8
            text(c, h, tx, yy, hs, "oswald", INK, p)
            for j, l in enumerate(dl):
                text(c, l, tx, yy + 14 + (j + 1) * 32, 24 if g.fmt == "long" else 27, "inter", MUTED, p)
        else:
            text(c, h, tx, y + ch / 2 + hs * .35, hs, "oswald", INK, p)


def sc_timeline(c, g, t, D, s):
    head(c, g, t, s)
    ev = s["events"]; n = len(ev)
    if g.fmt == "long":
        x0, x1, ly = g.x0 + 60, g.x1 - 60, g.cy + 40
        pl = eio(prog(t, 0, D * .35))
        c.drawLine(x0, ly, lerp(x0, x1, pl), ly, paint(LINE, 1, stroke=4))
        for i, e in enumerate(ev):
            x = lerp(x0, x1, i / max(1, n - 1)); st = at(e, i, n, D, .05, s.get("spread", .7))
            p = eback(prog(t, st, st + .5)); a = clamp(prog(t, st, st + .3))
            hl = e.get("hl"); cc = C(e.get("c", "gold" if hl else "ink"))
            if hl: c.drawCircle(x, ly, 40 * a, paint(cc, .25 * a, blur=16))
            c.drawCircle(x, ly, (18 if hl else 13) * clamp(p, 0, 1.2), paint(cc, a))
            up = i % 2 == 0
            text(c, e["y"], x, ly + (-50 if up else 80), 52 if hl else 44, "bebas", cc if hl else INK, a, "c")
            lw = min((x1 - x0) / max(1, n - 1) * 1.15, 440)
            lines = wrap(e["t"], lw, 26, "interSB")[:3]
            wmax = max(twidth(l, 26, "interSB") for l in lines) if lines else 0
            lx = min(max(x, g.x0 + wmax / 2 - 40), g.x1 - wmax / 2 + 40)
            for j, l in enumerate(lines):
                yy = (ly - 100 - (len(lines) - 1 - j) * 32) if up else (ly + 124 + j * 32)
                text(c, l, lx, yy, 26, "interSB", MUTED, a, "c")
    else:
        lx, y0, y1 = g.x0 + 70, g.top + 20, g.bot - 20
        pl = eio(prog(t, 0, D * .35))
        c.drawLine(lx, y0, lx, lerp(y0, y1, pl), paint(LINE, 1, stroke=4))
        for i, e in enumerate(ev):
            y = lerp(y0, y1, i / max(1, n - 1)); st = at(e, i, n, D, .05, s.get("spread", .7))
            p = eback(prog(t, st, st + .5)); a = clamp(prog(t, st, st + .3))
            hl = e.get("hl"); cc = C(e.get("c", "gold" if hl else "ink"))
            c.drawCircle(lx, y, (18 if hl else 13) * clamp(p, 0, 1.2), paint(cc, a))
            text(c, e["y"], lx + 50, y + 18, 58 if hl else 50, "bebas", cc if hl else INK, a)
            for j, l in enumerate(wrap(e["t"], g.x1 - lx - 220, 26, "interSB")[:2]):
                text(c, l, lx + 200, y + 4 + j * 32, 26, "interSB", MUTED, a)


def sc_stats(c, g, t, D, s):
    head(c, g, t, s)
    tiles = s["tiles"]; n = len(tiles)
    cols = s.get("cols") or (min(n, 4) if g.fmt == "long" else (1 if n <= 3 else 2))
    rows = math.ceil(n / cols); gap = 24
    top = g.top + 20
    tw = (g.cw - gap * (cols - 1)) / cols
    th = min((g.bot - top - gap * (rows - 1)) / rows, 320 if g.fmt == "long" else 360)
    top += max(0, (g.bot - top - (rows * th + (rows - 1) * gap)) / 2)
    for i, tl in enumerate(tiles):
        st = at(tl, i, n, D, .06, s.get("spread", .6))
        p = eback(prog(t, st, st + .5)); a = clamp(prog(t, st, st + .3))
        col, row = i % cols, i // cols
        x = g.x0 + col * (tw + gap); y = top + row * (th + gap)
        c.save(); c.translate(x + tw / 2, y + th / 2); sc = clamp(.85 + .15 * p, 0, 1.1); c.scale(sc, sc)
        rrect(c, -tw / 2, -th / 2, tw, th, 18, PANEL, .85 * a, stroke=2, scol=C(tl.get("c", "gold")), sa=.6 * a)
        vsz = fit(tl["v"], tw - 40, min(150, th * .5), "bebas")
        text(c, tl["v"], 0, vsz * .18, vsz, "bebas", C(tl.get("c", "gold")), a, "c", glow=8)
        lz = 26 if g.fmt == "long" else 30
        for j, l in enumerate(wrap(tl["l"], tw - 40, lz, "interB")[:2]):
            text(c, l, 0, vsz * .18 + 50 + j * lz * 1.25, lz, "interB", MUTED, a, "c")
        c.restore()


def sc_scorecard(c, g, t, D, s):
    head(c, g, t, s)
    teams = s["teams"]
    gap = 30; top = g.top + 10
    if g.fmt == "long":
        pw, ph = (g.cw - gap) / 2, g.bot - top
        boxes = [(g.x0, top), (g.x0 + pw + gap, top)]
    else:
        pw, ph = g.cw, (g.bot - top - gap) / 2
        boxes = [(g.x0, top), (g.x0, top + ph + gap)]
    k = 0; total = sum(len(tm["gain"]) + len(tm["lose"]) for tm in teams)
    for (x, y), tm in zip(boxes, teams):
        cc = C(tm.get("color", "gold"))
        p0 = eo(prog(t, 0, .6))
        rrect(c, x, y, pw, ph, 20, PANEL, .85 * p0, stroke=2, scol=cc, sa=.7 * p0)
        text(c, tm["name"], x + 36, y + 70, fit(tm["name"], pw - 72, 64, "bebas"), "bebas", cc, p0, track=2)
        yy = y + (140 if g.fmt == "long" else 120)
        ls = 36 if g.fmt == "long" else 30
        for sign, lst, sc_ in [("+", tm["gain"], GREEN), ("–", tm["lose"], RED)]:
            for it in lst:
                st = rv(k, total, D, .08, .8); k += 1
                p = eo(prog(t, st, st + .4))
                lines = wrap(it, pw - 120, ls, "interSB")
                text(c, sign, x + 40, yy + ls * .9, ls * 1.6, "bebas", sc_, p)
                for j, l in enumerate(lines):
                    text(c, l, x + 84, yy + ls * .9 + j * ls * 1.25, ls, "interSB", INK, p)
                yy += len(lines) * ls * 1.25 + (16 if g.fmt == "long" else 10)


def sc_line(c, g, t, D, s):
    head(c, g, t, s)
    gx, gy = g.x0 + 70, g.top + 40
    gw, gh = g.cw - 70 - (150 if g.fmt == "long" else 40), g.bot - g.top - 120
    ymin, ymax = s.get("ymin", 0), s["ymax"]
    xs = [p[0] for se in s["series"] for p in se["points"]]
    xmin, xmax = s.get("xmin", min(xs)), s.get("xmax", max(xs))
    pa = eo(prog(t, 0, .6))
    c.drawLine(gx, gy + gh, gx + gw, gy + gh, paint(LINE, pa, stroke=3))
    for v in s.get("yticks", []):
        yy = gy + gh - (v - ymin) / (ymax - ymin) * gh
        c.drawLine(gx, yy, gx + gw, yy, paint(LINE, .3 * pa, stroke=1))
        text(c, str(v), gx - 14, yy + 8, 22, "interSB", MUTED, pa, "r")
    for xv, lab in s.get("xticks", []):
        xx = gx + (xv - xmin) / (xmax - xmin) * gw
        text(c, lab, xx, gy + gh + 40, 24, "interSB", MUTED, pa, "c")
    if s.get("ylabel"): text(c, s["ylabel"], gx, gy - 24, 22, "interB", MUTED, pa, track=4)
    for k_, se in enumerate(s["series"]):
        st = se.get("at", .08 + k_ * .25) * D
        pl = eio(prog(t, st, st + se.get("dur", .4) * D))
        pts = [(gx + (x - xmin) / (xmax - xmin) * gw, gy + gh - (y - ymin) / (ymax - ymin) * gh) for x, y in se["points"]]
        if pl <= 0: continue
        path = skia.Path(); path.moveTo(*pts[0])
        for q in pts[1:]: path.lineTo(*q)
        meas = skia.PathMeasure(path, False); L = meas.getLength()
        seg = skia.Path(); meas.getSegment(0, L * pl, seg, True)
        cc = C(se.get("color", "gold"))
        c.drawPath(seg, paint(cc, .3, stroke=14, blur=8)); c.drawPath(seg, paint(cc, 1, stroke=5))
        pos, _ = meas.getPosTan(L * pl)
        c.drawCircle(pos.x(), pos.y(), 9, paint(cc))
        if pl >= 1 and se.get("name"):
            text(c, se["name"], pts[-1][0] + 18, pts[-1][1] + 9, 26, "interB", cc, eo(prog(t, st + se.get("dur", .4) * D, st + se.get("dur", .4) * D + .4)))
    if s.get("note"):
        text(c, s["note"], gx + gw, gy - 24, 20, "inter", MUTED, pa, "r")


def sc_gauge(c, g, t, D, s):
    head(c, g, t, s)
    vmin, vmax = s.get("min", 120), s.get("max", 165)
    cx, cy = g.cx, g.top + (430 if g.fmt == "long" else 470)
    R = 330 if g.fmt == "long" else 380
    a0, sweep = 160, 220
    pa = eo(prog(t, 0, .6))
    rect = skia.Rect.MakeXYWH(cx - R, cy - R, 2 * R, 2 * R)
    c.drawArc(rect, a0, sweep, False, paint(LINE, pa, stroke=26))
    def ang(v): return a0 + sweep * clamp((v - vmin) / (vmax - vmin))
    for v in range(int(math.ceil(vmin / 10) * 10), int(vmax) + 1, 10):
        A = math.radians(ang(v))
        text(c, str(v), cx + (R - 70) * math.cos(A), cy + (R - 70) * math.sin(A) + 10, 28, "interB", MUTED, pa, "c")
    for k_, m in enumerate(s.get("marks", [])):
        st = at(m, k_, len(s["marks"]), D, .15, .55)
        p = eo(prog(t, st, st + .5))
        A = math.radians(ang(m["v"]))
        cc = C(m.get("c", "blue"))
        x1, y1 = cx + (R + 20) * math.cos(A), cy + (R + 20) * math.sin(A)
        c.drawLine(cx + (R - 30) * math.cos(A), cy + (R - 30) * math.sin(A), x1, y1, paint(cc, p, stroke=6))
        lx, ly = cx + (R + 60) * math.cos(A), cy + (R + 60) * math.sin(A)
        al = "r" if math.cos(A) < -.2 else ("l" if math.cos(A) > .2 else "c")
        text(c, m["l"], lx, ly, 26, "interB", cc, p, al)
    nv = lerp(vmin, s["value"], eio(prog(t, D * s.get("needle_at", .55), D * s.get("needle_at", .55) + 1.6)))
    A = math.radians(ang(nv))
    c.drawArc(rect, a0, ang(nv) - a0, False, paint(GOLD, pa, stroke=26))
    c.drawLine(cx, cy, cx + (R - 50) * math.cos(A), cy + (R - 50) * math.sin(A), paint(INK, pa, stroke=8))
    c.drawCircle(cx, cy, 22, paint(INK, pa))
    text(c, f"{nv:.0f}", cx, cy + 170, 150, "bebas", GOLD, pa, "c", glow=14)
    text(c, s.get("label", "KM/H"), cx, cy + 220, 28, "interB", MUTED, pa, "c", track=6)


def sc_over(c, g, t, D, s):
    head(c, g, t, s)
    balls = s["balls"]; n = len(balls)
    if g.fmt == "long":
        r = 92; ys = [g.cy + 30]; per = n
    else:
        r = 110; ys = [g.top + 220, g.top + 560]; per = 3
    for i, b in enumerate(balls):
        st = at(b, i, n, D, .08, s.get("spread", .8))
        p = eback(prog(t, st, st + .45)); a = clamp(prog(t, st, st + .25))
        row, col = divmod(i, per)
        span = g.cw / per
        x = g.x0 + span * (col + .5); y = ys[min(row, len(ys) - 1)]
        cc = C(b.get("c", "ink"))
        c.drawCircle(x, y, r, paint(PANEL, .9 * a)); c.drawCircle(x, y, r, paint(cc, a, stroke=4))
        rs = fit(b["r"], r * 1.5, 110, "bebas")
        c.save(); c.translate(x, y); sc = clamp(p, 0, 1.15); c.scale(sc, sc)
        text(c, b["r"], 0, rs * .35, rs, "bebas", cc, a, "c", glow=8 if b.get("c") == "gold" else 0)
        c.restore()
        text(c, f"BALL {i + 1}", x, y - r - 18, 20, "interB", MUTED, a, "c", track=3)
        for j, l in enumerate(wrap(b.get("n", ""), span - 20, 22, "interSB")[:3]):
            text(c, l, x, y + r + 40 + j * 28, 22, "interSB", MUTED, a, "c")


def sc_swap(c, g, t, D, s):
    head(c, g, t, s)
    L_, R_ = s["left"], s["right"]
    long = g.fmt == "long"
    cw = g.cw * (.40 if long else 1); ch = 330 if long else 300
    boxes = [(g.x0, g.cy - ch / 2), (g.x1 - cw, g.cy - ch / 2)] if long else [(g.x0, g.top), (g.x0, g.bot - ch)]
    for k_, (pl, (x, y)) in enumerate(zip([L_, R_], boxes)):
        st = pl.get("_ts", k_ * .2 * D)
        p = eo(prog(t, st, st + .6))
        cc = C(pl.get("color", "gold"))
        rrect(c, x, y + (1 - p) * 40, cw, ch, 22, PANEL, .9 * p, stroke=3, scol=cc, sa=p)
        ns = fit(pl["name"], cw - 60, 110, "bebas", 2)
        text(c, pl["name"], x + cw / 2, y + 130 + (1 - p) * 40, ns, "bebas", INK, p, "c", track=2)
        text(c, pl.get("role", ""), x + cw / 2, y + 180, 24, "interB", MUTED, p, "c", track=5)
        tt_ = max(pl.get("_ts", 0) + 1.0, D * .45 + k_ * .2)
        pm = eo(prog(t, tt_, tt_ + .6))
        fs = 64; wf, wt = twidth(pl["from"], fs, "bebas", 2), twidth(pl["to"], fs, "bebas", 2)
        tot = wf + wt + 110; x0_ = x + cw / 2 - tot / 2; yb = y + 265
        text(c, pl["from"], x0_, yb, fs, "bebas", MUTED, pm, track=2)
        ax0, ax1 = x0_ + wf + 22, x0_ + wf + 22 + 66 * pm
        c.drawLine(ax0, yb - 22, ax1, yb - 22, paint(cc, pm, stroke=6))
        ah = skia.Path(); ah.moveTo(ax1 + 14, yb - 22); ah.lineTo(ax1 - 4, yb - 36); ah.lineTo(ax1 - 4, yb - 8); ah.close()
        c.drawPath(ah, paint(cc, pm))
        text(c, pl["to"], x0_ + wf + 110, yb, fs, "bebas", cc, pm, track=2, glow=8)
    # crossing arrows
    pa0 = max(R_.get("_ts", D * .35), D * .35)
    pa = eio(prog(t, pa0, pa0 + 1.0))
    if pa > 0 and long:
        mx = g.cx
        for k_, (y0, y1, cc) in enumerate([(g.cy - 60, g.cy + 60, C(L_.get("color"))), (g.cy + 60, g.cy - 60, C(R_.get("color")))]):
            xa, xb = (g.x0 + cw + 30, g.x1 - cw - 30) if k_ == 0 else (g.x1 - cw - 30, g.x0 + cw + 30)
            path = skia.Path(); path.moveTo(xa, y0); path.cubicTo(mx, y0, mx, y1, xb, y1)
            meas = skia.PathMeasure(path, False); Lg = meas.getLength()
            seg = skia.Path(); meas.getSegment(0, Lg * pa, seg, True)
            c.drawPath(seg, paint(cc, 1, stroke=6))
            pos, tan = meas.getPosTan(Lg * pa)
            c.drawCircle(pos.x(), pos.y(), 10, paint(cc))
    elif pa > 0:
        y0, y1 = g.top + ch + 30, g.bot - ch - 30
        text(c, "⇅" if False else "SWAP", g.cx, (y0 + y1) / 2 + 30, 90, "bebas", GOLD, pa, "c", track=8, glow=10)
        c.drawLine(g.cx - 220, y0 + 10, g.cx - 220, lerp(y0 + 10, y1 - 10, pa), paint(C(L_.get("color")), 1, stroke=6))
        c.drawLine(g.cx + 220, y1 - 10, g.cx + 220, lerp(y1 - 10, y0 + 10, pa), paint(C(R_.get("color")), 1, stroke=6))


def sc_field(c, g, t, D, s):
    head(c, g, t, s)
    c.save()
    if g.fmt == "long":
        c.translate(1250, 600)
    else:
        c.translate(g.cx - 50, g.cy + 60); c.scale(.85, .85)
    gfx.field(c, 0, 0, eo(prog(t, 0, .6)), t, lambda f: f * D * s.get("ball", .75), D)
    c.restore()


def sc_cta(c, g, t, D, s):
    long = g.fmt == "long"
    gfx.logo_lockup(c, g.cx, 250 if long else 560, 110 if long else 120, eo(prog(t, 0, .5)), "c")
    lines = s["lines"]; y = (430 if long else 780)
    for i, ln in enumerate(lines):
        tt = ln["t"] if isinstance(ln, dict) else ln
        cc = C(ln.get("c")) if isinstance(ln, dict) else INK
        sz = fit(tt, g.cw, 150, "bebas", 2)
        p = eo(prog(t, .1 + i * .15, .6 + i * .15))
        y += sz * .9
        text(c, tt, g.cx, y + (1 - p) * 40, sz, "bebas", cc, p, "c", track=2, glow=12 if cc == GOLD else 0)
    pill = s.get("pill") or ("SUBSCRIBE" if long else "FULL BREAKDOWN ON THE CHANNEL")
    if long:
        p3 = eo(prog(t, 1.0, 1.6))
        text(c, s.get("ask", "TELL US IN THE COMMENTS"), g.cx, y + 80, 34, "interB", MUTED, p3, "c", track=8)
        y += 60
    p4 = eback(prog(t, 1.4, 2.0))
    if p4 > 0:
        w = twidth(pill, 40, "bebas", 3) + 90
        c.save(); c.translate(g.cx, y + 130); sc = clamp(p4, 0, 1.2) * (1 + .03 * math.sin(max(0, t - 2) * 5)); c.scale(sc, sc)
        rrect(c, -w / 2, -42, w, 84, 42, RED if long else GOLD, clamp(p4))
        text(c, pill, 0, 14, 40, "bebas", INK if long else BG, clamp(p4), "c", track=3)
        c.restore()


SCENES = {k[3:]: v for k, v in globals().items() if k.startswith("sc_")}


# ------------------------------------------------------------------ chrome + captions
def chrome(c, g, spec, T, total, last):
    a = 0 if last else 1
    if g.fmt == "long":
        tag, sub = spec.get("tag", "WHAT IF?"), spec.get("tagsub", "")
        tw = twidth(tag, 34, "bebas", 1.5) + 36
        rrect(c, 70, 58, tw, 44, 6, GOLD, a)
        text(c, tag, 70 + tw / 2, 92, 34, "bebas", BG, a, "c", track=1.5)
        text(c, sub, 70 + tw + 18, 91, 22, "interSB", INK, a * .85, track=3)
        gfx.logo_lockup(c, g.W - 70, 80, 52, a * .9, "r")
        c.drawRect(skia.Rect.MakeXYWH(0, g.H - 6, g.W, 6), paint(LINE, a * .5))
        c.drawRect(skia.Rect.MakeXYWH(0, g.H - 6, g.W * clamp(T / total), 6), paint(GOLD, a * .9))
    else:
        gfx.logo_lockup(c, 70, 150, 64, a)
        tag, sub = spec.get("tag", "WHAT IF?"), spec.get("tagsub", "")
        tw = twidth(tag, 34, "bebas", 1.5) + 36
        rrect(c, 70, 220, tw, 44, 6, GOLD, a)
        text(c, tag, 70 + tw / 2, 254, 34, "bebas", BG, a, "c", track=1.5)
        text(c, sub, 70 + tw + 18, 253, fit(sub, g.W - tw - 180, 22, "interSB", 3), "interSB", INK, a * .85, track=3)
        c.drawRect(skia.Rect.MakeXYWH(0, 0, g.W * clamp(T / total), 8), paint(GOLD, .9))


def cap_groups(words, maxc=16):
    out, cur = [], []
    for w in words:
        if cur and (sum(len(x["w"]) + 1 for x in cur) + len(w["w"]) > maxc or cur[-1]["w"][-1] in ".?,!"):
            out.append(cur); cur = []
        cur.append(w)
    if cur: out.append(cur)
    return out


def captions(c, g, t, grps):
    gi = None
    for i, gr in enumerate(grps):
        end = grps[i + 1][0]["s"] if i + 1 < len(grps) else gr[-1]["e"] + .4
        if gr[0]["s"] - .05 <= t < end: gi = i; break
    if gi is None: return
    gr = grps[gi]
    pop = eback(prog(t, gr[0]["s"] - .05, gr[0]["s"] + .12))
    ws = [x["w"].upper() for x in gr]
    size = fit(" ".join(ws), g.W - 200, 76, "interB")
    widths = [twidth(w, size, "interB") for w in ws]
    total = sum(widths) + 22 * (len(ws) - 1)
    x = g.W / 2 - total / 2; y = 1430
    c.save(); c.translate(g.W / 2, y); sc = .85 + .15 * clamp(pop, 0, 1.1); c.scale(sc, sc); c.translate(-g.W / 2, -y)
    f = skia.Font(gfx.TF["interB"], size)
    for w, wd, wo in zip(ws, widths, gr):
        active = wo["s"] <= t < wo["e"] + .05
        sp = paint(BG, .95, stroke=14); sp.setStrokeJoin(skia.Paint.kRound_Join)
        c.drawString(w, x, y, f, sp)
        c.drawString(w, x, y, f, paint(GOLD if active else INK))
        x += wd + 22
    c.restore()


# ------------------------------------------------------------------ voice
def tts(paras, outdir, fmt):
    os.makedirs(outdir, exist_ok=True)
    mpath = f"{outdir}/meta.json"
    old = json.load(open(mpath)) if os.path.exists(mpath) else []
    meta = []
    for i, p in enumerate(paras):
        h = hashlib.md5((p + VOICE + str(TEMPO[fmt])).encode()).hexdigest()
        if i < len(old) and old[i].get("hash") == h and os.path.exists(f"{outdir}/p{i}.mp3"):
            meta.append(old[i]); continue
        body = {"text": p, "model_id": "eleven_multilingual_v2",
                "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.3, "use_speaker_boost": True},
                "previous_text": paras[i - 1] if i else None, "next_text": paras[i + 1] if i + 1 < len(paras) else None}
        req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_192",
                                     data=json.dumps(body).encode(), headers={"xi-api-key": XI_KEY, "Content-Type": "application/json"})
        for attempt in range(3):
            try:
                d = json.load(urllib.request.urlopen(req, timeout=180)); break
            except Exception as e:
                if attempt == 2: raise
        raw = f"{outdir}/raw{i}.mp3"
        open(raw, "wb").write(base64.b64decode(d["audio_base64"]))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", f"atempo={TEMPO[fmt]}", "-b:a", "192k", f"{outdir}/p{i}.mp3"], check=True)
        al = d["alignment"]; words, cur, st, en = [], "", None, None
        for ch, s_, e_ in zip(al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]):
            if ch.isspace():
                if cur: words.append([cur, st, en]); cur = ""
                continue
            if not cur: st = s_
            cur += ch; en = e_
        if cur: words.append([cur, st, en])
        disp = []
        for w, s_, e_ in words:
            core = w.strip(".,?!:;\"'"); lead = w[:len(w) - len(w.lstrip(".,?!:;\"'"))]; tail = w[len(w.rstrip(".,?!:;\"'")):]
            core = SHOW.get(core, core)
            disp.append({"w": lead + core + tail, "s": s_ / TEMPO[fmt], "e": e_ / TEMPO[fmt]})
        dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{outdir}/p{i}.mp3"]))
        meta.append({"hash": h, "dur": dur, "words": disp})
        json.dump(meta + old[len(meta):], open(mpath, "w"), ensure_ascii=False)
    meta = [breathe(outdir, i, m, fmt) for i, m in enumerate(meta)]
    json.dump(meta, open(mpath, "w"), ensure_ascii=False)
    return meta


# ------------------------------------------------------------------ natural pauses
# ElevenLabs often runs sentences together (and atempo shortens pauses further), while every clip carries its own
# leading/trailing silence. breathe() rebuilds each paragraph's audio from the word timings: it trims the edges and
# makes sure every punctuation mark gets at least a natural pause, never touching pauses that are already long enough.
BREATH_V = 2
MIN_PAUSE = {"long": {".": .34, "!": .34, "?": .42, ":": .26, ";": .24, "—": .22, ",": .13},
             "short": {".": .26, "!": .26, "?": .32, ":": .2, ";": .18, "—": .16, ",": .1}}
EDGE = (.04, .10)   # silence kept before the first word / after the last word


def breathe(outdir, i, m, fmt):
    out = f"{outdir}/b{i}.wav"
    if m.get("bv") == BREATH_V and os.path.exists(out): return m
    raw_words = m.get("words_raw", m["words"]); raw_dur = m.get("dur_raw", m["dur"])
    pcm = subprocess.check_output(["ffmpeg", "-loglevel", "error", "-i", f"{outdir}/p{i}.mp3", "-f", "f32le", "-ac", "1", "-ar", "44100", "-"])
    a = np.frombuffer(pcm, np.float32); SR = 44100
    t0 = max(0.0, raw_words[0]["s"] - EDGE[0]); t1 = min(len(a) / SR, raw_words[-1]["e"] + EDGE[1])
    pieces, words, cur, shift = [], [], int(t0 * SR), -t0
    for k, w in enumerate(raw_words):
        words.append({"w": w["w"], "s": w["s"] + shift, "e": w["e"] + shift})
        if k + 1 < len(raw_words):
            nxt = raw_words[k + 1]; gap = nxt["s"] - w["e"]
            mark = w["w"].rstrip("\"'”’")[-1:] if w["w"] else ""
            need = MIN_PAUSE[fmt].get(mark, 0) - gap
            if need > .015:   # insert silence in the middle of the existing gap
                cut = int((w["e"] + gap / 2) * SR)
                pieces.append(a[cur:cut]); pieces.append(np.zeros(int(need * SR), np.float32)); cur = cut; shift += need
    pieces.append(a[cur:int(t1 * SR)])
    y = np.concatenate(pieces)
    import wave
    with wave.open(out, "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
    return dict(m, words=words, dur=len(y) / SR, words_raw=raw_words, dur_raw=raw_dur, bv=BREATH_V)


# scene-to-scene silence, chosen by how the previous paragraph ends (a sentence end breathes, a continuation flows)
SCENE_GAP = {"long": {".": .55, "!": .55, "?": .75, "default": .3}, "short": {".": .36, "!": .36, "?": .5, "default": .2}}


def plan(spec, fmt, base):
    meta = json.load(open(f"{base}/vo/meta.json"))
    n = len(meta)
    lead = [(.5 if fmt == "long" else .12)] + [(.12 if fmt == "long" else .08)] * (n - 1)
    tail = []
    for i in range(n - 1):
        last = meta[i]["words"][-1]["w"].rstrip("\"'”’")[-1:]
        want = SCENE_GAP[fmt].get(last, SCENE_GAP[fmt]["default"])
        edges = (meta[i]["dur"] - meta[i]["words"][-1]["e"]) + meta[i + 1]["words"][0]["s"]
        tail.append(max(.03, want - edges - lead[i + 1]))
    tail.append(2.4 if fmt == "long" else 1.8)
    if fmt == "long" and n > 1: lead[1] += STING
    durs = [round((l + m["dur"] + tl) * FPS) / FPS for l, m, tl in zip(lead, meta, tail)]
    starts = list(np.concatenate([[0], np.cumsum(durs)]))
    return meta, lead, durs, starts, float(starts[-1])


# ------------------------------------------------------------------ rendering
def setup(fmt):
    g = G(fmt); gfx.W, gfx.H = g.W, g.H
    return g


STING = 3.2
INTRO_NAMES = ["fieldmap", "stumps", "flip", "kinetic"]
INTRO_LOG = os.path.join(ROOT, "intro_log.json")


def pick_intro(spec):
    """Rotation rule: keep a video's intro once assigned; otherwise least-recently-used, never the same as the last one;
    Scoreboard videos prefer the flip intro when it isn't the last one used."""
    if spec.get("intro") in INTRO_NAMES: return spec["intro"]
    log = json.load(open(INTRO_LOG)) if os.path.exists(INTRO_LOG) else {"order": [], "assigned": {}}
    if spec["slug"] in log["assigned"]: return log["assigned"][spec["slug"]]
    order = log["order"]; last = order[-1] if order else None
    def age(n): return max([i for i, x in enumerate(order) if x == n], default=-1)
    cands = [n for n in INTRO_NAMES if n != last]
    if spec.get("theme") == "scoreboard" and "flip" in cands: pick = "flip"
    else: pick = min(cands, key=age)
    order.append(pick); log["assigned"][spec["slug"]] = pick
    json.dump(log, open(INTRO_LOG, "w"), indent=1)
    return pick


def draw(c, g, spec, scenes, i, lt, D, T, total, frame, lead, grps, words=None):
    s = scenes[i]["scene"]
    if words is not None: autocue(s, words, lead)
    sting = g.fmt == "long" and i == 1
    if sting and lt < STING:
        import intros
        gfx.background(c, T)
        c.saveLayerAlpha(None, int(255 * clamp((STING - lt) / .3)))
        intros.INTROS[spec.get("_intro", "fieldmap")][0](c, g, lt)
        c.restore(); return
    gfx.background(c, T)
    last = i == len(scenes) - 1
    t0 = STING if sting else 0
    a = min(clamp((lt - t0) / .25) if i > 0 else 1, clamp((D - lt) / .25) if not last else 1)
    c.saveLayerAlpha(None, int(255 * a))
    SCENES[s["type"]](c, g, lt, D, s)
    c.restore()
    if i > 0:
        ca = clamp((lt - t0) / .5) if i == 1 else 1
        c.saveLayerAlpha(None, int(255 * ca)); chrome(c, g, spec, T, total, last); c.restore()
    # burned-in captions are off by default (on-screen graphics carry the key text; .srt ships alongside);
    # a spec can opt back in with "burn_captions": true
    if g.fmt == "short" and grps is not None and s["type"] != "cta" and spec.get("burn_captions"):
        captions(c, g, lt - lead, grps)
    gfx.grain(c, frame)
    if g.fmt == "long" and T < .5:
        c.drawRect(skia.Rect.MakeWH(g.W, g.H), paint((0, 0, 0), 1 - T / .5))


def render_scene(spec_path, fmt, i):
    spec = json.load(open(spec_path)); base = f"{ROOT}/out/{spec['slug']}/{fmt}"
    apply_theme(spec.get("theme", "whites")); spec["_intro"] = pick_intro(spec)
    g = setup(fmt); scenes = spec[fmt]
    meta, lead, durs, starts, total = plan(spec, fmt, base)
    grps = cap_groups(meta[i]["words"]) if fmt == "short" else None
    D = durs[i]; n = int(round(D * FPS))
    tmp, out = f"{base}/s{i}.tmp.mp4", f"{base}/s{i}.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{g.W}x{g.H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                          "-pix_fmt", "yuv420p", "-r", str(FPS), tmp], stdin=subprocess.PIPE)
    arr = np.zeros((g.H, g.W, 4), np.uint8); sf = skia.Surface(arr); c = sf.getCanvas()
    f0 = int(round(starts[i] * FPS))
    for fr in range(n):
        lt = fr / FPS
        draw(c, g, spec, scenes, i, lt, D, starts[i] + lt, total, f0 + fr, lead[i], grps, meta[i]["words"])
        sf.flushAndSubmit(); p.stdin.write(arr.tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, out)
    else: raise SystemExit(f"scene {i} failed")


def stills(spec_path, fmt, frac=.92):
    spec = json.load(open(spec_path)); base = f"{ROOT}/out/{spec['slug']}/{fmt}"
    apply_theme(spec.get("theme", "whites")); spec["_intro"] = pick_intro(spec)
    g = setup(fmt); scenes = spec[fmt]
    meta, lead, durs, starts, total = plan(spec, fmt, base)
    from PIL import Image
    ims = []
    for i in range(len(scenes)):
        arr = np.zeros((g.H, g.W, 4), np.uint8); sf = skia.Surface(arr); c = sf.getCanvas()
        lt = durs[i] * (frac if i < len(scenes) - 1 else .6)
        grps = cap_groups(meta[i]["words"]) if fmt == "short" else None
        draw(c, g, spec, scenes, i, lt, durs[i], starts[i] + lt, total, 0, lead[i], grps, meta[i]["words"]); sf.flushAndSubmit()
        ims.append(Image.fromarray(arr[..., :3].copy()))
    tw, th = (480, 270) if fmt == "long" else (216, 384)
    cols = 3 if fmt == "long" else 6
    rows = math.ceil(len(ims) / cols)
    sheet = Image.new("RGB", (tw * cols, th * rows))
    for k, im in enumerate(ims):
        sheet.paste(im.resize((tw, th)), ((k % cols) * tw, (k // cols) * th))
    sheet.save(f"{base}/sheet.jpg", quality=82)
    return f"{base}/sheet.jpg"


def mix(spec, fmt, base, total, lead, starts, n):
    subprocess.run(["python3", f"{ROOT}/music.py", str(total + 9), f"{base}/music.wav"], check=True)
    ins, flt = [], []
    sfx = None
    if fmt == "long" and n > 1:
        import intros
        nm = pick_intro(spec); impact = intros.INTROS[nm][1]
        sfx = f"{base}/intro_sfx.wav"
        intros.audio(sfx, impact, [.15 + k * .09 + .14 for k in range(12)] if nm == "flip" else ())
    for i in range(n):
        ins += ["-i", f"{base}/vo/b{i}.wav"]; ms = int((starts[i] + lead[i]) * 1000)
        flt.append(f"[{i}:a]aresample=44100,aformat=channel_layouts=stereo,adelay={ms}|{ms}[v{i}]")
    flt.append("".join(f"[v{i}]" for i in range(n)) + f"amix=inputs={n}:normalize=0,apad=whole_dur={total}[vo]")
    flt.append("[vo]asplit=2[vo1][vosc]")
    trim = "atrim=start=9,asetpts=PTS-STARTPTS," if fmt == "short" else ""
    flt.append(f"[{n}:a]{trim}volume=0.13[mus]")
    flt.append("[mus][vosc]sidechaincompress=threshold=0.03:ratio=6:attack=40:release=550[duck]")
    if sfx:
        ms = int(starts[1] * 1000)
        flt.append(f"[{n + 1}:a]aresample=44100,aformat=channel_layouts=stereo,volume=0.55,adelay={ms}|{ms}[fx]")
        flt.append(f"[vo1][duck][fx]amix=inputs=3:normalize=0,atrim=0:{total},afade=t=out:st={total - 1.2}:d=1.2,loudnorm=I=-14:TP=-1.5:LRA=11[out]")
    else:
        flt.append(f"[vo1][duck]amix=inputs=2:normalize=0,atrim=0:{total},afade=t=out:st={total - 1.2}:d=1.2,loudnorm=I=-14:TP=-1.5:LRA=11[out]")
    extra = ["-i", sfx] if sfx else []
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-i", f"{base}/music.wav", *extra, "-filter_complex", ";".join(flt),
                    "-map", "[out]", "-ar", "48000", "-ac", "2", "-c:a", "aac", "-b:a", "192k", f"{base}/mix.m4a"], check=True)


def srt(meta, lead, starts, path):
    def ts(x):
        ms = int(round(x * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s_, ms = divmod(ms, 1000)
        return f"{h:02}:{m:02}:{s_:02},{ms:03}"
    cues = []
    for i, m in enumerate(meta):
        off = starts[i] + lead[i]; cur = []
        for w in m["words"]:
            cur.append(w)
            line = " ".join(x["w"] for x in cur)
            if len(line) >= 40 or w["w"][-1] in ".?!":
                cues.append((cur[0]["s"] + off, cur[-1]["e"] + off, line)); cur = []
        if cur: cues.append((cur[0]["s"] + off, cur[-1]["e"] + off, " ".join(x["w"] for x in cur)))
    with open(path, "w") as f:
        for k, (a, b, tx) in enumerate(cues, 1):
            f.write(f"{k}\n{ts(a)} --> {ts(max(b, a + .8))}\n{tx}\n\n")


def lint_vo(spec):
    """Warn about narration a person couldn't say in one breath (no punctuation for 15+ words)."""
    import re
    for fmt in ("long", "short"):
        for i, sc in enumerate(spec.get(fmt, [])):
            for chunk in re.split(r"[.,?!:;—]", sc["vo"]):
                if len(chunk.split()) >= 15:
                    print(f"  ! {fmt} p{i}: {len(chunk.split())} words without a pause: \"{chunk.strip()[:80]}…\"", file=sys.stderr)


def build(spec_path, fmt):
    spec = json.load(open(spec_path)); slug = spec["slug"]
    lint_vo(spec)
    apply_theme(spec.get("theme", "whites"))
    base = f"{ROOT}/out/{slug}/{fmt}"; os.makedirs(base, exist_ok=True)
    scenes = spec[fmt]
    tts([s["vo"] for s in scenes], f"{base}/vo", fmt)
    meta, lead, durs, starts, total = plan(spec, fmt, base)
    mix(spec, fmt, base, total, lead, starts, len(scenes))
    order = sorted(range(len(scenes)), key=lambda i: -durs[i])
    procs = []
    for i in order:
        if len(procs) >= 2:
            procs.pop(0).wait()
        procs.append(subprocess.Popen(["python3", __file__, "scene", spec_path, fmt, str(i)], stderr=subprocess.DEVNULL))
    for p in procs: p.wait()
    missing = [i for i in range(len(scenes)) if not os.path.exists(f"{base}/s{i}.mp4")]
    if missing: raise SystemExit(f"missing scenes {missing}")
    with open(f"{base}/list.txt", "w") as f:
        for i in range(len(scenes)): f.write(f"file 's{i}.mp4'\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{base}/list.txt", "-c", "copy", f"{base}/video.mp4"], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{base}/video.mp4", "-i", f"{base}/mix.m4a", "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "copy", "-shortest", f"{base}/main.mp4"], check=True)
    outro = f"{ROOT}/out/outro_{fmt}_{gfx.THEME}.mp4"
    if not os.path.exists(outro): render_outro(fmt)
    with open(f"{base}/final.txt", "w") as f:
        f.write(f"file '{base}/main.mp4'\nfile '{outro}'\n")
    name = spec["files"][fmt]
    final = f"{ROOT}/deliver/{slug}/{name}.mp4"; os.makedirs(os.path.dirname(final), exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{base}/final.txt", "-c", "copy", "-movflags", "+faststart", final], check=True)
    srt(meta, lead, starts, f"{ROOT}/deliver/{slug}/{name}.srt")
    chap = [(0.0 if k == 0 else starts[k], sc["chapter"]) for k, sc in enumerate(scenes) if sc.get("chapter")]
    if fmt == "long" and len(chap) >= 3:     # YouTube chapters: first at 0:00, at least 3, each 10 s or longer
        chap[0] = (0.0, chap[0][1])
        with open(f"{ROOT}/deliver/{slug}/{name}.chapters.txt", "w") as f:
            for t, title in chap: f.write(f"{int(t // 60)}:{int(t % 60):02d} {title}\n")
    return final


# ------------------------------------------------------------------ animated logo outro
def outro_frame(c, g, t):
    gfx.background(c, 200 + t)
    long = g.fmt == "long"
    size = 300 if long else 360
    if long:
        ww = twidth("THIRD MAN", 190, "bebas", 3)
        mx, my = g.W / 2 - (.12 * size + ww) / 2, g.H / 2
    else:
        mx, my = g.W / 2, 800
    s = size / 190.0
    c.save(); c.translate(mx - 95 * s, my - 95 * s); c.scale(s, s)
    # ring draws on
    pr = eio(prog(t, .05, .75))
    if pr > 0:
        c.drawArc(skia.Rect.MakeXYWH(9, 9, 172, 172), -90, 360 * pr, False, paint(INK, 1, stroke=6))
    pi = eo(prog(t, .45, .9))
    c.drawCircle(95, 95, 50 * (.6 + .4 * pi), paint(LINE, pi, stroke=3))
    ps = eback(prog(t, .55, .95))
    if ps > 0:
        h = 46 * clamp(ps, 0, 1.1)
        rrect(c, 89, 95 - h / 2, 12, h, 3, INK, clamp(ps))
    for k, (x, y) in enumerate([(55, 48), (140, 58), (38, 112), (150, 104)]):
        pd = eback(prog(t, .75 + k * .07, 1.0 + k * .07))
        if pd > 0: c.drawCircle(x, y, 6 * clamp(pd, 0, 1.3), paint(MUTED, clamp(pd), stroke=3))
    # the gold ball flies from the batter to third man
    pb = eio(prog(t, 1.0, 1.55))
    if pb > 0:
        path = skia.Path(); path.moveTo(95, 115); path.quadTo(170, 110, 140, 148)
        meas = skia.PathMeasure(path, False); L = meas.getLength()
        seg = skia.Path(); meas.getSegment(max(0, L * pb - 40), L * pb, seg, True)
        c.drawPath(seg, paint(GOLD, .6 * (1 - prog(t, 1.5, 1.7)), stroke=6))
        pos, _ = meas.getPosTan(L * pb)
        c.drawCircle(pos.x(), pos.y(), 14 * (.5 + .5 * pb), paint(GOLD))
    pp = prog(t, 1.55, 2.3)
    if 0 < pp < 1:
        c.drawCircle(140, 148, 14 + 50 * eo(pp), paint(GOLD, .8 * (1 - pp), stroke=4))
    c.restore()
    # wordmark
    pw = eo(prog(t, 1.45, 2.05))
    if pw > 0:
        if long:
            x = mx + size * .62; off = (1 - pw) * 60
            text(c, "THE", x + off, my - 60, 52, "interB", MUTED, pw, track=20)
            text(c, "THIRD MAN", x + off, my + 90, 190, "bebas", INK, pw, track=3)
        else:
            off = (1 - pw) * 50
            text(c, "THE", g.W / 2, my + 300 + off, 48, "interB", MUTED, pw, "c", track=20)
            text(c, "THIRD MAN", g.W / 2, my + 470 + off, 190, "bebas", INK, pw, "c", track=3)
    ptg = eo(prog(t, 2.0, 2.6))
    if ptg > 0:
        tg = "CRICKET FROM A DIFFERENT ANGLE"
        if long: text(c, tg, mx + size * .62 + 6, my + 160, 30, "interB", GOLD, ptg, track=7)
        else: text(c, tg, g.W / 2, my + 560, 30, "interB", GOLD, ptg, "c", track=6)
    pf = prog(t, 3.5, 4.0)
    gfx.grain(c, int(t * FPS))
    if pf > 0: c.drawRect(skia.Rect.MakeWH(g.W, g.H), paint((0, 0, 0), pf))


def sting_frame(c, g, t):
    tt = min(t * 1.9, 2.75)
    c.saveLayerAlpha(None, int(255 * clamp((STING - t) / .25)))
    outro_frame(c, g, tt)
    c.restore()


def outro_audio(path, dur=4.0):
    import wave
    SR = 48000; n = int(SR * dur); t = np.arange(n) / SR
    rng = np.random.default_rng(5)
    from scipy.signal import butter, lfilter
    # riser/whoosh into the ball landing at 1.55s
    noise = rng.standard_normal(n)
    env = np.clip((t - .9) / .6, 0, 1) ** 2 * np.exp(-np.clip(t - 1.55, 0, None) * 8)
    b, a = butter(2, [800 / (SR / 2), 6000 / (SR / 2)], "band")
    wh = lfilter(b, a, noise) * env * .35
    # soft impact
    kt = np.clip(t - 1.55, 0, None)
    thump = np.sin(2 * np.pi * (55 + 60 * np.exp(-kt * 25)) * kt) * np.exp(-kt * 7) * (t >= 1.55) * .7
    # chime (major chord, bell-like)
    chime = np.zeros(n)
    for k, f in enumerate([880, 1108.7, 1318.5, 1760]):
        st = 1.55 + k * .06; tt = np.clip(t - st, 0, None)
        chime += (np.sin(2 * np.pi * f * tt) + .3 * np.sin(2 * np.pi * 2.76 * f * tt)) * np.exp(-tt * 2.6) * (t >= st) * .12
    pad = sum(np.sin(2 * np.pi * f * t) for f in [220, 277.2, 329.6]) * .05 * np.clip(t / .8, 0, 1)
    mixd = wh + thump + chime + pad
    mixd *= np.clip((dur - t) / .6, 0, 1)
    mixd /= np.abs(mixd).max() + 1e-9; mixd *= .8
    st = np.stack([mixd, np.roll(mixd, 300)], 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype(np.int16).tobytes())


def render_outro(fmt):
    g = setup(fmt); os.makedirs(f"{ROOT}/out", exist_ok=True)
    dur = 4.0; n = int(dur * FPS)
    vid = f"{ROOT}/out/outro_{fmt}_{gfx.THEME}_v.mp4"; wav = f"{ROOT}/out/outro.wav"; out = f"{ROOT}/out/outro_{fmt}_{gfx.THEME}.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{g.W}x{g.H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                          "-pix_fmt", "yuv420p", "-r", str(FPS), vid], stdin=subprocess.PIPE)
    arr = np.zeros((g.H, g.W, 4), np.uint8); sf = skia.Surface(arr); c = sf.getCanvas()
    for fr in range(n):
        outro_frame(c, g, fr / FPS); sf.flushAndSubmit(); p.stdin.write(arr.tobytes())
    p.stdin.close(); p.wait()
    outro_audio(wav, dur)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vid, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-af", "loudnorm=I=-16:TP=-2", "-ar", "48000", "-ac", "2", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
    return out


# ------------------------------------------------------------------ covers / thumbnails
def thumb(spec_path):
    spec = json.load(open(spec_path)); th = spec["thumb"]; slug = spec["slug"]
    apply_theme(spec.get("theme", "whites"))
    outdir = f"{ROOT}/deliver/{slug}"; os.makedirs(outdir, exist_ok=True)
    res = []
    for fmt, (OW, OH) in [("long", (1280, 720)), ("short", (1080, 1920))]:
        g = setup(fmt)
        arr = np.zeros((OH, OW, 4), np.uint8); sf = skia.Surface(arr); c = sf.getCanvas()
        c.save(); c.scale(OW / g.W, OH / g.H)
        gfx.background(c, 3.0)
        long = fmt == "long"
        # hero (big number / symbol) with a glow plate
        hero = th.get("hero"); hc = C(th.get("heroc", "gold"))
        if long:
            if hero:
                hs = fit(hero, 640, th.get("herosize", 560), "bebas")
                c.drawCircle(1480, 560, 360, paint(hc, .10, blur=60))
                text(c, hero, 1480, 560 + hs * .36, hs, "bebas", hc, 1, "c", glow=30)
            tw = 920 if hero else 1680
            y = 250
            k = th.get("kicker")
            if k:
                kw = twidth(k, 44, "bebas", 2) + 40
                rrect(c, 90, 120, kw, 64, 8, GOLD); text(c, k, 90 + kw / 2, 168, 44, "bebas", BG, 1, "c", track=2)
                y = 300
            lines = th["lines"]
            sizes = [fit(l["t"], tw, 230, "bebas", 2) for l in lines]
            for l, z in zip(lines, sizes):
                y += z * .86
                text(c, l["t"], 90, y, z, "bebas", C(l.get("c")), 1, track=2, glow=14 if l.get("c") == "gold" else 0)
                y += z * .1
            gfx.logo_lockup(c, 90, 980, 70, 1)
        else:
            k = th.get("kicker"); y = 330
            if k:
                kw = twidth(k, 50, "bebas", 2) + 44
                rrect(c, g.W / 2 - kw / 2, 250, kw, 72, 8, GOLD); text(c, k, g.W / 2, 304, 50, "bebas", BG, 1, "c", track=2)
                y = 380
            for l in th["lines"]:
                z = fit(l["t"], 960, 230, "bebas", 2)
                y += z * .86
                text(c, l["t"], g.W / 2, y, z, "bebas", C(l.get("c")), 1, "c", track=2, glow=14 if l.get("c") == "gold" else 0)
                y += z * .1
            if hero:
                hs = fit(hero, 900, th.get("herosize", 520), "bebas")
                c.drawCircle(g.W / 2, y + 360, 380, paint(hc, .10, blur=60))
                text(c, hero, g.W / 2, y + 360 + hs * .36, hs, "bebas", hc, 1, "c", glow=30)
            gfx.logo_lockup(c, g.W / 2, 1560, 90, 1, "c")
        c.restore(); sf.flushAndSubmit()
        name = spec["files"][fmt]
        path = f"{outdir}/{name}_{'thumbnail' if long else 'cover'}.jpg"
        skia.Image.fromarray(arr, colorType=skia.kRGBA_8888_ColorType).save(path, skia.kJPEG, 92)
        res.append(path)
    return res


# ------------------------------------------------------------------ cricket tactics board
# Field coordinates for a right-hander: x in units of 1.15R (off side = +x, screen-right), y in units of R (+y = behind the batter).
# The pitch runs from y=-0.25 (bowler's end) to y=+0.25 (batter's stumps).
POS = {
    "keeper": (0, .56), "slip": (.12, .56), "2nd slip": (.22, .53), "3rd slip": (.32, .49), "gully": (.45, .40),
    "point": (.55, .24), "backward point": (.48, .34), "cover": (.55, -.06), "extra cover": (.42, -.22), "mid-off": (.16, -.55),
    "mid-on": (-.16, -.55), "midwicket": (-.52, -.06), "square leg": (-.55, .24), "short leg": (-.18, .30), "leg slip": (-.12, .56),
    "fine leg": (-.45, .84), "deep third": (.45, .84), "third man": (.45, .84), "deep point": (.92, .24), "deep cover": (.80, -.45),
    "long-off": (.28, -.92), "long-on": (-.28, -.92), "deep midwicket": (-.80, -.45), "deep square leg": (-.92, .24),
    "bowler": (.06, -.42),
}
CORDON = {"keeper", "slip", "2nd slip", "3rd slip"}


def sc_fieldplan(c, g, t, D, s):
    head(c, g, t, s)
    long = g.fmt == "long"
    if long:
        cx, cy, R = 1280, 640, 330
    else:
        cx, cy, R = g.cx, g.top + 340, 330
    a = eo(prog(t, 0, .6))
    mir = -1 if s.get("lefty") else 1   # left-handed batter: off side flips
    P = lambda nm: (cx + mir * POS[nm][0] * 1.15 * R, cy + POS[nm][1] * R)
    # ground, circle, pitch
    light = gfx.THEMES[gfx.THEME]["light"]
    c.drawOval(skia.Rect.MakeXYWH(cx - R * 1.15, cy - R, 2.3 * R, 2 * R), paint((214, 234, 216) if light else (20, 52, 40), (1 if light else .55) * a))
    c.drawOval(skia.Rect.MakeXYWH(cx - R * 1.15, cy - R, 2.3 * R, 2 * R), paint(INK, (.35 if light else .5) * a, stroke=3))
    c.drawOval(skia.Rect.MakeXYWH(cx - R * .62, cy - R * .56, 1.24 * R, 1.12 * R), paint(INK, .14 * a, stroke=2))
    pw = .07 * 1.15 * R; py0, py1 = cy - .36 * R, cy + .36 * R
    rrect(c, cx - pw / 2, py0, pw, py1 - py0, 4, (190, 165, 110), .75 * a)
    # length zone (metres from the batter's stumps; pitch = 20.12 m)
    L = s.get("length")
    if L:
        pl = eo(prog(t, D * L.get("at", .15), D * L.get("at", .15) + .6))
        yA = py1 - L["from"] / 20.12 * (py1 - py0); yB = py1 - L["to"] / 20.12 * (py1 - py0)
        lc = C(L.get("c", "gold"))
        c.drawRect(skia.Rect.MakeLTRB(cx - pw * 1.6, yB, cx + pw * 1.6, yA), paint(lc, .45 * pl))
        c.drawRect(skia.Rect.MakeLTRB(cx - pw * 1.6, yB, cx + pw * 1.6, yA), paint(lc, pl, stroke=3))
        lx = cx - pw * 1.6 - 14
        text(c, L.get("label", ""), lx, (yA + yB) / 2 + 8, 22 if long else 24, "interB", lc, pl, "r", track=2)
    # batter + bowler
    bx, by = cx, py1 + 4
    c.drawCircle(bx, by, 11, paint(GOLD, a))
    c.drawCircle(*P("bowler"), 8, paint(MUTED, a))
    # fielders
    fl = s.get("fielders", []); hl = set(s.get("hl", []))
    for k, nm in enumerate(fl):
        st = D * (.05 + .25 * k / max(1, len(fl) - 1))
        p = eback(prog(t, st, st + .4)); pa = clamp(prog(t, st, st + .2))
        x, y = P(nm); h = nm in hl
        cc = GOLD if h else BLUE
        if h: c.drawCircle(x, y, 26 * pa, paint(GOLD, .25 * pa, blur=10))
        c.drawCircle(x, y, (11 if h else 9) * clamp(p, 0, 1.2), paint(cc, pa))
        if nm not in CORDON:
            text(c, nm.upper(), x, y - 20, 18 if long else 19, "interB", INK if h else MUTED, pa * (1 if h else .85), "c", track=2)
    cord = [nm for nm in fl if nm in CORDON]
    if cord:
        k = fl.index(cord[-1]); st = D * (.05 + .25 * k / max(1, len(fl) - 1))
        pa = clamp(prog(t, st, st + .3))
        lab = "KEEPER + " + str(len(cord) - 1) + (" SLIPS" if len(cord) > 2 else " SLIP") if len(cord) > 1 else "KEEPER"
        hx = max(P(n)[0] for n in cord) if mir > 0 else min(P(n)[0] for n in cord)
        text(c, lab, hx + 22 * mir, P(cord[-1])[1] - 18, 18 if long else 19, "interB", GOLD if any(n in hl for n in cord) else MUTED, pa, "l" if mir > 0 else "r", track=2)
    # shots: ball paths to a fielder (or a named point), drawn on cue
    for sh in s.get("shots", []):
        st = sh.get("_ts", D * sh.get("at", .5))
        pb = eio(prog(t, st, st + 1.0))
        if pb <= 0: continue
        ex, ey = P(sh["to"])
        mx, my = (bx + ex) / 2 + mir * sh.get("bend", 0) * R, (by + ey) / 2 - sh.get("lift", .15) * R
        path = skia.Path(); path.moveTo(bx, by); path.quadTo(mx, my, ex, ey)
        meas = skia.PathMeasure(path, False); Lg = meas.getLength()
        seg = skia.Path(); meas.getSegment(0, Lg * pb, seg, True)
        cc = C(sh.get("c", "red"))
        c.drawPath(seg, paint(cc, .35, stroke=12, blur=6)); c.drawPath(seg, paint(cc, 1, stroke=4))
        pos, _ = meas.getPosTan(Lg * pb)
        c.drawCircle(pos.x(), pos.y(), 8, paint((255, 255, 255)))
        if pb >= 1 and sh.get("label"):
            pp = eback(prog(t, st + 1.0, st + 1.4))
            c.drawCircle(ex, ey, 34 * clamp(pp, 0, 1.2), paint(cc, .9 * clamp(pp), stroke=4))
            if sh["to"] in CORDON:
                text(c, sh["label"], ex, ey + 80, 30, "bebas", cc, clamp(pp), "c", track=2)
            else:
                rt = ex <= cx + R * .6 if mir > 0 else ex < cx - R * .6
                text(c, sh["label"], ex + (40 if rt else -40), ey + 8, 30, "bebas", cc, clamp(pp), "l" if rt else "r", track=2)
    # side notes (long form): big lines + small sub
    if long and s.get("lines"):
        y = 420
        for i, ln in enumerate(s["lines"]):
            tt = ln["t"] if isinstance(ln, dict) else ln
            cc = C(ln.get("c")) if isinstance(ln, dict) else INK
            st = D * (ln.get("at", .1 + i * .08) if isinstance(ln, dict) else .1 + i * .08)
            p = eo(prog(t, st, st + .5))
            sz = fit(tt, 640, 96, "bebas", 2)
            y += sz * .9
            text(c, tt, 140 + (1 - p) * -30, y, sz, "bebas", cc, p, track=2)
        if s.get("sub"):
            p = eo(prog(t, D * s.get("subat", .5), D * s.get("subat", .5) + .6))
            for j, l in enumerate(wrap(s["sub"], 620, 28, "interSB")):
                text(c, l, 144, y + 60 + j * 38, 28, "interSB", MUTED, p)


SCENES["fieldplan"] = sc_fieldplan


# ------------------------------------------------------------------ team colours
# Team identity through colour and short codes only: no logos. Each team has a main colour and a
# light/dark alternate; team_col() picks whichever reads against the current theme background.
TEAMS = {
    # IPL
    "CSK": ((250, 200, 20), (190, 140, 0), "Chennai Super Kings"),
    "MI": ((0, 92, 185), (90, 160, 240), "Mumbai Indians"),
    "RCB": ((214, 30, 40), (240, 90, 90), "Royal Challengers Bengaluru"),
    "KKR": ((70, 40, 130), (160, 120, 230), "Kolkata Knight Riders"),
    "SRH": ((245, 120, 30), (200, 90, 10), "Sunrisers Hyderabad"),
    "DC": ((0, 90, 190), (230, 60, 60), "Delhi Capitals"),
    "PBKS": ((220, 30, 45), (245, 100, 100), "Punjab Kings"),
    "RR": ((235, 30, 140), (250, 120, 190), "Rajasthan Royals"),
    "GT": ((25, 45, 90), (140, 175, 220), "Gujarat Titans"),
    "LSG": ((0, 160, 220), (0, 110, 160), "Lucknow Super Giants"),
    # internationals
    "IND": ((25, 100, 200), (110, 170, 245), "India"),
    "NZ": ((25, 25, 25), (205, 205, 205), "New Zealand"),
    "AUS": ((250, 200, 20), (180, 130, 0), "Australia"),
    "ENG": ((20, 50, 120), (120, 160, 230), "England"),
    "PAK": ((0, 110, 60), (80, 190, 120), "Pakistan"),
    "SA": ((0, 120, 75), (80, 195, 130), "South Africa"),
    "SL": ((20, 50, 120), (240, 180, 40), "Sri Lanka"),
    "WI": ((125, 20, 30), (220, 90, 100), "West Indies"),
    "AFG": ((0, 70, 160), (90, 150, 240), "Afghanistan"),
    "BAN": ((0, 105, 60), (220, 40, 50), "Bangladesh"),
}
TEAM_BY_NAME = {v[2]: k for k, v in TEAMS.items()}


def _lum(c):
    return (0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]) / 255


def team_col(code):
    code = TEAM_BY_NAME.get(code, code)
    if code not in TEAMS: return INK
    main, alt, _ = TEAMS[code]
    return main if abs(_lum(main) - _lum(BG)) >= .28 else alt


def team_chip(c, code, x, y, h, a=1.0, align="l"):
    """Rounded tag with the team's short code in its colour (no logo). Returns its width."""
    code = TEAM_BY_NAME.get(code, code)
    col = team_col(code)
    fs = h * .62
    w = twidth(code, fs, "interB", 2) + h * .7
    x0 = x if align == "l" else (x - w if align == "r" else x - w / 2)
    rrect(c, x0, y, w, h, h * .22, col, a)
    tc = (255, 255, 255) if _lum(col) < .6 else (16, 20, 30)
    text(c, code, x0 + w / 2, y + h * .5 + fs * .36, fs, "interB", tc, a, "c", track=2)
    return w


_C0 = C


def C(x):  # noqa: F811  (extends the colour lookup with "team:RCB" / bare team codes)
    if isinstance(x, str):
        if x.startswith("team:"): return team_col(x[5:])
        if x in TEAMS: return team_col(x)
    return _C0(x)


# ------------------------------------------------------------------ silhouettes
# Original flat figures built from rounded limbs. Coordinates are in body heights (feet at 0, head ~0.92),
# facing +x. Joints: hd head, nk neck, pv pelvis, fk/ff front knee/foot, bk/bf back knee/foot,
# fe/fh front elbow/hand, be/bh back elbow/hand, bat = bat tip (from the hands).
POSES = {
    "stance": dict(hd=(.03, .90), nk=(.0, .79), pv=(-.03, .50), fk=(.07, .27), ff=(.12, .0), bk=(-.10, .26), bf=(-.15, .0),
                   fe=(.07, .62), fh=(.0, .52), be=(-.05, .63), bh=(-.01, .53), bat=(-.13, .10)),
    "drive": dict(hd=(.20, .82), nk=(.13, .73), pv=(.0, .45), fk=(.20, .25), ff=(.30, .0), bk=(-.14, .20), bf=(-.27, .0),
                  fe=(.27, .62), fh=(.30, .78), be=(.20, .70), bh=(.29, .80), bat=(.10, 1.10)),
    "pull": dict(hd=(-.02, .89), nk=(-.03, .78), pv=(-.04, .48), fk=(.10, .26), ff=(.16, .0), bk=(-.13, .25), bf=(-.18, .0),
                 fe=(.10, .74), fh=(.04, .80), be=(-.06, .70), bh=(.02, .80), bat=(-.42, .92)),
    "defend": dict(hd=(.14, .86), nk=(.09, .76), pv=(.0, .47), fk=(.18, .26), ff=(.24, .0), bk=(-.10, .23), bf=(-.20, .0),
                   fe=(.18, .58), fh=(.20, .48), be=(.10, .62), bh=(.20, .52), bat=(.24, .06)),
    "release": dict(hd=(.12, .89), nk=(.08, .79), pv=(.0, .52), fk=(.15, .28), ff=(.24, .0), bk=(-.17, .32), bf=(-.31, .12),
                    fe=(.12, 1.0), fh=(.15, 1.18), be=(.02, .62), bh=(-.07, .55)),
    "spin": dict(hd=(.07, .91), nk=(.04, .80), pv=(.0, .52), fk=(.10, .27), ff=(.16, .0), bk=(-.11, .28), bf=(-.20, .06),
                 fe=(.11, .98), fh=(.13, 1.12), be=(.08, .64), bh=(.03, .58)),
    "keeper": dict(hd=(.10, .62), nk=(.06, .54), pv=(-.06, .36), fk=(.10, .22), ff=(.10, .0), bk=(-.02, .20), bf=(-.10, .0),
                   fe=(.16, .40), fh=(.20, .30), be=(.12, .38), bh=(.20, .31)),
}


def figure(c, pose, x, y, h, col=None, a=1.0, mirror=False, ball=False):
    """Draw an original flat cricketer silhouette. (x, y) = point between the feet; h = height in px."""
    P = POSES[pose]; col = col or INK; sx = -1 if mirror else 1
    J = lambda k: (x + sx * P[k][0] * h, y - P[k][1] * h)
    back = tuple(int(v * .62 + b * .38) for v, b in zip(col, BG))   # far-side limbs, slightly receded
    lw, tw = h * .105, h * .16

    def limb(pts, w, cc):
        pa = skia.Path(); pa.moveTo(*pts[0])
        for q in pts[1:]: pa.lineTo(*q)
        p = paint(cc, a, stroke=w); p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
        c.drawPath(pa, p)

    limb([J("pv"), J("bk"), J("bf")], lw, back)
    limb([J("nk"), J("be"), J("bh")], lw * .8, back)
    if "bat" in P:
        hx, hy = J("bh"); bx, by = J("bat")
        ang = math.atan2(by - hy, bx - hx); L = math.hypot(bx - hx, by - hy)
        c.save(); c.translate(hx, hy); c.rotate(math.degrees(ang))
        rrect(c, 0, -h * .018, L * .32, h * .036, h * .018, col, a)                # handle
        rrect(c, L * .30, -h * .042, L * .70, h * .084, h * .03, (215, 190, 140) if _lum(BG) < .5 else (170, 135, 80), a)  # blade
        c.restore()
    limb([J("pv"), J("fk"), J("ff")], lw, col)
    limb([J("nk"), J("pv")], tw, col)
    limb([J("nk"), J("fe"), J("fh")], lw * .8, col)
    hx, hy = J("hd")
    c.drawCircle(hx, hy, h * .075, paint(col, a))
    if "bat" in P or pose == "keeper":   # helmet peak
        limb([(hx + sx * h * .02, hy - h * .015), (hx + sx * h * .095, hy - h * .005)], h * .025, col)
    if ball:
        bx, by = J("fh")
        c.drawCircle(bx + sx * h * .02, by - h * .03, h * .03, paint(RED, a))


def sc_matchup(c, g, t, D, s):
    """Bowler vs batter, face to face, with optional stat rows between them."""
    head(c, g, t, s)
    L, R = s["left"], s["right"]
    long = g.fmt == "long"
    fh = 430 if long else 470
    fy = g.bot - 60 if long else g.top + 500
    xl, xr = (g.x0 + 170, g.x1 - 170) if long else (g.x0 + 150, g.x1 - 150)
    for k, (side, x, mir) in enumerate([(L, xl, False), (R, xr, True)]):
        p = eo(prog(t, .1 + k * .25, .7 + k * .25))
        cc = C(side.get("color") or (("team:" + side["team"]) if side.get("team") else ("gold" if k == 0 else "ink")))
        c.drawOval(skia.Rect.MakeXYWH(x - fh * .3, fy - fh * .03, fh * .6, fh * .06), paint(cc, .18 * p, blur=6))
        figure(c, side.get("pose", "release" if k == 0 else "stance"), x + (1 - p) * (-60 if k == 0 else 60), fy, fh, cc, p,
               mirror=mir, ball=side.get("ball", k == 0))
        ny = fy + 56 if long else fy + 60
        text(c, side["name"], x, ny, fit(side["name"], 400, 48, "bebas", 2), "bebas", cc, p, "c", track=2)
        if side.get("team"): team_chip(c, side["team"], x, ny + 18, 34, p, "c")
        elif side.get("sub"): text(c, side["sub"], x, ny + 40, 22, "interB", MUTED, p, "c", track=3)
    rows = s.get("rows", [])
    if rows:
        if long:
            cx0, cw, top = g.cx - 360, 720, g.top + 40
        else:
            cx0, cw, top = g.x0, g.cw, fy + 150
        slot = 120 if long else 110
        for i, r in enumerate(rows):
            st = r[3] if len(r) > 3 and isinstance(r[3], (int, float)) else None
            st = D * st if st is not None else rv(i, len(rows), D, .3, .75)
            p = eo(prog(t, st, st + .5)); y = top + i * slot
            rrect(c, cx0, y, cw, slot - 18, 14, PANEL, .75 * p)
            text(c, r[0], cx0 + cw / 2, y + (slot - 18) / 2 + 9, fit(r[0], cw * .42, 22, "interB", 3), "interB", MUTED, p, "c", track=3)
            for val, x, k in [(r[1], cx0 + cw * .14, 0), (r[2], cx0 + cw * .86, 1)]:
                sd = L if k == 0 else R
                cc = C(sd.get("color") or (("team:" + sd["team"]) if sd.get("team") else ("gold" if k == 0 else "ink")))
                text(c, val, x, y + (slot - 18) / 2 + 26, fit(val, cw * .26, 72, "bebas"), "bebas", cc, p, "c")


# ------------------------------------------------------------------ ball trajectory (side-on)
LENGTH_ZONES = [("YORKER", 0, 2), ("FULL", 2, 5), ("GOOD", 5, 8), ("SHORT", 8, 11.5)]


def sc_trajectory(c, g, t, D, s):
    """Side-on view of the pitch: bowler at left, batter at right, deliveries drawn on cue.
    balls: [{length (m from batter's stumps), label, c, release (m), end (m height at batter), loop, at}]"""
    head(c, g, t, s)
    long = g.fmt == "long"
    gx0, gx1 = (g.x0 + 60, g.x1 - 60) if long else (g.x0 + 10, g.x1 - 10)
    gy = g.bot - 150 if long else g.top + 640
    ppm = (gx1 - gx0) / 20.12               # px per metre along the pitch
    vs = ppm * (2.3 if long else 3.4)       # vertical exaggeration so heights read clearly
    X = lambda m: gx1 - m * ppm             # m = metres from the batter's stumps
    Y = lambda hm: gy - hm * vs
    pa = eo(prog(t, 0, .6))
    # pitch strip, length zones, creases, stumps
    rrect(c, gx0 - 20, gy, gx1 - gx0 + 40, 14, 4, (190, 165, 110), .8 * pa)
    for k, (nm, a_, b_) in enumerate(s.get("zones", LENGTH_ZONES)):
        x_a, x_b = X(b_), X(a_)
        hl = nm in s.get("hl", [])
        c.drawRect(skia.Rect.MakeLTRB(x_a, gy + 20, x_b, gy + 64), paint(GOLD if hl else LINE, (.5 if hl else .22) * pa))
        text(c, nm, (x_a + x_b) / 2, gy + 50, fit(nm, x_b - x_a - 10, 20 if long else 18, "interB", 2), "interB",
             INK if hl else MUTED, pa, "c", track=2)
    for m in (0, 20.12):
        x = X(m)
        for dx in (-.11, 0, .11):
            c.drawLine(x + dx * ppm, gy, x + dx * ppm, Y(.71), paint(INK, .85 * pa, stroke=4))
    # figures (bowler at release, batter in stance) at true scale on the same vertical exaggeration
    fh = 1.8 * vs * .92
    bpose = s.get("bowler_pose", "release"); bfx = X(19.4)
    figure(c, bpose, bfx, gy, fh, C(s.get("bowler_c", "muted")), .9 * pa)
    hand = (bfx + POSES[bpose]["fh"][0] * fh, gy - POSES[bpose]["fh"][1] * fh)   # ball leaves the bowling hand
    figure(c, s.get("batter_pose", "stance"), X(-.5), gy, fh, C(s.get("batter_c", "ink")), .9 * pa, mirror=True)
    if s.get("speed"):
        text(c, s["speed"], hand[0] + 30, hand[1] - 40, 44 if long else 38, "bebas", GOLD, pa, "l", track=2)
    # deliveries
    balls = s.get("balls", [])
    for k, b in enumerate(balls):
        st = b.get("_ts", D * b.get("at", .15 + .6 * k / max(1, len(balls))))
        p = prog(t, st, st + b.get("dur", .9))
        if p <= 0: continue
        Lm = b["length"]; end = b.get("end", clamp(.15 + .16 * Lm, .1, 2.0))
        x0, y0 = hand; xb, yb = X(Lm), Y(0); x1, y1 = X(-.3), Y(end)
        loop = b.get("loop", 0)
        path = skia.Path(); path.moveTo(x0, y0)
        path.quadTo((x0 + xb) / 2, (y0 + yb) / 2 - loop * vs, xb, yb)
        path.quadTo((xb + x1) / 2, (yb + y1) / 2 - .12 * vs, x1, y1)
        meas = skia.PathMeasure(path, False); L1 = meas.getLength()
        seg = skia.Path(); meas.getSegment(0, L1 * eio(p), seg, True)
        cc = C(b.get("c", "gold"))
        c.drawPath(seg, paint(cc, .3, stroke=10, blur=6)); c.drawPath(seg, paint(cc, 1, stroke=3.5))
        pos, _ = meas.getPosTan(L1 * eio(p))
        c.drawCircle(pos.x(), pos.y(), 9 if long else 10, paint(RED if cc != RED else (255, 255, 255)))
        # bounce marker + label once the ball has pitched
        pb = clamp((p - .55) / .25)
        if pb > 0:
            c.drawCircle(xb, yb, 16 * eback(pb), paint(cc, pb, stroke=3))
            if b.get("label"):
                ly = gy + 112 + k * 42
                c.drawLine(xb, gy + 66, xb, ly - 30, paint(cc, .6 * pb, stroke=2))
                text(c, b["label"], xb, ly, 30 if long else 30, "bebas", cc, pb, "c", track=2)
    if s.get("note"):
        pn = eo(prog(t, D * s.get("noteat", .5), D * s.get("noteat", .5) + .6))
        nx, ny = (g.x0, g.top + 30) if long else (g.x0, g.top + 30)
        for j, l in enumerate(wrap(s["note"], 1300 if long else g.cw, 30, "interSB")):
            text(c, l, nx, ny + j * 40, 30, "interSB", MUTED, pn)


SCENES["matchup"] = sc_matchup
SCENES["trajectory"] = sc_trajectory


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "scene":
        render_scene(sys.argv[2], sys.argv[3], int(sys.argv[4]))
    elif cmd == "build":
        fmts = ["long", "short"] if len(sys.argv) < 4 or sys.argv[3] == "both" else [sys.argv[3]]
        for f in fmts: print(build(sys.argv[2], f), flush=True)
        print(*thumb(sys.argv[2]))
    elif cmd == "voice":
        spec = json.load(open(sys.argv[2]))
        for f in (["long", "short"] if len(sys.argv) < 4 else [sys.argv[3]]):
            m = tts([s["vo"] for s in spec[f]], f"{ROOT}/out/{spec['slug']}/{f}/vo", f)
            print(f, round(sum(x["dur"] for x in m), 1), "s")
    elif cmd == "stills":
        print(stills(sys.argv[2], sys.argv[3]))
    elif cmd == "outro":
        print(render_outro(sys.argv[2]))
    elif cmd == "thumb":
        print(*thumb(sys.argv[2]))
