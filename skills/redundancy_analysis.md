# Redundancy Analysis Screening Skill (Tier 2)

> See `redundancy.py` docstrings for function descriptions and test cases.
> See `examples/hunt_dataset.py` for the worked example showing
> redundancy alongside spurious correlation screening.

## Purpose

When a paper uses multiple predictor variables, some of those
predictors may be redundant — that is, one predictor can be
accurately predicted from the others. Including redundant predictors
in a model inflates apparent complexity without adding information,
and it distorts both regression coefficients and significance tests.

This skill file tells the LLM how to use `redundancy_analysis()` and
`suggest_removal()` to screen a predictor set for redundancy before
evaluating model results.

The methodology follows Speidel (2018), who applied R's
`Hmisc::redun()` to the Hunt (2013) 21-well geoscience dataset.
The Python implementation uses the same logic: for each predictor,
regress it on all remaining predictors using OLS. If the resulting
R² exceeds a threshold (default 0.90), that predictor is flagged
as redundant — it carries almost no information beyond what the
other predictors already provide.

---

## Key concepts

### Redundancy via OLS R²

For a set of k predictors X1, X2, ..., Xk:

1. For each Xi, fit OLS: Xi ~ X1 + ... + Xi-1 + Xi+1 + ... + Xk
2. Record R²_i — how well the other predictors explain Xi
3. If R²_i > threshold (default 0.90), Xi is redundant

**Intuition:** If 90% of the variance in Xi is already captured by
the other predictors, Xi adds at most 10% new information. Including
it inflates k (the number of variables tested) without proportionally
increasing the information content. This directly connects to
P_spurious: a redundant predictor inflates k, making the
multiple-comparison penalty harsher than it should be.

### Effective k

The number of truly independent predictors after removing redundant
ones. If you start with k=10 predictors and 3 are redundant,
k_eff=7. Use k_eff (not k) when computing P_spurious for a tighter
(less conservative but more honest) estimate of spurious correlation
risk.

Note: `dc_cluster.effective_k()` computes a different version of
this using distance correlation and hierarchical clustering. The
redundancy module uses linear (OLS) relationships; the DC cluster
module captures non-linear dependencies. They complement each other.

### Connection to VIF

Variance Inflation Factor (VIF) is a related diagnostic:
VIF_i = 1 / (1 - R²_i). A VIF above 10 corresponds to R² > 0.90.
The redundancy module uses R² directly because it is more
interpretable and maps directly to the Speidel methodology. Papers
that report VIF can be converted: R² = 1 - 1/VIF.

### Connection to multicollinearity

Redundancy analysis is the predictor-screening complement to
multicollinearity diagnostics. Multicollinearity inflates standard
errors on regression coefficients, making individual predictors
appear non-significant even when the overall model fits well.
Redundancy analysis identifies which specific predictors to remove
before fitting the model. The order matters: screen for redundancy
first, then fit the model, then check residuals and leverage.

---

## Functions

### redundancy_analysis()

**The screening question:** "Which predictors in this set are
redundant — predictable from the others?"
```python
redundancy_analysis(X, threshold=0.90)
# X: pandas DataFrame or 2D numpy array, columns = predictors
# Returns: dict with 'r_squared' (per predictor), 'redundant' (list),
#          'k_original', 'k_effective'
```

Returns a dict with:
- `r_squared` — dict mapping each predictor name to its R² when
  regressed on all others
- `redundant` — list of predictor names with R² > threshold
- `k_original` — total number of predictors
- `k_effective` — k_original minus number of redundant predictors

### suggest_removal()

**The action question:** "Which predictors should I drop, and in
what order?"
```python
suggest_removal(X, threshold=0.90)
# Returns: list of (predictor_name, R²) tuples, sorted by R²
#          descending (most redundant first)
```

Iterative removal: drop the most redundant predictor, recompute R²
for the remaining set, repeat until no predictor exceeds the
threshold. This avoids the problem of removing two predictors that
are redundant with each other but not with the rest.

---

## When to apply this skill

Use this module when a paper:
- Uses multiple predictor variables in regression or correlation
  screening
- Reports selecting "the best" predictors from a larger candidate set
- Tests many seismic attributes, genomic markers, or other
  high-dimensional features against an outcome
- Does not report checking for collinearity or redundancy among
  predictors

**Three questions to ask in order:**

1. How many predictors were used? If k > n/5 (predictors exceed
   one-fifth of observations), redundancy screening is essential.
2. Are any predictors transforms of each other (e.g., log(X1),
   X1², X1/X2)? These are almost certainly redundant by construction.
3. After removing redundant predictors, what is k_eff? Feed k_eff
   into `P_spurious(r, n, k_eff)` for a corrected spurious
   correlation estimate.

**Do not use alone.** Removing redundant predictors is a preprocessing
step. It does not validate the surviving predictors — they still need
domain justification (causal_consistency.md) and individual screening
(spurious_correlation.md).

---

## Worked Example: Hunt (2013) 21-well dataset — Speidel methodology

**Context:** Speidel (2018) applied `Hmisc::redun()` to the Hunt
(2013) dataset as part of a full statistical screening workflow. The
dataset has 21 wells and 4 predictor variables: GrossPay, Porosity,
X_fabricated (log(GrossPay) + noise), and X_random (pure noise).

**Setup:** Before running any correlations with the outcome variable
(production), screen the predictor set for internal redundancy.

### Step 1: Run redundancy_analysis()
```python
import pandas as pd
from bullshit_detector.redundancy import redundancy_analysis

# Hunt dataset predictors (no outcome variable)
data = pd.DataFrame({
    'GrossPay': [...],   # 21 values
    'Porosity': [...],   # 21 values
    'X_fabricated': [...],  # log(GrossPay) + noise
    'X_random': [...]    # pure noise
})

result = redundancy_analysis(data, threshold=0.90)
# result['r_squared']:
#   GrossPay:     ~0.85 (partially predicted by X_fabricated)
#   Porosity:     ~0.12 (independent of others)
#   X_fabricated: ~0.92 (predicted by GrossPay — REDUNDANT)
#   X_random:     ~0.08 (independent — noise is unpredictable)
# result['redundant']: ['X_fabricated']
# result['k_effective']: 3
```

**X_fabricated is flagged as redundant.** Its R² of ~0.92 when
regressed on the other predictors exceeds the 0.90 threshold.
This makes sense: it is log(GrossPay) + small noise, so GrossPay
alone explains most of its variance.

### Step 2: Feed k_eff into P_spurious
```python
from bullshit_detector.spurious import P_spurious

# With all 4 predictors (including redundant one):
print(P_spurious(0.55, 21, 4))   # → ~0.08

# With k_eff = 3 (after removing X_fabricated):
print(P_spurious(0.55, 21, 3))   # → ~0.06
```

The correction is modest here (k=4 vs k_eff=3), but with larger
predictor sets the difference can be dramatic. If k=50 seismic
attributes include 20 redundant ones, k_eff=30 substantially
reduces the P_spurious estimate.

### Step 3: Compare with domain screening

The redundancy module flagged X_fabricated on purely statistical
grounds (high R² with GrossPay). The spurious_correlation.md skill
file's domain check also rejects it (no independent physical
justification). When both statistical redundancy and domain
rejection agree, the verdict is unambiguous.

**Key insight from Speidel's workflow:** Run redundancy screening
BEFORE correlation screening. This prevents inflated k from making
P_spurious overly pessimistic, and it catches constructed variables
(transforms, ratios, interactions) that should not count as
independent predictors.

### Audit pattern

When a paper reports a multi-predictor model:

1. List all predictors. Include any that were screened and dropped
   — the total set matters, not just the final model.
2. Check for obvious transforms: log(X), X², X1/X2, X1*X2. These
   are redundant by construction with their parent variables.
3. If raw data is available, run `redundancy_analysis()` and
   `suggest_removal()`.
4. If raw data is not available, note the predictor count and flag
   any visible transforms. Use domain knowledge to estimate which
   predictors are likely correlated.
5. Report k_eff alongside k in the spurious correlation screening.

---

## Red flags checklist

1. **Predictor count exceeds n/5.** With 21 observations and 10
   predictors, the model is almost certainly overfit. Redundancy
   screening is mandatory.

2. **Transforms included as separate predictors.** log(X), X²,
   normalized X, or ratios of existing predictors counted as
   independent variables. These inflate k without adding information.

3. **No collinearity diagnostics reported.** If the paper does not
   mention VIF, condition number, or any redundancy check, the
   predictor set was not screened. Flag and compute if data is
   available.

4. **"Stepwise selection" used without redundancy pre-screening.**
   Stepwise methods (forward, backward, or bidirectional) are
   sensitive to collinearity. Two correlated predictors may trade
   places across runs without changing model fit. Redundancy
   screening before stepwise selection stabilises the process.

5. **k_eff not reported or discussed.** If the paper tested many
   predictors and reports P_spurious or multiple-comparison
   corrections using the full k, check whether redundancy would
   reduce the effective count.

6. **High R² model with many predictors and small n.** At k/n > 0.2,
   R² is mechanically inflated. Adjusted R² partially corrects this,
   but redundancy among predictors means even adjusted R² can mislead.

---

## Not covered by this skill file

- **Non-linear redundancy.** The OLS R² approach captures only linear
  relationships between predictors. A predictor that is a non-linear
  transform of another (e.g., X² when X spans both positive and
  negative values) may show low R² but high redundancy. Use
  `dc_cluster.effective_k()` for non-linear dependency detection.
- **Temporal redundancy.** Lagged versions of the same variable in
  time-series models are redundant by construction but will not
  necessarily show high R² in a cross-sectional OLS regression.
- **Categorical predictors.** The OLS approach requires continuous
  predictors. Dummy-coded categoricals can produce misleading R²
  values. Use domain judgment for categorical redundancy.
- **Optimal subset selection.** The module flags which predictors to
  remove but does not search for the best subset. Best-subset
  selection is a separate (and computationally expensive) problem.
- **Penalised regression (LASSO, ridge).** These methods handle
  collinearity internally by shrinking coefficients. Redundancy
  screening is still useful as a diagnostic but is not required
  as a preprocessing step when using penalised methods.
- **Feature importance from tree-based models.** Random forests and
  gradient boosting handle correlated predictors differently from
  OLS. Redundancy analysis applies to the predictor set, not to
  any specific model.

---

## References

- Speidel, T. (2018). "GeoConvention 2018: Data Science Tools for
  Petroleum Exploration and Production." R notebook.
- Harrell, F.E. (2001). *Regression Modeling Strategies.* Springer.
  (Source of `Hmisc::redun()` methodology.)
- Hunt, L. et al. (2013). "What's new in geophysical exploration for
  tight oil (Part 2)." *CSEG Recorder*, April 2013.
- Kalkomey, C.T. (1997). "Potential risks when using seismic
  attributes as predictors of reservoir properties." *The Leading
  Edge*, March 1997, pp. 247–251.
