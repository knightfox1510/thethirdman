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


## v1.6.1: commentary that did not load, and balls that were lost (Nov 2026)
- **Why it stopped at 20-40 balls:** the old loader jumped to the very bottom of the page each time. Cricinfo loads the next batch when the END OF THE COMMENTARY LIST scrolls into view (it sits just above the "sponsored" feed), so jumping past it loaded nothing. The loader now finds the last commentary item (an over.ball label such as 12.3), brings it to the middle of the window, nudges down and up in small steps, wiggles further when stuck, clicks a "load more" button only if it is not inside an ad block, and never scrolls into the ads. Tested on a local page that behaves this way: the old loader stalled at 20 of 240 balls, the new one loads all 240.
- **Why a match saved "0 balls":** the capture was kept in `sessionStorage` (about 5 MB, silently refuses a write when full, and belongs to ONE web address, so a hop between `www.cricinfo.com` and `www.espncricinfo.com` starts empty). It now lives in the extension's own storage (`chrome.storage.local`, `unlimitedStorage`), shared by both addresses, with IndexedDB as a fallback. I could not reproduce the loss locally, so the Activity log now prints, after every tab, how many balls are kept, where, and on which address (`store: N balls kept (extension) on www.cricinfo.com`): if it ever drops to 0 the log shows between which two tabs.
- **No more silent junk:** a match with fewer than 150 balls (and commentary expected) is NOT saved and NOT marked done: the commentary tab is loaded again, up to 2 more times. After that it is saved and marked `incomplete`. The panel's Options has **Redo low captures**: it forgets matches that older versions saved with too few balls and queues them again when their link was kept (links are kept from this version on; for older ones the log lists the ids so you can paste the links again).
- **Updating without losing the queue:** Stop, copy the new files over the SAME folder, press the reload arrow on `chrome://extensions`, open the panel and press Resume. The queue, done-list and settings live in `chrome.storage.local` and survive the reload. Reloading adds the `unlimitedStorage` permission.

### v1.6.2: both teams / innings
Cricinfo's commentary page shows one innings at a time; the switch is the team dropdown (for example "SL v") next to the sort ("New") and the filter ("Full Commentary"). The earlier code only looked for tabs containing the word "innings", so it never touched that dropdown and a match could be captured with one innings. Now, after the first load, the panel finds the team control (a dropdown button next to "Full Commentary", or a `<select>`), opens it, switches to every other team and loads that innings completely. The log shows it: `team control: SL (shown first) | ZIM (switched): 240 balls so far` and `innings seen: 1, 2`. A match only counts as captured when both innings were seen (otherwise it is retried like a thin capture, then saved as `incomplete`). If no team control is found the log says so and the old innings-tab search runs. Tested on a simulated page with a popup list; the real page's markup may differ, in which case the log line tells us what it found.

### v1.6.3: what the Kenya (65207) capture showed (Nov 2026)
- **Scorecard and playing-XI pages were never stored, in any capture.** The panel named each stored page by "the tab", but for Cricinfo URLs it picked the MATCH SLUG (the same for every tab), so scorecard, playing XI, commentary and statistics all overwrote one entry and only the last visited survived. That is why every capture's `pages` has a single key and `dataops.store` reports `has_xi: False`. Fixed: pages are now stored as `full-scorecard`, `match-playing-xi`, `ball-by-ball-commentary`, `match-statistics`. Captures made before this have only the statistics page (their comments are fine): `python3 -m dataops.store missing` will list them; re-capture to get the scorecard and XI.
- **One innings only:** 65207 has 320 balls, all `inningNumber 2` (a full second innings, overs 0.1 to 49.6); the page requested only innings 2 and the team control was not found, so innings 1 never loaded. The control finder no longer depends on the tag type: it finds the "Full Commentary" filter, takes everything on the same visual row (never the page heading), and uses the item that is a team code or team name, or the only one that is neither the sort nor the filter. If it still finds nothing, the log now prints what the row contains (`team control: none found (filter found; row items: button:'New' | div[button]:'IND' | ...)`) so the markup can be matched.
- **No wasted reloads:** if no team control exists, reloading the commentary tab cannot add the other innings, so the match is saved once and marked `incomplete` with the reason, instead of three identical loads.
- Verified on the real site by this capture: the scroll fix (20 -> 320 balls) and the storage fix (320 balls kept from the commentary tab to the end).
- **Redo low captures** now also re-queues matches saved as `incomplete` (for example one innings only) when their link was kept (links are kept from 1.6.0 on).

### v1.6.4: 65208, and a finder that does not guess (Nov 2026)
What the 65208 capture and the 65210 sample page showed, and what changed:
- **The team control was on the page, my search looked at the wrong row.** The page reads `Summary | Scorecard | Commentary | Overs | Table | News | Photos | New | AUS | Full Commentary`. The finder took the nav tab "Commentary" for the filter and scanned the nav row. It now needs the exact "Full Commentary" filter (never inside a tab list or nav).
- **The page says exactly what to look for.** Every Cricinfo tab embeds `match.teams[].team.abbreviation / longName / inningNumbers` and `content.innings[].inningNumber / balls`. The finder now looks for an item that IS one of the match's team labels (on the filter's row, then anywhere above the first commentary item), and the dropdown options are the other teams' labels (abbreviation or full name; any other option as a last resort). `select` elements work too.
- **Complete means "every innings the page lists".** The expected set comes from `content.innings` (those with balls bowled): 1, 2 for an ODI; 1 to 4 for a Test (each team then has two innings). The log shows `innings seen 1, 2 of expected 1, 2`. A match missing an innings is retried, then saved as `incomplete` with the reason. Checked on your three captures: 65210 NZ/WI [1,2], 65208 PAK/AUS [1,2], 65207 IND/KENYA [1,2].
- **Resuming on the wrong tab:** the runner decided "I am on this match" by match id alone, so resuming on the statistics tab recorded that page as the scorecard (65208 has no `full-scorecard`). It now also requires the tab the plan asks for, and navigates there if not.
- **Slow first batch:** the loader now waits up to 25 s for the first balls before it starts counting stalls, and is more patient while few balls are in (65208 stopped at 20 on the first try and reached 318 on the retry). After switching team it waits for the new innings' balls to arrive.
- Stale entries named after the match (left by the old tab-naming bug) are dropped when a capture is resumed.
- Tested on simulated pages: abbreviations, full-name popups with plain-div controls, a four-innings Test, resuming on the statistics tab with a nav row above the filter row.

### v1.6.5: 65210, "why is it still not working, and why retry again and again?" (Nov 2026)
- **What the 65210 capture showed:** the finder now found the control (`WI`) and "switched to NZ", yet all 57 comment requests in the file are `inningNumber=2`: the page never asked for innings 1. The log said "switched" only because my code had clicked something; a plain `element.click()` is not accepted by every dropdown (menus built on pointer or keyboard events ignore it).
- **Selecting is now tried several ways and every way is VERIFIED:** plain click, a full pointer sequence (pointerdown / mousedown / pointerup / mouseup / click with real coordinates), the clickable parent, then four keyboard sequences (Down+Enter, Down+Down+Enter, Up+Enter, Enter+Down+Enter). "It worked" means the control's label became the new team, or new innings' balls arrived, or the page itself requested another `inningNumber` (recorded from its API calls). The log says which way worked: `ZIM (switched by pointer events)`.
- **When nothing works, the real markup is kept:** the Activity log gets `switch diagnosis: ... control: <button ...> | popup: <div role=listbox ...>` (and the same goes into the saved JSON under `diag`), so the next fix is made from the page's actual HTML, not a guess.
- **No more retrying a failure that cannot change:** a reload can only help when something can differ (a slow load). If the control is missing or will not switch, the match is saved ONCE as `incomplete` with the reason (`no team control found` vs `found but the page would not switch`). Reloads remain only for thin captures with a working control.
- **The saved page text no longer contains our own panels** (the Activity log was ending up in `_text`, as seen in the statistics export).
- Tested on simulated dropdowns that react only to click, only to pointer events, only to the keyboard, and to nothing.

## Capturing every match (master index first)
1. Find a list page whose rows link to matches (Statsguru "match results" per format, 200 rows per page; or a season archive). Copy its URL and replace the page number with `{page}`.
2. `python3 -m dataops.index urls --template '<url with {page}>' --pages <N> --out data/index/urls_odi.txt`, paste the URLs into the batch box: each list page is saved as a page file (tables + links). From v1.7 the extension also runs on `stats.espncricinfo.com`.
3. `python3 -m dataops.index build <folder of saved pages>` (master list: id, url, official number, date, teams) then `python3 -m dataops.index check` (the numbers and dates must agree with Cricsheet before you trust them).
4. `python3 -m dataops.index queue --since 2003 --chunk 500`, paste `data/index/queue_001.txt` into the batch box, and repeat for each chunk. Already-complete matches are skipped.

### Easiest start: team series-results pages (v1.7.1)
`https://www.cricinfo.com/records/team/team-series-results/<team>-<id>/<format>-<classId>` (e.g. `.../india-6/test-matches-1`) lists every series that team played in that format. Paste one per team and format into the batch box: the crawler goes list -> series -> matches by itself (a list may now hold up to 600 series; series seen from several teams are queued once). Turn on "save lists" to keep each series page, then `python3 -m dataops.index build <folder>` reads their match lists into the master index.

## v1.8.0: direct fetch (faster, fewer requests)
`direct.js` is an optional, separate module (Options → "Direct fetch", on by default). After the scorecard page of a match has loaded it
- fetches the playing XI, statistics and summary tabs as plain HTML and stores their embedded data under the same keys as before (`match-playing-xi`, `match-statistics`, `live-cricket-score`);
- reads the commentary through the endpoint the page itself uses (`/v1/pages/match/comments`), innings by innings (1-2 for an ODI, 1-4 for a Test), following its `nextInningOver` cursor to the end: no scrolling, no team dropdown;
- checks the result against the scorecard (legal balls per innings); the log shows `innings 1: 689/689 ...`. A shortfall is reported, and the match is only treated as complete when the cursor reached its end for every innings.
Nothing is saved by the module itself: it hands the data to panel.js, so the saved JSON has the same format. If anything fails (or "Direct fetch" is off), that match is done the old way. A 403/429 stops the run the same way a human-check page does (auto-resume backs off). Pace: 8-16 s between matches (5-10 s with "Quick pace"), ~0.5-1 s between API requests.
Also: Test commentary controls labelled "ENG 2nd Innings" are now recognised by the old way too.
Updating a run that is in progress: Stop, reload the extension at chrome://extensions, refresh the tab, Resume. The queue, the done list and any half-captured match live in the extension's storage and carry over.

### v1.8.1
- The commentary API answered **403** to the direct requests in a live run. That is the server refusing this way of asking, so the module does not retry it or try other routes: direct fetch switches itself OFF for the rest of the run (Start/Resume tries it once more) and the match is finished the old way. Only HTTP **429** (slow down) triggers the backoff/rest.
- Tabs that were fetched as HTML (playing XI, statistics, summary) are still not opened again, so the old way needs fewer page loads even when the commentary API says no. Untick "Direct fetch" in Options to go back to exactly the 1.6.5 behaviour.

### v1.8.2: running while the screen is locked
Why a locked laptop stops it: when the session is locked (Win+L, Cmd+Ctrl+Q, or an automatic lock) Chrome treats its windows as hidden. A hidden page is not drawn, so the commentary's scroll-to-load never fires, and Chrome slows the page's timers to about one tick a minute after a few minutes. Keep-awake only stops the computer from SLEEPING; it cannot stop a lock.
What 1.8.2 does about it: waits are timed by the extension's background worker while the page is hidden (not throttled); the capture waits patiently ("window is hidden ... waiting") instead of timing out on the commentary and picks up when you unlock; Options → "also keep the screen on" holds the display awake, which stops the automatic lock on many systems; pages that need no scrolling (scorecard, playing XI, statistics, and direct fetch when the site allows it) keep working while hidden.
What it cannot do: load the commentary by scrolling in a window that is locked or minimised. For unattended runs, stop the lock itself:
- Windows: Settings → Accounts → Sign-in options → "If you've been away, when should Windows require you to sign in again?" = Never; Settings → Personalization → Lock screen → Screen saver: "On resume, display logon screen" unticked; Power: screen/sleep timers long, "closing the lid" = Do nothing. (Win+L locks on demand: do not press it.)
- macOS: System Settings → Lock Screen → "Require password after screen saver begins or display is turned off" = Never (or the longest); Battery/Power → prevent automatic sleeping; keep the lid open; `caffeinate -dimsu` in a terminal is a good extra.
- Leave the capture tab in its own Chrome window that is not minimised (covered by other windows is fine on most systems; minimised is not).
A display that is simply turned off (not locked) is fine on most systems.

**Re-capturing matches already done (v1.8.3):** the extension remembers finished matches and skips them. To re-scrape specific matches (for example ones whose file did not reconcile), put `#force` alone on the first line of the link box, then the links, then Start. Only that queue ignores the done-list, and the new file has the same name as the old one. The repo side (`python3 -m dataops.drive_ingest`) keeps the re-capture if it reconciles with the scorecard and the earlier one did not.

**Strict mode (v1.8.3):** tick "strict: capture only the links I pasted", or put `#strict` on a line at the top of the link box (it combines with `#force`, one per line). A series or list link in the queue is then never expanded: it is skipped (nothing queued, nothing saved), so the run covers exactly the set list you pasted. Match links are captured as usual. "Add links from this page" is a button you press yourself, so it still works.

**Chrome and Firefox (v1.9.0):** run `python3 build.py` in this folder to make `dist/ttm-capture-chrome-<v>.zip` and `dist/ttm-capture-firefox-<v>.zip` from the same source. Chrome: unzip, then Load unpacked at chrome://extensions. Firefox 128 or newer: unzip, then about:debugging#/runtime/this-firefox > Load Temporary Add-on > manifest.json (it is removed when Firefox closes). In Firefox the keep-awake option does nothing (keep the computer awake yourself). Chrome and Firefox keep separate done-lists and downloads, so give each its own links when running both. The Firefox build has not been run in Firefox by the author: report anything that behaves differently.
