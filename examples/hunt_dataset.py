"""
Kalkomey (1997) decision framework applied to Hunt (2013) 21-well dataset.

This example uses a *synthetic* dataset modelled on Hunt (2013) to demonstrate
why statistical significance alone is insufficient to validate a predictor.
The key lesson: a fabricated variable (log-transform of the real predictor
plus noise) can pass every statistical test yet must be rejected because it
has no independent physical justification.

References:
    Kalkomey, C.T. (1997). Potential risks when using seismic attributes as
        predictors of reservoir properties. The Leading Edge, March 1997,
        pp. 247–251.
    Hunt, L. et al. (2013). What's new in geophysical exploration for tight oil
        (Part 2). CSEG Recorder, April 2013.

Usage:
    python examples/hunt_dataset.py
"""

import numpy as np
import pandas as pd
from bullshit_detector.spurious import P_spurious, conf_int, r_crit

# ---------------------------------------------------------------------------
# Synthetic 21-well dataset (modelled on Hunt 2013)
# ---------------------------------------------------------------------------
rng = np.random.default_rng(42)
n = 21

# GrossPay is the physically justified predictor (Darcy's Law: flow ∝ thickness)
gross_pay = rng.uniform(5, 80, n)

# Production is linearly driven by GrossPay + geological scatter
production = 1.8 * gross_pay + rng.normal(0, 12, n)
production = np.clip(production, 5, None)

# Porosity: moderate predictor — real physical basis but weaker signal
porosity = 0.04 * gross_pay + rng.uniform(0.05, 0.20, n)

# X_fabricated: log(GrossPay) + small noise — high r, but NO independent
# physical justification (it is just a non-linear transform of gross_pay)
x_fabricated = np.log(gross_pay) + rng.normal(0, 0.15, n)

# X_random: pure noise — no relationship with production
x_random = rng.normal(0, 1, n)

df = pd.DataFrame({
    "Production":   production,
    "GrossPay":     gross_pay,
    "Porosity":     porosity,
    "X_fabricated": x_fabricated,
    "X_random":     x_random,
})

# ---------------------------------------------------------------------------
# Compute Pearson r with Production for each predictor
# ---------------------------------------------------------------------------
predictors = ["GrossPay", "Porosity", "X_fabricated", "X_random"]
corrs = {col: float(df["Production"].corr(df[col])) for col in predictors}

# ---------------------------------------------------------------------------
# Decision table
# ---------------------------------------------------------------------------
rc = r_crit(n, alpha=0.025)       # two-tailed 5% critical r
k  = len(predictors)               # number of attributes tested
p_threshold = 0.10                 # P(spurious) ≤ 10% → statistically trustworthy

# Physical justification (domain knowledge, not derivable from statistics)
domain_justified = {
    "GrossPay":     True,   # Darcy's Law: production ∝ pay thickness
    "Porosity":     True,   # pore volume drives storage capacity
    "X_fabricated": False,  # transform of GrossPay — not an independent attribute
    "X_random":     False,  # no physical basis
}

print("=" * 90)
print(f"Hunt (2013) 21-well synthetic dataset — Kalkomey decision framework")
print(f"n={n} wells,  k={k} attributes tested,  r_crit={rc:.3f}  (α=0.025, two-tailed)")
print("=" * 90)

col_w = [16, 7, 11, 10, 12, 10, 14]
hdr = (f"{'Predictor':<{col_w[0]}} {'r':>{col_w[1]}} "
       f"{'P(spur,k=1)':>{col_w[2]}} {'P(spur,k=4)':>{col_w[3]}} "
       f"{'r > r_crit':>{col_w[4]}} {'CI ∩ 0?':>{col_w[5]}} {'Recommendation':<{col_w[6]}}")
print(hdr)
print("-" * 90)

for col in predictors:
    r = corrs[col]
    p1 = P_spurious(r, n, k=1)
    pk = P_spurious(r, n, k=k)
    lo, hi = conf_int(r, n)
    ci_crosses_zero = lo < 0 < hi or hi < 0 < lo   # CI straddles zero

    passes_r   = abs(r) > rc
    passes_p   = pk <= p_threshold
    dom_ok     = domain_justified[col]

    if not passes_r or not passes_p:
        rec = "REJECT (stat)"
    elif ci_crosses_zero:
        rec = "REJECT (CI)"
    elif not dom_ok:
        rec = "REJECT (domain)"
    elif passes_r and passes_p:
        rec = "KEEP"
    else:
        rec = "CAUTION"

    ci_str = "yes" if ci_crosses_zero else "no"
    r_str  = "yes" if passes_r else "no"

    print(f"{col:<{col_w[0]}} {r:>{col_w[1]}.3f} "
          f"{p1:>{col_w[2]}.4f} {pk:>{col_w[3]}.4f} "
          f"{r_str:>{col_w[4]}} {ci_str:>{col_w[5]}} {rec:<{col_w[6]}}")

print()
print("Columns:")
print("  P(spur, k=1) — probability this single correlation is spurious by chance")
print("  P(spur, k=4) — probability of ≥1 spurious hit across all 4 attributes tested")
print("  r > r_crit   — is |r| above the two-tailed 5% significance threshold?")
print("  CI ∩ 0?      — does the 95% Fisher-Z confidence interval include zero?")
print()
print("Key lesson")
print("----------")
r_fab = corrs["X_fabricated"]
p_fab = P_spurious(r_fab, n, k=k)
lo_fab, hi_fab = conf_int(r_fab, n)
print(f"  X_fabricated:  r={r_fab:.3f},  P(spurious, k=4)={p_fab:.4f},  "
      f"95% CI = [{lo_fab:.3f}, {hi_fab:.3f}]")
print("  → Passes ALL statistical tests (r > r_crit, low P(spurious), CI excludes 0)")
print("  → Rejected because it is a non-linear transform of GrossPay, not an")
print("    independent attribute. Using it alongside GrossPay would double-count")
print("    the same geological information and inflate confidence in the model.")
print()
r_gp = corrs["GrossPay"]
p_gp = P_spurious(r_gp, n, k=k)
lo_gp, hi_gp = conf_int(r_gp, n)
print(f"  GrossPay:      r={r_gp:.3f},  P(spurious, k=4)={p_gp:.4f},  "
      f"95% CI = [{lo_gp:.3f}, {hi_gp:.3f}]")
print("  → Passes statistical tests AND has physical justification (Darcy's Law)")
print("  → Recommended to KEEP.")
