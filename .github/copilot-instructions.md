# Bullshit Detector — Copilot Instructions

This repository contains statistical detection tools for screening published research.
The package is organized in four tiers (Tier 0–3), from lightweight API lookups to
domain-expert data analysis. See `skills/OVERVIEW.md` for the full decision tree.

## Before writing code:
1. Read `skills/OVERVIEW.md` to understand the detection architecture
2. Read the relevant skill file for the module you're working on
3. Check existing implementations before writing new functions
4. Read docstrings in the stub files — they contain algorithm descriptions,
   test cases, and references to source material

## Module map:
- `src/bullshit_detector/paper_screening.py` → `skills/paper_screening.md` (Tier 0)
- `src/bullshit_detector/p_checker.py` → `skills/arithmetic_consistency.md` (Tier 1)
- `src/bullshit_detector/grimmer.py` → `skills/arithmetic_consistency.md` (Tier 1)
- `src/bullshit_detector/spurious.py` → `skills/spurious_correlation.md` (Tier 2)
- `src/bullshit_detector/power.py` → `skills/power_analysis.md` (Tier 2)
- `src/bullshit_detector/redundancy.py` → `skills/redundancy_analysis.md` (Tier 2)
- `src/bullshit_detector/leverage.py` → `skills/outlier_leverage.md` (Tier 3)
- `src/bullshit_detector/dc_cluster.py` → `skills/outlier_leverage.md` (Tier 3)
- `src/bullshit_detector/reproducibility.py` → `skills/reproducibility_challenge.md` (Tier 3)
- No code module → `skills/causal_consistency.md` (reasoning framework, not automatable)
- No code module → `skills/logical_fallacy.md` (fallacy checklist, supplements causal_consistency)
- No code module → `skills/fermi_sanity.md` (order-of-magnitude plausibility, normalization audit)

## Key constraints:
- Kalkomey functions are the package's unique value — these don't exist elsewhere
- A-GRIMMER is ported from Allard (2018) R code — validate against his test cases
- `grim` and `dcor` are dependencies; `statcheck` is GPL-3.0 — optional only
- Paper screening module (Tier 0) must carry full attribution to Bergstrom & West
- Fermi sanity skill (Tier 0) credits Niccoli (2026) framework and Weinstein estimation books
- Power and redundancy modules (Tier 2) credit Speidel (2018) GeoConvention R notebook
- All functions must have docstrings with references to source papers
- Tests must replicate known published results (Kalkomey tables, Allard examples)
