"""Layer 3: metric validity C, per-method support B_m, and common support D.

The three are computed and reported separately, because a benchmark can be
perfectly support-aligned and still be almost entirely inapplicable. Collapsing
them would hide exactly the distinction the audit exists to expose.
"""
from __future__ import annotations

import math
from typing import Dict, List, Sequence, Set

from .cases import AuditCase
from .contracts import AuditContractError, MethodContract
from .serialization import unavailable

UNDEFINED = None


def metric_valid(case: AuditCase) -> bool:
    """Set C: every target of the case needs a finite, strictly positive scale.

    A case whose scale is missing entirely is metric-valid for unnormalized
    fields; callers that need normalization must supply a scale.
    """
    for s in case.eval_only["metric_scale"]:
        if s is None or not math.isfinite(s) or s <= 0:
            return False
    return True


def support_sets(cases: Sequence[AuditCase],
                 methods: Sequence[MethodContract]) -> Dict[str, object]:
    """Build A, C, B_m and D explicitly and keep them separable for reporting."""
    if not methods:
        raise AuditContractError("at least one method contract is required")
    A = [c.key for c in cases]
    C = set(c.key for c in cases if metric_valid(c))
    B = {}
    for m in methods:
        B[m.method_id] = set(c.key for c in cases if m.supports(c.method_input()))
    D = set(A) & C
    for m in methods:
        D &= B[m.method_id]
    return {"A": A, "B": B, "C": C, "D": D}


def method_specific_support(sets: Dict[str, object], method_id: str) -> Set:
    """A ∩ C ∩ B_m --- the diagnostic set for one method on its own terms."""
    return set(sets["A"]) & sets["C"] & sets["B"][method_id]


def assert_identical_common_support(sets: Dict[str, object],
                                    methods: Sequence[MethodContract]) -> None:
    """Headline comparison requires exactly the same case keys for every method.

    Pairing by position would silently compare different populations, so a
    mismatch is a hard failure rather than a warning.
    """
    D = sets["D"]
    for m in methods:
        own = method_specific_support(sets, m.method_id)
        if not D <= own:
            raise AuditContractError(
                "common support is not contained in the support of method %r"
                % m.method_id)
    keys = {m.method_id: set(D) for m in methods}
    names = sorted(keys)
    first = keys[names[0]]
    for n in names[1:]:
        if keys[n] != first:                 # pragma: no cover - defensive
            raise AuditContractError(
                "common-support case keys differ between %s and %s" % (names[0], n))


def support_retention(sets: Dict[str, object]):
    """|D| / |A|, or the structured unavailable state when A is empty."""
    A = sets["A"]
    if not A:
        return unavailable("no admitted case; |A| = 0")
    return len(sets["D"]) / float(len(A))


def reconstruct_case(case: AuditCase, method: MethodContract):
    """Run one method on one case. Returns UNDEFINED, never a surrogate."""
    pred = method.reconstruct(case.method_input())
    if pred is UNDEFINED:
        return UNDEFINED
    pred = [tuple(float(x) for x in p) for p in pred]
    if len(pred) != len(case.tgt_t):
        raise AuditContractError(
            "method %r returned %d predictions for %d targets on case %r"
            % (method.method_id, len(pred), len(case.tgt_t), case.key))
    return pred


def target_errors(case: AuditCase, pred) -> Dict[str, List[float]]:
    """Per-target raw distance and scale-normalized distance."""
    if pred is UNDEFINED:
        raise AuditContractError(
            "refusing to score an undefined method output; no surrogate error "
            "exists for case %r" % (case.key,))
    ev = case.eval_only
    raw, normalized = [], []
    for i, actual in enumerate(ev["tgt_v"]):
        p = pred[i]
        if actual is None or len(p) != len(actual):
            raise AuditContractError(
                "prediction and reference dimensionality disagree on case %r"
                % (case.key,))
        d = math.sqrt(sum((p[k] - actual[k]) ** 2 for k in range(len(actual))))
        raw.append(d)
        scale = ev["metric_scale"][i]
        if scale is None or not math.isfinite(scale) or scale <= 0:
            raise AuditContractError(
                "case %r has a non-positive metric scale and must not be scored"
                % (case.key,))
        normalized.append(d / scale)
    return {"raw": raw, "normalized": normalized}
