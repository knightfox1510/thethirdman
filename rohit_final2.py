"""Final-frame stills v2 (NOT a render) for the SILENT 'Mumbai cha Raja' Rohit Sharma video (Channel Ep 3; episode number on no frame, no cover, no audio). Prepared for a possible MI captaincy announcement: discard if it does not happen.
v2 changes (owner, 18 Nov 2026): hype tone ("the captain is back"); the throne image only once (cold open); Deccan Chargers photos (2009 tile + 'how it started' frame); 2020 tile = the Dream11 photo; Hardik centred; Ricky Ponting named in frame 4;
every image rotates (arms-crossed MI portrait, the cape/trophies graphic cut-out, the 2020 photo...). Images only, no footage, no Bumrah, every IPL season 2008-2026.   python3 rohit_final2.py"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trades_mockups as T
import rohit_storyboard2 as B
from rohit_storyboard2 import deva, pill, strip, score, S, MI, M, THRONE, YRS, MIB, DCY, RED, GOLD, WHITE, MUTED, W, H, O, BEB, INT
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance


def strip(*a, **k):                                   # owner (18 Nov 2026): no "OUR DATA" line on any frame: this video uses every IPL season, and sources stay off screen
    return None


IN = "data/licensed/in/"; CUT = "data/licensed/cut/"; NAVY = (9, 14, 30)
IMG = lambda n: Image.open(IN + n + ".png").convert("RGB")
TILE = {2009: "deccan_left_confetti", 2013: "title_tile_TL", 2015: "title_tile_TR", 2017: "title_tile_ML", 2019: "title_tile_MR", 2020: "rohit_2020_trophy"}     # 2013-2019 order from the ribbon sponsors: OWNER TO CONFIRM


def cover(im, w, h, ax=.5, ay=.5):
    s = max(w / im.width, h / im.height); im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS); l = int((im.width - w) * ax); t = int((im.height - h) * ay); return im.crop((l, t, l + w, t + h))


def put(c, im, box, r=18, border=None, bw=5, ax=.5, ay=.5):
    x0, y0, x1, y1 = [int(v) for v in box]; p = cover(im, x1 - x0, y1 - y0, ax, ay); m = Image.new("L", p.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, p.width, p.height), r, fill=255)
    if border: ImageDraw.Draw(c).rounded_rectangle((x0 - bw, y0 - bw, x1 + bw, y1 + bw), r + bw, fill=border)
    c.paste(p, (x0, y0), m)


def face_c(c, cx, cy, r, im, box, ring=GOLD):                      # round face medallion from a crop box of any image
    f = im.crop(box).resize((2 * r, 2 * r), Image.LANCZOS); m = Image.new("L", f.size, 0); ImageDraw.Draw(m).ellipse((0, 0, 2 * r, 2 * r), fill=255)
    ImageDraw.Draw(c).ellipse((cx - r - 8, cy - r - 8, cx + r + 8, cy + r + 8), fill=ring); c.paste(f, (cx - r, cy - r), m)


def _save(c, name):
    c.save(O + name); return c


def ease(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3


def bgc(top=(0, 70, 170), bot=(0, 22, 75)): return T.bg(W, H, top, bot)


def rays(c, cy, n=18, a=22):
    d = ImageDraw.Draw(c, "RGBA")
    for k in range(n): ang = math.radians(k * 360 / n); d.polygon([(W / 2, cy), (W / 2 + 1700 * math.cos(ang - .045), cy + 1700 * math.sin(ang - .045)), (W / 2 + 1700 * math.cos(ang + .045), cy + 1700 * math.sin(ang + .045))], fill=(255, 205, 80, a))


def yr_tag(c, x, y, w, yr, col=MIB):
    T.rr(c, (x, y, x + w, y + 54), 14, fill=col + (255,)); T.txt(c, str(yr), (x + w / 2, y + 29), BEB(40), WHITE if col == MIB else NAVY, "mm", 2)


def banner(c, text, y, size=84, fill=GOLD, col=NAVY):
    w = int(ImageDraw.Draw(c).textlength(text, font=BEB(size)) + 100 + len(text) * 5); x = (W - w) // 2; ImageDraw.Draw(c, "RGBA").rounded_rectangle((x, y, x + w, y + size + 44), 22, fill=fill + (255,)); T.txt(c, text, (W / 2, y + size / 2 + 26), BEB(size), col, "mm", 5)


def f1():
    c = bgc((0, 40, 120), (4, 10, 30)); rays(c, 1000); w = 190
    for i, yr in enumerate((2013, 2015, 2017, 2019, 2020)): x = 22 + i * (w + 14); put(c, IMG(TILE[yr]), (x, 40, x + w, 290), 12, GOLD, 3, 0.5, 0.15); yr_tag(c, x, 236, w, yr)
    deva(c, "मुंबईचा राजा", (W / 2, 470), 190, GOLD, glow=True); T.txt(c, "ROHIT SHARMA", (W / 2, 635), BEB(160), WHITE, "mm", 8, True); banner(c, "THE CAPTAIN IS BACK", 730, 76); T.txt(c, "IPL 2027 · MUMBAI INDIANS", (W / 2, 880), BEB(50), WHITE, "mm", 10)
    t = THRONE.crop((0, 34, 495, 619)); t = t.resize((1000, int(1000 * t.height / t.width)), Image.LANCZOS); m = Image.new("L", t.size, 255)
    for y in range(0, 300): ImageDraw.Draw(m).line([(0, y), (t.width, y)], fill=int(255 * min(1, y / 300)))
    c.paste(t, (40, H - t.height + 140), m); return _save(c, "G1_cold_open.png")


def f2(t=0.0):
    st = IMG("mumbai_stadium_crowd").crop((60, 125, 554, 554)); c = cover(st, W, H).filter(ImageFilter.GaussianBlur(5)); c = ImageEnhance.Brightness(c).enhance(.55)
    ImageDraw.Draw(c, "RGBA").rectangle((0, 0, W, H), fill=(0, 25, 80, 130)); deva(c, "मुंबईचा राजा,", (W / 2, 760), 170, GOLD, glow=True); deva(c, "रोहित शर्मा!", (W / 2, 970), 170, WHITE); d = ImageDraw.Draw(c, "RGBA")
    for i in range(34): h = 30 + 90 * abs(math.sin(i * .7 + t * 7)) * (0.55 + 0.45 * abs(math.sin(t * 3 + i * .2))); d.rounded_rectangle((60 + i * 28, 1240 - h, 60 + i * 28 + 16, 1240 + h), 6, fill=GOLD + (210,))
    banner(c, "THE WANKHEDE ROARS", 1420, 64); return _save(c, "G2_chant.png")


def f3(p=1.0):
    c = bgc((4, 10, 28), (0, 40, 110)); d = ImageDraw.Draw(c, "RGBA"); cx, cy, r0 = W // 2, 860, 250; pill(c, "19 SEASONS · ONE LEGEND", (60, 200))
    for i, y in enumerate(YRS):
        a = math.radians(-90 + i * 360 / 19); eg = ease(p * 1.6 - i * 0.045); L = r0 + 360 * S[y]["runs"] / 540 * eg; col = DCY if y <= 2010 else MIB
        d.line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + L * math.cos(a), cy + L * math.sin(a))], fill=col + (255,), width=34); T.txt(c, str(y)[2:], (cx + (r0 - 38) * math.cos(a), cy + (r0 - 38) * math.sin(a)), BEB(26), MUTED, "mm", 1)
        if (MI[y]["title"] or y == 2009) and eg > .97: T.txt(c, "★", (cx + (L + 30) * math.cos(a), cy + (L + 30) * math.sin(a)), INT(34), GOLD, "mm")
    d.ellipse((cx - 190, cy - 190, cx + 190, cy + 190), fill=(6, 20, 60, 255)); face_c(c, cx, cy, 170, IMG("title_tile_ML"), (60, 10, 300, 250))
    T.txt(c, "7,046 RUNS THROUGH 2025", (W / 2, 1400), BEB(86), GOLD, "mm", 5); T.txt(c, "SECOND ONLY TO KOHLI · YELLOW DECCAN, BLUE MUMBAI · ★ TITLE", (W / 2, 1480), INT(22), MUTED, "mm", 3); strip(c, 1590); return _save(c, "G3_ring.png")


def f4():                                                           # from Deccan to Mumbai
    c = bgc((20, 18, 6), (4, 10, 30)); pill(c, "HOW IT STARTED", (60, 200)); T.txt(c, "DECCAN CHARGERS · 2008 TO 2010", (W / 2, 330), BEB(60), DCY, "mm", 6)
    put(c, IMG("deccan_left_confetti"), (40, 390, 520, 900), 20, DCY, 5, 0.5, 0.3); put(c, IMG("deccan_right_trophy"), (560, 390, 1040, 900), 20, DCY, 5, 0.3, 0.3); T.txt(c, "2009: A TITLE WITH DECCAN", (W / 2, 975), BEB(50), WHITE, "mm", 5)
    ImageDraw.Draw(c).polygon([(500, 1040), (580, 1040), (540, 1100)], fill=GOLD); banner(c, "2011 · MI WIN THE BID", 1130, 70); T.txt(c, "$2 MILLION · AGAINST PUNJAB AND DECCAN", (W / 2, 1310), BEB(56), WHITE, "mm", 5)
    T.txt(c, "FROM THEN ON, HE NEVER LEFT", (W / 2, 1420), BEB(70), GOLD, "mm", 8); return _save(c, "G4_deccan_to_mumbai.png")


def f5(p=1.0):                                                           # ribbon: 2013, with Ricky Ponting
    c = bgc((6, 12, 30), (14, 24, 52)); d = ImageDraw.Draw(c, "RGBA"); pill(c, "2013 · THE CAPTAINCY BEGINS", (60, 200)); put(c, IMG("rohit_with_trophy_2013"), (60, 310, 1020, 820), 20, GOLD, 5, 0.5, 0.35)
    T.txt(c, "WITH RICKY PONTING · 2013 CHAMPIONS", (W / 2, 870), BEB(46), WHITE, "mm", 5); T.txt(c, str(int(538 * ease(p * 1.5))), (W / 2, 1060), BEB(280), GOLD, "mm", 4); T.txt(c, "RUNS IN HIS FIRST SEASON AS CAPTAIN · MI 13-6 · TITLE", (W / 2, 1230), BEB(42), WHITE, "mm", 4)
    y0 = 1300; d.rounded_rectangle((20, y0 - 20, W - 20, y0 + 270), 24, fill=(255, 255, 255, 14))
    for i, y in enumerate(YRS):
        x = 60 + i * 52; col = DCY if y <= 2010 else MIB; h = 190 * S[y]["runs"] / 540 * ease(p * 1.5 - i * 0.03); hot = y == 2013
        d.rounded_rectangle((x, y0 + 230 - h, x + 40, y0 + 230), 8, fill=col + ((255,) if hot else (110,))); T.txt(c, str(y)[2:], (x + 20, y0 + 256), BEB(26), WHITE if hot else MUTED, "mm", 1)
        if (MI[y]["title"] or y == 2009) and ease(p * 1.5 - i * 0.03) > .95: T.txt(c, "★", (x + 20, y0 + 230 - h - 26), INT(34), GOLD, "mm")
    x = 60 + 5 * 52; d.rounded_rectangle((x - 12, y0 - 10, x + 52, y0 + 275), 12, outline=GOLD + (255,), width=5); T.txt(c, "C", (x + 20, y0 + 305), BEB(56), GOLD, "mm"); strip(c, 1720); return _save(c, "G5_ribbon_2013.png")


def f6():                                                           # six trophies
    c = bgc(); rays(c, 520, 16, 16); pill(c, "SIX TIMES A CHAMPION", (60, 200)); T.glowtext(c, "6", (W / 2, 520), BEB(440), GOLD, "mm", 4); T.txt(c, "IPL TITLES", (W / 2, 760), BEB(130), WHITE, "mm", 10); d = ImageDraw.Draw(c, "RGBA")
    for i, yr in enumerate(TILE):
        col, row = i % 3, i // 3; x0 = 60 + col * 320; y0 = 880 + row * 360; put(c, IMG(TILE[yr]), (x0, y0, x0 + 300, y0 + 280), 16, GOLD, 4, 0.5, 0.15); yr_tag(c, x0 + 60, y0 + 290, 180, yr, DCY if yr == 2009 else MIB)
    T.txt(c, "JOINT-MOST: AMBATI RAYUDU ALSO HAS SIX", (W / 2, 1610), INT(26), GOLD, "mm", 4); strip(c, 1680, "OUR DATA: THE WINNING XI IN EVERY IPL FINAL, 2008-2025"); return _save(c, "G6_trophies.png")


def f7():                                                           # the reign
    c = bgc((0, 40, 120), (4, 10, 30)); pill(c, "AS MI CAPTAIN · 2013 TO 2020", (60, 200)); T.txt(c, "5 FINALS.", (W / 2, 460), BEB(210), WHITE, "mm", 6, True); T.glowtext(c, "5 TITLES.", (W / 2, 690), BEB(210), GOLD, "mm", 6)
    put(c, IMG("rohit_five_trophies"), (40, 840, 1040, 1500), 22, GOLD, 5, 0.5, 0.5); banner(c, "NEVER LOST A FINAL AS CAPTAIN", 1550, 54); strip(c, 1700, "OUR DATA: EVERY IPL FINAL, 2008-2025"); return _save(c, "G7_reign.png")


def f8(p=1.0):                                                           # face-off: Hardik centred
    c = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(c); a, b = M["mi_under_rohit_2014_2023"], M["mi_under_hardik_2024_2026"]
    for y in range(960): t = y / 960; d.line([(0, y), (W, y)], fill=(0, int(60 + 30 * (1 - t)), int(190 - 50 * t)))
    for y in range(960, H): t = (y - 960) / 960; d.line([(0, y), (W, y)], fill=(int(210 - 50 * t), int(45 - 20 * t), int(55 - 20 * t)))
    d.polygon([(0, 905), (W, 800), (W, 1010), (0, 1115)], fill=NAVY); pill(c, "THE RECORD BEHIND THE RETURN", (36, 200), 32)
    face_c(c, 800, 560, 230, IMG("rohit_arms_crossed_mi"), (120, 20, 470, 370), (255, 255, 255)); put(c, IMG("hardik_mi_hand_on_head"), (40, 1130, 480, 1590), 22, (255, 255, 255), 5, 0.36, 0.5)
    T.txt(c, "2014 TO 2023", (40, 300), BEB(60), (200, 225, 255), "lt", 6); score(c, (40, 370), str(int(a["W"] * ease(p * 1.6))), str(int(a["L"] * ease(p * 1.6))), 210, "l"); T.txt(c, f'{a["win_pct"]:.0f}% / PLAYOFFS {a["playoffs"]} OF 10', (44, 600), BEB(54), GOLD, "lt", 4)
    T.txt(c, "2024 TO 2026", (1040, 1130), BEB(60), (255, 215, 215), "rt", 6); score(c, (1040, 1200), str(int(b["W"] * ease(p * 1.6 - .15))), str(int(b["L"] * ease(p * 1.6 - .15))), 210, "r"); T.txt(c, f'{b["win_pct"]:.0f}% / PLAYOFFS {b["playoffs"]} OF 3', (1036, 1430), BEB(54), GOLD, "rt", 4)
    strip(c, 1650); return _save(c, "G8_faceoff.png")


def card_base():
    c = bgc((30, 20, 6), (8, 12, 30)); d = ImageDraw.Draw(c, "RGBA"); x0, y0, x1, y1 = 140, 230, 940, 1500; d.rounded_rectangle((x0 - 14, y0 - 14, x1 + 14, y1 + 14), 56, fill=GOLD + (255,)); d.rounded_rectangle((x0, y0, x1, y1), 44, fill=(10, 18, 44, 255)); return c, d, x0, y0, x1, y1


def f9():
    c, d, x0, y0, x1, y1 = card_base(); put(c, IMG("rohit_arms_crossed_mi"), (x0 + 50, y0 + 60, x1 - 50, y0 + 790), 30, None, 0, 0.5, 0.2)
    deva(c, "मुंबईचा राजा", (540, y1 - 135), 100, GOLD); T.txt(c, "ROHIT SHARMA", (540, y1 - 50), BEB(70), WHITE, "mm", 6)
    for i, (v, l) in enumerate((("7,046", "RUNS"), ("303", "SIXES"), ("6", "TITLES"))): T.txt(c, v, (x0 + 160 + i * 240, y1 - 250), BEB(70), GOLD, "mm", 2); T.txt(c, l, (x0 + 160 + i * 240, y1 - 205), INT(20), MUTED, "mm", 4)
    strip(c, 1580); return _save(c, "G9_card_front.png")


def f10():
    c, d, x0, y0, x1, y1 = card_base(); T.txt(c, "RUNS IN EVERY SEASON", (540, y0 + 70), BEB(56), GOLD, "mm", 6)
    for i, y in enumerate(YRS):
        r, k = i % 4, i // 4; xx = x0 + 60 + r * 175; yy = y0 + 140 + k * 200; col = DCY if y <= 2010 else MIB; d.rounded_rectangle((xx, yy, xx + 150, yy + 180), 14, fill=col + (255,), outline=(255, 255, 255, 120), width=2)
        T.txt(c, str(y), (xx + 75, yy + 34), BEB(40), WHITE if col == MIB else NAVY, "mm", 2); T.txt(c, str(S[y]["runs"]), (xx + 75, yy + 100), BEB(64), WHITE if col == MIB else NAVY, "mm", 1)
        if MI[y]["title"] or y == 2009: T.txt(c, "★", (xx + 75, yy + 152), INT(28), GOLD if col == MIB else NAVY, "mm")
    T.txt(c, "DECCAN CHARGERS 2008-10 · MUMBAI INDIANS 2011-26", (540, y1 - 55), INT(20), MUTED, "mm", 3); strip(c, 1580); return _save(c, "G10_card_back.png")


def f11():
    c = bgc(); pill(c, "THE HITMAN IN THE RECORD BOOKS", (60, 200), 34)
    rows = [("6", "IPL TITLES", "JOINT-MOST · RAYUDU ALSO SIX"), ("7,046", "IPL RUNS TO 2025", "SECOND BATTER PAST 7,000"), ("303", "IPL SIXES TO 2025", "FIRST INDIAN PAST 300"), ("38Y 182D", "OLDEST NO. 1 ODI BATTER", "OCT 2025 · LATER OVERTAKEN")]
    for i, (big, lab, sub) in enumerate(rows):
        y = 330 + i * 320; T.rr(c, (50, y, 1030, y + 290), 30, fill=(255, 255, 255, 30), outline=GOLD + (255,), width=5); T.glowtext(c, big, (330, y + 135), BEB(150 if len(big) < 6 else 84), GOLD, "mm", 4); T.txt(c, lab, (560, y + 105), BEB(44), WHITE, "lm", 3); T.txt(c, sub, (560, y + 175), INT(20), (215, 225, 245), "lm", 2)
    strip(c, 1670, "OUR DATA: IPL 2008-2025 · ICC RANKING, OCT 2025"); return _save(c, "G11_records.png")


def f12():                                                          # close: the cape graphic cut-out
    c = bgc((0, 30, 100), (2, 8, 24)); rays(c, 800, 20, 28); p = Image.open(CUT + "rohit_cape_trophies.png").convert("RGBA"); p = p.crop((0, 0, p.width, int(p.height * .875))); k = 1150 / p.height; p = p.resize((int(p.width * k), 1150), Image.LANCZOS)
    g = Image.new("RGBA", c.size, (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((W / 2 - 420, 420, W / 2 + 420, 1300), fill=(255, 200, 70, 120)); g = g.filter(ImageFilter.GaussianBlur(70)); c.paste(g, (0, 0), g); c.paste(p, ((W - p.width) // 2, 170), p)
    banner(c, "WELCOME BACK, CAPTAIN", 1370, 70); deva(c, "मुंबईचा राजा,", (W / 2, 1620), 110, GOLD, glow=True); deva(c, "रोहित शर्मा!", (W / 2, 1750), 110, WHITE); return _save(c, "G12_close.png")


if __name__ == "__main__":
    fs = (f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12)
    for f in fs: f(); print("ok", f.__name__)
    names = ["G1_cold_open", "G2_chant", "G3_ring", "G4_deccan_to_mumbai", "G5_ribbon_2013", "G6_trophies", "G7_reign", "G8_faceoff", "G9_card_front", "G10_card_back", "G11_records", "G12_close"]
    sh = Image.new("RGB", (360 * 6, 640 * 2), (10, 10, 10))
    for i, n in enumerate(names): sh.paste(Image.open(O + n + ".png").convert("RGB").resize((360, 640)), ((i % 6) * 360, (i // 6) * 640))
    sh.save(O + "G_ALL.png"); print(sh.size)
