# Record 51 — JTA Prospective Evaluation Result (VAL + TEST)

**Date:** 2026-08-22 · **Branch:** `tpami-q1-20260821`  
**Status:** `OUTCOMES_COMPUTED_UNDER_FROZEN_PROTOCOL`  
**Protocol-50 freeze commit:** `96f3185d4c0413489394ada9cb891ae5e7483d90`  
**Record-49 freeze commit:** `13c82aa4aa1448d4c00627444eb8e9ffa4bf059c`  
**Protocol-50 hashes:** MD `72d3aa44b841d02f357840881c69064ba70ce5bfacf263138e75100560aac6fc` · JSON `4352e5a67fc9808d70a3134896f007cfcbfb6fd94cf1282615dc0c000b7f82d2`

Every rule applied below was frozen and pushed **before** the first VAL/TEST byte was read. Nothing in this record re-chooses a rule, and no rule was altered after access.

---

## 0. Result in one paragraph

On 256 unseen JTA sequences, the frozen classical operators transfer and the frozen learned checkpoints do not. Spline is the best classical method at **0.4562** torso-normalized error; the best learned model (MAE) reaches **14.86**, worse by a factor of **33×**. The three BiGRU seeds land within 0.46 of one another, so this is systematic, not seed noise.

The learned per-gap profile is flat and NON-monotone in g (error at g=1 exceeds error at g=8), unlike every classical method, whose error rises monotonically with gap length. A method whose error does not grow with gap difficulty is not failing at interpolation; it is mis-conditioned on its input.

On this external population the frozen learned checkpoints, AS DEPLOYED HERE, do not transfer. The degradation is dominated by an input-conditioning shift (section 6 diagnostic), not by gap difficulty, and record 50 sec 9 froze the interpretation of these numbers as a sensitivity test rather than a benchmark BEFORE any of them existed.

**What this result is.** a frozen DEPLOYMENT SENSITIVITY FAILURE: the measured quantity is how the frozen checkpoints behave when driven through an inference path whose normalization domain does not match the one they were trained under. That is a property of the deployment, and it is exactly what a prospective cross-dataset sensitivity test is designed to expose.

**What it is not.** evidence of intrinsic inferiority of the MAE or BiGRU architectures, or of learned skeleton infilling in general. No claim about model capacity, architecture quality, or learned-vs-classical superiority may be drawn from these numbers. The three BiGRU seeds agreeing to within 0.46 shows the effect is systematic rather than stochastic; it does not show the models are weak. A corrected deployment contract is frozen for the NEXT population in record 53 and these JTA scores are NOT recomputed, replaced or retracted under it.

Separately and independently of any method outcome, **58.52 % of primary targets admit no interpolation problem at all** under the frozen eligibility rule. That refusal rate is the population-level applicability result, and it is reported rather than discarded.

---

## 1. Population and manifest

- Population: **JTA val + test** — 256 sequences (128 val + 128 test), the dataset authors' own evaluation set.
- Manifest members: **256**; aggregate SHA-256 `7dff9158519f45d7e6d4032bd80f48ebb97dc47207b9d6758b70aed8e4f11bc4`.
- Manifest file SHA-256 `3e8835563679db75f85fc85ddeb23e63aa752329ac5f62050eb1dec41353fac0`.
- Videos downloaded: **False** — annotations only.
- Corpus: 167,965,292 annotation rows, 16,150 tracks, 7,634,786 person-frames.

## 2. Pre-evaluation integrity check (section C)

**Verdict: `PASS`** — violations: none.

| assumption required by protocol 50 | holds |
| --- | --- |
| `all_22_joint_types_present_every_person_frame` | **yes** |
| `common12_present_every_person_frame` | **yes** |
| `frame_person_joint_unique` | **yes** |
| `all_coordinates_finite` | **yes** |
| `occlusion_flags_binary` | **yes** |
| `no_malformed_rows` | **yes** |
| `joint_types_in_range` | **yes** |
| `hips_always_paired` | **yes** |

`L_torso` was computable on 7,634,786 person-frames; 100,363 were **excluded, never repaired**.

The integrity pass and the evaluation pass are independent reads of the same payload; their row, track and `L_torso` counts agree exactly (see §9 cross-validation).

## 3. Applicability (section D)

- primary targets: **48,854,154**
- anchors: **39,973,340**
- out-of-frame joint states: **2,789,938**

### Gate 1R partition

| category | count | share of targets |
| --- | ---: | ---: |
| eligible (strictly interior) | 20,266,544 | 41.48 % |
| ineligible — leading | 7,378,225 | 15.10 % |
| ineligible — trailing | 5,472,388 | 11.20 % |
| no anchor at all | 15,736,997 | 32.21 % |
| **sum** | **48,854,154** | **100.00 %** |

The four categories **exactly partition** the primary targets (`exact_partition = True`, asserted in code).

**58.52 % of primary targets (28,587,610) are refused** because the interpolation problem is undefined for them. This is not a discard — the refusal rate is itself a primary applicability result.

Per-sequence eligibility is strongly heterogeneous: min 3.17 %, Q1 29.30 %, median 46.12 %, Q3 64.62 %, max 95.44 % (n = 256) — an IQR of 35.32 pp. A point estimate alone would misrepresent the population.

### Support at each frozen gap length

| g | 1 | 2 | 3 | 5 | 8 | 10 | 20 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| admitted cases | 280,020 | 227,265 | 154,793 | 94,667 | 56,107 | 38,653 | 10,762 |

Maximal target runs falling **off** the frozen grid: 891,114. They remain in the applicability statistics and create no evaluation case; the grid is not extended for JTA.

## 4. Exact reconstruction support (section E)

- evaluated cases: **862,267**
- evaluation sequences: **256**; (sequence × g) cells: **1,791**
- admission rule: Gate 1R strictly-interior AND >=2 in-segment anchors AND L_torso finite and positive on every target frame
- identical support for every method: **True** (bigru_seed0 = 862,267, bigru_seed1 = 862,267, bigru_seed2 = 862,267, kalman = 862,267, linear = 862,267, mae = 862,267, spline = 862,267)

## 5. Method outcomes (section F)

Statistic: per target frame, L2 coordinate error divided by that frame's `L_torso`; per case, the mean over the case's target frames. Aggregation is the frozen sequence-first hierarchy (equal weight per g within a sequence, then equal weight per sequence).

| method | sequence-first estimate | per-seq min | Q1 | median | Q3 | max | cases |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `linear` | **0.5836** | 0.1166 | 0.2553 | 0.3829 | 0.5785 | 4.4424 | 862,267 |
| `spline` | **0.4562** | 0.0984 | 0.2078 | 0.3025 | 0.4735 | 2.7833 | 862,267 |
| `kalman` | **0.5079** | 0.1116 | 0.2073 | 0.3190 | 0.5034 | 3.7011 | 862,267 |
| `mae` | **14.8596** | 1.1193 | 4.8189 | 11.7013 | 19.4936 | 87.2797 | 862,267 |
| `bigru_seed0` | **27.7580** | 3.8601 | 11.4045 | 21.9699 | 38.5892 | 124.7958 | 862,267 |
| `bigru_seed1` | **27.5859** | 3.8889 | 11.4402 | 21.6619 | 38.1994 | 124.3881 | 862,267 |
| `bigru_seed2` | **27.2968** | 3.8523 | 11.1382 | 21.3250 | 37.9779 | 123.7803 | 862,267 |

### Per-gap normalized error

| method | g=1 | g=2 | g=3 | g=5 | g=8 | g=10 | g=20 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `linear` | 0.1449 | 0.1985 | 0.2529 | 0.3631 | 0.5739 | 0.7918 | 1.3132 |
| `spline` | 0.1340 | 0.1633 | 0.1912 | 0.2600 | 0.4041 | 0.5516 | 1.3235 |
| `kalman` | 0.1618 | 0.1925 | 0.2223 | 0.2864 | 0.4297 | 0.6054 | 1.3562 |
| `mae` | 18.2436 | 16.7317 | 15.1934 | 14.9321 | 11.9950 | 14.6652 | 19.7358 |
| `bigru_seed0` | 38.8885 | 35.1735 | 28.5868 | 26.4386 | 21.7125 | 25.2967 | 31.0108 |
| `bigru_seed1` | 38.6960 | 34.9581 | 28.3761 | 26.2136 | 21.5295 | 25.0852 | 30.8446 |
| `bigru_seed2` | 38.5855 | 34.8222 | 28.1297 | 25.9137 | 21.2691 | 24.7628 | 30.2685 |
| **cases** | **280,020** | **227,265** | **154,793** | **94,667** | **56,107** | **38,653** | **10,762** |

Dispersion is reported descriptively. **No inferential confidence-interval convention is claimed for JTA**, because none was frozen; the project's subject-clustered bootstrap does not transfer to scene clustering.

## 6. Learned cross-dataset sensitivity (section F)

**Frozen interpretation (record 50 §9):** cross-dataset sensitivity test under structural input shift, NOT a matched-input benchmark.

- 17-slot representation retained; permanently unavailable on JTA: `nose`, `left_eye`, `right_eye`, `left_ear`, `right_ear` → state **NATIVE_INVALID**, never `PADDING`, never a target.
- confidence value 0, `confidence_available = False`; confidence synthesized: **False**.
- scored joints: COMMON_12 only.
- no retraining · no checkpoint reselection · no architecture change.

BiGRU seed spread across 3 frozen seeds: min 27.2968, mean 27.5469, max 27.7580 (range 0.4612).

### Noise-sensitivity quantities — what transfers

**Transferred: False.** The frozen E5 noise-sensitivity design is a synthetic positional-jitter sweep (arms {(iid,0.0),(ar1,0.5),(ar1,0.7),(ar1,0.85)} x 8 sigmas) injected into clean coordinates. Protocol 50 freezes NO jitter rule for JTA, and the JTA construct is NATURAL occlusion with clean engine ground truth. Choosing a jitter rule now would be a post-access protocol change, which is forbidden.

What does transfer: the sigma = 0 clean-input condition only; JTA results are reported at that single condition. Invented here: **nothing**.

### Post-hoc diagnostic — normalization envelope

*Diagnostic only. Computed after outcomes, changes no rule and no reported number.*

- Frozen backend window W = 120. NTU evaluation sequences have median length 98 frames — shorter than one window — so whole-request normalization and per-window normalization coincide there.
- JTA tracks in the sampled sequences have median length 764 frames (max 900), spanning a 1920x1080 image.
- Max |normalized coordinate| on observed anchors: NTU median 3.77 (max 8.02); JTA median 86.16 (max 1251.62).
- MAE error rises monotonically with that envelope: [0,8) → 0.57 (n=972); [8,15) → 1.17 (n=1,229); [15,30) → 2.76 (n=1,499); [30,60) → 6.68 (n=6,091); >=60 → 28.68 (n=21,810).
- Linear interpolation over the same cases is unaffected by the envelope, because it never normalizes: [0,8) → 0.059; [8,15) → 0.155; [15,30) → 0.269; [30,60) → 0.421; >=60 → 0.623.

| subset | cases | MAE | linear |
| --- | ---: | ---: | ---: |
| within the NTU envelope | 972 | 0.573 | 0.059 |
| outside the NTU envelope | 30,629 | 21.936 | 0.546 |

**Caveat.** The within-envelope subset is SELECTED on a track property (short, weakly translating tracks), not randomly sampled, and covers only 972 of 31,601 sampled cases. Its error is descriptive of that subset alone and is NOT a corrected score. The reported MAE/BiGRU outcomes remain the frozen whole-population numbers in section 5; nothing here restates them.

## 7. Prospective spline Gate 1R (section G)

**Condition (frozen, record 50 §11):** every reconstructed target lies strictly inside the observed temporal support of its own valid on-screen segment (frozen record 50 sec 11).
Frozen before VAL/TEST access: **True**; threshold created after outcomes: **False**.

| concept | meaning, kept distinct |
| --- | --- |
| **operator validity** | the spline stencil is mathematically defined; not the same as being applicable |
| **aggregation validity** | a (sequence, g) cell has >=1 case so the frozen sequence-first mean is defined |
| **method applicability** | Gate 1R strict interior: the only condition used to admit a target into the spline evaluation |

- targets admitted by the gate: **20,266,544**
- targets refused by the gate: **28,587,610** (58.52 %)
- every evaluated case satisfies the condition: **True**

Under the pre-frozen restriction, spline attains **0.4562** versus linear 0.5836 and Kalman 0.5079 — spline best of the three classical methods: **True**. Its per-sequence upper tail is also the tightest (max 2.7833 vs linear 4.4424, Kalman 3.7011): **True**.

| g | spline | linear | ratio | spline better |
| --- | ---: | ---: | ---: | :--: |
| 1 | 0.1340 | 0.1449 | 0.925 | yes |
| 2 | 0.1633 | 0.1985 | 0.823 | yes |
| 3 | 0.1912 | 0.2529 | 0.756 | yes |
| 5 | 0.2600 | 0.3631 | 0.716 | yes |
| 8 | 0.4041 | 0.5739 | 0.704 | yes |
| 10 | 0.5516 | 0.7918 | 0.697 | yes |
| 20 | 1.3235 | 1.3132 | 1.008 | **no** |

The advantage is monotone in the interior of the grid and **reverses at g = 20**, the largest frozen gap. That reversal is reported, not smoothed.

This is a prospective result on an external population under an applicability restriction frozen in advance. It is **not** a reinterpretation of the earlier 3DPW T4 result: `not_a_reinterpretation_of_3dpw_t4 = True`.

## 8. TRAIN vs VAL+TEST structure (section H)

*descriptive only; computed AFTER outcomes and used to change no evaluation rule. TRAIN contributes no reconstruction outcome.*

| quantity | TRAIN (record 49) | VAL+TEST (record 51) |
| --- | ---: | ---: |
| sequences | 256 | 256 |
| tracks | 16,236 | 16,150 |
| annotation rows | 169,542,032 | 167,965,292 |
| target fraction | 53.10 % | 53.32 % |
| anchor fraction | 43.80 % | 43.63 % |
| out-of-frame fraction | 3.10 % | 3.05 % |
| Gate 1R eligible | 41.76 % | 41.48 % |
| Gate 1R no-anchor | 31.97 % | 32.21 % |
| Gate 1R leading | 14.02 % | 15.10 % |
| Gate 1R trailing | 12.24 % | 11.20 % |
| per-seq eligibility median | 47.38 % | 46.12 % |
| per-seq eligibility IQR | 34.02 pp | 35.32 pp |
| per-seq eligibility range | 2.64–95.79 % | 3.17–95.44 % |
| runs off the frozen grid | 894,453 | 891,114 |

The evaluation population is structurally very close to TRAIN on every frozen quantity, including the wide inter-sequence heterogeneity. Record 50 blocker 1 — that the anchorless prevalence on VAL/TEST was genuinely unknown, with the 8-sequence pilot reading 61.94 % against TRAIN's 31.97 % — **resolves in favour of the TRAIN-scale figure**: the pilot was unrepresentative, not the audit.

*TRAIN record 49 reports ALL maximal target runs by length; VAL+TEST reports Gate-1R-ADMITTED evaluation cases. The two counts are not like-for-like and are not differenced.*

| g | 1 | 2 | 3 | 5 | 8 | 10 | 20 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| TRAIN, all maximal runs | 290,398 | 237,742 | 163,955 | 105,622 | 63,260 | 44,330 | 13,800 |
| VAL+TEST, admitted cases | 280,020 | 227,265 | 154,793 | 94,667 | 56,107 | 38,653 | 10,762 |

## 9. Cross-validation of the two evaluation runs

The classical and learned halves come from two invocations of the same frozen script `scripts/jta/evaluate_valtest.py`.

- classical run `valtest_eval_classical.json` → linear, spline, kalman · SHA-256 `0e8253e85a2a9830bbb72325457695c2…`
- learned run `valtest_eval_learned.json` → bigru_seed0, bigru_seed1, bigru_seed2, mae · SHA-256 `9dbb24bb59249c4f7101315d2de50051…`

**Post-access script change:** additive only: a --skip-classical switch (which methods are computed) and a --case-dump sidecar (crash recovery). No protocol rule, no estimator, no aggregation, no admission rule was touched.

| cross-check | result |
| --- | --- |
| `protocol_string_identical` | **pass** |
| `population_identical` | **pass** |
| `corpus_identical` | **pass** |
| `applicability_identical` | **pass** |
| `cases_per_sequence_identical` | **pass** |
| `classical_run_computed_classical` | **pass** |
| `learned_run_skipped_classical` | **pass** |
| `integrity_rows_match_corpus` | **pass** |
| `integrity_tracks_match_corpus` | **pass** |
| `integrity_ltorso_matches_corpus` | **pass** |
| `integrity_verdict_pass` | **pass** |
| `manifest_val_128` | **pass** |
| `manifest_test_128` | **pass** |
| `manifest_members_256` | **pass** |
| `gate_1r_exact_partition` | **pass** |
| `all_methods_same_case_support` | **pass** |
| `support_equals_total_cases` | **pass** |

The two runs independently reproduce an identical corpus, an identical Gate 1R partition and an identical per-sequence case count, so the halves describe the same evaluation support and are safe to report side by side.

## 10. Limitations

- JTA is SYNTHETIC (GTA-V engine); provenance must be disclosed wherever it appears.
- Clustering is by SCENE (sequence), not by person. The frozen aggregation algebra transfers from the NTU subject-first form, but the cluster semantics do not; the project's subject-clustered bootstrap convention is NOT claimed here.
- Learned models face a structural input shift: 5 of 17 slots (nose, eyes, ears) are permanently NATIVE_INVALID on JTA.
- No confidence channel exists on JTA; confidence is 0 with confidence_available false and is never synthesized.
- Only descriptive per-sequence dispersion is reported. No inferential CI convention is claimed for JTA, because none was frozen.
- The frozen g grid {1,2,3,5,8,10,20} is not extended for JTA; maximal target runs off that grid remain in the applicability statistics but create no evaluation case.
- 58.52 % of primary targets are refused by Gate 1R (no anchor, or leading/trailing extrapolation). Reconstruction error is defined only on the admitted remainder, and that refusal rate is itself a primary applicability result.

## 11. Confirmations

| statement | value |
| --- | --- |
| `no_retraining` | **True** |
| `no_checkpoint_reselection` | **True** |
| `protocol_modified_after_val_test_access` | **False** |
| `train_reconstruction_outcomes` | **0** |
| `train_outcomes_computed` | **False** |
| `train_outcomes_confirmed_false_in_both_runs` | **True** |
| `project_final_test_sealed` | **True** |
| `final_test_seal_evidence` | **the JTA evaluation reads only data/jta/annotations/{val,test}. It resolves no NTU split manifest and loads no project partition, so the reserved final_test partition is untouched by this record. The POST-HOC envelope diagnostic in section 6 additionally read the NTU 'xsub_val' split as a control; xsub_val is not final_test, and that diagnostic contributes no reported outcome.** |
| `videos_downloaded` | **False** |
| `stgcn_run` | **False** |
| `protocol_frozen_before_val_test_access` | **True** |
| `record_50_pushed_before_access` | **True** |

