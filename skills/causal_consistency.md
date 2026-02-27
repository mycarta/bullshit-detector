# Causal Consistency Skill — Mill's Methods Inverted

> **Purpose:** A reasoning framework for auditing causal claims in research papers.
> Mill's Methods are normally used to *discover* patterns. Here we invert them
> to *check whether claimed patterns hold up*. This catches logical bullshit —
> claims where the argument structure is flawed even if the arithmetic is clean.
>
> **When to use:** Any paper claiming X causes Y, X predicts Y, or X is
> associated with Y. Complements the statistical modules (p_checker, spurious,
> power) which catch arithmetic problems. This skill catches reasoning problems.
>
> **Origin:** Developed from a real case study (Wilrich drilling problem) where
> applying Mill's Methods exposed inconsistencies in a claimed causal relationship.

---

## The five checks

Work through these in order. Each builds on the previous. Stop and flag
whenever a red flag appears — don't wait until all five are done.

### 1. Agreement — Is the cause present in ALL positive cases?

**Question:** In every case where the outcome occurred, was the claimed cause
actually present?

**What to look for in the paper:**
- List or count all reported positive cases (successes, responders, affected sites)
- For each one, confirm the claimed causal factor was present
- Look for "exceptions" — positive cases where the cause was absent
- Check whether exceptions are acknowledged, explained, or buried

**Red flags:**
- Positive cases where the claimed cause is absent but not discussed
- Vague or shifting definition of the causal factor across cases
- "Exceptions excluded due to protocol violations" — were they failures?
- Denominator changes between sections (how many cases were actually positive?)

**Green flags:**
- All positive cases clearly show the cause
- Exceptions acknowledged and given plausible explanations
- Consistent operationalization throughout

---

### 2. Difference — Does the cause distinguish positive from negative cases?

**Question:** In cases where the outcome did NOT occur, was the claimed cause
actually absent?

**What to look for in the paper:**
- Are negative cases (controls, non-responders, unaffected sites) reported at all?
- For each negative case, confirm the claimed cause was absent
- Look for "false positives" — cause present but outcome absent
- Look for "false negatives" — cause absent but outcome present (covered in Agreement)

**Red flags:**
- **No negative cases reported at all** — this is the biggest single red flag.
  A paper that only shows successes cannot support a causal claim.
- Negative cases where the cause IS present but outcome didn't occur (unexplained)
- Control group poorly defined, not matched, or described vaguely
- Controls selected post-hoc or changed between analyses

**Green flags:**
- Clear control group with explicit selection criteria
- Controls matched on relevant confounders
- False positives acknowledged and discussed

---

### 3. Joint Method — Does perfect discrimination hold? Is it suspicious?

**Question:** Is the cause present in ALL positive cases AND absent in ALL
negative cases?

This is the strongest test. If it passes, the causal claim has logical support
(though not proof). But paradoxically, **perfect discrimination in small samples
is itself a red flag** — real data is messy, and too-clean results suggest
curation or fabrication.

**What to look for:**
- Does the 2×2 table (cause present/absent × outcome present/absent) show
  perfect or near-perfect separation?
- How large is the sample? Perfect separation in n < 20 warrants scrutiny.
- Were any cases excluded to achieve this separation?

**Red flags:**
- Perfect discrimination with n < 20 and no discussion of how clean this is
- Cases excluded from analysis that would have broken the pattern
- Multiple definitions of "positive" tried until one gave clean separation

**Green flags:**
- Imperfect discrimination acknowledged, with effect size and confidence intervals
- Large n with clear separation
- Pre-registered definition of positive/negative

**Connection to other modules:**
- Use `spurious.P_spurious(r, n, k)` to quantify the probability that
  observed discrimination is chance
- Use `power.achieved_power()` to check whether n was adequate to detect
  the claimed effect

---

### 4. Residues — Does the effect only appear after "controlling for" many variables?

**Question:** Is the claimed effect visible in the raw data, or does it only
emerge after removing the influence of multiple covariates?

Some covariate adjustment is legitimate and necessary. The red flag is when
adjustment is **escalating** — the authors try progressively more complex models
until one produces significance — or **inconsistent** — different covariates
in different analyses without justification.

**What to look for:**
- How many covariates are adjusted for?
- Is the unadjusted effect reported? If not, why not?
- Do different analyses in the paper use different covariate sets?
- Are covariates chosen pre-registration or post-hoc?
- Are any covariates causally downstream of the treatment? (adjusting for
  mediators biases the estimate)

**Red flags:**
- Effect only significant in the most-adjusted model
- More than 3 covariates adjusted in a small sample (overfitting risk)
- Covariate sets change between analyses without explanation
- "We controlled for age, sex, BMI, baseline severity, comorbidities,
  site, and season" in a study with n = 40 (more parameters than the data support)
- Covariates include variables that could be consequences of the treatment

**Green flags:**
- Unadjusted and adjusted results both reported
- Pre-registered analysis plan specifying covariates
- Sensitivity analysis showing robustness to covariate choice
- Number of covariates appropriate for sample size (rule of thumb: ~15-20
  observations per covariate, per Harrell 2015)

**Connection to other modules:**
- Use `redundancy.redundancy_analysis()` to check whether covariates are
  themselves redundant (adjusting for collinear covariates wastes degrees of freedom)
- Use `power.achieved_power()` to check whether the adjusted model was
  adequately powered given the effective degrees of freedom

---

### 5. Concomitant Variation — Does the dose-response hold across the full range?

**Question:** If the paper claims "more X → more Y," does this hold across
the entire range of X, or only in a selected subrange?

**What to look for:**
- Is the full range of X shown, or are axes truncated?
- Does the relationship hold at the extremes, or only in the middle?
- Are there non-monotonic regions (reversals) that are smoothed over?
- Were outliers removed? If so, were they at the extremes?

**Red flags:**
- Correlation only holds in a selected subrange of the data
- Truncated axes hiding flat or reversed regions
- Outliers removed without justification, especially at extremes
- LOESS or spline fit shown instead of raw data (can hide non-monotonicity)
- Claimed linear relationship but no residual plot shown

**Green flags:**
- Full range of data shown with individual points visible
- Dose-response demonstrated across multiple levels, not just high vs. low
- Non-linearities acknowledged and modeled appropriately
- Prediction intervals shown, not just confidence intervals (see Notebook C,
  PI/CI distinction)

**Connection to other modules:**
- Use `spurious.conf_int(r, n)` to check whether the CI for the correlation
  crosses zero
- Use `spurious.r_crit(n)` to check whether r exceeds the critical threshold
- If raw data is available, use `leverage.influence_plot()` to check whether
  the relationship depends on a few high-leverage points

---

## Putting it together — the audit workflow

When reviewing a paper with causal claims, work through this sequence:

1. **Extract the claim:** What is X (cause)? What is Y (outcome)? What is the
   claimed relationship?

2. **Run the statistical modules first** (these are fast and unambiguous):
   - `check_p_value()` — do the reported p-values match the test statistics?
   - `P_spurious()` — given n and k, what's the probability of a spurious correlation?
   - `achieved_power()` — was the study powered to detect the claimed effect?

3. **Then work through Mill's Methods** (these require reading the paper carefully):
   - Agreement → Difference → Joint → Residues → Concomitant Variation

4. **Synthesize:** A paper can fail statistical checks but pass logical checks
   (sloppy arithmetic, sound reasoning) or pass statistical checks but fail
   logical checks (clean numbers, flawed argument). The combination is what
   gives you confidence — or doubt.

---

## Worked examples

These four examples calibrate the framework across different outcomes:
PASS, CAUTION, and REVIEW. They demonstrate what good and bad audits
look like, and illustrate the different failure modes Mill's Methods can catch.

---

### Example 1: Wilrich drilling problem (PASS)

**Source:** Hunt, "Value thinking: from the classical to the hyper-modern"
(CSEG talk); Niccoli (2026) blog post analysis.

**Claim:** Curvature AND Diffraction imaging together predict drilling problems
(loss of circulation from open fractures) in the Wilrich reservoir.

**Data:** 7 wells, 5 binary seismic attributes. 4 problem wells (A, B, F, G),
3 non-problem wells (C, D, E).

| Check | Result | Detail |
|-------|--------|--------|
| Agreement | ✅ PASS | All 4 problem wells have Curvature=TRUE AND Diffraction=TRUE |
| Difference | ✅ PASS | All 3 non-problem wells have at least one FALSE. Neither attribute alone discriminates (Well E: Curvature TRUE, no problem; Well D: Diffraction TRUE, no problem) — the conjunction is essential |
| Joint Method | ✅ PASS (caveat) | Perfect discrimination in n=7 would normally warrant scrutiny, but three factors mitigate: (1) framed as operational heuristic under asymmetric costs, not causal proof; (2) conjunction has independent physical justification (curvature=structural deformation, diffraction=discontinuities); (3) three independent methods converge (Mill's, neural network, Hunt's domain knowledge) |
| Residues | ✅ PASS | No covariate adjustment. Neural network learned negative weights for AVAz (−4.9) and VVAZ (−14.5) — Mill's Residues in action. Hunt (2014) independently documented these attributes were measuring coal response, not fractures |
| Concomitant Variation | ⬜ N/A | Binary attributes, no dose-response to test |

**Verdict: PASS.** Defensible reasoning under uncertainty. Small sample honestly
acknowledged. Physical justification for the specific conjunction. Three methods
converge. The authors framed it as a decision rule, not a causal claim — the
right epistemic stance for 7 data points.

**What this teaches the LLM:** Perfect discrimination in small samples is not
automatically suspicious if (a) the claim is appropriately modest, (b) the
discriminating variables have independent physical justification, and (c)
multiple methods converge.

---

### Example 2: Never Been Kissed (CAUTION)

**Source:** Lefkowitz, Wesche & Leavitt (2018), "Never Been Kissed: Correlates
of Lifetime Kissing Status in U.S. University Students," Archives of Sexual
Behavior, 47(4), 1283–1293.

**Claim:** Multiple personal, contextual, and adjustment/health factors predict
whether a university student has never kissed a partner by college. The authors
frame never having kissed as "off-time" and suggest it "may also be unhealthy."

**Data:** N = 738 first-year students, logistic regression with 15 predictors.

| Check | Result | Detail |
|-------|--------|--------|
| Agreement | ⬜ N/A | Probabilistic association study, not deterministic. No single predictor present in all never-kissed students. Expected for this design |
| Difference | ⚠️ WEAK | Heavy distributional overlap on all predictors. The strongest discriminator (romantic relationship status, OR=22.6) is near-tautological — being in a relationship almost guarantees having kissed |
| Joint Method | ⚠️ CAUTION | No overall model fit reported (no pseudo-R², no AUC). With 105 events and 15 predictors, events-per-predictor = 7, below Harrell's rule of thumb (~15–20). Model may be overfitted |
| Residues | 🚩 RED FLAG | Key findings evaporate in multivariate model: self-esteem drops from OR=2.33 (p<.001 bivariate) to OR=1.02 (n.s. multivariate). Neuroticism drops from OR=0.63 (p<.01) to OR=0.72 (n.s.). Yet both are used in the discussion to support the "unhealthy" narrative. Relationship status as a control is near-circular |
| Concomitant Variation | ⚠️ NOT TESTED | Linearity assumed but not verified. Alcohol finding may reflect binary drinker/non-drinker split, not continuous dose-response |

**Verdict: CAUTION.** The arithmetic is competent — no fabrication, no p-hacking.
But the argument structure overreaches. Findings that support the "off-time may
be unhealthy" conclusion (neuroticism, self-esteem) don't survive multivariate
controls. The strongest predictor is near-tautological. The rhetorical framing
carries more weight than the statistics support.

**What this teaches the LLM:** A paper can have correct p-values and still fail
the logical audit. The Residues check is particularly powerful here — it catches
the pattern of bivariate significance evaporating in multivariate models but
persisting in the discussion narrative. This is not fraud; it's overinterpretation.

---

### Example 3: Green Coffee Bean Extract (REVIEW — data integrity)

**Source:** Vinson, Burnham & Nagendran (2012), "Randomized, double-blind,
placebo-controlled, linear dose, crossover study to evaluate the efficacy and
safety of a green coffee bean extract in overweight subjects," Diabetes,
Metabolic Syndrome and Obesity. **Retracted 2014.**

**Claim:** Green coffee bean extract (GCA) causes weight loss of 17.7 pounds,
10.5% of body weight, 16% body fat in 22 weeks, "without diet or exercise."

**Data:** 16 subjects, crossover design (high-dose GCA, low-dose GCA, placebo).
Funded by Applied Food Sciences Inc. (AFS), the manufacturer.

| Check | Result | Detail |
|-------|--------|--------|
| Agreement | ❌ CANNOT EVALUATE | FTC found the lead investigator repeatedly altered weights, changed trial length, and misstated which subjects received placebo vs GCA. Cause-case links are unverifiable |
| Difference | 🚩 FAILS | Subjects were instructed to restrict diet and increase exercise during ALL phases (including placebo), but this was undisclosed. The placebo phases were not true negatives |
| Joint Method | 🚩 REVIEW | Subject assignments corrupted. Effect size implausible for n=16. FTC called the study "so hopelessly flawed that no reliable conclusions could be drawn from it" |
| Residues | 🚩 RED FLAG | Inverse residues abuse — known confounders (diet, exercise instructions) were hidden rather than controlled. Any weight loss could be attributable to the undisclosed interventions |
| Concomitant Variation | 🚩 RED FLAG | Three-phase dose-response claimed (high > low > placebo) but data integrity destroyed by measurement alteration. Cannot distinguish genuine gradient from fabricated one |

**Verdict: REVIEW (unreliable).** Fails or cannot be evaluated on every check.
The causal logic is broken at every level. Notably, Tier 0 screening
(paper_screening.py) should flag this before Mill's Methods is even needed:
sponsor = manufacturer, ghost authorship (hired academics rewrote the paper),
data never independently verified. The logical audit confirms what the
provenance audit already suggested.

**What this teaches the LLM:** When data integrity is compromised, Mill's Methods
checks become "cannot evaluate" rather than "pass" or "fail." The framework
correctly identifies that the logical structure is unassessable, which is itself
a strong signal. Also demonstrates the value of running Tier 0 screening first.

---

### Example 4: Musician Mortality by Genre (REVIEW — selection bias)

**Source:** Discussed in Bergstrom & West (2020), *Calling Bullshit*, Chapter 6.
Original study circa 2015, widely shared on social media.

**Claim:** Musical genre is associated with age at death. Rap/hip-hop musicians
die at ~30; blues, jazz, gospel musicians die at ~60+. Original researcher
compared the occupational hazard to war.

**Data:** Observational. Ages at death for deceased musicians, grouped by genre.
Living musicians excluded.

| Check | Result | Detail |
|-------|--------|--------|
| Agreement | ⚠️ MISLEADING | Genre is present in all cases by definition (every musician has a genre label). But genre acts as a proxy for genre age — rap has existed ~40 years, blues ~100+ years. The "cause" is misidentified |
| Difference | 🚩 FAILS | Study only includes deceased musicians. For newer genres, the only deceased musicians are those who died young (the genre hasn't existed long enough for anyone to die old in it). Living musicians — the essential comparison group — are entirely absent. This is right-censoring creating selection bias |
| Joint Method | 🚩 RED FLAG | The near-perfect genre→age-at-death pattern is almost entirely a statistical artifact of right-censoring. Bergstrom & West's chameleon example illustrates the mechanism: chameleons banded in recent years appear to die younger only because long-lived ones are still alive at study's end |
| Residues | 🚩 RED FLAG | The dominant confound (genre founding date → right censoring) is acknowledged in the paper's prose but absent from the visualization. In social media, the graph travels without the caveat |
| Concomitant Variation | 🚩 RED FLAG | The apparent dose-response (newer genre → younger death) maps perfectly onto genre founding date. The gradient IS the censoring artifact, not evidence of causation |

**Verdict: REVIEW (unreliable).** Every check reveals the same underlying
problem: right-censoring. Deceased musicians from newer genres are not a
representative sample — they are specifically the short-lived tail, because
the long-lived musicians are still alive.

**What this teaches the LLM:** This is the critical case where all arithmetic
is correct. The mean ages at death are accurately computed. No p-values are
wrong. No numbers are fabricated. `check_p_value()` and `a_grimmer()` would
find nothing. The bullshit is entirely in the reasoning — the leap from
"these are the ages at which deceased musicians died" to "these genres are
dangerous." This is exactly the layer Mill's Methods is designed to catch,
and exactly the layer that statistical modules alone will miss.

---

## Limitations

1. **Requires careful reading** — this is a reasoning framework, not an
   automated check. The LLM or human reviewer must extract claims, cases,
   and evidence from the paper.
2. **Internal consistency ≠ truth** — a fabricated dataset can be made
   perfectly consistent with Mill's Methods. This catches sloppy manipulation,
   not sophisticated fraud.
3. **Imperfect consistency ≠ fraud** — real data is messy. Some exceptions
   and imperfections are expected and healthy. The red flags indicate where
   to look harder, not where to conclude fraud.
4. **Domain knowledge matters** — whether an "exception" is legitimate requires
   understanding the field. The framework surfaces the questions; the expert
   interprets the answers.

---

## References

- Mill, J.S. (1843), *A System of Logic*, Book III, Chapter VIII —
  original formulation of the Methods of Agreement, Difference, Residues,
  and Concomitant Variation
- Niccoli, M. (2026), "The value of intellectual play: Mill, machine learning,
  and a drilling problem I couldn't stop thinking about" — blog post with
  Wilrich worked example. https://mycartablog.com/2026/01/20/the-value-of-intellectual-play-mill-machine-learning-and-a-drilling-problem-i-couldnt-stop-thinking-about/
- Hunt, L. et al. (2014), "Precise 3D seismic steering and production rates
  in the Wilrich tight gas sands of West Central Alberta," SEG Interpretation
- Lefkowitz, Wesche & Leavitt (2018), "Never Been Kissed: Correlates of
  Lifetime Kissing Status in U.S. University Students," Archives of Sexual
  Behavior, 47(4), 1283–1293
- Vinson, Burnham & Nagendran (2012), green coffee bean extract study,
  Diabetes, Metabolic Syndrome and Obesity (retracted 2014)
- Bergstrom & West (2020), *Calling Bullshit: The Art of Skepticism in a
  Data-Driven World*, Random House — musician mortality / right-censoring example
- Harrell (2015), *Regression Modeling Strategies* — rule of thumb for
  covariates per sample size
- Reis & Friese (2022), "The Myriad Forms of p-Hacking" — taxonomy of
  manipulation methods that Mill's Methods can catch (see also
  skills/arithmetic_consistency.md)
