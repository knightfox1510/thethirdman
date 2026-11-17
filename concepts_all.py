"""Format concept mock-ups (stills, NOT a render) for reel/video ideas beyond the Rohit video: 8 concepts, 1-4 frames each, REAL data. Images only (plain dashed boxes = images to come); licensed photos only.
Concepts: W Wrapped cards (Dhoni) | N Newspaper front page (Dhoni retirement) | A Sticker album (Gujarat Titans retention page) | R Receipt (confirmed trade fees) | P Film poster + credits (Dhoni) | K Calendar countdown (auction)
          M City map of trade moves | C Career scorecard (Rohit, every season). Devanagari via Noto fonts (Raqm). Output: deliver/_trades_mockups/X_<concept>_<n>.png + X_ALL_<part>.png.   python3 concepts_all.py"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trades_mockups as T
import rohit_storyboard2 as B
from rohit_storyboard2 import deva, slot, pill, strip, score, S, MI
from PIL import Image, ImageDraw, ImageFont, ImageFilter
O = T.O; W, H = 1080, 1920; BEB, INT, INTS = T.BEB, T.INT, T.INTS; GOLD, WHITE, MUTED = T.GOLD, T.WHITE, (170, 185, 215); NAVY = (9, 14, 30)
D = json.load(open("data/provenance/dhoni_ipl_figures.json")); SE = {s["season"]: s for s in D["seasons"]}
MONO = lambda z: ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf", z)
PLAY = lambda z: ImageFont.truetype("fonts/PlayfairBold.ttf", z)
DS = lambda z: ImageFont.truetype("fonts/NotoSerifDevanagari-Bold.ttf", z, layout_engine=ImageFont.Layout.RAQM)
CSKY = (250, 200, 20); MIB = (0, 85, 200)


def flat(col): return Image.new("RGB", (W, H), col)


def txt(c, s, xy, font, fill, anchor="la"): ImageDraw.Draw(c).text(xy, s, font=font, fill=fill, anchor=anchor)


# ================================================================ W  WRAPPED
def wrapped(n):
    pal = [(250, 200, 20, NAVY), (20, 30, 90, CSKY), (255, 90, 120, NAVY), (30, 160, 120, WHITE)][n - 1]; c = flat(pal[:3]); d = ImageDraw.Draw(c, "RGBA"); ink = pal[3]
    d.ellipse((-300, -300, 500, 500), fill=(255, 255, 255, 40)); d.ellipse((600, 1300, 1500, 2200), fill=(0, 0, 0, 40))
    T.txt(c, "MSD WRAPPED", (60, 90), BEB(54), ink, "lm", 8); T.txt(c, "IPL 2013-2025", (1020, 90), BEB(54), ink, "rm", 8)
    if n == 1:
        T.txt(c, "YOUR", (60, 330), BEB(150), ink, "lm", 4); T.txt(c, "IPL", (60, 470), BEB(150), ink, "lm", 4); T.txt(c, "WRAPPED.", (60, 610), BEB(190), ink, "lm", 4)
        slot(c, (240, 760, 840, 1360), "IMAGE: MSD\n(round crop, CSK kit)", False); T.txt(c, "13 SEASONS · 159 INNINGS · 200 SIXES", (540, 1480), BEB(52), ink, "mm", 4); T.txt(c, "SWIPE >>", (540, 1620), BEB(60), ink, "mm", 10)
    if n == 2:
        T.txt(c, "YOUR NUMBER OF THE YEAR(S)", (60, 280), BEB(60), ink, "lm", 6); T.txt(c, str(D["last2_most_sixes"]["first_val"]), (540, 800), BEB(700), ink, "mm", 2)
        T.txt(c, "SIXES IN THE LAST TWO OVERS", (540, 1230), BEB(80), ink, "mm", 4); T.txt(c, f'THE NEXT BEST HAS {D["last2_most_sixes"]["second_val"]}', (540, 1330), BEB(56), ink, "mm", 6); T.txt(c, "#1 IN OUR DATA", (540, 1500), BEB(90), (255, 200, 40), "mm", 8)
    if n == 3:
        T.txt(c, "YOUR SIGNATURE OVER", (60, 280), BEB(60), ink, "lm", 6); T.txt(c, "THE 20TH", (540, 620), BEB(330), ink, "mm", 4); a, b = D["over20"]["dhoni"]["sr"], D["over20"]["league_sr"]
        for k, (lab, v, col) in enumerate((("YOU", a, CSKY), ("THE LEAGUE", b, (220, 225, 240)))):
            y = 920 + k * 260; w = 720 * v / 260; d.rounded_rectangle((60, y, 60 + w, y + 150), 30, fill=col + (255,)); T.txt(c, f"{v:.0f}", (60 + w - 30, y + 78), BEB(120), NAVY, "rm", 2); T.txt(c, lab, (60, y - 40), BEB(48), ink, "lm", 6)
        T.txt(c, "STRIKE RATE IN THE FINAL OVER", (540, 1520), BEB(56), ink, "mm", 6)
    if n == 4:
        T.txt(c, "YOUR TOP 5 SEASONS", (60, 280), BEB(70), ink, "lm", 6); T.txt(c, "BY RUNS", (60, 360), BEB(60), ink, "lm", 6)
        top = sorted(SE.values(), key=lambda s: -s["runs"])[:5]
        for i, s in enumerate(top):
            y = 520 + i * 230; T.txt(c, str(i + 1), (70, y), BEB(190), ink, "lm", 2); T.txt(c, str(s["season"]), (260, y - 30), BEB(110), ink, "lm", 4); T.txt(c, f'{s["runs"]} RUNS · {s["sixes"]} SIXES', (260, y + 55), BEB(48), ink, "lm", 4)
        T.txt(c, "OUR DATA: IPL 2013-2025 (HE DID NOT PLAY 2026)", (540, 1740), BEB(34), ink, "mm", 4)
    c.save(O + f"X_wrapped_{n}.png")


# ================================================================ N  NEWSPAPER
def newspaper():
    c = flat((234, 226, 206)); d = ImageDraw.Draw(c, "RGBA"); ink = (30, 24, 18); d.rectangle((40, 40, 1040, 1880), outline=ink, width=4)
    txt(c, "दैनिक चौकार", (540, 160), DS(150), ink, "mm"); d.line([(60, 260), (1020, 260)], fill=ink, width=6); d.line([(60, 272), (1020, 272)], fill=ink, width=2)
    txt(c, "THE DAILY FOUR · EXTRA", (60, 310), MONO(26), ink, "lm"); txt(c, "TUE 17 NOVEMBER 2026", (1020, 310), MONO(26), ink, "rm"); d.line([(60, 350), (1020, 350)], fill=ink, width=2)
    txt(c, "DHONI RETIRES", (540, 470), PLAY(104), ink, "mm"); txt(c, "FROM THE IPL", (540, 590), PLAY(104), (160, 20, 30), "mm")
    txt(c, "Becomes CSK mentor: 278 matches, 5,439 runs,", (540, 680), PLAY(32), ink, "mm"); txt(c, "five titles as captain", (540, 722), PLAY(32), ink, "mm"); d.line([(60, 760), (1020, 760)], fill=ink, width=3)
    slot(c, (60, 790, 660, 1250), "IMAGE: MSD\n(photo, caption below)", False); txt(c, "FILE: HIS LAST SEASON WAS 2025.", (60, 1275), MONO(24), ink, "lm")
    d.rectangle((700, 790, 1020, 1250), fill=(30, 24, 18, 255)); txt(c, "BY THE NUMBERS", (860, 840), BEB(46), CSKY, "mm"); [(T.txt(c, a, (860, 900 + i * 82), BEB(58), WHITE, "mm", 1), T.txt(c, b, (860, 935 + i * 82), INT(17), (200, 200, 200), "mm", 3)) for i, (a, b) in enumerate((("278", "MATCHES"), ("5,439", "RUNS"), ("5", "TITLES"), ("10", "FINALS")))]
    for k in range(3):
        x = 60 + k * 330
        for r in range(12): d.rectangle((x, 1340 + r * 26, x + 300 - (60 if r % 5 == 4 else 0), 1352 + r * 26), fill=(30, 24, 18, 120))
    d.rectangle((60, 1350, 390, 1660), fill=(0, 0, 0, 0)); d.rectangle((400, 1700, 1020, 1860), fill=(160, 20, 30, 255)); txt(c, '"There is no CSK without MS Dhoni."', (710, 1760), PLAY(34), WHITE, "mm"); txt(c, "N. SRINIVASAN, CSK", (710, 1815), MONO(26), (255, 220, 220), "mm")
    c.save(O + "X_newspaper_1.png")


# ================================================================ A  STICKER ALBUM
def album():
    c = T.bg(W, H, (14, 22, 60), (6, 10, 28)); d = ImageDraw.Draw(c, "RGBA"); d.rounded_rectangle((30, 150, 1050, 1760), 40, fill=(245, 238, 215, 255), outline=(200, 160, 40, 255), width=10)
    d.rectangle((30, 150, 1050, 290), fill=(28, 45, 100, 255)); T.txt(c, "GUJARAT TITANS · IPL 2027", (540, 220), BEB(84), WHITE, "mm", 8)
    ret = ["Gill", "Sudharsan", "Tewatia", "Kushagra", "Rawat", "Buttler", "Banton", "Phillips", "Sundar", "Sai Kishore", "Suthar", "Rashid", "Jayant", "Holder", "Rabada", "Siraj", "Prasidh", "Brar", "Ashok", "Arshad", "Harshal*"]; rel = ["Ishant", "Wood", "Khejroliya", "Shahrukh", "Esterhuizen"]
    for i, nm in enumerate(ret + rel):
        r, k = i // 5, i % 5; x = 60 + k * 196; y = 330 + r * 228; released = i >= len(ret)
        d.rounded_rectangle((x, y, x + 184, y + 214), 16, fill=(255, 255, 255, 255), outline=(150, 150, 160, 255) if released else (28, 45, 100, 255), width=4)
        if released:
            d.rectangle((x + 8, y + 8, x + 176, y + 160), fill=(235, 235, 240, 255)); d.line([(x + 8, y + 8), (x + 176, y + 160)], fill=(225, 60, 70, 200), width=5); d.line([(x + 8, y + 160), (x + 176, y + 8)], fill=(225, 60, 70, 200), width=5)
        else: d.rectangle((x + 8, y + 8, x + 176, y + 160), fill=(60, 80, 150, 255)); T.txt(c, "IMAGE", (x + 92, y + 84), BEB(30), (255, 255, 255, 200), "mm", 4)
        T.txt(c, nm.upper(), (x + 92, y + 188), BEB(32), (140, 140, 150) if released else (20, 30, 70), "mm", 1)
    T.txt(c, "KEPT: 21 (* HARSHAL TRADED IN)", (60, 1815), INT(22), WHITE, "lm", 3); T.txt(c, "CROSSED OUT: 5 RELEASED", (1020, 1815), INT(22), (255, 130, 140), "rm", 3)
    T.txt(c, "PER CRICINFO'S RETENTION COVERAGE, 17 NOV 2026 · FULL LISTS STILL TO VERIFY", (540, 1860), INT(20), MUTED, "mm", 2); c.save(O + "X_album_1.png")


# ================================================================ R  RECEIPT
def receipt():
    c = T.bg(W, H, (30, 33, 40), (12, 13, 17)); d = ImageDraw.Draw(c, "RGBA"); x0, x1, y0, y1 = 150, 930, 120, 1800; d.rectangle((x0, y0, x1, y1), fill=(250, 250, 246, 255))
    for k in range(0, x1 - x0, 26): d.polygon([(x0 + k, y0), (x0 + k + 13, y0 - 16), (x0 + k + 26, y0)], fill=(250, 250, 246, 255)); d.polygon([(x0 + k, y1), (x0 + k + 13, y1 + 16), (x0 + k + 26, y1)], fill=(250, 250, 246, 255))
    ink = (30, 30, 34); txt(c, "IPL 2027 TRADE WINDOW", (540, 200), MONO(52), ink, "mm"); txt(c, "TAX INVOICE · SIX DEALS", (540, 260), MONO(30), ink, "mm"); d.line([(180, 300), (900, 300)], fill=ink, width=3)
    rows = [("HARDIK PANDYA   MI>PBKS", "18.00"), ("ARSHDEEP SINGH   PBKS>MI", "18.00"), ("RISHABH PANT   LSG>DC", "15.00"), ("KULDEEP YADAV   DC>LSG", "13.50"), ("LIVINGSTONE   SRH>CSK", " 6.00"), ("KHALEEL AHMED   CSK>SRH", " 4.80"), ("HARSHAL PATEL   SRH>GT", " 4.00"), ("JACK EDWARDS   SRH>CSK", " 3.00"), ("T NATARAJAN   DC>SRH", " 5.00"), ("NATHAN ELLIS   CSK>SRH", " 2.00"), ("ZEESHAN ANSARI   SRH>DC", " 0.40")]
    for i, (a, b) in enumerate(rows): y = 360 + i * 80; txt(c, a, (180, y), MONO(31), ink, "lm"); txt(c, b, (900, y), MONO(36), ink, "rm"); d.line([(180, y + 40), (900, y + 40)], fill=(190, 190, 190, 255), width=1)
    tot = 18 + 18 + 15 + 13.5 + 6 + 4.8 + 4 + 3 + 5 + 2 + .4; d.line([(180, 1290), (900, 1290)], fill=ink, width=5); txt(c, "TOTAL (INR CRORE)", (180, 1350), MONO(38), ink, "lm"); txt(c, f"{tot:.2f}", (900, 1350), MONO(60), (160, 20, 30), "rm")
    txt(c, "* SHAMI, SIDDHARTH, CURRAN: FEES NOT STATED", (180, 1440), MONO(26), ink, "lm"); txt(c, "FEES AS PUBLISHED: SOME FROM TRACKERS", (180, 1490), MONO(26), ink, "lm")
    for k in range(40): h = 60 if k % 3 else 90; d.rectangle((260 + k * 14, 1580, 260 + k * 14 + (5 if k % 2 else 9), 1580 + h), fill=ink)
    txt(c, "THANK YOU, COME AGAIN ON 16 DEC (AUCTION)", (540, 1735), MONO(28), ink, "mm"); c.save(O + "X_receipt_1.png")


# ================================================================ P  FILM POSTER + CREDITS
def poster(n):
    c = T.bg(W, H, (4, 8, 24), (0, 0, 0)); d = ImageDraw.Draw(c, "RGBA")
    if n == 1:
        for k in range(14): a = math.radians(-90 + (k - 6.5) * 9); d.polygon([(540, 1900), (540 + 2400 * math.cos(a - .03), 1900 + 2400 * math.sin(a - .03)), (540 + 2400 * math.cos(a + .03), 1900 + 2400 * math.sin(a + .03))], fill=(255, 210, 80, 26))
        T.txt(c, "A FILM IN 13 SEASONS", (540, 130), BEB(54), (255, 220, 120), "mm", 14); slot(c, (140, 220, 940, 1180), "IMAGE: MSD\n(full-height cut-out on the spotlight)", False)
        T.glowtext(c, "THE FINISHER", (540, 1330), BEB(230), GOLD, "mm", 10); T.txt(c, "ONE JOB. 98 SIXES IN THE LAST TWO OVERS.", (540, 1480), BEB(52), WHITE, "mm", 6)
        T.txt(c, "STARRING  MS DHONI   ·   CHENNAI SUPER KINGS", (540, 1590), INT(26), (200, 210, 230), "mm", 6); T.txt(c, "OUR DATA: IPL 2013-2025", (540, 1760), INT(22), MUTED, "mm", 5)
    else:
        T.txt(c, "STARRING", (540, 140), BEB(60), (255, 220, 120), "mm", 18)
        lines = [("MOST SIXES, LAST TWO OVERS", "98"), ("MOST RUNS, OVERS 16 TO 20", "2,573"), ("STRIKE RATE, THE 20TH OVER", "252"), ("IPL MATCHES", "278"), ("TITLES AS CAPTAIN", "5"), ("FINALS AS CAPTAIN", "10"), ("MATCHES AS CAPTAIN", "235"), ("WINS AS CAPTAIN", "136")]
        for i, (a, b) in enumerate(lines): y = 300 + i * 190; T.txt(c, b, (540, y), BEB(130), GOLD, "mm", 4); T.txt(c, a, (540, y + 80), INT(26), WHITE, "mm", 8)
        T.txt(c, "A THE THIRD MAN PRODUCTION", (540, 1830), BEB(44), (255, 220, 120), "mm", 14)
    c.save(O + f"X_poster_{n}.png")


# ================================================================ K  CALENDAR
def calendar():
    c = flat((226, 222, 214)); d = ImageDraw.Draw(c, "RGBA"); d.rounded_rectangle((80, 110, 1000, 1500), 30, fill=(255, 255, 255, 255), outline=(60, 60, 60, 255), width=6); d.rectangle((80, 110, 1000, 330), fill=(200, 30, 45, 255))
    for k in range(6): d.ellipse((200 + k * 140, 80, 232 + k * 140, 140), fill=(40, 40, 44, 255))
    T.txt(c, "DECEMBER 2026", (540, 230), BEB(130), WHITE, "mm", 8); days = ["TUE", "WED", "THU", "FRI", "SAT", "SUN", "MON"]
    for k, dname in enumerate(("MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN")): T.txt(c, dname, (140 + k * 120, 380), INT(26), (90, 90, 100), "mm", 3)
    for dday in range(1, 32):
        i = dday - 1 + 1; r, k = i // 7, i % 7; x, y = 140 + k * 120, 470 + r * 110; col = (30, 30, 36)
        if dday == 16: d.ellipse((x - 48, y - 48, x + 48, y + 48), fill=(200, 30, 45, 255)); col = WHITE
        elif dday == 9: d.ellipse((x - 46, y - 46, x + 46, y + 46), outline=(0, 85, 200, 255), width=6)
        T.txt(c, str(dday), (x, y), BEB(60), col, "mm", 1)
    T.txt(c, "29", (240, 1180), BEB(260), (200, 30, 45), "mm", 2); T.txt(c, "DAYS", (240, 1330), BEB(70), (30, 30, 36), "mm", 8); T.txt(c, "TO THE AUCTION", (420, 1270), BEB(66), (30, 30, 36), "lm", 5); T.txt(c, "GOA · 16 DEC · ONE DAY", (420, 1350), BEB(50), (200, 30, 45), "lm", 4); T.txt(c, "COUNTED FROM 17 NOV, RETENTION DAY", (420, 1420), INT(22), (90, 90, 100), "lm", 3)
    T.txt(c, "RED: AUCTION · BLUE: TRADE WINDOW SHUTS ~9 DEC (REPORTED)", (540, 1560), INT(22), (60, 60, 70), "mm", 2); slot(c, (80, 1610, 1000, 1830), "IMAGE: AUCTION HALL / PADDLE", False); c.save(O + "X_calendar_1.png")


# ================================================================ M  CITY MAP
def tmap():
    c = T.bg(W, H, (6, 14, 36), (2, 6, 20)); d = ImageDraw.Draw(c, "RGBA"); T.txt(c, "THE MOVES", (540, 130), BEB(120), GOLD, "mm", 10); T.txt(c, "SIX DEALS · SCHEMATIC LAYOUT, NOT TO SCALE", (540, 215), INT(24), MUTED, "mm", 4)
    city = {"MI": (19.1, 72.9, (0, 90, 200)), "CSK": (13.1, 80.3, (250, 200, 20)), "DC": (28.6, 77.2, (40, 90, 200)), "KKR": (22.6, 88.4, (110, 50, 160)), "SRH": (17.4, 78.5, (240, 110, 20)), "RCB": (13.0, 77.6, (200, 30, 45)),
            "LSG": (26.8, 80.9, (0, 150, 190)), "RR": (26.9, 75.8, (230, 60, 150)), "GT": (23.0, 72.6, (30, 50, 110)), "PBKS": (30.7, 76.7, (215, 40, 50))}
    pos = {"PBKS": (300, 450), "DC": (580, 520), "RR": (210, 700), "LSG": (860, 650), "GT": (170, 960), "KKR": (900, 980), "MI": (210, 1230), "SRH": (580, 1100), "RCB": (400, 1440), "CSK": (800, 1380)}
    deals = [("PBKS", "MI", "HARDIK ↔ ARSHDEEP", 0), ("LSG", "DC", "PANT ↔ KULDEEP", 0), ("SRH", "CSK", "4 PLAYERS", 0), ("SRH", "DC", "NATARAJAN", 1), ("SRH", "GT", "HARSHAL", 1), ("LSG", "RR", "SHAMI · SIDDHARTH ↔ CURRAN", 1)]
    for a, b, lab, curve in deals:
        (x1, y1), (x2, y2) = pos[a], pos[b]; mx, my = (x1 + x2) / 2 + (40 if curve else -40), (y1 + y2) / 2 - 40
        pts = [((1 - t) ** 2 * x1 + 2 * (1 - t) * t * mx + t * t * x2, (1 - t) ** 2 * y1 + 2 * (1 - t) * t * my + t * t * y2) for t in [i / 30 for i in range(31)]]; d.line(pts, fill=GOLD + (255,), width=6)
        ex, ey = pts[-1]; ax, ay = pts[-3]; ang = math.atan2(ey - ay, ex - ax); d.polygon([(ex, ey), (ex - 26 * math.cos(ang - .45), ey - 26 * math.sin(ang - .45)), (ex - 26 * math.cos(ang + .45), ey - 26 * math.sin(ang + .45))], fill=GOLD + (255,))
        rr = pts[15]; T.rr(c, (rr[0] - 6 * len(lab) - 12, rr[1] - 20, rr[0] + 6 * len(lab) + 12, rr[1] + 20), 20, fill=(9, 14, 30, 235), outline=GOLD + (255,), width=2); T.txt(c, lab, rr, BEB(26), GOLD, "mm", 1)
    for k, (x, y) in pos.items(): d.ellipse((x - 44, y - 44, x + 44, y + 44), fill=city[k][2] + (255,), outline=(255, 255, 255, 255), width=4); T.txt(c, k, (x, y), BEB(34), WHITE if k != "CSK" else NAVY, "mm", 1)
    strip(c, 1560, "DEALS FROM THE IPL'S PRESS RELEASES, 2026"); c.save(O + "X_map_1.png")


# ================================================================ C  CAREER SCORECARD
def scorecard():
    c = flat((244, 238, 218)); d = ImageDraw.Draw(c, "RGBA"); ink = (36, 28, 18); d.rectangle((0, 0, W, 230), fill=(0, 60, 150, 255)); T.txt(c, "ROHIT SHARMA · IPL BATTING CARD", (540, 100), BEB(78), WHITE, "mm", 6); T.txt(c, "EVERY SEASON, 2008 TO 2026 · OUR DATA", (540, 175), INT(26), (210, 225, 250), "mm", 4)
    cols = [("SEASON", 80, "lm"), ("TEAM", 270, "lm"), ("INN", 500, "rm"), ("RUNS", 640, "rm"), ("BALLS", 790, "rm"), ("6s", 890, "rm"), ("SR", 1020, "rm")]
    for h, x, a in cols: T.txt(c, h, (x, 275), BEB(40), (120, 100, 70), a, 3)
    d.line([(60, 305), (1020, 305)], fill=ink, width=4)
    for i, y in enumerate(range(2008, 2027)):
        s_ = S[y]; yy = 350 + i * 66; title = MI[y]["title"] or y == 2009
        if title: d.rectangle((60, yy - 30, 1020, yy + 30), fill=(255, 220, 120, 150))
        vals = [str(y), "DC" if y <= 2010 else "MI", str(s_["inn"]), str(s_["runs"]), str(s_["balls"]), str(s_["sixes"]), f'{s_["sr"]:.1f}']
        for (h, x, a), v in zip(cols, vals): T.txt(c, v + ("*" if (h == "SEASON" and title) else ""), (x, yy), BEB(46), ink, a, 2)
    d.line([(60, 1630), (1020, 1630)], fill=ink, width=4); tot = [("TOTAL", 80, "lm", "TOTAL"), ("", 270, "lm", ""), ("", 500, "rm", "275"), ("", 640, "rm", "7,329"), ("", 790, "rm", "5,514"), ("", 890, "rm", "324"), ("", 1020, "rm", "132.9")]
    for _, x, a, v in tot: T.txt(c, v, (x, 1680), BEB(54), (160, 20, 30), a, 2)
    T.txt(c, "* = IPL TITLE SEASON · DC = DECCAN CHARGERS · SR = STRIKE RATE", (540, 1780), INT(22), (90, 80, 60), "mm", 3); c.save(O + "X_scorecard_1.png")


if __name__ == "__main__":
    for n in (1, 2, 3, 4): wrapped(n)
    newspaper(); album(); receipt(); poster(1); poster(2); calendar(); tmap(); scorecard()
    sets = {"A": ["X_wrapped_1", "X_wrapped_2", "X_wrapped_3", "X_wrapped_4", "X_newspaper_1", "X_album_1"], "B": ["X_receipt_1", "X_poster_1", "X_poster_2", "X_calendar_1", "X_map_1", "X_scorecard_1"]}
    for k, names in sets.items():
        sh = Image.new("RGB", (360 * 6, 640), (10, 10, 10))
        for i, n in enumerate(names): sh.paste(Image.open(O + n + ".png").convert("RGB").resize((360, 640)), (i * 360, 0))
        sh.save(O + f"X_ALL_{k}.png"); print("sheet", k, sh.size)
