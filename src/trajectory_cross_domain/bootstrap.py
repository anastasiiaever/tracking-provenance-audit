"""Video-clustered finite-subset stability bootstrap (Record 57 sec. 11).

This is NOT a confidence interval. One frozen seed, one replicate count, and the
same resampled video multiset is used for every compared method in a replicate.
"""
from __future__ import annotations

from typing import Callable, Dict, List, Sequence

import numpy as np

from .protocol57 import (BOOTSTRAP_IS_CONFIDENCE_INTERVAL, BOOTSTRAP_REPLICATES,
                         BOOTSTRAP_SEED, ProtocolViolation)


def draw_clusters(clusters: Sequence[str], replicates: int = BOOTSTRAP_REPLICATES,
                  seed: int = BOOTSTRAP_SEED) -> np.ndarray:
    """One index matrix, reused by every method so replicates stay paired."""
    if not len(clusters):
        raise ProtocolViolation("cannot bootstrap an empty cluster frame")
    rng = np.random.default_rng(seed)
    return rng.integers(0, len(clusters), size=(replicates, len(clusters)))


def paired_stability(clusters: Sequence[str],
                     per_method_video_values: Dict[str, Dict[str, float]],
                     replicates: int = BOOTSTRAP_REPLICATES,
                     seed: int = BOOTSTRAP_SEED) -> Dict[str, object]:
    """Percentile stability bands over the observed subset, paired across methods."""
    clusters = list(clusters)
    draws = draw_clusters(clusters, replicates, seed)
    out = {}
    for name, vals in per_method_video_values.items():
        v = np.array([vals.get(c, np.nan) for c in clusters], dtype=float)
        taken = v[draws]
        ok = ~np.isnan(taken)
        cnt = ok.sum(axis=1)
        tot = np.where(ok, taken, 0.0).sum(axis=1)
        good = cnt > 0
        means = tot[good] / cnt[good]
        out[name] = {
            "lo": float(np.percentile(means, 2.5)),
            "hi": float(np.percentile(means, 97.5)),
            "n_replicates": int(replicates),
            "n_empty_draws": int((~good).sum()),
            "seed": seed,
            "cluster_unit": "videoName",
            "is_confidence_interval": BOOTSTRAP_IS_CONFIDENCE_INTERVAL,
            "interpretation": "cluster-resampling stability interval over this "
                              "observed subset; not a superpopulation interval"}
    return {"clusters": clusters, "paired": True, "methods": out}
