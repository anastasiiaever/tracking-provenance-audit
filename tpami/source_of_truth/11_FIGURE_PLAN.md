# FIGURE PLAN

v5 ships four main figures and three supplement figures. Three of the four main
figures survive; one is tied to the removed branch.

## Main

### F1. Admission cases on frames — REUSE
v5 asset: `fig_stv_cases_frames.pdf`, v5 main Fig. 1.
Job: show what an admitted and a non-admitted synthesized row look like on real
frames, with anchors and the reference track.
Change: add a third panel showing a TARGET_REFERENCE_ABSENT case from DanceTrack,
with the reference track's own gap drawn explicitly. That class does not occur on
MOT17, so v5's figure cannot illustrate it, and it is the class most likely to be
misread as a false positive.
Status: asset exists; the third panel is NEW and needs a frame selected from
`D1B2_row_local_examples.csv`.

### F2. The audit and its evaluated states — REUSE, EXTEND
v5 asset: `fig_provenance_eligibility_overview.pdf`, v5 main Fig. 2.
Job: define R0, R1, R2 and the eligibility check in one picture.
Change: add the transition-type branch, so the reader sees that R1 exists only on
the row-additive path and that the rewriting path stops at a state comparison.
Status: asset exists; needs the branch added.

### F3. Composition of added rows — REUSE, EXTEND
v5 asset: `fig1_v9_state_provenance.pdf`, v5 main Fig. 3.
Job: stacked bars of the four classes, normalised per deployment.
Change: add the four DanceTrack bars beside the five MOT17 bars and the MOT20
bar. The ABS segment appears only on the DanceTrack bars; that visual contrast
carries the population-dependence result.
Status: asset exists; needs the DanceTrack block.

### F4. Ordering margins across arms — NEW
Job: show every ordering cell once, with the crossing cells identified.
Form: one panel per arm. Each cell is a short segment from its pre-state margin to
its post-state margin on a signed axis, so a crossing is a segment that passes
through zero. Mark the zero line; mark the 3dp and 2dp reporting resolutions as
bands so the reader can see the crossings survive them.
Source: `FINAL_unified_pairwise_margins.csv`.
This replaces no v5 figure. v5 reported the ordering result in tables only.

### REMOVED: common-support reversal
v5 asset: `fig3_common_support_reversal.pdf`, v5 main Fig. 4.
This figure belongs to the NTU RGB+D skeleton-reconstruction branch. See
`13_V5_REUSE_MAP.md`; the branch moves out of the tracking narrative, so the
figure moves with it.

## Supplement

| id | figure | v5 asset | status |
|---|---|---|---|
| SF1 | PoseTrack21 annotation semantics | `figS_posetrack_annotation_semantics.pdf` | moves with the skeleton branch |
| SF2 | evaluation map | `fig2_evaluation_map.pdf` | moves with the skeleton branch |
| SF3 | amplification over gap length and correlation | `fig2b_amplification_over_g_phi.pdf` | moves with the skeleton branch |
| SF4 | GT fragmentation, DanceTrack against MOT17 | none | NEW: per-track gap-count histograms, 209 of 273 against 0 of 339 |
| SF5 | row-local support distribution by STV class | none | NEW: maximum-IoU histograms per class, with the 0.5 line, showing the overlap between admitted and non-admitted |
| SF6 | GSI stage decomposition | none | NEW: per-cell linear and GP contributions as a signed stacked bar over the 20 metric cells, showing the 8 cells where they oppose |

## Rules

- No figure introduces a number that is not in `05_NUMERIC_LEDGER.csv`.
- Every new figure needs a generator script stored beside the artifact it reads,
  and the caption names that artifact.
- If a panel cannot be built from an existing artifact, the caption slot is
  `[FACT NEEDED]` and the panel is dropped rather than illustrated schematically.
