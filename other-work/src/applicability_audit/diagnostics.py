"""Support geometry: how the methods' support sets relate to each other.

Applicability coverage and method-support agreement are different questions and
are reported separately here. A benchmark can be almost entirely inapplicable
and still have perfect conditional agreement between methods; another can be
broadly applicable and still be uncomparable because the methods ran on
different cases. Collapsing the two into one "support" number hides both.
"""
from __future__ import annotations

from typing import Dict, Sequence, Set

from .serialization import unavailable


def jaccard(a: Set, b: Set):
    """|a ∩ b| / |a ∪ b|, or the structured unavailable state for two empty sets."""
    union = a | b
    if not union:
        return unavailable("both support sets are empty; overlap is undefined")
    return len(a & b) / float(len(union))


def pairwise_support_geometry(support: Dict[str, Set]) -> Dict[str, object]:
    """A deterministic, symmetric table of pairwise support relationships.

    The normalized overlap is the Jaccard index, named explicitly rather than
    reported as an unlabelled "similarity" number. The diagonal is 1.0 for a
    non-empty set and structured unavailable for an empty one.
    """
    names = sorted(support)
    matrix = {}
    for i in names:
        row = {}
        for j in names:
            bi, bj = set(support[i]), set(support[j])
            row[j] = {"size_i": len(bi), "size_j": len(bj),
                      "intersection": len(bi & bj), "union": len(bi | bj),
                      "jaccard": jaccard(bi, bj)}
        matrix[i] = row
    return {"overlap_measure": "jaccard",
            "overlap_definition": "|B_i intersect B_j| / |B_i union B_j|",
            "methods": names,
            "matrix": matrix,
            "all_supports_identical": len({frozenset(support[n]) for n in names}) == 1}


def coverage_diagnostics(scoreable_targets: int, applicable_targets: int,
                         admitted_A: int, per_method_conditional: Dict[str, int],
                         common_D: int) -> Dict[str, object]:
    """Applicability coverage and support retention, kept deliberately apart.

    ``applicability_rate`` is a target-level quantity over the whole population.
    The retentions are case-level quantities conditional on admission. A low
    applicability rate says nothing about whether the admitted cases can be
    compared, and neither number may be substituted for the other.
    """
    def _rate(num, den, reason):
        return unavailable(reason) if not den else num / float(den)

    return {
        "applicability": {
            "scoreable_targets": scoreable_targets,
            "applicable_targets": applicable_targets,
            "applicability_rate": _rate(applicable_targets, scoreable_targets,
                                        "no scoreable target in the population"),
            "unit": "target",
            "note": "population-level coverage; independent of method support"},
        "support_retention": {
            "admitted_cases_A": admitted_A,
            "per_method_conditional_on_A": {
                m: _rate(n, admitted_A, "no admitted case; |A| = 0")
                for m, n in sorted(per_method_conditional.items())},
            "common_support_cases_D": common_D,
            "common_support_retention_conditional_on_A": _rate(
                common_D, admitted_A, "no admitted case; |A| = 0"),
            "unit": "case",
            "note": "conditional on admission; independent of applicability rate"},
    }
