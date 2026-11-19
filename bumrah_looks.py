"""Alternative look mock-ups for the Bumrah video: A broadsheet feature, B night cinematic, C biomechanics scan (with our own avatar sequence), plus the blueprint look with a photo filmstrip.   python3 bumrah_looks.py -> out/bumrah_looks.jpg (+ out/bumrah_looks/*.png)"""
import os, json, math, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
R = os.path.dirname(os.path.abspath(__file__)); FD = f"{R}/fonts/"; IN = f"{R}/data/licensed/in/"; CUT = f"{R}/data/licensed/cut/"; O = f"{R}/out/bumrah_looks"; os.makedirs(O, exist_ok=True)
F0 = json.load(open(f"{R}/data/provenance/bumrah_tests_figures.json")); F1 = json.load(open(f"{R}/data/provenance/bumrah_context_figures.json"))
def F(n, z): return ImageFont.truetype(FD + n, z)
PF = lambda z: F("PlayfairBold.ttf", z); PI = lambda z: F("PlayfairItalic.ttf", z); IB = lambda z: F("Inter-Bold.otf", z); IM = lambda z: F("Inter-Medium.otf", z); MO = lambda z: F("PlexMono.ttf", z); MB = lambda z: F("PlexMonoSB.ttf", z); BS = lambda z: F("BigShouldersBlack.ttf", z); TK = lambda z: F("TekoBold.ttf", z)
def cover(path, size, crop=None, dim=0, tint=None):
    p = Image.open(path).convert("RGB"); k = max(size[0] / p.width, size[1] / p.height); p = p.resize((int(p.width * k) + 1, int(p.height * k) + 1), Image.LANCZOS)
    if crop: l = int(crop[0] * (p.width - size[0])); t = int(crop[1] * (p.height - size[1]))
    else: l = (p.width - size[0]) // 2; t = (p.height - size[1]) // 2
    p = p.crop((l, t, l + size[0], t + size[1]))
    if dim: p = Image.blend(p, Image.new("RGB", p.size, tint or (0, 0, 0)), dim)
    return p
def grad(im, y0, y1, col, a0=0, a1=235, w=None):
    o = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(o)
    for y in range(y0, y1, 4): d.rectangle((0, y, im.width, y + 4), fill=col + (int(a0 + (a1 - a0) * (y - y0) / max(1, y1 - y0)),))
    im.alpha_composite(o)
def wrap(d, t, f, w):
    out, cur = [], ""
    for x in t.split():
        z = (cur + " " + x).strip()
        if d.textlength(z, font=f) > w and cur: out.append(cur); cur = x
        else: cur = z
    return out + [cur]
# ---------------------------------------------------------------- A: broadsheet
PAPER = (244, 238, 224); INKA = (24, 22, 20); REDA = (176, 36, 36)
def A_base(): im = Image.new("RGBA", (1920, 1080), PAPER); return im, ImageDraw.Draw(im)
def A_head(d, n, kick):
    d.line((70, 70, 1850, 70), fill=INKA, width=3); d.line((70, 78, 1850, 78), fill=INKA, width=1); d.text((70, 58), "THE THIRD MAN · A BUMRAH DOSSIER", font=MB(20), fill=INKA, anchor="ls"); d.text((1850, 58), f"No. {n} · {kick}", font=MB(20), fill=REDA, anchor="rs")
def A1():
    im, d = A_base(); A_head(d, 1, "THE WELLINGTON BALL")
    p = cover(IN + "bumrah_load_brisbane.jpg", (1100, 800), crop=(.4, .3)); im.paste(p, (70, 130)); d.rectangle((70, 130, 1170, 930), outline=INKA, width=3)
    d.text((70, 960), "FIG. 1  Loading at the Gabba: the arm cocked behind the head, the ball already out of sight.", font=PI(24), fill=INKA)
    d.text((1230, 220), "Why", font=PF(100), fill=INKA); d.text((1230, 330), "Bumrah", font=PF(150), fill=REDA); d.text((1230, 500), "cannot be", font=PF(100), fill=INKA); d.text((1230, 610), "played.", font=PF(100), fill=INKA)
    for j, t in enumerate(wrap(d, "A stuttering run-up, a hyperextended elbow, a fractured back, and the best bowling average in the history of Test cricket.", IM(30), 600)): d.text((1230, 780 + j * 42), t, font=IM(30), fill=INKA)
    return im.convert("RGB")
def A2():
    im, d = A_base(); A_head(d, 2, "THE ACTION")
    d.text((70, 150), "Five frames of one delivery", font=PF(70), fill=INKA); w, h = 340, 470
    for i, (nm, lab, crop) in enumerate((("bumrah_load_brisbane.jpg", "1 · LOAD", (.5, .3)), ("bumrah_side_jump_clean.jpg", "2 · LEAP", (.3, .2)), ("bumrah_side_jump_leeds.jpg", "3 · BOUND", (.3, .2)), ("bumrah_high_arm_closeup.jpg", "4 · RELEASE", (.8, .3)), ("bumrah_bowls_brook_lords.jpg", "5 · THE RESULT", (.5, .5)))):
        x = 70 + i * 356; im.paste(cover(IN + nm, (w, h), crop=crop), (x, 260)); d.rectangle((x, 260, x + w, 260 + h), outline=INKA, width=2); d.text((x, 760), f"FIG. {lab}", font=MB(22), fill=REDA)
    for j, (t, y) in enumerate((("The run-up is short and stuttering. A longer one, Holding argues, would make him less effective.", 810), ("The elbow hyperextends; the release is about half a metre closer to the batter.", 870), ("Backspin adds about five centimetres of bounce off a good length.", 930))): d.text((70, y), t, font=IM(27), fill=INKA)
    return im.convert("RGB")
def A3():
    im, d = A_base(); A_head(d, 3, "THE LEDGER")
    d.text((70, 150), "234 wickets at 19.79.", font=PF(110), fill=INKA); d.line((70, 300, 1850, 300), fill=INKA, width=2)
    rows = [("Runs per wicket", "19.79", "26.1"), ("Balls per wicket", "42.9", "49.7"), ("Wickets bowled or lbw", f"{F1['bumrah_bowled_lbw_pct']}%", f"{F1['baseline_bowled_lbw_pct']}%"), ("Average with the old ball / the new ball", "18.2", "23.9")]
    d.text((1180, 335), "BUMRAH", font=MB(24), fill=REDA); d.text((1500, 335), "47 OTHER QUICKS", font=MB(24), fill=INKA)
    for i, (a, b, c) in enumerate(rows):
        y = 400 + i * 120; d.text((70, y), a, font=PF(40), fill=INKA); d.text((1180, y - 6), b, font=PF(70), fill=REDA); d.text((1500, y - 6), c, font=PF(70), fill=INKA); d.line((70, y + 80, 1850, y + 80), fill=(190, 180, 160), width=1)
    d.text((70, 960), "Cricsheet men's Tests since 2018 · our archive", font=PI(24), fill=INKA); d.rectangle((1520, 880, 1850, 1010), outline=REDA, width=3); d.text((1685, 960), "BEST AVERAGE, 200+ WKTS", font=MB(18), fill=REDA, anchor="mm")
    return im.convert("RGB")
# ---------------------------------------------------------------- B: night cinematic
def B1():
    im = cover(IN + "bumrah_side_jump_leeds.jpg", (1920, 1080), crop=(.5, .4), dim=.45, tint=(0, 0, 10)).convert("RGBA"); grad(im, 500, 1080, (4, 6, 14)); d = ImageDraw.Draw(im)
    d.text((100, 640), "INDIA'S ONE-MAN", font=BS(70), fill=(255, 200, 80)); d.text((100, 710), "UNPLAYABLE", font=BS(260), fill=(250, 250, 250)); d.line((100, 1010, 560, 1010), fill=(255, 200, 80), width=6)
    return im.convert("RGB")
def B2():
    im = cover(IN + "bumrah_load_brisbane.jpg", (1920, 1080), crop=(.3, .2), dim=.55, tint=(0, 0, 10)).convert("RGBA"); d = ImageDraw.Draw(im)
    for i, (x, t, s) in enumerate(((120, "THE RUN-UP", "Short. Stuttering."), (720, "THE ARM", "Bends the 'wrong' way."), (1320, "THE RELEASE", "Half a metre closer."))):
        o = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(o).rounded_rectangle((x, 640, x + 480, 940), 20, fill=(10, 14, 26, 190), outline=(255, 200, 80, 255), width=3); im.alpha_composite(o); d = ImageDraw.Draw(im)
        d.text((x + 36, 740), f"0{i + 1}", font=BS(90), fill=(255, 200, 80)); d.text((x + 36, 830), t, font=BS(60), fill=(250, 250, 250)); d.text((x + 36, 890), s, font=IM(28), fill=(200, 210, 230))
    return im.convert("RGB")
def B3():
    im = cover(IN + "bumrah_bowls_brook_lords.jpg", (1920, 1080), crop=(.5, .55), dim=.6, tint=(0, 0, 10)).convert("RGBA"); d = ImageDraw.Draw(im)
    d.text((100, 200), "52%", font=BS(480), fill=(255, 200, 80)); d.text((900, 330), "OF HIS TEST WICKETS", font=BS(90), fill=(250, 250, 250)); d.text((900, 430), "ARE BOWLED OR LBW", font=BS(90), fill=(250, 250, 250)); d.text((900, 560), f"The other fast bowlers since 2018: {round(F1['baseline_bowled_lbw_pct'])}%", font=IM(40), fill=(200, 210, 230))
    return im.convert("RGB")
# ---------------------------------------------------------------- C: biomechanics scan (own avatar)
def avatar_strip(w, h, n=6, scale=470, y=980, x0=170, dx=300, glow=True):
    import skia, engine as E, gfx, bum_action as B
    arr = np.zeros((h, w, 4), np.uint8); sf = skia.Surface(arr); c = sf.getCanvas(); c.clear(0)
    for i in range(n):
        B.E.avatar(c, x0 + i * dx, y, scale, (40, 200, 190), None, "bum", i / (n - 1), 1.0, dir=1, cap=True)
    sf.flushAndSubmit(); return Image.fromarray(arr.copy(), "RGBA")
def C_base():
    im = Image.new("RGBA", (1920, 1080), (4, 10, 14)); d = ImageDraw.Draw(im)
    for y in range(0, 1080, 6): d.line((0, y, 1920, y), fill=(8, 20, 24))
    return im, d
TEAL = (50, 230, 200)
def C1():
    im, d = C_base(); d.text((90, 120), "SCAN 01 · JASPRIT BUMRAH · RIGHT-ARM FAST", font=MB(26), fill=TEAL)
    p = Image.open(CUT + "bumrah_side_jump_leeds.png").convert("RGBA"); p = p.crop(p.getbbox()); k = 900 / p.height; p = p.resize((int(p.width * k), 900), Image.LANCZOS)
    mono = p.convert("L").point(lambda v: v); tint = Image.new("RGBA", p.size, (30, 120, 120, 255)); tint.putalpha(p.split()[3]); tint = Image.blend(tint, Image.merge("RGBA", (mono, mono, mono, p.split()[3])).point(lambda v: int(v * .55)), .35)
    im.alpha_composite(tint, (1000, 150))
    for y in range(150, 1050, 14): d.line((960, y, 1700, y), fill=(50, 230, 200, 40))
    d.text((90, 520), "THE WRONG", font=TK(220), fill=(235, 250, 248)); d.text((90, 700), "ACTION.", font=TK(260), fill=TEAL)
    return im.convert("RGB")
def C2():
    im, d = C_base(); d.text((90, 100), "MOTION CAPTURE (ILLUSTRATIVE) · OUR OWN AVATAR · SIX PHASES OF ONE DELIVERY", font=MB(24), fill=TEAL)
    st = avatar_strip(1920, 1080, 6, 470, 900, 190, 310); sh = Image.new("RGBA", st.size, (0, 0, 0, 0)); sh.paste(st.filter(ImageFilter.GaussianBlur(14)), (0, 0)); im.alpha_composite(sh); im.alpha_composite(st); d = ImageDraw.Draw(im)
    import bum_action as B
    for i, (nm, _) in enumerate(B.KEYS):
        x = 190 + i * 310; d.line((x, 930, x, 960), fill=TEAL, width=2); d.text((x, 990), f"{i + 1} · {nm}", font=MB(20), fill=TEAL, anchor="ms")
    d.text((1100, 200), "RELEASE ARM: HYPEREXTENDED", font=MB(22), fill=(255, 200, 80)); d.arc((1500, 260, 1580, 340), 200, 330, fill=(255, 200, 80), width=4)
    return im.convert("RGB")
def C3():
    im, d = C_base(); d.text((90, 120), "RESULT · TESTS SINCE 2018", font=MB(26), fill=TEAL)
    d.text((90, 180), "52%", font=TK(420), fill=TEAL); d.text((960, 260), "BOWLED OR LBW", font=TK(120), fill=(235, 250, 248)); d.text((960, 400), f"vs {F1['baseline_bowled_lbw_pct']}% for 47 other quicks", font=IM(38), fill=(150, 200, 195))
    for i, (lab, v, mx, col) in enumerate((("BUMRAH", 19.79, 30, TEAL), ("THE REST", 26.1, 30, (90, 120, 125)))): y = 640 + i * 150; d.text((90, y), lab, font=MB(24), fill=(150, 200, 195)); d.rectangle((90, y + 36, 90 + 1100 * v / mx, y + 100), fill=col); d.text((90 + 1100 * v / mx + 20, y + 98), f"{v}", font=TK(80), fill=col, anchor="ls")
    return im.convert("RGB")
# ---------------------------------------------------------------- blueprint + photo filmstrip
def D2():
    BG = (12, 22, 42); CY = (64, 210, 240); AM = (255, 176, 32); MU = (128, 150, 184); WH = (240, 244, 250)
    im = Image.new("RGBA", (1920, 1080), BG); d = ImageDraw.Draw(im)
    for x in range(0, 1920, 60): d.line((x, 0, x, 1080), fill=(22, 38, 68))
    for y in range(0, 1080, 60): d.line((0, y, 1920, y), fill=(22, 38, 68))
    d.text((60, 56), "03 · THE ACTION", font=MB(24), fill=CY, anchor="ls"); d.line((60, 72, 1860, 72), fill=CY, width=2); d.text((60, 150), "One delivery,", font=TK(110), fill=WH); d.text((60, 240), "five frames.", font=TK(110), fill=AM)
    for i, (nm, lab, crop) in enumerate((("bumrah_load_brisbane.jpg", "LOAD", (.5, .3)), ("bumrah_side_jump_clean.jpg", "LEAP", (.3, .2)), ("bumrah_side_jump_leeds.jpg", "BOUND", (.3, .2)), ("bumrah_high_arm_closeup.jpg", "RELEASE", (.8, .3)), ("bumrah_bowls_brook_lords.jpg", "RESULT", (.5, .5)))):
        x = 60 + i * 360; p = cover(IN + nm, (330, 520), crop=crop); im.paste(p, (x, 380)); d.rectangle((x, 380, x + 330, 900), outline=CY, width=2); d.text((x + 12, 930), f"{i + 1} · {lab}", font=MB(24), fill=CY)
    for x in (390, 750, 1110, 1470): d.polygon([(x + 6, 640), (x + 28, 652), (x + 6, 664)], fill=AM)
    return im.convert("RGB")
def sheet(rows, labels, path):
    tw, th = 640, 360; s = Image.new("RGB", (3 * (tw + 16) + 16, len(rows) * (th + 60) + 16), (255, 255, 255)); d = ImageDraw.Draw(s)
    for r, (fr, lab) in enumerate(zip(rows, labels)):
        y = 16 + r * (th + 60); d.text((16, y + 14), lab, font=IB(28), fill=(20, 20, 22), anchor="lm")
        for i, f in enumerate(fr): s.paste(f.resize((tw, th), Image.LANCZOS), (16 + i * (tw + 16), y + 36))
    s.save(path, quality=88)
if __name__ == "__main__":
    A = [A1(), A2(), A3()]; B_ = [B1(), B2(), B3()]; C = [C1(), C2(), C3()]; Dd = [D2()]
    for nm, fr in (("A", A), ("B", B_), ("C", C), ("D", Dd)):
        for i, f in enumerate(fr, 1): f.save(f"{O}/{nm}{i}.png")
    sheet([A, B_, C, Dd], ["A · BROADSHEET FEATURE: cream paper, serif, photo plates", "B · NIGHT CINEMATIC: full-bleed photos, big condensed type", "C · BIOMECHANICS SCAN: our own avatar sequence, glow, joint labels", "BLUEPRINT (as approved) with the photo filmstrip"], f"{R}/out/bumrah_looks.jpg"); print("ok")
