"""Tests for A-GRIMMER module — validate against Allard (2018)."""

import pytest

from bullshit_detector.grimmer import a_grimmer


class TestAGrimmer:
    """Validate against Allard's known test cases."""

    def test_pizzagate_inconsistent(self):
        """Wansink paper: n=18, mean=3.44, SD=2.47 → GRIMMER inconsistent."""
        result = a_grimmer(n=18, mean=3.44, sd=2.47)
        assert result["result"] == "GRIMMER inconsistent"

    def test_grim_failure(self):
        """n=10, mean=3.45 → GRIM inconsistent (3.45 × 10 = 34.5)."""
        result = a_grimmer(n=10, mean=3.45, sd=1.50)
        assert result["result"] == "GRIM inconsistent"

    def test_consistent_values(self):
        """Known consistent values should pass.

        Data = [1,2,3,4,5,6,7,1,2,3], n=10, mean=3.40.
        sum_sq = 154, var = (154 - 10*3.4^2)/9 = 38.4/9, SD ≈ 2.07.
        """
        result = a_grimmer(n=10, mean=3.40, sd=2.07)
        assert result["result"] == "consistent"

    def test_large_n_skipped(self):
        """n > 10^decimals_mean → GRIM cannot be applied."""
        result = a_grimmer(n=1000, mean=3.44, sd=2.47)
        assert result["grim_passed"] is None  # inapplicable, not a failure
