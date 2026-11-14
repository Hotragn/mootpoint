# Deep read: Ashkinaze et al. 2026, "Information Discernment in Large Language Models" (Learn2Discern, L2D)

- **Authors:** Joshua Ashkinaze, Laura Kurek, Alina Faisal, Tongyuan Miao, Mariam Joseph, Ceren Budak, Eric Gilbert (University of Michigan)
- **Source:** arXiv:2607.19355v1. The arXiv stamp reads 22 May 2026. The PDF carries a NeurIPS Paper Checklist, so it was probably submitted to NeurIPS 2026, but no acceptance is stated. Label: **PRE**.
- **Read:** full text (Secs. 1–9 and Limitations), 2026-11-14.

## Problem
When LLMs meet external claims, do they update more for reliable sources ("source discernment") and more for claims that move them closer to the truth ("truth discernment")?

## Method
1. Elicit a numeric prior P1 for a question with known truth T.
2. Present "S says the answer is C = T×F. What do you think now?", with F ∈ {1/3, 1/2, 1, 2, 3}, and record the posterior P2.
3. Sources are 132 real news domains, stratified 3 popularity × 2 reliability. Reliability is Lin et al.'s PC1 composite score, split at 0.7.

**Metrics:**
- **Source discernment (SD):** Spearman ρ(|P1−P2|, reliability).
- **Truth discernment (TD):** ρ(update, improvement).
- **Correct defense:** how often a correct prior is kept.
- Reliability and truth propensities, built from matched pairs.

**Prompt conditions:** zero-shot, CoT, "Reliability" (rate the source first), "Bayesian" (weight the update by reliability) and "Defense".

A pre-registered user study (n = 299) validates the three axioms.

## Data and models
- 4,248 test questions from NumerSense, TriviaQA, GSS, TREC and World Bank, giving about 670K trials.
- 13 models: claude-3.5-sonnet, gemini-2-flash, gemini-2.5-flash, gpt-3.5-turbo, gpt-4o, gpt-4o-mini, gpt-4.1, gpt-4.1-mini, gpt-5, gpt-5-mini, mixtral-8x7b, qwen2.5-14b and qwen2.5-7b.

## Key numbers (quoted)
- Models "perform near chance on source and truth discernment" and "rely on source popularity 2× as much as source reliability."
- **Estimation versus application:** LLM-rated reliability correlates with PC1 at "ρ = 0.41". Source discernment rises "from ρ(∆, R_PC1) = 0.089 to ρ(∆, R̂_LLM) = 0.46" when it is computed against the model's own ratings. That is still "far below the +1 ceiling — meaning application failure is substantial regardless of estimation accuracy."
- The Bayesian prompt "improved source discernment but had lower truth discernment due to over-updating."

## Claimed vs shown
- The finding that source discernment is near chance relative to PC1 is well supported for the 13 models.
- The normative target is *monotonicity* (a rank correlation), not the *size* of the Bayes-optimal update, so the paper cannot say whether models over- or under-weight the signal relative to its validity.

## Limitations
- **Stated by the authors:** direct attribution rather than a full RAG pipeline; numeric questions only; a single reliability metric; credibility that may depend on the claim; synthetic perturbations; untested prompts.
- **Not stated:**
  - Reliability is the model's *prior knowledge of a domain's name*. No explicit label, track record or provenance metadata is shown, so "failure" mixes not knowing the source with not using it. The authors partly address this through the ratings analysis.
  - The ecological validity of a source is never manipulated. PC1 is fixed per domain, and the claim's truth is set independently of the source's reliability. Inside the experiment, therefore, *source reliability has zero actual validity*. A rational agent that knew this design would ignore the source, which complicates the normative axiom.
  - No forged-signal condition.

## Overlap with D1
**Medium–high.** This is the strongest published version of "do LLMs weight sources by reliability". D1 must cite it and present itself as the next step. D1 differs in four ways:
1. It **manipulates the signal's actual validity**, so the signal predicts truth with a known probability inside the experiment. L2D cannot do this, because its sources carry no in-experiment validity.
2. It compares update *magnitude* with the Bayes optimum, not only rank order.
3. It uses **explicit** signals (labels, track records, provenance) rather than domain names.
4. It adds forged signals.

The L2D finding that reliability carries no validity inside its own design is a sharp critique D1 can make in its framing.
