"""Storyboard v2 (stills, NOT a render) for the silent 'Mumbai cha Raja' Rohit Sharma video: the ring + ribbon + face-off + card mix, with MEDIA SLOTS (dashed boxes with a play icon = footage, plain dashed = image) in nearly every frame,
because the reels that go viral are image- and footage-heavy. Devanagari lines are drawn with Noto Sans Devanagari Bold through Pillow's Raqm shaping (the engine's own text drawer does not shape Devanagari, so the real render
will use pre-drawn text plates). Rohit's photo here is the owner-supplied throne graphic (data/licensed/in/rohit_throne.png).   python3 rohit_storyboard2.py"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trades_mockups as T
from PIL import Image, ImageDraw, ImageFont, ImageFilter
O = T.O; W, H = 1080, 1920; BEB, INT = T.BEB, T.INT; GOLD, WHITE, MUTED = T.GOLD, T.WHITE, (170, 185, 215)
MIB, DCY, RED = (0, 85, 200), (240, 190, 40), (225, 60, 70); YRS = list(range(2008, 2027))
A = json.load(open("data/provenance/rohit_all_seasons.json")); M = json.load(open("data/provenance/rohit_mi_figures.json"))
S = {int(k): v for k, v in A["seasons"].items()}; MI = {int(k): v for k, v in M["mi_by_season"].items()}
BUM = {2013: (2, 19), 2014: (11, 15), 2015: (4, 16), 2016: (14, 14), 2017: (16, 17), 2018: (14, 14), 2019: (16, 16), 2020: (15, 16), 2021: (14, 14), 2022: (14, 14), 2023: (0, 16), 2024: (13, 14), 2025: (12, 16), 2026: (13, 14)}   # Sportmonks: matches bowled / MI matches
DEVA = "fonts/NotoSansDevanagari-Bold.ttf"
THRONE = Image.open("/tmp/claude-0/-home-user-thethirdman/0e6d8023-8d7b-5fe3-9abc-6751d93064e2/images/21.png").convert("RGB")
os.makedirs("data/licensed/in", exist_ok=True); THRONE.save("data/licensed/in/rohit_throne.png")                                 # kept for the build (Drive backup via datasync); watermark question open
FACE = THRONE.crop((150, 120, 350, 330))


def deva(c, s, xy, size, fill, anchor="mm", glow=False):
    f = ImageFont.truetype(DEVA, size, layout_engine=ImageFont.Layout.RAQM)
    if glow:
        g = Image.new("RGBA", c.size, (0, 0, 0, 0)); ImageDraw.Draw(g).text(xy, s, font=f, fill=fill + (255,), anchor=anchor); g = g.filter(ImageFilter.GaussianBlur(16)); c.paste(g, (0, 0), g)
    ImageDraw.Draw(c).text((xy[0] + 4, xy[1] + 5), s, font=f, fill=(0, 0, 0), anchor=anchor); ImageDraw.Draw(c).text(xy, s, font=f, fill=fill, anchor=anchor)


def slot(c, box, label, video=False):
    d = ImageDraw.Draw(c, "RGBA"); x0, y0, x1, y1 = box; d.rounded_rectangle(box, 18, fill=(255, 255, 255, 22))
    for k in range(int(x0), int(x1), 36): d.line([(k, y0), (min(k + 18, x1), y0)], fill=(255, 255, 255, 170), width=3); d.line([(k, y1), (min(k + 18, x1), y1)], fill=(255, 255, 255, 170), width=3)
    for k in range(int(y0), int(y1), 36): d.line([(x0, k), (x0, min(k + 18, y1))], fill=(255, 255, 255, 170), width=3); d.line([(x1, k), (x1, min(k + 18, y1))], fill=(255, 255, 255, 170), width=3)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if video: d.polygon([(cx - 22, cy - 40), (cx - 22, cy + 10), (cx + 24, cy - 15)], fill=(255, 255, 255, 220))
    for i, ln in enumerate(label.split("\n")): T.txt(c, ln, (cx, cy + (34 if video else -8) + i * 30), INT(22), (255, 255, 255, 235), "mm", 3)


def score(c, xy, a, b, size, align="l", col=WHITE):
    """'82 - 66' drawn as digits plus a bar, because Bebas draws its dash too high."""
    f = BEB(size); d = ImageDraw.Draw(c); bb = f.getbbox("8", anchor="lt"); bar_w = int(size * .26); gap = int(size * .12)
    wa, wb = d.textlength(a, font=f), d.textlength(b, font=f); tot = wa + gap + bar_w + gap + wb; x = xy[0] if align == "l" else xy[0] - tot; y = xy[1]
    for dx, dy, cc in ((4, 5, (0, 0, 0)), (0, 0, col)):
        d.text((x + dx, y + dy), a, font=f, fill=cc, anchor="lt"); d.rectangle((x + wa + gap + dx, y + (bb[1] + bb[3]) / 2 - size * .04 + dy, x + wa + gap + bar_w + dx, y + (bb[1] + bb[3]) / 2 + size * .04 + dy), fill=cc); d.text((x + wa + 2 * gap + bar_w + dx, y + dy), b, font=f, fill=cc, anchor="lt")


def pill(c, text, xy=(60, 200), size=36):
    w = int(ImageDraw.Draw(c).textlength(text, font=BEB(size)) + 70 + len(text) * 3); T.rr(c, (xy[0], xy[1], xy[0] + w, xy[1] + 62), 31, fill=GOLD + (255,)); T.txt(c, text, (xy[0] + w / 2, xy[1] + 33), BEB(size), (9, 14, 30), "mm", 3)


def strip(c, y=1560, t="OUR DATA: EVERY IPL SEASON, 2008-2026"): T.txt(c, t, (W / 2, y), INT(24), (210, 220, 240), "mm", 5)


def face_circle(c, cx, cy, r, ring=GOLD):
    f = FACE.resize((2 * r, 2 * r), Image.LANCZOS); m = Image.new("L", f.size, 0); ImageDraw.Draw(m).ellipse((0, 0, 2 * r, 2 * r), fill=255)
    ImageDraw.Draw(c).ellipse((cx - r - 8, cy - r - 8, cx + r + 8, cy + r + 8), fill=ring); c.paste(f, (cx - r, cy - r), m)


def bg(top=(0, 70, 170), bot=(0, 22, 75)): return T.bg(W, H, top, bot)


def f1():                                                       # cold open: title + throne + footage montage
    c = bg((0, 40, 120), (4, 10, 30))
    for i in range(4): slot(c, (40 + i * 255, 40, 270 + i * 255, 250), f"FOOTAGE\nTITLE LIFT {('2013', '2015', '2017', '2019')[i]}", True)
    deva(c, "मुंबईचा राजा", (W / 2, 420), 190, GOLD, glow=True); T.txt(c, "ROHIT SHARMA", (W / 2, 590), BEB(160), WHITE, "mm", 8, True)
    t = THRONE.crop((0, 34, 495, 619)); t = t.resize((1080, int(1080 * t.height / t.width)), Image.LANCZOS); m = Image.new("L", t.size, 255)
    for y in range(0, 300): ImageDraw.Draw(m).line([(0, y), (t.width, y)], fill=int(255 * min(1, y / 300)))
    c.paste(t, (0, H - t.height + 60), m); pill(c, "IPL 2027 · MUMBAI INDIANS", (60, 690)); c.save(O + "S1_cold_open.png")


def f2():                                                       # the chant
    c = bg((0, 20, 60), (0, 8, 24)); slot(c, (0, 0, W, H), "", False); T.txt(c, "FOOTAGE: WANKHEDE CROWD CHANT (FULL-BLEED, DARKENED)", (W / 2, 120), INT(24), (255, 255, 255, 220), "mm", 3); ImageDraw.Draw(c, "RGBA").rectangle((0, 0, W, H), fill=(0, 20, 70, 150))
    deva(c, "मुंबईचा राजा,", (W / 2, 780), 170, GOLD, glow=True); deva(c, "रोहित शर्मा!", (W / 2, 990), 170, WHITE)
    d = ImageDraw.Draw(c, "RGBA")
    for i in range(34): h = 30 + 90 * abs(math.sin(i * .7)) ; d.rounded_rectangle((60 + i * 28, 1260 - h, 60 + i * 28 + 16, 1260 + h), 6, fill=GOLD + (200,))
    T.txt(c, "THE CHANT, SUBTITLED BAR BY BAR", (W / 2, 1480), INT(26), (225, 235, 250), "mm", 5); c.save(O + "S2_chant.png")


def f3():                                                       # ring: runs, every season
    c = bg((4, 10, 28), (0, 40, 110)); d = ImageDraw.Draw(c, "RGBA"); cx, cy, r0, rmax = W // 2, 860, 250, 400; pill(c, "EVERY SEASON, ONE RING")
    for i, y in enumerate(YRS):
        a = math.radians(-90 + i * 360 / 19); L = r0 + 360 * S[y]["runs"] / 540; col = DCY if y <= 2010 else MIB
        d.line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + L * math.cos(a), cy + L * math.sin(a))], fill=col + (255,), width=34); T.txt(c, str(y)[2:], (cx + (r0 - 38) * math.cos(a), cy + (r0 - 38) * math.sin(a)), BEB(26), MUTED, "mm", 1)
        if MI[y]["title"] or y == 2009: T.txt(c, "★", (cx + (L + 30) * math.cos(a), cy + (L + 30) * math.sin(a)), INT(34), GOLD, "mm")
    d.ellipse((cx - 190, cy - 190, cx + 190, cy + 190), fill=(6, 20, 60, 255)); face_circle(c, cx, cy, 170)
    T.txt(c, "7,046 RUNS THROUGH 2025", (W / 2, 1400), BEB(86), GOLD, "mm", 5); T.txt(c, "SECOND ONLY TO KOHLI · YELLOW DECCAN, BLUE MUMBAI", (W / 2, 1480), INT(24), MUTED, "mm", 4)
    strip(c, 1590); c.save(O + "S3_ring.png")


def f4():                                                       # ribbon: 2013, the captaincy begins
    c = bg((6, 12, 30), (14, 24, 52)); d = ImageDraw.Draw(c, "RGBA"); pill(c, "2013 · THE CAPTAINCY BEGINS"); slot(c, (60, 300, 1020, 800), "FOOTAGE: 2013 FINAL / TROPHY LIFT\nor Ponting-to-Rohit handover", True)
    T.txt(c, "538", (W / 2, 1000), BEB(300), GOLD, "mm", 4); T.txt(c, "RUNS IN HIS FIRST SEASON AS CAPTAIN · MI 13-6 · TITLE", (W / 2, 1180), BEB(44), WHITE, "mm", 4)
    y0 = 1260; d.rounded_rectangle((20, y0 - 20, W - 20, y0 + 270), 24, fill=(255, 255, 255, 14))
    for i, y in enumerate(YRS):
        x = 60 + i * 52; col = DCY if y <= 2010 else MIB; h = 190 * S[y]["runs"] / 540; hot = y == 2013
        d.rounded_rectangle((x, y0 + 230 - h, x + 40, y0 + 230), 8, fill=col + ((255,) if hot else (110,))); T.txt(c, str(y)[2:], (x + 20, y0 + 256), BEB(26), WHITE if hot else MUTED, "mm", 1)
        if MI[y]["title"] or y == 2009: T.txt(c, "★", (x + 20, y0 + 230 - h - 26), INT(34), GOLD, "mm")
    x = 60 + 5 * 52; d.rounded_rectangle((x - 12, y0 - 10, x + 52, y0 + 275), 12, outline=GOLD + (255,), width=5); T.txt(c, "C", (x + 20, y0 + 300), BEB(56), GOLD, "mm"); strip(c, 1640); c.save(O + "S4_ribbon.png")


def f5():                                                       # six trophies + photo strip
    c = bg(); pill(c, "THE TROPHY CASE"); T.glowtext(c, "6", (W / 2, 520), BEB(480), GOLD, "mm", 4); T.txt(c, "IPL TITLES", (W / 2, 760), BEB(130), WHITE, "mm", 10); d = ImageDraw.Draw(c, "RGBA")
    for i, (t, y) in enumerate([("DC", 2009), ("MI", 2013), ("MI", 2015), ("MI", 2017), ("MI", 2019), ("MI", 2020)]):
        x0 = 40 + i * 168; slot(c, (x0, 880, x0 + 156, 1180), f"IMAGE\n{y}", False); T.rr(c, (x0, 1190, x0 + 156, 1260), 16, fill=(DCY if t == "DC" else MIB) + (255,)); T.txt(c, str(y), (x0 + 78, 1226), BEB(48), (9, 14, 30) if t == "DC" else WHITE, "mm", 2)
    T.txt(c, "5 FINALS AS MI CAPTAIN · 5 TITLES · NEVER LOST ONE", (W / 2, 1360), BEB(46), WHITE, "mm", 4); T.txt(c, "JOINT-MOST: AMBATI RAYUDU ALSO HAS SIX", (W / 2, 1430), INT(26), GOLD, "mm", 4); strip(c, 1560, "OUR DATA: THE WINNING XI IN EVERY IPL FINAL, 2008-2025"); c.save(O + "S5_trophies.png")


def f6():                                                       # face-off: the two eras
    c = Image.new("RGB", (W, H), (9, 14, 30)); d = ImageDraw.Draw(c); a, b = M["mi_under_rohit_2014_2023"], M["mi_under_hardik_2024_2026"]
    for y in range(960): t = y / 960; d.line([(0, y), (W, y)], fill=(0, int(60 + 30 * (1 - t)), int(190 - 50 * t)))
    for y in range(960, H): t = (y - 960) / 960; d.line([(0, y), (W, y)], fill=(int(210 - 50 * t), int(45 - 20 * t), int(55 - 20 * t)))
    d.polygon([(0, 905), (W, 800), (W, 1010), (0, 1115)], fill=(9, 14, 30)); pill(c, "WITH ROHIT  vs  WITHOUT", (36, 200), 34); face_circle(c, 800, 560, 230, (255, 255, 255)); slot(c, (40, 1130, 480, 1580), "IMAGE: HARDIK (MI KIT)\nor FOOTAGE", True)
    T.txt(c, "2014 TO 2023", (40, 300), BEB(60), (200, 225, 255), "lt", 6); score(c, (40, 370), str(a['W']), str(a['L']), 210, 'l'); T.txt(c, f'{a["win_pct"]:.0f}% / PLAYOFFS {a["playoffs"]} OF 10', (44, 600), BEB(54), GOLD, "lt", 4)
    T.txt(c, "2024 TO 2026", (1040, 1130), BEB(60), (255, 215, 215), "rt", 6); score(c, (1040, 1200), str(b['W']), str(b['L']), 210, 'r'); T.txt(c, f'{b["win_pct"]:.0f}% / PLAYOFFS {b["playoffs"]} OF 3', (1036, 1430), BEB(54), GOLD, "rt", 4)
    strip(c, 1620); c.save(O + "S6_faceoff.png")


def f7():                                                       # card front
    c = bg((30, 20, 6), (8, 12, 30)); d = ImageDraw.Draw(c, "RGBA"); x0, y0, x1, y1 = 140, 230, 940, 1500; d.rounded_rectangle((x0 - 14, y0 - 14, x1 + 14, y1 + 14), 56, fill=GOLD + (255,)); d.rounded_rectangle((x0, y0, x1, y1), 44, fill=(10, 18, 44, 255))
    t = THRONE.resize((700, int(700 * THRONE.height / THRONE.width)), Image.LANCZOS).crop((0, 70, 700, 790)); m = Image.new("L", t.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, t.width, t.height), 30, fill=255); c.paste(t, (190, y0 + 60), m)
    deva(c, "मुंबईचा राजा", (540, y1 - 135), 100, GOLD); T.txt(c, "ROHIT SHARMA", (540, y1 - 50), BEB(70), WHITE, "mm", 6)
    for i, (v, l) in enumerate((("7,046", "RUNS"), ("303", "SIXES"), ("6", "TITLES"))): T.txt(c, v, (x0 + 160 + i * 240, y1 - 250), BEB(70), GOLD, "mm", 2); T.txt(c, l, (x0 + 160 + i * 240, y1 - 205), INT(20), MUTED, "mm", 4)
    strip(c, 1580); c.save(O + "S7_card_front.png")


def f8():                                                       # card back: every season
    c = bg((30, 20, 6), (8, 12, 30)); d = ImageDraw.Draw(c, "RGBA"); x0, y0, x1, y1 = 140, 230, 940, 1500; d.rounded_rectangle((x0 - 14, y0 - 14, x1 + 14, y1 + 14), 56, fill=GOLD + (255,)); d.rounded_rectangle((x0, y0, x1, y1), 44, fill=(10, 18, 44, 255))
    T.txt(c, "RUNS IN EVERY SEASON", (540, y0 + 70), BEB(56), GOLD, "mm", 6)
    for i, y in enumerate(YRS):
        r, k = i % 4, i // 4; xx = x0 + 60 + r * 175; yy = y0 + 140 + k * 200; col = DCY if y <= 2010 else MIB; d.rounded_rectangle((xx, yy, xx + 150, yy + 180), 14, fill=col + (255,), outline=(255, 255, 255, 120), width=2)
        T.txt(c, str(y), (xx + 75, yy + 34), BEB(40), WHITE if col == MIB else (9, 14, 30), "mm", 2); T.txt(c, str(S[y]["runs"]), (xx + 75, yy + 100), BEB(64), WHITE if col == MIB else (9, 14, 30), "mm", 1)
        if MI[y]["title"] or y == 2009: T.txt(c, "★", (xx + 75, yy + 152), INT(28), GOLD if col == MIB else (9, 14, 30), "mm")
    T.txt(c, "SECOND TO 7,000 RUNS · FIRST INDIAN TO 300 SIXES", (540, y1 - 55), INT(20), MUTED, "mm", 3); strip(c, 1580); c.save(O + "S8_card_back.png")


def f9():                                                       # optional: the Bumrah question, neutral data
    c = bg((4, 10, 28), (0, 40, 110)); d = ImageDraw.Draw(c, "RGBA"); pill(c, "THE OTHER NAME IN THE DEBATE (OPTIONAL)", (40, 200), 30); slot(c, (640, 290, 1040, 720), "IMAGE: BUMRAH (MI KIT)", False)
    T.txt(c, "BUMRAH", (50, 360), BEB(150), WHITE, "lt", 5, True); T.txt(c, "MATCHES BOWLED · EACH SEASON", (54, 520), INT(26), MUTED, "lt", 4); T.txt(c, "2016 TO 2026", (54, 560), BEB(60), GOLD, "lt", 4)
    ys = list(range(2016, 2027)); x0, ybase, hmax = 70, 1350, 480; bw = 940 / len(ys)
    for i, y in enumerate(ys):
        b, m = BUM[y]; xa = x0 + i * bw + 6; h = hmax * b / 16; d.rounded_rectangle((xa, ybase - h, xa + bw - 12, ybase), 8, fill=MIB + (255,) if b else (60, 70, 100, 255)); T.txt(c, f"{b}/{m}", (xa + (bw - 12) / 2, ybase - h - 24), BEB(30), WHITE, "mm", 0); T.txt(c, str(y)[2:], (xa + (bw - 12) / 2, ybase + 28), BEB(34), MUTED, "mm", 1)
    T.txt(c, "2023: DID NOT BOWL (0 OF 16 MI MATCHES)", (W / 2, 1460), INT(24), MUTED, "mm", 3); strip(c, 1590, "OUR DATA: IPL 2016-2026 · BOWLED / MI MATCHES"); c.save(O + "S9_bumrah.png")


def f10():                                                      # close
    c = bg((0, 20, 60), (0, 8, 24)); slot(c, (0, 0, W, 1000), "FOOTAGE: ROHIT, ARMS UP / FANS", True); ImageDraw.Draw(c, "RGBA").rectangle((0, 0, W, 1000), fill=(0, 20, 70, 110))
    face_circle(c, 540, 1000, 190); deva(c, "मुंबईचा राजा,", (W / 2, 1290), 130, GOLD, glow=True); deva(c, "रोहित शर्मा!", (W / 2, 1440), 130, WHITE); pill(c, "WELCOME BACK", (390, 1560), 36); c.save(O + "S10_close.png")


if __name__ == "__main__":
    fs = (f1, f2, f3, f4, f5, f6, f7, f8, f9, f10)
    for f in fs: f(); print("ok", f.__name__)
    sh = Image.new("RGB", (360 * 5, 640 * 2), (10, 10, 10)); names = ["S1_cold_open", "S2_chant", "S3_ring", "S4_ribbon", "S5_trophies", "S6_faceoff", "S7_card_front", "S8_card_back", "S9_bumrah", "S10_close"]
    for i, n in enumerate(names): sh.paste(Image.open(O + n + ".png").convert("RGB").resize((360, 640)), ((i % 5) * 360, (i // 5) * 640))
    sh.save(O + "S_ALL_storyboard2.png"); print(sh.size)
