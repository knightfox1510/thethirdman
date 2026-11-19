"""Storyboard stills (NOT a render) for the silent 'Rohit Sharma, MI captain' video, vertical 1080x1920, every IPL season 2008-2026 in the charts.
Draft headlines are written for the case where MI announce Rohit; if they do not, the whole thing is discarded. Figures: data/provenance/rohit_all_seasons.json, rohit_mi_figures.json (our archive).
The Rohit cut-out (owner-supplied, transparent PNG) goes where the dashed box is: data/licensed/in/rohit_mi.png once it arrives as a file.   python3 rohit_storyboard.py"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trades_mockups as T
from PIL import Image, ImageDraw
O = T.O; W, H = 1080, 1920; BEB, INT, INTS = T.BEB, T.INT, T.INTS
MIB, MIB2, GOLD, WHITE, MUTED = (0, 80, 190), (0, 45, 120), T.GOLD, T.WHITE, (170, 185, 215)
A = json.load(open("data/provenance/rohit_all_seasons.json")); M = json.load(open("data/provenance/rohit_mi_figures.json"))
S = {int(k): v for k, v in A["seasons"].items()}; MI = {int(k): v for k, v in M["mi_by_season"].items()}
DC_ = (240, 190, 40)


def base(top=(0, 70, 170), bot=(0, 25, 80)):
    return T.bg(W, H, top, bot)


def pill(c, text, xy=(60, 210), fill=GOLD, col=(9, 14, 30), size=40):
    w = int(ImageDraw.Draw(c).textlength(text, font=BEB(size)) + 60 + len(text) * 3); T.rr(c, (xy[0], xy[1], xy[0] + w, xy[1] + 66), 33, fill=fill + (255,)); T.txt(c, text, (xy[0] + w / 2, xy[1] + 36), BEB(size), col, "mm", 3)


def data_strip(c, text="OUR DATA: EVERY IPL SEASON, 2008-2026"):
    T.txt(c, text, (W / 2, 1535), INT(24), (210, 220, 240), "mm", 5)


def placeholder(c, box, label="ROHIT\nCUT-OUT"):
    d = ImageDraw.Draw(c, "RGBA"); x0, y0, x1, y1 = box
    for k in range(0, int(x1 - x0), 40): d.line([(x0 + k, y0), (x0 + k + 20, y0)], fill=(255, 255, 255, 150), width=4); d.line([(x0 + k, y1), (x0 + k + 20, y1)], fill=(255, 255, 255, 150), width=4)
    for k in range(0, int(y1 - y0), 40): d.line([(x0, y0 + k), (x0, y0 + k + 20)], fill=(255, 255, 255, 150), width=4); d.line([(x1, y0 + k), (x1, y0 + k + 20)], fill=(255, 255, 255, 150), width=4)
    for i, ln in enumerate(label.split("\n")): T.txt(c, ln, ((x0 + x1) / 2, (y0 + y1) / 2 - 30 + i * 70), BEB(64), (255, 255, 255, 200), "mm", 6)


def f1():
    c = base(); placeholder(c, (520, 330, 1060, 1560)); T.rr(c, (0, 1300, W, H), 0, fill=(0, 0, 0, 90))
    pill(c, "IPL 2027 · MUMBAI INDIANS", (60, 215))
    T.txt(c, "ROHIT", (60, 400), BEB(230), WHITE, "lt", 4, True); T.txt(c, "SHARMA", (60, 600), BEB(230), WHITE, "lt", 4, True)
    T.txt(c, "IS BACK AS", (64, 860), BEB(86), (150, 200, 255), "lt", 8); T.glowtext(c, "MI CAPTAIN", (64, 960), BEB(170), GOLD, "lt", 4)
    T.txt(c, "Won the T20 World Cup 2024 and the", (64, 1250), INTS(34), (230, 238, 250), "lt"); T.txt(c, "Champions Trophy 2025 as India captain", (64, 1296), INTS(34), (230, 238, 250), "lt")
    c.save(O + "R1_hero.png")


def f2():
    c = base(); pill(c, "THE TROPHY CASE", (60, 215))
    T.glowtext(c, "6", (W / 2, 560), BEB(560), GOLD, "mm", 4); T.txt(c, "IPL TITLES", (W / 2, 840), BEB(150), WHITE, "mm", 10)
    yrs = [("DC", 2009, DC_), ("MI", 2013, MIB), ("MI", 2015, MIB), ("MI", 2017, MIB), ("MI", 2019, MIB), ("MI", 2020, MIB)]
    d = ImageDraw.Draw(c, "RGBA")
    for i, (t, y, col) in enumerate(yrs):
        cx, cy = 190 + (i % 3) * 350, 1040 + (i // 3) * 190; d.rounded_rectangle((cx - 150, cy - 70, cx + 150, cy + 70), 30, fill=col + (255,), outline=(255, 255, 255, 220), width=4)
        T.txt(c, str(y), (cx, cy - 10), BEB(90), WHITE if t == "MI" else (9, 14, 30), "mm", 3); T.txt(c, "DECCAN CHARGERS" if t == "DC" else "MUMBAI INDIANS", (cx, cy + 46), INT(20), WHITE if t == "MI" else (9, 14, 30), "mm", 3)
    T.txt(c, "JOINT-MOST: AMBATI RAYUDU ALSO HAS SIX", (W / 2, 1440), INT(26), GOLD, "mm", 4); data_strip(c, "OUR DATA: THE WINNING XI IN EVERY IPL FINAL, 2008-2025")
    c.save(O + "R2_titles.png")


def f3():
    c = base(); pill(c, "AS MI CAPTAIN · 2013-2023", (60, 215))
    T.txt(c, "5 FINALS.", (W / 2, 640), BEB(250), WHITE, "mm", 5, True); T.glowtext(c, "5 TITLES.", (W / 2, 900), BEB(250), GOLD, "mm", 5)
    d = ImageDraw.Draw(c, "RGBA")
    for i, y in enumerate((2013, 2015, 2017, 2019, 2020)):
        cx = 140 + i * 200; d.ellipse((cx - 85, 1130, cx + 85, 1300), fill=GOLD + (255,)); T.txt(c, str(y), (cx, 1215), BEB(64), (9, 14, 30), "mm", 2)
    T.txt(c, "NEVER LOST A FINAL AS CAPTAIN", (W / 2, 1400), BEB(52), WHITE, "mm", 6); data_strip(c, "OUR DATA: EVERY IPL FINAL, 2008-2025")
    c.save(O + "R3_finals.png")


def f4():
    c = base((9, 14, 30), (22, 36, 72)); pill(c, "MI WINS, EVERY SEASON", (60, 215)); T.txt(c, "2008 TO 2026", (W / 2, 370), BEB(120), WHITE, "mm", 8)
    ys = list(range(2008, 2027)); x0, x1, ybase, hmax = 70, 1010, 1330, 700; bw = (x1 - x0) / len(ys); mx = 14
    d = ImageDraw.Draw(c, "RGBA")
    for y in ys:
        v = MI[y]["W"]; i = y - 2008; era = "pre" if y < 2013 else ("rohit" if y <= 2023 else "hardik"); col = {"pre": (120, 135, 170), "rohit": MIB, "hardik": (225, 60, 70)}[era]
        h = hmax * v / mx; xa = x0 + i * bw + 6; d.rounded_rectangle((xa, ybase - h, xa + bw - 12, ybase), 8, fill=col + (255,))
        T.txt(c, str(v), (xa + (bw - 12) / 2, ybase - h - 24), BEB(36), WHITE, "mm", 1); T.txt(c, str(y)[2:], (xa + (bw - 12) / 2, ybase + 28), BEB(34), MUTED, "mm", 1)
        if MI[y]["title"]: T.txt(c, "★", (xa + (bw - 12) / 2, ybase - h - 62), INT(40), GOLD, "mm")
    for lab, col, x in (("BEFORE ROHIT", (120, 135, 170), 80), ("ROHIT 2013-23", MIB, 400), ("HARDIK 2024-26", (225, 60, 70), 700)):
        d.rounded_rectangle((x, 1420, x + 30, 1450), 6, fill=col + (255,)); T.txt(c, lab, (x + 44, 1436), INT(26), WHITE, "lm", 3)
    data_strip(c); c.save(O + "R4_all_seasons_wins.png")


def f5():
    c = base(); pill(c, "THE TWO ERAS", (60, 215)); T.txt(c, "WITH ROHIT", (W / 2, 440), BEB(110), WHITE, "mm", 8); T.txt(c, "2014-2023 · 10 SEASONS", (W / 2, 520), INT(28), MUTED, "mm", 5)
    a, b = M["mi_under_rohit_2014_2023"], M["mi_under_hardik_2024_2026"]
    T.txt(c, f'{a["W"]}-{a["L"]}', (W / 2, 690), BEB(250), (140, 200, 255), "mm", 4); T.txt(c, f'{a["win_pct"]:.0f}% OF DECIDED MATCHES · PLAYOFFS IN {a["playoffs"]} OF 10', (W / 2, 830), BEB(46), WHITE, "mm", 3)
    ImageDraw.Draw(c).line([(120, 920), (960, 920)], fill=(255, 255, 255), width=3)
    T.txt(c, "WITH HARDIK", (W / 2, 1010), BEB(110), WHITE, "mm", 8); T.txt(c, "2024-2026 · 3 SEASONS", (W / 2, 1090), INT(28), MUTED, "mm", 5)
    T.txt(c, f'{b["W"]}-{b["L"]}', (W / 2, 1260), BEB(250), (255, 120, 125), "mm", 4); T.txt(c, f'{b["win_pct"]:.0f}% OF DECIDED MATCHES · PLAYOFFS IN {b["playoffs"]} OF 3', (W / 2, 1400), BEB(46), WHITE, "mm", 3)
    data_strip(c); c.save(O + "R5_eras.png")


def f6():
    c = base((9, 14, 30), (22, 36, 72)); pill(c, "ROHIT'S RUNS, EVERY SEASON", (60, 215)); T.txt(c, "7,046 RUNS", (W / 2, 400), BEB(160), GOLD, "mm", 6); T.txt(c, "THROUGH 2025 · SECOND ONLY TO KOHLI", (W / 2, 490), INT(28), WHITE, "mm", 5)
    ys = list(range(2008, 2027)); x0, x1, ybase, hmax = 70, 1010, 1330, 620; bw = (x1 - x0) / len(ys); mx = 560; d = ImageDraw.Draw(c, "RGBA")
    for y in ys:
        v = S[y]["runs"]; i = y - 2008; col = DC_ if y <= 2010 else MIB; h = hmax * v / mx; xa = x0 + i * bw + 6
        d.rounded_rectangle((xa, ybase - h, xa + bw - 12, ybase), 8, fill=col + (255,)); T.txt(c, str(v), (xa + (bw - 12) / 2, ybase - h - 22), BEB(26), WHITE, "mm", 0); T.txt(c, str(y)[2:], (xa + (bw - 12) / 2, ybase + 28), BEB(34), MUTED, "mm", 1)
    for lab, col, x in (("DECCAN CHARGERS 2008-10", DC_, 60), ("MUMBAI INDIANS 2011-26", MIB, 600)):
        d.rounded_rectangle((x, 1420, x + 30, 1450), 6, fill=col + (255,)); T.txt(c, lab, (x + 44, 1436), INT(26), WHITE, "lm", 3)
    data_strip(c); c.save(O + "R6_runs_all_seasons.png")


def f7():
    c = base(); pill(c, "ONLY HITMAN", (60, 215)); rows = [("7,000+", "IPL RUNS", "SECOND BATTER AFTER KOHLI"), ("300+", "IPL SIXES", "FIRST INDIAN · KOHLI 292"), ("6", "IPL TITLES", "JOINT-MOST · RAYUDU TOO")]
    for i, (big, lab, sub) in enumerate(rows):
        y = 420 + i * 360; T.rr(c, (60, y, 1020, y + 310), 30, fill=(255, 255, 255, 30), outline=GOLD + (255,), width=5)
        T.glowtext(c, big, (330, y + 150), BEB(190), GOLD, "mm", 4); T.txt(c, lab, (560, y + 110), BEB(72), WHITE, "lm", 6); T.txt(c, sub, (560, y + 180), INT(26), (215, 225, 245), "lm", 2)
    data_strip(c, "OUR DATA: EVERY IPL SEASON, 2008-2025"); c.save(O + "R7_records.png")


def f8():
    c = base((9, 14, 30), (22, 36, 72)); pill(c, "ONE THING THAT DID NOT CHANGE", (60, 215)); T.txt(c, "POWERPLAY STRIKE RATE", (W / 2, 420), BEB(86), WHITE, "mm", 6); T.txt(c, "ROHIT VS THE WHOLE LEAGUE", (W / 2, 500), INT(28), MUTED, "mm", 5)
    for k, (lab, r, l) in enumerate((("2014-2023", 125.4, 125.7), ("2024-2026", 151.7, 153.3))):
        y = 720 + k * 400; T.txt(c, lab, (W / 2, y - 80), BEB(70), GOLD, "mm", 6)
        for j, (nm, v, col) in enumerate((("ROHIT", r, MIB), ("LEAGUE", l, (150, 160, 185)))):
            yy = y + j * 100; w = 760 * v / 160; ImageDraw.Draw(c).rounded_rectangle((200, yy - 36, 200 + w, yy + 36), 14, fill=col); T.txt(c, nm, (180, yy), BEB(40), WHITE, "rm", 3); T.txt(c, f"{v:.0f}", (210 + w, yy), BEB(54), WHITE, "lm", 2)
    T.txt(c, "HE OPENED AT THE LEAGUE'S PACE IN BOTH ERAS", (W / 2, 1420), BEB(44), WHITE, "mm", 4); data_strip(c); c.save(O + "R8_tempo.png")


def f9():
    c = base(); placeholder(c, (150, 330, 930, 1450)); pill(c, "IPL 2027", (60, 215)); T.glowtext(c, "WELCOME BACK", (W / 2, 1490), BEB(130), GOLD, "mm", 6); T.txt(c, "ROHIT SHARMA · MI CAPTAIN", (W / 2, 1585), BEB(60), WHITE, "mm", 8)
    c.save(O + "R9_close.png")


if __name__ == "__main__":
    for f in (f1, f2, f3, f4, f5, f6, f7, f8, f9): f(); print("ok", f.__name__)
    names = ["R1_hero", "R2_titles", "R3_finals", "R4_all_seasons_wins", "R5_eras", "R6_runs_all_seasons", "R7_records", "R8_tempo", "R9_close"]
    sh = Image.new("RGB", (360 * 5, 640 * 2), (10, 10, 10))
    for i, n in enumerate(names): sh.paste(Image.open(O + n + ".png").convert("RGB").resize((360, 640)), ((i % 5) * 360, (i // 5) * 640))
    sh.save(O + "R_ALL_storyboard.png"); print(sh.size)
