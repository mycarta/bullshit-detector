"""Tests for dc_cluster.py — dist_corr, dc_matrix, effective_k."""

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("dcor", reason="dcor required")
pytest.importorskip("scipy", reason="scipy required")

from bullshit_detector.dc_cluster import dc_matrix, dist_corr, effective_k


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def rng():
    return np.random.default_rng(42)


@pytest.fixture
def correlated_df(rng):
    """DataFrame where 'a' and 'b' are perfectly correlated; 'c' is independent."""
    x = rng.normal(size=60)
    return pd.DataFrame({
        "a": x,
        "b": x * 3.0 + 1.0,   # linear copy → DC = 1
        "c": rng.normal(size=60),
    })


@pytest.fixture
def independent_df(rng):
    """DataFrame of three independent normal variables."""
    return pd.DataFrame({
        "p": rng.normal(size=80),
        "q": rng.normal(size=80),
        "r": rng.normal(size=80),
    })


# ---------------------------------------------------------------------------
# dist_corr tests
# ---------------------------------------------------------------------------

class TestDistCorr:
    def test_returns_float(self, rng):
        x, y = rng.normal(size=20), rng.normal(size=20)
        assert isinstance(dist_corr(x, y), float)

    def test_range_zero_to_one(self, rng):
        x, y = rng.normal(size=30), rng.normal(size=30)
        val = dist_corr(x, y)
        assert 0.0 <= val <= 1.0

    def test_identical_vectors_is_one(self):
        x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        assert dist_corr(x, x) == pytest.approx(1.0, abs=1e-6)

    def test_negated_vector_is_one(self):
        """DC is symmetric and monotone-invariant — negation keeps DC=1."""
        x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        assert dist_corr(x, -x) == pytest.approx(1.0, abs=1e-6)

    def test_linear_relationship_near_one(self, rng):
        x = np.linspace(0, 10, 50)
        y = 2.5 * x + rng.normal(0, 0.01, 50)
        assert dist_corr(x, y) > 0.99

    def test_accepts_lists(self):
        x = [1.0, 2.0, 3.0, 4.0]
        y = [2.0, 4.0, 6.0, 8.0]
        val = dist_corr(x, y)
        assert 0.0 <= val <= 1.0


# ---------------------------------------------------------------------------
# dc_matrix tests
# ---------------------------------------------------------------------------

class TestDcMatrix:
    def test_returns_dataframe(self, correlated_df):
        result = dc_matrix(correlated_df)
        assert isinstance(result, pd.DataFrame)

    def test_square(self, correlated_df):
        result = dc_matrix(correlated_df)
        assert result.shape == (3, 3)

    def test_column_and_index_names(self, correlated_df):
        result = dc_matrix(correlated_df)
        assert list(result.columns) == list(correlated_df.columns)
        assert list(result.index) == list(correlated_df.columns)

    def test_diagonal_is_one(self, correlated_df):
        result = dc_matrix(correlated_df)
        for col in correlated_df.columns:
            assert result.loc[col, col] == pytest.approx(1.0, abs=1e-6)

    def test_symmetric(self, correlated_df):
        result = dc_matrix(correlated_df)
        for i in correlated_df.columns:
            for j in correlated_df.columns:
                assert result.loc[i, j] == pytest.approx(result.loc[j, i], abs=1e-10)

    def test_values_in_range(self, correlated_df):
        result = dc_matrix(correlated_df)
        assert (result.values >= 0.0).all()
        assert (result.values <= 1.0 + 1e-9).all()

    def test_correlated_pair_near_one(self, correlated_df):
        """'a' and 'b' are linearly related — their DC should be ~1."""
        result = dc_matrix(correlated_df)
        assert result.loc["a", "b"] > 0.99

    def test_two_column_df(self, rng):
        df = pd.DataFrame({"x": rng.normal(size=20), "y": rng.normal(size=20)})
        result = dc_matrix(df)
        assert result.shape == (2, 2)


# ---------------------------------------------------------------------------
# effective_k tests
# ---------------------------------------------------------------------------

class TestEffectiveK:
    def test_returns_dict_keys(self, correlated_df):
        result = effective_k(correlated_df)
        assert set(result.keys()) == {"n_clusters", "cluster_labels",
                                      "dc_matrix", "dendrogram_data"}

    def test_n_clusters_is_int(self, correlated_df):
        result = effective_k(correlated_df)
        assert isinstance(result["n_clusters"], int)

    def test_cluster_labels_length(self, correlated_df):
        result = effective_k(correlated_df)
        assert len(result["cluster_labels"]) == len(correlated_df.columns)

    def test_dc_matrix_returned(self, correlated_df):
        result = effective_k(correlated_df)
        assert isinstance(result["dc_matrix"], pd.DataFrame)
        assert result["dc_matrix"].shape == (3, 3)

    def test_perfectly_correlated_grouped(self, correlated_df):
        """'a' and 'b' are linearly identical → they should share a cluster.
        Three variables with one redundant pair → 2 effective groups."""
        result = effective_k(correlated_df, threshold=0.5)
        assert result["n_clusters"] == 2

    def test_independent_variables_separate_clusters(self, independent_df):
        """Three independent variables should each get their own cluster
        when threshold is tight (< typical DC between random noise)."""
        result = effective_k(independent_df, threshold=0.05)
        assert result["n_clusters"] == 3

    def test_threshold_affects_n_clusters(self, correlated_df):
        """Loose threshold collapses everything; tight threshold splits more."""
        loose = effective_k(correlated_df, threshold=0.99)
        tight = effective_k(correlated_df, threshold=0.01)
        assert loose["n_clusters"] <= tight["n_clusters"]

    def test_dendrogram_data_is_dict(self, correlated_df):
        result = effective_k(correlated_df)
        assert isinstance(result["dendrogram_data"], dict)
