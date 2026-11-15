// Batch mode: works through a list of match links in YOUR browser tab, one at a time, at a human pace.
// For each match it opens the commentary, scorecard and statistics tabs, loads all commentary and saves one JSON (the same file the manual
// "Save JSON" makes). On a series/results list page it can save the list (match links + result text) or add all its match links to the queue.
// It only clicks what a person would (load more, tabs) and stops by itself on a captcha / access-denied page. State lives in chrome.storage.local.
(() => {
  const SITE = /cricbuzz/.test(location.hostname) ? "cricbuzz" : "cricinfo";
  const TABS = SITE === "cricinfo" ? ["ball-by-ball-commentary", "full-scorecard", "match-statistics"] : ["live-cricket-full-commentary", "live-cricket-scorecard"];   // tab slugs: adjust here if the site renames them
  const MAX_DEFAULT = 20, DELAY = [4000, 9000], BETWEEN = [12000, 25000];
  const rnd = ([a, b]) => a + Math.random() * (b - a);
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const get = () => new Promise((r) => chrome.storage.local.get("ttm_batch", (v) => r(v.ttm_batch || { running: false, queue: [], idx: 0, tab: 0, max: MAX_DEFAULT, log: [], results: [] })));
  const set = (s) => new Promise((r) => chrome.storage.local.set({ ttm_batch: s }, r));
  const idOf = (u) => { try { const x = new URL(u, location.href); return SITE === "cricinfo" ? ((x.pathname.match(/-(\d+)\/?(?:[^/]*)$/) || [])[1]) : ((x.pathname.match(/\/(\d{4,})\//) || [])[1]); } catch (e) { return null; } };
  const tabUrl = (u, i) => {
    const x = new URL(u, location.href);
    if (SITE === "cricinfo") { const m = x.pathname.match(/^(\/series\/[^/]+\/[^/]+-\d+)/); return m ? `${x.origin}${m[1]}/${TABS[i]}` : u; }
    const m = x.pathname.match(/^\/[a-z-]+\/(\d{4,})\/([^/?#]+)/); return m ? `${x.origin}/${TABS[i]}/${m[1]}/${m[2]}` : u;
  };
  const blocked = () => /access denied|captcha|unusual traffic|are you a robot|just a moment|verify you are human/i.test(document.title + " " + (document.body ? document.body.innerText.slice(0, 600) : ""));
  const log = async (s, msg) => { s.log.push(new Date().toISOString().slice(11, 19) + " " + msg); s.log = s.log.slice(-60); await set(s); render(s); };

  // ---------- list pages: collect match links
  const matchLinks = () => {
    const out = new Map();
    for (const a of document.querySelectorAll("a[href]")) {
      const h = a.href; const ok = SITE === "cricinfo" ? /\/series\/[^/]+\/[^/]+-\d+\/(full-scorecard|live-cricket-score|match-report|ball-by-ball-commentary)?/.test(h) : /\/live-cricket-(scores|scorecard|full-commentary)\/\d+\//.test(h);
      if (!ok) continue; const id = idOf(h); if (!id) continue;
      const row = a.closest("tr, li, div[class*=match], div[class*=card]") || a.parentElement;
      if (!out.has(id)) out.set(id, { id, url: h.split("#")[0], text: (row ? row.innerText : a.innerText).replace(/\s+/g, " ").trim().slice(0, 300) });
    }
    return [...out.values()];
  };

  // ---------- any other page (player profile, Statsguru / records tables, results lists): save its data as one JSON
  const savePage = () => {
    let nd = null; try { const el = document.getElementById("__NEXT_DATA__"); nd = el ? JSON.parse(el.textContent) : null; } catch (e) {}
    const tables = [...document.querySelectorAll("table")].slice(0, 40).map((t) => [...t.rows].map((r) => [...r.cells].map((c) => c.innerText.trim())));
    const out = { site: SITE, page_url: location.href, title: document.title, saved_at: new Date().toISOString(), next_data: nd, tables, text: (document.querySelector("main") || document.body).innerText.slice(0, 1_500_000), links: matchLinks() };
    const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([JSON.stringify(out)], { type: "application/json" }));
    a.download = `page_${SITE}_${(location.pathname + location.search).replace(/[^a-z0-9]+/gi, "_").slice(0, 80)}.json`; document.body.appendChild(a); a.click(); a.remove();
    return tables.length;
  };

  // ---------- state machine, runs on every page load
  const step = async () => {
    const s = await get(); if (!s.running) return render(s);
    if (blocked()) { s.running = false; await log(s, "STOPPED: the site is asking for a human check. Solve it in the tab, then press Start again."); return; }
    const job = s.queue[s.idx]; if (!job) { s.running = false; await log(s, `DONE: ${s.results.length} matches saved.`); return; }
    const jobId = idOf(job); const here = idOf(location.href);
    if (!jobId) {                                                          // not a match link: a profile / stats / list page, saved as is
      if (location.href.split("#")[0] !== job.split("#")[0]) { await log(s, `opening ${s.idx + 1}/${s.queue.length}: page`); await sleep(rnd(DELAY)); location.assign(job); return; }
      await sleep(rnd(DELAY)); const n = savePage(); s.results.push({ id: job, url: job, tables: n, at: new Date().toISOString() }); s.idx++; s.tab = 0;
      await log(s, `  SAVED page (${n} tables)`);
      if (s.idx >= Math.min(s.queue.length, s.max)) { s.running = false; await log(s, `DONE: ${s.results.length} saved.`); return; }
      await sleep(rnd(BETWEEN)); location.assign(s.queue[s.idx]); return;
    }
    if (here !== jobId) {                                                   // not on the job's match yet: go there
      await log(s, `opening ${s.idx + 1}/${s.queue.length}: ${jobId}`); await sleep(rnd(DELAY)); location.assign(tabUrl(job, s.tab || 0)); return;
    }
    const T = window.__ttm; if (!T) { await sleep(2000); return step(); }
    await sleep(rnd(DELAY));
    const tabName = TABS[s.tab || 0]; await log(s, `match ${jobId}: ${tabName}`);
    if (/commentary/.test(tabName)) {
      let n = await T.loadAll();
      const inn = [...document.querySelectorAll("[role=tab], button")].filter((b) => b.offsetParent && /innings|\binn\b|^\s*\d+(st|nd|rd|th)\b/i.test(b.textContent || "") && b.getAttribute("aria-selected") !== "true");
      for (const b of inn.slice(0, 3)) { b.click(); await sleep(2500); n = await T.loadAll(); }          // switch innings where the page offers tabs for them
      await log(s, `  ${n} balls so far`);
    } else { await sleep(3000); T.grabText(); T.save(); }
    if ((s.tab || 0) + 1 < TABS.length) { s.tab = (s.tab || 0) + 1; await set(s); await sleep(rnd(DELAY)); location.assign(tabUrl(job, s.tab)); return; }
    const balls = T.saveJson();                                            // all tabs visited: one JSON file for the match
    s.results.push({ id: jobId, url: job, balls, at: new Date().toISOString() }); s.idx++; s.tab = 0;
    await log(s, `  SAVED ${jobId}: ${balls} balls${balls < 150 ? "  (LOW: check the commentary loaded)" : ""}`);
    if (s.idx >= Math.min(s.queue.length, s.max)) { s.running = false; await log(s, `DONE: ${s.results.length} matches saved (cap ${s.max}).`); return; }
    await sleep(rnd(BETWEEN)); location.assign(tabUrl(s.queue[s.idx], 0));
  };

  // ---------- panel
  const box = document.createElement("div");
  box.style.cssText = "position:fixed;left:16px;bottom:16px;z-index:2147483647;background:#101a33;color:#fff;font:12px/1.4 system-ui,sans-serif;padding:10px 12px;border-radius:10px;box-shadow:0 6px 24px rgba(0,0,0,.35);width:270px";
  box.innerHTML = `<div style="font-weight:700;margin-bottom:4px">Third Man batch</div>
    <textarea id="tb-q" rows="4" placeholder="one match link per line" style="width:100%;box-sizing:border-box;font:11px monospace"></textarea>
    <div style="display:flex;gap:4px;margin:4px 0"><button id="tb-go" style="flex:1;background:#e63946;color:#fff;border:0;border-radius:6px;padding:5px;font-weight:700;cursor:pointer">Start</button><button id="tb-stop" style="flex:1;background:#2a3b6b;color:#fff;border:0;border-radius:6px;padding:5px;cursor:pointer">Stop</button></div>
    <div style="display:flex;gap:4px;margin-bottom:4px"><button id="tb-add" style="flex:1;background:#2a3b6b;color:#fff;border:0;border-radius:6px;padding:5px;cursor:pointer">Add links on this page</button><button id="tb-list" style="flex:1;background:#2a3b6b;color:#fff;border:0;border-radius:6px;padding:5px;cursor:pointer">Save this list</button><button id="tb-page" style="flex:1;background:#2a3b6b;color:#fff;border:0;border-radius:6px;padding:5px;cursor:pointer">Save this page</button></div>
    <label style="opacity:.8">max per run <input id="tb-max" type="number" value="${MAX_DEFAULT}" min="1" max="60" style="width:46px"></label>
    <pre id="tb-log" style="max-height:110px;overflow:auto;margin:6px 0 0;font-size:10px;white-space:pre-wrap;opacity:.85"></pre>`;
  const render = (s) => { const l = box.querySelector("#tb-log"); if (l) { l.textContent = (s.log || []).slice(-12).join("\n"); l.scrollTop = 1e9; } };
  const start = async () => {
    document.body.appendChild(box); const s = await get();
    box.querySelector("#tb-q").value = s.queue.join("\n"); box.querySelector("#tb-max").value = s.max || MAX_DEFAULT; render(s);
    box.querySelector("#tb-go").onclick = async () => {
      const q = box.querySelector("#tb-q").value.split(/\s+/).filter((x) => /^https?:/.test(x)); const t = await get();
      Object.assign(t, { queue: q, idx: 0, tab: 0, running: q.length > 0, max: Math.min(60, +box.querySelector("#tb-max").value || MAX_DEFAULT), results: [] });
      await log(t, `START: ${q.length} matches (cap ${t.max})`); step();
    };
    box.querySelector("#tb-stop").onclick = async () => { const t = await get(); t.running = false; await log(t, "stopped by you"); };
    box.querySelector("#tb-add").onclick = async () => { const ls = matchLinks(); const q = box.querySelector("#tb-q"); q.value = [...new Set((q.value.split(/\s+/).filter(Boolean)).concat(ls.map((x) => x.url)))].join("\n"); const t = await get(); await log(t, `added ${ls.length} links`); };
    box.querySelector("#tb-list").onclick = () => {                         // the list itself (match links + the result text of each row), for the coverage audit
      const out = { site: SITE, page_url: location.href, title: document.title, saved_at: new Date().toISOString(), matches: matchLinks() };
      const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([JSON.stringify(out)], { type: "application/json" }));
      a.download = `list_${SITE}_${location.pathname.replace(/[^a-z0-9]+/gi, "_").slice(0, 60)}.json`; document.body.appendChild(a); a.click(); a.remove();
    };
    box.querySelector("#tb-page").onclick = () => savePage();
    if (s.running) step();                                                  // resume after a page load
  };
  if (document.body) start(); else document.addEventListener("DOMContentLoaded", start);
})();
