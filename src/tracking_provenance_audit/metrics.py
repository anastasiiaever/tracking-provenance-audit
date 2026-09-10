"""Frozen evaluator interface. No automatic fallback to another evaluator."""
from __future__ import annotations
import hashlib, os
from typing import Dict, List, Optional

TRACKEVAL_COMMIT = "12c8791b303e0a0b50f753af204249e622d0281a"
METRICS = ("HOTA", "DetA", "AssA", "IDF1", "MOTA")
METRIC_NOT_AVAILABLE = "METRIC_NOT_AVAILABLE"


class EvaluatorPinMismatch(RuntimeError):
    pass


def file_sha256(path: str) -> str:
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def freeze_inputs(state_paths: Dict[str, str], gt_paths: Dict[str, str],
                  evaluator_commit: str, config: dict) -> dict:
    """Freeze evaluator commit, config, adapter and state input hashes."""
    if evaluator_commit != TRACKEVAL_COMMIT:
        raise EvaluatorPinMismatch(
            f"evaluator pin {evaluator_commit!r} != frozen {TRACKEVAL_COMMIT!r}; "
            "no automatic fallback is permitted")
    return dict(
        evaluator="TrackEval", evaluator_commit=evaluator_commit, config=dict(config),
        state_input_sha256={k: file_sha256(v) for k, v in sorted(state_paths.items())},
        gt_input_sha256={k: file_sha256(v) for k, v in sorted(gt_paths.items())},
    )


def empty_metric_table(reason: str = METRIC_NOT_AVAILABLE) -> dict:
    return {m: None for m in METRICS} | {"status": reason}


def delta(r0: Optional[dict], r2: Optional[dict]) -> dict:
    if not r0 or not r2:
        return {m: None for m in METRICS} | {"status": METRIC_NOT_AVAILABLE}
    out = {}
    for m in METRICS:
        a, b = r0.get(m), r2.get(m)
        out[m] = None if (a is None or b is None) else (b - a)
    return out
