# Replay Room Ep. 1: NZ v India, 4th ODI, Mount Maunganui (13 Nov 2026)
Data: Cricinfo + Cricbuzz captures (data/cricinfo|cricbuzz/nz_ind_4odi.json), imported with cricinfo_import.py; over-by-over runs match. Official result in both: NZ won by 244 runs; Player of the Match Matt Henry.

## The story
NZ 333 all out (49.6 ov). India 89 all out (26.4 ov). Two innings, two different matches: one slowly built on a reprieve, one over before the chase had even started.

## Facts (all from our ball table; verify the ones marked V before narration)
- Young 125 off 108 (14 fours, 4 sixes). 24 false shots in 108 balls; 8 in his first 25 balls, then 2 in balls 51-75; scoring 22 / 28 / 35 / 40 runs per block. Dropped twice early (Cricbuzz note, V).
- Where his runs came: cut 27, cover drive 23, pull 16, sweep 12; off Kuldeep 42 off 24, Brar 32 off 22.
- NZ by 10-over block: 72/0, 53/3, 89/0, 51/3, 68/4. Overs 21-30 the swing: 89 runs, batters out of control on 10% of balls.
- NZ hit 28 fours + 12 sixes (184 runs in boundaries); India 8 fours + 2 sixes (44). Dot balls: NZ 47%, India 74%.
- India bowlers' false-shot rate vs wickets: Arshdeep 33% for 1 wkt; Axar 12% for 2; Nabi 25% for 4. India dropped four catches (V: "most among full members since 2025, 50 drops").
- Chase: Henry's first over = Rohit 0 (1), Kohli 0 (4), Iyer 0 (1): 0/3. Gaikwad out at 9/4. 26/4 after the powerplay. Henry 6/27 off 10. Seven of India's ten were out defending. Top score: Kishan 27.
- Henry's plan: 34 of 58 legal balls outside off stump, 50% short or back of a length; 29% false shots drawn.
- V (leads from the notes): 9/4 equals India's 9/4 v Zimbabwe, 1983; Rohit and Kohli both ducks in an ODI for only the second time; India's lowest ODI total v NZ; margin vs India's biggest defeats. Series: India led 2-0 before this match, so 2-1 going into the 5th ODI on 15 Nov (V).

## Package
1. Long, 8-9 min: "333 and 89: what happened at Mount Maunganui". Cold open on 0/3. Beats: the result; the over that decided it (pitch map, Henry's line and length); Young's innings (wagon wheel, false-shot timeline, the two lives); why NZ went big (phase control, drops, India's short-of-length plan); what India did wrong in the chase (out defending, dots); verdict and what it means for the 5th ODI.
2. Short A (today): "0 for 3: Henry's first over".  Short B: "Will Young: two innings in one".  Short C: "74% dots: India out defending".
3. Look: Replay Room (Lab charts, board scenes for lines and lengths, stage scenes for key balls). No Cricinfo/Cricbuzz graphics or text.
4. Process: make_replay_4odi.py builds the spec and asserts every number; stills check; build; Drive sync; upload only on request; add rows to the Tracker; credit both sites in sources.
