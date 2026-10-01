"""Integrity tests for the release itself.

These check that the published tables, the frozen configuration files and the
release manifest agree, and that nothing in the tree claims to redistribute a
dataset or a checkpoint.
"""
from __future__ import annotations

import csv
import json
import os
import sys

import pytest
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from tracking_provenance_audit import materiality, metrics, ordering, stv  # noqa: E402

CLASS_COLS = ("semantically_admitted", "anchor_unmatched",
              "anchor_id_mismatch", "target_reference_absent")


def load_csv(*p):
    with open(os.path.join(ROOT, *p), newline="") as f:
        return list(csv.DictReader(f))


def load_json(*p):
    with open(os.path.join(ROOT, *p)) as f:
        return json.load(f)


def load_yaml(*p):
    with open(os.path.join(ROOT, *p)) as f:
        return yaml.safe_load(f)


# ------------------------------------------------------- configs match source
def test_frozen_gate_matches_the_source_constant():
    assert load_yaml("configs", "frozen", "admission_stv.yaml")["primary_iou_gate"] \
        == stv.PRIMARY_IOU_GATE


def test_frozen_sensitivity_grid_matches_the_source_constant():
    assert tuple(load_yaml("configs", "frozen", "admission_stv.yaml")["sensitivity_gates"]) \
        == stv.SENSITIVITY_GATES


def test_frozen_evaluator_pin_matches_the_source_constant():
    assert load_yaml("configs", "frozen", "evaluator.yaml")["evaluator_commit"] \
        == metrics.TRACKEVAL_COMMIT


def test_frozen_materiality_threshold_matches_the_source_constant():
    assert load_yaml("configs", "frozen", "materiality.yaml")["threshold_frozen_at"] \
        == materiality.THRESHOLD


# --------------------------------------------------------------- result tables
def test_the_ordering_matrix_is_complete():
    rows = load_csv("results", "mot17", "ordering_matrix.csv")
    pairs = {(r["deployment_a"], r["deployment_b"]) for r in rows}
    assert len(rows) == 50 and len(pairs) == 10
    assert {r["metric"] for r in rows} == set(metrics.METRICS)


def test_every_ordering_transition_re_derives_from_its_values():
    for r in load_csv("results", "mot17", "ordering_matrix.csv"):
        r0 = ordering.relation(float(r["a_R0"]), float(r["b_R0"]))
        r2 = ordering.relation(float(r["a_R2"]), float(r["b_R2"]))
        assert r0 == r["relation_R0"] and r2 == r["relation_R2"]
        assert ordering.transition(r0, r2) == r["transition"]


def test_the_published_ordering_summary_is_what_the_engine_counts():
    rows = load_csv("results", "mot17", "ordering_matrix.csv")
    got = ordering.summary([dict(a=r["deployment_a"], b=r["deployment_b"],
                                 metric=r["metric"], r0=r["relation_R0"],
                                 r2=r["relation_R2"], transition=r["transition"])
                            for r in rows])
    want = load_json("results", "mot17", "ordering_summary.json")["summary"]
    assert got == want


@pytest.mark.parametrize("table", ["results/mot17/stv_composition.csv"])
def test_admission_classes_partition_every_synthesized_set(table):
    for r in load_csv(*table.split("/")):
        if r["n_synthesized"] == "STRUCTURALLY_UNDEFINED":
            assert all(r[k] == "" for k in CLASS_COLS)
            continue
        assert sum(int(r[k]) for k in CLASS_COLS) == int(r["n_synthesized"])


def test_published_non_admission_fractions_re_derive():
    for r in load_csv("results", "mot17", "stv_composition.csv"):
        if r["n_synthesized"] == "STRUCTURALLY_UNDEFINED":
            continue
        v = materiality.classify(int(r["non_admitted"]), int(r["n_synthesized"]), 0)
        assert v["fraction_of_synthesized"] == pytest.approx(
            float(r["non_admitted_fraction"]))


def test_mot20_per_sequence_counts_sum_to_the_aggregate():
    rows = load_csv("results", "mot20", "deep_oc_sort_stv.csv")
    agg = next(r for r in rows if r["sequence"] == "ALL")
    per = [r for r in rows if r["sequence"] != "ALL"]
    for col in ("n_synthesized",) + CLASS_COLS:
        assert sum(int(r[col]) for r in per) == int(agg[col])


def test_the_mot20_eligibility_ledger_is_complete():
    cells = load_csv("results", "mot20", "eligibility.csv")
    ctx = load_json("results", "mot20", "eligibility_context.json")
    assert len(cells) == ctx["counts"]["TOTAL"] == 7
    assert sum(v for k, v in ctx["counts"].items() if k != "TOTAL") == 7
    assert sum(1 for r in cells if r["checkpoint_status"] == "NO_KNOWN_EVAL_LEAKAGE") == 1


def test_the_sensitivity_grid_covers_the_frozen_gates():
    rows = load_csv("results", "stv_sensitivity", "summary.csv")
    assert {float(r["iou_gate"]) for r in rows} == set(stv.SENSITIVITY_GATES)


def test_sensitivity_classes_partition_at_every_gate():
    for r in load_csv("results", "stv_sensitivity", "summary.csv"):
        total = int(r["n_synth"])
        parts = (int(r["n_admitted"]) + int(r["n_unmatched"])
                 + int(r["n_id_mismatch"]) + int(r["n_reference_absent"]))
        assert parts == total
        assert int(r["n_nonadmitted"]) == total - int(r["n_admitted"])


# ------------------------------------------------------------------- manifest
def test_the_release_manifest_covers_every_published_data_file():
    man = load_json("provenance", "RELEASE_MANIFEST.json")
    listed = {f["public_file"] for f in man["files"]}
    on_disk = set()
    for sub in ("results", "metadata", "provenance/frozen_records", "configs/frozen"):
        base = os.path.join(ROOT, sub)
        for dirpath, _, names in os.walk(base):
            for n in names:
                rel = os.path.relpath(os.path.join(dirpath, n), ROOT)
                on_disk.add(rel.replace(os.sep, "/"))
    missing = on_disk - listed
    assert not missing, f"unlisted files: {sorted(missing)[:5]}"


def test_no_released_file_is_dataset_or_checkpoint_material():
    man = load_json("provenance", "RELEASE_MANIFEST.json")
    bad = [f["public_file"] for f in man["files"]
           if f["redistribution"] in ("DATASET_DERIVED", "CHECKPOINT_DERIVED")]
    assert not bad


def test_no_private_path_email_or_host_survives_in_the_tree():
    """No absolute path, host or personal address from the research host leaks.

    The patterns are assembled from fragments so that this file does not itself
    contain the literals it searches for.
    """
    import re

    user = "anastas" + "iia"
    patterns = [
        "/da" + "ta/" + user,
        "/ho" + "me/[a-z]",
        "/ro" + "ot/[a-z]",
        "C:" + chr(92) + chr(92) + "?Users",
        "/Us" + "ers/[A-Z]",
        "mini" + "forge",
        "ipt" + "ime",
        "@kw" + chr(92) + ".ac" + chr(92) + ".kr",
    ]
    pattern = re.compile("|".join(patterns))

    hits = []
    for dirpath, dirnames, names in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__",
                                                        ".pytest_cache")]
        for n in names:
            p = os.path.join(dirpath, n)
            try:
                text = open(p, encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            if pattern.search(text):
                hits.append(os.path.relpath(p, ROOT))
    assert not hits, f"private identifiers found in: {hits}"


# ------------------------------------------------------------ controlled arm
def test_posetrack_classes_partition_under_every_segmentation_rule():
    rows = load_csv("results", "controlled", "posetrack21_applicability.csv")
    assert len(rows) == 3
    for r in rows:
        parts = sum(int(r[k]) for k in ("eligible", "leading", "trailing", "no_anchor"))
        assert parts == int(r["scoreable_occluded_targets"]) == int(r["partition_sum"])
        assert float(r["eligible_pct"]) + float(r["ineligible_pct"]) == pytest.approx(100.0)


def test_the_posetrack_target_count_is_rule_invariant():
    rows = load_csv("results", "controlled", "posetrack21_applicability.csv")
    rec = load_json("provenance", "frozen_records", "controlled",
                    "56_POSETRACK21_SEGMENTATION_SENSITIVITY.json")
    counts = {int(r["scoreable_occluded_targets"]) for r in rows}
    assert len(counts) == 1
    assert counts.pop() == rec["internal_validation"]["target_count"]


def test_posetrack_bootstrap_intervals_bracket_their_estimates():
    for r in load_csv("results", "controlled", "posetrack21_bootstrap.csv"):
        assert float(r["ci95_lo"]) <= float(r["point_estimate"]) <= float(r["ci95_hi"])


def test_the_ntu_reversal_changes_sign_between_supports():
    h = load_json("results", "controlled", "ntu_support_accounting.json")["headline"]
    assert h["before"]["paired_mae_minus_linear"] < 0
    assert h["after"]["paired_mae_minus_linear_common_support"] > 0
    assert h["before"]["ci_hi"] < 0 < h["after"]["ci_lo_common_support"]
    assert h["after"]["n_gaps_common_support"] == h["before"]["n_gaps"] - 900


def test_object_trajectory_partitions_are_exact_on_both_populations():
    rows = load_csv("results", "controlled", "objecttraj_applicability.csv")
    assert {r["population"] for r in rows} == {"bdd", "mot17"}
    for r in rows:
        parts = sum(int(r[k]) for k in ("eligible", "leading", "trailing", "no_anchor"))
        assert parts == int(r["scoreable_targets"])
        assert sum(float(r[k]) for k in ("eligible_fraction", "leading_fraction",
                                         "trailing_fraction", "no_anchor_fraction")) \
            == pytest.approx(1.0)


def test_kitti_strata_sum_to_the_pooled_partition():
    rows = load_csv("results", "controlled", "kitti_applicability.csv")
    pooled = next(r for r in rows if r["stratum"] == "all")
    for prefix in ("occlusion=", "category="):
        group = [r for r in rows if r["stratum"].startswith(prefix)]
        assert group
        assert sum(int(r["scoreable_targets"]) for r in group) \
            == int(pooled["scoreable_targets"])


def test_the_kitti_hypothesis_matches_its_frozen_record():
    released = load_json("results", "controlled", "kitti_hypothesis.json")
    frozen = load_json("provenance", "frozen_records", "controlled",
                       "KITTI_hypothesis_status.json")
    assert released == frozen
    assert released["ineligible_fraction"] >= released["threshold"]
    assert released["status"] == "SUPPORTED"


def test_jta_partition_is_exact_and_rates_recompute():
    r = load_csv("results", "controlled", "jta_applicability.csv")[0]
    tot = int(r["primary_targets"])
    parts = sum(int(r[k]) for k in ("eligible_strictly_interior", "ineligible_leading",
                                    "ineligible_trailing", "no_anchor"))
    assert parts == tot == int(r["partition_sum"])
    assert float(r["eligible_rate_pct"]) == pytest.approx(
        100.0 * int(r["eligible_strictly_interior"]) / tot)
    assert float(r["eligible_rate_pct"]) + float(r["excluded_undefined_rate_pct"]) \
        == pytest.approx(100.0)


def test_the_jta_headline_refuses_an_architecture_verdict():
    h = load_json("results", "controlled", "jta_headline.json")
    assert h["learned_worse_than_best_classical_by_factor"] == pytest.approx(
        h["learned_best_estimate"] / h["classical_best_estimate"])
    assert "SENSITIVITY" in h["what_this_result_is"].upper()
    assert h["what_this_result_is_NOT"]




def test_the_learned_input_contract_accounts_for_every_slot():
    ic = load_json("results", "controlled", "learned_input_contract.json")["input_contract"]
    assert ic["slots"] == 17
    assert ic["available"] == 13
    assert len(ic["unavailable_ntu_slots"]) == 4
    assert ic["available"] + len(ic["unavailable_ntu_slots"]) == ic["slots"]
    assert ic["never_padding"] is True
    assert ic["confidence_available"] is False and ic["confidence_synthesized"] is False


def test_every_beta_row_has_a_bracketing_interval():
    for r in load_csv("results", "controlled", "learned_beta_by_phi.csv"):
        assert float(r["ci95_lo"]) <= float(r["beta"]) <= float(r["ci95_hi"])


def test_the_architecture_claim_stays_unresolved():
    d = load_json("results", "controlled", "learned_architecture_diagnostics.json")
    assert "unresolved" in d["note"].lower()
    assert "not a proposed method" in d["note"].lower()
    assert d["estimand"]


# --------------------------------------------------------------- asset table
def test_every_hashed_checkpoint_has_a_full_digest_and_a_byte_size():
    rows = load_csv("metadata", "external_assets.csv")
    hashed = [r for r in rows if r["sha256"]]
    assert len(hashed) >= 5
    for r in hashed:
        assert len(r["sha256"]) == 64 and all(c in "0123456789abcdef" for c in r["sha256"])
        assert r["size_bytes"].isdigit() and int(r["size_bytes"]) > 0
        assert r["frozen_record"], r["asset"]


def test_the_two_mot17_ablation_detectors_are_byte_identical():
    rows = {r["asset"]: r for r in load_csv("metadata", "external_assets.csv")}
    a = rows["bytetrack_ablation.pth.tar"]
    b = rows["ocsort_mot17_ablation.pth.tar"]
    assert a["sha256"] == b["sha256"] and a["size_bytes"] == b["size_bytes"]
    assert rows["bytetrack_x_mot17.pth.tar"]["sha256"] != a["sha256"]


def test_no_asset_row_claims_redistribution():
    for r in load_csv("metadata", "external_assets.csv"):
        assert r["redistributed_here"] == "no", r["asset"]


# ------------------------------------------------------------------ path map
def test_the_path_map_resolves_every_public_equivalent():
    pm = load_json("provenance", "path_map.json")
    for ref, target in pm["public_equivalent"].items():
        assert os.path.exists(os.path.join(ROOT, target)), (ref, target)
    total = sum(pm["counts"].values())
    assert total == (len(pm["public_equivalent"])
                     + len(pm["upstream_third_party"]["paths"])
                     + len(pm["not_released"]["paths"]))


def test_the_release_requires_python_39_or_newer():
    assert sys.version_info >= (3, 9), (
        "the released audit core uses dict-union (PEP 584) and requires Python 3.9+")
