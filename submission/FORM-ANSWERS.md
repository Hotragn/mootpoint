# Submission form answers (for Hotragn to paste; I have not submitted anything)

| Field | Answer |
|---|---|
| ProjectTitle* | Common Ground Is Not Neutral Ground: Opposed AI Advocates Disagree by Silence |
| PDF File* | `Pettugani_MootPoint_AI-Epistemics-2026.pdf` |
| InterestedInPublishing* | Your call (recommended: yes) |
| Tracks | Track 1 (claims, honesty benchmarks and what keeps them meaningful). Optional second tick: Track 2 (verification tools). |
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

## ProjectSummary* (same as the paper abstract, 242 words)
A tempting way to remove a requester's bias from an AI description of evidence is to ask for the description twice, once for each opposed stakeholder, and keep only what both concede. Community Notes applies the same bridging logic to human raters. I test this "common ground" filter against ground truth. I built MootPoint, 100 synthetic case files whose contested points are known by construction, and had three models from three families describe each file under ten requester framings. A judge labelled 4,486 claims in held-out neutral descriptions; 327 take a side on a contested point or invent a fact. Requester framing shifts side-taking toward the requester (+0.145 [0.100, 0.191]). But agreement between opposed descriptions is a worse detector of side-taking (AUROC 0.656) than agreement between plain resamples (0.704) or between two non-stakeholder descriptions (0.746). The reason is how advocates disagree. They almost never contradict a claim; they drop the true facts that hurt them, so requiring agreement flags warranted claims. Counting contradictions instead is no better than chance (0.513). A strong model that reads only the neutral description does far better (0.828), and a reader from a different family than the judge matches it (0.836). Adding the opposed descriptions helps the reader by at most 0.035 AUROC, no more than any other two extra descriptions. All hypotheses and analysis code were frozen before the test split was judged. For AI fact-finding, what opposed advocates both say is not a neutrality signal.
