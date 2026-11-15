# Data plan: how we keep the data trustworthy, and what we can measure that nobody else shows

## 1. Source tiers
- **Tier A (authoritative):** ESPNcricinfo scorecards, results lists and Statsguru, ICC, BCCI / IPL / board sites. Reached through our Chrome extension (batch mode); the sandbox is blocked (403).
- **Tier B (structured, unofficial):** Cricsheet (free ball-by-ball, internationals from about 2001-02, near-complete for recent years but with missing matches, e.g. no India v Afghanistan T20I at all); Sportmonks (licensed, IPL and T20I only); Cricbuzz commentary captures.
- **Tier C (secondary):** Wikipedia (raw wikitext via the API; its team/player tables cite Cricinfo), news. Good for cross-checks, never the only source.

## 2. The pipeline (all in `dataops/`)
1. `python3 -m dataops.audit team India --since 2024-07-27` : what we HOLD vs what EXISTS (Wikipedia/Cricinfo all-time totals by format; `opp` lists the missing opponents). `audit.py player "V Kohli" "Virat Kohli"` does the same for a career (matches and runs).
2. `dataops/verify.py` : every number goes through `Claims.check(name, value, {source: value})`. Two independent sources agree = OK. One source = LABELLED only if the video says "in our archive". Disagreement = CONFLICT. A spec with `provenance_required` cannot be built (engine.py) or uploaded (publish/youtube.py) while any claim is UNVERIFIED or in CONFLICT.
3. Browser batch capture of Tier A pages (see tools/ttm-capture/README.md), then `python3 -m dataops.ingest <downloads folder>`.
Known gaps found by the audit (Nov 2026): Cricsheet holds 219 of India's 601 Tests (nothing before Dec 2001), 529 of 1,088 ODIs (nothing before Jun 2002), 289 of 303 T20Is (no Afghanistan matches, one Sri Lanka, one Scotland missing). So all-time totals and records must come from Tier A, never from Cricsheet sums.

## 3. Measures (implemented in `dataops/measures.py` where Cricsheet ball-by-ball allows; the rest need the Cricinfo captures) (beyond approach, intent and risk)
**Player profiles (e.g. a full Kohli career)**
- Era-adjusted value: runs above the league average per innings, by year; peak and decline detection; rolling 20-innings form curve; age curve against peers.
- Phase and matchup splits: powerplay / middle / death; pace vs spin, left- vs right-arm; record against the 10 bowlers he faced most; line, length and shot (Cricinfo captures); wagon-wheel scoring zones; control % (false-shot rate).
- Hazard curve: probability of dismissal at ball 1, 5, 10, 20, 30, 50 of an innings (when is he most vulnerable); dot-ball %, balls per boundary, acceleration curve.
- Context: home / away / neutral, by venue, day-night, batting first vs chasing, required-rate pressure, wickets down, finals and knockouts; match-impact (win-probability added) per innings.
- Consistency and dependence: share of innings over 30 / 50, conversion of fifties, big-score dependence, variance, ducks; role (opener / anchor / finisher) and partnership contribution.
- Dismissal anatomy: how, when, to whom; bowler-type dismissal map.
- Captaincy: record, toss, bowling changes, declarations, DRS success.
**Coach profiles and comparisons**
- Tenure ledger: W-L-D by format, home / away, opposition strength at the time (ICC rating), finals, series outcomes, and result vs expectation (Elo-style expected points per match).
- Team intent timeline: run rate by over averaged across a tenure vs predecessors; powerplay / middle / death scoring; aggression index (balls per boundary, dot-ball %); batting depth (how often batter 8 faces 10+ balls); collapse frequency (wickets in a 10-ball window, all-out %).
- Bowling approach: pace / spin share by phase, containment vs wicket-taking, death-over economy, new-ball plans, bowler workload.
- Selection and rotation: players used per series, debutants, XI stability (overlap between consecutive XIs), batting-order fixity per player, average age and caps, workload and rest patterns, captain changes, squad rotation by format (a rotated side flatters or hurts a record: always show it).
- Decisions: toss and bat-first outcomes, chase vs defend, declaration / follow-on timing, review accuracy.
- Luck vs skill: Pythagorean expected wins, close-match record (under 10 runs / last over), schedule difficulty.
- Comparison rules: same-format baseline per era, minimum sample sizes shown, same core players before / after, per-100-matches views.
**Unique visuals we can make from our data** (nobody shows these): "team DNA" radars per coach, intent timelines, XI-stability trees, collapse maps, player-usage flows, matchup heat maps, hazard curves, expected-vs-actual results.

## 4. What the captures give us per match (dataops/matchdata.py)
Series and match ids, date, format, day/night, season, toss winner and choice, result and margin, scheduled overs; venue (id, name, town, country, capacity); both teams, home side, captains; umpires, TV and reserve umpire, referee; innings (runs, wickets, overs, extras by type, fours, sixes, dropped catches); playing XI with each player's roles, batting and bowling style, date of birth; bench / squad members and roles when the playing-XI tab is captured; every partnership, fall of wicket, DRS review (team, umpire, batter, outcome); ball-by-ball with line, length, shot, control and wagon-wheel where Cricinfo has it. Coaches and support staff were NOT in the match-page data of our first two captures; the batch mode also saves each series' squads page so we can see where (if anywhere) the site lists them: `matchdata` prints every key it finds with coach / staff / squad in its name under `unmapped`.
