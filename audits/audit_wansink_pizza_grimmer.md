# Audit: Wansink Pizza Papers (2014–2016) — Impossible Descriptive Statistics

**Papers:** Four papers from a single dataset, all retracted:
1. Just, Sigirci & Wansink (2014). "Lower buffet prices lead to less
   taste satisfaction." *J. Sensory Studies.*
2. Just, Sigirci & Wansink (2015). "Peak-end pizza." *J. Product &
   Brand Management.*
3. Sigirci & Wansink (2015). "Low prices and high regret." *BMC
   Nutrition.*
4. Kniffin, Sigirci & Wansink (2016). "Eating heavily." *Evolutionary
   Psychological Science.*

**Known ground truth:** van der Zee, Anaya & Brown (2017) found 150+
errors across the four papers. All four retracted. Cornell found
scientific misconduct. Wansink resigned in 2018.

**Module applied:** `grimmer.a_grimmer()` — tests whether reported
means and standard deviations are mathematically compatible with the
stated sample sizes for integer (Likert-scale) data.

---

## What GRIMMER tests

When participants respond on a Likert scale (e.g., 1–9), their
answers are integers. This constrains which means and SDs are
possible for a given sample size:

- **GRIM test:** n × mean must be a whole number (because it is
  the sum of n integers). If not, the mean is impossible.
- **GRIMMER test:** Even if the mean passes GRIM, the SD must be
  compatible with some arrangement of n integers that produces that
  sum. If no such arrangement exists, the SD is impossible.

These are not statistical tests — they are arithmetic facts. A
GRIMMER failure means the reported numbers cannot have come from
the described data collection process, full stop.

---

## Extracted test cases

All Likert items are 9-point scales (1 = "strongly disagree" to
9 = "strongly agree"). Sample sizes are small subgroups from a
buffet experiment with N ≈ 95–139 total.

```
from bullshit_detector.grimmer import a_grimmer
```

| Label | Source | n | Mean | SD | Result |
|-------|--------|---|------|-----|--------|
| Guilt rating ($4 group) | Art.3 | 18 | 3.44 | 2.47 | **FAIL — GRIMMER** |
| $8 group, 3 pieces, discomfort | Art.4 Table 2 | 10 | 2.25 | 1.83 | **FAIL — GRIM** |
| $8 group, 3 pieces, overeating | Art.4 Table 2 | 10 | 3.92 | 2.15 | **FAIL — GRIM** |
| $4 group, 2 pieces, guilt | Art.4 Table 2 | 12 | 4.83 | 2.71 | **FAIL — GRIMMER** |
| $4 group, taste satisfaction | Art.1 | 15 | 3.67 | 1.95 | PASS |
| Solo diners, enjoyment | Art.3 | 8 | 5.38 | 2.07 | PASS |
| **CONTROL** (generated data, n=18) | — | 18 | 5.78 | 1.99 | PASS ✓ |
| **CONTROL** (generated data, n=10) | — | 10 | 4.70 | 3.02 | PASS ✓ |
| **CONTROL** (generated data, n=12) | — | 12 | 5.42 | 2.71 | PASS ✓ |

**Result: 4 of 6 Wansink values are mathematically impossible.
All 3 control values (generated from actual Likert data) pass.**

---

## Detailed failure analysis

### Case 1: n=10, mean=2.25 — GRIM failure

```python
a_grimmer(n=10, mean=2.25, sd=1.83)
# → GRIM inconsistent
```

For n=10 with integer responses, n × mean = 10 × 2.25 = 22.5. The
sum of 10 integers cannot be 22.5. For n=10, all valid means must
end in .X0 (e.g., 2.20, 2.30). The mean 2.25 is impossible — it
requires half a person.

This can be caught by visual inspection: any mean for n=10 with a
nonzero second decimal is wrong. van der Zee et al. noted this
explicitly.

### Case 2: n=18, mean=3.44, SD=2.47 — GRIMMER failure

```python
a_grimmer(n=18, mean=3.44, sd=2.47)
# → GRIMMER inconsistent (GRIM passes)
```

n × mean = 18 × 3.44 = 61.92, which rounds to 62. GRIM passes
because 62/18 = 3.4444... rounds to 3.44. But the SD of 2.47 is
not compatible with any set of 18 integers that sum to 62.

This is the Allard canonical test case — the A-GRIMMER technique
catches what simple GRIM misses. The mean looks plausible; the SD
betrays the impossibility.

### Case 3: n=12, mean=4.83, SD=2.71 — GRIMMER failure

n × mean = 12 × 4.83 = 57.96, rounds to 58. GRIM passes (58/12 =
4.8333... → 4.83). But SD=2.71 is incompatible with any arrangement
of 12 integers summing to 58.

### Why 2 of 6 values pass

Not every number in a flawed paper is impossible. Some reported
values happen to be arithmetically consistent even if the underlying
data handling was sloppy. The diagnostic power of GRIMMER comes from
the density of failures: finding 4 impossible values in 6 checks
from a single table is damning. A single typo might explain one
failure. Four failures across a table indicates systematic problems
with the data.

---

## Red flags checklist

**From arithmetic_consistency.md:**

- ☑ Multiple GRIM/GRIMMER failures in the same paper
- ☑ Sample sizes change between papers using the same dataset
  (N=95 in some papers, N=139 in others)
- ☑ Degrees of freedom inconsistent with sample sizes
- ☑ Data described as "failed study with null results" — then
  sliced into 4 publications with significant findings

**Not tested here but documented by van der Zee et al.:**

- Recalculated F and t statistics inconsistent with reported means/SDs
- Contradictory claims between papers from the same dataset
- Study duration reported differently across papers (2 weeks vs
  1 month vs 2 months)
- Season reported as "spring" but data collected October–December

---

## Verdict

| Check | Result |
|-------|--------|
| GRIM (mean consistency) | **2 FAILURES** (n=10 cases) |
| GRIMMER (SD consistency) | **2 FAILURES** (n=18, n=12 cases) |
| Control validation | 3/3 PASS |
| Density of failures | **4/6 = 67%** |

**Overall: REJECT.** The arithmetic is impossible. No interpretation
or reanalysis can save numbers that cannot exist. This is the
cleanest detection case in the package: GRIMMER gives a binary
answer (possible/impossible) with zero ambiguity.

---

## What the package caught vs. what it missed

**Caught:**
- Impossible means (GRIM failures for n=10)
- Impossible SDs (GRIMMER failures for n=18, n=12)
- High failure density indicating systematic problems

**Not caught (requires cross-paper analysis):**
- Sample size contradictions between papers from the same dataset
- Inconsistent test statistics (requires statcheck-style recomputation)
- Contradictory findings between papers
- Metadata inconsistencies (dates, seasons, study duration)
- The broader "salami slicing" pattern (4 papers from 1 failed study)

These cross-paper checks require comparing multiple documents — a
task for the future orchestrator, not a single-module audit. The
package catches the arithmetic; the human (or multi-agent system)
catches the pattern.

---

## References

- van der Zee, T., Anaya, J., & Brown, N.J.L. (2017). "Statistical
  heartburn: an attempt to digest four pizza publications from the
  Cornell Food and Brand Lab." *BMC Nutrition*, 3, 54.
- Allard, A. (2018). "Analytic-GRIMMER: a new way of testing the
  possibility of standard deviations." Blog post.
- Brown, N.J.L., & Heathers, J.A.J. (2017). "The GRIM test."
  *Social Psychological and Personality Science*, 8(4), 363–369.
- Anaya, J. (2016). "The GRIMMER test." *PeerJ Preprints*, 4, e2400v1.
