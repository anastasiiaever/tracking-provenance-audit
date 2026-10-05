# Record 56 — PoseTrack21 VAL Segmentation Sensitivity (SUPPLEMENTARY)

**Date:** 2026-08-22 · **Status:** `SUPPLEMENTARY — DOWNSTREAM OF THE FROZEN PROSPECTIVE RESULT` · **Annotation-only**

Supplementary analysis **downstream of the frozen prospective result**, record 54 (`60ded1973568045735394263073c47119552cae1`), executed under v3.2 §6.B (`26f66ee11113963d02863f2bf3b04cf07846538e`). No reconstruction method and no model was run. **The frozen 8.88 % is not replaced.**

## 1. Rules compared (no fourth rule invented)

| rule | definition |
| --- | --- |
| **A** | A — bridged |
| **B'** | B' — contiguous |
| **B** | B — strict contiguous + native-missing breaks (FROZEN PRIMARY) |

## 2. Internal validation

- scoreable occluded targets invariant across all three rules: **True** at **78,194**
- visibility semantics are S3 in all three rules, so the set of scoreable occluded targets cannot change; only the Gate 1R partition may move. The invariance is asserted in code, not assumed.
- exact Gate 1R partition under all three rules: **True**

Variant B reproduces record 54 exactly:

| check | result |
| --- | --- |
| `variant_B_reproduces_record_54_eligible_count` | **True** |
| `variant_B_reproduces_record_54_eligible_pct` | **True** |
| `variant_B_reproduces_record_54_partition` | **True** |
| `variant_B_reproduces_record_54_target_count` | **True** |
| `variant_B_g_support_matches_record_52_prenormalization_audit` | **True** |
| `variant_B_g_support_intentionally_exceeds_record_54_evaluated_counts` | **True** |

## 3. Applicability under each rule

| quantity | A — bridged | B' — contiguous | **B — frozen primary** |
| --- | ---: | ---: | ---: |
| scoreable occluded targets | 78,194 | 78,194 | 78,194 |
| Gate 1R eligible | 28,487 | 8,214 | 6,942 |
| leading-ineligible | 12,424 | 8,199 | 8,173 |
| trailing-ineligible | 14,616 | 8,511 | 8,729 |
| no-anchor | 22,667 | 53,270 | 54,350 |
| **eligible %** | **36.43 %** | **10.50 %** | **8.88 %** |
| ineligible % | 63.57 % | 89.50 % | 91.12 % |
| exact partition | True | True | True |

### Support by gap length — cases / independent VAL sequences / meets the frozen 30

| rule | g=1 | g=2 | g=3 | g=5 | g=8 | g=10 | g=20 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **A** cases | 4,147 | 1,514 | 778 | 299 | 127 | 71 | 17 |
| A sequences | 155 | 138 | 120 | 98 | 62 | 43 | 16 |
| A meets 30 | **yes** | **yes** | **yes** | **yes** | **yes** | **yes** | no |
| **B'** cases | 1,119 | 474 | 273 | 103 | 49 | 23 | 4 |
| B' sequences | 121 | 96 | 85 | 58 | 32 | 16 | 4 |
| B' meets 30 | **yes** | **yes** | **yes** | **yes** | **yes** | no | no |
| **B** cases | 773 | 365 | 229 | 85 | 44 | 23 | 4 |
| B sequences | 117 | 86 | 77 | 52 | 29 | 16 | 4 |
| B meets 30 | **yes** | **yes** | **yes** | **yes** | no | no | no |

| rule | primary grid selected by the frozen threshold |
| --- | --- |
| A | {1,2,3,5,8,10} |
| B' | {1,2,3,5,8} |
| B | {1,2,3,5} |

## 4. Conclusions

### Robustness of the qualitative conclusion

The qualitative conclusion is ROBUST. Under every one of the three segmentation rules, a clear majority of scoreable occluded targets do not define a valid interpolation problem: 63.57 % ineligible under the most permissive rule (A, bridged), 89.50 % under B', and 91.12 % under the frozen primary rule B. The claim that nominal occlusion does not imply a well-posed reconstruction problem does not depend on the choice of rule.

### Sensitivity of the absolute prevalence

The ABSOLUTE prevalence is SENSITIVE and moves materially. The eligible fraction ranges from 8.88 % to 36.43 % on the SAME 170 VAL sequences — a spread of 27.55 percentage points and a factor of 4.10 — driven solely by the segmentation definition, with no change to the data, the visibility semantics or the joint set. The headline 8.88 % is therefore a property of the population MEASURED UNDER THE FROZEN STRICT RULE, not a transferable constant. This is exactly the population- and protocol-dependence that v3.2 §2.3 requires to be stated wherever an eligible rate is reported.

*Descriptively, the movement is concentrated in the no-anchor category: 22,667 under A against 54,350 under B. Bridging annotation holes lets distant observations act as anchors for targets that the strict rule leaves anchorless. That is a description of what the counts do, not a claim about which rule is correct.*

**Threshold interaction.** The frozen 30-independent-sequence threshold selects a different primary grid under each rule: [1, 2, 3, 5, 8, 10] under A, [1, 2, 3, 5, 8] under B', and [1, 2, 3, 5] under the frozen rule B. The frozen primary grid {1,2,3,5} is the strictest of the three. No threshold is changed here.

**Primary result unchanged.** The primary scientific result remains variant B. The frozen 8.88 % is NOT replaced; this record quantifies how much it would move under the other two audited definitions.

## 5. Caveats

- annotation-only: no reconstruction method and no model was run for this analysis
- the three rules are the ones already audited in record 52; no fourth rule was invented
- variant A bridges annotation holes, which the project's frozen segmentation convention rejects; it is included as a bound, not as a candidate protocol
- support counts here are PRE-NORMALIZATION and are therefore deliberately larger than record 54's evaluated counts. They match the record-52 VAL audit exactly (773/365/229/85/44/23/4 at g=1,2,3,5,8,10,20, total 1,523) because neither applies the L_torso admissibility rule; record 54 applies it and evaluates 1,270 cases. The counts are comparable ACROSS RULES, which is this record's purpose, and are not a restatement of record 54's support

## 6. Confirmations

| statement | value |
| --- | --- |
| `reconstruction_performed` | **False** |
| `model_prediction_performed` | **False** |
| `record_53_modified` | **False** |
| `record_54_modified` | **False** |
| `frozen_8_88_percent_replaced` | **False** |
| `fourth_rule_invented` | **False** |
| `threshold_changed` | **False** |
| `training_performed` | **False** |
| `project_final_test_opened` | **False** |
| `record_56_committed` | **False** |

