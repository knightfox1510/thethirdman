# Third Man match capture (Chrome extension)

Saves the data of a Cricinfo or Cricbuzz match page **you have open** as one JSON file. It reads what the page itself loads; it makes no requests of its own and does nothing on other sites.

## Install (once)
1. Unzip `ttm-capture.zip` somewhere permanent.
2. Chrome → `chrome://extensions` → turn on **Developer mode** (top right) → **Load unpacked** → pick the unzipped folder.

## Capture a match (after it ends)
1. Open the match's **ball-by-ball commentary** tab. A "Third Man capture" panel appears bottom-right.
2. Click **Load all commentary** and wait until the ball count stops rising. Switch to the other innings in the commentary and do it again.
3. Open the **scorecard** and **match statistics** tabs once each (same browser tab is fine).
4. Back on any tab of that match, click **Save JSON**. A file `cricinfo_<id>_<match>.json` downloads.
5. Send that file to Claude (attach it in the chat).

Expect ~600 balls for a full ODI. If the count is far lower, scroll the commentary manually to the first ball of each innings and save again.

## Cricbuzz
Same steps on the match's **Full Commentary** page (cricbuzz.com/live-cricket-full-commentary/<id>/...): click **Load all commentary** (it also presses Cricbuzz's "load more"), switch innings and repeat, open the Scorecard tab, then **Save JSON** (file: `cricbuzz_<id>_<match>.json`). Cricbuzz adds the editorial notes between overs (stats, milestones); we use those as leads to verify, not text to copy.

Tip: stay in one browser tab per match; the capture is kept while you move between that match's tabs.

## On our side
`python3 cricinfo_import.py data/cricinfo/<file>.json` builds the ball table and prints which fields were found (runs, wickets, and where present wagon-wheel / line / length / shot / control), with innings totals to check against the official scorecard.

## Use of the data
Use the numbers for our own analysis and our own graphics. Do not copy Cricinfo's commentary text, charts or images into videos, and cross-check headline figures with the official scorecard (BCCI / NZC). Credit "ball-by-ball data: ESPNcricinfo" in the description sources.


## Batch and crawl mode (v1.5)
v1.5: a series page is read from the page's own data (the exact list of that series' matches; the page's "trending matches" box and "view full list" records links are ignored), including old trophies whose matches belong to a different tour series. Old matches that have no commentary, or no playing-XI / statistics page, are still captured: the missing tabs are skipped, the scorecard and players are saved, and the log says so. A missing tab never discards the match. Items marked done by older versions are re-done once.

Panel layout: a status chip (IDLE / RUNNING / STOPPED), what it is doing now, a progress bar (queue position), counts (queue left, this run, done ever), your link list, **Start / Resume** and **Stop**, **Add links from this page** and **Clear queue**, a collapsible Options box (max per run, from year, also save series/list pages, Save this page, Import known ids, Forget done) and an Activity log. **Stop is immediate** (it cancels the pending wait and navigation); **Clear queue** stops and empties the list. **Only the right links are collected:** from the page's main content only (never the header, menus, side panels or "recent / live / trending matches" widgets), and on a series page only matches of that series (their address must contain the series). A page that yields more than 150 links is not queued (the layout probably changed); the log shows examples of what it found. One .json file is downloaded per match (series / list pages are only saved if you tick the option). Upcoming and live matches are skipped and nothing is saved for them. Text is light on dark everywhere.

A second panel (bottom-left, "Third Man batch") works through a queue of links in your own tab at a human pace (random 4-25 s pauses, cap per run, never parallel). It recognises each link:
- **Match:** opens the scorecard, **playing XI** (squad / bench / roles when the site has them), ball-by-ball commentary (skipped for old matches that have none) and statistics, and downloads one `cricinfo_<id>_<match>.json`.
- **Series page:** collects the match links on it (fixtures and results) and queues the ones not yet captured.
- **A team's season / results list** (e.g. `https://www.cricinfo.com/ci/engine/series/index.html?search=india;view=season`): collects every series link on it and queues them. Set **from year** to limit how far back to go. Series then queue their matches. So one link can build a whole team's history; it runs over several sessions (press Start again, the queue and progress are kept).
- **Any other page** (a player's stats page such as `.../cricketers/abhishek-sharma-1070183/bowling-batting-stats`, a records table): saved as `page_*.json` with its tables and page data, and with every format tab / filter clicked through (Tests, ODIs, T20Is, IPL ...).
- **Queue links on this page / Save this page** do the same manually.
- **Never captured twice:** finished matches and series are remembered in the browser; **Import known ids** seeds it with what the repo already holds (`python3 -m dataops.store known`, paste the output); a match is only re-done if it was captured live / incomplete or with an older capture version. In the repo, `python3 -m dataops.ingest <downloads folder>` keeps one file per match and replaces it only with a more complete capture; `python3 -m dataops.store missing` lists the incomplete ones.
- **Stops by itself** on a captcha / access-denied page (solve it, press Start) and when you press Stop. Matches that were still live are never marked done.
- Rough pace: about 1-1.5 minutes per match, so 300 matches is several hours over a few sessions. Old matches (pre-2000s) have a scorecard and no ball-by-ball and are quicker.
- Not tested against the live sites from our side (they block our servers). Run 3 matches first, ingest them, and check `python3 -m dataops.matchdata --all` for what each capture holds. If a tab name changed, fix `TABS` at the top of batch.js.
- Same rules as before: your own browser, our own analysis and graphics, no republishing of their text or images. The sites' terms restrict automated collection: keep runs small and paced.


## Unattended runs: auto-resume and keep-awake (v1.6)
Open **Options** in the batch panel:
- **Auto-resume** (off by default): after the *max matches per run* limit the run rests for **Rest between runs** minutes (default 20, randomised a little) and then carries on by itself, so a long queue works through the night. After a captcha / "access denied" page it waits 20, then 45, then 90 minutes and tries that page again; if it is still blocked it stops and waits for you (solve the check, press Resume). A page that will not load in 2 minutes is retried 3 times; an unexpected error is retried up to 5 times. The pause is saved, so reloading the tab does not lose it; the panel chip shows RESTING with the time left. Stop and Clear queue cancel a pause at once. The settings take effect immediately, even mid-run.
- **Keep this computer awake while running** (on by default): `background.js` asks Chrome (`chrome.power`) to keep the system from sleeping while the batch is RUNNING or RESTING; the screen may still turn off. It lets go within 4 minutes if the tab stops reporting (tab closed, run stopped, queue finished).
- It cannot beat everything: **a laptop with the lid closed usually sleeps anyway**, and so does one that runs out of battery. Keep it plugged in with the lid open (or set the lid action to "do nothing"), leave the capture in its own window (minimised or hidden tabs are throttled, and Chrome's Memory Saver can discard an idle tab: add these sites to its exceptions). On a Mac, `caffeinate -dimsu` in Terminal holds the whole machine awake until you press Ctrl-C; on Windows, PowerToys "Awake" does the same.
- Please keep runs modest: the sites' terms restrict automated collection. Auto-resume keeps the human pace (random pauses, never parallel) and backs off when the site pushes back; it does not try to get round a captcha.

### Updating from v1.5 without losing the queue
The queue, the done-list and the settings live in the extension's own browser storage, which belongs to the folder it was loaded from. So: **do not reload the extension in the middle of a run** (Stop first, or wait until it finishes); copy the new files over the **same folder**, then press the reload arrow on `chrome://extensions`. Loading the new version from a different folder gives it a different id and an empty queue. The new manifest adds the `power` and `alarms` permissions and a background worker (`background.js`).
