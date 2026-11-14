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
    # analytic expectation of Delta_OPP-SC under the generator is about 0.075
    assert 0.03 < conf["H2"]["estimate"] < 0.12
    assert effect_res["H1b_exploratory"]["ci95_low"] > 0
    assert effect_res["secondary"]["auroc_count"]["estimate"] > 0.5


def test_null_gives_zero(null_res):
    conf = null_res["confirmatory"]
    for k in ["H2", "H3"]:  # the primary Deltas on one fixed null dataset
        assert conf[k]["ci95_low"] <= 0 <= conf[k]["ci95_high"], k
        assert not conf[k]["reject_holm_0.05"], k
    assert abs(conf["H2"]["estimate"]) < 0.04 and abs(conf["H3"]["estimate"]) < 0.04


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

def _row(fr, cid, label, gold=None, did="t1", model="m"):
    return dict(dossier_id=did, split="test", domain="d", model=model, framing=fr, claim_id=f"{did}-{model}-{fr}-{cid}",
                text="x", label=label, gold_id=gold, cluster_id=cid)


def _write(tmp, rows, facts=None, did="t1"):
    (tmp / "dossiers").mkdir(exist_ok=True)
    facts = facts or [{"fact_id": "g1", "text": "a", "favors": "A", "contested": False},
                      {"fact_id": "g2", "text": "b", "favors": "B", "contested": False}]
    (tmp / "dossiers" / f"{did}.json").write_text(json.dumps(dict(
        dossier_id=did, split="test", domain="d", side_A="a", side_B="b", documents="doc", facts=facts)))
    with open(tmp / "claims.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    return tmp / "claims.jsonl", tmp / "dossiers"


TOY = (
    # N1 claims (y, s_OPP, s_SC, count):  c1 U (0,1,2)  c2 U (1,0,2)  c3 U (0,0,0)  c4 G (1,1,4)  c5 S (0,1,3)
    [_row("N1", "u1", "UNSUPPORTED"), _row("N2", "u1", "UNSUPPORTED"), _row("N3", "u1", "UNSUPPORTED"),
     _row("N1", "u2", "UNSUPPORTED"), _row("A", "u2", "UNSUPPORTED"), _row("B", "u2", "UNSUPPORTED"),
     _row("N1", "u3", "UNSUPPORTED"),
     _row("N1", "g1", "GOLD", "g1"), _row("A", "g1", "GOLD", "g1"), _row("B", "g1", "GOLD", "g1"),
     _row("N2", "g1", "GOLD", "g1"), _row("N3", "g1", "GOLD", "g1"),
     _row("N1", "s5", "SUPPORTED_OTHER"), _row("A", "s5", "SUPPORTED_OTHER"), _row("N2", "s5", "SUPPORTED_OTHER"),
     _row("N3", "s5", "SUPPORTED_OTHER"),
     _row("A2", "x", "SUPPORTED_OTHER")]
)


def test_toy_hand_computed(tmp_path):
    c, d = _write(tmp_path, TOY)
    r = A.analyze(c, d, n_boot=200, make_figure=False)
    p = r["primary"]
    # OPP: flagged unsupported {c1,c3} = 2/3; kept supported {c4} = 1/2  -> BA = 7/12
    assert p["BA_OPP"]["estimate"] == pytest.approx(7 / 12)
    # SC: flagged unsupported {c2,c3} = 2/3; kept supported {c4,c5} = 1 -> BA = 5/6
    assert p["BA_SC"]["estimate"] == pytest.approx(5 / 6)
    # SAME (A & A2): nothing in N1 shares a cluster with A2 -> all flagged: BA = 0.5
    assert p["BA_SAME"]["estimate"] == pytest.approx(0.5)
    assert p["delta_OPP_SC"]["estimate"] == pytest.approx(7 / 12 - 5 / 6)
    # AUROC(count): U counts [2,2,0] all below S counts [4,3] -> 1.0
    assert r["secondary"]["auroc_count"]["estimate"] == pytest.approx(1.0)
    # count >= 3 keeps {c4,c5}: retention 2/5, precision 1; count >= 2 keeps {c1,c2,c4,c5}: precision 1/2
    th = r["secondary"]["count_thresholds"]
    assert (th[3]["retention"], th[3]["precision"]) == pytest.approx((2 / 5, 1.0))
    assert th[2]["precision"] == pytest.approx(1 / 2)
    # OPP retention = s=1 claims {c2,c4} / 5; precision = 1/2
    assert r["secondary"]["OPP"]["retention"]["estimate"] == pytest.approx(2 / 5)
    assert r["secondary"]["OPP"]["precision"]["estimate"] == pytest.approx(1 / 2)
    # H1a: unsupported A=1, B=1, N1=3 -> 1 - 3 = -2. H1b: A mentions ally g1 (+1); B mentions only opponent g1 (-1)
    assert r["H1a"]["estimate"] == pytest.approx(-2)
    assert r["H1b_exploratory"]["estimate"] == pytest.approx(0)
    assert r["n"]["N1_claims"] == 5 and r["n"]["N1_unsupported"] == 3


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
    (lambda rows: rows[0].update(gold_id="g1"), "must be null"),
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
