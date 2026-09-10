"""Record 62A --- auditing a published benchmark without rerunning anything.

The precomputed path exists for the common situation in which only aggregate
numbers and per-case outputs survive. Its central discipline is that alignment
is by case identifier and never by position: two result files of equal length
are not evidence that the methods ran on the same cases.
"""
from __future__ import annotations

import pytest

import applicability_audit as aa
from applicability_audit import aggregation as agg
from applicability_audit.audit import audit_precomputed_results

from tests.test_applicability_audit import (GRID, audit, linear_predict, method,
                                            reference_corpus, three_methods)

LADDER = agg.simple_case_ladder()


def cases_of(ids, sequences=None, strata=None, run_length=1):
    sequences = sequences or {}
    strata = strata or {}
    return [{"case_id": c, "sequence_id": sequences.get(c, "s"),
             "trajectory_id": "t", "first_target_frame": 0,
             "run_length": run_length, "stratum": strata.get(c)}
            for c in ids]


def results(mapping):
    """{method: {case_id: normalized value}} -> precomputed result payload."""
    return {m: {c: {"normalized": [v], "raw": [v * 10.0]}
                for c, v in rows.items()} for m, rows in mapping.items()}


# ----------------------------------------------------------- basic behaviour
def test_a_clean_precomputed_benchmark_is_admissible():
    r = audit_precomputed_results(
        cases_of(["c1", "c2", "c3"]),
        results({"a": {"c1": 0.1, "c2": 0.2, "c3": 0.3},
                 "b": {"c1": 0.4, "c2": 0.5, "c3": 0.6}}), LADDER)
    cert = r.certificate()
    assert cert["mode"] == "precomputed"
    assert cert["ranking_admissible"] is True and cert["reason_codes"] == []
    assert r["common_support"]["D"] == 3
    assert r["common_support_estimates"]["a"]["normalized"]["headline"] == \
        pytest.approx(0.2)


def test_no_reconstruction_callable_is_required():
    r = audit_precomputed_results(cases_of(["c1"]),
                                  results({"a": {"c1": 0.5}}), LADDER)
    assert r["provenance"]["methods"] == [{"method_id": "a",
                                           "description": "precomputed results"}]


def test_already_aggregated_case_values_are_accepted():
    r = audit_precomputed_results(
        cases_of(["c1", "c2"]),
        {"a": {"c1": {"value": {"normalized": 0.2, "raw": 2.0}},
               "c2": {"value": {"normalized": 0.4, "raw": 4.0}}}},
        agg.AggregationContract(levels=LADDER.levels,
                                metric_fields=("normalized", "raw")))
    assert r["common_support_estimates"]["a"]["normalized"]["headline"] == \
        pytest.approx(0.3)


# ------------------------------------------------------- support geometry
def test_methods_reporting_different_cases_expose_a_support_mismatch():
    """The README case: two published aggregates over different case sets."""
    r = audit_precomputed_results(
        cases_of(["c1", "c2", "c3"]),
        results({"a": {"c1": 0.10, "c2": 0.20},
                 "b": {"c2": 0.30, "c3": 0.40}}), LADDER)
    assert r["method_support"] == {"a": 2, "b": 2}
    assert r["common_support"]["D"] == 1
    geo = r["diagnostics"]["support_geometry"]
    assert geo["all_supports_identical"] is False
    assert geo["matrix"]["a"]["b"]["intersection"] == 1
    assert geo["matrix"]["a"]["b"]["union"] == 3
    assert geo["matrix"]["a"]["b"]["jaccard"] == pytest.approx(1 / 3.0)

    # the two originally published aggregates are NOT a like-for-like ranking
    own_a = r["method_specific_estimates"]["a"]["normalized"]["headline"]
    own_b = r["method_specific_estimates"]["b"]["normalized"]["headline"]
    assert own_a == pytest.approx(0.15) and own_b == pytest.approx(0.35)
    assert r["support_shift"]["a"]["supports_identical"] is False
    assert r["support_shift"]["b"]["supports_identical"] is False

    # the admissible comparison is the one restricted to D
    common_a = r["common_support_estimates"]["a"]["normalized"]["headline"]
    common_b = r["common_support_estimates"]["b"]["normalized"]["headline"]
    assert common_a == pytest.approx(0.20) and common_b == pytest.approx(0.30)
    assert r.certificate()["ranking_admissible"] is True


def test_equal_result_counts_do_not_imply_equal_support():
    r = audit_precomputed_results(
        cases_of(["c1", "c2", "c3", "c4"]),
        results({"a": {"c1": 0.1, "c2": 0.2}, "b": {"c3": 0.3, "c4": 0.4}}),
        LADDER)
    assert r["method_support"] == {"a": 2, "b": 2}
    assert r["common_support"]["D"] == 0
    assert r.certificate()["reason_codes"] == ["NO_COMMON_SUPPORT"]


# ---------------------------------------------------------- case alignment
def test_a_result_naming_an_unknown_case_is_an_alignment_mismatch():
    r = audit_precomputed_results(
        cases_of(["c1", "c2"]),
        results({"a": {"c1": 0.1, "c2": 0.2},
                 "b": {"c1": 0.3, "c9": 0.4}}), LADDER)
    cert = r.certificate()
    assert cert["ranking_admissible"] is False
    assert "CASE_ALIGNMENT_MISMATCH" in cert["reason_codes"]
    assert r["case_alignment"]["unknown_case_identifiers"] == {"b": ["c9"]}
    assert r["case_alignment"]["positional_alignment_used"] is False


def test_a_duplicate_case_identifier_is_a_hard_failure():
    with pytest.raises(aa.AuditContractError, match="duplicate precomputed case"):
        audit_precomputed_results(cases_of(["c1", "c1"]),
                                  results({"a": {"c1": 0.1}}), LADDER)


def test_a_method_reporting_nothing_is_support_incomplete():
    r = audit_precomputed_results(cases_of(["c1"]),
                                  {"a": {"c1": {"normalized": [0.1], "raw": [1.0]}},
                                   "b": {}}, LADDER)
    cert = r.certificate()
    assert cert["ranking_admissible"] is False
    assert "METHOD_SUPPORT_INCOMPLETE" in cert["reason_codes"]
    assert r["case_alignment"]["methods_reporting_no_case"] == ["b"]


def test_a_missing_metric_field_makes_the_results_incomplete():
    r = audit_precomputed_results(
        cases_of(["c1", "c2"]),
        {"a": {"c1": {"normalized": [0.1], "raw": [1.0]},
               "c2": {"normalized": [0.2], "raw": [2.0]}},
         "b": {"c1": {"normalized": [0.3], "raw": [3.0]},
               "c2": {"normalized": [0.4]}}},
        agg.AggregationContract(levels=LADDER.levels,
                                metric_fields=("normalized", "raw")))
    cert = r.certificate()
    assert "INCOMPLETE_METHOD_RESULTS" in cert["reason_codes"]
    assert r["common_support"]["D"] == 1


def test_no_admitted_case_at_all():
    r = audit_precomputed_results([], {"a": {}}, LADDER)
    cert = r.certificate()
    assert cert["ranking_admissible"] is False
    assert "NO_ADMITTED_CASES" in cert["reason_codes"]
    assert aa.is_unavailable(r["support_retention"])


# ------------------------------------------------------- metric validity
def test_metric_validity_removes_a_case_without_blaming_method_support():
    r = audit_precomputed_results(
        cases_of(["c1", "c2"]),
        results({"a": {"c1": 0.1, "c2": 0.2}, "b": {"c1": 0.3, "c2": 0.4}}),
        LADDER, metric_valid={"c1": True, "c2": False})
    assert r["method_support"] == {"a": 2, "b": 2}
    assert r["metric_validity"]["C"] == 1 and r["metric_validity"]["removed_from_A"] == 1
    assert r["common_support"]["D"] == 1
    row = [x for x in r["case_table"] if x["case_id"] == "c2"][0]
    assert row["exclusion_reason"] == "metric_validity"


# ----------------------------------------------------------- coverage info
def test_population_coverage_is_unavailable_unless_supplied():
    r = audit_precomputed_results(cases_of(["c1"]),
                                  results({"a": {"c1": 0.1}}), LADDER)
    cov = r["diagnostics"]["coverage"]["applicability"]
    assert aa.is_unavailable(cov["applicability_rate"])
    assert aa.is_unavailable(r["applicability"])
    assert r.certificate()["ranking_admissible"] is True


def test_supplied_applicability_information_is_verified_and_reported():
    r = audit_precomputed_results(
        cases_of(["c1"]), results({"a": {"c1": 0.1}}), LADDER,
        applicability={"scoreable_targets": 20,
                       "counts": {"eligible": 2, "leading": 8,
                                  "trailing": 4, "no_anchor": 6}})
    cov = r["diagnostics"]["coverage"]["applicability"]
    assert cov["applicable_targets"] == 2
    assert cov["applicability_rate"] == pytest.approx(0.1)
    assert r["applicability"]["exact_partition_verified"] is True


def test_supplied_applicability_that_does_not_partition_is_refused():
    with pytest.raises(aa.AuditContractError, match="do not partition"):
        audit_precomputed_results(
            cases_of(["c1"]), results({"a": {"c1": 0.1}}), LADDER,
            applicability={"scoreable_targets": 20,
                           "counts": {"eligible": 1, "leading": 1,
                                      "trailing": 1, "no_anchor": 1}})


# ------------------------------------------------------------ determinism
def test_precomputed_serialization_is_deterministic():
    args = (cases_of(["c1", "c2"]),
            results({"a": {"c1": 0.1, "c2": 0.2}, "b": {"c1": 0.3, "c2": 0.4}}),
            LADDER)
    assert aa.dumps(audit_precomputed_results(*args)) == \
        aa.dumps(audit_precomputed_results(*args))


def test_precomputed_report_renders():
    r = audit_precomputed_results(cases_of(["c1", "c2"]),
                                  results({"a": {"c1": 0.1, "c2": 0.2}}), LADDER)
    text = r.render_report()
    assert "Mode: precomputed" in text and "Ranking admissible" in text


# --------------------------------------- equivalence with executable mode
def test_precomputed_mode_reproduces_the_executable_audit():
    """Same cases, same numbers, two entry points, one answer."""
    methods = three_methods()
    live = audit(methods=methods, aggregation=agg.simple_case_ladder())

    pre_cases, pre_results = [], {m.method_id: {} for m in methods}
    for row in live["case_table"]:
        pre_cases.append({"case_id": row["case_id"],
                          "sequence_id": row["sequence_id"],
                          "trajectory_id": row["trajectory_id"],
                          "first_target_frame": row["first_target_frame"],
                          "run_length": row["run_length"],
                          "stratum": None if aa.is_unavailable(row["stratum"])
                          else row["stratum"]})
    # replay the very same per-case values the executable audit produced
    from applicability_audit.audit import _evaluate, _collect
    from applicability_audit.support import support_sets
    from applicability_audit.contracts import ApplicabilityContract
    contract = ApplicabilityContract(run_length_grid=GRID)
    corpus = _collect(reference_corpus(), contract)
    sets = support_sets(corpus["cases"], methods)
    evaluated = _evaluate(corpus["cases"], methods, sets)
    from applicability_audit.serialization import key_repr
    for m in methods:
        for key, entry in evaluated[m.method_id].items():
            if entry.get("supported") and "errors" in entry:
                pre_results[m.method_id][key_repr(key)] = {
                    "normalized": entry["errors"]["normalized"],
                    "raw": entry["errors"]["raw"]}

    pre = audit_precomputed_results(pre_cases, pre_results,
                                    agg.simple_case_ladder())

    assert pre["cases"]["admitted_A"] == live["cases"]["admitted_A"]
    assert pre["method_support"] == live["method_support"]
    assert pre["metric_validity"]["C"] == live["metric_validity"]["C"]
    assert pre["common_support"]["D"] == live["common_support"]["D"]
    assert pre["support_retention"] == live["support_retention"]
    assert (pre["diagnostics"]["support_geometry"]["matrix"]
            == live["diagnostics"]["support_geometry"]["matrix"])
    for m in methods:
        for field in ("normalized", "raw"):
            assert (pre["common_support_estimates"][m.method_id][field]["headline"]
                    == pytest.approx(
                        live["common_support_estimates"][m.method_id][field]["headline"]))
            assert (pre["method_specific_estimates"][m.method_id][field]["headline"]
                    == pytest.approx(
                        live["method_specific_estimates"][m.method_id][field]["headline"]))
            assert pre["support_shift"][m.method_id][field] == pytest.approx(
                live["support_shift"][m.method_id][field])
    assert (pre.certificate()["ranking_admissible"]
            == live.certificate()["ranking_admissible"])
    assert pre.certificate()["reason_codes"] == live.certificate()["reason_codes"]
