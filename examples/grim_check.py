"""
Wansink "pizzagate" case study -- A-GRIMMER demonstration.

Brian Wansink was a Cornell food marketing researcher whose lab published
dozens of papers claiming to show how environmental cues (plate size, serving
bowl placement, restaurant lighting, etc.) nudge people to eat more or less.
His work was widely cited in public-health policy.

In 2016-2017, Nick Brown and James Heathers applied the GRIM test and then the
GRIMMER test to his published descriptive statistics. They found that many
reported means and standard deviations were mathematically impossible given the
reported sample sizes -- the numbers could not have come from integer-scale data.
This was documented in:

    Brown, N.J.L. & Heathers, J.A.J. (2017), "The GRIM Test: A Simple Technique
    Detects Numerous Anomalies in the Reporting of Results in Psychology",
    Social Psychological and Personality Science, 8(4):363-369.

Subsequent investigation by university auditors confirmed the anomalies.
Cornell retracted or issued corrections to 18 of Wansink's papers; six were
retracted outright. Wansink resigned in 2018.

This script reproduces the canonical GRIMMER-inconsistent cell (n=18, mean=3.44,
SD=2.47) and contrasts it with a genuinely consistent set of values.
"""

from bullshit_detector.grimmer import a_grimmer


def print_result(label, result):
    """Pretty-print an a_grimmer() result dict with a labelled header."""
    print()
    print("-" * 60)
    print("  " + label)
    print("-" * 60)
    for key, value in result.items():
        print("  {:<22} {}".format(key, value))


# ---------------------------------------------------------------------------
# Wansink inconsistent case
# ---------------------------------------------------------------------------
# From one of the retracted papers: Likert-scale responses (integers 1-9)
# with n=18 participants. The combination fails GRIMMER -- no integer
# sum-of-squares exists consistent with both the reported mean and SD.

wansink_result = a_grimmer(n=18, mean=3.44, sd=2.47)
print_result(
    "WANSINK (n=18, mean=3.44, SD=2.47) -- known GRIMMER-inconsistent",
    wansink_result,
)

print()
print("  Interpretation:")
if wansink_result["result"] == "GRIMMER inconsistent":
    print("  [FAIL] GRIMMER INCONSISTENT -- no integer dataset of size 18 can")
    print("         produce mean=3.44 and SD=2.47 simultaneously.")
    print("         The GRIM check passed (18 x 3.44 = 61.92 ~ 62, which rounds")
    print("         back to 62 / 18 = 3.44), but the SD bounds admit no valid")
    print("         integer sum-of-squares, or none with the correct parity.")
elif wansink_result["result"] == "GRIM inconsistent":
    print("  [FAIL] GRIM INCONSISTENT -- n x mean does not round to an integer.")
else:
    print("  [PASS] consistent (unexpected -- check algorithm)")


# ---------------------------------------------------------------------------
# Consistent reference case
# ---------------------------------------------------------------------------
# n=10, mean=3.20, SD=1.48 on a Likert scale.
#
#   GRIM check:    10 x 3.20 = 32 (exact integer)                PASS
#   Step 2 bounds: sum-of-squares in [121.98, 122.25]; 122 ok    PASS
#   Reconstructed: sqrt((122 - 10 * 3.2^2) / 9) ~ 1.476 -> 1.48 PASS
#   Parity:        sum(x) = 32 (even); sum(x^2) = 122 (even)     PASS

consistent_result = a_grimmer(n=10, mean=3.20, sd=1.48)
print_result(
    "CONSISTENT REFERENCE (n=10, mean=3.20, SD=1.48)",
    consistent_result,
)

print()
print("  Interpretation:")
if consistent_result["result"] == "consistent":
    print("  [PASS] CONSISTENT -- an integer dataset of size 10 can produce")
    print("         mean=3.20 and SD=1.48. The combination passes all three")
    print("         GRIMMER steps: GRIM, sum-of-squares bounds, and parity.")
else:
    print("  Unexpected result: {}".format(consistent_result["result"]))


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print()
print("=" * 60)
print("  Summary")
print("=" * 60)
print("  Wansink case    -> {}".format(wansink_result["result"]))
print("  Reference case  -> {}".format(consistent_result["result"]))
print()
print("  A-GRIMMER reference:")
print("  Allard, A. (2018). Analytic-GRIMMER: a new way of testing")
print("  the possibility of standard deviations.")
print("  https://aurelienallard.netlify.app/post/")
print("         anaytic-grimmer-possibility-standard-deviations/")
