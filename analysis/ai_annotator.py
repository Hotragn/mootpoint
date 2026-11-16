"""Exploratory (Sun Nov 15, after test): agreement of a third-family AI annotator with both judges.

analysis/human_labels/ai_labels.csv holds W/U labels from Codex (GPT-6) on the pre-registered 100-claim sheet
(50 judge-unwarranted, 50 judge-warranted). It is NOT human validation. Its files were hash-frozen before the
key was opened (verify_ai_labels.py). Abstentions are dropped. κ interval: dossier-cluster bootstrap.
Usage: .venv/bin/python analysis/ai_annotator.py  -> analysis/results/test/ai_annotator.json
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
H = ROOT / "analysis" / "human_labels"
UNW = {"SIDE_TAKING", "UNSUPPORTED_FACT"}


def kappa(x, z):
    po = float((x == z).mean())
    pe = x.mean() * z.mean() + (1 - x.mean()) * (1 - z.mean())
    return po, float((po - pe) / (1 - pe))


def main():
    M = pd.read_csv(H / "key_DO_NOT_OPEN_BEFORE_LABELLING.csv").merge(pd.read_csv(H / "ai_labels.csv"), on="item")
    assert len(M) == 100
    M = M[M.your_label.isin(["W", "U"])]
    a = (M.your_label == "U").astype(int).to_numpy()
    y1, y2 = M.y.to_numpy(int), M.label2.isin(UNW).astype(int).to_numpy()
    D = M.dossier_id.to_numpy()
    rng, ks = np.random.default_rng(20261114), []
    for _ in range(10000):
        idx = np.concatenate([np.where(D == d)[0] for d in rng.choice(np.unique(D), len(np.unique(D)))])
        if a[idx].std() > 0 and y1[idx].std() > 0:
            ks.append(kappa(a[idx], y1[idx])[1])
    out = {"note": "exploratory; Codex (GPT-6) AI annotator, not human labels", "n": int(len(M)), "abstained": 100 - int(len(M))}
    for name, z in (("judge", y1), ("judge2", y2)):
        po, k = kappa(a, z)
        out[name] = {"agreement": po, "kappa": k}
    out["judge"]["kappa_ci95"] = [float(v) for v in np.percentile(ks, [2.5, 97.5])]
    po, k = kappa(y1, y2)
    out["judge_vs_judge2_same_items"] = {"agreement": po, "kappa": k}
    out["ai_W_on_judge_label"] = {l: int(((M.label == l) & (a == 0)).sum()) for l in sorted(M.label.unique())}
    (ROOT / "analysis" / "results" / "test" / "ai_annotator.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
