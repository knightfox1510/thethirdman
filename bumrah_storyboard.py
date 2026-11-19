"""Storyboard mock-ups for the dedicated Bumrah video ('Why Jasprit Bumrah is unplayable'): a new 'blueprint' look (deep navy, cyan line-art, amber highlights).
Pillow only; engine scenes follow after approval.   python3 bumrah_storyboard.py -> out/bumrah_storyboard/*.png and two contact sheets."""
import os, json, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
R = os.path.dirname(os.path.abspath(__file__)); FD = f"{R}/fonts/"; IN = f"{R}/data/licensed/in/"; CUT = f"{R}/data/licensed/cut/"; O = f"{R}/out/bumrah_storyboard"; os.makedirs(O, exist_ok=True)
BG = (12, 22, 42); GRID = (22, 38, 68); CY = (64, 210, 240); AM = (255, 176, 32); RD = (238, 74, 74); WH = (240, 244, 250); MU = (128, 150, 184); PANEL = (20, 34, 62)
def F(n, z): return ImageFont.truetype(FD + n, z)
T = lambda z: F("TekoBold.ttf", z); IB = lambda z: F("Inter-Bold.otf", z); IM = lambda z: F("Inter-Medium.otf", z); MO = lambda z: F("PlexMono.ttf", z); MB = lambda z: F("PlexMonoSB.ttf", z)
F0 = json.load(open(f"{R}/data/provenance/bumrah_tests_figures.json")); F1 = json.load(open(f"{R}/data/provenance/bumrah_context_figures.json"))
def canvas(w, h):
    im = Image.new("RGB", (w, h), BG); d = ImageDraw.Draw(im)
    for x in range(0, w, 60): d.line((x, 0, x, h), fill=GRID)
    for y in range(0, h, 60): d.line((0, y, w, y), fill=GRID)
    return im.convert("RGBA")
def chrome(d, w, num, label):
    d.text((60, 56), f"{num:02d} · {label}", font=MB(24), fill=CY, anchor="ls"); d.text((w - 60, 56), "THE THIRD MAN · BUMRAH", font=MB(22), fill=MU, anchor="rs")
    d.line((60, 72, w - 60, 72), fill=CY, width=2)
def box(d, xy, fill=PANEL, outline=CY, r=14, wd=2): d.rounded_rectangle(xy, r, fill=fill, outline=outline, width=wd)
def callout(d, p_from, p_to, text, w=360, size=24, color=CY, side="r"):
    d.line((p_from, p_to), fill=color, width=3); d.ellipse((p_from[0] - 7, p_from[1] - 7, p_from[0] + 7, p_from[1] + 7), fill=color)
    x, y = p_to; x0 = x if side == "r" else x - w
    d.rounded_rectangle((x0, y - 34, x0 + w, y + 40), 10, fill=PANEL, outline=color, width=2)
    lines = []; cur = ""
    for wd_ in text.split():
        t = (cur + " " + wd_).strip()
        if d.textlength(t, font=IM(size)) > w - 28: lines.append(cur); cur = wd_
        else: cur = t
    lines.append(cur)
    for i, ln in enumerate(lines[:3]): d.text((x0 + 14, y - 10 + i * (size + 4)), ln, font=IM(size), fill=WH)
def photo(im, path, xy, size, r=18, rot=0, tag=None, dim=0):
    p = Image.open(path).convert("RGB"); k = max(size[0] / p.width, size[1] / p.height); p = p.resize((int(p.width * k) + 1, int(p.height * k) + 1), Image.LANCZOS)
    l = (p.width - size[0]) // 2; t = (p.height - size[1]) // 2; p = p.crop((l, t, l + size[0], t + size[1]))
    if dim: p = Image.blend(p, Image.new("RGB", p.size, BG), dim)
    m = Image.new("L", size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0) + size, r, fill=255); q = p.convert("RGBA"); q.putalpha(m)
    if rot: q = q.rotate(rot, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((xy[0], xy[1] + 14, xy[0] + size[0], xy[1] + size[1] + 14), r, fill=(0, 0, 0, 110)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(20))); im.alpha_composite(q, xy)
    if tag: d = ImageDraw.Draw(im); wd = d.textlength(tag, font=MB(22)) + 30; d.rounded_rectangle((xy[0] + 18, xy[1] + 18, xy[0] + 18 + wd, xy[1] + 62), 8, fill=RD); d.text((xy[0] + 33, xy[1] + 49), tag, font=MB(22), fill=WH, anchor="ls")
def cut(path): im = Image.open(CUT + path).convert("RGBA"); return im.crop(im.getbbox())
def stamp(im, c, cx, bottom, hh):
    k = hh / c.height; c2 = c.resize((int(c.width * k), hh), Image.LANCZOS); im.alpha_composite(c2, (int(cx - c2.width / 2), int(bottom - hh)))
def need(d, xy, label, sub):
    x0, y0, x1, y1 = xy; d.rounded_rectangle(xy, 16, outline=AM, width=3)
    for i in range(0, int(x1 - x0), 26): d.line((x0 + i, y0, min(x0 + i + 12, x1), y0), fill=AM, width=3); d.line((x0 + i, y1, min(x0 + i + 12, x1), y1), fill=AM, width=3)
    d.text(((x0 + x1) / 2, (y0 + y1) / 2 - 12), label, font=MB(26), fill=AM, anchor="mm"); d.text(((x0 + x1) / 2, (y0 + y1) / 2 + 24), sub, font=MO(20), fill=MU, anchor="mm")
def wrap(d, text, font, width):
    out, cur = [], ""
    for w_ in text.split():
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=font) > width and cur: out.append(cur); cur = w_
        else: cur = t
    return out + [cur]
def overlay(im, box_, rgba):
    o = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(o).rectangle(box_, fill=rgba); im.alpha_composite(o)
def bars(d, x, y, w, rows, mx, hh=46, gap=70, unit=""):
    for i, (lab, v, col, txt) in enumerate(rows):
        yy = y + i * gap; d.text((x, yy), lab, font=MB(22), fill=MU); d.rounded_rectangle((x, yy + 20, x + w, yy + 20 + hh), 8, fill=(26, 44, 78)); d.rounded_rectangle((x, yy + 20, x + max(12, w * v / mx), yy + 20 + hh), 8, fill=col); d.text((x + w * v / mx + 16, yy + 20 + hh * .86), txt, font=T(56), fill=col, anchor="ls")

def L_cold():
    im = canvas(1920, 1080); photo(im, IN + "nz_day1_latham_bowled.jpg", (0, 0), (1920, 1080), r=0, dim=.35)
    for y0 in range(300, 1080, 6): overlay(im, (0, y0, 1920, y0 + 6), (12, 22, 42, int(min(1, (y0 - 300) / 700) * 235)))
    d = ImageDraw.Draw(im); d.text((100, 560), "OVER ONE · WELLINGTON · 19 NOV 2026", font=MB(26), fill=CY); d.text((100, 750), "HE LEFT IT.", font=T(170), fill=WH); d.text((100, 910), "IT CAME BACK.", font=T(170), fill=AM)
    return im.convert("RGB")
def L_numbers():
    im = canvas(1920, 1080); d = ImageDraw.Draw(im); chrome(d, 1920, 2, "THE NUMBERS")
    d.text((90, 120), "234 WICKETS.", font=T(130), fill=WH); d.text((90, 240), "AVERAGE 19.79.", font=T(130), fill=AM); d.text((92, 390), "Test career to 22 Nov 2025 · our archive · first bowler to 200 at under 20", font=MO(24), fill=MU)
    bars(d, 90, 440, 900, [("BUMRAH · RUNS PER WICKET", 19.79, AM, "19.8"), ("47 OTHER PACE BOWLERS SINCE 2018 (50+ WKTS)", 26.1, CY, "26.1")], 30, gap=110)
    bars(d, 90, 710, 900, [("BUMRAH · BALLS PER WICKET", 42.9, AM, "42.9"), ("THE 47 · BALLS PER WICKET", 49.7, CY, "49.7")], 60, gap=110)
    stamp(im, cut("nz_day1_bumrah_appeal.png"), 1500, 1010, 800); return im.convert("RGB")
def L_action():
    im = canvas(1920, 1080); d = ImageDraw.Draw(im); chrome(d, 1920, 3, "THE ACTION")
    d.text((90, 190), "A bowler built", font=T(120), fill=WH); d.text((90, 290), "the wrong way.", font=T(120), fill=AM)
    stamp(im, cut("bumrah_wellington_2020.png") if False else Image.open(CUT + "bumrah_wellington_2020_crop.png"), 1010, 1030, 780)
    d = ImageDraw.Draw(im)
    callout(d, (1130, 330), (1400, 250), "SHORT, STUTTERING RUN-UP. Holding: a long run-up would blunt him", w=430)
    callout(d, (1010, 470), (1400, 420), "ELBOW HYPEREXTENDS: the arm bends the 'wrong' way (ICC allows 15° of straightening)", w=430)
    callout(d, (1170, 600), (1400, 600), "RELEASE FAR CLOSER TO THE BATTER: about 48 cm vs Kemar Roach (cricket.com analysis)", w=430)
    callout(d, (930, 800), (560, 760), "WRIST AND FOREARM ADD BACKSPIN: about 5 cm more bounce off a good length", w=440, side="l")
    d.text((90, 1020), "2020 PHOTO · CALLOUTS ARE REPORTED ANALYSIS, DRAWN OVER THE IMAGE · ILLUSTRATIVE", font=MO(20), fill=MU); return im.convert("RGB")
def L_release():
    im = canvas(1920, 1080); d = ImageDraw.Draw(im); chrome(d, 1920, 4, "WHY HE IS HARD TO READ")
    d.text((90, 180), "The same release", font=T(110), fill=WH); d.text((90, 270), "for every length.", font=T(110), fill=AM)
    gy = 860; d.line((90, gy, 1830, gy), fill=CY, width=4)
    for k in range(0, 9): x = 1700 - k * 150; d.line((x, gy, x, gy + 16), fill=MU, width=2); d.text((x, gy + 46), f"{k} m", font=MO(20), fill=MU, anchor="ms")
    d.rectangle((1700, gy - 70, 1710, gy), fill=WH); rel = (430, 500); d.ellipse((rel[0] - 14, rel[1] - 14, rel[0] + 14, rel[1] + 14), fill=AM)
    for L in (1700 - 2 * 150, 1700 - 5 * 150, 1700 - 8 * 150):
        pts = [(rel[0] + (L - rel[0]) * t / 20, rel[1] + (gy - rel[1]) * (t / 20)) for t in range(21)]; d.line(pts, fill=CY, width=3)
    d.text((rel[0] - 20, rel[1] - 40), "BUMRAH: RELEASE HEIGHT ~1.96 M FOR LENGTHS 2-8 M (ESPNCRICINFO)", font=MB(22), fill=AM)
    d.text((90, 960), "A TALLER BOWLER RELEASES ABOUT 20 CM HIGHER (CRICKET.COM) · SCHEMATIC, NOT TO SCALE", font=MO(20), fill=MU)
    box(d, (1100, 130, 1830, 400)); d.text((1130, 175), "REACTION TIME (OUR ARITHMETIC)", font=MB(22), fill=CY); d.text((1130, 215), "~12 ms", font=T(110), fill=AM); d.text((1130, 350), "48 cm closer, ball at 140 km/h", font=IM(26), fill=WH)
    return im.convert("RGB")
def L_wickets():
    im = canvas(1920, 1080); d = ImageDraw.Draw(im); chrome(d, 1920, 5, "HOW THE WICKETS COME")
    d.text((90, 190), "He hits the stumps.", font=T(130), fill=WH)
    di = F0["dismissals"]; tot = sum(di.values()); parts = [("BOWLED", di["bowled"], RD), ("LBW", di["lbw"], AM), ("CAUGHT", di["caught"] + di["caught and bowled"], CY)]; x = 90
    for lab, n, col in parts:
        wd = 1100 * n / tot; d.rectangle((x, 360, x + wd, 470), fill=col); x += wd
    x = 90
    for lab, n, col in parts: d.text((x + 16, 372), f"{lab} {round(100 * n / tot)}%", font=T(60), fill=BG); x += 1100 * n / tot
    d.text((90, 640), f"{F1['bumrah_bowled_lbw_pct']}%", font=T(200), fill=AM); d.text((700, 620), "BOWLED OR LBW", font=T(80), fill=WH); d.text((700, 700), f"vs {F1['baseline_bowled_lbw_pct']}% for the other 47 pace bowlers", font=IM(32), fill=MU)
    photo(im, IN + "nz_day1_latham_bowled.jpg", (1300, 560), (520, 347), tag="BOWLED · 0.3 OV"); d.text((90, 1000), "CRICSHEET TESTS SINCE 2018 · 234 WICKETS · OUR ARCHIVE", font=MO(20), fill=MU); return im.convert("RGB")
def L_ball():
    im = canvas(1920, 1080); d = ImageDraw.Draw(im); chrome(d, 1920, 6, "THE SURPRISE")
    d.text((90, 190), "Better with the", font=T(130), fill=WH); d.text((90, 300), "OLD ball.", font=T(130), fill=AM)
    bars(d, 90, 520, 1000, [("FIRST 20 OVERS · NEW BALL · 64 WKTS", 23.9, CY, "23.9"), ("AFTER OVER 20 · OLD BALL · 170 WKTS", 18.2, AM, "18.2")], 30, hh=70, gap=130)
    d.text((90, 840), "Runs per wicket. We don't know the whole why: skid, backspin and a scuffed ball are the candidates.", font=IM(30), fill=WH); d.text((90, 900), "CRICSHEET TESTS SINCE 2018 · OUR ARCHIVE", font=MO(20), fill=MU); return im.convert("RGB")
def L_pitch():
    im = canvas(1920, 1080); d = ImageDraw.Draw(im); chrome(d, 1920, 7, "WHICH PITCH SUITS HIM")
    d.text((90, 190), "All of them.", font=T(150), fill=WH); d.text((90, 330), "A little more on green.", font=T(80), fill=AM)
    bp = F1["by_pitch_type"]; rows = []
    for k, lab in (("bowler-friendly (match avg under 28)", "SEAMING / BOWLER-FRIENDLY"), ("balanced (28-38)", "BALANCED"), ("flat (38+)", "FLAT")):
        v = bp[k]; rows.append((lab, v)); 
    y = 470
    for lab, v in rows:
        d.text((90, y), f"{lab} · {v['tests']} TESTS", font=MB(22), fill=MU); mx = 50; w_ = 900
        d.rounded_rectangle((90, y + 14, 90 + w_ * v["match_avg_all_bowlers"] / mx, y + 56), 8, fill=(40, 62, 100)); d.rounded_rectangle((90, y + 62, 90 + w_ * v["bumrah_avg"] / mx, y + 104), 8, fill=AM)
        d.text((90 + w_ * v["match_avg_all_bowlers"] / mx + 14, y + 48), f"all bowlers {v['match_avg_all_bowlers']}", font=IM(26), fill=MU); d.text((90 + w_ * v["bumrah_avg"] / mx + 14, y + 96), f"Bumrah {v['bumrah_avg']}", font=IB(30), fill=AM); y += 170
    d.text((90, 985), "ABOUT 70-75% OF THE MATCH AVERAGE ON EVERY TYPE OF PITCH · OUR ARCHIVE · PITCH TYPE = AVERAGE OF ALL BOWLERS IN THE TEST (A PROXY)", font=MO(18), fill=MU); return im.convert("RGB")
def L_where():
    im = canvas(1920, 1080); d = ImageDraw.Draw(im); chrome(d, 1920, 8, "HOME AND AWAY")
    d.text((90, 190), "Away or home,", font=T(130), fill=WH); d.text((90, 300), "unplayable.", font=T(130), fill=AM)
    v = F0["by_venue_type"]
    for i, (k, lab) in enumerate((("home", "IN INDIA"), ("SENA away", "SOUTH AFRICA · ENGLAND · NEW ZEALAND · AUSTRALIA"))):
        x = 90 + i * 880; box(d, (x, 460, x + 820, 800)); d.text((x + 30, 520), lab, font=MB(22), fill=CY); d.text((x + 30, 590), f"{v[k]['avg']}", font=T(190), fill=AM); d.text((x + 360, 600), f"{v[k]['tests']} Tests · {v[k]['wkts']} wkts", font=IM(30), fill=WH); d.text((x + 360, 650), f"strike rate {v[k]['sr']}", font=IM(30), fill=MU); d.text((x + 360, 700), "runs per wicket", font=IM(26), fill=MU)
    d.text((90, 870), "25 of his 52 Tests brought five or more wickets in the match. Border-Gavaskar 2024-25: 32 wickets at 13.06.", font=IM(34), fill=WH); d.text((90, 960), "CRICSHEET TESTS · OUR ARCHIVE · SENA FIGURES MATCH SPORTSKEEDA (159 WKTS, 34 TESTS)", font=MO(20), fill=MU); return im.convert("RGB")
def L_t20():
    im = canvas(1920, 1080); d = ImageDraw.Draw(im); chrome(d, 1920, 9, "THE SHORT FORMAT")
    d.text((90, 190), "The yorker", font=T(130), fill=WH); d.text((90, 300), "nobody can hit.", font=T(130), fill=AM)
    ip = F1["ipl_phases"]
    bars(d, 90, 500, 900, [("IPL DEATH OVERS · BUMRAH · ECONOMY", ip["death"]["econ"], AM, f"{ip['death']['econ']}"), ("LEAGUE, SAME SEASONS", ip["death"]["league_econ_same_seasons_weighted"], CY, f"{ip['death']['league_econ_same_seasons_weighted']}")], 11, hh=50, gap=100)
    lh = F1["ipl_vs_left_handers"]; bars(d, 90, 750, 900, [("IPL VS LEFT-HANDERS · BUMRAH", lh["econ"], AM, f"{lh['econ']}"), ("LEAGUE", lh["league_econ"], CY, f"{lh['league_econ']}")], 11, hh=50, gap=100)
    box(d, (1150, 500, 1830, 840)); d.text((1190, 560), "T20 WORLD CUP 2024", font=MB(24), fill=CY); d.text((1190, 600), "15 WKTS", font=T(130), fill=AM); d.text((1190, 760), "average 8.27 · Player of the Tournament", font=IM(30), fill=WH); d.text((90, 1000), "IPL 2013-2026 · OUR SPORTMONKS CACHE · T20 WORLD CUP: WISDEN", font=MO(20), fill=MU); return im.convert("RGB")
def L_cost():
    im = canvas(1920, 1080); d = ImageDraw.Draw(im); chrome(d, 1920, 10, "THE COST")
    d.text((90, 190), "The back.", font=T(150), fill=WH)
    ev = [("2019", "Lower-back stress fracture. About four months out."), ("2022", "Back spasms, then a stress fracture: out of the T20 World Cup."), ("MAR 2023", "Back surgery."), ("JAN 2025", "Back spasm in Sydney: no bowling in the second innings."), ("2025", "England: plans to play three of five Tests.")]
    x0, x1, y = 230, 1690, 480; d.line((90, y, 1830, y), fill=CY, width=4)
    for i, (yr, t) in enumerate(ev):
        x = x0 + i * (x1 - x0) / 4; d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=RD if i < 4 else AM); d.text((x, y - 40), yr, font=T(64), fill=WH, anchor="ms")
        for j, ln in enumerate(wrap(d, t, IM(24), 300)[:4]): d.text((x, y + 50 + j * 34), ln, font=IM(24), fill=WH if j == 0 else MU, anchor="ma")
    d.text((90, 860), "Pace, length and variations are not reported to have changed: his workload has.", font=IM(32), fill=AM); d.text((90, 1000), "WISDEN TIMELINE (JAN 2023) · ESPNCRICINFO · AGARKAR (MARCH 2023 SURGERY) · SYDNEY JAN 2025", font=MO(20), fill=MU); return im.convert("RGB")
def L_science():
    im = canvas(1920, 1080); d = ImageDraw.Draw(im); chrome(d, 1920, 11, "WHY THE BACK")
    d.text((90, 190), "The price of a", font=T(120), fill=WH); d.text((90, 290), "whip-like action?", font=T(120), fill=AM)
    box(d, (90, 470, 900, 940)); d.text((120, 520), "GENERAL RESEARCH ON FAST BOWLERS", font=MB(22), fill=CY)
    for i, t in enumerate(("Lumbar stress fractures: 24-55% of adult fast bowlers.", "Risk factors: a hyperextended, side-bent lower back, counter-rotation of the shoulders, heavy workloads.", "Under 3.5 days' rest: three times the injury risk (junior bowlers).")): d.text((120, 580 + i * 110), t[:58], font=IM(28), fill=WH); d.text((120, 614 + i * 110), t[58:], font=IM(28), fill=WH)
    box(d, (960, 470, 1830, 940), outline=AM); d.text((990, 520), "TWO READINGS OF BUMRAH", font=MB(22), fill=AM)
    d.text((990, 600), "'It's the action.' The whip that hides", font=IM(28), fill=WH); d.text((990, 636), "the ball also loads the spine.", font=IM(28), fill=WH)
    d.text((990, 730), "'It's the workload.' Coach Arun Singh puts", font=IM(28), fill=WH); d.text((990, 766), "his injuries down to long series, not the action.", font=IM(28), fill=WH)
    d.text((990, 860), "Nobody has the MRI: we can't diagnose, only show both.", font=IM(26), fill=MU); d.text((90, 1000), "PUBLISHED REVIEWS OF FAST-BOWLING INJURY (PMC, BJSM) · THEPRINT, 6 JAN 2025 · NOT A MEDICAL OPINION", font=MO(20), fill=MU); return im.convert("RGB")
def L_avail():
    im = canvas(1920, 1080); d = ImageDraw.Draw(im); chrome(d, 1920, 12, "HOW HE IS MANAGED")
    d.text((90, 190), "52 of 88.", font=T(160), fill=AM); d.text((740, 270), "India Tests played since his debut", font=IM(36), fill=WH)
    box(d, (90, 400, 930, 760)); d.text((120, 440), "INDIA'S RECORD (OUR ARCHIVE, TO NOV 2025)", font=MB(22), fill=CY)
    d.text((120, 600), f"{F0['india_with']['win_pct']:.0f}%", font=T(160), fill=AM); d.text((400, 560), "of Tests won", font=IM(30), fill=WH); d.text((400, 600), "WITH HIM", font=IB(36), fill=AM)
    d.text((420, 690), f"{F0['india_without']['win_pct']:.0f}% WITHOUT HIM", font=IB(36), fill=MU)
    box(d, (990, 400, 1830, 760), outline=AM); d.text((1020, 440), "WHY THAT IS MISLEADING (WISDEN, JULY 2025)", font=MB(22), fill=AM)
    for i, t in enumerate(("Most of his Tests are away: 69% of them.", "Without him India played many more home Tests.", "Count only tough away Tests and the gap flips.")): d.text((1020, 520 + i * 70), t, font=IM(28), fill=WH)
    d.text((90, 840), "Two long absences: seven Tests (2018-20) and nine Tests (Dec 2022 to Dec 2023).", font=IM(32), fill=WH); d.text((90, 1000), "CRICSHEET TESTS · WISDEN, 9 JULY 2025", font=MO(20), fill=MU); return im.convert("RGB")
def L_proscons():
    im = canvas(1920, 1080); d = ImageDraw.Draw(im); chrome(d, 1920, 13, "PROS AND CONS")
    d.text((90, 190), "The trade.", font=T(150), fill=WH)
    pro = ["Late, close release: less time to react", "Same release for every length", "Backspin: extra bounce, skid", "Hits the stumps: 52% bowled or lbw", "Yorker, new ball, old ball", "Stable head, relaxed until release"]
    con = ["Back: three stress-related lay-offs", "Cannot play every Test", "Flat pitches lift his average to 34", "Needs wicket-takers at the other end", "Short run-up: little room for error", "Depends on one body to hold it all"]
    box(d, (90, 400, 930, 960), outline=CY); box(d, (990, 400, 1830, 960), outline=RD)
    d.text((130, 440), "WHAT WORKS", font=T(56), fill=CY); d.text((1030, 440), "WHAT IT COSTS", font=T(56), fill=RD)
    for i, t in enumerate(pro): d.text((130, 520 + i * 70), "+ " + t, font=IM(28), fill=WH)
    for i, t in enumerate(con): d.text((1030, 520 + i * 70), "- " + t, font=IM(28), fill=WH)
    return im.convert("RGB")
def L_poll():
    im = canvas(1920, 1080); d = ImageDraw.Draw(im); chrome(d, 1920, 14, "YOUR CALL")
    d.text((90, 190), "Best fast bowler", font=T(130), fill=WH); d.text((90, 300), "of all time?", font=T(130), fill=AM)
    for i, (n, t, sub) in enumerate((("1", "YES", "The numbers say it"), ("2", "TOP THREE", "An argument, not an answer"), ("3", "NOT YET", "Workload keeps it unproven"))):
        x = 90 + i * 600; box(d, (x, 500, x + 560, 900), outline=AM if i == 0 else CY); d.text((x + 30, 520), n, font=T(200), fill=AM); d.text((x + 30, 740), t, font=T(90), fill=WH); d.text((x + 30, 830), sub, font=IM(26), fill=MU)
    d.text((90, 960), "Comment 1, 2 or 3, and tell us the spell that settled it for you.", font=IM(34), fill=WH); return im.convert("RGB")
def V_frames():
    out = []
    def V(): im = canvas(1080, 1920); return im, ImageDraw.Draw(im)
    im, d = V(); photo(im, IN + "nz_day1_latham_bowled.jpg", (0, 0), (1080, 1920), r=0, dim=.35)
    for y0 in range(900, 1920, 8): overlay(im, (0, y0, 1080, y0 + 8), (12, 22, 42, int(min(1, (y0 - 900) / 700) * 235)))
    d = ImageDraw.Draw(im)
    d.text((70, 1230), "OVER ONE · WELLINGTON", font=MB(26), fill=CY); d.text((70, 1290), "HE LEFT IT.", font=T(150), fill=WH); d.text((70, 1430), "IT CAME BACK.", font=T(150), fill=AM)
    for j, ln in enumerate(wrap(d, "How a man with the 'wrong' action became the best bowler by average.", IM(32), 940)): d.text((70, 1650 + j * 44), ln, font=IM(32), fill=WH)
    out.append(im.convert("RGB"))
    im, d = V(); chrome(d, 1080, 2, "THE ACTION"); d.text((60, 140), "Built the", font=T(110), fill=WH); d.text((60, 235), "wrong way.", font=T(110), fill=AM)
    stamp(im, Image.open(CUT + "bumrah_wellington_2020_crop.png"), 560, 1500, 1050); d = ImageDraw.Draw(im)
    callout(d, (640, 560), (600, 420), "SHORT, STUTTERING RUN-UP", w=380, side="r"); callout(d, (560, 720), (460, 700), "ELBOW HYPEREXTENDS", w=330); callout(d, (700, 980), (350, 1000), "RELEASE ~48 CM CLOSER", w=330, side="l"); callout(d, (520, 1200), (560, 1280), "BACKSPIN: ~5 CM EXTRA BOUNCE", w=400)
    d.text((60, 1640), "'Not a fast bowler's action. It works anyway.'", font=IM(34), fill=WH); d.text((60, 1860), "2020 PHOTO · REPORTED ANALYSIS · ILLUSTRATIVE", font=MO(20), fill=MU); out.append(im.convert("RGB"))
    im, d = V(); chrome(d, 1080, 3, "THE NUMBERS"); d.text((60, 200), "19.79", font=T(300), fill=AM); d.text((60, 480), "RUNS PER WICKET · 234 TEST WICKETS", font=MB(28), fill=WH)
    bars(d, 60, 640, 940, [("BUMRAH", 19.79, AM, "19.8"), ("47 OTHER QUICKS SINCE 2018", 26.1, CY, "26.1")], 30, hh=70, gap=140); stamp(im, cut("nz_day1_bumrah_appeal.png"), 700, 1860, 800); out.append(im.convert("RGB"))
    im, d = V(); chrome(d, 1080, 4, "HOW THE WICKETS COME"); d.text((60, 180), "He hits", font=T(150), fill=WH); d.text((60, 310), "the stumps.", font=T(150), fill=AM); d.text((60, 560), "52%", font=T(340), fill=AM); d.text((60, 860), "BOWLED OR LBW", font=T(80), fill=WH); d.text((60, 940), "vs 33% for 47 other pace bowlers", font=IM(34), fill=MU); photo(im, IN + "nz_day1_latham_bowled.jpg", (60, 1100), (960, 640), tag="BOWLED · 0.3 OV"); out.append(im.convert("RGB"))
    im, d = V(); chrome(d, 1080, 5, "OLD BALL · ANY PITCH"); d.text((60, 180), "Better with", font=T(130), fill=WH); d.text((60, 290), "the OLD ball.", font=T(130), fill=AM)
    bars(d, 60, 520, 900, [("NEW BALL · FIRST 20 OVERS", 23.9, CY, "23.9"), ("OLD BALL · AFTER OVER 20", 18.2, AM, "18.2")], 30, hh=80, gap=150); d.text((60, 860), "WHICH PITCH? ALL OF THEM.", font=T(80), fill=WH); y = 980
    for k, lab in (("bowler-friendly (match avg under 28)", "SEAMING"), ("balanced (28-38)", "BALANCED"), ("flat (38+)", "FLAT")):
        v = F1["by_pitch_type"][k]; d.text((60, y), f"{lab} · {v['tests']} TESTS", font=MB(22), fill=MU); d.rounded_rectangle((60, y + 14, 60 + 900 * v["match_avg_all_bowlers"] / 50, y + 50), 6, fill=(40, 62, 100)); d.rounded_rectangle((60, y + 56, 60 + 900 * v["bumrah_avg"] / 50, y + 92), 6, fill=AM)
        d.text((60 + 900 * v["match_avg_all_bowlers"] / 50 + 12, y + 44), f"all {v['match_avg_all_bowlers']}", font=IM(24), fill=MU); d.text((60 + 900 * v["bumrah_avg"] / 50 + 12, y + 86), f"Bumrah {v['bumrah_avg']}", font=IB(26), fill=AM); y += 150
    d.text((60, 1470), "About 70-75% of the match average on every pitch.", font=IB(34), fill=AM); out.append(im.convert("RGB"))
    im, d = V(); chrome(d, 1080, 6, "THE SHORT FORMAT"); d.text((60, 180), "The yorker", font=T(140), fill=WH); d.text((60, 300), "nobody hits.", font=T(140), fill=AM); ip = F1["ipl_phases"]
    bars(d, 60, 560, 940, [("IPL DEATH · BUMRAH", ip["death"]["econ"], AM, f"{ip['death']['econ']}"), ("LEAGUE, SAME SEASONS", ip["death"]["league_econ_same_seasons_weighted"], CY, f"{ip['death']['league_econ_same_seasons_weighted']}")], 11, hh=60, gap=120)
    box(d, (60, 900, 1020, 1240)); d.text((100, 960), "T20 WORLD CUP 2024", font=MB(26), fill=CY); d.text((100, 1100), "15 WKTS · 8.27", font=T(130), fill=AM); d.text((100, 1180), "Player of the Tournament", font=IM(32), fill=WH)
    lh = F1["ipl_vs_left_handers"]; bars(d, 60, 1330, 940, [("IPL VS LEFT-HANDERS · BUMRAH", lh["econ"], AM, f"{lh['econ']}"), ("LEAGUE", lh["league_econ"], CY, f"{lh['league_econ']}")], 11, hh=56, gap=120); out.append(im.convert("RGB"))
    im, d = V(); chrome(d, 1080, 7, "THE COST"); d.text((60, 180), "The back.", font=T(180), fill=WH)
    for i, (yr, t) in enumerate((("2019", "Stress fracture, ~4 months out"), ("2022", "Stress fracture: T20 World Cup missed"), ("MAR 2023", "Back surgery"), ("JAN 2025", "Sydney back spasm"), ("2025", "England: three of five Tests"))):
        y = 480 + i * 210; d.ellipse((70, y - 14, 98, y + 14), fill=RD); d.text((130, y + 12), yr, font=T(80), fill=WH, anchor="ls"); d.text((130, y + 60), t, font=IM(32), fill=MU)
    d.text((60, 1590), "52 of 88 India Tests played since his debut.", font=IB(40), fill=AM); d.text((60, 1660), "Action or workload? Both views, no MRI.", font=IM(32), fill=WH); out.append(im.convert("RGB"))
    im, d = V(); chrome(d, 1080, 8, "YOUR CALL"); d.text((60, 180), "Best fast", font=T(150), fill=WH); d.text((60, 310), "bowler ever?", font=T(150), fill=AM)
    for i, (n, t) in enumerate((("1", "YES"), ("2", "TOP THREE"), ("3", "NOT YET"))):
        y = 600 + i * 300; box(d, (60, y, 1020, y + 260), outline=AM if i == 0 else CY); d.text((110, y + 190), n, font=T(160), fill=AM, anchor="ls"); d.text((280, y + 180), t, font=T(110), fill=WH, anchor="ls")
    d.text((60, 1580), "Comment 1, 2 or 3 and tell us the spell that settled it.", font=IM(34), fill=WH); out.append(im.convert("RGB"))
    return out
def sheet(fr, cols, tw, th, path):
    rows = -(-len(fr) // cols); s = Image.new("RGB", (cols * (tw + 16) + 16, rows * (th + 16) + 16), (255, 255, 255))
    for i, f in enumerate(fr): s.paste(f.resize((tw, th), Image.LANCZOS), (16 + (i % cols) * (tw + 16), 16 + (i // cols) * (th + 16)))
    s.save(path, quality=88)
if __name__ == "__main__":
    L = [L_cold(), L_numbers(), L_action(), L_release(), L_wickets(), L_ball(), L_pitch(), L_where(), L_t20(), L_cost(), L_science(), L_avail(), L_proscons(), L_poll()]
    for i, f in enumerate(L, 1): f.save(f"{O}/l{i:02d}.png")
    V = V_frames()
    for i, f in enumerate(V, 1): f.save(f"{O}/v{i:02d}.png")
    sheet(L, 3, 640, 360, f"{R}/out/bumrah_storyboard_long.jpg"); sheet(V, 4, 330, 587, f"{R}/out/bumrah_storyboard_vertical.jpg"); print("ok", len(L), len(V))
