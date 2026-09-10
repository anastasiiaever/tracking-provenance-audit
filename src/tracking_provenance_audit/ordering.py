"""Pairwise ordering engine (protocol Sec. 11). Mechanical; no metric is computed here."""
from __future__ import annotations
from typing import Dict, List, Tuple

A_GREATER, TIE, A_LESS = "A_GREATER", "TIE", "A_LESS"
UNCHANGED, FLIP, TIE_CREATED, TIE_BROKEN = "UNCHANGED", "FLIP", "TIE_CREATED", "TIE_BROKEN"


def relation(a: float, b: float, tol: float = 0.0) -> str:
    if abs(a - b) <= tol:
        return TIE
    return A_GREATER if a > b else A_LESS


def transition(r0: str, r2: str) -> str:
    if r0 == r2:
        return UNCHANGED
    if r0 != TIE and r2 == TIE:
        return TIE_CREATED
    if r0 == TIE and r2 != TIE:
        return TIE_BROKEN
    return FLIP


def matrix(metrics_r0: Dict[str, Dict[str, float]],
           metrics_r2: Dict[str, Dict[str, float]],
           deployments: List[str], metrics: List[str]) -> List[dict]:
    """Every eligible pair x metric. All pairs are reported, not only flips."""
    out = []
    for i in range(len(deployments)):
        for j in range(i + 1, len(deployments)):
            A, B = deployments[i], deployments[j]
            for m in metrics:
                try:
                    r0 = relation(metrics_r0[A][m], metrics_r0[B][m])
                    r2 = relation(metrics_r2[A][m], metrics_r2[B][m])
                except KeyError:
                    out.append(dict(a=A, b=B, metric=m, r0=None, r2=None,
                                    transition="METRIC_NOT_AVAILABLE"))
                    continue
                out.append(dict(a=A, b=B, metric=m, r0=r0, r2=r2,
                                transition=transition(r0, r2)))
    return out


def summary(rows: List[dict]) -> dict:
    from collections import Counter
    c = Counter(r["transition"] for r in rows)
    pairs = {(r["a"], r["b"]) for r in rows}
    return dict(n_pairs=len(pairs), n_cells=len(rows),
                unchanged=c.get(UNCHANGED, 0), flips=c.get(FLIP, 0),
                ties_created=c.get(TIE_CREATED, 0), ties_broken=c.get(TIE_BROKEN, 0),
                metric_not_available=c.get("METRIC_NOT_AVAILABLE", 0))
