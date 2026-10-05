# Upstream code, datasets, and the layout the scripts expect

Nothing upstream is redistributed here. This file records what the audit used, so
the results can be regenerated from the original sources.

## Trackers and operators

Each deployment was run unmodified from its own repository at a pinned commit,
with its own documented post-processing rule. The per-deployment operator family,
parameters, documentation location and commit pin are in
`source_of_truth/` and in the released census, together with the SHA-256 of the
interpolation module blob the audit actually executed.

| deployment | operator audited | parameters |
|---|---|---|
| ByteTrack | linear DTI | `n_min = 5`, `n_dti = 20` |
| BoT-SORT | linear DTI | `n_min = 5`, `n_dti = 20` |
| OC-SORT | linear DTI; Gaussian-process refinement | `n_min = 30`, `n_dti = 20` |
| Deep-OC-SORT | linear DTI | `n_min = 30`, `n_dti = 20` |
| Hybrid-SORT | linear DTI | `n_min = 30`, `n_dti = 20` |
| StrongSORT++ | AFLink linking, then Gaussian-smoothed interpolation | upstream call-site values |

For the controlled arm the operator is ours: linear DTI extracted verbatim at a
pinned upstream commit and verified byte-identical across the three audited
repositories that ship it, at `n_min = 25` primary and `n_min = 30` sensitivity,
`n_dti = 20`; and Gaussian-smoothed interpolation at `interval = 20`, `tau = 10`,
with the appearance-free linking stage not applied.

## Evaluator

TrackEval, unmodified, at a single pinned commit for every state of every
deployment, with one configuration. No metric was substituted after any result
was seen.

## Datasets

Obtain from the original providers; none is redistributed.

| dataset | split used | obtain from |
|---|---|---|
| MOT17 | validation half of the seven FRCNN sequences | motchallenge.net |
| MOT20 | second half of MOT20-01, -02, -03, -05 | motchallenge.net |
| DanceTrack | validation set, 25 sequences | the DanceTrack release |

The MOT17 validation half is indexed from 1 in the audit, in the state files and
in the TrackEval validation-half ground truth, so those three agree without an
offset. Only image file names need the original numbering; for MOT17-02-FRCNN
that offset is 301, and the figure generator rederives it rather than assuming
it. DanceTrack ground truth and images share one numbering, so its offset is 0.

## Expected layout

The generators resolve the placeholders described in `PATHS.md`:

```
<MOT_AUDIT_ROOT>/states/<Tracker>/R0|R2/<sequence>.txt
<MOT_AUDIT_ROOT>/repos/TrackEval/data/gt/mot_challenge/MOT17-val_half/<sequence>/gt/gt.txt
<MOT_AUDIT_ROOT>/datasets/mot/train/<sequence>/img1/%06d.jpg
<DATASETS_ROOT>/dancetrack/val/<sequence>/img1/%08d.jpg
<AUDIT_ROOT>/...                      the frozen audit records
```

## What is publishable here

The released summaries, the frozen records, the implementation and the
verification scripts are this project's own work and are published. Dataset
frames, ground-truth annotation files, tracker weights and upstream tracker
source are not. Where a frozen record is a derived table over a dataset, the
table is published and the dataset is not.
