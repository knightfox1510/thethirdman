# Did You Know? : series plan and backlog

**What it is:** one surprising or misunderstood thing about cricket per video. Short answer first, then the Law, then a drawn example, then the twist. Evergreen, searchable ("can a batter be out for ...", "what is a silly mid-off"), and topical when the thing happens in a match.
**Format:** Short 40-75 s (main), IG version as usual; occasional 3-4 min long by theme. Hook: the question on screen in 2 seconds. Series colour lime, theme stadium, field plans from the Tactics Board (labelled Illustrative).

## Accuracy workflow (rules are the one thing we cannot get wrong)
1. Find the Law in the MCC Laws of Cricket (current code) and, for format rules, the ICC Playing Conditions (Test / ODI / T20I). Two sources agree, or we do not publish.
2. Write the claim with its Law number and format/version in the spec's `sources[]` and the YouTube description ("Law 41.16 (non-striker out of his ground)").
3. Where rules differ by format or changed recently, the video says which version it describes.
4. Real incidents ("it happened once in ...") are only used with a Tier A source; never "first / only / never" from memory.
5. Run through `dataops/verify.py` Claims like any other number (source names: `mcc_laws`, `icc_playing_conditions`).

## Backlog (topics only: each is verified against the Laws before it is written)
**Dismissals nobody expects:** handled the ball; obstructing the field; timed out; hit the ball twice; hit wicket; run out of the non-striker (the Mankad, Law 41.16); retired out vs retired hurt; can a batter be out off a no-ball (run out only); caught off a fielder's helmet; can you be out off a free hit; stumped vs run out when the keeper is involved.
**Extras and umpire calls:** every kind of no-ball (front foot, height, fielders, bowler's action); free hits; what makes a wide (and the leg-side wide); byes vs leg byes; penalty runs (5 for the ball hitting a helmet on the ground); dead ball; umpire's call in DRS and why it exists; soft signal (gone); the lbw checklist (pitching, impact, hitting).
**Positions and fielding:** every fielding position explained (slip cordon, gully, point, cover, mid-off, mid-on, mid-wicket, square leg, fine leg, third man, silly point, short leg, sweeper); why it is called "third man" (and where the channel's name comes from); fielding restrictions and powerplays by format; where can the wicketkeeper stand; how many fielders behind square on the leg side (Law 28.4); substitute fielders and what they cannot do; the concussion substitute and the IPL Impact Player.
**Match rules:** follow-on; declaration; tie vs draw; the super over (and what if that ties); DLS in plain words; how many overs make a match; minimum overs for a result; reserve days; over rates and the stop clock; why a Test has a new ball after 80 overs (and why it used to be 6 or 8 balls an over).
**Equipment and the ball:** why the ball is red, white or pink; seam and swing; the bat's size limits; stump height and bail weight; what is the pitch strip; can a batter use a left-hander's stance mid-over (switch hit); can a bowler change arm (declare it); can a fielder use a cap/hat to stop the ball (penalty).
**Oddities and history:** what happens if the ball hits a bird; ball lost in the stands; ball hits a spidercam; two balls in play (never); the longest over; a 36-ball over; the over of 6 wickets; why the Ashes are called that. (Each needs a Tier A source.)

## First five to build (recommended)
1. "Can a batter be out for handling the ball?" (a rarely-seen Law, clear drawn example)
2. "What is a Mankad? Is it legal?" (Law 41.16, hot topic, search volume)
3. "Why is it called third man?" (ties to the channel's name; fielding positions plan)
4. "What is the free hit rule?" (no-ball + dismissals that still count)
5. "How does DLS work in 40 seconds?" (high search volume; needs careful two-source checking)

## Production notes
- Register each episode in `publish/series.py` (series id `didyouknow`) before the first build. File names: `Did_You_Know_Ep01_<Subject>_Short_9x16`.
- Title pattern: `<Question>? | Did You Know Ep 3 #Shorts`.
- Scenes: stage + "board" (field plan) + verdict-style "YES / NO / IT DEPENDS" panel. Add a Law-number stamp panel as a new `law` panel kind when the first episode is built.

## More topic areas (added Nov 2026)
**Batting shots:** every shot and what it is for (forward defence, back foot defence, drive: straight, cover, off, on; cut and square cut; pull and hook; sweep, paddle, reverse sweep; flick and glance; late cut and upper cut; slog sweep; scoop, ramp, dilscoop; switch hit; helicopter shot; the leave); where each shot sends the ball (wagon wheel zones); which shots go with which length; "playing and missing" vs "edge"; the stance, the grip, the backlift; the bat's anatomy (sweet spot, edge, toe, shoulder).
**Ball types and deliveries:** the seam and why it matters; seam position on the delivery (upright, scrambled, angled) and what each does (swing, seam, nothing); conventional vs reverse swing; outswinger and inswinger; leg cutter and off cutter; yorker, full toss, half-volley, good length, short of a length, bouncer, beamer (illegal) ; slower ball, knuckle ball, back-of-the-hand slower; slower bouncer; wide yorker; round the wicket vs over the wicket (angles, and the lbw effect); spin: off spin, leg spin, left-arm orthodox, chinaman, googly/wrong'un, doosra, carrom ball, flipper, top-spinner, arm ball; what the ball's wear does (why it swings later, why the white ball swings early); how pace is measured; grip: how each delivery is held.
**Bowling:** run-up and the delivery stride; front-foot no-ball line; the action legal limit (15 degrees of elbow extension) and how it is tested; bowling restrictions (overs per bowler by format, a bowler cannot bowl two overs in a row); the bouncer limit per over by format; bowling round the wicket; protected area on the pitch and the warning rule; ball tampering (what is and is not allowed: shining, saliva rules).
**Fielding:** close catching, the slip catching technique, the throw-in and the flat throw, the sliding stop, the relay; "saving one" and "saving two"; boundary catches and the Law on fielders touching the rope (the rule changed: the catch must be completed within the boundary); where fielders can legally stand (no one on the pitch, no more than two behind square on the leg side) ; substitute fielders; sweeper and cow corner; why the positions mirror for left-handers.
**Wicket-keeping:** standing up vs standing back; the keeper's gloves and pads (what is allowed); the stumping and the leg-side stumping; keeper's catches and byes; the long stop (obsolete); why keepers wear different gloves; what a keeper cannot do (collect the ball in front of the stumps before it passes, with exceptions).
**Umpiring:** the signals (every one of them: four, six, wide, no-ball, bye, leg bye, dead ball, out, short run, penalty, revoke, new ball); the third umpire and what the TV umpire checks first (the no-ball); what an umpire's call means; bad light and light meters; the covers and when play stops; the umpire's counting stones/pebbles, and who holds the bowler's belongings; the match referee's role; the toss and the coin: who calls it and what the choice means; the stump mic and the snickometer: what they show.
**The ground:** the pitch dimensions (22 yards, the crease markings), the boundary rope and the 30-yard circle, the sightscreen, the sight screen's white/black side, the roller, the covers, the stumps and bails (and the "zing bails" tech), the over-rate clock, spidercam and the Law on it.
