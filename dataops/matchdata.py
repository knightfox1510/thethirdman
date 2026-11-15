"""Turn a captured ESPNcricinfo match JSON (data/cricinfo/*.json) into clean tables: one row per match, per team, per player-in-match (playing XI, bench / squad when the playing-XI tab was captured),
per official, per innings, partnership, fall of wickets, DRS review. Everything the capture holds is kept; fields the page does not carry (coaches, support staff) are searched for by name
and listed under `unmapped` so we can see what a given capture really contains.
    python3 -m dataops.matchdata data/cricinfo/nz_ind_4odi.json          # prints the tables' sizes and the first rows
    python3 -m dataops.matchdata --all                                    # writes data/matches/<site>_<id>.json for every capture"""
import glob, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _pg(d):
    for v in d["pages"].values():
        x = isinstance(v, dict) and v.get("props", {}).get("appPageProps", {}).get("data")
        if x and x.get("match"): return x
    return None


def _player(p):
    p = p or {}
    return {"id": p.get("id"), "name": p.get("name") or p.get("longName"), "long_name": p.get("longName"), "role": p.get("playingRoles") or p.get("playingRole"), "batting": p.get("battingStyles"), "bowling": p.get("bowlingStyles"),
            "dob": (p.get("dateOfBirth") or {}) if isinstance(p.get("dateOfBirth"), dict) else p.get("dateOfBirth"), "country_id": (p.get("country") or {}).get("id") if isinstance(p.get("country"), dict) else None}


def find_keys(o, pat, path="", out=None):
    """Every key path whose name matches pat (e.g. coach|staff|support) so a capture can be checked for fields we do not map yet."""
    out = [] if out is None else out
    if isinstance(o, dict):
        for k, v in o.items():
            if re.search(pat, k, re.I) and v not in (None, [], {}, ""): out.append((f"{path}/{k}", type(v).__name__))
            find_keys(v, pat, f"{path}/{k}", out)
    elif isinstance(o, list):
        for v in o[:3]: find_keys(v, pat, path + "[]", out)
    return out


def slim(o):
    """Replace nested player / team objects by their id and name so rows stay flat and readable."""
    out = {}
    for k, v in (o or {}).items():
        if isinstance(v, dict) and "id" in v and ("name" in v or "longName" in v): out[k + "_id"] = v["id"]; out[k + "_name"] = v.get("name") or v.get("longName")
        elif isinstance(v, (dict, list)): continue
        else: out[k] = v
    return out


def tables(d):
    x = _pg(d); m = x["match"]; c = x["content"]; T = {}
    teams = {t["team"]["id"]: t for t in m["teams"]}
    T["match"] = [{"match_id": m["id"], "espn_scribe_id": m.get("scribeId"), "series_id": m["series"]["id"], "series": m["series"].get("longName"), "title": m.get("title"), "format": m.get("format"), "date": m.get("startDate"), "end": m.get("endDate"),
                   "state": m.get("state"), "status": m.get("statusText"), "day_type": m.get("dayType"), "floodlit": m.get("floodlit"), "season": m.get("season"), "winner_team_id": m.get("winnerTeamId"),
                   "result_status": m.get("resultStatus"), "toss_winner_team_id": m.get("tossWinnerTeamId"), "toss_choice": m.get("tossWinnerChoice"), "scheduled_overs": m.get("scheduledOvers"),
                   "ground_id": m["ground"]["id"], "ground": m["ground"].get("name"), "town": (m["ground"].get("town") or {}).get("name"), "country": (m["ground"].get("country") or {}).get("name"), "capacity": m["ground"].get("capacity"),
                   "live_commentator": m.get("liveCommentator"), "has_commentary": m.get("hasCommentary"), "has_match_players": m.get("hasMatchPlayers")}]
    T["team"] = [{"match_id": m["id"], "team_id": t["team"]["id"], "team": t["team"].get("name"), "abbr": t["team"].get("abbreviation"), "is_home": t.get("isHome"), "score": t.get("score"), "captain": _player(t.get("captain")).get("name"),
                  "captain_id": (t.get("captain") or {}).get("id")} for t in m["teams"]]
    T["official"] = [{"match_id": m["id"], "role": role, **{k: v for k, v in _player(o.get("player")).items() if k in ("id", "name")}} for role, key in (("umpire", "umpires"), ("tv_umpire", "tvUmpires"), ("reserve_umpire", "reserveUmpires"), ("referee", "matchReferees")) for o in (m.get(key) or [])]
    T["innings"] = [{"match_id": m["id"], "inning": i["inningNumber"], "team_id": i["team"]["id"], "runs": i["runs"], "wickets": i["wickets"], "overs": i["overs"], "balls": i["balls"], "extras": i["extras"], "wides": i["wides"], "noballs": i["noballs"],
                     "byes": i["byes"], "legbyes": i["legbyes"], "target": i.get("target"), "fours": i["fours"], "sixes": i["sixes"], "catches_dropped": i.get("catchesDropped")} for i in c["innings"]]
    xi = {}                                                                                       # playing XI: everyone who batted, bowled or is listed in the match players block
    for i in c["innings"]:
        for b in i["inningBatsmen"]: xi[(b["player"]["id"], i["team"]["id"])] = {"role": "batted", **_player(b["player"]), "team_id": i["team"]["id"]}
        for bw in i["inningBowlers"]:
            opp = next((t["team"]["id"] for t in m["teams"] if t["team"]["id"] != i["team"]["id"]), None); xi.setdefault((bw["player"]["id"], opp), {"role": "bowled", **_player(bw["player"]), "team_id": opp})
    T["player_in_match"] = [{"match_id": m["id"], "status": "playing", **v} for v in xi.values()]
    mp = c.get("matchPlayers")
    if mp:                                                                                      # playing-XI tab captured: XI, bench / squad members, with roles
        def walk(o, ctx=None):
            if isinstance(o, dict):
                if "player" in o and isinstance(o["player"], dict): T["player_in_match"].append({"match_id": m["id"], "status": o.get("isSubstitute") and "substitute" or o.get("playerRoleType") or "squad", **_player(o["player"]), "raw": {k: v for k, v in o.items() if k != "player"}})
                for v in o.values(): walk(v)
            elif isinstance(o, list):
                for v in o: walk(v)
        walk(mp)
    T["partnership"] = [{"match_id": m["id"], "inning": i["inningNumber"], **slim(p)} for i in c["innings"] for p in i["inningPartnerships"] if isinstance(p, dict)]
    T["fall_of_wicket"] = [{"match_id": m["id"], "inning": i["inningNumber"], **slim(w)} for i in c["innings"] for w in i["inningFallOfWickets"] if isinstance(w, dict)]
    T["drs_review"] = [{"match_id": m["id"], "inning": i["inningNumber"], **slim(w)} for i in c["innings"] for w in i["inningDRSReviews"] if isinstance(w, dict)]
    T["unmapped"] = [{"match_id": m["id"], "path": p, "type": t} for p, t in find_keys(d["pages"], r"coach|staff|support|physio|analyst|squad|substitut|replacement|debut")]
    return T


if __name__ == "__main__":
    if sys.argv[1] == "--all":
        os.makedirs(f"{ROOT}/data/matches", exist_ok=True)
        for p in sorted(glob.glob(f"{ROOT}/data/cricinfo/*.json")):
            d = json.load(open(p, encoding="utf-8"))
            if "match_id" not in d or not _pg(d): continue
            json.dump(tables(d), open(f"{ROOT}/data/matches/cricinfo_{d['match_id']}.json", "w"), indent=1, ensure_ascii=False, default=str); print("wrote", d["match_id"])
    else:
        T = tables(json.load(open(sys.argv[1], encoding="utf-8")))
        for k, v in T.items(): print(f"{k:16s} {len(v):3d}", json.dumps(v[0], default=str)[:230] if v else "")
