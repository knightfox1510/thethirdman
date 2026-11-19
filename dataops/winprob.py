"""A transparent ODI win-probability model, fitted on the Cricsheet ODI archive (men's, 50-over matches without a rain method, 2009 onwards).
    python3 -m dataops.winprob fit        # fits, validates on held-out matches, saves data/models/odi_winprob.json
    from dataops import winprob; M = winprob.load(); M.p_chase(runs_needed, balls_left, wkts); M.p_first(runs, balls_left, wkts)
Chase (2nd innings): logistic regression on required rate, wickets lost, balls left, runs needed and the interactions that matter, fitted on every ball of every chase.
First innings: a ridge regression predicts the final total from (runs, wickets, balls left); the probability the side batting first wins is one minus the chaser's probability at ball 0 of that
target, averaged over the typical error of the projection. Both are FITTED ON AN ARCHIVE SAMPLE (see dataops.audit): use the results as "in our archive" indications. The model is validated
(log loss, accuracy, calibration bins) before it is used; the numbers are printed and saved with the model."""
import json, math, os, sys
import numpy as np
from . import cricsheet as C

ROOT = C.ROOT; PATH = f"{ROOT}/data/models/odi_winprob.json"


def _chase_feats(need, left, w):
    left = np.maximum(left, 1); rrr = np.clip(6 * need / left, 0, 30)
    return np.column_stack([np.ones_like(rrr), rrr, w, left / 300.0, np.log1p(np.maximum(need, 0)), rrr * w, rrr * (left / 300.0), (w >= 7).astype(float) * rrr, np.minimum(need, 0) * 0])


def _fit_logit(X, y, l2=1e-3, iters=40):
    b = np.zeros(X.shape[1])
    for _ in range(iters):
        z = X @ b; p = 1 / (1 + np.exp(-np.clip(z, -30, 30))); g = X.T @ (p - y) + l2 * b; W = p * (1 - p)
        H = (X * W[:, None]).T @ X + l2 * np.eye(X.shape[1]); step = np.linalg.solve(H, g); b -= step
        if np.abs(step).max() < 1e-7: break
    return b


def _first_feats(runs, left, w):
    left = np.asarray(left, float); f = left / 300.0
    return np.column_stack([np.ones_like(f), runs, w, f, runs * f, w * f, runs * w, f * f, np.log1p(runs), runs * f * f])


def rows():
    chase, first, meta = [], [], []
    for lab, p, m in C.matches("male"):
        i = m["info"]
        if lab != "ODI" or i["dates"][0] < "2009-01-01" or i.get("overs", 50) != 50: continue
        o = i.get("outcome", {})
        if "winner" not in o or "method" in o or len(m["innings"]) != 2: continue
        inns = [x for x in m["innings"] if not x.get("super_over")]
        if len(inns) != 2: continue
        win = o["winner"]; mid = os.path.basename(p)
        # first innings
        runs = w = ball = 0; st = []
        for ov in inns[0]["overs"]:
            for d in ov["deliveries"]:
                runs += d["runs"]["total"]; w += len(d.get("wickets", [])); ex = d.get("extras", {})
                if "wides" not in ex and "noballs" not in ex: ball += 1; st.append((runs, 300 - ball, w))
        total = runs
        for r, l, ww in st[::6]: first.append((r, l, ww, total, 1.0 if win == inns[0]["team"] else 0.0, mid))
        if total < 1: continue
        runs = w = ball = 0; target = total + 1
        for ov in inns[1]["overs"]:
            for d in ov["deliveries"]:
                runs += d["runs"]["total"]; w += len(d.get("wickets", [])); ex = d.get("extras", {})
                if "wides" not in ex and "noballs" not in ex:
                    ball += 1
                    if ball % 2 == 0: chase.append((target - runs, 300 - ball, w, 1.0 if win == inns[1]["team"] else 0.0, mid))
        chase.append((target, 300, 0, 1.0 if win == inns[1]["team"] else 0.0, mid))
        meta.append(mid)
    return chase, first, meta


class Model:
    def __init__(self, d): self.d = d; self.bc = np.array(d["chase"]); self.bf = np.array(d["first"]); self.sd = d["first_resid_sd_by_left"]

    def p_chase(self, need, left, w):
        need, left, w = map(lambda a: np.atleast_1d(np.asarray(a, float)), (need, left, w))
        p = 1 / (1 + np.exp(-np.clip(_chase_feats(need, left, w) @ self.bc, -30, 30)))
        return np.where(need <= 0, 1.0, np.where(left <= 0, 0.0, p))

    def proj(self, runs, left, w):
        return _first_feats(np.atleast_1d(np.asarray(runs, float)), left, np.atleast_1d(np.asarray(w, float))) @ self.bf

    def p_first(self, runs, left, w):
        """P(the side batting first wins)."""
        runs, left, w = map(lambda a: np.atleast_1d(np.asarray(a, float)), (runs, left, w))
        S = self.proj(runs, left, w); sd = np.interp(left, [0, 60, 120, 180, 240, 300], self.sd)
        z = np.array([-1.5, -.9, -.45, 0, .45, .9, 1.5]); wt = np.exp(-z ** 2 / 2); wt /= wt.sum(); out = np.zeros_like(S)
        for zi, wi in zip(z, wt):
            tot = np.maximum(S + zi * sd, runs + 0)                                    # final total can't be below the current score
            out += wi * (1 - self.p_chase(np.floor(tot) + 1, np.full_like(S, 300), np.zeros_like(S)))
        return out


def fit():
    chase, first, meta = rows(); ids = sorted(set(meta)); rng = np.random.RandomState(7); test = set(rng.choice(ids, size=max(1, len(ids) // 5), replace=False))
    ch = np.array([[r[0], r[1], r[2], r[3]] for r in chase]); chm = np.array([r[4] in test for r in chase])
    X = _chase_feats(ch[:, 0], ch[:, 1], ch[:, 2]); bc = _fit_logit(X[~chm], ch[~chm, 3])
    pt = 1 / (1 + np.exp(-np.clip(X[chm] @ bc, -30, 30))); yt = ch[chm, 3]
    ll = -np.mean(yt * np.log(np.clip(pt, 1e-6, 1)) + (1 - yt) * np.log(np.clip(1 - pt, 1e-6, 1))); acc = np.mean((pt > .5) == (yt > .5))
    bins = [(lo, hi, float(pt[(pt >= lo) & (pt < hi)].mean()), float(yt[(pt >= lo) & (pt < hi)].mean()), int(((pt >= lo) & (pt < hi)).sum())) for lo, hi in [(0, .1), (.1, .3), (.3, .5), (.5, .7), (.7, .9), (.9, 1.01)] if ((pt >= lo) & (pt < hi)).any()]
    bc_full = _fit_logit(X, ch[:, 3])
    fi = np.array([[r[0], r[1], r[2], r[3], r[4]] for r in first]); fim = np.array([r[5] in test for r in first])
    F = _first_feats(fi[:, 0], fi[:, 1], fi[:, 2]); A = F[~fim]; bfit = np.linalg.solve(A.T @ A + 1e-2 * np.eye(A.shape[1]), A.T @ fi[~fim, 3])
    res = fi[fim, 3] - F[fim] @ bfit; left_t = fi[fim, 1]
    sds = [float(np.std(res[(left_t >= lo) & (left_t < hi)])) if ((left_t >= lo) & (left_t < hi)).sum() > 30 else 40.0 for lo, hi in [(0, 30), (30, 90), (90, 150), (150, 210), (210, 270), (270, 301)]]
    bf_full = np.linalg.solve(F.T @ F + 1e-2 * np.eye(F.shape[1]), F.T @ fi[:, 3])
    d = {"chase": bc_full.tolist(), "first": bf_full.tolist(), "first_resid_sd_by_left": [sds[5], sds[4], sds[3], sds[2], sds[1], sds[0]][::-1] if False else [sds[0], sds[1], sds[2], sds[3], sds[4], sds[5]],
         "trained_on": {"matches": len(ids), "chase_states": int(len(chase)), "first_states": int(len(first)), "from": "2009-01-01", "source": "Cricsheet men's ODIs, 50 overs, no rain method (archive sample)"},
         "validation": {"chase_log_loss": float(ll), "chase_accuracy": float(acc), "chase_calibration": bins, "first_mae_runs": float(np.mean(np.abs(res))), "held_out_matches": len(test)}}
    os.makedirs(os.path.dirname(PATH), exist_ok=True); json.dump(d, open(PATH, "w"), indent=1)
    print(json.dumps(d["trained_on"])); print("chase: log loss %.3f, accuracy %.3f (held-out matches %d)" % (ll, acc, len(test)))
    for b in bins: print("  predicted %.2f-%.2f: mean predicted %.3f, actual %.3f (n=%d)" % (b[0], b[1], b[2], b[3], b[4]))
    print("first innings: projection MAE %.1f runs; residual sd by balls left (0-300):" % d["validation"]["first_mae_runs"], [round(x, 1) for x in sds])
    return d


def load():
    if not os.path.exists(PATH): fit()
    return Model(json.load(open(PATH)))


if __name__ == "__main__":
    if sys.argv[1:2] == ["fit"]: fit()
    else:
        M = load(); print("P(chase wins) 210 to win, start:", float(M.p_chase(210, 300, 0)[0]))
