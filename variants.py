"""Instagram extras built from a spec's existing scenes.

    python3 variants.py deepcut  specs/<slug>.json   # vertical 90-150 s "deep cut" Reel from spec["ig"]
    python3 variants.py carousel specs/<slug>.json   # 4:5 carousel slides from spec["carousel"]

spec["ig"]       = list of {"vo", "scene"} like "short" (usually long-form scenes, minus the intro, plus a YouTube CTA)
spec["carousel"] = {"cover": {"kicker", "lines", "hero"}, "slides": [["long", i], ...], "cta": {"lines", "pill"}, "caption": "..."}
Output lands in deliver/<slug>/ next to the other files."""
import copy, json, os, shutil, subprocess, sys
import numpy as np, skia
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)


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
    {"deepcut": deepcut, "carousel": carousel}[sys.argv[1]](sys.argv[2])
