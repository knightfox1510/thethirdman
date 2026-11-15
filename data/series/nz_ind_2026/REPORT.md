# NZ v IND ODI series 2026: analysis of the 4th and 5th ODIs (Bay Oval), in the context of the series

Everything below is derived by code from our own tables (`data/series/nz_ind_2026/`); series context for matches 1-3 is from Wikipedia (which cites Cricinfo match reports). Matches 1, 2, 4 and 5 are ball by ball (Cricbuzz captures; the 4th also has an independent Cricinfo capture that agrees over by over); this report covers the 4th and 5th in depth, SERIES.md the whole series. Win probability is from a model fitted on the Cricsheet ODI archive (see Method).

## Headlines

1. **India won by 22 runs defending 209, all out in 42.1 overs.** Our model gave New Zealand 78% to chase 210 before a ball was bowled, so this was a result the archive says happens about one time in five.
2. **The match turned at 158/7 in the 40th over** (over 40.4): Santner holed out to Arshdeep off Naman Dhir's bowling, India's win probability went from about 37% to 64% and never dropped below 50% again. It was the biggest single swing of the match (27 points).
3. **New Zealand's chase never accelerated.** They scored 4.1 an over in the first ten overs against a required 4.22, then 3.8 through the middle overs while the required rate climbed: after 30 overs 116/4, needing 94 at 4.7 (they were scoring 3.87); after 40 overs 155/6, needing 55 at 5.5 (scoring 3.88). 60.9% of their balls were dots.
4. **Drops almost decided it.** After the chances New Zealand put down (Axar Patel on 2, Shreyas Iyer on 5) India scored 61 more runs from those two batters; after India's two (Foxcroft on 5, Bracewell on 8) New Zealand scored 37. A net 24 runs, more than the 22-run margin. (Descriptive, not a counterfactual: a batter's later runs are not all down to the let-off.)
5. **Hidden winner: Naman Dhir.** Two overs, four runs, the Santner wicket: +0.26 win probability, second in the match behind Arshdeep Singh (the Player of the Match), yet eighth on a plain scorecard rank. **Hidden loser: Jacob Duffy** (3/60 in 8.1 overs, -0.20): three wickets that cost more than they gained.
6. **India's innings was a collapse in two parts.** 37/3 off the first 60 balls (70.0% dots, 5.0% boundary balls), then 5 wickets for 49 runs between overs 33.2 and 42.1. The last-wicket stand added 26 off 10 balls (183/9 to 209/10) but moved their win probability by only 7 points.
7. **Same ground, 48 hours apart, a different game.** New Zealand scored 333 (run rate 6.66, boundaries on 13.0% of balls) in the 4th ODI and 187 (run rate 3.88, 6.9%) in the 5th. India's bowling economy fell from 6.54 (pace) and 6.41 (spin) to 3.88 and 3.92, and their plan moved from 28.0 overs of pace and 22.0 of spin to 40.0 and 8.1.
8. **The series is 3-1 to India (one washout), but the two matches we have are opposites**: a 244-run defeat, in which India dropped the eventual centurion twice in the first two overs (the runs he made after the first drop: 120), and a 22-run win.

## Series context

| # | Date | Venue | Result | Player of the match | Ball by ball? |
|---|---|---|---|---|---|
| 1 | 2026-11-04 | Eden Park, Auckland | India won by 5 wickets (DLS): NZ 185 (40.2), India 143/5 (22.4), target 143 from 32 | Anshul Kamboj | yes |
| 2 | 2026-11-07 | Wellington Regional Stadium | India won by 4 runs (DLS): NZ 134 (41), India 113/7 (26), par 109 | Gurnoor Brar (4/30) | yes |
| 3 | 2026-11-10 | Seddon Park, Hamilton | No result (rain, no play) | - | no |
| 4 | 2026-11-13 | Bay Oval, Mount Maunganui | New Zealand won by 244 runs: NZ 333, India 89 (26.4) | Matt Henry (6/27) | yes |
| 5 | 2026-11-15 | Bay Oval, Mount Maunganui | India won by 22 runs: India 209 (42.1), NZ 187 (48.1) | Arshdeep Singh (3/30) | yes |

Source: Wikipedia, 'Indian cricket team in New Zealand in 2026-27' (Tier C; cites Cricinfo match reports); matches 4 and 5 are also in our own captures. India won the series 3-1 (one no result). The 3rd ODI had no play (rain). Matches 1, 2, 4 and 5 are ball by ball: the whole series is in SERIES.md.

## The 5th ODI in detail

### Win probability arc (India), end of every 5 overs

| Innings | After over | Score | India win prob. |
|---|---|---|---|
| 1 | 5 | 22/0 | 54% |
| 1 | 10 | 37/3 | 23% |
| 1 | 15 | 73/3 | 38% |
| 1 | 20 | 94/4 | 34% |
| 1 | 25 | 121/5 | 34% |
| 1 | 30 | 141/5 | 38% |
| 1 | 35 | 166/6 | 38% |
| 1 | 40 | 183/8 | 28% |
| 1 | 43 | 209/10 | 31% |
| 2 | 5 | 24/0 | 13% |
| 2 | 10 | 41/1 | 18% |
| 2 | 15 | 58/1 | 13% |
| 2 | 20 | 80/2 | 16% |
| 2 | 25 | 89/4 | 46% |
| 2 | 30 | 116/4 | 27% |
| 2 | 35 | 131/6 | 58% |
| 2 | 40 | 155/6 | 40% |
| 2 | 45 | 173/8 | 81% |
| 2 | 49 | 187/10 | 98% |

India's low point was 11% (inn2 over 15.6 (64/1)); the high was 98% at the end. Tipping point (last time the match crossed 50%): 158/7, over 40.4.

### The ten biggest swings

| When | Ball | Event | Swing | India win prob. after |
|---|---|---|---|---|
| inn2 40.4 | Naman Dhir to Mitchell Santner | wicket | -27 pts for the batting side | 64% |
| inn2 31.1 | Yash Thakur to Dean Foxcroft | wicket | -20 pts for the batting side | 64% |
| inn2 21.3 | Mohammed Siraj to Finn Allen | wicket | -19 pts for the batting side | 48% |
| inn2 30.6 | Auqib Nabi to Michael Bracewell | wicket | -18 pts for the batting side | 44% |
| inn2 42.4 | Arshdeep Singh to Kristian Clarke | wicket | -14 pts for the batting side | 84% |
| inn2 20.4 | Arshdeep Singh to Nick Kelly | wicket | -14 pts for the batting side | 29% |
| inn2 5.3 | Mohammed Siraj to Tim Seifert | wicket | -12 pts for the batting side | 25% |
| inn2 46.2 | Axar Patel to Jacob Duffy | wicket | -12 pts for the batting side | 88% |
| inn1 5.3 | Matthew Fisher to Rohit Sharma | wicket | -12 pts for the batting side | 42% |
| inn1 7.3 | Matthew Fisher to Virat Kohli | wicket | -11 pts for the batting side | 34% |

### New Zealand's chase against the required rate

| After over | Score | Needed | Required rate | Their run rate so far |
|---|---|---|---|---|
| 10 | 41/1 | 169 | 4.22 | 4.1 |
| 20 | 80/2 | 130 | 4.33 | 4.0 |
| 30 | 116/4 | 94 | 4.7 | 3.87 |
| 40 | 155/6 | 55 | 5.5 | 3.88 |
| 48 | 187/10 | 23 | 12.55 | 3.88 |

Their longest run of dot balls was 13 (ending over 23.1); the longest stretch without a boundary was 33 balls. The Cricbuzz commentary notes 11 dots in a row with a wicket in them against Foxcroft.

### Phases

| Side | Phase | Runs/wkts | Balls | Run rate | Dots | Boundary balls |
|---|---|---|---|---|---|---|
| India batting | powerplay (1-10) | 37/3 | 60 | 3.7 | 70.0% | 5.0% |
| India batting | middle (11-40) | 146/5 | 180 | 4.87 | 53.9% | 9.4% |
| India batting | death (41-50) | 26/2 | 13 | 12.0 | 53.8% | 30.8% |
| NZ batting | powerplay (1-10) | 41/1 | 60 | 4.1 | 63.3% | 8.3% |
| NZ batting | middle (11-40) | 114/5 | 180 | 3.8 | 62.2% | 7.2% |
| NZ batting | death (41-50) | 32/4 | 49 | 3.92 | 53.1% | 4.1% |

### Player value: win probability added (WPA), 5th ODI

| Player | Side | Batting | Bowling | Bat WPA | Bowl WPA | Total |
|---|---|---|---|---|---|---|
| Arshdeep Singh | IND | 14 (4) | 3/30 in 10.0 | 0.023 | 0.348 | 0.371 |
| Naman Dhir | IND | 22 (31) | 1/4 in 2.0 | -0.027 | 0.285 | 0.257 |
| Axar Patel | IND | 46 (55) | 2/28 in 6.1 | 0.089 | 0.038 | 0.127 |
| Matthew Fisher | NEW | 3 (6) | 2/28 in 7.0 | -0.066 | 0.15 | 0.084 |
| Ishan Kishan | IND | 46 (58) | 0/0 in 0.0 | 0.073 | 0.0 | 0.073 |
| Mohammed Siraj | IND | 14 (20) | 2/50 in 10.0 | 0.036 | 0.028 | 0.064 |
| Blair Tickner | NEW | 14 (19) | 1/24 in 5.0 | 0.024 | 0.023 | 0.046 |
| Yash Thakur | IND | 0 (4) | 1/38 in 10.0 | -0.062 | 0.093 | 0.032 |
| Auqib Nabi | IND | 5 (9) | 1/37 in 10.0 | -0.057 | -0.026 | -0.084 |
| Virat Kohli | IND | 5 (7) | 0/0 in 0.0 | -0.098 | 0.0 | -0.098 |
| Kristian Clarke | NEW | 16 (34) | 0/13 in 2.0 | -0.113 | -0.053 | -0.165 |
| Finn Allen | NEW | 1 (5) | 0/0 in 0.0 | -0.19 | 0.0 | -0.19 |
| Jacob Duffy | NEW | 9 (12) | 3/60 in 8.1 | -0.121 | -0.08 | -0.202 |

Definition: each ball's change in the batting side's win probability is credited to the batter and debited from the bowler (and the reverse for a falling probability). Hidden winners/losers: hidden winner: top-4 win-probability added but outside the top-4 of a plain scorecard rank (runs + 20 x wickets); hidden loser: bottom-5 win-probability added although inside the scorecard top-6.

### Catching: who turned wickets into swings

| Fielder | Catches | Win-probability swing of those wickets |
|---|---|---|
| Arshdeep Singh | 1 | 27 pts |
| Tim Seifert | 3 | 26 pts |
| Naman Dhir | 1 | 18 pts |
| Matthew Fisher | 2 | 14 pts |
| Ishan Kishan | 1 | 14 pts |
| Yash Thakur | 1 | 12 pts |

### Drops

| Fielding side | Batter | Over | Runs at the drop | Final | Runs after the drop |
|---|---|---|---|---|---|
| NZ | Axar Patel | 8.5 | 2 | 46 | 44 |
| NZ | Shreyas Iyer | 10.3 | 5 | 22 | 17 |
| India | Dean Foxcroft | 18.1 | 5 | 31 | 26 |
| India | Michael Bracewell | 25.5 | 8 | 19 | 11 |

### Bowling cards

| Bowler | Inn. | Overs | Runs | Wkts | Econ | Dots | Boundary balls | Style |
|---|---|---|---|---|---|---|---|---|
| Jacob Duffy | 1 | 8.1 | 60 | 3 | 7.35 | 57.1% | 7 | pace* |
| Matthew Fisher | 1 | 7.0 | 28 | 2 | 4.0 | 64.3% | 4 | pace |
| Kristian Clarke | 1 | 2.0 | 13 | 0 | 6.5 | 41.7% | 2 | pace* |
| Blair Tickner | 1 | 5.0 | 24 | 1 | 4.8 | 66.7% | 4 | pace* |
| Mitchell Santner | 1 | 10.0 | 47 | 3 | 4.7 | 56.7% | 5 | spin |
| Michael Bracewell | 1 | 10.0 | 35 | 1 | 3.5 | 53.3% | 2 | spin |
| Arshdeep Singh | 2 | 10.0 | 30 | 3 | 3.0 | 70.0% | 4 | pace |
| Mohammed Siraj | 2 | 10.0 | 50 | 2 | 5.0 | 61.7% | 7 | pace* |
| Auqib Nabi | 2 | 10.0 | 37 | 1 | 3.7 | 53.3% | 3 | pace |
| Yash Thakur | 2 | 10.0 | 38 | 1 | 3.8 | 58.3% | 3 | pace* |
| Axar Patel | 2 | 6.1 | 28 | 2 | 4.54 | 59.5% | 3 | spin |
| Naman Dhir | 2 | 2.0 | 4 | 1 | 2.0 | 66.7% | 0 | spin |

(* style assumed: not in our Cricinfo squad data.) Pace v spin: New Zealand: pace 22.1 ov 125/6 (econ 5.64), spin 20.0 ov 82/4 (econ 4.1); India: pace 40.0 ov 155/7 (econ 3.88), spin 8.1 ov 32/3 (econ 3.92).

## The 4th ODI, and 4th v 5th

### 4th ODI: the ten biggest swings

| When | Ball | Event | Swing | India win prob. after |
|---|---|---|---|---|
| inn1 14.2 | Axar Patel to Nick Kelly | wicket | -9 pts for the batting side | 35% |
| inn1 11.6 | Gurnoor Brar to Tim Seifert | wicket | -8 pts for the batting side | 28% |
| inn1 19.3 | Auqib Nabi to Dean Foxcroft | wicket | -8 pts for the batting side | 35% |
| inn2 0.1 | Matt Henry to Rohit Sharma | wicket | -8 pts for the batting side | 9% |
| inn1 1.3 | Auqib Nabi to Tim Seifert | SIX | +5 pts for the batting side | 42% |
| inn2 0.5 | Matt Henry to Virat Kohli | wicket | -4 pts for the batting side | 4% |
| inn1 6.2 | Gurnoor Brar to Tim Seifert | SIX | +4 pts for the batting side | 36% |
| inn1 0.6 | Arshdeep Singh to Will Young | FOUR | +4 pts for the batting side | 50% |

New Zealand scored 333 after India dropped Will Young twice in the second over, on the 5th and 6th balls (Rohit Sharma, then Ishan Kishan, both off Auqib Nabi): he was on 5 and made 125, i.e. 120 runs after the first let-off. India's drops cost 137 runs after the chances in total (Young 120, Santner 17). Matt Henry then took 6/27, including the first three India wickets in the first over (0/3).

### Side by side (same ground, 15 and 13 November)

| Side | Match | Score | Run rate | Dot balls | Boundary balls | Powerplay RR | Death RR |
|---|---|---|---|---|---|---|---|
| NZ batting | 4th: batting first | 333 | 6.66 | 47.3% | 13.0% | 7.2 | 6.8 |
| NZ batting | 5th: chasing | 187 | 3.88 | 60.9% | 6.9% | 4.1 | 3.92 |
| India batting | 4th: chasing | 89 | 3.34 | 70.6% | 6.2% | 2.6 | - |
| India batting | 5th: batting first | 209 | 4.96 | 57.7% | 9.5% | 3.7 | 12.0 |

**What changed.** (a) New Zealand's powerplay went from 72/0 (7.2) to 41/1 (4.1): Arshdeep Singh's figures were 10.0-55-1 in the 4th and 10.0-30-3 in the 5th, and the commentary shows India setting slips for the new ball (one slip to start, two slips for Siraj, a wide slip for Thakur). (b) India moved from a spin-heavy attack (22.0 overs of spin at 6.41 an over, 28.0 of pace at 6.54) to pace (40.0 overs at 3.88; spin 8.1 at 3.92). (c) New Zealand moved the other way: from 2.0 overs of spin to 20.0, and their spinners (4.1 an over) were more economical than their seamers (5.64). (d) India's batting still lost its top three cheaply (0/3 in the 4th; 34/3 in the 5th), but the 5th had more boundary balls (9.5% against 6.2%) and fewer dots (57.7% against 70.6%).

## Series-level observations we can support (and what we cannot)

- **Toss:** the side winning the toss chose to field in all five matches (Wikipedia: India in 1-4, New Zealand in 5). In the two we have ball by ball, the side batting first won the 4th (NZ, 333) and the 5th (India, 209): defending, not chasing, produced the results at Bay Oval.
- **Catching** is a recurring theme: in the two matches we hold, India dropped 3 chances in the 4th and 2 in the 5th, and New Zealand 1 and 2. A Cricbuzz note during the 5th ODI chase says India had made 14 misfields and dropped eight catches in the series so far (catching efficiency 74.1%): a lead for the whole series, which we can only confirm once matches 1-3 are captured.
- **Kohli's series:** Wikipedia lists him as India's leading run-scorer with 86; the Cricbuzz notes say the 5th ODI gave him a third single-digit score in the series. (Both leads: from the 4th (0) and 5th (5) we have, the other two innings are not ours.)
- **See SERIES.md** for the leaderboards, powerplay table, drops and catches across the four matches that were played.

## Video angles this supports (all numbers above are code-derived; check against Cricinfo before use)

1. **"The 22% win"**: India defended 209 against a model's 78% chase: the Santner moment (27 points), the drops (net 24 runs against a 22-run margin), the dot-ball squeeze. Long + Short.
2. **"Two days at Bay Oval"**: the 4th v 5th table: same ground, same toss decision, opposite results; India's pace plan, NZ's spin plan. Long.
3. **"The hidden winner"**: Naman Dhir's 2-0-4-1 (and Yash Thakur's debut, "two in two" at 30.6/31.1: Nabi's Bracewell then Thakur's Foxcroft, a combined 39-point swing). Short.
4. **"The cost of a drop"**: Will Young, 125 after two chances in two balls. A Data Story across the series (SERIES.md: India dropped eight chances in four matches, the batters let off first scored 244 more runs).

## Method, validation and limits

- **Tables:** `dataops/cricbuzz_balls.py` turns the Cricbuzz commentary into one row per delivery (wides and no-balls included); runs per delivery are the change in team score; innings totals are asserted against the last score in the commentary. Runs off the bat are the change in the striker's own total.
- **Validation (`analysis/nz_ind_validate.py`, 14 checks):** innings totals and overs, Axar 46 (55), Foxcroft 31 (42), Arshdeep 3/30, Santner 3/47 (5th ODI), Young 125 (108), Henry 6/27, Axar 2/39, Kishan 27 (53) (4th ODI) all equal Wikipedia's match boxes; NZ's pace 6/125 in 22.1 and spin 4/82 in 20 overs equal Cricbuzz's own editorial line; the 4th ODI's runs agree with the independent Cricinfo capture in all 77 overs.
- **Win-probability model (`dataops/winprob.py`):** logistic regression for chases and a projected-total model for first innings, fitted on 1,719 men's 50-over ODIs (Cricsheet, 2009 onwards, no rain method). Held-out chases: log loss 0.359, accuracy 83%, and the calibration bins sit within a few points of the actual win rates. It is an indication, not a fact: the archive is a sample, it knows nothing about this ground, these players or the pitch, and a 'win probability' is a modelling choice. Values are shown rounded.
- **Cricbuzz-only for the 5th ODI:** no line, length, shot or wagon data (only the 4th has the Cricinfo capture); a few dismissal kinds and fielders are parsed from commentary text. Bowling styles come from the Cricinfo squad data where we have it (starred where assumed).
- **Unverified leads kept out of the numbers:** Cricbuzz editorial notes (e.g. catching efficiency, 'second instance of India bundled out for' ...). Treat them as leads to check on Cricinfo.