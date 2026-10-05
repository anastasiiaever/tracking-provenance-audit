import os
V="<AUDIT_ROOT>/V6_SOURCE_OF_TRUTH"
def w(n,s): open(os.path.join(V,n),"w").write(s.lstrip("\n")); print("  wrote",n)

w("10_TABLE_PLAN.md", r"""
# TABLE PLAN

Each entry gives the table's job, its columns, the artifact every number comes
from, and whether it is new in v6. Numbers are in `05_NUMERIC_LEDGER.csv`; do not
retype them from prose.

## Main text

### T1. Documented post-processing and eligibility — REUSE v5 Table 1
Job: show which released systems document a post-processing rule, where, and
whether a held-out comparison is available.
Columns: system; operator; documented setting; reporting location (R, M, S, C);
population; TRAINING_SPLIT_DISJOINT; SELECTION_PROVENANCE; eligibility verdict.
Source: v5 main Table 1 plus v5 supplement Tables S1 and S2.
Change from v5: keep the two provenance fields separate, as in v5. Add the four
DanceTrack trackers as a second block, marked CONTROLLED, with the operator
column reading "common DTI applied by us" and "common GSI applied by us".

### T2. Evidence architecture — NEW in v6
Job: tell the reader, once and early, which audit each arm admits and why. This
is the table that prevents the reader from expecting STV everywhere.
Columns: arm; released or controlled; population; trackers; operator; transition
type; operator family; STV available; R1 available; ordering analysis available;
pre-specified or post-hoc.
Source: `06_EVIDENCE_ARCHITECTURE.csv`, eight rows.
Note: this replaces the role v5 played with scattered prose in Secs. 4.4 and S6.

### T3. Composition of added rows, MOT17 and MOT20 — REUSE v5 Table 2
Job: the released-deployment composition result.
Columns: deployment; R0 rows; R2 rows; synthesized; U; ID; ABS; ADM; non-admitted
count; non-admitted %; gate-stable non-admitted count; gate-stable %.
Source: Step 9 `B1_mot17_gate_summary.csv` and `B2_mot20_gate_summary.csv` for the
primary gate; `C3_gate_stability_summary.csv` for gate-stable.
Change from v5: the MOT20 row must carry its gate-stable figure, 6,631 and
19.046935 %. v5's table has the column; the D1B report dropped it, and that
omission must not propagate.

### T4. Composition of added rows, DanceTrack under one common operator — NEW
Job: the controlled composition result.
Columns: tracker; R0 rows; R2 rows; inserted; inserted % of R2; U; ID; ABS; ADM;
non-admitted count and %; gate-stable count and %.
Source: D1B `D1B_state_inventory.csv`, `D1B_stv_primary.csv`,
`D1B_gate_persistence_summary.csv`.
Note: the ABS column is non-zero here and zero in T3. That contrast is the point;
do not merge T3 and T4 into one table and lose it.

### T5. Metric values at each evaluated state — REUSE v5 Table 3, EXTEND
Job: the state-to-metric mapping for every arm that has one.
Columns: arm; tracker; state; HOTA; DetA; AssA; IDF1; MOTA.
Rows: MOT17 five deployments at R0, R1, R2; MOT20 eligible deployment at R0, R1,
R2; DanceTrack four trackers at R0, R2 under DTI and at R0, L_GSI, GSI under GSI;
StrongSORT++ at S0 and S2 in the frozen naming; OC-SORT at G0 and G2.
Source: v5 Table 3; D1B `D1B_metric_states.csv`; D2B and D2C
`D2C_three_state_metrics.csv`; frozen `pedestrian_summary.txt` files.
Note: say in the caption that DetA and AssA are factors of HOTA.

### T6. Unified pairwise ordering margins — NEW, replaces v5 Table S5's role
Job: one schema for every ordering cell in the paper, so the reader can see that
the same four facts are reported for each.
Columns: arm; tracker A; tracker B; metric; margin at the pre state; margin at the
post state; crosses zero; survives 3dp; survives 2dp; bootstrap P(sign differs).
Rows: 50 MOT17 cells, 30 DanceTrack DTI cells, 30 DanceTrack GSI cells, 30 each
for the two GSI sub-transitions. Main text shows the crossing cells and the
counts; the full matrices go to the supplement.
Source: `FINAL_unified_pairwise_margins.csv`,
`D2C_three_state_pairwise_margins.csv`, D1B.1 `D1B1_flip_precision_audit.csv`.
Caption must state that the matrix is exhaustive and the cells are dependent.

### T7. Operators that admit no row-additive decomposition — REUSE v5 Sec. S6 as a main table
Job: the structural result, promoted from supplement prose because it now carries
two arms, including the boundary case.
Columns: operator; family; keys; content of surviving rows; rows inserted;
rows deleted; rows rewritten; STV status; R1 status; metric change.
Rows: OC-SORT GPR; StrongSORT++ AFLink; StrongSORT++ GSI; DanceTrack GSI,
GP stage.
Source: `FINAL_gpr_rewrite_recount.csv`; frozen `DECOMPOSITION.json`;
`D2C_gsi_linear_state_inventory.csv`.
The GPR row must state the 1e-6 px criterion alongside the 52.

## Supplement

| id | table | source | note |
|---|---|---|---|
| S1 | post-processing census | v5 Table S1 | reuse |
| S2 | audited repository versions and commits | v5 Table S2 | reuse, add the four DanceTrack repositories and the TrackEval pin |
| S3 | MOT17 composition, full | v5 Table S3 | reuse |
| S4 | MOT17 metric values, full | v5 Table S4 | reuse |
| S5 | complete MOT17 ordering matrix, 50 cells | v5 Table S5 | reuse, add the 3dp and 2dp survival columns |
| S6 | StrongSORT++ metrics | v5 Table S6 | reuse, relabel states to the chosen scheme |
| S7 | MOT20 eligibility, 7 configurations | v5 Table S7 | reuse |
| S8 | MOT20 composition and metrics | v5 Table S8 | reuse |
| S9 | MOT20 output identities and hashes | v5 Table S9 | reuse |
| S10 | admission composition by gap length | v5 Table S10 | reuse |
| S11 | admission composition across gates, MOT17 | v5 Table S11 | reuse |
| S12 | unmatched-anchor categories | v5 Table S12 | reuse |
| S13 | DanceTrack asset inventory and hashes | D1A manifest and `hashes/` | NEW |
| S14 | DanceTrack training-split and selection provenance | `D1B_training_selection_provenance.csv` | NEW |
| S15 | DanceTrack composition across the five gates | `D1B_stv_gate_sweep.csv` | NEW |
| S16 | DanceTrack per-sequence composition | `D1B_per_sequence_composition.csv` | NEW |
| S17 | DTI parameter sensitivity, 25/20 against 30/20 | `D1B_dti_parameter_sensitivity.csv`, `D1B_stv_sens30_primary_gate.csv` | NEW |
| S18 | complete DanceTrack DTI ordering matrix, 30 cells | `D1B_pairwise_30cells.csv`, D1B.1 recomputation | NEW |
| S19 | DanceTrack REFERENCE_ABSENT mechanism | D1B.1 `D1B1_reference_absent_audit.json` | NEW |
| S20 | GT fragmentation, DanceTrack against MOT17 | final defence Part II | NEW |
| S21 | row-local geometric support by STV class | `D1B2_row_local_support.csv` | NEW |
| S22 | REFERENCE_ABSENT row-local support | `D1B2_reference_absent_local_support.csv` | NEW |
| S23 | GSI state inventory and rewrite shares | `D2B_state_inventory.csv` | NEW |
| S24 | complete DanceTrack GSI ordering matrix, 30 cells | `D2B_pairwise_30cells.csv` | NEW |
| S25 | GSI three-state decomposition, metrics | `D2C_three_state_metrics.csv` | NEW |
| S26 | GSI three-state decomposition, margins | `D2C_three_state_pairwise_margins.csv` | NEW |
| S27 | three-tracker provenance sensitivity | `FINAL_three_tracker_provenance_sensitivity.csv` | NEW |
| S28 | GPR rewrite recount across precisions | `FINAL_gpr_rewrite_recount.csv` | NEW, and it is the table that documents the rounding-boundary artifact |
| S29 | bootstrap design and index hashes | Step 9 `D1_bootstrap_indices.sha256`, D1B `D1B_bootstrap_indices.sha256` | reuse and extend |
| S30 | minimal tracking-submission provenance record | v5 Table S30 | reuse |
| S31 | full provenance ledger | `09_PROVENANCE_LEDGER.csv` | NEW |

## Rules

- Every table caption names the artifact its numbers come from.
- Any cell with no artifact is written `[FACT NEEDED]`, never estimated.
- Percentages carry the precision given in the ledger. Do not round 19.046935 to
  19.05 in the supplement table that is meant to be checkable; the main text may
  use 19.05 if the supplement gives full precision.
- Counts and percentages of different denominators never share a column.
""")

w("11_FIGURE_PLAN.md", r"""
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
""")
