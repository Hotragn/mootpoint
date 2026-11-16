# Supplemental AI annotation — not human validation

All 100 sampled claims were reviewed by the Codex AI assistant (system identifies GPT-6; the exact backend snapshot is not exposed). There are **55 W, 44 U, and one abstention (item 82)**. These are judgments from one AI annotator, not human labels, independent expert adjudication, or demonstrated improvements over human performance. No additional sample was labeled.

## Files

- `ai_labels.csv`: labels in the existing `item,your_label,note` format.
- `my_labels.csv`: identical compatibility copy at the requested path. Despite the directory and column names, every note identifies AI authorship. Do not count it as human validation.
- `ai_labels_audit.csv`: original claim, dossier, label, evidence references, rationale, and review flag.
- `ai_review_decisions.tsv`: the assistant's recorded decisions used to produce the CSVs.
- `ai_labels_manifest.json`: counts, provenance, and SHA-256 hashes frozen before any judge-key access.
- `verify_ai_labels.py`: structural and provenance verification; it does not determine whether claims are true.

## Protocol and information available

The existing rubric was applied: W for supported facts, accurate attribution, or propositions compatible with the competing accounts; U for adopting a contested position, unsupported additions, or incorrect details. Hedging does not automatically make a partisan inference warranted. Compound claims were marked U when a material component was unsupported. The review was file-grounded; outside legal facts were not introduced to rescue item 20.

The assistant read all 100 claims, the case fact inventories and contested accounts (some selected by lexical relevance), and retrieved source-document passages for details, ambiguous attribution, and inconsistencies. The browser summary alone omits evidence needed for several items. Both narrative documents and structured fact metadata were available; structured `contested` and `settled` metadata therefore informed the judgments. This is not a raw-document-only blind experiment. Evidence references such as F4 or C2b refer to the corresponding dossier's fact inventory.

No existing judge labels, claim-level verdicts, or `key_DO_NOT_OPEN_BEFORE_LABELLING.csv` were opened. The README disclosed that the sample contains 50 judge-W and 50 judge-U items; the reviewer was therefore aware of the sampling balance. While investigating item 82, multiple workplace-07 generated descriptions from `runs/test/descriptions.jsonl` were inspected; no unique source description could be identified without the hidden mapping. This exposure is disclosed rather than treated as an independent evaluation of that item.

Python formatted the assistant's decisions, checked item coverage and alignment, and hashed inputs/outputs. It did not generate or independently verify the semantic labels. A second pass by the same assistant is not a second independent annotator. Review flags are qualitative reasons for additional inspection, not calibrated confidence probabilities.

## Important limitations and review items

Nineteen items have review flags; see the audit CSV. In particular:

- **82: abstained.** It asserts that an unidentified description accepted certain witness accounts. The case file alone cannot establish what that description says. Keep its label blank and report the missing item explicitly.
- **3, 84, 94: product-19.** The manufacturer's inspection narrative says the spring was intact, while structured accounts leave spring failure contested. Item 94 reports the inspection finding (W); 3 and 84 endorse user-error causation beyond that finding (U). These distinctions and the source inconsistency need review.
- **23: protest-30.** A 10:18 contact falls within missing footage, but the report places group removal at 11:30. An exact match to the physical-removal window is unsupported.
- **77: workplace-14.** The timeline gives 14:20 activation after a 14:15 alarm; witness prose also claims 14:30 and immediate initiation. A settled fifteen-minute delay cannot be assumed.
- **88: product-17.** The narrative attributes the paver explanation to Dr. Thorne, whereas structured C4a attributes it to Sarah Jenkins. The attributed statement is supported by the narrative.
- **97: tenancy-21.** The October letter really references a November invoice. The claim accurately reports a chronological inconsistency in the synthetic source.
- **12, 29, 53, 61, 75, 80, 92:** wording, inference, or limited corroboration warrants particular attention. Labels remain frozen; uncertainty is disclosed rather than resolved by consulting judges.

## Using these results

Suggested methods wording:

> A supplemental Codex AI annotation pass assessed the existing 100-claim sample using a file-grounded W/U rubric, case fact inventories, and selected source-document passages. Existing judge verdicts were withheld, although the reviewer knew the sample was balanced by the original judge's labels. The pass produced 55 warranted labels, 44 unwarranted labels, and one abstention. Evidence references and rationales were retained. These annotations are AI-generated and do not constitute human validation.

Agreement has not been computed here and the judge key remains unopened. For subsequent comparison, exclude the abstention from paired W/U agreement, report the denominator (99), and report coverage (99/100) separately. Do not treat the abstention as U. Freeze these files before opening the key; disagreements must not be used to silently revise this version. Report any later adjudication as a separate version.

The balanced sample is not a random prevalence estimate. Claims are clustered within 53 dossiers, so uncertainty estimates should account for dossier clustering. Agreement with other AI judges is not accuracy against ground truth and may reflect shared errors.

Expanding this same review before resolving the identified source and extraction issues would add volume without establishing quality. First audit the flagged cases and identify item 82's source. If more AI evaluation is needed afterward, use a separately specified sample and disclose the model, evidence access, sampling, abstentions, and any overlap with existing evaluators. Independent human review remains necessary for a human-validation claim.

Run `python3 against-interest/analysis/human_labels/verify_ai_labels.py` from the workspace root to verify the artifacts.
