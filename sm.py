"""Sportmonks cricket helper: fetch + cache fixtures with ball-by-ball, classify bowling styles."""
import json, os, urllib.request
TOKEN = os.environ.get("SM_KEY", "")
BASE = "https://cricket.sportmonks.com/api/v2.0"
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
SPIN = ("orthodox", "break", "spin", "chinaman", "googly", "legbreak", "offbreak")


def get(path, **params):
    q = "&".join(f"{k}={v}" for k, v in params.items())
    with urllib.request.urlopen(f"{BASE}/{path}?api_token={TOKEN}&{q}", timeout=60) as r:
        return json.load(r)["data"]


def fixture(fid, refresh=False):
    p = f"{CACHE}/fx_{fid}.json"
    if os.path.exists(p) and not refresh:
        return json.load(open(p))
    d = get(f"fixtures/{fid}", include="balls.batsman,balls.bowler,balls.score,runs,localteam,visitorteam,venue")
    json.dump(d, open(p, "w"))
    return d


def balls(d):
    b = d["balls"]
    return b["data"] if isinstance(b, dict) else b


# Bowling styles missing from the feed, filled in by hand. Unknown styles are reported, never guessed.
STYLE_FIX = {"Michael Bracewell": "right-arm-offbreak"}
MISSING = set()


def kind(player):
    p = player or {}
    st = p.get("bowlingstyle") or STYLE_FIX.get(p.get("fullname"), "")
    if not st:
        MISSING.add(p.get("fullname"))
        return "unknown"
    return "spin" if any(k in st for k in SPIN) else "pace"


def phase(over_ball):
    o = int(over_ball)
    return "powerplay" if o < 6 else ("middle" if o < 15 else "death")


def get_all(path, **params):
    """Follow Sportmonks pagination and return every row."""
    out, page = [], 1
    while True:
        q = "&".join(f"{k}={v}" for k, v in {**params, "page": page}.items())
        with urllib.request.urlopen(f"{BASE}/{path}?api_token={TOKEN}&{q}", timeout=60) as r:
            d = json.load(r)
        out += d["data"]
        meta = (d.get("meta") or {})
        if not meta or meta.get("current_page", 1) >= meta.get("last_page", 1): break
        page += 1
    return out
