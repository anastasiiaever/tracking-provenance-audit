"""Record 59C --- corpus-level orchestration frozen by Record 59B.

This module contains **no scientific definition**. Every population rule,
target/anchor rule, segmentation rule, Gate 1R rule, natural-run rule, operator,
metric, support definition, aggregation rule, bootstrap setting and threshold is
imported from the Record 58 primitives or from ``protocol57``. What is added here
is only the deterministic corpus-level mapping that Record 59B specified:
drive both populations, accumulate, assemble, and populate the frozen 50-slot
result schema.

Testing seam
------------
``run_cross_domain_evaluation`` is the real-input wrapper; it verifies digests,
checks MOT17 ground-truth copy identity, calls the frozen parsers and hands
canonical rows to ``_run_from_canonical_populations``. The internal function
accepts already-canonical synthetic populations, so the complete corpus logic is
testable without either dataset. The seam exposes no scientific configuration.
"""
from __future__ import annotations

import hashlib
import platform
import zipfile
from typing import Dict, Iterable, List, Mapping, Optional, Sequence

from .bdd_parser import parse_parquet
from .bootstrap import paired_stability
from .canonical import (CanonicalRow, assert_exact_partition, build_cases,
                        classify_gate_1r, group_trajectories, natural_runs,
                        on_grid, segment_trajectory)
from .evaluate import (UNDEFINED, aggregate, assert_identical_case_keys,
                       reconstruct, support_sets, target_errors)
from .mot17_parser import parse_zip
from .protocol57 import (BDD_CATEGORIES, BDD_PATH, BDD_SHA256, BOOTSTRAP_REPLICATES,
                         BOOTSTRAP_SEED, GAP_GRID, GATE_1R_CLASSES,
                         MATERIALITY_CRITERION, MOT17_BASE_SEQUENCES, MOT17_PATH,
                         MOT17_SHA256, OPERATOR_NAMES, POPULATION_PRIMARY,
                         POPULATION_SECONDARY, PROTOCOL_COMMIT,
                         PROTOCOL_JSON_SHA256, PROTOCOL_MD_SHA256, RESULT_ROOT,
                         ProtocolViolation)
from .serialize import empty_result

# Record 57 sec. 3 names the three ground-truth directory copies. This tuple is
# used only for the byte-identity integrity check; DPM alone remains canonical.
MOT17_GT_COPY_DETECTORS = ("DPM", "FRCNN", "SDP")

METRIC_FIELDS = ("normalized", "raw_pixel")

REQUIRED_PROVENANCE_KEYS = (
    "implementation_commit", "protocol_commit", "protocol_md_sha256",
    "protocol_json_sha256", "implementation_lock_commit",
    "implementation_correction_commit", "release_commit",
    "orchestration_contract_commit", "timestamp_utc")


# --------------------------------------------------------- structured absence
def unavailable(reason: str) -> Dict[str, object]:
    """The single frozen representation of a defined-but-unpopulated slot."""
    return {"available": False, "reason": reason, "value": None}


def is_unavailable(value) -> bool:
    return isinstance(value, dict) and value.get("available") is False


def _value_or_unavailable(value, reason: str):
    return unavailable(reason) if value is None else value


# ------------------------------------------------------------------ integrity
def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_input_digest(path: str, expected_sha256: str, label: str) -> str:
    got = sha256_file(path)
    if got != expected_sha256:
        raise ProtocolViolation(
            "%s SHA mismatch: expected %s got %s" % (label, expected_sha256, got))
    return got


def verify_mot17_gt_copy_identity(path: str) -> Dict[str, str]:
    """Record 57 sec. 15: DPM/FRCNN/SDP ``gt.txt`` must stay byte-identical.

    Raw member bytes are hashed and compared. No ground-truth line is parsed and
    no scientific quantity is produced by this check.
    """
    digests = {}
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        for base in MOT17_BASE_SEQUENCES:
            per_copy = {}
            for det in MOT17_GT_COPY_DETECTORS:
                suffix = "%s-%s/gt/gt.txt" % (base, det)
                found = [n for n in names if n.endswith(suffix)]
                if len(found) != 1:
                    raise ProtocolViolation(
                        "MOT17 ground-truth member %s is not uniquely resolvable "
                        "(%d matches)" % (suffix, len(found)))
                per_copy[det] = hashlib.sha256(z.read(found[0])).hexdigest()
            if len(set(per_copy.values())) != 1:
                raise ProtocolViolation(
                    "MOT17 ground-truth copies differ for %s: %r; Record 57 "
                    "sec. 15 stop condition" % (base, per_copy))
            digests[base] = per_copy[MOT17_GT_COPY_DETECTORS[0]]
    return digests


# ------------------------------------------------------- corpus accumulation
def _trajectory_sort_key(key) -> tuple:
    return tuple(str(part) for part in key)


def collect_population(rows: Iterable[CanonicalRow]) -> Dict[str, object]:
    """Group, segment, account and collect cases over one whole population.

    Applicability accounting covers every scoreable target, not only targets
    inside on-grid natural runs. Gate 1R classifications are accumulated per
    segment and never merged across segments, because frame indices repeat.
    """
    counts = {c: 0 for c in GATE_1R_CLASSES}
    per_category_counts: Dict[object, Dict[str, int]] = {}
    per_category_scoreable: Dict[object, int] = {}
    scoreable = 0
    run_counts = {g: 0 for g in GAP_GRID}
    off_grid = 0
    total_runs = 0
    cases: List[dict] = []

    grouped = group_trajectories(rows)
    for key in sorted(grouped, key=_trajectory_sort_key):
        for segment in segment_trajectory(grouped[key]):
            classes = classify_gate_1r(segment)
            for r in segment:
                if not r.target:
                    continue
                cls = classes[r.frame_index]
                counts[cls] += 1
                scoreable += 1
                cat = per_category_counts.setdefault(
                    r.category, {c: 0 for c in GATE_1R_CLASSES})
                cat[cls] += 1
                per_category_scoreable[r.category] = \
                    per_category_scoreable.get(r.category, 0) + 1
            for run in natural_runs(segment):
                total_runs += 1
                if on_grid(run):
                    run_counts[len(run)] += 1
                else:
                    off_grid += 1
            cases.extend(build_cases(segment))

    assert_exact_partition(counts, scoreable)

    seen = set()
    for c in cases:
        if c["key"] in seen:
            raise ProtocolViolation(
                "duplicate reconstruction case key %r at corpus level" % (c["key"],))
        seen.add(c["key"])

    return {"gate_1r_counts": counts, "scoreable_targets": scoreable,
            "per_category_counts": per_category_counts,
            "per_category_scoreable": per_category_scoreable,
            "natural_run_counts": run_counts, "off_grid_run_count": off_grid,
            "total_natural_runs": total_runs, "cases": cases}


# ------------------------------------------------------- operator evaluation
def evaluate_cases(cases: Sequence[dict]):
    """Run the three frozen operators over every candidate case.

    An operator that is not defined yields ``valid: False`` and **no** error
    entry. No surrogate is ever created.
    """
    out = {name: {} for name in OPERATOR_NAMES}
    by_key = {}
    for case in cases:
        by_key[case["key"]] = case
        for name in OPERATOR_NAMES:
            pred = reconstruct(case, name)
            if pred is UNDEFINED:
                out[name][case["key"]] = {"valid": False}
                continue
            out[name][case["key"]] = {
                "valid": True,
                "errors": target_errors(case, pred),
                "sequence_id": case["sequence_id"],
                "gap_length": case["gap_length"],
                "category": case["category"]}
    return out, by_key


def _records_for(evaluated: Mapping[tuple, dict], keys: Iterable[tuple],
                 method: str) -> List[dict]:
    recs = []
    for key in sorted(keys, key=lambda k: tuple(str(p) for p in k)):
        rec = evaluated[key]
        if not rec["valid"]:
            raise ProtocolViolation(
                "operator %s was admitted to a support set for case %r but is "
                "not evaluable there; the frozen validity predicate and the "
                "frozen operator disagree" % (method, key))
        recs.append(rec)
    return recs


def _sanitize_per_video(per_video):
    """Keep the frozen per-video structure but never leave a bare None behind."""
    return {vid: {"cells": v["cells"],
                  "video_mean": _value_or_unavailable(
                      v["video_mean"], "no aggregable cell in this video"),
                  "represented_gap_lengths": v["represented_gap_lengths"]}
            for vid, v in per_video.items()}


def _aggregate_fields(evaluated, keys, method) -> Dict[str, object]:
    recs = _records_for(evaluated[method], keys, method)
    return {field: aggregate(recs, field) for field in METRIC_FIELDS}


# ------------------------------------------------------------------ assembly
def _population_result(population: str, corpus: Mapping[str, object],
                       provenance: Mapping[str, object],
                       input_path: str, input_sha256: str,
                       runtime: Mapping[str, object]) -> Dict[str, object]:
    result = empty_result(population)
    cases = corpus["cases"]
    scoreable = corpus["scoreable_targets"]

    # ---- provenance ------------------------------------------------------
    prov = result["provenance"]
    prov["implementation_commit"] = provenance["implementation_commit"]
    prov["input_path"] = input_path
    prov["input_sha256"] = input_sha256
    prov["runtime"] = dict(runtime)
    prov["timestamp_utc"] = provenance["timestamp_utc"]

    # ---- applicability ---------------------------------------------------
    app = result["applicability"]
    app["scoreable_targets"] = scoreable
    app["gate_1r_counts"] = dict(corpus["gate_1r_counts"])
    app["gate_1r_fractions"] = {
        c: (corpus["gate_1r_counts"][c] / float(scoreable) if scoreable
            else unavailable("no scoreable target in this population"))
        for c in GATE_1R_CLASSES}
    app["exact_partition_verified"] = True
    app["natural_run_counts"] = dict(corpus["natural_run_counts"])
    app["off_grid_run_count"] = corpus["off_grid_run_count"]

    # ---- support ladder --------------------------------------------------
    sets = support_sets(cases)
    A, B, C, D = sets["A"], sets["B"], sets["C"], sets["D"]
    evaluated, _by_key = evaluate_cases(cases)
    assert_identical_case_keys({name: set(D) for name in OPERATOR_NAMES})

    sup = result["operator_support"]
    sup["candidate_cases_A"] = len(A)
    sup["normalization_valid_C"] = len(C)
    sup["valid_cases_per_operator_B"] = {n: len(B[n]) for n in OPERATOR_NAMES}
    sup["common_support_cases_D"] = len(D)
    sup["retention"] = (len(D) / float(len(A)) if A
                        else unavailable("no Gate-1R candidate case; |A| = 0"))
    sup["case_keys_identical_across_methods"] = True

    # ---- reconstruction --------------------------------------------------
    rec = result["reconstruction"]
    common = {n: _aggregate_fields(evaluated, D, n) for n in OPERATOR_NAMES}
    method_specific = {}
    for n in OPERATOR_NAMES:
        own = (set(A) & C & B[n])
        method_specific[n] = {"support": own,
                              "fields": _aggregate_fields(evaluated, own, n)}

    empty_D = "common support D is empty"
    rec["primary_normalized_error"] = {
        n: _value_or_unavailable(common[n]["normalized"]["headline"], empty_D)
        for n in OPERATOR_NAMES}
    rec["raw_pixel_error"] = {
        n: _value_or_unavailable(common[n]["raw_pixel"]["headline"], empty_D)
        for n in OPERATOR_NAMES}
    rec["aggregation_components"] = {
        n: {field: {"per_video": _sanitize_per_video(common[n][field]["per_video"]),
                    "contributing_videos_per_gap_length":
                        common[n][field]["contributing_videos_per_gap_length"],
                    "gap_lengths_reported": common[n][field]["gap_lengths_reported"],
                    "aggregation": common[n][field]["aggregation"]}
            for field in METRIC_FIELDS}
        for n in OPERATOR_NAMES}
    rec["identical_common_support_estimates"] = {
        n: {"n_cases": len(D),
            **{field: _value_or_unavailable(common[n][field]["headline"], empty_D)
               for field in METRIC_FIELDS}}
        for n in OPERATOR_NAMES}

    ms_out = {}
    for n in OPERATOR_NAMES:
        own = method_specific[n]["support"]
        entry = {"n_cases": len(own), "supports_identical": set(own) == set(D)}
        for field in METRIC_FIELDS:
            mine = method_specific[n]["fields"][field]["headline"]
            theirs = common[n][field]["headline"]
            entry[field] = {
                "method_specific_estimate": _value_or_unavailable(
                    mine, "method-specific support is empty"),
                "common_support_estimate": _value_or_unavailable(theirs, empty_D),
                "support_shift": ((theirs - mine) if (mine is not None
                                                      and theirs is not None)
                                  else unavailable(
                                      "one side of the comparison is undefined"))}
        ms_out[n] = entry
    rec["method_specific_support_estimates"] = ms_out

    # ---- stability -------------------------------------------------------
    st = result["stability"]
    if population == POPULATION_PRIMARY:
        per_method_video = {
            n: {vid: v["video_mean"]
                for vid, v in common[n]["normalized"]["per_video"].items()
                if v["video_mean"] is not None}
            for n in OPERATOR_NAMES}
        clusters = sorted(set.intersection(*[set(per_method_video[n])
                                             for n in OPERATOR_NAMES])) \
            if per_method_video else []
        for n in OPERATOR_NAMES:
            missing = [c for c in clusters if c not in per_method_video[n]]
            if missing:                       # pragma: no cover - defensive
                raise ProtocolViolation(
                    "paired bootstrap cluster(s) %r lack a value for %s; no "
                    "imputation is permitted" % (missing, n))
        st["enabled"] = True
        st["cluster_unit"] = "videoName"
        st["paired"] = True
        if clusters:
            drawn = paired_stability(clusters, {n: per_method_video[n]
                                                for n in OPERATOR_NAMES},
                                     replicates=BOOTSTRAP_REPLICATES,
                                     seed=BOOTSTRAP_SEED)
            drawn["contributing_paired_clusters"] = len(clusters)
            st["results"] = drawn
        else:
            st["results"] = unavailable(
                "no video carries a common-support value for all three methods")
    else:
        st["enabled"] = False
        st["cluster_unit"] = unavailable(
            "MOT17 is not bootstrapped as a headline inferential analysis")
        st["paired"] = unavailable(
            "MOT17 is not bootstrapped as a headline inferential analysis")
        st["results"] = unavailable(
            "Record 57 sec. 12: MOT17 receives no confirmatory resampling")

    # ---- stratification --------------------------------------------------
    strat = result["stratification"]
    if population == POPULATION_PRIMARY:
        strat["bdd_category_summaries"] = _category_summaries(
            corpus, evaluated, D)
        strat["mot17_base_video_summaries"] = unavailable(
            "not applicable to the BDD population")
    else:
        strat["bdd_category_summaries"] = unavailable(
            "not applicable to the MOT17 population")
        strat["mot17_base_video_summaries"] = _base_video_summaries(common)

    # ---- outcome class ---------------------------------------------------
    if population == POPULATION_PRIMARY:
        if not scoreable:
            result["outcome_class"] = unavailable(
                "no scoreable target; the materiality criterion is undefined")
        else:
            ineligible = sum(corpus["gate_1r_counts"][c]
                             for c in ("leading", "trailing", "no_anchor"))
            frac = ineligible / float(scoreable)
            result["outcome_class"] = ("APPLICABILITY_MATERIAL"
                                       if frac >= MATERIALITY_CRITERION
                                       else "APPLICABILITY_NOT_MATERIAL")
    else:
        result["outcome_class"] = unavailable(
            "Record 57 assigns the materiality outcome class to the BDD "
            "population only")
    return result


def _category_summaries(corpus, evaluated, D) -> Dict[str, object]:
    """All eight frozen categories, always present, never fabricated."""
    counts = corpus["per_category_counts"]
    scoreable = corpus["per_category_scoreable"]
    out = {}
    for cat in BDD_CATEGORIES:
        entry: Dict[str, object] = {}
        n = scoreable.get(cat, 0)
        if n:
            c = counts[cat]
            entry["scoreable_targets"] = n
            entry["gate_1r_counts"] = {k: c[k] for k in GATE_1R_CLASSES}
            entry["gate_1r_fractions"] = {k: c[k] / float(n)
                                          for k in GATE_1R_CLASSES}
        else:
            entry["scoreable_targets"] = 0
            entry["gate_1r_counts"] = unavailable(
                "no scoreable target of this category")
            entry["gate_1r_fractions"] = unavailable(
                "no scoreable target of this category")
        keys = [k for k in D if evaluated[OPERATOR_NAMES[0]][k]["category"] == cat]
        if keys:
            entry["reconstruction"] = {
                m: {"n_cases": len(keys),
                    **{f: _value_or_unavailable(
                        _aggregate_fields(evaluated, keys, m)[f]["headline"],
                        "no aggregable case for this category")
                       for f in METRIC_FIELDS}}
                for m in OPERATOR_NAMES}
        else:
            entry["reconstruction"] = unavailable(
                "no common-support reconstruction case of this category")
        out[cat] = entry
    return out


def _base_video_summaries(common) -> Dict[str, object]:
    """All seven frozen base videos, before the final across-video average."""
    out = {}
    for base in MOT17_BASE_SEQUENCES:
        per_method = {}
        for m in OPERATOR_NAMES:
            fields = {}
            for f in METRIC_FIELDS:
                pv = common[m][f]["per_video"].get(base)
                fields[f] = (unavailable("no common-support case in this base video")
                             if pv is None else
                             {"cells": pv["cells"],
                              "video_mean": _value_or_unavailable(
                                  pv["video_mean"], "no aggregable cell"),
                              "represented_gap_lengths": pv["represented_gap_lengths"]})
            per_method[m] = fields
        out[base] = per_method
    return out


# ------------------------------------------------------ schema completeness
def assert_schema_complete(result: Mapping[str, object], path: str = "") -> None:
    """No raw ``None`` may survive population.

    A defined-but-empty quantity carries the frozen structured unavailable
    state; a bare ``None`` means a producer silently failed to run.
    """
    if is_unavailable(result):
        return
    if isinstance(result, dict):
        for k, v in result.items():
            assert_schema_complete(v, "%s.%s" % (path, k) if path else str(k))
        return
    if result is None:
        raise ProtocolViolation(
            "result field %r was never populated; Record 59B requires either a "
            "value or the structured unavailable state" % path)


def assert_schema_shape(result: Mapping[str, object], population: str) -> None:
    """Populated result must carry exactly the frozen serializer keys."""
    def shape(obj):
        if isinstance(obj, dict) and not is_unavailable(obj):
            return {k: shape(v) for k, v in obj.items()}
        return None
    reference = shape(empty_result(population))
    got = shape(result)

    def compare(ref, cur, path=""):
        if not isinstance(ref, dict):
            return
        if not isinstance(cur, dict):
            raise ProtocolViolation("result field %r lost its frozen shape" % path)
        missing = set(ref) - set(cur)
        extra = set(cur) - set(ref)
        if missing:
            raise ProtocolViolation("result is missing frozen key(s) %r at %r"
                                    % (sorted(map(str, missing)), path))
        if extra:
            raise ProtocolViolation("result adds non-frozen key(s) %r at %r"
                                    % (sorted(map(str, extra)), path))
        for k in ref:
            compare(ref[k], cur[k], "%s.%s" % (path, k) if path else str(k))
    compare(reference, got)


# ------------------------------------------------------------- orchestration
def _runtime_versions() -> Dict[str, object]:
    import numpy
    versions = {"python": platform.python_version(), "numpy": numpy.__version__,
                "scipy": None, "pandas": None}
    try:
        import scipy
        versions["scipy"] = scipy.__version__
    except Exception:                          # pragma: no cover - defensive
        versions["scipy"] = unavailable("scipy is not importable")
    try:
        import pandas
        versions["pandas"] = pandas.__version__
    except Exception:                          # pragma: no cover - defensive
        versions["pandas"] = unavailable("pandas is not importable")
    return versions


def _check_provenance(provenance: Mapping[str, object]) -> None:
    missing = [k for k in REQUIRED_PROVENANCE_KEYS if not provenance.get(k)]
    if missing:
        raise ProtocolViolation("provenance bundle is missing %r" % (missing,))
    if provenance["protocol_commit"] != PROTOCOL_COMMIT:
        raise ProtocolViolation("provenance protocol commit does not match the "
                                "frozen Record 57 commit")
    if (provenance["protocol_md_sha256"] != PROTOCOL_MD_SHA256
            or provenance["protocol_json_sha256"] != PROTOCOL_JSON_SHA256):
        raise ProtocolViolation("provenance protocol hashes do not match Record 57")


def _run_from_canonical_populations(populations: Mapping[str, Sequence[CanonicalRow]],
                                    provenance: Mapping[str, object],
                                    inputs: Mapping[str, Mapping[str, str]]
                                    ) -> Dict[str, object]:
    """Deterministic corpus orchestration over already-canonical populations.

    Execution order is frozen: BDD, then MOT17, then joint structural
    validation. No scientific value of the first population may influence the
    second; only a hard failure can prevent the second from running.
    """
    _check_provenance(provenance)
    runtime = _runtime_versions()
    results = {}
    for population in (POPULATION_PRIMARY, POPULATION_SECONDARY):
        if population not in populations:
            raise ProtocolViolation(
                "population %r is missing; both populations are frozen as "
                "mandatory by Record 59B" % population)
        corpus = collect_population(populations[population])
        results[population] = _population_result(
            population, corpus, provenance,
            inputs[population]["path"], inputs[population]["sha256"], runtime)
    for population, result in results.items():
        assert_schema_shape(result, population)
        assert_schema_complete(result)
    return results


def build_provenance_manifest(provenance: Mapping[str, object],
                              inputs: Mapping[str, Mapping[str, str]],
                              result_root: str) -> Dict[str, object]:
    return {
        "record": "60",
        "protocol_commit": provenance["protocol_commit"],
        "protocol_md_sha256": provenance["protocol_md_sha256"],
        "protocol_json_sha256": provenance["protocol_json_sha256"],
        "implementation_lock_commit": provenance["implementation_lock_commit"],
        "implementation_correction_commit":
            provenance["implementation_correction_commit"],
        "release_commit": provenance["release_commit"],
        "orchestration_contract_commit": provenance["orchestration_contract_commit"],
        "orchestration_implementation_commit": provenance["implementation_commit"],
        "inputs": {p: dict(inputs[p]) for p in sorted(inputs)},
        "runtime": _runtime_versions(),
        "timestamp_utc": provenance["timestamp_utc"],
        "populations": [POPULATION_PRIMARY, POPULATION_SECONDARY],
        "result_root": result_root,
        "mot17_gt_copy_identity_verified":
            provenance.get("mot17_gt_copy_identity_verified"),
    }


def run_cross_domain_evaluation(provenance: Mapping[str, object],
                                bdd_path: str = BDD_PATH,
                                mot17_path: str = MOT17_PATH,
                                result_root: str = RESULT_ROOT,
                                writer=None) -> Dict[str, object]:
    """Real-input entry point. Accepts no scientific configuration override.

    Every scientific rule is read from the frozen modules; the only arguments
    are input locations, the result root and an immutable provenance bundle.
    """
    from . import writer as writer_module

    _check_provenance(provenance)
    bdd_digest = verify_input_digest(bdd_path, BDD_SHA256, "BDD")
    mot17_digest = verify_input_digest(mot17_path, MOT17_SHA256, "MOT17")
    gt_digests = verify_mot17_gt_copy_identity(mot17_path)

    provenance = dict(provenance)
    provenance["mot17_gt_copy_identity_verified"] = sorted(gt_digests)

    populations = {POPULATION_PRIMARY: parse_parquet(bdd_path, BDD_SHA256),
                   POPULATION_SECONDARY: parse_zip(mot17_path, MOT17_SHA256)}
    inputs = {POPULATION_PRIMARY: {"path": bdd_path, "sha256": bdd_digest},
              POPULATION_SECONDARY: {"path": mot17_path, "sha256": mot17_digest}}

    results = _run_from_canonical_populations(populations, provenance, inputs)
    manifest = build_provenance_manifest(provenance, inputs, result_root)
    write = writer if writer is not None else writer_module.write_completed_result
    return write(result_root, results, manifest)
