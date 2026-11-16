# Exploratory validity sensitivity audit

This protocol is written after the original results and after the supplemental AI labels were frozen. It is not a preregistration or independent replication. The judge key has now been opened for comparison; frozen AI decisions will not be revised to agree with it.

Before computing the new sensitivity statistics, fix these exclusions:

1. Remove the two identified meta-description claims: product-17 / gemma-4-31b-it / N1:15 and workplace-07 / glm-53-flash / N1:15. These phrases describe an interpretation of a generated description rather than a standalone case proposition. Their exact source descriptions are retained for inspection.
2. Remove all five dossiers identified by the frozen AI audit's `inconsistent_source` flags: product-19, protest-30, workplace-14, product-17, tenancy-21. This deliberately excludes every claim from each affected dossier, not just claims that change a detector score. These are suspected inconsistencies, not expert-adjudicated errors.
3. Apply both exclusions together. For the independent generation rerun, apply the dossier exclusion only: claim IDs from the first run must not be transferred to a new generation.

Report the original sample alongside these subsets. Retain the original labels, scores, and frozen confirmatory scripts. Report AUROC and paired differences for OPP, SC, DIV, N1-only reading, and reading with opposed context, using 10,000 dossier-cluster bootstrap resamples and seed 20261114. Report H1a on the dossier-restricted data. No hypothesis decisions or significance-based subset selection will be added.

Compare the 99 frozen non-abstaining AI labels to both judges using raw agreement, Cohen's kappa, confusion counts, and dossier-cluster bootstrap intervals. Report 99/100 coverage and 50/50 original-judge-stratified sampling; neither raw agreement nor kappa is a population accuracy estimate or human validation. Retain all disagreements and provenance.

The audit does not certify the remaining dossiers as error-free. No new human judgments or new model calls are involved. A representative independent human audit remains a limitation. Improvements to wording and disclosure must reflect these constraints whether sensitivity results are favorable or unfavorable.

## Output-compliance extension

Source tracing exposed unfinished analysis in a GLM output. A word-count audit (before computing the following sensitivity results) found all 76 nonempty GLM N1 outputs above the requested 200–300 words. Add two explicit subsets in each run: exclude generator glm-53-flash entirely; retain only cells whose N1 output has 200–300 whitespace-delimited words. The latter checks N1 length only, not compliance of the other context descriptions or absence of reasoning prose. Report actual word counts by generator. These are additional post-test analyses, not new confirmatory tests. Preserve noncompliant outputs in the original analysis.
