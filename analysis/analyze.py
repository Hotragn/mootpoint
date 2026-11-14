"""Pre-registered analysis for the against-interest agreement study (PLAN.md, pre-registration v3).

Usage:
    python analysis/analyze.py --claims runs/<split>/claims.jsonl --dossiers data/dossiers \
        --out analysis/results/<split>/

The other inputs are read from the claims file's directory (override with flags):
    descriptions.jsonl (required), presence.jsonl (required), verifiers.jsonl (optional), judge2.jsonl (optional).

Every number the paper may cite goes to results.json; tables go to CSV; the frontier figure to figures/.
Any schema violation raises InputError (exit code 2): nothing is silently dropped. Incomplete dossier x model
cells are excluded from every analysis and listed in excluded_cells.csv and results.json.

Signals: for N1 claim c and pair X, k_X = number of X's two descriptions whose presence verdict is ASSERTS.
Suspicion score = 2 - k_X. Primary metric: AUROC of the suspicion score for y (ties count 1/2), paired Delta by
dossier-cluster bootstrap. Decision: Holm-adjusted one-sided bootstrap p < 0.05 over H1a, H2, H3.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata

FRAMINGS = ["A", "A2", "B", "N1", "N2", "N3", "P1", "P2"]
LABELLED = ["A", "B", "N1"]
OTHERS = ["A", "A2", "B", "N2", "N3", "P1", "P2"]
PAIRS = {"OPP": ("A", "B"), "SC": ("N2", "N3"), "DIV": ("P1", "P2"), "SAME": ("A", "A2")}
VERDICTS = {"ASSERTS", "CONTRADICTS", "SILENT"}
LABELS = {"GOLD", "SUPPORTED_OTHER", "NEUTRAL_INFERENCE", "SIDE_TAKING", "UNSUPPORTED_FACT"}
UNWARRANTED = {"SIDE_TAKING", "UNSUPPORTED_FACT"}  # y = 1
CLAIM_KEYS = ["dossier_id", "split", "domain", "model", "framing", "claim_id", "text", "label", "gold_id",
              "contested_id", "side", "evidence", "repaired"]
REPAIRS = {None, "gold_id_missing", "side_missing"}  # harness repairs of judge formatting slips
DOSSIER_KEYS = ["dossier_id", "split", "domain", "side_A", "side_B", "documents", "facts", "settled"]
FACT_KEYS = ["fact_id", "text", "favors", "contested"]
QWEN = "qwen3.5-397b"  # kappa is also reported excluding this generator's descriptions (judge2 shares its family)
SEED = 20261114
N_BOOT = 10_000
ALPHA = 0.05
TOST_MARGIN = 0.03
CHUNK = 1000
# Okabe-Ito colour-blind-safe palette
COLOURS = {"OPP": "#0072B2", "SC": "#E69F00", "DIV": "#009E73", "SAME": "#CC79A7", "v_closed": "#555555"}
MARKERS = {"OPP": "o", "SC": "s", "DIV": "^", "SAME": "D"}


class InputError(ValueError):
    pass


def _fail(msg):
    raise InputError(msg)


# ================================================================ loading and validation

def load_jsonl(path, required=True):
    path = Path(path)
    if not path.is_file():
        if required:
            _fail(f"{path}: file not found")
        return None
    rows = []
    for i, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as e:
            _fail(f"{path}:{i}: invalid JSON ({e})")
    if not rows:
        _fail(f"{path}: empty file (no rows)")
    return rows


def _nonempty_str(v):
    return isinstance(v, str) and v.strip() != ""


def _need(rows, keys, path):
    for i, r in enumerate(rows, 1):
        missing = [k for k in keys if k not in r]
        if missing:
            _fail(f"{path} row {i}: missing keys {missing}")


def _no_dups(df, keys, path):
    dup = df.duplicated(keys)
    if dup.any():
        _fail(f"{path}: duplicate rows for {keys}: {df.loc[dup, keys].head(3).to_dict('records')}")


def validate_claims(rows, path="claims"):
    _need(rows, CLAIM_KEYS, path)
    for i, r in enumerate(rows, 1):
        where = f"{path} row {i}"
        for k in ["dossier_id", "split", "domain", "model", "claim_id", "text"]:
            if not _nonempty_str(r[k]):
                _fail(f"{where}: {k} must be a non-empty string")
        if r["framing"] not in LABELLED:
            _fail(f"{where}: framing {r['framing']!r} not in {LABELLED}")
        if r["label"] not in LABELS:
            _fail(f"{where}: label {r['label']!r} not in {sorted(LABELS)}")
        if r["label"] == "GOLD" and not _nonempty_str(r["gold_id"]):
            _fail(f"{where}: GOLD claim without gold_id")
        if r["gold_id"] is not None and not _nonempty_str(r["gold_id"]):
            _fail(f"{where}: gold_id must be a non-empty string or null")
        if r["repaired"] not in REPAIRS:
            _fail(f"{where}: repaired {r['repaired']!r} not in {sorted(map(str, REPAIRS))}")
        if r["repaired"] == "gold_id_missing" and (r["label"] != "SUPPORTED_OTHER" or r["gold_id"] is not None):
            _fail(f"{where}: repaired=gold_id_missing requires label SUPPORTED_OTHER and gold_id null")
        if r["repaired"] == "side_missing":
            # SIDE_TAKING whose side the judge omitted: still y = 1, excluded from H1a only
            if r["label"] != "SIDE_TAKING" or r["side"] is not None or r["contested_id"] is not None:
                _fail(f"{where}: repaired=side_missing requires label SIDE_TAKING with side and contested_id null")
        elif r["label"] == "SIDE_TAKING":
            if not _nonempty_str(r["contested_id"]) or r["side"] not in ("A", "B"):
                _fail(f"{where}: SIDE_TAKING claim needs contested_id and side in A/B "
                      f"(got {r['contested_id']!r}, {r['side']!r})")
        elif r["side"] is not None:
            _fail(f"{where}: {r['label']} claim has side {r['side']!r} (must be null)")
        if r["evidence"] is not None and not isinstance(r["evidence"], str):
            _fail(f"{where}: evidence must be a string or null")
    df = pd.DataFrame(rows)[CLAIM_KEYS]
    _no_dups(df, ["dossier_id", "model", "claim_id"], path)  # claim_ids are local to a dossier x model cell
    splits = df["split"].unique()
    if len(splits) != 1:
        _fail(f"{path}: mixed splits {sorted(splits)}; analyse one split at a time")
    return df


def load_dossiers(dossier_dir, split):
    d = Path(dossier_dir)
    files = sorted(d.glob("*.json")) if d.is_dir() else []
    if not files:
        _fail(f"{d}: no dossier files")
    out = {}
    for f in files:
        try:
            x = json.loads(f.read_text())
        except json.JSONDecodeError as e:
            _fail(f"{f}: invalid JSON ({e})")
        missing = [k for k in DOSSIER_KEYS if k not in x]
        if missing:
            _fail(f"{f}: missing keys {missing}")
        if not _nonempty_str(x["documents"]):
            _fail(f"{f}: empty documents")
        if not isinstance(x["facts"], list) or not x["facts"]:
            _fail(f"{f}: no facts")
        if not isinstance(x["settled"], list):
            _fail(f"{f}: settled must be a list")
        for fact in x["facts"]:
            if any(k not in fact for k in FACT_KEYS):
                _fail(f"{f}: fact missing keys {[k for k in FACT_KEYS if k not in fact]}")
            if fact["favors"] not in ("A", "B", "N"):
                _fail(f"{f}: fact {fact['fact_id']} favors={fact['favors']!r} not in A/B/N")
        ids = [fact["fact_id"] for fact in x["facts"]]
        if len(set(ids)) != len(ids):
            _fail(f"{f}: duplicate fact_id")
        if x["dossier_id"] in out:
            _fail(f"{f}: duplicate dossier_id {x['dossier_id']}")
        if x["split"] == split:
            out[x["dossier_id"]] = x
    if not out:
        _fail(f"{d}: no dossiers with split={split!r}")
    return out


def check_claims_against_dossiers(df, dossiers):
    unknown = sorted(set(df["dossier_id"]) - set(dossiers))
    if unknown:
        _fail(f"claims reference dossiers not in the dossier dir for this split: {unknown[:5]}")
    for did, g in df.groupby("dossier_id"):
        x = dossiers[did]
        if set(g["domain"]) != {x["domain"]}:
            _fail(f"dossier {did}: claim domain {sorted(set(g['domain']))} != dossier domain {x['domain']!r}")
        bad = set(g["gold_id"].dropna()) - {f["fact_id"] for f in x["facts"]}
        if bad:
            _fail(f"dossier {did}: gold_id(s) not among verified facts: {sorted(bad)[:5]}")


def load_descriptions(path):
    rows = load_jsonl(path)
    _need(rows, ["dossier_id", "model", "framing", "excluded"], path)
    for i, r in enumerate(rows, 1):
        if r["framing"] not in FRAMINGS or not isinstance(r["excluded"], bool):
            _fail(f"{path} row {i}: framing not in {FRAMINGS} or non-boolean excluded")
    df = pd.DataFrame(rows)[["dossier_id", "model", "framing", "excluded"]]
    _no_dups(df, ["dossier_id", "model", "framing"], path)
    return df


def _n1_keys(claims):
    n1 = claims[claims["framing"] == "N1"]
    return set(zip(n1["dossier_id"], n1["model"], n1["claim_id"]))


def _check_refs(df, n1keys, path):
    bad = [k for k in zip(df["dossier_id"], df["model"], df["claim_id"]) if k not in n1keys]
    if bad:
        _fail(f"{path}: rows refer to claims that are not N1 claims in claims.jsonl: {bad[:3]}")


def load_presence(path, claims):
    rows = load_jsonl(path)
    _need(rows, ["dossier_id", "model", "claim_id", "framing", "verdict"], path)
    for i, r in enumerate(rows, 1):
        if r["framing"] not in OTHERS:
            _fail(f"{path} row {i}: framing {r['framing']!r} not in {OTHERS}")
        if r["verdict"] not in VERDICTS:
            _fail(f"{path} row {i}: verdict {r['verdict']!r} not in {sorted(VERDICTS)}")
    df = pd.DataFrame(rows)[["dossier_id", "model", "claim_id", "framing", "verdict"]]
    _no_dups(df, ["dossier_id", "model", "claim_id", "framing"], path)
    _check_refs(df, _n1_keys(claims), path)
    return df


def load_verifiers(path, claims):
    rows = load_jsonl(path, required=False)
    if rows is None:
        return None
    _need(rows, ["dossier_id", "model", "claim_id", "v_closed", "v_file"], path)
    for i, r in enumerate(rows, 1):
        for k in ("v_closed", "v_file"):
            v = r[k]
            if v is not None and (isinstance(v, bool) or not isinstance(v, (int, float)) or not 0 <= v <= 1):
                _fail(f"{path} row {i}: {k}={v!r} must be a number in [0, 1] or null")
    df = pd.DataFrame(rows)[["dossier_id", "model", "claim_id", "v_closed", "v_file"]]
    _no_dups(df, ["dossier_id", "model", "claim_id"], path)
    _check_refs(df, _n1_keys(claims), path)
    return df


def load_judge2(path, claims):
    rows = load_jsonl(path, required=False)
    if rows is None:
        return None
    _need(rows, ["dossier_id", "model", "claim_id", "label2"], path)
    for i, r in enumerate(rows, 1):
        if r["label2"] not in LABELS:
            _fail(f"{path} row {i}: label2 {r['label2']!r} not in {sorted(LABELS)}")
    df = pd.DataFrame(rows)[["dossier_id", "model", "claim_id", "label2"]]
    _no_dups(df, ["dossier_id", "model", "claim_id"], path)
    _check_refs(df, _n1_keys(claims), path)
    return df


def find_cells(claims, desc, presence, dossiers):
    """Complete cell = all 8 descriptions present and not excluded; N1, A and B each have >= 1 labelled claim;
    every N1 claim has presence rows for all 7 other framings. Expected cells = split dossiers x models seen."""
    excl = desc[desc["excluded"]]
    excl_keys = set(zip(excl["dossier_id"], excl["model"], excl["framing"]))
    clash = set(zip(claims["dossier_id"], claims["model"], claims["framing"])) & excl_keys
    if clash:
        _fail(f"claims exist for descriptions marked excluded: {sorted(clash)[:5]}")
    clash = set(zip(presence["dossier_id"], presence["model"], presence["framing"])) & excl_keys
    if clash:
        _fail(f"presence rows exist for descriptions marked excluded: {sorted(clash)[:5]}")
    models = sorted(set(claims["model"]) | set(desc[desc["dossier_id"].isin(dossiers)]["model"]))
    ok_desc = desc[~desc["excluded"]].groupby(["dossier_id", "model"])["framing"].agg(set).to_dict()
    lab = claims.groupby(["dossier_id", "model"])["framing"].agg(set).to_dict()
    n1 = claims[claims["framing"] == "N1"]
    n_n1 = n1.groupby(["dossier_id", "model"]).size().to_dict()
    pres_full = (presence.groupby(["dossier_id", "model", "claim_id"])["framing"].nunique() == len(OTHERS))
    n_full = pres_full[pres_full].groupby(level=[0, 1]).size().to_dict()
    complete, rows, miss = set(), [], []
    for did in sorted(dossiers):
        for m in models:
            have = ok_desc.get((did, m), set())
            missing_desc = [f for f in FRAMINGS if f not in have]
            miss += [(m, f) for f in missing_desc]
            reasons = []
            if missing_desc:
                reasons.append("missing or excluded descriptions: " + ",".join(missing_desc))
            no_lab = [f for f in LABELLED if f not in lab.get((did, m), set())]
            if no_lab:
                reasons.append("no labelled claims for: " + ",".join(no_lab))
            short = n_n1.get((did, m), 0) - n_full.get((did, m), 0)
            if short > 0:
                reasons.append(f"{short} N1 claim(s) lack presence rows for all 7 framings")
            if reasons:
                rows.append({"dossier_id": did, "model": m, "reason": "; ".join(reasons)})
            else:
                complete.add((did, m))
    cnt = pd.Series(miss, dtype=object).value_counts() if miss else pd.Series(dtype=float)
    rate = pd.DataFrame([{"model": m, "framing": f, "missing_or_excluded": int(cnt.get((m, f), 0)),
                          "expected": len(dossiers)} for m in models for f in FRAMINGS])
    rate["rate"] = rate["missing_or_excluded"] / rate["expected"]
    return complete, pd.DataFrame(rows, columns=["dossier_id", "model", "reason"]), rate


# ================================================================ per-claim table

def build_claim_table(claims, presence, verifiers, judge2):
    """One row per N1 claim in complete cells: y, k per pair, contradiction counts, verifier scores, label2."""
    n1 = claims[claims["framing"] == "N1"].copy()
    key = ["dossier_id", "model", "claim_id"]
    wide = presence.pivot_table(index=key, columns="framing", values="verdict", aggfunc="first")
    n1 = n1.join(wide, on=key)
    n1["y"] = n1["label"].isin(UNWARRANTED).astype(int)
    for p, (f1, f2) in PAIRS.items():
        n1[f"k_{p}"] = (n1[f1] == "ASSERTS").astype(int) + (n1[f2] == "ASSERTS").astype(int)
        n1[f"contra_{p}"] = (n1[f1] == "CONTRADICTS").astype(int) + (n1[f2] == "CONTRADICTS").astype(int)
    if verifiers is not None:
        n1 = n1.merge(verifiers, on=key, how="left")
    else:
        n1["v_closed"], n1["v_file"] = np.nan, np.nan
    n1["v_closed"] = pd.to_numeric(n1["v_closed"]).astype(float)
    n1["v_file"] = pd.to_numeric(n1["v_file"]).astype(float)
    if judge2 is not None:
        n1 = n1.merge(judge2, on=key, how="left")
    else:
        n1["label2"] = None
    n1["y2"] = np.where(n1["label2"].isna(), np.nan, n1["label2"].isin(UNWARRANTED).astype(float))
    # pre-specified combination: mean of the rank of v_closed and the rank of (2 - k_OPP), over claims with v_closed
    has = n1["v_closed"].notna().to_numpy()
    comb = np.full(len(n1), np.nan)
    if has.any():
        comb[has] = (rankdata(n1.loc[has, "v_closed"]) + rankdata(2 - n1.loc[has, "k_OPP"])) / 2
    n1["combo"] = comb
    return n1.reset_index(drop=True)


# ================================================================ bootstrap engine

class Boot:
    """Row 0 of every statistic array is the point estimate (all dossier weights 1); rows 1..B are dossier-cluster
    bootstrap resamples (multinomial dossier counts)."""

    def __init__(self, dossier_ids, n_boot=N_BOOT, seed=SEED):
        self.ids = list(dossier_ids)
        self.pos = {d: i for i, d in enumerate(self.ids)}
        D = len(self.ids)
        rng = np.random.default_rng(seed)
        idx = rng.integers(0, D, size=(n_boot, D))
        W = np.zeros((n_boot, D))
        np.add.at(W, (np.repeat(np.arange(n_boot), D), idx.ravel()), 1)
        self.W = np.vstack([np.ones((1, D)), W])

    def dsum(self, dossier, values):
        """Per-dossier sum of `values` (claim- or cell-level), then weighted totals: shape (B+1,)."""
        v = np.zeros(len(self.ids))
        np.add.at(v, [self.pos[d] for d in dossier], np.asarray(values, float))
        return self.W @ v

    def auroc(self, dossier, y, score, mask=None):
        """AUROC of `score` (higher = more suspicious) for y = 1; ties 1/2. NaN scores are dropped."""
        m = np.isfinite(score) if mask is None else (mask & np.isfinite(score))
        if not m.any():
            return np.full(self.W.shape[0], np.nan)
        lv, li = np.unique(score[m], return_inverse=True)
        di = np.array([self.pos[d] for d in np.asarray(dossier)[m]])
        H1, H0 = np.zeros((len(self.ids), len(lv))), np.zeros((len(self.ids), len(lv)))
        ym = y[m]
        np.add.at(H1, (di[ym == 1], li[ym == 1]), 1)
        np.add.at(H0, (di[ym == 0], li[ym == 0]), 1)
        out = []
        for s in range(0, self.W.shape[0], CHUNK):
            h1, h0 = self.W[s:s + CHUNK] @ H1, self.W[s:s + CHUNK] @ H0
            below0 = np.cumsum(h0, 1) - h0
            with np.errstate(invalid="ignore", divide="ignore"):
                out.append((h1 * (below0 + 0.5 * h0)).sum(1) / (h1.sum(1) * h0.sum(1)))
        return np.concatenate(out)

    def matched_precision(self, dossier, y, score, key, target_retention):
        """Keep the least suspicious claims (seeded random tie-break `key`) until the kept weight equals
        target_retention (array, per resample) of the total; precision = warranted share of the kept weight.
        The boundary claim is kept fractionally so the retention matches exactly."""
        order = np.lexsort((key, score))
        di = np.array([self.pos[d] for d in np.asarray(dossier)])[order]
        good = (1 - y[order]).astype(float)
        out = []
        for s in range(0, self.W.shape[0], CHUNK):
            w = self.W[s:s + CHUNK][:, di]
            cum = np.cumsum(w, 1)
            target = target_retention[s:s + CHUNK, None] * cum[:, -1:]
            kept = np.clip(target - (cum - w), 0, w)
            with np.errstate(invalid="ignore", divide="ignore"):
                out.append((kept * good).sum(1) / target[:, 0])
        return np.concatenate(out)


def _num(x):
    x = float(x)
    return None if math.isnan(x) or math.isinf(x) else x


def describe(arr, one_sided=False, ci90=False):
    """arr[0] = point estimate, arr[1:] = bootstrap. Percentile CIs over finite resamples."""
    b = arr[1:][np.isfinite(arr[1:])]
    r = {"estimate": _num(arr[0]), "n_boot_valid": int(b.size)}
    r["ci95_low"], r["ci95_high"] = (_num(v) for v in np.percentile(b, [2.5, 97.5])) if b.size else (None, None)
    if ci90:
        r["ci90_low"], r["ci90_high"] = (_num(v) for v in np.percentile(b, [5, 95])) if b.size else (None, None)
    if one_sided:  # H: statistic > 0; p = share of resamples at or below 0, with +1 smoothing
        r["p_one_sided"] = _num((1 + (b <= 0).sum()) / (b.size + 1)) if b.size else None
    return r


def holm(pvals):
    keys = sorted(pvals, key=lambda k: pvals[k])
    m, running, adj, rank = len(keys), 0.0, {}, {}
    for i, k in enumerate(keys):
        running = max(running, min(1.0, (m - i) * pvals[k]))
        adj[k], rank[k] = running, i
    return adj, rank


def cohen_kappa(a, b):
    a, b = np.asarray(a, int), np.asarray(b, int)
    if a.size == 0:
        return None
    po = (a == b).mean()
    pe = a.mean() * b.mean() + (1 - a.mean()) * (1 - b.mean())
    return _num((po - pe) / (1 - pe)) if pe < 1 else None


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ================================================================ drift (H1a, H1b)

def cell_drift(claims, dossiers):
    """Per complete cell: SIDE_TAKING counts by labelled framing and side (H1a), omission DiD (H1b).

    H1b per cell = mean over X in {A, B} of [(ally rate in X - ally rate in N1) - (opp rate in X - opp rate in N1)];
    rates = share of the dossier's UNCONTESTED gold facts favouring that side whose fact_id is the gold_id of some
    labelled claim in that description.
    """
    rows = []
    for (did, m), g in claims.groupby(["dossier_id", "model"]):
        st = g[(g["label"] == "SIDE_TAKING") & (g["repaired"] != "side_missing")]  # H1a needs a side
        cnt = lambda fr, side=None: int(((st["framing"] == fr) & ((st["side"] == side) if side else True)).sum())
        facts = [f for f in dossiers[did]["facts"] if not f["contested"]]
        fav = {s: {f["fact_id"] for f in facts if f["favors"] == s} for s in "AB"}
        said = {fr: set(g.loc[g["framing"] == fr, "gold_id"].dropna()) for fr in LABELLED}
        rate = lambda fr, s: len(said[fr] & fav[s]) / len(fav[s])
        did_ = np.nan
        if fav["A"] and fav["B"]:
            did_ = 0.5 * (((rate("A", "A") - rate("N1", "A")) - (rate("A", "B") - rate("N1", "B")))
                          + ((rate("B", "B") - rate("N1", "B")) - (rate("B", "A") - rate("N1", "A"))))
        rows.append({"dossier_id": did, "model": m,
                     "st_A_n": cnt("A"), "st_A_sideA": cnt("A", "A"), "st_B_n": cnt("B"), "st_B_sideB": cnt("B", "B"),
                     "st_N1_n": cnt("N1"), "st_N1_sideA": cnt("N1", "A"), "st_N1_sideB": cnt("N1", "B"),
                     "h1b_did": did_})
    return pd.DataFrame(rows)


def h1a_arr(bt, drift):
    s = {c: bt.dsum(drift["dossier_id"], drift[c]) for c in drift.columns if c.startswith("st_")}
    with np.errstate(invalid="ignore", divide="ignore"):
        return 0.5 * ((s["st_A_sideA"] / s["st_A_n"] - s["st_N1_sideA"] / s["st_N1_n"])
                      + (s["st_B_sideB"] / s["st_B_n"] - s["st_N1_sideB"] / s["st_N1_n"]))


def h1b_arr(bt, drift):
    d = drift.dropna(subset=["h1b_did"])
    with np.errstate(invalid="ignore", divide="ignore"):
        return bt.dsum(d["dossier_id"], d["h1b_did"]) / bt.dsum(d["dossier_id"], np.ones(len(d)))


def presence_validity(claims, presence):
    """For N1 GOLD claims and F in {A, B}: matrix ASSERTS vs F's labelled claims containing the same gold_id."""
    n1 = claims[(claims["framing"] == "N1") & (claims["label"] == "GOLD")]
    gold_in = claims[claims["framing"].isin(["A", "B"])].dropna(subset=["gold_id"])
    has = set(zip(gold_in["dossier_id"], gold_in["model"], gold_in["framing"], gold_in["gold_id"]))
    pv = presence[presence["framing"].isin(["A", "B"])].merge(
        n1[["dossier_id", "model", "claim_id", "gold_id"]], on=["dossier_id", "model", "claim_id"])
    if pv.empty:
        return {"n_pairs": 0, "agreement": None}
    matrix = (pv["verdict"] == "ASSERTS").to_numpy()
    label = np.array([(d, m, f, g) in has for d, m, f, g in
                      zip(pv["dossier_id"], pv["model"], pv["framing"], pv["gold_id"])])
    fr = pv["framing"].to_numpy()
    return {"n_pairs": int(len(pv)), "agreement": _num((matrix == label).mean()),
            "kappa": cohen_kappa(matrix, label),
            "both_present": int((matrix & label).sum()), "matrix_only": int((matrix & ~label).sum()),
            "labels_only": int((~matrix & label).sum()), "both_absent": int((~matrix & ~label).sum()),
            "per_framing": {f: _num((matrix[fr == f] == label[fr == f]).mean()) for f in ("A", "B") if (fr == f).any()}}


# ================================================================ main analysis

def analyze(claims_path, dossier_dir, out_dir=None, descriptions_path=None, presence_path=None,
            verifiers_path=None, judge2_path=None, n_boot=N_BOOT, seed=SEED, make_figure=True):
    claims_path = Path(claims_path)
    base = claims_path.parent
    descriptions_path = Path(descriptions_path or base / "descriptions.jsonl")
    presence_path = Path(presence_path or base / "presence.jsonl")
    verifiers_path = Path(verifiers_path or base / "verifiers.jsonl")
    judge2_path = Path(judge2_path or base / "judge2.jsonl")

    claims = validate_claims(load_jsonl(claims_path), str(claims_path))
    split = claims["split"].iloc[0]
    dossiers = load_dossiers(dossier_dir, split)
    check_claims_against_dossiers(claims, dossiers)
    desc = load_descriptions(descriptions_path)
    presence = load_presence(presence_path, claims)
    verifiers = load_verifiers(verifiers_path, claims)
    judge2 = load_judge2(judge2_path, claims)

    complete, excluded, rate_tab = find_cells(claims, desc, presence, dossiers)
    if not complete:
        _fail("no complete dossier x model cells: nothing to analyse")
    if len(excluded):
        print(f"WARNING: {len(excluded)} incomplete dossier x model cell(s) excluded; see excluded_cells.csv",
              file=sys.stderr)
    in_cell = lambda df: df[pd.Series(list(zip(df["dossier_id"], df["model"])), index=df.index).isin(complete)]
    claims_c, presence_c = in_cell(claims), in_cell(presence)
    T = build_claim_table(claims_c, presence_c, verifiers, judge2)
    if T.empty:
        _fail("no N1 claims in complete cells")
    if T["y"].sum() == 0 or (T["y"] == 0).sum() == 0:
        _fail("N1 claims in complete cells contain only one outcome class; AUROC undefined")
    drift = cell_drift(claims_c, dossiers)
    dossier_ids = sorted({d for d, _ in complete})
    bt = Boot(dossier_ids, n_boot, seed)
    D, y = T["dossier_id"].to_numpy(), T["y"].to_numpy()
    score = {p: (2 - T[f"k_{p}"]).to_numpy().astype(float) for p in PAIRS}
    for v in ("v_closed", "v_file", "combo"):
        score[v] = T[v].to_numpy()

    def aurocs(mask=None, sigs=tuple(PAIRS)):
        return {p: bt.auroc(D, y, score[p], mask) for p in sigs}

    res = {"meta": {
        "split": split, "n_boot": n_boot, "seed": seed, "alpha": ALPHA, "tost_margin": TOST_MARGIN,
        "files": {k: {"path": str(p), "sha256": sha256(p)} if p.is_file() else None for k, p in
                  [("claims", claims_path), ("descriptions", descriptions_path), ("presence", presence_path),
                   ("verifiers", verifiers_path), ("judge2", judge2_path)]},
        "analyze_py_sha256": sha256(__file__),
        "score": "suspicion = 2 - k_X, k_X = number of ASSERTS in pair X; AUROC ties count 1/2",
        "ci_method": "percentile, dossier-cluster bootstrap (dossiers resampled with all models and claims)",
        "p_method": "one-sided bootstrap p = (1 + #{stat* <= 0}) / (B_valid + 1)",
        "decision": "supported iff Holm-adjusted one-sided p < 0.05 over {H1a, H2, H3}",
    }}
    res["n"] = {
        "dossiers_in_split": len(dossiers), "dossiers_analysed": len(dossier_ids),
        "models": sorted(claims["model"].unique()),
        "cells_expected": len(dossiers) * len(set(rate_tab["model"])), "cells_complete": len(complete),
        "cells_excluded": len(excluded), "claims_total": len(claims), "claims_in_complete_cells": len(claims_c),
        "N1_claims": len(T), "N1_unwarranted": int(y.sum()), "N1_warranted": int((y == 0).sum()),
        "N1_by_label": {k: int(v) for k, v in T["label"].value_counts().items()},
        "side_taking_claims_with_side": {f: int(drift[f"st_{f}_n"].sum()) for f in LABELLED},
        "repaired_in_complete_cells": {r: {f: int(((claims_c["repaired"] == r) & (claims_c["framing"] == f)).sum())
                                           for f in LABELLED} for r in ("side_missing", "gold_id_missing")},
        "repaired_in_file": {r: {f: int(((claims["repaired"] == r) & (claims["framing"] == f)).sum())
                                 for f in LABELLED} for r in ("side_missing", "gold_id_missing")},
        "H1b_cells": int(drift["h1b_did"].notna().sum()),
        "N1_with_v_closed": int(T["v_closed"].notna().sum()), "N1_with_v_file": int(T["v_file"].notna().sum()),
        "N1_with_label2": int(T["label2"].notna().sum()),
    }
    res["exclusions"] = {
        "cells": excluded.to_dict("records"),
        "max_rate_model_x_framing": _num(rate_tab["rate"].max()),
        "over_10pct": rate_tab[rate_tab["rate"] > 0.10][["model", "framing", "rate"]].to_dict("records"),
    }

    # ---------------- primary: AUROC per signal and paired deltas
    A = aurocs()
    deltas = {"OPP_SC": A["OPP"] - A["SC"], "OPP_DIV": A["OPP"] - A["DIV"],
              "OPP_SAME": A["OPP"] - A["SAME"], "DIV_SC": A["DIV"] - A["SC"]}
    res["auroc"] = {p: describe(A[p]) for p in PAIRS}
    res["delta_auroc"] = {k: describe(v, one_sided=True, ci90=True) for k, v in deltas.items()}

    # ---------------- confirmatory family with Holm
    fam = {"H1a": h1a_arr(bt, drift), "H2": deltas["OPP_SC"], "H3": deltas["OPP_DIV"]}
    desc_f = {k: describe(v, one_sided=True, ci90=True) for k, v in fam.items()}
    raw = {k: v["p_one_sided"] if v["p_one_sided"] is not None else 1.0 for k, v in desc_f.items()}
    adj, rank = holm(raw)
    conf = {}
    for k, v in fam.items():
        lvl = ALPHA / (len(fam) - rank[k])  # Holm step-down level for this test's rank
        b = v[1:][np.isfinite(v[1:])]
        c = dict(desc_f[k], p_holm=adj[k], holm_rank=rank[k] + 1, holm_alpha=lvl,
                 holm_one_sided_lower=_num(np.percentile(b, 100 * lvl)) if b.size else None,
                 holm_one_sided_level=1 - lvl, supported=bool(adj[k] < ALPHA))
        if k in ("H2", "H3"):
            c["tost_equivalent_within_0.03"] = bool(c["ci90_low"] is not None and c["ci90_low"] > -TOST_MARGIN
                                                    and c["ci90_high"] < TOST_MARGIN)
        conf[k] = c
    conf["H1a"]["n_side_taking"] = res["n"]["side_taking_claims_with_side"]
    conf["H1a"]["n_side_missing_excluded"] = res["n"]["repaired_in_complete_cells"]["side_missing"]
    res["confirmatory"] = conf

    # ---------------- secondary
    sec = {}
    n_all = bt.dsum(D, np.ones(len(T)))
    n1_, n0_ = bt.dsum(D, y), bt.dsum(D, 1 - y)
    and_rule, ret = {}, {}
    for p in PAIRS:
        keep = (T[f"k_{p}"] == 2).to_numpy().astype(float)
        k0, k1 = bt.dsum(D, keep * (1 - y)), bt.dsum(D, keep * y)
        with np.errstate(invalid="ignore", divide="ignore"):
            ret[p] = (k0 + k1) / n_all
            and_rule[p] = {"BA": describe(0.5 * ((n1_ - k1) / n1_ + k0 / n0_)), "retention": describe(ret[p]),
                           "precision": describe(k0 / (k0 + k1))}
    sec["and_rule"] = and_rule
    tie_key = np.random.default_rng(seed + 7).random(len(T))  # seeded random tie-break
    mp = {p: bt.matched_precision(D, y, score[p], tie_key, ret["OPP"])
          for p in [*PAIRS, "v_closed", "v_file", "combo"] if np.isfinite(score[p]).all()}
    sec["matched_retention_precision"] = {"retention_target": describe(ret["OPP"]),
                                          **{p: describe(v) for p, v in mp.items()},
                                          "delta_OPP_SC": describe(mp["OPP"] - mp["SC"], one_sided=True),
                                          "delta_OPP_DIV": describe(mp["OPP"] - mp["DIV"], one_sided=True)}

    has_v = np.isfinite(score["v_closed"])
    if has_v.any():
        Av = {p: bt.auroc(D, y, score[p], has_v) for p in ("v_closed", "combo", "OPP", "SC")}
        Af = bt.auroc(D, y, score["v_file"])
        sec["verifiers"] = {
            "n_v_closed": int(has_v.sum()), "n_v_file": int(np.isfinite(score["v_file"]).sum()),
            "auroc_v_closed": describe(Av["v_closed"]), "auroc_v_file": describe(Af),
            "auroc_combo": describe(Av["combo"]), "auroc_OPP_same_claims": describe(Av["OPP"]),
            "delta_combo_minus_v_closed": describe(Av["combo"] - Av["v_closed"], one_sided=True),
            "delta_OPP_minus_v_closed": describe(Av["OPP"] - Av["v_closed"], one_sided=True),
            # share of the SC-to-ceiling gap that OPP recovers (descriptive point estimate)
            "gap_recovered_OPP": _num((Av["OPP"][0] - Av["SC"][0]) / (Af[0] - Av["SC"][0]))
            if np.isfinite(Af[0]) and Af[0] != Av["SC"][0] else None,
        }
    else:
        sec["verifiers"] = None

    def subgroup(mask, ci90=False):
        Am = aurocs(mask)
        return {"N1_claims": int(mask.sum()), "N1_unwarranted": int(y[mask].sum()),
                **{f"auroc_{p}": describe(Am[p]) for p in PAIRS},
                "delta_OPP_SC": describe(Am["OPP"] - Am["SC"], one_sided=True, ci90=ci90),
                "delta_OPP_DIV": describe(Am["OPP"] - Am["DIV"], one_sided=True, ci90=ci90)}

    models_arr, label_arr, dom_arr = T["model"].to_numpy(), T["label"].to_numpy(), T["domain"].to_numpy()
    sec["per_model"] = {m: subgroup(models_arr == m) for m in sorted(set(models_arr))}
    sec["per_domain"] = {d: subgroup(dom_arr == d) for d in sorted(set(dom_arr))}
    st_mask, uf_mask = (y == 0) | (label_arr == "SIDE_TAKING"), (y == 0) | (label_arr == "UNSUPPORTED_FACT")
    sec["per_error_type"] = {"SIDE_TAKING": subgroup(st_mask), "UNSUPPORTED_FACT": subgroup(uf_mask)}
    a_st, a_uf = aurocs(st_mask, ("OPP", "SC")), aurocs(uf_mask, ("OPP", "SC"))
    sec["error_type_interaction_OPP_SC"] = describe((a_st["OPP"] - a_st["SC"]) - (a_uf["OPP"] - a_uf["SC"]),
                                                    one_sided=True)
    sec["H1b_did_exploratory"] = dict(describe(h1b_arr(bt, drift), one_sided=True), n_cells=res["n"]["H1b_cells"])
    sec["SAME"] = {"auroc": res["auroc"]["SAME"], "delta_OPP_SAME": res["delta_auroc"]["OPP_SAME"],
                   "note": "one-sided-pressure control (A, A2); exploratory"}
    contra = {}
    for p in PAIRS:
        c = T[f"contra_{p}"].to_numpy()
        with np.errstate(invalid="ignore", divide="ignore"):
            contra[p] = {"rate_all": describe(bt.dsum(D, c) / (2 * n_all)),
                         "rate_y1": describe(bt.dsum(D, c * y) / (2 * n1_)),
                         "rate_y0": describe(bt.dsum(D, c * (1 - y)) / (2 * n0_)),
                         "n_cells": int(2 * len(T)), "n_contradicts": int(c.sum())}
    sec["contradicts_rate_by_pair"] = contra
    res["secondary"] = sec

    # ---------------- sensitivity
    y2 = T["y2"].to_numpy()
    k2 = np.isfinite(y2)
    res["sensitivity"] = {"drop_neutral_inference": subgroup(label_arr != "NEUTRAL_INFERENCE", ci90=True),
                          "judge2_agrees": subgroup(k2 & (y2 == y), ci90=True) if k2.any() else None}

    # ---------------- validation
    kap = lambda m: {"kappa": cohen_kappa(y[m], y2[m]), "n": int(m.sum())}
    res["validation"] = {
        "kappa_y": None if not k2.any() else {
            "overall": kap(k2),
            "per_model": {m: kap(k2 & (models_arr == m)) for m in sorted(set(models_arr))},
            f"excluding_{QWEN}": kap(k2 & (models_arr != QWEN))},
        "presence_validity": presence_validity(claims_c, presence_c),
    }

    if out_dir is not None:
        write_outputs(Path(out_dir), res, T, drift, excluded, rate_tab, make_figure)
    return res


# ================================================================ outputs

def _flat(name, d):
    row = {"group": name}
    for k, v in d.items():
        if isinstance(v, dict) and "estimate" in v:
            row.update({f"{k}_{f}": v[f] for f in ("estimate", "ci95_low", "ci95_high", "p_one_sided") if f in v})
        elif not isinstance(v, dict):
            row[k] = v
    return row


def write_outputs(out, res, T, drift, excluded, rate_tab, make_figure=True):
    out.mkdir(parents=True, exist_ok=True)
    (out / "results.json").write_text(json.dumps(res, indent=2))
    T.drop(columns=["text", "evidence"]).to_csv(out / "per_claim_signals.csv", index=False)
    drift.to_csv(out / "per_cell_drift.csv", index=False)
    excluded.to_csv(out / "excluded_cells.csv", index=False)
    rate_tab.to_csv(out / "missing_rate_model_framing.csv", index=False)
    sec = res["secondary"]
    pd.DataFrame([{"signal": p, **{f"auroc_{f}": res["auroc"][p][f] for f in ("estimate", "ci95_low", "ci95_high")},
                   **{f"and_{m}": sec["and_rule"][p][m]["estimate"] for m in ("BA", "retention", "precision")},
                   "precision_at_matched_retention": sec["matched_retention_precision"][p]["estimate"]}
                  for p in PAIRS]).to_csv(out / "signals.csv", index=False)
    pd.DataFrame([{"test": k, **{f: v for f, v in c.items() if not isinstance(v, dict)}}
                  for k, c in res["confirmatory"].items()]).to_csv(out / "confirmatory.csv", index=False)
    for name in ("per_model", "per_domain", "per_error_type"):
        pd.DataFrame([_flat(g, v) for g, v in sec[name].items()]).to_csv(out / f"{name}.csv", index=False)
    pd.DataFrame([_flat(g, v) for g, v in res["sensitivity"].items() if v]).to_csv(out / "sensitivity.csv", index=False)
    pd.DataFrame([{"pair": p, **{k: v["estimate"] for k, v in c.items() if isinstance(v, dict)},
                   "n_cells": c["n_cells"], "n_contradicts": c["n_contradicts"]}
                  for p, c in sec["contradicts_rate_by_pair"].items()]).to_csv(out / "contradicts.csv", index=False)
    if make_figure:
        frontier_figure(res, T, out / "figures" / "frontier.png")


def frontier_figure(res, T, path):
    """Precision vs retention: each pair's 3-level score gives points at k >= 1 and k = 2 (AND rule, with CI);
    the closed-book verifier, if present, is a threshold sweep."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    path.parent.mkdir(parents=True, exist_ok=True)
    y = T["y"].to_numpy()
    plt.rcParams.update({"font.size": 13})
    fig, ax = plt.subplots(figsize=(7.2, 6.4), dpi=200)
    names = {"OPP": "opposed (A, B)", "SC": "self-consistency (N2, N3)", "DIV": "diverse (P1, P2)",
             "SAME": "same side (A, A2)"}
    base = 1 - y.mean()
    for p in PAIRS:
        k = T[f"k_{p}"].to_numpy()
        pts = [(1.0, base)] + [((k >= t).mean(), 1 - y[k >= t].mean() if (k >= t).any() else np.nan) for t in (1, 2)]
        ax.plot(*zip(*pts), "-", marker=MARKERS[p], color=COLOURS[p], ms=7, lw=1.5, label=names[p], zorder=2)
        a = res["secondary"]["and_rule"][p]
        r, pr = a["retention"], a["precision"]
        if None not in (r["ci95_low"], pr["ci95_low"], r["estimate"], pr["estimate"]):
            ax.errorbar(r["estimate"], pr["estimate"],
                        xerr=[[r["estimate"] - r["ci95_low"]], [r["ci95_high"] - r["estimate"]]],
                        yerr=[[pr["estimate"] - pr["ci95_low"]], [pr["ci95_high"] - pr["estimate"]]], fmt="none",
                        color=COLOURS[p], capsize=3, zorder=3)
    v = T["v_closed"].to_numpy()
    if np.isfinite(v).all():
        o = np.argsort(v, kind="stable")
        n = np.arange(1, len(v) + 1)
        ax.plot(n / len(v), np.cumsum(1 - y[o]) / n, ":", color=COLOURS["v_closed"], lw=1.5,
                label="closed-book verifier (sweep)", zorder=1)
    ax.axvline(res["secondary"]["and_rule"]["OPP"]["retention"]["estimate"], color="#999999", lw=0.8, ls="--")
    ax.set_xlabel("Retention (share of N1 claims kept)")
    ax.set_ylabel("Precision (warranted share of kept)")
    n = res["n"]
    ax.set_title(f"Precision vs retention, {res['meta']['split']} split: points at k ≥ 1 and k = 2\n"
                 f"{n['N1_claims']} N1 claims, {n['dossiers_analysed']} dossiers; bars = 95% CI at k = 2; "
                 f"dashed = OPP retention", fontsize=10)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=10, loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=2, frameon=False)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--claims", required=True)
    ap.add_argument("--dossiers", required=True)
    ap.add_argument("--out", required=True)
    for f in ("descriptions", "presence", "verifiers", "judge2"):
        ap.add_argument(f"--{f}", default=None)
    ap.add_argument("--n-boot", type=int, default=N_BOOT)
    a = ap.parse_args(argv)
    try:
        res = analyze(a.claims, a.dossiers, a.out, a.descriptions, a.presence, a.verifiers, a.judge2, a.n_boot)
    except InputError as e:
        print(f"INPUT ERROR: {e}", file=sys.stderr)
        return 2
    print(json.dumps({"n": res["n"], "confirmatory": res["confirmatory"]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
