"""Record 62A --- synthetic validation of the reusable applicability audit.

Every fixture here is built in-process and is understandable without knowing
anything about BDD, MOT17 or skeletons. The equivalence tests import the frozen
trajectory implementation as a *reference* and never modify it; no real dataset
is opened anywhere in this module.
"""
from __future__ import annotations

import json
import math
import random

import pytest

import applicability_audit as aa
from applicability_audit import aggregation as agg
from applicability_audit.applicability import (classify_segment, natural_runs,
                                               segment, select_population)
from applicability_audit.audit import run_applicability_audit
from applicability_audit.cases import build_cases
from applicability_audit.contracts import AuditContractError
from applicability_audit.support import (metric_valid, support_sets,
                                         method_specific_support,
                                         support_retention)

GRID = (1, 2, 3)
SCALE = 10.0
ROLE = {"A": "anchor", "T": "target", "B": "breaker"}


# ------------------------------------------------------------------ fixtures
def obs(seq, traj, frame, role, value=0.0, scale=SCALE, stratum=None,
        scoreable=True, population="p"):
    kw = {"sequence_id": seq, "population_id": population, "stratum": stratum,
          "scoreable": scoreable}
    kw[ROLE[role]] = True
    if role == "B":
        return aa.CanonicalObservation(traj, frame, None, **kw)
    return aa.CanonicalObservation(
        traj, frame, (float(value), 0.0),
        metric_scale=(scale if role == "T" else None), **kw)


def trajectory(seq, traj, layout, values=None, scales=None, stratum=None,
               population="p"):
    """Build one trajectory from a layout string of A/T/B, one char per frame."""
    values = values or {}
    scales = scales or {}
    return [obs(seq, traj, i, ch, values.get(i, 0.0),
                scales.get(i, SCALE), stratum, population=population)
            for i, ch in enumerate(layout)]


def reference_corpus():
    """Multiple trajectories covering every applicability class and support case.

    vA/t1  A T A T T A T T T T   eligible run of 1, eligible run of 2,
                                 trailing off-grid run of 4
    vA/t2  T T A B T T T         leading pair, breaker, anchorless segment
    vB/t1  A T T A A             eligible run of 2 in a second group
    vB/t2  T T A                 targets with no reconstruction support
    """
    rows = []
    rows += trajectory("vA", "t1", "ATATTATTTT", stratum="alpha")
    rows += trajectory("vA", "t2", "TTABTTT", stratum="beta")
    rows += trajectory("vB", "t1", "ATTAA", stratum="alpha")
    rows += trajectory("vB", "t2", "TTA", stratum="gamma")
    return rows


def contract(grid=GRID):
    return aa.ApplicabilityContract(run_length_grid=grid)


def linear_predict(mi):
    """Toy interpolation: linear in the first component, zero in the second."""
    out = []
    for t in mi.tgt_t:
        lo = max([i for i, o in enumerate(mi.obs_t) if o < t], default=0)
        hi = min([i for i, o in enumerate(mi.obs_t) if o > t], default=len(mi.obs_t) - 1)
        t0, t1 = mi.obs_t[lo], mi.obs_t[hi]
        v0, v1 = mi.obs_v[lo][0], mi.obs_v[hi][0]
        w = 0.0 if t1 == t0 else (t - t0) / float(t1 - t0)
        out.append((v0 + w * (v1 - v0), 0.0))
    return out


def constant_predict(offset):
    def _f(mi):
        return [(offset, 0.0) for _ in mi.tgt_t]
    return _f


def method(mid, supports=None, reconstruct=None):
    return aa.MethodContract(mid, supports or (lambda mi: mi.n_anchors >= 2),
                             reconstruct or linear_predict)


def three_methods():
    return [method("method_all"),
            method("method_all_2", reconstruct=constant_predict(0.5)),
            method("method_restricted",
                   supports=lambda mi: mi.n_anchors >= 2 and mi.run_length != 2)]


def audit(rows=None, methods=None, grid=GRID, aggregation=None, **kw):
    return run_applicability_audit(
        rows if rows is not None else reference_corpus(),
        three_methods() if methods is None else methods,
        contract(grid),
        aggregation or agg.frozen_trajectory_ladder(grid),
        **kw)


# ------------------------------------------------- layer 1: population
def test_non_scoreable_observations_leave_the_population():
    rows = trajectory("v", "t", "ATA")
    rows.append(obs("v", "t", 9, "T", scoreable=False))
    kept, dropped = select_population(rows)
    assert dropped == 1 and len(kept) == 3
    r = audit(rows=rows, methods=[method("m")])
    assert r["population"]["non_scoreable_dropped"] == 1
    assert r["population"]["scoreable_targets"] == 1


def test_an_observation_must_have_exactly_one_role():
    with pytest.raises(AuditContractError, match="exactly one"):
        aa.CanonicalObservation("t", 0, (0.0, 0.0), target=True, anchor=True)
    with pytest.raises(AuditContractError, match="exactly one"):
        aa.CanonicalObservation("t", 0, (0.0, 0.0))


def test_duplicate_trajectory_frame_is_a_hard_failure():
    rows = trajectory("v", "t", "ATA") + [obs("v", "t", 1, "T")]
    with pytest.raises(AuditContractError, match="duplicate trajectory-frame"):
        audit(rows=rows, methods=[method("m")])


# --------------------------------------------- layer 2: exact partition
def test_the_four_classes_partition_the_scoreable_targets_exactly():
    r = audit()
    app = r["applicability"]
    c = app["counts"]
    assert c == {"eligible": 5, "leading": 4, "trailing": 4, "no_anchor": 3}
    assert sum(c.values()) == r["population"]["scoreable_targets"] == 16
    assert app["exact_partition_verified"] is True
    assert sum(app["fractions"].values()) == pytest.approx(1.0)


@pytest.mark.parametrize("layout,expected", [
    ("ATA", {"eligible": 1}), ("TTA", {"leading": 2}),
    ("ATT", {"trailing": 2}), ("TTT", {"no_anchor": 3})])
def test_each_applicability_class_in_isolation(layout, expected):
    r = audit(rows=trajectory("v", "t", layout), methods=[method("m")])
    counts = r["applicability"]["counts"]
    for k, v in expected.items():
        assert counts[k] == v
    assert sum(counts.values()) == sum(expected.values())


def test_classes_are_mutually_exclusive():
    seg = trajectory("v", "t", "ATATA")
    classes = classify_segment(seg)
    assert set(classes.values()) <= set(aa.APPLICABILITY_CLASSES)
    assert len(classes) == 2


def test_a_breaker_splits_continuity_and_is_never_bridged():
    rows = trajectory("v", "t", "ATBTA")
    segs = segment(rows, contract())
    assert len(segs) == 2
    assert all(not o.breaker for s in segs for o in s)
    r = audit(rows=rows, methods=[method("m")])
    assert r["applicability"]["counts"] == {"eligible": 0, "leading": 1,
                                            "trailing": 1, "no_anchor": 0}


def test_a_missing_frame_splits_continuity_when_the_contract_says_so():
    rows = [o for o in trajectory("v", "t", "ATTA") if o.frame_index != 2]
    assert len(segment(rows, contract())) == 2
    keep = aa.ApplicabilityContract(run_length_grid=GRID,
                                    split_on_missing_frame=False)
    assert len(segment(rows, keep)) == 1


def test_exact_partition_violation_raises():
    from applicability_audit.applicability import assert_exact_partition
    with pytest.raises(AuditContractError, match="do not partition"):
        assert_exact_partition({"eligible": 1}, 2)
    with pytest.raises(AuditContractError, match="unexpected applicability"):
        assert_exact_partition({"eligible": 1, "fifth": 0}, 1)


# ------------------------------------------------------- natural runs
def test_natural_run_inventory_counts_on_and_off_grid_runs():
    r = audit()
    nr = r["natural_runs"]
    assert nr["by_grid_length"] == {"1": 1, "2": 4, "3": 1}
    assert nr["off_grid"] == 1
    assert nr["total"] == 7
    assert sum(nr["by_grid_length"].values()) + nr["off_grid"] == nr["total"]


def test_every_declared_grid_length_is_reported_even_when_unsupported():
    r = audit(grid=(1, 2, 3, 5, 8))
    assert sorted(int(k) for k in r["natural_runs"]["by_grid_length"]) == [1, 2, 3, 5, 8]
    assert r["natural_runs"]["by_grid_length"]["8"] == 0


def test_an_off_grid_run_is_never_split_truncated_merged_or_padded():
    rows = trajectory("v", "t", "ATTTTA")          # one natural run of length 4
    r = audit(rows=rows, methods=[method("m")], grid=(1, 2, 3))
    assert r["natural_runs"]["total"] == 1
    assert r["natural_runs"]["off_grid"] == 1
    assert r["natural_runs"]["by_grid_length"] == {"1": 0, "2": 0, "3": 0}
    assert r["cases"]["admitted_A"] == 0        # not truncated down to length 3


def test_runs_are_enumerated_before_method_support():
    """An anchorless segment still contributes runs, though it admits no case."""
    r = audit(rows=trajectory("v", "t", "TTT"), methods=[method("m")])
    assert r["natural_runs"]["by_grid_length"]["3"] == 1
    assert r["cases"]["admitted_A"] == 0
    assert r["applicability"]["counts"]["no_anchor"] == 3


def test_adjacent_target_blocks_separated_by_an_anchor_are_two_runs():
    seg = trajectory("v", "t", "ATATA")
    assert [len(x) for x in natural_runs(seg)] == [1, 1]


# ---------------------------------------------------------- case identity
def test_case_keys_are_deterministic_and_unique():
    r = audit()
    ids = [row["case_id"] for row in r["case_table"]]
    assert len(ids) == len(set(ids)) == r["cases"]["admitted_A"] == 3
    assert r["cases"]["unique_keys_verified"] is True


def test_case_key_carries_the_frozen_generic_components():
    cases = build_cases(trajectory("vA", "t1", "ATTA"), contract())
    assert len(cases) == 1
    assert cases[0].key == ("p", "vA", "t1", 1, 2)


def test_duplicate_case_keys_are_a_hard_failure():
    from applicability_audit.cases import assert_unique_keys
    cases = build_cases(trajectory("vA", "t1", "ATTA"), contract())
    with pytest.raises(AuditContractError, match="duplicate reconstruction case key"):
        assert_unique_keys(cases + cases)


# ------------------------------------------------------- method support
def test_a_narrower_method_makes_a_differ_from_d():
    r = audit()
    assert r["cases"]["admitted_A"] == 3
    assert r["method_support"]["method_all"] == 3
    assert r["method_support"]["method_restricted"] == 1
    assert r["common_support"]["D"] == 1
    assert r["common_support"]["D"] != r["cases"]["admitted_A"]


def test_identical_support_makes_a_equal_b_equal_c_equal_d():
    """The Record 61 shape: perfectly support-aligned, judged on its own terms."""
    methods = [method("m1"), method("m2", reconstruct=constant_predict(1.0))]
    r = audit(methods=methods)
    A = r["cases"]["admitted_A"]
    assert r["method_support"] == {"m1": A, "m2": A}
    assert r["metric_validity"]["C"] == A
    assert r["common_support"]["D"] == A
    assert r["support_retention"] == 1.0
    assert r["common_support"]["identical_across_methods"] is True


def test_a_method_supporting_nothing_empties_d():
    methods = [method("m1"), method("none", supports=lambda mi: False)]
    r = audit(methods=methods)
    assert r["method_support"]["none"] == 0
    assert r["common_support"]["D"] == 0
    assert r["support_retention"] == 0.0
    for m in ("m1", "none"):
        assert aa.is_unavailable(r["common_support_estimates"][m]["normalized"]["headline"])


def test_method_specific_support_can_exceed_common_support():
    r = audit()
    own = r["method_specific_estimates"]["method_all"]["n_cases"]
    assert own == 3 > r["common_support_estimates"]["method_all"]["n_cases"] == 1


def test_method_identifiers_must_be_unique():
    with pytest.raises(AuditContractError, match="unique"):
        audit(methods=[method("dup"), method("dup")])


def test_at_least_one_method_is_required():
    with pytest.raises(AuditContractError, match="at least one method"):
        audit(methods=[])


def test_a_method_that_contradicts_its_own_support_predicate_is_a_hard_failure():
    calls = {"n": 0}

    def flaky_supports(mi):
        calls["n"] += 1
        return True

    m = aa.MethodContract("flaky", flaky_supports, lambda mi: None)
    with pytest.raises(AuditContractError, match="disagree"):
        audit(methods=[m])


def test_a_method_returning_the_wrong_number_of_predictions_is_refused():
    m = aa.MethodContract("short", lambda mi: True, lambda mi: [(0.0, 0.0)])
    with pytest.raises(AuditContractError, match="predictions for"):
        audit(rows=trajectory("v", "t", "ATTA"), methods=[m])


# ------------------------------------------------------ metric validity C
def test_metric_validity_may_be_redundant():
    r = audit(methods=[method("m")])
    assert r["metric_validity"]["removed_from_A"] == 0
    assert r["metric_validity"]["redundant"] is True


def test_metric_validity_can_remove_a_case_without_touching_admission():
    rows = (trajectory("vA", "t1", "ATTA", scales={1: 0.0, 2: 0.0})
            + trajectory("vB", "t1", "ATTA"))
    r = audit(rows=rows, methods=[method("m")])
    assert r["cases"]["admitted_A"] == 2          # admission unaffected
    assert r["metric_validity"]["C"] == 1
    assert r["metric_validity"]["removed_from_A"] == 1
    assert r["common_support"]["D"] == 1
    assert r["method_support"]["m"] == 2          # B_m unaffected by the metric


def test_a_metric_invalid_case_enters_neither_comparison():
    rows = trajectory("vA", "t1", "ATTA", scales={1: 0.0, 2: 0.0})
    r = audit(rows=rows, methods=[method("m")])
    assert r["method_specific_estimates"]["m"]["n_cases"] == 0
    assert r["common_support_estimates"]["m"]["n_cases"] == 0
    row = r["case_table"][0]
    assert row["metric_valid"] is False and row["exclusion_reason"] == "metric_validity"


def test_scoring_an_undefined_output_is_refused():
    from applicability_audit.support import target_errors
    case = build_cases(trajectory("v", "t", "ATA"), contract())[0]
    with pytest.raises(AuditContractError, match="no surrogate error"):
        target_errors(case, None)


# ------------------------------------------------------ retention & shift
def test_support_retention_is_the_endpoint_ratio():
    r = audit()
    assert r["support_retention"] == pytest.approx(1 / 3.0)


def test_support_retention_is_structured_unavailable_when_a_is_empty():
    r = audit(rows=trajectory("v", "t", "TTT"), methods=[method("m")])
    assert r["cases"]["admitted_A"] == 0
    assert aa.is_unavailable(r["support_retention"])
    assert r["support_retention"]["value"] is None


def test_support_shift_is_exactly_zero_when_supports_are_identical():
    methods = [method("m1"), method("m2", reconstruct=constant_predict(1.0))]
    r = audit(methods=methods)
    for m in ("m1", "m2"):
        assert r["support_shift"][m]["supports_identical"] is True
        assert r["support_shift"][m]["normalized"] == pytest.approx(0.0, abs=1e-15)


@pytest.mark.parametrize("offsets,sign", [
    ({1: 5.0}, "positive"), ({3: 5.0, 4: 5.0}, "negative")])
def test_support_shift_takes_both_signs(offsets, sign):
    """The wider method is judged on more cases than D, so its shift is signed."""
    rows = trajectory("vA", "t1", "ATATTA", values=offsets)
    methods = [method("wide"),
               method("narrow", supports=lambda mi: mi.run_length == 1)]
    r = audit(rows=rows, methods=methods, grid=(1, 2))
    assert r["cases"]["admitted_A"] == 2 and r["common_support"]["D"] == 1
    wide = r["support_shift"]["wide"]
    assert wide["supports_identical"] is False
    shift = wide["normalized"]
    assert not aa.is_unavailable(shift)
    assert (shift > 0) if sign == "positive" else (shift < 0)
    # the narrower method's own support already equals D, so its shift is zero
    assert r["support_shift"]["narrow"]["supports_identical"] is True
    assert r["support_shift"]["narrow"]["normalized"] == pytest.approx(0.0, abs=1e-15)


def test_support_shift_is_unavailable_when_one_side_is_undefined():
    methods = [method("m1"), method("none", supports=lambda mi: False)]
    r = audit(methods=methods)
    assert aa.is_unavailable(r["support_shift"]["none"]["normalized"])


# --------------------------------------------------------- aggregation
def test_equal_weighting_differs_from_a_pooled_case_mean():
    rows = trajectory("vA", "t1", "ATA", values={1: 1.0})
    for i, off in enumerate((2.0, 4.0, 6.0)):
        rows += trajectory("vB", "t%d" % i, "ATA", values={1: off})
    r = audit(rows=rows, methods=[method("m")], grid=(1,))
    equal = r["common_support_estimates"]["m"]["normalized"]["headline"]
    assert equal == pytest.approx(((1.0 / SCALE) + (4.0 / SCALE)) / 2.0, rel=1e-12)
    pooled = (1.0 + 2.0 + 4.0 + 6.0) / 4.0 / SCALE
    assert equal != pytest.approx(pooled, rel=1e-9)


def test_the_simple_ladder_is_the_pooled_case_mean():
    rows = trajectory("vA", "t1", "ATA", values={1: 1.0})
    for i, off in enumerate((2.0, 4.0, 6.0)):
        rows += trajectory("vB", "t%d" % i, "ATA", values={1: off})
    r = audit(rows=rows, methods=[method("m")], grid=(1,),
              aggregation=agg.simple_case_ladder())
    assert r["common_support_estimates"]["m"]["normalized"]["headline"] == \
        pytest.approx((1.0 + 2.0 + 4.0 + 6.0) / 4.0 / SCALE, rel=1e-12)


def test_every_aggregation_level_declares_its_unit_and_weighting():
    r = audit()
    ladder = r["aggregation"]["contract"]["levels"]
    assert [lv["name"] for lv in ladder] == ["sequence_and_run_length", "sequence", "headline"]
    for lv in ladder:
        assert lv["weighting"] == "equal" and "group_keys" in lv and lv["unavailable"]
    assert r["aggregation"]["contract"]["first_rung"].startswith("target error")


def test_a_hidden_weighting_rule_is_refused():
    with pytest.raises(AuditContractError, match="hidden weighting"):
        aa.AggregationLevel("bad", ("sequence_id",), weighting="by_case_count")


def test_the_final_level_must_collapse_to_one_unit():
    with pytest.raises(AuditContractError, match="final aggregation level"):
        aa.AggregationContract(levels=(aa.AggregationLevel("x", ("sequence_id",)),))


def test_contributing_units_are_reported_for_every_declared_length():
    r = audit(grid=(1, 2, 3, 5))
    per = r["aggregation"]["contributing_units_per_reported_grid_length"]
    assert sorted(int(k) for k in per) == [1, 2, 3, 5]
    assert per["5"] == 0


# --------------------------------------------------------------- strata
def test_every_stratum_present_in_the_input_is_reported():
    r = audit()
    assert sorted(r["strata"]) == ["alpha", "beta", "gamma"]
    for name in ("alpha", "beta", "gamma"):
        entry = r["strata"][name]
        assert sum(entry["counts"].values()) == entry["scoreable_targets"]


def test_a_stratum_without_support_is_structured_unavailable():
    r = audit()
    assert aa.is_unavailable(r["strata"]["gamma"]["reconstruction"])
    assert r["strata"]["gamma"]["scoreable_targets"] > 0


def test_the_core_does_not_interpret_stratum_names():
    rows = trajectory("v", "t", "ATA", stratum={"anything": 1}.__repr__())
    r = audit(rows=rows, methods=[method("m")])
    assert len(r["strata"]) == 1


def test_stratification_can_be_disabled():
    r = audit(strata=False)
    assert aa.is_unavailable(r["strata"])


# ------------------------------------------------------------ stability
def test_stability_is_disabled_by_default_and_says_so():
    r = audit()
    assert r["stability"]["enabled"] is False
    assert aa.is_unavailable(r["stability"]["results"])


def test_enabled_stability_reports_its_own_interpretation_label():
    st = aa.StabilityContract(enabled=True, cluster_key="sequence_id",
                              replicates=64, seed=20260825, paired=True)
    methods = [method("m1"), method("m2", reconstruct=constant_predict(1.0))]
    r = audit(methods=methods, stability=st)
    res = r["stability"]["results"]
    assert res["contributing_clusters"] == 2 and res["paired"] is True
    for m in ("m1", "m2"):
        band = res["methods"][m]
        assert band["lo"] <= band["hi"]
        assert band["is_confidence_interval"] is False
        assert band["seed"] == 20260825 and band["replicates"] == 64


def test_stability_is_deterministic_for_a_fixed_seed():
    st = aa.StabilityContract(enabled=True, replicates=64, seed=7)
    a = audit(methods=[method("m")], stability=st)["stability"]["results"]
    b = audit(methods=[method("m")], stability=st)["stability"]["results"]
    assert a == b


def test_enabled_stability_needs_a_positive_replicate_count():
    with pytest.raises(AuditContractError, match="positive replicate"):
        aa.StabilityContract(enabled=True, replicates=0)


# ------------------------------------------------------- no outcome leakage
def test_changing_reconstruction_error_changes_nothing_structural():
    """Radically different predictions, identical structural audit."""
    base = audit(methods=[method("m")])
    other = audit(methods=[method("m", reconstruct=constant_predict(1e3))])
    for section in ("population", "applicability", "natural_runs", "cases",
                    "metric_validity", "method_support", "common_support"):
        assert base[section] == other[section]
    assert base["support_retention"] == other["support_retention"]
    assert base["case_table"] == other["case_table"]
    assert (base["common_support_estimates"]["m"]["normalized"]["headline"]
            != other["common_support_estimates"]["m"]["normalized"]["headline"])


def test_a_method_cannot_reach_the_reference_values():
    """MethodInput exposes anchors and target times only."""
    captured = {}

    def spy(mi):
        captured["fields"] = set(dir(mi))
        return linear_predict(mi)

    audit(methods=[method("m", reconstruct=spy)])
    public = {f for f in captured["fields"] if not f.startswith("_")}
    assert public == {"key", "obs_t", "obs_v", "tgt_t", "n_anchors", "run_length"}
    assert "eval_only" not in public and "tgt_v" not in public


def test_applicability_does_not_consult_any_method():
    rows = reference_corpus()
    one = audit(rows=rows, methods=[method("m")])
    three = audit(rows=rows)
    assert one["applicability"] == three["applicability"]
    assert one["cases"] == three["cases"]
    assert one["natural_runs"] == three["natural_runs"]


# ------------------------------------------------------------ determinism
def test_two_identical_audits_serialize_byte_identically():
    assert aa.dumps(audit()) == aa.dumps(audit())


def test_semantically_irrelevant_input_order_does_not_matter():
    rows = reference_corpus()
    shuffled = list(rows)
    random.Random(20260825).shuffle(shuffled)
    assert aa.dumps(audit(rows=rows)) == aa.dumps(audit(rows=shuffled))


def test_serialization_rejects_non_finite_values():
    with pytest.raises(ValueError):
        aa.dumps({"x": float("nan")})


def test_no_raw_none_survives_a_completed_audit():
    from applicability_audit.serialization import assert_no_raw_none
    r = audit()
    assert_no_raw_none(r)
    r["cases"]["admitted_A"] = None
    with pytest.raises(AuditContractError, match="never populated"):
        assert_no_raw_none(r)


def test_the_result_is_json_round_trippable():
    text = aa.dumps(audit())
    assert aa.dumps(json.loads(text)) == text


# ------------------------------------------------------ provenance & audit
def test_provenance_records_every_contract():
    st = aa.StabilityContract(enabled=True, replicates=32, seed=5)
    r = audit(stability=st, provenance={"study": "synthetic"})
    p = r["provenance"]
    assert p["schema_version"] == aa.SCHEMA_VERSION
    assert p["applicability_contract"]["run_length_grid"] == list(GRID)
    assert sorted(m["method_id"] for m in p["methods"]) == \
        ["method_all", "method_all_2", "method_restricted"]
    assert p["aggregation_contract"]["levels"]
    assert p["stability_contract"]["replicates"] == 32
    assert p["supplied"] == {"study": "synthetic"}


def test_the_case_table_never_needs_a_reconstruction_error():
    r = audit()
    for row in r["case_table"]:
        assert set(row) >= {"case_id", "sequence_id", "trajectory_id",
                            "first_target_frame", "run_length",
                            "applicability_state", "metric_valid",
                            "method_support", "common_support"}
        assert "error" not in row and "prediction" not in row


def test_validation_block_records_the_hard_assertions():
    v = audit()["validation"]
    assert v["exact_applicability_partition"] is True
    assert v["unique_case_keys"] is True
    assert v["identical_common_support_keys"] is True
    assert v["no_silent_case_drop"] is True
    assert v["all_methods_represented"] == ["method_all", "method_all_2",
                                            "method_restricted"]


def test_the_failure_mode_taxonomy_is_exposed():
    assert audit()["failure_modes"]["taxonomy"] == list(aa.FAILURE_MODES)
    assert len(aa.FAILURE_MODES) == 7


def test_common_support_must_be_contained_in_every_method_support():
    from applicability_audit.support import assert_identical_common_support
    sets = {"A": [("k",)], "C": {("k",)}, "B": {"m": set()}, "D": {("k",)}}
    with pytest.raises(AuditContractError, match="not contained"):
        assert_identical_common_support(sets, [method("m")])


# -------------------------------------------------- core dependency audit
CORE_MODULES = ("applicability_audit", "applicability_audit.aggregation",
                "applicability_audit.applicability", "applicability_audit.audit",
                "applicability_audit.cases", "applicability_audit.contracts",
                "applicability_audit.serialization", "applicability_audit.support",
                "applicability_audit.synthesis")

FORBIDDEN_DEPENDENCIES = ("bdd", "mot17", "trajectory_cross_domain",
                          "reconstruction_generic", "skeleton", "posetrack",
                          "kitti", "ntu", "scripts")


def test_the_core_imports_no_dataset_specific_module():
    """Checked on import statements, not on prose: the core may *describe* a
    domain in a docstring, but it may never depend on one."""
    import importlib
    import inspect
    for name in CORE_MODULES:
        src = inspect.getsource(importlib.import_module(name))
        for line in src.splitlines():
            stripped = line.strip()
            if not (stripped.startswith("import ") or stripped.startswith("from ")):
                continue
            for token in FORBIDDEN_DEPENDENCIES:
                assert token not in stripped.lower(), \
                    "%s imported into %s via %r" % (token, name, stripped)


def test_no_dataset_specific_identifier_is_exported_by_the_core():
    import importlib
    banned = ("occluded", "truncated", "crowd", "visibility", "mark", "joint")
    for name in CORE_MODULES:
        mod = importlib.import_module(name)
        for attr in dir(mod):
            if attr.startswith("_"):
                continue
            assert not any(b in attr.lower() for b in banned), \
                "%s exports dataset-specific name %r" % (name, attr)


def test_the_public_api_is_small_and_explicit():
    assert set(aa.__all__) == {
        "run_applicability_audit", "audit_precomputed_results",
        "AuditResult", "AuditCertificate",
        "render_audit_report", "render_support_matrix",
        "RANKING_ADMISSIBLE", "RANKING_NOT_ADMISSIBLE", "REASON_CODES",
        "CanonicalObservation", "ApplicabilityContract",
        "MethodContract", "AggregationContract", "AggregationLevel",
        "StabilityContract", "frozen_trajectory_ladder", "simple_case_ladder",
        "AuditContractError", "APPLICABILITY_CLASSES", "FAILURE_MODES",
        "SCHEMA_VERSION", "dumps", "unavailable", "is_unavailable"}
    assert len(aa.__all__) == len(set(aa.__all__))
