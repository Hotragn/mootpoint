# Human label sheet (pre-registered, PLAN.md "Validation")
100 test N1 claims: 50 the judge called unwarranted, 50 warranted, shuffled (seed 20261114). Signals and labels are hidden.
For each row, open `dossier_file` and set `your_label` to:
- `W` warranted: a verified fact, an attributed account, or something every contested version allows;
- `U` unwarranted: takes one witness's side on a contested point, or states a wrong/invented fact.
Do not open the key file until all 100 are labelled. Then the agreement (κ with judge and judge2) can be reported. About 60–90 minutes.

**Status (Sun Nov 15):** the sheet was labelled by Codex (GPT-6), an AI annotator, not a human. `my_labels.csv` is an identical copy of `ai_labels.csv` (kept so `verify_ai_labels.py` hashes still match); it is NOT human labels. See `AI_LABELING_REPORT.md` and `analysis/ai_annotator.py`.
