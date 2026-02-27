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


def influence_plot(x, y, ax=None, alpha: float = 0.05):
    """Create an OLS influence plot with Cook's distance bubbles.

    Fits an OLS model of y ~ x, then renders a Cook's distance influence
    plot via ``statsmodels``. Points with large Cook's distance and/or
    high leverage are flagged.

    Requires ``statsmodels`` and ``matplotlib``
    (install with ``pip install bullshit-detector[full]``).

    Parameters
    ----------
    x, y : array-like
        Independent and dependent variable data.
    ax : matplotlib.axes.Axes, optional
        Axes for the influence plot. If None, a new figure is created.
    alpha : float
        Significance level used by ``sm.graphics.influence_plot`` to
        draw the reference lines. Default 0.05.

    Returns
    -------
    dict
        model : statsmodels RegressionResultsWrapper — fitted OLS model
        cooks_distance : ndarray — Cook's distance for each observation
        high_leverage : list of int — indices of high-leverage points
            (leverage > 2*(k+1)/n, where k=1 for simple OLS)
        high_residual : list of int — indices of studentised residuals
            with |resid| > 2
        cc : float — Pearson correlation coefficient of x and y

    Detection heuristic
    -------------------
    Did the authors justify data removal with domain knowledge AND formal
    leverage analysis, or did they simply drop points until the correlation
    looked good?

    Examples
    --------
    >>> import numpy as np
    >>> rng = np.random.default_rng(0)
    >>> x = rng.uniform(0, 1, 10)
    >>> y = 2 * x + rng.normal(0, 0.1, 10)
    >>> result = influence_plot(x, y)
    >>> 'cooks_distance' in result
    True

    References
    ----------
    Notebook E: Be-a-geoscience-detective_example_2.ipynb
    Cook, R. D. (1977). Detection of influential observations in linear
    regression. Technometrics, 19(1), 15–18.
    """
    try:
        import statsmodels.api as sm
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError as exc:
        raise ImportError(
            "statsmodels and matplotlib are required for influence_plot. "
            "Install with: pip install bullshit-detector[full]"
        ) from exc

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)

    X = sm.add_constant(x)
    k = X.shape[1] - 1  # number of predictors (excludes constant)
    lm = sm.OLS(y, X).fit()

    if ax is None:
        _, ax = plt.subplots(figsize=(8, 6))

    sm.graphics.influence_plot(lm, alpha=alpha, ax=ax, criterion="cooks")
    ax.grid(True)

    # Extract Cook's distance from the influence measures
    influence = lm.get_influence()
    cooks_d = influence.cooks_distance[0]

    # High leverage: h_ii > 2*(k+1)/n
    hat_diag = influence.hat_matrix_diag
    lev_threshold = 2 * (k + 1) / n
    high_leverage = list(np.where(hat_diag > lev_threshold)[0])

    # High residual: |studentised resid| > 2
    stud_resid = influence.resid_studentized_internal
    high_residual = list(np.where(np.abs(stud_resid) > 2)[0])

    cc = float(np.corrcoef(x, y)[0, 1])

    return {
        "model": lm,
        "cooks_distance": cooks_d,
        "high_leverage": high_leverage,
        "high_residual": high_residual,
        "cc": cc,
    }


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
    Székely et al. (2007). Measuring and testing dependence by correlation
    of distances. Annals of Statistics, 35(6), 2769–2794.
    Notebook E: Be-a-geoscience-detective_example_2.ipynb
    """
    try:
        import dcor
        import numpy as np
    except ImportError as exc:
        raise ImportError(
            "dcor is required for distance_correlation_test. "
            "Install with: pip install bullshit-detector[full]"
        ) from exc

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    dc = float(dcor.distance_correlation(x, y))
    result = dcor.independence.distance_covariance_test(
        x, y, num_resamples=num_resamples
    )
    p_value = float(result.pvalue)

    return {
        "dcor": dc,
        "p_value": p_value,
        "significant": p_value < 0.05,
    }
