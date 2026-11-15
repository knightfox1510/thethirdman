"""The rest of the situations on top of pitchview.trajectory(): stumped, run out, boundaries (four / six), wide, no-ball, misfield, dropped chance, bouncer, spin.
    kind = classify(dl); extra = situation(dl, tr)      # extra: dict(kind, big, lines, tags) and tr gains drawing keys (throw, rope, gloves, batter_adv, overstep)
Everything here follows the same rule as pitchview.py: DATA from the Cricinfo table and the capture, LEADS from the Cricbuzz commentary, MODEL for everything in between (always labelled)."""
import math
import numpy as np
from pitchview import *


def classify(dl):
    if getattr(dl, "force_kind", ""): return dl.force_kind                    # to show a situation that a richer event hides (e.g. a no-ball that also went for four)
    if dl.wicket: return {"caught": "caught", "bowled": "bowled", "lbw": "lbw", "stumped": "stumped", "run out": "run_out"}.get(dl.how, "wicket")
    if dl.wide: return "wide"
    if dl.six: return "six"
    if dl.four: return "four"
    if dl.noball: return "no_ball"
    if dl.facts.get("drop"): return "dropped"
    if dl.facts.get("misfield"): return "misfield"
    return "ball"


def sector_name(wx, wy, hand="R"):
    """Cricinfo wagon point -> fielding sector (right-hander: x < 180 off side; the table is already mirrored for left-handers, so 'leg side' is the side away from the off side)."""
    xr, yr = wx - 180, wy - 180; ang = math.degrees(math.atan2(abs(xr), yr)); leg = (xr > 0) if hand == "R" else (xr < 0)
    if ang < 15: return "straight down the ground"
    names = [(50, "long on", "long off"), (95, "deep midwicket", "deep cover"), (135, "deep square leg", "deep point"), (181, "fine leg", "third man")]
    for lim, l, o in names:
        if ang < lim: return l if leg else o
    return "fine leg" if leg else "third man"


def _arc(a, b, apex, n=40):
    return [(lerp(a[0], b[0], t), lerp(a[1], b[1], t), max(0.0, lerp(a[2], b[2], t) + 4 * apex * t * (1 - t))) for t in np.linspace(0, 1, n)]


def _bounces(a, b, n=60, amp=0.5, hops=3):
    """A four along the ground: low hops that die away."""
    out = []
    for t in np.linspace(0, 1, n):
        z = amp * (1 - t) * abs(math.sin(math.pi * hops * t)); out.append((lerp(a[0], b[0], t), lerp(a[1], b[1], t), z))
    return out


def situation(dl, tr):
    k = classify(dl); contact = tr["contact"]; S = summary(dl, tr); lines = []; tags = []; big = {"caught": "CAUGHT", "bowled": "BOWLED", "lbw": "LBW", "stumped": "STUMPED", "run_out": "RUN OUT", "six": "SIX", "four": "FOUR",
                                                                                                 "wide": "WIDE", "no_ball": "NO BALL", "misfield": "MISFIELD", "dropped": "DROPPED", "ball": "NO RUNS" if dl.runs == 0 else f"{dl.runs} RUN{'' if dl.runs == 1 else 'S'}"}.get(k, "WICKET")
    f = dl.facts or {}
    if tr["gate_z"] > 0.83 * dl.batter_h: tags.append("ABOVE THE SHOULDER AT THE CREASE (a bouncer)")
    if dl.spin: tags.append("SPIN: flighted, with drift" if dl.drift else "SPIN")
    if dl.round_wicket: tags.append("ROUND THE WICKET")
    tr["tags"] = tags
    if k == "stumped":
        up = (0.0, PL + 1.0, 0.55); tr["gloves"] = up; tr["end"] = up
        tr["bat"] = _arc((tr["post"][-1][0], PL, tr["post"][-1][2]), up, 0.05)
        adv = 1.8 if dl.came_down else 0.9; tr["batter_adv"] = adv
        tr["field"] = dict(name=dl.fielder, position="keeper (standing up)", start=up[:2], catch=up[:2], moved_m=0.0, exceptional=False, side="")
        lines += [f"Stumped by wicket-keeper {dl.fielder or 'the keeper'}, standing up to the spinner (assumed)." if dl.spin else f"Stumped by wicket-keeper {dl.fielder or 'the keeper'}."]
        lines += [("The batter came down the track (commentary); about %.1f m out of the crease is illustrative." % adv) if dl.came_down else "How far he was out of the crease is not in our data."]
        if dl.spin and dl.drift: lines += [f"Flight and drift {dl.drift}wards beat the shot (commentary)."]
    elif k == "run_out":
        thrower = f.get("thrower", ""); end_y = PL if "keeper" in f.get("throw_end", "keeper") or "striker" in f.get("throw_end", "") and "non" not in f.get("throw_end", "") else 0.0
        bowler_direct = bool(f.get("direct_hit")) and thrower and thrower.split()[-1] in dl.bowler
        if bowler_direct: start = (0.6, PL - 17.0); pos = "bowler"
        else:
            pos = f.get("shot_to") or "mid off"; pos = pos if pos in POSITIONS else "mid off"; start = spot(pos, dl.hand)
        stumps = (0.0, end_y, 0.4); tr["throw"] = _arc((start[0], start[1], 0.8), stumps, 1.6 if not bowler_direct else 0.8)
        tr["bat"] = _arc(contact, (start[0], start[1], 0.2), 0.6 if bowler_direct else 3.0)
        tr["field"] = dict(name=thrower, position=pos, start=start, catch=start, moved_m=0.0, exceptional=False, side="", approx=False)
        tr["end"] = stumps; tr["stumps_break"] = stumps
        lines += [(f"Direct hit by the bowler, {thrower}, at the keeper's end." if bowler_direct else f"Throw from {pos}{(' by ' + thrower) if thrower else ''} to the keeper's end; the stumps are broken.")]
        who = dl.out_batter + (" (non-striker)" if dl.out_batter != dl.batter else "")
        lines += [f"Out: {who}. How far he was short is not in our data."]
    elif k in ("six", "four"):
        if dl.wagon != (0, 0):
            ex, ey = wagon_world(*dl.wagon); r = math.hypot(ex, ey - PL / 2); lim = BOUNDARY_M + (5.0 if k == "six" else 0.0)
            if r < BOUNDARY_M * 0.92: ex, ey = (ex * lim / r, PL / 2 + (ey - PL / 2) * lim / r)      # the wagon point can sit inside the rope: extend along the same direction (approximate)
            end = (ex, ey, 0.0); dist = math.hypot(ex - contact[0], ey - contact[1])
            tr["bat"] = _arc(contact, end, min(30.0, 0.22 * dist + 4)) if k == "six" else _bounces(contact, end)
            tr["end"] = end; tr["rope"] = True
            lines += [f"{S['shot'].capitalize()} towards {sector_name(*dl.wagon, hand=dl.hand)}: " + ("over the rope." if k == "six" else "along the ground to the rope.")]
        else: lines += ["Direction not recorded in the data."]
        if dl.noball: lines += ["Also a no ball (free hit follows)."]
    elif k == "wide":
        lines += ["Called wide: outside the wide guideline (distance illustrative).", f"{max(1, dl.runs)} run{'s' if max(1, dl.runs) != 1 else ''} to the total."]
    elif k == "no_ball":
        tr["overstep"] = True; lines += [f"No ball ({f.get('noball_text', 'reason not stated')}); the next ball is a free hit.", "The overstep distance is not in our data (foot drawn illustrative)."]
    elif k in ("misfield", "dropped"):
        pos = dl.position if dl.position in POSITIONS else ""
        if pos:
            st = spot(pos, dl.hand); tr["bat"] = _arc(contact, (st[0], st[1], 0.3), 0.8 if k == "misfield" else 1.5); tr["end"] = (st[0], st[1], 0.3)
            tr["field"] = dict(name="", position=pos, start=st, catch=st, moved_m=0.0, exceptional=False, side="", approx=False)
        lines += [("Fumbled at " + (pos or "the field") + " (commentary): ") + f"{dl.runs} run{'' if dl.runs == 1 else 's'} taken." if k == "misfield" else "A chance put down (commentary)."]
    elif k == "ball":
        lines += [f"Shot: {S['shot']}. Control: {S['control']}."]
    tr["kind"] = k
    return dict(kind=k, big=big, lines=lines, tags=tags)
