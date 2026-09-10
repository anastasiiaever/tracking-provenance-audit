"""State construction: R1 (row-additive only) and S0/S2 structural analysis."""
from __future__ import annotations
from typing import Dict, List
from .rowid import Row, RowId
from .stv import SEMANTICALLY_ADMITTED
from .transitions import Transitions

R1_STRUCTURALLY_UNDEFINED = "STRUCTURALLY_UNDEFINED"
R1_UNAVAILABLE = "STRUCTURAL_DECOMPOSITION_UNAVAILABLE"
R1_CONSTRUCTED = "R1_CONSTRUCTED"


def build_R1(r0: Dict[RowId, Row], r2: Dict[RowId, Row],
             classes: Dict[RowId, str]) -> Dict[RowId, Row]:
    """R1 = all R0 rows + SEMANTICALLY_ADMITTED synthesized rows.

    Enforces R0 subset R1 subset R2 by canonical row identity.
    """
    r1 = dict(r0)
    for rid, cls in classes.items():
        if cls == SEMANTICALLY_ADMITTED:
            r1[rid] = r2[rid]
    assert set(r0) <= set(r1) <= set(r2), "R0 subset R1 subset R2 violated"
    return r1


def r1_status_for_non_row_additive(family: str) -> tuple:
    """Non-row-additive families never receive an R1 analogue.

    GPR_REWRITE and LINK_PLUS_SMOOTHING both rewrite values that their own
    regression/smoothing fit consumes, so removing a subset of generated rows
    would alter the fit itself. A row-subset causal decomposition is therefore
    STRUCTURALLY_UNDEFINED; no artificial intervention is synthesized.
    """
    reason = {
        "GPR_REWRITE":
            "the GPR stage consumes the linear-interpolated rows as its own "
            "regression input; removing a subset would alter the fit",
        "LINK_PLUS_SMOOTHING":
            "Gaussian smoothing refits every row of every track, so removing a "
            "subset would alter the smoothing fit and the surviving rows",
    }.get(family, "non-row-additive transformation")
    return (R1_STRUCTURALLY_UNDEFINED, reason)
