"""Exploratory (Sun Nov 15, after test): do the counting results survive a second presence matcher?

Recomputes k_X for OPP (A,B), SC (N2,N3), DIV (P1,P2), SAME (A,A2) from runs/<split>/presence_glm52.jsonl
(glm-5.2, a different family from the main matcher qwen3.5-397b), on the same N1 claims and labels, and reports:
AUROC of 2 - k_X, paired ΔAUROC OPP − SC and OPP − DIV, the warranted-claim omission / contradiction rates by
pair, and cell-level agreement between the two matchers (Cohen's κ over ASSERTS/SILENT/CONTRADICTS).
Dossier-cluster bootstrap from the frozen analysis (10,000 resamples, seed 20261114).
Usage: .venv/bin/python analysis/matcher2.py --split test  -> analysis/results/<split>/matcher2.json
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze import N_BOOT, SEED, Boot, describe  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
KEY = ["dossier_id", "model", "claim_id"]
PAIRS = {"OPP": ("A", "B"), "SC": ("N2", "N3"), "DIV": ("P1", "P2"), "SAME": ("A", "A2")}


def kappa(a, b):
    cats = sorted(set(a) | set(b))
    po = float(np.mean(a == b))
    pe = sum(float(np.mean(a == c)) * float(np.mean(b == c)) for c in cats)
    return (po - pe) / (1 - pe)


def main(split):
    res = ROOT / "analysis" / "results" / split
    S = pd.read_csv(res / "per_claim_signals.csv")[KEY + ["y", "label"]]
    P2 = pd.read_json(ROOT / "runs" / split / "presence_glm52.jsonl", lines=True)
    P1 = pd.read_json(ROOT / "runs" / split / "presence.jsonl", lines=True)
    W = P2.pivot_table(index=KEY, columns="framing", values="verdict", aggfunc="first").reset_index()
    S = S.merge(W, on=KEY, how="inner")
    assert len(S) > 1000, "too few claims joined"
    out = {"note": "exploratory, after test; second matcher glm-5.2", "n_claims": len(S), "n_unwarranted": int(S.y.sum())}
    D, y = S["dossier_id"].to_numpy(), S["y"].to_numpy(int)
    bt = Boot(sorted(set(D)), N_BOOT, SEED)
    A, rates = {}, {}
    for p, (f1, f2) in PAIRS.items():
        k = (S[f1] == "ASSERTS").astype(int) + (S[f2] == "ASSERTS").astype(int)
        A[p] = bt.auroc(D, y, (2 - k).to_numpy(float))
        both = k == 2
        contra = (S[f1] == "CONTRADICTS") | (S[f2] == "CONTRADICTS")
        warr = S.y == 0
        rates[p] = dict(warranted_repeated_by_both=float(both[warr].mean()),
                        warranted_contradicted_by_either=float(contra[warr].mean()),
                        unwarranted_repeated_by_both=float(both[~warr].mean()))
    out["auroc"] = {p: describe(a) for p, a in A.items()}
    out["delta"] = {"OPP_SC": describe(A["OPP"] - A["SC"], ci90=True), "OPP_DIV": describe(A["OPP"] - A["DIV"], ci90=True)}
    out["rates"] = rates
    M = P1.merge(P2, on=KEY + ["framing"], suffixes=("_qwen", "_glm"))
    out["matcher_agreement"] = {"n_cells": len(M), "agreement": float((M.verdict_qwen == M.verdict_glm).mean()),
                                "kappa": kappa(M.verdict_qwen.to_numpy(), M.verdict_glm.to_numpy())}
    (res / "matcher2.json").write_text(json.dumps(out, indent=2))
    f = lambda d: f"{d['estimate']:.3f} [{d['ci95_low']:.3f}, {d['ci95_high']:.3f}]"
    print({p: f(v) for p, v in out["auroc"].items()})
    print({p: f(v) for p, v in out["delta"].items()})
    print({p: {k: round(v, 3) for k, v in r.items()} for p, r in rates.items()})
    print(out["matcher_agreement"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="test")
    main(ap.parse_args().split)
