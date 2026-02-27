# Fermi Sanity Check Skill (Tier 0)

> Before digging into statistics, ask: does the headline claim survive
> back-of-envelope reasoning? A paper can have impeccable p-values and
> still make claims that violate basic magnitude, rate, or budget constraints.

This skill file adapts the judgment layer of Niccoli's Fermi estimation
framework (Niccoli, 2026; blog series "Teaching an AI to Reason Like Fermi")
from its original purpose — teaching LLMs to *do* Fermi estimation — into a
detection tool: checking whether a paper's claims *survive* one.

The framework's core taxonomy classifies every numerical quantity as KNOWN
(defensible to a skeptical non-specialist), BOUNDED (explicit upper/lower
limits with physical or logical motivation), or ASSERTED (stated without
justification). The "skeptical non-specialist" test (Niccoli, 2026) asks:
if a non-expert challenged this number, would the author need specialized
knowledge to defend it? If yes, the number requires citation or derivation,
not bare assertion.

## When to use this skill

Apply before any statistical analysis (Tier 1–3). If a claim fails
order-of-magnitude plausibility, no amount of statistical sophistication
can rescue it. This is a gate, not a replacement for deeper checks.

Trigger on:
- Headlines with large effect sizes ("reduces risk by 80%")
- Claims involving very large or very small numbers
- Comparisons across categories with different natural units or scales
- Any claim where the conclusion depends on a denominator choice

## Check 1 — Magnitude plausibility (LAW-DECOMPOSE + LAW-VALIDATE)

Break the headline claim into sub-quantities. For each, ask: is this
magnitude physically, biologically, or logically plausible?

**Procedure (adapted from Weinstein's five-step workflow via Niccoli):**
1. Identify the claimed quantity (effect size, rate, count, ratio)
2. Decompose into independent sub-quantities that multiply to give it
3. For each sub-quantity, classify as KNOWN, BOUNDED, or ASSERTED
4. Check whether the product of sub-quantities is consistent with the claim
5. If the independent estimate differs by >10× from the claim, flag

**Red flags:**
- Claimed effect requires multiple sub-quantities to all be at their
  extreme values simultaneously
- Order of magnitude of the claim is inconsistent with the decomposition
- Paper presents no independent cross-check or comparison to anchor values
- Claimed precision (e.g., "reduces mortality by 47.3%") is implausible
  given the study design and sample size

**Example — drug efficacy sanity check:**
A paper claims a drug reduces mortality by 50% in a population with 2%
baseline mortality. Decompose: 50% relative risk reduction on a 2% base
rate = 1 percentage point absolute reduction. To detect a 1pp change with
80% power at α=0.05, you need ~thousands of patients per arm. If the
study has n=80, the claim fails the magnitude check before you examine
the statistics. (Connect to `power.required_n()` for the precise number.)


## Check 2 — Normalization audit

The most common route to a misleading-but-technically-true claim is
choosing the wrong denominator. Two honest analysts can reach opposite
conclusions from the same data by normalizing differently.

**Questions to ask:**
- Per capita or aggregate? (A country's total emissions vs. per-person)
- Per year or cumulative? (Annual cancer cases vs. lifetime risk)
- Rate or count? (Deaths per million vs. total deaths)
- Per unit produced or per unit in service? (Manufacturing energy vs.
  lifetime energy including use phase)
- Aggregate or disaggregated by relevant subgroup? (Global average
  vs. regional trends that move in opposite directions)

**Red flags:**
- Denominator not stated explicitly — reader must infer what "per" means
- Denominator switches between sections without acknowledgment
- Aggregate trend reported when subgroups move in opposite directions
  (Simpson's paradox — connect to `logical_fallacy.md` Equivocation)
- Normalization choice that minimizes the effect the author wants to
  downplay, or maximizes the effect the author wants to emphasize
- Comparison between quantities normalized differently (rate vs. count,
  per-capita vs. aggregate in the same sentence)


## Check 3 — Assertion audit (KNOWN / BOUNDED / ASSERTED)

For every key numerical quantity in the paper, classify using Niccoli's
taxonomy (adapted from his LAW-ESTIMATE and LAW-FLAG):

**KNOWN** — A fact defensible to a skeptical non-specialist without domain
expertise. Speed of light, Earth's population, human height, water's
boiling point. These need no citation.

**BOUNDED** — Derived from explicit upper and lower limits with physical
or logical motivation. The paper states or implies a range and the
endpoints are grounded in something verifiable. Geometric mean of the
bounds gives a point estimate. (Niccoli's LAW-BOUNDS: bounds should span
1–3 orders of magnitude and be physically motivated, not arbitrary.)

**ASSERTED** — Stated without justification, citation, or derivation.
The number may be correct, but the reader cannot evaluate it from the
information provided.

**Red flags:**
- Key quantities ASSERTED without citation in a field where the reader
  cannot independently verify them → flag for domain expert review
- Quantities presented as KNOWN that fail the skeptical non-specialist
  test (e.g., "neutron star mass is 1.4 solar masses" — true, but not
  common knowledge; requires astrophysics training to defend)
- Bounds that are cosmetic rather than physical: point estimate given
  first, then narrow range wrapped around it (e.g., Cd ≈ 1.0 [0.7, 1.3]
  rather than "certainly more streamlined than a flat plate, certainly
  more blunt than a teardrop" → bounds from physical extremes)
- Sensitivity analysis absent when key inputs are ASSERTED — if the
  conclusion changes when an asserted quantity varies by 2×, the
  assertion needs stronger support


## Check 4 — Bounds quality

When a paper reports uncertainty ranges, confidence intervals, or
scenario analyses, check whether the bounds carry information or are
decorative.

**Physically motivated bounds** (good):
- Endpoints anchored to observable limits ("faster than walking, slower
  than highway speed" → velocity between 1.5 and 30 m/s)
- Behavioral or experiential anchors ("a gecko can walk on a ceiling
  but cannot run on one" — Niccoli's LAW-BOUNDS example)
- Bounds from independent estimation methods that agree

**Cosmetic bounds** (suspect):
- Symmetric range around a point estimate (±20% with no justification)
- Bounds narrower than the natural variability of the quantity
- "Sensitivity analysis" that varies one parameter at a time while
  holding others fixed (ignores covariance)
- Bounds that exclude the value needed to nullify the conclusion
  (i.e., the range is suspiciously convenient)

**Red flags:**
- No uncertainty range given at all for derived quantities
- Range stated but basis not explained
- Multiple uncertain inputs but only one varied in sensitivity analysis
- Conclusion described as "robust" without showing it survives
  simultaneous variation of key assumptions


## Worked example — PASS: Smil on embodied energy

Smil (2021, *Numbers Don't Lie*) compares embodied manufacturing energy
of global portable electronics vs. automobile production.

**Magnitude plausibility (Check 1):** Smil decomposes total energy into
per-unit embodied energy × units produced per year. Electronics:
0.25 GJ/phone, 4.5 GJ/laptop, 1 GJ/tablet → ~1 EJ for annual
production. Automobiles: <100 GJ/vehicle × 75 million vehicles → ~7 EJ.
Each sub-quantity is independently verifiable. Product is consistent.

**Normalization audit (Check 2):** Smil explicitly normalizes by product
lifetime — the key move. Cars last ~10 years, electronics ~2 years.
Per year of use: cars 0.7 EJ/yr, electronics 0.5 EJ/yr. The
counter-intuitive near-parity only emerges with the correct denominator.
Smil states the denominator choice explicitly and explains why it matters.

**Assertion audit (Check 3):** Per-unit energy values are ASSERTED but
flagged as conservative ("conservatively, an average embodied rate of
0.25 gigajoules per phone"). Unit counts are KNOWN (industry data).
Lifetimes are BOUNDED implicitly (electronics "on average, just two
years"; cars "at least a decade"). Key quantities are traceable.

**Bounds quality (Check 4):** Smil explicitly tests robustness: "even if
these rough aggregates were to err in opposite directions... the most
likely difference no greater than twofold." This is a proper sensitivity
test — simultaneous worst-case variation of both inputs, showing the
conclusion survives.

**Verdict:** PASS. Assumptions stated, denominator explicit and justified,
robustness tested against simultaneous adverse variation. This is what
honest Fermi reasoning looks like in published work.


## Worked example — FAIL: Lomborg on global wildfire

Lomborg claims "the world is burning less," citing Andela et al. (2017,
*Science*) showing global burned area declined ~25% over two decades.

**Magnitude plausibility (Check 1):** The global decline is real data,
not fabricated. No magnitude issue with the number itself.

**Normalization audit (Check 2):** FAIL. "Fires" in satellite burned-area
data = all vegetation burning (savanna clearing, agricultural burns,
wildfires). "Fires" in the headline = destructive wildfires threatening
communities. ~70% of global burned area is African savanna, where
conversion to cropland drives the decline. Meanwhile, temperate and
boreal forest fires are increasing. The aggregate trend hides opposite
subgroup trends — Simpson's paradox. Lead author Giglio stated that
presenting the global aggregate is "misleading because dominated by
Africa." Burton et al. (2024, *Nature Climate Change*) decomposed the
trend: land-use change suppressed burned area 19%, climate change
increased it 16%.

**Assertion audit (Check 3):** Lomborg presents the 25% decline as if it
answers the question "are wildfires getting worse?" The decline is KNOWN
(satellite data). But the implicit claim — that this decline means
wildfire risk is decreasing — is ASSERTED without acknowledging that the
relevant subgroup (forest wildfires in inhabited regions) trends opposite
to the aggregate.

**Bounds quality (Check 4):** No sensitivity analysis. No
acknowledgment that the conclusion depends on which fires you count.

**Verdict:** FAIL on normalization (Check 2). The data is real but the
denominator is wrong for the implied question. Aggregate masks subgroup
divergence. This is also an Equivocation fallacy — "fires" shifts meaning
between the data source and the headline claim (see `logical_fallacy.md`).


## Decision tree for LLM audit

```
Paper makes a quantitative claim
│
├─ Can you decompose the claim into sub-quantities?
│  ├─ Yes → Do the sub-quantities multiply to give the claimed value?
│  │        (within ~10×)
│  │  ├─ Yes → PASS Check 1
│  │  └─ No  → FLAG: magnitude implausible
│  └─ No  → Is the claim so domain-specific you cannot decompose it?
│           → Note limitation, proceed to Check 2
│
├─ What is the denominator?
│  ├─ Stated explicitly → Is it the right denominator for the question?
│  │  ├─ Yes → PASS Check 2
│  │  └─ No  → FLAG: normalization mismatch
│  └─ Not stated → FLAG: implicit denominator, check for switching
│
├─ For each key number: KNOWN, BOUNDED, or ASSERTED?
│  ├─ All KNOWN or BOUNDED with physical motivation → PASS Check 3
│  ├─ ASSERTED but with citation → acceptable, note dependency
│  └─ ASSERTED without citation or derivation → FLAG
│     Apply skeptical non-specialist test:
│     "Could a non-expert challenge this? Would the defense
│      require specialized knowledge?"
│     If yes → the number needs citation or derivation
│
├─ Are uncertainty bounds given?
│  ├─ Physically motivated, tested against adverse variation → PASS Check 4
│  ├─ Cosmetic (narrow, symmetric, single-parameter) → FLAG
│  └─ Absent → FLAG if conclusion depends on uncertain inputs
│
└─ Overall: any FLAGS? → Report which checks failed and why
   All PASS? → Proceed to Tier 1+ statistical checks
```


## Connections to other modules

- **Check 1** (magnitude) connects to `power.required_n()` — if the
  claimed effect size requires more subjects than the study has, the
  claim fails both the Fermi check and the power check
- **Check 2** (normalization) connects to `logical_fallacy.md` Equivocation —
  wrong denominator often co-occurs with term-shifting between sections
- **Check 2** also connects to `arithmetic_consistency.md` subgroup
  interaction — aggregate trends hiding opposite subgroup effects
- **Check 3** (assertion audit) connects to `paper_screening.md` — are
  asserted quantities supported by cited sources that actually exist?
- **Check 4** (bounds quality) connects to `outlier_leverage.md` — are
  reported confidence intervals honest given the regression diagnostics?


## References

- Niccoli, M. (2026). "Teaching an AI to Reason Like Fermi" (Parts 1–2).
  MyCarta blog. https://mycartablog.com — framework for KNOWN/BOUNDED/ASK
  taxonomy, LAW-BOUNDS, LAW-DECOMPOSE, LAW-VALIDATE, LAW-FLAG, and the
  "skeptical non-specialist" test.
- Weinstein, L. (2012). *Guesstimation 2.0*. Princeton University Press —
  five-step workflow (LAW0) and decomposition methodology.
- Weinstein, L. & Adam, J. A. (2008). *Guesstimation*. Princeton
  University Press — worked examples demonstrating bounding by physical
  comparison.
- Smil, V. (2021). *Numbers Don't Lie*. Penguin — PASS example:
  embodied energy comparison with explicit assumptions and robustness test.
- Andela, N. et al. (2017). "A human-driven decline in global burned
  area." *Science* 356(6345), 1356–1362.
- Burton, C. et al. (2024). "Global burned area increasingly explained
  by climate change." *Nature Climate Change*.
- Lomborg, B. — cited as FAIL example for normalization mismatch.
