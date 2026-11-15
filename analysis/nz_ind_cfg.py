"""Match configuration for the NZ v IND ODI series 2026 analysis: which innings India batted, rain revisions of the chase, and the expected figures from Wikipedia's match boxes (used by the validation).
India batted second in matches 1, 2 and 4 (they won the toss and fielded in 1-4) and first in the 5th (New Zealand won the toss and fielded)."""
STEMS = ["nz_ind_1odi", "nz_ind_2odi", "nz_ind_4odi", "nz_ind_5odi"]
INFO = {
    "nz_ind_1odi": {"n": 1, "label": "1st ODI", "india_bats": 2, "venue": "Eden Park, Auckland", "date": "2026-11-04",
                    "revision": {"after_legal_ball": 17, "target": 143, "balls_total": 192, "note": "rain stopped play after 2.5 overs of India's chase (30 runs); target revised to 143 from 32 overs (DLS)"}},
    "nz_ind_2odi": {"n": 2, "label": "2nd ODI", "india_bats": 2, "venue": "Wellington Regional Stadium", "date": "2026-11-07", "revision": None,
                    "note": "rain ended play at 113/7 after 26 overs; India 4 runs ahead of the DLS par (109): India won by 4 runs (DLS). Win probability below is the model's, not the DLS result"},
    "nz_ind_4odi": {"n": 4, "label": "4th ODI", "india_bats": 2, "venue": "Bay Oval, Mount Maunganui", "date": "2026-11-13", "revision": None},
    "nz_ind_5odi": {"n": 5, "label": "5th ODI", "india_bats": 1, "venue": "Bay Oval, Mount Maunganui", "date": "2026-11-15", "revision": None},
}
INDIA_BATS = {k: v["india_bats"] for k, v in INFO.items()}
LABELS = {k: v["label"] for k, v in INFO.items()}
# Wikipedia match boxes (cite Cricinfo): innings 1 and 2 (score, wickets, overs), a few individual lines
WIKI = {
    "nz_ind_1odi": {"inn": {1: (185, 10, "40.2"), 2: (143, 5, "22.4")}, "bat": {"Virat Kohli": (74, 51), "Tim Seifert": (38, 43)}, "bowl": {"Arshdeep Singh": (4, 70, 10), "Jacob Duffy": (3, 49, 7)}},
    "nz_ind_2odi": {"inn": {1: (134, 10, "41.0"), 2: (113, 7, "26.0")}, "bat": {"Daryl Mitchell": (55, 104), "Shreyas Iyer": (30, 46)}, "bowl": {"Gurnoor Brar": (4, 30, 10), "Kyle Jamieson": (3, 35, 10)}},
    "nz_ind_4odi": {"inn": {1: (333, 10, "50.0"), 2: (89, 10, "26.4")}, "bat": {"Will Young": (125, 108), "Ishan Kishan": (27, 53)}, "bowl": {"Matt Henry": (6, 27, 9.4), "Axar Patel": (2, 39, 10)}},
    "nz_ind_5odi": {"inn": {1: (209, 10, "42.1"), 2: (187, 10, "48.1")}, "bat": {"Axar Patel": (46, 55), "Dean Foxcroft": (31, 42)}, "bowl": {"Arshdeep Singh": (3, 30, 10), "Mitchell Santner": (3, 47, 10)}},
}
# series leaders per Wikipedia's infobox
WIKI_LEADERS = {"NZ most runs": ("Will Young", 162), "IND most runs": ("Virat Kohli", 86), "NZ most wickets": ("Jacob Duffy", 9), "IND most wickets": ("Gurnoor Brar", 9)}
