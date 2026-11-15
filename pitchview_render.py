"""3D renderer + Swiss-style poster layout for pitchview.Delivery (mock-ups for the pitch-view Reel; the engine scene will reuse the same geometry).
    python3 pitchview_render.py            writes deliver/_pitchview_mockups/v2/*.png (+ an animated catch)
Camera: Cam(target, yaw, elevation, distance). yaw 0 = behind the bowler looking down the pitch; 90 = side-on; 180 = behind the batter.
Everything not in the data is labelled 'illustrative' on the poster (see pitchview.py: DATA vs MODEL)."""
import math, os, subprocess, glob
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pitchview import *

FONTS = "fonts/"
font = lambda n, s: ImageFont.truetype(FONTS + n, max(1, int(s)))
W, H = 1080, 1920
PALS = {
    "swiss": dict(name="Swiss mono", bg=(246, 246, 242), ground=(232, 232, 226), grid=(222, 222, 216), pitch=(255, 255, 255), band=[(236, 236, 236), (244, 244, 244), (255, 255, 255), (244, 244, 244), (236, 236, 236)],
                  ink=(16, 16, 16), line=(24, 24, 24), accent=(226, 30, 30), muted=(112, 112, 106), rule=(16, 16, 16), fig=(60, 60, 60), circle=(40, 40, 40), field=(16, 16, 16)),
    "red_soil_swiss": dict(name="Red soil, Swiss layout", bg=(244, 236, 224), ground=(222, 198, 172), grid=(212, 186, 158), pitch=(204, 132, 88), band=[(186, 112, 72), (196, 122, 80), (204, 132, 88), (214, 146, 100), (224, 160, 116)],
                           ink=(26, 18, 14), line=(255, 244, 224), accent=(176, 52, 28), muted=(122, 96, 78), rule=(26, 18, 14), fig=(52, 36, 28), circle=(120, 70, 44), field=(26, 18, 14)),
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


def scene(P, cam, dl, tr, S=1.5, size=(W, 760), show_gate=True, ball_xyz=None, fielder_xyz=None, trail=1.0):
    """The 3D picture. ball_xyz / fielder_xyz place the moving ball and the moving fielder (for the animation); trail < 1 draws only that fraction of the off-the-bat arc."""
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

    def dot(pt, r_m, **k):
        q = cam.p(pt)
        if q: r = max(7, r_m * cam.F / q[2]); d.ellipse([(q[0] - r) * S, (q[1] - r) * S, (q[0] + r) * S, (q[1] + r) * S], **k)
        return q

    def label(pt, text, f, fill, anchor="la", dx=0, dy=0, bg=None):
        q = cam.p(pt)
        if not q: return
        x, y = q[0] * S + dx * S, q[1] * S + dy * S
        if bg: bb = d.textbbox((x, y), text, font=f, anchor=anchor); d.rectangle([bb[0] - 6 * S, bb[1] - 3 * S, bb[2] + 6 * S, bb[3] + 3 * S], fill=bg)
        d.text((x, y), text, font=f, fill=fill, anchor=anchor)

    poly([(-90, -40, 0), (90, -40, 0), (90, PL + 90, 0), (-90, PL + 90, 0)], fill=P["ground"])
    for gx in range(-90, 91, 10): line3([(gx, -40, 0), (gx, PL + 90, 0)], P["grid"], 1)
    for gy in range(-40, int(PL) + 91, 10): line3([(-90, gy, 0), (90, gy, 0)], P["grid"], 1)
    ring = [(27.43 * math.cos(a / 90 * 2 * math.pi), PL / 2 + 27.43 * math.sin(a / 90 * 2 * math.pi), 0) for a in range(91)]
    line3(ring, P["circle"], 3)                                                                                 # the 30-yard circle: one continuous line, clearly visible
    
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
        bxx = 0.55 * hand; head = (bxx, gy - 0.1, H_ - 0.12)
        line3([(bxx, gy - 0.1, 0), (bxx, gy - 0.1, H_ - 0.3)], P["fig"], 9); line3([(bxx, gy - 0.1, 0.9), (bxx - 0.25 * hand, gy - 0.5, 0.55)], P["fig"], 7)
        dot(head, 0.12, outline=P["fig"], width=int(5 * S)); line3([(bxx + 0.05 * hand, gy - 0.4, 0.5), (bxx - 0.18 * hand, gy - 0.9, 0.25)], P["accent"], 6)
    pre, post, bat = tr["pre"], tr["post"], tr["bat"]
    line3(pre + post, P["accent"], 7)
    if tr["bounce"]:
        bx_, by_, _ = tr["bounce"]; line3([(bx_ + 0.9 * math.cos(a / 24 * 2 * math.pi), by_ + 0.9 * math.sin(a / 24 * 2 * math.pi), 0) for a in range(25)], P["accent"], 4)
    if show_gate: dot((tr["contact"][0], gy, tr["gate_z"]), 0.16, fill=P["accent"], outline=P["bg"], width=int(3 * S))
    f = tr.get("field")
    if bat: line3(bat[:max(2, int(len(bat) * trail))], P["accent"], 5, dash=2)
    if f:                                                            # fielder: where he started (hollow), his move (solid line with arrow), where the catch was taken (filled ring)
        (sx, sy), (cx_, cy_) = f["start"], f["catch"]
        if f.get("moved_m", 0) > 0.2 and not f.get("approx"):
            line3([(x, y, 0.02) for x, y, _ in fielder_path(f)], P["field"], 6)
            dx, dy = cx_ - sx, cy_ - sy; nrm = math.hypot(dx, dy) or 1; ux, uy = dx / nrm, dy / nrm
            line3([(cx_ - ux * 0.5 - uy * 0.3, cy_ - uy * 0.5 + ux * 0.3, 0.02), (cx_, cy_, 0.02), (cx_ - ux * 0.5 + uy * 0.3, cy_ - uy * 0.5 - ux * 0.3, 0.02)], P["field"], 6)
        dot((sx, sy, 0.02), 0.45, outline=P["field"], width=int(5 * S))
        dot((cx_, cy_, 0.02), 0.28, fill=P["accent"], outline=P["field"], width=int(3 * S))
        q0 = cam.p((sx, sy, 0.02)); left_side = q0 and q0[0] < 380
        label((sx, sy, 0.02), (f["name"] or "fielder").upper() + " · " + f["position"].upper(), font("PlexMonoSB.ttf", 22), P["ink"], "la" if left_side else "ra", dx=22 if left_side else -22, dy=-4, bg=P["bg"])
        label((cx_, cy_, 0.02), "CATCH" if not f.get("approx") else "CATCH (APPROX.)", font("PlexMonoSB.ttf", 21), P["accent"], "la", dx=18, dy=34, bg=P["bg"])
    if ball_xyz: dot(ball_xyz, 0.17, fill=P["ink"])
    if fielder_xyz: dot(fielder_xyz, 0.42, fill=P["field"])
    return im, cam


def follow_cam(tr, yaw=-50, el=30):
    """Frames the ball's journey off the bat so the whole pitch, the bat contact, the fielder's start and the catch fit: pick the distance so the picture spans ~78% of the width, then centre it."""
    a, b = tr["contact"], tr["end"] or tr["contact"]; keys = [(-PW / 2, 0, 0), (PW / 2, PL, 0), a, b]
    if tr.get("field"): keys += [(*tr["field"]["start"], 0), (*tr["field"]["catch"], 0)]
    mid = (sum(k[0] for k in keys) / len(keys), sum(k[1] for k in keys) / len(keys), 0.5); R = 40.0
    for _ in range(3):
        cam = Cam(mid, yaw, el, R, F=1700, cy=400); pts = [q for q in (cam.p(k) for k in keys) if q]
        w = max(q[0] for q in pts) - min(q[0] for q in pts); h = max(q[1] for q in pts) - min(q[1] for q in pts)
        R *= max(w / (0.74 * W), h / 520.0)
    cam = Cam(mid, yaw, el, R, F=1700, cy=400); pts = [q for q in (cam.p(k) for k in keys) if q]
    xs, ys = [q[0] for q in pts], [q[1] for q in pts]; cam.cx += W / 2 - (min(xs) + max(xs)) / 2; cam.cy += 380 - (min(ys) + max(ys)) / 2
    return cam


def profile(d, P, dl, tr, X, y_top, h):
    """Side-on view of the delivery: ball height along the pitch against the stumps and the batter's own height. This is the 'where did it bounce and how high did it come through' panel."""
    x0, x1 = 80, W - 80; base = y_top + h - 34; scale = (h - 74) / 2.4; px = lambda y: x0 + (x1 - x0) * y / PL; pz = lambda z: base - z * scale
    d.text((X(60), X(y_top)), "SIDE-ON · THE BOUNCE", font=font("PlexMonoSB.ttf", 21), fill=P["muted"], anchor="la")
    d.line([X(x0), X(base), X(x1), X(base)], fill=P["ink"], width=X(3))
    sx = px(PL); d.rectangle([X(sx - 4), X(pz(.71)), X(sx + 4), X(base)], fill=P["ink"]); d.line([X(sx - 60), X(pz(.71)), X(sx + 18), X(pz(.71))], fill=P["muted"], width=X(2))
    d.text((X(sx + 22), X(pz(.71))), "STUMPS .71 m", font=font("PlexMono.ttf", 17), fill=P["muted"], anchor="lm")
    cx_ = px(PL - 1.22); d.line([X(cx_), X(base), X(cx_), X(pz(dl.batter_h))], fill=P["fig"], width=X(5)); d.ellipse([X(cx_ - 11), X(pz(dl.batter_h) - 20), X(cx_ + 11), X(pz(dl.batter_h) + 2)], outline=P["fig"], width=X(4))
    d.text((X(cx_ - 20), X(pz(dl.batter_h) + 6)), f"{dl.batter_h:.2f} m", font=font("PlexMono.ttf", 17), fill=P["muted"], anchor="ra")
    pts = tr["pre"] + tr["post"]; d.line([(X(px(y)), X(pz(z))) for _, y, z in pts], fill=P["accent"], width=X(5), joint="curve")
    if tr["bounce"]:
        by = tr["bounce"][1]; d.ellipse([X(px(by) - 9), X(base - 9), X(px(by) + 9), X(base + 9)], fill=P["accent"])
        d.text((X(px(by)), X(base + 14)), f"PITCHES {PL - by:.1f} m FROM THE STUMPS", font=font("PlexMonoSB.ttf", 17), fill=P["ink"], anchor="ma")
    gz = tr["gate_z"]; d.ellipse([X(cx_ - 9), X(pz(gz) - 9), X(cx_ + 9), X(pz(gz) + 9)], fill=P["ink"])
    d.text((X(cx_ - 20), X(pz(gz))), f"{gz:.2f} m", font=font("PlexMonoSB.ttf", 19), fill=P["ink"], anchor="rm")
    if dl.bounce == "low": d.text((X(px(PL * .30)), X(pz(1.0))), "KEPT LOW", font=font("OswaldBold.ttf", 34), fill=P["accent"], anchor="ma")
    elif dl.bounce == "extra": d.text((X(px(PL * .62)), X(pz(1.25))), "EXTRA BOUNCE", font=font("OswaldBold.ttf", 34), fill=P["accent"], anchor="ma")


def field_plan(d, P, dl, tr, X, x0, y0, size=300):
    """Top-down plan of the ground: the pitch, the 30-yard circle (one clear ring), the fielder's start, his move and the catch spot, and the ball's path off the bat. Always readable, whatever the 3D zoom."""
    f = tr.get("field"); pts = [(0, 0), (0, PL)] + ([f["start"], f["catch"]] if f else []) + ([tr["end"][:2]] if tr["end"] else [])
    ext = max(34.0, max(max(abs(p[0]), abs(p[1] - PL / 2)) for p in pts) + 6); sc = (size / 2 - 14) / ext; cx, cy = x0 + size / 2, y0 + size / 2
    m = lambda x, y: (cx + x * sc, cy + (y - PL / 2) * sc)                          # bowler's end at the top, as in the 3D views
    d.rectangle([X(x0), X(y0), X(x0 + size), X(y0 + size)], fill=mix(P["bg"], P["ground"], .6), outline=P["rule"], width=X(2))
    d.ellipse([X(cx - 27.43 * sc), X(cy - 27.43 * sc), X(cx + 27.43 * sc), X(cy + 27.43 * sc)], outline=P["circle"], width=X(4))
    d.text((X(cx), X(cy - 27.43 * sc - 4)), "30-YARD CIRCLE", font=font("PlexMonoSB.ttf", 14), fill=P["circle"], anchor="ms")
    (a, b), (c, e) = m(-PW / 2, 0), m(PW / 2, PL); d.rectangle([X(a), X(b), X(c), X(e)], fill=P["pitch"], outline=P["line"], width=X(2))
    if dl.hand == "R": d.text((X(x0 + 8), X(y0 + 8)), "OFF SIDE", font=font("PlexMono.ttf", 13), fill=P["muted"], anchor="la"); d.text((X(x0 + size - 8), X(y0 + 8)), "LEG SIDE", font=font("PlexMono.ttf", 13), fill=P["muted"], anchor="ra")
    else: d.text((X(x0 + 8), X(y0 + 8)), "LEG SIDE", font=font("PlexMono.ttf", 13), fill=P["muted"], anchor="la"); d.text((X(x0 + size - 8), X(y0 + 8)), "OFF SIDE", font=font("PlexMono.ttf", 13), fill=P["muted"], anchor="ra")
    if tr["bat"]: d.line([(X(m(x, y)[0]), X(m(x, y)[1])) for x, y, _ in tr["bat"]], fill=P["accent"], width=X(3))
    if f:
        s0, c0 = m(*f["start"]), m(*f["catch"])
        d.ellipse([X(s0[0] - 8), X(s0[1] - 8), X(s0[0] + 8), X(s0[1] + 8)], outline=P["field"], width=X(3))
        if f.get("moved_m", 0) > 0.2: d.line([X(s0[0]), X(s0[1]), X(c0[0]), X(c0[1])], fill=P["field"], width=X(3))
        d.ellipse([X(c0[0] - 6), X(c0[1] - 6), X(c0[0] + 6), X(c0[1] + 6)], fill=P["accent"], outline=P["field"], width=X(2))


def wrap(text, f, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if f.getlength(t) <= width: cur = t
        else: lines.append(cur); cur = w
    return lines + [cur] if cur else lines


def poster(P, dl, tr, cam, out, S=1.5, ball_xyz=None, fielder_xyz=None, trail=1.0, caption=None, match=None):
    """Swiss layout: hairline rules, the ball number, a 3D picture, a side-on bounce panel, three facts, the result in words, and the 'illustrative' note."""
    sm, _ = scene(P, cam, dl, tr, S=S, size=(W, 760), show_gate=(not dl.how == "caught"), ball_xyz=ball_xyz, fielder_xyz=fielder_xyz, trail=trail)
    im = Image.new("RGB", (int(W * S), int(H * S)), P["bg"]); d = ImageDraw.Draw(im); X = lambda v: int(v * S)
    im.paste(sm, (0, X(330)))
    d.line([X(60), X(96), X(W - 60), X(96)], fill=P["rule"], width=X(4))
    d.text((X(60), X(124)), "THE THIRD MAN · INSIGHTS", font=font("PlexMonoSB.ttf", 24), fill=P["muted"], anchor="la")
    d.text((X(W - 60), X(124)), (match or "").upper(), font=font("PlexMonoSB.ttf", 24), fill=P["muted"], anchor="ra")
    d.text((X(60), X(170)), f"{dl.over:.1f}".replace(".", "·"), font=font("OswaldBold.ttf", 170), fill=P["accent"], anchor="la")
    d.text((X(W - 60), X(190)), dl.bowler.upper(), font=font("OswaldBold.ttf", 56), fill=P["ink"], anchor="ra"); d.text((X(W - 60), X(256)), "TO  " + dl.batter.upper(), font=font("OswaldBold.ttf", 56), fill=P["ink"], anchor="ra")
    field_plan(d, P, dl, tr, X, W - 60 - 250, 345, 250)
    profile(d, P, dl, tr, X, 1110, 250)
    sm_ = summary(dl, tr); y0 = 1385
    d.line([X(60), X(y0), X(W - 60), X(y0)], fill=P["rule"], width=X(3))
    length = LEN_LABEL.get(tr["length_used"], tr["length_used"]).title(); sub = ""
    if tr["length_note"]:
        a = LEN_LABEL.get(dl.length_table or dl.length, "").title(); b = LEN_LABEL.get(dl.facts.get("length_text", ""), "").title()
        sub = f"Cricinfo: {a} · Cricbuzz: {b}" if tr["length_note"] == "conflict" else f"Table says {a}; fits {length}"
    res = (dl.how.upper() if dl.wicket else ("%d RUN%s" % (dl.runs, "" if dl.runs == 1 else "S")))
    cols = [("LENGTH", length, sub), ("LINE", sm_["line"].title(), ""), ("RESULT", res, "")]
    cw = (W - 120) / 3
    for i, (k, v, s2) in enumerate(cols):
        x = 60 + i * cw
        if i: d.line([X(x - 12), X(y0 + 18), X(x - 12), X(y0 + 150)], fill=P["muted"], width=X(1))
        d.text((X(x), X(y0 + 22)), k, font=font("PlexMonoSB.ttf", 21), fill=P["muted"], anchor="la")
        fs = 44 if len(v) < 14 else 32; d.text((X(x), X(y0 + 56)), v, font=font("OswaldBold.ttf", fs), fill=P["ink"], anchor="la")
        if s2:
            for j, ln in enumerate(wrap(s2, font("PlexMono.ttf", 15), cw - 30)): d.text((X(x), X(y0 + 108 + j * 20)), ln, font=font("PlexMono.ttf", 15), fill=P["accent"], anchor="la")
    d.line([X(60), X(y0 + 160), X(W - 60), X(y0 + 160)], fill=P["rule"], width=X(3))
    yb = y0 + 180
    big = {"caught": "CAUGHT", "bowled": "BOWLED", "lbw": "LBW", "stumped": "STUMPED", "run out": "RUN OUT"}.get(dl.how, "NO WICKET")
    d.text((X(60), X(yb)), big, font=font("OswaldBold.ttf", 92), fill=P["accent"], anchor="la")
    f_ = font("Inter-Medium.otf", 27); lines = wrap(sm_["where"][0].upper() + sm_["where"][1:] + ".", f_, 520)
    if dl.how == "caught" and tr.get("field") and tr["field"].get("exceptional"): lines += wrap("A demanding catch: the commentary describes a dive.", f_, 520)
    if tr["stump_z"] is not None and dl.how in ("bowled", "lbw"): lines += wrap(f"Model: {tr['stump_z']:.2f} m at the stumps, under their 0.71 m.", f_, 520)
    lines += [f"Shot: {sm_['shot']}. Control: {sm_['control']}."]
    for j, ln in enumerate(lines[:6]): d.text((X(500), X(yb + 4 + j * 36)), ln, font=f_, fill=P["ink"], anchor="la")
    foot = [f"MOCK-UP · ILLUSTRATIVE: bounce, height, arcs and the fielder's move are modelled ({dl.pace_kmh:.0f} km/h, {dl.batter_h:.2f} m batter).", "From the data: zones, shot, control, dismissal, catcher. From commentary (leads): fielding position, speed, how it behaved."]
    for i, ln in enumerate(foot): d.text((X(60), X(1846 + i * 26)), ln, font=font("PlexMono.ttf", 16), fill=P["muted"], anchor="la")
    if caption: d.text((X(W // 2), X(1290)), caption, font=font("OswaldBold.ttf", 34), fill=P["ink"], anchor="mm")
    im.resize((W, H), Image.LANCZOS).save(out)


def animate(P, dl, tr, out_mp4, match, seconds=5.0, fps=24, S=1.0):
    """The ball off the bat while the fielder moves from his start spot to the catch (a dive rises and drops). Silent preview, 720x1280."""
    cam = follow_cam(tr, -50, 32); n = int(seconds * fps); fr = out_mp4[:-4] + "_frames/"; os.makedirs(fr, exist_ok=True)
    for f in glob.glob(fr + "*.png"): os.remove(f)
    bat = tr["bat"]; fp = fielder_path(tr["field"]) if tr.get("field") else []
    for i in range(n):
        t = i / (n - 1); a = min(1.0, max(0.0, (t - 0.12) / 0.78)); k = int(a * (len(bat) - 1))
        ball = bat[k] if bat else None; fx = fp[min(len(fp) - 1, int(a * (len(fp) - 1)))] if fp else None
        poster(P, dl, tr, cam, fr + f"f{i:03d}.png", S=S, ball_xyz=ball, fielder_xyz=fx, trail=max(0.05, a), match=match)
        Image.open(fr + f"f{i:03d}.png").resize((720, 1280), Image.LANCZOS).save(fr + f"f{i:03d}.png")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(fps), "-i", fr + "f%03d.png", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", out_mp4], check=True)


if __name__ == "__main__":
    OUT = "deliver/_pitchview_mockups/v2/"; os.makedirs(OUT, exist_ok=True)
    T4 = ("data/cricinfo/nz_ind_4odi_balls.csv", "data/cricinfo/nz_ind_4odi.json"); CB = "data/cricbuzz/nz_ind_4odi.json"; M = "NZ v IND · 4th ODI"
    rohit = from_table(*T4, 2, 0.1, cricbuzz=CB); kohli = from_table(*T4, 2, 0.5, cricbuzz=CB); iyer = from_table(*T4, 2, 0.6, cricbuzz=CB)
    allen = from_table(*T4, 1, 30.2, cricbuzz=CB); seifert = from_table(*T4, 1, 11.6, cricbuzz=CB)
    for key, P in PALS.items():
        for tag, dl in (("rohit_first_slip", rohit), ("kohli_bowled_low", kohli), ("iyer_lbw", iyer), ("allen_short_cover_dive", allen), ("seifert_keeper", seifert)):
            tr = trajectory(dl)
            cam = follow_cam(tr, -50, 30) if dl.how == "caught" else Cam((0, PL - 1.0, 0.9), 24, 9, 9.5, cy=390)
            poster(P, dl, tr, cam, OUT + f"{key}_{tag}.png", match=M)
    P = PALS["swiss"]; tr = trajectory(allen); animate(P, allen, tr, OUT + "swiss_allen_catch_animated.mp4", M)
    print("ok")
