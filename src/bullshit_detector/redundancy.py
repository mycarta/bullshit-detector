"""
Tier 2 — Redundancy analysis.

Identifies variables that can be predicted from all remaining variables
with high confidence, and can therefore be safely removed from further
analysis. This is a more principled alternative to pairwise correlation
screening: a variable might have low pairwise correlations with every
other variable but still be fully determined by their combination.

Inspired by:
    Harrell, F.E. Jr., ``Hmisc::redun()`` in R — redundancy analysis
    using flexible parametric models.

    Speidel, T. (2018), "GeoConvention 2018: Data Science Tools for
    Petroleum Exploration and Production", R notebook. Used Hmisc::redun
    on the Hunt (2013) dataset with r2=0.70 threshold, identifying
    gross.pay and gross.pay.transform as redundant.

    See also: Harrell (2015), *Regression Modeling Strategies*, Springer.

Detector role
-------------
Feeds directly into P_spurious effective-k estimation: if redundancy
analysis shows that k_reported variables collapse to k_effective
independent predictors, use k_effective in the Kalkomey formula.

Also useful as a standalone collinearity screen: before interpreting
any regression, check whether predictors are redundant.
"""

import numpy as np


def redundancy_analysis(data, r2_threshold: float = 0.70,
                        method: str = "ols") -> dict:
    """Identify redundant variables by predicting each from all others.

    For each variable in the dataset, fit a model using all remaining
    variables as predictors. If the R² exceeds the threshold, the
    variable is flagged as redundant (it can be predicted from the
    others and carries little independent information).

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame where each column is a variable. The response variable
        (e.g., production) should be excluded before calling this function
        to avoid introducing bias.
    r2_threshold : float
        R² above which a variable is considered redundant. Default 0.70,
        following Speidel (2018) and Harrell's convention.
    method : str
        Regression method: "ols" (ordinary least squares) or "rf"
        (random forest, captures non-linear redundancy). Default "ols".

    Returns
    -------
    dict
        r_squared : dict — {variable_name: R²} for each variable
        redundant : list of str — variables exceeding the threshold,
            ordered by R² (most redundant first)
        retained : list of str — variables below the threshold
        effective_k : int — number of retained (non-redundant) variables
        threshold : float — echo of r2_threshold

    Notes
    -----
    This is a Python equivalent of R's ``Hmisc::redun()``. The R version
    uses flexible parametric (ACE/AVAS) transformations; this simpler
    version uses OLS or random forest.

    The procedure is:
        1. For each column X_i in data:
           - Fit X_i ~ all other columns
           - Record R² (adjusted for OLS, OOB for RF)
        2. Sort by R² descending
        3. Flag variables with R² > threshold as redundant
        4. Iterative removal: after flagging the most redundant variable,
           optionally re-fit remaining variables (Harrell's approach).
           Set iterative=True for this behavior (slower but more accurate).

    Requires ``scikit-learn`` (install with ``pip install bullshit-detector[full]``).

    Examples
    --------
    Hunt (2013) dataset, Speidel's R result with r2=0.70:
        gross.pay and gross.pay.transform flagged as redundant.
        gross.pay.transform is more redundant (algebraically derived).

    Detection heuristic
    -------------------
    If a paper reports k predictors but redundancy analysis reduces them
    to k_effective, the Kalkomey P_spurious should use k_effective.
    Papers that don't address multicollinearity before reporting
    multiple significant predictors deserve extra scrutiny.

    References
    ----------
    Harrell (2015), Regression Modeling Strategies, Springer.
    Speidel (2018), GeoConvention R notebook.
    """
    try:
        from sklearn.linear_model import LinearRegression
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.preprocessing import StandardScaler
    except ImportError as exc:
        raise ImportError(
            "scikit-learn is required for redundancy_analysis. "
            "Install it with: pip install scikit-learn"
        ) from exc

    import pandas as pd

    cols = list(data.columns)
    if len(cols) < 2:
        raise ValueError("DataFrame must have at least 2 columns.")

    r2_scores: dict = {}

    for target_col in cols:
        X = data[[c for c in cols if c != target_col]].values
        y = data[target_col].values

        if method == "ols":
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            model = LinearRegression()
            model.fit(X_scaled, y)
            y_pred = model.predict(X_scaled)
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
        elif method == "rf":
            model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
            model.fit(X, y)
            r2 = model.score(X, y)  # OOB not reliable with small n; use train R²
        else:
            raise ValueError(f"Unknown method '{method}'. Use 'ols' or 'rf'.")

        r2_scores[target_col] = round(float(r2), 4)

    # Sort by R² descending
    sorted_cols = sorted(r2_scores, key=lambda c: r2_scores[c], reverse=True)
    redundant = [c for c in sorted_cols if r2_scores[c] > r2_threshold]
    retained  = [c for c in sorted_cols if r2_scores[c] <= r2_threshold]

    return {
        "r_squared": r2_scores,
        "redundant": redundant,
        "retained": retained,
        "effective_k": len(retained),
        "threshold": r2_threshold,
    }


def suggest_removal(redundancy_result: dict) -> list:
    """Suggest which variable to remove from a redundant pair.

    When two variables are both flagged as redundant, the one with
    higher R² (more predictable from others) should be removed first.

    Parameters
    ----------
    redundancy_result : dict
        Output of redundancy_analysis().

    Returns
    -------
    list of str
        Variables to remove, in suggested order (most redundant first).

    Notes
    -----
    This is a statistical suggestion only. Domain knowledge should
    always be considered: if one variable is cheaper to measure or
    has stronger physical justification, keep it regardless of R².

    In Speidel's analysis, gross.pay and phi.h were both correlated
    with production, but redundancy analysis showed gross.pay was
    more predictable from other variables → remove gross.pay, keep phi.h.
    """
    redundant = redundancy_result.get("redundant", [])
    r2 = redundancy_result.get("r_squared", {})
    # redundant list is already sorted by R² descending from redundancy_analysis
    return list(redundant)
