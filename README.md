# MootPoint: Common Ground Is Not Neutral Ground

Code, benchmark and data for "Common Ground Is Not Neutral Ground: Opposed AI Advocates Disagree by Silence" (Apart AI x Epistemics Research Sprint, Nov 2026). Author: Hotragn Pettugani, Independent Researcher (pettugani.h@northeastern.edu).

**Finding.** When the same evidence is described for opposed stakeholders, keeping only what both descriptions say is a *worse* detector of side-taking than plain resampling (AUROC 0.656 vs 0.704), because advocates disagree by silence: they omit true facts that hurt them instead of contradicting them. A strong model reading the neutral description alone does far better (0.83–0.84; ceiling with the file 0.91).

**MootPoint** is the benchmark: 100 synthetic case files whose contested ("moot") points are known by construction, with 2,280 test descriptions under ten requester framings and 13,514 labelled claims.

## Reproduce every number (offline, no API key)
Run outputs (`runs/dev`, `runs/test`) are committed.
```bash
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest -q                      # 85 tests
.venv/bin/python analysis/analyze.py --claims runs/test/claims.jsonl --dossiers data/dossiers --out analysis/results/test/
.venv/bin/python analysis/readers.py --claims runs/test/claims.jsonl --signals analysis/results/test/per_claim_signals.csv --out analysis/results/test/
.venv/bin/python analysis/audit_extras.py --split test        # exploratory: trivial baselines, glm-5.2 closed-book reader
.venv/bin/python analysis/exploratory_final.py --split test   # exploratory: contradiction counting, glm-5.2 with-file ceiling
.venv/bin/python analysis/figures/make_figures.py --split test
```
Expected: `analysis/results/test/*.json` byte-identical to the committed files; Figures 2–3 in `analysis/figures/test/`.

Frozen confirmatory analysis (sha256): `analysis/analyze.py` 8135fa2c… (Family 1), `analysis/readers.py` 1f1af820… (Family 2). See `analysis/FREEZE*.md`, `PLAN.md` (pre-registration v1–v4) and `DECISIONS.md`. Everything in `audit_extras.py` and `exploratory_final.py` was added after the test results and is labelled exploratory in the paper.

## Build the paper and deck
```bash
python3.12 -m venv paper/.venv && paper/.venv/bin/pip install python-docx==1.1.2 pypdf==5.1.0
paper/.venv/bin/python paper/build_docx.py     # official Apart template (.docx) from paper/paper.md
paper/.venv/bin/python paper/build_pdf.py      # PDF via headless Chrome, same source and layout
.venv/bin/python paper/check_numbers.py        # every quoted number matches the result files
```
Figure 1 source: `paper/figures/fig1_method.drawio` (open in draw.io / diagrams.net).

## Regenerate from scratch (needs Adaption credits)
Put `ADAPTION_API_KEY` in `../.env` (never committed). Then `harness/dossiers.py`, `harness/describe.py --split test`, `harness/judge.py --split test --stages labels,presence,verifiers,judge2`, `harness/xf_strong.py`, `harness/vfile_strong.py`. Every call is cached in `runs/cache.sqlite` (not committed). The API has no seed, so a fresh run at temperature > 0 gives different text. Total spend for the project: about 25 credits.

## Layout
`harness/` generation and judging · `data/dossiers/` the 100 MootPoint case files · `runs/` all model outputs · `analysis/` frozen and exploratory analysis, results, figures · `analysis/human_labels/` a 100-claim sheet for human validation (labels hidden; key separate) · `paper/` source, builders, figures · `submission/` final PDF, slides, form answers.

## Preexisting work (disclosure)
The Adaption endpoint and payload fields in `harness/llm.py` follow what I learned in my earlier project `approve-what-you-see`. No code, data or analysis from that project or from `Ai swarm alignment` is reused. Everything else was written during the sprint.

## Tools
Claude Code wrote most code and text under my direction. ChatGPT (web) was used once for a literature cross-check and title ideas; Codex CLI once, read-only, to review the exploratory analysis code (`../codex/`). Experiment models ran on Adaption sprint credits. No paid API was used.
