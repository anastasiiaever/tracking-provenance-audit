# Provenance

Where the released artifacts come from, and the four facts a reader needs in
order to read them correctly. Each is stated once here; other documents point
back rather than restate.

## Source state

Every public file names its origin in `provenance/RELEASE_MANIFEST.json`: the
frozen artifact it was derived from, that artifact's SHA-256, and the
transformation applied. `provenance/MANIFEST.sha256` covers the published tree.

The release draws on two frozen states of the research repository, which is not
published:

| arm | tag | commit |
|---|---|---|
| primary | `tpami-v9-mot20-deep-results-verified-20260831` | `78a439acc1796fb389776347fd0bae73422023d6` |
| KITTI | `q1-kitti-generality-result-20260824` | `ff8569a44d0263fde0aa55e0429b27f1f80e84e8` |

The KITTI transfer was frozen on its own chain before the tracking arm existed,
so its three records are taken from that tag rather than the primary one.

The reported experimental results were produced by the frozen research execution
pipeline described in the paper. The public implementation in this repository
provides an independently checkable implementation of the audit logic and
reproduces the recorded audit decisions.

## MOT17 population naming

Public documentation uses one name: the **MOT17 validation half**.

`MOT17-val` and `MOT17-val_half` are two TrackEval folder names for the same
population. The ground-truth files are byte-identical and both correspond to the
second half of the seven MOT17 FRCNN training sequences, 299 frames per sequence.
The two names exist because the historical and the later deployments were
evaluated under separate TrackEval folders at the same pin, over the same ground
truth. Artifact directories keep their recorded names.

## MOT20 corpus

The MOT20 copy used in this study reached the authors through a verified mirror
and carries the status `MIRROR_TRANSPORT_FALLBACK`. Byte identity to an official
MOTChallenge archive is not established. The reported MOT20 results are
reproducible against the recorded per-sequence ground-truth hashes, but those
hashes have not been checked against the official archive.

## Eligibility vocabulary

`results/mot20/eligibility_context.json` reports **readiness** categories:
`BLOCKED_ASSET`, `BLOCKED_CHECKPOINT_PROVENANCE`, `BLOCKED_COMMAND`,
`BLOCKED_ENVIRONMENT`, `BLOCKED_INDEXING`, `BLOCKED_OTHER`, `READY`. They record
why a cell could not be executed and sum to the seven cells.

These are not the paper's estimand verdicts. The paper reports one eligible cell,
five ineligible through training overlap and one unresolved. That 1 / 5 / 1 result
is derived per cell from `checkpoint_status` in `results/mot20/eligibility.csv`:

| `checkpoint_status` | verdict |
|---|---|
| `NO_KNOWN_EVAL_LEAKAGE` | `ELIGIBLE` |
| `CONFIRMED_EVAL_LEAKAGE`, `INHERITED_CONFIRMED_EVAL_LEAKAGE` | `INELIGIBLE_TRAINING_OVERLAP` |
| `MIXED: ...` | `UNRESOLVED` |

`scripts/verify_mot20_eligibility.py` performs this derivation and compares the
result cell by cell with `provenance/frozen_records/10_MOT20_EXECUTION_READINESS.json`.
`UNRESOLVED` means the evidence does not settle the question; it is not a finding
of ineligibility.

## History normalization

The research history was rewritten once to normalize commit metadata. The rewrite
changed commit identifiers and messages only; the file trees are byte-identical
before and after, verified by tree-hash equality across all mapped commits.
