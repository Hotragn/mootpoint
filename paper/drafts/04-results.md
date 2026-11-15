## 4 Results

The test split has 76 case files. Of 228 file × model cells, 221 were complete. Seven were excluded: four lost a description to empty outputs and three had a stakeholder description with no valid labels. The 221 cells hold 4,486 neutral (N1) claims, of which 327 (7.3%) are unwarranted. Table 1 gives the six confirmatory tests. Five of my six written predictions held.

**Table 1.** Confirmatory tests on the test split. Estimates with 95% dossier-cluster bootstrap intervals; one-sided p, Holm-adjusted within each family.

| Test | Prediction | Estimate [95% CI] | Holm p | Supported |
|---|---|---|---|---|
| H1a: requester-aligned side-taking | yes | +0.145 [0.100, 0.191] | 0.0003 | yes |
| H2: ΔAUROC(OPP − SC) > 0 | no | −0.048 [−0.073, −0.024] | 1.00 | no |
| H3: ΔAUROC(OPP − DIV) > 0 | no | −0.091 [−0.123, −0.061] | 1.00 | no |
| R1: reading N1 alone beats SC counting | yes | +0.125 [0.071, 0.178] | 0.0003 | yes |
| R2: adding A and B helps the reader | no | +0.035 [0.012, 0.059] | 0.003 | yes |
| R3: A and B help more than P1 and P2 | no | −0.021 [−0.041, 0.002] | 0.96 | no |

### 4.1 Requester framing induces side-taking
When a stakeholder asks, the description takes that stakeholder's side more often (Figure 3). Of side-taking claims in N1, 65% favour side A. In A's own description this rises to 82%. For side B the share rises from 35% in N1 to 47% in B's description. The pooled shift H1a is +0.145 [0.100, 0.191]. Stakeholder descriptions also omit true facts that favour the other side more than neutral ones do (exploratory H1b difference-in-differences +0.030 [0.007, 0.052]).

### 4.2 Agreement across opposed requesters is a worse detector
Counting is weak overall, and opposition makes it weaker (Figure 2). AUROC for unwarranted N1 claims is 0.656 for the opposed pair, 0.704 for neutral resamples and 0.746 for the clerk and journalist. The opposed pair is no better than one side sampled twice (0.654). H2 and H3 are not supported. Both differences are negative and their intervals exclude zero. The result holds when the positives are restricted to side-taking claims (OPP − SC −0.054 [−0.080, −0.029]), and the point estimate is lower for each of the three generators.

Figure 4 shows why. Opposed descriptions repeat only 60% of warranted N1 claims, against 71% for neutral resamples. For unwarranted claims the two rates are the same: 115 and 116 of 327 (35%). Each stakeholder drops true facts that hurt its side, so a warranted claim often survives in only one of the two. Requiring agreement then flags it. Opposition does not make side-taking claims harder to repeat. It makes true claims easier to lose.

### 4.3 Reading beats counting, and the kind of context does not matter
A strong reader that sees only N1 reaches AUROC 0.828, against 0.704 for the best comparable counting signal (R1, +0.125 [0.071, 0.178]). This is within 0.04 of a reader that sees the case file itself (0.866).

Adding the two opposed descriptions raises the reader to 0.863 (R2, +0.035 [0.012, 0.059]). I predicted no gain, so this prediction failed. But the gain is not specific to opposition. Two neutral resamples give 0.862, an instructed debate gives 0.865, and the clerk and journalist give 0.884. The opposed context is 0.021 below the non-stakeholder context (R3, [−0.041, 0.002]). The comparisons between contexts other than R2 and R3 are descriptive.

Counting gains nothing when added to reading: the pre-registered combination (mean rank of the reader and the opposed count) scores 0.833, below the reader alone (0.863). Simple baselines sit far below: a random score gives 0.504, claim length 0.450, and a count of evaluative words (for example "clearly", "negligent", "suggests") 0.593. These baselines were added during the audit and are exploratory.

Reader capability matters more than context. A weaker reader from another family (deepseek-v4-flash) reaches 0.668 on N1 alone and 0.648 with A and B: below the best counting signal, and with no gain from opposition.

### 4.4 Validity checks
- **Second judge.** A judge from another family agreed with the main judge on the outcome with κ = 0.81. Re-scored on its labels, the ordering holds: counting 0.656 to 0.747, closed-book strong readers 0.874 to 0.909. On claims where both judges agree (250 positives), they reach 0.894 to 0.931.
- **Presence matrix.** For gold-fact claims, the matrix agrees with gold co-occurrence in 73% of cases (κ 0.36). This noise applies to every counting pair equally.
- **Generators.** OPP is below SC for all three generators (deepseek 0.595 vs 0.667, gemma 0.600 vs 0.632, glm 0.752 vs 0.791). The strong reader with A and B is between 0.853 and 0.876 for all three.
