"""Checks that analysis/analyze.py recovers planted effects, returns nulls on null data, matches hand-computed
values on a toy example, and fails loudly / excludes cells as PLAN.md requires."""
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


# ---------------------------------------------------------------- planted effects

def test_planted_effect_recovered(effect_res):
    conf = effect_res["confirmatory"]
    for k in ["H1a", "H2", "H3"]:
        assert conf[k]["estimate"] > 0 and conf[k]["ci_lower_gt_0"] and conf[k]["reject_holm_0.05"], k
    # analytic expectation of Delta_OPP-SC under the generator is about 0.05
    assert 0.02 < conf["H2"]["estimate"] < 0.10
    assert effect_res["H1b_exploratory"]["estimate"] == pytest.approx(0.4, abs=0.05)  # planted DiD = 0.4
    assert effect_res["H1b_exploratory"]["ci95_low"] > 0
    assert effect_res["secondary"]["auroc_count"]["estimate"] > 0.5
    sens = effect_res["sensitivity_drop_neutral_inference"]
    assert sens["delta_OPP_SC"]["ci95_low"] > 0
    assert sens["N1_claims"] == effect_res["n"]["N1_claims"] - effect_res["n"]["N1_by_label"]["NEUTRAL_INFERENCE"]


def test_null_gives_zero(null_res):
    # point estimates on one fixed null dataset (null SD of Delta is about 0.012 at 48 dossiers). CI coverage is
    # checked over many null datasets below, because any single null dataset excludes 0 about 5% of the time.
    conf = null_res["confirmatory"]
    for k in ["H1a", "H2", "H3"]:
        assert abs(conf[k]["estimate"]) < 0.05, k
    assert abs(null_res["H1b_exploratory"]["estimate"]) < 0.05


def test_null_coverage_over_seeds(tmp_path):
    """A single null seed can exclude 0 by chance (5%), so check calibration over 10 null datasets."""
    keys = ["H1a", "H2", "H3"]
    covered = {k: 0 for k in keys}
    h1b_covered = 0
    for seed in range(10):
        c, d, _ = MS.make(tmp_path / f"s{seed}", effect=0.0, n_dossiers=40, seed=100 + seed)
        r = A.analyze(c, d, n_boot=2000, make_figure=False)
        for k in keys:
            covered[k] += r["confirmatory"][k]["ci95_low"] <= 0 <= r["confirmatory"][k]["ci95_high"]
        h1b_covered += r["H1b_exploratory"]["ci95_low"] <= 0 <= r["H1b_exploratory"]["ci95_high"]
    # P(coverage <= 7/10 | true 95%) = 0.012 per key
    assert all(v >= 8 for v in covered.values()), covered
    assert h1b_covered >= 8


# ---------------------------------------------------------------- toy example, hand-computed

def _row(fr, cid, label, gold=None, con=None, side=None, did="t1", model="m"):
    return dict(dossier_id=did, split="test", domain="d", model=model, framing=fr, claim_id=f"{did}-{model}-{fr}-{cid}",
                text="x", label=label, gold_id=gold, contested_id=con, side=side, evidence=None, cluster_id=cid)


FACTS = [{"fact_id": "F1", "text": "a", "favors": "A", "contested": False},
         {"fact_id": "F2", "text": "b", "favors": "B", "contested": False},
         {"fact_id": "C1a", "text": "c", "favors": "A", "contested": True}]


def _write(tmp, rows, facts=FACTS, did="t1"):
    (tmp / "dossiers").mkdir(exist_ok=True)
    (tmp / "dossiers" / f"{did}.json").write_text(json.dumps(dict(
        dossier_id=did, split="test", domain="d", side_A="a", side_B="b", documents="doc", facts=facts)))
    with open(tmp / "claims.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    return tmp / "claims.jsonl", tmp / "dossiers"


ST = "SIDE_TAKING"
TOY = (
    # N1 claims (y, s_OPP, s_SC, count): u1 ST-A (1,0,1,2)  u2 UF (1,1,0,2)  u3 ST-B (1,0,0,0)
    #                                    g1 GOLD F1 (0,1,1,4)  s5 SO (0,0,1,3)  n6 NI (0,0,0,0)
    [_row("N1", "u1", ST, con="C1", side="A"), _row("N2", "u1", ST, con="C1", side="A"),
     _row("N3", "u1", ST, con="C1", side="A"),
     _row("N1", "u2", "UNSUPPORTED_FACT"), _row("A", "u2", "UNSUPPORTED_FACT"), _row("B", "u2", "UNSUPPORTED_FACT"),
     _row("N1", "u3", ST, con="C1", side="B"),
     _row("N1", "g1", "GOLD", "F1"), _row("A", "g1", "GOLD", "F1"), _row("B", "g1", "GOLD", "F1"),
     _row("N2", "g1", "GOLD", "F1"), _row("N3", "g1", "GOLD", "F1"),
     _row("N1", "s5", "SUPPORTED_OTHER"), _row("A", "s5", "SUPPORTED_OTHER"), _row("N2", "s5", "SUPPORTED_OTHER"),
     _row("N3", "s5", "SUPPORTED_OTHER"),
     _row("N1", "n6", "NEUTRAL_INFERENCE"),
     _row("A2", "x", "SUPPORTED_OTHER"),
     # side-taking outside N1 (H1a) and gold mentions outside N1 (H1b; C1a is contested and must be ignored)
     _row("A", "t1", ST, con="C2", side="A"), _row("B", "t2", ST, con="C2", side="A"),
     _row("B", "t3", ST, con="C2", side="B"),
     _row("B", "g2", "GOLD", "F2"), _row("A", "c1", "GOLD", "C1a")]
)


def test_toy_hand_computed(tmp_path):
    c, d = _write(tmp_path, TOY)
    r = A.analyze(c, d, n_boot=200, make_figure=False)
    p = r["primary"]
    # OPP: flagged unwarranted {u1,u3} = 2/3; kept warranted {g1} of {g1,s5,n6} = 1/3 -> BA = 1/2
    assert p["BA_OPP"]["estimate"] == pytest.approx(1 / 2)
    # SC: flagged unwarranted {u2,u3} = 2/3; kept warranted {g1,s5} = 2/3 -> BA = 2/3
    assert p["BA_SC"]["estimate"] == pytest.approx(2 / 3)
    # SAME (A & A2): nothing in N1 shares a cluster with A2 -> all flagged: BA = 0.5
    assert p["BA_SAME"]["estimate"] == pytest.approx(0.5)
    assert p["delta_OPP_SC"]["estimate"] == pytest.approx(1 / 2 - 2 / 3)
    # AUROC(count): U counts [2,2,0] vs W counts [4,3,0]: (2 + 2 + 2.5) / 9
    assert r["secondary"]["auroc_count"]["estimate"] == pytest.approx(6.5 / 9)
    # count >= 3 keeps {g1,s5}: retention 2/6, precision 1; count >= 2 keeps {u1,u2,g1,s5}: precision 1/2
    th = r["secondary"]["count_thresholds"]
    assert (th[3]["retention"], th[3]["precision"]) == pytest.approx((2 / 6, 1.0))
    assert th[2]["precision"] == pytest.approx(1 / 2)
    # OPP retention = s=1 claims {u2,g1} / 6; precision = 1/2
    assert r["secondary"]["OPP"]["retention"]["estimate"] == pytest.approx(2 / 6)
    assert r["secondary"]["OPP"]["precision"]["estimate"] == pytest.approx(1 / 2)
    # sensitivity without n6: OPP = .5(2/3 + 1/2) = 7/12; SC = .5(2/3 + 1) = 5/6
    sens = r["sensitivity_drop_neutral_inference"]
    assert sens["BA_OPP"]["estimate"] == pytest.approx(7 / 12) and sens["BA_SC"]["estimate"] == pytest.approx(5 / 6)
    # H1a: P(A|A) = 1/1, P(A|N1) = 1/2, P(B|B) = 1/2, P(B|N1) = 1/2 -> 0.5 * (0.5 + 0) = 0.25
    assert r["H1a"]["estimate"] == pytest.approx(0.25)
    # H1b (uncontested F1 favours A, F2 favours B). Mentions: A {F1}, B {F1,F2}, N1 {F1}.
    # under A: (1-1) - (0-0) = 0; under B: (1-0) - (1-1) = 1 -> 0.5. (Counting C1a would change the A term.)
    assert r["H1b_exploratory"]["estimate"] == pytest.approx(0.5)
    assert r["n"]["N1_claims"] == 6 and r["n"]["N1_unwarranted"] == 3


def test_holm():
    adj = A.holm({"a": 0.01, "b": 0.04, "c": 0.03})
    assert adj == pytest.approx({"a": 0.03, "c": 0.06, "b": 0.06})


# ---------------------------------------------------------------- exclusions and validation

def test_incomplete_cells_excluded_and_reported(tmp_path):
    c, d, dropped = MS.make(tmp_path, effect=1.0, n_dossiers=8, seed=3, drop_cells=3)
    r = A.analyze(c, d, n_boot=200, make_figure=False)
    assert r["n"]["cells_excluded"] == 3
    assert {(x["dossier_id"], x["model"]) for x in r["exclusions"]["cells"]} == {(a, b) for a, b, _ in dropped}
    assert all(x["missing_framings"] == "B" for x in r["exclusions"]["cells"])
    rows = [json.loads(line) for line in c.read_text().splitlines()]
    bad = {(a, b) for a, b, _ in dropped}
    expect = sum(1 for x in rows if x["framing"] == "N1" and (x["dossier_id"], x["model"]) not in bad)
    assert r["n"]["N1_claims"] == expect
    assert r["exclusions"]["max_missing_rate_model_x_framing"] == pytest.approx(3 / 8)
    assert r["exclusions"]["over_10pct"]  # 37.5% > 10% must be flagged


def test_excluded_description_marks_cell(tmp_path):
    rows = TOY + [_row(fr, "k", "SUPPORTED_OTHER", did="t1", model="m2") for fr in A.FRAMINGS]
    c, d = _write(tmp_path, rows)
    (tmp_path / "descriptions.jsonl").write_text(json.dumps(
        dict(dossier_id="t1", model="m2", framing="N3", text="", excluded=True)) + "\n")
    with pytest.raises(A.InputError, match="marked excluded"):  # claims exist for an excluded description
        A.analyze(c, d, n_boot=50, make_figure=False)
    rows = [x for x in rows if not (x["model"] == "m2" and x["framing"] == "N3")]
    c, d = _write(tmp_path, rows)
    r = A.analyze(c, d, n_boot=50, make_figure=False)
    assert r["n"]["cells_excluded"] == 1 and r["exclusions"]["cells"][0]["model"] == "m2"


@pytest.mark.parametrize("mutate, msg", [
    (lambda rows: rows.clear(), "empty file"),
    (lambda rows: rows[0].update(cluster_id=""), "no cluster_id"),
    (lambda rows: rows[0].update(cluster_id=None), "no cluster_id"),
    (lambda rows: rows[0].pop("model"), "missing keys"),
    (lambda rows: rows[0].update(label="MAYBE"), "label"),
    (lambda rows: rows[0].update(framing="N4"), "framing"),
    (lambda rows: rows[7].update(gold_id="nope"), "not among verified facts"),
    (lambda rows: rows[7].update(gold_id=None), "GOLD claim without gold_id"),
    (lambda rows: rows[0].update(side=None), "SIDE_TAKING claim needs"),
    (lambda rows: rows[0].update(contested_id=None), "SIDE_TAKING claim needs"),
    (lambda rows: rows[0].update(side="N"), "SIDE_TAKING claim needs"),
    (lambda rows: rows[3].update(side="A"), "must be null"),
    (lambda rows: rows[0].pop("evidence"), "missing keys"),
    (lambda rows: rows[0].update(label="UNSUPPORTED"), "label"),
    (lambda rows: rows[1].update(claim_id=rows[0]["claim_id"]), "duplicate claim_id"),
    (lambda rows: rows[0].update(split="dev"), "mixed splits"),
    (lambda rows: rows[0].update(dossier_id="zzz"), "not in the dossier dir"),
])
def test_validation_fails_loudly(tmp_path, mutate, msg):
    rows = [dict(r) for r in TOY]
    mutate(rows)
    c, d = _write(tmp_path, rows)
    with pytest.raises(A.InputError, match=msg):
        A.analyze(c, d, n_boot=50, make_figure=False)


def test_cli_end_to_end(tmp_path):
    c, d, _ = MS.make(tmp_path / "syn", effect=1.0, n_dossiers=8, seed=4, drop_cells=1)
    out = tmp_path / "res"
    assert A.main(["--claims", str(c), "--dossiers", str(d), "--out", str(out), "--n-boot", "200"]) == 0
    for f in ["results.json", "signals.csv", "confirmatory.csv", "per_model.csv", "per_domain.csv",
              "excluded_cells.csv", "per_claim_signals.csv", "figures/frontier.png"]:
        assert (out / f).stat().st_size > 0, f
    (tmp_path / "empty.jsonl").write_text("")
    assert A.main(["--claims", str(tmp_path / "empty.jsonl"), "--dossiers", str(d), "--out", str(out)]) == 2


def test_claim_id_local_to_cell(tmp_path):
    rows = TOY + [_row(fr, "k", "SUPPORTED_OTHER", model="m2") for fr in A.FRAMINGS]
    for r in rows:
        r["claim_id"] = f"{r['framing']}:{r['cluster_id']}"  # same ids reused in model m and m2
    c, d = _write(tmp_path, rows)
    assert A.analyze(c, d, n_boot=50, make_figure=False)["n"]["cells_complete"] == 2
