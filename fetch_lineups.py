"""Cache Sportmonks line-ups (incl. captain/keeper flags) for every cached IPL fixture: data/ipl/lineup_<id>.json"""
import glob, json, os, sys, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sm
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "ipl")


def one(fid):
    out = f"{D}/lineup_{fid}.json"
    if os.path.exists(out): return 0
    for k in range(5):
        try:
            r = sm.get(f"fixtures/{fid}", include="lineup")
            lu = r.get("lineup"); lu = lu["data"] if isinstance(lu, dict) else lu
            json.dump([{"id": p["id"], "name": p["fullname"], **(p.get("lineup") or {})} for p in (lu or [])], open(out, "w"))
            return 1
        except Exception as e:
            time.sleep(2 * (k + 1))
    return 0


ids = [int(os.path.basename(f)[3:-5]) for f in glob.glob(f"{D}/fx_*.json")]
with ThreadPoolExecutor(4) as ex: n = sum(ex.map(one, ids))
print("fetched", n, "of", len(ids))
