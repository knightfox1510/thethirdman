"""Storyboard mock-ups: owner-supplied photos (Latham bowled, Bumrah appeal, Bumrah in Wellington 2020) built into the Day 1 videos, lab look. Pillow only; the engine scenes follow after approval.
    python3 day1_photo_storyboard.py   -> out/nz_day1_photo_frames_vertical.jpg, out/nz_day1_photo_frames_long.jpg"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
R = os.path.dirname(os.path.abspath(__file__)); FD = f"{R}/fonts/"; IN = f"{R}/data/licensed/in/"; CUT = f"{R}/data/licensed/cut/"
INK = (20, 20, 22); RED = (214, 36, 56); MUTED = (130, 130, 128); PAPER = (246, 245, 241); LINE = (222, 220, 212)
def F(n, z): return ImageFont.truetype(FD + n, z)
IB = lambda z: F("Inter-Bold.otf", z); MONO = lambda z: F("PlexMono.ttf", z); MONOB = lambda z: F("PlexMonoSB.ttf", z)
def paper(w, h):
    im = Image.new("RGB", (w, h), PAPER); d = ImageDraw.Draw(im)
    for x in range(0, w, 54): d.line((x, 0, x, h), fill=(240, 239, 235))
    for y in range(0, h, 54): d.line((0, y, w, y), fill=(240, 239, 235))
    return im
def chrome(im, d, tag="THE REPLAY ROOM"):
    w, h = im.size; d.ellipse((w - 330, 62, w - 316, 76), fill=RED); d.text((w - 296, 82), "THE THIRD MAN", font=MONOB(26), fill=INK, anchor="ls")
def rounded(img, r):
    m = Image.new("L", img.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0) + img.size, r, fill=255); o = img.convert("RGBA"); o.putalpha(m); return o
def shadow(base, box, r, blur=26, off=14, a=70):
    s = Image.new("RGBA", base.size, (0, 0, 0, 0)); ImageDraw.Draw(s).rounded_rectangle((box[0], box[1] + off, box[2], box[3] + off), r, fill=(0, 0, 0, a)); base.alpha_composite(s.filter(ImageFilter.GaussianBlur(blur)))
def fit_text(d, t, font_fn, maxw, z0):
    z = z0
    while z > 12 and d.textlength(t, font=font_fn(z)) > maxw: z -= 2
    return font_fn(z)
def cut(name, bbox_pad=0):
    im = Image.open(CUT + name).convert("RGBA")
    return im.crop(im.getbbox())
def stamp(base, im, xy, anchor="ma"):
    x, y = xy; w, h = im.size; x0 = x - w // 2 if anchor[0] == "m" else x; base.alpha_composite(im, (int(x0), int(y)))
def tag(d, xy, t, size=30, fill=RED, txt=(255, 255, 255)):
    f = MONOB(size); w = d.textlength(t, font=f) + 36; x, y = xy; d.rounded_rectangle((x, y, x + w, y + size + 24), 8, fill=fill); d.text((x + 18, y + size + 8), t, font=f, fill=txt, anchor="ls"); return w
LATHAM = Image.open(IN + "nz_day1_latham_bowled.jpg").convert("RGB"); BAPPEAL = cut("nz_day1_bumrah_appeal.png"); B2020 = Image.open(CUT + "bumrah_wellington_2020.png").convert("RGBA")
# remove the stump fragment left in the 2020 cut-out (a vertical column to the right of the leg)
a = B2020.split()[3]; ImageDraw.Draw(a).rectangle((272, 1135, 338, 1585), fill=0); B2020.putalpha(a); B2020 = B2020.crop(B2020.getbbox())

def v_cold():
    w, h = 1080, 1920; im = paper(w, h).convert("RGBA"); d = ImageDraw.Draw(im); chrome(im, d)
    d.text((80, 260), "BUMRAH'S LAST BALL OF THE DAY · OVER 81", font=MONOB(26), fill=RED)
    d.text((80, 360), "ONE INSWINGER.", font=IB(112), fill=INK); d.text((80, 480), "ONE TOE.", font=IB(150), fill=RED)
    d.ellipse((90, 760, 990, 1660), fill=(255, 235, 235)); d.ellipse((90, 760, 990, 1660), outline=RED, width=8)
    b = BAPPEAL.copy(); b = b.resize((int(b.width * 1.55), int(b.height * 1.55)), Image.LANCZOS); stamp(im, b, (w // 2, 850))
    d.text((80, 1740), "Nicholls jammed his bat down in time.", font=IB(44), fill=INK); d.text((80, 1802), "Earlier that day: 70 for 5.", font=MONO(32), fill=MUTED)
    return im.convert("RGB")
def v_over1():
    w, h = 1080, 1920; im = paper(w, h).convert("RGBA"); d = ImageDraw.Draw(im); chrome(im, d)
    d.text((80, 250), "OVER ONE", font=MONOB(28), fill=RED); d.text((80, 330), "Bowled.", font=IB(130), fill=INK)
    ph = LATHAM.resize((920, int(920 * 533 / 800)), Image.LANCZOS); box = (80, 540, 1000, 540 + ph.height); shadow(im, box, 22)
    card = rounded(ph, 22).rotate(-1.6, expand=True, resample=Image.BICUBIC); im.alpha_composite(card, (int(w / 2 - card.width / 2), 520)); d = ImageDraw.Draw(im)
    tag(d, (120, 520 + 10), "BOWLED · 0.3 OV")
    d.text((80, 1310), "LATHAM b BUMRAH", font=IB(78), fill=INK)
    d.text((80, 1420), "FULL · 4TH-STUMP LINE · SEAM UPRIGHT", font=MONOB(30), fill=RED)
    d.text((80, 1480), "Latham left it, expecting it to go away. It came back.", font=IB(36), fill=INK)
    d.rounded_rectangle((80, 1570, 330, 1690), 18, fill=(255, 255, 255), outline=INK, width=4); d.text((205, 1650), "2/1", font=IB(78), fill=INK, anchor="ms")
    d.text((360, 1630), "NEW ZEALAND", font=MONOB(26), fill=MUTED)
    return im.convert("RGB")
def v_then_now():
    w, h = 1080, 1920; im = paper(w, h).convert("RGBA"); d = ImageDraw.Draw(im); chrome(im, d)
    d.text((80, 250), "SAME GROUND · SIX YEARS APART", font=MONOB(26), fill=RED); d.text((80, 330), "Wellington:", font=IB(100), fill=INK); d.text((80, 440), "then and now.", font=IB(100), fill=RED)
    for k, (cx, ph, col, ttl, big, sub) in enumerate(((290, B2020, (225, 222, 212), "2020", "1/88", "FIRST INNINGS · 26 OVERS"), (790, BAPPEAL, (255, 232, 235), "2026", "3/52", "DAY 1 · 17 OVERS"))):
        d.ellipse((cx - 240, 640, cx + 240, 1120), fill=col); d.ellipse((cx - 240, 640, cx + 240, 1120), outline=INK if k == 0 else RED, width=6)
        sc = 600 / ph.height if k == 0 else 470 / ph.height * 1.0
        p = ph.resize((int(ph.width * sc), int(ph.height * sc)), Image.LANCZOS); stamp(im, p, (cx, 1120 - p.height + (30 if k == 0 else 20)))
        d.rounded_rectangle((cx - 230, 1150, cx + 230, 1250), 12, fill=INK if k == 0 else RED); d.text((cx, 1215), f"WELLINGTON {ttl}", font=IB(38), fill=(255, 255, 255), anchor="ms")
        d.text((cx, 1420), big, font=IB(170), fill=INK if k == 0 else RED, anchor="ms"); d.text((cx, 1480), sub, font=MONOB(24), fill=MUTED, anchor="ms")
    d.text((80, 1700), "Bumrah, in the first innings of each Wellington Test.", font=IB(38), fill=INK); d.text((80, 1760), "Our archive: 2020 · Day 1 of 2026 so far.", font=MONO(26), fill=MUTED)
    return im.convert("RGB")
def v_poll():
    w, h = 1080, 1920; im = paper(w, h).convert("RGBA"); d = ImageDraw.Draw(im); chrome(im, d)
    d.text((80, 250), "YOUR CALL · COMMENT 1, 2 OR 3", font=MONOB(26), fill=RED); d.text((80, 330), "Who won", font=IB(120), fill=INK); d.text((80, 455), "day one?", font=IB(120), fill=RED)
    rows = [("1", "NICHOLLS", "113* · fifth Basin hundred", None), ("2", "PHILLIPS", "94 not out · 173 together", None), ("3", "BUMRAH", "3 for 52 · by the 29th over", BAPPEAL)]
    for i, (n, nm, sub, ph) in enumerate(rows):
        y = 700 + i * 330; d.rounded_rectangle((80, y, 1000, y + 290), 24, fill=(255, 255, 255), outline=RED if i == 2 else LINE, width=5)
        d.text((120, y + 200), n, font=IB(130), fill=RED, anchor="ls"); d.text((250, y + 135), nm, font=IB(70), fill=INK, anchor="ls"); d.text((250, y + 195), sub, font=fit_text(d, sub, IB, 480, 30), fill=MUTED, anchor="ls")
        if ph:
            p = ph.resize((int(ph.width * .42), int(ph.height * .42)), Image.LANCZOS); stamp(im, p, (860, y + 290 - p.height - 6))
        else:
            d.rounded_rectangle((760, y + 40, 960, y + 250), 100, outline=MUTED, width=3); d.text((860, y + 150), "PHOTO?", font=MONOB(26), fill=MUTED, anchor="mm")
    d.text((80, 1780), "Nicholls and Phillips: send a photo each, or the cards stay text-only.", font=MONO(26), fill=MUTED)
    return im.convert("RGB")
def l_cold():
    w, h = 1920, 1080; im = paper(w, h).convert("RGBA"); d = ImageDraw.Draw(im); chrome(im, d)
    d.text((140, 330), "BUMRAH'S LAST BALL OF THE DAY · OVER 81", font=MONOB(26), fill=RED); d.text((140, 440), "ONE INSWINGER.", font=IB(104), fill=INK); d.text((140, 560), "ONE TOE.", font=IB(104), fill=RED)
    d.text((140, 740), "Nicholls jammed his bat down in time. Earlier that day: 70 for 5.", font=IB(36), fill=INK)
    d.ellipse((1060, 130, 1700, 770), fill=(255, 235, 235)); d.ellipse((1060, 130, 1700, 770), outline=RED, width=6)
    b = BAPPEAL.resize((int(BAPPEAL.width * 1.5), int(BAPPEAL.height * 1.5)), Image.LANCZOS); stamp(im, b, (1380, 200))
    return im.convert("RGB")
def l_over1():
    w, h = 1920, 1080; im = paper(w, h).convert("RGBA"); d = ImageDraw.Draw(im); chrome(im, d)
    d.text((140, 150), "OVER ONE · BOWLED", font=MONOB(26), fill=RED)
    ph = LATHAM.resize((1000, int(1000 * 533 / 800)), Image.LANCZOS); box = (120, 230, 1120, 230 + ph.height); shadow(im, box, 22)
    card = rounded(ph, 22).rotate(-1.4, expand=True, resample=Image.BICUBIC); im.alpha_composite(card, (110, 215)); d = ImageDraw.Draw(im); tag(d, (150, 250), "BOWLED · 0.3 OV")
    d.text((1260, 380), "LATHAM", font=IB(84), fill=INK); d.text((1260, 470), "b BUMRAH", font=IB(84), fill=RED); d.text((1260, 590), "FULL · 4TH-STUMP LINE", font=MONOB(30), fill=INK); d.text((1260, 640), "SEAM UPRIGHT · CAME BACK IN", font=MONOB(30), fill=MUTED)
    d.rounded_rectangle((1260, 720, 1480, 830), 16, fill=(255, 255, 255), outline=INK, width=4); d.text((1370, 800), "2/1", font=IB(70), fill=INK, anchor="ms")
    return im.convert("RGB")
def l_then_now():
    w, h = 1920, 1080; im = paper(w, h).convert("RGBA"); d = ImageDraw.Draw(im); chrome(im, d)
    d.text((140, 130), "SAME GROUND · SIX YEARS APART", font=MONOB(26), fill=RED); d.text((140, 190), "Wellington: then and now.", font=IB(70), fill=INK)
    for k, (cx, ph, col, ttl, big, sub) in enumerate(((560, B2020, (225, 222, 212), "2020", "1/88", "FIRST INNINGS · 26 OVERS"), (1360, BAPPEAL, (255, 232, 235), "2026", "3/52", "DAY 1 · 17 OVERS"))):
        d.ellipse((cx - 190, 350, cx + 190, 730), fill=col); d.ellipse((cx - 190, 350, cx + 190, 730), outline=INK if k == 0 else RED, width=5)
        sc = 400 / ph.height if k == 0 else 360 / ph.height; p = ph.resize((int(ph.width * sc), int(ph.height * sc)), Image.LANCZOS); stamp(im, p, (cx, 730 - p.height + 24))
        d.rounded_rectangle((cx - 200, 740, cx + 200, 820), 10, fill=INK if k == 0 else RED); d.text((cx, 794), f"WELLINGTON {ttl}", font=IB(32), fill=(255, 255, 255), anchor="ms")
        d.text((cx, 960), big, font=IB(130), fill=INK if k == 0 else RED, anchor="ms"); d.text((cx, 1010), sub, font=MONOB(22), fill=MUTED, anchor="ms")
    return im.convert("RGB")
def sheet(frames, cols, tw, th, path):
    rows = -(-len(frames) // cols); s = Image.new("RGB", (tw * cols + 20 * (cols + 1), th * rows + 20 * (rows + 1)), (255, 255, 255))
    for i, f in enumerate(frames): s.paste(f.resize((tw, th), Image.LANCZOS), (20 + (i % cols) * (tw + 20), 20 + (i // cols) * (th + 20)))
    s.save(path, quality=90)
if __name__ == "__main__":
    V = [v_cold(), v_over1(), v_then_now(), v_poll()]; L = [l_cold(), l_over1(), l_then_now()]
    os.makedirs(f"{R}/out/storyboard_photos", exist_ok=True)
    for i, f in enumerate(V, 1): f.save(f"{R}/out/storyboard_photos/v{i}.png")
    for i, f in enumerate(L, 1): f.save(f"{R}/out/storyboard_photos/l{i}.png")
    sheet(V, 4, 400, 711, f"{R}/out/nz_day1_photo_frames_vertical.jpg"); sheet(L, 3, 640, 360, f"{R}/out/nz_day1_photo_frames_long.jpg"); print("ok")
