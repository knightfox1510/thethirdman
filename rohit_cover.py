"""IG cover for the Rohit reel in the usual 'avatar' theme (navy base, series pill, hook, number sticker, logo; grid-safe band) with the owner-licensed cut-out in place of the illustrated player. python3 rohit_cover.py"""
import numpy as np, skia
from PIL import Image
import covers as C, engine as E, gfx
from covers import _navy, _pill, _hook, paint, rrect, text
W, H = 1080, 1920; SLUG = "rohit_mumbai_cha_raja"
spec = {"slug": SLUG, "thumb": {"lines": [{"t": "ROHIT IS"}, {"t": "MI CAPTAIN", "c": "gold"}], "hero": "6", "sub": "IPL 2027 · SIX TITLES"}}
C.PILL_OVERRIDE[SLUG] = {"pill": "MUMBAI CHA RAJA"} if isinstance(next(iter(C.PILL_OVERRIDE.values()), ""), dict) else "MUMBAI CHA RAJA"
th, inf, sid, acc, arr, sf, c = C._base(spec, W, H)
_navy(c, W, H, acc, 1160); _pill(c, W, inf, sid, acc); y_ = _hook(c, W, th, acc, 460, 175)
text(c, th["sub"], W / 2, y_ + 60, 52, "bebas", (255, 255, 255), 0.9, "c", track=6); sf.flushAndSubmit()
im = Image.fromarray(arr[:, :, :3]).convert("RGBA")
p = Image.open("data/licensed/cut/rohit_cape_trophies.png").convert("RGBA"); p = p.crop((0, 0, p.width, int(p.height * .875))); k = 700 / p.height; p = p.resize((int(p.width * k), 700), Image.LANCZOS)
al = np.asarray(p.split()[3]).astype(float); al *= np.clip((700 - np.arange(700)) / 110, 0, 1)[:, None]; p.putalpha(Image.fromarray(al.astype('uint8')))
im.alpha_composite(p, ((W - p.width) // 2 - 60, 880))
arr2 = np.zeros((H, W, 4), np.uint8); sf2 = skia.Surface(arr2); c2 = sf2.getCanvas()
cx, cy, r = 830, 1250, 150; c2.drawCircle(cx, cy, r + 14, paint((0, 0, 0), .35, blur=24)); c2.drawCircle(cx, cy, r, paint(acc, 1)); c2.drawCircle(cx, cy, r - 14, paint(acc, 1, stroke=5))
z = E.fit("6", 2 * r - 70, 250, "bebas"); text(c2, "6", cx, cy + z * .34, z, "bebas", C.NAVY, 1, "c"); gfx.logo_lockup(c2, W / 2, 1592, 72, 1, "c"); sf2.flushAndSubmit()
im.alpha_composite(Image.fromarray(arr2)); out = im.convert("RGB")
D = f"deliver/{SLUG}/Channel_Ep03_Mumbai_cha_Raja_Short_9x16_IG_cover"; out.save(D + ".jpg", quality=93); out.save(D.replace("_IG_cover", "_cover") + ".jpg", quality=93)
C.safe_zones(np.asarray(out.convert("RGBA")), "/tmp/safe.png"); print("ok")
