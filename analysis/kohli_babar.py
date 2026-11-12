"""Stat Check: Kohli or Babar? Every T20I ball (Cricsheet men's T20Is, ODC-BY).
    python3 analysis/kohli_babar.py
Innings = every T20I in which they batted. Balls faced exclude wides. Dismissals use Cricsheet's player_out (includes non-striker run-outs).
Same-point comparison: first N innings of each, where N = the smaller career."""
import glob, json, os, collections
CS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "cricsheet", "t20i")
P = {"V Kohli": "Kohli", "Babar Azam": "Babar"}
FULL = {"Australia", "England", "India", "New Zealand", "Pakistan", "South Africa", "Sri Lanka", "West Indies", "Afghanistan", "Bangladesh",
        "Ireland", "Zimbabwe"}
TOP = {"Australia", "England", "India", "New Zealand", "Pakistan", "South Africa"}


def innings():
    out = collections.defaultdict(list)
    for f in glob.glob(f"{CS}/*.json"):
        d = json.load(open(f)); i = d["info"]
        for n, inn in enumerate(d.get("innings", [])):
            if inn.get("super_over"): continue
            team = inn["team"]; opp = [t for t in i["teams"] if t != team][0]
            r, b, fo, si, pp, ppb, de, deb, order, outp = tuple(collections.Counter() for _ in range(9)) + (set(),)
            seen = []
            for ov in inn.get("overs", []):
                for dl in ov["deliveries"]:
                    for p in (dl["batter"], dl["non_striker"]):
                        if p not in seen: seen.append(p)
                    bt = dl["batter"]; br = dl["runs"]["batter"]; wide = "wides" in dl.get("extras", {})
                    r[bt] += br
                    if not wide:
                        b[bt] += 1
                        if ov["over"] < 6: ppb[bt] += 1; pp[bt] += br
                        if ov["over"] >= 15: deb[bt] += 1; de[bt] += br
                    if br == 4 and not dl["runs"].get("non_boundary"): fo[bt] += 1
                    if br == 6: si[bt] += 1
                    for w in dl.get("wickets", []): outp.add(w["player_out"])
            for p in seen:
                if p in P:
                    res = i.get("outcome", {}).get("winner")
                    out[P[p]].append(dict(date=i["dates"][0], opp=opp, runs=r[p], balls=b[p], out=p in outp, fours=fo[p], sixes=si[p],
                                          pp=pp[p], ppb=ppb[p], de=de[p], deb=deb[p], chase=n == 1, won=res == team, pos=seen.index(p) + 1,
                                          event=i.get("event", {}).get("name", ""), stage=i.get("event", {}).get("stage", "")))
    for k in out: out[k].sort(key=lambda x: x["date"])
    return out


def summ(xs):
    R = sum(x["runs"] for x in xs); B = sum(x["balls"] for x in xs); O = sum(x["out"] for x in xs)
    return dict(inns=len(xs), runs=R, balls=B, outs=O, avg=R / max(1, O), sr=100 * R / max(1, B), fifties=sum(50 <= x["runs"] < 100 for x in xs),
                hundreds=sum(x["runs"] >= 100 for x in xs), f50=sum(x["runs"] >= 50 for x in xs), ducks=sum(x["runs"] == 0 and x["out"] for x in xs),
                fours=sum(x["fours"] for x in xs), sixes=sum(x["sixes"] for x in xs),
                bpb=B / max(1, sum(x["fours"] + x["sixes"] for x in xs)),
                ppsr=100 * sum(x["pp"] for x in xs) / max(1, sum(x["ppb"] for x in xs)), desr=100 * sum(x["de"] for x in xs) / max(1, sum(x["deb"] for x in xs)),
                deb=sum(x["deb"] for x in xs), ppb=sum(x["ppb"] for x in xs))


if __name__ == "__main__":
    I = innings()
    for k, xs in I.items(): print(k, "first", xs[0]["date"], "last", xs[-1]["date"], {a: round(b, 2) for a, b in summ(xs).items()})
    n = min(len(I["Kohli"]), len(I["Babar"])); print("\n== same point: first", n, "innings")
    for k in I: print(k, {a: round(b, 2) for a, b in summ(I[k][:n]).items()})
    for lab, f in [("chasing", lambda x: x["chase"]), ("chasing, won", lambda x: x["chase"] and x["won"]), ("setting", lambda x: not x["chase"]),
                   ("v top 6 teams", lambda x: x["opp"] in TOP), ("v others", lambda x: x["opp"] not in TOP),
                   ("ICC events", lambda x: any(e in x["event"] for e in ("World T20", "T20 World Cup", "World Twenty20"))),
                   ("ICC knockouts", lambda x: any(e in x["event"] for e in ("World T20", "T20 World Cup", "World Twenty20")) and x["stage"] in ("Final", "Semi Final")),
                   ("India v Pakistan", lambda x: x["opp"] in ("Pakistan", "India"))]:
        print(f"\n== {lab}")
        for k in I: print(" ", k, {a: round(b, 2) for a, b in summ([x for x in I[k] if f(x)]).items() if a in ("inns", "runs", "avg", "sr", "f50")})
    print("\nKohli v Pakistan innings:", [(x["date"], x["runs"], x["balls"], x["out"]) for x in I["Kohli"] if x["opp"] == "Pakistan"])
    print("Babar v India innings:", [(x["date"], x["runs"], x["balls"], x["out"]) for x in I["Babar"] if x["opp"] == "India"])
