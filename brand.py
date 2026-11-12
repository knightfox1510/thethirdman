"""Export the channel's brand pack (Field Map logo) to brand/.
    python3 brand.py
Profile pictures (YouTube/Instagram), watermark, horizontal lockups and the YouTube banner."""
import os, numpy as np, skia
from PIL import Image
import gfx

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brand")
NAVY, CREAM, GOLD, GREY = (16, 33, 63), (244, 241, 234), (245, 183, 0), (150, 160, 185)
TAGLINE = "CRICKET FROM A DIFFERENT ANGLE"


def palette(ink, line, muted, gold):
    gfx.INK, gfx.LINE, gfx.MUTED, gfx.GOLD = ink, line, muted, gold


def canvas(w, h, bg=None):
    arr = np.zeros((h, w, 4), np.uint8)
    sf = skia.Surface(arr); c = sf.getCanvas()
    c.clear(skia.Color(*bg) if bg else skia.ColorTRANSPARENT)
    return arr, sf, c


def save(arr, sf, name):
    sf.flushAndSubmit()
    im = Image.fromarray(arr.copy(), "RGBA")
    im.save(os.path.join(OUT, name)); return name


def mix(a, b, t): return tuple(int(x + (y - x) * t) for x, y in zip(a, b))


def main():
    os.makedirs(OUT, exist_ok=True)
    gfx.apply_theme("floodlights")      # Bebas wordmark
    files = []
    # profile pictures: the mark sits well inside the circular crop
    for name, bg, ink in [("profile_dark_800.png", NAVY, CREAM), ("profile_light_800.png", CREAM, NAVY)]:
        arr, sf, c = canvas(800, 800, bg)
        palette(ink, mix(bg, ink, .35), mix(bg, ink, .6), GOLD)
        gfx.logo_mark(c, 400, 400, 560, 1, detail=True)
        files.append(save(arr, sf, name))
    # watermark for YouTube (150x150, transparent)
    arr, sf, c = canvas(150, 150)
    palette(CREAM, (200, 200, 200), (220, 220, 220), GOLD)
    gfx.logo_mark(c, 75, 75, 136, 1, detail=False)
    files.append(save(arr, sf, "watermark_150.png"))
    # horizontal lockups, transparent
    for name, ink, muted in [("lockup_on_dark.png", CREAM, GREY), ("lockup_on_light.png", NAVY, (91, 100, 114))]:
        arr, sf, c = canvas(1400, 360)
        palette(ink, mix((128, 128, 128), ink, .4), muted, GOLD)
        gfx.logo_lockup(c, 700, 180, 240, 1, align="c")
        files.append(save(arr, sf, name))
    # YouTube banner 2560x1440; everything important inside the 1546x423 centre safe area
    arr, sf, c = canvas(2560, 1440, NAVY)
    palette(CREAM, mix(NAVY, CREAM, .35), mix(NAVY, CREAM, .6), GOLD)
    # faint field rings across the full banner (visible on TV/desktop, cropped on mobile)
    for r, al in [(1100, .05), (700, .06), (420, .07)]:
        c.drawCircle(1280, 720, r, gfx.paint(CREAM, al, stroke=4))
    gfx.logo_lockup(c, 1280, 690, 210, 1, align="c")
    gfx.text(c, TAGLINE, 1280, 850, 44, "interB", GOLD, 1, "c", track=10)
    files.append(save(arr, sf, "youtube_banner_2560x1440.png"))
    return files


if __name__ == "__main__":
    print(*main(), sep="\n")
