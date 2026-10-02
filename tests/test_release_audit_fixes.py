"""Regression tests for the pre-publication audit fixes.

Each test fails against the code as it stood before the fix, so a future change
that reintroduces the weakness is caught.
"""
from __future__ import annotations

import os

import pytest

from tracking_provenance_audit import guard, report, run_guard


# ------------------------------------------------- 2. report required fields
def _full_kwargs():
    kw = {k: None for k in report.REQUIRED}
    kw.pop("schema_version")
    return kw


def test_an_omitted_required_field_raises():
    kw = _full_kwargs()
    del kw["materiality"]
    with pytest.raises(ValueError, match="materiality"):
        report.build(**kw)


def test_a_required_field_explicitly_none_is_accepted():
    """Presence is the requirement, not a non-null value."""
    content = report.build(**_full_kwargs())
    assert content["materiality"] is None
    assert content["schema_version"] == report.SCHEMA_VERSION


# ----------------------------------------------------- 3. marker validation
def test_prose_containing_the_required_words_cannot_authorize(tmp_path):
    """A comment mentioning the field names is not a marker."""
    path = os.path.join(str(tmp_path), guard.MARKER_FILE)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("# schema: run_order: authorization: are described below\n")
    assert guard.release_marker_present(str(tmp_path)) is False
    with pytest.raises(guard.ExecutionNotAuthorized):
        guard.require_authorization("prospective_v9", str(tmp_path))


def test_a_yaml_scalar_is_not_a_marker(tmp_path):
    path = os.path.join(str(tmp_path), guard.MARKER_FILE)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("schema: run_order: authorization:\n")
    assert guard.release_marker_present(str(tmp_path)) is False


def test_a_mapping_with_every_required_key_is_a_marker(tmp_path):
    path = os.path.join(str(tmp_path), guard.MARKER_FILE)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("schema: v9-execution-authorization/1\n"
                 "run_order:\n  1: V9-MOT17-DEEPOCSORT-001\n"
                 "authorization: granted\n")
    assert guard.release_marker_present(str(tmp_path)) is True


def test_a_mot20_marker_must_declare_its_dataset_as_a_value(tmp_path):
    rel = guard.DATASET_MARKERS["MOT20"][0]
    path = os.path.join(str(tmp_path), rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("schema: v9/1\n"
                 "dataset: MOT17\n"            # wrong dataset, as a parsed value
                 "authorized_cells:\n  1: Deep-OC-SORT | V9-MOT20-DEEPOCSORT-001\n"
                 "authorization: granted\n")
    assert guard.authorized_cells("MOT20", str(tmp_path)) == set()


# ------------------------------------------- 4. checkpoint content hashes
def _sandbox(tmp_path, monkeypatch, run_id, contents):
    root = os.path.join(str(tmp_path), "sandbox")
    monkeypatch.setattr(run_guard, "SANDBOX_ROOT", root)
    wd = os.path.join(root, run_id, "external", "weights")
    os.makedirs(wd, exist_ok=True)
    for name, data in contents.items():
        with open(os.path.join(wd, name), "wb") as fh:
            fh.write(data)
    return root


def test_a_correctly_named_checkpoint_with_wrong_bytes_is_refused(tmp_path, monkeypatch):
    run_id = "V9-MOT20-DEEPOCSORT-001"
    _sandbox(tmp_path, monkeypatch, run_id,
             {name: b"not the real checkpoint" for name in run_guard.CLEAN_ASSETS})
    # the filename-only check is satisfied
    assert sorted(run_guard.reachable_weights(run_id)) == sorted(run_guard.CLEAN_ASSETS)
    # the content check is not
    with pytest.raises(run_guard.CacheContamination, match="ASSET_HASH_MISMATCH"):
        run_guard.require_clean_asset_isolation(run_id)


def test_hash_verification_is_on_by_default(tmp_path, monkeypatch):
    run_id = "V9-MOT20-DEEPOCSORT-001"
    _sandbox(tmp_path, monkeypatch, run_id,
             {name: b"wrong" for name in run_guard.CLEAN_ASSETS})
    with pytest.raises(run_guard.CacheContamination):
        run_guard.require_clean_asset_isolation(run_id)        # no argument
    run_guard.require_clean_asset_isolation(run_id, verify_hashes=False)  # opt-out


def test_preflight_cannot_skip_hash_verification():
    import inspect
    sig = inspect.signature(run_guard.preflight)
    assert "verify_hashes" not in sig.parameters


# ------------------------------------------------- 5. run_id path containment
@pytest.mark.parametrize("bad", ["../../etc", "../x", "/x", "x/y", "x\\y",
                                 ".", "..", "", "a/../../b", "./x"])
def test_an_unsafe_run_id_is_rejected(bad):
    with pytest.raises(run_guard.UnsafeRunId):
        run_guard.require_safe_run_id(bad)


def test_the_canonical_run_id_is_accepted():
    assert run_guard.require_safe_run_id("V9-MOT20-DEEPOCSORT-001") == \
        "V9-MOT20-DEEPOCSORT-001"
    assert run_guard.DEEP_MOT20_RUN_ID == "V9-MOT20-DEEPOCSORT-001"


@pytest.mark.parametrize("bad", ["../../etc", "/x", "x/y", "..", ""])
def test_path_builders_reach_the_validator(bad):
    """Every run_guard path constructor must refuse an unsafe run id."""
    for fn in (run_guard.sandbox_root, run_guard.canonical_artifacts,
               run_guard.reachable_weights, run_guard.dataset_root,
               run_guard.existing_artifacts):
        with pytest.raises(run_guard.UnsafeRunId):
            fn(bad)


def test_a_sandbox_path_stays_inside_the_configured_root():
    root = os.path.normpath(run_guard.SANDBOX_ROOT)
    built = os.path.normpath(run_guard.sandbox_root("V9-MOT20-DEEPOCSORT-001"))
    assert os.path.commonpath([root, built]) == root and built != root
