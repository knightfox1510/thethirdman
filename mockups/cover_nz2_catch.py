"""Cover / thumbnail for 'The Third Slip That Wasn't There' (Replay Room Ep 11): the Jurel catch photo (owner-supplied), grid-safe band y 300-1620, 1080x1920."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import skia, gfx, engine
from gfx import text, rrect, paint
W, H = 1080, 1920; CORAL = (255, 96, 96); NAVY = (8, 14, 34)
s = skia.Surface(W, H); c = s.getCanvas()
sh = skia.GradientShader.MakeLinear([(0, 0), (0, H)], [skia.Color(8, 14, 34), skia.Color(24, 26, 60)]); c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=sh))
c.drawCircle(W / 2, 1050, 700, paint((255, 96, 96), .10, blur=120))
wd = gfx.twidth("THE REPLAY ROOM · EP. 11", 40, "interB", 2) + 70; rrect(c, (W - wd) / 2, 330, wd, 84, 42, CORAL, 1); text(c, "THE REPLAY ROOM · EP. 11", W / 2, 388, 40, "interB", (10, 14, 30), 1, "c", track=2)
im = skia.Image.open("data/licensed/in/nz2_jurel_catch.webp"); cx0, cy0, cx1, cy1 = 400, 197, 1280, 852
x, y, w, h = 70, 470, 940, 700
c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y + 14, w, h), 36, 36), paint((0, 0, 0), .45, blur=26))
c.save(); c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), 36, 36), doAntiAlias=True)
c.drawImageRect(im, skia.Rect.MakeLTRB(cx0, cy0, cx1, cy1), skia.Rect.MakeXYWH(x, y, w, h), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear), paint((255, 255, 255), 1)); c.restore()
c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), 36, 36), paint(CORAL, 1, stroke=6))
wt = gfx.twidth("DHRUV JUREL · BACKWARD SHORT LEG", 28, "monoSB", 2) + 50; rrect(c, x + 28, y + 28, wt, 56, 12, (10, 14, 30), .85); text(c, "DHRUV JUREL · BACKWARD SHORT LEG", x + 53, y + 66, 28, "monoSB", (255, 255, 255), 1, "l", track=2)
text(c, "THE TRAP", W / 2, 1335, 128, "interB", (255, 255, 255), 1, "c", track=-3); text(c, "THAT WORKED", W / 2, 1465, 128, "interB", CORAL, 1, "c", track=-3)
text(c, "5 EDGES · 20 RUNS · NO THIRD SLIP", W / 2, 1540, 34, "monoSB", (200, 206, 230), 1, "c", track=3)
s.makeImageSnapshot().save("data/_tmp_cover.png")
