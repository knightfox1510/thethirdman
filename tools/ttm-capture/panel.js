// A small panel on Cricinfo and Cricbuzz match pages: collects what the page has loaded and saves it as JSON.
// Data is kept per match across the commentary / scorecard / statistics tabs (sessionStorage).
(() => {
  const SITE = /cricbuzz/.test(location.hostname) ? "cricbuzz" : "cricinfo";
  let m, matchSlug, matchId, series = null;
  if (SITE === "cricinfo") {
    m = location.pathname.match(/\/series\/([^/]+)\/([^/]+-(\d+))\/?([^/]*)/);
    if (!m) return;
    matchSlug = m[2]; matchId = m[3]; series = m[1];
  } else {
    // e.g. /live-cricket-full-commentary/161271/nz-vs-ind-4th-odi-... , /live-cricket-scorecard/161271/...
    m = location.pathname.match(/\/([a-z-]+)\/(\d{4,})\/([^/?#]+)/);
    if (!m) return;
    matchId = m[2]; matchSlug = m[3];
  }
  const tabNow = () => SITE === "cricinfo"
    ? ((location.pathname.match(/-\d+\/([^/]+)/) || [])[1] || "home")
    : ((location.pathname.match(/^\/([a-z-]+)\//) || [])[1] || "home");
  const KEY = "ttm_capture_" + SITE + "_" + matchId;

  // The capture is kept in IndexedDB, not sessionStorage: sessionStorage holds ~5 MB and its setItem failed silently once the scorecard / playing-XI pages and every API response
  // had been stored, so the commentary was lost on the next page load ("SAVED match: 0 balls"). IndexedDB has a far larger quota and stores the object as it is.
  const idb = () => new Promise((res, rej) => { const r = indexedDB.open("ttm_capture", 1); r.onupgradeneeded = () => r.result.createObjectStore("s"); r.onsuccess = () => res(r.result); r.onerror = () => rej(r.error); });
  const idbGet = async (k) => { try { const db = await idb(); return await new Promise((res) => { const q = db.transaction("s").objectStore("s").get(k); q.onsuccess = () => res(q.result || null); q.onerror = () => res(null); }); } catch (e) { return null; } };
  const idbPut = async (k, v) => { try { const db = await idb(); await new Promise((res) => { const t = db.transaction("s", "readwrite"); t.objectStore("s").put(v, k); t.oncomplete = res; t.onerror = res; t.onabort = res; }); return true; } catch (e) { return false; } };
  const idbDel = async (k) => { try { const db = await idb(); await new Promise((res) => { const t = db.transaction("s", "readwrite"); t.objectStore("s").delete(k); t.oncomplete = res; t.onerror = res; t.onabort = res; }); } catch (e) {} };
  // chrome.storage.local belongs to the EXTENSION, so it is shared by www.cricinfo.com and www.espncricinfo.com alike (sessionStorage and IndexedDB are per origin: a redirect between the two lost the capture)
  const hasExt = () => { try { return !!(chrome && chrome.storage && chrome.storage.local && chrome.runtime && chrome.runtime.id); } catch (e) { return false; } };
  const extGet = (k) => new Promise((res) => { try { chrome.storage.local.get(k, (v) => res((!chrome.runtime.lastError && v && v[k]) || null)); } catch (e) { res(null); } });
  const extPut = (k, v) => new Promise((res) => { try { chrome.storage.local.set({ [k]: v }, () => res(!chrome.runtime.lastError)); } catch (e) { res(false); } });
  const extDel = (k) => new Promise((res) => { try { chrome.storage.local.remove(k, () => res()); } catch (e) { res(); } });
  let mode = "memory", lastErr = "";
  const kvGet = async (k) => { let v = hasExt() ? await extGet(k) : null; if (v) { mode = "extension"; return v; } v = await idbGet(k); if (v) mode = "indexeddb"; return v; };
  const kvPut = async (k, v) => { if (hasExt() && await extPut(k, v)) { mode = "extension"; return true; } lastErr = "extension storage refused the write"; if (await idbPut(k, v)) { mode = "indexeddb"; return true; } mode = "memory"; lastErr = "no storage accepted the write"; return false; };
  const kvDel = async (k) => { if (hasExt()) await extDel(k); await idbDel(k); };
  let store = { site: SITE, match_id: matchId, match_slug: matchSlug, series, pages: {}, api: [], comments: {} };
  let ready = false, dirty = false, saving = null; const pending = [];
  const flush = async () => { if (!dirty && !saving) return; while (saving) await saving; if (!dirty) return; dirty = false; saving = kvPut(KEY, store).finally(() => { saving = null; }); await saving; };
  const save = () => { dirty = true; };                                       // cheap: the actual write is debounced (below) and awaited by flush() before any navigation / download
  setInterval(() => { if (dirty) flush(); }, 2000);
  window.addEventListener("pagehide", () => { if (dirty) flush(); });

  // Ball-by-ball items can arrive in several responses; keep them unique.
  const harvest = (o, depth = 0) => {
    if (!o || depth > 8) return;
    if (Array.isArray(o)) {
      for (const x of o) {
        if (x && typeof x === "object" && ("oversActual" in x || "ballNumber" in x) && ("bowlerPlayerId" in x || "batsmanPlayerId" in x || "totalRuns" in x)) {
          const k = `${x.inningNumber ?? x.inning ?? "?"}-${x.oversActual ?? (x.overNumber + "." + x.ballNumber)}-${x.id ?? x._uid ?? ""}`;
          store.comments[k] = x;
        } else if (x && typeof x === "object" && "commText" in x && ("ballNbr" in x || "overNumber" in x || "timestamp" in x)) {
          // Cricbuzz commentary item (balls and the editorial notes between them)
          const k = `cb-${x.inningsId ?? "?"}-${x.timestamp ?? ""}-${x.ballNbr ?? ""}-${x.overNumber ?? ""}`;
          store.comments[k] = x;
        } else harvest(x, depth + 1);
      }
    } else if (typeof o === "object") for (const v of Object.values(o)) harvest(v, depth + 1);
  };

  const grabNext = () => {
    const el = document.getElementById("__NEXT_DATA__");
    if (!el) {
      try { if (self.__next_f) store.pages[tabNow() + "_rsc"] = self.__next_f.map((x) => x[1]).filter(Boolean).join("").slice(0, 4_000_000); } catch (e) {}
      return;
    }
    try { const d = JSON.parse(el.textContent); store.pages[tabNow()] = d; harvest(d); } catch (e) {}
  };

  // Fallback if the structured data is missing: the visible commentary text.
  const grabText = () => {
    const main = document.querySelector("main") || document.body;
    store.pages[tabNow() + "_text"] = main.innerText.slice(0, 2_000_000);
  };

  window.addEventListener("message", (ev) => {
    const d = ev.data;
    if (ev.source !== window || !d || !d.__ttm) return;
    if (!/cricinfo\.com|cricbuzz\.com/.test(new URL(d.url, location.href).hostname)) return;
    if (!ready) { pending.push(d); return; }
    store.api.push({ url: d.url, at: new Date().toISOString(), body: d.body });
    harvest(d.body); save(); render();
  });

  // ---- panel UI ----
  const box = document.createElement("div");
  box.style.cssText = "position:fixed;right:16px;bottom:16px;z-index:2147483647;background:#0d1b3e;color:#fff;font:13px/1.4 system-ui,sans-serif;padding:12px 14px;border-radius:10px;box-shadow:0 6px 24px rgba(0,0,0,.35);width:230px";
  box.innerHTML = `<div id="ttm-head" style="font-weight:700;margin-bottom:6px;cursor:pointer">Manual capture · ${SITE} <span id="ttm-chev" style="float:right;opacity:.7">▾</span></div><div id="ttm-body">
    <div id="ttm-n" style="opacity:.85;margin-bottom:8px"></div>
    <button id="ttm-scroll" style="width:100%;margin-bottom:6px;padding:6px;border:0;border-radius:6px;background:#2a3b6b;color:#fff;cursor:pointer">Load all commentary</button>
    <button id="ttm-save" style="width:100%;padding:6px;border:0;border-radius:6px;background:#e63946;color:#fff;font-weight:700;cursor:pointer">Save JSON</button>
    <div style="opacity:.6;font-size:11px;margin-top:6px">Open the commentary, scorecard and statistics tabs (and switch innings in commentary), then save.</div></div>`;
  const collapse = (on) => { box.querySelector("#ttm-body").style.display = on ? "none" : "block"; box.querySelector("#ttm-chev").textContent = on ? "▸" : "▾"; box.style.width = on ? "170px" : "230px"; try { localStorage.setItem("ttm_manual_collapsed", on ? "1" : "0"); } catch (e) {} };
  box.querySelector("#ttm-head").onclick = () => collapse(box.querySelector("#ttm-body").style.display !== "none");
  const render = () => {
    const n = Object.keys(store.comments).length;
    const tabs = Object.keys(store.pages).filter((k) => !k.endsWith("_text")).join(", ") || "none";
    const el = box.querySelector("#ttm-n");
    if (el) el.textContent = `${n} balls captured · tabs: ${tabs}`;
  };

  // Infinite-scroll commentary loads the next batch when the end of the list scrolls into view. Jumping to the very bottom of the page skips straight past it into the ads feed, which loads
  // nothing. So: find the LAST commentary item, bring it to the middle of the window (the end-of-list trigger is just below it), nudge down and up in small steps, and give up only after
  // several tries with different positions. Never scroll beyond the list's end.
  const AD = '[class*="sponsor" i], [class*="taboola" i], [class*="outbrain" i], [id*="taboola" i], [id*="outbrain" i], [class*="advert" i], [id*="google_ads" i], [class*="-ad-" i], [data-ad], aside, footer, iframe';
  const lastItem = () => {
    let best = null, bestTop = -1;
    const w = document.createTreeWalker(document.querySelector("main") || document.body, NodeFilter.SHOW_TEXT);
    for (let n = w.nextNode(); n; n = w.nextNode()) {
      if (!/^\s*\d{1,2}\.\d\s*$/.test(n.nodeValue || "")) continue;                    // an over.ball label such as 12.3
      const el = n.parentElement; if (!el || el.closest(AD)) continue;
      const r = el.getBoundingClientRect(); if (r.height === 0) continue;
      const top = r.top + window.scrollY; if (top > bestTop) { best = el; bestTop = top; }
    }
    return best;
  };
  const repeatedItem = () => {                                                      // no over.ball labels found: the biggest run of look-alike siblings in the main column is the commentary list; its last child is the last item
    const root = document.querySelector("main") || document.body; let best = null, bestN = 7;
    for (const el of root.querySelectorAll("*")) {
      if (el.closest(AD) || el.children.length <= bestN) continue;
      const kids = [...el.children].filter((c) => c.getBoundingClientRect().height > 20), key = (c) => c.tagName + "." + (c.className || ""), counts = {};
      for (const c of kids) counts[key(c)] = (counts[key(c)] || 0) + 1;
      const top = Object.entries(counts).sort((a, b) => b[1] - a[1])[0]; if (top && top[1] > bestN) { bestN = top[1]; best = [...kids].filter((c) => key(c) === top[0]).pop(); }
    }
    return best;
  };
  const sweep = async () => {                                                        // last resort: scroll the whole page slowly from the top, like a person, so the end-of-list trigger must pass through the window
    const vh = window.innerHeight; const before = Object.keys(store.comments).length;
    for (let y = 0; y < document.body.scrollHeight; y += vh * 0.7) { window.scrollTo(0, y); await pause(260); if (Object.keys(store.comments).length > before) return true; if (window.__ttmStop) return false; }
    return false;
  };
  const moreButton = () => [...document.querySelectorAll("button, a, div[role=button], span")].find((b) => /^\s*(load|show|view) (more|older|previous)/i.test(b.textContent || "") && b.offsetParent && !b.closest(AD));
  const pause = (ms) => new Promise((r) => setTimeout(r, ms));
  const nudge = async (el, stuck = 0) => {                                         // small steps keep the end-of-list trigger inside the window for a moment
    const vh = window.innerHeight;
    if (el) el.scrollIntoView({ block: "center" });
    else window.scrollTo(0, Math.max(0, document.body.scrollHeight - vh * (4 + 3 * stuck)));   // no recognisable last item: aim a few windows above the page bottom, further up each time we are stuck (the ads feed below the list can be many windows tall)
    await pause(350);
    for (let i = 0; i < 4; i++) { window.scrollBy(0, vh * 0.12); await pause(160); }
    for (let i = 0; i < 2; i++) { window.scrollBy(0, -vh * 0.15); await pause(160); }
  };
  // The commentary page shows ONE innings at a time. On Cricinfo the switch is a team dropdown ("SL v") beside the sort ("New") and the filter ("Full Commentary"); other layouts use innings tabs or a <select>.
  // eachTeam() opens that control, switches to every other team and loads that innings' commentary completely. It reports what it found so the log shows it.
  const teamNames = () => { const m = (document.title + " " + ((document.querySelector('meta[property="og:title"]') || {}).content || "")).match(/([A-Z][\w .'-]+?) (?:vs|v) ([A-Z][\w .'-]+?)(?:,|\s-|\s\d|$)/); return m ? [m[1].trim(), m[2].trim()] : []; };
  const vis = (e) => !!(e && e.offsetParent !== null && e.getBoundingClientRect().height > 0);
  const CODE_RE = /^[A-Z]{2,5}$/;
  const findTeamControl = () => {
    for (const sel of document.querySelectorAll("select")) {
      const o = [...sel.options].map((x) => x.text.trim()); if (vis(sel) && o.length >= 2 && o.length <= 4 && o.every((t) => CODE_RE.test(t) || teamNames().some((n) => t.includes(n) || n.includes(t)))) return { kind: "select", el: sel, label: o[sel.selectedIndex] };
    }
    const btns = [...document.querySelectorAll("button, [role=button], [role=combobox], [aria-haspopup]")].filter((b) => vis(b) && !b.closest(AD));
    const anchor = btns.find((b) => /^\s*(full commentary|highlights|commentary)\b/i.test(b.textContent || ""));             // the team control sits beside the "Full Commentary" filter
    const near = anchor ? btns.filter((b) => b.parentElement === anchor.parentElement || (b.parentElement && b.parentElement.parentElement === anchor.parentElement)) : btns;
    const names = teamNames();
    const hit = near.find((b) => { const t = (b.textContent || "").trim(); return t.length <= 24 && (CODE_RE.test(t) || names.some((n) => t === n || t.startsWith(n))); });
    return hit ? { kind: "button", el: hit, label: (hit.textContent || "").trim() } : null;
  };
  const eachTeam = async (btn) => {
    const done = [], info = { found: false, tried: [] }; let ctl = findTeamControl();
    if (!ctl) return info; info.found = true; const first = ctl.label; done.push(first); info.tried.push(first + " (shown first)");
    const names = teamNames();
    for (let round = 0; round < 4 && !window.__ttmStop; round++) {
      ctl = findTeamControl(); if (!ctl) break;
      let target = null;
      if (ctl.kind === "select") { const o = [...ctl.el.options].find((x) => !done.includes(x.text.trim())); if (!o) break; target = o.text.trim(); ctl.el.value = o.value; ctl.el.dispatchEvent(new Event("change", { bubbles: true })); }
      else {
        const before = new Set([...document.querySelectorAll("*")].filter(vis)); ctl.el.click(); await pause(600);
        const opts = [...document.querySelectorAll("*")].filter((e) => vis(e) && !before.has(e) && e.children.length === 0 || (vis(e) && !before.has(e) && /^(option|menuitem|menuitemradio)$/.test(e.getAttribute("role") || "")));
        const cand = opts.map((e) => ({ e, t: (e.textContent || "").trim() })).filter((x) => x.t && x.t.length <= 24 && (CODE_RE.test(x.t) || names.some((n) => x.t === n || x.t.startsWith(n))) && !done.includes(x.t));
        if (!cand.length) { document.body.click(); if (done.length < 2) info.tried.push("dropdown opened but no other team option found"); break; }
        target = cand[0].t; (cand[0].e.closest("[role=option], [role=menuitem], li, button, a") || cand[0].e).click();
      }
      done.push(target); info.tried.push(target + " (switched)"); await pause(2500);
      const n = await loadAll(btn); info.tried[info.tried.length - 1] += `: ${n} balls so far`;
    }
    return info;
  };
  const innings = () => [...new Set(Object.values(store.comments).map((c) => c.inningNumber ?? c.inning ?? c.inningsId).filter((x) => x !== undefined && x !== null))].sort();
  const loadAll = async (btn) => {
    let last = -1, still = 0, tries = 0;
    while (still < 6 && !window.__ttmStop) {
      const more = moreButton(); if (more) more.click();
      const el = window.__ttmNoLast ? null : (lastItem() || repeatedItem());
      if (!el && still >= 1) { await sweep(); }
      else await nudge(el, still);
      if (still >= 2) {                                                           // stuck: wiggle further up and down around the end of the list
        const vh = window.innerHeight; window.scrollBy(0, -vh * (0.4 + 0.2 * (still - 2))); await pause(500); window.scrollBy(0, vh * 0.3); await pause(500);
      }
      await pause(1200);
      const n = Object.keys(store.comments).length;
      still = n === last ? still + 1 : 0; last = n; tries++;
      if (btn) btn.textContent = `Loading… ${n} balls`;
      if (tries > 400) break;
    }
    await flush();
    return Object.keys(store.comments).length;
  };
  const saveJson = () => {
    grabNext(); grabText(); flush();
    store.saved_at = new Date().toISOString(); store.page_url = location.href;
    const out = { ...store, schema: 4, comments: Object.values(store.comments) };
    const blob = new Blob([JSON.stringify(out)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob); a.download = `${SITE}_${matchId}_${matchSlug}.json`;
    document.body.appendChild(a); a.click(); a.remove();
    return Object.keys(store.comments).length;
  };
  box.querySelector("#ttm-scroll").onclick = async (e) => {
    const btn = e.target; btn.disabled = true; await loadAll(btn);
    btn.textContent = "Load all commentary"; btn.disabled = false;
  };
  box.querySelector("#ttm-save").onclick = saveJson;
  // batch.js (same content-script world) drives these in batch mode
  const meta = () => { for (const v of Object.values(store.pages)) { const d = v && v.props && v.props.appPageProps && v.props.appPageProps.data; if (d && d.match) return d.match; } return null; };
  
  const start = () => { document.body.appendChild(box); let c = true; try { c = localStorage.getItem("ttm_manual_collapsed") !== "0"; } catch (e) {} collapse(c); grabNext(); save(); render(); };
  const boot = async () => {
    let old = null; try { old = JSON.parse(sessionStorage.getItem(KEY)); } catch (e) {}                         // a capture started by the previous version of this panel
    const stored = await kvGet(KEY); if (stored) store = stored; else if (old) store = old;
    store.comments = store.comments || {}; store.pages = store.pages || {}; store.api = store.api || [];
    ready = true; for (const d of pending.splice(0)) { store.api.push({ url: d.url, at: new Date().toISOString(), body: d.body }); harvest(d.body); }
    window.__ttm = { meta, site: SITE, matchId, matchSlug, series, loadAll, saveJson, count: () => Object.keys(store.comments).length, grabText, save, flush, render,
      eachTeam, innings, info: () => ({ origin: location.origin, balls: Object.keys(store.comments).length, innings: innings(), tabs: Object.keys(store.pages).filter((k) => !k.endsWith("_text")), storage: mode, error: lastErr }),
      clear: async () => { await kvDel(KEY); try { sessionStorage.removeItem(KEY); } catch (e) {} } };
    if (document.body) start(); else document.addEventListener("DOMContentLoaded", start);
    let lastPath = location.pathname;                                           // client-side tab switches do not reload the page: re-read on URL change
    setInterval(() => { if (location.pathname !== lastPath) { lastPath = location.pathname; setTimeout(() => { grabText(); save(); render(); }, 1500); } }, 1000);
  };
  boot();
})();
