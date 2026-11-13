# Third Man control room

Dashboard for The Third Man: today, editable tracker, channel stats, formats (rules, structure, sample frames), playbook, daily ideas, library with Drive links, data and rules. Brand theme (navy / cream / gold, Bebas Neue).

## Deploy on Vercel (one-time, about 10 minutes)
1. Vercel → Add New Project → import `knightfox1510/thethirdman`. Framework: Other, no build. `vercel.json` serves `site/` and the `api/` functions.
2. Storage: Project → Storage → add **Upstash Redis** (Marketplace). It sets `KV_REST_API_URL` and `KV_REST_API_TOKEN` automatically.
3. Environment variables (Settings → Environment Variables; never put these in the repo):
   - `SITE_PASSWORD`: the password you type on the site to edit the tracker and see stats.
   - `CRON_SECRET`: any long random string (lets the daily stats cron run).
   - `G_CLIENT_ID`, `G_CLIENT_SECRET`, `G_YT_TOKEN`: the same YouTube values the publisher uses.
4. Watch hours and retention need one more permission. Enable **YouTube Analytics API** in the Google Cloud project, then on your computer run `python3 publish/reauth_youtube.py`, sign in as the channel account, and paste the refresh token it prints into Vercel as `G_YT_TOKEN`. Redeploy.
5. Open the site, click **Locked**, enter the password. Stats → **Refresh now** pulls the first numbers; after that the cron pulls them daily at 06:00 IST.

Without steps 2–3 the site still works read-only from the files in `site/data/`.

## How the pieces work
- **Tracker**: stored in Upstash (`/api/schedule`). The first Save moves the schedule there, seeded from `schedule.json`. Edit on the site; **Export JSON** is the backup. Claude updates it with `python3 site_sync.py` (env `TTM_SITE_URL`, `TTM_SITE_KEY`).
- **Stats** (`/api/stats`, password-protected): subscribers, views, per-video numbers, progress to 4,000 / 8,000 watch hours and the Shorts route, results per format (long and Shorts kept apart; "too early" under 3 videos). Daily history gives the trend lines and pace.
- **Drive links**: `python3 drive_links.py` writes `data/drive.json`; Library shows the folder and files per video. Re-run after builds or uploads.
- **Video → format map**: `site_build.py` writes `data/video_map.json` from `publish/youtube_log.json`; stats use it to group by format.
- **Match-day alerts**: one-off scheduled tasks check after each India match and push to your phone; the list is `data/reminders.json`.

## Data in `site/data/`
- `formats.json`: formats, channel-wide rules, playbook (by hand).
- `schedule.json`: seed and read-only fallback for the tracker.
- `fixtures.json`, `ideas/`: written by the daily ideas task.
- `library.json`, `stills.json`, `replay_sample.json`, `video_map.json`: `python3 site_build.py`.
- `drive.json`: `python3 drive_links.py`. `reminders.json`: by hand.

## Local preview
`node dev_server.js` → http://localhost:8787 (password `dev`, in-memory storage, sample stats numbers).
