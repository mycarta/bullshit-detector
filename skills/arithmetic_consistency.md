# Arithmetic Consistency Skill (Tier 1)

> Detailed worked examples to be written after code is stable.
> See p_checker.py and grimmer.py docstrings for function descriptions.
> See Session_Handoff_05.md for implementation notes and source references.

## P-hacking detection heuristics (checklist)

When a paper reports barely significant results (p ≈ 0.04), consider whether
any of these p-hacks might have been applied. Taxonomy from Reis & Friese (2022):

- **Optional stopping** — data collection stopped when p < 0.05, not at pre-determined n.
  Szucs (2016) shows via simulation how this inflates false positive rates.
- **Collecting additional data** — adding observations until significance is reached
- **Transforming distributions** — trying multiple transforms, picking the one that gives p < 0.05
- **Selectively excluding outliers** — trying multiple exclusion criteria, keeping the significant one
- **Trying multiple analytic methods** — running different tests, reporting the significant one
- **Multiple modelling** — trying different variable combinations without theoretical justification
- **Post-hoc replacement** — swapping conditions or subgroups after seeing results
- **Rounding p-values** — reporting p = 0.05 when computed p = 0.054

Key context: p > 0.05 does not mean "no effect" and p < 0.05 does not mean
"real effect" (Amrhein et al. 2017, "The earth is flat (p > 0.05)").

## Prosecutor's fallacy (transposed conditional)

The most fundamental p-value misinterpretation. Confuses:

- P(data | H₀) — the p-value. "If there's no effect, how surprising is this data?"
- P(H₀ | data) — what people want. "Given this data, how likely is the null?"

These are not the same. Bayes' theorem connects them, but you need the
**base rate** (prior probability of H₀) to convert one into the other.

**Named after its use in court:** "The probability of this DNA match occurring
by chance is 1 in a million, therefore there is only a 1-in-a-million chance
the defendant is innocent." Wrong — if 10 million people were tested, you'd
expect ~10 matches, and the defendant is just one of them. The prior matters.

**How it appears in research papers:**

- "p = 0.03, so there is only a 3% probability this result is due to chance"
  → WRONG. p = 0.03 means: if H₀ were true, you'd see data this extreme
  3% of the time. It says nothing about the probability H₀ is true.
- "The association was statistically significant (p < 0.01), confirming
  that X causes Y" → double error: transposes the conditional AND leaps
  from association to causation.
- "We found no significant difference (p = 0.34), demonstrating that the
  groups are equivalent" → inverse prosecutor's fallacy. Absence of
  evidence ≠ evidence of absence. The study may simply be underpowered
  (connect to `power.achieved_power()`).

**Red flags for LLM audit:**

1. Any sentence that equates the p-value with the probability of the
   null hypothesis being true → flag as prosecutor's fallacy.
2. Language like "only a X% chance this is due to chance" → flag.
3. "No significant difference, therefore no difference" → flag, then
   check power. If achieved power < 0.50, the non-significant result
   is uninformative.
4. Multiple comparisons without correction combined with transposed
   conditionals are especially dangerous: with 20 tests at α = 0.05,
   you expect 1 "significant" result even if all nulls are true. If
   the authors then claim P(H₀ | data) = 0.05 for that one result,
   they've compounded two errors.

**The Bayesian correction (for intuition, not for the skill file to compute):**
P(H₀ | data) depends on the prior P(H₀). If you're testing an implausible
hypothesis (high prior for H₀), even a small p-value may correspond to a
high posterior probability of H₀. Conversely, if the hypothesis is highly
plausible a priori, a marginal p-value may be convincing. This is why
Ioannidis (2005) showed that "most published research findings are false"
— when base rates of true effects are low and studies are underpowered,
the majority of significant results are false positives even at p < 0.05.

## Subgroup interaction fallacy

"Significant in subgroup A, not significant in subgroup B" does NOT mean
"the effect differs between A and B." This is one of the most common
misinterpretations in published research. Gelman & Stern (2006) put it
concisely: "the difference between significant and not significant is
not itself statistically significant."

**The correct test:** A formal interaction test (treatment × subgroup) that
directly tests whether the effect SIZE differs between subgroups.

**Worked example (from Miede 2019, PhUSE):**
A randomized trial shows overall HR = 0.54 (p < 0.0001). Subgroup analysis:
males HR = 0.51 (p = 0.0003, n = 143), females HR = 0.64 (p = 0.12, n = 57).
Naive conclusion: "treatment works in men but not women." Interaction test:
p = 0.36 — no evidence of differential effect. The apparent difference is
entirely explained by lower power in the smaller female subgroup. Both HRs
point in the same direction (< 1); only the confidence interval width differs.

**Red flags to check in any paper claiming differential subgroup effects:**

1. Did they report an interaction test, or only within-subgroup p-values?
   If only within-subgroup p-values → flag.
2. Are the subgroup sample sizes very unequal? Smaller subgroup will have
   wider CIs and is more likely to be "not significant" even if the true
   effect is identical.
3. Were multiple subgroups tested? Each additional subgroup test without
   multiplicity correction inflates the family-wise error rate. With k
   subgroups at α = 0.05, P(≥1 false positive) = 1 − (0.95)^k.
4. Was the subgroup analysis pre-specified or post-hoc? Post-hoc subgroup
   analyses are exploratory — language like "demonstrates" or "proves" is
   inappropriate.
5. Do the confidence intervals for the effect sizes overlap between
   subgroups? If they overlap substantially, the subgroups are likely
   consistent even if one is "significant" and the other is not.

**Where this connects to other modules:**
- `power.achieved_power()` — compute power for each subgroup separately.
  A "non-significant" subgroup result with power < 0.50 is uninformative,
  not evidence of no effect.
- `causal_consistency.md` → Concomitant Variation — if a paper claims
  dose-response in one subgroup but not another, check whether the
  "failure" subgroup simply had insufficient n.

## References

- Amrhein, Korner-Nievergelt & Roth (2017), "The earth is flat (p > 0.05):
  significance thresholds and the crisis of unreplicable research", PeerJ 5:e3544
- Gelman & Stern (2006), "The Difference Between 'Significant' and 'Not
  Significant' is not Itself Statistically Significant", The American
  Statistician 60(4):328–331
- Goodman (1999), "Toward Evidence-Based Medical Statistics. 1: The P Value
  Fallacy", Annals of Internal Medicine 130(12):995–1004
- Ioannidis (2005), "Why Most Published Research Findings Are False",
  PLoS Medicine 2(8):e124
- Miede (2019), "Misuse and Misapplication in Statistical Data Analysis —
  A Topic that Never Goes Out of Style", PhUSE US Connect 2019, Paper AB11
  (Best Presentation, Analytics/Big Data/Statistics)
- Pocock, Assmann, Enos & Kasten (2002), "Subgroup analysis, covariate
  adjustment and baseline comparisons in clinical trial reporting: current
  practice and problems", Statistics in Medicine 21:2917–2930
- Reis & Friese (2022), "The Myriad Forms of p-Hacking", in *Avoiding Questionable
  Research Practices in Applied Psychology*, Springer
- Szucs (2016), "A Tutorial on Hunting Statistical Significance by Chasing N",
  Frontiers in Psychology 7:1444
