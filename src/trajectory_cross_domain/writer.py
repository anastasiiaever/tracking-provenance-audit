"""Record 59C --- deterministic, atomic result writer frozen by Record 59B.

Contains no scientific computation. It serializes an already completed result,
renders a human-readable summary from that result alone, and makes the finished
directory visible in one atomic step so a partial run can never be mistaken for
a completed one.
"""
from __future__ import annotations

import json
import os
from typing import Dict, Mapping

from .protocol57 import (BOOTSTRAP_REPLICATES, BOOTSTRAP_SEED, GAP_GRID,
                         GATE_1R_CLASSES, OPERATOR_NAMES, POPULATION_PRIMARY,
                         POPULATION_SECONDARY, ProtocolViolation)

RESULT_FILENAME = "result.json"
SUMMARY_FILENAME = "summary.md"
PROVENANCE_FILENAME = "provenance.json"
COMPLETION_FILENAME = "COMPLETE.json"
FINAL_FILENAMES = (RESULT_FILENAME, SUMMARY_FILENAME, PROVENANCE_FILENAME,
                   COMPLETION_FILENAME)
INCOMPLETE_SUFFIX = ".incomplete"


def _normalize_keys(obj):
    """JSON has no integer keys; make the conversion explicit and round-trip stable.

    The frozen schema uses integer gap lengths as mapping keys. Left implicit,
    ``json.dumps`` would emit them as strings while ``sort_keys`` had ordered
    them as integers, so re-serializing a reparsed file would reorder it. No
    value is altered.
    """
    if isinstance(obj, dict):
        return {str(k): _normalize_keys(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_normalize_keys(v) for v in obj]
    return obj


def dumps(obj) -> str:
    """Deterministic JSON: stable key order, fixed indent, UTF-8, no NaN/Inf."""
    return json.dumps(_normalize_keys(obj), indent=2, sort_keys=True,
                      ensure_ascii=False, allow_nan=False) + "\n"


def _is_unavailable(value) -> bool:
    return isinstance(value, dict) and value.get("available") is False


def _fmt(value) -> str:
    if _is_unavailable(value):
        return "unavailable (%s)" % value.get("reason", "")
    if isinstance(value, float):
        return repr(value)
    return str(value)


def render_summary(results: Mapping[str, dict], manifest: Mapping[str, object]) -> str:
    """Render markdown from the completed structured result only.

    Nothing is recomputed here; every line reads a field that the orchestration
    already produced and validated.
    """
    out = ["# Cross-domain trajectory evaluation --- structured result summary", ""]
    out.append("Rendered from the completed result artifact. No quantity is "
               "recomputed in this file and no interpretation is added.")
    out.append("")
    out.append("Protocol commit `%s`; orchestration implementation commit `%s`; "
               "timestamp `%s`."
               % (manifest["protocol_commit"],
                  manifest["orchestration_implementation_commit"],
                  manifest["timestamp_utc"]))
    out.append("")
    for population in (POPULATION_PRIMARY, POPULATION_SECONDARY):
        r = results[population]
        app, sup, rec = r["applicability"], r["operator_support"], r["reconstruction"]
        out.append("## Population `%s`" % population)
        out.append("")
        out.append("Input `%s`, sha256 `%s`."
                   % (r["provenance"]["input_path"], r["provenance"]["input_sha256"]))
        out.append("")
        out.append("### Applicability")
        out.append("")
        out.append("Scoreable targets: %s. Exact partition verified: %s."
                   % (_fmt(app["scoreable_targets"]),
                      _fmt(app["exact_partition_verified"])))
        out.append("")
        out.append("| class | count | fraction |")
        out.append("|---|---|---|")
        for c in GATE_1R_CLASSES:
            out.append("| %s | %s | %s |" % (c, _fmt(app["gate_1r_counts"][c]),
                                             _fmt(app["gate_1r_fractions"][c])))
        out.append("")
        out.append("Natural runs by exact frozen grid length (all lengths shown):")
        out.append("")
        out.append("| gap length | runs |")
        out.append("|---|---|")
        for g in GAP_GRID:
            out.append("| %d | %s |" % (g, _fmt(app["natural_run_counts"][g])))
        out.append("")
        out.append("Off-grid natural runs: %s." % _fmt(app["off_grid_run_count"]))
        out.append("")
        out.append("### Support ladder")
        out.append("")
        out.append("A = %s; C = %s; D = %s; retention = %s; case keys identical "
                   "across methods: %s."
                   % (_fmt(sup["candidate_cases_A"]), _fmt(sup["normalization_valid_C"]),
                      _fmt(sup["common_support_cases_D"]), _fmt(sup["retention"]),
                      _fmt(sup["case_keys_identical_across_methods"])))
        out.append("")
        out.append("| method | B | headline normalized | headline raw pixel |")
        out.append("|---|---|---|---|")
        for m in OPERATOR_NAMES:
            out.append("| %s | %s | %s | %s |"
                       % (m, _fmt(sup["valid_cases_per_operator_B"][m]),
                          _fmt(rec["primary_normalized_error"][m]),
                          _fmt(rec["raw_pixel_error"][m])))
        out.append("")
        out.append("### Support comparison")
        out.append("")
        out.append("| method | supports identical | normalized shift |")
        out.append("|---|---|---|")
        ms = rec["method_specific_support_estimates"]
        for m in OPERATOR_NAMES:
            out.append("| %s | %s | %s |" % (m, _fmt(ms[m]["supports_identical"]),
                                             _fmt(ms[m]["normalized"]["support_shift"])))
        out.append("")
        st = r["stability"]
        out.append("### Stability")
        out.append("")
        out.append("Enabled: %s; cluster unit: %s; paired: %s; replicates: %s; "
                   "seed: %s; is_confidence_interval: %s."
                   % (_fmt(st["enabled"]), _fmt(st["cluster_unit"]),
                      _fmt(st["paired"]), _fmt(st["n_replicates"]),
                      _fmt(st["seed"]), _fmt(st["is_confidence_interval"])))
        out.append("")
        out.append("### Outcome class")
        out.append("")
        out.append("%s" % _fmt(r["outcome_class"]))
        out.append("")
    return "\n".join(out) + "\n"


def _refuse_if_occupied(final: str, temp: str) -> None:
    if os.path.exists(final) and os.listdir(final):
        raise ProtocolViolation(
            "refusing to write: %r already exists and is not empty; an existing "
            "scientific result is never overwritten, appended to or deleted"
            % final)
    if os.path.exists(temp):
        raise ProtocolViolation(
            "refusing to write: incomplete execution directory %r already "
            "exists; it is never deleted automatically" % temp)


def write_completed_result(result_root: str, results: Mapping[str, dict],
                           manifest: Mapping[str, object]) -> Dict[str, object]:
    """Write every artifact into a temporary directory, then reveal atomically.

    The completion marker is the last file written, and it is written *inside*
    the temporary directory, so the final directory is never visible without it.
    """
    final = os.path.abspath(result_root)
    temp = final + INCOMPLETE_SUFFIX
    _refuse_if_occupied(final, temp)

    for population in (POPULATION_PRIMARY, POPULATION_SECONDARY):
        if population not in results:
            raise ProtocolViolation(
                "refusing to write an incomplete run: population %r is absent"
                % population)

    payload = dumps({"populations": dict(results)})
    provenance = dumps(dict(manifest))
    summary = render_summary(results, manifest)

    parent = os.path.dirname(temp)
    if parent:
        os.makedirs(parent, exist_ok=True)
    os.makedirs(temp, exist_ok=False)
    written = []
    for name, text in ((RESULT_FILENAME, payload),
                       (PROVENANCE_FILENAME, provenance),
                       (SUMMARY_FILENAME, summary)):
        with open(os.path.join(temp, name), "w", encoding="utf-8") as fh:
            fh.write(text)
        written.append(name)

    marker = dumps({
        "complete": True,
        "populations": [POPULATION_PRIMARY, POPULATION_SECONDARY],
        "files": sorted(written + [COMPLETION_FILENAME]),
        "protocol_commit": manifest["protocol_commit"],
        "orchestration_implementation_commit":
            manifest["orchestration_implementation_commit"],
        "timestamp_utc": manifest["timestamp_utc"],
        "bootstrap": {"replicates": BOOTSTRAP_REPLICATES, "seed": BOOTSTRAP_SEED},
    })
    with open(os.path.join(temp, COMPLETION_FILENAME), "w", encoding="utf-8") as fh:
        fh.write(marker)

    os.replace(temp, final)
    return {"result_root": final, "files": sorted(FINAL_FILENAMES),
            "complete": True}


def is_completed_result(result_root: str) -> bool:
    """A directory without the completion marker is never a completed result."""
    return os.path.isfile(os.path.join(result_root, COMPLETION_FILENAME))
