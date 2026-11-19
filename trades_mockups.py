"""Mock-ups (stills) for a NEW format for the IPL trades video, using the owner's licensed player images (17 Nov 2026). Not a build: ideas to choose from.
Writes deliver/_trades_mockups/*.png (vertical 1080x1920 unless noted).  python3 trades_mockups.py"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
R = os.path.dirname(os.path.abspath(__file__)); A = f"{R}/deliver/_trades_mockups/assets/"; O = f"{R}/deliver/_trades_mockups/"
F = lambda n, z: ImageFont.truetype(f"{R}/fonts/{n}", z)
BEB = lambda z: F("Bebas.ttf", z); INT = lambda z: F("Inter-Bold.otf", z); INTS = lambda z: F("Inter-SemiBold.otf", z)
NAVY, NAVY2, GOLD, WHITE, MUTED = (9, 14, 30), (22, 36, 72), (255, 200, 40), (255, 255, 255), (150, 160, 185)
MI, PBKS, CSK, SRH, DC, LSG, GT, RR = (0, 90, 200), (215, 40, 50), (250, 200, 20), (240, 110, 20), (30, 80, 190), (0, 150, 190), (30, 50, 110), (230, 60, 150)
im = lambda n: Image.open(A + n + ".png").convert("RGB")


def bg(w=1080, h=1920, top=NAVY, bot=NAVY2):
    g = Image.new("RGB", (w, h)); d = ImageDraw.Draw(g)
    for y in range(h):
        t = y / h; k = 1 - abs(2 * t - 1) * .0
        d.line([(0, y), (w, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * min(1, t * 1.6)) for i in range(3)))
    return g


def rr(img, xy, r, fill=None, outline=None, width=3):
    d = ImageDraw.Draw(img, "RGBA"); d.rounded_rectangle(xy, r, fill=fill, outline=outline, width=width)


SPECIAL = "₹↔→▸↔"


def txt(img, s, xy, font, fill=WHITE, anchor="la", track=0, shadow=False):
    d = ImageDraw.Draw(img, "RGBA")
    if any(ch in SPECIAL for ch in s):                      # per-character fallback to Inter for glyphs Bebas lacks
        alt = INT(int(font.size * 0.82)); parts = [(ch, alt if ch in SPECIAL else font) for ch in s]
        w = sum(d.textlength(ch, font=f) + track for ch, f in parts) - track; x, y = xy
        if anchor[0] == "m": x -= w / 2
        elif anchor[0] == "r": x -= w
        for ch, f in parts:
            d.text((x, y), ch, font=f, fill=fill, anchor="l" + anchor[1]); x += d.textlength(ch, font=f) + track
        return
    if track:
        w = sum(d.textlength(c, font=font) + track for c in s) - track; x, y = xy
        if anchor[0] == "m": x -= w / 2
        elif anchor[0] == "r": x -= w
        for c in s:
            if shadow: d.text((x + 3, y + 3), c, font=font, fill=(0, 0, 0, 140), anchor="l" + anchor[1])
            d.text((x, y), c, font=font, fill=fill, anchor="l" + anchor[1]); x += d.textlength(c, font=font) + track
    else:
        if shadow: d.text((xy[0] + 3, xy[1] + 3), s, font=font, fill=(0, 0, 0, 140), anchor=anchor)
        d.text(xy, s, font=font, fill=fill, anchor=anchor)


def paste(img, p, xy, w=None, h=None, r=0, border=None, bw=0):
    p = p.copy()
    if w and h:                                      # cover-fit crop
        s = max(w / p.width, h / p.height); p = p.resize((int(p.width * s) + 1, int(p.height * s) + 1), Image.LANCZOS)
        l, t = (p.width - w) // 2, 0; p = p.crop((l, t, l + w, t + h))
    elif w: s = w / p.width; p = p.resize((w, int(p.height * s)), Image.LANCZOS)
    m = Image.new("L", p.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, p.width, p.height), r, fill=255)
    if border: ImageDraw.Draw(img).rounded_rectangle((xy[0] - bw, xy[1] - bw, xy[0] + p.width + bw, xy[1] + p.height + bw), r + bw, fill=border)
    img.paste(p, xy, m); return p.size


def glowtext(img, s, xy, font, col, anchor="ma", track=2):
    g = Image.new("RGBA", img.size, (0, 0, 0, 0)); txt(g, s, xy, font, col + (255,), anchor, track); g = g.filter(ImageFilter.GaussianBlur(14))
    img.paste(g, (0, 0), g); txt(img, s, xy, font, col, anchor, track)


def header(img, k, n, title="TRADE WINDOW 2027"):
    rr(img, (60, 110, 60 + 640, 190), 40, fill=GOLD + (255,)); txt(img, f"IPL · {title}", (90, 150), BEB(54), NAVY, "lm", 3)
    txt(img, f"DEAL {k} OF {n}", (1020, 150), BEB(54), GOLD, "rm", 3)


# ------------------------------------------------------------------- A  THE DEAL DESK
def mock_a():
    c = bg(); header(c, 4, 6)
    sz = paste(c, im("mi_pbks"), (60, 260), w=960, r=28, border=GOLD, bw=6)
    y = 260 + sz[1] + 40
    txt(c, "MUMBAI  ↔  PUNJAB", (540, y + 40), BEB(92), WHITE, "mm", 4); txt(c, "LIKE FOR LIKE · ₹18 CR EACH", (540, y + 120), BEB(58), GOLD, "mm", 6)
    for k, (col, who, line1, line2) in enumerate(((MI, "MI GET  ARSHDEEP SINGH", "2026: 14 WICKETS", "ECONOMY 10.3 · 13 MATCHES"), (PBKS, "PBKS GET  HARDIK PANDYA", "2026: 206 RUNS · SR 138", "4 WICKETS · ECONOMY 11.4"))):
        x = 60 + k * 490; rr(c, (x, y + 190, x + 470, y + 460), 24, fill=(255, 255, 255, 18), outline=col + (255,), width=5)
        txt(c, who, (x + 235, y + 245), BEB(50), col if col != MI else (110, 170, 255), "mm", 2); txt(c, "OUR DATA · IPL 2026", (x + 235, y + 292), INT(22), MUTED, "mm", 4)
        txt(c, line1, (x + 235, y + 360), BEB(62), WHITE, "mm", 1); txt(c, line2, (x + 235, y + 420), INTS(26), MUTED, "mm", 1)
    rr(c, (0, 1730, 1080, 1850), 0, fill=(0, 0, 0, 120))                                          # the ticker
    txt(c, "MORE ▸ PANT ↔ KULDEEP · NATARAJAN → SRH · HARSHAL → GT · SHAMI ↔ CURRAN", (30, 1790), INT(26), GOLD, "lm", 2)
    for i in range(6): c_ = ImageDraw.Draw(c); c_.ellipse((430 + i * 40, 1690, 454 + i * 40, 1714), fill=GOLD if i == 3 else (80, 90, 120))
    c.save(O + "A_deal_desk.png")


# ------------------------------------------------------------------- B  SPLIT-SCREEN SWAP
def mock_b():
    c = Image.new("RGB", (1080, 1920), NAVY); d = ImageDraw.Draw(c)
    for y in range(960):                                                                           # MI half (top), PBKS half (bottom)
        t = y / 960; d.line([(0, y), (1080, y)], fill=(int(0 + 20 * t), int(60 + 40 * (1 - t)), int(190 - 60 * t)))
    for y in range(960, 1920):
        t = (y - 960) / 960; d.line([(0, y), (1080, y)], fill=(int(220 - 60 * t), int(40 - 20 * t), int(50 - 20 * t)))
    h = im("hardik"); a = im("arshdeep")
    paste(c, h, (520, 80), w=560, h=820, r=0); paste(c, a, (0, 1010), w=560, h=850, r=0)
    ImageDraw.Draw(c).polygon([(0, 905), (1080, 800), (1080, 1010), (0, 1115)], fill=NAVY)         # the slash
    glowtext(c, "SWAP", (540, 905), BEB(210), GOLD, "mm", 8)
    txt(c, "HARDIK", (40, 160), BEB(118), WHITE, "lt", 3, True); txt(c, "PANDYA", (40, 270), BEB(118), (110, 190, 255), "lt", 3, True); txt(c, "MI → PBKS", (44, 420), BEB(66), GOLD, "lt", 6)
    txt(c, "206 RUNS", (44, 540), BEB(60), WHITE, "lt", 2); txt(c, "SR 138 · 4 WKTS", (44, 610), BEB(46), WHITE, "lt", 2); txt(c, "2026 · OUR DATA", (44, 670), INT(24), (200, 220, 255), "lt", 3)
    txt(c, "ARSHDEEP", (1040, 1330), BEB(118), WHITE, "rt", 3, True); txt(c, "SINGH", (1040, 1440), BEB(118), (255, 150, 150), "rt", 3, True); txt(c, "PBKS → MI", (1036, 1590), BEB(66), GOLD, "rt", 6)
    txt(c, "14 WICKETS", (1036, 1090), BEB(60), WHITE, "rt", 2); txt(c, "ECONOMY 10.3", (1036, 1160), BEB(46), WHITE, "rt", 2); txt(c, "2026 · OUR DATA", (1036, 1220), INT(24), (255, 210, 210), "rt", 3)
    rr(c, (700, 1790, 1020, 1880), 30, fill=GOLD + (255,)); txt(c, "₹18 CR EACH", (860, 1836), BEB(60), NAVY, "mm", 3)
    c.save(O + "B_split_swap.png")


# ------------------------------------------------------------------- C  THE DEPARTURES BOARD (landscape 1920x1080)
def mock_c():
    c = bg(1920, 1080, (6, 10, 22), (14, 22, 46)); d = ImageDraw.Draw(c)
    txt(c, "IPL 2027 · TRADE WINDOW", (80, 80), BEB(96), GOLD, "lm", 6); txt(c, "6 DEALS · 15 PLAYERS MOVED", (1840, 80), BEB(56), WHITE, "rm", 4)
    d.line([(80, 140), (1840, 140)], fill=GOLD, width=4)
    rows = [("23 JUN", "PANT", "LSG", "DC", "₹15 CR", "pant"), ("23 JUN", "KULDEEP YADAV", "DC", "LSG", "₹13.5 CR", "kuldeep"), ("05 NOV", "LIVINGSTONE · EDWARDS", "SRH", "CSK", "₹6 + 3 CR", "livingstone"),
            ("05 NOV", "KHALEEL · ELLIS", "CSK", "SRH", "₹4.8 + 2 CR", "khaleel"), ("11 NOV", "HARDIK PANDYA", "MI", "PBKS", "₹18 CR", "hardik"), ("11 NOV", "ARSHDEEP SINGH", "PBKS", "MI", "₹18 CR", "arshdeep"),
            ("15 NOV", "HARSHAL PATEL", "SRH", "GT", "₹4 CR", "harshal"), ("17 NOV", "SHAMI · SIDDHARTH", "LSG", "RR", "₹8 CR + 75 L", None)]
    y = 175
    for k, (dt, nm, a, b, fee, ph) in enumerate(rows):
        hot = k == 4; h = 106 if hot else 92
        rr(c, (80, y, 1840, y + h), 14, fill=(255, 200, 40, 40) if hot else (255, 255, 255, 14), outline=GOLD + (255,) if hot else None, width=4)
        if ph:
            p = im(ph); s = max(84 / p.width, 84 / p.height) if False else 1
            sz = 82 if not hot else 96; pp = p.crop((0, 0, p.width, int(p.width * 1.0))).resize((sz, sz), Image.LANCZOS)
            m = Image.new("L", (sz, sz), 0); ImageDraw.Draw(m).ellipse((0, 0, sz, sz), fill=255); c.paste(pp, (100, y + (h - sz) // 2), m)
        txt(c, dt, (230, y + h / 2), BEB(54), MUTED, "lm", 3); txt(c, nm, (420, y + h / 2), BEB(66 if hot else 58), WHITE, "lm", 3)
        txt(c, a, (1080, y + h / 2), BEB(62), (160, 175, 210), "mm", 3); txt(c, "→", (1170, y + h / 2), BEB(62), GOLD, "mm"); txt(c, b, (1270, y + h / 2), BEB(62), GOLD, "mm", 3)
        txt(c, fee, (1810, y + h / 2), BEB(60), WHITE, "rm", 3); y += h + 10
    txt(c, "HIGHLIGHTED ROW OPENS INTO ITS OWN SCENE: THE BIGGEST SWAP, ₹18 CR EACH WAY", (80, 1048), INT(26), GOLD, "lm", 4)
    c.save(O + "C_departures_board.png")


# ------------------------------------------------------------------- D  DEAL CARDS (trading cards that cross over)
def card(canvas, photo, xy, col, name, role, lines, fee, rot):
    w, h = 470, 740; cd = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(cd)
    d.rounded_rectangle((20, 20, w + 20, h + 20), 30, fill=(12, 18, 38, 255), outline=col + (255,), width=8)
    paste(cd, photo, (36, 36), w=w - 32, h=470, r=22); d = ImageDraw.Draw(cd)
    txt(cd, name, (w // 2 + 20, 548), BEB(72), WHITE, "mm", 3); txt(cd, role, (w // 2 + 20, 598), INT(22), col, "mm", 5)
    for i, l in enumerate(lines): txt(cd, l, (w // 2 + 20, 650 + i * 44), BEB(40), (210, 220, 240), "mm", 2)
    rr(cd, (w - 150, 20, w + 12, 100), 26, fill=GOLD + (255,)); txt(cd, fee, (w - 69, 60), BEB(46), NAVY, "mm", 2)
    cd = cd.rotate(rot, expand=True, resample=Image.BICUBIC); canvas.paste(cd, xy, cd)


def mock_d():
    c = bg(); header(c, 5, 6)
    glowtext(c, "TRADED", (540, 330), BEB(150), GOLD, "mm", 10)
    card(c, im("kuldeep"), (20, 440), (0, 170, 220), "KULDEEP YADAV", "DC → LSG", ["2026: 10 WKTS", "ECONOMY 10.3"], "₹13.5 CR", -7)
    card(c, im("pant"), (570, 520), (230, 60, 80), "RISHABH PANT", "LSG → DC", ["2026: 312 RUNS", "STRIKE RATE 138"], "₹15 CR", 7)
    d = ImageDraw.Draw(c); d.polygon([(500, 960), (580, 960), (580, 1000), (640, 930), (580, 860), (580, 900), (500, 900)], fill=GOLD)
    txt(c, "WHAT CHANGES", (540, 1330), BEB(70), GOLD, "mm", 8)
    txt(c, "DC GET THEIR OLD CAPTAIN BACK:", (540, 1410), BEB(54), WHITE, "mm", 3); txt(c, "312 RUNS FOR A WRISTSPINNER'S 10 WICKETS", (540, 1480), BEB(54), WHITE, "mm", 3)
    txt(c, "OUR DATA · IPL 2026", (540, 1560), INT(26), MUTED, "mm", 5)
    c.save(O + "D_deal_cards.png")


# ------------------------------------------------------------------- E  THE TRADE MAP (network, photos as nodes)
def mock_e():
    import math
    c = bg(); header(c, 6, 6, "THE TRADE MAP")
    cx, cy, Rr = 540, 930, 370
    teams = ["CSK", "SRH", "DC", "LSG", "RR", "GT", "PBKS", "MI"]; col = {"CSK": CSK, "SRH": SRH, "DC": (60, 120, 230), "LSG": LSG, "RR": RR, "GT": (70, 100, 190), "PBKS": PBKS, "MI": MI}
    pos = {t: (cx + Rr * math.cos(math.radians(-90 + i * 45)), cy + Rr * math.sin(math.radians(-90 + i * 45))) for i, t in enumerate(teams)}
    edges = [("PBKS", "MI", 18, "₹18 CR ↔ ₹18 CR"), ("DC", "LSG", 14, "₹15 CR ↔ ₹13.5 CR"), ("SRH", "CSK", 9, "4 PLAYERS"), ("SRH", "DC", 5, "₹5 CR ↔ ₹0.4 CR"), ("SRH", "GT", 4, "₹4 CR"), ("LSG", "RR", 8, "₹8.75 CR ↔ ₹2.4 CR")]
    d = ImageDraw.Draw(c, "RGBA")
    for a, b, wgt, lab in edges:
        (x1, y1), (x2, y2) = pos[a], pos[b]; d.line([(x1, y1), (x2, y2)], fill=GOLD + (200,), width=max(4, wgt // 2))
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2; rr(c, (mx - 120, my - 24, mx + 120, my + 24), 24, fill=(9, 14, 30, 230), outline=GOLD + (255,), width=3); txt(c, lab, (mx, my), BEB(34), GOLD, "mm", 2)
    ph = {"MI": "hardik", "PBKS": "arshdeep", "DC": "kuldeep", "LSG": "pant", "CSK": "khaleel", "SRH": "livingstone", "GT": "harshal", "RR": None}
    for t, (x, y) in pos.items():
        r = 78; d.ellipse((x - r - 8, y - r - 8, x + r + 8, y + r + 8), fill=col[t] + (255,))
        if ph[t]:
            p = im(ph[t]); sz = 2 * r; pp = p.crop((0, 0, p.width, min(p.height, int(p.width * 1.0)))).resize((sz, sz), Image.LANCZOS)
            m = Image.new("L", (sz, sz), 0); ImageDraw.Draw(m).ellipse((0, 0, sz, sz), fill=255); c.paste(pp, (int(x - r), int(y - r)), m)
        else: d.ellipse((x - r, y - r, x + r, y + r), fill=(20, 28, 56, 255))
        txt(c, t, (x, y + r + 34), BEB(54), WHITE, "mm", 4)
    txt(c, "SIX DEALS · EIGHT FRANCHISES", (540, 1600), BEB(70), WHITE, "mm", 6); txt(c, "LINE WIDTH = MONEY MOVED", (540, 1670), INT(26), MUTED, "mm", 4)
    c.save(O + "E_trade_map.png")


if __name__ == "__main__":
    for f in (mock_a, mock_b, mock_c, mock_d, mock_e): f(); print("ok", f.__name__)
