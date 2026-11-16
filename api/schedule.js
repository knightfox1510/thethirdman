// GET  /api/schedule            -> {rows, updated, editable}   (public: the schedule is not secret)
// PUT  /api/schedule  {rows}    -> saves the whole schedule     (needs x-ttm-key = SITE_PASSWORD)
// Seeded from site/data/schedule.json the first time (the site does that when storage is empty).
const { getJSON, setJSON, storageReady, authed, send } = require("./_lib");

const KEY = "ttm:schedule";
const STATUSES = ["Idea", "To build", "To do", "Ready", "Uploading", "Uploaded (private)", "Posted", "Hold", "Cancelled"];
const SERIES = ["01 Myth or Data", "02 The Replay Room", "03 Tactics Board", "04 The Lab", "05 Stat Check", "06 What If", "07 Rising Star", "08 Flip", "09 Data Stories", "10 Channel", "11 Did You Know"];   // same names as the Drive folders (publish/series.py)
const clip = (v, n) => (v == null || v === "" ? null : String(v).slice(0, n));

function clean(rows) {
  if (!Array.isArray(rows) || rows.length > 600) throw new Error("rows must be a list of at most 600");
  return rows.map((r, i) => {
    const date = clip(r.date, 10);
    if (date && !/^\d{4}-\d{2}-\d{2}$/.test(date)) throw new Error(`row ${i + 1}: date must be YYYY-MM-DD`);
    const status = clip(r.status, 30);
    if (status && !STATUSES.includes(status)) throw new Error(`row ${i + 1}: unknown status ${status}`);
    const content = clip(r.content, 200);
    if (!content) throw new Error(`row ${i + 1}: content is required`);
    const series = clip(r.series, 40);
    if (series && !SERIES.includes(series)) throw new Error(`row ${i + 1}: unknown series ${series}`);
    const link = clip(r.link, 300);
    if (link && !/^https?:\/\//.test(link)) throw new Error(`row ${i + 1}: link must start with http(s)://`);
    return { id: clip(r.id, 40) || Math.random().toString(36).slice(2, 10), date, platform: clip(r.platform, 80), series, content, status, link, notes: clip(r.notes, 500) };
  });
}

module.exports = async (req, res) => {
  try {
    if (req.method === "GET") {
      if (!storageReady()) return send(res, 200, { rows: null, editable: false, reason: "storage not configured" });
      const doc = await getJSON(KEY);
      return send(res, 200, { rows: doc ? doc.rows : null, updated: doc ? doc.updated : null, editable: true });
    }
    if (req.method === "PUT") {
      if (!authed(req)) return send(res, 401, { error: "wrong or missing password" });
      if (!storageReady()) return send(res, 503, { error: "storage not configured" });
      const body = typeof req.body === "string" ? JSON.parse(req.body) : req.body || {};
      const rows = clean(body.rows);
      // optimistic concurrency: refuse if someone saved since this client loaded
      const cur = await getJSON(KEY);
      if (cur && body.base && cur.updated !== body.base) return send(res, 409, { error: "the schedule changed elsewhere; reload and try again", updated: cur.updated });
      const doc = { rows, updated: new Date().toISOString() };
      await setJSON(KEY, doc);
      return send(res, 200, { ok: true, updated: doc.updated, count: rows.length });
    }
    res.setHeader("Allow", "GET, PUT");
    return send(res, 405, { error: "method not allowed" });
  } catch (e) {
    return send(res, 400, { error: String(e.message || e) });
  }
};
module.exports.STATUSES = STATUSES;
module.exports.SERIES = SERIES;
