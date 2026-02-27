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

import dcor
import numpy as np


def dist_corr(x, y, pval: bool = True, nruns: int = 2000) -> tuple:
    """Distance correlation with optional permutation p-value.

    Parameters
    ----------
    x, y : array-like
        Data vectors.
    pval : bool
        If True, also compute permutation p-value. Default True.
    nruns : int
        Number of permutation resamples. Default 2000.

    Returns
    -------
    tuple
        (dc, p_value) if pval=True, else just dc (float).

    References
    ----------
    Székely et al. (2007).
    Notebook F: dist_corr() function.
    """
    raise NotImplementedError("TODO: Extract from Notebook F")


def dc_matrix(data) -> "pd.DataFrame":
    """Compute pairwise distance correlation matrix for all columns.

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame where each column is a variable.

    Returns
    -------
    pd.DataFrame
        Square matrix of distance correlations.

    Notes
    -----
    Uses the lambda-based approach from Notebook F:
        data.apply(lambda col1: data.apply(lambda col2: dcor.distance_correlation(col1, col2)))

    References
    ----------
    Notebook F: blog post (see module docstring for URL).
    """
    raise NotImplementedError("TODO: Extract from Notebook F")


def effective_k(data, method: str = "complete") -> int:
    """Estimate effective number of independent variable groups.

    Applies hierarchical clustering to the distance correlation matrix
    and returns the number of clusters, which serves as effective k
    for the P_spurious calculation.

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame where each column is a variable.
    method : str
        Linkage method for hierarchical clustering. Default "complete".

    Returns
    -------
    int
        Number of independent variable clusters.

    Detection heuristic
    -------------------
    If a paper reports k "independent" predictors but DC clustering
    groups them into fewer clusters, the effective k for P_spurious
    is the cluster count, not the reported variable count.

    Requires ``seaborn`` and ``scipy`` (install with
    ``pip install bullshit-detector[full]``).

    References
    ----------
    Notebook F. Uses seaborn.clustermap internally.
    """
    raise NotImplementedError(
        "TODO: Implement DC matrix → hierarchical clustering → cluster count. "
        "See Notebook F for approach using sns.clustermap + dendrogram_col.reordered_ind."
    )
