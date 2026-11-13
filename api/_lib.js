// Shared helpers for the control-room API (Vercel Node functions, CommonJS).
// Environment (set in Vercel → Settings → Environment Variables; never in the repo):
//   SITE_PASSWORD                       password for editing and for private data (stats)
//   UPSTASH_REDIS_REST_URL / _TOKEN     storage (or KV_REST_API_URL / KV_REST_API_TOKEN from the Vercel integration)
//   G_CLIENT_ID, G_CLIENT_SECRET, G_YT_TOKEN   YouTube (refresh token must include yt-analytics.readonly for watch hours)
//   CRON_SECRET                         optional; Vercel sends it with the daily cron
const crypto = require("crypto");

const redisUrl = () => process.env.UPSTASH_REDIS_REST_URL || process.env.KV_REST_API_URL;
const redisTok = () => process.env.UPSTASH_REDIS_REST_TOKEN || process.env.KV_REST_API_TOKEN;
const storageReady = () => Boolean(redisUrl() && redisTok());

async function redis(...cmd) {
  const r = await fetch(redisUrl(), {
    method: "POST",
    headers: { Authorization: `Bearer ${redisTok()}`, "Content-Type": "application/json" },
    body: JSON.stringify(cmd),
  });
  const j = await r.json();
  if (!r.ok || j.error) throw new Error(`storage: ${j.error || r.status}`);
  return j.result;
}
const getJSON = async (key) => { const v = await redis("GET", key); return v ? JSON.parse(v) : null; };
const setJSON = (key, val) => redis("SET", key, JSON.stringify(val));

function safeEqual(a, b) {
  const x = crypto.createHash("sha256").update(String(a)).digest();
  const y = crypto.createHash("sha256").update(String(b)).digest();
  return crypto.timingSafeEqual(x, y);
}
function authed(req) {
  const pw = process.env.SITE_PASSWORD;
  if (!pw) return false;                       // no password configured: nothing private or writable is allowed
  return safeEqual(req.headers["x-ttm-key"] || "", pw);
}
function cronAuthed(req) {
  const s = process.env.CRON_SECRET;
  return Boolean(s) && safeEqual(req.headers["authorization"] || "", `Bearer ${s}`);
}
const send = (res, code, body) => { res.status(code).setHeader("Cache-Control", "no-store"); res.json(body); };

module.exports = { redis, getJSON, setJSON, storageReady, authed, cronAuthed, send };
