## Appendix A: Limitations and Dual-Use

### Limitations
- **Synthetic evidence.** The case files were written by a model to a specification. Real evidence is messier: contested points are not neatly paired, and documents contradict each other on uncontested points too. The benchmark buys known ground truth at the cost of realism. A follow-up should use real case files with expert-annotated contested points.
- **Model judges.** Labels come from one judge model (qwen3.5-397b). A second judge from another family agreed with κ = [[κ]] on the warranted/unwarranted outcome, and the main reader results hold on the second judge's labels and on claims both judges agree on. No human labels exist yet. The same model family labels claims and serves as the main reader. The second-judge checks reduce, but do not remove, the risk that the reader shares the judge's blind spots.
- **Presence matrix.** Counting depends on a model deciding whether a description asserts a claim. Against gold co-occurrence its agreement is [[agreement]] (κ [[κ_p]]). Noise here weakens all counting detectors. It cannot by itself explain why opposed counting is worse than resampling, because every pair goes through the same matcher.
- **Low base rate.** About [[rate]]% of neutral claims are unwarranted, so intervals are wide. The dossier-cluster bootstrap reflects this.
- **Scope of models and prompts.** Three open-weight generators, one prompt template per framing, temperature 0.7, 200–300 words. Larger models, longer outputs or agentic investigation may behave differently.
- **Pre-registration was revised.** I revised the design four times before the test split was judged and logged each revision with its reason (Section 3.6). Family 2 was written after seeing dev. Test is therefore a replication of dev-based predictions, not a first look.

### Dual-use and ethical considerations
- **Misuse.** The study shows how a stakeholder framing shifts what a model asserts about evidence. Someone could use this to produce a one-sided "neutral" summary on purpose. That effect is already documented (Section 2), and the framings I use are plain one-line role statements. I judge the added risk small and the defensive value larger: the benchmark measures the effect against ground truth and the reading detector flags it.
- **Over-trust in detectors.** A reader with AUROC near 0.8 misses many side-taking claims and flags warranted ones. It should prompt a human to open the evidence, not replace that step. In settings like the investigator's, a false accusation is costly. The friction a flag adds should scale with that cost.
- **No real people.** All case files, names and events are synthetic. No personal data was used.
- **Compute.** All calls went through donated sprint credits (about [[credits]] credits in total). No paid API was used.
