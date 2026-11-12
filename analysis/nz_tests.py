"""Figures for the India-in-New-Zealand Test preview (Cricsheet men's Test data, data/cricsheet/test).
Bowling type is not in Cricsheet: spinners are tagged by name below (everyone else counts as pace)."""
import json, glob, os, collections

D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "cricsheet", "test")
NZ_CITIES = {"Wellington", "Christchurch", "Hamilton", "Auckland", "Napier", "Dunedin", "Mount Maunganui", "Nelson"}
IND_CITIES = {"Mumbai", "Chennai", "Kolkata", "Delhi", "Bangalore", "Bengaluru", "Ahmedabad", "Nagpur", "Mohali", "Chandigarh",
              "Kanpur", "Hyderabad", "Rajkot", "Visakhapatnam", "Pune", "Ranchi", "Indore", "Dharamsala", "Lucknow", "Guwahati", "Cuttack"}
SPIN = {"DL Vettori", "MJ Santner", "JS Patel", "AY Patel", "IS Sodhi", "WER Somerville", "TD Astle", "MD Craig", "MG Bracewell",
        "GD Phillips", "R Ravindra", "KS Williamson", "TG Nethula", "BP Martin",
        "R Ashwin", "RA Jadeja", "A Mishra", "PP Ojha", "Harbhajan Singh", "Kuldeep Yadav", "AR Patel", "Washington Sundar", "A Kumble",
        "NM Lyon", "SK Warne", "SCG MacGill", "TR Murphy", "SNJ O'Keefe", "MJ Swepson", "M Kuhnemann",
        "M Muralitharan", "HMRKB Herath", "MDK Perera", "L Embuldeniya", "PM Jayasuriya", "RTM Mendis",
        "MS Panesar", "GP Swann", "MJ Leach", "MM Ali", "Shoaib Bashir", "TW Hartley", "Rehan Ahmed", "AU Rashid",
        "KA Maharaj", "SR Harmer", "T Shamsi", "DL Piedt", "N Boje", "PL Harris", "JL Ontong",
        "D Bishoo", "JA Warrican", "RL Chase", "K Pierre", "G Motie", "SJ Benn",
        "Danish Kaneria", "Abdur Rehman", "Yasir Shah", "Saeed Ajmal", "Bilal Asif", "Sajid Khan", "Noman Ali", "Abrar Ahmed",
        "Shakib Al Hasan", "Mehedi Hasan Miraz", "Taijul Islam", "Nayeem Hasan", "Abdur Razzak", "Enamul Haque", "Mohammad Rafique",
        "Rashid Khan", "Zahir Khan"}


def matches(cities):
    for f in sorted(glob.glob(f"{D}/*.json")):
        d = json.load(open(f)); i = d["info"]
        if i.get("city") in cities: yield d


def wickets(d):
    for inn in d.get("innings", []):
        for ov in inn.get("overs", []):
            for dl in ov["deliveries"]:
                for w in dl.get("wickets", []):
                    if w["kind"] not in ("run out", "retired hurt", "retired out", "obstructing the field"):
                        yield inn["team"], dl["bowler"]


def pace_share(cities, since="2010"):
    c = collections.Counter()
    for d in matches(cities):
        if d["info"]["dates"][0] < since: continue
        for _, b in wickets(d): c["spin" if b in SPIN else "pace"] += 1
    return 100 * c["pace"] / sum(c.values()), sum(c.values())


if __name__ == "__main__":
    print("== India Tests in New Zealand (Cricsheet coverage)")
    for d in matches(NZ_CITIES):
        i = d["info"]
        if "India" in i["teams"]: print(" ", i["dates"][0], i["venue"], i.get("outcome"))
    print("== Share of wickets taken by pace, 2010 onwards")
    for nm, cities in [("Tests in New Zealand", NZ_CITIES), ("Tests in India", IND_CITIES)]:
        p, n = pace_share(cities); print(f"  {nm}: {p:.1f}% of {n} wickets")
    print("== Runs per wicket for India (all Tests in NZ in the data vs home, 2010 onwards)")
    for nm, cities in [("in NZ", NZ_CITIES), ("in India", IND_CITIES)]:
        r = w = 0
        for d in matches(cities):
            if d["info"]["dates"][0] < "2009" or "India" not in d["info"]["teams"]: continue
            for inn in d.get("innings", []):
                if inn["team"] != "India": continue
                for ov in inn.get("overs", []):
                    for dl in ov["deliveries"]:
                        r += dl["runs"]["total"]; w += len(dl.get("wickets", []))
        print(f"  India {nm}: {r / max(1, w):.1f} runs per wicket ({w} wickets)")
    print("== NZ bowlers' wickets v India in Tests (all venues)")
    c = collections.Counter()
    for d in matches(NZ_CITIES | IND_CITIES | {"Southampton"}):
        if set(d["info"]["teams"]) != {"India", "New Zealand"}: continue
        for team, b in wickets(d):
            if team == "India": c[b] += 1
    print(" ", c.most_common(8))
    print("== Basin Reserve, Wellington, since 2010: first-innings average, result by batting first/second")
    fi, res = [], collections.Counter()
    for d in matches({"Wellington"}):
        i = d["info"]
        if i["dates"][0] < "2010" or not d.get("innings"): continue
        first = d["innings"][0]; fi.append(sum(dl["runs"]["total"] for ov in first.get("overs", []) for dl in ov["deliveries"]))
        o = i.get("outcome", {})
        if "winner" in o: res["bat first won" if o["winner"] == first["team"] else "bat second won"] += 1
        else: res["draw/other"] += 1
    print(f"  {len(fi)} Tests, avg 1st-innings {sum(fi) / len(fi):.0f}; {dict(res)}")
    print("== Current India squad members who have played a Test in New Zealand")
    squad = ["YBK Jaiswal", "KL Rahul", "D Padikkal", "B Sai Sudharsan", "RR Pant", "DC Jurel", "RA Jadeja", "Washington Sundar",
             "Nithish Kumar Reddy", "JJ Bumrah", "Mohammed Siraj", "Akash Deep", "M Prasidh Krishna", "AR Kamboj", "Kuldeep Yadav", "Shubman Gill"]
    played = set()
    for d in matches(NZ_CITIES):
        if "India" in d["info"]["teams"]: played |= set(d["info"]["players"]["India"])
    print("  ", sorted(p for p in squad if p in played), f"({sum(p in played for p in squad)} of {len(squad)})")
    print("  all India players in NZ Tests:", sorted(played))
