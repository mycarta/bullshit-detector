# Paper Screening Skill (Tier 0)

> Core worked examples to be written after code is stable.
> See paper_screening.py docstrings for API function descriptions.
> See Session_Handoff_05.md "paper_screening.py Implementation Notes" for API details.

## Non-statistical red flags (checklist — not automatable)

These supplement the API checks (journal, retraction, author) with human-judgment
heuristics. Sources: Bergstrom & West (2020), Seifert (2024), Cabanac et al. (2021).

**Conflict of interest signals:**
- Funding section mentions the company whose product is being studied
- Author affiliated with manufacturer of tested intervention
- COI statement absent or implausibly clean for industry-adjacent research

**Claims disproportionate to venue:**
- Revolutionary finding published in journal nobody's heard of
- Green coffee extract example: "near-miraculous weight loss" in unlisted Dove Press journal, n=16

**Paper mill / fabrication indicators:**
- "Tortured phrases" — AI-paraphrased text producing bizarre synonyms
  (e.g., "profound learning" for "deep learning"). See Cabanac et al. (2021),
  Problematic Paper Screener: https://www.irit.fr/~Guillaume.Cabanac/problematic-paper-screener/
- AI-generated text with oddly uniform style — Desaire et al. (2023) showed
  high-accuracy detection via stylometric analysis. External tools exist
  (GPTZero, Originality.ai) but reliability varies; treat as suggestive, not definitive
- Near-identical papers published with different author lists across journals —
  paper mill signature (Wittau et al. 2023)
- Papers previously offered for sale on paper mill websites (Abalkina 2023)
- Metadata anomalies: creation timestamps inconsistent with submission dates,
  author metadata mismatches (Sabel et al. 2023, Dadkhah et al. 2023)

**Peer review manipulation (visible to editors, not researchers):**
- Identical reviews from different reviewers → fake reviewer ring
- Multiple reviews submitted simultaneously for same paper
- Suggested reviewers with suspicious email domains
- (Abalkina & Bishop 2023; Day 2022)

**Publisher-side tools (not available to researchers, but good to know exist):**
- Springer Nature's Geppetto (AI-generated text detection) and SnappShot
  (gel/blot image duplication) screen submissions pre-publication. Not
  public, not open-source. Announced June 2024.
- STM Integrity Hub — cross-publisher collaborative tool. Also not public.
- Implication: papers in Springer Nature journals have been screened; papers
  in smaller publishers likely have not. Adjust scrutiny accordingly.

## ML explainability screening (Tier 0)

If the paper uses machine learning to make predictions or classifications,
check whether the authors report any explainability or interpretability
analysis. This is a screening check — you are not running SHAP yourself,
you are checking whether the authors did *anything* to open the black box.

### What to look for:

- Feature importance (any method: SHAP, permutation, impurity-based)
- Partial dependence or SHAP dependence plots
- Any discussion of *which* features drive predictions and *why*
- Physical or domain-based justification for the feature set used

### Red flags:

- ML model reported with accuracy/R² metrics only, no feature importance
  at all. The model might be fitting noise, and without explainability
  there is no way to tell from the paper alone.
- Feature importance reported but not discussed in domain terms. A ranked
  list of variable names without physical interpretation is decoration,
  not explanation.
- Large number of input features with no redundancy analysis. If 30
  seismic attributes went into a Random Forest with 50 wells, the
  spurious correlation risk is high regardless of reported accuracy.
  Route to `spurious.P_spurious()` and `redundancy.redundancy_analysis()`.

### What this does NOT catch:

This is a presence/absence check. A paper can report SHAP and still have
serious problems — implausible feature importance, SHAP used to claim
causation, redundant features splitting credit. Those are Tier 3 checks
covered in `outlier_leverage.md` (SHAP audit section).

### Verdict:

- **PASS** — Explainability analysis present and discussed in domain terms
- **CAUTION** — Explainability analysis present but superficial (ranked
  list without interpretation) or feature count is high relative to
  sample size
- **FLAG** — No explainability analysis reported for an ML model. Note
  in audit: "ML predictions reported without interpretability analysis.
  Cannot assess whether model relies on physically plausible features."

## What Tier 0 screening does NOT catch

Passing Tier 0 means the paper is published in a non-predatory journal,
has not been retracted, and the authors have verifiable credentials. It
does NOT mean the paper is good. Specifically:

- **Methodological flaws within a legitimate journal.** Nature, PNAS, and
  The Lancet have all published deeply flawed studies. Journal legitimacy
  is necessary but not sufficient.
- **Statistical errors.** Tier 0 does not check any numbers. A paper with
  impossible means, fabricated p-values, or 10% power sails through.
  Route to Tier 1 and Tier 2.
- **Salami slicing / redundant publication.** The same dataset published
  as multiple papers with minor variations. Requires cross-referencing
  author publication lists, not just checking one paper.
- **Undisclosed conflicts of interest.** The screening checks declared
  COI and funding sources. If the COI is not declared, Tier 0 cannot
  find it. Look for industry affiliations in author addresses and
  acknowledgments.
- **Ghost authorship.** OpenAlex shows who is listed. It cannot detect
  who should be listed but isn't, or who is listed but didn't contribute.
- **Predatory journal gray areas.** Binary lists (DOAJ yes/no) miss
  journals that are technically indexed but have negligible review
  standards. If in doubt, check acceptance rates and editorial board
  composition manually.

## References

- Abalkina (2023), identification of papers offered for sale by paper mills
- Abalkina & Bishop (2023), fake reviewer detection
- Bergstrom & West (2020), *Calling Bullshit*, Random House — paper legitimacy framework
- Cabanac, Labbé & Magazinov (2021), "Tortured phrases" detection
- Dadkhah et al. (2023), metadata-based fake paper indicators
- Desaire et al. (2023a, 2023b), AI-generated text detection via writing style
- Sabel et al. (2023), anomaly-based detection features
- Seifert (2021a), metadata anomalies in fake papers
- Wittau et al. (2023), duplicate submissions with different author lists
- Wittau & Seifert (2023), additional metadata indicators
