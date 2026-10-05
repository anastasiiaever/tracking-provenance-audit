> **How to use a fact packet.** Every number below is traceable to
> `05_NUMERIC_LEDGER.csv` and from there to an artifact. Write prose from these
> facts; do not add a number that is not here. If a sentence needs a fact that is
> absent, write `[FACT NEEDED]` and stop. Read
> `04_FORBIDDEN_OR_OBSOLETE_CLAIMS.md` and `30_UNSLOPPING_RULES_FOR_CODEX.md`
> before writing.

# DISCUSSION FACT PACKET

v5's Discussion is five paragraphs and its structure holds. Keep the order; change
what the evidence now supports.

## 1. Composition and metric change answer different questions — KEEP, EXTEND

v5's point: the non-admitted fraction of the synthesized set describes what the
operator added; its fraction of the submitted set describes their share of the
benchmark input; a metric change measures the net effect on evaluation. A score
gain alone does not describe the composition of the added rows.

New evidence: on MOT17 all 25 deltas were positive, which left open the reading
that non-admission and metric gain travel together. Under one common operator on
DanceTrack, 12 deltas are positive and 8 negative: OC-SORT and Deep-OC-SORT rise
on all five metrics, while ByteTrack and Hybrid-SORT fall on four of five and
rise only on AssA. Substantial non-admission occurs in both directions.

Both fractions are now available on two populations with different operators, so
state the two-denominator point with the DanceTrack inserted-fraction numbers,
3.79 to 6.93 % of the submitted file against 42.03 to 68.46 % of the added set.

## 2. Comparisons depend on the evaluated state — KEEP, CORRECT

v5's point stands: admission composition does not determine which pairwise
comparisons change, and a small margin permits a reversal without predicting one.

v5 supported it with an ordering coincidence: Hybrid-SORT had the highest
non-admitted fraction and appeared in four of five changed comparisons,
Deep-OC-SORT the lowest and three. **That coincidence does not replicate.** On
DanceTrack, ByteTrack has the highest non-admitted fraction, 68.46 %, and the
fewest appearances in crossing cells, 2; Deep-OC-SORT has the lowest, 42.03 %,
and four.

This strengthens v5's own conclusion rather than weakening it, and it should be
reported that way: the second population shows the composition-to-ordering
association was a small-sample coincidence, which is precisely why composition
cannot be read off a score change or vice versa.

Margin-size facts for both populations:

- MOT17: crossing cells' initial absolute margins 0.5104 to 1.4567; 17 of 45
  unchanged cells at or below 1.4567; smallest unchanged 0.1869.
- DanceTrack: crossing cells 0.6581 to 2.2203; 6 of 23 unchanged cells at or
  below 2.2203; smallest unchanged 0.2170.

## 3. Eligibility belongs to a released configuration — KEEP

v5's paragraph is correct and needs no new evidence. The MOT20 census is its
support: 1 eligible of 7, 5 failing through detector-training overlap. Keep the
sentence that running an ablation on MOT20 validation frames does not make them
held out if the detector checkpoint was trained on them.

Add one sentence from the DanceTrack arm: training-split disjointness and
selection provenance are separate questions, and on DanceTrack the first is
satisfied for all four trackers while the second is unresolved for all four at the
hyperparameter level. A single "held out" label would hide that.

## 4. Reporting prediction provenance — KEEP

v5's recommendation stands: a tracking release should retain raw output,
submitted output and the transformation settings together. Related practices:
datasheets, the BIAS guideline, model cards; `ghosh2026evalcards` and
`maierhein2024metrics` are in the bibliography and belong here too.

The DanceTrack arm adds a concrete argument for it. Holding the operator fixed
across four trackers required extracting the operator from source and verifying
that the extraction hashes identically across the three repositories that ship it.
That work would have been unnecessary had the releases recorded their
transformation settings alongside the submitted file.

## 5. What the arms do and do not share — REWRITE

v5's final paragraph contrasted the tracking arm with the skeleton arm. The
skeleton arm leaves the narrative, so this paragraph is rewritten around the two
contrasts v6 actually has.

**Contrast one: which audit an operator permits.** Row-additive transitions admit
a row-level decomposition and a withheld-row diagnostic state. Transitions that
rewrite surviving rows admit neither, because withholding a row changes the fit.
This is a structural property, so a reader can determine it from the operator
without running anything.

**Contrast two, the boundary case.** OC-SORT's GPR stage rewrites 52 rows above
1e-6 px and moves all five reported metrics by 0.0000. This bounds the paper's own
claim: a change to the evaluated state is necessary for a reported-score effect
and is not sufficient. A paper that argued only that post-processing changes the
state would be making a weaker point than this one, and the counterexample is what
shows the difference.

## 6. What admission does not measure — NEW PARAGRAPH

The row-local support measurement belongs in the Discussion as well as the
Results, because it is the limit of the diagnostic the paper proposes. Between
62.04 and 73.54 % of non-admitted DanceTrack rows reach maximum IoU 0.5 against
some scoreable identity, and 3,448 of 3,451 TARGET_REFERENCE_ABSENT rows have
another identity overlapping the box while 0 of 3,451 have the intended one.
Admission asks whether the reference supports the row's intended identity at that
frame. On a population of heavily overlapping targets, that question and "is there
a target here" come apart almost completely.

## Forbidden in the Discussion

Any causal statement from non-admission to metric change; "robust"; "significant";
"independent confirmation"; "breadth is closed"; a closing paragraph that
synthesises the preceding ones. The Discussion should end on the strongest
remaining substantive point, not on a summary.
