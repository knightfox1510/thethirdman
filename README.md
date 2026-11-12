# The Third Man – video engine

Spec-driven renderer for The Third Man cricket channel: long-form 16:9 videos, 9:16 Shorts/Reels,
word-synced captions, .srt subtitles, rotating animated intros, a logo outro, YouTube thumbnails and Short covers.

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
- `fieldplan`: fielders[], hl[], length{from,to,label,c}, shots[{to,label,c,lift,bend}], lines, sub
- `cta`: lines, pill, ask
Any item may carry "at" (0–1 of the scene) but items auto-sync to the narration word that matches their label.

## Rules baked in
- Indian names in Devanagari inside "vo" (correct pronunciation); captions map them back (SHOW dict in engine.py).
- Spell years out in words in "vo".
- Long videos: hook scene → rotating 3.2s intro → content → logo outro. Shorts: no intro.
- Intro rotation: least-recently-used, never twice in a row, Scoreboard prefers flip; assignments in intro_log.json.
- No broadcast footage, no player photos, no team/league logos – original graphics only.
