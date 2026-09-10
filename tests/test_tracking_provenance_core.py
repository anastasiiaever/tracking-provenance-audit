"""Unit tests for the released tracking-provenance audit core.

These exercise the admission rule, the ordering engine, the materiality rule, the
state construction and the execution guard directly, on fixtures whose correct
answer is known by construction. They need no dataset and no tracker.
"""
from __future__ import annotations

import os

import pytest

from tracking_provenance_audit import guard, materiality, metrics, ordering, states, stv
from tracking_provenance_audit.rowid import (DuplicateRowIdentity, Row, iou,
                                             parse_gt, parse_mot)

SEQ = "T-01"


def row(frame, tid, x, y, w=10.0, h=20.0, score=1.0):
    return Row(SEQ, frame, tid, x, y, w, h, score, 1.0, ())


# --------------------------------------------------------------- row identity
def test_row_identity_is_sequence_frame_track():
    assert row(3, 7, 0.0, 0.0).rid == (SEQ, 3, 7)


def test_parse_mot_rejects_a_repeated_row_identity():
    text = "1,1,0,0,10,20,1,1,1\n1,1,5,5,10,20,1,1,1\n"
    with pytest.raises(DuplicateRowIdentity):
        parse_mot(text, SEQ)


def test_parse_gt_keeps_only_scoreable_pedestrians():
    text = ("1,1,0,0,10,20,1,1,1\n"      # flag 1, class 1 -> kept
            "1,2,0,0,10,20,0,1,1\n"      # flag 0        -> dropped
            "1,3,0,0,10,20,1,7,1\n")     # class 7       -> dropped
    assert [r.track_id for r in parse_gt(text, SEQ)] == [1]


def test_parse_gt_does_not_threshold_visibility():
    text = "1,1,0,0,10,20,1,1,0.0\n"
    assert len(parse_gt(text, SEQ)) == 1


def test_iou_is_zero_for_disjoint_boxes_and_one_for_identical():
    assert iou(row(1, 1, 0.0, 0.0), row(1, 2, 500.0, 500.0)) == 0.0
    assert iou(row(1, 1, 0.0, 0.0), row(1, 2, 0.0, 0.0)) == pytest.approx(1.0)


# ------------------------------------------------------------------ admission
def _fixture():
    r0 = [row(1, 1, 0.0, 0.0), row(3, 1, 0.0, 0.0)]
    gt = [row(1, 1, 0.0, 0.0), row(2, 1, 0.0, 0.0), row(3, 1, 0.0, 0.0)]
    return r0, gt


def test_a_row_between_two_agreeing_anchors_is_admitted():
    r0, gt = _fixture()
    assert stv.classify([(SEQ, 2, 1)], r0, gt)[(SEQ, 2, 1)] == stv.SEMANTICALLY_ADMITTED


def test_anchors_resolving_to_different_identities_are_a_mismatch():
    r0 = [row(1, 1, 0.0, 0.0), row(3, 1, 100.0, 0.0)]
    gt = [row(1, 1, 0.0, 0.0), row(2, 1, 0.0, 0.0),
          row(3, 2, 100.0, 0.0), row(2, 2, 100.0, 0.0)]
    assert stv.classify([(SEQ, 2, 1)], r0, gt)[(SEQ, 2, 1)] == stv.ANCHOR_ID_MISMATCH


def test_an_anchor_matching_nothing_is_unmatched():
    r0 = [row(1, 1, 900.0, 900.0), row(3, 1, 900.0, 900.0)]
    gt = [row(1, 5, 0.0, 0.0), row(2, 5, 0.0, 0.0), row(3, 5, 0.0, 0.0)]
    assert stv.classify([(SEQ, 2, 1)], r0, gt)[(SEQ, 2, 1)] == stv.ANCHOR_UNMATCHED


def test_an_absent_reference_at_the_target_frame_is_its_own_class():
    r0, gt = _fixture()
    gt = [g for g in gt if g.frame != 2]
    assert stv.classify([(SEQ, 2, 1)], r0, gt)[(SEQ, 2, 1)] == stv.TARGET_REFERENCE_ABSENT


def test_a_row_without_two_bracketing_anchors_is_unmatched():
    r0 = [row(1, 1, 0.0, 0.0)]                    # no anchor after the target
    gt = [row(1, 1, 0.0, 0.0), row(2, 1, 0.0, 0.0)]
    assert stv.classify([(SEQ, 2, 1)], r0, gt)[(SEQ, 2, 1)] == stv.ANCHOR_UNMATCHED


def test_the_gate_is_applied_before_assignment():
    # 0.6 overlap: admitted at the frozen 0.5 gate, refused at 0.7.
    r0 = [row(1, 1, 0.0, 0.0), row(3, 1, 0.0, 0.0)]
    gt = [row(1, 1, 0.0, 5.0), row(2, 1, 0.0, 5.0), row(3, 1, 0.0, 5.0)]
    assert stv.classify([(SEQ, 2, 1)], r0, gt, gate=0.5)[(SEQ, 2, 1)] \
        == stv.SEMANTICALLY_ADMITTED
    assert stv.classify([(SEQ, 2, 1)], r0, gt, gate=0.7)[(SEQ, 2, 1)] \
        == stv.ANCHOR_UNMATCHED


def test_reference_assignment_is_one_to_one():
    # Two predictions compete for one ground-truth box; only one may take it.
    r0 = [row(1, 1, 0.0, 0.0), row(1, 2, 0.0, 1.0)]
    gt = [row(1, 9, 0.0, 0.0)]
    assert len(stv.assign_reference(r0, gt)) == 1


def test_the_classes_partition_the_synthesized_set_exactly():
    r0, gt = _fixture()
    counts = stv.partition_counts(stv.classify([(SEQ, 2, 1)], r0, gt))
    assert set(counts) == set(stv.CLASSES)
    assert sum(counts.values()) == 1


def test_the_frozen_gate_and_sensitivity_grid_are_unchanged():
    assert stv.PRIMARY_IOU_GATE == 0.5
    assert stv.SENSITIVITY_GATES == (0.3, 0.4, 0.5, 0.6, 0.7)


# ------------------------------------------------------------------- ordering
@pytest.mark.parametrize("a,b,want", [
    (2.0, 1.0, ordering.A_GREATER),
    (1.0, 2.0, ordering.A_LESS),
    (1.0, 1.0, ordering.TIE),
])
def test_relation(a, b, want):
    assert ordering.relation(a, b) == want


@pytest.mark.parametrize("r0,r2,want", [
    (ordering.A_GREATER, ordering.A_GREATER, ordering.UNCHANGED),
    (ordering.A_GREATER, ordering.A_LESS, ordering.FLIP),
    (ordering.A_GREATER, ordering.TIE, ordering.TIE_CREATED),
    (ordering.TIE, ordering.A_LESS, ordering.TIE_BROKEN),
])
def test_transition(r0, r2, want):
    assert ordering.transition(r0, r2) == want


def test_matrix_reports_every_pair_not_only_the_flips():
    r0 = {"a": {"HOTA": 2.0}, "b": {"HOTA": 1.0}, "c": {"HOTA": 3.0}}
    r2 = {"a": {"HOTA": 1.0}, "b": {"HOTA": 2.0}, "c": {"HOTA": 3.0}}
    rows = ordering.matrix(r0, r2, ["a", "b", "c"], ["HOTA"])
    assert len(rows) == 3                      # C(3,2) pairs x 1 metric
    assert ordering.summary(rows)["n_pairs"] == 3


def test_a_missing_metric_is_reported_not_imputed():
    rows = ordering.matrix({"a": {"HOTA": 1.0}, "b": {}}, {"a": {"HOTA": 1.0}, "b": {}},
                           ["a", "b"], ["HOTA"])
    assert rows[0]["transition"] == "METRIC_NOT_AVAILABLE"
    assert rows[0]["r0"] is None and rows[0]["r2"] is None


# ----------------------------------------------------------------- materiality
def test_materiality_uses_the_frozen_threshold():
    assert materiality.THRESHOLD == 0.10
    assert materiality.classify(10, 100, 1000)["classification"] == materiality.MATERIAL
    assert materiality.classify(9, 100, 1000)["classification"] == materiality.NOT_MATERIAL


def test_materiality_always_reports_the_submission_wide_companion():
    out = materiality.classify(10, 100, 1000)
    assert out["fraction_of_synthesized"] == pytest.approx(0.10)
    assert out["fraction_of_R2_rows"] == pytest.approx(0.01)


def test_materiality_is_undefined_without_synthesized_rows():
    out = materiality.classify(0, 0, 100)
    assert out["classification"] == materiality.UNDEFINED
    assert out["fraction_of_synthesized"] is None


def test_materiality_is_always_descriptive():
    assert materiality.classify(50, 100, 100)["status"] == "DESCRIPTIVE"


# ---------------------------------------------------------------- state build
def test_R1_is_R0_plus_the_admitted_rows_only():
    r0 = {(SEQ, 1, 1): row(1, 1, 0.0, 0.0)}
    r2 = dict(r0)
    r2[(SEQ, 2, 1)] = row(2, 1, 0.0, 0.0)
    r2[(SEQ, 3, 1)] = row(3, 1, 0.0, 0.0)
    classes = {(SEQ, 2, 1): stv.SEMANTICALLY_ADMITTED,
               (SEQ, 3, 1): stv.ANCHOR_UNMATCHED}
    r1 = states.build_R1(r0, r2, classes)
    assert set(r1) == {(SEQ, 1, 1), (SEQ, 2, 1)}
    assert set(r0) <= set(r1) <= set(r2)


@pytest.mark.parametrize("family", ["GPR_REWRITE", "LINK_PLUS_SMOOTHING"])
def test_non_row_additive_families_get_no_manufactured_R1(family):
    status, reason = states.r1_status_for_non_row_additive(family)
    assert status == states.R1_STRUCTURALLY_UNDEFINED
    assert reason and "remov" in reason


# ---------------------------------------------------------------------- guard
def test_fixture_and_historical_modes_need_no_authorization():
    guard.require_authorization("fixture")
    guard.require_authorization("historical_v8")


def test_prospective_execution_is_refused_without_a_marker(tmp_path):
    with pytest.raises(guard.ExecutionNotAuthorized):
        guard.require_authorization("prospective_v9", repo_root=str(tmp_path))


def test_an_empty_marker_authorizes_nothing(tmp_path):
    target = tmp_path / guard.MARKER_FILE
    os.makedirs(target.parent, exist_ok=True)
    target.write_text("")
    assert guard.release_marker_present(str(tmp_path)) is False


def test_a_mot17_marker_never_licenses_a_mot20_run(tmp_path):
    target = tmp_path / guard.MARKER_FILE
    os.makedirs(target.parent, exist_ok=True)
    target.write_text("schema: x\nrun_order:\n  1: V9-MOT17-DEEPOCSORT-001\nauthorization: y\n")
    guard.require_cell_authorized("MOT17", "Deep-OC-SORT", "V9-MOT17-DEEPOCSORT-001",
                                  repo_root=str(tmp_path))
    with pytest.raises(guard.DatasetNotAuthorized):
        guard.require_cell_authorized("MOT20", "Deep-OC-SORT", "V9-MOT20-DEEPOCSORT-001",
                                      repo_root=str(tmp_path))


def test_a_run_id_must_name_its_own_dataset(tmp_path):
    with pytest.raises(guard.RunIdDatasetMismatch):
        guard.require_cell_authorized("MOT20", "Deep-OC-SORT", "V9-MOT17-DEEPOCSORT-001",
                                      repo_root=str(tmp_path))


def test_an_unknown_dataset_is_refused(tmp_path):
    with pytest.raises(guard.DatasetNotAuthorized):
        guard.require_cell_authorized("DanceTrack", "ByteTrack", "V9-DanceTrack-001",
                                      repo_root=str(tmp_path))


# ------------------------------------------------------------------- evaluator
def test_the_evaluator_pin_is_enforced_with_no_fallback(tmp_path):
    f = tmp_path / "s.txt"
    f.write_text("1,1,0,0,10,20,1,1,1\n")
    with pytest.raises(metrics.EvaluatorPinMismatch):
        metrics.freeze_inputs({"s": str(f)}, {"s": str(f)}, "deadbeef", {})


def test_freezing_inputs_records_the_hashes_it_was_given(tmp_path):
    f = tmp_path / "s.txt"
    f.write_text("1,1,0,0,10,20,1,1,1\n")
    out = metrics.freeze_inputs({"s": str(f)}, {"s": str(f)},
                                metrics.TRACKEVAL_COMMIT, {"BENCHMARK": "MOT17"})
    assert out["evaluator"] == "TrackEval"
    assert out["state_input_sha256"]["s"] == out["gt_input_sha256"]["s"]


def test_a_missing_state_yields_an_unavailable_delta():
    assert metrics.delta(None, {"HOTA": 1.0})["status"] == metrics.METRIC_NOT_AVAILABLE
