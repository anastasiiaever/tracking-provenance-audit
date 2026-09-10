"""Operators, metric, common support and the frozen aggregation ladder.

Support ladder mirrors the frozen KITTI A/B/C/D structure (Record 57 sec. 8):

  A  Gate-1R candidate cases on the frozen exact-length grid
  B  per-method mathematical validity
  C  metric-normalization validity
  D  A and B and C intersected over EVERY method  -> the headline set
"""
from __future__ import annotations

import math
from typing import Dict, List, Sequence

# PATH NORMALISATION FOR RELEASE (no scientific change): the research tree kept
# this module under `scripts/` and injected the repository root into sys.path to
# reach `reconstruction_generic`. In this repository both packages are siblings
# under `src/`, so the plain import below resolves them directly.
from reconstruction_generic import OPERATORS, OperatorUndefined

from .protocol57 import GAP_GRID, OPERATOR_NAMES, ProtocolViolation  # noqa: E402

UNDEFINED = None          # an undefined operator NEVER yields a finite number


# ----------------------------------------------------------------- validity C
def normalization_valid(case: dict) -> bool:
    """Every target frame needs a finite, strictly positive bbox diagonal."""
    for d in case["eval_only"]["diagonal"]:
        if d is None or not math.isfinite(d) or d <= 0:
            return False
    return True


def operator_valid(case: dict, name: str) -> bool:
    """Set B: is this operator mathematically defined on this case, for x and y?"""
    op = OPERATORS[name]
    return bool(op.supports(case["obs_t"], case["obs_cx"], case["tgt_t"])
                and op.supports(case["obs_t"], case["obs_cy"], case["tgt_t"]))


def support_sets(cases: Sequence[dict]) -> Dict[str, object]:
    """Build A/B/C/D explicitly and keep them separable for reporting."""
    A = [c["key"] for c in cases]
    C = set(c["key"] for c in cases if normalization_valid(c))
    B = {n: set(c["key"] for c in cases if operator_valid(c, n)) for n in OPERATOR_NAMES}
    D = set(A) & C
    for n in OPERATOR_NAMES:
        D &= B[n]
    return {"A": A, "B": B, "C": C, "D": D}


def assert_identical_case_keys(per_method_keys: Dict[str, set]) -> None:
    """Exact case-key equality across methods, asserted before aggregation."""
    names = sorted(per_method_keys)
    if not names:
        raise ProtocolViolation("no method supplied to the common-support check")
    first = per_method_keys[names[0]]
    for n in names[1:]:
        if per_method_keys[n] != first:
            raise ProtocolViolation(
                "common-support case keys differ between %s and %s" % (names[0], n))


# ------------------------------------------------------------------ operators
def reconstruct(case: dict, name: str):
    """Run one operator on one case.

    Receives anchor times, anchor centres and target times ONLY. Returns
    ``UNDEFINED`` when the operator is not defined -- never a surrogate value.
    """
    op = OPERATORS[name]
    try:
        cx = op(case["obs_t"], case["obs_cx"], case["tgt_t"])
        cy = op(case["obs_t"], case["obs_cy"], case["tgt_t"])
    except OperatorUndefined:
        return UNDEFINED
    return list(cx), list(cy)


# --------------------------------------------------------------------- metric
def target_errors(case: dict, pred) -> Dict[str, List[float]]:
    """Primary normalized error and secondary raw pixel error, per target frame."""
    if pred is UNDEFINED:
        raise ProtocolViolation(
            "refusing to score an undefined operator; no surrogate error exists")
    cx, cy = pred
    ev = case["eval_only"]
    norm, raw = [], []
    for i in range(len(case["tgt_t"])):
        dx = cx[i] - ev["tgt_cx"][i]
        dy = cy[i] - ev["tgt_cy"][i]
        e = math.sqrt(dx * dx + dy * dy)
        d = ev["diagonal"][i]
        if d is None or not math.isfinite(d) or d <= 0:
            raise ProtocolViolation("target bbox diagonal is non-positive")
        raw.append(e)
        norm.append(e / d)
    return {"normalized": norm, "raw_pixel": raw}


# ---------------------------------------------------------------- aggregation
def _mean(vals):
    vals = [v for v in vals if v is not None]
    return sum(vals) / float(len(vals)) if vals else None


def aggregate(case_records: Sequence[dict], field: str = "normalized"):
    """Frozen KITTI ladder, with video substituted for sequence.

    target error -> case mean -> mean within (video, gap length)
      -> equal-weight mean over REPRESENTED grid lengths within video
        -> equal-weight mean across contributing videos
    """
    by_video = {}
    for rec in case_records:
        cm = _mean(rec["errors"][field])
        if cm is None:
            continue
        by_video.setdefault(rec["sequence_id"], {}).setdefault(rec["gap_length"], []).append(cm)
    per_video = {}
    for vid, by_g in by_video.items():
        cell = {g: _mean(v) for g, v in by_g.items() if g in GAP_GRID}
        represented = [cell[g] for g in GAP_GRID if g in cell]
        per_video[vid] = {"cells": cell, "video_mean": _mean(represented),
                          "represented_gap_lengths": [g for g in GAP_GRID if g in cell]}
    headline = _mean([v["video_mean"] for v in per_video.values()])
    support = {g: sorted(v for v, d in per_video.items() if g in d["cells"])
               for g in GAP_GRID}
    return {"headline": headline, "per_video": per_video,
            "contributing_videos_per_gap_length": {g: len(support[g]) for g in GAP_GRID},
            "gap_lengths_reported": list(GAP_GRID),
            "aggregation": "case mean -> (video, g) mean -> equal-weight over "
                           "represented g within video -> equal-weight across videos"}
