# STV composition by synthesized gap length — analysis specification

STATUS: POST-HOC / DESCRIPTIVE

This specification is frozen and hashed before the derivation is written or run.
It carries no confirmatory weight: the gap-length stratification was not
specified before the primary STV result existed.

## Population
The already frozen MOT17-DTI audit population only: MOT17 validation half,
FRCNN detector copy, seven sequences, 2,652 frames. No other population.

## Pipelines
ByteTrack, BoT-SORT, OC-SORT. StrongSORT++ is excluded: its transformation is
not row-additive, so a synthesized-row set is not defined for it.

## Synthesized-row identity
R2 \ R0 under the existing frozen row-identity definition (frame, track_id),
read from the immutable frozen state files. R0 must be a subset of R2.

## Gap length
g_synth = right_anchor_frame - left_anchor_frame - 1, where left/right are the
nearest observed R0 frames of the same track bracketing the synthesized row.
This is the number of interior frames the post-processor inserted for that gap.

## Expected support
The executed rule is `1 < right - left < n_dti` with n_dti = 20 for all three
pipelines, so g_synth in {1, ..., 18}. Any value outside this range is an error
and aborts the derivation.

## Reported per pipeline and per exact g_synth
synthesized row count; STV admitted count; unmatched-anchor count;
ID-mismatch count; reference-absent count; STV non-admission fraction.

## Method
The frozen classifier `scripts/mot_audit/stv_states.py` is loaded unmodified at
its frozen IoU gate of 0.5. Only a grouping by g_synth is added. Nothing is
recomputed that the frozen record already fixes.

## Prohibited
No bins. No threshold selection. No inference. No significance test. No causal
statement. No change to R1. No rerun of any tracker or post-processor. No use of
reconstruction error, ranking, method preference or bootstrap output.

## Permitted reading
Descriptive only: whether the STV composition varies with synthesized gap length.

## Acceptance gate
Summed over g_synth, each pipeline must reproduce the frozen synthesized totals
(ByteTrack 2,072; BoT-SORT 2,090; OC-SORT 2,622) and each STV class sum must
reproduce the frozen aggregate class counts exactly. Any difference aborts the
analysis and the result is not used.
