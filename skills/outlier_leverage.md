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
