# Logical Fallacy Quick-Reference for Research Paper Audits

## Purpose

This is a lightweight checklist of informal logical fallacies as they appear
in **empirical research papers** — not in everyday rhetoric. Most fallacies
that matter in research are already caught by other skills and modules in this
package. This file covers the gaps.

Use this **after** running Mill's Methods (causal_consistency.md) and the
statistical modules. If those found nothing but the paper's argument still
feels wrong, scan this list.

## Fallacy taxonomy for research contexts

The 13 categories below follow Jin et al. (2022), "Logical Fallacy Detection"
(Findings of EMNLP 2022). For each, we note how it manifests in papers and
which existing module already covers it (if any).

### Already covered by other modules/skills

| Fallacy | In papers | Covered by |
|---------|-----------|------------|
| **False Causality** | Post hoc reasoning, confounders ignored, correlation→causation | `causal_consistency.md` (Mill's checks 1–5), `spurious.P_spurious()` |
| **Faulty Generalization** | Small n extrapolated to population, convenience sample treated as representative | `power.achieved_power()`, `spurious.r_crit()`, Joint Method check |
| **Fallacy of Credibility** | Appeal to authority, COI not disclosed, industry-funded claims | `paper_screening.md` (COI, funding, author checks) |
| **Ad Hominem** | Dismissing prior work by attacking the researcher rather than the methods | Rare in peer-reviewed papers; flag if seen in Discussion |

### Partially covered — scan for these

| Fallacy | In papers | What to look for |
|---------|-----------|------------------|
| **Circular Reasoning** | Outcome variable is a near-tautology of a predictor. Result is definitionally true. | Example: predicting "kissed" from "in a relationship" (Lefkowitz 2018 — OR=22.6, near-circular). Mill's Residues partially catches this but the circularity may be subtle. |
| **False Dilemma** | Framing as only two explanations when others exist. "Either our model is correct or the data is noisy." | Common in Discussion sections. Look for "either…or" constructions that exclude plausible alternatives. |
| **Equivocation** | Key term shifts meaning between sections. "Significant" used statistically in Results, clinically in Discussion. | Also: "association" in Methods becoming "effect" or "impact" in Conclusions. Track key terms across sections. |
| **Appeal to Emotion** | Alarmist framing not supported by effect sizes. "Unhealthy" label applied to benign behaviors based on non-significant results. | Check whether Discussion language matches Results magnitude. Lefkowitz (2018): bivariate findings that vanish in multivariate model still called "unhealthy." |

### Rarely seen in empirical papers — low priority

| Fallacy | Notes |
|---------|-------|
| **Ad Populum** | "Many researchers agree…" without citation. Uncommon in well-edited journals. |
| **Fallacy of Extension** (Straw Man) | Misrepresenting prior work to make own contribution seem larger. Check cited papers if suspicious. |
| **Fallacy of Relevance** (Red Herring) | Introducing unrelated evidence in Discussion. Usually caught in peer review. |
| **Fallacy of Logic** (Non Sequitur) | Conclusion doesn't follow from premises. Subsumes many others; too broad to be actionable as a single check. |

## Worked example: Equivocation + aggregation bias

**Claim:** "The world is burning less" — global burned area declined ~25%
over 1998–2015 (Lomborg, WSJ 2023, citing Andela et al. 2017 in *Science*).
Used to argue that climate change is not making wildfires worse.

**The data is real.** Andela et al. (2017) did find a 24.3% decline in global
burned area. The paper is solid science, published in *Science*, from NASA
Goddard.

**The equivocation:** "Fires" in the satellite data means all vegetation
burning — savanna fires, agricultural clearing, grassland burns. "Fires" in
the op-ed headline means destructive wildfires threatening lives and property.
These are different phenomena with different drivers and different trends.

**What the source paper actually says:** The decline is driven almost entirely
by tropical savanna conversion to cropland, primarily in Africa, which
dominates the global total (~70% of global burned area). The lead author,
Prof. Louis Giglio, told *The Guardian* that presenting the global time
series in isolation is "misleading because it is dominated by Africa." In
temperate and boreal forests — where climate-driven wildfires occur —
burned area is *increasing*. A 2024 attribution study in *Nature Climate
Change* (Burton et al.) found that land-use change suppressed global burned
area by 19%, but climate change *increased* it by 16%, nearly cancelling
the decline.

**Fallacy structure:**
- **Equivocation:** The term "fires" shifts meaning between data source
  (all vegetation burning) and argument (climate-driven wildfires).
- **Aggregation bias (Simpson's paradox):** The global aggregate hides
  opposite trends in subgroups. Forest fires up, savanna fires down,
  total down because savanna dominates the denominator.
- **Misrepresentation of source:** The cited paper explicitly attributes
  the decline to agricultural expansion, not to benign climate conditions.
  Lomborg's argument inverts the paper's own conclusions.

**Which checks catch this:**
- `logical_fallacy.md` → Equivocation (this file — term shifts meaning)
- `causal_consistency.md` → Concomitant Variation (dose-response between
  warming and fire holds when disaggregated by biome, fails in aggregate)
- `causal_consistency.md` → Residues (dominant confound — land-use change —
  not controlled for in the public argument)

**Lesson for LLM:** When a claim cites real data from a reputable source,
check whether the *terms* used in the argument match the *variables* in the
data. A global aggregate can mask opposite regional trends. Always check
what the cited paper's own authors say about their findings.

## How to use this file

When auditing a paper's argument (not its arithmetic):

1. Run `causal_consistency.md` first — it catches the high-value fallacies
   (false causality, missing controls, selective evidence, confounded
   dose-response) with structured checks and worked examples.
2. If the paper passes Mill's Methods but something still feels off,
   scan the "Partially covered" table above.
3. Pay special attention to **Equivocation** and **Circular Reasoning** —
   these are the two fallacies most likely to survive both statistical
   checks and Mill's Methods.
4. In the Discussion/Conclusions: watch for language escalation. Terms
   like "association" becoming "effect," "correlation" becoming "cause,"
   "bivariate" findings surviving into conclusions after failing in
   multivariate models.

## Test data

The Jin et al. (2022) LOGIC dataset (~1.7K examples, 13 categories) is
available at https://github.com/causalNLP/logical-fallacy and on HuggingFace
at tasksource/logical-fallacy. Note: the original dataset has known quality
issues (quiz questions left in, definitions instead of examples). A cleaned
version exists at https://github.com/tmakesense/logical-fallacy.

These are textbook-style examples ("identify the fallacy"), not research paper
excerpts. They are useful for calibrating fallacy recognition but do not
substitute for the worked examples in causal_consistency.md.

## References

- Jin, Lalwani, Vaidhya, Shen, Ding, Lyu, Sachan, Mihalcea & Schoelkopf
  (2022), "Logical Fallacy Detection," Findings of EMNLP 2022.
  https://aclanthology.org/2022.findings-emnlp.532
- Sourati & Evans (2023), "Case-Based Reasoning with Language Models for
  Classification of Logical Fallacies," IJCAI 2023.
- Bergstrom & West (2020), *Calling Bullshit: The Art of Skepticism in a
  Data-Driven World*, Random House. (Chapter 3: logical fallacies in
  quantitative arguments.)
