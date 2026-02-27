"""
Tier 1 — P-value recomputation.

Lean reimplementation of the core statcheck computation: given a test
type, test statistic, and degrees of freedom, recompute the p-value
and check consistency with what the paper reports.

This replaces the need for the GPL-3.0 ``statcheck`` package for manual
screening. For automated batch extraction from PDFs, use
``pip install bullshit-detector[batch]`` which pulls in statcheck as an
optional dependency.

References
----------
- Nuijten et al. (2016), "The prevalence of statistical reporting errors
  in psychology (1985–2013)", Behavioral Research Methods 48:1205–1226.
- Sainani (2020), "How to Be a Statistical Detective", PM&R 12(2):211–215.
"""

import math
from scipy import stats


def check_p_value(
    test_type: str,
    statistic: float,
    df1: int,
    df2: int = None,
    reported_p: float = None,
    reported_comparison: str = "=",
    alpha: float = 0.05,
    one_tailed: bool = False,
) -> dict:
    """Recompute p-value from a reported test statistic and degrees of freedom.

    Parameters
    ----------
    test_type : str
        One of 't', 'F', 'chi2', 'z', 'r', 'Q'.
    statistic : float
        Reported test statistic value.
    df1 : int
        Degrees of freedom (or numerator df for F-test).
    df2 : int, optional
        Denominator df (F-test only).
    reported_p : float, optional
        The p-value reported in the paper. If provided, consistency
        is checked against the computed value.
    reported_comparison : str
        How the p-value was reported: '=' (exact), '<' (less than),
        '>' (greater than). Default '='.
    alpha : float
        Significance threshold for decision error detection. Default 0.05.
    one_tailed : bool
        If True, compute one-tailed p-value. Default False.

    Returns
    -------
    dict
        computed_p : float — the recomputed p-value
        reported_p : float or None — the reported p-value (echo)
        consistent : bool or None — True if reported matches computed
            within rounding tolerance. None if reported_p not provided.
        decision_error : bool or None — True if reported and computed
            disagree on significance at alpha. None if reported_p not
            provided.
        test_type, statistic, df1, df2 : echo of inputs

    Examples
    --------
    >>> check_p_value('t', 2.20, 28, reported_p=0.04)
    # computed_p ≈ 0.0363, reported 0.04 → inconsistent

    >>> check_p_value('F', 4.75, 1, 145, reported_p=0.031)
    # computed_p ≈ 0.0310 → consistent

    References
    ----------
    Nuijten et al. (2016), Behavioral Research Methods.
    Sainani (2020), PM&R 12(2):211-215.
    """
    # --- Recompute p-value ---
    test_type = test_type.lower()

    if test_type == "t":
        computed_p = 2 * stats.t.sf(abs(statistic), df1)
    elif test_type == "f":
        if df2 is None:
            raise ValueError("F-test requires df2 (denominator degrees of freedom)")
        computed_p = stats.f.sf(statistic, df1, df2)
    elif test_type == "chi2":
        computed_p = stats.chi2.sf(statistic, df1)
    elif test_type == "z":
        computed_p = 2 * stats.norm.sf(abs(statistic))
    elif test_type == "r":
        # Convert correlation to t-statistic, then compute p
        if abs(statistic) >= 1.0:
            computed_p = 0.0 if abs(statistic) == 1.0 else float("nan")
        else:
            t_val = statistic * math.sqrt(df1) / math.sqrt(1 - statistic**2)
            computed_p = 2 * stats.t.sf(abs(t_val), df1)
    elif test_type == "q":
        # Meta-analysis Q-test uses chi-squared distribution
        computed_p = stats.chi2.sf(statistic, df1)
    else:
        raise ValueError(
            f"Unknown test_type '{test_type}'. "
            "Expected one of: 't', 'F', 'chi2', 'z', 'r', 'Q'"
        )

    if one_tailed:
        computed_p = computed_p / 2

    # --- Compare with reported p if provided ---
    consistent = None
    decision_error = None

    if reported_p is not None:
        # Determine rounding tolerance from reported precision
        # e.g., reported_p = 0.031 → 3 decimal places → tolerance = 0.0005
        p_str = str(reported_p)
        if "." in p_str:
            decimals = len(p_str.split(".")[1])
        else:
            decimals = 0
        tolerance = 0.5 * 10 ** (-decimals)

        if reported_comparison == "=":
            consistent = abs(computed_p - reported_p) <= tolerance
        elif reported_comparison == "<":
            # p < X is consistent if computed_p < X
            consistent = computed_p < reported_p
        elif reported_comparison == ">":
            consistent = computed_p > reported_p
        else:
            consistent = None  # unknown comparison

        # Decision error: do reported and computed disagree on significance?
        reported_significant = reported_p < alpha
        computed_significant = computed_p < alpha
        decision_error = reported_significant != computed_significant

    return {
        "computed_p": computed_p,
        "reported_p": reported_p,
        "consistent": bool(consistent) if consistent is not None else None,
        "decision_error": bool(decision_error) if decision_error is not None else None,
        "test_type": test_type,
        "statistic": statistic,
        "df1": df1,
        "df2": df2,
    }
