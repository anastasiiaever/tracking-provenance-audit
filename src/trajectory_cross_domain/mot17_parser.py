"""MOT17 training ground truth -> canonical rows (Record 57 sec. 3).

Only the DPM copy of each of the seven base sequences is read. The classification
logic is pure and synthetic-testable; :func:`parse_zip` is the only function that
touches the archive and it verifies the frozen SHA256 first.
"""
from __future__ import annotations

import math
from typing import Iterable, List, Mapping, Tuple

from .canonical import CanonicalRow
from .protocol57 import (MOT17_CANONICAL_DIRS, MOT17_PATH,
                         MOT17_PEDESTRIAN_CLASS, MOT17_REQUIRED_MARK,
                         MOT17_SHA256, POPULATION_SECONDARY, ProtocolViolation)

GT_FIELDS = ("frame", "id", "x", "y", "w", "h", "mark", "class", "visibility")


def _finite(v) -> bool:
    try:
        return math.isfinite(float(v))
    except (TypeError, ValueError):
        return False


def check_visibility(v) -> float:
    """Parser-level numeric sanity check only. No tolerance, no threshold search."""
    if not _finite(v):
        raise ProtocolViolation("MOT17 visibility is not finite: %r" % (v,))
    f = float(v)
    if f < 0.0 or f > 1.0:
        raise ProtocolViolation("MOT17 visibility outside [0,1]: %r" % (f,))
    return f


def row_is_valid(rec: Mapping) -> bool:
    """Record 57 sec. 3.1 valid population (visibility range checked separately)."""
    if int(rec["mark"]) != MOT17_REQUIRED_MARK:
        return False
    if int(rec["class"]) != MOT17_PEDESTRIAN_CLASS:
        return False
    for f in ("x", "y", "w", "h"):
        if not _finite(rec[f]):
            return False
    if not float(rec["w"]) > 0 or not float(rec["h"]) > 0:
        return False
    return True


def inside_image(rec: Mapping, im_width: float, im_height: float) -> bool:
    """Record 57 sec. 3.2 boundary guard. No extra pixel margin."""
    x, y = float(rec["x"]), float(rec["y"])
    w, h = float(rec["w"]), float(rec["h"])
    return x > 0 and y > 0 and (x + w) < im_width and (y + h) < im_height


def classify(rec: Mapping, im_width: float, im_height: float) -> str:
    if not row_is_valid(rec):
        return "breaker"
    vis = check_visibility(rec["visibility"])
    if not inside_image(rec, im_width, im_height):
        return "breaker"
    return "target" if vis < 1.0 else "anchor"


def to_canonical(rec: Mapping, sequence_id: str,
                 im_width: float, im_height: float) -> CanonicalRow:
    role = classify(rec, im_width, im_height)
    valid = role != "breaker"
    x1 = float(rec["x"]) if valid else None
    y1 = float(rec["y"]) if valid else None
    x2 = (float(rec["x"]) + float(rec["w"])) if valid else None
    y2 = (float(rec["y"]) + float(rec["h"])) if valid else None
    diag = None
    if role == "target":
        w, h = float(rec["w"]), float(rec["h"])
        diag = math.sqrt(w * w + h * h)
        if not (math.isfinite(diag) and diag > 0):
            raise ProtocolViolation("target bbox diagonal is not finite and positive")
    return CanonicalRow(
        population=POPULATION_SECONDARY, sequence_id=sequence_id,
        track_id=rec["id"], frame_index=rec["frame"],
        x1=x1, y1=y1, x2=x2, y2=y2,
        target=(role == "target"), anchor=(role == "anchor"),
        breaker=(role == "breaker"),
        category="pedestrian",
        normalization_diagonal=diag,
        provenance={"visibility": rec.get("visibility")})


def rows_from_records(records: Iterable[Mapping], sequence_id: str,
                      im_width: float, im_height: float) -> List[CanonicalRow]:
    return [to_canonical(r, sequence_id, im_width, im_height) for r in records]


def parse_seqinfo(text: str) -> Tuple[int, int]:
    """Extract imWidth/imHeight from a seqinfo.ini body."""
    vals = {}
    for line in text.splitlines():
        if "=" in line:
            k, _, v = line.partition("=")
            vals[k.strip()] = v.strip()
    try:
        return int(vals["imWidth"]), int(vals["imHeight"])
    except (KeyError, ValueError):
        raise ProtocolViolation("malformed seqinfo.ini: imWidth/imHeight missing")


def parse_gt_line(line: str) -> dict:
    parts = line.strip().split(",")
    if len(parts) < 9:
        raise ProtocolViolation("malformed MOT17 gt line: %r" % (line,))
    return {"frame": int(parts[0]), "id": int(parts[1]),
            "x": float(parts[2]), "y": float(parts[3]),
            "w": float(parts[4]), "h": float(parts[5]),
            "mark": int(parts[6]), "class": int(parts[7]),
            "visibility": float(parts[8])}


def parse_zip(path: str = MOT17_PATH, expected_sha256: str = MOT17_SHA256):
    """Real-data entry point. Verifies the frozen digest before reading.

    Reads only the DPM copy of each of the seven base sequences.
    Never called by the synthetic test suite.
    """
    import hashlib
    import zipfile

    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    got = h.hexdigest()
    if got != expected_sha256:
        raise ProtocolViolation(
            "MOT17 SHA mismatch: expected %s got %s" % (expected_sha256, got))
    rows = []
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        for d in MOT17_CANONICAL_DIRS:
            gt = [n for n in names if n.endswith("%s/gt/gt.txt" % d)]
            info = [n for n in names if n.endswith("%s/seqinfo.ini" % d)]
            if len(gt) != 1 or len(info) != 1:
                raise ProtocolViolation(
                    "canonical MOT17 directory %s is not uniquely resolvable" % d)
            iw, ih = parse_seqinfo(z.read(info[0]).decode("utf-8", "replace"))
            recs = [parse_gt_line(l) for l in
                    z.read(gt[0]).decode("utf-8", "replace").splitlines() if l.strip()]
            rows.extend(rows_from_records(recs, d.rsplit("-", 1)[0], iw, ih))
    return rows
