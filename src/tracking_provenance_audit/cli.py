"""audit-tracking-postprocess — the single scientific execution path.

Supports ROW_ADDITIVE_R0_R1_R2, NON_ROW_ADDITIVE_S0_S2, DOCUMENTATION_ONLY
refusal and STOPPED_BEFORE_EXECUTION refusal through one code path.
"""
from __future__ import annotations
import argparse, hashlib, json, os, sys
from typing import Dict, Optional

from .rowid import parse_mot, parse_gt
from .transitions import inventory, assert_row_additive, RowAdditiveViolation
from .stv import (classify, partition_counts, PRIMARY_IOU_GATE, SENSITIVITY_GATES,
                  SEMANTICALLY_ADMITTED, CLASSES)
from .states import build_R1, r1_status_for_non_row_additive, R1_CONSTRUCTED
from . import (activation as activationmod, adapters, materiality,
               metrics as metricsmod, report as reportmod)
from .guard import (require_authorization, require_cell_authorized,
                    authorized_cells)

ROW_ADDITIVE = "ROW_ADDITIVE_R0_R1_R2"
NON_ROW_ADDITIVE = "NON_ROW_ADDITIVE_S0_S2"
DOCUMENTATION_ONLY = "DOCUMENTATION_ONLY"
STOPPED_BEFORE_EXECUTION = "STOPPED_BEFORE_EXECUTION"


def _sha(p: str) -> str:
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def load_cell(protocol_path: str, pipeline: str, dataset: str) -> dict:
    P = json.load(open(protocol_path))
    for c in P["cells"]:
        if c["pipeline"] == pipeline and c["dataset"] == dataset:
            return c
    raise SystemExit(f"no frozen cell for {pipeline} x {dataset}")


DATASET_MATERIALIZED = "DATASET_MATERIALIZED"
EXECUTION_NOT_AUTHORIZED = "EXECUTION_NOT_AUTHORIZED"
EXECUTION_AUTHORIZED_CODE = "EXECUTION_AUTHORIZED"
AUDIT_MODE_STOPPED = "AUDIT_MODE_STOPPED_BEFORE_EXECUTION"
STOPPED_DATASET_NOT_ACQUIRED = "STOPPED_DATASET_NOT_ACQUIRED"
MATERIALIZED_STATE = "DATASET_MATERIALIZED_FROM_VERIFIED_MIRROR"


def stop_reason_codes(cell: dict, pipeline: str, dataset: str,
                     repo_root: str = ".") -> list:
    """Why this cell is stopped, read from the cell rather than hardcoded.

    Emitting STOPPED_DATASET_NOT_ACQUIRED for a materialised population would be
    false (finding V9-B20). A materialised-but-unauthorized cell is refused for a
    different, accurately named reason, and an unlicensed cell says so as well.

    Once a dataset-scoped marker licenses the cell, EXECUTION_NOT_AUTHORIZED
    would itself become false: the remaining barrier is then the frozen protocol
    audit_mode, which only a protocol amendment may lift.
    """
    state = cell.get("execution_state", "")
    if state == MATERIALIZED_STATE:
        if not adapters.cell_is_licensed(pipeline, dataset):
            return [DATASET_MATERIALIZED, EXECUTION_NOT_AUTHORIZED,
                    adapters.CELL_NOT_LICENSED]
        try:
            authorized = any(p == pipeline
                             for p, _ in authorized_cells(dataset, repo_root))
        except Exception:
            authorized = False
        if authorized:
            return [DATASET_MATERIALIZED, EXECUTION_AUTHORIZED_CODE,
                    AUDIT_MODE_STOPPED]
        return [DATASET_MATERIALIZED, EXECUTION_NOT_AUTHORIZED]
    if state:
        return [state]
    return [STOPPED_DATASET_NOT_ACQUIRED]


def run(raw: Optional[str], post: Optional[str], gt: Optional[str],
        dataset: str, pipeline: str, protocol: str, sequence: str = "SEQ",
        protocol_manifest_hash: str = "", implementation_hash: str = "",
        execution_mode: str = "fixture", repo_root: str = ".",
        sensitivity: bool = False, run_id: str = "") -> dict:
    cell = load_cell(protocol, pipeline, dataset)
    require_authorization(execution_mode, repo_root)
    if execution_mode == "prospective_v9":
        # V9-B21: bind authorization to dataset AND deployment AND exact run id.
        # The MOT17 marker can never license a MOT20 run.
        require_cell_authorized(dataset, pipeline, run_id, repo_root)
    # Record 12A: the historical protocol is the ORIGINAL source; an append-only
    # activation may raise exactly one named cell to its effective audit mode.
    act = activationmod.resolve(cell, dataset, pipeline, run_id, repo_root)
    mode = act["effective_audit_mode"]
    activated = act["activation"] == activationmod.ACTIVATED_BY

    common = dict(
        protocol_manifest_hash=protocol_manifest_hash,
        implementation_hash=implementation_hash,
        pipeline=pipeline, dataset=dataset,
        documentation_role=cell["documentation_role"],
        structural_family=cell["structural_family"],
        audit_mode=mode, execution_state=act["effective_execution_state"],
        split_status=cell["split_status"],
        census_documentation_status=cell["census_documentation_status"],
        stop_reason=cell["stop_reason"],
        outcome_knowledge_status=cell["outcome_knowledge_status"],
        pre_v9_known_quantities=cell.get("pre_v9_known_quantities"),
        pre_v9_evidence_commit=cell.get("pre_v9_evidence_commit"),
        pre_v9_evidence_artifact=cell.get("pre_v9_evidence_artifact"),
        population_manifest=adapters.get_manifest(dataset, pipeline),
        # additive and present only for an activated cell, so every previously
        # frozen report content hash is bit-identical
        original_audit_mode=act["original_audit_mode"] if activated else None,
        effective_audit_mode=act["effective_audit_mode"] if activated else None,
        original_execution_state=act["original_execution_state"] if activated else None,
        effective_execution_state=act["effective_execution_state"] if activated else None,
        original_outcome_knowledge_status=(act["original_outcome_knowledge_status"]
                                           if activated else None),
        authorization_state=act["authorization_state"] if activated else None,
        run_id=act["run_id"] if activated else None,
        reproducibility=None, ordering=None,
        metric_table=None, r0_r2_delta=None, metric_input_manifests=None,
    )

    # --- C / D: refusals, without ever overwriting the documentation role ---
    if mode in (DOCUMENTATION_ONLY, STOPPED_BEFORE_EXECUTION):
        rc = ([cell["census_documentation_status"]] if mode == DOCUMENTATION_ONLY
              else stop_reason_codes(cell, pipeline, dataset, repo_root))
        if act["activation"] not in (activationmod.NOT_ACTIVATED,
                                     activationmod.ACTIVATED_BY):
            rc.append(act["activation"])
        return reportmod.build(input_hashes={},
                               row_transition_inventory=None, stv_partition=None,
                               state_construction_status=mode,
                               materiality=None, reason_codes=rc, **common)

    if not (raw and post and gt):
        raise SystemExit("executable cell requires --raw, --post and --ground-truth")

    r0 = parse_mot(open(raw).read(), sequence)
    r2 = parse_mot(open(post).read(), sequence)
    gtr = parse_gt(open(gt).read(), sequence)
    inv = inventory(r0, r2)
    hashes = {"raw": _sha(raw), "post": _sha(post), "ground_truth": _sha(gt)}
    reasons = []

    # --- B: non-row-additive ---
    if mode == NON_ROW_ADDITIVE:
        status, why = r1_status_for_non_row_additive(cell["structural_family"])
        reasons.append(status)
        return reportmod.build(input_hashes=hashes,
                               row_transition_inventory=inv.to_dict(),
                               stv_partition=None, state_construction_status=status,
                               materiality=None,
                               reason_codes=reasons + [why], **common)

    # --- A: row-additive ---
    try:
        assert_row_additive(inv)
    except RowAdditiveViolation as e:
        return reportmod.build(input_hashes=hashes,
                               row_transition_inventory=inv.to_dict(),
                               stv_partition=None,
                               state_construction_status=e.reason_code,
                               materiality=None,
                               reason_codes=[e.reason_code, e.detail], **common)

    synth = [tuple(x) for x in inv.inserted_ids]
    cls = classify(synth, list(r0.values()), gtr, PRIMARY_IOU_GATE)
    counts = partition_counts(cls)
    build_R1(r0, r2, cls)                       # asserts R0 subset R1 subset R2
    non_admitted = sum(counts[c] for c in CLASSES if c != SEMANTICALLY_ADMITTED)
    part = dict(gate=PRIMARY_IOU_GATE, counts=counts, n_synthesized=len(synth),
                primary=True)
    if sensitivity:
        part["sensitivity"] = {
            str(g): partition_counts(classify(synth, list(r0.values()), gtr, g))
            for g in SENSITIVITY_GATES}
        part["sensitivity_status"] = ("DESCRIPTIVE; the 0.5 result remains primary "
                                      "regardless of sensitivity outcome")
    if activated:
        reasons = reasons + [activationmod.ACTIVATED_BY]
    return reportmod.build(
        input_hashes=hashes, row_transition_inventory=inv.to_dict(),
        stv_partition=part, state_construction_status=R1_CONSTRUCTED,
        materiality=materiality.classify(non_admitted, len(synth), inv.n_R2_rows),
        reason_codes=reasons, **common)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="audit-tracking-postprocess")
    ap.add_argument("--raw"); ap.add_argument("--post"); ap.add_argument("--ground-truth", dest="gt")
    ap.add_argument("--dataset-contract", required=True)
    ap.add_argument("--pipeline-contract", required=True)
    ap.add_argument("--protocol", default="docs/tpami_v9_tracking_provenance/02_PROSPECTIVE_PROTOCOL.json")
    ap.add_argument("--sequence", default="SEQ")
    ap.add_argument("--protocol-manifest-hash", default="")
    ap.add_argument("--implementation-hash", default="")
    ap.add_argument("--execution-mode", default="prospective_v9",
                    choices=["fixture", "historical_v8", "prospective_v9"])
    ap.add_argument("--sensitivity", action="store_true")
    ap.add_argument("--run-id", dest="run_id", default="",
                    help="exact frozen run id; required for --execution-mode prospective_v9")
    ap.add_argument("--output", required=True)
    a = ap.parse_args(argv)
    rep = run(a.raw, a.post, a.gt, a.dataset_contract, a.pipeline_contract,
              a.protocol, a.sequence, a.protocol_manifest_hash,
              a.implementation_hash, a.execution_mode, ".", a.sensitivity, a.run_id)
    os.makedirs(os.path.dirname(a.output) or ".", exist_ok=True)
    with open(a.output, "w") as f:
        f.write(reportmod.serialize(rep))
    print(reportmod.content_hash(rep))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
