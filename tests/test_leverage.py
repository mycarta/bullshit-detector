"""Tests for leverage.py — influence_plot and distance_correlation_test."""

import numpy as np
import pytest

pytest.importorskip("statsmodels", reason="statsmodels required")
pytest.importorskip("dcor", reason="dcor required")
pytest.importorskip("matplotlib", reason="matplotlib required")

from bullshit_detector.leverage import distance_correlation_test, influence_plot


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def linear_data():
    """Near-perfect linear relationship, no influential outliers."""
    rng = np.random.default_rng(42)
    x = np.linspace(0, 1, 12)
    y = 3.0 * x + rng.normal(0, 0.05, 12)
    return x, y


@pytest.fixture
def outlier_data():
    """Linear data with one extreme leverage point appended."""
    rng = np.random.default_rng(42)
    x = np.linspace(0, 1, 9)
    y = 3.0 * x + rng.normal(0, 0.1, 9)
    # Append a high-leverage point far from the cluster
    x = np.append(x, 5.0)
    y = np.append(y, 0.5)
    return x, y


@pytest.fixture
def independent_data():
    """Two statistically independent vectors."""
    rng = np.random.default_rng(0)
    x = rng.normal(0, 1, 50)
    y = rng.normal(0, 1, 50)
    return x, y


@pytest.fixture
def dependent_data():
    """Two strongly dependent vectors."""
    rng = np.random.default_rng(0)
    x = rng.normal(0, 1, 50)
    y = x ** 2 + rng.normal(0, 0.1, 50)  # non-linear but dependent
    return x, y


# ---------------------------------------------------------------------------
# influence_plot tests
# ---------------------------------------------------------------------------

class TestInfluencePlot:
    def test_returns_dict_keys(self, linear_data):
        x, y = linear_data
        result = influence_plot(x, y)
        assert set(result.keys()) == {"model", "cooks_distance", "high_leverage",
                                      "high_residual", "cc"}

    def test_cooks_distance_length(self, linear_data):
        x, y = linear_data
        result = influence_plot(x, y)
        assert len(result["cooks_distance"]) == len(x)

    def test_cooks_distance_non_negative(self, linear_data):
        x, y = linear_data
        result = influence_plot(x, y)
        assert np.all(result["cooks_distance"] >= 0)

    def test_cc_range(self, linear_data):
        x, y = linear_data
        result = influence_plot(x, y)
        assert -1.0 <= result["cc"] <= 1.0

    def test_cc_near_one_for_linear(self, linear_data):
        x, y = linear_data
        result = influence_plot(x, y)
        assert result["cc"] > 0.99

    def test_high_leverage_indices_are_ints(self, linear_data):
        x, y = linear_data
        result = influence_plot(x, y)
        assert all(isinstance(i, (int, np.integer)) for i in result["high_leverage"])

    def test_outlier_flagged_as_high_leverage(self, outlier_data):
        """The extreme point at x=5 should appear in high_leverage."""
        x, y = outlier_data
        result = influence_plot(x, y)
        # Index 9 is the appended outlier
        assert 9 in result["high_leverage"]

    def test_accepts_axes_argument(self, linear_data):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        plt.close("all")
        x, y = linear_data
        fig, ax = plt.subplots()
        result = influence_plot(x, y, ax=ax)
        assert result is not None
        plt.close(fig)

    def test_leverage_threshold_uses_k(self, linear_data):
        """Threshold 2*(k+1)/n must equal 4/n for simple OLS (k=1)."""
        x, y = linear_data
        n = len(x)
        result = influence_plot(x, y)
        expected_threshold = 4 / n
        hat = result["model"].get_influence().hat_matrix_diag
        flagged = list(np.where(hat > expected_threshold)[0])
        assert result["high_leverage"] == flagged


# ---------------------------------------------------------------------------
# distance_correlation_test tests
# ---------------------------------------------------------------------------

class TestDistanceCorrelationTest:
    def test_returns_dict_keys(self, linear_data):
        x, y = linear_data
        result = distance_correlation_test(x, y, num_resamples=200)
        assert set(result.keys()) == {"dcor", "p_value", "significant"}

    def test_dcor_range(self, linear_data):
        x, y = linear_data
        result = distance_correlation_test(x, y, num_resamples=200)
        assert 0.0 <= result["dcor"] <= 1.0

    def test_p_value_range(self, linear_data):
        x, y = linear_data
        result = distance_correlation_test(x, y, num_resamples=200)
        assert 0.0 <= result["p_value"] <= 1.0

    def test_significant_is_bool(self, linear_data):
        x, y = linear_data
        result = distance_correlation_test(x, y, num_resamples=200)
        assert isinstance(result["significant"], bool)

    def test_significant_consistent_with_p_value(self, linear_data):
        x, y = linear_data
        result = distance_correlation_test(x, y, num_resamples=200)
        assert result["significant"] == (result["p_value"] < 0.05)

    def test_strong_dependence_high_dcor(self, dependent_data):
        """Strongly dependent data should yield high distance correlation."""
        x, y = dependent_data
        result = distance_correlation_test(x, y, num_resamples=200)
        assert result["dcor"] > 0.5

    def test_strong_dependence_significant(self, dependent_data):
        """Strongly dependent data should yield a significant p-value."""
        x, y = dependent_data
        result = distance_correlation_test(x, y, num_resamples=500)
        assert result["significant"]

    def test_independence_low_dcor(self, independent_data):
        """Independent data should yield low distance correlation."""
        x, y = independent_data
        result = distance_correlation_test(x, y, num_resamples=200)
        assert result["dcor"] < 0.3
