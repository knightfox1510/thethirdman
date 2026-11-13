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
