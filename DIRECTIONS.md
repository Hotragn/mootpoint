# DIRECTIONS: pick one (Sat Nov 14, 02:45 EST)

Process: I generated 20 raw ideas (`brainstorm/IDEAS.md`) and cut them to 4 by impact, gap and feasibility. The Scout ran logged, full-text novelty searches on all 4 (`litreview/novelty-D*.md`, 13 deep-read notes). I re-checked the 10 decisive citations myself at arxiv.org: titles and authors match.
Dropped: AI-written Community Notes evaluation (4+ studies in 2026, D4 in DECISIONS). G-theory audit of honesty benchmarks: already done (Messing, NeurIPS 2026, arXiv:2604.11581; Anand 2026, arXiv:2609.27787).
Budget facts: Adaption credits = USD and every option below costs < $40. The rate limit (about 10 calls/min) binds, so every design is ≤ 3,000 calls.

| Rank | Direction | Track | Predicted I / E / P | Novelty margin |
|---|---|---|---|---|
| **1 (recommended)** | **A. Against-interest agreement: opposed requester framings as a verification signal** | 1 (+Open) | 4–5 / 4 / 5 | moderate |
| 2 | B. Stated vs experienced reliability: do agents learn when a trust signal lies? | 2 | 4 / 4 / 4 | thin |
| 3 | C. Absence-claim audit of 2025–26 safety and honesty papers | Open | 3–4 / 4 / 4 | moderate (object), thin (method) |

---

## A. Against-interest agreement (recommended)

**Question.** When the same evidence is described for opposed requesters (activist vs prosecutor, plaintiff vs defence), are the claims that survive *both* framings more likely to be true than claims checked by ordinary self-consistency? Can that agreement serve as a cheap, unsupervised verification signal?

**Gap, with evidence.**
- Prior work shows that framing changes what models say about the same evidence:
  - Cho et al., NLLP 2025: legal roles cause selective omission.
  - Yousefi et al., AIES 2026: persona changes fact coverage, and an expert "factual floor" narrows the gaps.
  - JANUS 2026, arXiv:2606.10852: goal conditioning shifts framing by 0.202 but leaves selection near zero.
  - Asaad et al. 2026, arXiv:2609.03218: investor roles shift the evidence score on SEC filings, and 69% of the effect is interpretive.
- None of these test drift against ground truth. Asaad et al. say so themselves: they measure stability "not deviation from externally validated ground truth".
- Nobody has used invariance across *opposed* framings as a precision filter.
- The live caution is Ganesh et al., EACL 2026 (arXiv:2602.00723): consistency checks "detect consistency, not correctness".
- Dean Issacharoff's talk (VSIN) is the deployed anecdote: same video, prosecutor vs activist, different "facts". His platform has no way to tell which facts are framing artefacts.

**Why this could answer Ganesh (first principles).**
- Ordinary self-consistency resamples under the *same* pressure, so shared biases survive.
- Opposed framings push in opposite directions. A claim both sides assert is asserted *against* one side's interest.
- This is the old evidential principle behind "declarations against interest" in law, and behind triangulation of biased witnesses.
- Prediction: agreement under opposed pressure carries information about truth that agreement under identical pressure does not. The experiment tests exactly this, and it can fail.

**Representation.** A claim–evidence bipartite graph:
- Gold atomic facts sit on one side, each tagged favouring side A, side B, or neutral.
- Claims extracted from each framing's description sit on the other side.
- Edges mean "supported by"; claims with no edge are commissions.
- Each framing gives a subgraph. The *against-interest core* is the intersection across opposed framings.

This fits because the question is literally set membership plus support. The metrics (precision, recall, omission asymmetry, commission rate) are exact under a closed gold inventory.

**Methodology.**
1. **Data.** About 60 rich, raw evidence dossiers (witness statements, logs, reports; 1.5–3k tokens each) generated from authored structured fact specs. Each has about 25 gold atomic facts, some genuinely contested, plus deliberately ambiguous items. I check them for leakage. Rich and raw, not enumerated, because JANUS showed that clean fact lists suppress selection effects.
2. **Framings.** Neutral, side-A requester, side-B requester. Plus an equal-budget neutral resampling baseline (k samples).
3. **Models.** 3 families on Adaption (Qwen 3.5-397B, GLM-5.2, Gemma-4-31B) and DeepSeek-v4-flash as a judge-independence check.
4. **Measures.**
   - Omission asymmetry: the mention rate of opponent-favouring vs ally-favouring facts.
   - Commission rate: claims unsupported by the dossier.
   - Precision and recall of: a single neutral description; the self-consistency core (k neutral); the against-interest core; the union.
5. **Claim mapping.** An LLM maps each generated claim to a gold fact or to "unsupported". I hand-label a 60-description validation set and report judge agreement (κ).
6. **Held-out split.** 40 dev and 20 test dossiers. The analysis is frozen and hashed before the test run.

**Smallest settling experiment (pilot, about 100 calls, 1 h).** 8 dossiers × {A, B, neutral ×3} × 2 models. It settles two things: (a) is the omission and commission asymmetry > 0 on raw evidence, and (b) does the against-interest core beat the self-consistency core on precision at equal budget?

**Feasibility.** About 2,500 calls (720 descriptions, about 1,400 mapping calls, plus dossier generation), roughly 4–5 h of wall clock at 10/min, about $15–30. Solo hand-labelling of 60 items takes about 1.5 h. Fits by Sun 03:00.

**Predicted score.**
- **Impact 4–5:** it turns a known measurement (framing drift) into a reusable verification primitive with a clear user (OSINT and investigations, fact-checking pipelines), and it directly tests the leading objection to consistency-based checks.
- **Execution 4:** exact gold, a held-out split, an equal-budget baseline and a validated judge.
- **Presentation 5:** Dean's protest-video example is the opening, and one figure (a precision–recall frontier: single, self-consistency, against-interest) carries the result.

**Main risk.** The core may not beat self-consistency (Ganesh may be right here too), or drift may be small on synthetic dossiers.

**If it fails, we still learn something publishable:** "agreement under opposed pressure is no more truth-tracking than plain consistency". That extends Ganesh to adversarial framings and is a clean negative result. The drift measurements against gold still close Asaad's stated gap.

---

## B. Stated vs experienced reliability of trust signals

**Question.** When a provenance or credibility label claims 95% accuracy but the agent has *observed* it being right only 50% of the time, does the agent follow the label or the record? How far is it from a Beta-Binomial Bayes agent?

**Gap.**
- The broad question is answered:
  - Ashkinaze et al. 2026, arXiv:2607.19355: 13 models are near chance at weighting sources by reliability.
  - Guo et al. 2026, arXiv:2610.32055: a sweep of stated accuracy against Bayes, with updates far below Bayes, but only on 2–4B models.
  - Wu & Xiao 2026, arXiv:2608.22887: a lens-model tracking slope of 0.05 on demographic fields.
- The *conflict between stated and experienced validity* is untested. Yang & Yeung 2026 (arXiv:2609.22359) name it as their limitation: their switch "keys on reliability stated in the testimony, not on a separately audited track record".
- It also answers Track 2's question "does using a reliability tool improve behaviour?" ("nobody has measured it").

**Methodology.**
- Representation: a Beta-Bernoulli reliability model per signal source. It fits because reliability is a rate learned from outcomes, so the normative answer is exact.
- Design: experienced validity {0.5, 0.7, 0.9, 1.0} × stated validity {matched, inflated to 0.95}, over 15-round episodes with outcome feedback. Measure the tracking slope against Bayes and the number of rounds needed to discount a forged label.
- Fix: an external reliability ledger. The LLM supplies the evidence likelihoods; Bayes is done outside the model.
- Smallest experiment: one model, the 0.5-experienced vs 0.95-stated cell, 10 episodes (about 150 calls).

**Feasibility.** About 2,500–3,000 calls, < $20.

**Predicted score.** Impact 4, Execution 4, Presentation 4.

**Main risk.** Thin novelty: four 2026 papers each cover one piece, so a reviewer may call it a combination. The ledger fix is standard Bayesian aggregation. If it fails, the expected result ("models follow labels over records") still informs agent-framework developers.

---

## C. Absence-claim audit

**Question.** In 2025–26 safety, honesty and alignment papers, how many claims that a behaviour is absent ("0 of N", "never") license what they assert, given the rule-of-three and Clopper–Pearson bounds and their independence units?

**Gap.**
- The statistics are published: Kaur 2026 (arXiv:2607.21735) gives an evidential ceiling, a claims ladder, and audits 8 safety *suites*.
- Uncertainty-reporting prevalence is measured: Anand 2026 audited 628 papers.
- No coded audit of *research papers'* absence claims exists. It scales Navaie's 10-paper pilot (Artif Intell Rev 2026; the organiser's talk).

**Methodology.** A binomial upper-bound model. I code about 50 papers for claim wording, N, independence unit, any reported bound, and the claim actually licensed on Kaur's ladder. LLM-assisted extraction, all of it verified by me. I release a calculator and a reporting checklist.

**Feasibility.** Negligible inference cost. About 10–12 h of careful reading. It doesn't depend on the Adaption key.

**Predicted score.** Impact 3–4 (organiser fit, but meta-science rather than an AI-for-epistemics tool), Execution 4, Presentation 4.

**Main risk.** Kaur has announced a companion audit of frontier disclosures. The work leans on Kaur's framework, and coding is labour-bound and solo, so inter-rater reliability can't be established. If it fails, the field just has a smaller audit.

---

## My recommendation
**A.**
- It has the widest novelty margin that I could verify.
- It makes the strongest claim that can fail cleanly: it either answers Ganesh EACL 2026 or extends it.
- It is a reusable primitive, and it ties to an organiser-voiced deployment problem (Dean).
- The pilot settles the key risk within an hour of the Adaption key working.

B is the fallback if you prefer Track 2. C is the fallback if inference access fails.

**Needed from you:** (1) your pick (A, B or C, or edits); (2) `ADAPTION_API_KEY` in `ai-epistemics-sprint/.env` before Phase 3, ideally before Sat 09:00 EST.
