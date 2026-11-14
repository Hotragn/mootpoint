# Deep read: Yousefi, Aiersilan, Abroms & Broniatowski 2026, "Same Question, Different Answers: Auditing Persona-Dependent Variation in Six LLMs on Smoking-Cessation Advice"

- **Authors:** Artin Yousefi, Aizierjiang Aiersilan, Lorien C. Abroms, David A. Broniatowski (GWU)
- **Source:** arXiv:2610.42039 (2026-10-30). The journal-ref field and the PDF both read "Accepted for publication at the AAAI/ACM Conference on AI, Ethics, and Society (AIES 2026)". **Peer-reviewed.**
- **Read:** full text (Intro, Related Work, Methods 3.1–3.5, abstract results), 2026-11-14.

## Problem
Do LLMs give different health facts to different user personas? And can a "factual floor" system prompt reduce those differences?

## Method
- 12 personas: 4 life stages (16, 21, 40, 68) × 3 levels of self-described expertise. Each is a first-person prefix.
- 4 cessation questions; 6 models: claude-haiku-4-5, claude-sonnet-4-6, gemini-2.5-flash, gemini-2.5-pro, gpt-5.5 and grok-4.3.
- 5 repetitions, giving 2,880 responses.
- Regex metrics: word count, hedges, redirects, and **facts total** across 7 categories.
- **Intervention.** A system prompt that sets a **factual floor**: a hand-specified list of core facts every user must receive. Tone may still adapt.

## Key numbers (quoted)
- "Every model named FDA-approved prescription cessation medications less often to teen personas than to adult personas, by 32 to 67 percentage points."
- "in five of six models a persona presenting healthcare expertise received fewer facts than a persona presenting none."
- The prompt "narrows the teen-to-adult difference in prescription-medication mentions by 25 to 62 percentage points across all six models." However, "its effect on overall fact coverage varies in both magnitude and direction across models."

## Limitations
- **Stated by the authors:**
  - personas covary on several attributes, so results are reported at the scenario level;
  - an equal floor is not always the right clinical target;
  - the study is exploratory.
- **Not stated:**
  - Facts are scored by regex over 7 categories.
  - The floor is **specified by hand by domain experts**, not derived from the model's own outputs.
  - The work is advice-giving, not description of evidence.
  - Persona means identity (age or expertise), not an adversarial goal or stance.

## Overlap with D4
**Medium–high on the mitigation idea.** A "factual floor" that every requester must receive is conceptually close to D4's framing-invariant core.

D4 differs on three points:
1. Its core is **derived automatically** from the intersection of claims across adversarial reframings, with no expert list.
2. It is evaluated as a **verification signal**: do invariant claims have higher precision against ground truth?
3. It targets **description of evidence under adversarial requester goals**, not identity-tailored advice.

D4 must cite this paper and contrast its "derived core" with the "specified floor".
