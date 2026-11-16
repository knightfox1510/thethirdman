// Batch + crawl mode (v1.6.1: auto-resume, keep-awake, stall watchdog; commentary loads near the last item, the capture lives in extension storage, thin captures are retried and never marked done): works through a queue of links in YOUR browser tab, one at a time, at a human pace.
// Queue items are detected by their link: a MATCH (opens scorecard, playing XI, commentary, statistics; saves ONE json per match), a SERIES page (queues its matches),
// a LIST page such as a team's season view (queues its series), or any other page (player stats, records tables: saved as one json, with each stat tab).
// Nothing is captured twice: finished matches/series are remembered in the browser; paste the ids the repo already holds with "Import known ids" (python3 -m dataops.store known).
// Upcoming and live matches are skipped (nothing is saved for them). Stop is immediate (it cancels the pending wait / navigation), Clear queue empties the list.
(() => {
  const SITE = /cricbuzz/.test(location.hostname) ? "cricbuzz" : "cricinfo";
  const SCHEMA = 4;                                                     // bump when the capture gains new tabs/fields: older captures are then re-done once
  const TABS = SITE === "cricinfo"
    ? { score: "full-scorecard", xi: "match-playing-xi", comm: "ball-by-ball-commentary", stats: "match-statistics" }
    : { score: "live-cricket-scorecard", comm: "live-cricket-full-commentary" };       // tab slugs: adjust here if a site renames them
  const TAB_LABEL = { score: "scorecard", xi: "playing XI", comm: "commentary", stats: "statistics" };
  const MAX_DEFAULT = 20, DELAY = [4000, 9000], BETWEEN = [12000, 25000];
  const rnd = ([a, b]) => a + Math.random() * (b - a);
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  let stopFlag = false;                                                 // set by Stop / Clear: every wait below checks it, so nothing keeps running after you press Stop
  const wait = async (ms) => { const end = Date.now() + ms; while (Date.now() < end) { if (stopFlag) return false; await sleep(Math.min(250, end - Date.now())); } return !stopFlag; };
  const BACKOFF = [20, 45, 90];                                         // minutes to wait after a human-check / access-denied page when auto-resume is on (3 tries, then it stops and waits for you)
  const blank = () => ({ auto: false, cool: 20, keepAwake: true, backoff: null, blockTries: 0, navTries: 0, errs: 0, pausedUntil: 0, resumeUrl: null, running: false, queue: [], idx: 0, tab: 0, plan: null, max: MAX_DEFAULT, since: 0, saveLists: false, log: [], results: [], done: {}, now: "", ui: { min: false, opts: false, log: true } });
  const OPTS = ["auto", "cool", "keepAwake", "backoff"];                // settings live in their own key so changing them mid-run is never overwritten by a running step
  const get = () => new Promise((r) => chrome.storage.local.get(["ttm_batch", "ttm_opts"], (v) => r(Object.assign(blank(), v.ttm_batch || {}, v.ttm_opts || {}))));
  const setOpts = (s) => new Promise((r) => chrome.storage.local.set({ ttm_opts: Object.fromEntries(OPTS.map((k) => [k, s[k]])) }, r));
  const set = (s) => new Promise((r) => chrome.storage.local.set({ ttm_batch: s }, r));
  const clean = (u) => String(u).split("#")[0];
  const matchId = (u) => { try { const x = new URL(u, location.href); const p = x.pathname;
    if (SITE === "cricinfo") { if (/^\/series\/[^/]+-\d+\/[^/]+-\d+(\/|$)/.test(p)) return (p.match(/^\/series\/[^/]+-\d+\/[^/]+-(\d+)/) || [])[1]; const o = p.match(/\/(?:ci\/engine\/)?match\/(\d+)\.html/); return o ? o[1] : null; }
    return (p.match(/\/(?:live-cricket-[a-z-]+|cricket-scores?)\/(\d{4,})\//) || [])[1] || null; } catch (e) { return null; } };
  const isSeries = (u) => { try { const p = new URL(u, location.href).pathname; return SITE === "cricinfo" ? (/\/series\/[^/]+-\d+\/?(match-results|match-schedule-fixtures-and-results|squads)?\/?$/.test(p) || /\/ci\/engine\/series\/\d+\.html/.test(p)) && !matchId(u) : /\/cricket-series\/\d+\//.test(p); } catch (e) { return false; } };
  const kind = (u) => matchId(u) ? "match" : isSeries(u) ? "series" : /index\.html\?.*view=season|\/team\/[^/]+\/(match-results|series)|match-results|series-results/.test(u) ? "list" : "page";
  const doneKey = (u) => SITE + ":" + (matchId(u) || clean(u));
  const label = (u) => { const k = kind(u); return k === "match" ? `match ${matchId(u)}` : k === "page" ? `page ${(new URL(u, location.href).pathname.split("/").filter(Boolean).slice(-2).join("/"))}` : `${k} ${clean(u).slice(-40)}`; };
  const tabUrl = (u, name) => { const x = new URL(u, location.href);
    if (SITE === "cricinfo") { const m = x.pathname.match(/^(\/series\/[^/]+-\d+\/[^/]+-\d+)/); return m ? `${x.origin}${m[1]}/${name}` : u; }
    const m = x.pathname.match(/^\/[a-z-]+\/(\d{4,})\/([^/?#]+)/); return m ? `${x.origin}/${name}/${m[1]}/${m[2]}` : u; };
  const blocked = () => /access denied|captcha|unusual traffic|are you a robot|just a moment|verify you are human/i.test(document.title + " " + (document.body ? document.body.innerText.slice(0, 600) : ""));
  const notFound = () => /page not found|404|can't find|couldn't find/i.test(document.title);
  const yearOf = (t) => { const m = (t || "").match(/\b(19\d\d|20\d\d)\b/); return m ? +m[1] : 0; };
  // ---- keep the computer awake while running (background.js uses chrome.power; it lets go by itself if this tab stops sending a heartbeat)
  const awake = (on) => { try { chrome.runtime.sendMessage({ ttm: "awake", on }, () => void chrome.runtime.lastError); } catch (e) {} };
  const heartbeat = () => get().then((s) => awake(!!(s.running && s.keepAwake !== false))).catch(() => {});
  // ---- navigation with a stall watchdog: if the page has not replaced this one after 2 minutes, try again (3 times)
  let navTimer = null;
  const nav = (url) => {
    clearTimeout(navTimer);
    navTimer = setTimeout(async () => {
      const s = await get(); if (!s.running || stopFlag) return;
      s.navTries = (s.navTries || 0) + 1;
      if (s.navTries <= 3) { await log(s, `page did not load in 2 minutes: trying again (${s.navTries}/3)`); return nav(url); }
      s.navTries = 0; s.resumeUrl = url;
      if (s.auto && (s.blockTries || 0) < (s.backoff || BACKOFF).length) return backOff(s, "Page keeps failing to load (network down?)");
      return stopped(s, "STOPPED: the page will not load. Check the network, then press Resume.");
    }, 120000);
    location.assign(url);
  };
  // ---- auto-resume: pause (state is saved, so a reload of this tab does not lose the pause), then carry on by itself
  const backOff = async (s, why) => {
    const list = s.backoff || BACKOFF, m = list[s.blockTries || 0] * (0.9 + Math.random() * 0.2); s.blockTries = (s.blockTries || 0) + 1;
    return coolDown(s, why, m);
  };
  const coolDown = async (s, why, mins, resetRun) => {
    if (mins != null) { s.pausedUntil = Date.now() + mins * 60000; if (resetRun) s.results = []; await log(s, `${why}: auto-resume in ${mins < 1 ? Math.round(mins * 60) + " s" : Math.round(mins) + " min"} (about ${new Date(s.pausedUntil).toTimeString().slice(0, 5)}).`); }
    while (Date.now() < s.pausedUntil) {
      if (stopFlag) return;
      s.now = `paused (auto): resumes in ${Math.max(1, Math.ceil((s.pausedUntil - Date.now()) / 60000))} min`; render(s);
      if (!(await wait(Math.min(30000, Math.max(250, s.pausedUntil - Date.now()))))) return;
    }
    const t = await get(); if (!t.running || stopFlag) return;
    const url = t.resumeUrl; t.pausedUntil = 0; t.resumeUrl = null; await log(t, "Auto-resume: carrying on.");
    return url ? nav(url) : goNext(t, false);
  };
  const log = async (s, msg) => { s.log.push(new Date().toISOString().slice(11, 19) + " " + msg); s.log = s.log.slice(-120); await set(s); render(s); };

  // Links are collected from the page's MAIN content only, never from the header, menus, side panels or "recent / live / trending matches" widgets, and, for a series page, only matches of THAT series.
  const WIDGET = "header, nav, aside, footer, [role=navigation], [class*=trending], [class*=Trending], [class*=recent], [class*=Recent], [class*=live-match], [class*=LiveMatch], [class*=carousel], [class*=Carousel], [class*=ticker], [class*=Ticker], [class*=sidebar], [class*=Sidebar], [class*=related], [class*=Related], [class*=upcoming], [class*=Upcoming], [class*=latest], [class*=Latest], [class*=news], [class*=News], [class*=widget], [class*=Widget], [class*=menu], [class*=Menu]";
  const seriesSeg = (u) => { try { const p = new URL(u, location.href).pathname; return SITE === "cricinfo" ? (p.match(/\/series\/([^/]+-\d+)/) || [])[1] || null : (p.match(/\/cricket-series\/(\d+)\/([^/]+)/) || []).slice(1).join("/") || null; } catch (e) { return null; } };
  const structured = () => {                                             // Cricinfo: props.appPageProps.data.content.matches is the series' own list; props.editionDetails.trendingMatches is the unrelated sidebar
    try { const nd = JSON.parse(document.getElementById("__NEXT_DATA__").textContent); const ms = nd.props.appPageProps.data.content.matches; if (!Array.isArray(ms)) return null;
      return ms.filter((m) => m && m.slug && m.objectId && m.series && m.series.slug).map((m) => ({ kind: "match", id: String(m.objectId), url: `${location.origin}/series/${m.series.slug}-${m.series.objectId}/${m.slug}-${m.objectId}/full-scorecard`,
        text: `${m.title || ""} ${m.startDate || ""} ${m.status || ""}`, year: m.startDate ? +m.startDate.slice(0, 4) : 0, state: m.state })); } catch (e) { return null; }
  };
  const links = (scope) => {                                             // scope: a series page url (or null for a list page / "add links" button)
    const root = document.querySelector("main") || document.querySelector("[role=main]") || document.body; const seg = scope ? seriesSeg(scope) : null; const out = new Map();
    for (const a of root.querySelectorAll("a[href]")) {
      if (a.closest(WIDGET)) continue;                                   // sidebar / menu / recent-matches widgets
      const h = clean(a.href); const k = kind(h); if (k !== "match" && k !== "series") continue;
      if (seg && k === "match" && SITE === "cricbuzz") { const slug = (seg.split("/")[1] || ""), ms = (new URL(h).pathname.split("/").pop() || ""); if (slug && !ms.endsWith(slug.replace(/-\d+$/, "")) && !ms.includes(slug.replace(/-\d{4}$/, ""))) continue; }   // (Cricinfo matches can belong to a different tour series than the trophy page: no series filter there)
      const id = k === "match" ? matchId(h) : h; const row = a.closest("tr, li, div[class*=match], div[class*=card]") || a.parentElement;
      if (!out.has(k + id)) out.set(k + id, { kind: k, id, url: h, text: ((row ? row.innerText || row.textContent : a.innerText || a.textContent) || "").replace(/\s+/g, " ").trim().slice(0, 300) });
    } return [...out.values()];
  };
  const download = (name, obj) => { const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([JSON.stringify(obj)], { type: "application/json" })); a.download = name; document.body.appendChild(a); a.click(); a.remove(); };
  const savePage = async (prefix = "page") => {                          // tables, page data, text, links; stats pages: every format tab / filter too
    const panels = () => [...document.querySelectorAll("[data-ttm-panel]")], withPanelsHidden = (fn) => { const h = panels().map((e) => [e, e.style.display]); h.forEach(([e]) => (e.style.display = "none")); try { return fn(); } finally { h.forEach(([e, d]) => (e.style.display = d)); } };
    const grab = () => ({ tables: [...document.querySelectorAll("table")].slice(0, 60).map((t) => [...t.rows].map((r) => [...r.cells].map((c) => c.innerText.trim()))), text: withPanelsHidden(() => (document.querySelector("main") || document.body).innerText.slice(0, 600000)) });
    let nd = null; try { const el = document.getElementById("__NEXT_DATA__"); nd = el ? JSON.parse(el.textContent) : null; } catch (e) {}
    const out = { site: SITE, schema: SCHEMA, page_url: location.href, title: document.title, saved_at: new Date().toISOString(), next_data: nd, ...grab(), links: links(), views: {} };
    if (/stats|records|statsguru|career/i.test(location.href)) {
      const tabs = [...document.querySelectorAll("[role=tab], button, a")].filter((b) => b.offsetParent && /^(tests?|odis?|t20is?|t20|ipl|first[- ]class|list a|batting|bowling|fielding|all)$/i.test((b.textContent || "").trim())).slice(0, 14);
      for (const b of tabs) { if (stopFlag) break; try { b.click(); await sleep(2500); out.views[(b.textContent || "").trim()] = grab(); } catch (e) {} }
    }
    download(`${prefix}_${SITE}_${(location.pathname + location.search).replace(/[^a-z0-9]+/gi, "_").slice(0, 80)}.json`, out);
    return out.tables.length + Object.values(out.views).reduce((n, v) => n + v.tables.length, 0);
  };

  const enqueue = (s, items, front) => {                                 // adds links not already done / queued
    const have = new Set(s.queue.map((u) => doneKey(u)));
    const fresh = items.filter((u) => !s.done[doneKey(u)] && !have.has(doneKey(u)) && (!s.since || !yearOf(u.text) || yearOf(u.text) >= s.since)).map((u) => u.url);
    if (front) s.queue.splice(s.idx + 1, 0, ...fresh); else s.queue.push(...fresh);
    return fresh.length;
  };
  const stopped = async (s, msg) => { s.running = false; s.now = ""; s.pausedUntil = 0; awake(false); if (!(s.queue.length - s.idx)) s.started = false; await log(s, msg); };
  const advance = async (s) => { s.blockTries = 0; s.navTries = 0; s.errs = 0; s.idx++; s.tab = 0; s.plan = null; while (s.idx < s.queue.length && s.done[doneKey(s.queue[s.idx])] && s.done[doneKey(s.queue[s.idx])].schema === SCHEMA) s.idx++; await set(s); };   // skips already-done items at once
  const goNext = async (s, pause = true) => {
    if (stopFlag) return;
    if (s.idx >= s.queue.length) return stopped(s, `DONE: queue finished, ${s.results.length} captured this run.`);
    if (s.results.length >= s.max && s.auto) { s.resumeUrl = null; return coolDown(s, `Run limit reached (${s.max})`, (+s.cool || 20) * (0.8 + Math.random() * 0.4), true); }
    if (s.results.length >= s.max) return stopped(s, `Run limit reached (${s.max}). ${s.queue.length - s.idx} still queued: press Resume to continue.`);
    s.now = `next: ${label(s.queue[s.idx])}`; await set(s); render(s);
    if (pause && !(await wait(rnd(BETWEEN)))) return;
    nav(s.queue[s.idx]);
  };

  const step = async () => {                                            // errors never leave the run silently dead: with auto-resume it retries (5 times), otherwise it stops and says why
    try { await stepInner(); } catch (e) {
      const s = await get(); if (!s.running || stopFlag) return;
      s.errs = (s.errs || 0) + 1; await log(s, `error: ${e && e.message}`);
      if (s.auto && s.errs <= 5) { if (!(await wait(30000))) return; return step(); }
      return stopped(s, "STOPPED after an error (see the log). Press Resume to try again.");
    }
  };
  const stepInner = async () => {
    const s = await get(); if (!s.running || stopFlag) return render(s);
    clearTimeout(navTimer); s.navTries = 0;
    if (s.pausedUntil > Date.now()) return coolDown(s, null);          // the page was reloaded during an auto-resume pause: finish the pause first
    if (s.pausedUntil) { s.pausedUntil = 0; await set(s); }
    if (blocked()) {
      if (s.auto && (s.blockTries || 0) < (s.backoff || BACKOFF).length) { s.resumeUrl = location.href; return backOff(s, "The site asked for a human check / denied access"); }
      return stopped(s, s.auto ? `STOPPED: still blocked after ${(s.backoff || BACKOFF).length} automatic retries. Solve the check in the tab, then press Resume.` : "STOPPED: the site is asking for a human check. Solve it in the tab, then press Resume.");
    }
    const job = s.queue[s.idx]; if (!job) return stopped(s, `DONE: ${s.results.length} captured.`);
    const k = kind(job), key = doneKey(job);
    if (s.done[key] && s.done[key].schema === SCHEMA) { await advance(s); return goNext(s, false); }                       // already captured: skip, no waiting
    const here = clean(location.href), target = k === "match" ? matchId(job) : clean(job);
    const wantTab = k === "match" ? TABS[(s.plan || Object.keys(TABS))[s.tab || 0]] : null;
    const onTab = (t) => SITE === "cricinfo" ? location.pathname.split("/").filter(Boolean)[3] === t : location.pathname.replace(/^\//, "").startsWith(t);
    const onTarget = k === "match" ? (matchId(here) === target && onTab(wantTab)) : here.split("?")[0] === clean(job).split("?")[0];   // same MATCH is not enough: a resume on the statistics tab was recorded as the scorecard
    s.now = label(job); render(s);
    const go = k === "match" ? tabUrl(job, wantTab) : (k === "series" && SITE === "cricinfo" && !/match-schedule-fixtures-and-results|match-results/.test(job) && seriesSeg(job) ? `${new URL(job).origin}/series/${seriesSeg(job)}/match-schedule-fixtures-and-results` : job);
    if (!onTarget && !(k === "series" && clean(location.href).split("?")[0] === clean(go).split("?")[0])) { await log(s, `opening ${s.idx + 1}/${s.queue.length}: ${label(job)}`); if (!(await wait(rnd(DELAY)))) return; nav(go); return; }
    if (!(await wait(rnd(DELAY)))) return;
    if (k !== "match" && notFound()) { s.done[key] = { at: new Date().toISOString(), schema: SCHEMA, missing: true }; await log(s, "  page not found: skipped"); await advance(s); return goNext(s); }

    if (k === "list" || k === "series") {                                              // collect the next level down
      for (let i = 0; i < 4 && !stopFlag; i++) { window.scrollTo(0, document.body.scrollHeight); await sleep(1200); }
      if (stopFlag) return;
      const st = k === "series" && SITE === "cricinfo" ? structured() : null;                       // authoritative list when the page has it, else the main-content links
      const sub = st && st.length ? st : links(k === "series" ? job : null).filter((x) => k === "list" ? x.kind === "series" : x.kind === "match");
      if (st) await log(s, `  series list from the page data: ${st.length} matches${st.filter((x) => x.state && x.state !== "POST").length ? ` (${st.filter((x) => x.state && x.state !== "POST").length} not finished: they will be skipped)` : ""}`);
      if (sub.length > 150) { s.done[key] = { at: new Date().toISOString(), schema: SCHEMA, refused: sub.length }; await log(s, `  ${k}: ${sub.length} links found, far more than expected: not queued (the page layout may have changed). Add this ${k}'s links by hand.`); await advance(s); return goNext(s); }
      const n = enqueue(s, sub, true); if (sub.length) await log(s, `  e.g. ${sub.slice(0, 2).map((x) => (x.text || x.id).slice(0, 50)).join(" | ")}`);
      if (s.saveLists) await savePage(k);
      s.done[key] = { at: new Date().toISOString(), schema: SCHEMA, found: sub.length };
      await log(s, `  ${k}: ${sub.length} links found, ${n} new queued`); await advance(s); return goNext(s);
    }
    if (k === "page") {
      const n = await savePage("page"); if (stopFlag) return; s.done[key] = { at: new Date().toISOString(), schema: SCHEMA, tables: n }; s.results.push({ id: key });
      await log(s, `  saved page (${n} tables)`); await advance(s); return goNext(s);
    }
    // ---- a match
    const T = window.__ttm; if (!T) { if (!(await wait(2500))) return; return step(); }
    if (!s.plan) s.plan = Object.keys(TABS);                                           // scorecard first; the other tabs only if the match has them
    const idx = s.tab || 0, name = s.plan[idx]; s.now = `match ${target} · ${TAB_LABEL[name] || name}`; await log(s, `match ${target}: ${TAB_LABEL[name] || name}`);
    if (notFound()) {
      if (idx === 0) { s.done[key] = { at: new Date().toISOString(), schema: SCHEMA, missing: true }; await log(s, "  match page not found: skipped"); await advance(s); return goNext(s); }
      await log(s, `  no ${TAB_LABEL[name] || name} page for this match: skipped (the rest is still saved)`);
    } else {
      const mt0 = T.meta();
      if (mt0 && mt0.state && mt0.state !== "POST") { await log(s, `  match is ${mt0.state === "PRE" ? "upcoming" : "not finished"}: skipped, nothing saved`); await advance(s); return goNext(s); }
      if (name === "comm") {
        let n = await T.loadAll();
        const tm = await T.eachTeam();                                                   // the team dropdown ("SL v") switches the innings on Cricinfo: do every team
        await log(s, tm.found ? `  team control: ${tm.tried.join(" | ")}` : `  team control: none found (${T.diag()})`);
        s.noctl = s.noctl || {}; if (!tm.found || tm.stuck) s.noctl[key] = tm.found ? 2 : 1; else delete s.noctl[key];      // 1 = no control on the page, 2 = found but the page would not switch            // control missing, or found but the page would not switch: reloading cannot help, so no retries for the missing innings
        if (tm.stuck) await log(s, `  switch diagnosis: ${T.lastDiag()}`);
        if (tm.found) n = T.count();
        else {
          const inn = [...document.querySelectorAll("[role=tab], button")].filter((b) => b.offsetParent && /innings|\binn\b/i.test(b.textContent || "") && b.getAttribute("aria-selected") !== "true");
          for (const b of inn.slice(0, 3)) { if (stopFlag) return; b.click(); await sleep(2500); n = await T.loadAll(); }
        }
        await log(s, `  ${n} balls so far; innings seen ${T.innings().join(", ") || "?"} of expected ${T.expected().join(", ") || "?"}`);
      } else { if (!(await wait(2500))) return; T.grabText(); T.save(); }
    }
    if (stopFlag) return;
    const mtn = T.meta() || {};                                                        // what does this match have? (old matches: scorecard and players, no commentary)
    const applies = (nm) => nm === "xi" ? mtn.hasMatchPlayers !== false : nm === "comm" ? mtn.hasCommentary !== false : true;
    if (idx === 0) { if (mtn.hasCommentary === false) await log(s, "  no ball-by-ball exists for this match: commentary skipped (scorecard and players are still saved)"); if (mtn.hasMatchPlayers === false) await log(s, "  no playing-XI page for this match"); }
    let nx = idx + 1; while (nx < s.plan.length && !applies(s.plan[nx])) nx++;
    const inf = T.info(); await log(s, `  store: ${inf.balls} balls kept (${inf.storage}${inf.error ? ": " + inf.error : ""}) on ${inf.origin.replace("https://", "")}; innings ${inf.innings.join(", ") || "?"}`); await T.flush();   // where the balls are, tab by tab: a loss shows up here
    if (nx < s.plan.length) { s.tab = nx; await set(s); if (!(await wait(rnd(DELAY)))) return; nav(tabUrl(job, TABS[s.plan[nx]])); return; }
    const needs = mtn.hasCommentary !== false, have = T.count();
    const exp = T.expected(), seenInn = T.innings(), missingInn = exp.length ? exp.filter((n) => !seenInn.includes(n)) : (seenInn.length >= 2 ? [] : [2]);   // what the page itself lists (2 for an ODI, 4 for a Test) minus what we captured
    const twoInn = !needs || missingInn.length === 0;
    const noCtl = !!(s.noctl && s.noctl[key]);                                        // no team control on this page: reloading cannot add the other innings, so do not waste three loads on it
    if (needs && !noCtl && (have < 150 || !twoInn)) {                               // reloading only helps when something can change (a slow load): never when the control is missing or will not switch                                                         // thin commentary: do NOT save a near-empty file and do NOT mark the match done
      s.tries = s.tries || {}; s.tries[key] = (s.tries[key] || 0) + 1;
      if (s.tries[key] <= 2) { s.tab = Math.max(0, s.plan.indexOf("comm")); await set(s); await log(s, `  only ${have} balls / innings ${T.innings().join(", ") || "?"}: NOT saved, NOT marked done; loading the commentary again (try ${s.tries[key]}/2)`); if (!(await wait(rnd(DELAY)))) return; nav(tabUrl(job, TABS.comm)); return; }
    }
    const balls = T.saveJson();                                                        // one json per match
    s.done[key] = { at: new Date().toISOString(), schema: SCHEMA, balls, url: job, state: mtn.state || null, hasMatchPlayers: !!mtn.hasMatchPlayers, hasCommentary: mtn.hasCommentary, incomplete: needs && (balls < 150 || missingInn.length > 0), innings: T.innings(), expected: exp };
    s.results.push({ id: key, balls });
    await log(s, `  SAVED match ${target}: ${balls} balls${mtn.hasCommentary === false ? " (no commentary exists: scorecard + players)" : needs && (balls < 150 || missingInn.length) ? "  (INCOMPLETE: innings seen " + (T.innings().join(", ") || "?") + " of expected " + (exp.join(", ") || "?") + (noCtl ? (s.noctl[key] === 2 ? "; the team control was found but the page would not switch" : "; no team control found") + ", so the missing innings could not be switched to" : " after 3 tries") + ")" : ""}`);
    if (!(needs && (balls < 150 || missingInn.length))) await T.clear();                                      // the match is on disk: free its stored copy
    await advance(s); return goNext(s);
  };

  // ---------- panel (dark card, light text everywhere: nothing white-on-white)
  const C = { bg: "#0f172a", card: "#1e293b", line: "#334155", text: "#e2e8f0", mute: "#94a3b8", green: "#16a34a", red: "#dc2626", amber: "#d97706", blue: "#3b82f6" };
  const box = document.createElement("div"); box.setAttribute("data-ttm-panel", "1");
  box.style.cssText = `position:fixed;left:16px;bottom:16px;z-index:2147483647;background:${C.bg};color:${C.text};font:13px/1.45 system-ui,sans-serif;border-radius:12px;box-shadow:0 8px 30px rgba(0,0,0,.45);width:330px;border:1px solid ${C.line}`;
  const B = (id, text, bg, extra = "") => `<button id="${id}" style="background:${bg};color:#fff;border:0;border-radius:8px;padding:8px 10px;font:600 13px system-ui;cursor:pointer;${extra}">${text}</button>`;
  const INP = `background:${C.card};color:${C.text};border:1px solid ${C.line};border-radius:6px;padding:4px 6px;font:13px system-ui`;
  box.innerHTML = `
    <div id="tb-head" style="display:flex;align-items:center;gap:8px;padding:10px 12px;cursor:pointer">
      <b style="flex:1">Third Man capture</b><span id="tb-chip" style="font:700 11px system-ui;padding:2px 8px;border-radius:99px;background:${C.line}">IDLE</span><span id="tb-min" style="color:${C.mute}">–</span></div>
    <div id="tb-body" style="padding:0 12px 12px">
      <div id="tb-now" style="color:${C.mute};font-size:12px;min-height:18px;margin-bottom:4px"></div>
      <div style="height:8px;background:${C.card};border-radius:99px;overflow:hidden"><div id="tb-bar" style="height:100%;width:0;background:${C.green};transition:width .3s"></div></div>
      <div id="tb-stats" style="display:flex;justify-content:space-between;color:${C.mute};font-size:12px;margin:5px 0 10px"></div>
      <div style="font-weight:600;margin-bottom:3px">Links to capture <span id="tb-count" style="color:${C.mute};font-weight:400"></span></div>
      <textarea id="tb-q" rows="4" spellcheck="false" placeholder="Paste links here, one per line:&#10;• match pages&#10;• a series page&#10;• a team's season / results list&#10;• a player's stats page" style="width:100%;box-sizing:border-box;${INP};font:11px ui-monospace,monospace;resize:vertical"></textarea>
      <div style="display:flex;gap:6px;margin:8px 0 6px">${B("tb-go", "▶ Start", C.green, "flex:2")}${B("tb-stop", "■ Stop", C.red, "flex:1")}</div>
      <div style="display:flex;gap:6px">${B("tb-add", "＋ Add links from this page", C.card, "flex:2;border:1px solid " + C.line)}${B("tb-clear", "Clear queue", C.card, "flex:1;border:1px solid " + C.line)}</div>
      <div id="tb-optt" style="margin:10px 0 4px;color:${C.mute};cursor:pointer;font-size:12px">▸ Options</div>
      <div id="tb-opts" style="display:none;border:1px solid ${C.line};border-radius:8px;padding:8px;margin-bottom:6px">
        <label style="display:block;margin-bottom:6px">Max matches per run <input id="tb-max" type="number" min="1" max="100" style="width:56px;${INP}"></label>
        <label style="display:block;margin-bottom:6px">Only from year <input id="tb-since" type="number" style="width:70px;${INP}"> <span style="color:${C.mute}">(0 = all)</span></label>
        <label style="display:block;margin-bottom:8px"><input id="tb-lists" type="checkbox"> also save series / list pages (for audits)</label>
        <div style="border-top:1px solid ${C.line};margin:2px 0 8px;padding-top:8px">
          <label style="display:block;margin-bottom:4px"><input id="tb-auto" type="checkbox"> <b>Auto-resume</b> (keeps going while you sleep)</label>
          <div style="color:${C.mute};font-size:11px;margin:0 0 6px 20px">After the run limit it rests, then carries on; after a human-check page it waits 20, 45 then 90 minutes and tries again, then stops for you.</div>
          <label style="display:block;margin:0 0 6px 20px">Rest between runs <input id="tb-cool" type="number" min="5" max="240" style="width:56px;${INP}"> min</label>
          <label style="display:block;margin-bottom:2px"><input id="tb-awake" type="checkbox"> Keep this computer awake while running</label>
          <div style="color:${C.mute};font-size:11px;margin:0 0 4px 20px">Keep the laptop plugged in and the lid open, and leave this tab in its own window.</div>
        </div>
        <div style="display:flex;gap:6px;flex-wrap:wrap">${B("tb-page", "Save this page", C.card, "border:1px solid " + C.line)}${B("tb-known", "Import known ids", C.card, "border:1px solid " + C.line)}${B("tb-low", "Redo low captures", C.card, "border:1px solid " + C.line)}${B("tb-reset", "Forget done", C.card, "border:1px solid " + C.red + ";color:#fca5a5")}</div></div>
      <div id="tb-logt" style="margin:8px 0 4px;color:${C.mute};cursor:pointer;font-size:12px">▾ Activity</div>
      <pre id="tb-log" style="height:130px;overflow:auto;margin:0;padding:6px 8px;background:${C.card};border-radius:8px;font:11px/1.45 ui-monospace,monospace;white-space:pre-wrap;color:${C.text}"></pre>
      <div style="display:flex;justify-content:space-between;margin-top:4px"><span style="color:${C.mute};font-size:11px">One .json file is downloaded per match.</span><a id="tb-clog" href="#" style="color:${C.mute};font-size:11px">clear log</a></div>
    </div>`;
  const $ = (id) => box.querySelector("#" + id);
  const lines = (t) => t.split(/\s+/).filter((x) => /^https?:/.test(x));
  const render = (s) => {
    const left = Math.max(0, s.queue.length - s.idx), done = Object.keys(s.done || {}).length, ran = (s.results || []).length;
    const paused = s.running && s.pausedUntil > Date.now();
    const chip = $("tb-chip"); chip.textContent = paused ? "RESTING" : s.running ? "RUNNING" : left ? "STOPPED" : "IDLE"; chip.style.background = paused ? C.blue : s.running ? C.green : left ? C.amber : C.line;
    $("tb-go").textContent = s.running ? "● Running…" : (s.started && left ? "▶ Resume" : "▶ Start"); $("tb-go").disabled = s.running; $("tb-go").style.opacity = s.running ? .6 : 1;
    $("tb-stop").disabled = !s.running; $("tb-stop").style.opacity = s.running ? 1 : .45;
    $("tb-now").textContent = s.now ? (s.running ? "Now: " : "") + s.now : (s.running ? "Starting…" : "Not running");
    const total = s.queue.length || 1; $("tb-bar").style.width = Math.min(100, Math.round(100 * (s.queue.length ? s.idx / total : 0))) + "%";
    $("tb-stats").innerHTML = `<span>Queue: <b style="color:${C.text}">${left}</b> left of ${s.queue.length}</span><span>This run: <b style="color:${C.text}">${ran}</b>/${s.max}</span><span>Done ever: <b style="color:${C.text}">${done}</b></span>`;
    $("tb-count").textContent = `(${lines($("tb-q").value).length} links)`;
    const l = $("tb-log"); l.textContent = (s.log || []).slice(-60).join("\n"); l.scrollTop = 1e9;
    $("tb-body").style.display = s.ui.min ? "none" : "block"; $("tb-min").textContent = s.ui.min ? "+" : "–"; $("tb-opts").style.display = s.ui.opts ? "block" : "none"; $("tb-optt").textContent = (s.ui.opts ? "▾" : "▸") + " Options";
    l.style.display = s.ui.log ? "block" : "none"; $("tb-logt").textContent = (s.ui.log ? "▾" : "▸") + " Activity";
  };
  const start = async () => {
    document.body.appendChild(box); let s = await get();
    $("tb-q").value = s.queue.slice(s.idx).join("\n"); $("tb-max").value = s.max; $("tb-since").value = s.since || 0; $("tb-lists").checked = !!s.saveLists; $("tb-auto").checked = !!s.auto; $("tb-cool").value = s.cool || 20; $("tb-awake").checked = s.keepAwake !== false; render(s);
    const saveOpts = async () => { const t = await get(); t.auto = $("tb-auto").checked; t.cool = Math.min(240, Math.max(5, +$("tb-cool").value || 20)); t.keepAwake = $("tb-awake").checked; await setOpts(t); heartbeat(); };   // applies at once, even mid-run
    $("tb-auto").onchange = $("tb-cool").onchange = $("tb-awake").onchange = saveOpts;
    setInterval(heartbeat, 45000); heartbeat();
    $("tb-q").oninput = () => render(s);
    const ui = async (k) => { s = await get(); s.ui[k] = !s.ui[k]; await set(s); render(s); };
    $("tb-head").onclick = () => ui("min"); $("tb-optt").onclick = () => ui("opts"); $("tb-logt").onclick = () => ui("log");
    $("tb-go").onclick = async () => {
      s = await get(); const typed = lines($("tb-q").value); stopFlag = false; window.__ttmStop = false;
      const same = typed.join("\n") === s.queue.slice(s.idx).join("\n");                       // unchanged text = resume where we stopped; edited text = new queue
      const q = same ? s.queue : typed.filter((u) => !(s.done[doneKey(u)] && s.done[doneKey(u)].schema === SCHEMA));
      Object.assign(s, { queue: q, idx: same ? s.idx : 0, tab: 0, plan: null, running: q.length > 0, started: q.length > 0, results: same ? s.results : [], max: Math.min(100, +$("tb-max").value || MAX_DEFAULT), since: +$("tb-since").value || 0, saveLists: $("tb-lists").checked, pausedUntil: 0, resumeUrl: null, blockTries: 0, navTries: 0, errs: 0, auto: $("tb-auto").checked, cool: Math.min(240, Math.max(5, +$("tb-cool").value || 20)), keepAwake: $("tb-awake").checked });
      await setOpts(s);
      if (!q.length) { await log(s, "Nothing to do: the queue is empty (or everything in it is already done)."); return; }
      await log(s, `${same ? "RESUME" : "START"}: ${q.length - s.idx} to capture, up to ${s.max} this run${s.auto ? ", auto-resume ON" : ""}`); heartbeat(); step();
    };
    $("tb-stop").onclick = async () => { stopFlag = true; window.__ttmStop = true; s = await get(); s.running = false; s.now = ""; s.pausedUntil = 0; s.resumeUrl = null; await log(s, `Stopped. ${Math.max(0, s.queue.length - s.idx)} still queued: press Resume to continue, or Clear queue.`); };
    $("tb-clear").onclick = async () => { stopFlag = true; window.__ttmStop = true; s = await get(); Object.assign(s, { pausedUntil: 0, resumeUrl: null, running: false, started: false, queue: [], idx: 0, tab: 0, plan: null, now: "", results: [] }); $("tb-q").value = ""; await log(s, "Queue cleared."); };
    $("tb-add").onclick = async () => { s = await get(); const ls = links(isSeries(location.href) ? location.href : null); const cur = lines($("tb-q").value); const all = [...new Set(cur.concat(ls.map((x) => x.url)))]; $("tb-q").value = all.join("\n"); await log(s, `Added ${all.length - cur.length} new links from this page (${ls.length} found).`); render(s); };
    $("tb-page").onclick = async () => { const n = await savePage("page"); s = await get(); await log(s, `Saved this page (${n} tables).`); };
    $("tb-known").onclick = async () => { const txt = prompt("Paste the JSON printed by `python3 -m dataops.store known`"); if (!txt) return; s = await get();
      try { const j = JSON.parse(txt); let n = 0; for (const [site, ids] of Object.entries(j)) for (const id of ids) { s.done[`${site}:${id}`] = { at: "repo", schema: SCHEMA }; n++; } await log(s, `Imported ${n} ids we already hold: they will be skipped.`); } catch (e) { alert("That is not valid JSON."); } };
    $("tb-low").onclick = async () => {                                                            // matches saved with too few balls (older versions marked them done): forget them and queue the ones whose link we kept
      s = await get(); const low = Object.entries(s.done).filter(([k, v]) => v && v.balls !== undefined && (v.balls < 150 || v.incomplete) && v.hasCommentary !== false && !v.missing && v.found === undefined && v.tables === undefined);
      let queued = 0; const lost = [];
      for (const [k, v] of low) { delete s.done[k]; if (v.url) { s.queue.push(v.url); queued++; } else lost.push(k.split(":")[1]); }
      if (queued) { s.started = true; if (s.idx > s.queue.length) s.idx = s.queue.length - queued; }
      await log(s, `Redo low captures: ${low.length} found, ${queued} queued again${lost.length ? `; add these links by hand (no link was kept): ${lost.join(", ")}` : ""}.`); $("tb-q").value = s.queue.slice(s.idx).join("\n"); render(s); };
    $("tb-reset").onclick = async () => { if (!confirm("Forget which matches are done in this browser? (the repo's own index is not affected)")) return; s = await get(); s.done = {}; await log(s, "Done-list cleared."); };
    $("tb-clog").onclick = async (e) => { e.preventDefault(); s = await get(); s.log = []; await set(s); render(s); };
    if (s.running) { stopFlag = false; step(); }                                                    // resume after a page load
  };
  if (document.body) start(); else document.addEventListener("DOMContentLoaded", start);
})();
