# Spurious Correlation Skill (Tier 2)

> Detailed worked examples to be written after code is stable.
> See spurious.py docstrings for function descriptions.
> See Session_Handoff_05.md for implementation notes and source references.

## Notes for worked examples

**Positive example (adequate sample size):** Roure & Perez (2025), "Maximizing
field development through rock physics informed hi-res ML seismic estimates of
reservoir properties", GeoConvention 2025. Hundreds of wells in the Llanos Basin,
Colombia. With n this large, Kalkomey's P_spurious is negligible even for many
attributes. Good contrast case against the 5-well scenarios Kalkomey warns about.
Also uses SHAP (Explainable AI) for model QC — note that SHAP explains *why a
model predicts what it does*, which is a different question from *whether to believe
the prediction*. The bullshit-detector tools answer the latter.

**Negative examples (from Kalkomey 1997):** 5 wells, 10 attributes, r≥0.6 →
96% chance at least one correlation is spurious. Even doubling to 10 wells → still
50%. These are the cases where the detector adds the most value.
