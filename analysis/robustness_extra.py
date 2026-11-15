"""Exploratory robustness checks added on Sun Nov 15 (after test; NOT pre-registered). No new model calls.

1. Loaded language: detector AUROC on N1 claims that contain no evaluative word (audit_extras.EVAL lexicon).
2. Error type: AUROC with positives restricted to SIDE_TAKING, or to UNSUPPORTED_FACT (all warranted claims kept).
3. Flag budget: if a reviewer checks only the top 10% / 20% of N1 claims by a detector's score, the share of
   unwarranted claims caught (recall) and the share of flags that are unwarranted (precision).
4. Per domain: AUROC of SC, OPP and the strong readers in each of the four domains.
Usage: .venv/bin/python analysis/robustness_extra.py --split test [--run test_r1]
       -> analysis/results/<run>/robustness_extra.json
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze import N_BOOT, SEED, Boot, describe  # noqa: E402
from audit_extras import EVAL, KEY  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DETECTORS = ["SC", "OPP", "DIV", "v_closed_none", "v_closed", "xs_none"]


def load(run):
    res = ROOT / "analysis" / "results" / run
    S = pd.read_csv(res / "per_claim_signals.csv")
    C = pd.read_json(ROOT / "runs" / run / "claims.jsonl", lines=True)
    S = S.merge(C[KEY + ["text"]], on=KEY, how="left")
    V = pd.read_json(ROOT / "runs" / run / "verifiers.jsonl", lines=True)
    S = S.drop(columns=[c for c in V.columns if c in S.columns and c not in KEY]).merge(V, on=KEY, how="left")
    xs = ROOT / "runs" / run / "xf_strong.jsonl"
    if xs.exists():
        S = S.merge(pd.read_json(xs, lines=True), on=KEY, how="left")
    assert len(S) and S["text"].notna().all(), "claims did not join"
    for p in ("SC", "OPP", "DIV"):
        S[p] = 2 - S[f"k_{p}"]
    return S, res


def flag_budget(S, score, frac, rng):
    """Flag the top `frac` of claims by score (random tie-break); return recall and precision."""
    v = S[score].to_numpy(float)
    m = np.isfinite(v)
    v, y = v[m], S["y"].to_numpy(int)[m]
    order = np.lexsort((rng.random(len(v)), -v))
    k = int(round(frac * len(v)))
    flagged = np.zeros(len(v), bool)
    flagged[order[:k]] = True
    return dict(recall=float(flagged[y == 1].mean()), precision=float(y[flagged].mean()), n=int(len(v)), k=k)


def main(run):
    S, res = load(run)
    D = S["dossier_id"].to_numpy()
    bt = Boot(sorted(set(D)), N_BOOT, SEED)
    y = S["y"].to_numpy(int)
    dets = [d for d in DETECTORS if d in S]
    out = {"note": "exploratory, added after test (Sun Nov 15); no new model calls", "run": run,
           "n_claims": len(S), "n_unwarranted": int(y.sum())}

    def aurocs(mask, yy):
        blk = {}
        for d in dets:
            v = S[d].to_numpy(float)
            m = mask & np.isfinite(v)
            blk[d] = dict(describe(bt.auroc(D, yy, v, m)), n=int(m.sum()), n_pos=int(yy[m].sum()))
        return blk

    no_eval = (S["text"].str.count(EVAL) == 0).to_numpy()
    out["no_evaluative_words"] = aurocs(no_eval, y)
    out["no_evaluative_words"]["share_of_claims"] = float(no_eval.mean())
    out["no_evaluative_words"]["share_of_unwarranted"] = float(no_eval[y == 1].mean())
    for lab in ("SIDE_TAKING", "UNSUPPORTED_FACT"):
        keep = ((S["label"] == lab) | (S["y"] == 0)).to_numpy()
        out[f"positives_{lab}"] = aurocs(keep, ((S["label"] == lab).to_numpy() & keep).astype(int))
    rng = np.random.default_rng(SEED)
    out["flag_budget"] = {f"top_{int(f * 100)}pct": {d: flag_budget(S, d, f, rng) for d in dets} for f in (0.10, 0.20)}
    out["per_domain"] = {}
    for dom in sorted(S["domain"].unique()):
        m = (S["domain"] == dom).to_numpy()
        out["per_domain"][dom] = {d: dict(describe(bt.auroc(D, y, S[d].to_numpy(float), m & np.isfinite(S[d].to_numpy(float)))),
                                          n_pos=int(y[m].sum())) for d in dets}
        out["per_domain"][dom]["OPP_minus_SC"] = describe(bt.auroc(D, y, S["OPP"].to_numpy(float), m)
                                                          - bt.auroc(D, y, S["SC"].to_numpy(float), m))
    assert out["n_unwarranted"] > 0 and out["no_evaluative_words"]["SC"]["n"] > 0
    (res / "robustness_extra.json").write_text(json.dumps(out, indent=2))
    show = lambda b: {k: round(v["estimate"], 3) for k, v in b.items() if isinstance(v, dict) and "estimate" in v}
    print("no evaluative words:", show(out["no_evaluative_words"]),
          "share claims", round(out["no_evaluative_words"]["share_of_claims"], 3),
          "share unwarranted", round(out["no_evaluative_words"]["share_of_unwarranted"], 3))
    for lab in ("SIDE_TAKING", "UNSUPPORTED_FACT"):
        print(lab, show(out[f"positives_{lab}"]))
    for f, blk in out["flag_budget"].items():
        print(f, {d: (round(v["recall"], 3), round(v["precision"], 3)) for d, v in blk.items()})
    for dom, blk in out["per_domain"].items():
        print(dom, show(blk))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="test")
    ap.add_argument("--run", help="results/run folder (default: the split)")
    a = ap.parse_args()
    main(a.run or a.split)
