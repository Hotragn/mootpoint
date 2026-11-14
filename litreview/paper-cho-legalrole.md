# Deep read: Cho, Hoyle & Hermstrüwer 2025, "Modeling Motivated Reasoning in Law: Evaluating Strategic Role Conditioning in LLM Summarization"

- **Authors:** Eunjung Cho, Alexander Hoyle, Yoan Hermstrüwer
- **Source:** arXiv:2509.00529v2. The arXiv comment reads "Accepted at NLLP 2025" (the Natural Legal Language Processing workshop, co-located with EMNLP 2025). **Peer-reviewed workshop.**
- **Read:** full text (Intro, Related Work, Data, Setup, Results 5.1, Limitations), 2026-11-14.

## Problem
Do LLMs show stakeholder-specific motivated reasoning when they summarise the same judicial decision for different legal roles?

## Method
- 200 Swiss Federal Supreme Court opinions in German, split 100 criminal and 100 private. Expert Swissblawg summaries serve as the reference.
- **Roles.** Criminal: judge, prosecutor, defense attorney, no role. Private: judge, plaintiff attorney, respondent attorney, no role. Each role is described abstractly, e.g. "a defense attorney representing a client in a similar situation".
- **Models.** Summaries come from o1 and Llama 3.3 70B-Instruct, 1,600 in total. GPT-4o extracts the facts and reasoning, and GPT-4o and DeepSeek classify favourability and match inclusion.
- **Metrics:** fact inclusion rate, and a favourability bias score (favourable minus unfavourable inclusion), reported separately for facts and for reasoning. Three Swiss-trained annotators rated 10 cases.

## Key numbers (quoted)
- "adversarial roles (e.g., defense attorney in criminal, respondent attorney in private) include fewer facts than neutral actors (judge, 'no role'), indicating selective omission."
- Fact favourability bias: "Defense attorney summaries show positive fact bias (GPT-4o: 0.012 and DeepSeek: 0.041) … Prosecutor summaries are more neutral (GPT-4o: 0.001 and DeepSeek: 0.019)." These effects are very small.
- Human ratings: "20% of o1-generated summaries written from prosecutor's perspective were deemed favorable to defense attorney, compared to 100% of summaries written from the defense attorney's own perspective."
- Human–LLM agreement on facts reached "ICC = 0.61, 95% CI [−0.22, 0.90]", a very wide interval from 10 cases.

## Claimed vs shown
- The paper claims "the first empirical evidence of computational motivated reasoning". The automated effect sizes are tiny, and the human study is n = 10 cases.
- **The role is the summariser's own perspective ("from the perspective of"), not a third-party requester.** The authors themselves speculate about the requester case ("as LLMs begin to infer user roles … even without explicit role instructions") but do not test it.

## Limitations
- **Stated by the authors:**
  - role prompts are ambiguous;
  - case-level variance;
  - LLM-as-judge reliability.
- **Not stated:**
  - Only two generator models.
  - No commission or hallucination analysis: only inclusion of facts extracted from the opinion.
  - No mitigation.
  - Facts are drawn from the opinion, which, as the authors note, already reflects legal argument.

## Overlap with D4
**High for "role → selective omission on the same evidence."** This paper is the closest precedent to Dean's prosecutor-versus-activist anecdote, and D4 must cite it.

D4 remains new on four points:
1. The **requester** is the one framed, not the summariser.
2. Adversarial *pairs* of reframings are crossed systematically.
3. **Commission** is measured: claims asserted beyond the evidence.
4. The **framing-invariant core** is tested as a verification filter.
