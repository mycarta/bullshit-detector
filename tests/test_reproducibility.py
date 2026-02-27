"""Tests for reproducibility.py — error_flag and bootstrap_proportion."""

import numpy as np
import pytest

from bullshit_detector.reproducibility import bootstrap_proportion, error_flag


# ---------------------------------------------------------------------------
# error_flag tests
# ---------------------------------------------------------------------------

class TestErrorFlag:
    def test_perfect_match_no_flags(self):
        x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        result = error_flag(x, x)
        assert result["n_flagged"] == 0
        assert result["flagged_points"] == []
        assert result["fraction_flagged"] == 0.0

    def test_perfect_match_zero_abs_errors(self):
        x = np.array([1.0, 3.0, 2.0])
        result = error_flag(x, x)
        assert np.all(result["abs_errors"] == 0.0)

    def test_returns_dict_keys(self):
        x = np.array([1.0, 2.0])
        result = error_flag(x, x)
        assert set(result.keys()) == {
            "abs_errors", "slope_sign_mismatches",
            "flagged_points", "n_flagged", "fraction_flagged",
        }

    def test_known_abs_errors(self):
        predicted = np.array([1.0, 2.0, 3.0])
        actual    = np.array([0.0, 0.0, 0.0])
        result = error_flag(predicted, actual)
        np.testing.assert_array_almost_equal(result["abs_errors"], [1.0, 2.0, 3.0])

    def test_threshold_filters_correctly(self):
        predicted = np.array([0.0, 0.0, 0.0])
        actual    = np.array([0.5, 1.5, 0.3])
        result = error_flag(predicted, actual, threshold=1.0)
        # Only index 1 has abs_error = 1.5 > 1.0
        assert result["flagged_points"] == [1]
        assert result["n_flagged"] == 1
        assert result["fraction_flagged"] == pytest.approx(1 / 3)

    def test_all_flagged_when_threshold_zero_and_mismatch(self):
        predicted = np.array([1.0, 2.0, 3.0])
        actual    = np.array([2.0, 3.0, 4.0])
        result = error_flag(predicted, actual, threshold=0.0)
        assert result["n_flagged"] == 3

    def test_fraction_flagged_range(self):
        predicted = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        actual    = np.array([1.0, 2.0, 0.0, 4.0, 5.0])
        result = error_flag(predicted, actual, threshold=0.5)
        assert 0.0 <= result["fraction_flagged"] <= 1.0

    def test_slope_sign_mismatch_detected(self):
        # predicted rises then falls; actual rises then rises → mismatch at index 2
        predicted = np.array([1.0, 3.0, 2.0])
        actual    = np.array([1.0, 2.0, 3.0])
        result = error_flag(predicted, actual)
        assert 2 in result["slope_sign_mismatches"]

    def test_no_slope_mismatch_parallel_curves(self):
        # Both curves always move in the same direction
        predicted = np.array([1.0, 2.0, 3.0, 4.0])
        actual    = np.array([2.0, 3.0, 4.0, 5.0])
        result = error_flag(predicted, actual)
        assert result["slope_sign_mismatches"] == []

    def test_accepts_lists(self):
        result = error_flag([1.0, 2.0, 3.0], [1.0, 2.0, 3.0])
        assert result["n_flagged"] == 0

    def test_shape_mismatch_raises(self):
        with pytest.raises(ValueError):
            error_flag(np.array([1.0, 2.0]), np.array([1.0, 2.0, 3.0]))

    def test_abs_errors_length_matches_input(self):
        n = 10
        x = np.random.default_rng(0).normal(size=n)
        result = error_flag(x, x * 1.1)
        assert len(result["abs_errors"]) == n

    def test_multiple_slope_mismatches(self):
        # Zigzag predicted vs monotone actual → many mismatches
        predicted = np.array([0.0, 2.0, 0.0, 2.0, 0.0])
        actual    = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
        result = error_flag(predicted, actual)
        assert len(result["slope_sign_mismatches"]) >= 2


# ---------------------------------------------------------------------------
# bootstrap_proportion tests
# ---------------------------------------------------------------------------

class TestBootstrapProportion:
    def test_returns_dict_keys(self):
        data = np.array([1, 0, 1, 1, 0])
        result = bootstrap_proportion(data, lambda x: x == 1,
                                      n_boot=100, random_state=0)
        assert set(result.keys()) == {
            "proportion", "ci_lower", "ci_upper",
            "n_boot", "bootstrap_proportions",
        }

    def test_proportion_correct(self):
        data = np.array([1] * 70 + [0] * 30)
        result = bootstrap_proportion(data, lambda x: x == 1,
                                      n_boot=200, random_state=0)
        assert result["proportion"] == pytest.approx(0.7)

    def test_ci_contains_true_proportion(self):
        data = np.array([1] * 70 + [0] * 30)
        result = bootstrap_proportion(data, lambda x: x == 1,
                                      n_boot=5000, ci=0.95, random_state=42)
        assert result["ci_lower"] < 0.7 < result["ci_upper"]

    def test_ci_ordered(self):
        data = np.array([1] * 50 + [0] * 50)
        result = bootstrap_proportion(data, lambda x: x == 1,
                                      n_boot=500, random_state=1)
        assert result["ci_lower"] <= result["proportion"] <= result["ci_upper"]

    def test_bootstrap_proportions_length(self):
        data = np.arange(20)
        result = bootstrap_proportion(data, lambda x: x > 10,
                                      n_boot=300, random_state=0)
        assert len(result["bootstrap_proportions"]) == 300

    def test_n_boot_in_output(self):
        data = np.ones(10)
        result = bootstrap_proportion(data, lambda x: x > 0,
                                      n_boot=250, random_state=0)
        assert result["n_boot"] == 250

    def test_reproducible_with_random_state(self):
        data = np.array([1] * 40 + [0] * 60)
        r1 = bootstrap_proportion(data, lambda x: x == 1,
                                  n_boot=500, random_state=7)
        r2 = bootstrap_proportion(data, lambda x: x == 1,
                                  n_boot=500, random_state=7)
        np.testing.assert_array_equal(r1["bootstrap_proportions"],
                                      r2["bootstrap_proportions"])

    def test_different_seeds_differ(self):
        data = np.array([1] * 40 + [0] * 60)
        r1 = bootstrap_proportion(data, lambda x: x == 1,
                                  n_boot=500, random_state=1)
        r2 = bootstrap_proportion(data, lambda x: x == 1,
                                  n_boot=500, random_state=2)
        assert not np.array_equal(r1["bootstrap_proportions"],
                                   r2["bootstrap_proportions"])

    def test_ci_width_shrinks_with_more_data(self):
        rng = np.random.default_rng(0)
        small = rng.integers(0, 2, size=30)
        large = rng.integers(0, 2, size=300)
        r_small = bootstrap_proportion(small, lambda x: x == 1,
                                       n_boot=1000, ci=0.95, random_state=0)
        r_large = bootstrap_proportion(large, lambda x: x == 1,
                                       n_boot=1000, ci=0.95, random_state=0)
        width_small = r_small["ci_upper"] - r_small["ci_lower"]
        width_large = r_large["ci_upper"] - r_large["ci_lower"]
        assert width_large < width_small

    def test_all_true_proportion_is_one(self):
        data = np.ones(50)
        result = bootstrap_proportion(data, lambda x: x > 0,
                                      n_boot=200, random_state=0)
        assert result["proportion"] == pytest.approx(1.0)

    def test_none_true_proportion_is_zero(self):
        data = np.zeros(50)
        result = bootstrap_proportion(data, lambda x: x > 0,
                                      n_boot=200, random_state=0)
        assert result["proportion"] == pytest.approx(0.0)

    def test_condition_fn_with_float_threshold(self):
        data = np.linspace(0, 1, 100)
        result = bootstrap_proportion(data, lambda x: x > 0.5,
                                      n_boot=500, random_state=0)
        # ~49 of 100 values exceed 0.5
        assert 0.45 < result["proportion"] < 0.55
