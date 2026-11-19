"""Build a Delivery from the Cricbuzz commentary ALONE, for matches that have no Cricinfo ball table (1st / 2nd / 5th ODI, four U19 matches).
    dl = from_commentary("data/cricbuzz/nz_ind_1odi.json", inning=1, over=21.1)
Line, length and shot are READ FROM THE TEXT (leads, often not stated); when the text does not say, the poster says "not stated" and draws the ball at a neutral spot.
Control and the wagon-wheel spot do not exist here. Everything else (bounce, arcs, fielder moves) is the same model as pitchview.py, and the poster carries a COMMENTARY ONLY badge."""
import json, re
from pitchview import *
from pitchview_text import ball_text, load

LINE_WORDS = [("wide outside off", "WIDE_OUTSIDE_OFFSTUMP"), ("outside off", "OUTSIDE_OFFSTUMP"), ("outside leg", "DOWN_LEG"), ("down leg", "DOWN_LEG"), ("down the leg", "DOWN_LEG"), ("leg stump", "ON_THE_STUMPS"),
              ("off stump", "ON_THE_STUMPS"), ("middle stump", "ON_THE_STUMPS"), ("middle and off", "ON_THE_STUMPS"), ("off and middle", "ON_THE_STUMPS"), ("middle and leg", "ON_THE_STUMPS"), ("on the stumps", "ON_THE_STUMPS"),
              ("around off", "OUTSIDE_OFFSTUMP"), ("on off", "ON_THE_STUMPS"), ("fourth stump", "OUTSIDE_OFFSTUMP"), ("fifth stump", "OUTSIDE_OFFSTUMP")]
LEN_EXTRA = [("back of a length", "SHORT_OF_A_GOOD_LENGTH"), ("back of length", "SHORT_OF_A_GOOD_LENGTH"), ("half-volley", "FULL"), ("half volley", "FULL"), ("full and", "FULL"), ("full,", "FULL"), ("full ", "FULL"), ("short", "SHORT")]
SHOT_WORDS = [("left alone", "LEFT_ALONE"), ("leaves", "LEFT_ALONE"), ("lets it go", "LEFT_ALONE"), ("cover drive", "COVER_DRIVE"), ("on-drive", "ON_DRIVE"), ("straight drive", "STRAIGHT_DRIVE"), ("drive", "DRIVE"), ("pull", "PULL"),
              ("hook", "HOOK"), ("cut", "CUT_SHOT"), ("flick", "FLICK"), ("glance", "LEG_GLANCE"), ("reverse sweep", "REVERSE_SWEEP"), ("sweep", "SWEEP_SHOT"), ("defend", "DEFENDED"), ("block", "DEFENDED"), ("slog", "SLOG_SHOT"), ("dab", "DAB"), ("push", "PUSH")]
HOW_RE = re.compile(r"(Caught by ([A-Z][\w'’ -]+?)!!|Caught!!|Bowled!!|Lbw!!|LBW!!|Stumped!!|Run Out!!|Hit wicket!!)")
OUT_RUNOUT_RE = re.compile(r",\s*([A-Z][\w'’ -]+?) Run Out!!")


def _record(cs, inning, over, nth=0):
    key = round(float(over), 1); seen = 0
    for c in cs:
        t = c.get("commText") or ""
        try: ov = round(float(c.get("overNumber")), 1)
        except (TypeError, ValueError): continue
        if ov != key or str(c.get("inningsId")) != str(inning) or len(t) < 40: continue
        if seen < nth: seen += 1; continue
        return c
    return None


def _first(text, table, default=None):
    low = text.lower()
    for w, code in table:
        if w in low: return code
    return default


def from_commentary(path, inning, over, nth=0, hand=None, **assume):
    cs = load(path); c = _record(cs, inning, over, nth)
    if not c: raise ValueError(f"no commentary for {over} in innings {inning}")
    t = re.sub(r"\s+", " ", re.sub(r"B\d\$", " ", c.get("commText") or "")).strip(); f = ball_text(cs, inning, over, nth=nth)
    bat = (c.get("batsmanStriker") or {}).get("batName") or ""; bowl = (c.get("bowlerStriker") or {}).get("bowlName") or ""
    m = re.match(r"(.+?) to (.+?),\s*(.*)$", t); rest = m.group(3) if m else t
    if m and not bat: bowl, bat = m.group(1), m.group(2)
    head = rest[:70].lower(); ev = f.get("events", [])
    how = ""; fielder = ""; out_name = bat
    h = HOW_RE.search(rest)
    if h:
        w = h.group(1)
        how = "caught" if w.startswith("Caught") else {"Bowled!!": "bowled", "Lbw!!": "lbw", "LBW!!": "lbw", "Stumped!!": "stumped", "Run Out!!": "run out", "Hit wicket!!": "hit wicket"}.get(w, "")
        if h.group(2): fielder = h.group(2).strip()
        mo = OUT_RUNOUT_RE.search(", " + rest) if how == "run out" else None
        if mo: out_name = mo.group(1)
    body = rest[rest.find("!!") + 2:] if "!!" in rest else rest                 # the descriptive sentences after the headline
    line = _first(body, LINE_WORDS); length = f.get("length_text") or _first(body, LEN_EXTRA)
    shot = _first(body, SHOT_WORDS, "") or ""
    runs = int(c.get("totalRuns") or 0)
    h_ = hand or ("L" if re.search(r"left-?hander|left-?handed|\bLHB\b", t, re.I) else "R")
    dl = Delivery(bowler=bowl, batter=bat, over=float(over), line=line or "ON_THE_STUMPS", length=length or "GOOD_LENGTH", shot=shot, control=0, runs=runs, wicket=bool(how), how=how, fielder=fielder,
                  keeper_catch=False, wagon=(0, 0), hand=h_, **assume)
    dl.source = "commentary"; dl.line_guess = line is None; dl.length_guess = length is None; dl.out_batter = out_name
    dl.facts = f; dl.events = ev; dl.four = "FOUR" in ev; dl.six = "SIX" in ev
    dl.wide = bool(re.search(r"\bwide\b", head)) and "run" not in head.split("wide")[0][-12:] if False else bool(re.search(r"\bwides?\b|called a wide|is called wide", head + " " + body[:60].lower())) and not how
    dl.noball = bool(re.search(r"no.?ball", head)); dl.free_hit = "free hit" in t.lower()
    dl.byes = runs if re.search(r"\bbyes?\b", head) and "leg" not in head else 0; dl.legbyes = runs if "leg bye" in head else 0
    if "speed_kph" in f and "pace_kmh" not in assume: dl.pace_kmh = f["speed_kph"]
    if f.get("catcher"): dl.fielder = f["catcher"]
    dl.position = f.get("position", ""); dl.side = f.get("side", ""); dl.exceptional = f.get("exceptional", ""); dl.bounce = f.get("bounce", ""); dl.movement = f.get("movement", "")
    dl.spin = bool(f.get("spin")); dl.drift = f.get("drift", ""); dl.came_down = bool(f.get("came_down")); dl.round_wicket = bool(f.get("round")); dl.left_arm = bool(f.get("left_arm")); dl.swing = f.get("swing", "")
    if f.get("bouncer") and not dl.bounce: dl.bounce = "extra"
    if dl.spin and "pace_kmh" not in assume and "speed_kph" not in f: dl.pace_kmh, dl.release_z, dl.restitution = 85.0, 2.0, 0.50
    if dl.how == "caught" and dl.fielder and dl.fielder.split()[-1] in dl.bowler: dl.position = "bowler"
    return dl
