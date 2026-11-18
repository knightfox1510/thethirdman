"""Scenes for the IPL 2027 'What every IPL team needs' Data Story (lab look, official mono team icons from data/licensed/logos):
needs_hook, needs_purse, needs_map, needs_team, needs_pool, needs_bids. Installed by looks.install."""
import os, math
import skia
import gfx
from gfx import text, rrect, paint, prog, eo, eback, clamp, twidth
E = None; LK = None
ROOT = os.path.dirname(os.path.abspath(__file__)); _IMG = {}
AMB = (226, 150, 24); GRN = (40, 150, 90)


def _logo(code):
    if code not in _IMG:
        _IMG[code] = skia.Image.open(f"{ROOT}/data/licensed/logos/{code}_{'light' if code == 'RR' else 'dark'}.png")
    return _IMG[code]


def logo(c, code, cx, cy, size, a=1.0):
    im = _logo(code); w, h = im.width(), im.height(); k = size / max(w, h)
    c.drawImageRect(im, skia.Rect.MakeXYWH(cx - w * k / 2, cy - h * k / 2, w * k, h * k), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear), paint((255, 255, 255), a))


def cc(v): return LK.RED if v < .7 else (AMB if v < .9 else GRN)
def stag(t, D, k, n, lo=.06, span=.6): st = D * lo + k * D * span / max(1, n); return eo(prog(t, st, st + .5))


def sc_needs_hook(c, g, t, D, s):
    LK.header(c, g, t, D, s); sh = g.fmt == "short"; a = eo(prog(t, .0, .5)); cx = g.W / 2
    y = 520 if sh else 360
    big = E.fit("298 CRORE", 760 if sh else 900, 230 if sh else 250, "interB", -3)
    tw = twidth("298 CRORE", big, "interB", -3) + big * .75
    text(c, "₹", cx - tw / 2, y, big * .9, "interB", LK.RED, a); text(c, "298 CRORE", cx - tw / 2 + big * .75, y, big, "interB", gfx.INK, a, track=-3)
    text(c, s.get("line", "66 SLOTS · 10 TEAMS · ONE AUCTION"), cx, y + (80 if sh else 90), 38 if sh else 40, "monoSB", gfx.MUTED, eo(prog(t, .2, .7)), "c", track=2)
    codes = s["codes"]; per = 5 if sh else 10; sz = 150 if sh else 140; gap = (g.W - 160) / per
    for i, code in enumerate(codes):
        q = eback(prog(t, .3 + .05 * i, .75 + .05 * i)); r, k = divmod(i, per)
        logo(c, code, 80 + gap * (k + .5), (y + 230 if sh else y + 250) + r * (200), sz * (.7 + .3 * q), clamp(q))
    text(c, s.get("tagline", "What every IPL team still needs"), cx, y + (640 if sh else 450), 52 if sh else 46, "interB", gfx.INK, eo(prog(t, .6, 1.0)), "c")


def sc_needs_purse(c, g, t, D, s):
    LK.header(c, g, t, D, s); l = LK.L(g); sh = g.fmt == "short"; items = s["items"]; n = len(items); mx = max(i["cr"] for i in items)
    top = l["top"] + (10 if sh else 0); rh = (l["bot"] - top) / n; lg = rh * .8
    x0 = l["x0"]; bx = x0 + lg + 24; bw = (l["x1"] - bx) - (260 if sh else 420)
    for k, it in enumerate(items):
        q = stag(t, D, k, n); y = top + k * rh + rh / 2; red = it.get("low")
        logo(c, it["code"], x0 + lg / 2, y, lg, q)
        h = rh * .52; w = bw * it["cr"] / mx * q
        rrect(c, bx, y - h / 2, max(4, w), h, 6, LK.RED if red else gfx.INK, q)
        text(c, f'₹{it["cr"] * q:.2f}'.rstrip("0").rstrip("."), bx + w + 14, y + h * .34, h * 1.05, "interB", LK.RED if red else gfx.INK, q)
        text(c, f'{it["slots"]} slots · {it["ovs"]} ovs' if not sh else f'{it["slots"]} slots', l["x1"], y + 9, 24 if sh else 26, "monoSB", gfx.MUTED, q, "r")


COLS = [("BAT", "POWERPLAY"), ("BAT", "MIDDLE"), ("BAT", "DEATH"), ("PACE", "POWERPLAY"), ("SPIN", "MIDDLE"), ("PACE", "DEATH")]


def sc_needs_map(c, g, t, D, s):
    LK.header(c, g, t, D, s); l = LK.L(g); sh = g.fmt == "short"; rows = s["rows"]; n = len(rows)
    lw = 110 if sh else 190; kw = 70 if sh else 110; gw = (l["x1"] - l["x0"] - lw - kw) / 6; top = l["top"] + 8
    a = eo(prog(t, .1, .5))
    for j, (a1, a2) in enumerate(COLS):
        x = l["x0"] + lw + gw * (j + .5)
        text(c, a1, x, top + 12, 22 if sh else 24, "monoSB", gfx.INK, a, "c", track=1); text(c, a2[:5] if sh else a2, x, top + 38, 17 if sh else 19, "mono", gfx.MUTED, a, "c")
    text(c, "KEEPERS", l["x1"] - kw / 2, top + 24, 18 if sh else 19, "monoSB", gfx.INK, a, "c")
    top += 52; rh = min((l["bot"] - top) / n, 120 if sh else 80)
    for k, r in enumerate(rows):
        q = stag(t, D, k, n, .1, .6); y = top + k * rh
        logo(c, r["code"], l["x0"] + 36, y + rh / 2, min(rh * .84, 64), q)
        if not sh: text(c, r["code"], l["x0"] + 82, y + rh / 2 + 14, 40, "interB", gfx.INK, q)
        for j, v in enumerate(r["v"]):
            x = l["x0"] + lw + gw * j + 4
            rrect(c, x, y + 3, gw - 8, rh - 6, 10, cc(v), q)
            text(c, f"{v:.2f}", x + (gw - 8) / 2, y + rh / 2 + (11 if sh else 14), 32 if sh else 38, "interB", (255, 255, 255), q, "c")
        text(c, str(r["k"]), l["x1"] - kw / 2, y + rh / 2 + 14, 38, "interB", LK.RED if r["k"] < 2 else gfx.INK, q, "c")


def sc_needs_team(c, g, t, D, s):
    LK.header(c, g, t, D, s); l = LK.L(g); sh = g.fmt == "short"; a = eo(prog(t, .05, .45)); q = eback(prog(t, .0, .6))
    if sh:
        logo(c, s["code"], l["x0"] + 120, l["top"] + 110, 230 * (.7 + .3 * q), clamp(q)); x = l["x0"] + 270; y = l["top"] + 110
        text(c, "₹", x, y, 110, "interB", LK.RED, a); text(c, f'{s["cr"]:g} CR', x + 70, y, 118, "interB", gfx.INK, a, track=-3)
        text(c, f'{s["slots"]} slots · {s["ovs"]} overseas', x, y + 52, 32, "monoSB", gfx.MUTED, a)
        hz = E.fit(s["head"].upper(), l["x1"] - l["x0"], 76, "interB", -2)
        text(c, s["head"].upper(), l["x0"], l["top"] + 290, hz, "interB", LK.RED, eo(prog(t, .2, .6)), track=-2); by = l["top"] + 350; cols = 2; step = 150; bh = 42
    else:
        logo(c, s["code"], 340, l["top"] + 160, 300 * (.7 + .3 * q), clamp(q)); x = 560; y = l["top"] + 120
        text(c, "₹", x, y, 150, "interB", LK.RED, a); text(c, f'{s["cr"]:g} CR', x + 100, y, 160, "interB", gfx.INK, a, track=-3)
        text(c, f'{s["slots"]} slots · {s["ovs"]} overseas', x, y + 60, 34, "monoSB", gfx.MUTED, a)
        hz = E.fit(s["head"].upper(), l["x1"] - 560, 70, "interB", -2)
        text(c, s["head"].upper(), 560, y + 150, hz, "interB", LK.RED, eo(prog(t, .2, .6)), track=-2); by = y + 215; cols = 3; step = 110; bh = 34
    bars = s["bars"]; n = len(bars); bw = (l["x1"] - l["x0"] - 40 * (cols - 1)) / cols
    for k, (nm, v) in enumerate(bars):
        qq = stag(t, D, k, n, .25, .5); cx = l["x0"] + (k % cols) * (bw + 40); cy = by + (k // cols) * step
        rrect(c, cx, cy, bw, bh, 8, (224, 222, 214), qq); rrect(c, cx, cy, max(10, bw * min(v, 1.3) / 1.3 * qq), bh, 8, cc(v), qq)
        text(c, nm, cx, cy + bh + 34, 28 if sh else 26, "interSB", gfx.INK, qq); text(c, f"{v:.2f}", cx + bw, cy + bh + 34, 36 if sh else 30, "interB", cc(v), qq, "r")
    fy = by + (math.ceil(n / cols)) * step + (10 if sh else 0)
    text(c, s["fits"], l["x0"], min(fy, l["bot"] + 10) if not sh else fy, 30 if sh else 30, "interSB", gfx.INK, eo(prog(t, D * .55, D * .55 + .6)))
    text(c, "OUR MODEL · IPL 2025-26 · NOT A FRANCHISE PLAN", l["x0"], (min(fy, l["bot"] + 10) if not sh else fy) + 44, 20, "mono", gfx.MUTED, eo(prog(t, D * .6, D * .6 + .6)))


def sc_needs_pool(c, g, t, D, s):
    LK.header(c, g, t, D, s); l = LK.L(g); sh = g.fmt == "short"; bx = s["boxes"]; cols = 1 if sh else 2
    gap = 30; bw = (l["x1"] - l["x0"] - gap * (cols - 1)) / cols; rows = math.ceil(len(bx) / cols); bh = (l["bot"] - l["top"] - gap * (rows - 1)) / rows
    for k, b in enumerate(bx):
        q = stag(t, D, k, len(bx), .08, .6); x = l["x0"] + (k % cols) * (bw + gap); y = l["top"] + (k // cols) * (bh + gap); k_ = {"g": GRN, "a": AMB, "r": LK.RED}[b["c"]]
        rrect(c, x, y, bw, bh, 20, (255, 255, 255), q, stroke=5, scol=k_, sa=q)
        text(c, b["h"], x + 36, y + bh * .42, min(80, bh * .4), "interB", k_, q, track=-1)
        for j, ln in enumerate(E.wrap(b["d"], bw - 72, 32 if sh else 34, "interSB")[:2]): text(c, ln, x + 36, y + bh * .68 + j * 42, 32 if sh else 34, "interSB", gfx.INK, q)


def sc_needs_bids(c, g, t, D, s):
    LK.header(c, g, t, D, s); l = LK.L(g); sh = g.fmt == "short"; items = s["items"]; n = len(items); rh = (l["bot"] - l["top"]) / n
    for k, it in enumerate(items):
        q = stag(t, D, k, n, .08, .65); y = l["top"] + k * rh; nx = l["x0"] + (70 if sh else 80)
        text(c, str(k + 1), l["x0"], y + rh * (.5 if sh else .72), rh * (.5 if sh else .8), "interB", LK.RED, q)
        if sh:
            z = E.fit(it["name"].upper(), l["x1"] - nx, 54, "interB", -1)
            text(c, it["name"].upper(), nx, y + rh * .32, z, "interB", gfx.INK, q, track=-1); text(c, it["why"], nx, y + rh * .32 + 36, 28, "inter", gfx.MUTED, q)
            for j, code in enumerate(it["buyers"]): logo(c, code, nx + 38 + j * 84, y + rh * .78, 66, q)
        else:
            z = E.fit(it["name"].upper(), (l["x1"] - nx) - 520, 56, "interB", -1)
            text(c, it["name"].upper(), nx, y + rh * .5, z, "interB", gfx.INK, q, track=-1); text(c, it["why"], nx, y + rh * .5 + 38, 26, "inter", gfx.MUTED, q)
            sz = rh * .66
            for j, code in enumerate(it["buyers"]): logo(c, code, l["x1"] - sz * .55 - (len(it["buyers"]) - 1 - j) * (sz * 1.1), y + rh * .45, sz, q)


def install(engine, looks):
    global E, LK
    E = engine; LK = looks
    E.SCENES.update({"needs_hook": sc_needs_hook, "needs_purse": sc_needs_purse, "needs_map": sc_needs_map, "needs_team": sc_needs_team, "needs_pool": sc_needs_pool, "needs_bids": sc_needs_bids})
