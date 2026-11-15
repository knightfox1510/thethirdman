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
| Dropped chance | built, NOT tested | no example in the captured commentary | needs a match whose text says a catch was put down |
| Bouncer (height above the shoulder at the crease) | built (tag), NOT tested | none of the six short balls checked reached shoulder height at the model's speed | |
| Spin (loop, drift, slower, lower release) | done (basic) | Axar 14.2, Kuldeep 25.4 | turn after pitching is not modelled (direction is rarely in the text) |
| Seam in/away after pitching | done (small lateral move) | Henry over | |
| Swing before pitching (conventional / reverse) | NOT built | | text cues exist ("swing"); needs a lateral arc in the pre-bounce phase |
| Bowler arm / angle (left-arm, round the wicket) | tag only | | release point is not moved yet |
| Batter's-eye and keeper's-eye cameras | done (rough framing) | Kohli 0.5, Rohit 0.1 | |
| Over on one page (six landing spots, outcome, control) | done | Henry's first over | data only |
| Where the runs went (wagon plot, any slice: over, spell, innings, match) | done | Will Young's innings | data only; fours/sixes/wicket in red |
| Hit wicket, obstructing the field, handled the ball, timed out | NOT built | no examples in the captures | rare; text-driven |
| Captain's field-placement view (the whole field at a moment) | NOT built | | positions are only known for the fielders the commentary names |
| DRS / ball-tracking (pitching, impact, hitting, umpire's call) | not planned | | no tracking data |
| Animation | catch only | Finn Allen 30.2 | the others are still posters; the same path code can animate them |

## Checks before any of this is published
Every number goes through `dataops.verify` (two sources, or "in our archive"); the length disagreement on a ball is a CONFLICT until a third source settles it; commentary leads are paraphrased as facts, never quoted.
