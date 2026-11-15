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

## ProjectSummary* (same as the paper abstract, 250 words)
When an AI model describes evidence, the person asking can bias it. A tempting fix is to ask twice, once for each side of a dispute, and keep only what both descriptions say. Community Notes applies the same "common ground" logic to human raters. I test this filter against known answers. I built MootPoint, 100 synthetic case files whose disputed points are known by construction, and had three models from three families describe each file for ten different requesters. A judge model labelled 4,486 claims in held-out neutral descriptions; 327 take a side on a disputed point or invent a fact. Descriptions requested by one side take that side more often (+0.145 [0.100, 0.191]). But agreement between the two sides is a worse detector of side-taking (AUROC 0.656, where 0.5 is guessing and 1 is perfect) than agreement between two plain repeat requests (0.704) or between two neutral requesters (0.746). The reason is how the sides disagree. They almost never contradict a claim; they leave out the true facts that hurt them, so requiring agreement flags true claims. A strong model that reads the neutral description does far better (0.828), and a reader from a different family than the judge matches it (0.836). Adding the two sides' descriptions helps the reader by at most 0.035 AUROC, no more than any other two extra descriptions. All hypotheses and analysis code were frozen before the test split was judged. For AI fact-finding, what opposed sides both say is a weak neutrality signal.
