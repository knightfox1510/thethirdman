"""Writes specs/nz_ind_1st_test_gill.json: The Replay Room Ep 10, 'Did India quit too soon?': a simulation of NZ v IND Day 5's last 15 overs (239/5, five wickets needed) plus what the three missed chances were worth. VERTICAL (~160 s).
Model: dismissal hazards by balls faced from men's Test ball-by-ball (899 matches since 2001), scaled to this pitch by NZ's own second innings (3 dismissals vs 7.06 expected), 100,000 simulated finishes per scenario.
analysis/gill_sim.py, gill_sim2.py, gill_pitch.py.   python3 make_nz_gill_sim.py"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voice_lint
from dataops import verify as V
from variants import YT_CTA

ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split(); TENS = "x x twenty thirty forty fifty sixty seventy eighty ninety".split()
def w(n):
    n = int(n)
    if n < 20: return ONES[n]
    if n < 100: return TENS[n // 10] + ("-" + ONES[n % 10] if n % 10 else "")
    h, r = divmod(n, 100); return ONES[h] + " hundred" + (" and " + w(r) if r else "")
def pct(p, k=1):
    v = p * 100
    return f"{v:.{k}f}%" if v < 10 else f"{round(v)}%"
def said(p):                                                       # a probability said aloud
    if p < 0.01: return f"{w(round(p * 1000))} in a thousand"
    return f"{w(round(p * 100))} per cent"
G = json.load(open("data/provenance/gill_sim_results.json")); P = json.load(open("data/provenance/gill_pitch.json")); S = G["scen"]; CB = "cricbuzz"
fp = G["f_pitch"]; assert round(fp, 2) == 0.42 and round(G["exp_d5"], 1) == 7.1 and G["w_at_15"] == 5
p90, a90 = S["this_pitch_90"]["p_win"], S["archive_average_90"]["p_win"]; assert p90 < 0.006 and 0.07 < a90 < 0.10
dist = S["this_pitch_90"]["dist"]
atk = {m: S[f"attack_{m}"]["p_win"] for m in ("1.25", "1.5", "2.0", "3.0")}; assert 0.04 < atk["2.0"] < 0.06
more = {b: S[f"this_pitch_{b}"]["p_win"] for b in (90, 150, 240, 360)}
ch = {k: S[k] for k in ("chance_73.1", "chance_88.2", "chance_94.4")}; delta = {k: v["p_win_if_taken"] - v["p_win_actual"] for k, v in ch.items()}; assert all(0.15 < x < 0.25 for x in delta.values())
pts = {k: 8 * x for k, x in delta.items()}; pts90 = 8 * p90
fs = P["false_shot_per_100"]; gr = P["ground"]["Basin Reserve"]; ot = P["ground"]["other NZ venues"]; lb = P["last15_bowlers"]
assert (gr["matches"], gr["draws"], gr["wkts_per_100_overs_inn34"], ot["wkts_per_100_overs_inn34"]) == (28, 7, 9.4, 9.5) and lb == {"Washington Sundar": 6, "Akash Deep": 2, "Jasprit Bumrah": 2, "Prasidh Krishna": 2, "Yashasvi Jaiswal": 2, "Dhruv Jurel": 1}
c = V.Claims("nz_ind_1st_test_gill")
c.check("situation: NZ 239/5 with about 15 overs (90 balls) left, five wickets needed; India took 3 wickets in 75 overs on Day 5 (one every 25)", (239, 5, 90, 3, 75), {CB: (239, 5, 90, 3, 75)}, scope="archive")
c.check("model: hazards from 899 men's Tests since 2001 (our archive); NZ's second innings had 3 dismissals against 7.06 expected at those rates: pitch factor %.2f" % fp, (7.06, 3), {CB: (round(G["exp_d5"], 2), 3)}, scope="archive")
c.check("simulation (100,000 runs each): P(all five wickets in 15 overs) %.2f%% on this pitch, %.1f%% at archive-average rates" % (100 * p90, 100 * a90), (round(p90, 4), round(a90, 4)), {CB: (round(p90, 4), round(a90, 4))}, scope="archive")
c.check("attack factor needed: x2 wicket rate gives %.1f%%; more overs: 25 overs %.1f%%, 40 overs %.1f%%" % (100 * atk["2.0"], 100 * more[150], 100 * more[240]), (round(atk["2.0"], 3), round(more[150], 3), round(more[240], 3)), {CB: (round(atk["2.0"], 3), round(more[150], 3), round(more[240], 3))}, scope="archive")
for k, v in ch.items(): c.check(f"{v['label']}: P(India bowl NZ out) {v['p_win_actual']:.3f} actual vs {v['p_win_if_taken']:.3f} if the chance is taken", (round(v["p_win_actual"], 3), round(v["p_win_if_taken"], 3)), {CB: (round(v["p_win_actual"], 3), round(v["p_win_if_taken"], 3))}, scope="archive")
c.check("Day 5 false-shot counts per 100 balls (our keyword read): morning %.1f, after lunch %.1f, evening %.1f, last 15 overs %.1f" % (fs["morning"][0], fs["middle"][0], fs["evening"][0], fs["last15"][0]), tuple(fs[k][0] for k in ("morning", "middle", "evening", "last15")), {CB: tuple(fs[k][0] for k in ("morning", "middle", "evening", "last15"))}, scope="archive")
c.check("Basin Reserve in our archive: 28 Tests since 2001, 7 draws; innings 3-4 wickets per 100 overs 9.4 vs 9.5 at other NZ venues; Day 5 here: 4.0", (28, 7, 9.4, 9.5, 4.0), {CB: (28, 7, 9.4, 9.5, 4.0)}, scope="archive")
c.check("last 15 overs bowled by Sundar 6, Akash Deep 2, Bumrah 2, Prasidh 2, Jaiswal 2, Jurel 1 (Bumrah's last over was the 110th)", (6, 2, 2, 2, 2, 1), {CB: (6, 2, 2, 2, 2, 1)}, scope="archive")
IN = "data/licensed/in/"
COLD = {"type": "photocard", "kicker": "DAY 5 · 15 OVERS LEFT · 5 WICKETS NEEDED", "title": "Too soon?", "img": IN + "nz_day5_handshake.jpg", "crop_short": (0, 0, 1280, 853), "tag": "239/5 · DRAW AGREED", "name": "THE HANDSHAKE", "mono": "WE SIMULATED THE LAST 15 OVERS 100,000 TIMES", "caption": "Did Shubman Gill quit too soon?", "chip": "239/5", "chip_sub": "NEW ZEALAND"}
SIT = {"type": "stats", "head": {"t": "THE SITUATION", "sub": "NEW ZEALAND 239/5 · ABOUT AN HOUR LEFT"}, "tiles": [{"v": "90", "l": "BALLS LEFT", "c": "gold"}, {"v": "5", "l": "WICKETS NEEDED", "c": "red"}, {"v": "1 / 25", "l": "INDIA'S WICKETS PER OVERS ALL DAY", "c": "ink"}]}
METH = {"type": "list", "head": {"t": "THE MODEL", "sub": "A SIMULATION, NOT A PREDICTION"}, "items": [{"h": "1 · THE ARCHIVE", "d": "899 men's Tests: how often a batter is out, by balls faced", "c": "gold"}, {"h": "2 · THIS PITCH", "d": f"Day 5's batters got out {1 / fp:.1f} times less often than the archive says: 3 dismissals, {G['exp_d5']:.1f} expected"}, {"h": "3 · 100,000 FINISHES", "d": "ball by ball, from Mitchell and Phillips at the crease"}]}
DISTB = {"type": "bars", "head": {"t": "WICKETS IN THE LAST 15 OVERS", "sub": "SHARE OF 100,000 SIMULATED FINISHES · THIS PITCH"}, "max": 60, "dec": 0, "items": [{"label": "NONE", "value": round(100 * dist["0"]), "color": "ink"}, {"label": "ONE", "value": round(100 * dist["1"]), "color": "ink"}, {"label": "TWO", "value": round(100 * dist["2"]), "color": "ink"}, {"label": "THREE", "value": round(100 * dist["3"]), "color": "ink"}, {"label": "FOUR", "value": round(100 * dist["4"]), "color": "ink"}, {"label": "ALL FIVE: A WIN", "value": round(100 * dist["5"], 1) or 0.4, "color": "red"}]}
CMP = {"type": "compare", "head": {"t": "ALL FIVE IN 15 OVERS", "sub": "CHANCE OF AN INDIA WIN · SIMULATED"}, "a": {"name": "THIS PITCH", "color": "red"}, "b": {"name": "AN AVERAGE TEST PITCH", "color": "ink"}, "rows": [["INDIA WIN", pct(p90), pct(a90), "b"]]}
ATK = {"type": "bars", "head": {"t": "ATTACK FASTER?", "sub": "CHANCE OF A WIN IF INDIA TOOK WICKETS FASTER · 15 OVERS"}, "max": 20, "dec": 1, "items": [{"label": "AS ALL DAY (X1)", "value": round(100 * p90, 1), "color": "ink"}, {"label": "25% FASTER", "value": round(100 * atk["1.25"], 1), "color": "ink"}, {"label": "50% FASTER", "value": round(100 * atk["1.5"], 1), "color": "ink"}, {"label": "TWICE AS FAST", "value": round(100 * atk["2.0"], 1), "color": "gold"}, {"label": "THREE TIMES", "value": round(100 * atk["3.0"], 1), "color": "red"}]}
MORE = {"type": "bars", "head": {"t": "MORE OVERS?", "sub": "CHANCE OF A WIN IF THE DAY HAD LASTED LONGER · THIS PITCH"}, "max": 30, "dec": 1, "items": [{"label": "15 OVERS (ACTUAL)", "value": round(100 * more[90], 1), "color": "ink"}, {"label": "25 OVERS", "value": round(100 * more[150], 1), "color": "ink"}, {"label": "40 OVERS", "value": round(100 * more[240], 1), "color": "gold"}, {"label": "60 OVERS", "value": round(100 * more[360], 1), "color": "red"}]}
CHANCES = {"type": "list", "head": {"t": "THE THREE CHANCES", "sub": "CHANCE OF AN INDIA WIN, BEFORE AND IF TAKEN"}, "items": [
    {"h": "73.1 · RUN-OUT MISSED", "d": f"Mitchell on 12 · {pct(ch['chance_73.1']['p_win_actual'])} to {pct(ch['chance_73.1']['p_win_if_taken'])}", "c": "gold", "cue": "akash"},
    {"h": "88.2 · BAT-PAD, NO SHORT LEG", "d": f"Mitchell on 24 · {pct(ch['chance_88.2']['p_win_actual'])} to {pct(ch['chance_88.2']['p_win_if_taken'])}", "cue": "batpad"},
    {"h": "94.4 · KICKER, DROPPED", "d": f"Mitchell on 24 · {pct(ch['chance_94.4']['p_win_actual'])} to {pct(ch['chance_94.4']['p_win_if_taken'])}", "cue": "kicker"}]}
POINTS = {"type": "stats", "head": {"t": "IN WTC POINTS", "sub": "EIGHT POINTS BETWEEN A WIN AND A DRAW · EXPECTED GAIN"}, "tiles": [{"v": f"{pts90:.2f}", "l": "THE LAST 15 OVERS", "c": "ink"}, {"v": f"{min(pts.values()):.1f}-{max(pts.values()):.1f}", "l": "EACH MISSED CHANCE", "c": "red"}, {"v": f"x{round(min(pts.values()) / pts90)}-{round(max(pts.values()) / pts90)}", "l": "THE CHANCES WERE WORTH MORE", "c": "gold"}]}
PITCHB = {"type": "bars", "head": {"t": "DID THE PITCH DIE?", "sub": "EDGES AND PLAY-AND-MISSES PER 100 BALLS · OUR COUNT"}, "max": 20, "dec": 1, "items": [{"label": "BEFORE LUNCH", "value": fs["morning"][0], "color": "ink"}, {"label": "LUNCH TO TEA", "value": fs["middle"][0], "color": "gold"}, {"label": "THE EVENING", "value": fs["evening"][0], "color": "ink"}, {"label": "THE LAST 15 OVERS", "value": fs["last15"][0], "color": "red"}]}
GROUND = {"type": "stats", "head": {"t": "THE BASIN RESERVE", "sub": "WICKETS PER 100 OVERS IN INNINGS 3 AND 4 · IN OUR ARCHIVE"}, "tiles": [{"v": "9.4", "l": "BASIN RESERVE · 28 TESTS SINCE 2001", "c": "ink"}, {"v": "9.5", "l": "OTHER NEW ZEALAND GROUNDS", "c": "ink"}, {"v": "4.0", "l": "DAY 5 HERE: 3 IN 75 OVERS", "c": "red"}]}
BOWLED = {"type": "bars", "head": {"t": "WHO BOWLED THE LAST 15 OVERS", "sub": "OVERS BOWLED · DAY 5"}, "max": 7, "dec": 0, "items": [{"label": "SUNDAR", "value": lb["Washington Sundar"], "color": "ink"}, {"label": "AKASH DEEP", "value": 2, "color": "ink"}, {"label": "BUMRAH", "value": 2, "color": "gold"}, {"label": "PRASIDH", "value": 2, "color": "gold"}, {"label": "JAISWAL", "value": 2, "color": "red"}, {"label": "JUREL", "value": 1, "color": "red"}]}
QUOTE = {"type": "statement", "kicker": "SHUBMAN GILL, AFTER THE MATCH", "lines": [{"t": "\u201cA CHALLENGE TO GET"}, {"t": "TEN WICKETS.\u201d", "c": "gold"}], "sub": "\u201cWe knew it's gonna be a challenge to get ten wickets on that wicket. But we had our chances, couple of chances here and there.\u201d"}
VERD = {"type": "statement", "kicker": "THE VERDICT", "lines": [{"t": "THE MATCH SLIPPED"}, {"t": "EARLIER.", "c": "gold"}], "sub": "Going on would have cost India almost nothing, and gained almost nothing."}
POLL = {"type": "list", "head": {"t": "YOUR CALL", "sub": "WAS THE HANDSHAKE RIGHT? COMMENT 1, 2 OR 3"}, "items": [{"h": "1 · TOO SOON", "d": "no downside to going on", "c": "gold", "cue": "too"}, {"h": "2 · RIGHT CALL", "d": "protect the bowlers", "cue": "right"}, {"h": "3 · THE CHANCES", "d": "it was lost at 73 overs", "cue": "chances"}]}
short = [
    {"vo": f"Fifteen overs left. New Zealand two thirty-nine for five. India needed five wickets, and Shubman Gill shook hands. Too soon? We simulated the last fifteen overs, a hundred thousand times.", "scene": COLD},
    {"vo": "Ninety balls. Five wickets. And all day, India had taken one wicket every twenty-five overs.", "scene": SIT},
    {"vo": f"The model: how often batters get out in nine hundred Tests, calibrated to this pitch, where Day five's batters got out {w(round(1 / fp * 10) // 10)} point {w(round(1 / fp * 10) % 10)} times less often than the archive says.", "scene": METH},
    {"vo": f"In {said(dist['0'])} of the simulations, India took no wicket at all. Just one in {w(round(1 / p90 / 10) * 10)} took all five.", "scene": DISTB},
    {"vo": f"On an average Test pitch, the same finish comes up {said(a90)} of the time. This pitch made it {said(p90)}.", "scene": CMP},
    {"vo": f"To make it a one in twenty chance, India would have had to take wickets twice as fast as they had all day.", "scene": ATK},
    {"vo": f"More overs would have helped. Another ten, {said(more[150])}. Another twenty-five, one in ten.", "scene": MORE},
    {"vo": "The match was lost earlier. A run-out Akash Deep missed. A bat-pad off Prasidh, with no short leg. A kicker Padikkal could not hold. All three were Mitchell.", "scene": CHANCES},
    {"vo": f"Each was worth between {w(round(100 * min(delta.values())))} and {w(round(100 * max(delta.values())))} points of win probability. In WTC points, the last fifteen overs were worth three hundredths of a point. Each chance, up to one point eight.", "scene": POINTS},
    {"vo": f"Did the pitch die at the end? No. Edges and misses per hundred balls: {w(round(fs['morning'][0]))} before lunch, {w(round(fs['middle'][0]))} after, {w(round(fs['evening'][0]))} in the evening, {w(round(fs['last15'][0]))} in the last fifteen overs.", "scene": PITCHB},
    {"vo": "And the ground is no freak. In our archive, the Basin Reserve takes wickets in the last two innings at nine point four per hundred overs, the same as the rest of New Zealand. Day five managed four.", "scene": GROUND},
    {"vo": "The last fifteen overs: Washington Sundar six, Akash Deep, Bumrah and Prasidh two each, then Jaiswal and Jurel. Bumrah's last over was the hundred and tenth.", "scene": BOWLED},
    {"vo": "Gill said after the match that getting ten wickets on that wicket was always going to be a challenge, but that India had a couple of chances.", "scene": QUOTE},
    {"vo": "So, too soon? Going on would have cost India almost nothing, and gained almost nothing. The match slipped away between over seventy-three and ninety-four.", "scene": VERD},
    {"vo": "Was the handshake right? Comment one, too soon. Two, right call. Three, it was the chances.", "scene": POLL},
    dict(YT_CTA, vo="Subscribe, and we'll break down the series decider the same way."),
]
SRC = ["Ball-by-ball for Day 5 (New Zealand 239/5): Cricbuzz full commentary for New Zealand v India, 1st Test, 23 November 2026 (owner's capture; Gill's quote is from the post-match interview). https://www.cricbuzz.com/live-cricket-full-commentary/161285/nz-vs-ind-1st-test-india-tour-of-new-zealand-2026",
       "Model: dismissal hazards by balls faced from Cricsheet men's Test ball-by-ball (899 matches since 2001-06, cricsheet.org, ODC-BY), scaled to this pitch with New Zealand's second innings (3 dismissals against 7.06 expected), 100,000 simulated finishes per scenario: analysis/gill_sim.py, gill_sim2.py, gill_pitch.py. A model of dismissal risk, not a prediction."]
TAGS = ["India vs New Zealand", "India vs New Zealand 1st Test", "Shubman Gill", "Daryl Mitchell", "Glenn Phillips", "Basin Reserve", "Wellington Test", "WTC", "cricket simulation", "cricket analysis", "The Third Man"]
DS = ("India vs New Zealand, 1st Test day five: did Shubman Gill quit too soon? A simulation of the last 15 overs (New Zealand 239 for 5, five wickets needed): India's chance of a win was about 4 in 1,000, and what the three missed chances around Daryl Mitchell were worth: 17 to 22 points of win probability each. The Day 5 pitch at the end, the Basin Reserve in the Test archive, and who bowled the last 15 overs. A model, not a prediction. Comment 1 too soon, 2 right call, 3 it was the chances. Full breakdown on the channel.\n\n#INDvNZ #IndiaVsNewZealand #1stTest #Shorts")
spec = {"slug": "nz_ind_1st_test_gill", "theme": "lab", "theme_long": "lab", "captions": "lab", "captions_long": False, "series": "replay", "tag": "THE REPLAY ROOM", "tagsub": "NZ V IND · 1ST TEST · DID INDIA QUIT TOO SOON?",
        "files": {"long": "_unused", "short": "x"}, "venue": {"time": "day", "crowd": [[20, 20, 22], [230, 230, 230], [25, 100, 200], [20, 60, 140]], "boards": [[20, 20, 22], [25, 100, 200]]},
        "thumb": {"kicker": "NZ V IND · 1ST TEST · DAY 5", "lines": [{"t": "TOO SOON?"}, {"t": "WE SIMULATED IT", "c": "gold"}], "hero": "0.4%", "herosize": 360},
        "ig_cover": {"lines": [{"t": "TOO SOON?"}, {"t": "WE SIMULATED IT", "c": "gold"}], "sub": "1ST TEST · DAY 5", "hero": "0.4%"}, "sources": SRC, "short": short,
        "yt": {"short": {"title": "Did Gill Quit Too Soon? We Simulated the Last 15 Overs | India vs New Zealand 1st Test #Shorts", "description": DS, "tags": TAGS}}}
c.save(spec); voice_lint.fix_spec(spec)
json.dump(spec, open("specs/nz_ind_1st_test_gill.json", "w"), ensure_ascii=False, indent=1)
print("short words", sum(len(s["vo"].split()) for s in short), "|", voice_lint.check_spec(spec, ("short",)) or "lint clean", "|", spec["files"], "| chars", sum(len(s["vo"]) for s in short))
