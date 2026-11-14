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


def render_panel(spec, W=1080, H=1920):
    th = thumb_of(spec); inf = series.info(spec["slug"]); sid = inf["sid"] if inf else "data"; acc = ACCENT.get(sid, (255, 200, 40))
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


KIT = {"myth_ep2_kohli_reinvention": "RCB", "anchor": "RCB", "rcb_back_to_back": "RCB", "hardik_arshdeep": "MI", "flip_mi_captains": "MI", "dhoni_captain": "CSK",
       "replay_4odi": "NZ", "replay_4odi_young": "NZ", "henry_6balls": "NZ", "santner_problem": "NZ", "bradman_ipl": "AUS", "flip_root_same_point": "ENG"}
POSE = {"myth_ep1_kohli_knockouts": "point", "myth_ep2_kohli_reinvention": "helmet", "myth_ep3_aaryavir": "raise", "replay_u19_final": "celebrate", "hardik_arshdeep": "stand",
        "replay_4odi": "celebrate", "replay_4odi_young": "raise", "replay_4odi_dots": "dejected", "henry_6balls": "arms_wide", "santner_problem": "point", "abhishek_plan": "point",
        "wellington_odi": "stand", "nz_test_preview": "walk", "bay_oval_new_ball": "dejected", "lab_ep1_abhishek_twin": "point", "lab_ep2_bumrah_twin": "arms_wide",
        "stat_check_bumrah_rashid": "point", "bradman_ipl": "raise", "bumrah_vs_90s": "arms_wide", "dhoni_captain": "stand", "sachin_t20": "helmet", "aaryavir_sehwag": "helmet",
        "flip_abhishek_openers": "point", "flip_bumrah_52_tests": "arms_wide", "flip_mi_captains": "raise", "flip_root_same_point": "point", "anchor": "point",
        "powerplay_revolution": "point", "ipl_batting_evolution": "walk", "two_hundred": "raise", "india_160": "stand", "bumrah_economy": "arms_wide", "death_kings": "celebrate",
        "rcb_back_to_back": "celebrate", "kohli_2000_nz": "raise"}
BOWLERS = {"henry_6balls", "santner_problem", "lab_ep2_bumrah_twin", "bumrah_vs_90s", "flip_bumrah_52_tests", "bumrah_economy", "death_kings"}     # bowlers wear a cap, not a helmet
# Flips have no thumb block: their cover comes from the spec's own title and end card
FLIP_COVER = {"flip_abhishek_openers": ("ABHISHEK VS", "THE WORLD'S OPENERS", "191.9"), "flip_bumrah_52_tests": ("BUMRAH VS", "THE BEST OF THE CENTURY", "19.79"),
              "flip_mi_captains": ("EVERY MI CAPTAIN", "VS ROHIT SHARMA", "56.3%"), "flip_root_same_point": ("JOE ROOT VS", "EVERYONE ELSE", "14,278")}


def thumb_of(spec):
    if spec.get("thumb"): return spec["thumb"]
    f = FLIP_COVER.get(spec["slug"])
    return {"lines": [{"t": f[0]}, {"t": f[1], "c": "gold"}], "hero": f[2]} if f else {}


def _base(spec, W, H, light=False):
    th = thumb_of(spec); inf = series.info(spec["slug"]); sid = inf["sid"] if inf else "data"; acc = ACCENT.get(sid, (255, 200, 40))
    arr = np.zeros((H, W, 4), np.uint8); sf = skia.Surface(arr); c = sf.getCanvas()
    return th, inf, sid, acc, arr, sf, c


def _pill(c, W, inf, sid, acc, y=330, dark=False):
    ep = f" · EP. {int(inf['ep'])}" if inf and inf["ep"].isdigit() and int(inf["ep"]) > 0 and sid in ("myth", "lab", "statcheck", "replay", "tactics", "whatif", "rising", "flip") else ""
    pill = SERIES_SHORT.get(sid, "") + ep
    if sid == "replay" and inf and inf["ep"][-1:].isalpha(): pill = "THE REPLAY ROOM · EXTRA"
    pw = twidth(pill, 56, "bebas", 3) + 70
    rrect(c, W / 2 - pw / 2, y, pw, 84, 42, (14, 14, 18) if dark else acc, 1); text(c, pill, W / 2, y + 61, 56, "bebas", acc if dark else NAVY, 1, "c", track=3)


def _navy(c, W, H, acc, glow_y=1090):
    bg = skia.Paint(); bg.setShader(skia.GradientShader.MakeLinear([(0, 0), (0, H)], [skia.Color(*NAVY), skia.Color(*NAVY2), skia.Color(*NAVY)], [0, .55, 1]))
    c.drawRect(skia.Rect.MakeWH(W, H), bg)
    glow = skia.Paint(); glow.setShader(skia.GradientShader.MakeRadial((W / 2, glow_y), 720, [skia.Color(acc[0], acc[1], acc[2], 80), skia.Color(acc[0], acc[1], acc[2], 0)]))
    c.drawRect(skia.Rect.MakeWH(W, H), glow)


def _hook(c, W, th, acc, y0=470, size=200, align="c", x=None, width=940, light=False):
    y = y0
    for l in th.get("lines", [])[:2]:
        z = E.fit(l["t"], width, size, "bebas", 2); y += z * .86
        hot = l.get("c") in ("gold", "red")
        col = (acc if hot else ((20, 20, 24) if light else (255, 255, 255)))
        text(c, l["t"], W / 2 if align == "c" else x, y, z, "bebas", col, 1, align, track=2, glow=16 if (hot and not light) else 0)
        y += z * .08
    return y


def render_avatar(spec, W=1080, H=1920):
    """The channel cover: navy base, series accent, illustrated player in the team kit, the number as a sticker. Safe band y 300-1620."""
    th, inf, sid, acc, arr, sf, c = _base(spec, W, H)
    _navy(c, W, H, acc, 1160)
    _pill(c, W, inf, sid, acc)
    _hook(c, W, th, acc, 460, 175)
    slug = spec["slug"]; kit, pose = KIT.get(slug, "IND"), POSE.get(slug, "stand")
    if slug == "channel_trailer":                                              # the brand mark stands in for the player
        c.drawCircle(W / 2, 1190, 330, paint(acc, .10)); gfx.logo_lockup(c, W / 2, 1230, 250, 1, "c")
    else:
        E.avatar(c, W / 2 - 30, 1545, 520, kit, None, pose, 1.1, 1.0, cap=True if slug in BOWLERS else None)
    hero = th.get("hero")
    if hero and slug != "channel_trailer":                                      # the number as a sticker on the figure's shoulder
        if len(hero) <= 4:
            cx, cy, r = 780, 1290, 170
            c.drawCircle(cx, cy, r + 14, paint((0, 0, 0), .35, blur=24)); c.drawCircle(cx, cy, r, paint(acc, 1)); c.drawCircle(cx, cy, r - 14, paint(acc, 1, stroke=5))
            z = E.fit(hero, 2 * r - 70, 250, "bebas"); text(c, hero, cx, cy + z * .34, z, "bebas", NAVY, 1, "c")
        else:                                                                    # longer values get a wide rounded sticker
            z = E.fit(hero, 480, 190, "bebas"); w_ = min(620, twidth(hero, z, "bebas", 0) + 90); cx, cy = W - 80 - w_ / 2, 1290
            rrect(c, cx - w_ / 2, cy - 112, w_, 224, 60, (0, 0, 0), .35); rrect(c, cx - w_ / 2, cy - 100, w_, 200, 56, acc, 1)
            text(c, hero, cx, cy + z * .34, z, "bebas", NAVY, 1, "c")
    gfx.logo_lockup(c, W / 2, 1592, 72, 1, "c")
    sf.flushAndSubmit(); return arr


def render_scoreboard(spec, W=1080, H=1920):
    th, inf, sid, acc, arr, sf, c = _base(spec, W, H)
    bg = skia.Paint(); bg.setShader(skia.GradientShader.MakeLinear([(0, 0), (0, H)], [skia.Color(14, 16, 20), skia.Color(30, 34, 42), skia.Color(14, 16, 20)])); c.drawRect(skia.Rect.MakeWH(W, H), bg)
    _pill(c, W, inf, sid, acc)
    y = _hook(c, W, th, acc, 460, 190)
    bx, by, bw, bh = 70, max(y + 50, 940), W - 140, 600
    rrect(c, bx, by, bw, bh, 38, (62, 66, 74), 1); rrect(c, bx + 16, by + 16, bw - 32, bh - 32, 28, (8, 12, 10), 1)
    for i in range(17):                                                         # bulbs round the bezel
        xx = bx + 60 + i * (bw - 120) / 16; c.drawCircle(xx, by + 8, 5, paint(acc, .95)); c.drawCircle(xx, by + bh - 8, 5, paint(acc, .95))
    LED = (255, 176, 20)
    hero = th.get("hero", "")
    z = E.fit(hero, bw - 180, 470, "bebas")
    for k in range(3):                                                          # LED glow
        text(c, hero, W / 2, by + bh / 2 + z * .34, z, "bebas", LED, .12 if k < 2 else 1, "c", glow=40 if k < 2 else 8)
    gfx.logo_lockup(c, W / 2, 1620, 72, 1, "c")
    sf.flushAndSubmit(); return arr


def render_paper(spec, W=1080, H=1920):
    E.apply_theme("lab")
    th, inf, sid, acc, arr, sf, c = _base(spec, W, H)
    c.drawRect(skia.Rect.MakeWH(W, H), paint((246, 245, 241), 1))
    for i in range(0, W, 60): c.drawLine(i, 0, i, H, paint((20, 20, 24), .035, stroke=1))
    for j in range(0, H, 60): c.drawLine(0, j, W, j, paint((20, 20, 24), .035, stroke=1))
    _pill(c, W, inf, sid, acc, dark=True)
    y = 470
    for k, l in enumerate(th.get("lines", [])[:2]):
        z = E.fit(l["t"], 900, 200, "bebas", 2); y += z * .86; hot = l.get("c") in ("gold", "red")
        if hot:
            tw = twidth(l["t"], z, "bebas", 2); rrect(c, W / 2 - tw / 2 - 26, y - z * .86, tw + 52, z * .96, 10, acc, 1)
        text(c, l["t"], W / 2, y, z, "bebas", (20, 20, 24), 1, "c", track=2); y += z * .1
    hero = th.get("hero")
    if hero:
        hz = E.fit(hero, 880, 520, "bebas"); hy = max(y + 80, 1100) + hz * .62
        text(c, hero, W / 2, hy, hz, "bebas", (20, 20, 24), 1, "c")
        c.drawRect(skia.Rect.MakeXYWH(W / 2 - 230, hy + 36, 460, 22), paint(acc, 1))
    gfx.logo_lockup(c, W / 2, 1610, 76, 1, "c")
    sf.flushAndSubmit(); E.apply_theme("stadium"); return arr


def render_poster(spec, W=1080, H=1920):
    th, inf, sid, acc, arr, sf, c = _base(spec, W, H)
    _navy(c, W, H, acc, 960)
    hero = th.get("hero", "")
    if hero:
        hz = E.fit(hero, 1200, 1000, "bebas"); text(c, hero, W / 2, 1050 + hz * .34, hz, "bebas", acc, .17, "c")           # giant watermark number
    _pill(c, W, inf, sid, acc)
    y = _hook(c, W, th, acc, 560, 260, "l", 90, 900)
    band = skia.Path(); band.moveTo(0, 1360); band.lineTo(W, 1270); band.lineTo(W, 1480); band.lineTo(0, 1570); band.close(); c.drawPath(band, paint(acc, 1))
    if hero:
        z = E.fit(hero, 700, 200, "bebas"); c.save(); c.translate(W / 2, 1420); c.rotate(-5); text(c, hero, 0, z * .34, z, "bebas", NAVY, 1, "c"); c.restore()
    gfx.logo_lockup(c, W / 2, 1650, 72, 1, "c")
    sf.flushAndSubmit(); return arr


STYLES = {"panel": render_panel, "avatar": render_avatar, "scoreboard": render_scoreboard, "paper": render_paper, "poster": render_poster}


def render(spec, W=1080, H=1920, style=None):
    return STYLES[style or spec.get("cover_style") or "avatar"](spec, W, H)


def safe_zones(arr, path):
    """The cover with Instagram's crops marked: profile grid (3:4, centre), feed preview (4:5), and the buttons drawn on grid tiles."""
    from PIL import Image, ImageDraw
    im = Image.fromarray(arr[:, :, :3]).convert("RGBA"); W, H = im.size; ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    gy0 = (H - int(W * 4 / 3)) // 2; fy0 = (H - int(W * 5 / 4)) // 2
    for y0, y1 in ((0, gy0), (H - gy0, H)): d.rectangle([0, y0, W, y1], fill=(0, 0, 0, 170))          # hidden in the grid
    d.rectangle([0, gy0, W - 1, H - gy0], outline=(0, 255, 120, 255), width=6)                       # grid 3:4
    d.line([0, fy0, W, fy0], fill=(255, 80, 80, 255), width=5); d.line([0, H - fy0, W, H - fy0], fill=(255, 80, 80, 255), width=5)   # feed 4:5
    d.rectangle([W - 160, gy0 + 20, W - 30, gy0 + 140], outline=(255, 255, 0, 255), width=5)        # reel icon (top right of a tile)
    d.rectangle([20, H - gy0 - 120, 250, H - gy0 - 20], outline=(255, 255, 0, 255), width=5)         # view count (bottom left of a tile)
    Image.alpha_composite(im, ov).convert("RGB").resize((W // 2, H // 2)).save(path); return path


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
    style = os.environ.get("STYLE", "avatar")
    for slug in sys.argv[1:]:
        spec = json.load(open(f"{ROOT}/specs/{slug}.json")); a = render(spec, style=style); arrs.append(a)
        Image.fromarray(a[:, :, :3]).save(f"{ROOT}/out/_covers/{slug}_{style}.png")
    print(grid(arrs, f"{ROOT}/out/_covers/grid_{style}.png"))
