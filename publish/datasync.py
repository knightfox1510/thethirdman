"""Back up / restore the project files that git does NOT hold, via Drive (The Third Man/Data/Backup/), so any account or session can pick up exactly where another stopped.
    python3 publish/datasync.py push [raw] [vo <slug> ...]     # upload (skips what is unchanged: MD5 compare)
    python3 publish/datasync.py pull [raw] [vo <slug> ...]     # restore into this checkout
    python3 publish/datasync.py status                          # what is in Drive
Groups:
    raw  = owner captures (data/cricbuzz, data/cricinfo), data/players, data/capture_index.json, data/ipl_balls.pkl-free small data  (irreplaceable)
    vo   = cached narration for a slug (out/<slug>/*/vo): saves ElevenLabs credits when rebuilding (optional, per slug)
Not backed up (re-fetch): Cricsheet (python3 -m dataops.cricsheet fetch), Sportmonks IPL cache (SM_KEY python3 fetch_ipl.py), rendered videos (python3 publish/drive.py pull <slug>)."""
import hashlib, os, sys, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gauth import api, resumable, token
import drive as DR

ROOT = DR.ROOT
RAW = ["data/cricbuzz", "data/cricinfo", "data/players", "data/capture_index.json", "data/abhishek_t20i_ids.json", "data/index", "data/licensed"]


def bk_folder(): return DR.folder("Backup", DR.folder("Data", DR.folder("The Third Man")))


def pack(name, paths):
    z = f"/tmp/ttm_{name}.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in paths:
            ap = os.path.join(ROOT, p)
            if os.path.isfile(ap): zf.write(ap, p)
            elif os.path.isdir(ap):
                for d, _, fs in os.walk(ap):
                    for f in fs: zf.write(os.path.join(d, f), os.path.relpath(os.path.join(d, f), ROOT))
    return z


def push_one(name, paths):
    paths = [p for p in paths if os.path.exists(os.path.join(ROOT, p))]
    if not paths: print(f"  skip {name}: nothing local"); return
    z = pack(name, paths); fid = bk_folder(); fn = name + ".zip"
    old = [f for f in DR.children(fid) if f["name"] == fn]
    if old and old[0].get("md5Checksum") == DR.md5(z): print(f"  same {fn}"); return
    for f in old: api("PATCH", f"{DR.D}/{f['id']}", "drive", body={"trashed": True}, params={"fields": "id"})
    resumable("https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable", "drive", {"name": fn, "parents": [fid]}, z, "application/zip", params={"fields": "id"})
    print(f"  up   {fn} ({os.path.getsize(z) / 1e6:.0f} MB)")


def pull_one(name):
    import urllib.request
    fn = name + ".zip"; hit = [f for f in DR.children(bk_folder()) if f["name"] == fn]
    if not hit: print(f"  none in Drive: {fn}"); return
    z = f"/tmp/ttm_{name}.zip"
    req = urllib.request.Request(f"{DR.D}/{hit[0]['id']}?alt=media", headers={"Authorization": "Bearer " + token("drive")})
    with urllib.request.urlopen(req, timeout=900) as r, open(z, "wb") as o:
        for b in iter(lambda: r.read(1 << 20), b""): o.write(b)
    zipfile.ZipFile(z).extractall(ROOT); print(f"  got  {fn}")


def groups(args):
    out = []; i = 0
    while i < len(args):
        if args[i] == "raw": out.append(("raw", RAW)); i += 1
        elif args[i] == "vo":
            for s in args[i + 1:]:
                d = os.path.join(ROOT, "out", s)
                out.append((f"vo_{s}", [os.path.relpath(os.path.join(d, f, "vo"), ROOT) for f in (os.listdir(d) if os.path.isdir(d) else []) if os.path.isdir(os.path.join(d, f, "vo"))]))
            break
        else: raise SystemExit("usage: datasync.py push|pull|status [raw] [vo <slug> ...]")
    return out


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"; args = sys.argv[2:] or ["raw"]
    if cmd == "status":
        for f in DR.children(bk_folder()): print(f["name"])
    elif cmd == "push":
        for n, p in groups(args): push_one(n, p)
    elif cmd == "pull":
        for g in args[:1] if args[0] != "vo" else []: pull_one("raw")
        if "vo" in args:
            for s in args[args.index("vo") + 1:]: pull_one(f"vo_{s}")
