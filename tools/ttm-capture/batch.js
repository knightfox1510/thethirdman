// Batch + crawl mode (v1.3): works through a queue of links in YOUR browser tab, one at a time, at a human pace.
// Queue items are detected by their link: a MATCH (opens scorecard, playing XI, commentary, statistics; saves one JSON), a SERIES page (collects its match links and
// queues them), a LIST page such as a team's season view (queues its series), or any other page (player stats, records tables: saved as one JSON, with each stat tab/filter).
// Nothing is captured twice: finished matches/series are remembered in the browser (chrome.storage) and you can paste the ids we already hold (python3 -m dataops.store known).
(() => {
  const SITE = /cricbuzz/.test(location.hostname) ? "cricbuzz" : "cricinfo";
  const SCHEMA = 3;                                                     // bump when the capture gains new tabs/fields: older captures are then re-done once
  const TABS = SITE === "cricinfo"
    ? { score: "full-scorecard", xi: "match-playing-xi", comm: "ball-by-ball-commentary", stats: "match-statistics" }
    : { score: "live-cricket-scorecard", comm: "live-cricket-full-commentary" };       // tab slugs: adjust here if a site renames them
  const MAX_DEFAULT = 20, DELAY = [4000, 9000], BETWEEN = [12000, 25000];
  const rnd = ([a, b]) => a + Math.random() * (b - a);
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const blank = () => ({ running: false, queue: [], idx: 0, tab: 0, plan: null, max: MAX_DEFAULT, since: 0, log: [], results: [], done: {} });
  const get = () => new Promise((r) => chrome.storage.local.get("ttm_batch", (v) => r(Object.assign(blank(), v.ttm_batch || {}))));
  const set = (s) => new Promise((r) => chrome.storage.local.set({ ttm_batch: s }, r));
  const clean = (u) => String(u).split("#")[0];
  const matchId = (u) => { try { const x = new URL(u, location.href); const p = x.pathname;
    if (SITE === "cricinfo") { if (/\/series\/[^/]+\/[^/]+-\d+(\/|$)/.test(p)) return (p.match(/\/series\/[^/]+\/[^/]+-(\d+)/) || [])[1]; const o = p.match(/\/(?:ci\/engine\/)?match\/(\d+)\.html/); return o ? o[1] : null; }
    return (p.match(/\/(?:live-cricket-[a-z-]+|cricket-scores?)\/(\d{4,})\//) || [])[1] || null; } catch (e) { return null; } };
  const isSeries = (u) => { try { const p = new URL(u, location.href).pathname; return SITE === "cricinfo" ? (/\/series\/[^/]+-\d+\/?(match-results|match-schedule-fixtures-and-results|squads)?\/?$/.test(p) || /\/ci\/engine\/series\/\d+\.html/.test(p)) && !matchId(u) : /\/cricket-series\/\d+\//.test(p); } catch (e) { return false; } };
  const kind = (u) => matchId(u) ? "match" : isSeries(u) ? "series" : /index\.html\?.*view=season|\/team\/[^/]+\/(match-results|series)|match-results|series-results/.test(u) ? "list" : "page";
  const doneKey = (u) => SITE + ":" + (matchId(u) || clean(u));
  const tabUrl = (u, name) => { const x = new URL(u, location.href);
    if (SITE === "cricinfo") { const m = x.pathname.match(/^(\/series\/[^/]+\/[^/]+-\d+)/); return m ? `${x.origin}${m[1]}/${name}` : u; }
    const m = x.pathname.match(/^\/[a-z-]+\/(\d{4,})\/([^/?#]+)/); return m ? `${x.origin}/${name}/${m[1]}/${m[2]}` : u; };
  const blocked = () => /access denied|captcha|unusual traffic|are you a robot|just a moment|verify you are human/i.test(document.title + " " + (document.body ? document.body.innerText.slice(0, 600) : ""));
  const notFound = () => /page not found|404|can't find|couldn't find/i.test(document.title);
  const log = async (s, msg) => { s.log.push(new Date().toISOString().slice(11, 19) + " " + msg); s.log = s.log.slice(-80); await set(s); render(s); };

  const links = () => {                                                  // every match / series link on the page, with its row text
    const out = new Map();
    for (const a of document.querySelectorAll("a[href]")) {
      const h = clean(a.href); const k = kind(h); if (k !== "match" && k !== "series") continue;
      const id = k === "match" ? matchId(h) : h; const row = a.closest("tr, li, div[class*=match], div[class*=card]") || a.parentElement;
      if (!out.has(k + id)) out.set(k + id, { kind: k, id, url: h, text: (row ? row.innerText : a.innerText).replace(/\s+/g, " ").trim().slice(0, 300) });
    } return [...out.values()];
  };
  const yearOf = (t) => { const m = (t || "").match(/\b(19\d\d|20\d\d)\b/); return m ? +m[1] : 0; };

  const savePage = async () => {                                         // any other page: tables, page data, text, links; stats pages: every format tab / filter too
    const grab = () => ({ tables: [...document.querySelectorAll("table")].slice(0, 60).map((t) => [...t.rows].map((r) => [...r.cells].map((c) => c.innerText.trim()))), text: (document.querySelector("main") || document.body).innerText.slice(0, 600000) });
    let nd = null; try { const el = document.getElementById("__NEXT_DATA__"); nd = el ? JSON.parse(el.textContent) : null; } catch (e) {}
    const out = { site: SITE, schema: SCHEMA, page_url: location.href, title: document.title, saved_at: new Date().toISOString(), next_data: nd, ...grab(), links: links(), views: {} };
    if (/stats|records|statsguru|career/i.test(location.href)) {                                           // click through the tabs / filters a person would (Tests, ODIs, T20Is, IPL ...)
      const tabs = [...document.querySelectorAll("[role=tab], button, a")].filter((b) => b.offsetParent && /^(tests?|odis?|t20is?|t20|ipl|first[- ]class|list a|batting|bowling|fielding|all)$/i.test((b.textContent || "").trim())).slice(0, 14);
      for (const b of tabs) { try { b.click(); await sleep(2500); out.views[(b.textContent || "").trim()] = grab(); } catch (e) {} }
    }
    const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([JSON.stringify(out)], { type: "application/json" }));
    a.download = `page_${SITE}_${(location.pathname + location.search).replace(/[^a-z0-9]+/gi, "_").slice(0, 80)}.json`; document.body.appendChild(a); a.click(); a.remove();
    return out.tables.length + Object.values(out.views).reduce((n, v) => n + v.tables.length, 0);
  };

  const enqueue = (s, items, front) => {                                 // adds links not already done / queued, newest first as listed
    const have = new Set(s.queue.map((u) => doneKey(u)));
    const fresh = items.filter((u) => !s.done[doneKey(u)] && !have.has(doneKey(u)) && (!s.since || !yearOf(u.text) || yearOf(u.text) >= s.since)).map((u) => u.url);
    if (front) s.queue.splice(s.idx + 1, 0, ...fresh); else s.queue.push(...fresh);
    return fresh.length;
  };
  const finish = async (s, msg) => { s.running = false; await log(s, msg); };
  const next = async (s, extraWait = 0) => {
    if (s.idx >= s.queue.length || s.results.length >= s.max) return finish(s, `DONE: ${s.results.length} captured this run (cap ${s.max}), ${Math.max(0, s.queue.length - s.idx)} still queued. Press Start to continue later.`);
    await sleep(rnd(BETWEEN) + extraWait); location.assign(s.queue[s.idx]);
  };

  const step = async () => {
    const s = await get(); if (!s.running) return render(s);
    if (blocked()) return finish(s, "STOPPED: the site is asking for a human check. Solve it in the tab, then press Start again.");
    const job = s.queue[s.idx]; if (!job) return finish(s, `DONE: ${s.results.length} captured.`);
    const k = kind(job), key = doneKey(job);
    if (s.done[key] && s.done[key].schema === SCHEMA && !s.force) { s.idx++; s.tab = 0; s.plan = null; await set(s); return next(s); }      // already captured: skip
    const here = clean(location.href), target = k === "match" ? matchId(job) : clean(job);
    const onTarget = k === "match" ? matchId(here) === target : here === clean(job) || (k !== "match" && here.split("?")[0] === clean(job).split("?")[0]);
    if (!onTarget) { await log(s, `open ${s.idx + 1}/${s.queue.length} [${k}]`); await sleep(rnd(DELAY)); location.assign(k === "match" ? tabUrl(job, TABS.score) : job); return; }
    await sleep(rnd(DELAY));
    if (notFound()) { s.done[key] = { at: new Date().toISOString(), schema: SCHEMA, missing: true }; s.idx++; s.tab = 0; s.plan = null; await log(s, "  page not found: skipped"); return next(s); }

    if (k === "list" || k === "series") {                                              // collect the next level down
      for (let i = 0; i < 4; i++) { window.scrollTo(0, document.body.scrollHeight); await sleep(1200); }
      const ls = links(); const sub = ls.filter((x) => k === "list" ? x.kind === "series" : x.kind === "match");
      const n = enqueue(s, sub, true); await savePage();
      s.done[key] = { at: new Date().toISOString(), schema: SCHEMA, found: sub.length }; s.idx++; s.tab = 0;
      await log(s, `  ${k}: ${sub.length} links, ${n} new queued`); return next(s);
    }
    if (k === "page") {
      const n = await savePage(); s.done[key] = { at: new Date().toISOString(), schema: SCHEMA, tables: n }; s.results.push({ id: key }); s.idx++;
      await log(s, `  SAVED page (${n} tables)`); return next(s);
    }
    // ---- a match
    const T = window.__ttm; if (!T) { await sleep(2500); return step(); }
    if (!s.plan) s.plan = Object.keys(TABS);                                           // scorecard first, then the rest, decided by what the match has
    const name = s.plan[s.tab || 0]; await log(s, `match ${target}: ${name}`);
    if (name === "comm") {
      const mt = T.meta(); if (mt && mt.hasCommentary === false) await log(s, "  no ball-by-ball for this match: skipped");
      else { let n = await T.loadAll();
        const inn = [...document.querySelectorAll("[role=tab], button")].filter((b) => b.offsetParent && /innings|\binn\b/i.test(b.textContent || "") && b.getAttribute("aria-selected") !== "true");
        for (const b of inn.slice(0, 3)) { b.click(); await sleep(2500); n = await T.loadAll(); } await log(s, `  ${n} balls so far`); }
    } else { await sleep(2500); T.grabText(); T.save(); }
    if ((s.tab || 0) + 1 < s.plan.length) { s.tab = (s.tab || 0) + 1; await set(s); await sleep(rnd(DELAY)); location.assign(tabUrl(job, TABS[s.plan[s.tab]])); return; }
    const mt = T.meta() || {}; const balls = T.saveJson();
    s.done[key] = { at: new Date().toISOString(), schema: SCHEMA, balls, state: mt.state || null, hasMatchPlayers: !!mt.hasMatchPlayers };
    s.results.push({ id: key, balls }); s.idx++; s.tab = 0; s.plan = null;
    await log(s, `  SAVED ${target}: ${balls} balls${mt.hasCommentary && balls < 150 ? "  (LOW: check the commentary loaded)" : ""}${mt.state && mt.state !== "POST" ? "  (match not finished: will be re-done later)" : ""}`);
    if (mt.state && mt.state !== "POST") delete s.done[key];                           // live / incomplete matches are never marked done
    return next(s);
  };

  // ---------- panel
  const box = document.createElement("div");
  box.style.cssText = "position:fixed;left:16px;bottom:16px;z-index:2147483647;background:#101a33;color:#fff;font:12px/1.4 system-ui,sans-serif;padding:10px 12px;border-radius:10px;box-shadow:0 6px 24px rgba(0,0,0,.35);width:290px";
  const btn = (id, label, bg = "#2a3b6b") => `<button id="${id}" style="flex:1;background:${bg};color:#fff;border:0;border-radius:6px;padding:5px;cursor:pointer">${label}</button>`;
  box.innerHTML = `<div style="font-weight:700;margin-bottom:4px">Third Man batch <span id="tb-n" style="opacity:.6;font-weight:400"></span></div>
    <textarea id="tb-q" rows="3" placeholder="links, one per line: matches, series, a team's season view, player stats pages" style="width:100%;box-sizing:border-box;font:11px monospace"></textarea>
    <div style="display:flex;gap:4px;margin:4px 0">${btn("tb-go", "Start", "#e63946")}${btn("tb-stop", "Stop")}${btn("tb-add", "Queue links on this page")}</div>
    <div style="display:flex;gap:4px;margin-bottom:4px">${btn("tb-page", "Save this page")}${btn("tb-known", "Import known ids")}${btn("tb-reset", "Forget done")}</div>
    <label style="opacity:.8">max per run <input id="tb-max" type="number" value="${MAX_DEFAULT}" min="1" max="100" style="width:44px"></label>
    <label style="opacity:.8;margin-left:6px">from year <input id="tb-since" type="number" value="0" style="width:52px"></label>
    <pre id="tb-log" style="max-height:120px;overflow:auto;margin:6px 0 0;font-size:10px;white-space:pre-wrap;opacity:.85"></pre>`;
  const render = (s) => { const l = box.querySelector("#tb-log"); if (l) { l.textContent = (s.log || []).slice(-14).join("\n"); l.scrollTop = 1e9; }
    const n = box.querySelector("#tb-n"); if (n) n.textContent = `${Object.keys(s.done || {}).length} done · ${Math.max(0, (s.queue || []).length - (s.idx || 0))} queued`; };
  const start = async () => {
    document.body.appendChild(box); const s = await get(); box.querySelector("#tb-q").value = s.queue.slice(s.idx).join("\n"); box.querySelector("#tb-max").value = s.max; box.querySelector("#tb-since").value = s.since || 0; render(s);
    const q = () => box.querySelector("#tb-q");
    box.querySelector("#tb-go").onclick = async () => {
      const t = await get(); const typed = q().value.split(/\s+/).filter((x) => /^https?:/.test(x));
      Object.assign(t, { queue: typed, idx: 0, tab: 0, plan: null, running: typed.length > 0, results: [], max: Math.min(100, +box.querySelector("#tb-max").value || MAX_DEFAULT), since: +box.querySelector("#tb-since").value || 0, force: false });
      await log(t, `START: ${typed.length} queued, cap ${t.max}${t.since ? ", from " + t.since : ""}`); step();
    };
    box.querySelector("#tb-stop").onclick = async () => { const t = await get(); t.running = false; await log(t, "stopped by you"); };
    box.querySelector("#tb-add").onclick = async () => { const t = await get(); const ls = links(); q().value = [...new Set(q().value.split(/\s+/).filter(Boolean).concat(ls.map((x) => x.url)))].join("\n"); await log(t, `added ${ls.length} links from this page`); };
    box.querySelector("#tb-page").onclick = async () => { const n = await savePage(); const t = await get(); await log(t, `saved this page (${n} tables)`); };
    box.querySelector("#tb-known").onclick = async () => {                                    // ids already held by the repo: python3 -m dataops.store known
      const txt = prompt("Paste the JSON from `python3 -m dataops.store known`"); if (!txt) return; const t = await get();
      try { const j = JSON.parse(txt); let n = 0; for (const [site, ids] of Object.entries(j)) for (const id of ids) { t.done[`${site}:${id}`] = { at: "repo", schema: SCHEMA }; n++; } await log(t, `imported ${n} known ids`); } catch (e) { alert("not valid JSON"); } };
    box.querySelector("#tb-reset").onclick = async () => { if (!confirm("Forget which matches are done in this browser? (the repo's own index is unaffected)")) return; const t = await get(); t.done = {}; await log(t, "done-list cleared"); };
    if (s.running) step();                                                                  // resume after a page load
  };
  if (document.body) start(); else document.addEventListener("DOMContentLoaded", start);
})();
