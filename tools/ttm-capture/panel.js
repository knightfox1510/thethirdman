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

  let store;
  try { store = JSON.parse(sessionStorage.getItem(KEY)) || null; } catch (e) { store = null; }
  if (!store) store = { site: SITE, match_id: matchId, match_slug: matchSlug, series, pages: {}, api: [], comments: {} };
  const save = () => { try { sessionStorage.setItem(KEY, JSON.stringify(store)); } catch (e) { /* too big: kept in memory */ } };

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
    store.api.push({ url: d.url, at: new Date().toISOString(), body: d.body });
    harvest(d.body); save(); render();
  });

  // ---- panel UI ----
  const box = document.createElement("div");
  box.style.cssText = "position:fixed;right:16px;bottom:16px;z-index:2147483647;background:#0d1b3e;color:#fff;font:13px/1.4 system-ui,sans-serif;padding:12px 14px;border-radius:10px;box-shadow:0 6px 24px rgba(0,0,0,.35);width:230px";
  box.innerHTML = `<div style="font-weight:700;margin-bottom:6px">Third Man capture · ${SITE}</div>
    <div id="ttm-n" style="opacity:.85;margin-bottom:8px"></div>
    <button id="ttm-scroll" style="width:100%;margin-bottom:6px;padding:6px;border:0;border-radius:6px;background:#2a3b6b;color:#fff;cursor:pointer">Load all commentary</button>
    <button id="ttm-save" style="width:100%;padding:6px;border:0;border-radius:6px;background:#e63946;color:#fff;font-weight:700;cursor:pointer">Save JSON</button>
    <div style="opacity:.6;font-size:11px;margin-top:6px">Open the commentary, scorecard and statistics tabs (and switch innings in commentary), then save.</div>`;
  const render = () => {
    const n = Object.keys(store.comments).length;
    const tabs = Object.keys(store.pages).filter((k) => !k.endsWith("_text")).join(", ") || "none";
    const el = box.querySelector("#ttm-n");
    if (el) el.textContent = `${n} balls captured · tabs: ${tabs}`;
  };

  box.querySelector("#ttm-scroll").onclick = async (e) => {
    const btn = e.target; btn.disabled = true;
    let last = -1, still = 0;
    while (still < 4) {
      window.scrollTo(0, document.body.scrollHeight);
      const more = [...document.querySelectorAll("button, a, div[role=button], span")].find((b) => /^\s*(load|show|view) more/i.test(b.textContent || "") && b.offsetParent);
      if (more) more.click();
      await new Promise((r) => setTimeout(r, 1500));
      const n = Object.keys(store.comments).length;
      still = n === last ? still + 1 : 0; last = n;
      btn.textContent = `Loading… ${n} balls`;
    }
    btn.textContent = "Load all commentary"; btn.disabled = false;
  };

  box.querySelector("#ttm-save").onclick = () => {
    grabNext(); grabText();
    store.saved_at = new Date().toISOString(); store.page_url = location.href;
    const out = { ...store, comments: Object.values(store.comments) };
    const blob = new Blob([JSON.stringify(out)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob); a.download = `${SITE}_${matchId}_${matchSlug}.json`;
    document.body.appendChild(a); a.click(); a.remove();
  };

  const start = () => { document.body.appendChild(box); grabNext(); save(); render(); };
  // client-side tab switches do not reload the page: re-read on URL change
  let lastPath = location.pathname;
  setInterval(() => { if (location.pathname !== lastPath) { lastPath = location.pathname; setTimeout(() => { grabText(); save(); render(); }, 1500); } }, 1000);
  if (document.body) start(); else document.addEventListener("DOMContentLoaded", start);
})();
