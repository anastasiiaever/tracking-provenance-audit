import os, csv
V="<AUDIT_ROOT>/V6_SOURCE_OF_TRUTH"
def w(n,s): open(os.path.join(V,n),"w").write(s.lstrip("\n")); print("  wrote",n)
def wc(n,hdr,rows):
    with open(os.path.join(V,n),"w",newline="") as f:
        x=csv.writer(f); x.writerow(hdr); x.writerows(rows)
    print(f"  wrote {n} ({len(rows)} rows)")

H=["claim_id","v6_section","claim","evidence_type","authoritative_artifact",
   "ledger_ids","status","v5_status","guardrail"]
R=[]
def C(cid,sec,claim,et,art,lids,st="VERIFIED",v5="NEW",g=""):
    R.append([cid,sec,claim,et,art,lids,st,v5,g])

# framework
C("F1","3.1","A benchmark score characterises an evaluated output state, not a tracker in isolation.",
  "DEFINITIONAL","07_METHOD_DEFINITIONS.md Sec. 1","","DEFINITION","IN_V5",
  "not an empirical claim; do not cite an artifact for it")
C("F2","3.1","The submitted file of several widely used trackers contains rows added by offline post-processing.",
  "RELEASED_DEPLOYMENT_AUDIT","Step 9 A3_primary_replay_rows.csv; v5 Table 1","M17-SYNTH-TOTAL","VERIFIED","IN_V5")
C("F3","3.4","Which audit is available is determined by the transition structure, not chosen by the auditor.",
  "STRUCTURAL","frozen states.py r1_status_for_non_row_additive; DECOMPOSITION.json","","VERIFIED","IN_V5_SUPPLEMENT",
  "promote to the main text with Table T2")
C("F4","3.2","Scoreable-target admission is a reference-side diagnostic; the synthesized row's coordinates do not enter the predicate.",
  "DEFINITIONAL","07_METHOD_DEFINITIONS.md Sec. 7","","DEFINITION","PARTIALLY_IN_V5",
  "must be stated in the Method, not deferred to the Discussion")
# MOT17
C("A1","5.1","Five released MOT17 deployments add rows failing admission in 28.92 to 49.02 % of the added set at gate 0.50.",
  "RELEASED_DEPLOYMENT_AUDIT","posthoc_composition_20261003/results/B1_mot17_gate_summary.csv","M17-NA-RANGE","VERIFIED","IN_V5")
C("A2","5.1","Gate-stable non-admission is 23.45 to 43.90 %.",
  "RELEASED_DEPLOYMENT_AUDIT","results/C3_gate_stability_summary.csv","M17-GS-RANGE","VERIFIED","IN_V5")
C("A3","5.1","TARGET_REFERENCE_ABSENT is empty for every MOT17 deployment at every gate.",
  "RELEASED_DEPLOYMENT_AUDIT","results/B1 and C3","M17-ABS-ALL","VERIFIED","IN_V5",
  "pair with the DanceTrack contrast; the cause is the reference, not the tracker")
C("A4","5.2","All 25 MOT17 metric deltas from R0 to R2 are positive.",
  "RELEASED_DEPLOYMENT_AUDIT","results/D1_bootstrap_summary.json point_estimates","M17-DELTAS","VERIFIED","IN_V5")
C("A5","5.3","5 of 50 exhaustive pairwise metric cells cross zero; all five survive 3dp and 2dp reporting.",
  "RELEASED_DEPLOYMENT_AUDIT","FINAL_unified_pairwise_margins.csv","M17-CROSS,M17-CROSS-3DP,M17-CROSS-2DP","VERIFIED","IN_V5",
  "exhaustive and dependent; never a rate or a p-value")
C("A6","5.3","Crossing cells had initial absolute margins 0.5104 to 1.4567, and 17 of 45 unchanged cells were at or below that.",
  "RELEASED_DEPLOYMENT_AUDIT","FINAL_unified_pairwise_margins.csv","M17-CROSS-MARGIN,M17-UNCH-BELOW,M17-UNCH-MIN","VERIFIED","IN_V5")
C("A7","7","Re-execution reconstructed the 12,767-row population with unique identities and reproduced 105 of 105 MOT17 and 130 of 130 total frozen sequence-by-class counts.",
  "RE_EXECUTION","step9_1/STEP9_REPORT_CORRECTIONS.md","M17-SYNTH-TOTAL,M17-REPLAY","VERIFIED","CORRECTS_V5",
  "v5's per-row phrasing is an overstatement and must be corrected")
# MOT20
C("B1","5.4","Of seven pre-specified MOT20 configurations, 1 is eligible, 5 fail on detector-training overlap, 1 is unresolved.",
  "ELIGIBILITY_CENSUS","v5 supplement Sec. S7","M20-CELLS,M20-ELIG,M20-OVERLAP,M20-UNRES","VERIFIED","IN_V5")
C("B2","5.4","The eligible deployment adds 34,814 rows; non-admission is 25.1364 % at gate 0.50.",
  "RELEASED_DEPLOYMENT_AUDIT","results/B2_mot20_gate_summary.csv","M20-SYNTH,M20-NAPCT","VERIFIED","IN_V5")
C("B3","5.4","Its gate-stable non-admission is 6,631 of 34,814, 19.046935 %.",
  "RELEASED_DEPLOYMENT_AUDIT","results/C3_gate_stability_summary.csv","M20-GS,M20-GSPCT","VERIFIED","IN_V5",
  "omitted from an intermediate report by a population filter; must appear in v6")
C("B4","5.4","MOT20 supports a composition check and no ordering analysis.",
  "STRUCTURAL","06_EVIDENCE_ARCHITECTURE.csv","","VERIFIED","IN_V5",
  "one deployment yields no pair")
# DanceTrack DTI
C("C1","6.1","Under one common operator applied by us with n_min=25 and n_dti=20, non-admission is 42.03 to 68.46 % across four trackers.",
  "CONTROLLED_COMMON_OPERATOR","D1B_stv_primary.csv","DTI-NA-RANGE","VERIFIED","NEW")
C("C2","6.1","Gate-stable non-admission is 38.05 to 62.62 %.",
  "CONTROLLED_COMMON_OPERATOR","D1B_gate_persistence_summary.csv","DTI-GS-RANGE","VERIFIED","NEW")
C("C3","6.1","The operator adds 3.79 to 6.93 % of the submitted rows.",
  "CONTROLLED_COMMON_OPERATOR","D1B_state_inventory.csv","DTI-INS-RANGE","VERIFIED","NEW")
C("C4","6.2","12 of 20 metric deltas are positive and 8 negative; OC-SORT and Deep-OC-SORT rise on all five metrics, ByteTrack and Hybrid-SORT fall on four of five and rise only on AssA.",
  "CONTROLLED_COMMON_OPERATOR","D1B_metric_deltas_primary.csv","DTI-DELTAS","VERIFIED","NEW",
  "the key contrast with the all-positive MOT17 arm")
C("C5","6.2","Substantial non-admission occurs whether the common operator improves or degrades the reported metrics.",
  "CONTROLLED_COMMON_OPERATOR","D1B_stv_primary.csv with D1B_metric_deltas_primary.csv","DTI-NA-RANGE,DTI-DELTAS","VERIFIED","NEW",
  "descriptive co-occurrence, not a causal claim")
C("C6","6.3","7 of 30 exhaustive pairwise cells cross zero; all survive 3dp and 2dp.",
  "CONTROLLED_COMMON_OPERATOR","D1B1_pairwise_30cells_recomputed.csv; D1B1_flip_precision_audit.csv","DTI-CROSS,DTI-CROSS-3DP,DTI-CROSS-2DP","VERIFIED","NEW")
C("C7","6.3","The composition-to-ordering association seen on MOT17 does not replicate: the tracker with the highest non-admission appears in the fewest crossing cells.",
  "CONTROLLED_COMMON_OPERATOR","FINAL_unified_pairwise_margins.csv with D1B_stv_primary.csv","DTI-CROSS-APPEAR,DTI-NAPCT","VERIFIED","CONTRADICTS_V5_READING",
  "v5's Discussion offered the MOT17 association; v6 must report the non-replication")
C("C8","6.1","The composition conclusion does not depend on n_min 25 against 30: at most 0.42 points of non-admission and 0.0422 metric points.",
  "CONTROLLED_COMMON_OPERATOR","D1B_stv_sens30_primary_gate.csv; D1B_dti_parameter_sensitivity.csv","DTI-SENS-NA,DTI-SENS-MET","VERIFIED","NEW")
C("C9","4.2","Training-split disjointness holds for all four DanceTrack trackers; selection provenance is unresolved for Deep-OC-SORT's checkpoint and for all four at the hyperparameter level.",
  "PROVENANCE_AUDIT","D1B_training_selection_provenance.csv","","VERIFIED","NEW",
  "keep the two fields separate; never a single held-out label")
C("C10","6.3","Dropping the tracker with unresolved checkpoint provenance leaves 3 of 15 cells crossing zero under both operators.",
  "CONTROLLED_COMMON_OPERATOR","FINAL_three_tracker_provenance_sensitivity.csv","DTI-3T-CROSS,GSI-3T-CROSS","VERIFIED","NEW",
  "a sensitivity subset, not an exclusion")
# REFERENCE_ABSENT
C("D1","6.4","TARGET_REFERENCE_ABSENT is non-empty on DanceTrack and empty on MOT17 and MOT20.",
  "CONTROLLED_COMMON_OPERATOR","D1B_stv_primary.csv against results/B1 and B2","DT-ABS-TOTAL,M17-ABS-ALL,M20-ABS","VERIFIED","NEW")
C("D2","6.4","All 16,019 such rows across four trackers and five gates lie strictly inside a gap in the ground-truth track's own observed frame set.",
  "MECHANISM_AUDIT","D1B1_reference_absent_audit.json","DT-ABS-ALLGATES,DT-ABS-INGAP","VERIFIED","NEW")
C("D3","6.4","DanceTrack's scoreable ground truth has 1,370 interior gaps over 209 of 273 tracks; MOT17's has none over 339.",
  "MECHANISM_AUDIT","final_defense_20261004 report Part II; corroborated by Frag=1370","DT-GTGAPS,DT-GTGAPPED,M17-GTGAP","VERIFIED","NEW")
C("D4","6.4","An independently written predicate agreed with the frozen classifier on 250,470 of 250,470 decisions.",
  "RE_EXECUTION","D1B1_reference_absent_audit.json","DT-ABS-AGREE","VERIFIED","NEW")
C("D5","6.4","The class records that the anchor-resolved reference identity is absent at that frame; it is not a tracker error and not a false-positive label.",
  "DEFINITIONAL","07_METHOD_DEFINITIONS.md Sec. 7","","DEFINITION","NEW")
# row-local
C("E1","6.5","Admitted rows reach maximum IoU >= 0.5 in 97.39 to 98.22 % of cases, and 1.78 to 2.61 % fall below.",
  "CONTROLLED_COMMON_OPERATOR","D1B2_row_local_support.csv","DT-RL-ADM-RANGE,DT-RL-ADM-BELOW","VERIFIED","NEW",
  "report both directions")
C("E2","6.5","62.04 to 73.54 % of non-admitted rows overlap some scoreable ground truth at maximum IoU >= 0.5, so non-admission is not geometric implausibility.",
  "CONTROLLED_COMMON_OPERATOR","D1B2_row_local_support.csv","DT-RL-NA-RANGE","VERIFIED","NEW")
C("E3","6.5","For REFERENCE_ABSENT rows the intended identity is absent in all 3,451 cases while another identity overlaps in 3,448.",
  "CONTROLLED_COMMON_OPERATOR","D1B2_reference_absent_local_support.csv","DT-ABS-INTENDED,DT-ABS-OTHERGT","VERIFIED","NEW")
# GSI
C("G1","6.6","GSI is key-additive but content-rewriting: 0 deletions and 56.84 to 67.47 % of surviving coordinates rewritten.",
  "CONTROLLED_COMMON_OPERATOR","D2B_state_inventory.csv","GSI-DEL,GSI-RW-RANGE","VERIFIED","NEW")
C("G2","6.6","Its metric split is 12 positive and 8 negative and 7 of 30 cells cross zero, the same pair-and-metric identities as the DTI arm.",
  "CONTROLLED_COMMON_OPERATOR","D2B_metric_deltas.csv; D2B_pairwise_30cells.csv","GSI-DELTAS,GSI-CROSS,XARM-CROSS-ID","VERIFIED","NEW")
C("G3","6.6","Decomposed, R0 to L_GSI is strictly row-additive and carries 7 of 30 crossings; L_GSI to GSI rewrites coordinates only and carries 0 of 30.",
  "CONTROLLED_COMMON_OPERATOR","D2C_three_state_pairwise_margins.csv","D2C-LIN-CROSS,D2C-GP-CROSS,D2C-TOT-CROSS","VERIFIED","SUPERSEDES_D2B_READING",
  "therefore GSI is NOT an independent second mechanism")
C("G4","6.6","The GP stage does change the evaluated state: all 20 metric cells move, median share 0.181, opposing the linear stage in 8 of 20.",
  "CONTROLLED_COMMON_OPERATOR","D2C_three_state_metrics.csv","D2C-GP-SHARE,D2C-GP-SHARE-RANGE,D2C-GP-OPPOSE","VERIFIED","NEW",
  "report alongside the 0 of 30; either half alone misleads")
C("G5","6.6","Neither STV nor an R1 analogue is defined for this transition.",
  "STRUCTURAL","frozen states.py; GSI_PROTOCOL_LOCK.md Sec. 5","","VERIFIED","NEW")
# GPR
C("H1","5.5","OC-SORT's GPR stage inserts and deletes nothing: 45,927 rows in both states.",
  "RELEASED_DEPLOYMENT_AUDIT","FINAL_gpr_rewrite_recount.csv","GPR-G0,GPR-G2,GPR-INS,GPR-DEL","VERIFIED","IN_V5")
C("H2","5.5","52 rows change by more than 1e-6 px; 2,622 differ at exact float equality in x and y only, by 8.9e-12 to 1.7e-05 px; w and h are bit-identical.",
  "RELEASED_DEPLOYMENT_AUDIT","FINAL_gpr_rewrite_recount.csv","GPR-RW-TOL,GPR-RW-EXACT,GPR-RW-WH,GPR-RW-MAX","VERIFIED","EXTENDS_V5",
  "always state the tolerance; the 212 figure was a rounding-boundary artifact")
C("H3","5.5","All five reported metrics change by 0.0000; the 3dp summary is byte-identical and the detailed output differs in 197 LocA-family fields.",
  "RELEASED_DEPLOYMENT_AUDIT","FINAL_gpr_rewrite_recount.csv","GPR-METRIC,GPR-DETAILED","VERIFIED","IN_V5")
C("H4","8","An operator can rewrite the evaluated state and move no reported metric, so state change is necessary and not sufficient for a score effect.",
  "RELEASED_DEPLOYMENT_AUDIT","FINAL_gpr_rewrite_recount.csv","GPR-RW-TOL,GPR-METRIC","VERIFIED","NEW_FRAMING",
  "this is the claim the boundary case exists to support")
# StrongSORT
C("I1","5.5","AFLink changes 1,316 row identities across 29 remappings, reduces identities from 435 to 406, and loses one row.",
  "RELEASED_DEPLOYMENT_AUDIT","frozen strongsort/DECOMPOSITION.json","SS-IDCHG,SS-REMAP,SS-IDS-PRE,SS-IDS-S0","VERIFIED","IN_V5")
C("I2","5.5","GSI then adds 3,184 rows, drops none, and rewrites 46,866 of 46,913 surviving coordinates, 99.8998 %.",
  "RELEASED_DEPLOYMENT_AUDIT","frozen strongsort/DECOMPOSITION.json","SS-ADD,SS-RW,SS-RWPCT","VERIFIED","IN_V5")
C("I3","5.5","Containment of the pre-GSI state holds on identity keys and fails on row content; no R1 analogue exists.",
  "STRUCTURAL","DECOMPOSITION.json nesting_claim and stv_state fields","","VERIFIED","IN_V5",
  "mind the v5 state-naming collision")
# scope
C("J1","9","The principal single-population limitation is substantially reduced.",
  "SCOPE","06_EVIDENCE_ARCHITECTURE.csv","M17-CELLS,DTI-CELLS,GSI-CROSS","VERIFIED","CHANGES_V5_STATUS",
  "this exact wording; never 'breadth is closed'")
C("J2","9","The DanceTrack arms characterise a common operator applied by us, not any author's released DanceTrack practice.",
  "SCOPE","D1B and GSI protocol locks","","VERIFIED","NEW",
  "state in the introduction as well as the limitations")
wc("26_CLAIM_TO_ARTIFACT_MAP.csv",H,R)

w("27_V6_BUILD_GUARDRAILS.md", r"""
# V6 BUILD GUARDRAILS

Binding on anyone writing v6, including a model. Read this file,
`04_FORBIDDEN_OR_OBSOLETE_CLAIMS.md` and `30_UNSLOPPING_RULES_FOR_CODEX.md`
before writing a sentence.

## 1. Precedence

`01_ARTIFACT_PRECEDENCE.md` is the only tie-breaker. A later-dated artifact with
a verified manifest beats an earlier one. A correction record beats the report it
corrects. A filename containing FINAL proves nothing.

When two sources disagree and the precedence rule does not settle it, do not pick
one. Write `[CONTRADICTION]` with both values and both paths, and stop.

## 2. Numbers

- Every number in v6 comes from `05_NUMERIC_LEDGER.csv`. Nothing is retyped from
  prose, not even this directory's own prose.
- A number not in the ledger is written `[FACT NEEDED]`. Do not estimate, do not
  interpolate, do not derive a percentage from two other percentages.
- Report at the precision the ledger gives. If the main text rounds, the
  supplement must carry the full precision so the figure stays checkable.
- Counts and percentages with different denominators never share a column or a
  sentence without their denominators named.
- Every tolerance-dependent count carries its tolerance. The GPR 52 is the
  standing example.

## 3. Claims

- Only claims in `03_ALLOWED_CLAIMS.md` may be asserted.
- Claims in `04_FORBIDDEN_OR_OBSOLETE_CLAIMS.md` may not appear, in any
  paraphrase. Paraphrase does not launder a forbidden claim: "replicated
  independently" is forbidden for the GSI arm whatever words carry it.
- Each claim's section, artifact and ledger ids are in
  `26_CLAIM_TO_ARTIFACT_MAP.csv`.

## 4. Statistics

- No p-values. No "significant". No "robust" in a technical sense.
- No multiplicity correction, and no sentence implying one was needed and
  omitted.
- Crossing counts are counts out of an exhaustive dependent matrix. Never a rate,
  never a trial, never a binomial.
- `P(sign differs)` is a bootstrap frequency. Say so where it first appears.
- Percentile intervals are descriptive.
- "25 sequence-level clusters", never "25 independent sequences".

## 5. Evidence category

Every result carries its category, and the categories do not blur:

| category | arms |
|---|---|
| released-deployment audit | MOT17 five deployments; MOT20 eligible cell; OC-SORT GPR; StrongSORT++ |
| controlled intervention, operator applied by us | DanceTrack DTI and GSI |
| pre-specified | everything except the GSI arm |
| post-hoc | the GSI arm and its decomposition |

Do not describe a controlled arm as released practice, and do not describe the
post-hoc arm as confirmatory.

## 6. Interpretation

- Non-admission is reference-side. It is not error, not false positive, not
  implausibility.
- No causal language from composition to metric change, in either direction.
- State change does not imply score change. The GPR case is the counterexample
  and should be cited wherever the temptation arises.
- Do not claim breadth is closed. The allowed sentence is that the principal
  single-population limitation is substantially reduced.

## 7. Reuse

- v5 is frozen. Copy from it; never edit it. Hashes are in
  `09_PROVENANCE_LEDGER.csv`.
- Reuse decisions are in `13_V5_REUSE_MAP.md`, including the one required
  correction to v5's Verification section and the bibliography-file trap.
- Re-point every `\ref` and `\label` carried over from v5. v5's `sec:results`
  belongs to the removed section and must not be reused for v6's new Sec. 6.

## 8. Writing

- Style precedence and the full rule set are in
  `28_WRITING_STYLE_REFERENCE.md`, `29_WSOL_STYLE_OBSERVATIONS.md` and
  `30_UNSLOPPING_RULES_FOR_CODEX.md`. The style files govern wording only and
  carry no scientific authority.
- Terminology is frozen. `R0`, `R1`, `R2`, `ANCHOR_UNMATCHED`,
  `ANCHOR_ID_MISMATCH`, `TARGET_REFERENCE_ABSENT`, `SEMANTICALLY_ADMITTED`,
  `scoreable-target admission`, `gate-stable`, `row-additive`,
  `key-additive but content-rewriting`, `rewrite-only`, `evaluated state`,
  `estimand eligibility`. Do not vary these for readability.
- State the thesis once. Do not restate the contribution set at the head of each
  results section, and do not end sections with summaries of themselves.
- Do not even out section lengths. Sec. 6 is the new contribution and should be
  the longest.

## 9. Stop conditions

Stop writing and report, rather than working around, if any of these occurs:

1. A required number is absent from the ledger and absent from every artifact.
2. Two authoritative artifacts disagree and precedence does not resolve it.
3. A claim needed for the argument is in the forbidden list.
4. A manifest fails verification.
5. An artifact referenced by this directory is missing from disk.

## 10. What this directory does not authorise

No new experiments. No new datasets, trackers, operator families or parameter
searches. No modification of v5, of the public repository, or of any frozen
experimental artifact. The experimental expansion is closed.

If writing v6 appears to require a new measurement, that is a stop condition
under item 1, not a licence.
""")
