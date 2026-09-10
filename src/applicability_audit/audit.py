"""The audit orchestrator: four layers, executed and reported separately.

The pipeline decides admission from structure, then method support, then metric
validity, then --- and only then --- ranking on identical common support. The
order is the point: it is what lets an audit say "every method supported every
admitted case, and almost nothing was admitted".
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Sequence

import hashlib

from . import aggregation as agg
from .certificate import build_certificate, render_audit_report, render_support_matrix
from .diagnostics import coverage_diagnostics, pairwise_support_geometry
from .applicability import (assert_exact_partition, classify_segment,
                            group_trajectories, natural_runs, on_grid,
                            segment, select_population)
from .cases import AuditCase, assert_unique_keys, build_cases
from .contracts import (APPLICABILITY_CLASSES, AggregationContract,
                        ApplicabilityContract, AuditContractError,
                        CanonicalObservation, FAILURE_MODES, MethodContract,
                        StabilityContract)
from .serialization import (SCHEMA_VERSION, assert_no_raw_none, is_unavailable,
                            key_repr, unavailable, value_or_unavailable)
from .support import (assert_identical_common_support, method_specific_support,
                      metric_valid, reconstruct_case, support_retention,
                      support_sets, target_errors, UNDEFINED)


class AuditResult(dict):
    """The structured audit payload, with its certificate attached."""

    def certificate(self):
        return AuditCertificate(self["certificate"])

    def render_report(self) -> str:
        return render_audit_report(self["certificate"])

    def render_support_matrix(self) -> str:
        return render_support_matrix(self["diagnostics"]["support_geometry"])


class AuditCertificate(dict):
    """A deterministic structural verdict; it carries no scientific claim."""

    def render(self) -> str:
        return render_audit_report(self)


def configuration_fingerprint(applicability_contract, methods, aggregation,
                              stability) -> str:
    """A deterministic digest of the effective contracts. No clock, no paths."""
    from .serialization import dumps
    payload = {"applicability": applicability_contract.describe(),
               "methods": sorted(m.method_id for m in methods),
               "aggregation": aggregation.describe(),
               "stability": stability.describe(),
               "schema_version": SCHEMA_VERSION}
    return hashlib.sha256(dumps(payload).encode("utf-8")).hexdigest()


def _sort_key(key):
    return tuple(key_repr(k) for k in key) if isinstance(key, tuple) else key_repr(key)


def _collect(observations, contract):
    """Layers 1--2 plus case construction, in one deterministic pass."""
    population, dropped = select_population(observations)
    counts = {c: 0 for c in APPLICABILITY_CLASSES}
    per_stratum = {}
    scoreable_targets = 0
    run_counts = {g: 0 for g in contract.run_length_grid}
    off_grid = 0
    total_runs = 0
    n_segments = 0
    cases: List[AuditCase] = []

    grouped = group_trajectories(population)
    for tkey in sorted(grouped, key=_sort_key):
        for seg in segment(grouped[tkey], contract):
            n_segments += 1
            classes = classify_segment(seg)
            for o in seg:
                if not o.target:
                    continue
                cls = classes[o.frame_index]
                counts[cls] += 1
                scoreable_targets += 1
                st = per_stratum.setdefault(
                    o.stratum, {c: 0 for c in APPLICABILITY_CLASSES})
                st[cls] += 1
            for run in natural_runs(seg):
                total_runs += 1
                if on_grid(run, contract):
                    run_counts[len(run)] += 1
                else:
                    off_grid += 1
            cases.extend(build_cases(seg, contract))

    assert_exact_partition(counts, scoreable_targets)
    assert_unique_keys(cases)
    return {"population_observations": len(population),
            "non_scoreable_dropped": dropped,
            "trajectories": len(grouped), "segments": n_segments,
            "scoreable_targets": scoreable_targets,
            "counts": counts, "per_stratum": per_stratum,
            "run_counts": run_counts, "off_grid": off_grid,
            "total_runs": total_runs, "cases": cases}


def _evaluate(cases, methods, sets):
    """Run every method on every case it supports; never substitute a result."""
    evaluated = {m.method_id: {} for m in methods}
    for case in cases:
        for m in methods:
            if case.key not in sets["B"][m.method_id]:
                evaluated[m.method_id][case.key] = {"supported": False}
                continue
            pred = reconstruct_case(case, m)
            if pred is UNDEFINED:
                raise AuditContractError(
                    "method %r was admitted to its own support set for case %r "
                    "but produced no result; the support predicate and the "
                    "method disagree" % (m.method_id, case.key))
            entry = {"supported": True}
            if metric_valid(case):
                entry["errors"] = target_errors(case, pred)
            evaluated[m.method_id][case.key] = entry
    return evaluated


def _records(cases_by_key, evaluated_m, keys, field):
    recs = []
    for key in sorted(keys, key=_sort_key):
        entry = evaluated_m[key]
        if not entry.get("supported") or "errors" not in entry:
            continue
        recs.append({"value": agg.case_mean(entry["errors"][field]),
                     "meta": cases_by_key[key].metadata()})
    return recs


def _estimates(cases_by_key, evaluated_m, keys, contract):
    out = {"n_cases": len(keys)}
    for field in contract.metric_fields:
        recs = _records(cases_by_key, evaluated_m, keys, field)
        out[field] = agg.run_ladder(recs, contract, field)
    return out


def run_applicability_audit(observations: Iterable[CanonicalObservation],
                            methods: Sequence[MethodContract],
                            applicability_contract: ApplicabilityContract,
                            aggregation: AggregationContract,
                            strata: bool = True,
                            stability: Optional[StabilityContract] = None,
                            provenance: Optional[Dict[str, object]] = None
                            ) -> Dict[str, object]:
    """Run the complete four-layer audit and return one structured result."""
    methods = list(methods)
    if not methods:
        raise AuditContractError("at least one method contract is required")
    if len({m.method_id for m in methods}) != len(methods):
        raise AuditContractError("method identifiers must be unique")
    stability = stability or StabilityContract(enabled=False)

    corpus = _collect(observations, applicability_contract)
    cases = corpus["cases"]
    cases_by_key = {c.key: c for c in cases}
    sets = support_sets(cases, methods)
    assert_identical_common_support(sets, methods)
    evaluated = _evaluate(cases, methods, sets)

    S = corpus["scoreable_targets"]
    common = {m.method_id: _estimates(cases_by_key, evaluated[m.method_id],
                                      sets["D"], aggregation) for m in methods}
    own_sets = {m.method_id: method_specific_support(sets, m.method_id)
                for m in methods}
    specific = {m.method_id: _estimates(cases_by_key, evaluated[m.method_id],
                                        own_sets[m.method_id], aggregation)
                for m in methods}

    shift = {}
    for m in methods:
        entry = {"supports_identical": set(own_sets[m.method_id]) == set(sets["D"])}
        for field in aggregation.metric_fields:
            a = common[m.method_id][field]["headline"]
            b = specific[m.method_id][field]["headline"]
            entry[field] = (unavailable("one side of the comparison is undefined")
                            if (is_unavailable(a) or is_unavailable(b))
                            else a - b)
        shift[m.method_id] = entry

    result = {
        "schema_version": SCHEMA_VERSION,
        "population": {
            "observations_in_population": corpus["population_observations"],
            "non_scoreable_dropped": corpus["non_scoreable_dropped"],
            "trajectories": corpus["trajectories"],
            "segments": corpus["segments"],
            "scoreable_targets": S},
        "applicability": {
            "counts": dict(corpus["counts"]),
            "fractions": {c: (corpus["counts"][c] / float(S) if S else
                              unavailable("no scoreable target"))
                          for c in APPLICABILITY_CLASSES},
            "exact_partition_verified": True,
            "admitted_classes": list(applicability_contract.admitted_classes)},
        "natural_runs": {
            "total": corpus["total_runs"],
            "by_grid_length": {str(g): corpus["run_counts"][g]
                               for g in sorted(corpus["run_counts"])},
            "off_grid": corpus["off_grid"],
            "grid": list(applicability_contract.run_length_grid)},
        "cases": {"admitted_A": len(sets["A"]), "unique_keys_verified": True},
        "metric_validity": {
            "C": len(sets["C"]),
            "removed_from_A": len(set(sets["A"]) - sets["C"]),
            "redundant": len(set(sets["A"]) - sets["C"]) == 0},
        "method_support": {m.method_id: len(sets["B"][m.method_id]) for m in methods},
        "common_support": {
            "D": len(sets["D"]),
            "case_keys_identical_across_methods": True,
            "identical_across_methods": len({len(sets["B"][m.method_id])
                                             for m in methods}) == 1},
        "support_retention": support_retention(sets),
        "method_specific_estimates": specific,
        "common_support_estimates": common,
        "support_shift": shift,
        "aggregation": {
            "contract": aggregation.describe(),
            "contributing_units_per_reported_grid_length":
                agg.contributing_units_per_grid_length(
                    _records(cases_by_key, evaluated[methods[0].method_id],
                             sets["D"], aggregation.metric_fields[0]),
                    aggregation)},
        "failure_modes": {"taxonomy": list(FAILURE_MODES)},
        "provenance": {
            "applicability_contract": applicability_contract.describe(),
            "methods": [m.describe() for m in methods],
            "aggregation_contract": aggregation.describe(),
            "stability_contract": stability.describe(),
            "schema_version": SCHEMA_VERSION,
            "supplied": dict(provenance) if provenance else {}},
        "validation": {
            "exact_applicability_partition": True,
            "unique_case_keys": True,
            "identical_common_support_keys": True,
            "all_methods_represented": sorted(m.method_id for m in methods),
            "no_silent_case_drop": True},
    }

    result["strata"] = (_strata(corpus, cases_by_key, evaluated, sets,
                                aggregation, methods)
                        if strata else unavailable("stratification disabled"))
    result["stability"] = _stability(cases_by_key, evaluated, sets, aggregation,
                                     methods, stability)
    result["case_table"] = _case_table(cases, sets, methods)
    result["diagnostics"] = _diagnostics(result, sets, methods, corpus,
                                         applicability_contract)
    result["provenance"]["mode"] = "executable"
    result["provenance"]["configuration_fingerprint"] = configuration_fingerprint(
        applicability_contract, methods, aggregation, stability)
    result["certificate"] = build_certificate(result)
    assert_no_raw_none(result)
    return AuditResult(result)


def _diagnostics(result, sets, methods, corpus, applicability_contract):
    """Support geometry and coverage, reported as two separate questions."""
    support = {m.method_id: set(sets["B"][m.method_id]) for m in methods}
    applicable = sum(corpus["counts"][c]
                     for c in applicability_contract.admitted_classes)
    conditional = {m.method_id: len(method_specific_support(sets, m.method_id))
                   for m in methods}
    return {"support_geometry": pairwise_support_geometry(support),
            "coverage": coverage_diagnostics(
                scoreable_targets=corpus["scoreable_targets"],
                applicable_targets=applicable,
                admitted_A=len(sets["A"]),
                per_method_conditional=conditional,
                common_D=len(sets["D"]))}


def _strata(corpus, cases_by_key, evaluated, sets, aggregation, methods):
    """Per-stratum applicability, and reconstruction where support exists."""
    names = sorted(corpus["per_stratum"], key=key_repr)
    if not names:
        return unavailable("no stratum metadata supplied")
    out = {}
    for name in names:
        c = corpus["per_stratum"][name]
        n = sum(c.values())
        entry = {"scoreable_targets": n,
                 "counts": dict(c),
                 "fractions": {k: c[k] / float(n) for k in c} if n else
                 unavailable("no scoreable target in this stratum")}
        keys = [k for k in sets["D"] if cases_by_key[k].stratum == name]
        entry["reconstruction"] = (
            {m.method_id: _estimates(cases_by_key, evaluated[m.method_id],
                                     keys, aggregation) for m in methods}
            if keys else unavailable("no common-support case in this stratum"))
        out[key_repr(name)] = entry
    return out


def _stability(cases_by_key, evaluated, sets, aggregation, methods, stability):
    if not stability.enabled:
        return {"enabled": False,
                "results": unavailable("stability analysis is not enabled"),
                "contract": stability.describe()}
    field = aggregation.metric_fields[0]
    per_method = {}
    for m in methods:
        recs = _records(cases_by_key, evaluated[m.method_id], sets["D"], field)
        vals = {}
        for r in recs:
            vals.setdefault(r["meta"].get(stability.cluster_key), []).append(r["value"])
        per_method[m.method_id] = {k: sum(v) / float(len(v)) for k, v in vals.items()}
    shared = [c for c in sorted(set.intersection(
        *[set(per_method[m.method_id]) for m in methods]), key=key_repr)]
    return {"enabled": True, "contract": stability.describe(),
            "results": agg.paired_cluster_stability(shared, per_method, stability)}


def _case_table(cases, sets, methods):
    """Case-level audit rows. Applicability never depends on an error value."""
    rows = []
    for c in sorted(cases, key=lambda x: _sort_key(x.key)):
        rows.append({
            "case_id": key_repr(c.key),
            "population_id": value_or_unavailable(c.population_id, "not supplied"),
            "sequence_id": c.sequence_id,
            "trajectory_id": c.trajectory_id,
            "first_target_frame": c.first_target_frame,
            "run_length": c.run_length,
            "applicability_state": "admitted",
            "metric_valid": c.key in sets["C"],
            "method_support": {m.method_id: c.key in sets["B"][m.method_id]
                               for m in methods},
            "common_support": c.key in sets["D"],
            "stratum": value_or_unavailable(c.stratum, "not supplied"),
            "exclusion_reason": (
                unavailable("case is in common support")
                if c.key in sets["D"] else
                ("metric_validity" if c.key not in sets["C"] else "method_support"))})
    return rows


# --------------------------------------------------------- precomputed mode
def _precomputed_value(entry, field):
    """Accept per-target error lists or an already-computed case-level value."""
    if isinstance(entry, dict):
        if "errors" in entry and field in entry["errors"]:
            return agg.case_mean(entry["errors"][field])
        if "value" in entry and isinstance(entry["value"], dict):
            return entry["value"].get(field)
        if field in entry:
            v = entry[field]
            return agg.case_mean(v) if isinstance(v, (list, tuple)) else v
    return None


def audit_precomputed_results(cases, method_results, aggregation,
                              applicability=None, metric_valid=None,
                              strata: bool = True,
                              stability: Optional[StabilityContract] = None,
                              provenance: Optional[Dict[str, object]] = None
                              ) -> "AuditResult":
    """Audit a published benchmark without rerunning any reconstruction method.

    ``method_results`` is keyed by method identifier and then by **case
    identifier**. Nothing is ever aligned by position: two methods reporting the
    same number of rows is not evidence that they ran on the same cases, and a
    result naming a case that is not in the admitted set is reported as an
    alignment mismatch rather than quietly intersected away.
    """
    stability = stability or StabilityContract(enabled=False)
    reasons: List[str] = []

    meta_by_id = {}
    for row in cases:
        cid = key_repr(row["case_id"])
        if cid in meta_by_id:
            raise AuditContractError(
                "duplicate precomputed case identifier %r" % (cid,))
        meta = {k: row.get(k) for k in
                ("population_id", "sequence_id", "trajectory_id",
                 "first_target_frame", "run_length", "stratum")}
        meta.setdefault("sequence_id", None)
        meta_by_id[cid] = meta
    A = sorted(meta_by_id)

    if metric_valid is None:
        C = set(A)
    elif isinstance(metric_valid, dict):
        C = set(k for k in A if metric_valid.get(k, True))
    else:
        C = set(A) & {key_repr(k) for k in metric_valid}

    method_ids = sorted(method_results)
    if not method_ids:
        raise AuditContractError("at least one method's results are required")

    values = {}
    B = {}
    unknown_ids = {}
    for mid in method_ids:
        rows = method_results[mid]
        seen = {}
        stray = []
        for raw_cid, entry in rows.items():
            cid = key_repr(raw_cid)
            if cid in seen:                  # pragma: no cover - dict keys unique
                raise AuditContractError(
                    "duplicate case identifier %r in results of %r" % (cid, mid))
            if cid not in meta_by_id:
                stray.append(cid)
                continue
            seen[cid] = {f: _precomputed_value(entry, f)
                         for f in aggregation.metric_fields}
        values[mid] = seen
        B[mid] = set(seen)
        if stray:
            unknown_ids[mid] = sorted(stray)
        if not seen:
            reasons.append("METHOD_SUPPORT_INCOMPLETE")
    if unknown_ids:
        reasons.append("CASE_ALIGNMENT_MISMATCH")

    D = set(A) & C
    for mid in method_ids:
        D &= B[mid]
    for mid in method_ids:
        missing = [cid for cid in sorted(D)
                   if any(values[mid][cid].get(f) is None
                          for f in aggregation.metric_fields)]
        if missing:
            reasons.append("INCOMPLETE_METHOD_RESULTS")
            D -= set(missing)

    def _estimate(mid, keys):
        out = {"n_cases": len(keys)}
        for field in aggregation.metric_fields:
            recs = [{"value": values[mid][k][field], "meta": meta_by_id[k]}
                    for k in sorted(keys)
                    if values[mid][k].get(field) is not None]
            out[field] = agg.run_ladder(recs, aggregation, field)
        return out

    own_sets = {mid: (set(A) & C & B[mid]) for mid in method_ids}
    common = {mid: _estimate(mid, D) for mid in method_ids}
    specific = {mid: _estimate(mid, own_sets[mid]) for mid in method_ids}

    shift = {}
    for mid in method_ids:
        entry = {"supports_identical": own_sets[mid] == D}
        for field in aggregation.metric_fields:
            a = common[mid][field]["headline"]
            b = specific[mid][field]["headline"]
            entry[field] = (unavailable("one side of the comparison is undefined")
                            if (is_unavailable(a) or is_unavailable(b)) else a - b)
        shift[mid] = entry

    if applicability is None:
        app_block = unavailable(
            "no population-level applicability information was supplied")
        scoreable = 0
        applicable = 0
    else:
        counts = dict(applicability.get("counts", {}))
        scoreable = int(applicability.get("scoreable_targets", sum(counts.values())))
        assert_exact_partition(counts, scoreable)
        admitted = tuple(applicability.get("admitted_classes", ("eligible",)))
        applicable = sum(counts.get(c, 0) for c in admitted)
        app_block = {"counts": counts,
                     "fractions": {c: (counts[c] / float(scoreable) if scoreable
                                       else unavailable("no scoreable target"))
                                   for c in counts},
                     "exact_partition_verified": True,
                     "admitted_classes": list(admitted)}

    result = {
        "schema_version": SCHEMA_VERSION,
        "population": {"observations_in_population": len(A),
                       "non_scoreable_dropped": 0,
                       "trajectories": len({meta_by_id[c]["trajectory_id"]
                                            for c in A}),
                       "segments": unavailable("not applicable in precomputed mode"),
                       "scoreable_targets": scoreable if applicability else
                       unavailable("no applicability information supplied")},
        "applicability": app_block,
        "natural_runs": unavailable("not reconstructible from precomputed results"),
        "cases": {"admitted_A": len(A), "unique_keys_verified": True},
        "metric_validity": {"C": len(C), "removed_from_A": len(set(A) - C),
                            "redundant": len(set(A) - C) == 0},
        "method_support": {mid: len(B[mid]) for mid in method_ids},
        "common_support": {"D": len(D),
                           "case_keys_identical_across_methods": not unknown_ids,
                           "identical_across_methods":
                               len({frozenset(B[m]) for m in method_ids}) == 1},
        "support_retention": (unavailable("no admitted case; |A| = 0") if not A
                              else len(D) / float(len(A))),
        "method_specific_estimates": specific,
        "common_support_estimates": common,
        "support_shift": shift,
        "aggregation": {"contract": aggregation.describe(),
                        "contributing_units_per_reported_grid_length":
                            agg.contributing_units_per_grid_length(
                                [{"value": 1.0, "meta": meta_by_id[k]}
                                 for k in sorted(D)], aggregation)},
        "failure_modes": {"taxonomy": list(FAILURE_MODES)},
        "case_alignment": {
            "aligned_by": "case identifier",
            "positional_alignment_used": False,
            "unknown_case_identifiers": unknown_ids or {},
            "methods_reporting_no_case": [m for m in method_ids if not B[m]]},
        "strata": unavailable("stratification disabled") if not strata else
        _precomputed_strata(meta_by_id, values, D, aggregation, method_ids),
        "stability": {"enabled": False,
                      "results": unavailable("stability is not computed in "
                                             "precomputed mode"),
                      "contract": stability.describe()},
        "case_table": [{"case_id": cid,
                        "population_id": value_or_unavailable(
                            meta_by_id[cid]["population_id"], "not supplied"),
                        "sequence_id": value_or_unavailable(
                            meta_by_id[cid]["sequence_id"], "not supplied"),
                        "trajectory_id": value_or_unavailable(
                            meta_by_id[cid]["trajectory_id"], "not supplied"),
                        "first_target_frame": value_or_unavailable(
                            meta_by_id[cid]["first_target_frame"], "not supplied"),
                        "run_length": value_or_unavailable(
                            meta_by_id[cid]["run_length"], "not supplied"),
                        "applicability_state": "admitted",
                        "metric_valid": cid in C,
                        "method_support": {m: cid in B[m] for m in method_ids},
                        "common_support": cid in D,
                        "stratum": value_or_unavailable(
                            meta_by_id[cid]["stratum"], "not supplied"),
                        "exclusion_reason": (
                            unavailable("case is in common support") if cid in D
                            else ("metric_validity" if cid not in C
                                  else "method_support"))}
                       for cid in A],
        "provenance": {
            "applicability_contract": unavailable(
                "not supplied in precomputed mode") if applicability is None
            else {"admitted_classes": list(app_block["admitted_classes"])},
            "methods": [{"method_id": m, "description": "precomputed results"}
                        for m in method_ids],
            "aggregation_contract": aggregation.describe(),
            "stability_contract": stability.describe(),
            "schema_version": SCHEMA_VERSION,
            "mode": "precomputed",
            "supplied": dict(provenance) if provenance else {}},
        "validation": {"exact_applicability_partition": applicability is not None,
                       "unique_case_keys": True,
                       "identical_common_support_keys": not unknown_ids,
                       "all_methods_represented": method_ids,
                       "no_silent_case_drop": True},
    }
    result["diagnostics"] = {
        "support_geometry": pairwise_support_geometry(B),
        "coverage": coverage_diagnostics(
            scoreable_targets=scoreable, applicable_targets=applicable,
            admitted_A=len(A),
            per_method_conditional={m: len(own_sets[m]) for m in method_ids},
            common_D=len(D))}
    fp_payload = {"aggregation": aggregation.describe(),
                  "methods": method_ids, "mode": "precomputed",
                  "stability": stability.describe()}
    result["provenance"]["configuration_fingerprint"] = hashlib.sha256(
        _fingerprint_bytes(fp_payload)).hexdigest()
    result["certificate"] = build_certificate(result, extra_reasons=reasons)
    assert_no_raw_none(result)
    return AuditResult(result)


def _fingerprint_bytes(payload) -> bytes:
    from .serialization import dumps
    return dumps(payload).encode("utf-8")


def _precomputed_strata(meta_by_id, values, D, aggregation, method_ids):
    names = sorted({meta_by_id[c]["stratum"] for c in meta_by_id}, key=key_repr)
    if names == [None]:
        return unavailable("no stratum metadata supplied")
    out = {}
    for name in names:
        keys = [c for c in sorted(D) if meta_by_id[c]["stratum"] == name]
        entry = {"cases_in_common_support": len(keys)}
        if keys:
            per = {}
            for mid in method_ids:
                fields = {"n_cases": len(keys)}
                for field in aggregation.metric_fields:
                    recs = [{"value": values[mid][k][field], "meta": meta_by_id[k]}
                            for k in keys if values[mid][k].get(field) is not None]
                    fields[field] = agg.run_ladder(recs, aggregation, field)
                per[mid] = fields
            entry["reconstruction"] = per
        else:
            entry["reconstruction"] = unavailable(
                "no common-support case in this stratum")
        out[key_repr(name)] = entry
    return out
