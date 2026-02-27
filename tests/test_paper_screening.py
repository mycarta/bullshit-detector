"""Tests for paper screening module — validate API lookups."""

import pytest

from bullshit_detector.paper_screening import (
    check_journal,
    check_retraction,
    check_author,
)


class TestCheckJournal:
    """Test DOAJ + OpenAlex journal lookups."""

    def test_known_good_journal(self):
        """Nature should be found in OpenAlex with high citation count."""
        result = check_journal("Nature")
        assert result["works_count"] > 100000

    def test_predatory_journal(self):
        """Dove Press journal from Bergstrom & West example — result has correct shape."""
        result = check_journal("Diabetes, Metabolic Syndrome, and Obesity")
        expected_keys = {"in_doaj", "publisher", "works_count", "cited_by_count", "is_oa", "issn"}
        assert expected_keys.issubset(result.keys())

    def test_issn_lookup(self):
        """Should work with ISSN as well as name."""
        result = check_journal("0028-0836")  # Nature's ISSN
        expected_keys = {"in_doaj", "publisher", "works_count", "cited_by_count", "is_oa", "issn"}
        assert expected_keys.issubset(result.keys())
        assert isinstance(result["works_count"], int)


class TestCheckRetraction:
    """Test CrossRef + PubPeer lookups."""

    def test_retracted_paper(self):
        """Green coffee extract paper should show retracted."""
        result = check_retraction("10.2147/DMSO.S27665")
        assert result["retracted"] is True

    def test_clean_paper(self):
        """A known-good paper should not be retracted."""
        result = check_retraction("10.1038/s41586-020-2649-2")
        assert result["retracted"] is False

    def test_return_shape(self):
        """Result always has required keys."""
        result = check_retraction("10.2147/DMSO.S27665")
        expected = {"retracted", "corrections", "pubpeer_comments", "pubpeer_url"}
        assert expected.issubset(result.keys())
        assert isinstance(result["corrections"], list)


class TestCheckAuthor:
    """Test OpenAlex author lookups."""

    def test_prolific_author(self):
        """Well-known researcher should have substantial record."""
        result = check_author("Carl T. Bergstrom")
        assert result["works_count"] > 100
        assert result["h_index"] > 20

    def test_unknown_author(self):
        """Author with minimal or no record should have low counts."""
        result = check_author("Mysore V. Nagendran")
        assert result["works_count"] < 5

    def test_return_shape(self):
        """Result always has all required keys regardless of lookup outcome."""
        result = check_author("Xyzzy Nonexistent Author 99999")
        expected = {"works_count", "cited_by_count", "h_index", "institution", "top_fields", "orcid"}
        assert expected.issubset(result.keys())
        assert isinstance(result["top_fields"], list)
