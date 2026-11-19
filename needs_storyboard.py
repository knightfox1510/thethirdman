"""Storyboard stills for the 'What every IPL team needs' Data Story (IPL 2027). Landscape 1920x1080, Lab look. python3 needs_storyboard.py"""
import json, os
from PIL import Image, ImageDraw
import trades_mockups as T
R = os.path.dirname(os.path.abspath(__file__)); O = f"{R}/out/storyboard_needs"; os.makedirs(O, exist_ok=True)
D = json.load(open(f"{R}/data/provenance/ipl2027_needs.json"))["teams"]
CREAM = (240, 235, 222); NAVY = (24, 34, 66); RED = (200, 50, 45); GREY = (120, 120, 130); GREEN = (40, 130, 90); AMB = (220, 150, 30)
ORDER = ["KKR", "CSK", "DC", "LSG", "SRH", "PBKS", "MI", "RR", "RCB", "GT"]
ROLES = [("bat_powerplay", "Bat PP"), ("bat_middle", "Bat mid"), ("bat_death", "Bat death"), ("pace_pp", "Pace PP"), ("spin_mid", "Spin mid"), ("pace_death", "Pace death")]
def logo(c): return Image.open(f"{R}/data/licensed/logos/{c}_{'light' if c=='RR' else 'dark'}.png").convert("RGBA")
def paste_logo(im, c, x, y, s):
    l = logo(c); l.thumbnail((s, s)); im.paste(l, (x + (s - l.width) // 2, y + (s - l.height) // 2), l)
def new(): return Image.new("RGB", (1920, 1080), CREAM)
def tx(d, xy, t, f, fill=NAVY, anchor="la"): d.text(xy, t, font=f, fill=fill, anchor=anchor)
def col(v): return RED if v < .7 else (AMB if v < .9 else GREEN)
def tag(d, n, name):
    tx(d, (40, 30), f"FRAME {n} · {name}", T.INTS(22), GREY); tx(d, (1880, 30), "STORYBOARD · NOT FINAL", T.INTS(22), RED, "ra")
def save(im, n): im.save(f"{O}/f{n}.png")
def val(r, k): v = r[k]; return v[0]
# 1 hook
im = new(); d = ImageDraw.Draw(im); tag(d, 1, "Hook (0-8 s)")
tx(d, (560, 250), "₹", T.INT(210), NAVY, "mm"); tx(d, (1000, 250), "298 CRORE", T.BEB(250), NAVY, "mm"); tx(d, (960, 430), "66 SLOTS  ·  10 TEAMS  ·  ONE AUCTION", T.BEB(80), RED, "mm")
for i, c in enumerate(ORDER): paste_logo(im, c, 140 + i * 165, 560, 140)
tx(d, (960, 800), "What every IPL team still needs", T.INT(66), NAVY, "mm"); tx(d, (960, 900), "Auction 16 Dec 2026 · Goa · needs from our ball-by-ball, IPL 2025-26", T.INTS(34), GREY, "mm"); save(im, 1)
# 2 purse
im = new(); d = ImageDraw.Draw(im); tag(d, 2, "Who has the money (8-30 s)")
tx(d, (120, 110), "Purse left (Rs crore)  ·  slots  ·  overseas", T.BEB(70))
pr = sorted(ORDER, key=lambda c: -D[c]["purse_cr"])
for i, c in enumerate(pr):
    y = 210 + i * 80; paste_logo(im, c, 110, y - 6, 70); w = int(D[c]["purse_cr"] / 47.45 * 1000)
    d.rounded_rectangle((200, y, 200 + w, y + 58), 8, fill=RED if c in ("GT", "RCB") else NAVY); tx(d, (210 + w, y + 29), f'{D[c]["purse_cr"]}', T.BEB(54), NAVY, "lm")
    tx(d, (1780, y + 29), f'{D[c]["slots"]} slots · {D[c]["overseas_slots"]} ovs', T.INTS(28), GREY, "rm")
save(im, 2)
# 3 heat map
im = new(); d = ImageDraw.Draw(im); tag(d, 3, "The need map (30-60 s)")
tx(d, (120, 100), "Capacity vs an average squad (1.00)", T.BEB(70)); tx(d, (120, 170), "red = thin (<0.70) · amber · green = deep   ·   our model, IPL 2025-26", T.INTS(26), GREY)
for j, (_, n) in enumerate(ROLES): tx(d, (560 + j * 215 + 90, 225), n, T.INTS(26), NAVY, "mm")
tx(d, (1860, 225), "Keepers", T.INTS(26), NAVY, "mm")
for i, c in enumerate(ORDER):
    y = 255 + i * 77; paste_logo(im, c, 110, y - 4, 66); tx(d, (200, y + 32), c, T.BEB(46), NAVY, "lm")
    for j, (k, _) in enumerate(ROLES):
        v = val(D[c], k); x = 560 + j * 215; d.rounded_rectangle((x, y, x + 180, y + 62), 10, fill=col(v)); tx(d, (x + 90, y + 31), f"{v:.2f}", T.BEB(44), (255, 255, 255), "mm")
    tx(d, (1860, y + 31), str(D[c]["keepers"]), T.BEB(44), RED if D[c]["keepers"] < 2 else NAVY, "mm")
save(im, 3)
# 4-5 team cards
LINE = {"KKR": ("Batting is thin in every phase", "one keeper · pace at 0.60 / 0.66", "Fits (our model): Nissanka (opener), Tushar Raheja (keeper lead), Pathirana (death pace)"),
        "CSK": ("Pace is the hole", "powerplay 0.48 · death 0.49", "Fits (our model): Boult, Pathirana, Prashant Veer buy-back")}
for n, c in ((4, "KKR"), (5, "CSK")):
    im = new(); d = ImageDraw.Draw(im); tag(d, n, f"Team card {n-3} of 10 (~25 s each)"); r = D[c]
    paste_logo(im, c, 100, 90, 300); tx(d, (460, 190), "₹", T.INT(150), NAVY); tx(d, (560, 160), f'{r["purse_cr"]} CR', T.BEB(190), NAVY); tx(d, (460, 340), f'{r["slots"]} slots · {r["overseas_slots"]} overseas', T.INTS(40), GREY)
    tx(d, (460, 430), LINE[c][0].upper(), T.BEB(80), RED); tx(d, (460, 520), LINE[c][1], T.INT(40), NAVY)
    for j, (k, nm) in enumerate(ROLES):
        v = val(r, k); x = 120 + j * 285; y = 640; d.rounded_rectangle((x, y, x + 250, y + 40), 8, fill=(215, 210, 195)); d.rounded_rectangle((x, y, x + int(250 * min(v, 1.3) / 1.3), y + 40), 8, fill=col(v)); tx(d, (x, y + 70), nm, T.INTS(28), NAVY); tx(d, (x + 250, y + 70), f"{v:.2f}", T.BEB(40), col(v), "ra")
    tx(d, (120, 850), LINE[c][2], T.INTS(34), NAVY); tx(d, (120, 960), "Illustrative reading of squad + purse, not a franchise plan", T.INTS(24), GREY); save(im, n)
# 6 pool
im = new(); d = ImageDraw.Draw(im); tag(d, 6, "The pool (3 min)")
tx(d, (120, 110), "What's in the pool", T.BEB(90)); tx(d, (120, 215), "released players only; the official list comes ~3 Dec", T.INTS(30), GREY)
for i, (h, s, c2) in enumerate([("PACE", "Boult · Pathirana · Chahar", GREEN), ("SPIN", "Hasaranga, then very little", RED), ("OPENERS", "Nissanka; Head reported out", AMB), ("FINISHERS", "Hetmyer 139 SR at the death vs ~171", RED)]):
    x = 120 + (i % 2) * 880; y = 300 + (i // 2) * 330; d.rounded_rectangle((x, y, x + 840, y + 290), 24, fill=(255, 255, 255), outline=c2, width=6); tx(d, (x + 40, y + 40), h, T.BEB(90), c2); tx(d, (x + 40, y + 170), s, T.INT(40), NAVY)
save(im, 6)
# 7 bids
im = new(); d = ImageDraw.Draw(im); tag(d, 7, "Who could draw the biggest bids (our model)")
tx(d, (120, 100), "Demand vs supply: who could go big", T.BEB(80)); tx(d, (120, 190), "OUR MODEL · opinion, not a price prediction", T.INTS(30), RED)
for i, (nm, w, buy) in enumerate([("Trent Boult", "pace both phases", ["LSG", "KKR", "DC", "CSK"]), ("Matheesha Pathirana", "best death bowler", ["LSG", "KKR", "DC", "CSK"]), ("Wanindu Hasaranga", "only proven wrist-spinner", ["MI", "SRH", "DC"]), ("Deepak Chahar", "Indian powerplay pace", ["LSG", "DC", "KKR", "PBKS"]), ("Pathum Nissanka", "best realistic opener", ["DC", "KKR", "SRH"])]):
    y = 270 + i * 150; tx(d, (150, y + 10), str(i + 1), T.BEB(110), RED); tx(d, (260, y + 5), nm.upper(), T.BEB(70)); tx(d, (260, y + 80), w, T.INTS(30), GREY)
    for j, c in enumerate(buy): paste_logo(im, c, 1180 + j * 150, y - 5, 120)
save(im, 7)
# 8 end
im = new(); d = ImageDraw.Draw(im); tag(d, 8, "Close (last 8 s)")
tx(d, (960, 330), "WHO WINS THE AUCTION?", T.BEB(150), NAVY, "mm"); tx(d, (960, 500), "Tell us in the comments", T.INT(60), RED, "mm"); tx(d, (960, 680), "Subscribe · @thethirdman_angle", T.INTS(46), NAVY, "mm")
for i, c in enumerate(ORDER): paste_logo(im, c, 140 + i * 165, 800, 140)
save(im, 8)
sheet = Image.new("RGB", (1920 * 2 // 2, 1080 * 4 // 2), (255, 255, 255))
for i in range(8):
    f = Image.open(f"{O}/f{i+1}.png").resize((960, 540)); sheet.paste(f, ((i % 2) * 960, (i // 2) * 540))
sheet.save(f"{O}/sheet.png"); print("ok")
