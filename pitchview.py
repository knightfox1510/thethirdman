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

PL, PW = 20.12, 3.05
G = 9.81
BOUNDARY_M, WAGON_R = 65.0, 180.0
K = BOUNDARY_M / WAGON_R                     # metres per wagon pixel (approximate)
HEIGHT_MARKS = [("KNEE", .28), ("WAIST", .55), ("CHEST", .75), ("SHOULDER", .83), ("HEAD", 1.0)]   # fractions of the batter's height (illustrative anthropometry)
LEN_FROM_STUMPS = {"YORKER": 1.0, "FULL": 3.0, "GOOD_LENGTH": 5.0, "SHORT_OF_A_GOOD_LENGTH": 7.0, "SHORT": 9.5, "FULL_TOSS": None}   # metres in front of the batter's stumps where it pitches (zone centres, illustrative)
LEN_LABEL = {"YORKER": "YORKER", "FULL": "FULL", "GOOD_LENGTH": "GOOD LENGTH", "SHORT_OF_A_GOOD_LENGTH": "SHORT OF A GOOD LENGTH", "SHORT": "SHORT", "FULL_TOSS": "FULL TOSS"}
LINE_LABEL = {"OUTSIDE_OFFSTUMP": "OUTSIDE OFF", "ON_THE_STUMPS": "ON THE STUMPS", "DOWN_LEG": "DOWN LEG", "WIDE_OUTSIDE_OFFSTUMP": "WIDE OUTSIDE OFF"}
DISMISSAL = {1: "caught", 2: "bowled", 3: "lbw", 4: "run out", 5: "stumped"}   # code -> text: verified against the 4th ODI table (11 caught, 4 bowled, 2 lbw, 1 stumped match the commentary counts); 4 assumed run out


@dataclass
class Delivery:
    bowler: str; batter: str; over: float; line: str; length: str
    shot: str = ""; control: int = 0; runs: int = 0; wicket: bool = False; how: str = ""      # how: caught / bowled / lbw / stumped / run out
    fielder: str = ""; keeper_catch: bool = False; wagon: tuple = (0, 0); hand: str = "R"
    pace_kmh: float = 130.0; batter_h: float = 1.80; release_z: float = 2.15; restitution: float = 0.58; catch_z: float = 1.1   # model assumptions
    result_text: str = ""


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


def from_table(csv, capture_json, inning, over, hand=None, **assume):
    d = pd.read_csv(csv); r = d[(d.inning == inning) & (d.overs.round(1) == round(over, 1))]
    if r.empty: raise ValueError(f"no ball {over} in innings {inning}")
    r = r.iloc[0]; hand = hand or infer_hand(d, r.batter); js = open(capture_json, encoding="utf-8").read() if capture_json else ""
    how, long = _dismissal_text(js, r.batter) if bool(r.wicket) else ("", "")
    if bool(r.wicket) and not how: how = DISMISSAL.get(int(r.dismissal), "")
    fielder = ""
    m = re.match(r"(?:c|st)\s+(†)?(.+?)\s+b\s", long or "")
    if m: fielder = m.group(2).strip()
    return Delivery(bowler=r.bowler, batter=r.batter, over=float(r.overs), line=r.pitch_line, length=r.pitch_length, shot=str(r.shot), control=int(r.control), runs=int(r.runs),
                    wicket=bool(r.wicket), how=how, fielder=fielder, keeper_catch=bool(m and m.group(1)), wagon=(float(r.wagon_x), float(r.wagon_y)), hand=hand, **assume)


def line_x(dl):
    off = -1 if dl.hand == "R" else 1
    return {"OUTSIDE_OFFSTUMP": 0.5 * off, "ON_THE_STUMPS": 0.0, "DOWN_LEG": -0.5 * off, "WIDE_OUTSIDE_OFFSTUMP": 1.2 * off}.get(dl.line, 0.0)


def wagon_world(wx, wy):
    return ((wx - 180) * K, PL - (wy - 180) * K)


def trajectory(dl, n=60):
    """The delivery as three phases: 'pre' (release to bounce), 'post' (bounce to the batter's crease and the stumps), 'bat' (off the bat to where the data says it ended: the catch).
    Returns dict(pre, post, bat, gate_z, bounce, contact, end, notes). Heights are model output, labelled illustrative."""
    v = dl.pace_kmh / 3.6; xb = line_x(dl); xr = xb * 0.3 + (0.25 if dl.hand == "R" else -0.25); yr, zr = 1.0, dl.release_z
    full_toss = LEN_FROM_STUMPS.get(dl.length) is None
    gate_y = PL - 1.22
    if full_toss:
        yb = None; t = (gate_y - yr) / v; vz0 = (0.95 - zr + 0.5 * G * t * t) / t
        pre = [(lerp(xr, xb, a), lerp(yr, gate_y, a), zr + vz0 * (a * t) - 0.5 * G * (a * t) ** 2) for a in np.linspace(0, 1, n)]
        gate_z = pre[-1][2]; post = []
        bounce = None
    else:
        yb = PL - LEN_FROM_STUMPS[dl.length]; t1 = (yb - yr) / v; vz0 = (-zr + 0.5 * G * t1 * t1) / t1; vzi = vz0 - G * t1
        vzp = -dl.restitution * vzi; v1 = 0.80 * v; t2 = (PL - yb) / v1
        pre = [(lerp(xr, xb, a), lerp(yr, yb, a), max(0.0, zr + vz0 * (a * t1) - 0.5 * G * (a * t1) ** 2)) for a in np.linspace(0, 1, n)]
        xs = xb * 0.6
        post = [(lerp(xb, xs, a), lerp(yb, PL, a), max(0.0, vzp * (a * t2) - 0.5 * G * (a * t2) ** 2)) for a in np.linspace(0, 1, n)]
        tg = (gate_y - yb) / v1; gate_z = max(0.0, vzp * tg - 0.5 * G * tg * tg); bounce = (xb, yb, 0.0)
    contact = (xb * 0.7, gate_y, gate_z)
    bat = []; end = None
    if dl.wicket and dl.how == "caught" and dl.keeper_catch:        # the wagon spot is where the shot was going, not where it was taken: the keeper takes it behind the stumps
        end = (xb * 0.5, PL + 4.0, 1.0); contact = (xb * 0.7, gate_y, gate_z)
        bat = [(lerp(contact[0], end[0], a), lerp(contact[1], end[1], a), max(0.0, lerp(contact[2], end[2], a) + 4 * 0.5 * a * (1 - a))) for a in np.linspace(0, 1, n)]
    elif dl.wicket and dl.how in ("caught",) and dl.wagon != (0, 0):
        ex, ey = wagon_world(*dl.wagon); end = (ex, ey, dl.catch_z); dist = math.hypot(ex - contact[0], ey - contact[1]); apex = max(contact[2] + 0.5, 0.14 * dist)
        for a in np.linspace(0, 1, n):
            z = lerp(contact[2], dl.catch_z, a) + 4 * (apex - (contact[2] + dl.catch_z) / 2) * a * (1 - a); bat.append((lerp(contact[0], ex, a), lerp(contact[1], ey, a), max(0.0, z)))
    elif dl.wicket and dl.how in ("bowled", "lbw"):
        end = (xb * 0.6, PL, min(gate_z, 0.7))
    return dict(pre=pre, post=post, bat=bat, gate_z=gate_z, bounce=bounce, contact=contact, end=end)


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
                how=dl.how, fielder=dl.fielder, height_m=round(z, 2), height_text=height_label(z, dl.batter_h), keeper=dl.keeper_catch)
