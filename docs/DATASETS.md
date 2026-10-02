# Datasets and external assets

**This repository redistributes no dataset, no annotation file and no
checkpoint.** Every corpus below is obtained by you, from its own distributor,
under its own terms. Nothing here grants or extends a licence to any of them.

The released tables in `results/` are aggregate counts and metric values derived
from these corpora. They contain no image, no video, no annotation row and no
personally identifying material.

## What you need, and for what

| If you want to | You need |
|---|---|
| Run `scripts/verify_release.py`, the tests, or the minimal example | nothing |
| Re-derive the MOT17 audit from tracker outputs | MOT17, the upstream trackers, TrackEval |
| Re-run the executed MOT20 cell end to end | MOT20, Deep-OC-SORT, two checkpoints, TrackEval |
| Re-run the object-trajectory applicability audit | MOT17 and the BDD100K MOT label table |

Everything in the repository's own quick start is in the first row.

## Corpora

`metadata/datasets.csv` carries the same table in machine-readable form.

### MOT17
<https://motchallenge.net/data/MOT17/> — registration required.

The audit population is the labelled `train` split, FRCNN detector copy only,
second half of each of the seven base sequences. MOT17 ships DPM, FRCNN and SDP
copies of every base sequence with byte-identical ground truth; exactly one copy
is used so the seven sequences are counted once. Per-sequence lengths, rebase
offsets and ground-truth SHA-256 values are in
`configs/frozen/populations.yaml`.

### MOT20
<https://motchallenge.net/data/MOT20/> — registration required.

Four sequences (MOT20-01, -02, -03, -05), second half, 4,463 frames.

The MOT20 corpus status is `MIRROR_TRANSPORT_FALLBACK`; see
[PROVENANCE.md](PROVENANCE.md#mot20-corpus). If you obtain MOT20 from the official
source your copy may differ in bytes; check the frame count and sequence set
against `provenance/frozen_records/09A_MOT20_POPULATION_MANIFEST_SPEC.json`.

### BDD100K (MOT labels)
<https://bdd-data.berkeley.edu/> — registration required.

The object-trajectory audit read a derived parquet label table rather than the
raw release, verified against the pinned SHA-256
`e296934ebba47f360fb49a61060d5dfc6027f91a8655b96b565ece7ac1599e02`. That audit is
a supplement-only analysis; its implementation is not part of this release and its
released partition is `results/controlled/objecttraj_applicability.csv`.

### KITTI tracking
<https://www.cvlibs.net/datasets/kitti/> — registration required.

The 21 officially labelled tracking sequences (`0000`–`0020`), evaluated classes
`Car` and `Pedestrian`. The applicability partition derived from it is released
in `results/controlled/kitti_applicability.csv`; the corpus is not.

### PoseTrack21
<https://github.com/anDoer/PoseTrack21> — **access-gated**: a signed agreement is
emailed to the maintainers, who issue an access token that doubles as the
annotation archive's password.

The evaluation population is the 170-sequence validation split. Only annotations
were used — no imagery entered case construction, scoring or any reported number.
The released summaries (`results/controlled/posetrack21_*.csv`) are aggregate
counts, percentages and bootstrap intervals; **no annotation row is
redistributed here**, and the dataset's terms remain between you and its
maintainers.

The study read the access token from an environment variable or a no-echo
prompt, never from `argv`, and extracted the archive in-process, so the token did
not reach `ps` output or shell history.

### NTU RGB+D 60
<https://rose1.ntu.edu.sg/dataset/actionRecognition/> — request-based access.

The controlled population is the `xsub_val` split. The study read the
two-dimensional HRNet keypoints distributed with
[PYSKL](https://github.com/kennymckormick/pyskl), in image pixels of the corpus's
uniform 1920×1080 frame, so NTU values are in pixels and are **not** on the
body-scale-normalised PoseTrack21 scale. The released summary
(`results/controlled/ntu_support_accounting.json`) carries the reclassification
counts, the affected-row summary and the two paired estimates with their
intervals; neither the corpus nor the derived keypoints ship here.

### JTA
<https://github.com/fabbrimatteo/JTA-Dataset> — synthetic corpus, own terms.

Used for the within-corpus structural replication. The applicability partition
and the frozen headline reading are released in
`results/controlled/jta_applicability.csv` and `results/controlled/jta_headline.json`; the corpus is
not, and neither are the learned checkpoints whose JTA scores the headline
reports.

## Checkpoints

None are redistributed. `metadata/external_assets.csv` lists each one with its
role and, where the frozen record pins it, its SHA-256 — so you can confirm you
obtained the same file rather than a same-named one.

The two assets the executed MOT20 cell is allowed to reach:

| asset | SHA-256 |
|---|---|
| `bytetrack_x_mot17.pth.tar` | `e3945f3523fde1e107708aacd64dab0670c34e371d136e54587cac7a50d3cfba` |
| `osnet_ain_ms_d_c.pth.tar` | `2f38acc25e28cb29407635db2be315edc08d5457a904b72a9a11e427f41f3242` |

`src/tracking_provenance_audit/run_guard.py` refuses to start a run if any other
checkpoint is reachable from the sandbox — in particular any MOT20-trained
detector, which would violate the eligibility criterion the MOT20 arm rests on.

## Evaluator

TrackEval, pinned at commit `12c8791b303e0a0b50f753af204249e622d0281a`, obtained
from <https://github.com/JonathonLuiten/TrackEval>. It is used unmodified. The
pin is enforced in code: `metrics.freeze_inputs` raises `EvaluatorPinMismatch`
rather than falling back to another evaluator or another commit.

## Upstream trackers

`metadata/upstream_pipelines.csv` lists all eight pipelines with the exact commit
the census pinned. None of their source is included here. Clone each from its own
repository at the pinned commit; the audit reads their outputs and never patches
or imports them.
