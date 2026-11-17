"""Builds specs/ipl_trades_2027.json: Channel Ep 2, "IPL 2027 trades: every deal" (long + Short), in the new TRADE SPLIT format (engine scene "tradesplit": the screen splits on a diagonal into
the two teams' colours, the players cross over, the incoming player's name and 2026 numbers appear). Photos: the owner's licensed images, cut out by cutout.py (data/licensed/cut).
Sources and how each claim is checked (dataops/verify.py, below):
  - The deals: the IPL's own press releases (iplt20.com/news, read 17 Nov 2026), Cricinfo trade stories (via search excerpts; the pages return 403 to us) and Oneindia's trade list.
  - Fees: the IPL's own graphics / statement where there is one (Hardik-Arshdeep, CSK-SRH, Pant-Kuldeep), a second source for each (iplretention.in tracker, Outlook, Cricinfo). The 17 Nov deal (Shami, Siddharth, Curran): no second source for the fees yet,
    so NO fee is stated for it.
  - 2026 numbers: Sportmonks ball-by-ball (data/provenance/trades_2026_figures.json), shown as 'OUR DATA'.
Deals (date, from the IPL press releases): Pant <-> Kuldeep (23 Jun), Natarajan -> SRH / Ansari -> DC (14 Oct), CSK <-> SRH four players (5 Nov), Hardik <-> Arshdeep (~11 Nov), Harshal -> GT (15 Nov), Shami + Siddharth -> RR / Curran -> LSG (17 Nov)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voice_lint
from dataops import verify as V
from variants import YT_CTA

F = json.load(open("data/provenance/trades_2026_figures.json"))
L = "data/licensed/cut/"
IPL, OWN, TRK, CI, OUT, OI, STA, YH = "ipl_official", "owner_graphic", "iplretention", "cricinfo", "outlook", "oneindia", "statesman", "yahoo"

c = V.Claims("ipl_trades_2027")
c.check("Pant to DC at 15 crore (down from the 27 crore LSG paid in 2025)", 15, {IPL: 15, OUT: 15}); c.check("Pant's 2025 auction price (crore)", 27, {IPL: 27, OUT: 27})
c.check("Kuldeep to LSG at 13.5 crore", 13.5, {IPL: 13.5, TRK: 13.5})
c.check("Natarajan to SRH at 5 crore", 5, {OWN: 5, TRK: 5}); c.check("Ansari to DC at 40 lakh", 40, {OWN: 40, TRK: 40})
c.check("Livingstone 6 crore", 6, {OWN: 6, TRK: 6}); c.check("Edwards 3 crore", 3, {OWN: 3, TRK: 3}); c.check("Khaleel 4.8 crore", 4.8, {OWN: 4.8, TRK: 4.8}); c.check("Ellis 2 crore", 2, {OWN: 2, TRK: 2})
c.check("CSK-SRH four-player trade", "Livingstone, Edwards to CSK; Khaleel, Ellis to SRH", {IPL: "Livingstone, Edwards to CSK; Khaleel, Ellis to SRH", CI: "Livingstone, Edwards to CSK; Khaleel, Ellis to SRH"})
c.check("Hardik to PBKS and Arshdeep to MI at 18 crore each", 18, {OWN: 18, TRK: 18}); c.check("Hardik was Mumbai's captain", "yes", {CI: "yes", YH: "yes"})
c.check("Harshal Patel to GT at 4 crore (half his 8 crore auction price)", 4, {OWN: 4, CI: 4})
c.check("17 Nov deal: Shami and Siddharth to RR, Curran to LSG", "traded", {IPL: "traded", OI: "traded"})
c.check("auction on 16 December in Goa", "16 Dec, Goa", {CI: "16 Dec, Goa", TRK: "16 Dec, Goa", YH: "16 Dec, Goa"})
c.check("six deals", 6, {IPL: 6, OI: 6}); c.check("fourteen players moved", 14, {IPL: 14, OI: 14})
for nm, key, val in (("Pant 2026 runs (LSG)", "Rishabh Pant", F["Rishabh Pant"]["runs"]), ("Kuldeep 2026 wickets (DC)", "Kuldeep Yadav", F["Kuldeep Yadav"]["wkts"]), ("Hardik 2026 runs (MI)", "Hardik Pandya", F["Hardik Pandya"]["runs"]),
                     ("Arshdeep 2026 wickets (PBKS)", "Arshdeep Singh", F["Arshdeep Singh"]["wkts"]), ("Natarajan 2026 wickets (DC)", "Thangarasu Natarajan", F["Thangarasu Natarajan"]["wkts"]), ("Shami 2026 wickets (LSG)", "Mohammed Shami", F["Mohammed Shami"]["wkts"])):
    c.check("archive: " + nm, val, {"sportmonks": val}, scope="archive")
assert c.summary().get("UNVERIFIED", 0) == 0 and c.summary().get("CONFLICT", 0) == 0, c.summary()
assert (F["Rishabh Pant"]["runs"], F["Kuldeep Yadav"]["wkts"], F["Hardik Pandya"]["runs"], F["Arshdeep Singh"]["wkts"], F["Thangarasu Natarajan"]["wkts"], F["Mohammed Shami"]["wkts"]) == (312, 10, 206, 14, 5, 12)

COL = {"MI": [0, 80, 190], "PBKS": [205, 35, 45], "DC": [30, 80, 190], "LSG": [0, 140, 185], "CSK": [215, 160, 0], "SRH": [235, 105, 20], "GT": [28, 45, 100], "RR": [220, 55, 145]}
NAME = {"MI": "MUMBAI INDIANS", "PBKS": "PUNJAB KINGS", "DC": "DELHI CAPITALS", "LSG": "LUCKNOW SUPER GIANTS", "CSK": "CHENNAI SUPER KINGS", "SRH": "SUNRISERS HYDERABAD", "GT": "GUJARAT TITANS", "RR": "RAJASTHAN ROYALS"}
T = lambda k: {"team": k, "name": NAME[k], "color": COL[k]}
P = lambda img, lines, stat=None, pair=False: {"img": L + img + ".png", "lines": lines, "stat": stat, "pair": pair}


def deal(label, a, b, p1, p2, vo, fee=None, one_way=None, sfx=True):
    sc = {"type": "tradesplit", "label": label, "a": T(a), "b": T(b), "p1": p1, "p2": p2}
    if fee: sc["fee"] = fee
    if one_way: sc["one_way_text"] = one_way
    return {"vo": vo, "scene": sc}


# the deals, in date order. a = the team whose half is on top / left; p1 goes a -> b, p2 goes b -> a
D1 = deal("DEAL 1 OF 6 · 23 JUN", "LSG", "DC", P("pant_dc", ["RISHABH", "PANT"], ["312 RUNS · SR 138"]), P("kuldeep_lsg", ["KULDEEP", "YADAV"], ["10 WICKETS · ECON 10.3"]),
         "June, and the first blockbuster. ऋषभ पंत goes back to दिल्ली at fifteen crore, down from the record twenty-seven that लखनऊ paid. कुलदीप यादव goes the other way, at thirteen and a half. Last season, पंत made three hundred and twelve runs, and कुलदीप took ten wickets.",
         fee="₹15 CR  ↔  ₹13.5 CR")
D2 = deal("DEAL 2 OF 6 · 14 OCT", "DC", "SRH", P("ansari_dc", ["ZEESHAN", "ANSARI"], None), P("natarajan_srh", ["T NATARAJAN"], ["5 WICKETS · 2026"]),
          "October. टी नटराजन returns to हैदराबाद for five crore, and ज़ीशान अंसारी moves to दिल्ली, for forty lakh. नटराजन took five wickets for दिल्ली last season.", fee="₹40 L  ↔  ₹5 CR")
D3 = deal("DEAL 3 OF 6 · 5 NOV", "SRH", "CSK", P("pair_livingstone_edwards", ["LIVINGSTONE", "& EDWARDS"], None, True), P("pair_khaleel_ellis", ["KHALEEL", "& ELLIS"], None, True),
          "November, and a four-player deal. Liam Livingstone and Jack Edwards go to चेन्नई, for six crore and three. ख़लील अहमद and Nathan Ellis go to हैदराबाद, for four point eight crore and two.", fee="₹9 CR  ↔  ₹6.8 CR")
D4 = deal("DEAL 4 OF 6 · 11 NOV", "MI", "PBKS", P("hardik_mi", ["HARDIK", "PANDYA"], ["206 RUNS · SR 138"]), P("arshdeep_pbks", ["ARSHDEEP", "SINGH"], ["14 WICKETS · ECON 10.3"]),
          "The big one. हार्दिक पंड्या goes from मुंबई to पंजाब, and अर्शदीप सिंह comes the other way, for eighteen crore each. मुंबई lose their captain. पंड्या made two hundred and six runs last season, and अर्शदीप took fourteen wickets.", fee="₹18 CR EACH")
D5 = deal("DEAL 5 OF 6 · 15 NOV", "SRH", "GT", P("harshal_gt_portrait", ["HARSHAL", "PATEL"], None), None,
          "Then, हर्षल पटेल moves from हैदराबाद to गुजरात for four crore, half of what he cost at the auction.", fee="₹4 CR", one_way="NOTHING BACK")
D6 = deal("DEAL 6 OF 6 · 17 NOV", "LSG", "RR", P("pair_shami_siddharth", ["MOHAMMED SHAMI", "& M SIDDHARTH"], ["SHAMI: 12 WICKETS · ECON 9.0"], True), P("curran_lsg", ["SAM", "CURRAN"], None),
          "And today. मोहम्मद शमी and एम सिद्धार्थ go to राजस्थान, while Sam Curran goes to लखनऊ. शमी took twelve wickets for लखनऊ last season.")
long = [
    {"vo": "The IPL twenty twenty-seven trade window has already moved fourteen players, in six deals. Here is every one of them.",
     "scene": {"type": "statement", "lines": [{"t": "6 DEALS."}, {"t": "14 PLAYERS.", "c": "gold"}], "sub": "IPL 2027 TRADE WINDOW · EVERY DEAL"}},
    D1, D2, D3, D4, D5, D6,
    {"vo": "Six deals, fourteen players, and more could still come before the auction on the sixteenth of December, in Goa.",
     "scene": {"type": "statement", "kicker": "WHAT NEXT", "lines": [{"t": "AUCTION"}, {"t": "16 DEC · GOA", "c": "gold"}], "sub": "THE TRADE WINDOW IS STILL OPEN"}},
    {"vo": "Which trade changes the most? Tell us in the comments, and subscribe for more.", "scene": {"type": "cta", "lines": [{"t": "WHICH TRADE"}, {"t": "CHANGES MOST?", "c": "gold"}]}},
]
short = [
    {"vo": "Six trades, fourteen players. The IPL window is wild.", "scene": {"type": "statement", "lines": [{"t": "6 DEALS."}, {"t": "14 PLAYERS.", "c": "gold"}], "sub": "IPL 2027 TRADE WINDOW"}},
    deal("DEAL 4 OF 6 · 11 NOV", "MI", "PBKS", D4["scene"]["p1"], D4["scene"]["p2"], "हार्दिक पंड्या goes to पंजाब. अर्शदीप सिंह goes to मुंबई. Eighteen crore each, and मुंबई lose their captain.", fee="₹18 CR EACH"),
    deal("DEAL 1 OF 6 · 23 JUN", "LSG", "DC", D1["scene"]["p1"], D1["scene"]["p2"], "ऋषभ पंत goes back to दिल्ली, at fifteen crore. कुलदीप यादव goes to लखनऊ, at thirteen and a half.", fee="₹15 CR  ↔  ₹13.5 CR"),
    deal("DEAL 3 OF 6 · 5 NOV", "SRH", "CSK", D3["scene"]["p1"], D3["scene"]["p2"], "Four players between चेन्नई and हैदराबाद: Livingstone, Edwards, ख़लील and Ellis.", fee="₹9 CR  ↔  ₹6.8 CR"),
    {"vo": YT_CTA["vo"], "scene": YT_CTA["scene"]},
]
SRC = ["The deals: the IPL's own press releases, https://www.iplt20.com/news (Pant and Kuldeep 23 Jun, https://www.iplt20.com/news/4379/rishabh-pant-and-kuldeep-yadav-complete-high-profile-trade-between-dc-and-lsg ; Natarajan and Ansari 14 Oct; CSK and SRH 5 Nov; Hardik and Arshdeep; Harshal Patel 15 Nov; Shami, Siddharth and Curran 17 Nov), read 17 Nov 2026; Cricinfo trade stories (CSK-SRH https://www.cricinfo.com/story/ipl-2027-csk-trade-khaleel-ahmed-and-nathan-ellis-to-srh-in-exchange-for-liam-livingstone-and-jack-edwards-1561531 ; Hardik-Arshdeep https://www.cricinfo.com/story/ipl-2027-mumbai-indians-and-punjab-kings-complete-hardik-pandya-and-arshdeep-singh-swap-1562157 ; Harshal https://www.cricinfo.com/story/sunrisers-hyderabad-set-to-trade-harshal-patel-to-gujarat-titans-1562498), read through search excerpts because the pages return 403 to us.",
       "Fees: the IPL's statement on Pant (INR 15 crore, down from INR 27 crore at the 2025 auction) and Kuldeep (INR 13.5 crore), also reported by Outlook https://www.outlookindia.com/sports/cricket/ipl-2027-player-trade-rishabh-pant-kuldeep-yadav-swap-between-delhi-capitals-and-lucknow-super-giants ; the other fees from the IPL and outlet graphics supplied by the channel owner and the iplretention.in tracker https://iplretention.in/ . The 17 Nov deal's fees are not stated (no second source yet).",
       "2026 numbers: Sportmonks ball-by-ball (our archive), IPL 2026, super overs excluded; wickets exclude run-outs. Figures: data/provenance/trades_2026_figures.json. Player photos: licensed images supplied by the channel owner."]
TAGS = ["IPL 2027 trades", "IPL trade window", "Hardik Pandya Arshdeep Singh trade", "Rishabh Pant Delhi Capitals", "Kuldeep Yadav LSG", "Mohammed Shami Rajasthan Royals", "IPL 2027", "IPL trades explained", "IPL news", "The Third Man"]
DL = ("IPL 2027 trades: every deal of the trade window so far. Six deals, fourteen players: Rishabh Pant back to Delhi Capitals (INR 15 crore) for Kuldeep Yadav to Lucknow Super Giants (INR 13.5 crore); T Natarajan to Sunrisers Hyderabad and Zeeshan Ansari to Delhi; "
      "Liam Livingstone and Jack Edwards to Chennai Super Kings for Khaleel Ahmed and Nathan Ellis to Sunrisers; Hardik Pandya to Punjab Kings for Arshdeep Singh to Mumbai Indians (INR 18 crore each); Harshal Patel to Gujarat Titans (INR 4 crore); and Mohammed Shami and M Siddharth to Rajasthan Royals for Sam Curran to Lucknow.\n\n"
      "The IPL 2027 auction is on 16 December in Goa. 2026 numbers are from our own archive (Sportmonks ball-by-ball). Fees as announced by the IPL where it published them; the 17 November deal's fees are not stated.\n\n#IPL2027 #IPLTrades #IPL")
DS = ("IPL 2027 trade window: six deals, fourteen players. Hardik Pandya to Punjab for Arshdeep Singh to Mumbai (INR 18 crore each), Pant back to Delhi, Kuldeep to Lucknow, and a four-player deal between Chennai and Hyderabad. Full breakdown on the channel.\n\n#IPL2027 #IPLTrades #Shorts")
spec = {"slug": "ipl_trades_2027", "theme": "stadium", "theme_long": "stadium", "captions": "v2", "captions_long": False, "series": "channel", "tag": "THE THIRD MAN", "tagsub": "IPL 2027 TRADES, EVERY DEAL",
        "files": {"long": "x", "short": "x"}, "thumb": {"kicker": "IPL 2027 TRADE WINDOW", "lines": [{"t": "EVERY TRADE"}, {"t": "SO FAR", "c": "gold"}], "hero": "6", "herosize": 520},
        "sources": SRC, "venue": {"time": "night", "crowd": [[25, 100, 200], [250, 150, 30], [230, 230, 240], [0, 120, 75]], "boards": [[25, 100, 200], [250, 150, 30]]}, "long": long, "short": short,
        "yt": {"long": {"title": "IPL 2027 Trades: Every Deal So Far | Hardik, Pant, Shami, Curran", "description": DL, "tags": TAGS},
               "short": {"title": "IPL 2027 Trades: Hardik for Arshdeep, Pant Back to Delhi #Shorts", "description": DS, "tags": TAGS}}}
c.save(spec); voice_lint.fix_spec(spec); spec["files"].setdefault("long", "_unused")
json.dump(spec, open("specs/ipl_trades_2027.json", "w"), ensure_ascii=False, indent=1)
print("wrote specs/ipl_trades_2027.json", voice_lint.check_spec(spec, ("long", "short")) or "voice lint clean", "|", sum(len(x["vo"]) for x in long), "+", sum(len(x["vo"]) for x in short), "chars")
