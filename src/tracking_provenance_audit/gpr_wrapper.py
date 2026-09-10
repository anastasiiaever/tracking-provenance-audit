"""External reproducibility wrapper for the unmodified upstream OC-SORT GPR path.

Frozen seed 20260830 (02_PROSPECTIVE_PROTOCOL.json). Upstream scientific source
is NEVER edited; the wrapper only fixes externally controllable RNG state before
calling it.
"""
from __future__ import annotations
import hashlib, os, platform, random, sys
from typing import Callable, Optional

GPR_AUDIT_SEED = 20260830
REPRODUCIBILITY_FAILURE = "REPRODUCIBILITY_FAILURE"

# Stochastic APIs discoverable in tools/gp_interpolation.py.
STOCHASTIC_APIS = (
    "numpy.random.choice (median_trick)",
    "sklearn.gaussian_process.GaussianProcessRegressor(n_restarts_optimizer=2) "
    "optimizer restarts (draw from the NumPy global state; random_state is None upstream)",
)

# Externally controllable only before interpreter startup; verified irrelevant to
# the GPR scientific path by the fresh-process preflight.
UNCONTROLLED_FROM_INSIDE_PROCESS = ("PYTHONHASHSEED (CPython string-hash randomization)",)


def environment() -> dict:
    def ver(mod):
        try:
            return __import__(mod).__version__
        except Exception:
            return None
    return dict(python=platform.python_version(), numpy=ver("numpy"),
                sklearn=ver("sklearn"), scipy=ver("scipy"))


def seed_all(seed: int = GPR_AUDIT_SEED) -> None:
    """Fix every RNG that is externally controllable FROM INSIDE a running process.

    Controlled here: `random` and `numpy.random` global state. These are the
    generators the upstream GPR path actually reaches
    (`numpy.random.choice` in median_trick; the unseeded optimizer restarts of
    GaussianProcessRegressor, which draw from the NumPy global state).

    NOT controlled here: CPython's string-hash randomization. `PYTHONHASHSEED`
    only takes effect if it is set BEFORE interpreter startup; assigning it to
    os.environ inside an already-running interpreter does not change that
    interpreter's hash seed. We therefore do not set it and do not claim it.

    Empirically it does not matter: the fresh-process preflight
    (04_GPR_REPRODUCIBILITY_PREFLIGHT.md) ran the GPR path in four fresh
    interpreters, two of which had demonstrably DIFFERENT hash seeds, and all
    four produced byte-identical scientific output. Python hash randomization is
    irrelevant to this path, which uses numeric keys and NumPy arrays rather
    than str-keyed set/dict iteration.
    """
    random.seed(seed)
    try:
        import numpy as np
        np.random.seed(seed)
    except Exception:
        pass


def run_seeded(fn: Callable[[], object], seed: int = GPR_AUDIT_SEED) -> object:
    seed_all(seed)
    return fn()


def replay_verify(fn: Callable[[], object], seed: int = GPR_AUDIT_SEED,
                  digest: Optional[Callable[[object], str]] = None) -> dict:
    """One exact same-seed replay. NOT a second scientific trial.

    The replay result is never averaged or pooled with the first execution.
    """
    if digest is None:
        digest = lambda o: hashlib.sha256(repr(o).encode()).hexdigest()
    first = digest(run_seeded(fn, seed))
    second = digest(run_seeded(fn, seed))
    ok = first == second
    return dict(seed=seed, first_digest=first, replay_digest=second,
                reproducible=ok,
                status="REPRODUCIBLE" if ok else REPRODUCIBILITY_FAILURE,
                environment=environment(), stochastic_apis=list(STOCHASTIC_APIS),
                note=("replay is a reproducibility verification only; its values are "
                      "never averaged or pooled with the first execution"),
                licensed=("quantitative GPR claims are licensed" if ok else
                          "no quantitative GPR ranking claim is licensed"))


def upstream_source_sha256(path: str) -> str:
    return hashlib.sha256(open(path, "rb").read()).hexdigest()
