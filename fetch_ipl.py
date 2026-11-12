"""Download and cache IPL ball-by-ball data (all seasons in the plan) plus player profiles from Sportmonks.
usage: SM_KEY=... python3 fetch_ipl.py [season ...]"""
import json, os, sys, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sm

D = os.path.join(sm.CACHE, "ipl"); os.makedirs(D, exist_ok=True)
P = os.path.join(sm.CACHE, "players"); os.makedirs(P, exist_ok=True)


def call(path, **params):
    for attempt in range(6):
        try:
            return sm.get(path, **params)
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(30 * (attempt + 1)); continue
            if attempt == 5: raise
            time.sleep(3)
        except Exception:
            if attempt == 5: raise
            time.sleep(3)


def season_fixtures(season):
    p = f"{D}/season_{season['name']}.json"
    if os.path.exists(p): return json.load(open(p))
    fx = call("fixtures", **{"filter[league_id]": "1", "filter[season_id]": str(season["id"]), "include": "localteam,visitorteam,venue", "sort": "starting_at"})
    json.dump(fx, open(p, "w")); return fx


def fixture(fid):
    p = f"{D}/fx_{fid}.json"
    if os.path.exists(p): return
    d = call(f"fixtures/{fid}", include="balls.score,runs,localteam,visitorteam,venue")
    # keep it compact: drop nested team objects from balls
    for b in (d.get("balls") or []):
        b["team"] = {"id": b["team"]["id"], "name": b["team"]["name"]} if b.get("team") else None
    json.dump(d, open(p, "w"))


def player(pid):
    p = f"{P}/{pid}.json"
    if os.path.exists(p): return
    d = call(f"players/{pid}")
    json.dump({k: d.get(k) for k in ("id", "fullname", "battingstyle", "bowlingstyle", "position", "country_id")}, open(p, "w"))


if __name__ == "__main__":
    lg = call("leagues/1", include="seasons")
    seasons = sorted(lg["seasons"], key=lambda s: s["name"])
    if len(sys.argv) > 1: seasons = [s for s in seasons if s["name"] in sys.argv[1:]]
    ids = []
    for s in seasons:
        fx = season_fixtures(s)
        done = [f["id"] for f in fx if f.get("status") == "Finished"]
        ids += done
        print(s["name"], len(done), "finished fixtures", flush=True)
    with ThreadPoolExecutor(4) as ex: list(ex.map(fixture, ids))
    print("fixtures cached", len(ids), flush=True)
    pids = set()
    for fid in ids:
        d = json.load(open(f"{D}/fx_{fid}.json"))
        for b in d.get("balls") or []:
            pids.update([b.get("batsman_id"), b.get("bowler_id")])
    pids.discard(None)
    with ThreadPoolExecutor(4) as ex: list(ex.map(player, sorted(pids)))
    print("players cached", len(pids), "DONE", flush=True)
