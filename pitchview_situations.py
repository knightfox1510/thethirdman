"""The rest of the situations on top of pitchview.trajectory(): stumped, run out, boundaries (four / six), wide, no-ball, misfield, dropped chance, bouncer, spin.
    kind = classify(dl); extra = situation(dl, tr)      # extra: dict(kind, big, lines, tags) and tr gains drawing keys (throw, rope, gloves, batter_adv, overstep)
Everything here follows the same rule as pitchview.py: DATA from the Cricinfo table and the capture, LEADS from the Cricbuzz commentary, MODEL for everything in between (always labelled)."""
import math
import numpy as np
from pitchview import *


def classify(dl):
    if getattr(dl, "force_kind", ""): return dl.force_kind                    # to show a situation that a richer event hides (e.g. a no-ball that also went for four)
    f = dl.facts or {}
    if dl.wicket:
        if dl.how == "caught" and dl.position == "bowler": return "caught_bowled"
        h = (dl.how or "").lower()
        for key, kind in (("hit wicket", "hit_wicket"), ("handled", "handled"), ("obstruct", "obstruct"), ("timed out", "timed_out"), ("retired", "retired")):
            if key in h: return kind
        return {"caught": "caught", "bowled": "bowled", "lbw": "lbw", "stumped": "stumped", "run out": "run_out"}.get(h, "wicket")
    if f.get("runout_miss"): return "runout_miss"
    if dl.wide: return "wide"
    if dl.six: return "six"
    if dl.four: return "four"
    if dl.noball: return "no_ball"
    if f.get("drop"): return "dropped"
    if f.get("review"): return "review"
    if f.get("misfield"): return "misfield"
    if dl.shot == "LEFT_ALONE" and dl.runs == 0: return "leave"
    if dl.byes: return "bye"
    if dl.legbyes: return "leg_bye"
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
                                                                                                 "wide": "WIDE", "no_ball": "NO BALL", "misfield": "MISFIELD", "dropped": "DROPPED", "runout_miss": "RUN-OUT MISSED", "review": "REVIEW", "leave": "LEFT ALONE", "bye": "BYE", "leg_bye": "LEG BYE", "caught_bowled": "CAUGHT & BOWLED", "hit_wicket": "HIT WICKET", "handled": "HANDLED THE BALL", "obstruct": "OBSTRUCTING", "timed_out": "TIMED OUT", "retired": "RETIRED", "ball": "NO RUNS" if dl.runs == 0 else f"{dl.runs} RUN{'' if dl.runs == 1 else 'S'}"}.get(k, "WICKET")
    f = dl.facts or {}
    if tr["gate_z"] > 0.83 * dl.batter_h: tags.append("ABOVE THE SHOULDER AT THE CREASE (a bouncer)")
    if dl.spin: tags.append("SPIN: flighted, with drift" if dl.drift else "SPIN")
    if dl.round_wicket: tags.append("ROUND THE WICKET")
    if dl.left_arm: tags.append("LEFT-ARM BOWLER")
    if dl.free_hit: tags.append("FREE HIT (the previous ball was a no ball)")
    if dl.swing: tags.append(f"SWING {dl.swing.upper()} IN THE AIR" if dl.swing in ("in", "away") else f"{dl.swing.upper()}")
    if f.get("bouncer"): tags.append("BOUNCER")
    if f.get("overthrow"): tags.append("OVERTHROW")
    if f.get("edge"): tags.append(f"{f['edge'].upper()}")
    if f.get("body") and k not in ("lbw",): tags.append(f"HIT ON THE BODY: {f['body'].upper()}")
    if dl.control == 2 and dl.runs == 0 and not dl.wicket and dl.shot not in ("LEFT_ALONE", "DEFENDED", ""): tags.append("BEATEN: the batter was not in control")
    for e in dl.events:
        if e in ("FIFTY", "HUNDRED", "TEAM_FIFTY", "TEAM_HUNDRED", "MAIDEN_OVER"): tags.append(e.replace("_", " "))
    if f.get("review"): tags.append("REVIEW: " + (", ".join(f.get("review_notes", [])) or "decision stands") + "")
    tr["tags"] = tags
    if k == "stumped":
        up = (0.0, PL + 1.0, 0.55); tr["gloves"] = up; tr["end"] = up
        tr["bat"] = _arc((tr["post"][-1][0], PL, tr["post"][-1][2]), up, 0.05)
        adv = 1.8 if dl.came_down else 0.9; tr["batter_adv"] = adv
        tr["field"] = dict(name=dl.fielder, position="keeper (standing up)", start=up[:2], catch=up[:2], moved_m=0.0, exceptional=False, side="")
        lines += [f"Stumped by wicket-keeper {dl.fielder or 'the keeper'}, standing up to the spinner (assumed)." if dl.spin else f"Stumped by wicket-keeper {dl.fielder or 'the keeper'}."]
        lines += [("The batter came down the track; about %.1f m out of the crease is illustrative." % adv) if dl.came_down else "Distance out of the crease illustrative."]
        if dl.spin and dl.drift: lines += [f"Flight and drift {dl.drift}wards beat the shot "]
    elif k == "run_out":
        thrower = f.get("thrower", ""); bowler_direct = bool(f.get("direct_hit")) and thrower and thrower.split()[-1] in dl.bowler
        pos = "bowler" if bowler_direct else (f.get("shot_to") if f.get("shot_to") in POSITIONS else "")
        te = f.get("throw_end", "")
        if pos and te:
            end_y = 0.0 if "bowler" in te else PL; start = (0.6, PL - 17.0) if bowler_direct else spot(pos, dl.hand)
            stumps = (0.0, end_y, 0.4); tr["throw"] = _arc((start[0], start[1], 0.8), stumps, 1.6 if not bowler_direct else 0.8)
            tr["bat"] = _arc(contact, (start[0], start[1], 0.2), 0.6 if bowler_direct else 3.0)
            tr["field"] = dict(name=thrower, position=pos, start=start, catch=start, moved_m=0.0, exceptional=False, side="", approx=False)
            tr["end"] = stumps; tr["stumps_break"] = stumps
            lines += [(f"Direct hit by the bowler, {thrower}, at the {'keeper' if end_y else 'bowler'}'s end." if bowler_direct else f"Throw from {pos}{(' by ' + thrower) if thrower else ''} to the {'keeper' if end_y else 'bowler'}'s end; the stumps are broken.")]
        else: lines += ["Run out: the throw is not shown."]
        who = dl.out_batter + (" (non-striker)" if dl.out_batter != dl.batter else "")
        lines += [f"Out: {who}. "]
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
        tr["overstep"] = True; lines += [f"No ball ({f.get('noball_text', 'reason not stated')}); the next ball is a free hit.", "The overstep is drawn illustratively."]
    elif k == "misfield":
        pos = dl.position if dl.position in POSITIONS else ""
        if pos:
            st = spot(pos, dl.hand); tr["bat"] = _arc(contact, (st[0], st[1], 0.3), 0.8 if k == "misfield" else 1.5); tr["end"] = (st[0], st[1], 0.3)
            tr["field"] = dict(name="", position=pos, start=st, catch=st, moved_m=0.0, exceptional=False, side="", approx=False)
        lines += [("Fumbled at " + (pos or "the field") + ": ") + f"{dl.runs} run{'' if dl.runs == 1 else 's'} taken."]
    elif k == "dropped":
        who = f.get("dropper", ""); pos = dl.position if dl.position in POSITIONS else (f.get("shot_to") if f.get("shot_to") in POSITIONS else "")
        if pos: st = spot(pos, dl.hand)
        elif dl.wagon != (0, 0): st = wagon_world(*dl.wagon)
        else: st = None
        if st:
            tr["bat"] = _arc(contact, (st[0], st[1], 1.0), 1.2); tr["end"] = (st[0], st[1], 1.0); tr["cross"] = (st[0], st[1], 1.0)
            tr["field"] = dict(name=who, position=pos or "outfield (wagon spot, approx.)", start=st, catch=st, moved_m=0.0, exceptional=False, side="", approx=not pos)
        lines += [f"Chance put down{' by ' + who if who else ''}{' at ' + pos if pos else ''} "]
        if f.get("edge"): lines += [f"It came off the {f['edge']}."]
    elif k == "runout_miss":
        thrower = f.get("thrower", ""); pos = f.get("shot_to") if f.get("shot_to") in POSITIONS else ""; te = f.get("throw_end", "")
        if pos and te:
            start = spot(pos, dl.hand); end_y = 0.0 if "bowler" in te else PL; stumps = (0.0, end_y, 0.4); miss = (0.7, end_y, 0.4)
            tr["throw"] = _arc((start[0], start[1], 0.9), miss, 1.2); tr["bat"] = _arc(contact, (start[0], start[1], 0.2), 3.0); tr["end"] = miss
            tr["field"] = dict(name=thrower, position=pos, start=start, catch=start, moved_m=0.0, exceptional=False, side="", approx=False); tr["missed_stumps"] = stumps
            lines += [f"Throw from {pos} at the {'bowler' if end_y == 0 else 'keeper'}'s end misses the stumps; the batter is safe ({dl.runs} run{'' if dl.runs == 1 else 's'})."]
        else: lines += ["A throw at the stumps missed; where it came from is not stated, so no throw is drawn."]
        lines += ["The batter's distance short of the crease is not shown."]
    elif k == "review":
        lines += ["A review was taken."]
    elif k == "leave":
        lines += [f"Left alone: the batter judged the line ({S['line'].lower()}). Control: {S['control']}."]
    elif k in ("bye", "leg_bye"):
        tr["bat"] = _arc((tr["post"][-1][0], PL, tr["post"][-1][2]), (tr["post"][-1][0] * 1.5, PL + 16.0, 0.0), 0.5); tr["end"] = (tr["post"][-1][0] * 1.5, PL + 16.0, 0.0)
        n = dl.byes or dl.legbyes; lines += [f"{n} run{'s' if n != 1 else ''} as {'byes' if k == 'bye' else 'leg byes'}: not off the bat."]
    elif k == "caught_bowled":
        lines += [f"Caught and bowled by {dl.bowler}: back to the bowler."]
        tr["field"] = dict(name=dl.bowler, position="bowler", start=(0.6, PL - 17.0), catch=(0.6, PL - 17.0), moved_m=0.0, exceptional=bool(dl.exceptional), side="")
    elif k == "hit_wicket":
        tr["end"] = (0.0, PL, 0.5); tr["stumps_break"] = tr["end"]; lines += ["The batter's bat or body disturbed his own wicket (hit wicket)."]
    elif k in ("handled", "obstruct", "timed_out", "retired"):
        lines += [{"handled": "Dismissed for handling the ball.", "obstruct": "Dismissed for obstructing the field.", "timed_out": "Timed out: the next batter was not ready to face a ball in time. No ball was bowled.", "retired": "Retired."}[k]]
    elif k == "ball":
        lines += [(f"Shot: {S['shot']}. " if S['shot'] else "") + f"Control: {S['control']}."]
    tr["kind"] = k
    return dict(kind=k, big=big, lines=lines, tags=tags)
