# FORBIDDEN AND OBSOLETE CLAIMS

Binding. Several entries correct statements that appeared in earlier reports in
this project.

## Corrected errors, do not reintroduce

| forbidden | correct form | basis |
|---|---|---|
| MOT17 deployments add 1,224 to 3,023 rows | each adds 2,072 to 3,023 rows; 1,224 to 2,104 of them are admitted | `B1_mot17_gate_summary.csv`; the 1,224 was ByteTrack's SEMANTICALLY_ADMITTED count, not its synthesized total |
| OC-SORT GPR rewrites 212 rows, 0.4616 % | 52 rows above 1e-6 px; 2,622 at exact float equality | `FINAL_gpr_rewrite_recount.csv`; the 212 figure was a 2-decimal rounding-boundary artifact |
| the GPR rewrite count needs no tolerance | state the 1e-6 px criterion explicitly | exact equality gives 2,622, so an untolerated reproduction disagrees with 52 |
| MOT20 gate-stable non-admission is unavailable | 6,631 / 34,814 = 19.0469 % | Step 9 `C3_gate_stability_summary.csv`; the D1B table omitted it through a code filter |
| GSI independently replicates the DTI ordering effect | all 7 crossings arise at GSI's linear stage; the GP stage adds 0 | D2C |
| two independent mechanisms reproduced the ranking effect | the two operators share a linear interpolation stage | D2C |
| independent interpolation mechanisms | GSI's first stage *is* linear gap filling | D2C |
| 12,767 frozen per-row STV classifications were independently reproduced | population and identities reproduced; frozen agreement is at the sequence-by-class level; no frozen per-row class table exists | Step 9.1 |
| 25 independent sequences | 25 sequences, or 25 sequence-level clusters | D1B.1; independence was never established |
| the GP stage contributes no evaluated-state effect | all 20 metric cells move; median GP share 0.1812, max 0.8722 | D2C |
| the GP stage changes the ordering conclusions | 0 of 30 cells cross zero on that transition | D2C |
| using `S0`, `S1`, `S2` and the frozen `PRE`, `S0`, `S2` interchangeably | the two naming schemes collide; see the naming-collision note below | v5 supplement Sec. S6 against frozen `DECOMPOSITION.json` |
| an R1 analogue exists for the AFLink or GSI stages | withholding added rows changes the fit, so no row-subset intervention exists | frozen `states.py` field `r1_status_for_non_row_additive` |

## Never mix a class count with a total or a denominator

The four STV classes are a partition of the synthesized set. A class count is
therefore never the synthesized total, never the added-row count, and never a
denominator for a non-admission percentage. The one error found in this packet
came from exactly that substitution.

Before writing any range, name the quantity and check both endpoints come from
the same column of the same artifact. On MOT17 the four columns give four
different ranges:

| quantity | range | column in `B1_mot17_gate_summary.csv` |
|---|---|---|
| synthesized rows per deployment | 2,072 to 3,023 | `n_synthesized` |
| ANCHOR_UNMATCHED | 408 to 1,266 | `n_unmatched` |
| ANCHOR_ID_MISMATCH | 216 to 375 | `n_id_mismatch` |
| SEMANTICALLY_ADMITTED | 1,224 to 2,104 | `n_admitted` |
| non-admitted | 783 to 1,482 | `n_nonadmitted` |

TARGET_REFERENCE_ABSENT is 0 for every MOT17 deployment, so it has no range.

## Naming collision, StrongSORT++ states

This is a labelling hazard, not a numerical disagreement. The counts agree
exactly between v5 and the frozen artifact.

| v5 supplement Sec. S6 | frozen `DECOMPOSITION.json` | rows | what it is |
|---|---|---|---|
| `S0` | `PRE` | 46,914 | base tracker output |
| `S1` | `S0` | 46,913 | post-AFLink |
| `S2` | `S2` | 50,097 | post-GSI |

v6 must pick one scheme and say which. Recommended: keep the frozen artifact's
`PRE` / `S0` / `S2`, because the artifacts and the released `states.py` use it and
because `S1` invites the reader to expect an R1-style withheld-row state, which
does not exist for this transition. If v6 instead keeps v5's `S0` / `S1` / `S2`,
every cross-reference to an artifact must be relabelled, and Table S6's
`$S_2 - S_1$` row must be read as post-GSI minus post-AFLink in both schemes.

Either way, state explicitly that the base tracker output was written but not
scored, so the AFLink comparison is structural only.

## Independence and statistics

| forbidden | why |
|---|---|
| 5/50 independent changes, 7/30 independent changes, 30 independent comparisons, n=30 independent confirmations | the matrices are exhaustive and dependent: pairs are formed from a small tracker set so each tracker appears in several pairs and margins share pooled scores, and DetA and AssA are factors of HOTA |
| 7/30 as a binomial success rate | same |
| p-values derived from P(sign differs) | it is a bootstrap frequency; no null hypothesis is tested |
| statistically significant, family-wise significance | no test was performed |
| robust ranking reversal, robust ranking instability | no robustness criterion was pre-specified; report full precision, 3-decimal survival, 2-decimal survival and bootstrap support as four separate facts |
| the percentile intervals are significance tests | they are descriptive |

## Evidence category

| forbidden | why |
|---|---|
| DanceTrack reproduces released post-processing practice | the operator is ours; no released DanceTrack submission is audited |
| replication of StrongSORT++ on DanceTrack | no such deployment exists in the audited source |
| released DanceTrack GSI practice | upstream StrongSORT has no DanceTrack entry in `opts.py` at all |
| confirmatory second experiment, pre-specified GSI arm | the GSI arm was designed after the DTI outcomes were known |
| independent confirmation | it implies the second operator was planned before the first arm's outcomes |
| the DanceTrack ByteTrack arm is the same deployment audited on MOT17 | it uses the DanceTrack repository overlay, not the audited commit |

## Interpretation of admission

| forbidden | why |
|---|---|
| non-admitted rows are false positives | non-admission means absence of reference support under a stated criterion |
| non-admitted means geometrically implausible | 62.0388 to 73.5409 % of non-admitted DanceTrack rows reach maximum IoU at or above 0.5 |
| REFERENCE_ABSENT rows have no nearby ground-truth geometry | 3,448 of 3,451 have another identity overlapping the box |
| the added rows are errors | the audit measures composition and reference support, not correctness |
| admitted rows always have strong local geometric support | 1.7849 to 2.6080 % of admitted rows fall below IoU 0.5 |
| causal contribution of GSI rewritten rows | the operator admits no row-subset intervention |
| higher non-admission causes lower metrics | a four-tracker ordering coincidence, no inferential weight |

## Provenance

| forbidden | why |
|---|---|
| all DanceTrack checkpoints are fully held out | training-split disjointness holds, but Deep-OC-SORT's checkpoint selection and all four trackers' hyperparameter selection are UNRESOLVED |
| Deep-OC-SORT is ineligible | it is included; the three-tracker table is a checkpoint-selection-provenance sensitivity subset |
| a single held-out label covering training data and selection | keep TRAINING_SPLIT_DISJOINT and SELECTION_PROVENANCE as separate fields |

## Scope

| forbidden | why |
|---|---|
| breadth is closed | explicitly disallowed |
| universal generalisation is established | two populations, one operator family plus one rewrite-heavy operator, four controlled trackers |
| the effect universally generalises | same |
| rewriting the evaluated state implies a benchmark effect | the GPR case rewrites 52 rows and moves all five metrics by 0.0000 |
