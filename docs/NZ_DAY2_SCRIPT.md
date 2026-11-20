# NZ v IND, 1st Test, Day 2: analysis, storyboard and script (DRAFT for review, 20 Nov 2026)
Source: the owner's Cricbuzz full-commentary capture (`data/cricbuzz/nz_ind_1st_test_day2.json`). Our analysis: `analysis/nz_day2.py` -> `data/provenance/nz_day2_figures.json` / `nz_day2_balls.json`. Nothing is voiced or rendered until approved.

## 0. What the capture does and does not contain (read first)
- It holds **India's first innings to stumps (240 deliveries, 38.6 overs, 159/1)** in full ball-by-ball.
- It does **not** hold NZ's Day 2 morning: the NZ-innings entries stop at 243/5 (Day 1). Cricbuzz's own stumps summary says "New Zealand's 368", so NZ added 125 for the last five wickets, but we have no ball data, scorers or wicket-takers for that. **Request: re-capture the "NZ 1st Innings" tab** (Full Commentary, click "NZ 1st Innings", then capture). Until then the video states 368 only as Cricbuzz's figure and tells the NZ morning in one line without names.
- Numbers below are from the capture; length is OUR keyword read of Cricbuzz's text (61 of 240 balls unclassified); speeds only where Cricbuzz printed one (small samples). Control / false-shot figures are not used for India's innings (not in this capture).

## 1. The analysis (what the day was)
**Scoreline.** India 159/1 in 38.6 overs, chasing 368 (trail by 209). Jaiswal 85 (89 balls, 16 fours, SR 95.5; out c Blundell b Henry, 27.5, at 130). Rahul 52 not out (116 balls, 5 fours, SR 44.8). Padikkal 16* (35).
**Two completely different innings in one stand.** Jaiswal: 85 off 89. Rahul at the other end: 52 off 116 (88 dots). Fifty for Jaiswal came off 66 balls; his last 35 runs came off 23.
**The shape of the day (our over blocks).** Before tea: 8 overs, 16 runs (Jamieson's maidens, three slips and a gully, a ball that missed off stump by a whisker at 2.5). After tea: 143 runs in 31 overs; Cricbuzz's drinks note: "15 overs, 81 runs", NZ "hardly created any chances". Blocks (runs per six overs): 7, 27, 34, 39, 28, 10, 14. After Jaiswal's wicket (27.5): 29 runs in the last eleven overs (4 fours).
**The lives and the reviews (the drama).**
- 4.2: Jaiswal on 0, edge between third slip (Nicholls dived) and gully: four.
- ~3.6: NZ reviewed a Jamieson LBW on Rahul (impact outside off): inconclusive; Cricbuzz: the review was confirmed lost.
- 6.4: Henry's LBW shout on Rahul (on 5), "two sounds" (front pad and back pad); Latham, with one second left, chose not to review. Cricbuzz's commentators: "NZ should have reviewed". Henry threw his sweater down after the over. (Ball-tracker outcome not shown: we do not say whether it was hitting.)
- 7.3: Jaiswal on 6, edge to gully, Phillips drops it (four). Jamieson "not a happy bowler".
- 27.5: Henry "adamant", NZ review, Jaiswal c Blundell for 85 "against the run of play" (Cricbuzz).
**Length lesson.** NZ bowled full 57 times and conceded 46 runs; good length 33 balls, 10 runs; short of a length 38 balls, 24 runs; short 45 balls, 16 runs. Jaiswal vs full: 27 balls, 41 runs. Jaiswal vs good length: 10 balls, 0 runs. Rahul vs full: 26 balls, 5 runs (he left and defended them). The full ball gave Jaiswal his innings.
**The bowlers.** Jamieson 11-5-15-0 (best figures, no wicket). Henry 12-3-43-1. Smith 6-0-29-0. Duffy 10-0-72-0 and **six no-balls in the innings (Duffy 3, Smith 3)** per Cricbuzz's bowler lines. Speeds printed: Henry avg 129.5 (15 balls), Jamieson 133.1 (19), Smith 133.8 (9), Duffy 135.4 (18), max 141.1.
**Cross-day link (Day 1).** India's seamers bowled short 37% of their classified balls on Day 1 (131 of 352), NZ's attack 26% (45 of 174) on Day 2; the NZ plan was fuller and shaped the ball, India's drifted short as the pitch eased. Same pitch, different plan; and NZ paid for fullness when it was driveable. (Our classification; label it.)
**Context to keep honest.** Cricbuzz: KL's 22nd Test fifty and his first fifty against NZ in Tests (single source, label "per Cricbuzz"). "First Indian opener with 50+ in all SENA countries" is also Cricbuzz's only: leave out unless a second source confirms.

## 2. Story (the arc that makes people stay)
**Question for the whole video: "How do you score 85 off 89 balls and still not be the story?"** Answer structure:
1. Cold open: the score and the paradox (159/1, trail by 209) + "Jaiswal should have been out twice, and New Zealand threw away a review and then did not take the one that mattered."
2. Rewind: the day begins with NZ at 368 (callback to Day 1: from 70/5). India must bat 3 sessions vs the pace trio (Henry, Jamieson, Duffy).
3. Act 1, the squeeze (before tea): 8 overs, 16 runs. Three slips and a gully. A leave that missed the stump by a whisker.
4. Act 2, the three moments (reviews and the drop): the wasted review, the unreviewed LBW, the dropped catch at gully, and Henry's sweater.
5. Act 3, the flood (after tea): 143 in 31 overs; the full ball; 85 off 89; the fifty and the last 35 in 23.
6. Act 4, the sting: Jaiswal falls to a review Henry insisted on; then the grind: KL's fifty (116 balls), 29 runs in eleven overs; Duffy's 72 and six no-balls.
7. Close: what Day 3 decides (trail by 209, nine wickets, KL and Padikkal; new-ball/old-ball) + comment poll.

Note: Cricbuzz numbers overs from zero (3.6 is the end of the fourth over), so the script says "over four" for 3.6, "over five" for 4.2, "over seven" for 6.4, "over eight" for 7.3.

## 3. Storyboard: VERTICAL (Instagram + YouTube Short), about 150 s, lab look, ~380 words
1. **bignum** 159/1 · TRAIL BY 209 | JAISWAL 85 (89) · "He should've been out twice."
2. **photohero** (needs owner photo of Jaiswal; otherwise stage scene) JAISWAL 85 OFF 89.
3. **stats** THE SQUEEZE: 16 runs in 8 overs before tea; 5 maidens for Jamieson over the day (11-5-15).
4. **timeline** THE THREE MOMENTS: 3.6 NZ review lost | 4.2 Jaiswal on 0, edge past slip | 6.4 Henry LBW, no review | 7.3 Phillips drops Jaiswal on 6.
5. **statement** TEA.
6. **bars** WHAT NZ BOWLED: runs per ball by length (full 57 / 46 runs; good 33 / 10; short of length 38 / 24; short 45 / 16).
7. **compare** JAISWAL vs FULL / vs GOOD LENGTH: 27 balls 41 runs | 10 balls 0 runs.
8. **overstrip** THE DAY OVER BY OVER (runs per over, the wicket marked).
9. **bignum** 85 OFF 89 · 16 FOURS · 64 OF 85 IN BOUNDARIES.
10. **photocard / wicket** 27.5 c BLUNDELL b HENRY: THE REVIEW HE INSISTED ON.
11. **compare** AFTER THE WICKET: 29 RUNS IN 11 OVERS | KL 52 OFF 116 (SR 44.8).
12. **bars** NZ BOWLERS: JAMIESON 11-5-15-0 | HENRY 12-3-43-1 | SMITH 6-0-29-0 | DUFFY 10-0-72-0 (3 NO-BALLS; SMITH 3).
13. **poll** DAY 3: Does India get within 100? (<100 / 100-200 / more) + end card (YT Short: subscribe; IG: link in bio).

### Vertical script (to be voiced; names go to Devanagari at build)
1. India, one fifty-nine for one. Still two hundred and nine behind New Zealand's three sixty-eight. And the man who made eighty-five of those runs should have been out twice. Today's story: how Yashasvi Jaiswal got a second life, and how New Zealand threw away a review, and then did not take the one that mattered.
2. Eighty-five, off eighty-nine balls. Sixteen fours. Sixty-four of his eighty-five came in boundaries.
3. But start with the squeeze. Before tea, eight overs, sixteen runs. Three slips and a gully. Kyle Jamieson bowled over after over on the off stump and finished the day with eleven overs, five maidens, fifteen runs.
4. Then the drama. Over four, New Zealand review an lbw against KL Rahul, and lose it: the impact was outside off. Over five, Jaiswal, on nought, edges between third slip and gully. Four. Over seven, Matt Henry beats Rahul on the pads, two sounds, a huge appeal. Tom Latham, with a second left on the clock, does not review. Henry throws his sweater down. And over eight, Jaiswal, on six, edges to gully, where Glenn Phillips drops it.
5. Then tea. And everything changed.
6. After tea: a hundred and forty-three runs in thirty-one overs. And here is why. New Zealand's bowlers were full. Fifty-seven full balls, forty-six runs. The good-length ones? Thirty-three balls, ten runs.
7. Jaiswal against the full ball: twenty-seven balls, forty-one runs. Against good length: ten balls, no runs. Same bowlers, same pitch. The full ball gave him the innings.
8. His fifty took sixty-six balls. His last thirty-five took twenty-three. Then Matt Henry, adamant, got a review, and Jaiswal was caught behind. Against the run of play, on eighty-five.
9. After that, India scored twenty-nine in eleven overs. KL Rahul, fifty-two off a hundred and sixteen balls, his first Test fifty against New Zealand. Strike rate, forty-five.
10. Jacob Duffy bowled ten overs for seventy-two and no wicket. Six no-balls from Duffy and Nathan Smith, according to Cricbuzz's bowler lines. Jamieson, fifteen runs for the day, no wickets.
11. So, Day 3. Nine wickets in hand, two hundred and nine to find. Do India get within a hundred of New Zealand? Comment one, under a hundred. Two, a hundred to two hundred. Three, more.

## 4. Storyboard: LONG (YouTube, ~5.5 min, lab look; the same arc in nine beats)
1 Cold open (159/1, the paradox) · 2 Rewind: NZ 368 from 70/5, the pace trio (one line, no names for the morning until re-capture) · 3 Squeeze: 16 in 8 overs, Jamieson's maidens, off-stump line (compare: Day 1 India length) · 4 The lifelines timeline (3.6 / 4.2 / 6.4 / 7.3) with the review rule explained in one sentence · 5 Tea · 6 Flood: block-by-block bar chart (7, 27, 34, 39, 28, 10, 14), drinks 15 overs 81 runs · 7 Length chart + Jaiswal vs full / good (our classification, labelled) · 8 The wicket (27.5) and the slow hour (KL, 29 in 11 overs; fifty No. 22) · 9 NZ bowlers (Duffy 72, six no-balls; Jamieson 15) + Day 3 questions + poll. Script follows the vertical one with the extra beats at 3, 7 and 9 (~800 words).

## 5. Decisions I need from you
1. Re-capture the **NZ 1st Innings tab** so we can add the morning session (who scored the 125, who took the last five). If you would rather skip it, the video treats 368 as a given.
2. Photos: only Nicholls, Phillips, Latham, Bumrah exist on file. For Jaiswal and Rahul (and Henry, Jamieson, Duffy), hand over rights-cleared photos in chat if you want photo scenes; otherwise stage scenes with our own avatar.
3. Title (search-first): `India vs New Zealand - 1st Test Day 2 Analysis | 85 Off 89 and Three Lives` (Short: `85 Off 89 and Three Lives | India vs New Zealand 1st Test Day 2 #Shorts`). Alternative hook: `How NZ Wasted a Review`.
4. Short + IG at ~150 s as Day 1 (long after your approval; or vertical only first, like Bumrah).
