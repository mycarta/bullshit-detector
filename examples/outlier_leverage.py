"""
Outlier leverage analysis — influence plot and distance correlation.

Demonstrates how a single influential data point can substantially change
a reported correlation, using Close et al. (2010) as the motivating example.

This script generates synthetic data with known outliers and shows:
  1. Which points are flagged as high-leverage / high-residual
  2. Cook's distance values for each observation
  3. How removing influential points changes CC and DC
  4. Distance correlation test results (with and without outliers)

Based on: Notebook E (Be-a-geoscience-detective_example_2.ipynb)
Reference: Close et al. (2010), CSEG Recorder.

Usage:
    python examples/outlier_leverage.py
Saves: examples/influence_plot.png
"""

import os

import matplotlib
matplotlib.use("Agg")   # non-interactive backend for saving
import matplotlib.pyplot as plt
import numpy as np

from bullshit_detector.leverage import distance_correlation_test, influence_plot

# ---------------------------------------------------------------------------
# Build synthetic dataset
# ---------------------------------------------------------------------------
rng = np.random.default_rng(7)
n_clean = 20

# Clean data: moderate positive linear trend
x_clean = rng.uniform(0.5, 3.5, n_clean)
y_clean = 1.8 * x_clean + rng.normal(0, 0.6, n_clean)

# Outlier A — high leverage (far from cluster in x, on the regression line)
# Increases apparent CC without adding real information.
x_lev = np.array([8.0])
y_lev = np.array([1.8 * 8.0 + 0.1])

# Outlier B — high residual (within x range but very far from regression line)
x_res = np.array([2.0])
y_res = np.array([-4.0])

# Full dataset (clean + both outliers)
x_all = np.concatenate([x_clean, x_lev, x_res])
y_all = np.concatenate([y_clean, y_lev, y_res])

idx_lev = n_clean       # index 20
idx_res = n_clean + 1   # index 21

# ---------------------------------------------------------------------------
# Run influence_plot on full dataset
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(2, 1, figsize=(10, 12))

# Top panel: scatter + regression line
ax_scatter = axes[0]
ax_scatter.scatter(x_clean, y_clean, color="steelblue", s=60,
                   label="clean data", zorder=3)
ax_scatter.scatter(x_lev, y_lev, color="darkorange", s=100, marker="^",
                   label=f"high-leverage point (idx {idx_lev})", zorder=4)
ax_scatter.scatter(x_res, y_res, color="crimson", s=100, marker="s",
                   label=f"high-residual point (idx {idx_res})", zorder=4)

# Fit line for visual reference
from scipy.stats import linregress as _lr
slope, intercept, *_ = _lr(x_all, y_all)
xfit = np.linspace(x_all.min() - 0.3, x_all.max() + 0.3, 200)
ax_scatter.plot(xfit, slope * xfit + intercept, "k--", lw=1.5,
                label="OLS fit (all data)")

for i, (xi, yi) in enumerate(zip(x_all, y_all)):
    ax_scatter.annotate(str(i), (xi + 0.05, yi + 0.05), fontsize=7, color="grey")

ax_scatter.set_xlabel("x")
ax_scatter.set_ylabel("y")
ax_scatter.set_title("Synthetic data with known influential points")
ax_scatter.legend(fontsize=9)
ax_scatter.grid(True, alpha=0.4)

# Bottom panel: statsmodels influence plot
result = influence_plot(x_all, y_all, ax=axes[1])

plt.tight_layout()
out_path = os.path.join(os.path.dirname(__file__), "influence_plot.png")
plt.savefig(out_path, dpi=120, bbox_inches="tight")
plt.close()

# ---------------------------------------------------------------------------
# Print Cook's distance summary
# ---------------------------------------------------------------------------
cooks  = result["cooks_distance"]
h_lev  = result["high_leverage"]
h_res  = result["high_residual"]
cc_all = result["cc"]

print("=" * 62)
print("Outlier Leverage Analysis — Synthetic Dataset")
print("=" * 62)
cook_header = f"{'Idx':>4}  {'Cooks D':>10}  {'High leverage?':>15}  {'High residual?':>15}"
print("\n" + cook_header)
print("-" * 52)
for i in range(len(x_all)):
    hl = "YES" if i in h_lev else ""
    hr = "YES" if i in h_res else ""
    marker = " <-- outlier" if i in (idx_lev, idx_res) else ""
    print(f"{i:>4}  {cooks[i]:>10.4f}  {hl:>15}  {hr:>15}{marker}")

print()
print(f"High-leverage indices (hat > 2(k+1)/n): {h_lev}")
print(f"High-residual indices (|stud. resid| > 2): {h_res}")

# ---------------------------------------------------------------------------
# Correlation comparison: all data vs. clean only
# ---------------------------------------------------------------------------
from scipy.stats import pearsonr as _pr

r_all,   _ = _pr(x_all,   y_all)
r_clean, _ = _pr(x_clean, y_clean)
r_no_lev, _ = _pr(np.delete(x_all, idx_lev), np.delete(y_all, idx_lev))
r_no_res, _ = _pr(np.delete(x_all, idx_res), np.delete(y_all, idx_res))

print()
print("=" * 62)
print("Pearson CC — impact of individual outliers")
print("=" * 62)
print(f"  All data (n={len(x_all)}):                          r = {r_all:.3f}")
print(f"  Without high-leverage point (idx {idx_lev}):   r = {r_no_lev:.3f}")
print(f"  Without high-residual point  (idx {idx_res}):   r = {r_no_res:.3f}")
print(f"  Clean data only (n={n_clean}):                   r = {r_clean:.3f}")

# ---------------------------------------------------------------------------
# Distance correlation test — all data vs. clean only
# ---------------------------------------------------------------------------
print()
print("=" * 62)
print("Distance correlation test (permutation, 2000 resamples)")
print("=" * 62)

dc_all   = distance_correlation_test(x_all,   y_all,   num_resamples=2000)
dc_clean = distance_correlation_test(x_clean, y_clean, num_resamples=2000)

print(f"  All data   — DC = {dc_all['dcor']:.3f},  "
      f"p = {dc_all['p_value']:.4f},  "
      f"significant = {dc_all['significant']}")
print(f"  Clean only — DC = {dc_clean['dcor']:.3f},  "
      f"p = {dc_clean['p_value']:.4f},  "
      f"significant = {dc_clean['significant']}")

print()
print("Key question (Kalkomey / Close et al. framework):")
print("  Did the authors justify removal of influential points with domain")
print("  knowledge AND formal leverage analysis, or did they simply drop")
print("  points until the correlation looked good?")
print()
print(f"Influence plot saved → {out_path}")
