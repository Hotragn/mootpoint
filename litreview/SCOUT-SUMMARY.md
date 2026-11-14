# Scout summary: novelty check for D1, D2, D4 and D6

Scout session, 2026-11-14, 02:09–02:29 EST. Status: **complete** for all four directions, including a second search pass on each.

How the search was done:
- **Sources:** the arXiv API and arxiv.org/abs pages, the ACL Anthology, Crossref, and WebSearch restricted to arxiv.org, aclanthology.org and openreview.net.
- **Semantic Scholar:** the API returned HTTP 429 every time, so I could not use it.
- **arXiv API:** it was rate-limited (429) from about 02:17 to 02:25. I covered that window with WebSearch, then re-ran D1, D4 and D6 queries once the API recovered.
- **Checking:** every paper cited below was opened at its source, with title, authors and venue checked there. Every CLOSE paper was read in full and has a `paper-*.md` note.

Per-direction detail: `novelty-D1.md`, `novelty-D2.md`, `novelty-D4.md`, `novelty-D6.md`.

---

## D1 Signal-weighting audit: **NOVEL-IF-NARROWED** (thin margin)

The broad question, whether LLMs weight sources by reliability, has been answered several times in 2026:
- Ashkinaze et al., Learn2Discern (arXiv:2607.19355, PRE): 13 models perform "near chance"; popularity counts 2× as much as reliability.
- Schuster et al., ACL 2026.
- Tang & Lin, NeurIPS 2026: stated reliability and stated track records shift how often models reverse their answers.

D1's own core design was **"sweep the label's stated accuracy and compare with Bayes."** It is published as Guo et al. 2026, "How Much Do You Trust A Dog?" (arXiv:2610.32055, PRE):
- nine declared accuracies from 0% to 100%, against Δ_Bayes = log(3r/(1−r));
- result: "only 1.46 log-odds units in Qwen and 0.40 in Gemma" against a Bayes value of 5.89;
- caveat: only 2B–4B models.

Two other papers cover the remaining pieces:
- **Lens-model method:** Wu & Xiao 2026 (arXiv:2608.22887) already run a tracking-slope audit of swept cue validity with 80 labeled in-context examples and a Bayesian reference learner. They report a pooled slope of 0.05, but on demographic proxy fields, not provenance.
- **Cue-utilisation framing:** Zhang et al. 2026 (arXiv:2610.12788) take that vocabulary and use 7/8-versus-4/8 track records.

**What survives:** an explicit provenance or reliability *tool* (credibility label, fact-check tag, provenance manifest) whose *actual* validity the model must infer from an **observed in-context track record**. The design has three parts:
- sweep the experienced validity from 0.5 to 1.0;
- cross it with a **conflicting stated validity** ("label says 95%, record shows 50%", i.e. forged or miscalibrated);
- score the model with the tracking slope against a Beta-Binomial Bayes agent on 27B–400B models.

Yang & Yeung 2026 (arXiv:2609.22359) state this gap as their own limitation: their switch "keys on reliability stated in the testimony, not on a separately audited track record". The only forgery result in the literature is at the content level: Pradhan & Goley 2026 show fabricated statistics get the same weight as valid ones. No evaluation of C2PA or Community Notes context as an LLM input signal was found.

**Risk:** several of these papers are recent and judges in this area will know them. D1 must present itself as "experienced versus stated validity" and cite Guo, Wu & Xiao, Ashkinaze and Yang & Yeung up front.

## D4 Framing-induced factual drift: **NOVEL-IF-NARROWED** (moderate margin)

The measurement half has been done several times:
- **Asaad et al. 2026** (arXiv:2609.03218, PRE; found in the second pass). Investor roles change the *neutral* evidence score on the same SEC filings. Under neutral retrieval, 69% of the effect remains, so the drift is interpretive. The paper also tests separating an invariant evidence output from the personalised one.
- **Cho et al., NLLP 2025.** Legal roles produce selective inclusion of facts.
- **JANUS 2026** (arXiv:2606.10852). An institutional goal shifts ordering by +0.106 and framing by +0.202. "selection deltas remain near zero" on fixed 6-fact pools.
- **Yousefi et al., AIES 2026.** Persona changes fact coverage, and a *hand-specified* "factual floor" narrows the gaps.
- **Isch & Jennings, ACL 2026.** User stance and persona shift the rhetoric of summaries of science.

**What survives, in two parts:**
1. Adversarial requester pairs on **raw** evidence, scoring **omission and commission** of claims against an atomic-claim gold inventory.
2. **The framing-invariant core tested as an unsupervised precision filter against ground truth.** Do claims that survive K reframings have higher precision, and at what cost in recall? Compare against self-consistency and against an expert-written floor.

Asaad et al. explicitly measure stability "not deviation from externally validated ground truth". That limitation is D4's opening, and nothing I found tests part 2.

**Must engage with:** Ganesh et al. (EACL 2026) find that consistency-based detection "detect[s] consistency, not correctness".

**Risk:** JANUS shows that enumerated, clean evidence yields almost no selection effect. The evidence needs to be rich (long transcripts or opinions), and evaluative labels should count as claims.

## D2 G-theory audit: **DONE** as a method; the leftover piece is incremental

The method is already published:
- **Messing, NeurIPS 2026** (arXiv:2604.11581). "Total Evaluation Error" is explicitly G-theory: item, prompt-variant, judge and replicate facets, plus D-studies. "naive standard errors are 53-70% smaller" than the corrected ones.
- **Anand 2026** (arXiv:2609.27787, PRE). A system-as-object G-study over item and judge facets, which is exactly D2's "how many items and judges does a stable ranking need". Single-judge ceilings are 0.600 for MT-Bench and 0.792 for Arena-Hard, and MT-Bench needs 25 judges at 30 items.

Prompt sensitivity and calibration-protocol sensitivity are also published:
- Brittlebench, NeurIPS 2026: one perturbation reorders model rankings in 63% of cases.
- Kim & Kang 2026; Ghosh et al. 2026; Karmakar & Chatterjee 2026.

**What is left:** the Anand/Messing design applied to honesty, calibration and sycophancy benchmarks, with an elicitation-format facet. Judges would read that as an application.

**Do not cite Norman et al. 2026 (arXiv:2606.19544).** arXiv has withdrawn it.

## D6 Absence-claim audit: **NOVEL-IF-NARROWED** (moderate on the object, thin on the method)

The statistical argument is published. Kaur 2026, "What AI Red-Team Evaluations Can and Cannot Prove" (arXiv:2607.21735, PRE), gives:
- an evidential ceiling and a claims ladder;
- a design audit of 8 safety suites, e.g. StrongREJECT has a 73.1% false-certification probability at p = 0.001;
- the rule-of-three bound, e.g. "Zero harms in 520 prompts … 0.57 percent".

Prevalence of uncertainty reporting is also covered: Anand 2026 audited 628 papers and found "only 46-67% report uncertainty of any kind".

**What survives:** a coded audit of **absence claims in 2025–26 safety, honesty and alignment research papers**. Code each claim's wording, N and independence unit, whether a bound is reported, and the claim it actually licenses, using Kaur's ladder as the rubric. This scales up Navaie's 10-paper pilot (Artif. Intell. Rev. 2026, verified via Crossref).

**Collision risk:** Kaur announces a separate audit of frontier *disclosures* ("We develop that audit … separately"). It is not yet found online, and it targets system cards and similar documents, not research papers.

---

## Ranking by novelty margin (best first)

1. **D4. Moderate margin.** The invariant-core-as-verification test against ground truth is unclaimed, and the closest paper (Asaad 2026) names it as a limitation. It also has the strongest sprint fit (Dean's anecdote) and a reusable artefact. It must be positioned past Asaad, JANUS, Cho and Yousefi, and it must answer Ganesh EACL 2026.
2. **D6. Moderate on the object, thin on the method.** No audit of research papers' absence claims exists, and it fits the organiser (Navaie). But it is labour-heavy manual coding, it leans on Kaur's framework, and a companion audit has been announced.
3. **D1. Thin margin.** It survives only in the experienced-versus-stated validity form. Four 2026 papers each cover one piece (Guo, Wu & Xiao, Ashkinaze, Yang & Yeung), so a reviewer could call it a combination. It fits Track 2 well, though, and the "forged label versus observed record" cell is clean and cheap.
4. **D2. Effectively DONE.** Messing (NeurIPS 2026) and Anand (2026) did the method. Only an application to a new benchmark family is left.

The ranking is by novelty margin only. It does not weigh feasibility under the Adaption rate limit, which is the PI's call.
