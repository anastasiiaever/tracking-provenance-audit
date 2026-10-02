"""Development guard (protocol Sec. 17).

Real prospective V9 execution is blocked until an explicit release marker
exists. The marker is created only by a later execution-authorizing commit.
Fixtures and the immutable historical V8 replay are always permitted.
"""
from __future__ import annotations
import os

import yaml

MARKER_ENV = "TPAMI_V9_EXECUTION_AUTHORIZED"  # retained for reference only; NOT an authorization path
MARKER_FILE = "docs/tpami_v9_tracking_provenance/EXECUTION_AUTHORIZED"
RETRY_MARKER_FILE = "docs/tpami_v9_tracking_provenance/EXECUTION_AUTHORIZED_RETRY"
REQUIRED_RETRY_KEYS = ("schema", "authorized_run_ids", "refused_run_ids", "stop_rule")
REASON = "V9_EXECUTION_NOT_AUTHORIZED"


def _structured_marker(text, required_keys):
    """Parse a marker as YAML and return the mapping, or None if it is not a
    valid marker.

    A marker authorizes execution only if it parses as a YAML mapping whose
    top-level keys include every required key. A substring test cannot do this:
    a comment line, or prose containing `schema:` and `authorization:`, would
    satisfy it without ever defining those keys.
    """
    try:
        doc = yaml.safe_load(text)
    except yaml.YAMLError:
        return None
    if not isinstance(doc, dict):
        return None
    for key in required_keys:
        if key not in doc:
            return None
    return doc


class ExecutionNotAuthorized(RuntimeError):
    pass


REQUIRED_MARKER_KEYS = ("schema", "run_order", "authorization")


def release_marker_present(repo_root: str = ".") -> bool:
    """True only when a schema-valid authorization marker FILE exists.

    The marker file is the sole authorization for prospective execution. The
    generic environment-variable bypass was deliberately removed: an env var is
    not a reviewable, committed artifact, and the frozen marker is present and
    sufficient. An empty or malformed marker does not authorize anything.
    """
    path = os.path.join(repo_root, MARKER_FILE)
    if not os.path.isfile(path):
        return False
    try:
        text = open(path, encoding="utf-8").read()
    except OSError:
        return False
    return _structured_marker(text, REQUIRED_MARKER_KEYS) is not None


def require_authorization(mode: str, repo_root: str = ".") -> None:
    """mode: 'fixture' | 'historical_v8' | 'prospective_v9'."""
    if mode in ("fixture", "historical_v8"):
        return
    if mode != "prospective_v9":
        raise ValueError(f"unknown execution mode {mode!r}")
    if not release_marker_present(repo_root):
        raise ExecutionNotAuthorized(
            f"{REASON}: prospective V9 execution requires the schema-valid "
            f"authorization marker {MARKER_FILE}. No environment-variable bypass "
            f"is accepted.")


class RunIdNotAuthorized(RuntimeError):
    pass


def authorized_retry_run_ids(repo_root: str = ".") -> set:
    """Run IDs licensed by the append-only retry marker.

    Returns an empty set unless a schema-valid retry marker exists. Only IDs
    listed under `authorized_run_ids:` are licensed; everything else — reuse of
    a completed or failed -001 ID, a DEEPOCSORT-002 rerun, or an arbitrary -003
    — is refused.
    """
    path = os.path.join(repo_root, RETRY_MARKER_FILE)
    if not os.path.isfile(path):
        return set()
    try:
        text = open(path, encoding="utf-8").read()
    except OSError:
        return set()
    if _structured_marker(text, REQUIRED_RETRY_KEYS) is None:
        return set()
    out, inblock = set(), False
    for line in text.splitlines():
        if line.startswith("authorized_run_ids:"):
            inblock = True
            continue
        if inblock:
            st = line.strip()
            if not line.startswith((" ", "\t")) or not st:
                break
            if ":" in st:
                out.add(st.split(":", 1)[1].strip())
    return out


def require_run_id_authorized(run_id: str, repo_root: str = ".") -> None:
    ok = authorized_retry_run_ids(repo_root)
    if run_id not in ok:
        raise RunIdNotAuthorized(
            f"RUN_ID_NOT_AUTHORIZED: {run_id!r} is not licensed by the retry marker "
            f"{RETRY_MARKER_FILE}. Authorized: {sorted(ok) or 'none'}.")


# ---------------------------------------------------------------------------
# Dataset-, cell- and run-scoped authorization (record 11A, finding V9-B21)
#
# require_authorization() above checks only that SOME marker exists. That is not
# sufficient: the MOT17 marker must never license a MOT20 run. Everything below
# binds on (dataset, pipeline, run_id) simultaneously.
# ---------------------------------------------------------------------------

DATASET_MARKERS = {
    "MOT17": (MARKER_FILE, RETRY_MARKER_FILE),
    "MOT20": ("docs/tpami_v9_tracking_provenance/EXECUTION_AUTHORIZED_MOT20",),
}
RUN_ID_BLOCKS = ("run_order:", "authorized_run_ids:", "authorized_cells:")
DATASET_MARKER_REQUIRED_KEYS = {
    "MOT17": ("schema", "authorization"),
    "MOT20": ("schema", "dataset", "authorized_cells", "authorization"),
}


class DatasetNotAuthorized(RuntimeError):
    pass


class RunIdDatasetMismatch(RuntimeError):
    pass


class CellNotAuthorized(RuntimeError):
    pass


def _marker_text(repo_root: str, rel: str):
    path = os.path.join(repo_root, rel)
    if not os.path.isfile(path):
        return None
    try:
        return open(path, encoding="utf-8").read()
    except OSError:
        return None


def _parse_authorized_entries(text: str) -> set:
    """Entries under a run-id block, as (pipeline_or_None, run_id) pairs.

    A value may be a bare run id (`1: V9-MOT17-DEEPOCSORT-001`) or a
    pipeline-bound cell (`1: Deep-OC-SORT | V9-MOT20-DEEPOCSORT-001`).
    """
    out, inblock = set(), False
    for line in text.splitlines():
        if any(line.startswith(b) for b in RUN_ID_BLOCKS):
            inblock = True
            continue
        if not inblock:
            continue
        stripped = line.strip()
        if not line.startswith((" ", "\t")) or not stripped:
            inblock = False
            continue
        if stripped.startswith("#") or ":" not in stripped:
            continue
        value = stripped.split(":", 1)[1].strip()
        value = value.split("#", 1)[0].strip()
        if not value:
            continue
        if "|" in value:
            pipeline, run_id = (x.strip() for x in value.split("|", 1))
            out.add((pipeline or None, run_id))
        else:
            out.add((None, value))
    return out


def authorized_cells(dataset: str, repo_root: str = ".") -> set:
    """(pipeline_or_None, run_id) pairs licensed for this dataset. Empty = none."""
    rels = DATASET_MARKERS.get(dataset)
    if not rels:
        return set()
    required = DATASET_MARKER_REQUIRED_KEYS[dataset]
    out = set()
    for rel in rels:
        text = _marker_text(repo_root, rel)
        if text is None:
            continue
        doc = _structured_marker(text, required)
        if doc is None:
            continue
        if dataset == "MOT20":
            # a MOT20 marker must declare itself as such, as a parsed value
            if doc.get("dataset") != "MOT20":
                continue
        out |= _parse_authorized_entries(text)
    return out


def require_cell_authorized(dataset: str, pipeline: str, run_id: str,
                            repo_root: str = ".") -> None:
    """Bind authorization to dataset AND deployment AND exact run id.

    Refuses, in order, an unknown dataset, a run id naming a different dataset,
    a dataset with no marker of its own, and a cell/run id the marker does not
    list. The MOT17 marker can never satisfy a MOT20 request because
    DATASET_MARKERS maps the two datasets to disjoint files.
    """
    if dataset not in DATASET_MARKERS:
        raise DatasetNotAuthorized(
            f"DATASET_NOT_AUTHORIZED: no authorization marker is defined for "
            f"dataset {dataset!r}.")
    if not run_id:
        raise CellNotAuthorized("RUN_ID_REQUIRED: prospective execution needs --run-id.")
    prefix = f"V9-{dataset}-"
    if not run_id.startswith(prefix):
        raise RunIdDatasetMismatch(
            f"RUN_ID_DATASET_MISMATCH: run id {run_id!r} does not name dataset "
            f"{dataset} (expected prefix {prefix!r}).")
    licensed = authorized_cells(dataset, repo_root)
    if not licensed:
        raise DatasetNotAuthorized(
            f"{dataset}_EXECUTION_NOT_AUTHORIZED: no schema-valid authorization "
            f"marker exists for {dataset} at any of "
            f"{list(DATASET_MARKERS[dataset])}. The markers for other datasets do "
            f"not license this one.")
    if (pipeline, run_id) in licensed or (None, run_id) in licensed:
        return
    raise CellNotAuthorized(
        f"CELL_NOT_AUTHORIZED: ({dataset}, {pipeline!r}, {run_id!r}) is not licensed "
        f"by the {dataset} marker. Licensed: {sorted(licensed) or 'none'}.")
