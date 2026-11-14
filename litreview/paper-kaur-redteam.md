# Deep read: Kaur 2026, "What AI Red-Team Evaluations Can and Cannot Prove"

- **Author:** Bandana Kaur
- **Source:** arXiv:2607.21735 (2026-07-23; read v2). 21 pp. No venue. Label: **PRE**.
- **Read:** the full text, covering the intro, the theorems at a high level, Sec. 5 (audit of eight suites), Sec. 6 (claims ladder and reforms) and Sec. 7 (Limitations). Read 2026-11-14.

## Problem
Which safety claims can a red-team or benchmark evaluation support? In particular, how much does a clean sheet (zero observed harms) license?

## Method
- Defines an **"evidential ceiling"**: the largest factor by which one result can move belief under a fixed testing budget. The paper derives it in closed form for the null result of a benchmark.
- Locates a crossing harm rate. Above it, a clean sheet certifies; below it, no feasible passive benchmark can.
- Generalises the result to adaptive and automated red teaming.
- **Audits eight suites by sample size alone**, at assumed harm rates: XSTest (n = 250), SafetyBench (n = 2,100), AdvBench (520), HarmBench (400), StrongREJECT (313), and others.
- Proposes a "claims ladder" (Table 4) and four reforms: pre-registration, calibrated reporting, held-out corpora and independent evaluation.

## Key numbers (quoted)
- **Power:** at p_unsafe = 0.01 with a 50% improvement, power is "14.9 percent (XSTest, n = 250) to 59.3 percent (SafetyBench, n = 2,100)". AdvBench and HarmBench are "at 22.6 and 18.7 percent"; 80% power "requires approximately 3,679 prompts per arm".
- **False certification:** "At p = 0.001, StrongREJECT (n = 313) yields a false-certification probability of 73.1 percent and AdvBench 59.4 percent."
- **Rule of three:** "Zero harms in 520 prompts gives a 95 percent one-sided upper bound of 0.57 percent, roughly one in 174. Zero in 2,100 gives 0.14 percent."
- **Preliminary disclosure review:** "Across nine such documents … only one endpoint reports both an exact numerator and an exact denominator for a binary harm rate, and none reports the dependence structure needed to interpret it. **We develop that audit, and the transparency instrument behind it, separately.**"

## Limitations
- **Stated by the author:**
  - "The mathematics is elementary … We claim no mathematical novelty";
  - the operating-point harm rates are assumed;
  - the suites measure different things (heterogeneous estimands);
  - the distributional gap covers only one mixture component.
- **Not stated:**
  - The audit is of benchmark *designs*, using sample size alone. It does not check what published papers actually *claim* from their results.
  - The review of frontier disclosures covers only n = 9 documents and is preliminary.

## Overlap with D6
**High, and a collision risk.**
1. The statistical argument D6 wanted to make has been made here and turned into a usable "claims ladder": zero-failure results need upper bounds, the rule of three, and power analysis for rare harms.
2. The author **announces a separate audit** of the numerator and denominator reporting in frontier disclosures. That audit may appear at any time.

**What D6 can still claim:** a systematic, pre-registered **audit of absence claims in the 2025–26 research literature** on safety, honesty and alignment papers. That literature is not covered by benchmark-suite design or by frontier disclosures. The audit would code:
- the wording of each claim ("never", "0/N", "no evidence of");
- N and the unit of independence;
- whether a bound is reported;
- the claim the data actually license, scored with Kaur's ladder.

Kaur's framework should be the scoring rubric. D6 should not try to replace it.
