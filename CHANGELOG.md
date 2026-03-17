# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.2] — 2026-03-09

### Changed
- License switched from Apache-2.0 to MIT.

### Added
- Three paper audit worked examples in `audits/`: Carney (2010) power posing, Wansink pizza GRIMMER, ORBITA (2018) PCI/angina.
- Paper audits section added to README.
- `skills/reproducibility_challenge.md` — placeholder replaced with full Notebook D/E methodology writeup.
- `skills/redundancy_analysis.md` — placeholder replaced with full Speidel methodology writeup.
- Weinstein & Adam *Guesstimation* references added to intellectual foundations.

---

## [0.2.1] — 2026-03-05

### Changed
- README updated to reflect SHAP/XAI audit capability, unsupervised learning critique, and ML explainability screening across tier descriptions.

---

## [0.2.0] — 2026-03-05

### Added
- `skills/spurious_correlation.md` — expanded with Kalkomey tables, Hunt worked example, red flags, and "Not covered" section.
- `skills/power_analysis.md` — expanded with Button et al., Speidel geoscience context, SD/SE trap worked examples, and "Not covered" section.
- `skills/unsupervised_learning_critique.md` — new skill file covering cluster reification, centroid vs medoid, stability, dimensionality reduction as evidence; worked example: Ahlqvist (2018).
- `skills/outlier_leverage.md` — SHAP/XAI audit section added.
- `skills/paper_screening.md` — ML explainability screening note added.
- All code-backed skill files updated with "Not covered" sections declaring blind spots.
- Tier 0 blind spots section added to `paper_screening.md`.

---

## [0.1.1] — 2026-02-27

### Added
- 7 example scripts in `examples/`: green coffee, GRIM check, Hunt dataset, Kalkomey screening, outlier leverage, SD vs SE, underpowered study.
- Quick Start section in README with real outputs.
- Acknowledgments section in README (Sainani 2020, Speidel 2018).

### Changed
- README prose and Quick Start examples improved.

---

## [0.1.0] — 2026-02-27

### Added
- Initial implementation: 6 detection modules (`p_checker`, `grimmer`, `spurious`, `power`, `leverage`, `dc_cluster`, `reproducibility`, `paper_screening`, `redundancy`).
- 40 tests passing (expanded to 104 by end of phase).
- `pyproject.toml` with core and optional dependencies (`full`, `batch`, `dev` extras).
