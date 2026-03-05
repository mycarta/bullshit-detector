# Power Analysis Screening Skill (Tier 2)

> See `power.py` docstrings for function descriptions and test cases.
> See `examples/underpowered_study.py` for the Button et al. (2013)
> reproduction. See `examples/hunt_dataset.py` for the Speidel (2018)
> geoscience case.

## Purpose

When a paper reports a "significant" result, the first Tier 2 question
is whether the study was adequately powered to detect the effect it
claims. An underpowered study that finds p < 0.05 is more likely
reporting a false positive than a true effect -- and if the effect is
real, its magnitude is almost certainly inflated (the "winner's curse").

This skill file tells the LLM how to use `achieved_power()` and
`required_n()` to screen papers for power failure, and how to
interpret the results.

---

## Key concepts

### Statistical power

Power is the probability that a study will detect an effect of a given
size, if that effect truly exists. Formally: power = 1 - beta, where
beta is the probability of a Type II error (failing to detect a real
effect).

Power depends on four quantities:
- **Effect size** (Cohen's d, or raw difference / SD)
- **Sample size** (n per group)
- **Significance level** (alpha, usually 0.05)
- **Alternative** (one-sided or two-sided test)

The conventional threshold for adequate power is 0.80 (80% chance of
detecting the effect). Below that, findings should be treated with
increasing caution:

| Power | Interpretation |
|-------|----------------|
| >= 0.80 | Adequate -- standard threshold |
| 0.50-0.80 | Marginal -- findings need caution |
| < 0.50 | Underpowered -- coin flip or worse; significant results likely inflated |
| < 0.20 | Severely underpowered -- most significant findings are false positives |

### Why underpowered significant results are dangerous

This is counterintuitive but critical: a study powered at 20% that
reports p < 0.05 is not a reassuring finding -- it is a suspicious one.

**The logic (Ioannidis 2005, Button et al. 2013):**

Suppose a field has a 10% base rate of true effects (R = 1:9 prior
odds). With power = 0.20 and alpha = 0.05:

- Out of 1000 hypotheses tested: 100 are true, 900 are false
- True positives: 100 x 0.20 = 20
- False positives: 900 x 0.05 = 45
- Positive predictive value: 20 / (20 + 45) = 31%

**69% of significant findings are false.** Higher power shifts this:
at 80% power, PPV rises to 64%. The lower the power, the less you
should trust a significant result.

### The winner's curse

Underpowered studies that do find significance tend to overestimate
the true effect size. The reason: to clear the significance threshold
with small n, you need a lucky sample where the observed effect
happened to be large. The published effect size is biased upward.

This matters for replication: the next study, run at the inflated
effect size estimate, will be even more underpowered than it appears
and will likely fail to replicate.

### Cohen's d

The standardised mean difference between two groups:

```
d = (mean_1 - mean_2) / SD_pooled
```

Cohen's conventions: d = 0.2 (small), d = 0.5 (medium), d = 0.8 (large).

These conventions are rough guides, not thresholds. What counts as
"small" depends on the domain. In some fields, d = 0.2 is clinically
important; in others, d = 0.8 is noise.

When a paper reports raw means, SDs, and group sizes but not Cohen's d,
compute it. The `power.py` functions accept either Cohen's d directly
(`effect_size` parameter) or raw difference with SDs (`d` + `sd` or
`sd1`/`sd2` parameters).

---

## Functions

### achieved_power()

**The screening question:** "Given the reported effect size and sample
size, how powered was this study?"

```python
achieved_power(effect_size=0.5, n_per_group=16, alpha=0.05)
# -> {"power": 0.293, "adequate": False, ...}
```

Returns a dict with `power` (0 to 1), `adequate` (bool), and
`interpretation` (qualitative string).

**Input options:**
- `effect_size` -- Cohen's d directly
- `d` + `sd` -- raw mean difference with pooled SD
- `d` + `sd1` + `sd2` -- raw difference with group-specific SDs
  (Welch's approach, as in Speidel 2018)
- `n_per_group` or `n_total` -- sample size

### required_n()

**The planning question:** "How many observations per group would this
study have needed for 80% power?"

```python
required_n(effect_size=0.5, alpha=0.05, power=0.80)
# -> {"n_per_group": 64, "n_total": 128, ...}
```

The gap between required_n and actual n is the "power deficit" -- a
direct measure of how under-resourced the study was.

---

## When to apply this skill

Use this module when a paper:
- Reports a "significant" result from small to moderate samples
- Claims a specific effect size (Cohen's d, odds ratio, mean difference)
- Reports means, SDs, and group sizes (from which d can be computed)
- Makes clinical or policy recommendations based on the finding

**Three questions to ask in order:**

1. What is the achieved power for the claimed effect size and actual n?
   If power < 0.50, the finding is suspect regardless of p-value.
2. What n would have been needed for 80% power? If the required n is
   3x or more the actual n, the study was substantially under-resourced.
3. Is the effect size plausible, or is it inflated by the winner's
   curse? Compare to meta-analytic estimates if available.

---

## Worked Example 1: Button et al. (2013) -- neuroscience power failure

**Context:** Button et al. (2013) analysed 730 studies from 41
meta-analyses across 8 domains of neuroscience and estimated that the
median statistical power was approximately 21%. This paper is one of
the foundational documents of the replication crisis.

**Setup:** A typical small neuroimaging study: n=16 per group, claiming
a medium effect (Cohen's d=0.5), alpha=0.05 two-sided.

### Screening with achieved_power()

```python
from bullshit_detector.power import achieved_power, required_n

result = achieved_power(effect_size=0.5, n_per_group=16, alpha=0.05)
# -> power = 0.293, adequate = False
```

**Power = 29.3%.** This study has less than a 1-in-3 chance of
detecting its own claimed effect. If it reports p < 0.05, the
positive predictive value is low -- most such findings will be false
positives or inflated true positives.

### How many participants were actually needed?

```python
result = required_n(effect_size=0.5, alpha=0.05, power=0.80)
# -> n_per_group = 64, n_total = 128
```

**64 per group (128 total).** The typical neuroimaging study recruited
about 16 per group -- 4x too small. This is the power deficit: the
gap between what was needed and what was done.

### Power across the effect size spectrum

At n=20 per group (slightly above the neuroimaging norm), power
varies dramatically by effect size:

| Effect size | d | Power at n=20 | n needed for 80% | Verdict |
|-------------|-----|--------------|-------------------|---------|
| Small | 0.2 | ~9% | ~394/group | UNDERPOWERED |
| Small+ | 0.3 | ~14% | ~176/group | UNDERPOWERED |
| Medium | 0.5 | ~34% | ~64/group | UNDERPOWERED |
| Large | 0.8 | ~69% | ~26/group | Marginal |

At n=20, only large effects (d=0.8) have even marginal power. Small
to medium effects -- the norm in psychology and neuroscience -- are
essentially undetectable. Studies this small that report finding small
effects are almost certainly reporting noise.

### Audit pattern

When screening a paper for power:

1. Extract effect size and sample size. If only means and SDs are
   reported, compute d.
2. Call `achieved_power()` with those values.
3. If power < 0.50, flag: "Less than a coin-flip chance of detecting
   its claimed effect. Significant result should be interpreted with
   skepticism."
4. If power < 0.80, note: "Below conventional threshold. Interpret
   with caution."
5. Call `required_n()` to quantify the gap.
6. Check whether the reported effect size is plausible -- if much
   larger than meta-analytic estimates, suspect winner's curse.

---

## Worked Example 2: Speidel (2018) -- geoscience field study

**Context:** Speidel (2018) applied power analysis to the Hunt (2013)
21-well geoscience dataset to determine whether the sample was
adequate to detect production differences between geological zones.

**Setup:** Two production zones with estimated mean difference d=16,
sd1=16, sd2=12 (unequal variances), alpha=0.10 (relaxed for
exploration stage).

### Required n with unequal variances

```python
from bullshit_detector.power import required_n

result = required_n(d=16, sd1=16, sd2=12, alpha=0.10, power=0.80)
# -> n_per_group = 11, n_total = 22
```

**11 per group (22 total).** The Hunt dataset has 21 wells -- right at
the threshold. Whether the study is adequately powered depends
sensitively on the assumed effect size and variance.

### Why a range matters more than a point estimate

Speidel's key insight: solve for a range of plausible values, not a
single point. If the true difference is 12 instead of 16 (25% smaller),
the required n jumps. If sd1 is 20 instead of 16, the required n
jumps again.

Power analysis on a single assumed effect size gives a false sense of
precision. The right question is: "Over the range of plausible effect
sizes, is this study adequate?" If adequate only at the optimistic end,
it is probably underpowered for the true effect.

### Geoscience-specific considerations

- Well data is expensive. A 21-well study may be all that exists.
  Power analysis calibrates confidence, not validity.
- The alpha=0.10 choice reflects exploration-stage risk tolerance
  (missing a prospect costs more than drilling a dry hole). Defensible
  but must be stated explicitly.
- Effect sizes are often estimated from analogues (nearby fields,
  similar geology). Analogue quality determines power estimate quality.

---

## Worked Example 3: the SD-vs-SE trap

**Context:** From `examples/sd_vs_se.py`. A sports science paper
reports group means and "error bars" without clearly labelling whether
the bars show standard deviation or standard error. Confusing the two
changes the apparent effect size dramatically.

**Setup:** Two groups, mean difference = 12 units. Reported "spread"
= 6 units per group. n = 30 per group.

**If the reported spread is SD:**

```python
achieved_power(d=12, sd=6, n_per_group=30)
# d_cohen = 12/6 = 2.0 -> power = 1.00
```

Cohen's d = 2.0 (enormous). Zero overlap between groups. This should
trigger a Fermi sanity alarm -- a d of 2.0 means the groups do not
overlap at all, which is extremely rare in biological data.

**If the reported spread is SE (and SD = SE x sqrt(n)):**

```python
import math
sd_corrected = 6 * math.sqrt(30)  # = 32.9
achieved_power(d=12, sd=sd_corrected, n_per_group=30)
# d_cohen = 12/32.9 = 0.36 -> power = 0.25
```

Cohen's d drops to 0.36 -- small-to-medium effect with only 25% power.

**Lesson:** Always check whether a paper reports SD or SE. They are
related by SE = SD / sqrt(n). Confusing them inflates the apparent
effect size by a factor of sqrt(n). At n=30, that is 5.5x inflation.
An implausibly large d (>1.5 in biological contexts) is a signal to
check the units.

---

## Red flags checklist

1. **No power analysis reported.** Compute it yourself from the
   reported n and effect size.

2. **Post-hoc power analysis.** "Observed power" after the study is
   circular -- a 1-to-1 function of the p-value. Flag if used to
   justify non-significant results.

3. **n < 20 per group with significant results.** At n=20, only large
   effects (d>=0.8) have adequate power. Smaller effects reported as
   significant from n<20 are suspect.

4. **Claimed effect size much larger than meta-analytic estimate.**
   Winner's curse: first significant study in underpowered literature
   will overestimate the effect.

5. **Pilot study used for hypothesis confirmation.** Pilot studies
   (n<15) are powered to detect only enormous effects. They should
   inform sample size planning, not serve as evidence.

6. **SD vs. SE ambiguity.** Implausibly large d (>1.5 in bio/behavioral
   research) -- check whether denominator used SD or SE.

7. **Unequal group sizes not acknowledged.** If n1 != n2, power is
   determined by the smaller group. n1=100, n2=10 has the power of
   roughly n=10.

---

## Not covered by this skill file

- **Non-parametric tests.** Power formulas assume normal distributions
  and two-group comparisons. Wilcoxon, chi-square, etc. require
  different formulas or simulation.
- **Regression power.** Power for detecting a significant predictor in
  multiple regression depends on R-squared increment, number of
  predictors, and total n. Not implemented.
- **Cluster-randomised trials.** Effective sample size is the number of
  clusters, not individuals. Ignoring the design effect can inflate
  apparent power by 10x or more.
- **Sequential / adaptive designs.** Interim analyses and stopping rules
  change power characteristics.
- **Bayesian power / assurance.** Not addressed here.
- **Multi-arm trials.** Multiple treatment arms require correction for
  multiple comparisons, changing effective alpha.

---

## References

- Button, K.S., Ioannidis, J.P.A., Mokrysz, C., et al. (2013).
  "Power failure: why small sample size undermines the reliability of
  neuroscience." *Nature Reviews Neuroscience*, 14(5), 365-376.
- Ioannidis, J.P.A. (2005). "Why most published research findings
  are false." *PLoS Medicine*, 2(8), e124.
- Cohen, J. (1988). *Statistical Power Analysis for the Behavioral
  Sciences* (2nd ed.). Lawrence Erlbaum Associates.
- Speidel, T. (2018). "GeoConvention 2018: Data Science Tools for
  Petroleum Exploration and Production." R notebook.
- Hunt, L. et al. (2013). "What's new in geophysical exploration for
  tight oil (Part 2)." *CSEG Recorder*, April 2013.
