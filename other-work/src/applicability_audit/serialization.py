"""Structured absence and deterministic, JSON-compatible serialization."""
from __future__ import annotations

import json
from typing import Any, Dict

SCHEMA_VERSION = "applicability_audit/1"


def unavailable(reason: str) -> Dict[str, object]:
    """The single representation of a defined-but-unpopulated quantity."""
    return {"available": False, "reason": reason, "value": None}


def is_unavailable(value) -> bool:
    return isinstance(value, dict) and value.get("available") is False


def value_or_unavailable(value, reason: str):
    return unavailable(reason) if value is None else value


def key_repr(key) -> str:
    """Deterministic string form of a structured key, stable across runs."""
    if isinstance(key, (list, tuple)):
        return "|".join("" if k is None else str(k) for k in key)
    return "" if key is None else str(key)


def _normalize(obj):
    """JSON has no tuple keys and no integer keys; make the mapping explicit."""
    if isinstance(obj, dict):
        return {key_repr(k): _normalize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set, frozenset)):
        items = sorted(obj, key=key_repr) if isinstance(obj, (set, frozenset)) else obj
        return [_normalize(v) for v in items]
    return obj


def dumps(obj) -> str:
    """Deterministic JSON: stable key order, fixed indent, UTF-8, no NaN/Inf."""
    return json.dumps(_normalize(obj), indent=2, sort_keys=True,
                      ensure_ascii=False, allow_nan=False) + "\n"


def assert_no_raw_none(obj, path: str = "") -> None:
    """A bare ``None`` means a producer silently failed; absence must be structured."""
    from .contracts import AuditContractError
    if is_unavailable(obj):
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            assert_no_raw_none(v, "%s.%s" % (path, key_repr(k)) if path else key_repr(k))
        return
    if isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            assert_no_raw_none(v, "%s[%d]" % (path, i))
        return
    if obj is None:
        raise AuditContractError(
            "audit field %r was never populated; a value or the structured "
            "unavailable state is required" % path)
