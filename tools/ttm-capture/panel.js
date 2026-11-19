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
  const tabNow = () => SITE === "cricinfo"                                       // /series/<series-id>/<match-slug-id>/<tab>: the TAB is the 4th segment. (It used to be the match slug, identical for every tab, so scorecard / playing XI / statistics overwrote each other and only the last survived.)
    ? (location.pathname.split("/").filter(Boolean)[3] || "home")
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
    const hidden = []; for (const el of document.querySelectorAll("[data-ttm-panel]")) { hidden.push([el, el.style.display]); el.style.display = "none"; }          // our own panels are not page content (the Activity log was ending up in the saved text)
    try { store.pages[tabNow() + "_text"] = main.innerText.slice(0, 2_000_000); } finally { for (const [el, d] of hidden) el.style.display = d; }
  };

  window.addEventListener("message", (ev) => {
    const d = ev.data;
    if (ev.source !== window || !d || !d.__ttm) return;
    if (!/cricinfo\.com|cricbuzz\.com/.test(new URL(d.url, location.href).hostname)) return;
    if (!ready) { pending.push(d); return; }
    store.api.push({ url: d.url, at: new Date().toISOString(), body: d.body });
    { const m = /inningNumber=(\d+)/.exec(d.url || ""); if (m) { store.reqInnings = store.reqInnings || []; if (!store.reqInnings.includes(+m[1])) store.reqInnings.push(+m[1]); } }   // which innings the page itself asked for
    harvest(d.body); save(); render();
  });

  // ---- panel UI ----
  const box = document.createElement("div"); box.setAttribute("data-ttm-panel", "1");
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
  const CODE_RE = /^[A-Z]{2,5}$/, INN_RE = /^[A-Z]{2,5}\s+(?:1st|2nd|3rd|4th)\s+Innings$/i;     // a Test's control reads "ENG 2nd Innings"
  // The page's own data (present on every tab) says which teams played and which innings have balls: match.teams[].team.abbreviation / name / inningNumbers, content.innings[].inningNumber / balls.
  const pageData = () => { for (const v of Object.values(store.pages)) { const d = v && v.props && v.props.appPageProps && v.props.appPageProps.data; if (d && d.match) return d; } return null; };
  const teamList = () => { const d = pageData(); return ((d && d.match && d.match.teams) || []).map((t) => ({ abbr: (t.team && t.team.abbreviation) || "", name: (t.team && (t.team.longName || t.team.name)) || "", innings: t.inningNumbers || [] })); };
  const expectedInnings = () => {                                                  // 1,2 for a one-day match, 1..4 for a Test: whatever the page lists with balls bowled
    const d = pageData(); let ex = []; const inn = d && d.content && d.content.innings;
    if (Array.isArray(inn)) ex = inn.filter((i) => (i.balls || 0) > 0).map((i) => i.inningNumber);
    if (!ex.length) ex = teamList().flatMap((t) => t.innings);
    return [...new Set(ex)].sort((a, b) => a - b);
  };
  const ownText = (e) => (e.textContent || "").replace(/\s+/g, " ").trim();
  const clickable = (e) => e.closest("button, [role=button], [role=combobox], [role=tab], [aria-haspopup], a") || e;
  const rowItems = (lbl) => {                                                       // every short visible item on the filter's own visual row, left to right (not tied to any parent element)
    const lr = lbl.getBoundingClientRect(), ly = lr.top + lr.height / 2, tol = Math.max(24, lr.height * 0.8);
    const all = [...document.querySelectorAll("body *")].filter((e) => { if (!vis(e) || e.closest("h1, h2, h3, h4, h5, h6") || e.closest(AD)) return false; const r = e.getBoundingClientRect(); return Math.abs(r.top + r.height / 2 - ly) < tol && ownText(e).length >= 1 && ownText(e).length <= 24 && ![...e.children].some((c) => ownText(c) === ownText(e)); });
    const uniq = all.filter((e) => !all.some((o) => o !== e && e.contains(o)));                       // keep the innermost items, not a wrapper whose text happens to be short
    return uniq.sort((a, b) => a.getBoundingClientRect().left - b.getBoundingClientRect().left);
  };
  const toolbarChips = () => {                                                       // the row that holds "New", the team control and "Full Commentary": found through the filter label, whatever tags the page uses
    const FILTER = /^(full commentary)$/i;                                           // the filter button only: the nav tab "Commentary" (Summary | Scorecard | Commentary | ...) is NOT it, and matching it picked the wrong row on 65208
    const lbl = [...document.querySelectorAll("button, [role=button], div, span, a, li")].filter((e) => vis(e) && !e.closest(AD) && !e.closest("[role=tablist], nav") && FILTER.test(ownText(e))).filter((e) => ![...e.children].some((c) => FILTER.test(ownText(c))))[0];
    if (!lbl) return { lbl: null, chips: [] };
    let anc = lbl;
    for (let i = 0; i < 6 && anc.parentElement; i++) {
      anc = anc.parentElement;
      const lr = lbl.getBoundingClientRect(), ly = lr.top + lr.height / 2, tol = Math.max(24, lr.height * 0.8);                  // only items on the SAME visual row as the filter (the page header also contains team names)
      const chips = [...anc.querySelectorAll("*")].filter((e) => { if (!vis(e) || /^H[1-6]$/.test(e.tagName) || e.closest("h1, h2, h3, h4, h5, h6")) return false; const r = e.getBoundingClientRect(); return Math.abs(r.top + r.height / 2 - ly) < tol && ownText(e).length >= 1 && ownText(e).length <= 24 && ![...e.children].some((c) => ownText(c) === ownText(e)) && !e.closest(AD); });
      const uniq = chips.filter((e) => !chips.some((o) => o !== e && e.contains(o)));
      if (uniq.length >= 3) return { lbl, chips: uniq };                           // sort + team + filter at least
    }
    const row = rowItems(lbl); return { lbl, chips: row.length >= 2 ? row : [] };                    // no common ancestor found: use the row scan
  };
  const findTeamControl = () => {
    const teams = teamList(), words = new Set(teams.flatMap((t) => [t.abbr, t.name]).filter(Boolean)), names = teamNames();
    for (const sel of document.querySelectorAll("select")) {
      const o = [...sel.options].map((x) => x.text.trim()); if (vis(sel) && o.length >= 2 && o.length <= 4 && o.every((t) => words.has(t) || CODE_RE.test(t) || names.some((n) => t.includes(n) || n.includes(t)))) return { kind: "select", el: sel, label: o[sel.selectedIndex] };
    }
    const { lbl, chips } = toolbarChips(); const SORT = /^(new|old|newest|oldest|latest|full commentary|highlights|wickets|fours|sixes|commentary)$/i;
    let hit = chips.find((e) => words.has(ownText(e)));                                                          // 1. on the filter's row: an item that IS a team's abbreviation or name (from the page's own data)
    if (!hit && lbl) hit = rowItems(lbl).find((e) => words.has(ownText(e)));
    if (!hit) {                                                                                                  // 2. anywhere above the first commentary item: a short item that is exactly a team label
      const first = [...document.querySelectorAll("main *")].find((e) => /^\s*\d{1,2}\.\d\s*$/.test(e.textContent || "") && vis(e)), limit = first ? first.getBoundingClientRect().top + window.scrollY : 1200;
      hit = [...document.querySelectorAll("body *")].filter((e) => vis(e) && !e.closest(AD) && !e.closest("h1, h2, h3, h4, h5, h6") && !e.closest("[role=tablist], nav") && words.has(ownText(e)) && ![...e.children].some((c) => words.has(ownText(c))) && e.getBoundingClientRect().top + window.scrollY < limit)
        .sort((a, b) => a.getBoundingClientRect().top - b.getBoundingClientRect().top).pop();                      // the lowest such item is the one nearest the commentary (the header's team names sit higher up)
    }
    if (!hit) hit = chips.find((e) => CODE_RE.test(ownText(e)) || names.some((n) => ownText(e) === n || ownText(e).startsWith(n)));
    if (!hit) hit = chips.find((e) => INN_RE.test(ownText(e)));
    if (!hit) { const rest = chips.filter((e) => !SORT.test(ownText(e))); if (rest.length === 1) hit = rest[0]; }
    return hit ? { kind: "button", el: clickable(hit), label: ownText(hit) } : null;
  };
  const describeToolbar = () => {                                                  // what the page actually has near the filter, for the log when the control is not found
    const lbl = (toolbarChips().lbl); const chips = lbl ? rowItems(lbl) : []; if (!lbl) return `no "Full Commentary" filter on this page; clickable text seen: ` + [...document.querySelectorAll("button, [role=button], [role=tab], select")].filter(vis).slice(0, 10).map((e) => `${e.tagName.toLowerCase()}:${ownText(e).slice(0, 18)}`).join(" | ");
    return `filter found; row items: ` + (chips.length ? chips : [lbl]).map((e) => `${e.tagName.toLowerCase()}${e.getAttribute("role") ? "[" + e.getAttribute("role") + "]" : ""}.${String(e.className).split(" ")[0].slice(0, 22)}:'${ownText(e).slice(0, 18)}'`).join(" | ");
  };
  // A dropdown may ignore a plain element.click() (menus built on pointer or keyboard events), so each team switch is tried in several ways and VERIFIED each time:
  // the control's label becomes the new team, or new innings' balls arrive, or the page itself requests another inningNumber. If nothing works the real markup goes to the log and the capture.
  const html = (e, n = 420) => { try { return e.outerHTML.replace(/\s+/g, " ").slice(0, n); } catch (x) { return ""; } };
  const realClick = (el) => {
    el.scrollIntoView({ block: "center" }); const r = el.getBoundingClientRect(), x = r.left + r.width / 2, y = r.top + r.height / 2;
    const o = (b) => ({ bubbles: true, cancelable: true, composed: true, view: window, clientX: x, clientY: y, button: 0, buttons: b, pointerType: "mouse", pointerId: 1, isPrimary: true });
    for (const t of ["pointerover", "pointerenter", "mouseover", "mousemove"]) el.dispatchEvent(new (t.startsWith("pointer") ? PointerEvent : MouseEvent)(t, o(0)));
    el.dispatchEvent(new PointerEvent("pointerdown", o(1))); el.dispatchEvent(new MouseEvent("mousedown", o(1))); try { el.focus(); } catch (e) {}
    el.dispatchEvent(new PointerEvent("pointerup", o(0))); el.dispatchEvent(new MouseEvent("mouseup", o(0))); el.dispatchEvent(new MouseEvent("click", o(0)));
  };
  const key = (el, k) => { for (const t of ["keydown", "keyup"]) el.dispatchEvent(new KeyboardEvent(t, { key: k, code: k, bubbles: true, cancelable: true, composed: true })); };
  const wantedWords = () => new Set(teamList().flatMap((t) => [t.abbr, t.name]).filter(Boolean));
  const findOption = (target, ctlEl) => [...document.querySelectorAll("body *")].filter((e) => vis(e) && ownText(e) === target && !ctlEl.contains(e) && !e.contains(ctlEl) && ![...e.children].some((c) => ownText(c) === target) && !e.closest("h1, h2, h3, h4, h5, h6, [role=tablist], nav")).sort((a, b) => b.getBoundingClientRect().top - a.getBoundingClientRect().top)[0];
  const switched = (target, innBefore, reqBefore) => { const c = findTeamControl(); return (c && c.label === target) || innings().length > innBefore || (store.reqInnings || []).length > reqBefore; };
  const eachTeam = async (btn) => {
    const done = [], info = { found: false, tried: [], stuck: false }; let ctl = findTeamControl();
    if (!ctl) return info; info.found = true; const first = ctl.label; done.push(first); info.tried.push(first + " (shown first)");
    const words = wantedWords(), names = teamNames(); const missing = () => expectedInnings().filter((n) => !innings().includes(n));
    for (let round = 0; round < 5 && !window.__ttmStop; round++) {
      if (expectedInnings().length && !missing().length) break;                                   // every innings the page lists has been seen
      ctl = findTeamControl(); if (!ctl) break;
      if (ctl.kind === "select") {
        const o = [...ctl.el.options].find((x) => !done.includes(x.text.trim())); if (!o) break; const target = o.text.trim(); const innBefore = innings().length, reqBefore = (store.reqInnings || []).length;
        ctl.el.value = o.value; ctl.el.dispatchEvent(new Event("change", { bubbles: true })); done.push(target); info.tried.push(target + " (select changed)");
        for (let i = 0; i < 20 && !switched(target, innBefore, reqBefore) && !window.__ttmStop; i++) await pause(1000);
      } else {
        // which other team is next? read the options once the control is opened
        const before = new Set([...document.querySelectorAll("*")].filter(vis)); ctl.el.click(); await pause(600);
        if (![...document.querySelectorAll("*")].some((e) => vis(e) && !before.has(e))) { realClick(ctl.el); await pause(600); }
        const opts = [...document.querySelectorAll("*")].filter((e) => vis(e) && !before.has(e) && (e.children.length === 0 || /^(option|menuitem|menuitemradio)$/.test(e.getAttribute("role") || "")));
        let cand = opts.map((e) => ({ e, t: ownText(e) })).filter((x) => x.t && x.t.length <= 30 && (words.has(x.t) || CODE_RE.test(x.t) || INN_RE.test(x.t) || names.some((n) => x.t === n || x.t.startsWith(n))) && !done.includes(x.t));
        if (!cand.length) cand = [...document.querySelectorAll("[role=option], [role=menuitem], li")].filter(vis).map((e) => ({ e, t: ownText(e) })).filter((x) => x.t && x.t.length <= 30 && !done.includes(x.t) && x.t !== ctl.label);
        if (!cand.length) { document.body.click(); if (missing().length) { info.tried.push("dropdown opened but no other option found"); info.stuck = true; store.diag = (store.diag || []).concat({ at: new Date().toISOString(), what: "no option found", control: html(ctl.el) }); } break; }
        const target = cand[0].t, popup = cand[0].e.closest("[role=listbox], [role=menu], ul, ol") || cand[0].e.parentElement;
        const strategies = [
          ["click", (o) => o.click()],
          ["pointer events", (o) => realClick(o)],
          ["parent element", (o) => realClick(o.closest("[role=option], [role=menuitem], [role=menuitemradio], li, button, a, [tabindex]") || o.parentElement || o)],
          ["keyboard: Down, Enter", async () => { ctl.el.focus(); key(ctl.el, "ArrowDown"); await pause(250); key(document.activeElement || ctl.el, "Enter"); }],
          ["keyboard: Down, Down, Enter", async () => { ctl.el.focus(); key(ctl.el, "ArrowDown"); await pause(250); key(document.activeElement || ctl.el, "ArrowDown"); await pause(250); key(document.activeElement || ctl.el, "Enter"); }],
          ["keyboard: Up, Enter", async () => { ctl.el.focus(); key(ctl.el, "ArrowUp"); await pause(250); key(document.activeElement || ctl.el, "Enter"); }],
          ["keyboard: Enter, Down, Enter", async () => { ctl.el.focus(); key(ctl.el, "Enter"); await pause(300); key(document.activeElement || ctl.el, "ArrowDown"); await pause(250); key(document.activeElement || ctl.el, "Enter"); }],
        ];
        const innBefore = innings().length, reqBefore = (store.reqInnings || []).length; let worked = "", tried = [];
        for (const [name, run] of strategies) {
          if (window.__ttmStop) break;
          let o = findOption(target, ctl.el);
          if (!o && !name.startsWith("keyboard")) { ctl.el.click(); await pause(500); o = findOption(target, ctl.el); }       // the menu closed after the last attempt: open it again
          if (!o && !name.startsWith("keyboard")) { tried.push(name + ": option not visible"); continue; }
          await run(o); tried.push(name);
          for (let i = 0; i < (name.startsWith("keyboard") ? 3 : 6) && !switched(target, innBefore, reqBefore); i++) await pause(1000);
          if (switched(target, innBefore, reqBefore)) { worked = name; break; }
          document.body.click(); await pause(300);                                          // close whatever is open before the next way
        }
        done.push(target);
        if (!worked) {
          info.stuck = true; info.tried.push(`${target}: the page did not switch (tried ${tried.join(", ")})`);
          store.diag = (store.diag || []).concat({ at: new Date().toISOString(), what: "switch failed", target, tried, control: html(ctl.el), popup: html(popup, 700) }); save();
          document.body.click(); break;                                                                // deterministic failure: do not repeat it
        }
        info.tried.push(`${target} (switched by ${worked})`);
        for (let i = 0; i < 25 && innings().length <= innBefore && !window.__ttmStop; i++) await pause(1000);              // wait until the new innings' balls arrive
      }
      const n = await loadAll(btn); info.tried[info.tried.length - 1] += `: ${n} balls so far`;
    }
    info.expected = expectedInnings(); info.missing = missing();
    return info;
  };
  const innings = () => [...new Set(Object.values(store.comments).map((c) => c.inningNumber ?? c.inning ?? c.inningsId).filter((x) => x !== undefined && x !== null))].sort();
  const loadAll = async (btn) => {
    let last = -1, still = 0, tries = 0;
    for (let i = 0; i < 25 && Object.keys(store.comments).length === 0 && !window.__ttmStop; i++) await pause(1000);   // the first batch can be slow: do not start counting stalls before it arrives
    while (still < (Object.keys(store.comments).length < 100 ? 12 : 6) && !window.__ttmStop) {              // few balls so far: be more patient before giving up (65208 stopped at 20, then got 318 on the retry)
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
    delete store.pages[matchSlug]; delete store.pages[matchSlug + "_text"];                                       // left behind by the old tab-naming bug (every tab shared this key)
    ready = true; for (const d of pending.splice(0)) { store.api.push({ url: d.url, at: new Date().toISOString(), body: d.body }); harvest(d.body); }
    // direct.js (optional) stores what it fetches through these; they add to the capture exactly as the page's own requests and tab loads do
    const put = (tab, data) => { store.pages[tab] = data; harvest(data); save(); render(); };
    const addApi = (url, body) => { store.api.push({ url, at: new Date().toISOString(), body }); { const m = /inningNumber=(\d+)/.exec(url || ""); if (m) { store.reqInnings = store.reqInnings || []; if (!store.reqInnings.includes(+m[1])) store.reqInnings.push(+m[1]); } } harvest(body); save(); render(); };
    const apiHost = () => { const u = (store.api.map((a) => a.url).find((x) => /\/\/hs-consumer-api\./.test(x || "")) || ""); const m = u.match(/^https:\/\/[^/]+/); return m ? m[0] : ""; };
    const check = () => { const d = pageData(), inn = (d && d.content && d.content.innings) || [], got = {};     // per innings: legal balls the scorecard says were bowled vs balls we hold (wides / no-balls are extra items)
      for (const c of Object.values(store.comments)) { const n = c.inningNumber ?? c.inning; if (n != null && !c.wides && !c.noballs) got[n] = (got[n] || 0) + 1; }
      return inn.filter((i) => (i.balls || 0) > 0).map((i) => ({ n: i.inningNumber, want: i.balls, got: got[i.inningNumber] || 0 })); };
    window.__ttm = { meta, put, addApi, apiHost, check, site: SITE, matchId, matchSlug, series, loadAll, saveJson, count: () => Object.keys(store.comments).length, grabText, save, flush, render,
      eachTeam, innings, expected: expectedInnings, diag: describeToolbar, lastDiag: () => { const d = (store.diag || []).slice(-1)[0]; return d ? `${d.what}${d.target ? " -> " + d.target : ""}; control: ${d.control}${d.popup ? " | popup: " + d.popup : ""}` : ""; }, info: () => ({ origin: location.origin, balls: Object.keys(store.comments).length, innings: innings(), expected: expectedInnings(), tabs: Object.keys(store.pages).filter((k) => !k.endsWith("_text")), storage: mode, error: lastErr }),
      clear: async () => { await kvDel(KEY); try { sessionStorage.removeItem(KEY); } catch (e) {} } };
    if (document.body) start(); else document.addEventListener("DOMContentLoaded", start);
    let lastPath = location.pathname;                                           // client-side tab switches do not reload the page: re-read on URL change
    setInterval(() => { if (location.pathname !== lastPath) { lastPath = location.pathname; setTimeout(() => { grabText(); save(); render(); }, 1500); } }, 1000);
  };
  boot();
})();
