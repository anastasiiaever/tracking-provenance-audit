"""The verifiers must FAIL on corrupted data, not merely pass on good data.

Each test copies the whole release into a temporary directory, corrupts exactly
one value there, runs the relevant verifier against the copy, and asserts a
non-zero exit. Authoritative files are never modified: everything happens inside
pytest's tmp_path.
"""
from __future__ import annotations

import csv
import json
import os
import shutil
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _clone(tmp_path):
    dst = os.path.join(str(tmp_path), "release")
    shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns(
        ".git", "__pycache__", ".pytest_cache", "*.pyc"))
    return dst


def _run(repo, script):
    return subprocess.run([sys.executable, os.path.join(repo, "scripts", script)],
                          capture_output=True, text=True, cwd=repo)


def _baseline_passes(repo, script):
    assert _run(repo, script).returncode == 0, f"{script} should pass before corruption"


def _rewrite_csv(path, mutate):
    rows = list(csv.DictReader(open(path)))
    fields = list(rows[0].keys())
    mutate(rows)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def test_a_changed_mot17_admission_count_is_detected(tmp_path):
    repo = _clone(tmp_path)
    _baseline_passes(repo, "verify_admission.py")

    def bump(rows):
        for r in rows:
            if r["deployment"] == "ByteTrack":
                r["anchor_id_mismatch"] = str(int(r["anchor_id_mismatch"]) + 1)
    _rewrite_csv(os.path.join(repo, "results/mot17/stv_composition.csv"), bump)

    out = _run(repo, "verify_admission.py")
    assert out.returncode != 0, "a changed STV class count must fail the verifier"


def test_a_changed_ordering_cell_is_detected(tmp_path):
    repo = _clone(tmp_path)
    _baseline_passes(repo, "verify_ordering.py")

    def flip(rows):
        r = rows[0]
        r["relation_R2"] = "A_LESS" if r["relation_R2"] == "A_GREATER" else "A_GREATER"
    _rewrite_csv(os.path.join(repo, "results/mot17/ordering_matrix.csv"), flip)

    out = _run(repo, "verify_ordering.py")
    assert out.returncode != 0, "a flipped ordering relation must fail the verifier"


def test_a_frozen_record_disagreeing_with_a_public_result_is_detected(tmp_path):
    """Corrupt the FROZEN side instead of the public side: the cross-check must
    still fire. This is what proves the verifier is not merely self-consistent."""
    repo = _clone(tmp_path)
    _baseline_passes(repo, "verify_ordering.py")

    p = os.path.join(repo, "provenance/frozen_records/07_ORDERING_MATRIX.json")
    rec = json.load(open(p))
    cell = rec["matrix"][0]
    cell["r2"] = "A_LESS" if cell["r2"] == "A_GREATER" else "A_GREATER"
    json.dump(rec, open(p, "w"), indent=1)

    out = _run(repo, "verify_ordering.py")
    assert out.returncode != 0, "a frozen record disagreeing with results must fail"


def test_a_changed_mot20_eligibility_verdict_is_detected(tmp_path):
    repo = _clone(tmp_path)
    _baseline_passes(repo, "verify_mot20_eligibility.py")

    def relabel(rows):
        for r in rows:
            if r["checkpoint_status"].strip() == "CONFIRMED_EVAL_LEAKAGE":
                r["checkpoint_status"] = "NO_KNOWN_EVAL_LEAKAGE"
                break
    _rewrite_csv(os.path.join(repo, "results/mot20/eligibility.csv"), relabel)

    out = _run(repo, "verify_mot20_eligibility.py")
    assert out.returncode != 0, "a changed eligibility verdict must fail the verifier"


def test_an_unresolved_cell_relabelled_as_ineligible_is_detected(tmp_path):
    """UNRESOLVED and INELIGIBLE_TRAINING_OVERLAP must not be interchangeable."""
    repo = _clone(tmp_path)
    _baseline_passes(repo, "verify_mot20_eligibility.py")

    def relabel(rows):
        for r in rows:
            if r["checkpoint_status"].strip().startswith("MIXED"):
                r["checkpoint_status"] = "CONFIRMED_EVAL_LEAKAGE"
                break
    _rewrite_csv(os.path.join(repo, "results/mot20/eligibility.csv"), relabel)

    out = _run(repo, "verify_mot20_eligibility.py")
    assert out.returncode != 0, "collapsing UNRESOLVED into INELIGIBLE must fail"


def test_an_inconsistent_historical_row_total_is_detected(tmp_path):
    repo = _clone(tmp_path)
    _baseline_passes(repo, "verify_admission.py")

    def bump(rows):
        for r in rows:
            if r["deployment"] == "OC-SORT":
                r["n_r2"] = str(int(r["n_r2"]) + 10)   # breaks n_synth == n_r2 - n_r0
    _rewrite_csv(os.path.join(repo, "results/mot17/row_totals.csv"), bump)

    out = _run(repo, "verify_admission.py")
    assert out.returncode != 0, "n_synth != n_r2 - n_r0 must fail the verifier"


def test_a_row_total_that_breaks_a_published_range_is_detected(tmp_path):
    """Change n_r2 and n_synth together so the identity still holds but the
    derived fraction moves: the range check must catch it."""
    repo = _clone(tmp_path)
    _baseline_passes(repo, "verify_admission.py")

    def shift(rows):
        for r in rows:
            if r["deployment"] == "BoT-SORT":
                r["n_r0"] = str(int(r["n_r0"]) - 4000)
                r["n_synth"] = str(int(r["n_r2"]) - int(r["n_r0"]))
    _rewrite_csv(os.path.join(repo, "results/mot17/row_totals.csv"), shift)

    out = _run(repo, "verify_admission.py")
    assert out.returncode != 0, "a row total that moves a published range must fail"
