"""Append-only execution-mode activation (record 12A).

The historical protocol (02_PROSPECTIVE_PROTOCOL.json) is the source of the
ORIGINAL audit mode and is never mutated. This module is the source of the
EFFECTIVE audit mode, and it only ever raises a single, exactly-named cell out of
STOPPED_BEFORE_EXECUTION.

Resolution is conjunctive: dataset AND deployment AND run_id must all match an
activation entry, AND the dataset-scoped authorization marker must still license
that exact triple. Remove or break the marker and resolution falls straight back
to the historical mode.
"""
from __future__ import annotations

import json
import os
from typing import Optional

from .guard import require_cell_authorized

ACTIVATION_RECORD = ("docs/tpami_v9_tracking_provenance/"
                     "12A_MOT20_DEEP_EXECUTION_MODE_ACTIVATION.json")
ACTIVATED_BY = "EXECUTION_MODE_ACTIVATED_BY_12A"
NOT_ACTIVATED = "NO_EXECUTION_MODE_ACTIVATION"


def load_activations(repo_root: str = ".") -> list:
    path = os.path.join(repo_root, ACTIVATION_RECORD)
    if not os.path.isfile(path):
        return []
    try:
        with open(path, encoding="utf-8") as fh:
            rec = json.load(fh)
    except (OSError, ValueError):
        return []
    acts = rec.get("activations")
    return acts if isinstance(acts, list) else []


def find_activation(dataset: str, pipeline: str, run_id: str,
                    repo_root: str = ".") -> Optional[dict]:
    """The activation entry for this EXACT triple, or None."""
    if not (dataset and pipeline and run_id):
        return None
    for a in load_activations(repo_root):
        if (a.get("dataset") == dataset
                and a.get("deployment") == pipeline
                and a.get("run_id") == run_id):
            return a
    return None


def resolve(cell: dict, dataset: str, pipeline: str, run_id: str,
            repo_root: str = ".") -> dict:
    """Historical vs effective execution state for one cell.

    Always returns both. `effective_audit_mode` differs from
    `original_audit_mode` only when an activation entry matches the exact triple
    AND the authorization marker still licenses it.
    """
    original_mode = cell["audit_mode"]
    out = {
        "original_audit_mode": original_mode,
        "original_execution_state": cell.get("execution_state"),
        "original_outcome_knowledge_status": cell.get("outcome_knowledge_status"),
        "effective_audit_mode": original_mode,
        "effective_execution_state": cell.get("execution_state"),
        "authorization_state": "NOT_AUTHORIZED",
        "activation": NOT_ACTIVATED,
        "run_id": run_id or None,
    }
    a = find_activation(dataset, pipeline, run_id, repo_root)
    if a is None:
        return out
    # the marker is re-checked on every resolution, never cached
    try:
        require_cell_authorized(dataset, pipeline, run_id, repo_root)
    except Exception:
        out["activation"] = "ACTIVATION_ENTRY_PRESENT_BUT_NOT_AUTHORIZED"
        return out
    if a.get("original_audit_mode") != original_mode:
        # the activation was written against a different historical state
        out["activation"] = "ACTIVATION_HISTORICAL_MISMATCH"
        return out
    out["effective_audit_mode"] = a["effective_audit_mode"]
    out["effective_execution_state"] = a["effective_execution_state"]
    out["authorization_state"] = a.get("authorization_state", "AUTHORIZED")
    out["activation"] = ACTIVATED_BY
    return out
