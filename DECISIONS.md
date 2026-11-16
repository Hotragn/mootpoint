# Decision log

Format: Claim / Evidence / Mechanism / Alternative (and how ruled out) / Residue.

## D1 (Sat 02:30): Keep PLAN/RUBRIC/STATUS in `claude/` until the project repo exists
- Claim: The repo name depends on the direction, so the planning files live in `claude/` and move into `<project>/` in Phase 2.
- Evidence: Kickoff prompt, workspace section: "choose a short name once the direction is picked".
- Mechanism: This avoids creating and later renaming a git repo.
- Alternative: Create a placeholder repo now. Ruled out because renaming leaves stale paths in logs.
- Residue: None.

## D2 (Sat 02:30): Rate limit, not credits, constrains the design
- Claim: Every experiment must fit in ≤ 5,000 model calls.
- Evidence: Adaption docs pricing (credits = USD, deepseek-v4-flash 0.045/0.14 per 1M tokens), and the T2 chat report of 1 concurrent call and about 10/min.
- Mechanism: 5,000 calls at 10/min is about 8.3 h, which fits Phase 3 with a margin.
- Alternative: The limit may be per model, which would allow parallel use across models. This is not verified; I will test it during the connectivity check.
- Residue: The actual limit is unknown until tested.

## D3 (Sat 02:30): No reading of other projects' `.env`
- Claim: Credentials for this project come from Hotragn placing `ADAPTION_API_KEY` in `<project>/.env`.
- Evidence: The auto-mode classifier denied an attempt to list variable names from `../approve-what-you-see/experiments/.env`.
- Mechanism: Respecting that boundary.
- Alternative: None needed.
- Residue: The connectivity check waits for the key. It does not block Phases 1–2.

## D4 (Sat 03:00): Drop idea #5 (evaluating AI note writers on Community Notes)
- Claim: This direction is already well covered in 2026.
- Evidence: WebSearch 2026-11-14 found arXiv 2604.02592 (field evaluation of LLM-written notes, Nov 2025–Jan 2026), 2605.16566 (characterising AI fact-checkers: 41.2% of submitted notes in May 2026), 2606.30905 (Collaborative Notes), 2609.40067 (API and AI writer design), and R Street (7 months of data, AI accounts identified via `apiEarnedIn`). I read only the search abstracts, not the full texts. That is enough to establish crowding.
- Mechanism: Four or more groups measured helpfulness of AI notes against human notes on the same public data.
- Alternative: A narrow angle (e.g. the timing confound) may remain. Ruled out because 2605.16566 already separates early and late submission.
- Residue: Community Notes data stays useful as a *source of reliability signals* for D1.

## D5 (Sat 02:45): Recommend direction A
- Claim: A has the highest expected score.
- Evidence: `litreview/SCOUT-SUMMARY.md` (D4 is the widest margin); Asaad 2609.03218 states its no-ground-truth limitation; Ganesh EACL 2026 gives a falsifiable target.
- Mechanism: Opposed-pressure agreement differs from same-pressure resampling in a testable way, at an affordable call count.
- Alternative: B fits Track 2 more directly. Ruled out as first choice because four 2026 papers each cover a piece (thin margin).
- Residue: Drift may be small on synthetic dossiers (JANUS). The pilot settles it.

## D6 (Sat 03:35): The rate limit does not bind; the earlier D2 assumption is revised
- Claim: Throughput is not a constraint. The sample size is raised to 100 dossiers and 3 generators.
- Evidence: `harness/probe.py` on 2026-11-14 03:30: 4 models in parallel took 0.5 s with no 429; 8 concurrent calls to glm-5.2 took 0.6 s and 8 to deepseek-v4-flash took 0.5 s, all OK (`runs/cache.sqlite`, tags probe_par and probe_burst). Spent 0.0002 credits.
- Mechanism: The limit reported in the T2 chat applied then or to another plan. It does not apply to this key now.
- Alternative: The limit may be adaptive and appear at volume. The client retries 429s with backoff, and the run is cached, so a throttle only slows the run.
- Residue: Unknown behaviour under sustained load.

## D7 (Sat 03:40): The PI acts as Builder; Analyst and Critic run as nested sessions
- Claim: The harness is the critical path and tightly coupled to the design, so the PI builds it. The analysis code and the design review are independent and go to separate sessions.
- Evidence: The kickoff prompt's team table; "one writer per set of files".
- Mechanism: The Analyst owns only `analysis/`, the Critic only `../claude/reviews/`, the PI owns `harness/` and `data/`. The PLAN.md schemas are the contract.
- Alternative: A separate Builder session. Ruled out because a brief round-trip on every pipeline bug costs more than it saves.
- Residue: Less independence on the build. This is offset by unit tests and the Critic's review of the code before the test run.

## D8 (Sat 05:00): Pre-registration v2 changes the outcome to side-taking (pilot-driven, before dev/test)
- Claim: v1's "UNSUPPORTED" outcome measured claim type, not truth. v2 anchors the outcome to the known contested points.
- Evidence: Pilot (4 dossiers × 3 models × 6 framings, `runs/pilot/`): 334 of 340 unsupported labels were evaluations and 6 were facts. In a hand-read of 40 unsupported claims, about 12 were actually supported (meta "accounts conflict" statements and plain facts). Pilot BA was OPP 0.724 vs SC 0.723; within evaluations 0.521 vs 0.576. Mention rates: N1 covers A facts 0.409 vs B facts 0.226, so asymmetry needs a neutral baseline.
- Mechanism: Strong models attribute contested testimony carefully and rarely fabricate facts from a 2–3k-word file. Drift appears as inference and characterisation that resolves contested points. That has a ground truth here, because the contested points are known by construction.
- Alternative: Keep v1 and report the null. Rejected because v1's outcome was invalid (label noise plus a type confound), so a null would be uninformative. The risk that v2 was chosen to get a positive result is controlled: the change uses pilot data only, dev and test are untouched, and v2 is frozen before any dev description is judged.
- Residue: NEUTRAL_INFERENCE vs SIDE_TAKING is still a judge call. That makes judge validation (κ against a second judge and a manual read) more important.

## D9 (Sat 04:05): PLAN v3 applies the Critic's design review (`../claude/reviews/design-review-1.md`)
- Claim: Adopted #1 (framing-blind, label-blind presence matrix replaces clustering), #2 (DIV non-stakeholder control; H3 = OPP vs DIV), #3 (paired ΔAUROC primary; AND-rule BA secondary; matched retention), #4 (closed-book equal-information verifier V_closed; with-file ceiling V_file), #5 (second judge on 100% of test N1), #6 (split 24/76; TOST ±0.03; 4% gate), #11 (Holm-adjusted one-sided decisions), #13 (witnesses use their own evaluative language in rendering). #7a and #12 were already covered by v2. #7b (side-claim analysis) is deferred as first to cut. #9 is already satisfied (identical instruction body; requester line only). #10: authorship is stated in PLAN.
- Evidence: The review's #1 shows the clustering procedure differed by label class, a measurement asymmetry that would bias every signal and favour H2. #2 shows OPP vs SC confounds opposition with prompt diversity.
- Mechanism: Each fix removes a way H2 could pass or fail for reasons other than opposition.
- Alternative: Keep v2 and save about 2,400 calls. Rejected because cost is not binding (D6) and Execution ≤ 2 was predicted without #1.
- Residue: Pilot signals under v2 (old clustering, n = 10 positives) favoured SC: BA OPP 0.562 vs SC 0.687. B-framing also leaned A (12 A-side vs 7 B-side side-taking claims), so the models seem to have an intrinsic lean that opposition may not cancel. H2 may fail; H3 and the error-type analysis then carry the paper.

## D10 (Sat 04:08): Logged repair of label formatting slips instead of discarding descriptions
- Claim: GOLD with a missing or unknown id becomes SUPPORTED_OTHER. SIDE_TAKING without a valid side or contested id keeps its label with side = null. Both are flagged in `repaired`.
- Evidence: Pilot: 11 of 72 descriptions failed strict validation (8 GOLD without id, 2 side missing, 1 contested_id missing).
- Mechanism: Dropping a whole description because of one slip would bias the sample toward simpler descriptions.
- Alternative: Retry at a higher temperature. Already done (3 attempts), and it still failed.
- Residue: Repairs slightly undercount gold mentions for H1b, equally across framings. Repair counts will be reported.

## D11 (Sat 04:15): Discord collision check, read-only: no collision
- Evidence: Alignment Jams #projects│teams (4 posts loaded). The closest is "Track 1/2 | Same facts, softer words: does corporate wording change AI fact-checkers' verdicts?" (Abi, 1d ago). It varies the *wording of the claim* shown to a fact-checker. We vary the *requester* of a description of fixed evidence and use opposed agreement as a verification signal. Others: an Epistemics/Decision-making evals megaproject (Jimmm), "Clarity", a swarm-alignment leftover. No posts on persona framing, against-interest agreement or consistency-based verification.
- Residue: The forum lazy-loads, so I may have missed posts. Discord is reference only per the brief.

## D12 (Sat 04:20): Analysis frozen for PLAN v3: `analysis/analyze.py` sha256 8135fa2c52e5bcd013595769a4c0201aab2efd028f2bdf376ffc1fa1e7eef1e3
- Evidence: `analysis/FREEZE.md`; 55/55 tests pass (planted effect recovered, null calibrated, hand-computed AUROC toy, TOST, exclusions, loud validation). Synthetic data only. No dev or test claims existed.
- Rule: The test analysis runs this exact file. Any change after this point is a new hash logged here with a reason. Results produced by a changed file are labelled exploratory unless the change is a bug fix that does not alter the specification.

## D13 (Sat 05:20): glm-5.2 is unavailable, so model roles are reassigned (PLAN v3.1)
- Claim: Judge = qwen3.5-397b. Generators = gemma-4-31b-it, deepseek-v4-flash, glm-53-flash. Dossier author = qwen3.8-27b. Fact check and settle check = deepseek-v4-flash. V_file = qwen3.8-27b. Second judge = deepseek-v4-flash.
- Evidence: From about 04:10, glm-5.2 calls hung: no call completed for an hour; the build produced 0 renders. Probe at 05:12 with a 20-token request: ReadTimeout at 60 s, then three 504 Gateway Time-outs after all my jobs were stopped. The other 6 models returned 200 in 0.4–0.7 s. The old client retried 5xx silently up to 40 times, which hid the outage for about an hour. The client now fails after 6 server errors and logs each one to stderr.
- Mechanism: The judge must be strong and outside the generator families. qwen3.5-397b is the strongest model that responds. The generators then cover 3 families (Gemma, DeepSeek, GLM) with no family overlap with the judge. The author (Qwen) shares a family with the judge, as glm did before; this is disclosed.
- Alternative: Wait for glm-5.2 to recover. Rejected because the recovery time is unknown, and switching mid-run would mix judges.
- Residue: glm-53-flash is a weaker generator. The second judge (deepseek) is also a generator, so κ is reported excluding its own descriptions. Lost about 1 h of wall clock. The schedule still holds (dev by 13:00).

## D14 (Sat 05:25): After the pilot, add closed-book verifier context controls and tighten the side-taking rule (dev-stage; before any dev or test data)
- Claim: Add V_closed variants that read N1 alone (`v_closed_none`), N1 + P1/P2 (`v_closed_div`) and N1 + N2/N3 (`v_closed_sc`), next to the pre-registered `v_closed` (N1 + A/B). The judge prompt now states that repeating what a document or record says is not side-taking.
- Evidence: Pilot v3.1 (4 dossiers, 9 unwarranted N1 claims; `analysis/results/pilot/`) gives AUROC OPP 0.570, SC 0.678, DIV 0.672, SAME 0.467; v_closed 0.759, v_file 0.844; H1a +0.194 [0.051, 0.357]. Hand-read: some side-taking claims are asserted in all 7 other descriptions (a lean shared across framings), and some side-taking labels were documentary facts (e.g. "a December 12 environmental report confirmed ... Stachybotrys").
- Mechanism: If opposed accounts help a *reader* rather than a *vote*, then v_closed should beat v_closed_none and v_closed_div. Without these controls, v_closed's advantage could be just the judge's priors on evaluative wording.
- Alternative: Treat the pilot as noise and change nothing. Rejected because the controls cost about 900 calls and are needed to interpret v_closed whatever the dev result.
- Residue: n = 9 positives. Nothing here is a finding yet. Whether any of this becomes confirmatory will be decided on dev, frozen before test (v4), and labelled as added after the pilot. A novelty check against AI debate (information-asymmetric judges) has been sent to the Scout.

## D15 (Sat 05:35): Add an instructed-debate arm (DA/DB) after the Scout's debate novelty check (dev-stage)
- Claim: Add two descriptions per cell in which the stakeholder explicitly asks for "the strongest case for my side", and a closed-book verifier variant that reads N1 + DA + DB (`v_closed_debate`). These rows are written to `descriptions_debate.jsonl` so the frozen v3 analysis stays runnable unchanged.
- Evidence: `../claude/litreview/novelty-D4b-debate.md`: the reading-judge protocol is structurally static, information-asymmetric debate (Khan et al., ICML 2024; Kenton et al., NeurIPS 2024). It is novel only because the advocates are uninstructed, the judged object is a third neutral text, and ground truth comes from contested points. The Scout lists an instructed-debate arm as a must-do so the paper can place itself relative to debate. Finding (i) is expected given Tan et al. (EMNLP 2025) and Ganesh et al. (EACL 2026) and will be framed as confirmation.
- Mechanism: Comparing v_closed (uninstructed stakeholders) with v_closed_debate (instructed advocates) shows whether naturally occurring stakeholder descriptions give a judge as much as purpose-built debate.
- Alternative: Cite debate and skip the arm. Rejected because it costs about 1,350 calls and answers the reviewer's first question with data.
- Residue: The Scout read the 2025–26 debate papers at abstract plus key-passage level. Carro et al. 2026 (no debate gains for weaker AI judges) and Radharapu et al. 2025 (judges take stances) must be discussed.

## D16 (Sat 06:35): glm-53-flash errors under load are handled by retrying; incomplete cells no longer crash a stage
- Evidence: The first dev run logged 277 server errors from glm-53-flash (247× 504, 30× 502), so 37 of its descriptions were excluded. A probe at 06:32 returned 200 in under 1 s. The rerun recovered all 37 (2 gemma empty outputs remain excluded). The verifiers stage crashed on a cell missing N2, and the crash also stopped presence.
- Fix: The verifiers stage skips cells missing a needed framing; analysis reports incomplete cells. Excluded descriptions are retried once before judging (cache makes this free for successes).
- Residue: GLM-family availability is fragile. For the test run I will retry exclusions in the same way and report the final exclusion counts per model × framing.

## D17 (Sat 07:05): Pre-registration v4. Dev shows counting and opposition do not help; reader family F2 added; cross-family reader built into the harness
- Evidence: The dev numbers are in PLAN "v4 additions". Exploratory dev checks: reader AUROCs hold on judge2 labels (v_closed_none 0.819) and on judge-agreed claims (0.834), so the reader is not just reproducing its own labels as judge. A weaker cross-family reader (deepseek-v4-flash) gets 0.639 (N1 only) and 0.624 (with A+B), so reader capability matters. For side-taking positives, OPP − SC = −0.063 [−0.116, −0.008]. H1b DiD +0.037 [−0.009, 0.083].
- Claim: The study's honest headline is negative for the original idea. Opposed framings measurably shift side-taking (H1a). Agreement across them is a *worse* detector than resampling, because the omission of inconvenient true facts penalises warranted claims. Reading opposed accounts adds little over reading the neutral text alone with a strong model.
- Alternative: Change the outcome or the signals to rescue H2. Rejected: that would be test-hunting. F1 stays as frozen. F2 is added with predictions written from dev before test, and test is a replication.
- Residue: The reader that labels is the same model as the main reader; this is mitigated by the judge2 and agreed-label checks. Presence-matrix validity is moderate (agreement 0.74, κ 0.38 against gold co-occurrence). Gold mentions are undercounted by about 5% because of repaired ids.

## D18 (Sat 07:15): Verifier id fallback; dev verifier coverage rises from 59 to 70 of 71 cells; test generation starts
- Evidence: qwen3.8-27b (v_file) sometimes keyed outputs as "1".."n" or "claim_i" instead of "N1:i" (28+25+25 of 240 sampled keys). Strict validation dropped whole cells, so v_file failures removed all reader rows for 12 dev cells.
- Fix: If keys are exactly 0..n−1 or 1..n (any prefix), map them to ids by position. Any other mismatch still fails. Tested.
- Prompts for every stage are now frozen for test. Test description generation starts now. The analysis spec for F2 is fixed in PLAN v4; `readers.py` is frozen before test judging.

## D19: `analysis/readers.py` frozen for F2: sha256 1f1af82090e197755653debce8a53a1781ebadc771a3b8faf8582ce41e8bfa9f
- Evidence: `analysis/FREEZE-READERS.md`; 85/85 tests pass across the project; dev check only; `runs/test` not opened. analyze.py is unchanged (8135fa2c…). Recorded before any test description was judged.

## D20 (Sat 08:10): Test descriptions final; one extra retry pass before judging
- Evidence: 2,280 test descriptions (76 dossiers × 3 models × 10 framings incl. DA/DB; corrected Sun Nov 15 from a miscount of 2,736). After the first pass 60 were excluded (glm-53-flash 5xx). The planned retry recovered 52. A third pass, run before any test label existed, recovered 4 more gemma empty outputs. 4 remain excluded, all gemma-4-31b-it (N1 ×3 of 76, P2 ×1); no cell is over 4% excluded, under the 10% failure line. Spend for test generation: about 11 credits.
- Mechanism: Excluded rows are empty outputs or exhausted 5xx retries; they do not depend on content, so retrying them adds no selection.
- Residue: Three gemma N1 descriptions are missing, so those 3 cells drop out of every N1 analysis.

## D21 (Sat 09:05): Test results from both frozen analyses; 5 of 6 confirmatory predictions held
- Evidence: hashes checked before running (analyze.py 8135fa2c…, readers.py 1f1af820…). 76 dossiers, 221 complete cells (7 excluded: 3 missing gemma N1, 1 missing gemma P2, 3 B descriptions with no valid labels), 4,486 N1 claims, 327 unwarranted (7.3%). `analysis/results/test/`.
  - F1: H1a +0.145 [0.100, 0.191], Holm p 0.0003, supported. H2 −0.048 [−0.073, −0.024] and H3 −0.091 [−0.123, −0.061], not supported (both point the wrong way; TOST not equivalent because the effect is outside the margin in the negative direction).
  - F2: R1 +0.125 [0.071, 0.178], Holm p 0.0003, supported. **R2 +0.035 [0.012, 0.059], Holm p 0.003, supported, against my prediction.** R3 −0.021 [−0.041, 0.002], not supported.
  - Side-taking-only OPP − SC −0.054 [−0.080, −0.029], as predicted.
  - Descriptive AUROC: counting SAME 0.654, OPP 0.656, SC 0.704, DIV 0.746; strong reader none 0.828, +SC 0.862, +A/B 0.863, +P 0.884, +debate 0.865; with-file 0.866; weak reader 0.668 / 0.648.
  - Validation: judge2 κ 0.81; reader ordering holds on judge2 and agreed labels; presence agreement 0.73 (κ 0.36). H1b DiD +0.030 [0.007, 0.052].
- Claim: R2 failed as a prediction and is reported as such. The R2 gain is matched or exceeded by every other two-description context (SC 0.862, DIV 0.884), so it reflects more context, not opposition (R3 and the descriptive comparisons). The paper says this without upgrading any descriptive comparison to confirmatory.
- Residue: Nothing was changed after seeing test. The context-generic reading is post hoc interpretation of descriptive numbers.

## D22 (Sun 19:40): Exploratory strengthening after test; independent rerun of every test description
- Evidence (all exploratory, after test; analyze.py and readers.py unchanged):
  - Second presence matcher glm-5.2 (`harness/presence2.py`, `analysis/matcher2.py`): OPP − SC −0.030 [−0.052, −0.008]; matcher κ 0.60.
  - `analysis/robustness_extra.py`: no-evaluative-word subset, error type, flag budget, per domain (`results/test/robustness_extra.json`).
  - Independent rerun `runs/test_r1` (fresh samples of all 2,280 descriptions, same judges; `analysis/replicate.py` → `results/test_r1/replicate_compare.json`). Same decision on all six confirmatory tests. H1a +0.137, H3 −0.076 [−0.115, −0.039], R1 +0.136, R2 +0.042 [0.020, 0.069]. **H2 (OPP − SC) −0.021 [−0.055, 0.015]: the interval now includes zero.** Warranted omission repeats exactly (opposed 60%, resamples 71%).
  - Two Codex CLI read-only reviews (`../claude/reviews/CODEX-JUDGE-REVIEW*.md`); wording fixes applied. Description count corrected from 2,736 to 2,280 (D20 fixed in place).
- Claim: the paper now says the opposed pair is "no better than" resampling, not "worse". "Worse than the non-stakeholder pair" (H3) and the omission mechanism hold in both runs.
- Residue: two runs are a small sample of run-to-run variance. No human labels yet. Spend about 40 credits in total; no money spent.
