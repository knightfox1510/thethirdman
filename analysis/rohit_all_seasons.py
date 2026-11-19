"""Rohit Sharma across EVERY IPL season 2008-2026 (Cricsheet IPL archive; Deccan Chargers 2008-10, Mumbai Indians 2011-26), plus checks of the achievements in MI's tribute copy against the archive.
Needs IPL_DIR (the Cricsheet ipl_json files). Writes data/provenance/rohit_all_seasons.json. Everything is 'in our archive'."""
import glob, json, os, collections
IPL_DIR = os.environ.get("IPL_DIR", "/tmp/claude-0/-home-user-thethirdman/0e6d8023-8d7b-5fe3-9abc-6751d93064e2/scratchpad/csipl/x")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "provenance", "rohit_all_seasons.json")
yr = lambda s: {"2007/08": 2008, "2009": 2009, "2009/10": 2010, "2020/21": 2020}.get(str(s), int(str(s)[:4]))
R = "RG Sharma"
by = collections.defaultdict(lambda: {"runs": 0, "balls": 0, "fours": 0, "sixes": 0, "pp_runs": 0, "pp_balls": 0, "inn": 0, "scores": [], "team": set()})
lg = collections.defaultdict(lambda: {"pp_runs": 0, "pp_balls": 0, "runs": 0, "balls": 0})
bat_runs = collections.defaultdict(lambda: collections.defaultdict(int)); bat_sixes = collections.defaultdict(lambda: collections.defaultdict(int)); titles = collections.Counter(); finals = {}
for f in glob.glob(IPL_DIR + "/*.json"):
    d = json.load(open(f)); i = d["info"]
    if i.get("match_type") != "T20" or "Indian Premier League" not in (i.get("event") or {}).get("name", ""): continue
    y = yr(i["season"]); st = (i.get("event") or {}).get("stage"); w = (i.get("outcome") or {}).get("winner")
    if st == "Final" and w:
        finals[y] = {"winner": w, "xi": i["players"][w]}
        for p in i["players"][w]: titles[p] += 1
    for inn in d["innings"]:
        if inn.get("super_over"): continue
        score = 0; had = False
        for ov in inn["overs"]:
            for dl in ov["deliveries"]:
                rb = dl["runs"]["batter"]; ex = dl.get("extras", {}); legal = "wides" not in ex; pp = ov["over"] < 6; b = dl["batter"]
                bat_runs[b][y] += rb; bat_sixes[b][y] += (rb == 6)
                L = lg[y]; L["runs"] += rb
                if legal: L["balls"] += 1
                if pp: L["pp_runs"] += rb; L["pp_balls"] += legal
                if b == R:
                    had = True; c = by[y]; c["runs"] += rb; c["balls"] += legal; c["fours"] += (rb == 4); c["sixes"] += (rb == 6); score += rb; c["team"].add(inn["team"])
                    if pp: c["pp_runs"] += rb; c["pp_balls"] += legal
        if had: by[y]["inn"] += 1; by[y]["scores"].append(score)
S = {}
for y in sorted(by):
    c = by[y]; L = lg[y]; sc = c["scores"]
    S[y] = {"team": sorted(c["team"])[0], "inn": c["inn"], "runs": c["runs"], "balls": c["balls"], "sr": round(100 * c["runs"] / c["balls"], 1), "sixes": c["sixes"], "fifties": sum(50 <= s < 100 for s in sc), "hundreds": sum(s >= 100 for s in sc),
            "pp_sr": round(100 * c["pp_runs"] / max(1, c["pp_balls"]), 1), "league_pp_sr": round(100 * L["pp_runs"] / L["pp_balls"], 1), "league_sr": round(100 * L["runs"] / L["balls"], 1)}
F = {"seasons": S}
F["career_2008_2026"] = {k: sum(S[y][k] for y in S) for k in ("inn", "runs", "balls", "sixes", "fifties", "hundreds")}
# the achievements in MI's copy
runs_to = lambda b, y: sum(v for k, v in bat_runs[b].items() if k <= y); six_to = lambda b, y: sum(v for k, v in bat_sixes[b].items() if k <= y)
F["titles_by_player"] = {p: n for p, n in titles.most_common(8)}; F["rohit_titles"] = {y: v["winner"] for y, v in finals.items() if R in v["xi"]}
F["runs_through_2025_top"] = [(b, runs_to(b, 2025)) for b in sorted(bat_runs, key=lambda b: -runs_to(b, 2025))[:6]]
F["sixes_through_2025_top"] = [(b, six_to(b, 2025)) for b in sorted(bat_sixes, key=lambda b: -six_to(b, 2025))[:8]]
F["rohit_runs_through_2024"] = runs_to(R, 2024); F["rohit_runs_through_2025"] = runs_to(R, 2025); F["rohit_sixes_through_2024"] = six_to(R, 2024); F["rohit_sixes_through_2025"] = six_to(R, 2025)
print("season  team                     inn runs   SR  6s 50 100 | PP SR (league) | league SR")
for y, v in S.items(): print(f'{y} {v["team"][:22]:22} {v["inn"]:>3} {v["runs"]:>4} {v["sr"]:>6} {v["sixes"]:>3} {v["fifties"]:>2} {v["hundreds"]:>2} | {v["pp_sr"]:>6} ({v["league_pp_sr"]:>6}) | {v["league_sr"]}')
print("career 2008-2026:", F["career_2008_2026"])
print("titles (XI of the winning side in each final):", F["titles_by_player"]); print("Rohit's titles:", F["rohit_titles"])
print("runs through 2025:", F["runs_through_2025_top"]); print("sixes through 2025:", F["sixes_through_2025_top"])
print("Rohit runs through 2024 / 2025:", F["rohit_runs_through_2024"], F["rohit_runs_through_2025"], "| sixes:", F["rohit_sixes_through_2024"], F["rohit_sixes_through_2025"])
json.dump(F, open(OUT, "w"), indent=1, default=str); print("saved", OUT)
