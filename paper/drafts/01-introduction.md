## 1 Introduction

At the sprint's opening talks, a visual investigator described asking one model about one protest video twice. Prompted as a human-rights activist, the model described disproportionate force. Prompted as a prosecutor, it described an illegal mob committing arson. The video did not change. Only the requester did. His team shows such descriptions to users, and nothing tells them which details come from the video and which from the prompt.

This is a general problem for AI-assisted fact-finding. Investigators, journalists and courts increasingly ask models to describe evidence. The person asking usually has a stake. If the stake leaks into the description, the description settles disputes that the evidence leaves open. A reader who cannot open the evidence cannot tell.

A natural fix borrows from adversarial legal process: ask for the description from opposed stakeholders and keep only what both concede. A claim that survives a prosecutor's framing and a defender's framing should be safe. This is cheap, needs no labels and no access to the source, and extends self-consistency checks from resampling to adversarial prompting.

I test this idea against ground truth. I built 100 synthetic case files in four domains. Each file contains verified facts and contested points: pairs of conflicting witness accounts that nothing else in the file settles. Three models from three families described each file under ten requester framings. A judge labelled each claim of a neutral description as warranted or unwarranted, where unwarranted means it takes a side on a contested point or invents a fact. I then compared two detectors that never see the file. *Counting* scores a claim by how many other descriptions repeat it. *Reading* asks a strong model to judge the claim from the descriptions alone.

My contributions:
1. **A benchmark with known contested points.** Requester-framing effects can be measured against what the evidence actually settles, not only as instability between framings.
2. **Requester framing induces side-taking.** [[H1a result]]
3. **Agreement across opposed requesters is a worse detector than plain resampling.** [[H2/H3 result]] Opposed descriptions omit true facts that hurt their side, so counting penalises warranted claims.
4. **Reading beats counting, and opposition adds little to reading.** [[R1–R3 result]] A weaker reader does much worse, so the gain depends on reader capability.

All hypotheses, analysis code and predictions were frozen before any test description was judged. Test is a replication of written predictions from a separate dev split.
