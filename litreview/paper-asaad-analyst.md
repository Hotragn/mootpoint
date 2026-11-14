# Deep read: Asaad, Mohamed, Zhang & Abdelsalam 2026, "The Analyst in the Prompt: Role, Retrieval, and Memory Biases in LLM Financial Analysis"

- **Authors:** Ahmed Asaad, Amr Mohamed, Yang Zhang, Omneya Abdelsalam (Durham University; the correspondence address is durham.ac.uk)
- **Source:** arXiv:2609.03218 (2026-09-02). No venue is listed. The PDF is in ACL format, with a Limitations section. Label: **PRE**.
- **Read:** the full text, covering the intro, design (Fig. 1), results on interpretive drift and retention, and Limitations. Read 2026-11-14.

## Problem
When the document is fixed and only the user context changes (an investor persona given as a role, a profile or a memory), does the model's *neutral, evidence-based* judgment move? If it does, is that because it retrieves different evidence or because it interprets the same evidence differently?

## Method
- The corpus is 3,575 SEC 10-K and 10-Q filings, analysed with 12 LLMs from 5 families. The models include:
  - Llama-3.1-8B and Llama-3.3-70B
  - Qwen3.5-9B, Qwen3.5-35B-A3B and Qwen3.6-35B-A3B
  - gpt-oss-20b and gpt-oss-120b
  - DeepSeek-V3.1
- The model outputs two scores in [−1, +1]:
  - an **EvidenceScore**, which is meant to be invariant to the user;
  - a **PersonalizedScore**, which is allowed to adapt to the user.
- Three matched conditions:
  - **PR**: persona-conditioned retrieval.
  - **NR**: neutral retrieval, with the persona role kept. This isolates interpretation of fixed evidence.
  - **MEM**: the same mindset supplied as a user-memory profile rather than as the assistant's role.
- Personas are investor archetypes such as ShortSeller and LongOnly.
- Two mitigations are tested:
  - framing the mindset as a user profile instead of an assistant role;
  - separating the evidence-based output from the personalised output.

## Key numbers (quoted)
- "the panel retains 69% of the PR effect on average and 68% at the median, with model-level retention ranging from 44–89%". ShortSeller: "eight of twelve models retain at least 74% of the PR effect, and the panel median is 89.1%."
- "The dominant source is interpretive drift: models assign different evidence-based scores to the same filing chunks once a role is in scope."
- "larger models are not uniformly more invariant."
- "profile-framing spillover remains only 16–39% of role-framing under both output formats". An entity-masking control leaves "retention ≥ 97%".

## Limitations
- **Stated by the authors:**
  - One domain, one retriever and one template family.
  - The decomposition is accounting, not causal mediation.
  - SEC filings may have been seen in pretraining.
  - **"user-context spillover measures movement relative to a neutral-condition invariance reference, not deviation from externally validated ground truth."**
- **Not stated:**
  - The outcome is a *scalar sentiment-like score*, not a set of asserted or omitted propositions.
  - The personas are aligned investor goals, not adversarial requester pairs in a contested-evidence setting.

## Overlap with D4
**High on the measurement design.** It shows that the same evidence plus a different requester context gives a different "neutral" judgment, and that the drift is interpretive rather than retrieval-driven. It even proposes *separating an invariant evidence output*.

**D4's surviving contribution is what the authors themselves leave open:**
1. Measure drift at the **claim level** (omission and commission of propositions), not as a scalar score.
2. Test whether the **framing-invariant core is more accurate against externally validated ground truth**. The authors say explicitly that they test stability, "not whether the neutral judgment is objectively correct".

D4 should cite this paper in its first paragraph and quote that limitation as the gap it fills.
