# Reproducibility Challenge Screening Skill (Tier 3)

> See `reproducibility.py` docstrings for function descriptions and
> test cases. Based on Notebooks D and E from the "Be a geoscience
> detective" project (Niccoli, 2021; TRANSFORM 2021 lightning talk).

## Purpose

When a paper reports trends, relationships, or predictive models,
the Tier 3 reproducibility check asks: "If I tried to reproduce the
key claim from the reported data, would I get the same answer?" This
is not a full replication (which would require new data) — it is a
computational reproducibility check using the numbers the paper
itself provides.

This skill file tells the LLM how to use `error_flag()` and
`bootstrap_proportion()` to detect inconsistencies between reported
data and reported conclusions, and to quantify the uncertainty in
proportional claims.

The methodology comes from the "Be a geoscience detective" project
(Sainani, 2020 → Niccoli, 2021): given a paper's reported data
points, check whether the claimed trend direction, magnitude, or
proportion holds up under resampling and sign analysis.

---

## Key concepts

### Error flagging via sign analysis

The simplest reproducibility check: does the direction of the
claimed trend match the data?

Given a sequence of values (e.g., yearly measurements, dose-response
points, time-series observations), compute the first differences
(consecutive changes) and check whether the signs match the claimed
pattern.

**Example:** A paper claims "production increased monotonically over
the study period." If the reported annual values are
[100, 105, 103, 110, 108], the first differences are
[+5, -2, +7, -2]. Two of four differences are negative — the claim
of monotonic increase is falsified by the paper's own data.

This is trivial arithmetic, but it catches a surprisingly common
failure: authors state a trend in the Discussion that is contradicted
by the data in their own Table 2.

### Bootstrap proportion confidence intervals

When a paper reports a proportion (e.g., "73% of studies were
underpowered," "85% of wells showed improvement"), the uncertainty
in that proportion depends on the sample size. A claim of "85%
success rate" from n=20 has a much wider confidence interval than
the same claim from n=200.

`bootstrap_proportion()` resamples the binary outcomes (success/fail)
with replacement and computes a percentile confidence interval for
the true proportion. This directly quantifies how much the reported
percentage should be trusted.

**Connection to Fermi sanity:** If a paper claims "most" of something
without quantifying uncertainty, the bootstrap CI makes the
uncertainty explicit. A proportion of 0.73 from n=30 has a 95% CI
of roughly (0.55, 0.87) — the true value might be barely above
half.

### Condition functions

`error_flag()` accepts a user-defined condition function that
specifies what constitutes an "error" or "inconsistency" in the
data. This makes the check flexible:

- Monotonic increase: `condition_fn = lambda x: np.all(np.diff(x) > 0)`
- All values positive: `condition_fn = lambda x: np.all(x > 0)`
- Slope sign matches claim: `condition_fn = lambda x: np.polyfit(range(len(x)), x, 1)[0] > 0`

The condition function returns True if the data is consistent with
the claim and False if it is not. This lets the same machinery
handle diverse reproducibility checks without hardcoding specific
tests.

---

## Functions

### error_flag()

**The screening question:** "Does the reported data match the
claimed trend or pattern?"
```python
error_flag(values, condition_fn, description="")
# values: array-like of reported data points
# condition_fn: callable, returns True if data matches claim
# description: string label for the check being performed
# Returns: dict with 'consistent' (bool), 'details' (string),
#          'first_differences' (array), 'signs' (array)
```

Returns a dict with:
- `consistent` — True if condition_fn(values) returns True
- `details` — human-readable explanation of the check result
- `first_differences` — the consecutive differences in values
- `signs` — the signs of those differences (+1, -1, or 0)

### bootstrap_proportion()

**The uncertainty question:** "How much should I trust this reported
proportion?"
```python
bootstrap_proportion(successes, n, n_bootstrap=10000,
                     confidence=0.95, seed=None)
# successes: number of successes (int) or boolean array
# n: total number of observations
# n_bootstrap: number of bootstrap resamples
# confidence: confidence level for the interval
# Returns: dict with 'proportion', 'ci_lower', 'ci_upper',
#          'n', 'confidence'
```

Returns a dict with:
- `proportion` — observed proportion (successes / n)
- `ci_lower`, `ci_upper` — percentile bootstrap confidence interval
- `n` — sample size
- `confidence` — confidence level used

---

## When to apply this skill

Use this module when a paper:
- Reports a trend (increasing, decreasing, monotonic) that can be
  checked against the reported data points
- Claims a proportion or percentage from a countable sample
- Presents data in tables or figures from which values can be
  extracted and the claimed pattern verified
- Reports a before/after comparison where the direction of change
  matters

**Three questions to ask in order:**

1. Can the claimed trend be checked against the reported data? If
   the paper says "X increased over time" and reports the time-series
   values, run `error_flag()` to verify the signs.
2. Is the reported proportion based on a small enough sample that the
   CI matters? If n < 100, the bootstrap CI will likely be wide
   enough to challenge the headline claim.
3. Does the paper acknowledge the uncertainty in its proportional
   claims, or does it state percentages as if they were exact?

**Requires data extraction.** Unlike Tier 0-2 modules that can work
from reported summary statistics (means, SDs, p-values, correlation
coefficients), the reproducibility module needs the actual data
points — from tables, figures, or supplementary material. If the
data is not available, note this as a limitation and flag that the
claim cannot be independently verified.

---

## Worked Example 1: Monotonic trend claim — production data

**Context:** A geoscience paper claims "Production in Zone A showed
a consistent upward trend over the 2015-2020 period." The paper's
Table 3 reports annual production values.

**Setup:** Extracted values from Table 3:
[1200, 1350, 1280, 1420, 1510, 1480] (barrels/day, 2015-2020)

### Step 1: Check the monotonicity claim
```python
import numpy as np
from bullshit_detector.reproducibility import error_flag

values = [1200, 1350, 1280, 1420, 1510, 1480]

result = error_flag(
    values,
    condition_fn=lambda x: np.all(np.diff(x) > 0),
    description="Monotonic increase in production"
)
# result['consistent']: False
# result['first_differences']: [150, -70, 140, 90, -30]
# result['signs']: [1, -1, 1, 1, -1]
```

**Two negative differences** (2016→2017: -70, 2019→2020: -30). The
claim of "consistent upward trend" is contradicted by the paper's
own data. The overall trend is upward (net change +280), but
"consistent" implies monotonic, and the data is not monotonic.

### Step 2: Check the weaker claim (overall positive slope)
```python
result_slope = error_flag(
    values,
    condition_fn=lambda x: np.polyfit(range(len(x)), x, 1)[0] > 0,
    description="Overall positive slope"
)
# result_slope['consistent']: True
```

The overall slope is positive. The paper's claim would be accurate
as "generally upward" but is overstated as "consistent."

### Audit pattern

1. Extract the specific language of the claim. "Consistent,"
   "monotonic," "steady" imply no reversals. "Generally," "overall,"
   "on average" permit fluctuations.
2. Extract the data points from the table or figure.
3. Run `error_flag()` with a condition function matching the
   strength of the claim.
4. If the strong claim fails but the weak claim passes, note the
   overstatement — this is a precision-of-language issue, not
   necessarily fraud.

---

## Worked Example 2: Proportion claim — Archer et al. (2023)

**Context:** Archer et al. (2023) reported that 73% of clinical
prediction model studies were below the minimum sample size
recommended by Riley et al. (2019). This is a proportion claim
from a countable sample.

**Setup:** Suppose 168 of 230 studies were below the threshold.

### Step 1: Compute the bootstrap CI
```python
from bullshit_detector.reproducibility import bootstrap_proportion

result = bootstrap_proportion(
    successes=168, n=230, confidence=0.95, seed=42
)
# result['proportion']: 0.730
# result['ci_lower']: ~0.672
# result['ci_upper']: ~0.786
```

**95% CI: (0.67, 0.79).** The point estimate of 73% is well-supported
— even the lower bound shows two-thirds of studies are underpowered.
This is a case where the bootstrap CI reinforces the claim rather
than undermining it.

### Step 2: Compare with smaller sample

If the same proportion (73%) came from n=30:
```python
result_small = bootstrap_proportion(
    successes=22, n=30, confidence=0.95, seed=42
)
# result_small['proportion']: 0.733
# result_small['ci_lower']: ~0.557
# result_small['ci_upper']: ~0.887
```

**95% CI: (0.56, 0.89).** Now the true proportion could plausibly be
as low as 56% or as high as 89%. The headline "73%" is much less
informative at this sample size.

### Audit pattern

1. Extract the reported count and total (successes/n).
2. Run `bootstrap_proportion()` to get the CI.
3. If the CI is narrow relative to the claim, the claim is
   well-supported.
4. If the CI is wide (e.g., spans more than 20 percentage points),
   the claim overstates the precision of the evidence.
5. Note whether the paper reports any uncertainty around its
   proportion. Many do not.

---

## Red flags checklist

1. **Trend claim contradicted by own data.** Paper says "increased"
   but table shows decreases in some intervals. Run `error_flag()`
   with the relevant condition function.

2. **Percentage claim from small n without CI.** "85% of patients
   improved" from n=20 has a CI of roughly (0.64, 0.96). The
   headline number hides enormous uncertainty.

3. **"All" or "none" claims from finite samples.** "All wells showed
   improvement" from n=12 has a bootstrap lower bound for the true
   proportion well below 1.0.

4. **Inconsistency between text and tables.** The abstract says
   "decreased by 30%" but the table shows a 22% decrease. This is
   the most common reproducibility failure: rounding, transcription
   errors, or selective reporting of the most impressive comparison.

5. **Figures that contradict text.** Visual inspection of a figure
   shows a flat or noisy relationship, but the text describes it as
   "clear" or "strong." Extract data points from the figure if
   possible and run the checks.

6. **No raw data available.** If only summary statistics are reported
   and the original data cannot be obtained, note this as a
   reproducibility limitation. The claim cannot be independently
   verified.

---

## Not covered by this skill file

- **Full replication.** This module checks computational
  reproducibility (do the reported numbers support the reported
  conclusions?). It does not address replicability (would a new
  study find the same result?).
- **Code reproducibility.** Whether the authors' analysis code runs
  and produces the stated outputs. This requires access to the code
  and data, not just the paper.
- **Figure data extraction.** The module assumes data points are
  available (from tables or supplementary material). Extracting data
  from rasterised figures requires additional tools (e.g.,
  WebPlotDigitizer) not included in this package.
- **Multi-step reproducibility.** Checking whether intermediate
  results (e.g., model coefficients in Table 4) are consistent with
  the raw data in Table 1 requires re-running the full analysis
  pipeline, not just sign checks and bootstrap CIs.
- **Bayesian proportion estimation.** The bootstrap approach is
  frequentist. A Beta-binomial model would give a posterior interval
  that may differ slightly, especially for extreme proportions or
  very small n.
- **Systematic review reproducibility.** Checking whether a
  systematic review's search strategy, inclusion criteria, and data
  extraction are reproducible requires domain-specific methodology
  (PRISMA, etc.) beyond this module's scope.

---

## References

- Sainani, K. (2020). "How to Read a Paper: Statistics for the
  Non-Statistician." Stanford University. (Intellectual foundation
  for the "detective" approach.)
- Niccoli, M. (2021). "Be a geoscience and data science detective."
  TRANSFORM 2021 lightning talk, MyCarta blog, GitHub repository.
  (Source for Notebooks D and E; the error_flag and bootstrap
  methodology.)
- Archer, L., et al. (2023). "Underpowered clinical prediction
  models." (Proportion claim example.)
- Riley, R.D., et al. (2019). "Minimum sample size for developing
  a multivariable prediction model." *Statistics in Medicine*.
- Efron, B. & Tibshirani, R.J. (1993). *An Introduction to the
  Bootstrap.* Chapman & Hall.
