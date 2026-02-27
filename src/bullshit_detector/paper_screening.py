"""
Tier 0 — Paper-level screening.

API wrappers that check journal legitimacy, retraction status, and author
credentials before any statistical analysis is performed.

Attribution
-----------
This module is inspired by and based on the work of Carl T. Bergstrom and
Jevin D. West, specifically their paper-level legitimacy framework from
*Calling Bullshit: The Art of Skepticism in a Data-Driven World*
(Random House, 2020) and the "Calling Bullshit" course at the University
of Washington (https://callingbullshit.org/).

Their checklist for evaluating whether a scientific paper is legitimate —
covering journal venue, retraction status, author credentials, conflicts
of interest, and claims-to-venue proportionality — provides the conceptual
architecture for this module. The module automates the checks that can be
automated; the rest are encoded as heuristics in the accompanying skill
file (skills/paper_screening.md).

Full credit to Bergstrom & West for the framework; any errors in
implementation are ours.

APIs used (all free, no authentication required):
    - DOAJ: https://doaj.org/api/
    - OpenAlex: https://api.openalex.org/
    - CrossRef: https://api.crossref.org/
    - PubPeer: https://pubpeer.com/api/
"""

import requests


# ---------------------------------------------------------------------------
# Journal legitimacy
# ---------------------------------------------------------------------------

def check_journal(name_or_issn: str) -> dict:
    """Check whether a journal is listed in DOAJ and/or OpenAlex.

    Parameters
    ----------
    name_or_issn : str
        Journal name or ISSN (e.g., "Nature" or "0028-0836").

    Returns
    -------
    dict
        Keys: in_doaj (bool), publisher (str), works_count (int),
        cited_by_count (int), is_oa (bool), issn (str or None).

    Detection heuristic
    -------------------
    Extraordinary claims in unlisted journals are a major red flag.
    "If your finding is revolutionary, why is it in a journal nobody's
    heard of?" — Bergstrom & West (2020).

    Test case: "Diabetes, Metabolic Syndrome, and Obesity: Target and
    Therapy" (Dove Press) — the green coffee extract journal.
    """
    result = {
        "in_doaj": False,
        "publisher": None,
        "works_count": 0,
        "cited_by_count": 0,
        "is_oa": False,
        "issn": None,
    }

    # --- DOAJ lookup ---------------------------------------------------
    try:
        doaj_url = (
            "https://doaj.org/api/search/journals/"
            + requests.utils.quote(name_or_issn, safe="")
        )
        doaj_resp = requests.get(doaj_url, timeout=10)
        doaj_resp.raise_for_status()
        doaj_data = doaj_resp.json()
        if doaj_data.get("total", 0) > 0:
            result["in_doaj"] = True
            bibjson = doaj_data["results"][0].get("bibjson", {})
            publisher_block = bibjson.get("publisher", {})
            result["publisher"] = publisher_block.get("name")
            for ident in bibjson.get("identifier", []):
                if ident.get("type") in ("pissn", "eissn"):
                    result["issn"] = ident.get("id")
                    break
    except Exception:
        pass

    # --- OpenAlex lookup (richer metadata) -----------------------------
    try:
        _HEADERS = {"User-Agent": "bullshit-detector/0.1 (mailto:info@example.org)"}
        oa_url = (
            "https://api.openalex.org/sources?search="
            + requests.utils.quote(name_or_issn, safe="")
        )
        oa_resp = requests.get(oa_url, timeout=10, headers=_HEADERS)
        oa_resp.raise_for_status()
        oa_data = oa_resp.json()
        if oa_data.get("results"):
            top = oa_data["results"][0]
            result["works_count"] = top.get("works_count", 0) or 0
            result["cited_by_count"] = top.get("cited_by_count", 0) or 0
            result["is_oa"] = bool(top.get("is_oa", False))
            if result["issn"] is None:
                result["issn"] = top.get("issn_l")
            if result["publisher"] is None:
                result["publisher"] = top.get("host_organization_name")
    except Exception:
        pass

    return result


# ---------------------------------------------------------------------------
# Retraction and post-publication review
# ---------------------------------------------------------------------------

def check_retraction(doi: str) -> dict:
    """Check for retractions, corrections, and PubPeer commentary.

    Parameters
    ----------
    doi : str
        Digital Object Identifier (e.g., "10.2147/DMSO.S27665").

    Returns
    -------
    dict
        Keys: retracted (bool), corrections (list), pubpeer_comments (int),
        pubpeer_url (str or None).

    Notes
    -----
    Uses CrossRef API ``update-to`` field for retractions/corrections,
    and PubPeer API for post-publication commentary.

    Test case: DOI for the green coffee extract paper — should return
    retracted=True.
    """
    _HEADERS = {"User-Agent": "bullshit-detector/0.1 (mailto:info@example.org)"}
    _doi_clean = doi.strip().lower()

    result = {
        "retracted": False,
        "corrections": [],
        "pubpeer_comments": 0,
        "pubpeer_url": f"https://pubpeer.com/publications/{_doi_clean.replace('/', '-').upper()}",
    }

    # --- CrossRef: check the original record's own update-to field -------
    try:
        cr_url = f"https://api.crossref.org/works/{requests.utils.quote(_doi_clean, safe='')}"
        cr_resp = requests.get(cr_url, timeout=10, headers=_HEADERS)
        if cr_resp.ok:
            work = cr_resp.json().get("message", {})
            for upd in work.get("update-to") or []:
                upd_type = (upd.get("type") or "").lower()
                if upd_type == "retraction":
                    result["retracted"] = True
                elif upd_type in ("correction", "erratum"):
                    result["corrections"].append(upd.get("DOI") or upd_type)
    except Exception:
        pass

    # --- CrossRef: find retraction/correction notices that update our DOI --
    # (handles the common case where the retraction notice is a separate record)
    try:
        filter_url = (
            "https://api.crossref.org/works?"
            f"filter=updates:{_doi_clean}&rows=10"
        )
        filter_resp = requests.get(filter_url, timeout=10, headers=_HEADERS)
        if filter_resp.ok:
            items = filter_resp.json().get("message", {}).get("items", [])
            for item in items:
                for upd in item.get("update-to") or []:
                    upd_doi = (upd.get("DOI") or "").lower()
                    upd_type = (upd.get("type") or "").lower()
                    if upd_doi == _doi_clean:
                        if upd_type == "retraction":
                            result["retracted"] = True
                        elif upd_type in ("correction", "erratum"):
                            notice_doi = item.get("DOI")
                            if notice_doi and notice_doi not in result["corrections"]:
                                result["corrections"].append(notice_doi)
    except Exception:
        pass

    # --- PubPeer: attempt comment count, degrade gracefully ---------------
    try:
        pp_url = f"https://pubpeer.com/api/publications?doi={_doi_clean}"
        pp_resp = requests.get(pp_url, timeout=8, headers=_HEADERS)
        if pp_resp.ok:
            pp_data = pp_resp.json()
            pubs = pp_data if isinstance(pp_data, list) else pp_data.get("publications", [])
            if pubs:
                result["pubpeer_comments"] = pubs[0].get("comments", 0) or 0
    except Exception:
        pass

    return result


# ---------------------------------------------------------------------------
# Author credentials
# ---------------------------------------------------------------------------

def check_author(name: str, orcid: str = None) -> dict:
    """Look up author publication record via OpenAlex.

    Parameters
    ----------
    name : str
        Author name (e.g., "Mysore V. Nagendran").
    orcid : str, optional
        ORCID identifier for disambiguation (recommended).

    Returns
    -------
    dict
        Keys: works_count (int), cited_by_count (int), h_index (int),
        institution (str), top_fields (list of str), orcid (str or None).

    Detection heuristics
    --------------------
    (a) works_count < 5 making extraordinary claims → flag.
    (b) top_fields don't overlap with paper's field → flag.
    (c) institution is the company whose product is studied → COI flag.

    Caveat: name disambiguation is hard. Provide ORCID when available.
    """
    _HEADERS = {"User-Agent": "bullshit-detector/0.1 (mailto:info@example.org)"}

    result = {
        "works_count": 0,
        "cited_by_count": 0,
        "h_index": 0,
        "institution": None,
        "top_fields": [],
        "orcid": orcid,
    }

    try:
        # When ORCID is provided, use the direct author endpoint — unambiguous.
        if orcid:
            _orcid = orcid.replace("https://orcid.org/", "")
            url = f"https://api.openalex.org/authors/https://orcid.org/{_orcid}"
            resp = requests.get(url, timeout=10, headers=_HEADERS)
            resp.raise_for_status()
            author = resp.json()
        else:
            url = (
                "https://api.openalex.org/authors?search="
                + requests.utils.quote(name, safe="")
            )
            resp = requests.get(url, timeout=10, headers=_HEADERS)
            resp.raise_for_status()
            data = resp.json()
            if not data.get("results"):
                return result
            author = data["results"][0]

        result["works_count"] = author.get("works_count", 0) or 0
        result["cited_by_count"] = author.get("cited_by_count", 0) or 0
        result["h_index"] = (author.get("summary_stats") or {}).get("h_index", 0) or 0
        result["orcid"] = author.get("orcid")

        # Last known institution
        affiliations = author.get("affiliations") or []
        if affiliations:
            inst = affiliations[0].get("institution", {})
            result["institution"] = inst.get("display_name")
        else:
            institutions = author.get("last_known_institutions") or []
            if institutions:
                result["institution"] = institutions[0].get("display_name")

        # Top fields from topics (sorted by count desc, take display_name)
        topics = author.get("topics") or []
        result["top_fields"] = [
            t["display_name"]
            for t in sorted(topics, key=lambda x: x.get("count", 0), reverse=True)[:5]
            if t.get("display_name")
        ]
    except Exception:
        pass

    return result
