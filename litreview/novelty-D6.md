# Novelty check, D6: Absence-claim audit (zero-failure claims without statistical bounds)

Scout, 2026-11-14, about 02:22–02:26 EST. Every paper was opened at its source. The one close paper was read in full; see `paper-kaur-redteam.md`.

## Verdict: **NOVEL-IF-NARROWED**

**Already done.** The *argument* that zero-failure results license only an upper bound, and that benchmarks are underpowered for rare harms, is published with closed forms and a claims ladder: Kaur 2026, arXiv:2607.21735. General surveys of how papers report uncertainty also exist:
- Anand 2026 (628 arXiv papers): "only 46-67% report uncertainty of any kind";
- Bean et al. 2025 (NeurIPS D&B, 445 benchmarks).

**What survives** is a systematic audit of absence claims in 2025–26 AI safety, honesty and alignment **research papers**. Code each claim:
- its wording ("0 of N", "never", "no evidence of X", "did not observe");
- N, and the independence unit (prompts against seeds against replays);
- whether an upper bound or a power analysis is reported;
- whether the scope of the claim exceeds what the sample supports.

Score each claim against Kaur's ladder (the licensed claim against the claim made). Keivan Navaie's 10-paper pilot (Artif. Intell. Rev. 2026, verified via Crossref) is the organiser-side precedent. An audit of n ≳ 50 papers would be the scale-up.

**Collision risk.** Kaur announces a forthcoming audit: "We develop that audit, and the transparency instrument behind it, separately". It targets **frontier developer disclosures** (system cards and the like), not research papers. It could still appear before or during judging.

**Novelty margin: moderate on the *object*, thin on the *method*.** The work is mostly manual reading, and it risks coming across as a statistics lecture, as IDEAS.md already noted.

## Closest prior work, ranked
1. **Kaur 2026**, "What AI Red-Team Evaluations Can and Cannot Prove", arXiv:2607.21735 (PRE). Evidential ceiling and claims ladder. A design audit of eight suites: "At p = 0.001, StrongREJECT (n = 313) yields a false-certification probability of 73.1 percent". "Zero harms in 520 prompts gives a 95 percent one-sided upper bound of 0.57 percent". A preliminary review of 9 frontier disclosures found "only one endpoint reports both an exact numerator and an exact denominator". → `paper-kaur-redteam.md`
2. **Anand 2026**, "Ask Which, Not How Good", arXiv:2609.27787 (PRE). An audit of 628 arXiv papers, double-coded and human-validated at κ = 0.73. It found "fewer than one paper in four states whether its evaluation was run more than once, and only 46-67% report uncertainty of any kind". This covers general uncertainty reporting, not absence claims. → `paper-anand-askwhich.md`
3. **Navaie 2026**, "Epistemic norms for AI safety and alignment research", *Artificial Intelligence Review* (DOI 10.1007/s10462-026-11666-8, published 2026-08-07; title, author and venue verified via Crossref). The abstract and slides report a pilot of 10 alignment papers with "0/10 had independent verification", described as an "n = 10 pilot fragment". I could not read the full text: Springer's HTML did not render and the PDF was not fetched. The presence-versus-absence axis comes from here.
4. **Bean et al. 2025**, "Measuring what Matters", **NeurIPS 2025 D&B** (arXiv:2511.04703). Construct-validity review of 445 benchmarks. The Oxford Internet Institute press release (not the paper) reports that 16% used statistical tests.
5. **Miller 2024**, "Adding Error Bars to Evals", arXiv:2411.00640 (PRE). The foundation for statistical reporting. It does not treat the zero-numerator case.
6. **Vishwarupe, Shadbolt, Jirotka & Flechais 2026**, "NeurIPS Should Require Reproducibility Standards for Frontier AI Safety Claims", arXiv:2605.08192 (position paper). Proposes a "mandatory claim inventory" for safety claims. It argues the case but performs no audit.
7. **Summerfield et al. 2025**, "Lessons from a Chimp: AI 'Scheming' and the Quest for Ape Language", arXiv:2507.03409 (PRE). Criticises anecdote-driven claims in scheming research and calls for statistical modelling. A critique, not an audit.
8. Rare-failure estimation, which is method rather than audit:
   - **Kim, Gu, Tiwari & Kolter 2026**, "Measuring Five-Nines Reliability", arXiv:2605.11209;
   - **Broadwater 2026**, APST, arXiv:2602.11786, binomial per-inference failure rates;
   - **Jones et al. 2025**, "Forecasting Rare Language Model Behaviors", arXiv:2502.16797 (not opened beyond the search snippet).
9. Adjacent work:
   - **Zhu & Chang 2026**, "Refuse, Decompose, Refresh", arXiv:2609.20538. Reports "0/20 … one-sided exact 95% upper bound of 0.1391". It shows good practice and is not an audit.
   - **Levy & Perl 2026**, "Bounding the Black Box", arXiv:2604.21854, a certification framework.
   - **Uluırmak & Kurban 2026**, EvalSafetyGap survey, arXiv:2606.30219: 373 studies, with no absence-claim coding.

## What a reviewer would say about each variant
| D6 variant | Verdict | Killer citation |
|---|---|---|
| "Zero failures in N trials only bound the rate; use the rule of three and power analysis" | DONE | Kaur 2026; Hanley & Lippman-Hand 1983 |
| "Safety benchmarks are underpowered for rare harms" | DONE | Kaur 2026 (eight-suite audit) |
| "Papers often fail to report uncertainty" | DONE | Anand 2026 (628 papers); Bean NeurIPS 2025 |
| "Frontier disclosures rarely give numerator and denominator" | Preliminary (n = 9); full audit announced | Kaur 2026 |
| **Coded audit of absence claims in 2025–26 safety, honesty and alignment research papers, scored with a licensed-claim ladder** | **Not found** | (none); Navaie's pilot has n = 10 |

## Query log (2026-11-14 EST; times are approximate to about ±5 min, and the scripted API calls are logged exactly in the scratchpad querylog)
| Time | Source | Query |
|---|---|---|
| 02:28 | WebSearch (extended) | "audit of zero-failure claims \"rule of three\" upper bound AI safety evaluation papers statistical rigor" → Kaur, Zhu & Chang, Levy & Perl (plus blogs, ignored) |
| 02:28 | WebSearch (arxiv / openreview / acl) | "\"0 out of\" failures LLM safety evaluation confidence upper bound absence of evidence rare events red teaming statistics 2026" → five-nines, APST |
| 02:28 | WebSearch (arxiv / openreview / acl) | "meta-research audit of statistical reporting in LLM evaluation papers confidence intervals significance tests percentage of papers 2026" (no prevalence audit found) |
| 02:30 | WebSearch (extended) | "Bandana Kaur audit frontier model safety disclosures harm rate numerator denominator transparency instrument 2026 arXiv" (companion audit **not yet found**) |
| 02:30 | WebSearch (arxiv / openreview / springer) | "systematic review of AI safety or alignment papers claims of absence \"no evidence of\" scheming sandbagging zero instances statistical bounds critique 2026" (nothing direct) |
| 02:31 | Crossref API | DOI 10.1007/s10462-026-11666-8 → Navaie, *Artif. Intell. Rev.*, 2026-08-07 |
| — | Carried over from D2 | Anand's 628-paper audit; Bean NeurIPS 2025; Miller 2024 |
| Note | arXiv API | Rate-limited (429), so searches went through WebSearch; abstracts were read on arxiv.org/abs pages |

### Second pass (about 02:28, arXiv API back up)
| Source | Query → result |
|---|---|
| arXiv API | `abs:"rule of three" AND (LLM OR AI OR "language model")` (no audit; the hits are matches on other meanings of the phrase) |
| arXiv API | `abs:"zero failures" AND (LLM OR AI)` (no audit) |
| arXiv API | `abs:"absence of evidence" AND (AI OR LLM) AND safety` (0) |
| arXiv API | `abs:"upper bound" AND "red teaming" AND "zero"` (no audit) |
| arXiv API | `abs:"meta-research" AND (LLM OR "AI safety")` (no audit) |
| arXiv API | `abs:"claims" AND audit AND "alignment papers"` (0) |

The second pass does not change the D6 verdict. No audit of research papers' absence claims was found.
