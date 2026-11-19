"""Final-frame stills (NOT a render) for the SILENT 'Mumbai cha Raja' Rohit Sharma video (prepared for a possible MI captaincy announcement; discard if it does not happen).
Concept = the ring + ribbon + face-off + card mix, with the owner's licensed images (data/licensed/in), no footage, no Bumrah, all IPL seasons 2008-2026. Silent: no voice, no music; the voice-over and music come later from ElevenLabs only if announced.
No episode number on any frame or the cover. Outlet marks are cropped out where the crop is natural (owner to confirm rights).   python3 rohit_final.py"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trades_mockups as T
import rohit_storyboard2 as B
from rohit_storyboard2 import deva, pill, strip, face_circle, score, S, MI, M, THRONE, YRS, MIB, DCY, RED, GOLD, WHITE, MUTED, W, H, O, BEB, INT
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
IN = "data/licensed/in/"; NAVY = (9, 14, 30)
IMG = lambda n: Image.open(IN + n + ".png").convert("RGB")
TILE = {2013: "title_tile_TL", 2015: "title_tile_TR", 2017: "title_tile_ML", 2019: "title_tile_MR", 2020: "title_tile_B"}      # sponsor ribbons suggest this order; OWNER TO CONFIRM


def cover(im, w, h, anchor=0.5):
    s = max(w / im.width, h / im.height); im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS); l = (im.width - w) // 2; t = int((im.height - h) * anchor); return im.crop((l, t, l + w, t + h))


def put(c, im, box, r=18, border=None, bw=5, anchor=0.5):
    x0, y0, x1, y1 = [int(v) for v in box]; p = cover(im, x1 - x0, y1 - y0, anchor); m = Image.new("L", p.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, p.width, p.height), r, fill=255)
    if border: ImageDraw.Draw(c).rounded_rectangle((x0 - bw, y0 - bw, x1 + bw, y1 + bw), r + bw, fill=border)
    c.paste(p, (x0, y0), m)


def bgc(top=(0, 70, 170), bot=(0, 22, 75)): return T.bg(W, H, top, bot)


def yr_tag(c, x, y, w, yr, col=MIB):
    T.rr(c, (x, y, x + w, y + 54), 14, fill=col + (255,)); T.txt(c, str(yr), (x + w / 2, y + 29), BEB(40), WHITE if col == MIB else NAVY, "mm", 2)


def f1():                                                           # cold open
    c = bgc((0, 40, 120), (4, 10, 30)); w = 190
    for i, yr in enumerate(TILE): x = 22 + i * (w + 14); put(c, IMG(TILE[yr]), (x, 40, x + w, 290), 12, GOLD, 3, 0.15); yr_tag(c, x, 236, w, yr)
    deva(c, "मुंबईचा राजा", (W / 2, 470), 190, GOLD, glow=True); T.txt(c, "ROHIT SHARMA", (W / 2, 640), BEB(160), WHITE, "mm", 8, True)
    t = THRONE.crop((0, 34, 495, 619)); t = t.resize((1080, int(1080 * t.height / t.width)), Image.LANCZOS); m = Image.new("L", t.size, 255)
    for y in range(0, 300): ImageDraw.Draw(m).line([(0, y), (t.width, y)], fill=int(255 * min(1, y / 300)))
    c.paste(t, (0, H - t.height + 90), m); pill(c, "IPL 2027 · MUMBAI INDIANS", (300, 730)); c.save(O + "F1_cold_open.png")


def f2():                                                           # chant over the stadium
    st = IMG("mumbai_stadium_crowd").crop((60, 125, 554, 554)); c = cover(st, W, H, 0.5).filter(ImageFilter.GaussianBlur(5)); c = ImageEnhance.Brightness(c).enhance(.55)
    ImageDraw.Draw(c, "RGBA").rectangle((0, 0, W, H), fill=(0, 25, 80, 130)); deva(c, "मुंबईचा राजा,", (W / 2, 760), 170, GOLD, glow=True); deva(c, "रोहित शर्मा!", (W / 2, 970), 170, WHITE); d = ImageDraw.Draw(c, "RGBA")
    for i in range(34): h = 30 + 90 * abs(math.sin(i * .7)); d.rounded_rectangle((60 + i * 28, 1240 - h, 60 + i * 28 + 16, 1240 + h), 6, fill=GOLD + (210,))
    T.txt(c, "THE CHANT", (W / 2, 1460), BEB(60), WHITE, "mm", 14); c.save(O + "F2_chant.png")


def f3():                                                           # ring
    c = bgc((4, 10, 28), (0, 40, 110)); d = ImageDraw.Draw(c, "RGBA"); cx, cy, r0 = W // 2, 860, 250; pill(c, "EVERY SEASON, ONE RING", (60, 200))
    for i, y in enumerate(YRS):
        a = math.radians(-90 + i * 360 / 19); L = r0 + 360 * S[y]["runs"] / 540; col = DCY if y <= 2010 else MIB
        d.line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + L * math.cos(a), cy + L * math.sin(a))], fill=col + (255,), width=34); T.txt(c, str(y)[2:], (cx + (r0 - 38) * math.cos(a), cy + (r0 - 38) * math.sin(a)), BEB(26), MUTED, "mm", 1)
        if MI[y]["title"] or y == 2009: T.txt(c, "★", (cx + (L + 30) * math.cos(a), cy + (L + 30) * math.sin(a)), INT(34), GOLD, "mm")
    d.ellipse((cx - 190, cy - 190, cx + 190, cy + 190), fill=(6, 20, 60, 255)); face_circle(c, cx, cy, 170)
    T.txt(c, "7,046 RUNS THROUGH 2025", (W / 2, 1400), BEB(86), GOLD, "mm", 5); T.txt(c, "SECOND ONLY TO KOHLI · YELLOW DECCAN, BLUE MUMBAI · ★ TITLE", (W / 2, 1480), INT(22), MUTED, "mm", 3); strip(c, 1590); c.save(O + "F3_ring.png")


def f4():                                                           # ribbon: 2013
    c = bgc((6, 12, 30), (14, 24, 52)); d = ImageDraw.Draw(c, "RGBA"); pill(c, "2013 · THE CAPTAINCY BEGINS", (60, 200)); put(c, IMG("rohit_with_trophy_2013"), (60, 310, 1020, 820), 20, GOLD, 5, 0.35)
    T.txt(c, "538", (W / 2, 1020), BEB(300), GOLD, "mm", 4); T.txt(c, "RUNS IN HIS FIRST SEASON AS CAPTAIN · MI 13-6 · TITLE", (W / 2, 1200), BEB(44), WHITE, "mm", 4)
    y0 = 1280; d.rounded_rectangle((20, y0 - 20, W - 20, y0 + 270), 24, fill=(255, 255, 255, 14))
    for i, y in enumerate(YRS):
        x = 60 + i * 52; col = DCY if y <= 2010 else MIB; h = 190 * S[y]["runs"] / 540; hot = y == 2013
        d.rounded_rectangle((x, y0 + 230 - h, x + 40, y0 + 230), 8, fill=col + ((255,) if hot else (110,))); T.txt(c, str(y)[2:], (x + 20, y0 + 256), BEB(26), WHITE if hot else MUTED, "mm", 1)
        if MI[y]["title"] or y == 2009: T.txt(c, "★", (x + 20, y0 + 230 - h - 26), INT(34), GOLD, "mm")
    x = 60 + 5 * 52; d.rounded_rectangle((x - 12, y0 - 10, x + 52, y0 + 275), 12, outline=GOLD + (255,), width=5); T.txt(c, "C", (x + 20, y0 + 305), BEB(56), GOLD, "mm"); strip(c, 1700); c.save(O + "F4_ribbon_2013.png")


def f5():                                                           # trophy case: six titles
    c = bgc(); pill(c, "THE TROPHY CASE", (60, 200)); T.glowtext(c, "6", (W / 2, 520), BEB(440), GOLD, "mm", 4); T.txt(c, "IPL TITLES", (W / 2, 760), BEB(130), WHITE, "mm", 10); d = ImageDraw.Draw(c, "RGBA")
    items = [(2009, None)] + [(y, TILE[y]) for y in TILE]
    for i, (yr, tn) in enumerate(items):
        col, row = i % 3, i // 3; x0 = 60 + col * 320; y0 = 880 + row * 360
        if tn: put(c, IMG(tn), (x0, y0, x0 + 300, y0 + 280), 16, GOLD, 4, 0.2)
        else: d.rounded_rectangle((x0, y0, x0 + 300, y0 + 280), 16, fill=DCY + (255,), outline=GOLD + (255,), width=4); T.txt(c, "DECCAN", (x0 + 150, y0 + 110), BEB(60), NAVY, "mm", 5); T.txt(c, "CHARGERS", (x0 + 150, y0 + 175), BEB(60), NAVY, "mm", 5)
        yr_tag(c, x0 + 60, y0 + 290, 180, yr, DCY if yr == 2009 else MIB)
    T.txt(c, "JOINT-MOST: AMBATI RAYUDU ALSO HAS SIX", (W / 2, 1610), INT(26), GOLD, "mm", 4); strip(c, 1680, "OUR DATA: THE WINNING XI IN EVERY IPL FINAL, 2008-2025"); c.save(O + "F5_trophies.png")


def f6():                                                           # the reign: five trophies
    c = bgc((0, 40, 120), (4, 10, 30)); pill(c, "AS MI CAPTAIN · 2013 TO 2020", (60, 200)); T.txt(c, "5 FINALS.", (W / 2, 460), BEB(210), WHITE, "mm", 6, True); T.glowtext(c, "5 TITLES.", (W / 2, 690), BEB(210), GOLD, "mm", 6)
    put(c, IMG("rohit_five_trophies"), (40, 840, 1040, 1500), 22, GOLD, 5, 0.5); T.txt(c, "NEVER LOST A FINAL AS CAPTAIN", (W / 2, 1590), BEB(56), WHITE, "mm", 6); strip(c, 1670, "OUR DATA: EVERY IPL FINAL, 2008-2025"); c.save(O + "F6_reign.png")


def f7():                                                           # face-off
    c = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(c); a, b = M["mi_under_rohit_2014_2023"], M["mi_under_hardik_2024_2026"]
    for y in range(960): t = y / 960; d.line([(0, y), (W, y)], fill=(0, int(60 + 30 * (1 - t)), int(190 - 50 * t)))
    for y in range(960, H): t = (y - 960) / 960; d.line([(0, y), (W, y)], fill=(int(210 - 50 * t), int(45 - 20 * t), int(55 - 20 * t)))
    d.polygon([(0, 905), (W, 800), (W, 1010), (0, 1115)], fill=NAVY); pill(c, "WITH ROHIT  vs  WITHOUT", (36, 200), 34); face_circle(c, 800, 560, 230, (255, 255, 255)); put(c, IMG("hardik_mi_hand_on_head"), (40, 1130, 480, 1590), 22, (255, 255, 255), 5, 0.5)
    T.txt(c, "2014 TO 2023", (40, 300), BEB(60), (200, 225, 255), "lt", 6); score(c, (40, 370), str(a["W"]), str(a["L"]), 210, "l"); T.txt(c, f'{a["win_pct"]:.0f}% / PLAYOFFS {a["playoffs"]} OF 10', (44, 600), BEB(54), GOLD, "lt", 4)
    T.txt(c, "2024 TO 2026", (1040, 1130), BEB(60), (255, 215, 215), "rt", 6); score(c, (1040, 1200), str(b["W"]), str(b["L"]), 210, "r"); T.txt(c, f'{b["win_pct"]:.0f}% / PLAYOFFS {b["playoffs"]} OF 3', (1036, 1430), BEB(54), GOLD, "rt", 4)
    strip(c, 1650); c.save(O + "F7_faceoff.png")


def card_base():
    c = bgc((30, 20, 6), (8, 12, 30)); d = ImageDraw.Draw(c, "RGBA"); x0, y0, x1, y1 = 140, 230, 940, 1500; d.rounded_rectangle((x0 - 14, y0 - 14, x1 + 14, y1 + 14), 56, fill=GOLD + (255,)); d.rounded_rectangle((x0, y0, x1, y1), 44, fill=(10, 18, 44, 255)); return c, d, x0, y0, x1, y1


def f8():
    c, d, x0, y0, x1, y1 = card_base(); t = THRONE.resize((700, int(700 * THRONE.height / THRONE.width)), Image.LANCZOS).crop((0, 70, 700, 790)); m = Image.new("L", t.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, t.width, t.height), 30, fill=255); c.paste(t, (190, y0 + 60), m)
    deva(c, "मुंबईचा राजा", (540, y1 - 135), 100, GOLD); T.txt(c, "ROHIT SHARMA", (540, y1 - 50), BEB(70), WHITE, "mm", 6)
    for i, (v, l) in enumerate((("7,046", "RUNS"), ("303", "SIXES"), ("6", "TITLES"))): T.txt(c, v, (x0 + 160 + i * 240, y1 - 250), BEB(70), GOLD, "mm", 2); T.txt(c, l, (x0 + 160 + i * 240, y1 - 205), INT(20), MUTED, "mm", 4)
    strip(c, 1580); c.save(O + "F8_card_front.png")


def f9():
    c, d, x0, y0, x1, y1 = card_base(); T.txt(c, "RUNS IN EVERY SEASON", (540, y0 + 70), BEB(56), GOLD, "mm", 6)
    for i, y in enumerate(YRS):
        r, k = i % 4, i // 4; xx = x0 + 60 + r * 175; yy = y0 + 140 + k * 200; col = DCY if y <= 2010 else MIB; d.rounded_rectangle((xx, yy, xx + 150, yy + 180), 14, fill=col + (255,), outline=(255, 255, 255, 120), width=2)
        T.txt(c, str(y), (xx + 75, yy + 34), BEB(40), WHITE if col == MIB else NAVY, "mm", 2); T.txt(c, str(S[y]["runs"]), (xx + 75, yy + 100), BEB(64), WHITE if col == MIB else NAVY, "mm", 1)
        if MI[y]["title"] or y == 2009: T.txt(c, "★", (xx + 75, yy + 152), INT(28), GOLD if col == MIB else NAVY, "mm")
    T.txt(c, "DECCAN CHARGERS 2008-10 · MUMBAI INDIANS 2011-26", (540, y1 - 55), INT(20), MUTED, "mm", 3); strip(c, 1580); c.save(O + "F9_card_back.png")


def f10():                                                          # verified records
    c = bgc(); pill(c, "THE HITMAN IN THE RECORD BOOKS", (60, 200), 34)
    rows = [("6", "IPL TITLES", "JOINT-MOST · RAYUDU ALSO SIX"), ("7,046", "IPL RUNS TO 2025", "SECOND BATTER PAST 7,000"), ("303", "IPL SIXES TO 2025", "FIRST INDIAN PAST 300"), ("38Y 182D", "OLDEST NO. 1 ODI BATTER", "OCT 2025 · LATER OVERTAKEN")]
    for i, (big, lab, sub) in enumerate(rows):
        y = 330 + i * 320; T.rr(c, (50, y, 1030, y + 290), 30, fill=(255, 255, 255, 30), outline=GOLD + (255,), width=5); T.glowtext(c, big, (330, y + 135), BEB(150 if len(big) < 6 else 84), GOLD, "mm", 4); T.txt(c, lab, (560, y + 105), BEB(44), WHITE, "lm", 3); T.txt(c, sub, (560, y + 175), INT(20), (215, 225, 245), "lm", 2)
    strip(c, 1670, "OUR DATA: IPL 2008-2025 · ICC RANKING, OCT 2025"); c.save(O + "F10_records.png")


def f11():                                                          # close
    c = bgc((0, 20, 60), (0, 8, 24)); st = IMG("mumbai_stadium_crowd").crop((60, 125, 554, 554)); bg = ImageEnhance.Brightness(cover(st, W, 1000, 0.3).filter(ImageFilter.GaussianBlur(3))).enhance(.6); c.paste(bg, (0, 0)); ImageDraw.Draw(c, "RGBA").rectangle((0, 0, W, 1000), fill=(0, 20, 70, 100))
    face_circle(c, 540, 960, 200); deva(c, "मुंबईचा राजा,", (W / 2, 1290), 130, GOLD, glow=True); deva(c, "रोहित शर्मा!", (W / 2, 1440), 130, WHITE); pill(c, "WELCOME BACK", (390, 1560), 38); c.save(O + "F11_close.png")


if __name__ == "__main__":
    fs = (f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11)
    for f in fs: f(); print("ok", f.__name__)
    names = ["F1_cold_open", "F2_chant", "F3_ring", "F4_ribbon_2013", "F5_trophies", "F6_reign", "F7_faceoff", "F8_card_front", "F9_card_back", "F10_records", "F11_close"]
    sh = Image.new("RGB", (360 * 6, 640 * 2), (10, 10, 10))
    for i, n in enumerate(names): sh.paste(Image.open(O + n + ".png").convert("RGB").resize((360, 640)), ((i % 6) * 360, (i // 6) * 640))
    sh.save(O + "F_ALL.png"); print(sh.size)
