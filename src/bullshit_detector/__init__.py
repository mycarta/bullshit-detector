"""
bullshit-detector: Statistical detection tools for screening published research.

This package provides tools organized in four tiers:

    Tier 0 — Paper-level screening (journal, retraction, author checks)
    Tier 1 — Arithmetic consistency (GRIM, A-GRIMMER, p-value recomputation)
    Tier 2 — Statistical plausibility (spurious correlation, critical r, CI)
    Tier 3 — Domain judgment + data access (influence plots, distance correlation,
             variable clustering, reproducibility challenges)

Intellectual foundations:
    - Bergstrom & West (2020), "Calling Bullshit: The Art of Skepticism in a
      Data-Driven World", Random House. Their paper-level legitimacy framework
      directly inspired the Tier 0 screening module.
    - Frankfurt (2005), "On Bullshit", Princeton University Press.
    - Kalkomey (1997), "Potential risks when using seismic attributes as
      predictors of reservoir properties", The Leading Edge.
    - Sainani (2020), "How to Be a Statistical Detective", PM&R 12(2):211-215.

See skills/ directory for detection heuristics and worked examples.
See README.md for full references and installation instructions.

Modules:
    paper_screening — Tier 0: journal, retraction, author checks
    p_checker       — Tier 1: p-value recomputation
    grimmer         — Tier 1: A-GRIMMER test (means + SDs from integer scales)
    spurious        — Tier 2: Kalkomey spurious correlation probability
    power           — Tier 2: sample size and power calculations
    redundancy      — Tier 2: variable redundancy analysis
    dc_cluster      — Tier 3: distance correlation matrix and variable clustering
    leverage        — Tier 3: outlier influence and distance correlation tests
    reproducibility — Tier 3: error flagging and bootstrap CIs
"""

__version__ = "0.1.0"
