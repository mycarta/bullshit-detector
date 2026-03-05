# Unsupervised Learning Critique Skill (Reasoning Only)

> No code module. This is a structured reasoning framework for the LLM.
> Complements `spurious_correlation.md` (Tier 2) and `outlier_leverage.md`
> (Tier 3) by catching methodological failures specific to clustering and
> dimensionality reduction.

## Purpose

When a paper uses unsupervised methods (k-means, hierarchical clustering,
PCA, t-SNE, UMAP, etc.) to discover "types," "subtypes," "groups," or
"latent structure," the results are only meaningful if the method's
assumptions match the data and the interpretation doesn't overstate what
the algorithm found.

The core danger: **cluster reification** — treating algorithm output as
discovered natural kinds. Clustering algorithms always produce clusters.
That doesn't mean the clusters are real.

This skill file tells the LLM what to look for and what to flag.

---

## Cluster analysis audit checklist

### 1. Why this algorithm?

**The question:** Did the authors justify choosing their clustering method,
or did they reach for k-means by default?

**What to look for in the paper:**
- Is the choice of algorithm stated and justified?
- Does the algorithm match the data type? k-means assumes continuous
  variables with Euclidean distance. If the data includes categorical
  variables, binary indicators, or mixed types, k-means is inappropriate.
  k-prototypes or PAM (partitioning around medoids) should be used instead.
- Does the algorithm match the expected cluster shape? k-means assumes
  spherical clusters of roughly equal size. DBSCAN or Gaussian mixture
  models handle non-spherical or unequal clusters.

**Red flags:**
- k-means used on mixed-type clinical data (continuous lab values +
  categorical diagnoses + binary flags) without acknowledgment of the
  mismatch.
- No mention of alternative algorithms tried.
- Algorithm chosen because it's "widely used" rather than because it
  fits the data structure.


### 2. Centroids vs. medoids

**The question:** Are cluster centres reported as actual observations, or
as synthetic averages that may fall in empty space?

**What to look for in the paper:**
- Does the paper report cluster centroids (arithmetic means of each
  variable within cluster)? If so, does any reported "typical member"
  actually correspond to a real data point?
- Were distances from each member to its cluster centre reported or
  visualised? Without these, you cannot tell whether clusters are tight
  groups or arbitrary partitions of a continuum.
- If centroids fall in low-density or empty regions of the feature space,
  the "typical" member of that cluster doesn't exist. The cluster label
  is a statistical artefact, not a type.

**Red flags:**
- Cluster centres described as "profiles" or "phenotypes" without
  confirming that any actual observation resembles the centroid.
- No report of within-cluster dispersion (distances to centre, silhouette
  widths, or spread on any dimension).
- Centroid coordinates that are implausible composites — e.g., a cluster
  "centre" with 0.6 on a binary variable, described as a type.

**Computational checks (Tier 3, if data available):**
- Recompute with PAM (k-medoids) and compare cluster assignments. If
  >20% of members swap clusters, the centroid-based solution is unstable.
- Compute silhouette widths for both k-means and k-medoids. If k-medoids
  produces comparable or better silhouettes, report.
- Check density at centroid locations — if centroids sit in low-density
  regions, clusters are splitting a continuum, not recovering groups.


### 3. How many clusters?

**The question:** Was k chosen by evidence, or imposed?

**What to look for in the paper:**
- Did the authors use a data-driven method to select k (silhouette,
  gap statistic, elbow method, BIC for mixture models)?
- Did they report results for alternative values of k?
- Is the chosen k suspiciously convenient — matching a prior hypothesis
  or a clinical taxonomy the authors wanted to confirm?

**Red flags:**
- k stated as given with no justification ("We used k=5 clusters").
- Elbow plot shown but the "elbow" is ambiguous and the authors chose
  the value that supports their narrative.
- Silhouette or gap statistic suggests k=2 but the paper reports k=5
  because "clinically meaningful subtypes" were expected.
- No sensitivity analysis: what happens at k±1?


### 4. Cluster stability and reproducibility

**The question:** Would different random seeds, different subsamples, or
different distance metrics produce the same clusters?

**What to look for in the paper:**
- Were clusters validated by bootstrap resampling, cross-validation,
  or split-half analysis?
- Were results reported for multiple random initializations (k-means
  is initialization-dependent)?
- Were results compared across different distance metrics?

**Red flags:**
- No stability analysis of any kind.
- "We ran k-means 100 times and selected the solution with the lowest
  within-cluster sum of squares" — this finds the best k-means solution,
  not evidence that k-means is the right model.
- Clusters validated only by showing that cluster membership correlates
  with an outcome — this is circular if the outcome variables were
  included in the clustering, and merely confirmatory if they weren't
  (any partition of a dataset will show some outcome differences by
  chance).


### 5. Cluster reification

**The question:** Does the paper treat algorithm output as discovered
natural kinds?

This is the highest-value check in this skill file. Everything above
feeds into it.

**What to look for in the paper:**
- Does the language escalate from "clusters" in Methods to "subtypes,"
  "types," "distinct groups," or "phenotypes" in Discussion/Conclusions?
- Are clusters given proper names (e.g., "severe insulin-resistant
  diabetes," "mild age-related diabetes") that imply discrete biological
  entities?
- Does the paper propose clinical action based on cluster membership
  (different treatments per subtype) without validating that cluster
  membership is stable and predictive?

**Red flags:**
- Naming clusters as if they were diseases or conditions.
- Proposing cluster-specific treatment pathways based on a single
  clustering analysis with no replication.
- Ignoring within-cluster heterogeneity — members near cluster
  boundaries may be more similar to the neighbouring cluster than
  to their own centroid.
- No discussion of the continuum alternative: that the data may be
  unimodal or multimodal but continuous, with no discrete types.

**The question to always ask:** Would a density plot or mixture model
show distinct modes, or is the algorithm imposing boundaries on a
smooth distribution?


### 6. Dimensionality reduction as evidence

**The question:** When PCA, t-SNE, or UMAP is used to "visualise"
clusters, does the visualisation actually support the claim?

**What to look for in the paper:**
- t-SNE and UMAP can make any dataset look clustered by tuning
  perplexity/n_neighbors. Were hyperparameters reported and justified?
- Were multiple perplexity/n_neighbors values shown? If one setting
  shows separation and another doesn't, the evidence is weak.
- Does PCA explain enough variance for the 2D projection to be
  meaningful? If PC1 + PC2 capture only 25% of variance, the plot
  is mostly noise.

**Red flags:**
- t-SNE or UMAP plot shown as primary evidence of "distinct clusters"
  with no quantitative validation.
- Perplexity or n_neighbors not reported.
- Only the "best-looking" projection shown.
- PCA biplot with low explained variance but confident cluster
  interpretation.

---

## Worked example: Ahlqvist et al. (2018) — diabetes subtypes

**Paper:** Ahlqvist, E., Storm, P., Käräjämäki, A., et al. (2018).
"Novel subgroups of adult-onset diabetes and their association with
outcomes: a data-driven cluster analysis of six variables."
*The Lancet Diabetes & Endocrinology*, 6(5), 361–369.

**Claim:** Five reproducible subtypes of adult-onset diabetes, each with
distinct progression patterns and complication risks. Named: SAID
(severe autoimmune), SIDD (severe insulin-deficient), SIRD (severe
insulin-resistant), MOD (mild obesity-related), MARD (mild age-related).

**Audit using this checklist:**

**Check 1 — Algorithm choice:** k-means on six continuous variables
(GAD antibodies, HbA1c, BMI, age at diagnosis, HOMA2-B, HOMA2-IR).
All continuous, so k-means is defensible on data-type grounds. However,
some variables (GAD antibodies) have highly skewed distributions with
many zeros — k-means assumes roughly spherical clusters, and a spike
at zero plus a long right tail is not spherical in that dimension.
**Verdict: CAUTION.**

**Check 2 — Centroids vs. medoids:** The paper reports cluster centroids
(mean values per cluster). No distances from members to centres are
reported. No density plots showing whether members cluster tightly
around centres or spread across the full range. The centroid of the
SIRD cluster, for example, has specific mean values of HOMA2-IR and
HOMA2-B — but how many actual patients in SIRD closely resemble that
profile? Not reported.
**Verdict: FLAG.** This is the core issue Thomas Speidel identified.

**Check 3 — Number of clusters:** The paper reports using hierarchical
clustering to select k, then k-means for final assignment. k=5 chosen
based on visual inspection of dendrograms. No gap statistic, no BIC,
no systematic comparison of k=3,4,5,6,7. The five subtypes map
conveniently onto a clinical narrative.
**Verdict: CAUTION.**

**Check 4 — Stability:** The paper replicates clusters in three
independent Scandinavian cohorts — this is genuine external validation
and a strength. However, no bootstrap stability analysis within cohorts,
no sensitivity to initialization, and importantly: replication was
assessed by whether cluster-level mean profiles matched, not whether
individual patients assigned consistently.
**Verdict: MIXED.** External replication is real. Individual assignment
stability unknown.

**Check 5 — Reification:** The paper names the five clusters as
"subtypes" and proposes subtype-specific treatment implications.
Subsequent commentary (e.g., Udler, 2019) noted that continuous
variation across clusters is at least as plausible as discrete types.
Patients near cluster boundaries — who may be the most clinically
ambiguous and thus most in need of guidance — get forced into a
category that may not describe them well.
**Verdict: FLAG.** Language escalation from "clusters" to "subtypes"
to "diseases" occurred in the paper and accelerated in the subsequent
literature. The paper itself is careful in places but the framing
invites reification.

**Overall verdict: REVIEW.** The statistical work is competent and the
replication across cohorts is genuine. But the interpretation overstates
what clustering can show. The method finds clusters — it does not prove
types. The absence of within-cluster dispersion data (Check 2) and the
reification of labels (Check 5) are the primary concerns.

---

## How to use this file

When auditing a paper that uses unsupervised methods:

1. **Identify the method** — k-means, hierarchical, DBSCAN, GMM, PCA,
   t-SNE, UMAP, or something else.
2. **Work through checks 1–6 in order.** Not all will apply to every
   paper. Skip checks that don't match the method used.
3. **Pay special attention to Check 2 (centroids vs. medoids) and
   Check 5 (reification).** These are the two failures most likely to
   survive peer review because they are interpretive, not arithmetic.
4. **Language escalation is the tell.** Track what the paper calls its
   groups across sections: "clusters" in Methods → "subtypes" in
   Results → "types" or "phenotypes" in Discussion → "diseases" in
   Conclusions. Each escalation is an unsupported inferential leap.

This skill file is reasoning-only. If raw data is available, the
computational checks under Check 2 can be run using standard Python
(scikit-learn's `KMedoids` from sklearn_extra, `silhouette_score`
from sklearn.metrics, scipy hierarchical clustering). These are not
wrapped in the bullshit-detector package because they are standard
library calls, not custom detection logic.

---

## Not covered by this skill file

This skill file addresses clustering and dimensionality reduction.
It does **not** cover:

- **Variable dichotomisation** — median splits of continuous predictors,
  arbitrary cutpoints. See `variable_handling_critique.md` (planned).
- **Supervised learning diagnostics** — overfitting, train/test leakage,
  feature importance. See `outlier_leverage.md` (SHAP section).
- **Time-series clustering** — DTW distance, regime detection. Not yet
  addressed in any skill file.
- **Network/graph clustering** — community detection, modularity. Not
  yet addressed.
- **Latent class analysis / mixture models** — model-based clustering.
  Shares some failure modes with k-means (reification, k selection) but
  has its own assumptions (distributional forms). Partially covered by
  Checks 3 and 5 above.

---

## References

- Ahlqvist, E., Storm, P., Käräjämäki, A., et al. (2018). "Novel
  subgroups of adult-onset diabetes and their association with outcomes:
  a data-driven cluster analysis of six variables." *The Lancet Diabetes
  & Endocrinology*, 6(5), 361–369.
- Udler, M.S. (2019). "Type 2 Diabetes: Multiple Genes, Multiple
  Diseases." *Current Diabetes Reports*, 19, 55.
- Hennig, C. (2015). "What are the true clusters?" *Pattern Recognition
  Letters*, 64, 53–62.
- von Luxburg, U. (2010). "Clustering Stability: An Overview."
  *Foundations and Trends in Machine Learning*, 2(3), 235–274.
- Royston, P., Altman, D.G. & Sauerbrei, W. (2006). "Dichotomizing
  continuous predictors in multiple regression: a bad idea." *Statistics
  in Medicine*, 25(1), 127–141. (Cross-reference for variable_handling_critique.md.)
