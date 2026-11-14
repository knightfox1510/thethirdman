"""Write site/data/drive.json: for every video, its Drive folder and the links to its files.
    python3 drive_links.py            # needs the Google credentials (env or /dev/shm), same as publish/drive.py
Read-only: it only lists folders the channel's Drive app created. Folder/file links open only for the Drive owner."""
import json, os, sys, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "publish"))
from gauth import api  # noqa: E402

D = "https://www.googleapis.com/drive/v3/files"
FOLDER = "application/vnd.google-apps.folder"
q = lambda s: s.replace("\\", "\\\\").replace("'", "\\'")


def one(name, parent=None):
    qs = f"name='{q(name)}' and mimeType='{FOLDER}' and trashed=false" + (f" and '{parent}' in parents" if parent else "")
    r = api("GET", D, "drive", params={"q": qs, "fields": "files(id,webViewLink)"})
    return (r.get("files") or [None])[0]


def kids(parent):
    out, tok = [], None
    while True:
        p = {"q": f"'{parent}' in parents and trashed=false", "fields": "nextPageToken,files(id,name,mimeType,size,webViewLink)", "pageSize": 1000}
        if tok: p["pageToken"] = tok
        r = api("GET", D, "drive", params=p); out += r.get("files", []); tok = r.get("nextPageToken")
        if not tok: return out


def kind(name):
    n = name.lower()
    if n.endswith(".srt"): return "subtitles"
    if n.endswith((".jpg", ".png")): return "cover" if "cover" in n else "thumbnail"
    if n.endswith(".mp4"): return "short" if ("short" in n or "9x16" in n) else "long"
    if n.endswith(".txt"): return "text"
    return "other"


def main():
    root = one("The Third Man")
    if not root: raise SystemExit("no 'The Third Man' folder found in Drive")
    sroot = one("Series", root["id"])
    out = {"root": f"https://drive.google.com/drive/folders/{root['id']}", "synced": datetime.date.today().isoformat(), "videos": {}, "series": {}}
    if not sroot: raise SystemExit("no 'Series' folder yet: run publish/drive_migrate.py --apply")
    for sf in sorted(kids(sroot["id"]), key=lambda x: x["name"]):
        if sf["mimeType"] != FOLDER: continue
        out["series"][sf["name"]] = {"folder": sf.get("webViewLink"), "episodes": []}
        for ef in sorted(kids(sf["id"]), key=lambda x: x["name"]):
            if ef["mimeType"] != FOLDER: continue
            meta = api("GET", f"{D}/{ef['id']}", "drive", params={"fields": "id,name,appProperties,webViewLink"})
            slug = (meta.get("appProperties") or {}).get("slug") or ef["name"]
            files = [dict(name=x["name"], kind=kind(x["name"]), mb=round(int(x.get("size", 0)) / 1e6, 1), url=x.get("webViewLink"))
                     for x in kids(ef["id"]) if x["mimeType"] != FOLDER]
            state = "posted" if ef["name"].endswith("[posted]") else "not posted"
            out["videos"][slug] = {"state": state, "series": sf["name"], "episode": ef["name"], "folder": ef.get("webViewLink") or f"https://drive.google.com/drive/folders/{ef['id']}", "files": files}
            out["series"][sf["name"]]["episodes"].append(slug)
            print(f"  {sf['name']:22s} {ef['name'][:60]:60s} {state:10s} {len(files)} files")
    json.dump(out, open(os.path.join(HERE, "site", "data", "drive.json"), "w"), indent=1)
    print(f"{len(out['videos'])} video folders -> site/data/drive.json")


if __name__ == "__main__":
    main()
