# Record 54 — PoseTrack21 Prospective Evaluation Result (VAL)

**Date:** 2026-08-22 · **Branch:** `tpami-q1-20260821` · **Status:** `OUTCOMES_COMPUTED_UNDER_FROZEN_PROTOCOL`

| upstream record | commit |
| --- | --- |
| 51 — JTA result | `b2cc61d053190dde7aa1df62afbbe41480209a5b` |
| 52 — PoseTrack21 audit | `3fe153786f2a6bd9f4466b7bf9c29b7619beffea` |
| **53 — PoseTrack21 protocol** | **`588b4a252313dfc479bac0bdc96938df5c3e3a0b`** |

Every rule was frozen and pushed **before** the first PoseTrack21 outcome existed.

---

## 0. Result in one paragraph

On 170 unseen PoseTrack21 VAL sequences the classical operators transfer and the frozen learned checkpoints still do not, even under the corrected training-consistent inference contract. Best classical is **linear at 0.2837** torso-normalized error; best learned is **mae at 2.4062**, a factor of **8.5×** worse. The catastrophic JTA regime is gone — MAE fell from 14.86 there to 2.41 here — but the population and the inference contract changed together, so that improvement is **not attributable** to the correction alone.

Two pre-registered questions resolve against expectation. The applicability-restricted **spline claim FAILS TO SUPPORT**: spline is the worst of the three classical operators here despite every case satisfying the pre-frozen strict-interior condition. And the **NTU learned-family ordering inverts** — the family that sat below every classical operator on NTU sits far above all of them here.

---

## 1. Outcome population

- **PoseTrack21 VAL — 170 sequences**, 1,794 tracks, 20,161 frames
- TRAIN contributed outcomes: **False** (0 TRAIN sequences used)
- public annotated TEST split exists: **False**

## 2. Pre-run integrity checks

| check | result |
| --- | --- |
| `population_is_val_only` | **True** |
| `exactly_170_sequences` | **True** |
| `train_outcomes_computed` | **False** |
| `gate_1r_exact_partition` | **True** |
| `identical_support_all_methods` | **True** |
| `primary_aggregate_used_only_primary_g` | **True** |
| `confidence_synthesized` | **False** |
| `protocol53_checks` | **51/51** |
| `deployment_contract_checks` | **23/23** |
| `learned_inference_contract` | corrected window-local (training-consistent) |
| `unavailable_slots_state` | NATIVE_INVALID |

### Case enumeration against the frozen record-52 audit

| g | 1 | 2 | 3 | 5 | 8 | 10 | 20 | total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| audit cases at frozen g | 773 | 365 | 229 | 85 | 44 | 23 | 4 | 1,523 |
| evaluated | 634 | 313 | 190 | 70 | 41 | 18 | 4 | **1,270** |
| excluded | 139 | 52 | 39 | 15 | 3 | 5 | 0 | 253 |

the frozen normalization rule: a case is dropped when L_torso is undefined at any of its target frames (either hip native missing, or a degenerate zero scale), or when its sub-segment carries fewer than two anchors. Excluded, never repaired.

## 3. Applicability under strict non-bridging segmentation

- scoreable occluded targets: **78,194**
- anchors: 482,945
- native-missing observations (excluded, never scoreable): 200,050

| Gate 1R category | count | share of targets |
| --- | ---: | ---: |
| eligible (strictly interior) | 6,942 | 8.88 % |
| ineligible — leading | 8,173 | 10.45 % |
| ineligible — trailing | 8,729 | 11.16 % |
| no anchor in the segment | 54,350 | 69.51 % |
| **sum** | **78,194** | **100.00 %** |

Exact partition: **True**. Eligible rate **8.88 %** — so **91.12 %** of scoreable occluded targets admit no interpolation problem under the frozen rule. Runs off the frozen grid: 459.

Per-sequence eligibility: min 0.00 %, Q1 1.84 %, median 7.15 %, Q3 15.48 %, max 48.48 % (n = 169).

**Normalization coverage.** L_torso defined on **43,305** segment-frame scales (**73.96 %**); 15,248 undefined and excluded, never repaired.

## 4. Support at every frozen gap length

| | g=1 | g=2 | g=3 | g=5 | g=8 | g=10 | g=20 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| cases | 634 | 313 | 190 | 70 | 41 | 18 | 4 |
| (sequence, g) cells | 113 | 79 | 70 | 46 | 27 | 11 | 4 |
| independent sequences | 113 | 79 | 70 | 46 | 27 | 11 | 4 |
| in primary aggregate | **yes** | **yes** | **yes** | **yes** | no | no | no |

Primary grid **{1,2,3,5}**; sparse descriptive **{8,10,20}**; 1,270 evaluated cases in total, identical for every method.

## 5. Method outcomes

### Primary aggregate over g ∈ {1,2,3,5} (sequence-first)

| method | primary | sequences | cells | per-seq min | Q1 | median | Q3 | max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `linear` | **0.2837** | 125 | 308 | 0.0035 | 0.0828 | 0.1409 | 0.2580 | 4.7523 |
| `spline` | **0.3204** | 125 | 308 | 0.0044 | 0.0854 | 0.1449 | 0.2973 | 5.0490 |
| `kalman` | **0.2857** | 125 | 308 | 0.0055 | 0.0812 | 0.1343 | 0.2424 | 4.9400 |
| `mae` | **2.4062** | 125 | 308 | 0.0177 | 0.3304 | 0.5330 | 1.6796 | 41.5159 |
| `bigru_seed0` | **4.0552** | 125 | 308 | 0.1985 | 1.0724 | 1.5684 | 3.6175 | 62.2368 |
| `bigru_seed1` | **3.8699** | 125 | 308 | 0.2301 | 0.9932 | 1.5369 | 3.5594 | 62.0258 |
| `bigru_seed2` | **3.8652** | 125 | 308 | 0.1490 | 0.9556 | 1.4298 | 3.4595 | 61.8888 |

### Error at every gap length (sparse cells marked \*)

| method | g=1 | g=2 | g=3 | g=5 | g=8\* | g=10\* | g=20\* |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `linear` | 0.2049 | 0.4677 | 0.2896 | 0.5755 | 0.3819 | 0.4742 | 0.6156 |
| `spline` | 0.2437 | 0.4782 | 0.3305 | 0.6912 | 0.3516 | 0.3973 | 0.6255 |
| `kalman` | 0.2112 | 0.4715 | 0.3023 | 0.5680 | 0.3413 | 0.4307 | 0.5291 |
| `mae` | 2.2245 | 3.3152 | 2.7923 | 2.6852 | 3.5238 | 2.2016 | 0.8968 |
| `bigru_seed0` | 3.7780 | 5.4806 | 4.6101 | 4.7488 | 4.4782 | 2.9570 | 1.6117 |
| `bigru_seed1` | 3.6907 | 4.9549 | 4.3498 | 4.5778 | 4.6178 | 2.8206 | 1.7132 |
| `bigru_seed2` | 3.6433 | 5.0371 | 4.4331 | 4.5938 | 4.3925 | 2.8334 | 1.7723 |

\* descriptive sparse-support cell: evaluated and reported, **excluded from the primary aggregate**. Every method refused exactly `[8, 10, 20]`.

*per-g means on PoseTrack21 VAL are computed over SMALL and largely NON-OVERLAPPING sets of sequences (113, 79, 70, 46, 27, 11 and 4 independent sequences at g=1,2,3,5,8,10,20). Cross-g comparison within a method is therefore weakly identified here, unlike JTA where every gap length drew on the same 256 sequences. The non-monotone per-g profiles seen on this population — present for the CLASSICAL operators too — must not be read as the flat-profile signature reported for the learned models on JTA.*

## 6. Prospective spline test

**Condition (frozen):** every reconstructed target lies strictly inside the observed temporal support of its own valid non-bridged segment (record 53). New pass/fail threshold introduced: **False**.

| concept | meaning, kept distinct |
| --- | --- |
| **operator validity** | the cubic-spline stencil is mathematically defined |
| **aggregation validity** | a (sequence, g) cell exists so the frozen sequence-first mean is defined |
| **method applicability** | Gate 1R strict interior — the only condition admitting a target into the spline evaluation |

# `FAILS_TO_SUPPORT`

The real-world PoseTrack21 VAL result FAILS TO SUPPORT the applicability-restricted spline claim. Every evaluated case satisfies the pre-frozen strict-interior condition, yet under that restriction spline is the WORST of the three classical operators (0.3204 against linear 0.2837 and Kalman 0.2857) and also carries the largest per-sequence maximum. It is beaten by linear at every gap length inside the primary grid.

| g | spline | linear | ratio | spline better | in primary |
| --- | ---: | ---: | ---: | :--: | :--: |
| 1 | 0.2437 | 0.2049 | 1.190 | **no** | yes |
| 2 | 0.4782 | 0.4677 | 1.022 | **no** | yes |
| 3 | 0.3305 | 0.2896 | 1.141 | **no** | yes |
| 5 | 0.6912 | 0.5755 | 1.201 | **no** | yes |
| 8 | 0.3516 | 0.3819 | 0.921 | yes | no |
| 10 | 0.3973 | 0.4742 | 0.838 | yes | no |
| 20 | 0.6255 | 0.6156 | 1.016 | **no** | no |

**Not an anchor-scarcity artefact.** anchor support is ample: 96.5 %, 96.8 %, 95.8 % and 95.7 % of cases at g=1,2,3,5 carry at least the four anchors the spline implementation requires, and 78.5 % of all cases carry twelve or more. Only 3.8 % of cases fall below four anchors, so the result is NOT a thin-anchor artefact. No mechanism is asserted beyond that.

**Relation to earlier results.** On JTA (record 51) spline was the BEST classical operator under the same kind of pre-frozen interior restriction; on NTU (record 45) it was by far the worst family in the noise-amplification estimand. PoseTrack21 lands with NTU in ordering, not with JTA. These are three populations under two different estimands and no unified claim is made here; the earlier 3DPW T4 conclusion and JTA record 51 are quoted, not rewritten.

## 7. Learned cross-population transfer

First prospective external evaluation under the corrected contract (`corrected window-local (training-consistent)`). No retraining, no checkpoint reselection, no architecture change.

BiGRU seed spread: 0.1900 (3.8652–4.0552) — systematic, not stochastic.

### Q1 — does the corrected deployment remove the JTA-style failure?

**PARTIALLY, AND NOT ATTRIBUTABLY**

the magnitude collapses: on JTA the same frozen checkpoints scored MAE 14.86 and BiGRU 27.30-27.76 torso lengths; on PoseTrack21 VAL under the corrected contract they score MAE 2.41 and BiGRU 3.87-4.06. The catastrophic regime is gone. But this is NOT a controlled comparison: the population changed AND the inference contract changed at the same time, so the improvement cannot be attributed to the correction alone. The only controlled evidence for the correction is the verification suite, which shows it is exactly a no-op where training and old inference already agreed and exactly window-local where they did not.

### Q2 — are the errors finite and scale-plausible?

**YES**

every learned case error is finite. The per-sequence MEDIAN is 0.5330 for MAE and about 1.5684 for BiGRU — around half a torso length and one and a half torso lengths respectively, which is physically plausible. The MEAN is far higher (2.41 and 3.87-4.06) because the per-sequence distribution is heavily right-skewed, with maxima of 41.5 and 62.2. Both the mean and the dispersion are reported; neither is suppressed.

### Q3 — does the NTU learned-family direction remain visible?

**NO — IT INVERTS**

on NTU the learned family sat BELOW every classical operator (BiGRU 0.075-0.090 < MAE 0.117 < linear 0.605 < Kalman 1.437 < spline 10.546). On PoseTrack21 VAL the ordering is linear 0.2837 < Kalman 0.2857 < spline 0.3204 << MAE 2.4062 < BiGRU 3.8652-4.0552. The learned family moves from best to worst, and within it BiGRU and MAE swap places: BiGRU led on NTU, MAE leads here.

*Estimand caveat: record 45 reports beta, the noise-amplification slope from the E5 sigma sweep, NOT a torso-normalized reconstruction error. No sigma sweep is applicable to PoseTrack21 (no jitter rule is frozen for it, exactly as for JTA), so this is an ORDERING comparison across two different estimands and not a like-for-like magnitude comparison.*

### Q4 — population shift or the already-fixed preprocessing mismatch?

**THE PREPROCESSING MISMATCH IS EXCLUDED; THE RESIDUAL IS NOT ATTRIBUTED**

the preprocessing mismatch diagnosed on JTA is verified fixed: 23/23 checks, including exact agreement with the old path where the normalization domains coincide and exact window-locality where they do not. So the residual gap is NOT that defect. It is NOT thereby shown to be population shift. Untested alternatives remain open and are listed rather than dismissed.

Untested alternatives, listed rather than dismissed:
- structural input shift: 4 of 17 slots (both eyes, both ears) are permanently NATIVE_INVALID on PoseTrack21
- no confidence channel exists and none is synthesized
- PoseTrack21 segments are short — strict non-bridging leaves far less temporal context per window than the 120-frame training window assumes
- genuine domain gap between NTU indoor single-subject capture and PoseTrack21 in-the-wild multi-person video
- the target construct differs: NTU targets are synthetically masked, PoseTrack21 targets are natural annotated occlusions

## 8. Cross-population comparison (nothing recomputed)

`ntu_recomputed = False` · `jta_recomputed = False` · `record_51_unchanged = True`

| method | NTU record 45 (β, φ=0) | JTA record 51 | PoseTrack21 VAL |
| --- | ---: | ---: | ---: |
| `linear` | 0.60490 | 0.5836 | 0.2837 |
| `spline` | 10.54643 | 0.4562 | 0.3204 |
| `kalman` | 1.43686 | 0.5079 | 0.2857 |
| `mae` | 0.11684 | 14.8596 | 2.4062 |
| `bigru_seed0` | 0.07856 | 27.7580 | 4.0552 |
| `bigru_seed1` | 0.07496 | 27.5859 | 3.8699 |
| `bigru_seed2` | 0.09015 | 27.2968 | 3.8652 |

> **the three columns are NOT the same estimand. NTU record 45 reports a noise amplification slope beta; JTA record 51 and PoseTrack21 record 54 report torso-normalized reconstruction error under their own frozen protocols, on different populations, different joint sets and different segmentation rules. Only ORDERING within a column may be compared across columns, and even that carries the estimand caveat.**

| population | ordering |
| --- | --- |
| ntu_record_45 | BiGRU < MAE < linear < Kalman << spline |
| jta_record_51 | spline < Kalman < linear << MAE < BiGRU |
| posetrack21_val | linear < Kalman < spline << MAE < BiGRU |

## 9. Confirmations

| statement | value |
| --- | --- |
| `training_performed` | **False** |
| `checkpoint_reselection` | **False** |
| `architecture_modified` | **False** |
| `hyperparameters_tuned` | **False** |
| `protocol_modified_after_first_posetrack_outcome` | **False** |
| `train_reconstruction_outcomes` | **0** |
| `jta_record_51_unchanged` | **True** |
| `jta_record_51_recomputed` | **False** |
| `ntu_results_recomputed` | **False** |
| `3dpw_t4_interpretation_modified` | **False** |
| `stgcn_run` | **False** |
| `project_final_test_sealed` | **True** |
| `record_54_committed` | **False** |

Result artifact `data/posetrack21/audit/val_eval_primary.json` — SHA-256 `d73ba1bc9bde6925d15959b8b0a19fc8707c0f6958924ec2e991dcf8b9bdc668`.

