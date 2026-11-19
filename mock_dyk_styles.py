"""Mock-ups of four new looks for the Did You Know? series (the board look is too similar from episode to episode). One frame each for 'Where is third man?'.
    python3 mock_dyk_styles.py     -> out/_mock/dyk_style_<a|b|c|d>.png and a contact sheet"""
import math, random, os
import numpy as np, skia
import engine as E, gfx
from gfx import paint, text, rrect, twidth

W, H = 1080, 1920
POS = {"keeper": (0, .28), "slip": (.09, .31), "2nd slip": (.17, .34), "gully": (.31, .31), "point": (.5, .16), "cover": (.58, -.1), "mid-off": (.4, -.5), "mid-on": (-.4, -.5),
       "midwicket": (-.6, -.05), "square leg": (-.55, .2), "fine leg": (-.55, .7), "third man": (.56, .74)}


def new():
    arr = np.zeros((H, W, 4), np.uint8); sf = skia.Surface(arr); return arr, sf, sf.getCanvas()


def save(arr, sf, name):
    sf.flushAndSubmit(); skia.Image.fromarray(arr, colorType=skia.kRGBA_8888_ColorType).save(f"out/_mock/{name}.png", skia.kPNG); return name


def jline(c, p0, p1, p, r, j=3.0, seg=14):
    pa = skia.Path(); pa.moveTo(*p0)
    for k in range(1, seg + 1):
        f = k / seg; pa.lineTo(p0[0] + (p1[0] - p0[0]) * f + r.uniform(-j, j), p0[1] + (p1[1] - p0[1]) * f + r.uniform(-j, j))
    c.drawPath(pa, p)


def jcircle(c, cx, cy, rad, p, r, j=3.0, n=60):
    pa = skia.Path()
    for k in range(n + 3):
        a = 2 * math.pi * k / n; rr = rad + r.uniform(-j, j)
        (pa.moveTo if k == 0 else pa.lineTo)(cx + rr * math.cos(a), cy + rr * math.sin(a))
    c.drawPath(pa, p)


# ---------------------------------------------------------------- A: the field-guide plate (cream paper, ink, numbered figures)
def mock_a():
    arr, sf, c = new(); r = random.Random(4)
    c.clear(skia.Color(238, 226, 196))
    for _ in range(2600): c.drawCircle(r.random() * W, r.random() * H, r.uniform(.6, 2.2), paint((150, 120, 70), r.uniform(.04, .14)))
    INK = (52, 36, 26); RED = (160, 40, 36)
    for o, w_ in ((70, 3), (88, 1.5)): c.drawRect(skia.Rect.MakeLTRB(o, o + 150, W - o, H - o - 150), paint(INK, .9, stroke=w_))
    text(c, "PLATE I", W / 2, 400, 34, "serifI", INK, .8, "c", track=10)
    text(c, "THE THIRD MAN", W / 2, 500, 88, "serifBI", INK, 1, "c")
    text(c, "a fielder of the off side, far behind the wicket", W / 2, 560, 38, "serifI", INK, .85, "c")
    cx, cy, R = W / 2, 1010, 400
    p = paint(INK, .85, stroke=3)
    jcircle(c, cx, cy, R, p, r, 3); jcircle(c, cx, cy, R * .55, paint(INK, .35, stroke=2), r, 3)
    for k in range(70):                                                   # hatching on the boundary ring, engraving style
        a = 2 * math.pi * k / 70; jline(c, (cx + (R - 22) * math.cos(a), cy + (R - 22) * math.sin(a)), (cx + R * math.cos(a), cy + R * math.sin(a)), paint(INK, .5, stroke=1.6), r, .8, 2)
    c.drawRect(skia.Rect.MakeLTRB(cx - 14, cy - R * .2, cx + 14, cy + R * .2), paint((215, 190, 140), .9)); c.drawRect(skia.Rect.MakeLTRB(cx - 14, cy - R * .2, cx + 14, cy + R * .2), paint(INK, .8, stroke=2))
    figs = [("keeper", "1"), ("slip", "2"), ("gully", "3"), ("third man", "4")]
    for nm, num in figs:
        x, y = cx + POS[nm][0] * R, cy + POS[nm][1] * R; hot = nm == "third man"
        c.drawCircle(x, y + 22, 13, paint((0, 0, 0), .15))
        c.drawCircle(x, y - 22, 11, paint(RED if hot else INK, .95)); jline(c, (x, y - 11), (x, y + 14), paint(RED if hot else INK, .95, stroke=7), r, .6, 3)
        jline(c, (x - 14, y - 3), (x + 14, y - 3), paint(RED if hot else INK, .95, stroke=4), r, .6, 3)
        off = {"keeper": (-70, 70), "slip": (-10, 78), "gully": (30, 56), "third man": (-96, -44)}[nm]
        text(c, "Fig. " + num, x + off[0], y + off[1], 30, "serifI", RED if hot else INK, 1)
    jline(c, (cx + POS["third man"][0] * R - 20, cy + POS["third man"][1] * R - 50), (cx + 300, cy + 130), paint(RED, .8, stroke=2.5), r, 1.5)
    text(c, "batter", cx - 90, cy - R * .2 - 14, 26, "serifI", INK, .8)
    leg = ["Fig. 1  Wicket-keeper", "Fig. 2  First slip", "Fig. 3  Gully", "Fig. 4  Third man  (the subject of this plate)"]
    for i, t in enumerate(leg): text(c, t, 150, 1500 + i * 46, 32, "serifI", RED if i == 3 else INK, .95)
    c.save(); c.translate(870, 1560); c.rotate(-12)
    c.drawCircle(0, 0, 92, paint(RED, .9, stroke=5)); c.drawCircle(0, 0, 78, paint(RED, .9, stroke=2))
    text(c, "DID YOU", 0, -8, 34, "bebas", RED, .95, "c", track=3); text(c, "KNOW?", 0, 30, 40, "bebas", RED, .95, "c", track=3); c.restore()
    return save(arr, sf, "dyk_style_a")


# ---------------------------------------------------------------- B: the chalkboard (hand-drawn chalk, arrows, scribbled notes)
def mock_b():
    arr, sf, c = new(); r = random.Random(9)
    g = skia.Paint(); g.setShader(skia.GradientShader.MakeRadial((W / 2, H / 2), 1300, [skia.Color(44, 78, 62), skia.Color(24, 44, 36)], [0, 1])); c.drawRect(skia.Rect.MakeWH(W, H), g)
    for _ in range(900): c.drawCircle(r.random() * W, r.random() * H, r.uniform(1, 4), paint((255, 255, 255), r.uniform(.01, .045)))
    for k in range(5): c.drawRect(skia.Rect.MakeXYWH(0, 120 + k * 380 + r.uniform(-30, 30), W, r.uniform(20, 60)), paint((255, 255, 255), .015))
    CH = (244, 242, 232); YL = (255, 214, 90); PK = (255, 140, 150)
    def chalk(txt, x, y, size, col, tf="serifBI", a=.95, al="c"):
        for k in range(2): text(c, txt, x + r.uniform(-1.4, 1.4), y + r.uniform(-1.2, 1.2), size, tf, col, a * (.8 if k else 1), al)
    chalk("Where is", W / 2, 440, 66, CH); chalk("THIRD MAN?", W / 2, 560, 130, YL, "bebas")
    cx, cy, R = W / 2, 1020, 410; pc = paint(CH, .9, stroke=5); pc.setStrokeCap(skia.Paint.kRound_Cap)
    jcircle(c, cx, cy, R, pc, r, 3.5); d = paint(CH, .5, stroke=3); d.setPathEffect(skia.DashPathEffect.Make([16, 14], 0)); jcircle(c, cx, cy, R * .55, d, r, 3)
    jline(c, (cx - 14, cy - R * .2), (cx - 14, cy + R * .2), pc, r, 2); jline(c, (cx + 14, cy - R * .2), (cx + 14, cy + R * .2), pc, r, 2)
    jline(c, (cx - 14, cy - R * .2), (cx + 14, cy - R * .2), pc, r, 2); jline(c, (cx - 14, cy + R * .2), (cx + 14, cy + R * .2), pc, r, 2)
    for nm in ("keeper", "slip", "2nd slip", "gully"):
        x, y = cx + POS[nm][0] * R, cy + POS[nm][1] * R; jcircle(c, x, y, 13, paint(CH, .9, stroke=4), r, 1.5, 16)
    x, y = cx + POS["third man"][0] * R, cy + POS["third man"][1] * R
    jcircle(c, x, y, 20, paint(YL, .95, stroke=6), r, 2, 18); jcircle(c, x, y, 34, paint(YL, .6, stroke=3), r, 3, 24)
    chalk("third man", x - 20, y + 80, 52, YL, "serifBI", 1, "c")
    ar = skia.Path(); ar.moveTo(cx + 40, cy + R * .3 + 60); ar.cubicTo(cx + 180, cy + R * .35 + 160, cx + 280, cy + R * .6, x - 40, y - 30)
    pa = paint(PK, .95, stroke=6); pa.setStrokeCap(skia.Paint.kRound_Cap); c.drawPath(ar, pa)
    ah = skia.Path(); ah.moveTo(x - 40, y - 30); ah.lineTo(x - 78, y - 24); ah.lineTo(x - 52, y - 62); ah.close(); c.drawPath(ah, paint(PK, .95))
    chalk("edge!", cx + 235, cy + R * .27 + 150, 44, PK, "serifI")
    chalk("off side →", cx + R - 40, cy - R * .55, 38, CH, "serifI", .9)
    chalk("keeper", cx - 130, cy + R * .28 + 60, 34, CH, "serifI", .85)
    chalk("~ stops the edges that beat the slips ~", W / 2, 1540, 40, CH, "serifI", .9)
    return save(arr, sf, "dyk_style_b")


# ---------------------------------------------------------------- C: tracking HUD (dark, glowing grid, readouts)
def mock_c():
    arr, sf, c = new(); r = random.Random(2)
    c.clear(skia.Color(4, 10, 16)); TL = (70, 240, 220); AM = (255, 190, 60)
    for gx in range(0, W + 1, 60): c.drawLine(gx, 280, gx, 1640, paint(TL, .07))
    for gy in range(280, 1641, 60): c.drawLine(0, gy, W, gy, paint(TL, .07))
    text(c, "TRACKING · FIELD VIEW", 70, 340, 28, "monoSB", TL, .9, track=4); text(c, "REC ●", W - 70, 340, 28, "monoSB", (255, 80, 80), .95, "r", track=4)
    text(c, "WHERE IS", W / 2, 470, 62, "bebas", (220, 250, 250), .95, "c", track=8); text(c, "THIRD MAN?", W / 2, 590, 140, "bebas", TL, 1, "c", glow=22)
    cx, cy, R = W / 2, 1030, 410
    for k, rr in enumerate((R, R * .78, R * .55, R * .33)): c.drawCircle(cx, cy, rr, paint(TL, .5 if k == 0 else .22, stroke=3 if k == 0 else 2))
    for a in range(0, 360, 30): c.drawLine(cx, cy, cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a)), paint(TL, .08))
    c.drawRect(skia.Rect.MakeLTRB(cx - 14, cy - R * .2, cx + 14, cy + R * .2), paint(TL, .25)); c.drawRect(skia.Rect.MakeLTRB(cx - 14, cy - R * .2, cx + 14, cy + R * .2), paint(TL, .9, stroke=2))
    for nm in ("keeper", "slip", "2nd slip", "gully", "point", "cover", "mid-off", "mid-on", "midwicket", "square leg", "fine leg"):
        x, y = cx + POS[nm][0] * R, cy + POS[nm][1] * R; c.drawCircle(x, y, 9, paint(TL, .9)); c.drawCircle(x, y, 17, paint(TL, .35, stroke=2))
    x, y = cx + POS["third man"][0] * R, cy + POS["third man"][1] * R
    for rr, al in ((52, .25), (36, .5)): c.drawCircle(x, y, rr, paint(AM, al, stroke=3))
    c.drawCircle(x, y, 13, paint(AM, 1)); c.drawLine(cx, cy + R * .2, x, y, paint(AM, .7, stroke=2))
    rrect(c, x - 330, y - 160, 300, 118, 8, (8, 22, 30), .9, stroke=2, scol=AM)
    for i, t in enumerate(("THIRD MAN", "OFF SIDE · BEHIND WICKET", "BOUNDARY EDGE ZONE")): text(c, t, x - 316, y - 120 + i * 32, 24 if i else 30, "monoSB", AM if i == 0 else (220, 250, 250), .95)
    text(c, "ILLUSTRATIVE", 70, 1600, 22, "mono", TL, .6, track=4); text(c, "RH BATTER", W - 70, 1600, 22, "mono", TL, .6, "r", track=4)
    sc = paint(TL, .18); c.drawRect(skia.Rect.MakeXYWH(0, 700, W, 5), sc); c.drawRect(skia.Rect.MakeXYWH(0, 697, W, 12), paint(TL, .05))
    return save(arr, sf, "dyk_style_c")


# ---------------------------------------------------------------- D: the rulebook page (parchment, Law numeral, highlighter, margin notes, stamp)
def mock_d():
    arr, sf, c = new(); r = random.Random(7)
    c.clear(skia.Color(224, 214, 190)); P = (250, 244, 228); INK = (34, 34, 40); HL = (255, 226, 70); RED = (190, 38, 40)
    c.save(); c.translate(W / 2, 960); c.rotate(-1.2)
    c.drawRect(skia.Rect.MakeLTRB(-440, -700, 460, 740), paint((0, 0, 0), .22, blur=24)); c.drawRect(skia.Rect.MakeLTRB(-450, -710, 450, 730), paint(P))
    text(c, "28", -60, 130, 640, "bebas", (60, 40, 20), .06, "c")
    text(c, "THE LAWS OF CRICKET · THE FIELDER", -410, -640, 24, "mono", (90, 70, 50), .9, track=3)
    text(c, "Where is", -410, -540, 70, "serifBI", INK, 1); text(c, "THIRD MAN?", -410, -420, 138, "bebas", INK, 1)
    for i, (w_, hl) in enumerate([(780, 0), (700, 1), (760, 1), (520, 0), (780, 0), (640, 0), (760, 0), (400, 0)]):
        y = -330 + i * 58
        if hl: c.drawRect(skia.Rect.MakeXYWH(-410, y - 34, w_, 44), paint(HL, .8))
        c.drawRect(skia.Rect.MakeXYWH(-410, y - 20, w_ * .97, 9), paint(INK, .78 if hl else .55))
    cx, cy, R = 40, 360, 215
    c.drawCircle(cx, cy, R, paint((120, 160, 110), .35)); c.drawCircle(cx, cy, R, paint(INK, .8, stroke=3)); c.drawRect(skia.Rect.MakeLTRB(cx - 9, cy - R * .2, cx + 9, cy + R * .2), paint((215, 190, 140), .95))
    for nm in ("keeper", "slip", "2nd slip", "gully", "point", "cover"): c.drawCircle(cx + POS[nm][0] * R, cy + POS[nm][1] * R, 8, paint(INK, .9))
    c.drawCircle(cx + POS["third man"][0] * R, cy + POS["third man"][1] * R, 11, paint(RED, 1)); c.drawCircle(cx + POS["third man"][0] * R, cy + POS["third man"][1] * R, 21, paint(RED, .9, stroke=3))
    text(c, "third man", cx + POS["third man"][0] * R - 170, cy + POS["third man"][1] * R + 46, 30, "serifI", RED, 1)
    text(c, "← behind the wicket,", -410, 640, 28, "serifI", RED, .95); text(c, "off side", -410, 676, 28, "serifI", RED, .95)
    c.restore()
    c.save(); c.translate(860, 330); c.rotate(14); rrect(c, -150, -46, 300, 92, 6, RED, .0, stroke=6, scol=RED, sa=.9)
    text(c, "DID YOU KNOW?", 0, 14, 44, "bebas", RED, .95, "c", track=3); c.restore()
    
    return save(arr, sf, "dyk_style_d")


if __name__ == "__main__":
    names = [mock_a(), mock_b(), mock_c(), mock_d()]
    from PIL import Image
    ims = [Image.open(f"out/_mock/{n}.png").convert("RGB").resize((540, 960)) for n in names]
    sheet = Image.new("RGB", (540 * 4 + 30, 960), (20, 20, 20))
    for i, im in enumerate(ims): sheet.paste(im, (i * 550, 0))
    sheet.save("out/_mock/dyk_styles_sheet.png"); print("ok")
