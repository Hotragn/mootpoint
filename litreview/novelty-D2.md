# Novelty check, D2: a generalizability-theory audit of honesty and calibration benchmarks

Scout, 2026-11-14, about 02:17–02:22 EST. Every paper was opened on arXiv or at its venue, and the metadata was checked there. The two close papers were read in full; see the `paper-*.md` notes.

## Verdict: **DONE** (method), with a residual that is only **NOVEL-IF-NARROWED** and has a thin margin

The core of D2 has already been published in 2026:
- **G-theory variance decomposition of LLM evaluation scores** into item, prompt, judge and replicate facets, with **D-studies** that set how many items, prompts and judges are needed. This is Messing (NeurIPS 2026).
- The same with **the model or system as the object of measurement**, where the system × judge term caps reliability. This is Anand (2026, PRE).

The only part left is narrow: applying that design to **honesty and calibration benchmarks** (MASK, SimpleQA-style calibration, sycophancy suites), adding an **elicitation-format facet on the system side** (verbalised versus token confidence, scale design) and a seed facet, and reporting the relative G coefficient for *model rankings*. There is partial prior work on calibration in particular:
- Kim & Kang 2026: the ECE "better score flips in 8 settings" across protocols.
- Ghosh et al. 2026: "slightly different prompt templates yield scores that barely correlate".
- Karmakar & Chatterjee 2026: an ECE redefinition shifts the score by "0.149".

A reviewer would call the residual "Anand/Messing applied to a new benchmark family". It is an incremental application, not a new method.

## Closest prior work, ranked
1. **Messing 2026**, "Hidden Measurement Error in LLM Pipelines Distorts Annotation, Evaluation, and Benchmarking", arXiv:2604.11581, **accepted at NeurIPS 2026**. "TEE builds on generalizability theory (G-theory)". It covers the facets listed above, plus D-study cost frontiers. The headline result: "naive standard errors are 53-70% smaller than the corrected SE". On safety, judge-related terms are "73% of the variance". Its object of measurement is the mean or item, and the SUT×judge interaction is not captured. → `paper-messing-tee.md`
2. **Anand 2026**, "Ask Which, Not How Good: Sizing Benchmarks Scored by an LLM", arXiv:2609.27787 (PRE). A system × item × judge G-study over "373,019 judgments", with single-judge ceilings "0.600 (MT-Bench) … 0.792 (Arena-Hard)" and "25 judges for MT-Bench" needed to reach Eρ² = 0.8 at 30 items. It also audits 628 papers for how they report uncertainty. The prompt format is fixed, and only chat benchmarks are used. → `paper-anand-askwhich.md`
3. **Romanou et al. 2026**, "Brittlebench: Quantifying LLM robustness via prompt sensitivity", **NeurIPS 2026** (arXiv:2603.13285). Decomposes variance into data difficulty and prompt variability: "a single perturbation alters the relative ranking of models in 63% of cases", and perturbations "account for up to half of the performance variance".
4. **Kim & Kang 2026**, "Same Answer, Different Confidence: Protocol Sensitivity in LLM Confidence Calibration", arXiv:2605.27752 (PRE). The calibration-protocol facet: context shifts the ECE gap ".287 vs. .304", and "The better score flips in 8 settings". It covers five open LLMs plus four up to 72B.
5. **Ghosh, Kumar & Garg 2026**, "Measurement Validity and Representation Dynamics of Confidence Signals in LLMs", arXiv:2610.25846 (PRE, pre-registered). "verbalized confidence is unstable: slightly different prompt templates yield scores that barely correlate". Qwen2.5 models from 0.5B to 7B.
6. **Karmakar & Chatterjee 2026**, "What Single-Prompt Accuracy Misses: A Multi-Variant Reliability Audit", arXiv:2605.02038 (PRE). 10 instruct models × 5 benchmarks × 5 prompt variants; calibration fragility.
7. **Wang 2025**, "Measuring all the noises of LLM Evals", arXiv:2512.21326 (PRE). Prediction noise against data noise, and all-pairs paired comparison.
8. **Heineman et al. 2025**, "Signal and Noise", arXiv:2508.13144. The search result lists it as NeurIPS 2025. I did not confirm that at the venue, and the arXiv page shows no comment.
9. **Bean et al. 2025**, "Measuring what Matters: Construct Validity in LLM Benchmarks", **NeurIPS 2025 Datasets & Benchmarks** (arXiv:2511.04703). A review of 445 benchmarks. The Oxford press release (not the paper) reports that only 16% used statistical tests.
10. Foundations:
    - Mizrahi et al., "State of What Art? A Call for Multi-Prompt LLM Evaluation", **TACL** (arXiv:2401.00595).
    - Polo et al., "Efficient multi-prompt evaluation of LLMs" (PromptEval), **NeurIPS 2024** (arXiv:2405.17202).
    - Miller 2024, "Adding Error Bars to Evals", arXiv:2411.00640 (PRE).
    - Choi et al., "Diagnosing the Reliability of LLM-as-a-Judge via IRT", **ICML 2026** (arXiv:2602.00521).
    - The Machine Learning Society 2026, "The sample complexity of LLM evaluation" (tmls.nyc web report; not a paper; not opened).
11. Not usable: Norman et al. 2026 (arXiv:2606.19544), "Reliability without Validity". **The arXiv admin has withdrawn it** for not meeting "research content quality standards". **Do not cite it.**

## What a reviewer would say about each variant
| D2 variant | Verdict | Killer citation |
|---|---|---|
| G-theory decomposition of LLM-eval variance (item, prompt, judge, replicate) plus D-study | DONE | Messing NeurIPS 2026 |
| System-as-object G-study: how many items and judges a stable ranking needs | DONE (chat benchmarks) | Anand 2026 |
| Prompt sensitivity reshuffles model rankings | DONE | Brittlebench NeurIPS 2026; Mizrahi TACL; PromptEval NeurIPS 2024 |
| Calibration and confidence metrics are protocol-sensitive | DONE (descriptively) | Kim & Kang 2026; Ghosh 2026; Karmakar 2026 |
| **System-as-object G-study and D-study of honesty, calibration and sycophancy benchmarks, with elicitation-format and seed facets** | **Not found**, but incremental | (none) |

## Query log (2026-11-14 EST; times are approximate to about ±5 min, and the scripted API calls are logged exactly in the scratchpad querylog)
| Time | Source | Query |
|---|---|---|
| 02:21 | WebSearch (extended) | "generalizability theory LLM evaluation variance components prompt format judge items D-study benchmark reliability" → Messing, autoscoring and brand-variance papers |
| 02:21 | WebSearch (arxiv / acl / openreview / pmlr / neurips) | "\"generalizability theory\" large language model benchmark 2026" → Anand |
| 02:23 | WebSearch (arxiv / acl / openreview) | "variance decomposition prompt format sensitivity calibration or honesty or sycophancy benchmark model ranking stability LLM 2026" → Brittlebench, FSI |
| 02:23 | WebSearch | "\"Signal and Noise\" … Heineman" |
| 02:23 | WebSearch | "Bean Measuring what Matters … NeurIPS 2025" |
| 02:24 | WebSearch (extended; arxiv / acl / openreview) | "reliability of honesty benchmark scores (MASK, TruthfulQA, sycophancy) across judges and prompt templates, rank instability" (nothing direct) |
| 02:24 | WebSearch (arxiv / acl / openreview) | "verbalized confidence calibration ECE sensitivity to elicitation prompt format model ranking … number of prompts needed" → Kim & Kang, Ghosh, Karmakar |
| — | Citation chasing | Related-work sections of Anand and Messing: Song et al. 2025, TMLS 2026, Yagubyan 2026, Choi ICML 2026 |
| Note | arXiv API | Returned HTTP 429 from about 02:17. D2 searches went through WebSearch plus arXiv abstract pages |
