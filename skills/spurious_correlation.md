# Spurious Correlation Screening Skill (Tier 2)

> See `spurious.py` docstrings for function descriptions and test cases.
> See `examples/kalkomey_screening.py` for reproduction of Kalkomey (1997)
> Tables 1 and 3. See `examples/hunt_dataset.py` for the synthetic
> geoscience case study.

## Purpose

When a paper reports a correlation between two variables, the finding
may be real or it may be an artefact of small samples and multiple
comparisons. This skill file tells the LLM how to estimate the
probability that a reported correlation is spurious — that is,
that the observed r could appear by chance when the true correlation
is zero.

The core formula is from Kalkomey (1997), who showed that the
probability of obtaining at least one spurious correlation above a
critical threshold rises rapidly when multiple variables are tested
against a small number of observations. This is the single most
important result in the package: it quantifies the multiple-comparison
trap without requiring access to raw data.

---

## Key concepts

### The Kalkomey formula: P_spurious

Given:
- **n** — number of observations (wells, participants, samples)
- **k** — number of predictor variables tested
- **r** — the reported correlation coefficient

The probability that at least one of k independent variables produces
a spurious correlation ≥ |r| with n observations is:

```
P_spurious(r, n, k) = 1 - [P(|ρ| < |r| | n, ρ=0)]^k
```

where `P(|ρ| < |r| | n, ρ=0)` is the probability that a single
correlation from n observations falls below |r| when the true
correlation is zero. This comes from the t-distribution with df = n−2.

**Intuition:** Each variable is an independent lottery ticket. The
chance of losing every ticket is `(1−p)^k`. The chance of winning
at least once is `1 − (1−p)^k`. With enough tickets (variables),
you almost certainly "win" — even though each individual result
is "statistically significant."

### Critical correlation: r_crit

For a given n and significance level α, the minimum |r| that would
be declared significant:

```
r_crit(n, alpha=0.025)  → two-tailed 5% threshold
```

This is the threshold below which individual correlations fail a
standard t-test. But a result above r_crit is not safe — it may
still be spurious if many variables were tested.

Key values from the code:
- n=21 wells: r_crit ≈ 0.433
- n=5 wells: r_crit ≈ 0.878 (need very high r with few samples)
- n=100: r_crit ≈ 0.197 (even weak correlations pass with large n)

### Confidence interval: conf_int

Fisher Z-transform confidence interval for the population correlation:

```
conf_int(r, n, confidence=0.95)
```

Detection heuristic: if the CI crosses zero, the correlation is not
significantly different from zero at the stated confidence level.
Even strong-looking correlations may have extremely wide CIs with
small n:
- r=0.73, n=9: CI ≈ (0.13, 0.94) — nearly useless
- r=0.90, n=8 (after outlier removal): CI ≈ (0.53, 0.98)

### Prediction intervals vs. confidence intervals

A confidence interval for r tells you the uncertainty in the
correlation coefficient itself. A prediction interval tells you
where a new observation would fall. Papers that report only CIs
around a regression line hide the true scatter. If a paper shows
a tight-looking regression with no prediction bands, ask why.

---

## When to apply this skill

Use this module when a paper:
- Reports correlation(s) between variables from a small to moderate
  sample
- Tests multiple predictor variables against a single outcome
- Claims a "significant" correlation without adjusting for multiple
  comparisons
- Reports r (or R²) as evidence of a relationship

**Three questions to ask in order:**

1. Is |r| above r_crit for this n? If not, stop — the result is
   not even individually significant.
2. What is P_spurious(r, n, k) where k is the total number of
   variables tested (not just the ones reported)? If P_spurious
   > 0.10, the result is suspect.
3. Does the confidence interval for r cross zero? If yes, the
   result cannot be distinguished from independence.

**Do not use alone.** A low P_spurious does not prove the
relationship is real — it only means chance is unlikely to explain
it. Domain plausibility (causal_consistency.md) and model
diagnostics (outlier_leverage.md) are still needed.

---

## Worked Example 1: Kalkomey (1997) — the multi-attribute trap

**Context:** Kalkomey (1997) showed that in geoscience, the practice
of screening many seismic attributes against a well property
(porosity, permeability, etc.) is statistically dangerous. Even when
no true relationship exists, the probability of finding at least one
"significant" correlation approaches certainty as the number of
attributes grows.

**Setup:** 21 wells (n=21), testing k seismic attributes against a
reservoir property. True correlation is zero for all attributes.

### Table 1 — P(spurious) for a single attribute (k=1)

With k=1 (only one variable tested), P_spurious equals the standard
two-tailed p-value:

| n | r=0.3 | r=0.5 | r=0.6 | r=0.7 | r=0.8 |
|---|-------|-------|-------|-------|-------|
| 5 | 0.624 | 0.391 | 0.285 | 0.188 | 0.104 |
| 10 | 0.400 | 0.141 | 0.067 | 0.024 | 0.005 |
| 15 | 0.277 | 0.058 | 0.019 | 0.004 | <0.001 |
| 21 | 0.187 | 0.021 | 0.004 | <0.001 | <0.001 |
| 50 | 0.034 | <0.001 | <0.001 | <0.001 | <0.001 |

**Reading:** At n=21, a single r=0.50 has only a 2.1% chance of
being spurious — looks safe. But this is for k=1 only.

### The escalation: what happens with multiple attributes

This is where the Kalkomey insight bites. Same n=21, same r=0.50,
but now k varies:

| k tested | P(spurious) at r=0.50 |
|----------|----------------------|
| 1 | 0.021 |
| 5 | 0.100 |
| 10 | 0.191 |
| 20 | 0.346 |
| 50 | 0.658 |
| 100 | 0.883 |

At k=100, there is an 88% chance that the best r=0.50 result is
entirely spurious. And 100 attributes is not unusual in modern
seismic interpretation or genomics.

### Table 3 — expected best spurious r by k

As you test more attributes, the best-looking spurious correlation
gets progressively higher:

| k tested | Best spurious r (expected), n=21 |
|----------|--------------------------------|
| 1 | ~0.43 (at significance threshold) |
| 10 | ~0.62 |
| 50 | ~0.72 |
| 100 | ~0.77 |
| 500 | ~0.85 |

At k=500, you expect to find a completely spurious r of 0.85 — an
R² of 0.72. Most reviewers would find this convincing. It is pure
noise.

### Audit pattern

When a paper reports a single "best" correlation from a
multi-attribute screening:

1. **Ask: how many attributes were screened?** If the paper doesn't
   say, flag it. This is essential information.
2. Call `P_spurious(r, n, k)` with the total k (not just the
   reported winners).
3. If P_spurious > 0.10, the result is suspect.
4. If the paper reports only the winning attribute(s) and not the
   total number tested, note that the effective k may be much larger
   than what appears in the paper.
5. Feed k into the redundancy module: `redundancy.redundancy_analysis()`
   computes the effective number of independent predictors. If k_eff
   < k because predictors are correlated, use k_eff in P_spurious for
   a tighter (less conservative) estimate.

**Code:**

```python
from bullshit_detector.spurious import P_spurious, r_crit

# Kalkomey Table 1 replication
print(P_spurious(0.50, 21, 100))  # → ~0.88
print(P_spurious(0.60, 21, 100))  # → ~0.33

# Critical r for 21 wells
print(r_crit(21))  # → ~0.433
```

---

## Worked Example 2: Hunt dataset — statistics pass, domain fails

**Context:** This example uses a synthetic 21-well geoscience dataset
(modelled on Hunt 2013) to demonstrate why statistical screening is
necessary but not sufficient. The key lesson: a fabricated variable
can pass every statistical test yet must be rejected because it has
no independent physical justification.

**Setup:** 21 wells, 4 predictor variables tested against production:
- GrossPay — physically justified (Darcy's Law: flow ∝ thickness)
- Porosity — physically justified (pore volume drives storage)
- X_fabricated — log(GrossPay) + small noise. High correlation with
  production, but it is just a non-linear transform of GrossPay, not
  an independent attribute.
- X_random — pure noise, no relationship.

**Decision table (from `examples/hunt_dataset.py`):**

| Predictor | r | P(spur, k=4) | r > r_crit | CI ∋ 0? | Domain OK? | Verdict |
|-----------|------|-------------|-----------|---------|-----------|---------|
| GrossPay | ~0.88 | low | yes | no | yes | **KEEP** |
| Porosity | ~0.55 | moderate | yes | no | yes | KEEP |
| X_fabricated | ~0.85 | low | yes | no | **no** | **REJECT (domain)** |
| X_random | ~0.05 | high | no | yes | no | REJECT (stat) |

**The critical case is X_fabricated.** It passes every statistical
check: r is well above r_crit, P_spurious is low even at k=4, and
the confidence interval is tight and excludes zero. If statistics
were the only filter, X_fabricated would be accepted.

It must be rejected because:
- It is a transform of GrossPay, not an independent measurement
- Using it alongside GrossPay double-counts the same geological
  information
- The "domain justification" for X_fabricated would be post-hoc
  rationalisation

**Verdict: REJECT on domain grounds, despite statistical PASS.**

**Lesson:** P_spurious answers "could chance explain this result?"
It does not answer "is this relationship real?" Low P_spurious means
you need a non-chance explanation — but the explanation must come
from domain knowledge. This is why causal_consistency.md (Mill's
Methods) and the redundancy module exist as separate checks.

**This is the Kalkomey trap made explicit.** In real papers, the
fabrication is rarely deliberate — it is more often an attribute
selected from hundreds of candidates, where the "domain
justification" is post-hoc narrative fitted to the winning variable.

---

## Red flags checklist

When reading a paper that reports correlations, scan for these:

1. **Missing k.** The paper reports the best correlation(s) but not
   how many variables were tested. Without k, you cannot compute
   P_spurious. Flag and ask.

2. **r just above significance.** A result with r barely above r_crit
   and moderate k is likely spurious. Run P_spurious to quantify.

3. **Multiple "significant" results all near threshold.** If a paper
   reports five correlations at r=0.44–0.48 from n=21, these are all
   just above r_crit≈0.43 and likely spurious given any reasonable k.

4. **No confidence intervals reported.** Without CIs, you cannot see
   the uncertainty in r. A paper reporting r=0.70 from n=9 without
   noting the CI spans (0.07, 0.94) is hiding the uncertainty.

5. **R² without r.** Some papers report only R² (e.g., "our model
   explains 64% of variance"). Convert: r = √R² = 0.80. Then run
   the checks.

6. **"Best attribute" narrative.** The paper screened many attributes,
   found the winner, and tells a story about why that attribute
   makes physical sense. The story was constructed after the
   screening. This is the Kalkomey trap.

7. **Prediction intervals missing.** Only confidence bands around
   the regression line are shown. Prediction bands would show how
   uncertain individual predictions are. Their absence flatters the
   model.

---

## Not covered by this skill file

- **Non-linear correlations.** P_spurious assumes Pearson r.
  Non-linear relationships (which may show low r but strong
  association) require distance correlation
  (`leverage.distance_correlation_test()`).
- **Time-series correlations.** Autocorrelated data inflate
  effective sample size and produce spuriously significant
  correlations. Requires specialised handling not in this module.
- **Partial correlations.** When confounders are present, the
  bivariate r may be misleading. The causal_consistency.md skill
  (Mill's Method of Residues) addresses this conceptually.
- **Within-subject correlations.** Repeated measures on the same
  units violate the independence assumption that P_spurious
  requires.
- **Effect of non-normal data on r.** Outliers can inflate or
  deflate Pearson r. See outlier_leverage.md for diagnostics.
- **Correction for multiple comparisons.** P_spurious quantifies
  the risk but does not adjust p-values (no Bonferroni, FDR, etc.).
  It is a detection tool, not a correction tool.

---

## References

- Kalkomey, C.T. (1997). "Potential risks when using seismic
  attributes as predictors of reservoir properties." *The Leading
  Edge*, March 1997, pp. 247–251.
- Hunt, L. et al. (2013). "What's new in geophysical exploration for
  tight oil (Part 2)." *CSEG Recorder*, April 2013.
- Speidel, T. (2018). "GeoConvention 2018: Data Science Tools for
  Petroleum Exploration and Production." R notebook.
- Fisher, R.A. (1921). "On the 'probable error' of a coefficient of
  correlation deduced from a small sample." *Metron*, 1, 3–32.
- Niccoli, M. (2026). "Visual data exploration in Python — correlation,
  confidence, spuriousness." MyCarta blog.
