# MootPoint: Common Ground Is Not Neutral Ground

Code, benchmark and data for "Common Ground Is Not Neutral Ground: Opposed AI Advocates Disagree by Silence" (Apart AI x Epistemics Research Sprint, Nov 2026). Author: Hotragn Pettugani, Independent Researcher (pettugani.h@northeastern.edu).

**Finding.** Opposed agreement showed no reliable advantage over neutral resampling. In the original run AUROC was 0.656 versus 0.704; the rerun difference was inconclusive (−0.021 [−0.055, 0.015]). Opposed descriptions omitted more warranted claims. Strong readers reached 0.83–0.84 from the neutral text alone, but are triage tools rather than fact checkers.

**MootPoint** contains 100 synthetic case files with specified and model-checked facts and disputes. A post-test audit found five suspect dossiers, two meta-description claims, and output-length noncompliance. Sensitivity exclusions preserve the original-run pattern; they do not certify ground truth. See paper Appendix E and `analysis/VALIDITY-AUDIT-PROTOCOL.md`.

**Supplemental labels are AI-generated:** 55 W, 44 U, one abstention. Agreement is 88/99 with the first judge and 80/99 with the second on a judge-stratified sample. No human validation has been performed. The original confirmatory labels and scripts are unchanged.

## Reproduce every number (offline, no API key)
Run outputs (`runs/dev`, `runs/test`) are committed.
```bash
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest -q                      # 87 tests
.venv/bin/python analysis/analyze.py --claims runs/test/claims.jsonl --dossiers data/dossiers --out analysis/results/test/
.venv/bin/python analysis/readers.py --claims runs/test/claims.jsonl --signals analysis/results/test/per_claim_signals.csv --out analysis/results/test/
.venv/bin/python analysis/audit_extras.py --split test        # exploratory: trivial baselines, glm-5.2 closed-book reader
.venv/bin/python analysis/exploratory_final.py --split test   # exploratory: contradiction counting, glm-5.2 with-file ceiling
.venv/bin/python analysis/figures/make_figures.py --split test
.venv/bin/python analysis/validity_audit.py                    # post-test source/compliance audit
```
Expected: `analysis/results/test/*.json` byte-identical to the committed files; Figures 2–3 in `analysis/figures/test/`.

Frozen confirmatory analysis (sha256): `analysis/analyze.py` 8135fa2c… (Family 1), `analysis/readers.py` 1f1af820… (Family 2). See `analysis/FREEZE*.md`, `PLAN.md` (pre-registration v1–v4) and `DECISIONS.md`. Everything in `audit_extras.py` and `exploratory_final.py` was added after the test results and is labelled exploratory in the paper.

## Build the paper and deck
```bash
python3.12 -m venv paper/.venv && paper/.venv/bin/pip install -r paper/requirements-render.txt
paper/.venv/bin/python paper/build_docx.py     # official Apart template (.docx) from paper/paper.md
paper/.venv/bin/python paper/build_portable_pdf.py    # offline PDF; no browser required
paper/.venv/bin/python paper/build_portable_slides.py # revised 8-slide PDF
.venv/bin/python paper/check_numbers.py        # every quoted number matches the result files
```
Figure 1 source: `paper/figures/make_method_figure.py` (Matplotlib). The draw.io file is retained as a legacy design, not the current rendering source. The Chrome builder remains available but was blocked by the execution environment; the final PDF uses ReportLab and was visually checked. Use the PDF for submission. The editable DOCX is rebuilt from the same text but requires a local Word layout check.

## Regenerate from scratch (needs Adaption credits)
Put `ADAPTION_API_KEY` in `../.env` (never committed). Then `harness/dossiers.py`, `harness/describe.py --split test`, `harness/judge.py --split test --stages labels,presence,verifiers,judge2`, `harness/xf_strong.py`, `harness/vfile_strong.py`. Every call is cached in `runs/cache.sqlite` (not committed). The API has no seed, so a fresh run at temperature > 0 gives different text. Total spend for the project: about 25 credits.

## Layout
`harness/` generation and judging · `data/dossiers/` the 100 MootPoint case files · `runs/` all model outputs · `analysis/` frozen and exploratory analysis, results, figures · `analysis/human_labels/` a 100-claim sheet for human validation (labels hidden; key separate) · `paper/` source, builders, figures · `submission/` final PDF, slides, form answers.

## Preexisting work (disclosure)
The Adaption endpoint and payload fields in `harness/llm.py` follow what I learned in my earlier project `approve-what-you-see`. No code, data or analysis from that project or from `Ai swarm alignment` is reused. Everything else was written during the sprint.

## Tools
Claude Code wrote most code and text under my direction. ChatGPT (web) was used once for a literature cross-check and title ideas; Codex reviewed code and paper, generated the disclosed AI labels, implemented the post-test validity audit, and revised the submission. AI annotation is not human validation. Experiment models ran on Adaption sprint credits. No paid API was used.

## Audit and archive reproduction

The exclusion protocol was fixed before computing the new subset results, after earlier results and audit findings were visible. This is exploratory sensitivity, not preregistration. The frozen labels are checked against their SHA-256 manifest before joining the now-open judge key. Never silently overwrite them.

```bash
python3 analysis/human_labels/verify_ai_labels.py
.venv/bin/python analysis/validity_audit.py
.venv/bin/python paper/check_numbers.py
python3 paper/build_archive.py
```

`submission/MootPoint-reproducibility.zip` is a self-contained local sharing artifact, not a public URL. It excludes credentials, caches, virtual environments and Git internals. Its embedded manifest records every included file's SHA-256. The official template is included under `paper/template/` for the optional DOCX build. All generated labels remain AI-generated despite the legacy folder name `human_labels`.
