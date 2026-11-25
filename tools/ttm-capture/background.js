// Keeps the computer from sleeping while a batch is running (chrome.power: system sleep is blocked; with the "screen" option the display stays on too). Also times waits for hidden pages.
// batch.js sends {ttm:"awake", on} every 45 s while it is running. If the heartbeats stop (tab closed, browser crashed, run finished or stopped)
// the lock is released within 4 minutes. This cannot stop a laptop that sleeps when the lid is closed: keep the lid open (see README).
const STALE_MS = 4 * 60 * 1000;
const POWER = typeof chrome !== "undefined" && chrome.power ? chrome.power : null;                  // Firefox has no chrome.power: keep-awake does nothing there (keep the computer awake yourself), everything else works
const release = () => { if (POWER) POWER.releaseKeepAwake(); chrome.alarms.clear("ttm-check"); chrome.storage.local.set({ ttm_beat: 0 }); };
chrome.runtime.onMessage.addListener((m, sender, sendResponse) => {
  if (m && m.ttm === "sleep") { setTimeout(() => { try { sendResponse({ ok: true }); } catch (e) {} }, Math.min(Math.max(+m.ms || 0, 0), 60000)); return true; }   // a timer for a hidden page (its own timers are throttled)
  if (!m || m.ttm !== "awake") return;
  if (m.on) { if (POWER) POWER.requestKeepAwake(m.screen ? "display" : "system"); chrome.storage.local.set({ ttm_beat: Date.now() }); chrome.alarms.create("ttm-check", { periodInMinutes: 1 }); }
  else release();
});
chrome.alarms.onAlarm.addListener((a) => {
  if (a.name !== "ttm-check") return;
  chrome.storage.local.get("ttm_beat", (v) => { if (!v.ttm_beat || Date.now() - v.ttm_beat > STALE_MS) release(); });
});
chrome.runtime.onStartup.addListener(release);
chrome.runtime.onInstalled.addListener(release);
