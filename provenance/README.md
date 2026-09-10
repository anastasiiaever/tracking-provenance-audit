# Provenance

Three things live here.

| | |
|---|---|
| `RELEASE_MANIFEST.json` | every published file, the frozen artifact it came from, that artifact's SHA-256, the transformation applied, and its redistribution class |
| `MANIFEST.sha256` | digests of the whole published tree — `sha256sum -c provenance/MANIFEST.sha256` |
| `frozen_records/` | the study's own protocol, census, eligibility and result records, released **byte-identical** |

`frozen_records/README.md` lists what is in that set and why it is a curated
subset. This file explains the one thing a reader trips over first.

## Why paths inside the frozen records do not resolve

The records were written during the study, against the authors' private research
tree. They were **not rewritten** for this release, and they will not be: a
record whose bytes changed after freezing is no longer the record that was
frozen, and the point of publishing them verbatim is that their digests still
check against `RELEASE_MANIFEST.json`.

So a record naming `stv.py`, `tools/interpolation.py` or `eval_ALL.json` is
naming a file in the research tree or in an upstream repository — not a file in
this repository. There are 70 such references across 13 records. Every one falls
into exactly one of three cases, and `path_map.json` resolves them all in
machine-readable form.

*(Filenames quoted below are the records' own strings. They are meant not to
resolve against this repository — resolving them is what this page is for.)*

### 1 — Has a public equivalent here (24 references)

The file is published, at a different path. The audit source modules moved from
`scripts/tracking_provenance_audit/` to `src/tracking_provenance_audit/`, and the
records moved into `provenance/frozen_records/`.

| record says | this repository |
|---|---|
| `stv.py`, `ordering.py`, `guard.py`, `materiality.py`, `metrics.py`, `rowid.py`, `states.py`, `transitions.py`, `report.py`, `adapters.py`, `cli.py`, `gpr_wrapper.py` | `src/tracking_provenance_audit/…` |
| `01_SOURCE_MANIFEST.json`, `02_CLI_CONTRACT.md`, `02_PROTOCOL_MANIFEST.json`, `02A_…md`, `02_LITERATURE_AUDIT_SPEC.md`, `03_EXECUTABLE_IMPLEMENTATION.md`, `07_ORDERING_MATRIX.json`, `08_ORDERING_RECOMPUTATION.json`, `09A_MOT20_POPULATION_MANIFEST_SPEC.json`, `11_INVARIANT_MATRIX.json` | `provenance/frozen_records/…` |
| `ADAPTER_SPEC.md`, `PROTOCOL.md` | `provenance/frozen_records/MOT_AUDIT_ADAPTER_SPEC.md`, `…_PROTOCOL.md` |

### 2 — Belongs to an upstream project or a dataset (33 references)

`tools/interpolation.py`, `GSI.py`, `AFLink/AppFreeLink.py`,
`trackeval/datasets/mot_challenge_2d_box.py`, the `yolox_*.py` experiment
configs, `annotations/train.json`, `*.pth.tar` and the rest name files inside a
tracker repository, the evaluator, or a dataset archive. **None of them is in
this repository, and none can be.** Obtain each from its own source:

- trackers and their pinned commits — `metadata/upstream_pipelines.csv`
- checkpoints, with SHA-256 and byte size — `metadata/external_assets.csv`
- corpora — `docs/DATASETS.md`

Reading a record against upstream code is exactly what the record is for: it
cites the line that decides a classification, so you can check the classification
against the upstream source yourself.

### 3 — Deliberately not released (13 references)

| | |
|---|---|
| `eval_ALL.json`, `eval_ByteTrack.json`, `eval_OCSORT.json` | raw evaluator outputs |
| `BoTSORT_states.json`, `ByteTrack_states.json`, `OCSORT_states.json`, `RESULTS.json`, `STRONGSORT_*.json` | per-sequence raw state files and their hash tables |
| `data/posetrack21/audit/val_eval_primary.json` | per-case PoseTrack21 outputs derived from licensed annotations |
| `scripts/mot_audit/stv_states.py`, `scripts/run_mot_challenge.py` | site-bound execution scripts that hard-code the authors' host paths |

These are bulky, site-specific, or derived from corpora this repository may not
redistribute. **Their scientific content is not lost:** the counts, metrics,
compositions and orderings computed from them are the tables in `results/`, and
`RELEASE_MANIFEST.json` names the frozen artifact behind each one.

Also not released, and for the same reason, are the command, asset and
environment manifests (records 04, 06B, 09B, 10, 10A, 12B): they are lists of
absolute paths on the execution host. What they *fix* — the evaluator pin, the
checkpoint hashes and sizes, the frozen frame counts — is published in
`configs/frozen/`, `metadata/external_assets.csv` and `docs/REPRODUCIBILITY.md`.

## Checking a record yourself

```bash
sha256sum -c provenance/MANIFEST.sha256                 # the published tree
python -c "import json;m=json.load(open('provenance/RELEASE_MANIFEST.json'));\
print([f for f in m['files'] if f['public_file'].startswith('provenance/frozen_records/')][0])"
```

Every entry whose `transformation` reads `none (byte-identical copy)` carries the
source artifact's own SHA-256 in `source_sha256`, so a record can be checked
against the study's frozen copy without trusting this repository's packaging.
