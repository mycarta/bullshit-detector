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


def error_flag(predicted, actual, threshold: float = 0.0) -> dict:
    """Compare predicted vs actual curves point by point.

    For each point checks two conditions:

    * **Absolute error** — whether ``|predicted[i] - actual[i]|`` exceeds
      *threshold*.
    * **Slope sign mismatch** — whether the direction of change from the
      previous point differs between the two curves (i.e., one rises while
      the other falls).

    Parameters
    ----------
    predicted, actual : array-like
        Predicted and actual values (e.g., inversion result vs well log).
        Must be the same length (≥ 2).
    threshold : float
        Absolute-error threshold for flagging a point. Default 0.0
        (flag every point with any deviation).

    Returns
    -------
    dict
        abs_errors : ndarray — ``|predicted - actual|`` for every point
        slope_sign_mismatches : list of int — indices (1-based relative to
            the *differences* array, so valid range is 1..n-1) where the
            sign of the slope flips between curves
        flagged_points : list of int — indices where abs_error > threshold
        n_flagged : int — len(flagged_points)
        fraction_flagged : float — n_flagged / n

    Examples
    --------
    >>> import numpy as np
    >>> p = np.array([1.0, 2.0, 3.0])
    >>> result = error_flag(p, p)          # perfect match
    >>> result['n_flagged']
    0
    >>> result2 = error_flag(np.array([0., 1.]), np.array([1., 2.]), threshold=0.5)
    >>> result2['n_flagged']
    0

    References
    ----------
    Notebook D: Be-a-geoscience-detective.ipynb (error_flag function).
    """
    predicted = np.asarray(predicted, dtype=float)
    actual = np.asarray(actual, dtype=float)
    if predicted.shape != actual.shape:
        raise ValueError("predicted and actual must have the same shape.")
    n = len(predicted)

    abs_errors = np.abs(predicted - actual)
    flagged_points = list(np.where(abs_errors > threshold)[0])

    # Slope-sign mismatch: compare sign of first-difference at each interior point
    pred_diff = np.diff(predicted)
    act_diff = np.diff(actual)
    # Mismatch when signs are strictly opposite (ignore zeros to avoid ambiguity)
    sign_pred = np.sign(pred_diff)
    sign_act = np.sign(act_diff)
    # A mismatch is where both diffs are non-zero and their signs differ
    mismatch_mask = (sign_pred != 0) & (sign_act != 0) & (sign_pred != sign_act)
    # Return the index of the *second* point in each pair (1-based in diff space,
    # which equals index i+1 in the original array)
    slope_sign_mismatches = list(np.where(mismatch_mask)[0] + 1)

    return {
        "abs_errors": abs_errors,
        "slope_sign_mismatches": slope_sign_mismatches,
        "flagged_points": flagged_points,
        "n_flagged": len(flagged_points),
        "fraction_flagged": len(flagged_points) / n,
    }


def bootstrap_proportion(data, condition_fn, n_boot: int = 10000,
                         ci: float = 0.95,
                         random_state=None) -> dict:
    """Estimate a proportion with bootstrap confidence interval.

    Computes the proportion of values in *data* satisfying *condition_fn*,
    then bootstraps to produce a percentile-based CI.

    Parameters
    ----------
    data : array-like
        1-D data array of any numeric type.
    condition_fn : callable
        Function that takes a single value and returns ``True``/``False``.
        Example: ``lambda x: x > 0``.
    n_boot : int
        Number of bootstrap resamples. Default 10 000.
    ci : float
        Confidence level as a fraction in (0, 1). Default 0.95.
    random_state : int or None
        Seed for reproducibility. Default None.

    Returns
    -------
    dict
        proportion : float — observed proportion satisfying *condition_fn*
        ci_lower : float — lower percentile bound of the bootstrap CI
        ci_upper : float — upper percentile bound of the bootstrap CI
        n_boot : int — number of resamples used
        bootstrap_proportions : ndarray — full array of per-resample
            proportions (length *n_boot*), for plotting

    Examples
    --------
    >>> import numpy as np
    >>> data = np.array([1] * 70 + [0] * 30)
    >>> result = bootstrap_proportion(data, lambda x: x == 1, random_state=0)
    >>> abs(result['proportion'] - 0.7) < 0.01
    True
    >>> result['ci_lower'] < 0.7 < result['ci_upper']
    True

    References
    ----------
    Notebook D: Be-a-geoscience-detective.ipynb (bootstrap_proportion function).
    Efron, B. & Tibshirani, R. J. (1993). An Introduction to the Bootstrap.
    """
    rng = np.random.default_rng(random_state)
    data = np.asarray(data)
    n = len(data)

    flags = np.array([bool(condition_fn(v)) for v in data])
    proportion = float(flags.mean())

    boot_props = np.empty(n_boot)
    for i in range(n_boot):
        sample = rng.choice(flags, size=n, replace=True)
        boot_props[i] = sample.mean()

    alpha = 1.0 - ci
    ci_lower = float(np.percentile(boot_props, 100 * alpha / 2))
    ci_upper = float(np.percentile(boot_props, 100 * (1 - alpha / 2)))

    return {
        "proportion": proportion,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "n_boot": n_boot,
        "bootstrap_proportions": boot_props,
    }
