# The Third Man: working rules

A faceless cricket channel ("Cricket from a different angle"). Every video is a JSON spec in `specs/`; `engine.py` renders it. See README.md for setup, commands and the spec schema, and CATALOG.md for the index of every video.

## Secrets
- API keys come ONLY from env vars: `XI_KEY` (ElevenLabs), `SM_KEY` (Sportmonks), and for publishing `G_CLIENT_ID`, `G_CLIENT_SECRET`, `G_DRIVE_TOKEN`, `G_YT_TOKEN`. Never write them into any file, spec, commit or log (publish/gauth.py also reads a RAM-only /dev/shm file during a session).
- Upload to YouTube only when the user asks. Drive sync (publish/drive.py) runs after every build.

## Voice (ElevenLabs "Ruhaan", eleven_multilingual_v2)
- Write Indian player names in Devanagari in `vo` (e.g. अभिषेक शर्मा). Add each new name to `SHOW` in engine.py so captions show English.
- Write for the ear: short sentences, and a comma wherever a narrator would breathe. The build warns about 15+ words without punctuation. Pauses come from punctuation: breathe() in engine.py guarantees a pause at every . ? ! : ; , and scene gaps follow how the paragraph ends.
- Spell years and most numbers out in words ("twenty twenty-six", "one fifty-seven"). Digits are misread, especially after Devanagari.

## Content
- Facts must be current: check the web for anything that can change (squads, trades, records, results).
- Every spec carries `sources[]`. Data claims cite the Sportmonks ball-by-ball cache and how they were filtered.
- No broadcast footage, player photos, or team/league logos. Label illustrative visuals (e.g. field plans).
- The Sportmonks plan covers IPL 2013-2026 plus T20Is/T20 World Cups. It has NO men's ODIs or Tests, so take those numbers from the web.

## Workflow
- Content schedule (what's posted, what's next, library, ideas): the Sheets artifact https://claude.ai/artifact/W2S945TTf7fCL2htKDMfLy. Read it through the Claude Docs connector, and update Status/Link there after every upload.
- Drive: The Third Man/Videos/<slug> = not yet posted; Published_YT/<slug> = posted (youtube.py moves it); Archive/ = replaced versions.
- Instagram is posted by hand: Reels = the Short files; carousels in deliver/<slug>/carousel with caption.txt.
- Adjust one video: edit its spec, then `./batch.sh <slug>` (narration is cached per paragraph, so only changed lines hit the API).
- Global look changes: edit engine.py/gfx.py/intros.py, then re-render with batch.sh.
- Before a full build, check `python3 engine.py stills specs/<slug>.json long|short`.
- Run builds in the background with XI_KEY set; batch.sh prints OK/FAIL per slug.
- After adding videos, run `python3 catalog.py` and commit the spec, CATALOG.md and intro_log.json.
- Data: `SM_KEY=... python3 fetch_ipl.py` downloads the IPL ball-by-ball cache into data/. stats.py builds the ball table (super overs are innings S3/S4; exclude them).

## Production defaults (every new video; use each where it fits the story)
- Hook: a number or the key claim on screen within 2 seconds. No slow title card first.
- Shorts use the stadium-stage look: theme "stadium", captions "v2", "stage" scenes with the illustrated player (no likeness of anyone real).
- Pick a pose for each beat: walk (entrance), stance, drive, pull, run, bowl, celebrate, raise (milestone), dejected (failure), stand.
- Put the opponent in the frame on "versus" beats: a second avatar in their kit (e.g. NZ for a semi against New Zealand).
- Show the ball when a moment is about a shot: "ball": {"word": ..., "shot": six|four}, with "hit" on the batter. Use a side view ("view": "side") for shots.
- Vary the camera from scene to scene: "cam" wide / push / pull / close / drift, and switch between end-on and side-on views.
- Vary the venue for each video: "venue" {"time": night|day|dusk, "crowd": fan colours, "boards": [c1, c2]}; match it to the real ground and time where known.
- Sound effects come from sfx.py (synthesised): whoosh on panels, crack + crowd on shots, crowd on big numbers and celebrations, stamp on verdicts. Add extra cues with "sfx": [{"kind", "at"|"word"}].
- Series verdicts use the "verdict" panel stamp (busted / half / confirmed), so the series has a recognisable sign-off.

## Series looks (pick one per video; variety comes from rotating series, the brand stays constant)
- Myth or Data? - theme "stadium", captions "v2", stage scenes, verdict stamp.
- The Lab / Stat Check - theme "lab", captions "lab": editorial paper, round tabs, lab_dots / lab_swarm / lab_units / lab_vs / lab_big / lab_big_text / lab_radial / lab_rings / lab_score / lab_compare. Model-driven stories (nearest-neighbour twins, head-to-heads in rounds with a scorecard). Generate the spec from the analysis (make_lab_twin.py, make_bumrah_rashid.py) and assert every claim in code.
- Tactics Board - "board" scenes (tilted field, pucks, zones, ball paths; tone navy|cream) mixed with Lab charts; captions "serif". Label fields "Illustrative".
- What If? - stadium-stage scenes with "film": true (sepia film), opening "clipping" (illustrative newspaper-style cutting, no real masthead); the last content scene is back in colour. Captions "serif".
- Rising Star - theme "card": a trading card that flips (front: illustrated player, back: verified numbers), then stage scenes.
- Flip - the benchmark flip format (flips.py).
make_series.py re-homes classic Shorts into a series (originals stay in short_classic).

## Accuracy lessons
- Sportmonks bowled dismissals have no out_id, and non-striker run-outs are not striker_out: count a batter's dismissals as (out_id == batter) or (out_id missing and striker_out). See analysis/lab_twin.py.
- Cricsheet T20Is are incomplete for some players (e.g. Kohli: 112 of 117 innings, missing his 122*). Never present Cricsheet sums as career totals; check against the official record first.
- Cross-check headline numbers with an official source (IPL Orange Cap table, team sites) before building, and note any you can't reconcile (e.g. one Rashid wicket) by avoiding that figure.
- Monetization: YPP entry doubles for new applicants from 1 Feb 2027 (8,000 watch hours or 20M Shorts views in 90 days); current partners are grandfathered. Prioritise long-form watch time before then; Shorts feed subscribers.
