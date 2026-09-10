# Estimands and eligibility

Two questions in this repository look similar and are not the same. Keeping them
apart is most of what the audit does.

## The four states

| state | what it is |
|---|---|
| `R0` | what the tracker observed |
| `R1` | `R0` plus only those synthesized rows the reference supports |
| `R2` | what was submitted — `R0` plus every synthesized row |
| `S0` / `S2` | the pre- and post-operator states of a transformation with no row-additive decomposition |

`R0 ⊆ R1 ⊆ R2` by canonical row identity `(sequence, frame, track_id)`, and
`states.build_R1` asserts it.

`R1` is a **diagnostic**, not a deployable correction: it is built with knowledge
of the ground truth, which a deployed filter would not have. The frozen records
label it `gt_informed_diagnostic` and `non_deployable`.

## When R1 does not exist

Four of the eight census pipelines apply an operator that rewrites values its own
fit consumes. Removing a subset of generated rows would change the fit itself, so
a row-subset decomposition is not defined. The audit reports
`STRUCTURALLY_UNDEFINED` and manufactures nothing:

- **GPR rewrite** — the regression consumes the interpolated rows as its input.
- **Link plus smoothing** — smoothing refits every row of every track, so removing
  a subset alters the surviving rows too.

This is why StrongSORT++ appears in `results/mot17/strongsort_decomposition.csv`
as `S0`/`S2` only, and why OC-SORT-GPR is excluded from the ordering matrix
rather than given an invented `R0`/`R2` reading.

## Admission (STV)

For each synthesized row, take its two bracketing `R0` observations. Under a
frozen per-frame one-to-one assignment against scoreable ground truth — computed
on `R0` *before* any synthesized row exists, then frozen — do both anchors
resolve to the same reference identity, and is that identity present at the
target frame?

Four classes, applied in this priority order, exhaustive and mutually exclusive:

| class | meaning |
|---|---|
| `ANCHOR_UNMATCHED` | at least one anchor matched no scoreable reference |
| `ANCHOR_ID_MISMATCH` | the anchors resolve to different reference identities |
| `TARGET_REFERENCE_ABSENT` | the agreed identity is absent at the target frame |
| `SEMANTICALLY_ADMITTED` | admitted under the frozen rule |

Two properties are load-bearing:

- **Gate before assignment.** The IoU gate is a hard admissibility mask applied
  before the Hungarian assignment, not a filter afterwards. Ineligible pairs
  cannot be selected at all.
- **One class only.** `stv.partition_counts` asserts the partition is exact. The
  released tables are checked against this in `tests/test_release_integrity.py`.

### What the classes do and do not license

`ANCHOR_ID_MISMATCH` is the only class that licenses the phrase *"the two anchors
resolve, under the frozen matcher, to different ground-truth identities"*.

`ANCHOR_UNMATCHED` is **non-admission under a matching rule**. It is not a
demonstrated semantic error and not a false-positive determination. A row can be
unmatched because the tracker was wrong, or because the matcher was strict, and
this evidence does not separate those.

STV is a reference-side diagnostic. It is not a tracking metric and not a
proposed replacement for one.

## Materiality

A secondary, descriptive classification only:

```
STV_COMPOSITION_MATERIAL  iff  non_admitted / synthesized >= 0.10
```

The denominator is synthesized rows because the criterion concerns the
composition of what the post-processor produced. The corresponding fraction of
*all* submitted rows is always reported alongside, so a large conditional fraction
cannot be read as a submission-wide effect — for the executed MOT20 cell those
two numbers are 25.1% and 1.55%.

The threshold was frozen in advance and carries no significance or generalization
claim. `materiality.classify` returns `status: DESCRIPTIVE` on every path.

## Ordering

Two deployments are comparable only within the same dataset, the same frozen
population, the same evaluator configuration and the same metric. Every eligible
pair is reported on every metric at both `R0` and `R2` — all of them, not only
those that change.

Transitions: `UNCHANGED`, `FLIP`, `TIE_CREATED`, `TIE_BROKEN`. A metric that does
not exist for a pair is reported as `METRIC_NOT_AVAILABLE` and never imputed.

**The estimand warning matters here.** These are *system-level deployment*
orderings. A difference between two pipelines cannot be attributed to the
post-processing family alone, because the tracker and detector systems also
differ. Within-pipeline `R0 → R2` deltas and between-pipeline ordering are
separate estimands and are reported separately.

## MOT20 eligibility

Seven cells were pre-specified before any MOT17 execution. The question asked of
each was not "does it run" but "is the estimand even available" — for a held-out
half-train estimand, a detector trained on the evaluation frames makes the
comparison unavailable regardless of what it scores.

Six cells were blocked. Five for confirmed or inherited evaluation leakage, one
mixed. `results/mot20/eligibility.csv` carries the evidence field behind each
verdict, not just the verdict.

One cell — Deep-OC-SORT — was the only one classified `NO_KNOWN_EVAL_LEAKAGE`,
and is the one that was executed. Three things are recorded about that, and
`scripts/verify_mot20_eligibility.py` checks all three:

1. no checkpoint was substituted to rescue any blocked cell (`0`);
2. no MOT20 outcome existed when the cell was selected;
3. MOT17 outcomes did not choose the MOT20 commands.

The frozen records state the prohibition directly: this selection must **not** be
described as a prospectively selected winner, as outcome-based selection, or as a
best-performing method. It is the only cell whose estimand was available.
