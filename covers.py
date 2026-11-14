"""Cover images for vertical videos (Instagram grid + YouTube Shorts): one consistent system across every series.
    python3 covers.py <slug> [<slug> ...]       # writes out/_covers/<slug>_cover_v2.png (mockups)
Design rules (Instagram's profile grid shows the centre 3:4 of the 9:16 frame, ~320 px wide on a phone):
  - the same dark navy base on every video; the SERIES is told by an accent colour + the series/episode pill, never by a different background
  - everything that matters sits inside the grid-safe band (y 300-1620 of 1920)
  - the hero number sits on a dark panel (it used to sit on the tan pitch and lost contrast); two-line hook in huge white + accent type"""
import json, math, os, sys
import numpy as np, skia
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "publish"))
import engine as E, gfx, series
from gfx import text, rrect, paint, twidth

ACCENT = {"myth": (255, 200, 40), "replay": (255, 92, 92), "tactics": (92, 190, 255), "lab": (110, 225, 170), "statcheck": (190, 150, 255),
          "whatif": (255, 160, 70), "rising": (255, 130, 205), "flip": (70, 225, 225), "data": (255, 236, 150), "channel": (255, 200, 40)}
NAVY, NAVY2 = (9, 14, 30), (22, 36, 72)
SERIES_SHORT = {"myth": "MYTH OR DATA?", "replay": "THE REPLAY ROOM", "tactics": "TACTICS BOARD", "lab": "THE LAB", "statcheck": "STAT CHECK", "whatif": "WHAT IF?",
                "rising": "RISING STAR", "flip": "FLIP", "data": "DATA STORY", "channel": "WELCOME"}


def render(spec, W=1080, H=1920):
    th = spec.get("thumb") or {}; inf = series.info(spec["slug"]); sid = inf["sid"] if inf else "data"; acc = ACCENT.get(sid, (255, 200, 40))
    arr = np.zeros((H, W, 4), np.uint8); sf = skia.Surface(arr); c = sf.getCanvas()
    bg = skia.Paint(); bg.setShader(skia.GradientShader.MakeLinear([(0, 0), (0, H)], [skia.Color(*NAVY), skia.Color(*NAVY2), skia.Color(*NAVY)], [0, .55, 1]))
    c.drawRect(skia.Rect.MakeWH(W, H), bg)
    for i in range(-6, 14):                                                     # brand stripes, faint, in the series colour
        x = i * 190; p = skia.Path(); p.moveTo(x, 0); p.lineTo(x + 90, 0); p.lineTo(x + 90 + 1300, H); p.lineTo(x + 1300, H); p.close()
        c.drawPath(p, paint(acc, .035))
    glow = skia.Paint(); glow.setShader(skia.GradientShader.MakeRadial((W / 2, 1090), 700, [skia.Color(acc[0], acc[1], acc[2], 70), skia.Color(acc[0], acc[1], acc[2], 0)]))
    c.drawRect(skia.Rect.MakeWH(W, H), glow)
    # series / episode pill
    ep = f" · EP. {int(inf['ep'])}" if inf and inf["ep"].isdigit() and int(inf["ep"]) > 0 and sid in ("myth", "lab", "statcheck", "replay", "tactics", "whatif", "rising", "flip") else ""
    pill = SERIES_SHORT.get(sid, "") + ep
    if sid == "replay" and inf and inf["ep"][-1:].isalpha(): pill = "THE REPLAY ROOM · EXTRA"
    pw = twidth(pill, 56, "bebas", 3) + 70
    rrect(c, W / 2 - pw / 2, 330, pw, 84, 42, acc, 1); text(c, pill, W / 2, 391, 56, "bebas", NAVY, 1, "c", track=3)
    # hook: two lines, white then accent
    y = 470
    for k, l in enumerate(th.get("lines", [])[:2]):
        z = E.fit(l["t"], 940, 210, "bebas", 2); y += z * .86
        text(c, l["t"], W / 2, y, z, "bebas", (255, 255, 255) if (l.get("c") not in ("gold", "red")) else acc, 1, "c", track=2, glow=16 if l.get("c") in ("gold", "red") else 0)
        y += z * .08
    # hero number (or, for a cover with none, the brand mark) on a dark panel
    hero = th.get("hero"); ph = 500; py = max(y + 30, 960)
    rrect(c, 90, py, W - 180, ph, 56, (0, 0, 0), .55, stroke=6, scol=acc, sa=.9)
    if hero:
        hs = E.fit(hero, 800, min(th.get("herosize", 520), 480), "bebas")
        text(c, hero, W / 2, py + ph / 2 + hs * .34, hs, "bebas", acc, 1, "c", glow=26)
    else:
        gfx.logo_lockup(c, W / 2, py + ph / 2 + 30, 200, 1, "c")
    if not hero: pass
    gfx.logo_lockup(c, W / 2, 1600, 80, 1, "c") if hero else None
    sf.flushAndSubmit()
    return arr


def grid(arrs, path, cols=3, tile_w=360):
    """What Instagram's profile grid shows: the centre 3:4 of each 9:16 cover."""
    from PIL import Image
    tiles = []
    for a in arrs:
        im = Image.fromarray(a[:, :, :3]); w, h = im.size; ch = int(w * 4 / 3); y0 = (h - ch) // 2
        tiles.append(im.crop((0, y0, w, y0 + ch)).resize((tile_w, int(tile_w * 4 / 3))))
    rows = (len(tiles) + cols - 1) // cols; th_ = tiles[0].size[1]
    sheet = Image.new("RGB", (cols * tile_w + (cols - 1) * 3, rows * th_ + (rows - 1) * 3), (0, 0, 0))
    for i, t in enumerate(tiles): sheet.paste(t, ((i % cols) * (tile_w + 3), (i // cols) * (th_ + 3)))
    sheet.save(path); return path


if __name__ == "__main__":
    E.apply_theme("stadium"); os.makedirs(f"{ROOT}/out/_covers", exist_ok=True); arrs = []
    from PIL import Image
    for slug in sys.argv[1:]:
        spec = json.load(open(f"{ROOT}/specs/{slug}.json")); a = render(spec); arrs.append(a)
        Image.fromarray(a[:, :, :3]).save(f"{ROOT}/out/_covers/{slug}_cover_v2.png")
    print(grid(arrs, f"{ROOT}/out/_covers/grid_v2.png"))
