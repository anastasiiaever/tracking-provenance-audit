"""A reusable, dataset-agnostic applicability audit for reconstruction tasks.

The audit separates four questions that benchmarks routinely conflate:

1. population / scoreability --- which observations are in scope at all?
2. applicability / admission --- can a target be evaluated under the frozen
   target-anchor continuity contract?
3. method support --- can method *m* produce a valid result for an admitted case?
4. ranking --- how do methods compare on identical common support?

Formally, with ``T`` the scoreable targets, ``A`` the admitted cases, ``B_m`` the
support of method *m*, ``C`` the metric-valid cases and
``D = A ∩ C ∩ ⋂_m B_m``, headline ranking uses ``D`` only.

This package is an evaluation artifact, not a reconstruction algorithm, and it
contains no dataset-specific annotation semantics.
"""
from .aggregation import (AggregationContract, frozen_trajectory_ladder,
                          simple_case_ladder)
from .audit import (AuditCertificate, AuditResult, audit_precomputed_results,
                    run_applicability_audit)
from .certificate import (RANKING_ADMISSIBLE, RANKING_NOT_ADMISSIBLE,
                          REASON_CODES, render_audit_report,
                          render_support_matrix)
from .contracts import (APPLICABILITY_CLASSES, AggregationLevel,
                        ApplicabilityContract, AuditContractError,
                        CanonicalObservation, FAILURE_MODES, MethodContract,
                        StabilityContract)
from .serialization import SCHEMA_VERSION, dumps, is_unavailable, unavailable

__all__ = [
    "run_applicability_audit",
    "audit_precomputed_results",
    "AuditResult",
    "AuditCertificate",
    "render_audit_report",
    "render_support_matrix",
    "RANKING_ADMISSIBLE",
    "RANKING_NOT_ADMISSIBLE",
    "REASON_CODES",
    "CanonicalObservation",
    "ApplicabilityContract",
    "MethodContract",
    "AggregationContract",
    "AggregationLevel",
    "StabilityContract",
    "frozen_trajectory_ladder",
    "simple_case_ladder",
    "AuditContractError",
    "APPLICABILITY_CLASSES",
    "FAILURE_MODES",
    "SCHEMA_VERSION",
    "dumps",
    "unavailable",
    "is_unavailable",
]
