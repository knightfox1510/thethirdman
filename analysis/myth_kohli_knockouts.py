"""Figures for Myth or Data? Ep. 1, "Does Kohli fail in knockouts?" (Cricsheet ODIs and T20Is).
ICC knockouts = semi-finals, quarter-finals and finals of the ODI World Cup, Champions Trophy and T20 World Cup."""
import glob, json, os, collections

CS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "cricsheet")
ICC = ("World Cup", "Champions Trophy", "World T20", "T20 World Cup", "World Twenty20")
KO = ("Final", "Semi Final", "Quarter Final")


def innings(kind, who=None):
    """Yield (date, event, stage, batter, runs, balls, out) for every batting innings."""
    for f in glob.glob(f"{CS}/{kind}/*.json"):
        d = json.load(open(f)); i = d["info"]; ev = i.get("event", {})
        for inn in d.get("innings", []):
            r, b, out, seen = collections.Counter(), collections.Counter(), set(), []
            for ov in inn.get("overs", []):
                for dl in ov["deliveries"]:
                    for p in (dl["batter"], dl["non_striker"]):
                        if p not in seen: seen.append(p)
                    r[dl["batter"]] += dl["runs"]["batter"]
                    if "wides" not in dl.get("extras", {}): b[dl["batter"]] += 1
                    for w in dl.get("wickets", []): out.add(w["player_out"])
            for p in seen:
                if who and p != who: continue
                yield i["dates"][0], ev.get("name", ""), ev.get("stage", ""), p, r[p], b[p], p in out


def is_icc_ko(name, stage): return any(k in name for k in ICC) and stage in KO and "Asian" not in name


def summary(rows):
    runs = sum(x[4] for x in rows); outs = sum(x[6] for x in rows); balls = sum(x[5] for x in rows)
    return dict(inns=len(rows), runs=runs, outs=outs, avg=runs / outs if outs else float("nan"), sr=100 * runs / max(1, balls))


if __name__ == "__main__":
    for kind in ("odi", "t20i"):
        allk = list(innings(kind, "V Kohli"))
        ko = sorted(x for x in allk if is_icc_ko(x[1], x[2]))
        rest = [x for x in allk if not is_icc_ko(x[1], x[2])]
        print(f"== Kohli {kind.upper()}: career {summary(allk)}")
        print(f"   ICC knockouts {summary(ko)} | all other games {summary(rest)}")
        fin = [x for x in ko if x[2] == "Final"]; semi = [x for x in ko if x[2] != "Final"]
        print(f"   finals {summary(fin)} | semis/quarters {summary(semi)}")
        for x in ko: print(f"     {x[0]} {x[1]} {x[2]}: {x[4]}{'' if x[6] else '*'} ({x[5]})")
    print("== Best averages in T20 World Cup knockouts (min 4 innings)")
    by = collections.defaultdict(list)
    for x in innings("t20i"):
        if is_icc_ko(x[1], x[2]): by[x[3]].append(x)
    tab = sorted(((summary(v)["avg"], p, summary(v)) for p, v in by.items() if len(v) >= 4 and summary(v)["outs"]), reverse=True)
    for a, p, s in tab[:8]: print(f"   {p}: {s}")
    print("== Most runs in ODI World Cup + Champions Trophy knockouts")
    by = collections.defaultdict(list)
    for x in innings("odi"):
        if is_icc_ko(x[1], x[2]): by[x[3]].append(x)
    tab = sorted(((summary(v)["runs"], p, summary(v)) for p, v in by.items()), reverse=True)
    for r, p, s in tab[:8]: print(f"   {p}: {s}")
