# Post-Processing Provenance and the Evaluated State of Tracking Submissions

Code and released audit artifacts for the paper
***Post-Processing Provenance and the Evaluated State of Tracking Submissions*.**

This repository contains the audit implementation, the frozen provenance records,
the result tables behind the paper's claims, and the scripts that check them. It
contains **no tracker training code, no datasets and no model checkpoints**.

## 1. What is audited

Several released multi-object trackers apply an offline post-processing stage
before submission, so the file a benchmark scores is not the tracker's output.
The audit measures what that file contains and what the transition that produced
it permits anyone to measure.

| arm | what it covers |
|---|---|
| released MOT17 | five released deployments, their added rows, the four-class admission decomposition, metric change and every pairwise margin |
| released MOT20 | the estimand-eligibility census over seven configurations and the one eligible cell |
| controlled DanceTrack, linear DTI | one operator of ours held fixed across four trackers that share a detector |
| controlled DanceTrack, GSI | a second operator that also rewrites surviving rows, decomposed into its linear and Gaussian-process stages |
| released OC-SORT GPR | the rewrite-only boundary case |
| released StrongSORT++ | the linking-and-smoothing structural audit |

## 2. Repository structure

```
tpami/                     everything this paper rests on
  results/                 per-arm released summaries
    dancetrack_dti/        controlled linear-DTI arm
    dancetrack_gsi/        controlled GSI arm and its stage decomposition
    gpr_rewrite_only/      the rewrite-only recount at several tolerances
    margins/               the unified pairwise-margin matrix, all arms
    gt_gap/                ground-truth interior-gap population summary
  source_of_truth/         the frozen artifact set and its manifest
  figures/                 figure generators and per-figure provenance
  ARTIFACT_MAP.md          manuscript claim/table/figure -> file
  UPSTREAM.md              upstream code, datasets, expected layout
  PATHS.md                 what the path placeholders mean
src/tracking_provenance_audit/   the audit implementation
scripts/                   the verification stages
results/, provenance/      the MOT17 and MOT20 released records
other-work/                a SEPARATE paper; see other-work/README.md
```

## 3. Environment

Python 3.9 or newer. The audit core uses PEP 584 dict-union and will not run on
3.8.

```bash
conda env create -f environment.yml
conda activate tracking-provenance-audit
```

## 4. Reproduction order

```bash
python scripts/verify_release.py          # all offline verification stages
sha256sum -c provenance/MANIFEST.sha256   # released-file integrity
cd tpami/source_of_truth && sha256sum -c RELEASE_MANIFEST_SANITISED.sha256
python -m pytest -q tests/                # the tracking-paper test suite
```

Each stage is offline and re-measures nothing: it checks that every released
summary is internally exact and agrees cell for cell with the frozen record it
came from.

## 5. Tables and figures

The generators under `tpami/figures/scripts/` rebuild the manuscript figures and
write a provenance record beside each one. They assert every case they draw
against the frozen records and abort rather than draw an unverified example.

```bash
python tpami/figures/scripts/gen_fig1_fourclass.py      # Fig. 1, four admission classes
python tpami/figures/scripts/gen_fig2.py                # Fig. 2, states and permitted diagnostics
python tpami/figures/scripts/gen_fig3.py                # Fig. 3, composition across all columns
python tpami/figures/scripts/gen_fig4_margins.py        # Fig. 4, margin movement
python tpami/figures/scripts/gen_figS1.py               # Fig. S1
python tpami/figures/scripts/gen_figS2_trajectories.py  # Fig. S2
python tpami/results/gt_gap/make_gt_gap_population_summary.py
```

They need the frozen state files and the dataset frames, which are not
redistributed here; see `tpami/UPSTREAM.md` and `tpami/PATHS.md`.

## 6. Expected checks

| check | expected |
|---|---|
| `scripts/verify_release.py` | all stages PASS |
| `provenance/MANIFEST.sha256` | 266 of 266 OK |
| `tpami/source_of_truth/RELEASE_MANIFEST_SANITISED.sha256` | 52 of 52 OK |
| `pytest tests/` | 107 passed |
| `pytest tests/ other-work/tests/` | 214 passed |

Last run on Python 3.10.21: **107 passed** for the tracking suite, **214 passed**
including the separate paper's suite.

## 7. Upstream code and data

Not redistributed. `tpami/UPSTREAM.md` gives, for each tracker and operator, the
upstream repository and the pinned commit the audit used, the datasets and how to
obtain them, the directory layout the scripts expect, and content hashes for the
artifacts that are legally publishable.

## 8. Release

The commit tagged **`v1.1.1-tpami-submission`** is the state this paper's claims
were checked against. It supersedes `v1.1.0-tpami-submission`, which remains in
place; neither tag is rewritten.

## 9. Other work in this repository

`other-work/` holds the records and code of a **different, separate paper** on
common-support and skeleton reconstruction. It is kept for history and is **not
part of this paper**. Nothing in `tpami/`, `src/tracking_provenance_audit/`,
`results/` or `provenance/` depends on it.

## 10. Limitations on what can be released

No dataset frames, no ground-truth annotation files, no tracker weights and no
upstream tracker source are redistributed here. What is released is this project's
own audit outputs, the frozen records they were derived from, the implementation,
and the verification scripts. Absolute host paths are replaced by placeholders;
see `tpami/PATHS.md`.
