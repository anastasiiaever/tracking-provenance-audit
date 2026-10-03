# Complete five-pipeline IoU-gate sensitivity

STATUS: **POST-HOC / DESCRIPTIVE.** This is a retrospective sensitivity analysis.
It carries no confirmatory weight and the primary gate remains 0.5.

## What was done

No tracker was re-run and no model was trained. The analysis reads the same frozen
MOT17 validation-half FRCNN population, the same seven sequences, the same frozen
`R0` and `R2` state rows and the same scoreable ground truth that the primary
audit used, and re-applies the admission matcher at each gate.

The gates 0.3, 0.4, 0.5, 0.6 and 0.7 are not new: they are the `sensitivity_gates`
already fixed in `configs/frozen/admission_stv.yaml`.

The matcher is the frozen TrackEval zero-before-assignment form described in
`docs/ESTIMAND_ELIGIBILITY.md`: similarities below the gate are zeroed before the
one-to-one assignment, and selected zero-similarity pairs are dropped from the
result. The assignment is recomputed independently at every gate, on `R0` only;
synthesized rows never influence it.

## Relationship to the existing table

`summary.csv` is the original three-pipeline sweep and is **preserved unchanged**.
This file extends the same analysis to every MOT17 pipeline for which row-additive
`R0`/`R2` states exist. Its ByteTrack, BoT-SORT and OC-SORT rows reproduce
`summary.csv` exactly; Deep-OC-SORT and Hybrid-SORT are the new coverage.

## Coverage, and why it stops at five

| pipeline | included | reason |
|---|---|---|
| ByteTrack, BoT-SORT, OC-SORT | yes | row-additive, frozen MOT17 states exist |
| Deep-OC-SORT, Hybrid-SORT | yes | row-additive, frozen MOT17 states exist |
| SparseTrack | no | never executed on MOT17; no frozen state exists |
| OC-SORT-GPR | no | non-row-additive; no defined `R0`/`R2` synthesized-row set |
| StrongSORT++ | no | non-row-additive; no defined `R0`/`R2` synthesized-row set |

## Reading the sweep

The synthesized set is a property of the post-processor, not of the matcher, so
`n_synthesized` is invariant across gates within a pipeline. The four classes
partition it exactly in all 25 cells, and `TARGET_REFERENCE_ABSENT` is zero
throughout.

Raising the gate shrinks the set of above-gate entries monotonically. It does
**not** make the selected assignment pairs nested; pairs may be reassigned as the
gate moves.
