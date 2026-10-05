"""Row-provenance analysis of a post-processing transformation.

Dataset-agnostic. Given the rows a producer emitted and the rows that survive
some downstream transformation, both keyed by a row identity, decide what the
transformation did: which rows it added, dropped, modified in place, or left
alone. The question this answers is whether a *row-subset* diagnostic ---
re-evaluating with only a chosen subset of the added rows --- is even well
defined, which it is not when the transformation rewrites rows it did not add.
"""
from typing import Dict, Hashable, Mapping, Sequence, Tuple

ROW_SUBSET_DEFINED = "DEFINED"
ROW_SUBSET_NOT_DEFINED = "NOT_DEFINED"
NON_ROW_ADDITIVE_TRANSFORMATION = "NON_ROW_ADDITIVE_TRANSFORMATION"

__all__ = ["diff_rows", "is_row_additive", "row_subset_diagnostic",
           "ROW_SUBSET_DEFINED", "ROW_SUBSET_NOT_DEFINED",
           "NON_ROW_ADDITIVE_TRANSFORMATION"]


def diff_rows(base: Mapping[Hashable, Sequence[float]],
              transformed: Mapping[Hashable, Sequence[float]],
              tolerance: float = 0.0) -> Dict[str, object]:
    """Classify every row identity of ``base`` and ``transformed``.

    ``tolerance`` is an absolute per-component bound; the default of exactly
    zero means a row counts as modified if any component changed at all.
    """
    if tolerance < 0:
        raise ValueError("tolerance must be non-negative")
    kb, kt = set(base), set(transformed)
    added, dropped, shared = sorted(kt - kb), sorted(kb - kt), kb & kt
    modified, unchanged = [], []
    for k in sorted(shared):
        a, b = tuple(base[k]), tuple(transformed[k])
        if len(a) != len(b):
            modified.append(k)
        elif any(abs(x - y) > tolerance for x, y in zip(a, b)):
            modified.append(k)
        else:
            unchanged.append(k)
    return {"base_rows": len(kb), "transformed_rows": len(kt),
            "added": added, "dropped": dropped,
            "modified": modified, "unchanged": unchanged,
            "n_added": len(added), "n_dropped": len(dropped),
            "n_modified": len(modified), "n_unchanged": len(unchanged),
            "n_shared": len(shared), "tolerance": float(tolerance)}


def is_row_additive(diff: Mapping[str, object]) -> bool:
    """True iff the transformation only appended rows."""
    return diff["n_dropped"] == 0 and diff["n_modified"] == 0


def row_subset_diagnostic(diff: Mapping[str, object]) -> Tuple[str, object]:
    """Whether a row-subset diagnostic state is definable for this transformation.

    Returns ``(status, reason)``. A non-row-additive transformation refits or
    rewrites rows it did not add, so removing a subset of the added rows would
    change the surviving rows too, and no subset state is well defined.
    """
    if is_row_additive(diff):
        return ROW_SUBSET_DEFINED, None
    return ROW_SUBSET_NOT_DEFINED, NON_ROW_ADDITIVE_TRANSFORMATION
