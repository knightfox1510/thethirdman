"""Cricsheet access for the audit tools: download the internationals archives and build a one-row-per-match index.
    python3 -m dataops.cricsheet fetch      # downloads tests/odis/t20s (men's and women's) into data/cricsheet/ (gitignored)
The index is only what we HOLD. dataops/audit.py compares it with reference totals from other sources."""
import glob, json, os, subprocess, sys, zipfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CS = os.environ.get("CS_DIR", os.path.join(ROOT, "data", "cricsheet"))
FORMATS = {"tests": "Test", "odis": "ODI", "t20s": "T20I"}


def fetch():
    os.makedirs(CS, exist_ok=True)
    for f in FORMATS:
        z = os.path.join(CS, f + ".zip")
        subprocess.run(["curl", "-sS", "-m", "300", "-o", z, f"https://cricsheet.org/downloads/{f}_json.zip"], check=True)
        os.makedirs(os.path.join(CS, f), exist_ok=True)
        zipfile.ZipFile(z).extractall(os.path.join(CS, f)); os.remove(z)
        print(f, len(glob.glob(os.path.join(CS, f, "*.json"))), "matches")
    subprocess.run(["curl", "-sS", "-m", "120", "-o", os.path.join(CS, "people.csv"), "https://cricsheet.org/register/people.csv"], check=True)


def result(info):
    """('W'|'L'|'T'|'D'|'NR', winner or None) from the match's outcome. A super-over decision is a TIE here (as in ESPNcricinfo's result summaries); `so_winner` is kept separately."""
    o = info.get("outcome", {})
    if "winner" in o: return "WIN", o["winner"]
    r = o.get("result")
    if r == "tie": return "TIE", None
    if r == "draw": return "DRAW", None
    return "NR", None


def matches(gender="male"):
    """Yield (path, info, innings) for every internationals match we hold, sorted by date."""
    out = []
    for fmt, label in FORMATS.items():
        for p in glob.glob(os.path.join(CS, fmt, "*.json")):
            m = json.load(open(p)); i = m["info"]
            if i.get("gender") != gender: continue
            out.append((i["dates"][0], label, p, m))
    for d, label, p, m in sorted(out, key=lambda x: (x[0], x[2])): yield label, p, m


def team_rows(team, gender="male"):
    rows = []
    for label, p, m in matches(gender):
        i = m["info"]
        if team not in i["teams"]: continue
        kind, winner = result(i)
        rows.append({"id": os.path.basename(p)[:-5], "date": i["dates"][0], "fmt": label, "opp": [t for t in i["teams"] if t != team][0], "kind": kind, "winner": winner,
                     "so_winner": i.get("outcome", {}).get("eliminator"), "event": i.get("event", {}).get("name", ""), "venue": i.get("venue", ""),
                     "res": "W" if winner == team else "L" if kind == "WIN" else kind[0] if kind != "NR" else "NR"})
    return rows


if __name__ == "__main__":
    if sys.argv[1:2] == ["fetch"]: fetch()
