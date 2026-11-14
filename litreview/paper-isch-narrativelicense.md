# Deep read: Isch & Jennings 2026, "Narrative License and Model Sycophancy in LLM Summaries of Scientific Work"

- **Authors:** Calvin Isch, Grace Jennings (University of Pennsylvania)
- **Source:** **ACL 2026 Long Papers** (aclanthology.org/2026.acl-long.746). The PDF page numbers are around 16421–16423. I verified the record on the ACL Anthology page. The page's meta tags did not parse, but the abstract and PDF were retrieved from it.
- **Read:** full text (method, sycophancy manipulations in Sec. 3, results in Secs. 4.1–4.3), 2026-11-14.

## Problem
Do LLM summaries of papers inflate claims ("Narrative License", NL: causal overreach, rhetorical confidence, sentiment)? Do the user's stance and persona shift NL?

## Method
- 100 peer-reviewed articles.
- 6 models: GPT-5.1, GPT-5-mini, Claude-4.5-Sonnet, DeepSeek-V3.2-chat, Qwen-2.5-7B-Instruct and Llama-3.1-8B-Instruct.
- Several prompt families: basic, cautious, practical and others.
- **Sycophancy conditions:**
  - an enthusiastic or skeptical stance statement placed before the prompt;
  - GPT-5-mini-generated study-specific personas, aligned or misaligned with the findings;
  - the two crossed.
- 8,400 extra summaries in total.

## Key numbers (quoted)
- **For user stances:**
  - causal language: "OR = 0.66, CI = [0.52, 0.85], p = 0.001";
  - confidence: "b = 0.52 … p = 2.0 × 10−13";
  - sentiment: "b = 0.03 … p = 0.002".
- **For personas:** causal "OR = 0.73 … p = 3.4 × 10−5".
- The authors' own summary: "The direction of these effects is consistent and significant, though magnitudes are relatively small."

## Limitations
- **Stated by the authors:** the NL measure has limits.
- **Not stated:**
  - The outcomes are rhetorical (causal wording, boosters and hedges, sentiment), **not which propositions are asserted or omitted**.
  - The stance is about how much the user likes the result, not an adversarial goal.
  - There is no mitigation based on invariance.

## Overlap with D4
**Medium.** This is a published (ACL 2026) demonstration that the requester's stance and persona shift summaries of the *same* source document. D4 must cite it and separate from it by measuring **propositional content**: claims asserted, omitted or fabricated against an atomic-claim gold inventory.
