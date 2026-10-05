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
