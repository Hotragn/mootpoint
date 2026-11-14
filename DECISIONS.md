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
