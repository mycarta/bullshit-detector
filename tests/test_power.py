"""Tests for power and sample size module."""

import pytest

from bullshit_detector.power import required_n, achieved_power
# power_curve imported when implemented


class TestRequiredN:
    """Validate against Speidel (2018) and standard power tables."""

    def test_speidel_example(self):
        """Speidel: d=16, sd1=16, sd2=12, alpha=0.10, power=0.80.

        The normal approximation yields n=10; Speidel's R power.t.test
        (t-distribution) yields 11. We accept 9–12.
        """
        result = required_n(d=16, sd1=16, sd2=12, alpha=0.10, power=0.80)
        assert 9 <= result["n_per_group"] <= 12

    def test_cohens_d_medium(self):
        """Cohen's d=0.5, alpha=0.05, power=0.80 → n≈63 per group."""
        result = required_n(effect_size=0.5, alpha=0.05, power=0.80)
        assert 60 <= result["n_per_group"] <= 68

    def test_larger_effect_needs_fewer(self):
        """Larger effect size should require fewer observations."""
        n_small = required_n(effect_size=0.3, alpha=0.05, power=0.80)
        n_large = required_n(effect_size=0.8, alpha=0.05, power=0.80)
        assert n_large["n_per_group"] < n_small["n_per_group"]

    def test_one_sided_needs_fewer(self):
        """One-sided test needs fewer observations than two-sided."""
        n_two = required_n(effect_size=0.5, alpha=0.05, power=0.80,
                           alternative="two-sided")
        n_one = required_n(effect_size=0.5, alpha=0.05, power=0.80,
                           alternative="one-sided")
        assert n_one["n_per_group"] < n_two["n_per_group"]


class TestAchievedPower:
    """Test achieved power calculations."""

    def test_underpowered_study(self):
        """Medium effect, small n → low power."""
        result = achieved_power(effect_size=0.5, n_per_group=10, alpha=0.05)
        assert result["power"] < 0.30
        assert result["adequate"] is False

    def test_well_powered_study(self):
        """Large effect, decent n → high power."""
        result = achieved_power(effect_size=0.8, n_per_group=30, alpha=0.05)
        assert result["power"] > 0.80
        assert result["adequate"] is True

    def test_round_trip(self):
        """required_n then achieved_power should give back ~0.80."""
        n_result = required_n(effect_size=0.5, alpha=0.05, power=0.80)
        p_result = achieved_power(effect_size=0.5,
                                  n_per_group=n_result["n_per_group"],
                                  alpha=0.05)
        assert abs(p_result["power"] - 0.80) < 0.02
