# Unreleased Changes

_Current PyPI version: 0.1.1_
_Last updated: 5 March 2026 (Session 14)_

---

## Skill file edits (ready to apply)

Source files on `P:\Bullshit detector\` and `/mnt/user-data/outputs/`.

- [x] `skills/outlier_leverage.md` — SHAP/XAI audit section ✓
- [x] `paper_screening.md` — ML explainability screening note ✓
- [x] All code-backed skill files — add "Not covered" sections declaring blind spots ✓

## Skill files to fill (currently partial or placeholder)

- [x] `skills/spurious_correlation.md` — expanded with Kalkomey tables, Hunt worked example, red flags, "not covered" section ✓
- [x] `skills/power_analysis.md` — expanded with Button et al., Speidel geoscience, SD/SE trap worked examples ✓
- [ ] `skills/redundancy_analysis.md` — 5 lines, placeholder, needs Speidel methodology writeup
- [ ] `skills/reproducibility_challenge.md` — 5 lines, placeholder, needs Notebook D/E methodology writeup

## New skill files (not yet written)

- [x] `unsupervised_learning_critique.md` — cluster reification, centroid vs medoid, stability, dimensionality reduction as evidence. Worked example: Ahlqvist (2018). ✓
- [ ] Variable handling critique — dichotomisation of continuous predictors, median splits lose 38-60% power, inflate type I error. Test case: Royston, Altman & Sauerbrei (2006). Reasoning-only agent, no code module needed. From Thomas Speidel's test cases.

## Packaging / infrastructure

- [ ] Fix license field in `pyproject.toml` — switch from deprecated TOML table format to SPDX string. Deadline: Feb 2027. setuptools warns but builds fine for now.
- [ ] PyPI old account recovery — transfer `bullshit-detector` ownership when resolved. Ticket: https://github.com/pypi/support/issues/

## Example scripts

- [ ] Anscombe's quartet demo — run `influence_plot()` (flags the outlier in Set III), `distance_correlation_test()` (catches nonlinearity in Set II). Fun example script or blog post material.

## OVERVIEW.md update

- [ ] Add Fermi sanity check between Tier 0 paper screening and Tier 1 p-value recomputation in decision tree (noted in Session_Handoff_10, not yet applied to repo copy)
- [ ] Add SHAP audit branch under Tier 3 in decision tree

## README updates

- [ ] Add SHAP/XAI mention to capabilities list after skill file edit lands

---

## When ready, release as: 0.2.0

Batch all skill file edits + filled placeholders into a single release.

```bash
# After all changes committed:
# 1. Update version in pyproject.toml to 0.2.0
# 2. Build and publish
python -m build
twine check dist/bullshit_detector-0.2.0*
twine upload dist/bullshit_detector-0.2.0*

# 3. Commit version bump
git add pyproject.toml UNRELEASED.md
git commit -m "Release v0.2.0 — skill file expansion, SHAP audit, filled placeholders"
git push origin main

# 4. Clear completed items from this file, keep remaining items
```

---

## Not in this release (future milestones)

These live here as reminders but don't block 0.2.0:

- SLM multi-agent architecture (see `multi_agent_architecture.md`)
- Gradio frontend
- PDF extraction via Landing AI ADE
- Evaluation against Thomas Speidel's 8 test papers
- Blog posts: "Inverting Mill's Methods", "bullshit-detector launch post", Fermi sanity skill, "Distributed Bullshit Detection: Small Models as Specialized Auditors"
- Announce: LinkedIn, Software Underground Mattermost, r/Python
