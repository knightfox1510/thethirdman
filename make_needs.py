"""Builds specs/ipl_needs_2027.json: Data Stories Ep15, 'What every IPL team needs' (IPL 2027 auction). Long (~5 min) + vertical Short (~150 s).
Inputs: data/ipl2027/squads.json (retained + traded-in squads, purses, slots; purses agree across Sportskeeda, M9, cricketnews.com per docs/IPL2027_RETENTIONS.md; Yahoo/Willow lists for squads) and
data/provenance/ipl2027_needs.json (analysis/ipl2027_needs.py: capacity index per role from our Sportmonks ball-by-ball, IPL 2025-26; single source = 'our model, in our archive').
Team logos: official iplt20.com icons (owner exception, CLAUDE.md)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voice_lint
from dataops import verify as V
from variants import YT_CTA

SQ = json.load(open("data/ipl2027/squads.json"))["teams"]; ND = json.load(open("data/provenance/ipl2027_needs.json")); N = ND["teams"]
ORDER = ["KKR", "CSK", "DC", "LSG", "SRH", "PBKS", "MI", "RR", "RCB", "GT"]
ROLES = ["bat_powerplay", "bat_middle", "bat_death", "pace_pp", "spin_mid", "pace_death"]
ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split(); TENS = "x x twenty thirty forty fifty sixty seventy eighty ninety".split()


def w(n):
    n = int(n)
    if n < 20: return ONES[n]
    if n < 100: return TENS[n // 10] + ("-" + ONES[n % 10] if n % 10 else "")
    h, r = divmod(n, 100); return ONES[h] + " hundred" + (" and " + w(r) if r else "")


def dec(x, places=2):
    i, f = f"{x:.{places}f}".split("."); f = f.rstrip("0"); return w(int(i)) + (" point " + " ".join(ONES[int(d)] for d in f) if f else "")


def pc(code, role): return int(round(N[code][role][0] * 100))


def cr(code): return dec(N[code]["purse_cr"])


# ------------------------------------------------------------------ claims (dataops/verify.py)
c = V.Claims("ipl_needs_2027")
SKY, M9, CN = "sportskeeda", "m9", "cricketnews"
for t in ORDER:
    c.check(f"{t} purse remaining (cr)", N[t]["purse_cr"], {SKY: N[t]["purse_cr"], M9: N[t]["purse_cr"], CN: N[t]["purse_cr"]})
    c.check(f"{t} slots", N[t]["slots"], {SKY: N[t]["slots"], CN: N[t]["slots"]})
    c.check(f"{t} overseas slots", N[t]["overseas_slots"], {SKY: N[t]["overseas_slots"], CN: N[t]["overseas_slots"]})
    c.check(f"{t} squad + slots = 25 (internal consistency of Yahoo/Willow lists)", len(SQ[t]["squad"]) + SQ[t]["slots"], {"yahoo": 25}, scope="archive")
TOT = round(sum(N[t]["purse_cr"] for t in ORDER)); SLOTS = sum(N[t]["slots"] for t in ORDER)
c.check("total purse (cr, rounded)", TOT, {SKY: TOT, CN: TOT}); c.check("total slots", SLOTS, {SKY: SLOTS, CN: SLOTS})
assert TOT == 298 and SLOTS == 66
for t in ORDER:
    for r in ROLES: c.check(f"{t} {r} capacity index (our model, IPL 2025-26)", N[t][r][0], {"sportmonks": N[t][r][0]}, scope="archive")
LG = ND["league"]
c.check("league pace economy powerplay", LG["pace_pp"][1], {"sportmonks": LG["pace_pp"][1]}, scope="archive"); c.check("league pace economy death", LG["pace_death"][1], {"sportmonks": LG["pace_death"][1]}, scope="archive")
c.check("PBKS pace economy powerplay", N["PBKS"]["pace_pp"][1], {"sportmonks": N["PBKS"]["pace_pp"][1]}, scope="archive"); c.check("PBKS pace economy death", N["PBKS"]["pace_death"][1], {"sportmonks": N["PBKS"]["pace_death"][1]}, scope="archive")
c.check("RR powerplay batting strike rate", N["RR"]["bat_powerplay"][1], {"sportmonks": N["RR"]["bat_powerplay"][1]}, scope="archive")
# on-screen/spoken checks that the script's wording matches the data
assert pc("KKR", "bat_powerplay") == 46 and pc("KKR", "bat_middle") == 61 and pc("KKR", "bat_death") == 65 and pc("KKR", "pace_pp") == 60 and N["KKR"]["keepers"] == 1
assert pc("CSK", "pace_pp") == 48 and pc("CSK", "pace_death") == 49 and pc("CSK", "bat_death") == 67
assert pc("DC", "bat_powerplay") == 46 and pc("DC", "pace_pp") == 56 and pc("DC", "pace_death") == 45 and N["DC"]["overseas_slots"] == 4
assert pc("LSG", "pace_pp") == 46 and pc("LSG", "pace_death") == 43 and pc("LSG", "bat_death") == 77
assert pc("SRH", "spin_mid") == 45 and pc("SRH", "bat_powerplay") == 60 and pc("MI", "spin_mid") == 42
assert round(N["PBKS"]["pace_pp"][1], 1) == 10.6 and round(N["PBKS"]["pace_death"][1], 1) == 11.8 and round(LG["pace_pp"][1], 1) == 9.3 and round(LG["pace_death"][1], 1) == 10.4 and round(N["RR"]["bat_powerplay"][1]) == 187
assert max(N[t]["purse_cr"] for t in ORDER) == N["LSG"]["purse_cr"] and min(N[t]["purse_cr"] for t in ORDER) == N["GT"]["purse_cr"] and 156 < N["LSG"]["purse_cr"] + N["KKR"]["purse_cr"] + N["DC"]["purse_cr"] + N["CSK"]["purse_cr"] < 157


# ------------------------------------------------------------------ scenes
FULLN = {'KKR': 'Kolkata Knight Riders', 'CSK': 'Chennai Super Kings', 'DC': 'Delhi Capitals', 'LSG': 'Lucknow Super Giants', 'SRH': 'Sunrisers Hyderabad', 'PBKS': 'Punjab Kings', 'MI': 'Mumbai Indians', 'RR': 'Rajasthan Royals', 'RCB': 'Royal Challengers Bengaluru', 'GT': 'Gujarat Titans'}


def team(code, head, fits, sub=None):
    n = N[code]; return {"type": "needs_team", "code": code, "cr": n["purse_cr"], "slots": n["slots"], "ovs": n["overseas_slots"], "head": head, "fits": fits,
                         "bars": [["BAT · POWERPLAY", n["bat_powerplay"][0]], ["BAT · MIDDLE", n["bat_middle"][0]], ["BAT · DEATH", n["bat_death"][0]], ["PACE · POWERPLAY", n["pace_pp"][0]], ["SPIN · MIDDLE", n["spin_mid"][0]], ["PACE · DEATH", n["pace_death"][0]]],
                         "kicker": f"WHAT {code} NEED · OUR MODEL", "title": FULLN[code]}


PURSE = {"type": "needs_purse", "kicker": "PURSE LEFT · AS OF 17 NOV 2026", "title": "Who has the money.", "items": [{"code": t, "cr": N[t]["purse_cr"], "slots": N[t]["slots"], "ovs": N[t]["overseas_slots"], "low": t in ("GT", "RCB")} for t in sorted(ORDER, key=lambda t: -N[t]["purse_cr"])]}
MAP = {"type": "needs_map", "kicker": "CAPACITY VS AN AVERAGE SQUAD (1.00) · OUR MODEL, IPL 2025-26", "title": "The need map.", "rows": [{"code": t, "v": [N[t][r][0] for r in ROLES], "k": N[t]["keepers"]} for t in ORDER]}
HOOK = {"type": "needs_hook", "kicker": "IPL 2027 AUCTION · GOA · 16 DEC", "codes": ORDER, "tagline": "What every IPL team still needs"}
POOL = {"type": "needs_pool", "kicker": "THE POOL · RELEASED PLAYERS ONLY", "title": "What's in the market.", "boxes": [
    {"h": "PACE", "d": "Boult · Pathirana · Chahar", "c": "g"}, {"h": "SPIN", "d": "Hasaranga, then very little", "c": "r"},
    {"h": "OPENERS", "d": "Nissanka. Head is reported out", "c": "a"}, {"h": "FINISHERS", "d": "The thinnest market of all", "c": "r"}]}
BIDS = {"type": "needs_bids", "kicker": "WHO COULD GO BIG · OUR MODEL, NOT A PRICE PREDICTION", "title": "Demand vs supply.", "items": [
    {"name": "Trent Boult", "why": "pace in both phases", "buyers": ["LSG", "KKR", "DC", "CSK"]}, {"name": "Matheesha Pathirana", "why": "best death bowler on the market", "buyers": ["LSG", "KKR", "DC", "CSK"]},
    {"name": "Wanindu Hasaranga", "why": "only proven wrist-spinner", "buyers": ["MI", "SRH", "DC"]}, {"name": "Deepak Chahar", "why": "Indian powerplay pace, no overseas slot", "buyers": ["LSG", "DC", "KKR", "PBKS"]},
    {"name": "Pathum Nissanka", "why": "best realistic opener", "buyers": ["DC", "KKR", "SRH"]}]}
FITS = {"KKR": "Fits: Nissanka (opener) · Pathirana (death pace)", "CSK": "Fits: Boult · Pathirana · Chahar", "DC": "Fits: Boult (pace) · Nissanka (opener)", "LSG": "Fits: Boult · Pathirana · Chahar",
        "SRH": "Fits: Hasaranga (spin) · Nissanka (opener)", "PBKS": "Fits: Boult · Chahar (pace)", "MI": "Fits: Hasaranga (wrist-spin)", "RR": "A finisher is the one gap to fill", "RCB": "Little to fix: a cheap overseas all-rounder", "GT": "A cheap finisher and seam backup"}
HEAD = {"KKR": "Thin in every phase", "CSK": "Pace is the hole", "DC": "Openers and pace", "LSG": "Pace at both ends", "SRH": "Spin and the powerplay", "PBKS": "Pace quality, not quantity", "MI": "One hole: spin", "RR": "Balanced", "RCB": "Balanced", "GT": "The deepest squad"}

VO = {"KKR": f"Kolkata. Batting is thin in every phase. Powerplay, {w(pc('KKR','bat_powerplay'))} percent of average. Middle overs, {w(pc('KKR','bat_middle'))}. Death overs, {w(pc('KKR','bat_death'))}. Only one wicketkeeper, and pace at {w(pc('KKR','pace_pp'))} percent. {cr('KKR')} crore, three overseas slots, and a long list.",
      "CSK": f"Chennai. Pace is the hole. {w(pc('CSK','pace_pp'))} percent in the powerplay, {w(pc('CSK','pace_death'))} at the death. Death batting is thin too, at {w(pc('CSK','bat_death'))}. {cr('CSK')} crore, six slots, two overseas.",
      "DC": f"Delhi. Their openers are at {w(pc('DC','bat_powerplay'))} percent. Pace is the problem in both phases: {w(pc('DC','pace_pp'))} in the powerplay, {w(pc('DC','pace_death'))} at the death. {cr('DC')} crore, and the most overseas slots in the league, four.",
      "LSG": f"Lucknow have the biggest purse, and the clearest need. Pace, at both ends. {w(pc('LSG','pace_pp'))} percent with the new ball, {w(pc('LSG','pace_death'))} at the death. Batting at the death is a little short too, at {w(pc('LSG','bat_death'))}.",
      "SRH": f"Hyderabad. Spin is at {w(pc('SRH','spin_mid'))} percent, and the powerplay batting, which drives their whole approach, is at {w(pc('SRH','bat_powerplay'))}. {cr('SRH')} crore says they can fix both.",
      "PBKS": f"Punjab. The issue is not how much, but how well. Their pace bowlers go for ten point six runs an over in the powerplay, and eleven point eight at the death. The league's are nine point three, and ten point four. {cr('PBKS')} crore, six slots.",
      "MI": f"Mumbai. A strong squad with one hole: spin, at {w(pc('MI','spin_mid'))} percent of average. A wrist-spinner is the missing piece, and {cr('MI')} crore can buy one."}
long = [
    {"vo": f"Two hundred and ninety-eight crore rupees. Sixty-six slots. Ten teams. One auction, on the sixteenth of December, in Goa. Before a single bid, we looked at what each squad is missing.", "chapter": "Intro", "scene": HOOK},
    {"vo": "Here is how. We took every squad as it stands today: retained players, plus trades. Then we measured, from two seasons of ball-by-ball data, how many balls those players face and bowl in each phase. A hundred percent is an average squad. Below seventy is a hole.",
     "chapter": "How we measured", "scene": {"type": "lab_big_text", "kicker": "OUR MODEL · IPL 2025-26 · IN OUR ARCHIVE", "lines": ["100% is", "[an average squad.]", "Under 70% is a hole."]}},
    {"vo": f"First, the money. Lucknow have the most, {cr('LSG')} crore, for seven slots. Kolkata, forty-one. Hyderabad, forty. Delhi, thirty-nine, with nine slots to fill. Then Mumbai, Chennai, Rajasthan. Punjab have eighteen. Bengaluru, fourteen. And Gujarat, under nine crore, for three slots.", "chapter": "Who has the money", "scene": PURSE},
    {"vo": "Put it all in one grid, and the picture is clear. Pace is the league's biggest hole, at the death and with the new ball. Spin is thin at Mumbai and Hyderabad. And Kolkata are thin almost everywhere. Let's go through them, most needy first.", "chapter": "The need map", "scene": MAP},
] + [{"vo": VO[t], "chapter": {"KKR": "Kolkata", "CSK": "Chennai", "DC": "Delhi", "LSG": "Lucknow", "SRH": "Hyderabad", "PBKS": "Punjab", "MI": "Mumbai"}[t], "scene": team(t, HEAD[t], FITS[t])} for t in ORDER[:7]] + [
    {"vo": f"Rajasthan are balanced. Their powerplay batting strikes at one eighty-seven, the best in the league. Bengaluru are balanced too, with fourteen crore and five slots. And Gujarat are the deepest squad of all, with three slots and under nine crore. They will be watching, not shopping.", "chapter": "The balanced three",
     "scene": {"type": "needs_map", "kicker": "THE BALANCED THREE · OUR MODEL", "title": "Rajasthan, Bengaluru, Gujarat.", "rows": [{"code": t, "v": [N[t][r][0] for r in ROLES], "k": N[t]["keepers"]} for t in ("RR", "RCB", "GT")]}},
    {"vo": "Now, who is out there? The registered list comes around the third of December, so this is only the players the teams released. Pace is rich: Trent Boult, Matheesha Pathirana, Deepak Chahar. Spin is thin: Wanindu Hasaranga, then very little. Openers: Pathum Nissanka. And finishers are the thinnest market of all.", "chapter": "The pool", "scene": POOL},
    {"vo": f"So who could draw the biggest bids? This is our model, an opinion, not a price prediction. Trent Boult: good in the powerplay and the death, and four teams with over a hundred and fifty crore between them could want him. Matheesha Pathirana: the best death bowler on the market. Wanindu Hasaranga: the only proven wrist-spinner, and both Mumbai and Hyderabad need spin. Deepak Chahar: an Indian new-ball bowler, no overseas slot needed. Pathum Nissanka: the best realistic opener.", "chapter": "Who could go big", "scene": BIDS},
    {"vo": "One warning. Mitchell Starc and Travis Head are reported unavailable, and the official list is not out. We will update this on the third of December.", "scene": {"type": "lab_big_text", "kicker": "BEFORE YOU QUOTE THIS", "lines": ["Official list", "[due ~3 December.]"]}},
    {"vo": "Which team wins this auction? Tell us in the comments, and subscribe for the breakdown when the list drops.", "scene": {"type": "cta", "lines": [{"t": "WHO WINS"}, {"t": "THE AUCTION?", "c": "gold"}], "pill": "SUBSCRIBE FOR MORE"}},
]
SH = lambda t, fits: team(t, HEAD[t], fits)
short = [
    {"vo": "Two hundred and ninety-eight crore rupees. Sixty-six slots. Ten teams. One auction, on the sixteenth of December, in Goa. Here is what every IPL team still needs.", "scene": HOOK},
    {"vo": "We measured every squad from two seasons of ball-by-ball data. A hundred percent is an average squad. Below seventy is a hole, and it shows in red. Pace is the league's biggest gap, with the new ball and at the death. Spin is thin at Mumbai and Hyderabad. And Kolkata are thin almost everywhere.", "scene": MAP},
    {"vo": f"Kolkata first. Batting at {w(pc('KKR','bat_powerplay'))} percent in the powerplay, {w(pc('KKR','bat_middle'))} in the middle overs, {w(pc('KKR','bat_death'))} at the death. Only one wicketkeeper, and pace at {w(pc('KKR','pace_pp'))} percent. {cr('KKR')} crore to fix it, and three overseas slots.", "scene": team("KKR", HEAD["KKR"], FITS["KKR"])},
    {"vo": f"Chennai. Pace is the hole: {w(pc('CSK','pace_pp'))} percent with the new ball, {w(pc('CSK','pace_death'))} at the death. Death batting is thin too, at {w(pc('CSK','bat_death'))}. {cr('CSK')} crore for six slots.", "scene": team("CSK", HEAD["CSK"], FITS["CSK"])},
    {"vo": f"Delhi. Their openers are at {w(pc('DC','bat_powerplay'))} percent, and pace is short in both phases, {w(pc('DC','pace_pp'))} and {w(pc('DC','pace_death'))}. They have the most overseas slots in the league, four.", "scene": team("DC", HEAD["DC"], FITS["DC"])},
    {"vo": f"Lucknow have the biggest purse, {cr('LSG')} crore, and the clearest need. Pace, at both ends: {w(pc('LSG','pace_pp'))} percent with the new ball, {w(pc('LSG','pace_death'))} at the death.", "scene": team("LSG", HEAD["LSG"], FITS["LSG"])},
    {"vo": f"Hyderabad. Spin is at {w(pc('SRH','spin_mid'))} percent, and the powerplay batting, which drives their whole approach, is at {w(pc('SRH','bat_powerplay'))}. Forty crore says they can fix both.", "scene": team("SRH", HEAD["SRH"], FITS["SRH"])},
    {"vo": "Punjab. The issue is quality, not quantity. Their pace bowlers go for ten point six runs an over in the powerplay, and eleven point eight at the death. The league's are nine point three, and ten point four.", "scene": team("PBKS", HEAD["PBKS"], FITS["PBKS"])},
    {"vo": f"Mumbai. A strong squad with one hole: spin, at {w(pc('MI','spin_mid'))} percent of average. A wrist-spinner is the missing piece.", "scene": team("MI", HEAD["MI"], FITS["MI"])},
    {"vo": "Rajasthan and Bengaluru are balanced. Gujarat are the deepest squad of all, with three slots and under nine crore. They will be watching, not shopping.", "scene": {"type": "needs_map", "kicker": "THE BALANCED THREE · OUR MODEL", "title": "RR · RCB · GT", "rows": [{"code": t, "v": [N[t][r][0] for r in ROLES], "k": N[t]["keepers"]} for t in ("RR", "RCB", "GT")]}},
    {"vo": "Now, who is out there? Only the players the teams released, until the official list lands around the third of December. Pace is rich: Trent Boult, Matheesha Pathirana, Deepak Chahar. Spin is thin: Wanindu Hasaranga, then very little. Pathum Nissanka is the opener. Finishers are the scarcest of all.", "scene": POOL},
    {"vo": "So who could draw the biggest bids? Our model says Boult, Pathirana, Hasaranga, Chahar and Nissanka, because the most teams need what they offer. That is an opinion, not a price prediction.", "scene": BIDS},
    {"vo": "Which team wins this auction? Tell us in the comments, and subscribe to The Third Man for the full breakdown.", "scene": YT_CTA["scene"]},
]
SRC = ["Squads, purses and slots after retentions and trades, 17-18 Nov 2026: Yahoo Sports/Willow retained and released lists; purses agree across Sportskeeda, M9 and cricketnews.com (https://www.cricketnews.com/en/cricket/news/ipl-2027-mini-auction-remaining-purse-budget/c9b5bc94e78e3e790531ef50). Purses move with the trade window and are not yet official.",
       "Capacity index per role (batting in the powerplay, middle overs and death; pace in the powerplay and at the death; spin in the middle overs): our own model on the Sportmonks ball-by-ball cache, IPL 2025 and 2026, super overs excluded (analysis/ipl2027_needs.py). 'Our model, in our archive'.",
       "Pool names and numbers: released players per franchise; Sportmonks 2025-26 (docs/IPL2027_POOL_LEADS.md). Starc and Head reported unavailable by Cricinfo (live blog); the official registered list is due around 3 December 2026.",
       "Team icons: official iplt20.com team assets, used to identify each franchise."]
TAGS = ["IPL 2027", "IPL 2027 auction", "IPL auction", "IPL mini auction 2026", "what every IPL team needs", "IPL purse", "IPL retention", "IPL released players", "Trent Boult", "Matheesha Pathirana", "Wanindu Hasaranga", "IPL data", "cricket analysis", "The Third Man"]
DL = ("IPL 2027 auction preview: what every IPL team needs. Ten squads, ₹298 crore, 66 slots, one auction on 16 December 2026 in Goa. We measured each squad's batting by phase and its pace and spin from IPL 2025-26 ball-by-ball data, then matched the gaps to the players the franchises released.\n\n"
      "In our model Kolkata are thin in every phase; Chennai, Delhi and Lucknow need pace; Hyderabad and Mumbai need spin; Punjab's pace is expensive; Rajasthan, Bengaluru and Gujarat are balanced. Boult, Pathirana, Hasaranga, Chahar and Nissanka could draw the biggest bids (opinion, not a price prediction).\n\n"
      "Purses and slots as of 17 November 2026, not yet official. The registered list is due around 3 December; Starc and Head are reported unavailable. Capacity: 100% is an average squad. Our model, in our archive (Sportmonks IPL 2025-26).\n\n#IPL2027 #IPLAuction #IPL")
DS = ("What every IPL team needs before the 2027 auction: Kolkata thin everywhere, Chennai, Delhi and Lucknow need pace, Hyderabad and Mumbai need spin. Our model, IPL 2025-26 data. Full breakdown on the channel.\n\n#IPL2027 #IPLAuction #Shorts")
spec = {"slug": "ipl_needs_2027", "theme": "lab", "theme_long": "lab", "captions": "lab", "captions_long": False, "series": "data", "tag": "DATA STORY", "tagsub": "WHAT EVERY IPL TEAM NEEDS",
        "files": {"long": "x", "short": "x"}, "thumb": {"kicker": "IPL 2027 AUCTION · EVERY TEAM", "lines": [{"t": "WHAT EVERY"}, {"t": "IPL TEAM NEEDS", "c": "gold"}], "hero": "298", "herosize": 520},
        "ig_cover": {"lines": [{"t": "WHAT EVERY"}, {"t": "IPL TEAM NEEDS", "c": "gold"}], "sub": "IPL 2027 AUCTION", "hero": "298"}, "sources": SRC, "long": long, "short": short,
        "yt": {"long": {"title": "IPL 2027 Auction Preview: What Every Team Needs | Data Story Ep 15", "description": DL, "tags": TAGS},
               "short": {"title": "What Every IPL Team Needs | IPL 2027 Auction Data Story Ep 15 #Shorts", "description": DS, "tags": TAGS}}}
c.save(spec); voice_lint.fix_spec(spec); spec["files"].setdefault("long", "_unused")
json.dump(spec, open("specs/ipl_needs_2027.json", "w"), ensure_ascii=False, indent=1)
print("wrote specs/ipl_needs_2027.json", voice_lint.check_spec(spec, ("long", "short")) or "voice lint clean", "|", sum(len(x["vo"].split()) for x in long), "long words,", sum(len(x["vo"].split()) for x in short), "short words,", sum(len(x["vo"]) for x in long) + sum(len(x["vo"]) for x in short), "chars")
