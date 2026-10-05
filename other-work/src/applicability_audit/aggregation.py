"""Layer 4: the declared aggregation ladder, and optional stability.

No weighting is ever implicit. Each rung names its grouping keys, its unit and
its weighting rule, and the effective contract is serialized with the result so
a reader never has to guess what was averaged over what.
"""
from __future__ import annotations

from typing import Dict, List, Sequence

from .contracts import AggregationContract, AggregationLevel, AuditContractError
from .serialization import key_repr, unavailable, value_or_unavailable


def _mean(values):
    vals = [v for v in values if v is not None]
    return sum(vals) / float(len(vals)) if vals else None


def case_mean(errors: Sequence[float]):
    """The first rung, fixed for every ladder: target errors -> one case value."""
    return _mean(errors)


def run_ladder(records: Sequence[Dict[str, object]],
               contract: AggregationContract, field: str) -> Dict[str, object]:
    """Execute the declared ladder over per-case records.

    Each record needs ``value`` (the case mean) plus the metadata fields named
    by the levels. Every rung collapses its input units into groups and takes an
    equal-weight mean, so the unit of one rung is the group of the previous one.
    """
    units = []
    for rec in records:
        if rec.get("value") is None:
            continue
        units.append({"value": rec["value"], "meta": rec["meta"], "n_cases": 1})

    levels_out = []
    for level in contract.levels:
        groups = {}
        for u in units:
            gk = tuple(u["meta"].get(k) for k in level.group_keys)
            groups.setdefault(gk, []).append(u)
        collapsed = []
        table = {}
        for gk, members in groups.items():
            v = _mean([m["value"] for m in members])
            table[key_repr(gk)] = value_or_unavailable(
                v, "no valued unit in this group")
            if v is None and level.unavailable == "skip":
                continue
            meta = dict(members[0]["meta"])
            collapsed.append({"value": v, "meta": meta,
                              "n_cases": sum(m["n_cases"] for m in members)})
        levels_out.append({"name": level.name,
                           "group_keys": list(level.group_keys),
                           "weighting": level.weighting,
                           "unavailable": level.unavailable,
                           "n_units_in": len(units),
                           "n_groups_out": len(groups),
                           "groups": table})
        units = collapsed

    headline = units[0]["value"] if len(units) == 1 else _mean(
        [u["value"] for u in units])
    return {"field": field,
            "headline": value_or_unavailable(headline, "no aggregable case"),
            "levels": levels_out}


def contributing_units_per_grid_length(records: Sequence[Dict[str, object]],
                                       contract: AggregationContract,
                                       unit_key: str = "sequence_id"
                                       ) -> Dict[str, int]:
    """How many units support each reported run length, including empty ones.

    Every declared length is reported, so a length with no support is visible
    rather than silently missing.
    """
    seen = {int(g): set() for g in contract.reported_grid}
    for rec in records:
        if rec.get("value") is None:
            continue
        g = rec["meta"].get("run_length")
        if g in seen:
            seen[g].add(rec["meta"].get(unit_key))
    return {str(g): len(seen[g]) for g in sorted(seen)}


def paired_cluster_stability(clusters: Sequence[str],
                             per_method_cluster_values: Dict[str, Dict[str, float]],
                             stability) -> Dict[str, object]:
    """Optional resampling over whole clusters, paired across methods.

    The same resampled cluster multiset is reused for every method, and the
    output carries its own interpretation label. It is not called a confidence
    interval unless the contract explicitly says it is one.
    """
    import numpy as np

    clusters = list(clusters)
    if not clusters:
        return unavailable("no cluster carries a value for every compared method")
    rng = np.random.default_rng(stability.seed)
    draws = rng.integers(0, len(clusters), size=(stability.replicates, len(clusters)))
    out = {}
    for name, vals in sorted(per_method_cluster_values.items()):
        missing = [c for c in clusters if c not in vals]
        if missing:
            raise AuditContractError(
                "paired stability cluster(s) %r lack a value for %s; no "
                "imputation is permitted" % (missing, name))
        v = np.array([vals[c] for c in clusters], dtype=float)
        means = v[draws].mean(axis=1)
        out[name] = {"lo": float(np.percentile(means, 2.5)),
                     "hi": float(np.percentile(means, 97.5)),
                     "replicates": int(stability.replicates),
                     "seed": int(stability.seed),
                     "cluster_key": stability.cluster_key,
                     "paired": stability.paired,
                     "interpretation": stability.interpretation,
                     "is_confidence_interval": stability.is_confidence_interval}
    return {"clusters": clusters, "contributing_clusters": len(clusters),
            "paired": stability.paired, "methods": out}


def frozen_trajectory_ladder(reported_grid) -> AggregationContract:
    """The trajectory ladder used by the frozen prospective experiment.

    target error -> case mean -> mean within (sequence, run length)
      -> equal-weight over represented run lengths within sequence
        -> equal-weight across contributing sequences
    """
    return AggregationContract(
        levels=(AggregationLevel("sequence_and_run_length",
                                 ("sequence_id", "run_length")),
                AggregationLevel("sequence", ("sequence_id",)),
                AggregationLevel("headline", ())),
        metric_fields=("normalized", "raw"),
        reported_grid=reported_grid)


def simple_case_ladder() -> AggregationContract:
    """The minimal ladder: target error -> case mean -> equal-weight case mean."""
    return AggregationContract(levels=(AggregationLevel("headline", ()),),
                               metric_fields=("normalized", "raw"),
                               reported_grid=())
