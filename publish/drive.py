"""Sync finished videos to Google Drive, archiving the previous version.
    python3 publish/drive.py <slug> [<slug> ...]      # or: all   (upload)
    python3 publish/drive.py pull <slug> [<slug> ...] # download a slug's files into deliver/<slug>/
Layout in Drive:
    The Third Man/Videos/<slug>/            current files (long, Short, .srt, thumbnail, cover), not yet posted
    The Third Man/Published_YT/<slug>/      the same, once anything from it has been uploaded to YouTube
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


def sync_dir(src, cur, arch_parent, stamp, label=""):
    """Mirror one local folder into Drive folder `cur`; replaced/removed files go to arch_parent/<stamp>/."""
    existing = {f["name"]: f for f in children(cur)}
    arch = None

    def archive(f, why):
        nonlocal arch
        arch = arch or folder(stamp, arch_parent)
        api("PATCH", f"{D}/{f['id']}", "drive", body={}, params={"addParents": arch, "removeParents": cur, "fields": "id"})
        print(f"  ↳ archived {why} {label}{f['name']}")

    for name in sorted(os.listdir(src)):
        path = os.path.join(src, name)
        old = existing.pop(name, None)
        if os.path.isdir(path):   # e.g. carousel/
            sub = old["id"] if old and old.get("mimeType") == FOLDER else folder(name, cur)
            sync_dir(path, sub, folder(name, arch_parent), stamp, label + name + "/")
            continue
        if old and old.get("md5Checksum") == md5(path):
            print(f"  = {label}{name} (unchanged)"); continue
        if old: archive(old, "old")
        mime = mimetypes.guess_type(name)[0] or ("application/x-subrip" if name.endswith(".srt") else "application/octet-stream")
        resumable("https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable", "drive",
                  {"name": name, "parents": [cur]}, path, mime, params={"fields": "id"})
        print(f"  ↑ {label}{name} ({os.path.getsize(path) / 1e6:.1f} MB)")
    for name, f in existing.items():
        if f.get("mimeType") != FOLDER: archive(f, "removed")


def find_child(name, parent):
    r = api("GET", D, "drive", params={"q": f"name='{q(name)}' and mimeType='{FOLDER}' and trashed=false and '{parent}' in parents",
                                       "fields": "files(id)"})
    return r["files"][0]["id"] if r.get("files") else None


def video_folder(slug, root_id):
    """A video's folder lives in Videos/ until it is posted, then in Published_YT/."""
    pub = find_child("Published_YT", root_id)
    return (pub and find_child(slug, pub)) or folder(slug, folder("Videos", root_id))


def sync(slug, root_id, stamp):
    src = os.path.join(DELIVER, slug)
    if not os.path.isdir(src): print(f"  skip {slug}: nothing in deliver/"); return
    arch_root = folder("Archive", root_id)
    sync_dir(src, video_folder(slug, root_id), folder(slug, arch_root), stamp)


def mark_published(slug):
    """Move Videos/<slug> to Published_YT/<slug> (called after a YouTube upload)."""
    root_id = folder("The Third Man")
    pub = folder("Published_YT", root_id)
    if find_child(slug, pub): return "already in Published_YT"
    vids = folder("Videos", root_id); cur = find_child(slug, vids)
    if not cur: return "no Videos folder to move"
    api("PATCH", f"{D}/{cur}", "drive", body={}, params={"addParents": pub, "removeParents": vids, "fields": "id"})
    return "moved to Published_YT"


def pull(slug, root_id):
    """Download the current files of a video from Videos/ or Published_YT/ into deliver/<slug>/."""
    import urllib.request
    from gauth import token
    cur = video_folder(slug, root_id)
    dst = os.path.join(DELIVER, slug); os.makedirs(dst, exist_ok=True)
    for f in children(cur):
        if f["mimeType"] == FOLDER: continue
        path = os.path.join(dst, f["name"])
        if os.path.exists(path) and md5(path) == f.get("md5Checksum"): print(f"  same {f['name']}"); continue
        req = urllib.request.Request(f"{D}/{f['id']}?alt=media", headers={"Authorization": "Bearer " + token("drive")})
        with urllib.request.urlopen(req, timeout=600) as r, open(path + ".part", "wb") as o:
            for b in iter(lambda: r.read(1 << 20), b""): o.write(b)
        os.replace(path + ".part", path); print(f"  got  {f['name']}")


if __name__ == "__main__":
    if sys.argv[1:2] == ["pull"]:
        rid = folder("The Third Man")
        for s in sys.argv[2:]: print(f"== pull {s}"); pull(s, rid)
        sys.exit(0)
    slugs = sys.argv[1:] or ["all"]
    if slugs == ["all"]: slugs = sorted(d for d in os.listdir(DELIVER) if os.path.isdir(os.path.join(DELIVER, d)))
    root_id = folder("The Third Man")
    stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30))).strftime("%Y-%m-%d %H%M")
    for s in slugs:
        print(f"== {s}"); sync(s, root_id, stamp)
    print(f"Drive folder: https://drive.google.com/drive/folders/{root_id}")
