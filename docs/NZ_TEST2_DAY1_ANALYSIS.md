# NZ v IND, 2nd Test, Hagley Oval, Day 1 (27 Nov 2026): in-depth analysis

Source: the owner's Cricinfo capture of match 1539443 (517 deliveries: line, length, shot, control, wagon zone, plus the day's ball-by-ball text with speeds, reviews and chances). Every bowler's figures and every batter's runs reproduce the official scorecard (checked). Ground and series history: Cricsheet men's Tests (our archive; partial before 2001-02, so never used for "first/only/never"). Scripts: `analysis/nz2_day1.py`, `analysis/nz2_ground.py`; tables in `data/provenance/nz2_day1_figures.json`, `nz2_ground_figures.json`; ball table `data/cricinfo/nz2_day1_balls.csv`.
No source is named in any video made from this; credit them in the description only.

## 1. The day in one paragraph
India chose to field. New Zealand finished **246/5 in 85 overs** (run rate 2.89; Blundell 53*, Phillips 36*). The openers added **77** before India broke through on the last ball before lunch; the day turned in a **14-ball spell (overs 41.3 to 43.6) where three wickets fell with no run added (110/1 became 110/4)**; Mitchell and Blundell then put on 74 and Blundell and Phillips an unbroken 62. India's attack bowled **232 good-length balls for 57 runs and four of the five wickets**, but gave away **106 runs off 138 full balls** (43% of the day's 246) and bowled **seven no-balls, all by Gurnoor Brar**. Wickets: 5; false shots: 112 in 510 balls (22.0%); the bowling side got a wicket from 1 in 22 of them.

## 2. How the day moved
| Phase | Overs | Runs | Wkts | Run rate | Dot balls | Not in control | Left alone |
|---|---|---|---|---|---|---|---|
| Session 1 (to lunch) | 1-26 | 77 | 1 | 2.96 | 77.6% | 21.8% | 28.8% |
| Session 2 (to tea) | 27-50 | 54 | 3 | 2.25 | 85.4% | 28.5% | 31.9% |
| Session 3 (to stumps) | 51-85 | 115 | 1 | 3.29 | 73.8% | 17.6% | 22.4% |
| New ball (taken at 80.3) | 81-85 | 9 | 0 | 1.8 | 83.3% | 26.7% | 36.7% |
- **Session 2 was India's**: the slowest scoring (2.25), the most dot balls (85%), the most false shots (28.5%) and three wickets. **Session 3 was New Zealand's**: 3.29 an over, 14 of the day's 26 fours, false shots down to 17.6%, and left-alone balls down to 22%. India had the ball moving through the middle session (the commentary mentions seam or straightening 16 times in session 2 against 2 mentions of swing); after tea it mentions swing 15 times and bounce 14 (the harder, older ball coming on) but the batters were more in control.
- **The first ten overs** (new ball, India fielding first): 26 runs, no wicket, 20% false shots, 35% of balls left. The openers saw off Bumrah and Anshul Kamboj; the first wicket needed a late review (Conway lbw, 25.6).
- **The collapse (overs 41-44)**: 24 balls, 4 runs, 3 wickets, 92% dot balls, 46% of balls left alone. Akash Deep took Latham and Ravindra with the same delivery (full length on a close-to-off line that seamed away and took the edge); Anshul Kamboj took Nicholls with a short ball pulled to deep backward square leg.

## 3. India's bowling
Overs-maidens-runs-wickets are the official figures (checked). "Not in control" is Cricinfo's control flag. Speeds are only the ones the commentators quoted (n in brackets): a hint, not a measurement.
| Bowler | O-M-R-W | Econ | Dots | Not in control | Full+good / short | Full | Speed (n) |
|---|---|---|---|---|---|---|---|
| A Kamboj | 17-5-56-1 | 3.29 | 77.5% | 17.6% | 72% / 28% | 28% | 132 (15) |
| Akash Deep | 21-6-52-2 | 2.48 | 80.2% | 27.0% | 73% / 26% | 21% | 137 (20) |
| Gurnoor Brar | 19-4-52-1 | 2.74 | 80.7% | 21.9% | 58% / 42% | 22% | 138 (36) |
| JJ Bumrah | 19-4-37-0 | 1.95 | 84.2% | 22.8% | 78% / 22% | 31% | 133 (46) |
| Washington Sundar | 9-1-36-1 | 4.0 | 64.8% | 16.7% | 96% / 4% | 41% | n/a (0) |
- **What worked: the good length.** 232 balls, **1.47 an over, 83.6% dots, 24% not in control, 4 wickets**. Back of a length: 117 balls at 3.49 an over, 27% not in control, 1 wicket. **What leaked: the full ball.** 138 balls at **4.61 an over**, only 15% not in control, no wicket: 12 of the 26 fours came off full balls (12 more off back-of-a-length balls, only 2 off good length). The batters scored freely when India pitched it up and were beaten when India held the length.
- **Lines:** 67% outside off, 24% on the stumps, 6% down the leg side, 3% wide. Down-leg balls cost 4.45 an over and were the least controlled (52% not in control: the batters were flicking across the line). On the stumps: 2.90 an over. Outside off: 2.48.
- **Bumrah: 19-4-37-0 is a pure bad-luck spell.** Economy 1.95, 84% dots, **26 false shots (23%) and no wicket**; the commentary notes he was "struggling to get his speeds up" (128 to 133 kph) at 47.4. He bowled the fullest plan of the five (31% full, 78% full-or-good). At this ground in our archive he had 5 wickets at 20.2 in the 2020 Test.
- **Akash Deep: 21-6-52-2**: the best of the day. The heaviest good-length share (52%), the most false shots induced (34), the fastest average of the quoted speeds (137 kph), two wickets, and a dropped chance behind them.
- **Gurnoor Brar: 19-4-52-1**: the short-ball bowler (42% short or back of a length, 12% short; the highest of the five) and the quickest quoted speeds (up to 142 kph). **Seven no-balls**: 7 free runs and about an over's worth of extra balls; one came on a ball that beat Latham's outside edge (19.5).
- **Anshul Kamboj: 17-5-56-1**: the shortest-speed seamer (132 kph average quoted); 71% full-or-good, 5 maidens. **Washington Sundar: 9-1-36-1** ran in at 4.00 an over, 96% full or good length, the only spinner; his wicket (Mitchell, bat-pad at 64.4) came from turn and bounce.

## 4. New Zealand's batting
(Runs and balls as on the scorecard; the other columns from our ball table.)
| Batter | Runs (balls) | SR | Left alone | Attacking shots | Not in control | Dots |
|---|---|---|---|---|---|---|
| Tom Latham | 59 (128) | 47.2 | 32.0% | 39.2% | 24.8% | 80.0% |
| Devon Conway | 31 (79) | 39.2 | 31.6% | 29.1% | 22.8% | 81.0% |
| Henry Nicholls | 16 (46) | 34.8 | 34.8% | 43.5% | 23.9% | 82.6% |
| Rachin Ravindra | 0 (9) | 0.0 | 55.6% | 0.0% | 11.1% | 100.0% |
| Daryl Mitchell | 31 (74) | 43.7 | 18.3% | 38.0% | 18.3% | 73.2% |
| Tom Blundell | 53 (117)* | 45.7 | 19.8% | 37.9% | 21.6% | 76.7% |
| Glenn Phillips | 36 (64)* | 56.2 | 25.0% | 46.9% | 20.3% | 73.4% |
- **Latham, 59 (128): left 32% of balls, played 39% of balls with an attacking shot and was not in control of 25%**: lucky and patient. He made 50 off 88 balls (fifty "in fortunate fashion", an outside edge through second slip at 27.3), and by the 2nd drink was already 29. He moved past McCullum's Test run tally during the innings (commentary).
- **Blundell, 53* (117): the least expansive** (defended 49 of 116 balls, 38% attacking, 98 hundredths of a run per attacking shot) and the most patient partner for Mitchell (74) and Phillips (62*).
- **Conway: 31 (79), SR 39**: left 32% and not in control of 23%: a scratchy start (played and missed at 1.2, 8.5, 8.6, 9.2; edged past the slips at 10.4) before the lbw.
- **Where the runs came (off the bat, 226):** leg-side shots (flick, glance, on-drive, pull) **98 runs off 96 balls**, off-side shots (cover drive, square drive, cut, steer, dab) **84 runs off 60 balls**, straight bat and defence **37 off 213**, **138 balls left alone**. Fours: 26, so **104 of the 226 bat runs (46%)**; no six. Extras: 20 (13 byes and leg byes, 7 no-balls). The off-side shots were the most efficient (1.40 a ball); the leg-side shots were the least controlled (40 of 96 not in control: balls angled in across the left-handers).
- **Partnerships:** 77 (Latham-Conway, 156 balls, 2.96 an over), 33 (Latham-Nicholls, 93 balls), 0 (Nicholls-Ravindra, 4 balls), 0 (Mitchell-Ravindra, 11 balls), **74 (Mitchell-Blundell, 124 balls, 3.58)** and **62* (Blundell-Phillips, 122 balls, 3.05)**.

## 5. Chances, reviews and luck
- **The drop:** Rahul dropped a thick edge at second slip at **14.1 off Akash Deep**. Cricinfo's scoring has Latham on strike; the commentary text names Conway: they disagree, so any script says "a catch put down at second slip" without naming the batter. Latham went on to 59.
- **Edges that fell where no fielder stood (commentary): 10.4** (Conway, past second slip), **27.3** (Latham's fifty: through the hands of second slip, grounded), **44.2** (Blundell, streaky four past the cordon), **58.6** (Mitchell, "only two slips"), **61.5** (Mitchell, "no third slip: would have been gobbled up"), **73.4** (Phillips, wide of the diving second slip), **83.1** (Blundell, just short of gully), plus a top-edged pull that fell short of cover (37.4) and a deflection off Pant's glove to first slip (38.3).
- **Reviews and lbws:** NZ reviewed twice (0.5, Latham, upheld: the ball missed leg stump; 25.6, Conway, struck down), India once (47.5, Blundell lbw, struck down). India did not review a big lbw against Latham at 14.2; further lbw appeals were turned down at 22.5, 29.3 (Latham), 33.3 (Nicholls: "height is a problem"), 63.1 and 79.5 (Blundell: high or down leg).
- **False shots to wickets:** 112 balls not in control, 5 wickets, all five on not-in-control balls. By bowler: Akash Deep 34 for 2, Gurnoor Brar 25 for 1, Bumrah 26 for 0, Anshul Kamboj 18 for 1, Sundar 9 for 1.

## 6. The five wickets
| Over | Score | Bowler | Batter | How | Ball |
|---|---|---|---|---|---|
| 25.6 | 77/1 | Gurnoor Brar | Conway | lbw (review failed) | good length, outside off, scramble-seam, past the inside edge onto the back pad |
| 41.3 | 110/2 | Akash Deep | Latham | c Pant | good length close to off, straightened off the pitch, edge |
| 42.1 | 110/3 | Anshul Kamboj | Nicholls | c Akash Deep | short, around leg, pulled to deep backward square leg |
| 43.6 | 110/4 | Akash Deep | Ravindra | c Pant | full length close to off, seamed away, edge |
| 64.4 | 184/5 | Washington Sundar | Mitchell | c Jurel | turn and bounce, backward short leg |

## 7. The ground: Hagley Oval (our archive: 15 men's Tests, 2014 to 2025)
| Year | Match | Toss | Innings totals | Result |
|---|---|---|---|---|
| 2014 | New Zealand v Sri Lanka | Sri Lanka field | 441, 138, 407, 107 | New Zealand by 8 wkts |
| 2016 | New Zealand v Australia | Australia field | 370, 505, 335, 201 | Australia by 7 wkts |
| 2016 | New Zealand v Pakistan | New Zealand field | 133, 200, 171, 108 | New Zealand by 8 wkts |
| 2017 | New Zealand v Bangladesh | New Zealand field | 289, 354, 173, 111 | New Zealand by 9 wkts |
| 2018 | England v New Zealand | New Zealand field | 307, 278, 352, 256 | draw |
| 2018 | New Zealand v Sri Lanka | Sri Lanka field | 178, 104, 585, 236 | New Zealand by 423 runs |
| 2020 | New Zealand v India | New Zealand field | 242, 235, 124, 132 | New Zealand by 7 wkts |
| 2021 | Pakistan v New Zealand | New Zealand field | 297, 659, 186 | New Zealand by an innings and 176 runs |
| 2022 | New Zealand v Bangladesh | Bangladesh field | 521, 126, 278 | New Zealand by an innings and 117 runs |
| 2022 | South Africa v New Zealand | New Zealand field | 95, 482, 111 | New Zealand by an innings and 276 runs |
| 2022 | South Africa v New Zealand | South Africa bat | 364, 293, 354, 227 | South Africa by 198 runs |
| 2023 | Sri Lanka v New Zealand | New Zealand field | 355, 373, 302, 285 | New Zealand by 2 wkts |
| 2024 | New Zealand v Australia | Australia field | 162, 256, 372, 281 | Australia by 3 wkts |
| 2024 | New Zealand v England | England field | 348, 499, 254, 104 | England by 8 wkts |
| 2025 | New Zealand v West Indies | West Indies field | 231, 167, 466, 457 | draw |
- **Toss:** 14 of 15 teams chose to field (India did the same today). The toss winner won 10 of 15. **Batting first won only 4 of the 13 decided Tests**; 2 draws.
- **Par:** first-innings average **288.9** (range 95 to 521; median 297); Hagley runs per over **3.39** against 3.29 across all New Zealand venues in our archive (and 3.39 at Hagley); runs per wicket 32.3. Today's 2.89 an over is **15% below the Hagley rate**.
- **After 85 overs in the first innings** (the six first innings that lasted that long): 232/3, 278/8, 325/9, 332/1, 336/8, 439/8, average 324/6.2. **New Zealand's 246/5 would be the second-lowest of the seven**, but with five wickets down, not eight or nine.
- **How wickets fall at Hagley:** 494 wickets in our archive: **72% caught, 14% bowled, 10.5% lbw**, 1.4% run out, 1.4% caught and bowled. Today: 4 caught, 1 lbw.
- **Batters at Hagley (our archive):** Latham 27 innings, 1,299 runs, **average 50.0**; Mitchell 11 innings, average 55.3; Rachin Ravindra 6 innings, average 53.8; Nicholls 17 innings, average 44.1; Conway 10 innings, average 33.5; Blundell 14 innings, average 30.1 (53* today); Glenn Phillips 4 innings, average 31.7.
- **Bowlers at Hagley:** Bumrah, 5 wickets at 20.2 (2020, India's only Test here); Matt Henry 40 wickets at 23.3; Kyle Jamieson 28 wickets at 17.6. Both Henry and Jamieson are in the NZ XI and still to bat or bowl.

## 8. India in New Zealand (our archive, 2009 to 2020: 7 Tests)
New Zealand won 3, India 1 (Hamilton, 2009, by 10 wickets), 3 drawn. India's only previous Test at Hagley: **29 Feb to 2 Mar 2020**, New Zealand won by 7 wickets (India 242 and 124, New Zealand 235 and 132/3). Series so far this tour: the 1st Test at the Basin Reserve was a **draw**.
**Day 1 against Day 1, Test 1 vs Test 2:** New Zealand were **243/5 in 81.6 overs** at the Basin Reserve (Nicholls 113*, Phillips 94* at the close) and **246/5 in 85 overs** at Hagley. Almost the same score, but a different shape: in Wellington four wickets fell inside 29 overs (Bumrah took 3 in the day); here the first wicket needed 25.6 overs and Bumrah took none.

## 9. What Day 2 looks like
- **The unbeaten pair** (Blundell 53*, Phillips 36*, 62 in 122 balls) face India with the second-new-ball effect gone (taken at 80.3; they scored 9 off its first 30 balls, 83% dots, 27% not in control: it did not hurt them). Phillips was struck on the right thumb at 65.6 (commentary): worth watching.
- **The tail to come:** Smith, Jamieson, Henry, Duffy. Jamieson and Henry are the better batters of the four; Hagley's first-innings range is 95 to 521, so **330 to 370 is a plausible first innings if the pair add 90 to 120 at 3 an over (our scenario, not a forecast).**
- **India's problem** is not control (they induced 22% false shots, the highest of any phase in session 2) but **finishing the chances and the full ball**. If India hold the good length on a second morning, the pair has 4 wickets of cover but 112 false shots in the book for a reason.

## 10. Checks before any video
- The 14.1 dropped catch: Cricinfo's scoring and its commentary text disagree on the batter (Latham or Conway).
- Speeds are only from commentary mentions (Bumrah 46 of 114 balls); label as "quoted".
- The Cricsheet Hagley sample is 15 Tests (2014 to 2025): say "in our archive", never "has never/first time".
- The 2026 Basin Reserve comparison uses our earlier Day 1 capture (a different source and classification): compare scores and wickets, not lengths.
- Photos: send the Test 2 images you want used (rights as before); no broadcast footage unless you confirm.

## 11. Video options
1. **Vertical ~160 s "The 14 balls that turned Day 1"**: 110/1 to 110/4, same delivery twice, the good-length-vs-full split (1.47 vs 4.61), the dropped catch, Bumrah's 0-for.
2. **Vertical "India's full-ball problem"**: 138 full balls, 106 runs, 12 fours; the same plan produced 4 wickets from 232 good-length balls.
3. **Long "Day 1 analysis"**: all of the above plus Hagley history, India in New Zealand and the Day 2 scenarios.
