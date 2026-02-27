"""
Reproduce Kalkomey (1997) Table 1 — P(spurious correlation).

Reference:
    Kalkomey, C.T. (1997). Potential risks when using seismic attributes
    as predictors of reservoir properties. The Leading Edge, March 1997,
    pp. 247–251.

Usage:
    python examples/kalkomey_screening.py
"""

from bullshit_detector.spurious import P_spurious, conf_int, r_crit

# ---------------------------------------------------------------------------
# Table 1 — P(spurious) for k=1 attribute
# Rows: sample size n | Columns: correlation r
# ---------------------------------------------------------------------------

r_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
n_values = [5, 10, 15, 20, 30, 50, 100]

print("=" * 72)
print("Kalkomey (1997) Table 1 — P(spurious correlation), k=1 attribute")
print("=" * 72)

col_width = 8
header = f"{'n':>5}" + "".join(f"  r={r:.1f}" for r in r_values)
print(header)
print("-" * len(header))

for n in n_values:
    row = f"{n:>5}"
    for r in r_values:
        p = P_spurious(r, n, k=1)
        row += f"  {p:5.3f} "
    print(row)

print()

# ---------------------------------------------------------------------------
# Multi-attribute case: n=5, r=0.6, varying k
# Shows how quickly P(spurious) approaches 1.0 with more attributes
# ---------------------------------------------------------------------------

k_values = [1, 5, 10, 20, 40]

print("=" * 52)
print("Multi-attribute risk: n=5, r=0.6, k attributes")
print("=" * 52)
print(f"{'k':>6}   {'P(spurious)':>12}   {'Risk level'}")
print("-" * 52)

for k in k_values:
    p = P_spurious(0.6, n=5, k=k)
    if p < 0.10:
        level = "Low"
    elif p < 0.50:
        level = "Moderate"
    elif p < 0.90:
        level = "High"
    else:
        level = "*** Very high ***"
    print(f"{k:>6}   {p:12.4f}   {level}")

print()

# ---------------------------------------------------------------------------
# Critical r values — minimum r needed to trust a single-attribute result
# ---------------------------------------------------------------------------

print("=" * 48)
print("Critical r (alpha=0.025, two-tailed) vs n, k=1")
print("=" * 48)
print(f"{'n':>6}   {'r_crit':>8}   {'95% CI half-width (at r_crit)'}")
print("-" * 48)

for n in n_values:
    rc = r_crit(n, alpha=0.025)
    lo, hi = conf_int(rc, n)
    hw = (hi - lo) / 2
    print(f"{n:>6}   {rc:8.3f}   ±{hw:.3f}")

print()
print("Interpretation: any reported r below r_crit is statistically")
print("indistinguishable from zero at the two-tailed 5% level.")
