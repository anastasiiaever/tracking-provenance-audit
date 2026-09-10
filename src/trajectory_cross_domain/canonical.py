"""Canonical trajectory rows and the dataset-independent applicability layer.

Dataset parsers produce ``CanonicalRow`` objects; everything downstream --- the
segmentation contract, Gate 1R, natural-run extraction --- is written against
that representation only and knows nothing about BDD or MOT17.

Leakage rule (Record 57 sec. 4 and sec. 13): ``center_x``/``center_y`` of a
TARGET row and ``normalization_diagonal`` are evaluation-only. The case payload
built by :func:`build_cases` therefore carries anchor centres and target times
and never a target centre or box size.
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .protocol57 import GAP_GRID, GATE_1R_CLASSES, ProtocolViolation


class CanonicalRow(object):
    """One annotated observation of one trajectory at one frame.

    Exactly one of ``target`` / ``anchor`` / ``breaker`` is True; a row outside
    the frozen population is not emitted at all.
    """

    __slots__ = ("population", "sequence_id", "track_id", "frame_index",
                 "x1", "y1", "x2", "y2", "center_x", "center_y",
                 "target", "anchor", "breaker", "category",
                 "normalization_diagonal", "provenance")

    def __init__(self, population, sequence_id, track_id, frame_index,
                 x1, y1, x2, y2, target, anchor, breaker, category,
                 normalization_diagonal=None, provenance=None):
        self.population = population
        self.sequence_id = sequence_id
        self.track_id = track_id
        self.frame_index = int(frame_index)
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
        self.center_x = None if x1 is None else (x1 + x2) / 2.0
        self.center_y = None if y1 is None else (y1 + y2) / 2.0
        self.target = bool(target)
        self.anchor = bool(anchor)
        self.breaker = bool(breaker)
        self.category = category
        self.normalization_diagonal = normalization_diagonal
        self.provenance = provenance or {}
        n = sum((self.target, self.anchor, self.breaker))
        if n != 1:
            raise ProtocolViolation(
                "row must be exactly one of target/anchor/breaker, got %d" % n)

    @property
    def key(self):
        return (self.population, self.sequence_id, self.track_id, self.frame_index)

    def __repr__(self):
        role = "target" if self.target else ("anchor" if self.anchor else "breaker")
        return "<CanonicalRow %s/%s/%s@%d %s>" % (
            self.population, self.sequence_id, self.track_id, self.frame_index, role)


# --------------------------------------------------------------- segmentation
def group_trajectories(rows: Iterable[CanonicalRow]) -> Dict[Tuple, List[CanonicalRow]]:
    """Group rows by (population, sequence_id, track_id), ordered by frame.

    Duplicate (trajectory, frame) keys are a hard error: Record 57 forbids
    silent deduplication.
    """
    out = {}
    for r in rows:
        out.setdefault((r.population, r.sequence_id, r.track_id), []).append(r)
    for key, group in out.items():
        seen = {}
        for r in group:
            if r.frame_index in seen:
                raise ProtocolViolation(
                    "duplicate trajectory-frame key %r at frame %d; silent "
                    "deduplication is forbidden" % (key, r.frame_index))
            seen[r.frame_index] = r
        group.sort(key=lambda r: r.frame_index)
    return out


def segment_trajectory(ordered: Sequence[CanonicalRow]) -> List[List[CanonicalRow]]:
    """Split one ordered trajectory into non-bridged segments.

    A segment breaks on an explicit breaker row and on a missing frame index.
    Neither is ever bridged.
    """
    segments, cur, prev = [], [], None
    for r in ordered:
        if r.breaker:
            if cur:
                segments.append(cur)
            cur, prev = [], None
            continue
        if prev is not None and r.frame_index != prev + 1:
            if cur:
                segments.append(cur)
            cur = []
        cur.append(r)
        prev = r.frame_index
    if cur:
        segments.append(cur)
    return segments


# -------------------------------------------------------------------- Gate 1R
def classify_gate_1r(segment: Sequence[CanonicalRow]) -> Dict[int, str]:
    """Classify every target frame of one segment into the four frozen classes.

    eligible : an anchor exists strictly before AND strictly after the target
    leading  : anchors exist only after  the target
    trailing : anchors exist only before the target
    no_anchor: the segment contains no anchor at all
    """
    anchor_t = sorted(r.frame_index for r in segment if r.anchor)
    out = {}
    for r in segment:
        if not r.target:
            continue
        if not anchor_t:
            out[r.frame_index] = "no_anchor"
            continue
        before = any(a < r.frame_index for a in anchor_t)
        after = any(a > r.frame_index for a in anchor_t)
        if before and after:
            out[r.frame_index] = "eligible"
        elif after:
            out[r.frame_index] = "leading"
        elif before:
            out[r.frame_index] = "trailing"
        else:                                    # pragma: no cover - impossible
            raise ProtocolViolation(
                "target at frame %d has an anchor neither before nor after it, "
                "which would require an anchor at the same frame" % r.frame_index)
    return out


def assert_exact_partition(counts: Dict[str, int], n_scoreable: int) -> None:
    """The four Gate 1R classes must tile the scoreable targets exactly."""
    missing = set(GATE_1R_CLASSES) - set(counts)
    extra = set(counts) - set(GATE_1R_CLASSES)
    if extra:
        raise ProtocolViolation("unexpected Gate 1R class(es): %s" % sorted(extra))
    total = sum(counts.get(c, 0) for c in GATE_1R_CLASSES)
    if total != n_scoreable:
        raise ProtocolViolation(
            "Gate 1R classes do not partition the scoreable targets: "
            "%d classified vs %d scoreable" % (total, n_scoreable))
    if missing and n_scoreable:
        # absent classes are legitimate; they are reported as zero, never dropped
        for c in missing:
            counts[c] = 0


# --------------------------------------------------------------- natural runs
def natural_runs(segment: Sequence[CanonicalRow]) -> List[List[CanonicalRow]]:
    """Maximal consecutive runs of target frames inside one non-bridged segment."""
    runs, cur, prev = [], [], None
    for r in segment:
        if r.target and (prev is None or r.frame_index == prev + 1):
            cur.append(r)
        elif r.target:
            if cur:
                runs.append(cur)
            cur = [r]
        else:
            if cur:
                runs.append(cur)
            cur = []
        prev = r.frame_index
    if cur:
        runs.append(cur)
    return runs


def on_grid(run: Sequence[CanonicalRow]) -> bool:
    """A run is admissible only when its EXACT natural length is on the grid."""
    return len(run) in GAP_GRID


# ------------------------------------------------------------------- payloads
def build_cases(segment: Sequence[CanonicalRow]) -> List[dict]:
    """Frozen-grid, Gate-1R-eligible cases of one segment.

    The returned payload deliberately carries ``obs_t``/``obs_cx``/``obs_cy``
    and ``tgt_t`` only. Target centres and box sizes stay in ``eval_only`` and
    are never handed to a reconstruction operator.
    """
    cls = classify_gate_1r(segment)
    anchors = [r for r in segment if r.anchor]
    obs_t = [r.frame_index for r in anchors]
    obs_cx = [r.center_x for r in anchors]
    obs_cy = [r.center_y for r in anchors]
    cases = []
    for run in natural_runs(segment):
        if not on_grid(run):
            continue
        if any(cls.get(r.frame_index) != "eligible" for r in run):
            continue
        head = run[0]
        cases.append({
            "key": (head.population, head.sequence_id, head.track_id,
                    head.frame_index, len(run)),
            "population": head.population,
            "sequence_id": head.sequence_id,
            "category": head.category,
            "gap_length": len(run),
            "obs_t": list(obs_t),
            "obs_cx": list(obs_cx),
            "obs_cy": list(obs_cy),
            "tgt_t": [r.frame_index for r in run],
            "eval_only": {
                "tgt_cx": [r.center_x for r in run],
                "tgt_cy": [r.center_y for r in run],
                "diagonal": [r.normalization_diagonal for r in run]},
        })
    return cases
