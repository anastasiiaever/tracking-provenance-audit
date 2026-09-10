"""Layers 1 and 2: population, continuity, the exact partition, natural runs.

Nothing in this module consults a reconstruction method, a prediction or an
error. Admission is decided from structure alone, which is what makes the
no-outcome-leakage property checkable.
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Sequence, Tuple

from .contracts import (APPLICABILITY_CLASSES, ApplicabilityContract,
                        AuditContractError, CanonicalObservation)


def select_population(observations: Iterable[CanonicalObservation]):
    """Layer 1. Only scoreable observations enter the audit population."""
    kept, dropped = [], 0
    for o in observations:
        if o.scoreable:
            kept.append(o)
        else:
            dropped += 1
    return kept, dropped


def group_trajectories(observations: Sequence[CanonicalObservation]):
    """Group by (population, sequence, trajectory), ordered by frame index."""
    out = {}
    for o in observations:
        out.setdefault((o.population_id, o.sequence_id, o.trajectory_id), []).append(o)
    for key, group in out.items():
        seen = set()
        for o in group:
            if o.frame_index in seen:
                raise AuditContractError(
                    "duplicate trajectory-frame key %r at frame %d; silent "
                    "deduplication is forbidden" % (key, o.frame_index))
            seen.add(o.frame_index)
        group.sort(key=lambda o: o.frame_index)
    return out


def segment(ordered: Sequence[CanonicalObservation],
            contract: ApplicabilityContract):
    """Split one ordered trajectory into non-bridged segments.

    A breaker always ends a segment. A missing frame ends one too when the
    contract says so. Breaker rows are not part of any segment, and nothing is
    ever bridged across them.
    """
    segments, cur, prev = [], [], None
    for o in ordered:
        if o.breaker:
            if cur:
                segments.append(cur)
            cur, prev = [], None
            continue
        if (contract.split_on_missing_frame and prev is not None
                and o.frame_index != prev + 1):
            if cur:
                segments.append(cur)
            cur = []
        cur.append(o)
        prev = o.frame_index
    if cur:
        segments.append(cur)
    return segments


def classify_segment(seg: Sequence[CanonicalObservation]) -> Dict[int, str]:
    """The exact four-class partition of one segment's targets.

    eligible  -- an anchor exists strictly before AND strictly after the target
    leading   -- anchors exist only after the target
    trailing  -- anchors exist only before the target
    no_anchor -- the segment holds no anchor at all
    """
    anchor_t = sorted(o.frame_index for o in seg if o.anchor)
    out = {}
    for o in seg:
        if not o.target:
            continue
        if not anchor_t:
            out[o.frame_index] = "no_anchor"
            continue
        before = any(a < o.frame_index for a in anchor_t)
        after = any(a > o.frame_index for a in anchor_t)
        if before and after:
            out[o.frame_index] = "eligible"
        elif after:
            out[o.frame_index] = "leading"
        elif before:
            out[o.frame_index] = "trailing"
        else:                                # pragma: no cover - impossible
            raise AuditContractError(
                "target at frame %d has an anchor neither before nor after it"
                % o.frame_index)
    return out


def assert_exact_partition(counts: Dict[str, int], n_scoreable_targets: int) -> None:
    """The four classes must tile the scoreable targets exactly."""
    extra = set(counts) - set(APPLICABILITY_CLASSES)
    if extra:
        raise AuditContractError(
            "unexpected applicability class(es): %s" % sorted(extra))
    total = sum(counts.get(c, 0) for c in APPLICABILITY_CLASSES)
    if total != n_scoreable_targets:
        raise AuditContractError(
            "applicability classes do not partition the scoreable targets: "
            "%d classified vs %d scoreable" % (total, n_scoreable_targets))
    for c in APPLICABILITY_CLASSES:
        counts.setdefault(c, 0)


def natural_runs(seg: Sequence[CanonicalObservation]):
    """Maximal consecutive runs of target frames inside one non-bridged segment."""
    runs, cur, prev = [], [], None
    for o in seg:
        if o.target and (prev is None or o.frame_index == prev + 1):
            cur.append(o)
        elif o.target:
            if cur:
                runs.append(cur)
            cur = [o]
        else:
            if cur:
                runs.append(cur)
            cur = []
        prev = o.frame_index
    if cur:
        runs.append(cur)
    return runs


def on_grid(run: Sequence[CanonicalObservation],
            contract: ApplicabilityContract) -> bool:
    """A run is admissible only when its EXACT natural length is on the grid.

    Runs are never split, truncated, merged or padded to make them fit.
    """
    return len(run) in contract.run_length_grid
