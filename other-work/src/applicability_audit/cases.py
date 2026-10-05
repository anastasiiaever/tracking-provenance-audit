"""Case construction and the deterministic case key.

The payload handed to a method carries anchor times, anchor values and target
times only. Target values and metric scales live in ``eval_only`` and are
unreachable from :class:`MethodInput`, which is what makes outcome leakage a
structural impossibility rather than a convention.
"""
from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

from .applicability import classify_segment, natural_runs, on_grid
from .contracts import ApplicabilityContract, AuditContractError, CanonicalObservation


class MethodInput(object):
    """Everything a method is allowed to see about a case."""

    __slots__ = ("key", "obs_t", "obs_v", "tgt_t")

    def __init__(self, key, obs_t, obs_v, tgt_t):
        self.key = key
        self.obs_t = tuple(obs_t)
        self.obs_v = tuple(obs_v)
        self.tgt_t = tuple(tgt_t)

    @property
    def n_anchors(self):
        return len(self.obs_t)

    @property
    def run_length(self):
        return len(self.tgt_t)


class AuditCase(object):
    """One admitted reconstruction case."""

    __slots__ = ("key", "population_id", "sequence_id", "trajectory_id",
                 "first_target_frame", "run_length", "stratum",
                 "obs_t", "obs_v", "tgt_t", "eval_only")

    def __init__(self, key, population_id, sequence_id, trajectory_id,
                 first_target_frame, run_length, stratum, obs_t, obs_v, tgt_t,
                 eval_only):
        self.key = key
        self.population_id = population_id
        self.sequence_id = sequence_id
        self.trajectory_id = trajectory_id
        self.first_target_frame = first_target_frame
        self.run_length = run_length
        self.stratum = stratum
        self.obs_t = list(obs_t)
        self.obs_v = list(obs_v)
        self.tgt_t = list(tgt_t)
        self.eval_only = eval_only

    def method_input(self) -> MethodInput:
        return MethodInput(self.key, self.obs_t, self.obs_v, self.tgt_t)

    def metadata(self) -> Dict[str, object]:
        return {"population_id": self.population_id,
                "sequence_id": self.sequence_id,
                "trajectory_id": self.trajectory_id,
                "first_target_frame": self.first_target_frame,
                "run_length": self.run_length,
                "stratum": self.stratum}


def build_cases(seg: Sequence[CanonicalObservation],
                contract: ApplicabilityContract) -> List[AuditCase]:
    """Admitted cases of one segment, on the exact-length grid only."""
    classes = classify_segment(seg)
    anchors = [o for o in seg if o.anchor]
    obs_t = [o.frame_index for o in anchors]
    obs_v = [o.value for o in anchors]
    cases = []
    for run in natural_runs(seg):
        if not on_grid(run, contract):
            continue
        if contract.require_all_targets_admitted and any(
                classes.get(o.frame_index) not in contract.admitted_classes
                for o in run):
            continue
        head = run[0]
        key = (head.population_id, head.sequence_id, head.trajectory_id,
               head.frame_index, len(run))
        cases.append(AuditCase(
            key=key, population_id=head.population_id,
            sequence_id=head.sequence_id, trajectory_id=head.trajectory_id,
            first_target_frame=head.frame_index, run_length=len(run),
            stratum=head.stratum, obs_t=obs_t, obs_v=obs_v,
            tgt_t=[o.frame_index for o in run],
            eval_only={"tgt_v": [o.value for o in run],
                       "metric_scale": [o.metric_scale for o in run]}))
    return cases


def assert_unique_keys(cases: Sequence[AuditCase]) -> None:
    seen = set()
    for c in cases:
        if c.key in seen:
            raise AuditContractError(
                "duplicate reconstruction case key %r at corpus level" % (c.key,))
        seen.add(c.key)
