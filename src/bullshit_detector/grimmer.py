"""
Tier 1 — Analytic GRIMMER (A-GRIMMER) test.

Tests whether a reported standard deviation is mathematically possible
given the reported mean and sample size, for data collected on integer
scales (e.g., Likert scales).

Ported from R to Python based on:
    Allard, A. (2018), "Analytic-GRIMMER: a new way of testing the
    possibility of standard deviations", blog post.
    URL: https://aurelienallard.netlify.app/post/anaytic-grimmer-possibility-standard-deviations/

The original GRIMMER technique was developed by:
    Anaya, J. (2016), "The GRIMMER test: A statistical test of the
    probability of mean and standard deviation combinations",
    PeerJ Preprints.

The GRIM test on which this builds was developed by:
    Brown, N.J.L. & Heathers, J.A.J. (2017), "The GRIM Test: A Simple
    Technique Detects Numerous Anomalies in the Reporting of Results in
    Psychology", Social Psychological and Personality Science, 8(4):363-369.

Algorithm (4 steps)
-------------------
1. GRIM check: n × mean must round to an integer.
2. Sum-of-squares integer check: (n-1)×σ² + n×μ² must be an integer
   (within rounding bounds of the reported SD).
3. SD reconstruction: for each candidate integer, reconstruct SD and
   check if it rounds to the reported value.
4. Parity check: sum of squares must have same oddness as sum of values
   (squaring preserves parity).

Validation
----------
- Allard validated against 100,000 simulated samples (n=5–99, Likert 1–7)
  with zero false negatives.
- Validated against "pizzagate" (Wansink) paper: aGrimmer(n=18, mean=3.44,
  SD=2.47) → "GRIMMER inconsistent".
- 88% of all mean/SD/n combinations (means 1–7, SD 0–4, n 5–50) are
  impossible. Of those passing GRIM, ~50% fail A-GRIMMER.
"""

import math


def _round_half_down(number: float, decimals: int = 2) -> float:
    """Round to `decimals` places, always rounding half towards -infinity."""
    factor = 10 ** decimals
    is_five = number * factor * 10 - math.floor(number * factor) * 10
    if abs(is_five - 5) < 1e-9:
        return math.floor(number * factor) / factor
    return round(number, decimals)


def _round_half_up(number: float, decimals: int = 2) -> float:
    """Round to `decimals` places, always rounding half towards +infinity."""
    factor = 10 ** decimals
    is_five = number * factor * 10 - math.floor(number * factor) * 10
    if abs(is_five - 5) < 1e-9:
        return math.ceil(number * factor) / factor
    return round(number, decimals)


def a_grimmer(
    n: int,
    mean: float,
    sd: float,
    decimals_mean: int = 2,
    decimals_sd: int = 2,
) -> dict:
    """Test consistency of reported mean, SD, and sample size.

    Parameters
    ----------
    n : int
        Sample size.
    mean : float
        Reported mean.
    sd : float
        Reported standard deviation.
    decimals_mean : int
        Number of decimal places in the reported mean. Default 2.
    decimals_sd : int
        Number of decimal places in the reported SD. Default 2.

    Returns
    -------
    dict
        result : str — "GRIM inconsistent", "GRIMMER inconsistent",
            or "consistent"
        grim_passed : bool
        grimmer_passed : bool or None (None if GRIM failed)
        reconstructed_mean : float — the GRIM-consistent mean closest
            to the reported value

    Examples
    --------
    >>> a_grimmer(n=18, mean=3.44, sd=2.47)
    {'result': 'GRIMMER inconsistent', ...}

    >>> a_grimmer(n=20, mean=3.45, sd=1.82)
    {'result': 'GRIM inconsistent', ...}

    References
    ----------
    Allard (2018), blog post (see module docstring for URL).
    Brown & Heathers (2017), SPPS 8(4):363-369.
    """
    # Graceful handling when n is too large for GRIM to apply
    if n > 10 ** decimals_mean:
        return {
            "result": "GRIM inapplicable (n too large for reported precision)",
            "grim_passed": None,
            "grimmer_passed": None,
            "reconstructed_mean": mean,
        }

    # Step 1: GRIM test — n × mean must round to an integer
    total = mean * n
    realsum = round(total)          # Python round() is banker's rounding, same as R
    realmean = realsum / n

    consistency_down = abs(_round_half_down(realmean, decimals_mean) - mean) < 1e-9
    consistency_up   = abs(_round_half_up(realmean, decimals_mean)   - mean) < 1e-9
    grim_passed = consistency_down or consistency_up

    if not grim_passed:
        return {
            "result": "GRIM inconsistent",
            "grim_passed": False,
            "grimmer_passed": None,
            "reconstructed_mean": realmean,
        }

    # Step 2: Compute lower/upper bounds on sigma (from SD rounding)
    half_unit = 5.0 / (10 ** decimals_sd)
    lsigma = 0.0 if sd < half_unit else sd - half_unit
    usigma = sd + half_unit

    # Step 3: Bounds on Σ(x²) = (n-1)·σ² + n·μ²
    lower_bound = (n - 1) * lsigma ** 2 + n * realmean ** 2
    upper_bound = (n - 1) * usigma ** 2 + n * realmean ** 2

    # Step 4: At least one integer must exist in [lower_bound, upper_bound]
    if math.ceil(lower_bound) > math.floor(upper_bound):
        return {
            "result": "GRIMMER inconsistent",
            "grim_passed": True,
            "grimmer_passed": False,
            "reconstructed_mean": realmean,
        }

    # Step 5: All candidate integers
    possible_integers = list(range(math.ceil(lower_bound), math.floor(upper_bound) + 1))

    # Step 6: Reconstruct SD for each candidate; check if it rounds to reported SD
    matches_sd = []
    for x in possible_integers:
        var = (x - n * realmean ** 2) / (n - 1)
        if var < 0:
            matches_sd.append(False)
            continue
        pred_sd = math.sqrt(var)
        down = _round_half_down(pred_sd, decimals_sd)
        up   = _round_half_up(pred_sd, decimals_sd)
        matches_sd.append(abs(down - sd) < 1e-9 or abs(up - sd) < 1e-9)

    if not any(matches_sd):
        return {
            "result": "GRIMMER inconsistent",
            "grim_passed": True,
            "grimmer_passed": False,
            "reconstructed_mean": realmean,
        }

    # Step 7: Parity check — Σ(x²) must have the same parity as Σ(x)
    oddness = realsum % 2
    matches_oddness = [x % 2 == oddness for x in possible_integers]
    third_test = [m_sd and m_odd for m_sd, m_odd in zip(matches_sd, matches_oddness)]

    if not any(third_test):
        return {
            "result": "GRIMMER inconsistent",
            "grim_passed": True,
            "grimmer_passed": False,
            "reconstructed_mean": realmean,
        }

    return {
        "result": "consistent",
        "grim_passed": True,
        "grimmer_passed": True,
        "reconstructed_mean": realmean,
    }
