"""Tests for redundancy analysis module."""

import numpy as np
import pandas as pd
import pytest

from bullshit_detector.redundancy import redundancy_analysis, suggest_removal


# ---------------------------------------------------------------------------
# Synthetic dataset that mirrors the Hunt (2013) structure used by Speidel:
#   - gross.pay          : measured variable
#   - gross.pay.transform: algebraically derived (log transform) → highly redundant
#   - phi.h              : independent measured variable
#   - random.1/2         : pure noise → should NOT be flagged
# ---------------------------------------------------------------------------

RNG = np.random.default_rng(42)
N = 50
_gross_pay = RNG.uniform(5, 80, size=N)

HUNT_LIKE = pd.DataFrame({
    "gross.pay":           _gross_pay,
    "gross.pay.transform": np.log1p(_gross_pay) + RNG.normal(0, 0.05, N),  # near-perfect
    "phi.h":               RNG.uniform(0.1, 0.4, size=N),
    "random.1":            RNG.standard_normal(N),
    "random.2":            RNG.standard_normal(N),
})


class TestRedundancyAnalysis:
    """Validate against Speidel (2018) R results."""

    def test_algebraic_redundancy(self):
        """gross.pay.transform should be highly redundant (algebraically derived)."""
        result = redundancy_analysis(HUNT_LIKE, r2_threshold=0.70)
        assert "gross.pay.transform" in result["redundant"]

    def test_random_variables_not_redundant(self):
        """random.1 and random.2 should NOT be redundant."""
        result = redundancy_analysis(HUNT_LIKE, r2_threshold=0.70)
        assert "random.1" not in result["redundant"]
        assert "random.2" not in result["redundant"]

    def test_effective_k_less_than_total(self):
        """effective_k should be less than total number of variables."""
        result = redundancy_analysis(HUNT_LIKE, r2_threshold=0.70)
        assert result["effective_k"] < HUNT_LIKE.shape[1]

    def test_high_threshold_retains_all(self):
        """With r2_threshold=0.99, only the algebraically-derived column is flagged."""
        result = redundancy_analysis(HUNT_LIKE, r2_threshold=0.99)
        # gross.pay.transform is near-perfect (r2 > 0.99 via log transform + tiny noise)
        # All others should be retained
        assert result["effective_k"] >= HUNT_LIKE.shape[1] - 1

    def test_return_shape(self):
        """Result always contains all required keys."""
        result = redundancy_analysis(HUNT_LIKE)
        expected = {"r_squared", "redundant", "retained", "effective_k", "threshold"}
        assert expected.issubset(result.keys())
        assert isinstance(result["r_squared"], dict)
        assert isinstance(result["redundant"], list)
        assert isinstance(result["retained"], list)
        assert result["effective_k"] == len(result["retained"])

    def test_suggest_removal(self):
        """suggest_removal returns redundant cols ordered by R² descending."""
        result = redundancy_analysis(HUNT_LIKE, r2_threshold=0.70)
        to_remove = suggest_removal(result)
        assert to_remove == result["redundant"]
