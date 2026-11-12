# The Third Man – video engine

Spec-driven renderer for The Third Man cricket channel: long-form 16:9 videos, 9:16 Shorts/Reels,
on-screen text graphics, .srt subtitles for both formats (burned-in Short captions are opt-in: "burn_captions": true), rotating animated intros, a logo outro, YouTube thumbnails and Short covers.

## Setup (once per session)
```
bash setup.sh                       # pip installs skia-python, numpy, scipy, fonttools, pillow; checks ffmpeg
export XI_KEY=<ElevenLabs API key>  # voice (Ruhaan, eleven_multilingual_v2)
export SM_KEY=<Sportmonks key>      # optional: cricket ball-by-ball data (sm.py)
```
The network allowlist must include api.elevenlabs.io (and cricket.sportmonks.com for data).

## Make a video
1. Write `specs/<slug>.json` (see the schema below and any existing spec).
2. `python3 engine.py voice specs/<slug>.json` – generates narration (cached per paragraph).
3. `python3 engine.py stills specs/<slug>.json long` (and `short`) – preview sheet at `out/<slug>/<fmt>/sheet.jpg`.
4. `./batch.sh <slug> [<slug> ...]` – full build. Results in `deliver/<slug>/`:
   long .mp4 + .srt + thumbnail, Short .mp4 + cover.

## Spec schema
```
{ "slug": "...", "theme": "whites|blue|scoreboard|floodlights", "intro": optional fieldmap|stumps|flip|kinetic,
  "tag": "SERIES TAG", "tagsub": "VIDEO SUBTITLE",
  "files": {"long": "File_Name", "short": "File_Name_Short_9x16"},
  "thumb": {"kicker": "...", "lines": [{"t": "LINE"}, {"t": "LINE", "c": "gold"}], "hero": "146", "herosize": 520},
  "long":  [ {"vo": "narration paragraph", "scene": {...}}, ... ],
  "short": [ ... ] }
```
Scene types (colors: ink, gold, blue, red, orange, muted – mapped per theme):
- `statement` / `title`: kicker, lines[{t,c}], sub
- `bignum`: value, dec, prefix, suffix, from, label, note, color
- `bars`: head, items[{label,value,color,text}], max, dec, unit, note
- `compare`: head, a{name,color,sub}, b{...}, rows[[label, a, b, "a"|"b"]]
- `list`: head, items[{h,d,c}]
- `timeline`: head, events[{y,t,hl,c}]
- `stats`: head, tiles[{v,l,c}]
- `scorecard`: head, teams[{name,color,gain[],lose[]}]
- `line`: series[{name,color,points[[x,y]]}], ymin, ymax, xticks, yticks
- `gauge`: value, min, max, marks[{v,l,c}]
- `over`: balls[{r,n,c}]  (an imagined over)
- `swap`: left/right {name, role, from, to, color}  (trades)
- `fieldplan`: fielders[], hl[], length{from,to,label,c}, shots[{to,label,c,lift,bend}], lines, sub, lefty (mirror for a left-handed batter)
- `trajectory`: side-on pitch view. balls[{length (m from batter's stumps), label, c, loop, end, at, dur}], hl[] (length zones),
  speed, note, bowler_pose, bowler_c, batter_c
- `matchup`: two original figures face to face. left/right {name, pose, team|color, sub}, rows[[label, left, right]]
- `cta`: lines, pill, ask
Team colours: any color can be "team:RCB" (or a bare team code); bars items and compare/matchup sides accept "team": "MI"
for a coloured code chip. Codes: CSK MI RCB KKR SRH DC PBKS RR GT LSG IND NZ AUS ENG PAK SA SL WI AFG BAN (no logos).
Figure poses: stance, drive, pull, defend, release (pace), spin, keeper.
Any item may carry "at" (0–1 of the scene) but items auto-sync to the narration word that matches their label.

## Stadium stage (Shorts default)
Spec level: `"theme": "stadium"`, `"captions": "v2"`, `"venue": {"time": "night|day|dusk", "crowd": [[r,g,b], ...], "boards": [[r,g,b], [r,g,b]]}`.
Keep a different look for the long version with `"theme_long"`.
A `stage` scene:
```json
{"type": "stage", "cam": "wide|push|pull|close|drift", "view": "end|side", "stumps": [0.2, 0.92],
 "panel": {"kind": "headline|bignum|versus|score|table|verdict", "at": 0.05, "kicker": "..."},
 "avatars": [{"kit": "IND", "number": 18, "pose": "stance", "hit": "pull", "x": 0.36, "x2": 0.5, "dir": 1, "scale": 1, "cap": false, "pads": true}],
 "ball": {"word": "owns", "shot": "six|four|bowled", "side": -1, "color": "white|red"},
 "sfx": [{"kind": "crowd|crack|whoosh|stamp|bounce", "at": 0.5}]}
```
- Poses: front `stand walk celebrate raise dejected`; side-on `stance drive pull run bowl` (`dir: -1` mirrors).
- `kit` is a team code from TEAMS or an [r, g, b] colour (e.g. cream Test whites). `cap: true` gives a cap with no helmet or pads (bowlers, fielders).
- `ball` is timed to a spoken word (or `at`, a fraction of the scene). The first avatar plays the shot, switching to its `hit` pose on contact.
- Panels: `verdict` is the Myth or Data? stamp (`"verdict": "busted|half|confirmed"`).
- Sound effects are automatic for stage scenes (sfx.py synthesises them; no samples): whoosh on panels, crack + crowd on shots, crowd on big numbers, stamp on verdicts.
- `make_stage_shorts.py` converts a classic Short to this look. The old version stays in `short_classic`.

## Instagram extras
- `python3 variants.py deepcut specs/<slug>.json`: a 90-150 s vertical "deep cut" Reel from the spec's `ig` scenes
  (file name from `files.ig`), ending with a "full breakdown on YouTube" CTA.
- `python3 variants.py carousel specs/<slug>.json`: 4:5 carousel slides (cover, scenes listed in `carousel.slides`, CTA)
  plus `caption.txt`, written to `deliver/<slug>/carousel/`.

## Flip Shorts (no narration)
`python3 flips.py specs/flip_<slug>.json`: a benchmark vs challengers at the same point in their careers, hard cuts on a
synthesised beat (100 bpm, a panel every two beats), team colours, silhouettes, one giant number per panel.
Specs are generated from data by `make_flips.py` (figures in `analysis/flips.py`). IPL captains come from Sportmonks line-ups
(`fetch_lineups.py` caches them); Tests and T20Is come from Cricsheet (data/cricsheet/{test,t20i}).

## Analysis
`analysis/<slug>.py` prints every Sportmonks-derived figure used in that video's spec (conventions in analysis/common.py).
Run it after a data refresh and update the spec if anything moved.

## Rules baked in
- Indian names in Devanagari inside "vo" (correct pronunciation); captions map them back (SHOW dict in engine.py).
- Spell years out in words in "vo".
- Long videos: hook scene → rotating 3.2s intro → content → logo outro. Shorts: no intro.
- Intro rotation: least-recently-used, never twice in a row, Scoreboard prefers flip; assignments in intro_log.json.
- No broadcast footage, no player photos, no team/league logos – original graphics only.

## Publishing (Google Drive + YouTube)
Credentials only via env vars (never commit them): `G_CLIENT_ID`, `G_CLIENT_SECRET`, `G_DRIVE_TOKEN`, `G_YT_TOKEN`
(refresh tokens from the one-time sign-in; Drive and YouTube need separate sign-ins because Google won't combine those scopes).
- `python3 publish/drive.py <slug>|all`: syncs `deliver/<slug>/` to Drive `The Third Man/Videos/<slug>/`. Changed files
  replace the old ones and the old ones move to `The Third Man/Archive/<slug>/<date time>/`. Unchanged files are skipped (MD5).
- `python3 publish/youtube.py <slug> long|short [--publish-at ISO]`: uploads with title/description/tags from the spec's
  `yt` block (`{"yt": {"long": {"title","description","tags"}, "short": {...}}}`), sets the thumbnail for long-form and uploads
  captions for both formats, and logs the video ID in `publish/youtube_log.json`. Until the API audit passes, YouTube forces uploads to
  private, so publish them in YouTube Studio. Quota: about 6 uploads a day.
