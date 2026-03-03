# Unsupervised Learning Critique Skill

> **Purpose:** A reasoning framework for auditing papers that use clustering,
> dimensionality reduction, or other unsupervised methods to identify structure
> in data. No code module — this is a checklist for human or LLM reasoning.
>
> **When to use:** Any paper that reports "groups", "subtypes", "clusters",
> "communities", or "archetypes" derived from an algorithm rather than from
> prior clinical, physical, or theoretical criteria.
>
> **Origin:** Developed from Thomas Speidel's test cases, anchored to
> Ahlqvist et al. (2018) as the canonical worked example.

---

## The four checks

Work through these in order. Each targets a distinct failure mode. A paper
can fail any one of them while passing the others — flag each separately.

---

### 1. Cluster reification

**The problem:** An algorithm partitions data into groups. The paper then
treats those groups as real, pre-existing entities — subtypes of a disease,
customer segments, geological facies — as if the algorithm *discovered*
something that was there rather than *imposed* a partition on a continuous
distribution.

**What to look for in the paper:**
- Does the paper test whether the continuous distribution is actually
  multimodal? A unimodal distribution clustered into k groups produces
  k interpretable-looking clusters that mean nothing.
- Is there a distributional test (Hartigan's dip test, Silverman bandwidth
  test, mclust model comparison) showing that the data support discrete
  groups rather than a continuum?
- Are the cluster boundaries treated as sharp when the underlying variables
  are continuous?

**Red flags:**
- "We identified five distinct subtypes" — "distinct" is doing enormous work.
  Was distinctness tested or assumed?
- Clusters reported with means and standard deviations, no overlap shown.
  Overlapping distributions can still be clustered; the overlap tells you
  how distinct the groups really are.
- Clinical or operational decisions tied to cluster membership without
  uncertainty quantification. If a patient near the boundary of two clusters
  gets a different treatment depending on cluster label, that's a problem.
- No comparison to a simpler model. Does the k-cluster solution predict
  outcomes better than a single continuous score on the most important
  variable?

**Green flags:**
- Authors test for multimodality explicitly.
- Confidence or uncertainty in cluster assignment reported (soft
  clustering, posterior probabilities from a mixture model).
- Authors explicitly state that clusters are operational summaries, not
  discovered natural kinds.

**Worked example — Ahlqvist et al. (2018):**
Ahlqvist et al. applied k-means clustering (k=5) to six continuous variables
(GADA positivity, age at diagnosis, BMI, HbA1c, HOMA2-B, HOMA2-IR) in
8,980 Swedish patients and named the resulting groups as putative diabetes
subtypes (SAID, SIDD, SIRD, MOD, MARD). The paper generated enormous
clinical interest, yet the five k=5 centroids were never tested against
k=4 or k=6, nor was multimodality in the six input variables demonstrated.
Subsequent replication studies (e.g., Zaharia et al. 2019, Udler et al. 2019)
found that the clusters were not stable across cohorts and did not map cleanly
onto distinct biological mechanisms. The clusters were real as algorithmic
outputs; whether they were real as disease entities remained contested.

---

### 2. Centroid vs. medoid — does the representative patient exist?

**The problem:** k-means minimises within-cluster sum of squared distances
to the cluster *centroid* — the mean of each variable across cluster members.
The centroid is a mathematical point that may not correspond to any actual
observation. Interpreting the centroid as "the typical patient in this group"
is only appropriate if the distribution within each cluster is approximately
symmetric and unimodal. For binary or bounded variables (e.g., antibody
positivity in Ahlqvist), a centroid value of 0.3 is not a real patient —
it is an average of zeroes and ones.

**What to look for in the paper:**
- Are cluster summaries reported as means? If any input variables are
  binary or bounded, the centroid is not a real observation.
- Does the paper present a "representative case" or "prototype patient"?
  Is it an actual observation (medoid) or a constructed centroid?
- Would k-medoids clustering (PAM — Partitioning Around Medoids) have
  been more appropriate? It returns actual data points as cluster centres,
  making the representative patient real.

**Red flags:**
- Binary input variables but means reported as cluster summaries. A cluster
  with a mean GADA of 0.4 is a mix of antibody-positive and antibody-negative
  patients — it is not a low-GADA subtype.
- "Cluster 3 is characterised by high BMI and moderate insulin resistance" —
  is this describing an actual patient or a centroid?
- No uncertainty around cluster centres reported.

**Green flags:**
- k-medoids used, or medoids explicitly reported alongside centroids.
- Cluster plots show actual data points, not just centroid markers.
- Distribution of each variable within each cluster shown (violin plots,
  boxplots) so the reader can judge whether the centroid is representative.

---

### 3. Stability — would different choices produce the same clusters?

**The problem:** Clustering results depend on: (a) the number of clusters k,
(b) the initialisation seed (for k-means), (c) the distance metric, (d) the
variables included, (e) the sample. A result that changes substantially under
any of these perturbations is not a stable finding.

**What to look for in the paper:**
- Is there a justification for the chosen k? Common internal criteria include
  the elbow method (within-cluster sum of squares vs. k), silhouette scores,
  gap statistic, or information criteria from mixture models (BIC/AIC from
  mclust). Were multiple values of k tested?
- Was stability under resampling evaluated? Bootstrap resampling with the
  Jaccard similarity index (Hennig 2007) or consensus clustering are standard.
  A cluster with Jaccard < 0.6 is considered unstable.
- Was external validation performed? Do the clusters predict outcomes in a
  held-out sample or a different cohort?

**Red flags:**
- k chosen by visual inspection of a dendrogram or by clinical preference,
  not by a data-driven criterion from the training set.
- Single random seed used for k-means with no stability check.
- No held-out set or external cohort validation.
- "The clusters were replicated in a validation cohort" — but replication
  was done by assigning new patients to the training-set centroids, not
  by running clustering independently on the new cohort and checking that
  the same structure emerged.

**Green flags:**
- Multiple k values tested with an internal validity index, k chosen
  at the elbow or maximum silhouette.
- Bootstrap stability reported (Jaccard, cophenetic correlation, or
  consensus clustering heatmap).
- Independent cohort ran clustering separately and found consistent
  structure (not just nearest-centroid assignment).

**Worked example — Ahlqvist et al. (2018):**
The original paper did not report stability analysis. Udler et al. (2019)
subsequently showed that a genetic factor model (using GWAS data) partially
supported the subtype concept, but with different boundaries. Zaharia et al.
(2019) could not fully replicate the five-cluster structure in a German cohort.
These are textbook failure modes of cluster reification without stability
testing: the clusters were stable enough within the training cohort to look
compelling, but not stable enough across cohorts to be treated as natural kinds.

---

### 4. Dimensionality reduction as evidence

**The problem:** Papers routinely show PCA, t-SNE, or UMAP plots with
cluster labels overlaid to "demonstrate" that the clusters are visually
distinct. This reasoning is circular and unreliable.

- PCA is linear and will not reveal non-linear structure. Clusters that
  look overlapping in PCA may be well-separated in higher dimensions and
  vice versa.
- t-SNE and UMAP *always* produce visually distinct blobs given enough
  perplexity/neighbour tuning, even for random data. The visual separation
  is partly a function of the algorithm parameters, not just the data.
- If the cluster labels were derived from the same data shown in the plot,
  the plot is not independent evidence of cluster structure — it is a
  visualisation of the algorithm's own output.

**What to look for in the paper:**
- Is the dimensionality reduction used exploratorily (to visualise data
  before clustering) or presentationally (to show clusters discovered
  by a separate algorithm)?
- If t-SNE/UMAP is used, are the perplexity/neighbour parameters reported?
  Were multiple parameter values tried?
- Is there any between-cluster overlap visible in the plot? Authors sometimes
  select projection axes or parameters that maximise apparent separation.

**Red flags:**
- "The PCA/t-SNE/UMAP plot confirms five distinct clusters" — a projection
  onto 2D is not confirmation. It is a visualisation subject to heavy
  parameterisation choices.
- UMAP or t-SNE plot shown but hyperparameters not reported.
- The same data used to fit clusters and to produce the plot that "validates"
  them.
- Authors describe the 2D plot without mentioning that most variance is in
  higher dimensions.

**Green flags:**
- Plot clearly labelled as exploratory or descriptive, not confirmatory.
- Hyperparameters stated and at least one sensitivity check shown.
- Quantitative cluster separation reported (e.g., between-cluster vs.
  within-cluster variance ratio, silhouette scores) in addition to visual.
- Dimensionality reduction applied to held-out data, not just training data.

---

## Overall verdict framework

Assess each check independently, then combine:

| Check | PASS | CAUTION | FLAG |
|---|---|---|---|
| Reification | Multimodality tested or soft clustering used | Clusters reported as discrete without explicit test | No distributional test; groups named as natural kinds |
| Centroid/medoid | Medoids reported or all inputs continuous and symmetric | Means reported with bounded inputs, acknowledged | Binary inputs; centroids described as representative patients |
| Stability | k justified, bootstrap stability reported, external validation | Some stability checks but incomplete | Single k, no seed sensitivity, in-sample validation only |
| Dimensionality reduction | Used exploratorily with stated hyperparameters | Shown without hyperparameters | Described as evidence for cluster structure |

**FLAG on any single check is sufficient to warrant escalation.** Note in
audit which check failed and why. Multiple FLAGs indicate a paper where the
claimed discovery structure is largely algorithmic artefact.

---

## Routing

- Cluster instability + many input features → `spurious.P_spurious()` (many
  variables, small N inflates chance of finding apparent structure)
- Clusters used to predict an outcome → `power.power_from_paper()` (underpowered
  subgroup analyses within clusters are common)
- Clusters used in a regression → `leverage.influence_plot()` (extreme
  observations can anchor a centroid)
- Causal claims attached to cluster membership → `causal_consistency.md`

---

## References

- Ahlqvist et al. (2018), "Novel subgroups of adult-onset diabetes and
  their association with outcomes: a data-driven cluster analysis of six
  variables", *The Lancet Diabetes & Endocrinology*, 6(5), 361–369.
  https://doi.org/10.1016/S2213-8587(18)30051-2
- Hennig (2007), "Cluster-wise assessment of cluster stability",
  *Computational Statistics & Data Analysis*, 52(1), 258–271.
- Kaufman & Rousseeuw (1990), *Finding Groups in Data: An Introduction
  to Cluster Analysis*, Wiley. (k-medoids / PAM)
- Udler et al. (2019), "Type 2 diabetes genetic loci informed by
  multi-trait associations point to disease mechanisms and subtypes",
  *PLOS Genetics*, 14(9), e1007654.
- Zaharia et al. (2019), "High risk of failure of the novel subgroups of
  type 2 diabetes in an external cohort", *Annals of Internal Medicine*,
  170(5), 360–361.
- Wattenberg, Viégas & Johnson (2016), "How to use t-SNE effectively",
  *Distill*. https://doi.org/10.23915/distill.00002
  (t-SNE parameter sensitivity)
- McInnes, Healy & Melville (2018), "UMAP: Uniform Manifold Approximation
  and Projection for Dimension Reduction", arXiv:1802.03426.
  (UMAP parameter sensitivity)
