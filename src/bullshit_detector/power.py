"""
Tier 2 — Sample size and statistical power calculations.

Tools for assessing whether a study was adequately powered to detect
the effects it claims. Underpowered studies are a major source of
unreliable findings: they either miss real effects or, paradoxically,
when they do find "significant" results, those results are more likely
to be inflated or spurious.

Inspired by:
    Speidel, T. (2018), "GeoConvention 2018: Data Science Tools for
    Petroleum Exploration and Production", R notebook. Power analysis
    on Hunt (2013) dataset showing need for ≥11 wells per group to
    detect a production difference of 16 with 80% power at α=0.10.

    Button et al. (2013), "Power failure: why small sample size
    undermines the reliability of neuroscience", Nature Reviews
    Neuroscience, 14:365-376. Median power in neuroscience is ~21%.

    Ioannidis (2005), "Why Most Published Research Findings Are False",
    PLoS Medicine, 2(8):e124.

Detector role
-------------
A Tier 2 screening question: "Given the claimed effect size and sample
size, was this study adequately powered?" If a paper reports a barely
significant result (p ≈ 0.04) from a study powered at 20%, the finding
is far more likely to be a false positive than a true effect.

Also useful prospectively: "How many wells/samples do I need to detect
an effect of size d?"
"""

import math
from scipy import stats


def required_n(
    effect_size: float = None,
    d: float = None,
    sd: float = None,
    sd1: float = None,
    sd2: float = None,
    alpha: float = 0.05,
    power: float = 0.80,
    alternative: str = "two-sided",
    equal_n: bool = True,
) -> dict:
    """Minimum sample size to detect a given effect.

    Parameters
    ----------
    effect_size : float, optional
        Cohen's d (standardized mean difference). If provided, sd/d are
        ignored.
    d : float, optional
        Raw mean difference (unstandardized). Requires sd or sd1+sd2.
    sd : float, optional
        Pooled standard deviation (when groups have equal variance).
    sd1, sd2 : float, optional
        Group-specific standard deviations (for unequal variance,
        uses Welch's approach). Speidel used sd1=16, sd2=12.
    alpha : float
        Significance level. Default 0.05.
    power : float
        Desired power (1 - beta). Default 0.80.
    alternative : str
        "two-sided" or "one-sided". Default "two-sided".
    equal_n : bool
        If True (default), assume equal allocation (n1 = n2).

    Returns
    -------
    dict
        n_per_group : int — minimum observations per group (ceiling)
        n_total : int — total observations needed (2 × n_per_group)
        effect_size_d : float — Cohen's d used
        alpha : float
        power : float
        alternative : str

    Notes
    -----
    For two independent groups:
        n = ((Z_{alpha/2} + Z_beta)^2 * 2 * sigma^2) / d^2

    For unequal variances (Speidel's approach):
        n = ((Z_{alpha/2} + Z_beta)^2 * (sd1^2 + sd2^2)) / d^2

    Examples
    --------
    Speidel (2018) GeoConvention example:
    >>> required_n(d=16, sd1=16, sd2=12, alpha=0.10, power=0.80)
    # → n_per_group ≈ 11 (total ≈ 22)

    Screening a paper that claims d=5 with n=8 per group:
    >>> achieved_power(d=5, sd=10, n_per_group=8, alpha=0.05)
    # → power ≈ 0.12 — massively underpowered!

    References
    ----------
    Speidel (2018), GeoConvention R notebook.
    Button et al. (2013), Nature Reviews Neuroscience 14:365-376.
    Cohen (1988), Statistical Power Analysis for the Behavioral Sciences.
    """
    if alternative == "two-sided":
        z_alpha = stats.norm.ppf(1.0 - alpha / 2.0)
    else:
        z_alpha = stats.norm.ppf(1.0 - alpha)
    z_beta = stats.norm.ppf(power)

    # Resolve Cohen's d
    if effect_size is not None:
        d_cohen = float(effect_size)
        # For raw-to-float conversion we need sigma; use sd if available
        _raw_d = None
        _sd1, _sd2 = None, None
    elif d is not None:
        _raw_d = float(d)
        _sd1 = sd1
        _sd2 = sd2
        if sd1 is not None and sd2 is not None:
            d_cohen = _raw_d / math.sqrt((sd1 ** 2 + sd2 ** 2) / 2.0)
        elif sd is not None:
            d_cohen = _raw_d / float(sd)
        else:
            raise ValueError("Provide sd, or sd1 and sd2, when using raw d.")
    else:
        raise ValueError("Provide effect_size (Cohen's d) or raw d with sd/sd1/sd2.")

    # Compute n per group
    if (
        effect_size is None
        and _raw_d is not None
        and _sd1 is not None
        and _sd2 is not None
    ):
        # Speidel unequal-variance formula (preserves the raw variance structure)
        n_float = (z_alpha + z_beta) ** 2 * (_sd1 ** 2 + _sd2 ** 2) / _raw_d ** 2
    else:
        # Standard equal-variance formula from Cohen's d
        n_float = 2.0 * ((z_alpha + z_beta) / d_cohen) ** 2

    n_per_group = math.ceil(n_float)

    return {
        "n_per_group": n_per_group,
        "n_total": 2 * n_per_group,
        "effect_size_d": round(d_cohen, 4),
        "alpha": alpha,
        "power": power,
        "alternative": alternative,
    }


def achieved_power(
    d: float = None,
    effect_size: float = None,
    sd: float = None,
    sd1: float = None,
    sd2: float = None,
    n_per_group: int = None,
    n_total: int = None,
    alpha: float = 0.05,
    alternative: str = "two-sided",
) -> dict:
    """Compute achieved power for a given study design.

    This is the screening function: "Given what the paper reports,
    how powered was this study?"

    Parameters
    ----------
    d : float, optional
        Raw mean difference (requires sd or sd1+sd2).
    effect_size : float, optional
        Cohen's d (standardized). Takes precedence over d+sd.
    sd, sd1, sd2 : float, optional
        Standard deviation(s). Same logic as required_n.
    n_per_group : int, optional
        Sample size per group. Provide this OR n_total.
    n_total : int, optional
        Total sample size (divided by 2 for per-group).
    alpha : float
        Significance level used. Default 0.05.
    alternative : str
        "two-sided" or "one-sided". Default "two-sided".

    Returns
    -------
    dict
        power : float — achieved power (0 to 1)
        n_per_group : int
        effect_size_d : float — Cohen's d
        alpha : float
        adequate : bool — True if power >= 0.80
        interpretation : str — qualitative assessment

    Detection heuristic
    -------------------
    Power < 0.50: study had less than a coin-flip chance of detecting
    its own claimed effect. Any "significant" finding is suspect.

    Power < 0.80: conventional threshold for adequate power. Below this,
    findings should be interpreted with extra caution.

    Button et al. (2013) found median power in neuroscience was ~21%.

    Examples
    --------
    >>> achieved_power(d=16, sd1=16, sd2=12, n_per_group=21, alpha=0.10)
    # Hunt dataset: 21 wells, α=0.10 → power ≈ ???

    >>> achieved_power(effect_size=0.5, n_per_group=20, alpha=0.05)
    # Medium effect, 20 per group → power ≈ 0.34 — underpowered!
    """
    # Resolve n per group
    if n_per_group is None and n_total is not None:
        n_per_group = n_total // 2
    if n_per_group is None:
        raise ValueError("Provide n_per_group or n_total.")

    # Resolve Cohen's d
    if effect_size is not None:
        d_cohen = float(effect_size)
    elif d is not None:
        _raw_d = float(d)
        if sd1 is not None and sd2 is not None:
            d_cohen = _raw_d / math.sqrt((sd1 ** 2 + sd2 ** 2) / 2.0)
        elif sd is not None:
            d_cohen = _raw_d / float(sd)
        else:
            raise ValueError("Provide sd, or sd1 and sd2, when using raw d.")
    else:
        raise ValueError("Provide effect_size (Cohen's d) or raw d with sd/sd1/sd2.")

    # Non-centrality parameter: d * sqrt(n/2) for two equal groups
    ncp = d_cohen * math.sqrt(n_per_group / 2.0)

    if alternative == "two-sided":
        z_alpha = stats.norm.ppf(1.0 - alpha / 2.0)
        pwr = stats.norm.sf(z_alpha - ncp) + stats.norm.cdf(-z_alpha - ncp)
    else:
        z_alpha = stats.norm.ppf(1.0 - alpha)
        pwr = stats.norm.sf(z_alpha - ncp)

    pwr = float(min(pwr, 1.0))
    adequate = pwr >= 0.80

    if pwr >= 0.80:
        interpretation = "Adequate (≥80% power)"
    elif pwr >= 0.50:
        interpretation = "Marginal (50–80% power) — treat findings with caution"
    else:
        interpretation = (
            "Underpowered (<50%) — coin-flip or worse; ‘significant’ result likely inflated"
        )

    return {
        "power": round(pwr, 4),
        "n_per_group": n_per_group,
        "effect_size_d": round(d_cohen, 4),
        "alpha": alpha,
        "adequate": adequate,
        "interpretation": interpretation,
    }


def power_curve(
    d_range: tuple = None,
    n_range: tuple = None,
    sd: float = None,
    sd1: float = None,
    sd2: float = None,
    alpha: float = 0.05,
    power: float = 0.80,
    alternative: str = "two-sided",
) -> "pd.DataFrame":
    """Generate a power curve for a range of effect sizes or sample sizes.

    Produces a table (and optionally a plot) showing how required n
    changes across a range of plausible effect sizes, or how power
    changes across a range of sample sizes.

    Parameters
    ----------
    d_range : tuple of (float, float, float), optional
        (min_d, max_d, step) for effect sizes. Solves for n at each.
    n_range : tuple of (int, int, int), optional
        (min_n, max_n, step) for sample sizes. Solves for power at each.
        Provide d_range OR n_range, not both.
    sd, sd1, sd2 : float
        Standard deviation(s).
    alpha : float
        Significance level. Default 0.05.
    power : float
        Target power (only used with d_range). Default 0.80.
    alternative : str
        "two-sided" or "one-sided". Default "two-sided".

    Returns
    -------
    pd.DataFrame
        Columns depend on mode:
        - d_range mode: d, n_per_group, n_total
        - n_range mode: n_per_group, power

    Notes
    -----
    Speidel (2018) generated power curves for mu1 in [34, 44] and
    mu2 in [24, 34] with sd1=16, sd2=12, alpha=0.10, power=0.80.
    This showed the sensitivity of required n to assumed effect size.

    "It is always wise to solve for a range of plausible values,
    rather than a single point." — Speidel (2018)

    References
    ----------
    Speidel (2018), GeoConvention R notebook, Section 7.
    """
    raise NotImplementedError(
        "TODO: Loop over d_range or n_range, call required_n or "
        "achieved_power at each point, collect into DataFrame."
    )
