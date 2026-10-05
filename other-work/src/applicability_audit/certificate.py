"""The audit certificate: is this ranking structurally interpretable?

The certificate answers a structural question, never a scientific one. It says
whether the declared contracts make a ranking readable at all; it does not say
whether an effect matters, and it introduces no threshold of its own.

In particular, a low applicability rate never invalidates a ranking by itself.
If cases were admitted, a non-empty common support exists, case alignment is
exact, metric validity is satisfied and the aggregation is declared, then the
ranking on that common support is admissible --- and the certificate reports the
low coverage alongside it rather than instead of it.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence

from .serialization import SCHEMA_VERSION, is_unavailable, key_repr, unavailable

CERTIFICATE_SCHEMA_VERSION = "applicability_audit/certificate/1"

RANKING_ADMISSIBLE = "RANKING_ADMISSIBLE"
RANKING_NOT_ADMISSIBLE = "RANKING_NOT_ADMISSIBLE"

AUDIT_COMPLETE = "AUDIT_COMPLETE"
AUDIT_FAILED = "AUDIT_FAILED"

REASON_CODES = (
    "NO_ADMITTED_CASES",
    "NO_COMMON_SUPPORT",
    "CASE_ALIGNMENT_MISMATCH",
    "METHOD_SUPPORT_INCOMPLETE",
    "METRIC_VALIDITY_FAILURE",
    "AGGREGATION_CONTRACT_INVALID",
    "DUPLICATE_CASE_KEYS",
    "INCOMPLETE_METHOD_RESULTS",
    "OUTCOME_LEAKAGE_DETECTED",
)

REASON_TAXONOMY = {
    "NO_ADMITTED_CASES": "applicability_admission",
    "NO_COMMON_SUPPORT": "method_support",
    "CASE_ALIGNMENT_MISMATCH": "common_support_mismatch",
    "METHOD_SUPPORT_INCOMPLETE": "method_support",
    "METRIC_VALIDITY_FAILURE": "metric_validity",
    "AGGREGATION_CONTRACT_INVALID": "aggregation_configuration",
    "DUPLICATE_CASE_KEYS": "population_scoreability",
    "INCOMPLETE_METHOD_RESULTS": "post_admission_reconstruction",
    "OUTCOME_LEAKAGE_DETECTED": "applicability_admission",
}

CHECK_ORDER = (
    ("population_contract", "Population contract"),
    ("applicability_partition", "Applicability partition"),
    ("natural_run_integrity", "Natural-run integrity"),
    ("case_identity", "Case identity"),
    ("method_support_accounting", "Method-support accounting"),
    ("metric_validity", "Metric validity"),
    ("common_support_identity", "Common-support identity"),
    ("aggregation_declaration", "Aggregation declaration"),
    ("outcome_leakage_safeguards", "Outcome-leakage safeguards"),
)


def build_certificate(result: Dict[str, object],
                      extra_reasons: Optional[Sequence[str]] = None,
                      fatal: bool = False) -> Dict[str, object]:
    """Derive the certificate from an already validated audit result."""
    reasons: List[str] = list(extra_reasons or [])
    checks = {
        "population_contract": result["population"]["observations_in_population"] >= 0,
        "applicability_partition": (
            True if is_unavailable(result["applicability"]) else
            bool(result["applicability"]["exact_partition_verified"])),
        "natural_run_integrity": (
            True if is_unavailable(result["natural_runs"]) else
            sum(result["natural_runs"]["by_grid_length"].values())
            + result["natural_runs"]["off_grid"] == result["natural_runs"]["total"]),
        "case_identity": bool(result["cases"]["unique_keys_verified"]),
        "method_support_accounting": bool(result["method_support"]),
        "metric_validity": result["metric_validity"]["C"] >= 0,
        "common_support_identity": bool(
            result["common_support"]["case_keys_identical_across_methods"]),
        "aggregation_declaration": bool(
            result["aggregation"]["contract"]["levels"]),
        "outcome_leakage_safeguards": bool(
            result["validation"]["no_silent_case_drop"]),
    }
    for name, passed in sorted(checks.items()):
        if passed:
            continue
        code = {"applicability_partition": "OUTCOME_LEAKAGE_DETECTED",
                "case_identity": "DUPLICATE_CASE_KEYS",
                "common_support_identity": "CASE_ALIGNMENT_MISMATCH",
                "aggregation_declaration": "AGGREGATION_CONTRACT_INVALID",
                "method_support_accounting": "METHOD_SUPPORT_INCOMPLETE",
                "metric_validity": "METRIC_VALIDITY_FAILURE"}.get(name)
        if code and code not in reasons:
            reasons.append(code)

    A = result["cases"]["admitted_A"]
    D = result["common_support"]["D"]
    if A == 0 and "NO_ADMITTED_CASES" not in reasons:
        reasons.append("NO_ADMITTED_CASES")
    elif D == 0 and "NO_COMMON_SUPPORT" not in reasons:
        reasons.append("NO_COMMON_SUPPORT")

    admissible = (not reasons) and all(checks.values()) and D > 0
    unknown = [r for r in reasons if r not in REASON_CODES]
    if unknown:                              # pragma: no cover - defensive
        raise ValueError("unknown reason code(s): %r" % (unknown,))

    return {
        "schema_version": CERTIFICATE_SCHEMA_VERSION,
        "audit_status": AUDIT_FAILED if fatal else AUDIT_COMPLETE,
        "ranking_admissible": bool(admissible),
        "ranking_verdict": RANKING_ADMISSIBLE if admissible else RANKING_NOT_ADMISSIBLE,
        "reason_codes": sorted(set(reasons)),
        "reason_taxonomy": {r: REASON_TAXONOMY[r] for r in sorted(set(reasons))},
        "checks": {k: ("PASS" if v else "FAIL") for k, v in sorted(checks.items())},
        "coverage": result["diagnostics"]["coverage"],
        "support_geometry": {
            "overlap_measure": result["diagnostics"]["support_geometry"]["overlap_measure"],
            "all_supports_identical":
                result["diagnostics"]["support_geometry"]["all_supports_identical"]},
        "methods": sorted(result["method_support"]),
        "mode": result["provenance"].get("mode", "executable"),
        "configuration_fingerprint": result["provenance"]["configuration_fingerprint"],
        "provenance": {
            "schema_version": result["schema_version"],
            "applicability_contract": result["provenance"]["applicability_contract"],
            "aggregation_contract": result["provenance"]["aggregation_contract"],
            "stability_contract": result["provenance"]["stability_contract"],
            "supplied": result["provenance"].get("supplied", {})},
        "note": ("a low applicability rate does not by itself make a ranking "
                 "inadmissible; coverage and structural admissibility are "
                 "reported separately"),
    }


def _fmt(value, digits=6):
    if is_unavailable(value):
        return "unavailable"
    if isinstance(value, float):
        return ("%%.%df" % digits) % value
    return str(value)


def render_audit_report(certificate: Dict[str, object]) -> str:
    """A deterministic plain-text/markdown rendering. No colours, no plotting."""
    cov = certificate["coverage"]
    app, sup = cov["applicability"], cov["support_retention"]
    width = max(len(label) for _, label in CHECK_ORDER) + 2
    lines = ["# Applicability Audit Certificate", ""]
    lines.append("Mode: %s" % certificate["mode"])
    lines.append("")
    for key, label in CHECK_ORDER:
        lines.append("%-*s %s" % (width, label, certificate["checks"][key]))
    lines.append("")
    lines.append("%-*s %s" % (width, "Ranking admissible",
                              "YES" if certificate["ranking_admissible"] else "NO"))
    if certificate["reason_codes"]:
        lines.append("%-*s %s" % (width, "Reason codes",
                                  ", ".join(certificate["reason_codes"])))
    lines.append("")
    lines.append("%-*s %s" % (width, "Scoreable targets",
                              _fmt(app["scoreable_targets"])))
    lines.append("%-*s %s" % (width, "Applicable targets",
                              _fmt(app["applicable_targets"])))
    lines.append("%-*s %s" % (width, "Applicability rate",
                              _fmt(app["applicability_rate"])))
    lines.append("%-*s %s" % (width, "Admitted cases", _fmt(sup["admitted_cases_A"])))
    lines.append("%-*s %s" % (width, "Common-support cases",
                              _fmt(sup["common_support_cases_D"])))
    lines.append("%-*s %s" % (width, "Common-support retention",
                              _fmt(sup["common_support_retention_conditional_on_A"])))
    lines.append("")
    lines.append("Applicability coverage and support retention are distinct: "
                 "a low rate here does not invalidate the ranking on D.")
    return "\n".join(lines) + "\n"


def render_support_matrix(geometry: Dict[str, object]) -> str:
    """A deterministic text rendering of the pairwise overlap matrix."""
    names = geometry["methods"]
    if not names:                            # pragma: no cover - defensive
        return "(no method)\n"
    w = max(len(n) for n in names) + 2
    head = " " * w + "".join("%-*s" % (w, n) for n in names)
    lines = ["Pairwise support overlap (%s)" % geometry["overlap_measure"], head]
    for i in names:
        row = "%-*s" % (w, i)
        for j in names:
            row += "%-*s" % (w, _fmt(geometry["matrix"][i][j]["jaccard"], 3))
        lines.append(row)
    return "\n".join(lines) + "\n"
