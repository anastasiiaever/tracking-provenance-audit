"""Deterministic audit report (protocol Sec. 14).

Serialization is canonical (sorted keys, fixed separators). No wall-clock value
may enter the hashed content; any timestamp lives outside `content`.
"""
from __future__ import annotations
import hashlib, json
from typing import Any, Dict

SCHEMA_VERSION = "v9-audit-report/1.1"

REQUIRED = (
    "schema_version", "input_hashes", "protocol_manifest_hash",
    "implementation_hash", "pipeline", "dataset", "documentation_role",
    "structural_family", "audit_mode", "execution_state", "split_status",
    "census_documentation_status", "stop_reason", "population_manifest",
    "outcome_knowledge_status", "pre_v9_known_quantities",
    "pre_v9_evidence_commit", "pre_v9_evidence_artifact",
    "row_transition_inventory", "stv_partition", "state_construction_status",
    "metric_input_manifests", "metric_table", "r0_r2_delta", "ordering",
    "materiality", "reason_codes", "reproducibility",
)

# Additive, and present ONLY when an execution-mode activation applies
# (record 12A). Absent by default, so every previously frozen report content
# hash is bit-identical under this schema version.
OPTIONAL = (
    "original_audit_mode", "effective_audit_mode", "original_execution_state",
    "effective_execution_state", "original_outcome_knowledge_status",
    "authorization_state", "run_id",
)


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)


def content_hash(content: Dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(content).encode("utf-8")).hexdigest()


# build() supplies this itself, so a caller is not required to pass it.
_SELF_SUPPLIED = ("schema_version",)


def build(**kw) -> Dict[str, Any]:
    # The requirement is key PRESENCE, not a non-null value: several required
    # fields are legitimately None (a documentation-only cell has no metric
    # table). Checking the assembled content cannot detect an omission, because
    # every required key would already have been created there.
    missing = [k for k in REQUIRED
               if k not in _SELF_SUPPLIED and k not in kw]
    if missing:
        raise ValueError(f"report missing required fields: {missing}")
    content = {k: kw.get(k) for k in REQUIRED}
    for k in OPTIONAL:
        if kw.get(k) is not None:
            content[k] = kw[k]
    content["schema_version"] = SCHEMA_VERSION
    return content


def serialize(content: Dict[str, Any]) -> str:
    """Deterministic bytes: identical content -> identical bytes and hash."""
    return canonical_json({"content": content, "content_sha256": content_hash(content)})
