"""3D articulated cricketer for the broadcast camera. Joints live in world metres (x right, y up, z toward the batter) and are
projected by broadcast.Cam, so the same figure is seen from behind during the run-up and from the front in a stance.
Illustrated, no likeness. Pose = dict(yaw, pelvis, lean, feet=[L,R], hands=[L,R], look); feet/hands are (fwd, up, side) in the body frame."""
import math
import skia
import gfx

KITS = {"NZ": ((28, 28, 32), (24, 24, 28)), "IND": ((38, 110, 205), (30, 70, 165)), "UMP": ((236, 120, 176), (40, 40, 48))}
SKIN, SHOE, PAD, GLOVE, HELM = (196, 146, 108), (240, 240, 240), (238, 238, 232), (240, 240, 240), (22, 34, 66)
TH, SH, UA, FA = .46, .46, .30, .28


def add(*v): return tuple(sum(c) for c in zip(*v))
def mul(a, k): return tuple(x * k for x in a)
def sub(a, b): return tuple(x - y for x, y in zip(a, b))
def ln(a): return math.sqrt(sum(x * x for x in a))
def nrm(a): l = ln(a) or 1; return mul(a, 1 / l)
def dot(a, b): return sum(x * y for x, y in zip(a, b))


def blend(a, b, u):
    if isinstance(a, dict): return {k: blend(a[k], b[k], u) for k in a}
    if isinstance(a, (list, tuple)): return type(a)(blend(x, y, u) for x, y in zip(a, b))
    if isinstance(a, (int, float)): return a + (b - a) * u
    return b


def ik(S, T, l1, l2, pole):
    d = sub(T, S); dist = min(max(ln(d), .05), l1 + l2 - 1e-3); dv = nrm(d)
    a = (l1 * l1 - l2 * l2 + dist * dist) / (2 * dist); h = math.sqrt(max(l1 * l1 - a * a, 0))
    pp = sub(pole, mul(dv, dot(pole, dv)))
    E = add(S, mul(dv, a), mul(nrm(pp), h))
    return E, add(S, mul(dv, dist))


def smooth(u): u = max(0, min(1, u)); return u * u * (3 - 2 * u)

# ----------------------------------------------------------- poses (body frame: fwd, up, side(+right))
def RUN(ph):
    c, s = math.cos(ph), math.sin(ph)
    return dict(yaw=0.0, pelvis=.93, lean=.16, look=0.0,
                feet=[(.50 * s, .32 * max(0, c), -.13), (-.50 * s, .32 * max(0, -c), .13)],
                hands=[(.30 * -s + .1, 1.05 + .08 * c, -.32), (.30 * s + .1, 1.05 - .08 * c, .30)])
GATHER = dict(yaw=1.15, pelvis=.86, lean=.12, look=0.0, feet=[(.55, .0, -.12), (-.30, .0, .22)], hands=[(.55, 2.05, -.12), (-.25, 1.35, .30)])
RELEASE = dict(yaw=.35, pelvis=.82, lean=.50, look=0.0, feet=[(.46, .0, -.15), (-.52, .12, .10)], hands=[(.12, 1.25, -.42), (.06, 2.50, .14)])
FOLLOW = dict(yaw=.0, pelvis=.78, lean=.80, look=0.0, feet=[(.12, .0, -.15), (.55, .30, .12)], hands=[(.15, 1.0, -.36), (.45, .85, .22)])
STANCE = dict(yaw=-math.pi / 2, pelvis=.80, lean=.50, look=math.pi, feet=[(.04, 0, -.30), (-.04, 0, .30)], hands=[(.22, .78, -.06), (.28, .62, .12)])
DEFEND = dict(yaw=-math.pi / 2, pelvis=.78, lean=.62, look=math.pi, feet=[(.30, 0, -.30), (-.10, 0, .30)], hands=[(.52, .86, -.04), (.55, .74, .12)])
DEJECT = dict(yaw=-math.pi / 2 + .6, pelvis=.88, lean=.55, look=0.0, feet=[(.04, 0, -.26), (-.04, 0, .26)], hands=[(.15, .45, -.1), (.2, .35, .1)])
KEEP = dict(yaw=math.pi, pelvis=.50, lean=.35, look=math.pi, feet=[(.0, 0, -.28), (.0, 0, .28)], hands=[(.50, .45, -.20), (.50, .45, .20)])
STAND = dict(yaw=0.0, pelvis=.98, lean=.0, look=0.0, feet=[(0, 0, -.12), (0, 0, .12)], hands=[(.0, .90, -.24), (.0, .90, .24)])
READY = dict(yaw=math.pi, pelvis=.80, lean=.30, look=math.pi, feet=[(.0, 0, -.25), (.0, 0, .25)], hands=[(.45, .70, -.22), (.45, .70, .22)])
CATCH = dict(yaw=math.pi, pelvis=.95, lean=.0, look=math.pi, feet=[(.0, 0, -.22), (.0, 0, .22)], hands=[(.25, 1.9, -.16), (.25, 1.9, .16)])
CELEB = dict(yaw=math.pi, pelvis=.95, lean=-.1, look=math.pi, feet=[(0, 0, -.2), (0, 0, .2)], hands=[(.1, 2.2, -.38), (.1, 2.2, .38)])


def figure(c, cam, x, z, P, kit="IND", bat=False, pads=False, cap=False, brim=False, flip=False, a=1.0, sink=None):
    """Draw one cricketer at ground point (x, z). `flip` mirrors left/right (left-handers)."""
    shirt, trou = KITS.get(kit, kit if isinstance(kit, tuple) else KITS["IND"])
    if isinstance(kit, tuple): shirt, trou = kit, tuple(int(v * .6) for v in kit)
    yaw = P["yaw"] * (-1 if flip else 1); f = (math.sin(yaw), 0, math.cos(yaw)); r = (math.cos(yaw), 0, -math.sin(yaw)); up = (0, 1, 0)
    fl = -1 if flip else 1
    O = (x, 0, z); pel = add(O, (0, P["pelvis"], 0))
    body = lambda p, base: add(base, mul(f, p[0]), (0, p[1], 0), mul(r, p[2] * fl))        # (fwd, up, side) -> world
    hips = [add(pel, mul(r, -.10)), add(pel, mul(r, .10))]
    feet = [body((P["feet"][i][0], P["feet"][i][1] + .07, P["feet"][i][2]), O) for i in range(2)]
    knees = [ik(hips[i], feet[i], TH, SH, add(f, (0, .25, 0)))[0] for i in range(2)]
    lean = P["lean"]; tl = .56
    neck = add(pel, mul(up, tl * math.cos(lean)), mul(f, tl * math.sin(lean)))
    chest = add(pel, mul(up, .40 * math.cos(lean)), mul(f, .40 * math.sin(lean)))
    shd = [add(neck, mul(r, -.19), (0, -.06, 0)), add(neck, mul(r, .19), (0, -.06, 0))]
    hand_t = [body((P["hands"][i][0], P["hands"][i][1], P["hands"][i][2]), O) for i in range(2)]
    elbows = [ik(shd[i], hand_t[i], UA, FA, add(mul(f, -.3), (0, -1, 0), mul(r, (-1 if i == 0 else 1) * .8)))[0] for i in range(2)]
    head = add(neck, mul(up, .15), mul(f, .04 * lean))
    prims = []                                                              # (depth, draw fn)

    def P3(p): u, v, k = cam.p(*p); return u, v, k

    def seg(p0, p1, w, col, al=1.0):
        if sink is not None: sink.append(("seg", p0, p1, w, col)); return
        a0, a1 = P3(p0), P3(p1)
        def d():
            pp = gfx.paint(col, a * al, stroke=max(1.5, w * (a0[2] + a1[2]) / 2)); pp.setStrokeCap(skia.Paint.kRound_Cap)
            c.drawLine(a0[0], a0[1], a1[0], a1[1], pp)
        prims.append(((p0[2] + p1[2]) / 2, d))

    def dot_(p, rad, col, al=1.0):
        if sink is not None: sink.append(("dot", p, rad, col)); return
        q = P3(p)
        def d(): c.drawCircle(q[0], q[1], max(1.5, rad * q[2]), gfx.paint(col, a * al))
        prims.append((p[2], d))
    for i in range(2):                                                      # legs
        seg(hips[i], knees[i], .17, trou); seg(knees[i], feet[i], .12, trou)
        if pads: seg(add(knees[i], mul(sub(feet[i], knees[i]), .05)), add(feet[i], (0, .02, 0)), .15, PAD)
        sh_ = add(feet[i], mul(f, .08)); seg(feet[i], sh_, .11, SHOE)
    seg(pel, neck, .36, shirt); seg(pel, add(pel, mul(up, .02)), .30, trou)    # torso
    for i in range(2):                                                      # arms
        seg(shd[i], elbows[i], .10, shirt); seg(elbows[i], hand_t[i], .085, SKIN)
        dot_(hand_t[i], .06, GLOVE if (bat or pads) else SKIN)
    if bat:                                                                 # bat: handle at the hands, blade to the ground
        h0 = hand_t[1]; ground = add(O, mul(f, P["feet"][0][0] + .34), (0, .02, 0)); dirv = nrm(sub(ground, h0)); tipb = add(h0, mul(dirv, .95))
        seg(h0, add(h0, mul(dirv, .28)), .035, (40, 40, 44)); seg(add(h0, mul(dirv, .28)), tipb, .11, (214, 180, 120))
    seg(neck, head, .09, SKIN); dot_(head, .115, SKIN)                      # head
    look = P["look"] * (-1 if flip else 1); lv = (math.sin(look), 0, math.cos(look))
    helmet = bat or pads
    if helmet:
        dot_(add(head, (0, .035, 0)), .125, HELM)
        if lv[2] < -.2:
            hp = add(head, mul(lv, .09))
            for k in range(3): seg(add(hp, (0, -.03 - .03 * k, -.0)), add(hp, (-.0, -.03 - .03 * k, 0)), .13, (200, 205, 215), .55)
    elif cap or brim: dot_(add(head, (0, .045, 0)), .12, shirt if cap else (245, 245, 245))
    else: dot_(add(head, (0, .045, 0)), .115, (40, 32, 28))                  # hair
    if sink is not None: return
    prims.sort(key=lambda t: -t[0])                                         # far first
    sh0 = P3((x, 0, z)); c.drawOval(skia.Rect.MakeXYWH(sh0[0] - .5 * sh0[2], sh0[1] - .09 * sh0[2], 1.0 * sh0[2], .2 * sh0[2]), gfx.paint((0, 0, 0), .22 * a))
    for _, d in prims: d()
