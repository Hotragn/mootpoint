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
