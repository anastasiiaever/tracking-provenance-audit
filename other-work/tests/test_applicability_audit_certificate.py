"""Record 62A --- the structural verdict, support geometry and coverage.

The certificate answers "is this ranking readable?", never "does this effect
matter". These tests pin that boundary: no threshold of the toolkit's own
invention may ever turn a valid comparison into an invalid one.
"""
from __future__ import annotations

import pytest

import applicability_audit as aa
from applicability_audit import aggregation as agg
from applicability_audit.certificate import (REASON_TAXONOMY, build_certificate,
                                             render_support_matrix)
from applicability_audit.diagnostics import jaccard, pairwise_support_geometry

from test_applicability_audit import (GRID, audit, contract, method,
                                            reference_corpus, trajectory,
                                            constant_predict, three_methods)


# ------------------------------------------------------- certificate shape
def test_a_clean_audit_is_admissible_and_every_check_passes():
    cert = audit().certificate()
    assert cert["ranking_verdict"] == aa.RANKING_ADMISSIBLE
    assert cert["ranking_admissible"] is True
    assert cert["reason_codes"] == []
    assert set(cert["checks"].values()) == {"PASS"}
    assert cert["audit_status"] == "AUDIT_COMPLETE"
    assert cert["mode"] == "executable"


def test_the_certificate_carries_a_configuration_fingerprint():
    a, b = audit().certificate(), audit().certificate()
    assert a["configuration_fingerprint"] == b["configuration_fingerprint"]
    assert len(a["configuration_fingerprint"]) == 64
    other = audit(grid=(1, 2)).certificate()
    assert other["configuration_fingerprint"] != a["configuration_fingerprint"]


def test_every_reason_code_maps_to_the_frozen_taxonomy():
    assert set(aa.REASON_CODES) == set(REASON_TAXONOMY)
    assert set(REASON_TAXONOMY.values()) <= set(aa.FAILURE_MODES)


def test_the_certificate_is_byte_identical_for_identical_input():
    assert aa.dumps(audit().certificate()) == aa.dumps(audit().certificate())


def test_the_certificate_holds_no_clock_reading():
    """Checked on key names, not substrings: 'outcome' contains 'utc'."""
    banned = ("timestamp", "generated_at", "created_at", "datetime", "wall_clock")
    seen = []

    def walk(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                seen.append(str(k).lower())
                walk(v)
        elif isinstance(obj, (list, tuple)):
            for v in obj:
                walk(v)

    walk(audit().certificate())
    assert seen
    for key in seen:
        assert not any(b in key for b in banned), "clock-derived key %r" % key


# ---------------------------------------------- the two distinct conditions
def low_applicability_corpus():
    """Ten leading targets, one eligible target, every method supporting it."""
    return trajectory("v", "t", "TTTTTTTTTTATA")


def test_low_applicability_with_perfect_support_agreement_is_still_admissible():
    """The Record 61 shape: severe coverage failure, no support mismatch."""
    methods = [method("m1"), method("m2", reconstruct=constant_predict(1.0)),
               method("m3", reconstruct=constant_predict(2.0))]
    r = audit(rows=low_applicability_corpus(), methods=methods, grid=(1,))
    cov = r["diagnostics"]["coverage"]

    assert cov["applicability"]["scoreable_targets"] == 11
    assert cov["applicability"]["applicable_targets"] == 1
    assert cov["applicability"]["applicability_rate"] == pytest.approx(1 / 11.0)

    A = r["cases"]["admitted_A"]
    assert A == 1
    assert r["method_support"] == {"m1": A, "m2": A, "m3": A}
    assert r["metric_validity"]["C"] == A
    assert r["common_support"]["D"] == A
    assert cov["support_retention"]["common_support_retention_conditional_on_A"] == 1.0
    assert all(v == 1.0 for v in
               cov["support_retention"]["per_method_conditional_on_A"].values())

    cert = r.certificate()
    assert cert["ranking_admissible"] is True, "low coverage must not invalidate D"
    assert cert["reason_codes"] == []
    assert cert["support_geometry"]["all_supports_identical"] is True


def test_coverage_and_support_retention_are_reported_as_separate_units():
    cov = audit(rows=low_applicability_corpus(), methods=[method("m")],
                grid=(1,))["diagnostics"]["coverage"]
    assert cov["applicability"]["unit"] == "target"
    assert cov["support_retention"]["unit"] == "case"
    assert cov["applicability"]["applicability_rate"] != \
        cov["support_retention"]["common_support_retention_conditional_on_A"]


def test_support_mismatch_is_detected_but_does_not_by_itself_invalidate():
    r = audit()                                # method_restricted is narrower
    assert r["cases"]["admitted_A"] == 3 and r["common_support"]["D"] == 1
    geo = r["diagnostics"]["support_geometry"]
    assert geo["all_supports_identical"] is False
    assert geo["matrix"]["method_all"]["method_restricted"]["intersection"] == 1
    cert = r.certificate()
    assert cert["ranking_admissible"] is True   # exact D exists and aligns
    assert cert["coverage"]["support_retention"][
        "common_support_retention_conditional_on_A"] == pytest.approx(1 / 3.0)


def test_no_threshold_of_the_toolkits_own_is_applied():
    """A 1/11 applicability rate and a 1/3 retention both stay admissible."""
    for rows, methods, grid in ((low_applicability_corpus(),
                                 [method("m1"), method("m2")], (1,)),
                                (reference_corpus(), three_methods(), GRID)):
        assert audit(rows=rows, methods=methods, grid=grid).certificate()[
            "ranking_admissible"] is True


# --------------------------------------------------------- inadmissibility
def test_no_common_support_is_reported_and_blocks_the_ranking():
    methods = [method("m1"), method("none", supports=lambda mi: False)]
    cert = audit(methods=methods).certificate()
    assert cert["ranking_admissible"] is False
    assert cert["ranking_verdict"] == aa.RANKING_NOT_ADMISSIBLE
    assert cert["reason_codes"] == ["NO_COMMON_SUPPORT"]
    assert cert["reason_taxonomy"]["NO_COMMON_SUPPORT"] == "method_support"


def test_no_admitted_case_is_reported_and_retention_is_unavailable():
    r = audit(rows=trajectory("v", "t", "TTT"), methods=[method("m")])
    cert = r.certificate()
    assert cert["ranking_admissible"] is False
    assert cert["reason_codes"] == ["NO_ADMITTED_CASES"]
    ret = cert["coverage"]["support_retention"][
        "common_support_retention_conditional_on_A"]
    assert aa.is_unavailable(ret)


def test_metric_invalidity_is_not_mislabelled_as_a_support_failure():
    rows = trajectory("vA", "t1", "ATTA", scales={1: 0.0, 2: 0.0})
    r = audit(rows=rows, methods=[method("m")])
    assert r["method_support"]["m"] == 1        # the method does support it
    assert r["metric_validity"]["removed_from_A"] == 1
    cert = r.certificate()
    assert cert["reason_codes"] == ["NO_COMMON_SUPPORT"]
    assert cert["checks"]["metric_validity"] == "PASS"
    row = r["case_table"][0]
    assert row["exclusion_reason"] == "metric_validity"


# ------------------------------------------------------- support geometry
def test_pairwise_geometry_is_exact_and_symmetric():
    geo = pairwise_support_geometry({"a": {1, 2, 3}, "b": {2, 3, 4}, "c": {1, 2, 3}})
    ab = geo["matrix"]["a"]["b"]
    assert ab["size_i"] == 3 and ab["size_j"] == 3
    assert ab["intersection"] == 2 and ab["union"] == 4
    assert ab["jaccard"] == pytest.approx(0.5)
    assert geo["matrix"]["b"]["a"]["jaccard"] == ab["jaccard"]
    assert geo["matrix"]["a"]["c"]["jaccard"] == 1.0
    assert geo["all_supports_identical"] is False
    assert geo["overlap_measure"] == "jaccard"
    assert "union" in geo["overlap_definition"]


def test_the_geometry_diagonal_and_empty_support_behave_as_declared():
    geo = pairwise_support_geometry({"full": {1, 2}, "empty": set()})
    assert geo["matrix"]["full"]["full"]["jaccard"] == 1.0
    assert aa.is_unavailable(geo["matrix"]["empty"]["empty"]["jaccard"])
    assert geo["matrix"]["full"]["empty"]["jaccard"] == 0.0
    assert aa.is_unavailable(jaccard(set(), set()))


def test_identical_supports_are_flagged():
    geo = pairwise_support_geometry({"a": {1, 2}, "b": {1, 2}})
    assert geo["all_supports_identical"] is True
    assert geo["matrix"]["a"]["b"]["jaccard"] == 1.0


def test_the_support_matrix_renders_deterministically():
    geo = audit()["diagnostics"]["support_geometry"]
    text = render_support_matrix(geo)
    assert text == render_support_matrix(geo)
    assert "jaccard" in text
    for name in geo["methods"]:
        assert name in text
    assert audit().render_support_matrix() == text


# ------------------------------------------------------ readable report
def test_the_report_lists_every_check_and_the_verdict():
    text = audit().render_report()
    for label in ("Population contract", "Applicability partition",
                  "Natural-run integrity", "Case identity",
                  "Method-support accounting", "Metric validity",
                  "Common-support identity", "Aggregation declaration",
                  "Outcome-leakage safeguards"):
        assert label in text
    assert "Ranking admissible" in text and "YES" in text
    assert "Applicability rate" in text and "Common-support retention" in text
    assert "does not invalidate the ranking on D" in text


def test_the_report_names_the_reason_when_ranking_is_unavailable():
    methods = [method("m1"), method("none", supports=lambda mi: False)]
    text = audit(methods=methods).render_report()
    assert "Ranking admissible" in text and "NO" in text
    assert "NO_COMMON_SUPPORT" in text


def test_the_report_is_deterministic():
    assert audit().render_report() == audit().render_report()


def test_a_certificate_can_be_rendered_from_its_own_object():
    cert = audit().certificate()
    assert cert.render() == aa.render_audit_report(cert)


# ------------------------------------------------------ leakage safeguard
def test_the_certificate_structure_ignores_reconstruction_error():
    base = audit(methods=[method("m")]).certificate()
    other = audit(methods=[method("m", reconstruct=constant_predict(1e6))]
                  ).certificate()
    for field in ("checks", "ranking_admissible", "reason_codes", "coverage",
                  "support_geometry", "configuration_fingerprint"):
        assert base[field] == other[field]


# ------------------------------------------------------- README stays honest
def test_the_readme_example_reproduces_its_documented_numbers():
    """Pins the figures printed in applicability_audit/README.md."""
    def o(seq, traj, frame, role, value=0.0):
        kw = {"sequence_id": seq, "target": role == "T", "anchor": role == "A"}
        return aa.CanonicalObservation(traj, frame, (value, 0.0),
                                       metric_scale=(1.0 if role == "T" else None),
                                       **kw)

    rows = []
    for i, off in enumerate((0.2, 0.4, 0.6, 0.8)):
        rows += [o("s%d" % i, "t%d" % i, 0, "A"),
                 o("s%d" % i, "t%d" % i, 1, "T", off),
                 o("s%d" % i, "t%d" % i, 2, "A")]
    for j in range(2):
        rows += [o("s9", "u%d" % j, k, "T") for k in range(4)]

    flat = lambda mi: [(0.0, 0.0) for _ in mi.tgt_t]
    methods = [aa.MethodContract("linear", lambda mi: mi.n_anchors >= 2, flat),
               aa.MethodContract("spline", lambda mi: mi.n_anchors >= 2,
                                 lambda mi: [(0.1, 0.0) for _ in mi.tgt_t]),
               aa.MethodContract("shallow", lambda mi: mi.key[1] != "s3", flat)]

    r = aa.run_applicability_audit(
        rows, methods, aa.ApplicabilityContract(run_length_grid=(1, 2, 3)),
        agg.simple_case_ladder())
    cov = r["diagnostics"]["coverage"]
    assert cov["applicability"]["scoreable_targets"] == 12
    assert cov["applicability"]["applicable_targets"] == 4
    assert cov["applicability"]["applicability_rate"] == pytest.approx(1 / 3.0)
    assert cov["support_retention"]["admitted_cases_A"] == 4
    assert cov["support_retention"]["common_support_cases_D"] == 3
    assert cov["support_retention"][
        "common_support_retention_conditional_on_A"] == pytest.approx(0.75)
    assert r.certificate()["ranking_admissible"] is True
    geo = r["diagnostics"]["support_geometry"]["matrix"]
    assert geo["linear"]["spline"]["jaccard"] == 1.0
    assert geo["linear"]["shallow"]["jaccard"] == pytest.approx(0.75)
    assert r["common_support_estimates"]["spline"]["normalized"]["headline"] == \
        pytest.approx(0.3)
