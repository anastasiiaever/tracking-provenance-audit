"""Generic, domain-independent trajectory interpolation operators.

Deliberately isolated from ``reconstruction/`` (the frozen skeleton package):
nothing here imports skeleton code, and no skeleton hyperparameter is used.
"""
from .traj_ops import (  # noqa: F401
    OperatorUndefined,
    LinearInterp,
    NaturalCubicSpline,
    Pchip,
    OPERATORS,
    common_support_keys,
)
