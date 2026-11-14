# Analysis freeze (pre-registration v3 + `repaired` addendum)

- **Frozen:** Sat Nov 14 2026, 04:14 EST (system clock). Synthetic data only; no dev or test claims exist.
- **`analysis/analyze.py` sha256:** `8135fa2c52e5bcd013595769a4c0201aab2efd028f2bdf376ffc1fa1e7eef1e3`
- `analysis/make_synthetic.py` sha256: `bcab62c47c422103fefed982aadc26b7ae46af7cb8e41d0af1bdbfcad60d9ea8`
- `tests/test_analysis.py` sha256: `e541b32aee2baeefb4eb21e70415856e5f84e2504835bae09ef55098a2132229`
- Supersedes v3 without the addendum (04:11, `6ee9fafa…`), v2 (03:57, `fa1ca3f5…`) and v1 (03:29, `74e71ae5…`).
- Environment: `.venv`, Python 3.12.15, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1. Bootstrap: 10,000 resamples, seed 20261114.
- Verify: `shasum -a 256 analysis/analyze.py`. Every `results.json` records `meta.analyze_py_sha256` and the sha256 of each input file.

## Usage
```
.venv/bin/python analysis/analyze.py --claims runs/test/claims.jsonl --dossiers data/dossiers --out analysis/results/test/
```
These files are read from the claims file's folder (each can be overridden with a flag):
- `descriptions.jsonl` and `presence.jsonl`: required;
- `verifiers.jsonl` and `judge2.jsonl`: optional. If one is absent, its sections are `null`.

On a schema violation the script prints `INPUT ERROR: …` and exits with code 2.

Outputs:
- `results.json`: every citable number, with n.
- Tables: `confirmatory.csv`, `signals.csv`, `per_model.csv`, `per_domain.csv`, `per_error_type.csv`, `sensitivity.csv`, `contradicts.csv`, `per_claim_signals.csv`, `per_cell_drift.csv`, `excluded_cells.csv`, `missing_rate_model_framing.csv`.
- Figure: `figures/frontier.png`.

## What v3 computes
- **Signals.** k_X is the number of ASSERTS verdicts in pair X: OPP (A, B), SC (N2, N3), DIV (P1, P2), SAME (A, A2). The suspicion score is 2 − k_X. y = 1 iff label ∈ {SIDE_TAKING, UNSUPPORTED_FACT}.
- **Confirmatory tests:**
  - H1a: aligned side-taking.
  - H2: ΔAUROC(OPP − SC).
  - H3: ΔAUROC(OPP − DIV).

  Each has a one-sided bootstrap p, Holm adjustment, and the decision rule "supported iff Holm-adjusted p < 0.05". Each also reports a Holm-level one-sided lower bound. H2 and H3 add a TOST at ±0.03 using the 90% CI.
- **Secondary:**
  - BA, retention and precision of the AND rule;
  - precision at matched retention (target = the OPP AND-rule retention);
  - AUROC of v_closed, v_file and the combination, plus combo − v_closed, OPP − v_closed and the share of the SC-to-ceiling gap that OPP recovers;
  - per-generator, per-domain and per-error-type results, plus the error-type interaction;
  - H1b DiD; SAME; CONTRADICTS rates by pair, also split by y.
- **`repaired` addendum:**
  - A SIDE_TAKING row with `repaired = "side_missing"` may have side and contested_id null. It still counts as y = 1 and is excluded from H1a only.
  - A row with `repaired = "gold_id_missing"` must be SUPPORTED_OTHER with gold_id null.
  - Every other row keeps the strict checks.
  - Counts per framing are in `n.repaired_in_file`, `n.repaired_in_complete_cells` and `confirmatory.H1a.n_side_missing_excluded`.
  - The synthetic generator marks 5% of SIDE_TAKING claims as side_missing.
- **Sensitivity:** drop NEUTRAL_INFERENCE claims; keep only claims where judge2 agrees on y.
- **Validation:**
  - κ on y: overall, per generator, and excluding qwen3.5-397b.
  - Presence validity: agreement, κ and the 2×2 table.

## Test output
```
test_planted_effect_recovered PASSED            test_null_point_estimates PASSED
test_null_coverage_over_seeds PASSED            test_tost_declares_equivalence_on_large_null PASSED
test_toy_hand_computed PASSED                   test_presence_validity_detects_mismatch PASSED
test_holm PASSED                                test_holm_level_lower_bound PASSED
test_incomplete_cells_excluded_and_reported PASSED
test_incomplete_cell_reasons × 3 PASSED  (missing presence row; no labelled B claims; missing P2 description)
test_validation_fails_loudly × 31 PASSED (claims, dossier, descriptions, presence, verifiers, judge2 schema;
    duplicates; references to non-N1 claims; rows for excluded descriptions; `repaired` missing, unknown value,
    side_missing on a non-SIDE_TAKING row or with side still set, gold_id_missing on a GOLD row)
test_optional_files_absent PASSED               test_cli_end_to_end PASSED
============================= 45 passed in 14.92s ==============================
```
The toy test checks every value against a hand computation:
- the AUROC of each of the 4 signals and both Δs;
- the AND-rule BA, retention and precision;
- matched-retention precision;
- the verifier and combination AUROCs;
- the error-type AUROC and the CONTRADICTS rates;
- H1a = 0.25 (a side_missing SIDE_TAKING claim in A must be excluded, or the value would differ), and H1b = 0.5 (a contested fact must be ignored);
- the repaired counts per framing;
- both sensitivity analyses;
- κ = 1/6;
- presence validity.

## Synthetic results
Data: `analysis/synthetic/{effect,null}`, seed 7, 48 dossiers × 3 models, 2 incomplete cells each. Results are in `analysis/results/synthetic_{effect,null}/`.

| | H1a | H2 ΔAUROC OPP−SC | H3 ΔAUROC OPP−DIV | H1b DiD |
|---|---|---|---|---|
| effect | 0.464 [0.454, 0.473], supported | 0.072 [0.045, 0.098], supported | 0.086 [0.053, 0.118], supported | 0.400 (planted 0.4) |
| null | −0.003 [−0.028, 0.024], not supported | −0.020 [−0.049, 0.012], not supported | 0.013 [−0.024, 0.050], not supported | −0.003 |

**Calibration over 20 extra null datasets (48 dossiers, 1,000 resamples; measured before the addendum, which changes only H1a's inputs):**
- The 95% CI excluded 0 in 1/20 (H1a), 2/20 (H2) and 0/20 (H3).
- Mean null Δ was +0.004 for H2 (SD 0.020) and +0.002 for H3 (SD 0.014).
- The test file checks coverage over 10 seeds and Holm familywise error (at most 2/10). I did not pick a seed that passes.

## Findings the PI should act on
1. **The pilot now loads unchanged.** Run on the real `runs/pilot/claims.jsonl` with dummy presence rows, counts only:
   - 5 side_missing rows (A 4, N1 1) and 27 gold_id_missing rows (A 10, B 6, N1 11);
   - 11 of 12 cells complete, 230 N1 claims;
   - the one cell whose P1 description was excluded is reported.

   Note: 27 relabels in about 766 claims is 3.5% of claims moved into y = 0 by repair. Worth a line in Limitations, plus an optional exploratory check that drops repaired rows.
2. **The presence stage must not write rows for an excluded description.** The analysis treats such rows as a hard error, consistent with confirmed call #3. The pilot has one excluded P1 description (smoke-protest × gemma).
3. **TOST power is marginal.** At 48 dossiers with about 17% unwarranted claims, the null SD of ΔAUROC is about 0.020, so the 90% half-width is about 0.033, which is wider than the 0.03 margin. TOST declared equivalence in only 2/20 null datasets at that size, and reliably at 200 dossiers (tested). With 76 test dossiers and a lower real unwarranted rate, expect TOST to be inconclusive, and state that in advance.
4. **The combination can score below v_closed.** It is a rank average, so when k_OPP carries no information it dilutes v_closed. In the synthetic null, combo AUROC = 0.672 against v_closed 0.706. This is expected behaviour, not a bug.

## Judgement calls (v3 additions; your earlier confirmations of 1–12, 14–16 and 18 still apply where relevant)
1. **Optional inputs.** Missing `verifiers.jsonl` or `judge2.jsonl` gives `null` sections. Descriptions and presence are required.
2. **Verifier coverage.** A null v_closed or v_file is allowed per row. AUROCs use the claims that have a value, and n is reported. Matched-retention precision for a verifier is computed only if every claim has a value.
3. **Combination.** Average ranks (ties averaged) are computed once on the analysed claims that have v_closed. They are not re-ranked inside each bootstrap resample.
4. **Verifier comparisons.** OPP − v_closed and combo − v_closed are paired on claims that have v_closed. Gap recovered = (AUROC_OPP − AUROC_SC)/(AUROC_v_file − AUROC_SC), point estimate only.
5. **Holm-level CI.** For the test ranked r (1 = smallest p), α_r = 0.05/(4 − r). The reported bound is the one-sided α_r percentile of the bootstrap distribution.
6. **TOST.** Equivalence iff the 90% percentile CI lies strictly inside (−0.03, 0.03). It is reported for H2 and H3 and for both sensitivity analyses (via ci90).
7. **Matched retention.**
   - One seeded uniform tie-break key per claim (seed + 7), fixed across resamples.
   - The target in each resample is that resample's OPP AND-rule retention.
   - The boundary claim is kept fractionally so retention matches exactly.
   - The Δprecision values OPP−SC and OPP−DIV are reported with CIs as descriptive results.
8. **Error type.** Positives are restricted to one label, against all y = 0. The pre-registered moderation prediction is reported as the interaction [Δ(OPP−SC) on SIDE_TAKING] − [Δ(OPP−SC) on UNSUPPORTED_FACT], with a one-sided p.
9. **CONTRADICTS rate** = the share of (N1 claim, description) cells in the pair, overall and split by y.
10. **Presence validity** uses the A and B descriptions only. "Labels contain the gold_id" means any labelled claim in A or B carries that gold_id, whatever its label.
11. **κ** is Cohen's κ on binary y, over N1 claims in complete cells that have label2. Point estimate and n only; no CI.
12. **The judge2-agrees sensitivity** keeps only claims with a label2 that agrees on y. Claims without a label2 are dropped.
13. **Missing presence row → cell incomplete, not an error.** A presence row for an excluded description → hard error.
14. **Expected cells** = split dossiers × the union of models in the claims and the descriptions.
15. **Subgroups** reuse the same dossier bootstrap draws: all dossiers are resampled and claims are masked, so subgroup Δs and their differences are paired.
16. **One outcome class only** in the complete cells → hard error, because AUROC is undefined.
17. **Dossier `settled`** must be a list but is not used, since settled points are already dropped upstream. Extra keys in any row (e.g. `repaired`) are ignored.
18. **Addendum details.**
    - `repaired` is a required key; its value may be null.
    - A side_missing row must have side and contested_id both null.
    - A gold_id_missing row must be SUPPORTED_OTHER with gold_id null.
    - side_missing rows are dropped from both the numerators and the denominators of H1a.
    - Nothing else changes.
19. **Unchanged from v2:**
    - H1a is a pooled ratio over A and B only.
    - H1b uses uncontested facts, with equal weight per cell.
    - claim_ids must be unique within each dossier × model.
    - The >10% exclusion rule is checked per model × framing, now over all 8 framings.
