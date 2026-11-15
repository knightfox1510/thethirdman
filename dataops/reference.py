"""Reference totals from sources that are NOT Cricsheet, parsed from raw Wikipedia wikitext (which cites ESPNcricinfo's results summaries / player pages).
    python3 -m dataops.reference team India            # all-time Test / ODI / T20I totals (won, lost, tied, tie+win, NR...) with the 'correct as of' match
    python3 -m dataops.reference player "Virat Kohli"  # career figures from the infobox
Wikipedia is Tier C (secondary): these numbers cross-check our data and claims, and each carries its 'as of' text."""
import json, os, re, sys, urllib.parse, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = {"User-Agent": "TheThirdManResearch/1.0 (cricket analysis)"}
COLS = {"Test": ["matches", "won", "lost", "tied", "drawn"], "ODI": ["matches", "won", "lost", "tied", "no_result"],
        "T20I": ["matches", "won", "lost", "tied", "tie_win", "tie_loss", "no_result"]}


def raw(title):
    url = "https://en.wikipedia.org/w/index.php?title=" + urllib.parse.quote(title.replace(" ", "_")) + "&action=raw"
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read().decode("utf-8")


def team_totals(team="India"):
    out = {}
    for fmt in ("Test", "ODI", "T20I"):
        t = raw(f"Template:{team} {fmt} cricket records by opponent"); lines = t.splitlines(); tot = None
        for k, ln in enumerate(lines):
            if "'''Total'''" in ln:
                cand = ln if ln.lstrip().startswith("|'''") else (lines[k + 1] if k + 1 < len(lines) else "")
                tot = [re.sub(r"[^\d.]", "", x) for x in re.findall(r"'''([^']+)'''", cand)]
                break
        asof = re.search(r"correct as of (.+?)''", t)
        asof = re.sub(r"\{\{[^}]*\}\}|\[\[|\]\]|<ref.*", "", asof.group(1)).strip() if asof else ""
        cols = COLS[fmt]
        out[fmt] = {"total": dict(zip(cols, map(int, tot[:len(cols)]))) if tot else None, "as_of": asof,
                    "source": f"https://en.wikipedia.org/wiki/Template:{team.replace(' ', '_')}_{fmt}_cricket_records_by_opponent (cites ESPNcricinfo results summaries)"}
    return out


CODES = {"AFG": "Afghanistan", "AUS": "Australia", "BAN": "Bangladesh", "ENG": "England", "IRE": "Ireland", "NZL": "New Zealand", "PAK": "Pakistan", "RSA": "South Africa", "SRI": "Sri Lanka",
         "SL": "Sri Lanka", "WIN": "West Indies", "WI": "West Indies", "ZIM": "Zimbabwe", "UAE": "United Arab Emirates", "NED": "Netherlands", "SCO": "Scotland", "NAM": "Namibia", "OMA": "Oman",
         "USA": "United States of America", "CAN": "Canada", "HK": "Hong Kong", "NEP": "Nepal", "PNG": "Papua New Guinea", "KEN": "Kenya", "BER": "Bermuda", "EAF": "East Africa", "MAS": "Malaysia",
         "SIN": "Singapore", "JPN": "Japan", "ITA": "Italy", "BHR": "Bahrain", "KUW": "Kuwait", "QAT": "Qatar", "SAU": "Saudi Arabia", "JER": "Jersey", "GER": "Germany", "ICC": "ICC World XI", "ASIA": "Asia XI", "AFR": "Africa XI", "MLT": "Malta"}


def team_by_opponent(team="India"):
    """{fmt: {opponent name: {matches, won, lost, ...}}} from the same templates (rows keyed by the {{cr|CODE}} flag template)."""
    out = {}
    for fmt in ("Test", "ODI", "T20I"):
        t = raw(f"Template:{team} {fmt} cricket records by opponent"); lines = t.splitlines(); rows = {}
        for k, ln in enumerate(lines):
            m = re.search(r"\{\{cr\|([A-Za-z]+)", ln)
            if m and ln.lstrip().startswith("!") and k + 1 < len(lines):
                nums = [re.sub(r"[^\d.]", "", x) for x in lines[k + 1].strip("| ").split("||")]
                if nums and nums[0].isdigit(): rows[CODES.get(m.group(1), m.group(1))] = dict(zip(COLS[fmt], [int(x) for x in nums[:len(COLS[fmt])] if x.replace('.', '').isdigit()]))
        out[fmt] = rows
    return out


def player_infobox(title):
    t = raw(title); out = {}
    for k, v in re.findall(r"^\|\s*([a-z0-9/ _-]+?)\s*=\s*(.*)$", t, flags=re.M):
        if re.search(r"(matches|runs|bat avg|100s/50s|top score|wickets|bowl avg|catches/stumpings|deliveries)\d?$", k) or k in ("fullname", "birth_date"):
            out[k] = re.sub(r"<ref.*|\{\{.*?\}\}|\[\[|\]\]", "", v).strip()
    return out


if __name__ == "__main__":
    if sys.argv[1] == "team":
        tm = sys.argv[2]; r = team_totals(tm); os.makedirs(f"{ROOT}/data/reference", exist_ok=True)
        json.dump(r, open(f"{ROOT}/data/reference/{tm.lower()}_by_opponent.json", "w"), indent=1); print(json.dumps(r, indent=1))
    else:
        print(json.dumps(player_infobox(sys.argv[2]), indent=1))
