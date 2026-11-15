# Pitch-view model: what it covers (and what it cannot)

`pitchview.py` (model) + `pitchview_text.py` (commentary leads) + `pitchview_render.py` (3D + poster + animation). One `Delivery` per ball, built from ANY captured match:
`from_table(csv, capture_json, inning, over, cricbuzz=<cricbuzz capture>)`. Nothing is specific to one match or one bowler.

## Data vs model (always labelled on screen)
| Thing shown | Source | Status |
|---|---|---|
| Line and length zone, shot, control flag, runs | Cricinfo ball table | data |
| How out (caught / bowled / lbw / stumped), catcher's name, keeper catch (dagger) | Cricinfo capture dismissal text | data |
| Batting hand | inferred from the shot directions (off-side shots at wagon x < 180 = right-hander) | data-derived |
| Speed, named fielding position, "diving / one-handed", which way the fielder moved, "kept low / extra bounce", seam movement, the length the commentator names | Cricbuzz commentary text | LEADS: structured, never copied; disagreements with Cricinfo are flagged on the poster |
| Ball height, bounce, arcs, release height, restitution | model; for bowled/lbw the rebound is solved so the ball is under stump height at the stumps | illustrative |
| Batter's height (default 1.80 m), catch height | assumption (override per player only with a sourced height) | illustrative |
| Fielder's start spot | typical spot for the named position (RH; mirrored for LH) | illustrative |
| How far a fielder moved | start spot to the commentary-implied catch spot (1.4 m moving, 2.4 m diving) | estimate, labelled |
| Keeper standing back | assumed for pace >= 120 kph | assumption, labelled |

## Situations (renders: `python3 pitchview_demo.py` -> deliver/_pitchview_mockups/v3/, from real balls of the 4th ODI)
| Situation | Status | Tested on | Notes |
|---|---|---|---|
| Bowled, lbw (bounce solved to the stumps; kept-low / extra bounce) | done | Kohli 0.5, Iyer 0.6 | Cricinfo vs Cricbuzz length disagreements are shown, not hidden |
| Caught: named position, exceptional (dive), keeper (standing back assumed) | done, animated | Rohit 0.1 (first slip), Finn Allen 30.2 (short cover, dive), Seifert 11.6 (keeper) | fielder's move is an estimate |
| Caught with no position named | partial | - | falls back to the wagon spot, marked approx. |
| Stumped | done | Kelly 14.2 (Axar, flight + drift, came down the track) | how far out of the crease is NOT in the data: drawn illustrative |
| Run out: direct hit by the bowler; throw from the deep | done | Henry (non-striker) 49.5; Fisher 49.6 | who was short and by how much is not in the data; the non-striker's name comes from out_id |
| Four / six (ball flight to the rope, sector named) | done | Young 13.4 (six), Seifert 2.2 (four) | rope radius approximate (65 m), wagon spot extended to the rope when it sits inside |
| Wide, no-ball (overstep foot), free hit | done | Jamieson 49.1 (wide), Kuldeep 25.4 (no-ball, also a four) | overstep distance is not in the data |
| Misfield / fumble | done (from commentary leads) | Iyer 24.6 at extra cover | |
| Dropped chance (Cricbuzz event DROPPED; dropper and position from the text) | done | Young 1.5 (Rohit), Axar 5.4 (Kelly at backward point) | 17 DROPPED events exist across the 9 Cricbuzz captures; only matches with a Cricinfo table can be drawn |
| Bouncer (commentary says so, or the model puts the ball above the shoulder) | done (tag + higher bounce) | Brar 11.3 to Young | height is the model's, not measured |
| Spin (loop, drift, slower, lower release) | done (basic) | Axar 14.2, Kuldeep 25.4 | turn after pitching is not modelled (direction is rarely in the text) |
| Seam in/away after pitching | done (small lateral move) | Henry over | |
| Swing before pitching (in / away, from the text) | done | Arshdeep 0.5, Young 1.5 | direction from commentary; size of the swing is illustrative |
| Bowler arm / angle (left-arm, round the wicket): the release point moves | done | Arshdeep 26.5 (round the wicket) | the bowler's arm is only known when the text says left-arm |
| Batter's-eye and keeper's-eye cameras | done (rough framing) | Kohli 0.5, Rohit 0.1 | |
| Over on one page (six landing spots, outcome, control) | done | Henry's first over | data only |
| Where the runs went (wagon plot, any slice: over, spell, innings, match) | done | Will Young's innings | data only; fours/sixes/wicket in red |
| Hit wicket, handled the ball, obstructing the field, timed out, retired | built, NOT tested on a real ball | none in our captures (smoke-tested only) | law numbers deliberately not shown (the MCC 2026 edition may renumber) |
| Field as the commentary describes it (one over) | done, sparse by nature | Henry's first over (2 positions named) | NOT a full field: only fielders the commentary mentions |
| DRS / ball-tracking (pitching, impact, hitting, umpire's call) | not planned | | no tracking data |
| Animation (orbiting camera: delivery, then catch / run-out throw / boundary flight) | done | catch (Allen 30.2), run out (49.5 direct hit), six (Young 13.4) | any situation with a ball path can be animated the same way |
| Free hit (the ball after a no-ball) | done | Seifert 1.3: six off the free hit | the table order decides it; balls bowled twice under one number are told apart (`nth`) |
| Run-out missed (Cricbuzz event RUNOUT_MISS) | done | Kohli's throw from mid off, 47.2 | |
| Review (UDRS): commentary notes only | done (no tracking picture) | Iyer 0.6 (three reds), Young 33.3 | we have no ball-tracking data |
| Leave (LEFT_ALONE: 54 in the two tables) | done | Allen | |
| Byes and leg byes | done | Seifert 9.1 (leg byes), Clarke 40.1 (byes) | |
| Caught and bowled | built, NOT tested | none in our captures | |
| Edges, body blows, beaten, milestones (50 / 100), maiden over | done as tags | various | from the commentary and Cricbuzz events (leads) |

## Known data gaps
- Cricbuzz and Cricinfo sometimes disagree on length (flagged on the poster) and on an event (Kuldeep 25.4: Cricinfo four + no-ball, Cricbuzz tags SIX): a CONFLICT until a third source settles it.
- Cricbuzz-only matches (1st, 2nd, 5th ODI and four U19 matches) have the commentary leads but no Cricinfo ball table: they cannot be drawn until their Cricinfo pages are captured.
- Speed is in about 4% of commentary lines (default 130 kph; 85 for spin).

## Checks before any of this is published
Every number goes through `dataops.verify` (two sources, or "in our archive"); the length disagreement on a ball is a CONFLICT until a third source settles it; commentary leads are paraphrased as facts, never quoted.
