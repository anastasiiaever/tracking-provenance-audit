# Record 55 — PoseTrack21 VAL Sequence-Clustered Uncertainty (SUPPLEMENTARY)

**Date:** 2026-08-22 · **Status:** `SUPPLEMENTARY — DOWNSTREAM OF THE FROZEN PROSPECTIVE RESULT`

Supplementary analysis **downstream of the frozen prospective result**, record 54 (`60ded1973568045735394263073c47119552cae1`), executed under v3.2 §6.A (`26f66ee11113963d02863f2bf3b04cf07846538e`). It adds uncertainty to the frozen point estimates and **replaces none of them**.

This record does not: recompute or alter any frozen point estimate; modify record 53 or record 54; modify any protocol rule; open project final_test; train, reselect checkpoints or change architecture.

## 1. Recovery of the per-sequence contributions

Record 54 stored per-sequence dispersion quantiles but not the per-sequence values; the clustered bootstrap needs the values. the FROZEN evaluation functions in scripts/posetrack21/evaluate_val.py (byte-identical to commit 60ded19) were imported and re-driven over the same VAL population; the frozen evaluate_val.py was NOT modified.

| method | recovered | frozen (record 54) | bitwise equal |
| --- | ---: | ---: | :--: |
| `linear` | 0.28373618281876 | 0.28373618281876 | **True** |
| `spline` | 0.32038581125267 | 0.32038581125267 | **True** |
| `kalman` | 0.28569476746424 | 0.28569476746424 | **True** |
| `bigru_seed0` | 4.05523235682741 | 4.05523235682741 | **True** |
| `bigru_seed1` | 3.86987062825683 | 3.86987062825683 | **True** |
| `bigru_seed2` | 3.86519972861945 | 3.86519972861945 | **True** |
| `mae` | 2.40616965225251 | 2.40616965225251 | **True** |

All seven method entries reproduce **bitwise exactly**. Identical support across methods: **True**; support matches record 54: **True**; TRAIN opened: **False**.

## 2. Bootstrap specification — frozen before any interval was computed

Specification file SHA-256 `cffa7760bfbb347bf40b7ff1cf7bd2c7dbcf2dac0a797280b8b5c8895ab2bd66`.

| parameter | value |
| --- | --- |
| independent unit | PoseTrack21 VAL sequence |
| resampling frame | all 170 distributed VAL sequences |
| draws | 10,000 |
| RNG seed | 20260822 |
| interval | percentile, 95 % |
| estimator | frozen `protocol53.primary_aggregate`, unmodified |

**Cluster integrity.** when a sequence is drawn, its ENTIRE within-sequence contribution structure is carried with it: every case, at every gap length, for every method. Individual gaps/cases are NEVER resampled as independent observations.

**Missing-g handling.** inherited from the frozen estimator and NOT special-cased: within a drawn sequence the equal-per-g step averages over the PRIMARY_G values that sequence actually has. A drawn sequence with no primary-g cell contributes nothing to that draw, exactly as in the frozen point estimate.

**Pairing.** within a single bootstrap draw the SAME resampled multiset of sequences is used for every method, so per-draw differences between methods are paired by construction. All methods share an identical 1270-case support, so a sequence that contributes to one method contributes to all.

**Why percentile, not BCa.** BCa needs a jackknife acceleration term over clusters; the percentile interval is simpler, makes fewer assumptions here, and is not tuned to any observed result. Chosen before seeing intervals and not revisited.

Execution: 10,000 draws, seed 20260822, **0 discarded**, 125/170 sequences contributing a primary-g cell.

## 3. Results

| method | frozen point | 95 % CI | width | seq median | seq IQR |
| --- | ---: | :--: | ---: | ---: | ---: |
| `linear` | 0.2837 | [0.2012, 0.3892] | 0.1880 | 0.1409 | 0.1753 |
| `kalman` | 0.2857 | [0.1996, 0.3967] | 0.1971 | 0.1343 | 0.1611 |
| `spline` | 0.3204 | [0.2225, 0.4422] | 0.2198 | 0.1449 | 0.2119 |
| `mae` | 2.4062 | [1.5299, 3.4794] | 1.9495 | 0.5330 | 1.3492 |
| `bigru_seed0` | 4.0552 | [2.8523, 5.5240] | 2.6717 | 1.5684 | 2.5451 |
| `bigru_seed1` | 3.8699 | [2.7209, 5.2986] | 2.5777 | 1.5369 | 2.5662 |
| `bigru_seed2` | 3.8652 | [2.7043, 5.3019] | 2.5976 | 1.4298 | 2.5039 |
| `bigru_mean` | 3.9301 | [2.7666, 5.3718] | 2.6052 | — | — |

### Paired sequence-level differences

| difference | observed | 95 % CI | includes zero | conclusion |
| --- | ---: | :--: | :--: | --- |
| `linear - kalman` | -0.0020 | [-0.0084, +0.0037] | **yes** | UNRESOLVED — interval includes zero |
| `linear - spline` | -0.0366 | [-0.0700, -0.0137] | no | resolved: linear < spline |
| `kalman - spline` | -0.0347 | [-0.0677, -0.0130] | no | resolved: kalman < spline |
| `mae - linear` | +2.1224 | [+1.2521, +3.1806] | no | resolved: mae > linear |
| `bigru_mean - linear` | +3.6464 | [+2.4951, +5.0609] | no | resolved: bigru_mean > linear |

*the marginal interval for each method is wide (linear [0.2012, 0.3892]) because it carries the variability of which sequences are drawn. The PAIRED difference intervals are far tighter because both methods are evaluated on the SAME resampled sequences in every draw, so the shared sequence-composition variance cancels. Comparing overlapping marginal intervals would be the wrong test; the paired interval is the correct one and is what the conclusions use.*

## 4. Conclusions

### linear vs Kalman — `UNRESOLVED`

The ordering of linear and Kalman is UNRESOLVED. The paired sequence-level difference is -0.0020 with a 95 % percentile interval of [-0.0084, +0.0037], which includes zero. No ranking between them is asserted, and no significance threshold beyond the frozen interval coverage is invented.

### spline

Spline is resolved as WORSE than both linear and Kalman: the paired differences are linear − spline -0.0366 CI [-0.0700, -0.0137] and kalman − spline -0.0347 CI [-0.0677, -0.0130], both excluding zero. This SUPPORTS the record-54 spline FAILS_TO_SUPPORT verdict at the sequence level.

### classical vs learned

The classical-vs-learned gap is supported by the sequence-clustered uncertainty. MAE − linear is +2.1224 CI [+1.2521, +3.1806] and BiGRU(mean) − linear is +3.6464 CI [+2.4951, +5.0609]; both intervals exclude zero by a wide margin. The frozen learned models are worse than the classical operators on this population by an amount the data support.

## 5. Caveats

- supplementary and downstream: this analysis adds uncertainty to the frozen record-54 point estimates and replaces none of them
- the percentile interval is a bootstrap approximation, not an exact coverage guarantee, and 125 of 170 VAL sequences contribute a primary-g cell
- the three BiGRU seeds are training realisations of one frozen family, summarised as a mean rather than pooled into a seed-level interval (record 24 rule)
- sparse g {8,10,20} are structurally excluded from the primary aggregate and therefore carry no interval here; they remain descriptive in record 54

## 6. Confirmations

| statement | value |
| --- | --- |
| `frozen_point_estimates_altered` | **False** |
| `record_53_modified` | **False** |
| `record_54_modified` | **False** |
| `protocol_modified` | **False** |
| `training_performed` | **False** |
| `checkpoint_reselection` | **False** |
| `project_final_test_opened` | **False** |
| `jta_corrected_contract_diagnostic_run` | **False** |
| `new_dataset_added` | **False** |
| `new_model_family_added` | **False** |
| `record_55_committed` | **False** |

