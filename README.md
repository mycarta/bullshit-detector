# bullshit-detector

Statistical detection tools for screening published research.

> "Bullshit is unavoidable whenever circumstances require someone to talk without knowing what they are talking about." — Harry Frankfurt, *On Bullshit* (2005)

## What this is

A Python toolkit for systematically screening research papers for statistical red flags. Organized in four tiers, from quick API lookups to deep data analysis. Developed from petroleum geoscience applications but applicable to any field where correlations, p-values, and sample sizes are reported.

| Tier | What it checks | What you need | Time |
|------|---------------|---------------|------|
| **0 — Paper screening** | Journal legitimacy, retractions, author credentials | DOI, journal name | Minutes |
| **1 — Arithmetic** | p-value consistency, GRIM/GRIMMER tests | Reported statistics | Minutes |
| **2 — Plausibility** | Spurious correlations, critical r, confidence intervals | Summary stats (r, n, k) | Minutes |
| **3 — Data analysis** | Outlier leverage, distance correlation, reproducibility | Raw/digitized data | Hours |

## Installation

```bash
pip install bullshit-detector          # Core (Tiers 0–2)
pip install bullshit-detector[full]    # + Tier 3 tools (statsmodels, seaborn)
pip install bullshit-detector[batch]   # + statcheck for PDF batch scanning (GPL-3.0)
pip install bullshit-detector[dev]     # + pytest for development
```

## Quick start

```python
from bullshit_detector.p_checker import check_p_value
from bullshit_detector.spurious import P_spurious, r_crit, conf_int
from bullshit_detector.grimmer import a_grimmer
from bullshit_detector.paper_screening import check_journal, check_retraction
from bullshit_detector.power import required_n, achieved_power
from bullshit_detector.redundancy import redundancy_analysis

# Tier 0: Is the journal legitimate?
check_journal("Diabetes, Metabolic Syndrome, and Obesity")

# Tier 0: Has the paper been retracted?
check_retraction("10.2147/DMSO.S27665")

# Tier 1: Does the reported p-value match the test statistic?
check_p_value('t', 2.20, 28, reported_p=0.04)

# Tier 1: Is this mean possible from integer data?
a_grimmer(n=18, mean=3.44, sd=2.47)  # → "GRIMMER inconsistent"

# Tier 2: What's the probability this correlation is spurious?
P_spurious(0.6, 5, 10)  # r=0.6, 5 wells, 10 attributes → ~96%

# Tier 2: What's the critical r for this sample size?
r_crit(21)  # → ~0.433

# Tier 2: What's the CI for this correlation?
conf_int(0.73, 9)  # → (~0.13, ~0.94) — very broad!

# Tier 2: Was this study adequately powered?
achieved_power(d=16, sd1=16, sd2=12, n_per_group=11, alpha=0.10)

# Tier 2: How many wells would we need?
required_n(d=16, sd1=16, sd2=12, alpha=0.10, power=0.80)  # → ~11 per group
```

## Intellectual foundations

This project stands on the shoulders of:

- **Carl T. Bergstrom & Jevin D. West** — *Calling Bullshit: The Art of Skepticism in a Data-Driven World* (Random House, 2020) and their [University of Washington course](https://callingbullshit.org/). The paper-level screening module (Tier 0) directly implements their legitimacy framework.
- **Harry Frankfurt** — *On Bullshit* (Princeton University Press, 2005). Established the philosophical foundation.
- **C.T. Kalkomey** — "Potential risks when using seismic attributes as predictors of reservoir properties" (*The Leading Edge*, 1997). The spurious correlation probability formula.
- **N.J.L. Brown & J.A.J. Heathers** — "The GRIM Test" (*SPPS*, 2017). Arithmetic consistency checking for means.
- **Aurélien Allard** — "Analytic-GRIMMER" (2018). Extended GRIM to standard deviations. The Python port in this package is the first on PyPI.
- **Kristin Sainani** — "How to Be a Statistical Detective" (*PM&R*, 2020). Pedagogical framework tying these tools together.
- **Thomas Speidel** — GeoConvention 2018 R notebook. Variable selection methods (redundancy analysis, LASSO, sparse PCA, power analysis) on the Hunt dataset, complementing Niccoli's Python implementations. Inspired the redundancy and power modules.
- **Michèle Nuijten et al.** — statcheck (*Behavioral Research Methods*, 2016). P-value recomputation methodology.

## For AI assistants

The `skills/` directory contains detection heuristics and decision trees for each module. If you're a coding assistant (Copilot, Claude Code, etc.), read `skills/OVERVIEW.md` first.

## Acknowledgments

**Kristin Sainani** — her paper "How to Be a Statistical Detective" (*PM&R*, 2020, 12(2):211–215, DOI: [10.1002/pmrj.12305](https://doi.org/10.1002/pmrj.12305)) inspired the Tier 1 arithmetic consistency approach and the overall "statistical detective" framing of this package. The `p_checker` module's pedagogical structure follows her framework of treating statistical anomalies as clues that warrant further investigation.

**Thomas Speidel** — his GeoConvention 2018 R notebook, *Data Science Tools for Petroleum Exploration and Production*, provided the methodology for the power analysis and redundancy modules (Tier 2). The original GeoConvention 2018 presentation was a collaboration between Matteo Niccoli and Thomas Speidel; Speidel's R implementations of power analysis and variable redundancy (`Hmisc::redun`), applied to the Hunt (2013) 21-well dataset, were translated into the Python `power` and `redundancy` modules in this package.

## License

Apache-2.0. The optional `statcheck` dependency is GPL-3.0.
