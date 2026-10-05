# ALLOWED CLAIMS

Each entry is supported by the artifact named in `26_CLAIM_TO_ARTIFACT_MAP.csv`.
Wording here is indicative, not final prose.

## Framework

- A benchmark score characterises an evaluated output state, not a tracker in
  isolation.
- The submitted file of several widely used trackers contains both tracker output
  and rows added by offline post-processing.
- Which audit is available depends on the structural transition. A row-additive
  transition admits a row-level admission decomposition; a transition that
  rewrites surviving rows does not.
- Scoreable-target admission is a reference-side diagnostic. It asks whether an
  added row has reference support under a stated criterion.

## MOT17, released-deployment audit

- Five released deployments on one validation population each add rows that fail
  admission, with primary-gate non-admission from 28.92 to 49.02 % and
  gate-stable non-admission from 23.45 to 43.90 %.
- All 25 metric deltas are positive.
- 5 of 50 exhaustive pairwise metric cells cross zero, and all five survive
  3-decimal and 2-decimal score reporting.
- TARGET_REFERENCE_ABSENT is empty for every MOT17 deployment.
- Re-execution reconstructed the same 12,767-row synthesized population with all
  12,767 identities unique and reproduced every available frozen
  sequence-by-class count, 105 of 105 for MOT17 and 130 of 130 including MOT20.

## MOT20

- Of seven configurations pre-specified before any MOT17 execution, one is
  eligible for the held-out comparison, five fail through detector-training
  overlap and one is unresolved.
- The eligible deployment adds 34,814 rows; primary-gate non-admission is
  25.1364 % and gate-stable non-admission is 19.0469 %.
- One deployment permits a composition check on a second population but no
  pairwise ordering analysis.

## DanceTrack, controlled DTI

- Under one common operator applied by us, with `n_min=25` and `n_dti=20`
  identical for four trackers, primary-gate non-admission is 42.03 to 68.46 %
  and gate-stable non-admission 38.05 to 62.62 %.
- The operator adds 3.79 to 6.93 % of output rows.
- 12 of 20 metric deltas are positive, 8 negative. OC-SORT and Deep-OC-SORT rise
  on all five metrics; ByteTrack and Hybrid-SORT fall on four of five and rise
  only on AssA.
- The controlled DanceTrack intervention shows that substantial non-admission can
  occur whether the common post-processing operator improves or degrades the
  reported metrics.
- 7 of 30 exhaustive pairwise metric cells cross zero, all surviving 3-decimal
  and 2-decimal reporting.
- The composition conclusion does not depend on `n_min` 25 against 30:
  non-admission differs by at most 0.42 percentage points.
- Training-split disjointness holds for all four trackers.

## DanceTrack, TARGET_REFERENCE_ABSENT

- The class is non-empty on DanceTrack and empty on MOT17 and MOT20.
- Every such row lies strictly inside a gap in the ground-truth track's own
  observed frame set. DanceTrack's scoreable ground truth is fragmented: 209 of
  273 tracks have at least one interior gap, 1,370 gaps in total; MOT17's has
  none.
- The class records that the anchor-resolved reference identity is absent at that
  frame. It is not a tracker error and not a false-positive label.

## DanceTrack, row-local geometric support

- Admission is defined through the anchors and the availability of the
  anchor-resolved reference identity; the synthesized row's own coordinates are
  not part of the predicate.
- Admitted rows reach maximum IoU at or above 0.5 in 97.392 to 98.2151 % of cases,
  not 100 %.
- 62.0388 to 73.5409 % of non-admitted rows overlap some scoreable ground truth at
  maximum IoU at or above 0.5.
- For TARGET_REFERENCE_ABSENT rows, the intended reference identity is absent in
  all 3,451 cases while another ground-truth identity overlaps the box in 3,448
  of them. The two statements are not equivalent.

## DanceTrack, controlled GSI

- GSI applied to the same four frozen states is key-additive but
  content-rewriting: 0 deletions, and 56.8389 to 67.4668 % of surviving coordinates
  rewritten.
- Its metric-delta split and its 7-of-30 crossing count match the DTI arm, and
  the seven cells are the same pair-and-metric identities.
- GSI changes the evaluated state through extensive coordinate rewriting in
  addition to interpolation, while the observed ordering crossings are already
  established by its interpolation stage.
- Decomposed: R0 to L_GSI is strictly row-additive and carries 7 of 30 crossings;
  L_GSI to GSI rewrites coordinates only and carries 0 of 30.
- The Gaussian-process stage does produce evaluated-state change: all 20 metric
  cells move, median share of absolute movement 0.1812, and in 8 of 20 cells it
  opposes the linear stage.
- STV and an R1 analogue are not defined for this transition.

## OC-SORT GPR boundary case

- G0 and G2 both contain 45,927 rows with zero insertions and zero deletions.
- 52 rows change by more than 1e-6 px; 2,622 rows differ at exact floating-point
  equality, in x and y only, by magnitudes from 8.9e-12 to 1.7e-05 px; w and h
  are bit-identical everywhere.
- The three-decimal summary file is byte-identical between the two states while
  the full-precision detailed output differs in 197 LocA-family fields.
- An operator can rewrite the evaluated state and move no reported metric.

## StrongSORT++ AFLink and GSI structural case

- AFLink changes the identity of 1,316 rows across 29 remappings, reduces the
  distinct identity count from 435 to 406, and loses one row, from 46,914 to
  46,913.
- GSI then adds 3,184 rows, drops none, and rewrites 46,866 of 46,913 surviving
  coordinates, 99.8998 %.
- Containment of the pre-GSI state in the post-GSI state holds on identity keys
  and fails on row content.
- No R1 analogue exists for this transition because withholding added rows would
  change the fit and therefore the surviving coordinates. The frozen artifact
  records this in its own `nesting_claim` and `stv_state` fields.
- The base tracker output was written but not scored, so the AFLink comparison is
  structural only.

## Scope

- The principal single-population limitation is substantially reduced: the
  ordering evidence now comes from two populations, four controlled trackers and
  two operator families over 25 sequence-level clusters, where previously all 50
  ordering cells came from one population.
