## 2 Related Work

**Framing drift on fixed evidence.** Several 2025–26 studies show that who asks, or what goal is set, changes what a model says about the same evidence:
- **Cho et al. (2025)** had models summarise Swiss court opinions "from the perspective of" a judge, prosecutor or defence. Adversarial roles included fewer facts.
- **Yousefi et al. (2026)** found that persona changes which health facts six frontier models give. An expert-written "factual floor" in the system prompt narrows the gaps by 25 to 62 percentage points.
- **JANUS (Giannouris et al., 2026)** gives models a fixed six-fact pool and an institutional goal. Selection barely moves, while ordering and framing shift.
- **Isch and Jennings (2026)** show that a user's stance shifts the rhetoric of summaries of science.
- **Asaad et al. (2026)** are closest. Investor roles shift a "neutral" evidence score computed from the same SEC filings, and 69% of the effect survives neutral retrieval. They measure stability, "not deviation from externally validated ground truth".

I measure drift against ground truth. The contested points of each case file are known by construction, so a claim that settles one is side-taking by definition.

**Consistency as verification, and its limits.** Sampling a model several times and keeping what it repeats is a common unsupervised check. Ganesh et al. (2026) show that such detectors "detect consistency, not correctness". Tan et al. (2025) show that errors a model makes consistently defeat all four families of consistency detector they test. A natural strengthening is to vary the prompt adversarially rather than resample it, and keep what survives opposed framings. No prior work tests this against ground truth. I test it and find it fails.

**Debate and judges without the source.** My reading condition is structurally a static, information-asymmetric debate: a judge without the source reads outputs from parties who saw it (Irving et al., 2018; Khan et al., 2024; Kenton et al., 2024). Khan et al. found static debate as effective as interactive debate on QuALITY. Carro et al. (2026) report that weaker AI judges gain little from debate. Radharapu et al. (2025) find that judges themselves take stances on contested topics.

My setting differs in three ways:
- The "advocates" are ordinary descriptions requested by opposed stakeholders. They are never instructed to argue.
- The judged object is claim-level side-taking in a third, neutral description, not a choice between answers.
- Ground truth comes from which points the evidence leaves contested.

I also include an instructed-debate arm, so the comparison with debate is measured rather than assumed.
