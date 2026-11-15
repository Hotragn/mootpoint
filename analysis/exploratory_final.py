"""Exploratory (final audit, after test was analysed; not pre-registered).

1. Contradiction counting: score = number of a pair's descriptions that CONTRADICT the N1 claim. Tests whether opposed
   descriptions disagree by contradiction (then this signal would work) or by silence (then it would not).
2. Same-model ceiling: glm-5.2 reading the case file (runs/<split>/vfile_strong.jsonl) against glm-5.2 closed-book
   (runs/<split>/xf_strong.jsonl, from harness/xf_strong.py).
Same dossier-cluster bootstrap and seed as the frozen analysis. Writes analysis/results/<split>/exploratory_final.json.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze import N_BOOT, SEED, Boot, describe  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
KEY = ["dossier_id", "model", "claim_id"]


def main(split, n_boot=N_BOOT):
    res = ROOT / "analysis" / "results" / split
    S = pd.read_csv(res / "per_claim_signals.csv")
    for f in ("xf_strong.jsonl", "vfile_strong.jsonl"):
        S = S.merge(pd.read_json(ROOT / "runs" / split / f, lines=True), on=KEY, how="left")
    assert len(S) and S["y"].sum() > 0, "empty unit"
    y, D = S["y"].to_numpy().astype(int), S["dossier_id"].to_numpy()
    bt = Boot(sorted(set(D)), n_boot, SEED)
    allm = np.ones(len(S), bool)
    out = {"note": "exploratory, added in the final audit after test analysis", "n_claims": len(S),
           "n_unwarranted": int(y.sum()), "contradiction_counting": {}, "contradiction_rate": {}}
    A = {}
    for p in ("OPP", "SC", "DIV", "SAME"):
        A[p] = bt.auroc(D, y, S[f"contra_{p}"].to_numpy().astype(float), allm)
        out["contradiction_counting"][p] = describe(A[p])
        c = S[f"contra_{p}"] > 0
        out["contradiction_rate"][p] = {"warranted": float(c[S.y == 0].mean()), "unwarranted": float(c[S.y == 1].mean())}
    out["contradiction_counting"]["OPP_minus_SC"] = describe(A["OPP"] - A["SC"], ci90=True)
    both = allm & S["xs_none"].notna().to_numpy() & S["vs_file"].notna().to_numpy()
    R = {c: bt.auroc(D, y, S[c].to_numpy().astype(float), both) for c in ("xs_none", "xs_opp", "vs_file")}
    out["glm52"] = {c: describe(R[c]) for c in R}
    out["glm52"]["vs_file_minus_xs_none"] = describe(R["vs_file"] - R["xs_none"], ci90=True)
    out["glm52"]["vs_file_minus_xs_opp"] = describe(R["vs_file"] - R["xs_opp"], ci90=True)
    out["glm52"]["n_claims"] = int(both.sum())
    (res / "exploratory_final.json").write_text(json.dumps(out, indent=2))
    print(json.dumps({k: {kk: round(vv["estimate"], 3) if isinstance(vv, dict) and "estimate" in vv else vv
                          for kk, vv in v.items()} if isinstance(v, dict) else v for k, v in out.items()}, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="test")
    ap.add_argument("--n-boot", type=int, default=N_BOOT)
    a = ap.parse_args()
    main(a.split, a.n_boot)
