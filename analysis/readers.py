"""Pre-registered family F2, reading vs counting (PLAN.md "v4 additions").

Usage:
    python analysis/readers.py --claims runs/<split>/claims.jsonl \
        --signals analysis/results/<split>/per_claim_signals.csv --out analysis/results/<split>/

Inputs, read from the claims file's directory unless overridden:
- verifiers.jsonl (required): one row per N1 claim with v_closed, v_closed_none and v_closed_div, which are required
  in every row, plus the descriptive columns v_file, v_closed_sc, v_closed_debate, xf_none and xf_opp. A descriptive
  column is either present in every row or absent from the file. All values are numbers in [0, 1].
- judge2.jsonl (optional).
--signals is the frozen analyze.py output. Its results.json must carry analyze.py sha256 8135fa2c... and the sha256
of this claims file.

Unit: N1 claims in cells that are complete under analyze.py's rule (the rows of per_claim_signals.csv) and whose
every N1 claim has a verifiers.jsonl row. Other complete cells are dropped and counted.
k_SC is recomputed from the N2 and N3 verdicts and must match the frozen k_SC.

F2 (one-sided; Holm within F2; dossier-cluster bootstrap with analyze.py's Boot, 10,000 resamples, seed 20261114):
    R1 = AUROC(v_closed_none) - AUROC(2 - k_SC)
    R2 = AUROC(v_closed) - AUROC(v_closed_none)        (+ TOST at +-0.03 via the 90% CI)
    R3 = AUROC(v_closed) - AUROC(v_closed_div)         (+ TOST at +-0.03 via the 90% CI)
Descriptive: every reader's AUROC, xf_opp - xf_none, everything re-scored on judge2 labels and on judge-agreed
claims, per generator, and OPP - SC with SIDE_TAKING positives only (two-sided).
Any schema violation raises InputError (exit code 2).
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze import (ALPHA, LABELS, N_BOOT, SEED, TOST_MARGIN, UNWARRANTED, VERDICTS, Boot, InputError,  # noqa: E402
                     _fail, _need, _no_dups, _num, describe, holm, load_jsonl, sha256)

FROZEN_ANALYZE = "8135fa2c52e5bcd013595769a4c0201aab2efd028f2bdf376ffc1fa1e7eef1e3"
KEY = ["dossier_id", "model", "claim_id"]
REQUIRED = ["v_closed", "v_closed_none", "v_closed_div"]
DESCRIPTIVE = ["v_file", "v_closed_sc", "v_closed_debate", "xf_none", "xf_opp"]
F2 = {"R1": ("v_closed_none", "SC"), "R2": ("v_closed", "v_closed_none"), "R3": ("v_closed", "v_closed_div")}
TOST_FOR = ("R2", "R3")
SIGNAL_COLS = ["dossier_id", "model", "claim_id", "framing", "label", "y", "k_OPP", "k_SC", "k_DIV", "N2", "N3"]


# ================================================================ loading and validation

def _scores(rows, cols, path, all_rows):
    """Each column in `cols` must be in every row (all_rows) or in none; values numbers in [0, 1]."""
    present = []
    for c in cols:
        n = sum(c in r for r in rows)
        if n == 0 and not all_rows:
            continue
        if n != len(rows):
            _fail(f"{path}: column {c} is in {n} of {len(rows)} rows; it must be in every row"
                  + ("" if all_rows else " or in none"))
        for i, r in enumerate(rows, 1):
            v = r[c]
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not 0 <= v <= 1:
                _fail(f"{path} row {i}: {c}={v!r} must be a number in [0, 1]")
        present.append(c)
    return present


def load_readers(path, n1keys):
    rows = load_jsonl(path)
    _need(rows, KEY, path)
    _scores(rows, REQUIRED, path, all_rows=True)
    cols = REQUIRED + _scores(rows, DESCRIPTIVE, path, all_rows=False)
    df = pd.DataFrame(rows)[KEY + cols]
    _no_dups(df, KEY, path)
    _refs(df, n1keys, path)
    return df, cols


def _refs(df, n1keys, path):
    bad = set(map(tuple, df[KEY].to_numpy())) - n1keys
    if bad:
        _fail(f"{path}: {len(bad)} row(s) refer to no N1 claim in the claims file, e.g. {sorted(bad)[:3]}")


def load_signals(path, claims_path, claims):
    path = Path(path)
    res_path = path.parent / "results.json"
    if not path.is_file():
        _fail(f"{path}: file not found")
    if not res_path.is_file():
        _fail(f"{res_path}: not found; the signals must come with the frozen analyze.py's results.json")
    meta = json.loads(res_path.read_text())["meta"]
    if meta.get("analyze_py_sha256") != FROZEN_ANALYZE:
        _fail(f"{res_path}: analyze.py sha256 {meta.get('analyze_py_sha256')} is not the frozen {FROZEN_ANALYZE}")
    if (meta.get("files", {}).get("claims") or {}).get("sha256") != sha256(claims_path):
        _fail(f"{res_path}: the signals were computed from a different claims file than {claims_path}")
    S = pd.read_csv(path, dtype={"dossier_id": str, "model": str, "claim_id": str})
    miss = [c for c in SIGNAL_COLS if c not in S.columns]
    if miss:
        _fail(f"{path}: missing columns {miss}")
    if S.empty:
        _fail(f"{path}: no rows")
    _no_dups(S, KEY, path)
    if (S["framing"] != "N1").any():
        _fail(f"{path}: rows with framing other than N1")
    for f in ("N2", "N3"):
        if not S[f].isin(VERDICTS).all():
            _fail(f"{path}: {f} holds values outside {sorted(VERDICTS)}")
    k_sc = (S["N2"] == "ASSERTS").astype(int) + (S["N3"] == "ASSERTS").astype(int)
    if (k_sc != S["k_SC"]).any():
        _fail(f"{path}: k_SC does not equal the number of ASSERTS in N2 and N3 for {(k_sc != S['k_SC']).sum()} rows")
    if (S["y"] != S["label"].isin(UNWARRANTED).astype(int)).any():
        _fail(f"{path}: y disagrees with label")
    lab = claims.set_index(KEY)["label"]
    joined = S.join(lab.rename("label_claims"), on=KEY)
    if joined["label_claims"].isna().any():
        _fail(f"{path}: rows not found among the N1 claims of {claims_path}")
    if (joined["label_claims"] != S["label"]).any():
        _fail(f"{path}: labels disagree with {claims_path}")
    return S[SIGNAL_COLS]  # reader scores and label2 come from verifiers.jsonl and judge2.jsonl, not the CSV


def load_judge2(path, n1keys):
    rows = load_jsonl(path, required=False)
    if rows is None:
        return None
    _need(rows, KEY + ["label2"], path)
    for i, r in enumerate(rows, 1):
        if r["label2"] not in LABELS:
            _fail(f"{path} row {i}: label2 {r['label2']!r} not in {sorted(LABELS)}")
    df = pd.DataFrame(rows)[KEY + ["label2"]]
    _no_dups(df, KEY, path)
    _refs(df, n1keys, path)
    return df


def build_unit(claims_path, signals_path, verifiers_path=None, judge2_path=None):
    claims_path = Path(claims_path)
    base = claims_path.parent
    verifiers_path = Path(verifiers_path or base / "verifiers.jsonl")
    judge2_path = Path(judge2_path or base / "judge2.jsonl")
    rows = load_jsonl(claims_path)
    _need(rows, ["dossier_id", "model", "framing", "claim_id", "label", "split"], claims_path)
    claims = pd.DataFrame(rows)
    n1 = claims[claims["framing"] == "N1"]
    n1keys = set(map(tuple, n1[KEY].to_numpy()))
    S = load_signals(signals_path, claims_path, n1)
    V, cols = load_readers(verifiers_path, n1keys)
    J = load_judge2(judge2_path, n1keys)

    S = S.merge(V, on=KEY, how="left")
    has = S.groupby(["dossier_id", "model"])["v_closed"].agg(lambda s: (s.notna().all(), s.notna().any()))
    cells = pd.DataFrame(has.tolist(), index=has.index, columns=["all", "any"])
    keep = set(cells.index[cells["all"]])
    dropped = [{"dossier_id": d, "model": m, "reason": "some N1 claims lack verifier rows" if cells.loc[(d, m), "any"]
                else "no verifier rows"} for d, m in cells.index[~cells["all"]]]
    T = S[pd.Series(list(zip(S["dossier_id"], S["model"])), index=S.index).isin(keep)].reset_index(drop=True)
    if T.empty:
        _fail("no complete cell has verifier rows for all its N1 claims: nothing to analyse")
    if J is not None:
        T = T.drop(columns=[c for c in ("label2", "y2") if c in T.columns]).merge(J, on=KEY, how="left")
        T["y2"] = np.where(T["label2"].isna(), np.nan, T["label2"].isin(UNWARRANTED).astype(float))
    else:
        T["label2"], T["y2"] = None, np.nan
    info = {"split": str(claims["split"].iloc[0]), "reader_columns": cols,
            "reader_columns_absent": [c for c in DESCRIPTIVE if c not in cols],
            "cells_complete": len(cells), "cells_analysed": len(keep), "cells_dropped_no_verifier_rows": dropped,
            "files": {k: {"path": str(p), "sha256": sha256(p)} if Path(p).is_file() else None for k, p in
                      [("claims", claims_path), ("signals", Path(signals_path)), ("verifiers", verifiers_path),
                       ("judge2", judge2_path)]}}
    return T, info


# ================================================================ statistics

def _two_sided(arr):
    b = arr[1:][np.isfinite(arr[1:])]
    return _num(min(1.0, 2 * min((1 + (b <= 0).sum()), (1 + (b >= 0).sum())) / (b.size + 1))) if b.size else None


def compute(T, cols, n_boot=N_BOOT, seed=SEED):
    """T: unit table with dossier_id, model, label, y, y2, k_OPP, k_SC, k_DIV and the reader columns in `cols`."""
    y = T["y"].to_numpy().astype(int)
    if y.sum() == 0 or (y == 0).sum() == 0:
        _fail("the unit contains only one outcome class; AUROC undefined")
    bt = Boot(sorted(T["dossier_id"].unique()), n_boot, seed)
    D = T["dossier_id"].to_numpy()
    score = {p: (2 - T[f"k_{p}"]).to_numpy().astype(float) for p in ("OPP", "SC", "DIV")}
    score.update({c: T[c].to_numpy().astype(float) for c in cols})
    sigs = ["SC", "OPP", "DIV", *cols]
    y2 = T["y2"].to_numpy().astype(float)
    k2 = np.isfinite(y2)
    models, labels = T["model"].to_numpy(), T["label"].to_numpy()

    def block(yy, mask):
        """AUROC of every signal and the F2 deltas, on outcome yy over claims in mask."""
        A = {s: bt.auroc(D, yy, score[s], mask) for s in sigs}
        out = {"N1_claims": int(mask.sum()), "N1_unwarranted": int(yy[mask].sum()),
               "auroc": {s: dict(describe(A[s]), n=int((mask & np.isfinite(score[s])).sum())) for s in sigs},
               "delta": {k: describe(A[a] - A[b], one_sided=True, ci90=True) for k, (a, b) in F2.items()}}
        if "xf_none" in cols and "xf_opp" in cols:
            both = mask & np.isfinite(score["xf_none"]) & np.isfinite(score["xf_opp"])
            dx = bt.auroc(D, yy, score["xf_opp"], both) - bt.auroc(D, yy, score["xf_none"], both)
            out["xf_opp_minus_xf_none"] = dict(describe(dx, ci90=True), p_two_sided=_two_sided(dx),
                                               n=int(both.sum()))
        return out, A

    allm = np.ones(len(T), bool)
    main_block, A = block(y, allm)
    fam = {k: A[a] - A[b] for k, (a, b) in F2.items()}
    d = main_block["delta"]
    raw = {k: d[k]["p_one_sided"] if d[k]["p_one_sided"] is not None else 1.0 for k in F2}
    adj, rank = holm(raw)
    conf = {}
    for k, (a, b) in F2.items():
        lvl = ALPHA / (len(F2) - rank[k])
        bs = fam[k][1:][np.isfinite(fam[k][1:])]
        c = dict(d[k], definition=f"AUROC({a}) - AUROC({b})", p_holm=adj[k], holm_rank=rank[k] + 1, holm_alpha=lvl,
                 holm_one_sided_lower=_num(np.percentile(bs, 100 * lvl)) if bs.size else None,
                 holm_one_sided_level=1 - lvl, supported=bool(adj[k] < ALPHA))
        if k in TOST_FOR:
            c["tost_equivalent_within_0.03"] = bool(c["ci90_low"] is not None and c["ci90_low"] > -TOST_MARGIN
                                                    and c["ci90_high"] < TOST_MARGIN)
        conf[k] = c

    st = (y == 0) | (labels == "SIDE_TAKING")  # analyze.py's per-error-type mask
    st_delta = bt.auroc(D, y, score["OPP"], st) - bt.auroc(D, y, score["SC"], st)
    res = {
        "n": {"N1_claims": len(T), "N1_unwarranted": int(y.sum()), "dossiers": int(len(set(D))),
              "N1_with_label2": int(k2.sum()), "by_model": {m: int((models == m).sum()) for m in sorted(set(models))}},
        "confirmatory_F2": conf,
        "descriptive": main_block,
        "secondary_OPP_minus_SC_side_taking_positives": dict(
            describe(st_delta, ci90=True), p_two_sided=_two_sided(st_delta), N1_claims=int(st.sum()),
            N1_side_taking=int((labels == "SIDE_TAKING").sum()),
            note="positives restricted to SIDE_TAKING, all y = 0 kept (analyze.py per_error_type mask); "
                 "pre-registered prediction: < 0; reported two-sided"),
        "judge2_labels": block(np.where(k2, y2, 0).astype(int), k2)[0] if k2.any() else None,
        "judge_agreed": block(y, k2 & (y2 == y))[0] if k2.any() else None,
        "per_model": {m: block(y, models == m)[0] for m in sorted(set(models))},
    }
    return res


def analyze_readers(claims_path, signals_path, out_dir=None, verifiers_path=None, judge2_path=None,
                    n_boot=N_BOOT, seed=SEED):
    T, info = build_unit(claims_path, signals_path, verifiers_path, judge2_path)
    if info["cells_dropped_no_verifier_rows"]:
        print(f"WARNING: {len(info['cells_dropped_no_verifier_rows'])} complete cell(s) dropped for lacking "
              f"verifier rows; see readers.json", file=sys.stderr)
    res = compute(T, info["reader_columns"], n_boot, seed)
    res["meta"] = {"n_boot": n_boot, "seed": seed, "alpha": ALPHA, "tost_margin": TOST_MARGIN,
                   "readers_py_sha256": sha256(__file__), "frozen_analyze_py_sha256": FROZEN_ANALYZE,
                   "score": "readers: the probability as given; counting signals: 2 - k_X; AUROC ties count 1/2",
                   "decision": "supported iff Holm-adjusted one-sided p < 0.05 over {R1, R2, R3}", **info}
    res["n"]["cells_complete"] = info["cells_complete"]
    res["n"]["cells_analysed"] = info["cells_analysed"]
    res["n"]["cells_dropped_no_verifier_rows"] = len(info["cells_dropped_no_verifier_rows"])
    if out_dir is not None:
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / "readers.json").write_text(json.dumps(res, indent=2))
        pd.DataFrame(_flatten(res)).to_csv(out / "readers.csv", index=False)
    return res


def _flatten(d, path=""):
    """One CSV row per statistic (any dict holding an 'estimate')."""
    if isinstance(d, dict) and "estimate" in d:
        return [{"stat": path, **{k: v for k, v in d.items() if not isinstance(v, (dict, list))}}]
    if isinstance(d, dict):
        return [r for k, v in d.items() if k != "meta" for r in _flatten(v, f"{path}.{k}" if path else k)]
    return []


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--claims", required=True)
    ap.add_argument("--signals", required=True)
    ap.add_argument("--out", required=True)
    for f in ("verifiers", "judge2"):
        ap.add_argument(f"--{f}", default=None)
    ap.add_argument("--n-boot", type=int, default=N_BOOT)
    a = ap.parse_args(argv)
    try:
        res = analyze_readers(a.claims, a.signals, a.out, a.verifiers, a.judge2, a.n_boot)
    except InputError as e:
        print(f"INPUT ERROR: {e}", file=sys.stderr)
        return 2
    print(json.dumps({"n": res["n"], "confirmatory_F2": res["confirmatory_F2"]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
