# What every IPL team needs: voice-over script (DRAFT for approval, 18 Nov 2026)
Long ~5 min (about 650 words). Devanagari = how the name is written in `vo`; screen text uses English. Numbers are spelled out. "Capacity" = our index: 100% is an average squad (IPL 2025-26, Sportmonks). No audio is generated until you approve.

**1 Hook (frame 1)**
Two hundred and ninety-eight crore rupees. Sixty-six slots. Ten teams. One auction, on the sixteenth of December, in गोवा. Before a single bid, we looked at what each squad is missing.

**2 Method (frame 1 → 2)**
Here is how. We took every squad as it stands today, retained players plus trades. Then we measured, from two seasons of ball-by-ball data, how many balls those players face and bowl in each phase. Hundred percent is an average squad. Below seventy is a hole.

**3 Purse (frame 2)**
First, the money. लखनऊ have the most, forty-seven crore, for seven slots. Kolkata, forty-one. Hyderabad, forty. Delhi, thirty-nine, and nine slots to fill. Then Mumbai, Chennai, Rajasthan. Punjab have eighteen. Bengaluru, fourteen. And Gujarat, under nine crore, for three slots.

**4 Need map (frame 3)**
Put it all in one grid, and the picture is clear. Pace is the league's biggest hole. Bowling at the death, and with the new ball. Spin is thin at Mumbai and Hyderabad. And Kolkata are thin almost everywhere. Let's go through them, most needy first.

**5 KKR (frame 4)**
Kolkata. Batting is thin in every phase. Powerplay, forty-six percent of average. Middle overs, sixty-one. Death overs, sixty-five. Only one wicketkeeper. And pace is at sixty percent. Forty-one crore, three overseas slots, and a long list.

**6 CSK (frame 5)**
Chennai. Pace is the hole. Forty-eight percent in the powerplay, forty-nine at the death. Death batting is also thin, at sixty-seven. Twenty-eight crore, six slots, two overseas.

**7 DC**
Delhi. Their openers are at forty-six percent. Pace is the problem in both phases, fifty-six in the powerplay, forty-five at the death. Thirty-nine crore, and the most overseas slots in the league, four.

**8 LSG**
लखनऊ have the biggest purse, and the clearest need. Pace, both ends. Forty-six percent with the new ball, forty-three at the death. Their batting at the death is a little short too, at seventy-seven.

**9 SRH**
Hyderabad. Spin is at forty-five percent, and the powerplay batting, which drives their whole approach, is at sixty. Forty crore says they can fix both.

**10 PBKS**
Punjab. The issue is not how much, but how well. Their pace bowlers go for ten point six runs an over in the powerplay and eleven point eight at the death. The league's are nine point three and ten point four. Eighteen crore, six slots.

**11 MI**
Mumbai. A strong squad with one hole: spin. Forty-two percent of average. A wrist-spinner is the missing piece, and thirty-two crore can buy one.

**12 RR, RCB, GT**
Rajasthan are balanced. Their powerplay batting strikes at one eighty-seven, the best in the league. Bengaluru are balanced too, with fourteen crore and five slots. And Gujarat are the deepest squad of all. Three slots, under nine crore. They will be watching, not shopping.

**13 Pool (frame 6)**
Now, who is out there? The registered list comes around the third of December, so this is only the players the teams released. Pace is rich: Trent Boult, मथीशा पथिराना, दीपक चाहर. Spin is thin: वानिन्दु हसरंगा, then very little. Openers: पथुम निसंका. Travis Head is reported out. And finishers, the thinnest market of all.

**14 Bids (frame 7)**
So who could draw the biggest bids? This is our model, an opinion, not a price prediction. Trent Boult: good in the powerplay and the death, and four teams with a hundred and fifty-six crore between them could want him. मथीशा पथिराना: the best death bowler on the market. वानिन्दु हसरंगा: the only proven wrist-spinner, and both Mumbai and Hyderabad need spin. दीपक चाहर: an Indian new-ball bowler, no overseas slot needed. पथुम निसंका: the best realistic opener.

**15 Caveat**
One warning. Mitchell Starc and Travis Head are reported unavailable, and the official list is not out. We will update this on the third of December.

**16 Close (frame 8)**
Which team wins this auction? Tell us in the comments. And subscribe, for the breakdown when the list drops.

---
## Checks before generation
- Add to voice_lint.NAMES: मथीशा पथिराना (Pathirana), वानिन्दु हसरंगा (Hasaranga), दीपक चाहर (Chahar), पथुम निसंका (Nissanka), गोवा; also लखनऊ / Kolkata etc. stay English except LSG city (flagged: say "Lucknow" in English instead?).
- Claims to run through `Claims.check`: purses, slots, overseas slots (squads.json vs a second source e.g. Cricinfo/Sportskeeda), all capacity percentages (our model, single source: say "in our archive"), PBKS economies, RR PP strike rate 187, Boult 156 crore buyers sum (47.45+41.65+39.5+28.05=156.65, so say "over a hundred and fifty crore").
- Vertical cut (owner: ~150 s, about 400 words; YouTube Shorts allow up to 3 min, and 150 s is under Instagram's 3-min Reel limit). Same script, trimmed, all ten teams kept:
  | Beat | Source | Time |
  |---|---|---|
  | Hook | 1 | 10 s |
  | Method + purse (one line each, top 3 and bottom 2 only) | 2, 3 | 20 s |
  | Need map | 4 | 12 s |
  | KKR, CSK, DC, LSG, SRH (two numbers each) | 5-9 | 50 s |
  | PBKS, MI | 10-11 | 18 s |
  | RR, RCB, GT | 12 | 8 s |
  | Pool | 13 | 10 s |
  | Bids (Boult, Pathirana, Hasaranga, Chahar, Nissanka) | 14 | 16 s |
  | Starc/Head caveat + close | 15-16 | 10 s |
  Vertical frames re-laid out 1080x1920 inside the grid-safe band; logos kept.
