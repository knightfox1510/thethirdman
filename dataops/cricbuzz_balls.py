"""Turn a Cricbuzz full-commentary capture (data/cricbuzz/<f>.json) into clean tables: balls, overs, wickets, partnerships, editorial notes.
    python3 -m dataops.cricbuzz_balls data/cricbuzz/nz_ind_5odi.json [outdir]
Each delivery (including wides and no-balls) is one row; `legal` marks the deliveries that count as a ball. Runs per delivery are the change in the team score, so extras are included.
The innings totals are checked against the last score shown in the commentary; a mismatch raises, so nothing is silently wrong.
Cricbuzz gives no line / length / wagon data: use the Cricinfo capture (dataops.matchdata / cricinfo_import) when there is one."""
import csv, json, os, re, sys, collections

DISM = [("run out", r"\brun out\b"), ("stumped", r"\bstumped\b"), ("lbw", r"\blbw\b"), ("hit wicket", r"\bhit[- ]wicket\b"), ("caught", r"\bcaught\b"), ("bowled", r"\bbowled\b")]
EXTRA = [("wide", r"\bwide\b(?!\s+of|\s+outside|\s+down)"), ("no ball", r"\bno[- ]ball\b|\bFree Hit\b"), ("leg bye", r"\bleg byes?\b"), ("bye", r"\bbyes?\b(?!.*leg)")]


def load(path):
    d = json.load(open(path, encoding="utf-8")); cs = d["comments"]
    cs = [c for c in cs if c.get("inningsId")]
    return d, sorted(cs, key=lambda c: (c["inningsId"], c["timestamp"]))


def parse(path):
    d, cs = load(path); balls, overs, notes = [], [], []
    state = {}
    for c in cs:
        inn = c["inningsId"]
        if c.get("overNumber") is None or not c.get("ballNbr"):
            notes.append({"inning": inn, "text": re.sub(r"B\d\$", "", c["commText"]).strip(), "event": c.get("event")})
            continue
        s = state.setdefault(inn, {"score": 0, "ball": 0, "wkts": 0})
        text = re.sub(r"B\d\$", "", c["commText"]).strip()
        m = re.match(r"^(.*?) to (.*?),", text); bowler, batter = (m.group(1).strip(), m.group(2).strip()) if m else ((c.get("bowlerStriker") or {}).get("bowlName", ""), (c.get("batsmanStriker") or {}).get("batName", ""))
        sb, sw = (c.get("batsmanStriker") or {}).get("batName", ""), (c.get("bowlerStriker") or {}).get("bowlName", "")        # the structured full names win over the commentary's short forms ("Rahul", "Nicholls")
        if sb: batter = sb
        if sw: bowler = sw
        score = c.get("batTeamScore", s["score"]); runs = score - s["score"]
        legal = c["ballNbr"] != s["ball"]
        ev = c.get("event") or ""
        wicket = "WICKET" in ev; kind = None
        if wicket:
            head = text.split("!!")[0] if "!!" in text[:200] else text[:200]
            kind = next((k for k, rx in DISM if re.search(rx, head, re.I)), "other")
        extra = None
        head = text[:90]
        if not legal: extra = "no ball" if (c.get("legalRuns", 0) > 0 or re.search(r"\bno[- ]ball\b|\bfree hit\b", head, re.I)) else "wide"     # a delivery that is not a legal ball is a wide or a no-ball
        elif runs > 0 and c.get("legalRuns", 0) == 0:
            extra = "leg bye" if re.search(r"\bleg byes?\b", head, re.I) else "bye" if re.search(r"\bbyes?\b", head, re.I) else None
        if wicket: s["wkts"] += 1
        balls.append({"inning": inn, "bat_team": c.get("batTeamName"), "over": c["overNumber"], "ball_no": c["ballNbr"], "legal": legal, "bowler": bowler, "batter": batter,
                      "runs": runs, "bat_runs": c.get("legalRuns", 0), "extra": extra, "wicket": wicket, "dismissal": kind, "event": ev, "score_after": score, "wkts_after": s["wkts"],
                      "striker_runs": (c.get("batsmanStriker") or {}).get("batRuns"), "striker_balls": (c.get("batsmanStriker") or {}).get("batBalls"), "text": text, "ts": c["timestamp"]})
        sr_ = (c.get("batsmanStriker") or {}).get("batRuns")                      # runs off the bat = change in the striker's own total (covers no-ball boundaries, which legalRuns misses)
        prev = s.setdefault("bat", {}).get(batter)
        if sr_ is not None and batter:
            balls[-1]["bat_runs"] = max(0, sr_ - (prev if prev is not None else 0)) if (prev is not None or sr_ <= 6) else balls[-1]["bat_runs"]; s["bat"][batter] = sr_
        s["score"], s["ball"] = score, c["ballNbr"]
        sep = c.get("overSeparator")
        if sep:
            overs.append({"inning": inn, "over": int(c["overNumber"]) + (1 if c["overNumber"] % 1 > .5 or round(c["overNumber"] % 1, 1) == .6 else 0), "score": sep.get("score"), "wickets": sep.get("wickets"), "runs": sep.get("runs"),
                          "balls": (sep.get("o_summary") or "").strip(), "bowler": ", ".join(sep.get("bowlNames", [])), "batters": ", ".join(sep.get("batStrikerNames", []) + sep.get("batNonStrikerNames", []))})
    for inn, s in state.items():                                                        # self-check: totals against the commentary's own last score
        assert s["score"] == [b for b in balls if b["inning"] == inn][-1]["score_after"]
    return {"meta": {"match_id": d.get("match_id"), "slug": d.get("match_slug")}, "balls": balls, "overs": overs, "notes": notes}


def wickets(balls):
    out = []
    for b in balls:
        if not b["wicket"]: continue
        t = b["text"]; out_name = b["batter"]
        if b["dismissal"] == "run out":                                                    # the dismissed batter may be the non-striker: Cricbuzz writes "<name> Run Out!!"
            m = re.search(r",\s+([A-Z][\w'. -]+?)\s+run out", t[:200], re.I)
            if m: out_name = m.group(1).strip()
        fld = re.search(r"[Cc]aught (?:by|at)\s+(?:\(sub\)\s*)?([A-Z][\w' .-]+?)\s*[!.,]", t) or re.search(r"[Cc]aught (?:and|&) [Bb]owled", t[:80]) and re.match(r"(.*)", b["bowler"])
        out.append({"inning": b["inning"], "over": b["over"], "wicket_no": b["wkts_after"], "score": b["score_after"], "batter": out_name, "bowler": b["bowler"], "kind": b["dismissal"],
                    "fielder": fld.group(1).strip() if fld else None, "runs_of_batter": b["striker_runs"], "balls_of_batter": b["striker_balls"], "text": t[:300]})
    return out


def partnerships(balls):
    """Runs and balls between wickets, with the batters who faced a ball in that window."""
    out = []
    for inn in sorted({b["inning"] for b in balls}):
        bb = [b for b in balls if b["inning"] == inn]; cur = {"start_score": 0, "balls": 0, "batters": collections.Counter(), "n": 1}
        for b in bb:
            if b["legal"]: cur["balls"] += 1
            cur["batters"][b["batter"]] += 1
            if b["wicket"] or b is bb[-1]:
                out.append({"inning": inn, "wicket": b["wkts_after"] if b["wicket"] else None, "runs": b["score_after"] - cur["start_score"], "balls": cur["balls"], "batters": " & ".join(n for n, _ in cur["batters"].most_common(3)), "end_over": b["over"]})
                cur = {"start_score": b["score_after"], "balls": 0, "batters": collections.Counter(), "n": cur["n"] + 1}
    return out


def save(res, outdir, stem):
    os.makedirs(outdir, exist_ok=True)
    def w(name, rows):
        if not rows: return
        with open(f"{outdir}/{stem}_{name}.csv", "w", newline="", encoding="utf-8") as f:
            wr = csv.DictWriter(f, fieldnames=list(rows[0].keys())); wr.writeheader(); wr.writerows(rows)
    w("balls", res["balls"]); w("overs", res["overs"]); w("notes", res["notes"]); w("wickets", wickets(res["balls"])); w("partnerships", partnerships(res["balls"]))


if __name__ == "__main__":
    p = sys.argv[1]; res = parse(p); od = sys.argv[2] if len(sys.argv) > 2 else "data/series/nz_ind_2026"
    save(res, od, os.path.basename(p)[:-5])
    for inn in (1, 2):
        bb = [b for b in res["balls"] if b["inning"] == inn]
        print(f"innings {inn}: {bb[-1]['score_after']}/{bb[-1]['wkts_after']} in {sum(b['legal'] for b in bb)} legal balls, {len(bb)} deliveries")
