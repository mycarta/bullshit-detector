"""
Tier 3 — Outlier leverage analysis.

Tools for assessing whether reported correlations depend on influential
data points, including Cook's distance influence plots and distance
correlation as a non-parametric independence test.

Based on Notebook E: mycarta/Be-a-geoscience-detective (example 2).
Blog: "Be a geoscience and data science detective" (https://mycartablog.com)

Worked example: Close et al. (2010) reported CC=0.7 improving to CC=0.9
after removing one well. This module provides tools to evaluate whether
such removal is justified.
"""


def influence_plot(x, y, ax=None):
    """Create an OLS influence plot with Cook's distance bubbles.

    Requires ``statsmodels`` (install with ``pip install bullshit-detector[full]``).

    Parameters
    ----------
    x, y : array-like
        Independent and dependent variable data.
    ax : matplotlib.axes.Axes, optional
        Axes to plot on.

    Returns
    -------
    dict
        cooks_distance : array — Cook's distance for each observation
        high_leverage : list of int — indices of high-leverage points
        high_residual : list of int — indices of high-residual points

    Detection heuristic
    -------------------
    Did the authors justify data removal with domain knowledge AND formal
    leverage analysis, or did they simply drop points until the correlation
    looked good?

    References
    ----------
    Notebook E: Be-a-geoscience-detective_example_2.ipynb
    """
    raise NotImplementedError(
        "TODO: Wrap statsmodels sm.graphics.influence_plot. "
        "Extract from Notebook E."
    )


def distance_correlation_test(x, y, num_resamples: int = 2000) -> dict:
    """Non-parametric independence test using distance correlation.

    Unlike Pearson r, distance correlation DC=0 actually means
    independence (not just absence of linear relationship).

    Parameters
    ----------
    x, y : array-like
        Data vectors.
    num_resamples : int
        Number of permutation resamples for p-value. Default 2000.

    Returns
    -------
    dict
        dc : float — distance correlation
        p_value : float — permutation-based p-value
        independent : bool — True if p_value > 0.05

    Notes
    -----
    Uses ``dcor.independence.distance_covariance_test`` which shuffles
    association between x and y to build a null distribution.

    Examples
    --------
    Close et al. (2010), all 9 wells:  DC=0.745, p=0.043
    Close et al. (2010), 8 wells:      DC=0.917, p=0.0008

    References
    ----------
    Székely et al. (2007). Notebook E implementation.
    """
    raise NotImplementedError("TODO: Wrap dcor library. Extract from Notebook E.")
