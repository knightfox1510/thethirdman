"""What exactly is missing from Cricsheet? Two independent yardsticks, both free:
 1. OFFICIAL MATCH NUMBERS. Cricsheet stores each match's official number (Test no., ODI no., T20I no.: info.match_type_number, the same number ESPNcricinfo prints on the match page).
    The numbers run 1..N with no holes, so every number we do not hold is a missing match. (each format is numbered separately for men and women)
 2. TEAM TOTALS BY OPPONENT (Wikipedia templates citing Cricinfo): reference matches minus held matches, per opponent, tells which opponents' series are incomplete.
    python3 -m dataops.gaps numbers             # missing official numbers per format (men's), with the date window of each hole, writes data/audit/gaps_numbers.json
    python3 -m dataops.gaps team India          # India: held vs reference per opponent per format, + held per year, writes data/audit/gaps_India.json
    python3 -m dataops.gaps fields              # what data points Cricsheet carries per format
The capture list for the Cricinfo extension = the missing numbers (skip a match page whose "<Format> no." is held)."""
import collections, glob, json, os, sys, time
from . import cricsheet as C, reference as R
ROOT = C.ROOT; AUD = os.path.join(ROOT, "data", "audit")
FILES = {"Test": "tests", "ODI": "odis", "T20I": "t20s"}
ALIAS = {"New": "New Zealand", "NZ": "New Zealand", "South": "South Africa", "SA": "South Africa", "Sri": "Sri Lanka", "West": "West Indies", "HKG": "Hong Kong", "UAE": "United Arab Emirates"}


def load():
    rows = []
    for fmt, d in FILES.items():
        for p in glob.glob(os.path.join(C.CS, d, "*.json")):
            m = json.load(open(p)); i = m["info"]
            rows.append({"fmt": fmt, "gender": i.get("gender"), "num": i.get("match_type_number"), "date": i["dates"][0], "teams": i["teams"], "event": i.get("event", {}).get("name", ""),
                         "venue": i.get("venue", ""), "id": os.path.basename(p)[:-5], "res": C.result(i)})
    return rows


def numbers(rows):
    out = {}
    for fmt in FILES:
        r = [x for x in rows if x["fmt"] == fmt and x["num"]]
        groups = {g: [x for x in r if x["gender"] == g] for g in ("male", "female")}
        for g, rr in groups.items():
            if not rr: continue
            by = {x["num"]: x for x in rr}
            top = sorted(by)
            while len(top) > 1 and top[-1] - top[-2] > 300: by.pop(top.pop())        # a lone mis-numbered row in Cricsheet (e.g. a Turkey v Estonia T20I numbered 4931): ignore
            lo, hi = min(by), max(by)
            if fmt != "T20I" or g == "both": pass
            miss = []; nums = sorted(by)
            for a, b in zip(nums, nums[1:]):
                if b - a > 1: miss.append({"numbers": [a + 1, b - 1], "count": b - a - 1, "after": by[a]["date"], "before": by[b]["date"]})
            out[f"{fmt}/{g}"] = {"first_held": lo, "last_held": hi, "first_date": by[lo]["date"], "last_date": by[hi]["date"], "held": len(by), "missing_before_first": lo - 1,
                                 "missing_inside": sum(x["count"] for x in miss), "holes": miss}
    return out


def team(name, rows):
    mine = [x for x in rows if name in x["teams"] and x["gender"] == "male"]
    full = None
    for attempt in range(5):
        try: full = R.team_by_opponent(name); break
        except Exception as e: time.sleep(25)
    out = {"team": name, "formats": {}}
    for fmt in FILES:
        held = collections.Counter(next(t for t in x["teams"] if t != name) for x in mine if x["fmt"] == fmt)
        ref = {ALIAS.get(k, k): v for k, v in (full or {}).get(fmt, {}).items()}
        opp = {}
        for o in sorted(set(held) | set(ref)):
            rm = (ref.get(o) or {}).get("matches"); opp[o] = {"held": held[o], "reference": rm, "missing": None if rm is None else rm - held[o]}
        yrs = collections.Counter(x["date"][:4] for x in mine if x["fmt"] == fmt)
        out["formats"][fmt] = {"held": sum(held.values()), "by_opponent": opp, "held_per_year": dict(sorted(yrs.items())),
                               "held_from": min((x["date"] for x in mine if x["fmt"] == fmt), default=None), "held_to": max((x["date"] for x in mine if x["fmt"] == fmt), default=None)}
    return out


def fields():
    for fmt, d in FILES.items():
        info = collections.Counter(); dl = collections.Counter(); wk = collections.Counter(); ex = collections.Counter(); n = 0
        for p in glob.glob(os.path.join(C.CS, d, "*.json")):
            m = json.load(open(p))
            if m["info"].get("gender") != "male": continue
            n += 1; info.update(m["info"])
            for inn in m["innings"]:
                for o in inn["overs"]:
                    for b in o["deliveries"]:
                        dl.update(b); ex.update(b.get("extras", {}))
                        for w in b.get("wickets", []): wk.update(w)
        print(f"== {fmt}: {n} men's matches\n  match: {dict(info)}\n  per ball: {dict(dl)}\n  wicket: {dict(wk)}\n  extras: {dict(ex)}")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "fields": fields(); sys.exit()
    rows = load(); os.makedirs(AUD, exist_ok=True)
    if cmd == "numbers":
        o = numbers(rows); json.dump(o, open(os.path.join(AUD, "gaps_numbers.json"), "w"), indent=1)
        for k, v in o.items(): print(f"{k:14} held {v['held']:5}  numbers {v['first_held']}..{v['last_held']} ({v['first_date']}..{v['last_date']})  missing before: {v['missing_before_first']:5}  missing inside: {v['missing_inside']:4}")
    else:
        o = team(sys.argv[2], rows); json.dump(o, open(os.path.join(AUD, f"gaps_{sys.argv[2]}.json"), "w"), indent=1)
        for fmt, v in o["formats"].items():
            print(f"\n== {sys.argv[2]} {fmt}: held {v['held']}  ({v['held_from']} .. {v['held_to']})")
            for opp, x in v["by_opponent"].items():
                if x["missing"]: print(f"   {opp:24} held {x['held']:4}  reference {x['reference']}  MISSING {x['missing']}")
