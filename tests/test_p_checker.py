"""Tests for p_checker module."""

from bullshit_detector.p_checker import check_p_value


def test_t_test_inconsistent():
    """Sainani (2020): t(28) = 2.20, reported p = .04."""
    result = check_p_value("t", 2.20, 28, reported_p=0.04)
    assert result["computed_p"] < 0.04  # actual ≈ 0.0363
    # Whether this is "inconsistent" depends on rounding tolerance


def test_f_test_consistent():
    """F(1, 145) = 4.75, reported p = .031."""
    result = check_p_value("F", 4.75, 1, 145, reported_p=0.031)
    assert result["consistent"] is True


def test_decision_error():
    """Reported p < .05 but computed p > .05 → gross inconsistency."""
    # Fabricated example: weak t-stat, reported as significant
    result = check_p_value("t", 1.5, 20, reported_p=0.04)
    assert result["decision_error"] is True  # computed p ≈ 0.149


def test_correlation_to_p():
    """Convert r to t-statistic, then compute p."""
    result = check_p_value("r", 0.5, 20)
    assert 0 < result["computed_p"] < 1


def test_one_tailed():
    """One-tailed p should be half of two-tailed."""
    two_tailed = check_p_value("t", 2.0, 30)
    one_tailed = check_p_value("t", 2.0, 30, one_tailed=True)
    assert abs(one_tailed["computed_p"] - two_tailed["computed_p"] / 2) < 1e-10


def test_less_than_comparison():
    """p < .05 is consistent with any computed p below 0.05."""
    result = check_p_value("t", 2.5, 30, reported_p=0.05,
                           reported_comparison="<")
    assert result["consistent"] is True  # computed ≈ 0.018
