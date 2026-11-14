# Novelty check, D1: Signal-weighting audit (provenance and reliability signals against their actual validity)

Scout, 2026-11-14 (02:10–02:20 EST). Every paper below was opened on arXiv and its metadata checked there. Close papers were read in full; see the `paper-*.md` notes.

## Verdict: **NOVEL-IF-NARROWED**
The broad version is **DONE**: "Do LLMs weight sources by reliability?" and "Do stated-reliability sweeps match Bayes?" both already exist.

What survives is narrower: **an explicit provenance or reliability tool, such as a credibility label or fact-check tag, whose *actual* validity the model has to infer from an observed in-context track record.** The design has three parts:
- sweep the experienced validity from 0.5 to 1.0;
- cross it with a *stated* validity that can conflict with the experienced one ("forged" or miscalibrated labels);
- score the model with the lens-model tracking slope against a Beta-Binomial Bayes-optimal agent, on 27B–400B models.

The novelty margin is **thin but real**. The method has a precedent in Wu & Xiao (Aug 2026, proxy features). The declared-validity sweep is done in Guo et al. (Oct 2026, 2B–4B models). Our contribution is the combination, the target (provenance signals, which Track 2 names as unmeasured), and stated-versus-experienced conflict, which none of these papers tests.

## Closest prior work, ranked
1. **Guo, Pabbaraju, Ahmadian, Munagala, Vijayaraghavan 2026**, "How Much Do You Trust A Dog?", arXiv:2610.32055 (PRE). The prompt declares "independent predictor correct with probability r", with nine values of r from 0% to 100%, and the result is compared with the Bayes value Δ = log(3r/(1−r)). Quote: "Raising declared accuracy from 5% to 95% increases the mean log-odds shift by only 1.46 log-odds units in Qwen and 0.40 in Gemma … the Bayesian benchmark increases by 5.89." **This is D1's original design for declared validity.** Differences: only 2B–4B models (Qwen 3.5 2B, Gemma 4 E2B); reliability is declared, never experienced; no forgery; no realistic provenance format. → `paper-guo-trustdog.md`
2. **Wu & Xiao 2026**, "Language Models Give Group-Linked Fields the Wrong Weight", arXiv:2608.22887 (PRE). Cue validity β is swept, 80 labeled in-context examples are given, a Bayesian regression serves as reference learner, and the tracking slope is "0.05". **Same lens-model method, but the cues are demographic proxy fields, not provenance signals.** → `paper-wu-proxyweight.md`
3. **Ashkinaze et al. 2026**, "Information Discernment in LLMs" (Learn2Discern), arXiv:2607.19355 (PRE, NeurIPS-format). 132 real news domains with PC1 reliability scores; source discernment is a Spearman correlation. Quote: models "rely on source popularity 2× as much as source reliability". Reliability is the model's prior over domain names. There is no in-experiment validity, no explicit signal and no Bayes magnitude. → `paper-learn2discern.md`
4. **Zhang, Jiang & Lu 2026**, "What Counts as Evidence? Epistemic Cue Utilization in LLMs", arXiv:2610.12788 (PRE, anonymised submission). Uses cue-utilisation vocabulary. Track records are a summary statistic ("7 of 8" versus "4 of 8"). Swap effects run from 0 to 100 pp despite about 99–100% identification. Only two validity levels, no normative weight. → `paper-zhang-cueutil.md`
5. **Yang & Yeung 2026**, "Resist, Update, Reject: Preference Optimization Installs a Prior-Dependent Reliability Switch", arXiv:2609.22359 (PRE). A "Bayesian-witness threshold benchmark": a source states reliability r, and the correct move is to flip iff r > p, where p is the prior. The paper trains Qwen2.5-7B with DPO and IPO; the untrained base model scores "accuracy 0.64, Spearman 0.29". Its own stated limitation: the switch "keys on reliability stated in the testimony, not on a separately audited track record". **That limitation is exactly D1's surviving niche.** The companion paper, arXiv:2607.12985 ("Resist and Update", the same authors), covers activation-level clamps on the same benchmark.
6. **Tang & Lin 2026**, "When Expert Disagreement Hurts", arXiv:2611.16694, **accepted at NeurIPS 2026**. Expert-label prestige drives revision. Quote: "Stated reliability moves reversal in the expected direction … Adding 'but they may be wrong' … lowers reversal for all five models", and "a stated track record raises it for all five". Qualitative reliability statements only; no sweep.
7. **Pradhan & Goley 2026**, "Trust, but Don't Verify: Epistemic Blind Spots in LLM Source Evaluation", arXiv:2606.05403 (PRE). Fabricated statistics get the same weight as valid ones through a "methodology-register gate", across six models in four families. **This is the closest prior work on forged signals**, but the forgery is in the source's *content* (impossible confidence intervals), not in a provenance label. It uses weight-of-advice from the judge–advisor literature.
8. **Schuster, Gautam & Markert 2026**, "Whose Facts Win? LLM Source Preferences under Knowledge Conflicts", **ACL 2026 Long** (pp. 29430–29459; arXiv:2601.03746). Synthetic source types across 13 open LLMs: models prefer institutional sources, and repetition reverses that preference. No validity manipulation.
9. **Cheng, Hawkins & Jurafsky 2026**, "Accommodation and Epistemic Vigilance", **ACL 2026 Long** (arXiv:2601.04435). Source reliability is one of the factors that change whether a model challenges a false belief. Qualitative.
10. **Mammen, Joswin & Venkitachalam 2026**, arXiv:2601.13433 (PRE), authority bias across four expertise levels. **Bajaj & Tiganj 2026**, arXiv:2602.13568 (PRE): human-expert labels are trusted more than LLM labels, "including when that signal is incorrect".
11. **Pan et al. 2024**, "Not All Contexts Are Equal: Teaching LLMs Credibility-aware Generation", **EMNLP 2024 Main** (arXiv:2404.06809). Foundation: trains models to use supplied credibility scores. It is a training method, not an audit of calibration to validity.
12. **Atwell et al. 2025**, BASIL, arXiv:2508.16846 (PRE). A Bayesian separation of sycophancy from rational updating. **Kawada & Kellis 2026**, "Evidence Integration in LLMs", arXiv:2609.04290 (PRE, 114 pp.): evidence integration is "determined by receiver properties rather than scalar trust in the evidence source".
13. Adjacent work I checked and set aside:
    - **Singh 2026** (arXiv:2606.22030): reliability-conditional agent memory, an architecture.
    - **Huang et al. 2026** (arXiv:2610.13008, NeurIPS 2026 workshop oral): provenance-lineage updating, i.e. repetition versus independent evidence.
    - **Zhang et al. 2026** "Don't Blindly Trust It" (arXiv:2606.21409): misleading tool feedback.
    - **Gupta et al. ACL 2025**, "Enough Coin Flips Can Make LLMs Act Bayesian".

## What a reviewer would say about each variant
| D1 variant | Verdict | Killer citation |
|---|---|---|
| "Do LLMs weight sources by reliability?" | DONE | Ashkinaze 2026; Schuster ACL 2026; Tang & Lin NeurIPS 2026 |
| "Sweep a label's stated accuracy; compare with Bayes" | DONE (small models), replication on larger models | Guo et al. 2026; Yang & Yeung 2026 |
| "Lens model: reliance slope against swept cue validity with in-context examples" | DONE for proxy features | Wu & Xiao 2026 |
| "Forged or fabricated credibility cues get weighted" | Partly done (content-level forgery) | Pradhan & Goley 2026 |
| **Experienced-validity sweep of a provenance/reliability tool, crossed with stated-vs-experienced conflict, scored by tracking slope against Beta-Binomial Bayes, on 27B–400B models** | **Not found** | (none) |
| C2PA, Content Credentials or Community Notes context as the signal for LLM agents | Not found as an evaluation. Search turned up only vendor and product pages | (none) |

## Query log (all on 2026-11-14 EST; times are approximate to about ±5 min, and the scripted API calls are logged exactly in the scratchpad querylog)
| Time | Source | Query |
|---|---|---|
| 02:10 | arXiv API | `abs:"source credibility" AND abs:LLM` |
| 02:10 | arXiv API | `abs:provenance AND abs:agents AND abs:reliability` |
| 02:10 | arXiv API | `abs:"source reliability" AND (abs:LLM OR abs:"language model")` |
| 02:10 | arXiv API | `abs:"credibility" AND abs:"retrieval-augmented" AND abs:"language model"` |
| 02:11 | arXiv API | `abs:"track record" AND (LLM) AND abs:advice`; `abs:"advice taking" AND (LLM)` |
| 02:11 | arXiv API | `abs:C2PA AND (LLM OR agent)`; `abs:"content credentials" AND LLM` |
| 02:11 | arXiv API | `abs:"community notes" AND LLM AND abs:context`; `abs:"credibility label(s)"` |
| 02:11 | arXiv API | `abs:"lens model" AND LLM`; `abs:"cue validity" AND LLM`; `abs:"cue utilization" AND LLM` |
| 02:11 | Semantic Scholar API | 7 queries (Bayes and source reliability, in-context track record, CAG, provenance signals, Brunswik, advisor calibration, forged signals). **All returned HTTP 429 (rate limited).** Covered instead by arXiv and WebSearch |
| 02:12 | WebSearch | "LLM learns source reliability from track record in-context feedback Bayesian update arXiv 2026" |
| 02:12 | WebSearch | "LLM agents provenance metadata C2PA trust signals evaluation … 2026" (vendor pages only) |
| 02:12 | WebSearch | "language models weight reliability labels proportional to label accuracy forged credibility label" |
| 02:12 | arXiv API | `abs:"whom to trust"`; `abs:"epistemic trust"`; `abs:"Bayes-optimal" AND abs:"source reliability"` (0 hits); `abs:"fact-check label"`; `abs:"NewsGuard" AND retrieval` |
| 02:13 | arXiv API | `ti:"credibility-aware generation"`; `abs:"stated reliability" OR "declared reliability" OR "declared accuracy"`; `abs:"source reliability" AND abs:sycophancy` |
| 02:13 | arXiv API | `abs:"track record" AND LLMs AND reliability`; `abs:provenance AND abs:belief AND LLMs` |
| 02:14 | arXiv API | `abs:"weight of advice" AND LLM`; `abs:"judge-advisor" AND LLM` (0 hits) |
| 02:14 | WebSearch (extended) | "language models learn advisor reliability across repeated trials in-context calibrated reliance on unreliable tool outputs arXiv 2026" → found Wu & Xiao |
| — | Citation chasing | Related-work sections of Guo et al. and Yang & Yeung, which yielded Mammen, Kawada & Kellis, De Marez, Cheng, Pradhan & Goley, and Singh |

## Advice to the PI
- If D1 is chosen, the framing must be "**experienced** versus **stated** validity." Cite Guo et al. (stated sweep), Wu & Xiao (method), Ashkinaze (real sources) and Yang & Yeung (whose stated limitation is our gap) in the first paragraph.
- Do not call the lens model new to LLMs; Zhang et al. and Wu & Xiao already use the vocabulary or the method.
- The cheapest new cell, which nobody has run, is a "label claims 95% accurate, observed record 50% accurate" condition against its reverse.

### Second pass (about 02:26, arXiv API back up)
| Source | Query → notable hits |
|---|---|
| arXiv API | `abs:"source reliability" AND abs:"in-context"` → Tang & Lin (already listed); Wu 2026, "Split the Labor" (arXiv:2608.14509): an evidence tuple with a reliability bucket and pooled log-likelihood ratios. An architecture paper, not an audit |
| arXiv API | `abs:"reliability" AND abs:"advisor" AND LLM` (no LLM-as-advisee hit) |
| arXiv API | `abs:"trust calibration" AND abs:"LLM agents"` → **AlRabah et al. 2026, PredActBench** (arXiv:2608.02372, PRE): agents using noisy predictive tools; "SOTA models rarely make predictor uncertainty visible to users". The focus is what agents communicate to users, not Bayes-weighting of tool output by its validity. Adjacent |
| arXiv API | `abs:"credibility signals" AND (LLM OR agents)` → Hu, Rong & Van Kleek, FAccT 2026 (arXiv:2605.30169): a conceptual argument that agents "lack grounding for reputation mechanisms". Not empirical |
| arXiv API | `abs:"provenance" AND abs:"misinformation" AND LLM AND abs:label`; `abs:"fact-check" AND abs:"labels" AND LLM AND abs:belief`; `abs:"ecological validity" AND abs:"cue" AND LLM`; `abs:"warning labels" AND LLM` (no relevant hits) |

The second pass does not change the D1 verdict.
