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
