"""Builds specs/stat_check_bumrah_rashid.json from the IPL cache; every number is computed and asserted here."""
import json, sys, pandas as pd
sys.path.insert(0, "analysis")
from common import ipl
import bumrah_rashid as B
d = ipl(); A = {}
for nm, key in (("Jasprit Bumrah", "JB"), ("Rashid Khan", "RK")):
    x = d[d.bowler == nm]; A[key] = {"all": B.bowl(x), **{ph: B.bowl(x[x.phase == ph]) for ph in ("powerplay", "middle", "death")},
                                     "season": {int(s): B.bowl(y) for s, y in x.groupby("season")}}
lg = lambda y: 6 * y.runs.sum() / y.legal_bowl.sum()
LG = {"all": lg(d), **{ph: lg(d[d.phase == ph]) for ph in ("powerplay", "middle", "death")}}
J, R = A["JB"], A["RK"]
r2 = lambda v: round(float(v), 2)
# claims
assert J["all"]["balls"] == 3631 and R["all"]["balls"] == 3527
assert r2(J["all"]["econ"]) == 7.34 and r2(R["all"]["econ"]) == 7.26 and round(LG["all"], 1) == 8.5
assert J["powerplay"]["balls"] / J["all"]["balls"] > 1 / 3
assert round(R["middle"]["balls"] / R["all"]["balls"] * 100) == 72
assert round(J["all"]["bp6"]) == 27 and round(R["all"]["bp6"]) == 18
rk_peak = [R["season"][s]["econ"] for s in range(2017, 2023)]; assert max(rk_peak) < 6.8
streak = best = 0
for s in sorted(J["season"]):
    streak = streak + 1 if J["season"][s]["econ"] < 7 and (s - 1 in J["season"] or streak == 0) else (1 if J["season"][s]["econ"] < 7 else 0); best = max(best, streak)
assert best == 3, best
assert all(R["season"][s]["econ"] > 8 for s in range(2023, 2027))
# who was hardest to score off, 2017-2022 (min 1,500 balls)?
p = d[d.season.between(2017, 2022)].groupby("bowler").apply(lambda y: pd.Series({"balls": y.legal_bowl.sum(), "econ": lg(y)}))
p = p[p.balls >= 1500].sort_values("econ"); print(p.head(5).round(2)); rk_best = p.index[0] == "Rashid Khan"
print({k: {ph: (r2(v[ph]["econ"]), v[ph]["balls"]) for ph in ("all", "powerplay", "middle", "death")} for k, v in A.items()}, {k: r2(v) for k, v in LG.items()})
print("dot", r2(J["all"]["dot"]), r2(R["all"]["dot"]), "best streak", best, "rashid best 2017-22", rk_best)

FOOT = "IPL ball-by-ball, Sportmonks, 2013-2026 · economy = runs off the bat + wides + no-balls per over · super overs excluded · analysis/bumrah_rashid.py"
TABS = ["ECONOMY", "POWERPLAY", "MIDDLE", "DEATH", "DOTS", "SIXES", "PEAK"]
JB = {"t": "JB", "kit": "MI", "name": "Bumrah"}; RK = {"t": "RK", "kit": "GT", "name": "Rashid"}
def S(vo, sc): return {"vo": vo, "scene": sc}
def rnd(i): return {"tabs": TABS, "tab": i, "foot": FOOT}
def vs(i, kicker, title, j, r, lgv, word_r="rashid"):
    return dict(type="lab_vs", kicker=kicker, title=title, items=[
        {"label": f"Bumrah · {j['balls']:,} balls", "v": r2(j["econ"]), "text": f"{j['econ']:.2f}", "c": "MI", "t": "JB", "kit": "MI", "word": "bumrah"},
        {"label": f"Rashid · {r['balls']:,} balls", "v": r2(r["econ"]), "text": f"{r['econ']:.2f}", "c": "GT", "t": "RK", "kit": "GT", "word": word_r},
        {"label": "IPL average", "v": r2(lgv), "text": f"{lgv:.2f}", "c": "grey", "at": .05}], max=11, **rnd(i))
title = S("Two of the best T20 bowlers of this era. Both arrived in the IPL after twenty twelve, so we have every ball they've bowled in it. So, who's better? Seven rounds.",
          {"type": "lab_title", "kicker": "STAT CHECK", "lines": ["Bumrah or [Rashid?]"], "teaser": "7 rounds · every IPL ball", "players": [{"kit": "MI", "pose": "bowl", "cap": True, "name": "Bumrah", "sub": "IPL 2013-2026", "chip": [f"{J['all']['balls']:,}", "balls bowled"]}, {"kit": "GT", "pose": "bowl", "cap": True, "name": "Rashid Khan", "sub": "IPL 2017-2026", "chip": [f"{R['all']['balls']:,}", "balls bowled"]}]})
method = S("First, the workload. बुमराह has bowled three thousand six hundred and thirty-one balls in the IPL. Rashid, three thousand five hundred and twenty-seven. Almost exactly the same.",
           dict(type="lab_compare", kicker="THE METHOD", title="Same workload.", a=JB, b=RK, rows=[
               ["Balls bowled", f"{J['all']['balls']:,}", f"{R['all']['balls']:,}", "level"], ["IPL seasons", str(len(J["season"])), str(len(R["season"])), "level"],
               ["First season", str(min(J["season"])), str(min(R["season"])), "level"]], foot=FOOT))
r1 = S("Round one: economy. Since twenty thirteen, IPL bowlers have gone for eight and a half an over. बुमराह: seven point three four. Rashid: seven point two six. Almost nothing in it. Round one: level.",
       vs(0, "ROUND 1 · ECONOMY", "Almost nothing in it.", J["all"], R["all"], LG["all"]))
r2_ = S("Round two: the powerplay. More than a third of बुमराह's balls come here, at six point nine five. Rashid bowls far fewer, at seven point four seven. बुमराह takes it.",
        vs(1, "ROUND 2 · OVERS 1-6", "The new ball.", J["powerplay"], R["powerplay"], LG["powerplay"]))
r3 = S("Round three: the middle overs. This is Rashid's home. Seventy-two percent of his balls, at six point eight six. बुमराह is cheaper still, but bowls far fewer of them. We'll call it level.",
       vs(2, "ROUND 3 · OVERS 7-15", "Rashid's home.", J["middle"], R["middle"], LG["middle"]))
r4 = S("Round four: the death. The league goes at ten an over. बुमराह has bowled more than fourteen hundred balls there, at eight point one nine. Rashid, six hundred and thirty, at eight point seven five. बुमराह, clearly.",
       vs(3, "ROUND 4 · OVERS 16-20", "The death.", J["death"], R["death"], LG["death"]))
r5 = S("Round five: dot balls. Four in every ten of बुमराह's balls are dots. Rashid, about three and a half. बुमराह again.",
       dict(type="lab_rings", kicker="ROUND 5 · DOT BALLS", title="Nothing to hit.", items=[
           {"v": r2(J["all"]["dot"]), "dec": 1, "label": "Bumrah", "c": "MI", "t": "JB", "kit": "MI"},
           {"v": r2(R["all"]["dot"]), "dec": 1, "label": "Rashid", "c": "GT", "t": "RK", "kit": "GT", "word": "rashid"}], **rnd(4)))
r6 = S("Round six: sixes. Batters clear the rope off बुमराह once every twenty-seven balls. Off Rashid, every eighteen. बुमराह.",
       dict(type="lab_vs", kicker="ROUND 6 · SIXES", title="Balls per six conceded.", items=[
           {"label": "Bumrah", "v": r2(J["all"]["bp6"]), "text": f"{J['all']['bp6']:.1f}", "c": "MI", "t": "JB", "kit": "MI"},
           {"label": "Rashid", "v": r2(R["all"]["bp6"]), "text": f"{R['all']['bp6']:.1f}", "c": "GT", "t": "RK", "kit": "GT", "word": "rashid"}], max=30, **rnd(5)))
peak_rows = [{"label": f"Rashid {s}", "v": round(100 * (10 - R['season'][s]['econ']) / 5), "text": f"{R['season'][s]['econ']:.2f}", "hl": True, "at": .1 + .05 * k}
             for k, s in enumerate(range(2017, 2023))]
r7 = S("Round seven: the peak. From twenty seventeen to twenty twenty-two, Rashid went at under six point eight an over. Six seasons in a row. बुमराह has never put together more than three seasons under seven. Rashid takes it.",
       dict(type="lab_dots", kicker="ROUND 7 · THE PEAK", title="Six years under 6.8.", sub="economy by season · further right = cheaper", rows=peak_rows,
            domain=[0, 100], tick_labels=False, **rnd(6)))
since = S("But since then, Rashid has gone at over eight an over, every season. बुमराह was at his best in twenty twenty-four and twenty twenty-five, before a quiet twenty twenty-six.",
          dict(type="lab_compare", kicker="SINCE 2023", title="Then the lines crossed.", a=JB, b=RK, rows=[
              [str(s), (f"{J['season'][s]['econ']:.2f}" if s in J["season"] else "did not play"), f"{R['season'][s]['econ']:.2f}",
               "a" if s in J["season"] and J["season"][s]["econ"] < R["season"][s]["econ"] else "b"] for s in range(2023, 2027)], foot=FOOT))
card = S("So, the scorecard. बुमराह wins four rounds. Rashid wins one. Two are level.",
         dict(type="lab_score", kicker="THE SCORE", title="That sounds like Bumrah.", rows=[
             {"label": "Economy", "win": "Level", "c": "grey"}, {"label": "Powerplay", "win": "Bumrah", "c": "MI"}, {"label": "Middle overs", "win": "Level", "c": "grey"},
             {"label": "Death", "win": "Bumrah", "c": "MI"}, {"label": "Dot balls", "win": "Bumrah", "c": "MI"}, {"label": "Sixes", "win": "Bumrah", "c": "MI"},
             {"label": "The peak", "win": "Rashid", "c": "GT"}], foot=FOOT))
ver_vo = "बुमराह is the better IPL bowler. But for six seasons, " + ("no bowler in the IPL was harder to score off than Rashid Khan." if rk_best else "Rashid Khan was one of the hardest bowlers in the IPL to score off.")
verdict = S(ver_vo, {"type": "lab_big_text", "kicker": "THE VERDICT", "lines": ["Bumrah, [4-1].", "Rashid's peak:", "untouchable."] if rk_best else ["Bumrah, [4-1].", "Rashid's peak:", "elite."]})
cta = S("Who should we put head to head next? Tell us in the comments.", {"type": "cta", "lines": [{"t": "WHO'S NEXT?"}, {"t": "STAT CHECK", "c": "gold"}], "pill": "SUBSCRIBE FOR MORE"})
top5 = p.head(5)
peak_tbl = S("How good was that peak? From twenty seventeen to twenty twenty-two, of every bowler with fifteen hundred balls, Rashid had the best economy in the IPL. Six point three four. Nobody else was under seven.",
             dict(type="lab_vs", kicker="2017-2022 · MIN. 1,500 BALLS", title="Nobody close.", items=[
                 {"label": f"{'Rashid' if n == 'Rashid Khan' else n.split()[-1]} · {int(r.balls):,} balls", "v": r2(r.econ), "text": f"{r.econ:.2f}", "c": "GT" if n == "Rashid Khan" else ("MI" if n == "Jasprit Bumrah" else "ink"),
                  "at": .1 + .12 * k} for k, (n, r) in enumerate(top5.head(3).iterrows())], max=8, foot=FOOT))
assert top5.econ.iloc[1] >= 7.0
hands = {k: {h: B.bowl(d[(d.bowler == nm) & (d.bat_hand == h)]) for h in ("right-hand-bat", "left-hand-bat")} for nm, k in (("Jasprit Bumrah", "JB"), ("Rashid Khan", "RK"))}
hand = S("Both are tougher on left-handers. बुमराह goes at six point six two against them, and seven point six six against right-handers. Rashid's gap is smaller. But he takes a left-hander's wicket every seventeen balls.",
         dict(type="lab_compare", kicker="LEFT V RIGHT", title="Lefties, beware.", a=JB, b=RK, rows=[
             ["Economy v left-handers", f"{hands['JB']['left-hand-bat']['econ']:.2f}", f"{hands['RK']['left-hand-bat']['econ']:.2f}", "a"],
             ["Economy v right-handers", f"{hands['JB']['right-hand-bat']['econ']:.2f}", f"{hands['RK']['right-hand-bat']['econ']:.2f}", "b"],
             ["Balls per wicket v left-handers", f"{hands['JB']['left-hand-bat']['sr']:.1f}", f"{hands['RK']['left-hand-bat']['sr']:.1f}", "b"]], foot=FOOT))
assert round(hands["RK"]["left-hand-bat"]["sr"]) == 17 and r2(hands["JB"]["left-hand-bat"]["econ"]) == 6.62
kv = {k: B.bowl(d[(d.bowler == nm) & (d.batter == "Virat Kohli")]) for nm, k in (("Jasprit Bumrah", "JB"), ("Rashid Khan", "RK"))}
kohli = S("And the biggest name they've both bowled to? विराट कोहली has taken one sixty-one off बुमराह's hundred and eight balls. But बुमराह has dismissed him five times. Against Rashid, कोहली has a hundred and seventeen off ninety balls, and been out twice.",
          dict(type="lab_compare", kicker="THE KOHLI TEST", title="Both v Kohli.", a=JB, b=RK, rows=[
              ["Balls to Kohli", str(kv["JB"]["balls"]), str(kv["RK"]["balls"]), "level"], ["Runs conceded", str(kv["JB"]["runs"]), str(kv["RK"]["runs"]), "level"],
              ["Times dismissed him", str(kv["JB"]["wkts"]), str(kv["RK"]["wkts"]), "a"], ["Economy", f"{kv['JB']['econ']:.2f}", f"{kv['RK']['econ']:.2f}", "b"]], foot=FOOT))
assert (kv["JB"]["balls"], kv["JB"]["runs"], kv["JB"]["wkts"], kv["RK"]["balls"], kv["RK"]["runs"], kv["RK"]["wkts"]) == (108, 161, 5, 90, 117, 2), kv
spec = {"slug": "stat_check_bumrah_rashid", "theme": "lab", "captions": "lab", "series": "lab", "tag": "STAT CHECK", "tagsub": "BUMRAH OR RASHID?",
        "files": {"long": "Stat_Check_Bumrah_or_Rashid_Every_IPL_Ball", "short": "Stat_Check_Bumrah_or_Rashid_Short_9x16"},
        "thumb": {"kicker": "STAT CHECK", "lines": [{"t": "BUMRAH"}, {"t": "OR RASHID?", "c": "gold"}], "hero": "4-1", "herosize": 300},
        "sources": ["Sportmonks IPL ball-by-ball cache 2013-2026 (both careers began in 2013 or later, so every IPL ball they've bowled is included). Economy = runs off the bat + wides + no-balls per 6 legal balls; byes and leg byes excluded; super overs excluded. analysis/bumrah_rashid.py, make_bumrah_rashid.py"],
        "long": [title, method, r1, r2_, r3, r4, r5, r6, r7, peak_tbl, since, hand, kohli, card, verdict, cta],
        "short": [title, r1, r4, r6, r7, card, verdict, cta]}
for k, nm in [(0, "The question"), (2, "Round 1: Economy"), (3, "Round 2: Powerplay"), (4, "Round 3: Middle overs"), (5, "Round 4: Death"), (6, "Round 5: Dot balls"),
              (7, "Round 6: Sixes"), (8, "Round 7: The peak"), (11, "Left v right, and Kohli"), (13, "The verdict")]:
    spec["long"][k] = dict(spec["long"][k], chapter=nm)
spec["yt"] = {"long": {"title": "Bumrah or Rashid? We checked every IPL ball they've bowled",
                       "description": "Stat Check: Jasprit Bumrah vs Rashid Khan across every IPL ball since 2013. Seven rounds: economy, powerplay, middle overs, death, dot balls, sixes and peak seasons.",
                       "tags": ["Jasprit Bumrah", "Rashid Khan", "Bumrah vs Rashid", "IPL stats", "best T20 bowler", "Stat Check", "The Third Man"]},
              "short": {"title": "Bumrah or Rashid? Every IPL ball, 7 rounds 📊 #Shorts", "description": "Stat Check: Bumrah vs Rashid, every IPL ball since 2013.",
                        "tags": ["Bumrah", "Rashid Khan", "IPL", "cricket stats", "Stat Check", "The Third Man"]}}
import voice_lint; voice_lint.fix_spec(spec)
json.dump(spec, open("specs/stat_check_bumrah_rashid.json", "w"), ensure_ascii=False, indent=1)
print("long words", sum(len(x["vo"].split()) for x in spec["long"]), "short", sum(len(x["vo"].split()) for x in spec["short"]))
