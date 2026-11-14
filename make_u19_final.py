"""Builds specs/replay_u19_final.json: India v Pakistan, ACC Men's U19 Asia Cup 2026 final (Al Amerat, Oman, 14 Nov 2026), long analysis + Short.
Every number spoken or shown is computed from the Cricinfo + Cricbuzz captures (data/cricinfo/u19_final_balls.csv via cricinfo_import.py) and asserted here;
bowler figures and Pakistan's batting were cross-checked against Cricbuzz's scorecard (Kavya Patel 10-0-68-4, Venkata 5-0-40-3, Usman Khan 107 off 111 ...).
    python3 cricinfo_import.py data/cricinfo/u19_final.json data/cricbuzz/u19_final.json   # builds the csv
    python3 make_u19_final.py"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "analysis"))
import u19_final as U
import voice_lint
P, I = U.P, U.I

# ---------------------------------------------------------------- facts (asserted)
assert (int(P.runs.sum()), int(P.wicket.sum()), int(P.legal.sum())) == (337, 9, 300) and (int(I.runs.sum()), int(I.wicket.sum()), int(I.legal.sum())) == (339, 9, 300)
bp, bi = U.batting(P), U.batting(I)
assert tuple(bp.loc["Usman Khan", ["runs", "balls", "fours", "sixes"]]) == (107, 111, 11, 3) and tuple(bp.loc["Abdul Qadir", ["runs", "balls", "fours", "sixes"]]) == (80, 54, 3, 8)
assert tuple(bp.loc["Farhan Yousaf", ["runs", "balls"]]) == (63, 60)                     # all three agree with Cricbuzz's scorecard
assert tuple(bi.loc["Lakshya Raichandani", ["runs", "balls", "fours"]]) == (80, 101, 5) and tuple(bi.loc["Aaryavir Sehwag", ["runs", "balls", "fours"]]) == (58, 61, 9)
assert tuple(bi.loc["Mohit Ulva", ["runs", "balls", "fours", "sixes"]]) == (49, 26, 5, 3) and tuple(bi.loc["Manal Chauhan", ["runs", "balls", "sixes"]]) == (47, 32, 3)
bw = U.bowling(P)                                                                         # India's bowlers (they bowled to Pakistan); matches Cricbuzz
assert tuple(bw.loc["Kavya Paresh Patel", ["balls", "runs", "wkts"]]) == (60, 68, 4) and tuple(bw.loc["Chigurupati Venkata", ["balls", "runs", "wkts"]]) == (30, 40, 3)
bq = U.bowling(I)
assert tuple(bq.loc["Mohammad Sayyam", ["balls", "runs", "wkts"]]) == (60, 79, 1) and tuple(bq.loc["Rizwanullah", ["balls", "runs", "wkts"]]) == (60, 53, 3)
assert U.phases(P) == [(93, 1), (45, 0), (66, 1), (70, 1), (63, 6)] and U.phases(I) == [(54, 0), (53, 1), (60, 1), (81, 4), (91, 3)]
assert U.after(P, 30) == (204, 2, 180) and U.after(P, 40) == (274, 3, 240)
# the chase: need 338 to win (337 to tie)
TGT = 338
def need(ov): r, w, b = U.after(I, ov); return TGT - r, 300 - b, w
assert need(10) == (284, 240, 0) and need(35) == (125, 90, 4) and need(40) == (90, 60, 6) and need(42) == (86, 48, 8) and need(43) == (79, 42, 8)
assert need(46) == (34, 24, 8) and need(48) == (25, 12, 9) and need(49) == (8, 6, 9)
rrr = lambda ov: round(6 * need(ov)[0] / need(ov)[1], 1)
assert [rrr(o) for o in (10, 20, 30, 40, 43, 46, 48)] == [7.1, 7.7, 8.6, 9.0, 11.3, 8.5, 12.5]
per_over = {o: int(I[I.over_no == o].runs.sum()) for o in range(41, 51)}
assert per_over == {41: 3, 42: 1, 43: 7, 44: 19, 45: 13, 46: 13, 47: 4, 48: 5, 49: 17, 50: 9}
assert sum(per_over[o] for o in (44, 45, 46)) == 45 and I[I.over_no.isin([44, 45, 46])].legal.sum() == 18
assert I[I.over_no.isin([44, 45, 46])].six.sum() == 4 and I[I.over_no.isin([44, 45, 46])].bowler.nunique() == 3
assert I[I.over_no == 44].bowler.iloc[0] == "Mohammad Sayyam" and I[I.over_no == 49].bowler.iloc[0] == "Mohammad Sayyam" and per_over[44] + per_over[49] == 36
assert U.after(I, 35)[:2] == (213, 4) and U.after(I, 42)[:2] == (252, 8)
# the two-in-two: Raichandani caught (36.2, Ali Raza), Anvay Dravid run out next ball (36.3)
w2 = I[I.wicket & (I.over_no == 37)]; assert list(w2.overs) == [36.2, 36.3] and list(w2.dismissal) == [1.0, 4.0] and set(w2.bowler) == {"Ali Raza"}
# last pairs: Chauhan-Ulva 57 off 35 (9th wicket), Ulva-Venkata 30 off 16 unbeaten
i9 = I[(I.overs >= 41.3) & (I.overs <= 47.2)]; i10 = I[I.overs > 47.2]
assert (int(i9.runs.sum()), int(i9.legal.sum())) == (57, 35) or (int(I[(I.overs > 41.3) & (I.overs <= 47.2)].runs.sum()), int(I[(I.overs > 41.3) & (I.overs <= 47.2)].legal.sum())) == (57, 35)
assert (int(i10.runs.sum()), int(i10.legal.sum())) == (30, 16)
# last over (50th): need 8 off 6; dot, wide, 1, 1, 1, 1, 4 = 9 off 7 deliveries
lo = I[I.over_no == 50]; assert list(lo.runs) == [0, 1, 1, 1, 1, 1, 4] and list(lo.wides) == [0, 1, 0, 0, 0, 0, 0] and list(lo.batter) == ["Mohit Ulva", "Mohit Ulva", "Mohit Ulva", "Chigurupati Venkata", "Mohit Ulva", "Chigurupati Venkata", "Mohit Ulva"]
assert I.cum[lo.index[-2]] == 335 and lo.bowler.iloc[0] == "Ahmed Hussain" and lo.iloc[-1]["shot"] == "COVER_DRIVE" and bool(lo.iloc[-1].four)
KP = P[(P.bowler == "Kavya Paresh Patel") & P.legal]; assert len(KP) == 60 and int(KP.bowler_wkt.sum()) == 4
# death overs (41-50): same lengths, different result
def death(g):
    d = g[(g.over_no >= 41) & g.legal]; return dict(full=round(100 * d.pitch_length.isin(["FULL", "YORKER", "FULL_TOSS"]).mean()), false=round(100 * (d.control == 2).mean()),
                                                     bnd=int(g[(g.over_no >= 41)].four.sum() + g[(g.over_no >= 41)].six.sum()), sixes=int(g[g.over_no >= 41].six.sum()))
dP, dI = death(P), death(I)
assert (dP["full"], dI["full"], dP["false"], dI["false"]) == (40, 38, 37, 38), (dP, dI)
# extras and margin
ex = lambda g: int(g.wides.sum() + g.noballs.sum() + g.byes.sum() + g.legbyes.sum())
assert (int(I.wides.sum()), int(I.legbyes.sum()), ex(I)) == (9, 8, 17)
# Pakistan's innings, run out and wickets
assert [int(x) for x in P[P.wicket].dismissal] == [1, 1, 1, 1, 1, 1, 1, 2, 4] and P[P.wicket].iloc[-1].overs == 49.5
assert int(P[(P.over_no >= 41)].wicket.sum()) == 6 and int(P[P.over_no >= 41].runs.sum()) == 63
# tournament path (Cricinfo standings in the capture): group 8 Nov PAK beat IND by 3 wickets (IND 208, PAK 209/7 in 48.1 overs); semis 12 Nov
assert (dP["bnd"], dI["bnd"]) == (3, 13)                                                  # boundaries (fours + sixes) in overs 41-50
assert (int(P.six.sum()), int(I.six.sum())) == (15, 8)
assert list(I[I.over_no.isin([44, 45, 46])].bowler.drop_duplicates()) == ["Mohammad Sayyam", "Rizwanullah", "Ali Raza"]
assert I[I.over_no.isin([44, 45, 46]) & (I.six == True)].batter.value_counts().to_dict() == {"Manal Chauhan": 2, "Mohit Ulva": 2}
dw = P[(P.over_no >= 41) & P.wicket]; assert dw.bowler.value_counts().to_dict() == {"Kavya Paresh Patel": 3, "Chigurupati Venkata": 3} and int((dw.dismissal == 4).sum()) == 1
assert sorted(dw[dw.bowler == "Chigurupati Venkata"].over_no.unique()) == [45, 47] and int(dw[dw.bowler == "Kavya Paresh Patel"].bowler_wkt.sum()) == 2
assert int(KP.runs.eq(0).sum()) == 29 and I.cum[I[I.over_no == 40].index[-1]] == 248                      # Kavya Patel's dot balls; India 248 after 40 overs (6.2 an over)
assert I[(I.over_no == 38)].shape[0] > 0 and int(I[I.wicket & (I.dismissal.isin([1, 2, 3]))].shape[0]) == 8
assert I[I.wicket & (I.dismissal == 1)].iloc[3].batter == "Yashbardhan Chauhan"
print("all facts asserted; death", dP, dI)

# ---------------------------------------------------------------- helpers
def S(vo, sc, **kw): return dict({"vo": vo, "scene": sc}, **kw)
def stage(vo, panel, av, **kw): return S(vo, dict({"type": "stage", "panel": dict(panel, at=.05), "avatars": av}, **kw))
def tok(t, nm): return {"t": t, "kit": t, "name": nm}
def balls_of(df): return [[r.pitch_line, r.pitch_length, "wicket" if r.bowler_wkt else ("false" if r.control == 2 else "ok")] for r in df.itertuples()]

long = [
 S("Three runs needed from the last ball. Nine wickets down. The Under nineteen Asia Cup final, India against Pakistan. And Mohit Ulva hit it for four. This is how India chased three hundred and thirty-eight, and won by one wicket, with no balls to spare.",
   {"type": "lab_big_text", "kicker": "UNDER-19 ASIA CUP FINAL · LAST BALL", "lines": ["3 to win.", "[1 ball.]"]}),
 S("This is the Replay Room. We took every ball of the Under nineteen Asia Cup final, from the Al Amerat ground in Oman: its line, its length, the shot, and whether the batter was in control. Then we asked how India pulled it off.",
   {"type": "lab_title", "kicker": "THE REPLAY ROOM · U19 ASIA CUP FINAL", "lines": ["338 [chased.]"], "teaser": "India U19 v Pakistan U19 · Al Amerat, Oman"}, chapter="The final"),
 S("Pakistan won the toss and batted, and made three thirty-seven for nine. India answered with three thirty-nine for nine. A one-wicket win, on the very last ball.",
   {"type": "lab_vs", "kicker": "THE RESULT", "title": "India won by one wicket.", "items": [
       {"label": "Pakistan · 50 overs", "v": 337, "text": "337/9", "c": "PAK", "t": "PAK", "kit": "PAK", "word": "thirty-seven"},
       {"label": "India · 50 overs", "v": 339, "text": "339/9", "c": "IND", "t": "IND", "kit": "IND", "word": "thirty-nine"}], "max": 360}),
 S("It was a rematch. On the eighth of November, in the group stage, Pakistan had beaten India by three wickets, chasing two hundred and nine with eleven balls to spare. Pakistan then won all three group games, and the semi-final by nine wickets. India lost that one match, and won the semi-final by eight.",
   {"type": "lab_compare", "kicker": "THE ROAD TO THE FINAL", "title": "Pakistan: unbeaten. Until now.", "a": tok("IND", "INDIA U19"), "b": tok("PAK", "PAKISTAN U19"), "rows": [
       ["Group games won", "2 of 3", "3 of 3", "b"], ["Head-to-head, 8 Nov", "Lost by 3 wkts", "Won", "b"], ["Semi-final margin", "8 wickets", "9 wickets", "b"]]}, chapter="The road"),
 S("Pakistan's innings. A spectacular start: ninety-three for one in the first ten overs, and two hundred and four for two after thirty. Then the finish. In the last ten overs, they added just sixty-three runs, and lost six wickets.",
   {"type": "lab_dots", "kicker": "PAKISTAN · RUNS IN EACH TEN OVERS", "title": "Fast start. Flat finish.", "domain": [0, 100], "ticks": [0, 50, 100], "rows": [
       {"label": "Overs 1-10 · 1 wkt", "v": 93, "text": "93"}, {"label": "Overs 11-20 · 0 wkts", "v": 45, "text": "45"}, {"label": "Overs 21-30 · 1 wkt", "v": 66, "text": "66"},
       {"label": "Overs 31-40 · 1 wkt", "v": 70, "text": "70"}, {"label": "Overs 41-50 · 6 wkts", "v": 63, "text": "63", "hl": True, "word": "sixty-three"}]}, chapter="Pakistan's innings"),
 S("The engine of it was उस्मान ख़ान, a hundred and seven off a hundred and eleven balls. But the spark was अब्दुल क़ादिर. Eighty off fifty-four, including eight sixes. Pakistan hit fifteen sixes in all, to India's eight.",
   {"type": "lab_compare", "kicker": "PAKISTAN'S TWO BIG INNINGS", "title": "The anchor and the hitter.", "a": tok("PAK", "USMAN KHAN"), "b": tok("PAK", "ABDUL QADIR"), "rows": [
       ["Runs", "107", "80", "a"], ["Balls", "111", "54", "level"], ["Strike rate", "96", "148", "b"], ["Sixes", "3", "8", "b"]]}),
 S("India's comeback with the ball was built at the death. चिगुरुपति वेंकट took three wickets in two overs, the forty-fifth and the forty-seventh. काव्य पटेल took two more, plus a run out in his final over. Six wickets, for sixty-three runs.",
   {"type": "lab_big", "kicker": "PAKISTAN'S LAST TEN OVERS", "title": "Six wickets for sixty-three.", "value": 6, "suffix": " WKTS", "label": "for 63 runs in overs 41 to 50: three to Venkata, two to Kavya Patel, one run out", "color": "red", "word": "six"}),
 S("Look at काव्य पटेल's ten overs, sixty balls on a pitch map. Four wickets for sixty-eight, from the short-of-a-length cut that got हयाम ख़ान early, to the yorker that bowled निक़ाब शफ़ीक़ at the death. Twenty-nine of the sixty balls went for no run.",
   {"type": "lab_pitch", "kicker": "KAVYA PATEL · 10 OVERS · 4 FOR 68", "title": "From back of a length to the yorker.", "pitch_balls": balls_of(KP), "from": .25, "to": .85}),
 S("Now, the chase. Three thirty-eight to win. India's openers started steadily: fifty-four without loss after ten overs, a hundred and seven for one after twenty. The first wicket added ninety-five, with आर्यवीर सहवाग making fifty-eight off sixty-one, with nine fours.",
   {"type": "lab_dots", "kicker": "INDIA · RUNS IN EACH TEN OVERS", "title": "A chase in three acts.", "domain": [0, 100], "ticks": [0, 50, 100], "rows": [
       {"label": "Overs 1-10 · 0 wkts", "v": 54, "text": "54"}, {"label": "Overs 11-20 · 1 wkt", "v": 53, "text": "53"}, {"label": "Overs 21-30 · 1 wkt", "v": 60, "text": "60"},
       {"label": "Overs 31-40 · 4 wkts", "v": 81, "text": "81"}, {"label": "Overs 41-50 · 3 wkts", "v": 91, "text": "91", "hl": True, "word": "ninety-one"}]}, chapter="The chase"),
 S("The required rate tells the story. Seven an over after ten. Eight point six after thirty. Nine after forty. Then eleven point three, after the forty-third over, with only two wickets left. It dipped to eight and a half, and then climbed again, to twelve and a half, with twelve balls to go.",
   {"type": "lab_dots", "kicker": "RUNS NEEDED PER OVER · INDIA'S CHASE OF 338", "title": "The required rate.", "domain": [0, 14], "ticks": [0, 7, 14], "tick_labels": False, "rows": [
       {"label": "After 10 overs", "v": 7.1, "text": "7.1"}, {"label": "After 20", "v": 7.7, "text": "7.7"}, {"label": "After 30", "v": 8.6, "text": "8.6"}, {"label": "After 40", "v": 9.0, "text": "9.0"},
       {"label": "After 43 · 8 down", "v": 11.3, "text": "11.3", "hl": True}, {"label": "After 46", "v": 8.5, "text": "8.5"}, {"label": "After 48 · 9 down", "v": 12.5, "text": "12.5", "hl": True, "word": "twelve"}]}),
 S("लक्ष्य रायचंदानी was the anchor: eighty off a hundred and one balls, a strike rate of seventy-nine, with no sixes. It was not pretty, and it was not fast. But it kept India in the game, until the thirty-seventh over.",
   {"type": "lab_compare", "kicker": "INDIA'S OPENERS", "title": "Fast start, then the anchor.", "a": tok("IND", "SEHWAG"), "b": tok("IND", "RAICHANDANI"), "rows": [
       ["Runs", "58", "80", "b"], ["Balls", "61", "101", "level"], ["Strike rate", "95", "79", "a"], ["Fours", "9", "5", "a"]]}),
 S("Then the match turned. India were two-thirteen for four after thirty-five overs. In the thirty-seventh, अली रज़ा had रायचंदानी caught, and with the very next ball, अन्वय द्रविड़ was run out. Savsani fell. Then काव्य पटेल. Two fifty-two for eight, after forty-two overs. India needed eighty-six off forty-eight balls, with two wickets in hand.",
   {"type": "lab_big_text", "kicker": "THE TURN · OVERS 35 TO 42", "lines": ["213 for 4.", "Then [252 for 8.]"]}, chapter="The turn"),
 S("This is where मानल चौहान and मोहित उलवा took over. From the forty-fourth over, three overs, eighteen balls, and forty-five runs. मोहम्मद सय्यम went for nineteen. रिज़वानुल्लाह for thirteen. अली रज़ा for thirteen. Four sixes in all: two from चौहान, two from उलवा.",
   {"type": "lab_dots", "kicker": "INDIA · RUNS PER OVER · OVERS 43 TO 50", "title": "The overs that won it.", "domain": [0, 20], "ticks": [0, 10, 20], "rows": [
       {"label": "43rd · Ali Raza", "v": 7, "text": "7"}, {"label": "44th · Sayyam", "v": 19, "text": "19", "hl": True, "word": "nineteen"}, {"label": "45th · Rizwanullah", "v": 13, "text": "13"},
       {"label": "46th · Ali Raza", "v": 13, "text": "13"}, {"label": "47th · Rizwanullah", "v": 4, "text": "4"}, {"label": "48th · Niqab Shafiq", "v": 5, "text": "5 · wkt"},
       {"label": "49th · Sayyam", "v": 17, "text": "17", "hl": True}, {"label": "50th · Ahmed Hussain", "v": 9, "text": "9"}]}),
 S("And Pakistan went back to मोहम्मद सय्यम for the forty-ninth over. It cost seventeen: four, six, one, four, one, one. His two overs, the forty-fourth and the forty-ninth, went for thirty-six runs. Almost half of his seventy-nine.",
   {"type": "lab_big", "kicker": "MOHAMMAD SAYYAM · 10 OVERS · 79 RUNS", "title": "Two overs.", "value": 36, "suffix": " RUNS", "label": "in his 44th and 49th overs: 19 and 17", "color": "red", "word": "thirty-six"}),
 S("Twenty-five off twelve became eight off six. And the last over, bowled by अहमद हुसैन, was a masterpiece of nerve. A dot. A wide. Then four singles in a row. Three needed from the last ball. Two would tie it, and send the final to a Super Over.",
   {"type": "lab_dots", "kicker": "THE LAST OVER · NEED 8 OFF 6", "title": "Three to win. One ball.", "domain": [0, 5], "ticks": [0, 2, 4], "tick_labels": False, "rows": [
       {"label": "Ball 1", "v": 0, "text": "dot · 8 off 5"}, {"label": "Wide", "v": 1, "text": "1 · 7 off 5"}, {"label": "Ball 2", "v": 1, "text": "1 · 6 off 4"},
       {"label": "Ball 3", "v": 1, "text": "1 · 5 off 3"}, {"label": "Ball 4", "v": 1, "text": "1 · 4 off 2"}, {"label": "Ball 5", "v": 1, "text": "1 · 3 off 1", "hl": True}, {"label": "Ball 6", "v": 4, "text": "FOUR", "hl": True, "word": "four"}]}),
 S("Mohit Ulva stood in front of it. Good length, outside off stump. A cover drive. Four. India win the Under nineteen Asia Cup by one wicket, off the last ball.",
   {"type": "lab_big", "kicker": "THE LAST BALL · AHMED HUSSAIN TO ULVA", "title": "Cover drive. Four.", "value": 4, "label": "Needed three to win. Two would have tied it.", "color": "gold", "word": "four"}, chapter="The last ball"),
 S("So what decided it? Not the lengths. In the last ten overs, India's bowlers and Pakistan's bowlers pitched the ball full, or a yorker, about the same share of the time: forty per cent, and thirty-eight. And both attacks drew a false shot about thirty-seven per cent of the time. But Pakistan's last ten overs brought sixty-three runs, six wickets, and just three boundaries. India's brought ninety-one runs, three wickets, and thirteen boundaries.",
   {"type": "lab_compare", "kicker": "THE LAST TEN OVERS", "title": "Same lengths. Different result.", "a": tok("PAK", "PAKISTAN BATTING"), "b": tok("IND", "INDIA BATTING"), "rows": [
       ["Full or yorker", "40%", "38%", "level"], ["Not in control", "37%", "38%", "level"], ["Runs", "63", "91", "b"], ["Wickets lost", "6", "3", "b"], ["Fours and sixes", "3", "13", "b"]]}, chapter="The analysis"),
 S("One more number. Pakistan's bowlers gave away seventeen extras in India's innings: nine wides, and eight leg byes. In a match that came down to the final ball, that is seventeen runs, and a free ball in the last over.",
   {"type": "lab_big", "kicker": "EXTRAS IN INDIA'S INNINGS", "title": "Seventeen free runs.", "value": 17, "label": "9 wides and 8 leg byes, including a wide in the last over", "color": "red", "word": "seventeen"}),
 S("Our verdict? India lost the group game by three wickets, and won the final by one. After forty overs they needed nine an over, and were scoring six, and they needed two Sayyam overs to go for thirty-six. But they didn't give up, and they won the Under nineteen Asia Cup.",
   {"type": "lab_big_text", "kicker": "THE VERDICT", "lines": ["Behind all day.", "[Ahead at the end.]"]}, chapter="The verdict"),
 S("Was this the greatest Under nineteen final? Tell us in the comments, and follow for the next Replay Room.",
   {"type": "cta", "lines": [{"t": "GREATEST U19 FINAL?"}, {"t": "THE REPLAY ROOM", "c": "gold"}], "pill": "SUBSCRIBE FOR MORE"}),
]

# ---------------------------------------------------------------- Short (stadium stage)
VEN = {"time": "day", "crowd": [[25, 100, 200], [0, 110, 60], [240, 240, 240], [250, 150, 30]], "boards": [[25, 100, 200], [0, 110, 60]]}
IN = lambda pose, **k: dict(kit="IND", pose=pose, **k)
PK = lambda pose, **k: dict(kit="PAK", pose=pose, **k)
short = [
 stage("Three runs needed from the last ball. Nine wickets down. The Under nineteen Asia Cup final. India against Pakistan.",
       {"kind": "headline", "at": 0.0, "kicker": "UNDER-19 ASIA CUP FINAL", "lines": [{"t": "3 TO WIN."}, {"t": "1 BALL.", "c": "gold"}]},
       [PK("bowl", x=.66, dir=-1), IN("stance", x=.26)], view="side", cam="wide", stumps=[.17, .93], fx=["vignette", "spot"]),
 stage("Pakistan batted first, and made three thirty-seven. उस्मान ख़ान, a hundred and seven. अब्दुल क़ादिर, eighty off fifty-four, with eight sixes.",
       {"kind": "versus", "kicker": "PAKISTAN BATTED FIRST", "left": {"v": "337", "l": "Pakistan", "c": "gold"}, "right": {"v": "338", "l": "India needed", "c": "red"}},
       [PK("pull", x=.32, hit="loft", ghost=True), IN("stand", x=.76)], view="side", cam="push", stumps=[.2, .93], ball={"at": .55, "shot": "six"}, fx=["vignette", "sparks"]),
 stage("But India fell apart. Two-thirteen for four. Then two fifty-two for eight. They needed eighty-six off forty-eight balls.",
       {"kind": "bignum", "kicker": "AFTER 42 OVERS", "label": "INDIA · NEED 86 OFF 48", "value": 252, "suffix": "/8", "count_dur": .6, "color": "red"},
       [IN("dejected", x=.5)], cam="drift", fx=["vignette"]),
 stage("Then मानल चौहान and मोहित उलवा hit forty-five off three overs, with four sixes.",
       {"kind": "versus", "kicker": "OVERS 44 TO 46", "left": {"v": "45", "l": "Runs", "c": "gold"}, "right": {"v": "4", "l": "Sixes", "c": "gold"}},
       [IN("stance", x=.32, hit="loft", ghost=True)], view="side", cam="pull", stumps=[.2, .93], ball={"at": .5, "shot": "six"}, fx=["vignette", "shake", "sparks"]),
 stage("Twenty-five off twelve. Then seventeen off one over. Eight needed from the last six.",
       {"kind": "bignum", "kicker": "THE LAST OVER", "label": "NEED 8 OFF 6", "value": 8, "suffix": " OFF 6", "count_dur": .5, "color": "gold"},
       [IN("run", x=.4)], cam="push", fx=["vignette", "spot"]),
 stage("A dot. A wide. Four singles. Three needed from the last ball. Two would tie it, and send the final to a Super Over.",
       {"kind": "headline", "kicker": "THE LAST BALL", "lines": [{"t": "3 TO WIN."}, {"t": "2 TO TIE.", "c": "gold"}]},
       [PK("bowl", x=.66, dir=-1), IN("stance", x=.26)], view="side", cam="push", stumps=[.17, .93], fx=["vignette", "spot"]),
 stage("मोहित उलवा. Cover drive. Four!",
       {"kind": "bignum", "kicker": "AHMED HUSSAIN TO ULVA", "label": "FOUR", "value": 4, "count_dur": .4, "color": "gold"},
       [IN("stance", x=.3, hit="drive", ghost=True)], view="side", cam="pull", stumps=[.2, .93], ball={"word": "four", "shot": "four"}, fx=["vignette", "flash", "speed", "shake", "sparks"]),
 stage("India win by one wicket, off the last ball. Pakistan had beaten them in the group stage. India are Under nineteen Asia Cup champions.",
       {"kind": "headline", "kicker": "INDIA WIN THE FINAL", "lines": [{"t": "BY ONE"}, {"t": "WICKET.", "c": "gold"}]},
       [IN("arms_wide", x=.34), PK("dejected", x=.74)], cam="pull", fx=["vignette", "spot", "confetti"], fx_at=.2),
 {"vo": "Was this the greatest Under nineteen final? Tell us in the comments, and follow for the full breakdown.",
  "scene": {"type": "cta", "lines": [{"t": "GREATEST U19 FINAL?"}, {"t": "FULL BREAKDOWN →", "c": "gold"}], "pill": "FOLLOW FOR MORE"}},
]

# ---------------------------------------------------------------- package
SRC = ["ESPNcricinfo match capture, India U19 v Pakistan U19, ACC Men's U19 Asia Cup 2026 final, Al Amerat, Oman, 14 Nov 2026 (match 1558444): ball-by-ball with line, length, shot and control, captured with our own tool.",
       "Cricbuzz match capture (match 175720): over-by-over cross-check (all runs match) and the first-innings scorecard (Pakistan's batting and India's bowling figures agree with our figures). Result in both: India won by 1 wicket (0 balls remaining).",
       "Tournament path (group and semi-final results) from the Cricinfo series standings in the same capture. Conventions: balls faced exclude wides; bowler runs exclude byes and leg byes; a run out is not credited to the bowler.",
       "All figures computed in make_u19_final.py and analysis/u19_final.py from data/cricinfo/u19_final_balls.csv. Web coverage of this match was not yet indexed when this was made, so no record claims are made. Graphics are original illustrations, not broadcast footage."]
DESC_L = ("India vs Pakistan, Under-19 Asia Cup final 2026 analysis: India chased 338 and won by one wicket, off the last ball, at Al Amerat in Oman. We took every ball of the final "
          "(line, length, shot played, and whether the batter was in control) to explain how: Pakistan's fast start and flat finish, India's collapse from 213 for 4 to 252 for 8, the overs that won it, and the last-over nerve.\n\n"
          "Sources: ball-by-ball data from ESPNcricinfo and Cricbuzz match pages (captured with our own tool, cross-checked over by over). All numbers are computed by us; "
          "'not in control' is the Cricinfo shot-control flag. All graphics are original illustrations, not broadcast footage.\n\n#INDvPAK #U19AsiaCup #AsiaCup2026 #IndiaVsPakistan")
DESC_S = ("India vs Pakistan, Under-19 Asia Cup final 2026: 3 needed off the last ball, nine wickets down. The Replay Room: a ball-by-ball breakdown. Data: ESPNcricinfo and Cricbuzz match pages, analysis by The Third Man. Full video on the channel.\n#INDvPAK #U19AsiaCup #AsiaCup2026")
TAGS = ["India vs Pakistan", "India vs Pakistan U19 Asia Cup final", "U19 Asia Cup final 2026", "IND vs PAK U19", "Under 19 Asia Cup", "Mohit Ulva", "Abdul Qadir", "Usman Khan", "cricket analysis", "The Replay Room", "The Third Man"]
spec = {"slug": "replay_u19_final", "theme": "stadium", "theme_long": "lab", "captions": "serif", "captions_long": False, "series": "replay", "tag": "THE REPLAY ROOM", "tagsub": "U19 ASIA CUP FINAL · IND V PAK",
        "files": {"long": "India_vs_Pakistan_U19_Asia_Cup_Final_Analysis_338_Chased", "short": "India_vs_Pakistan_U19_Asia_Cup_Final_Short_9x16"},
        "thumb": {"kicker": "U19 ASIA CUP FINAL", "lines": [{"t": "338 CHASED"}, {"t": "LAST BALL", "c": "gold"}], "hero": "338", "herosize": 420},
        "sources": SRC, "venue": VEN, "long": long, "short": short,
        "yt": {"long": {"title": "India vs Pakistan - U19 Asia Cup Final Analysis | 338 Chased Off the Last Ball", "description": DESC_L, "tags": TAGS},
               "short": {"title": "3 Needed Off the Last Ball! | India vs Pakistan U19 Asia Cup Final #Shorts", "description": DESC_S, "tags": TAGS}}}
voice_lint.fix_spec(spec)
json.dump(spec, open("specs/replay_u19_final.json", "w"), ensure_ascii=False, indent=1)
print("wrote specs/replay_u19_final.json: long", sum(len(x["vo"].split()) for x in long), "words,", len(long), "scenes; short", sum(len(x["vo"].split()) for x in short), "words")
