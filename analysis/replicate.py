"""Exploratory (Sun Nov 15, after test): does an independent rerun of every test description reproduce the results?

runs/test_r1 regenerates all descriptions (fresh samples) and relabels them with the same judges; analyze.py and
readers.py run unchanged. This script puts the headline numbers of both runs side by side.
Usage: .venv/bin/python analysis/replicate.py  -> analysis/results/test_r1/replicate_compare.json
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1] / "analysis" / "results"
est = lambda d: {k: round(d[k], 3) for k in ("estimate", "ci95_low", "ci95_high")}


def summary(run):
    R = json.loads((ROOT / run / "results.json").read_text())
    Q = json.loads((ROOT / run / "readers.json").read_text())
    S = pd.read_csv(ROOT / run / "per_claim_signals.csv")
    w = S.y == 0
    out = {"N1_claims": R["n"]["N1_claims"], "N1_unwarranted": R["n"]["N1_unwarranted"],
           "cells_complete": R["n"]["cells_complete"]}
    out["auroc"] = {k: est(v) for k, v in R["auroc"].items()}
    out["auroc"].update({k: est(Q["descriptive"]["auroc"][k]) for k in ("v_closed_none", "v_closed", "v_closed_div")})
    out["tests"] = {k: dict(est(v), supported=v["supported"]) for k, v in {**R["confirmatory"], **Q["confirmatory_F2"]}.items()
                    if isinstance(v, dict) and "supported" in v}
    out["OPP_SC_side_taking_positives"] = est(Q["secondary_OPP_minus_SC_side_taking_positives"])
    out["warranted_repeated_by_both"] = {"OPP": round(float((S.k_OPP[w] == 2).mean()), 3),
                                         "SC": round(float((S.k_SC[w] == 2).mean()), 3)}
    out["unwarranted_repeated_by_both"] = {"OPP": int((S.k_OPP[~w] == 2).sum()), "SC": int((S.k_SC[~w] == 2).sum())}
    return out


if __name__ == "__main__":
    a, b = summary("test"), summary("test_r1")
    same = {t: a["tests"][t]["supported"] == b["tests"][t]["supported"] for t in a["tests"]}
    assert set(a["tests"]) == set(b["tests"]) == {"H1a", "H2", "H3", "R1", "R2", "R3"}
    out = {"note": "exploratory, after test; independent regeneration of all test descriptions",
           "test": a, "test_r1": b, "same_decision": same}
    (ROOT / "test_r1" / "replicate_compare.json").write_text(json.dumps(out, indent=2))
    for t in a["tests"]:
        print(t, a["tests"][t], "|", b["tests"][t])
    print("same decision on every test:", all(same.values()))
