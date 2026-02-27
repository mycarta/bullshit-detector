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
