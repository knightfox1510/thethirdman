"""Move the files of every episode folder in Drive into platform sub folders (YouTube/, Instagram/). Idempotent; moves, never copies or deletes.
    python3 publish/drive_platform.py            # dry run
    python3 publish/drive_platform.py --apply"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import drive as Dr
from gauth import api

apply = "--apply" in sys.argv
root = Dr.folder("The Third Man"); sroot = Dr.find_child("Series", root)
n = 0
for sf in Dr.children(sroot):
    if sf["mimeType"] != Dr.FOLDER: continue
    for ef in Dr.children(sf["id"]):
        if ef["mimeType"] != Dr.FOLDER: continue
        subs = {}
        for f in Dr.children(ef["id"]):
            if f["mimeType"] == Dr.FOLDER and f["name"] in ("YouTube", "Instagram"): continue
            plat = Dr.platform(f["name"], f["mimeType"] == Dr.FOLDER)
            n += 1; print(f"  {ef['name'][:45]:45s} {f['name'][:70]:70s} -> {plat}")
            if apply:
                if plat not in subs: subs[plat] = Dr.folder(plat, ef["id"])
                api("PATCH", f"{Dr.D}/{f['id']}", "drive", body={}, params={"addParents": subs[plat], "removeParents": ef["id"], "fields": "id"})
print(n, "items", "moved" if apply else "to move (dry run)")
