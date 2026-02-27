# Bullshit Detector — Build Guide

_For future Matteo picking this up between sessions._
_Created: 19 Feb 2026_
_Last updated: 19 Feb 2026_

---

## How this repo is set up

The scaffold is complete. Every `.py` file has:
- Full module docstring with attribution and references
- Function signatures with typed parameters
- Detailed docstrings with algorithm descriptions, examples, and test cases
- `raise NotImplementedError(...)` with specific instructions

Exception: **`p_checker.py` is fully implemented** — it was simple enough to do in the scaffold. You can run its tests immediately.

The `skills/` files are placeholders. Write them after the code is stable.

---

## How to work on this

**Open VS Code. Open a Copilot chat. Attach the relevant file(s).**

Each task below is self-contained. You can do them in any order (though the suggested order builds from easy to hard). Each task has:
- What to do
- What files to attach in Copilot chat  
- What to tell Copilot
- How to verify it worked

**Model choice:** Sonnet for all module implementations. Opus if you want to write skill files or make architectural changes.

---

## TODO List

Check off items as you complete them. Each is one Copilot chat session.

### Phase 1 — Core functions (do these first)

- [ ] **1.1 Verify scaffold works**
  - Run: `pip install -e ".[dev]"` from the repo root
  - Run: `pytest tests/test_p_checker.py -v`
  - Expected: p_checker tests pass (it's fully implemented)
  - If anything fails, fix the packaging before proceeding

- [ ] **1.2 Implement `spurious.py` — P_spurious, r_crit, conf_int**
  - _This is the package's unique value. Prioritize it._
  - Attach in Copilot: `src/bullshit_detector/spurious.py`, `tests/test_spurious.py`
  - Tell Copilot: "Implement the three functions in spurious.py. The algorithms are described in the docstrings. P_spurious uses the t-distribution to compute p_sc, then applies 1-(1-p_sc)^k. r_crit uses the inverse t-distribution. conf_int uses Fisher Z-transform. All scipy.stats. Remove the @skip decorators from tests and make them pass."
  - Verify: `pytest tests/test_spurious.py -v` — all tests pass
  - Extra credit: add a test replicating Kalkomey Table 1 values

- [ ] **1.3 Implement `grimmer.py` — a_grimmer()**
  - _First Python A-GRIMMER on PyPI._
  - Attach in Copilot: `src/bullshit_detector/grimmer.py`, `tests/test_grimmer.py`
  - Tell Copilot: "Port the Allard (2018) R function to Python. The R source is at https://aurelienallard.netlify.app/post/anaytic-grimmer-possibility-standard-deviations/ — fetch it and translate. The algorithm is described in the module docstring. Use math.ceil/math.floor. Handle the .5 rounding ambiguity with both round-up and round-down. Remove @skip decorators and make tests pass."
  - Verify: `pytest tests/test_grimmer.py -v`
  - Key test: `a_grimmer(n=18, mean=3.44, sd=2.47)` → result contains "GRIMMER inconsistent"

### Phase 2 — API wrappers and Tier 2 tools

- [ ] **2.1 Implement `paper_screening.py` — check_journal()**
  - Attach: `src/bullshit_detector/paper_screening.py`, `tests/test_paper_screening.py`
  - Tell Copilot: "Implement check_journal(). Query DOAJ API at https://doaj.org/api/search/journals/{query} and OpenAlex at https://api.openalex.org/sources?search={name}. Return the dict described in the docstring. Preserve the full Bergstrom & West attribution in the module docstring."
  - Verify: `pytest tests/test_paper_screening.py::TestCheckJournal -v` (needs internet)

- [ ] **2.2 Implement `paper_screening.py` — check_retraction()**
  - Attach: same files
  - Tell Copilot: "Implement check_retraction(). Use CrossRef API at https://api.crossref.org/works/{doi} — check the update-to field for retractions. Also query PubPeer at https://pubpeer.com/api/ for commentary."
  - Verify: test with known retracted DOI

- [ ] **2.3 Implement `paper_screening.py` — check_author()**
  - Attach: same files
  - Tell Copilot: "Implement check_author(). Use OpenAlex API at https://api.openalex.org/authors?search={name}. If ORCID provided, use it for disambiguation. Return works_count, h_index, institution, top_fields."
  - Verify: `pytest tests/test_paper_screening.py::TestCheckAuthor -v`

- [ ] **2.4 Implement `power.py` — required_n() and achieved_power()**
  - _"Was this study adequately powered?" — the question you always wanted to ask._
  - Attach: `src/bullshit_detector/power.py`, `tests/test_power.py`
  - Tell Copilot: "Implement required_n() and achieved_power(). The formulas are in the docstrings. Use scipy.stats.norm.ppf for Z-values. Handle both equal variance (pooled sd) and unequal variance (sd1, sd2) cases. For unequal variance: n = ((z_alpha + z_beta)^2 * (sd1^2 + sd2^2)) / d^2. Key test: Speidel's example d=16, sd1=16, sd2=12, alpha=0.10, power=0.80 → n≈11 per group."
  - Verify: `pytest tests/test_power.py -v`
  - Optional: also implement power_curve() for plotting

- [ ] **2.5 Implement `redundancy.py` — redundancy_analysis()**
  - _Python equivalent of Harrell's Hmisc::redun()._
  - Attach: `src/bullshit_detector/redundancy.py`, `tests/test_redundancy.py`
  - Tell Copilot: "Implement redundancy_analysis(). For each column in the DataFrame, fit an OLS model using all other columns as predictors (sklearn LinearRegression). Record R². Flag columns with R² > threshold as redundant. Return dict with r_squared, redundant list, retained list, effective_k. Speidel's R result with r2=0.70 on Hunt data: gross.pay and gross.pay.transform were flagged as redundant."
  - Verify: `pytest tests/test_redundancy.py -v`
  - Note: needs the Hunt dataset CSV for integration testing

### Phase 3 — Tier 3 tools (need notebook source code)

_These require extracting functions from your Jupyter notebooks.
Open the notebook, find the function, paste it into Copilot chat._

- [ ] **3.1 Implement `leverage.py` — influence_plot()**
  - Source: Notebook E (`Be-a-geoscience-detective_example_2.ipynb`)
  - Attach: `src/bullshit_detector/leverage.py`
  - You'll need to: open Notebook E, find the influence plot cell, paste the code into Copilot and ask it to wrap as a function
  
- [ ] **3.2 Implement `leverage.py` — distance_correlation_test()**
  - Source: Notebook E
  - Simple wrapper around `dcor.independence.distance_covariance_test`

- [ ] **3.3 Implement `dc_cluster.py` — dist_corr(), dc_matrix(), effective_k()**
  - Source: Notebook F (distance correlation blog post notebook)
  - `dist_corr` and `dc_matrix` are near-direct extractions
  - `effective_k` needs: build DC matrix → hierarchical clustering → count clusters

- [ ] **3.4 Implement `reproducibility.py` — error_flag(), bootstrap_proportion()**
  - Source: Notebook D (`Be-a-geoscience-detective.ipynb`)
  - Open notebook, find the functions, extract

### Phase 4 — Documentation and polish

- [ ] **4.1 Write `skills/OVERVIEW.md`** — already has a decision tree, flesh it out with worked examples once functions exist
- [ ] **4.2 Write `skills/paper_screening.md`** — Bergstrom & West checklist + API usage examples
- [ ] **4.3 Write `skills/spurious_correlation.md`** — Kalkomey framework + notebook examples
- [ ] **4.4 Write `skills/arithmetic_consistency.md`** — GRIM/GRIMMER/p-checker workflow
- [ ] **4.5 Write `skills/outlier_leverage.md`** — Cook's distance + dcor workflow
- [ ] **4.6 Write `skills/power_analysis.md`** — sample size + power screening workflow
- [ ] **4.7 Write `skills/redundancy_analysis.md`** — variable redundancy + effective-k workflow
- [ ] **4.8 Write `skills/causal_consistency.md`** — DONE (Mill's Methods inverted). Expand
  Wilrich worked example with specifics from blog post.
- [ ] **4.9 Write `skills/reproducibility_challenge.md`** — error_flag + bootstrap workflow
- [ ] **4.9 Write examples/** — standalone scripts showing each module in action.
  Include cross-domain examples to broaden audience beyond geoscience:
  - `examples/kalkomey_screening.py` — reproduce Kalkomey Tables 1, 3 (geoscience)
  - `examples/hunt_dataset.py` — Hunt (2013) 21-well decision framework (geoscience)
  - `examples/outlier_leverage.py` — Close et al. (2010) worked example (geoscience)
  - `examples/grim_check.py` — Wansink "pizzagate" example (psychology/social science)
  - `examples/green_coffee.py` — Bergstrom & West green coffee extract paper: Tier 0
    journal + retraction + author checks (nutrition/biomedical)
  - `examples/underpowered_study.py` — Button et al. (2013) neuroscience power analysis:
    median power ~21%, show achieved_power() on their reported numbers (biomedical)
  - `examples/sd_vs_se.py` — Sainani's finding that 45% of highly cited strength &
    conditioning meta-analyses used SE instead of SD, producing effect sizes of 11–14
    standard deviations. Use check_p_value() or a simple plausibility check (sports science)
- [ ] **4.10 Final README review** — update Quick Start with real outputs

### Phase 5 — Release

- [ ] **5.1 Run full test suite:** `pytest tests/ -v`
- [ ] **5.2 Create GitHub repo:** `mycarta/bullshit-detector`
- [ ] **5.3 Push scaffold + completed modules**
- [ ] **5.4 Test PyPI upload:** `pip install build && python -m build && twine check dist/*`
- [ ] **5.5 Publish to PyPI** (when ready)
- [ ] **5.6 Blog post on MyCarta** about the package

---

## Future directions

Ideas that don't belong in v0.1 but are worth tracking.

- [ ] **Image forensics skill file** — `skills/image_forensics.md`. Checklist (not code) for when you suspect figure manipulation: duplicated Western blots, suspiciously smooth histograms, copy-move artifacts. Points to external tools: PhotoHolmes (Python CLI, https://github.com/photoholmes/photoholmes), Ghiro, FotoForensics, ImageMagick ELA. PhotoHolmes is a full deep learning pipeline (10 methods, PyTorch, GPU) — too heavy to wrap as a dependency, but the right tool to recommend. See O'Flaherty et al. (2024), arXiv:2412.14969.
- [ ] **EXIF/metadata consistency** — lightweight check: do all figures in a paper come from the same camera/software? Are timestamps consistent? A few lines of `Pillow` + `piexif`. The one automatable piece of image forensics that could live in the package without a deep learning stack.
- [ ] **LLM-powered causal audit pipeline** — use an LLM to extract claims, cases, and evidence from paper text, then run the Mill's Methods checks from `skills/causal_consistency.md` programmatically. The skill file is the reasoning scaffold; the extraction step is the hard part. Would turn the checklist into an automated (or semi-automated) audit tool.
- [ ] **Misleading axes / proportional ink** — decided in Session 05 this is 100% human-eye detection, not automatable. Skill file checklist only, referencing Bergstrom & West's visual bullshit examples.
- [ ] **Wilson score interval** — evaluated and left out in Session 05 (standard scipy, no unique value). Revisit if a use case emerges.

---

## Reference files

If you need to look things up between sessions:

| What | Where |
|------|-------|
| Full project plan, all implementation notes | `Session_Handoff_05.md` (in your Claude.ai project) |
| Allard A-GRIMMER R source code | https://aurelienallard.netlify.app/post/anaytic-grimmer-possibility-standard-deviations/ |
| Bergstrom & West paper screening | https://callingbullshit.org/tools/tools_legit.html |
| Your distance correlation blog post | https://mycartablog.com/2019/04/10/data-exploration-in-python-distance-correlation-and-variable-clustering/ |
| DOAJ API docs | https://doaj.org/api/ |
| OpenAlex API docs | https://docs.openalex.org/ |
| CrossRef API docs | https://api.crossref.org/ |
| `grim` PyPI package | https://github.com/phoughton/grim_test |
| `dcor` library | https://github.com/vnmabus/dcor |
| Notebook A (P_spurious, r_crit, confInt) | `mycarta/Data-science-tools-petroleum-exploration-and-production` |
| Notebook B (decision framework) | `mycarta/predict` |
| Notebook D (error_flag, bootstrap) | `mycarta/Be-a-geoscience-detective` |
| Notebook E (influence plot, dcor) | `mycarta/Be-a-geoscience-detective` (example 2) |
| Notebook F (DC clustering) | `mycarta/Niccoli_Speidel_2018_Geoconvention` |
| Thomas Speidel's R notebook (redundancy, LASSO, power) | `mycarta/Data-science-tools-petroleum-exploration-and-production/R/geoconference_2018.Rmd` |

---

## Tips for returning after a break

1. Read this file first
2. Check which boxes are checked — that's where you left off
3. Each task is one Copilot chat — no need to remember context
4. The stub files contain everything Copilot needs in their docstrings
5. If something doesn't work, the `Session_Handoff_05.md` in your Claude.ai project has the full backstory and implementation notes
