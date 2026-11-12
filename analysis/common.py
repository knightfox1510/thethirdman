"""Shared helpers for the per-video analysis scripts.

Every script in analysis/ prints each Sportmonks-derived figure used in its spec,
so any number on screen can be traced and regenerated. Run from the repo root:
    python3 analysis/<slug>.py
Needs the data cache (SM_KEY=... python3 fetch_ipl.py; India T20Is via sm.fixture()).

Conventions (match stats.py):
  - bowler economy = runs off the bat + wides + no-balls per 6 legal deliveries (byes and leg byes excluded)
  - team run rate   = all runs incl. byes and leg byes per 6 legal deliveries
  - batter SR       = runs off the bat per 100 balls faced (wides don't count as balls faced)
  - super overs (innings S3/S4) are excluded
  - phases: powerplay overs 1-6, middle 7-15, death 16-20
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stats  # noqa: E402

batting, bowling = stats.batting, stats.bowling


def ipl():
    df = stats.ipl()
    return df[df.inning.isin(["S1", "S2"])]


def t20i(fixtures=None):
    df = stats.t20i()
    df = df[df.inning.isin(["S1", "S2"])]
    return df[df.fixture.isin(fixtures)] if fixtures is not None else df


def econ(d):
    return 6 * d.runs.sum() / max(1, d.legal_bowl.sum())


def run_rate(d):
    return 6 * d.team_runs.sum() / max(1, d.legal_bowl.sum())


def show(label, value, fmt="{:.2f}"):
    v = fmt.format(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else value
    print(f"  {label:<58} {v}")


def section(title):
    print(f"\n== {title}")
