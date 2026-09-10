# V9 Prospective Tracking-Provenance Audit Protocol

**FROZEN BEFORE ANY V9 OUTCOME EXISTS.**

No tracker was executed, no post-processing was run on real benchmark outputs, no TrackEval
invocation was made, no STV was computed, no ranking was computed, and no V9 metric or result
file was inspected. Frozen 2026-08-30 from census commit `ad688f554e47bb1ebd859dc83967b4845f12f446`.

Frozen V8 is untouched.

## 1. Cell roles (all 24 census cells, none dropped)

**Schema A1: `documentation_role` and `audit_mode` are independent axes.**

| Deployment | Dataset | Census status | Documentation role | Family | Audit mode | Execution state | Split status | Stop |
|---|---|---|---|---|---|---|---|---|
| ByteTrack | MOT17 | DOCUMENTED_DEFAULT | SECONDARY_SPLIT_ADAPTED | LINEAR_DTI_ROW_ADDITIVE | ROW_ADDITIVE_R0_R1_R2 | EXECUTABLE | SPLIT_ADAPTED_FROM_TEST | — |
| ByteTrack | MOT20 | DOCUMENTED_DEFAULT | SECONDARY_SPLIT_ADAPTED | LINEAR_DTI_ROW_ADDITIVE | STOPPED_BEFORE_EXECUTION | STOPPED_DATASET_NOT_ACQUIRED | SPLIT_ADAPTED_FROM_TEST | yes |
| ByteTrack | DanceTrack | NO_DOCUMENTED_RULE | NO_DOCUMENTED_RULE | LINEAR_DTI_ROW_ADDITIVE | DOCUMENTATION_ONLY | NOT_EXECUTABLE_DOCUMENTATION_ONLY | NOT_APPLICABLE | — |
| BoT-SORT | MOT17 | DOCUMENTED_DEFAULT | SECONDARY_SPLIT_ADAPTED | LINEAR_DTI_ROW_ADDITIVE | ROW_ADDITIVE_R0_R1_R2 | EXECUTABLE | SPLIT_ADAPTED_FROM_TEST | — |
| BoT-SORT | MOT20 | DOCUMENTED_DEFAULT | SECONDARY_SPLIT_ADAPTED | LINEAR_DTI_ROW_ADDITIVE | STOPPED_BEFORE_EXECUTION | STOPPED_DATASET_NOT_ACQUIRED | SPLIT_ADAPTED_FROM_TEST | yes |
| BoT-SORT | DanceTrack | NO_DOCUMENTED_RULE | NO_DOCUMENTED_RULE | LINEAR_DTI_ROW_ADDITIVE | DOCUMENTATION_ONLY | NOT_EXECUTABLE_DOCUMENTATION_ONLY | NOT_APPLICABLE | — |
| OC-SORT | MOT17 | DOCUMENTED_DEFAULT | SECONDARY_SPLIT_ADAPTED | LINEAR_DTI_ROW_ADDITIVE | ROW_ADDITIVE_R0_R1_R2 | EXECUTABLE | SPLIT_ADAPTED_FROM_TEST | — |
| OC-SORT | MOT20 | DOCUMENTED_DEFAULT | SECONDARY_SPLIT_ADAPTED | LINEAR_DTI_ROW_ADDITIVE | STOPPED_BEFORE_EXECUTION | STOPPED_DATASET_NOT_ACQUIRED | SPLIT_ADAPTED_FROM_TEST | yes |
| OC-SORT | DanceTrack | IMPLEMENTED_NOT_DATASET_DOCUMENTED | DOCUMENTATION_ONLY_IMPLEMENTED | LINEAR_DTI_ROW_ADDITIVE | DOCUMENTATION_ONLY | NOT_EXECUTABLE_DOCUMENTATION_ONLY | NOT_APPLICABLE | — |
| OC-SORT-GPR | MOT17 | DOCUMENTED_OPTIONAL | OPTIONAL_DOCUMENTED_FAMILY | GPR_REWRITE | NON_ROW_ADDITIVE_S0_S2 | EXECUTABLE | SPLIT_ADAPTED_FROM_TEST | — |
| OC-SORT-GPR | MOT20 | DOCUMENTED_OPTIONAL | OPTIONAL_DOCUMENTED_FAMILY | GPR_REWRITE | STOPPED_BEFORE_EXECUTION | STOPPED_DATASET_NOT_ACQUIRED | SPLIT_ADAPTED_FROM_TEST | yes |
| OC-SORT-GPR | DanceTrack | IMPLEMENTED_NOT_DATASET_DOCUMENTED | DOCUMENTATION_ONLY_IMPLEMENTED | GPR_REWRITE | DOCUMENTATION_ONLY | NOT_EXECUTABLE_DOCUMENTATION_ONLY | NOT_APPLICABLE | — |
| Deep-OC-SORT | MOT17 | DOCUMENTED_DEFAULT | PRIMARY_DOCUMENTED_VALIDATION | LINEAR_DTI_ROW_ADDITIVE | ROW_ADDITIVE_R0_R1_R2 | EXECUTABLE | DOCUMENTED_ON_VALIDATION | — |
| Deep-OC-SORT | MOT20 | DOCUMENTED_DEFAULT | PRIMARY_DOCUMENTED_VALIDATION | LINEAR_DTI_ROW_ADDITIVE | STOPPED_BEFORE_EXECUTION | STOPPED_DATASET_NOT_ACQUIRED | DOCUMENTED_ON_VALIDATION | yes |
| Deep-OC-SORT | DanceTrack | DOCUMENTED_DEFAULT | PRIMARY_DOCUMENTED_VALIDATION | LINEAR_DTI_ROW_ADDITIVE | STOPPED_BEFORE_EXECUTION | STOPPED_DATASET_NOT_ACQUIRED | DOCUMENTED_ON_VALIDATION | yes |
| Hybrid-SORT | MOT17 | DOCUMENTED_DEFAULT | SECONDARY_SPLIT_ADAPTED | LINEAR_DTI_ROW_ADDITIVE | ROW_ADDITIVE_R0_R1_R2 | EXECUTABLE | SPLIT_ADAPTED_FROM_TEST | — |
| Hybrid-SORT | MOT20 | DOCUMENTED_DEFAULT | SECONDARY_SPLIT_ADAPTED | LINEAR_DTI_ROW_ADDITIVE | STOPPED_BEFORE_EXECUTION | STOPPED_DATASET_NOT_ACQUIRED | SPLIT_ADAPTED_FROM_TEST | yes |
| Hybrid-SORT | DanceTrack | IMPLEMENTED_NOT_DATASET_DOCUMENTED | DOCUMENTATION_ONLY_IMPLEMENTED | LINEAR_DTI_ROW_ADDITIVE | DOCUMENTATION_ONLY | NOT_EXECUTABLE_DOCUMENTATION_ONLY | NOT_APPLICABLE | — |
| StrongSORT++ | MOT17 | DOCUMENTED_DEFAULT | PRIMARY_DOCUMENTED_VALIDATION | LINK_PLUS_SMOOTHING | NON_ROW_ADDITIVE_S0_S2 | EXECUTABLE | DOCUMENTED_ON_VALIDATION | — |
| StrongSORT++ | MOT20 | DOCUMENTED_DEFAULT | SECONDARY_SPLIT_ADAPTED | LINK_PLUS_SMOOTHING | STOPPED_BEFORE_EXECUTION | STOPPED_DATASET_NOT_ACQUIRED | SPLIT_ADAPTED_FROM_TEST | yes |
| StrongSORT++ | DanceTrack | NO_DOCUMENTED_RULE | NO_DOCUMENTED_RULE | LINK_PLUS_SMOOTHING | DOCUMENTATION_ONLY | NOT_EXECUTABLE_DOCUMENTATION_ONLY | NOT_APPLICABLE | — |
| SparseTrack | MOT17 | IMPLEMENTED_NOT_DATASET_DOCUMENTED | DOCUMENTATION_ONLY_IMPLEMENTED | LINEAR_DTI_ROW_ADDITIVE | DOCUMENTATION_ONLY | NOT_EXECUTABLE_DOCUMENTATION_ONLY | NOT_APPLICABLE | — |
| SparseTrack | MOT20 | IMPLEMENTED_NOT_DATASET_DOCUMENTED | DOCUMENTATION_ONLY_IMPLEMENTED | LINEAR_DTI_ROW_ADDITIVE | DOCUMENTATION_ONLY | NOT_EXECUTABLE_DOCUMENTATION_ONLY | NOT_APPLICABLE | — |
| SparseTrack | DanceTrack | IMPLEMENTED_NOT_DATASET_DOCUMENTED | DOCUMENTATION_ONLY_IMPLEMENTED | LINEAR_DTI_ROW_ADDITIVE | DOCUMENTATION_ONLY | NOT_EXECUTABLE_DOCUMENTATION_ONLY | NOT_APPLICABLE | — |

Documentation role: SECONDARY_SPLIT_ADAPTED 9, DOCUMENTATION_ONLY_IMPLEMENTED 6, PRIMARY_DOCUMENTED_VALIDATION 4, NO_DOCUMENTED_RULE 3, OPTIONAL_DOCUMENTED_FAMILY 2.

Audit mode: DOCUMENTATION_ONLY 9, STOPPED_BEFORE_EXECUTION 8, ROW_ADDITIVE_R0_R1_R2 5, NON_ROW_ADDITIVE_S0_S2 2.

SCHEMA A1: documentation role and structural audit mode are INDEPENDENT axes. `documentation_role` is derived only from census documentation status and documented split; it never encodes structural behaviour. `audit_mode` is derived only from structural family, corpus availability and documentation-executability; it never encodes documentation status. NON_ROW_ADDITIVE_STRUCTURAL is REMOVED as a documentation role; the non-row-additive property is now carried by audit_mode = NON_ROW_ADDITIVE_S0_S2 together with structural_family. Documentation status is never inferred from structural behaviour, and vice versa.

Amendment A1 (`02A_PROTOCOL_AMENDMENT_ROLE_AUDITMODE.md`) records why this schema replaced the
single-role schema of the original protocol commit. A1 preceded every V9 outcome.

## 2. Populations

### MOT17 — FROZEN_AND_MATERIALISED

- Source split: MOT17 train (labelled), FRCNN detector copy only
- Detector-copy rule: MOT17 ships DPM/FRCNN/SDP copies of each base sequence with byte-identical ground truth; exactly one copy (FRCNN) is used so the seven base sequences are counted once.
- Frame-range rule: Verbatim from ByteTrack tools/convert_mot17_to_coco.py:57-58 and reproduced identically in Deep-OC-SORT data/tools/convert_mot17_to_coco.py:57-58: image_range = [num_images//2 + 1, num_images - 1] over 0-indexed images; image i maps to 1-indexed frame i+1, so the retained native frame range is [num//2 + 2, num].
- Frame-index convention: 1-indexed; rebased to 1..val_half_length by subtracting rebase_offset = num//2 + 1
- GT source: MOT17 train gt/gt_val_half.txt emitted by the frozen converter; per-sequence sha256 above
- Ignore/crowd semantics: MOTChallenge gt column 7 (flag) must equal 1; class column 8 must equal 1 (pedestrian). Classes {3,4,5,6,9,10,11} are non-person and dropped; classes {2,7,8,12} are ignore-person regions and are neither scored nor counted as reference identities. Visibility (column 9) is NOT thresholded.
- Evaluator configuration: TrackEval MOT17 val_half; identical config for every comparable pipeline
- Population manifest hash: sha256 over the sorted concatenation of per-sequence (sequence, native_frames_retained, rebase_offset, val_half_length, gt_sha256) records
- Common population: All quantitatively comparable MOT17 deployments use THIS population. Deep-OC-SORT's documented MOT17-val is the same second-half split (identical converter rule), so no pipeline selects its own population.

| Sequence | native length | retained native frames | rebase offset | val-half length |
|---|---|---|---|---|
| MOT17-02-FRCNN | 600 | 302–600 | 301 | 299 |
| MOT17-04-FRCNN | 1050 | 527–1050 | 526 | 524 |
| MOT17-05-FRCNN | 837 | 420–837 | 419 | 418 |
| MOT17-09-FRCNN | 525 | 264–525 | 263 | 262 |
| MOT17-10-FRCNN | 654 | 329–654 | 328 | 326 |
| MOT17-11-FRCNN | 900 | 452–900 | 451 | 449 |
| MOT17-13-FRCNN | 750 | 377–750 | 376 | 374 |
| **total** | | | | **2652** |

### MOT20 — STOPPED_DATASET_NOT_ACQUIRED

- Intended rule (frozen now): Analogous frozen split: labelled MOT20 train sequences MOT20-01/02/03/05, one common second-half population under the identical image_range rule as MOT17 (Deep-OC-SORT ships data/tools/convert_mot20_to_coco.py with the same rule).
- Blocking: No MOT20 corpus is present; the population manifest cannot be materialised or hashed.
- Rule is frozen now; only materialisation is deferred. Cells remain in the universe.

### DanceTrack — STOPPED_DATASET_NOT_ACQUIRED

- Intended rule (frozen now): Official DanceTrack val split as distributed. The census found no documented validation path defining another population, so the official val split governs.
- Blocking: No DanceTrack corpus is present.
- Rule is frozen now; only materialisation is deferred.

## 3. Wording contract (binding on V9 language)

Applies to: every SECONDARY_SPLIT_ADAPTED cell.

- REQUIRED: State that the repository's documented TEST-set post-processing rule was applied unchanged to a pre-specified validation population.
- FORBIDDEN: Do not state or imply that the repository documents post-processing use on the validation split for these cells.
- Exempt: PRIMARY_DOCUMENTED_VALIDATION cells (Deep-OC-SORT; StrongSORT++ MOT17) may state that validation use is documented, because it is.

**This corrects over-broad wording that appeared in frozen V8 ('under their documented post-processing rules' applied to a validation population). V8 is NOT edited; the correction binds V9 language only.**

## 4. Counting units

- Deployments in universe: **8**
- Independent post-processing families: **3**

  - `LINEAR_DTI_ROW_ADDITIVE`: ByteTrack, BoT-SORT, OC-SORT, Deep-OC-SORT, Hybrid-SORT, SparseTrack
  - `GPR_REWRITE`: OC-SORT-GPR
  - `LINK_PLUS_SMOOTHING`: StrongSORT++

Every future table must state BOTH deployment count and independent family count. Repository count is never family count.

## 5. Row-additive audit contract

- R0 = raw tracker output immediately before the audited interpolation stage
- R2 = output immediately after the frozen documented interpolation call
- Invariant: R0 subseteq R2 by row identity; pre-existing R0 rows field-identical up to normalised serialisation
- Row identity: (sequence, frame, track_id) after the frozen parser normalisation
- Normalisation allowed: numeric formatting/precision of the writer only; no coordinate or id change
- On failure: do NOT construct R1; classify the cell STRUCTURAL_DECOMPOSITION_UNAVAILABLE
- R1 = R0 plus only those synthesized R2 rows admitted by the frozen STV criterion; GT-informed diagnostic only; never deployable

## 6. Non-row-additive contract

Applies to GPR_REWRITE, LINK_PLUS_SMOOTHING. no R1 analogue may be forced.

- S0 = state immediately before the audited transformation
- S2 = state immediately after it
- Structural measurements: `rows_inserted`, `rows_deleted`, `preexisting_rows_with_changed_coordinates`, `preexisting_rows_with_changed_ids`, `row_identity_survives`, `S0_subseteq_S2`

If the transformation rewrites values that its own regression/smoothing fit consumes, a row-subset causal decomposition is declared STRUCTURALLY_UNDEFINED. This is an allowed outcome, not a failure of the study.

## 7. OC-SORT GPR reproducibility contract

- **GPR_AUDIT_SEED = 20260830** (frozen now, before execution)
- Upstream source is NOT modified.
- Stochastic APIs found in source: numpy.random.choice (median_trick); sklearn GaussianProcessRegressor(n_restarts_optimizer=2) optimizer restarts
- the harness seeds NumPy/random global state immediately before calling the unmodified upstream entry point
- exactly one same-seed replay is required as reproducibility verification
- replay values must never be averaged or pooled with the first execution
- On failure: status = REPRODUCIBILITY_FAILURE; no quantitative GPR ranking claim is licensed
- Forbidden: seed search; choosing a seed because of an observed output
- Recorded: upstream source hash, seed, exact invocation, python/numpy/sklearn versions, stochastic APIs reached

## 8. STV reference-semantic rule

- Primary gate: IoU = 0.5
- Anchors: the two bracketing R0 observations of a synthesized row
- Reference assignment: per-frame one-to-one assignment against scoreable GT, computed on R0 BEFORE any synthesized row is introduced, and then frozen
- Order: gate first, then assignment (gate-before-assignment)
- Algorithm: Hungarian one-to-one on IoU with the gate applied as a hard admissibility mask before assignment
- Classes in priority order: `ANCHOR_UNMATCHED` > `ANCHOR_ID_MISMATCH` > `TARGET_REFERENCE_ABSENT` > `SEMANTICALLY_ADMITTED`
- Only ANCHOR_ID_MISMATCH licenses 'anchors resolve, under the frozen matcher, to different ground-truth identities'. ANCHOR_UNMATCHED is non-admission, NOT demonstrated semantic error.
- STV is a reference-side diagnostic and never a replacement tracking metric
- Sensitivity gates [0.3, 0.4, 0.5, 0.6, 0.7]: DESCRIPTIVE; the 0.5 result remains primary regardless of sensitivity outcome

## 9. Primary outcomes per quantitative cell

- A n_R0_rows
- B n_R2_rows
- C n_synthesized_rows
- D synthesized_fraction_of_R2
- E stv_four_class_counts
- F stv_four_class_pct_of_synthesized
- G nonadmission_fraction_of_synthesized
- H nonadmission_fraction_of_R2
- I anchor_id_mismatch_fraction_of_synthesized
- J anchor_id_mismatch_fraction_of_R2
- K per_metric_R0_and_R2
- L per_metric_delta_R2_minus_R0

Non-row-additive: C-J replaced by the structural transition inventory; A, B, K, L retained.
the reported quantities are fixed here; no post-hoc selection of which to headline.

## 10. Metrics

- Evaluator: TrackEval pinned at `12c8791b303e0a0b50f753af204249e622d0281a` (same evaluator family pinned in V8; commit frozen before execution)
- Metrics: HOTA, DetA, AssA, IDF1, MOTA
- Unavailable: METRIC_NOT_AVAILABLE
- no metric may be substituted after results are seen
- GT parsing: frozen MOTChallenge parser; identical config for every comparable pipeline

## 11. Pairwise ordering matrix

- Comparable only within: same dataset; same frozen population; same evaluator configuration; same metric
- every quantitatively eligible deployment pair; relations ['A>B', 'A=B', 'A<B'] at ['R0', 'R2']
- Classified as: UNCHANGED, FLIP, TIE_CREATED, TIE_BROKEN
- all pairs reported, not only those that flip
- Reported: eligible pair count, pairs per dataset, pairs per metric, full matrix, total flips, ties created/broken

**These are SYSTEM-LEVEL deployment orderings. A cross-pipeline ordering difference must NOT be attributed solely to the post-processing family, because tracker and detector systems differ. Within-pipeline R0->R2 deltas and between-pipeline ordering are separate estimands.**

## 12. Materiality (secondary, descriptive)

- Status: SECONDARY_DESCRIPTIVE_ONLY; not the headline hypothesis
- Criterion: `STV_COMPOSITION_MATERIAL = total_non_admitted_synthesized_rows / synthesized_rows >= 0.10`
- Denominator justification: The denominator is synthesized rows because the criterion concerns the composition of what the post-processor produced, not of the whole submission.
- Mandatory companion: the corresponding fraction of total submitted R2 rows must ALWAYS be reported alongside, so a large conditional fraction cannot be read as a submission-wide effect
- Threshold frozen at 0.1; no post-hoc adjustment; carries no significance or generalization claim.

## 13. Status vocabulary

`SUPPORTED`, `FAILS_TO_SUPPORT`, `UNRESOLVED`, `DESCRIPTIVE`, `POST_HOC`, `STRUCTURALLY_UNDEFINED`, `METRIC_NOT_AVAILABLE`, `REPRODUCIBILITY_FAILURE`, `NO_DOCUMENTED_RULE`

- SUPPORTED/FAILS_TO_SUPPORT only for a criterion frozen before its outcome
- simple measured quantities need no hypothesis label
- no confirmatory claim may be invented because a result is large

## 14. Stop conditions

- unresolved census AMBIGUOUS cell (currently: none)
- population not reproducible from a frozen manifest (currently: MOT20, DanceTrack)
- raw/post state boundary unidentifiable
- documented rule needs an undocumented parameter choice
- evaluator configuration differs across comparable pipelines
- a supposedly row-additive implementation rewrites existing rows
- GPR RNG not externally fixable/replayable without changing scientific source semantics
- CLI is not the actual execution path
- any real V9 metric/STV outcome inspected during protocol or CLI development

a stopped cell remains in the universe carrying its stop reason; it is never silently removed.

## 15. Companion specifications

- `02_CLI_CONTRACT.md` — CLI is the execution path; 17 required tests; development only against fixtures and frozen V8 artifacts.
- `02_LITERATURE_AUDIT_SPEC.md` — disclosure coding, fixed search order, disclosure definition.
