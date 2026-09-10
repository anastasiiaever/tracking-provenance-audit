"""Record 62A --- synthetic equivalence with the frozen trajectory pipeline.

The frozen Record 58/59C implementation is the reference for the semantics the
two share. It is imported read-only and never modified; if a mismatch appeared,
the correct response would be to stop and report it, not to bend either side.

No real BDD or MOT17 data is touched. Every fixture is built here.
"""
from __future__ import annotations

import math

import pytest

import applicability_audit as aa
from applicability_audit import aggregation as agg
from applicability_audit.applicability import (classify_segment, natural_runs,
                                               segment)
from applicability_audit.audit import _collect, _evaluate
from applicability_audit.cases import build_cases as tk_build_cases
from applicability_audit.serialization import key_repr
from applicability_audit.support import support_sets as tk_support_sets

# --- reference implementation, imported read-only for comparison only --------
from reconstruction_generic import OPERATORS, OperatorUndefined
from trajectory_cross_domain import canonical as fz_canonical
from trajectory_cross_domain import evaluate as fz_evaluate
from trajectory_cross_domain.protocol57 import GAP_GRID, OPERATOR_NAMES

SIZE = 10.0
DIAG = math.sqrt(SIZE * SIZE + SIZE * SIZE)

SPEC = [
    # (sequence, track, layout, {frame: centre offset})
    ("vA", 1, "ATATTATTTT", {1: 1.0, 3: 2.0, 4: 3.0, 6: 4.0}),
    ("vA", 2, "TTABTTT", {}),
    ("vB", 1, "ATTTAA", {1: 5.0, 2: 6.0, 3: 7.0}),
    ("vB", 2, "ATA", {1: 2.5}),
    ("vB", 3, "TTA", {}),
]
ROLE = {"A": "anchor", "T": "target", "B": "breaker"}


def frozen_rows():
    rows = []
    for seq, tid, layout, off in SPEC:
        for i, ch in enumerate(layout):
            role = ROLE[ch]
            if role == "breaker":
                rows.append(fz_canonical.CanonicalRow(
                    "syn", seq, tid, i, None, None, None, None,
                    False, False, True, "cat", None))
                continue
            c = off.get(i, 0.0)
            rows.append(fz_canonical.CanonicalRow(
                "syn", seq, tid, i, c - SIZE / 2, -SIZE / 2, c + SIZE / 2, SIZE / 2,
                role == "target", role == "anchor", False, "cat",
                DIAG if role == "target" else None))
    return rows


def toolkit_rows():
    rows = []
    for seq, tid, layout, off in SPEC:
        for i, ch in enumerate(layout):
            role = ROLE[ch]
            kw = {"sequence_id": seq, "population_id": "syn", "stratum": "cat"}
            kw[role] = True
            if role == "breaker":
                rows.append(aa.CanonicalObservation(tid, i, None, **kw))
                continue
            c = off.get(i, 0.0)
            rows.append(aa.CanonicalObservation(
                tid, i, (c, 0.0),
                metric_scale=(DIAG if role == "target" else None), **kw))
    return rows


def toolkit_method(name):
    """Wrap a frozen operator behind the generic method contract."""
    op = OPERATORS[name]

    def supports(mi):
        ox = [v[0] for v in mi.obs_v]
        oy = [v[1] for v in mi.obs_v]
        return bool(op.supports(list(mi.obs_t), ox, list(mi.tgt_t))
                    and op.supports(list(mi.obs_t), oy, list(mi.tgt_t)))

    def reconstruct(mi):
        ox = [v[0] for v in mi.obs_v]
        oy = [v[1] for v in mi.obs_v]
        try:
            cx = op(list(mi.obs_t), ox, list(mi.tgt_t))
            cy = op(list(mi.obs_t), oy, list(mi.tgt_t))
        except OperatorUndefined:             # pragma: no cover - defensive
            return None
        return [(float(cx[i]), float(cy[i])) for i in range(len(mi.tgt_t))]

    return aa.MethodContract(name, supports, reconstruct)


CONTRACT = aa.ApplicabilityContract(run_length_grid=GAP_GRID)
LADDER = agg.frozen_trajectory_ladder(GAP_GRID)
METHODS = [toolkit_method(n) for n in OPERATOR_NAMES]
FIELD_MAP = {"normalized": "normalized", "raw": "raw_pixel"}


# ------------------------------------------------------- reference pipeline
def frozen_pipeline():
    """Reproduce the frozen corpus pass using frozen primitives only."""
    counts = {c: 0 for c in ("eligible", "leading", "trailing", "no_anchor")}
    scoreable = 0
    runs = {g: 0 for g in GAP_GRID}
    off_grid = 0
    total_runs = 0
    cases = []
    grouped = fz_canonical.group_trajectories(frozen_rows())
    for key in sorted(grouped, key=lambda k: tuple(str(p) for p in k)):
        for seg in fz_canonical.segment_trajectory(grouped[key]):
            classes = fz_canonical.classify_gate_1r(seg)
            for r in seg:
                if not r.target:
                    continue
                counts[classes[r.frame_index]] += 1
                scoreable += 1
            for run in fz_canonical.natural_runs(seg):
                total_runs += 1
                if fz_canonical.on_grid(run):
                    runs[len(run)] += 1
                else:
                    off_grid += 1
            cases.extend(fz_canonical.build_cases(seg))
    sets = fz_evaluate.support_sets(cases)
    evaluated = {}
    for name in OPERATOR_NAMES:
        per = {}
        for c in cases:
            if c["key"] not in sets["B"][name]:
                continue
            pred = fz_evaluate.reconstruct(c, name)
            if pred is fz_evaluate.UNDEFINED:  # pragma: no cover - defensive
                continue
            if not fz_evaluate.normalization_valid(c):
                continue
            per[c["key"]] = {"errors": fz_evaluate.target_errors(c, pred),
                             "case": c}
        evaluated[name] = per
    return {"counts": counts, "scoreable": scoreable, "runs": runs,
            "off_grid": off_grid, "total_runs": total_runs,
            "cases": cases, "sets": sets, "evaluated": evaluated}


def frozen_estimate(ref, name, keys, field):
    recs = []
    for key in keys:
        entry = ref["evaluated"][name][key]
        recs.append({"sequence_id": entry["case"]["sequence_id"],
                     "gap_length": entry["case"]["gap_length"],
                     "errors": entry["errors"]})
    return fz_evaluate.aggregate(recs, field)


@pytest.fixture(scope="module")
def both():
    ref = frozen_pipeline()
    tk = aa.run_applicability_audit(toolkit_rows(), METHODS, CONTRACT, LADDER)
    return ref, tk


# -------------------------------------------------------------- equivalence
def test_the_fixture_actually_exercises_every_class_and_an_off_grid_run(both):
    ref, _ = both
    assert all(v > 0 for v in ref["counts"].values())
    assert ref["off_grid"] > 0 and len(ref["cases"]) > 0


def test_applicability_partition_matches_the_frozen_gate(both):
    ref, tk = both
    assert tk["applicability"]["counts"] == ref["counts"]
    assert tk["population"]["scoreable_targets"] == ref["scoreable"]


def test_segment_and_class_semantics_match_case_by_case():
    fz_grouped = fz_canonical.group_trajectories(frozen_rows())
    tk_grouped = {}
    for o in toolkit_rows():
        tk_grouped.setdefault((o.population_id, o.sequence_id, o.trajectory_id),
                              []).append(o)
    for key in fz_grouped:
        tk_rows = sorted(tk_grouped[key], key=lambda o: o.frame_index)
        fz_segs = fz_canonical.segment_trajectory(fz_grouped[key])
        tk_segs = segment(tk_rows, CONTRACT)
        assert [len(s) for s in fz_segs] == [len(s) for s in tk_segs]
        for fs, ts in zip(fz_segs, tk_segs):
            assert fz_canonical.classify_gate_1r(fs) == classify_segment(ts)
            assert ([len(r) for r in fz_canonical.natural_runs(fs)]
                    == [len(r) for r in natural_runs(ts)])


def test_natural_run_inventory_matches(both):
    ref, tk = both
    assert tk["natural_runs"]["by_grid_length"] == {str(g): ref["runs"][g]
                                                    for g in sorted(ref["runs"])}
    assert tk["natural_runs"]["off_grid"] == ref["off_grid"]
    assert tk["natural_runs"]["total"] == ref["total_runs"]


def test_case_keys_match_exactly(both):
    ref, tk = both
    frozen_keys = sorted(key_repr(c["key"]) for c in ref["cases"])
    toolkit_keys = sorted(row["case_id"] for row in tk["case_table"])
    assert frozen_keys == toolkit_keys


def test_support_sets_a_b_c_d_match(both):
    ref, tk = both
    assert tk["cases"]["admitted_A"] == len(ref["sets"]["A"])
    assert tk["metric_validity"]["C"] == len(ref["sets"]["C"])
    assert tk["common_support"]["D"] == len(ref["sets"]["D"])
    for name in OPERATOR_NAMES:
        assert tk["method_support"][name] == len(ref["sets"]["B"][name])
    assert (sorted(key_repr(k) for k in ref["sets"]["D"])
            == sorted(row["case_id"] for row in tk["case_table"]
                      if row["common_support"]))


def test_support_retention_matches(both):
    ref, tk = both
    expected = len(ref["sets"]["D"]) / float(len(ref["sets"]["A"]))
    assert tk["support_retention"] == pytest.approx(expected)


@pytest.mark.parametrize("field", ["normalized", "raw"])
def test_common_support_estimates_match(both, field):
    ref, tk = both
    for name in OPERATOR_NAMES:
        frozen = frozen_estimate(ref, name, sorted(
            ref["sets"]["D"], key=lambda k: tuple(str(p) for p in k)),
            FIELD_MAP[field])["headline"]
        toolkit = tk["common_support_estimates"][name][field]["headline"]
        assert toolkit == pytest.approx(frozen, rel=1e-12)


@pytest.mark.parametrize("field", ["normalized", "raw"])
def test_method_specific_estimates_and_shifts_match(both, field):
    ref, tk = both
    for name in OPERATOR_NAMES:
        own = set(ref["sets"]["A"]) & ref["sets"]["C"] & ref["sets"]["B"][name]
        frozen_own = frozen_estimate(ref, name, sorted(
            own, key=lambda k: tuple(str(p) for p in k)),
            FIELD_MAP[field])["headline"]
        assert tk["method_specific_estimates"][name][field]["headline"] == \
            pytest.approx(frozen_own, rel=1e-12)
        frozen_common = frozen_estimate(ref, name, sorted(
            ref["sets"]["D"], key=lambda k: tuple(str(p) for p in k)),
            FIELD_MAP[field])["headline"]
        assert tk["support_shift"][name][field] == pytest.approx(
            frozen_common - frozen_own, abs=1e-15)


def test_aggregation_cells_and_per_sequence_means_match(both):
    ref, tk = both
    keys = sorted(ref["sets"]["D"], key=lambda k: tuple(str(p) for p in k))
    for name in OPERATOR_NAMES:
        frozen = frozen_estimate(ref, name, keys, "normalized")
        levels = tk["common_support_estimates"][name]["normalized"]["levels"]
        cells = levels[0]["groups"]
        seqs = levels[1]["groups"]
        for vid, entry in frozen["per_video"].items():
            assert seqs[vid] == pytest.approx(entry["video_mean"], rel=1e-12)
            for g, v in entry["cells"].items():
                assert cells["%s|%d" % (vid, g)] == pytest.approx(v, rel=1e-12)


def test_contributing_units_per_grid_length_match(both):
    ref, tk = both
    keys = sorted(ref["sets"]["D"], key=lambda k: tuple(str(p) for p in k))
    frozen = frozen_estimate(ref, OPERATOR_NAMES[0], keys,
                             "normalized")["contributing_videos_per_gap_length"]
    toolkit = tk["aggregation"]["contributing_units_per_reported_grid_length"]
    assert toolkit == {str(g): n for g, n in frozen.items()}


def test_structured_unavailable_matches_where_the_frozen_side_has_none():
    """An anchorless corpus: frozen headline is None, toolkit says unavailable."""
    rows = [aa.CanonicalObservation(1, i, (0.0, 0.0), target=True,
                                    sequence_id="v", population_id="syn",
                                    metric_scale=DIAG) for i in range(3)]
    tk = aa.run_applicability_audit(rows, METHODS, CONTRACT, LADDER)
    assert tk["cases"]["admitted_A"] == 0
    assert aa.is_unavailable(tk["support_retention"])
    frozen_headline = fz_evaluate.aggregate([], "normalized")["headline"]
    assert frozen_headline is None
    for name in OPERATOR_NAMES:
        assert aa.is_unavailable(
            tk["common_support_estimates"][name]["normalized"]["headline"])


def test_the_frozen_reference_was_not_modified():
    """The released operator and canonicalisation code is the frozen code.

    Paths were rebased for this release (``scripts/`` -> ``src/``); the digests
    below are the frozen ones and are unchanged.

    ``evaluate.py`` is the one exception and is checked separately. In the
    research tree it injected the repository root into ``sys.path`` to reach
    ``reconstruction_generic``; in this layout both packages are siblings under
    ``src/`` and the plain import resolves them. That edit is confined to the
    import block -- the assertions below pin its frozen digest, its released
    digest, and the fact that no path manipulation survives. Every operator,
    metric, support rule and ladder in the file is untouched, which is what the
    equivalence tests above actually exercise.
    """
    import hashlib
    import os

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def digest(rel):
        with open(os.path.join(root, rel), "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()

    unmodified = {
        "src/trajectory_cross_domain/canonical.py":
            "74bb5b9646f15a896d5178487a8d5dd63e2741349532f809c9fbd3e945c20942",
        "src/reconstruction_generic/traj_ops.py":
            "01719f05c7086448b2b9ac00fc7d1be3d3ab498fa1bc7147112d221ae185094b"}
    for path, want in unmodified.items():
        assert digest(path) == want, path

    FROZEN_EVALUATE = "918bc550d7a781701b8a30c63163680593c01673f3fc4862ae5e33dd8dd45bd5"
    RELEASED_EVALUATE = "4d274356a85eba6c4faa875de90364c5cdddced779d693a91b3a1aaa0cdfddf5"
    got = digest("src/trajectory_cross_domain/evaluate.py")
    assert got != FROZEN_EVALUATE, "evaluate.py was expected to carry the release import block"
    assert got == RELEASED_EVALUATE, "evaluate.py drifted from the released revision"

    with open(os.path.join(root, "src/trajectory_cross_domain/evaluate.py")) as fh:
        text = fh.read()
    assert "sys.path.insert" not in text and "\nimport sys" not in text
    assert "from reconstruction_generic import OPERATORS, OperatorUndefined" in text
