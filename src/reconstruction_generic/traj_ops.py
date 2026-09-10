"""Three generic 1-D trajectory interpolation operators, no silent fallback.

Scope
-----
Each operator maps strictly-increasing observed times ``obs_t`` with values
``obs_v`` to values at query times ``tgt_t``. They are applied independently to
cx(t) and cy(t); nothing here is aware of skeletons, joints, bounding boxes or
any dataset.

No-fallback policy
------------------
Every operator either evaluates its own mathematics or raises
``OperatorUndefined``. None of them substitutes a different method when support
is small. This is the property the frozen skeleton spline does NOT have
(``reconstruction/utils.py::cubic_spline_1d`` returns ``np.interp`` whenever
fewer than four points are observed), which is why that implementation is not
reused here.

Minimum support, established empirically against the installed SciPy and frozen
before any BDD100K validation outcome (see the protocol record):

===================  ==========================  ================================
operator             minimum unique obs. times   routine
===================  ==========================  ================================
linear               2                           ``numpy.interp``
natural cubic spline 2                           ``scipy.interpolate.CubicSpline``
                                                 with ``bc_type="natural"``
PCHIP                2                           ``scipy.interpolate.PchipInterpolator``
===================  ==========================  ================================

Small-support behaviour of the natural cubic spline
---------------------------------------------------
At n = 2 the natural boundary conditions (S'' = 0 at both ends) force the cubic
and quadratic coefficients to vanish, so the interpolant coincides with the
straight line through the two points. This was verified directly from the
returned piecewise-polynomial coefficients. It is a mathematical consequence of
the operator's own boundary conditions, **not** a substitution of a different
algorithm: SciPy's special-cased ``n == 2`` / ``n == 3`` branches are guarded by
``bc_type in {'not-a-knot', 'periodic'}`` and are never entered for
``'natural'``. Frozen decision: this coincidence is PART OF THE OPERATOR and is
not counted as a fallback.

All operators reject duplicate or non-monotone observed times rather than
sorting or de-duplicating silently.
"""
from __future__ import annotations

from typing import Dict, Sequence

import numpy as np
from scipy.interpolate import CubicSpline, PchipInterpolator


class OperatorUndefined(Exception):
    """Raised when an operator is not mathematically defined for the input."""


def _validate(obs_t: np.ndarray, obs_v: np.ndarray, tgt_t: np.ndarray, min_pts: int) -> None:
    obs_t = np.asarray(obs_t, dtype=float)
    obs_v = np.asarray(obs_v, dtype=float)
    tgt_t = np.asarray(tgt_t, dtype=float)
    if obs_t.ndim != 1 or obs_v.ndim != 1 or obs_t.size != obs_v.size:
        raise OperatorUndefined("obs_t and obs_v must be 1-D and equal length")
    if not np.all(np.isfinite(obs_t)) or not np.all(np.isfinite(obs_v)):
        raise OperatorUndefined("non-finite observed input")
    if not np.all(np.isfinite(tgt_t)):
        raise OperatorUndefined("non-finite query time")
    if obs_t.size < min_pts:
        raise OperatorUndefined(f"needs >= {min_pts} observed points, got {obs_t.size}")
    if np.any(np.diff(obs_t) <= 0):
        raise OperatorUndefined("obs_t must be strictly increasing (no duplicates)")
    # strict interior: never extrapolate, in any operator
    if tgt_t.size and (tgt_t.min() <= obs_t[0] or tgt_t.max() >= obs_t[-1]):
        raise OperatorUndefined("query time is not strictly interior to observed support")


class _Operator:
    name = "abstract"
    min_points = 2

    def supports(self, obs_t, obs_v, tgt_t) -> bool:
        """True iff this operator is mathematically defined here. Never raises."""
        try:
            _validate(obs_t, obs_v, tgt_t, self.min_points)
        except OperatorUndefined:
            return False
        return True

    def __call__(self, obs_t, obs_v, tgt_t) -> np.ndarray:
        raise NotImplementedError


class LinearInterp(_Operator):
    """Piecewise-linear interpolation. Local stencil: the two bracketing points."""
    name = "linear"
    min_points = 2
    stencil = "local (two bracketing observations)"

    def __call__(self, obs_t, obs_v, tgt_t) -> np.ndarray:
        _validate(obs_t, obs_v, tgt_t, self.min_points)
        return np.interp(np.asarray(tgt_t, float), np.asarray(obs_t, float),
                         np.asarray(obs_v, float))


class NaturalCubicSpline(_Operator):
    """Natural cubic spline: S'' = 0 at both ends. Global stencil."""
    name = "natural_spline"
    min_points = 2
    stencil = "global (all observations in the segment)"

    def __call__(self, obs_t, obs_v, tgt_t) -> np.ndarray:
        _validate(obs_t, obs_v, tgt_t, self.min_points)
        cs = CubicSpline(np.asarray(obs_t, float), np.asarray(obs_v, float),
                         bc_type="natural", extrapolate=False)
        out = cs(np.asarray(tgt_t, float))
        if not np.all(np.isfinite(out)):
            raise OperatorUndefined("natural spline produced a non-finite value")
        return out


class Pchip(_Operator):
    """Shape-preserving piecewise cubic Hermite (PCHIP). Local-ish stencil."""
    name = "pchip"
    min_points = 2
    stencil = "local (monotone Hermite slopes from neighbouring observations)"

    def __call__(self, obs_t, obs_v, tgt_t) -> np.ndarray:
        _validate(obs_t, obs_v, tgt_t, self.min_points)
        pc = PchipInterpolator(np.asarray(obs_t, float), np.asarray(obs_v, float),
                               extrapolate=False)
        out = pc(np.asarray(tgt_t, float))
        if not np.all(np.isfinite(out)):
            raise OperatorUndefined("pchip produced a non-finite value")
        return out


OPERATORS: Dict[str, _Operator] = {
    op.name: op for op in (LinearInterp(), NaturalCubicSpline(), Pchip())
}


def common_support_keys(cases: Sequence[dict]) -> list:
    """Keys of cases on which EVERY operator is defined for both cx and cy.

    ``cases`` items need: ``key``, ``obs_t``, ``obs_cx``, ``obs_cy``, ``tgt_t``.
    Purely structural; consults no reconstruction error.
    """
    out = []
    for c in cases:
        ok = True
        for op in OPERATORS.values():
            if not (op.supports(c["obs_t"], c["obs_cx"], c["tgt_t"])
                    and op.supports(c["obs_t"], c["obs_cy"], c["tgt_t"])):
                ok = False
                break
        if ok:
            out.append(c["key"])
    return out
