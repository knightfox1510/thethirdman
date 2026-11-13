"""Refresh the dashboard's generated data (site/data/library.json, stills.json, replay_sample.json, video_map.json).
(drive.json comes from drive_links.py.)
    python3 site_build.py [--work /home/claude/video]
formats.json, schedule.json, fixtures.json and ideas/ are edited directly (by hand or by the daily ideas task).
Vercel serves site/ as-is (vercel.json), so a push is a deploy."""
import json, glob, os, subprocess, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = sys.argv[sys.argv.index("--work") + 1] if "--work" in sys.argv else (os.path.exists("/home/claude/video") and "/home/claude/video") or HERE
OUT = os.path.join(HERE, "site", "data")

SERIES = {"myth_ep1_kohli_knockouts": "myth", "anchor": "myth", "bumrah_economy": "myth", "india_160": "myth", "rcb_back_to_back": "myth",
          "lab_ep1_abhishek_twin": "lab", "lab_ep2_bumrah_twin": "lab", "ipl_batting_evolution": "lab", "powerplay_revolution": "lab", "two_hundred": "lab",
          "stat_check_bumrah_rashid": "statcheck", "wellington_odi": "tactics", "santner_problem": "tactics", "abhishek_plan": "tactics",
          "death_kings": "tactics", "nz_test_preview": "tactics", "bradman_ipl": "whatif", "sachin_t20": "whatif", "dhoni_captain": "whatif",
          "bumrah_vs_90s": "whatif", "aaryavir_sehwag": "rising", "kohli_2000_nz": "news", "hardik_arshdeep": "news", "channel_trailer": "news"}
# titles and re-check notes as kept in the schedule sheet's Library tab
TITLES = {"channel_trailer": "Channel trailer", "ipl_batting_evolution": "How the IPL Changed T20 Batting Forever",
          "nz_test_preview": "Can India Win a Test Series in New Zealand?", "hardik_arshdeep": "Hardik–Arshdeep trade: who won?",
          "wellington_odi": "How India won the Wellington ODI", "santner_problem": "The Santner Problem", "abhishek_plan": "Who Should Bowl to Abhishek Sharma?",
          "powerplay_revolution": "The IPL Powerplay Revolution", "death_kings": "Who Rules the Death Overs (IPL)", "rcb_back_to_back": "How RCB Won Back-to-Back",
          "bumrah_vs_90s": "Bumrah vs 90s Sachin & Lara", "sachin_t20": "What If Sachin Played in the T20 Era", "bradman_ipl": "What If Bradman Played in the IPL",
          "dhoni_captain": "What If Dhoni Never Became Captain", "india_160": "Why No Indian Has Bowled 160", "anchor": "Is the T20 Anchor Dead?",
          "bumrah_economy": "Bumrah's Economy Makes No Sense", "two_hundred": "Why 200 Is the New 160", "kohli_2000_nz": "Kohli: 22 runs from 2,000 vs NZ",
          "flip_mi_captains": "Flip: Every MI captain vs Rohit", "flip_bumrah_52_tests": "Flip: Bumrah vs the best fast bowlers after 52 Tests",
          "flip_root_same_point": "Flip: Joe Root vs everyone at the same point", "flip_abhishek_openers": "Flip: Abhishek vs the world's T20I openers",
          "lab_ep1_abhishek_twin": "The Lab Ep. 1: Abhishek Sharma's statistical twin", "lab_ep2_bumrah_twin": "The Lab Ep. 2: Bumrah's twin",
          "stat_check_bumrah_rashid": "Stat Check: Bumrah or Rashid?", "myth_ep1_kohli_knockouts": "Myth or Data? Ep. 1: Kohli in knockouts",
          "aaryavir_sehwag": "Rising Star: Aaryavir Sehwag"}
RECHECK = {"nz_test_preview": "Pant fitness, WTC table", "hardik_arshdeep": "MI captaincy news", "abhishek_plan": "Any new IPL/T20I data",
           "india_160": "Fastest-Indian speeds", "kohli_2000_nz": "Expires once he bats in the 4th ODI", "flip_mi_captains": "New MI captain named?",
           "flip_bumrah_52_tests": "Bumrah's Test count changes after the NZ series", "flip_root_same_point": "Root/Brook/Jaiswal totals after new Tests"}


def dur(p):
    if not os.path.exists(p): return None
    s = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))
    return f"{int(s // 60)}:{int(s % 60):02d}"


def library():
    sched = json.load(open(f"{OUT}/schedule.json"))["rows"]
    items = []
    for p in sorted(glob.glob(f"{WORK}/specs/*.json")):
        sp = json.load(open(p)); s = sp["slug"]; f = sp.get("files", {}) or {}
        d = f"{WORK}/deliver/{s}"
        name = lambda k: f.get(k) if isinstance(f.get(k), str) and f.get(k) != "_unused" else None
        title = TITLES.get(s, s.replace("_", " ").capitalize())
        rows = [r for r in sched if r["content"] and (r["content"].lower()[:18] in title.lower() or title.lower()[:18] in r["content"].lower())]
        posted = next((r for r in rows if r["status"] == "Posted"), None)
        planned = sorted(rows, key=lambda r: r["date"] or "9999")
        items.append(dict(slug=s, title=title, format=SERIES.get(s, "flip" if s.startswith("flip_") else "news"),
                          long=dur(f"{d}/{name('long')}.mp4") if name("long") else None, short=dur(f"{d}/{name('short')}.mp4") if name("short") else None,
                          status=(posted or (planned[0] if planned else {})).get("status") or "Not scheduled",
                          link=(posted or {}).get("link"), planned=planned[0]["date"] if planned else None,
                          recheck=RECHECK.get(s), sources=sp.get("sources", [])))
    json.dump({"items": items}, open(f"{OUT}/library.json", "w"), ensure_ascii=False, indent=1)
    return len(items)


def video_map():
    """YouTube video id -> slug / long|short / format, for the stats API (no credentials in it)."""
    f = f"{WORK}/publish/youtube_log.json"
    if not os.path.exists(f): return 0
    m = {}
    for r in json.load(open(f)):
        if r.get("deleted"): continue
        s = r["slug"]
        m[r["video_id"]] = dict(slug=s, kind=r["fmt"], title=TITLES.get(s, s), format=SERIES.get(s, "flip" if s.startswith("flip_") else "news"))
    json.dump(m, open(f"{OUT}/video_map.json", "w"), indent=1, ensure_ascii=False)
    return len(m)


def stills():
    out = {}
    for fp in sorted(glob.glob(os.path.join(HERE, "site", "img", "*.webp"))):
        b = os.path.basename(fp); fmt = b.split("_")[0]
        kind = "short" if "_short_" in b else "long"
        slug = re.sub(r"_(short|long)_\d+\.webp$", "", b[len(fmt) + 1:])
        out.setdefault(fmt, []).append({"src": "img/" + b, "kind": kind, "slug": slug})
    json.dump(out, open(f"{OUT}/stills.json", "w"), indent=1)


def replay_sample():
    """Real numbers from the 4th ODI capture (NZ innings) to show what the Replay Room can draw."""
    import pandas as pd
    f = f"{WORK}/data/cricinfo/cricinfo_1539440_balls.csv"
    if not os.path.exists(f): return
    df = pd.read_csv(f); L = df[df.wides == 0].copy(); L["fs"] = L.control == 2
    y = L[L.batter == "Will Young"].reset_index(drop=True)
    shots = [dict(x=int(r.wagon_x), y=int(r.wagon_y), r=int(r.bat_runs), fs=bool(r.fs), len=r.pitch_length, shot=r.shot)
             for r in y.itertuples() if r.bat_runs > 0 and (r.wagon_x or r.wagon_y)]
    blocks = [dict(balls=f"{i*25+1}-{min(i*25+25, len(y))}", runs=int(g.bat_runs.sum()), false_shots=int(g.fs.sum()))
              for i, g in y.groupby(y.index // 25)]
    lengths = [dict(length=k.replace("_", " ").title(), balls=int(len(g)), runs=int(g.bat_runs.sum()), false_shots=int(g.fs.sum()))
               for k, g in y.groupby("pitch_length")]
    bowl = L.groupby("bowler").agg(balls=("runs", "size"), runs=("runs", "sum"), wkts=("wicket", "sum"), fs=("fs", "mean")).reset_index()
    bowlers = [dict(bowler=r.bowler, balls=int(r.balls), econ=round(r.runs / r.balls * 6, 2), wkts=int(r.wkts), false_pct=round(r.fs * 100, 1))
               for r in bowl.sort_values("fs", ascending=False).itertuples()]
    phases = [dict(overs=f"{i*10+1}-{i*10+10}", runs=int(g.runs.sum()), wkts=int(g.wicket.sum()), false_pct=round(g.fs.mean() * 100, 1))
              for i, g in L.groupby((L.over_no - 1) // 10)]
    json.dump(dict(match="NZ v India, 4th ODI, Mount Maunganui, 13 Nov 2026: New Zealand innings (333 all out)",
                   source="Captured from ESPNcricinfo ball-by-ball (tools/ttm-capture), cross-checked with Cricbuzz over by over",
                   young=dict(runs=int(y.bat_runs.sum()), balls=len(y), shots=shots, blocks=blocks, lengths=lengths),
                   bowlers=bowlers, phases=phases), open(f"{OUT}/replay_sample.json", "w"), indent=1)


if __name__ == "__main__":
    n = library(); stills(); replay_sample(); vm = video_map()
    print(f"library {n} videos; {vm} uploaded videos mapped; stills; replay sample -> {OUT}")
