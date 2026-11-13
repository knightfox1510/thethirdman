"""Turn a Third Man capture file (tools/ttm-capture, saved from a Cricinfo match page you opened)
into a ball table like stats.py's, plus a field report.
    python3 cricinfo_import.py data/cricinfo/cricinfo_<id>.json [data/cricbuzz/cricbuzz_<id>.json]
Cricinfo is the backbone (line, length, shot, control, wagon wheel). The optional Cricbuzz capture is checked
against it over by over and adds its running scores plus the notes between balls (field changes, pitch, stats leads).
Use the numbers for our own analysis and graphics; do not reproduce Cricinfo's text or charts.
Field names are read defensively: run the report on the first real capture and adjust FIELDS if needed."""
import json, sys, os, re
import pandas as pd

# our column -> candidate keys in the Cricinfo ball item
FIELDS = {
    "inning": ["inningNumber", "inning"], "over_no": ["overNumber"], "ball_no": ["ballNumber"], "overs": ["oversActual", "oversUnique"],
    "batter_id": ["batsmanPlayerId"], "bowler_id": ["bowlerPlayerId"], "nonstriker_id": ["nonStrikerPlayerId"],
    "runs": ["totalRuns"], "bat_runs": ["batsmanRuns"], "four": ["isFour"], "six": ["isSix"], "wicket": ["isWicket"],
    "wides": ["wides"], "noballs": ["noballs"], "byes": ["byes"], "legbyes": ["legbyes"], "penalties": ["penalties"],
    "out_id": ["outPlayerId", "dismissalPlayerId"], "dismissal": ["dismissalType", "dismissalText"],
    # tracking-style fields (present on many Cricinfo matches; may be missing or null)
    "wagon_x": ["wagonX"], "wagon_y": ["wagonY"], "wagon_zone": ["wagonZone"], "pitch_line": ["pitchLine"],
    "pitch_length": ["pitchLength"], "shot": ["shotType"], "control": ["shotControl"],
}


def pick(d, keys):
    for k in keys:
        if k in d and d[k] is not None: return d[k]
    return None


def players(cap):
    """id -> name, from any object in the captured pages/API that looks like a player."""
    out = {}
    def walk(o, depth=0):
        if depth > 12 or o is None: return
        if isinstance(o, dict):
            if isinstance(o.get("objectId") or o.get("id"), int) and (o.get("longName") or o.get("name")) and ("battingStyles" in o or "playingRoles" in o or "longName" in o):
                for k in ("id", "objectId"):
                    if isinstance(o.get(k), int): out.setdefault(o[k], o.get("longName") or o.get("name"))
            for v in o.values(): walk(v, depth + 1)
        elif isinstance(o, list):
            for v in o: walk(v, depth + 1)
    walk(cap.get("pages")); walk([a.get("body") for a in cap.get("api", [])])
    return out


def table(cap):
    P = players(cap)
    rows = []
    for c in cap.get("comments", []):
        r = {k: pick(c, ks) for k, ks in FIELDS.items()}
        r["batter"] = P.get(r["batter_id"]); r["bowler"] = P.get(r["bowler_id"])
        r["legal"] = not (r["wides"] or 0) and not (r["noballs"] or 0)
        txt = c.get("commentTextItems") or c.get("commentText")
        r["has_text"] = bool(txt)
        rows.append(r)
    df = pd.DataFrame(rows)
    if len(df): df = df.sort_values(["inning", "over_no", "ball_no"], na_position="last").reset_index(drop=True)
    return df


def report(df, cap):
    print(f"match {cap.get('match_id')} · {len(df)} ball items · tabs {list(cap.get('pages', {}))} · {len(cap.get('api', []))} API responses")
    if not len(df): print("no ball items found: open the ball-by-ball tab, press 'Load all commentary' for each innings, then save"); return
    for k in FIELDS: print(f"  {k:14s} {df[k].notna().mean():5.0%} filled")
    print("  names         ", f"{df['batter'].notna().mean():.0%} batters, {df['bowler'].notna().mean():.0%} bowlers resolved")
    for inn, g in df.groupby("inning"):
        legal = g[g.legal]
        print(f"  innings {inn}: {int(g.runs.fillna(0).sum())} runs, {int(g.wicket.fillna(False).astype(bool).sum())} wkts, "
              f"{len(legal)} legal balls (overs {legal.overs.max()})  <- check against the official scorecard")


def cricbuzz(cb, df):
    """Attach Cricbuzz ball numbers + notes, after checking both sources agree over by over."""
    items = sorted(cb.get("comments", []), key=lambda x: x.get("timestamp") or 0)
    balls = [x for x in items if x.get("ballNbr")]
    bdf = pd.DataFrame([dict(inning=x.get("inningsId"), ov=x.get("overNumber"), runs=x.get("totalRuns") or 0, event=x.get("event")) for x in balls])
    bdf["over_no"] = bdf.groupby("inning").ov.ffill().apply(lambda v: int(v) + 1)
    a = df.groupby(["inning", "over_no"]).runs.sum(); b = bdf.groupby(["inning", "over_no"]).runs.sum()
    bad = (a - b).dropna(); bad = bad[bad != 0]
    print(f"cricbuzz: {len(balls)} balls; over-by-over runs " + ("MATCH" if bad.empty else f"DIFFER in {list(bad.index)}"))
    # notes between balls, tagged with the ball they follow
    notes, last = [], None
    for x in items:
        if x.get("ballNbr"): last = (x.get("inningsId"), x.get("overNumber")); continue
        t = re.sub(r"[BI]\d\$", "", x.get("commText") or "").strip()
        if t: notes.append(dict(inning=(last or (None,))[0], after_over=(last or (None, None))[1], note=t))
    return pd.DataFrame(notes)


if __name__ == "__main__":
    f = sys.argv[1]
    cap = json.load(open(f))
    df = table(cap)
    report(df, cap)
    if len(sys.argv) > 2:
        nt = cricbuzz(json.load(open(sys.argv[2])), df)
        nf = os.path.splitext(f)[0] + "_notes.csv"; nt.to_csv(nf, index=False); print(f"wrote {nf} ({len(nt)} notes: leads to verify, not text to copy)")
    out = os.path.splitext(f)[0] + "_balls.csv"
    df.to_csv(out, index=False); print("wrote", out)
