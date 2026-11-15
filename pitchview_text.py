"""Reads the Cricbuzz commentary text for one delivery and pulls out facts the Cricinfo ball table does not have:
speed (kph), where a catch was taken and by whom, how the fielder moved (diving, one-handed, to his left/right), how the ball behaved (nipped back, seamed away, kept low, extra bounce),
and the length the commentator names. These are LEADS (CLAUDE.md: Cricbuzz notes are leads to verify, never text to copy): the module records WHAT was said as structured fields,
never the sentence, and flags a disagreement with the Cricinfo table instead of silently choosing a side.
    facts = ball_text("data/cricbuzz/nz_ind_4odi.json", inning=2, over=0.1)"""
import json, re

POS = ("first slip|second slip|third slip|fourth slip|fly slip|slip|gully|backward point|deep point|point|short cover|extra cover|deep extra cover|deep cover|cover point|cover|"
       "mid-?off|mid-?on|short mid-?wicket|deep mid-?wicket|mid-?wicket|backward square leg|deep backward square leg|deep square leg|square leg|short leg|leg slip|"
       "deep fine leg|fine leg|short third man|third man|long-?on|long-?off|cow corner|silly point|silly mid-?off|silly mid-?on|wicket-?keeper|keeper|bowler")
POS = POS.replace("-?", "[- ]?")
POS_RE = re.compile(r"\b(?:at|in|by|to)\s+(?:the\s+)?(%s)\b" % POS, re.I)
SPEED_RE = re.compile(r"(\d{2,3}(?:\.\d)?)\s?kph", re.I)
SIDE_RE = re.compile(r"(?:to|on)\s+his\s+(left|right)", re.I)
EXC_RE = re.compile(r"\b(diving|dives?|dived|one-?handed|full stretch|leaps?|leaping|jumps?|running|sprint\w*|back-?pedal\w*|tumbl\w*|reflex|stunning|screamer|superb|brilliant|fine two-handed)\b", re.I)
LEN_WORDS = [("short of a good length", "SHORT_OF_A_GOOD_LENGTH"), ("short of length", "SHORT_OF_A_GOOD_LENGTH"), ("short-of-a-good-length", "SHORT_OF_A_GOOD_LENGTH"), ("good length", "GOOD_LENGTH"),
             ("yorker", "YORKER"), ("full toss", "FULL_TOSS"), ("full length", "FULL"), ("fuller", "FULL"), ("pitched up", "FULL"), ("short ball", "SHORT"), ("bouncer", "SHORT")]
MOVE = [(r"nip(?:s|ped)? back|moves? (?:back )?in|in-?seam|jag(?:s|ged)? back|comes? in|inward movement", "in"), (r"seams? away|seam movement away|out-?seam|jag(?:s|ging|ged)? away|moves? away|shapes? away|angle away", "away")]
LOW_RE = re.compile(r"keeps? (?:a bit |a little )?low|stays? low|stayed low|shoots? (?:through|under)|skids?|grubber", re.I)
BOUNCE_RE = re.compile(r"extra bounce|bounces? (?:more|steeply)|steep bounce|bounce is tough|leaps? up|lifts?|rears?|climbs", re.I)
SPIN_RE = re.compile(r"turn(?:s|ed|ing)? (?:sharply|a lot|big|away|in)|spun|spinning|grips?|drift", re.I)
REVIEW_RE = re.compile(r"(umpire'?s call|ball-?tracking|three reds|hitting the stumps|missing the stumps|sonic|hotspot|review)", re.I)


DROP_RE = re.compile(r"\b(dropped|drops|dropping|put down|grassed|spills?|spilled|burst through)\b", re.I)
MISFIELD_RE = re.compile(r"\b(fumbl\w*|misfield\w*|mis-field\w*|lets it through|through the legs|bobbled?)\b", re.I)
OVERTHROW_RE = re.compile(r"over-?throw", re.I)
DIRECT_RE = re.compile(r"direct[- ]hit", re.I)
RUNOUT_END_RE = re.compile(r"(keeper'?s end|bowler'?s end|non-striker'?s end|striker'?s end)", re.I)
THROWER_RE = re.compile(r"\b([A-Z][a-z]+(?: [A-Z][a-z]+)?) (?:charges in|collects|picks up|gathers|fires|throws|swoops|runs in|is quick to collect)", re.I)
TOWARDS_RE = re.compile(r"(?:towards|to|at)\s+(%s)\b" % POS, re.I)
SPIN_CUE_RE = re.compile(r"\b(tossed up|flighted|flight|loop(?:s|ed|y)?|dragged down|googly|wrong'?un|doosra|carrom|arm ball|turning|turned|turns|spinner|spun)\b", re.I)
DRIFT_RE = re.compile(r"drift\w*\s+(?:into|in to|towards)\s+the\s+(left|right)-?hander|drift\w*\s+(away)", re.I)
COMEDOWN_RE = re.compile(r"(come[sd]? down the (?:track|wicket|pitch)|charg\w+|dances? down|steps? out|advanc\w+ down)", re.I)
ROUND_RE = re.compile(r"round the wicket", re.I)
LEFTARM_RE = re.compile(r"left-?arm|left-?armer", re.I)
NOBALL_RE = re.compile(r"(no.?ball|overstep\w*|front.?foot|free hit)", re.I)


SWING_RE = re.compile(r"(?:swing\w*|shap(?:es|ed|ing)|banana)[^.]{0,25}?\b(away|in)\b|\b(reverse swing|late swing|conventional swing)", re.I)
EDGE_RE = re.compile(r"\b(inside edge|outside edge|top edge|thick edge|thin edge|leading edge|under-?edge|bottom edge|edge[sd]?)\b", re.I)
BODY_RE = re.compile(r"\b(helmet|grille|on the pad|thigh pad|on the body|ribs|gloves?|finger|forearm|hit on the (?:arm|shoulder|chest|head)|rapped)\b", re.I)
BOUNCER_RE = re.compile(r"\b(bouncer|banged in short|short ball|short and (?:rising|nasty)|bumper)\b", re.I)
DROPPER_RE = re.compile(r"\b([A-Z][a-z]+)\b[^.]{0,45}?(?:puts? (?:him )?down|drops?|dropped|spill\w*|lets it go|puts down)|([A-Z][a-z]+) (?:- |is )the culprit|[Ff]lies to ([A-Z][a-z]+)")
REVIEW_OUT_RE = re.compile(r"(three reds|umpire'?s call|overturn\w*|decision stays|stays with|clipping|missing the stumps|going over|pitched outside leg|pitching outside leg|impact outside|inside edge|ultra ?edge)", re.I)
HIT_WICKET_RE = re.compile(r"hit[- ]wicket|treads on|dislodg", re.I)


def _norm_pos(p):
    p = re.sub(r"\s+", " ", p.lower().replace("-", " ")).strip()
    return {"midoff": "mid off", "midon": "mid on", "midwicket": "mid wicket", "wicketkeeper": "keeper", "wicket keeper": "keeper"}.get(p.replace(" ", ""), p).replace("mid wicket", "midwicket")


def load(path):
    return json.load(open(path, encoding="utf-8"))["comments"]


def ball_text(comments_or_path, inning, over, nth=0):
    """Facts for one ball (inning 1/2, over like 0.1). Returns {} if the capture has no text for it."""
    cs = load(comments_or_path) if isinstance(comments_or_path, str) else comments_or_path
    key = round(float(over), 1); seen = 0
    for c in cs:
        t = c.get("commText") or ""
        try: ov = round(float(c.get("overNumber")), 1)
        except (TypeError, ValueError): continue
        if ov != key or c.get("inningsId") not in (inning, str(inning), None): continue
        if not (c.get("ballNbr") or 0) or len(t) < 40: continue
        if seen < nth: seen += 1; continue                                  # the nth delivery with this over number (no-balls and wides are bowled again under the same number)
        t1 = re.sub(r"B\d\$", " ", re.sub(r"\s+", " ", t))
        out = {"has_text": True}
        m = SPEED_RE.search(t1)
        if m: out["speed_kph"] = float(m.group(1))
        tp = t1.replace("-", " "); pos = POS_RE.findall(tp)
        if pos: out["position"] = _norm_pos(pos[-1] if re.search(r"caught|catch|taken|snaffle", t1, re.I) else pos[0])
        m = re.search(r"(?:Caught|Stumped) by ([A-Z][A-Za-z'\-]+(?: [A-Z][A-Za-z'\-]+){0,2})!", t1)
        if m: out["catcher"] = m.group(1)
        m = SIDE_RE.search(t1)
        if m: out["side"] = m.group(1).lower()
        if EXC_RE.search(t1) and re.search(r"caught|catch", t1, re.I): out["exceptional"] = EXC_RE.search(t1).group(1).lower()
        for pat, name in MOVE:
            if re.search(pat, t1, re.I): out["movement"] = name; break
        if LOW_RE.search(t1): out["bounce"] = "low"
        elif BOUNCE_RE.search(t1): out["bounce"] = "extra"
        if SPIN_RE.search(t1): out["spin"] = True
        low = t1.lower()
        for w, code in LEN_WORDS:
            if w in low: out["length_text"] = code; break
        if REVIEW_RE.search(t1): out["review"] = True
        if DROP_RE.search(t1) and re.search(r"catch|chance|edge", t1, re.I): out["drop"] = True
        if MISFIELD_RE.search(t1): out["misfield"] = True
        if OVERTHROW_RE.search(t1): out["overthrow"] = True
        if DIRECT_RE.search(t1): out["direct_hit"] = True
        m = RUNOUT_END_RE.search(t1)
        if m: out["throw_end"] = m.group(1).lower().replace("'", "")
        m = THROWER_RE.search(t1)
        if m: out["thrower"] = m.group(1)
        m = re.search(r"(?:drives?|hits?|pushes|pushed|flicks?|pulls?|cuts?|sweeps?|plays?|nudges?|works?|steers?)[^.]{0,40}?(?:towards|to)\s+(%s)\b" % POS, tp, re.I)
        if m: out["shot_to"] = _norm_pos(m.group(1))
        if SPIN_CUE_RE.search(t1): out["spin"] = True
        m = DRIFT_RE.search(t1)
        if m: out["drift"] = "in" if m.group(1) else "away"
        if COMEDOWN_RE.search(t1): out["came_down"] = True
        if ROUND_RE.search(t1): out["round"] = True
        if LEFTARM_RE.search(t1): out["left_arm"] = True
        if NOBALL_RE.search(t1): out["noball_text"] = NOBALL_RE.search(t1).group(1).lower()
        ev = [e for e in str(c.get("event") or "").split(",") if e and e not in ("NONE", "over-break")]
        if ev: out["events"] = ev
        m = SWING_RE.search(t1)
        if m: out["swing"] = (m.group(1) or "reverse").lower()
        m = EDGE_RE.search(t1)
        if m: out["edge"] = m.group(1).lower().replace("-", " ")
        if BODY_RE.search(t1): out["body"] = BODY_RE.search(t1).group(1).lower()
        if BOUNCER_RE.search(t1): out["bouncer"] = True
        if "DROPPED" in ev or DROP_RE.search(t1):
            m = DROPPER_RE.search(t1)
            if m: out["dropper"] = next(g for g in m.groups() if g)
            out["drop"] = True
        if "RUNOUT_MISS" in ev: out["runout_miss"] = True
        if "UDRS" in ev or re.search(r"\breview\b", t1, re.I):
            out["review"] = True; m = REVIEW_OUT_RE.findall(t1); out["review_notes"] = list(dict.fromkeys(x.lower() for x in m))[:3]
        if HIT_WICKET_RE.search(t1): out["hit_wicket"] = True
        return out
    return {}
