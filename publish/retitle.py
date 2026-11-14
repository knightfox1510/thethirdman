"""Sync title, description and tags of already-uploaded videos from their specs' "yt" blocks (so a naming change needs no re-upload).
    python3 publish/retitle.py [--dry-run] [--title-only] slug:fmt [slug:fmt ...]      e.g. replay_4odi:long hardik_arshdeep:short
Uses the newest non-deleted upload of each slug+format in publish/youtube_log.json. Descriptions are rebuilt exactly as youtube.py builds them
(footer, sources, chapters), so edits made by hand in Studio are overwritten unless --title-only is given."""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gauth import api
import youtube as Y

ap = argparse.ArgumentParser(); ap.add_argument("targets", nargs="+"); ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--title-only", action="store_true")
a = ap.parse_args()
log = json.load(open(Y.LOG))
for t in a.targets:
    slug, fmt = t.split(":")
    rec = next(r for r in reversed(log) if r["slug"] == slug and r["fmt"] == fmt and not r.get("deleted"))
    spec = json.load(open(os.path.join(Y.ROOT, "specs", f"{slug}.json")))
    title, desc, tags = Y.meta_for(spec, fmt)
    chap = os.path.join(Y.ROOT, "deliver", slug, spec["files"][fmt] + ".chapters.txt")
    if fmt == "long" and os.path.exists(chap):
        head, _, rest = desc.partition("\n\n"); desc = head + "\n\nChapters:\n" + open(chap).read().strip() + "\n\n" + rest
    live = api("GET", f"{Y.YT}/videos", "youtube", params={"part": "snippet", "id": rec["video_id"]})["items"][0]["snippet"]
    snip = {"title": title, "categoryId": live["categoryId"], "defaultLanguage": live.get("defaultLanguage", "en"), "defaultAudioLanguage": live.get("defaultAudioLanguage", "en-IN")}
    if a.title_only: snip.update(description=live.get("description", ""), tags=live.get("tags", []))
    else:
        if fmt == "long" and not os.path.exists(chap) and "Chapters:" in live.get("description", ""):
            print(f"  note: {slug} has no local chapters file; the live description keeps its chapters only if the spec text includes them")
        snip.update(description=desc, tags=tags)
    print(f"{slug}:{fmt} {rec['video_id']}\n   was: {live['title']}\n   now: {title}")
    if a.dry_run: continue
    api("PUT", f"{Y.YT}/videos", "youtube", body={"id": rec["video_id"], "snippet": snip}, params={"part": "snippet"})
    rec["title"] = title
json.dump(log, open(Y.LOG, "w"), indent=1, ensure_ascii=False)
