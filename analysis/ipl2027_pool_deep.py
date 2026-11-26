"""IPL 2027 auction: the named pool (top base-price brackets as reported 25 Nov 2026) and the uncapped-Indian dark-horse screen, from OUR Sportmonks IPL ball-by-ball (2013-2026).
Named brackets: data/provenance/ipl2027_register_named.json (hand-entered from press reports of the BCCI register, 25 Nov 2026; the full 1,220 list and base prices are due 4 Dec).
'Likely uncapped' = no India appearance in Cricsheet men's internationals under the same surname + first initial (Cricsheet is partial: verify against the official capped flag).
Writes data/provenance/ipl2027_pool_deep.json.   python3 analysis/ipl2027_pool_deep.py"""
import json, os, sys, glob, re, collections, unicodedata
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, R); sys.path.insert(0, f"{R}/analysis")
import numpy as np, pandas as pd, common
df = common.ipl(); df = df[df.comp.notna()] if "comp" in df else df
def norm(s):
    s = "" if s is None else str(s); return re.sub(r"[^a-z ]", "", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()).strip()
NAMED = json.load(open(f"{R}/data/provenance/ipl2027_register_named.json"))["brackets"]
names = sorted(set(map(str, df.batter.dropna())) | set(map(str, df.bowler.dropna()))); byn = {norm(n): n for n in names}
def find(n):
    k = norm(n)
    if k in byn: return byn[k]
    t = k.split(); last = t[-1]; first = t[0]
    c = [v for kk, v in byn.items() if kk.split()[-1] == last and kk.split()[0][:1] == first[:1]]
    if len(c) == 1: return c[0]
    c = [v for kk, v in byn.items() if kk.endswith(" " + last) and (first in kk or kk.split()[0] in first)]
    return c[0] if len(c) == 1 else None
SEAS = [2024, 2025, 2026]; rec = df[df.season.isin(SEAS)]
def bat(d):
    leg = d[d.legal == 1] if "legal" in d else d; b = len(leg); r = int(leg.bat_runs.sum()); dis = int(((d.out_id == d.batter_id) | (d.out_id.isna() & (d.striker_out == 1)) & (d.wicket == 1)).sum()) if len(d) else 0
    return dict(inn=int(d.fixture.nunique()), balls=int(b), runs=r, sr=round(100 * r / b, 1) if b else None, outs=dis, avg=round(r / dis, 1) if dis else None, bnd=round(100 * (leg.four.sum() * 4 + leg.six.sum() * 6) / r, 0) if r else None, sixes=int(leg.six.sum()))
def bowl(d):
    lb = int(d.legal_bowl.sum()); r = int(d.runs.sum()); w = int(((d.wicket == 1) & (~d.dismissal.fillna("").isin(["run out", "retired hurt", "retired out", "obstructing the field"]))).sum())
    return dict(balls=lb, econ=round(6 * r / lb, 2) if lb else None, wkts=w)
def phase(d, p, kind): 
    x = d[d.phase == p]; return bat(x) if kind == "bat" else bowl(x)
def profile(n):
    b = df[df.batter == n]; w = df[df.bowler == n]; b3 = rec[rec.batter == n]; w3 = rec[rec.bowler == n]
    seasons = sorted(set(b.season) | set(w.season))
    out = dict(name=n, seasons=f"{seasons[0]}-{seasons[-1]}" if seasons else "", n_seasons=len(seasons), bat_hand=(b.bat_hand.mode().iloc[0] if len(b) else None), bowl_kind=(w.bowl_kind.mode().iloc[0] if len(w) else None),
               career_bat=bat(b), career_bowl=bowl(w), r3_bat=bat(b3), r3_bowl=bowl(w3), r3_bat_pp=phase(b3, "powerplay", "bat"), r3_bat_mid=phase(b3, "middle", "bat"), r3_bat_death=phase(b3, "death", "bat"), r3_bowl_pp=phase(w3, "powerplay", "bowl"), r3_bowl_death=phase(w3, "death", "bowl"))
    return out
out = {"named": {}, "unmatched": [], "dark_horses": {}}
for br, lst in NAMED.items():
    for n in lst:
        f = find(n["n"] if isinstance(n, dict) else n)
        if not f: out["unmatched"].append((br, n)); continue
        p = profile(f); p["bracket"] = br; p["listed_as"] = n["n"] if isinstance(n, dict) else n; p["country"] = n.get("c") if isinstance(n, dict) else None; out["named"][f] = p
# who is in a retained squad (not available)
sq = json.load(open(f"{R}/data/ipl2027/squads.json"))["teams"]; nm = json.load(open(f"{R}/data/ipl2027/name_map.json")); retained = {norm(nm.get(x, x)) for t in sq.values() for x in t["squad"]}
# India caps from Cricsheet men's internationals
caps = set()
for f in glob.glob(f"{R}/data/cricsheet/*/*.json"):
    if "/ipl" in f or "ipl_json" in f: continue
    try: d = json.load(open(f))
    except Exception: continue
    i = d.get("info", {})
    if i.get("gender") != "male" or "India" not in i.get("teams", []) or "India" not in (i.get("players") or {}): continue
    ev = (i.get("event") or {}).get("name", "") + i.get("team_type", "")
    if i.get("team_type") != "international": continue
    for pn in i["players"]["India"]:
        t = norm(pn).split(); 
        if t: caps.add((t[-1], t[0][:1]))
pl = {}
for f in glob.glob(f"{R}/data/players/*.json"):
    d = json.load(open(f)); pl[d["fullname"]] = d
kohli = pl.get("Virat Kohli", {}).get("country_id"); IND = {c for n, c in ((x, pl[x].get("country_id")) for x in ("Virat Kohli", "Rohit Sharma", "Jasprit Bumrah", "Shubman Gill", "Ravindra Jadeja") if x in pl)}; IND = collections.Counter(c for c in IND).most_common(1)[0][0] if IND else kohli
def is_indian(n): return pl.get(n, {}).get("country_id") == IND
def capped(n): t = norm(n).split(); return (t[-1], t[0][:1]) in caps
cand = []
for n in sorted(set(rec.batter.dropna()) | set(rec.bowler.dropna())):
    if not is_indian(n) or norm(n) in retained or capped(n): continue
    p = profile(n); p["listed_as"] = n; p["retained"] = False; cand.append(p)
out["dark_horses"] = {p["name"]: p for p in cand}; out["india_country_id"] = IND; out["n_candidates"] = len(cand); out["caps_keys"] = len(caps)
json.dump(out, open(f"{R}/data/provenance/ipl2027_pool_deep.json", "w"), ensure_ascii=False, indent=1, default=str)
print("named matched", len(out["named"]), "unmatched", out["unmatched"], "| IND country id", IND, "| uncapped-unretained Indian IPL players 2024-26:", len(cand), "| cap keys", len(caps))
