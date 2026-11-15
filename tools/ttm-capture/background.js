// Keeps the computer from sleeping while a batch is running (chrome.power: system sleep is blocked, the screen may still turn off).
// batch.js sends {ttm:"awake", on} every 45 s while it is running. If the heartbeats stop (tab closed, browser crashed, run finished or stopped)
// the lock is released within 4 minutes. This cannot stop a laptop that sleeps when the lid is closed: keep the lid open (see README).
const STALE_MS = 4 * 60 * 1000;
const release = () => { chrome.power.releaseKeepAwake(); chrome.alarms.clear("ttm-check"); chrome.storage.local.set({ ttm_beat: 0 }); };
chrome.runtime.onMessage.addListener((m) => {
  if (!m || m.ttm !== "awake") return;
  if (m.on) { chrome.power.requestKeepAwake("system"); chrome.storage.local.set({ ttm_beat: Date.now() }); chrome.alarms.create("ttm-check", { periodInMinutes: 1 }); }
  else release();
});
chrome.alarms.onAlarm.addListener((a) => {
  if (a.name !== "ttm-check") return;
  chrome.storage.local.get("ttm_beat", (v) => { if (!v.ttm_beat || Date.now() - v.ttm_beat > STALE_MS) release(); });
});
chrome.runtime.onStartup.addListener(release);
chrome.runtime.onInstalled.addListener(release);
