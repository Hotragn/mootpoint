"""Checks that analysis/readers.py (PLAN v4, family F2) recovers planted reader effects, returns nulls, matches a
hand-computed toy, counts dropped cells and fails loudly on bad inputs."""
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "analysis"))
import analyze as A  # noqa: E402
import make_synthetic as MS  # noqa: E402
import readers as R  # noqa: E402

NB = 2000


def make_world(tmp, effect, seed, n_dossiers=48):
    """Synthetic run + frozen analyze.py signals + verifiers.jsonl with the v4 reader columns.
    effect: v_closed separates y better than v_closed_none and v_closed_div; v_closed_none better than SC.
    null (effect=None): the three F2 readers are 2 - k_SC with random tie-breaking, so every F2 delta is 0 in
    expectation (random tie-breaks leave the expected AUROC equal to the ties-1/2 AUROC)."""
    c, d, _ = MS.make(tmp / "run", effect=1.0, n_dossiers=n_dossiers, seed=seed, drop_cells=1)
    A.analyze(c, d, out_dir=tmp / "res", n_boot=50, make_figure=False)
    S = pd.read_csv(tmp / "res" / "per_claim_signals.csv", dtype={"claim_id": str})
    rng = np.random.default_rng(seed + 100)
    y, n = S["y"].to_numpy(), len(S)
    clip = lambda v: np.clip(v, 0, 1)
    noisy = lambda shift: clip(0.35 + shift * y + rng.normal(0, 0.2, n))
    if effect is None:
        tie = lambda: (2 - S["k_SC"].to_numpy()) / 2 * 0.9 + 0.05 * rng.random(n)
        cols = {"v_closed": tie(), "v_closed_none": tie(), "v_closed_div": tie()}
    else:
        cols = {"v_closed": noisy(0.35), "v_closed_none": noisy(0.15), "v_closed_div": noisy(0.15)}
    cols.update({k: noisy(0.15) for k in ("v_file", "v_closed_sc", "v_closed_debate", "xf_none", "xf_opp")})
    with open(tmp / "run" / "verifiers.jsonl", "w") as fh:
        for i, r in S.iterrows():
            fh.write(json.dumps({"dossier_id": r.dossier_id, "model": r.model, "claim_id": r.claim_id,
                                 **{k: float(v[i]) for k, v in cols.items()}}) + "\n")
    return c, tmp / "res" / "per_claim_signals.csv"


@pytest.fixture(scope="module")
def effect_world(tmp_path_factory):
    return make_world(tmp_path_factory.mktemp("eff"), 1.0, seed=3)


@pytest.fixture(scope="module")
def small_world(tmp_path_factory):
    return make_world(tmp_path_factory.mktemp("small"), 1.0, seed=5, n_dossiers=8)


def test_planted_effect_recovered(effect_world):
    res = R.analyze_readers(*effect_world, n_boot=NB)
    conf = res["confirmatory_F2"]
    for k in ("R1", "R2", "R3"):
        assert conf[k]["estimate"] > 0 and conf[k]["supported"] and conf[k]["holm_one_sided_lower"] > 0, k
    assert not conf["R2"]["tost_equivalent_within_0.03"] and not conf["R3"]["tost_equivalent_within_0.03"]
    assert res["n"]["cells_dropped_no_verifier_rows"] == 0 and res["n"]["cells_analysed"] == 48 * 3 - 1
    d = res["descriptive"]
    assert set(d["auroc"]) == {"SC", "OPP", "DIV", "v_closed", "v_closed_none", "v_closed_div", "v_file",
                               "v_closed_sc", "v_closed_debate", "xf_none", "xf_opp"}
    assert abs(d["xf_opp_minus_xf_none"]["estimate"]) < 0.06  # same generative model for both
    # make_synthetic plants OPP > SC on SIDE_TAKING claims
    assert res["secondary_OPP_minus_SC_side_taking_positives"]["ci95_low"] > 0
    assert set(res["per_model"]) == set(MS.MODELS)
    assert res["judge2_labels"]["N1_claims"] == res["n"]["N1_claims"]
    assert res["judge_agreed"]["N1_claims"] < res["n"]["N1_claims"]


@pytest.mark.parametrize("seed", [11, 12, 13])
def test_null_not_supported(tmp_path, seed):
    res = R.analyze_readers(*make_world(tmp_path, None, seed), n_boot=NB)
    for k, c in res["confirmatory_F2"].items():
        assert not c["supported"], k
        assert c["ci95_low"] <= 0 <= c["ci95_high"], k
        assert abs(c["estimate"]) < 0.03, k


def toy_table():
    # dossier d1 = claims 0-2, d2 = claims 3-5; claim 0 SIDE_TAKING and claim 1 UNSUPPORTED_FACT are y = 1
    return pd.DataFrame({
        "dossier_id": ["d1"] * 3 + ["d2"] * 3, "model": ["m1", "m2"] * 3,
        "label": ["SIDE_TAKING", "UNSUPPORTED_FACT", "GOLD", "GOLD", "SUPPORTED_OTHER", "GOLD"],
        "y": [1, 1, 0, 0, 0, 0],
        "y2": [1, 0, 0, 0, 0, 1.0],
        "k_SC": [1, 2, 2, 1, 2, 2], "k_OPP": [0, 2, 2, 2, 1, 2], "k_DIV": [2] * 6,
        "v_closed_none": [.9, .3, .1, .5, .2, .4],
        "v_closed": [.9, .6, .1, .5, .2, .4],
        "v_closed_div": [.9, .45, .1, .5, .2, .4],
        "xf_none": [.5] * 6, "xf_opp": [.9, .6, .1, .5, .2, .4]})


def test_toy_hand_computed():
    cols = ["v_closed", "v_closed_none", "v_closed_div", "xf_none", "xf_opp"]
    res = R.compute(toy_table(), cols, n_boot=200)
    a = res["descriptive"]["auroc"]
    # 2 positives x 4 negatives = 8 pairs; ties count 1/2
    assert a["SC"]["estimate"] == pytest.approx(5 / 8)  # SC score 1,0 vs 0,1,0,0: 3.5 + 1.5
    assert a["v_closed_none"]["estimate"] == pytest.approx(6 / 8)
    assert a["v_closed"]["estimate"] == pytest.approx(8 / 8)
    assert a["v_closed_div"]["estimate"] == pytest.approx(7 / 8)
    conf = res["confirmatory_F2"]
    assert conf["R1"]["estimate"] == pytest.approx(1 / 8)
    assert conf["R2"]["estimate"] == pytest.approx(2 / 8)
    assert conf["R3"]["estimate"] == pytest.approx(1 / 8)
    assert res["descriptive"]["xf_opp_minus_xf_none"]["estimate"] == pytest.approx(0.5)
    # judge2 labels: positives are claims 0 and 5 -> v_closed .9 beats 4, .4 beats .1 and .2 -> 6/8
    assert res["judge2_labels"]["auroc"]["v_closed"]["estimate"] == pytest.approx(6 / 8)
    # judge-agreed subset = claims 0, 2, 3, 4
    assert res["judge_agreed"]["N1_claims"] == 4
    assert res["judge_agreed"]["auroc"]["v_closed"]["estimate"] == pytest.approx(1.0)
    # SIDE_TAKING positives only (claims 0, 2-5): OPP 2 vs 0,0,1,0 = 1; SC 1 vs 0,1,0,0 = 3.5/4
    st = res["secondary_OPP_minus_SC_side_taking_positives"]
    assert st["estimate"] == pytest.approx(1 - 3.5 / 4) and st["N1_claims"] == 5
    assert res["per_model"]["m1"]["N1_claims"] == 3


def test_two_sided_p():
    arr = np.concatenate([[0.0], np.full(99, 1.0)])
    assert R._two_sided(arr) == pytest.approx(2 / 100)


def copy_world(world, tmp):
    c, s = world
    shutil.copytree(Path(c).parent, tmp / "run")
    shutil.copytree(Path(s).parent, tmp / "res")
    return tmp / "run" / "claims.jsonl", tmp / "res" / "per_claim_signals.csv"


def rewrite(path, fn):
    rows = [json.loads(x) for x in Path(path).read_text().splitlines()]
    rows = fn(rows)
    Path(path).write_text("".join(json.dumps(r) + "\n" for r in rows))


def test_cells_without_verifier_rows_dropped(small_world, tmp_path):
    c, s = copy_world(small_world, tmp_path)
    v = c.parent / "verifiers.jsonl"
    rows = [json.loads(x) for x in v.read_text().splitlines()]
    cells = sorted({(r["dossier_id"], r["model"]) for r in rows})
    gone, partial = cells[0], cells[1]
    first_partial = next(i for i, r in enumerate(rows) if (r["dossier_id"], r["model"]) == partial)
    rewrite(v, lambda rs: [r for i, r in enumerate(rs) if (r["dossier_id"], r["model"]) != gone and i != first_partial])
    T, info = R.build_unit(c, s)
    reasons = {(x["dossier_id"], x["model"]): x["reason"] for x in info["cells_dropped_no_verifier_rows"]}
    assert reasons == {gone: "no verifier rows", partial: "some N1 claims lack verifier rows"}
    assert info["cells_analysed"] == info["cells_complete"] - 2
    assert not set(zip(T["dossier_id"], T["model"])) & {gone, partial}


def drop_key(k):
    return lambda rs: [{kk: vv for kk, vv in r.items() if kk != k} for r in rs]


def set_first(k, v):
    return lambda rs: [dict(rs[0], **{k: v})] + rs[1:]


def drop_key_first(k):
    return lambda rs: [{kk: vv for kk, vv in rs[0].items() if kk != k}] + rs[1:]


BAD_VERIFIERS = {
    "required column absent (pilot layout)": drop_key("v_closed_none"),
    "required column missing in one row": drop_key_first("v_closed_div"),
    "descriptive column in some rows only": drop_key_first("xf_opp"),
    "value above 1": set_first("v_closed", 1.2),
    "null value": set_first("v_file", None),
    "bool value": set_first("v_closed", True),
    "string value": set_first("xf_none", "0.3"),
    "duplicate row": lambda rs: rs + rs[:1],
    "unknown claim": lambda rs: rs + [dict(rs[0], claim_id="N1:999")],
    "non-N1 claim": lambda rs: rs + [dict(rs[0], claim_id="A:gF0")],
}


@pytest.mark.parametrize("case", list(BAD_VERIFIERS))
def test_bad_verifiers_fail_loudly(small_world, tmp_path, case):
    c, s = copy_world(small_world, tmp_path)
    rewrite(c.parent / "verifiers.jsonl", BAD_VERIFIERS[case])
    with pytest.raises(R.InputError):
        R.build_unit(c, s)


def test_descriptive_columns_may_be_absent(small_world, tmp_path):
    c, s = copy_world(small_world, tmp_path)
    rewrite(c.parent / "verifiers.jsonl", lambda rs: [{k: v for k, v in r.items() if not k.startswith("xf")}
                                                      for r in rs])
    (c.parent / "judge2.jsonl").unlink()
    res = R.analyze_readers(c, s, n_boot=100)
    assert res["meta"]["reader_columns_absent"] == ["xf_none", "xf_opp"]
    assert "xf_opp_minus_xf_none" not in res["descriptive"]
    assert res["judge2_labels"] is None and res["judge_agreed"] is None


def _tamper_csv(s, fn):
    df = pd.read_csv(s, dtype={"claim_id": str})
    fn(df)
    df.to_csv(s, index=False)


BAD_OTHER = {
    "k_SC disagrees with N2/N3": lambda c, s: _tamper_csv(s, lambda df: df.loc.__setitem__((0, "k_SC"),
                                                                                         (df.loc[0, "k_SC"] + 1) % 3)),
    "invalid N2 verdict": lambda c, s: _tamper_csv(s, lambda df: df.loc.__setitem__((0, "N2"), "MAYBE")),
    "y disagrees with label": lambda c, s: _tamper_csv(s, lambda df: df.loc.__setitem__((0, "y"), 1 - df.loc[0, "y"])),
    "signals column missing": lambda c, s: _tamper_csv(s, lambda df: df.pop("k_OPP")),
    "signals not from frozen analyze.py": lambda c, s: (s.parent / "results.json").write_text(
        json.dumps({"meta": dict(json.loads((s.parent / "results.json").read_text())["meta"],
                                 analyze_py_sha256="0" * 64)})),
    "results.json missing": lambda c, s: (s.parent / "results.json").unlink(),
    "claims file differs from the signals'": lambda c, s: rewrite(c, lambda rs: rs[:-1]),
    "invalid label2": lambda c, s: rewrite(c.parent / "judge2.jsonl", set_first("label2", "MAYBE")),
    "duplicate judge2 row": lambda c, s: rewrite(c.parent / "judge2.jsonl", lambda rs: rs + rs[:1]),
}


@pytest.mark.parametrize("case", list(BAD_OTHER))
def test_bad_signals_or_judge2_fail_loudly(small_world, tmp_path, case):
    c, s = copy_world(small_world, tmp_path)
    BAD_OTHER[case](c, s)
    with pytest.raises(R.InputError):
        R.build_unit(c, s)


def test_cli_end_to_end(small_world, tmp_path, capsys):
    c, s = small_world
    assert R.main(["--claims", str(c), "--signals", str(s), "--out", str(tmp_path / "out"), "--n-boot", "100"]) == 0
    res = json.loads((tmp_path / "out" / "readers.json").read_text())
    assert set(res["confirmatory_F2"]) == {"R1", "R2", "R3"}
    csv = pd.read_csv(tmp_path / "out" / "readers.csv")
    assert {"confirmatory_F2.R1", "descriptive.auroc.v_closed_debate",
            "secondary_OPP_minus_SC_side_taking_positives"} <= set(csv["stat"])
    c2, s2 = copy_world(small_world, tmp_path / "bad")
    rewrite(c2.parent / "verifiers.jsonl", drop_key("v_closed"))
    assert R.main(["--claims", str(c2), "--signals", str(s2), "--out", str(tmp_path / "o2")]) == 2
    assert "INPUT ERROR" in capsys.readouterr().err
