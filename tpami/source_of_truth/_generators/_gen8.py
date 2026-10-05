import os
V="<AUDIT_ROOT>/V6_SOURCE_OF_TRUTH"
def w(n,s): open(os.path.join(V,n),"w").write(s.lstrip("\n")); print("  wrote",n)

HEAD = """
> **How to use a fact packet.** Every number below is traceable to
> `05_NUMERIC_LEDGER.csv` and from there to an artifact. Write prose from these
> facts; do not add a number that is not here. If a sentence needs a fact that is
> absent, write `[FACT NEEDED]` and stop. Read
> `04_FORBIDDEN_OR_OBSOLETE_CLAIMS.md` and `30_UNSLOPPING_RULES_FOR_CODEX.md`
> before writing.
"""

w("16_ABSTRACT_FACT_PACKET.md", HEAD + r"""
# ABSTRACT FACT PACKET

Target: one paragraph, roughly 170 to 200 words. The WSOL reference abstract is
179 words in 8 sentences with no numerals; see `29_WSOL_STYLE_OBSERVATIONS.md`.
This paper's abstract should carry a small number of numerals, because the
quantities are the result, but it does not need more than three or four.

## The one statement the abstract exists to make

A benchmark score characterises an evaluated output state, not a tracker in
isolation. For several widely used trackers the submitted file contains rows that
the tracker did not produce, and which audit a reader can perform on that file
depends on the structure of the transition that produced it.

## Facts available, in descending order of priority

1. Five released MOT17 deployments add rows that fail scoreable-target admission
   in 28.92 to 49.02 % of the added set at the primary gate, and in 23.45 to
   43.90 % at every gate in the sweep.
2. All 25 metric deltas are positive; 5 of the 50 exhaustive pairwise metric
   cells change sign, and all five survive 2-decimal reporting.
3. Under one common operator applied by us to four trackers on DanceTrack,
   non-admission is 42.03 to 68.46 %, 7 of 30 pairwise cells change sign, and the
   metric deltas go both ways: 12 positive and 8 negative.
4. A second operator family reproduces the same 7 cells, but its own
   interpolation stage accounts for all of them.
5. One released operator rewrites the evaluated state and moves all five reported
   metrics by 0.0000.

## Sentence-level guidance

- Open on the practice, not on the field. The first sentence should let a reader
  who knows MOTChallenge recognise the thing being audited.
- The four-class admission decomposition needs naming once, without listing all
  four classes in the abstract.
- The abstract must not promise generality. Two populations, four controlled
  trackers, two operator families.
- Do not write "we propose a framework" as the opening move; the framework exists
  to make a measurement possible, and the measurement is the result.
- Do not end on an outlook sentence. The last sentence should be the strongest
  remaining fact, most likely the boundary case or the bidirectional metric
  result.

## Forbidden in the abstract

"significant", "robust", "independent confirmation", "universally", "we are the
first", any count presented as a rate, and the word "reveal".
""")

w("17_INTRO_FACT_PACKET.md", HEAD + r"""
# INTRODUCTION FACT PACKET

Target: 5 to 7 paragraphs. v5's introduction is lines 129 to 156 and is being
rewritten, because the contribution set changed.

## Opening

Open on the concrete practice. The specific, checkable facts available for an
opening paragraph:

- The MOTChallenge submission format is ten columns per row and carries no field
  distinguishing a tracker-produced row from one added afterwards
  (`dendorfer2021motchallenge`; TrackEval, `luiten2020trackeval`).
- ByteTrack, OC-SORT, Deep-OC-SORT, BoT-SORT, Hybrid-SORT and StrongSORT++ each
  ship an offline post-processing stage, and five of them apply it on the path
  that produces the submitted file.
- On MOT17-val, each deployment adds 2,072 to 3,023 rows, 12,767 synthesized rows
  in total across the five deployments. Of those added rows, 1,224 to 2,104 per
  deployment are admitted; the two ranges are different quantities and must not
  be combined into one.

## The problem statement

Two things are true at once and the introduction must hold both:

- the added rows are not errors, and the audit does not claim they are;
- the score that is reported and compared is computed on a file that contains
  them.

So the question is not whether post-processing is legitimate. It is what a reader
of a benchmark table can determine about the state that table scored.

## What the paper contributes

1. A definition of the evaluated state and of scoreable-target admission, with
   the four classes and their exact partition.
2. A statement of which audit each operator structure permits: row-additive
   transitions admit a row-level decomposition and a withheld-row diagnostic
   state; transitions that rewrite surviving rows admit neither.
3. An estimand-eligibility condition for when a held-out comparison is available
   from a released configuration, applied as a census: on MOT20, 1 of 7
   pre-specified configurations is eligible, 5 fail through detector-training
   overlap, 1 is unresolved.
4. A released-deployment audit on MOT17-val, 7 sequences and 2,652 frames, and the
   eligible MOT20 cell, 4 sequences and 4,463 frames.
5. A controlled audit on DanceTrack-val, 25 sequences and 25,508 frames, in which
   one operator is applied by us to four trackers, so tracker differences cannot
   be attributed to differences in post-processing.
6. Two bounding results: an operator that rewrites the state and moves no metric,
   and a measurement showing that non-admission does not mean geometric
   implausibility.

## The honest framing of the second population

The DanceTrack arm is ours, not an author's. Say so in the introduction, not only
in the limitations. The sentence a reviewer needs is that no released DanceTrack
submission is audited and that the arm exists to hold the operator fixed.

## What must not appear in the introduction

- a contribution list that is then restated at the head of every results section;
- "to the best of our knowledge";
- a claim that the ordering results are statistically significant;
- the words "independent confirmation" for the GSI arm;
- a general observation about the growth of the tracking literature.

## Available numbers

See `05_NUMERIC_LEDGER.csv`. For the introduction the useful ones are the
population sizes (7 / 2,652; 4 / 4,463; 25 / 25,508), the synthesized totals
(12,767; 34,814; 8,511 to 15,103), the non-admission ranges, and the crossing
counts with their denominators (5 of 50; 7 of 30).
""")

w("18_METHOD_FACT_PACKET.md", HEAD + r"""
# METHOD FACT PACKET

All definitions come from `07_METHOD_DEFINITIONS.md`. That file is normative; this
one says what the Method section must make the reader able to do.

## After reading the Method, a reader must be able to

1. say what R0, R1 and R2 are, and why R1 does not exist for every operator;
2. compute the four admission classes themselves from a submission file, its
   pre-operator file and the ground truth;
3. state what admission does not measure;
4. decide, for a new operator, which of the three audits it permits;
5. check the eligibility of a released configuration for a held-out comparison;
6. reproduce the bootstrap, including the resampling unit and the seed.

## Must be stated explicitly, because it is the most misreadable part

Admission is evaluated from the anchors and from the availability of the
anchor-resolved reference identity. The synthesized row's own coordinates never
enter the predicate. Therefore non-admission is a statement about reference
support, not about geometric plausibility, and TARGET_REFERENCE_ABSENT is a
statement about the reference being silent, not about the tracker being wrong.

Put this in the Method, in the subsection that defines the classes. Do not defer
it to the Discussion.

## Must be stated once and not repeated

- The classes are evaluated as an `if`/`elif` chain in the given priority order
  and partition the synthesized set exactly; counts sum to the synthesized total
  in every table.
- Scoreable ground truth is `mark != 0 AND class == 1`, matching the evaluator's
  own preprocessing.
- The primary gate is 0.50 and the sweep is 0.30 to 0.70 in steps of 0.10;
  gate-stable non-admission is non-admission at every gate and is therefore a
  conservative lower bound.
- R1 is realised by zeroing similarity before assignment, so a withheld row can
  neither match nor displace a match.
- DetA and AssA are factors of HOTA.

## The structural subsection, new in the main text

Table T2 from `06_EVIDENCE_ARCHITECTURE.csv` goes here. The text around it must
make the following four transition types distinguishable, with one audited
example each:

| transition | keys | surviving content | example |
|---|---|---|---|
| row-additive | grow | unchanged | linear DTI, five released deployments and our DanceTrack arm |
| key-additive, content-rewriting | grow | changed | StrongSORT GSI, released and in our DanceTrack arm |
| rewrite-only | unchanged | changed | OC-SORT's GPR stage |
| identity-remapping | may shrink | identity changed | StrongSORT++ AFLink |

The reason no R1 exists for the last three is one sentence: withholding a row
changes the fit, so the surviving rows would change too, and the withheld-row
state is therefore not a subset operation on the submitted file. The released
`states.py` records this in `r1_status_for_non_row_additive`.

## The controlled-arm subsection

Facts to state:

- one operator for four trackers: `dti` and `write_results_score` extracted
  verbatim from ByteTrack's `tools/interpolation.py` at commit `d1bf0191`, with
  `n_min=25`, `n_dti=20`;
- the extracted code hashes identically across the three repositories that ship
  it, so "the same operator" is a checkable statement, not an assertion;
- sensitivity at `n_min=30`: non-admission differs by at most 0.42 points and any
  metric by at most 0.0422;
- the second operator: StrongSORT's `GSInterpolation` with `interval=20`,
  `tau=10`, the values hardcoded at its only upstream call site; AFLink not
  applied;
- one shared detector across the four trackers, which removes detector variation
  as a confound and removes detector diversity at the same time.

## The reproducibility subsection

`BaseTrack._count` is a class attribute and `clear_count()` is never called
upstream, so running a subset of sequences shifts every tracker id by a constant.
Equivalence is therefore defined up to a bijective per-sequence relabelling, with
exact equality of frames, boxes and the track partition and no splits, merges,
missing or extra rows.

State the invariances at the precision at which they were verified, and no
further:

- TrackEval is invariant to arbitrary within-sequence bijective relabelling;
- DTI is invariant modulo the corresponding relabelling;
- STV is verified invariant for the observed order-preserving constant shift
  +424; arbitrary non-order-preserving permutations are not guaranteed, because
  `assign_reference` sorts predictions by tracker id;
- no downstream analysis joins absolute tracker ids across sequences.

## The statistics subsection

- Resampling unit: the sequence cluster, 7 on MOT17, 25 on DanceTrack. Justified
  by the purity of TrackEval's `combine_sequences`, which recomputes pooled
  metrics from per-sequence accumulators without reference to other sequences.
- 10,000 draws, seed 20261003, multiplicity carried by distinct dictionary keys
  `"<sequence>#<slot>"`. Index matrices are hashed.
- Percentile intervals are descriptive. No hypothesis is tested, no p-value is
  computed, and `P(sign differs)` is a bootstrap frequency.
- Sequences are not claimed to be independent.
- The pairwise matrices are exhaustive and their cells are dependent. Say this in
  the Method, once, so no later section has to apologise for it.
""")

w("19_RESULTS_MOT17_FACT_PACKET.md", HEAD + r"""
# RESULTS FACT PACKET: MOT17 RELEASED DEPLOYMENTS

Population: MOT17 validation half, 7 sequences, 2,652 frames.
Evidence type: released-deployment audit, pre-specified, retrospective.
Authoritative artifacts: `posthoc_composition_20261003/results/` with
`MANIFEST.sha256` = `829bd398f2ac264f7d393c4219e291406554dabe7503007cc231cfd964148b77`,
45 of 45 verified, plus the Step 9.1 corrections.

## Composition at the primary gate, 0.50

| deployment | synthesized | U | ID | ABS | ADM | non-admitted | % | gate-stable | % |
|---|---|---|---|---|---|---|---|---|---|
| Deep-OC-SORT | 2,960 | 570 | 286 | 0 | 2,104 | 856 | 28.9189 | 694 | 23.4459 |
| OC-SORT | 2,622 | 408 | 375 | 0 | 1,839 | 783 | 29.8627 | 666 | 25.4005 |
| BoT-SORT | 2,090 | 576 | 227 | 0 | 1,287 | 803 | 38.4211 | 634 | 30.3349 |
| ByteTrack | 2,072 | 604 | 244 | 0 | 1,224 | 848 | 40.9266 | 694 | 33.4942 |
| Hybrid-SORT | 3,023 | 1,266 | 216 | 0 | 1,541 | 1,482 | 49.0241 | 1,327 | 43.8968 |

Totals: 12,767 synthesized rows across the five deployments.
Ranges, each with its own quantity named: synthesized rows per deployment 2,072
to 3,023; admitted rows per deployment 1,224 to 2,104; non-admission 28.92 to
49.02 %; gate-stable non-admission 23.45 to 43.90 %.

The ABS column is zero for every deployment at every gate in the sweep. This is
not a null result to pass over: it is the fact that makes the DanceTrack ABS
column meaningful, and the reason is the reference, not the tracker. MOT17's
scoreable ground truth has no interior gaps in any of its 339 tracks.

## Metric change

All 25 cells, five deployments by five metrics, are positive from R0 to R2.
Values per state are in v5 Table 3 and in the frozen detailed evaluator output.

## Ordering

50 exhaustive pairwise metric cells, 5 cross zero. Named:

| pair | metric | R0 margin | R2 margin | 3dp | 2dp | P(sign differs) |
|---|---|---|---|---|---|---|
| BoT-SORT − Deep-OC-SORT | IDF1 | +0.5104 | −0.2033 | survives | survives | 0.3585 |
| Deep-OC-SORT − Hybrid-SORT | DetA | −1.2037 | +0.2117 | survives | survives | 0.5532 |
| Deep-OC-SORT − Hybrid-SORT | MOTA | −0.8387 | +1.3490 | survives | survives | 0.5859 |
| OC-SORT − Hybrid-SORT | HOTA | −0.5761 | +0.1796 | survives | survives | 0.4332 |
| OC-SORT − Hybrid-SORT | MOTA | −1.4567 | +0.2227 | survives | survives | 0.4260 |

Bootstrap: 33 of 50 percentile intervals exclude zero at R0, 28 of 50 at R2, and
32 of 50 for the change in margin.

## The margin-size observation and its limit

The five crossing cells had initial absolute margins between 0.5104 and 1.4567,
comparable to the post-processing gains. But 17 of the 45 unchanged cells also
had initial margins at or below 1.4567, the smallest being 0.1869. A small margin
permits a reversal and does not predict one.

Appearances in crossing cells: Hybrid-SORT 4, Deep-OC-SORT 3, OC-SORT 2,
BoT-SORT 1. Hybrid-SORT has the highest non-admitted fraction and the most
appearances; Deep-OC-SORT has the lowest and three appearances. With four of five
deployments involved and five cells in total, this is an ordering coincidence in a
very small sample. Report it as such; see the DanceTrack packet, where it does not
replicate.

## Verification, with the required correction

Re-execution reconstructed the 12,767-row synthesized population with all 12,767
identities unique, and reproduced every available frozen count at the
sequence-by-class level: 105 of 105 cells for MOT17, 130 of 130 including MOT20.

No frozen per-row class table exists, so per-row agreement against the frozen
artifact was not checked and must not be claimed. v5's Verification sentence must be
corrected, and in v6 it lands with the MOT17 composition rather than in a
separate Verification section. Source: `step9_1/STEP9_REPORT_CORRECTIONS.md`.

Other verification facts from v5 Sec. 7 that remain correct: one authorised MOT20
execution, recomputed independently from stored output files; the MOT17 ordering
matrix recomputed from full-precision output with no mismatches; the R1 writer
checked on all 2,223,712 MOT20 coordinates, 97.11 % bit-identical and maximum
deviation 0.005, the half-step of two-decimal rendering.
""")

w("20_RESULTS_DANCETRACK_DTI_FACT_PACKET.md", HEAD + r"""
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
""")
