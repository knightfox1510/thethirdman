"""Rebuild the Shorts of existing specs in the stadium-stage look (see CLAUDE.md, production defaults).
    python3 make_stage_shorts.py [slug ...]
The original Short is kept in spec["short_classic"]; narration lines are reused, so the voice cache still applies.
Each slug below gives: kit/number/venue, and per scene the poses, camera, view, ball and opponents."""
import copy, json, sys

WHITES = [238, 234, 220]                     # cream Test kit


def panel_for(sc, first):
    """Turn a classic scene into a stage panel (None = keep the classic scene as it is)."""
    t = sc["type"]; at = 0.0 if first else .05
    if t in ("statement", "title"):
        return {"kind": "headline", "at": at, "kicker": sc.get("kicker", ""), "lines": sc["lines"]}
    if t == "bignum":
        p = {"kind": "bignum", "at": at, "label": sc["label"]}
        for k in ("value", "dec", "prefix", "suffix", "color", "count_dur", "from"):
            if k in sc: p[k] = sc[k]
        if sc.get("note"): p["kicker"] = sc["note"]
        return p
    if t == "compare" and len(sc["rows"]) == 1:
        r = sc["rows"][0]
        return {"kind": "versus", "at": at, "kicker": sc["head"]["t"],
                "left": {"v": r[1], "l": sc["a"]["name"], "c": sc["a"].get("color", "gold" if r[3] == "a" else "ink")},
                "right": {"v": r[2], "l": sc["b"]["name"], "c": sc["b"].get("color", "gold" if r[3] == "b" else "ink")}}
    if t == "bars":
        rows = [[i["label"], i.get("text") or f'{i["value"]:.{sc.get("dec", 0)}f}', i.get("color", "ink")] for i in sc["items"]]
        k = sc["head"]["t"] + (" · " + sc["head"]["sub"] if sc["head"].get("sub") else "")
        return {"kind": "table", "at": at, "kicker": k, "rows": rows}
    if t == "stats":
        ti = sc["tiles"]
        if len(ti) == 1: return {"kind": "score", "at": at, "kicker": sc["head"]["t"], "event": ti[0]["l"], "score": ti[0]["v"], "color": ti[0].get("c", "gold")}
        return {"kind": "versus", "at": at, "kicker": sc["head"]["t"], "left": {"v": ti[0]["v"], "l": ti[0]["l"], "c": ti[0].get("c", "ink")},
                "right": {"v": ti[1]["v"], "l": ti[1]["l"], "c": ti[1].get("c", "gold")}}
    return None


# per scene: dict with p (pose), cam, view, x, hit, ball, opp (extra avatars), panel (override), keep (keep classic scene)
CFG = {
 "nz_test_preview": dict(kit="IND", venue={"time": "day", "crowd": [[25, 25, 25], [235, 235, 235], [40, 90, 200], [60, 60, 60]], "boards": [[25, 25, 25], [235, 235, 235]]},
   scenes=[dict(p="walk", x=.32, x2=.5, cam="push", opp=[dict(kit="NZ", pose="stand", x=.78, scale=.85, cap=True)]),
           dict(view="side", p="stance", x=.3, cam="wide", opp=[dict(kit="NZ", pose="bowl", x=.78, dir=-1)], stumps=[.2, .93]),
           dict(p="dejected", cam="close"), {}]),
 "santner_problem": dict(kit="NZ", number=74, venue={"time": "night", "crowd": [[40, 90, 200], [250, 150, 40], [230, 230, 240]]},
   scenes=[dict(view="side", p="bowl", x=.62, dir=-1, cap=True, cam="push"),
           dict(p="stand", cap=True, cam="drift"),
           dict(p="celebrate", cap=True, cam="push"),
           dict(view="side", p="bowl", x=.66, dir=-1, cam="pull", opp=[dict(kit="IND", pose="stance", x=.26)], stumps=[.17, .93]), {}]),
 "abhishek_plan": dict(kit="SRH", venue={"time": "night", "crowd": [[255, 120, 20], [30, 30, 30], [240, 240, 240]], "boards": [[255, 120, 20], [30, 30, 30]]},
   scenes=[dict(p="walk", x=.3, x2=.5, cam="push"),
           dict(view="side", p="stance", hit="drive", x=.32, cam="wide", ball={"at": .55, "shot": "bowled"}, stumps=[.2, .93],
                panel={"kind": "versus", "at": .05, "kicker": "OUT WITHIN HIS FIRST SIX BALLS · IPL", "left": {"v": "25", "l": "Times", "c": "red"}, "right": {"v": "89", "l": "Innings", "c": "ink"}}),
           dict(p="stand", cam="close"),
           dict(view="side", p="stance", x=.3, cam="push", opp=[dict(kit="ink", pose="bowl", x=.76, dir=-1)], stumps=[.2, .93]), {}]),
 "death_kings": dict(kit="MI", number=93, cap=True, venue={"time": "night", "crowd": [[0, 75, 160], [212, 175, 55], [235, 235, 245]], "boards": [[0, 75, 160], [212, 175, 55]]},
   scenes=[dict(view="side", p="stance", hit="pull", x=.36, cam="push", kit="CSK", number=None, cap=False, ball={"at": .5, "shot": "six"}),
           dict(view="side", p="bowl", x=.64, dir=-1, cam="wide"),
           dict(p="stand", cam="drift"),
           dict(p="celebrate", cam="push"), {}]),
 "rcb_back_to_back": dict(kit="RCB", cap=True, venue={"time": "night", "crowd": [[200, 30, 40], [212, 175, 55], [30, 30, 30]], "boards": [[200, 30, 40], [212, 175, 55]]},
   scenes=[dict(view="side", p="bowl", x=.62, dir=-1, cam="push"),
           dict(p="stand", cam="drift"),
           dict(view="side", p="stance", hit="drive", x=.32, cam="wide", kit="SRH", cap=False, ball={"at": .55, "shot": "bowled"}, stumps=[.2, .93]),
           dict(p="celebrate", cam="push"), {}]),
 "powerplay_revolution": dict(kit="SRH", venue={"time": "night", "crowd": [[255, 120, 20], [40, 90, 200], [240, 240, 240], [200, 30, 40]]},
   scenes=[dict(view="side", p="stance", hit="pull", x=.36, cam="push", ball={"at": .45, "shot": "six"}),
           dict(p="walk", x=.35, x2=.5, cam="drift"),
           dict(p="celebrate", cam="push"),
           dict(p="stand", cam="close"), {}]),
 "bumrah_economy": dict(kit="IND", number=93, cap=True, venue={"time": "night", "crowd": [[40, 90, 200], [250, 150, 40], [230, 230, 240]]},
   scenes=[dict(view="side", p="bowl", x=.64, dir=-1, cam="push"),
           dict(p="stand", cam="drift"),
           dict(p="celebrate", cam="push"),
           dict(p="dejected", kit="MI", cam="close"),
           dict(p="stand", cam="wide"), {}]),
 "bumrah_vs_90s": dict(kit="IND", number=93, venue={"time": "day", "crowd": [[230, 230, 240], [40, 90, 200], [120, 120, 130]]},
   scenes=[dict(view="side", p="bowl", x=.7, dir=-1, cap=True, cam="push", opp=[dict(kit=WHITES, pose="stance", x=.28)], stumps=[.18, .93],
                panel={"kind": "versus", "at": 0.0, "kicker": "ONE OVER · ILLUSTRATIVE", "left": {"v": "BUMRAH", "l": "Today", "c": "gold"}, "right": {"v": "90s", "l": "Sachin & Lara", "c": "ink"}}),
           dict(keep=True), {}]),
 "dhoni_captain": dict(kit="IND", number=7, venue={"time": "dusk", "crowd": [[40, 90, 200], [250, 150, 40], [230, 230, 240], [0, 120, 75]]},
   scenes=[dict(p="walk", x=.3, x2=.5, cam="push"),
           dict(p="raise", cam="pull"),
           dict(view="side", p="bowl", x=.66, dir=-1, number=None, cap=True, cam="wide", opp=[dict(kit="PAK", pose="stance", x=.26)], stumps=[.17, .93]),
           dict(view="side", p="stance", x=.4, number=None, cam="drift"), {}]),
 "sachin_t20": dict(kit="IND", number=10, venue={"time": "night", "crowd": [[40, 90, 200], [250, 150, 40], [230, 230, 240]]},
   scenes=[dict(p="walk", x=.3, x2=.5, cam="push"),
           dict(p="stand", cam="drift"),
           dict(p="raise", cam="push"),
           dict(view="side", p="stance", hit="pull", x=.34, cam="wide", ball={"word": "upper", "shot": "six", "side": -1}, stumps=[.2, .93],
                opp=[dict(kit="PAK", pose="bowl", x=.84, dir=-1)],
                panel={"kind": "headline", "at": .05, "kicker": "ILLUSTRATIVE", "lines": [{"t": "THE UPPER CUT"}, {"t": "OVER THIRD MAN", "c": "gold"}]}),
           dict(p="celebrate", cam="push"), {}]),
 "bradman_ipl": dict(kit=WHITES, cap=True, pads=True, venue={"time": "day", "crowd": [[230, 230, 240], [0, 90, 50], [212, 175, 55], [120, 120, 130]]},
   scenes=[dict(p="walk", x=.3, x2=.5, cam="push", bat=True),
           dict(p="stand", cam="drift", bat=True),
           dict(view="side", p="stance", x=.38, cam="wide"),
           dict(view="side", p="stance", hit="drive", x=.36, cam="push", ball={"at": .45, "shot": "four"}),
           dict(view="side", p="stance", hit="pull", x=.36, kit=[212, 175, 55], cap=False, pads=None, cam="push", ball={"word": "owns", "shot": "six"}), {}]),
 "india_160": dict(kit="IND", cap=True, venue={"time": "night", "crowd": [[40, 90, 200], [250, 150, 40], [230, 230, 240]]},
   scenes=[dict(view="side", p="bowl", x=.66, dir=-1, cam="push"),
           dict(keep=True),
           dict(view="side", p="stance", x=.3, cam="wide", cap=False, kit="AUS", ball={"at": .4, "shot": "bowled"}, hit="drive", stumps=[.18, .93]),
           dict(p="celebrate", number=93, cam="push"), {}]),
 "two_hundred": dict(kit="KKR", venue={"time": "night", "crowd": [[58, 34, 95], [212, 175, 55], [240, 240, 240], [255, 120, 20]]},
   scenes=[dict(view="side", p="stance", hit="pull", x=.36, cam="push", ball={"at": .55, "shot": "six"}),
           dict(p="stand", cam="drift"),
           dict(p="celebrate", cam="push"),
           dict(view="side", p="stance", hit="drive", x=.36, cam="wide", ball={"word": "harder", "shot": "six", "side": 1}), {}]),
 "anchor": dict(kit="LSG", venue={"time": "night", "crowd": [[0, 160, 220], [200, 30, 40], [240, 240, 240]]},
   scenes=[dict(p="walk", x=.3, x2=.5, cam="push"),
           dict(p="dejected", cam="close"),
           dict(view="side", p="stance", hit="drive", x=.36, kit="RCB", number=18, cam="push", ball={"at": .6, "shot": "six", "side": 1}),
           dict(p="stand", cam="wide"), {}]),
 "wellington_odi": dict(kit="IND", venue={"time": "dusk", "crowd": [[25, 25, 25], [235, 235, 235], [40, 90, 200]], "boards": [[25, 25, 25], [235, 235, 235]]},
   scenes=[dict(p="walk", x=.3, x2=.5, cam="push", opp=[dict(kit="NZ", pose="dejected", x=.8, scale=.85, cap=True)]),
           dict(keep=True), dict(keep=True),
           dict(p="celebrate", cam="push"), {}]),
 "ipl_batting_evolution": dict(kit="CSK", venue={"time": "night", "crowd": [[255, 205, 0], [0, 75, 160], [200, 30, 40], [240, 240, 240]]},
   scenes=[dict(p="walk", x=.3, x2=.5, cam="push"),
           dict(view="side", p="stance", hit="pull", x=.36, cam="push", kit="SRH", ball={"at": .35, "shot": "six"}),
           dict(p="stand", cam="drift"),
           dict(p="celebrate", cam="push"), {}]),
}


def convert(slug):
    p = f"specs/{slug}.json"; spec = json.load(open(p)); cfg = CFG[slug]
    if spec.get("theme", "whites") != "stadium" and "theme_long" not in spec: spec["theme_long"] = spec.get("theme", "whites")
    classic = spec.get("short_classic") or copy.deepcopy(spec["short"]); spec["short_classic"] = classic
    out = []
    for i, (para, sc_cfg) in enumerate(zip(classic, cfg["scenes"] + [{}] * 20)):
        sc = para["scene"]
        if sc["type"] == "cta" or sc_cfg.get("keep"):
            out.append(copy.deepcopy(para)); continue
        panel = sc_cfg.get("panel") or panel_for(sc, i == 0)
        if panel is None: out.append(copy.deepcopy(para)); continue
        A = {"kit": sc_cfg.get("kit", cfg["kit"]), "pose": sc_cfg.get("p", "stand"), "x": sc_cfg.get("x", .5)}
        num = sc_cfg.get("number", cfg.get("number"))
        if num is not None: A["number"] = num
        for k in ("x2", "dir", "hit", "bat"):
            if k in sc_cfg: A[k] = sc_cfg[k]
        for k in ("cap", "pads"):
            v = sc_cfg.get(k, cfg.get(k))
            if v is not None: A[k] = v
        new = {"type": "stage", "panel": panel, "avatars": [A] + sc_cfg.get("opp", []), "cam": sc_cfg.get("cam", "drift")}
        for k in ("view", "ball", "stumps"):
            if k in sc_cfg: new[k] = sc_cfg[k]
        out.append({"vo": para["vo"], "scene": new})
    spec["short"] = out
    spec["theme"] = "stadium"; spec["captions"] = "v2"; spec["venue"] = cfg["venue"]
    json.dump(spec, open(p, "w"), ensure_ascii=False, indent=1)
    return slug


if __name__ == "__main__":
    for s in sys.argv[1:] or CFG: print("converted", convert(s))
