"""
Underpowered neuroscience -- reproducing Button et al. (2013).

Button et al. analysed 730 studies from 41 meta-analyses across 8 domains
of neuroscience and estimated that the median statistical power was ~21%.
That means the typical study had less than a 1-in-4 chance of detecting
the effect it was designed to find -- even if the effect is real.

Consequences of chronic underpowering (Button et al. 2013, Ioannidis 2005):
  1. Most published "significant" findings are false positives.
  2. True effects that are published tend to be inflated
     (the "winner's curse").
  3. Studies replicate poorly -- the replication crisis in a nutshell.

This script uses achieved_power() and required_n() to reproduce the
core quantitative argument from three angles:

  Scenario 1 -- Typical small neuroimaging study
     n=16/group, Cohen's d=0.5 (medium effect)
     What power did that study actually have?

  Scenario 2 -- What n would 80% power actually require?
     required_n() for d=0.5 at alpha=0.05, power=0.80

  Scenario 3 -- Power across a range of effect sizes at n=20/group
     Sweeps d in {0.2, 0.3, 0.5, 0.8} to show the full landscape.

References
----------
Button, K.S. et al. (2013). Power failure: why small sample size
undermines the reliability of neuroscience.
Nature Reviews Neuroscience, 14(5), 365-376.
DOI: 10.1038/nrn3475

Ioannidis, J.P.A. (2005). Why most published research findings are false.
PLoS Medicine, 2(8), e124. DOI: 10.1371/journal.pmed.0020124

Cohen, J. (1988). Statistical Power Analysis for the Behavioral
Sciences (2nd ed.). Lawrence Erlbaum Associates.
"""

from bullshit_detector.power import achieved_power, required_n


SEP  = "-" * 62
SEP2 = "=" * 62


def power_label(pwr):
    """Return a short ASCII verdict string for a power value."""
    if pwr >= 0.80:
        return "adequate"
    if pwr >= 0.50:
        return "marginal"
    return "UNDERPOWERED"


# ---------------------------------------------------------------------------
# Scenario 1 -- Typical small neuroimaging study (n=16/group, d=0.5)
# ---------------------------------------------------------------------------
print(SEP2)
print("  Scenario 1 -- Typical small neuroimaging study")
print(SEP2)
print("  Design:  n=16 per group, Cohen's d=0.5 (medium effect)")
print("  Alpha:   0.05 (two-sided)")
print()

sc1 = achieved_power(effect_size=0.5, n_per_group=16, alpha=0.05)

print(SEP)
print("  achieved_power() result")
print(SEP)
for key, value in sc1.items():
    if key == "interpretation":
        continue  # printed separately below (avoids console encoding issues)
    print("  {:<20} {}".format(key, value))

print()
print("  Result:  {:.1f}% power -- {}".format(
          sc1["power"] * 100, power_label(sc1["power"])))
print()
print("  Button et al. (2013): median neuroscience power is ~21%.")
print("  Even this optimistic medium-effect scenario is only ~{:.0f}%.".format(
          sc1["power"] * 100))
print("  A study powered at 30% that reports p<0.05 is more likely to")
print("  be a false positive than a true effect.")


# ---------------------------------------------------------------------------
# Scenario 2 -- How many participants does 80% power actually require?
# ---------------------------------------------------------------------------
print()
print(SEP2)
print("  Scenario 2 -- Required n for 80% power at d=0.5")
print(SEP2)
print("  Target:  80% power, d=0.5, alpha=0.05 (two-sided)")
print()

sc2 = required_n(effect_size=0.5, alpha=0.05, power=0.80)

print(SEP)
print("  required_n() result")
print(SEP)
for key, value in sc2.items():
    print("  {:<20} {}".format(key, value))

print()
print("  Result:  {} per group ({} total) needed for 80% power.".format(
          sc2["n_per_group"], sc2["n_total"]))
print("  The typical neuroimaging study recruits ~16/group -- {:.0f}x too small.".format(
          sc2["n_per_group"] / 16))


# ---------------------------------------------------------------------------
# Scenario 3 -- Power table: d in {0.2, 0.3, 0.5, 0.8} at n=20/group
# ---------------------------------------------------------------------------
print()
print(SEP2)
print("  Scenario 3 -- Power at n=20/group across effect sizes")
print(SEP2)
print("  Design:  n=20 per group, alpha=0.05, two-sided")
print()

effect_sizes = [
    (0.2, "small  (Cohen d=0.2)"),
    (0.3, "small+ (Cohen d=0.3)"),
    (0.5, "medium (Cohen d=0.5)"),
    (0.8, "large  (Cohen d=0.8)"),
]

print("  {:<35} {:>8}  {:>12}  {}".format(
      "Effect size", "Power", "n needed*", "Verdict"))
print("  " + "-" * 58)

for d_val, label in effect_sizes:
    ap = achieved_power(effect_size=d_val, n_per_group=20, alpha=0.05)
    rn = required_n(effect_size=d_val, alpha=0.05, power=0.80)
    print("  {:<35} {:>7.1f}%  {:>12}  {}".format(
          label,
          ap["power"] * 100,
          str(rn["n_per_group"]) + "/grp",
          power_label(ap["power"])))

print()
print("  * n needed = minimum per group for 80% power at that d.")


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print()
print(SEP2)
print("  Summary")
print(SEP2)
print("  A study with n=16/group has only ~{:.0f}% power to detect d=0.5.".format(
          achieved_power(effect_size=0.5, n_per_group=16)["power"] * 100))
print("  To detect the same effect with 80% power requires ~{} per group.".format(
          required_n(effect_size=0.5, power=0.80)["n_per_group"]))
print()
print("  Button et al. conclusion:")
print("    'The average statistical power of studies in the neurosciences is")
print("     very low. [...] This has a profound impact on the reliability of")
print("     findings. [...] Low-powered studies also tend to have inflated")
print("     effect sizes, making it harder to accurately gauge true effect")
print("     magnitudes.'")
print()
print("  Reference:")
print("  Button et al. (2013). Nature Reviews Neuroscience, 14(5), 365-376.")
print("  DOI: 10.1038/nrn3475")
