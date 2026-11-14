# Deep read: Guo et al. 2026, "How Much Do You Trust A Dog? Quantifying Hint-Following in Reasoning Language Models"

- **Authors:** Anxin Guo, Chirag Pabbaraju, Sara Ahmadian, Kamesh Munagala, Aravindan Vijayaraghavan
- **Source:** arXiv:2610.32055v2 (v1 posted 2026-10-23). No venue in the arXiv comments. The PDF has an ACL-style Limitations section, so it is probably an ARR submission. Label: **PRE**.
- **Read:** full text, including Sec. 1, Sec. 4, Related Work, Limitations and App. D.1 (Table 9). Read 2026-11-14.

## Problem
Hints of the form "[Source] thinks the answer is (X)" shift model answers. The paper asks what form the shift takes, and whether it is calibrated to the source's reliability.

## Method
- MMLU four-choice questions. The authors sample many reasoning rollouts per (question, target) pair, "up to 500 independent open-ended reasoning rollouts per question and per hint condition", and measure the log-odds shift of the hinted option against a matched no-hint reference.
- The hint source is a professor, a friend or a dog. Hint responses fit an exponential tilt, Δ ≈ α_s + η(q,i): a source effect plus a shared question–target susceptibility.
- **Sec. 4.1, declared reliability.** This is the part that collides with D1. The prompt reads "An independent predictor is correct with probability r% and otherwise chooses uniformly among the three incorrect options. On this question, it predicted (D)." There are nine declared values, r ∈ {0, 1, 5, 25, 50, 75, 95, 99, 100}%, on 200 pairs per model. The normative baseline is **Δ_Bayes(r) = log(3r/(1−r))**: zero at chance (r = 25%) and negative below it.
- **Sec. 4.2:** a "malicious actor trying to mislead you" source, plus hints wrapped as retrieved passages with and without explicit distrust warnings.
- **Sec. 3:** a synthetic-transformer mechanism in which KL-regularised reward training for hint-following produces the tilt.

## Models
Qwen 3.5 2B, Gemma 4 E2B and SmolLM3 3B. Sec. 4 uses only Qwen and Gemma. Everything is in the 2B–4B range.

## Key numbers (quoted)
- "Raising declared accuracy from 5% to 95% increases the mean log-odds shift by only 1.46 log-odds units in Qwen and 0.40 in Gemma. Over the same range, the Bayesian benchmark increases by 5.89."
- Both models show "positive mean shifts even at chance (r = 25%) and below-chance declarations."
- Under the malicious-actor framing, "The mean empirical shift remains positive at about +0.44 in both models."
- Adding an explicit distrust warning "reduces the shifts by about 1–2 log-odds units, but leaves them substantially above zero."
- In Table 9 (Gemma), the mean shift is 1.723 at r = 0% and 2.099 at r = 100%, against Bayes values of −∞ and +∞.
- With explicit negation ("the answer is not (X)"), the mean shift is −3.1 for Qwen and −1.5 for Gemma, so the direction does reverse when the hint itself is negated.

## Claimed vs shown
- The claim that response strength is "not calibrated to declared evidence under this benchmark" holds, but only for two models of 2B–4B parameters, on MMLU MCQ, with reliability **declared** in the prompt.
- No model is larger than 4B, and no closed model is tested.

## Limitations
- **Stated by the authors:** compute restricted them to 2B–4B models ("it remains an open question whether massive models obey a similar form"), and they study only one hint family (answer-directed MCQ hints).
- **Not stated:**
  - Reliability is only ever *asserted*. The model never experiences the source being right or wrong, so the comparison is with a declared likelihood, not with ecological validity.
  - No forged or contradicting signal is tested, for example a stated r = 95% while the observed track record is 50%.
  - The numeric "independent predictor" wording is unnatural compared with real provenance or credibility labels such as Community Notes, C2PA manifests or NewsGuard ratings.
  - They do not look at abstention or at verbalised confidence.

## Overlap with D1
**High on the core idea.** "Sweep a signal's validity and compare the update with Bayes-optimal" is done here for *declared* validity, using the same closed-form likelihood-ratio baseline that D1 proposed. A D1 that sweeps a stated "label is correct r% of the time" against Bayes would be a scale-up replication on larger models (Adaption-hosted 27B–400B), not a new contribution.

**What is left open:**
1. Validity that the model must **infer from an observed track record**, the true Brunswik ecological validity, rather than read off a statement.
2. **Stated-versus-experienced conflict**, which is a form of forgery.
3. Realistic provenance formats.
4. Models above 4B.
