"""Instagram extras built from a spec's existing scenes.

    python3 variants.py deepcut  specs/<slug>.json   # vertical 90-150 s "deep cut" Reel from spec["ig"]
    python3 variants.py carousel specs/<slug>.json   # 4:5 carousel slides from spec["carousel"]
    python3 variants.py igshort  specs/<slug>.json   # Instagram version of the Short: same video, end card says "full breakdown on YouTube, link in bio"

spec["ig"]       = list of {"vo", "scene"} like "short" (usually long-form scenes, minus the intro, plus a YouTube CTA)
spec["carousel"] = {"cover": {"kicker", "lines", "hero"}, "slides": [["long", i], ...], "cta": {"lines", "pill"}, "caption": "..."}
Output lands in deliver/<slug>/ next to the other files."""
import copy, json, os, re, shutil, subprocess, sys
import numpy as np, skia
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)


# Instagram viewers can't see a YouTube "subscribe" button: their end card points to YouTube and the bio link. (YouTube's own version
# keeps the spec's end card, ideally the YT_CTA below.) Handle and logo: brand/ and the owner's channel id.
YT_HANDLE = "@thethirdman_angle"            # YouTube (underscore)
IG_HANDLE = "@thethirdman.angle"            # Instagram (dot)
IG_CTA = {"vo": "The full breakdown is on YouTube. The link is in our bio.",
          "scene": {"type": "cta", "lines": [{"t": "FULL BREAKDOWN"}, {"t": "ON YOUTUBE", "c": "gold"}], "yt": {"label": "THE THIRD MAN", "handle": "YOUTUBE " + YT_HANDLE, "bio": "LINK IN BIO"}}}
YT_CTA = {"vo": "Want the full breakdown? Subscribe to The Third Man on YouTube.",
          "scene": {"type": "cta", "lines": [{"t": "WANT THE FULL"}, {"t": "BREAKDOWN?", "c": "gold"}], "yt": {"label": "THE THIRD MAN", "handle": YT_HANDLE, "sub": "SUBSCRIBE · INSTAGRAM " + IG_HANDLE, "bio": None}}}


# Shorts with no long video of their own: don't promise a "full breakdown" (the replay extras do have one: their episode's long)
IG_CTA_MORE = {"vo": "More cricket analysis on YouTube. The link is in our bio.",
               "scene": {"type": "cta", "lines": [{"t": "MORE CRICKET"}, {"t": "ON YOUTUBE", "c": "gold"}], "yt": {"label": "THE THIRD MAN", "handle": "YOUTUBE " + YT_HANDLE, "bio": "LINK IN BIO"}}}
LONG_COMPANION = {"replay_4odi_young", "replay_4odi_dots", "henry_6balls"}


def igshort(spec_path):
    """Build deliver/<slug>/<short file>_IG.mp4 (+ .srt, cover): the Short with its last (end-card) scene replaced by the Instagram end card.
    Narration is cached per paragraph, so only the new last line is voiced: the cache of the main Short is copied across first."""
    spec = json.load(open(spec_path)); slug = spec["slug"]
    if spec.get("pairs"):                                  # Flip format: flips.py draws its own IG end card
        import flips; flips.build(spec_path, ig=True)
        print("caption:", write_caption(spec_path)); print("cover:", write_cover(spec_path)); return
    v = copy.deepcopy(spec); v["slug"] = f"{slug}__igshort"
    cta = spec.get("ig_cta") or (IG_CTA if (spec.get("long") or slug in LONG_COMPANION) else IG_CTA_MORE)
    sc = v["short"]; last_is_cta = sc and sc[-1]["scene"].get("type") == "cta"
    if not last_is_cta:                                   # a spoken "Follow for the full breakdown." closing line is replaced by the IG end card
        import re
        sc[-1]["vo"] = re.sub(r"\s*(Follow|Subscribe)[^.!?]*[.!?]\s*$", "", sc[-1]["vo"]).strip()
    v["short"] = (sc[:-1] if last_is_cta else sc) + [cta]
    base = spec["files"]["short"]; v["files"] = {"short": base + "_IG", "long": "_unused"}
    v.pop("long", None); v.pop("burn_captions", None)
    src_vo, dst_vo = f"{ROOT}/out/{slug}/short/vo", f"{ROOT}/out/{slug}__igshort/short/vo"
    if os.path.isdir(src_vo):                               # always start from the main video's CURRENT narration: a stale copy (older text/timings) made two clips overlap
        shutil.rmtree(dst_vo, ignore_errors=True); shutil.copytree(src_vo, dst_vo)
    os.makedirs(f"{ROOT}/out/_variants", exist_ok=True)
    vp = f"{ROOT}/out/_variants/{slug}__igshort.json"; json.dump(v, open(vp, "w"), ensure_ascii=False)
    subprocess.run(["python3", f"{ROOT}/engine.py", "build", vp, "short"], check=True)
    src, dst = f"{ROOT}/deliver/{slug}__igshort", f"{ROOT}/deliver/{slug}"
    os.makedirs(dst, exist_ok=True)
    for f in os.listdir(src):
        if f.startswith(base + "_IG") and f.endswith((".mp4", ".srt", ".jpg")): shutil.move(os.path.join(src, f), os.path.join(dst, f))
    shutil.rmtree(src, ignore_errors=True)
    print("IG version:", f"{dst}/{base}_IG.mp4"); print("caption:", write_caption(spec_path)); print("cover:", write_cover(spec_path))


IG_REEL_CTA = {"vo": "Tell us what you think in the comments. For the full breakdown, follow The Third Man on YouTube. Link in bio.",
               "scene": IG_CTA["scene"]}


def igreel(spec_path):
    """Extended vertical Instagram Reel (about 2.5 minutes: Instagram stops recommending Reels over 3 minutes) from spec["reel"]: more of the story than the 70-second
    Short, with the "full breakdown on YouTube, link in bio" end card. Writes deliver/<slug>/<long name with _Long -> _Reel_9x16>_IG.mp4 (+ .srt) and _IG_caption.txt."""
    spec = json.load(open(spec_path)); slug = spec["slug"]
    v = copy.deepcopy(spec); v["slug"] = f"{slug}__igreel"
    v["short"] = spec["reel"] + [spec.get("reel_cta") or IG_REEL_CTA]
    base = spec["files"]["long"].replace("_Long", "") + "_Reel_9x16_IG"
    v["files"] = {"short": base, "long": "_unused"}; v.pop("long", None); v.pop("burn_captions", None)
    os.makedirs(f"{ROOT}/out/_variants", exist_ok=True)
    vp = f"{ROOT}/out/_variants/{slug}__igreel.json"; json.dump(v, open(vp, "w"), ensure_ascii=False)
    subprocess.run(["python3", f"{ROOT}/engine.py", "build", vp, "short"], check=True)
    src, dst = f"{ROOT}/deliver/{slug}__igreel", f"{ROOT}/deliver/{slug}"
    for f in os.listdir(src):
        if f.startswith(base) and f.endswith((".mp4", ".srt")): shutil.move(os.path.join(src, f), os.path.join(dst, f))
    shutil.rmtree(src, ignore_errors=True)
    cap = spec.get("reel_caption") or caption_text(spec)   # a spec may carry its own Reel caption when the Reel covers different ground than the Short
    open(f"{dst}/{base}_caption.txt", "w", encoding="utf-8").write(cap)
    print("IG reel:", f"{dst}/{base}.mp4")


def igfull(spec_path):
    """Full-detail vertical version: the whole narration of the long video, re-laid out in 9:16 as stadium-stage scenes (spec["full"], see make_aaryavir_full.py),
    with the Instagram end card. Over 3 minutes, so Instagram will not push it as a Reel: post it as a regular video for people who want the whole story.
    Writes deliver/<slug>/<long name with _Long -> _Full_9x16>_IG.mp4 (+ .srt) and _IG_caption.txt."""
    spec = json.load(open(spec_path)); slug = spec["slug"]
    v = copy.deepcopy(spec); v["slug"] = f"{slug}__igfull"
    v["short"] = spec["full"] + [spec.get("reel_cta") or IG_REEL_CTA]
    if spec.get("full_theme"): v["theme"] = spec["full_theme"]                       # e.g. a lab-look Data Story whose vertical long is stadium-stage scenes
    if spec.get("full_captions"): v["captions"] = spec["full_captions"]
    base = spec["files"]["long"].replace("_Long", "") + "_Full_9x16_IG"
    v["files"] = {"short": base, "long": "_unused"}; v.pop("long", None); v.pop("burn_captions", None)
    os.makedirs(f"{ROOT}/out/_variants", exist_ok=True)
    vp = f"{ROOT}/out/_variants/{slug}__igfull.json"; json.dump(v, open(vp, "w"), ensure_ascii=False)
    subprocess.run(["python3", f"{ROOT}/engine.py", "build", vp, "short"], check=True)
    src, dst = f"{ROOT}/deliver/{slug}__igfull", f"{ROOT}/deliver/{slug}"
    for f in os.listdir(src):
        if f.startswith(base) and f.endswith((".mp4", ".srt")): shutil.move(os.path.join(src, f), os.path.join(dst, f))
    shutil.rmtree(src, ignore_errors=True)
    open(f"{dst}/{base}_caption.txt", "w", encoding="utf-8").write(spec.get("reel_caption") or caption_text(spec))     # the Instagram caption written for the vertical cut, else the generic one
    print("IG full vertical:", f"{dst}/{base}.mp4")


def iglab(spec_path):
    """Vertical Instagram Reel in The Lab look (no avatars): editorial-paper lab scenes picked from spec["long"] by spec["lab_reel"] (indices), 9:16, with the
    Instagram end card. Writes deliver/<slug>/<long name with _Long -> _Lab_9x16>_IG.mp4 (+ .srt) and _IG_caption.txt."""
    spec = json.load(open(spec_path)); slug = spec["slug"]
    v = copy.deepcopy(spec); v["slug"] = f"{slug}__iglab"
    v["short"] = [copy.deepcopy(spec["long"][i]) for i in spec["lab_reel"]]
    for sc in v["short"]: sc["scene"]["vert"] = True
    v["short"].append(spec.get("reel_cta") or IG_REEL_CTA)
    v["theme"] = spec.get("theme_long", "lab"); v["captions"] = spec.get("captions_long") or "lab"
    base = spec["files"]["long"].replace("_Long", "") + "_Lab_9x16_IG"
    v["files"] = {"short": base, "long": "_unused"}; v.pop("long", None); v.pop("burn_captions", None)
    os.makedirs(f"{ROOT}/out/_variants", exist_ok=True)
    vp = f"{ROOT}/out/_variants/{slug}__iglab.json"; json.dump(v, open(vp, "w"), ensure_ascii=False)
    subprocess.run(["python3", f"{ROOT}/engine.py", "build", vp, "short"], check=True)
    src, dst = f"{ROOT}/deliver/{slug}__iglab", f"{ROOT}/deliver/{slug}"
    for f in os.listdir(src):
        if f.startswith(base) and f.endswith((".mp4", ".srt")): shutil.move(os.path.join(src, f), os.path.join(dst, f))
    shutil.rmtree(src, ignore_errors=True)
    open(f"{dst}/{base}_caption.txt", "w", encoding="utf-8").write(caption_text(spec))
    print("IG lab reel:", f"{dst}/{base}.mp4")


IG_LONG_CTA = {"vo": "Want more detailed breakdowns like this? Follow The Third Man on YouTube. Link in bio.",
               "scene": {"type": "cta", "lines": [{"t": "MORE DETAILED"}, {"t": "BREAKDOWNS ON YOUTUBE", "c": "gold"}],
                         "yt": {"label": "THE THIRD MAN", "handle": "YOUTUBE " + YT_HANDLE, "sub": "FOLLOW FOR SIMILAR DEEP DIVES", "bio": "LINK IN BIO"}}}


def iglong(spec_path):
    """Instagram version of the full-length video: same video, the end card says "follow The Third Man on YouTube for more detailed breakdowns, link in bio".
    Writes deliver/<slug>/<long name>_IG.mp4 (+ .srt) and <long name>_IG_caption.txt. Narration cache is copied, so only the new last line is voiced."""
    spec = json.load(open(spec_path)); slug = spec["slug"]; base = spec["files"]["long"]
    v = copy.deepcopy(spec); v["slug"] = f"{slug}__iglong"
    sc = v["long"]
    if sc[-1]["scene"].get("type") == "cta":
        keep = re.sub(r"[^.!?]*\b(follow|subscribe)\b[^.!?]*[.!?]\s*$", "", sc[-1]["vo"], flags=re.I).strip()
        sc[-1] = {"vo": (keep + " " + (spec.get("iglong_vo") or IG_LONG_CTA["vo"])).strip(), "scene": IG_LONG_CTA["scene"]}      # spec "iglong_vo": reuse an already-narrated end line (no ElevenLabs credits)
    else: sc.append(IG_LONG_CTA)
    v["files"] = {"long": base + "_IG", "short": "_unused"}; v.pop("short", None); v.pop("burn_captions", None)
    src_vo, dst_vo = f"{ROOT}/out/{slug}/long/vo", f"{ROOT}/out/{slug}__iglong/long/vo"
    if os.path.isdir(src_vo):                               # always start from the main video's CURRENT narration: a stale copy (older text/timings) made two clips overlap
        shutil.rmtree(dst_vo, ignore_errors=True); shutil.copytree(src_vo, dst_vo)
    os.makedirs(f"{ROOT}/out/_variants", exist_ok=True)
    vp = f"{ROOT}/out/_variants/{slug}__iglong.json"; json.dump(v, open(vp, "w"), ensure_ascii=False)
    subprocess.run(["python3", f"{ROOT}/engine.py", "build", vp, "long"], check=True)
    src, dst = f"{ROOT}/deliver/{slug}__iglong", f"{ROOT}/deliver/{slug}"
    for f in os.listdir(src):
        if f.startswith(base + "_IG") and f.endswith((".mp4", ".srt")): shutil.move(os.path.join(src, f), os.path.join(dst, f))
    shutil.rmtree(src, ignore_errors=True)
    y = (spec.get("yt") or {}).get("long", {}); title = y.get("title", slug)
    parts = [x.strip() for x in title.split(" | ")]; first = y.get("description", "").split("\n\n")[0]
    first = re.split(r"\s*(?:Data:|Sources?:)", re.sub(r"#\w+", "", first))[0].strip()
    cap = (parts[0] + ".\n" + (parts[1] if len(parts) > 1 else "") + "\n\n" + first + "\n\nWant more detailed breakdowns like this? Follow The Third Man on YouTube (" + YT_HANDLE + "). Link in bio.\n\n"
           + " ".join(h for h in dict.fromkeys(re.findall(r"#\w+", y.get("description", "")) + BASE_TAGS) if len(h) <= 24 and h.lower() != "#shorts")[:300])
    open(f"{dst}/{base}_IG_caption.txt", "w", encoding="utf-8").write(cap)
    print("IG long:", f"{dst}/{base}_IG.mp4")


# ---------------------------------------------------------------- Instagram captions
BASE_TAGS = ["#cricket", "#cricketanalysis", "#cricketstats", "#TheThirdMan"]


def _hashtag(s):
    w = re.sub(r"[^A-Za-z0-9 ]+", " ", s).split()
    return "#" + "".join(x if x.isupper() else x[:1].upper() + x[1:] for x in w) if w else ""


def caption_text(spec):
    """Instagram caption for a spec's Short: hook, context, call to action (YouTube + link in bio), hashtags."""
    y = (spec.get("yt") or {}).get("short") or (spec.get("yt") or {}).get("long") or {}
    import voice_lint
    sm_ = voice_lint.show_map()
    en = lambda s: " ".join(sm_.get(w, w) for w in s.split())
    sys.path.insert(0, f"{ROOT}/publish"); import series as _series
    inf = _series.info(spec["slug"])
    if not y.get("title") and inf:                       # older specs have no yt block: build from the episode name and the narration
        narr = [s_ for sc_ in (spec.get("short") or []) for s_ in re.split(r"(?<=[.!?])\s+", en(sc_.get("vo", ""))) if s_ and not re.search(r"[\u0900-\u097F]", s_)]
        y = {"title": inf["subject"] + " | " + inf["series_name"], "description": " ".join(narr[:3]),
             "tags": [inf["series_name"], inf["subject"]]}
    title = re.sub(r"#\w+", "", y.get("title", "")).strip(" |")
    parts = [x.strip() for x in title.split(" | ") if x.strip()]
    hook = re.sub(r"[^\w\s:'’,.?!%&-]", "", parts[0] if parts else spec["slug"]).strip()          # no emoji in the hook
    if re.match(r"(Is|Does|Can|Why|Who|How|Will|Did|Are)\b", hook) and hook[-1] not in ".!?": hook += "?"
    ctx = parts[1] if len(parts) > 1 else ""
    desc = y.get("description", "")
    body = desc.split("\n\n")[0].replace("#Shorts\n", "").strip()
    body = re.sub(r"#\w+", "", body).strip()
    body = re.split(r"\s*(?:Data:|Sources?:|Full video on the channel)", body)[0].strip()
    sents = re.split(r"(?<=[.!?])\s+", body); out = ""
    for s_ in sents:
        if len(out) + len(s_) > 330: break
        out += (" " if out else "") + s_
    body = out
    has_long = bool(spec.get("long")) or spec.get("slug") in LONG_COMPANION
    q = ""                                               # the video's own comment prompt ("Was this the greatest Under nineteen final? Tell us in the comments"), Devanagari names back to English
    import voice_lint
    sm = voice_lint.show_map()
    for sc_ in reversed(spec.get("short") or []):
        v_ = " ".join(sm.get(w, w) for w in sc_.get("vo", "").split())
        m_ = re.search(r"([^.!?]*\?)\s*(Tell us[^.]*\.|Let us know[^.]*\.)?", v_)
        if m_ and "comments" in v_ and not re.search(r"[\u0900-\u097F]", m_.group(0)) and "Want the full" not in v_:
            q = re.sub(r"(comments)[^.]*\.", r"\1.", m_.group(0).strip()); break
    cta = ("Full breakdown on YouTube: The Third Man (" + YT_HANDLE + ")" if has_long else "More cricket analysis on YouTube: The Third Man (" + YT_HANDLE + ")") + ". Link in bio."
    tags = re.findall(r"#\w+", desc.replace("#Shorts", "")) + [_hashtag(t) for t in y.get("tags", []) if t.lower() not in ("the third man",)]
    seen, tagl = set(), []
    for h in tags + BASE_TAGS:
        if h and h.lower() not in seen and len(h) > 2: seen.add(h.lower()); tagl.append(h)
    tagl = [h for h in tagl if len(h) <= 24]
    lines = [hook + ("." if hook[-1] not in ".!?" else ""), ctx, "", body, "", q, "", cta, "", " ".join(tagl[:12])]
    return "\n".join(l for i, l in enumerate(lines) if l or (i and lines[i - 1])).strip() + "\n"


def write_cover(spec_path):
    """The Instagram cover (grid-safe, series-coded): <short name>_IG_cover.jpg, to pick when posting the Reel."""
    sys.path.insert(0, ROOT); import covers, engine as E
    spec = json.load(open(spec_path)); base = (spec.get("files") or {}).get("short")
    if not base or "unused" in base.lower() or not (spec.get("thumb") or spec["slug"] in covers.FLIP_COVER): return None
    if spec.get("ig_cover"): spec = dict(spec, thumb={**(spec.get("thumb") or {}), **spec["ig_cover"]})        # Instagram-only cover text (the YouTube thumbnail keeps spec["thumb"])
    E.apply_theme("stadium"); a = covers.render(spec); d = f"{ROOT}/deliver/{spec['slug']}"; os.makedirs(d, exist_ok=True)
    p = f"{d}/{base}_IG_cover.jpg"; skia_img = __import__("skia").Image.fromarray(a, colorType=__import__("skia").kRGBA_8888_ColorType); skia_img.save(p, __import__("skia").kJPEG, 92); return p


def write_caption(spec_path):
    spec = json.load(open(spec_path)); slug = spec["slug"]
    base = (spec.get("files") or {}).get("short")
    if not base or "unused" in base.lower(): return None
    d = f"{ROOT}/deliver/{slug}"; os.makedirs(d, exist_ok=True)
    path = f"{d}/{base}_IG_caption.txt"; open(path, "w", encoding="utf-8").write(caption_text(spec)); return path


def deepcut(spec_path):
    spec = json.load(open(spec_path)); slug = spec["slug"]
    v = copy.deepcopy(spec)
    v["slug"] = f"{slug}__ig"; v["short"] = spec["ig"]
    v["files"] = {"short": spec["files"].get("ig", spec["files"]["long"] + "_IG_DeepCut_9x16"), "long": "_unused"}
    v.pop("burn_captions", None)
    os.makedirs(f"{ROOT}/out/_variants", exist_ok=True)
    vp = f"{ROOT}/out/_variants/{slug}__ig.json"; json.dump(v, open(vp, "w"), ensure_ascii=False)
    subprocess.run(["python3", f"{ROOT}/engine.py", "build", vp, "short"], check=True)
    src, dst = f"{ROOT}/deliver/{slug}__ig", f"{ROOT}/deliver/{slug}"
    os.makedirs(dst, exist_ok=True)
    for f in os.listdir(src):
        if f.endswith((".mp4", ".srt")) and not f.startswith("_unused"): shutil.move(os.path.join(src, f), os.path.join(dst, f))
    shutil.rmtree(src, ignore_errors=True)
    print(f"{dst}/{v['files']['short']}.mp4")


def carousel(spec_path):
    import engine as E, gfx
    spec = json.load(open(spec_path)); slug = spec["slug"]; car = spec["carousel"]
    E.apply_theme(spec.get("theme", "whites")); spec["_intro"] = "fieldmap"
    g = E.setup("short")
    W, H, Y0 = 1080, 1350, 400          # 4:5 window cut from the 9:16 layout (skips the top chrome)
    out = f"{ROOT}/deliver/{slug}/carousel"; shutil.rmtree(out, ignore_errors=True); os.makedirs(out)

    def canvas():
        arr = np.zeros((g.H, g.W, 4), np.uint8); sf = skia.Surface(arr); return arr, sf, sf.getCanvas()

    def finish(arr, sf, k, n, crop=True):
        sf.flushAndSubmit()
        im = Image.fromarray(arr[..., :3].copy())
        im = im.crop((0, Y0, W, Y0 + H)) if crop else im
        sk = np.array(im.convert("RGBA")); s2 = skia.Surface(sk); c2 = s2.getCanvas()
        gfx.logo_lockup(c2, 70, H - 70, 54, 1)                                    # brand footer
        gfx.text(c2, f"{k}/{n}", W - 70, H - 56, 30, "interB", gfx.MUTED, 1, "r", track=2)
        s2.flushAndSubmit()
        Image.fromarray(sk[..., :3]).save(f"{out}/{k:02d}.jpg", quality=92)

    slides = car["slides"]; n = len(slides) + 2
    # 1. cover
    arr, sf, c = canvas(); gfx.background(c, 3)
    cv = car["cover"]; y = Y0 + 300
    if cv.get("kicker"):
        kw = E.twidth(cv["kicker"], 44, "bebas", 2) + 40
        E.rrect(c, W / 2 - kw / 2, y - 60, kw, 64, 8, E.GOLD); E.text(c, cv["kicker"], W / 2, y - 12, 44, "bebas", E.BG, 1, "c", track=2)
        y += 40
    for ln in cv["lines"]:
        z = E.fit(ln["t"], 940, 150, "bebas", 2); y += z * .9
        E.text(c, ln["t"], W / 2, y, z, "bebas", E.C(ln.get("c")), 1, "c", track=2)
    if cv.get("hero"):
        z = E.fit(cv["hero"], 900, 260, "bebas"); E.text(c, cv["hero"], W / 2, y + 60 + z * .8, z, "bebas", E.GOLD, 1, "c", glow=20)
    E.text(c, "SWIPE →", W / 2, Y0 + H - 170, 30, "interB", E.MUTED, 1, "c", track=6)
    finish(arr, sf, 1, n)
    # 2..n-1: scenes in their fully revealed state
    for k, (fmt, i) in enumerate(slides, 2):
        sc = spec[fmt][i]["scene"]
        arr, sf, c = canvas(); gfx.background(c, 3)
        E.SCENES[sc["type"]](c, g, 30.0, 30.5, sc)          # late in a long scene: everything on screen
        finish(arr, sf, k, n)
    # last: call to action
    arr, sf, c = canvas(); gfx.background(c, 3)
    y = Y0 + 380
    for ln in car["cta"]["lines"]:
        z = E.fit(ln["t"], 940, 130, "bebas", 2); y += z * .9
        E.text(c, ln["t"], W / 2, y, z, "bebas", E.C(ln.get("c")), 1, "c", track=2)
    pill = car["cta"].get("pill", "FULL BREAKDOWN ON YOUTUBE · LINK IN BIO")
    pw = E.twidth(pill, 30, "interB", 3) + 70
    E.rrect(c, W / 2 - pw / 2, y + 70, pw, 70, 35, E.GOLD); E.text(c, pill, W / 2, y + 116, 30, "interB", E.BG, 1, "c", track=3)
    finish(arr, sf, n, n)
    if car.get("caption"): open(f"{out}/caption.txt", "w").write(car["caption"] + "\n")
    print(out)


if __name__ == "__main__":
    {"deepcut": deepcut, "carousel": carousel, "igshort": igshort, "iglong": iglong, "igreel": igreel, "igfull": igfull, "iglab": iglab, "igcaption": lambda p: print(write_caption(p)), "igcover": lambda p: print(write_cover(p))}[sys.argv[1]](sys.argv[2])
