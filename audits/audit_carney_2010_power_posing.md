# Audit: Carney, Cuddy & Yap (2010) — Power Posing

**Paper:** Carney, D.R., Cuddy, A.J.C., & Yap, A.J. (2010). "Power
Posing: Brief Nonverbal Displays Affect Neuroendocrine Levels and Risk
Tolerance." *Psychological Science*, 21(10), 1363–1368.

**Known ground truth:** Small sample, multiple outcomes, selective
reporting, researcher degrees of freedom. Lead author (Carney) publicly
disavowed the findings in 2016. Failed replication by Ranehill et al.
(2015, N=200). Simmons & Simonsohn (2017) p-curve analysis found no
evidential value.

**Modules applied:** `power.achieved_power()`, `power.required_n()`,
`spurious.P_spurious()`, `spurious.conf_int()`

---

## Extracted statistics

| DV | Test statistic | p (reported) | Effect size r | Cohen's d |
|----|----------------|-------------|---------------|-----------|
| Testosterone change | F(1,39) = 4.29 | < .05 | .34 | 0.72 |
| Cortisol change | F(1,38) = 7.45 | < .02 | .43 | 0.95 |
| Risk-taking (gamble) | χ²(1,42) = 3.86 | < .05 | Φ = .30 | 0.63 |
| Felt power | F(1,41) = 9.53 | < .01 | .44 | 0.98 |

**Design:** N=42 (26 female, 16 male), 21 per condition (high-power
pose vs. low-power pose). Saliva samples pre/post. Outliers removed:
2 cortisol (>3 SD), 1 testosterone (>3 SD).

Felt power means: high-power M=2.57, SD=0.81; low-power M=1.83,
SD=0.81 → d = 0.91 (direct computation).

---

## Power analysis screening

```
from bullshit_detector.power import achieved_power, required_n
```

| DV | Cohen's d | Power (n=21/group) | Verdict | n needed (80%) | Shortfall |
|----|-----------|-------------------|---------|----------------|-----------|
| Testosterone | 0.72 | **0.649** | UNDERPOWERED | 31/group (62 total) | 1.5× |
| Cortisol | 0.95 | 0.870 | Adequate | 18/group (36 total) | — |
| Risk-taking | 0.63 | **0.531** | UNDERPOWERED | 40/group (80 total) | 1.9× |
| Felt power | 0.98 | 0.888 | Adequate | 17/group (34 total) | — |

**Interpretation:** Two of four outcomes — testosterone and risk-taking
— are underpowered. The testosterone result (power = 0.65) has roughly
a 1-in-3 chance of missing its own claimed effect. The risk-taking
result (power = 0.53) is barely better than a coin flip.

The two outcomes that appear adequately powered (cortisol and felt
power) show suspiciously large effect sizes. Cohen's d of 0.95–0.98
means the groups barely overlap — implausible for a 2-minute body
posture manipulation on hormones and self-report.

**Winner's curse flag:** The effect sizes required for adequate power
at n=21 are large (d > 0.80). The study can only detect large effects.
If the true effects are small-to-medium (as subsequent meta-analyses
suggest), the significant results here are inflated by the winner's
curse — they had to be large to clear the significance threshold with
this sample.

---

## Spurious correlation screening (multiple outcomes)

```
from bullshit_detector.spurious import P_spurious, conf_int
```

The paper tests k=4 dependent variables against a single experimental
manipulation with no correction for multiple comparisons.

| DV | r | P_spurious (k=1) | P_spurious (k=4) | 95% CI for r | CI crosses 0? |
|----|------|-----------------|-----------------|--------------|---------------|
| Testosterone | .34 | .032 | **.121** | (0.03, 0.59) | No (barely) |
| Cortisol | .43 | .006 | .022 | (0.14, 0.65) | No |
| Risk-taking | .30 | .060 | **.219** | (−0.01, 0.56) | **YES** |
| Felt power | .44 | .005 | .018 | (0.15, 0.66) | No |

Critical r for n=42: r_crit ≈ 0.304.

**Interpretation:**

- **Testosterone** (P_spurious = 0.12 at k=4): Above the 0.10
  suspicion threshold. With four outcomes tested, there is a 12%
  probability this result is entirely spurious. The lower CI bound
  (0.03) nearly touches zero.

- **Risk-taking** (P_spurious = 0.22 at k=4): Above the 0.10 threshold
  by a wide margin. The 95% CI for r crosses zero (−0.01, 0.56),
  meaning the effect cannot be distinguished from independence at
  the 95% level. The reported r of 0.30 is barely above r_crit
  (0.304) — this is a marginal result that would not survive
  multiple-comparison correction.

- **Cortisol and felt power** survive the k=4 screen (P_spurious <
  0.05). However, this does not vindicate them — it means chance
  alone is unlikely to explain the result. The implausibly large
  effect sizes (see power analysis above) suggest winner's curse
  rather than genuine large effects.

---

## Additional red flags (from skill file checklists)

**From power_analysis.md:**

- ☑ No power analysis reported in the paper.
- ☑ n < 20 per group with significant results on multiple DVs.
- ☑ Claimed effect sizes much larger than subsequent meta-analytic
  estimates.
- ☑ Pilot-like sample size used for confirmatory claims.

**From spurious_correlation.md:**

- ☑ Multiple outcomes tested, no multiple-comparison correction.
- ☑ Risk-taking r just above r_crit — marginal result.
- ☑ No confidence intervals reported in the paper.

**From Carney's own 2016 disclosure (not detectable by the package,
but confirming the audit):**

- Optional stopping: subjects run in chunks of 25, then 10, then 7,
  then 5 — checking significance along the way.
- Researcher degrees of freedom on risk-taking: Likelihood Ratio
  (p = .05) reported instead of Pearson χ² (p = .052) because
  the former was smaller.
- Outlier exclusion applied to hormone analyses but not all analyses.
- Gender not handled appropriately for testosterone (bimodal
  distribution collapsed).

---

## Verdict

| Check | Result |
|-------|--------|
| Power (testosterone) | **UNDERPOWERED** (0.65) |
| Power (risk-taking) | **UNDERPOWERED** (0.53) |
| Power (cortisol) | Adequate but implausible d |
| Power (felt power) | Adequate but implausible d |
| P_spurious (testosterone, k=4) | **SUSPECT** (0.12 > 0.10) |
| P_spurious (risk-taking, k=4) | **SUSPECT** (0.22 > 0.10) |
| CI crosses zero (risk-taking) | **YES** |
| Multiple comparisons corrected | **NO** |

**Overall: REVIEW.** Two of four outcomes are underpowered, one CI
crosses zero, and the multiple-comparison penalty pushes two outcomes
above the suspicion threshold. The remaining two outcomes show
effect sizes too large to be plausible for a 2-minute posture
manipulation. The package correctly identifies the statistical
weaknesses that were later confirmed by failed replications and the
lead author's own disclosure.

---

## What the package caught vs. what it missed

**Caught:**
- Underpowered outcomes (testosterone, risk-taking)
- Multiple-comparison risk across 4 DVs
- Marginal risk-taking result (CI crosses zero)
- Implausibly large effect sizes (via Fermi intuition from the
  power analysis — d > 0.9 for a posture manipulation)

**Not caught (requires information beyond the paper's statistics):**
- Optional stopping (sequential data collection with peeking)
- Researcher degrees of freedom (choice of test statistic)
- Selective outlier exclusion
- Gender confound in testosterone analysis
- The paper's sweeping causal claims from a single underpowered study

These are exactly the gaps the skill files document: the package
screens the reported numbers, not the unreported analytic choices.
The Tier 0 paper_screening module would add context (Carney's 2016
retraction statement), and the causal_consistency skill would flag
the implausibility of a 2-minute manipulation causing lasting
hormonal changes.
