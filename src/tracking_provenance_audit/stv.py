"""Semantic Trajectory Validity, exactly as frozen in 02_PROSPECTIVE_PROTOCOL.json.

Gate before assignment; one-to-one Hungarian assignment on R0 only, per frame,
against scoreable GT; the assignment is frozen before synthesized rows exist.

The matcher follows the stateless TrackEval preprocessing form. IoU similarities
below the gate are set to zero before the one-to-one assignment, and selected
zero-similarity pairs are removed from the returned assignment. No below-gate pair
is ever returned as a reference match, but a zeroed entry can still affect the
global assignment through row/column competition. Selected pairs are therefore not
guaranteed to be nested as the gate rises; only the set of above-gate entries is.
"""
from __future__ import annotations
import sys
from typing import Dict, List, Optional, Tuple
from .rowid import Row, RowId, iou

# Same numerical convention as the frozen classifier and TrackEval, which both
# use numpy's float eps; sys.float_info.epsilon is that identical value.
_EPS = sys.float_info.epsilon

PRIMARY_IOU_GATE = 0.5
SENSITIVITY_GATES = (0.3, 0.4, 0.5, 0.6, 0.7)

ANCHOR_UNMATCHED = "ANCHOR_UNMATCHED"
ANCHOR_ID_MISMATCH = "ANCHOR_ID_MISMATCH"
TARGET_REFERENCE_ABSENT = "TARGET_REFERENCE_ABSENT"
SEMANTICALLY_ADMITTED = "SEMANTICALLY_ADMITTED"
CLASSES = (ANCHOR_UNMATCHED, ANCHOR_ID_MISMATCH, TARGET_REFERENCE_ABSENT,
           SEMANTICALLY_ADMITTED)

# Only this class licenses the frozen semantic phrasing.
SEMANTIC_REASON = {
    ANCHOR_ID_MISMATCH:
        "the two anchors resolve, under the frozen matcher, to different "
        "ground-truth identities",
    ANCHOR_UNMATCHED:
        "non-admission under the frozen matching rule; NOT a demonstrated "
        "semantic error and NOT a false positive",
    TARGET_REFERENCE_ABSENT:
        "the agreed reference identity is absent at the target frame",
    SEMANTICALLY_ADMITTED: "admitted under the frozen reference-semantic rule",
}


def _hungarian(cost: List[List[float]]) -> List[Tuple[int, int]]:
    """Minimum-cost one-to-one assignment. scipy when available, else exact search.

    Both paths minimise the same objective over exactly min(n, m) pairs. When the
    rows outnumber the columns the search runs over row subsets, otherwise over
    column subsets; taking only the first rows would ignore cheaper assignments
    available to later rows and would disagree with scipy.
    """
    if not cost or not cost[0]:
        return []
    try:
        import numpy as np
        from scipy.optimize import linear_sum_assignment
        r, c = linear_sum_assignment(np.array(cost, dtype=float))
        return list(zip(r.tolist(), c.tolist()))
    except Exception:
        import itertools
        n, m = len(cost), len(cost[0])
        if n <= m:
            candidates = ([(i, cols[i]) for i in range(n)]
                          for cols in itertools.permutations(range(m), n))
        else:
            candidates = ([(rows[j], j) for j in range(m)]
                          for rows in itertools.permutations(range(n), m))
        best, pairs = None, []
        for candidate in candidates:
            tot = sum(cost[i][j] for i, j in candidate)
            if best is None or tot < best:
                best, pairs = tot, candidate
        return pairs


def assign_reference(r0_rows: List[Row], gt_rows: List[Row],
                     gate: float = PRIMARY_IOU_GATE) -> Dict[RowId, int]:
    """Per-frame one-to-one R0 -> GT identity assignment, gate applied first.

    Similarities below ``gate`` are zeroed before assignment and selected
    zero-similarity pairs are removed from the result, so no below-gate pair is
    returned. Zeroed entries may still compete for a row or column slot.
    """
    by_frame_pred: Dict[int, List[Row]] = {}
    by_frame_gt: Dict[int, List[Row]] = {}
    for r in r0_rows:
        by_frame_pred.setdefault(r.frame, []).append(r)
    for g in gt_rows:
        by_frame_gt.setdefault(g.frame, []).append(g)
    out: Dict[RowId, int] = {}
    for frame, preds in by_frame_pred.items():
        gts = by_frame_gt.get(frame, [])
        if not gts:
            continue
        preds = sorted(preds, key=lambda r: r.track_id)
        gts = sorted(gts, key=lambda g: g.track_id)
        ious = [[iou(p, g) for g in gts] for p in preds]
        # Gate BEFORE assignment, in the TrackEval preprocessing form: sub-gate
        # similarities are zeroed, the assignment maximises the total remaining
        # similarity, and any selected zero-similarity pair is then dropped.
        score = [[ious[i][j] if ious[i][j] >= gate - _EPS else 0.0
                  for j in range(len(gts))] for i in range(len(preds))]
        # _hungarian minimises, so negating makes it maximise total similarity;
        # the scipy path and the fallback therefore solve the same problem.
        neg = [[-v for v in row] for row in score]
        for i, j in _hungarian(neg):
            if i < len(preds) and j < len(gts) and score[i][j] > _EPS:
                out[preds[i].rid] = gts[j].track_id
    return out


def anchors_for(synth_rid: RowId, r0_frames_by_track: Dict[int, List[int]]
                ) -> Optional[Tuple[int, int]]:
    """The two bracketing R0 observation frames of a synthesized row."""
    seq, frame, track = synth_rid
    frames = r0_frames_by_track.get(track)
    if not frames:
        return None
    left = None
    right = None
    for f in frames:
        if f < frame:
            left = f if left is None or f > left else left
        elif f > frame:
            right = f if right is None or f < right else right
    if left is None or right is None:
        return None
    return (left, right)


def classify(synth_rids, r0_rows: List[Row], gt_rows: List[Row],
             gate: float = PRIMARY_IOU_GATE) -> Dict[RowId, str]:
    """Classify every synthesized row into exactly one class, in priority order."""
    assign = assign_reference(r0_rows, gt_rows, gate)
    frames_by_track: Dict[int, List[int]] = {}
    for r in r0_rows:
        frames_by_track.setdefault(r.track_id, []).append(r.frame)
    for k in frames_by_track:
        frames_by_track[k].sort()
    gt_ids_by_frame: Dict[int, set] = {}
    for g in gt_rows:
        gt_ids_by_frame.setdefault(g.frame, set()).add(g.track_id)

    out: Dict[RowId, str] = {}
    for rid in synth_rids:
        seq, frame, track = rid
        anc = anchors_for(rid, frames_by_track)
        if anc is None:
            out[rid] = ANCHOR_UNMATCHED
            continue
        lf, rf = anc
        la = assign.get((seq, lf, track))
        ra = assign.get((seq, rf, track))
        if la is None or ra is None:            # 1
            out[rid] = ANCHOR_UNMATCHED
        elif la != ra:                          # 2
            out[rid] = ANCHOR_ID_MISMATCH
        elif la not in gt_ids_by_frame.get(frame, set()):   # 3
            out[rid] = TARGET_REFERENCE_ABSENT
        else:                                   # 4
            out[rid] = SEMANTICALLY_ADMITTED
    return out


def partition_counts(classes: Dict[RowId, str]) -> Dict[str, int]:
    counts = {c: 0 for c in CLASSES}
    for v in classes.values():
        counts[v] += 1
    assert sum(counts.values()) == len(classes), "STV partition is not exact"
    return counts
