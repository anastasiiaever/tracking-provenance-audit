"""Canonical row identity and MOTChallenge parsing.

Frozen by 02_PROSPECTIVE_PROTOCOL.json: row identity is
(sequence, frame, track_id).  Coordinates, score, class and formatting are
carried separately.

NON_EVALUATED_METADATA_NORMALIZATION (protocol amendment A2, Sec. 5)
-------------------------------------------------------------------
A change confined to fields the frozen evaluator never reads is a metadata
normalization, not a rewrite of scientifically relevant content.  Verified by
tracing TrackEval at the frozen pin 12c8791b: for MOTChallenge2DBox the tracker
score (column 6) is parsed into `tracker_confidences`, is carried through
`get_preprocessed_seq_data` only by index deletion alongside removed rows, and
is read by NO metric implementation -- `hota.py`, `clear.py` and `identity.py`
contain no reference to it, and no file under `trackeval/metrics/` does.
Row removal (`to_remove_tracker`) is decided from similarity scores and
distractor classes, never from confidence.  Therefore a score change cannot
affect HOTA, DetA, AssA, IDF1, MOTA or MOT17 preprocessing, and does not violate
the scientifically relevant R0-subset-R2 invariant.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple

RowId = Tuple[str, int, int]          # (sequence, frame, track_id)
NON_EVALUATED_FIELDS = ("score",)   # under the frozen MOT17 evaluator semantics
COORD_TOL = 1e-6                      # writer round-trip tolerance only


@dataclass(frozen=True)
class Row:
    sequence: str
    frame: int
    track_id: int
    x: float
    y: float
    w: float
    h: float
    score: float
    cls: float
    extra: Tuple[float, ...]

    @property
    def rid(self) -> RowId:
        return (self.sequence, self.frame, self.track_id)

    @property
    def coords(self) -> Tuple[float, float, float, float]:
        return (self.x, self.y, self.w, self.h)

    def coords_equal(self, other: "Row") -> bool:
        return all(abs(a - b) <= COORD_TOL for a, b in zip(self.coords, other.coords))


class DuplicateRowIdentity(ValueError):
    """Two rows share a canonical row identity within one state."""


def parse_mot(text: str, sequence: str) -> Dict[RowId, Row]:
    """Parse MOTChallenge rows. Raises DuplicateRowIdentity on a repeated id."""
    out: Dict[RowId, Row] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        p = line.split(",")
        if len(p) < 6:
            raise ValueError(f"malformed MOT row: {line!r}")
        vals = [float(v) for v in p]
        row = Row(sequence, int(vals[0]), int(vals[1]),
                  vals[2], vals[3], vals[4], vals[5],
                  vals[6] if len(vals) > 6 else -1.0,
                  vals[7] if len(vals) > 7 else -1.0,
                  tuple(vals[8:]))
        if row.rid in out:
            raise DuplicateRowIdentity(f"duplicate row identity {row.rid}")
        out[row.rid] = row
    return out


def parse_gt(text: str, sequence: str, scoreable_only: bool = True) -> List[Row]:
    """Parse ground truth.

    Frozen scoreable predicate (02_PROSPECTIVE_PROTOCOL.json, MOT17 population):
    column 7 (flag) == 1 AND column 8 (class) == 1 (pedestrian).
    Visibility (column 9) is NOT thresholded.  GT may legitimately repeat a
    (frame, id) pair across ignore regions, so GT is returned as a list.
    """
    rows: List[Row] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        v = [float(x) for x in line.split(",")]
        flag = v[6] if len(v) > 6 else 1.0
        cls = v[7] if len(v) > 7 else 1.0
        if scoreable_only and not (int(flag) == 1 and int(cls) == 1):
            continue
        rows.append(Row(sequence, int(v[0]), int(v[1]), v[2], v[3], v[4], v[5],
                        flag, cls, tuple(v[8:])))
    return rows


def iou(a: Row, b: Row) -> float:
    ax2, ay2 = a.x + a.w, a.y + a.h
    bx2, by2 = b.x + b.w, b.y + b.h
    ix = max(0.0, min(ax2, bx2) - max(a.x, b.x))
    iy = max(0.0, min(ay2, by2) - max(a.y, b.y))
    inter = ix * iy
    union = a.w * a.h + b.w * b.h - inter
    return inter / union if union > 0 else 0.0
