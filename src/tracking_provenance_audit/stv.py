"""Semantic Trajectory Validity, exactly as frozen in 02_PROSPECTIVE_PROTOCOL.json.

Gate before assignment; one-to-one Hungarian assignment on R0 only, per frame,
against scoreable GT; the assignment is frozen before synthesized rows exist.
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple
from .rowid import Row, RowId, iou

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
    """Optimal one-to-one assignment. scipy when available, else exact fallback."""
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
        best, pairs = None, []
        rows = range(n)
        for perm in itertools.permutations(range(m), min(n, m)):
            tot = sum(cost[i][perm[i]] for i in range(len(perm)))
            if best is None or tot < best:
                best = tot
                pairs = [(i, perm[i]) for i in range(len(perm))]
        return pairs


def assign_reference(r0_rows: List[Row], gt_rows: List[Row],
                     gate: float = PRIMARY_IOU_GATE) -> Dict[RowId, int]:
    """Per-frame one-to-one R0 -> GT identity assignment, gate applied first."""
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
        # gate BEFORE assignment: ineligible pairs cannot be selected
        BIG = 1e6
        cost = [[(1.0 - ious[i][j]) if ious[i][j] >= gate else BIG
                 for j in range(len(gts))] for i in range(len(preds))]
        for i, j in _hungarian(cost):
            if i < len(preds) and j < len(gts) and cost[i][j] < BIG:
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
