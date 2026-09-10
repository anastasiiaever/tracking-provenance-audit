"""BDD100K-derived Kaggle MOT subset -> canonical rows (Record 57 sec. 2).

The row-classification logic is pure and is exercised entirely on synthetic
fixtures. Only :func:`parse_parquet` touches the real file, and it verifies the
frozen SHA256 first.
"""
from __future__ import annotations

import math
from typing import Iterable, List, Mapping

import numpy as np
import pandas as pd

from .canonical import CanonicalRow
from .protocol57 import (BDD_CATEGORIES, BDD_PATH, BDD_SCHEMA, BDD_SHA256,
                         POPULATION_PRIMARY, ProtocolViolation)

REQUIRED_FIELDS = BDD_SCHEMA

# Record 60A / Record 60A1: exactly the three BDD annotation flags whose missing
# values normalize to False. No other field is amended, and this tuple is the
# allowlist that keeps the amendment from broadening.
BDD_NULL_FALSE_FIELDS = ("attributes.crowd", "attributes.occluded",
                         "attributes.truncated")


def _finite(v) -> bool:
    try:
        return math.isfinite(float(v))
    except (TypeError, ValueError):
        return False


def _is_floating_nan(v) -> bool:
    """Narrow: a Python or NumPy *floating* scalar that is NaN, nothing else."""
    return isinstance(v, (float, np.floating)) and math.isnan(v)


def _as_amended_bool(v, field: str) -> bool:
    """Record 60A1 sec. 13 decision order, for the three amended flags only.

    Total over arbitrary objects: it returns a Python bool, returns False for an
    enumerated missing sentinel, or raises ``ProtocolViolation``. No value is
    evaluated for generic truthiness and no equality membership test is used, so
    ``pd.NA`` never reaches an ambiguous comparison.
    """
    if isinstance(v, bool):
        return v
    if isinstance(v, np.bool_):
        return bool(v)
    if v is None or v is pd.NA or v is pd.NaT:
        return False
    if _is_floating_nan(v):
        return False
    raise ProtocolViolation(
        "field %r carries a non-boolean value %r; Record 57 stop condition "
        "'invalid boolean semantics'" % (field, v))


def _as_bool(v, field: str) -> bool:
    """Booleans must already be boolean. Ambiguous encodings are a hard error.

    The three annotation flags frozen by Record 60A and clarified by Record 60A1
    additionally normalize an enumerated set of missing sentinels to False.
    Every other field keeps its historical behaviour byte-for-byte, including
    the historical acceptance of numeric 0/1 that Record 60A1 supersedes only
    for the amended fields.
    """
    if field in BDD_NULL_FALSE_FIELDS:
        return _as_amended_bool(v, field)
    if isinstance(v, bool):
        return v
    if v in (0, 1):
        return bool(v)
    raise ProtocolViolation(
        "field %r carries a non-boolean value %r; Record 57 stop condition "
        "'invalid boolean semantics'" % (field, v))


def row_is_valid(rec: Mapping) -> bool:
    """Record 57 sec. 2.3 row validity."""
    if not _as_bool(rec["haveVideo"], "haveVideo"):
        return False
    if _as_bool(rec["attributes.crowd"], "attributes.crowd"):
        return False
    if rec["category"] not in BDD_CATEGORIES:
        return False
    for f in ("box2d.x1", "box2d.x2", "box2d.y1", "box2d.y2"):
        if not _finite(rec[f]):
            return False
    if not float(rec["box2d.x2"]) > float(rec["box2d.x1"]):
        return False
    if not float(rec["box2d.y2"]) > float(rec["box2d.y1"]):
        return False
    return True


def classify(rec: Mapping) -> str:
    """Return 'target', 'anchor' or 'breaker' for one BDD record."""
    if not row_is_valid(rec):
        return "breaker"
    occ = _as_bool(rec["attributes.occluded"], "attributes.occluded")
    trunc = _as_bool(rec["attributes.truncated"], "attributes.truncated")
    if trunc:
        return "breaker"
    return "target" if occ else "anchor"


def to_canonical(rec: Mapping) -> CanonicalRow:
    role = classify(rec)
    valid = role != "breaker"
    x1 = float(rec["box2d.x1"]) if valid else None
    x2 = float(rec["box2d.x2"]) if valid else None
    y1 = float(rec["box2d.y1"]) if valid else None
    y2 = float(rec["box2d.y2"]) if valid else None
    diag = None
    if role == "target":
        w, h = x2 - x1, y2 - y1
        diag = math.sqrt(w * w + h * h)
        if not (math.isfinite(diag) and diag > 0):
            raise ProtocolViolation(
                "target bbox diagonal is not finite and positive")
    return CanonicalRow(
        population=POPULATION_PRIMARY,
        sequence_id=rec["videoName"], track_id=rec["id"],
        frame_index=rec["frameIndex"],
        x1=x1, y1=y1, x2=x2, y2=y2,
        target=(role == "target"), anchor=(role == "anchor"),
        breaker=(role == "breaker"),
        category=rec.get("category"),
        normalization_diagonal=diag,
        provenance={"name": rec.get("name")})


def rows_from_records(records: Iterable[Mapping]) -> List[CanonicalRow]:
    """Convert an iterable of BDD records. Used directly by synthetic tests."""
    return [to_canonical(r) for r in records]


def assert_schema(columns: Iterable[str]) -> None:
    missing = [c for c in REQUIRED_FIELDS if c not in set(columns)]
    if missing:
        raise ProtocolViolation("unexpected BDD schema; missing %r" % (missing,))


def parse_parquet(path: str = BDD_PATH, expected_sha256: str = BDD_SHA256):
    """Real-data entry point. Verifies the frozen digest before reading.

    Never called by the synthetic test suite.
    """
    import hashlib

    import pandas as pd

    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    got = h.hexdigest()
    if got != expected_sha256:
        raise ProtocolViolation(
            "BDD SHA mismatch: expected %s got %s" % (expected_sha256, got))
    df = pd.read_parquet(path)
    assert_schema(df.columns)
    return rows_from_records(df.to_dict("records"))
