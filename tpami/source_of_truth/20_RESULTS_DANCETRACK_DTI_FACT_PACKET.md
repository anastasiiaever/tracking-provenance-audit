> **How to use a fact packet.** Every number below is traceable to
> `05_NUMERIC_LEDGER.csv` and from there to an artifact. Write prose from these
> facts; do not add a number that is not here. If a sentence needs a fact that is
> absent, write `[FACT NEEDED]` and stop. Read
> `04_FORBIDDEN_OR_OBSOLETE_CLAIMS.md` and `30_UNSLOPPING_RULES_FOR_CODEX.md`
> before writing.

# RESULTS FACT PACKET: DANCETRACK, ONE COMMON OPERATOR, FOUR TRACKERS

Population: DanceTrack validation split, 25 sequences, 25,508 frames,
225,148 scoreable ground-truth rows, 273 ground-truth tracks.
Evidence type: controlled intervention. The operator is ours. The protocol was
frozen before any result was inspected; the protocol lock is
`991a455fff6bd0ceffb879c50cee372822904c2d5fea07b1b4b131280d8514a9`.
Authoritative artifacts: `D1B_MANIFEST.sha256` =
`334979c51d3067b98ffd41b322277545d14edaa18465a9256d5eabb0ba14caef`, 428 of 428,
with the D1B.1 audit, `3e2638e7…`, 29 of 29.

## What the control buys

One operator, `n_min=25` and `n_dti=20`, identical for all four trackers, and one
shared detector. Differences between trackers therefore cannot be attributed to
differences in post-processing. The cost is that the four R0 states share a
detector and are more similar to one another than four independently trained
systems would be.

## Composition at the primary gate, 0.50

| tracker | R0 | R2 | inserted | % of R2 | U | ID | ABS | ADM | non-adm | % | gate-stable | % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ByteTrack | 216,310 | 224,821 | 8,511 | 3.786 | 3,659 | 1,642 | 526 | 2,684 | 5,827 | 68.46 | 5,330 | 62.62 |
| OC-SORT | 202,787 | 217,890 | 15,103 | 6.931 | 2,338 | 3,817 | 1,007 | 7,941 | 7,162 | 47.42 | 6,547 | 43.35 |
| Deep-OC-SORT | 203,149 | 217,171 | 14,022 | 6.457 | 2,015 | 2,790 | 1,089 | 8,128 | 5,894 | 42.03 | 5,335 | 38.05 |
| Hybrid-SORT | 215,393 | 227,851 | 12,458 | 5.468 | 5,206 | 1,941 | 829 | 4,482 | 7,976 | 64.02 | 7,139 | 57.30 |

Ranges: inserted 3.79 to 6.93 % of the submitted file; non-admission 42.03 to
68.46 %; gate-stable 38.05 to 62.62 %.

The ABS column is non-zero here and zero on MOT17 and MOT20. That contrast is a
result and carries its own subsection; see below.

## Metric change goes both ways

20 cells: 12 positive, 0 zero, 8 negative. **OC-SORT and Deep-OC-SORT** rise on
all five metrics. **ByteTrack and Hybrid-SORT** fall on four of five and rise only
on AssA. Per tracker, in the order HOTA, DetA, AssA, IDF1, MOTA:

| tracker | HOTA | DetA | AssA | IDF1 | MOTA |
|---|---|---|---|---|---|
| ByteTrack | -0.0836 | -0.4602 | **+0.0991** | -0.1104 | -0.5903 |
| OC-SORT | +0.6587 | +1.3324 | +0.3129 | +0.4493 | +2.4491 |
| Deep-OC-SORT | +0.6786 | +1.4348 | +0.2434 | +0.4269 | +2.6414 |
| Hybrid-SORT | -0.1897 | -0.5071 | **+0.0242** | -0.1841 | -0.1381 |

The two trackers that fall are the two with the *highest* non-admitted fractions,
68.46 % and 64.02 %, and the two that rise are the two with the lowest, 47.42 %
and 42.03 %. State that as a co-occurrence in this four-tracker sample, never as
a mechanism.

This is the arm's most useful single fact. On MOT17 every delta was positive, so a
reader could suppose that non-admission and metric gain travel together. Under a
common operator they do not: substantial non-admission occurs whether the operator
improves or degrades the reported metrics.

## Ordering

30 exhaustive pairwise metric cells, 7 cross zero, all surviving 3-decimal and
2-decimal reporting:

| pair | metric | R0 margin | R2 margin | P(sign differs) |
|---|---|---|---|---|
| ByteTrack − Deep-OC-SORT | MOTA | +0.7297 | −2.5019 | 0.8454 |
| ByteTrack − OC-SORT | MOTA | +1.0131 | −2.0262 | 0.9365 |
| Deep-OC-SORT − Hybrid-SORT | HOTA | −0.6581 | +0.2102 | 0.3240 |
| Deep-OC-SORT − Hybrid-SORT | DetA | −1.2302 | +0.7117 | 0.9289 |
| Deep-OC-SORT − Hybrid-SORT | MOTA | −1.9369 | +0.8426 | 0.9013 |
| OC-SORT − Hybrid-SORT | DetA | −1.4832 | +0.3562 | 0.7222 |
| OC-SORT − Hybrid-SORT | MOTA | −2.2203 | +0.3669 | 0.6925 |

Crossing cells' initial absolute margins: 0.6581 to 2.2203. Of the 23 unchanged
cells, 6 had initial margins at or below 2.2203, the smallest 0.2170.

Appearances in crossing cells: Hybrid-SORT 5, Deep-OC-SORT 4, OC-SORT 3,
ByteTrack 2.

**The MOT17 ordering coincidence does not replicate.** On MOT17 the deployment
with the highest non-admitted fraction appeared in the most crossing cells. Here
ByteTrack has the highest non-admitted fraction, 68.46 %, and the fewest
appearances, 2; Deep-OC-SORT has the lowest, 42.03 %, and four. Report this
plainly. It is the cleanest available evidence that composition does not determine
which comparisons change, and it closes off a reading that the MOT17 numbers
alone would have left open.

## Parameter sensitivity

At `n_min=30`, `n_dti=20`: non-admission differs from the primary setting by at
most 0.42 percentage points and any metric by at most 0.0422 points. The
composition conclusion does not depend on the choice between 25 and 30.

## Provenance

Training-split disjointness holds for all four trackers. Deep-OC-SORT's
checkpoint-selection provenance is UNRESOLVED and hyperparameter-selection
provenance is UNRESOLVED for all four. The three-tracker sensitivity subset, which
drops Deep-OC-SORT, has 15 cells of which 3 cross zero. Deep-OC-SORT is included
in the primary analysis; the subset is a sensitivity check, not an exclusion.

## Reproducibility

The smoke-against-full comparison initially failed on absolute tracker ids. Cause:
`BaseTrack._count` is a class attribute that upstream never resets, giving the
14th sequence a constant +424 offset. An isolated one-sequence rerun was
byte-identical to the smoke output. Equivalence is defined up to a bijective
per-sequence relabelling and documented in
`PROTOCOL_CLARIFICATION_01_TRACK_ID_EQUIVALENCE.md`,
`b5e008fc8fc7dfc5f66d3252cb27c94f001d60bfcc42aed1dc22b5ef2d969feb`.

If this appears in the paper, it belongs in the supplement, and it should be
stated as what it was: the validator demanded more than reproducibility requires.

## Where the reference is silent: TARGET_REFERENCE_ABSENT

Counts: 3,451 rows at the primary gate across the four trackers; 16,019 rows
across four trackers and all five gates. The class is empty on MOT17 and MOT20.

The mechanism is established positively, not inferred from the absence of an
alternative:

- All 16,019 rows lie strictly inside a gap in the ground-truth track's own
  observed frame set. Not most of them; all of them.
- An independently written predicate agreed with the frozen classifier on
  250,470 of 250,470 decisions.
- DanceTrack's scoreable ground truth is fragmented: 209 of 273 tracks, 76.6 %,
  have at least one interior gap, 1,370 gaps in total, 15,326 missing frame-slots.
  MOT17's has none across 339 tracks.
- Corroborated independently: the evaluator's own `Frag = 1370` from the D1A
  sanity check matches the gap count.
- For 9,047 of the 16,019 rows the identity is annotated at an immediately
  adjacent frame, so the gap is often a single missing slot rather than a long
  absence.

What this class means, stated carefully: the anchors resolve to one reference
identity and that identity has no scoreable row at the synthesized frame. The
reference does not state where the target is. This is a property of the
annotation, so the class will appear on any population whose reference tracks are
fragmented, and its absence on MOT17 is a property of MOT17's annotation rather
than of MOT17's trackers.

Do not write that these rows are false positives, and do not write that there is
no ground-truth geometry near them. See the next section.

## Row-local geometric support: what admission does and does not measure

This measurement exists to bound the framework's own diagnostic, and it should be
reported as a result rather than as a defence.

| quantity | value |
|---|---|
| ADMITTED rows reaching maximum IoU ≥ 0.5 against some scoreable identity | 97.392 to 98.2151 % |
| ADMITTED rows below maximum IoU 0.5 | 1.7849 to 2.6080 % |
| non-admitted rows reaching maximum IoU ≥ 0.5 | 62.0388 to 73.5409 % |
| REFERENCE_ABSENT rows whose intended reference identity is present | 0 of 3,451 |
| REFERENCE_ABSENT rows with some other identity overlapping the box | 3,448 of 3,451 |

Two conclusions follow, and both belong in the text:

1. Non-admission is not geometric implausibility. Between 62 and 74 % of
   non-admitted rows sit on top of a scoreable target well enough to pass an
   IoU-0.5 test. Admission asks whether the reference supports the row's intended
   identity at that frame, which is a different question.
2. "The intended reference identity is absent" and "no ground truth is nearby"
   are not the same statement. On DanceTrack, where dancers overlap heavily, the
   two come apart almost completely: 0 of 3,451 against 3,448 of 3,451.

Admission is also imperfect in the other direction: a small but non-zero fraction
of admitted rows has weak local overlap. Reporting only the non-admitted side
would misrepresent the measurement.
