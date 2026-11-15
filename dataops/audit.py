"""Coverage audit: what do we HOLD (Cricsheet) vs what EXISTS (reference totals from other sources)?
    python3 -m dataops.audit team India [--since 2024-07-27]
    python3 -m dataops.audit player "V Kohli" "Virat Kohli"       # Cricsheet name, Wikipedia title
Prints a table per format and a verdict: COMPLETE (we hold every match), GAPS (missing matches: do not claim totals/records), or UNVERIFIED (no reference).
Writes data/audit/<subject>.json, which dataops/verify.py reads: a claim about an incomplete subject must be labelled 'in our archive'."""
import collections, json, os, sys
from . import cricsheet as C, reference as R

ROOT = C.ROOT


def team(name, since=None):
    rows = C.team_rows(name)
    ref = R.team_totals(name)
    out = {"subject": name, "kind": "team", "formats": {}}
    for fmt in ("Test", "ODI", "T20I"):
        r = [x for x in rows if x["fmt"] == fmt]
        c = collections.Counter(x["res"] for x in r)
        held = {"matches": len(r), "won": c["W"], "lost": c["L"], "tied": c["T"] if fmt != "T20I" else sum(1 for x in r if x["res"] == "T" and not x["so_winner"]),
                "no_result": c["NR"], "drawn": c["D"]}
        if fmt == "T20I":
            held["tie_win"] = sum(1 for x in r if x["res"] == "T" and x["so_winner"] == name); held["tie_loss"] = sum(1 for x in r if x["res"] == "T" and x["so_winner"] and x["so_winner"] != name)
        refv = (ref[fmt]["total"] or {})
        gap = {k: refv[k] - held.get(k, 0) for k in refv}
        status = "UNVERIFIED" if not refv else "COMPLETE" if all(v == 0 for v in gap.values()) else "GAPS"
        out["formats"][fmt] = {"held": held, "reference": refv, "gap": gap, "status": status, "as_of": ref[fmt]["as_of"], "source": ref[fmt]["source"],
                               "held_from": min((x["date"] for x in r), default=None), "held_to": max((x["date"] for x in r), default=None)}
    if since:                                                              # window listing by event, for a manual or second-source check
        for fmt in ("Test", "ODI", "T20I"):
            w = [x for x in rows if x["fmt"] == fmt and x["date"] >= since]; ev = collections.OrderedDict()
            for x in w: ev.setdefault(x["event"], []).append(x)
            out["formats"][fmt]["window"] = {"since": since, "matches": len(w), "by_event": {e: "".join(y["res"][0] if y["res"] in ("W", "L", "D") else y["res"][0].lower() for y in v) for e, v in ev.items()}}
    return out


def by_opponent(name, fmt):
    """Where are the gaps? Our holdings vs the reference per opponent for one format (lists only the opponents that differ)."""
    ref = R.team_by_opponent(name)[fmt]; rows = [x for x in C.team_rows(name) if x["fmt"] == fmt]; out = {}
    for opp in sorted(set(ref) | {x["opp"] for x in rows}):
        r = [x for x in rows if x["opp"] == opp]; got = {"matches": len(r), "won": sum(x["res"] == "W" for x in r), "lost": sum(x["res"] == "L" for x in r)}
        exp = ref.get(opp, {}); d = {k: exp.get(k, 0) - got[k] for k in got}
        if any(d.values()): out[opp] = {"held": got, "reference": {k: exp.get(k, 0) for k in got}, "years_held": [min(x["date"] for x in r)[:4], max(x["date"] for x in r)[:4]] if r else None}
    return out


def show(o):
    print(f"== {o['subject']}  ({o['kind']})")
    for fmt, f in o["formats"].items():
        print(f"  {fmt:5s} {f['status']:10s} held {f['held']['matches']:4d} of {f['reference'].get('matches','?'):>4}  | gap {f['gap']}  | reference as of: {f['as_of'][:70]}")
        print(f"        held from {f['held_from']} to {f['held_to']}")
        if "window" in f: print(f"        window since {f['window']['since']}: {f['window']['matches']} matches; by event {f['window']['by_event']}")


def player(cs_name, wiki_title):
    """Our holdings of one player's innings vs the career figures in the Wikipedia infobox (matches, runs) per format."""
    ref = R.player_infobox(wiki_title); num = lambda s: int(s.replace(",", "")) if s and s.replace(",", "").isdigit() else None
    fmts = {"Test": "1", "ODI": "2", "T20I": "3"}
    out = {"subject": cs_name, "kind": "player", "formats": {}}
    for label, k in fmts.items():
        held = {"matches": 0, "innings": 0, "runs": 0, "balls": 0}
        for lab, p, m in C.matches("male"):
            if lab != label: continue
            if cs_name not in [x for t in m["info"]["players"].values() for x in t]: continue
            held["matches"] += 1
            for inn in m["innings"]:
                if inn.get("super_over"): continue
                bat = False
                for ov in inn["overs"]:
                    for d in ov["deliveries"]:
                        if d["batter"] == cs_name:
                            bat = True; held["runs"] += d["runs"]["batter"]; held["balls"] += "wides" not in d.get("extras", {})
                held["innings"] += bat
        rv = {"matches": num(ref.get("matches" + k)), "runs": num(ref.get("runs" + k))}
        gap = {x: (rv[x] - held[x]) if rv[x] is not None else None for x in rv}
        status = "UNVERIFIED" if rv["runs"] is None else "COMPLETE" if gap["matches"] == 0 and gap["runs"] == 0 else "GAPS"
        out["formats"][label] = {"held": held, "reference": rv, "gap": gap, "status": status, "as_of": "Wikipedia infobox (cites ESPNcricinfo)", "source": f"https://en.wikipedia.org/wiki/{wiki_title.replace(' ', '_')}",
                                 "held_from": None, "held_to": None}
    return out


def save(o):
    os.makedirs(f"{ROOT}/data/audit", exist_ok=True)
    json.dump(o, open(f"{ROOT}/data/audit/{o['kind']}_{o['subject'].replace(' ', '_')}.json", "w"), indent=1)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "opp":
        print(json.dumps(by_opponent(a[1], a[2]), indent=1)); sys.exit(0)
    if a[0] == "team":
        o = team(a[1], a[a.index("--since") + 1] if "--since" in a else None)
    else:
        o = player(a[1], a[2])
    show(o); save(o)
