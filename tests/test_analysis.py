"""Checks that analysis/analyze.py (PLAN v3) recovers planted effects, returns calibrated nulls, matches
hand-computed values on a toy example, runs TOST correctly, and fails loudly / excludes cells as required."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "analysis"))
import analyze as A  # noqa: E402
import make_synthetic as MS  # noqa: E402


@pytest.fixture(scope="module")
def effect_res(tmp_path_factory):
    c, d, _ = MS.make(tmp_path_factory.mktemp("eff"), effect=1.0, seed=1)
    return A.analyze(c, d, make_figure=False)


@pytest.fixture(scope="module")
def null_res(tmp_path_factory):
    c, d, _ = MS.make(tmp_path_factory.mktemp("null"), effect=0.0, seed=2)
    return A.analyze(c, d, make_figure=False)


# ---------------------------------------------------------------- planted effects and nulls

def test_planted_effect_recovered(effect_res):
    conf = effect_res["confirmatory"]
    for k in ["H1a", "H2", "H3"]:
        assert conf[k]["estimate"] > 0 and conf[k]["supported"] and conf[k]["holm_one_sided_lower"] > 0, k
    assert not conf["H2"]["tost_equivalent_within_0.03"] and not conf["H3"]["tost_equivalent_within_0.03"]
    sec = effect_res["secondary"]
    assert sec["H1b_did_exploratory"]["estimate"] == pytest.approx(0.4, abs=0.06)  # planted DiD = 0.4
    assert sec["matched_retention_precision"]["delta_OPP_SC"]["ci95_low"] > 0
    # the planted mechanism acts on SIDE_TAKING only: the error-type interaction must be positive
    assert sec["error_type_interaction_OPP_SC"]["estimate"] > 0
    assert sec["per_error_type"]["SIDE_TAKING"]["delta_OPP_SC"]["ci95_low"] > 0
    v = sec["verifiers"]
    assert v["auroc_v_file"]["estimate"] > v["auroc_v_closed"]["estimate"] > 0.5
    assert effect_res["validation"]["presence_validity"]["agreement"] == 1.0  # generator is internally consistent
    assert 0.6 < effect_res["validation"]["kappa_y"]["overall"]["kappa"] < 0.95  # 10% label noise in judge2
    assert effect_res["sensitivity"]["drop_neutral_inference"]["N1_claims"] == (
        effect_res["n"]["N1_claims"] - effect_res["n"]["N1_by_label"]["NEUTRAL_INFERENCE"])


def test_null_point_estimates(null_res):
    # one fixed null dataset: point estimates near 0 (null SD of Delta AUROC is about 0.02 at 48 dossiers).
    # CI coverage is checked over many null datasets below, since any single one excludes 0 about 5% of the time.
    for k in ["H1a", "H2", "H3"]:
        assert abs(null_res["confirmatory"][k]["estimate"]) < 0.06, k
    assert abs(null_res["secondary"]["H1b_did_exploratory"]["estimate"]) < 0.05


def test_null_coverage_over_seeds(tmp_path):
    keys = ["H1a", "H2", "H3"]
    covered, rejected = dict.fromkeys(keys, 0), 0
    for seed in range(10):
        c, d, _ = MS.make(tmp_path / f"s{seed}", effect=0.0, n_dossiers=40, seed=100 + seed)
        r = A.analyze(c, d, n_boot=1000, make_figure=False)
        for k in keys:
            covered[k] += r["confirmatory"][k]["ci95_low"] <= 0 <= r["confirmatory"][k]["ci95_high"]
        rejected += any(r["confirmatory"][k]["supported"] for k in keys)
    assert all(v >= 8 for v in covered.values()), covered  # P(<= 7/10 | 95% coverage) = 0.012
    assert rejected <= 2  # familywise error under Holm should be <= 5%


def test_tost_declares_equivalence_on_large_null(tmp_path):
    c, d, _ = MS.make(tmp_path, effect=0.0, n_dossiers=200, seed=11)
    conf = A.analyze(c, d, n_boot=2000, make_figure=False)["confirmatory"]
    for k in ("H2", "H3"):
        assert -A.TOST_MARGIN < conf[k]["ci90_low"] and conf[k]["ci90_high"] < A.TOST_MARGIN, k
        assert conf[k]["tost_equivalent_within_0.03"] and not conf[k]["supported"], k


# ---------------------------------------------------------------- toy example, hand-computed

FACTS = [{"fact_id": "F1", "text": "a", "favors": "A", "contested": False},
         {"fact_id": "F2", "text": "b", "favors": "B", "contested": False},
         {"fact_id": "C1a", "text": "c", "favors": "A", "contested": True}]
ST = "SIDE_TAKING"
#            label, gold, side,   A     A2    B     N2    N3    P1    P2
N1_TOY = {"c1": (ST, None, "A", "AS", "AS", "CO", "AS", "AS", "AS", "SI"),
          "c2": ("UNSUPPORTED_FACT", None, None, "SI", "SI", "SI", "AS", "SI", "SI", "SI"),
          "c3": ("GOLD", "F1", None, "AS", "AS", "AS", "AS", "AS", "AS", "AS"),
          "c4": ("SUPPORTED_OTHER", None, None, "AS", "SI", "AS", "SI", "AS", "AS", "AS"),
          "c5": ("NEUTRAL_INFERENCE", None, None, "AS", "AS", "SI", "AS", "AS", "SI", "SI")}
SIDE_TOY = [("A", "g", "GOLD", "F1", None), ("A", "c", "GOLD", "C1a", None), ("A", "s1", ST, None, "A"),
            ("A", "s2", ST, None, "B"), ("B", "g", "GOLD", "F1", None), ("B", "f2", "GOLD", "F2", None),
            ("B", "s3", ST, None, "B")]
VERD = {"AS": "ASSERTS", "CO": "CONTRADICTS", "SI": "SILENT"}
V_TOY = {"c1": (0.9, 0.8), "c2": (0.2, 0.7), "c3": (0.1, 0.1), "c4": (0.3, 0.2), "c5": (0.5, 0.3)}
J2_TOY = {"c1": ST, "c2": "SUPPORTED_OTHER", "c3": "GOLD", "c4": "UNSUPPORTED_FACT", "c5": "NEUTRAL_INFERENCE"}


def _claim(fr, cid, label, gold=None, side=None, model="m", did="t1", repaired=None):
    return dict(dossier_id=did, split="test", domain="d", model=model, framing=fr, claim_id=f"{fr}:{cid}", text="x",
                label=label, gold_id=gold, contested_id=("C1" if label == ST and side else None), side=side,
                evidence=None, repaired=repaired)


def toy_rows(models=("m",)):
    out = {k: [] for k in ("claims", "descriptions", "presence", "verifiers", "judge2")}
    for m in models:
        out["descriptions"] += [dict(dossier_id="t1", model=m, framing=f, text="t", n_words=1, excluded=False)
                                for f in A.FRAMINGS]
        for cid, (lab, gold, side, *v) in N1_TOY.items():
            out["claims"].append(_claim("N1", cid, lab, gold, side, m))
            out["presence"] += [dict(dossier_id="t1", model=m, claim_id=f"N1:{cid}", framing=f, verdict=VERD[x])
                                for f, x in zip(A.OTHERS, v)]
            out["verifiers"].append(dict(dossier_id="t1", model=m, claim_id=f"N1:{cid}", v_closed=V_TOY[cid][0],
                                         v_file=V_TOY[cid][1]))
            out["judge2"].append(dict(dossier_id="t1", model=m, claim_id=f"N1:{cid}", label2=J2_TOY[cid]))
        out["claims"] += [_claim(fr, cid, lab, gold, side, m) for fr, cid, lab, gold, side in SIDE_TOY]
        # harness repairs: a side-less SIDE_TAKING in A (must not enter H1a) and a relabelled claim in B
        out["claims"] += [_claim("A", "r1", ST, model=m, repaired="side_missing"),
                          _claim("B", "r2", "SUPPORTED_OTHER", model=m, repaired="gold_id_missing")]
    return out


def write(tmp, rows, facts=FACTS):
    (tmp / "dossiers").mkdir(parents=True, exist_ok=True)
    (tmp / "dossiers" / "t1.json").write_text(json.dumps(dict(
        dossier_id="t1", split="test", domain="d", side_A={}, side_B={}, documents="doc", facts=facts, settled=[])))
    for name, rs in rows.items():
        with open(tmp / f"{name}.jsonl", "w") as f:
            for r in rs:
                f.write(json.dumps(r) + "\n")
    return tmp / "claims.jsonl", tmp / "dossiers"


def test_toy_hand_computed(tmp_path):
    r = A.analyze(*write(tmp_path, toy_rows()), n_boot=200, make_figure=False)
    au = r["auroc"]
    # suspicion = 2 - k. y = 1: c1, c2; y = 0: c3, c4, c5.
    # OPP scores U [1, 2] vs W [0, 0, 1]: (1 + 1 + .5) + 3 = 5.5 / 6
    assert au["OPP"]["estimate"] == pytest.approx(5.5 / 6)
    # SC  U [0, 1] vs W [0, 1, 0]: (.5 + 0 + .5) + (1 + .5 + 1) = 3.5 / 6
    assert au["SC"]["estimate"] == pytest.approx(3.5 / 6)
    # DIV U [1, 2] vs W [0, 0, 2]: (1 + 1 + 0) + (1 + 1 + .5) = 4.5 / 6
    assert au["DIV"]["estimate"] == pytest.approx(4.5 / 6)
    # SAME U [0, 2] vs W [0, 1, 0]: (.5 + 0 + .5) + 3 = 4 / 6
    assert au["SAME"]["estimate"] == pytest.approx(4 / 6)
    conf = r["confirmatory"]
    assert conf["H2"]["estimate"] == pytest.approx(2 / 6) and conf["H3"]["estimate"] == pytest.approx(1 / 6)
    sec = r["secondary"]
    # AND rule (OPP keeps k = 2: c3, c4): flags both U (1), keeps 2/3 W -> BA 5/6; retention 2/5; precision 1
    a = sec["and_rule"]["OPP"]
    assert (a["BA"]["estimate"], a["retention"]["estimate"], a["precision"]["estimate"]) == pytest.approx((5 / 6, .4, 1))
    # matched retention 2/5 = keep the 2 least suspicious. OPP {c3,c4} = 1; DIV {c3,c4} = 1; v_closed {c3 .1, c2 .2}
    # = 1/2; v_file {c3, c4} = 1; SC has a 3-way tie at 0 (c1, c3, c5) broken by the seeded key: 1/2 or 1
    mr = sec["matched_retention_precision"]
    assert mr["retention_target"]["estimate"] == pytest.approx(0.4)
    assert (mr["OPP"]["estimate"], mr["DIV"]["estimate"], mr["v_closed"]["estimate"], mr["v_file"]["estimate"]) == \
        pytest.approx((1, 1, 0.5, 1))
    assert mr["SC"]["estimate"] in (pytest.approx(0.5), pytest.approx(1.0))
    # verifiers: v_closed U [.9, .2] vs W [.1, .3, .5] -> (3 + 1)/6; v_file separates perfectly -> 1
    # combo = mean(rank v_closed, rank 2-k_OPP): c1 4.25, c2 3.5, c3 1.25, c4 2.25, c5 3.75 -> (3 + 2)/6
    v = sec["verifiers"]
    assert v["auroc_v_closed"]["estimate"] == pytest.approx(4 / 6) and v["auroc_v_file"]["estimate"] == 1
    assert v["auroc_combo"]["estimate"] == pytest.approx(5 / 6)
    # error type: SIDE_TAKING positives only (c1) vs all W, OPP: 1 vs [0, 0, 1] -> 2.5/3
    assert sec["per_error_type"]["SIDE_TAKING"]["auroc_OPP"]["estimate"] == pytest.approx(2.5 / 3)
    # CONTRADICTS in OPP: 1 of 10 cells; among y = 1 claims 1 of 4
    co = sec["contradicts_rate_by_pair"]["OPP"]
    assert co["rate_all"]["estimate"] == pytest.approx(0.1) and co["rate_y1"]["estimate"] == pytest.approx(0.25)
    # H1a: P(A|A) = 1/2, P(A|N1) = 1, P(B|B) = 1, P(B|N1) = 0 -> 0.5 * (-0.5 + 1) = 0.25
    # (the side_missing SIDE_TAKING claim in A is excluded; counting it would make P(A|A) = 1/3)
    assert conf["H1a"]["estimate"] == pytest.approx(0.25)
    assert conf["H1a"]["n_side_taking"] == {"A": 2, "B": 1, "N1": 1}
    assert conf["H1a"]["n_side_missing_excluded"] == {"A": 1, "B": 0, "N1": 0}
    assert r["n"]["repaired_in_complete_cells"]["gold_id_missing"] == {"A": 0, "B": 1, "N1": 0}
    # H1b: uncontested F1 (A), F2 (B). Mentions: A {F1} (C1a ignored), B {F1, F2}, N1 {F1}.
    # under A: (1 - 1) - (0 - 0) = 0; under B: (1 - 0) - (1 - 1) = 1 -> 0.5
    assert sec["H1b_did_exploratory"]["estimate"] == pytest.approx(0.5)
    # sensitivity: drop NEUTRAL_INFERENCE (c5): OPP U [1, 2] vs W [0, 0] -> 1
    assert r["sensitivity"]["drop_neutral_inference"]["auroc_OPP"]["estimate"] == pytest.approx(1)
    # judge2 agrees on c1, c3, c5: OPP U [1] vs W [0, 1] -> 0.75
    assert r["sensitivity"]["judge2_agrees"]["auroc_OPP"]["estimate"] == pytest.approx(0.75)
    # kappa: y = 11000, y2 = 10010 -> po = .6, pe = .4*.4 + .6*.6 = .52 -> (.6 - .52)/.48 = 1/6
    kap = r["validation"]["kappa_y"]
    assert kap["overall"]["kappa"] == pytest.approx(1 / 6) and kap["overall"]["n"] == 5
    assert kap[f"excluding_{A.QWEN}"]["n"] == 5
    # presence validity: c3 (F1) ASSERTS in A and B, and both A and B cite F1 -> 2/2
    pv = r["validation"]["presence_validity"]
    assert (pv["n_pairs"], pv["agreement"]) == (2, 1.0)


def test_presence_validity_detects_mismatch(tmp_path):
    rows = toy_rows()
    for p in rows["presence"]:
        if p["claim_id"] == "N1:c3" and p["framing"] == "B":
            p["verdict"] = "SILENT"
    pv = A.analyze(*write(tmp_path, rows), n_boot=50, make_figure=False)["validation"]["presence_validity"]
    assert pv["agreement"] == pytest.approx(0.5) and pv["labels_only"] == 1


def test_holm():
    adj, rank = A.holm({"a": 0.01, "b": 0.04, "c": 0.03})
    assert adj == pytest.approx({"a": 0.03, "c": 0.06, "b": 0.06}) and rank == {"a": 0, "c": 1, "b": 2}


def test_holm_level_lower_bound(tmp_path):
    r = A.analyze(*write(tmp_path, toy_rows()), n_boot=200, make_figure=False)["confirmatory"]
    levels = sorted(c["holm_alpha"] for c in r.values())
    assert levels == pytest.approx([0.05 / 3, 0.05 / 2, 0.05])


# ---------------------------------------------------------------- exclusions

def test_incomplete_cells_excluded_and_reported(tmp_path):
    c, d, dropped = MS.make(tmp_path, effect=1.0, n_dossiers=8, seed=3, drop_cells=3)
    r = A.analyze(c, d, n_boot=200, make_figure=False)
    assert r["n"]["cells_excluded"] == 3
    assert {(x["dossier_id"], x["model"]) for x in r["exclusions"]["cells"]} == set(dropped)
    assert all("P1" in x["reason"] for x in r["exclusions"]["cells"])
    rows = [json.loads(line) for line in c.read_text().splitlines()]
    expect = sum(1 for x in rows if x["framing"] == "N1" and (x["dossier_id"], x["model"]) not in set(dropped))
    assert r["n"]["N1_claims"] == expect
    assert r["exclusions"]["max_rate_model_x_framing"] == pytest.approx(3 / 8)
    assert r["exclusions"]["over_10pct"]


@pytest.mark.parametrize("mutate, reason", [
    (lambda r: r["presence"].pop(0), "lack presence rows"),
    (lambda r: r.__setitem__("claims", [c for c in r["claims"] if not (c["model"] == "m" and c["framing"] == "B")]),
     "no labelled claims for: B"),
    (lambda r: r.__setitem__("descriptions", [x for x in r["descriptions"]
                                              if not (x["model"] == "m" and x["framing"] == "P2")]),
     "missing or excluded descriptions: P2"),
])
def test_incomplete_cell_reasons(tmp_path, mutate, reason):
    rows = toy_rows(models=("m", "m2"))
    mutate(rows)
    r = A.analyze(*write(tmp_path, rows), n_boot=50, make_figure=False)
    assert r["n"]["cells_complete"] == 1 and r["n"]["cells_excluded"] == 1
    assert r["exclusions"]["cells"][0]["model"] == "m" and reason in r["exclusions"]["cells"][0]["reason"]


# ---------------------------------------------------------------- loud validation

def _set(rows, name, i, **kw):
    rows[name][i].update(kw)


def _excl(rows, framing):
    for x in rows["descriptions"]:
        if x["framing"] == framing:
            x["excluded"] = True


@pytest.mark.parametrize("mutate, msg", [
    (lambda r: r["claims"].clear(), "empty file"),
    (lambda r: r["claims"][0].pop("model"), "missing keys"),
    (lambda r: r["claims"][0].pop("evidence"), "missing keys"),
    (lambda r: _set(r, "claims", 0, label="UNSUPPORTED"), "label"),
    (lambda r: _set(r, "claims", 0, framing="A2"), "framing"),
    (lambda r: _set(r, "claims", 2, gold_id="nope"), "not among verified facts"),
    (lambda r: _set(r, "claims", 2, gold_id=None), "GOLD claim without gold_id"),
    (lambda r: _set(r, "claims", 0, side=None), "SIDE_TAKING claim needs"),
    (lambda r: _set(r, "claims", 0, contested_id=None), "SIDE_TAKING claim needs"),
    (lambda r: _set(r, "claims", 1, side="A"), "must be null"),
    (lambda r: r["claims"][0].pop("repaired"), "missing keys"),
    (lambda r: _set(r, "claims", 0, repaired="other"), "repaired"),
    (lambda r: _set(r, "claims", 1, repaired="side_missing"), "side_missing requires"),
    (lambda r: _set(r, "claims", 0, repaired="side_missing"), "side_missing requires"),  # side still set
    (lambda r: _set(r, "claims", 2, repaired="gold_id_missing"), "gold_id_missing requires"),
    (lambda r: _set(r, "claims", 1, claim_id="N1:c1"), "duplicate rows"),
    (lambda r: _set(r, "claims", 0, split="dev"), "mixed splits"),
    (lambda r: _set(r, "claims", 0, dossier_id="zzz"), "not in the dossier dir"),
    (lambda r: r.pop("presence"), "presence.jsonl: file not found"),
    (lambda r: r.pop("descriptions"), "descriptions.jsonl: file not found"),
    (lambda r: _set(r, "presence", 0, verdict="MAYBE"), "verdict"),
    (lambda r: _set(r, "presence", 0, framing="N1"), "framing"),
    (lambda r: _set(r, "presence", 0, claim_id="A:g"), "not N1 claims"),
    (lambda r: _set(r, "presence", 1, framing="A"), "duplicate rows"),
    (lambda r: _set(r, "verifiers", 0, v_closed=1.5), "must be a number in"),
    (lambda r: _set(r, "verifiers", 0, v_file="high"), "must be a number in"),
    (lambda r: _set(r, "judge2", 0, label2="BAD"), "label2"),
    (lambda r: _set(r, "judge2", 0, claim_id="N1:zz"), "not N1 claims"),
    (lambda r: _set(r, "descriptions", 0, excluded="no"), "non-boolean"),
    (lambda r: _excl(r, "B"), "claims exist for descriptions marked excluded"),
    (lambda r: _excl(r, "P1"), "presence rows exist for descriptions marked excluded"),
])
def test_validation_fails_loudly(tmp_path, mutate, msg):
    rows = toy_rows()
    mutate(rows)
    with pytest.raises(A.InputError, match=msg):
        A.analyze(*write(tmp_path, rows), n_boot=50, make_figure=False)


def test_optional_files_absent(tmp_path):
    rows = toy_rows()
    del rows["verifiers"], rows["judge2"]
    r = A.analyze(*write(tmp_path, rows), n_boot=50, make_figure=False)
    assert r["secondary"]["verifiers"] is None and r["validation"]["kappa_y"] is None
    assert r["sensitivity"]["judge2_agrees"] is None and r["auroc"]["OPP"]["estimate"] == pytest.approx(5.5 / 6)


def test_cli_end_to_end(tmp_path):
    c, d, _ = MS.make(tmp_path / "syn", effect=1.0, n_dossiers=8, seed=4, drop_cells=1)
    out = tmp_path / "res"
    assert A.main(["--claims", str(c), "--dossiers", str(d), "--out", str(out), "--n-boot", "200"]) == 0
    for f in ["results.json", "signals.csv", "confirmatory.csv", "per_model.csv", "per_domain.csv",
              "per_error_type.csv", "sensitivity.csv", "contradicts.csv", "excluded_cells.csv",
              "per_claim_signals.csv", "per_cell_drift.csv", "figures/frontier.png"]:
        assert (out / f).stat().st_size > 0, f
    (tmp_path / "empty.jsonl").write_text("")
    assert A.main(["--claims", str(tmp_path / "empty.jsonl"), "--dossiers", str(d), "--out", str(out)]) == 2
