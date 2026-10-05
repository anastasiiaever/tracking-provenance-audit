"""Explicit, inspectable configuration objects for the applicability audit.

Every scientific choice the audit makes is carried by one of these objects, so
that nothing is decided by a hidden global. The contracts are deliberately
dataset-agnostic: none of them knows what an occlusion, a visibility score or a
skeleton joint is.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Sequence, Tuple

APPLICABILITY_CLASSES = ("eligible", "leading", "trailing", "no_anchor")

FAILURE_MODES = (
    "population_scoreability",
    "applicability_admission",
    "method_support",
    "metric_validity",
    "common_support_mismatch",
    "aggregation_configuration",
    "post_admission_reconstruction",
)


class AuditContractError(RuntimeError):
    """Raised whenever an audit contract or invariant would be broken."""


class CanonicalObservation(object):
    """One already-interpreted observation of one trajectory at one frame.

    The semantic flags are supplied by a dataset adapter and are **never**
    inferred here. The core has no access to, and no opinion about, the raw
    annotation fields the adapter used to decide them.
    """

    __slots__ = ("trajectory_id", "frame_index", "value", "scoreable", "target",
                 "anchor", "breaker", "sequence_id", "population_id", "stratum",
                 "metric_scale")

    def __init__(self, trajectory_id, frame_index, value=None, scoreable=True,
                 target=False, anchor=False, breaker=False, sequence_id=None,
                 population_id=None, stratum=None, metric_scale=None):
        self.trajectory_id = trajectory_id
        self.frame_index = int(frame_index)
        self.value = None if value is None else tuple(float(v) for v in value)
        self.scoreable = bool(scoreable)
        self.target = bool(target)
        self.anchor = bool(anchor)
        self.breaker = bool(breaker)
        self.sequence_id = sequence_id if sequence_id is not None else trajectory_id
        self.population_id = population_id
        self.stratum = stratum
        self.metric_scale = None if metric_scale is None else float(metric_scale)
        roles = (self.target, self.anchor, self.breaker)
        if sum(1 for r in roles if r) != 1:
            raise AuditContractError(
                "observation %r at frame %d must be exactly one of "
                "target/anchor/breaker" % (trajectory_id, self.frame_index))

    def __repr__(self):                      # pragma: no cover - debugging aid
        role = "target" if self.target else ("anchor" if self.anchor else "breaker")
        return "<CanonicalObservation %s/%s@%d %s>" % (
            self.sequence_id, self.trajectory_id, self.frame_index, role)


class ApplicabilityContract(object):
    """Layer 2: how admission is decided, independently of any method.

    ``run_length_grid`` is the caller's frozen set of admissible natural-run
    lengths. ``split_on_missing_frame`` decides whether a hole in the frame
    sequence breaks continuity; nothing is ever bridged implicitly.
    """

    __slots__ = ("run_length_grid", "split_on_missing_frame", "admitted_classes",
                 "require_all_targets_admitted")

    def __init__(self, run_length_grid=(), split_on_missing_frame=True,
                 admitted_classes=("eligible",),
                 require_all_targets_admitted=True):
        self.run_length_grid = tuple(int(g) for g in run_length_grid)
        self.split_on_missing_frame = bool(split_on_missing_frame)
        self.admitted_classes = tuple(admitted_classes)
        self.require_all_targets_admitted = bool(require_all_targets_admitted)
        for c in self.admitted_classes:
            if c not in APPLICABILITY_CLASSES:
                raise AuditContractError("unknown applicability class %r" % (c,))

    def describe(self):
        return {"run_length_grid": list(self.run_length_grid),
                "split_on_missing_frame": self.split_on_missing_frame,
                "admitted_classes": list(self.admitted_classes),
                "require_all_targets_admitted": self.require_all_targets_admitted,
                "applicability_classes": list(APPLICABILITY_CLASSES)}


class MethodContract(object):
    """Layer 3: one reconstruction method.

    ``supports`` and ``reconstruct`` receive a :class:`MethodInput` view that
    carries anchor times, anchor values and target times only. The support
    decision and the reconstruction output are separate concepts: a method that
    does not support a case simply never runs on it, and nothing is substituted.
    """

    __slots__ = ("method_id", "supports", "reconstruct", "description")

    def __init__(self, method_id, supports, reconstruct, description=""):
        self.method_id = str(method_id)
        if not callable(supports) or not callable(reconstruct):
            raise AuditContractError(
                "method %r needs callable supports() and reconstruct()" % (method_id,))
        self.supports = supports
        self.reconstruct = reconstruct
        self.description = str(description)

    def describe(self):
        return {"method_id": self.method_id, "description": self.description}


class AggregationLevel(object):
    """One rung of an aggregation ladder.

    ``group_keys`` are case metadata field names. An empty tuple means "one
    group holding everything", which is how a headline is produced.
    """

    __slots__ = ("name", "group_keys", "weighting", "unavailable")

    def __init__(self, name, group_keys=(), weighting="equal",
                 unavailable="skip"):
        self.name = str(name)
        self.group_keys = tuple(str(k) for k in group_keys)
        if weighting != "equal":
            raise AuditContractError(
                "only explicit equal weighting is implemented; %r would be a "
                "hidden weighting rule" % (weighting,))
        self.weighting = weighting
        if unavailable not in ("skip", "propagate"):
            raise AuditContractError("unknown unavailable policy %r" % (unavailable,))
        self.unavailable = unavailable

    def describe(self):
        return {"name": self.name, "group_keys": list(self.group_keys),
                "weighting": self.weighting, "unavailable": self.unavailable}


class AggregationContract(object):
    """Layer 4 input: the complete, declared aggregation ladder.

    The ladder is always serialized with the result, so a reader never has to
    guess what was averaged over what, or with which weights.
    """

    __slots__ = ("levels", "metric_fields", "reported_grid")

    def __init__(self, levels, metric_fields=("normalized", "raw"),
                 reported_grid=()):
        self.levels = tuple(levels)
        if not self.levels:
            raise AuditContractError("an aggregation ladder needs at least one level")
        if self.levels[-1].group_keys:
            raise AuditContractError(
                "the final aggregation level must group everything into one "
                "unit; got group_keys=%r" % (self.levels[-1].group_keys,))
        self.metric_fields = tuple(str(f) for f in metric_fields)
        self.reported_grid = tuple(int(g) for g in reported_grid)

    def describe(self):
        return {"levels": [lv.describe() for lv in self.levels],
                "metric_fields": list(self.metric_fields),
                "reported_grid": list(self.reported_grid),
                "first_rung": "target error -> case mean"}


class StabilityContract(object):
    """Optional resampling. Never called a confidence interval by default."""

    __slots__ = ("enabled", "cluster_key", "replicates", "seed", "paired",
                 "interpretation", "is_confidence_interval")

    def __init__(self, enabled=False, cluster_key="sequence_id", replicates=0,
                 seed=0, paired=True,
                 interpretation="cluster-resampling stability over the observed subset",
                 is_confidence_interval=False):
        self.enabled = bool(enabled)
        self.cluster_key = str(cluster_key)
        self.replicates = int(replicates)
        self.seed = int(seed)
        self.paired = bool(paired)
        self.interpretation = str(interpretation)
        self.is_confidence_interval = bool(is_confidence_interval)
        if self.enabled and self.replicates <= 0:
            raise AuditContractError("enabled stability needs a positive replicate count")

    def describe(self):
        return {"enabled": self.enabled, "cluster_key": self.cluster_key,
                "replicates": self.replicates, "seed": self.seed,
                "paired": self.paired, "interpretation": self.interpretation,
                "is_confidence_interval": self.is_confidence_interval}
