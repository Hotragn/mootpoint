# Readers freeze (PLAN v4, family F2)

- **Frozen:** Sat Nov 14 2026, 06:59 EST (system clock). Synthetic and dev data only; `runs/test` was never opened.
- **`analysis/readers.py` sha256:** `1f1af82090e197755653debce8a53a1781ebadc771a3b8faf8582ce41e8bfa9f`
- `tests/test_readers.py` sha256: `b8f06e9084a5bec1bd78e557da41e45d500b4c734a2f4654a5a94d2c80493ed8`
- `analysis/analyze.py` is unchanged: `8135fa2c52e5bcd013595769a4c0201aab2efd028f2bdf376ffc1fa1e7eef1e3`. readers.py imports its Boot, describe and holm and does not modify it.
- Environment: `.venv`, Python 3.12.15. Bootstrap: 10,000 resamples, seed 20261114, analyze.py's dossier-cluster `Boot`.

## Usage
Run analyze.py first. Then:
```
.venv/bin/python analysis/readers.py --claims runs/test/claims.jsonl \
    --signals analysis/results/test/per_claim_signals.csv --out analysis/results/test/
```
- `verifiers.jsonl` and `judge2.jsonl` are read from the claims folder by default; `--verifiers` and `--judge2` override them.
- Outputs: `readers.json`, which holds every number, plus `readers.csv`, which has one row per statistic.
- On a schema violation the script prints `INPUT ERROR: …` and exits with code 2.

## What it computes
- **Unit:** N1 claims in cells that are complete under analyze.py's rule (the rows of `per_claim_signals.csv`) and in which every N1 claim has a verifiers row. Other complete cells are dropped and listed with a reason ("no verifier rows" or "some N1 claims lack verifier rows"). The count is `n.cells_dropped_no_verifier_rows`.
- **F2** (one-sided, Holm over R1–R3; each test also reports a Holm-level one-sided lower bound):
  - R1 = AUROC(v_closed_none) − AUROC(2 − k_SC).
  - R2 = AUROC(v_closed) − AUROC(v_closed_none), plus TOST at ±0.03 via the 90% CI.
  - R3 = AUROC(v_closed) − AUROC(v_closed_div), plus TOST at ±0.03 via the 90% CI.
- **Descriptive:**
  - AUROC with 95% CI for SC, OPP, DIV and every reader column present;
  - xf_opp − xf_none, paired, two-sided;
  - all of the above, plus the R deltas, re-scored on judge2 labels and on the judge-agreed subset, and per generator;
  - secondary: OPP − SC with SIDE_TAKING positives only, using analyze.py's per-error-type mask. It is reported two-sided; the prediction is < 0.

## Test output
```
test_planted_effect_recovered PASSED          test_null_not_supported[11, 12, 13] PASSED
test_toy_hand_computed PASSED                 test_two_sided_p PASSED
test_cells_without_verifier_rows_dropped PASSED
test_bad_verifiers_fail_loudly × 10 PASSED    (pilot layout lacking v_closed_none; required column missing in one row;
    descriptive column in some rows only; value > 1; null; bool; string; duplicate; unknown claim; non-N1 claim)
test_descriptive_columns_may_be_absent PASSED
test_bad_signals_or_judge2_fail_loudly × 9 PASSED (k_SC ≠ ASSERTS count in N2/N3; bad verdict; y ≠ label; missing column;
    results.json not from the frozen analyze.py; results.json missing; claims file differs; bad label2; duplicate judge2)
test_cli_end_to_end PASSED
tests/test_readers.py + tests/test_analysis.py: 73 passed in 21.02s
```
- **Planted effect:** v_closed separates y better than v_closed_none and v_closed_div, and v_closed_none is better than SC. R1, R2 and R3 are all supported, with Holm lower bounds > 0 and no TOST equivalence.
- **Null:** the three F2 readers are 2 − k_SC with random tie-breaking, so every Δ is 0 in expectation. Over 3 seeds nothing is supported, every 95% CI covers 0, and |Δ| < 0.03.
- **Toy:** hand-computed AUROCs SC 5/8, v_closed_none 6/8, v_closed 1, v_closed_div 7/8, giving R1 = 1/8, R2 = 2/8, R3 = 1/8. Also checked: xf Δ 0.5, judge2-relabelled AUROC 6/8, the judge-agreed subset, and side-taking OPP − SC = 1/8.
- I checked that every failure test raises its own intended error message, not an incidental one.

## Dev check (dev was already viewed; nothing was tuned)
- 69 of 69 complete cells, 0 dropped, 1,341 N1 claims, 86 unwarranted.
- R1 +0.061 [−0.057, 0.149], R2 +0.036 [−0.003, 0.089], R3 −0.004 [−0.048, 0.056]. None is supported after Holm, and there is no TOST equivalence.
- AUROC: SC 0.711, OPP 0.663, DIV 0.727 (all three match analyze.py's frozen dev results).
  - v_closed 0.808, v_closed_none 0.772, v_closed_div 0.812, v_closed_sc 0.794, v_closed_debate 0.829;
  - v_file 0.757;
  - xf_none 0.619, xf_opp 0.604.
- Side-taking OPP − SC: −0.063 [−0.116, −0.008], two-sided p = 0.027.
- The pilot fails loudly, as intended: `verifiers.jsonl: column v_closed_none is in 0 of 249 rows`.

## Findings the PI should act on
1. **PLAN v4's dev reader numbers do not match the current files.** PLAN gives v_closed 0.827, v_closed_none 0.798, v_file 0.798, xf_none 0.639, xf_opp 0.624, R1 dev +0.087 and R2 +0.031. On the current `runs/dev/verifiers.jsonl` (1,353 rows, covering all 1,341 analysed claims), readers.py gives the numbers above. An independent scipy Mann–Whitney check reproduces them. I think PLAN was written from an earlier, partial verifiers file (it had 1,128 rows when I first looked). The SC, OPP and DIV values agree exactly. Consider correcting PLAN's dev numbers, or noting that they came from a partial file.
2. **`xf_readers.jsonl` is no longer read.** Its columns are now in `verifiers.jsonl` with identical values, so readers.py reads only `verifiers.jsonl`.

## Judgement calls
1. **Signals provenance.** The `results.json` next to `per_claim_signals.csv` must carry analyze.py sha `8135fa2c…` and the sha256 of the given claims file. Otherwise the run is a hard error.
2. **Recomputed columns.** k_SC is recomputed from N2/N3 and must equal the frozen column. y must agree with the label, and labels must agree with claims.jsonl.
3. **Reader scores and label2** come from `verifiers.jsonl` and `judge2.jsonl`. The CSV's own v_closed, v_file and label2 columns are ignored.
4. **Strict reader values.** A null value is a hard error; analyze.py, by contrast, allowed nulls. A required column (v_closed, v_closed_none, v_closed_div) must be in every row. A descriptive column must be in every row or in none; if it is in none, it is listed in `meta.reader_columns_absent`.
5. **Partial cells.** A cell in which any N1 claim lacks a verifier row is dropped whole, so each cell contributes either all of its claims or none.
6. **Bootstrap dossiers** = the dossiers in the readers unit. They match F1's dossiers when no cell is dropped, but are not guaranteed to.
7. **judge2-relabelled block:** positives are judge2 unwarranted, over claims that have a label2. **Judge-agreed block:** claims whose label2 agrees with the judge on y, scored with y.
8. **Two-sided p** = min(1, 2·min(#{Δ* ≤ 0} + 1, #{Δ* ≥ 0} + 1)/(B_valid + 1)).
9. **Descriptive Δs** (including the R deltas within subgroups) carry one-sided p values only for reference. Only `confirmatory_F2` carries Holm and decisions.
