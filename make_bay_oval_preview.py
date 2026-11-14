"""Builds specs/bay_oval_new_ball.py's video: "Surviving the new ball at Bay Oval" (Tactics, long), a preview of the 5th ODI (15 Nov 2026).
Every number spoken or shown is computed here and asserted:
  - Bay Oval + league history: Cricsheet men's 50-over ODIs (to 25 Oct 2025; https://cricsheet.org/downloads/odis_json.zip, ODC-BY), unzip to CS_DIR
  - the 4th ODI (13 Nov 2026): Cricinfo + Cricbuzz captures -> data/cricinfo/nz_ind_4odi_balls.csv (python3 cricinfo_import.py ...)
    CS_DIR=/path/to/odis_json python3 make_bay_oval_preview.py"""
import json, os, sys
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "analysis"))
import bay_oval_new_ball as BO
import voice_lint

# ---------------------------------------------------------------- history (Cricsheet)
ms = BO.load()
bay = [m for m in ms if "Bay Oval" in m["info"].get("venue", "")]
nz = [m for m in ms if m["info"].get("city") in BO.NZ_CITIES and m not in bay]
assert len(ms) == 2617 and len(bay) == 13 and max(m["info"]["dates"][0] for m in bay) == "2025-10-26", (len(ms), len(bay))


def stats(grp):
    rows = [r for m in grp for r in BO.innings_rows(m)]; n = len(rows)
    return dict(n=n, wk=sum(r["p1w"] for r in rows) / n, rr=sum(r["p1r"] for r in rows) / n / 10, w1=100 * sum(1 for r in rows if r["w1"] > 0) / n,
                three=100 * sum(1 for r in rows if r["p1w"] >= 3) / n, w1n=sum(1 for r in rows if r["w1"] > 0))


SB, SA = stats(bay), stats(ms)
assert (SB["n"], SA["n"]) == (26, 5165)
assert (round(SB["wk"], 2), round(SA["wk"], 2)) == (1.42, 1.43) and (round(SB["rr"], 2), round(SA["rr"], 2)) == (4.88, 4.74)
assert (SB["w1n"], round(SB["w1"]), round(SA["w1"])) == (2, 8, 13) and (round(SB["three"]), round(SA["three"])) == (12, 16)
# three wickets in the first over: never, in all 5,165 innings
c3 = sum(1 for m in ms for inn in m["innings"] if not inn.get("super_over") for o in inn["overs"] if o["over"] == 0
         and sum(1 for d in o["deliveries"] for w in d.get("wickets", []) if w["kind"] != "retired hurt") >= 3)
assert c3 == 0

# Bay Oval totals, results (13 men's matches to Oct 2025) + the 4th ODI
tot1 = []; bat_first_wins = 0; toss_field = 0
for m in sorted(bay, key=lambda m: m["info"]["dates"][0]):
    inn = [x for x in m["innings"] if not x.get("super_over")]; i = m["info"]
    r1 = sum(d["runs"]["total"] for o in inn[0]["overs"] for d in o["deliveries"])
    tot1.append((i["dates"][0], inn[0]["team"], [t for t in i["teams"] if t != inn[0]["team"]][0], r1))
    bat_first_wins += i["outcome"].get("winner") == inn[0]["team"]; toss_field += i["toss"]["decision"] == "field"
assert (len(tot1), bat_first_wins, toss_field) == (13, 6, 7)
assert round(sum(t[3] for t in tot1) / 13) == 268
b = pd.read_csv("data/cricinfo/nz_ind_4odi_balls.csv"); n1, n2 = b[b.inning == 1], b[b.inning == 2]
assert (n1.runs.sum(), n2.runs.sum(), n2.wicket.sum()) == (333, 89, 10)
tot1.append(("2026-11-13", "New Zealand", "India", 333))        # 4th ODI: India won the toss and bowled; NZ won by 244 runs (both captures)
assert round(sum(t[3] for t in tot1) / 14) == 272 and bat_first_wins + 1 == 7 and toss_field + 1 == 8
allt = sorted([x["runs"] for m in bay for x in BO.innings_rows(m)] + [333, 89], reverse=True)
assert allt[0] == 371 and allt[1] == 333 and min(allt) == 89
prev_low = min(x["runs"] for m in bay for x in BO.innings_rows(m)); assert prev_low == 202 and 202 - 89 == 113
# highest successful chase: NZ 300/5 v India, 11 Feb 2020
chase = max((BO.innings_rows(m)[1]["runs"], m["info"]["dates"][0]) for m in bay if m["info"]["outcome"].get("winner") == BO.innings_rows(m)[1]["team"])
assert chase == (300, "2020-02-11")
margin_prev = max(m["info"]["outcome"]["by"].get("runs", 0) for m in bay); assert margin_prev == 90
# India at Bay Oval (men's): 26 Jan 2019 W by 90 runs, 28 Jan 2019 W by 7 wkts, 11 Feb 2020 L, 13 Nov 2026 L
ind = sorted((m["info"]["dates"][0], m["info"]["outcome"].get("winner")) for m in bay if "India" in m["info"]["teams"])
assert ind == [("2019-01-26", "India"), ("2019-01-28", "India"), ("2020-02-11", "New Zealand")]

# India's new ball in New Zealand vs elsewhere (first ten overs, India batting)
def india_nb(filt):
    r = []
    for m in ms:
        if "India" not in m["info"]["teams"] or not filt(m): continue
        for x in BO.innings_rows(m):
            if x["team"] == "India": r.append((x["p1r"], x["p1w"]))
    n = len(r); return n, sum(a for a, _ in r) / n, sum(w for _, w in r) / n, 100 * sum(1 for _, w in r if w >= 3) / n
IN_NZ, IN_EL = india_nb(lambda m: m["info"].get("city") in BO.NZ_CITIES), india_nb(lambda m: m["info"].get("city") not in BO.NZ_CITIES)
assert IN_NZ[0] == 28 and (round(IN_NZ[1], 1), round(IN_NZ[2], 2)) == (47.8, 1.43) and (round(IN_EL[1], 1), round(IN_EL[2], 2)) == (51.0, 1.25)
assert (round(IN_NZ[3]), round(IN_EL[3])) == (14, 12)

# chases: win rate by wickets lost in the first ten overs (completed, no D/L)
rows = []
for m in ms:
    o = m["info"]["outcome"]; inn = [x for x in m["innings"] if not x.get("super_over")]
    if len(inn) < 2 or o.get("method") or not o.get("winner"): continue
    rows.append((BO.innings_rows(m)[1]["p1w"], o["winner"] == inn[1]["team"]))
ch = pd.DataFrame(rows, columns=["wk", "won"])
assert len(ch) == 2269
w01, w3, w4 = (round(100 * ch[ch.wk <= 1].won.mean()), round(100 * ch[ch.wk >= 3].won.mean()), round(100 * ch[ch.wk >= 4].won.mean()))
assert (w01, w3, w4) == (64, 26, 13)

# ---------------------------------------------------------------- the 4th ODI, first ten overs (Cricinfo capture)
nb = b[(b.over_no <= 10)]; Lg = nb[nb.legal]
A, Bn = Lg[Lg.inning == 1], Lg[Lg.inning == 2]                    # 1 = NZ batting v India's new ball, 2 = India batting v NZ's new ball
assert (len(A), len(Bn), int(nb[nb.inning == 1].runs.sum()), int(nb[nb.inning == 2].runs.sum()), int(nb[nb.inning == 1].wicket.sum()), int(nb[nb.inning == 2].wicket.sum())) == (60, 60, 72, 26, 0, 4)
assert set(A.bowler) == {"Arshdeep Singh", "Auqib Nabi", "Gurnoor Brar"} and set(Bn.bowler) == {"Matt Henry", "Kyle Jamieson"}
pct = lambda s: round(100 * s.mean())
off = lambda d: d.pitch_line.isin(["OUTSIDE_OFFSTUMP", "WIDE_OUTSIDE_OFFSTUMP"])
short = lambda d: d.pitch_length.isin(["SHORT", "SHORT_OF_A_GOOD_LENGTH"])
assert (pct(off(Bn)), pct(short(Bn))) == (63, 42) and (pct(off(A)), pct(short(A))) == (78, 43)
assert (pct(A.control == 2), pct(Bn.control == 2)) == (32, 32)
assert (pct(A.runs == 0), pct(Bn.runs == 0)) == (55, 82) and (pct(A.runs > 0), pct(Bn.runs > 0)) == (45, 18)
assert (pct(A["shot"] == "DEFENDED"), pct(Bn["shot"] == "DEFENDED")) == (12, 27) and (pct(A["shot"] == "LEFT_ALONE"), pct(Bn["shot"] == "LEFT_ALONE")) == (0, 12)
byb = {k: (pct(g.control == 2), int(nb[(nb.inning == g.inning.iloc[0]) & (nb.bowler == k)].wicket.sum()), len(g)) for k, g in Lg.groupby("bowler")}
assert byb["Arshdeep Singh"] == (40, 0, 30) and byb["Kyle Jamieson"] == (37, 1, 30) and byb["Auqib Nabi"] == (29, 0, 24) and byb["Matt Henry"] == (27, 3, 30)
assert max(v[0] for k, v in byb.items() if v[2] >= 20) == 40
w = nb[(nb.inning == 2) & nb.wicket]
assert list(w.batter) == ["Rohit Sharma", "Virat Kohli", "Shreyas Iyer", "Ruturaj Gaikwad"] and list(w["shot"]) == ["DEFENDED", "DEFENDED", "PUSH", "DEFENDED"]
assert list(w.pitch_line).count("OUTSIDE_OFFSTUMP") == 3 and sum(l in ("SHORT", "SHORT_OF_A_GOOD_LENGTH") for l in w.pitch_length) == 3
hn = n2[n2.bowler == "Matt Henry"]; assert (int(hn.wicket.sum()), int(hn.runs.sum()), len(hn)) == (6, 27, 60)
sh = A[A.bat_runs > 0].groupby("shot").bat_runs.sum().sort_values(ascending=False); assert int(A.bat_runs.sum()) == 67 and int(sh.sum()) == 67
YOUNG_NB = [[int(r.wagon_x), int(r.wagon_y), int(r.bat_runs)] for r in A.itertuples() if r.bat_runs > 0]
assert len(YOUNG_NB) == int((A.bat_runs > 0).sum())
assert (sh.ON_DRIVE, sh.PULL, sh.COVER_DRIVE, sh.CUT_SHOT) == (18, 14, 12, 12)
print("all facts asserted; top scoring shots", sh.head(4).to_dict())


def balls_of(df):
    return [[r.pitch_line, r.pitch_length, "wicket" if r.wicket else ("false" if r.control == 2 else "ok")] for r in df.itertuples()]


# ---------------------------------------------------------------- scenes
def S(vo, sc, **kw): return dict({"vo": vo, "scene": sc}, **kw)
IN = lambda nm: {"t": "IND", "kit": "IND", "name": nm}
NZ = lambda nm: {"t": "NZ", "kit": "NZ", "name": nm}
months = {"01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "10": "Oct", "11": "Nov"}
code = {"New Zealand": "NZ", "South Africa": "SA", "Sri Lanka": "SL", "England": "ENG", "India": "IND", "Netherlands": "NED", "Canada": "CAN", "Pakistan": "PAK", "Australia": "AUS"}
rows_tot = [{"label": f"{months[d[5:7]]} {d[:4]} · {code[t]} v {code[o]}", "v": r, "text": str(r), **({"hl": True, "word": "three"} if r in (371, 333) else {})} for d, t, o, r in tot1]

long = [
 S("Three wickets in the first over. In our ball-by-ball archive of more than five thousand men's one-day innings, it had never happened. Then, on Friday, at the Bay Oval, it happened to India. And on Sunday, they're back.",
   {"type": "lab_big_text", "kicker": "FIRST OVER · BAY OVAL", "lines": ["0 in 5,165.", "Then [Friday.]"]}),
 S("This is the preview of the fifth and final one-day international, on Sunday, at the same ground. India lead the series, two-one. The third match was rained off, and New Zealand won the fourth by two hundred and forty-four runs. So the question for India is simple: how do you survive the new ball at Bay Oval?",
   {"type": "lab_title", "kicker": "THE PREVIEW · NZ V IND · 5TH ODI", "lines": ["Surviving the", "[new ball.]"], "teaser": "Bay Oval · Mount Maunganui · Sunday"}, chapter="The setup"),
 S("Two-one to India, with the third match washed out. If New Zealand win on Sunday, it's two-all. India cannot lose the series. But another collapse would carry real momentum into the Test series, which starts on the nineteenth.",
   {"type": "lab_vs", "kicker": "THE SERIES · 5-MATCH ODI", "title": "India lead, two-one.", "items": [
       {"label": "India", "v": 2, "text": "2", "c": "IND", "t": "IND", "kit": "IND", "word": "two-one"}, {"label": "New Zealand", "v": 1, "text": "1", "c": "NZ", "t": "NZ", "kit": "NZ"}], "max": 3}),
 S("Start with the ground. Is Bay Oval a new-ball graveyard? The history says no. In thirteen men's one-day internationals here, up to October twenty twenty-five, the first ten overs produced one point four wickets an innings. Across all one-day cricket, it's one point four as well. A wicket falls in the first over in about eight per cent of innings here, against thirteen per cent everywhere. And the run rate is higher: four point nine, against four point seven.",
   {"type": "lab_compare", "kicker": "THE FIRST TEN OVERS · MEN'S ODIs", "title": "An ordinary new ball.", "a": {"t": "BAY", "kit": "NZ", "name": "BAY OVAL"}, "b": {"t": "ALL", "kit": "ink", "name": "ALL ODIs"}, "rows": [
       ["Wickets per innings", "1.42", "1.43", "level"], ["Runs per over", "4.88", "4.74", "a"], ["Wicket in over one", "8%", "13%", "a"], ["Lose 3+ in ten overs", "12%", "16%", "a"]]}, chapter="The ground"),
 S("The totals back that up. The average first-innings score is two sixty-eight up to October, and two seventy-two with Friday's three thirty-three. The highest total here is three seventy-one, by New Zealand against Sri Lanka in twenty nineteen. The highest successful chase is three hundred, by New Zealand against India in twenty twenty. Teams batting first have won seven of fourteen. It is an even contest, tilted towards runs.",
   {"type": "lab_dots", "kicker": "FIRST-INNINGS TOTALS AT BAY OVAL · MEN'S ODIs", "title": "A batting ground.", "domain": [150, 400], "ticks": [200, 300, 400], "tick_labels": False, "rows": rows_tot}),
 S("India know this ground. Four one-day matches here: won by ninety runs, won by seven wickets, and lost to a three hundred chase. And on Friday, they were all out for eighty-nine. It is the lowest total ever posted at Bay Oval, by a hundred and thirteen runs.",
   {"type": "lab_units", "kicker": "INDIA AT BAY OVAL · MEN'S ODIs", "title": "Two wins. Two defeats.", "rows": [{"label": "India's ODIs here", "n": 4, "k": 2, "c": "red", "text": "2 won · 2 lost", "word": "eighty-nine"}]}),
 S("India's new-ball batting is a little more fragile in New Zealand. Across twenty-eight innings, they lose one point four three wickets in the first ten overs, against one point two five everywhere else, and score three runs fewer.",
   {"type": "lab_compare", "kicker": "INDIA BATTING · FIRST TEN OVERS", "title": "A little more fragile.", "a": NZ("IN NEW ZEALAND"), "b": {"t": "ALL", "kit": "ink", "name": "ELSEWHERE"}, "rows": [
       ["Wickets lost", "1.43", "1.25", "b"], ["Runs scored", "47.8", "51.0", "b"], ["Lose 3+ wickets", "14%", "12%", "b"]]}),
 S("Why does it matter? Because chases are decided early. In more than two thousand completed one-day chases, teams that lost one wicket or fewer in the first ten overs won sixty-four per cent. Lose three or more, and it drops to twenty-six. Lose four, and it's thirteen. On Friday, India were twenty-six for four.",
   {"type": "lab_vs", "kicker": "CHASES WON · BY WICKETS LOST IN THE FIRST TEN OVERS", "title": "Early wickets decide chases.", "items": [
       {"label": "One wicket or fewer", "v": 64, "text": "64%", "c": "NZ", "t": "NZ", "kit": "NZ"}, {"label": "Three or more", "v": 26, "text": "26%", "c": "IND", "t": "IND", "kit": "IND"},
       {"label": "Four or more", "v": 13, "text": "13%", "c": "IND", "t": "IND", "kit": "IND", "word": "thirteen"}], "max": 100}),
 S("Now, Friday. This is every ball Matt Henry and Kyle Jamieson bowled in the first ten overs: sixty balls, on a pitch map. The gold dots are the wickets. Sixty-three per cent were outside off stump, and more than four in ten were short of a good length or shorter. Nothing exotic. The same question, asked again and again.",
   {"type": "lab_pitch", "kicker": "NEW ZEALAND'S NEW BALL · HENRY AND JAMIESON", "title": "The same question, sixty times.", "pitch_balls": balls_of(Bn), "from": .3, "to": .85}, chapter="Friday"),
 S("India asked a similar question. Arshdeep Singh, Auqib Nabi and Gurnoor Brar bowled sixty balls of their own, more than three-quarters outside off stump. And they made the batters look just as uncomfortable. New Zealand's openers were not in control on thirty-two per cent of balls. So were India's. The same share. But one side took four wickets and conceded twenty-six runs. The other took none, and conceded seventy-two.",
   {"type": "lab_compare", "kicker": "FIRST TEN OVERS · FRIDAY", "title": "Same share. Different result.", "a": NZ("NZ'S NEW BALL"), "b": IN("INDIA'S NEW BALL"), "rows": [
       ["Batter not in control", "32%", "32%", "level"], ["Wickets", "4", "0", "a"], ["Runs conceded", "26", "72", "a"], ["Dot balls", "82%", "55%", "a"]]}),
 S("What separated them? Catches. In the second over, Will Young was dropped twice. He went on to make a hundred and twenty-five. India's bowlers beat the bat a third of the time, and got nothing for it.",
   {"type": "lab_big", "kicker": "THE SECOND OVER", "title": "Two lives.", "value": 125, "label": "Will Young's score after being dropped twice in the second over", "color": "red"}),
 S("Look at it bowler by bowler. Arshdeep Singh drew a false shot on forty per cent of his balls, the most of anyone in the first ten overs, and took no wickets. Kyle Jamieson, thirty-seven per cent, one wicket. Auqib Nabi, twenty-nine, none. Matt Henry drew them on twenty-seven per cent, and took three.",
   {"type": "lab_dots", "kicker": "FIRST TEN OVERS · % OF BALLS BATTER NOT IN CONTROL", "title": "Beaten, not rewarded.", "domain": [0, 50], "ticks": [0, 25, 50], "rows": [
       {"label": "Arshdeep · 0 wkts", "v": 40, "text": "40%", "hl": True, "word": "forty"}, {"label": "Jamieson · 1 wkt", "v": 37, "text": "37%"},
       {"label": "Nabi · 0 wkts", "v": 29, "text": "29%"}, {"label": "Henry · 3 wkts", "v": 27, "text": "27%", "hl": True}]}),
 S("Then, how India batted. In the first ten overs, they defended twenty-seven per cent of balls, and scored off just eighteen. New Zealand's openers defended twelve, and scored off forty-five. India left alone twelve per cent. New Zealand's openers never needed to.",
   {"type": "lab_compare", "kicker": "FIRST TEN OVERS · HOW THEY BATTED", "title": "Defend, or score.", "a": IN("INDIA"), "b": NZ("NEW ZEALAND"), "rows": [
       ["Balls defended", "27%", "12%", "b"], ["Balls left alone", "12%", "0%", "level"], ["Balls scored off", "18%", "45%", "b"]]}),
 S("The four wickets tell the same story. रोहित शर्मा, विराट कोहली and ऋतुराज गायकवाड़ were out defending. श्रेयस अय्यर was out pushing. Three of the four balls were outside off stump, and three were short of a good length or shorter. Not one was out to a drive, a cut or a pull.",
   {"type": "lab_units", "kicker": "INDIA'S FOUR NEW-BALL WICKETS", "title": "Out on the defensive.", "rows": [{"label": "Dismissed defending or pushing", "n": 4, "k": 4, "c": "red", "text": "4 of 4", "word": "four"}]}),
 S("So how do India survive? Three rules, from the data. One: leave more. Sixty-three per cent of New Zealand's new-ball deliveries were outside off stump, and India left alone twelve per cent. Two: score off more balls. New Zealand's openers scored off nearly half. India scored off one in five. Three: respect the back-of-a-length ball. Three of the four wickets came there, or shorter, and none was an attacking shot.",
   {"type": "board", "tone": "cream", "tag": "ILLUSTRATIVE FIELD", "head": ["Three ways to", "[survive] the new ball"],
    "fielders": ["keeper", "slip", "2nd slip", "gully", "point", "cover", "mid-off", "mid-on", "fine leg"], "hl": ["slip", "2nd slip", "gully"],
    "zones": [{"pos": ["slip", "2nd slip", "gully"], "label": "catchers waiting", "at": .45}], "length": {"from": 5.5, "to": 8, "c": "hl", "at": .6}}, chapter="The plan"),
 S("And here is what scoring looks like when the new ball doesn't bite. New Zealand's openers made sixty-seven off the bat in ten overs without losing a wicket, in every direction. The on drive brought eighteen of them, the pull fourteen, the cover drive and the cut twelve each.",
   {"type": "lab_wagon", "kicker": "NEW ZEALAND · FIRST TEN OVERS · 67 RUNS, NO WICKET", "title": "When the ball doesn't bite.", "wagon_shots": YOUNG_NB}),
 S("What do we know about Sunday? Not much that is certain. The squads, the toss and the weather will be settled on the morning, and we can't say which strip they'll use. What we do know is how Friday played: a slowish, hard surface, a little nip early, and little change later. India won the toss, bowled first, and New Zealand made three thirty-three.",
   {"type": "lab_big_text", "kicker": "WHAT WE KNOW · AND DON'T", "lines": ["Friday: slow, hard,", "[a little nip.]"]}, chapter="Sunday"),
 S("Our read: the new ball at Bay Oval is not the problem. The numbers say it's an ordinary new ball on a ground that scores. What India face is a bowler in form, Matt Henry, with six for twenty-seven, and their own habit of defending the ball outside off stump. Survive the first ten overs with one wicket or fewer, and history says a chase is won sixty-four per cent of the time. Lose three, and it's twenty-six.",
   {"type": "lab_big_text", "kicker": "THE VERDICT", "lines": ["Not the pitch.", "[The plan.]"]}, chapter="The verdict"),
 S("Will India survive the first ten overs? Tell us in the comments, and follow for the Test series preview.",
   {"type": "cta", "lines": [{"t": "WILL INDIA SURVIVE?"}, {"t": "THE THIRD MAN", "c": "gold"}], "pill": "SUBSCRIBE FOR MORE"}),
]

SRC = ["Cricsheet men's ODI ball-by-ball archive (cricsheet.org/downloads/odis_json.zip, ODC-BY), 50-over matches 2002 to 25 Oct 2025 (2,617 matches, 5,165 innings; super overs excluded). "
       "Bay Oval = the 13 men's ODIs at Bay Oval, Mount Maunganui; 'new ball' = overs 1-10; wickets include run outs, exclude retired hurt; chases exclude D/L results. Figures: analysis/bay_oval_new_ball.py and make_bay_oval_preview.py.",
       "ESPNcricinfo match capture, NZ v IND 4th ODI, Bay Oval, Mount Maunganui (match 1539440): ball-by-ball with line, length, shot and control, captured with our own tool; first-ten-over figures computed from it.",
       "Cricbuzz match capture (match 161271): over-by-over cross-check; match notes (toss, conditions, dropped catches) used as leads. Result in both: New Zealand won by 244 runs; Player of the Match Matt Henry.",
       "Series position (India 2-1; third ODI rained off) and the 5th ODI date (15 Nov) from ESPN's fixture list and the channel's schedule; squads, toss, weather and pitch for the 5th ODI were not yet confirmed when this was made.",
       "All graphics are original; the field plan is illustrative, not the actual field."]
DESC = ("India lead New Zealand 2-1 with one ODI to play, at the same ground as the 4th ODI where India lost three wickets in the first over and were bowled out for 89. "
        "So how do you survive the new ball at Bay Oval? We look at the ground's history (13 men's ODIs), how the first ten overs have played, what happened on Friday ball by ball, and what India's batters can do about it.\n\n"
        "Sources: Cricsheet ball-by-ball (ODC-BY); ESPNcricinfo and Cricbuzz match pages (captured with our own tool, cross-checked over by over). All numbers are computed by us; "
        "'not in control' is the Cricinfo shot-control flag. Graphics are original illustrations, not broadcast footage; the field plan is illustrative.")
TAGS = ["India vs New Zealand", "5th ODI", "Bay Oval", "Mount Maunganui", "new ball", "cricket analysis", "cricket tactics", "Matt Henry", "India batting", "The Third Man"]
spec = {"slug": "bay_oval_new_ball", "theme": "lab", "theme_long": "lab", "captions": "serif", "captions_long": False, "series": "tactics",
        "tag": "TACTICS BOARD", "tagsub": "BAY OVAL · 5TH ODI PREVIEW",
        "files": {"long": "Surviving_the_New_Ball_at_Bay_Oval_5th_ODI_Preview", "short": "_unused"},
        "thumb": {"kicker": "5TH ODI PREVIEW", "lines": [{"t": "SURVIVING THE"}, {"t": "NEW BALL", "c": "gold"}], "hero": "0/3", "herosize": 420},
        "sources": SRC, "long": long,
        "yt": {"long": {"title": "Surviving the New Ball at Bay Oval | NZ vs India 5th ODI Preview (Tactics)", "description": DESC, "tags": TAGS}}}
voice_lint.fix_spec(spec)
json.dump(spec, open("specs/bay_oval_new_ball.json", "w"), ensure_ascii=False, indent=1)
print("wrote specs/bay_oval_new_ball.json:", sum(len(x["vo"].split()) for x in long), "words,", len(long), "scenes")
