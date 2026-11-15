# Session handoff (15 Nov 2026)

Branch: `claude/youtube-shorts-upload-tracker-1vhadp` (everything committed and pushed; no open PR).

## State
- Replay Room Ep 3 (`replay_5odi`) and Data Stories Ep 12 (`data_nz_ind_series`, India v NZ ODI series 2026): built, uploaded to YouTube as PRIVATE (long + Short each), tracker rows Posted, Drive synced. IG Short, IG Reel (avatar) and IG Lab Reel (`variants.py iglab`) are on Drive for manual posting.
- Links: 5th ODI long https://youtu.be/9Iu25SLhXGg, Short https://youtu.be/Ty2LP-UQV1c; series long https://youtu.be/UAlk7dwMfjw, Short https://youtu.be/SLTOXJ6CQqw. Owner still needs to publish them from Studio.
- On hold: Gambhir "Player vs Coach" (gate blocks it: coach record needs a second source). Did You Know Ep 2 (fielding positions) still to be redone in the plate look with an explanatory Short.

## Not in git (gitignored): rebuild or pull
- `deliver/`, `out/`: rendered files. Pull from Drive: `python3 publish/drive.py pull <slug>`. Rebuild: `python3 engine.py build specs/<slug>.json both` (~10-15 min, XI_KEY needed; narration is re-synthesised).
- `data/cricsheet`, `data/models`, raw `data/cricbuzz|cricinfo` captures: re-download Cricsheet (men's ODIs/T20Is/tests zips) into a dir and set `CS_DIR`; make_*.py generators read the tracked analysis outputs in `data/series/nz_ind_2026/` and `data/provenance/`.
- Secrets: env vars only (XI_KEY, SM_KEY, G_CLIENT_ID, G_CLIENT_SECRET, G_DRIVE_TOKEN, G_YT_TOKEN). Never write them to files.

## Known caveats
- Win probability is our model (Cricsheet 50-over ODIs); say "our model". Matches 1-2 were DLS decisions.
- Drop counts and runs-after-drops are single-source (Cricbuzz-derived): labelled "in our archive".
- `batch.sh` has a wrong path here; call `python3 engine.py build ...` directly.
- IG end line: set `reel_cta` per spec (generic default now; Aaryavir specs carry their own).
