# Reproducibility

There are three levels here, and they cost very different amounts. Level 1 is
what most readers want.

## Level 1 — verify the released audit, offline (seconds, no data)

```bash
python scripts/verify_release.py
python -m pytest tests/ -q
```

This re-derives every ordering relation and transition from the released
full-precision metric values, re-runs the admission classifier on fixtures with
known answers, re-checks that the four admission classes partition every
synthesized set, recomputes every published fraction and materiality verdict from
the released integers, re-checks the MOT20 eligibility ledger against its own
counts, and confirms the frozen configuration files still agree with the source
constants they were transcribed from.

**What it does not do:** it does not re-run a tracker, an evaluator, or the
matcher over real ground truth. It verifies that the released logic produces the
released numbers, and that the released numbers are internally consistent. That
is a real check — it catches transcription error, arithmetic drift and silently
edited constants — but it is not an independent re-measurement.

### Requirements

Python **3.9 or newer** (the audit core uses PEP 584 dict union), plus `PyYAML`
and `pytest`. `numpy`, `scipy` and `pandas` are needed only for the
object-trajectory modules and their tests.

Two environments are documented, and they are different things.

| | Python | role |
|---|---|---|
| **Frozen reproduction environment** | 3.9.23 | the interpreter the reported numbers were produced under; pinned in `environment.yml` |
| **Verified modern environments** | 3.10.21, 3.11.15, 3.12.14 | the offline verification and the full test suite were run on each and pass identically |

Measured, not assumed:

| Python | tests | verification scripts | minimal example |
|---|---|---|---|
| 3.8.10 | **2 failed**, 187 passed | 6/6 exit 0 | ok |
| 3.9.23 | **189 passed** | 6/6 exit 0 | ok |
| 3.10.21 | **189 passed** | 6/6 exit 0 | ok |
| 3.11.15 | **189 passed** | 6/6 exit 0 | ok |
| 3.12.14 | **189 passed** | 6/6 exit 0 | ok |

Python 3.8 is genuinely not enough. The two failures are
`test_a_missing_state_yields_an_unavailable_delta` — `metrics.delta` uses
`dict | dict`, added in 3.9 — and the version guard that asserts exactly this.
Neither was worked around: changing frozen scientific code to widen
compatibility is not a trade this release makes.

The modern runs used current dependency versions (NumPy 2.x, SciPy 1.17, pandas
3.x on 3.11), so the pass is a real compatibility result, not an artefact of
pinning everything back to 2026.

## Level 2 — re-derive the audit from tracker outputs (hours, needs corpora)

You need MOT17, the upstream tracker repositories at their pinned commits, and
TrackEval at commit `12c8791b303e0a0b50f753af204249e622d0281a`. See
[DATASETS.md](DATASETS.md).

Run each tracker's own documented command to produce its raw output `R0` and its
post-processed submission `R2`. Nothing in this repository patches, imports or
wraps upstream tracker code; the audit consumes the files they write.

Then, per deployment and sequence, feed `R0`, `R2` and the ground truth through
the audit:

```python
from tracking_provenance_audit.rowid import parse_mot, parse_gt
from tracking_provenance_audit import stv, states

r0 = parse_mot(open("R0.txt").read(), "MOT17-02-FRCNN")
r2 = parse_mot(open("R2.txt").read(), "MOT17-02-FRCNN")
gt = parse_gt(open("gt.txt").read(), "MOT17-02-FRCNN")

classes = stv.classify(sorted(set(r2) - set(r0)), list(r0.values()), gt,
                       gate=stv.PRIMARY_IOU_GATE)
counts = stv.partition_counts(classes)
r1 = states.build_R1(r0, r2, classes)
```

`examples/minimal_example/run.py` is exactly this, on eight rows you can read.

Score `R0`, `R1` and `R2` with the pinned TrackEval and the configuration in
`configs/frozen/evaluator.yaml`. The ordering matrix then follows from
`ordering.matrix(...)` and `ordering.summary(...)`.

Four of the eight pipelines in the census admit no row-additive decomposition.
For those, `R1` does not exist and none is manufactured —
`states.r1_status_for_non_row_additive` returns `STRUCTURALLY_UNDEFINED` and the
reason. StrongSORT++ is reported as `S0`/`S2` only, and OC-SORT-GPR is excluded
from the ordering matrix for the same reason.

## Level 3 — re-run the executed MOT20 cell (needs corpus, checkpoints, GPU)

This is the one prospective tracker execution in the study. It is deliberately
hard to start by accident.

`src/tracking_provenance_audit/guard.py` refuses prospective execution unless a
schema-valid authorization marker file exists, and binds authorization to
`(dataset, pipeline, run_id)` simultaneously. A MOT17 marker cannot license a
MOT20 run: the two datasets map to disjoint marker files, and a run identifier
must carry its dataset prefix. There is no environment-variable bypass; that was
removed deliberately, because an environment variable is not a reviewable
committed artifact.

`src/tracking_provenance_audit/run_guard.py` adds the run-scoping. Before a run
starts it enumerates every canonical output path for that identifier and refuses
if any exists — it never deletes, never overwrites and never auto-increments to a
`-002` identifier. It verifies that the reachable checkpoint set is exactly the
two clean assets in [DATASETS.md](DATASETS.md) and that no MOT20-trained
checkpoint is reachable. It verifies the frozen frame count (4,463, not a
re-halved count) before every run. Generated caches must be run-scoped and empty;
the authors' precomputed camera-motion files are linked read-only as a scientific
input, not regenerated.

The eight location constants in `src/tracking_provenance_audit/run_guard.py` were absolute paths on the
authors' host. They now read from the environment with workspace-relative
defaults:

```
TPA_WORKSPACE            root for all defaults below (default: ./workspace)
TPA_DEEP_REPO            upstream Deep-OC-SORT checkout, unmodified
TPA_SANDBOX_ROOT         writable per-run sandbox root
TPA_TRACKER_INPUT        frozen MOT20 validation-half tracker input
TPA_DEPRECATED_ADAPTER   superseded adapter directory; refused if reachable
TPA_ASSET_STORE          checkpoint store holding exactly the two clean assets
TPA_TRACKEVAL_TRACKERS   TrackEval tracker-output root
TPA_STV_OUTPUT_ROOT      where this audit writes its MOT20 states
```

No check, hash, refusal rule or ordering changed with that edit, and every
SHA-256 in the file is the frozen one.

## The environment the reported numbers came from

Python 3.9.23, torch 1.13.1+cu117, torchvision 0.14.1+cu117, NumPy 1.23.5,
SciPy 1.10.1, scikit-learn 1.0.2, OpenCV 4.11.0, on an NVIDIA A100-SXM4-80GB
MIG 7g.80gb under CUDA 11.7. Evaluation used TrackEval at commit `12c8791b`,
unmodified, at admission gate `tau = 0.5`.

`environment.yml` reproduces the parts that matter for the offline verification.
The GPU stack is only needed for level 3.

## What is frozen, and what that means

`provenance/frozen_records/` holds the protocol, the census, the eligibility
ledger, the results and their independent verifications, released verbatim. The
protocol (record 02) was frozen before any prospective execution; the eligibility
audit (records 10 and 10A) before any MOT20 outcome existed. The constants in
`configs/frozen/` are transcribed from record 02 and are read, never tuned —
`scripts/verify_release.py` fails if they drift from the source constants.

`provenance/RELEASE_MANIFEST.json` maps every published file to the frozen
artifact it came from, that artifact's SHA-256, and the transformation applied.
`provenance/MANIFEST.sha256` covers the published tree.

## Known limits of this repository

- The offline verification checks internal consistency, not independent
  re-measurement. Level 2 is the independent path.
- The MOT20 corpus provenance is a mirror, not a byte-verified official archive.
- Five of the eight census pipelines have no released results here; the census
  records why each cell was or was not executed.
- Historical MOT17 metrics come from the study's earlier evaluation record rather
  than a fresh evaluator invocation. The pin, configuration and ground-truth
  hashes are identical, and `results/mot17/ordering_summary.json` carries that
  caveat rather than dropping it.
