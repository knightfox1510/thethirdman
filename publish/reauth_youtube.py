"""Get a YouTube refresh token that also allows YouTube Analytics (watch hours, retention) - run ONCE on your own computer.
    G_CLIENT_ID=... G_CLIENT_SECRET=... python3 publish/reauth_youtube.py
It opens Google's consent page, receives the answer on http://127.0.0.1:8765 and prints the new refresh token in the
terminal only (nothing is written to disk). Paste it into Vercel as G_YT_TOKEN (and your own G_YT_TOKEN env var).
Needs: the OAuth client type "Desktop app", and the "YouTube Analytics API" enabled in the same Google Cloud project."""
import http.server, json, os, secrets, sys, threading, urllib.parse, urllib.request, webbrowser

SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl",
          "https://www.googleapis.com/auth/yt-analytics.readonly"]
PORT = 8765
cid, sec = os.environ.get("G_CLIENT_ID"), os.environ.get("G_CLIENT_SECRET")
if not (cid and sec): sys.exit("set G_CLIENT_ID and G_CLIENT_SECRET first")
redirect, state, got = f"http://127.0.0.1:{PORT}", secrets.token_urlsafe(16), {}


class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if q.get("state", [""])[0] == state and "code" in q: got["code"] = q["code"][0]
        self.send_response(200); self.send_header("Content-Type", "text/plain; charset=utf-8"); self.end_headers()
        self.wfile.write(b"Done. You can close this tab and go back to the terminal.")
        threading.Thread(target=self.server.shutdown, daemon=True).start()
    def log_message(self, *a): pass


url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
    "client_id": cid, "redirect_uri": redirect, "response_type": "code", "scope": " ".join(SCOPES),
    "access_type": "offline", "prompt": "consent", "state": state})
print("Opening the Google consent page. Sign in as the channel's Google account.\nIf no browser opens, visit:\n" + url)
webbrowser.open(url)
http.server.HTTPServer(("127.0.0.1", PORT), H).serve_forever()
if "code" not in got: sys.exit("no authorisation code received")
data = urllib.parse.urlencode({"code": got["code"], "client_id": cid, "client_secret": sec, "redirect_uri": redirect, "grant_type": "authorization_code"}).encode()
r = json.load(urllib.request.urlopen("https://oauth2.googleapis.com/token", data, timeout=60))
if "refresh_token" not in r: sys.exit("Google returned no refresh token: " + json.dumps({k: v for k, v in r.items() if k != "access_token"}))
print("\nGranted:", r.get("scope"))
print("\nNew refresh token (keep it secret; paste into Vercel as G_YT_TOKEN):\n\n" + r["refresh_token"] + "\n")
