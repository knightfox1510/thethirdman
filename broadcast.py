"""Broadcast camera for The Third Man: a pseudo-3D "behind the bowler's arm" view (scene type "cam").
Real pitch geometry (20.12 m, stumps, creases) is projected with a pinhole camera that sits behind the umpire,
watches the run-up, follows the ball from the hand to the bounce to the batter, then closes in on the result.
Illustrated figures only (no likeness, no broadcast footage, no logos). Label scenes "Illustrative recreation".

Scene spec:
 {"type": "cam", "hand": "R"|"L", "bowler": {"kit": "NZ"}, "batter": {"kit": "IND"},
  "delivery": {"line": "OUTSIDE_OFFSTUMP", "length": "SHORT_OF_A_GOOD_LENGTH"},     # Cricinfo values
  "result": "bowled"|"lbw"|"caught"|"dot",
  "ball": {"at": .62 | "word": "bowled"},           # time of contact (fraction of the scene, or a spoken word)
  "split": true,                                    # lbw/any: bowler and batter side by side after the result
  "panel": {...}}                                   # same panel as stage scenes (headline, table, bignum ...)"""
import math
import skia
import gfx
import rig3d as R
from gfx import prog, eo, eio, clamp

E = None
PL = 20.12                       # pitch length, metres
LEN = {"YORKER": 1.0, "FULL": 3.4, "GOOD_LENGTH": 6.0, "SHORT_OF_A_GOOD_LENGTH": 7.6, "SHORT": 10.0}   # metres short of the batter's stumps
STUMP_H, STUMP_DX = .711, .1143
FLIGHT = .85                     # seconds from hand to batter (slowed for TV)


def lerp(a, b, f): return a + (b - a) * f


def _geom(s):
    hand = 1 if s.get("hand", "R") == "R" else -1
    off = -hand                                            # off side is camera-left for a right-hander
    d = s.get("delivery", {}); res = s.get("result", "dot")
    zb = PL - LEN.get(d.get("length", "GOOD_LENGTH"), 6.0)
    xb = {"ON_THE_STUMPS": 0.0, "OUTSIDE_OFFSTUMP": off * .34, "WIDE_OUTSIDE_OFFSTUMP": off * .9, "DOWN_LEG": -off * .45}.get(d.get("line", "ON_THE_STUMPS"), 0.0)
    T = {"bowled": (off * STUMP_DX, .5, PL), "lbw": (off * .05, .46, PL - .6), "caught": (off * .12, .8, PL - .55),
         "dot": (off * .55, .7, PL + 1.0)}[res]
    return hand, off, zb, xb, T


WAGON_C, BOUNDARY = 181.0, 65.0           # Cricinfo wagon grid centre (px) and an assumed boundary radius (m): positions are approximate


def wagon_to_world(wx, wy):
    """Cricinfo wagon (x across, y toward the bowler) -> world metres on the field. Verified: RH cover drives sit at low x, LH at high x."""
    return (wx - WAGON_C) / WAGON_C * BOUNDARY, PL - (wy - WAGON_C) / WAGON_C * BOUNDARY


def fielder_pos(s):
    """Where the catcher stands: from the scene's wagon coordinates, else a keeper/bowler/default position by catch type."""
    if "_fp" in s: return s["_fp"]
    kind = s.get("catch", "field"); hand, off, zb, xb, T = _geom(s)
    if kind == "keeper": fp = (0.4 * off, PL + 8.0)
    elif kind == "bowler": fp = (0.0, -1.0)
    elif s.get("wagon"): fp = wagon_to_world(*s["wagon"])
    else: fp = (-off * 5.5, PL - 7.0)
    s["_fp"] = fp; return fp


def ball_state(s, t, tR, tc):
    """(x, y, z) of the ball, or None. Hand -> bounce -> target before contact, then the result path."""
    hand, off, zb, xb, T = _geom(s)
    z0, x0, y0 = -.3, .22, 2.45
    if tR <= t < tc:
        q = (t - tR) / (tc - tR); z = lerp(z0, T[2], q); sb = (zb - z0) / (T[2] - z0)
        if q < sb: u = q / sb; return (lerp(x0, xb, u), y0 * (1 - u) ** 2, z)
        u = (q - sb) / (1 - sb); return (lerp(xb, T[0], u), T[1] * u ** .85 + .55 * math.sin(u * math.pi) * u * .3, z)
    if t >= tc:
        u = t - tc; res = s.get("result", "dot")
        if res == "bowled": return None
        if res == "lbw": return (T[0], max(.04, T[1] * (1 - 3 * u) * (u < .35) + .04), T[2] - .5 * u)
        if res == "caught":
            fx, fz = fielder_pos(s); dist = math.hypot(fx - T[0], fz - T[2]); Tf = max(.9, dist / 16 + .55); q = min(1, u / Tf)
            apex = min(14.0, 2.5 + dist * .2)
            return (lerp(T[0], fx, q), lerp(T[1], 1.2, q) + apex * 4 * q * (1 - q), lerp(T[2], fz, q))
        return (lerp(T[0], T[0] + off * .3, min(1, u / 1.2)), lerp(T[1], .1, min(1, u / 1.2)), T[2] + 14 * min(1, u / 1.2))
    return None


class Cam:
    def __init__(s, g, zc, h, th, f): s.g = g; s.zc = zc; s.h = h; s.th = th; s.f = f; s.cx = g.W / 2; s.cy = g.H * .43

    def p(s, X, Y, Z):
        rx, ry, rz = X, Y - s.h, Z - s.zc
        d = rz * math.cos(s.th) - ry * math.sin(s.th)                 # along the view axis (looking down by th)
        up = ry * math.cos(s.th) + rz * math.sin(s.th)
        d = max(d, .25)
        k = s.f / d
        return s.cx + rx * k, s.cy - up * k, k


def look(zc, h, y, z): return math.atan2(h - y, z - zc)


def _plan(s, D, g, t):
    """Camera: wide on the run-up, follows the ball from the hand, then closes in on the result."""
    tc = s["ball"]["_t"]; tR = max(.4, tc - FLIGHT); res = s.get("result", "dot")
    hand, off, zb, xb, T = _geom(s)
    zc, h = -19.0, 3.3
    wide_th = look(zc, h, .3, 12.0); wide_f = g.W * 2.75
    th, f = wide_th, wide_f
    b = ball_state(s, min(max(t, tR), tc - 1e-3), tR, tc)
    if t >= tR:
        k = eio(prog(t, tR, tc)); bx, by, bz = b
        th = lerp(wide_th, look(zc, h, by + .2, bz), min(1, eio(prog(t, tR, tR + .35))) * .8 + k * .2)
        f = lerp(wide_f, g.W * 5.2, k * .8 + eo(prog(t, tR, tR + .5)) * .2)
    if t >= tc:
        m = eio(prog(t, tc, tc + .55))
        if res == "bowled": tgt = (look(zc, h, .4, PL), g.W * 7.2)
        elif res == "lbw": tgt = (look(zc, h, .5, PL - .6), g.W * 6.0)
        elif res == "caught":
            bb = ball_state(s, t, tR, tc) or (T[0], T[1], T[2]); fx, fz = fielder_pos(s)
            tgt = (look(zc, h, bb[1] * .6, bb[2]), lerp(g.W * 4.0, g.W * 3.0, min(1, math.hypot(fx - T[0], fz - T[2]) / 25)))
        else: tgt = (look(zc, h, .5, PL + 4.0), g.W * 3.6)
        th0 = look(zc, h, T[1] + .2, T[2]); f0 = g.W * 5.2
        th, f = lerp(th0, tgt[0], m), lerp(f0, tgt[1], m)
    return Cam(g, zc, h, th, f), tR, tc


def _poly(c, pts, col, a=1.0):
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]: p.lineTo(*q)
    p.close(); c.drawPath(p, gfx.paint(col, a))


def _ground(c, cam, g):
    W, H = g.W, g.H
    hy = cam.p(0, 0, 400)[1]
    sk = skia.Paint(); sk.setShader(skia.GradientShader.MakeLinear([(0, 0), (0, hy)], [skia.Color(70, 140, 215), skia.Color(170, 205, 235)]))
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, hy + 2), sk)
    band = max(60, min(H * .22, (cam.p(0, 0, 70)[1] - cam.p(0, 6, 70)[1]) * 1.0))
    top = hy - band                                                                  # stand + crowd band
    crowd = (E.VENUE.get("crowd") if getattr(E, "VENUE", None) else None) or [[30, 36, 60], [200, 70, 70], [60, 120, 200], [230, 230, 230]]
    cp = skia.Paint(); cp.setShader(skia.GradientShader.MakeLinear([(0, top), (0, hy)], [skia.Color(32, 36, 56), skia.Color(58, 62, 84)]))
    c.drawRect(skia.Rect.MakeLTRB(0, top, W, hy), cp)
    for i in range(520):
        rx = (math.sin(i * 12.9898) * 43758.5453) % 1; ry = (math.sin(i * 78.233) * 12543.1) % 1
        cc = crowd[i % len(crowd)]; c.drawCircle(rx * W, top + 6 + ry * (band - 14), 2.4 + 2 * ry, gfx.paint(tuple(cc), .75))
    bd = E.VENUE.get("boards") if getattr(E, "VENUE", None) else None
    if bd: c.drawRect(skia.Rect.MakeLTRB(0, hy - 14, W, hy), gfx.paint(tuple(bd[0]), .95))
    z = -6.0; k = 0
    while z < 200:                                                                   # mown stripes in perspective
        z1 = z + (4 if z < 40 else 12 if z < 80 else 40)
        a, b = cam.p(-300, 0, z), cam.p(300, 0, z); c2, d = cam.p(300, 0, z1), cam.p(-300, 0, z1)
        _poly(c, [a[:2], b[:2], c2[:2], d[:2]], (46, 128, 54) if k % 2 == 0 else (54, 142, 62)); z = z1; k += 1
    c.drawRect(skia.Rect.MakeLTRB(0, cam.p(0, 0, 200)[1], W, cam.p(0, 0, 200)[1] + 1), gfx.paint((46, 128, 54)))
    pts = [cam.p(-1.55, 0, -1.4), cam.p(1.55, 0, -1.4), cam.p(1.55, 0, PL + 1.4), cam.p(-1.55, 0, PL + 1.4)]
    _poly(c, [q[:2] for q in pts], (206, 178, 120))                                  # the pitch
    for zz, hw in ((0, 1.32), (1.22, 1.32), (PL - 1.22, 1.32), (PL, 1.32)):           # creases
        a, b = cam.p(-hw, .005, zz), cam.p(hw, .005, zz)
        pp = gfx.paint((245, 240, 225), .9, stroke=max(2, a[2] * .05)); c.drawLine(a[0], a[1], b[0], b[1], pp)
    for sx in (-1.32, 1.32):                                                         # return creases
        a, b = cam.p(sx, .005, 0), cam.p(sx, .005, 1.22 + .6)
        pp = gfx.paint((245, 240, 225), .8, stroke=max(2, a[2] * .04)); c.drawLine(a[0], a[1], b[0], b[1], pp)


def _stumps(c, cam, z, hit=None, t=0.0, tc=1e9):
    """Three stumps with bails at depth z. `hit`: {"x": the stump struck} scatters them after tc."""
    u = max(0.0, t - tc) if hit else 0.0
    for i, sx in enumerate((-STUMP_DX, 0, STUMP_DX)):
        base = (sx, 0.0, z); L = STUMP_H
        if hit:
            q = min(1.0, u / .9); phi = q * (.9 + .35 * i) * (1 if i != 1 else -.6)
            base = (sx + (i - 1) * .9 * q, max(0, .9 * q * (1 - q) * (1 + i * .3)), z + 1.6 * q * (1 + .25 * i))
            tip = (base[0] + .12 * math.sin(phi * 2) * (i - 1), base[1] + L * math.cos(phi), base[2] + L * math.sin(phi))
        else: tip = (sx, L, z)
        a, b = cam.p(*base), cam.p(*tip); w = max(2.0, a[2] * .038)
        p = gfx.paint((248, 244, 228), 1.0, stroke=w); p.setStrokeCap(skia.Paint.kButt_Cap); c.drawLine(a[0], a[1], b[0], b[1], p)
        if i < 2 and not hit:
            q0, q1 = cam.p(sx, L + .01, z), cam.p(sx + STUMP_DX, L + .01, z)
            c.drawLine(q0[0], q0[1], q1[0], q1[1], gfx.paint((255, 214, 90), 1.0, stroke=max(2, q0[2] * .028)))
    if hit:                                                                          # bails fly
        for sg in (-1, 1):
            f = min(1.0, u / 1.1); bx = sg * STUMP_DX * .5 + sg * 1.1 * f; by = L + 1.3 * f - 2.6 * f * f + .05; bz = z + 1.8 * f
            a = cam.p(bx - .05, max(0, by), bz); b = cam.p(bx + .05, max(0, by) + .02 * sg, bz)
            c.drawLine(a[0], a[1], b[0], b[1], gfx.paint((255, 214, 90), 1.0 - f * .2, stroke=max(2, a[2] * .03)))


def _person(c, cam, x, z, kit, pose, t, hgt=1.84, dir=1, a=1.0, **kw):
    u, v, k = cam.p(x, 0, z)
    if k < 3: return
    E.avatar(c, u, v, hgt * k, kit, None, pose, t, a, dir=dir, **kw)


def _bowler_pose(t, tR):
    """Run-up (cycle) -> gather -> release -> follow-through."""
    ph = t * 9.0
    if t < tR - .55: return R.RUN(ph)
    if t < tR - .22: return R.blend(R.RUN(ph), R.GATHER, R.smooth((t - (tR - .55)) / .33))
    if t < tR + .02: return R.blend(R.GATHER, R.RELEASE, R.smooth((t - (tR - .22)) / .24))
    if t < tR + .55: return R.blend(R.RELEASE, R.FOLLOW, R.smooth((t - tR) / .55))
    return R.FOLLOW


def sc_cam(c, g, t, D, s):
    s.setdefault("ball", {}); s["ball"].setdefault("_t", D * s["ball"].get("at", .62))
    cam, tR, tc = _plan(s, D, g, t)
    hand, off, zb, xb, T = _geom(s); res = s.get("result", "dot")
    _ground(c, cam, g)
    bz = -.5 - 8.5 * (1 - eio(prog(t, 0, tR)))                                       # run-up, then follow-through
    after = prog(t, tR, tR + 1.0)
    bz = bz if t < tR else lerp(-.5, 3.0, eo(after))
    bx = lerp(0, -off * 1.0, eo(after)) if t >= tR else 0
    bk = s.get("bowler", {}).get("kit", "NZ"); btk = s.get("batter", {}).get("kit", "IND")
    _stumps(c, cam, 0.0)
    R.figure(c, cam, -off * 1.45, .3, R.STAND, "UMP", brim=True)                      # umpire (illustrative)
    R.figure(c, cam, bx, bz, _bowler_pose(t, tR), bk, cap=True)
    _stumps(c, cam, PL, hit={"x": 0} if res == "bowled" and t >= tc else None, t=t, tc=tc)
    R.figure(c, cam, 0, PL + 8.0, R.KEEP, bk, cap=True)                              # wicketkeeper (illustrative)
    bp = R.STANCE
    if t >= tc:
        u_ = eio(prog(t, tc, tc + .5))
        bp = {"bowled": R.blend(R.STANCE, R.DEJECT, u_), "lbw": R.blend(R.STANCE, R.DEJECT, eio(prog(t, tc + .25, tc + .9))),
              "caught": R.blend(R.STANCE, R.DEFEND, min(1, u_ * 2)), "dot": R.blend(R.STANCE, R.DEFEND, min(1, u_ * 2))}[res]
    R.figure(c, cam, -off * .0 + .0, PL - 1.0, bp, btk, bat=True, pads=True, flip=(hand < 0))
    if res == "caught":
        fx, fz = fielder_pos(s); dist = math.hypot(fx - T[0], fz - T[2]); tcatch = tc + max(.9, dist / 16 + .55)
        fp = R.READY if t < tcatch - .35 else (R.CATCH if t < tcatch + .5 else R.CELEB)
        R.figure(c, cam, fx, fz, fp, bk, cap=True)
    bs = ball_state(s, t, tR, tc)
    if bs:
        u, v, k = cam.p(*bs); r = max(5.0, .09 * k)
        for j in range(1, 8):                                                        # speed trail
            pj = ball_state(s, t - j * .018, tR, tc)
            if pj:
                uj, vj, kj = cam.p(*pj); c.drawCircle(uj, vj, r * (1 - j * .1), gfx.paint((250, 248, 240), .28 * (1 - j / 8)))
        sh = cam.p(bs[0], 0, bs[2]); c.drawOval(skia.Rect.MakeXYWH(sh[0] - r * 1.1, sh[1] - r * .3, r * 2.2, r * .6), gfx.paint((0, 0, 0), .25))
        c.drawCircle(u, v, r, gfx.paint((250, 248, 240)))
        if tc - .12 <= t < tc + .3 and res != "dot":                                 # contact flash
            f = (t - (tc - .12)) / .42; pp = gfx.paint((255, 255, 255), .9 * (1 - f)); pp.setStyle(skia.Paint.kStroke_Style); pp.setStrokeWidth(6)
            c.drawCircle(u, v, 18 + 110 * f, pp)
    if s.get("split") and t >= tc + .9: _split(c, g, t, tc + .9, s)
    if "panel" in s: E.stage_panel(c, g, t, D, s)
    gfx_text = gfx.text
    gfx_text(c, "ILLUSTRATIVE RECREATION", g.cx, g.H - 70, 24, "interB", (255, 255, 255), .55, "c", track=5)


def _split(c, g, t, t0, s):
    """Bowler and batter side by side at the moment of impact (illustrated)."""
    q = eo(prog(t, t0, t0 + .45)); hand = 1 if s.get("hand", "R") == "R" else -1
    pw, ph = g.W * .47, g.H * .36; y0 = g.H * .52 - (1 - q) * 40
    for k, (kit, pose, lab, x) in enumerate(((s.get("bowler", {}).get("kit", "NZ"), "bowl", "BOWLER", g.W * .03),
                                             (s.get("batter", {}).get("kit", "IND"), "stance", "BATTER · PAD", g.W * .5))):
        gfx.rrect(c, x, y0, pw, ph, 26, (14, 22, 40), .92 * q)
        gfx.rrect(c, x + 6, y0 + 6, pw - 12, ph - 12, 22, None, 0, stroke=3, scol=(255, 214, 0), sa=.9 * q)
        gfx.text(c, lab, x + pw / 2, y0 + 46, 26, "interB", (255, 214, 0), q, "c", track=5)
        E.avatar(c, x + pw / 2, y0 + ph - 34, ph * .62, kit, None, pose, t * 1.4, q, dir=1 if k == 0 else -hand, cap=(k == 0), bat=(k == 1), pads=(k == 1))
        if k == 1:
            gfx.rrect(c, x + pw / 2 - ph * .10, y0 + ph - 34 - ph * .26, ph * .2, ph * .13, 14, None, 0, stroke=5, scol=(235, 60, 60), sa=q)


def sfx(s, D, T0):
    tc = s["ball"]["_t"]; res = s.get("result", "dot"); ev = [[T0 + tc - FLIGHT, "whoosh", .7], [T0 + tc - FLIGHT * .38, "bounce", 1]]
    if res == "bowled": ev += [[T0 + tc, "crack", .9], [T0 + tc + .12, "crowd", 1]]
    elif res in ("lbw", "caught"): ev += [[T0 + tc, "crack", .7], [T0 + tc + .4, "crowd", 1]]
    return ev


def install(engine):
    global E
    E = engine
    E.SCENES["cam"] = sc_cam
    E.NO_CAPTION |= set()
