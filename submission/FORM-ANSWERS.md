# Submission form answers (for Hotragn to paste; I have not submitted anything)

| Field | Answer |
|---|---|
| ProjectTitle* | Common Ground Is Not Neutral Ground: Opposed AI Advocates Disagree by Silence |
| PDF File* | `Pettugani_MootPoint_AI-Epistemics-2026.pdf` |
| InterestedInPublishing* | Your call (recommended: yes) |
| Tracks | Track 1: Model Epistemics & Decision-Making Evals (primary: MootPoint benchmark of requester-induced side-taking). Track 2: Trust Infrastructure (the reading detector vs consensus filters). |
| Presentation (URL) | leave blank, or a video link if you record one |
| Code (URL) | leave blank unless you make the repo public (your decision; I took no outward action) |
| Slideshow File | `Pettugani_MootPoint_AI-Epistemics-2026_slides.pdf` |
| Image File | `Pettugani_MootPoint_AI-Epistemics-2026_figure1.png` |
| AdditionalLink | leave blank |
| TeamName* | Hotragn Pettugani (solo) |
| Location* | your location |
| Member1 Name* | Hotragn Pettugani |
| Member1 Email* | pettugani.h@northeastern.edu |
| Member1 Discord / Scholar | yours |

## ProjectSummary* (same as the paper abstract)
Can agreement between opposed AI advocates identify claims that overstate evidence? I test an intersection filter: ask one model to describe a case for each side, then distrust claims that both descriptions do not repeat. MootPoint contains 100 synthetic case files with specified factual and contested points, rendered and checked by models. Three model families described each file under ten request conditions. On 76 held-out files, a judge labelled 4,486 neutral-description claims, including 327 unwarranted claims. Requester-aligned side-taking increased by 0.145 [0.100, 0.191]. Opposed agreement performed worse than neutral resampling in the original run (AUROC 0.656 versus 0.704); the rerun difference was inconclusive (−0.021 [−0.055, 0.015]). Opposed descriptions omitted more warranted claims while repeating unwarranted claims at similar rates. A strong reader of the neutral text reached 0.828; a reader from another family reached 0.836. Opposed context added 0.035 [0.012, 0.059], without establishing a unique benefit of opposition. Confirmatory analyses were frozen before test judging. A later AI audit found source inconsistencies and extraction issues; excluding affected dossiers preserved the main pattern in both runs. All retained GLM neutral outputs exceeded the requested word limit, but the original-run result also held without GLM. These checks strengthen robustness, not ground-truth certainty: human validation remains absent. Opposed agreement offers no demonstrated advantage over resampling here; source-free readers are useful triage signals, not fact checkers.
