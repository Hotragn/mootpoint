# Deep read: Wu & Xiao 2026, "Language Models Give Group-Linked Fields the Wrong Weight"

- **Authors:** Zengqing Wu, Chuan Xiao (Osaka University; corresponding author chuanx@ist.osaka-u.ac.jp)
- **Source:** arXiv:2608.22887v2 (v1 posted 2026-08-24). The web-search snippet carried the earlier title "Proxy reliance in large language model decisions is uncalibrated to predictive evidence". There is no venue, and the layout is Nature-journal style. Label: **PRE**.
- **Read:** Sec. 1, Sec. 2.1–2.2, the Fig. 1–2 captions and the location of the Limitations section. Read 2026-11-14.

## Why this paper matters for D1
It is not about provenance. It does, however, **already implement the method at the centre of D1**:
1. Set a cue's true predictive validity β, from zero up to a positive value.
2. Show the model labeled examples in context, so the validity is *experienced*.
3. Measure the model's cue reliance.
4. Compare that reliance with a normative reference learner and report a **tracking slope** (1 = calibrated).

This is a Brunswik cue-utilisation-versus-ecological-validity audit in all but name.

## Method
- Pairwise patient-triage ranking with simulated numeric fields. Task fields always predict risk. Proxy fields shift with a hidden group and add weight β to true risk.
- The prompt has either no labeled examples or 80 labeled examples.
- **Reliance** is the proxy-specific effect (PSE): the change in P(choose target) when only the target's proxies are counterfactually swapped.
- **References:** the full-information rule, and a Bayesian linear regression fitted to the same 80 examples.
- **Models:** Claude Sonnet 4.5, DeepSeek-V4-Flash, Qwen3.7-max and GPT-5.6 Terra.

## Key numbers (quoted)
- With β = 0 and 80 examples, "the models still moved: about 21 points for Sonnet, 24 for DeepSeek, 25 for Qwen and 29 for GPT, far above the learner."
- As β rises in four steps, "the eight fitted slopes ranged from −0.08 to +0.15, and every upper bound lay below 0.5". The pooled slope over Sonnet, DeepSeek and Qwen is "0.05 (one-sided 95% bounds −0.04 and 0.13)". GPT-5.6 Terra's repeated measurement gave "0.28 (0.05 to 0.53), still far from 1."
- The authors' own caveat: "It is not a test of Bayesian optimality, and the ±0.15 margin is descriptive."

## Limitations
- **Stated by the authors:** a simplified simulation with a cap on how much proxies contribute (Sec. at line ~729 of the extracted text).
- **Not stated:**
  - Proxies are features of people, not signals about the reliability of information.
  - No forged signal, and no stated-versus-experienced conflict.

## Overlap with D1
**Methodological precedent, not a topical collision.** D1 must cite it as the closest *method* and present itself as applying an evidence-referenced, validity-swept audit to **provenance and reliability signals** (credibility labels, fact-check tags, provenance manifests). D1 should also borrow the "tracking slope" as its headline statistic, so it reads as connected work rather than a reinvention.

D1 should not claim that "comparing LLM cue reliance to a normative learner across swept validity" is new. Wu & Xiao did it in Aug 2026.
