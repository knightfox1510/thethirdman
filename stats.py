"""Ball-level table for IPL (2013-2026) and India T20Is from the Sportmonks cache, plus helpers.
Every row is one delivery."""
import glob, json, os, re
import pandas as pd

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
SPIN = ("orthodox", "break", "spin", "chinaman", "googly", "legbreak", "offbreak")
STYLE_FIX = {"Michael Bracewell": "right-arm-offbreak"}


def players():
    P = {}
    for p in glob.glob(f"{DATA}/players/*.json"):
        d = json.load(open(p)); P[d["id"]] = d
    return P


def bowler_kind(style):
    if not style: return "unknown"
    s = style.lower()
    if "orthodox" in s or "chinaman" in s: return "left-arm spin"
    if "offbreak" in s or "off-break" in s: return "off-spin"
    if "legbreak" in s or "googly" in s: return "leg-spin"
    if "left" in s: return "left-arm pace"
    return "right-arm pace"


def _rows(d, comp, season, P):
    venue = (d.get("venue") or {}).get("name")
    teams = {d["localteam"]["id"]: d["localteam"]["name"], d["visitorteam"]["id"]: d["visitorteam"]["name"]} if d.get("localteam") else {}
    for b in (d.get("balls") or {}).get("data", []) if isinstance(d.get("balls"), dict) else (d.get("balls") or []):
        sc = b.get("score") or {}
        bat = P.get(b.get("batsman_id")) or (b.get("batsman") if isinstance(b.get("batsman"), dict) else {}) or {}
        bowl = P.get(b.get("bowler_id")) or (b.get("bowler") if isinstance(b.get("bowler"), dict) else {}) or {}
        bstyle = bowl.get("bowlingstyle") or STYLE_FIX.get(bowl.get("fullname"))
        bat_team = (b.get("team") or {}).get("name")
        bowl_team = next((v for k, v in teams.items() if v != bat_team), None)
        # feed encoding: wides have ball=False; "runs" includes wide/no-ball penalties; byes/leg byes are separate fields
        r_bat = ((sc.get("runs") or 0) - (sc.get("noball_runs") or 0)) if sc.get("ball") else 0
        yield dict(comp=comp, season=season, fixture=d["id"], date=(d.get("starting_at") or "")[:10], venue=venue,
                   bat_team=bat_team, bowl_team=bowl_team, inning=b.get("scoreboard"), ball=b.get("ball"),
                   over=int(b.get("ball") or 0), batter=bat.get("fullname"), batter_id=b.get("batsman_id"),
                   bat_hand=bat.get("battingstyle"), bowler=bowl.get("fullname"), bowler_id=b.get("bowler_id"),
                   bowl_style=bstyle, bowl_kind=bowler_kind(bstyle), runs=sc.get("runs") or 0, bat_runs=max(r_bat, 0),
                   extras_b=(sc.get("bye") or 0) + (sc.get("leg_bye") or 0),
                   legal=bool(sc.get("ball")), legal_bowl=bool(sc.get("ball")) and not sc.get("noball"), four=bool(sc.get("four")), six=bool(sc.get("six")),
                   wicket=bool(sc.get("is_wicket")), out_id=b.get("batsmanout_id"), dismissal=sc.get("name"))


def ipl(cache=True):
    pq = f"{DATA}/ipl_balls.pkl"
    if cache and os.path.exists(pq): return pd.read_pickle(pq)
    P = players(); rows = []
    seasons = {}
    for sp in glob.glob(f"{DATA}/ipl/season_*.json"):
        nm = re.search(r"season_(\d+)", sp).group(1)
        for f in json.load(open(sp)): seasons[f["id"]] = int(nm)
    for fp in glob.glob(f"{DATA}/ipl/fx_*.json"):
        d = json.load(open(fp)); rows += list(_rows(d, "IPL", seasons.get(d["id"]), P))
    df = pd.DataFrame(rows); df = _derive(df); df.to_pickle(pq); return df


def t20i(ids_file="abhishek_t20i_ids.json"):
    P = players(); rows = []
    for fp in glob.glob(f"{DATA}/fx_*.json"):
        d = json.load(open(fp)); yr = int((d.get("starting_at") or "0000")[:4])
        rows += list(_rows(d, "T20I", yr, P))
    return _derive(pd.DataFrame(rows))


def _derive(df):
    df["phase"] = pd.cut(df["over"], [-1, 5, 14, 19], labels=["powerplay", "middle", "death"]).astype(str)
    df["dot"] = df["legal_bowl"] & (df["runs"] == 0) & (df["extras_b"] == 0)
    df["team_runs"] = df["runs"] + df["extras_b"]
    # the dismissed batter is the striker unless out_id says otherwise (run outs)
    df["striker_out"] = df["wicket"] & ((df["out_id"].isna()) | (df["out_id"] == df["batter_id"]))
    return df


def batting(df, by):
    g = df.groupby(by)
    out = pd.DataFrame({"runs": g["bat_runs"].sum(), "balls": g["legal"].sum(), "outs": g["striker_out"].sum(),
                        "fours": g["four"].sum(), "sixes": g["six"].sum(), "dots": g["dot"].sum()})
    out["sr"] = 100 * out["runs"] / out["balls"].clip(lower=1)
    out["avg"] = out["runs"] / out["outs"].clip(lower=1)
    out["dot%"] = 100 * out["dots"] / out["balls"].clip(lower=1)
    out["bpd"] = out["balls"] / out["outs"].clip(lower=1)
    return out


def bowling(df, by):
    g = df.groupby(by)
    out = pd.DataFrame({"runs": g["runs"].sum(), "balls": g["legal_bowl"].sum(), "wkts": g["striker_out"].sum()})
    out["econ"] = 6 * out["runs"] / out["balls"].clip(lower=1)
    out["sr"] = out["balls"] / out["wkts"].clip(lower=1)
    return out
