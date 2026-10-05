# Artifact map: manuscript claim -> released file

Every row was checked to exist in this release at the tagged commit.

| claim | where in the paper | released file | present |
|---|---|---|---|
| MOT17 added-row composition, four classes | Sec. 4.2, Table 2 | `results/mot17/stv_composition.csv` | yes |
| MOT17 metric values per state | Sec. 4.3, supp. S5 | `results/mot17/metrics_by_state.csv` | yes |
| MOT17 pairwise margins, all 50 cells | Sec. 4.3, Table 4, Fig. 4 | `tpami/results/margins/FINAL_unified_pairwise_margins.csv` | yes |
| MOT20 eligibility census, 7 configurations | Sec. 4.4, Table 1, supp. S7 | `results/mot20/eligibility.csv` | yes |
| MOT20 eligible-cell result | Sec. 4.4, supp. S8 | `results/mot20/deep_oc_sort_result.json` | yes |
| DanceTrack controlled DTI, state inventory | Sec. 5.2, Table 3 | `tpami/results/dancetrack_dti/D1B_state_inventory.csv` | yes |
| DanceTrack controlled DTI, admission at the primary gate | Sec. 5.2, Table 3 | `tpami/results/dancetrack_dti/D1B_stv_primary.csv` | yes |
| DanceTrack gate persistence | Sec. 5.2, supp. S10 | `tpami/results/dancetrack_dti/D1B_gate_persistence_summary.csv` | yes |
| DanceTrack metric deltas | Sec. 5.3, Table 3 | `tpami/results/dancetrack_dti/D1B1_metric_deltas_recomputed.csv` | yes |
| DanceTrack pairwise margins, all 30 cells | Sec. 5.4, Table 4, Fig. 4 | `tpami/results/margins/FINAL_unified_pairwise_margins.csv` | yes |
| three-tracker provenance sensitivity | Sec. 5.4, supp. S15 | `tpami/results/margins/FINAL_three_tracker_provenance_sensitivity.csv` | yes |
| reference-absent rows, row-local support | Sec. 5.5, 5.6, supp. S13 | `tpami/results/dancetrack_dti/D1B2_reference_absent_local_support.csv` | yes |
| GSI state inventory and stage decomposition | Sec. 6.1, 6.2, supp. S16 | `tpami/results/dancetrack_gsi/D2C_gsi_linear_state_inventory.csv` | yes |
| GSI three-state metrics | Sec. 6.2, supp. S16 | `tpami/results/dancetrack_gsi/D2C_three_state_metrics.csv` | yes |
| GSI three-state pairwise margins | Sec. 6.2, supp. S16 | `tpami/results/dancetrack_gsi/D2C_three_state_pairwise_margins.csv` | yes |
| rewrite-only GPR recount by tolerance | Sec. 6.3, supp. S17 | `tpami/results/gpr_rewrite_only/FINAL_gpr_rewrite_recount.csv` | yes |
| StrongSORT++ structural decomposition | Sec. 6.4, supp. S18 | `results/mot17/strongsort_decomposition.csv` | yes |
| ground-truth interior-gap population | Sec. 5.5, supp. ledger | `tpami/results/gt_gap/gt_gap_population_summary_20261005.csv` | yes |
| every numeral in the paper | supp. S26 ledger | `tpami/source_of_truth/05_NUMERIC_LEDGER.csv` | yes |
| transition-type normative table | Sec. 3.1, Fig. 2 | `tpami/source_of_truth/07_METHOD_DEFINITIONS.md` | yes |
| evidence architecture, per-arm applicability | Sec. 3.4, Fig. 2 | `tpami/source_of_truth/06_EVIDENCE_ARCHITECTURE.csv` | yes |
