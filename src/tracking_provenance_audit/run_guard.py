"""External execution wrapper for the frozen Deep-OC-SORT x MOT20 run.

Closes findings V9-B30 (run-id / output non-reuse) and V9-B31 (cache identity).

NOTHING here changes tracking science. Upstream Deep-OC-SORT source is never
edited, never patched and never imported. The wrapper works entirely through the
process working directory, because every cache and output path in the upstream
code is CWD-relative:

    detector.py:23-25   ./cache/det_<weight_stem>.pkl
    embedding.py:21-22  ./cache/embeddings/<video_name>_embedding.pkl
    cmc.py:13-14        ./cache/affine_ocsort.pkl
    cmc.py:45-69        ./cache/cmc_files/{DanceTrack,MOT17_ablation,MOT20_ablation,MOTChallenge}/
    main.py:19          results/trackers/
    dataset.py:11       data/<DATASET>
    main.py:67-81       external/weights/<checkpoint>

Running `python <abs>/main.py` from a per-run sandbox therefore puts the
repository on sys.path[0] (so every module resolves to the frozen upstream tree)
while every one of those relative paths resolves inside the sandbox.

`cache/cmc_files` is NOT a generated cache: it holds the authors' precomputed
global-motion files and is a required scientific input. It is linked read-only.
The MOT20_ablation files are pre-sliced to the frozen validation half -- 214 /
1390 / 1202 / 1657 lines, local 1-indexed -- and cmc.py:56-58 registers them
under the bare tag `MOT20-0X`, which cmc.py:66-68 then refuses to overwrite with
the full-length MOTChallenge copies.
"""
from __future__ import annotations

import hashlib
import re
import os
from typing import Dict, List, Optional

# PATH NORMALISATION FOR RELEASE (no scientific change): the eight location
# constants below were absolute paths into the authors' execution host. They are
# now read from the environment, with workspace-relative defaults, so the guard
# is site-independent. No check, hash, refusal rule or ordering was altered --
# the guard still refuses on exactly the same conditions, and every SHA-256
# below is transcribed verbatim from the frozen record.
#
# Point these at your own checkouts before attempting a tracker run:
#   TPA_DEEP_REPO         upstream Deep-OC-SORT checkout (unmodified)
#   TPA_SANDBOX_ROOT      writable per-run sandbox root
#   TPA_TRACKER_INPUT     frozen MOT20 validation-half tracker input
#   TPA_DEPRECATED_ADAPTER  superseded adapter directory, refused if reachable
#   TPA_ASSET_STORE       checkpoint store holding exactly the two clean assets
#   TPA_TRACKEVAL_TRACKERS  TrackEval tracker-output root
#   TPA_STV_OUTPUT_ROOT   where this audit writes its MOT20 states
#
# See docs/REPRODUCIBILITY.md. Nothing in this repository can start a tracker
# run on its own: an authorization marker is still required (see guard.py).

_WS = os.environ.get("TPA_WORKSPACE", "workspace")

DEEP_REPO = os.environ.get("TPA_DEEP_REPO", os.path.join(_WS, "repos/Deep-OC-SORT"))
SANDBOX_ROOT = os.environ.get("TPA_SANDBOX_ROOT", os.path.join(_WS, "run_sandbox"))
TRACKER_INPUT = os.environ.get("TPA_TRACKER_INPUT",
                               os.path.join(_WS, "datasets/mot20_tracker_input/datasets/MOT20"))
DEPRECATED_ADAPTER = os.environ.get("TPA_DEPRECATED_ADAPTER",
                                    os.path.join(_WS, "datasets/mot20_population"))
ASSET_STORE = os.environ.get("TPA_ASSET_STORE", os.path.join(_WS, "assets"))

DEEP_MOT20_RUN_ID = "V9-MOT20-DEEPOCSORT-001"
RESULT_SPLIT = "MOT20-val"
TRACKEVAL_TRACKERS = os.environ.get(
    "TPA_TRACKEVAL_TRACKERS",
    os.path.join(_WS, "repos/TrackEval/data/trackers/mot_challenge"))
STV_OUTPUT_ROOT = os.environ.get(
    "TPA_STV_OUTPUT_ROOT",
    os.path.join(_WS, "results/tracking_provenance/deep_oc_sort_mot20"))

CLEAN_ASSETS = {
    "bytetrack_x_mot17.pth.tar":
        "e3945f3523fde1e107708aacd64dab0670c34e371d136e54587cac7a50d3cfba",
    "osnet_ain_ms_d_c.pth.tar":
        "2f38acc25e28cb29407635db2be315edc08d5457a904b72a9a11e427f41f3242",
}
# Never reachable from the sandbox: leaking or wrong-branch checkpoints.
FORBIDDEN_ASSETS = ("bytetrack_x_mot20.tar", "bytetrack_x_mot20.pth.tar",
                    "mot20_sbs_S50.pth", "mot17_sbs_S50.pth",
                    "ocsort_x_mot20.pth.tar", "bytetrack_ablation.pth.tar")

# Generated caches: must be run-scoped and empty before the canonical run.
GENERATED_CACHE_ENTRIES = ("embeddings", "affine_ocsort.pkl",
                           "det_bytetrack_x_mot17.pkl")
# Shipped scientific input: linked in, never regenerated.
SHIPPED_CACHE_ENTRIES = ("cmc_files",)


class RunIdReuse(RuntimeError):
    """A canonical artifact for this run id already exists."""


class CacheContamination(RuntimeError):
    """A cache from another dataset, checkpoint or configuration is reachable."""


class SandboxInvalid(RuntimeError):
    """The isolated run root is not in the state the contract requires."""


class ImportPrerequisiteMissing(RuntimeError):
    """A cwd-dependent import prerequisite is absent from the sandbox."""


class UnsafeRunId(ValueError):
    """A run id that cannot be used as a single path component."""


# A run id names one directory under a configured root. It is never a path.
_SAFE_RUN_ID = re.compile(r"\A[A-Za-z0-9][A-Za-z0-9._-]*\Z")


def require_safe_run_id(run_id: str) -> str:
    """Validate a run id before it is used to build any path.

    Every path in this module is rooted at a configured directory and extended
    by the run id, so an unconstrained run id would be a traversal primitive:
    `../../etc` would resolve outside the sandbox. This is the single gate that
    all run_guard path construction reaches, via sandbox_root().
    """
    if not isinstance(run_id, str) or not run_id:
        raise UnsafeRunId("run id must be a non-empty string")
    if run_id in (".", ".."):
        raise UnsafeRunId(f"run id {run_id!r} is a path reference, not a name")
    if os.path.isabs(run_id) or run_id.startswith(("/", "\\")):
        raise UnsafeRunId(f"run id {run_id!r} must not be an absolute path")
    if "/" in run_id or "\\" in run_id or os.sep in run_id or (os.altsep and os.altsep in run_id):
        raise UnsafeRunId(f"run id {run_id!r} must not contain a path separator")
    if not _SAFE_RUN_ID.match(run_id):
        raise UnsafeRunId(
            f"run id {run_id!r} must match {_SAFE_RUN_ID.pattern} "
            f"(letters, digits, dot, underscore, hyphen)")
    # Belt and braces: the joined path must stay inside its root.
    probe = os.path.normpath(os.path.join(SANDBOX_ROOT, run_id))
    root = os.path.normpath(SANDBOX_ROOT)
    if os.path.commonpath([root, probe]) != root or probe == root:
        raise UnsafeRunId(f"run id {run_id!r} escapes the sandbox root")
    return run_id


def sandbox_root(run_id: str) -> str:
    return os.path.join(SANDBOX_ROOT, require_safe_run_id(run_id))


def canonical_artifacts(run_id: str) -> Dict[str, str]:
    """Every canonical location that must be ABSENT before launch (V9-B30)."""
    require_safe_run_id(run_id)      # also reached via sandbox_root(); explicit
    sb = sandbox_root(run_id)
    return {
        "R0": os.path.join(sb, "results/trackers", RESULT_SPLIT, run_id),
        "R2": os.path.join(sb, "results/trackers", RESULT_SPLIT, run_id + "_post"),
        "run_log_dir": os.path.join(sb, "logs"),
        "run_manifest": os.path.join(sb, "manifest", "RUN_MANIFEST.json"),
        "trackeval_output": os.path.join(TRACKEVAL_TRACKERS, RESULT_SPLIT, run_id),
        "stv_output": os.path.join(STV_OUTPUT_ROOT, "audit"),
        "detector_cache": os.path.join(sb, "cache", "det_bytetrack_x_mot17.pkl"),
        "embedding_cache_dir": os.path.join(sb, "cache", "embeddings"),
    }


def existing_artifacts(run_id: str) -> Dict[str, str]:
    out = {}
    for name, path in canonical_artifacts(run_id).items():
        if name == "embedding_cache_dir":
            if os.path.isdir(path) and os.listdir(path):
                out[name] = path
            continue
        if os.path.exists(path):
            out[name] = path
    return out


def require_no_run_artifacts(run_id: str) -> None:
    """Refuse the launch if ANY canonical artifact exists. Never deletes."""
    present = existing_artifacts(run_id)
    if present:
        raise RunIdReuse(
            "REFUSE_RUN_ID_REUSE: canonical artifacts already exist for "
            f"{run_id!r}: {sorted(present)}. They are NOT deleted, NOT overwritten "
            "and NOT superseded by an auto-generated -002. A completed run id is "
            "single-use; reuse requires a new authorization, not a retry.")


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def reachable_weights(run_id: str) -> List[str]:
    d = os.path.join(sandbox_root(run_id), "external", "weights")
    return sorted(os.listdir(d)) if os.path.isdir(d) else []


def require_clean_asset_isolation(run_id: str, verify_hashes: bool = True) -> None:
    """Only the two clean checkpoints may be reachable from the sandbox.

    Content hashes are verified by default. A filename check alone cannot
    establish checkpoint identity: a file named `bytetrack_x_mot17.pth.tar`
    carrying different bytes would otherwise pass, and the MOT20 eligibility
    argument rests on which detector actually ran, not on what it was called.
    `verify_hashes=False` exists only for unit tests that construct a sandbox
    without real checkpoint bytes.
    """
    names = reachable_weights(run_id)
    if not names:
        raise SandboxInvalid(f"sandbox weights directory is missing for {run_id!r}")
    for bad in FORBIDDEN_ASSETS:
        if bad in names:
            raise CacheContamination(
                f"FORBIDDEN_ASSET_REACHABLE: {bad!r} is visible in the sandbox "
                f"weights directory for {run_id!r}.")
    if set(names) != set(CLEAN_ASSETS):
        raise SandboxInvalid(
            f"sandbox weights must be exactly {sorted(CLEAN_ASSETS)}, found {names}")
    if verify_hashes:
        base = os.path.join(sandbox_root(run_id), "external", "weights")
        for name, want in CLEAN_ASSETS.items():
            got = sha256_file(os.path.join(base, name))
            if got != want:
                raise CacheContamination(
                    f"ASSET_HASH_MISMATCH: {name} is {got}, expected {want}")


def require_cache_isolation(run_id: str) -> None:
    """No cache from another dataset, checkpoint or configuration is reachable."""
    cache = os.path.join(sandbox_root(run_id), "cache")
    if not os.path.isdir(cache):
        raise SandboxInvalid(f"sandbox cache directory is missing for {run_id!r}")
    entries = set(os.listdir(cache))
    unexpected = entries - set(GENERATED_CACHE_ENTRIES) - set(SHIPPED_CACHE_ENTRIES)
    if unexpected:
        raise CacheContamination(
            f"UNEXPECTED_CACHE_ENTRY: {sorted(unexpected)} in {cache}")
    for stale in ("det_bytetrack_ablation.pkl", "det_bytetrack_x_mot20.pkl",
                  "det_ocsort_x_mot20.pkl", "affine_ocsort.pkl"):
        if stale in entries:
            raise CacheContamination(
                f"STALE_CACHE_REACHABLE: {stale!r} in {cache}")
    emb = os.path.join(cache, "embeddings")
    if os.path.isdir(emb):
        leftovers = sorted(os.listdir(emb))
        if leftovers:
            raise CacheContamination(
                f"EMBEDDING_CACHE_NOT_EMPTY: {leftovers} in {emb}. The frozen run "
                "requires a fresh namespace; MOT17 embeddings must never be "
                "consumed and MOT20 embeddings must never be reused across "
                "ReID configurations.")
    cmc = os.path.join(cache, "cmc_files")
    if not os.path.isdir(cmc):
        raise SandboxInvalid(
            "cache/cmc_files is a REQUIRED scientific input (cmc.py:45-69), not a "
            "generated cache; it must be linked into the sandbox.")


def cmc_alignment(run_id: str) -> Dict[str, int]:
    """Line counts of the MOT20 global-motion files the run will consume."""
    d = os.path.join(sandbox_root(run_id), "cache", "cmc_files", "MOT20_ablation")
    out = {}
    for name in sorted(os.listdir(d)):
        seq = name.replace("GMC-", "").replace(".txt", "")
        with open(os.path.join(d, name), encoding="utf-8") as fh:
            out[seq] = sum(1 for line in fh if line.strip())
    return out


def dataset_root(run_id: str) -> Optional[str]:
    p = os.path.join(sandbox_root(run_id), "data", "MOT20")
    return os.path.realpath(p) if os.path.exists(p) else None


def require_corrected_adapter(run_id: str) -> None:
    """The sandbox must see the full-sequence adapter, not the pre-halved one."""
    root = dataset_root(run_id)
    if root is None:
        raise SandboxInvalid(f"sandbox data/MOT20 is missing for {run_id!r}")
    if os.path.realpath(root) == os.path.realpath(DEPRECATED_ADAPTER):
        raise SandboxInvalid(
            "DEPRECATED_HALVED_ADAPTER: data/MOT20 resolves to the pre-halved "
            "population, which the pipeline would halve a second time (2228 "
            "frames instead of 4463). Use the corrected full-sequence adapter.")
    if os.path.realpath(root) != os.path.realpath(TRACKER_INPUT):
        raise SandboxInvalid(
            f"data/MOT20 resolves to {root}, expected {TRACKER_INPUT}")
    for seq, length in (("MOT20-01", 429), ("MOT20-02", 2782),
                        ("MOT20-03", 2405), ("MOT20-05", 3315)):
        img = os.path.join(root, "train", seq, "img1")
        n = len(os.listdir(img))
        if n != length:
            raise SandboxInvalid(
                f"{seq} exposes {n} images, expected the FULL native {length}")


# Deep-OC-SORT/external/__init__.py:3 does
#     sys.path.append(os.path.join(os.getcwd(), "external"))
# i.e. it appends the CURRENT WORKING DIRECTORY's external/, not the package's.
# Running from a sandbox therefore breaks the bare `fast_reid` import in
# external/adaptors/fastreid_adaptor.py, which embedding.py imports at module
# level -- main.py would die at import time. Found by the record 12B preflight
# (finding V9-B36) and fixed by exposing exactly that one package.
CWD_IMPORT_PREREQUISITES = ("fast_reid",)


def require_import_prerequisites(run_id: str) -> None:
    ext = os.path.join(sandbox_root(run_id), "external")
    for name in CWD_IMPORT_PREREQUISITES:
        target = os.path.join(ext, name)
        if not os.path.exists(target):
            raise ImportPrerequisiteMissing(
                f"CWD_IMPORT_PREREQUISITE_MISSING: {name!r} is not present at {target}. "
                "Deep-OC-SORT/external/__init__.py appends os.getcwd()/external to "
                "sys.path, so this bare import only resolves when the sandbox exposes "
                "it. Without it main.py raises ModuleNotFoundError at import time.")


def preflight(run_id: str = DEEP_MOT20_RUN_ID) -> dict:
    """All launch preconditions. Raises on the first violation; never mutates.

    Checkpoint content hashes are always verified here: the canonical execution
    path has no option to skip them.
    """
    require_no_run_artifacts(run_id)
    require_corrected_adapter(run_id)
    require_clean_asset_isolation(run_id, verify_hashes=True)
    require_cache_isolation(run_id)
    require_import_prerequisites(run_id)
    return {
        "run_id": run_id,
        "sandbox": sandbox_root(run_id),
        "dataset_root": dataset_root(run_id),
        "reachable_weights": reachable_weights(run_id),
        "cmc_alignment": cmc_alignment(run_id),
        "import_prerequisites": list(CWD_IMPORT_PREREQUISITES),
        "canonical_artifacts_absent": sorted(canonical_artifacts(run_id)),
        "asset_hashes_verified": True,
        "launch_permitted_by_run_guard": True,
        "execution_authorized": False,
        "note": ("the run guard only certifies isolation and non-reuse. It confers "
                 "NO execution authorization; that requires a MOT20 marker."),
    }
