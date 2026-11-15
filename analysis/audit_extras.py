"""Exploratory analyses added in the audit (after test was analysed; NOT pre-registered).

- trivial baselines: random score, claim length, evaluative-word count;
- strong cross-family reader (glm-5.2, runs/<split>/xf_strong.jsonl) vs the qwen reader, on judge and judge2 labels.
Uses the frozen analysis's dossier-cluster bootstrap (analyze.Boot, 10,000 resamples, seed 20261114).
Usage: .venv/bin/python analysis/audit_extras.py --split test   -> analysis/results/<split>/audit_extras.json
"""
import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze import N_BOOT, SEED, UNWARRANTED, Boot, describe  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
KEY = ["dossier_id", "model", "claim_id"]
EVAL = re.compile(r"\b(suggest|indicat|appear|likely|clearly|deliberat|negligen|fail|ignor|demonstrat|reckless|"
                  r"unlawful|excessive|proves?)\w*", re.I)


def main(split):
    res_dir = ROOT / "analysis" / "results" / split
    S = pd.read_csv(res_dir / "per_claim_signals.csv")
    C = pd.read_json(ROOT / "runs" / split / "claims.jsonl", lines=True)
    S = S.merge(C[KEY + ["text"]], on=KEY, how="left")
    V = pd.read_json(ROOT / "runs" / split / "verifiers.jsonl", lines=True)
    S = S.drop(columns=[c for c in V.columns if c in S.columns and c not in KEY]).merge(V, on=KEY, how="left")
    xs = ROOT / "runs" / split / "xf_strong.jsonl"
    if xs.exists():
        S = S.merge(pd.read_json(xs, lines=True), on=KEY, how="left")
    J = pd.read_json(ROOT / "runs" / split / "judge2.jsonl", lines=True)
    S = S.drop(columns=[c for c in ("label2", "y2") if c in S.columns]).merge(J[KEY + ["label2"]], on=KEY, how="left")
    assert len(S) and S["text"].notna().all(), "claims did not join"

    rng = np.random.default_rng(SEED)
    score = {"random": rng.random(len(S)), "length_words": S["text"].str.split().str.len().to_numpy(float),
             "evaluative_words": S["text"].str.count(EVAL).to_numpy(float), "SC": (2 - S["k_SC"]).to_numpy(float)}
    for c in ("v_closed", "v_closed_none", "xs_none", "xs_opp"):
        if c in S:
            score[c] = S[c].to_numpy(float)

    D = S["dossier_id"].to_numpy()
    bt = Boot(sorted(set(D)), N_BOOT, SEED)
    y = S["y"].to_numpy(int)
    y2 = S["label2"].isin(UNWARRANTED).to_numpy(int)
    has2 = S["label2"].notna().to_numpy()
    out = {"note": "exploratory, added in audit after test analysis", "n_claims": len(S), "n_unwarranted": int(y.sum())}
    for name, yy, base in (("judge_labels", y, np.ones(len(S), bool)), ("judge2_labels", y2, has2)):
        blk, A = {}, {}
        for s, v in score.items():
            m = base & np.isfinite(v)
            A[s] = bt.auroc(D, yy, v, m)
            blk[s] = dict(describe(A[s]), n=int(m.sum()))
        if "xs_none" in A:
            both = base & np.isfinite(score["xs_none"]) & np.isfinite(score["xs_opp"])
            blk["delta_xs_opp_minus_xs_none"] = describe(bt.auroc(D, yy, score["xs_opp"], both)
                                                         - bt.auroc(D, yy, score["xs_none"], both), ci90=True)
            blk["delta_xs_none_minus_SC"] = describe(A["xs_none"] - A["SC"], ci90=True)
        out[name] = blk
    out["xs_coverage_claims"] = int(np.isfinite(score.get("xs_none", np.array([np.nan]))).sum())
    (res_dir / "audit_extras.json").write_text(json.dumps(out, indent=2))
    for name in ("judge_labels", "judge2_labels"):
        print(name, {k: round(v["estimate"], 3) for k, v in out[name].items() if "estimate" in v})


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="test")
    main(ap.parse_args().split)
