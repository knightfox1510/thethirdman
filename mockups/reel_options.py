"""Mockup stills for new reel formats (Vaibhav 204 as the sample content). Three options x four frames; not part of the engine.   python3 mockups/reel_options.py"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import skia, gfx, engine  # engine import registers the fonts
from gfx import text, rrect, paint
W, H = 1080, 1920; OUT = "mockups/out"; os.makedirs(OUT, exist_ok=True)
IN = "data/licensed/in/"; U = json.load(open("data/provenance/vaibhav_uae_figures.json"))
GOLD = (245, 200, 60); RED = (226, 52, 60); NAVY = (8, 14, 34); PAPER = (244, 241, 234); GREEN = (34, 120, 70); INKD = (20, 20, 24); LIME = (190, 235, 60)
SAMP = skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear); _I = {}
def img(p):
    if p not in _I: _I[p] = skia.Image.open(p)
    return _I[p]
def cover(c, p, x, y, w, h, crop=None, a=1.0, r=0):
    im = img(p); iw, ih = im.width(), im.height()
    if crop is None:
        k = max(w / iw, h / ih); sw, sh = w / k, h / k; crop = ((iw - sw) / 2, (ih - sh) / 2, (iw + sw) / 2, (ih + sh) / 2)
    c.save()
    if r: c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r), doAntiAlias=True)
    c.drawImageRect(im, skia.Rect.MakeLTRB(*crop), skia.Rect.MakeXYWH(x, y, w, h), SAMP, paint((255, 255, 255), a)); c.restore()
def grad(c, y0, y1, c0, c1, a0=1, a1=1, x0=0, x1=W):
    sh = skia.GradientShader.MakeLinear([(0, y0), (0, y1)], [skia.Color(*c0, int(255 * a0)), skia.Color(*c1, int(255 * a1))])
    p = skia.Paint(Shader=sh); c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), p)
def frame(draw):
    s = skia.Surface(W, H); c = s.getCanvas(); draw(c); return s.makeImageSnapshot()
def save(name, im): im.save(f"{OUT}/{name}.png"); return im
def outline(c, x, y, w, h, r, col, sw=5):
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r), paint(col, 1, stroke=sw))
def tag(c, s, x, y, col=RED, size=26, tc=(255, 255, 255)):
    wd = gfx.twidth(s, size, "monoSB", 2) + 36; rrect(c, x, y, wd, size + 24, 8, col, 1); text(c, s, x + 18, y + size + 7, size, "monoSB", tc, 1, track=2); return wd
def brand(c, dark=True):
    text(c, "THE THIRD MAN", 60, 92, 26, "monoSB", GOLD if dark else RED, 1, track=3); text(c, "VAIBHAV · 204 OFF 53", W - 60, 92, 22, "monoSB", (150, 160, 185) if dark else (110, 110, 110), 1, "r", track=2)
BALLS = [("s", 6)] * 28 + [("f", 4)] * 7 + [("d", 0)] * 11 + [("o", 1)] * 7
import random; random.Random(5).shuffle(BALLS)
def ribbon(c, y, lit, dark=True, h=70, x0=60, x1=W - 60):
    n = len(BALLS); w = (x1 - x0) / n
    for i, (k, r) in enumerate(BALLS):
        col = {"s": GOLD, "f": RED, "o": (200, 200, 200) if dark else (120, 120, 120), "d": (60, 70, 100) if dark else (205, 203, 196)}[k]; hh = {"s": h, "f": h * .75, "o": h * .45, "d": h * .2}[k]
        on = i < lit; rrect(c, x0 + i * w + 1.5, y + h - hh, w - 3, hh, 3, col, 1 if on else .18)
def pitch_persp(c, top=700, bot=1800, a=1.0):
    p = skia.Path(); p.moveTo(W / 2 - 170, top); p.lineTo(W / 2 + 170, top); p.lineTo(W / 2 + 480, bot); p.lineTo(W / 2 - 480, bot); p.close()
    c.drawPath(p, paint((226, 214, 170), a)); c.drawPath(p, paint((255, 255, 255), .35 * a, stroke=4))
def night(c):
    grad(c, 0, H, (6, 10, 26), (10, 40, 30), 1, 1); c.drawRect(skia.Rect.MakeLTRB(0, 560, W, H), paint((20, 90, 56), 1))
    grad(c, 560, H, (18, 70, 44), (8, 40, 28), 1, 1)
    for x in (230, 850):
        p = skia.Path(); p.moveTo(x, 120); p.lineTo(x - 260, 1100); p.lineTo(x + 260, 1100); p.close(); c.drawPath(p, paint((255, 245, 200), .07, blur=18))
        for k in range(3): c.drawRect(skia.Rect.MakeXYWH(x - 38 + k * 26, 104, 22, 22), paint((255, 250, 220), .95, blur=2))
def dotgrid(c, cx, top, bot, lit, rows=8):
    n = len(BALLS); cols = math.ceil(n / rows); k = 0
    for r_ in range(rows):
        t = r_ / (rows - 1); y = top + (bot - top) * t; half = 150 + 300 * t; dx = 2 * half / (cols + 1)
        for j in range(cols):
            if k >= n: break
            kk, rr = BALLS[k]; x = cx - half + dx * (j + 1); rad = 14 + 20 * t; on = k < lit
            col = {"s": GOLD, "f": RED, "o": (255, 255, 255), "d": (130, 120, 90)}[kk]
            if on: c.drawCircle(x, y, rad * (1.5 if kk == "s" else 1), paint(col, .45 if kk != "d" else .0, blur=14))
            c.drawCircle(x, y, rad, paint(col, 1 if on else .22)); k += 1
def A1(c):
    night(c); brand(c); pitch_persp(c, 860, 1820); dotgrid(c, W / 2, 980, 1700, 53)
    text(c, "ONE BOY. FIFTY-THREE BALLS.", W / 2, 250, 40, "monoSB", (200, 210, 235), 1, "c", track=3)
    text(c, "204", W / 2, 700, 440, "interB", GOLD, 1, "c", track=-10, glow=60); text(c, "28 SIXES · 7 FOURS · 11 DOTS", W / 2, 800, 38, "monoSB", (255, 255, 255), 1, "c", track=2)
def A2(c):
    night(c); brand(c); pitch_persp(c, 600, 1820); dotgrid(c, W / 2, 760, 1650, 53)
    text(c, "EVERY LIGHT IS A BALL", W / 2, 300, 66, "interB", PAPER, 1, "c", track=-1); text(c, "GOLD = SIX · RED = FOUR · DIM = DOT", W / 2, 370, 30, "monoSB", GOLD, 1, "c", track=2)
    rrect(c, 130, 450, 820, 130, 16, (14, 22, 50), .85, stroke=3, scol=GOLD, sa=1); text(c, "96% OF HIS RUNS CAME IN BOUNDARIES", W / 2, 535, 40, "interB", PAPER, 1, "c")
def A3(c):
    night(c); brand(c); pitch_persp(c, 900, 1820, .8)
    text(c, "WHY IT WORKS", W / 2, 230, 60, "interB", GOLD, 1, "c", track=-1)
    c.save(); c.translate(W / 2, 1000); c.rotate(-2.5); rrect(c, -400, -560, 800, 1120, 14, (246, 240, 222), 1); cover(c, IN + "vaibhav_technique_ref.jpg", -360, -520, 720, 540, crop=(110, 0, 510, 608), r=6)
    text(c, "1  BAT PAST THE VERTICAL", -360, 80, 46, "interB", INKD, 1); text(c, "A longer arc and more time to build bat speed.", -360, 140, 32, "inter", (70, 70, 70), 1)
    text(c, "2  CLOSED SHOULDERS", -360, 230, 46, "interB", INKD, 1); text(c, "Separation: more force when the body unwinds.", -360, 290, 32, "inter", (70, 70, 70), 1)
    text(c, "3  BRACED FRONT KNEE", -360, 380, 46, "interB", INKD, 1); text(c, "Weight transfer becomes rotation.", -360, 440, 32, "inter", (70, 70, 70), 1); c.restore()
def A4(c):
    night(c); brand(c); text(c, "SO WHERE IS", W / 2, 520, 110, "interB", PAPER, 1, "c", track=-3); text(c, "THE WEAKNESS?", W / 2, 650, 120, "interB", GOLD, 1, "c", track=-3, glow=40)
    for i, (n, s) in enumerate((("1", "LEFT-ARM PACE"), ("2", "THE RED BALL"), ("3", "NOWHERE YET"))):
        y = 820 + i * 190; rrect(c, 110, y, 860, 150, 20, (14, 22, 50), .9, stroke=3, scol=GOLD if i == 0 else (60, 80, 140), sa=1); c.drawCircle(200, y + 75, 44, paint(GOLD, 1)); text(c, n, 200, y + 100, 64, "interB", NAVY, 1, "c"); text(c, s, 280, y + 98, 54, "interB", PAPER, 1)
    ribbon(c, 1700, 53)
def paper(c):
    c.drawRect(skia.Rect.MakeWH(W, H), paint(PAPER, 1))
    for x in range(0, W, 60): c.drawLine(x, 0, x, H, paint((0, 0, 0), .035, stroke=1))
    for y in range(0, H, 60): c.drawLine(0, y, W, y, paint((0, 0, 0), .035, stroke=1))
def B1(c):
    paper(c); brand(c, False); ribbon(c, 190, 53, False, 90)
    text(c, "BALL BY BALL", 60, 150, 24, "monoSB", RED, 1, track=3); text(c, "204", W / 2, 900, 540, "interB", INKD, 1, "c", track=-20)
    text(c, "OFF 53 BALLS", W / 2, 1010, 74, "interB", RED, 1, "c"); tag(c, "INDIA A V UAE · 24 NOV 2026", 60, 1110, INKD)
    cover(c, IN + "vaibhav_celebration.webp", 60, 1230, 960, 520, crop=(0, 60, 718, 538), r=24); outline(c, 60, 1230, 960, 520, 24, INKD)
    text(c, "AGED 15 YEARS, 8 MONTHS", 60, 1830, 36, "monoSB", INKD, 1, track=2)
def B2(c):
    paper(c); brand(c, False); ribbon(c, 190, 28, False, 90); text(c, "BALL 28 · THE HUNDRED", 60, 150, 24, "monoSB", RED, 1, track=3)
    text(c, "28 SIXES", 60, 420, 150, "interB", INKD, 1, track=-5); R = 400; cx, cy = W / 2, 1050
    c.drawCircle(cx, cy, R, paint((226, 233, 214), 1)); c.drawCircle(cx, cy, R, paint(INKD, 1, stroke=5)); c.drawCircle(cx, cy, R * .5, paint(INKD, .3, stroke=2)); rrect(c, cx - 15, cy - 8, 30, 150, 4, (214, 196, 150), 1)
    for r in U["rows"]:
        if r["ang"] is None or r["res"] not in ("SIX", "FOUR"): continue
        th = math.radians(r["ang"]); ln = R * (1.03 if r["res"] == "SIX" else .95); c.drawLine(cx, cy, cx + math.sin(th) * ln, cy + math.cos(th) * ln, paint(RED if r["res"] == "SIX" else (226, 150, 24), .85, stroke=4))
    for i, (v, l) in enumerate((("12", "LEG SIDE"), ("7", "STRAIGHT"), ("9", "OFF SIDE"))):
        x = 60 + i * 330; rrect(c, x, 1530, 300, 190, 18, (255, 255, 255), 1, stroke=3, scol=RED if i == 1 else INKD, sa=1); text(c, v, x + 150, 1640, 100, "interB", RED if i == 1 else INKD, 1, "c"); text(c, l, x + 150, 1695, 26, "monoSB", (110, 110, 110), 1, "c", track=2)
def B3(c):
    paper(c); brand(c, False); ribbon(c, 190, 53, False, 90); text(c, "BIG TEAMS, SMALL TEAMS?", 60, 360, 66, "interB", INKD, 1, track=-2); text(c, "IN THE IPL IT FLIPS", 60, 440, 36, "monoSB", RED, 1, track=3)
    for i, (l, v, mx, col) in enumerate((("TOP FOUR SIDES", 248, 260, RED), ("THE REST", 207, 260, INKD))):
        y = 600 + i * 260; text(c, l, 60, y, 34, "monoSB", (110, 110, 110), 1, track=2); rrect(c, 60, y + 30, 960 * v / mx, 130, 14, col, 1); text(c, str(v), 60 + 960 * v / mx - 30, y + 125, 100, "interB", (255, 255, 255), 1, "r")
    text(c, "STRIKE RATE · 23 IPL INNINGS", 60, 1170, 26, "monoSB", (110, 110, 110), 1, track=2)
    rrect(c, 60, 1300, 960, 330, 22, INKD, 1); text(c, "PLAYOFFS", 110, 1380, 30, "monoSB", GOLD, 1, track=3); text(c, "193 off 76", 110, 1520, 150, "interB", PAPER, 1, track=-4); text(c, "ELIMINATOR 97 · QUALIFIER TWO 96", 110, 1590, 30, "monoSB", (180, 190, 210), 1, track=2)
def B4(c):
    paper(c); brand(c, False); ribbon(c, 190, 53, False, 90); text(c, "THE TECHNIQUE", 60, 150, 24, "monoSB", RED, 1, track=3)
    cover(c, IN + "vaibhav_technique_graphic2.png", 60, 300, 960, 540, crop=(215, 0, 600, 595), r=0) if False else cover(c, IN + "vaibhav_technique_graphic2.png", 60, 300, 520, 800, crop=(215, 0, 600, 595), r=20)
    outline(c, 60, 300, 520, 800, 20, INKD); c.drawOval(skia.Rect.MakeXYWH(340, 850, 210, 170), paint(RED, 1, stroke=9))
    text(c, "3", 640, 400, 120, "interB", RED, 1); text(c, "BRACED", 640, 520, 64, "interB", INKD, 1, track=-1); text(c, "FRONT KNEE", 640, 590, 64, "interB", INKD, 1, track=-1)
    for i, s in enumerate(("Like a fast bowler's", "front leg: the lower", "body stops, the upper", "body flings through.")): text(c, s, 640, 690 + i * 44, 31, "inter", (60, 60, 60), 1)
    for i, (t, s) in enumerate((("1  BAT PAST THE VERTICAL", "done"), ("2  CLOSED SHOULDERS", "done"), ("3  BRACED FRONT KNEE", "now"), ("4  THE O FOLLOW-THROUGH", "next"))):
        y = 1230 + i * 120; rrect(c, 60, y, 960, 96, 14, INKD if s == "now" else (255, 255, 255), 1, stroke=3, scol=INKD, sa=1); text(c, t, 100, y + 64, 40, "interB", PAPER if s == "now" else (INKD if s == "done" else (150, 150, 150)), 1)
def poster_bg(c, photo, crop, tint=(10, 22, 70)):
    cover(c, photo, 0, 0, W, H, crop=crop); c.drawRect(skia.Rect.MakeWH(W, H), paint(tint, .55)); grad(c, 1100, H, (6, 10, 30), (6, 10, 30), 0, .96); grad(c, 0, 380, (6, 10, 30), (6, 10, 30), .85, 0)
def sticker(c, s, x, y, rot, col=GOLD, tc=NAVY, size=54):
    c.save(); c.translate(x, y); c.rotate(rot); wd = gfx.twidth(s, size, "interB", -1) + 60; rrect(c, -wd / 2, -50, wd, 100, 14, col, 1); text(c, s, 0, 20, size, "interB", tc, 1, "c", track=-1); c.restore()
def C1(c):
    poster_bg(c, IN + "vaibhav_celebration.webp", (0, 0, 718, 898)); brand(c)
    text(c, "204", W / 2, 1000, 640, "interB", (255, 255, 255), .0, "c"); text(c, "204", W / 2, 1080, 540, "interB", GOLD, 1, "c", track=-18, glow=40)
    sticker(c, "28 SIXES", 270, 1230, -6); sticker(c, "SR 385", 780, 1300, 5, RED, (255, 255, 255)); sticker(c, "AGE 15", 330, 1400, 3, (255, 255, 255)); text(c, "VAIBHAV SURYAVANSHI", 60, 1560, 66, "interB", PAPER, 1, track=-2); text(c, "INDIA A V UAE · 53 BALLS", 60, 1620, 30, "monoSB", GOLD, 1, track=3); ribbon(c, 1700, 53)
def C2(c):
    poster_bg(c, IN + "vaibhav_portrait.jpg", (380, 0, 1100, 720), (8, 14, 40)); brand(c); text(c, "15 YEARS,", 60, 1240, 130, "interB", PAPER, 1, track=-4); text(c, "8 MONTHS.", 60, 1370, 130, "interB", GOLD, 1, track=-4, glow=30)
    text(c, "THE YOUNGEST MAN TO PLAY FOR INDIA", 60, 1450, 30, "monoSB", (200, 210, 235), 1, track=2); sticker(c, "1,028 IPL RUNS", 400, 1590, -3, RED, (255, 255, 255), 52); ribbon(c, 1700, 53)
def C3(c):
    c.drawRect(skia.Rect.MakeWH(W, H), paint(NAVY, 1)); grad(c, 0, H, (10, 20, 60), (4, 8, 22), 1, 1); brand(c)
    cover(c, IN + "vaibhav_technique_ref.jpg", 140, 220, 800, 1220, crop=(110, 0, 510, 608), r=26); outline(c, 140, 220, 800, 1220, 26, LIME)
    c.drawOval(skia.Rect.MakeXYWH(660, 300, 260, 230), paint(LIME, 1, stroke=10)); sticker(c, "BAT PAST THE VERTICAL", 540, 1500, -2, LIME, NAVY, 46); text(c, "A longer arc, more time to build bat speed.", W / 2, 1610, 34, "inter", PAPER, 1, "c"); ribbon(c, 1700, 53)
def C4(c):
    c.drawRect(skia.Rect.MakeWH(W, H), paint(NAVY, 1)); grad(c, 0, H, (10, 20, 60), (4, 8, 22), 1, 1); brand(c); text(c, "THE SCORECARD", 60, 220, 28, "monoSB", GOLD, 1, track=3)
    for i, (v, l, col) in enumerate((("385", "STRIKE RATE", GOLD), ("96%", "OF RUNS IN BOUNDARIES", RED), ("11", "DOT BALLS OF 53", (255, 255, 255)), ("12", "BALLS PER FIFTY AFTER THE FIRST", LIME))):
        y = 290 + i * 320; c.save(); c.translate(540, y + 140); c.rotate((-1.5, 1.2, -0.8, 1.0)[i]); rrect(c, -480, -140, 960, 280, 22, (14, 24, 60), 1, stroke=3, scol=col, sa=1); text(c, v, -430, 60, 190, "interB", col, 1, track=-6, glow=20); text(c, l, 120, 20, 30, "monoSB", PAPER, 1, "c", track=2) if False else text(c, l, -430, 110, 30, "monoSB", PAPER, 1, track=2); c.restore()
    ribbon(c, 1700, 53)
OPT = {"A_night_pitch": (A1, A2, A3, A4), "B_ball_ribbon": (B1, B2, B3, B4), "C_poster": (C1, C2, C3, C4)}
for name, fs in OPT.items():
    ims = [save(f"{name}_{i + 1}", frame(f)) for i, f in enumerate(fs)]
    sh = skia.Surface(4 * 420 + 50, 760 + 20); c = sh.getCanvas(); c.drawRect(skia.Rect.MakeWH(sh.width(), sh.height()), paint((30, 30, 34), 1))
    for i, im in enumerate(ims): c.drawImageRect(im, skia.Rect.MakeXYWH(10 + i * 430, 10, 420, 746), SAMP)
    sh.makeImageSnapshot().save(f"{OUT}/{name}_sheet.png"); print(name)
