# Power Analysis Skill (Tier 2)

> Detailed worked examples to be written after code is stable.
> See power.py docstrings for function descriptions.
> See Speidel (2018) GeoConvention R notebook for worked example.

## Detection heuristic

If a study's sample size doesn't match what a power calculation would require
for the claimed effect, the sample may have been "chased" — data collected
until p < 0.05, then stopped (Szucs 2016). Pre-registered power calculations
are a sign of good practice; their absence in underpowered studies is a red flag.

## References

- Button et al. (2013), "Power failure: why small sample size undermines the
  reliability of neuroscience", Nature Reviews Neuroscience 14:365-376
- Speidel (2018), GeoConvention R notebook — power analysis on Hunt dataset
- Szucs (2016), "A Tutorial on Hunting Statistical Significance by Chasing N",
  Frontiers in Psychology 7:1444
