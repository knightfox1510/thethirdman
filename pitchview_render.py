"""3D renderer + Swiss-style poster layout for pitchview.Delivery (mock-ups for the pitch-view Reel; the engine scene will reuse the same geometry).
    python3 pitchview_render.py            writes deliver/_pitchview_mockups/v2/*.png (+ an animated catch)
Camera: Cam(target, yaw, elevation, distance). yaw 0 = behind the bowler looking down the pitch; 90 = side-on; 180 = behind the batter.
Everything not in the data is labelled 'illustrative' on the poster (see pitchview.py: DATA vs MODEL)."""
import math, os, subprocess, glob
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pitchview import *
from pitchview_situations import classify, situation, sector_name

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


class LookCam(Cam):
    """A camera placed at an eye position looking at a target (batter's-eye and keeper's-eye views)."""
    def __init__(s, eye, target, F=1500, cx=W / 2, cy=380):
        s.C = np.array(eye, float); f = np.array(target, float) - s.C; s.f = f / np.linalg.norm(f); r = np.cross(s.f, [0, 0, 1.0]); s.r = r / np.linalg.norm(r); s.u = np.cross(s.r, s.f); s.F, s.cx, s.cy = F, cx, cy


def mix(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def scene(P, cam, dl, tr, S=1.5, size=(W, 760), show_gate=True, ball_xyz=None, fielder_xyz=None, trail=1.0, throw_trail=1.0):
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
    if tr.get("rope"):                                               # boundary rope (assumed radius, labelled)
        line3([(BOUNDARY_M * math.cos(a / 120 * 2 * math.pi), PL / 2 + BOUNDARY_M * math.sin(a / 120 * 2 * math.pi), 0) for a in range(121)], P["muted"], 4, dash=3)
    if tr.get("overstep"):                                           # the front foot over the bowler's crease (distance illustrative)
        line3([(-0.15, 1.22, 0.0), (0.25, 1.22 - 0.25, 0.0)], P["accent"], 14)
    if tr.get("batter_adv"):                                         # a batter who has come down the track
        ax = 0.55 * hand; ay = gy - tr["batter_adv"]
        line3([(ax, ay, 0), (ax, ay, H_ - 0.3)], P["fig"], 9); dot((ax, ay, H_ - 0.12), 0.12, outline=P["fig"], width=int(5 * S)); line3([(ax, ay + 0.2, 0.0), (ax + 0.3 * hand, ay - 0.35, 0.0)], P["fig"], 7)
        label((ax, ay, H_ + 0.1), "BATTER (OUT OF HIS CREASE, ILLUSTRATIVE)", font("PlexMonoSB.ttf", 18), P["muted"], "la", dx=14, bg=P["bg"])
    pre, post, bat = tr["pre"], tr["post"], tr["bat"]
    line3(pre + post, P["accent"], 7)
    if tr.get("throw"):
        th = tr["throw"]; line3(th[:max(2, int(len(th) * throw_trail))], P["field"], 6, dash=2); e = th[-1]; dot(e, 0.35, outline=P["accent"], width=int(6 * S))
        if throw_trail >= 1.0: label((e[0], e[1], 0.0), "MISSED" if tr.get("kind") == "runout_miss" else "STUMPS BROKEN", font("PlexMonoSB.ttf", 20), P["accent"], "la", dx=16, dy=12, bg=P["bg"])
        if tr.get("missed_stumps"): ms_ = tr["missed_stumps"]; dot(ms_, 0.30, outline=P["field"], width=int(4 * S))
    if tr.get("gloves"): dot(tr["gloves"], 0.30, outline=P["field"], width=int(6 * S)); label(tr["gloves"], "GLOVES", font("PlexMonoSB.ttf", 20), P["field"], "la", dx=16, dy=-6, bg=P["bg"])
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
        kind_ = tr.get("kind", "caught")
        if kind_ == "dropped": label((cx_, cy_, 0.02), "DROPPED", font("PlexMonoSB.ttf", 21), P["accent"], "la", dx=18, dy=34, bg=P["bg"])
        if kind_ == "caught": label((cx_, cy_, 0.02), "CATCH" if not f.get("approx") else "CATCH (APPROX.)", font("PlexMonoSB.ttf", 21), P["accent"], "la", dx=18, dy=34, bg=P["bg"])
    if tr.get("cross"):                                              # a dropped chance: a cross where the ball went down
        cxm = tr["cross"]; line3([(cxm[0] - .5, cxm[1] - .5, cxm[2]), (cxm[0] + .5, cxm[1] + .5, cxm[2])], P["accent"], 8); line3([(cxm[0] - .5, cxm[1] + .5, cxm[2]), (cxm[0] + .5, cxm[1] - .5, cxm[2])], P["accent"], 8)
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


def poster(P, dl, tr, cam, out, S=1.5, ball_xyz=None, fielder_xyz=None, trail=1.0, caption=None, match=None, throw_trail=1.0):
    sit = situation(dl, tr)
    """Swiss layout: hairline rules, the ball number, a 3D picture, a side-on bounce panel, three facts, the result in words, and the 'illustrative' note."""
    sm, _ = scene(P, cam, dl, tr, S=S, size=(W, 760), show_gate=(sit["kind"] in ("bowled", "lbw", "ball", "wide", "no_ball", "dropped", "misfield") and cam.F > 1800), ball_xyz=ball_xyz, fielder_xyz=fielder_xyz, trail=trail, throw_trail=throw_trail)
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
    res_ = {"caught": "CAUGHT", "bowled": "BOWLED", "lbw": "LBW", "stumped": "STUMPED", "run_out": "RUN OUT"}
    d.text((X(60), X(yb)), sit["big"], font=font("OswaldBold.ttf", 92 if len(sit["big"]) < 9 else 70), fill=P["accent"], anchor="la")
    f_ = font("Inter-Medium.otf", 27); lines = []
    if sit["kind"] in ("caught", "bowled", "lbw"):
        lines = wrap(sm_["where"][0].upper() + sm_["where"][1:] + ".", f_, 520)
        if sit["kind"] == "caught" and tr.get("field") and tr["field"].get("exceptional"): lines += wrap("A demanding catch: the commentary describes a dive.", f_, 520)
        if tr["stump_z"] is not None and sit["kind"] in ("bowled", "lbw"): lines += wrap(f"Model: {tr['stump_z']:.2f} m at the stumps, under their 0.71 m.", f_, 520)
        lines += [f"Shot: {sm_['shot']}. Control: {sm_['control']}."]
    else:
        for ln in sit["lines"]: lines += wrap(ln, f_, 520)
        if sit["kind"] not in ("ball", "wide", "no_ball"): lines += [f"Shot: {sm_['shot']}. Control: {sm_['control']}."]
    for tg in sit["tags"]: lines += wrap(tg.capitalize() + ".", font("Inter-Medium.otf", 22), 540)
    small = len(lines) > 6; f2 = font("Inter-Medium.otf", 23 if small else 27)
    for j, ln in enumerate(lines[:10]): d.text((X(500), X(yb + 4 + j * (28 if small else 34))), ln, font=f2, fill=P["ink"], anchor="la")
    foot = [f"MOCK-UP · ILLUSTRATIVE: bounce, height, arcs and the fielder's move are modelled ({dl.pace_kmh:.0f} km/h, {dl.batter_h:.2f} m batter).", "From the data: zones, shot, control, dismissal, catcher. From commentary (leads): fielding position, speed, how it behaved."]
    for i, ln in enumerate(foot): d.text((X(60), X(1846 + i * 26)), ln, font=font("PlexMono.ttf", 16), fill=P["muted"], anchor="la")
    if caption: d.text((X(W // 2), X(1290)), caption, font=font("OswaldBold.ttf", 34), fill=P["ink"], anchor="mm")
    im.resize((W, H), Image.LANCZOS).save(out)


def animate(P, dl, tr, out_mp4, match, seconds=6.0, fps=24, S=1.0, orbit=(-64, -26)):
    """Silent preview, 720x1280: the delivery (slowed), then what happened next, with the camera orbiting slowly.
    Catch: ball off the bat while the fielder moves to the catch. Run out: ball to the fielder, then the throw, then the stumps. Boundary: the ball to the rope. Others: the delivery and its result."""
    sit = situation(dl, tr); fr = out_mp4[:-4] + "_frames/"; os.makedirs(fr, exist_ok=True)
    for f in glob.glob(fr + "*.png"): os.remove(f)
    n = int(seconds * fps); delivery = tr["pre"] + tr["post"]; bat = tr["bat"]; throw = tr.get("throw") or []; fp = fielder_path(tr["field"]) if (tr.get("field") and tr["field"].get("moved_m", 0) > 0.2) else []
    w_del, w_bat, w_thr = 0.34, (0.36 if bat else 0.0), (0.22 if throw else 0.0)
    for i in range(n):
        t = i / (n - 1); yaw = orbit[0] + (orbit[1] - orbit[0]) * t; cam = follow_cam(tr, yaw, 30)
        a1 = min(1.0, t / w_del); ball = delivery[int(a1 * (len(delivery) - 1))]; trail = 1.0 if not bat else 0.0; thr = 1.0 if not throw else 0.0; fx = None
        if t > w_del and bat:
            a2 = min(1.0, (t - w_del) / w_bat); ball = bat[int(a2 * (len(bat) - 1))]; trail = max(0.05, a2)
            if fp: fx = fp[min(len(fp) - 1, int(a2 * (len(fp) - 1)))]
        if t > w_del + w_bat and throw:
            a3 = min(1.0, (t - w_del - w_bat) / w_thr); ball = throw[int(a3 * (len(throw) - 1))]; thr = max(0.05, a3); trail = 1.0
        if t > w_del + w_bat + w_thr: trail, thr = 1.0, 1.0
        if t <= w_del: trail = 0.0 if bat else 1.0; thr = 0.0 if throw else 1.0
        poster(P, dl, tr, cam, fr + f"f{i:03d}.png", S=S, ball_xyz=ball, fielder_xyz=fx, trail=max(trail, 0.02) if bat else 1.0, throw_trail=thr if throw else 1.0, match=match)
        Image.open(fr + f"f{i:03d}.png").resize((720, 1280), Image.LANCZOS).save(fr + f"f{i:03d}.png")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(fps), "-i", fr + "f%03d.png", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", out_mp4], check=True)
    for f in glob.glob(fr + "*.png"): os.remove(f)
    os.rmdir(fr)


def _header(d, P, X, match, title_big, sub_right):
    d.line([X(60), X(96), X(W - 60), X(96)], fill=P["rule"], width=X(4))
    d.text((X(60), X(124)), "THE THIRD MAN · INSIGHTS", font=font("PlexMonoSB.ttf", 24), fill=P["muted"], anchor="la"); d.text((X(W - 60), X(124)), (match or "").upper(), font=font("PlexMonoSB.ttf", 24), fill=P["muted"], anchor="ra")
    d.text((X(60), X(170)), title_big, font=font("OswaldBold.ttf", 150), fill=P["accent"], anchor="la")
    for i, ln in enumerate(sub_right): d.text((X(W - 60), X(190 + i * 66)), ln, font=font("OswaldBold.ttf", 56), fill=P["ink"], anchor="ra")


def _ground(d, P, X, cx, cy, sc, with_rope=True):
    """Top-down ground, bowler's end at the top: the 30-yard circle as one clear ring, the (approximate) rope, the pitch."""
    if with_rope: d.ellipse([X(cx - BOUNDARY_M * sc), X(cy - BOUNDARY_M * sc), X(cx + BOUNDARY_M * sc), X(cy + BOUNDARY_M * sc)], outline=P["muted"], width=X(3))
    d.ellipse([X(cx - 27.43 * sc), X(cy - 27.43 * sc), X(cx + 27.43 * sc), X(cy + 27.43 * sc)], outline=P["circle"], width=X(4))
    d.text((X(cx), X(cy - 27.43 * sc - 6)), "30-YARD CIRCLE", font=font("PlexMonoSB.ttf", 16), fill=P["circle"], anchor="ms")
    if with_rope: d.text((X(cx), X(cy - BOUNDARY_M * sc - 6)), f"BOUNDARY (APPROX. {BOUNDARY_M:.0f} m)", font=font("PlexMonoSB.ttf", 16), fill=P["muted"], anchor="ms")
    d.rectangle([X(cx - PW / 2 * sc), X(cy - PL / 2 * sc), X(cx + PW / 2 * sc), X(cy + PL / 2 * sc)], fill=P["pitch"], outline=P["line"], width=X(2))


def wagon_poster(P, df, out, title, who, match, hand="R", S=1.5):
    """Where the runs went (data only): every recorded shot from the batter's end to its wagon-wheel spot; fours and sixes heavier. Works for an over, a spell, a batter's innings or a whole match (pass a DataFrame slice)."""
    im = Image.new("RGB", (int(W * S), int(H * S)), P["bg"]); d = ImageDraw.Draw(im); X = lambda v: int(v * S)
    _header(d, P, X, match, title, who)
    cx, cy, sc = W / 2, 790, 440 / (BOUNDARY_M * 1.02); _ground(d, P, X, cx, cy, sc)
    sh = df[(df.wagon_x > 0) & (df.runs > 0) | (df.wicket == True) & (df.wagon_x > 0)]
    base = (cx, cy + PL / 2 * sc - 0)
    for _, r in sh.iterrows():
        ex, ey = wagon_world(r.wagon_x, r.wagon_y); px, py = cx + ex * sc, cy + (ey - PL / 2) * sc
        runs = int(r.bat_runs); wk = bool(r.wicket)
        col = P["accent"] if (runs >= 4 or wk) else P["ink"]; w = 7 if runs == 6 else 5 if runs == 4 else 2
        d.line([X(cx), X(cy + PL / 2 * sc), X(px), X(py)], fill=col, width=X(w))
        if wk: d.ellipse([X(px - 9), X(py - 9), X(px + 9), X(py + 9)], fill=P["ink"], outline=P["accent"], width=X(3))
        elif runs >= 4: d.ellipse([X(px - 7), X(py - 7), X(px + 7), X(py + 7)], fill=col)
    side_off, side_leg = (0, 0)
    for _, r in sh.iterrows():
        leg = (r.wagon_x > 180) if hand == "R" else (r.wagon_x < 180); runs = int(r.bat_runs)
        if leg: side_leg += runs
        else: side_off += runs
    tot = int(df.bat_runs.sum()); b4 = int((df.four == True).sum()); b6 = int((df.six == True).sum()); wk = int((df.wicket == True).sum()); balls = int((df.legal == True).sum())
    y0 = 1330; d.line([X(60), X(y0), X(W - 60), X(y0)], fill=P["rule"], width=X(3)); cw = (W - 120) / 4
    for i, (k, v) in enumerate([("RUNS OFF THE BAT", str(tot)), ("BALLS", str(balls)), ("FOURS · SIXES", f"{b4} · {b6}"), ("WICKETS", str(wk))]):
        x = 60 + i * cw; d.text((X(x), X(y0 + 22)), k, font=font("PlexMonoSB.ttf", 19), fill=P["muted"], anchor="la"); d.text((X(x), X(y0 + 56)), v, font=font("OswaldBold.ttf", 64), fill=P["ink"], anchor="la")
    d.line([X(60), X(y0 + 150), X(W - 60), X(y0 + 150)], fill=P["rule"], width=X(3)); f_ = font("Inter-Medium.otf", 29)
    d.text((X(60), X(y0 + 175)), f"Off side {side_off} runs · leg side {side_leg} runs (recorded shots).", font=f_, fill=P["ink"], anchor="la")
    d.text((X(60), X(y0 + 218)), "Red line = a boundary or a wicket. The line ends at the wagon-wheel spot; the rope radius is approximate.", font=font("Inter-Medium.otf", 24), fill=P["muted"], anchor="la")
    d.text((X(60), X(1846)), "FROM THE DATA: Cricinfo capture (wagon wheel, runs, wickets). Positions are approximate (wagon grid scale assumed).", font=font("PlexMono.ttf", 16), fill=P["muted"], anchor="la")
    im.resize((W, H), Image.LANCZOS).save(out)


def over_poster(P, df, out, title, who, match, S=1.5):
    """An over (or any six balls) on one page, data only: where each ball pitched (line and length zones), how it ended and who was in control."""
    im = Image.new("RGB", (int(W * S), int(H * S)), P["bg"]); d = ImageDraw.Draw(im); X = lambda v: int(v * S)
    _header(d, P, X, match, title, who)
    rows = list(df.head(6).itertuples()); cw, chh = 320, 480
    for i, r in enumerate(rows):
        x0 = 60 + (i % 3) * (cw + 20); y0 = 340 + (i // 3) * (chh + 24)
        wk = bool(r.wicket); d.rounded_rectangle([X(x0), X(y0), X(x0 + cw), X(y0 + chh)], radius=X(6), outline=P["accent"] if wk else P["muted"], width=X(4 if wk else 2))
        d.text((X(x0 + 14), X(y0 + 12)), f"BALL {i + 1}", font=font("PlexMonoSB.ttf", 20), fill=P["muted"], anchor="la")
        chip = {1: "OUT", 2: "OUT"}.get(0, ""); label_ = "OUT" if wk else (f"{int(r.runs)}" if r.runs else "·")
        d.text((X(x0 + cw - 14), X(y0 + 6)), label_, font=font("OswaldBold.ttf", 44), fill=P["accent"] if (wk or r.runs >= 4) else P["ink"], anchor="ra")
        px0, px1, py0, py1 = x0 + cw / 2 - 52, x0 + cw / 2 + 52, y0 + 70, y0 + chh - 120
        d.rectangle([X(px0), X(py0), X(px1), X(py1)], fill=P["pitch"], outline=P["line"], width=X(2))
        for frac in (.2, .4, .6, .8): d.line([X(px0), X(py0 + (py1 - py0) * frac), X(px1), X(py0 + (py1 - py0) * frac)], fill=mix(P["muted"], P["bg"], .5), width=X(1))
        dl = type("D", (), dict(line=r.pitch_line, hand="R", wide=False))(); lx = line_x(dl); L = LEN_FROM_STUMPS.get(r.pitch_length)
        if L is not None:
            y = py0 + (py1 - py0) * (1 - L / PL) ; x = x0 + cw / 2 + lx / (PW / 2) * 50
            d.ellipse([X(x - 12), X(y - 12), X(x + 12), X(y + 12)], fill=P["accent"] if wk else P["ink"], outline=P["bg"], width=X(2))
        d.text((X(x0 + cw / 2), X(y1 := py1 + 14)), LEN_LABEL.get(r.pitch_length, r.pitch_length).title(), font=font("OswaldBold.ttf", 26), fill=P["ink"], anchor="ma")
        d.text((X(x0 + cw / 2), X(y1 + 36)), LINE_LABEL.get(r.pitch_line, r.pitch_line).title(), font=font("Inter-Medium.otf", 22), fill=P["ink"], anchor="ma")
        d.text((X(x0 + cw / 2), X(y1 + 66)), (str(r.shot).replace("_", " ").title() + (" · in control" if r.control == 1 else " · not in control")), font=font("PlexMono.ttf", 15), fill=P["muted"], anchor="ma")
    n = len(rows); wk = sum(bool(r.wicket) for r in rows); runs = sum(int(r.runs) for r in rows); short = sum(r.pitch_length in ("SHORT", "SHORT_OF_A_GOOD_LENGTH") for r in rows); nic = sum(int(r.control) == 2 for r in rows)
    y0 = 1400; d.line([X(60), X(y0), X(W - 60), X(y0)], fill=P["rule"], width=X(3)); f_ = font("Inter-Medium.otf", 30)
    for j, ln in enumerate([f"{wk} wicket{'s' if wk != 1 else ''}, {runs} run{'s' if runs != 1 else ''} in {n} balls.", f"{short} of {n} balls were short of a good length or shorter; the batter was not in control of {nic}.", "Data only: where each ball pitched is the Cricinfo line and length zone; spots within a zone are drawn at its centre."]): d.text((X(60), X(y0 + 30 + j * 52)), ln, font=f_ if j < 2 else font("Inter-Medium.otf", 24), fill=P["ink"] if j < 2 else P["muted"], anchor="la")
    d.text((X(60), X(1846)), "FROM THE DATA: Cricinfo capture (line, length, shot, control, runs, wickets).", font=font("PlexMono.ttf", 16), fill=P["muted"], anchor="la")
    im.resize((W, H), Image.LANCZOS).save(out)


def field_poster(P, comments, inning, over, df, out, title, who, match, hand="R", S=1.5):
    """The field as the commentary describes it for one over: every fielding position it names, placed on the ground (typical spots, mirrored for left-handers), with the shots' directions as thin lines.
    This is NOT a full field: only fielders the commentary mentions appear, and the poster says so."""
    from pitchview_text import ball_text
    im = Image.new("RGB", (int(W * S), int(H * S)), P["bg"]); d = ImageDraw.Draw(im); X = lambda v: int(v * S)
    _header(d, P, X, match, title, who); cx, cy, sc = W / 2, 790, 440 / (BOUNDARY_M * 1.02); _ground(d, P, X, cx, cy, sc)
    seen = {}
    for i in range(1, 7):
        f = ball_text(comments, inning, round(over + i / 10.0, 1))
        for key in ("position", "shot_to"):
            pos = f.get(key)
            if pos in POSITIONS and pos not in ("bowler", "keeper"): seen.setdefault(pos, i)
    for _, r in df.iterrows():
        if r.wagon_x > 0:
            ex, ey = wagon_world(r.wagon_x, r.wagon_y); d.line([X(cx), X(cy + PL / 2 * sc), X(cx + ex * sc), X(cy + (ey - PL / 2) * sc)], fill=mix(P["muted"], P["bg"], .4), width=X(2))
    for pos, i in seen.items():
        x, y = spot(pos, hand); px, py = cx + x * sc, cy + (y - PL / 2) * sc
        d.ellipse([X(px - 9), X(py - 9), X(px + 9), X(py + 9)], fill=P["ink"]); d.text((X(px + 14), X(py)), pos.upper(), font=font("PlexMonoSB.ttf", 17), fill=P["ink"], anchor="lm")
    y0 = 1330; d.line([X(60), X(y0), X(W - 60), X(y0)], fill=P["rule"], width=X(3))
    d.text((X(60), X(y0 + 28)), f"{len(seen)} fielding position{'s' if len(seen) != 1 else ''} named by the commentary for this over.", font=font("Inter-Medium.otf", 30), fill=P["ink"], anchor="la")
    d.text((X(60), X(y0 + 76)), "This is not the full field: only fielders the commentary mentions appear. Spots are typical for each position.", font=font("Inter-Medium.otf", 24), fill=P["muted"], anchor="la")
    d.text((X(60), X(1846)), "LEADS: Cricbuzz commentary (positions named); DATA: Cricinfo wagon wheel (shot lines). Positions are typical spots, not measured.", font=font("PlexMono.ttf", 16), fill=P["muted"], anchor="la")
    im.resize((W, H), Image.LANCZOS).save(out)


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
