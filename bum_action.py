"""An original animated bowling-action sequence from our own illustrated avatar (no likeness): keyframed side-view poses (run-up, leap, bound, load, release, follow-through) injected into engine._pose as pose "bum" (t = phase 0..1).
Joints are in 1/100 of the figure's height, origin between the feet, up is negative: hb/hf hips, kb/kf knees, ab/af ankles (back/front leg), sb/sf shoulders, eb/wb the BOWLING arm (elbow, wrist, ball in hand), ef/wf the front arm."""
import engine as E

KEYS = [  # (name, joints)
    ("RUN-UP", dict(hb=(-3, -47), hf=(1, -47), kb=(-13, -30), ab=(-24, -10), kf=(11, -34), af=(13, -12), sb=(1, -75), sf=(5, -75), head=(8, -88), eb=(-3, -62), wb=(7, -66), ef=(12, -64), wf=(18, -73))),
    ("LEAP", dict(hb=(-2, -62), hf=(2, -62), kb=(-12, -50), ab=(-22, -38), kf=(14, -56), af=(19, -44), sb=(0, -90), sf=(4, -90), head=(7, -102), eb=(-8, -104), wb=(-6, -121), ef=(18, -90), wf=(33, -92))),
    ("BOUND", dict(hb=(-3, -60), hf=(1, -60), kb=(-15, -48), ab=(-28, -40), kf=(15, -52), af=(23, -38), sb=(-2, -88), sf=(2, -88), head=(5, -100), eb=(-10, -103), wb=(-9, -120), ef=(18, -90), wf=(34, -90))),
    ("LOAD", dict(hb=(-4, -50), hf=(2, -50), kb=(-6, -28), ab=(-20, -4), kf=(12, -28), af=(18, -3), sb=(-5, -79), sf=(-1, -80), head=(-2, -92), eb=(-12, -99), wb=(-17, -114), ef=(12, -90), wf=(26, -97))),
    ("RELEASE", dict(hb=(-3, -50), hf=(3, -50), kb=(-9, -32), ab=(-16, -14), kf=(11, -27), af=(17, -3), sb=(5, -74), sf=(9, -72), head=(13, -85), eb=(8, -96), wb=(9, -113), ef=(14, -62), wf=(8, -52))),
    ("FOLLOW-THROUGH", dict(hb=(-1, -48), hf=(5, -48), kb=(-6, -30), ab=(-12, -21), kf=(12, -27), af=(18, -3), sb=(10, -66), sf=(14, -64), head=(22, -76), eb=(18, -60), wb=(11, -42), ef=(2, -60), wf=(-4, -48))),
]
_orig = E._pose


def pose_at(p):
    p = min(max(p, 0.0), 0.9999) * (len(KEYS) - 1); i = int(p); f = p - i; f = f * f * (3 - 2 * f)
    a, b = KEYS[i][1], KEYS[i + 1][1]; return {k: (a[k][0] + (b[k][0] - a[k][0]) * f, a[k][1] + (b[k][1] - a[k][1]) * f) for k in a}


def _pose(pose, t):
    if pose == "bum":
        j = _orig("bowl", 0); j.update(pose_at(t)); j["ball"] = True; j["bat"] = None; return j
    return _orig(pose, t)


def install(): E._pose = _pose
install()
