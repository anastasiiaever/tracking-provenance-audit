# V9 Independent Result Verification

Every derived quantity was recomputed from immutable run outputs and evaluator records **without**
using the 07 summaries as an oracle. No tracker, interpolation or GPR was rerun.

**Verdict: 30/30 checks PASS, 0 FAIL, 0 UNRESOLVED.**

## Finding: narrative transcription error in the prior chat report

**NARRATIVE-TRANSCRIPTION-ERROR** — severity: reporting only; no artifact affected.

The prior turn's chat-report metric tables for Hybrid-SORT (R0/R1/R2 and R2-R0) and for OC-SORT-GPR (S0/S2 and S2-S0) did not match the evaluator outputs; those rows were stated without being read. The COMMITTED artifacts contain the correct evaluator values, and the ordering matrix was computed from the correct values and verified field-wise identical at full precision. Correct: Hybrid-SORT R0 66.948/65.991/68.473/77.745/75.992, R1 68.194/67.784/69.183/78.815/78.616, R2 67.811/67.312/68.920/78.193/77.588, R2-R0 +0.863/+1.321/+0.447/+0.448/+1.596; OC-SORT-GPR S0 = S2 = 67.990/66.644/69.840/79.418/77.810, all deltas +0.000.

The committed artifacts were correct; only the prose was wrong. This is recorded rather than quietly fixed.

## Checks

| Area | Check | Verdict |
|---|---|---|
| input_identity | MOT17 7 sequences / 2652 frames | **PASS** |
| input_identity | GT hashes match frozen population in dataset and both evaluator benchmark folders | **PASS** |
| evaluator_comparability | TrackEval pin 12c8791b for historical and prospective | **PASS** |
| row_accounting | Deep-OC-SORT: n_R2-n_R0 == n_synthesized | **PASS** |
| stv_partition | Deep-OC-SORT: STV four classes sum to n_synthesized | **PASS** |
| R1 | Deep-OC-SORT: R1 identity set and row count == R0 + ADMITTED | **PASS** |
| row_additive | Deep-OC-SORT: 0 deletions / 0 coordinate rewrites / 0 ID rewrites | **PASS** |
| agreement_with_07 | Deep-OC-SORT: counts and STV match the 07 record | **PASS** |
| materiality | Deep-OC-SORT: criterion nonadm/synth >= 0.10 reproduced | **PASS** |
| row_accounting | Hybrid-SORT: n_R2-n_R0 == n_synthesized | **PASS** |
| stv_partition | Hybrid-SORT: STV four classes sum to n_synthesized | **PASS** |
| R1 | Hybrid-SORT: R1 identity set and row count == R0 + ADMITTED | **PASS** |
| row_additive | Hybrid-SORT: 0 deletions / 0 coordinate rewrites / 0 ID rewrites | **PASS** |
| agreement_with_07 | Hybrid-SORT: counts and STV match the 07 record | **PASS** |
| materiality | Hybrid-SORT: criterion nonadm/synth >= 0.10 reproduced | **PASS** |
| gpr | canonical and replay each have 7 files, same set | **PASS** |
| gpr | replay byte-identical to canonical (GPR_REPLAY_STATUS PASS) | **PASS** |
| gpr | S0 rows == S2 rows, 0 insertions, 0 deletions | **PASS** |
| gpr | R1 remains STRUCTURALLY_UNDEFINED | **PASS** |
| gpr | seed 20260830 recorded in canonical stdout | **PASS** |
| gpr | failed GPR-001 partial artifact absent from all scientific inputs | **PASS** |
| metric_extraction | full-precision reconstruction agrees with 3-dp summaries for all 5 deployments | **PASS** |
| ordering | independent recomputation field-wise identical to 07_ORDERING_MATRIX.json | **PASS** |
| ordering | 10 eligible pairs and 50 pair x metric cells | **PASS** |
| ordering | no transition changed by 3-decimal rounding | **PASS** |
| ordering | no near-tie | **PASS** |
| chronology | ByteTrack / BoT-SORT / OC-SORT = HISTORICAL_OUTCOME_KNOWN_PRE_V9 | **PASS** |
| chronology | Deep-OC-SORT / Hybrid-SORT = PROSPECTIVE_OUTCOME_UNSEEN_AT_V9_FREEZE | **PASS** |
| chronology | GPR prospective quantities first known from GPR-002 | **PASS** |
| chronology | procedural deviation and failed attempts preserved | **PASS** |

## Recomputed row accounting, STV and materiality

| Quantity | Deep-OC-SORT | Hybrid-SORT |
|---|---|---|
| n_R0 | 43581 | 49160 |
| n_R1 | 45685 | 50701 |
| n_R2 | 46541 | 52183 |
| n_synthesized | 2960 | 3023 |
| STV ANCHOR_UNMATCHED | 570 | 1266 |
| STV ANCHOR_ID_MISMATCH | 286 | 216 |
| STV TARGET_REFERENCE_ABSENT | 0 | 0 |
| STV SEMANTICALLY_ADMITTED | 2104 | 1541 |
| synthesized / R2 | 0.063600 | 0.057931 |
| nonadmission / synthesized | 0.289189 | 0.490241 |
| nonadmission / R2 | 0.018392 | 0.028400 |
| ID mismatch / synthesized | 0.096622 | 0.071452 |
| ID mismatch / R2 | 0.006145 | 0.004139 |
| materiality | STV_COMPOSITION_MATERIAL | STV_COMPOSITION_MATERIAL |

## Recomputed GPR S0 to S2

| Quantity | Value |
|---|---|
| S0 rows | 45927 |
| S2 rows | 45927 |
| insertions | 0 |
| deletions | 0 |
| coordinate rewrites | 52 |
| ID rewrites | 0 |
| ambiguous attribution | 0 |
| S0 subset S2 | True |
| R1 status | STRUCTURALLY_UNDEFINED |
| GPR_REPLAY_STATUS | PASS (byte-identical, 7/7 files) |

## Ordering recomputation

Independently: **10 pairs, 50 cells — UNCHANGED 45, FLIP 5, TIE_CREATED 0, TIE_BROKEN 0**. Field-wise identical to `07_ORDERING_MATRIX.json`.

Precision source: TrackEval pedestrian_detailed.csv COMBINED row; HOTA/DetA/AssA recomputed as the mean over alpha thresholds, IDF1/MOTA direct. Full precision was available for the historical
deployments too, so the comparison is not limited to 3-decimal values.

**Transitions changed by 3-decimal rounding: 0.** No flip is a rounding artifact.

### The five flips, at full precision

| A | B | metric | A_R0 | B_R0 | A_R0-B_R0 | A_R2 | B_R2 | A_R2-B_R2 | transition |
|---|---|---|---|---|---|---|---|---|---|
| BoT-SORT | Deep-OC-SORT | IDF1 | 81.643556 | 81.133163 | +0.510393 | 82.697586 | 82.900892 | -0.203306 | FLIP |
| Deep-OC-SORT | Hybrid-SORT | DetA | 64.787492 | 65.991183 | -1.203691 | 67.523431 | 67.311743 | +0.211688 | FLIP |
| Deep-OC-SORT | Hybrid-SORT | MOTA | 75.153090 | 75.991835 | -0.838746 | 78.936723 | 77.587679 | +1.349044 | FLIP |
| Hybrid-SORT | OC-SORT | HOTA | 66.948483 | 66.372369 | +0.576115 | 67.810525 | 67.990146 | -0.179622 | FLIP |
| Hybrid-SORT | OC-SORT | MOTA | 75.991835 | 74.535164 | +1.456671 | 77.587679 | 77.810354 | -0.222676 | FLIP |

Smallest absolute margin across all 50 cells: 0.186903 at R0 and 0.150321 at R2. No cell has a
margin below 0.05, so there are no near-ties and no ordering uncertainty from rounding.

## Chronology

| Deployment | Knowledge status |
|---|---|
| ByteTrack | HISTORICAL_OUTCOME_KNOWN_PRE_V9 |
| BoT-SORT | HISTORICAL_OUTCOME_KNOWN_PRE_V9 |
| OC-SORT | HISTORICAL_OUTCOME_KNOWN_PRE_V9 |
| Deep-OC-SORT | PROSPECTIVE_OUTCOME_UNSEEN_AT_V9_FREEZE |
| Hybrid-SORT | PROSPECTIVE_OUTCOME_UNSEEN_AT_V9_FREEZE |

OC-SORT-GPR prospective quantities first became known from `V9-MOT17-OCSORTGPR-002`. The
procedural deviation record and both failed `-001` attempts are preserved. Not all V9 quantities
were prospectively unseen: three of the five ordering deployments are historical.
