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

## Situations
| Situation | Status | Notes |
|---|---|---|
| Bowled, lbw (bounce solved to hit the stumps; kept-low / extra bounce) | done (poster) | Cricinfo and Cricbuzz can disagree on length (Kohli 0.5: Short vs good length): shown, not hidden |
| Caught at slip / gully / point / cover / mid-off ... (named position) | done (poster, animation) | catch spot = start spot + the described move |
| Exceptional catch (dive, one hand, running) | done (animation of the move) | distance is an estimate; no player tracking exists in our data |
| Keeper catch (edge, top-edge) | done | wagon spot is where the SHOT went, so it is not used for keeper catches |
| Caught in the deep with no position named | partial | falls back to the wagon-wheel spot, marked "approx." |
| Stumped | todo | keeper's gloves + stumps break; needs how far the batter was out of the crease (not in data) |
| Run out | todo | throw path from the fielder's spot to the stumps; Cricinfo has dismissal code 4 (assumed), the fielder from the text |
| Hit wicket, obstructing, handled, timed out | todo | rare; text-driven |
| Boundary four / six (ball flight to the rope) | todo | wagon spot gives the direction; height unknown |
| Dropped catch, misfield, overthrow | todo | text leads ("dropped"); no tracking |
| Wide, no-ball, free hit, bouncer | todo | the pitch table has no wide/no-ball geometry; bouncers need height at the crease (model can do it) |
| Spin (turn, drift, flight) | todo | needs a spin parameter; the commentary gives turn words; the current bounce model is pace-only |
| Swing (conventional / reverse) and seam | partial | seam in/away is a small lateral move after pitching; swing before pitching not modelled |
| Left-arm, round the wicket, left-hand bat | partial | batter hand handled; bowler arm/angle not yet |
| DRS / ball-tracking (lbw: pitching, impact, hitting; umpire's call) | not planned for now | needs tracking data we do not have; the text only says "umpire's call" |
| Batter's-eye view (balls faced as dots by control; shot arrows) | todo | all data exists in the table |
| Keeper-eye view, captain's field-placement view | todo | positions from text and Cricbuzz field-change notes |
| Partnership / over / spell sequences (six balls in one scene) | todo | the model is per ball; sequencing is a layout job |

## Checks before any of this is published
Every number goes through `dataops.verify` (two sources, or "in our archive"); the length disagreement on a ball is a CONFLICT until a third source settles it; commentary leads are paraphrased as facts, never quoted.
