"""MOTChallenge post-processing adapter for the generic applicability audit.

Consumes immutable third-party tracker output and routes the audit *decision*
through :mod:`applicability_audit`. It computes no tracking metric: TrackEval
remains the authoritative metric implementation.

Layer mapping (see protocols/mot_audit/ADAPTER_SPEC.md):
  synthesized row -> target;  raw row -> anchor
  layer A  : the core's own segment()/classify_segment() -- Gate 1R
  layer B_m: the post-processor's temporal-support contract (n_min, n_dti)
  layer C  : the study-specific semantic-validity subcheck (STV)
  layer D  : the core's intersection and certificate
"""
import hashlib
from collections import defaultdict
from typing import Dict, Mapping, Sequence, Tuple

from ..applicability import classify_segment, segment
from ..aggregation import AggregationContract, AggregationLevel
from ..audit import audit_precomputed_results
from ..contracts import ApplicabilityContract, AuditContractError, CanonicalObservation
from ..serialization import unavailable
from ..synthesis import diff_rows, row_subset_diagnostic

STV_CLASSES = ("ANCHOR_UNMATCHED", "ANCHOR_ID_MISMATCH",
               "TARGET_REFERENCE_ABSENT", "SEMANTICALLY_VALID")
IOU_GATE = 0.5
PEDESTRIAN = 1

__all__ = ["read_mot_txt", "read_gt", "sha256", "anchor_assignment",
           "stv_classify", "audit_dti_sequence", "audit_non_additive_transform",
           "STV_CLASSES"]


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def read_mot_txt(path: str, require_frame_sorted: bool = True
                 ) -> Dict[Tuple[int, int], Tuple[float, ...]]:
    """MOTChallenge rows keyed by (frame, track id). Hard-fails on any violation.

    ``require_frame_sorted`` is a precondition of the DTI family only: the
    published ``dti()`` never sorts and therefore relies on file order being
    temporal order. Post-processors that emit id-major order (GSI does) are read
    with the check disabled; it is not relaxed for DTI.
    """
    rows, order = {}, []
    with open(path) as f:
        for ln, line in enumerate(f, 1):
            if not line.strip():
                continue
            p = line.strip().split(",")
            if len(p) < 6:
                raise AuditContractError("%s:%d has %d columns" % (path, ln, len(p)))
            fr, tid = int(float(p[0])), int(float(p[1]))
            box = tuple(round(float(x), 3) for x in p[2:6])
            if box[2] <= 0 or box[3] <= 0:
                raise AuditContractError("%s:%d non-positive w/h" % (path, ln))
            if (fr, tid) in rows:
                raise AuditContractError(
                    "%s:%d duplicate (frame,id) key %r" % (path, ln, (fr, tid)))
            rows[(fr, tid)] = box
            order.append(fr)
    if not rows:
        raise AuditContractError("%s is empty" % path)
    if require_frame_sorted and any(b < a for a, b in zip(order, order[1:])):
        raise AuditContractError("%s: frames are not ascending" % path)
    return rows


def read_gt(path: str):
    """Preprocessing-surviving pedestrian ground truth."""
    per_frame, per_id = defaultdict(list), defaultdict(set)
    with open(path) as f:
        for line in f:
            if not line.strip():
                continue
            p = line.strip().split(",")
            if int(float(p[6])) == 0 or int(float(p[7])) != PEDESTRIAN:
                continue
            fr, gid = int(float(p[0])), int(float(p[1]))
            per_frame[fr].append((gid, tuple(float(x) for x in p[2:6])))
            per_id[gid].add(fr)
    return per_frame, per_id


def _iou(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    x1, y1 = max(ax, bx), max(ay, by)
    x2, y2 = min(ax + aw, bx + bw), min(ay + ah, by + bh)
    iw, ih = max(0.0, x2 - x1), max(0.0, y2 - y1)
    inter = iw * ih
    u = aw * ah + bw * bh - inter
    return inter / u if u > 0 else 0.0


def anchor_assignment(raw: Mapping, per_frame: Mapping) -> Dict[Tuple[int, int], int]:
    """Frozen once on the raw output: per-frame one-to-one IoU matching, gate 0.5."""
    from scipy.optimize import linear_sum_assignment
    import numpy as np
    by_frame = defaultdict(list)
    for (fr, tid), box in raw.items():
        by_frame[fr].append((tid, box))
    out = {}
    for fr, dets in by_frame.items():
        gts = per_frame.get(fr, [])
        if not gts:
            continue
        C = np.zeros((len(dets), len(gts)))
        for i, (_, db) in enumerate(dets):
            for j, (_, gb) in enumerate(gts):
                v = _iou(db, gb)
                C[i, j] = v if v >= IOU_GATE - np.finfo("float").eps else 0.0
        ri, ci = linear_sum_assignment(-C)
        for i, j in zip(ri, ci):
            if C[i, j] > np.finfo("float").eps:
                out[(fr, dets[i][0])] = gts[j][0]
    return out


def stv_classify(synth_keys, raw, assign, per_id):
    """The study-specific semantic-validity subcheck, in priority order."""
    frames_by_tid = defaultdict(list)
    for (fr, tid) in raw:
        frames_by_tid[tid].append(fr)
    for t in frames_by_tid:
        frames_by_tid[t].sort()
    cls, anchors = {}, {}
    for (t, tid) in synth_keys:
        fs = frames_by_tid[tid]
        lo = [x for x in fs if x < t]
        hi = [x for x in fs if x > t]
        if not lo or not hi:
            raise AuditContractError(
                "synthesized row (%d,%d) is not interior" % (t, tid))
        L, R = max(lo), min(hi)
        anchors[(t, tid)] = (L, R)
        a, b = assign.get((L, tid)), assign.get((R, tid))
        if a is None or b is None:
            cls[(t, tid)] = "ANCHOR_UNMATCHED"
        elif a != b:
            cls[(t, tid)] = "ANCHOR_ID_MISMATCH"
        elif t not in per_id.get(a, ()):
            cls[(t, tid)] = "TARGET_REFERENCE_ABSENT"
        else:
            cls[(t, tid)] = "SEMANTICALLY_VALID"
    if set(cls) != set(synth_keys):
        raise AuditContractError("STV partition is not total")
    return cls, anchors


def _observations(seq, raw, synth_keys):
    """Canonical observations: raw rows are anchors, synthesized rows are targets."""
    synth = set(synth_keys)
    by_tid = defaultdict(list)
    for (fr, tid) in sorted(set(raw) | synth):
        by_tid[tid].append(fr)
    obs = []
    for tid, frames in by_tid.items():
        for fr in frames:
            is_t = (fr, tid) in synth
            obs.append(CanonicalObservation(
                trajectory_id="%s/%d" % (seq, tid), frame_index=fr,
                value=(raw.get((fr, tid)) or (0.0, 0.0, 1.0, 1.0))[:2],
                scoreable=True, target=is_t, anchor=not is_t,
                sequence_id=seq, population_id="MOT17-val_half",
                metric_scale=1.0))
    return obs


def audit_dti_sequence(seq, r0_path, r2_path, gt_path, n_min, n_dti,
                       method_id="published_DTI"):
    """Audit one sequence's row-additive post-processing through the generic core."""
    raw, post = read_mot_txt(r0_path), read_mot_txt(r2_path)
    per_frame, per_id = read_gt(gt_path)

    diff = diff_rows(raw, post)                      # generic core
    status, reason = row_subset_diagnostic(diff)     # generic core
    if diff["n_modified"] or diff["n_dropped"]:
        raise AuditContractError(
            "%s: post-processing is not row-additive (%d modified, %d dropped); "
            "use audit_non_additive_transform" % (seq, diff["n_modified"], diff["n_dropped"]))
    synth = list(diff["added"])

    # layer A -- the core's own Gate 1R partition
    contract = ApplicabilityContract(run_length_grid=(), split_on_missing_frame=True,
                                     admitted_classes=("eligible",))
    obs = _observations(seq, raw, synth)
    by_traj = defaultdict(list)
    for o in obs:
        by_traj[o.trajectory_id].append(o)
    app_counts = {c: 0 for c in ("eligible", "leading", "trailing", "no_anchor")}
    a_class = {}
    for tid, os_ in by_traj.items():
        for sg in segment(sorted(os_, key=lambda o: o.frame_index), contract):
            for fr, c in classify_segment(sg).items():
                app_counts[c] += 1
                a_class[(fr, int(tid.split("/")[1]))] = c

    # layer C -- study-specific semantic-validity subcheck
    assign = anchor_assignment(raw, per_frame)
    cls, anchors = stv_classify(synth, raw, assign, per_id)

    # layer B_m -- the post-processor's own temporal-support contract
    frames_by_tid = defaultdict(list)
    for (fr, tid) in raw:
        frames_by_tid[tid].append(fr)
    for t in frames_by_tid:
        frames_by_tid[t].sort()
    supported = set()
    for k in synth:
        t, tid = k
        L, R = anchors[k]
        if 1 < R - L < n_dti and len(frames_by_tid[tid]) > n_min:
            supported.add(k)

    cases = [{"case_id": "%s|%d|%d" % (seq, k[1], k[0]), "population_id": "MOT17-val_half",
              "sequence_id": seq, "trajectory_id": str(k[1]),
              "first_target_frame": k[0], "run_length": 1, "stratum": cls[k]}
             for k in synth]
    method_results = {method_id: {"%s|%d|%d" % (seq, k[1], k[0]): {} for k in supported}}
    metric_valid = {"%s|%d|%d" % (seq, k[1], k[0]): (cls[k] == "SEMANTICALLY_VALID")
                    for k in synth}
    aggregation = AggregationContract(levels=(AggregationLevel("headline", ()),),
                                      metric_fields=())
    result = audit_precomputed_results(          # generic core makes the decision
        cases=cases, method_results=method_results, aggregation=aggregation,
        applicability={"counts": app_counts, "scoreable_targets": sum(app_counts.values()),
                       "admitted_classes": ("eligible",)},
        metric_valid=metric_valid, strata=False,
        provenance={"sequence": seq, "r0_sha256": sha256(r0_path),
                    "r2_sha256": sha256(r2_path), "gt_sha256": sha256(gt_path),
                    "n_min": n_min, "n_dti": n_dti,
                    "row_subset_diagnostic": status,
                    "row_subset_reason": (reason if reason is not None else
                                          unavailable("row-subset diagnostic is "
                                                      "defined; no refusal applies"))})
    counts = {c: 0 for c in STV_CLASSES}
    for v in cls.values():
        counts[v] += 1
    return {"sequence": seq, "synthesized": synth, "stv_class": cls,
            "stv_counts": counts, "applicability_counts": app_counts,
            "row_subset_diagnostic": status, "audit": result}


def audit_non_additive_transform(seq, s0_path, s2_path):
    """Certify that a transformation is not row-additive and refuse the subset state."""
    base = read_mot_txt(s0_path, require_frame_sorted=False)
    post = read_mot_txt(s2_path, require_frame_sorted=False)
    diff = diff_rows(base, post)
    status, reason = row_subset_diagnostic(diff)
    return {"sequence": seq, "diff": diff,
            "row_subset_diagnostic": status, "reason": reason,
            "s0_sha256": sha256(s0_path), "s2_sha256": sha256(s2_path)}
