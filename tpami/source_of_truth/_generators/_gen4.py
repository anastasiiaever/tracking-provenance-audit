import os, csv, hashlib
V="<AUDIT_ROOT>/V6_SOURCE_OF_TRUTH"
B="<AUDIT_ROOT>"
D=B+"/dancetrack_controlled_20261003"
def w(n,s): open(os.path.join(V,n),"w").write(s.lstrip("\n")); print("  wrote",n)
def wc(n,hdr,rows):
    with open(os.path.join(V,n),"w",newline="") as f:
        x=csv.writer(f); x.writerow(hdr); x.writerows(rows)
    print(f"  wrote {n} ({len(rows)} rows)")
def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda: f.read(1<<20), b""): h.update(b)
    return h.hexdigest()

w("03_ALLOWED_CLAIMS.md", r"""
# ALLOWED CLAIMS

Each entry is supported by the artifact named in `26_CLAIM_TO_ARTIFACT_MAP.csv`.
Wording here is indicative, not final prose.

## Framework

- A benchmark score characterises an evaluated output state, not a tracker in
  isolation.
- The submitted file of several widely used trackers contains both tracker output
  and rows added by offline post-processing.
- Which audit is available depends on the structural transition. A row-additive
  transition admits a row-level admission decomposition; a transition that
  rewrites surviving rows does not.
- Scoreable-target admission is a reference-side diagnostic. It asks whether an
  added row has reference support under a stated criterion.

## MOT17, released-deployment audit

- Five released deployments on one validation population each add rows that fail
  admission, with primary-gate non-admission from 28.92 to 49.02 % and
  gate-stable non-admission from 23.45 to 43.90 %.
- All 25 metric deltas are positive.
- 5 of 50 exhaustive pairwise metric cells cross zero, and all five survive
  3-decimal and 2-decimal score reporting.
- TARGET_REFERENCE_ABSENT is empty for every MOT17 deployment.
- Re-execution reconstructed the same 12,767-row synthesized population with all
  12,767 identities unique and reproduced every available frozen
  sequence-by-class count, 105 of 105 for MOT17 and 130 of 130 including MOT20.

## MOT20

- Of seven configurations pre-specified before any MOT17 execution, one is
  eligible for the held-out comparison, five fail through detector-training
  overlap and one is unresolved.
- The eligible deployment adds 34,814 rows; primary-gate non-admission is
  25.1364 % and gate-stable non-admission is 19.046935 %.
- One deployment permits a composition check on a second population but no
  pairwise ordering analysis.

## DanceTrack, controlled DTI

- Under one common operator applied by us, with `n_min=25` and `n_dti=20`
  identical for four trackers, primary-gate non-admission is 42.03 to 68.46 %
  and gate-stable non-admission 38.05 to 62.62 %.
- The operator adds 3.79 to 6.93 % of output rows.
- 12 of 20 metric deltas are positive, 8 negative. OC-SORT and Deep-OC-SORT rise
  on all five metrics; ByteTrack and Hybrid-SORT fall on four of five and rise
  only on AssA.
- The controlled DanceTrack intervention shows that substantial non-admission can
  occur whether the common post-processing operator improves or degrades the
  reported metrics.
- 7 of 30 exhaustive pairwise metric cells cross zero, all surviving 3-decimal
  and 2-decimal reporting.
- The composition conclusion does not depend on `n_min` 25 against 30:
  non-admission differs by at most 0.42 percentage points.
- Training-split disjointness holds for all four trackers.

## DanceTrack, TARGET_REFERENCE_ABSENT

- The class is non-empty on DanceTrack and empty on MOT17 and MOT20.
- Every such row lies strictly inside a gap in the ground-truth track's own
  observed frame set. DanceTrack's scoreable ground truth is fragmented: 209 of
  273 tracks have at least one interior gap, 1,370 gaps in total; MOT17's has
  none.
- The class records that the anchor-resolved reference identity is absent at that
  frame. It is not a tracker error and not a false-positive label.

## DanceTrack, row-local geometric support

- Admission is defined through the anchors and the availability of the
  anchor-resolved reference identity; the synthesized row's own coordinates are
  not part of the predicate.
- Admitted rows reach maximum IoU at or above 0.5 in 97.39 to 98.22 % of cases,
  not 100 %.
- 62.04 to 73.54 % of non-admitted rows overlap some scoreable ground truth at
  maximum IoU at or above 0.5.
- For TARGET_REFERENCE_ABSENT rows, the intended reference identity is absent in
  all 3,451 cases while another ground-truth identity overlaps the box in 3,448
  of them. The two statements are not equivalent.

## DanceTrack, controlled GSI

- GSI applied to the same four frozen states is key-additive but
  content-rewriting: 0 deletions, and 56.84 to 67.47 % of surviving coordinates
  rewritten.
- Its metric-delta split and its 7-of-30 crossing count match the DTI arm, and
  the seven cells are the same pair-and-metric identities.
- GSI changes the evaluated state through extensive coordinate rewriting in
  addition to interpolation, while the observed ordering crossings are already
  established by its interpolation stage.
- Decomposed: R0 to L_GSI is strictly row-additive and carries 7 of 30 crossings;
  L_GSI to GSI rewrites coordinates only and carries 0 of 30.
- The Gaussian-process stage does produce evaluated-state change: all 20 metric
  cells move, median share of absolute movement 0.181, and in 8 of 20 cells it
  opposes the linear stage.
- STV and an R1 analogue are not defined for this transition.

## OC-SORT GPR boundary case

- G0 and G2 both contain 45,927 rows with zero insertions and zero deletions.
- 52 rows change by more than 1e-6 px; 2,622 rows differ at exact floating-point
  equality, in x and y only, by magnitudes from 8.9e-12 to 1.7e-05 px; w and h
  are bit-identical everywhere.
- The three-decimal summary file is byte-identical between the two states while
  the full-precision detailed output differs in 197 LocA-family fields.
- An operator can rewrite the evaluated state and move no reported metric.

## StrongSORT++ AFLink and GSI structural case

- AFLink changes the identity of 1,316 rows across 29 remappings and loses one
  row, from 46,914 to 46,913.
- GSI then adds 3,184 rows, drops none, and rewrites 46,866 of 46,913 surviving
  coordinates, 99.8998 %.
- Containment of the pre-GSI state in the post-GSI state holds on identity keys
  and fails on row content.
- No R1 analogue exists for this transition because withholding added rows would
  change the fit and therefore the surviving coordinates.

## Scope

- The principal single-population limitation is substantially reduced: the
  ordering evidence now comes from two populations, four controlled trackers and
  two operator families over 25 sequence-level clusters, where previously all 50
  ordering cells came from one population.
""")

w("04_FORBIDDEN_OR_OBSOLETE_CLAIMS.md", r"""
# FORBIDDEN AND OBSOLETE CLAIMS

Binding. Several entries correct statements that appeared in earlier reports in
this project.

## Corrected errors, do not reintroduce

| forbidden | correct form | basis |
|---|---|---|
| OC-SORT GPR rewrites 212 rows, 0.4616 % | 52 rows above 1e-6 px; 2,622 at exact float equality | `FINAL_gpr_rewrite_recount.csv`; the 212 figure was a 2-decimal rounding-boundary artifact |
| the GPR rewrite count needs no tolerance | state the 1e-6 px criterion explicitly | exact equality gives 2,622, so an untolerated reproduction disagrees with 52 |
| MOT20 gate-stable non-admission is unavailable | 6,631 / 34,814 = 19.046935 % | Step 9 `C3_gate_stability_summary.csv`; the D1B table omitted it through a code filter |
| GSI independently replicates the DTI ordering effect | all 7 crossings arise at GSI's linear stage; the GP stage adds 0 | D2C |
| two independent mechanisms reproduced the ranking effect | the two operators share a linear interpolation stage | D2C |
| independent interpolation mechanisms | GSI's first stage *is* linear gap filling | D2C |
| 12,767 frozen per-row STV classifications were independently reproduced | population and identities reproduced; frozen agreement is at the sequence-by-class level; no frozen per-row class table exists | Step 9.1 |
| 25 independent sequences | 25 sequences, or 25 sequence-level clusters | D1B.1; independence was never established |
| the GP stage contributes no evaluated-state effect | all 20 metric cells move; median GP share 0.181, max 0.872 | D2C |
| the GP stage changes the ordering conclusions | 0 of 30 cells cross zero on that transition | D2C |
| S1 exists for StrongSORT++ | PRE, S0, S2 only; no S1, because GSI is not row-additive | frozen `DECOMPOSITION.json` |

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
| non-admitted means geometrically implausible | 62.04 to 73.54 % of non-admitted DanceTrack rows reach maximum IoU at or above 0.5 |
| REFERENCE_ABSENT rows have no nearby ground-truth geometry | 3,448 of 3,451 have another identity overlapping the box |
| the added rows are errors | the audit measures composition and reference support, not correctness |
| admitted rows always have strong local geometric support | 1.78 to 2.61 % of admitted rows fall below IoU 0.5 |
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
""")

MET = ["HOTA","DetA","AssA","IDF1","MOTA"]
rows=[]
def L(qid, pop, arm, quantity, value, unit, artifact, status="CURRENT", note=""):
    rows.append([qid,pop,arm,quantity,value,unit,artifact,status,note])
# MOT17
m17 = [("Deep-OC-SORT",2960,570,286,0,2104,856,"28.9189",694,"23.4459"),
       ("OC-SORT",2622,408,375,0,1839,783,"29.8627",666,"25.4005"),
       ("BoT-SORT",2090,576,227,0,1287,803,"38.4211",634,"30.3349"),
       ("ByteTrack",2072,604,244,0,1224,848,"40.9266",694,"33.4942"),
       ("Hybrid-SORT",3023,1266,216,0,1541,1482,"49.0241",1327,"43.8968")]
for n,sy,u,i,a,ad,na,pc,gs,gp in m17:
    L(f"M17-{n}-SYNTH","MOT17","released DTI",f"{n} synthesized rows",sy,"rows","Step 9 B1_mot17_gate_summary.csv")
    L(f"M17-{n}-UNM","MOT17","released DTI",f"{n} ANCHOR_UNMATCHED at gate 0.50",u,"rows","Step 9 B1_mot17_gate_summary.csv")
    L(f"M17-{n}-IDM","MOT17","released DTI",f"{n} ANCHOR_ID_MISMATCH at gate 0.50",i,"rows","Step 9 B1_mot17_gate_summary.csv")
    L(f"M17-{n}-ABS","MOT17","released DTI",f"{n} TARGET_REFERENCE_ABSENT at gate 0.50",a,"rows","Step 9 B1_mot17_gate_summary.csv")
    L(f"M17-{n}-ADM","MOT17","released DTI",f"{n} SEMANTICALLY_ADMITTED at gate 0.50",ad,"rows","Step 9 B1_mot17_gate_summary.csv")
    L(f"M17-{n}-NA","MOT17","released DTI",f"{n} non-admitted at gate 0.50",na,"rows","Step 9 B1_mot17_gate_summary.csv")
    L(f"M17-{n}-NAPCT","MOT17","released DTI",f"{n} non-admitted fraction at gate 0.50",pc,"percent","Step 9 B1_mot17_gate_summary.csv")
    L(f"M17-{n}-GS","MOT17","released DTI",f"{n} gate-stable non-admitted",gs,"rows","Step 9 C3_gate_stability_summary.csv")
    L(f"M17-{n}-GSPCT","MOT17","released DTI",f"{n} gate-stable non-admitted fraction",gp,"percent","Step 9 C3_gate_stability_summary.csv")
L("M17-NA-RANGE","MOT17","released DTI","primary-gate non-admission range","28.92 to 49.02","percent","Step 9 B1")
L("M17-GS-RANGE","MOT17","released DTI","gate-stable non-admission range","23.45 to 43.90","percent","Step 9 C3")
L("M17-ABS-ALL","MOT17","released DTI","TARGET_REFERENCE_ABSENT, every deployment, every gate",0,"rows","Step 9 B1 and C3")
L("M17-DELTAS","MOT17","released DTI","metric deltas positive/zero/negative","25/0/0","cells","Step 9 D1_bootstrap_summary.json point_estimates")
L("M17-CELLS","MOT17","released DTI","exhaustive pairwise metric cells",50,"cells","Step 9 D1_bootstrap_10000.csv")
L("M17-CROSS","MOT17","released DTI","cells crossing zero",5,"cells","Step 9 D1_bootstrap_summary.json")
L("M17-CROSS-3DP","MOT17","released DTI","crossings surviving 3-decimal reporting",5,"cells","FINAL_unified_pairwise_margins.csv")
L("M17-CROSS-2DP","MOT17","released DTI","crossings surviving 2-decimal reporting",5,"cells","FINAL_unified_pairwise_margins.csv")
L("M17-CI-R0","MOT17","released DTI","percentile intervals excluding zero at R0","33/50","cells","Step 9 D1_bootstrap_summary.json")
L("M17-CI-R2","MOT17","released DTI","percentile intervals excluding zero at R2","28/50","cells","Step 9 D1_bootstrap_summary.json")
L("M17-CI-D","MOT17","released DTI","percentile intervals excluding zero for delta margin","32/50","cells","Step 9 D1_bootstrap_summary.json")
L("M17-SEQ","MOT17","released DTI","sequences",7,"sequences","v5 main Sec. 4.3")
L("M17-FRAMES","MOT17","released DTI","frames",2652,"frames","v5 main Sec. 4.3")
L("M17-SYNTH-TOTAL","MOT17","released DTI","synthesized rows, all five deployments",12767,"rows","Step 9 A3_primary_replay_rows.csv")
L("M17-REPLAY","MOT17","released DTI","frozen sequence-by-class cells reproduced","105/105 MOT17, 130/130 including MOT20","cells","Step 9.1 STEP9_REPORT_CORRECTIONS.md","CURRENT","supersedes the per-row phrasing")
L("M17-GTGAP","MOT17","reference population","GT tracks with an interior gap","0 of 339","tracks","final_defense_20261004 report Part II")
# MOT20
L("M20-CELLS","MOT20","eligibility census","configurations pre-specified",7,"configurations","v5 supplement Sec. S7")
L("M20-ELIG","MOT20","eligibility census","eligible",1,"configurations","v5 supplement Sec. S7")
L("M20-OVERLAP","MOT20","eligibility census","clause (i) detector-training overlap",5,"configurations","v5 supplement Sec. S7")
L("M20-UNRES","MOT20","eligibility census","unresolved under clause (ii)",1,"configurations","v5 supplement Sec. S7")
L("M20-FRAMES","MOT20","released DTI","frames",4463,"frames","v5 supplement Sec. S8")
L("M20-SYNTH","MOT20","released DTI","synthesized rows",34814,"rows","Step 9 B2_mot20_gate_summary.csv")
L("M20-NA","MOT20","released DTI","non-admitted at gate 0.50",8751,"rows","Step 9 B2")
L("M20-NAPCT","MOT20","released DTI","non-admitted fraction at gate 0.50","25.1364","percent","Step 9 B2")
L("M20-GS","MOT20","released DTI","gate-stable non-admitted",6631,"rows","Step 9 C3","CURRENT","D1B omitted this; D1B.1 restored it")
L("M20-GSPCT","MOT20","released DTI","gate-stable non-admitted fraction","19.046935","percent","Step 9 C3","CURRENT","6631/34814")
L("M20-ABS","MOT20","released DTI","TARGET_REFERENCE_ABSENT, every gate",0,"rows","Step 9 B2 and C3")
for g,na,pc in (("0.30",6768,"19.4405"),("0.40",7612,"21.8648"),("0.50",8751,"25.1364"),("0.60",11793,"33.8743"),("0.70",18891,"54.2627")):
    L(f"M20-GATE-{g}","MOT20","released DTI",f"non-admitted at gate {g}",na,"rows","Step 9 B2")
    L(f"M20-GATEPCT-{g}","MOT20","released DTI",f"non-admitted fraction at gate {g}",pc,"percent","Step 9 B2")
# DanceTrack population
L("DT-SEQ","DanceTrack","population","sequences",25,"sequences","D1B protocol lock Sec. 6")
L("DT-FRAMES","DanceTrack","population","frames",25508,"frames","D1B protocol lock Sec. 6")
L("DT-GTROWS","DanceTrack","population","scoreable GT rows",225148,"rows","D1B protocol lock Sec. 6")
L("DT-GTTRACKS","DanceTrack","population","GT tracks",273,"tracks","final_defense_20261004 Part II")
L("DT-GTGAPPED","DanceTrack","population","GT tracks with an interior gap","209 of 273, 76.6 %","tracks","final_defense_20261004 Part II")
L("DT-GTGAPS","DanceTrack","population","interior GT gaps",1370,"gaps","final_defense_20261004 Part II","CURRENT","matches Frag=1370 from the D1A evaluator sanity test")
L("DT-GTSLOTS","DanceTrack","population","missing GT frame-slots",15326,"slots","final_defense_20261004 Part II")
# DanceTrack DTI
dt=[("ByteTrack",216310,224821,8511,"3.786",8511,3659,1642,526,2684,5827,"68.46",5330,"62.62"),
    ("OC-SORT",202787,217890,15103,"6.931",15103,2338,3817,1007,7941,7162,"47.42",6547,"43.35"),
    ("Deep-OC-SORT",203149,217171,14022,"6.457",14022,2015,2790,1089,8128,5894,"42.03",5335,"38.05"),
    ("Hybrid-SORT",215393,227851,12458,"5.468",12458,5206,1941,829,4482,7976,"64.02",7139,"57.30")]
for n,r0,r2,ins,pct,sy,u,i,a,ad,na,napct,gs,gspct in dt:
    L(f"DTI-{n}-R0","DanceTrack","controlled DTI",f"{n} R0 rows",r0,"rows","D1B D1B_state_inventory.csv")
    L(f"DTI-{n}-R2","DanceTrack","controlled DTI",f"{n} R2 primary rows",r2,"rows","D1B D1B_state_inventory.csv")
    L(f"DTI-{n}-INS","DanceTrack","controlled DTI",f"{n} inserted rows",ins,"rows","D1B D1B_state_inventory.csv")
    L(f"DTI-{n}-INSPCT","DanceTrack","controlled DTI",f"{n} inserted fraction of R2",pct,"percent","D1B D1B_state_inventory.csv")
    L(f"DTI-{n}-UNM","DanceTrack","controlled DTI",f"{n} ANCHOR_UNMATCHED at gate 0.50",u,"rows","D1B D1B_stv_primary.csv")
    L(f"DTI-{n}-IDM","DanceTrack","controlled DTI",f"{n} ANCHOR_ID_MISMATCH at gate 0.50",i,"rows","D1B D1B_stv_primary.csv")
    L(f"DTI-{n}-ABS","DanceTrack","controlled DTI",f"{n} TARGET_REFERENCE_ABSENT at gate 0.50",a,"rows","D1B D1B_stv_primary.csv")
    L(f"DTI-{n}-ADM","DanceTrack","controlled DTI",f"{n} SEMANTICALLY_ADMITTED at gate 0.50",ad,"rows","D1B D1B_stv_primary.csv")
    L(f"DTI-{n}-NA","DanceTrack","controlled DTI",f"{n} non-admitted at gate 0.50",na,"rows","D1B D1B_stv_primary.csv")
    L(f"DTI-{n}-NAPCT","DanceTrack","controlled DTI",f"{n} non-admitted fraction at gate 0.50",napct,"percent","D1B D1B_stv_primary.csv")
    L(f"DTI-{n}-GS","DanceTrack","controlled DTI",f"{n} gate-stable non-admitted",gs,"rows","D1B D1B_gate_persistence_summary.csv")
    L(f"DTI-{n}-GSPCT","DanceTrack","controlled DTI",f"{n} gate-stable non-admitted fraction",gspct,"percent","D1B D1B_gate_persistence_summary.csv")
L("DTI-NMIN","DanceTrack","controlled DTI","primary n_min",25,"frames","D1B protocol lock Sec. 8")
L("DTI-NDTI","DanceTrack","controlled DTI","primary n_dti",20,"frames","D1B protocol lock Sec. 8")
L("DTI-NMIN-S","DanceTrack","controlled DTI","sensitivity n_min",30,"frames","D1B protocol lock Sec. 8")
L("DTI-NA-RANGE","DanceTrack","controlled DTI","primary-gate non-admission range","42.03 to 68.46","percent","D1B D1B_stv_primary.csv")
L("DTI-GS-RANGE","DanceTrack","controlled DTI","gate-stable non-admission range","38.05 to 62.62","percent","D1B D1B_gate_persistence_summary.csv")
L("DTI-INS-RANGE","DanceTrack","controlled DTI","inserted fraction range","3.79 to 6.93","percent","D1B D1B_state_inventory.csv")
L("DTI-DELTAS","DanceTrack","controlled DTI","metric deltas positive/zero/negative","12/0/8","cells","D1B D1B_metric_deltas_primary.csv")
L("DTI-CELLS","DanceTrack","controlled DTI","exhaustive pairwise metric cells",30,"cells","D1B D1B_pairwise_30cells.csv")
L("DTI-CROSS","DanceTrack","controlled DTI","cells crossing zero",7,"cells","D1B.1 D1B1_pairwise_30cells_recomputed.csv")
L("DTI-CROSS-3DP","DanceTrack","controlled DTI","crossings surviving 3-decimal reporting",7,"cells","D1B.1 D1B1_flip_precision_audit.csv")
L("DTI-CROSS-2DP","DanceTrack","controlled DTI","crossings surviving 2-decimal reporting",7,"cells","D1B.1 D1B1_flip_precision_audit.csv")
L("DTI-PSIGN-RANGE","DanceTrack","controlled DTI","P(sign differs) across the seven crossings","0.3240 to 0.9365","frequency","D1B.1 D1B1_flip_precision_audit.csv","CURRENT","descriptive, not a p-value")
L("DTI-SENS-NA","DanceTrack","controlled DTI","largest non-admission difference, 25/20 against 30/20","0.42","percentage points","D1B D1B_stv_sens30_primary_gate.csv")
L("DTI-SENS-MET","DanceTrack","controlled DTI","largest metric difference, 25/20 against 30/20","0.0422","metric points","D1B D1B_dti_parameter_sensitivity.csv")
L("DTI-3T-CELLS","DanceTrack","controlled DTI","three-tracker provenance-sensitivity cells",15,"cells","FINAL_three_tracker_provenance_sensitivity.csv")
L("DTI-3T-CROSS","DanceTrack","controlled DTI","three-tracker cells crossing zero",3,"cells","FINAL_three_tracker_provenance_sensitivity.csv")
L("DT-ABS-TOTAL","DanceTrack","controlled DTI","TARGET_REFERENCE_ABSENT rows at gate 0.50, all four",3451,"rows","D1B.2 D1B2_reference_absent_local_support.csv")
L("DT-ABS-ALLGATES","DanceTrack","controlled DTI","TARGET_REFERENCE_ABSENT rows, all four trackers, all five gates",16019,"rows","D1B.1 D1B1_reference_absent_audit.json")
L("DT-ABS-INGAP","DanceTrack","controlled DTI","of those, inside a verified internal GT gap","16019 of 16019","rows","D1B.1 D1B1_reference_absent_audit.json")
L("DT-ABS-ADJ","DanceTrack","controlled DTI","identity annotated at an adjacent frame",9047,"rows","D1B.1 D1B1_reference_absent_audit.json")
L("DT-ABS-AGREE","DanceTrack","controlled DTI","independent predicate agreements with the frozen classifier","250470 of 250470","decisions","D1B.1 D1B1_reference_absent_audit.json")
L("DT-ABS-OTHERGT","DanceTrack","row-local support","REFERENCE_ABSENT rows with another GT identity overlapping","3448 of 3451","rows","D1B.2 D1B2_reference_absent_local_support.csv")
L("DT-ABS-INTENDED","DanceTrack","row-local support","REFERENCE_ABSENT rows with the intended identity present","0 of 3451","rows","D1B.2")
L("DT-RL-ADM-RANGE","DanceTrack","row-local support","ADMITTED rows at maxIoU >= 0.5","97.39 to 98.22","percent","D1B.2 D1B2_row_local_support.csv")
L("DT-RL-NA-RANGE","DanceTrack","row-local support","non-admitted rows at maxIoU >= 0.5","62.04 to 73.54","percent","D1B.2 D1B2_row_local_support.csv")
L("DT-RL-ADM-BELOW","DanceTrack","row-local support","ADMITTED rows below maxIoU 0.5","1.78 to 2.61","percent","D1B.2 D1B2_row_local_support.csv")
# GSI
gsi=[("ByteTrack",225199,8889,127411,"58.902",134528,"59.74"),
     ("OC-SORT",218591,15804,136814,"67.467",150335,"68.77"),
     ("Deep-OC-SORT",218075,14926,123954,"61.016",136145,"62.43"),
     ("Hybrid-SORT",228696,13303,122427,"56.839",133187,"58.24")]
for n,tot,ins,rw,pct,rw2,pct2 in gsi:
    L(f"GSI-{n}-ROWS","DanceTrack","controlled GSI",f"{n} GSI rows",tot,"rows","D2B D2B_state_inventory.csv")
    L(f"GSI-{n}-INS","DanceTrack","controlled GSI",f"{n} inserted rows",ins,"rows","D2B D2B_state_inventory.csv")
    L(f"GSI-{n}-RW","DanceTrack","controlled GSI",f"{n} surviving rows with coordinate rewrites",rw,"rows","D2B D2B_state_inventory.csv")
    L(f"GSI-{n}-RWPCT","DanceTrack","controlled GSI",f"{n} coordinate-rewrite fraction",pct,"percent","D2B D2B_state_inventory.csv")
    L(f"GSI-{n}-GPRW","DanceTrack","controlled GSI",f"{n} L_GSI to GSI coordinate rewrites",rw2,"rows","D2C D2C_gsi_linear_state_inventory.csv")
    L(f"GSI-{n}-GPRWPCT","DanceTrack","controlled GSI",f"{n} L_GSI to GSI rewrite fraction",pct2,"percent","D2C D2C_gsi_linear_state_inventory.csv")
L("GSI-INTERVAL","DanceTrack","controlled GSI","interval",20,"frames","D2A GSI_PROTOCOL_LOCK.md Sec. 4")
L("GSI-TAU","DanceTrack","controlled GSI","tau",10,"unitless","D2A GSI_PROTOCOL_LOCK.md Sec. 4")
L("GSI-DEL","DanceTrack","controlled GSI","deleted rows, all four",0,"rows","D2B D2B_state_inventory.csv")
L("GSI-IDCHG","DanceTrack","controlled GSI","tracker-id changes, all four",0,"rows","D2B D2B_state_inventory.csv")
L("GSI-RW-RANGE","DanceTrack","controlled GSI","coordinate-rewrite fraction range","56.839 to 67.467","percent","D2B D2B_state_inventory.csv")
L("GSI-DELTAS","DanceTrack","controlled GSI","metric deltas positive/zero/negative","12/0/8","cells","D2B D2B_metric_deltas.csv")
L("GSI-CROSS","DanceTrack","controlled GSI","cells crossing zero",7,"cells","D2B D2B_pairwise_30cells.csv")
L("GSI-CROSS-3DP","DanceTrack","controlled GSI","crossings surviving 3-decimal reporting",7,"cells","D2B D2B_pairwise_30cells.csv")
L("GSI-CROSS-2DP","DanceTrack","controlled GSI","crossings surviving 2-decimal reporting",7,"cells","D2B D2B_pairwise_30cells.csv")
L("GSI-3T-CROSS","DanceTrack","controlled GSI","three-tracker cells crossing zero",3,"cells","FINAL_three_tracker_provenance_sensitivity.csv")
L("D2C-LIN-RW","DanceTrack","GSI decomposition","R0 to L_GSI coordinate rewrites, all four",0,"rows","D2C D2C_gsi_linear_state_inventory.csv")
L("D2C-LIN-CROSS","DanceTrack","GSI decomposition","R0 to L_GSI cells crossing zero",7,"cells","D2C D2C_three_state_pairwise_margins.csv")
L("D2C-GP-CROSS","DanceTrack","GSI decomposition","L_GSI to GSI cells crossing zero",0,"cells","D2C D2C_three_state_pairwise_margins.csv")
L("D2C-TOT-CROSS","DanceTrack","GSI decomposition","R0 to GSI cells crossing zero",7,"cells","D2C D2C_three_state_pairwise_margins.csv")
L("D2C-GP-SHARE","DanceTrack","GSI decomposition","GP share of total absolute metric movement, median","0.181","fraction","D2C D2C_three_state_metrics.csv")
L("D2C-GP-SHARE-RANGE","DanceTrack","GSI decomposition","GP share range","0.042 to 0.872","fraction","D2C D2C_three_state_metrics.csv")
L("D2C-GP-OPPOSE","DanceTrack","GSI decomposition","cells where the GP delta opposes the linear delta","8 of 20","cells","D2C D2C_three_state_metrics.csv")
# GPR
L("GPR-G0","MOT17","GPR boundary case","G0 rows",45927,"rows","FINAL_gpr_rewrite_recount.csv")
L("GPR-G2","MOT17","GPR boundary case","G2 rows",45927,"rows","FINAL_gpr_rewrite_recount.csv")
L("GPR-INS","MOT17","GPR boundary case","insertions",0,"rows","FINAL_gpr_rewrite_recount.csv")
L("GPR-DEL","MOT17","GPR boundary case","deletions",0,"rows","FINAL_gpr_rewrite_recount.csv")
L("GPR-RW-TOL","MOT17","GPR boundary case","rows changed by more than 1e-6 px",52,"rows","FINAL_gpr_rewrite_recount.csv","CURRENT","the manuscript value; state the tolerance")
L("GPR-RW-EXACT","MOT17","GPR boundary case","rows differing at exact float equality",2622,"rows","FINAL_gpr_rewrite_recount.csv")
L("GPR-RW-SCALARS","MOT17","GPR boundary case","changed coordinate scalars at exact equality",5244,"scalars","FINAL_gpr_rewrite_recount.csv")
L("GPR-RW-WH","MOT17","GPR boundary case","rows with w or h changed",0,"rows","FINAL_gpr_rewrite_recount.csv")
L("GPR-RW-MAX","MOT17","GPR boundary case","largest coordinate change","1.7e-05","pixels","FINAL_gpr_rewrite_recount.csv")
L("GPR-RW-MED","MOT17","GPR boundary case","median coordinate change","3.69e-09","pixels","FINAL_gpr_rewrite_recount.csv")
L("GPR-RW-GT1E3","MOT17","GPR boundary case","rows changed by more than 0.001 px",0,"rows","FINAL_gpr_rewrite_recount.csv")
L("GPR-METRIC","MOT17","GPR boundary case","change in all five reported metrics","0.0000","metric points","FINAL_gpr_rewrite_recount.csv","CURRENT","to four decimals")
L("GPR-DETAILED","MOT17","GPR boundary case","differing fields in the full-precision detailed output",197,"fields","FINAL_gpr_rewrite_recount.csv","CURRENT","all LocA family")
L("GPR-212","MOT17","GPR boundary case","superseded rewrite count",212,"rows","FINAL_gpr_rewrite_recount.csv","SUPERSEDED","2-decimal rounding-boundary artifact; do not cite")
# StrongSORT
L("SS-PRE","MOT17","AFLink and GSI","PRE rows",46914,"rows","frozen strongsort/DECOMPOSITION.json")
L("SS-S0","MOT17","AFLink and GSI","S0 rows, post-AFLink",46913,"rows","frozen strongsort/DECOMPOSITION.json")
L("SS-S2","MOT17","AFLink and GSI","S2 rows, post-GSI",50097,"rows","frozen strongsort/DECOMPOSITION.json")
L("SS-IDCHG","MOT17","AFLink and GSI","rows whose identity AFLink changed",1316,"rows","frozen strongsort/DECOMPOSITION.json")
L("SS-REMAP","MOT17","AFLink and GSI","distinct AFLink identity remappings",29,"remappings","frozen strongsort/DECOMPOSITION.json")
L("SS-ADD","MOT17","AFLink and GSI","rows added by the linear stage",3184,"rows","frozen strongsort/DECOMPOSITION.json")
L("SS-RW","MOT17","AFLink and GSI","surviving rows with rewritten coordinates",46866,"rows","frozen strongsort/DECOMPOSITION.json")
L("SS-RWPCT","MOT17","AFLink and GSI","rewrite fraction","99.8998","percent","frozen strongsort/DECOMPOSITION.json")
for m,v in zip(MET,["+1.220","+1.278","+1.211","+0.830","+1.561"]):
    L(f"SS-D{m}","MOT17","AFLink and GSI",f"GSI stage {m} delta",v,"metric points","frozen StrongSORT_S0/S2 pedestrian_summary.txt")
# bootstrap
L("BS-DRAWS","both","bootstrap","draws",10000,"draws","Step 9 and D1B bootstrap summaries")
L("BS-SEED","both","bootstrap","seed",20261003,"integer","Step 9 and D1B bootstrap summaries")
L("BS-M17-UNITS","MOT17","bootstrap","resampling units",7,"sequence clusters","Step 9 D1_bootstrap_summary.json")
L("BS-DT-UNITS","DanceTrack","bootstrap","resampling units",25,"sequence clusters","D1B D1B_bootstrap_summary.json")
L("BS-M17-HASH","MOT17","bootstrap","index matrix sha256","8cd16bcc23a47d1f4ce8bd5275ad8df660fa69411390b8ee7e365970e2db7cd2","sha256","Step 9 D1_bootstrap_indices.sha256")
L("BS-DT-HASH","DanceTrack","bootstrap","index matrix file sha256","50b2fb2240ffbdbc221d5a0f73681a4dfbec4ccc4f07a42f9cd01cc3c18516da","sha256","D1B bootstrap/D1B_bootstrap_indices.sha256")
wc("05_NUMERIC_LEDGER.csv",
   ["id","population","arm","quantity","value","unit","artifact","status","note"], rows)
