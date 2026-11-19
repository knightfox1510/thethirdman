# NZ v IND ODI series 2026 (Nov 2026): dataset

Built from the Cricbuzz full-commentary captures (`data/cricbuzz/nz_ind_{1,2,4,5}odi.json`; local, gitignored) and, for cross-checking the 4th ODI, the Cricinfo capture (`data/cricinfo/nz_ind_4odi.json`). Matches 1, 2, 4, 5 are ball by ball; the 3rd was washed out (no play).

Rebuild:
```
for m in 1 2 4 5: python3 -m dataops.cricbuzz_balls data/cricbuzz/nz_ind_${m}odi.json  -> <stem>_balls/overs/wickets/partnerships/notes.csv
CS_DIR=<cricsheet dir> python3 -m dataops.winprob fit                  # win-probability model (data/models/odi_winprob.json)
CS_DIR=... python3 analysis/nz_ind_wp.py && python3 analysis/nz_ind_deep.py && python3 analysis/nz_ind_story.py
python3 analysis/nz_ind_validate.py                                    # 26 cross-checks
python3 analysis/nz_ind_series.py                                      # SERIES.md (whole series; leaders asserted against Wikipedia) (Wikipedia match boxes, Cricbuzz editorial lines, Cricinfo capture)
python3 analysis/nz_ind_report.py                                      # REPORT.md
```

| File | What it is |
|---|---|
| `<stem>_balls.csv` | one row per delivery (wides/no-balls included): inning, over, ball_no, legal, bowler, batter, runs (team score change), bat_runs (off the bat), extra, wicket, dismissal, event (FOUR/SIX/DROPPED/UDRS/...), score_after, wkts_after, striker_runs/balls, text |
| `<stem>_overs.csv` | the over summaries Cricbuzz gives: score, wickets, runs in the over, per-ball runs string, bowler, batters |
| `<stem>_wickets.csv` | every wicket: batter, bowler, kind, fielder, score, over |
| `<stem>_partnerships.csv` | runs/balls between wickets with the batters involved |
| `<stem>_notes.csv` | Cricbuzz's editorial lines (stats, milestones, field changes, injuries): leads to verify, never text to copy |
| `analysis/<stem>_wp.csv` | win probability after every delivery (batting side and India), the swing, text |
| `analysis/<stem>_player_value.csv` | win probability added by each player (batting, bowling), runs saved v the archive baseline |
| `analysis/summary.json` | innings and phase tables, bowling cards, pace v spin, drops, reviews, partnerships |
| `analysis/story.json` | win-probability curve, tipping point, chase checkpoints, drops cost, fielding swings, collapse windows, hidden winners/losers, series context (Wikipedia) |
| `REPORT.md` | the 4th and 5th ODIs in depth, every number code-derived |
| `SERIES.md` | the whole series: leaderboards, phases, drops, catches, venues |

Limits: Cricbuzz only (no line/length/shot/wagon for the 5th ODI); the win-probability model is fitted on the Cricsheet ODI archive (a sample; validated on held-out matches) and is an indication, not a fact; bowling styles are from our Cricinfo squad data where available (assumed otherwise, starred in the report).
