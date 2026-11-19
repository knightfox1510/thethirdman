"""Soundless vertical preview of the Bumrah video in look B (night cinematic): photo cards on blurred backdrops, big condensed type, amber accent, animated counters and bars.
1080x1920, 30 fps, NO audio (the voice-over and music come later). Numbers are asserted against data/provenance/bumrah_*_figures.json.
    python3 bumrah_render.py [--preview]   -> deliver/bumrah_unplayable/Bumrah_Unplayable_Short_9x16_preview_silent.mp4"""
import os, sys, json, math, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
R = os.path.dirname(os.path.abspath(__file__)); FD = f"{R}/fonts/"; IN = f"{R}/data/licensed/in/"; CUT = f"{R}/data/licensed/cut/"; W, H, FPS = 1080, 1920, 30
PREVIEW = "--preview" in sys.argv
F0 = json.load(open(f"{R}/data/provenance/bumrah_tests_figures.json")); F1 = json.load(open(f"{R}/data/provenance/bumrah_context_figures.json"))
assert (F0["tests"], F0["wkts"], F0["avg"], F0["sr"]) == (52, 234, 19.79, 42.9) and round(F1["bumrah_bowled_lbw_pct"]) == 52 and round(F1["baseline_bowled_lbw_pct"]) == 33 and round(F1["baseline_avg"], 1) == 26.1
assert (F0["new_ball_overs1_20"]["avg"], F0["old_ball_overs21plus"]["avg"]) == (23.9, 18.2) and round(F0["india_with"]["win_pct"]) == 42 and round(F0["india_without"]["win_pct"]) == 67 and F0["played_of"] == [52, 88]
assert (F1["ipl_phases"]["death"]["econ"], round(F1["ipl_phases"]["death"]["league_econ_same_seasons_weighted"], 1), F1["ipl_vs_left_handers"]["econ"], F1["ipl_vs_left_handers"]["league_econ"]) == (7.87, 9.6, 6.35, 8.31)
AM = (255, 200, 80); WH = (250, 250, 250); MU = (196, 206, 228); DK = (4, 6, 14); RD = (240, 84, 84)
def F(n, z): return ImageFont.truetype(FD + n, z)
BS = lambda z: F("BigShouldersBlack.ttf", z); IB = lambda z: F("Inter-Bold.otf", z); IM = lambda z: F("Inter-Medium.otf", z); MB = lambda z: F("PlexMonoSB.ttf", z); MO = lambda z: F("PlexMono.ttf", z)
def ease(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)
def eo(x): x = min(1, max(0, x)); return 1 - (1 - x) ** 3
def seg(t, a, b): return eo((t - a) / max(1e-6, b - a))
_PH = {}
def photo(name): 
    if name not in _PH: _PH[name] = Image.open(IN + name).convert("RGB")
    return _PH[name]
_BG = {}
def backdrop(name, dim=.62):
    k = (name, dim)
    if k not in _BG:
        p = photo(name); s = max(W / p.width, H / p.height); p = p.resize((int(p.width * s) + 1, int(p.height * s) + 1), Image.BILINEAR).filter(ImageFilter.GaussianBlur(26))
        l = (p.width - W) // 2; t = (p.height - H) // 2; p = p.crop((l, t, l + W, t + H)); _BG[k] = Image.blend(p, Image.new("RGB", (W, H), DK), dim).convert("RGBA")
    return _BG[k].copy()
def plain(top=(10, 14, 28), bot=(2, 3, 8)):
    a = np.zeros((H, W, 3), np.uint8)
    for c in range(3): a[:, :, c] = np.linspace(top[c], bot[c], H)[:, None]
    return Image.fromarray(a).convert("RGBA")
def card(im, name, box, t, D, zoom=.05, r=26, crop=None, rot=0, tag=None, alpha=1.0):
    x, y, w, h = box; p = photo(name); z = 1 + zoom * t / D; s = max(w / p.width, h / p.height) * z
    q = p.resize((max(w, int(p.width * s)), max(h, int(p.height * s))), Image.BILINEAR)
    cx, cy = crop if crop else (.5, .5); l = int((q.width - w) * cx); tp = int((q.height - h) * cy); q = q.crop((l, tp, l + w, tp + h)).convert("RGBA")
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w, h), r, fill=int(255 * alpha)); q.putalpha(m)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((x, y + 16, x + w, y + h + 16), r, fill=(0, 0, 0, int(150 * alpha))); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(22)))
    if rot: q = q.rotate(rot, expand=True, resample=Image.BICUBIC); im.alpha_composite(q, (x - (q.width - w) // 2, y - (q.height - h) // 2))
    else: im.alpha_composite(q, (x, y))
    if tag: d = ImageDraw.Draw(im); tw = d.textlength(tag, font=MB(24)) + 34; d.rounded_rectangle((x + 20, y + 20, x + 20 + tw, y + 66), 8, fill=RD + (int(255 * alpha),)); d.text((x + 37, y + 52), tag, font=MB(24), fill=WH, anchor="ls")
def txt(im, xy, s, font, fill, a=1.0, anchor="la", dy=0):
    if a <= 0: return
    o = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(o); room = (W - 60 - xy[0]) if anchor[0] == "l" else (W - 120)
    if anchor[0] == "m": room = W - 100
    wd = d.textlength(s, font=font)
    if wd > room and room > 100: font = ImageFont.truetype(font.path, max(14, int(font.size * room / wd)))
    d.text((xy[0], xy[1] + dy), s, font=font, fill=fill + (int(255 * min(1, a)),), anchor=anchor); im.alpha_composite(o)
def rect(im, xy, fill, a=1.0, r=0, outline=None, wd=2):
    o = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(o).rounded_rectangle(xy, r, fill=fill + (int(fill_a(a)),) if fill else None, outline=(outline + (int(255 * a),)) if outline else None, width=wd); im.alpha_composite(o)
def fill_a(a): return 255 * a
def grad(im, y0, y1, a1=235, col=DK):
    o = Image.new("RGBA", (W, y1 - y0), (0, 0, 0, 0)); d = ImageDraw.Draw(o)
    for yy in range(0, y1 - y0, 4): d.rectangle((0, yy, W, yy + 4), fill=col + (int(a1 * yy / (y1 - y0)),))
    im.alpha_composite(o, (0, y0))
def wrap(d, s, f, w):
    out, cur = [], ""
    for x in s.split():
        z = (cur + " " + x).strip()
        if d.textlength(z, font=f) > w and cur: out.append(cur); cur = x
        else: cur = z
    return out + [cur]
def paras(im, x, y, s, font, fill, a, w=940, lh=46, anchor="la"):
    d = ImageDraw.Draw(im)
    for i, ln in enumerate(wrap(d, s, font, w)): txt(im, (x, y + i * lh), ln, font, fill, a, anchor)
def bar(im, x, y, w, frac, col, label, val, t0, t, hh=64):
    p = seg(t, t0, t0 + 1.0); txt(im, (x, y - 8), label, MB(24), MU, p)
    rect(im, (x, y + 20, x + w, y + 20 + hh), (30, 36, 56), p, 10); rect(im, (x, y + 20, x + max(14, w * frac * p), y + 20 + hh), col, p, 10); txt(im, (x + w * frac * p + 16, y + 20 + hh * .86), val, BS(78), col, p, "ls")
# ------------------------------------------------------------------ scenes: (seconds, function(t, D) -> RGBA)
def s_cold(t, D):
    im = backdrop("nz_day1_latham_bowled.jpg"); card(im, "nz_day1_latham_bowled.jpg", (60, 330, 960, 640), t, D, tag="BOWLED · 0.3 OV", crop=(.5, .5))
    txt(im, (70, 1130), "OVER ONE · WELLINGTON · 19 NOV 2026", MB(26), AM, seg(t, .2, .8)); txt(im, (70, 1180), "HE LEFT IT.", BS(190), WH, seg(t, .5, 1.1), dy=(1 - seg(t, .5, 1.1)) * 40)
    txt(im, (70, 1360), "IT CAME BACK.", BS(190), AM, seg(t, 1.6, 2.2), dy=(1 - seg(t, 1.6, 2.2)) * 40); txt(im, (70, 1580), "Latham b Bumrah, 2/1.", IB(40), WH, seg(t, 4.0, 4.6))
    paras(im, 70, 1650, "How does a man with the 'wrong' action become the best Test bowler by average?", IM(36), MU, seg(t, 6.5, 7.2), 940, 48); return im
def s_wrong(t, D):
    im = backdrop("bumrah_load_brisbane.jpg"); card(im, "bumrah_load_brisbane.jpg", (40, 330, 1000, 600), t, D, crop=(.45, .4))
    txt(im, (70, 1000), "THE WRONG ACTION.", BS(150), WH, seg(t, .4, 1.0)); txt(im, (70, 1140), "THE BEST AVERAGE.", BS(150), AM, seg(t, 1.2, 1.8))
    for i, s_ in enumerate(("A SHORT, STUTTERING RUN-UP", "AN ELBOW THAT BENDS THE 'WRONG' WAY", "A BACK THAT HAS FRACTURED")): a = seg(t, 3.0 + i * 1.2, 3.6 + i * 1.2); rect(im, (70, 1350 + i * 110, 1010, 1440 + i * 110), (10, 14, 26), a * .85, 16, AM, 2); txt(im, (100, 1410 + i * 110), s_, MB(30), WH, a)
    return im
def s_numbers(t, D):
    im = plain(); c = Image.open(CUT + "nz_day1_bumrah_appeal_crop.png").convert("RGBA"); k = 640 / c.height; c = c.resize((int(c.width * k), 640), Image.LANCZOS); a = seg(t, .2, 1.0)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(glow).ellipse((330, 1180, 1050, 1900), fill=(255, 200, 80, 60)); im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(70))); im.alpha_composite(Image.blend(Image.new("RGBA", c.size, (0, 0, 0, 0)), c, a), (560, 1230))
    wk = int(234 * seg(t, .3, 2.2)); txt(im, (70, 140), "TEST CAREER · 52 MATCHES", MB(26), AM, seg(t, 0, .5)); txt(im, (70, 190), f"{wk}", BS(330), WH); txt(im, (70, 500), "WICKETS", BS(100), WH, seg(t, .5, 1.0))
    av = 19.79 * seg(t, 1.2, 3.2); txt(im, (70, 610), f"{av:.2f}", BS(330), AM, seg(t, 1.0, 1.5)); txt(im, (70, 920), "RUNS PER WICKET", BS(100), AM, seg(t, 1.6, 2.1))
    bar(im, 70, 1070, 700, 19.79 / 30, AM, "BUMRAH", "19.8", 4.0, t); bar(im, 70, 1230, 700, 26.1 / 30, (90, 190, 255), "47 OTHER QUICKS SINCE 2018", "26.1", 5.0, t)
    txt(im, (70, 1450), "THE FIRST BOWLER TO 200 TEST WICKETS", IB(32), WH, seg(t, 7, 7.6)); txt(im, (70, 1495), "AT AN AVERAGE UNDER 20", IB(32), WH, seg(t, 7.4, 8.0)); txt(im, (70, 1560), "TESTS SINCE 2018 · IN OUR ARCHIVE", MO(22), MU, seg(t, 8, 8.6)); return im
def s_frames(t, D):
    im = plain(); txt(im, (70, 140), "THE ACTION", MB(26), AM, seg(t, 0, .5)); txt(im, (70, 190), "ONE DELIVERY.", BS(150), WH, seg(t, .2, .9)); txt(im, (70, 330), "FOUR FRAMES.", BS(150), AM, seg(t, .6, 1.3))
    items = (("bumrah_load_brisbane.jpg", "1 · LOAD", (.45, .4)), ("bumrah_side_jump_clean.jpg", "2 · LEAP", (.3, .3)), ("bumrah_side_jump_leeds.jpg", "3 · BOUND", (.3, .3)), ("bumrah_high_arm_closeup.jpg", "4 · RELEASE", (.85, .3)))
    for i, (nm, lab, cr) in enumerate(items):
        a = seg(t, 1.5 + i * 2.2, 2.1 + i * 2.2); x = 50 + (i % 2) * 500; y = 560 + (i // 2) * 470; card(im, nm, (x, y, 480, 400), t, D, zoom=.03, crop=cr, alpha=a); txt(im, (x + 14, y + 440), lab, MB(26), AM, a)
    paras(im, 70, 1560, "A short run-up, a leap, a bound, and a release from a hyperextended arm.", IB(38), WH, seg(t, 9.5, 10.2), 940, 52); return im
def s_callouts(t, D):
    im = backdrop("bumrah_high_arm_closeup.jpg"); card(im, "bumrah_high_arm_closeup.jpg", (40, 300, 1000, 640), t, D, crop=(.8, .3))
    for i, (x, y, w, s_, s2) in enumerate(((60, 980, 940, "ELBOW HYPEREXTENDS", "The arm bends the other way. ICC allows 15° of straightening."), (60, 1170, 940, "RELEASE ~HALF A METRE CLOSER", "Less time for the batter. About 12 ms at 140 km/h (our arithmetic)."), (60, 1360, 940, "BACKSPIN FROM THE WRIST", "About 5 cm more bounce off a good length."))):
        a = seg(t, 1.5 + i * 3.0, 2.2 + i * 3.0); rect(im, (x, y, x + w, y + 160), (10, 14, 26), a * .9, 18, AM, 3); txt(im, (x + 30, y + 22), s_, BS(56), AM, a); paras(im, x + 30, y + 90, s2, IM(26), WH, a, w - 60, 34)
    return im
def s_release(t, D):
    im = plain(); txt(im, (70, 140), "WHY HE IS HARD TO READ", MB(26), AM, seg(t, 0, .5)); txt(im, (70, 190), "THE SAME RELEASE", BS(140), WH, seg(t, .2, .9)); txt(im, (70, 320), "FOR EVERY LENGTH.", BS(140), AM, seg(t, .6, 1.3))
    gy = 1500; rel = (150, 800); d = ImageDraw.Draw(im); rect(im, (70, gy, 1010, gy + 6), (120, 160, 220), 1.0)
    for k in range(0, 9): x = 960 - k * 100; d.line((x, gy, x, gy + 18), fill=(120, 160, 220, 255), width=2); txt(im, (x, gy + 52), f"{k}", MO(22), MU, 1, "ms")
    rect(im, (960, gy - 90, 972, gy), WH, 1.0)
    p = seg(t, 1.5, 6.0)
    for L in (2, 5, 8):
        tx = 960 - L * 100; pts = [(rel[0] + (tx - rel[0]) * u, rel[1] + (gy - rel[1]) * u) for u in np.linspace(0, p, 40)]; d.line(pts, fill=(90, 190, 255, 255), width=4)
    d.ellipse((rel[0] - 18, rel[1] - 18, rel[0] + 18, rel[1] + 18), fill=AM + (255,)); txt(im, (rel[0] - 40, rel[1] - 60), "RELEASE · ~1.96 M", MB(26), AM, seg(t, 1.0, 1.6))
    paras(im, 70, 1700, "Lengths 2, 5 and 8 metres from the stumps: the ball leaves the hand from the same height.", IM(32), WH, seg(t, 6.5, 7.2), 940, 44); return im
def s_stumps(t, D):
    im = backdrop("bumrah_bowls_brook_lords.jpg"); card(im, "bumrah_bowls_brook_lords.jpg", (160, 300, 760, 560), t, D, crop=(.5, .55), tag="BOWLED")
    v = 52 * seg(t, .8, 2.6); txt(im, (70, 920), f"{int(v)}%", BS(420), AM, seg(t, .5, 1.0)); txt(im, (70, 1320), "OF HIS TEST WICKETS", BS(90), WH, seg(t, 1.6, 2.2)); txt(im, (70, 1410), "ARE BOWLED OR LBW", BS(90), WH, seg(t, 2.0, 2.6))
    txt(im, (70, 1550), "33% for the other 47 pace bowlers since 2018.", IB(38), MU, seg(t, 5, 5.6)); txt(im, (70, 1610), "HE HITS THE STUMPS.", BS(80), AM, seg(t, 7, 7.6)); txt(im, (70, 1710), "TESTS SINCE 2018 · IN OUR ARCHIVE", MO(22), MU, seg(t, 8, 8.6)); return im
def s_oldball(t, D):
    im = backdrop("bumrah_side_jump_leeds.jpg"); card(im, "bumrah_side_jump_leeds.jpg", (40, 300, 1000, 560), t, D, crop=(.35, .3)); txt(im, (70, 930), "BETTER WITH", BS(130), WH, seg(t, .3, .9)); txt(im, (70, 1050), "THE OLD BALL.", BS(130), AM, seg(t, .8, 1.4))
    bar(im, 70, 1230, 900, 23.9 / 30, (90, 190, 255), "NEW BALL · FIRST 20 OVERS", "23.9", 2.4, t, 70); bar(im, 70, 1390, 900, 18.2 / 30, AM, "OLD BALL · AFTER OVER 20", "18.2", 3.4, t, 70)
    paras(im, 70, 1590, "And on any pitch: about 70-75% of the match average, seaming or flat.", IB(34), WH, seg(t, 6.5, 7.2), 940, 46); txt(im, (70, 1750), "RUNS PER WICKET · TESTS SINCE 2018 · IN OUR ARCHIVE", MO(20), MU, seg(t, 7.5, 8.1)); return im
def s_t20(t, D):
    im = plain((12, 14, 30), (2, 3, 8)); txt(im, (70, 140), "THE SHORT FORMAT", MB(26), AM, seg(t, 0, .5)); txt(im, (70, 190), "THE YORKER", BS(150), WH, seg(t, .2, .9)); txt(im, (70, 330), "NOBODY HITS.", BS(150), AM, seg(t, .6, 1.3))
    bar(im, 70, 560, 900, 7.87 / 11, AM, "IPL DEATH OVERS · BUMRAH", "7.87", 1.5, t, 60); bar(im, 70, 700, 900, 9.6 / 11, (90, 190, 255), "THE LEAGUE, SAME SEASONS", "9.60", 2.3, t, 60)
    bar(im, 70, 880, 900, 6.35 / 11, AM, "VS LEFT-HANDERS · BUMRAH", "6.35", 3.4, t, 60); bar(im, 70, 1020, 900, 8.31 / 11, (90, 190, 255), "THE LEAGUE", "8.31", 4.2, t, 60)
    a = seg(t, 6, 6.7); rect(im, (70, 1230, 1010, 1420), (14, 20, 40), a, 18, AM, 3); txt(im, (100, 1290), "T20 WORLD CUP 2024", MB(26), AM, a); txt(im, (100, 1400), "15 WKTS AT 8.27", BS(100), WH, a, "ls")
    a = seg(t, 8, 8.7); rect(im, (70, 1450, 1010, 1640), (14, 20, 40), a, 18, AM, 3); txt(im, (100, 1510), "T20 WORLD CUP 2026 FINAL", MB(26), AM, a); txt(im, (100, 1620), "4/15 · PLAYER OF THE MATCH", BS(80), WH, a, "ls"); txt(im, (70, 1780), "IPL 2013-2026 · IN OUR ARCHIVE", MO(22), MU, seg(t, 9, 9.6)); return im
def s_cost(t, D):
    im = plain((20, 8, 12), (3, 2, 4)); txt(im, (70, 140), "THE COST", MB(26), AM, seg(t, 0, .5)); txt(im, (70, 190), "THE BACK.", BS(240), WH, seg(t, .2, .9))
    ev = (("2019", "Lower-back stress fracture. About four months out."), ("2022", "Back spasms, then a stress fracture: out of the T20 World Cup."), ("MARCH 2023", "Back surgery."), ("JANUARY 2025", "Back spasm in Sydney: no bowling in the second innings."), ("2025", "England: three Tests of five."))
    d = ImageDraw.Draw(im); d.line((100, 560, 100, 560 + 5 * 160 - 60), fill=(120, 60, 70, 255), width=4)
    for i, (y_, s_) in enumerate(ev):
        a = seg(t, 1.5 + i * 1.6, 2.1 + i * 1.6); yy = 560 + i * 160; d.ellipse((86, yy - 14, 114, yy + 14), fill=(RD if i < 4 else AM) + (int(255 * a),)); txt(im, (150, yy + 14), y_, BS(80), WH, a, "ls"); paras(im, 150, yy + 22, s_, IM(28), MU, a, 860, 36)
    a = seg(t, 10.5, 11.2); txt(im, (70, 1480), "52 OF INDIA'S 88 TESTS", BS(100), AM, a); txt(im, (70, 1580), "SINCE HIS DEBUT.", BS(100), WH, a); paras(im, 70, 1700, "Action or workload? Both views exist. Nobody outside has the scans.", IM(30), MU, seg(t, 12, 12.7), 940, 40); return im
def s_managed(t, D):
    im = plain(); txt(im, (70, 140), "HOW HE IS MANAGED", MB(26), AM, seg(t, 0, .5)); txt(im, (70, 190), "INDIA WIN MORE", BS(140), WH, seg(t, .2, .9)); txt(im, (70, 320), "WITHOUT HIM.", BS(140), AM, seg(t, .6, 1.3))
    w1 = round(42 * seg(t, 1.5, 3.0)); w2 = round(67 * seg(t, 2.5, 4.0)); txt(im, (70, 560), f"{w1}%", BS(360), AM, seg(t, 1.4, 2)); txt(im, (700, 640), "OF TESTS WON", IB(36), WH, seg(t, 2, 2.6)); txt(im, (700, 690), "WITH HIM", BS(70), AM, seg(t, 2, 2.6))
    txt(im, (70, 960), f"{w2}%", BS(360), (90, 190, 255), seg(t, 2.5, 3.1)); txt(im, (700, 1040), "OF TESTS WON", IB(36), WH, seg(t, 3.2, 3.8)); txt(im, (700, 1090), "WITHOUT HIM", BS(70), (90, 190, 255), seg(t, 3.2, 3.8))
    paras(im, 70, 1400, "But 69% of his Tests were away, against tougher sides. Count only those, and the gap flips.", IB(38), WH, seg(t, 5.5, 6.2), 940, 52); txt(im, (70, 1640), "INDIA'S TESTS SINCE JANUARY 2018 · IN OUR ARCHIVE", MO(22), MU, seg(t, 8, 8.6)); return im
def s_verdict(t, D):
    im = backdrop("nz_day1_bumrah_appeal.jpg", .7); c = Image.open(CUT + "nz_day1_bumrah_appeal_crop.png").convert("RGBA"); k = 760 / c.height; c = c.resize((int(c.width * k), 760), Image.LANCZOS); im.alpha_composite(c, (W // 2 - c.width // 2, 300))
    txt(im, (70, 1130), "UNPLAYABLE", BS(230), WH, seg(t, .4, 1.0)); txt(im, (70, 1340), "WHEN FIT.", BS(230), AM, seg(t, 1.4, 2.0)); txt(im, (70, 1600), "The price is the body that holds it together.", IM(36), MU, seg(t, 4, 4.7)); return im
def s_poll(t, D):
    im = plain(); txt(im, (70, 140), "YOUR CALL · COMMENT 1, 2 OR 3", MB(26), AM, seg(t, 0, .5)); txt(im, (70, 190), "BEST FAST", BS(170), WH, seg(t, .2, .9)); txt(im, (70, 350), "BOWLER EVER?", BS(170), AM, seg(t, .6, 1.3))
    for i, (n, s_, sub) in enumerate((("1", "YES", "The numbers say it"), ("2", "TOP THREE", "An argument, not an answer"), ("3", "NOT YET", "The workload keeps it unproven"))):
        a = seg(t, 1.5 + i * .9, 2.1 + i * .9); y = 640 + i * 300; rect(im, (70, y, 1010, y + 260), (12, 18, 36), a, 22, AM if i == 0 else (90, 190, 255), 4); txt(im, (110, y + 200), n, BS(200), AM, a, "ls"); txt(im, (290, y + 150), s_, BS(130), WH, a, "ls"); txt(im, (290, y + 215), sub, IM(30), MU, a, "ls")
    txt(im, (70, 1620), "Tell us the spell that settled it.", IB(42), WH, seg(t, 6, 6.7)); return im
def s_end(t, D):
    im = plain((6, 10, 22), (2, 3, 8)); a = seg(t, 0, .6); yt = Image.open(f"{R}/brand/youtube_logo_white.png").convert("RGBA") if os.path.exists(f"{R}/brand/youtube_logo_white.png") else None
    txt(im, (W // 2, 560), "FULL BREAKDOWN", BS(170), WH, a, "mm"); txt(im, (W // 2, 720), "ON YOUTUBE", BS(170), AM, a, "mm")
    if yt: k = 300 / yt.width; yt = yt.resize((300, int(yt.height * k)), Image.LANCZOS); im.alpha_composite(yt, (W // 2 - 150, 860))
    txt(im, (W // 2, 1160), "THE THIRD MAN", BS(120), WH, seg(t, 1, 1.6), "mm"); txt(im, (W // 2, 1280), "@thethirdman.angle", IB(48), AM, seg(t, 1.6, 2.2), "mm"); txt(im, (W // 2, 1420), "LINK IN BIO", MB(46), WH, seg(t, 2.4, 3.0), "mm"); return im
SCENES = [("cold open", 11, s_cold), ("the wrong action", 9, s_wrong), ("numbers", 12, s_numbers), ("four frames", 14, s_frames), ("callouts", 12, s_callouts), ("release", 10, s_release), ("stumps", 11, s_stumps), ("old ball", 10, s_oldball), ("short format", 11, s_t20),
          ("the back", 15, s_cost), ("managed", 10, s_managed), ("verdict", 7, s_verdict), ("poll", 9, s_poll), ("end card", 5, s_end)]
if PREVIEW: SCENES = [(n, 2.5, f) for n, _, f in SCENES]
def main():
    od = f"{R}/deliver/bumrah_unplayable"; os.makedirs(od, exist_ok=True); out = f"{od}/Bumrah_Unplayable_Short_9x16_preview_silent{'_quick' if PREVIEW else ''}.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    prev = None; total = 0; stills = []
    for nm, D, fn in SCENES:
        print(f"scene {nm} ({D}s)", flush=True); n = int(D * FPS)
        for k in range(n):
            t = k / FPS; im = fn(t, D).convert("RGB")
            if t < .35 and prev is not None: im = Image.blend(prev, im, ease(t / .35))
            if k == int(n * .8): stills.append(im.copy())
            ff.stdin.write(np.asarray(im, np.uint8).tobytes()); total += 1; last = im
        prev = last
    ff.stdin.close(); ff.wait(); print("frames", total, "seconds", round(total / FPS, 1), "->", out)
    sh = Image.new("RGB", (7 * 270 + 8 * 8, 2 * 480 + 24), (255, 255, 255))
    for i, s_ in enumerate(stills): sh.paste(s_.resize((270, 480)), (8 + (i % 7) * 278, 8 + (i // 7) * 488))
    sh.save(f"{R}/out/bumrah_preview_stills.jpg", quality=85)
if __name__ == "__main__": main()
