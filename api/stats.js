// GET /api/stats                 -> last saved stats                     (needs x-ttm-key)
// GET /api/stats?refresh=1       -> pulls fresh numbers from YouTube     (needs x-ttm-key, or the daily cron's secret)
// Data API gives subscribers, views, per-video views/likes. The Analytics API adds watch hours and retention and needs the
// yt-analytics.readonly scope on the refresh token; without it the page still works and says what is missing.
const fs = require("fs");
const path = require("path");
const { getJSON, setJSON, storageReady, authed, cronAuthed, send } = require("./_lib");

const KEY = "ttm:stats", HIST = "ttm:stats:history";
const YPP = { watch_hours_now: 4000, watch_hours_feb_2027: 8000, shorts_views_90d_now: 10_000_000, shorts_views_90d_feb_2027: 20_000_000, subs: 1000 };

async function accessToken() {
  const { G_CLIENT_ID, G_CLIENT_SECRET, G_YT_TOKEN } = process.env;
  if (!(G_CLIENT_ID && G_CLIENT_SECRET && G_YT_TOKEN)) throw new Error("YouTube credentials are not set in Vercel (G_CLIENT_ID, G_CLIENT_SECRET, G_YT_TOKEN)");
  const r = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ client_id: G_CLIENT_ID, client_secret: G_CLIENT_SECRET, refresh_token: G_YT_TOKEN, grant_type: "refresh_token" }),
  });
  const j = await r.json();
  if (!j.access_token) throw new Error("could not refresh the YouTube token: " + (j.error_description || j.error));
  return j.access_token;
}
const yt = async (tok, url) => {
  const r = await fetch(url, { headers: { Authorization: `Bearer ${tok}` } });
  const j = await r.json();
  if (!r.ok) { const e = new Error(j.error?.message || r.status); e.status = r.status; throw e; }
  return j;
};
const isoDur = (d) => { const m = /PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/.exec(d || "") || []; return (+m[1] || 0) * 3600 + (+m[2] || 0) * 60 + (+m[3] || 0); };
const day = (offset = 0) => new Date(Date.now() + offset * 864e5).toISOString().slice(0, 10);
const num = (x) => (x == null ? 0 : Number(x));

function videoMap() {
  try { return JSON.parse(fs.readFileSync(path.join(process.cwd(), "site", "data", "video_map.json"), "utf8")); } catch (e) { return {}; }
}

async function build() {
  const tok = await accessToken();
  const map = videoMap();
  const ch = (await yt(tok, "https://www.googleapis.com/youtube/v3/channels?part=statistics,contentDetails&mine=true")).items[0];
  const uploads = ch.contentDetails.relatedPlaylists.uploads;
  let ids = [], page = "";
  do {
    const p = await yt(tok, `https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults=50&playlistId=${uploads}${page ? "&pageToken=" + page : ""}`);
    ids.push(...p.items.map((i) => i.contentDetails.videoId)); page = p.nextPageToken;
  } while (page && ids.length < 500);
  const videos = [];
  for (let i = 0; i < ids.length; i += 50) {
    const v = await yt(tok, `https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics,contentDetails,status&id=${ids.slice(i, i + 50).join(",")}`);
    for (const x of v.items) {
      const m = map[x.id] || {};
      const secs = isoDur(x.contentDetails.duration);
      videos.push({ id: x.id, title: m.title || x.snippet.title, yt_title: x.snippet.title, slug: m.slug || null, format: m.format || null,
        kind: m.kind || (secs <= 180 ? "short" : "long"), seconds: secs, privacy: x.status.privacyStatus, published: x.snippet.publishedAt,
        views: num(x.statistics.viewCount), likes: num(x.statistics.likeCount), comments: num(x.statistics.commentCount) });
    }
  }
  const out = { updated: new Date().toISOString(),
    channel: { subs: num(ch.statistics.subscriberCount), views: num(ch.statistics.viewCount), videos: num(ch.statistics.videoCount) },
    analytics: false, analytics_note: null, ypp: { targets: YPP, long_watch_hours_365: null, shorts_views_90: null }, videos, formats: [] };

  // Analytics (optional): watch hours, retention per video, and YPP numbers split by content type
  try {
    const rep = (q) => yt(tok, `https://youtubeanalytics.googleapis.com/v2/reports?ids=channel==MINE&${q}`);
    const perVideo = await rep(`startDate=${day(-365)}&endDate=${day(0)}&dimensions=video&metrics=views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained&sort=-views&maxResults=200`);
    const byId = Object.fromEntries((perVideo.rows || []).map((r) => [r[0], r]));
    for (const v of videos) {
      const r = byId[v.id]; if (!r) continue;
      Object.assign(v, { minutes: num(r[2]), avg_view_s: num(r[3]), avg_view_pct: num(r[4]), subs_gained: num(r[5]) });
    }
    const t365 = await rep(`startDate=${day(-365)}&endDate=${day(0)}&dimensions=creatorContentType&metrics=views,estimatedMinutesWatched`);
    const t90 = await rep(`startDate=${day(-90)}&endDate=${day(0)}&dimensions=creatorContentType&metrics=views,estimatedMinutesWatched`);
    const get = (t, type, i) => num(((t.rows || []).find((r) => r[0] === type) || [])[i]);
    out.ypp.long_watch_hours_365 = Math.round(get(t365, "VIDEO_ON_DEMAND", 2) / 60 * 10) / 10;
    out.ypp.shorts_views_90 = get(t90, "SHORTS", 1);
    out.analytics = true;
  } catch (e) {
    out.analytics_note = e.status === 403
      ? "Watch hours and retention need the yt-analytics.readonly permission on the YouTube login (see README: re-authorise once)."
      : "Analytics unavailable: " + e.message;
  }

  // results per format (only videos mapped to a format)
  const groups = {};
  for (const v of videos) { if (!v.format) continue; (groups[v.format + "|" + v.kind] ||= []).push(v); }
  out.formats = Object.entries(groups).map(([k, vs]) => {
    const [format, kind] = k.split("|");
    const views = vs.reduce((a, v) => a + v.views, 0);
    const wv = vs.filter((v) => v.avg_view_pct != null && v.views > 0);
    const w = wv.reduce((a, v) => a + v.views, 0);
    return { format, kind, videos: vs.length, views, avg_views: Math.round(views / vs.length),
      avg_view_pct: w ? Math.round(wv.reduce((a, v) => a + v.avg_view_pct * v.views, 0) / w * 10) / 10 : null,
      watch_hours: wv.length ? Math.round(vs.reduce((a, v) => a + (v.minutes || 0), 0) / 6) / 10 : null };
  }).sort((a, b) => b.avg_views - a.avg_views);
  return out;
}

module.exports = async (req, res) => {
  try {
    const refresh = req.query && (req.query.refresh === "1" || req.query.refresh === "true");
    if (!(authed(req) || (refresh && cronAuthed(req)))) return send(res, 401, { error: "wrong or missing password" });
    if (!storageReady()) return send(res, 503, { error: "storage not configured" });
    if (!refresh) {
      const doc = await getJSON(KEY);
      return send(res, 200, doc || { empty: true, history: [] });
    }
    const stats = await build();
    const hist = (await getJSON(HIST)) || [];
    const d = day(0), snap = { date: d, subs: stats.channel.subs, views: stats.channel.views, long_watch_hours_365: stats.ypp.long_watch_hours_365, shorts_views_90: stats.ypp.shorts_views_90 };
    const i = hist.findIndex((h) => h.date === d); if (i >= 0) hist[i] = snap; else hist.push(snap);
    stats.history = hist.slice(-400);
    await setJSON(KEY, stats); await setJSON(HIST, stats.history);
    return send(res, 200, stats);
  } catch (e) {
    return send(res, 500, { error: String(e.message || e) });
  }
};
