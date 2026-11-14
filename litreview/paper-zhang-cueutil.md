# Deep read: Zhang, Jiang & Lu 2026, "What Counts as Evidence? Epistemic Cue Utilization in Large Language Models"

- **Authors:** Jinchang Zhang, Kaijun Jiang, Guoyu Lu
- **Source:** arXiv:2610.12788v1 (2026-10-08). The code is on anonymous.4open.science, so this is an anonymised submission under review. Label: **PRE**.
- **Read:** full text (benchmark design, tracks, Sec. 3 results, interventions, Limitations, App. C on probe design), 2026-11-14.

## Problem
Does a model's ability to *identify* an epistemic cue (for example, which source has the better track record) predict whether that cue *influences* its judgment? The paper borrows the cue-utilisation framing from judgment research and cites Brehmer 1972 and Anderson 1981. It does **not** use the Brunswik lens model formally and computes no ecological validity.

## Method
- 500 fictional "worlds" (300 Controlled Core, 120 Structural Generalisation, 80 Naturalised), with 48 requests per world, giving 312,000 model–request cells.
- **Five tracks:** cue representation, integration, reliability utilisation, cue competition, and verified reasoning.
- **Source history** is presented as a summary: the "higher-history profile, with 7 of 8 earlier reports matching trusted verification, or a chance-level-history profile, with 4 of 8 matching verification."
- The key test is an HL↔LH history swap. The outcome is a change in choice, measured in percentage points.
- **Interventions on Qwen checkpoints:** sham material, fact restatement ("Flat"), a structured evidence ledger, and the ledger plus an explicit weighting principle.

## Models
13 LLMs. Those named in the text include Qwen3.5-27B, Qwen3.6-27B, Qwen3.5-9B, Grok 4.3 and GPT-6 Sol.

## Key numbers (quoted)
- Models "achieve approximately 99–100% recognition accuracy on unequal-history probes, yet their responses to the corresponding history swap range from" a 0.0-point swap effect up to "GPT-6 Sol achieves 100% recognition accuracy with a 100.0-point swap effect."
- Adding the weighting rule to the Ledger "raises history sensitivity by 39.2 and 47.2 pp, reaching 64.4 and 65.0 pp" in the two 27B models.
- "Verified-state accuracy remains 100% throughout these interventions."

## Claimed vs shown
- The dissociation between identifying a cue and being influenced by it is shown clearly.
- There is **no normative target for how much** a 7/8 versus 4/8 history should move the choice. The paper measures sensitivity, not calibration.

## Limitations
- **Stated by the authors:** fictional, text-only scenarios.
- **Not stated:**
  - Only two history levels are used (7/8 and 4/8), so there is no validity sweep.
  - The track record is a summary statistic, not an observed sequence of outcomes.
  - There is no Bayes-optimal comparison and no forged signal (for example, a stated history that contradicts the observed one).
  - Choices are binary, with no graded belief.

## Overlap with D1
**Medium–high.** This paper takes the Brunswik-style "cue utilisation" vocabulary and the track-record cue, so D1 cannot claim to be first in bringing cue-utilisation framing to LLMs.

**What is left open:**
1. A **graded validity sweep**.
2. **Calibration against the normative weight** (achievement and matching in the lens-model sense: r_a = G·R_e·R_s).
3. **Observed outcome sequences** in place of summary records.
4. Forged signals and conflicts between stated and experienced reliability.
