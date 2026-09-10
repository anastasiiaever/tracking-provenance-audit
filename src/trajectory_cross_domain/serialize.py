"""Deterministic result schema, fixed before any outcome exists (Record 57 sec. 18).

``empty_result`` returns the full shape with every scientific slot set to None.
Record 58 ships this shape populated only by synthetic fixtures; no real value
is ever written during the implementation lock.
"""
from __future__ import annotations

from typing import Dict

from .protocol57 import (BOOTSTRAP_IS_CONFIDENCE_INTERVAL, BOOTSTRAP_REPLICATES,
                         BOOTSTRAP_SEED, GAP_GRID, GATE_1R_CLASSES,
                         OPERATOR_NAMES, PROTOCOL_COMMIT, PROTOCOL_JSON_SHA256,
                         PROTOCOL_MD_SHA256, RESULT_ROOT)

SCHEMA_VERSION = "trajectory_cross_domain/1"


def empty_result(population: str) -> Dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "population": population,
        "executed": False,
        "provenance": {
            "protocol_record": 57,
            "protocol_commit": PROTOCOL_COMMIT,
            "protocol_md_sha256": PROTOCOL_MD_SHA256,
            "protocol_json_sha256": PROTOCOL_JSON_SHA256,
            "implementation_commit": None,
            "input_path": None, "input_sha256": None,
            "runtime": {"python": None, "numpy": None, "scipy": None, "pandas": None},
            "timestamp_utc": None,
            "result_root": RESULT_ROOT},
        "applicability": {
            "scoreable_targets": None,
            "gate_1r_counts": {c: None for c in GATE_1R_CLASSES},
            "gate_1r_fractions": {c: None for c in GATE_1R_CLASSES},
            "exact_partition_verified": None,
            "natural_run_counts": {g: None for g in GAP_GRID},
            "off_grid_run_count": None},
        "operator_support": {
            "candidate_cases_A": None,
            "normalization_valid_C": None,
            "valid_cases_per_operator_B": {n: None for n in OPERATOR_NAMES},
            "common_support_cases_D": None,
            "retention": None,
            "case_keys_identical_across_methods": None},
        "reconstruction": {
            "primary_normalized_error": {n: None for n in OPERATOR_NAMES},
            "raw_pixel_error": {n: None for n in OPERATOR_NAMES},
            "aggregation_components": None,
            "method_specific_support_estimates": None,
            "identical_common_support_estimates": None},
        "stability": {
            "enabled": None, "n_replicates": BOOTSTRAP_REPLICATES,
            "seed": BOOTSTRAP_SEED, "cluster_unit": None, "paired": None,
            "results": None,
            "is_confidence_interval": BOOTSTRAP_IS_CONFIDENCE_INTERVAL},
        "stratification": {
            "bdd_category_summaries": None,
            "mot17_base_video_summaries": None},
        "outcome_class": None,
    }
