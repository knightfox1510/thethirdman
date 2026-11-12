"""Upload a finished video to The Third Man YouTube channel.
    python3 publish/youtube.py <slug> long|short [--privacy private|unlisted|public] [--publish-at 2026-11-20T18:00:00+05:30]
Reads title/description/tags from the spec's "yt" block (see README), uploads the video, then for long-form
also sets the custom thumbnail; both formats get the .srt uploaded as English captions. Every upload is recorded in
publish/youtube_log.json (video IDs only, no credentials).

Note: until the Google Cloud project passes YouTube's API audit, uploads are forced to PRIVATE by YouTube
whatever --privacy says; publish or schedule them in YouTube Studio."""
import argparse, datetime, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gauth import api, resumable, token
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "youtube_log.json")
YT = "https://www.googleapis.com/youtube/v3"
UP = "https://www.googleapis.com/upload/youtube/v3"
FOOTER = ("\n\n—\nThe Third Man · Cricket from a different angle\n"
          "Data: Sportmonks ball-by-ball where stated; other sources listed above.\n"
          "All graphics are original illustrations. Narration voice is AI-generated.\n"
          "Subscribe for data stories, tactics and What Ifs.")


def meta_for(spec, fmt):
    y = (spec.get("yt") or {}).get(fmt)
    if not y: raise SystemExit(f'spec {spec["slug"]} has no yt.{fmt} block (title, description, tags)')
    desc = y["description"].strip()
    src = [s for s in spec.get("sources", []) if s.startswith("http")]
    if fmt == "long" and src:
        desc += "\n\nSources:\n" + "\n".join(src)
    desc += FOOTER
    title = y["title"]
    if fmt == "short" and "#shorts" not in title.lower() and "#shorts" not in desc.lower():
        desc = "#Shorts\n" + desc
    assert len(title) <= 100, "YouTube titles are limited to 100 characters"
    assert len(desc) <= 5000, "YouTube descriptions are limited to 5000 characters"
    return title, desc, y.get("tags", [])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug"); ap.add_argument("fmt", choices=["long", "short"])
    ap.add_argument("--privacy", default="private", choices=["private", "unlisted", "public"])
    ap.add_argument("--publish-at", help="ISO time; schedules the video (implies private until then)")
    ap.add_argument("--thumb-only", action="store_true", help="only (re)set the thumbnail of the already-uploaded video")
    ap.add_argument("--delete", metavar="VIDEO_ID", help="delete one of our own earlier uploads (must be in youtube_log.json)")
    a = ap.parse_args()
    if a.delete:
        log = json.load(open(LOG))
        rec = next((r for r in log if r["video_id"] == a.delete and r["slug"] == a.slug), None)
        if not rec: raise SystemExit(f"{a.delete} is not one of our logged uploads for {a.slug}")
        api("DELETE", f"{YT}/videos", "youtube", params={"id": a.delete})
        rec["deleted"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
        json.dump(log, open(LOG, "w"), indent=1, ensure_ascii=False)
        print(f"deleted https://youtu.be/{a.delete}"); return
    if a.thumb_only:
        log = json.load(open(LOG))
        rec = next(r for r in reversed(log) if r["slug"] == a.slug and r["fmt"] == a.fmt)
        spec = json.load(open(os.path.join(ROOT, "specs", f"{a.slug}.json")))
        thumb = os.path.join(ROOT, "deliver", a.slug, spec["files"][a.fmt] + "_thumbnail.jpg")
        req = urllib.request.Request(f"{UP}/thumbnails/set?videoId={rec['video_id']}&uploadType=media", data=open(thumb, "rb").read(),
                                     method="POST", headers={"Authorization": "Bearer " + token("youtube"), "Content-Type": "image/jpeg"})
        urllib.request.urlopen(req, timeout=120); rec["thumbnail"] = True
        json.dump(log, open(LOG, "w"), indent=1, ensure_ascii=False)
        print(f"thumbnail set on https://youtu.be/{rec['video_id']}"); return
    spec = json.load(open(os.path.join(ROOT, "specs", f"{a.slug}.json")))
    out = os.path.join(ROOT, "deliver", a.slug)
    base = spec["files"][a.fmt]
    video = os.path.join(out, base + ".mp4")
    if not os.path.exists(video): raise SystemExit(f"missing {video}: build it first")
    title, desc, tags = meta_for(spec, a.fmt)
    chap = os.path.join(out, base + ".chapters.txt")
    if a.fmt == "long" and os.path.exists(chap):      # YouTube turns timestamps in the description into chapters
        head, sep, rest = desc.partition("\n\n")
        desc = head + "\n\nChapters:\n" + open(chap).read().strip() + "\n\n" + rest
    status = {"privacyStatus": "private" if a.publish_at else a.privacy, "selfDeclaredMadeForKids": False,
              "embeddable": True}
    if a.publish_at: status["publishAt"] = a.publish_at
    body = {"snippet": {"title": title, "description": desc, "tags": tags, "categoryId": "17",   # Sports
                        "defaultLanguage": "en", "defaultAudioLanguage": "en-IN"}, "status": status}
    print(f"uploading {os.path.basename(video)} ({os.path.getsize(video) / 1e6:.0f} MB) …")
    v = resumable(f"{UP}/videos?uploadType=resumable", "youtube", body, video, "video/mp4", params={"part": "snippet,status"})
    vid = v["id"]; print(f"  video: https://youtu.be/{vid}  (privacy: {v['status']['privacyStatus']})")
    rec = {"slug": a.slug, "fmt": a.fmt, "video_id": vid, "title": title,
           "uploaded": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
           "privacy": v["status"]["privacyStatus"], "publish_at": a.publish_at}
    if a.fmt == "long":
        thumb = os.path.join(out, base + "_thumbnail.jpg")
        if os.path.exists(thumb):
            req = urllib.request.Request(f"{UP}/thumbnails/set?videoId={vid}&uploadType=media", data=open(thumb, "rb").read(),
                                         method="POST", headers={"Authorization": "Bearer " + token("youtube"), "Content-Type": "image/jpeg"})
            try:
                urllib.request.urlopen(req, timeout=120); print("  thumbnail set"); rec["thumbnail"] = True
            except urllib.error.HTTPError as e:
                print(f"  thumbnail NOT set ({e.code}): {e.read().decode()[:300]}\n  (custom thumbnails need a phone-verified channel)")
    srt = os.path.join(out, base + ".srt")      # captions for long-form and Shorts
    if os.path.exists(srt):
        c = resumable(f"{UP}/captions?uploadType=resumable", "youtube",
                      {"snippet": {"videoId": vid, "language": "en", "name": "English", "isDraft": False}},
                      srt, "application/octet-stream", params={"part": "snippet"})
        print(f"  captions uploaded ({c.get('id')})"); rec["captions"] = True
    log = json.load(open(LOG)) if os.path.exists(LOG) else []
    log.append(rec); json.dump(log, open(LOG, "w"), indent=1, ensure_ascii=False)
    try:
        from drive import mark_published
        print("  drive:", mark_published(a.slug))
    except SystemExit as e:
        print("  drive: could not move folder:", e)
    print("done")


if __name__ == "__main__":
    main()
