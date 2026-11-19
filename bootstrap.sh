#!/bin/bash
# Make a fresh checkout/session fully usable (idempotent). Needs the G_* env vars (Drive) and, for rebuilds, XI_KEY.
#   ./bootstrap.sh [<slug> ...]      restores raw captures, optionally the finished videos and narration cache for the given slugs
set -e
cd "$(dirname "$0")"
python3 publish/datasync.py pull raw                                   # owner captures, players, capture index
[ -d data/cricsheet/odis ] || python3 -m dataops.cricsheet fetch       # public Cricsheet archives (not backed up: re-downloaded)
for s in "$@"; do
  python3 publish/drive.py pull "$s"                                   # finished videos -> deliver/<slug>/
  python3 publish/datasync.py pull vo "$s"                             # cached narration -> out/<slug>/*/vo (saves ElevenLabs credits on rebuild)
done
echo "ready. Sportmonks IPL cache (needs SM_KEY): python3 fetch_ipl.py"
