"""The channel's series registry: one place that says which series, episode and name every video has.
Drive layout (publish/drive.py):  The Third Man / Series / <NN Series> / <EpNN - Title> [posted]  (folder property slug=<slug>)
File names (spec "files", applied by voice_lint.fix_spec and publish/drive_migrate.py):
    <Series>_Ep<NN>_<Subject>_Long.mp4 (+ .srt, _thumbnail.jpg, .chapters.txt),  <...>_Short_9x16.mp4 (+ .srt, _cover.jpg),  <...>_Short_9x16_IG.mp4 (Instagram version)
Add every new video here (slug -> series id, episode label, subject) before its first build."""
import re

SERIES = [  # (id, folder number, name, file prefix)
    ("myth", 1, "Myth or Data", "Myth_or_Data"),
    ("replay", 2, "The Replay Room", "Replay_Room"),
    ("tactics", 3, "Tactics Board", "Tactics_Board"),
    ("lab", 4, "The Lab", "The_Lab"),
    ("statcheck", 5, "Stat Check", "Stat_Check"),
    ("whatif", 6, "What If", "What_If"),
    ("rising", 7, "Rising Star", "Rising_Star"),
    ("flip", 8, "Flip", "Flip"),
    ("data", 9, "Data Stories", "Data_Story"),
    ("channel", 10, "Channel", "Channel"),
]
# slug -> (series id, episode label, subject as shown in the Drive folder name)
EPISODES = {
    "myth_ep1_kohli_knockouts": ("myth", "01", "Does Kohli Fail in Knockouts"),
    "myth_ep2_kohli_reinvention": ("myth", "02", "Is Kohli Too Slow for T20"),
    "myth_ep3_aaryavir": ("myth", "03", "Aaryavir Sehwag, Like Father Like Son"),
    "replay_4odi": ("replay", "01", "India vs New Zealand 4th ODI"),
    "replay_4odi_young": ("replay", "01b", "4th ODI extra, Will Young Two Innings in One"),
    "replay_4odi_dots": ("replay", "01c", "4th ODI extra, India 74 Percent Dot Balls"),
    "henry_6balls": ("replay", "01d", "4th ODI extra, Matt Henry 3 Wickets in 6 Balls"),
    "replay_u19_final": ("replay", "02", "India vs Pakistan U19 Asia Cup Final"),
    "santner_problem": ("tactics", "01", "The Santner Problem, NZ v IND T20Is"),
    "abhishek_plan": ("tactics", "02", "How to Bowl to Abhishek Sharma"),
    "wellington_odi": ("tactics", "03", "Wellington ODI Breakdown"),
    "nz_test_preview": ("tactics", "04", "India in New Zealand Test Preview"),
    "bay_oval_new_ball": ("tactics", "05", "Surviving the New Ball at Bay Oval"),
    "lab_ep1_abhishek_twin": ("lab", "01", "Abhishek Sharma's Statistical Twin"),
    "lab_ep2_bumrah_twin": ("lab", "02", "Bumrah's Bowling Twin"),
    "stat_check_bumrah_rashid": ("statcheck", "01", "Bumrah or Rashid"),
    "bradman_ipl": ("whatif", "01", "Bradman in the IPL"),
    "bumrah_vs_90s": ("whatif", "02", "Bumrah vs 90s Sachin and Lara"),
    "dhoni_captain": ("whatif", "03", "Dhoni Never Became Captain"),
    "sachin_t20": ("whatif", "04", "Sachin in the T20 Era"),
    "aaryavir_sehwag": ("rising", "01", "Aaryavir Sehwag 160"),
    "flip_abhishek_openers": ("flip", "01", "Abhishek Sharma vs T20I Openers"),
    "flip_bumrah_52_tests": ("flip", "02", "Bumrah vs Fast Bowlers After 52 Tests"),
    "flip_mi_captains": ("flip", "03", "Every MI Captain vs Rohit Sharma"),
    "flip_root_same_point": ("flip", "04", "Joe Root vs Everyone at the Same Point"),
    "anchor": ("data", "01", "Is the T20 Anchor Dead"),
    "powerplay_revolution": ("data", "02", "The Powerplay Revolution"),
    "ipl_batting_evolution": ("data", "03", "How the IPL Changed T20 Batting"),
    "two_hundred": ("data", "04", "Why 200 Is the New 160"),
    "india_160": ("data", "05", "India's Missing 160"),
    "bumrah_economy": ("data", "06", "The Bumrah Paradox"),
    "death_kings": ("data", "07", "The Death Overs Kings"),
    "rcb_back_to_back": ("data", "08", "How RCB Won Back to Back"),
    "hardik_arshdeep": ("data", "09", "Hardik for Arshdeep Trade"),
    "kohli_2000_nz": ("data", "10", "Kohli vs New Zealand Milestone Watch"),
    "channel_trailer": ("channel", "00", "Welcome to The Third Man"),
}
_S = {s[0]: s for s in SERIES}


def _ascii(s): return re.sub(r"_+", "_", re.sub(r"[^A-Za-z0-9]+", "_", s)).strip("_")


def info(slug):
    """-> dict(series_dir, series_name, ep, subject, folder, base) or None for an unregistered slug."""
    e = EPISODES.get(slug)
    if not e: return None
    sid, ep, subject = e; _, num, name, prefix = _S[sid]
    return {"series_dir": f"{num:02d} {name}", "series_name": name, "ep": ep, "subject": subject, "sid": sid,
            "folder": f"Ep{ep} - {subject}", "base": f"{prefix}_Ep{ep}_{_ascii(subject)}"}


def file_names(slug):
    i = info(slug)
    return {"long": i["base"] + "_Long", "short": i["base"] + "_Short_9x16"} if i else None


def apply_names(spec):
    """Point a spec's output file names at the series naming (formats that are "_unused" or absent stay as they are)."""
    nm = file_names(spec.get("slug"))
    if not nm: return spec
    f = spec.get("files") or {}
    for k in ("long", "short"):
        if f.get(k) and "unused" not in f[k].lower(): f[k] = nm[k]
    return spec
