"""One-off (re-runnable) move of the channel's Drive folders into the series layout, with series file names.
    python3 publish/drive_migrate.py            # dry run: prints the plan
    python3 publish/drive_migrate.py --apply    # does it (Drive folders + files, local deliver/ files, specs' "files")
Per registered slug (publish/series.py): the legacy folder Videos/<slug> or Published_YT/<slug> becomes
Series/<NN Series>/<EpNN - Subject> [posted], tagged with appProperties slug=<slug>; files inside are renamed to the series names;
deliver/<slug>/ and specs/<slug>.json follow, so the next drive sync matches. Nothing is deleted."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import drive as Dr, series
from gauth import api

ROOT = os.path.dirname(HERE); D = Dr.D; FOLDER = Dr.FOLDER
APPLY = "--apply" in sys.argv


def rename_map(slug):
    sp = json.load(open(os.path.join(ROOT, "specs", f"{slug}.json")))
    old = (sp.get("files") or {}); new = series.file_names(slug)
    pairs = [(old[k], new[k]) for k in ("long", "short") if old.get(k) and "unused" not in old[k].lower()]
    return sorted(pairs, key=lambda p: -len(p[0]))                      # longest old prefix first


def new_name(n, pairs):
    for o, nw in pairs:
        if n.startswith(o): return nw + n[len(o):]
    return n


def main():
    root = Dr.folder("The Third Man")
    pub = Dr.find_child("Published_YT", root); vids = Dr.find_child("Videos", root)
    sroot = Dr.folder("Series", root) if APPLY else (Dr.find_child("Series", root) or "(new)")
    for slug in series.EPISODES:
        inf = series.info(slug); pairs = rename_map(slug)
        legacy, parent = None, None
        for par in (pub, vids):
            if par and Dr.find_child(slug, par): legacy, parent = Dr.find_child(slug, par), par; break
        tagged = Dr.by_slug(slug)
        target = inf["folder"] + (" [posted]" if Dr._posted(slug) else "")
        print(f"== {slug}: {'legacy ' + ('Published_YT' if parent == pub else 'Videos') if legacy else ('already in series layout' if tagged else 'no Drive folder (local rename only)')} -> {inf['series_dir']}/{target}")
        fid = legacy or (tagged and tagged["id"])
        if fid:
            for f in Dr.children(fid):
                nn = new_name(f["name"], pairs)
                if nn != f["name"]:
                    print(f"     {f['name']}  ->  {nn}")
                    if APPLY: api("PATCH", f"{D}/{f['id']}", "drive", body={"name": nn}, params={"fields": "id"})
            if legacy and APPLY:
                sdir = Dr.folder(inf["series_dir"], sroot)
                api("PATCH", f"{D}/{legacy}", "drive", body={"name": target, "appProperties": {"slug": slug}},
                    params={"addParents": sdir, "removeParents": parent, "fields": "id"})
        ldir = os.path.join(ROOT, "deliver", slug)                       # local files follow
        if os.path.isdir(ldir):
            for n in sorted(os.listdir(ldir)):
                nn = new_name(n, pairs)
                if nn != n:
                    print(f"     local {n}  ->  {nn}")
                    if APPLY: os.replace(os.path.join(ldir, n), os.path.join(ldir, nn))
        if APPLY:
            sp_path = os.path.join(ROOT, "specs", f"{slug}.json"); sp = json.load(open(sp_path))
            series.apply_names(sp); json.dump(sp, open(sp_path, "w"), ensure_ascii=False, indent=1)
    print("\\nDONE" if APPLY else "\\n(dry run: nothing changed; re-run with --apply)")


if __name__ == "__main__":
    main()
