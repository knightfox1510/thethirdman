"""Pitch-view model for the Replay Room: ONE delivery, built from any captured match, drawn in 3D with a camera that can orbit it.
    from pitchview import Delivery, from_table, trajectory
    dl = from_table("data/cricinfo/nz_ind_4odi_balls.csv", "data/cricinfo/nz_ind_4odi.json", inning=2, over=0.5)
Inputs are the Cricinfo ball table (line, length, shot, control, wagon, dismissal code) and the capture json (dismissal text: who caught it, who kept).
What is DATA: line and length zones, shot, control flag, how the batter was out, who took the catch, the wagon-wheel spot where the ball ended up.
What is MODEL (assumptions, always labelled "illustrative" on screen): release height, ball speed, bounce restitution, the batter's height, the catch height, and the arcs between data points.
Wagon coordinates (checked against shots of known direction): x < 180 is the off side for a right-hander (mirrored for a left-hander, whose table is already mirrored), y > 180 is down the ground
towards the bowler, centre (180,180); the field scale is approximate (BOUNDARY_M, as in broadcast.py).
World: metres. x lateral (off side is -x for a right-hander), y along the pitch (0 bowler's stumps, PL batter's stumps), z up."""
import json, math, re
from dataclasses import dataclass, field
import numpy as np
import pandas as pd
from pitchview_text import ball_text

PL, PW = 20.12, 3.05
G = 9.81
BOUNDARY_M, WAGON_R = 65.0, 180.0
K = BOUNDARY_M / WAGON_R                     # metres per wagon pixel (approximate)
HEIGHT_MARKS = [("KNEE", .28), ("WAIST", .55), ("CHEST", .75), ("SHOULDER", .83), ("HEAD", 1.0)]   # fractions of the batter's height (illustrative anthropometry)
LEN_FROM_STUMPS = {"YORKER": 1.0, "FULL": 3.0, "GOOD_LENGTH": 5.0, "SHORT_OF_A_GOOD_LENGTH": 7.0, "SHORT": 9.5, "FULL_TOSS": None}   # metres in front of the batter's stumps where it pitches (zone centres, illustrative)
LEN_LABEL = {"YORKER": "YORKER", "FULL": "FULL", "GOOD_LENGTH": "GOOD LENGTH", "SHORT_OF_A_GOOD_LENGTH": "SHORT OF A GOOD LENGTH", "SHORT": "SHORT", "FULL_TOSS": "FULL TOSS"}
LINE_LABEL = {"OUTSIDE_OFFSTUMP": "OUTSIDE OFF", "ON_THE_STUMPS": "ON THE STUMPS", "DOWN_LEG": "DOWN LEG", "WIDE_OUTSIDE_OFFSTUMP": "WIDE OUTSIDE OFF"}
DISMISSAL = {1: "caught", 2: "bowled", 3: "lbw", 4: "run out", 5: "stumped"}   # code -> text: verified against the 4th ODI table (11 caught, 4 bowled, 2 lbw, 1 stumped match the commentary counts); 4 assumed run out


# Typical fielding spots for a RIGHT-hander, metres from the middle of the batter's stumps: x lateral (off side is -x), y along the pitch (PL = batter's stumps, > PL is behind the wicket).
# Used for the START of a fielder's move and to say where a catch was taken; illustrative (positions are neither fixed nor precisely defined). Mirrored for left-handers.
POSITIONS = {
    "keeper": (0.0, PL + 1.2), "first slip": (-1.7, PL + 3.6), "slip": (-1.7, PL + 3.6), "second slip": (-2.9, PL + 3.9), "third slip": (-4.1, PL + 4.2), "fourth slip": (-5.2, PL + 4.5), "fly slip": (-4.5, PL + 12.0),
    "gully": (-7.0, PL + 5.0), "leg slip": (2.4, PL + 4.0), "silly point": (-3.0, PL - 1.5), "silly mid off": (-3.0, PL - 3.0), "silly mid on": (3.0, PL - 3.0), "short leg": (3.0, PL - 1.0),
    "point": (-14.0, PL + 1.0), "backward point": (-15.0, PL + 7.0), "cover point": (-13.0, PL - 4.0), "short cover": (-10.0, PL - 6.0), "cover": (-15.0, PL - 9.0), "extra cover": (-17.0, PL - 14.0),
    "mid off": (-9.0, PL - 21.0), "mid on": (9.0, PL - 21.0), "midwicket": (16.0, PL - 9.0), "short midwicket": (9.0, PL - 6.0), "square leg": (14.0, PL + 0.5), "backward square leg": (15.0, PL + 7.0),
    "deep point": (-55.0, PL + 2.0), "deep cover": (-46.0, PL - 38.0), "deep extra cover": (-34.0, PL - 52.0), "long off": (-22.0, PL - 58.0), "long on": (22.0, PL - 58.0), "deep midwicket": (44.0, PL - 28.0),
    "cow corner": (48.0, PL - 38.0), "deep square leg": (55.0, PL + 1.0), "deep backward square leg": (50.0, PL + 18.0), "fine leg": (18.0, PL + 24.0), "deep fine leg": (30.0, PL + 50.0),
    "keeper back": (0.0, PL + 14.0), "third man": (-38.0, PL + 42.0), "short third man": (-14.0, PL + 14.0), "bowler": (0.0, PL - 21.0),
}
ZONE_NAME = {1: "fine leg", 2: "deep backward square leg", 3: "deep midwicket", 4: "long on", 5: "long off", 6: "deep cover", 7: "deep point", 8: "third man side"}   # Cricinfo wagon zones 1-8 (checked on the 4th ODI): used only when the commentary names no position
EXC_WORDS = ("diving", "dives", "dived", "one-handed", "one handed", "full stretch", "leaps", "running", "sprint", "tumbl", "fine two-handed", "stunning", "screamer")


def spot(name, hand):
    x, y = POSITIONS[name]; return (x if hand == "R" else -x, y)


@dataclass
class Delivery:
    bowler: str; batter: str; over: float; line: str; length: str
    shot: str = ""; control: int = 0; runs: int = 0; wicket: bool = False; how: str = ""      # how: caught / bowled / lbw / stumped / run out
    fielder: str = ""; keeper_catch: bool = False; wagon: tuple = (0, 0); hand: str = "R"
    pace_kmh: float = 130.0; batter_h: float = 1.80; release_z: float = 2.15; restitution: float = 0.58; catch_z: float = 1.1   # model assumptions
    result_text: str = ""
    facts: dict = field(default_factory=dict)          # leads parsed from the Cricbuzz commentary (pitchview_text.py)
    length_table: str = ""                              # what the Cricinfo table says, when the commentary names a different length
    length_note: str = ""                               # "conflict" or "outcome" when the two sources disagree
    position: str = ""; side: str = ""; exceptional: str = ""; bounce: str = ""; movement: str = ""
    four: bool = False; six: bool = False; wide: bool = False; noball: bool = False; byes: int = 0; legbyes: int = 0
    spin: bool = False; drift: str = ""; came_down: bool = False; round_wicket: bool = False; left_arm: bool = False


def _dismissal_text(js, batter):
    """The capture's own dismissal text for a batter (e.g. 'c †Ishan Kishan b Gurnoor Brar'); a leading dagger marks the wicket-keeper."""
    m = re.search(r'"short":"(\w[\w ]*)","long":"([^"]*)","commentary":"%s ' % re.escape(batter), js)
    return (m.group(1), m.group(2)) if m else ("", "")


OFF_SHOTS = {"COVER_DRIVE", "CUT_SHOT", "SQUARE_CUT", "OFF_DRIVE", "LATE_CUT", "UPPER_CUT"}
LEG_SHOTS = {"FLICK", "PULL", "HOOK", "ON_DRIVE", "SLOG_SWEEP", "GLANCE", "SWEEP", "PADDLE", "REVERSE_SWEEP"}


def infer_hand(d, batter):
    """Batting hand from the data: off-side shots land at wagon x < 180 for a right-hander, x > 180 for a left-hander (checked: Santner's cut shots sit at x > 180). Votes over the batter's recorded shots."""
    b = d[(d.batter == batter) & (d.wagon_x > 0)]; v = 0
    for _, r in b.iterrows():
        side = (r.wagon_x - 180)
        if r.shot in OFF_SHOTS: v += 1 if side < 0 else -1
        elif r.shot in LEG_SHOTS: v += 1 if side > 0 else -1
    return "L" if v < 0 else "R"


def from_table(csv, capture_json, inning, over, hand=None, cricbuzz=None, **assume):
    d = pd.read_csv(csv); r = d[(d.inning == inning) & (d.overs.round(1) == round(over, 1))]
    if r.empty: raise ValueError(f"no ball {over} in innings {inning}")
    r = r.iloc[0]; hand = hand or infer_hand(d, r.batter); js = open(capture_json, encoding="utf-8").read() if capture_json else ""
    out_name = r.batter                                                  # who was dismissed: the striker, unless a run-out took the non-striker (out_id differs from batter_id)
    if bool(r.wicket) and pd.notna(r.out_id) and int(r.out_id) != int(r.batter_id):
        nm = d[d.batter_id == int(r.out_id)].batter; out_name = nm.iloc[0] if len(nm) else r.batter
    how, long = _dismissal_text(js, out_name) if bool(r.wicket) else ("", "")
    if bool(r.wicket) and not how: how = DISMISSAL.get(int(r.dismissal), "")
    fielder = ""
    m = re.match(r"(?:c|st)\s+(†)?(.+?)\s+b\s", long or "")
    if m: fielder = m.group(2).strip()
    dl = Delivery(bowler=r.bowler, batter=r.batter, over=float(r.overs), line=r.pitch_line, length=r.pitch_length, shot=str(r.shot), control=int(r.control), runs=int(r.runs),
                  wicket=bool(r.wicket), how=how, fielder=fielder, keeper_catch=bool(m and m.group(1)), wagon=(float(r.wagon_x), float(r.wagon_y)), hand=hand, **assume)
    dl.out_batter = out_name; dl.four, dl.six, dl.wide, dl.noball = bool(r.four), bool(r.six), int(r.wides) > 0, int(r.noballs) > 0; dl.byes, dl.legbyes = int(r.byes), int(r.legbyes)
    if cricbuzz:
        f = ball_text(cricbuzz, inning, over); dl.facts = f
        dl.spin = bool(f.get("spin")); dl.drift = f.get("drift", ""); dl.came_down = bool(f.get("came_down")); dl.round_wicket = bool(f.get("round")); dl.left_arm = bool(f.get("left_arm"))
        if dl.spin and "pace_kmh" not in assume and "speed_kph" not in f: dl.pace_kmh, dl.release_z, dl.restitution = 85.0, 2.0, 0.50     # a spinner: slower, lower release, less bounce (assumptions)
        if "speed_kph" in f and "pace_kmh" not in assume: dl.pace_kmh = f["speed_kph"]
        if f.get("catcher"): dl.fielder = f["catcher"]
        dl.position = f.get("position", ""); dl.side = f.get("side", ""); dl.exceptional = f.get("exceptional", ""); dl.bounce = f.get("bounce", ""); dl.movement = f.get("movement", "")
        if f.get("length_text") and f["length_text"] != dl.length: dl.length_table = dl.length; dl.length_note = "conflict"
    return dl


def line_x(dl):
    off = -1 if dl.hand == "R" else 1
    if dl.wide: return (-off * 1.7) if dl.line == "DOWN_LEG" else off * 1.7           # called wide: beyond the wide guideline (distance illustrative)
    return {"OUTSIDE_OFFSTUMP": 0.5 * off, "ON_THE_STUMPS": 0.0, "DOWN_LEG": -0.5 * off, "WIDE_OUTSIDE_OFFSTUMP": 1.2 * off}.get(dl.line, 0.0)


def wagon_world(wx, wy):
    return ((wx - 180) * K, PL - (wy - 180) * K)


def _flight(dl, yb, e, xb, v, n, zr, full_toss=False):
    """Ball height along the pitch for a given bounce spot yb and restitution e: pre-bounce arc, then the rebound (speed loses 20%). Returns (pre, post, gate_z, stump_z)."""
    xr = xb * 0.3 + (0.25 if dl.hand == "R" else -0.25); yr = 1.0; gate_y = PL - 1.22
    t1 = (yb - yr) / v; vz0 = (-zr + 0.5 * G * t1 * t1) / t1; vzi = vz0 - G * t1; vzp = -e * vzi; v1 = 0.80 * v; t2 = (PL - yb) / v1
    mv = {"in": 0.35, "away": -0.35}.get(dl.movement, 0.0) * (1 if dl.hand == "R" else -1) * -1      # seam movement after pitching: 'in' drifts towards the batter's body (leg side), 'away' towards off
    xs = xb - mv
    loft = 0.9 if dl.spin else 0.0; legdir = 1 if dl.hand == "R" else -1                               # a spinner's ball loops; drift bows the path (both illustrative)
    dr = {"in": -0.25, "away": 0.25}.get(dl.drift, 0.0) * legdir
    pre = [(lerp(xr, xb, a) + dr * math.sin(math.pi * a), lerp(yr, yb, a), max(0.0, zr + vz0 * (a * t1) - 0.5 * G * (a * t1) ** 2 + loft * math.sin(math.pi * a))) for a in np.linspace(0, 1, n)]
    post = [(lerp(xb, xs, a), lerp(yb, PL, a), max(0.0, vzp * (a * t2) - 0.5 * G * (a * t2) ** 2)) for a in np.linspace(0, 1, n)]
    tg = (gate_y - yb) / v1; gate_z = max(0.0, vzp * tg - 0.5 * G * tg * tg); stump_z = max(0.0, vzp * t2 - 0.5 * G * t2 * t2)
    return pre, post, gate_z, stump_z, xs


def trajectory(dl, n=60):
    """The delivery in phases: 'pre' (release to bounce), 'post' (bounce to the stumps), 'bat' (off the bat to the catch), plus fielder start/catch spot and the fielder's own move.
    Outcome constraints (this is what makes the bounce honest): a ball that hit the stumps (bowled / lbw) must be under stump height at the stumps, so the rebound is solved to fit it;
    'kept low' in the commentary lowers it further, 'extra bounce' raises it. If the table's length cannot produce that (a short ball does not skid into the stumps) and the commentary
    names a length that can, the commentary length is used and the disagreement is flagged (length_note)."""
    v = dl.pace_kmh / 3.6; xb = line_x(dl); n = int(n); zr = dl.release_z; gate_y = PL - 1.22
    full_toss = LEN_FROM_STUMPS.get(dl.length) is None
    hits_stumps = dl.wicket and dl.how in ("bowled", "lbw")
    e = {"low": 0.42, "extra": 0.70}.get(dl.bounce, dl.restitution)
    length = dl.length; note = dl.length_note
    if full_toss:
        yb = None; xr = xb * 0.3 + (0.25 if dl.hand == "R" else -0.25); t = (gate_y - 1.0) / v; vz0 = (0.95 - zr + 0.5 * G * t * t) / t
        pre = [(lerp(xr, xb, a), lerp(1.0, gate_y, a), zr + vz0 * (a * t) - 0.5 * G * (a * t) ** 2) for a in np.linspace(0, 1, n)]; post = []; gate_z = pre[-1][2]; bounce = None; xs = xb
    else:
        def solve(L):
            yb_ = PL - LEN_FROM_STUMPS[L]
            if not hits_stumps: return yb_, e, _flight(dl, yb_, e, xb, v, n, zr)
            lo, hi = 0.15, 0.75; target = 0.35 if dl.bounce == "low" else 0.55               # the ball must clear the turf and still be under the stumps' 0.71 m
            for _ in range(40):
                mid = (lo + hi) / 2; z = _flight(dl, yb_, mid, xb, v, n, zr)[3]
                lo, hi = (mid, hi) if z < target else (lo, mid)
            ee = (lo + hi) / 2; return yb_, ee, _flight(dl, yb_, ee, xb, v, n, zr)
        yb, ee, fl = solve(length)
        if hits_stumps and (ee <= 0.2 or ee >= 0.74) and dl.facts.get("length_text") and dl.facts["length_text"] != length and LEN_FROM_STUMPS.get(dl.facts["length_text"]):
            length = dl.facts["length_text"]; note = "outcome"; yb, ee, fl = solve(length)       # the table's length cannot hit the stumps under stump height; the commentary's can
        pre, post, gate_z, stump_z, xs = fl; bounce = (xb, yb, 0.0); dl.restitution_used = ee
    contact = (xb * 0.7, gate_y, gate_z)
    bat = []; end = None; field = None
    pos = dl.position or ("keeper" if dl.keeper_catch else "")
    if pos == "keeper" and dl.pace_kmh >= 120: pos = "keeper back"                # to a fast bowler the keeper stands back; the distance is an assumption (not in the data)
    if dl.wicket and dl.how == "caught":
        if pos in POSITIONS:
            fx, fy = spot(pos, dl.hand); sx, sy = fx, fy
            fxv, fyv = (0 - fx), (PL - fy); nrm = math.hypot(fxv, fyv) or 1.0; fxv, fyv = fxv / nrm, fyv / nrm; left = (-fyv, fxv)   # unit vectors: facing the batter, and to the fielder's left
            dive = any(w in (dl.exceptional or "") for w in EXC_WORDS) or bool(dl.exceptional)
            mag = (2.4 if dive else 1.4) if dl.side else 0.0
            sign = 1 if dl.side == "left" else -1
            cx_, cy_ = fx + sign * left[0] * mag, fy + sign * left[1] * mag
            cz = 0.5 if dive else dl.catch_z if pos not in ("keeper",) else 1.0
            end = (cx_, cy_, cz); field = dict(name=dl.fielder, position=pos, start=(sx, sy), catch=(cx_, cy_), moved_m=round(math.hypot(cx_ - sx, cy_ - sy), 1), exceptional=bool(dive), side=dl.side)
        elif dl.wagon != (0, 0):
            ex, ey = wagon_world(*dl.wagon); end = (ex, ey, dl.catch_z); field = dict(name=dl.fielder, position=ZONE_NAME.get(int(dl.wagon_zone), "outfield") if hasattr(dl, "wagon_zone") else "outfield", start=(ex, ey), catch=(ex, ey), moved_m=0.0, exceptional=False, side="", approx=True)
        if end:
            dist = math.hypot(end[0] - contact[0], end[1] - contact[1]); apex = max(contact[2] + 0.4, 0.13 * dist)
            bat = [(lerp(contact[0], end[0], a), lerp(contact[1], end[1], a), max(0.0, lerp(contact[2], end[2], a) + 4 * (apex - (contact[2] + end[2]) / 2) * a * (1 - a))) for a in np.linspace(0, 1, n)]
    elif hits_stumps:
        end = (xs, PL, min(max(gate_z, 0.2), 0.7))
    return dict(pre=pre, post=post, bat=bat, gate_z=gate_z, bounce=bounce, contact=contact, end=end, field=field, length_used=length, length_note=note, stump_z=(None if full_toss else stump_z), e=getattr(dl, "restitution_used", e))


def fielder_path(f, n=40):
    """The fielder's own move from where he started to the catch (a dive rises then drops): points (x, y, z)."""
    if not f: return []
    (sx, sy), (cx, cy) = f["start"], f["catch"]
    return [(lerp(sx, cx, a), lerp(sy, cy, a), (0.9 * (1 - 4 * (a - 0.5) ** 2) * 0.4 + 0.0 if f.get("exceptional") else 0.0)) for a in np.linspace(0, 1, n)]


def where_text(dl, tr):
    """Where the wicket fell, in words: the named fielding position (commentary) or, failing that, the wagon-wheel sector (approximate)."""
    f = tr.get("field")
    if dl.how == "caught" and f:
        move = f", moving about {f['moved_m']} m to his {f['side']}" if (f.get("moved_m") and not f.get("approx") and f.get("side")) else ""
        if dl.keeper_catch:
            stand = ", standing back (assumed)" if f["position"] == "keeper back" else ""
            return f"caught behind by wicket-keeper {dl.fielder}{stand}{move}"
        return f"caught at {f['position']}{' (approx.)' if f.get('approx') else ''} by {dl.fielder}{move}"
    return {"bowled": "bowled: the ball hit the stumps", "lbw": "lbw: hit on the pad in front of the stumps", "stumped": "stumped by the wicket-keeper", "run out": "run out"}.get(dl.how, dl.how)


def lerp(a, b, t): return a + (b - a) * t


def height_label(z, H):
    """Where the ball crossed the batter's crease, as a body height (relative to an assumed batter height H)."""
    f = z / H
    for name, top in HEIGHT_MARKS:
        if f <= top: return {"KNEE": "knee height or lower", "WAIST": "between knee and waist", "CHEST": "between waist and chest", "SHOULDER": "between chest and shoulder", "HEAD": "above the shoulder"}[name]
    return "above the batter's head"


def summary(dl, tr):
    """Plain facts for captions and the voiceover: data first, model clearly marked."""
    z = tr["gate_z"]
    return dict(line=LINE_LABEL.get(dl.line, dl.line), length=LEN_LABEL.get(dl.length, dl.length), shot=dl.shot.replace("_", " ").lower(), control="in control" if dl.control == 1 else "not in control",
                how=dl.how, fielder=dl.fielder, height_m=round(z, 2), height_text=height_label(z, dl.batter_h), keeper=dl.keeper_catch, where=where_text(dl, tr), stump_z=tr.get("stump_z"))
