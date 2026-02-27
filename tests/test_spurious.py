"""Tests for spurious correlation module — validate against Kalkomey (1997)."""

import pytest

from bullshit_detector.spurious import P_spurious, r_crit, conf_int


class TestPSpurious:
    """Validate P_spurious against Kalkomey Table 1 (k=1) and Table 3 (k=10)."""

    def test_table1_high_r_many_wells(self):
        """R=0.9, n=100, k=1 → P_spurious ≈ 0."""
        result = P_spurious(0.9, 100, 1)
        assert result < 0.001

    def test_table1_low_r_few_wells(self):
        """R=0.3, n=5, k=1 → P_spurious is high."""
        result = P_spurious(0.3, 5, 1)
        assert result > 0.5

    def test_multi_attribute_amplification(self):
        """More attributes → higher spurious probability."""
        p1 = P_spurious(0.6, 5, 1)
        p10 = P_spurious(0.6, 5, 10)
        assert p10 > p1

    def test_kalkomey_key_example(self):
        """5 wells, 10 attributes, r≥0.6 → ~96% spurious."""
        result = P_spurious(0.6, 5, 10)
        assert result > 0.90


class TestRCrit:
    """Validate r_crit against known values."""

    def test_21_wells(self):
        """21 wells, alpha=0.025 → r_crit ≈ 0.433."""
        result = r_crit(21)
        assert abs(result - 0.433) < 0.005

    def test_5_wells(self):
        """5 wells → r_crit ≈ 0.878 (need very high r)."""
        result = r_crit(5)
        assert abs(result - 0.878) < 0.005


class TestConfInt:
    """Validate conf_int against Notebook E examples."""

    def test_broad_ci(self):
        """r=0.73, n=9 → CI ≈ (0.13, 0.94), very broad."""
        lo, hi = conf_int(0.73, 9)
        assert lo < 0.2
        assert hi > 0.90

    def test_tight_ci_after_outlier_removal(self):
        """r=0.90, n=8 → CI ≈ (0.53, 0.98), tighter."""
        lo, hi = conf_int(0.90, 8)
        assert lo > 0.4
        assert hi > 0.95
