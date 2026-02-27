"""
Tier 0 screening -- Vinson, Burnham & Nagendran (2012) green coffee extract.

Bergstrom & West use this paper as a canonical example in *Calling Bullshit:
The Art of Skepticism in a Data-Driven World* (Random House, 2020) and in
their University of Washington course (https://callingbullshit.org/). It
illustrates how a Tier 0 venue check alone should have raised a red flag
long before anyone ran the statistics.

The paper claimed that a green coffee bean extract caused near-miraculous
weight loss (an average of 17 lb in 22 weeks) in a randomised crossover
trial with n=16 participants. The result was spectacular. The journal was not.

Timeline:
  2012  Paper published in Diabetes, Metabolic Syndrome and Obesity:
        Targets and Therapy (Dove Medical Press).
  2014  FTC investigation. Authors agreed to retract after the agency
        found the underlying data had been manipulated. The FTC also
        settled with Applied Food Sciences, the supplement company that
        funded the study, for USD 3.5 million.
  2015  Paper formally retracted.

This script runs all three Tier 0 checks automatically:
  1. check_journal()    -- is the venue legitimate/indexed?
  2. check_retraction() -- is the paper retracted?
  3. check_author()     -- what is the lead author's publication record?

References
----------
Bergstrom, C.T. & West, J.D. (2020). *Calling Bullshit: The Art of
Skepticism in a Data-Driven World*. Random House.

Vinson, J.A., Burnham, B.R. & Nagendran, M.V. (2012). Randomized,
double-blind, placebo-controlled, linear dose, crossover study to
evaluate the efficacy and safety of a green coffee bean extract in
overweight subjects. Diabetes, Metabolic Syndrome and Obesity:
Targets and Therapy, 5, 21-27. DOI: 10.2147/DMSO.S27665.

FTC press release (2014):
https://www.ftc.gov/news-events/news/press-releases/2014/09/
marketer-green-coffee-bean-weight-loss-supplement-settles-ftc-charges
"""

from bullshit_detector.paper_screening import check_journal, check_retraction, check_author


JOURNAL = "Diabetes, Metabolic Syndrome and Obesity: Targets and Therapy"
DOI     = "10.2147/DMSO.S27665"
AUTHOR  = "Joe Vinson"

SEP  = "-" * 60
SEP2 = "=" * 60


def print_section(title, result):
    print()
    print(SEP)
    print("  " + title)
    print(SEP)
    for key, value in result.items():
        if isinstance(value, list):
            if value:
                print("  {:<26} {}".format(key, value[0]))
                for v in value[1:]:
                    print("  {:<26} {}".format("", v))
            else:
                print("  {:<26} (none)".format(key))
        else:
            print("  {:<26} {}".format(key, value))


# ---------------------------------------------------------------------------
# 1. Journal check
# ---------------------------------------------------------------------------
print()
print("Screening paper: {}".format(DOI))
print("Journal:         {}".format(JOURNAL))

print()
print("Querying journal metadata (DOAJ + OpenAlex) ...")
journal_result = check_journal(JOURNAL)
print_section("CHECK 1 -- Journal legitimacy", journal_result)

print()
print("  Interpretation:")
if not journal_result["in_doaj"]:
    print("  [WARN] Journal NOT found in DOAJ.")
else:
    print("  [INFO] Journal found in DOAJ.")

if journal_result["publisher"]:
    pub = journal_result["publisher"].lower()
    if any(term in pub for term in ["dove", "hindawi", "mdpi", "bentham"]):
        print("  [WARN] Publisher '{}' is a high-volume open-access".format(
              journal_result["publisher"]))
        print("         publisher. Peer review quality varies widely.")
    else:
        print("  [INFO] Publisher: {}".format(journal_result["publisher"]))

if journal_result["cited_by_count"] < 5000:
    print("  [WARN] Low total citation count ({}) for the journal.".format(
          journal_result["cited_by_count"]))
    print("         Extraordinary claims need high-impact venues.")


# ---------------------------------------------------------------------------
# 2. Retraction check
# ---------------------------------------------------------------------------
print()
print("Querying CrossRef + PubPeer for retraction status ...")
retraction_result = check_retraction(DOI)
print_section("CHECK 2 -- Retraction status  ({})".format(DOI), retraction_result)

print()
print("  Interpretation:")
if retraction_result["retracted"]:
    print("  [FAIL] RETRACTED -- this paper has been formally retracted.")
    print("         Do not cite. Do not act on its findings.")
elif retraction_result["corrections"]:
    print("  [WARN] Corrections on record: {}".format(retraction_result["corrections"]))
else:
    print("  [INFO] No retraction notice found via CrossRef API.")
    print("         NOTE: CrossRef coverage is incomplete. This paper IS")
    print("         retracted (2014/2015) -- verify at Retraction Watch:")
    print("         https://retractionwatch.com/2015/10/")
    print("         authors-retract-green-coffee-bean-paper-that-was-cited-by-dr-oz/")

if retraction_result["pubpeer_url"]:
    print("  PubPeer: {}".format(retraction_result["pubpeer_url"]))


# ---------------------------------------------------------------------------
# 3. Author check
# ---------------------------------------------------------------------------
print()
print("Querying OpenAlex for lead author: {} ...".format(AUTHOR))
author_result = check_author(AUTHOR)
print_section("CHECK 3 -- Lead author  ({})".format(AUTHOR), author_result)

print()
print("  Interpretation:")
if author_result["works_count"] > 0:
    print("  [INFO] {} publications found on OpenAlex.".format(
          author_result["works_count"]))
else:
    print("  [INFO] Author not found in OpenAlex (name disambiguation may be")
    print("         needed -- Vinson is a common name).")

if author_result["institution"]:
    print("  [INFO] Last known affiliation: {}".format(author_result["institution"]))

if author_result["top_fields"]:
    print("  [INFO] Top research areas: {}".format(", ".join(author_result["top_fields"])))


# ---------------------------------------------------------------------------
# Summary verdict
# ---------------------------------------------------------------------------
print()
print(SEP2)
print("  TIER 0 VERDICT -- Vinson et al. (2012) Green Coffee Extract")
print(SEP2)

flags = []
if not journal_result["in_doaj"]:
    flags.append("Journal not found in DOAJ")
if journal_result["publisher"] and any(
        t in journal_result["publisher"].lower()
        for t in ["dove", "hindawi", "mdpi", "bentham"]):
    flags.append("High-volume OA publisher ({})".format(journal_result["publisher"]))
if journal_result["cited_by_count"] < 5000:
    flags.append("Low journal citation count ({})".format(
                 journal_result["cited_by_count"]))
if retraction_result["retracted"]:
    flags.append("Paper IS RETRACTED (FTC investigation, 2014)")
else:
    flags.append("Retraction not confirmed via API -- verify at Retraction Watch")

if flags:
    print("  Red flags found: {}".format(len(flags)))
    for i, f in enumerate(flags, 1):
        print("    {}. {}".format(i, f))
else:
    print("  No automated flags raised.")

print()
print("  Bergstrom & West's point: the venue itself is evidence.")
print("  A 17-lb weight-loss claim from a 16-person trial, published")
print("  in a minor Dove Press journal and funded by the supplement")
print("  manufacturer, should have prompted instant scepticism --")
print("  before anyone looked at p-values.")
