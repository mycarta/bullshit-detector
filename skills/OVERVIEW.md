# Bullshit Detector — Skills Overview

## When to use which module

```
Is this paper even worth reading carefully?
│
├─ Check journal legitimacy ──→ paper_screening.check_journal()
├─ Check for retractions ─────→ paper_screening.check_retraction()
├─ Check author credentials ──→ paper_screening.check_author()
│
│  If paper passes screening, do a sanity check on headline claims:
│
Does the headline claim survive back-of-envelope reasoning?
├─ Decompose into sub-quantities → magnitude plausible? → skills/fermi_sanity.md
├─ What denominator is used? → appropriate for the question asked?
├─ Key numbers: KNOWN, BOUNDED, or ASSERTED without justification?
├─ Uncertainty bounds: physically motivated or cosmetic?
│  Fail any check → flag before proceeding to statistics
│
│  If paper passes Tier 0, proceed to statistics:
│
Does the paper report test statistics (t, F, r, χ², z)?
├─ Yes → p_checker.check_p_value()
│
Does it report means/SDs from integer scales (Likert, counts)?
├─ Means → use `grim` package directly
├─ Means + SDs → grimmer.a_grimmer()
│
Does the paper report correlations from small samples?
├─ How many variables were tested?
│  ├─ Reported → spurious.P_spurious(r, n, k)
│  └─ Not reported → Flag: "How many comparisons were possible?"
├─ Is r above the critical threshold? → spurious.r_crit(n)
├─ Does the CI for r cross zero? → spurious.conf_int(r, n)
├─ Are prediction intervals shown, or only CIs? → Skill checklist
│
Are the reported predictors actually independent?
├─ redundancy.redundancy_analysis() → effective_k
│  Feed effective_k into spurious.P_spurious()
│
Was the study adequately powered to detect its claimed effect?
├─ power.achieved_power(effect_size, n_per_group)
│  Power < 0.50 → finding is suspect
│  Power < 0.80 → interpret with extra caution
├─ How many samples would they have needed?
│  → power.required_n(effect_size, alpha, power)
│
Does the paper make causal claims? (X causes Y, X predicts Y)
├─ Work through Mill's Methods checklist → skills/causal_consistency.md
│  1. Agreement — is the cause present in ALL positive cases?
│  2. Difference — does the cause distinguish positive from negative?
│  3. Joint — is perfect discrimination suspicious given n?
│  4. Residues — does the effect only appear after heavy covariate adjustment?
│  5. Concomitant Variation — does dose-response hold across the full range?
│  These checks require careful reading, not just numbers.
│  Use statistical modules to quantify what Mill's Methods surface.
│
Paper passes Mill's Methods but argument still feels off?
├─ Scan logical fallacy checklist → skills/logical_fallacy.md
│  Focus on: Equivocation (terms shifting meaning across sections),
│  Circular Reasoning (predictor ≈ outcome by definition),
│  False Dilemma, language escalation in Discussion.
│
Do you have access to the actual data (or can extract from figures)?
├─ Were data points dropped to improve fit?
│  → leverage.influence_plot() + leverage.distance_correlation_test()
├─ Are the reported variables actually independent?
│  → dc_cluster.effective_k() → feed into spurious.P_spurious()
├─ Can you challenge a qualitative claim quantitatively?
│  → reproducibility.error_flag() + reproducibility.bootstrap_proportion()
```

## Tier summary

| Tier | What you need | Module | Effort |
|------|---------------|--------|--------|
| 0 | DOI, journal name, author name | paper_screening | Minutes |
| 0 | Headline claim, key numbers | fermi_sanity (skill file) | Minutes |
| 1 | Reported statistics from paper text | p_checker, grimmer | Minutes |
| 2 | Reported summary stats (r, n, k) | spurious | Minutes |
| 2 | Claimed effect size + sample size | power | Minutes |
| 2 | Multiple predictor variables (data) | redundancy | Minutes |
| 3 | Raw data or digitized figures | leverage, dc_cluster, reproducibility | Hours |

## Key principle

Each tier is a gate. Fail early, save effort. Don't dig into Tier 3
data analysis if Tier 0 shows the journal is predatory or the paper
has been retracted.
