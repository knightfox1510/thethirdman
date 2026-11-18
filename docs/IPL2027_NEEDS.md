# IPL 2027: purses, squads and what each team needs (18 Nov 2026)

Method: `analysis/ipl2027_needs.py` over OUR ball-by-ball data (Sportmonks, IPL 2025 and 2026). Squads = retained + traded-in (`data/ipl2027/squads.json`). Output: `data/provenance/ipl2027_needs.json`.
**Capacity index** = balls the squad's players bowled or faced in a role in 2025-26 / (league total / 10). 1.00 = an average squad, below 0.60 = a clear hole. Quality = economy or strike rate of those balls against the league.
Roles: batting in the powerplay (overs 1-6), middle (7-15), death (16-20); pace bowling in the powerplay and at the death; spin in the middle overs. Players with no IPL data in our archive count as zero (new or uncapped). Wicketkeeper counts use our own classification.

## How solid is the squad data?
- Full retained and released lists: Yahoo Sports / Willow, 17 Nov 2026, 21:06 UTC. They carried duplicates (Vishnu Vinod twice, Arshin Kulkarni in both LSG lists) and left out some trade-ins; I applied the IPL's own press releases (CSK-SRH four-player deal, Natarajan, Shami and Siddharth to RR, Curran to LSG, Harshal to GT).
- **Check:** after those adjustments, every squad plus its open slots equals exactly 25 (CSK 19+6, MI 16+9, RCB 20+5, KKR 17+8, SRH 18+7, RR 19+6, DC 16+9, PBKS 19+6, GT 22+3, LSG 18+7), and the counts match Wikipedia's page for the teams it lists.
- **Purses and slots:** the same ten figures appear at Sportskeeda, Yahoo, M9 News and cricketnews.com. Treat them as reported, not official: the IPL had not published a table when read. Top-up of ₹5 cr before the mini-auction is mentioned by one outlet only.
- **Unresolved:** the Wikipedia page leaves out the last part of SRH's list; Yahoo's lists have no Shami/Siddharth at RR until the 17 Nov trade is applied (done here).
- **Correction to the 17 Nov brief:** Wikipedia's personnel-changes page records Ajinkya Rahane retiring on 30 July 2026, and Yahoo's captains piece says the same. Cricinfo still lists him among KKR's released names. Say "released and retired" only after a second look.

## Purses
| Team | Purse (₹ cr) | Open slots | Overseas slots | ₹ cr per slot |
|---|---|---|---|---|
| LSG | 47.45 | 7 | 3 | 6.8 |
| KKR | 41.65 | 8 | 3 | 5.2 |
| SRH | 40.15 | 7 | 3 | 5.7 |
| DC | 39.50 | 9 | 4 | 4.4 |
| MI | 32.60 | 9 | 2 | 3.6 |
| CSK | 28.05 | 6 | 2 | 4.7 |
| RR | 27.05 | 6 | 3 | 4.5 |
| PBKS | 18.60 | 6 | 2 | 3.1 |
| RCB | 14.15 | 5 | 1 | 2.8 |
| GT | 8.75 | 3 | 2 | 2.9 |
Total across the ten: ₹298 cr and 66 slots.

## Capacity by role (1.00 = average squad)
| Team | Bat PP | Bat mid | Bat death | Pace PP | Spin mid | Pace death | Keepers |
|---|---|---|---|---|---|---|---|
| CSK | 0.76 | 0.78 | 0.67 | **0.48** | 0.75 | **0.49** | 2 |
| MI | 1.07 | 1.00 | 0.93 | 0.84 | **0.42** | 1.00 | 2 |
| RCB | 0.97 | 1.01 | 0.95 | 1.17 | 1.20 | 1.13 | 3 |
| KKR | **0.46** | 0.61 | 0.65 | 0.60 | 1.08 | 0.66 | 1 |
| SRH | 0.60 | 0.86 | 0.84 | 0.98 | **0.45** | 0.97 | 3 |
| RR | 0.90 | 0.90 | 0.95 | 1.15 | 1.11 | 0.98 | 2 |
| DC | **0.46** | 0.88 | 1.05 | 0.56 | 0.78 | **0.45** | 3 |
| PBKS | 0.92 | 0.86 | 1.07 | 0.63 | 0.78 | 0.78 | 2 |
| GT | 1.09 | 1.02 | 0.98 | 1.25 | 1.04 | 1.12 | 4 |
| LSG | 1.09 | 1.00 | 0.77 | **0.46** | 1.13 | **0.43** | 2 |

## What each team needs (our reading)
| Team | Biggest gaps | Resources | Read |
|---|---|---|---|
| **LSG** | Powerplay pace (0.46) and death pace (0.43); death batting 0.77 | Largest purse, ₹47.45 cr, 7 slots, 3 overseas | Two pace bowlers, one a death specialist, and a finisher |
| **DC** | Opening batters (0.46), powerplay pace (0.56), death pace (0.45) | ₹39.5 cr, 9 slots, **4 overseas** (most flexible) | An opening pair and two pacers |
| **KKR** | Batting in every phase (PP 0.46, middle 0.61, death 0.65), pace 0.60-0.66; only 1 keeper | ₹41.65 cr, 8 slots, 3 overseas | The most holes: openers, a middle-order batter, pace; a keeper too |
| **CSK** | Pace in both phases (0.48, 0.49), death batting 0.67; Dhoni's finishing role is open | ₹28.05 cr, 6 slots, 2 overseas | New-ball and death pace, plus a finisher |
| **MI** | Spin (0.42): the three spinners they released took the spin overs | ₹32.6 cr, 9 slots, 2 overseas | Two spinners and a powerplay pacer (Boult, Chahar released) |
| **SRH** | Spin (0.45); powerplay batting 0.60 with Head released | ₹40.15 cr, 7 slots, 3 overseas | A spinner and an opener |
| **PBKS** | Pace quality, not quantity: economy 10.62 in the powerplay and 11.85 at the death, against 9.35 and 10.39 for the league; spin 0.78 | ₹18.6 cr, 6 slots, 2 overseas | Better pace bowlers on a modest purse |
| **RR** | Balanced; their powerplay strike rate (187) is the league's best, their death-over economy (10.6) is slightly worse than the league's | ₹27.05 cr, 6 slots, 3 overseas | Depth only; a death specialist at most |
| **RCB** | Balanced and deep (1.0 or above in every role bar batting 0.95-0.97) | ₹14.15 cr, 5 slots, **1 overseas** | Depth, within a small purse |
| **GT** | Deepest squad (1.0 or above everywhere, 4 keepers) | **₹8.75 cr, 3 slots** | Cheap backups only |

## The pool: who is actually available (released players, our 2025-26 numbers)
- **Openers (120+ powerplay balls):** Pathum Nissanka (DC) 169 strike rate, Travis Head (SRH) 167 but he has opted out of 2027 per Cricinfo, Ajinkya Rahane (KKR) 156 but retired per Wikipedia, Abhishek Porel (DC) 147. **Realistic openers: Nissanka and Porel.**
- **Finishers (50+ death balls):** Shahrukh Khan (GT) 180 on a small sample, Shimron Hetmyer (RR) 139 on 119 balls. **A thin market.**
- **Spinners (120+ middle-over balls):** Wanindu Hasaranga (LSG) 8.83 economy, AM Ghazanfar (MI) 8.78. **A thin market, and the two teams that need spin most (MI, SRH) have only these to choose from.**
- **New-ball pace (60+ powerplay balls):** Deepak Chahar 8.34, Trent Boult 9.29, Jaydev Unadkat 10.00, Mitchell Starc 10.03 (but reported unavailable for 2027), Spencer Johnson 10.47, Tushar Deshpande 10.53, Akash Deep 10.92, Avesh Khan 12.73.
- **Death pace (60+ balls):** Trent Boult 9.13, Mitchell Starc 9.40, Matheesha Pathirana 9.69, Avesh Khan 10.33, Tushar Deshpande 11.29.
**Pattern:** the pool is rich in pace, which suits LSG, DC, CSK and KKR, and thin in openers, finishers and spin, which are the needs of MI, SRH, DC and KKR. The auction pool will also include unretained and uncapped players not in these lists; the registration list (~3 Dec, unconfirmed) will change this picture.

## Caveats
1. Two seasons of data; a player who was injured or sat out in 2025-26 looks thin. New and uncapped players have no data and count as zero (CSK 18 of 19 players have data, RCB 17 of 20, SRH 16 of 18).
2. Roles are inferred from how players were used in 2025-26, not from a role label.
3. Capacity is relative to the league's average workload, not to what a coach would pick; a high index can hide ageing players (RCB, GT).
4. Everything here is our reading, not a prediction. Do not show it as fact on screen: label it "our model".

## Ideas to build on this (each needs the verification gate and a source check before it goes on screen)
1. **Data Story: "What every IPL team needs"**: ten cards in the sticker-album format, each with its three biggest gaps, its purse and slots.
2. **"Who's in the pool"**: the released players ranked by role, with the thin markets called out.
3. **Purse chart ("Money per slot")**: LSG ₹6.8 cr a slot against GT ₹2.9 cr, in the receipt or departures format.
4. **Best-fit board (opinion, labelled as such)**: for each released name, the teams whose gap he fills and who can afford him.
5. **Control-room page "Auction 2027"** on the site: purses, slots, needs and the pool in one place, updated as the lists firm up.
6. **Countdown content** to 16 Dec 2026 (14:30 IST, Goa, Star Sports and JioHotstar per Wikipedia); redo the pool when the registration list (~3 Dec) is out.
