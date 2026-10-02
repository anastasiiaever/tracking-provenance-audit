"""Dataset adapters. Only frozen semantics are implemented."""
from __future__ import annotations
import hashlib
from typing import Dict

STOPPED = "STOPPED_DATASET_NOT_ACQUIRED"

# Frozen MOT17 val-half population (02_PROSPECTIVE_PROTOCOL.json).
MOT17_SEQUENCES = [
    ("MOT17-02-FRCNN", 600, 301, [302, 600], 299,
     "51390514c58bcd580a1a614a93d84ed1241bd3708cd4f3e7a4a35f508f8d2ff8"),
    ("MOT17-04-FRCNN", 1050, 526, [527, 1050], 524,
     "7c849ece19e0b28e73b71c3ea38a0ecc516fbd903f8108c88d3a921299107f9d"),
    ("MOT17-05-FRCNN", 837, 419, [420, 837], 418,
     "bbc278f8ca51f7ea75d47e7ed2e5f40a1c8734f3f6e777bcaf86b1a0d24137f1"),
    ("MOT17-09-FRCNN", 525, 263, [264, 525], 262,
     "5d6999a90f484ccc0bc2209b3b90877bee094dabee49c188443576fda67e3b14"),
    ("MOT17-10-FRCNN", 654, 328, [329, 654], 326,
     "b5e5afb90a4974bbf8107743886b953bcddfec1d5a405ba0fe1314411e583090"),
    ("MOT17-11-FRCNN", 900, 451, [452, 900], 449,
     "8b95ce717406def67f9437c461e5b56a42d696fc25fb0dc72219d6d7337c6507"),
    ("MOT17-13-FRCNN", 750, 376, [377, 750], 374,
     "1f314df9b7ac28969f11aafd072db091d3e3ad7fbc272373232a7cd68de44ea2"),
]
MOT17_TOTAL_FRAMES = 2652
MOT17_MANIFEST_SHA256 = "9dd181ee08ead5fd8818735b8a0e1edeb11c88d7bdc0c79b7e0f45a821577254"


def mot17_manifest() -> dict:
    seqs = [dict(sequence=s, native_length=n, rebase_offset=r,
                 native_frames_retained=fr, val_half_length=L, gt_sha256=h)
            for s, n, r, fr, L, h in MOT17_SEQUENCES]
    rec = "".join(
        f"{s['sequence']}|{s['native_frames_retained']}|{s['rebase_offset']}|"
        f"{s['val_half_length']}|{s['gt_sha256']}\n"
        for s in sorted(seqs, key=lambda x: x["sequence"]))
    return dict(dataset="MOT17", status="FROZEN", sequences=seqs,
                total_val_half_frames=sum(s["val_half_length"] for s in seqs),
                population_manifest_sha256=hashlib.sha256(rec.encode()).hexdigest())


def verify_mot17_manifest() -> bool:
    m = mot17_manifest()
    return (m["population_manifest_sha256"] == MOT17_MANIFEST_SHA256
            and m["total_val_half_frames"] == MOT17_TOTAL_FRAMES
            and len(m["sequences"]) == 7)


# Frozen MOT20 population, materialised in 09B and unchanged since
# (tag tpami-v9-mot20-population-materialized-20260831).  The hash is the
# canonical hash of 09B_MOT20_MATERIALIZED_POPULATION.json, asserted here as a
# constant. That record is part of the private research tree and is not
# published, so this repository states the hash rather than recomputing it;
# mot20_manifest() names the record under `record` so the source is citable.
MOT20_SEQUENCES = [
    ("MOT20-01", 429, 216, 429, 214,
     "e768e229779ca13d6dc9f9da7adb122d2cee9fb22a320574ce2f087889219385"),
    ("MOT20-02", 2782, 1393, 2782, 1390,
     "d44327aa3fdc5f0ca493e34826c55bbaca11da1a35856c5852371481558d695f"),
    ("MOT20-03", 2405, 1204, 2405, 1202,
     "6a41a39c498d15050ac47362d3c57ee08692c77ff183d40802ef1904dafded5e"),
    ("MOT20-05", 3315, 1659, 3315, 1657,
     "b0e0420dfb061b6d1d631c16d538e41c0deea607b6b6086ca82d4f114eef388b"),
]
MOT20_TOTAL_FRAMES = 4463
MOT20_MANIFEST_SHA256 = (
    "aabe4907077934fb834a7639b9722b9120de0a007553bbc98a6132b768d3e232")
MOT20_MATERIALIZED = "DATASET_MATERIALIZED_FROM_VERIFIED_MIRROR"
MOT20_PROVENANCE = "MIRROR_TRANSPORT_FALLBACK"
MOT20_RECORD = "docs/tpami_v9_tracking_provenance/09B_MOT20_MATERIALIZED_POPULATION.json"

# Cell licensing is NOT generic. Only the single cell the readiness audit
# classified NO_KNOWN_EVAL_LEAKAGE (record 10A) may resolve an executable MOT20
# population. Every other MOT20 cell stays non-executable, and enabling one is a
# protocol amendment, not a code change.
MOT20_LICENSED_CELLS = frozenset({("Deep-OC-SORT", "MOT20")})
CELL_NOT_LICENSED = "MOT20_CELL_NOT_LICENSED_FOR_EXECUTION"


def mot20_manifest() -> dict:
    seqs = [dict(sequence=s, native_length=n, first_native_frame=lo,
                 last_native_frame=hi, included_frame_count=c, gt_sha256=h,
                 local_to_native_offset=lo - 1)
            for s, n, lo, hi, c, h in MOT20_SEQUENCES]
    return dict(dataset="MOT20", status=MOT20_MATERIALIZED, sequences=seqs,
                total_frames=sum(s["included_frame_count"] for s in seqs),
                population_manifest_sha256=MOT20_MANIFEST_SHA256,
                provenance_status=MOT20_PROVENANCE,
                provenance_caveat=("Kaggle mirror; byte identity to an official "
                                   "MOT20.zip is NOT established and no wording may "
                                   "claim a direct MOTChallenge download"),
                record=MOT20_RECORD)



def stopped_manifest(dataset: str) -> dict:
    """No corpus: schema support only. Manifests are never fabricated."""
    return dict(dataset=dataset, status=STOPPED,
                population_manifest_sha256=None, sequences=None,
                reason=("corpus not acquired; the frozen population rule exists but "
                        "cannot be materialised. Acquiring the corpus later "
                        "materialises the frozen population; it must not redefine it."))


def unlicensed_mot20_manifest(pipeline) -> dict:
    """The corpus exists, but this cell may not execute against it.

    Reporting STOPPED_DATASET_NOT_ACQUIRED here would be false: the population
    was materialised in 09B. The cell is non-executable for its own reason,
    recorded in 10 and 10A.
    """
    m = mot20_manifest()
    m["status"] = CELL_NOT_LICENSED
    m["licensed_for_execution"] = False
    m["pipeline"] = pipeline
    m["reason"] = ("the MOT20 population is materialised, but this cell is not "
                   "licensed for execution: see 10_MOT20_EXECUTION_READINESS and "
                   "10A_MOT20_READINESS_CORRECTION. Licensing a cell is a protocol "
                   "amendment, not a code change.")
    return m


def cell_is_licensed(pipeline, dataset: str) -> bool:
    if dataset == "MOT17":
        return True
    if dataset == "MOT20":
        return (pipeline, dataset) in MOT20_LICENSED_CELLS
    return False


def get_manifest(dataset: str, pipeline=None) -> dict:
    if dataset == "MOT17":
        return mot17_manifest()
    if dataset == "MOT20":
        if cell_is_licensed(pipeline, dataset):
            m = mot20_manifest()
            m["licensed_for_execution"] = True
            m["pipeline"] = pipeline
            return m
        return unlicensed_mot20_manifest(pipeline)
    if dataset == "DanceTrack":
        return stopped_manifest(dataset)
    raise ValueError(f"unknown dataset contract: {dataset}")
