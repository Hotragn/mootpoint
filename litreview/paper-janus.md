# Deep read: Giannouris, Kabir & Ananiadou 2026, "JANUS: Evaluating Goal-Conditioned Distortion in Factually Grounded LLM Communication"

- **Authors:** Polydoros Giannouris, Mohsinul Kabir, Sophia Ananiadou (University of Manchester, per the GitHub org)
- **Source:** arXiv:2606.10852. The arXiv metadata gives a citation date of 2026-06-09 and an online date of 2026-10-29 (the latest version). No venue appears in the comments. The PDF has an ACL-style Limitations section. Label: **PRE**.
- **Read:** full text (Secs. 1–5, the Table 1 comparison, results, Limitations), 2026-11-14.

## Problem
Can LLMs mislead with true facts? When an *institutional objective* is assigned (for example, "increase adoption"), does the model change how it presents a **fixed** evidence pool?

## Method
- 160 scenarios across 8 domains. Each scenario has a recipient, an institutional actor, a decision subject, an objective, and **6 facts (3 favourable, 3 adverse)**, all stipulated as true and manually validated.
- **Paired prompts with the same user message, where only the system message changes:**
  - Neutral: "Use only the provided facts and do not add outside information."
  - Goal-conditioned: "You are a {ROLE} … {GOAL_OWNER} wants the summary to {OBJECTIVE}."
- **Five distortion dimensions:** selection, emphasis, ordering, numerical specificity and framing. They are scored by automated sentence–fact matching and an LLM framing judge, with manual validation.
- **Models (12 configurations):** GPT-5.4, GPT-5.4 Mini, Llama 3.1 8B/70B, Qwen3 8B/14B/32B (each with and without thinking), and DeepSeek v4 (with thinking).

## Key numbers (quoted)
- "Across models, selection deltas remain near zero". Favourable/adverse inclusion is "99.31%/99.60% under neutral prompting and 98.85%/98.52% under goal conditioning."
- "Ordering effects are positive for all 12 and significant for 11 models (mean delta: 0.106)."
- "Framing shifts are even more uniform, with all models exhibiting significant goal-congruent changes (mean delta 0.202)."
- "DeepSeek v4 Thinking exhibits the highest average distortion (0.114), driven by the strongest ordering (0.171) and framing (0.305) shifts."

## Claimed vs shown
- The result that true-only distortion through ordering and framing is pervasive is well supported.
- Selection, i.e. omission, is shown to be *small*, but only under a 6-fact pool with an explicit instruction to use only the provided facts. Short, enumerated fact lists make omission unlikely, so the design may suppress it.

## Limitations
- **Stated by the authors:**
  - constructed scenarios;
  - hallucination and fabrication are out of scope by design;
  - the automated evaluators can make errors.
- **Not stated:**
  1. The conditioning is the *system or institution's* goal, not the *requester's* persona or stance.
  2. The facts are pre-extracted. The model never has to describe raw evidence (a document, transcript or video) where it would decide for itself what counts as a fact.
  3. No commission is possible, because new claims are discouraged.
  4. There is no mitigation or architecture.

## Overlap with D4
**High on the phenomenon; different conditioning and different evidence format.** A reviewer will cite JANUS against "framing changes how LLMs present the same evidence." D4 must:
- vary the **requester** (persona or goal in the user turn), not the system-side objective;
- use **raw, unenumerated evidence**, so that omission and *commission* of claims can occur;
- treat the framing-invariant core as its contribution.

JANUS's near-zero selection result is also a **risk signal** for D4. With a fixed, short fact list, models rarely drop facts. D4's effect may therefore live mostly in evaluative framing ("mob" versus "protesters") unless the evidence is rich enough to force selection.
