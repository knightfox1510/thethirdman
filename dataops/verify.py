"""The verification gate. Every number a video states goes through a claim with its sources:
    from dataops import verify as V
    c = V.Claims("gambhir_player_coach")
    c.check("India Tests since 27 Jul 2024 (W-L-D)", (8, 10, 3), {"cricsheet": (8, 10, 3), "cricinfo": (8, 10, 3)})        # two independent sources agree: OK
    c.check("T20I strike rate", 167, {"cricsheet": 167}, scope="archive")        # one source, but the video says 'in our archive': LABELLED
    c.check("Test win rate", 38.1, {"cricsheet": 38.1})                          # one source, claimed without a label: UNVERIFIED -> build/upload blocked
    c.require_complete("team_India")                                            # the coverage audit must say COMPLETE for the subject, else claims need scope='archive'
    c.save(spec)                                                                # writes data/provenance/<slug>.json and sets spec['provenance_required']
Statuses: OK (>=2 independent sources agree) | LABELLED (single source, scope='archive'/'sample', said so on screen) | CONFLICT (sources disagree) | UNVERIFIED (single source, unlabelled).
gate(spec) (called by engine.py build and publish/youtube.py) refuses to build/upload a spec with provenance_required unless every claim is OK or LABELLED.
Source independence: cricsheet, sportmonks, cricinfo, cricbuzz, wikipedia (which cites cricinfo, so it counts as a Tier C check, not as independent of cricinfo), official (ICC/BCCI/board sites)."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAMILY = {"wikipedia": "cricinfo", "cricinfo": "cricinfo", "cricbuzz": "cricbuzz", "cricsheet": "cricsheet", "sportmonks": "sportmonks", "official": "official", "icc": "official", "bcci": "official"}


def _norm(v):
    return tuple(_norm(x) for x in v) if isinstance(v, (list, tuple)) else round(v, 2) if isinstance(v, float) else v


class Claims:
    def __init__(self, slug):
        self.slug = slug; self.items = []

    def check(self, name, value, sources, scope="career", tol=0):
        """sources: {source name: value or None (not available)}. scope 'career' = the video states it as fact; 'archive'/'sample' = the video says 'in our archive'."""
        have = {k: v for k, v in sources.items() if v is not None}
        agree = {k for k, v in have.items() if self._eq(v, value, tol)}
        fam = {FAMILY.get(k, k) for k in agree}
        conflict = [k for k, v in have.items() if not self._eq(v, value, tol)]
        status = "CONFLICT" if conflict else "OK" if len(fam) >= 2 else "LABELLED" if scope in ("archive", "sample") and agree else "UNVERIFIED"
        self.items.append({"claim": name, "value": value, "sources": {k: v for k, v in sources.items()}, "scope": scope, "status": status, "conflicts": conflict})
        mark = {"OK": "  ok ", "LABELLED": " lbl ", "CONFLICT": "FAIL ", "UNVERIFIED": "UNVF "}[status]
        print(f"{mark} {name}: {value}  [{', '.join(f'{k}={v}' for k, v in sources.items())}]")
        return status

    @staticmethod
    def _eq(a, b, tol):
        a, b = _norm(a), _norm(b)
        return abs(a - b) <= tol if isinstance(a, (int, float)) and isinstance(b, (int, float)) else a == b

    def require_complete(self, audit_name, fmt=None):
        """The coverage audit file (data/audit/<audit_name>.json) must say COMPLETE (for fmt, or every format) or the claims that depend on it stay unverified."""
        p = f"{ROOT}/data/audit/{audit_name}.json"
        a = json.load(open(p)) if os.path.exists(p) else None
        fm = (a or {}).get("formats", {}); sel = [fm[fmt]] if fmt and fmt in fm else list(fm.values())
        ok = bool(sel) and all(f["status"] == "COMPLETE" for f in sel)
        self.items.append({"claim": f"coverage audit {audit_name}{'/' + fmt if fmt else ''}", "value": "COMPLETE" if ok else "GAPS/UNAUDITED", "sources": {"audit": "data/audit/" + audit_name + ".json"}, "scope": "coverage",
                           "status": "OK" if ok else "UNVERIFIED", "conflicts": []})
        print(("  ok " if ok else "UNVF ") + f"coverage audit {audit_name}: " + ("COMPLETE" if ok else "not complete / not run: state totals as 'in our archive'"))
        return ok

    def summary(self):
        from collections import Counter
        return Counter(i["status"] for i in self.items)

    def save(self, spec=None):
        os.makedirs(f"{ROOT}/data/provenance", exist_ok=True)
        json.dump({"slug": self.slug, "claims": self.items, "summary": dict(self.summary())}, open(f"{ROOT}/data/provenance/{self.slug}.json", "w"), indent=1, ensure_ascii=False, default=str)
        if spec is not None: spec["provenance_required"] = True
        print("provenance:", dict(self.summary()), "->", f"data/provenance/{self.slug}.json")
        return self.summary()


def gate(spec):
    """None if the spec may be built/uploaded; otherwise a message. Specs without provenance_required (older videos) pass."""
    if not spec.get("provenance_required"): return None
    p = f"{ROOT}/data/provenance/{spec['slug']}.json"
    if not os.path.exists(p): return f"{spec['slug']}: provenance_required but {p} is missing: run the generator (it must call dataops.verify)"
    bad = [i for i in json.load(open(p))["claims"] if i["status"] in ("UNVERIFIED", "CONFLICT")]
    if bad: return f"{spec['slug']}: {len(bad)} unverified/conflicting claims, e.g. " + "; ".join(f"{b['claim']} [{b['status']}]" for b in bad[:4])
    return None


if __name__ == "__main__":
    s = json.load(open(sys.argv[1])); m = gate(s); print(m or "gate: ok"); sys.exit(1 if m else 0)
