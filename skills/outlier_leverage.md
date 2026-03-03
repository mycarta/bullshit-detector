# Outlier, Leverage & Regression Diagnostics Skill (Tier 3)

> See leverage.py and dc_cluster.py docstrings for function descriptions.
> See Session_Handoff_05.md for implementation notes and source references.

## Purpose

When a paper reports regression results (linear, logistic, Cox, etc.),
the numbers only mean what they claim if the model assumptions hold.
Most papers never show diagnostic evidence. This skill file tells the
LLM what to look for and what to flag when it's missing.

The canonical illustration is Davis (1986), *Statistical Methods in the
Earth Sciences*, Figure 6.2: linear regression assumes (1) a linear
relationship, (2) normally distributed residuals, (3) constant variance
(homoscedasticity), and (4) zero-mean disturbances. When any of these
fail, the regression line, r², p-values, and confidence intervals are
all unreliable.

## Regression assumption audit checklist

### 1. Linearity

**The assumption:** The relationship between X and Y is linear (or the
specified functional form is correct).

**What to look for in the paper:**
- Did the authors show a scatterplot of X vs. Y? If not, why not?
- Did they report fitting alternatives (quadratic, log-transform, GAM,
  LOESS) and showing that linear was adequate?
- Is the claimed linear range physically plausible? Some relationships
  are inherently nonlinear (e.g., dose-response curves, permeability
  vs. porosity in geoscience, enzyme kinetics).

**Red flags:**
- High r² reported without any scatterplot shown. The fit could be
  driven by a few extreme points with a nonlinear cloud in between.
- Residual-vs-fitted plot not shown. A U-shaped or curved pattern in
  residuals is the clearest linearity violation signal.
- Data transformed to "achieve linearity" (e.g., log-log) without
  justification from the underlying physics or biology.
- Authors report r² for a clearly bounded variable (proportions,
  percentages, saturating processes). Linear extrapolation beyond
  bounds is guaranteed to fail.

**Connection to other modules:**
- `causal_consistency.md` Check 5 (Concomitant Variation): asks whether
  dose-response holds across the full range. A nonlinear relationship
  reported as linear is a form of Concomitant Variation failure —
  the "dose-response" holds only in the cherry-picked subrange.
- `spurious.conf_int()`: confidence intervals assume linearity. If the
  relationship is nonlinear, the CI is wrong even if it doesn't cross
  zero.

### 2. Normality of residuals

**The assumption:** The disturbance terms (residuals) are normally
distributed around the regression line.

**What to look for in the paper:**
- Q-Q plot of residuals? Histogram of residuals?
- Shapiro-Wilk or Kolmogorov-Smirnov test reported?
- For small n, normality tests have low power — visual diagnostics
  (Q-Q plot) are more informative than formal tests.

**Red flags:**
- No residual distribution shown at all. This is the most common
  omission in published research.
- Heavy tails or skewed residuals → p-values and CIs from OLS are
  unreliable. The regression line itself (point estimate) is more
  robust, but inference (significance, intervals) breaks down.
- Bimodal residuals → possible missing variable or mixture of two
  populations. The regression is fitting a line through two clusters.

**What it means when violated:**
- Mild non-normality: OLS is somewhat robust for large n (CLT).
  Point estimates are OK, but p-values may be slightly off.
- Severe non-normality (heavy tails, outliers): p-values and CIs
  become unreliable. A single outlier can flip significance.
- Skewness: CIs become asymmetric but OLS reports symmetric intervals.

### 3. Homoscedasticity (constant variance)

**The assumption:** The variance of residuals is the same across all
values of X (or fitted values).

**What to look for in the paper:**
- Residual-vs-fitted plot? The spread of residuals should be roughly
  constant (no "fan" or "trumpet" shape).
- Breusch-Pagan test, White test, or Goldfeld-Quandt test reported?
- If heteroscedasticity acknowledged, did they use robust standard
  errors (HC0–HC3, sandwich estimator)?

**Red flags:**
- Variance visibly increases with Y (common in count data, financial
  data, any variable that spans orders of magnitude).
- Log-transformed Y to "fix" heteroscedasticity without back-
  transforming predictions correctly. Predictions on the log scale
  don't back-transform to means on the original scale (they give
  medians, biased low).
- Weighted least squares claimed but weights not justified or reported.

**What it means when violated:**
- OLS coefficient estimates remain unbiased but are no longer
  efficient (not minimum-variance).
- Standard errors are wrong → p-values are wrong → CIs are wrong.
- Points in high-variance regions get the same weight as low-variance
  regions, so the fit is distorted toward the noisy end.

### 4. Zero-mean residuals (no systematic bias)

**The assumption:** E(ε) = 0 at every value of X. The residuals don't
have a systematic pattern.

**What to look for in the paper:**
- Residual-vs-fitted plot (again — this single plot catches most
  violations of assumptions 1, 3, and 4 simultaneously).
- Residuals plotted against each predictor and against time/sequence.

**Red flags:**
- Residuals show a trend or curve when plotted against fitted values
  → linearity violation (Check 1) or omitted variable bias.
- Residuals show a trend when plotted against time or observation
  order → autocorrelation. Common in time series and spatial data.
  Durbin-Watson test or variogram should be reported.
- Mean residual per subgroup is systematically positive or negative
  → the model underpredicts for some conditions and overpredicts
  for others. Possible missing interaction or nonlinear term.

**What it means when violated:**
- Coefficient estimates are biased — they absorb the effect of
  whatever is missing from the model.
- All downstream inference (p-values, CIs, predictions) is wrong
  in a directional way, not just noisy.

## Outlier and leverage audit

Beyond the four Gauss-Markov assumptions, individual data points can
disproportionately influence regression results.

### What to look for:

- **Cook's distance** — combines leverage (unusual X) and residual
  (unusual Y). Points with Cook's D > 4/n or > 1 deserve scrutiny.
  Did the authors report Cook's D or at least mention checking it?
- **DFBETAS** — how much each coefficient changes when a point is
  removed. Important when a single observation might flip the sign
  or significance of a predictor.
- **Hat values (leverage)** — points far from the centroid of X space
  have disproportionate influence. In multivariate regression,
  leverage is not always obvious from bivariate scatterplots.
- **Sensitivity analysis** — did the authors report "results are robust
  to removing outliers" or show a leave-one-out analysis? If not,
  and the sample is small, the results may be driven by 1–2 points.

### Red flags:

- Small n (< 30) with no outlier analysis reported. In small samples,
  a single point can dominate the fit. This connects directly to
  `spurious.P_spurious()` — a high r with small n is more likely to
  be a chance arrangement of a few influential points.
- Outliers removed "to improve model fit" without independent
  justification (measurement error, known data entry mistake). This
  is data dredging if the removal criterion is the residual itself.
- Authors report both "with outliers" and "without outliers" results
  and focus on whichever is significant → selective reporting.

### Connection to code modules:

- `leverage.influence_plot()` — Cook's D, hat values, studentized
  residuals. Use when raw data is available or digitized from figures.
- `leverage.distance_correlation_test()` — nonlinear association test
  that doesn't assume linearity.
- `dc_cluster.effective_k()` — if predictors cluster, the effective
  number of independent variables is lower than the nominal count.

## Quick decision guide for LLM paper audit

```
Paper reports regression results?
│
├─ Is a scatterplot shown?
│  ├─ No → Flag: "No visual evidence of relationship shape"
│  └─ Yes → Check for obvious nonlinearity, clusters, outliers
│
├─ Are residual plots shown?
│  ├─ No → Flag: "Regression assumptions not verified"
│  └─ Yes → Check for patterns (curve, fan, clusters)
│
├─ Is n < 30?
│  ├─ Yes → Flag: "Small sample — check influence of individual points"
│  │         Ask: Cook's D reported? Sensitivity analysis?
│  └─ No  → Lower concern, but heteroscedasticity still matters
│
├─ Were outliers removed?
│  ├─ Yes → Was removal justified independently of the model?
│  │         If justified by residual size alone → Flag: data dredging
│  └─ No  → OK, but if n is small, absence of outlier check is itself
│            a concern
│
└─ Does the paper claim prediction/extrapolation?
   ├─ Yes → Is the prediction range within the observed data range?
   │         Extrapolation beyond observed range is unreliable even
   │         if all assumptions hold within range.
   └─ No  → Standard inference concerns apply
```

## Explainable AI as audit tool (SHAP, permutation importance)

When a paper (or your own work) reports ML predictions — Random Forest,
gradient boosting, neural nets — traditional regression diagnostics
(residual plots, Cook's D) don't apply directly. The model is a black
box. Explainable AI methods, particularly SHAP (SHapley Additive
exPlanations), open that box for auditing purposes.

This section tells the auditor what to look for in SHAP output, not
how to compute it. SHAP is a mature, well-maintained package. The
bullshit-detector's value add is the *interpretation framework* —
connecting SHAP results to the statistical red flags caught by other
modules.

### What SHAP shows

SHAP decomposes each prediction into additive contributions from each
feature. For a single prediction: how much did each input push the
prediction above or below the baseline? Across the dataset: which
features matter most, and how does their effect vary with feature value?

Three SHAP plot types matter for auditing:

- **Summary (beeswarm) plot** — global feature importance ranked by
  mean |SHAP value|. Shows which features the model relies on and
  whether the direction of effect makes physical sense.
- **Waterfall plot** — single-prediction decomposition. Shows exactly
  which features drove a specific prediction, and by how much. Useful
  for auditing whether individual predictions are physically defensible
  (see Roure & Perez 2025 for a geoscience example: SHAP waterfall
  applied to GR log prediction from seismic attributes).
- **Dependence plot** — SHAP value for one feature vs. that feature's
  value, colored by a second feature. This is essentially a ceteris
  paribus curve: how does the model's output change as one input varies?

### What to look for (red flags)

**Feature importance without physical justification:**
A feature with no known physical relationship to the target shows high
SHAP importance. This is the Kalkomey trap made visible. Cross-reference
against `spurious.P_spurious()` for that sample size and attribute count.
If P_spurious is high and the top SHAP feature is physically implausible,
the model has likely learned a coincidence.

Example: In seismic reservoir property prediction, if a geometric
attribute with no rock physics basis outranks impedance or amplitude,
the model may be fitting noise. The Hunt dataset synthetic example
is the extreme case: X_fabricated would show as the most important
feature in SHAP — and that importance *is* the red flag.

**Non-monotonic or implausible dependence shapes:**
SHAP dependence plots should show relationships consistent with domain
knowledge. In a porosity prediction model, acoustic impedance should
show a negative relationship (higher impedance → lower porosity in
clastics). If the dependence plot shows the opposite, or a
non-monotonic zigzag, the model may be fitting artifacts.

Connection to `causal_consistency.md` Check 5 (Concomitant Variation):
the SHAP dependence plot is a visual dose-response check. If the
curve is flat everywhere except a narrow region, the claimed effect
may depend on an outlier cluster or a specific covariate combination.

**Redundant features sharing importance:**
If several highly correlated features all show moderate SHAP importance,
the model is splitting credit among collinear inputs. The total effect
of the underlying physical property is underrepresented by any single
feature's SHAP rank. Cross-reference with `redundancy.redundancy_analysis()`
or `dc_cluster.effective_k()` to identify the redundancy structure.
SHAP interaction values (if computed) can reveal whether the model is
using different collinear features in different regions of the input
space — a sign of overfitting to noise.

**Feature importance that contradicts reported variable selection:**
If the paper claims they selected features carefully but SHAP shows
that two of the top five features are trivially correlated with each
other (e.g., P-impedance and density in the same inversion), the
effective dimensionality is lower than claimed. Feed the SHAP-revealed
redundancy back into `spurious.P_spurious()` with corrected k.

### Where SHAP fits in the tier system

SHAP is Tier 3 — it requires either raw data and a fitted model, or
enough information in the paper to reconstruct the analysis. It
complements:

- `leverage.influence_plot()` — which points drive the fit (data-space
  view) vs. which features drive predictions (feature-space view)
- `dc_cluster.effective_k()` — redundancy structure in the predictors,
  now visible through SHAP's credit allocation
- `spurious.P_spurious()` — SHAP makes the spurious correlation
  problem concrete by naming the suspect features

### When SHAP is not the right tool

SHAP explains what a model learned. It does not tell you whether what
the model learned is true. A model can have perfectly interpretable
SHAP plots and still be fitting spurious correlations — especially
when n is small relative to k. SHAP importance is not evidence of
causation. Always check `spurious.P_spurious()` and `power.achieved_power()`
before trusting SHAP-based narratives about feature importance.

### Quick decision guide for SHAP audit

```
Paper reports ML model with feature importance or SHAP?
│
├─ Are the top features physically plausible?
│  ├─ No → Flag: "Dominant feature has no known physical mechanism"
│  │        Cross-check: spurious.P_spurious(r, n, k)
│  └─ Yes → Check dependence plot shapes
│
├─ Do SHAP dependence plots show sensible relationships?
│  ├─ Non-monotonic or reversed → Flag: "Feature effect contradicts
│  │   domain knowledge" — possible overfitting or confounding
│  └─ Monotonic, correct direction → Lower concern
│
├─ Are multiple correlated features sharing importance?
│  ├─ Yes → Flag: "Redundant features inflate apparent model complexity"
│  │         Feed effective_k into spurious.P_spurious()
│  └─ No  → OK
│
├─ Is n small relative to number of features?
│  ├─ n/k < 10 → Flag: "SHAP importance unreliable — model likely
│  │              overfit. Check spurious.P_spurious() and power."
│  └─ n/k > 10 → Standard concerns apply
│
└─ Does the paper use SHAP to claim causation?
   ├─ Yes → Flag: "SHAP shows model reliance, not causal effect"
   │         Route to causal_consistency.md Mill's Methods
   └─ No  → OK
```

## Future extensions

- **Ceteris paribus plots** (Molnar, *Interpretable ML*; Kuźba et al.
  2019) as a complement to SHAP dependence plots. CP plots show how
  a prediction changes when one feature varies while everything else
  is held constant — a direct visual check for Mill's Concomitant
  Variation (Check 5 in `causal_consistency.md`). If the CP curve is
  flat everywhere except a narrow region, the claimed effect may depend
  on outliers or a specific covariate combination. Requires raw data
  or fitted model. Complements `influence_plot()` (which points drive
  the fit) with how the prediction surface behaves across the full
  input range.
- **Permutation feature importance** as a simpler alternative to SHAP
  when full SHAP computation is too expensive. Same audit logic applies:
  if the most important feature by permutation has no physical basis,
  flag it.

## References

- Davis (1986), *Statistical Methods in the Earth Sciences*, Cambridge
  University Press. Figure 6.2: regression assumption violations.
- Cook (1977), "Detection of Influential Observation in Linear
  Regression", Technometrics 19(1):15–18
- Belsley, Kuh & Welsch (1980), *Regression Diagnostics: Identifying
  Influential Data and Sources of Collinearity*, Wiley
- Anscombe (1973), "Graphs in Statistical Analysis", The American
  Statistician 27(1):17–21. (Anscombe's quartet — identical summary
  statistics, wildly different data patterns. The original argument
  for always plotting your data.)
- Speidel (2018), GeoConvention R notebook on petroleum dataset
  diagnostics — source material for leverage.py implementation.
- Lundberg & Lee (2017), "A Unified Approach to Interpreting Model
  Predictions", NeurIPS 2017. (SHAP: SHapley Additive exPlanations.)
- Molnar (2022), *Interpretable Machine Learning*, 2nd edition.
  https://christophm.github.io/interpretable-ml-book/
  (Chapters on SHAP, permutation importance, feature interaction,
  ceteris paribus plots.)
- Roure & Perez (2025), "Maximizing field development through rock
  physics informed hi-res ML seismic estimates of reservoir properties",
  GeoConvention 2025. (SHAP waterfall applied to GR log prediction
  from seismic attributes — good geoscience XAI example.)
- Lubo-Robles, Devegowda, Jayaram, Bedle, Marfurt & Pranter (2022),
  "Quantifying the sensitivity of seismic facies classification to
  seismic attribute selection: An explainable machine-learning study",
  Interpretation, SE41–SE69.
