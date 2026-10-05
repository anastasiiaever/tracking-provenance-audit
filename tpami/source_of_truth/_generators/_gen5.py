"""Writes 06, 07, 08, 09.

Line-ending note: csv.writer here emits CRLF, which matches the shipped 05, 06
and 26. The shipped 09_PROVENANCE_LEDGER.csv carries LF, because two sha256
fields were filled in afterwards by a text-mode patch that normalised the file.
Content is identical either way; a full re-run of this generator reproduces 09's
fields exactly but with CRLF. Regenerate 09 only when its content changes.
"""
import os, csv
V="<AUDIT_ROOT>/V6_SOURCE_OF_TRUTH"
def w(n,s): open(os.path.join(V,n),"w").write(s.lstrip("\n")); print("  wrote",n)
def wc(n,hdr,rows):
    with open(os.path.join(V,n),"w",newline="") as f:
        x=csv.writer(f); x.writerow(hdr); x.writerows(rows)
    print(f"  wrote {n} ({len(rows)} rows)")

HDR=["arm","v6_label","released_or_controlled","population","n_trackers","operator",
     "state_transition_type","operator_family","STV_applicable","R1_applicable",
     "metric_state_comparison","ordering_margin_analysis","prespecified","main_caveat",
     "v6_section","authoritative_artifact"]
rows=[
["MOT17 released DTI deployments","Arm 1","RELEASED","MOT17-val, 7 sequences, 2652 frames",5,
 "each deployment's own documented DTI; n_min was 5 or 30 across the released deployments, 5 for ByteTrack and BoT-SORT and 30 for OC-SORT, Deep-OC-SORT and Hybrid-SORT, with n_dti 20 throughout",
 "row-additive in evaluator-relevant geometry and identity","LINEAR_DTI","YES","YES",
 "YES, 25 cells, 25 positive 0 zero 0 negative",
 "YES, 50 exhaustive pairwise metric cells, 5 cross zero, all 5 survive 3dp and 2dp",
 "PRE-SPECIFIED",
 "retrospective; eligibility governed by the documented-rule requirement; ordering evidence from one population only",
 "Sec. 4.2-4.3, released deployments",
 "posthoc_composition_20261003/results/{B1,C3,D1}"],
["MOT20 eligible released cell","Arm 2","RELEASED","MOT20-val, 4 sequences, 4463 frames",1,
 "Deep-OC-SORT's released DTI, n_min=30",
 "row-additive in evaluator-relevant geometry and identity","LINEAR_DTI","YES","YES",
 "single deployment, no ordering pair available",
 "NOT AVAILABLE: one tracker yields no pair",
 "PRE-SPECIFIED, eligibility census frozen before any MOT17 execution",
 "secondary population, one eligible deployment of seven pre-specified; primary-gate non-admission 25.1364 %, gate-stable 19.0469 %",
 "Sec. 4.4, second population composition",
 "posthoc_composition_20261003/results/{B2,C3}"],
["DanceTrack controlled DTI","Arm 3","CONTROLLED","DanceTrack-val, 25 sequences, 25508 frames",4,
 "one common DTI applied by us, n_min=25 n_dti=20, identical for all four",
 "row-additive in evaluator-relevant geometry and identity; confidence column overwritten","LINEAR_DTI","YES","YES",
 "YES, 20 cells, 12 positive 0 zero 8 negative",
 "YES, 30 exhaustive pairwise metric cells, 7 cross zero, all 7 survive 3dp and 2dp",
 "PRE-SPECIFIED within the DanceTrack step; protocol frozen before any result was inspected",
 "the operator is ours, not the authors'; one shared detector improves control but reduces detector diversity; Deep-OC-SORT checkpoint-selection provenance UNRESOLVED",
 "Sec. 5.2-5.6, controlled second population",
 "dancetrack_controlled_20261003/summaries/* and step_d1b_1/*"],
["DanceTrack controlled GSI","Arm 4","CONTROLLED","DanceTrack-val, 25 sequences",4,
 "one common StrongSORT GSI applied by us, interval=20 tau=10",
 "key-additive but content-rewriting: 0 deletions, 56.8389 to 67.4668 % of surviving coordinates rewritten",
 "LINK_AND_SMOOTHING, smoothing stage only",
 "NO: the GP fit couples output coordinates to the state being fitted, so no row-subset intervention exists",
 "NO, same reason",
 "YES, 20 cells, 12 positive 0 zero 8 negative",
 "YES, 30 cells, 7 cross zero; D2C shows all 7 are established by the linear stage and the GP stage adds 0",
 "POST-HOC, designed after the DTI outcomes were known",
 "not released DanceTrack practice; its linear stage shares a mechanism with DTI, so it is NOT an independent downstream mechanism",
 "Sec. 5.7, operator-family generality",
 "dancetrack_controlled_20261003/gsi_exec_20261004/* and final_defense_20261004/D2C_*"],
["GSI decomposed, linear stage","Arm 4a","CONTROLLED","DanceTrack-val, 25 sequences",4,
 "GSI's LinearInterpolation only, interval=20","strictly row-additive, 0 coordinate rewrites","LINEAR_DTI","YES","YES",
 "YES, 20 cells","YES, 30 cells, 7 cross zero",
 "POST-HOC, decomposition of Arm 4",
 "shares its mechanism with Arm 3, so the two operator arms are not independent",
 "Sec. 5.7, operator-family generality",
 "final_defense_20261004/D2C_three_state_pairwise_margins.csv"],
["GSI decomposed, Gaussian-process stage","Arm 4b","CONTROLLED","DanceTrack-val, 25 sequences",4,
 "GSI's GaussianSmooth only, tau=10","rewrite-only on the linear state; 58.2376 to 68.7746 % of rows rewritten",
 "LINK_AND_SMOOTHING","NO","NO",
 "YES, all 20 cells move; median GP share of absolute movement 0.1812, range 0.0421 to 0.8722; opposes the linear stage in 8 of 20",
 "YES, 30 cells, 0 cross zero",
 "POST-HOC, decomposition of Arm 4",
 "produces evaluated-state change without producing ordering crossings on this population",
 "Sec. 5.7, operator-family generality",
 "final_defense_20261004/D2C_three_state_metrics.csv"],
["OC-SORT GPR, MOT17","Arm 5","RELEASED","MOT17-val, 7 sequences",1,
 "OC-SORT's released GPR stage",
 "rewrite-only: 0 inserted, 0 deleted; 52 of 45927 surviving rows change by more than 1e-6 px, 0.1132 %; 2622 differ at exact float equality by 8.9e-12 to 1.7e-05 px; only x and y, never w or h",
 "GPR_REWRITE","NO: STRUCTURALLY_UNDEFINED","NO",
 "YES, and the change is 0.0000 on all five metrics to four decimals; pedestrian_summary.txt byte-identical, pedestrian_detailed.csv differs in 197 LocA-family fields",
 "NOT AVAILABLE: one tracker yields no pair",
 "PRE-SPECIFIED as part of the operator-family census",
 "boundary case: an operator that rewrites the evaluated state yet moves no reported metric; it shows rewriting alone does not imply a benchmark effect",
 "Sec. 3.4 and Sec. 6.1, boundary case",
 "final_defense_20261004/FINAL_gpr_rewrite_recount.csv"],
["StrongSORT++ AFLink and GSI, MOT17","Arm 6","RELEASED","MOT17-val, 7 sequences",1,
 "StrongSORT++'s released AFLink then GSI, interval=20 tau=10",
 "AFLink: 1316 rows change identity across 29 remappings, 1 row lost, 46914 to 46913. GSI: 3184 rows added, 0 dropped, 46866 of 46913 surviving coordinates rewritten, 99.8998 %",
 "LINK_AND_SMOOTHING","NO: no row-subset intervention preserves the fit","NO",
 "YES, the GSI stage moves HOTA +1.220, DetA +1.278, AssA +1.211, IDF1 +0.830, MOTA +1.561",
 "NOT AVAILABLE: one tracker yields no pair",
 "PRE-SPECIFIED as part of the operator-family census",
 "containment of the pre-GSI state holds on identity keys and fails on row content; no R1 analogue exists, so PRE, S0 and S2 only, with no S1",
 "Sec. 3.4 and Sec. 6.2, linking and smoothing",
 "frozen strongsort/DECOMPOSITION.json via posthoc_composition_20261003"],
]
wc("06_EVIDENCE_ARCHITECTURE.csv",HDR,rows)

w("07_METHOD_DEFINITIONS.md", r"""
# METHOD DEFINITIONS

Normative. Every definition below is the one implemented in the released code and
used by every artifact in this directory. Use these words; do not paraphrase them
into looser ones.

## 1. States

| symbol | meaning | availability |
|---|---|---|
| R0 | the tracker's own output, before the offline operator | all arms |
| R1 | the diagnostic state in which rows that fail admission are withheld from scoring | row-additive transitions only |
| R2 | the submitted, post-processed state | all arms |

For StrongSORT++ the three released stages in the frozen artifact are named PRE,
S0 and S2: PRE is the tracker output, S0 the post-AFLink state and S2 the post-GSI
state. The frozen scheme has no third intermediate state, because GSI is not
row-additive and so admits no withheld-row state. Note that v5's supplement uses a
different scheme, S0 for the tracker output and S1 for post-AFLink; see the
naming-collision note in `04_FORBIDDEN_OR_OBSOLETE_CLAIMS.md` and pick one scheme
for v6. For OC-SORT's GPR stage the two states are G0 and G2.

For the decomposed GSI arm the intermediate state is L_GSI: the output of GSI's
linear interpolation before its Gaussian-process smoothing.

## 2. Row identity

A row is identified by the tuple

    (population, tracker, sequence, frame, track_id)

This key is what makes the row-additive claim checkable. It is also the reason the
GSI transition is called *key-additive but content-rewriting*: the key set grows
monotonically while the coordinates attached to surviving keys change.

## 3. Synthesized row

A row present in R2 and absent from R0 under the key above.

## 4. Scoreable ground truth

A ground-truth row with `mark != 0` and `class == 1`, matching TrackEval's own
preprocessing for the MOTChallenge 2D box task. Admission is evaluated against
this set, not against the raw annotation file.

## 5. Anchors

For a synthesized row at frame `f` with track id `t`, the anchors are the nearest
rows of the same track id in R0 at frames strictly below and strictly above `f`.
Linear DTI creates rows only strictly between two observed frames, so both
anchors exist for every synthesized row in the row-additive arms.

## 6. Admission gate

A synthesized row's anchors are matched to scoreable ground truth by IoU at a
stated gate. The primary gate is 0.50. The reported sweep is
0.30, 0.40, 0.50, 0.60, 0.70.

A row is *gate-stable non-admitted* when it is non-admitted at every gate in the
sweep. Gate-stable counts are therefore conservative by construction: they are a
lower bound on non-admission that does not depend on the choice of gate.

## 7. Scoreable-target validity, the four classes

Evaluated in this exact priority order, as an `if`/`elif` chain. The four classes
partition the synthesized rows exactly; the counts sum to the synthesized total in
every artifact.

1. **ANCHOR_UNMATCHED** — at least one anchor has no scoreable ground-truth match
   at the gate. The operator extended a track segment whose endpoints are not
   themselves anchored in the reference.
2. **ANCHOR_ID_MISMATCH** — both anchors match, but to different ground-truth
   identities. The interpolated segment spans an identity boundary, so no single
   reference identity is implied.
3. **TARGET_REFERENCE_ABSENT** — both anchors match the same ground-truth
   identity, but that identity has no scoreable row at the synthesized frame.
   The reference does not state where the target is at that moment.
4. **SEMANTICALLY_ADMITTED** — both anchors match the same identity and that
   identity is present at the synthesized frame.

Classes 1 to 3 are collectively *non-admitted*.

### What admission is and is not

Admission is a **reference-side** predicate. It is computed from the anchors and
from the availability of the anchor-resolved reference identity. The synthesized
row's own coordinates do not enter the predicate at all.

Consequently:

- non-admission is **not** a false-positive label and **not** a claim that the row
  is geometrically wrong;
- TARGET_REFERENCE_ABSENT is **not** a tracker error: it records that the
  reference is silent at that frame;
- a row can be non-admitted and still overlap scoreable ground truth well. On
  DanceTrack, 62.0388 to 73.5409 % of non-admitted rows reach maximum IoU at or above
  0.5 against some scoreable identity.

The row-local support measurement in D1B.2 exists to make this gap explicit rather
than to repair it.

## 8. Transition types and the audit each admits

| transition type | keys | content of surviving rows | STV | R1 |
|---|---|---|---|---|
| row-additive | grow | unchanged | defined | defined |
| key-additive but content-rewriting | grow | changed | undefined | undefined |
| rewrite-only | unchanged | changed | undefined | undefined |
| identity-remapping | may shrink | identity changed | undefined | undefined |

Which audit is available is a property of the transition, not a choice. The
released `states.py` records this in the field `r1_status_for_non_row_additive`.

## 9. Operator families

- **LINEAR_DTI** — row-additive gap filling by linear interpolation between
  observed anchors, gated on tracklet length (`n_min`) and gap width (`n_dti`).
- **GPR_REWRITE** — a Gaussian-process refit of surviving coordinates with no key
  change.
- **LINK_AND_SMOOTHING** — tracklet association followed by a smoothing refit;
  keys may grow and surviving content is rewritten.

## 10. The common DanceTrack operator

The DTI arm applies one operator to all four trackers: the `dti` and
`write_results_score` functions extracted verbatim from ByteTrack's
`tools/interpolation.py`, with `n_min=25` and `n_dti=20` for the primary state and
`n_min=30`, `n_dti=20` for the sensitivity state. The extraction is byte-identical
across the three repositories that ship this code.

The GSI arm applies one operator to the same four frozen R0 states: StrongSORT's
`GSInterpolation` with `interval=20` and `tau=10`, the values hardcoded at its only
upstream call site. AFLink is not applied.

Because the operator is held fixed while the tracker varies, this is the
controlled arm: differences between trackers cannot be attributed to differences
in post-processing.

## 11. Evaluation

TrackEval pinned at commit `12c8791b303e0a0b50f753af204249e622d0281a`, unmodified.
Reported metrics are HOTA, DetA, AssA, IDF1 and MOTA. R1 is realised by zeroing
the similarity of non-admitted rows *before* assignment, so a withheld row can
neither match nor displace a match.

Note that DetA and AssA are factors of HOTA. The three are not independent
readings of the same comparison.

## 12. Pairwise ordering margins

For a tracker pair and a metric, the margin is the difference of their scores in
one state. A cell *crosses zero* when the margin has one sign at R0 and the other
at R2. The matrix is exhaustive over pairs and metrics: with four trackers and
five metrics it has 30 cells, and with five deployments, 50.

These cells are **dependent**. Each tracker appears in several pairs, margins
share pooled scores, and HOTA contains DetA and AssA. Counts such as 5 of 50 or
7 of 30 describe how many cells of an exhaustive dependent matrix change sign.
They are not independent trials and carry no binomial interpretation.

Each crossing is reported with four separate facts: the full-precision margins,
whether the crossing survives 3-decimal reporting, whether it survives 2-decimal
reporting, and the bootstrap frequency with which the two states' margins differ
in sign.

## 13. Bootstrap

TrackEval's `combine_sequences` recomputes pooled metrics from per-sequence
accumulators without reference to any other sequence, so resampling whole
sequences and recombining reproduces exactly what the evaluator would report on
that multiset. The resampling unit is therefore the sequence cluster: 7 for
MOT17, 25 for DanceTrack. Draws: 10,000. Seed: 20261003. Multiplicity is carried
by distinct dictionary keys of the form `"<sequence>#<slot>"`.

Sequences are **not** claimed to be independent. "25 sequence-level clusters"
describes the resampling unit; it is not an independence assumption. The reported
intervals are percentile intervals, used descriptively. No hypothesis is tested
and no p-value is computed. The quantity `P(sign differs)` is a bootstrap
frequency.

## 14. Tracker-state equivalence

Two tracker outputs are equivalent when they agree on frames, boxes and the
partition of rows into tracks after a bijective per-sequence relabelling of
tracker ids, with no splits, merges, missing rows or extra rows.

This matters because `BaseTrack._count` is a class attribute that upstream never
resets between sequences, so running a subset of sequences shifts every tracker id
by a constant. The observed ByteTrack smoke-against-full mapping is the
order-preserving shift +424.

Verified invariance, stated at the precision at which it was checked:

- TrackEval is invariant to arbitrary within-sequence bijective tracker-id
  relabelling; it relabels ids internally.
- DTI is invariant modulo the corresponding relabelling.
- STV is verified invariant **for the observed order-preserving constant shift**.
  Arbitrary non-order-preserving permutations are not guaranteed, because
  `assign_reference` sorts predictions by tracker id and tie-breaking can depend
  on that order.

No downstream analysis joins absolute tracker ids across sequences.

## 15. Training-split disjointness and selection provenance

Two separate fields, never merged into one "held out" label.

- **TRAINING_SPLIT_DISJOINT** — whether the evaluated split's images or
  annotations entered the training of the detector or the appearance model.
- **SELECTION_PROVENANCE** — whether the checkpoint and the hyperparameters were
  chosen without reference to the evaluated split.

On DanceTrack, training-split disjointness holds for all four trackers.
Deep-OC-SORT's checkpoint selection is UNRESOLVED, and hyperparameter-selection
provenance is UNRESOLVED for all four. The three-tracker table is the sensitivity
subset that drops the tracker with unresolved checkpoint provenance; it is not a
claim that Deep-OC-SORT is ineligible.
""")

w("08_LIMITATIONS_LEDGER.md", r"""
# LIMITATIONS LEDGER

Status values: OPEN, REDUCED, CLOSED, UNRESOLVED_BY_DESIGN.
"REDUCED" means the limitation is narrower than in v5 and still real.

## L1 Single-population ordering evidence — REDUCED

v5 position: all 50 ordering cells came from MOT17-val.
v6 position: ordering evidence comes from two populations, 50 cells on MOT17-val
across five released deployments and 30 cells on DanceTrack-val across four
controlled trackers, plus a 30-cell replication under a second operator.

Allowed wording: "the principal single-population limitation is substantially
reduced."
Forbidden wording: "breadth is closed", "generality is established".
Residual: two populations, both MOTChallenge-format pedestrian or dancer video.
No aerial, vehicle, or multi-camera population. MOT20 contributes composition but
no ordering pair.

## L2 Operator-family breadth — REDUCED

Audited: LINEAR_DTI across five released deployments and four controlled
trackers; GPR_REWRITE as one released boundary case; LINK_AND_SMOOTHING as one
released case and as one controlled DanceTrack arm.
Residual: the two controlled DanceTrack operators share a linear interpolation
stage, established in D2C. The GSI arm is therefore not an independent second
mechanism for the ordering result. No non-interpolating, non-smoothing family
(for example re-identification-based track merging, or detection-confidence
rewriting) is audited under control.

## L3 Post-hoc status of the GSI arm — UNRESOLVED_BY_DESIGN

The DTI outcomes were known before the GSI protocol was written. The protocol was
frozen before any GSI output was inspected, and that freeze is hashed, but the
arm cannot be called pre-specified or confirmatory. Report it as a post-hoc
operator-family generality check.

## L4 The DanceTrack operator is ours — OPEN

No released DanceTrack submission is audited. The DanceTrack arms demonstrate
what a common post-processing operator does to a controlled comparison; they do
not characterise any author's deployed practice on that benchmark. Upstream
StrongSORT has no DanceTrack entry in `opts.py` at all.

## L5 Shared detector on DanceTrack — OPEN

Control over the operator was bought by holding one detector fixed across the
four trackers. This removes detector variation as a confound and simultaneously
removes detector diversity, so the four R0 states are more similar to one another
than four independently trained systems would be. Both directions should be
stated.

## L6 Selection provenance — OPEN

Training-split disjointness holds for all four DanceTrack trackers.
Deep-OC-SORT's checkpoint-selection provenance is UNRESOLVED. Hyperparameter
selection is UNRESOLVED for all four. The three-tracker subset is reported as a
sensitivity analysis: 3 of 15 cells cross zero under both operators.

## L7 Dependence inside the ordering matrices — UNRESOLVED_BY_DESIGN

The pairwise matrices are exhaustive and dependent. No multiplicity correction is
applied, because none is appropriate to a descriptive census of an exhaustive
matrix. The consequence is that the crossing counts must never be read as
independent trials or converted into a rate or a p-value.

## L8 No statistical test — UNRESOLVED_BY_DESIGN

Bootstrap percentile intervals and sign-change frequencies are descriptive. No
null hypothesis is specified, no test is performed, and the words "significant"
and "robust" are not available in their technical senses.

## L9 Sequence independence is not established — OPEN

The resampling unit is the sequence cluster. Independence between sequences was
never demonstrated, and the earlier phrase "25 independent sequences" was an
error. The bootstrap is justified by the purity of TrackEval's
`combine_sequences`, not by an independence argument.

## L10 Admission is reference-side only — OPEN, and explicitly characterised

Non-admission does not imply geometric implausibility. D1B.2 quantifies the gap:
62.0388 to 73.5409 % of non-admitted DanceTrack rows reach maximum IoU at or above
0.5, and 3,448 of 3,451 TARGET_REFERENCE_ABSENT rows have some other ground-truth
identity overlapping the box. Admission is also not perfectly aligned in the
other direction: 1.7849 to 2.6080 % of admitted rows fall below maximum IoU 0.5.

## L11 TARGET_REFERENCE_ABSENT is population-dependent — CLOSED as a mechanism

Empty on MOT17 and MOT20, non-empty on DanceTrack. The mechanism is established
positively: all 16,019 such rows across trackers and gates lie strictly inside a
gap in the ground-truth track's own observed frame set, and DanceTrack's
scoreable ground truth has 1,370 interior gaps over 209 of 273 tracks where
MOT17's has none over 339 tracks. This is a property of the annotation, so the
class will appear on any population whose reference tracks are fragmented.

## L12 Rewriting operators admit no row-level audit — UNRESOLVED_BY_DESIGN

For GPR_REWRITE and LINK_AND_SMOOTHING there is no row-subset intervention,
because withholding a row changes the fit and therefore the surviving
coordinates. The evaluated-state comparison remains available; the admission
decomposition does not. This is a structural result about what those operators
permit, not a gap in effort.

## L13 Rewriting does not imply a benchmark effect — CLOSED as a counterexample

OC-SORT's GPR stage rewrites 52 rows above 1e-6 px and moves all five reported
metrics by 0.0000. The counterexample bounds the framework's own claim: state
change is necessary, not sufficient, for a reported-score effect.

## L14 Eligibility rules exclude most released systems — OPEN

The documented-rule requirement is restrictive by design. On MOT20, one of seven
pre-specified configurations is eligible, five fail through detector-training
overlap, and one is unresolved. The audit therefore characterises the systems
whose post-processing is documented well enough to replay, which is a biased
subset of deployed practice.

## L15 Validation population sizes — OPEN

MOT17-val is 7 sequences and 2,652 frames; MOT20-val is 4 sequences and 4,463
frames; DanceTrack-val is 25 sequences and 25,508 frames. The MOT17 and MOT20
populations are small, and the bootstrap over 7 clusters is correspondingly
coarse.
""")

PH=["artifact","path_relative_to_project_root","sha256","kind","step","status","role_in_v6"]
B=""
prov=[
["v5 main manuscript","TPAMI_main_submission_v5.tex","628512b614c6fe32db1e2366dbb83fc677d79ca2b8c6193500c16e36519b2131","manuscript","v5","FROZEN, DO NOT MODIFY","source of reusable prose and of the v5 claim set"],
["v5 main PDF","TPAMI_main_submission_v5.pdf","5042473a6fdd16283e037bd1a06f6292dd6e85047b8b67f06465367a4c9431ef","manuscript","v5","FROZEN, DO NOT MODIFY","rendered reference"],
["v5 supplement","TPAMI_supplement_submission_v5.tex","aae6151e97398eef139583f016d86f281bfc614200a3b243e94e5949cf3a2cd0","manuscript","v5","FROZEN, DO NOT MODIFY","source of the MOT20 eligibility census and the skeleton material"],
["v5 supplement PDF","TPAMI_supplement_submission_v5.pdf","25150bd03993927a5f718ab881b51e3d1b79308cfe0489f761572f4f46e3aa46","manuscript","v5","FROZEN, DO NOT MODIFY","rendered reference"],
["Step 9 protocol lock","posthoc_composition_20261003/PROTOCOL_LOCK.md","d7e26ff602aa229c5a61d084cc2fe1540e0d3192099427b981c46ed4351a6e19","protocol","Step 9","FROZEN","MOT17 and MOT20 replay protocol"],
["Step 9 manifest","posthoc_composition_20261003/MANIFEST.sha256","829bd398f2ac264f7d393c4219e291406554dabe7503007cc231cfd964148b77","manifest","Step 9","VERIFIED 45/45","integrity of the released-deployment arm"],
["Step 9.1 manifest","posthoc_composition_20261003/step9_1/STEP9_1_MANIFEST.sha256","29bbafa712d2b75517f0890c18bcd84e8ef3b2a11ce62d3bd0e952ffbea4eae2","manifest","Step 9.1","VERIFIED 5/5","integrity of the Step 9 corrections"],
["Step 9.1 corrections","posthoc_composition_20261003/step9_1/STEP9_REPORT_CORRECTIONS.md","367460ed35323de5f82602e1e439a02218fb25ceb0a9b943f7854d4e48853730","report","Step 9.1","CURRENT","corrects the per-row replay phrasing; authoritative over the Step 9 prose"],
["Step 9.1 v5 claim map","posthoc_composition_20261003/step9_1/STEP9_V5_CLAIM_MAP.csv","c173084cacd99085b19ce47e4eaf94866871dc9ff01517e150868b4eb22d219b","table","Step 9.1","CURRENT","v5 claim to artifact mapping for the MOT17 and MOT20 arms"],
["D1A manifest","dancetrack_controlled_20261003/D1A_MANIFEST.sha256","db1bf820f3b4952470269bb4c0536c1626eb057cd8998bae837b0e12271c2642","manifest","D1A","VERIFIED 77/77","asset acquisition, hashes, evaluator verification, smoke tests"],
["DanceTrack protocol lock","dancetrack_controlled_20261003/protocol/DANCETRACK_CONTROLLED_PROTOCOL_LOCK.md","991a455fff6bd0ceffb879c50cee372822904c2d5fea07b1b4b131280d8514a9","protocol","D1A","FROZEN, 368 lines, 19 sections","authoritative protocol for the controlled DTI arm"],
["Track-id equivalence clarification","dancetrack_controlled_20261003/protocol/PROTOCOL_CLARIFICATION_01_TRACK_ID_EQUIVALENCE.md","b5e008fc8fc7dfc5f66d3252cb27c94f001d60bfcc42aed1dc22b5ef2d969feb","protocol","D1B","CURRENT","defines reproducibility up to bijective per-sequence relabelling and scopes STV invariance"],
["Acceleration equivalence audit","dancetrack_controlled_20261003/protocol/D1B_ACCELERATION_EQUIVALENCE_AUDIT.md","6756481a3b46f8d926551229d43224f2f46b4645b8ebec58f31220e17234b83b","report","D1B","CURRENT","records why batching and detector caching were rejected"],
["Common DTI operator","dancetrack_controlled_20261003/scripts/common_dti.py","e0f2289f7051225377455ac7033541c9dbb0113cff55b08be0b9b9e9a49315ea","code","D1A","FROZEN","the one operator applied to all four trackers; verbatim ByteTrack extraction"],
["D1B manifest","dancetrack_controlled_20261003/D1B_MANIFEST.sha256","334979c51d3067b98ffd41b322277545d14edaa18465a9256d5eabb0ba14caef","manifest","D1B","VERIFIED 428/428","integrity of the controlled DTI arm"],
["D1B.1 manifest","dancetrack_controlled_20261003/step_d1b_1/D1B1_MANIFEST.sha256","3e2638e7d3c2111f6c5c849ecd5e84d97932b44f8b2ae69539b5cc48f889f489","manifest","D1B.1","VERIFIED 29/29","integrity of the DanceTrack correction audit"],
["D1B.1 report","dancetrack_controlled_20261003/step_d1b_1/D1B1_REPORT.md","364b509870998e904f77fb291a59b79fc7d91b3b44d2e22ecc94243501c01c38","report","D1B.1","CURRENT","restores the MOT20 gate-stable figure, validates REFERENCE_ABSENT, recomputes the 7 crossings"],
["GSI protocol lock","dancetrack_controlled_20261003/gsi_protocol_20261004/GSI_PROTOCOL_LOCK.md","6ac1b00bd6ef37bfc5c5b7bc416c33ad46c4735d2f0c910cb9c42ea8f31484b8","protocol","D2A","FROZEN","authoritative protocol for the controlled GSI arm"],
["GSI protocol manifest","dancetrack_controlled_20261003/gsi_protocol_20261004/GSI_PROTOCOL_MANIFEST.sha256","bd22822b7fe8846de45af553f6232cb1b92c89039520d25df75b3dd106b038fe","manifest","D2A","VERIFIED 20/20","integrity of the GSI protocol freeze"],
["D2B manifest","dancetrack_controlled_20261003/gsi_exec_20261004/D2B_MANIFEST.sha256","6276bff16669a585fbf94cf6eb71b6f3139e1a6ed6fa251eb1d722a6770d9a2f","manifest","D2B","VERIFIED 285/285","integrity of the GSI execution"],
["D2B report","dancetrack_controlled_20261003/gsi_exec_20261004/D2B_REPORT.md","91a848d04a647bcc3ce1471f56640dfd307aee4558ffac6b22674e24703313dd","report","D2B","CURRENT, superseded in interpretation by D2C","GSI execution results"],
["Final defence manifest","dancetrack_controlled_20261003/final_defense_20261004/FINAL_MANIFEST.sha256","c2fc4b5f7230744d858b3f08a1937976e2a3b2a3c9af168deeaf2e2be887b827","manifest","D2C and D1B.2","VERIFIED 241/241","integrity of the final experimental defence pass"],
["Final defence report","dancetrack_controlled_20261003/final_defense_20261004/FINAL_EXPERIMENTAL_DEFENSE_REPORT.md","6ebfc8e8ed85b168aee549c6a4dd5d6020a16a3ed79d658055b0e8564248e61e","report","D2C and D1B.2","CURRENT, post-correction","GSI stage decomposition, row-local support, unified margins"],
["GPR rewrite recount","dancetrack_controlled_20261003/final_defense_20261004/FINAL_gpr_rewrite_recount.csv","1653eea2b8405ea81c9e7c2a55b2ebfaa8f1a9474bc482d4d986f487a4263dd0","table","final correction audit","CURRENT, authoritative","resolves 212 against 52; the 52-row figure stands"],
["Evidence architecture","dancetrack_controlled_20261003/final_defense_20261004/FINAL_evidence_architecture.csv","8494510b3f2c3a0402c6911b24e49eef1b418eed2133408f91f4ecf626b7b4e7","table","D2C","CURRENT","basis for 06_EVIDENCE_ARCHITECTURE.csv"],
["v6 claim guardrails","dancetrack_controlled_20261003/final_defense_20261004/FINAL_v6_claim_guardrails.csv","161288ff77288dbfc04225411a75e872e9acaeb7aed255ea06710c8943b6f5ff","table","D2C","CURRENT","basis for 04_FORBIDDEN_OR_OBSOLETE_CLAIMS.md"],
["Unified pairwise margins","dancetrack_controlled_20261003/final_defense_20261004/FINAL_unified_pairwise_margins.csv","b50ef556328288a7645ddecfd23d326dd1de79a0453a730cc9d428951f5fc57c","table","D2C","CURRENT","one schema for all ordering cells across arms"],
["Three-tracker sensitivity","dancetrack_controlled_20261003/final_defense_20261004/FINAL_three_tracker_provenance_sensitivity.csv","a8afe91c3bfb592d4b0bc1d8fe6d9df647549e6919f3eba8eb3d288882edae6a","table","D2C","CURRENT","checkpoint-provenance sensitivity subset"],
["WSOL style reference","reference/WSOL_TPAMI_2023.pdf","7623cb9d8a83807cb2981f44171626a2498f32d9a425c4dd788d97689e82874b","style reference","Sec. 18","STYLE ONLY, NOT A SCIENTIFIC SOURCE","human scientific-writing reference"],
]
wc("09_PROVENANCE_LEDGER.csv",PH,prov)
