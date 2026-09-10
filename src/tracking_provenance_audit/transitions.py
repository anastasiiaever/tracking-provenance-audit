"""Row transition inventory and the row-additive invariant (protocol Sec. 4, 3)."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Dict, List
from .rowid import Row, RowId


@dataclass
class Transitions:
    n_R0_rows: int
    n_R2_rows: int
    inserted_rows: int
    deleted_rows: int
    rewritten_coordinate_rows: int
    uniquely_attributable_ID_rewrites: int
    id_change_attribution_ambiguous: int
    unchanged_existing_rows: int
    inserted_ids: List[RowId] = field(default_factory=list)
    deleted_ids: List[RowId] = field(default_factory=list)
    coordinate_rewritten_ids: List[RowId] = field(default_factory=list)
    subset_R0_in_R2: bool = True

    def to_dict(self) -> dict:
        d = asdict(self)
        for k in ("inserted_ids", "deleted_ids", "coordinate_rewritten_ids"):
            d[k] = [list(x) for x in sorted(d[k])]
        return d


def inventory(r0: Dict[RowId, Row], r2: Dict[RowId, Row]) -> Transitions:
    """Explicit state difference. Synthesis is never inferred from frame gaps.

    ID-rewrite accounting (protocol amendment A2, Sec. 6): because canonical row
    identity contains track_id, a track-id change cannot be observed within one
    identity; it appears as a deletion plus an insertion. Pairing them is only
    licensed when it is UNAMBIGUOUS: exactly one deletion and exactly one
    insertion at the same (sequence, frame), with identical coordinates. Any
    other configuration is reported as ambiguous. No matching between old and
    new tracker rows is ever invented.
    """
    ins = sorted(set(r2) - set(r0))
    dele = sorted(set(r0) - set(r2))
    common = sorted(set(r0) & set(r2))
    coord_rw = [i for i in common if not r0[i].coords_equal(r2[i])]

    by_fr_del: Dict[tuple, List[RowId]] = {}
    by_fr_ins: Dict[tuple, List[RowId]] = {}
    for rid in dele:
        by_fr_del.setdefault(rid[:2], []).append(rid)
    for rid in ins:
        by_fr_ins.setdefault(rid[:2], []).append(rid)

    unique_id_rw, ambiguous = 0, 0
    for fr in set(by_fr_del) | set(by_fr_ins):
        d, i = by_fr_del.get(fr, []), by_fr_ins.get(fr, [])
        if not d:
            continue                      # pure insertions: not an ID rewrite
        if len(d) == 1 and len(i) == 1 and r0[d[0]].coords_equal(r2[i[0]]):
            unique_id_rw += 1             # unambiguous 1-to-1 with equal geometry
        else:
            ambiguous += len(d)           # attribution unavailable; never fabricated

    return Transitions(
        n_R0_rows=len(r0), n_R2_rows=len(r2),
        inserted_rows=len(ins), deleted_rows=len(dele),
        rewritten_coordinate_rows=len(coord_rw),
        uniquely_attributable_ID_rewrites=unique_id_rw,
        id_change_attribution_ambiguous=ambiguous,
        unchanged_existing_rows=len(common) - len(coord_rw),
        inserted_ids=ins, deleted_ids=dele, coordinate_rewritten_ids=coord_rw,
        subset_R0_in_R2=not dele,
    )


class RowAdditiveViolation(Exception):
    def __init__(self, reason_code: str, detail: str):
        self.reason_code = reason_code
        self.detail = detail
        super().__init__(f"{reason_code}: {detail}")


def assert_row_additive(t: Transitions) -> None:
    """Raise if the row-additive invariant R0 subset R2 (values preserved) fails.

    On failure the caller must emit STRUCTURAL_DECOMPOSITION_UNAVAILABLE and
    must NOT construct R1.
    """
    if t.deleted_rows:
        raise RowAdditiveViolation(
            "STRUCTURAL_DECOMPOSITION_UNAVAILABLE",
            f"{t.deleted_rows} R0 row identities absent from R2")
    if t.rewritten_coordinate_rows:
        raise RowAdditiveViolation(
            "STRUCTURAL_DECOMPOSITION_UNAVAILABLE",
            f"{t.rewritten_coordinate_rows} pre-existing rows have rewritten coordinates")
