"""Sync finished videos to Google Drive, archiving the previous version.
    python3 publish/drive.py <slug> [<slug> ...]      # or: all
Layout in Drive:
    The Third Man/Videos/<slug>/            current files (long, Short, .srt, thumbnail, cover)
    The Third Man/Archive/<slug>/<YYYY-MM-DD HHMM>/   the version that was there before
A file is only re-uploaded (and the old one archived) when its contents changed (MD5 compare)."""
import datetime, hashlib, mimetypes, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gauth import api, resumable

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DELIVER = os.path.join(ROOT, "deliver")
FOLDER = "application/vnd.google-apps.folder"
D = "https://www.googleapis.com/drive/v3/files"


def q(s): return s.replace("\\", "\\\\").replace("'", "\\'")


def children(parent):
    out, tok = [], None
    while True:
        p = {"q": f"'{parent}' in parents and trashed=false", "fields": "nextPageToken,files(id,name,mimeType,md5Checksum)",
             "pageSize": 1000}
        if tok: p["pageToken"] = tok
        r = api("GET", D, "drive", params=p)
        out += r.get("files", []); tok = r.get("nextPageToken")
        if not tok: return out


def folder(name, parent=None):
    """Find or create a folder (drive.file scope only sees folders this app created)."""
    qs = f"name='{q(name)}' and mimeType='{FOLDER}' and trashed=false" + (f" and '{parent}' in parents" if parent else "")
    r = api("GET", D, "drive", params={"q": qs, "fields": "files(id)"})
    if r.get("files"): return r["files"][0]["id"]
    meta = {"name": name, "mimeType": FOLDER}
    if parent: meta["parents"] = [parent]
    return api("POST", D, "drive", body=meta, params={"fields": "id"})["id"]


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()


def sync(slug, root_id, stamp):
    src = os.path.join(DELIVER, slug)
    if not os.path.isdir(src): print(f"  skip {slug}: nothing in deliver/"); return
    vids = folder("Videos", root_id); arch_root = folder("Archive", root_id)
    cur = folder(slug, vids)
    existing = {f["name"]: f for f in children(cur)}
    arch = None
    for name in sorted(os.listdir(src)):
        path = os.path.join(src, name)
        if not os.path.isfile(path): continue
        old = existing.pop(name, None)
        if old and old.get("md5Checksum") == md5(path):
            print(f"  = {name} (unchanged)"); continue
        if old:   # move the previous version into the archive (no re-upload)
            arch = arch or folder(stamp, folder(slug, arch_root))
            api("PATCH", f"{D}/{old['id']}", "drive", body={}, params={"addParents": arch, "removeParents": cur, "fields": "id"})
            print(f"  ↳ archived old {name}")
        mime = mimetypes.guess_type(name)[0] or ("application/x-subrip" if name.endswith(".srt") else "application/octet-stream")
        resumable("https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable", "drive",
                  {"name": name, "parents": [cur]}, path, mime, params={"fields": "id"})
        print(f"  ↑ {name} ({os.path.getsize(path) / 1e6:.1f} MB)")
    for name, f in existing.items():   # files no longer produced: archive them too
        arch = arch or folder(stamp, folder(slug, arch_root))
        api("PATCH", f"{D}/{f['id']}", "drive", body={}, params={"addParents": arch, "removeParents": cur, "fields": "id"})
        print(f"  ↳ archived removed {name}")


if __name__ == "__main__":
    slugs = sys.argv[1:] or ["all"]
    if slugs == ["all"]: slugs = sorted(d for d in os.listdir(DELIVER) if os.path.isdir(os.path.join(DELIVER, d)))
    root_id = folder("The Third Man")
    stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30))).strftime("%Y-%m-%d %H%M")
    for s in slugs:
        print(f"== {s}"); sync(s, root_id, stamp)
    print(f"Drive folder: https://drive.google.com/drive/folders/{root_id}")
