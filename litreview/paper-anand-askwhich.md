# Deep read: Anand 2026, "Ask Which, Not How Good: Sizing Benchmarks Scored by an LLM"

- **Author:** Atul Anand
- **Source:** arXiv:2609.27787 (2026-08-17); 18 pages. No venue is listed. Label: **PRE**.
- **Read:** abstract, contributions, Related Work, the benchmark and design sections, and the results on ceilings and D-study exchange rates. Read 2026-11-14.

## Problem
LLM-judged benchmarks settle differences of tenths of a point, but nobody has measured their resolution. How many items and judges does a stable comparison between *systems* need?

## Method
- G-theory with **the system as the object of measurement**, decomposing 373,019 judgments into system, item, judge and interaction components.
- The items come from MT-Bench, Arena-Hard, AlpacaEval 2 and a discrimination-screened set.
- Scoring uses a pointwise 0–5 rubric against a pairwise protocol in both orders, which makes position an estimable facet.
- A second judge universe uses five open-weight judges.
- The paper also audits 628 arXiv papers for how they report uncertainty, double-coded with human validation at κ = 0.73.

## Key numbers (quoted)
- "under a single judge, generalizability asymptotes to σ²_s/(σ²_s+σ²_sj) regardless of item count … Items saturate; judges do not."
- Single-judge asymptotes are "0.600 (MT-Bench), 0.706 (AlpacaEval 2), 0.746 (our screened items) and 0.792 (Arena-Hard)."
- "Reaching Eρ² = 0.8 at 30 items requires 25 judges for MT-Bench, 7 for AlpacaEval 2, and 2 each for our screened set and Arena-Hard."
- Pairwise in both orders: the ceiling "rises to 0.986 (bootstrap [0.934, 1.000] on 11 systems)". Position bias is "8.6 percentage points … 1.23x the median improvement claimed in the 53 published win-rate comparisons".
- "all 17 recovered MT-Bench improvements fall below MT-Bench's own floor"; "fewer than one paper in four states whether its evaluation was run more than once, and only 46-67% report uncertainty of any kind."

## Limitations
- **Not stated by the author:**
  - The prompt or elicitation format is *fixed* ("one pointwise 0–5 rubric and one scale fixed while varying the items"), so there is no format facet for the system under test.
  - Only chat-quality benchmarks are covered; no honesty, calibration or sycophancy benchmark.
  - There are about 11 systems.

## Overlap with D2
**Very high.** This paper is D2's proposed design (a system × item × judge G-study plus a D-study for how many items and judges a stable ranking needs), carried out on chat benchmarks. It also includes an audit of how papers report uncertainty, which touches D6.

**What is left for D2:**
- the **prompt- or elicitation-format facet** on the *system* side (Messing has prompt variants, but on the grand mean);
- the **honesty and calibration benchmark family**, where the scores are not judge ratings but proper-score or ECE-type metrics.

In practice, D2 would be "Anand's design applied to epistemic benchmarks, with a format facet". That is an incremental application.
