# Audit: Al-Lamee et al. (2018) — ORBITA Trial

**Paper:** Al-Lamee, R., Thompson, D., Dehbi, H.-M., et al. (2018).
"Percutaneous coronary intervention in stable angina (ORBITA): a
double-blind, randomised controlled trial." *The Lancet*, 391, 31–40.

**Known ground truth:** Adequately powered for its design target
(30 s, SD 75 s → power 0.81) but observed effect was smaller than
anticipated. Confidence interval compatible with clinically meaningful
benefit, widely misinterpreted as "PCI doesn't work for angina."
ORBITA-2 (2023, N=301, no background antianginals) later showed PCI
does improve angina symptoms vs placebo (OR 2.21, p<0.001).

**Modules applied:** `power.achieved_power()`, `power.required_n()`,
`spurious.conf_int()` (CI interpretation), Fermi sanity check

---

## Extracted statistics

**Design:** 200 patients randomized (105 PCI, 95 placebo), single-vessel
stenosis ≥70%, 6 weeks medication optimization pre-randomization,
6-week blinded follow-up. Placebo = sham catheterization procedure.

**Primary endpoint:** Exercise time increment (PCI vs placebo)

| Measure | Value |
|---------|-------|
| PCI minus placebo | 16.6 s |
| 95% CI | (−8.9, 42.0) |
| p-value | 0.200 |
| PCI group increase | 28.4 s (CI: 11.6 to 45.1) |
| Placebo group increase | 11.8 s (CI: −7.8 to 31.3) |

**Design target:** 30 s effect, SD 75 s (from protocol).

**Derived quantities:**
- SE = 12.98 s (from CI width)
- SD from CI = 91.7 s (higher than protocol assumption)
- Cohen's d (observed, protocol SD) = 16.6 / 75 = 0.221 (small)
- Cohen's d (design target, protocol SD) = 30 / 75 = 0.400 (small-to-medium)

**Significant secondary outcome:** Dobutamine stress echocardiography
wall motion index: PCI −0.08 (CI: −0.11 to −0.04) vs placebo +0.02
(CI: −0.03 to +0.06), p = 0.0011. PCI objectively reduced ischemia.

---

## Power analysis screening

```
from bullshit_detector.power import achieved_power, required_n
```

**CORRECTION (10 March 2026):** The original version of this audit
used the observed effect size in the power calculation. As correctly
pointed out by a LinkedIn commenter, power should be assessed using
the design target (the effect size the trial was planned to detect),
not the post-hoc observed estimate. Using the observed effect is
circular: every negative trial has a small observed effect, so every
negative trial would appear underpowered.

### Power at design parameters (SD = 75 s from protocol)

| Scenario | Cohen's d | Power (n=100/group) | Required n (80%) | Verdict |
|----------|-----------|--------------------|--------------------|---------|
| Design target (30 s / 75 s) | 0.400 | **0.807** | 99/group (198 total) | **ADEQUATE** |
| Observed effect (16.6 s / 75 s) | 0.221 | 0.347 | 321/group (642 total) | Post-hoc only |
| Clinical benchmark (45 s / 75 s) | 0.600 | 0.989 | 44/group (88 total) | Adequate |

All Cohen's d values use the protocol SD of 75 s. The CI-derived
SD of 91.7 s reflects real-world variability (which was higher than
anticipated), but power analysis for design assessment should use the
assumptions that informed the sample size calculation.

**Interpretation:** Using the design parameters from the ORBITA
protocol, the trial had 0.81 power — adequately powered for what it
set out to detect. The required n was 99 per group; they had 100.
No design shortfall.

The "observed effect" row (0.35 power) is shown for reference only.
It answers a different question: "could this trial have detected what
it found?" That is useful for understanding why the result was non-
significant, but it is NOT evidence that the trial was poorly designed.

### What this means for the package

`achieved_power()` is a correct function. The error was in the input,
not the code. The skill file (`power_analysis.md`) should be updated
to explicitly warn: "Use the design-stage effect size and SD when
assessing whether a trial was adequately planned. Use the observed
effect size only when asking whether the trial could have detected
what it found — and label this clearly as a post-hoc calculation."

---

## Confidence interval interpretation

The primary endpoint CI of (−8.9, 42.0) is the critical diagnostic:

- **Crosses zero:** Yes — cannot exclude no effect
- **Compatible with no effect:** Yes
- **Compatible with meaningful benefit (≥30 s):** Yes (upper bound 42.0)
- **Compatible with clinically important harm:** No (lower bound only −8.9)

**This is the audit's key finding.** A non-significant p-value does
not mean "no effect." It means "we cannot tell." The CI for ORBITA
is consistent with PCI providing anywhere from a trivial 9-second
decrement to a 42-second improvement. The 42-second upper bound
approaches the effect of a single antianginal drug.

Gelman & Stern (2006): "The difference between significant and
not significant is not itself statistically significant." ORBITA's
p=0.20 does not establish absence of effect — it establishes
insufficient evidence to distinguish effect from noise.

---

## Fermi sanity check

**Question:** Is the observed 16.6 s improvement physically plausible?

| Benchmark | Improvement | ORBITA as % |
|-----------|-------------|-------------|
| Single antianginal drug vs placebo | >45 s | 37% |
| Unblinded PCI vs medical therapy | ~96 s | 17% |
| ORBITA PCI vs sham | 16.6 s | — |

The 16.6 s figure is plausible as the **physical component** of PCI
benefit after subtracting the placebo effect. Unblinded trials showed
~96 s; if roughly 80% of that was placebo/expectation, the physical
component would be ~19 s — close to what ORBITA observed.

**Verdict: PLAUSIBLE.** The observed effect size is physically
reasonable. The true effect may be real but smaller than the 30 s
design target, which is why the trial could not resolve it.

---

## What the package catches vs. the common misinterpretation

**Common media/clinical interpretation:** "ORBITA showed PCI doesn't
work for angina."

**What the package shows:**
1. The trial was adequately powered for its design target (0.81) —
   no design flaw
2. The CI is compatible with a benefit nearly as large as a drug
   (up to 42 s)
3. The non-significant p-value means "insufficient evidence," not
   "no effect"
4. The objective ischemia endpoint (stress echo) was significant —
   PCI does reduce ischemia
5. The Fermi check shows the observed effect size is physically
   plausible, not implausibly small
6. The true effect appears smaller than the design target — a
   larger trial was needed to resolve it, which is exactly what
   ORBITA-2 did

**Correct interpretation:** ORBITA demonstrates that most of the
symptomatic benefit patients experience from PCI is a placebo effect.
It does NOT demonstrate that PCI has zero physical benefit. The CI
leaves the door open for meaningful benefit — which ORBITA-2 (2023)
subsequently confirmed.

---

## Red flags checklist

**From power_analysis.md:**
- ☐ Power adequate for design target (0.81) — no design flaw
- ☑ Non-significant result interpreted as "no effect" rather than
  "insufficient evidence"
- ☑ Observed effect smaller than design target — trial could not
  resolve whether the smaller effect is real

**From spurious_correlation.md (CI interpretation):**
- ☑ Wide CI crossing zero but also including clinically meaningful
  benefit
- ☑ p-value reported without CI context in many commentaries

**From fermi_sanity.md:**
- ☐ Effect size is physically plausible (no Fermi flag)

---

## Verdict

| Check | Result |
|-------|--------|
| Power (design target, SD=75s) | **ADEQUATE** (0.81) |
| Power (observed effect, post-hoc) | 0.35 (not a design flaw) |
| Power (clinical benchmark 45s) | Adequate (0.99) |
| CI crosses zero | YES |
| CI includes meaningful benefit | **YES** (up to 42 s) |
| Fermi plausibility | PASS |
| Objective outcome (stress echo) | SIGNIFICANT (p=0.001) |

**Overall: CAUTION — interpret with nuance.** The trial is well-
designed (blinded, sham-controlled, pre-registered) and adequately
powered for its design target. The non-significant result on the
primary endpoint is correctly reported but widely over-interpreted.
The CI ambiguity — compatible with both no effect and clinically
meaningful benefit — is the real finding, not the p-value.

This is a different failure mode from Carney et al. (2010): that
paper found significance it shouldn't have trusted (underpowered +
multiple comparisons → likely false positive). ORBITA failed to find
significance it might have found with more patients — not because the
design was flawed, but because the true effect was smaller than
anticipated. Both illustrate why power matters; the consequences
point in opposite directions.

---

## What the package caught vs. what it missed

**Caught:**
- CI compatible with meaningful benefit (not just zero)
- Fermi-plausible effect size
- The "significant vs not significant" trap
- Objective ischemia outcome was significant despite primary being null

**Misapplied in original audit (corrected 10 March 2026):**
- Used observed effect size and CI-derived SD in power calculation
  instead of design-stage assumptions — made the trial appear
  underpowered when it was not. The function `achieved_power()` is
  correct; the input was wrong. Lesson: always use design-stage
  assumptions for design assessment.

**Not caught (requires information beyond the paper's statistics):**
- The medication optimization protocol may have reduced the
  detectable PCI benefit (both arms optimized on drugs first)
- 6-week follow-up may be too short for full PCI benefit
- Single-vessel disease only — results may not generalize to
  multi-vessel disease
- Change-from-baseline methodology (Harrell's critique: should have
  used covariate-adjusted follow-up, not change scores)
- ORBITA-2 redesigned to address these issues (no background
  antianginals, longer follow-up, Harrell as co-author)
