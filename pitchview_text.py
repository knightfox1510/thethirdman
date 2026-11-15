"""Reads the Cricbuzz commentary text for one delivery and pulls out facts the Cricinfo ball table does not have:
speed (kph), where a catch was taken and by whom, how the fielder moved (diving, one-handed, to his left/right), how the ball behaved (nipped back, seamed away, kept low, extra bounce),
and the length the commentator names. These are LEADS (CLAUDE.md: Cricbuzz notes are leads to verify, never text to copy): the module records WHAT was said as structured fields,
never the sentence, and flags a disagreement with the Cricinfo table instead of silently choosing a side.
    facts = ball_text("data/cricbuzz/nz_ind_4odi.json", inning=2, over=0.1)"""
import json, re

POS = ("first slip|second slip|third slip|fourth slip|fly slip|slip|gully|backward point|deep point|point|short cover|extra cover|deep extra cover|deep cover|cover point|cover|"
       "mid-?off|mid-?on|short mid-?wicket|deep mid-?wicket|mid-?wicket|backward square leg|deep backward square leg|deep square leg|square leg|short leg|leg slip|"
       "deep fine leg|fine leg|short third man|third man|long-?on|long-?off|cow corner|silly point|silly mid-?off|silly mid-?on|wicket-?keeper|keeper|bowler")
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


def _norm_pos(p):
    p = re.sub(r"\s+", " ", p.lower().replace("-", " ")).strip()
    return {"midoff": "mid off", "midon": "mid on", "midwicket": "mid wicket", "wicketkeeper": "keeper", "wicket keeper": "keeper"}.get(p.replace(" ", ""), p).replace("mid wicket", "midwicket")


def load(path):
    return json.load(open(path, encoding="utf-8"))["comments"]


def ball_text(comments_or_path, inning, over):
    """Facts for one ball (inning 1/2, over like 0.1). Returns {} if the capture has no text for it."""
    cs = load(comments_or_path) if isinstance(comments_or_path, str) else comments_or_path
    key = round(float(over), 1)
    for c in cs:
        t = c.get("commText") or ""
        try: ov = round(float(c.get("overNumber")), 1)
        except (TypeError, ValueError): continue
        if ov != key or c.get("inningsId") not in (inning, str(inning), None): continue
        if not (c.get("ballNbr") or 0) or len(t) < 40: continue
        t1 = re.sub(r"B\d\$", " ", re.sub(r"\s+", " ", t))
        out = {"has_text": True}
        m = SPEED_RE.search(t1)
        if m: out["speed_kph"] = float(m.group(1))
        pos = POS_RE.findall(t1)
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
        return out
    return {}
