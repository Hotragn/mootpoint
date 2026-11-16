# STATUS

## Gate 0 (Sat Nov 14, 02:35 EST): Phase 0 done, except the Adaption check
- Read all 3 transcripts, 4 chats and the slides (with speaker notes), plus the sprint Overview, Resources, Guidelines and Schedule. Output: `claude/brainstorm/SPRINT-SIGNALS.md`.
- `claude/RUBRIC.md` quotes the rubric, the checklist and the form fields. The template was downloaded to `claude/brainstorm/raw/template/`.
- `claude/PLAN.md` holds the timeline. The PDF draft is due Sun 14:00 and the handover Sun 20:00.
- Adaption: endpoint and models confirmed from the public docs (7 models, 4 families). **A live call is pending.** It needs `ADAPTION_API_KEY` in the project `.env`, which Hotragn creates. No credentials have been read or printed.
- Note: the references live in `docs/local/references/`.
- Next: Phase 1.

## Gate 1 (Sat Nov 14, 02:45 EST): DIRECTIONS.md delivered. STOPPED for Hotragn's choice
- 20 ideas, then a shortlist of 4. Scout novelty checks are done (`litreview/`). I re-verified the 10 decisive citations at arXiv.
- Ranked: A against-interest agreement (recommended), B stated vs experienced reliability, C absence-claim audit. G-theory was dropped as already done; Community Notes was dropped as crowded.
- Ahead of schedule (PLAN had Gate 1 at 07:30).
- Blockers: the direction choice; the Adaption key; ChatGPT cross-check sends were blocked by the permission classifier.

## Gate 2 (Sat Nov 14, 05:40 EST): Phase 2 done; Phase 3 building
- Direction A chosen by Hotragn (Sat about 02:50).
- Pre-registration went v1 → v2 (pilot: the outcome measured claim type) → v3 (Critic's 7 major fixes) → v3.1 (glm-5.2 outage; roles reassigned). Analysis frozen at sha256 8135fa2c… (D12); 56 tests pass.
- Pilot (4 dossiers, 9 positives): H1a +0.19 [0.05, 0.36]. Agreement signals are weak (OPP 0.57, SC 0.68, DIV 0.67). The closed-book judge reading the opposed accounts gets 0.76 (ceiling 0.84). Dev-stage controls added (D14) and an instructed-debate arm (D15); both are to be frozen as v4 before test.
- Novelty: D4b (passive debate) is novel if narrowed; positioning sentence in `../claude/litreview/novelty-D4b-debate.md`.
- Discord: no collision (D11).
- Incidents: glm-5.2 outage cost about 1 h (D13). About 20% of dossiers fail the keep rule (mostly settled contested points), so spares were raised.
- Schedule: dev by 13:00, test by 20:00. On track. Spend about 17 credits.

## Gate 3 (Sat Nov 14, 09:05 EST): Phase 3 and 4 done; test analysed with both frozen files
- Test: 76 dossiers, 2,280 descriptions (4 excluded), 221/228 complete cells, 4,486 N1 claims, 327 unwarranted. Spend all-time about 22 credits.
- Confirmatory: H1a supported; H2, H3 not supported (negative); R1 supported; R2 supported (I predicted not); R3 not supported. D21.
- Figures: `analysis/figures/test/` (fig2 detectors, fig3 side-taking, fig4 mechanism). Figure 1 still to be drawn by hand.
- Next: results section, discussion, abstract; full paper in the template; deck; Critic pass. Well ahead of the Sun 14:00 draft deadline.

## Audit (Sat Nov 14, 18:15 EST): `../claude/reviews/AUDIT-20261114-1811.md`
- Fixed: run outputs tracked + pinned requirements (fresh clone reproduces test results byte for byte); README, DATA_LICENSES; 4 calibration fixes in drafts; number slots filled; combination score and trivial baselines added; AssertBench added; reference check (13/13 verified, `../claude/reviews/REFERENCE-CHECK.md`); blind human-label sheet.
- Open: no paper/PDF/Figure 1/deck/submission; no commits 09:28–18:11; cross-family strong reader not run; human labels. Paper email confirmed by Hotragn: pettugani.h@northeastern.edu.

## Gate 4 (Sat Nov 14, 20:00 EST): final audit and upgrade done; submission package ready (NOT submitted)
- Report: `../claude/reviews/AUDIT-FINAL.md` (PASS/FAIL/FIXED with evidence). Naming: `../claude/brainstorm/NAMING.md`. References: `../claude/reviews/REFERENCE-CHECK.md` (19 verified, 0 hallucinated).
- New title: **Common Ground Is Not Neutral Ground: Opposed AI Advocates Disagree by Silence**. Benchmark name: **MootPoint**.
- New evidence (exploratory, after test):
  - glm-5.2 cross-family reader 0.836 / 0.849 (rules out judge self-agreement);
  - same-model file ceiling 0.909;
  - contradiction counting 0.513 (chance), giving the "disagree by silence" mechanism;
  - trivial baselines.
- Paper: `paper/paper.md` → `submission/Pettugani_MootPoint_AI-Epistemics-2026.pdf` (12 pp; main text ends p8; abstract 242 words) and `.docx` (official template). Deck: `…_slides.pdf` (7 slides). Form answers: `submission/FORM-ANSWERS.md`.
- Checks:
  - `paper/check_numbers.py` 41/41 + 14/14;
  - fresh clone byte-identical, 85 tests pass;
  - secrets scan clean;
  - Codex read-only review (1 bug fixed, 1 latent noted).
- Spend about 25 credits in total. No money spent. Nothing posted or submitted.
- **Needs Hotragn:**
  1. dismiss the Microsoft Word dialog, then optionally re-export the PDF from the `.docx`;
  2. optional human labels (`analysis/human_labels/`, 60–90 min);
  3. submit via the form;
  4. decide whether to make the repo public.

## Sun Nov 15, 19:40 EST: rerun added; submission package rebuilt (NOT submitted)
- An independent rerun of every test description reproduces all six confirmatory decisions. OPP − SC shrinks to −0.021 [−0.055, 0.015], so the paper and deck now say "no better than resampling" (D22).
- Added since Gate 4: second matcher, loaded-language, error-type, flag-budget and per-domain checks (Appendix D), and two Codex reviews.
- Checks: `check_numbers.py` 49/49 + 14/14. Abstract 249 words. Everything before References fits on 8 pages. `submission/` holds the rebuilt PDF, docx and slides, and FORM-ANSWERS carries the current abstract.
- **Needs Hotragn:** optional human labels (`analysis/human_labels/label.html`, then save `my_labels.csv` there); submit via the form; decide whether to make the repo public.
- Sun 23:00: validation sheet labelled by a model (Codex, GPT-6); κ 0.78 with the judge, reported as an AI check (D23). check_numbers 51/51 + 14/14; still 8 pages. Human labels still absent.

## Mon Nov 16: SUBMITTED by Hotragn
- Hotragn submitted the form (PDF, slides, cover image, repo https://github.com/Hotragn/mootpoint). Final commit before submission: 7a574b4.
