"""
Tier 2 — Spurious correlation detection.

Tools for assessing whether reported correlations could be spurious,
based on the number of wells (samples), attributes (variables tested),
and the correlation coefficient itself.

Based on:
    Kalkomey, C.T. (1997), "Potential risks when using seismic attributes
    as predictors of reservoir properties", The Leading Edge, March 1997,
    pp. 247-251.

Functions extracted from Matteo Niccoli's notebooks:
    - Notebook A: mycarta/Data-science-tools-petroleum-exploration-and-production
    - Blog: "Visual data exploration in Python – correlation, confidence,
      spuriousness" (https://mycartablog.com)
"""

import math
import numpy as np
from scipy import stats


def P_spurious(r: float, n: int, k: int = 1) -> float:
    """Probability of at least one spurious correlation.

    Computes the probability that at least one of k independent attributes
    would produce a correlation coefficient >= |r| by chance alone, given
    n observations and true population correlation rho = 0.

    Parameters
    ----------
    r : float
        Observed correlation coefficient (absolute value used).
    n : int
        Number of observations (wells, samples).
    k : int
        Number of independent attributes tested. Default 1.

    Returns
    -------
    float
        Probability in [0, 1] that at least one correlation >= |r|
        is spurious.

    Notes
    -----
    Implements Kalkomey (1997) equation:
        P(at least 1 spurious) = sum_{i=1}^{k} p_sc * (1 - p_sc)^{i-1}
    which equals 1 - (1 - p_sc)^k, where p_sc is the probability that
    a single attribute produces |r| >= R by chance.

    For k=1, this reduces to the single-attribute case.
    For k>1, this is the multi-attribute extension (Kalkomey Tables 2-5).

    Examples
    --------
    >>> P_spurious(0.85, 21, 1)   # R=0.85, 21 wells, 1 attribute
    # ≈ 0.0 (almost certainly real)

    >>> P_spurious(0.38, 5, 10)   # R=0.38, 5 wells, 10 attributes
    # ≈ 0.96 (almost certainly spurious)

    References
    ----------
    Kalkomey (1997), The Leading Edge, Tables 1, 3.
    """
    r_abs = abs(r)
    t_stat = r_abs * math.sqrt(n - 2) / math.sqrt(1.0 - r_abs ** 2)
    p_sc = 2.0 * stats.t.sf(t_stat, df=n - 2)
    return 1.0 - (1.0 - p_sc) ** k


def r_crit(n: int, alpha: float = 0.025) -> float:
    """Critical correlation coefficient for a given sample size.

    The minimum |r| needed to reject the null hypothesis that the
    population correlation is zero, at the specified significance level.

    Parameters
    ----------
    n : int
        Number of observations (wells, samples).
    alpha : float
        Significance level (one-tailed). Default 0.025 (two-tailed 0.05).

    Returns
    -------
    float
        Critical correlation coefficient.

    Notes
    -----
    Uses the inverse relationship between r and the t-distribution:
        t_crit = t.ppf(1 - alpha, df=n-2)
        r_crit = t_crit / sqrt(t_crit^2 + n - 2)

    Examples
    --------
    >>> r_crit(21)   # 21 wells, alpha=0.025 (95% two-tailed)
    # ≈ 0.433

    >>> r_crit(5)    # 5 wells
    # ≈ 0.878 (need very high r with few wells)

    References
    ----------
    Brown, "Stats Without Tears" notation.
    Kalkomey (1997), The Leading Edge.
    """
    t_crit = stats.t.ppf(1.0 - alpha, df=n - 2)
    return t_crit / math.sqrt(t_crit ** 2 + n - 2)


def conf_int(r: float, n: int, confidence: float = 0.95) -> tuple:
    """Fisher Z-transform confidence interval for population correlation.

    Parameters
    ----------
    r : float
        Observed correlation coefficient.
    n : int
        Number of observations.
    confidence : float
        Confidence level. Default 0.95.

    Returns
    -------
    tuple of (float, float)
        (lower_bound, upper_bound) of the confidence interval for rho.

    Notes
    -----
    Uses Fisher's Z-transformation:
        Z = 0.5 * ln((1+r)/(1-r))
        SE = 1 / sqrt(n-3)
    then converts back via inverse transform.

    Detection heuristic: if CI crosses zero, cannot reject independence.
    Even strong-looking correlations may have wide CIs with small n.

    Examples
    --------
    >>> conf_int(0.73, 9)    # 9 wells
    # ≈ (0.13, 0.94) — very broad

    >>> conf_int(0.90, 8)    # 8 wells (after outlier removal)
    # ≈ (0.53, 0.98) — tightened dramatically

    References
    ----------
    Fisher (1921). Notebook A, Notebook C, Notebook E implementations.
    """
    z = math.atanh(r)
    se = 1.0 / math.sqrt(n - 3)
    z_crit = stats.norm.ppf((1.0 + confidence) / 2.0)
    lo = math.tanh(z - z_crit * se)
    hi = math.tanh(z + z_crit * se)
    return (lo, hi)
