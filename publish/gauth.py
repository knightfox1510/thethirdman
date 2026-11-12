"""Google access tokens for publishing. Credentials come ONLY from the environment (or a RAM-only session file):
    G_CLIENT_ID, G_CLIENT_SECRET, G_DRIVE_TOKEN (refresh token), G_YT_TOKEN (refresh token)
Fallback: /dev/shm/thirdman_google.json (in memory, gone when the session ends). Never commit tokens."""
import json, os, time, urllib.parse, urllib.request

SHM = "/dev/shm/thirdman_google.json"
_cache = {}


def _creds():
    d = json.load(open(SHM)) if os.path.exists(SHM) else {}
    return {
        "client_id": os.environ.get("G_CLIENT_ID") or d.get("client_id"),
        "client_secret": os.environ.get("G_CLIENT_SECRET") or d.get("client_secret"),
        "drive": os.environ.get("G_DRIVE_TOKEN") or d.get("drive"),
        "youtube": os.environ.get("G_YT_TOKEN") or d.get("youtube"),
    }


def token(which):
    """Fresh access token for 'drive' or 'youtube'."""
    if which in _cache and _cache[which][1] > time.time() + 60:
        return _cache[which][0]
    c = _creds()
    if not (c["client_id"] and c["client_secret"] and c[which]):
        raise SystemExit(f"missing Google credentials for {which}: set G_CLIENT_ID, G_CLIENT_SECRET and "
                         f"{'G_DRIVE_TOKEN' if which == 'drive' else 'G_YT_TOKEN'}")
    data = urllib.parse.urlencode({"client_id": c["client_id"], "client_secret": c["client_secret"],
                                   "refresh_token": c[which], "grant_type": "refresh_token"}).encode()
    r = json.load(urllib.request.urlopen("https://oauth2.googleapis.com/token", data, timeout=60))
    _cache[which] = (r["access_token"], time.time() + r.get("expires_in", 3600))
    return r["access_token"]


def api(method, url, which, body=None, params=None, headers=None, raw=None):
    """JSON API call with a bearer token. Returns parsed JSON (or {} for empty responses)."""
    if params: url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    h = {"Authorization": "Bearer " + token(which)}
    if headers: h.update(headers)
    data = raw
    if body is not None:
        data = json.dumps(body).encode(); h["Content-Type"] = "application/json; charset=UTF-8"
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            txt = r.read().decode() or "{}"
            return json.loads(txt) if txt.strip().startswith(("{", "[")) else {"_raw": txt}
    except urllib.error.HTTPError as e:
        raise SystemExit(f"{method} {url} -> {e.code}: {e.read().decode()[:600]}")


def resumable(init_url, which, meta, path, mime, params=None):
    """Resumable upload (Drive and YouTube both use this protocol). Returns the created resource."""
    size = os.path.getsize(path)
    if params: init_url += ("&" if "?" in init_url else "?") + urllib.parse.urlencode(params)
    req = urllib.request.Request(init_url, data=json.dumps(meta).encode(), method="POST", headers={
        "Authorization": "Bearer " + token(which), "Content-Type": "application/json; charset=UTF-8",
        "X-Upload-Content-Type": mime, "X-Upload-Content-Length": str(size)})
    try:
        loc = urllib.request.urlopen(req, timeout=120).headers["Location"]
    except urllib.error.HTTPError as e:
        raise SystemExit(f"upload init -> {e.code}: {e.read().decode()[:600]}")
    CH = 16 * 1024 * 1024
    with open(path, "rb") as f:
        pos = 0
        while pos < size:
            chunk = f.read(CH); end = pos + len(chunk) - 1
            for attempt in range(5):
                req = urllib.request.Request(loc, data=chunk, method="PUT", headers={
                    "Authorization": "Bearer " + token(which), "Content-Length": str(len(chunk)),
                    "Content-Range": f"bytes {pos}-{end}/{size}"})
                try:
                    with urllib.request.urlopen(req, timeout=600) as r:
                        return json.loads(r.read().decode())            # final chunk: 200/201 with the resource
                except urllib.error.HTTPError as e:
                    if e.code == 308: break                              # chunk accepted, continue
                    if e.code in (500, 502, 503, 504) and attempt < 4: time.sleep(2 ** attempt); continue
                    raise SystemExit(f"upload chunk -> {e.code}: {e.read().decode()[:600]}")
                except (TimeoutError, ConnectionError, urllib.error.URLError):
                    if attempt < 4: time.sleep(2 ** attempt); continue
                    raise
            pos = end + 1
    raise SystemExit("upload ended without a final response")
