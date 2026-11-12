# The Third Man: working rules

A faceless cricket channel ("Cricket from a different angle"). Every video is a JSON spec in `specs/`; `engine.py` renders it. See README.md for setup, commands and the spec schema, and CATALOG.md for the index of every video.

## Secrets
- API keys come ONLY from env vars: `XI_KEY` (ElevenLabs), `SM_KEY` (Sportmonks), and for publishing `G_CLIENT_ID`, `G_CLIENT_SECRET`, `G_DRIVE_TOKEN`, `G_YT_TOKEN`. Never write them into any file, spec, commit or log (publish/gauth.py also reads a RAM-only /dev/shm file during a session).
- Upload to YouTube only when the user asks. Drive sync (publish/drive.py) runs after every build.

## Voice (ElevenLabs "Ruhaan", eleven_multilingual_v2)
- Write Indian player names in Devanagari in `vo` (e.g. अभिषेक शर्मा). Add each new name to `SHOW` in engine.py so captions show English.
- Spell years and most numbers out in words ("twenty twenty-six", "one fifty-seven"). Digits are misread, especially after Devanagari.

## Content
- Facts must be current: check the web for anything that can change (squads, trades, records, results).
- Every spec carries `sources[]`. Data claims cite the Sportmonks ball-by-ball cache and how they were filtered.
- No broadcast footage, player photos, or team/league logos. Label illustrative visuals (e.g. field plans).
- The Sportmonks plan covers IPL 2013-2026 plus T20Is/T20 World Cups. It has NO men's ODIs or Tests, so take those numbers from the web.

## Workflow
- Adjust one video: edit its spec, then `./batch.sh <slug>` (narration is cached per paragraph, so only changed lines hit the API).
- Global look changes: edit engine.py/gfx.py/intros.py, then re-render with batch.sh.
- Before a full build, check `python3 engine.py stills specs/<slug>.json long|short`.
- Run builds in the background with XI_KEY set; batch.sh prints OK/FAIL per slug.
- After adding videos, run `python3 catalog.py` and commit the spec, CATALOG.md and intro_log.json.
- Data: `SM_KEY=... python3 fetch_ipl.py` downloads the IPL ball-by-ball cache into data/. stats.py builds the ball table (super overs are innings S3/S4; exclude them).
