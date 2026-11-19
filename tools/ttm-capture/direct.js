// Direct fetch module (v1.8.0). OPTIONAL and separate from the click-and-scroll capture: it asks Cricinfo's own JSON for the same data the page loads, from inside the match tab that is already open.
//   - the other tabs (playing XI, statistics, summary) are fetched as plain HTML and their __NEXT_DATA__ is stored exactly as if the tab had been opened (same keys, same shape);
//   - the ball-by-ball commentary is read through the same endpoint the page uses (/v1/pages/match/comments), innings by innings, following its own "nextInningOver" cursor to the end.
// No tab switching, no scrolling, no team dropdown (which is why Tests with four innings no longer depend on clicking "ENG 2nd Innings"). Requests are paced like the page's own scrolling.
// It never saves anything itself: it hands what it fetched to panel.js (window.__ttm.put / addApi), so the saved JSON has the same format as before. If anything fails, run() returns ok:false and
// batch.js falls back to the old way for that match. window.__ttm.direct.run(opts) -> { ok, blocked (HTTP 429), refused (the data API said 403: stop using direct fetch), notes[], tabs[], innings:[{n, want, got, ended}] }.
(() => {
  if (/cricbuzz/.test(location.hostname)) return;
  const sleep = (ms) => (window.__ttmSleep ? window.__ttmSleep(ms) : new Promise((r) => setTimeout(r, ms)));    // batch.js's timer: not throttled while the window is hidden
  const rnd = ([a, b]) => a + Math.random() * (b - a);
  const GAP = [450, 1000], LONG_EVERY = 20, LONG = [2000, 4000], MAX_PAGES = 400;
  const NEXT = /<script[^>]*id=["']__NEXT_DATA__["'][^>]*>([\s\S]*?)<\/script>/;

  const apiBase = (T) => { const h = T.apiHost && T.apiHost(); return h || "https://hs-consumer-api." + location.hostname.replace(/^www\./, ""); };
  const seriesId = (T) => (String(T.series || "").match(/-(\d+)$/) || [])[1];

  async function get(url, json, T) {                                  // one request, retried on slow server errors; a 403/429 means STOP (the site is asking us to slow down)
    let last = "";
    for (let attempt = 0; attempt < 4; attempt++) {
      if (window.__ttmStop) throw Object.assign(new Error("stopped"), { stopped: true });
      for (const cred of json ? ["omit", "include"] : ["same-origin"]) {
        try {
          const r = await fetch(url, { credentials: cred, headers: json ? { accept: "application/json" } : { accept: "text/html" } });
          if (r.status === 429) throw Object.assign(new Error("HTTP 429"), { blocked: true });                     // slow down: stop
          if (r.status === 403) { let say = ""; try { say = (await r.text()).replace(/\s+/g, " ").slice(0, 120); } catch (e) {} throw Object.assign(new Error(`HTTP 403 (${(r.headers.get("content-type") || "").split(";")[0]}) ${say}`), { refused: true }); }   // the server says no to this way of asking: we do NOT try other ways round it, we stop using it and the old way takes over
          if (r.status === 404) return { status: 404 };
          if (!r.ok) { last = "HTTP " + r.status; break; }
          return { status: 200, body: json ? await r.json() : await r.text() };
        } catch (e) { if (e.blocked || e.refused || e.stopped) throw e; last = (e && e.message) || String(e); }
      }
      await sleep(1500 * (attempt + 1) + rnd([0, 800]));
    }
    throw new Error(last || "request failed");
  }

  async function tab(T, slug, out) {                                  // a match tab as HTML: its __NEXT_DATA__ goes into the capture under the tab's slug, like grabNext() does on the open page
    const url = `${location.origin}/series/${T.series}/${T.matchSlug}/${slug}`;
    const r = await get(url, false, T);
    if (r.status === 404) { out.notes.push(`${slug}: no such page`); return false; }
    const m = NEXT.exec(r.body); if (!m) { out.notes.push(`${slug}: page has no embedded data`); return false; }
    let d; try { d = JSON.parse(m[1]); } catch (e) { out.notes.push(`${slug}: embedded data unreadable`); return false; }
    T.put(slug, d); out.tabs.push(slug); return true;
  }

  async function innings(T, n, out, gap) {                            // one innings of commentary: newest page first, then fromInningOver=<nextInningOver> until it is null
    const sid = seriesId(T), base = apiBase(T); let cursor = null, pages = 0, ended = false, calls = 0;
    while (pages < MAX_PAGES) {
      const url = `${base}/v1/pages/match/comments?lang=en&seriesId=${sid}&matchId=${T.matchId}&inningNumber=${n}&commentType=ALL&sortDirection=DESC` + (cursor !== null ? `&fromInningOver=${cursor}` : "");
      const r = await get(url, true, T); if (r.status === 404) break;
      T.addApi(url, r.body); pages++; calls++;
      const nx = r.body && r.body.nextInningOver;
      if (nx === null || nx === undefined) { ended = true; break; }
      if (cursor !== null && nx >= cursor) break;                      // the cursor must move back: anything else is a loop
      cursor = nx;
      await sleep(calls % LONG_EVERY === 0 ? rnd(LONG) : rnd(gap));
    }
    return ended;
  }

  async function run(opts = {}) {
    const T = window.__ttm, out = { ok: false, blocked: false, notes: [], tabs: [], innings: [] }, gap = opts.gap || GAP;
    try {
      if (!T || !T.put || !T.addApi || !T.check) { out.notes.push("panel too old for direct fetch"); return out; }
      const have = new Set((T.info().tabs) || []);
      for (const slug of opts.tabs || []) { if (have.has(slug)) continue; try { await tab(T, slug, out); } catch (e) { if (e.blocked || e.stopped) throw e; out.notes.push(`${slug}: ${e.message}`); } await sleep(rnd([300, 800])); }   // (a tab the server refuses is skipped; the old way can still open it)
      if (opts.commentary) {
        const want = T.check(); if (!want.length) { out.notes.push("no innings listed on the page: cannot tell what to fetch"); return out; }
        let allEnded = true;
        for (const w of want) {
          if (window.__ttmStop) throw Object.assign(new Error("stopped"), { stopped: true });
          let ended = await innings(T, w.n, out, gap);
          if (!ended) { await sleep(rnd([1500, 3000])); ended = await innings(T, w.n, out, gap); }                            // the cursor never reached its end (a failed page): one more full pass
          const g = T.check().find((x) => x.n === w.n); out.innings.push({ n: w.n, want: w.want, got: g ? g.got : 0, ended });
          if (!ended) allEnded = false;
        }
        await T.flush();
        out.ok = allEnded;
        const short = out.innings.filter((i) => i.got < i.want);
        if (short.length) out.notes.push("commentary is short of the scorecard's balls in innings " + short.map((i) => `${i.n} (${i.got}/${i.want})`).join(", ") + (allEnded ? ": the source ends there" : ""));
      } else { await T.flush(); out.ok = true; }
    } catch (e) { out.blocked = !!e.blocked; out.refused = !!e.refused; out.stopped = !!e.stopped; out.notes.push(e.message); out.ok = false; }
    return out;
  }

  const attach = () => { const T = window.__ttm; if (!T) return false; T.direct = { run, version: 1 }; return true; };
  if (!attach()) { let n = 0; const id = setInterval(() => { if (attach() || ++n > 300) clearInterval(id); }, 100); }
  if (typeof module !== "undefined") module.exports = { run, attach };
})();
