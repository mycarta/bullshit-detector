"""
Tier 3 — Distance correlation matrix and variable clustering.

Computes pairwise distance correlation for all variables and applies
hierarchical clustering to estimate the effective number of independent
variable groups (effective k). This feeds directly into P_spurious:
use the cluster count instead of the reported variable count.

Based on Notebook F and blog post:
    https://mycartablog.com/2019/04/10/data-exploration-in-python-distance-correlation-and-variable-clustering/

Repository: mycarta/Niccoli_Speidel_2018_Geoconvention
Uses Hunt (2013) dataset (same as Notebooks A/B).
"""

import numpy as np


def dist_corr(x, y) -> float:
    """Distance correlation between two vectors.

    Thin wrapper around ``dcor.distance_correlation``. Unlike Pearson r,
    distance correlation equals zero if and only if the variables are
    statistically independent (for continuous distributions).

    Parameters
    ----------
    x, y : array-like
        Data vectors of equal length.

    Returns
    -------
    float
        Distance correlation in [0, 1].

    Examples
    --------
    >>> import numpy as np
    >>> x = np.array([1., 2., 3., 4., 5.])
    >>> dist_corr(x, x)  # perfect dependence
    1.0
    >>> dist_corr(x, -x)  # monotone inverse still dependent
    1.0

    References
    ----------
    Székely et al. (2007). Measuring and testing dependence by correlation
    of distances. Annals of Statistics, 35(6), 2769–2794.
    Notebook F: dist_corr() function.
    """
    import dcor

    return float(dcor.distance_correlation(np.asarray(x, dtype=float),
                                           np.asarray(y, dtype=float)))


def dc_matrix(df) -> "pd.DataFrame":
    """Pairwise distance correlation matrix for all columns of a DataFrame.

    Computes the upper triangle only and mirrors it to avoid redundant
    computation.  The diagonal is set to 1.0.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame where each column is a variable (rows are observations).

    Returns
    -------
    pd.DataFrame
        Square symmetric DataFrame of shape (n_cols × n_cols) with
        column/index names matching ``df.columns`` and 1.0 on the diagonal.

    Examples
    --------
    >>> import pandas as pd, numpy as np
    >>> rng = np.random.default_rng(0)
    >>> df = pd.DataFrame({'a': rng.normal(size=30), 'b': rng.normal(size=30)})
    >>> m = dc_matrix(df)
    >>> m.shape
    (2, 2)
    >>> float(m.loc['a', 'a'])
    1.0

    References
    ----------
    Notebook F / blog post:
    https://mycartablog.com/2019/04/10/data-exploration-in-python-distance-correlation-and-variable-clustering/
    """
    import pandas as pd

    cols = list(df.columns)
    n = len(cols)
    mat = np.ones((n, n))

    for i in range(n):
        for j in range(i + 1, n):
            val = dist_corr(df.iloc[:, i].values, df.iloc[:, j].values)
            mat[i, j] = val
            mat[j, i] = val

    return pd.DataFrame(mat, index=cols, columns=cols)


def effective_k(df, threshold: float = 0.5, method: str = "complete") -> dict:
    """Estimate effective number of independent variable groups via DC clustering.

    Builds the pairwise distance correlation matrix, converts it to a
    distance matrix (``1 − DC``), applies hierarchical linkage, and cuts
    the dendrogram at ``threshold`` to count clusters.  The cluster count
    is the *effective k* to use in ``P_spurious`` instead of the raw
    variable count.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame where each column is a variable.
    threshold : float
        Distance threshold for ``scipy.cluster.hierarchy.fcluster``
        (criterion ``'distance'``).  Default 0.5.
    method : str
        Linkage method passed to ``scipy.cluster.hierarchy.linkage``.
        Default ``'complete'``.

    Returns
    -------
    dict
        n_clusters : int — effective k (number of independent groups)
        cluster_labels : ndarray — cluster assignment per column (1-based)
        dc_matrix : pd.DataFrame — pairwise DC matrix
        dendrogram_data : dict — output of
            ``scipy.cluster.hierarchy.dendrogram(..., no_plot=True)``

    Detection heuristic
    -------------------
    If a paper reports k "independent" predictors but DC clustering
    groups them into fewer clusters, use the cluster count (not k) when
    calling ``P_spurious``.

    Examples
    --------
    >>> import pandas as pd, numpy as np
    >>> rng = np.random.default_rng(0)
    >>> x = rng.normal(size=40)
    >>> df = pd.DataFrame({'a': x, 'b': x * 2, 'c': rng.normal(size=40)})
    >>> result = effective_k(df)
    >>> result['n_clusters']  # a and b are perfectly correlated → 2 groups
    2

    References
    ----------
    Notebook F / blog post (see module docstring).
    Niccoli & Speidel (2018), GeoConvention.
    """
    from scipy.cluster.hierarchy import dendrogram, fcluster, linkage

    dcm = dc_matrix(df)

    # Convert correlation to distance; clip to avoid tiny negatives from float arithmetic
    dist_mat = np.clip(1.0 - dcm.values, 0.0, None)
    np.fill_diagonal(dist_mat, 0.0)

    # Condense upper triangle for linkage
    n = dist_mat.shape[0]
    condensed = dist_mat[np.triu_indices(n, k=1)]

    Z = linkage(condensed, method=method)
    labels = fcluster(Z, t=threshold, criterion="distance")
    dend = dendrogram(Z, no_plot=True)

    return {
        "n_clusters": int(labels.max()),
        "cluster_labels": labels,
        "dc_matrix": dcm,
        "dendrogram_data": dend,
    }
