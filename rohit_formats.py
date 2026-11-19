"""Format ideas (stills, NOT a render) for the silent 'Rohit Sharma, MI captain' video: five new looks, two frames each, real data (every IPL season 2008-2026).
The dashed boxes are where Rohit's cut-out goes (owner-supplied PNG). Output: deliver/_trades_mockups/rf_<concept>_<n>.png and rf_ALL.png.   python3 rohit_formats.py"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trades_mockups as T
from rohit_storyboard import placeholder, pill
from PIL import Image, ImageDraw
O = T.O; W, H = 1080, 1920; BEB, INT, INTS, GOLD, WHITE = T.BEB, T.INT, T.INTS, T.GOLD, T.WHITE
A = json.load(open("data/provenance/rohit_all_seasons.json")); M = json.load(open("data/provenance/rohit_mi_figures.json"))
S = {int(k): v for k, v in A["seasons"].items()}; MI = {int(k): v for k, v in M["mi_by_season"].items()}
MIB, DCY, RED, MUTED = (0, 85, 200), (240, 190, 40), (225, 60, 70), (170, 185, 215); YRS = list(range(2008, 2027))


def strip(c, y=1560, t="OUR DATA: EVERY IPL SEASON, 2008-2026"): T.txt(c, t, (W / 2, y), T.INT(24), (210, 220, 240), "mm", 5)


# ---------------------------------------------------------------- 1. CAREER RIBBON: the seasons run across like a film strip; the cursor sits on one
def ribbon(n):
    c = T.bg(W, H, (6, 12, 30), (14, 24, 52)); d = ImageDraw.Draw(c, "RGBA")
    if n == 1:
        pill(c, "ROHIT SHARMA · 19 SEASONS", (60, 215)); placeholder(c, (330, 330, 750, 900), "ROHIT\nCUT-OUT")
        T.txt(c, "7,329", (W / 2, 1000), BEB(250), GOLD, "mm", 4); T.txt(c, "IPL RUNS · 275 INNINGS · 324 SIXES", (W / 2, 1130), INT(28), WHITE, "mm", 5)
    else:
        pill(c, "2013 · THE CAPTAINCY BEGINS", (60, 215)); T.txt(c, "538", (W / 2, 520), BEB(360), GOLD, "mm", 4); T.txt(c, "RUNS IN HIS FIRST SEASON AS CAPTAIN", (W / 2, 700), BEB(54), WHITE, "mm", 5)
        T.txt(c, "MI 13-6 · THE FIRST TITLE", (W / 2, 790), BEB(60), (140, 200, 255), "mm", 5)
    y0 = 1260 if n == 1 else 1000; step = 150; cur = 2013 if n == 2 else None
    d.rounded_rectangle((20, y0 - 20, W - 20, y0 + 270), 24, fill=(255, 255, 255, 14))
    for i, y in enumerate(YRS):
        x = 60 + i * 52; col = DCY if y <= 2010 else MIB; h = 190 * S[y]["runs"] / 540; hot = (cur == y)
        d.rounded_rectangle((x, y0 + 230 - h, x + 40, y0 + 230), 8, fill=col + ((255,) if (cur is None or hot) else (110,))); T.txt(c, str(y)[2:], (x + 20, y0 + 256), BEB(26), WHITE if hot else MUTED, "mm", 1)
        if MI[y]["title"] or y == 2009: T.txt(c, "★", (x + 20, y0 + 230 - h - 26), INT(34), GOLD, "mm")
    if n == 2:
        x = 60 + 5 * 52; d.rounded_rectangle((x - 12, y0 - 10, x + 52, y0 + 275), 12, outline=GOLD + (255,), width=5); T.txt(c, "C", (x + 20, y0 - 44), BEB(60), GOLD, "mm"); strip(c, y0 + 340)
        T.txt(c, "THE RIBBON SCROLLS ACROSS THE SEASONS; THE BIG NUMBER CHANGES WITH THE CURSOR", (W / 2, 1640), INT(22), (150, 165, 195), "mm", 3)
    else: strip(c, y0 + 340)
    c.save(O + f"rf_ribbon_{n}.png")


# ---------------------------------------------------------------- 2. SEASON RING: runs as a radial bar chart, his portrait in the centre
def ring(n):
    c = T.bg(W, H, (4, 10, 28), (0, 40, 110)); d = ImageDraw.Draw(c, "RGBA"); cx, cy = W // 2, 880; r0, rmax = 250, 400
    pill(c, "EVERY SEASON, ONE RING", (60, 215))
    vals = [S[y]["runs"] if n == 1 else MI[y]["W"] for y in YRS]; mx = 540 if n == 1 else 14
    for i, y in enumerate(YRS):
        a = math.radians(-90 + i * 360 / len(YRS)); L = r0 + (rmax - 40) * vals[i] / mx
        col = (DCY if y <= 2010 else MIB) if n == 1 else ((120, 135, 170) if y < 2013 else (MIB if y <= 2023 else RED))
        x0_, y0_ = cx + r0 * math.cos(a), cy + r0 * math.sin(a); x1_, y1_ = cx + L * math.cos(a), cy + L * math.sin(a)
        d.line([(x0_, y0_), (x1_, y1_)], fill=col + (255,), width=34)
        tx, ty = cx + (r0 - 38) * math.cos(a), cy + (r0 - 38) * math.sin(a); T.txt(c, str(y)[2:], (tx, ty), BEB(26), MUTED, "mm", 1)
        title = MI[y]["title"] or (n == 1 and y == 2009)
        if title: T.txt(c, "★", (cx + (L + 30) * math.cos(a), cy + (L + 30) * math.sin(a)), INT(34), GOLD, "mm")
    d.ellipse((cx - 180, cy - 180, cx + 180, cy + 180), fill=(6, 20, 60, 255), outline=(255, 255, 255, 120), width=3)
    if n == 1: placeholder(c, (cx - 130, cy - 150, cx + 130, cy + 150), "ROHIT"); T.txt(c, "7,046 RUNS THROUGH 2025", (W / 2, 1400), BEB(80), GOLD, "mm", 5); T.txt(c, "BAR = RUNS IN THAT SEASON · YELLOW DECCAN, BLUE MUMBAI", (W / 2, 1480), INT(24), MUTED, "mm", 4)
    else: T.txt(c, "MI WINS", (cx, cy - 20), BEB(80), WHITE, "mm", 6); T.txt(c, "BY SEASON", (cx, cy + 50), INT(26), MUTED, "mm", 6); T.txt(c, "★ = TITLE · BLUE ROHIT · RED HARDIK", (W / 2, 1480), INT(26), WHITE, "mm", 4)
    strip(c); c.save(O + f"rf_ring_{n}.png")


# ---------------------------------------------------------------- 3. STADIUM SCOREBOARD: a big LED board; numbers tick up
def board(n):
    c = T.bg(W, H, (8, 12, 22), (18, 26, 46)); d = ImageDraw.Draw(c, "RGBA"); AMB = (255, 190, 40)
    for k in range(0, 1080, 60): d.ellipse((k + 20, 90, k + 40, 110), fill=(255, 255, 255, 90))
    d.rounded_rectangle((50, 180, 1030, 1480), 30, fill=(6, 8, 14, 255), outline=(90, 100, 130, 255), width=8)
    d.rounded_rectangle((70, 200, 1010, 330), 18, fill=(0, 60, 150, 255)); T.txt(c, "MUMBAI INDIANS · IPL 2027" if n == 1 else "MI · BY ERA", (540, 265), BEB(76), WHITE, "mm", 8)
    if n == 1:
        rows = [("ROHIT SHARMA", ""), ("IPL RUNS", "7,046"), ("IPL SIXES", "303"), ("IPL TITLES", "6"), ("AS CAPTAIN", "5 FINALS · 5 TITLES")]
        for i, (a, b) in enumerate(rows):
            y = 420 + i * 210; T.txt(c, a, (110, y), BEB(70 if i else 100), AMB if i == 0 else (200, 205, 220), "lm", 5)
            if b: T.txt(c, b, (970, y + (60 if i else 0)), BEB(150 if i < 4 else 70), AMB, "rm" if i < 4 else "rm", 3)
        placeholder(c, (640, 360, 980, 600), "")
    else:
        T.txt(c, "SEASON    CAPTAIN    W-L", (110, 400), BEB(48), (150, 160, 190), "lm", 4)
        for i, y in enumerate((2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026)):
            yy = 470 + i * 70; hot = y in (2015, 2017, 2019, 2020); cap = "ROHIT" if y <= 2023 else "HARDIK"; col = AMB if hot else ((140, 200, 255) if y <= 2023 else (255, 120, 125))
            T.txt(c, str(y), (110, yy), BEB(54), col, "lm", 3); T.txt(c, cap, (330, yy), BEB(54), col, "lm", 3); T.txt(c, f'{MI[y]["W"]}-{MI[y]["L"]}' + ("  ★" if hot else ""), (640, yy), BEB(54), col, "lm", 3)
    strip(c, 1530); c.save(O + f"rf_board_{n}.png")


# ---------------------------------------------------------------- 4. FACE-OFF: the trades split, two eras
def faceoff(n):
    c = Image.new("RGB", (W, H), (9, 14, 30)); d = ImageDraw.Draw(c)
    for y in range(960): t = y / 960; d.line([(0, y), (W, y)], fill=(0, int(60 + 30 * (1 - t)), int(190 - 50 * t)))
    for y in range(960, H): t = (y - 960) / 960; d.line([(0, y), (W, y)], fill=(int(210 - 50 * t), int(45 - 20 * t), int(55 - 20 * t)))
    d.polygon([(0, 905), (W, 800), (W, 1010), (0, 1115)], fill=(9, 14, 30))
    pill(c, "WITH ROHIT  vs  WITHOUT", (36, 215), size=34); placeholder(c, (560, 280, 1040, 880), "ROHIT"); placeholder(c, (40, 1120, 480, 1560), "HARDIK")
    a, b = M["mi_under_rohit_2014_2023"], M["mi_under_hardik_2024_2026"]
    if n == 1:
        T.txt(c, "2014-2023", (40, 330), BEB(60), (200, 225, 255), "lt", 6); T.txt(c, f'{a["W"]}-{a["L"]}', (40, 400), BEB(220), WHITE, "lt", 3, True); T.txt(c, f'{a["win_pct"]:.0f}% OF MATCHES', (44, 640), BEB(58), GOLD, "lt", 5)
        T.txt(c, "2024-2026", (1040, 1140), BEB(60), (255, 215, 215), "rt", 6); T.txt(c, f'{b["W"]}-{b["L"]}', (1040, 1210), BEB(220), WHITE, "rt", 3, True); T.txt(c, f'{b["win_pct"]:.0f}% OF MATCHES', (1036, 1450), BEB(58), GOLD, "rt", 5)
    else:
        T.txt(c, "PLAYOFFS", (40, 330), BEB(60), (200, 225, 255), "lt", 6); T.txt(c, f'{a["playoffs"]} OF 10', (40, 400), BEB(190), WHITE, "lt", 3, True); T.txt(c, "SEASONS · 4 TITLES", (44, 600), BEB(58), GOLD, "lt", 5)
        T.txt(c, "PLAYOFFS", (1040, 1140), BEB(60), (255, 215, 215), "rt", 6); T.txt(c, f'{b["playoffs"]} OF 3', (1040, 1210), BEB(190), WHITE, "rt", 3, True); T.txt(c, "SEASONS · 0 TITLES", (1036, 1410), BEB(58), GOLD, "rt", 5)
    strip(c, 1590); c.save(O + f"rf_faceoff_{n}.png")


# ---------------------------------------------------------------- 5. PLAYER CARD: the front is the portrait, the back is the seasons
def card(n):
    c = T.bg(W, H, (30, 20, 6), (8, 12, 30)); d = ImageDraw.Draw(c, "RGBA"); x0, y0, x1, y1 = 140, 250, 940, 1500
    d.rounded_rectangle((x0 - 14, y0 - 14, x1 + 14, y1 + 14), 56, fill=GOLD + (255,)); d.rounded_rectangle((x0, y0, x1, y1), 44, fill=(10, 18, 44, 255))
    if n == 1:
        placeholder(c, (x0 + 50, y0 + 60, x1 - 50, y1 - 330), "ROHIT\nCUT-OUT"); T.txt(c, "ROHIT", (540, y1 - 230), BEB(130), WHITE, "mm", 6); T.txt(c, "SHARMA", (540, y1 - 120), BEB(130), GOLD, "mm", 6)
        for i, (v, l) in enumerate((("7,046", "RUNS"), ("303", "SIXES"), ("6", "TITLES"))): T.txt(c, v, (x0 + 150 + i * 250, y0 + 120), BEB(70), GOLD, "mm", 2); T.txt(c, l, (x0 + 150 + i * 250, y0 + 175), INT(20), MUTED, "mm", 4)
    else:
        T.txt(c, "ROHIT SHARMA · EVERY SEASON", (540, y0 + 70), BEB(54), GOLD, "mm", 6)
        for i, y in enumerate(YRS):
            r, k = i % 4, i // 4; xx = x0 + 60 + r * 175; yy = y0 + 150 + k * 215; col = DCY if y <= 2010 else MIB; d.rounded_rectangle((xx, yy, xx + 150, yy + 190), 14, fill=col + (255,), outline=(255, 255, 255, 120), width=2)
            T.txt(c, str(y), (xx + 75, yy + 36), BEB(40), WHITE if col == MIB else (9, 14, 30), "mm", 2); T.txt(c, str(S[y]["runs"]), (xx + 75, yy + 105), BEB(66), WHITE if col == MIB else (9, 14, 30), "mm", 1)
            if MI[y]["title"] or y == 2009: T.txt(c, "★", (xx + 75, yy + 160), INT(30), GOLD if col == MIB else (9, 14, 30), "mm")
        T.txt(c, "RUNS PER SEASON · ★ TITLE", (540, y1 - 60), INT(24), MUTED, "mm", 5)
    strip(c, 1580); c.save(O + f"rf_card_{n}.png")


if __name__ == "__main__":
    for f in (ribbon, ring, board, faceoff, card):
        for n in (1, 2): f(n)
    names = [f"rf_{k}_{n}" for n in (1, 2) for k in ("ribbon", "ring", "board", "faceoff", "card")]
    sh = Image.new("RGB", (360 * 5, 640 * 2), (10, 10, 10))
    for i, nm in enumerate(names): sh.paste(Image.open(O + nm + ".png").convert("RGB").resize((360, 640)), ((i % 5) * 360, (i // 5) * 640))
    sh.save(O + "rf_ALL.png"); print("ok", sh.size)
