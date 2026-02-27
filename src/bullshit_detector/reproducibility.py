"""
Tier 3 — Reproducibility challenge tools.

Tools for quantitatively challenging qualitative claims in papers,
when you have access to data (or can extract it from figures).

Based on Notebook D: mycarta/Be-a-geoscience-detective
Blog: "Be a geoscience and data science detective" (https://mycartablog.com)

Worked example: CSEG Recorder 2009 paper on seismic inversion.
Hand-digitized results, applied error_flag + bootstrap CI to show
that the original paper's qualitative visual comparison only holds
clearly for one of two zones.
"""

import numpy as np


def error_flag(predicted, actual, threshold: float = None,
               method: str = "both") -> np.ndarray:
    """Flag samples where prediction deviates from actual.

    Parameters
    ----------
    predicted, actual : array-like
        Predicted and actual values (e.g., inversion result vs well log).
    threshold : float, optional
        Deviation threshold. If None, uses median + MAD.
    method : str
        Flagging method: "difference" (absolute deviation exceeds threshold),
        "slope" (sign of local slope differs), or "both". Default "both".

    Returns
    -------
    np.ndarray of bool
        True where prediction is flagged as deviating.

    Notes
    -----
    This is a domain QC tool for predicted vs. actual curves.
    Uses median/MAD statistic by default for robustness.

    References
    ----------
    Notebook D: error_flag function.
    """
    raise NotImplementedError("TODO: Extract from Notebook D")


def bootstrap_proportion(flags, n_resamples: int = 5000,
                         ci: float = 0.90) -> dict:
    """Bootstrap confidence interval on proportion of flagged samples.

    Parameters
    ----------
    flags : array-like of bool
        Boolean array from error_flag().
    n_resamples : int
        Number of bootstrap resamples. Default 5000.
    ci : float
        Confidence interval width. Default 0.90.

    Returns
    -------
    dict
        proportion : float — observed proportion of flagged samples
        ci_lower : float — lower bound of CI
        ci_upper : float — upper bound of CI
        n_resamples : int

    Notes
    -----
    Standard bootstrap: resample flags with replacement, compute
    proportion in each resample, use percentiles for CI bounds.

    Notebook D used 5,000–20,000 resamples and 5th/95th percentiles
    for a 90% CI.

    References
    ----------
    Notebook D: bootstrap_proportion function.
    """
    raise NotImplementedError("TODO: Extract from Notebook D")
