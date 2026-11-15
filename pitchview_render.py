"""3D renderer + Swiss-style poster layout for pitchview.Delivery (mock-ups for the pitch-view Reel; the engine scene will reuse the same geometry).
    python3 pitchview_render.py            writes deliver/_pitchview_mockups/final/*.png
Camera: Cam(target, yaw, elevation, distance). yaw 0 = behind the bowler looking down the pitch; 90 = side-on; 180 = behind the batter.
Everything not in the data is labelled 'illustrative' on the poster (see pitchview.py: DATA vs MODEL)."""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pitchview import *

FONTS = "fonts/"
font = lambda n, s: ImageFont.truetype(FONTS + n, max(1, int(s)))
W, H = 1080, 1920
PALS = {
    "swiss": dict(name="Swiss mono", bg=(246, 246, 242), ground=(232, 232, 226), grid=(222, 222, 216), pitch=(255, 255, 255), band=[(236, 236, 236), (244, 244, 244), (255, 255, 255), (244, 244, 244), (236, 236, 236)],
                  ink=(16, 16, 16), line=(24, 24, 24), accent=(226, 30, 30), alt=(16, 16, 16), muted=(112, 112, 106), rule=(16, 16, 16), fig=(60, 60, 60), gate=(226, 30, 30)),
    "red_soil_swiss": dict(name="Red soil, Swiss layout", bg=(244, 236, 224), ground=(220, 196, 170), grid=(210, 184, 156), pitch=(204, 132, 88), band=[(186, 112, 72), (196, 122, 80), (204, 132, 88), (214, 146, 100), (224, 160, 116)],
                           ink=(26, 18, 14), line=(255, 244, 224), accent=(176, 52, 28), alt=(26, 18, 14), muted=(122, 96, 78), rule=(26, 18, 14), fig=(52, 36, 28), gate=(176, 52, 28)),
}


class Cam:
    def __init__(s, target, yaw, el, R, F=1900, cx=W / 2, cy=500):
        y, e = math.radians(yaw), math.radians(el); t = np.array(target, float)
        s.C = t + R * np.array([math.sin(y) * math.cos(e), -math.cos(y) * math.cos(e), math.sin(e)])
        f = t - s.C; s.f = f / np.linalg.norm(f); r = np.cross(s.f, [0, 0, 1.0]); s.r = r / np.linalg.norm(r); s.u = np.cross(s.r, s.f); s.F, s.cx, s.cy = F, cx, cy

    def p(s, pt):
        v = np.array(pt, float) - s.C; z = v @ s.f
        return None if z < 0.3 else (s.cx + s.F * (v @ s.r) / z, s.cy - s.F * (v @ s.u) / z, z)


def mix(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def scene(P, cam, dl, tr, S=1.5, size=(W, 1000), show_gate=True, show_bat=True, ball_at=None):
    """The 3D picture on a plain ground. Returns a PIL image of `size` (scaled by S)."""
    Wd, Hd = int(size[0] * S), int(size[1] * S); im = Image.new("RGB", (Wd, Hd), P["bg"]); d = ImageDraw.Draw(im)
    sc = lambda q: (q[0] * S, q[1] * S)

    def poly(pts, **k):
        q = [cam.p(p) for p in pts]
        if all(q): d.polygon([sc(x) for x in q], **k)

    def line3(pts, fill, w, dash=0):
        q = [cam.p(p) for p in pts]; q = [x for x in q if x]
        if len(q) < 2: return
        if not dash: d.line([sc(x) for x in q], fill=fill, width=max(1, int(w * S)), joint="curve"); return
        for i in range(0, len(q) - 1, dash * 2): d.line([sc(x) for x in q[i:i + dash + 1]], fill=fill, width=max(1, int(w * S)))

    poly([(-90, -40, 0), (90, -40, 0), (90, PL + 90, 0), (-90, PL + 90, 0)], fill=P["ground"])
    for gx in range(-90, 91, 10): line3([(gx, -40, 0), (gx, PL + 90, 0)], P["grid"], 1)
    for gy in range(-40, int(PL) + 91, 10): line3([(-90, gy, 0), (90, gy, 0)], P["grid"], 1)
    ring = [(27.43 * math.cos(a / 60 * 2 * math.pi), PL / 2 + 27.43 * math.sin(a / 60 * 2 * math.pi), 0) for a in range(61)]; line3(ring, P["muted"], 2, dash=2)   # the 30-yard circle
    poly([(-PW / 2, 0, 0), (PW / 2, 0, 0), (PW / 2, PL, 0), (-PW / 2, PL, 0)], fill=P["pitch"])
    for i, (y0, y1) in enumerate([(PL - 2, PL), (PL - 4, PL - 2), (PL - 6, PL - 4), (PL - 8, PL - 6), (8.0, PL - 8)]):
        poly([(-PW / 2, y0, 0), (PW / 2, y0, 0), (PW / 2, y1, 0), (-PW / 2, y1, 0)], fill=P["band"][i])
    line3([(-PW / 2, 0, 0), (PW / 2, 0, 0), (PW / 2, PL, 0), (-PW / 2, PL, 0), (-PW / 2, 0, 0)], P["line"], 3)
    for yy in (1.22, PL - 1.22): line3([(-1.3, yy, 0), (1.3, yy, 0)], P["line"], 3)
    for yy in (0, PL):
        for xx in (-0.11, 0, 0.11): line3([(xx, yy, 0), (xx, yy, 0.71)], P["ink"] if P["name"] == "Swiss mono" else P["line"], 6)
    H_ = dl.batter_h; gy = PL - 1.22; hand = 1 if dl.hand == "R" else -1
    if show_gate:                                                    # the crease 'gate': a height ruler at the batter's crease, in the batter's own proportions
        gx0, gx1 = -1.7, 1.7
        for name, f in HEIGHT_MARKS + [("STUMPS", .71 / H_)]:
            z = f * H_; line3([(gx0, gy, z), (gx1, gy, z)], mix(P["muted"], P["bg"], .35), 2)
            q = cam.p((gx0 - 0.15, gy, z))
            if q: d.text(sc(q), name, font=font("PlexMonoSB.ttf", 19), fill=P["muted"], anchor="rm")
        line3([(gx0, gy, 0), (gx0, gy, H_ + .1)], P["muted"], 2); line3([(gx1, gy, 0), (gx1, gy, H_ + .1)], P["muted"], 2)
        bx = -0.55 * hand * -1                                       # batter stands beside the stumps on the leg side of the pitch centre
        bxx = 0.55 * hand
        head = (bxx, gy - 0.1, H_ - 0.12); line3([(bxx, gy - 0.1, 0), (bxx, gy - 0.1, H_ - 0.3)], P["fig"], 9); line3([(bxx, gy - 0.1, 0.9), (bxx - 0.25 * hand, gy - 0.5, 0.55)], P["fig"], 7)   # body, front leg
        hq = cam.p(head)
        if hq: r = max(6, 0.12 * cam.F / hq[2]); d.ellipse([(hq[0] - r) * S, (hq[1] - r) * S, (hq[0] + r) * S, (hq[1] + r) * S], outline=P["fig"], width=int(5 * S))
        line3([(bxx + 0.05 * hand, gy - 0.4, 0.5), (bxx - 0.18 * hand, gy - 0.9, 0.25)], P["accent"], 6)   # bat
    # ball path: pre-bounce, post-bounce (accent), off the bat (dashed, to the catch)
    pre, post, bat = tr["pre"], tr["post"], tr["bat"]
    line3(pre + post, P["accent"], 7)
    if bat: line3(bat, P["accent"], 5, dash=2)
    if tr["bounce"]:
        bx_, by_, _ = tr["bounce"]; ring_ = [(bx_ + 0.9 * math.cos(a / 24 * 2 * math.pi), by_ + 0.9 * math.sin(a / 24 * 2 * math.pi), 0) for a in range(25)]; line3(ring_, P["accent"], 4)
    if show_gate:
        gz = tr["gate_z"]; q = cam.p((tr["contact"][0] / 0.7 * 0.7, gy, gz))
        if q: r = max(8, 0.16 * cam.F / q[2]); d.ellipse([(q[0] - r) * S, (q[1] - r) * S, (q[0] + r) * S, (q[1] + r) * S], fill=P["accent"], outline=P["bg"], width=int(3 * S))
    end = tr["end"]
    if end and bat:
        q = cam.p(end)
        if q: r = max(9, .3 * cam.F / q[2]); d.ellipse([(q[0] - r) * S, (q[1] - r) * S, (q[0] + r) * S, (q[1] + r) * S], outline=P["ink"], width=int(5 * S))
    if ball_at is not None:
        pts = pre + post + bat; q = cam.p(pts[min(len(pts) - 1, int(ball_at * (len(pts) - 1)))])
        if q: r = max(9, .17 * cam.F / q[2]); d.ellipse([(q[0] - r) * S, (q[1] - r) * S, (q[0] + r) * S, (q[1] + r) * S], fill=P["ink"])
    return im, cam


def follow_cam(tr, yaw=-50, el=30):
    """Frames the ball's journey off the bat so the whole pitch, the bat contact and the catch fit: pick the distance so the picture spans ~78% of the width, then centre it."""
    a, b = tr["contact"], tr["end"] or tr["contact"]; mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 0.5); keys = ((-PW / 2, 0, 0), (PW / 2, PL, 0), a, b)
    R = 40.0
    for _ in range(3):
        cam = Cam(mid, yaw, el, R, F=1700, cy=520); pts = [q for q in (cam.p(k) for k in keys) if q]
        w = max(q[0] for q in pts) - min(q[0] for q in pts); h = max(q[1] for q in pts) - min(q[1] for q in pts)
        R *= max(w / (0.78 * W), h / 760.0)
    cam = Cam(mid, yaw, el, R, F=1700, cy=520); pts = [q for q in (cam.p(k) for k in keys) if q]
    xs, ys = [q[0] for q in pts], [q[1] for q in pts]; cam.cx += W / 2 - (min(xs) + max(xs)) / 2; cam.cy += 500 - (min(ys) + max(ys)) / 2
    return cam


def poster(P, dl, tr, cam, mode, out, S=1.5):
    """Swiss layout: hairline rules, a big ball number, three facts in columns, the model's reading in one plain sentence, and the 'illustrative' note."""
    sm, _ = scene(P, cam, dl, tr, S=S, size=(W, 1040), show_gate=(mode == "height"))
    im = Image.new("RGB", (int(W * S), int(H * S)), P["bg"]); d = ImageDraw.Draw(im); X = lambda v: int(v * S)
    im.paste(sm, (0, X(330)))
    d.rectangle([0, X(330), X(W), X(1370)], outline=None)
    d.line([X(60), X(96), X(W - 60), X(96)], fill=P["rule"], width=X(4))
    d.text((X(60), X(124)), "THE THIRD MAN · INSIGHTS", font=font("PlexMonoSB.ttf", 24), fill=P["muted"], anchor="la")
    d.text((X(W - 60), X(124)), "NZ v IND · 4TH ODI" if "Henry" in dl.bowler or "Brar" in dl.bowler else "U19 ASIA CUP FINAL", font=font("PlexMonoSB.ttf", 24), fill=P["muted"], anchor="ra")
    d.text((X(60), X(170)), f"{dl.over:.1f}".replace(".", "·"), font=font("OswaldBold.ttf", 170), fill=P["accent"], anchor="la")
    d.text((X(W - 60), X(190)), dl.bowler.upper(), font=font("OswaldBold.ttf", 56), fill=P["ink"], anchor="ra"); d.text((X(W - 60), X(256)), "TO  " + dl.batter.upper(), font=font("OswaldBold.ttf", 56), fill=P["ink"], anchor="ra")
    sm_ = summary(dl, tr); y0 = 1400
    d.line([X(60), X(y0), X(W - 60), X(y0)], fill=P["rule"], width=X(3))
    cols = [("LENGTH", sm_["length"].title()), ("LINE", sm_["line"].title()), ("RESULT", (sm_["how"] or ("%d run%s" % (dl.runs, "" if dl.runs == 1 else "s"))).upper() if dl.wicket else ("%d run%s" % (dl.runs, "" if dl.runs == 1 else "s")))]
    cw = (W - 120) / 3
    for i, (k, v) in enumerate(cols):
        x = 60 + i * cw
        if i: d.line([X(x - 12), X(y0 + 20), X(x - 12), X(y0 + 170)], fill=P["muted"], width=X(1))
        d.text((X(x), X(y0 + 28)), k, font=font("PlexMonoSB.ttf", 21), fill=P["muted"], anchor="la")
        fs = 44 if len(v) < 16 else 31; d.text((X(x), X(y0 + 70)), v, font=font("OswaldBold.ttf", fs), fill=P["ink"], anchor="la")
    d.line([X(60), X(y0 + 190), X(W - 60), X(y0 + 190)], fill=P["rule"], width=X(3))
    if mode == "height":
        big = f"{tr['gate_z']:.1f} m"; d.text((X(60), X(y0 + 215)), big, font=font("OswaldBold.ttf", 120), fill=P["accent"], anchor="la")
        d.text((X(380), X(y0 + 232)), "ball height at the batter's crease", font=font("Inter-SemiBold.otf", 31), fill=P["ink"], anchor="la")
        d.text((X(380), X(y0 + 276)), sm_["height_text"].capitalize() + f" of a {dl.batter_h:.2f} m batter.", font=font("Inter-Medium.otf", 29), fill=P["ink"], anchor="la")
        d.text((X(380), X(y0 + 320)), f"Control: {sm_['control']}.", font=font("Inter-Medium.otf", 29), fill=P["ink"], anchor="la")
    else:
        who = dl.fielder or "the fielder"; kind = "wicket-keeper" if dl.keeper_catch else "fielder"
        d.text((X(60), X(y0 + 215)), "CAUGHT", font=font("OswaldBold.ttf", 96), fill=P["accent"], anchor="la")
        d.text((X(480), X(y0 + 228)), f"by {who.upper()}", font=font("OswaldBold.ttf", 46), fill=P["ink"], anchor="la")
        d.text((X(480), X(y0 + 290)), ("The keeper takes it behind the stumps." if dl.keeper_catch else "Catch spot from the wagon wheel (approximate)."), font=font("Inter-Medium.otf", 29), fill=P["ink"], anchor="la")
        d.text((X(480), X(y0 + 332)), f"Shot: {sm_['shot']}. Control: {sm_['control']}.", font=font("Inter-Medium.otf", 29), fill=P["ink"], anchor="la")
    for i, ln in enumerate((f"MOCK-UP · ILLUSTRATIVE: bounce, height and arcs are modelled ({dl.pace_kmh:.0f} km/h, {dl.batter_h:.2f} m batter, {dl.catch_z:.1f} m catch).", "Zones, shot, control, dismissal and catcher are from the Cricinfo capture.")):
        d.text((X(60), X(1846 + i * 26)), ln, font=font("PlexMono.ttf", 17), fill=P["muted"], anchor="la")
    im.resize((W, H), Image.LANCZOS).save(out)


if __name__ == "__main__":
    OUT = "deliver/_pitchview_mockups/final/"; os.makedirs(OUT, exist_ok=True)
    T4 = ("data/cricinfo/nz_ind_4odi_balls.csv", "data/cricinfo/nz_ind_4odi.json"); U19 = ("data/cricinfo/u19_final_balls.csv", "data/cricinfo/u19_final.json")
    jobs = []
    kohli = from_table(*T4, 2, 0.5); rohit = from_table(*T4, 2, 0.1); seifert = from_table(*T4, 1, 11.6); aary = from_table(*U19, 2, 17.4, pace_kmh=120.0)
    for key, P in PALS.items():
        for tag, dl, mode, cam in (("height_kohli", kohli, "height", lambda t: Cam((0, PL - 1.0, 0.9), 24, 9, 9.5, cy=540)),
                                   ("catch_rohit", rohit, "catch", lambda t: follow_cam(t))):
            tr = trajectory(dl); poster(P, dl, tr, cam(tr), mode, OUT + f"{key}_{tag}.png")
    P = PALS["swiss"]
    for tag, dl, cam in (("catch_keeper_seifert", seifert, None), ("catch_u19_aaryavir", aary, None)):
        tr = trajectory(dl); poster(P, dl, tr, follow_cam(tr, -50, 45 if "u19" in tag else 28), "catch", OUT + f"swiss_{tag}.png")
    print("ok")
