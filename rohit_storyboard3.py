"""Storyboard v3 (stills, NOT a render): concept 'THE CORONATION' for the silent 'Mumbai cha Raja' Rohit Sharma video. Rules from the owner (17 Nov 2026): no Bumrah frame, NO video slots (images only), every IPL season 2008-2026 in the data.
Royal look: navy and gold, crowns, towers, a decree scroll. Image slots are plain dashed boxes; the throne portrait is the owner's graphic (data/licensed/in/rohit_throne.png, outlet watermark cropped out: rights to be confirmed).
Devanagari lines use Noto Sans Devanagari Bold via Raqm (real render: pre-drawn text plates).   python3 rohit_storyboard3.py"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rohit_storyboard2 as B
from rohit_storyboard2 import *          # helpers: deva, pill, strip, face_circle, bg, S, MI, M, THRONE, YRS, MIB, DCY, RED, GOLD, WHITE, MUTED, T, W, H, O, BEB, INT
from PIL import Image, ImageDraw, ImageFilter

ROYAL = (120, 20, 40)


def royal_bg(glow_y=900):
    c = T.bg(W, H, (6, 12, 34), (2, 6, 20)); g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    for r, a in ((780, 50), (560, 70), (360, 90)): d.ellipse((W / 2 - r, glow_y - r, W / 2 + r, glow_y + r), fill=(255, 190, 50, a))
    g = g.filter(ImageFilter.GaussianBlur(80)); c.paste(g, (0, 0), g); return c


def crown(c, cx, cy, w, col=GOLD, jewels=True):
    d = ImageDraw.Draw(c, "RGBA"); h = w * .62; x0, y0 = cx - w / 2, cy - h / 2
    pts = [(x0, y0 + h), (x0, y0 + h * .35), (x0 + w * .2, y0 + h * .6), (x0 + w * .35, y0 + h * .1), (x0 + w * .5, y0 + h * .55), (x0 + w * .65, y0 + h * .1), (x0 + w * .8, y0 + h * .6), (x0 + w, y0 + h * .35), (x0 + w, y0 + h)]
    d.polygon(pts, fill=col + (255,), outline=(255, 255, 255, 120)); d.rectangle((x0, y0 + h * .82, x0 + w, y0 + h), fill=tuple(int(v * .78) for v in col) + (255,))
    for px, py in ((x0, y0 + h * .35), (x0 + w * .35, y0 + h * .1), (x0 + w * .65, y0 + h * .1), (x0 + w, y0 + h * .35)): d.ellipse((px - w * .04, py - w * .04, px + w * .04, py + w * .04), fill=(255, 255, 255, 235))
    if jewels:
        for k, jc in enumerate(((225, 60, 70), (60, 140, 255), (225, 60, 70))): d.ellipse((x0 + w * (.25 + .25 * k) - w * .04, y0 + h * .86 - w * .035, x0 + w * (.25 + .25 * k) + w * .04, y0 + h * .86 + w * .035), fill=jc + (255,))


def frame_gold(c, box, r=36, wd=8):
    d = ImageDraw.Draw(c, "RGBA"); d.rounded_rectangle(box, r, outline=GOLD + (255,), width=wd); x0, y0, x1, y1 = box
    for px, py in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)): d.ellipse((px - 14, py - 14, px + 14, py + 14), fill=GOLD + (255,))


def fan_slot(c, box, label):                                     # image slot only (no play icon)
    B.slot(c, box, label, False)


def g1():                                                         # coronation: the throne, rays, title
    c = royal_bg(1000); d = ImageDraw.Draw(c, "RGBA")
    for k in range(18): a = math.radians(k * 20); d.polygon([(W / 2, 1000), (W / 2 + 1500 * math.cos(a - .05), 1000 + 1500 * math.sin(a - .05)), (W / 2 + 1500 * math.cos(a + .05), 1000 + 1500 * math.sin(a + .05))], fill=(255, 200, 70, 22))
    t = THRONE.crop((0, 34, 495, 619)); t = t.resize((1060, int(1060 * t.height / t.width)), Image.LANCZOS); m = Image.new("L", t.size, 255)
    for y in range(0, 260): ImageDraw.Draw(m).line([(0, y), (t.width, y)], fill=int(255 * y / 260))
    c.paste(t, (10, H - t.height + 40), m)
    crown(c, W / 2, 150, 200); deva(c, "मुंबईचा राजा", (W / 2, 400), 200, GOLD, glow=True); T.txt(c, "ROHIT SHARMA", (W / 2, 580), BEB(170), WHITE, "mm", 8, True); pill(c, "IPL 2027 · MUMBAI INDIANS", (300, 690)); c.save(O + "C1_coronation.png")


def g2():                                                         # the chant on a royal banner
    c = royal_bg(800); d = ImageDraw.Draw(c, "RGBA"); d.polygon([(120, 250), (960, 250), (960, 1250), (540, 1360), (120, 1250)], fill=ROYAL + (255,), outline=GOLD + (255,)); frame_gold(c, (150, 280, 930, 1210), 20, 6)
    crown(c, W / 2, 380, 170); deva(c, "मुंबईचा राजा,", (W / 2, 640), 150, GOLD, glow=True); deva(c, "रोहित शर्मा!", (W / 2, 850), 150, WHITE)
    for i in range(3): face_circle(c, 300 + i * 240, 1080, 78 if i != 1 else 100)
    T.txt(c, "THE CHANT", (W / 2, 1480), BEB(60), GOLD, "mm", 10); fan_slot(c, (60, 1520, 1020, 1640), "IMAGE: FANS AT WANKHEDE (OPTIONAL BACKDROP)"); c.save(O + "C2_chant.png")


def g3():                                                         # the kingdom: MI wins as towers, every season
    c = royal_bg(1100); d = ImageDraw.Draw(c, "RGBA"); pill(c, "THE KINGDOM · MI WINS EVERY SEASON"); T.txt(c, "2008 TO 2026", (W / 2, 370), BEB(120), WHITE, "mm", 8)
    x0, ybase, hmax = 60, 1330, 700; bw = 960 / 19
    for i, y in enumerate(YRS):
        v = MI[y]["W"]; era = "pre" if y < 2013 else ("rohit" if y <= 2023 else "hardik"); col = {"pre": (110, 125, 160), "rohit": MIB, "hardik": RED}[era]; h = hmax * v / 14; xa = x0 + i * bw + 5; wv = bw - 10
        d.rectangle((xa, ybase - h, xa + wv, ybase), fill=col + (255,))
        for k in range(3): d.rectangle((xa + k * wv / 2.6, ybase - h - 16, xa + k * wv / 2.6 + wv / 4, ybase - h), fill=col + (255,))    # crenellations
        d.rectangle((xa + wv / 2 - 6, ybase - 70, xa + wv / 2 + 6, ybase), fill=(0, 0, 0, 90))
        T.txt(c, str(v), (xa + wv / 2, ybase - h - 40), BEB(30), WHITE, "mm", 0); T.txt(c, str(y)[2:], (xa + wv / 2, ybase + 30), BEB(30), MUTED, "mm", 1)
        if MI[y]["title"]: d.line([(xa + wv / 2, ybase - h - 16), (xa + wv / 2, ybase - h - 120)], fill=GOLD + (255,), width=4); d.polygon([(xa + wv / 2, ybase - h - 120), (xa + wv / 2 + 44, ybase - h - 100), (xa + wv / 2, ybase - h - 80)], fill=GOLD + (255,))
    for lab, col, x in (("BEFORE ROHIT", (110, 125, 160), 60), ("ROHIT 2013-23", MIB, 380), ("HARDIK 2024-26", RED, 700)): d.rectangle((x, 1420, x + 28, 1448), fill=col + (255,)); T.txt(c, lab, (x + 42, 1435), INT(26), WHITE, "lm", 3)
    T.txt(c, "GOLD FLAG = IPL TITLE", (W / 2, 1495), INT(24), GOLD, "mm", 5); strip(c, 1580); c.save(O + "C3_kingdom.png")


def g4():                                                         # crown jewels: six titles
    c = royal_bg(700); crown(c, W / 2, 330, 520); T.glowtext(c, "6", (W / 2, 720), BEB(330), GOLD, "mm", 4); T.txt(c, "IPL TITLES", (W / 2, 910), BEB(110), WHITE, "mm", 10); d = ImageDraw.Draw(c, "RGBA")
    for i, (t, y) in enumerate([("DC", 2009), ("MI", 2013), ("MI", 2015), ("MI", 2017), ("MI", 2019), ("MI", 2020)]):
        x0 = 40 + i * 168; fan_slot(c, (x0, 1000, x0 + 156, 1290), f"IMAGE\n{y}"); col = DCY if t == "DC" else MIB; d.polygon([(x0 + 78, 1300), (x0 + 156, 1340), (x0 + 78, 1400), (x0, 1340)], fill=col + (255,), outline=(255, 255, 255, 220)); T.txt(c, str(y), (x0 + 78, 1344), BEB(40), (9, 14, 30) if t == "DC" else WHITE, "mm", 2)
    T.txt(c, "JOINT-MOST: AMBATI RAYUDU ALSO HAS SIX", (W / 2, 1470), INT(26), GOLD, "mm", 4); strip(c, 1560, "OUR DATA: THE WINNING XI IN EVERY IPL FINAL, 2008-2025"); c.save(O + "C4_crown_jewels.png")


def g5():                                                         # the reign: five crowns
    c = royal_bg(900); pill(c, "THE REIGN · AS MI CAPTAIN"); T.txt(c, "5 FINALS.", (W / 2, 470), BEB(200), WHITE, "mm", 6, True); T.glowtext(c, "5 TITLES.", (W / 2, 680), BEB(200), GOLD, "mm", 6)
    for i, y in enumerate((2013, 2015, 2017, 2019, 2020)):
        cx = 120 + i * 210; crown(c, cx, 960, 170); T.txt(c, str(y), (cx, 1060), BEB(60), WHITE, "mm", 3); fan_slot(c, (cx - 92, 1110, cx + 92, 1330), f"IMAGE\n{y}")
    T.txt(c, "NEVER LOST A FINAL AS CAPTAIN", (W / 2, 1440), BEB(52), WHITE, "mm", 6); strip(c, 1540, "OUR DATA: EVERY IPL FINAL, 2008-2025"); c.save(O + "C5_reign.png")


def g6():                                                         # two eras: two scrolls
    c = royal_bg(960); d = ImageDraw.Draw(c, "RGBA"); a, b = M["mi_under_rohit_2014_2023"], M["mi_under_hardik_2024_2026"]; pill(c, "TWO ERAS · MI 2014 TO 2026")
    for k, (box, col, lab, yrs, rec, pl, extra, face) in enumerate((((60, 300, 1020, 860), MIB, "WITH ROHIT", "2014 TO 2023", (a["W"], a["L"]), f'{a["win_pct"]:.0f}% OF MATCHES', f'PLAYOFFS {a["playoffs"]} OF 10 · 4 TITLES', True),
                                                                   ((60, 940, 1020, 1500), RED, "WITH HARDIK", "2024 TO 2026", (b["W"], b["L"]), f'{b["win_pct"]:.0f}% OF MATCHES', f'PLAYOFFS {b["playoffs"]} OF 3 · 0 TITLES', False))):
        d.rounded_rectangle(box, 40, fill=col + (230,), outline=GOLD + (255,), width=6); x0, y0, x1, y1 = box
        T.txt(c, lab, (x0 + 40, y0 + 70), BEB(70), WHITE, "lm", 6); T.txt(c, yrs, (x0 + 40, y0 + 135), INT(28), (230, 238, 250), "lm", 5); B.score(c, (x0 + 40, y0 + 180), str(rec[0]), str(rec[1]), 200, "l")
        T.txt(c, pl, (x0 + 44, y1 - 90), BEB(50), GOLD, "lm", 4); T.txt(c, extra, (x0 + 44, y1 - 36), BEB(34), WHITE, "lm", 4)
        if face: face_circle(c, x1 - 190, y0 + 250, 150, (255, 255, 255))
        else: fan_slot(c, (x1 - 340, y0 + 70, x1 - 40, y0 + 400), "IMAGE: HARDIK\n(MI KIT)")
    strip(c, 1580); c.save(O + "C6_two_eras.png")


def g7():                                                         # the seal: runs ring, every season
    c = royal_bg(860); d = ImageDraw.Draw(c, "RGBA"); cx, cy, r0 = W // 2, 800, 250; pill(c, "THE ROYAL SEAL · EVERY SEASON")
    for i, y in enumerate(YRS):
        a = math.radians(-90 + i * 360 / 19); L = r0 + 360 * S[y]["runs"] / 540; col = DCY if y <= 2010 else MIB
        d.line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + L * math.cos(a), cy + L * math.sin(a))], fill=col + (255,), width=34); T.txt(c, str(y)[2:], (cx + (r0 - 38) * math.cos(a), cy + (r0 - 38) * math.sin(a)), BEB(26), MUTED, "mm", 1)
        if MI[y]["title"] or y == 2009: crown(c, cx + (L + 44) * math.cos(a), cy + (L + 44) * math.sin(a), 46, jewels=False)
    d.ellipse((cx - 190, cy - 190, cx + 190, cy + 190), fill=(6, 20, 60, 255)); face_circle(c, cx, cy, 170)
    T.txt(c, "7,046 RUNS THROUGH 2025", (W / 2, 1470), BEB(86), GOLD, "mm", 5); T.txt(c, "SECOND ONLY TO KOHLI · CROWN = TITLE · YELLOW DECCAN, BLUE MUMBAI", (W / 2, 1545), INT(22), MUTED, "mm", 3); strip(c, 1610); c.save(O + "C7_seal.png")


def g8():                                                         # the decree: records
    c = royal_bg(900); d = ImageDraw.Draw(c, "RGBA"); d.rounded_rectangle((100, 230, 980, 1500), 30, fill=(245, 232, 200, 255), outline=GOLD + (255,), width=10); d.rectangle((70, 210, 1010, 270), fill=ROYAL + (255,)); d.rectangle((70, 1460, 1010, 1520), fill=ROYAL + (255,))
    ink = (60, 30, 10); T.txt(c, "THE ROYAL RECORD", (W / 2, 380), BEB(100), ROYAL, "mm", 8); deva(c, "मुंबईचा राजा", (W / 2, 500), 90, ROYAL)
    for i, (big, l1, l2) in enumerate((("7,046", "RUNS THROUGH 2025", "SECOND BATTER PAST 7,000"), ("303", "IPL SIXES", "FIRST INDIAN PAST 300"), ("6", "IPL TITLES", "JOINT-MOST WITH RAYUDU"), ("7,329", "RUNS IN 19 SEASONS", "275 INNINGS · 2008 TO 2026"))):
        y = 700 + i * 190; T.txt(c, big, (150, y), BEB(140), ROYAL, "lm", 3); T.txt(c, l1, (540, y - 24), BEB(46), ink, "lm", 4); T.txt(c, l2, (540, y + 30), INT(24), ink, "lm", 2)
    strip(c, 1600); c.save(O + "C8_decree.png")


def g9():                                                         # close
    c = royal_bg(900); crown(c, W / 2, 200, 240); face_circle(c, 540, 700, 280); deva(c, "मुंबईचा राजा,", (W / 2, 1180), 150, GOLD, glow=True); deva(c, "रोहित शर्मा!", (W / 2, 1370), 150, WHITE); pill(c, "WELCOME BACK", (390, 1520), 38); c.save(O + "C9_close.png")


if __name__ == "__main__":
    fs = (g1, g2, g3, g4, g5, g6, g7, g8, g9)
    for f in fs: f(); print("ok", f.__name__)
    names = ["C1_coronation", "C2_chant", "C3_kingdom", "C4_crown_jewels", "C5_reign", "C6_two_eras", "C7_seal", "C8_decree", "C9_close"]
    sh = Image.new("RGB", (360 * 5, 640 * 2), (10, 10, 10))
    for i, n in enumerate(names): sh.paste(Image.open(O + n + ".png").convert("RGB").resize((360, 640)), ((i % 5) * 360, (i // 5) * 640))
    sh.save(O + "C_ALL_storyboard3.png"); print(sh.size)
