"""Re-home each Short in its series look (see CLAUDE.md, "Series looks"). Narration is reused from short_classic.
    python3 make_series.py [slug ...]
Series: lab (data stories), tactics (boards + editorial charts), whatif (retro film, clippings), rising (trading card),
myth (stadium stage, unchanged here)."""
import copy, json, re, sys

SERIES = {
    "tactics": ["santner_problem", "abhishek_plan", "wellington_odi", "death_kings", "nz_test_preview"],
    "whatif": ["bradman_ipl", "sachin_t20", "dhoni_captain", "bumrah_vs_90s"],
    "lab": ["ipl_batting_evolution", "powerplay_revolution", "two_hundred"],
}
# per-slug touches: scene index -> overrides (merged into the converted scene) or a full replacement {"replace": {...}}
EXTRA = {
    "santner_problem": {0: {"replace": {"type": "board", "tone": "navy", "tag": "NZ v INDIA · T20Is", "head": ["One bowler India", "[couldn't hit.]"],
                                        "fielders": ["keeper", "point", "cover", "mid-off", "mid-on", "midwicket", "deep square leg", "long-on", "deep cover"],
                                        "labels": False, "pucks": [{"p": "bowler", "xy": [0.06, -0.42], "c": "hl", "label": "Santner", "at": .3}],
                                        "foot": "Illustrative field"}}},
    "abhishek_plan": {0: {"replace": {"type": "board", "tone": "navy", "tag": "MATCHUP DATA · IPL", "head": ["How to get", "[Abhishek] out"],
                                      "fielders": ["keeper", "slip", "point", "cover", "mid-off", "mid-on", "midwicket", "fine leg", "deep square leg"],
                                      "hl": ["slip"], "labels": False, "batter_label": "Abhishek", "foot": "Illustrative field"}}},
    "death_kings": {4: {}},
    "nz_test_preview": {1: {"replace": {"type": "board", "tone": "cream", "tag": "TESTS IN NZ", "head": ["Pace takes", "[86%] of wickets"],
                                        "fielders": ["keeper", "slip", "2nd slip", "3rd slip", "gully", "point", "mid-off", "mid-on", "fine leg"],
                                        "hl": ["slip", "2nd slip", "3rd slip", "gully"], "labels": True,
                                        "zones": [{"pos": ["slip", "2nd slip", "3rd slip", "gully"], "at": .35}],
                                        "paths": [{"from": [0.06, -0.42], "to": "2nd slip", "at": .55, "bend": .08}],
                                        "foot": "Illustrative field · share of wickets: data on screen next"}},
                        2: {}},
}


NAMES = {"Bumrah", "Kohli", "Sachin", "Tendulkar", "Dhoni", "Rohit", "Bradman", "Abhishek", "Santner", "Tilak", "Varma", "Shreyas", "Iyer", "Pathirana",
         "Bhuvneshwar", "Joginder", "Lara", "Umran", "Shoaib", "India", "New", "Zealand", "Wellington", "Jamieson", "Brar", "Gurnoor"}
STOP = {"in", "the", "of", "a", "an", "and", "to", "at", "on", "for", "by", "per", "vs", "v"}
ACR = {"IPL", "NZ", "ICC", "T20", "T20I", "T20IS", "ODI", "ODIS", "SR", "RCB", "CSK", "MI", "SRH", "DLS", "UAE", "WTC", "DC", "KKR", "GT", "LSG", "RR"}
VO = ""


def sc_(txt, mode="sentence"):
    """Sentence case that keeps acronyms and the proper nouns used in the narration."""
    out = []
    for k, w in enumerate(re.split(r"(\s+)", txt)):
        core = re.sub(r"[^A-Za-z0-9+\-']", "", w)
        if not core.strip(): out.append(w); continue
        if core.upper() in ACR: out.append(w.upper()); continue
        if any(ch.isdigit() for ch in core): out.append(w.lower() if k else w[:1].upper() + w[1:].lower()); continue
        m = core.capitalize() in NAMES or (core.lower() not in STOP and len(core) > 3 and re.search(r"\b(" + re.escape(core.capitalize()) + r")\b", VO))
        if m or (mode == "title") or (k == 0): out.append(w[:1].upper() + w[1:].lower())
        else: out.append(w.lower())
    return "".join(out)


def tok(name):
    return "".join(w[0] for w in name.replace("&", "").split()[:2]).upper()


def to_lab(sc, i, slug, look):
    t = sc["type"]
    head = (sc.get("head") or {}).get("t", "")
    sub = (sc.get("head") or {}).get("sub", "")
    if t in ("statement", "title"):
        lines = [ln["t"] if isinstance(ln, dict) else ln for ln in sc["lines"]]
        gold = [(ln.get("c") == "gold") if isinstance(ln, dict) else False for ln in sc["lines"]]
        txt = [f"[{ln}]" if g else ln for ln, g in zip(lines, gold)]
        if look == "whatif":
            return {"type": "clipping", "dateline": sc.get("kicker", "A WHAT IF? STORY"), "headline": [" ".join(lines)] if len(" ".join(lines)) < 22 else lines,
                    "seed": i + 3}
        return {"type": "lab_title", "kicker": sc.get("kicker", "STAT CHECK"), "lines": txt} if i == 0 else \
               {"type": "lab_big_text", "lines": txt}
    if t == "bignum":
        d = {"type": "lab_big", "title": "", "value": sc["value"], "dec": sc.get("dec", 0), "label": sc_(sc["label"]),
             "color": "red" if sc.get("color") in ("red",) else "ink" if sc.get("color") == "ink" else "red"}
        for k in ("prefix", "suffix", "from", "count_dur"):
            if k in sc: d[k] = sc[k]
        if sc.get("note"): d["kicker"] = sc["note"]
        if sc.get("suffix", "").strip() and not d.get("unit"):
            d["unit"] = sc["suffix"].strip().lower(); d.pop("suffix")
        return d
    if t == "bars" and len(sc["items"]) <= 3:
        return {"type": "lab_vs", "kicker": (sub or "THE NUMBERS").upper(), "title": sc_(head) + ".",
                "items": [{"label": sc_(it["label"], "title"), "v": it["value"],
                           "text": it.get("text") or f'{it["value"]:.{sc.get("dec", 0)}f}',
                           "c": {"gold": "red", "red": "red"}.get(it.get("color"), "ink"), "at": .1 + .3 * k} for k, it in enumerate(sc["items"])],
                "max": sc.get("max")}
    if t == "bars":
        vals = [it["value"] for it in sc["items"]]; hi = sc.get("max", max(vals) * 1.15)
        rows = [{"label": sc_(it["label"], "title"), "v": round(100 * it["value"] / hi, 1),
                 "text": it.get("text") or f'{it["value"]:.{sc.get("dec", 0)}f}', "hl": it.get("color") == "gold", "at": .1 + .25 * k}
                for k, it in enumerate(sc["items"])]
        return {"type": "lab_dots", "kicker": sub or "THE NUMBERS", "title": sc_(head) + ".", "rows": rows, "ticks": [0, 100],
                "domain": [0, 100], "tick_labels": False}
    if t == "compare" and len(sc["rows"]) == 1 and all(ch.isdigit() or ch in ".%" for ch in (sc["rows"][0][1] + sc["rows"][0][2]).replace(" ", "")):
        r = sc["rows"][0]; num = lambda v: float(v.replace("%", ""))
        return {"type": "lab_vs", "kicker": (r[0]).upper(), "title": sc_(head) + ".",
                "items": [{"label": sc_(sc["a"]["name"], "title"), "v": num(r[1]), "text": r[1], "c": "red" if r[3] == "a" else "ink", "at": .1},
                          {"label": sc_(sc["b"]["name"], "title"), "v": num(r[2]), "text": r[2], "c": "red" if r[3] == "b" else "ink", "at": .4}]}
    if t == "compare" and len(sc["rows"]) == 1:
        r = sc["rows"][0]; A, B = sc["a"], sc["b"]
        return {"type": "lab_compare", "kicker": "HEAD TO HEAD", "title": sc_(head) + ".",
                "a": {"t": tok(A["name"]), "kit": A.get("team", "ink"), "name": sc_(A["name"], "title")},
                "b": {"t": tok(B["name"]), "kit": B.get("team", "red"), "name": sc_(B["name"], "title")},
                "rows": [[sc_(r[0]), r[1], r[2], r[3]]]}
    if t == "stats":
        ti = sc["tiles"]
        if len(ti) == 1:
            return {"type": "lab_big_text", "kicker": head, "lines": [f"[{ti[0]['v']}]", ti[0]["l"].capitalize()]}
        return {"type": "lab_big_text", "kicker": head, "lines": [f"[{ti[0]['v']}] {sc_(ti[0]['l']).lower()}.", f"[{ti[1]['v']}] {ti[1]['l'].lower()}."]}
    if t == "fieldplan":
        d = {"type": "board", "tone": "cream" if i % 2 else "navy", "tag": "TACTICS BOARD", "fielders": sc.get("fielders", []), "hl": sc.get("hl", []),
             "head": [sc_(head)], "foot": "Illustrative field"}
        if sc.get("length"): d["length"] = {"from": sc["length"]["from"], "to": sc["length"]["to"], "at": .2}
        if sc.get("hl"): d["zones"] = [{"pos": sc["hl"], "at": .35}]
        for s_ in sc.get("shots", []):
            d.setdefault("paths", []).append({"from": [0, .25], "to": s_["to"], "at": .5, "bend": .15})
        return d
    if t == "trajectory":
        return {"type": "board", "tone": "navy", "tag": "TACTICS BOARD", "head": [sc_(head)], "fielders": ["keeper", "slip", "gully", "fine leg", "deep square leg"],
                "length": {"from": 9, "to": 12, "at": .15, "c": "red"}, "paths": [{"from": [0.06, -0.42], "to": [0, .1], "at": .3, "bend": 0, "c": "red"}],
                "foot": "Illustrative"}
    if t == "matchup":
        L, R = sc["left"], sc["right"]
        return {"type": "lab_compare", "kicker": (sc.get("head") or {}).get("t", "THE MATCHUP"), "title": "The matchup.",
                "a": {"t": tok(L["name"]), "kit": L.get("team", "ink"), "name": sc_(L["name"], "title")},
                "b": {"t": tok(R["name"]), "kit": R.get("team", "ink"), "name": sc_(R["name"], "title")},
                "rows": [[sc_(r[0]), r[1], r[2], "level"] for r in sc.get("rows", [])]}
    return None


def convert_whatif(slug):
    import make_stage_shorts as M
    M.convert(slug)                                    # stadium-stage version from short_classic
    p = f"specs/{slug}.json"; spec = json.load(open(p)); sh = spec["short"]
    first = spec["short_classic"][0]["scene"]
    if first["type"] in ("statement", "title"):
        lines = [ln["t"] if isinstance(ln, dict) else ln for ln in first["lines"]]
        sh[0]["scene"] = {"type": "clipping", "dateline": first.get("kicker", "A WHAT IF? STORY"), "headline": lines, "seed": 4}
    content = [k for k, x in enumerate(sh) if x["scene"]["type"] != "cta"]
    for k in content[:-1]: sh[k]["scene"]["film"] = True
    sh[content[-1]]["scene"]["film"] = False          # back to colour: today
    spec["theme"] = "stadium"; spec["captions"] = "serif"; spec["series"] = "whatif"
    import voice_lint; voice_lint.fix_spec(spec)
    json.dump(spec, open(p, "w"), ensure_ascii=False, indent=1)
    return slug


def convert(slug, look):
    if look == "whatif": return convert_whatif(slug)
    p = f"specs/{slug}.json"; spec = json.load(open(p))
    classic = spec.get("short_classic") or spec["short"]; spec["short_classic"] = classic
    if spec.get("theme", "whites") not in ("stadium",) and "theme_long" not in spec: spec["theme_long"] = spec.get("theme", "whites")
    global VO
    VO = " ".join(x["vo"] for x in classic)
    out = []
    for i, para in enumerate(classic):
        sc = para["scene"]; ex = EXTRA.get(slug, {}).get(i, {})
        if sc["type"] == "cta": new = copy.deepcopy(sc)
        elif "replace" in ex: new = copy.deepcopy(ex["replace"])
        elif sc["type"] in ("over", "gauge"): new = copy.deepcopy(sc)
        else: new = to_lab(sc, i, slug, look) or copy.deepcopy(sc)
        if look == "whatif" and new["type"] not in ("clipping",) and i < len(classic) - 2: new["film"] = True
        out.append({"vo": para["vo"], "scene": new})
    spec["short"] = out
    spec["theme"] = {"tactics": "lab", "whatif": "retro", "lab": "lab"}[look]
    spec["captions"] = "serif" if look in ("tactics", "whatif") else "lab"
    spec["series"] = look
    spec.pop("venue", None)
    import voice_lint; voice_lint.fix_spec(spec)
    json.dump(spec, open(p, "w"), ensure_ascii=False, indent=1)
    return slug


if __name__ == "__main__":
    want = set(sys.argv[1:])
    for look, slugs in SERIES.items():
        for s in slugs:
            if not want or s in want: print(look, convert(s, look))
