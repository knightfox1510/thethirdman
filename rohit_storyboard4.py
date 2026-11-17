"""Storyboard v4 (stills, NOT a render): concept 'THE MUMBAI LOCAL' for the silent 'Mumbai cha Raja' Rohit Sharma video. Rules (owner, 17 Nov 2026): no Bumrah, NO video slots (images only), every IPL season 2008-2026.
World: Mumbai suburban-railway signage. The 19 seasons are stations on one line (yellow = Deccan Chargers 2008-10, blue = Mumbai Indians 2011-26), titles are interchange stops, the stats are departure boards, tickets and a season pass.
Years are also shown in Devanagari numerals (Marathi). Data: data/provenance/rohit_all_seasons.json, rohit_mi_figures.json. Photos: owner's throne graphic (watermark cropped out; rights to be confirmed), plain dashed boxes = images to come.   python3 rohit_storyboard4.py"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rohit_storyboard2 import *                 # deva, pill, strip, face_circle, score, slot, S, MI, M, THRONE, FACE, YRS, MIB, DCY, RED, GOLD, WHITE, MUTED, T, W, H, O, BEB, INT
import rohit_storyboard2 as B
from rohit_storyboard3 import crown
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AMB = (255, 176, 30); CHAR = (22, 24, 30); RAIL_Y = (252, 204, 0); BLK = (14, 14, 16); TEAL = (0, 150, 140)
DN = str.maketrans("0123456789", "०१२३४५६७८९")
dn = lambda s: str(s).translate(DN)


def dfont(size): return ImageFont.truetype("fonts/NotoSansDevanagari-Bold.ttf", size, layout_engine=ImageFont.Layout.RAQM)


def station_bg():
    c = T.bg(W, H, (30, 33, 40), (12, 13, 17)); d = ImageDraw.Draw(c, "RGBA")
    for x in range(0, W, 120): d.rectangle((x, 0, x + 6, 150), fill=(255, 255, 255, 14))         # station roof rafters
    d.rectangle((0, 0, W, 16), fill=RAIL_Y + (255,)); return c


def sign(c, box, text, sub=None, fill=RAIL_Y, col=BLK, size=64):
    d = ImageDraw.Draw(c, "RGBA"); d.rounded_rectangle(box, 12, fill=fill + (255,), outline=(0, 0, 0, 255), width=6); x0, y0, x1, y1 = box
    T.txt(c, text, ((x0 + x1) / 2, (y0 + y1) / 2 - (14 if sub else 0)), BEB(size), col, "mm", 5)
    if sub and any(ord(ch) > 0x900 for ch in sub): ImageDraw.Draw(c).text(((x0 + x1) / 2, y1 - 30), sub, font=dfont(30), fill=col, anchor="mm")
    elif sub: T.txt(c, sub, ((x0 + x1) / 2, y1 - 30), INT(22), col, "mm", 4)


def led(c, text, xy, size, col=AMB, anchor="mm", deva_font=False):
    """Amber dot-matrix look: draw the text, then punch a dot grid over it."""
    L = Image.new("RGBA", c.size, (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    if deva_font: d.text(xy, text, font=dfont(size), fill=col + (255,), anchor=anchor)
    else: T.txt(L, text, xy, BEB(size), col, anchor, 4)
    mask = Image.new("L", c.size, 0); md = ImageDraw.Draw(mask)
    for y in range(0, c.size[1], 6):
        for x in range(0, c.size[0], 6): md.ellipse((x, y, x + 4, y + 4), fill=255)
    a = L.getchannel("A"); L.putalpha(Image.composite(a, Image.new("L", c.size, 0), mask)); g = L.filter(ImageFilter.GaussianBlur(7)); c.paste(g, (0, 0), g); c.paste(L, (0, 0), L)


def board(c, box):
    d = ImageDraw.Draw(c, "RGBA"); d.rounded_rectangle(box, 18, fill=BLK + (255,), outline=(70, 74, 86, 255), width=8)


def d1():                                                                   # arrival: LED destination board + the poster
    c = station_bg(); board(c, (50, 80, 1030, 520)); led(c, "IPL 2027 · MUMBAI INDIANS", (540, 160), 54); led(c, "मुंबईचा राजा", (540, 340), 190, deva_font=True)
    T.txt(c, "NOW ARRIVING", (540, 470), BEB(46), (255, 255, 255, 220), "mm", 12)
    sign(c, (60, 570, 360, 680), "PLATFORM", "रोहित शर्मा", RAIL_Y, BLK, 52)
    t = THRONE.crop((0, 34, 495, 619)); t = t.resize((780, int(780 * t.height / t.width)), Image.LANCZOS); d = ImageDraw.Draw(c, "RGBA")
    d.rounded_rectangle((150, 730, 930, 730 + t.height + 120), 20, fill=(240, 240, 240, 255)); c.paste(t, (150, 740)); sign(c, (150, 740 + t.height + 6, 930, 740 + t.height + 116), "WELCOME BACK", None, RAIL_Y, BLK, 70)
    c.save(O + "L1_arrival.png")


def d2():                                                                   # the line: 19 seasons as stations
    c = station_bg(); pill(c, "THE LINE · EVERY SEASON, 2008 TO 2026", (40, 60), 32); d = ImageDraw.Draw(c, "RGBA"); x_line, y0, step = 190, 190, 72
    for i, y in enumerate(YRS):
        yy = y0 + i * step
        if i: d.rectangle((x_line - 9, yy - step, x_line + 9, yy), fill=(DCY if y <= 2010 else MIB) + (255,))
        title = MI[y]["title"] or y == 2009; r = 30 if title else 17; col = DCY if y <= 2010 else MIB
        d.ellipse((x_line - r, yy - r, x_line + r, yy + r), fill=(255, 255, 255, 255), outline=col + (255,), width=8 if title else 6)
        if title: crown(c, x_line - 70, yy, 44, jewels=False)
        T.txt(c, str(y), (270, yy), BEB(44), GOLD if title else WHITE, "lm", 3); ImageDraw.Draw(c).text((400, yy), dn(y), font=dfont(30), fill=(150, 160, 185), anchor="lm")
        T.txt(c, "DECCAN" if y <= 2010 else "MUMBAI", (520, yy), INT(22), (210, 220, 240), "lm", 2); T.txt(c, str(S[y]["runs"]), (735, yy), BEB(36), WHITE, "rm", 2)
        w = 260 * S[y]["runs"] / 540; d.rounded_rectangle((760, yy - 11, 760 + w, yy + 11), 6, fill=col + (255,))
    ycap = y0 + 5 * step; d.line([(40, ycap), (150, ycap)], fill=GOLD + (255,), width=4); T.txt(c, "C", (70, ycap - 34), BEB(46), GOLD, "mm"); T.txt(c, "CAPTAIN FROM 2013", (500, y0 + 19 * step + 20), BEB(40), GOLD, "mm", 6)
    T.txt(c, "CROWN = IPL TITLE · NUMBER AND BAR = RUNS IN THE SEASON", (540, y0 + 19 * step + 84), INT(22), MUTED, "mm", 3); strip(c, 1730, "OUR DATA: EVERY IPL SEASON, 2008-2026"); c.save(O + "L2_the_line.png")


def d3():                                                                   # the platform board for 2013: captain's first season
    c = station_bg(); sign(c, (60, 80, 460, 190), "PLATFORM", dn(2013) + "  ·  2013", RAIL_Y, BLK, 56); board(c, (60, 230, 1020, 770)); led(c, "2013 · CAPTAIN ROHIT", (540, 310), 60); led(c, "538", (540, 520), 300); led(c, "RUNS · MI 13-6 · TITLE", (540, 700), 56)
    B.slot(c, (60, 820, 1020, 1380), "IMAGE: 2013 TROPHY LIFT / HANDOVER\n(Ponting to Rohit)", False); T.txt(c, "THE FIRST OF FIVE", (540, 1470), BEB(80), GOLD, "mm", 10); strip(c, 1580); c.save(O + "L3_platform_2013.png")


def ticket(c, x, y, w, h, yr, rec):
    d = ImageDraw.Draw(c, "RGBA"); d.rounded_rectangle((x, y, x + w, y + h), 22, fill=(248, 240, 214, 255), outline=(60, 40, 10, 255), width=5)
    for k in range(0, h, 26): d.ellipse((x + w * .30 - 8, y + k, x + w * .30 + 8, y + k + 16), fill=(30, 33, 40, 255))              # perforation
    d.rounded_rectangle((x + 18, y + 18, x + w * .30 - 22, y + h - 18), 14, fill=(30, 33, 42, 255)); B.slot(c, (x + 18, y + 18, x + w * .30 - 22, y + h - 18), f"IMAGE\n{yr}", False)
    X = x + w * .30 + 40; ink = (60, 30, 10); T.txt(c, "FIRST CLASS · MUMBAI → TROPHY", (X, y + 40), INT(22), ink, "lm", 3); T.txt(c, str(yr), (X, y + 110), BEB(110), (130, 20, 40), "lm", 3); ImageDraw.Draw(c).text((X + 290, y + 112), dn(yr), font=dfont(48), fill=ink, anchor="lm")
    T.txt(c, f"MI {rec}  ·  FINAL WON", (X, y + 190), BEB(46), ink, "lm", 4)


def d4():                                                                   # five tickets
    c = station_bg(); pill(c, "FIVE TICKETS · FIVE FINALS · FIVE TITLES", (40, 60), 32)
    for i, yr in enumerate((2013, 2015, 2017, 2019, 2020)):
        ticket(c, 60, 180 + i * 262, 960, 240, yr, f'{MI[yr]["W"]}-{MI[yr]["L"]}')
    T.txt(c, "AS MI CAPTAIN · NEVER LOST A FINAL", (540, 1545), BEB(52), WHITE, "mm", 6); strip(c, 1640, "OUR DATA: EVERY IPL FINAL, 2008-2025"); c.save(O + "L4_tickets.png")


def d5():                                                                   # departures board: every MI season
    c = station_bg(); board(c, (40, 70, 1040, 1620)); T.txt(c, "DEPARTURES · MUMBAI INDIANS", (540, 130), BEB(70), AMB, "mm", 8)
    T.txt(c, "YEAR", (110, 215), BEB(40), (170, 175, 190), "lm", 5); T.txt(c, "W-L", (470, 215), BEB(40), (170, 175, 190), "lm", 5); T.txt(c, "RESULT", (650, 215), BEB(40), (170, 175, 190), "lm", 5); d = ImageDraw.Draw(c, "RGBA")
    for i, y in enumerate(range(2008, 2027)):
        yy = 275 + i * 69; res = "TITLE" if MI[y]["title"] else ("FINAL" if MI[y]["final"] else ("PLAYOFFS" if MI[y]["playoff"] else "-")); era = (110, 125, 160) if y < 2013 else (MIB if y <= 2023 else RED)
        d.rectangle((60, yy - 26, 76, yy + 26), fill=era + (255,)); col = GOLD if res == "TITLE" else (WHITE if res != "-" else (120, 125, 140))
        T.txt(c, str(y), (110, yy), BEB(50), col, "lm", 3); T.txt(c, f'{MI[y]["W"]} - {MI[y]["L"]}', (470, yy), BEB(50), col, "lm", 3); T.txt(c, res if res != "-" else "NO PLAYOFFS", (650, yy), BEB(46), col, "lm", 3)
    for lab, col, x in (("BEFORE ROHIT", (110, 125, 160), 70), ("ROHIT 2013-23", MIB, 380), ("HARDIK 2024-26", RED, 690)): d.rectangle((x, 1675, x + 24, 1699), fill=col + (255,)); T.txt(c, lab, (x + 36, 1687), INT(22), WHITE, "lm", 3)
    strip(c, 1760); c.save(O + "L5_departures.png")


def d6():                                                                   # two routes
    c = station_bg(); pill(c, "TWO ROUTES · MI 2014 TO 2026", (40, 60), 32); a, b = M["mi_under_rohit_2014_2023"], M["mi_under_hardik_2024_2026"]; d = ImageDraw.Draw(c, "RGBA")
    for k, (y0, col, lab, yrs, rec, pl, ex, face) in enumerate(((190, MIB, "ROHIT LINE", "2014 TO 2023 · 10 SEASONS", (a["W"], a["L"]), f'{a["win_pct"]:.0f}% OF MATCHES', f'PLAYOFFS {a["playoffs"]} OF 10 · 4 TITLES', True), (980, RED, "HARDIK LINE", "2024 TO 2026 · 3 SEASONS", (b["W"], b["L"]), f'{b["win_pct"]:.0f}% OF MATCHES', f'PLAYOFFS {b["playoffs"]} OF 3 · 0 TITLES', False))):
        d.rounded_rectangle((40, y0, 1040, y0 + 700), 28, fill=BLK + (255,), outline=col + (255,), width=10); d.rectangle((40, y0 + 18, 1040, y0 + 56), fill=col + (255,)); T.txt(c, lab, (80, y0 + 110), BEB(70), WHITE, "lm", 6); T.txt(c, yrs, (80, y0 + 170), INT(26), (200, 210, 230), "lm", 4)
        B.score(c, (80, y0 + 220), str(rec[0]), str(rec[1]), 230, "l", AMB); T.txt(c, pl, (84, y0 + 560), BEB(60), WHITE, "lm", 4); T.txt(c, ex, (84, y0 + 625), BEB(40), AMB, "lm", 4)
        n = 10 if k == 0 else 3
        for j in range(n): d.ellipse((560 + (j % 5) * 0, 0, 560, 0), fill=None)
        if face: face_circle(c, 830, y0 + 330, 160, (255, 255, 255))
        else: B.slot(c, (700, y0 + 120, 1000, y0 + 500), "IMAGE: HARDIK\n(MI KIT)", False)
    strip(c, 1730); c.save(O + "L6_two_routes.png")


def d7():                                                                   # the season pass
    c = station_bg(); d = ImageDraw.Draw(c, "RGBA"); d.rounded_rectangle((90, 130, 990, 1560), 50, fill=(0, 70, 170, 255), outline=(255, 255, 255, 255), width=10); d.rectangle((90, 250, 990, 330), fill=RAIL_Y + (255,)); T.txt(c, "SEASON PASS · 19 SEASONS", (540, 290), BEB(60), BLK, "mm", 8)
    t = THRONE.crop((20, 70, 475, 560)); t = t.resize((540, int(540 * t.height / t.width)), Image.LANCZOS); m = Image.new("L", t.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, t.width, t.height), 28, fill=255); c.paste(t, (270, 380), m)
    deva(c, "मुंबईचा राजा", (540, 1075), 96, GOLD); T.txt(c, "ROHIT SHARMA", (540, 1165), BEB(84), WHITE, "mm", 8)
    for i, (v, l) in enumerate((("7,046", "RUNS TO 2025"), ("303", "SIXES"), ("6", "TITLES"))): T.txt(c, v, (250 + i * 290, 1285), BEB(100), AMB, "mm", 2); T.txt(c, l, (250 + i * 290, 1350), INT(22), (225, 235, 250), "mm", 3)
    T.txt(c, "SECOND BATTER PAST 7,000 · FIRST INDIAN PAST 300 SIXES", (540, 1425), INT(21), (225, 235, 250), "mm", 2); T.txt(c, "VALID: EVERY SEASON SINCE 2008", (540, 1490), INT(22), AMB, "mm", 4); strip(c, 1640); c.save(O + "L7_season_pass.png")


def d8():                                                                   # close
    c = station_bg(); board(c, (50, 110, 1030, 560)); led(c, "मुंबईचा राजा,", (540, 280), 150, deva_font=True); led(c, "रोहित शर्मा!", (540, 450), 150, deva_font=True)
    face_circle(c, 540, 930, 260); sign(c, (240, 1260, 840, 1380), "WELCOME BACK", None, RAIL_Y, BLK, 80); T.txt(c, "IPL 2027 · MUMBAI INDIANS", (540, 1460), BEB(54), WHITE, "mm", 8); c.save(O + "L8_close.png")


if __name__ == "__main__":
    fs = (d1, d2, d3, d4, d5, d6, d7, d8)
    for f in fs: f(); print("ok", f.__name__)
    names = ["L1_arrival", "L2_the_line", "L3_platform_2013", "L4_tickets", "L5_departures", "L6_two_routes", "L7_season_pass", "L8_close"]
    sh = Image.new("RGB", (360 * 4, 640 * 2), (10, 10, 10))
    for i, n in enumerate(names): sh.paste(Image.open(O + n + ".png").convert("RGB").resize((360, 640)), ((i % 4) * 360, (i // 4) * 640))
    sh.save(O + "L_ALL_storyboard4.png"); print(sh.size)
