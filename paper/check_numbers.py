"""Check that the paper and deck quote the committed result files exactly.

Each entry: the string as printed, and the value it must equal (recomputed here from analysis/results/test/).
Usage: paper/.venv/bin/python paper/check_numbers.py   (exit 1 on any mismatch or missing string)
"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "analysis" / "results" / "test"
res, rd = json.loads((R / "results.json").read_text()), json.loads((R / "readers.json").read_text())
ax, ex = json.loads((R / "audit_extras.json").read_text()), json.loads((R / "exploratory_final.json").read_text())
sig = pd.read_csv(R / "per_claim_signals.csv")
f3 = lambda v: f"{v:.3f}"
ci = lambda d: f"[{d['ci95_low']:.3f}, {d['ci95_high']:.3f}]".replace("-", "−")
sgn = lambda v: (f"+{v:.3f}" if v >= 0 else f"−{abs(v):.3f}")
A = rd["descriptive"]["auroc"]
both = lambda p, y: (sig[f"k_{p}"] == 2)[sig.y == y]
rc = json.loads((ROOT / "analysis" / "results" / "test_r1" / "replicate_compare.json").read_text())
va = json.loads((ROOT / "analysis/results/validity_audit/results.json").read_text())
rr = rc["test_r1"]; rp = rr["tests"]
contra = lambda p, y: (sig[f"contra_{p}"] > 0)[sig.y == y].mean()

CHECKS = {  # printed string -> source description
    "4,486": res["n"]["N1_claims"] == 4486, "327": res["n"]["N1_unwarranted"] == 327,
    sgn(res["confirmatory"]["H1a"]["estimate"]) + " " + ci(res["confirmatory"]["H1a"]): True,
    sgn(res["delta_auroc"]["OPP_SC"]["estimate"]) + " " + ci(res["delta_auroc"]["OPP_SC"]): True,
    sgn(res["delta_auroc"]["OPP_DIV"]["estimate"]) + " " + ci(res["delta_auroc"]["OPP_DIV"]): True,
    sgn(rd["confirmatory_F2"]["R1"]["estimate"]) + " " + ci(rd["confirmatory_F2"]["R1"]): True,
    sgn(rd["confirmatory_F2"]["R2"]["estimate"]) + " " + ci(rd["confirmatory_F2"]["R2"]): True,
    ci(rd["confirmatory_F2"]["R3"]): True,
    f3(A["OPP"]["estimate"]) + " " + ci(A["OPP"]): True, f3(A["SC"]["estimate"]) + " " + ci(A["SC"]): True,
    f3(A["DIV"]["estimate"]) + " " + ci(A["DIV"]): True, f3(A["v_closed_none"]["estimate"]) + " " + ci(A["v_closed_none"]): True,
    f3(A["v_closed"]["estimate"]): True, f3(A["v_closed_sc"]["estimate"]): True, f3(A["v_closed_div"]["estimate"]): True,
    f3(A["v_closed_debate"]["estimate"]): True, f3(A["xf_none"]["estimate"]): True, f3(A["xf_opp"]["estimate"]): True,
    f3(res["auroc"]["SAME"]["estimate"]): True,
    sgn(rd["secondary_OPP_minus_SC_side_taking_positives"]["estimate"]) + " " + ci(rd["secondary_OPP_minus_SC_side_taking_positives"]): True,
    f3(res["secondary"]["verifiers"]["auroc_combo"]["estimate"]): True,
    f3(ax["judge_labels"]["random"]["estimate"]): True, f3(ax["judge_labels"]["length_words"]["estimate"]): True,
    f3(ax["judge_labels"]["evaluative_words"]["estimate"]): True,
    f3(ex["glm52"]["xs_none"]["estimate"]) + " " + ci(ex["glm52"]["xs_none"]): True,
    f3(ex["glm52"]["xs_opp"]["estimate"]) + " " + ci(ex["glm52"]["xs_opp"]): True,
    f3(ex["glm52"]["vs_file"]["estimate"]) + " " + ci(ex["glm52"]["vs_file"]): True,
    f3(ex["glm52"]["vs_file_minus_xs_none"]["estimate"]) + " " + ci(ex["glm52"]["vs_file_minus_xs_none"]): True,
    f3(ex["glm52"]["vs_file_minus_xs_opp"]["estimate"]): True,
    sgn(ax["judge_labels"]["delta_xs_opp_minus_xs_none"]["estimate"]) + " " + ci(ax["judge_labels"]["delta_xs_opp_minus_xs_none"]): True,
    f3(ex["contradiction_counting"]["OPP"]["estimate"]) + " " + ci(ex["contradiction_counting"]["OPP"]): True,
    f"κ = {res['validation']['kappa_y']['overall']['kappa']:.2f}": True,
    f"{100 * res['validation']['presence_validity']['agreement']:.0f}%": True,
    f"κ {res['validation']['presence_validity']['kappa']:.2f}": True,
    sgn(res["secondary"]["H1b_did_exploratory"]["estimate"]) + " " + ci(res["secondary"]["H1b_did_exploratory"]): True,
    f"{100 * both('OPP', 0).mean():.0f}%": True, f"{100 * both('SC', 0).mean():.0f}%": True,
    f"{both('OPP', 1).sum()} and {both('SC', 1).sum()} of 327": True,
    f"{100 * contra('OPP', 0):.1f}%": True, f"{100 * contra('SC', 0):.1f}%": True,
    f"{100 * (1 - both('OPP', 0).mean() - contra('OPP', 0)):.0f}%": True,  # silent share, opposed warranted (39%)
    # independent rerun (analysis/replicate.py -> results/test_r1/replicate_compare.json)
    sgn(rp["H2"]["estimate"]) + " " + ci(rp["H2"]): True, sgn(rp["H3"]["estimate"]) + " " + ci(rp["H3"]): True,
    sgn(rp["H1a"]["estimate"]): True, sgn(rp["R1"]["estimate"]): True, sgn(rp["R2"]["estimate"]) + " " + ci(rp["R2"]): True,
    f3(rr["auroc"]["OPP"]["estimate"]) + ", SC " + f3(rr["auroc"]["SC"]["estimate"]): True,
    "Same decision on all six tests": all(rc["same_decision"].values()),
    # third-family AI annotator (analysis/ai_annotator.py)
    f"rerun: {100 * rr['warranted_repeated_by_both']['OPP']:.0f}% and {100 * rr['warranted_repeated_by_both']['SC']:.0f}%": True,
}
DECK = ["0.66", "0.70", "0.75", "+0.145", "[0.100, 0.191]", "1.3%", "39%", "29%", "0.51", "0.83–0.84", "0.91", "+0.035", "0.67", "κ = 0.81"]

# Supplemental audit: check both judges, coverage and every Table 3 paired interval.
for judge in ('judge1', 'judge2'):
    k = va['agreement'][judge]['kappa']
    CHECKS[f"κ = {k['estimate']:.3f} [{k['ci95_low']:.3f}, {k['ci95_high']:.3f}]"] = True
CHECKS['Coverage was 99/100: 55 W, 44 U, one abstention.'] = va['coverage']['labelled'] == 99
for run, subsets in va['runs'].items():
    for subset, values in subsets.items():
        if subset == 'original':
            continue
        for name in ('OPP_minus_SC', 'reader_minus_SC'):
            d = values['differences'][name]
            text = (f"{d['estimate']:+.3f} [{d['ci95_low']:+.3f}, {d['ci95_high']:+.3f}]"
                    .replace('-', '−').replace('[+', '[').replace(', +', ', '))
            CHECKS[text] = True


def main():
    paper = (ROOT / "paper" / "paper.md").read_text().replace("-0.", "−0.")
    deck = (ROOT / "paper" / "deck.html").read_text()
    bad = [k for k, ok in CHECKS.items() if not ok or k not in paper]
    bad += [f"deck:{k}" for k in DECK if k not in deck]
    for k in CHECKS:
        print(("OK   " if k not in bad else "FAIL ") + k)
    print(f"{len(CHECKS) - len([b for b in bad if not b.startswith('deck:')])}/{len(CHECKS)} paper strings found; "
          f"{len(DECK) - len([b for b in bad if b.startswith('deck:')])}/{len(DECK)} deck strings found")
    if bad:
        print("MISSING:", bad)
        sys.exit(1)


if __name__ == "__main__":
    main()
