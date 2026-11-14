# Novelty check, D4: Framing-induced factual drift and the framing-invariant core

Scout, 2026-11-14, 02:15–02:20 EST. Each cited paper was opened at its source (arXiv abstract page or the ACL Anthology). Close papers were read in full; see the `paper-*.md` notes.

## Verdict: **NOVEL-IF-NARROWED**

**The measurement half is largely DONE.** These papers already show that who asks, or what goal is set, changes what the model says about the same evidence:
- Cho et al., NLLP 2025: legal roles change which facts are included.
- JANUS, 2026 PRE: an institutional goal changes the order and framing of a fixed fact pool.
- Yousefi et al., AIES 2026: persona changes fact coverage.
- Isch & Jennings, ACL 2026: user stance or persona changes the rhetoric of summaries of science.
- ConsistencyAI, 2025 PRE: cross-persona factual similarity.
- **Asaad et al. 2026 PRE, "The Analyst in the Prompt"** (found in the second pass at about 02:27): the investor role changes the *neutral* evidence score for the same SEC filing chunks. Most of the effect is "interpretive drift" (69% of the effect remains under neutral retrieval). The paper also tests separating an invariant evidence output from the personalised one. Its stated limitation is exactly D4's opening: it measures stability "not deviation from externally validated ground truth". → `paper-asaad-analyst.md`

A D4 that only says "persona X makes the model describe the evidence differently" will read as replication.

**What survives** is two things together:
1. **Requester-goal-conditioned propositional drift on raw, unenumerated evidence.** Measure both omission *and commission*: claims asserted that go beyond the evidence, scored against an atomic-claim gold inventory. Use adversarial *pairs* of requesters, such as activist versus prosecutor or plaintiff versus defense.
2. **A framing-invariant core tested as an unsupervised verification signal.** Do claims that survive K adversarial reframings have higher precision against gold than single-frame claims, and at what cost in recall? Compare this with the expert-specified "factual floor" (Yousefi) and with ordinary self-consistency or paraphrase consistency.

No paper I found evaluates invariance across adversarial requester framings as a filter for factual precision. Two published cautions frame the test:
- Ganesh et al. (EACL 2026): "detection techniques detect consistency, not correctness."
- HAUNT: a model can be self-consistent and still wrong.

**Novelty margin: moderate.** Part 2 is the new contribution. Part 1 is the needed setup and must be framed as such.

## Closest prior work, ranked
0. **Asaad, Mohamed, Zhang & Abdelsalam 2026, "The Analyst in the Prompt: Role, Retrieval, and Memory Biases in LLM Financial Analysis"** (arXiv:2609.03218, PRE, ACL format). This is now the *closest* paper. It uses 3,575 SEC filings and 12 open models (Llama, Qwen, gpt-oss, DeepSeek), with three matched conditions that separate retrieval drift from interpretive drift. Neutral retrieval "retains 69% of the PR effect on average". Framing the mindset as a profile rather than a role cuts spillover to "16–39%". **Different from D4:** the outcome is a scalar [−1, +1] evidence score, not claims; the investor personas are not adversarial requester pairs; and stability is not checked against ground truth (the authors' own stated limitation). → `paper-asaad-analyst.md`
1. **Giannouris, Kabir & Ananiadou 2026, JANUS** (arXiv:2606.10852, PRE). Covers 160 scenarios with fixed 6-fact pools. A system-side institutional objective is compared with a neutral prompt. Results: "selection deltas remain near zero" (inclusion 98.5–99.6%), "Ordering … mean delta: 0.106", "Framing … mean delta 0.202", across 12 LLMs. **Different from D4:** the conditioning is the system's goal, not the requester's; the facts are pre-enumerated; commission is excluded by design; and there is no fix. → `paper-janus.md`
2. **Cho, Hoyle & Hermstrüwer 2025** (arXiv:2509.00529, **NLLP 2025 workshop**). Swiss court opinions summarised "from the perspective of" a judge, prosecutor or defense, using o1 and Llama-3.3-70B. Adversarial roles "include fewer facts … indicating selective omission". Favourability bias is tiny (0.001–0.041). **Different from D4:** the role is the summariser's own, not the requester's; only two models; no commission; no fix. → `paper-cho-legalrole.md`
3. **Yousefi, Aiersilan, Abroms & Broniatowski 2026** (arXiv:2610.42039, **AIES 2026**). 12 personas across 6 frontier models. Teens are told about prescription medications "by 32 to 67 percentage points" less often. A **"factual floor"** system prompt narrows the gap by "25 to 62 percentage points". **Different from D4:** the floor is specified by experts, not derived from the model's outputs; the task is advice, not describing evidence; persona means identity, not an adversarial goal. → `paper-yousefi-factfloor.md`
4. **Isch & Jennings 2026**, "Narrative License and Model Sycophancy in LLM Summaries of Scientific Work", **ACL 2026 Long** (2026.acl-long.746). A user stance or persona shifts causal overclaiming (OR = 0.66), confidence and sentiment. "magnitudes are relatively small". **Different from D4:** the outcomes are rhetorical, not propositional. → `paper-isch-narrativelicense.md`
5. **Banyas et al. 2025, ConsistencyAI** (arXiv:2510.13852, PRE). Embedding cosine similarity of "5 facts" answers across 100 personas, for 19 LLMs. Scores run "from 0.9065 to 0.7896". There is no gold inventory, and similarity is not truth.
6. **Dash, Reymond, Spiro & Caliskan 2025/26**, "Persona-Assigned LLMs Exhibit Human-Like Motivated Reasoning", **ACL Findings 2026** (arXiv:2506.20020). Personas reduce veracity discernment by "up to 9%". The persona is assigned *to the model*, and the task is judging headlines.
7. **Political-sycophancy cluster**, which concerns opinions or stance rather than describing evidence:
   - **Fu et al. 2026**, EMNLP 2026 Main (arXiv:2608.29198);
   - **Macmillan-Scott et al. 2026**, Poli-SHIFT (arXiv:2609.38256, PRE): terminology alone "reverses which side … in 16.9% of matched comparisons";
   - **Törnberg & Schimmel 2026** (arXiv:2604.27633, PRE).
8. **Alessa et al. 2025**, "Quantifying Cognitive Bias Induction in LLM-Generated Content", AACL 2025 (arXiv:2507.03194). Summaries change the sentiment of their context "in 26.42% of cases (framing bias)". No persona conditioning.
9. **Ganesh, Shokri & Farnadi 2026**, "Rethinking Hallucinations: Correctness, Consistency, and Prompt Multiplicity", **EACL 2026** (arXiv:2602.00723). Finds "detection techniques detect consistency, not correctness". **This is the key prior caution for the invariant-core claim.** D4 must test against it.
10. Adjacent work, checked and set aside:
    - Ren et al. 2026, "Persona Following Is Not Selective Control" (arXiv:2609.35036): a persona shifts non-target attributes.
    - Lee et al. 2026, OMIT (AACL Findings 2026, arXiv:2610.07847): moral omission bias, not factual.
    - Dogra et al. ACL 2025, "LMs can subtly deceive without lying" (cited by JANUS).

## What a reviewer would say about each variant
| D4 variant | Verdict | Killer citation |
|---|---|---|
| "Persona or role changes which facts an LLM includes about the same evidence" | DONE | Cho et al. NLLP 2025; Yousefi AIES 2026 |
| "Goal conditioning distorts presentation of fixed true facts" | DONE | JANUS 2026 |
| "User stance shifts how summaries frame findings" | DONE (rhetoric) | Isch & Jennings ACL 2026 |
| "Cross-persona factual consistency score" | DONE (embedding-level) | ConsistencyAI 2025 |
| "Prompt with a fixed list of facts every user must get" | DONE | Yousefi AIES 2026 (factual floor) |
| "Same evidence, role or profile shifts the neutral judgment; drift is interpretive, not retrieval" | DONE (scalar score, finance) | Asaad et al. 2026 |
| "Separate an invariant evidence output from the personalised output" | DONE (as an output schema) | Asaad et al. 2026 |
| **Commission under adversarial requester pairs on raw evidence, against atomic-claim gold** | **Not found** | (none) |
| **Framing-invariant core as an unsupervised precision filter, compared with self-consistency and the expert floor** | **Not found** | (none); caution from Ganesh EACL 2026 |
| Visual or OSINT evidence (Dean's video case) with persona prompts to VLMs | Not found as a controlled study | Closest: VLM counterfactual social-bias work (NAACL 2025) and a disability-context VLM audit (arXiv:2601.17348), not opened |

## Risk the PI should know
JANUS reports near-zero *selection* effects when facts are enumerated and the instruction says to use only the supplied facts. If D4's evidence is too clean, the drift may show up mostly as framing (evaluative words like "mob" versus "protesters") rather than as propositional omission or commission. This would make the precision test of the invariant core underpowered. Mitigations:
- Use rich, raw evidence: long transcripts, or court opinions as in Cho et al.
- Count evaluative-label claims ("arson", "disproportionate") as claims.

## Query log (2026-11-14 EST; times are approximate to about ±5 min, and the scripted API calls are logged exactly in the scratchpad querylog)
| Time | Source | Query |
|---|---|---|
| 02:15 | arXiv API | `abs:persona AND abs:summarization AND abs:bias AND LLM` (0) |
| 02:15 | arXiv API | `abs:"user identity" AND abs:sycophancy` (0) |
| 02:15 | arXiv API | `abs:"framing effect" AND LLM AND abs:factual` |
| 02:15 | arXiv API | `abs:"perspective" AND abs:omission AND LLM` → OMIT |
| 02:15 | arXiv API | `abs:"requester" AND LLM AND abs:persona` |
| 02:15 | arXiv API | `abs:"selective omission" AND LLM` |
| 02:15 | arXiv API | `abs:"persona" AND abs:"factual consistency"` → ConsistencyAI |
| 02:15 | arXiv API | `abs:"user persona" AND abs:"factual"` → Yousefi |
| 02:15 | arXiv API | `abs:"audience" AND abs:"tailor" AND abs:facts` |
| 02:16 | arXiv API | `abs:sycophancy AND abs:summar AND abs:evidence` |
| 02:16 | arXiv API | `"who is asking"` |
| 02:16 | arXiv API | `abs:"targeted underperformance"` |
| 02:16 | arXiv API | `abs:"user goal" AND abs:summar` |
| 02:16 | arXiv API | `abs:"invariant" AND abs:"reframing"` |
| 02:16 | arXiv API | `abs:"multi-perspective" AND abs:consistency AND abs:hallucination` |
| 02:16 | arXiv API | `abs:"advocacy" AND LLM AND abs:facts` |
| 02:16 | arXiv API | `abs:"prosecutor" AND LLM` → Cho et al. |
| 02:16 | arXiv API | `abs:"spin" AND LLM AND abs:evidence` |
| 02:17 | arXiv API | `abs:"motivated reasoning" AND LLM AND abs:persona` → Dash |
| 02:17 | arXiv API | `abs:"role-conditioned" AND summarization` |
| 02:17 | arXiv API | `abs:"stakeholder" AND summarization AND bias` |
| 02:17 | arXiv API | `abs:"cross-persona"` |
| 02:17 | arXiv API | `persona AND "hallucination detection"` |
| 02:17 | arXiv API | `"perspective-invariant" OR "framing-invariant" OR "persona-invariant"` |
| 02:17 | arXiv API | `"image description" AND persona` |
| 02:17 | arXiv API | `"vision-language" AND persona AND factual` |
| 02:17 | arXiv API | `OSINT AND LLM` |
| 02:17 | arXiv API | `"user framing" AND fact` |
| 02:17 | Note | The arXiv API began returning HTTP 429 at about this point, so some of the empty results above may be rate-limit artefacts. I re-covered them with WebSearch |
| 02:17 | WebSearch (extended) | "LLM user persona or goal changes which facts are included when describing the same evidence, selective omission, framing, 2026 arXiv" → JANUS |
| 02:17 | WebSearch | "consistency of claims across adversarial reframings or perspectives as hallucination detection signal LLM persona invariant claims" → Ganesh EACL 2026 |
| 02:17 | WebSearch | "vision language model describes same protest video differently depending on prompt persona activist prosecutor" (nothing controlled) |
| 02:18 | WebSearch (arxiv / acl / openreview) | "persona-conditioned hallucination … commission vs omission" (nothing direct) |
| 02:18 | WebSearch (arxiv / acl / openreview) | "claims that remain consistent across multiple user perspectives … verification filter" (nothing direct) |
| 02:18 | WebSearch (arxiv / acl / openreview) | "sycophancy toward user's political stance in factual summaries of news events" → Isch & Jennings ACL 2026, Fu EMNLP 2026 |
| 02:19 | WebSearch (extended) | "generate answer under opposing framings, keep only claims that agree, improves precision" (nothing direct) |

### Second pass (about 02:26–02:28, arXiv API back up)
| Source | Query |
|---|---|
| arXiv API | `abs:"same evidence" AND LLM` → **Asaad et al. 2026 (new, close)** |
| arXiv API | `abs:"user persona" AND abs:omission` (0) |
| arXiv API | `abs:"persona" AND abs:"summaries" AND abs:"facts"` (0) |
| arXiv API | `abs:sycophancy AND abs:"fact" AND abs:"summary"` (0) |
| arXiv API | `abs:"perspective" AND abs:"invariance" AND claims` |
| arXiv API | `abs:"human rights" AND (LLM OR VLM) AND abs:video` (0) |
| arXiv API | `"user-tailored" OR "audience-tailored" AND factual` |
| arXiv API | `abs:"stance" AND summarization AND user AND omit` (0) |
| arXiv API | `abs:"role" AND bias AND same AND documents AND summar` → only 2021–2023 framing-bias work (Lee et al. 2311.01817, polarity minimisation; 2106.10084, subjective bias) |
| arXiv API | `ti:sycophancy AND abs:"summarization"` (0) |
| arXiv API | `abs:"requested by" AND LLM AND bias` |
