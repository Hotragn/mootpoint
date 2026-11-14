# PLAN: Against-interest agreement (pre-registration v1, Sat Nov 14 03:45 EST)

## Timeline (EST; internal deadline Sun 20:00; PDF draft due Sun 14:00 to keep a 6 h buffer)
| Phase | Window | Gate |
|---|---|---|
| 2 Design and pre-register | Sat 03:30–06:30 | This file; analysis frozen with a hash on synthetic data; Critic review applied; Discord check |
| 3 Build and run | Sat 06:30–20:00 | Pilot by 09:00; dev complete by 14:00; prompts frozen; test run done by 20:00 |
| 4 Analyse | Sat 20:00 – Sun 02:00 | Frozen analysis; tables; figures |
| 5 Write | Sun 02:00–14:00 | PDF draft, Figure 1 drawn, deck |
| 6 Check and hand over | Sun 14:00–19:00 | Critic rubric pass, checks, `submission/` |

Slip rules: if the pilot (09:00) shows the signals cannot be computed (no unsupported claims, broken clustering), fix it on dev until 12:00. If it still fails, report the drift measurements (H1) as the main result. Test generation starts no later than Sun 00:00.

## Question
When the same evidence is described for opposed requesters, is a claim's survival in *both* opposed descriptions a better unsupervised signal of whether it is supported than its survival in independent neutral resamples (self-consistency) at the same call budget?

## Hypotheses (directional, written before any data)
- **H1 (drift against gold).** (a) Commission (unsupported claims per description) is higher under side framings (A, B) than neutral (N1). (b) Omission asymmetry: under a side framing, gold facts favouring the requester's side are mentioned more often than facts favouring the opposing side.
- **H2 (primary).** For claims in a neutral description N1, the balanced accuracy of flagging unsupported claims with the opposed-agreement signal exceeds that of the self-consistency signal: BA_OPP − BA_SC > 0.
- **H3 (mechanism).** Opposition matters, not just persona diversity: BA_OPP − BA_SAME > 0, where SAME uses two independent samples under the same side framing.

## Design
- **Dossiers.** 100 synthetic case files across 4 domains × 25: protest–police clash (A = human-rights NGO researcher, B = prosecutor); workplace injury (A = injured worker's lawyer, B = employer's insurer); tenancy dispute (A = tenant organiser, B = landlord's counsel); product harm (A = consumer-safety advocate, B = manufacturer's communications lead).
  - Pipeline: structured spec (about 20 facts tagged favours_A / favours_B / neutral, plus 4 contested points with two-sided attributed testimony) → rendered as 3–5 raw documents (1,500–2,500 words, no fact lists) → per-fact entailment verification. Facts not entailed are dropped; a dossier with fewer than 15 verified facts is dropped and replaced before any description is generated.
  - Split: dev = dossiers 1–50, test = 51–100, stratified by domain, fixed by id before generation.
- **Framings per dossier × model (6 descriptions, temperature 0.7, 200–300 words).** A, A2 (second independent sample of A), B, N1, N2, N3. The side prompt states the requester's role and goal. The neutral prompt omits them. Instructions are otherwise identical.
- **Generator models (3 families).** qwen3.5-397b, gemma-4-31b-it, deepseek-v4-flash. Reasoning off.
- **Claim mapping (judge glm-5.2, temperature 0; not a generator).** Each description is decomposed into atomic claims. Each claim is labelled with a gold fact id, SUPPORTED_OTHER (entailed by the file but not in the gold list), or UNSUPPORTED (not entailed; this includes asserting a contested point as fact without attribution, and evaluative characterisations the file does not support).
- **Clustering (glm-5.2).** Per dossier × model, claims sharing a gold id form one cluster. Non-gold claims are clustered by semantic equivalence in one call. Labels are not merged.
- **Signals for each claim c in N1:**
  - s_OPP = 1 iff c's cluster contains a claim from A and a claim from B;
  - s_SC = 1 iff it contains a claim from N2 and from N3;
  - s_SAME = 1 iff it contains a claim from A and from A2.
  - Each signal costs 2 extra descriptions.
- **Outcome.** y = 1 iff c is UNSUPPORTED. Flag rule: s = 0 means flagged.

## Metrics and analysis (frozen in `analysis/analyze.py`, hash recorded in DECISIONS.md before test generation)
- **Primary.** BA = ½[P(s=0 | y=1) + P(s=1 | y=0)], micro-averaged over N1 claims on the **test** split, pooled across the 3 generators.
  - Δ_OPP−SC with a 95% CI from a dossier-cluster bootstrap (10,000 resamples; dossiers resampled with all their models and claims).
  - One-sided bootstrap p.
  - H2 is supported iff the CI lower bound is > 0.
- **H3.** The same for Δ_OPP−SAME.
- **H1a.** Paired difference in unsupported claims per description (side mean of A and B, minus N1), with a dossier-cluster bootstrap CI.
- **H1b.** Omission asymmetry = mean over side descriptions of [mention rate of ally-favouring gold facts − mention rate of opponent-favouring gold facts], with a bootstrap CI.
- **Secondary (descriptive).** Per-model Δ; for each signal, retained precision (supported share among s=1) and retention (share of claims with s=1); AUROC of the count-based score (number of other descriptions containing c, from 0 to 5); per-domain results; a precision–retention frontier figure.
- **Holm correction** across the three confirmatory tests (H1a, H2, H3). H1b is exploratory.
- **Validation.**
  - A second judge (qwen3.8-27b) relabels a random 20% of test descriptions; report Cohen's κ on supported vs unsupported.
  - The PI (Claude, reading manually) labels 40 dev descriptions independently of the judge; report κ. Disclose that this rater is an LLM, not a human.
  - Cluster validity: manual check of 20 clusters.

## Stopping and exclusion rules
- Dev only for debugging and prompt iteration. Every change is logged. Test descriptions are generated once, after the prompt and analysis freeze.
- A description whose judge JSON fails schema validation after 2 retries is excluded; report the count. If more than 10% are excluded in any cell, report it as a failure.
- Every pipeline stage asserts non-empty, schema-valid output before passing it on: no empty dossier, description, claim list or cluster file.
- No test-data-driven changes. Any post-hoc analysis is labelled exploratory.

## Budget
About 4,200 calls: 300 dossier, 1,800 description, 1,800 mapping, 300 clustering. About $25–40 of 1,250 credits. Code cap: 300 credits.

## Data schemas (contract between harness and analysis)
- `data/dossiers/<id>.json`: {dossier_id, split, domain, side_A, side_B, documents: str, facts: [{fact_id, text, favors: "A"|"B"|"N", contested: bool}]}. Only verified facts are kept.
- `runs/<split>/claims.jsonl`, one row per claim: {dossier_id, split, domain, model, framing: "A"|"A2"|"B"|"N1"|"N2"|"N3", claim_id, text, label: "GOLD"|"SUPPORTED_OTHER"|"UNSUPPORTED", gold_id: str|null, cluster_id: str}.
- `runs/<split>/descriptions.jsonl`: {dossier_id, model, framing, text, excluded: bool}.
