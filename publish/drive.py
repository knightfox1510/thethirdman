"""Sync finished videos to Google Drive, archiving the previous version.
    python3 publish/drive.py [--keep] <slug> [<slug> ...]      # or: all   (upload; --keep = never archive files missing locally)
    python3 publish/drive.py pull <slug> [<slug> ...] # download a slug's files into deliver/<slug>/
Layout in Drive:
    The Third Man/Series/<NN Series>/<EpNN - Subject>[ [posted]]/YouTube/ and /Instagram/   (platform sub folders; _IG files + carousels go to Instagram)
    (legacy) The Third Man/Videos/<slug>/            current files (long, Short, .srt, thumbnail, cover), not yet posted
    The Third Man/Published_YT/<slug>/      the same, once anything from it has been uploaded to YouTube
    The Third Man/Archive/<slug>/<YYYY-MM-DD HHMM>/   the version that was there before
A file is only re-uploaded (and the old one archived) when its contents changed (MD5 compare)."""
import datetime, hashlib, json, mimetypes, os, sys
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


def platform(name, isdir=False):
    """Which platform subfolder a deliverable belongs to: Instagram = the _IG files (reel, srt, cover, caption) and carousels; everything else YouTube."""
    return "Instagram" if (isdir or "_IG" in name) else "YouTube"


def sync_dir(src, cur, arch_parent, stamp, label="", keep=False, pick=None):
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
        if pick and not pick(name, os.path.isdir(path)): continue
        old = existing.pop(name, None)
        if os.path.isdir(path):   # e.g. carousel/
            sub = old["id"] if old and old.get("mimeType") == FOLDER else folder(name, cur)
            sync_dir(path, sub, folder(name, arch_parent), stamp, label + name + "/", keep)
            continue
        if old and old.get("md5Checksum") == md5(path):
            print(f"  = {label}{name} (unchanged)"); continue
        if old: archive(old, "old")
        mime = mimetypes.guess_type(name)[0] or ("application/x-subrip" if name.endswith(".srt") else "application/octet-stream")
        resumable("https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable", "drive",
                  {"name": name, "parents": [cur]}, path, mime, params={"fields": "id"})
        print(f"  ↑ {label}{name} ({os.path.getsize(path) / 1e6:.1f} MB)")
    for name, f in existing.items():
        if f.get("mimeType") != FOLDER and not keep: archive(f, "removed")


def find_child(name, parent):
    r = api("GET", D, "drive", params={"q": f"name='{q(name)}' and mimeType='{FOLDER}' and trashed=false and '{parent}' in parents",
                                       "fields": "files(id)"})
    return r["files"][0]["id"] if r.get("files") else None


def _posted(slug):
    """True once any non-deleted YouTube upload of this slug is logged."""
    try: log = json.load(open(os.path.join(ROOT, "publish", "youtube_log.json")))
    except Exception: return False
    return any(r["slug"] == slug and not r.get("deleted") for r in log)


def by_slug(slug):
    """The Drive folder tagged slug=<slug> (set by drive_migrate.py / created by video_folder), or None."""
    r = api("GET", D, "drive", params={"q": f"appProperties has {{ key='slug' and value='{q(slug)}' }} and mimeType='{FOLDER}' and trashed=false",
                                       "fields": "files(id,name,parents)"})
    return (r.get("files") or [None])[0]


def video_folder(slug, root_id):
    """Series layout: The Third Man / Series / <NN Series> / <EpNN - Subject> [posted]. A folder created before the series layout
    (Videos/<slug> or Published_YT/<slug>) is still found, until drive_migrate.py moves it."""
    f = by_slug(slug)
    if f: return f["id"]
    pub = find_child("Published_YT", root_id); vids = find_child("Videos", root_id)        # the legacy folders no longer exist once migrated: never query with an empty parent
    legacy = (pub and find_child(slug, pub)) or (vids and find_child(slug, vids))
    if legacy: return legacy
    import series
    inf = series.info(slug)
    sroot = folder("Series", root_id)
    parent = folder(inf["series_dir"], sroot) if inf else folder("00 Unsorted", sroot)
    name = (inf["folder"] if inf else slug) + (" [posted]" if _posted(slug) else "")
    meta = {"name": name, "mimeType": FOLDER, "parents": [parent], "appProperties": {"slug": slug}}
    return api("POST", D, "drive", body=meta, params={"fields": "id"})["id"]


def sync(slug, root_id, stamp, keep=False):
    src = os.path.join(DELIVER, slug)
    if not os.path.isdir(src): print(f"  skip {slug}: nothing in deliver/"); return
    arch_root = folder("Archive", root_id)
    vf = video_folder(slug, root_id)
    for plat in ("YouTube", "Instagram"):        # one sub folder per platform inside the episode folder
        if any(platform(n, os.path.isdir(os.path.join(src, n))) == plat for n in os.listdir(src)):
            sync_dir(src, folder(plat, vf), folder(plat, folder(slug, arch_root)), stamp, label=plat + "/", keep=keep,
                     pick=lambda n, d, p=plat: platform(n, d) == p)


def mark_published(slug):
    """After a YouTube upload: tag the episode folder " [posted]" (the series layout has no Videos/Published split)."""
    root_id = folder("The Third Man")
    f = by_slug(slug)
    if not f:
        pub = folder("Published_YT", root_id); vids = folder("Videos", root_id); cur = find_child(slug, vids)     # legacy folders
        if not cur: return "no Drive folder to mark"
        if find_child(slug, pub): return "already in Published_YT"
        api("PATCH", f"{D}/{cur}", "drive", body={}, params={"addParents": pub, "removeParents": vids, "fields": "id"})
        return "moved to Published_YT (legacy layout)"
    if f["name"].endswith("[posted]"): return "already marked posted"
    api("PATCH", f"{D}/{f['id']}", "drive", body={"name": f["name"] + " [posted]"}, params={"fields": "id"})
    return "marked [posted]"


def pull(slug, root_id):
    """Download the current files of a video from Videos/ or Published_YT/ into deliver/<slug>/."""
    import urllib.request
    from gauth import token
    cur = video_folder(slug, root_id)
    dst = os.path.join(DELIVER, slug); os.makedirs(dst, exist_ok=True)
    files = []
    for f in children(cur):                       # files sit in YouTube/ and Instagram/ sub folders (flat legacy folders still work)
        if f["mimeType"] == FOLDER and f["name"] in ("YouTube", "Instagram"):
            for g_ in children(f["id"]):
                if g_["mimeType"] != FOLDER: files.append(g_)
        elif f["mimeType"] != FOLDER: files.append(f)
    for f in files:
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
    keep = "--keep" in sys.argv                      # add/replace only: leave Drive files that are not in deliver/<slug> untouched
    slugs = [a for a in sys.argv[1:] if a != "--keep"] or ["all"]
    if slugs == ["all"]: slugs = sorted(d for d in os.listdir(DELIVER) if os.path.isdir(os.path.join(DELIVER, d)))
    root_id = folder("The Third Man")
    stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30))).strftime("%Y-%m-%d %H%M")
    for s in slugs:
        print(f"== {s}"); sync(s, root_id, stamp, keep)
    print(f"Drive folder: https://drive.google.com/drive/folders/{root_id}")
