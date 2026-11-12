"""Data for the "flip" Shorts: a benchmark player vs challengers at the same point in their careers.
    python3 analysis/flips.py            # prints every figure used
Sources: Sportmonks IPL fixtures + line-ups (captains), Cricsheet men's Tests and T20Is (cricsheet.org, ODC-BY)."""
import glob, json, os, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CS = os.path.join(ROOT, "data", "cricsheet")
NOT_BOWLER = {"run out", "retired hurt", "retired out", "obstructing the field", "retired not out"}


# ---------------------------------------------------------------- IPL captains
def mi_captains(team="Mumbai Indians"):
    rows = []
    for f in glob.glob(f"{ROOT}/data/ipl/fx_*.json"):
        d = json.load(open(f))
        teams = {d["localteam"]["id"]: d["localteam"]["name"], d["visitorteam"]["id"]: d["visitorteam"]["name"]}
        tid = next((k for k, v in teams.items() if v == team), None)
        if tid is None: continue
        lp = f"{ROOT}/data/ipl/lineup_{d['id']}.json"
        if not os.path.exists(lp): continue
        cap = next((p["name"] for p in json.load(open(lp)) if p.get("team_id") == tid and p.get("captain")), None)
        if d.get("draw_noresult") or not d.get("winner_team_id"): continue   # no result: left out of win %
        rows.append((d["starting_at"], cap, d["winner_team_id"] == tid))
    rows.sort()
    by = collections.defaultdict(list)
    for _, cap, won in rows: by[cap].append(won)
    return by


# ---------------------------------------------------------------- Cricsheet helpers
def matches(kind):
    for f in glob.glob(f"{CS}/{kind}/*.json"):
        d = json.load(open(f))
        yield d["info"]["dates"][0], d


def test_bowling_by_match(names):
    """{bowler: [(date, runs conceded, wickets), ...]} for every Test they played (0/0 if they didn't bowl)."""
    out = {n: [] for n in names}
    for date, d in sorted(matches("test"), key=lambda x: x[0]):
        played = {p for ps in d["info"]["players"].values() for p in ps}
        r = collections.Counter(); w = collections.Counter()
        for inn in d.get("innings", []):
            for ov in inn.get("overs", []):
                for dl in ov["deliveries"]:
                    b = dl["bowler"]
                    if b not in out: continue
                    ex = dl.get("extras", {})
                    r[b] += dl["runs"]["batter"] + ex.get("wides", 0) + ex.get("noballs", 0)
                    w[b] += sum(1 for x in dl.get("wickets", []) if x["kind"] not in NOT_BOWLER)
        for n in out:
            if n in played: out[n].append((date, r[n], w[n]))
    return out


def test_batting_by_match(names):
    out = {n: [] for n in names}
    for date, d in sorted(matches("test"), key=lambda x: x[0]):
        played = {p for ps in d["info"]["players"].values() for p in ps}
        r = collections.Counter()
        for inn in d.get("innings", []):
            for ov in inn.get("overs", []):
                for dl in ov["deliveries"]:
                    if dl["batter"] in out: r[dl["batter"]] += dl["runs"]["batter"]
        for n in out:
            if n in played: out[n].append((date, r[n]))
    return out


def t20i_opening_innings(names):
    """{batter: [(date, runs, balls faced), ...]} for T20I innings in which they opened (one of the first two to bat)."""
    out = {n: [] for n in names}
    for date, d in sorted(matches("t20i"), key=lambda x: x[0]):
        for inn in d.get("innings", []):
            order, r, bf = [], collections.Counter(), collections.Counter()
            for ov in inn.get("overs", []):
                for dl in ov["deliveries"]:
                    for p in (dl["batter"], dl["non_striker"]):
                        if p not in order: order.append(p)
                    r[dl["batter"]] += dl["runs"]["batter"]
                    if "wides" not in dl.get("extras", {}): bf[dl["batter"]] += 1
            for n in out:
                if n in order[:2]: out[n].append((date, r[n], bf[n]))
    return out


def avg(rw): r = sum(x[1] for x in rw); w = sum(x[2] for x in rw); return r / w if w else float("nan"), w


if __name__ == "__main__":
    print("== MI captains (win % of decided matches, IPL 2013-2026)")
    by = mi_captains(); rohit = by.get("Rohit Sharma", [])
    for cap, res in sorted(by.items(), key=lambda x: -len(x[1])):
        n = len(res); rr = rohit[:n]
        print(f"  {cap}: {sum(res)}/{n} = {100 * sum(res) / n:.1f}%  | Rohit after {n}: {100 * sum(rr) / len(rr):.1f}%")

    print("== Fast bowlers' Test average after Bumrah's number of Tests")
    PACE = ["JJ Bumrah", "PJ Cummins", "MA Starc", "K Rabada", "JR Hazlewood", "SCJ Broad", "TG Southee", "TA Boult", "Mohammed Shami",
            "Shaheen Shah Afridi", "MJ Henry", "OE Robinson", "MA Wood"]
    tb = test_bowling_by_match(PACE); n_b = len(tb["JJ Bumrah"])
    print(f"  Bumrah: {n_b} Tests in the data, avg {avg(tb['JJ Bumrah'])[0]:.2f} ({avg(tb['JJ Bumrah'])[1]} wkts)")
    for p in PACE[1:]:
        x = tb[p]
        if len(x) >= n_b: a, w = avg(x[:n_b]); print(f"  {p}: first Test {x[0][0]}, avg after {n_b} Tests {a:.2f} ({w} wkts)")
        else: print(f"  {p}: only {len(x)} Tests")

    print("== Test runs after the same number of Tests as each challenger, vs Joe Root")
    BAT = ["JE Root", "SPD Smith", "V Kohli", "KS Williamson", "Babar Azam", "M Labuschagne", "HC Brook", "YBK Jaiswal", "Shubman Gill", "TM Head"]
    tt = test_batting_by_match(BAT); root = tt["JE Root"]
    print(f"  Root: {len(root)} Tests, {sum(x[1] for x in root)} runs, debut {root[0][0]}")
    for p in BAT[1:]:
        x = tt[p]; n = len(x)
        print(f"  {p}: {n} Tests, {sum(r for _, r in x)} runs (debut {x[0][0] if x else '-'}) | Root after {n}: {sum(r for _, r in root[:n])}")

    print("== T20I strike rate as an opener, after Abhishek Sharma's number of opening innings")
    OPEN = ["Abhishek Sharma", "PD Salt", "TM Head", "JC Buttler", "RG Sharma", "DA Warner", "Babar Azam", "Mohammad Rizwan", "Q de Kock",
            "YBK Jaiswal", "FH Allen", "TL Seifert", "SV Samson", "Sahibzada Farhan", "Ishan Kishan"]
    oi = t20i_opening_innings(OPEN); n_a = len(oi["Abhishek Sharma"])
    sr = lambda x: 100 * sum(i[1] for i in x) / max(1, sum(i[2] for i in x))
    print(f"  Abhishek: {n_a} opening innings, SR {sr(oi['Abhishek Sharma']):.1f}, last {oi['Abhishek Sharma'][-1][0] if n_a else '-'}")
    for p in OPEN[1:]:
        x = oi[p]
        if len(x) >= n_a: print(f"  {p}: SR after first {n_a} opening innings {sr(x[:n_a]):.1f} (first {x[0][0]})")
        else: print(f"  {p}: only {len(x)} opening innings")
