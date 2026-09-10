# Claim matrix

Every headline figure this repository exposes, the artifact that carries it, the
command that checks it, and what an external re-measurement would additionally
need. All values were verified against the frozen records named in the last
column.

**Status vocabulary**

| | |
|---|---|
| `PUBLICLY_REPRODUCIBLE` | the released artifact and code re-derive the figure offline, with no external asset |
| `PUBLIC_SUMMARY_ONLY` | the figure is released and checked against its frozen record, but re-measuring it needs a corpus this repository does not ship |
| `EXTERNAL_ASSET_REQUIRED` | not derivable here at all without a corpus and/or checkpoints |
| `MISSING_FROM_RELEASE` | referenced by the paper, no artifact here |

## Tracking arm

| paper claim | public artifact | verification command | external asset needed | status |
|---|---|---|---|---|
| MOT17 ordering: 10 pairs × 5 metrics, **45 unchanged, 5 reversed**, 0 ties created/broken | `results/mot17/ordering_matrix.csv`, `results/mot17/ordering_summary.json` | `python scripts/verify_ordering.py` | none | `PUBLICLY_REPRODUCIBLE` |
| Full-precision R0/R2 metric values, all five deployments | `results/mot17/metrics_by_state.csv` | `python scripts/verify_release.py` (cross-file stage) | none | `PUBLICLY_REPRODUCIBLE` |
| MOT17 admission composition, **28.92%–49.02%** not admitted | `results/mot17/stv_composition.csv` | `python scripts/verify_admission.py` | none | `PUBLICLY_REPRODUCIBLE` |
| The admission classifier itself (gate-before-assignment, one-to-one, exact partition) | `src/tracking_provenance_audit/stv.py` | `python scripts/verify_admission.py` (fixtures), `pytest tests/test_tracking_provenance_core.py` | none | `PUBLICLY_REPRODUCIBLE` |
| StrongSORT++ admits **no row-additive decomposition**; S0/S2 only | `results/mot17/strongsort_decomposition.csv`, `results/mot17/strongsort_structure.json` | `pytest tests/test_tracking_provenance_core.py` | none | `PUBLICLY_REPRODUCIBLE` |
| MOT20: **7** pre-specified cells, **1** eligible, 0 checkpoints substituted | `results/mot20/eligibility.csv`, `results/mot20/eligibility_context.json` | `python scripts/verify_mot20_eligibility.py` | none | `PUBLICLY_REPRODUCIBLE` |
| MOT20 executed cell: **34,814** synthesized, **25.14%** of synthesized / **1.55%** of submitted | `results/mot20/deep_oc_sort_stv.csv`, `results/mot20/deep_oc_sort_result.json` | `python scripts/verify_admission.py` | none | `PUBLICLY_REPRODUCIBLE` |
| Admission-gate sensitivity over **0.3–0.7** | `results/stv_sensitivity/*.csv` | `pytest tests/test_release_integrity.py` | none | `PUBLICLY_REPRODUCIBLE` |
| Post-processing universe: **8 pipelines × 3 datasets = 24 cells** | `metadata/postprocessing_universe.csv` | `python scripts/verify_release.py` | none | `PUBLICLY_REPRODUCIBLE` |
| Detector identity: `bytetrack_ablation` and `ocsort_mot17_ablation` are **byte-identical** (`26cb8d28…`, 792,835,795 B) | `metadata/external_assets.csv` | inspect the two rows; hash your own copy | the checkpoints, to re-verify | `PUBLIC_SUMMARY_ONLY` |
| Re-measuring any MOT17/MOT20 metric from tracker outputs | `src/tracking_provenance_audit/` | see `docs/REPRODUCIBILITY.md` level 2–3 | MOT17/MOT20, 8 tracker repos, TrackEval, checkpoints | `EXTERNAL_ASSET_REQUIRED` |

## Controlled arm

| paper claim | public artifact | verification command | external asset needed | status |
|---|---|---|---|---|
| PoseTrack21 applicability: **78,194** scoreable occluded targets → **6,942 (8.88%)** eligible, **54,350** no-anchor, exact partition | `results/controlled/posetrack21_applicability.csv` | `python scripts/verify_controlled_arm.py` | PoseTrack21 annotations, to re-measure | `PUBLIC_SUMMARY_ONLY` |
| Segmentation sensitivity: **8.88 / 10.50 / 36.43%** eligible; **91.12 / 89.50 / 63.57%** ineligible; target count invariant | `results/controlled/posetrack21_applicability.csv` | `python scripts/verify_controlled_arm.py` | PoseTrack21 annotations | `PUBLIC_SUMMARY_ONLY` |
| Support ladder: **1,270** evaluated cases; primary grid g ∈ {1,2,3,5} | `results/controlled/posetrack21_support_by_gap.csv` | `python scripts/verify_controlled_arm.py` | PoseTrack21 annotations | `PUBLIC_SUMMARY_ONLY` |
| Sequence-clustered bootstrap: MAE−linear **+2.12 [+1.25,+3.18]**, BiGRU−linear **+3.65 [+2.50,+5.06]**, linear−Kalman **−0.0020 [−0.0084,+0.0037]** (includes zero) | `results/controlled/posetrack21_bootstrap.csv` | `python scripts/verify_controlled_arm.py` | PoseTrack21 annotations **and** the three learned checkpoints | `PUBLIC_SUMMARY_ONLY` |
| NTU support accounting: **300** cells (**5.8824%**) reclassified per operator; **900** of **181,275** gap rows affected | `results/controlled/ntu_support_accounting.json` | `python scripts/verify_controlled_arm.py` | NTU RGB+D + PYSKL keypoints | `PUBLIC_SUMMARY_ONLY` |
| The reversal: **−1.20859 [−2.55087,−0.13772]** over 181,275 → **+3.63705 [+2.49074,+4.58300]** over 180,375, both excluding zero in opposite directions | `results/controlled/ntu_support_accounting.json` | `python scripts/verify_controlled_arm.py` | NTU RGB+D + the trained MAE checkpoint | `PUBLIC_SUMMARY_ONLY` |
| Support shifts: linear **5.24980** on both supports (shift 0); MAE **9.52936 → 8.88685** (shift −0.64251); contaminated pooled **10.73795** | `results/controlled/ntu_support_accounting.json` | `python scripts/verify_controlled_arm.py` | NTU RGB+D + checkpoint | `PUBLIC_SUMMARY_ONLY` |
| Object-trajectory applicability: BDD100K-derived **2.41%** eligible of 1,054,224; MOT17 GT **25.13%** of 66,226; exact partition on both | `results/controlled/objecttraj_applicability.csv` | `python scripts/verify_controlled_arm.py` | BDD100K MOT labels, MOT17 | `PUBLIC_SUMMARY_ONLY` |
| KITTI transfer: **12,554 / 16,096 = 0.779945** ineligible, threshold 0.10, status **SUPPORTED**; strata sum to the pool | `results/controlled/kitti_applicability.csv`, `results/controlled/kitti_hypothesis.json` | `python scripts/verify_controlled_arm.py` | KITTI tracking | `PUBLIC_SUMMARY_ONLY` |
| The support-accounting engine: refuses to read own-support and common-support as one number; reports the support shift as a quantity | `src/applicability_audit/` | `python scripts/verify_support_accounting.py`, `pytest tests/test_applicability_audit*.py` | none | `PUBLICLY_REPRODUCIBLE` |
| Cross-population input shift: **17** slots, **13** available, **four** unavailable (`NATIVE_INVALID`, never padded), no confidence channel | `results/controlled/learned_input_contract.json` | `python scripts/verify_controlled_arm.py` | PoseTrack21 + the checkpoints, to re-measure | `PUBLIC_SUMMARY_ONLY` |
| JTA within-corpus replication: **48,854,154** targets → **20,266,544** eligible (**41.48%**), **58.52%** refused, exact partition over 256 sequences | `results/controlled/jta_applicability.csv`, `results/controlled/jta_headline.json` | `python scripts/verify_controlled_arm.py` | JTA corpus | `PUBLIC_SUMMARY_ONLY` |
| JTA learned deployment-sensitivity failure: classical best **0.456**, learned best **14.86**, factor **32.57**, BiGRU seed range **0.461** — a deployment failure, not an architecture verdict | `results/controlled/jta_headline.json` | `python scripts/verify_controlled_arm.py` | JTA corpus + the frozen checkpoints | `PUBLIC_SUMMARY_ONLY` |
| 3DPW matched-predictor validation: Kalman **28/28** in band, spline **24/28**; medians **0.999585 / 0.996523**; worst \|ratio−1\| **0.009077 / 0.472676**; verdict `FAIL_QUANTITATIVE_B` | `results/controlled/threedpw_matched_criterion_b.csv` | `python scripts/verify_controlled_arm.py` | 3DPW corpus | `PUBLIC_SUMMARY_ONLY` |
| 3DPW: the four missed cells are all spline at **g = 20** | `results/controlled/threedpw_failing_cells.csv` | `python scripts/verify_controlled_arm.py` | 3DPW corpus | `PUBLIC_SUMMARY_ONLY` |
| Operator-level noise decomposition (analytic identity T1–T3) | `src/reconstruction_generic/`, `src/trajectory_cross_domain/` | `pytest tests/test_applicability_audit_equivalence.py` | none for the operators; 3DPW for the validation | `PUBLIC_SUMMARY_ONLY` |
| Learned-model noise-sensitivity grid: β at φ ∈ {0, 0.5, 0.7, 0.85} for every operator and every trained checkpoint, with intervals | `results/controlled/learned_beta_by_phi.csv` | `python scripts/verify_controlled_arm.py` | NTU + the nine checkpoints | `PUBLIC_SUMMARY_ONLY` |
| Architecture-level magnitude **unresolved**: across-training-realization variability exceeds the between-family gap; the third family is a probe, not a proposed method | `results/controlled/learned_architecture_diagnostics.json` | `python scripts/verify_controlled_arm.py` | NTU + the nine checkpoints | `PUBLIC_SUMMARY_ONLY` |

## What this means in one sentence

The **tracking arm is publicly reproducible offline end to end** at the level of
the released summaries and audit logic. The **controlled arm is released as
summaries checked against their frozen records**, not as a re-runnable pipeline:
six corpora and nine trained checkpoints stand between this repository and a
re-measurement. Every controlled figure the paper puts in front of a reader now
has a released artifact and a check; **nothing in the controlled arm is
`MISSING_FROM_RELEASE`**.

No command in this repository re-measures anything. `docs/REPRODUCIBILITY.md`
sets out what a real re-measurement costs.
