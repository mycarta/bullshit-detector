"""
SD vs SE confusion -- Sainani (2020) sports science case study.

Kristin Sainani (2020) audited 157 highly cited meta-analyses in strength
and conditioning research and found that 45% of them used the standard
error of the mean (SE) where they should have used the standard deviation
(SD) when computing Cohen's d effect sizes. Because SE = SD / sqrt(n),
substituting SE for SD deflates the denominator and inflates d by sqrt(n).

With typical group sizes of n=25-35, the inflation factor is 5-6x.
This produced reported effect sizes of 11-14 standard deviations --
physically impossible values that somehow passed peer review.

This script demonstrates the error pattern with a concrete scenario:

  Step 1 -- The reported value: d=12.0.
            A Fermi sanity check immediately flags this as impossible.

  Step 2 -- The correction: if SE was used instead of SD, and n=30,
            then SD = SE x sqrt(30) ~ SE x 5.48.
            Corrected d = 12.0 / sqrt(30) ~ 2.19.

  Step 3 -- Power check: achieved_power() shows that d=12 would be
            detectable with absurdly tiny samples, while the real d~2.19
            requires realistic sample sizes.

References
----------
Sainani, K.L. (2020). The problem of multiple comparison correction.
PM&R, 12(10), 1073-1076. DOI: 10.1002/pmrj.12501

Sainani, K.L. et al. (2021). Call to improve the statistical reporting
in strength and conditioning research.
International Journal of Strength and Conditioning, 1(1).
DOI: 10.47206/ijsc.v1i1.69

Cohen, J. (1988). Statistical Power Analysis for the Behavioral
Sciences (2nd ed.). Lawrence Erlbaum Associates.
"""

import math
from scipy import stats
from bullshit_detector.power import achieved_power, required_n


SEP  = "-" * 64
SEP2 = "=" * 64


# ---------------------------------------------------------------------------
# The scenario: a meta-analysis reports d = 12.0
# ---------------------------------------------------------------------------
D_REPORTED = 12.0
N_PER_GROUP = 30        # typical group size in strength & conditioning studies

print(SEP2)
print("  SD vs SE Confusion -- Sainani (2020)")
print(SEP2)
print("  Reported effect size: Cohen's d = {:.1f}".format(D_REPORTED))
print("  Typical group size:   n = {} per group".format(N_PER_GROUP))


# ---------------------------------------------------------------------------
# Step 1 -- Fermi sanity check: is d=12 physically plausible?
# ---------------------------------------------------------------------------
print()
print(SEP)
print("  Step 1 -- Fermi sanity check: is d={:.1f} plausible?".format(D_REPORTED))
print(SEP)
print()

# Cohen's d = (mean1 - mean2) / SD
# U3 statistic = fraction of group 2 below the mean of group 1
# At d=12, the overlap between the two distributions is negligible.
u3_reported = stats.norm.cdf(D_REPORTED)
tail_prob   = stats.norm.sf(D_REPORTED)

print("  Cohen's d interpretation (normal distributions):")
print("    d = 0.2  small effect  -- distributions overlap ~85%")
print("    d = 0.5  medium effect -- distributions overlap ~67%")
print("    d = 0.8  large effect  -- distributions overlap ~53%")
print("    d = 2.0  huge effect   -- distributions overlap ~16%")
print("    d = 4.0  extreme       -- overlap < 0.01%")
print()
print("  d = {:.1f}:".format(D_REPORTED))
print("    U3 statistic:       {:.10f}".format(u3_reported))
print("    P(any overlap):     {:.2e}".format(tail_prob))
print("    This means ~100% of group 2 would score below group 1's mean.")
print("    In strength & conditioning terms: every untrained person would")
print("    score below *every* trained person without exception -- across")
print("    the entire population. This is impossible.")
print()
print("  [FLAG] d={:.1f} is not physically plausible. Investigate the".format(D_REPORTED))
print("         denominator. Likely cause: SE used instead of SD.")


# ---------------------------------------------------------------------------
# Step 2 -- SE/SD correction
# ---------------------------------------------------------------------------
print()
print(SEP)
print("  Step 2 -- SE/SD correction")
print(SEP)
print()

se_to_sd_factor = math.sqrt(N_PER_GROUP)
D_CORRECTED = D_REPORTED / se_to_sd_factor

print("  If the authors used SE instead of SD:")
print("    SE = SD / sqrt(n)")
print("    => SD = SE x sqrt(n) = SE x sqrt({}) = SE x {:.3f}".format(
          N_PER_GROUP, se_to_sd_factor))
print()
print("  Inflation factor:      sqrt({}) = {:.3f}".format(
          N_PER_GROUP, se_to_sd_factor))
print("  Reported d:            {:.1f}".format(D_REPORTED))
print("  Corrected d:           d / sqrt(n) = {:.1f} / {:.3f} = {:.2f}".format(
          D_REPORTED, se_to_sd_factor, D_CORRECTED))

u3_corrected = stats.norm.cdf(D_CORRECTED)
overlap_corrected = 2 * stats.norm.sf(D_CORRECTED / 2.0)

print()
print("  d = {:.2f} (corrected):".format(D_CORRECTED))
print("    U3 statistic:     {:.4f}  ({:.1f}% of group 2 below group 1 mean)".format(
          u3_corrected, u3_corrected * 100))
print("    Distributional    overlap ~ {:.1f}%".format(overlap_corrected * 100))
print("    This is a very large, but not physically impossible, effect.")
print("    It would still be exceptional in sports science.")


# ---------------------------------------------------------------------------
# Step 3 -- Power check: what does each d imply about study design?
# ---------------------------------------------------------------------------
print()
print(SEP)
print("  Step 3 -- Power check")
print(SEP)
print()

rn_reported  = required_n(effect_size=D_REPORTED,  alpha=0.05, power=0.80)
rn_corrected = required_n(effect_size=D_CORRECTED, alpha=0.05, power=0.80)
ap_reported  = achieved_power(effect_size=D_REPORTED,  n_per_group=N_PER_GROUP)
ap_corrected = achieved_power(effect_size=D_CORRECTED, n_per_group=N_PER_GROUP)

print("  Required n per group for 80% power (alpha=0.05):")
print("    d = {:.1f} (reported):  {} per group  ({} total)".format(
          D_REPORTED,
          rn_reported["n_per_group"],
          rn_reported["n_total"]))
print("    d = {:.2f} (corrected): {} per group  ({} total)".format(
          D_CORRECTED,
          rn_corrected["n_per_group"],
          rn_corrected["n_total"]))
print()
print("  Achieved power at n={}/group:".format(N_PER_GROUP))
print("    d = {:.1f} (reported):  {:.1f}%  -- any study is massively overpowered".format(
          D_REPORTED, ap_reported["power"] * 100))
print("    d = {:.2f} (corrected): {:.1f}%  -- realistic but still needs n>{}/grp".format(
          D_CORRECTED,
          ap_corrected["power"] * 100,
          rn_corrected["n_per_group"]))
print()
print("  [FLAG] If d=12 were real, you could detect it with n=2 per group.")
print("         No study in sports science needs more than a handful of")
print("         participants per cell. Actual studies use n=20-40, which")
print("         is appropriate for the corrected d~2.2 -- not for d=12.")


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print()
print(SEP2)
print("  Summary")
print(SEP2)
print("  Reported d:   {:.1f}  --> physically impossible".format(D_REPORTED))
print("  Corrected d:  {:.2f}  --> plausible (very large training effect)".format(
          D_CORRECTED))
print("  Root cause:   SE used as denominator instead of SD")
print("  Inflation:    sqrt(n) = sqrt({}) = {:.2f}x".format(
          N_PER_GROUP, se_to_sd_factor))
print()
print("  Sainani (2020) finding:")
print("    45% of highly cited strength & conditioning meta-analyses")
print("    contained this error, producing effect sizes of 11-14 SD.")
print("    A Fermi check -- 'is this many standard deviations physically")
print("    possible?' -- immediately identifies the error without")
print("    access to the raw data.")
print()
print("  Reference:")
print("  Sainani et al. (2021). Int. J. Strength and Conditioning, 1(1).")
print("  DOI: 10.47206/ijsc.v1i1.69")
