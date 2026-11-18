"""IPL 2027 retention needs: what each franchise's squad (retained + traded in, data/ipl2027/squads.json) lacks, from OUR ball-by-ball data (Sportmonks, IPL 2025 and 2026, super overs excluded).
Capacity index = (balls the squad's players bowled or faced in a role in 2025-26) / (league total / 10): 1.00 is an average squad, below 1 is thin. Quality = economy (bowling) or strike rate (batting) of those balls vs the league.
Roles: batting = powerplay (overs 1-6), middle (7-15), death (16-20); bowling = pace in powerplay, spin in middle, pace at the death. Players with no IPL data in our archive count as zero (new or uncapped).
Keepers and overseas counts use our own classification list below. Writes data/provenance/ipl2027_needs.json.   python3 analysis/ipl2027_needs.py"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from common import ipl
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQ = json.load(open(f"{R}/data/ipl2027/squads.json"))["teams"]; MAP = json.load(open(f"{R}/data/ipl2027/name_map.json")); MAP.update({"KL Rahul": "Lokesh Rahul", "Smaran Ravichandran": "Ravichandran Smaran"})
df = ipl(); d = df[df.season >= 2025].copy(); d["pace"] = ~d.bowl_kind.astype(str).str.contains("spin", case=False, na=False)
KEEPERS = {"Sanju Samson", "Urvil Patel", "Quinton de Kock", "Ryan Rickelton", "Phil Salt", "Jitesh Sharma", "Jordan Cox", "Tim Seifert", "Heinrich Klaasen", "Ishan Kishan", "Salil Arora", "Dhruv Jurel", "Lhuan-dre Pretorius", "KL Rahul", "Rishabh Pant",
           "Prabhsimran Singh", "Vishnu Vinod", "Jos Buttler", "Tom Banton", "Kumar Kushagra", "Anuj Rawat", "Nicholas Pooran", "Josh Inglis", "Madhav Tiwari"}
lg = {}
bat = d[d.legal == 1]; bowl = d[d.legal_bowl == 1]
for ph in ("powerplay", "middle", "death"):
    b = bat[bat.phase == ph]; lg[f"bat_{ph}"] = (len(b) / 10, 100 * b.bat_runs.sum() / len(b))
pp = bowl[(bowl.phase == "powerplay") & bowl.pace]; mid = bowl[(bowl.phase == "middle") & ~bowl.pace]; dth = bowl[(bowl.phase == "death") & bowl.pace]
for k, x in (("pace_pp", pp), ("spin_mid", mid), ("pace_death", dth)): lg[k] = (len(x) / 10, 6 * x.runs.sum() / len(x))


def team_row(players):
    real = {MAP.get(p) for p in players if MAP.get(p)}; r = {"players_with_data": len(real), "of": len(players)}
    for ph in ("powerplay", "middle", "death"):
        b = bat[(bat.phase == ph) & bat.batter.isin(real)]; r[f"bat_{ph}"] = (round(len(b) / lg[f"bat_{ph}"][0], 2), round(100 * b.bat_runs.sum() / max(1, len(b)), 1))
    for k, x in (("pace_pp", pp), ("spin_mid", mid), ("pace_death", dth)):
        b = x[x.bowler.isin(real)]; r[k] = (round(len(b) / lg[k][0], 2), round(6 * b.runs.sum() / max(1, len(b)), 2), int((b.groupby("bowler").size() >= 60).sum()))     # index, economy, bowlers with 10+ overs in the role
    return r


OUT = {"league": {k: [round(v[0]), round(v[1], 2)] for k, v in lg.items()}, "teams": {}}
for t, v in SQ.items():
    r = team_row(v["squad"]); r["keepers"] = sum(p in KEEPERS for p in v["squad"]); r["purse_cr"] = v["purse_cr"]; r["slots"] = v["slots"]; r["overseas_slots"] = v["overseas_slots"]; r["cr_per_slot"] = round(v["purse_cr"] / v["slots"], 1); OUT["teams"][t] = r
print("LEAGUE per-team average (balls, then SR or economy):", OUT["league"])
print(f'\n{"team":5}{"data":>6}{"PPbat":>7}{"MIDbat":>8}{"DTHbat":>8} |{"PPpace":>8}{"SPIN":>7}{"DTHpace":>9} |{"keepers":>8}{"purse":>7}{"slots":>6}{"ovs":>5}{"cr/slot":>8}')
for t, r in OUT["teams"].items():
    print(f'{t:5}{r["players_with_data"]:>3}/{r["of"]:<2}{r["bat_powerplay"][0]:>7}{r["bat_middle"][0]:>8}{r["bat_death"][0]:>8} |{r["pace_pp"][0]:>8}{r["spin_mid"][0]:>7}{r["pace_death"][0]:>9} |{r["keepers"]:>8}{r["purse_cr"]:>7}{r["slots"]:>6}{r["overseas_slots"]:>5}{r["cr_per_slot"]:>8}')
print("\nQUALITY (batting SR in PP / middle / death; economy PP pace / middle spin / death pace) vs league", {k: v[1] for k, v in lg.items()})
for t, r in OUT["teams"].items(): print(f'{t:5} SR {r["bat_powerplay"][1]:>6} {r["bat_middle"][1]:>6} {r["bat_death"][1]:>6} | econ {r["pace_pp"][1]:>5} {r["spin_mid"][1]:>5} {r["pace_death"][1]:>5} | bowlers with 10+ overs: PPpace {r["pace_pp"][2]} spin {r["spin_mid"][2]} DTHpace {r["pace_death"][2]}')
# the auction pool: released players ranked by role (2025-26)
pool = {}
for t, v in SQ.items():
    for p in v["released"]: pool[p] = (t, MAP.get(p))
names = {n: (p, t) for p, (t, n) in pool.items() if n}; rows = []
for n, (p, t) in names.items():
    b = bat[bat.batter == n]; w = bowl[bowl.bowler == n]; ppb = b[b.phase == "powerplay"]; db = b[b.phase == "death"]
    rows.append({"player": p, "from": t, "pp_balls": len(ppb), "pp_sr": round(100 * ppb.bat_runs.sum() / max(1, len(ppb)), 1), "death_balls": len(db), "death_sr": round(100 * db.bat_runs.sum() / max(1, len(db)), 1), "mid_spin_balls": int(((w.phase == "middle") & ~w.pace).sum()), "mid_spin_econ": round(6 * w[(w.phase == "middle") & ~w.pace].runs.sum() / max(1, ((w.phase == "middle") & ~w.pace).sum()), 2),
                 "pp_pace_balls": int(((w.phase == "powerplay") & w.pace).sum()), "pp_pace_econ": round(6 * w[(w.phase == "powerplay") & w.pace].runs.sum() / max(1, ((w.phase == "powerplay") & w.pace).sum()), 2), "death_pace_balls": int(((w.phase == "death") & w.pace).sum()), "death_pace_econ": round(6 * w[(w.phase == "death") & w.pace].runs.sum() / max(1, ((w.phase == "death") & w.pace).sum()), 2)})
P = pd.DataFrame(rows); OUT["pool_released"] = rows
print("\nRELEASED POOL (2025-26): openers by PP balls >= 120"); print(P[P.pp_balls >= 120].sort_values("pp_sr", ascending=False)[["player", "from", "pp_balls", "pp_sr"]].to_string(index=False))
print("\nfinishers: death balls >= 50"); print(P[P.death_balls >= 50].sort_values("death_sr", ascending=False)[["player", "from", "death_balls", "death_sr"]].to_string(index=False))
print("\nspinners: middle-overs balls >= 120"); print(P[P.mid_spin_balls >= 120].sort_values("mid_spin_econ")[["player", "from", "mid_spin_balls", "mid_spin_econ"]].to_string(index=False))
print("\npace new ball: PP balls >= 60"); print(P[P.pp_pace_balls >= 60].sort_values("pp_pace_econ")[["player", "from", "pp_pace_balls", "pp_pace_econ"]].to_string(index=False))
print("\npace death: balls >= 60"); print(P[P.death_pace_balls >= 60].sort_values("death_pace_econ")[["player", "from", "death_pace_balls", "death_pace_econ"]].to_string(index=False))
json.dump(OUT, open(f"{R}/data/provenance/ipl2027_needs.json", "w"), indent=1, default=str); print("\nsaved data/provenance/ipl2027_needs.json")
